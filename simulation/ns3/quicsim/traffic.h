// Background / stimulus UDP sources and their sink: qtraffic's departure processes
// (qvideo/src/Departures.h, Ppbp.h, unchanged) and its record files under traffic/.
#pragma once

#include "common.h"
#include "qvideo/Departures.h"

#include "ns3/internet-module.h"

#include <cmath>
#include <optional>

namespace quicsim {

struct BgConfig {
  uint32_t event{0};          // index among the run's traffic events (tag flow id high bits)
  std::string id;             // scenario event id: traffic/<id>-*.csv
  std::string process;        // "poisson" (Departures.h) or "pace" (qtraffic's 1 ms credit loop)
  std::vector<qvideo::Burst> bursts;
  std::vector<double> weights{1.0};
  uint64_t seed{1};
  uint32_t packet{1200};      // UDP payload bytes
  ns3::Time start;            // simulator time of T0 + at_s
  double durationS{0};
  ns3::Address dest;
  std::string outPrefix;      // <run>/traffic/<id>
  uint16_t basePort{0};       // local source port of flow i = basePort + i
  bool lazy{false};           // sockets open at start, close at end (port reuse over time)
};

class BgSource : public ns3::Application {
 public:
  explicit BgSource(BgConfig c) : c_(std::move(c)), steps_(c_.bursts) {}

  void StartApplication() override {
    using namespace ns3;
    {
      Csv b(c_.outPrefix + "-bursts.csv", "burst,start_s,duration_s,rate_mbps");
      for (size_t i = 0; i < c_.bursts.size(); ++i) {
        b << i << ',' << c_.bursts[i].startS << ',' << c_.bursts[i].durationS << ',' << c_.bursts[i].rateMbps << '\n';
      }
    }
    const size_t n = c_.process == "poisson" ? c_.weights.size() : 1;
    // One UDP socket per flow, so every flow has its own 5-tuple on the wire (fq_codel / cake hash it).
    // Above 300 flows per event the port blocks of consecutive events overlap (plan.py stride); such a
    // flow gets an ephemeral port instead (49152-65535), as before item 5, but explicitly, and a failed
    // bind stops the run instead of passing silently. Records use the label basePort + i either way.
    // lazy (plan "lazy=1", stage C port reuse, user 2026-11-19 U2): the sockets open at the source's own start
    // and close at its end, so the planner can give a route's ports to a later source; otherwise all at t = 0.
    if (c_.lazy) {
      Simulator::Schedule(c_.start - Simulator::Now(), &BgSource::openSockets, this, n);
    } else {
      openSockets(n);
    }
    seq_.assign(n, 0);
    bytes_.assign(n, 0);
    first_.assign(n, 0);
    last_.assign(n, 0);
    sent_.open(c_.outPrefix + "-sent.csv", "t_us,active_bursts,offered_mbps,sent_bytes,send_errors");
    if (c_.process == "poisson") sent5_.open(c_.outPrefix + "-sent5.csv", "t_us,sent_bytes");
    startUs_ = simClock().unixUs(c_.start);
    endUs_ = startUs_ + int64_t(c_.durationS * 1e6);
    binStart_ = bin5Start_ = startUs_;
    if (c_.process == "poisson") {
      src_.emplace(steps_, c_.weights, c_.packet, uint64_t(c_.durationS * 1e6), c_.seed);
      Simulator::Schedule(c_.start - Simulator::Now(), &BgSource::NextDeparture, this);
    } else if (c_.process == "pace") {
      Simulator::Schedule(c_.start - Simulator::Now(), &BgSource::Tick, this);
    } else {
      throw std::runtime_error("traffic process not supported in the simulation: " + c_.process);
    }
  }

  void StopApplication() override { finish(); }

