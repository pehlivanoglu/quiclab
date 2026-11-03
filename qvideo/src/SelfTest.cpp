// Assert-based checks of the frame model, request parsing and playback model.
#include "Common.h"
#include "Playback.h"
#include "Ppbp.h"
#include "SendQueue.h"

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
  assert(qvideo::parseRequest("QV1 sub-1 2500 0 123456")->recvBasisUs == 123456);
  assert(!qvideo::parseRequest("QV1 sub-1 2500 0 -5"));
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
  // Stream starts at 10 s, phase 0.5 s, 30 fps, keyframe every 60 frames.
  const qvideo::Schedule sched{10'000'000, 500'000, 30, 60};
  assert(sched.timeUs(0) == 10'500'000 && sched.timeUs(60) == 12'500'000);
  assert(sched.firstFrame(9'000'000) == 0);   // connected before the start
  assert(sched.firstFrame(10'500'000) == 0);  // exactly at frame 0
  assert(sched.firstFrame(11'000'000) == 60); // mid-GOP: next keyframe
  assert(sched.firstFrame(12'500'001) == 120);
  // PPBP: long-run offered load converges to the mean; a seed fixes the bursts.
  const qvideo::PpbpParams pp{20.0, 2.0, 0.5, 0.7, 5000.0, 7};
  const auto bursts = qvideo::ppbpBursts(pp);
  double busy = 0;
  for (const auto& b : bursts) {
    assert(b.startS >= 0 && b.durationS > 0 && b.startS + b.durationS <= pp.durationS + 1e-9);
    busy += b.durationS;
  }
  const double load = busy * pp.burstMbps / pp.durationS;
  assert(std::abs(load - pp.meanMbps) / pp.meanMbps < 0.1);
  const auto again = qvideo::ppbpBursts(pp);
  assert(again.size() == bursts.size() && again.back().startS == bursts.back().startS);
  // Send queue: 30 frames per GOP, 1 s limit. GOP 0 waits too long.
  {
    qvideo::SendQueue q(1'000'000);
    std::vector<qvideo::QueuedFrame> dropped;
    for (uint64_t k = 0; k < 40; ++k) {
      q.push({k, k / 30, k % 30 == 0, 1000, k * 33'333}, dropped);
    }
    assert(dropped.empty() && q.bytes() == 40'000);
    q.dropStale(1'100'000, dropped);  // frame 0 is 1.1 s old: all of GOP 0 goes
    assert(dropped.size() == 30 && q.front().index == 30 && q.front().keyframe);
    dropped.clear();
    q.dropStale(1'200'000, dropped);  // frame 30 is only 0.2 s old
    assert(dropped.empty() && q.bytes() == 10'000);
    // A drop in the middle of GOP 1 also drops its later frames as they are produced.
    q.dropStale(2'200'000, dropped);
    assert(dropped.size() == 10 && q.empty());
    dropped.clear();
    q.push({40, 1, false, 1000, 2'300'000}, dropped);
    assert(dropped.size() == 1 && q.empty());
    q.push({60, 2, true, 1000, 2'400'000}, dropped);
    assert(!q.empty() && q.front().index == 60);
    qvideo::SendQueue unlimited(0);
    unlimited.push({0, 0, true, 1000, 0}, dropped);
    unlimited.dropStale(100'000'000, dropped);
    assert(!unlimited.empty());
  }

  // Playback after a sender skip: frames 5..9 were dropped, keyframe 10 says so.
  {
    qvideo::Playback skip(33000, 100000);
    for (uint64_t k = 0; k < 5; ++k) {
      skip.onFrame(k, k * 33000);
    }
    skip.onFrame(10, 10 * 33000, 5);
    assert(skip.skipped() == 5 && skip.stalls() == 0);
    assert(skip.bufferUs(10 * 33000) > 0);  // contiguous through the skip
  }
  // Reordering across GOP streams is not a skip: keyframe 10 first, then 8, 9.
  {
    qvideo::Playback reorder(33000, 100000);
    for (uint64_t k = 0; k < 8; ++k) {
      reorder.onFrame(k, k * 33000);
    }
    reorder.onFrame(10, 8 * 33000);
    reorder.onFrame(8, 9 * 33000);
    reorder.onFrame(9, 9 * 33000);
    assert(reorder.skipped() == 0 && reorder.stalls() == 0);
  }
  std::puts("qvideo selftest ok");
  return 0;
}
