// Plan file of one simulation run, written by simlab/plan.py from the testbed's own
// topology.yaml + scenario.yaml. One record per line: "<type> key=value key=value ...".
// Values never contain spaces. Unknown record types are an error (the plan and this
// reader change together).
#pragma once

#include <cstdint>
#include <fstream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace quicsim {

struct Record {
  std::string type;
  std::map<std::string, std::string> kv;
  int line{0};

  bool has(const std::string& k) const { return kv.count(k) > 0; }
  const std::string& str(const std::string& k) const {
    auto it = kv.find(k);
    if (it == kv.end()) {
      throw std::runtime_error("plan line " + std::to_string(line) + " (" + type + "): missing " + k);
    }
    return it->second;
  }
  std::string str(const std::string& k, const std::string& def) const { return has(k) ? kv.at(k) : def; }
  double num(const std::string& k) const { return std::stod(str(k)); }
  double num(const std::string& k, double def) const { return has(k) ? std::stod(kv.at(k)) : def; }
  int64_t i64(const std::string& k) const { return std::stoll(str(k)); }
  int64_t i64(const std::string& k, int64_t def) const { return has(k) ? std::stoll(kv.at(k)) : def; }
};

inline std::vector<std::string> splitList(const std::string& s, char sep = ',') {
  std::vector<std::string> out;
  std::stringstream in(s);
  std::string item;
  while (std::getline(in, item, sep)) {
    if (!item.empty()) out.push_back(item);
  }
  return out;
}

inline std::vector<Record> readPlan(const std::string& path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read plan " + path);
  std::vector<Record> out;
  std::string line;
  int n = 0;
  while (std::getline(in, line)) {
    ++n;
    if (line.empty() || line[0] == '#') continue;
    std::istringstream words(line);
    Record r;
    r.line = n;
    words >> r.type;
    std::string w;
    while (words >> w) {
      const auto eq = w.find('=');
      if (eq == std::string::npos) throw std::runtime_error("plan line " + std::to_string(n) + ": bad token " + w);
      r.kv[w.substr(0, eq)] = w.substr(eq + 1);
    }
    out.push_back(std::move(r));
  }
  return out;
}

}  // namespace quicsim
