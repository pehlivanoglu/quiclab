#pragma once

#include <algorithm>
#include <cstdint>
#include <set>

namespace qvideo {

// Playback model: the first received frame k0 arriving at a0 plays at
// a0 + buffer; frame k plays one frame interval after k-1. A frame that arrives
// after its play time stalls playback until it arrives (the schedule shifts by
// the stall), as a live player without frame skipping would.
class Playback {
 public:
  explicit Playback(uint64_t frameUs, uint64_t bufferUs) : frameUs_(frameUs), bufferUs_(bufferUs) {}

  // Returns lateness vs. the current schedule (>0: this frame stalled playback).
  int64_t onFrame(uint64_t index, uint64_t arrivalUs) {
    if (!started_) {
      started_ = true;
      k0_ = index;
      play0Us_ = arrivalUs + bufferUs_;
      contiguous_ = index;
    } else if (index < k0_) {
      return 0; // older than the first played frame: never played
    } else {
      pending_.insert(index);
      while (pending_.count(contiguous_ + 1)) {
        pending_.erase(++contiguous_);
      }
    }
    const int64_t late = int64_t(arrivalUs) - int64_t(playUs(index));
    if (late > 0) {
      if (!stalled_) {
        ++stalls_;
      }
      stalled_ = true;
      stallUs_ += uint64_t(late);
      play0Us_ += uint64_t(late);
    } else if (index == contiguous_) {
      stalled_ = false;
    }
    return late;
  }

  // shortcut: reorder across GOP streams is credited at arrival, not at play
  // time; fine while GOP streams finish in order, revisit for frame skipping.
  int64_t bufferUs(uint64_t nowUs) const {
    return started_ ? std::max<int64_t>(0, int64_t(playUs(contiguous_) + frameUs_) - int64_t(nowUs))
                    : 0;
  }

  bool started() const { return started_; }
  uint64_t stalls() const { return stalls_; }
  uint64_t stallUs() const { return stallUs_; }

 private:
  uint64_t playUs(uint64_t index) const { return play0Us_ + (index - k0_) * frameUs_; }

  uint64_t frameUs_;
  uint64_t bufferUs_;
  bool started_{false};
  bool stalled_{false};
  uint64_t k0_{0};
  uint64_t play0Us_{0};
  uint64_t contiguous_{0};
  std::set<uint64_t> pending_;
  uint64_t stalls_{0};
  uint64_t stallUs_{0};
};

} // namespace qvideo

