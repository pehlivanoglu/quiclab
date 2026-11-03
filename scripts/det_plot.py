#!/usr/bin/env python3
"""Timeline figures of what the network did and what the detectors did.

    python3 scripts/det_plot.py .runs/<run> [...]     # after det_eval.py score

Per run, into <run>/detector/plots/:
  overview.png      bottleneck capacity / offered / sent rates, router queue
                    delay, drops + ECN marks, and per client the truth episodes
                    and the shadow alarms.
  <client>.png      one client end to end: model truth u(t), alarms of every
                    detector (shadow, its verified level, GCC, BBR), the shadow
                    components (deficit, gradient, offered, excess, backlog,
                    loss), the inputs behind them (queuing delay seen by the
                    sender vs measured at the router, delivery vs BBR estimate
                    vs demand, deficit / offered ratios, delay trend vs GCC
                    threshold, sender backlog), router drops and the player.

The shadow detector is replayed with det_eval.TUNED (the scored setting) into a
temporary directory; its per-ACK state is not kept on disk.
"""

from __future__ import annotations

import math
import statistics
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402

# Reference palette (dataviz skill references/palette.md), one hue per
# detector in every figure, same assignment as moqlab's shadow report.
INK, INK_2, MUTED, GRID, SURFACE = "#1f1f1e", "#5f5e58", "#a3a29a", "#e6e5df", "#fcfcfb"
SHADOW, VERIFIED, BBR, GCC = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
ROUTER, CLIENT, ALARM_FP = "#6250d6", "#e87ba4", "#e34948"
CONGESTED, AMBIGUOUS = "#f6c8c8", "#ebeae5"
BIN_S = 0.1


# ── data ─────────────────────────────────────────────────────────────────

def binned(ts: list[float], vs: list[float], how=statistics.median) -> tuple[list[float], list[float]]:
    """Per-ACK series to BIN_S bins (median by default) so plots stay legible."""
    bins = defaultdict(list)
    for t, v in zip(ts, vs):
        if v is not None and not math.isnan(v):
            bins[int(t / BIN_S)].append(v)
    xs, ys, last = [], [], None
    for k in sorted(bins):
        if last is not None and k - last > 3:  # break the line over gaps instead of bridging them
            xs.append((last + 1) * BIN_S)
            ys.append(math.nan)
        xs.append(k * BIN_S)
        ys.append(how(bins[k]))
        last = k
    return xs, ys


def num(text: str) -> float:
    return float(text) if text not in ("", "nan", "null") else math.nan


def spans(ts: list[float], flags: list[bool]) -> list[tuple[float, float]]:
    out, start = [], None
    for t, f in zip(ts, flags):
        if f and start is None:
            start = t
        elif not f and start is not None:
            out.append((start, t))
            start = None
    if start is not None and ts:
        out.append((start, ts[-1]))
    return out


def on_off(events: list[dict], sid: str, variant: str, on: str, off: str, end: float) -> list[tuple[float, float]]:
    out, start = [], None
    for e in events:
        if e["subscriber"] != sid or e["variant"] != variant:
            continue
        if e["event"] == on and start is None:
            start = e["t"]
        elif e["event"] == off and start is not None:
            out.append((start, e["t"]))
            start = None
    if start is not None:
        out.append((start, end))
    return out


# ── drawing helpers ──────────────────────────────────────────────────────

def style(ax, ylabel: str) -> None:
    ax.set_facecolor(SURFACE)
    ax.set_ylabel(ylabel, color=INK_2, fontsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.tick_params(colors=INK_2, labelsize=7, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)


def legend(ax) -> None:
    if ax.get_legend_handles_labels()[0]:
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncols=6, fontsize=7, frameon=False,
                  handlelength=1.5, borderaxespad=0.2, labelcolor=INK)


