// qtraffic: PPBP cross traffic over UDP (see Ppbp.h).
//
//   send: precomputes every burst from the seed (written to <out>-bursts.csv,
//         the offered-load truth), waits for --start_unix_us, then paces
//         packets at the aggregate rate of the active bursts.
//   recv: sink; per 100 ms writes packets, bytes, sequence gaps (loss) and
//         one-way delay (sender and receiver share one kernel clock).

#include "Common.h"
#include "Ppbp.h"

#include <gflags/gflags.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <algorithm>
#include <cerrno>
#include <csignal>
#include <cstdio>
#include <fstream>
#include <iostream>

DEFINE_string(mode, "", "send or recv");
DEFINE_string(bind, "0.0.0.0", "local address");
DEFINE_string(dest, "", "receiver address (send)");
DEFINE_int32(port, 5300, "receiver UDP port");
DEFINE_uint64(start_unix_us, 0, "send: CLOCK_REALTIME start; 0 = now");
DEFINE_double(duration_s, 10, "send: length of the process");
DEFINE_double(mean_mbps, 0, "send: long-run offered load");
DEFINE_double(burst_mbps, 0, "send: rate of one active burst");
DEFINE_double(mean_burst_s, 0.5, "send: mean burst duration");
DEFINE_double(hurst, 0.8, "send: Hurst parameter, 0.5 < H < 1");
DEFINE_uint64(seed, 1, "send: burst process seed");
DEFINE_int32(packet_size, 1200, "send: UDP payload bytes");
DEFINE_string(out, "", "CSV path prefix");

namespace {

constexpr uint64_t kBinUs = 100000;
constexpr uint64_t kTickUs = 1000;

#pragma pack(push, 1)
struct Header {
  uint64_t seq;
  uint64_t sendUs;
};
#pragma pack(pop)

volatile std::sig_atomic_t stopRequested = 0;

void sleepUntil(uint64_t unixUs) {
  timespec ts{time_t(unixUs / 1000000), long(unixUs % 1000000) * 1000};
  while (clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &ts, nullptr) == EINTR && !stopRequested) {
  }
}

sockaddr_in address(const std::string& ip, int port) {
  sockaddr_in a{};
  a.sin_family = AF_INET;
  a.sin_port = htons(uint16_t(port));
  if (inet_pton(AF_INET, ip.c_str(), &a.sin_addr) != 1) {
    std::cerr << "invalid IPv4 address " << ip << "\n";
    std::exit(2);
  }
  return a;
}

int udpSocket(const std::string& bindIp, int bindPort) {
  int fd = socket(AF_INET, SOCK_DGRAM, 0);
  int buf = 8 << 20;
  setsockopt(fd, SOL_SOCKET, SO_SNDBUF, &buf, sizeof(buf));
  setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &buf, sizeof(buf));
  sockaddr_in a = address(bindIp, bindPort);
  if (bind(fd, reinterpret_cast<sockaddr*>(&a), sizeof(a)) != 0) {
    std::perror("bind");
    std::exit(1);
  }
  return fd;
}

