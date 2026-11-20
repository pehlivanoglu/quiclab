// quicsim: one testbed run (topology.yaml + scenario.yaml, converted to a plan by
// simlab/plan.py) on ns-3 with TCP BBR, writing the testbed's run-folder records so
// the frozen detector, truths and grouping read it unchanged.
//
//   ./ns3 run "quicsim --plan=<run>/sim/plan.txt --out=<run>"
//
// Spec: quiclab/docs/simulation-spec.md section 4. Every model choice that differs
// from the testbed is marked FLAG here and listed in simulation/NOTES.md.

#include "common.h"
#include "flow.h"
#include "plan.h"
#include "router.h"
#include "traffic.h"
#include "video.h"

#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/traffic-control-module.h"

#include <chrono>
#include <iostream>

using namespace ns3;

namespace quicsim {

Clock& simClock() {
  static Clock c;
  return c;
}

uint64_t nextSeq() {
  static uint64_t seq = 0;
  return ++seq;
}

NS_OBJECT_ENSURE_REGISTERED(FlowTag);
TypeId FlowTag::GetTypeId() {
  static TypeId tid = TypeId("quicsim::FlowTag").SetParent<Tag>().AddConstructor<FlowTag>();
  return tid;
}

NS_OBJECT_ENSURE_REGISTERED(TcpBbrObs);
TypeId TcpBbrObs::GetTypeId() {
  static TypeId tid =
      TypeId("quicsim::TcpBbrObs").SetParent<TcpBbr>().SetGroupName("Internet").AddConstructor<TcpBbrObs>();
  return tid;
}

// Read-only access to TcpBbr's private bandwidth filter (explicit instantiation may
// name private members; no ns-3 source is changed).
namespace {
struct BwFilterTag {
  using type = TcpBbr::MaxBandwidthFilter_t TcpBbr::*;
  friend type get(BwFilterTag);
};
template <typename Tag, typename Tag::type M>
struct Rob {
  friend typename Tag::type get(Tag) { return M; }
};
template struct Rob<BwFilterTag, &TcpBbr::m_maxBwFilter>;
}  // namespace

uint64_t TcpBbrObs::bwBps() const { return (this->*get(BwFilterTag{})).GetBest().GetBitRate(); }

}  // namespace quicsim

using namespace quicsim;

namespace {

struct Net {
  std::map<std::string, Ptr<Node>> nodes;
  std::map<std::string, Ipv4Address> addr;                           // node -> its first interface address
  std::map<std::pair<std::string, std::string>, Ptr<NetDevice>> dev;  // (node, peer) -> node's device
  std::map<std::pair<std::string, std::string>, Ptr<QueueDisc>> qd;
};

std::string queueDiscType(const Record& e, TrafficControlHelper& tch) {
  const std::string aqm = e.str("aqm");
  const std::string limit = e.str("limit_p") + "p";
  if (aqm == "pfifo" || aqm == "fifo") {
    tch.SetRootQueueDisc("ns3::FifoQueueDisc", "MaxSize", StringValue(limit));
  } else if (aqm == "codel") {
    tch.SetRootQueueDisc("ns3::CoDelQueueDisc", "MaxSize", StringValue(limit), "Target",
                         StringValue(e.str("target", "5ms")), "Interval", StringValue(e.str("interval", "100ms")),
                         "UseEcn", BooleanValue(false));
  } else if (aqm == "pie") {
    tch.SetRootQueueDisc("ns3::PieQueueDisc", "MaxSize", StringValue(limit), "QueueDelayReference",
                         TimeValue(Time(e.str("target", "15ms"))), "Tupdate",
                         TimeValue(Time(e.str("tupdate", "15ms"))), "UseEcn", BooleanValue(false));
  } else if (aqm == "red") {
    // Byte mode, as Linux red; thresholds and limit from the plan (time -> bytes there).
    tch.SetRootQueueDisc("ns3::RedQueueDisc", "MaxSize", StringValue(e.str("limit_b") + "B"), "MinTh",
                         DoubleValue(e.num("min_b")), "MaxTh", DoubleValue(e.num("max_b")), "MeanPktSize",
                         UintegerValue(uint32_t(e.num("avpkt", 1200))), "LInterm",
                         DoubleValue(1.0 / e.num("max_p", 0.02)), "Gentle", BooleanValue(false), "UseEcn",
                         BooleanValue(false), "LinkBandwidth", DataRateValue(DataRate(uint64_t(e.num("rate_bps")))));
  } else {
    throw std::runtime_error("queue not supported in the simulation: " + aqm + " (plan line " +
                             std::to_string(e.line) + ")");
  }
  return aqm;
}

}  // namespace