def shade_truth(ax, bands: list[tuple[float, str]], episodes: list[dict], sid: str) -> None:
    for a, b in spans([t for t, _ in bands], [x == "ambiguous" for _, x in bands]):
        ax.axvspan(a, b, color=AMBIGUOUS, linewidth=0, zorder=0)
    for e in episodes:
        if e["subscriber"] == sid:
            ax.axvspan(e["t0"], e["end"], color=CONGESTED, linewidth=0, zorder=0,
                       hatch=None if e["scored"] else "///", fill=bool(e["scored"]))


def mark_bursts(ax, bursts: list[dict], label: bool = False) -> None:
    """Injected bursts (burst benchmark): start = exact ground truth onset."""
    for i, b in enumerate(bursts):
        ax.axvline(b["start"], color=INK, linewidth=0.9, zorder=3,
                   label="burst start (truth)" if label and i == 0 else None)
        ax.axvline(b["end"], color=INK, linewidth=0.6, linestyle=":", zorder=3)
        if label:
            ax.annotate(f"u{b['u_cell']:g} {b['d_cell']}s", (b["start"], 1), xycoords=("data", "axes fraction"),
                        xytext=(2, -10), textcoords="offset points", fontsize=6, color=INK_2)


def lanes(ax, rows: list[tuple[str, str, list[tuple[float, float]], list[float]]]) -> None:
    """One labelled row per item: spans as bars, ticks as markers."""
    for i, (label, color, span_list, ticks) in enumerate(rows):
        y = len(rows) - 1 - i
        for a, b in span_list:
            ax.broken_barh([(a, max(b - a, 0.05))], (y - 0.3, 0.6), color=color, linewidth=0)
        if ticks:
            ax.plot(ticks, [y] * len(ticks), "|", color=color, markersize=10, markeredgewidth=2)
    ax.set_yticks(range(len(rows)), [r[0] for r in reversed(rows)], fontsize=7, color=INK)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.grid(False)


# ── figures ──────────────────────────────────────────────────────────────

