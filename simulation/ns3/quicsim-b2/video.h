// Video sender and sink over one TCP connection per client: the qvideo-server /
// qvideo-client models (frame sizes, live schedule, GOP-aware send queue, playback)
// taken unchanged from qvideo/src, and the testbed's per-client record files.
#pragma once

#include "flow.h"
#include "qvideo/Common.h"
#include "qvideo/Playback.h"
#include "qvideo/SendQueue.h"

#include "ns3/internet-module.h"

#include <limits>
#include <sstream>

namespace quicsim {

// The testbed's per-packet size columns hold the QUIC packet's encoded size (UDP
// payload): router skb->len - 42. Here the same quantity: IPv4 length - 28. With the
// segment size set so a full data packet is 1260 B of IP, a full segment reads 1232,
// as on the testbed (FLAG: equal wire size, not equal payload).
constexpr uint32_t kTcpIpHeader = 20 + 20 + 12;  // IPv4 + TCP + timestamps option
inline uint32_t encodedSize(uint32_t payload) { return payload + kTcpIpHeader - 28; }

struct VideoConfig {
  qvideo::VideoParams video;    // rateKbps set per client
  uint64_t sendBufferMs{1000};
  uint32_t statsMs{50};         // sender -cc.csv
  uint32_t clientStatsMs{100};  // client -playback.csv
  uint32_t bufferMs{600};
  uint32_t segment{1208};
  bool pktLog{true};
  std::string pubDir;           // <run>/publishers/<pub>
  std::string clientDir;        // <run>/clients
};

class VideoSender : public ns3::Application {
 public:
  VideoSender(VideoFlow* f, const VideoConfig& c, ns3::Address peer, ns3::Time leaveAt)
      : f_(f), cfg_(c), peer_(peer), leaveAt_(leaveAt) {
    params_ = c.video;
    params_.rateKbps = f->rateKbps;
  }

  void StartApplication() override {
    using namespace ns3;
    sock_ = DynamicCast<TcpSocketBase>(Socket::CreateSocket(GetNode(), TcpSocketFactory::GetTypeId()));
    obs_ = CreateObject<TcpBbrObs>();
    obs_->hook = [this](Ptr<TcpSocketState> tcb, const TcpRateOps::TcpRateSample& rs, TcpBbrObs*) {
      tcb_ = tcb;
      // CongControl runs inside ACK processing; record once it has finished.
      lossBytes_ += rs.m_bytesLoss;
      Simulator::ScheduleNow(&VideoSender::RecordAck, this, rs);
    };
    sock_->SetCongestionControlAlgorithm(obs_);
    sock_->TraceConnectWithoutContext("Tx", MakeCallback(&VideoSender::OnTx, this));
    sock_->TraceConnectWithoutContext("CongestionWindow", MakeCallback(&VideoSender::OnCwnd, this));
    sock_->TraceConnectWithoutContext("HighestSequence", MakeCallback(&VideoSender::OnHigh, this));
    sock_->SetConnectCallback(MakeCallback(&VideoSender::OnConnected, this),
                              MakeCallback(&VideoSender::OnConnectFailed, this));
    sock_->Bind();
    sock_->Connect(peer_);
  }

  void StopApplication() override { finish(); }

  void finish() {
    if (done_) return;
    done_ = true;
    frameEv_.Cancel();
    pumpEv_.Cancel();
    statsEv_.Cancel();
    writeOwd();
    for (Csv* c : {&acks_, &sent_, &frames_, &drops_, &cc_, &pkts_, &pktacks_}) c->close();
    if (sock_) sock_->Close();
  }

