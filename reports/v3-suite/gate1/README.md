# Campaign gate (.runs/2026-11-14_1818_v3): FAIL on check 5 only

`gate-report.md` in the campaign folder: all 9 gate runs pass checks 1, 2, 3, 4 and 6 (the legacy
run has no background, so check 6 is "-"). Check 5 fails on both G3 runs (S-BURST, pfifo and
fq_codel). The campaign stopped before any core run, as designed.

Table: [surge-components.md](surge-components.md), script [surge_components.py](surge_components.py).

## Why

Check 5 compares the router's measured offered load in each surge window (all traffic arriving
at the egress / C) with the cell's u. The surge was sized as u = U + extra / C, which assumes
the video keeps its calm rate s U = 0.21 C during the window. It does not: BBR and the GOP-aware
sender queue back off under overload.

| u | non-video measured (planned U(1 - s) + u - U) | video measured (calm s U = 0.210) | router total | check 5 failures (pfifo / fq_codel) |
|---|---|---|---|---|
| 1.05 | 0.800-0.849 (0.840) | 0.183-0.251 | 1.016-1.085 | 0 of 6 / 0 of 6 |
| 1.15 | 0.915-0.939 (0.940) | 0.150-0.233 | 1.088-1.171 | 1 of 6 / 4 of 6 |
| 1.30 | 1.054-1.085 (1.090) | 0.094-0.147 | 1.176-1.232 | 6 of 6 / 6 of 6 |

- The generator delivers what was planned. Background plus surge is within -0.04 to +0.01 of
  plan; the low end comes from the 2 s windows, where 100 ms sender bins cut the edges.
- The video share drops to ~0.1 C at u = 1.3. So the realized total overload is ~1.2, not 1.3.
  The miss grows with u and with the window length (the video needs ~1-2 s to back off), and it
  is larger under pfifo than under fq_codel at u = 1.3.

So check 5 fails by construction: it measures the elastic video together with the stimulus.

## Options (yours)

1. Check 5 on the stimulus itself: background + surge offered (qtraffic logs) within +-0.05 of
   the planned U(1 - s) + (u - U). Report the realized total u (router offered) per window as
   information, and use it in the analyses. Both G3 runs would pass: the largest deviation is
   -0.04, on a 2 s window.
2. Keep check 5 as written and size the surge to hit the total u: that needs the video's reaction
   in advance (circular, cell-dependent). Not recommended.
3. Keep the cells and record that the nominal u = 1.3 cells deliver ~1.2 total (pfifo 1.18-1.22,
   fq_codel 1.20-1.23).

Resume after a decision: `bash scripts/run_v3_campaign.sh .runs/2026-11-14_1818_v3` keeps the 9
finished gate runs and re-evaluates the gate without rerunning them.

## Decision of 2026-11-14: option 1 (implemented)

- **Check 5:** background + surge arriving at the target within +-0.05 of U(1 - s) + (u - U).
  It is measured from the GT-Q trace (enqueue times, tc-sized packets); the senders' logs are
  used where an egress has no trace. On copies of the two G3 runs: pass, deviations -0.009 to
  +0.014.
  - pfifo: total 1.03-1.09 / 1.10-1.16 / 1.18-1.23 at u = 1.05 / 1.15 / 1.3; video relative to
    calm 0.90-1.13 / 0.76-0.97 / 0.43-0.65.
  - fq_codel: total 1.02-1.05 / 1.09-1.17 / 1.20-1.24; video 0.81-0.90 / 0.67-1.04 / 0.52-0.66.
- **Every run:** `<run>/v3-stimuli.csv` (scripts/v3_stimuli.py), one row per stimulus window:
  nominal u, measured non-video, video and total load at the router ingress, video relative to
  calm, planned non-video, capacity in force, source.
- **After the campaign:** `<campaign>/video-reaction.md`: video relative to calm by nominal u,
  C2 vs C5 vs M3, per AQM, reps side by side.
- The paper notes record the definition of u and the finding.
