// Shared pieces: the run clock (testbed CLOCK_MONOTONIC / CLOCK_REALTIME stand-ins),
// the packet tag every application packet carries, and buffered CSV output.
#pragma once

#include "ns3/core-module.h"
#include "ns3/network-module.h"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <memory>
#include <string>

namespace quicsim {

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

// Buffered CSV file; the directory is created on open.
class Csv {
 public:
  Csv() = default;
  Csv(const std::string& path, const std::string& header) { open(path, header); }
  void open(const std::string& path, const std::string& header) {
    std::filesystem::create_directories(std::filesystem::path(path).parent_path());
    buf_.resize(1 << 20);
    out_ = std::make_unique<std::ofstream>();
    out_->rdbuf()->pubsetbuf(buf_.data(), std::streamsize(buf_.size()));
    out_->open(path);
    if (!*out_) throw std::runtime_error("cannot write " + path);
    *out_ << header << '\n';
  }
  bool isOpen() const { return out_ != nullptr; }
  std::ofstream& os() { return *out_; }
  template <typename T>
  Csv& operator<<(const T& v) {
    *out_ << v;
    return *this;
  }
  void close() {
    if (out_) out_->close();
    out_.reset();
  }

 private:
  std::vector<char> buf_;
  std::unique_ptr<std::ofstream> out_;
};

}  // namespace quicsim
