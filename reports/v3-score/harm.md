# Harm onset, GT-Q time coverage, fq_codel GT-H

Runs with a valid GT-Q: 201. Every value: rep 1 / rep 2 unless marked. Script: reports/v3-score/harm.py.

## A. Alarm at harm onset, v2-owd (GT-H 600 harmful forward episodes)

| AQM | harmful | overlap at any time (the 99 %) | hit: start in collar (gtq_score recall) | alarm_before_harm (hit, first start before t_harm) | on at t_harm | on, span opened in collar | on, held from before the collar | off at t_harm |
|---|---|---|---|---|---|---|---|---|
| pfifo | 3735 / 3718 | 1.00 / 1.00 | 0.77 / 0.79 | 0.77 / 0.79 | 1.00 / 1.00 | 0.77 / 0.79 | 0.23 / 0.21 | 0.00 / 0.00 |
| codel | 2797 / 2627 | 1.00 / 1.00 | 0.66 / 0.72 | 0.66 / 0.72 | 1.00 / 1.00 | 0.66 / 0.72 | 0.34 / 0.28 | 0.00 / 0.00 |
| fq_codel | 2773 / 2889 | 0.96 / 0.97 | 0.21 / 0.19 | 0.20 / 0.18 | 0.98 / 0.99 | 0.20 / 0.19 | 0.78 / 0.80 | 0.02 / 0.01 |
| pie | 698 / 671 | 1.00 / 0.99 | 0.52 / 0.52 | 0.52 / 0.52 | 1.00 / 0.99 | 0.52 / 0.52 | 0.48 / 0.47 | 0.00 / 0.01 |
| all | 10038 / 10420 | 0.99 / 0.99 | 0.57 / 0.58 | 0.56 / 0.57 | 0.99 / 1.00 | 0.57 / 0.58 | 0.43 / 0.42 | 0.01 / 0.00 |

How long before harm the alarm had opened (lead = t_harm - span start, episodes on at t_harm), v2-owd, s:

| AQM | on at t_harm | lead p10 | p25 | p50 | p75 | p90 | lead < 0.2 s | 0.2-1 s | 1-5 s | > 5 s |
|---|---|---|---|---|---|---|---|---|---|---|
| pfifo | 3725 / 3716 | 0.60 / 0.58 | 0.79 / 0.76 | 1.30 / 1.29 | 3.26 / 3.14 | 6.67 / 6.99 | 0.00 / 0.00 | 0.38 / 0.39 | 0.46 / 0.45 | 0.16 / 0.16 |
| codel | 2796 / 2627 | 0.82 / 0.80 | 1.07 / 1.04 | 1.59 / 1.49 | 3.34 / 2.61 | 6.55 / 6.26 | 0.00 / 0.00 | 0.20 / 0.22 | 0.64 / 0.65 | 0.16 / 0.13 |
| fq_codel | 2718 / 2859 | 0.61 / 0.60 | 1.71 / 1.88 | 3.85 / 4.04 | 6.83 / 6.75 | 9.07 / 9.03 | 0.00 / 0.00 | 0.18 / 0.17 | 0.43 / 0.44 | 0.38 / 0.39 |
| pie | 696 / 667 | 0.79 / 0.77 | 0.96 / 0.92 | 1.35 / 1.30 | 2.96 / 3.16 | 5.98 / 6.40 | 0.00 / 0.00 | 0.31 / 0.34 | 0.54 / 0.50 | 0.14 / 0.16 |
| all | 9970 / 10383 | 0.67 / 0.64 | 0.95 / 0.93 | 1.76 / 1.74 | 4.41 / 4.41 | 7.99 / 8.00 | 0.00 / 0.00 | 0.27 / 0.28 | 0.51 / 0.50 | 0.22 / 0.22 |

Episodes on at t_harm with the span opened BEFORE the collar (held from an earlier alarm), v2-owd:

