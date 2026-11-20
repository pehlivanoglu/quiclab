# Validation set (valset.py; from scenario definitions only)

Never-used runs only (K1 A1-A3, A8, A9; K2; K3). Assigned from <campaign>/_gen plan + topology, the re-run list and the manifest's health_unverified list; no run output read. K3 is still running: unfinished runs are counted (column 'pending').

## Main validation: single-queue, >= 2 leaves, static membership, BBR

Runs per seed: r1 38, r2 37, r3 18, r4 12, r5 12, r6 2, r7 2, r8 2, r9 2, r10 2; total 127 (pending 23).

| campaign | block | type / variant / aqm | why here | r1 | r2 | r3 | r4 | r5 | r6 | r7 | r8 | r9 | r10 | pending |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K1 | A8 | llong2 / def / codel | - | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K1 | A8 | llong2 / def / pfifo | - | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | N5 | hsparse / def / codel | - | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | N5 | hsparse / def / pfifo | - | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | N6 | hhier / bgbursty / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | N6 | hhier / bgmix / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X1 | hhier / s030 / codel | - | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X1 | hhier / s030 / pfifo | - | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X1 | hhier / s030 / pie | - | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X2 | hindep / s030 / codel | - | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X2 | hindep / s030 / pfifo | - | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X2 | huneven / uneven / codel | - | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X2 | huneven / uneven / pfifo | - | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X3 | hdepth / tree16 / pfifo | - | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X4 | hhier / ext / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X6 | hhier / hs50 / codel | - | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K2 | X6 | hhier / hs50 / pfifo | - | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | I1 | hhier / ip1.2 / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| K3 | I1 | hhier / ip6 / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| K3 | L1 | fbload / def / codel | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L1 | fbload / def / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L1 | fbload / def / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L10 | hhier / bgonoff / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L2 | fbcross / x20 / codel | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L2 | fbcross / x20 / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L2 | fbcross / x40 / codel | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L2 | fbcross / x40 / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L2 | fbcross / x60 / codel | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L2 | fbcross / x60 / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L2 | fbcross / x80 / codel | - | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L2 | fbcross / x80 / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L3 | fblag / def / codel | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L3 | fblag / def / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L4 | fbscale / par2 / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L4 | fbscale / par4x8 / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L4 | fbscale / par6 / pie | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L5 | fbcold / def / codel | - | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 8 |
| K3 | L5 | fbcold / def / pie | - | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 8 |
| K3 | L6 | ppar / def / codel | - | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| K3 | L6 | ppar / def / pfifo | - | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| K3 | L8 | hytb / bdp05 / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L8 | hytb / bdp1 / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L8 | hytb / bdp2 / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | L8 | hytb / rev / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| K3 | M | hhier / m7-noroot / pfifo | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| K3 | M | hhier / m8-mixab / mixab | - | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

## Robustness: other runs with a usable grouping truth

Runs per seed: r1 86, r2 84, r3 29, r4 9, r5 9; total 217 (pending 33).