def client_figure(run: d.Run, sid: str, ctx: dict, out: Path) -> None:
    s = ctx["samples"].get(sid)
    if not s:
        return
    t = [run.t_mono_us(int(x)) for x in s["mono_us"]]
    end = run.duration
    alarms = [a for a in ctx["alarms"] if a["subscriber"] == sid]
    hop, router = ctx["bottleneck"][sid]
    fig, axes = plt.subplots(10, 1, figsize=(14, 24), sharex=True,
                             gridspec_kw={"height_ratios": [1.2, 1.1, 1.6, 1.2, 1.2, 1.1, 1.1, 1.1, 0.8, 1]})
    fig.patch.set_facecolor(SURFACE)

    # 1. model truth
    ax = axes[0]
    style(ax, "utilization u")
    shade_truth(ax, ctx["bands"][sid], ctx["episodes"], sid)
    ax.plot([b for b, _ in ctx["bands"][sid]], ctx["u"][sid], color=INK, linewidth=1.2, label="truth u(t) (model)")
    ax.axhline(d.CONGESTED_U, color=MUTED, linewidth=0.8, linestyle="--")
    ax.axhline(d.CLEAR_U, color=MUTED, linewidth=0.8, linestyle=":")
    ax.set_ylim(0, max(2.2, max(ctx["u"][sid] or [0]) * 1.05))
    mark_bursts(ax, ctx["bursts"], label=True)
    legend(ax)

    # 2. detector alarms
    ax = axes[1]
    style(ax, "")
    starts = defaultdict(lambda: defaultdict(list))
    for a in alarms:
        starts[a["detector"]][a["label"]].append(float(a["t"]))
    rows = [
        ("shadow pre-signal", SHADOW, on_off(ctx["events"], sid, "tuned:full", "pre_signal_on", "pre_signal_off", end), []),
        ("shadow verified", VERIFIED, [], [e["t"] for e in ctx["events"] if e["subscriber"] == sid
                                           and e["variant"] == "tuned:full" and e["event"] == "verified_on"]),
        ("GCC overuse", GCC, on_off(ctx["events"], sid, "gcc", "pre_signal_on", "pre_signal_off", end), []),
        ("BBR estimate drop", BBR, [], [e["t"] for e in ctx["events"] if e["subscriber"] == sid
                                        and e["variant"] == "" and e["event"] == "bbr_bw_drop"]),
    ]
    lanes(ax, rows)
    names = {"shadow pre-signal": "shadow", "shadow verified": "shadow_verified",
             "GCC overuse": "gcc", "BBR estimate drop": "bbr"}
    for i, (label, *_rest) in enumerate(rows):
        fp = starts[names[label]]["fp"]
        if fp:
            ax.plot(fp, [len(rows) - 1 - i] * len(fp), "x", color=ALARM_FP, markersize=8, markeredgewidth=2,
                    label="false alarm (clear band)" if i == 0 or not ax.get_legend_handles_labels()[0] else None)
    shade_truth(ax, ctx["bands"][sid], ctx["episodes"], sid)
    mark_bursts(ax, ctx["bursts"])
    legend(ax)

    # 3. shadow components
    ax = axes[2]
    style(ax, "")
    flag = lambda col: [num(v) > 0 for v in s[col]]  # noqa: E731
    comp_events = lambda name: [e["t"] for e in ctx["events"] if e["subscriber"] == sid  # noqa: E731
                                and e["variant"] == "tuned:full" and e["event"] == name]
    lanes(ax, [
        ("deficit", SHADOW, spans(t, flag("deficit_pre")), []),
        ("delay gradient", SHADOW, spans(t, flag("gradient_pre")), []),
        ("offered load", SHADOW, spans(t, flag("offered_pre")), []),
        ("excess inflight", SHADOW, spans(t, flag("excess_high")), []),
        ("backlog (onsets)", SHADOW, [], comp_events("backlog_onset")),
        ("loss", SHADOW, [], [tt for tt, v in zip(t, s["newly_lost"]) if num(v) > 0]),
        ("masked (startup/probe)", MUTED, spans(t, [v not in ("", "0", "none") for v in s["mask"]]), []),
    ])
    shade_truth(ax, ctx["bands"][sid], ctx["episodes"], sid)

    # 4. queuing delay: sender's view vs router measurement
    ax = axes[3]
    style(ax, "queuing delay (ms)")
    if router:
        r = ctx["router"][router]
        ax.plot(*binned(r["t"], r["queue_ms"], max), color=ROUTER, linewidth=2.0, alpha=0.55,
                label=f"router {hop[0]}->{hop[1]}: backlog / capacity (all flows)")
    ax.plot(*binned(t, [num(v) for v in s["queue_delay_ms"]]), color=SHADOW, linewidth=0.9,
            label="sender: RTT - min RTT")
    legend(ax)

    # 5. rates
    ax = axes[4]
    style(ax, "Mb/s")
    ax.plot(*binned(t, [num(v) / 1e6 for v in s["ack_bps"]]), color=SHADOW, linewidth=1.0, label="delivery rate")
    ax.plot(*binned(t, [num(v) / 1e6 for v in s["bbr_bw_bps"]]), color=BBR, linewidth=1.2, label="BBR bandwidth estimate")
    ax.axhline(ctx["demand"][sid] / 1e6, color=INK_2, linewidth=0.8, linestyle="--", label="video demand")
    legend(ax)

    # 6. deficit / offered ratios
    ax = axes[5]
    style(ax, "ratio")
    ax.plot(*binned(t, [num(v) for v in s["ratio"]]), color=SHADOW, linewidth=1.0, label="delivery / BBR estimate")
    ax.plot(*binned(t, [num(v) for v in s["offered_ratio"]]), color=VERIFIED, linewidth=1.0,
            label="delivered / offered (1 s)")
    ax.axhline(0.8, color=MUTED, linewidth=0.8, linestyle="--", label="threshold 0.8")
    ax.set_ylim(0, 1.6)
    legend(ax)

    # 7. delay trend
    ax = axes[6]
    style(ax, "trend")
    ax.plot(*binned(t, [num(v) for v in s["residual_trend"]]), color=SHADOW, linewidth=1.0, label="residual delay trend")
    ax.plot(*binned(t, [num(v) for v in s["gamma"]]), color=GCC, linewidth=1.0, label="GCC threshold gamma")
    legend(ax)

    # 8. sender backlog
    ax = axes[7]
    style(ax, "kB")
    ax.plot(*binned(t, [num(v) / 1e3 for v in s["stream_buffer_bytes"]], max), color=SHADOW, linewidth=1.0,
            label="sender backlog (frame queue + QUIC unsent)")
    ax.plot(*binned(t, [num(v) / 1e3 for v in s["inflight_bytes"]], max), color=BBR, linewidth=1.0, label="in flight")
    legend(ax)

    # 9. router drops / marks
    ax = axes[8]
    style(ax, "pkts / 100 ms")
    if router:
        r = ctx["router"][router]
        ax.plot(*binned(r["t"], [a + b for a, b in zip(r["drops"], r["marks"])], sum), color=ROUTER,
                linewidth=1.0, drawstyle="steps-post", label="router drops + ECN marks (all flows)")
    legend(ax)

    # 10. player
    ax = axes[9]
    style(ax, "buffer (ms)")
    play = ctx["playback"].get(sid, [])
    if play:
        pt = [run.t_unix_us(int(x["t_us"])) for x in play]
        ax.plot(pt, [float(x["buffer_ms"]) for x in play], color=CLIENT, linewidth=1.0, label="player buffer")
        stalls = [tt for tt, a, b in zip(pt[1:], play, play[1:]) if int(b["stalls"]) > int(a["stalls"])]
        ax.plot(stalls, [0] * len(stalls), "v", color=ALARM_FP, markersize=8, label="stall")
    legend(ax)
    ax.set_xlabel("run time (s)", color=INK_2, fontsize=8)
    ax.set_xlim(0, end)

    fig.suptitle(f"{run.path.name} — {sid} ({ctx['demand'][sid] / 1e6:.1f} Mb/s, bottleneck {hop[0]}->{hop[1]}, "
                 f"{run.aqm}). Red = congested truth episode (hatched: minor, not scored); "
                 f"grey = ambiguous band (not scored)", fontsize=9, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(out / f"{sid}.png", dpi=110, facecolor=SURFACE)
    plt.close(fig)


def overview_figure(run: d.Run, ctx: dict, out: Path) -> None:
    routers = sorted({p for p in ctx["bottleneck_files"] if p})
    subs = [s for s in run.subs if s in ctx["samples"]]
    fig, axes = plt.subplots(3 + 1, 1, figsize=(14, 10), sharex=True,
                             gridspec_kw={"height_ratios": [1.2, 1, 0.8, 0.5 * len(subs) + 0.6]})
    fig.patch.set_facecolor(SURFACE)
    for path in routers[:1]:
        r = ctx["router"][path]
        ax = axes[0]
        style(ax, "Mb/s")
        ax.plot(*binned(r["t"], r["offered_mbps"], statistics.mean), color=INK_2, linewidth=1.0, label="offered to the queue")
        ax.plot(*binned(r["t"], r["sent_mbps"], statistics.mean), color=ROUTER, linewidth=1.0, label="sent")
        ax.plot(r["t"], r["cap_mbps"], color=INK, linewidth=1.4, drawstyle="steps-post", label="capacity")
        legend(ax)
        ax = axes[1]
        style(ax, "queue delay (ms)")
        ax.plot(*binned(r["t"], r["queue_ms"], max), color=ROUTER, linewidth=1.0, label=f"{path.stem} backlog / capacity")
        legend(ax)
        ax = axes[2]
        style(ax, "pkts / 100 ms")
        ax.plot(*binned(r["t"], r["drops"], sum), color=ALARM_FP, linewidth=1.0, drawstyle="steps-post", label="drops")
        ax.plot(*binned(r["t"], r["marks"], sum), color=GCC, linewidth=1.0, drawstyle="steps-post", label="ECN marks")
        legend(ax)
    ax = axes[3]
    style(ax, "")
    rows = []
    for sid in subs:
        rows.append((f"{sid} shadow", SHADOW,
                     on_off(ctx["events"], sid, "tuned:full", "pre_signal_on", "pre_signal_off", run.duration), []))
    lanes(ax, rows)
    for i, sid in enumerate(subs):
        y = len(subs) - 1 - i
        for e in ctx["episodes"]:
            if e["subscriber"] == sid:
                ax.add_patch(plt.Rectangle((e["t0"], y - 0.45), e["end"] - e["t0"], 0.9, zorder=0, linewidth=0,
                                           color=CONGESTED, fill=bool(e["scored"]), hatch=None if e["scored"] else "///"))
        fp = [float(a["t"]) for a in ctx["alarms"] if a["subscriber"] == sid and a["detector"] == "shadow"
              and a["label"] == "fp"]
        ax.plot(fp, [y] * len(fp), "x", color=ALARM_FP, markersize=8, markeredgewidth=2)
    for a in axes:
        mark_bursts(a, ctx["bursts"])
    ax.set_xlabel("run time (s)", color=INK_2, fontsize=8)
    ax.set_xlim(0, run.duration)
    fig.suptitle(f"{run.path.name} ({run.aqm}): bottleneck and shadow alarms per client. Red = congested truth "
                 f"episode (hatched: minor); x = false alarm", fontsize=9, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out / "overview.png", dpi=110, facecolor=SURFACE)
    plt.close(fig)


def plot(run_dir: Path) -> None:
    run = d.Run(run_dir)
    det = run_dir / "detector"
    if not (det / "alarms.csv").exists():
        sys.exit(f"{run_dir}: score it first (scripts/det_eval.py score)")
    episodes = [{**e, "t0": float(e["t0"]), "end": float(e["end"]), "scored": int(e["scored"])}
                for e in d.rows(det / "truth.csv")]
    _, bands = d.build_truth(run)
    demand = {s: d.demand_bps(run, s) for s in run.subs}
    caps, cross = d.capacity_series(run), d.cross_series(run)
    paths = {s: d.path_hops(run, run.pub, s) for s in run.subs}
    u = defaultdict(list)
    for t, _ in bands[run.subs[0]]:
        for s, x in d.utilization(run, demand, caps, cross, paths, t).items():
            u[s].append(min(x, 5.0))
    with tempfile.TemporaryDirectory() as tmp:
        events = [{**e, "variant": f"tuned:{e['variant']}"} if e["variant"] else e
                  for e in d.replay(run, d.TUNED, samples_to=Path(tmp))]
        events += [e for e in d.replay(run, d.PARAMS) if e["variant"] == "gcc"]
        samples = {}
        for f in Path(tmp).glob("*.csv"):
            rows = d.rows(f)
            samples[f.stem] = {k: [r[k] for r in rows] for k in rows[0]} if rows else {}
    bottlenecks = {s: d.bottleneck(run, s, caps) for s in run.subs}
    files = {p for _, p in bottlenecks.values() if p}
    ctx = {
        "episodes": episodes, "bands": bands, "u": u, "demand": demand, "events": events,
        "alarms": d.rows(det / "alarms.csv"), "samples": samples, "bottleneck": bottlenecks,
        "bottleneck_files": files, "bursts": d.burst_truth(run),
        "router": {p: d.router_series(run, p, caps[bottlenecks[next(s for s in run.subs if bottlenecks[s][1] == p)][0]])
                   for p in files},
        "playback": {s: d.rows(run.path / "clients" / f"{s}-playback.csv") for s in run.subs
                     if (run.path / "clients" / f"{s}-playback.csv").exists()},
    }
    out = det / "plots"
    out.mkdir(parents=True, exist_ok=True)
    overview_figure(run, ctx, out)
    for sid in run.subs:
        client_figure(run, sid, ctx, out)
    print(f"{run_dir.name}: plots in {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        plot(Path(arg))
