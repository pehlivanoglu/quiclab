#pragma once

#include <cstdint>
#include <deque>
#include <optional>
#include <vector>

namespace qvideo {

struct QueuedFrame {
  uint64_t index;
  uint64_t gop;
  bool keyframe;
  uint32_t size;
  uint64_t producedUs;
};

// Sender-side frame queue in front of QUIC, bounded in media time with
// GOP-aware head drop: a frame older than the limit is dropped together with
// the rest of its GOP (later P-frames would not decode), including frames of
// that GOP still to be produced; sending resumes at the next keyframe.
// A limit of 0 never drops.
class SendQueue {
 public:
  explicit SendQueue(uint64_t limitUs) : limitUs_(limitUs) {}

  void push(const QueuedFrame& f, std::vector<QueuedFrame>& dropped) {
    if (skippingGop_ && f.gop == *skippingGop_) {
      dropped.push_back(f);
      return;
    }
    skippingGop_.reset();
    frames_.push_back(f);
    bytes_ += f.size;
  }

  void dropStale(uint64_t nowUs, std::vector<QueuedFrame>& dropped) {
    while (limitUs_ && !frames_.empty() && nowUs - frames_.front().producedUs > limitUs_) {
      const uint64_t gop = frames_.front().gop;
      skippingGop_ = gop;
      // FIFO in frame order: the stale GOP's queued frames sit at the head.
      while (!frames_.empty() && frames_.front().gop == gop) {
        dropped.push_back(frames_.front());
        pop();
      }
    }
  }

  bool empty() const { return frames_.empty(); }
  const QueuedFrame& front() const { return frames_.front(); }
  void pop() {
    bytes_ -= frames_.front().size;
    frames_.pop_front();
  }
  uint64_t bytes() const { return bytes_; }
  uint64_t oldestAgeUs(uint64_t nowUs) const {
    return frames_.empty() || nowUs < frames_.front().producedUs ? 0 : nowUs - frames_.front().producedUs;
  }

 private:
  uint64_t limitUs_;
  std::deque<QueuedFrame> frames_;
  uint64_t bytes_{0};
  std::optional<uint64_t> skippingGop_;
};

}  // namespace qvideo
