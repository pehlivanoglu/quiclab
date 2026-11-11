// qvideo-server: live synthetic video over plain QUIC (mvfst).
//
// One connection = one client = one fixed rendition from the ladder. Frames are
// produced on a wall-clock-aligned live schedule (all clients of one rendition
// and phase see the same encoder output), one unidirectional stream per GOP.
// The app never waits for the transport: frames are written as they are
// "encoded", so a congested path builds sender-side backlog like a live encoder.

#include "Common.h"
#include "SendQueue.h"

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
#include <quic/state/StateData.h>

#include <atomic>
#include <csignal>
#include <filesystem>
#include <limits>
#include <map>

DEFINE_string(host, "0.0.0.0", "listen address");
DEFINE_int32(port, 4433, "listen UDP port");
DEFINE_string(cc, "bbr", "mvfst congestion controller (bbr, bbr2, copa, cubic, newreno, ...)");
DEFINE_string(ladder_kbps, "500,1000,2500,5000,8000,12000", "allowed renditions");
DEFINE_int32(fps, 30, "frames per second");
DEFINE_int32(gop_ms, 1000, "GOP duration; one QUIC stream per GOP");
DEFINE_double(ip_ratio, 4.0, "mean I-frame / mean P-frame size");
DEFINE_double(size_sigma, 0.2, "lognormal sigma of per-frame size noise");
DEFINE_uint64(seed, 1, "frame size seed");
DEFINE_int32(stats_ms, 50, "sender CC stats sampling interval");
DEFINE_int32(workers, 1, "QUIC worker threads (one EventBase each)");
DEFINE_int32(send_buffer_ms, 1000, "sender frame queue limit in media time (GOP-aware head drop); 0 = unlimited");
DEFINE_uint64(start_unix_us, 0, "stream start (CLOCK_REALTIME us) shared by all clients; 0 = now");
DEFINE_string(out_dir, "/tmp/qvideo-server", "per-connection logs");
DEFINE_bool(record_acks, true, "write per-ACK detector inputs (<client>-acks.csv, -sent.csv)");
DEFINE_bool(owd, true, "write exact one-way delay per 5 ms (<client>-owd.csv) from ACK receive timestamps");

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

constexpr std::chrono::microseconds kPumpInterval{5000};

// Processing order across all connections, so an offline replay interleaves
// sends and ACKs of every flow exactly as they happened.
std::atomic<uint64_t> gSeq{0};

int64_t monoUs(quic::TimePoint time) {
  return std::chrono::duration_cast<std::chrono::microseconds>(time.time_since_epoch()).count();
}

const char* bbrPhase(const quic::QuicConnectionStateBase* conn) {
  if (!conn || !conn->congestionController) {
    return "unknown";
  }
  quic::CongestionControllerStats stats{};
  conn->congestionController->getStats(stats);
  switch (conn->congestionController->type()) {
    case quic::CongestionControlType::BBR2:
    case quic::CongestionControlType::BBR2Modular: {
      static const char* const kNames[] = {"startup", "drain", "probe_bw_down", "probe_bw_cruise",
                                           "probe_bw_refill", "probe_bw_up", "probe_rtt"};
      return stats.bbr2Stats.state < 7 ? kNames[stats.bbr2Stats.state] : "unknown";
    }
    case quic::CongestionControlType::BBR: {
      static const char* const kNames[] = {"startup", "drain", "probe_bw", "probe_rtt"};
      return stats.bbrStats.state < 4 ? kNames[stats.bbrStats.state] : "unknown";
    }
    default:
      return "unknown";
  }
}

// Exact one-way delay of the video's own QUIC packets, in 5 ms bins of send
// time. The client reports each packet's receive time in its ACKs (relative
// to its connection start, which it sends in the request); sender and client
// share one CLOCK_MONOTONIC, so receive - send is the true OWD (propagation +
// transmission + queuing), not an estimate. Bins are written once 10 s old,
// so late ACKs still land; packets_sent - packets_timed = lost or untimed.
class OwdRecorder : public quic::ManagedObserver {
 public:
  static constexpr int64_t kBinUs = 5000;  // FlowBot's OWD sampling step
  static constexpr int64_t kHoldUs = 10000000;

