#!/usr/bin/env python3
"""Scenario catalog (read-only): topologies, scenarios, congestion events, calm load and the
campaign matrix, generated from the code and the run folders.

    .venv/bin/python3 scripts/scenario_catalog.py > docs/scenario-catalog-generated.md

Sources: configs/topologies/*.yaml (nodes, links, subscribers), the topologies' base scenario
files in configs/scenarios/ (capacities, delays, queue limits), scripts/det_matrix.py
(stimuli), scripts/grouping_campaign.py (campaigns, planners), quiclab/config/schema.py and
qvideo (video defaults), and every run's plan.json / scenario.yaml / router-metrics.

Measured calm load: per router egress, transmitted bytes / capacity over calm time (outside
every stimulus window +- 1 s, after the 15 s warm-up, before the shutdown tail; FLAG margin 1 s);
video share = bytes the publisher sent to the clients behind that egress / bytes the egress
transmitted, same time (sent.csv counts packets as they leave the sender, so the share can
exceed 1 by what sits in the queue or is lost; FLAG). One pfifo r1 run per scenario type from
the staggered campaign, plus the synchronized runs.
"""

from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import det_eval as d  # noqa: E402
import det_matrix as dm  # noqa: E402
import grouping_campaign as gc  # noqa: E402
import gt1  # noqa: E402

FOLDERS = {"ip4-not-sync-keyframes-oldGT": "stag (before 2026-11-13; was 2026-11-10_1946_v2)",
           "2026-11-13_2238_ip4-sync-keyframes-oldGT": "sync mini campaign",
           "2026-11-14_0240_night-sync": "sync overnight",
           "2026-11-14_0240_night-stag": "stag overnight (second reps)"}
CALM_MARGIN = 1.0
PKT_BYTES = 1500


def f(x, fmt=".2f"):
    return "-" if x is None else format(x, fmt)


# ── video ────────────────────────────────────────────────────────────────

def video_section():
    from quiclab.config.schema import PublisherConfig, SubscriberConfig
    p, s = PublisherConfig(), SubscriberConfig(connects_to="x")
    gop_frames = p.gop_ms * p.fps // 1000
    print("## 1. Video and sender\n")
    print(f"- qvideo-server over mvfst QUIC, congestion control **{p.cc_algo}**, pacing on (per connection); one QUIC "
          f"connection per client, one unidirectional stream per GOP.")
    print(f"- Ladder {p.ladder_kbps} kb/s; each client takes one fixed rendition (no ABR).")
    print(f"- **{p.fps} fps, GOP {p.gop_ms} ms = {gop_frames} frames, no B-frames, I/P size ratio {p.ip_ratio:g}**, "
          f"per-frame lognormal size noise sigma {p.size_sigma:g} (mean kept), frame header 40 B, seed {p.seed} "
          "(every client of one rendition gets byte-identical frame sizes).")
    print(f"- Frame sizes: GOP bytes = rate / 8 x {p.gop_ms / 1000:g} s; P mean = GOP / (I/P + frames - 1) = GOP / "
          f"{p.ip_ratio + gop_frames - 1:g}; I mean = {p.ip_ratio:g} x P = GOP x {p.ip_ratio:g}/{p.ip_ratio + gop_frames - 1:g} "
          f"(~{100 * p.ip_ratio / (p.ip_ratio + gop_frames - 1):.0f} % of a second of data).")
    print("\n| rate kb/s | GOP kB | P frame kB | keyframe kB |\n|---|---|---|---|")
    for r in p.ladder_kbps:
        g = r * 1000 / 8 * p.gop_ms / 1000
        pm = g / (p.ip_ratio + gop_frames - 1)
        print(f"| {r} | {g / 1000:.1f} | {pm / 1000:.1f} | {p.ip_ratio * pm / 1000:.1f} |")
    print(f"\n- Schedule: frame k is due at start + phase + k / fps, start shared by all clients; keyframes at k % "
          f"{gop_frames} == 0. Frames are handed to QUIC whole when due; an application queue of at most "
          f"{p.send_buffer_ms} ms of media sits in front of QUIC (GOP-aware head drop) and holds frames while QUIC's "
          "unsent bytes exceed the congestion window.")
    print(f"- Client: playback buffer {s.buffer_ms} ms, QUIC PING every 50 ms (keeps ACK receive timestamps flowing), "
          f"stats every {s.stats_ms} ms. Sender logs per client: frames, sent packets, ACKs (RTT, cwnd, BBR state, "
          "OWD from ACK receive timestamps), CC state every 50 ms, OWD per 5 ms send bin.")
    print("- Wire overhead used for load sizing: x1.03 of the video rate (det_matrix.WIRE_OVERHEAD).")
    print("- Keyframe phases: **stag** = the topology files' phase_ms (runs before 2026-11-13); **sync** = every "
          "client phase 0 (grouping_campaign --phase sync, default since 2026-11-13).\n")


