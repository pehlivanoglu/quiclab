// Router-side records of one egress queue disc, in the testbed's formats:
//   router-metrics/<node>/<iface>.csv        25 ms tc counters (per-interval deltas)
//   router-metrics/<node>/<iface>-queue.csv  5 ms queue state (cumulative drops)
//   router-trace/<iface>-packets.csv         every packet dequeued or dropped (GT-Q)
#pragma once

#include "common.h"

#include "ns3/internet-module.h"
#include "ns3/traffic-control-module.h"

#include <sstream>
#include <unordered_map>

namespace quicsim {

constexpr uint32_t kEthHeader = 14;  // the router's skb->len includes Ethernet

// Logical 5-tuple of a tagged packet, as the testbed's tracer would print it.
struct TupleMap {
  struct Video { std::string pub, sub; uint16_t subPort; };
  struct Bg { std::string saddr, daddr; uint16_t basePort, dport; };
  std::vector<Video> video;            // by client index
  std::vector<Bg> bg;                  // by traffic event index
};

struct MonitorConfig {
  std::string node, iface, hop;        // hop "a->b"
  bool metrics{false};
  uint32_t intervalMs{25}, queueIntervalMs{5};
  bool trace{false};
  bool totals{false};                  // write <iface>-totals.csv at the end (stage C, no-trace health)
  int64_t delayNs{0};                  // netem delay of this egress (GT-Q labeler adds it back)
  uint32_t limitPackets{0};
  uint32_t ifindex{0};
  std::string runDir;
};

class EgressMonitor {
 public:
  EgressMonitor(MonitorConfig c, ns3::Ptr<ns3::QueueDisc> qd, const TupleMap* tuples)
      : c_(std::move(c)), qd_(qd), tuples_(tuples) {
    using namespace ns3;
    qd_->TraceConnectWithoutContext("Enqueue", MakeCallback(&EgressMonitor::OnEnqueue, this));
    qd_->TraceConnectWithoutContext("Dequeue", MakeCallback(&EgressMonitor::OnDequeue, this));
    qd_->TraceConnectWithoutContext("DropBeforeEnqueue", MakeCallback(&EgressMonitor::OnDropBefore, this));
    qd_->TraceConnectWithoutContext("DropAfterDequeue", MakeCallback(&EgressMonitor::OnDropAfter, this));
    if (c_.metrics) {
      const std::string base = c_.runDir + "/router-metrics/" + c_.node + "/" + c_.iface;
      main_.open(base + ".csv",
                 "timestamp_mono_ns,interval_ns,collection_duration_ns,offered_bytes,transmitted_bytes,drops,"
                 "dualpi2_drops,l_enqueued_packets,c_enqueued_packets,ecn_marks,step_marks,queue_capacity_packets,"
                 "queue_packets,queue_percent,queue_backlog_bytes,queue_memory_capacity_bytes,queue_memory_bytes,"
                 "queue_memory_percent,l_head_delay_us,c_head_delay_us,separate_queue_packets,"
                 "separate_queue_backlog_bytes,counter_reset");
      flows_.open(base + "-flows.csv", "timestamp_mono_ns,class,flow,qlen_packets,backlog_bytes,drops");
      queue_.open(base + "-queue.csv", "timestamp_mono_ns,queue_packets,queue_backlog_bytes,drops");
      Simulator::ScheduleNow(&EgressMonitor::SampleMain, this);
      Simulator::ScheduleNow(&EgressMonitor::SampleQueue, this);
    }
    if (c_.trace) {
      trace_.open(c_.runDir + "/router-trace/" + c_.iface + "-packets.csv",
                  "kind,t_enq_ns,t_deq_ns,t_drop_ns,reason,saddr,daddr,proto,sport,dport,len,hash,prio");
      Csv(c_.runDir + "/router-trace/" + c_.iface + "-unmatched-enq.csv", "kind,t_enq_ns,t_seen_ns");
      startNs_ = simClock().monoNs(Simulator::Now());
    }
  }

