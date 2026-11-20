# 300-client test, re-run with fast links (2026-11-19 evening)

The same plan, cell, seed and ACK profile as the first run (`../sim-scale300/`), with three changes:
- every link that is not a designed bottleneck at 100 Gb/s (plan.py --fast-links);
- every random stream fixed;
- queue totals of every queue disc.

Started by the user, 18:43-19:34. Numbers: `timings.txt`, `sizes.txt`, `health-lite.json`, `compare.json`,
`spread-stimuli.json`, `sets-diag.json`.

## 1. Validity and light health check (accepted at 300 clients)

| check | first run | re-run |
|---|---|---|
| frozen GT-Q health | ok | ok (lost 0, identity ok, match min 1.0) |
| light check, all items | item 4 FAILED (676k packets lost outside the router) | **ok on items 1, 3-8** (item 2 needs the trace-"sample" totals file: not applicable to a trace-"full" run) |
| loss balance (unacked video + lost background - drops) | 676,159 / 1,001,618 | **30,122 / 2,054,146 (1.5 %)** |
| drops outside the designed bottleneck | (not measured) | **0 on 609 other queues** |
| stimulus load at the bottleneck / plan | 0.86-1.04 (u = 1.3 windows 0.86-0.89) | **1.02-1.05** |
| late arrivals | 0 | 0 |

The light check passes where the frozen check passes, and it failed the first run for a real fault. Together with
the 44 B2 runs and the negative tests, that is its acceptance at 300 clients.

## 2. First run against re-run (every moved value marked *)

| quantity | first run | re-run |
|---|---|---|
| member-onsets found / missed (18 stimuli x 300) | 5,389 / 11 | 5,400 / 0 * |
| onset spread p50 / p90 / p98 / max ms | 280 / 558 / 801 / 891 | **66 / 356 / 647 / 726** * |
| stimuli with spread > 0.5 s | 3 | 1 * |
| share of onsets outside 0.5 s after the first | 0.30 % (16) | **0.02 % (1)** * |
| SETS k = 2: leaf F1 mean / pair P / pair R | 0.50 / 1.00 / 0.996 | **0.885 / 1.00 / 1.00** * |
| SETS k = 2: leaf group F1 >= 0.9 after | 19 events, 139 s | **4 events, 62 s** * |
| SETS k = 3: leaf F1 mean / group after | 0.50 / 19 events | 0.81 / 6 events, 75 s * |
| E0 closes (18 stimuli) / first group | 40 / close 21, 138 s | **26 / close 4, 60 s** * |
| E1-0.5 events | 22 | 19 * |
| SETS@E1-0.5 k = 2: first exact / mean leaf F1 / false-split closes | stimulus 4 / 0.68 / 0 | **stimulus 1 / 0.95 / 16** * |
| NPR-A: first exact / mean leaf F1 / false splits | stimulus 0 (close 2) / 0.96 / 0 | stimulus 0 (close 1) / **1.00** / 0 * |
| NPR-B: first exact / mean leaf F1 / false splits / CPU | stimulus 0 / 0.96 / **10** / 0.16 s | stimulus 0 / **1.00** / **0** / 0.86 s * |
| simulation wall / peak memory | 475 s / 0.52 GB | 490 s / (run.py step incl. health 9.3 GB) |
| GT-Q step peak memory | 11.0 GB | 11.1 GB |
| raw / zstd output | 5.23 / 0.92 GB | 5.43 / 0.91 GB |

## 3. What changes in the earlier conclusions

- **The 0.5 s event window holds, more clearly than before:** 0.02 % of onsets outside it, against 0.30 %.
- **The onset spread at the 300-client leaf was inflated by the weakened surges:** p50 66 ms, not 280 ms. The first
  run's spread numbers are not to be used.
- **SETS at 300: the late group was mostly an artefact of the weakened surges.**
  - The accepted finding was "late group, from the method".
  - With full-strength surges the E0 events split far less (26 closes for 18 stimuli instead of 40). The group
    appears at the 2nd stimulus (close 4, 60 s) instead of the 7th, and leaf F1 is 0.885 instead of 0.50.
  - The two mechanisms are real but small here: the 150 ms E0 window still splits some stimuli (p90 356 ms), and the
    miss-rate estimate still starts at 0.
  - On E1-0.5 events, SETS now finds the leaf at the first stimulus but splits it in 16 closes. In the first run it
    found the leaf only at stimulus 4 and never split it.
- **NPR:** both readers keep the leaf whole from the first event; NPR-B's splits in the first run came from the
  weakened surges.
- **The extrapolation of `../sim-scale300/README.md` section 6 stands:** time, memory and sizes moved by a few percent.

This test still has one leaf: it says nothing about separating leaves.

## 4. Superseded (user, 2026-11-19 evening; the old text is kept, marked, in ../sim-scale300/ and NOTES.md)

- "SETS forms the 300-client group late because of the method": **mostly an artefact of the weakened surges.** With
  stimuli at planned strength the group forms at the second stimulus. The two mechanisms (150 ms E0 window,
  miss-rate estimate starting at 0) exist but are small here.
- NPR-B's splits of the leaf in the first run: **also from the weakened surges.**
- **All onset-spread figures of the first run.**

Standing:
- the 0.5 s event window holds at 300 clients (0.02 % of onsets outside it);
- this run has one leaf and says nothing about separating leaves.

## 5. Why SETS on E1-0.5 splits the leaf in 16 closes

- **What happened.** In stimulus 3 (t0 73.0 s) one client, sub-224, had its onset 0.7 s after the first one. E1-0.5
  therefore formed a 299-member event and a separate 1-member event. That 299-member set is the only incomplete
  observation of the run; all other 17 stimuli give the full 300.
- **Why it becomes a group.** Under the frozen SETS rule every later 300-member observation counts toward the
  299-member set: it contains it, with one flow extra (extra <= 1). The miss-rate estimate stays near 0, so q(300)
  = 0, and the 299 set is not absorbed into the 300 set.
- **Why it stays.** SETS forgets nothing, so from close 4 on both groups stand at every close: the leaf (300) and the
  leaf minus sub-224 (299). The split-off part is one client: sub-224's smallest group is the 300 group, everyone
  else's is the 299 group. That counts as a false split at 16 of 19 closes and pair recall 0.994.
- **Why frozen SETS on its own E0 events does not split.** The E0 fragments push its miss-rate estimate up, so q is
  large and the 299 set is absorbed.
- **Where it matters.** This is the frozen rule's behaviour at near-zero miss rate: one late member in one event
  splits the group permanently. It bears on stage C's large leaves.

## 6. What the first run suggests (untested)

The first run is not a result. It does hint that with weaker congestion the onsets spread out and SETS degrades far
more than NPR (SETS group after 7 stimuli, leaf F1 0.50; NPR-A unaffected). This is untested. Stage C's stimuli have
u = 1.05, 1.15 and 1.3, so **its grouping results are to be reported per stimulus level**.