| campaign | block | type / variant / aqm | why here | r1 | r2 | r3 | r4 | r5 | pending |
|---|---|---|---|---|---|---|---|---|---|
| K1 | A2 | sburst / def / cake | per-flow queue (cake, same-link reading); 1 leaf | 1 | 1 | 1 | 1 | 1 | 0 |
| K1 | A2 | sburst / def / codel | 1 leaf | 1 | 1 | 1 | 1 | 1 | 0 |
| K1 | A2 | sburst / def / fq_codel | per-flow queue (fq_codel, same-link reading); 1 leaf | 1 | 1 | 1 | 1 | 1 | 0 |
| K1 | A2 | sburst / def / pfifo | 1 leaf | 1 | 1 | 1 | 1 | 1 | 0 |
| K1 | A2 | sburst / def / pie | 1 leaf | 1 | 1 | 1 | 1 | 1 | 0 |
| K1 | A2 | sburst / def / red | 1 leaf | 1 | 1 | 1 | 1 | 1 | 0 |
| K1 | A3 | sjoin / def / codel | 1 leaf; join | 1 | 1 | 1 | 0 | 0 | 0 |
| K1 | A3 | sjoin / def / pfifo | 1 leaf; join | 1 | 1 | 1 | 0 | 0 | 0 |
| K1 | A3 | sramp / def / codel | 1 leaf | 1 | 1 | 1 | 0 | 0 | 0 |
| K1 | A3 | sramp / def / pfifo | 1 leaf | 1 | 1 | 1 | 0 | 0 | 0 |
| K1 | A3 | stcp / def / codel | 1 leaf | 1 | 1 | 1 | 0 | 0 | 0 |
| K1 | A3 | stcp / def / pfifo | 1 leaf | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N1 | hshift / def / codel | shifting bottleneck | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N1 | hshift / def / pfifo | shifting bottleneck | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N1 | hshift / sustained / pfifo | shifting bottleneck | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | N2 | spersist / def / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | N2 | spersist / def / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | N3 | hchurn / def / codel | churn | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N3 | hchurn / def / pfifo | churn | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N4 | hconc / f000 / pfifo | concurrent events | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N4 | hconc / f025 / pfifo | concurrent events | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N4 | hconc / f050 / pfifo | concurrent events | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N4 | hconc / f100 / pfifo | concurrent events | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | N7 | hjoin / def / codel | join | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | N7 | hjoin / def / pfifo | join | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T2 | sburst / jit10 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T2 | sburst / jit10 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T2 | sburst / jit2 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T2 | sburst / jit2 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T2 | sburst / jit5 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T2 | sburst / jit5 / pfifo | 1 leaf | 1 | 0 | 0 | 0 | 0 | 0 |
| K2 | T3 | sdense / def / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T3 | smild / u105 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T3 | smild / u105 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T3 | smild / u110 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T3 | smild / u110 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T3 | smild / u115 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | T3 | smild / u115 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K2 | X2 | amixed / access / codel | 1 leaf | 0 | 0 | 1 | 1 | 1 | 0 |
| K2 | X2 | amixed / access / pfifo | 1 leaf | 0 | 0 | 1 | 1 | 1 | 0 |
| K2 | X3 | sburst / s030u070 / pie | 1 leaf | 0 | 0 | 1 | 1 | 1 | 0 |
| K2 | X5 | sburst / hs50 / codel | 1 leaf | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | X5 | sburst / hs50 / pfifo | 1 leaf | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | X5 | sburst / hs70 / codel | 1 leaf | 1 | 1 | 1 | 0 | 0 | 0 |
| K2 | X5 | sburst / hs70 / pfifo | 1 leaf | 1 | 1 | 1 | 0 | 0 | 0 |
| K3 | C1 | amixed / copa / pfifo | 1 leaf; Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | C1 | hhier / copa / codel | Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | C1 | hhier / copa / pfifo | Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | C1 | hindep / copa / pfifo | Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | C1 | sburst / copa / codel | 1 leaf; Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | C1 | sburst / copa / fq_codel | per-flow queue (fq_codel, same-link reading); 1 leaf; Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | C1 | sburst / copa / pfifo | 1 leaf; Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | C1 | sjoin / copa / pfifo | 1 leaf; join; Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | C1 | stcp / copa / pfifo | 1 leaf; Copa | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | I1 | sburst / ip1.2 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 2 |
| K3 | I1 | sburst / ip1.2 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 2 |
| K3 | I1 | sburst / ip6 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | I1 | sburst / ip6 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | L11 | spause / def / pfifo | 1 leaf | 1 | 0 | 0 | 0 | 0 | 0 |
| K3 | L11 | sshort / def / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | L11 | sshort / def / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 0 |
| K3 | L9 | sbnsb / nsb / pfifo | concurrent events (NSB: both leaves at once) | 1 | 1 | 1 | 0 | 0 | 1 |
| K3 | L9 | sbnsb / sb / pfifo | 1 leaf; concurrent events (NSB: both leaves at once) | 1 | 1 | 1 | 0 | 0 | 1 |
| K3 | M | sburst / m1-q100 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m1-q300 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m10-ip2 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m10-ip8 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m11-bw4x1 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m11-bw4x12 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m11-bw4x8 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m12-jitfwd / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m12-jitrev / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m2-capdrop / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m2-capdrop / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m3-bgbursty / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m3-bgbursty / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m3-bgmix / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m3-bgmix / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m4-rttwide / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m4-rttx05 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m4-rttx4 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m5-fps15 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m5-fps15 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m5-fps60 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m5-fps60 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sburst / m6-stag / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | ssparse / m14-s030u070 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sstress / m9-s030u070 / codel | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |
| K3 | M | sstress / m9-s030u070 / pfifo | 1 leaf | 1 | 1 | 0 | 0 | 0 | 1 |

## Excluded

| campaign | reason | runs |
|---|---|---|
| K1 | no grouping truth (calm) | 30 |
| K1 | no grouping truth (nloss) | 3 |
| K1 | no grouping truth (rrev) | 3 |
| K2 | gate run (campaign acceptance, 90 s; not a campaign cell) | 10 |
| K2 | no grouping truth (dclean) | 6 |
| K2 | no grouping truth (negcalm) | 8 |
| K2 | no grouping truth (neglossh) | 2 |
| K2 | no grouping truth (negpriv) | 4 |
| K2 | no grouping truth (rrevasym) | 2 |
| K2 | not reliable (re-run list); was robustness | 1 |
| K3 | gate run (campaign acceptance, 90 s; not a campaign cell) | 16 |
| K3 | health_unverified; was main | 6 |
| K3 | no grouping truth (calm) | 10 |
| K3 | no grouping truth (sshortrfc) | 4 |
| K3 | not reliable (re-run list); was main | 1 |
| K3 | not reliable (re-run list); was robustness | 1 |

Excluded by name (not reliable / health_unverified): v4-L11-spause-def-pfifo-r2, v4-L2-fbcross-x80-codel-r2, v4-L7-hycombo-cap-pfifo-r1, v4-L7-hycombo-cap-pfifo-r2, v4-L7-hycombo-cap-pfifo-r3, v4-L7-hycombo-surge-pfifo-r1, v4-L7-hycombo-surge-pfifo-r2, v4-L7-hycombo-surge-pfifo-r3, v4-T2-sburst-jit5-pfifo-r2