  void finish() {
    flushPending();
    main_.close();
    flows_.close();
    queue_.close();
    trace_.close();
    endNs_ = simClock().monoNs(ns3::Simulator::Now());
    // Packets still queued at the end were enqueued but never left: the testbed's tracer
    // stops after the run drains, so they are not counted there either.
    queuedEnd_ = qd_->GetNPackets();
    nEnq_ -= queuedEnd_;
    if (c_.totals) {
      // Queue-disc totals, written with or without the per-packet trace (light health check):
      // n_enq counts every enqueue attempt minus the packets still queued, as tracer-counts.csv.
      Csv t(c_.runDir + "/router-metrics/" + c_.node + "/" + c_.iface + "-totals.csv",
            "node,iface,hop,n_enq,n_deq,n_drop,queued_at_end,offered_bytes,transmitted_bytes");
      t << c_.node << ',' << c_.iface << ',' << c_.hop << ',' << nEnq_ << ',' << nDeq_ << ',' << nDrop_ << ','
        << queuedEnd_ << ',' << offered_ << ',' << transmitted_ << '\n';
    }
  }

  const MonitorConfig& config() const { return c_; }
  // tracer-counts.csv row (router_trace.COUNTERS and the row totals)
  void countsRow(Csv& out) const {
    out << c_.node << ',' << c_.iface << ',' << c_.ifindex << ",1,1," << startNs_ << ',' << endNs_ << ",0,"
        << nEnq_ << ',' << nDeq_ << ',' << nDrop_ << ",0,0,0,0,0," << rowsDeq_ << ',' << rowsDrop_
        << ",0,0,0,0,0,0,0,0,0,0,\n";
  }

 private:
  uint32_t wireLen(ns3::Ptr<const ns3::QueueDiscItem> item) const { return item->GetSize() + kEthHeader; }

  // A packet the AQM takes out of its queue and then drops (CoDel: DropAfterDequeue) fires the queue
  // disc's "Dequeue" trace first (ns-3 queue-disc.cc PacketDequeued, then DropAfterDequeue). It is a
  // drop only, as the testbed's tracer records it: the dequeue record is held until the next callback
  // or sample and cancelled when the same item is dropped right after (fix 2026-11-19, NOTES.md).
  void flushPending() {
    if (!pending_) return;
    transmitted_ += pendLen_;
    ++nDeq_;
    if (trace_.isOpen()) {
      trace_ << pendRow_;   // formatted at the dequeue (tags and size as they were then)
      ++rowsDeq_;
    }
    pending_ = nullptr;
  }

  void OnEnqueue(ns3::Ptr<const ns3::QueueDiscItem> item) {
    flushPending();
    offered_ += wireLen(item);
    ++nEnq_;
  }
  void OnDequeue(ns3::Ptr<const ns3::QueueDiscItem> item) {
    flushPending();
    pending_ = item;
    pendEnq_ = enqNs(item);
    pendOut_ = outNs();
    pendLen_ = wireLen(item);   // now: the device adds its own header to the packet after the dequeue
    if (trace_.isOpen()) pendRow_ = format("dequeue", item, pendEnq_, pendOut_, -1);
  }
  void OnDropBefore(ns3::Ptr<const ns3::QueueDiscItem> item, const char*) {
    flushPending();
    offered_ += wireLen(item);
    ++drops_;
    ++nEnq_;  // tracer convention: every enqueue attempt counts (enq = deq + drop)
    ++nDrop_;
    if (trace_.isOpen()) row("drop", item, simClock().monoNs(ns3::Simulator::Now()), -1, outNs());
  }
  void OnDropAfter(ns3::Ptr<const ns3::QueueDiscItem> item, const char*) {
    if (pending_ == item) {
      pending_ = nullptr;   // dequeued only to be dropped: a drop, not a dequeue
      ++dequeueThenDrop_;
    } else {
      flushPending();
    }
    ++drops_;
    ++nDrop_;
    if (trace_.isOpen()) row("drop", item, enqNs(item), -1, outNs());
  }

  // The testbed's chain is htb -> netem -> AQM: the tracer's t_enq is the packet's arrival
  // at the egress, netem then delays it, and the queue comes after; the GT-Q labeler adds
  // the delay to t_enq to get the queue entry. Here the delay is on the wire after the
  // queue. Equivalent mapping (FLAG): t_enq = arrival (= queue entry here, also what the
  // sender-log match uses), t_deq / t_drop = simulator time + delay, so
  // t_deq - (t_enq + delay) is the true sojourn and t_deq is when the testbed's packet
  // would leave the egress.
  int64_t enqNs(ns3::Ptr<const ns3::QueueDiscItem> item) const { return simClock().monoNs(item->GetTimeStamp()); }
  int64_t outNs() const { return simClock().monoNs(ns3::Simulator::Now()) + c_.delayNs; }

