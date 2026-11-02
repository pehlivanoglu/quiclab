// Assert-based checks of the frame model, request parsing and playback model.
#include "Common.h"
#include "Playback.h"

#include <cassert>
#include <cstdio>

int main() {
  qvideo::VideoParams p;
  p.rateKbps = 2500;
  double total = 0;
  double key = 0, other = 0;
  const uint64_t frames = 30 * 600; // 10 min
  for (uint64_t k = 0; k < frames; ++k) {
    const double s = qvideo::frameSize(p, k);
    total += s;
    (k % p.gopFrames == 0 ? key : other) += s;
  }
  const double rate = total * 8 / (frames / double(p.fps)) / 1000;
  assert(std::abs(rate - 2500) / 2500 < 0.02);
  const double ratio = (key / (frames / p.gopFrames)) / (other / (frames - frames / p.gopFrames));
  assert(ratio > 7.0 && ratio < 9.0);
  assert(qvideo::frameSize(p, 123) == qvideo::frameSize(p, 123));

  assert(qvideo::parseRequest("QV1 sub-1 2500 0"));
  assert(!qvideo::parseRequest("QV1 ../x 2500 0"));
  assert(!qvideo::parseRequest("QV1 sub 0 0"));
  assert(!qvideo::parseRequest("XX1 sub 2500 0"));

  // 33 ms frames, 100 ms buffer: frames 0..9 on time, frame 10 arrives 50 ms late.
  qvideo::Playback pb(33000, 100000);
  for (uint64_t k = 0; k < 10; ++k) {
    assert(pb.onFrame(k, k * 33000) <= 0);
  }
  assert(pb.onFrame(10, 10 * 33000 + 100000 + 50000) == 50000);
  assert(pb.stalls() == 1 && pb.stallUs() == 50000);
  assert(pb.onFrame(11, 11 * 33000 + 100000 + 50000) <= 0);
  assert(pb.stalls() == 1);
  std::puts("qvideo selftest ok");
  return 0;
}
