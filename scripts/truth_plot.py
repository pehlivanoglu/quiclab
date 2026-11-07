#!/usr/bin/env python3
"""Ground-truth timelines: router queue and load next to the three truths and the
shadow detector, to check the truths by eye.

    python3 scripts/truth_plot.py .runs/<run> [...]          # one or more runs
    python3 scripts/truth_plot.py --campaign .runs/<campaign> # every run + <campaign>/truth-plots.html

Per run, into <run>/truth/plots/:
  overview.png   whole run: capacity, offered and sent rate, queue delay (max per
                 100 ms), drops, then lanes: injected events; per router egress
                 GT1 (persistent queue, scripts/gt1.py) and GT2 (demand >= capacity,
                 scripts/gt2.py); per client GT3 (its own OWD / loss, scripts/gt3.py)
                 and the shadow alarm (det_eval.TUNED replay, pre_signal on/off).
  zoom-NN.png    the same panels at sample resolution (every 25 ms sample, and
                 the 5 ms queue CSV where recorded) in windows around each
                 injected event, or every 30 s on runs without events; three
                 windows per page.

Every truth uses its default parameters. Hops shown: router egresses with a GT1
or GT2 episode, else the shared bottleneck. Only the shadow is replayed.
"""

from __future__ import annotations

import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import det_eval as d  # noqa: E402
import det_plot as dp  # noqa: E402
import gt1  # noqa: E402
import gt2  # noqa: E402
import gt3  # noqa: E402

GT1_COLOR, GT2_COLOR, GT3_COLOR = "#6250d6", "#0e8f8f", "#e34948"
QUEUE_COLORS = ("#6250d6", "#1baf7a", "#eda100", "#e87ba4")
WINDOW_S, LEAD_S, TAIL_S, CALM_STEP_S = 8.0, 1.5, 2.5, 30.0
PER_PAGE = 3


def gather(run: d.Run) -> dict:
    caps = d.capacity_series(run)
    eps1 = gt1.run_episodes(run, gt1.Params())
    egresses = dict(gt1.router_egresses(run))
    eps2 = gt2.run_episodes(run, gt2.Params())
    hops = sorted({e["hop"] for e in eps1} | {e["queue_id"] for e in eps2})
    if not hops:
        shared = d.leaf_queues(run.topology, {s: d.path_hops(run, run.pub, s) for s in run.subs})
        hops = sorted({h for h in shared.values() if h})
    series = {}
    for hop in hops:
        key = tuple(hop.split("->"))
        if key not in egresses:
            continue
        csv = egresses[key]
        t, backlog, tx, drops = gt1._samples(run.path, csv)
        cap = np.array([d.value_at(caps[key], x) for x in t]) * 1e6
        fine = csv.with_name(csv.stem + "-queue.csv")
        f = None
        if fine.exists():
            ft, fb, _, _ = gt1._samples(run.path, fine)
            f = (ft, fb * 8 / np.array([d.value_at(caps[key], x) for x in ft]) / 1e6 * 1000)
        dt = np.diff(t, prepend=t[0] - 0.025)
        offered = gt2._samples(run.path, csv)[1]
        series[hop] = {"t": t, "q_ms": backlog * 8 / cap * 1000, "drops": drops, "cap": cap / 1e6,
                       "sent": (tx * 8 / dt / 1e6) if tx is not None else None, "fine": f,
                       "offered": offered * 8 / dt / 1e6}
    events = d.replay(run, d.TUNED)
    shadow = {s: dp.on_off(events, s, "full", "pre_signal_on", "pre_signal_off", run.duration) for s in run.subs}
    eps3 = gt3.run_truth(run, gt3.Params(), path_queues=False)[0]
    gt3_spans = {s: [(e["t_on"], e["t_end"]) for e in eps3 if e["flow"] == s] for s in run.subs}
    return {"eps1": eps1, "eps2": eps2, "series": series, "shadow": shadow, "gt3": gt3_spans,
            "bursts": gt1._bursts(run.path)}