# ── topologies ───────────────────────────────────────────────────────────

def topo_section():
    print("## 2. Topologies\n")
    print("Shaping (quiclab/orchestrator/shaping.py, mininet_backend.initial_shaping_commands): **every link direction** "
          "gets an htb rate limit (the link's bandwidth, else the scenario's link_defaults, 100 Mb/s here); a netem stage "
          "when the direction has delay / jitter / loss; an **AQM qdisc only on router egresses** (the router's AQM and "
          "queue limit; per-egress overrides possible). Switches, the publisher and the clients have no AQM. "
          "Congestion happens on router egresses only. Queue delay at the limit = limit x 1500 B / capacity.\n")
    for name, (tf, bf, targets, default) in dm.TOPOLOGIES.items():
        topo = yaml.safe_load((ROOT / "configs/topologies" / tf).read_text())
        base = yaml.safe_load((ROOT / "configs/scenarios" / bf).read_text())
        n = dm.topology_numbers(name)
        ld = base.get("link_defaults", {})
        spec = {(l["from"], l["to"]): l for l in base.get("links", [])}
        routers = base.get("routers", {}) or {}
        print(f"### {name}\n")
        print(f"Files: `configs/topologies/{tf}`, base scenario `configs/scenarios/{bf}`. Bottleneck targets: "
              + ", ".join(f"{t} = {a}->{b}" for t, (a, b, *_) in targets.items()) + f" (default {default}).\n")
        pubs = topo.get("publishers", {})
        sub = topo.get("subscribers", {})
        print(f"- Publisher(s): " + ", ".join(f"{k} ({', '.join(f'{a}={b}' for a, b in (v or {}).items()) or 'defaults'})"
                                         for k, v in pubs.items()))
        print(f"- Routers: {', '.join(topo.get('routers', {}))}; switches: {', '.join(topo.get('switches', {}) or []) or '-'}")
        print(f"- Clients ({len(sub)}): " + ", ".join(f"{k} {(v or {}).get('rate_kbps')} kb/s, phase {(v or {}).get('phase_ms', 0)} ms"
                                                  for k, v in sub.items()))
        print("\n| link | forward Mb/s | forward delay ms | reverse delay ms | stages on forward egress | queue limit (packets / ms) |")
        print("|---|---|---|---|---|---|")
        for link in topo["links"]:
            a, b = link["from"], link["to"]
            s_ = spec.get((a, b), {})
            fw, rv = s_.get("forward") or {}, s_.get("reverse") or {}
            bw = fw.get("bandwidth_mbps", (ld.get("forward") or {}).get("bandwidth_mbps"))
            stages = ["htb"] + (["netem"] if fw.get("delay_ms") or fw.get("jitter_ms") or fw.get("loss_pct") else [])
            q = "-"
            if a in routers:
                r = routers[a] or {}
                lim = ((r.get("egress") or {}).get(b) or {}).get("queue_limit_packets", r.get("queue_limit_packets"))
                stages.append("AQM")
                if lim and bw:
                    q = f"{lim} / {lim * PKT_BYTES * 8 / (bw * 1e6) * 1000:.0f}"
            print(f"| {a} -> {b} | {f(bw, 'g') if bw else '-'} | {fw.get('delay_ms', 0)} | {rv.get('delay_ms', 0)} | "
                  f"{' + '.join(stages)} | {q} |")
        # RTT per client and designed load per bottleneck
        delays = {}
        for (a, b), l in spec.items():
            delays[(a, b)] = ((l.get("forward") or {}).get("delay_ms", 0) or 0) + ((l.get("reverse") or {}).get("delay_ms", 0) or 0)
        print("\nBase RTT per client (sum of forward + reverse link delays on the path; queueing excluded): " + ", ".join(
            f"{s} {sum(delays.get(h, 0) for h in _path(topo, next(iter(pubs)), s)):g} ms" for s in sub))
        print("\n| bottleneck | link | capacity Mb/s | clients behind | video demand on the wire Mb/s | designed calm load |")
        print("|---|---|---|---|---|---|")
        for t, h in n["hops"].items():
            print(f"| {t} | {h['link']['from']}->{h['link']['to']} | {h['base']} | {', '.join(sorted(h['clients']))} | "
                  f"{h['demand']:.2f} | {h['demand'] / h['base']:.2f} |")
        print()


