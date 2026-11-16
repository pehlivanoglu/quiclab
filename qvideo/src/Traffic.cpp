// qtraffic: PPBP cross traffic over UDP (see Ppbp.h), or a fixed burst schedule.
//
//   send: precomputes every burst, from the seed or from --schedule (written to
//         <out>-bursts.csv, the offered-load truth), waits for --start_unix_us,
//         then emits the aggregate rate of the active bursts:
//           --process=pace (default)  1 ms credit loop, one socket (the original sender);
//           --process=poisson         --flow_weights flows, one socket (own source port,
//                                     own 5-tuple) and one Poisson RNG stream each
//                                     (Departures.h); suite v3 background and surges;
//           --process=asv             aggregate synchronized video (Departures.h), one socket;
//           --proto=tcp               one TCP connection (--cc), the 1 ms credit loop paces
//                                     the application writes (rate-limited / on-off TCP).
//   recv: sink; per 100 ms writes packets, bytes, sequence gaps (loss, per flow) and
//         one-way delay (sender and receiver share one kernel clock). --proto=tcp
//         accepts one connection and counts bytes.
//   plan: --process=poisson|asv without sockets: writes every departure of the
//         process to <out>-plan.csv (t_us since start, flow, bytes), for tests.

#include "Common.h"
#include "Departures.h"
#include "Ppbp.h"

#include <gflags/gflags.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <unistd.h>

#include <algorithm>
#include <cerrno>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <optional>
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
DEFINE_string(process, "pace", "send/plan: pace | poisson | asv");
DEFINE_string(proto, "udp", "send/recv: udp | tcp (tcp: --process=pace only)");
DEFINE_string(cc, "", "send --proto=tcp: TCP_CONGESTION (cubic, bbr, ...); empty = kernel default");
DEFINE_string(flow_weights, "1", "poisson: relative rate of each flow, w1,w2,...");
DEFINE_uint64(stream_start_us, 0, "asv: the shared stream start T0 (frame k due at T0 + k / fps)");
DEFINE_int32(asv_kbps, 5000, "asv: rendition whose frame-size pattern is replayed");
DEFINE_double(asv_ref_mbps, 0, "asv: payload rate the pattern is scaled from; 0 = asv_kbps / 1000");
DEFINE_int32(fps, 30, "asv: frame rate");
DEFINE_int32(gop_ms, 1000, "asv: GOP length");
DEFINE_double(ip_ratio, 4.0, "asv: mean I-frame / mean P-frame size");
DEFINE_double(size_sigma, 0.2, "asv: lognormal frame-size sigma");
DEFINE_uint64(video_seed, 1, "asv: the video frame-size seed");
DEFINE_uint64(asv_key_spread_us, 0, "asv: emission time of a keyframe");
DEFINE_uint64(asv_p_spread_us, 0, "asv: emission time of a P-frame");
DEFINE_uint64(bin5_us, 5000, "send poisson/asv/tcp: bin of <out>-sent5.csv (byte counts for the phase-lock check)");