| AQM | n | span start in an earlier episode's collar | gap to that episode p50 s | gap p90 s | held before t0 p50 s | p90 s | episode duration p50 s |
|---|---|---|---|---|---|---|---|
| pfifo | 855 / 763 | 1.00 / 1.00 | 0.46 / 0.08 | 6.57 / 4.63 | 4.10 / 4.77 | 10.03 / 10.36 | 0.07 / 0.06 |
| codel | 948 / 737 | 1.00 / 1.00 | -1.77 / -1.27 | 5.65 / 4.70 | 3.34 / 3.17 | 9.49 / 10.17 | 0.06 / 0.06 |
| fq_codel | 2156 / 2318 | 1.00 / 1.00 | 2.55 / 2.76 | 7.36 / 7.29 | 4.25 / 4.26 | 8.77 / 8.71 | 0.38 / 0.39 |
| pie | 334 / 316 | 1.00 / 1.00 | 0.58 / 0.37 | 5.23 / 4.79 | 2.46 / 2.60 | 8.14 / 8.71 | 0.09 / 0.10 |
| all | 4293 / 4368 | 1.00 / 1.00 | 1.27 / 1.33 | 6.96 / 6.64 | 3.88 / 4.08 | 9.09 / 9.38 | 0.19 / 0.25 |

Episodes off at t_harm, v2-owd: next alarm start after t_harm

| AQM | off at t_harm | next start inside the collar (late hit) | next start p50 s after t_harm | no later start |
|---|---|---|---|---|
| pfifo | 10 / 2 | 0.30 / 0.50 | 1.56 / 0.32 | 0 / 0 |
| codel | 1 / 0 | 1.00 / - | 1.03 / - | 0 / 0 |
| fq_codel | 55 / 30 | 0.55 / 0.63 | 0.38 / 0.87 | 0 / 0 |
| pie | 2 / 4 | 1.00 / 0.00 | 1.29 / 15.34 | 0 / 0 |
| all | 68 / 37 | 0.53 / 0.57 | 0.46 / 0.88 | 0 / 0 |

## A. Alarm at harm onset, v2-fixed-owd (GT-H 600 harmful forward episodes)

| AQM | harmful | overlap at any time (the 99 %) | hit: start in collar (gtq_score recall) | alarm_before_harm (hit, first start before t_harm) | on at t_harm | on, span opened in collar | on, held from before the collar | off at t_harm |
|---|---|---|---|---|---|---|---|---|
| pfifo | 3735 / 3718 | 1.00 / 1.00 | 0.75 / 0.78 | 0.75 / 0.77 | 1.00 / 1.00 | 0.75 / 0.78 | 0.25 / 0.22 | 0.00 / 0.00 |
| codel | 2797 / 2627 | 1.00 / 1.00 | 0.66 / 0.72 | 0.66 / 0.72 | 1.00 / 1.00 | 0.66 / 0.72 | 0.34 / 0.28 | 0.00 / 0.00 |
| fq_codel | 2773 / 2889 | 0.97 / 0.97 | 0.20 / 0.18 | 0.19 / 0.17 | 0.98 / 0.99 | 0.20 / 0.18 | 0.79 / 0.81 | 0.02 / 0.01 |
| pie | 698 / 671 | 1.00 / 0.99 | 0.52 / 0.52 | 0.52 / 0.52 | 1.00 / 0.99 | 0.52 / 0.52 | 0.48 / 0.47 | 0.00 / 0.01 |
| all | 10038 / 10420 | 0.99 / 0.99 | 0.56 / 0.57 | 0.55 / 0.57 | 0.99 / 1.00 | 0.56 / 0.57 | 0.44 / 0.43 | 0.01 / 0.00 |

How long before harm the alarm had opened (lead = t_harm - span start, episodes on at t_harm), v2-fixed-owd, s:

