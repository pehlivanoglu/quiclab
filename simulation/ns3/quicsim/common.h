// Shared pieces: the run clock (testbed CLOCK_MONOTONIC / CLOCK_REALTIME stand-ins),
// the packet tag every application packet carries, and buffered CSV output.
#pragma once

#include "ns3/core-module.h"
#include "ns3/network-module.h"

#include <cerrno>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <memory>
#include <set>
#include <string>

#include <fcntl.h>
#include <unistd.h>

namespace quicsim {

// Fixed ns-3 random stream numbers (NOTES.md "Randomness", user 2026-11-19): every random variable that stays in
// the simulation gets one, so no draw depends on ns-3's automatic numbering (which counts every random variable
// created before it). BBR of video flow i: sender kStreamBbr + i, receiver kStreamBbrRx + i; queue disc of egress k
// (PIE, RED): kStreamQueue + k; the internet stacks (ARP, IPv6 / ICMPv6, global routing when used):
// kStreamStack onwards.
constexpr int64_t kStreamBbr = 1000;
constexpr int64_t kStreamBbrRx = 50000;
constexpr int64_t kStreamQueue = 100000;
constexpr int64_t kStreamStack = 200000;

// Simulator time 0 maps to these instants. The testbed's files hold monotonic
// (mono_us, *_mono_ns) and wall-clock (t_us, *_unix_ns) times; the frozen readers
// only ever subtract the run's epoch, so any fixed offsets work.
struct Clock {
  int64_t mono0Ns{0};
  int64_t unix0Ns{0};
  ns3::Time epoch;  // scenario t = 0 (events.csv "epoch"), also the live stream start

  int64_t monoNs(ns3::Time t) const { return mono0Ns + t.GetNanoSeconds(); }
  int64_t monoUs(ns3::Time t) const { return monoNs(t) / 1000; }
  int64_t unixUs(ns3::Time t) const { return (unix0Ns + t.GetNanoSeconds()) / 1000; }
  int64_t monoUsNow() const { return monoUs(ns3::Simulator::Now()); }
  int64_t unixUsNow() const { return unixUs(ns3::Simulator::Now()); }
  // Simulator time of a wall-clock instant (unix us).
  ns3::Time atUnixUs(int64_t us) const { return ns3::NanoSeconds(us * 1000 - unix0Ns); }
};

Clock& simClock();

// The testbed server numbers every sent-row and ACK-row of all clients with one
// process-wide counter (gSeq); the replay uses it as the processing order.
uint64_t nextSeq();

enum class Kind : uint8_t { Video = 1, VideoAck = 2, Bg = 3 };

// Carried by every application packet (and the video sink's ACKs): which flow and
// which transmission it is, and when it left. Read at the routers (traces) and at
// the receivers (exact one-way delay; spec 4 "packet arrival time at the receiver",
// FLAG: idealisation of the QUIC receive-timestamp extension).
class FlowTag : public ns3::Tag {
 public:
  static ns3::TypeId GetTypeId();
  ns3::TypeId GetInstanceTypeId() const override { return GetTypeId(); }
  uint32_t GetSerializedSize() const override { return 1 + 4 + 8 + 8; }
  void Serialize(ns3::TagBuffer b) const override {
    b.WriteU8(uint8_t(kind));
    b.WriteU32(flow);
    b.WriteU64(tx);
    b.WriteU64(uint64_t(sendNs));
  }
  void Deserialize(ns3::TagBuffer b) override {
    kind = Kind(b.ReadU8());
    flow = b.ReadU32();
    tx = b.ReadU64();
    sendNs = int64_t(b.ReadU64());
  }
  void Print(std::ostream& os) const override { os << "flow=" << flow << " tx=" << tx; }

  Kind kind{Kind::Video};
  uint32_t flow{0};   // video: client index; bg: (event index << 16) | flow index
  uint64_t tx{0};     // video: transmission index (the pkts.csv "pn"); bg: per-flow sequence
  int64_t sendNs{0};  // simulator time of the transmission
};

// CSV output through one shared, bounded buffer pool (item 5: memory independent of the number of
// files / clients). Each file appends to its own string; when all buffered bytes together exceed
// OutputPool::capBytes (E: engineering constant, NOTES.md), every buffer is written to its file and
// released. Formatting is std::ostream's, as before, so the bytes written are unchanged.
class CsvBuf;

struct OutputPool {
  static constexpr uint64_t capBytes = uint64_t(256) << 20;  // (E) 256 MiB for all files together
  uint64_t buffered{0};
  std::set<CsvBuf*> open;
  void flushAll();
  static OutputPool& get() {
    static OutputPool p;
    return p;
  }
};

class CsvBuf : public std::streambuf {
 public:
  explicit CsvBuf(const std::string& path) {
    fd_ = ::open(path.c_str(), O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (fd_ < 0) throw std::runtime_error("cannot write " + path + ": " + std::strerror(errno));
    OutputPool::get().open.insert(this);
  }
  ~CsvBuf() override { close(); }
  void flushOut() {
    size_t done = 0;
    while (done < data_.size()) {
      const ssize_t n = ::write(fd_, data_.data() + done, data_.size() - done);
      if (n < 0) {
        if (errno == EINTR) continue;
        throw std::runtime_error(std::string("write failed: ") + std::strerror(errno));
      }
      done += size_t(n);
    }
    OutputPool::get().buffered -= data_.size();
    std::string().swap(data_);  // release the memory, not only the contents
  }
  void close() {
    if (fd_ < 0) return;
    flushOut();
    ::close(fd_);
    fd_ = -1;
    OutputPool::get().open.erase(this);
  }

 protected:
  int_type overflow(int_type c) override {
    if (c != traits_type::eof()) {
      const char ch = traits_type::to_char_type(c);
      xsputn(&ch, 1);
    }
    return traits_type::not_eof(c);
  }
  std::streamsize xsputn(const char* s, std::streamsize n) override {
    data_.append(s, size_t(n));
    OutputPool& pool = OutputPool::get();
    pool.buffered += uint64_t(n);
    if (pool.buffered > OutputPool::capBytes) pool.flushAll();
    return n;
  }

 private:
  int fd_{-1};
  std::string data_;
};

inline void OutputPool::flushAll() {
  for (CsvBuf* b : open) b->flushOut();
}

// CSV file; the directory is created on open.
class Csv {
 public:
  Csv() = default;
  Csv(const std::string& path, const std::string& header) { open(path, header); }
  void open(const std::string& path, const std::string& header) {
    std::filesystem::create_directories(std::filesystem::path(path).parent_path());
    buf_ = std::make_unique<CsvBuf>(path);
    out_ = std::make_unique<std::ostream>(buf_.get());
    *out_ << header << '\n';
  }
  bool isOpen() const { return out_ != nullptr; }
  std::ostream& os() { return *out_; }
  template <typename T>
  Csv& operator<<(const T& v) {
    *out_ << v;
    return *this;
  }
  void close() {
    out_.reset();
    if (buf_) buf_->close();
    buf_.reset();
  }
  ~Csv() { close(); }
  Csv(const Csv&) = delete;
  Csv& operator=(const Csv&) = delete;
  Csv(Csv&&) = default;
  Csv& operator=(Csv&& o) noexcept {
    if (this != &o) {
      close();
      buf_ = std::move(o.buf_);
      out_ = std::move(o.out_);
    }
    return *this;
  }

 private:
  std::unique_ptr<CsvBuf> buf_;
  std::unique_ptr<std::ostream> out_;
};

}  // namespace quicsim