  void row(const char* kind, ns3::Ptr<const ns3::QueueDiscItem> item, int64_t tEnq, int64_t tDeq, int64_t tDrop) {
    trace_ << format(kind, item, tEnq, tDeq, tDrop);
    if (kind[1] == 'e') ++rowsDeq_;
    else ++rowsDrop_;
  }

  std::string format(const char* kind, ns3::Ptr<const ns3::QueueDiscItem> item, int64_t tEnq, int64_t tDeq,
                     int64_t tDrop) const {
    FlowTag tag;
    std::string saddr, daddr;
    int sport = -1, dport = -1, proto = -1;
    if (item->GetPacket()->PeekPacketTag(tag)) {
      // FLAG: video flows are TCP here; written as proto 17 because the frozen GT-Q
      // selects a client's packets by its addresses and UDP.
      proto = 17;
      if (tag.kind == Kind::Bg) {
        const auto& b = tuples_->bg.at(tag.flow >> 16);
        saddr = b.saddr;
        daddr = b.daddr;
        sport = b.basePort + int(tag.flow & 0xffff);
        dport = b.dport;
      } else {
        const auto& v = tuples_->video.at(tag.flow);
        const bool fwd = tag.kind == Kind::Video;
        saddr = fwd ? v.pub : v.sub;
        daddr = fwd ? v.sub : v.pub;
        sport = fwd ? 4433 : v.subPort;
        dport = fwd ? v.subPort : 4433;
      }
    }
    std::ostringstream o;
    o << kind << ',' << tEnq << ',' << tDeq << ',' << tDrop << ",0," << saddr << ',' << daddr << ',' << proto << ','
      << sport << ',' << dport << ',' << wireLen(item) << ",0,0\n";
    return o.str();
  }

  void SampleMain() {
    using namespace ns3;
    flushPending();
    const int64_t now = simClock().monoNs(Simulator::Now());
    const uint32_t pk = qd_->GetNPackets();
    const uint64_t backlog = qd_->GetNBytes() + uint64_t(pk) * kEthHeader;
    const double pct = c_.limitPackets ? 100.0 * pk / c_.limitPackets : 0;
    main_ << now << ',' << (lastMain_ ? now - lastMain_ : 0) << ",0," << offered_ - offeredRow_ << ','
          << transmitted_ - transmittedRow_ << ',' << drops_ - dropsRow_ << ",0,0,0,0,0," << c_.limitPackets << ','
          << pk << ',' << pct << ',' << backlog << ",0,0,0.0,0,0,0,0,0\n";
    lastMain_ = now;
    offeredRow_ = offered_;
    transmittedRow_ = transmitted_;
    dropsRow_ = drops_;
    Simulator::Schedule(MilliSeconds(c_.intervalMs), &EgressMonitor::SampleMain, this);
  }

  void SampleQueue() {
    using namespace ns3;
    const uint32_t pk = qd_->GetNPackets();
    queue_ << simClock().monoNs(Simulator::Now()) << ',' << pk << ',' << qd_->GetNBytes() + uint64_t(pk) * kEthHeader
           << ',' << drops_ << '\n';
    Simulator::Schedule(MilliSeconds(c_.queueIntervalMs), &EgressMonitor::SampleQueue, this);
  }

  MonitorConfig c_;
  ns3::Ptr<ns3::QueueDisc> qd_;
  const TupleMap* tuples_;
  uint64_t offered_{0}, transmitted_{0}, drops_{0}, offeredRow_{0}, transmittedRow_{0}, dropsRow_{0};
  uint64_t nEnq_{0}, nDeq_{0}, nDrop_{0}, rowsDeq_{0}, rowsDrop_{0}, queuedEnd_{0}, dequeueThenDrop_{0};
  ns3::Ptr<const ns3::QueueDiscItem> pending_;
  int64_t pendEnq_{0}, pendOut_{0};
  uint64_t pendLen_{0};
  std::string pendRow_;
  int64_t lastMain_{0}, startNs_{0}, endNs_{0};
  Csv main_, flows_, queue_, trace_;
};

}  // namespace quicsim
