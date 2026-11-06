/* SPDX-License-Identifier: Apache-2.0 */
#include "shadow/Detector.h"

#include <algorithm>
#include <iomanip>
#include <sstream>

namespace openmoq::moqx::shadow {
namespace {

std::string num(double value) {
  if (!std::isfinite(value)) return "null";
  std::ostringstream out;
  out << std::setprecision(6) << value;
  return out.str();
}

class Detail {
 public:
  Detail& add(const char* key, double value) {
    sep();
    out_ << '"' << key << "\":" << num(value);
    return *this;
  }
  Detail& add(const char* key, int64_t value) {
    sep();
    out_ << '"' << key << "\":" << value;
    return *this;
  }
  Detail& add(const char* key, bool value) {
    sep();
    out_ << '"' << key << "\":" << (value ? "true" : "false");
    return *this;
  }
  Detail& add(const char* key, const std::string& value) {
    sep();
    out_ << '"' << key << "\":\"" << value << '"';
    return *this;
  }
  Detail& raw(const char* key, const std::string& json) {
    sep();
    out_ << '"' << key << "\":" << json;
    return *this;
  }
  std::string str() const { return out_.str(); }

 private:
  void sep() {
    if (!first_) out_ << ',';
    first_ = false;
  }
  std::ostringstream out_;
  bool first_{true};
};

template <class Points, class Field>
double linearSlope(const Points& points, Field field) {
  const double x0 = points.front().xMs;
  double sx = 0, sy = 0;
  for (const auto& p : points) {
    sx += p.xMs - x0;
    sy += p.*field;
  }
  const double n = static_cast<double>(points.size());
  const double mx = sx / n, my = sy / n;
  double num = 0, den = 0;
  for (const auto& p : points) {
    const double dx = p.xMs - x0 - mx;
    num += dx * (p.*field - my);
    den += dx * dx;
  }
  return den > 0 ? num / den : 0.0;
}

bool isProbeRttLike(BbrPhase phase) {
  return phase == BbrPhase::ProbeRtt;
}

} // namespace

const char* phaseName(BbrPhase phase) {
  switch (phase) {
    case BbrPhase::Startup: return "startup";
    case BbrPhase::Drain: return "drain";
    case BbrPhase::ProbeBwDown: return "probe_bw_down";
    case BbrPhase::ProbeBwCruise: return "probe_bw_cruise";
    case BbrPhase::ProbeBwRefill: return "probe_bw_refill";
    case BbrPhase::ProbeBwUp: return "probe_bw_up";
    case BbrPhase::ProbeBw: return "probe_bw";
    case BbrPhase::ProbeRtt: return "probe_rtt";
    case BbrPhase::Unknown: break;
  }
  return "unknown";
}

std::vector<Variant> builtinVariants(const Params& base) {
  std::vector<Variant> variants;
  variants.push_back({"full", base});
  auto noPropagation = base;
  noPropagation.propagation = false;
  variants.push_back({"no_propagation", noPropagation});
  auto noMasks = base;
  noMasks.maskPhases = false;
  variants.push_back({"no_masks", noMasks});
  auto noNormalization = base;
  noNormalization.normalizeBySent = false;
  variants.push_back({"no_normalization", noNormalization});
  // Grouped members judged on their own samples only (no shared aggregate).
  auto noShared = base;
  noShared.sharedContext = false;
  variants.push_back({"no_shared_context", noShared});
  // One signal alone: no agreement rule, no other signal.
  const auto singleSignal = [](Params& p) {
    p.minSignals = 1;
    p.soloBacklogMs = 0;
    p.lossRate = 0;
  };
  auto deficitOnly = base;
  deficitOnly.useGradient = false;
  deficitOnly.useExcess = false;
  deficitOnly.backlogMs = 0;
  deficitOnly.levelMs = 0;
  deficitOnly.useOffered = false;
  singleSignal(deficitOnly);
  variants.push_back({"deficit_only", deficitOnly});
  auto offeredOnly = base;
  offeredOnly.useDeficit = false;
  offeredOnly.useGradient = false;
  offeredOnly.useExcess = false;
  offeredOnly.backlogMs = 0;
  offeredOnly.levelMs = 0;
  singleSignal(offeredOnly);
  variants.push_back({"offered_only", offeredOnly});
  auto gradientOnly = base;
  gradientOnly.useDeficit = false;
  gradientOnly.useExcess = false;
  gradientOnly.backlogMs = 0;
  gradientOnly.levelMs = 0;
  gradientOnly.useOffered = false;
  singleSignal(gradientOnly);
  variants.push_back({"gradient_only", gradientOnly});
  // GCC's own overuse rule on the same RTT trendline: s = 1, no BBR
  // awareness, no send normalization, no propagation.
  auto gcc = base;
  gcc.useDeficit = false;
  gcc.useExcess = false;
  gcc.backlogMs = 0;
  gcc.levelMs = 0;
  gcc.useOffered = false;
  gcc.gradientScale = 1.0;
  gcc.normalizeBySent = false;
  gcc.maskPhases = false;
  gcc.propagation = false;
  gcc.sharedContext = false;
  singleSignal(gcc);
  variants.push_back({"gcc", gcc});
  auto backlogOnly = base;
  backlogOnly.useDeficit = false;
  backlogOnly.useGradient = false;
  backlogOnly.useOffered = false;
  backlogOnly.useExcess = false;
  backlogOnly.levelMs = 0;
  if (backlogOnly.backlogMs <= 0) backlogOnly.backlogMs = 50.0;
  singleSignal(backlogOnly);
  variants.push_back({"backlog_only", backlogOnly});
  auto lossOnly = base;
  lossOnly.useDeficit = false;
  lossOnly.useGradient = false;
  lossOnly.useOffered = false;
  lossOnly.useExcess = false;
  lossOnly.backlogMs = 0;
  lossOnly.levelMs = 0;
  singleSignal(lossOnly);
  lossOnly.lossRate = base.lossRate > 0 ? base.lossRate : 0.02;
  variants.push_back({"loss_only", lossOnly});
  return variants;
}

std::vector<std::string> builtinVariantNames() {
  std::vector<std::string> names;
  for (const auto& variant : builtinVariants(Params{})) names.push_back(variant.name);
  return names;
}

std::string applyParam(Params& p, const std::string& name, double v) {
  const std::string key = "shadow.params." + name;
  auto positive = [&](double& field) -> std::string {
    if (!(v > 0)) return key + " must be > 0";
    field = v;
    return {};
  };
  auto unit = [&](double& field) -> std::string {
    if (!(v > 0 && v < 1)) return key + " must be in (0, 1)";
    field = v;
    return {};
  };
  auto count = [&](uint32_t& field, uint32_t min) -> std::string {
    if (v < min || v != std::floor(v) || v > 1e6) return key + " must be an integer >= " + std::to_string(min);
    field = static_cast<uint32_t>(v);
    return {};
  };
  auto millis = [&](int64_t& field) -> std::string {
    if (!(v > 0)) return key + " must be > 0";
    field = static_cast<int64_t>(v * 1000);
    return {};
  };
  auto flag = [&](bool& field) -> std::string {
    if (v != 0 && v != 1) return key + " must be 0 or 1";
    field = v == 1;
    return {};
  };
  auto nonNegative = [&](double& field) -> std::string {
    if (!(v >= 0)) return key + " must be >= 0";
    field = v;
    return {};
  };
  if (name == "theta") return unit(p.theta);
  if (name == "deficit_samples") return count(p.deficitSamples, 1);
  if (name == "deficit_min_delay_ms") return nonNegative(p.deficitMinDelayMs);
  if (name == "trend_window") return count(p.trendWindow, 3);
  if (name == "trend_smoothing") return unit(p.trendSmoothing);
  if (name == "trend_gain") return positive(p.trendGain);
  if (name == "trend_group_ms") return millis(p.trendGroupUs);
  if (name == "gradient_scale") return positive(p.gradientScale);
  if (name == "gradient_points") return count(p.gradientPoints, 1);
  if (name == "gamma_initial") return positive(p.gammaInitial);
  if (name == "gamma_min") return positive(p.gammaMin);
  if (name == "gamma_max") return positive(p.gammaMax);
  if (name == "gamma_k_up") return positive(p.gammaKUp);
  if (name == "gamma_k_down") return positive(p.gammaKDown);
  if (name == "excess_ms") return positive(p.excessMs);
  if (name == "excess_trigger") return flag(p.excessTrigger);
  if (name == "use_deficit") return flag(p.useDeficit);
  if (name == "use_gradient") return flag(p.useGradient);
  if (name == "use_offered") return flag(p.useOffered);
  if (name == "use_excess") return flag(p.useExcess);
  if (name == "floor_window_ms") {
    if (!(v >= 0)) return key + " must be >= 0";
    p.floorWindowUs = static_cast<int64_t>(v * 1000);
    return {};
  }
  if (name == "level_ms") return nonNegative(p.levelMs);
  if (name == "level_rtts") return positive(p.levelRtts);
  if (name == "backlog_ms") return nonNegative(p.backlogMs);
  if (name == "backlog_window_ms") return millis(p.backlogWindowUs);
  if (name == "backlog_require_growth") return flag(p.backlogRequireGrowth);
  if (name == "backlog_flush_ratio") return nonNegative(p.backlogFlushRatio);
  if (name == "offered_buffer") return flag(p.offeredBuffer);
  if (name == "probe_up_factor") return positive(p.probeUpFactor);
  if (name == "post_probe_rtt_mask_rtts") return positive(p.postProbeRttMaskRtts);
  if (name == "bbr_drop_fraction") return unit(p.bbrDropFraction);
  if (name == "bbr_drop_lookback_ms") return millis(p.bbrDropLookbackUs);
  if (name == "loss_packets") return count(p.lossPackets, 1);
  if (name == "send_queue_ms") return positive(p.sendQueueMs);
  if (name == "confirm_hold_ms") return millis(p.confirmHoldUs);
  if (name == "clear_ms") return millis(p.clearUs);
  if (name == "pool_z") return positive(p.poolZ);
  if (name == "lag_rtts") return positive(p.lagRtts);
  if (name == "lag_max_ms") return millis(p.lagMaxUs);
  if (name == "propagation_factor") {
    if (!(v > 0 && v <= 1)) return key + " must be in (0, 1]";
    p.propagationFactor = v;
    return {};
  }
  if (name == "propagation_rtts") return positive(p.propagationRtts);
  if (name == "propagation") return flag(p.propagation);
  if (name == "propagation_min_z") return nonNegative(p.propagationMinZ);
  if (name == "min_signals") return count(p.minSignals, 1);
  if (name == "solo_backlog_ms") return nonNegative(p.soloBacklogMs);
  if (name == "persist_rtts") return nonNegative(p.persistRtts);
  if (name == "persist_min_ms") return millis(p.persistMinUs);
  if (name == "backlog_rate_window_ms") {
    if (!(v >= 0)) return key + " must be >= 0";
    p.backlogRateWindowUs = static_cast<int64_t>(v * 1000);
    return {};
  }
  if (name == "calm_delay_k") return nonNegative(p.calmDelayK);
  if (name == "verified_ms") return nonNegative(p.verifiedMs);
  if (name == "loss_rate") {
    if (!(v >= 0 && v < 1)) return key + " must be in [0, 1)";
    p.lossRate = v;
    return {};
  }
  if (name == "loss_window_rtts") return positive(p.lossWindowRtts);
  if (name == "loss_min_packets") return count(p.lossMinPackets, 1);
  if (name == "propagation_min_ms") return millis(p.propagationMinUs);
  if (name == "residual_floor_ms") {
    if (!(v >= 0)) return key + " must be >= 0";
    p.residualFloorMs = v;
    return {};
  }
  if (name == "offered_window_ms") return millis(p.offeredWindowUs);
  if (name == "offered_min_bytes") return positive(p.offeredMinBytes);
  if (name == "shared_window_ms") return millis(p.sharedWindowUs);
  if (name == "capacity_lookback_ms") return millis(p.capacityLookbackUs);
  if (name == "shared_require_backlog") return flag(p.sharedRequireBacklog);
  if (name == "calm_alpha") return unit(p.calmAlpha);
  if (name == "calm_warmup") return count(p.calmWarmup, 1);
  return "unknown shadow.params key: " + name;
}

void SharedBottleneck::onSent(int64_t sendUs, uint64_t bytes) {
  const int64_t start = sendUs - sendUs % kBinUs;
  if (sends_.empty() || start > sends_.back().startUs) {
    sends_.push_back({start, bytes});
  } else {
    // Same bin, or a late write: fold into the newest bin so bins the model
    // already consumed are never rewritten.
    sends_.back().bytes += bytes;
  }
  while (sends_.size() > 1 && sendUs - sends_.front().startUs > 3'000'000) sends_.pop_front();
}

void SharedBottleneck::onAck(const std::string& member, int64_t ackUs, uint64_t bytesAckedTotal,
                             bool networkLimited, bool dataWaiting) {
  if (p_.sharedRequireBacklog) networkLimited = networkLimited && dataWaiting;
  Member* state = nullptr;
  for (auto& [id, m] : members_)
    if (id == member) state = &m;
  if (!state) {
    members_.emplace_back(member, Member{bytesAckedTotal, ackUs, networkLimited});
    if (!firstAckUs_) firstAckUs_ = ackUs;
    return;
  }
  if (bytesAckedTotal > state->ackedTotal) {
    const uint64_t delta = bytesAckedTotal - state->ackedTotal;
    acks_.emplace_back(ackUs, delta);
    windowBytes_ += delta;
  }
  state->ackedTotal = std::max(state->ackedTotal, bytesAckedTotal);
  state->lastUs = ackUs;
  state->networkLimited = networkLimited;
  while (!acks_.empty() && ackUs - acks_.front().first > p_.sharedWindowUs) {
    windowBytes_ -= acks_.front().second;
    acks_.pop_front();
  }
  // Capacity = windowed max of aggregate delivery (BBR's max filter, applied
  // to the whole group). Keyframe collisions saturate the link every GOP, so
  // it tracks the shared link rate rather than any member's share.
  if (ackUs - firstAckUs_ >= p_.sharedWindowUs &&
      (rates_.empty() || ackUs - rates_.back().first >= 10'000)) {
    rates_.emplace_back(ackUs, windowBytes_ * 8e6 / static_cast<double>(p_.sharedWindowUs));
    while (!rates_.empty() && ackUs - rates_.front().first > p_.capacityLookbackUs) rates_.pop_front();
  }
}

void SharedBottleneck::removeMember(const std::string& member) {
  std::erase_if(members_, [&](const auto& m) { return m.first == member; });
}

void SharedBottleneck::model(int64_t uptoUs) {
  double capacity = 0;
  for (const auto& [t, rate] : rates_) capacity = std::max(capacity, rate);
  for (auto& bin : sends_) {
    if (bin.modelled) continue;
    // A bin is final once its 5 ms have passed.
    if (bin.startUs + kBinUs > uptoUs) break;
    if (capacity > 0) {
      const double drainedMs = modelledUs_ ? (bin.startUs - modelledUs_) / 1000.0 : 0.0;
      queueMs_ = std::clamp(queueMs_ - drainedMs + bin.bytes * 8e3 / capacity, 0.0, 2000.0);
    }
    bin.queueMs = queueMs_;
    bin.modelled = true;
    modelledUs_ = bin.startUs;
  }
}

SharedContext SharedBottleneck::context(int64_t nowUs, int64_t sendUs, size_t members) {
  SharedContext context;
  for (const auto& [t, rate] : rates_) context.capacityBps = std::max(context.capacityBps, rate);
  if (members < 2 || context.capacityBps <= 0) return context;
  context.valid = true;
  if (nowUs - firstAckUs_ >= p_.sharedWindowUs)
    context.deliveredBps = windowBytes_ * 8e6 / static_cast<double>(p_.sharedWindowUs);
  size_t limited = 0, active = 0;
  for (const auto& [id, m] : members_) {
    if (nowUs - m.lastUs > 500'000) continue;
    ++active;
    limited += m.networkLimited;
  }
  // Aggregate delivery is only a capacity measurement once the whole window
  // was network-limited; a 160 ms keyframe burst never qualifies, a real
  // capacity drop does after one window.
  if (active && 2 * limited >= active) {
    if (!limitedSinceUs_) limitedSinceUs_ = nowUs;
  } else {
    limitedSinceUs_ = 0;
  }
  context.limited = limitedSinceUs_ && nowUs - limitedSinceUs_ >= p_.sharedWindowUs;
  model(nowUs);
  // The queue a packet met is the one modelled at its send time.
  for (auto it = sends_.rbegin(); it != sends_.rend(); ++it) {
    if (it->startUs <= sendUs) {
      if (it->modelled) context.expectedQueueMs = it->queueMs;
      break;
    }
  }
  return context;
}

void Ewma::add(double value, double alpha) {
  if (!std::isfinite(value)) return;
  if (count_ == 0) {
    mean_ = value;
    var_ = 0;
  } else {
    // Converge quickly during warm-up, then forget at the configured rate.
    const double a = std::max(alpha, 1.0 / static_cast<double>(count_ + 1));
    const double diff = value - mean_;
    const double increment = a * diff;
    mean_ += increment;
    var_ = (1 - a) * (var_ + diff * increment);
  }
  ++count_;
}

double Ewma::z(double value, double floor) const {
  if (!std::isfinite(value) || count_ == 0) return NAN;
  return (value - mean_) / std::max(sd(), floor);
}

std::vector<Event> FlowDetector::onAck(const AckSample& x, const SharedContext* shared) {
  std::vector<Event> events;
  if (!p_.sharedContext) shared = nullptr;
  s_.sharedUsed = shared && shared->valid;
  lastUs_ = x.ackUs;
  if (x.srttUs > 0) srttUs_ = x.srttUs;
  if (x.minRttUs > 0) minRttUs_ = x.minRttUs;
  s_.queueDelayMs = x.rttUs && x.minRttUs > 0
      ? std::max<int64_t>(0, *x.rttUs - x.minRttUs) / 1000.0
      : NAN;
  s_.deficitValid = false;
  s_.ratio = NAN;
  s_.offeredValid = false;
  s_.offeredRatio = NAN;
  s_.gradientValid = false;
  s_.excessHigh = false;
  s_.propagated = p_.propagation && x.ackUs < propagationUntilUs_;
  const double factor = s_.propagated ? p_.propagationFactor : 1.0;

  bool leftAppLimited = false;
  if (x.rateValid) {
    if (x.appLimited) {
      notAppLimitedRun_ = 0;
      if (++appLimitedRun_ >= 2 * p_.deficitSamples) appLimitedRegime_ = true;
    } else {
      appLimitedRun_ = 0;
      if (++notAppLimitedRun_ == 2 * p_.deficitSamples && appLimitedRegime_) {
        appLimitedRegime_ = false;
        leftAppLimited = true;
      }
    }
  }
  updateMask(x);
  // Annotation only: the flow leaving the app-limited regime while BBR is
  // not probing is the moment delivery samples start reflecting capacity.
  if (leftAppLimited && s_.mask.empty() && x.phase != BbrPhase::ProbeBwUp) {
    events.push_back({"app_limited_exit", x.ackUs,
        Detail().add("phase", std::string(phaseName(x.phase))).str()});
  }
  ackedHistory_.emplace_back(x.ackUs, x.bytesAckedTotal);
  bufferHistory_.emplace_back(x.ackUs, x.streamBufferBytes);
  while (ackedHistory_.size() > 1 && x.ackUs - ackedHistory_.front().first > p_.offeredWindowUs + 2'000'000)
    ackedHistory_.pop_front();
  while (bufferHistory_.size() > 1 && x.ackUs - bufferHistory_.front().first > p_.offeredWindowUs + 2'000'000)
    bufferHistory_.pop_front();
  updateDeficit(x, factor, shared);
  updateOffered(x, factor);
  updateBacklog(x, factor);
  updateLoss(x, factor);
  updateGradient(x, factor, shared);
  updateExcess(x);
  updateScore(x);
  updateConfirmed(x, events);
  updatePre(x, events);
  return events;
}

int64_t FlowDetector::persistUs(double factor) const {
  if (!(p_.persistRtts > 0)) return 0;
  const auto rtt = static_cast<double>(minRttUs_ > 0 ? minRttUs_ : srttUs_);
  const auto need = std::max<double>(p_.persistMinUs, p_.persistRtts * rtt);
  return std::max<int64_t>(1, static_cast<int64_t>(need * factor));
}

double FlowDetector::effectiveThreshold(double fixedMs, const Ewma& calm) const {
  if (!(fixedMs > 0) || !(p_.calmDelayK > 0) || calm.count() < p_.calmWarmup) return fixedMs;
  // Never below 1 ms: on a very quiet path the calm spread is ~0.
  return std::min(fixedMs, std::max(1.0, calm.mean() + p_.calmDelayK * calm.sd()));
}

void FlowDetector::updateMask(const AckSample& x) {
  if (isProbeRttLike(lastPhase_) && !isProbeRttLike(x.phase)) probeRttExitUs_ = x.ackUs;
  lastPhase_ = x.phase;
  s_.mask.clear();
  if (x.relaySaturated) {
    s_.mask = "relay_saturated";
    return;
  }
  const bool startup = x.phase == BbrPhase::Startup || x.phase == BbrPhase::Drain;
  // App-limited video can keep BBR in Startup indefinitely: app-limited
  // samples never prove a bandwidth plateau. Startup only builds a queue
  // while it is actually probing, so once the flow has been app-limited in
  // Startup for a while, stop masking until BBR leaves Startup. Staying
  // unmasked matters: the capacity drop is exactly what ends app-limiting.
  if (!startup) {
    startupAppLimitedSinceUs_ = 0;
    startupSettled_ = false;
  } else if (appLimitedRegime_) {
    if (!startupAppLimitedSinceUs_) startupAppLimitedSinceUs_ = x.ackUs;
    if (x.ackUs - startupAppLimitedSinceUs_ >= kStartupSettleUs) startupSettled_ = true;
  } else {
    startupAppLimitedSinceUs_ = 0;
  }
  if (!p_.maskPhases) return;
  if (startup && !startupSettled_) {
    s_.mask = "startup";
  } else if (x.phase == BbrPhase::ProbeRtt) {
    s_.mask = "probe_rtt";
  } else if (x.ackUs - probeRttExitUs_ <
             static_cast<int64_t>(p_.postProbeRttMaskRtts * std::max<int64_t>(srttUs_, 10'000))) {
    s_.mask = "post_probe_rtt";
  }
}

void FlowDetector::updateDeficit(const AckSample& x, double factor, const SharedContext* shared) {
  s_.deficitCount = deficitCount_;
  if (!p_.useDeficit) return;
  const int64_t hold = std::max<int64_t>(2 * srttUs_, 200'000);
  if (x.ackUs - lastDeficitValidUs_ > hold) deficitCount_ = 0;
  if (deficitCount_ == 0) deficitSinceUs_ = 0;
  double ratio = NAN;
  if (shared) {
    // Members split the shared link, so one member's delivery falls whenever
    // keyframes collide. The group aggregate only falls when capacity does.
    // Until the group capacity is known, a member has no valid deficit:
    // falling back to its own samples would alarm on the first collision.
    if (s_.mask.empty() && shared->valid && shared->limited && shared->capacityBps > 0 &&
        std::isfinite(shared->deliveredBps))
      ratio = shared->deliveredBps / shared->capacityBps;
  } else if (s_.mask.empty() && x.rateValid && !x.appLimited && x.bbrBwBps > 0 && x.ackBps > 0) {
    // BBR's max_bw keeps the old capacity for several RTTs after a drop;
    // fresh delivery samples fall within one.
    ratio = x.ackBps / x.bbrBwBps;
  }
  if (!std::isfinite(ratio)) {
    s_.deficitCount = deficitCount_;
    return;
  }
  const double theta = 1.0 - (1.0 - p_.theta) * factor;
  s_.ratio = ratio;
  s_.deficitValid = true;
  lastDeficitValidUs_ = x.ackUs;
  const double minDelay = effectiveThreshold(p_.deficitMinDelayMs, calmDelay_);
  s_.deficitMinDelayMs = minDelay;
  const bool queued = !(minDelay > 0) ||
      (std::isfinite(s_.queueDelayMs) && s_.queueDelayMs >= minDelay * factor);
  deficitCount_ = ratio < theta && queued ? deficitCount_ + 1 : 0;
  if (deficitCount_ == 1) deficitSinceUs_ = x.ackUs;
  s_.deficitCount = deficitCount_;
  if (calmDeficit_.count() >= 20) {
    s_.zDeficit = calmDeficit_.z(1.0 - ratio, 0.05);
    lastZDeficitUs_ = x.ackUs;
  }
}

void FlowDetector::onSent(int64_t sendUs, uint64_t bytes) {
  sentTotal_ += bytes;
  sentHistory_.emplace_back(sendUs, sentTotal_);
  while (sentHistory_.size() > 1 && sendUs - sentHistory_.front().first > p_.offeredWindowUs + 2'000'000)
    sentHistory_.pop_front();
}

namespace {
// Cumulative value at time t from a (time, cumulative) history.
std::optional<uint64_t> cumulativeAt(const std::deque<std::pair<int64_t, uint64_t>>& history, int64_t t) {
  if (history.empty() || history.front().first > t) return std::nullopt;
  auto it = std::upper_bound(history.begin(), history.end(), t,
                             [](int64_t value, const auto& entry) { return value < entry.first; });
  return std::prev(it)->second;
}
} // namespace

void FlowDetector::updateOffered(const AckSample& x, double factor) {
  if (!p_.useOffered) return;
  const int64_t hold = std::max<int64_t>(2 * srttUs_, 200'000);
  if (x.ackUs - lastOfferedValidUs_ > hold) offeredCount_ = 0;
  if (offeredCount_ == 0) offeredSinceUs_ = 0;
  if (!s_.mask.empty() || x.minRttUs <= 0) return;
  // What arrived in the last window vs what was sent one base RTT earlier.
  // Their difference is the queue growth over the window; a whole GOP per
  // window means a keyframe's own queue has drained inside it.
  const int64_t end = x.ackUs, sentEnd = x.ackUs - x.minRttUs;
  const auto ackedThen = cumulativeAt(ackedHistory_, end - p_.offeredWindowUs);
  const auto sentNow = cumulativeAt(sentHistory_, sentEnd);
  const auto sentThen = cumulativeAt(sentHistory_, sentEnd - p_.offeredWindowUs);
  if (!ackedThen || !sentNow || !sentThen || *sentNow <= *sentThen) return;
  double sent = static_cast<double>(*sentNow - *sentThen);
  if (p_.offeredBuffer) {
    // Bytes the application offered = bytes sent + growth of what it queued
    // behind BBR's cwnd. Without this, a cwnd-limited sender sends only what
    // is delivered and the ratio returns to 1 while the relay queue grows.
    const auto bufNow = cumulativeAt(bufferHistory_, sentEnd);
    const auto bufThen = cumulativeAt(bufferHistory_, sentEnd - p_.offeredWindowUs);
    if (bufNow && bufThen)
      sent = std::max(sent + static_cast<double>(*bufNow) - static_cast<double>(*bufThen), 1.0);
  }
  if (sent < p_.offeredMinBytes || x.bytesAckedTotal < *ackedThen) return;
  const double ratio = (x.bytesAckedTotal - *ackedThen) / sent;
  const double theta = 1.0 - (1.0 - p_.theta) * factor;
  s_.offeredValid = true;
  s_.offeredRatio = ratio;
  lastOfferedValidUs_ = x.ackUs;
  offeredCount_ = ratio < theta ? offeredCount_ + 1 : 0;
  if (offeredCount_ == 1) offeredSinceUs_ = x.ackUs;
  if (calmOffered_.count() >= 20) {
    s_.zOffered = calmOffered_.z(1.0 - ratio, 0.05);
    lastZOfferedUs_ = x.ackUs;
  }
}

void FlowDetector::updateBacklog(const AckSample& x, double factor) {
  s_.backlogMs = NAN;
  s_.backlogPre = false;
  soloBacklog_ = false;
  if ((p_.backlogMs <= 0 && p_.verifiedMs <= 0 && p_.soloBacklogMs <= 0) || x.minRttUs <= 0) return;
  if (!s_.mask.empty()) {
    backlogWindow_.clear();
    backlogHistory_.clear();
    backlogDraining_ = false;
    backlogFirstUs_ = 0;
    return;
  }
  const auto ackedThen = cumulativeAt(ackedHistory_, x.ackUs - p_.offeredWindowUs);
  if (!ackedThen || x.bytesAckedTotal < *ackedThen) return;
  const double delivered = static_cast<double>(x.bytesAckedTotal - *ackedThen);
  if (delivered < p_.offeredMinBytes) return;
  const double deliveryBps = delivered * 8.0 / (p_.offeredWindowUs / 1e6);
  // Long-run demand: what the path delivers on average (10 s EWMA).
  const double dt = demandLastUs_ ? static_cast<double>(x.ackUs - demandLastUs_) : 0.0;
  demandLastUs_ = x.ackUs;
  demandBps_ = demandBps_ > 0 ? demandBps_ + (1.0 - std::exp(-dt / 10e6)) * (deliveryBps - demandBps_)
                              : deliveryBps;
  bool flushing = false;
  if (p_.backlogFlushRatio > 0 && demandBps_ > 0) {
    const auto recentThen = cumulativeAt(ackedHistory_, x.ackUs - p_.backlogWindowUs);
    if (recentThen && x.bytesAckedTotal >= *recentThen) {
      const double recentBps = (x.bytesAckedTotal - *recentThen) * 8.0 / (p_.backlogWindowUs / 1e6);
      flushing = recentBps >= p_.backlogFlushRatio * demandBps_;
    }
  }
  // The drain rate: a 1 s rate lags a capacity drop, so optionally the lower of
  // it and a short-window rate (an idle short window keeps the 1 s rate).
  double drainBps = deliveryBps;
  if (p_.backlogRateWindowUs > 0) {
    const auto shortThen = cumulativeAt(ackedHistory_, x.ackUs - p_.backlogRateWindowUs);
    if (shortThen && x.bytesAckedTotal > *shortThen) {
      drainBps = std::min(drainBps, (x.bytesAckedTotal - *shortThen) * 8.0 /
                                        (p_.backlogRateWindowUs / 1e6));
    }
  }
  const double pending = static_cast<double>(x.inflightBytes + x.streamBufferBytes);
  const double drainMs = pending * 8.0 / drainBps * 1000.0 - x.minRttUs / 1000.0;
  // Running minimum: a keyframe's backlog that drains within the window
  // never raises it; a queue that keeps growing does.
  while (!backlogWindow_.empty() && backlogWindow_.back().second >= drainMs) backlogWindow_.pop_back();
  backlogWindow_.emplace_back(x.ackUs, drainMs);
  while (x.ackUs - backlogWindow_.front().first > p_.backlogWindowUs) backlogWindow_.pop_front();
  if (!backlogFirstUs_) backlogFirstUs_ = x.ackUs;
  if (x.ackUs - backlogFirstUs_ < p_.backlogWindowUs) return;
  s_.backlogMs = backlogWindow_.front().second;
  backlogHistory_.emplace_back(x.ackUs, s_.backlogMs);
  while (backlogHistory_.size() > 1 && x.ackUs - backlogHistory_[1].first >= p_.backlogWindowUs)
    backlogHistory_.pop_front();
  if (p_.backlogRequireGrowth && x.ackUs - backlogHistory_.front().first >= p_.backlogWindowUs) {
    const double before = backlogHistory_.front().second;
    if (!backlogDraining_ && s_.backlogMs < before) {
      backlogDraining_ = true;
    } else if (backlogDraining_ &&
               (x.streamBufferBytes == 0 || s_.backlogMs >= before + p_.backlogMs)) {
      backlogDraining_ = false;
    }
  }
  // The flush gate only keeps a new alarm from opening: an alarm raised by
  // real congestion stays on through the flush instead of splitting.
  const bool gate = !backlogDraining_ && !(flushing && !pre_);
  s_.backlogPre = p_.backlogMs > 0 && s_.backlogMs >= p_.backlogMs * factor && gate;
  soloBacklog_ = p_.soloBacklogMs > 0 && s_.backlogMs >= p_.soloBacklogMs * factor && gate;
}

void FlowDetector::updateLoss(const AckSample& x, double factor) {
  s_.lossRate = NAN;
  s_.lossPre = false;
  if (!(p_.lossRate > 0) || minRttUs_ <= 0) return;
  // Packet-size estimate for converting sent bytes to packets.
  constexpr double kLossPacketBytes = 1200;
  const int64_t window = std::max<int64_t>(200'000, static_cast<int64_t>(p_.lossWindowRtts * minRttUs_));
  if (x.newlyLost) lossHistory_.emplace_back(x.ackUs, x.newlyLost);
  while (!lossHistory_.empty() && x.ackUs - lossHistory_.front().first > window) lossHistory_.pop_front();
  if (!s_.mask.empty()) return;
  // Losses are declared about one RTT after the send.
  const auto sentNow = cumulativeAt(sentHistory_, x.ackUs - minRttUs_);
  const auto sentThen = cumulativeAt(sentHistory_, x.ackUs - minRttUs_ - window);
  if (!sentNow || !sentThen || *sentNow <= *sentThen) return;
  uint32_t lost = 0;
  for (const auto& [t, n] : lossHistory_) lost += n;
  const double sentPackets = (*sentNow - *sentThen) / kLossPacketBytes;
  s_.lossRate = lost / std::max(1.0, sentPackets);
  s_.lossPre = lost >= p_.lossMinPackets && s_.lossRate >= p_.lossRate * factor;
}

void FlowDetector::updateGradient(const AckSample& x, double factor, const SharedContext* shared) {
  if (!p_.useGradient || !x.rttUs || x.minRttUs <= 0) return;
  if (!s_.mask.empty()) {
    // Masked samples (ProbeRTT and its refill, startup, relay saturation)
    // must not linger in the trendline window after the mask lifts.
    points_.clear();
    haveSmoothed_ = false;
    numDeltas_ = 0;
    expectedQueueMs_ = 0;
    gradientRun_ = 0;
    floorWindow_.clear();
    levelSinceUs_ = 0;
    return;
  }
  if (x.sentUs - lastPointSentUs_ < p_.trendGroupUs) return;
  const double delay = std::max<int64_t>(0, *x.rttUs - x.minRttUs) / 1000.0;
  if (!points_.empty() && x.bbrBwBps > 0 && x.bytesSentAtSend >= points_.back().bytes) {
    // Delay our own sending explains: a FIFO fed with the bytes the relay
    // actually sent and drained at BBR's believed capacity. Keyframes and
    // ProbeBW UP fill this model; a real capacity drop does not, because
    // the believed capacity is still the old, higher one.
    const double dtMs = x.sentUs / 1000.0 - points_.back().xMs;
    if (dtMs > 0) {
      const double sendBps = (x.bytesSentAtSend - points_.back().bytes) * 8.0 / (dtMs / 1000.0);
      expectedQueueMs_ =
          std::clamp(expectedQueueMs_ + (sendBps / x.bbrBwBps - 1.0) * dtMs, 0.0, 1000.0);
    }
  }
  lastPointSentUs_ = x.sentUs;
  // A grouped member's queue is fed by every member: use the group's model.
  const double explained = shared && shared->valid ? shared->expectedQueueMs : expectedQueueMs_;
  double residualDelay = p_.normalizeBySent ? delay - explained : delay;
  if (p_.floorWindowUs > 0) {
    while (!floorWindow_.empty() && floorWindow_.back().second >= residualDelay) floorWindow_.pop_back();
    floorWindow_.emplace_back(x.sentUs, residualDelay);
    while (x.sentUs - floorWindow_.front().first > p_.floorWindowUs) floorWindow_.pop_front();
    residualDelay = floorWindow_.front().second;
  }
  s_.floorDelayMs = residualDelay;
  lastFloorUs_ = x.ackUs;
  if (p_.levelMs > 0 && residualDelay >= p_.levelMs * factor) {
    if (!levelSinceUs_) levelSinceUs_ = x.ackUs;
  } else {
    levelSinceUs_ = 0;
  }
  const double a = p_.trendSmoothing;
  smoothedDelay_ = haveSmoothed_ ? a * smoothedDelay_ + (1 - a) * delay : delay;
  smoothedResidual_ = haveSmoothed_ ? a * smoothedResidual_ + (1 - a) * residualDelay : residualDelay;
  haveSmoothed_ = true;
  points_.push_back({x.sentUs / 1000.0, smoothedDelay_, smoothedResidual_, x.bytesSentAtSend});
  while (points_.size() > p_.trendWindow) points_.pop_front();
  ++numDeltas_;
  s_.expectedQueueMs = explained;
  if (points_.size() < p_.trendWindow) return;

  const double n = static_cast<double>(std::min<uint64_t>(numDeltas_, 60));
  const double trend = n * linearSlope(points_, &TrendPoint::yMs) * p_.trendGain;
  const double residual = n * linearSlope(points_, &TrendPoint::rMs) * p_.trendGain;

  // GCC adaptive threshold, updated with the raw trend exactly as GCC would.
  if (gamma_ == 0) gamma_ = p_.gammaInitial;
  const double dt = std::isfinite(lastGammaXMs_)
      ? std::min(points_.back().xMs - lastGammaXMs_, 100.0)
      : 0.0;
  lastGammaXMs_ = points_.back().xMs;
  if (std::abs(trend) <= gamma_ + 15.0) {
    const double k = std::abs(trend) < gamma_ ? p_.gammaKDown : p_.gammaKUp;
    gamma_ = std::clamp(gamma_ + k * (std::abs(trend) - gamma_) * dt, p_.gammaMin, p_.gammaMax);
  }

  s_.gradientValid = true;
  s_.trend = trend;
  s_.residualTrend = residual;
  s_.gamma = gamma_;
  lastGradientValidUs_ = x.ackUs;
  const double upFactor =
      p_.maskPhases && x.phase == BbrPhase::ProbeBwUp ? p_.probeUpFactor : 1.0;
  const double threshold = p_.gradientScale * gamma_ * factor * upFactor;
  // With normalization, a growing *slope* of a few ms of unexplained delay
  // is model error (capacity estimated a few % off), not congestion: require
  // the unexplained delay itself to be material too. GCC's rule has no floor.
  const double floorMs = effectiveThreshold(p_.residualFloorMs, calmResidual_);
  s_.residualFloorMs = floorMs;
  const bool material = !p_.normalizeBySent || smoothedResidual_ >= floorMs * factor;
  gradientRun_ = residual > threshold && material ? gradientRun_ + 1 : 0;
  gccRun_ = trend > gamma_ ? gccRun_ + 1 : 0;
  if (calmGradient_.count() >= 20) {
    s_.zGradient = calmGradient_.z(residual, 1.0);
    lastZGradientUs_ = x.ackUs;
  }
}

void FlowDetector::updateExcess(const AckSample& x) {
  s_.excessMs = NAN;
  s_.zExcess = NAN;
  if (!p_.useExcess || x.bbrBwBps <= 0 || x.minRttUs <= 0) return;
  // Bytes beyond BBR's own BDP estimate. Stale max_bw after a drop makes
  // this an underestimate, so it is supporting evidence only.
  const double bdpBytes = x.bbrBwBps / 8.0 * (x.minRttUs / 1e6);
  const double excessBytes = static_cast<double>(x.inflightBytes) - bdpBytes;
  s_.excessMs = excessBytes * 8.0 / x.bbrBwBps * 1000.0;
  const bool masked = !s_.mask.empty() || (p_.maskPhases && x.phase == BbrPhase::ProbeBwUp);
  s_.excessHigh = !masked && s_.excessMs > p_.excessMs;
  if (calmExcess_.count() >= 20) s_.zExcess = calmExcess_.z(s_.excessMs, 2.0);
}

void FlowDetector::updateScore(const AckSample& x) {
  const int64_t hold = std::max<int64_t>(srttUs_, 50'000);
  double score = NAN;
  if (x.ackUs - lastZDeficitUs_ <= hold && std::isfinite(s_.zDeficit)) score = s_.zDeficit;
  if (x.ackUs - lastZGradientUs_ <= hold && std::isfinite(s_.zGradient))
    score = std::isfinite(score) ? std::max(score, s_.zGradient) : s_.zGradient;
  if (x.ackUs - lastZOfferedUs_ <= hold && std::isfinite(s_.zOffered))
    score = std::isfinite(score) ? std::max(score, s_.zOffered) : s_.zOffered;
  if (!std::isfinite(score)) score = 0;
  if (score >= 1.0 && std::isfinite(s_.zExcess) && s_.excessHigh) score += 0.5 * std::max(0.0, s_.zExcess);
  if (!s_.mask.empty()) score = 0;
  const double tau = static_cast<double>(std::max<int64_t>(srttUs_, 10'000));
  const double dt = scoreLastUs_ ? static_cast<double>(x.ackUs - scoreLastUs_) : tau;
  scoreLastUs_ = x.ackUs;
  smoothedScore_ += (1.0 - std::exp(-std::max(dt, 0.0) / tau)) * (score - smoothedScore_);
  s_.score = smoothedScore_;

  // Noise statistics come only from calm, unmasked periods so that the
  // event being detected never widens its own threshold.
  if (!pre_ && !confirmed_ && s_.mask.empty()) {
    if (s_.deficitValid) calmDeficit_.add(1.0 - s_.ratio, p_.calmAlpha);
    if (s_.offeredValid) calmOffered_.add(1.0 - s_.offeredRatio, p_.calmAlpha);
    if (s_.gradientValid) calmGradient_.add(s_.residualTrend, p_.calmAlpha);
    if (std::isfinite(s_.queueDelayMs)) calmDelay_.add(s_.queueDelayMs, p_.calmAlpha);
    if (s_.gradientValid) calmResidual_.add(smoothedResidual_, p_.calmAlpha);
    if (std::isfinite(s_.excessMs) && x.phase != BbrPhase::ProbeBwUp)
      calmExcess_.add(s_.excessMs, p_.calmAlpha);
    score_.add(smoothedScore_, p_.calmAlpha);
  }
}

void FlowDetector::updateConfirmed(const AckSample& x, std::vector<Event>& events) {
  std::string reason;
  if (x.bbrBwBps > 0) {
    bbrHistory_.emplace_back(x.ackUs, x.bbrBwBps);
    while (!bbrHistory_.empty() && x.ackUs - bbrHistory_.front().first > p_.bbrDropLookbackUs)
      bbrHistory_.pop_front();
    double peak = 0;
    for (const auto& [t, bw] : bbrHistory_) peak = std::max(peak, bw);
    if (!bbrDropped_ && x.bbrBwBps < (1.0 - p_.bbrDropFraction) * peak) {
      bbrDropped_ = true;
      reason = "bbr_bw_drop";
      events.push_back({"bbr_bw_drop", x.ackUs,
          Detail().add("from_bps", peak).add("to_bps", x.bbrBwBps)
              .add("phase", std::string(phaseName(x.phase))).str()});
    } else if (bbrDropped_ && x.bbrBwBps >= (1.0 - p_.bbrDropFraction / 2) * peak) {
      bbrDropped_ = false;
    }
  }
  if (x.newlyLost) losses_.emplace_back(x.ackUs, x.newlyLost);
  const int64_t lossWindow = std::max<int64_t>(srttUs_, 50'000);
  while (!losses_.empty() && x.ackUs - losses_.front().first > lossWindow) losses_.pop_front();
  uint32_t lost = 0;
  for (const auto& [t, n] : losses_) lost += n;
  if (reason.empty() && x.newlyLost && lost >= p_.lossPackets) reason = "loss";

  if (x.bbrBwBps > 0) {
    const double queueMs = x.streamBufferBytes * 8.0 / x.bbrBwBps * 1000.0;
    if (queueMs > p_.sendQueueMs) {
      if (!sendQueueSinceUs_) sendQueueSinceUs_ = x.ackUs;
      if (reason.empty() && x.ackUs - sendQueueSinceUs_ >= std::max<int64_t>(srttUs_, 100'000) &&
          !sendQueueReported_) {
        reason = "send_queue";
        sendQueueReported_ = true;
      }
    } else {
      sendQueueSinceUs_ = 0;
      sendQueueReported_ = false;
    }
  }
  if (x.relaySaturated) reason.clear();

  if (!reason.empty()) {
    confirmLastTriggerUs_ = x.ackUs;
    if (!confirmed_) {
      confirmed_ = true;
      confirmReason_ = reason;
      events.push_back({"confirmed_on", x.ackUs,
          Detail().add("reason", reason).add("bbr_bw_bps", x.bbrBwBps)
              .add("lost_in_rtt", static_cast<int64_t>(lost))
              .add("send_queue_bytes", static_cast<int64_t>(x.streamBufferBytes))
              .add("phase", std::string(phaseName(x.phase)))
              .add("pre_active", pre_).str()});
    }
  } else if (confirmed_ && x.ackUs - confirmLastTriggerUs_ > p_.confirmHoldUs) {
    confirmed_ = false;
    events.push_back({"confirmed_off", x.ackUs, Detail().add("reason", confirmReason_).str()});
  }
  s_.confirmed = confirmed_;
}

std::string FlowDetector::evidence() const {
  std::string list = "[";
  auto add = [&](bool on, const char* name) {
    if (!on) return;
    if (list.size() > 1) list += ',';
    list += '"';
    list += name;
    list += '"';
  };
  add(s_.deficitPre, "deficit");
  add(s_.gradientPre, "gradient");
  add(s_.offeredPre, "offered");
  add(s_.excessHigh, "excess");
  add(s_.levelPre, "level");
  add(s_.backlogPre, "backlog");
  add(s_.lossPre, "loss");
  return list + "]";
}

void FlowDetector::updatePre(const AckSample& x, std::vector<Event>& events) {
  const int64_t hold = std::max<int64_t>(2 * srttUs_, 200'000);
  const double factor = s_.propagated ? p_.propagationFactor : 1.0;
  const uint32_t needed = std::max<uint32_t>(
      1, static_cast<uint32_t>(std::ceil(p_.deficitSamples * factor)));
  const int64_t persist = persistUs(factor);
  const auto held = [&](uint32_t count, int64_t sinceUs) {
    return persist ? count >= 1 && x.ackUs - sinceUs >= persist : count >= needed;
  };
  s_.deficitPre = p_.useDeficit && held(deficitCount_, deficitSinceUs_) &&
      x.ackUs - lastDeficitValidUs_ <= hold;
  s_.gradientPre = p_.useGradient && gradientRun_ >= p_.gradientPoints &&
      x.ackUs - lastGradientValidUs_ <= hold;
  s_.offeredPre = p_.useOffered && held(offeredCount_, offeredSinceUs_) &&
      x.ackUs - lastOfferedValidUs_ <= hold;
  s_.gccOveruse = p_.useGradient && gccRun_ >= p_.gradientPoints &&
      x.ackUs - lastGradientValidUs_ <= hold;
  s_.levelPre = p_.levelMs > 0 && levelSinceUs_ &&
      x.ackUs - levelSinceUs_ >= static_cast<int64_t>(p_.levelRtts * std::max<int64_t>(srttUs_, 10'000)) &&
      x.ackUs - lastFloorUs_ <= hold;
  const bool partial =
      (p_.useDeficit && deficitCount_ >= std::max<uint32_t>(1, needed / 2)) ||
      (p_.useOffered && offeredCount_ >= std::max<uint32_t>(1, needed / 2)) ||
      (p_.useGradient && std::isfinite(s_.residualTrend) && std::isfinite(s_.gamma) &&
       s_.residualTrend > 0.5 * p_.gradientScale * s_.gamma * factor);

  auto onset = [&](bool now, bool& previous, const char* name) {
    if (now && !previous && s_.mask.empty()) {
      events.push_back({name, x.ackUs,
          Detail().add("propagated", s_.propagated).add("ratio", s_.ratio)
              .add("offered_ratio", s_.offeredRatio)
              .add("residual_trend", s_.residualTrend).add("gamma", s_.gamma)
              .add("excess_ms", s_.excessMs).str()});
    }
    previous = now;
  };
  onset(s_.deficitPre, prevDeficitPre_, "deficit_onset");
  onset(s_.gradientPre, prevGradientPre_, "gradient_onset");
  onset(s_.offeredPre, prevOfferedPre_, "offered_onset");
  onset(p_.excessTrigger && s_.excessHigh && partial, prevExcessHigh_, "excess_onset");
  onset(s_.levelPre, prevLevelPre_, "level_onset");
  onset(s_.backlogPre, prevBacklogPre_, "backlog_onset");
  onset(s_.lossPre, prevLossPre_, "loss_onset");

  // While the relay flushes its backlog (drain latch), no signal may open a
  // new alarm: capacity is back and the queue is ours, being emptied.
  const bool flushing = p_.backlogRequireGrowth && backlogDraining_ && !pre_;
  const uint32_t agreeing = s_.deficitPre + s_.gradientPre + s_.offeredPre + s_.levelPre +
      s_.backlogPre + s_.lossPre + (p_.excessTrigger && s_.excessHigh && partial);
  const bool trigger = s_.mask.empty() && !flushing && (agreeing >= p_.minSignals || soloBacklog_);
  if (trigger) {
    preLastTriggerUs_ = x.ackUs;
    if (!pre_) {
      pre_ = true;
      preOnsetUs_ = x.ackUs;
      events.push_back({"pre_signal_on", x.ackUs,
          Detail().raw("evidence", evidence()).add("propagated", s_.propagated)
              .add("ratio", s_.ratio).add("deficit_count", static_cast<int64_t>(deficitCount_))
              .add("offered_ratio", s_.offeredRatio)
              .add("trend", s_.trend).add("residual_trend", s_.residualTrend)
              .add("expected_queue_ms", s_.expectedQueueMs).add("gamma", s_.gamma)
              .add("excess_ms", s_.excessMs).add("queue_delay_ms", s_.queueDelayMs)
              .add("floor_delay_ms", s_.floorDelayMs).add("backlog_ms", s_.backlogMs)
              .add("bbr_bw_bps", x.bbrBwBps).add("send_bps", x.sendBps)
              .add("ack_bps", x.ackBps).add("app_limited", x.appLimited)
              .add("phase", std::string(phaseName(x.phase)))
              .add("score", s_.score).str()});
    }
  } else if (pre_ && x.ackUs - preLastTriggerUs_ > std::max<int64_t>(p_.clearUs, 2 * srttUs_)) {
    pre_ = false;
    verified_ = false;
    events.push_back({"pre_signal_off", x.ackUs,
        Detail().add("duration_ms", (x.ackUs - preOnsetUs_) / 1000.0).str()});
  }
  if (pre_ && !verified_ && p_.verifiedMs > 0 && std::isfinite(s_.backlogMs) &&
      s_.backlogMs >= p_.verifiedMs) {
    verified_ = true;
    events.push_back({"verified_on", x.ackUs,
        Detail().add("backlog_ms", s_.backlogMs)
            .add("since_pre_ms", (x.ackUs - preOnsetUs_) / 1000.0).str()});
  }
  s_.pre = pre_;
  s_.verified = verified_;
}

GroupLayer::MemberState& GroupLayer::member(const std::string& id) {
  for (auto& [key, state] : state_)
    if (key == id) return state;
  state_.emplace_back(id, MemberState{});
  return state_.back().second;
}

double GroupLayer::memberZ(const std::string& id) const {
  for (const auto& [key, state] : state_)
    if (key == id) return state.z;
  return NAN;
}

std::vector<Event> GroupLayer::evaluate(
    int64_t nowUs,
    const std::string& source,
    bool sourcePreOnset,
    const std::vector<Member>& members) {
  std::vector<Event> events;
  int64_t maxSrtt = 0;
  for (const auto& m : members) maxSrtt = std::max(maxSrtt, m.flow->srttUs());
  if (maxSrtt <= 0) maxSrtt = 100'000;
  // Members see the same event up to one RTT apart; a lag-tolerant max over
  // that window lets their evidence line up before it is summed.
  const int64_t lag = std::min<int64_t>(
      p_.lagMaxUs, std::max<int64_t>(10'000, static_cast<int64_t>(p_.lagRtts * maxSrtt)));

  double sum = 0;
  int active = 0, preCount = 0;
  Detail zs;
  for (const auto& m : members) {
    auto& ms = member(m.id);
    if (m.id == source) {
      ms.scores.emplace_back(nowUs, m.flow->signals().score);
      while (ms.scores.size() > 1 && nowUs - ms.scores.front().first > lag) ms.scores.pop_front();
    }
    ms.z = NAN;
    if (!m.flow->warm() || ms.scores.empty() || nowUs - m.flow->lastUs() > 1'000'000) continue;
    double v = -std::numeric_limits<double>::infinity();
    for (const auto& [t, score] : ms.scores)
      if (nowUs - t <= lag) v = std::max(v, score);
    if (!std::isfinite(v)) v = ms.scores.back().second;
    const bool calm = !m.flow->pre() && !m.flow->confirmed() && !pooledOn_;
    if (ms.calm.count() >= p_.calmWarmup) ms.z = ms.calm.z(v, 0.25);
    if (m.id == source && calm) ms.calm.add(v, p_.calmAlpha);
    if (!std::isfinite(ms.z)) continue;
    sum += ms.z;
    ++active;
    preCount += m.flow->pre();
    zs.add(m.id.c_str(), ms.z);
  }
  active_ = active;
  pooled_ = active ? sum / std::sqrt(static_cast<double>(active)) : 0;

  if (active >= 2) {
    if (pooled_ > p_.poolZ) {
      pooledLastUs_ = nowUs;
      if (!pooledOn_) {
        pooledOn_ = true;
        events.push_back({"group_pooled_on", nowUs,
            Detail().add("pooled_z", pooled_).add("active", static_cast<int64_t>(active))
                .add("members_pre", static_cast<int64_t>(preCount))
                .add("lag_ms", lag / 1000.0).add("source", source)
                .raw("member_z", "{" + zs.str() + "}").str()});
      }
    } else if (pooledOn_ && nowUs - pooledLastUs_ > std::max<int64_t>(p_.clearUs, 2 * maxSrtt)) {
      pooledOn_ = false;
      events.push_back({"group_pooled_off", nowUs, Detail().add("pooled_z", pooled_).str()});
    }
  }

  if (sourcePreOnset) {
    if (!anyPre_) {
      events.push_back({"group_first_member", nowUs,
          Detail().add("member", source).add("pooled_z", pooled_).str()});
    }
    const FlowDetector* sourceFlow = nullptr;
    for (const auto& m : members)
      if (m.id == source) sourceFlow = m.flow;
    // A propagated onset does not propagate again; that would let one false
    // alarm keep the whole group sensitised indefinitely.
    if (p_.propagation && sourceFlow && !sourceFlow->signals().propagated) {
      const int64_t until = nowUs + std::max<int64_t>(
          p_.propagationMinUs, static_cast<int64_t>(p_.propagationRtts * maxSrtt));
      for (const auto& m : members) {
        if (m.id == source) continue;
        if (p_.propagationMinZ > 0) {
          const double z = memberZ(m.id);
          if (!std::isfinite(z) || z < p_.propagationMinZ) continue;
        }
        m.flow->propagateUntil(until);
      }
      events.push_back({"propagation", nowUs,
          Detail().add("from", source).add("until_mono_us", until).str()});
    }
  }
  int anyPreNow = 0;
  for (const auto& m : members) anyPreNow += m.flow->pre();
  anyPre_ = anyPreNow > 0;

  int confirmedNow = 0;
  for (const auto& m : members) confirmedNow += m.flow->confirmed();
  const bool confirm = confirmedNow >= 1 &&
      (pooled_ >= p_.poolZ / 2 || 2 * anyPreNow >= static_cast<int>(members.size()));
  if (confirm && !confirmed_) {
    confirmed_ = true;
    events.push_back({"group_confirmed_on", nowUs,
        Detail().add("pooled_z", pooled_).add("members_pre", static_cast<int64_t>(anyPreNow))
            .add("members_confirmed", static_cast<int64_t>(confirmedNow)).str()});
  } else if (confirmed_ && confirmedNow == 0) {
    confirmed_ = false;
    events.push_back({"group_confirmed_off", nowUs, Detail().add("pooled_z", pooled_).str()});
  }
  return events;
}

} // namespace openmoq::moqx::shadow