int main(int argc, char* argv[]) {
  std::string planPath, out;
  CommandLine cmd;
  cmd.AddValue("plan", "plan file (simlab/plan.py)", planPath);
  cmd.AddValue("out", "run folder to write", out);
  cmd.Parse(argc, argv);
  const auto wall0 = std::chrono::steady_clock::now();
  const auto plan = readPlan(planPath);
  auto ofType = [&](const std::string& t) {
    std::vector<const Record*> r;
    for (const auto& x : plan) if (x.type == t) r.push_back(&x);
    return r;
  };
  const Record& run = *ofType("run").at(0);

  Clock& clk = simClock();
  clk.mono0Ns = run.i64("mono0_ns");
  clk.unix0Ns = run.i64("unix0_ns");
  clk.epoch = Seconds(run.num("epoch_s"));
  const double duration = run.num("duration_s");
  RngSeedManager::SetSeed(uint32_t(run.i64("seed")));
  RngSeedManager::SetRun(1);

  // ── TCP (spec 4 "Transport"; constants tagged in NOTES.md) ──────────────
  const uint32_t segment = uint32_t(run.i64("segment"));
  Config::SetDefault("ns3::TcpL4Protocol::SocketType", TypeIdValue(TcpBbrObs::GetTypeId()));
  Config::SetDefault("ns3::TcpSocket::SegmentSize", UintegerValue(segment));
  Config::SetDefault("ns3::TcpSocket::DelAckCount", UintegerValue(uint32_t(run.i64("delack_count"))));
  Config::SetDefault("ns3::TcpSocket::DelAckTimeout", TimeValue(MilliSeconds(run.num("delack_ms"))));
  Config::SetDefault("ns3::TcpSocket::SndBufSize", UintegerValue(uint32_t(run.i64("sndbuf"))));
  Config::SetDefault("ns3::TcpSocket::RcvBufSize", UintegerValue(uint32_t(run.i64("rcvbuf"))));
  Config::SetDefault("ns3::TcpSocket::InitialCwnd", UintegerValue(uint32_t(run.i64("init_cwnd"))));
  Config::SetDefault("ns3::TcpSocketBase::Sack", BooleanValue(true));
  Config::SetDefault("ns3::TcpSocketBase::Timestamp", BooleanValue(true));
  Config::SetDefault("ns3::TcpSocketBase::MinRto", TimeValue(MilliSeconds(run.num("min_rto_ms"))));
  Config::SetDefault("ns3::TcpSocketState::EnablePacing", BooleanValue(true));

  // ── nodes and links ─────────────────────────────────────────────────────
  Net net;
  InternetStackHelper stack;
  for (const Record* n : ofType("node")) {
    auto node = CreateObject<Node>();
    net.nodes[n->str("name")] = node;
    stack.Install(node);
  }
  std::map<std::pair<std::string, std::string>, const Record*> egress;
  for (const Record* e : ofType("egress")) egress[{e->str("node"), e->str("peer")}] = e;

  Ipv4AddressHelper ip;
  uint32_t subnet = 0;
  for (const Record* l : ofType("link")) {
    const std::string a = l->str("a"), b = l->str("b");
    const double dab = l->num("delay_ab"), dba = l->num("delay_ba");
    if (dab != dba) {
      // FLAG: one point-to-point channel has one delay; asymmetric links are not modelled yet.
      throw std::runtime_error("asymmetric delay on " + a + "-" + b + " not supported");
    }
    PointToPointHelper p2p;
    p2p.SetChannelAttribute("Delay", TimeValue(Seconds(dab)));
    // FLAG: one packet of device queue so the queue lives in the queue disc (as the
    // testbed's qdisc); the queue disc then sees up to one packet time less sojourn.
    p2p.SetQueue("ns3::DropTailQueue", "MaxSize", StringValue("1p"));
    NetDeviceContainer d = p2p.Install(net.nodes.at(a), net.nodes.at(b));
    DynamicCast<PointToPointNetDevice>(d.Get(0))->SetDataRate(DataRate(uint64_t(l->num("rate_ab"))));
    DynamicCast<PointToPointNetDevice>(d.Get(1))->SetDataRate(DataRate(uint64_t(l->num("rate_ba"))));
    net.dev[{a, b}] = d.Get(0);
    net.dev[{b, a}] = d.Get(1);
    for (int side = 0; side < 2; ++side) {
      const std::string from = side ? b : a, to = side ? a : b;
      const Record* e = egress.at({from, to});
      TrafficControlHelper tch;
      queueDiscType(*e, tch);
      QueueDiscContainer q = tch.Install(d.Get(side));
      net.qd[{from, to}] = q.Get(0);
    }
    const std::string base = "10." + std::to_string(subnet / 256) + "." + std::to_string(subnet % 256) + ".0";
    ++subnet;
    ip.SetBase(base.c_str(), "255.255.255.0");
    Ipv4InterfaceContainer ifs = ip.Assign(d);
    net.addr.try_emplace(a, ifs.GetAddress(0));
    net.addr.try_emplace(b, ifs.GetAddress(1));
  }
  Ipv4GlobalRoutingHelper::PopulateRoutingTables();

  const Time end = clk.epoch + Seconds(duration);

  // ── traced / sampled egresses ───────────────────────────────────────────
  TupleMap tuples;
  for (const Record* v : ofType("video")) {
    tuples.video.push_back({v->str("pub_ip"), v->str("sub_ip"), uint16_t(v->i64("port"))});
  }
  for (const Record* g : ofType("bg")) {
    tuples.bg.push_back({g->str("saddr"), g->str("daddr"), uint16_t(g->i64("sport")), uint16_t(g->i64("port"))});
  }
  std::vector<std::unique_ptr<EgressMonitor>> monitors;
  for (const Record* m : ofType("monitor")) {
    MonitorConfig c;
    c.node = m->str("node");
    c.iface = m->str("iface");
    c.hop = m->str("node") + "->" + m->str("peer");
    c.metrics = m->i64("metrics") != 0;
    c.intervalMs = uint32_t(m->i64("interval_ms", 25));
    c.queueIntervalMs = uint32_t(m->i64("queue_interval_ms", 5));
    c.trace = m->i64("trace") != 0;
    c.delayNs = int64_t(m->num("delay_s") * 1e9);
    c.limitPackets = uint32_t(m->i64("limit_p", 0));
    c.ifindex = uint32_t(m->i64("ifindex", 0));
    c.runDir = out;
    monitors.push_back(std::make_unique<EgressMonitor>(c, net.qd.at({c.node, m->str("peer")}), &tuples));
  }

  // ── video clients ───────────────────────────────────────────────────────
  const Record& vp = *ofType("videoparams").at(0);
  VideoConfig vc;
  vc.video.fps = uint32_t(vp.i64("fps"));
  vc.video.gopFrames = uint32_t(vp.i64("gop_frames"));
  vc.video.ipRatio = vp.num("ip_ratio");
  vc.video.sizeSigma = vp.num("sigma");
  vc.video.seed = uint64_t(vp.i64("vseed"));
  vc.sendBufferMs = uint64_t(vp.i64("send_buffer_ms"));
  vc.statsMs = uint32_t(vp.i64("stats_ms"));
  vc.clientStatsMs = uint32_t(vp.i64("client_stats_ms"));
  vc.bufferMs = uint32_t(vp.i64("buffer_ms"));
  vc.segment = segment;
  vc.pktLog = vp.i64("pkt_log") != 0;
  vc.pubDir = out + "/publishers/" + vp.str("pub");
  vc.clientDir = out + "/clients";
  std::vector<std::unique_ptr<VideoFlow>> flows;
  for (const Record* v : ofType("video")) {
    auto f = std::make_unique<VideoFlow>();
    f->index = uint32_t(flows.size());
    f->sid = v->str("sid");
    f->rateKbps = uint32_t(v->i64("rate_kbps"));
    f->phaseMs = uint32_t(v->i64("phase_ms"));
    const uint16_t port = uint16_t(v->i64("port"));
    auto sink = CreateObject<VideoSink>(
        f.get(), vc, port, vc.video.fps, uint32_t(v->i64("delack_count", run.i64("delack_count"))),
        MilliSeconds(v->num("delack_ms", run.num("delack_ms"))));
    net.nodes.at(f->sid)->AddApplication(sink);
    sink->SetStartTime(Seconds(0));
    sink->SetStopTime(end);
    const double join = v->num("join_s");
    const double leave = v->num("leave_s", -1);
    auto snd = CreateObject<VideoSender>(f.get(), vc, InetSocketAddress(net.addr.at(f->sid), port),
                                         leave >= 0 ? clk.epoch + Seconds(leave) : Time(0));
    net.nodes.at(v->str("pub"))->AddApplication(snd);
    // Initial clients connect before the stream starts (testbed: before the epoch).
    snd->SetStartTime(join > 0 ? clk.epoch + Seconds(join) : clk.epoch - Seconds(run.num("connect_lead_s")));
    snd->SetStopTime(end);
    flows.push_back(std::move(f));
  }

  // ── background and stimuli ──────────────────────────────────────────────
  uint32_t ei = 0;
  for (const Record* g : ofType("bg")) {
    BgConfig c;
    c.event = ei++;
    c.id = g->str("id");
    c.process = g->str("process");
    c.seed = uint64_t(g->i64("seed"));
    c.packet = uint32_t(g->i64("packet"));
    c.start = clk.epoch + Seconds(g->num("at_s"));
    c.durationS = g->num("duration_s");
    c.outPrefix = out + "/traffic/" + c.id;
    c.basePort = uint16_t(g->i64("sport"));
    const uint16_t port = uint16_t(g->i64("port"));
    c.dest = InetSocketAddress(net.addr.at(g->str("dst")), port);
    if (g->has("weights")) {
      c.weights.clear();
      for (const auto& w : splitList(g->str("weights"))) c.weights.push_back(std::stod(w));
    }
    if (g->has("ppbp")) {  // mean:burst:mean_burst_s:hurst
      const auto p = splitList(g->str("ppbp"), ':');
      c.bursts = qvideo::ppbpBursts({std::stod(p[0]), std::stod(p[1]), std::stod(p[2]), std::stod(p[3]),
                                     c.durationS, c.seed});
    } else {
      for (const auto& s : splitList(g->str("schedule"))) {
        const auto p = splitList(s, ':');
        c.bursts.push_back({std::stod(p[0]), std::stod(p[1]), std::stod(p[2])});
      }
    }
    auto src = CreateObject<BgSource>(c);
    net.nodes.at(g->str("src"))->AddApplication(src);
    src->SetStartTime(Seconds(0));
    src->SetStopTime(end);
    auto sink = CreateObject<BgSink>(c.outPrefix, port);
    net.nodes.at(g->str("dst"))->AddApplication(sink);
    sink->SetStartTime(Seconds(0));
    sink->SetStopTime(end);
  }

  // ── link capacity changes ───────────────────────────────────────────────
  for (const Record* e : ofType("linkevent")) {
    auto d = DynamicCast<PointToPointNetDevice>(net.dev.at({e->str("a"), e->str("b")}));
    const DataRate r(uint64_t(e->num("rate_bps")));
    Simulator::Schedule(clk.epoch + Seconds(e->num("t_s")), [d, r]() { d->SetDataRate(r); });
  }

  Simulator::Stop(end + MilliSeconds(1));
  Simulator::Run();
  for (auto& m : monitors) m->finish();
  if (std::any_of(monitors.begin(), monitors.end(), [](auto& m) { return m->config().trace; })) {
    Csv ifs(out + "/router-trace/interfaces.csv", "router,iface,ifindex,netns,hop");
    Csv cnt(out + "/router-trace/tracer-counts.csv",
            "router,iface,ifindex,started,stopped_clean,tracer_start_ns,tracer_end_ns,lost_events,n_enq,n_deq,"
            "n_drop,n_requeue,n_nohit,n_batched,n_truncated,n_orphan,rows_dequeue,rows_drop,rows_nohit,"
            "rows_requeue,requeue_stale,nohit_late,oversize,unmatched_deq,unmatched_enq,unmatched_enq_rows,"
            "unmatched_deq_max_200ms,unmatched_enq_max_200ms,errors");
    for (auto& m : monitors) {
      if (!m->config().trace) continue;
      ifs << m->config().node << ',' << m->config().iface << ',' << m->config().ifindex << ",0," << m->config().hop
          << '\n';
      m->countsRow(cnt);
    }
  }
  Simulator::Destroy();
  const double wall = std::chrono::duration<double>(std::chrono::steady_clock::now() - wall0).count();
  std::cout << "quicsim done: simulated " << duration << " s, wall " << wall << " s, clients " << flows.size()
            << "\n";
  return 0;
}
