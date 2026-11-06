/* SPDX-License-Identifier: Apache-2.0 */
#pragma once

// Passive early-congestion shadow detector. It reads the same per-ACK signals
// BBR sees and never feeds anything back into the congestion controller.
// Independent of src/sbd: grouping comes from configuration, not detection.

#include <cmath>
#include <cstdint>
#include <deque>
#include <limits>
#include <optional>
#include <string>
#include <vector>

namespace openmoq::moqx::shadow {

enum class BbrPhase : uint8_t {
  Unknown,
  Startup,
  Drain,
  ProbeBwDown,
  ProbeBwCruise,
  ProbeBwRefill,
  ProbeBwUp,
  ProbeBw, // BBRv1: the gain cycle position is not exposed by mvfst.
  ProbeRtt,
};
const char* phaseName(BbrPhase phase);

struct Params {
  // Delivery deficit: delivery_rate / max_bw < theta for M valid samples.
  bool useDeficit{true};
  double theta{0.8};
  uint32_t deficitSamples{3};
  // A deficit sample counts only with at least this much queuing delay. Low
  // delivery with an empty queue is the sender holding back (BBR pacing at a
  // stale low estimate while it recovers), not the network. 0 = off.
  double deficitMinDelayMs{0};

  // Delay gradient: WebRTC trendline over (send time, rtt - min_rtt).
  bool useGradient{true};
  uint32_t trendWindow{20};
  double trendSmoothing{0.9};
  double trendGain{4.0};
  int64_t trendGroupUs{5'000};
  double gradientScale{0.5}; // s < 1: pre-signal below GCC's overuse threshold.
  uint32_t gradientPoints{2};
  double gammaInitial{12.5};
  double gammaMin{6.0};
  double gammaMax{600.0};
  double gammaKUp{0.0087};
  double gammaKDown{0.039};

  // Excess inflight (supporting only).
  bool useExcess{true};
  // Offered-load deficit: bytes delivered vs bytes sent over one GOP-long
  // window. Valid while app-limited; keyframes cancel out within a GOP.
  bool useOffered{true};
  int64_t offeredWindowUs{1'000'000};
  double offeredMinBytes{12'000};
  double excessMs{10.0};
  // false: excess only raises the score and never triggers the pre-signal.
  bool excessTrigger{true};

  // BBR self-induced queue masking.
  bool maskPhases{true};
  double probeUpFactor{1.5};
  double postProbeRttMaskRtts{3.0};

  // Subtract the queue the relay's own sending explains from measured delay.
  bool normalizeBySent{true};
  double residualFloorMs{50.0}; // unexplained delay needed before a gradient alarm
  // QoE-aware delay: the residual delay is replaced by its minimum over this
  // trailing window, so a keyframe's queue that drains within it is ignored.
  // A queue that never drains (congestion) raises the floor. 0 = off.
  int64_t floorWindowUs{0};
  // Level trigger: the (floored) residual delay above levelMs for levelRtts
  // smoothed RTTs. Faster than the trendline in deep queues. 0 = off.
  double levelMs{0};
  double levelRtts{2.0};

  // Backlog: bytes not yet delivered (inflight + relay send buffer) as the
  // time to drain them at the current delivery rate, minus min RTT, floored
  // over backlogWindowUs. It sees the queue wherever it builds — in the
  // network or, once BBR's cwnd holds data back, in the relay. 0 = off.
  double backlogMs{0};
  int64_t backlogWindowUs{500'000};
  // Drain latch: once the floored backlog is lower than one window earlier,
  // the relay is flushing what it held during congestion (capacity is back);
  // backlog alarms stay off until the send buffer is empty or the backlog has
  // grown again by backlogMs over a window. Without the latch, keyframes
  // inside the flush flip the gate and every flip is a new alarm.
  bool backlogRequireGrowth{false};
  // Flush gate: no backlog alarm while delivery over the last backlog window
  // runs at least this many times the long-run demand (a 10 s average of
  // delivery). A path that delivers faster than the media rate is draining a
  // backlog (after relief, or a burst from a recovered upstream), not
  // congested. It only blocks a new alarm; one already on stays on. 0 = off.
  double backlogFlushRatio{0};
  // Offered-load: count growth of the relay send buffer as offered load.
  bool offeredBuffer{false};

  // Grouped flows: evaluate the deficit and the self-induced queue on the
  // group aggregate, because members' keyframes collide at the shared link.
  bool sharedContext{true};
  int64_t sharedWindowUs{200'000};
  int64_t capacityLookbackUs{10'000'000};
  // A member counts as network-limited only with data waiting (relay send
  // buffer non-empty or cwnd full). mvfst keeps marking samples
  // non-app-limited for seconds after a backlog drains; without data waiting
  // the group's delivery is its demand, not its capacity.
  bool sharedRequireBacklog{false};

  // Confirmed tier.
  double bbrDropFraction{0.1};
  int64_t bbrDropLookbackUs{5'000'000};
  uint32_t lossPackets{2};
  double sendQueueMs{100.0};
  int64_t confirmHoldUs{1'000'000};

  int64_t clearUs{300'000};
  // Primary signals that must agree to raise the pre-signal (1 = any).
  uint32_t minSignals{1};
  // Hybrid rule: backlog alone raises the pre-signal at this drain time even
  // when minSignals > 1 (a strong, reliable condition). 0 = off.
  double soloBacklogMs{0};

  // Deficit and offered-load deficit persistence in time instead of samples:
  // the condition must hold for max(persistRtts * min RTT, persistMinUs). ACK
  // counts are ~1 ms apart at high bitrates and ~10 ms at low ones. The min
  // RTT, not srtt: srtt grows with the very queue being detected. 0 = use
  // deficitSamples consecutive samples.
  double persistRtts{0};
  int64_t persistMinUs{20'000};

  // Backlog delivery rate: min(rate over this window, rate over
  // offeredWindowUs). A 1 s rate lags a capacity drop and understates the
  // drain time. 0 = 1 s rate only.
  int64_t backlogRateWindowUs{0};

  // Queuing-delay thresholds relative to the flow's own calm distribution:
  // deficitMinDelayMs and residualFloorMs are lowered to mean + k * sd of the
  // calm queuing delay / residual delay when that is smaller. AQMs keep the
  // queue near their target (fq_codel 5 ms), below fixed thresholds. 0 = off.
  double calmDelayK{0};

  // Loss rate: packets declared lost in the last max(lossWindowRtts * min RTT,
  // 200 ms) over the packets sent one min RTT earlier (bytes / kLossPacketBytes)
  // >= lossRate, with at least lossMinPackets lost. Drop-based AQMs show
  // congestion as loss more than as delay. 0 = off.
  double lossRate{0};
  double lossWindowRtts{4.0};
  uint32_t lossMinPackets{3};

  // Second-level output: a pre-signal is "verified" once the backlog drain
  // time reaches this (late but precise: the subscriber is this far behind).
  // Reported as verified_on; it does not change the pre-signal. 0 = off.
  double verifiedMs{0};

  // Group layer.
  double poolZ{3.5};
  double lagRtts{1.0};
  int64_t lagMaxUs{1'000'000};
  bool propagation{true};
  double propagationFactor{0.5};
  // Propagate only to members whose own group z-score is already at least
  // this (some evidence of their own); 0 = propagate to every member.
  double propagationMinZ{0};
  double propagationRtts{2.0};
  int64_t propagationMinUs{300'000};

  // Calm-period noise statistics used for z-scores.
  double calmAlpha{0.02};
  uint32_t calmWarmup{100};
};

struct Variant {
  std::string name;
  Params params;
};

// Built-in parallel variants. They run on the same samples, so ablations are
// paired: every variant sees exactly the same network history.
std::vector<Variant> builtinVariants(const Params& base);
std::vector<std::string> builtinVariantNames();

// Applies one numeric `shadow.params` override; returns an error message, or
// an empty string on success.
std::string applyParam(Params& params, const std::string& name, double value);

struct AckSample {
  int64_t ackUs{0};
  int64_t sentUs{0}; // send time of the largest newly acked packet
  std::optional<int64_t> rttUs;
  int64_t minRttUs{0};
  int64_t srttUs{0};
  bool rateValid{false};
  double sendBps{0};
  double ackBps{0};
  bool appLimited{false};
  uint64_t bytesSentAtSend{0}; // connection total when that packet was sent
  uint64_t bytesAckedTotal{0};
  double bbrBwBps{0};
  uint64_t cwndBytes{0};
  uint64_t inflightBytes{0};
  uint64_t streamBufferBytes{0};
  BbrPhase phase{BbrPhase::Unknown};
  uint32_t newlyLost{0};
  bool relaySaturated{false};
};

struct Event {
  std::string name;
  int64_t monoUs{0};
  std::string detail; // compact JSON object body without braces
};

// What the group's shared bottleneck looks like when one member's sample is
// evaluated.
struct SharedContext {
  bool valid{false};
  double capacityBps{0};        // windowed max of aggregate delivery
  double deliveredBps{NAN};     // aggregate delivery over sharedWindowUs
  bool limited{false};          // at least half the members network-limited
  double expectedQueueMs{0};    // group FIFO model at the sample's send time
};

// Aggregate of one configured group: bytes the relay sent to every member
// (by send time, as written) and bytes they acknowledged (by ACK arrival).
// Keyframes reach all members at once, so their queue only shows up here.
class SharedBottleneck {
 public:
  explicit SharedBottleneck(Params params) : p_(params) {}
  void onSent(int64_t sendUs, uint64_t bytes);
  void onAck(const std::string& member, int64_t ackUs, uint64_t bytesAckedTotal,
             bool networkLimited, bool dataWaiting = true);
  void removeMember(const std::string& member);
  SharedContext context(int64_t nowUs, int64_t sendUs, size_t members);

 private:
  static constexpr int64_t kBinUs = 5'000;
  struct SendBin {
    int64_t startUs;
    uint64_t bytes;
    double queueMs{0};
    bool modelled{false};
  };
  struct Member {
    uint64_t ackedTotal{0};
    int64_t lastUs{0};
    bool networkLimited{false};
  };
  void model(int64_t uptoUs);

  Params p_;
  std::deque<SendBin> sends_;
  double queueMs_{0};
  int64_t modelledUs_{0};
  std::deque<std::pair<int64_t, uint64_t>> acks_;
  uint64_t windowBytes_{0};
  std::deque<std::pair<int64_t, double>> rates_;
  int64_t firstAckUs_{0};
  int64_t limitedSinceUs_{0};
  std::vector<std::pair<std::string, Member>> members_;
};

struct Signals {
  double queueDelayMs{NAN};
  bool deficitValid{false};
  double ratio{NAN};
  uint32_t deficitCount{0};
  bool gradientValid{false};
  double trend{NAN};
  double residualTrend{NAN};
  double expectedQueueMs{0}; // self-induced delay predicted from bytes sent
  double gamma{NAN};
  double excessMs{NAN};
  bool sharedUsed{false}; // deficit/queue model came from the group aggregate
  double zDeficit{NAN};
  double zGradient{NAN};
  double zExcess{NAN};
  bool offeredValid{false};
  double offeredRatio{NAN};
  double floorDelayMs{NAN}; // floored residual delay (floorWindowUs)
  double backlogMs{NAN};    // floored backlog drain time beyond min RTT
  double deficitMinDelayMs{NAN}; // effective deficit queuing-delay threshold
  double residualFloorMs{NAN};   // effective residual floor
  bool verified{false};
  double zOffered{NAN};
  double score{0}; // smoothed combined z-score fed to the group layer
  bool deficitPre{false};
  bool gradientPre{false};
  bool excessHigh{false};
  bool offeredPre{false};
  bool levelPre{false};
  bool backlogPre{false};
  double lossRate{NAN};
  bool lossPre{false};
  bool gccOveruse{false};
  std::string mask; // empty when unmasked
  bool propagated{false};
  bool pre{false};
  bool confirmed{false};
};

class Ewma {
 public:
  void add(double value, double alpha);
  uint64_t count() const { return count_; }
  double mean() const { return mean_; }
  double sd() const { return std::sqrt(std::max(var_, 0.0)); }
  double z(double value, double floor) const;

 private:
  uint64_t count_{0};
  double mean_{0};
  double var_{0};
};

class FlowDetector {
 public:
  explicit FlowDetector(Params params) : p_(params) {}

  // Returns events produced by this sample; signals() reflects the sample.
  // `shared` is the member's group context, or null for an ungrouped flow.
  std::vector<Event> onAck(const AckSample& sample, const SharedContext* shared = nullptr);

  // Group layer hook: lower this flow's thresholds until monoUs.
  // Bytes the relay wrote on this connection (all of them, as written).
  void onSent(int64_t sendUs, uint64_t bytes);

  void propagateUntil(int64_t monoUs) { propagationUntilUs_ = std::max(propagationUntilUs_, monoUs); }

  const Signals& signals() const { return s_; }
  const Params& params() const { return p_; }
  bool pre() const { return pre_; }
  bool confirmed() const { return confirmed_; }
  bool warm() const { return score_.count() >= p_.calmWarmup; }
  int64_t srttUs() const { return srttUs_; }
  int64_t lastUs() const { return lastUs_; }

 private:
  struct TrendPoint {
    double xMs; // packet send time
    double yMs; // smoothed queuing delay
    double rMs; // smoothed queuing delay minus the self-induced model
    uint64_t bytes;
  };

  void updateMask(const AckSample& sample);
  void updateDeficit(const AckSample& sample, double factor, const SharedContext* shared);
  void updateGradient(const AckSample& sample, double factor, const SharedContext* shared);
  void updateExcess(const AckSample& sample);
  void updateOffered(const AckSample& sample, double factor);
  void updateBacklog(const AckSample& sample, double factor);
  void updateScore(const AckSample& sample);
  void updateConfirmed(const AckSample& sample, std::vector<Event>& events);
  void updatePre(const AckSample& sample, std::vector<Event>& events);
  std::string evidence() const;

  Params p_;
  Signals s_;
  int64_t lastUs_{0};
  int64_t srttUs_{0};

  static constexpr int64_t kNever = std::numeric_limits<int64_t>::min() / 2;
  static constexpr int64_t kStartupSettleUs = 2'000'000;

  BbrPhase lastPhase_{BbrPhase::Unknown};
  int64_t startupAppLimitedSinceUs_{0};
  bool startupSettled_{false};
  int64_t probeRttExitUs_{kNever};
  uint32_t appLimitedRun_{0};
  uint32_t notAppLimitedRun_{0};
  bool appLimitedRegime_{false};

  uint32_t deficitCount_{0};
  int64_t deficitSinceUs_{0};
  int64_t lastDeficitValidUs_{kNever};
  int64_t lastZDeficitUs_{kNever};

  std::deque<TrendPoint> points_;
  int64_t lastPointSentUs_{kNever};
  double smoothedDelay_{0};
  double smoothedResidual_{0};
  double expectedQueueMs_{0};
  bool haveSmoothed_{false};
  uint64_t numDeltas_{0};
  double gamma_{0};
  double lastGammaXMs_{NAN};
  uint32_t gradientRun_{0};
  uint32_t gccRun_{0};
  int64_t lastGradientValidUs_{kNever};
  int64_t lastZGradientUs_{kNever};

  Ewma calmDeficit_, calmGradient_, calmExcess_, calmOffered_, score_;
  Ewma calmDelay_, calmResidual_;  // calm queuing / smoothed residual delay (calmDelayK)
  uint64_t sentTotal_{0};
  std::deque<std::pair<int64_t, uint64_t>> sentHistory_;   // (send time, cumulative bytes)
  std::deque<std::pair<int64_t, uint64_t>> ackedHistory_;  // (ack time, cumulative acked)
  std::deque<std::pair<int64_t, uint64_t>> bufferHistory_;  // (ack time, send buffer bytes)
  std::deque<std::pair<int64_t, double>> floorWindow_;       // (send time, residual), increasing
  int64_t levelSinceUs_{0};
  int64_t lastFloorUs_{kNever};
  std::deque<std::pair<int64_t, double>> backlogWindow_;     // (ack time, backlog ms), increasing
  int64_t backlogFirstUs_{0};
  std::deque<std::pair<int64_t, double>> backlogHistory_;    // (ack time, floored backlog ms)
  bool backlogDraining_{false};
  double demandBps_{0};
  int64_t demandLastUs_{0};
  uint32_t offeredCount_{0};
  int64_t offeredSinceUs_{0};
  int64_t lastOfferedValidUs_{kNever};
  int64_t lastZOfferedUs_{kNever};
  double smoothedScore_{0};
  int64_t scoreLastUs_{0};

  std::deque<std::pair<int64_t, double>> bbrHistory_;
  bool bbrDropped_{false};
  std::deque<std::pair<int64_t, uint32_t>> losses_;
  int64_t sendQueueSinceUs_{0};
  bool sendQueueReported_{false};
  int64_t confirmLastTriggerUs_{0};
  std::string confirmReason_;

  int64_t propagationUntilUs_{0};
  bool pre_{false};
  bool confirmed_{false};
  bool prevDeficitPre_{false};
  bool prevGradientPre_{false};
  bool prevExcessHigh_{false};
  bool prevOfferedPre_{false};
  bool prevLevelPre_{false};
  bool prevBacklogPre_{false};
  bool prevLossPre_{false};
  std::deque<std::pair<int64_t, uint32_t>> lossHistory_;  // (ack time, newly lost packets)
  int64_t preLastTriggerUs_{0};
  int64_t preOnsetUs_{0};
  bool verified_{false};
  bool soloBacklog_{false};
  int64_t minRttUs_{0};

  void updateLoss(const AckSample& x, double factor);
  // Time the deficit / offered condition must hold (persistRtts), or 0.
  int64_t persistUs(double factor) const;
  // Thresholds lowered toward the calm distribution (calmDelayK).
  double effectiveThreshold(double fixedMs, const Ewma& calm) const;
};

// One configured group of flows believed to share a bottleneck.
class GroupLayer {
 public:
  explicit GroupLayer(Params params) : p_(params) {}

  struct Member {
    std::string id;
    FlowDetector* flow;
  };

  // Called after any member processed a sample. Returns group events and
  // applies warning propagation to members.
  std::vector<Event> evaluate(
      int64_t nowUs,
      const std::string& source,
      bool sourcePreOnset,
      const std::vector<Member>& members);

  double pooled() const { return pooled_; }
  bool pooledOn() const { return pooledOn_; }
  bool confirmed() const { return confirmed_; }
  int activeMembers() const { return active_; }
  double memberZ(const std::string& id) const;

 private:
  struct MemberState {
    std::deque<std::pair<int64_t, double>> scores;
    Ewma calm;
    double z{NAN};
  };

  Params p_;
  std::vector<std::pair<std::string, MemberState>> state_;
  double pooled_{0};
  bool pooledOn_{false};
  bool confirmed_{false};
  bool anyPre_{false};
  int active_{0};
  int64_t pooledLastUs_{0};

  MemberState& member(const std::string& id);
};

} // namespace openmoq::moqx::shadow