def _path(topo, src, dst):
    adj = defaultdict(set)
    for l in topo["links"]:
        adj[l["from"]].add(l["to"])
        adj[l["to"]].add(l["from"])
    prev, todo = {src: None}, [src]
    for node in todo:
        for x in sorted(adj[node]):
            if x not in prev:
                prev[x] = node
                todo.append(x)
    out, node = [], dst
    while prev.get(node) is not None:
        out.append((prev[node], node))
        node = prev[node]
    return out


# ── scenarios and events ─────────────────────────────────────────────────

def event_stats(k, rtype):
    tmp = Path(tempfile.mkdtemp())
    gc.PHASE = "stag"
    scen, topo, dur = gc.scenario_for(k, rtype, gc.CAMPAIGNS[k]["aqms"][0], 1, tmp / k)
    data = yaml.safe_load(scen.read_text())
    windows = json.loads((tmp / k / "_gen" / f"{gc.run_id(rtype, gc.CAMPAIGNS[k]['aqms'][0], 1)}-windows.json").read_text())
    ev = data.get("events", [])
    kinds = Counter()
    cross = []
    for e in ev:
        if e["type"] == "link":
            if e.get("label", "").startswith("burst u="):
                kinds["capacity drop"] += 1
            elif "loss_pct" in e and e.get("loss_pct"):
                kinds["loss on"] += 1
            elif e.get("label") == "trace":
                kinds["trace step"] += 1
            elif "delay_ms" in e or "jitter_ms" in e:
                kinds["delay / jitter change"] += 1
        elif e["type"] == "flow":
            kinds[f"{e.get('kind')} flow"] += 1
            cross.append(f"{e.get('kind')} {e.get('rate_mbps', e.get('cc', ''))} {e.get('duration_s')} s")
        elif e["type"] == "bursts":
            kinds["udp bursts"] += len(e["bursts"])
            cross += [f"udp {b['rate_mbps']} Mb/s {b['duration_s']} s" for b in e["bursts"][:3]]
        elif e["type"] == "ppbp":
            kinds["ppbp"] += 1
            cross.append(f"ppbp mean {e.get('mean_mbps')} Mb/s, burst {e.get('burst_mbps')} Mb/s, hurst {e.get('hurst')}")
        else:
            kinds[e["type"]] += 1
    targets = Counter(w["target"] for w in windows)
    shared = [w for w in windows if len(w.get("expected", [])) >= 2]
    spans = sorted((w["start"], w["end"]) for w in windows)
    tot, cur = 0.0, None
    for a, b in spans:
        if cur and a <= cur[1]:
            cur[1] = max(cur[1], b)
        else:
            if cur:
                tot += cur[1] - cur[0]
            cur = [a, b]
    if cur:
        tot += cur[1] - cur[0]
    import re
    us = Counter(re.search(r"u=([\d.]+)", e.get("label", "")).group(1) for e in ev if "u=" in e.get("label", ""))
    ds = Counter(re.search(r"d=([\d.]+)", e.get("label", "")).group(1) for e in ev if "d=" in e.get("label", ""))
    return {"duration": dur, "kinds": dict(kinds), "windows": len(windows), "shared": len(shared), "targets": dict(targets),
            "u": dict(us), "d": dict(ds), "congested_s": tot, "cross": cross[:3], "topology": gc.topology_of(k, rtype)}