| AQM | on at t_harm | lead p10 | p25 | p50 | p75 | p90 | lead < 0.2 s | 0.2-1 s | 1-5 s | > 5 s |
|---|---|---|---|---|---|---|---|---|---|---|
| pfifo | 3728 / 3714 | 0.58 / 0.57 | 0.78 / 0.75 | 1.30 / 1.30 | 3.42 / 3.33 | 7.38 / 7.74 | 0.01 / 0.01 | 0.38 / 0.38 | 0.44 / 0.44 | 0.17 / 0.17 |
| codel | 2795 / 2627 | 0.79 / 0.77 | 1.05 / 1.01 | 1.56 / 1.46 | 3.30 / 2.56 | 6.59 / 6.28 | 0.00 / 0.00 | 0.22 / 0.24 | 0.62 / 0.63 | 0.16 / 0.13 |
| fq_codel | 2731 / 2861 | 0.63 / 0.63 | 1.84 / 1.95 | 4.04 / 4.16 | 7.21 / 6.97 | 9.42 / 9.24 | 0.00 / 0.00 | 0.18 / 0.16 | 0.42 / 0.43 | 0.40 / 0.40 |
| pie | 696 / 667 | 0.76 / 0.74 | 0.92 / 0.89 | 1.30 / 1.24 | 2.92 / 3.13 | 5.93 / 6.39 | 0.00 / 0.00 | 0.35 / 0.36 | 0.51 / 0.49 | 0.14 / 0.15 |
| all | 9985 / 10383 | 0.67 / 0.63 | 0.94 / 0.92 | 1.80 / 1.75 | 4.58 / 4.57 | 8.38 / 8.33 | 0.00 / 0.00 | 0.28 / 0.28 | 0.49 / 0.49 | 0.23 / 0.23 |

Episodes on at t_harm with the span opened BEFORE the collar (held from an earlier alarm), v2-fixed-owd:

| AQM | n | span start in an earlier episode's collar | gap to that episode p50 s | gap p90 s | held before t0 p50 s | p90 s | episode duration p50 s |
|---|---|---|---|---|---|---|---|
| pfifo | 928 / 827 | 0.97 / 0.94 | 0.62 / 0.13 | 8.83 / 4.95 | 4.41 / 5.17 | 11.53 / 13.68 | 0.08 / 0.07 |
| codel | 951 / 735 | 1.00 / 1.00 | -1.94 / -1.35 | 5.55 / 4.91 | 3.34 / 3.15 | 9.58 / 10.17 | 0.06 / 0.06 |
| fq_codel | 2187 / 2343 | 1.00 / 1.00 | 2.72 / 2.91 | 7.95 / 7.71 | 4.41 / 4.36 | 9.10 / 8.97 | 0.38 / 0.39 |
| pie | 334 / 315 | 1.00 / 1.00 | 0.55 / 0.40 | 5.23 / 4.80 | 2.45 / 2.58 | 8.01 / 8.72 | 0.09 / 0.10 |
| all | 4400 / 4454 | 0.99 / 0.99 | 1.46 / 1.50 | 7.68 / 7.06 | 4.02 / 4.19 | 9.53 / 9.76 | 0.20 / 0.26 |

Episodes off at t_harm, v2-fixed-owd: next alarm start after t_harm

| AQM | off at t_harm | next start inside the collar (late hit) | next start p50 s after t_harm | no later start |
|---|---|---|---|---|
| pfifo | 7 / 4 | 0.71 / 1.00 | 0.35 / 0.02 | 0 / 0 |
| codel | 2 / 0 | 1.00 / - | 0.65 / - | 0 / 0 |
| fq_codel | 42 / 28 | 0.60 / 0.64 | 0.38 / 0.90 | 0 / 0 |
| pie | 2 / 4 | 1.00 / 0.00 | 1.35 / 15.39 | 0 / 0 |
| all | 53 / 37 | 0.64 / 0.62 | 0.38 / 0.90 | 0 / 0 |

## B. How much of the time GT-Q covers, and the precision of a random alarm

Flow time after warm-up, sub-ctrl excluded. episode = union of forward GT-Q episodes [t0, t1]; collar = union of collars [t0 - W, t1 + d_obs + W]; gray = gray intervals outside collars. Random precision (uniform) = collar / (T - gray); random precision (alarm-weighted) = the same per flow, weighted by the detector's alarms on that flow. Detector precision = gtq_score's (alarms in a collar / (those + FP)), from reports/v3-detector/rows.jsonl.

