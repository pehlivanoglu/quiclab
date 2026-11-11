# Grouping: episode ends, in-episode agreement, events to membership (2026-11-11)

Offline study on the development set of campaign `.runs/2026-11-10_1946_v2`
(K1–K6, C1, M1–M5; 1 rep; held-out N1–N5 not read), onset source v2-owd.
No new runs. Code: `scripts/grouping_episode_study.py` (definitions in its
docstring). Data here is gzipped JSONL, one record per pair / membership;
the `*-summary.txt` files are the script's summaries of it.

| file | content |
|---|---|
| `pairs.jsonl.gz`, `pairs-summary.txt` | per pair and shared GT1 window: start / end spreads (three end definitions), window sweep, correlation, level difference, peak ratio; end vs router GT1 end |
| `member.jsonl.gz`, `member-summary.txt` | per (run, flow) membership: events, evidence entries and weights from the engine's `evidence.jsonl` |
| `noise.jsonl.gz`, `noise-summary.txt` | FIFO pairs: correlation and level difference under added per-client delay noise |

Regenerate:

    C=.runs/2026-11-10_1946_v2; O=reports/grouping-episode
    python3 scripts/grouping_episode_study.py pairs  $C $O/pairs.jsonl  && gzip $O/pairs.jsonl
    python3 scripts/grouping_episode_study.py member $C $O/member.jsonl && gzip $O/member.jsonl
    python3 scripts/grouping_episode_study.py noise  $C $O/noise.jsonl  && gzip $O/noise.jsonl
    python3 scripts/grouping_episode_study.py summary        $O/pairs.jsonl.gz
    python3 scripts/grouping_episode_study.py member-summary $O/member.jsonl.gz
    python3 scripts/grouping_episode_study.py noise-summary  $O/noise.jsonl.gz

## Findings (FIFO-like AQMs unless stated)

1. **Episode end.** The detector's alarm end is about 1 s after the router's
   GT1 end and spread 280 / 1780 ms (p50 / p90) between members of the same
   group. The end read from the delay itself (queue delay < 10 ms) is 8 ms from
   the router end and 47 / 245 ms between members. Merging gaps < 200 ms cuts the
   p90 for self-ending scenarios (tcpbbr, tcpcubic, ppbp) from 663 to 239 ms.
   Early ends (p10 about −2 s against the router) remain; most likely the GT1
   standing-queue definition outlasting the client's 10 ms threshold.
   Decision: the end is not used, neither as an event nor in the agreement score.
2. **Hard case.** Different bottlenecks congested at the same time (DIFF-conc,
   K1 and K6, 558 pairs) start 58 ms apart (SAME: 42 ms). The window cannot
   separate them. Correlation p50 0.77 vs SAME 0.94; mean level difference
   20 vs 7 ms; peak ratio is useless (0.98 vs 0.99, equal severities by design).
   Best clean threshold pair (corr ≥ 0.9 and level difference ≤ 8 ms) still
   passes 5 % of DIFF-conc (SAME 51 %).
3. **Window.** Narrowing 300 → 150 ms (delay-based start) keeps 92 % of SAME and
   drops DIFF-conc from 91 to 74 %; shifted events and false alarms are already
   outside at 300 ms. Decision: 150 ms, delay-based start, gaps < 200 ms merged.
4. **Events to membership.** Every positive evidence entry is at the cap
   (0.55 A = 2.50, base ln(p_det / p_fa) = 3.28; c_lag, c_mag never below 1), and
   A = 4.55, so two entries make a member unless decay (gap > 60 s) or a silent
   event intervenes. FIFO: 270 / 323 memberships after exactly 2 positive entries
   (more: negative evidence 33, decay 20); reporting (confirmed leaf) is not later
   in 98 %. The 3–5 "events" are events the flow took part in that carry no
   evidence: SOLO, GLOBAL, C (K1 / K6 median 5 events, 2 positive entries).
   Time to membership is set by how often a clean event arrives (p50 17 s, p90 96 s
   from the first shared window). A "1 high-agreement + 1 normal event" rule
   therefore changes nothing; only one-event membership would, and that is rejected.
5. **Noise.** Per-ACK noise added to each client's OWD queue delay before the
   5-ACK median (white, or low-passed with a 200 ms time constant), metric windows
   fixed from the clean series. Ranking power (AUC SAME vs DIFF-conc) holds better
   for the level difference (0.88 clean, 0.85 white / 0.77 correlated at 20 ms)
   than for correlation (0.85 → 0.73 / 0.65). Thresholds fixed on clean data do
   not hold: both together pass SAME 73 % clean, 26 % (white) / 7 % (correlated)
   at 20 ms; on self-ending scenarios 61 % clean, 7 % at 10 ms white. Usable only
   with thresholds tied to a measured per-client noise floor.

fq_codel / cake: no metric separates (SAME correlation about 0.1, level difference
56 ms); left as a limit until per-flow router counters give a per-flow truth.
