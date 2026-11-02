// qvideo-server: live synthetic video over plain QUIC (mvfst).
//
// One connection = one client = one fixed rendition from the ladder. Frames are
// produced on a wall-clock-aligned live schedule (all clients of one rendition
// and phase see the same encoder output), one unidirectional stream per GOP.
// The app never waits for the transport: frames are written as they are
// "encoded", so a congested path builds sender-side backlog like a live encoder.

#include "Common.h"

#include <folly/Synchronized.h>
#include <folly/init/Init.h>
#include <folly/io/async/AsyncSignalHandler.h>
#include <folly/io/async/AsyncTimeout.h>
#include <folly/io/async/EventBase.h>
#include <gflags/gflags.h>
#include <glog/logging.h>
#include <proxygen/httpserver/samples/hq/FizzContext.h>
#include <quic/congestion_control/ServerCongestionControllerFactory.h>
#include <quic/observer/SocketObserverTypes.h>
#include <quic/server/QuicServer.h>
#include <quic/server/QuicServerTransport.h>
#include <quic/server/ThreadedQuicServer.h>

#include <csignal>
#include <filesystem>

DEFINE_string(host, "0.0.0.0", "listen address");
DEFINE_int32(port, 4433, "listen UDP port");
DEFINE_string(cc, "bbr", "mvfst congestion controller (bbr, bbr2, copa, cubic, newreno, ...)");
DEFINE_string(ladder_kbps, "500,1000,2500,5000,8000,12000", "allowed renditions");
DEFINE_int32(fps, 30, "frames per second");
DEFINE_int32(gop_ms, 1000, "GOP duration; one QUIC stream per GOP");
DEFINE_double(ip_ratio, 8.0, "mean I-frame / mean P-frame size");
DEFINE_double(size_sigma, 0.2, "lognormal sigma of per-frame size noise");
DEFINE_uint64(seed, 1, "frame size seed");
DEFINE_int32(stats_ms, 50, "sender CC stats sampling interval");
DEFINE_int32(workers, 1, "QUIC worker threads (one EventBase each)");
DEFINE_uint64(start_unix_us, 0, "stream start (CLOCK_REALTIME us) shared by all clients; 0 = now");
DEFINE_string(out_dir, "/tmp/qvideo-server", "per-connection logs");

namespace {

using quic::QuicError;
using quic::StreamId;

struct Config {
  std::vector<uint32_t> ladder;
  uint64_t startUs{0};
  quic::samples::FizzServerContextPtr fizz;
};

// TransportInfo has no pacing rate (its pacingInterval is the time until the
// next write); the pacer reports its rate through this observer event.
class PacingObserver : public quic::ManagedObserver {
 public:
  PacingObserver()
      : quic::ManagedObserver(EventSetBuilder().enable(Events::pacingRateUpdatedEvents).build()) {}

  void pacingRateUpdated(quic::QuicSocketLite*, const PacingRateUpdateEvent& e) noexcept override {
    packetsPerInterval = e.packetsPerInterval;
    interval = e.interval;
  }

  // 0 when the pacer is not limiting (zero interval) or has not reported yet.
  uint64_t rateBps(uint64_t mss) const {
    return interval.count() > 0 ? packetsPerInterval * mss * 8 * 1000000 / uint64_t(interval.count()) : 0;
  }

