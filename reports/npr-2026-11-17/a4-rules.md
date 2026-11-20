# A.4 validation: rules fixed before any result (user, 2026-11-18)

- Validation list: valset.md / valset.json as produced by valset.py (frozen, read-only; sha256 below). No
  case-by-case moves (N4 hconc f000 robustness; L8 hytb rev and M m8-mixab main). Gate runs, not-reliable and
  health_unverified runs excluded as listed.
- Start only after K3 has finished and its health checks are done (the 23 missing main runs in). No changes after
  results are seen.
- ~~20-runs-per-seed condition~~ and ~~"too few to read alone" mark~~: removed 2026-11-19 (see the addendum at the
  end). Decision on the main table's r1 and r2 totals. Run counts next to every value.
- Decision rule on r1 and r2. r3 and later: one separate labelled column, never merged into r1 / r2. If that column
  clearly contradicts the r1 / r2 outcome (fails a condition both r1 and r2 pass, or passes one both fail), the
  decision is marked "not reliable", reported, and the work stops.
- Main table also shown split into "FB-* cells" and "all other cells", same measures; decision on the whole table.
- Decision: NPR-B if pair P >= 0.90 in r1 and r2 and leaf F1 >= frozen SETS on the same runs (its false-split share
  reported with the 2a breakdown); else NPR-A under the same two conditions plus false-split share <= alpha; else
  SETS stays and NPR is future work. The other NPR row is reported next to the chosen one.
- Robustness table reported, not part of the decision. Held-out N1-N5 stays closed.
- Measures (note B): pair P with 95 % bootstrap interval (runs within a seed), pair R, leaf F1, false-split share,
  root split delay p50 / p90, time to first correct group p50 / p90 from the leaf's first stimulus, late joiner;
  accuracy by events seen with plateau point (events and seconds, p50 / p90); B.b cost (per step, 5 repeats).
180371ed60b0964a5c14c9e09c183c4e4519bfd8ff7832c4976b3db72011c335  valset.py
a58186a661dcf69fe0d71ec02671a72d55151cd49c6b81a5c10e6d9ab69a8a2f  valset.md
9a6e55a23ce5b96adc51bb32a150e9e1744df85c5ca2046b1c79e109a53ec070  valset.json

## Addendum 2026-11-19: run-id mapping for the 8 K3 I1 ip1.2 runs (user decision; valset files unchanged)

The 8 K3 runs `v4-I1-*-ip1.2-*` never ran (the runtime refuses "." in a run id:
`^[a-zA-Z0-9][a-zA-Z0-9_-]{0,62}$`). They are run now on the K3 binary (qvideo/build, 2026-11-15) together with the
re-runs, in the re-run folder, under a new run id with "." -> "p". Only the run id and the generated file names
change: scripts/rerun_v4.py regenerates them with the v4 planner unchanged, checks the files identical to the K3
`_gen` files, then byte-copies them to the new names (the plan still records variant "ip1.2"). The frozen valset keeps
each run in its assigned table; validation reads them under the new names from the re-run folder:

| valset name (frozen) | run id now | table |
|---|---|---|
| v4-I1-calm-ip1.2-pfifo-r1 | v4-I1-calm-ip1p2-pfifo-r1 | as in valset.json |
| v4-I1-calm-ip1.2-pfifo-r2 | v4-I1-calm-ip1p2-pfifo-r2 | as in valset.json |
| v4-I1-hhier-ip1.2-pfifo-r1 | v4-I1-hhier-ip1p2-pfifo-r1 | as in valset.json |
| v4-I1-hhier-ip1.2-pfifo-r2 | v4-I1-hhier-ip1p2-pfifo-r2 | as in valset.json |
| v4-I1-sburst-ip1.2-codel-r1 | v4-I1-sburst-ip1p2-codel-r1 | as in valset.json |
| v4-I1-sburst-ip1.2-codel-r2 | v4-I1-sburst-ip1p2-codel-r2 | as in valset.json |
| v4-I1-sburst-ip1.2-pfifo-r1 | v4-I1-sburst-ip1p2-pfifo-r1 | as in valset.json |
| v4-I1-sburst-ip1.2-pfifo-r2 | v4-I1-sburst-ip1p2-pfifo-r2 | as in valset.json |