  OwdRecorder(const std::string& base, int64_t basisUs)
      : quic::ManagedObserver(EventSetBuilder()
                                  .enable(Events::packetsWrittenEvents)
                                  .enable(Events::acksProcessedEvents)
                                  .build()),
        basisUs_(basisUs) {
    const int64_t mono = monoUs(quic::Clock::now());
    unixOffsetUs_ = int64_t(qvideo::nowUs()) - mono;
    csv_.open(base + "-owd.csv");
    csv_ << "t_us,bin_mono_us,packets_sent,packets_timed,owd_min_us,owd_mean_us,owd_max_us\n";
  }

  void packetsWritten(quic::QuicSocketLite*, const PacketsWrittenEvent& event) noexcept override {
    event.invokeForEachNewOutstandingPacketOrdered([&](const auto& packet) {
      if (packet.packet.header.getPacketNumberSpace() == quic::PacketNumberSpace::AppData) {
        ++bins_[monoUs(packet.metadata.time) / kBinUs].sent;
      }
    });
  }

  void acksProcessed(quic::QuicSocketLite*, const AcksProcessedEvent& event) noexcept override {
    for (const auto& ack : event.ackEvents) {
      if (ack.implicit || ack.packetNumberSpace != quic::PacketNumberSpace::AppData) {
        continue;
      }
      for (const auto& packet : ack.ackedPackets) {
        if (!packet.receiveRelativeTimeStampUsec) {
          continue;
        }
        const int64_t sentUs = monoUs(packet.outstandingPacketMetadata.time);
        const int64_t owd = basisUs_ + packet.receiveRelativeTimeStampUsec->count() - sentUs;
        auto& b = bins_[sentUs / kBinUs];
        b.minUs = b.timed ? std::min(b.minUs, owd) : owd;
        b.maxUs = b.timed ? std::max(b.maxUs, owd) : owd;
        b.sumUs += owd;
        ++b.timed;
      }
    }
  }

  // Writes every bin older than kHoldUs (all bins when final), as a gap-free
  // 5 ms grid: bins without packets have empty OWD fields.
  void flush(bool final) {
    const int64_t limit = final ? std::numeric_limits<int64_t>::max()
                                : (monoUs(quic::Clock::now()) - kHoldUs) / kBinUs;
    while (!bins_.empty() && bins_.begin()->first < limit) {
      const auto [bin, b] = *bins_.begin();
      for (int64_t gap = next_ ? next_ : bin; gap < bin; ++gap) {
        csv_ << gap * kBinUs + unixOffsetUs_ << ',' << gap * kBinUs << ",0,0,,,\n";
      }
      csv_ << bin * kBinUs + unixOffsetUs_ << ',' << bin * kBinUs << ',' << b.sent << ',' << b.timed << ',';
      if (b.timed) {
        csv_ << b.minUs << ',' << b.sumUs / b.timed << ',' << b.maxUs;
      } else {
        csv_ << ",,";
      }
      csv_ << '\n';
      next_ = bin + 1;
      bins_.erase(bins_.begin());
    }
    csv_.flush();
  }

 private:
  struct Bin {
    uint32_t sent{0};
    uint32_t timed{0};
    int64_t sumUs{0};
    int64_t minUs{0};
    int64_t maxUs{0};
  };
  int64_t basisUs_;
  int64_t unixOffsetUs_{0};
  int64_t next_{0};
  std::map<int64_t, Bin> bins_;
  std::ofstream csv_;
};

