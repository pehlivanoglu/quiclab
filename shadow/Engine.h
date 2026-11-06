/* SPDX-License-Identifier: Apache-2.0 */
#pragma once

#include "shadow/Detector.h"

#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace openmoq::moqx::shadow {

struct FlowInfo {
  std::string id;
  std::string peer;
  std::string name;
  std::string group; // empty: evaluated alone
};

// Flows x variants, configured groups and their shared bottleneck. Pure C++
// so the live relay and the offline replay tool run identical logic.
class Engine {
 public:
  // `variant` is empty for variant-independent events (BBR's own reaction).
  using Sink = std::function<void(const std::string& variant, const char* scope,
                                  const FlowInfo& flow, const Event& event)>;

  Engine(std::vector<Variant> variants, Sink sink);

  const std::vector<Variant>& variants() const { return variants_; }
  void addFlow(const FlowInfo& info);
  void removeFlow(const std::string& id);
  bool active(const std::string& id) const;
  void onSent(const std::string& id, int64_t sendUs, uint64_t bytes);
  void onLoss(const std::string& id, uint32_t packets);
  // False when the flow is not active; the sample is then ignored.
  bool onAck(const std::string& id, AckSample sample);

  // One CSV row (kSampleHeader) for the flow's latest sample, `full` variant.
  std::string sampleRow(const std::string& id) const;

  struct FlowState {
    FlowInfo info;
    std::vector<std::unique_ptr<FlowDetector>> detectors; // per variant
    uint32_t pendingLost{0};
    uint64_t acks{0};
    AckSample last;
    SharedContext shared;
    bool active{false};
  };
  struct GroupState {
    std::vector<std::unique_ptr<GroupLayer>> layers; // per variant
    SharedBottleneck shared;
    explicit GroupState(const Params& params) : shared(params) {}
  };
  const std::map<std::string, FlowState>& flows() const { return flows_; }
  const std::map<std::string, std::unique_ptr<GroupState>>& groups() const { return groups_; }

 private:
  size_t activeMembers(const std::string& group) const;

  std::vector<Variant> variants_;
  Sink sink_;
  std::map<std::string, FlowState> flows_;
  std::map<std::string, std::unique_ptr<GroupState>> groups_;
};

// Built-in variants filtered by name (empty: all); `full` is always first.
std::vector<Variant> selectVariants(const Params& base, const std::vector<std::string>& names);

extern const char* const kSampleHeader;
// Raw per-ACK inputs only (what the offline replay reads), plus the relay's
// processing order `seq`. Written instead of kSampleHeader in record-only runs.
extern const char* const kRawSampleHeader;
std::string rawSampleRow(const AckSample& sample, uint64_t seq);
// Per-flow bytes written by the relay, one row per packetsWritten event.
extern const char* const kSentHeader;
// Per-flow packet outcomes for offline baselines (not read by the detector):
// every newly acked packet with the peer's receive time when it reports one
// (ACK receive timestamps, host CLOCK_MONOTONIC us on a shared-clock testbed),
// and every packet declared lost.
extern const char* const kAckedHeader;
extern const char* const kLostHeader;

std::string jsonString(const std::string& value);
std::string sampleFileName(const FlowInfo& flow);
std::string sentFileName(const FlowInfo& flow);
std::string ackedFileName(const FlowInfo& flow);
std::string lostFileName(const FlowInfo& flow);
std::string eventLine(const std::string& relayId, int64_t unixOffsetNs, const std::string& variant,
                      const char* scope, const FlowInfo& flow, const Event& event);

struct MetaFlow {
  FlowInfo info;
  bool eligible{false};
  bool closed{false};
  bool hasSamples{false};
};
std::string metaJson(const std::string& relayId, int64_t unixOffsetNs, double relayCpuThreshold, bool recordOnly,
                     const std::vector<Variant>& variants,
                     const std::map<std::string, std::vector<std::string>>& groups,
                     const std::vector<MetaFlow>& flows);

} // namespace openmoq::moqx::shadow