DESCR = {
    "hier": "cap cells on up | a | b | a+b | a+b@0.5 | a+b@2 | a+up, u x d grid",
    "depth": "cap cells on A | B | C | D | X | Y | root | A+C",
    "depthroot2": "K6 plan; root link x2 capacity (load ~0.33), leaves unchanged",
    "burstlongsplit": "long cap bursts d 10 / 30 / 60 s on up, a, b",
    "mixed": "12 shared cap bursts + 16 private access drops shuffled; sub-d joins at 60 s",
    "indep": "independent timing on up / a / b (exp. gaps mean 30 s, min 5 s), 600 s",
    "uneven": "independent timing on A / B / C, 600 s", "cross": "UDP (u x capacity) or 2 / 4 Cubic flows 4 / 8 s, independent timing, 600 s",
    "trace": "scaled LTE traces on every access link (200 ms steps) + shared cap drops, 600 s",
    "churn": "clients on (exp mean 90 s, min 20) / off (mean 30 s, min 5); shared drops sized to the on clients, 900 s",
    "revasym": "cap bursts; reverse delay per client 5 / 40 / 80 / 120 ms", "revjit10": "cap bursts; reverse jitter 10 ms",
    "revcross": "bursts on the ACK path only (r1 -> r0 at 10 Mb/s)", "revcrossmix": "ACK-path bursts mixed with forward bursts",
    "hierjit5": "K1 plan + forward normal access jitter 5 ms (order kept)", "hierjit10": "K1 plan + jitter 10 ms",
    "hierjit20": "K1 plan + jitter 20 ms", "hiersamephase": "K1 plan, b clients on a's phases (stag only)",
    "hierrandphase": "K1 plan, random phases (stag only)",
    "calm030": "no events, capacity sized to load 0.30", "calm065": "no events, base capacity (load 0.65)",
    "calm090": "no events, capacity sized to load 0.90", "calmcbr090": "constant-rate UDP filling the bottleneck to load 0.90",
    "randloss": "random loss 0.5 / 1 / 2 % on the publisher link, 10 s each, 3x",
    "calmsplit": "calm065 on split", "calmtree8": "calm065 on tree8", "calmuneven": "calm065 on uneven",
    "burstcap": "cap u 1.1 / 1.3 / 2.0 x d 1 / 2 / 4 s, 2x", "burstudp": "UDP cross traffic at u x capacity - demand, same grid",
    "bursttiny": "cap u 1.3 / 2.0 x d 0.2 / 0.5 s, 5x", "ramp": "capacity ramp in 2 s steps to peak u 1.05 / 1.1 / 1.2, 4x",
    "tcpcubic": "Cubic bulk flow 2 / 4 / 8 s, 5x", "tcpbbr": "BBR bulk flow 2 / 4 / 8 s, 5x",
    "ppbp": "self-similar PPBP UDP (Hurst 0.8, 2 Mb/s bursts of 0.5 s mean), mean load ~0.95", "burstlong": "cap d 10 / 30 / 60 s",
    "burstcaplowrtt": "burstcap, all delays x0.25", "burstcaphighrtt": "burstcap, all delays x2",
    "burstcapq05": "burstcap, queue limits x0.5", "burstcapq15": "burstcap, queue limits x1.5", "burstcapq20": "burstcap, queue limits x2",
    "revjit5": "burstcap + reverse jitter 5 ms", "revjit20": "burstcap + reverse jitter 20 ms",
    "fps15": "burstcap, publisher 15 fps", "fps60": "burstcap, publisher 60 fps",
    "bw1": "burstcap, 4 x 1000 kb/s", "bw8": "burstcap, 4 x 8000 kb/s", "bwmix": "burstcap, mixed bitrates",
    "gapfast": "burstcap grid, gaps 2-5 s", "gapslow": "burstcap grid, gaps 45-75 s",
    "indepfast": "split, independent timing mean 10 s, 600 s", "indepslow": "split, independent timing mean 60 s, 600 s",
}