// Read-only per-ACK record of what the CC sees, in the raw sample format of
// the moq-testbed shadow detector replay (moqx_shadow_replay), so detectors
// run offline on the exact network history. Times are CLOCK_MONOTONIC us
// (the router metrics and events.csv share that clock).
class AckRecorder : public quic::ManagedObserver {
 public:
  // recvBasisUs: the client's receive clock basis (its request); 0 = no OWD column values.
  AckRecorder(const std::string& base, int64_t recvBasisUs, std::function<uint64_t()> backlogBytes)
      : quic::ManagedObserver(EventSetBuilder()
                                  .enable(Events::packetsWrittenEvents)
                                  .enable(Events::acksProcessedEvents)
                                  .enable(Events::lossEvents)
                                  .build()),
        recvBasisUs_(recvBasisUs),
        backlogBytes_(std::move(backlogBytes)) {
    acks_.open(base + "-acks.csv");
    // owd_us: one-way delay of the largest newly acked packet from its own ACK
    // receive timestamp (empty when the ACK carried none): what an OWD-based
    // detector knows at this ACK, nothing from later ACKs or send-time bins.
    acks_ << "mono_us,sent_mono_us,rtt_us,min_rtt_us,srtt_us,rate_valid,app_limited,send_bps,ack_bps,"
             "bbr_bw_bps,cwnd_bytes,inflight_bytes,stream_buffer_bytes,bytes_acked_total,"
             "bytes_sent_at_send,phase,newly_lost,relay_saturated,seq,owd_us\n";
    sent_.open(base + "-sent.csv");
    sent_ << "send_mono_us,bytes,seq\n";
  }

  void packetsWritten(quic::QuicSocketLite*, const PacketsWrittenEvent& event) noexcept override {
    uint64_t bytes = 0;
    int64_t sendUs = 0;
    event.invokeForEachNewOutstandingPacketOrdered([&](const auto& packet) {
      if (packet.packet.header.getPacketNumberSpace() != quic::PacketNumberSpace::AppData) {
        return;
      }
      bytes += packet.metadata.encodedSize;
      sendUs = monoUs(packet.metadata.time);
    });
    if (bytes) {
      sent_ << sendUs << ',' << bytes << ',' << ++gSeq << '\n';
    }
  }

  void packetLossDetected(quic::QuicSocketLite*, const LossEvent& event) noexcept override {
    for (const auto& packet : event.lostPackets) {
      lost_ += packet.pnSpace == quic::PacketNumberSpace::AppData;
    }
  }