namespace {

constexpr uint64_t kBinUs = 100000;
constexpr uint64_t kTickUs = 1000;

#pragma pack(push, 1)
struct Header {
  uint64_t seq;     // per flow
  uint64_t sendUs;
  uint32_t flow;
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

std::vector<qvideo::Burst> scheduledBursts() {
  return FLAGS_schedule.empty()
      ? qvideo::ppbpBursts({FLAGS_mean_mbps, FLAGS_burst_mbps, FLAGS_mean_burst_s, FLAGS_hurst,
                            FLAGS_duration_s, FLAGS_seed})
      : parseSchedule(FLAGS_schedule);
}

void writeBursts(const std::vector<qvideo::Burst>& bursts) {
  std::ofstream out(FLAGS_out + "-bursts.csv");
  out << "burst,start_s,duration_s,rate_mbps\n";
  for (size_t i = 0; i < bursts.size(); ++i) {
    out << i << ',' << bursts[i].startS << ',' << bursts[i].durationS << ',' << bursts[i].rateMbps << '\n';
  }
}

std::vector<double> parseWeights(const std::string& text) {
  std::vector<double> w;
  std::istringstream in(text);
  std::string item;
  while (std::getline(in, item, ',')) {
    char* end = nullptr;
    const double v = std::strtod(item.c_str(), &end);
    if (end == item.c_str() || *end != '\0' || !(v > 0)) {
      return {};
    }
    w.push_back(v);
  }
  return w.size() > 256 ? std::vector<double>{} : w;
}

qvideo::AsvParams asvParams(uint64_t start) {
  qvideo::AsvParams p;
  p.video.rateKbps = uint32_t(FLAGS_asv_kbps);
  p.video.fps = uint32_t(FLAGS_fps);
  p.video.gopFrames = uint32_t(std::max(1L, std::lround(FLAGS_gop_ms * FLAGS_fps / 1000.0)));
  p.video.ipRatio = FLAGS_ip_ratio;
  p.video.sizeSigma = FLAGS_size_sigma;
  p.video.seed = FLAGS_video_seed;
  p.refMbps = FLAGS_asv_ref_mbps > 0 ? FLAGS_asv_ref_mbps : FLAGS_asv_kbps / 1000.0;
  p.streamStartUs = FLAGS_stream_start_us ? FLAGS_stream_start_us : start;
  p.startUs = start;
  p.keySpreadUs = FLAGS_asv_key_spread_us;
  p.pSpreadUs = FLAGS_asv_p_spread_us;
  return p;
}

// Departures of --process=poisson | asv, one at a time in time order.
struct DepartureStream {
  qvideo::RateSteps steps;
  std::optional<qvideo::PoissonSource> poisson;
  std::optional<qvideo::AsvSource> asv;

  DepartureStream(const std::vector<qvideo::Burst>& bursts, uint64_t start)
      : steps(bursts) {
    const uint64_t dur = uint64_t(FLAGS_duration_s * 1e6);
    if (FLAGS_process == "poisson") {
      poisson.emplace(steps, parseWeights(FLAGS_flow_weights), uint32_t(FLAGS_packet_size), dur, FLAGS_seed);
    } else {
      asv.emplace(steps, asvParams(start), uint32_t(FLAGS_packet_size), dur);
    }
  }
  size_t flows() const { return poisson ? poisson->flows() : 1; }
  std::optional<qvideo::Departure> next() { return poisson ? poisson->next() : asv->next(); }
};

int runPlan() {
  const auto bursts = scheduledBursts();
  writeBursts(bursts);
  // asv without --stream_start_us: the process starts on the stream grid at T0 = 0.
  const uint64_t start = FLAGS_start_unix_us ? FLAGS_start_unix_us : FLAGS_stream_start_us;
  DepartureStream d(bursts, start);
  std::ofstream out(FLAGS_out + "-plan.csv");
  out << "t_us,flow,bytes\n";
  while (auto x = d.next()) {
    out << x->tUs << ',' << x->flow << ',' << x->bytes << '\n';
  }
  return 0;
}

// Sender log every 100 ms (the original columns) plus 5 ms byte bins.
struct SendLog {
  std::ofstream sent, sent5;
  std::vector<std::pair<uint64_t, double>> steps;  // offered rate edges (us since start)
  size_t next{0};
  int active{0};
  double offeredMbps{0};
  uint64_t start, binStart, bin5Start, binBytes{0}, binErrors{0}, bin5Bytes{0};

  SendLog(const std::vector<qvideo::Burst>& bursts, uint64_t start_, bool fine)
      : start(start_), binStart(start_), bin5Start(start_) {
    for (const auto& b : bursts) {
      steps.emplace_back(uint64_t(b.startS * 1e6), b.rateMbps);
      steps.emplace_back(uint64_t((b.startS + b.durationS) * 1e6), -b.rateMbps);
    }
    std::sort(steps.begin(), steps.end());
    sent.open(FLAGS_out + "-sent.csv");
    sent << "t_us,active_bursts,offered_mbps,sent_bytes,send_errors\n";
    if (fine) {
      sent5.open(FLAGS_out + "-sent5.csv");
      sent5 << "t_us,sent_bytes\n";
    }
  }

