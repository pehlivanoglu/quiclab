// qvideo-client: consumes one fixed rendition from qvideo-server and simulates
// playback with a fixed startup/jitter buffer (see Playback.h).

#include "Common.h"
#include "Playback.h"

#include <fizz/protocol/CertificateVerifier.h>
#include <folly/init/Init.h>
#include <folly/io/async/AsyncSignalHandler.h>
#include <folly/io/async/AsyncTimeout.h>
#include <folly/io/async/EventBase.h>
#include <gflags/gflags.h>
#include <glog/logging.h>
#include <moxygen/util/InsecureVerifierDangerousDoNotUseInProduction.h>
#include <quic/client/QuicClientTransport.h>
#include <quic/common/events/FollyQuicEventBase.h>
#include <quic/common/udpsocket/FollyQuicAsyncUDPSocket.h>
#include <quic/fizz/client/handshake/FizzClientQuicHandshakeContext.h>

#include <csignal>
#include <filesystem>
#include <map>

DEFINE_string(host, "", "server address");
DEFINE_int32(port, 4433, "server UDP port");
DEFINE_string(id, "", "client id (log file prefix, sent to the server)");
DEFINE_int32(rate_kbps, 2500, "rendition to request (must be in the server ladder)");
DEFINE_int32(phase_ms, 0, "keyframe phase offset of the live schedule");
DEFINE_int32(fps, 30, "frames per second (must match the server)");
DEFINE_int32(buffer_ms, 600, "playback buffer before first frame plays");
DEFINE_int32(stats_ms, 100, "playback sampling interval");
DEFINE_int32(duration_s, 0, "stop after this many seconds (0 = until signalled)");
DEFINE_string(out_dir, "/tmp/qvideo-client", "logs");
DEFINE_int32(ping_ms, 50, "send a QUIC PING this often (0 = never); see pingTimer_");