  void openSockets(size_t n) {
    using namespace ns3;
    for (size_t i = 0; i < n; ++i) {
      auto s = Socket::CreateSocket(GetNode(), UdpSocketFactory::GetTypeId());
      if (s->Bind(InetSocketAddress(Ipv4Address::GetAny(), uint16_t(c_.basePort + i))) != 0 && s->Bind() != 0) {
        throw std::runtime_error("bg flow " + std::to_string(i) + " of " + c_.outPrefix + ": no source port left");
      }
      s->Connect(c_.dest);
      socks_.push_back(s);
    }
  }

  void finish() {
    if (done_) return;
    done_ = true;
    if (c_.lazy) {
      for (auto& s : socks_) s->Close();   // frees the ports for a later source on this route
    }
    advance(endUs_);
    sent_.close();
    sent5_.close();
    if (c_.process != "poisson") return;
    Csv f(c_.outPrefix + "-flows.csv", "flow,src_port,weight,packets,bytes,first_us,last_us,mean_mbps");
    for (size_t i = 0; i < socks_.size(); ++i) {
      const double span = last_[i] > first_[i] ? double(last_[i] - first_[i]) : 0;
      f << i << ',' << c_.basePort + i << ',' << c_.weights[i] << ',' << seq_[i] << ',' << bytes_[i] << ','
        << first_[i] << ',' << last_[i] << ',' << (span > 0 ? double(bytes_[i]) * 8 / span : 0) << '\n';
    }
  }

 private:
  void send(size_t flow, uint32_t bytes) {
    using namespace ns3;
    auto p = Create<Packet>(bytes);
    FlowTag tag;
    tag.kind = Kind::Bg;
    tag.flow = (c_.event << 16) | uint32_t(flow);
    tag.tx = seq_[flow]++;
    tag.sendNs = Simulator::Now().GetNanoSeconds();
    p->AddPacketTag(tag);
    const int64_t now = simClock().unixUsNow();
    advance(now);
    const int n = socks_[flow]->Send(p);
    if (n < 0) {
      ++binErrors_;
      return;
    }
    binBytes_ += uint64_t(n);
    bin5Bytes_ += uint64_t(n);
    bytes_[flow] += uint64_t(n);
    first_[flow] = first_[flow] ? first_[flow] : now;
    last_[flow] = now;
  }

  // qtraffic SendLog on a regular grid: rows at each bin's end (100 ms; 5 ms for sent5).
  void advance(int64_t now) {
    while (now - bin5Start_ >= 5000 && sent5_.isOpen()) {
      bin5Start_ += 5000;
      sent5_ << bin5Start_ << ',' << bin5Bytes_ << '\n';
      bin5Bytes_ = 0;
    }
    while (now - binStart_ >= 100000) {
      binStart_ += 100000;
      size_t hint = 0;
      const double rate = steps_.at(uint64_t(binStart_ - startUs_), hint);
      int active = 0;
      for (const auto& b : c_.bursts) {
        const double t = double(binStart_ - startUs_) / 1e6;
        active += t >= b.startS && t < b.startS + b.durationS;
      }
      sent_ << binStart_ << ',' << active << ',' << rate << ',' << binBytes_ << ',' << binErrors_ << '\n';
      binBytes_ = binErrors_ = 0;
    }
  }

  void NextDeparture() {
    if (done_) return;
    if (pending_) send(pending_->flow, pending_->bytes);
    pending_ = src_->next();
    if (!pending_) {
      ns3::Simulator::Schedule(simClock().atUnixUs(endUs_) - ns3::Simulator::Now(), &BgSource::finish, this);
      return;
    }
    const ns3::Time due = simClock().atUnixUs(startUs_ + int64_t(pending_->tUs));
    ns3::Simulator::Schedule(std::max(due - ns3::Simulator::Now(), ns3::Time(0)), &BgSource::NextDeparture, this);
  }

