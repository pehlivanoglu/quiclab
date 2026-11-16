#pragma once

// Departure processes of qtraffic (suite v3 background and stimuli). Pure:
// no sockets and no clocks, so `qtraffic --mode=plan` can write exactly the
// departures a send run would emit (tests/unit/test_qtraffic_v3.py).
//
//   RateSteps      aggregate offered rate (UDP payload Mb/s) as a step function
//                  of time since the process start, built from a burst schedule
//                  (overlapping bursts add up).
//   PoissonSource  n flows; flow i carries share w_i / sum(w) of the aggregate
//                  rate as its own non-homogeneous Poisson process of full-size
//                  packets (thinning against the peak rate, one RNG stream per
//                  flow), so departures are independent of any frame clock.
//   AsvSource      aggregate synchronized video: the frame-size pattern of one
//                  qvideo rendition (Common.h frameSize, same seed), frames on
//                  the shared live grid (stream start + k / fps, phase 0), each
//                  frame scaled by rate(GOP start) / ref rate and spread evenly
//                  over the measured emission time of a keyframe or a P-frame.

#include "Common.h"
#include "Ppbp.h"

#include <cmath>
#include <cstdint>
#include <optional>
#include <queue>
#include <random>
#include <vector>

namespace qvideo {

struct Departure {
  uint64_t tUs;    // since the process start
  uint32_t flow;   // index into the flow list (one socket each)
  uint32_t bytes;  // UDP payload
};

class RateSteps {
 public:
  explicit RateSteps(const std::vector<Burst>& bursts) {
    std::vector<std::pair<uint64_t, double>> edges;
    for (const auto& b : bursts) {
      edges.emplace_back(uint64_t(std::llround(b.startS * 1e6)), b.rateMbps);
      edges.emplace_back(uint64_t(std::llround((b.startS + b.durationS) * 1e6)), -b.rateMbps);
    }
    std::sort(edges.begin(), edges.end());
    double r = 0;
    for (const auto& [t, d] : edges) {
      r = std::max(0.0, r + d);
      if (!t_.empty() && t_.back() == t) {
        rate_.back() = r;
      } else {
        t_.push_back(t);
        rate_.push_back(r);
      }
      peak_ = std::max(peak_, r);
    }
  }

  double peakMbps() const { return peak_; }

  // Rate in force at t (0 before the first edge); `hint` speeds up monotone queries.
  double at(uint64_t t, size_t& hint) const {
    while (hint < t_.size() && t_[hint] <= t) {
      ++hint;
    }
    return hint == 0 ? 0.0 : rate_[hint - 1];
  }

  // First edge time > t after which the rate is positive; nullopt if none.
  std::optional<uint64_t> nextPositive(uint64_t t, size_t hint) const {
    for (size_t i = hint; i < t_.size(); ++i) {
      if (t_[i] > t && rate_[i] > 0) {
        return t_[i];
      }
    }
    return std::nullopt;
  }

 private:
  std::vector<uint64_t> t_;
  std::vector<double> rate_;
  double peak_{0};
};

class PoissonSource {
 public:
  PoissonSource(const RateSteps& steps, std::vector<double> weights, uint32_t packetBytes,
                uint64_t durationUs, uint64_t seed)
      : steps_(steps), packet_(packetBytes), end_(durationUs) {
    double sum = 0;
    for (double w : weights) {
      sum += w;
    }
    for (size_t i = 0; i < weights.size(); ++i) {
      Flow f;
      f.share = weights[i] / sum;
      // Peak packet rate of this flow, per microsecond.
      f.lambdaMax = steps_.peakMbps() * f.share * 1e6 / 8.0 / packetBytes / 1e6;
      f.rng.seed(splitmix64(seed * 0x100000001b3ULL + i + 1));
      flows_.push_back(std::move(f));
    }
    for (uint32_t i = 0; i < flows_.size(); ++i) {
      advance(i, 0);
    }
  }

  std::optional<Departure> next() {
    if (heap_.empty()) {
      return std::nullopt;
    }
    const auto [t, i] = heap_.top();
    heap_.pop();
    advance(i, t);
    return Departure{t, i, packet_};
  }

  size_t flows() const { return flows_.size(); }

 private:
  struct Flow {
    double share{0};
    double lambdaMax{0};
    size_t hint{0};
    std::mt19937_64 rng;
  };