### v2-owd

| runs | AQM | episode share of time | collar share | gray share | random precision (uniform) | random precision (alarm-weighted) | detector precision | detector alarm-on share of time | GT-Q episodes per flow-minute |
|---|---|---|---|---|---|---|---|---|---|
| calm | pfifo | 0.08 / 0.08 | 0.21 / 0.20 | 0.02 / 0.02 | 0.21 / 0.21 | 0.37 / 0.32 | 1.00 / 1.00 | 0.00 / 0.00 | 84.2 / 75.1 |
| calm | codel | 0.11 / 0.11 | 0.22 / 0.22 | 0.03 / 0.04 | 0.23 / 0.23 | 0.50 / 0.44 | 1.00 / 0.96 | 0.00 / 0.01 | 50.5 / 50.3 |
| calm | all | 0.09 / 0.09 | 0.21 / 0.21 | 0.02 / 0.03 | 0.22 / 0.21 | 0.44 / 0.40 | 1.00 / 0.98 | 0.00 / 0.00 | 77.1 / 67.4 |
| stimulus | pfifo | 0.31 / 0.31 | 0.40 / 0.40 | 0.01 / 0.01 | 0.41 / 0.41 | 0.42 / 0.42 | 0.99 / 1.00 | 0.30 / 0.31 | 56.5 / 54.8 |
| stimulus | codel | 0.31 / 0.31 | 0.41 / 0.41 | 0.01 / 0.01 | 0.41 / 0.41 | 0.42 / 0.42 | 1.00 / 1.00 | 0.30 / 0.30 | 62.5 / 60.8 |
| stimulus | fq_codel | 0.56 / 0.57 | 0.74 / 0.76 | 0.09 / 0.09 | 0.82 / 0.83 | 0.78 / 0.80 | 0.98 / 0.98 | 0.14 / 0.13 | 108.7 / 112.5 |
| stimulus | pie | 0.32 / 0.32 | 0.41 / 0.42 | 0.00 / 0.01 | 0.42 / 0.42 | 0.42 / 0.43 | 0.98 / 1.00 | 0.31 / 0.32 | 62.9 / 61.6 |
| stimulus | all | 0.36 / 0.36 | 0.47 / 0.46 | 0.02 / 0.02 | 0.48 / 0.47 | 0.46 / 0.46 | 0.99 / 1.00 | 0.27 / 0.28 | 68.0 / 66.9 |
| all | pfifo | 0.28 / 0.29 | 0.38 / 0.38 | 0.01 / 0.01 | 0.38 / 0.39 | 0.42 / 0.42 | 0.99 / 1.00 | 0.26 / 0.28 | 60.6 / 56.6 |
| all | codel | 0.30 / 0.30 | 0.39 / 0.39 | 0.01 / 0.01 | 0.40 / 0.40 | 0.42 / 0.42 | 1.00 / 1.00 | 0.28 / 0.28 | 61.7 / 60.1 |
| all | fq_codel | 0.56 / 0.57 | 0.74 / 0.76 | 0.09 / 0.09 | 0.82 / 0.83 | 0.78 / 0.80 | 0.98 / 0.98 | 0.14 / 0.13 | 108.7 / 112.5 |
| all | pie | 0.32 / 0.32 | 0.41 / 0.42 | 0.00 / 0.01 | 0.42 / 0.42 | 0.42 / 0.43 | 0.98 / 1.00 | 0.31 / 0.32 | 62.9 / 61.6 |
| all | all | 0.33 / 0.34 | 0.44 / 0.45 | 0.02 / 0.02 | 0.45 / 0.46 | 0.46 / 0.46 | 0.99 / 1.00 | 0.25 / 0.26 | 68.8 / 66.9 |

### v2-fixed-owd

