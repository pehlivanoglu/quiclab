// qtraffic: PPBP cross traffic over UDP (see Ppbp.h), or a fixed burst schedule.
//
//   send: precomputes every burst, from the seed or from --schedule (written to
//         <out>-bursts.csv, the offered-load truth), waits for --start_unix_us,
//         then paces packets at the aggregate rate of the active bursts.
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
#include <sstream>

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
DEFINE_string(schedule, "", "send: fixed bursts start_s:duration_s:rate_mbps,... instead of PPBP");

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

// "start:duration:rate,..." -> bursts; empty on any malformed or non-positive entry.
std::vector<qvideo::Burst> parseSchedule(const std::string& text) {
  std::vector<qvideo::Burst> bursts;
  std::istringstream in(text);
  std::string item;
  while (std::getline(in, item, ',')) {
    qvideo::Burst b{};
    char c1 = 0, c2 = 0;
    std::istringstream fields(item);
    if (!(fields >> b.startS >> c1 >> b.durationS >> c2 >> b.rateMbps) || c1 != ':' || c2 != ':' ||
        b.startS < 0 || b.durationS <= 0 || b.rateMbps <= 0) {
      return {};
    }
    bursts.push_back(b);
  }
  return bursts;
}

int runSend() {
  const auto bursts = FLAGS_schedule.empty()
      ? qvideo::ppbpBursts({FLAGS_mean_mbps, FLAGS_burst_mbps, FLAGS_mean_burst_s, FLAGS_hurst,
                            FLAGS_duration_s, FLAGS_seed})
      : parseSchedule(FLAGS_schedule);
  {
    std::ofstream out(FLAGS_out + "-bursts.csv");
    out << "burst,start_s,duration_s,rate_mbps\n";
    for (size_t i = 0; i < bursts.size(); ++i) {
      out << i << ',' << bursts[i].startS << ',' << bursts[i].durationS << ',' << bursts[i].rateMbps << '\n';
    }
  }
  // Offered rate as a step function: + a burst's rate at its start, - at its end.
  std::vector<std::pair<uint64_t, double>> steps;
  for (const auto& b : bursts) {
    steps.emplace_back(uint64_t(b.startS * 1e6), b.rateMbps);
    steps.emplace_back(uint64_t((b.startS + b.durationS) * 1e6), -b.rateMbps);
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
  double offeredMbps = 0;
  double credit = 0;
  uint64_t seq = 0, binBytes = 0, binErrors = 0, binStart = start, last = start;
  for (uint64_t tick = start; tick < end && !stopRequested; tick += kTickUs) {
    sleepUntil(tick);
    const uint64_t now = qvideo::nowUs();
    while (next < steps.size() && start + steps[next].first <= now) {
      active += steps[next].second > 0 ? 1 : -1;
      offeredMbps = std::max(0.0, offeredMbps + steps[next++].second);
    }
    const double rateBps = offeredMbps * 1e6;
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
      sent << now << ',' << active << ',' << offeredMbps << ',' << binBytes << ','
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
  const bool ppbpOk = FLAGS_mean_mbps > 0 && FLAGS_burst_mbps > 0 && FLAGS_mean_burst_s > 0 &&
                      FLAGS_hurst > 0.5 && FLAGS_hurst < 1;
  const bool scheduleOk = !FLAGS_schedule.empty() && !parseSchedule(FLAGS_schedule).empty();
  if (FLAGS_mode != "send" || FLAGS_dest.empty() || FLAGS_duration_s <= 0 ||
      FLAGS_packet_size < int(sizeof(Header)) || FLAGS_packet_size > 1472 ||
      (FLAGS_schedule.empty() ? !ppbpOk : !scheduleOk)) {
    std::cerr << "send needs --dest, --duration_s, --packet_size and either a valid --schedule "
                 "(start_s:duration_s:rate_mbps,...) or --mean_mbps/--burst_mbps/--mean_burst_s/"
                 "--hurst (0.5..1)\n";
    return 2;
  }
  return runSend();
}