  uint64_t packetsPerInterval{0};
  std::chrono::microseconds interval{0};
};

class Session : public quic::QuicSocket::ConnectionSetupCallback,
                public quic::QuicSocket::ConnectionCallback,
                public quic::QuicSocket::ReadCallback {
 public:
  Session(folly::EventBase* evb, const Config& cfg) : evb_(evb), cfg_(cfg) {}

  void setSocket(std::shared_ptr<quic::QuicSocket> sock) { sock_ = std::move(sock); }

  void onConnectionSetupError(QuicError e) noexcept override { finish("setup error: " + e.message); }
  void onTransportReady() noexcept override {}

  void onNewBidirectionalStream(StreamId id) noexcept override {
    if (request_) {
      LOG(WARNING) << "ignoring extra bidi stream " << id;
      return;
    }
    (void)sock_->setReadCallback(id, this);
  }
  void onNewUnidirectionalStream(StreamId) noexcept override {}
  void onStopSending(StreamId, quic::ApplicationErrorCode) noexcept override {}
  void onConnectionEnd() noexcept override { finish("closed"); }
  void onConnectionError(QuicError e) noexcept override { finish("error: " + e.message); }

  void readAvailable(StreamId id) noexcept override {
    auto res = sock_->read(id, 0);
    if (res.hasError()) {
      return;
    }
    if (res->first) {
      auto range = res->first->coalesce();
      requestBuf_.append(reinterpret_cast<const char*>(range.data()), range.size());
    }
    if (requestBuf_.size() > 256) {
      reject("request too long");
      return;
    }
    auto nl = requestBuf_.find('\n');
    if (nl == std::string::npos || request_) {
      return;
    }
    auto req = qvideo::parseRequest(requestBuf_.substr(0, nl));
    if (!req) {
      reject("malformed request");
      return;
    }
    if (std::find(cfg_.ladder.begin(), cfg_.ladder.end(), req->rateKbps) == cfg_.ladder.end()) {
      reject("rate not in ladder");
      return;
    }
    request_ = *req;
    start();
  }
  void readError(StreamId, QuicError) noexcept override {}

 private:
  void reject(const std::string& why) {
    LOG(WARNING) << "rejecting client: " << why;
    sock_->close(QuicError(quic::ApplicationErrorCode(1), std::string(why)));
  }

  void start() {
    params_.rateKbps = request_->rateKbps;
    params_.fps = uint32_t(FLAGS_fps);
    params_.gopFrames = uint32_t(std::max(1, FLAGS_gop_ms * FLAGS_fps / 1000));
    params_.ipRatio = FLAGS_ip_ratio;
    params_.sizeSigma = FLAGS_size_sigma;
    params_.seed = FLAGS_seed;
    schedule_.startUs = cfg_.startUs;
    schedule_.phaseUs = uint64_t(request_->phaseMs) * 1000;
    schedule_.fps = params_.fps;
    schedule_.gopFrames = params_.gopFrames;

    const std::string base = FLAGS_out_dir + "/" + request_->clientId;
    pacing_ = std::make_shared<PacingObserver>();
    sock_->addObserver(pacing_);
    framesCsv_.open(base + "-frames.csv");
    framesCsv_ << "index,keyframe,size,send_us,stream\n";
    statsCsv_.open(base + "-cc.csv");
    // cc: the controller mvfst actually runs (TransportInfo), not the flag.
    statsCsv_ << "t_us,cc,srtt_us,min_rtt_us,latest_rtt_us,cwnd_bytes,inflight_bytes,"
                 "pacing_bps,bw_est_bps,bytes_sent,bytes_acked,retx_bytes,lost_packets,"
                 "app_bytes,backlog_bytes\n";

    nextIndex_ = schedule_.firstFrame(qvideo::nowUs());
    LOG(INFO) << request_->clientId << " rate=" << params_.rateKbps << "kbps phase="
              << request_->phaseMs << "ms first_frame=" << nextIndex_;

    frameTimer_ = folly::AsyncTimeout::make(*evb_, [this]() noexcept { onFrameTimer(); });
    statsTimer_ = folly::AsyncTimeout::make(*evb_, [this]() noexcept { onStatsTimer(); });
    scheduleFrame();
    statsTimer_->scheduleTimeout(FLAGS_stats_ms);
  }

  void scheduleFrame() {
    const uint64_t now = qvideo::nowUs();
    const uint64_t due = schedule_.timeUs(nextIndex_);
    frameTimer_->scheduleTimeoutHighRes(std::chrono::microseconds(due > now ? due - now : 0));
  }

  void onFrameTimer() {
    if (done_) {
      return;
    }
    // Catch up on every frame whose time has passed (a late timer must not
    // lower the encoded bitrate).
    for (uint64_t now = qvideo::nowUs(); schedule_.timeUs(nextIndex_) <= now; ++nextIndex_) {
      if (!sendFrame(nextIndex_)) {
        return;
      }
    }
    scheduleFrame();
  }

  bool sendFrame(uint64_t k) {
    const bool key = k % params_.gopFrames == 0;
    if (key) {
      if (stream_) {
        (void)sock_->writeChain(*stream_, quic::Buf::create(0), true);
      }
      auto id = sock_->createUnidirectionalStream();
      if (id.hasError()) {
        finish("cannot open GOP stream");
        return false;
      }
      stream_ = *id;
    }
    qvideo::FrameHeader h;
    h.keyframe = key ? 1 : 0;
    h.index = k;
    h.size = qvideo::frameSize(params_, k);
    h.rateKbps = params_.rateKbps;
    h.sendUs = qvideo::nowUs();
    auto buf = quic::Buf::create(h.size);
    std::memset(buf->writableData(), 0, h.size);
    std::memcpy(buf->writableData(), &h, sizeof(h));
    buf->append(h.size);
    if (sock_->writeChain(*stream_, std::move(buf), false).hasError()) {
      finish("write failed");
      return false;
    }
    appBytes_ += h.size;
    framesCsv_ << k << ',' << int(h.keyframe) << ',' << h.size << ',' << h.sendUs << ','
               << *stream_ << '\n';
    return true;
  }

  void onStatsTimer() {
    if (done_) {
      return;
    }
    const auto info = sock_->getTransportInfo();
    const uint64_t pacingBps = pacing_->rateBps(info.mss);
    const uint64_t bwBps = info.maybeCCState && info.maybeCCState->maybeBandwidthBitsPerSec
        ? *info.maybeCCState->maybeBandwidthBitsPerSec
        : 0;
    const uint64_t minRtt = info.maybeMinRtt ? info.maybeMinRtt->count() : 0;
    const uint64_t backlog =
        appBytes_ > info.totalNewStreamBytesSent ? appBytes_ - info.totalNewStreamBytesSent : 0;
    const uint64_t t = qvideo::nowUs();
    std::ostringstream row;
    row << t << ',' << quic::congestionControlTypeToString(info.congestionControlType) << ','
        << info.srtt.count() << ',' << minRtt << ','
        << info.lrtt.count() << ',' << info.congestionWindow << ',' << info.bytesInFlight << ','
        << pacingBps << ',' << bwBps << ',' << info.bytesSent << ',' << info.bytesAcked << ','
        << info.totalBytesRetransmitted << ',' << info.totalPacketsMarkedLost << ',' << appBytes_
        << ',' << backlog << '\n';
    statsCsv_ << row.str();
    statsCsv_.flush();
    framesCsv_.flush();
    statsTimer_->scheduleTimeout(FLAGS_stats_ms);
  }

  void finish(const std::string& why) {
    if (done_) {
      return;
    }
    done_ = true;
    if (frameTimer_) {
      frameTimer_->cancelTimeout();
    }
    if (statsTimer_) {
      statsTimer_->cancelTimeout();
    }
    framesCsv_.flush();
    statsCsv_.flush();
    LOG(INFO) << (request_ ? request_->clientId : std::string("?")) << " session end: " << why;
  }

  folly::EventBase* evb_;
  const Config& cfg_;
  std::shared_ptr<quic::QuicSocket> sock_;
  std::shared_ptr<PacingObserver> pacing_;
  std::string requestBuf_;
  std::optional<qvideo::Request> request_;
  qvideo::VideoParams params_;
  qvideo::Schedule schedule_;
  uint64_t nextIndex_{0};
  uint64_t appBytes_{0};
  std::optional<StreamId> stream_;
  std::unique_ptr<folly::AsyncTimeout> frameTimer_;
  std::unique_ptr<folly::AsyncTimeout> statsTimer_;
  std::ofstream framesCsv_;
  std::ofstream statsCsv_;
  bool done_{false};
};

class SessionFactory : public quic::QuicServerTransportFactory {
 public:
  SessionFactory(const Config& cfg, std::shared_ptr<const fizz::server::FizzServerContext> ctx)
      : cfg_(cfg), ctx_(std::move(ctx)) {}