| runs | AQM | episode share of time | collar share | gray share | random precision (uniform) | random precision (alarm-weighted) | detector precision | detector alarm-on share of time | GT-Q episodes per flow-minute |
|---|---|---|---|---|---|---|---|---|---|
| calm | pfifo | 0.08 / 0.08 | 0.21 / 0.20 | 0.02 / 0.02 | 0.21 / 0.21 | 0.39 / 0.43 | 0.89 / 0.91 | 0.03 / 0.03 | 84.2 / 75.1 |
| calm | codel | 0.11 / 0.11 | 0.22 / 0.22 | 0.03 / 0.04 | 0.23 / 0.23 | 0.43 / 0.39 | 0.84 / 0.77 | 0.15 / 0.15 | 50.5 / 50.3 |
| calm | all | 0.09 / 0.09 | 0.21 / 0.21 | 0.02 / 0.03 | 0.22 / 0.21 | 0.41 / 0.41 | 0.87 / 0.83 | 0.06 / 0.06 | 77.1 / 67.4 |
| stimulus | pfifo | 0.31 / 0.31 | 0.40 / 0.40 | 0.01 / 0.01 | 0.41 / 0.41 | 0.42 / 0.42 | 0.99 / 0.99 | 0.32 / 0.33 | 56.5 / 54.8 |
| stimulus | codel | 0.31 / 0.31 | 0.41 / 0.41 | 0.01 / 0.01 | 0.41 / 0.41 | 0.42 / 0.42 | 1.00 / 1.00 | 0.31 / 0.31 | 62.5 / 60.8 |
| stimulus | fq_codel | 0.56 / 0.57 | 0.74 / 0.76 | 0.09 / 0.09 | 0.82 / 0.83 | 0.80 / 0.81 | 0.95 / 0.95 | 0.21 / 0.21 | 108.7 / 112.5 |
| stimulus | pie | 0.32 / 0.32 | 0.41 / 0.42 | 0.00 / 0.01 | 0.42 / 0.42 | 0.42 / 0.43 | 1.00 / 1.00 | 0.32 / 0.33 | 62.9 / 61.6 |
| stimulus | all | 0.36 / 0.36 | 0.47 / 0.46 | 0.02 / 0.02 | 0.48 / 0.47 | 0.48 / 0.47 | 0.99 / 0.99 | 0.29 / 0.30 | 68.0 / 66.9 |
| all | pfifo | 0.28 / 0.29 | 0.38 / 0.38 | 0.01 / 0.01 | 0.38 / 0.39 | 0.42 / 0.42 | 0.98 / 0.99 | 0.28 / 0.30 | 60.6 / 56.6 |
| all | codel | 0.30 / 0.30 | 0.39 / 0.39 | 0.01 / 0.01 | 0.40 / 0.40 | 0.42 / 0.42 | 0.99 / 0.99 | 0.30 / 0.30 | 61.7 / 60.1 |
| all | fq_codel | 0.56 / 0.57 | 0.74 / 0.76 | 0.09 / 0.09 | 0.82 / 0.83 | 0.80 / 0.81 | 0.95 / 0.95 | 0.21 / 0.21 | 108.7 / 112.5 |
| all | pie | 0.32 / 0.32 | 0.41 / 0.42 | 0.00 / 0.01 | 0.42 / 0.42 | 0.42 / 0.43 | 1.00 / 1.00 | 0.32 / 0.33 | 62.9 / 61.6 |
| all | all | 0.33 / 0.34 | 0.44 / 0.45 | 0.02 / 0.02 | 0.45 / 0.46 | 0.47 / 0.47 | 0.98 / 0.98 | 0.27 / 0.28 | 68.8 / 66.9 |

## D. Is 'on at t_harm' high only because the alarm is on most of the time?

Harmful GT-H 600 forward episodes with t_harm after warm-up, sub-ctrl excluded. on-share = alarm-on time / flow time; on-share in queue = alarm-on time inside GT-Q forward episodes / episode time (an alarm that is on exactly while a queue exists, at random inside it); shift = the flow's own alarm spans kept, harm instants moved by a random circular offset over [warm-up, duration] (20 offsets per flow, mean and min-max of the pooled share).

### v2-owd