Health checks as for any K3 run; a run that fails a health check is handled by the existing rules. Validation (A.4)
starts after these 8 runs and their health check are in.

## Addendum 2026-11-19: interval method (user decision, recorded before any validation result is computed)

- Method: paired percentile bootstrap over runs within one seed (r1 alone, r2 alone). One replicate draws n runs with
  replacement from that seed's run list (n = the number of runs in it); every candidate and frozen SETS are scored on
  the same drawn runs. 10,000 replicates; 95 % interval = 2.5th and 97.5th percentiles. Every interval is reported next
  to its point estimate (the value on the runs as they are).
- RNG: one generator, numpy.random.default_rng(20261119), consumed in the fixed order main r1, main r2, main r3+,
  robustness r1, r2, r3+ (each seed column takes its own 10,000 x n index draws in turn); the draws are made once and
  shared by all candidates. (Wording made precise 2026-11-19 before any result; the earlier line said "one generator
  per (table, seed column)", which was ambiguous.)
- Statistics recomputed on each replicate exactly as the point estimate: pair precision pooled over the drawn runs
  (sum of correct pairs / sum of predicted pairs, as step12_report.pooled); leaf F1 = mean of per-run leaf F1;
  difference = candidate leaf F1 - frozen SETS leaf F1 on the same replicate (interval of the difference, not of
  each value).
- Runs resampled per seed, as listed in valset.json: main r1 38, main r2 37 (decision); main r3+ 52 (separate column);
  robustness r1 86, r2 84, r3+ 47 (reported only). If a run drops out under the existing health / re-run rules, the
  count actually resampled is reported next to the result; the list itself is not changed.
- Same method for the pair precision intervals and the leaf F1 difference intervals. ~~Campaign / cell columns and the
  FB-* / other split: point values with run counts (no interval).~~ Replaced by the addendum below.

## Addendum 2026-11-19 (2): user changes, recorded before any validation result is computed

1. The "too few to read alone" mark is removed. No column is labelled by its run count.
2. The condition that the main table needs at least 20 runs per seed is removed. Run counts are reported next to every
   value (main table 38 / 37); no minimum is applied.

Breakdown columns (per campaign, per cell, FB-* cells against all other cells), every column regardless of size:
point value, number of runs, and the interval by the same method on the same resampled-run lists restricted to that
column's runs (per replicate: the drawn runs that belong to the column; a replicate that draws none of them is
skipped and the number of skipped replicates is reported). Where a column has few runs, the per-run values are listed
as well. Under the tables, one plain sentence: intervals computed from a handful of runs are rough and can be too
narrow; the per-run values are shown for that reason. No threshold attached to that sentence.

Reporting: at the top of the report (and in chat), a separate list of the columns that rest on few runs: column
name, table, seed, number of runs, sorted by number of runs, smallest first. A notice, not a judgment: those values are
neither marked unreliable nor left out.

Unchanged: decision on the main table's r1 and r2 totals only; r3+ separate column with the "not reliable" stop rule;
pair precision >= 0.90 in both seeds; leaf F1 rule (if not met: difference with its interval, per-cell breakdown,
stop; the user decides).

## Addendum 2026-11-19 (3): user decisions, recorded before any validation result is computed

1. "Few runs" notice: the top of the validation report lists the columns that rest on 5 runs or fewer (column, table,
   seed, number of runs), smallest first. A notice only: no value is marked unreliable or left out; per-run values are
   shown for those columns (the same threshold: 5 runs or fewer).
2. v4-C1-sjoin-copa-pfifo-r2 stays in the frozen validation list where it is (robustness table), flagged in the report
   with the reason: one unmatched drop record at the router (trace has one extra drop row against the kernel counter;
   GT-Q / GT-H on that hop affected by one packet); client-side inputs unaffected. Its re-run (re-run folder, same run
   id) is shown next to it as an extra row and does not replace it; it enters no table total. No change to valset.*.