  // Next accepted departure of flow i after t (thinning; restart at the next positive-rate edge).
  void advance(uint32_t i, uint64_t t) {
    Flow& f = flows_[i];
    if (f.lambdaMax <= 0) {
      return;
    }
    std::exponential_distribution<double> gap(f.lambdaMax);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    double x = double(t);
    while (true) {
      x += gap(f.rng);
      if (x >= double(end_)) {
        return;
      }
      const uint64_t ti = uint64_t(x);
      const double r = steps_.at(ti, f.hint);
      if (r <= 0) {
        const auto restart = steps_.nextPositive(ti, f.hint);
        if (!restart || *restart >= end_) {
          return;
        }
        x = double(*restart);  // memoryless: draw the next gap from the edge
        continue;
      }
      if (unit(f.rng) * steps_.peakMbps() <= r) {
        heap_.push({ti, i});
        return;
      }
    }
  }

  const RateSteps& steps_;
  uint32_t packet_;
  uint64_t end_;
  std::vector<Flow> flows_;
  std::priority_queue<std::pair<uint64_t, uint32_t>, std::vector<std::pair<uint64_t, uint32_t>>,
                      std::greater<>> heap_;
};

struct AsvParams {
  VideoParams video;          // rendition rate, fps, GOP frames, I/P ratio, sigma, seed
  double refMbps{5.0};        // payload rate the pattern is scaled from (the rendition rate)
  uint64_t streamStartUs{0};  // shared stream T0 (CLOCK_REALTIME)
  uint64_t startUs{0};        // this process's start (CLOCK_REALTIME)
  uint64_t keySpreadUs{0};    // emission time of a keyframe
  uint64_t pSpreadUs{0};      // emission time of a P-frame
};

class AsvSource {
 public:
  AsvSource(const RateSteps& steps, const AsvParams& p, uint32_t packetBytes, uint64_t durationUs)
      : steps_(steps), p_(p), packet_(packetBytes), end_(durationUs) {
    const Schedule s{p.streamStartUs, 0, p.video.fps, p.video.gopFrames};
    k_ = p.startUs <= s.timeUs(0) ? 0 : uint64_t(double(p.startUs - p.streamStartUs) * p.video.fps / 1e6);
    while (s.timeUs(k_) < p.startUs) {
      ++k_;
    }
    loadFrame();
  }

  std::optional<Departure> next() {
    while (j_ >= n_) {
      ++k_;
      if (!loadFrame()) {
        return std::nullopt;
      }
    }
    const uint64_t t = frameT_ + (n_ > 1 ? spread_ * j_ / n_ : 0);
    const uint32_t bytes = j_ + 1 < n_ ? packet_ : last_;
    ++j_;
    return Departure{t, 0, bytes};
  }

  // Scale of the current GOP (rate / ref), for the log.
  double scale() const { return scale_; }

 private:
  // Frame k_: returns false past the end; frames of a GOP at rate 0 get no packets.
  bool loadFrame() {
    const Schedule s{p_.streamStartUs, 0, p_.video.fps, p_.video.gopFrames};
    const uint64_t abs = s.timeUs(k_);
    if (abs < p_.startUs || abs - p_.startUs >= end_) {
      return false;
    }
    frameT_ = abs - p_.startUs;
    const uint64_t gop = k_ - k_ % p_.video.gopFrames;
    const uint64_t gopAbs = s.timeUs(gop);
    const uint64_t gopRel = gopAbs > p_.startUs ? gopAbs - p_.startUs : 0;
    scale_ = steps_.at(gopRel, hint_) / p_.refMbps;
    const double bytes = double(frameSize(p_.video, k_)) * scale_;
    const bool key = k_ % p_.video.gopFrames == 0;
    spread_ = key ? p_.keySpreadUs : p_.pSpreadUs;
    j_ = 0;
    n_ = bytes < 1 ? 0 : uint32_t(std::ceil(bytes / packet_));
    // The last packet carries the remainder (at least 64 B: qtraffic's header must fit).
    last_ = n_ ? uint32_t(std::max(64.0, bytes - double(n_ - 1) * packet_)) : 0;
    return true;
  }

  const RateSteps& steps_;
  AsvParams p_;
  uint32_t packet_;
  uint64_t end_;
  uint64_t k_{0};
  uint64_t frameT_{0};
  uint64_t spread_{0};
  uint32_t j_{0}, n_{0}, last_{0};
  double scale_{0};
  size_t hint_{0};
};

}  // namespace qvideo