| runs | AQM | harmful | on at t_harm (observed) | on-share of time | on-share in queue time | shift baseline mean (min-max) |
|---|---|---|---|---|---|---|
| stimulus | pfifo | 3735 / 3718 | 1.00 / 1.00 | 0.30 / 0.31 | 0.79 / 0.80 | 0.32 (0.30-0.33) / 0.33 (0.31-0.34) |
| stimulus | codel | 2797 / 2627 | 1.00 / 1.00 | 0.30 / 0.30 | 0.81 / 0.81 | 0.31 (0.28-0.33) / 0.32 (0.30-0.33) |
| stimulus | fq_codel | 2773 / 2889 | 0.98 / 0.99 | 0.14 / 0.13 | 0.18 / 0.16 | 0.32 (0.29-0.35) / 0.34 (0.30-0.38) |
| stimulus | pie | 698 / 671 | 1.00 / 0.99 | 0.31 / 0.32 | 0.82 / 0.82 | 0.30 (0.24-0.37) / 0.30 (0.25-0.37) |
| stimulus | all | 10038 / 10420 | 0.99 / 1.00 | 0.27 / 0.28 | 0.62 / 0.63 | 0.31 (0.30-0.32) / 0.33 (0.31-0.34) |
| all | pfifo | 3735 / 3718 | 1.00 / 1.00 | 0.26 / 0.28 | 0.75 / 0.78 | 0.32 (0.30-0.33) / 0.33 (0.31-0.34) |
| all | codel | 2797 / 2627 | 1.00 / 1.00 | 0.28 / 0.28 | 0.79 / 0.79 | 0.31 (0.28-0.33) / 0.32 (0.30-0.33) |
| all | fq_codel | 2773 / 2889 | 0.98 / 0.99 | 0.14 / 0.13 | 0.18 / 0.16 | 0.32 (0.29-0.35) / 0.34 (0.30-0.38) |
| all | pie | 698 / 671 | 1.00 / 0.99 | 0.31 / 0.32 | 0.82 / 0.82 | 0.30 (0.24-0.37) / 0.30 (0.25-0.37) |
| all | all | 10038 / 10420 | 0.99 / 1.00 | 0.25 / 0.26 | 0.60 / 0.62 | 0.31 (0.30-0.32) / 0.33 (0.31-0.34) |

### v2-fixed-owd

| runs | AQM | harmful | on at t_harm (observed) | on-share of time | on-share in queue time | shift baseline mean (min-max) |
|---|---|---|---|---|---|---|
| stimulus | pfifo | 3735 / 3718 | 1.00 / 1.00 | 0.32 / 0.33 | 0.79 / 0.80 | 0.34 (0.33-0.36) / 0.35 (0.34-0.37) |
| stimulus | codel | 2797 / 2627 | 1.00 / 1.00 | 0.31 / 0.31 | 0.80 / 0.81 | 0.31 (0.28-0.33) / 0.32 (0.31-0.34) |
| stimulus | fq_codel | 2773 / 2889 | 0.98 / 0.99 | 0.21 / 0.21 | 0.25 / 0.23 | 0.36 (0.32-0.39) / 0.38 (0.33-0.41) |
| stimulus | pie | 698 / 671 | 1.00 / 0.99 | 0.32 / 0.33 | 0.81 / 0.81 | 0.30 (0.25-0.38) / 0.31 (0.26-0.38) |
| stimulus | all | 10038 / 10420 | 0.99 / 1.00 | 0.29 / 0.30 | 0.64 / 0.65 | 0.33 (0.32-0.35) / 0.35 (0.33-0.36) |
| all | pfifo | 3735 / 3718 | 1.00 / 1.00 | 0.28 / 0.30 | 0.76 / 0.78 | 0.34 (0.33-0.36) / 0.35 (0.34-0.37) |
| all | codel | 2797 / 2627 | 1.00 / 1.00 | 0.30 / 0.30 | 0.79 / 0.80 | 0.31 (0.28-0.33) / 0.32 (0.31-0.34) |
| all | fq_codel | 2773 / 2889 | 0.98 / 0.99 | 0.21 / 0.21 | 0.25 / 0.23 | 0.36 (0.32-0.39) / 0.38 (0.33-0.41) |
| all | pie | 698 / 671 | 1.00 / 0.99 | 0.32 / 0.33 | 0.81 / 0.81 | 0.30 (0.25-0.38) / 0.31 (0.26-0.38) |
| all | all | 10038 / 10420 | 0.99 / 1.00 | 0.27 / 0.28 | 0.63 / 0.64 | 0.33 (0.32-0.35) / 0.35 (0.33-0.36) |