  // qtraffic --process=pace: 1 ms ticks, credit at most 10 ms behind (Traffic.cpp runSend).
  void Tick() {
    if (done_) return;
    const int64_t now = simClock().unixUsNow();
    if (now >= endUs_) {
      finish();
      return;
    }
    size_t hint = 0;
    const double rateBps = steps_.at(uint64_t(now - startUs_), hint) * 1e6;
    const int64_t prev = lastTick_ ? lastTick_ : now;
    credit_ = std::min(credit_ + rateBps / 8 * double(now - prev) / 1e6, rateBps / 8 * 0.01 + c_.packet);
    lastTick_ = now;
    while (credit_ >= c_.packet) {
      send(0, c_.packet);
      credit_ -= c_.packet;
    }
    ns3::Simulator::Schedule(ns3::MicroSeconds(1000), &BgSource::Tick, this);
  }

  BgConfig c_;
  qvideo::RateSteps steps_;
  std::optional<qvideo::PoissonSource> src_;
  std::optional<qvideo::Departure> pending_;
  std::vector<ns3::Ptr<ns3::Socket>> socks_;
  std::vector<uint64_t> seq_, bytes_;
  std::vector<int64_t> first_, last_;
  int64_t startUs_{0}, endUs_{0}, binStart_{0}, bin5Start_{0}, lastTick_{0};
  uint64_t binBytes_{0}, bin5Bytes_{0}, binErrors_{0};
  double credit_{0};
  bool done_{false};
  Csv sent_, sent5_;
};

// qtraffic --mode=recv (UDP): per 100 ms packets, bytes, lost (sequence gaps), OWD.
class BgSink : public ns3::Application {
 public:
  BgSink(std::string outPrefix, uint16_t port) : out_(std::move(outPrefix)), port_(port) {}

  void StartApplication() override {
    using namespace ns3;
    sock_ = Socket::CreateSocket(GetNode(), UdpSocketFactory::GetTypeId());
    sock_->Bind(InetSocketAddress(Ipv4Address::GetAny(), port_));
    sock_->SetRecvCallback(MakeCallback(&BgSink::OnRecv, this));
    csv_.open(out_ + "-recv.csv", "t_us,packets,bytes,lost,owd_mean_us,owd_max_us");
    binStart_ = simClock().unixUsNow();
    ev_ = Simulator::Schedule(MilliSeconds(100), &BgSink::Flush, this);
  }

  void StopApplication() override {
    ev_.Cancel();
    csv_.close();
  }

 private:
  void OnRecv(ns3::Ptr<ns3::Socket> s) {
    while (auto p = s->Recv()) {
      FlowTag tag;
      if (!p->PeekPacketTag(tag)) continue;
      ++packets_;
      bytes_ += p->GetSize();
      auto& next = expect_[tag.flow];
      if (tag.tx > next) lost_ += tag.tx - next;
      next = std::max(next, tag.tx + 1);
      const int64_t owd = (ns3::Simulator::Now().GetNanoSeconds() - tag.sendNs) / 1000;
      owdSum_ += owd;
      owdMax_ = std::max(owdMax_, owd);
    }
  }

  void Flush() {
    binStart_ += 100000;
    csv_ << binStart_ << ',' << packets_ << ',' << bytes_ << ',' << lost_ << ','
         << (packets_ ? owdSum_ / int64_t(packets_) : 0) << ',' << owdMax_ << '\n';
    packets_ = bytes_ = lost_ = 0;
    owdSum_ = owdMax_ = 0;
    ev_ = ns3::Simulator::Schedule(ns3::MilliSeconds(100), &BgSink::Flush, this);
  }

  std::string out_;
  uint16_t port_;
  ns3::Ptr<ns3::Socket> sock_;
  std::map<uint32_t, uint64_t> expect_;
  uint64_t packets_{0}, bytes_{0}, lost_{0};
  int64_t owdSum_{0}, owdMax_{0}, binStart_{0};
  ns3::EventId ev_;
  Csv csv_;
};

}  // namespace quicsim
