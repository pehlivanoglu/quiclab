/* SPDX-License-Identifier: Apache-2.0 */
// moqx_shadow_replay: re-run the shadow detector offline over a recorded
// run's per-ACK CSVs, through the same Engine the relay uses.
//
//   moqx_shadow_replay --manifest FILE --output DIR --relay-id ID
//       [--unix-offset-ns N] [--cpu-threshold X] [--variant NAME]...
//       [--events-only]   (events and meta only, no per-ACK sample files)
//       [--param KEY=VALUE]...
//
// Manifest lines (tab-separated): connection_id, flow, group (may be empty),
// peer, path to that flow's samples CSV, and optionally its sent CSV.
//
// Inputs come from the CSV, so detector logic changes can be evaluated on
// the exact network history of earlier runs. Sent bytes come from the
// relay's sent log (5 ms bins of what it wrote) when the run has one; older
// runs rebuild them from acknowledged packets (bytes_sent_at_send at
// sent_mono_us), spread evenly between consecutive acked packets.

#include "shadow/Engine.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace openmoq::moqx::shadow;

namespace {

std::vector<std::string> split(const std::string& line, char separator) {
  std::vector<std::string> fields;
  std::string field;
  std::istringstream in(line);
  while (std::getline(in, field, separator)) fields.push_back(field);
  if (!line.empty() && line.back() == separator) fields.emplace_back();
  return fields;
}

double number(const std::string& text) {
  return text.empty() ? 0.0 : std::stod(text);
}

BbrPhase phaseFrom(const std::string& name) {
  for (auto phase : {BbrPhase::Startup, BbrPhase::Drain, BbrPhase::ProbeBwDown,
                     BbrPhase::ProbeBwCruise, BbrPhase::ProbeBwRefill, BbrPhase::ProbeBwUp,
                     BbrPhase::ProbeBw, BbrPhase::ProbeRtt})
    if (name == phaseName(phase)) return phase;
  return BbrPhase::Unknown;
}

struct Input {
  FlowInfo info;
  std::vector<AckSample> samples;
  std::vector<uint64_t> seq;  // relay processing order (empty for older runs)
};

Input load(const FlowInfo& info, const std::string& path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read " + path);
  std::string line;
  std::getline(in, line);
  std::map<std::string, size_t> col;
  const auto header = split(line, ',');
  for (size_t i = 0; i < header.size(); ++i) col[header[i]] = i;
  for (const char* required : {"mono_us", "sent_mono_us", "rtt_us", "min_rtt_us", "srtt_us",
                               "rate_valid", "app_limited", "send_bps", "ack_bps", "bbr_bw_bps",
                               "cwnd_bytes", "inflight_bytes", "stream_buffer_bytes",
                               "bytes_acked_total", "bytes_sent_at_send", "phase", "newly_lost",
                               "relay_saturated"})
    if (!col.count(required)) throw std::runtime_error(path + ": missing column " + required);
  Input input{info, {}};
  while (std::getline(in, line)) {
    const auto f = split(line, ',');
    if (f.size() < header.size()) continue; // truncated final line
    auto get = [&](const char* name) -> const std::string& { return f[col.at(name)]; };
    AckSample s;
    s.ackUs = static_cast<int64_t>(number(get("mono_us")));
    s.sentUs = static_cast<int64_t>(number(get("sent_mono_us")));
    if (!get("rtt_us").empty()) s.rttUs = static_cast<int64_t>(number(get("rtt_us")));
    s.minRttUs = static_cast<int64_t>(number(get("min_rtt_us")));
    s.srttUs = static_cast<int64_t>(number(get("srtt_us")));
    s.rateValid = get("rate_valid") == "1";
    s.appLimited = get("app_limited") == "1";
    s.sendBps = number(get("send_bps"));
    s.ackBps = number(get("ack_bps"));
    s.bbrBwBps = number(get("bbr_bw_bps"));
    s.cwndBytes = static_cast<uint64_t>(number(get("cwnd_bytes")));
    s.inflightBytes = static_cast<uint64_t>(number(get("inflight_bytes")));
    s.streamBufferBytes = static_cast<uint64_t>(number(get("stream_buffer_bytes")));
    s.bytesAckedTotal = static_cast<uint64_t>(number(get("bytes_acked_total")));
    s.bytesSentAtSend = static_cast<uint64_t>(number(get("bytes_sent_at_send")));
    s.phase = phaseFrom(get("phase"));
    s.newlyLost = static_cast<uint32_t>(number(get("newly_lost")));
    s.relaySaturated = get("relay_saturated") == "1";
    input.samples.push_back(s);
    if (col.count("seq")) input.seq.push_back(std::stoull(get("seq")));
  }
  return input;
}

struct Sent {
  int64_t t;
  uint64_t bytes;
  uint64_t seq;
};

// Recorded relay writes, or empty when the run predates them.
std::vector<Sent> loadSent(const std::string& path) {
  std::vector<Sent> sent;
  if (path.empty()) return sent;
  std::ifstream in(path);
  if (!in) return sent;
  std::string line;
  std::getline(in, line);  // header
  while (std::getline(in, line)) {
    const auto f = split(line, ',');
    if (f.size() < 2) continue;
    sent.push_back({std::stoll(f[0]), std::stoull(f[1]), f.size() > 2 ? std::stoull(f[2]) : 0});
  }
  return sent;
}

enum Kind { kEligible = 0, kSend = 1, kAck = 2, kClose = 3 };

struct Step {
  int64_t t;
  int kind;
  size_t flow;
  size_t row;
  uint64_t bytes;
  int64_t order{0};  // relay processing order when recorded, else the time
};

} // namespace

