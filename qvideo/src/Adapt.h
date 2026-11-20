#pragma once

// K5-sender: simple CC-driven rate adaptation (off by default; user decision 2026-11-17).
// target = x * estimate (BBR: its bandwidth estimate; Copa: cwnd / srtt). The video's rate is
// min(nominal, target), never below floor * nominal, applied by scaling every frame produced from the
// next frame on (an ideal encoder). Not an ABR; neither the detector nor the grouping feeds it.
// x = 0.85 (P) and floor = 0.3 (P) come from reports/adapt-whatif-2026-11-17; no recovery rule.

#include <algorithm>
#include <cmath>
#include <cstdint>

namespace qvideo {

// The congestion controller's sending-rate estimate in bit/s; 0 when there is none yet.
inline double ccEstimateBps(bool copa, uint64_t bwBps, uint64_t cwndBytes, uint64_t srttUs) {
  if (!copa && bwBps > 0) {
    return double(bwBps);
  }
  return srttUs > 0 ? double(cwndBytes) * 8.0 * 1e6 / double(srttUs) : 0.0;
}

class RateAdapter {
 public:
  RateAdapter(double x, double floor, double nominalBps)
      : x_(x), floor_(std::clamp(floor, 0.0, 1.0)), nominal_(nominalBps) {}

  bool enabled() const { return x_ > 0 && nominal_ > 0; }

  // A new estimate; returns the scale in force from the next frame. No estimate (<= 0): unchanged.
  double update(double estimateBps) {
    if (!enabled() || estimateBps <= 0) {
      return scale_;
    }
    target_ = x_ * estimateBps;
    scale_ = std::clamp(target_ / nominal_, floor_, 1.0);
    return scale_;
  }

  uint32_t apply(uint32_t size, uint32_t minSize) const {
    if (!enabled()) {
      return size;
    }
    return std::max<uint32_t>(minSize, uint32_t(std::lround(double(size) * scale_)));
  }

  double scale() const { return scale_; }
  double target() const { return target_; }

 private:
  double x_;
  double floor_;
  double nominal_;
  double scale_ = 1.0;
  double target_ = 0.0;
};

}  // namespace qvideo