 private:
  // ── session ──────────────────────────────────────────────────────────────
  void OnConnected(ns3::Ptr<ns3::Socket>) {
    using namespace ns3;
    const std::string base = cfg_.pubDir + "/" + f_->sid;
    acks_.open(base + "-acks.csv",
               "mono_us,sent_mono_us,rtt_us,min_rtt_us,srtt_us,rate_valid,app_limited,send_bps,ack_bps,"
               "bbr_bw_bps,cwnd_bytes,inflight_bytes,stream_buffer_bytes,bytes_acked_total,"
               "bytes_sent_at_send,phase,newly_lost,relay_saturated,seq,owd_us");
    sent_.open(base + "-sent.csv", "send_mono_us,bytes,seq");
    frames_.open(base + "-frames.csv", "index,keyframe,size,send_us,write_us,stream");
    drops_.open(base + "-drops.csv", "t_us,index,gop,keyframe,size,age_us");
    cc_.open(base + "-cc.csv",
             "t_us,cc,srtt_us,min_rtt_us,latest_rtt_us,cwnd_bytes,inflight_bytes,pacing_bps,bw_est_bps,"
             "bytes_sent,bytes_acked,retx_bytes,lost_packets,app_bytes,queue_bytes,queue_age_us,"
             "quic_unsent_bytes,backlog_bytes,dropped_frames");
    if (cfg_.pktLog) {
      pkts_.open(base + "-pkts.csv", "send_mono_us,pn,size");
      pktacks_.open(base + "-pktacks.csv", "ack_mono_us,ranges");
    }
    schedule_.startUs = uint64_t(simClock().unixUs(simClock().epoch));
    schedule_.phaseUs = uint64_t(f_->phaseMs) * 1000;
    schedule_.fps = params_.fps;
    schedule_.gopFrames = params_.gopFrames;
    queue_.emplace(cfg_.sendBufferMs * 1000);
    nextIndex_ = schedule_.firstFrame(uint64_t(simClock().unixUsNow()));
    scheduleFrame();
    statsEv_ = Simulator::Schedule(MilliSeconds(cfg_.statsMs), &VideoSender::OnStats, this);
    if (cfg_.sendBufferMs > 0) pumpEv_ = Simulator::Schedule(MicroSeconds(5000), &VideoSender::OnPump, this);
    if (!leaveAt_.IsZero()) Simulator::Schedule(leaveAt_ - Simulator::Now(), &VideoSender::finish, this);
  }

  void OnConnectFailed(ns3::Ptr<ns3::Socket>) {
    throw std::runtime_error("video connection failed: " + f_->sid);
  }

  void scheduleFrame() {
    const int64_t now = simClock().unixUsNow();
    const int64_t due = int64_t(schedule_.timeUs(nextIndex_));
    frameEv_ = ns3::Simulator::Schedule(ns3::MicroSeconds(due > now ? due - now : 0), &VideoSender::OnFrame, this);
  }

  // Produce every frame whose time has passed; the queue decides what reaches TCP.
  void OnFrame() {
    if (done_) return;
    std::vector<qvideo::QueuedFrame> dropped;
    const uint64_t now = uint64_t(simClock().unixUsNow());
    for (; schedule_.timeUs(nextIndex_) <= now; ++nextIndex_) {
      const uint64_t k = nextIndex_;
      queue_->push({k, k / params_.gopFrames, k % params_.gopFrames == 0, qvideo::frameSize(params_, k), now},
                   dropped);
    }
    logDrops(dropped);
    pump();
    scheduleFrame();
  }

  void OnPump() {
    if (done_) return;
    pump();
    pumpEv_ = ns3::Simulator::Schedule(ns3::MicroSeconds(5000), &VideoSender::OnPump, this);
  }

  uint64_t unsent() const {
    const uint64_t sentNew = f_->haveSeq0 ? uint64_t(f_->offsetOf(f_->highTx)) : 0;
    return appBytes_ > sentNew ? appBytes_ - sentNew : 0;
  }

  // Hand queued frames to TCP while its unsent data is below one cwnd (Server.cpp pump()).
  void pump() {
    std::vector<qvideo::QueuedFrame> dropped;
    queue_->dropStale(uint64_t(simClock().unixUsNow()), dropped);
    logDrops(dropped);
    uint64_t pending = unsent();
    const uint64_t cap = cfg_.sendBufferMs > 0 ? std::max<uint64_t>(cwnd_, 1) : std::numeric_limits<uint64_t>::max();
    while (!queue_->empty() && pending < cap) {
      const qvideo::QueuedFrame fr = queue_->front();
      queue_->pop();
      writeFrame(fr);
      pending += fr.size;
    }
  }