  // Sessions live on their worker EventBase; destroy them there.
  ~SessionFactory() override {
    sessions_.withWLock([](auto& sessions) {
      for (auto& [evb, session] : sessions) {
        evb->runImmediatelyOrRunInEventBaseThreadAndWait([&] { session.reset(); });
      }
    });
  }

  quic::QuicServerTransport::Ptr make(
      folly::EventBase* evb,
      std::unique_ptr<quic::FollyAsyncUDPSocketAlias> sock,
      const quic::SocketAddress&,
      quic::QuicVersion) noexcept override {
    auto session = std::make_unique<Session>(evb, cfg_);
    auto transport =
        quic::QuicServerTransport::make(evb, std::move(sock), session.get(), session.get(), ctx_);
    transport->setCongestionControllerFactory(ccFactory_);
    session->setSocket(transport);
    sessions_.wlock()->emplace_back(evb, std::move(session));
    return transport;
  }

 private:
  const Config& cfg_;
  std::shared_ptr<const fizz::server::FizzServerContext> ctx_;
  std::shared_ptr<quic::CongestionControllerFactory> ccFactory_{
      std::make_shared<quic::ServerCongestionControllerFactory>()};
  folly::Synchronized<std::vector<std::pair<folly::EventBase*, std::unique_ptr<Session>>>>
      sessions_;
};

class StopOnSignal : public folly::AsyncSignalHandler {
 public:
  StopOnSignal(folly::EventBase* evb, std::function<void()> stop)
      : folly::AsyncSignalHandler(evb), stop_(std::move(stop)) {
    registerSignalHandler(SIGTERM);
    registerSignalHandler(SIGINT);
  }
  void signalReceived(int) noexcept override { stop_(); }

