// Per-client video flow state shared by the sender, the sink and the BBR observer
// (one process: the simulator knows each transmission's fate exactly), and the BBR
// subclass that exposes the per-ACK rate sample and BBR state without editing ns-3.
#pragma once

#include "common.h"

#include "ns3/internet-module.h"

#include <deque>
#include <functional>
#include <map>
#include <string>
#include <vector>

namespace quicsim {

struct Tx {               // one transmission of one TCP segment (the pkts.csv row)
  uint32_t off;           // stream offset of the segment's first byte
  uint32_t len;           // payload bytes
  int64_t sendNs;         // simulator time
  int64_t arriveNs{-1};   // first arrival at the receiver, -1 if lost
  uint64_t sentTotal;     // bytes transmitted by the flow up to and including this one
};

struct Seg {              // a segment as the ACK path sees it
  uint32_t len;
  uint64_t lastTx;        // latest transmission
  int64_t arrivedTx{-1};  // the transmission that arrived first, if any
};

struct FrameRec {         // a frame written to the socket, for the receiver's frame log
  uint64_t end;           // stream offset one past its last byte
  uint64_t index;
  bool keyframe;
  uint32_t size;
  uint64_t sendUs;        // produced (unix us), the FrameHeader sendUs
  uint32_t skippedBefore;
};

struct OwdBin {
  uint32_t sent{0}, timed{0};
  int64_t sumUs{0}, minUs{0}, maxUs{0};
};

struct VideoFlow {
  uint32_t index{0};
  std::string sid;
  uint32_t rateKbps{0};
  uint32_t phaseMs{0};

  // transmissions and segments
  std::vector<Tx> txs;
  std::map<uint32_t, Seg> segs;     // by offset; erased once cumulatively acked
  bool haveSeq0{false};
  ns3::SequenceNumber32 seq0;       // sequence number of stream offset 0
  uint32_t ackedOff{0};
  uint64_t sentTotal{0}, retxBytes{0}, lostPackets{0};
  ns3::SequenceNumber32 highTx;     // highest sequence ever sent (unsent = written - this)

  // receiver
  std::deque<FrameRec> frames;
  uint64_t recvOff{0};

  // sender-side OWD log (-owd.csv), 5 ms bins of send time
  std::map<int64_t, OwdBin> owdBins;

  uint32_t offsetOf(ns3::SequenceNumber32 s) const { return uint32_t(s - seq0); }
};

class TcpBbrObs;
using AckHook = std::function<void(ns3::Ptr<ns3::TcpSocketState>, const ns3::TcpRateOps::TcpRateSample&,
                                   TcpBbrObs*)>;

// TcpBbr with a hook after every CongControl call (every ACK). Behaviour unchanged.
class TcpBbrObs : public ns3::TcpBbr {
 public:
  static ns3::TypeId GetTypeId();
  TcpBbrObs() = default;
  TcpBbrObs(const TcpBbrObs& o) : ns3::TcpBbr(o), hook(o.hook) {}
  void CongControl(ns3::Ptr<ns3::TcpSocketState> tcb, const ns3::TcpRateOps::TcpRateConnection& rc,
                   const ns3::TcpRateOps::TcpRateSample& rs) override {
    ns3::TcpBbr::CongControl(tcb, rc, rs);
    if (hook) hook(tcb, rs, this);
  }
  ns3::Ptr<ns3::TcpCongestionOps> Fork() override { return ns3::CopyObject<TcpBbrObs>(this); }

  // BBR's own bandwidth estimate (max filter), read through the member pointer below.
  uint64_t bwBps() const;
  const char* phase() { return kPhase[GetBbrState()]; }

  AckHook hook;

 private:
  static constexpr const char* kPhase[] = {"startup", "drain", "probe_bw", "probe_rtt"};
};

}  // namespace quicsim