  void logDrops(const std::vector<qvideo::QueuedFrame>& dropped) {
    const int64_t now = simClock().unixUsNow();
    for (const auto& fr : dropped) {
      drops_ << now << ',' << fr.index << ',' << fr.gop << ',' << int(fr.keyframe) << ',' << fr.size << ','
             << now - int64_t(fr.producedUs) << '\n';
    }
    droppedFrames_ += dropped.size();
    droppedSinceWrite_ += dropped.size();
  }

  void writeFrame(const qvideo::QueuedFrame& fr) {
    if (fr.keyframe) stream_ = streams_++ * 4 + 3;  // server unidirectional stream ids, one per GOP
    if (sock_->Send(ns3::Create<ns3::Packet>(fr.size), 0) < 0) {
      throw std::runtime_error("socket send failed: " + f_->sid + " (send buffer too small)");
    }
    appBytes_ += fr.size;
    f_->frames.push_back({appBytes_, fr.index, fr.keyframe, fr.size, fr.producedUs, uint32_t(droppedSinceWrite_)});
    droppedSinceWrite_ = 0;
    frames_ << fr.index << ',' << int(fr.keyframe) << ',' << fr.size << ',' << fr.producedUs << ','
            << simClock().unixUsNow() << ',' << stream_ << '\n';
  }

  // ── transport events ─────────────────────────────────────────────────────
  void OnCwnd(uint32_t, uint32_t now) { cwnd_ = now; }
  void OnHigh(ns3::SequenceNumber32, ns3::SequenceNumber32 now) { f_->highTx = now; }

  void OnTx(ns3::Ptr<const ns3::Packet> p, const ns3::TcpHeader& h, ns3::Ptr<const ns3::TcpSocketBase>) {
    using namespace ns3;
    FlowTag tag;
    tag.kind = Kind::Video;
    tag.flow = f_->index;
    tag.sendNs = Simulator::Now().GetNanoSeconds();
    tag.tx = std::numeric_limits<uint64_t>::max();  // handshake / control
    const uint32_t len = p->GetSize();
    if (len > 0 && !done_) {
      if (!f_->haveSeq0) {
        f_->haveSeq0 = true;
        f_->seq0 = h.GetSequenceNumber();
        f_->highTx = f_->seq0;
      }
      const uint32_t off = f_->offsetOf(h.GetSequenceNumber());
      const uint64_t tx = f_->txs.size();
      f_->sentTotal += len;
      f_->txs.push_back({off, len, tag.sendNs, -1, f_->sentTotal});
      auto [it, fresh] = f_->segs.try_emplace(off, Seg{len, tx, -1});
      if (!fresh) {
        it->second.lastTx = tx;
        f_->retxBytes += len;
      }
      tag.tx = tx;
      const int64_t mono = simClock().monoUsNow();
      sent_ << mono << ',' << encodedSize(len) << ',' << nextSeq() << '\n';
      if (pkts_.isOpen()) pkts_ << mono << ',' << tx << ',' << encodedSize(len) << '\n';
      ++f_->owdBins[mono / 5000].sent;
    }
    p->AddPacketTag(tag);
  }

