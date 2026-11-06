/* SPDX-License-Identifier: Apache-2.0 */
#include "shadow/Engine.h"

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <iomanip>
#include <sstream>
#include <utility>

namespace openmoq::moqx::shadow {
namespace {

std::string num(double value) {
  if (!std::isfinite(value)) return "";
  std::ostringstream out;
  out << std::setprecision(10) << value;
  return out.str();
}

std::string jsonNum(double value) {
  const auto text = num(value);
  return text.empty() ? "null" : text;
}

} // namespace

const char* const kSampleHeader =
    "mono_us,sent_mono_us,rtt_us,min_rtt_us,srtt_us,queue_delay_ms,rate_valid,app_limited,"
    "send_bps,ack_bps,bbr_bw_bps,cwnd_bytes,inflight_bytes,stream_buffer_bytes,"
    "bytes_acked_total,bytes_sent_at_send,phase,newly_lost,relay_saturated,mask,ratio,"
    "deficit_count,trend,residual_trend,expected_queue_ms,gamma,excess_ms,z_deficit,"
    "z_gradient,z_excess,score,deficit_pre,gradient_pre,excess_high,gcc_overuse,"
    "propagated,pre,confirmed,group_member_z,group_pooled_z,group_pooled_on,"
    "shared_used,shared_capacity_bps,shared_delivered_bps,shared_limited,offered_ratio,offered_pre\n";

std::string jsonString(const std::string& value) {
  std::string out = "\"";
  for (const char c : value) {
    switch (c) {
      case '"': out += "\\\""; break;
      case '\\': out += "\\\\"; break;
      case '\n': out += "\\n"; break;
      default:
        if (static_cast<unsigned char>(c) < 0x20) {
          char escaped[8];
          std::snprintf(escaped, sizeof escaped, "\\u%04x", c);
          out += escaped;
        } else {
          out += c;
        }
    }
  }
  return out + "\"";
}

const char* const kRawSampleHeader =
    "mono_us,sent_mono_us,rtt_us,min_rtt_us,srtt_us,rate_valid,app_limited,send_bps,ack_bps,"
    "bbr_bw_bps,cwnd_bytes,inflight_bytes,stream_buffer_bytes,bytes_acked_total,"
    "bytes_sent_at_send,phase,newly_lost,relay_saturated,seq\n";

std::string rawSampleRow(const AckSample& x, uint64_t seq) {
  std::ostringstream row;
  row << x.ackUs << ',' << x.sentUs << ',' << (x.rttUs ? std::to_string(*x.rttUs) : "") << ','
      << x.minRttUs << ',' << x.srttUs << ',' << x.rateValid << ',' << x.appLimited << ','
      << num(x.sendBps) << ',' << num(x.ackBps) << ',' << num(x.bbrBwBps) << ',' << x.cwndBytes
      << ',' << x.inflightBytes << ',' << x.streamBufferBytes << ',' << x.bytesAckedTotal << ','
      << x.bytesSentAtSend << ',' << phaseName(x.phase) << ',' << x.newlyLost << ','
      << x.relaySaturated << ',' << seq << '\n';
  return row.str();
}

const char* const kSentHeader = "send_mono_us,bytes,seq\n";

std::string sentFileName(const FlowInfo& flow) {
  std::string name = sampleFileName(flow);
  return "sent/" + name.substr(std::string("samples/").size());
}

const char* const kAckedHeader = "ack_mono_us,pkt_num,sent_mono_us,recv_mono_us,bytes\n";
const char* const kLostHeader = "loss_mono_us,pkt_num,sent_mono_us,bytes,by_timeout,by_reorder\n";

std::string ackedFileName(const FlowInfo& flow) {
  std::string name = sampleFileName(flow);
  return "acked/" + name.substr(std::string("samples/").size());
}

std::string lostFileName(const FlowInfo& flow) {
  std::string name = sampleFileName(flow);
  return "lost/" + name.substr(std::string("samples/").size());
}

std::string sampleFileName(const FlowInfo& flow) {
  std::string name = flow.name;
  for (auto& c : name)
    if (!std::isalnum(static_cast<unsigned char>(c)) && c != '-' && c != '_' && c != '.') c = '_';
  return "samples/" + name + "__" + flow.id + ".csv";
}

std::string eventLine(const std::string& relayId, int64_t unixOffsetNs, const std::string& variant,
                      const char* scope, const FlowInfo& flow, const Event& event) {
  std::string line = "{\"schema_version\":1,\"relay_id\":" + jsonString(relayId) +
      ",\"variant\":" + (variant.empty() ? "null" : jsonString(variant)) +
      ",\"scope\":\"" + scope + "\",\"event\":\"" + event.name + "\",\"mono_us\":" +
      std::to_string(event.monoUs) + ",\"unix_ns\":" +
      std::to_string(event.monoUs * 1000 + unixOffsetNs) +
      ",\"connection_id\":" + jsonString(flow.id) + ",\"flow\":" + jsonString(flow.name) +
      ",\"group\":" + (flow.group.empty() ? "null" : jsonString(flow.group));
  if (!event.detail.empty()) line += "," + event.detail;
  return line + "}\n";
}

std::string metaJson(const std::string& relayId, int64_t unixOffsetNs, double relayCpuThreshold, bool recordOnly,
                     const std::vector<Variant>& variants,
                     const std::map<std::string, std::vector<std::string>>& groups,
                     const std::vector<MetaFlow>& flows) {
  std::ostringstream out;
  auto b = [](bool v) { return v ? "true" : "false"; };
  out << "{\n  \"schema_version\": 1,\n  \"relay_id\": " << jsonString(relayId)
      << ",\n  \"unix_offset_ns\": " << unixOffsetNs
      << ",\n  \"clock\": \"steady_clock_monotonic_us\",\n  \"relay_cpu_threshold\": "
      << jsonNum(relayCpuThreshold) << ",\n  \"record_only\": " << (recordOnly ? "true" : "false")
      << ",\n  \"variants\": [";
  for (size_t i = 0; i < variants.size(); ++i) out << (i ? ", " : "") << jsonString(variants[i].name);
  out << "],\n  \"params\": {";
  for (size_t i = 0; i < variants.size(); ++i) {
    const auto& p = variants[i].params;
    out << (i ? "," : "") << "\n    " << jsonString(variants[i].name) << ": {"
        << "\"use_deficit\": " << b(p.useDeficit) << ", \"use_gradient\": " << b(p.useGradient)
        << ", \"use_excess\": " << b(p.useExcess) << ", \"use_offered\": " << b(p.useOffered)
        << ", \"offered_window_ms\": " << jsonNum(p.offeredWindowUs / 1000.0)
        << ", \"offered_min_bytes\": " << jsonNum(p.offeredMinBytes)
        << ", \"mask_phases\": " << b(p.maskPhases)
        << ", \"normalize_by_sent\": " << b(p.normalizeBySent)
        << ", \"shared_context\": " << b(p.sharedContext)
        << ", \"propagation\": " << b(p.propagation) << ", \"theta\": " << jsonNum(p.theta)
        << ", \"deficit_samples\": " << p.deficitSamples << ", \"trend_window\": " << p.trendWindow
        << ", \"trend_smoothing\": " << jsonNum(p.trendSmoothing)
        << ", \"trend_gain\": " << jsonNum(p.trendGain)
        << ", \"trend_group_ms\": " << jsonNum(p.trendGroupUs / 1000.0)
        << ", \"gradient_scale\": " << jsonNum(p.gradientScale)
        << ", \"gradient_points\": " << p.gradientPoints
        << ", \"gamma_initial\": " << jsonNum(p.gammaInitial)
        << ", \"gamma_min\": " << jsonNum(p.gammaMin) << ", \"gamma_max\": " << jsonNum(p.gammaMax)
        << ", \"gamma_k_up\": " << jsonNum(p.gammaKUp) << ", \"gamma_k_down\": " << jsonNum(p.gammaKDown)
        << ", \"excess_ms\": " << jsonNum(p.excessMs)
        << ", \"probe_up_factor\": " << jsonNum(p.probeUpFactor)
        << ", \"post_probe_rtt_mask_rtts\": " << jsonNum(p.postProbeRttMaskRtts)
        << ", \"residual_floor_ms\": " << jsonNum(p.residualFloorMs)
        << ", \"shared_window_ms\": " << jsonNum(p.sharedWindowUs / 1000.0)
        << ", \"capacity_lookback_ms\": " << jsonNum(p.capacityLookbackUs / 1000.0)
        << ", \"bbr_drop_fraction\": " << jsonNum(p.bbrDropFraction)
        << ", \"bbr_drop_lookback_ms\": " << jsonNum(p.bbrDropLookbackUs / 1000.0)
        << ", \"loss_packets\": " << p.lossPackets << ", \"send_queue_ms\": " << jsonNum(p.sendQueueMs)
        << ", \"confirm_hold_ms\": " << jsonNum(p.confirmHoldUs / 1000.0)
        << ", \"clear_ms\": " << jsonNum(p.clearUs / 1000.0) << ", \"pool_z\": " << jsonNum(p.poolZ)
        << ", \"lag_rtts\": " << jsonNum(p.lagRtts) << ", \"lag_max_ms\": " << jsonNum(p.lagMaxUs / 1000.0)
        << ", \"propagation_factor\": " << jsonNum(p.propagationFactor)
        << ", \"propagation_rtts\": " << jsonNum(p.propagationRtts)
        << ", \"propagation_min_ms\": " << jsonNum(p.propagationMinUs / 1000.0)
        << ", \"calm_alpha\": " << jsonNum(p.calmAlpha) << ", \"calm_warmup\": " << p.calmWarmup
        << ", \"excess_trigger\": " << b(p.excessTrigger)
        << ", \"deficit_min_delay_ms\": " << jsonNum(p.deficitMinDelayMs)
        << ", \"shared_require_backlog\": " << b(p.sharedRequireBacklog)
        << ", \"floor_window_ms\": " << jsonNum(p.floorWindowUs / 1000.0)
        << ", \"level_ms\": " << jsonNum(p.levelMs) << ", \"level_rtts\": " << jsonNum(p.levelRtts)
        << ", \"backlog_ms\": " << jsonNum(p.backlogMs)
        << ", \"backlog_window_ms\": " << jsonNum(p.backlogWindowUs / 1000.0)
        << ", \"backlog_require_growth\": " << b(p.backlogRequireGrowth)
        << ", \"offered_buffer\": " << b(p.offeredBuffer)
        << ", \"propagation_min_z\": " << jsonNum(p.propagationMinZ)
        << ", \"min_signals\": " << p.minSignals
        << ", \"backlog_flush_ratio\": " << jsonNum(p.backlogFlushRatio)
        << ", \"solo_backlog_ms\": " << jsonNum(p.soloBacklogMs)
        << ", \"persist_rtts\": " << jsonNum(p.persistRtts)
        << ", \"persist_min_ms\": " << jsonNum(p.persistMinUs / 1000.0)
        << ", \"backlog_rate_window_ms\": " << jsonNum(p.backlogRateWindowUs / 1000.0)
        << ", \"calm_delay_k\": " << jsonNum(p.calmDelayK)
        << ", \"verified_ms\": " << jsonNum(p.verifiedMs)
        << ", \"loss_rate\": " << jsonNum(p.lossRate)
        << ", \"loss_window_rtts\": " << jsonNum(p.lossWindowRtts)
        << ", \"loss_min_packets\": " << p.lossMinPackets << "}";
  }
  out << "\n  },\n  \"groups\": {";
  bool first = true;
  for (const auto& [group, peers] : groups) {
    out << (first ? "" : ",") << "\n    " << jsonString(group) << ": [";
    for (size_t i = 0; i < peers.size(); ++i) out << (i ? ", " : "") << jsonString(peers[i]);
    out << "]";
    first = false;
  }
  out << "\n  },\n  \"flows\": [";
  for (size_t i = 0; i < flows.size(); ++i) {
    const auto& f = flows[i];
    out << (i ? "," : "") << "\n    {\"connection_id\": " << jsonString(f.info.id)
        << ", \"peer\": " << jsonString(f.info.peer) << ", \"flow\": " << jsonString(f.info.name)
        << ", \"group\": " << (f.info.group.empty() ? "null" : jsonString(f.info.group))
        << ", \"eligible\": " << b(f.eligible) << ", \"closed\": " << b(f.closed)
        << ", \"samples_file\": " << (f.hasSamples ? jsonString(sampleFileName(f.info)) : "null")
        << ", \"sent_file\": " << (f.hasSamples ? jsonString(sentFileName(f.info)) : "null")
        << ", \"acked_file\": " << (f.hasSamples ? jsonString(ackedFileName(f.info)) : "null")
        << ", \"lost_file\": " << (f.hasSamples ? jsonString(lostFileName(f.info)) : "null") << "}";
  }
  out << "\n  ]\n}\n";
  return out.str();
}

std::vector<Variant> selectVariants(const Params& base, const std::vector<std::string>& names) {
  std::vector<Variant> variants;
  for (auto& variant : builtinVariants(base))
    if (names.empty() || std::find(names.begin(), names.end(), variant.name) != names.end())
      variants.push_back(std::move(variant));
  // "full" drives the per-ACK CSV and the group view; keep it first.
  if (variants.empty() || variants.front().name != "full")
    variants.insert(variants.begin(), builtinVariants(base).front());
  return variants;
}

Engine::Engine(std::vector<Variant> variants, Sink sink)
    : variants_(std::move(variants)), sink_(std::move(sink)) {}

void Engine::addFlow(const FlowInfo& info) {
  auto& flow = flows_[info.id];
  flow.info = info;
  flow.active = true;
  if (flow.detectors.empty())
    for (const auto& variant : variants_)
      flow.detectors.push_back(std::make_unique<FlowDetector>(variant.params));
  if (!info.group.empty() && !groups_.count(info.group)) {
    auto group = std::make_unique<GroupState>(variants_.front().params);
    for (const auto& variant : variants_)
      group->layers.push_back(std::make_unique<GroupLayer>(variant.params));
    groups_[info.group] = std::move(group);
  }
}

void Engine::removeFlow(const std::string& id) {
  const auto it = flows_.find(id);
  if (it == flows_.end()) return;
  it->second.active = false;
  if (const auto g = groups_.find(it->second.info.group); g != groups_.end())
    g->second->shared.removeMember(id);
}

bool Engine::active(const std::string& id) const {
  const auto it = flows_.find(id);
  return it != flows_.end() && it->second.active;
}

void Engine::onSent(const std::string& id, int64_t sendUs, uint64_t bytes) {
  const auto it = flows_.find(id);
  if (it == flows_.end() || !it->second.active) return;
  for (auto& detector : it->second.detectors) detector->onSent(sendUs, bytes);
  if (const auto g = groups_.find(it->second.info.group); g != groups_.end())
    g->second->shared.onSent(sendUs, bytes);
}

void Engine::onLoss(const std::string& id, uint32_t packets) {
  if (const auto it = flows_.find(id); it != flows_.end() && it->second.active)
    it->second.pendingLost += packets;
}

size_t Engine::activeMembers(const std::string& group) const {
  size_t count = 0;
  for (const auto& [id, flow] : flows_) count += flow.active && flow.info.group == group;
  return count;
}

bool Engine::onAck(const std::string& id, AckSample sample) {
  const auto it = flows_.find(id);
  if (it == flows_.end() || !it->second.active) return false;
  auto& flow = it->second;
  sample.newlyLost += std::exchange(flow.pendingLost, 0);
  ++flow.acks;
  flow.last = sample;

  GroupState* group = nullptr;
  if (const auto g = groups_.find(flow.info.group); g != groups_.end()) group = g->second.get();
  flow.shared = {};
  if (group) {
    // Data waiting: the relay holds unsent bytes, or cwnd is (almost) full.
    const bool dataWaiting = sample.streamBufferBytes > 0 ||
        (sample.cwndBytes > 0 && sample.inflightBytes + 1500 >= sample.cwndBytes);
    group->shared.onAck(id, sample.ackUs, sample.bytesAckedTotal,
                        sample.rateValid && !sample.appLimited, dataWaiting);
    flow.shared = group->shared.context(sample.ackUs, sample.sentUs, activeMembers(flow.info.group));
  }
  // Grouped members always get their group's context, valid or still warming.
  const SharedContext* shared = group ? &flow.shared : nullptr;

  std::vector<bool> preOnset(variants_.size(), false);
  for (size_t v = 0; v < variants_.size(); ++v) {
    for (const auto& event : flow.detectors[v]->onAck(sample, shared)) {
      if (event.name == "pre_signal_on") preOnset[v] = true;
      // BBR's own reaction is the baseline and identical in every variant.
      const bool common = event.name == "bbr_bw_drop" || event.name == "app_limited_exit";
      if (common && v > 0) continue;
      sink_(common ? "" : variants_[v].name, "flow", flow.info, event);
    }
  }
  if (group) {
    std::vector<GroupLayer::Member> members;
    for (size_t v = 0; v < variants_.size(); ++v) {
      members.clear();
      for (auto& [memberId, member] : flows_)
        if (member.active && member.info.group == flow.info.group)
          members.push_back({memberId, member.detectors[v].get()});
      if (members.size() < 2) continue;
      for (const auto& event : group->layers[v]->evaluate(sample.ackUs, id, preOnset[v], members))
        sink_(variants_[v].name, "group", flow.info, event);
    }
  }
  return true;
}

std::string Engine::sampleRow(const std::string& id) const {
  const auto& flow = flows_.at(id);
  const auto& x = flow.last;
  const auto& s = flow.detectors.front()->signals();
  double memberZ = NAN, pooled = NAN;
  bool pooledOn = false;
  if (const auto g = groups_.find(flow.info.group); g != groups_.end()) {
    const auto& layer = *g->second->layers.front();
    memberZ = layer.memberZ(id);
    if (layer.activeMembers() >= 2) {
      pooled = layer.pooled();
      pooledOn = layer.pooledOn();
    }
  }
  std::ostringstream row;
  row << x.ackUs << ',' << x.sentUs << ',' << (x.rttUs ? std::to_string(*x.rttUs) : "") << ','
      << x.minRttUs << ',' << x.srttUs << ',' << num(s.queueDelayMs) << ',' << x.rateValid << ','
      << x.appLimited << ',' << num(x.sendBps) << ',' << num(x.ackBps) << ',' << num(x.bbrBwBps)
      << ',' << x.cwndBytes << ',' << x.inflightBytes << ',' << x.streamBufferBytes << ','
      << x.bytesAckedTotal << ',' << x.bytesSentAtSend << ',' << phaseName(x.phase) << ','
      << x.newlyLost << ',' << x.relaySaturated << ',' << s.mask << ',' << num(s.ratio) << ','
      << s.deficitCount << ',' << num(s.trend) << ',' << num(s.residualTrend) << ','
      << num(s.expectedQueueMs) << ',' << num(s.gamma) << ',' << num(s.excessMs) << ','
      << num(s.zDeficit) << ',' << num(s.zGradient) << ',' << num(s.zExcess) << ','
      << num(s.score) << ',' << s.deficitPre << ',' << s.gradientPre << ',' << s.excessHigh << ','
      << s.gccOveruse << ',' << s.propagated << ',' << s.pre << ',' << s.confirmed << ','
      << num(memberZ) << ',' << num(pooled) << ',' << pooledOn << ',' << s.sharedUsed << ','
      << (flow.shared.valid ? num(flow.shared.capacityBps) : "") << ','
      << (flow.shared.valid ? num(flow.shared.deliveredBps) : "") << ','
      << (flow.shared.valid ? flow.shared.limited : 0) << ',' << num(s.offeredRatio) << ','
      << s.offeredPre << '\n';
  return row.str();
}

} // namespace openmoq::moqx::shadow