def draw(axes, run: d.Run, ctx: dict, lo: float, hi: float, fine: bool, show_labels: bool) -> None:
    ax_rate, ax_q, ax_drop, ax_lane = axes
    for ax, label in ((ax_rate, "Mb/s"), (ax_q, "queue delay (ms)"), (ax_drop, "drops / sample" if fine else "drops / 100 ms")):
        dp.style(ax, label if show_labels else "")
    for i, (hop, s) in enumerate(ctx["series"].items()):
        color = QUEUE_COLORS[i % len(QUEUE_COLORS)]
        m = (s["t"] >= lo) & (s["t"] <= hi)
        t = s["t"][m]
        ax_rate.plot(t, s["cap"][m], color=color, linewidth=1.3, drawstyle="steps-post", label=f"{hop} capacity")
        if s["sent"] is not None:
            if fine:
                ax_rate.plot(t, s["sent"][m], color=color, linewidth=0.7, alpha=0.6, label=f"{hop} sent")
                ax_rate.plot(t, s["offered"][m], color=color, linewidth=0.7, linestyle="--", label=f"{hop} offered")
            else:
                ax_rate.plot(*dp.binned(list(t), list(s["sent"][m]), np.mean), color=color, linewidth=0.7, alpha=0.6,
                             label=f"{hop} sent")
                ax_rate.plot(*dp.binned(list(t), list(s["offered"][m]), np.mean), color=color, linewidth=0.7,
                             linestyle="--", label=f"{hop} offered")
        if fine:
            if s["fine"] is not None:
                ft, fq = s["fine"]
                fm = (ft >= lo) & (ft <= hi)
                ax_q.plot(ft[fm], fq[fm], color=color, linewidth=0.6, alpha=0.55, label=f"{hop} 5 ms")
            ax_q.plot(t, s["q_ms"][m], color=color, linewidth=1.0, marker=".", markersize=3, label=f"{hop} 25 ms")
            ax_drop.bar(t, s["drops"][m], width=0.02, color=color, label=hop)
        else:
            ax_q.plot(*dp.binned(list(t), list(s["q_ms"][m]), max), color=color, linewidth=0.9, label=f"{hop} max / 100 ms")
            ax_drop.plot(*dp.binned(list(t), list(s["drops"][m]), sum), color=color, linewidth=0.9, drawstyle="steps-post", label=hop)
    ax_q.axhline(gt1.TARGET_MS, color=dp.ALARM_FP, linewidth=0.8, linestyle="--", label=f"TARGET {gt1.TARGET_MS:g} ms")
    rows = [("injected event", dp.INK, [(b["start"], b["end"]) for b in ctx["bursts"]], [])]
    for hop in ctx["series"]:
        rows.append((f"GT1 {hop}", GT1_COLOR, [(e["start_s"], e["end_s"]) for e in ctx["eps1"] if e["hop"] == hop], []))
        rows.append((f"GT2 {hop}", GT2_COLOR, [(e["t_on"], e["t_end"]) for e in ctx["eps2"] if e["queue_id"] == hop], []))
    for sid in run.subs:
        rows.append((f"{sid} GT3", GT3_COLOR, ctx["gt3"].get(sid, []), []))
        rows.append((f"{sid} shadow", dp.SHADOW, ctx["shadow"].get(sid, []), []))
    rows = [(n, c, [(max(a, lo), min(b, hi)) for a, b in sp if b >= lo and a <= hi], tk) for n, c, sp, tk in rows]
    dp.style(ax_lane, "")
    dp.lanes(ax_lane, rows)
    if not show_labels:
        ax_lane.set_yticklabels([])
    for ax in axes:
        for b in ctx["bursts"]:
            if lo <= b["start"] <= hi:
                ax.axvline(b["start"], color=dp.INK, linewidth=0.8, zorder=3)
            if lo <= b["end"] <= hi:
                ax.axvline(b["end"], color=dp.INK, linewidth=0.6, linestyle=":", zorder=3)
        ax.set_xlim(lo, hi)
    if show_labels:
        for ax in (ax_rate, ax_q, ax_drop):
            dp.legend(ax)


def figure(n_cols: int, n_lanes: int, width: float):
    fig, axes = plt.subplots(4, n_cols, figsize=(width, 7 + 0.22 * n_lanes), sharex="col", squeeze=False,
                             gridspec_kw={"height_ratios": [0.9, 1.3, 0.6, 0.18 * n_lanes + 0.4]})
    fig.patch.set_facecolor(dp.SURFACE)
    return fig, axes