namespace {

using quic::QuicError;
using quic::StreamId;

class Client : public quic::QuicSocket::ConnectionSetupCallback,
               public quic::QuicSocket::ConnectionCallback,
               public quic::QuicSocket::ReadCallback {
 public:
  explicit Client(folly::EventBase* evb)
      : evb_(evb),
        playback_(uint64_t(1000000 / FLAGS_fps), uint64_t(FLAGS_buffer_ms) * 1000) {}

  void start() {
    const std::string base = FLAGS_out_dir + "/" + FLAGS_id;
    framesCsv_.open(base + "-frames.csv");
    framesCsv_ << "index,keyframe,size,send_us,recv_us,owd_us,late_us\n";
    playCsv_.open(base + "-playback.csv");
    playCsv_ << "t_us,frames,bytes,goodput_bps,buffer_ms,stalls,stall_ms,owd_ms,skipped_frames\n";

    auto qevb = std::make_shared<quic::FollyQuicEventBase>(evb_);
    auto sock = std::make_unique<quic::FollyQuicAsyncUDPSocket>(qevb);
    auto fizzCtx = std::make_shared<fizz::client::FizzClientContext>();
    fizzCtx->setSupportedAlpns({qvideo::kAlpn});
    auto handshake =
        quic::FizzClientQuicHandshakeContext::Builder()
            .setFizzClientContext(std::move(fizzCtx))
            .setCertificateVerifier(
                std::make_shared<moxygen::test::InsecureVerifierDangerousDoNotUseInProduction>())
            .build();
    transport_ = std::make_shared<quic::QuicClientTransport>(qevb, std::move(sock), std::move(handshake));
    transport_->setHostname("qvideo");
    transport_->addNewPeerAddress(folly::SocketAddress(FLAGS_host, uint16_t(FLAGS_port), true));
    quic::TransportSettings ts;
    // Receive windows far above any BDP here: only the path may limit the flow.
    ts.advertisedInitialConnectionFlowControlWindow = 256 << 20;
    ts.advertisedInitialUniStreamFlowControlWindow = 64 << 20;
    ts.advertisedInitialMaxStreamsUni = 1 << 20;
    ts.idleTimeout = std::chrono::seconds(30);
    // Report every packet's receive time in ACKs (legacy mvfst ACK_RECEIVE_TIMESTAMPS,
    // 1 us resolution), so the sender can log exact one-way delay.
    ts.maybeAckReceiveTimestampsConfigSentToPeer =
        quic::AckReceiveTimestampsConfig{.maxReceiveTimestampsPerAck = 64, .receiveTimestampsExponent = 0};
    ts.maxReceiveTimestampsPerAckStored = 64;
    // IETF draft-02 format: the legacy mvfst format only reports a gap-free
    // suffix of packets and drops to ~0 % coverage once there is loss.
    ts.enableIetfAckReceiveTimestamps = true;
    ts.advertiseLegacyAckReceiveTimestamps = false;
    ts.sendDraft02AckReceiveTimestamps = true;
    transport_->setTransportSettings(ts);
    transport_->start(this, this);

    statsTimer_ = folly::AsyncTimeout::make(*evb_, [this]() noexcept { onStats(); });
    statsTimer_->scheduleTimeout(FLAGS_stats_ms);
    if (FLAGS_ping_ms > 0) {
      // A receiver that only sends ACKs never gets its own ACKs acknowledged,
      // so mvfst never retires old ACK ranges: every loss adds one (up to
      // 1024) until the ranges fill the ACK packet and leave no room for the
      // receive timestamps the sender's OWD log needs. A periodic PING is
      // ack-eliciting; the server's ACK of it lets the client retire them.
      pingTimer_ = folly::AsyncTimeout::make(*evb_, [this]() noexcept {
        transport_->sendPing(std::chrono::milliseconds(0));
        pingTimer_->scheduleTimeout(FLAGS_ping_ms);
      });
      pingTimer_->scheduleTimeout(FLAGS_ping_ms);
    }
    if (FLAGS_duration_s > 0) {
      stopTimer_ = folly::AsyncTimeout::make(*evb_, [this]() noexcept { stop("duration reached"); });
      stopTimer_->scheduleTimeout(std::chrono::seconds(FLAGS_duration_s));
    }
  }

  void stop(const std::string& why) {
    if (stopped_) {
      return;
    }
    stopped_ = true;
    LOG(INFO) << FLAGS_id << " stopping: " << why << " frames=" << frames_
              << " stalls=" << playback_.stalls() << " stall_ms=" << playback_.stallUs() / 1000;
    onStats();
    framesCsv_.flush();
    playCsv_.flush();
    if (statsTimer_) {
      statsTimer_->cancelTimeout();
    }
    if (stopTimer_) {
      stopTimer_->cancelTimeout();
    }
    if (pingTimer_) {
      pingTimer_->cancelTimeout();
    }
    if (transport_) {
      transport_->close(std::nullopt);
    }
    evb_->terminateLoopSoon();
  }

  void onConnectionSetupError(QuicError e) noexcept override { stop("setup error: " + e.message); }

  void onTransportReady() noexcept override {
    auto id = transport_->createBidirectionalStream();
    if (id.hasError()) {
      stop("cannot open request stream");
      return;
    }
    // Receive timestamps in our ACKs count from our connection start (steady
    // clock = CLOCK_MONOTONIC, shared with the sender in this testbed).
    const int64_t basisUs = std::chrono::duration_cast<std::chrono::microseconds>(
        transport_->getTransportInfo().connectionTime.time_since_epoch()).count();
    const std::string req = "QV1 " + FLAGS_id + " " + std::to_string(FLAGS_rate_kbps) + " " +
        std::to_string(FLAGS_phase_ms) + " " + std::to_string(basisUs) + "\n";
    (void)transport_->writeChain(*id, quic::Buf::copyBuffer(req.data(), req.size()), true);
    LOG(INFO) << FLAGS_id << " connected, requested " << FLAGS_rate_kbps << " kbps";
  }

  void onNewBidirectionalStream(StreamId) noexcept override {}
  void onNewUnidirectionalStream(StreamId id) noexcept override {
    (void)transport_->setReadCallback(id, this);
  }
  void onStopSending(StreamId, quic::ApplicationErrorCode) noexcept override {}
  void onConnectionEnd() noexcept override { stop("connection end"); }
  void onConnectionError(QuicError e) noexcept override { stop("connection error: " + e.message); }

  void readAvailable(StreamId id) noexcept override {
    auto res = transport_->read(id, 0);
    if (res.hasError()) {
      return;
    }
    auto& pending = streams_[id];
    if (res->first) {
      auto range = res->first->coalesce();
      pending.append(reinterpret_cast<const char*>(range.data()), range.size());
    }
    const uint64_t now = qvideo::nowUs();
    while (pending.size() >= sizeof(qvideo::FrameHeader)) {
      qvideo::FrameHeader h;
      std::memcpy(&h, pending.data(), sizeof(h));
      if (h.magic != qvideo::kMagic || h.size < sizeof(h)) {
        stop("corrupt frame on stream " + std::to_string(id));
        return;
      }
      if (pending.size() < h.size) {
        break;
      }
      pending.erase(0, h.size);
      onFrame(h, now);
    }
    if (res->second) {
      if (!pending.empty()) {
        LOG(WARNING) << "stream " << id << " ended with " << pending.size() << " stray bytes";
      }
      streams_.erase(id);
    }
  }
  void readError(StreamId id, QuicError) noexcept override { streams_.erase(id); }

 private:
  void onFrame(const qvideo::FrameHeader& h, uint64_t now) {
    const int64_t late = playback_.onFrame(h.index, now, h.skippedBefore);
    const uint64_t owd = now > h.sendUs ? now - h.sendUs : 0;
    ++frames_;
    bytes_ += h.size;
    owdSumUs_ += owd;
    ++owdCount_;
    framesCsv_ << h.index << ',' << int(h.keyframe) << ',' << h.size << ',' << h.sendUs << ','
               << now << ',' << owd << ',' << late << '\n';
  }

  void onStats() {
    const uint64_t now = qvideo::nowUs();
    const double dt = lastStatsUs_ ? double(now - lastStatsUs_) / 1e6 : 0;
    const double goodput = dt > 0 ? double(bytes_ - lastBytes_) * 8 / dt : 0;
    const double owdMs = owdCount_ ? double(owdSumUs_) / owdCount_ / 1000 : 0;
    std::ostringstream row;
    row << now << ',' << frames_ << ',' << bytes_ << ',' << uint64_t(goodput) << ','
        << playback_.bufferUs(now) / 1000 << ',' << playback_.stalls() << ','
        << playback_.stallUs() / 1000 << ',' << owdMs << ',' << playback_.skipped() << '\n';
    playCsv_ << row.str();
    playCsv_.flush();
    framesCsv_.flush();
    lastStatsUs_ = now;
    lastBytes_ = bytes_;
    owdSumUs_ = 0;
    owdCount_ = 0;
    if (!stopped_) {
      statsTimer_->scheduleTimeout(FLAGS_stats_ms);
    }
  }

  folly::EventBase* evb_;
  std::shared_ptr<quic::QuicClientTransport> transport_;
  std::map<StreamId, std::string> streams_;
  qvideo::Playback playback_;
  std::unique_ptr<folly::AsyncTimeout> statsTimer_;
  std::unique_ptr<folly::AsyncTimeout> pingTimer_;
  std::unique_ptr<folly::AsyncTimeout> stopTimer_;
  std::ofstream framesCsv_;
  std::ofstream playCsv_;
  uint64_t frames_{0};
  uint64_t bytes_{0};
  uint64_t lastBytes_{0};
  uint64_t lastStatsUs_{0};
  uint64_t owdSumUs_{0};
  uint64_t owdCount_{0};
  bool stopped_{false};
};

class StopOnSignal : public folly::AsyncSignalHandler {
 public:
  StopOnSignal(folly::EventBase* evb, Client& client) : folly::AsyncSignalHandler(evb), client_(client) {
    registerSignalHandler(SIGTERM);
    registerSignalHandler(SIGINT);
  }
  void signalReceived(int) noexcept override { client_.stop("signal"); }

 private:
  Client& client_;
};

} // namespace

int main(int argc, char** argv) {
  folly::Init init(&argc, &argv);
  if (FLAGS_host.empty() || !qvideo::validClientId(FLAGS_id) || FLAGS_fps <= 0 ||
      FLAGS_rate_kbps <= 0 || FLAGS_buffer_ms < 0) {
    LOG(ERROR) << "need --host, a valid --id, positive --fps/--rate_kbps, --buffer_ms >= 0";
    return 2;
  }
  std::filesystem::create_directories(FLAGS_out_dir);
  folly::EventBase evb;
  Client client(&evb);
  StopOnSignal signals(&evb, client);
  evb.runInEventBaseThread([&] { client.start(); });
  evb.loopForever();
  return 0;
}