  // One acks.csv row per ACK that newly acknowledges data (AckRecorder in Server.cpp).
  void RecordAck(ns3::TcpRateOps::TcpRateSample rs) {
    using namespace ns3;
    if (done_ || !f_->haveSeq0 || !tcb_) return;
    const uint32_t ackOff = f_->offsetOf(tcb_->m_lastAckedSeq);
    std::vector<uint64_t> acked;
    uint64_t largest = 0;
    bool any = false;
    for (auto it = f_->segs.begin(); it != f_->segs.end() && it->first + it->second.len <= ackOff;) {
      const Seg& s = it->second;
      largest = s.arrivedTx >= 0 ? uint64_t(s.arrivedTx) : s.lastTx;
      acked.push_back(largest);
      any = true;
      it = f_->segs.erase(it);
    }
    if (!any) return;  // duplicate / SACK-only ACK: no newly acked packet in the QUIC sense (FLAG)
    f_->ackedOff = ackOff;
    const Tx& t = f_->txs[largest];
    const int64_t nowNs = Simulator::Now().GetNanoSeconds();
    const uint32_t lost = (lossBytes_ + cfg_.segment - 1) / cfg_.segment;
    lossBytes_ = 0;
    f_->lostPackets += lost;
    const double sendUs = double(rs.m_sendElapsed.GetMicroSeconds());
    const double ackUs = double(rs.m_ackElapsed.GetMicroSeconds());
    const bool rateValid = sendUs > 0 && ackUs > 0 && rs.m_delivered > 0;
    const double sendBps = rateValid ? rs.m_delivered * 8e6 / sendUs : 0;
    const double ackBps = rateValid ? rs.m_delivered * 8e6 / ackUs : 0;
    const int64_t minRtt = tcb_->m_minRtt == Time::Max() ? 0 : tcb_->m_minRtt.GetMicroSeconds();
    acks_ << simClock().monoUsNow() << ',' << simClock().monoUs(NanoSeconds(t.sendNs)) << ','
          << (nowNs - t.sendNs) / 1000 << ',' << minRtt << ',' << tcb_->m_srtt.Get().GetMicroSeconds() << ','
          << int(rateValid) << ',' << int(rs.m_isAppLimited) << ',' << uint64_t(sendBps) << ','
          << uint64_t(ackBps) << ',' << obs_->bwBps() << ',' << tcb_->m_cWnd.Get() << ','
          << tcb_->m_bytesInFlight.Get() << ',' << queue_->bytes() + unsent() << ',' << ackOff << ','
          << t.sentTotal << ',' << obs_->phase() << ',' << lost << ",0," << nextSeq() << ',';
    if (t.arriveNs >= 0) acks_ << (t.arriveNs - t.sendNs) / 1000;
    acks_ << '\n';
    if (pktacks_.isOpen()) {
      std::sort(acked.begin(), acked.end());
      std::ostringstream r;
      for (size_t i = 0; i < acked.size();) {
        size_t j = i;
        while (j + 1 < acked.size() && acked[j + 1] == acked[j] + 1) ++j;
        r << (i ? ";" : "") << acked[i] << '-' << acked[j];
        i = j + 1;
      }
      pktacks_ << simClock().monoUsNow() << ',' << r.str() << '\n';
    }
  }

  void OnStats() {
    if (done_) return;
    using namespace ns3;
    const int64_t t = simClock().unixUsNow();
    const uint64_t u = unsent();
    const int64_t srtt = tcb_ ? tcb_->m_srtt.Get().GetMicroSeconds() : 0;
    const int64_t minRtt = tcb_ && tcb_->m_minRtt != Time::Max() ? tcb_->m_minRtt.GetMicroSeconds() : 0;
    const int64_t lrtt = tcb_ ? tcb_->m_lastRtt.Get().GetMicroSeconds() : 0;
    const uint64_t pacing = tcb_ ? tcb_->m_pacingRate.Get().GetBitRate() : 0;
    const uint64_t inflight = tcb_ ? tcb_->m_bytesInFlight.Get() : 0;
    cc_ << t << ",bbr," << srtt << ',' << minRtt << ',' << lrtt << ',' << cwnd_ << ',' << inflight << ','
        << pacing << ',' << obs_->bwBps() << ',' << f_->sentTotal << ',' << f_->ackedOff << ',' << f_->retxBytes
        << ',' << f_->lostPackets << ',' << appBytes_ << ',' << queue_->bytes() << ','
        << queue_->oldestAgeUs(uint64_t(t)) << ',' << u << ',' << queue_->bytes() + u << ',' << droppedFrames_
        << '\n';
    statsEv_ = Simulator::Schedule(MilliSeconds(cfg_.statsMs), &VideoSender::OnStats, this);
  }