 private:
  std::function<void()> stop_;
};

} // namespace

int main(int argc, char** argv) {
  folly::Init init(&argc, &argv);
  auto cc = quic::congestionControlStrToType(FLAGS_cc);
  if (!cc) {
    LOG(ERROR) << "unknown --cc " << FLAGS_cc;
    return 2;
  }
  Config cfg;
  cfg.ladder = qvideo::parseList(FLAGS_ladder_kbps);
  cfg.startUs = FLAGS_start_unix_us ? FLAGS_start_unix_us : qvideo::nowUs();
  if (cfg.ladder.empty() || FLAGS_fps <= 0 || FLAGS_gop_ms <= 0 || FLAGS_workers <= 0) {
    LOG(ERROR) << "invalid ladder/fps/gop/workers";
    return 2;
  }
  std::filesystem::create_directories(FLAGS_out_dir);

  quic::ServerOptions options;
  auto& ts = options.transportSettings;
  ts.defaultCongestionController = *cc;
  ts.pacingEnabled = true;
  ts.idleTimeout = std::chrono::seconds(30);
  // No GSO: router queues must see wire-sized packets, not 64 KB super-packets.
  ts.batchingMode = quic::QuicBatchingMode::BATCHING_MODE_NONE;

  auto server = std::make_unique<quic::ThreadedQuicServer>(
      std::move(options),
      std::make_unique<SessionFactory>(
          cfg,
          quic::samples::createFizzServerContextWithInsecureDefault(
              {qvideo::kAlpn}, fizz::server::ClientAuthMode::None, "", "")));

  folly::EventBase evb;
  quic::SocketAddress addr(FLAGS_host, uint16_t(FLAGS_port));
  server->start(addr, size_t(FLAGS_workers));
  StopOnSignal stop(&evb, [&] {
    server->shutdown();
    evb.terminateLoopSoon();
  });
  LOG(INFO) << "qvideo-server listening on " << addr.describe() << " cc=" << FLAGS_cc
            << " workers=" << FLAGS_workers;
  evb.loopForever();
  return 0;
}