def windows(run: d.Run, bursts) -> list[tuple[float, float, str]]:
    if bursts:
        out = []
        for b in bursts:  # events starting together (split "a+up") share one window
            label = f"{b['kind']} u={b['u_agg']:g} {b['end'] - b['start']:.1f} s on {b['hop'][0]}->{b['hop'][1]}"
            hi = max(b["start"] - LEAD_S + WINDOW_S, b["end"] + TAIL_S)
            if out and abs(out[-1][0] - (b["start"] - LEAD_S)) < 0.1:
                out[-1] = (out[-1][0], max(out[-1][1], hi), out[-1][2] + " + " + label)
            else:
                out.append((b["start"] - LEAD_S, hi, label))
        return out
    out, t = [], d.WARMUP_S
    while t + WINDOW_S <= run.duration - d.SHUTDOWN_S:
        out.append((t, t + WINDOW_S, "no injected event"))
        t += CALM_STEP_S
    return out


def plot(run_dir: Path, out: Path | None = None) -> str:
    """Draw one run's figures into out (default <run>/truth/plots)."""
    run = d.Run(run_dir)
    ctx = gather(run)
    out = out or run_dir / "truth" / "plots"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("zoom-*.png"):
        old.unlink()
    n_lanes = 1 + len(ctx["series"]) * 2 + len(run.subs) * 2
    title = (f"{run.path.name} ({run.aqm}). Lanes: per router egress GT1 persistent queue (purple) and GT2 demand >= "
             f"capacity (teal); per client GT3 flow impact (red) and shadow alarm (blue). Solid line = event start, dotted = end.")
    fig, axes = figure(1, n_lanes, 16)
    draw(axes[:, 0], run, ctx, 0, run.duration, fine=False, show_labels=True)
    axes[-1, 0].set_xlabel("run time (s)", color=dp.INK_2, fontsize=8)
    fig.suptitle(title, fontsize=9, color=dp.INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out / "overview.png", dpi=100, facecolor=dp.SURFACE)
    plt.close(fig)
    wins = windows(run, ctx["bursts"])
    for page in range(math.ceil(len(wins) / PER_PAGE)):
        chunk = wins[page * PER_PAGE:(page + 1) * PER_PAGE]
        fig, axes = figure(PER_PAGE, n_lanes, 21)
        for col in range(PER_PAGE):
            if col >= len(chunk):
                for ax in axes[:, col]:
                    ax.set_visible(False)
                continue
            lo, hi, label = chunk[col]
            draw(axes[:, col], run, ctx, lo, hi, fine=True, show_labels=col == 0)
            if col == 0:
                for ax in axes[:3, 0]:
                    if ax.get_legend():
                        ax.get_legend().set_bbox_to_anchor((0, 1.0 + (0.18 if ax is axes[0, 0] else 0.0)))
            axes[0, col].set_title(f"{lo:.1f}-{hi:.1f} s: {label}", fontsize=8, color=dp.INK, loc="left", pad=4)
            axes[-1, col].set_xlabel("run time (s)", color=dp.INK_2, fontsize=8)
        fig.suptitle(title, fontsize=9, color=dp.INK, x=0.01, ha="left")
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        fig.savefig(out / f"zoom-{page + 1:02d}.png", dpi=90, facecolor=dp.SURFACE)
        plt.close(fig)
    return f"{run_dir.name}: overview + {math.ceil(len(wins) / PER_PAGE)} zoom pages"


def index(campaign: Path, runs: list[Path]) -> Path:
    parts = [f"<!doctype html><meta charset=utf-8><title>Truth plots {campaign.name}</title>",
             "<style>body{font:14px system-ui;margin:16px;background:#fcfcfb;color:#1f1f1e}img{max-width:100%;border:1px solid #e6e5df}"
             "details{margin:6px 0}summary{cursor:pointer;font-weight:600}</style>",
             f"<h1>Truth plots: {campaign.name}</h1><p>Each run: overview, then zoom pages. Click a run to open it.</p>"]
    for r in runs:
        plots = r / "truth" / "plots"
        imgs = [plots / "overview.png"] + sorted(plots.glob("zoom-*.png"))
        parts.append(f"<details><summary>{r.name}</summary>"
                     + "".join(f'<p>{p.name}</p><img loading="lazy" src="{p.relative_to(campaign)}">' for p in imgs if p.exists())
                     + "</details>")
    out = campaign / "truth-plots.html"
    out.write_text("\n".join(parts))
    return out


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    campaign = None
    if argv[0] == "--campaign":
        campaign = Path(argv[1])
        runs = sorted(p for p in campaign.iterdir() if (p / "events.csv").exists())
    else:
        runs = [Path(a) for a in argv]
    with ProcessPoolExecutor(max_workers=12) as pool:
        for line in pool.map(plot, runs):
            print(line, flush=True)
    if campaign:
        print(index(campaign, runs))


if __name__ == "__main__":
    main(sys.argv[1:])