  // -owd.csv: gap-free 5 ms grid of send time from the first bin (OwdRecorder::flush).
  void writeOwd() {
    if (f_->owdBins.empty()) return;
    Csv out(cfg_.pubDir + "/" + f_->sid + "-owd.csv",
            "t_us,bin_mono_us,packets_sent,packets_timed,owd_min_us,owd_mean_us,owd_max_us");
    const int64_t unixMinusMonoUs = simClock().unix0Ns / 1000 - simClock().mono0Ns / 1000;
    for (int64_t bin = f_->owdBins.begin()->first; bin <= f_->owdBins.rbegin()->first; ++bin) {
      auto it = f_->owdBins.find(bin);
      out << bin * 5000 + unixMinusMonoUs << ',' << bin * 5000 << ',';
      if (it == f_->owdBins.end()) {
        out << "0,0,,,\n";
        continue;
      }
      const OwdBin& b = it->second;
      out << b.sent << ',' << b.timed << ',';
      if (b.timed) out << b.minUs << ',' << b.sumUs / b.timed << ',' << b.maxUs;
      else out << ",,";
      out << '\n';
    }
  }

  VideoFlow* f_;
  VideoConfig cfg_;
  qvideo::VideoParams params_;
  ns3::Address peer_;
  ns3::Time leaveAt_;
  ns3::Ptr<ns3::TcpSocketBase> sock_;
  ns3::Ptr<TcpBbrObs> obs_;
  ns3::Ptr<ns3::TcpSocketState> tcb_;
  qvideo::Schedule schedule_;
  std::optional<qvideo::SendQueue> queue_;
  uint64_t nextIndex_{0}, appBytes_{0}, droppedFrames_{0}, droppedSinceWrite_{0}, stream_{3}, streams_{0};
  uint64_t lossBytes_{0};
  uint32_t cwnd_{0};
  bool done_{false};
  ns3::EventId frameEv_, pumpEv_, statsEv_;
  Csv acks_, sent_, frames_, drops_, cc_, pkts_, pktacks_;
};

class VideoSink : public ns3::Application {
 public:
  // delAckCount / delAckTimeout: this client's receiver ACK policy (plan.py profile); the
  // accepted socket inherits them from the listening socket (TcpSocketBase copy constructor).
  VideoSink(VideoFlow* f, const VideoConfig& c, uint16_t port, uint32_t fps, uint32_t delAckCount,
            ns3::Time delAckTimeout)
      : f_(f), cfg_(c), port_(port), playback_(uint64_t(1e6 / fps), uint64_t(c.bufferMs) * 1000),
        delAckCount_(delAckCount), delAckTimeout_(delAckTimeout) {}

  void StartApplication() override {
    using namespace ns3;
    listen_ = Socket::CreateSocket(GetNode(), TcpSocketFactory::GetTypeId());
    listen_->SetAttribute("DelAckCount", UintegerValue(delAckCount_));
    listen_->SetAttribute("DelAckTimeout", TimeValue(delAckTimeout_));
    listen_->Bind(InetSocketAddress(Ipv4Address::GetAny(), port_));
    listen_->Listen();
    listen_->SetAcceptCallback(MakeNullCallback<bool, Ptr<Socket>, const Address&>(),
                               MakeCallback(&VideoSink::OnAccept, this));
    frames_.open(cfg_.clientDir + "/" + f_->sid + "-frames.csv", "index,keyframe,size,send_us,recv_us,owd_us,late_us");
    play_.open(cfg_.clientDir + "/" + f_->sid + "-playback.csv",
               "t_us,frames,bytes,goodput_bps,buffer_ms,stalls,stall_ms,owd_ms,skipped_frames");
    statsEv_ = Simulator::Schedule(MilliSeconds(cfg_.clientStatsMs), &VideoSink::OnStats, this);
  }

  void StopApplication() override {
    stopped_ = true;  // data still in flight after the run's end is not recorded (files are closed)
    statsEv_.Cancel();
    frames_.close();
    play_.close();
  }

 private:
  void OnAccept(ns3::Ptr<ns3::Socket> s, const ns3::Address&) {
    using namespace ns3;
    conn_ = s;
    s->SetRecvCallback(MakeCallback(&VideoSink::OnRecv, this));
    s->TraceConnectWithoutContext("Rx", MakeCallback(&VideoSink::OnRx, this));
    s->TraceConnectWithoutContext("Tx", MakeCallback(&VideoSink::OnAckTx, this));
  }

