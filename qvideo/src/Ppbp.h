#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <random>
#include <vector>

namespace qvideo {

// Poisson Pareto Burst Process (as in FlowBot's ns-3 cross traffic): bursts
// start as a Poisson process, last Pareto-distributed times, and each sends at
// a constant rate while active. The aggregate is long-range dependent with
// Hurst parameter H, from the Pareto shape alpha = 3 - 2H (1 < alpha < 2).
struct PpbpParams {
  double meanMbps{0};     // long-run offered load
  double burstMbps{0};    // rate of one active burst
  double meanBurstS{0};   // mean burst duration
  double hurst{0.8};      // 0.5 < H < 1
  double durationS{0};    // bursts start in [0, durationS) and are cut there
  uint64_t seed{1};
};

struct Burst {
  double startS;
  double durationS;  // after cutting at durationS
};

inline std::vector<Burst> ppbpBursts(const PpbpParams& p) {
  const double alpha = 3.0 - 2.0 * p.hurst;
  const double scale = p.meanBurstS * (alpha - 1.0) / alpha;  // Pareto x_m for the given mean
  const double lambda = p.meanMbps / (p.burstMbps * p.meanBurstS);
  std::mt19937_64 rng(p.seed);
  std::exponential_distribution<double> gap(lambda);
  std::uniform_real_distribution<double> unit(0.0, 1.0);
  std::vector<Burst> bursts;
  // Start ten mean burst lengths before 0 so bursts are already active at t=0.
  for (double t = -p.meanBurstS * 10 + gap(rng); t < p.durationS; t += gap(rng)) {
    const double length = scale / std::pow(1.0 - unit(rng), 1.0 / alpha);
    const double begin = std::max(0.0, t);
    const double end = std::min(p.durationS, t + length);
    if (end > begin) {
      bursts.push_back({begin, end - begin});
    }
  }
  return bursts;
}

}  // namespace qvideo