int main(int argc, char** argv) {
  std::string manifest, output, relayId = "relay";
  int64_t unixOffsetNs = 0;
  double cpuThreshold = 0.9;
  std::vector<std::string> variantNames;
  Params params;
  bool eventsOnly = false;  // write events and meta, no per-ACK sample files
  try {
    for (int i = 1; i < argc; ++i) {
      const std::string arg = argv[i];
      auto value = [&]() -> std::string {
        if (i + 1 >= argc) throw std::runtime_error(arg + " needs a value");
        return argv[++i];
      };
      if (arg == "--manifest") manifest = value();
      else if (arg == "--output") output = value();
      else if (arg == "--relay-id") relayId = value();
      else if (arg == "--unix-offset-ns") unixOffsetNs = std::stoll(value());
      else if (arg == "--cpu-threshold") cpuThreshold = std::stod(value());
      else if (arg == "--variant") variantNames.push_back(value());
      else if (arg == "--events-only") eventsOnly = true;
      else if (arg == "--param") {
        const auto kv = value();
        const auto eq = kv.find('=');
        if (eq == std::string::npos) throw std::runtime_error("--param needs KEY=VALUE");
        if (auto error = applyParam(params, kv.substr(0, eq), std::stod(kv.substr(eq + 1)));
            !error.empty())
          throw std::runtime_error(error);
      } else {
        throw std::runtime_error("unknown argument " + arg);
      }
    }
    if (manifest.empty() || output.empty()) throw std::runtime_error("--manifest and --output are required");
    const auto known = builtinVariantNames();
    for (const auto& name : variantNames)
      if (std::find(known.begin(), known.end(), name) == known.end())
        throw std::runtime_error("unknown variant " + name);

    std::vector<Input> inputs;
    std::vector<std::vector<Sent>> sentLogs;
    std::ifstream list(manifest);
    if (!list) throw std::runtime_error("cannot read " + manifest);
    std::string line;
    while (std::getline(list, line)) {
      if (line.empty()) continue;
      const auto f = split(line, '\t');
      if (f.size() < 5) throw std::runtime_error("bad manifest line: " + line);
      inputs.push_back(load(FlowInfo{f[0], f[3], f[1], f[2]}, f[4]));
      sentLogs.push_back(loadSent(f.size() > 5 ? f[5] : ""));
    }

    std::vector<Step> steps;
    for (size_t i = 0; i < inputs.size(); ++i) {
      const auto& samples = inputs[i].samples;
      if (samples.empty()) continue;
      steps.push_back({samples.front().ackUs - 1, kEligible, i, 0, 0});
      steps.push_back({samples.back().ackUs + 1, kClose, i, 0, 0});
      if (!sentLogs[i].empty()) {
        // Exact relay writes: the same sends the live engine saw.
        for (size_t r = 0; r < samples.size(); ++r) steps.push_back({samples[r].ackUs, kAck, i, r, 0});
        for (const auto& s : sentLogs[i]) steps.push_back({s.t, kSend, i, 0, s.bytes});
        continue;
      }
      uint64_t lastBytes = samples.front().bytesSentAtSend;
      int64_t lastSent = samples.front().sentUs;
      for (size_t r = 0; r < samples.size(); ++r) {
        const auto& s = samples[r];
        steps.push_back({s.ackUs, kAck, i, r, 0});
        if (s.bytesSentAtSend <= lastBytes || s.sentUs <= lastSent) continue;
        const uint64_t delta = s.bytesSentAtSend - lastBytes;
        const int64_t gap = s.sentUs - lastSent;
        // Spread over the interval in 5 ms pieces; long idle gaps carry the
        // bytes at the end, where the burst actually happened.
        const int pieces = gap <= 200'000 ? std::max<int>(1, static_cast<int>(gap / 5'000)) : 1;
        for (int p = 0; p < pieces; ++p) {
          const uint64_t share = delta / pieces + (p == pieces - 1 ? delta % pieces : 0);
          steps.push_back({s.sentUs - (pieces - 1 - p) * 5'000, kSend, i, r, share});
        }
        lastBytes = s.bytesSentAtSend;
        lastSent = s.sentUs;
      }
    }
    // Runs that recorded the relay's processing order replay in that order
    // (sends and ACKs of all flows interleaved exactly as live); eligibility
    // and close bracket each flow's first and last recorded step.
    bool ordered = !inputs.empty();
    for (size_t i = 0; i < inputs.size(); ++i)
      ordered = ordered && (inputs[i].samples.empty() ||
                            (inputs[i].seq.size() == inputs[i].samples.size() && !sentLogs[i].empty() &&
                             sentLogs[i].front().seq > 0));
    if (ordered) {
      std::vector<size_t> sentIndex(inputs.size(), 0);
      for (auto& step : steps) {
        const auto& in = inputs[step.flow];
        switch (step.kind) {
          case kAck: step.order = 2 * static_cast<int64_t>(in.seq[step.row]); break;
          case kSend: step.order = 2 * static_cast<int64_t>(sentLogs[step.flow][sentIndex[step.flow]++].seq); break;
          case kEligible: {
            const uint64_t first = std::min(in.seq.front(), sentLogs[step.flow].front().seq);
            step.order = 2 * static_cast<int64_t>(first) - 1;
            break;
          }
          case kClose: {
            const uint64_t last = std::max(in.seq.back(), sentLogs[step.flow].back().seq);
            step.order = 2 * static_cast<int64_t>(last) + 1;
            break;
          }
        }
      }
    } else {
      for (auto& step : steps) step.order = step.t;
    }
    std::stable_sort(steps.begin(), steps.end(), [](const Step& a, const Step& b) {
      return a.order != b.order ? a.order < b.order : a.kind < b.kind;
    });

    std::filesystem::create_directories(std::filesystem::path(output) / "samples");
    std::ofstream events(output + "/events.jsonl", std::ios::trunc);
    Engine engine(selectVariants(params, variantNames),
                  [&](const std::string& variant, const char* scope, const FlowInfo& flow,
                      const Event& event) {
                    events << eventLine(relayId, unixOffsetNs, variant, scope, flow, event);
                  });
    std::vector<std::ofstream> files(inputs.size());
    for (const auto& step : steps) {
      const auto& info = inputs[step.flow].info;
      switch (step.kind) {
        case kEligible:
          engine.addFlow(info);
          if (!eventsOnly) files[step.flow].open(output + "/" + sampleFileName(info), std::ios::trunc);
          if (!eventsOnly) {
            // Same layout as a live run: detector columns plus the relay's order.
            const std::string header = kSampleHeader;
            files[step.flow] << header.substr(0, header.size() - 1) << (inputs[step.flow].seq.empty() ? "" : ",seq")
                             << '\n';
          }
          events << eventLine(relayId, unixOffsetNs, "", "flow", info,
                              Event{"flow_eligible", step.t, "\"peer\":" + jsonString(info.peer)});
          break;
        case kSend:
          engine.onSent(info.id, step.t, step.bytes);
          break;
        case kAck:
          if (engine.onAck(info.id, inputs[step.flow].samples[step.row]) && !eventsOnly)
          {
            std::string row = engine.sampleRow(info.id);
            if (!inputs[step.flow].seq.empty()) {
              row.pop_back();
              row += "," + std::to_string(inputs[step.flow].seq[step.row]) + "\n";
            }
            files[step.flow] << row;
          }
          break;
        case kClose:
          engine.removeFlow(info.id);
          events << eventLine(relayId, unixOffsetNs, "", "flow", info, Event{"flow_closed", step.t, ""});
          break;
      }
    }
    std::map<std::string, std::vector<std::string>> groups;
    std::vector<MetaFlow> flows;
    for (const auto& input : inputs) {
      if (!input.info.group.empty()) groups[input.info.group].push_back(input.info.peer);
      flows.push_back({input.info, true, true, !input.samples.empty()});
    }
    std::ofstream(output + "/meta.json", std::ios::trunc)
        << metaJson(relayId, unixOffsetNs, cpuThreshold, false, engine.variants(), groups, flows);
    std::cerr << "replayed " << steps.size() << " steps for " << inputs.size() << " flows into "
              << output << "\n";
  } catch (const std::exception& error) {
    std::cerr << "moqx_shadow_replay: " << error.what() << "\n";
    return 2;
  }
  return 0;
}