  void acksProcessed(quic::QuicSocketLite* socket, const AcksProcessedEvent& event) noexcept override {
    const auto info = socket->getTransportInfo();
    const auto* conn = socket->getState();
    const char* phase = bbrPhase(conn);
    const uint64_t backlog = backlogBytes_();
    for (const auto& ack : event.ackEvents) {
      if (ack.implicit || ack.packetNumberSpace != quic::PacketNumberSpace::AppData) {
        continue;
      }
      const auto* largest = ack.getLargestNewlyAckedPacket();
      if (!largest) {
        continue;
      }
      const auto& sent = largest->outstandingPacketMetadata;
      std::optional<int64_t> rtt;
      if (ack.rttSampleNoAckDelay) {
        rtt = ack.rttSampleNoAckDelay->count();
      } else if (ack.rttSample) {
        rtt = ack.rttSample->count();
      }
      // BBR's delivery-rate sample: bytes delivered since the packet acked
      // last when this one was sent, send and ack intervals reported apart.
      bool rateValid = false;
      double sendBps = 0, ackBps = 0;
      if (largest->lastAckedPacketInfo) {
        const auto& last = *largest->lastAckedPacketInfo;
        const int64_t sendUs = monoUs(sent.time) - monoUs(last.sentTime);
        int64_t ackUs = monoUs(ack.adjustedAckTime) - monoUs(last.adjustedAckTime);
        if (ackUs <= 0) {
          ackUs = monoUs(ack.ackTime) - monoUs(last.ackTime);
        }
        const uint64_t sendBytes =
            sent.totalBytesSent >= last.totalBytesSent ? sent.totalBytesSent - last.totalBytesSent : 0;
        const uint64_t delivered =
            ack.totalBytesAcked >= last.totalBytesAcked ? ack.totalBytesAcked - last.totalBytesAcked : 0;
        if (sendUs > 0 && ackUs > 0 && delivered > 0) {
          rateValid = true;
          sendBps = sendBytes * 8e6 / double(sendUs);
          ackBps = delivered * 8e6 / double(ackUs);
        }
      }
      double bwBps = 0;
      uint64_t cwnd = info.congestionWindow;
      if (ack.ccState) {
        if (ack.ccState->maybeBandwidthBitsPerSec) {
          bwBps = double(*ack.ccState->maybeBandwidthBitsPerSec);
        }
        cwnd = ack.ccState->congestionWindowBytes;
      }
      std::string owd;
      if (recvBasisUs_ > 0 && largest->receiveRelativeTimeStampUsec) {
        owd = std::to_string(recvBasisUs_ + largest->receiveRelativeTimeStampUsec->count() - monoUs(sent.time));
      }
      acks_ << monoUs(ack.ackTime) << ',' << monoUs(sent.time) << ','
            << (rtt ? std::to_string(*rtt) : std::string()) << ','
            << (info.maybeMinRtt ? info.maybeMinRtt->count() : 0) << ',' << info.srtt.count() << ','
            << rateValid << ',' << ack.largestNewlyAckedPacketAppLimited << ',' << uint64_t(sendBps) << ','
            << uint64_t(ackBps) << ',' << uint64_t(bwBps) << ',' << cwnd << ',' << info.bytesInFlight << ','
            << backlog << ',' << ack.totalBytesAcked << ',' << sent.totalBytesSent << ',' << phase << ','
            << lost_ << ",0," << ++gSeq << ',' << owd << '\n';
      lost_ = 0;
    }
  }

  void flush() {
    acks_.flush();
    sent_.flush();
  }

 private:
  int64_t recvBasisUs_{0};
  std::function<uint64_t()> backlogBytes_;
  std::ofstream acks_;
  std::ofstream sent_;
  uint32_t lost_{0};
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
    // send_us: when the frame was produced (carried to the client for OWD);
    // write_us: when it left the sender queue for QUIC.
    framesCsv_ << "index,keyframe,size,send_us,write_us,stream\n";
    dropsCsv_.open(base + "-drops.csv");
    dropsCsv_ << "t_us,index,gop,keyframe,size,age_us\n";
    queue_.emplace(uint64_t(FLAGS_send_buffer_ms) * 1000);
    if (FLAGS_record_acks) {
      // Sender-side backlog not yet on the wire: frame queue + QUIC unsent.
      acks_ = std::make_shared<AckRecorder>(base, FLAGS_owd ? request_->recvBasisUs : 0, [this] {
        return queue_->bytes() + quicUnsent(sock_->getTransportInfo());
      });
      sock_->addObserver(acks_);
    }
    if (FLAGS_owd && request_->recvBasisUs > 0) {
      owd_ = std::make_shared<OwdRecorder>(base, request_->recvBasisUs);
      sock_->addObserver(owd_);
    }
    statsCsv_.open(base + "-cc.csv");
    // cc: the controller mvfst actually runs (TransportInfo), not the flag.
    statsCsv_ << "t_us,cc,srtt_us,min_rtt_us,latest_rtt_us,cwnd_bytes,inflight_bytes,"
                 "pacing_bps,bw_est_bps,bytes_sent,bytes_acked,retx_bytes,lost_packets,"
                 "app_bytes,queue_bytes,queue_age_us,quic_unsent_bytes,backlog_bytes,dropped_frames\n";