  // Every segment as it arrives, before reassembly: the transmission's exact OWD.
  void OnRx(ns3::Ptr<const ns3::Packet> p, const ns3::TcpHeader&, ns3::Ptr<const ns3::TcpSocketBase>) {
    if (stopped_) return;
    FlowTag tag;
    if (p->GetSize() == 0 || !p->PeekPacketTag(tag) || tag.kind != Kind::Video || tag.tx >= f_->txs.size()) return;
    Tx& t = f_->txs[tag.tx];
    if (t.arriveNs >= 0) return;
    t.arriveNs = ns3::Simulator::Now().GetNanoSeconds();
    if (auto it = f_->segs.find(t.off); it != f_->segs.end() && it->second.arrivedTx < 0) {
      it->second.arrivedTx = int64_t(tag.tx);
    }
    const int64_t owd = (t.arriveNs - t.sendNs) / 1000;
    OwdBin& b = f_->owdBins[simClock().monoUs(ns3::NanoSeconds(t.sendNs)) / 5000];
    b.minUs = b.timed ? std::min(b.minUs, owd) : owd;
    b.maxUs = b.timed ? std::max(b.maxUs, owd) : owd;
    b.sumUs += owd;
    ++b.timed;
  }

  void OnAckTx(ns3::Ptr<const ns3::Packet> p, const ns3::TcpHeader&, ns3::Ptr<const ns3::TcpSocketBase>) {
    FlowTag tag;
    tag.kind = Kind::VideoAck;
    tag.flow = f_->index;
    tag.tx = std::numeric_limits<uint64_t>::max();
    tag.sendNs = ns3::Simulator::Now().GetNanoSeconds();
    p->AddPacketTag(tag);
  }

  void OnRecv(ns3::Ptr<ns3::Socket> s) {
    if (stopped_) return;
    while (auto p = s->Recv()) f_->recvOff += p->GetSize();
    const uint64_t now = uint64_t(simClock().unixUsNow());
    while (!f_->frames.empty() && f_->frames.front().end <= f_->recvOff) {
      const FrameRec fr = f_->frames.front();
      f_->frames.pop_front();
      const int64_t late = playback_.onFrame(fr.index, now, fr.skippedBefore);
      const uint64_t owd = now > fr.sendUs ? now - fr.sendUs : 0;
      ++nFrames_;
      bytes_ += fr.size;
      owdSumUs_ += owd;
      ++owdCount_;
      frames_ << fr.index << ',' << int(fr.keyframe) << ',' << fr.size << ',' << fr.sendUs << ',' << now << ','
              << owd << ',' << late << '\n';
    }
  }

  void OnStats() {
    const uint64_t now = uint64_t(simClock().unixUsNow());
    const double dt = lastStatsUs_ ? double(now - lastStatsUs_) / 1e6 : 0;
    const double goodput = dt > 0 ? double(bytes_ - lastBytes_) * 8 / dt : 0;
    const double owdMs = owdCount_ ? double(owdSumUs_) / double(owdCount_) / 1000 : 0;
    play_ << now << ',' << nFrames_ << ',' << bytes_ << ',' << uint64_t(goodput) << ','
          << playback_.bufferUs(now) / 1000 << ',' << playback_.stalls() << ',' << playback_.stallUs() / 1000 << ','
          << owdMs << ',' << playback_.skipped() << '\n';
    lastStatsUs_ = now;
    lastBytes_ = bytes_;
    owdSumUs_ = 0;
    owdCount_ = 0;
    statsEv_ = ns3::Simulator::Schedule(ns3::MilliSeconds(cfg_.clientStatsMs), &VideoSink::OnStats, this);
  }

  VideoFlow* f_;
  VideoConfig cfg_;
  uint16_t port_;
  qvideo::Playback playback_;
  uint32_t delAckCount_;
  ns3::Time delAckTimeout_;
  ns3::Ptr<ns3::Socket> listen_, conn_;
  uint64_t nFrames_{0}, bytes_{0}, lastBytes_{0}, lastStatsUs_{0}, owdSumUs_{0}, owdCount_{0};
  ns3::EventId statsEv_;
  bool stopped_{false};
  Csv frames_, play_;
};

}  // namespace quicsim
