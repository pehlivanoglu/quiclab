#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <ctime>
#include <fstream>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

namespace qvideo {

inline constexpr const char* kAlpn = "qvideo";
inline constexpr uint32_t kMagic = 0x31465651; // "QVF1"

// Every QUIC endpoint shares one kernel (Mininet netns), so CLOCK_REALTIME
// timestamps from the sender are directly comparable at the client (exact OWD).
inline uint64_t nowUs() {
  timespec ts{};
  clock_gettime(CLOCK_REALTIME, &ts);
  return uint64_t(ts.tv_sec) * 1000000 + uint64_t(ts.tv_nsec) / 1000;
}

#pragma pack(push, 1)
struct FrameHeader {
  uint32_t magic{kMagic};
  uint8_t keyframe{0};
  uint8_t pad[3]{};
  uint64_t index{0};   // live frame index: floor((t - phase) / frame interval)
  uint64_t sendUs{0};  // CLOCK_REALTIME when the frame was handed to QUIC
  uint32_t size{0};    // total bytes including this header
  uint32_t rateKbps{0};
};
#pragma pack(pop)
static_assert(sizeof(FrameHeader) == 32);

struct VideoParams {
  uint32_t rateKbps{0};
  uint32_t fps{30};
  uint32_t gopFrames{60};
  double ipRatio{8.0};   // mean I-frame size / mean P-frame size
  double sizeSigma{0.2}; // lognormal sigma of per-frame size noise
  uint64_t seed{1};
};

inline uint64_t splitmix64(uint64_t x) {
  x += 0x9e3779b97f4a7c15ULL;
  x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
  x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
  return x ^ (x >> 31);
}

// Deterministic in (seed, rate, index): every client of one rendition sees the
// same "live encoder" output, and reruns reproduce it exactly.
inline uint32_t frameSize(const VideoParams& p, uint64_t index) {
  const bool key = index % p.gopFrames == 0;
  const double gopBytes = double(p.rateKbps) * 1000.0 / 8.0 * p.gopFrames / p.fps;
  const double pMean = gopBytes / (p.ipRatio + p.gopFrames - 1);
  const double mean = key ? p.ipRatio * pMean : pMean;
  const uint64_t h = splitmix64(p.seed ^ splitmix64(index) ^ (uint64_t(p.rateKbps) << 40));
  const double u1 = (double(h >> 11) + 1.0) / 9007199254740993.0; // (0, 1]
  const double u2 = double(splitmix64(h) >> 11) / 9007199254740992.0;
  const double z = std::sqrt(-2.0 * std::log(u1)) * std::cos(2.0 * M_PI * u2);
  const double scale = std::exp(p.sizeSigma * z - p.sizeSigma * p.sizeSigma / 2.0);
  return std::max<uint32_t>(sizeof(FrameHeader), uint32_t(std::lround(mean * scale)));
}

// Live schedule anchored at the stream start shared by every client of a run:
// frame k is due at startUs + phaseUs + k / fps, keyframes at k % gopFrames == 0.
struct Schedule {
  uint64_t startUs{0};
  uint64_t phaseUs{0};
  uint32_t fps{30};
  uint32_t gopFrames{60};

  uint64_t timeUs(uint64_t k) const {
    return startUs + phaseUs + uint64_t(std::ceil(double(k) * 1e6 / fps));
  }

  // A viewer that arrives before the stream starts gets frame 0; a later one
  // tunes in at the next keyframe.
  uint64_t firstFrame(uint64_t nowUs) const {
    if (nowUs <= timeUs(0)) {
      return 0;
    }
    uint64_t k = uint64_t(double(nowUs - startUs - phaseUs) * fps / 1e6) + 1;
    return k + (gopFrames - k % gopFrames) % gopFrames;
  }
};

inline std::vector<uint32_t> parseList(const std::string& csv) {
  std::vector<uint32_t> out;
  std::stringstream ss(csv);
  std::string item;
  while (std::getline(ss, item, ',')) {
    if (!item.empty()) {
      out.push_back(uint32_t(std::stoul(item)));
    }
  }
  return out;
}

// Request line the client sends on its bidi stream:
// "QV1 <client-id> <rate_kbps> <phase_ms>\n"
struct Request {
  std::string clientId;
  uint32_t rateKbps{0};
  uint32_t phaseMs{0};
};

inline bool validClientId(const std::string& id) {
  if (id.empty() || id.size() > 63) {
    return false;
  }
  return std::all_of(id.begin(), id.end(), [](char c) {
    return std::isalnum(static_cast<unsigned char>(c)) || c == '-' || c == '_';
  });
}

inline std::optional<Request> parseRequest(const std::string& line) {
  std::istringstream in(line);
  std::string magic;
  Request r;
  long long rate = -1, phase = -1;
  if (!(in >> magic >> r.clientId >> rate >> phase) || magic != "QV1" ||
      !validClientId(r.clientId) || rate <= 0 || rate > 1000000 || phase < 0 ||
      phase > 600000) {
    return std::nullopt;
  }
  r.rateKbps = uint32_t(rate);
  r.phaseMs = uint32_t(phase);
  return r;
}

} // namespace qvideo
