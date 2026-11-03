# SBD baselines: DCW, rmcatSBD, dcSBD (vendored)

General shared-bottleneck detection baselines, not FlowBot (FlowBot is a
separate baseline). The code is taken from the FlowBot repository, where they
are FlowBot's comparison methods (https://github.com/PrinceS17/flowbot,
commit a7a21fa, `src/`):

- DCW: wavelet-denoised OWD cross-correlation (Kim et al.)
- rmcatSBD: RFC 8382 summary statistics and its threshold-based grouping
- dcSBD: RFC 8382 statistics grouped by graph clustering (Chinese Whispers)

Run them on quiclab runs with `scripts/sbd_baselines.py`.

| file | origin | changes |
|---|---|---|
| `sbd.py` | `src/sbd.py` | import paths; one-line label fix in `rmcat_clustering` (below) |
| `denoise.py` | `src/denoise.py` | none |
| `cluster.py` | `src/siamese/cluster.py` | `import torch` made optional (only its batched branch, unused here, needs it) |
| `chinese_whispers.py` | `src/siamese/chinese_whispers.py` | none |
| `preprocess.py` | `measure_time` from `src/siamese/preprocess.py` | verbatim function only (rest of the module needs torch) |
| `detector.py` | `CobottleneckDetector` from `src/detector.py` | methods copied verbatim (AST-extracted); own `__init__` |

`detector.py` cannot be imported from the FlowBot repo as is: it imports
`models.Pipeline`, which does not exist in that snapshot (`src/models/` holds only
`.pt` files), plus torch and pytorch_lightning. The original `__init__` also needs
ground-truth labels and unpickles a scikit-learn 0.24 classifier; DCW and SBD use
neither, so `__init__` here only sets the attributes the copied methods read.

The one algorithm-side change: rmcatSBD labelled a non-bottlenecked flow with its
flow number while bottleneck groups are numbered 0..k-1, so the two collided (a
non-bottlenecked flow looked grouped with a bottleneck group; 12 % of
non-bottlenecked flow-windows on a test run). It now gets `max(flow) + 1 + flow`,
the same idea dcSBD already uses (`f_max + ri + 1`). Decisions are unchanged; only
label numbers move.

Known behaviour kept as is:
- `classify()` needs a `label` column for DCW (it reads `tmp_df` only when present).
- DCW's threshold comes from `model_th` (fallback 0.5; FlowBot's evaluation
  pipeline passes 0.2 unless configured; the paper uses 0.8, our default).
- Written for pandas 1.5: needs pandas < 3 (pandas 3 drops grouping columns in
  `groupby().apply`); pandas 2.2 prints FutureWarnings.
