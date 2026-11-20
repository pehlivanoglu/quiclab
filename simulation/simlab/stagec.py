#!/usr/bin/env python3
"""Stage C driver (user decisions 2026-11-19; plan reports/sim-stageC-plan/README.md). The user starts it.

    python3 simulation/simlab/stagec.py dry-run [--check-plans]   # prints what it would do; runs nothing
    python3 simulation/simlab/stagec.py run [--blocks C1,C2,C3,C4] [--sim-parallel 4] [--fast-score]
    python3 simulation/simlab/stagec.py status

Grid: C1 100 clients and C2 300 clients (L10, L50, L100, uneven x pfifo / CoDel x seeds 1-2, sampled router trace +
GT-Q); C3 1000 clients (4 layouts x pfifo x seeds 1-2) and C4 1000 clients L50 at U 0.70 (EXT) x pfifo x seeds 1-2,
both without router trace and GT-Q. 600 s, ack-matched.

Per run: plan folder (stagec_gen) -> simulation (run.py --trace sample|none --no-health) -> scoring, one step at a
time: health (frozen GT-Q health where traced; health-lite always), detector (frozen v2-owd), SETS (frozen;
--fast-score only after the fast path is accepted), events kept (E0, E1-0.5), GT1, GT3, GT-Q (traced) -> outputs
checked complete -> the run's tick cache deleted (W2) -> the run's own files compressed and verified (W1).

Rules enforced here (user 2026-11-19):
- memory: the expected peak of a step plus everything running stays < 45 GB, else the step waits; swap growth
  > SWAP_STOP_MB stops the batch;
- disk: before each simulation, free disk minus the run's expected raw output and cache must stay >= 30 GB, else
  the batch stops cleanly; < 50 GB is logged as a warning;
- tick cache only in TICK_CACHE (outside quiclab/); a run's cache is deleted only when its scored outputs exist and
  are complete; a failed step keeps the cache and is reported;
- compression only of stage C run folders whose scoring is complete; each file decompressed and compared (sha256)
  before the original is removed; a manifest per run (compress-manifest.json); any failure keeps the originals;
- nothing else under quiclab/ is touched; an incomplete run folder is kept and reported, and a re-run goes to a new
  folder <name>.a<k>.
Stop: SIGINT / SIGTERM (Ctrl-C in tmux, or the guard) stops running steps and writes the state; resume = same command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUICLAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import stagec_numbers as num  # noqa: E402

PY = sys.executable
ROOT = QUICLAB / "simulation" / "runs" / "stageC"
TICK_CACHE = Path("/home/ubuntu/simcache-stageC")          # W2 (user 2026-11-19)
CACHE_MARK = ".made-by-sim-session-stageC"
STATE = ROOT / "state.json"
MEM_LIMIT_GB = 45.0                                        # user 2026-11-19
DISK_STOP_GB, DISK_WARN_GB = 30.0, 50.0                    # standing limits
SWAP_STOP_MB = 512                                         # (T) swap growth that counts as "the machine swaps"
COMPRESS_MIN_BYTES = 64 * 1024                             # (T) smaller files (metadata, scores) stay plain
DUR = 600
LAYOUTS = ("L10", "L50", "L100", "uneven")


# ── run list ────────────────────────────────────────────────────────────────

def run_list() -> list[dict]:
    out = []
    for block, n in (("C1", 100), ("C2", 300)):
        for lay in LAYOUTS:
            for aqm in ("pfifo", "codel"):
                for seed in (1, 2):
                    out.append(dict(block=block, n=n, layout=lay, aqm=aqm, seed=seed, point="DEF", trace="sample"))
    for lay in LAYOUTS:
        for seed in (1, 2):
            out.append(dict(block="C3", n=1000, layout=lay, aqm="pfifo", seed=seed, point="DEF", trace="none"))
    for seed in (1, 2):
        out.append(dict(block="C4", n=1000, layout="L50", aqm="pfifo", seed=seed, point="EXT", trace="none"))
    for r in out:
        r["ports"] = "route" if r["trace"] != "none" else "reuse"   # U2 (user 2026-11-19)
        r["name"] = f"sim-C-{r['block']}-{r['layout']}-n{r['n']}-{r['aqm']}-r{r['seed']}"
        e = num.run(r["n"], r["layout"], r["aqm"], r["seed"], "U0.70" if r["point"] == "EXT" else "U0.50", DUR,
                    r["trace"] != "none")
        r["exp"] = {"raw_gb": sum(v[0] for k, v in e["disk"].items() if k != "tick cache") / 1e9,
                    "zst_gb": sum(v[1] for k, v in e["disk"].items() if k != "tick cache") / 1e9,
                    "cache_gb": e["disk"]["tick cache"][0] / 1e9, "mem": e["mem"], "time": e["t"]}
    return out


def test_run() -> list[dict]:
    """--test: one small run through every step (user 2026-11-19: end-to-end pass before stage C), in its own root."""
    r = dict(block="T", n=20, layout="L10", aqm="pfifo", seed=1, point="DEF", trace="sample", ports="route",
             name="sim-C-T-L10-n20-pfifo-r1")
    e = num.run(20, "L10", "pfifo", 1, "U0.50", DUR, True)
    r["exp"] = {"raw_gb": sum(v[0] for k, v in e["disk"].items() if k != "tick cache") / 1e9,
                "zst_gb": sum(v[1] for k, v in e["disk"].items() if k != "tick cache") / 1e9,
                "cache_gb": e["disk"]["tick cache"][0] / 1e9, "mem": e["mem"], "time": e["t"]}
    return [r]


def plan_dir(r): return ROOT / "plans" / r["name"]
def cache_dir(r): return TICK_CACHE / r["block"] / r["name"]


# ── state ───────────────────────────────────────────────────────────────────

def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(st: dict) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=1, default=str))
    tmp.replace(STATE)


def log(msg: str) -> None:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}", flush=True)


def run_dir(r: dict, st: dict) -> Path:
    return ROOT / r["block"] / st.get(r["name"], {}).get("folder", r["name"])


# ── checks ──────────────────────────────────────────────────────────────────

def free_gb() -> float:
    return shutil.disk_usage("/").free / 1e9


def swap_used_mb() -> float:
    m = dict(ln.split(":", 1) for ln in Path("/proc/meminfo").read_text().splitlines())
    return (int(m["SwapTotal"].split()[0]) - int(m["SwapFree"].split()[0])) / 1024


def complete(rd: Path, traced: bool) -> tuple[bool, list[str]]:
    need = ["sim/meta.json", "sim/scored.json", "sim/episodes-v2-owd.json", "sim/sets.json", "sim/events-E0.json",
            "sim/events-E1-0.5.json", "health-lite.csv", "truth/gt1.csv", "truth/gt3.csv"]
    if traced:
        need += ["gtq-health.csv", "truth/gtq.csv"]
    missing = [p for p in need if not (rd / p).exists() or (rd / p).stat().st_size == 0]
    if (rd / "sim" / "scored.json").exists() and "FAILED" in (rd / "sim" / "scored.json").read_text():
        missing.append("sim/scored.json has FAILED")
    return not missing, missing


# ── W2: the tick cache ─────────────────────────────────────────────────────

def ensure_cache_root() -> None:
    TICK_CACHE.mkdir(parents=True, exist_ok=True)
    (TICK_CACHE / CACHE_MARK).write_text("tick cache of stage C; files here are deleted per run after scoring\n")


def delete_cache(r: dict, rd: Path) -> str:
    d = cache_dir(r).resolve()
    ok, missing = complete(rd, r["trace"] != "none")
    if not ok:
        return f"cache kept (scoring incomplete: {missing})"
    if TICK_CACHE.resolve() not in d.parents or not (TICK_CACHE / CACHE_MARK).exists():
        return f"cache kept ({d} is not under the marked cache root)"
    if d.exists():
        shutil.rmtree(d)
    return "cache deleted"


# ── W1: compression ────────────────────────────────────────────────────────

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def compress_run(r: dict, rd: Path) -> str:
    ok, missing = complete(rd, r["trace"] != "none")
    if not ok:
        return f"not compressed (scoring incomplete: {missing})"
    if rd.resolve().parent.parent != ROOT.resolve():
        return f"not compressed ({rd} is not a stage C run folder)"
    files = [p for p in sorted(rd.rglob("*")) if p.is_file() and not p.name.endswith(".zst")
             and p.name != "compress-manifest.json" and p.stat().st_size >= COMPRESS_MIN_BYTES]
    manifest, bad = [], []
    for p in files:
        z = p.with_name(p.name + ".zst")
        orig = sha256_file(p)
        subprocess.run(["zstd", "-3", "-T1", "-q", "-f", str(p), "-o", str(z)], check=True)
        dec = subprocess.run(["zstd", "-dc", str(z)], capture_output=True, check=True).stdout
        if hashlib.sha256(dec).hexdigest() != orig:
            bad.append(str(p.relative_to(rd)))
        manifest.append({"file": str(p.relative_to(rd)), "bytes": p.stat().st_size, "sha256": orig,
                         "zst_bytes": z.stat().st_size})
    (rd / "compress-manifest.json").write_text(json.dumps({"verified": not bad, "failures": bad, "files": manifest},
                                                          indent=1))
    if bad:
        return f"compression verification FAILED for {len(bad)} file(s); originals kept"
    for p in files:
        p.unlink()
    return f"compressed {len(files)} files, {sum(m['bytes'] for m in manifest) / 1e9:.2f} -> " \
           f"{sum(m['zst_bytes'] for m in manifest) / 1e9:.2f} GB"


# ── steps (each its own process, so its memory is released) ───────────────

def step_cmds(r: dict, rd: Path, fast: bool) -> list[tuple[str, list[str], float]]:
    """(step, argv, expected peak GB) of the scoring chain."""
    pd, traced, e = plan_dir(r), r["trace"] != "none", r["exp"]["mem"]
    pre = f"import sys, json; sys.path.insert(0, {str(HERE)!r}); import scale_ext; from pathlib import Path; " \
          f"rd = Path({str(rd)!r}); "
    sc = rd / "sim" / "scored.json"
    steps = []
    if traced:
        steps.append(("health", [PY, "-c", pre + "import run; print(run.gtq_health(rd))"], e["health"]))
    steps.append(("health-lite", [PY, str(HERE / "health_lite.py"), str(rd)], 1.0))
    steps.append(("detector", [PY, "-c", pre + "import frozen; e = frozen.episodes(rd); "
                               "json.dump({k: [list(x) for x in v] for k, v in e.items()}, "
                               "open(rd / 'sim' / 'episodes-v2-owd.json', 'w'))"], e["det"]))
    sets_call = (f"import fastscore; fastscore.install(); " if fast else "") + \
        f"import stageb_compare as c; s = c.sets_scores(rd, Path({str(pd)!r})); " \
        "(rd / 'sim' / 'sets.json').write_text(json.dumps(s, indent=1, default=str))"
    steps.append(("sets", [PY, "-c", pre + sets_call], e["sets"]))
    steps.append(("events", [PY, "-c", pre + "import stagec_events as ev; ev.write(rd)"], e["sets"]))
    for s in ("gt1", "gt3") + (("gtq",) if traced else ()):
        steps.append((s, [PY, str(HERE / "scale_ext.py"), str(QUICLAB / "scripts" / f"{s}.py"), "score", str(rd)],
                      e["gtq"] if s == "gtq" else 1.0 if s == "gt1" else e["det"]))
    return steps


# ── run ─────────────────────────────────────────────────────────────────────

class Stop(Exception):
    pass


def cmd_run(a) -> int:
    global ROOT, STATE
    if a.test:
        ROOT = QUICLAB / "simulation" / "runs" / "stageC-test"
        STATE = ROOT / "state.json"
        runs = test_run()
    else:
        runs = [r for r in run_list() if r["block"] in a.blocks]
    st = load_state()
    ensure_cache_root()
    env = dict(os.environ, QUICLAB_SIM_TICK_CACHE=str(TICK_CACHE), OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               PYTHONDONTWRITEBYTECODE="1")   # nothing written into the frozen NPR folder it imports from
    sims: dict[str, subprocess.Popen] = {}
    scoring: dict = {}          # name -> {"steps": [...], "i": k, "proc": Popen, "lines": {}}
    swap0 = swap_used_mb()
    stopping = {"sig": None}

    def on_sig(sig, _f):
        stopping["sig"] = sig
    signal.signal(signal.SIGINT, on_sig)
    signal.signal(signal.SIGTERM, on_sig)

    def mem_running() -> float:
        g = sum(next(r for r in runs if r["name"] == n)["exp"]["mem"]["sim"] for n in sims)
        for n, s in scoring.items():
            if s.get("proc"):
                g += s["steps"][s["i"]][2]
        return g

    def todo(state):
        return [r for r in runs if st.get(r["name"], {}).get("state") == state]

    for r in runs:   # resume: incomplete simulations get a new folder, the old one is kept and reported
        s = st.setdefault(r["name"], {"state": "planned"})
        if s["state"] in ("simulating",):
            old = run_dir(r, st)
            k = 2
            while (ROOT / r["block"] / f"{r['name']}.a{k}").exists():
                k += 1
            s.update(state="planned", folder=f"{r['name']}.a{k}", note=f"incomplete earlier attempt kept: {old}")
            log(f"{r['name']}: incomplete simulation kept in {old}; re-run goes to {s['folder']}")
        if s["state"] == "scoring" or (a.retry_failed and s["state"] == "failed"
                                       and (run_dir(r, st) / "sim" / "meta.json").exists()):
            s["state"] = "simulated"   # scoring restarts from its first step (outputs are rewritten)
            s.pop("failed_step", None)
    save_state(st)
    try:
        while True:
            if stopping["sig"]:
                raise Stop(f"signal {stopping['sig']}")
            if swap_used_mb() - swap0 > SWAP_STOP_MB:
                raise Stop(f"the machine swaps ({swap_used_mb() - swap0:.0f} MB more swap than at the start)")
            # finished simulations
            for n, p in list(sims.items()):
                if p.poll() is not None:
                    r = next(x for x in runs if x["name"] == n)
                    ok = p.returncode == 0 and (run_dir(r, st) / "sim" / "meta.json").exists()
                    st[n]["state"] = "simulated" if ok else "failed"
                    st[n]["sim_rc"] = p.returncode
                    log(f"{n}: simulation {'done' if ok else f'FAILED (rc {p.returncode})'}")
                    del sims[n]
                    save_state(st)
            # scoring: one run at a time, its steps in order
            if scoring:
                n, s = next(iter(scoring.items()))
                r = next(x for x in runs if x["name"] == n)
                p = s.get("proc")
                if p is not None and p.poll() is not None:
                    step = s["steps"][s["i"]][0]
                    out = (s["out"].read_text() if s["out"].exists() else "").strip().splitlines()
                    s["lines"][step] = (out[-1] if out else "ok") if p.returncode == 0 else f"FAILED rc {p.returncode}: {out[-3:]}"
                    if step in ("gt1", "gt3", "gtq"):
                        sc = run_dir(r, st) / "sim" / "scored.json"
                        cur = json.loads(sc.read_text()) if sc.exists() else {}
                        cur[step] = s["lines"][step]
                        sc.write_text(json.dumps(cur, indent=1) + "\n")
                    log(f"{n}: {step}: {s['lines'][step][:160]}")
                    s["proc"] = None
                    if step == "health-lite" and p.returncode != 0:   # user 2026-11-19: a run failing it is invalid
                        st[n]["invalid"] = s["lines"][step][:300]
                        log(f"{n}: INVALID (light health check failed); scoring continues, the run is reported as invalid")
                    if p.returncode != 0 and step != "health-lite":
                        st[n].update(state="failed", failed_step=step, note="cache kept")
                        log(f"{n}: scoring step {step} FAILED; tick cache kept; batch continues with other runs")
                        del scoring[n]
                        save_state(st)
                        continue
                    s["i"] += 1
                if n in scoring and s.get("proc") is None:
                    if s["i"] >= len(s["steps"]):
                        rd = run_dir(r, st)
                        sc = rd / "sim" / "scored.json"
                        cur = json.loads(sc.read_text()) if sc.exists() else {}
                        cur["detector"] = "ok" if (rd / "sim" / "episodes-v2-owd.json").exists() else "FAILED"
                        cur["health_lite"] = s["lines"].get("health-lite")
                        sc.write_text(json.dumps(cur, indent=1) + "\n")
                        st[n]["cache"] = delete_cache(r, rd)
                        st[n]["compress"] = compress_run(r, rd)
                        st[n]["state"] = "done" if "FAILED" not in st[n]["compress"] else "failed"
                        log(f"{n}: {st[n]['cache']}; {st[n]['compress']}")
                        del scoring[n]
                        save_state(st)
                    else:
                        step, argv, need = s["steps"][s["i"]]
                        if mem_running() + need < MEM_LIMIT_GB:
                            s["out"] = run_dir(r, st) / "logs" / f"score-{step}.log"
                            s["proc"] = subprocess.Popen(["nice", "-n", "19", *argv], env=env,
                                                         stdout=s["out"].open("w"), stderr=subprocess.STDOUT,
                                                         start_new_session=True)
            if not scoring:
                nxt = todo("simulated")
                if nxt:
                    r = nxt[0]
                    st[r["name"]]["state"] = "scoring"
                    scoring[r["name"]] = {"steps": step_cmds(r, run_dir(r, st), a.fast_score), "i": 0, "lines": {}}
                    save_state(st)
                    continue
            # new simulations
            waiting = todo("planned")
            if waiting and len(sims) < a.sim_parallel:
                r = waiting[0]
                need_disk = r["exp"]["raw_gb"] + r["exp"]["cache_gb"] + sum(
                    x["exp"]["raw_gb"] for x in runs if x["name"] in sims)
                left = free_gb() - need_disk
                if left < DISK_STOP_GB:
                    raise Stop(f"disk: {free_gb():.0f} GB free, {need_disk:.0f} GB expected for {r['name']} and the "
                               f"running simulations -> {left:.0f} GB < {DISK_STOP_GB:.0f} GB")
                if left < DISK_WARN_GB:
                    log(f"WARNING disk: {left:.0f} GB expected free after {r['name']} (< {DISK_WARN_GB:.0f})")
                if mem_running() + r["exp"]["mem"]["sim"] < MEM_LIMIT_GB:
                    pd = plan_dir(r)
                    if not (pd / "v3-plan.json").exists():
                        import stagec_gen
                        stagec_gen.make(pd, r["n"], r["layout"], r["aqm"], r["seed"], r["point"], r["block"])
                    rd = run_dir(r, st)
                    rd.parent.mkdir(parents=True, exist_ok=True)
                    (ROOT / "logs").mkdir(exist_ok=True)
                    st[r["name"]]["state"] = "simulating"
                    save_state(st)
                    sims[r["name"]] = subprocess.Popen(
                        ["nice", "-n", "19", PY, str(HERE / "run.py"), str(pd), str(rd), "--seed", str(r["seed"]),
                         "--ack", "matched", "--trace", r["trace"], "--ports", r["ports"], "--fast-links", "--no-health"], env=env,
                        stdout=(ROOT / "logs" / f"{r['name']}.log").open("w"), stderr=subprocess.STDOUT,
                        start_new_session=True)
                    log(f"{r['name']}: simulation started ({len(sims)} running; free disk {free_gb():.0f} GB)")
                    continue
            if not sims and not scoring and not todo("planned") and not todo("simulated"):
                done = sum(st[r["name"]]["state"] == "done" for r in runs)
                log(f"batch finished: {done} / {len(runs)} done, "
                    f"{sum(st[r['name']]['state'] == 'failed' for r in runs)} failed")
                return 0 if done == len(runs) else 1
            time.sleep(5)
    except Stop as e:
        log(f"STOP: {e}")
        for p in list(sims.values()) + [s["proc"] for s in scoring.values() if s.get("proc")]:
            try:
                os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        save_state(st)
        log("stopped cleanly; finished runs kept; resume with the same command")
        return 2


# ── dry run / status ───────────────────────────────────────────────────────

def cmd_dry(a) -> int:
    import stagec_gen as g
    runs = run_list()
    print(f"# Stage C dry run ({time.strftime('%Y-%m-%d %H:%M')}): nothing is simulated, scored, deleted or compressed\n")
    print(f"Runs: {len(runs)}; run folders {ROOT}/<block>/<run>; plans {ROOT}/plans/<run>; tick cache {TICK_CACHE}/<block>/<run> "
          f"(one run at a time); state {STATE}\n")
    print("## Leaves per layout (leaf name: clients; sampled = traced leaves under 'sample')\n")
    import plan as P
    for n in (100, 300, 1000):
        for lay in LAYOUTS:
            sizes = g.leaf_sizes(n, lay)
            w = max(2, len(str(len(sizes))))
            names = [f"l{i + 1:0{w}d}" for i in range(len(sizes))]
            samp = P.sampled_leaves({"egress": {"up": {}, **{x: {} for x in names}}})
            if lay == "uneven" or len(names) <= 10:
                desc = ", ".join(f"{x}: {k}" for x, k in zip(names, sizes))
            else:
                desc = f"{len(names)} leaves of {sizes[0]}"
            print(f"- {n} clients, {lay}: {desc}; sampled ({'C1/C2' if n < 1000 else 'none: no trace at 1000'}): "
                  f"{', '.join(samp) if n < 1000 else '-'}")
    print("\n## Run list (expected per run, extrapolated: stagec_numbers.py)\n")
    print("| # | run | trace | raw GB | zstd GB | cache GB | sim min | scoring min | largest step GB |")
    print("|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(runs, 1):
        t, m = r["exp"]["time"], r["exp"]["mem"]
        sc = (t["health"] + t["gtq"] + t["det"] + t["sets"] + t["gt3"]) / 60
        print(f"| {i} | {r['name']} | {r['trace']} | {r['exp']['raw_gb']:.1f} | {r['exp']['zst_gb']:.1f} | "
              f"{r['exp']['cache_gb']:.1f} | {min(t['sim'], t['sim_hi']) / 60:.0f}-{max(t['sim'], t['sim_hi']) / 60:.0f} | "
              f"{sc:.0f} | {max(v for k, v in m.items()):.1f} |")
    print("\n## Steps per run, in this order\n")
    r = runs[0]
    for s, argv, need in step_cmds(r, ROOT / r["block"] / r["name"], False):
        print(f"- {s} (expected peak {need:.1f} GB for {r['name']})")
    print("- check outputs complete -> delete the run's tick cache (W2) -> compress and verify (W1, manifest)")
    if a.check_plans:
        print("\n## Plan check (each run's plan built in a temporary folder outside quiclab/, then removed)\n")
        tmp = Path(tempfile.mkdtemp(prefix="stagec-dry-"))
        try:
            for r in runs:
                pd = tmp / r["name"]
                try:
                    g.make(pd, r["n"], r["layout"], r["aqm"], r["seed"], r["point"], r["block"])
                    lines = P.build(pd, tmp / "sim" / r["name"], r["seed"], "matched", r["trace"], r["ports"],
                                    fast_links=True)
                    used = {}
                    for ln in lines:
                        if ln.startswith("bg "):
                            kv = dict(x.split("=", 1) for x in ln.split()[1:] if "=" in x)
                            n = len(kv.get("weights", "1").split(","))
                            used[kv["src"]] = max(used.get(kv["src"], 0), int(kv["sport"]) + n - P.BG_SPORT_BASE)
                    print(f"- {r['name']}: ok, {len(lines)} plan records; ports '{r['ports']}': highest port block end "
                          f"on one route {max(used.values())} of {P.PORT_SPAN} available")
                except Exception as e:  # noqa: BLE001
                    print(f"- {r['name']}: **FAILS**: {type(e).__name__}: {e}")
        finally:
            shutil.rmtree(tmp)
    tot_raw = sum(r["exp"]["zst_gb"] for r in runs)
    print(f"\n## Disk check\n\nfree now {free_gb():.0f} GB; outputs kept (compressed) {tot_raw:.0f} GB; "
          f"peak extra while running (largest raw run + its cache) "
          f"{max(r['exp']['raw_gb'] + r['exp']['cache_gb'] for r in runs):.0f} GB per running 1000-client run; "
          f"expected free at the end {free_gb() - tot_raw:.0f} GB (from today's free space)")
    return 0


def cmd_status(_a) -> int:
    st = load_state()
    runs = run_list()
    print(f"free disk {free_gb():.0f} GB; swap used {swap_used_mb():.0f} MB")
    for r in runs:
        s = st.get(r["name"], {"state": "not started"})
        print(f"{r['name']:45s} {s['state']:12s} {'INVALID ' if s.get('invalid') else ''}{s.get('failed_step', '')} "
              f"{s.get('cache', '')} {s.get('compress', '')}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dry-run")
    d.add_argument("--check-plans", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--blocks", default="C1,C2,C3,C4", type=lambda s: s.split(","))
    r.add_argument("--sim-parallel", type=int, default=4)
    r.add_argument("--fast-score", action="store_true", help="only after the fast path is accepted (W5)")
    r.add_argument("--retry-failed", action="store_true", help="re-score failed runs whose simulation finished")
    r.add_argument("--test", action="store_true", help="one small run (20 clients) through every step, own root")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    return {"dry-run": cmd_dry, "run": cmd_run, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
