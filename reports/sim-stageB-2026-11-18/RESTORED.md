# Restored 2026-11-19 (evening)

This folder was deleted by accident on 2026-11-19, together with the stage B v1 runs and their tick caches
(simulation/runs/stageB-2026-11-18*, reports/sim-cache/stageB-2026-11-18*). There is no git history or trash copy.

- README.md: restored byte for byte from the session record (the last Write of the file, 2026-11-18 21:01 EST; no
  later edit of it was found).
- Not restorable: the v1 runs no longer exist, and these files were generated from them.
  - tables.md, tables-matched.md, tables-spec.md, rows*.jsonl, compare-*.log (stageb_compare);
  - applimited-check.md (applimited_check.py, needed the v1 A1 run);
  - rerun-diff.md (firstbuild against v1).
  The v1 values that later reports use survive there: the B2 report's agreement table (the "v1" columns) and
  reports/sim-stageB2-applimited/extra.md.
- sizes-n100.md: can be regenerated from simulation/runs/smoke100 (still present) if wanted.