    nextIndex_ = schedule_.firstFrame(qvideo::nowUs());
    LOG(INFO) << request_->clientId << " rate=" << params_.rateKbps << "kbps phase="
              << request_->phaseMs << "ms first_frame=" << nextIndex_;

    frameTimer_ = folly::AsyncTimeout::make(*evb_, [this]() noexcept { onFrameTimer(); });
    statsTimer_ = folly::AsyncTimeout::make(*evb_, [this]() noexcept { onStatsTimer(); });
    scheduleFrame();
    statsTimer_->scheduleTimeout(FLAGS_stats_ms);
    if (FLAGS_send_buffer_ms > 0) {
      pumpTimer_ = folly::AsyncTimeout::make(*evb_, [this]() noexcept {
        pump();
        if (!done_) {
          pumpTimer_->scheduleTimeoutHighRes(kPumpInterval);
        }
      });
      pumpTimer_->scheduleTimeoutHighRes(kPumpInterval);
    }
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
    // Produce every frame whose time has passed (a late timer must not lower
    // the encoded bitrate); the queue decides what reaches QUIC.
    std::vector<qvideo::QueuedFrame> dropped;
    for (uint64_t now = qvideo::nowUs(); schedule_.timeUs(nextIndex_) <= now; ++nextIndex_) {
      const uint64_t k = nextIndex_;
      queue_->push({k, k / params_.gopFrames, k % params_.gopFrames == 0,
                    qvideo::frameSize(params_, k), qvideo::nowUs()}, dropped);
    }
    logDrops(dropped);
    pump();
    scheduleFrame();
  }

  // Hand queued frames to QUIC while its unsent data is below one cwnd, so
  // the backlog stays in the queue, where stale frames can still be dropped.
  // Unlimited mode writes everything at once (no queue in front of QUIC).
  void pump() {
    if (done_) {
      return;
    }
    std::vector<qvideo::QueuedFrame> dropped;
    queue_->dropStale(qvideo::nowUs(), dropped);
    logDrops(dropped);
    const auto info = sock_->getTransportInfo();
    uint64_t unsent = quicUnsent(info);
    const uint64_t cap = FLAGS_send_buffer_ms > 0 ? std::max<uint64_t>(info.congestionWindow, 1)
                                                  : std::numeric_limits<uint64_t>::max();
    while (!queue_->empty() && unsent < cap) {
      const qvideo::QueuedFrame f = queue_->front();
      queue_->pop();
      if (!writeFrame(f)) {
        return;
      }
      unsent += f.size;
    }
  }

  uint64_t quicUnsent(const quic::TransportInfo& info) const {
    return appBytes_ > info.totalNewStreamBytesSent ? appBytes_ - info.totalNewStreamBytesSent : 0;
  }

  void logDrops(const std::vector<qvideo::QueuedFrame>& dropped) {
    const uint64_t now = qvideo::nowUs();
    for (const auto& f : dropped) {
      dropsCsv_ << now << ',' << f.index << ',' << f.gop << ',' << int(f.keyframe) << ',' << f.size
                << ',' << now - f.producedUs << '\n';
    }
    droppedFrames_ += dropped.size();
    droppedSinceWrite_ += dropped.size();
  }

  bool writeFrame(const qvideo::QueuedFrame& f) {
    if (f.keyframe) {
      if (stream_) {
        (void)sock_->writeChain(*stream_, quic::Buf::create(0), true);
      }
      auto id = sock_->createUnidirectionalStream();
      if (id.hasError()) {
        finish("cannot open GOP stream");
        return false;
      }
      stream_ = *id;
    } else if (!stream_) {
      return true;  // every session starts at a keyframe, so this never happens
    }
    qvideo::FrameHeader h;
    h.keyframe = f.keyframe ? 1 : 0;
    h.index = f.index;
    h.size = f.size;
    h.rateKbps = params_.rateKbps;
    h.sendUs = f.producedUs;
    // The queue is FIFO in frame order: everything dropped since the last
    // write lies right before this frame.
    h.skippedBefore = uint32_t(droppedSinceWrite_);
    auto buf = quic::Buf::create(h.size);
    std::memset(buf->writableData(), 0, h.size);
    std::memcpy(buf->writableData(), &h, sizeof(h));
    buf->append(h.size);
    if (sock_->writeChain(*stream_, std::move(buf), false).hasError()) {
      finish("write failed");
      return false;
    }
    appBytes_ += h.size;
    droppedSinceWrite_ = 0;
    framesCsv_ << f.index << ',' << int(h.keyframe) << ',' << h.size << ',' << h.sendUs << ','
               << qvideo::nowUs() << ',' << *stream_ << '\n';
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
    const uint64_t t = qvideo::nowUs();
    const uint64_t unsent = quicUnsent(info);
    std::ostringstream row;
    row << t << ',' << quic::congestionControlTypeToString(info.congestionControlType) << ','
        << info.srtt.count() << ',' << minRtt << ','
        << info.lrtt.count() << ',' << info.congestionWindow << ',' << info.bytesInFlight << ','
        << pacingBps << ',' << bwBps << ',' << info.bytesSent << ',' << info.bytesAcked << ','
        << info.totalBytesRetransmitted << ',' << info.totalPacketsMarkedLost << ',' << appBytes_
        << ',' << queue_->bytes() << ',' << queue_->oldestAgeUs(t) << ',' << unsent << ','
        << queue_->bytes() + unsent << ',' << droppedFrames_ << '\n';
    statsCsv_ << row.str();
    statsCsv_.flush();
    framesCsv_.flush();
    dropsCsv_.flush();
    if (acks_) {
      acks_->flush();
    }
    if (owd_) {
      owd_->flush(false);
    }
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
    if (pumpTimer_) {
      pumpTimer_->cancelTimeout();
    }
    dropsCsv_.flush();
    framesCsv_.flush();
    statsCsv_.flush();
    if (acks_) {
      acks_->flush();
    }
    if (owd_) {
      owd_->flush(true);
    }
    LOG(INFO) << (request_ ? request_->clientId : std::string("?")) << " session end: " << why;
  }

  folly::EventBase* evb_;
  const Config& cfg_;
  std::shared_ptr<quic::QuicSocket> sock_;
  std::shared_ptr<PacingObserver> pacing_;
  std::shared_ptr<AckRecorder> acks_;
  std::shared_ptr<OwdRecorder> owd_;
  std::string requestBuf_;
  std::optional<qvideo::Request> request_;
  qvideo::VideoParams params_;
  qvideo::Schedule schedule_;
  uint64_t nextIndex_{0};
  uint64_t appBytes_{0};
  std::optional<StreamId> stream_;
  std::unique_ptr<folly::AsyncTimeout> frameTimer_;
  std::unique_ptr<folly::AsyncTimeout> statsTimer_;
  std::unique_ptr<folly::AsyncTimeout> pumpTimer_;
  std::optional<qvideo::SendQueue> queue_;
  uint64_t droppedFrames_{0};
  uint64_t droppedSinceWrite_{0};
  std::ofstream dropsCsv_;
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
  if (FLAGS_owd) {
    // Ask clients for per-packet receive timestamps in their ACKs (OwdRecorder).
    ts.maybeAckReceiveTimestampsConfigSentToPeer =
        quic::AckReceiveTimestampsConfig{.maxReceiveTimestampsPerAck = 64, .receiveTimestampsExponent = 0};
    ts.maxReceiveTimestampsPerAckStored = 64;
    // IETF draft-02 format: the legacy mvfst format only reports a gap-free
    // suffix of packets and drops to ~0 % coverage once there is loss.
    ts.enableIetfAckReceiveTimestamps = true;
    ts.advertiseLegacyAckReceiveTimestamps = false;
    ts.sendDraft02AckReceiveTimestamps = true;
  }
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