  void advance(uint64_t now) {
    while (next < steps.size() && start + steps[next].first <= now) {
      active += steps[next].second > 0 ? 1 : -1;
      offeredMbps = std::max(0.0, offeredMbps + steps[next++].second);
    }
    if (sent5.is_open()) {
      while (now - bin5Start >= FLAGS_bin5_us) {
        bin5Start += FLAGS_bin5_us;
        sent5 << bin5Start << ',' << bin5Bytes << '\n';
        bin5Bytes = 0;
      }
    }
    if (now - binStart >= kBinUs) {
      sent << now << ',' << active << ',' << offeredMbps << ',' << binBytes << ',' << binErrors << '\n';
      binStart = now;
      binBytes = binErrors = 0;
    }
  }

  void record(ssize_t n) {
    if (n < 0) {
      ++binErrors;
    } else {
      binBytes += uint64_t(n);
      bin5Bytes += uint64_t(n);
    }
  }
};

int connectedUdp(const sockaddr_in& dest) {
  int fd = udpSocket(FLAGS_bind, 0);
  if (connect(fd, reinterpret_cast<const sockaddr*>(&dest), sizeof(dest)) != 0) {
    std::perror("connect");
    std::exit(1);
  }
  return fd;
}

int localPort(int fd) {
  sockaddr_in a{};
  socklen_t len = sizeof(a);
  getsockname(fd, reinterpret_cast<sockaddr*>(&a), &len);
  return ntohs(a.sin_port);
}

// --process=poisson | asv: one UDP socket per flow, each departure at its planned time.
int runSendDepartures() {
  const auto bursts = scheduledBursts();
  writeBursts(bursts);
  const uint64_t start = FLAGS_start_unix_us ? FLAGS_start_unix_us : qvideo::nowUs();
  const uint64_t end = start + uint64_t(FLAGS_duration_s * 1e6);
  DepartureStream d(bursts, start);
  const sockaddr_in dest = address(FLAGS_dest, FLAGS_port);
  std::vector<int> fds;
  for (size_t i = 0; i < d.flows(); ++i) {
    fds.push_back(connectedUdp(dest));
  }
  const auto weights = FLAGS_process == "poisson" ? parseWeights(FLAGS_flow_weights) : std::vector<double>{1.0};
  std::vector<uint64_t> seq(fds.size(), 0), bytes(fds.size(), 0), first(fds.size(), 0), last(fds.size(), 0);
  std::vector<char> packet(size_t(FLAGS_packet_size), 0);
  SendLog log(bursts, start, true);
  sleepUntil(start);
  while (!stopRequested) {
    const auto x = d.next();
    const uint64_t due = x ? start + x->tUs : end;
    // Sleep only when the departure is far enough ahead; a late one leaves at once.
    for (uint64_t now = qvideo::nowUs(); now + 30 < due && !stopRequested; now = qvideo::nowUs()) {
      log.advance(now);
      sleepUntil(std::min(due, now + kBinUs / 2));
    }
    if (!x || stopRequested) {
      break;
    }
    const uint64_t now = qvideo::nowUs();
    log.advance(now);
    Header h{seq[x->flow]++, now, x->flow};
    std::memcpy(packet.data(), &h, sizeof(h));
    const ssize_t n = send(fds[x->flow], packet.data(), x->bytes, 0);
    log.record(n);
    if (n > 0) {
      bytes[x->flow] += uint64_t(n);
      first[x->flow] = first[x->flow] ? first[x->flow] : now;
      last[x->flow] = now;
    }
  }
  log.advance(qvideo::nowUs());
  std::ofstream flows(FLAGS_out + "-flows.csv");
  flows << "flow,src_port,weight,packets,bytes,first_us,last_us,mean_mbps\n";
  for (size_t i = 0; i < fds.size(); ++i) {
    const double span = last[i] > first[i] ? double(last[i] - first[i]) : 0;
    flows << i << ',' << localPort(fds[i]) << ',' << (i < weights.size() ? weights[i] : 1.0) << ',' << seq[i]
          << ',' << bytes[i] << ',' << first[i] << ',' << last[i] << ','
          << (span > 0 ? double(bytes[i]) * 8 / span : 0) << '\n';
  }
  return 0;
}

int runSend() {
  if (FLAGS_process != "pace") {
    return runSendDepartures();
  }
  const auto bursts = scheduledBursts();
  writeBursts(bursts);
  // Offered rate as a step function: + a burst's rate at its start, - at its end.
  std::vector<std::pair<uint64_t, double>> steps;
  for (const auto& b : bursts) {
    steps.emplace_back(uint64_t(b.startS * 1e6), b.rateMbps);
    steps.emplace_back(uint64_t((b.startS + b.durationS) * 1e6), -b.rateMbps);
  }
  std::sort(steps.begin(), steps.end());

  const bool tcp = FLAGS_proto == "tcp";
  sockaddr_in dest = address(FLAGS_dest, FLAGS_port);
  int fd = -1;
  if (tcp) {
    fd = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in a = address(FLAGS_bind, 0);
    if (bind(fd, reinterpret_cast<sockaddr*>(&a), sizeof(a)) != 0) {
      std::perror("bind");
      return 1;
    }
    if (!FLAGS_cc.empty() &&
        setsockopt(fd, IPPROTO_TCP, TCP_CONGESTION, FLAGS_cc.c_str(), socklen_t(FLAGS_cc.size())) != 0) {
      std::perror("TCP_CONGESTION");
      return 1;
    }
  } else {
    fd = udpSocket(FLAGS_bind, 0);
  }
  const uint64_t start = FLAGS_start_unix_us ? FLAGS_start_unix_us : qvideo::nowUs();
  const uint64_t end = start + uint64_t(FLAGS_duration_s * 1e6);
  if (tcp) {
    // Connect ahead of the start (the receiver listens from setup), so the first
    // bytes leave at the planned time; retry while the sink comes up.
    while (connect(fd, reinterpret_cast<sockaddr*>(&dest), sizeof(dest)) != 0) {
      if (qvideo::nowUs() > start + 2000000 || stopRequested) {
        std::perror("connect");
        return 1;
      }
      ::close(fd);
      fd = socket(AF_INET, SOCK_STREAM, 0);
      sockaddr_in a = address(FLAGS_bind, 0);
      bind(fd, reinterpret_cast<sockaddr*>(&a), sizeof(a));
      if (!FLAGS_cc.empty()) {
        setsockopt(fd, IPPROTO_TCP, TCP_CONGESTION, FLAGS_cc.c_str(), socklen_t(FLAGS_cc.size()));
      }
      usleep(50000);
    }
  } else if (connect(fd, reinterpret_cast<sockaddr*>(&dest), sizeof(dest)) != 0) {
    std::perror("connect");
    return 1;
  }
  std::vector<char> packet(size_t(FLAGS_packet_size), 0);
  std::ofstream sent(FLAGS_out + "-sent.csv");
  sent << "t_us,active_bursts,offered_mbps,sent_bytes,send_errors\n";
  std::ofstream sent5;
  if (tcp) {
    sent5.open(FLAGS_out + "-sent5.csv");
    sent5 << "t_us,sent_bytes\n";
  }
  uint64_t bin5Start = start, bin5Bytes = 0;
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
      Header h{seq++, qvideo::nowUs(), 0};
      std::memcpy(packet.data(), &h, sizeof(h));
      // TCP: a full send buffer blocks here (the flow is cwnd-limited); the credit cap
      // above keeps it from bursting afterwards.
      const ssize_t n = send(fd, packet.data(), packet.size(), tcp ? MSG_NOSIGNAL : 0);
      if (n < 0) {
        ++binErrors;
      } else {
        binBytes += uint64_t(n);
        bin5Bytes += uint64_t(n);
      }
      credit -= FLAGS_packet_size;
    }
    if (sent5.is_open()) {
      while (now - bin5Start >= FLAGS_bin5_us) {
        bin5Start += FLAGS_bin5_us;
        sent5 << bin5Start << ',' << bin5Bytes << '\n';
        bin5Bytes = 0;
      }
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

int runRecvTcp() {
  int lfd = socket(AF_INET, SOCK_STREAM, 0);
  int one = 1;
  setsockopt(lfd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
  sockaddr_in a = address(FLAGS_bind, FLAGS_port);
  if (bind(lfd, reinterpret_cast<sockaddr*>(&a), sizeof(a)) != 0 || listen(lfd, 1) != 0) {
    std::perror("bind/listen");
    return 1;
  }
  std::ofstream out(FLAGS_out + "-recv.csv");
  out << "t_us,packets,bytes,lost,owd_mean_us,owd_max_us\n";
  timeval timeout{0, 100000};
  setsockopt(lfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
  int fd = -1;
  while (fd < 0 && !stopRequested) {
    fd = accept(lfd, nullptr, nullptr);
  }
  if (fd < 0) {
    return 0;
  }
  setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
  std::vector<char> buf(1 << 16);
  uint64_t bytes = 0, binStart = qvideo::nowUs();
  while (!stopRequested) {
    const ssize_t n = recv(fd, buf.data(), buf.size(), 0);
    if (n == 0) {
      break;
    }
    const uint64_t now = qvideo::nowUs();
    if (n > 0) {
      bytes += uint64_t(n);
    }
    if (now - binStart >= kBinUs) {
      out << now << ",0," << bytes << ",0,0,0\n";
      out.flush();
      binStart = now;
      bytes = 0;
    }
  }
  return 0;
}

int runRecv() {
  if (FLAGS_proto == "tcp") {
    return runRecvTcp();
  }
  int fd = udpSocket(FLAGS_bind, FLAGS_port);
  timeval timeout{0, 100000};
  setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
  std::ofstream out(FLAGS_out + "-recv.csv");
  out << "t_us,packets,bytes,lost,owd_mean_us,owd_max_us\n";
  std::vector<char> buf(65536);
  std::vector<uint64_t> expected(256, 0);
  uint64_t packets = 0, bytes = 0, lost = 0, owdSum = 0, owdMax = 0;
  uint64_t binStart = qvideo::nowUs();
  while (!stopRequested) {
    const ssize_t n = recv(fd, buf.data(), buf.size(), 0);
    const uint64_t now = qvideo::nowUs();
    if (n >= ssize_t(sizeof(Header))) {
      Header h;
      std::memcpy(&h, buf.data(), sizeof(h));
      uint64_t& exp = expected[h.flow % expected.size()];
      if (h.seq > exp) {
        lost += h.seq - exp;  // per flow: reordering across flows (fq_codel) is not loss
      }
      exp = std::max(exp, h.seq + 1);
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
  prctl(PR_SET_TIMERSLACK, 1UL);  // departures to the microsecond, not the default 50 us slack
  if (FLAGS_mode == "recv") {
    return runRecv();
  }
  const bool departures = FLAGS_process == "poisson" || FLAGS_process == "asv";
  if (!departures && FLAGS_process != "pace") {
    std::cerr << "--process must be pace, poisson or asv\n";
    return 2;
  }
  if ((FLAGS_proto != "udp" && FLAGS_proto != "tcp") || (FLAGS_proto == "tcp" && departures)) {
    std::cerr << "--proto must be udp or tcp; tcp needs --process=pace\n";
    return 2;
  }
  if (FLAGS_process == "poisson" && parseWeights(FLAGS_flow_weights).empty()) {
    std::cerr << "--flow_weights: 1 to 256 positive numbers\n";
    return 2;
  }
  if (FLAGS_process == "asv" && (FLAGS_asv_kbps <= 0 || FLAGS_fps <= 0 || FLAGS_gop_ms <= 0)) {
    std::cerr << "asv needs positive --asv_kbps, --fps, --gop_ms\n";
    return 2;
  }
  if (FLAGS_mode == "plan") {
    if (!departures || FLAGS_duration_s <= 0 || FLAGS_schedule.empty() || parseSchedule(FLAGS_schedule).empty()) {
      std::cerr << "plan needs --process=poisson|asv, --duration_s and a valid --schedule\n";
      return 2;
    }
    return runPlan();
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