def scenario_section():
    print("## 3. Scenarios and congestion events\n")
    print("Common timing: 15 s warm-up, 10-15 s random gaps between stimuli (unless the type says otherwise), 10 s tail. "
          "u = overload factor: a capacity drop sets the target link to video demand / u; UDP cross traffic sends "
          "u x capacity - demand. Same seed (= rep) on every AQM. Event counts below are for rep 1 (seed 1); other seeds "
          "reorder the same cells, so counts and durations stay within a few seconds.\n")
    print("| campaign | type | topology | clients | what happens | duration s | event kinds (count) | truth windows (shared >= 2 clients) | "
          "windows per target | u values (count) | d values s (count) | stimulated time s | cross traffic examples |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, c in gc.CAMPAIGNS.items():
        for t in c["types"]:
            try:
                s = event_stats(k, t)
            except Exception as e:   # noqa: BLE001
                print(f"| {k} | {t} | - | - | {DESCR.get(t, '')} | error {type(e).__name__} | | | | | | | |")
                continue
            topo = yaml.safe_load((ROOT / "configs/topologies" / dm.TOPOLOGIES[s["topology"]][0]).read_text())
            nsub = len(topo["subscribers"])
            print(f"| {k} | {t} | {s['topology']} | {nsub} | {DESCR.get(t, '')} | {s['duration']:.0f} | "
                  + ", ".join(f"{a} {b}" for a, b in s["kinds"].items()) + f" | {s['windows']} ({s['shared']}) | "
                  + ", ".join(f"{a} {b}" for a, b in s["targets"].items()) + " | "
                  + ", ".join(f"{a}: {b}" for a, b in sorted(s["u"].items())) + " | "
                  + ", ".join(f"{a}: {b}" for a, b in sorted(s["d"].items(), key=lambda x: float(x[0]))) + f" | "
                  f"{s['congested_s']:.0f} | {'; '.join(s['cross']) or '-'} |")
    print()


# ── AQMs ─────────────────────────────────────────────────────────────────

def aqm_section():
    print("## 4. AQMs\n")
    print("| AQM | qdisc as configured | notes |\n|---|---|---|")
    print("| pfifo | `pfifo limit N` | tail drop, no ECN |")
    print("| red | `red ... bandwidth <capacity> ecn`; min ~15 ms / max ~45 ms of the smallest bottleneck's capacity (capped at 0.75 x limit) | det_matrix.red_thresholds |")
    print("| pie | `pie limit N ecn` | kernel defaults (target 15 ms) |")
    print("| codel | `codel limit N ecn` | kernel defaults (target 5 ms, interval 100 ms) |")
    print("| fq_codel | `fq_codel limit N ecn` | per-client flow pinned to a fixed class (per-flow counters since 2026-11-11) |")
    print("| cake | `cake unlimited besteffort` | htb shapes, cake only queues; per-client flow pinned |")
    print("| mixab | r1 pfifo; r2 egress to switch-a pfifo, to switch-b fq_codel | K1 only |")
    print("\nN = the egress queue limit of the topology's base file (section 2), scaled by queue_scale in M2 q05 / q15 / q20.\n")


# ── measured calm load ───────────────────────────────────────────────────

def calm_load(rd: Path):
    try:
        run = d.Run(rd)
        windows = json.loads((rd / "grouping" / "windows.json").read_text()) if (rd / "grouping" / "windows.json").exists() else []
        busy = [(w["start"] - CALM_MARGIN, w["end"] + CALM_MARGIN) for w in windows]

        def calm(t):
            ok = (t >= d.WARMUP_S) & (t <= run.duration - d.SHUTDOWN_S)
            for a, b in busy:
                ok &= ~((t >= a) & (t <= b))
            return ok
        caps = d.capacity_series(run)
        sent = {}
        for s in run.subs:
            p = run.sender_file(s, "sent")
            if p.exists():
                x = pd.read_csv(p, usecols=["send_mono_us", "bytes"])
                sent[s] = (np.array([run.t_mono_us(v) for v in x.send_mono_us]), x.bytes.values.astype(float))
        out = {}
        for hop, csv in gt1.router_egresses(run):
            r = pd.read_csv(csv, usecols=["timestamp_mono_ns", "interval_ns", "transmitted_bytes"])
            t = np.array([run.t_mono_us(v / 1000) for v in r.timestamp_mono_ns])
            iv = r.interval_ns.values / 1e9
            tx = r.transmitted_bytes.values.astype(float)
            cap = np.array([d.value_at(caps[hop], v) for v in t]) * 1e6 / 8
            ok = calm(t) & (iv > 0)
            if not ok.any() or not np.sum(cap[ok] * iv[ok]):
                continue
            load = float(np.sum(tx[ok]) / np.sum(cap[ok] * iv[ok]))
            if load < 0.02:
                continue
            behind = [s for s in run.subs if hop in set(d.path_hops(run, run.pub, s))]
            vb = 0.0
            for s in behind:
                if s in sent:
                    ts_, b_ = sent[s]
                    vb += float(np.sum(b_[calm(ts_)]))
            # bytes over the same calm seconds: the egress rows cover [t - iv, t]
            share = vb / float(np.sum(tx[ok])) if np.sum(tx[ok]) else None
            out[f"{hop[0]}->{hop[1]}"] = {"load": round(load, 3), "video_share": round(share, 3) if share else None,
                                          "clients": len(behind)}
        return {"folder": rd.parent.parent.name, "campaign": rd.parent.name, "run": rd.name, "egress": out}
    except Exception as e:   # noqa: BLE001
        return {"folder": rd.parent.parent.name, "campaign": rd.parent.name, "run": rd.name, "error": repr(e)}


def calm_runs():
    out = []
    old = ROOT / ".runs/ip4-not-sync-keyframes-oldGT"
    for k in sorted(old.iterdir()):
        if k.is_dir() and not k.name.startswith("N"):
            seen = set()
            for rd in sorted(k.glob("grp-*-pfifo-r1")):
                t = rd.name.split("-")[1]
                if t not in seen:
                    seen.add(t)
                    out.append(rd)
    for fold in ("2026-11-13_2238_ip4-sync-keyframes-oldGT", "2026-11-14_0240_night-sync"):
        base = ROOT / ".runs" / fold
        if base.exists():
            for k in sorted(base.iterdir()):
                if k.is_dir():
                    out += sorted(rd for rd in k.glob("grp-*-r1") if rd.is_dir())
    return out


def load_section():
    print("## 5. Calm load per bottleneck (measured)\n")
    print("Load = egress transmitted bytes / capacity over calm time (outside stimulus windows +- 1 s, after warm-up). "
          "Video share = bytes the publisher sent to the clients behind the egress / bytes the egress transmitted, same "
          "time (can be slightly above 1: packets still queued or lost). Designed value 0.65 unless the scenario "
          "changes it (calm030 / calm090 / calmcbr090, bw*, K6R root). Only egresses with load >= 0.02 are listed; "
          "sub-ctrl's own egress included.\n")
    with Pool(12) as pool:
        rows = pool.map(calm_load, calm_runs())
    print("Reading the video share: the publisher's sent.csv counts QUIC packet bytes while the router counts IP / UDP "
          "headers too, so an egress that carries only our video shows ~0.96. Values clearly below that are cross "
          "traffic: calmcbr090 (constant-rate UDP to load 0.9) and ppbp (PPBP UDP, total load ~0.95). Burst-type cross "
          "traffic (burstudp, tcp*, N3) runs only inside stimulus windows, which are excluded here. The ramp type keeps "
          "sub-1 steps (load 0.9-0.95) outside its windows, hence its higher calm load. sub-ctrl's egress carries only "
          "its 2500 kb/s stream (load ~0.05 of 50 Mb/s).\n")
    print("| folder | campaign | run | egress: load (video share) |\n|---|---|---|---|")
    for r in rows:
        if "error" in r:
            print(f"| {r['folder']} | {r['campaign']} | {r['run']} | error {r['error'][:80]} |")
            continue
        print(f"| {FOLDERS.get(r['folder'], r['folder']).split(' (')[0]} | {r['campaign']} | {r['run']} | " + "; ".join(
            f"{h} {v['load']:.2f} ({f(v['video_share'])})" for h, v in sorted(r["egress"].items())) + " |")
    print()


# ── campaign matrix ──────────────────────────────────────────────────────

def matrix_section():
    print("## 6. Campaign matrix (what exists in each run folder)\n")
    print("Per folder and campaign: types x AQMs with the reps present, keyframe phase, run duration (plan.json). "
          "Durations are emulated seconds; wall clock was ~1.04-1.2 x.\n")
    for fold, label in FOLDERS.items():
        base = ROOT / ".runs" / fold
        if not base.exists():
            continue
        print(f"### `.runs/{fold}`: {label}\n")
        print("| campaign | type | AQM: reps | phase | duration s (r1) | runs |\n|---|---|---|---|---|---|")
        total, total_s = 0, 0.0
        for k in sorted(base.iterdir()):
            if not k.is_dir():
                continue
            by = defaultdict(lambda: defaultdict(list))
            info = {}
            for rd in sorted(k.glob("grp-*")):
                if not rd.is_dir():
                    continue
                parts = rd.name.split("-")
                t, a, rep = parts[1], parts[-2], rd.name.rsplit("-r", 1)[1]
                by[t][a].append(rep)
                pj = rd / "grouping" / "plan.json"
                if pj.exists():
                    p = json.loads(pj.read_text())
                    total_s += p["duration_s"]
                    info.setdefault(t, (p.get("phase", "stag"), p["duration_s"]))
                total += 1
            for t in sorted(by):
                ph, dur = info.get(t, ("?", None))
                n = sum(len(v) for v in by[t].values())
                print(f"| {k.name} | {t} | " + ", ".join(f"{a}: r{','.join(sorted(v, key=int))}" for a, v in sorted(by[t].items()))
                      + f" | {ph} | {f(dur, '.0f')} | {n} |")
        print(f"\nTotal: {total} runs, {total_s / 3600:.1f} h of emulation.\n")
    print("Held-out N1-N5 are in the staggered folder only and stay closed (infra checks only). "
          "Archived: `.runs/old/2026-11-10_1946_v2-aggregate-gt1` (fq_codel / cake / mixab before per-flow counters), "
          "`.runs/old/ip4`, `.runs/old/ip8` (earlier campaigns).\n")


def overview_section():
    print("## 0. Testbed in one page\n")
    print("- Emulation: Mininet. Nodes: one publisher (`pub`, qvideo-server), routers (queues), switches (fan-out only), "
          "clients (qvideo-client), plus iperf3 / PPBP endpoints for cross traffic on named routes. Link changes "
          "(capacity, delay, jitter, loss, AQM) are applied live with `tc ... change` at the planned times; the applied "
          "time of every event is in the run's `events.csv`.")
    print("- Every topology has the control client `sub-ctrl` (2500 kb/s) on its own router egress next to the "
          "publisher: it never shares a congested queue and must never be grouped.")
    print("- Router metrics: every router egress every 25 ms (queue packets and bytes, transmitted bytes, drops, ECN "
          "marks); split, tree8 and uneven also record the queue every 5 ms; fq_codel / cake add per-client class "
          "counters (since 2026-11-11).")
    print("- Truths used in the reports: **GT1** = CoDel-style standing queue on a router egress (target 5 ms, "
          "interval 150 ms); **GT2** = demand >= capacity; **GT3** = the client's own OWD + loss episodes with a queue "
          "on its path. Grouping truth = the topology's leaf sets (clients behind the same leaf egress). The detector "
          "is the frozen Shadow v2 on OWD ticks (v2-owd); grouping methods are ECG v1.2 (onset co-occurrence, "
          "delta 150 ms) and the template-based h3 of steps 3 / 4.")
    print("- Every run folder holds the resolved `topology.yaml` and `scenario.yaml` (every event with its time), "
          "`grouping/plan.json` (campaign, type, AQM, rep = seed, phase, keyframe phases, duration), "
          "`grouping/windows.json` (stimulus windows and expected clients), `grouping/keyframe-spread.json` "
          "(sync-era runs), sender / client logs and router metrics.\n")


def main():
    print("# Scenario catalog\n")
    print("Generated by `scripts/scenario_catalog.py` from the configuration files, the planners and the run folders "
          "(read-only). Do not edit by hand; rerun the script after a change.\n")
    print("Contents: 0 testbed, 1 video and sender, 2 topologies (links, shaping stages, capacities, delays, queue "
          "limits, RTTs, designed load), 3 scenarios and congestion events, 4 AQMs, 5 measured calm load and video "
          "share, 6 campaign matrix.\n")
    overview_section()
    video_section()
    topo_section()
    scenario_section()
    aqm_section()
    load_section()
    matrix_section()


if __name__ == "__main__":
    main()
