# Diagnosis of the corrected test's loss of power (E1-0.5)

## 4. Both ends of the trade-off (same runs, single-queue, r1 / r2)

| test | alpha | false-split share (single-leaf runs / every leaf alone) | pair P | leaf F1 | pair R |
|---|---|---|---|---|---|
| first | 0.05 | 0.082 / 0.062 | 0.988 / 0.989 | 0.965 / 0.965 | 0.997 / 0.991 |
| first | 0.01 | 0.061 / 0.046 | 0.988 / 0.988 | 0.965 / 0.965 | 0.997 / 0.992 |
| first | 0.1 | 0.129 / 0.124 | 0.989 / 0.989 | 0.965 / 0.965 | 0.996 / 0.990 |
| corrected | 0.05 | 0.007 / 0.007 | 0.930 / 0.871 | 0.952 / 0.934 | 0.993 / 0.996 |
| corrected | 0.01 | 0.007 / 0.007 | 0.922 / 0.866 | 0.951 / 0.933 | 0.993 / 0.999 |
| corrected | 0.1 | 0.007 / 0.007 | 0.932 / 0.873 | 0.952 / 0.935 | 0.993 / 0.995 |

## 1. Corrected test by the number of true leaves and a stimulated shared upstream (single-queue, r1 / r2)

| group | runs | leaf F1 corrected | pair P corrected | pair P first test | leaf F1 first test |
|---|---|---|---|---|---|
| 1 leaf, all | 149 | 0.967 / 0.960 | 1.000 / 1.000 | 1.000 / 1.000 | 0.967 / 0.960 |
| 1 leaf, no stimulated shared upstream | 149 | 0.967 / 0.960 | 1.000 / 1.000 | 1.000 / 1.000 | 0.967 / 0.960 |
| 2 leaves, all | 51 | 0.930 / 0.856 | 0.820 / 0.675 | 0.946 / 0.970 | 0.966 / 0.979 |
| 2 leaves, no stimulated shared upstream | 2 | 0.922 / 0.819 | 0.784 / 0.580 | 1.000 / 0.965 | 0.990 / 0.990 |
| 2 leaves, shared upstream stimulated | 49 | 0.931 / 0.859 | 0.822 / 0.679 | 0.944 / 0.970 | 0.964 / 0.979 |
| 3 leaves, all | 14 | 0.887 / 0.921 | 0.950 / 0.831 | 1.000 / 0.975 | 0.941 / 0.984 |
| 3 leaves, no stimulated shared upstream | 14 | 0.887 / 0.921 | 0.950 / 0.831 | 1.000 / 0.975 | 0.941 / 0.984 |
| >= 4 leaves, all | 4 | 0.763 / 0.782 | 0.462 / 0.476 | 0.899 / 0.933 | 0.943 / 0.956 |
| >= 4 leaves, shared upstream stimulated | 4 | 0.763 / 0.782 | 0.462 / 0.476 | 0.899 / 0.933 | 0.943 / 0.956 |

## 2. Pairs of true leaves left merged by the corrected test (alpha 0.05, V-bin, end of run)

5 merged pairs (detail per event in [diag-merged-pairs.json](diag-merged-pairs.json)). log(1 / alpha) = 3.00.

| leaves in the merged group | pairs | events with exactly one of the two on, p50 | oracle split log E end, in-sample null p50 / share >= threshold | oracle split log E end, predictive null p50 / share | proposed split log E end, in-sample p50 | null m0 / f0 p50 |
|---|---|---|---|---|---|---|
| 2 | 5 | 18 | 100.9 / 1.00 | 161.9 / 1.00 | 30.3 | 0.000 / 0.343 |