## C. Per-episode vs merged-event GT-H 600 recall (alarm start in the collar)

Merged event: forward episodes of a flow with gap < G joined (M). recall = harmful merged events with an alarm start in the merged collar / harmful merged events.

### v2-owd

| AQM | per-episode recall (harmful n) | G 0.5 s: recall (harmful events, episodes per event) | G 1 s: recall (harmful events, episodes per event) | G 2 s: recall (harmful events, episodes per event) |
|---|---|---|---|---|
| pfifo | 0.77 (3735) / 0.79 (3718) | 0.82 (3355, 2.0) / 0.84 (3336, 1.9) | 0.93 (2402, 21.0) / 0.92 (2575, 19.3) | 0.98 (1467, 52.6) / 0.95 (1575, 47.7) |
| codel | 0.66 (2797) / 0.72 (2627) | 0.72 (2427, 2.1) / 0.78 (2308, 2.2) | 0.89 (1730, 20.3) / 0.88 (1770, 20.5) | 0.93 (1054, 53.3) / 0.93 (1004, 53.3) |
| fq_codel | 0.21 (2773) / 0.19 (2889) | 0.71 (699, 9.6) / 0.71 (654, 11.2) | 0.81 (581, 27.2) / 0.80 (545, 30.8) | 0.92 (294, 95.7) / 0.95 (257, 114.2) |
| pie | 0.52 (698) / 0.52 (671) | 0.79 (412, 3.8) / 0.78 (383, 3.8) | 0.94 (325, 24.4) / 0.91 (325, 19.1) | 0.98 (159, 72.8) / 0.97 (178, 60.1) |
| all | 0.57 (10038) / 0.58 (10420) | 0.77 (6928, 2.9) / 0.80 (6964, 3.0) | 0.90 (5071, 21.6) / 0.89 (5470, 20.7) | 0.96 (2993, 58.1) / 0.94 (3150, 55.8) |

### v2-fixed-owd

| AQM | per-episode recall (harmful n) | G 0.5 s: recall (harmful events, episodes per event) | G 1 s: recall (harmful events, episodes per event) | G 2 s: recall (harmful events, episodes per event) |
|---|---|---|---|---|
| pfifo | 0.75 (3735) / 0.78 (3718) | 0.80 (3355, 2.0) / 0.82 (3336, 1.9) | 0.91 (2402, 21.0) / 0.90 (2575, 19.3) | 0.97 (1467, 52.6) / 0.93 (1575, 47.7) |
| codel | 0.66 (2797) / 0.72 (2627) | 0.71 (2427, 2.1) / 0.78 (2308, 2.2) | 0.88 (1730, 20.3) / 0.88 (1770, 20.5) | 0.93 (1054, 53.3) / 0.93 (1004, 53.3) |
| fq_codel | 0.20 (2773) / 0.18 (2889) | 0.69 (699, 9.6) / 0.70 (654, 11.2) | 0.80 (581, 27.2) / 0.80 (545, 30.8) | 0.91 (294, 95.7) / 0.95 (257, 114.2) |
| pie | 0.52 (698) / 0.52 (671) | 0.77 (412, 3.8) / 0.77 (383, 3.8) | 0.93 (325, 24.4) / 0.90 (325, 19.1) | 0.98 (159, 72.8) / 0.97 (178, 60.1) |
| all | 0.56 (10038) / 0.57 (10420) | 0.76 (6928, 2.9) / 0.79 (6964, 3.0) | 0.89 (5071, 21.6) / 0.88 (5470, 20.7) | 0.95 (2993, 58.1) / 0.93 (3150, 55.8) |