int runSend() {
  const qvideo::PpbpParams params{FLAGS_mean_mbps, FLAGS_burst_mbps, FLAGS_mean_burst_s,
                                  FLAGS_hurst, FLAGS_duration_s, FLAGS_seed};
  const auto bursts = qvideo::ppbpBursts(params);
  {
    std::ofstream out(FLAGS_out + "-bursts.csv");
    out << "burst,start_s,duration_s,rate_mbps\n";
    for (size_t i = 0; i < bursts.size(); ++i) {
      out << i << ',' << bursts[i].startS << ',' << bursts[i].durationS << ',' << FLAGS_burst_mbps << '\n';
    }
  }
  // Offered rate as a step function: +1 active burst at a start, -1 at an end.
  std::vector<std::pair<uint64_t, int>> steps;
  for (const auto& b : bursts) {
    steps.emplace_back(uint64_t(b.startS * 1e6), 1);
    steps.emplace_back(uint64_t((b.startS + b.durationS) * 1e6), -1);
  }
  std::sort(steps.begin(), steps.end());

  int fd = udpSocket(FLAGS_bind, 0);
  sockaddr_in dest = address(FLAGS_dest, FLAGS_port);
  if (connect(fd, reinterpret_cast<sockaddr*>(&dest), sizeof(dest)) != 0) {
    std::perror("connect");
    return 1;
  }
  std::vector<char> packet(size_t(FLAGS_packet_size), 0);
  std::ofstream sent(FLAGS_out + "-sent.csv");
  sent << "t_us,active_bursts,offered_mbps,sent_bytes,send_errors\n";

  const uint64_t start = FLAGS_start_unix_us ? FLAGS_start_unix_us : qvideo::nowUs();
  const uint64_t end = start + uint64_t(FLAGS_duration_s * 1e6);
  sleepUntil(start);
  size_t next = 0;
  int active = 0;
  double credit = 0;
  uint64_t seq = 0, binBytes = 0, binErrors = 0, binStart = start, last = start;
  for (uint64_t tick = start; tick < end && !stopRequested; tick += kTickUs) {
    sleepUntil(tick);
    const uint64_t now = qvideo::nowUs();
    while (next < steps.size() && start + steps[next].first <= now) {
      active += steps[next++].second;
    }
    const double rateBps = active * FLAGS_burst_mbps * 1e6;
    // Credit at most 10 ms behind: a late tick catches up, a stall does not flood.
    credit = std::min(credit + rateBps / 8 * double(now - last) / 1e6, rateBps / 8 * 0.01 + FLAGS_packet_size);
    last = now;
    while (credit >= FLAGS_packet_size) {
      Header h{seq++, qvideo::nowUs()};
      std::memcpy(packet.data(), &h, sizeof(h));
      if (send(fd, packet.data(), packet.size(), 0) < 0) {
        ++binErrors;
      } else {
        binBytes += packet.size();
      }
      credit -= FLAGS_packet_size;
    }
    if (now - binStart >= kBinUs) {
      sent << now << ',' << active << ',' << active * FLAGS_burst_mbps << ',' << binBytes << ','
           << binErrors << '\n';
      binStart = now;
      binBytes = binErrors = 0;
    }
  }
  return 0;
}

int runRecv() {
  int fd = udpSocket(FLAGS_bind, FLAGS_port);
  timeval timeout{0, 100000};
  setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
  std::ofstream out(FLAGS_out + "-recv.csv");
  out << "t_us,packets,bytes,lost,owd_mean_us,owd_max_us\n";
  std::vector<char> buf(65536);
  uint64_t expected = 0, packets = 0, bytes = 0, lost = 0, owdSum = 0, owdMax = 0;
  uint64_t binStart = qvideo::nowUs();
  while (!stopRequested) {
    const ssize_t n = recv(fd, buf.data(), buf.size(), 0);
    const uint64_t now = qvideo::nowUs();
    if (n >= ssize_t(sizeof(Header))) {
      Header h;
      std::memcpy(&h, buf.data(), sizeof(h));
      if (h.seq > expected) {
        lost += h.seq - expected;  // reordering would count as loss; netem without jitter keeps order
      }
      expected = std::max(expected, h.seq + 1);
      const uint64_t owd = now > h.sendUs ? now - h.sendUs : 0;
      ++packets;
      bytes += uint64_t(n);
      owdSum += owd;
      owdMax = std::max(owdMax, owd);
    }
    if (now - binStart >= kBinUs) {
      out << now << ',' << packets << ',' << bytes << ',' << lost << ','
          << (packets ? owdSum / packets : 0) << ',' << owdMax << '\n';
      out.flush();
      binStart = now;
      packets = bytes = lost = owdSum = owdMax = 0;
    }
  }
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  gflags::ParseCommandLineFlags(&argc, &argv, true);
  std::signal(SIGTERM, [](int) { stopRequested = 1; });
  std::signal(SIGINT, [](int) { stopRequested = 1; });
  if (FLAGS_out.empty() || FLAGS_port <= 0) {
    std::cerr << "need --out and a positive --port\n";
    return 2;
  }
  if (FLAGS_mode == "recv") {
    return runRecv();
  }
  if (FLAGS_mode != "send" || FLAGS_dest.empty() || FLAGS_mean_mbps <= 0 || FLAGS_burst_mbps <= 0 ||
      FLAGS_mean_burst_s <= 0 || FLAGS_hurst <= 0.5 || FLAGS_hurst >= 1 || FLAGS_duration_s <= 0 ||
      FLAGS_packet_size < int(sizeof(Header)) || FLAGS_packet_size > 1472) {
    std::cerr << "send needs --dest and valid --mean_mbps/--burst_mbps/--mean_burst_s/"
                 "--hurst (0.5..1)/--duration_s/--packet_size\n";
    return 2;
  }
  return runSend();
}
