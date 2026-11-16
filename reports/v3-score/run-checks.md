# Suite v3 run checks (203 runs)

- runs with load / share off target (marked, kept): ['v3-M11-sburst-bw4x1-pfifo-r1', 'v3-M3-sburst-bgbursty-codel-r1', 'v3-M3-sburst-bgbursty-pfifo-r1']
- worst CPU idle: 0.694
- worst inter-dequeue p99: 4.172
Gating checks: 1_load_share, 2_ecn, 3_mtu, 4_health, 5_surge, 6_phase (scripts/v3_gate.py). Runs: 203.

| run | 1 load_share | 2 ecn | 3 mtu | 4 health | 5 surge | 6 phase |
|---|---|---|---|---|---|---|
| v3-C10-hindep-s030-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C10-hindep-s030-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C10-hindep-s030-fq_codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C10-hindep-s030-fq_codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C10-hindep-s030-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C10-hindep-s030-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C11-huneven-uneven-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C11-huneven-uneven-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C11-huneven-uneven-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C11-huneven-uneven-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C12-amixed-access-codel-r1 | ok | ok | ok | FAIL | ok | ok |
| v3-C12-amixed-access-codel-r2 | ok | ok | ok | FAIL | ok | ok |
| v3-C12-amixed-access-fq_codel-r1 | ok | ok | ok | FAIL | ok | ok |
| v3-C12-amixed-access-fq_codel-r2 | ok | ok | ok | FAIL | ok | ok |
| v3-C12-amixed-access-pfifo-r1 | ok | ok | ok | FAIL | ok | ok |
| v3-C12-amixed-access-pfifo-r2 | ok | ok | ok | FAIL | ok | ok |
| v3-C12-amixed-access-pie-r1 | ok | ok | ok | FAIL | ok | ok |
| v3-C12-amixed-access-pie-r2 | ok | ok | ok | FAIL | ok | ok |
| v3-C13-llong-s030-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C13-llong-s030-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C13-llong-s030-pfifo-r1 | ok | ok | ok | FAIL | ok | ok |
| v3-C13-llong-s030-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C14-rrev-rev-fq_codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C14-rrev-rev-fq_codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C14-rrev-rev-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C14-rrev-rev-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C15-nloss-s030u070-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C15-nloss-s030u070-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C15-nloss-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C15-nloss-s030u070-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-legacy-codel-r1 | ok | ok | ok | ok | - | - |
| v3-C1a-calm-legacy-codel-r2 | ok | ok | ok | ok | - | - |
| v3-C1a-calm-legacy-pfifo-r1 | ok | ok | ok | ok | - | - |
| v3-C1a-calm-legacy-pfifo-r2 | ok | ok | ok | ok | - | - |
| v3-C1a-calm-s010u070-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s010u070-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s010u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s010u070-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s010u085-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s010u085-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s010u085-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s010u085-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u050-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u050-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u050-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u050-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u070-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u070-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u070-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u085-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u085-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u085-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s030u085-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u050-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u050-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u050-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u050-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u070-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u070-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u070-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u085-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u085-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u085-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1a-calm-s065u085-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1b-calm-split4-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1b-calm-split4-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1b-calm-tree16-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1b-calm-tree16-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C1b-calm-uneven-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C1b-calm-uneven-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C2-sburst-s030u070-cake-r1 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-cake-r2 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-fq_codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-fq_codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-pie-r1 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-pie-r2 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-red-r1 | ok | ok | ok | ok | ok | ok |
| v3-C2-sburst-s030u070-red-r2 | ok | ok | ok | ok | ok | ok |
| v3-C3a-sburst-s010u070-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C3a-sburst-s010u070-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C3a-sburst-s010u070-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C3a-sburst-s010u070-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C3a-sburst-s065u070-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C3a-sburst-s065u070-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C3a-sburst-s065u070-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C3a-sburst-s065u070-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C3b-sburst-legacy-pfifo-r1 | ok | ok | ok | ok | - | - |
| v3-C3b-sburst-legacy-pfifo-r2 | ok | ok | ok | ok | - | - |
| v3-C4-sramp-s030u070-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C4-sramp-s030u070-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C4-sramp-s030u070-fq_codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C4-sramp-s030u070-fq_codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C4-sramp-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C4-sramp-s030u070-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C4-sramp-s030u070-pie-r1 | ok | ok | ok | ok | - | ok |
| v3-C4-sramp-s030u070-pie-r2 | ok | ok | ok | ok | - | ok |
| v3-C5-stcp-s030u070-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C5-stcp-s030u070-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C5-stcp-s030u070-fq_codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C5-stcp-s030u070-fq_codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C5-stcp-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C5-stcp-s030u070-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C5-stcp-s030u070-pie-r1 | ok | ok | ok | ok | - | ok |
| v3-C5-stcp-s030u070-pie-r2 | ok | ok | ok | ok | - | ok |
| v3-C6-sjoin-s030u070-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C6-sjoin-s030u070-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C6-sjoin-s030u070-fq_codel-r1 | ok | ok | ok | ok | - | ok |
| v3-C6-sjoin-s030u070-fq_codel-r2 | ok | ok | ok | ok | - | ok |
| v3-C6-sjoin-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-C6-sjoin-s030u070-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-C7-hhier-s030-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C7-hhier-s030-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C7-hhier-s030-fq_codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C7-hhier-s030-fq_codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C7-hhier-s030-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C7-hhier-s030-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C7-hhier-s030-pie-r1 | ok | ok | ok | ok | ok | ok |
| v3-C7-hhier-s030-pie-r2 | ok | ok | ok | ok | ok | ok |
| v3-C8-hhier-s065-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C8-hhier-s065-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-C9-hdepth-tree16-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C9-hdepth-tree16-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C9-hdepth-tree16-fq_codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-C9-hdepth-tree16-fq_codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-G1-calm-legacy-pfifo-r1 | ok | ok | ok | ok | - | - |
| v3-G1-calm-s030u070-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-access-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-rev-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-split4-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-tree16-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G2-calm-uneven-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-G3-sburst-s030u070-fq_codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-G3-sburst-s030u070-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M1-sburst-q100-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M1-sburst-q100-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M1-sburst-q300-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M1-sburst-q300-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M10-sburst-ip2-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M10-sburst-ip2-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M10-sburst-ip8-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M10-sburst-ip8-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M11-sburst-bw4x1-pfifo-r1 | FAIL | ok | ok | FAIL | ok | ok |
| v3-M11-sburst-bw4x1-pfifo-r2 | ok | ok | ok | FAIL | FAIL | ok |
| v3-M11-sburst-bw4x12-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M11-sburst-bw4x12-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M11-sburst-bw4x8-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M11-sburst-bw4x8-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M12-sburst-jitfwd-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M12-sburst-jitfwd-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M12-sburst-jitrev-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M12-sburst-jitrev-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M13-sburst-copa-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-M13-sburst-copa-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-M13-sburst-copa-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M13-sburst-copa-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M14-ssparse-s030u070-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M14-ssparse-s030u070-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M2-sburst-capdrop-codel-r1 | ok | ok | ok | ok | - | ok |
| v3-M2-sburst-capdrop-codel-r2 | ok | ok | ok | ok | - | ok |
| v3-M2-sburst-capdrop-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-M2-sburst-capdrop-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-M3-sburst-bgbursty-codel-r1 | FAIL | ok | ok | ok | FAIL | - |
| v3-M3-sburst-bgbursty-codel-r2 | ok | ok | ok | ok | FAIL | - |
| v3-M3-sburst-bgbursty-pfifo-r1 | FAIL | ok | ok | ok | FAIL | - |
| v3-M3-sburst-bgbursty-pfifo-r2 | ok | ok | ok | ok | FAIL | - |
| v3-M3-sburst-bgmix-codel-r1 | ok | ok | ok | ok | FAIL | ok |
| v3-M3-sburst-bgmix-codel-r2 | ok | ok | ok | ok | FAIL | FAIL |
| v3-M3-sburst-bgmix-pfifo-r1 | ok | ok | ok | ok | FAIL | ok |
| v3-M3-sburst-bgmix-pfifo-r2 | ok | ok | ok | ok | FAIL | FAIL |
| v3-M4-sburst-rttwide-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M4-sburst-rttwide-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M4-sburst-rttx05-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M4-sburst-rttx05-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M4-sburst-rttx4-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M4-sburst-rttx4-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M5-sburst-fps15-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-M5-sburst-fps15-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-M5-sburst-fps15-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M5-sburst-fps15-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M5-sburst-fps60-codel-r1 | ok | ok | ok | ok | ok | ok |
| v3-M5-sburst-fps60-codel-r2 | ok | ok | ok | ok | ok | ok |
| v3-M5-sburst-fps60-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M5-sburst-fps60-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M6-calm-stag-pfifo-r1 | ok | ok | ok | ok | - | ok |
| v3-M6-calm-stag-pfifo-r2 | ok | ok | ok | ok | - | ok |
| v3-M6-sburst-stag-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M6-sburst-stag-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M7-hhier-noroot-pfifo-r1 | ok | ok | ok | ok | ok | ok |
| v3-M7-hhier-noroot-pfifo-r2 | ok | ok | ok | ok | ok | ok |
| v3-M8-hhier-mixab-mixab-r1 | ok | ok | ok | FAIL | ok | ok |
| v3-M8-hhier-mixab-mixab-r2 | ok | ok | ok | ok | ok | ok |
| v3-M9-sstress-s030u070-codel-r1 | ok | ok | ok | ok | FAIL | ok |
| v3-M9-sstress-s030u070-codel-r2 | ok | ok | ok | ok | FAIL | ok |
| v3-M9-sstress-s030u070-pfifo-r1 | ok | ok | ok | ok | FAIL | ok |
| v3-M9-sstress-s030u070-pfifo-r2 | ok | ok | ok | ok | FAIL | ok |

## Load and share per egress (target U, s)

| run | egress | hop | load (U) | share / 0.96 (s) |
|---|---|---|---|---|
| v3-C10-hindep-s030-codel-r1 | up | r1->r2 | 0.712 (0.7) | 0.314 (0.3) |
| v3-C10-hindep-s030-codel-r1 | a | r2->switch-a | 0.711 (0.7) | 0.312 (0.3) |
| v3-C10-hindep-s030-codel-r1 | b | r2->switch-b | 0.713 (0.7) | 0.314 (0.3) |
| v3-C10-hindep-s030-codel-r2 | up | r1->r2 | 0.713 (0.7) | 0.314 (0.3) |
| v3-C10-hindep-s030-codel-r2 | a | r2->switch-a | 0.712 (0.7) | 0.311 (0.3) |
| v3-C10-hindep-s030-codel-r2 | b | r2->switch-b | 0.714 (0.7) | 0.315 (0.3) |
| v3-C10-hindep-s030-fq_codel-r1 | up | r1->r2 | 0.713 (0.7) | 0.315 (0.3) |
| v3-C10-hindep-s030-fq_codel-r1 | a | r2->switch-a | 0.712 (0.7) | 0.314 (0.3) |
| v3-C10-hindep-s030-fq_codel-r1 | b | r2->switch-b | 0.714 (0.7) | 0.315 (0.3) |
| v3-C10-hindep-s030-fq_codel-r2 | up | r1->r2 | 0.714 (0.7) | 0.315 (0.3) |
| v3-C10-hindep-s030-fq_codel-r2 | a | r2->switch-a | 0.713 (0.7) | 0.314 (0.3) |
| v3-C10-hindep-s030-fq_codel-r2 | b | r2->switch-b | 0.715 (0.7) | 0.316 (0.3) |
| v3-C10-hindep-s030-pfifo-r1 | up | r1->r2 | 0.711 (0.7) | 0.312 (0.3) |
| v3-C10-hindep-s030-pfifo-r1 | a | r2->switch-a | 0.711 (0.7) | 0.312 (0.3) |
| v3-C10-hindep-s030-pfifo-r1 | b | r2->switch-b | 0.711 (0.7) | 0.311 (0.3) |
| v3-C10-hindep-s030-pfifo-r2 | up | r1->r2 | 0.713 (0.7) | 0.312 (0.3) |
| v3-C10-hindep-s030-pfifo-r2 | a | r2->switch-a | 0.712 (0.7) | 0.312 (0.3) |
| v3-C10-hindep-s030-pfifo-r2 | b | r2->switch-b | 0.713 (0.7) | 0.314 (0.3) |
| v3-C11-huneven-uneven-codel-r1 | A | r2->switch-a | 0.709 (0.7) | 0.309 (0.3) |
| v3-C11-huneven-uneven-codel-r1 | B | r2->switch-b | 0.709 (0.7) | 0.309 (0.3) |
| v3-C11-huneven-uneven-codel-r1 | C | r2->switch-c | 0.711 (0.7) | 0.311 (0.3) |
| v3-C11-huneven-uneven-codel-r2 | A | r2->switch-a | 0.709 (0.7) | 0.309 (0.3) |
| v3-C11-huneven-uneven-codel-r2 | B | r2->switch-b | 0.707 (0.7) | 0.309 (0.3) |
| v3-C11-huneven-uneven-codel-r2 | C | r2->switch-c | 0.709 (0.7) | 0.309 (0.3) |
| v3-C11-huneven-uneven-pfifo-r1 | A | r2->switch-a | 0.709 (0.7) | 0.308 (0.3) |
| v3-C11-huneven-uneven-pfifo-r1 | B | r2->switch-b | 0.708 (0.7) | 0.309 (0.3) |
| v3-C11-huneven-uneven-pfifo-r1 | C | r2->switch-c | 0.709 (0.7) | 0.31 (0.3) |
| v3-C11-huneven-uneven-pfifo-r2 | A | r2->switch-a | 0.708 (0.7) | 0.308 (0.3) |
| v3-C11-huneven-uneven-pfifo-r2 | B | r2->switch-b | 0.707 (0.7) | 0.308 (0.3) |
| v3-C11-huneven-uneven-pfifo-r2 | C | r2->switch-c | 0.709 (0.7) | 0.309 (0.3) |
| v3-C12-amixed-access-codel-r1 | main | router->switch | 0.691 (0.7) | 0.293 (0.3) |
| v3-C12-amixed-access-codel-r2 | main | router->switch | 0.693 (0.7) | 0.295 (0.3) |
| v3-C12-amixed-access-fq_codel-r1 | main | router->switch | 0.691 (0.7) | 0.294 (0.3) |
| v3-C12-amixed-access-fq_codel-r2 | main | router->switch | 0.693 (0.7) | 0.294 (0.3) |
| v3-C12-amixed-access-pfifo-r1 | main | router->switch | 0.691 (0.7) | 0.293 (0.3) |
| v3-C12-amixed-access-pfifo-r2 | main | router->switch | 0.69 (0.7) | 0.292 (0.3) |
| v3-C12-amixed-access-pie-r1 | main | router->switch | 0.69 (0.7) | 0.293 (0.3) |
| v3-C12-amixed-access-pie-r2 | main | router->switch | 0.691 (0.7) | 0.293 (0.3) |
| v3-C13-llong-s030-codel-r1 | up | r1->r2 | 0.712 (0.7) | 0.314 (0.3) |
| v3-C13-llong-s030-codel-r1 | a | r2->switch-a | 0.712 (0.7) | 0.314 (0.3) |
| v3-C13-llong-s030-codel-r1 | b | r2->switch-b | 0.711 (0.7) | 0.315 (0.3) |
| v3-C13-llong-s030-codel-r2 | up | r1->r2 | 0.711 (0.7) | 0.312 (0.3) |
| v3-C13-llong-s030-codel-r2 | a | r2->switch-a | 0.714 (0.7) | 0.312 (0.3) |
| v3-C13-llong-s030-codel-r2 | b | r2->switch-b | 0.711 (0.7) | 0.31 (0.3) |
| v3-C13-llong-s030-pfifo-r1 | up | r1->r2 | 0.708 (0.7) | 0.309 (0.3) |
| v3-C13-llong-s030-pfifo-r1 | a | r2->switch-a | 0.709 (0.7) | 0.311 (0.3) |
| v3-C13-llong-s030-pfifo-r1 | b | r2->switch-b | 0.705 (0.7) | 0.309 (0.3) |
| v3-C13-llong-s030-pfifo-r2 | up | r1->r2 | 0.707 (0.7) | 0.309 (0.3) |
| v3-C13-llong-s030-pfifo-r2 | a | r2->switch-a | 0.709 (0.7) | 0.307 (0.3) |
| v3-C13-llong-s030-pfifo-r2 | b | r2->switch-b | 0.709 (0.7) | 0.309 (0.3) |
| v3-C14-rrev-rev-fq_codel-r1 | main | r1->switch | 0.71 (0.7) | 0.311 (0.3) |
| v3-C14-rrev-rev-fq_codel-r2 | main | r1->switch | 0.709 (0.7) | 0.31 (0.3) |
| v3-C14-rrev-rev-pfifo-r1 | main | r1->switch | 0.708 (0.7) | 0.309 (0.3) |
| v3-C14-rrev-rev-pfifo-r2 | main | r1->switch | 0.708 (0.7) | 0.309 (0.3) |
| v3-C15-nloss-s030u070-codel-r1 | main | router->switch | 0.704 (0.7) | 0.309 (0.3) |
| v3-C15-nloss-s030u070-codel-r2 | main | router->switch | 0.708 (0.7) | 0.307 (0.3) |
| v3-C15-nloss-s030u070-pfifo-r1 | main | router->switch | 0.705 (0.7) | 0.309 (0.3) |
| v3-C15-nloss-s030u070-pfifo-r2 | main | router->switch | 0.708 (0.7) | 0.307 (0.3) |
| v3-C1a-calm-legacy-codel-r1 | main | router->switch | 0.669 (0.65) | 1.004 (1.0) |
| v3-C1a-calm-legacy-codel-r2 | main | router->switch | 0.667 (0.65) | 1.004 (1.0) |
| v3-C1a-calm-legacy-pfifo-r1 | main | router->switch | 0.669 (0.65) | 1.009 (1.0) |
| v3-C1a-calm-legacy-pfifo-r2 | main | router->switch | 0.667 (0.65) | 1.008 (1.0) |
| v3-C1a-calm-s010u070-codel-r1 | main | router->switch | 0.702 (0.7) | 0.104 (0.1) |
| v3-C1a-calm-s010u070-codel-r2 | main | router->switch | 0.704 (0.7) | 0.104 (0.1) |
| v3-C1a-calm-s010u070-pfifo-r1 | main | router->switch | 0.702 (0.7) | 0.104 (0.1) |
| v3-C1a-calm-s010u070-pfifo-r2 | main | router->switch | 0.704 (0.7) | 0.104 (0.1) |
| v3-C1a-calm-s010u085-codel-r1 | main | router->switch | 0.852 (0.85) | 0.104 (0.1) |
| v3-C1a-calm-s010u085-codel-r2 | main | router->switch | 0.855 (0.85) | 0.104 (0.1) |
| v3-C1a-calm-s010u085-pfifo-r1 | main | router->switch | 0.852 (0.85) | 0.104 (0.1) |
| v3-C1a-calm-s010u085-pfifo-r2 | main | router->switch | 0.854 (0.85) | 0.104 (0.1) |
| v3-C1a-calm-s030u050-codel-r1 | main | router->switch | 0.504 (0.5) | 0.308 (0.3) |
| v3-C1a-calm-s030u050-codel-r2 | main | router->switch | 0.505 (0.5) | 0.307 (0.3) |
| v3-C1a-calm-s030u050-pfifo-r1 | main | router->switch | 0.504 (0.5) | 0.308 (0.3) |
| v3-C1a-calm-s030u050-pfifo-r2 | main | router->switch | 0.505 (0.5) | 0.307 (0.3) |
| v3-C1a-calm-s030u070-codel-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-C1a-calm-s030u070-codel-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-C1a-calm-s030u070-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-C1a-calm-s030u070-pfifo-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-C1a-calm-s030u085-codel-r1 | main | router->switch | 0.857 (0.85) | 0.308 (0.3) |
| v3-C1a-calm-s030u085-codel-r2 | main | router->switch | 0.859 (0.85) | 0.307 (0.3) |
| v3-C1a-calm-s030u085-pfifo-r1 | main | router->switch | 0.857 (0.85) | 0.308 (0.3) |
| v3-C1a-calm-s030u085-pfifo-r2 | main | router->switch | 0.859 (0.85) | 0.307 (0.3) |
| v3-C1a-calm-s065u050-codel-r1 | main | router->switch | 0.511 (0.5) | 0.659 (0.65) |
| v3-C1a-calm-s065u050-codel-r2 | main | router->switch | 0.51 (0.5) | 0.658 (0.65) |
| v3-C1a-calm-s065u050-pfifo-r1 | main | router->switch | 0.511 (0.5) | 0.66 (0.65) |
| v3-C1a-calm-s065u050-pfifo-r2 | main | router->switch | 0.51 (0.5) | 0.658 (0.65) |
| v3-C1a-calm-s065u070-codel-r1 | main | router->switch | 0.715 (0.7) | 0.659 (0.65) |
| v3-C1a-calm-s065u070-codel-r2 | main | router->switch | 0.714 (0.7) | 0.658 (0.65) |
| v3-C1a-calm-s065u070-pfifo-r1 | main | router->switch | 0.715 (0.7) | 0.663 (0.65) |
| v3-C1a-calm-s065u070-pfifo-r2 | main | router->switch | 0.714 (0.7) | 0.66 (0.65) |
| v3-C1a-calm-s065u085-codel-r1 | main | router->switch | 0.868 (0.85) | 0.661 (0.65) |
| v3-C1a-calm-s065u085-codel-r2 | main | router->switch | 0.867 (0.85) | 0.66 (0.65) |
| v3-C1a-calm-s065u085-pfifo-r1 | main | router->switch | 0.868 (0.85) | 0.661 (0.65) |
| v3-C1a-calm-s065u085-pfifo-r2 | main | router->switch | 0.867 (0.85) | 0.66 (0.65) |
| v3-C1b-calm-split4-pfifo-r1 | up | r1->r2 | 0.706 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-split4-pfifo-r1 | a | r2->switch-a | 0.708 (0.7) | 0.307 (0.3) |
| v3-C1b-calm-split4-pfifo-r1 | b | r2->switch-b | 0.707 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-split4-pfifo-r2 | up | r1->r2 | 0.707 (0.7) | 0.307 (0.3) |
| v3-C1b-calm-split4-pfifo-r2 | a | r2->switch-a | 0.707 (0.7) | 0.307 (0.3) |
| v3-C1b-calm-split4-pfifo-r2 | b | r2->switch-b | 0.707 (0.7) | 0.307 (0.3) |
| v3-C1b-calm-tree16-pfifo-r1 | root | rr->r0 | 0.708 (0.7) | 0.309 (0.3) |
| v3-C1b-calm-tree16-pfifo-r1 | X | r0->r1 | 0.711 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-tree16-pfifo-r1 | Y | r0->r2 | 0.71 (0.7) | 0.309 (0.3) |
| v3-C1b-calm-tree16-pfifo-r1 | A | r1->switch-a | 0.71 (0.7) | 0.309 (0.3) |
| v3-C1b-calm-tree16-pfifo-r1 | B | r1->switch-b | 0.709 (0.7) | 0.309 (0.3) |
| v3-C1b-calm-tree16-pfifo-r1 | C | r2->switch-c | 0.712 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-tree16-pfifo-r1 | D | r2->switch-d | 0.709 (0.7) | 0.309 (0.3) |
| v3-C1b-calm-tree16-pfifo-r2 | root | rr->r0 | 0.71 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-tree16-pfifo-r2 | X | r0->r1 | 0.71 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-tree16-pfifo-r2 | Y | r0->r2 | 0.71 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-tree16-pfifo-r2 | A | r1->switch-a | 0.711 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-tree16-pfifo-r2 | B | r1->switch-b | 0.71 (0.7) | 0.309 (0.3) |
| v3-C1b-calm-tree16-pfifo-r2 | C | r2->switch-c | 0.71 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-tree16-pfifo-r2 | D | r2->switch-d | 0.708 (0.7) | 0.309 (0.3) |
| v3-C1b-calm-uneven-pfifo-r1 | A | r2->switch-a | 0.705 (0.7) | 0.307 (0.3) |
| v3-C1b-calm-uneven-pfifo-r1 | B | r2->switch-b | 0.709 (0.7) | 0.307 (0.3) |
| v3-C1b-calm-uneven-pfifo-r1 | C | r2->switch-c | 0.707 (0.7) | 0.308 (0.3) |
| v3-C1b-calm-uneven-pfifo-r2 | A | r2->switch-a | 0.707 (0.7) | 0.306 (0.3) |
| v3-C1b-calm-uneven-pfifo-r2 | B | r2->switch-b | 0.707 (0.7) | 0.307 (0.3) |
| v3-C1b-calm-uneven-pfifo-r2 | C | r2->switch-c | 0.708 (0.7) | 0.308 (0.3) |
| v3-C2-sburst-s030u070-cake-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-C2-sburst-s030u070-cake-r2 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-C2-sburst-s030u070-codel-r1 | main | router->switch | 0.71 (0.7) | 0.311 (0.3) |
| v3-C2-sburst-s030u070-codel-r2 | main | router->switch | 0.709 (0.7) | 0.311 (0.3) |
| v3-C2-sburst-s030u070-fq_codel-r1 | main | router->switch | 0.712 (0.7) | 0.315 (0.3) |
| v3-C2-sburst-s030u070-fq_codel-r2 | main | router->switch | 0.712 (0.7) | 0.314 (0.3) |
| v3-C2-sburst-s030u070-pfifo-r1 | main | router->switch | 0.709 (0.7) | 0.31 (0.3) |
| v3-C2-sburst-s030u070-pfifo-r2 | main | router->switch | 0.709 (0.7) | 0.31 (0.3) |
| v3-C2-sburst-s030u070-pie-r1 | main | router->switch | 0.707 (0.7) | 0.309 (0.3) |
| v3-C2-sburst-s030u070-pie-r2 | main | router->switch | 0.708 (0.7) | 0.31 (0.3) |
| v3-C2-sburst-s030u070-red-r1 | main | router->switch | 0.707 (0.7) | 0.308 (0.3) |
| v3-C2-sburst-s030u070-red-r2 | main | router->switch | 0.707 (0.7) | 0.308 (0.3) |
| v3-C3a-sburst-s010u070-codel-r1 | main | router->switch | 0.703 (0.7) | 0.104 (0.1) |
| v3-C3a-sburst-s010u070-codel-r2 | main | router->switch | 0.705 (0.7) | 0.105 (0.1) |
| v3-C3a-sburst-s010u070-pfifo-r1 | main | router->switch | 0.703 (0.7) | 0.104 (0.1) |
| v3-C3a-sburst-s010u070-pfifo-r2 | main | router->switch | 0.703 (0.7) | 0.103 (0.1) |
| v3-C3a-sburst-s065u070-codel-r1 | main | router->switch | 0.721 (0.7) | 0.665 (0.65) |
| v3-C3a-sburst-s065u070-codel-r2 | main | router->switch | 0.723 (0.7) | 0.664 (0.65) |
| v3-C3a-sburst-s065u070-pfifo-r1 | main | router->switch | 0.721 (0.7) | 0.665 (0.65) |
| v3-C3a-sburst-s065u070-pfifo-r2 | main | router->switch | 0.72 (0.7) | 0.661 (0.65) |
| v3-C3b-sburst-legacy-pfifo-r1 | main | router->switch | 0.677 (0.65) | 1.004 (1.0) |
| v3-C3b-sburst-legacy-pfifo-r2 | main | router->switch | 0.678 (0.65) | 1.003 (1.0) |
| v3-C4-sramp-s030u070-codel-r1 | main | router->switch | 0.708 (0.7) | 0.312 (0.3) |
| v3-C4-sramp-s030u070-codel-r2 | main | router->switch | 0.712 (0.7) | 0.311 (0.3) |
| v3-C4-sramp-s030u070-fq_codel-r1 | main | router->switch | 0.71 (0.7) | 0.315 (0.3) |
| v3-C4-sramp-s030u070-fq_codel-r2 | main | router->switch | 0.717 (0.7) | 0.316 (0.3) |
| v3-C4-sramp-s030u070-pfifo-r1 | main | router->switch | 0.707 (0.7) | 0.31 (0.3) |
| v3-C4-sramp-s030u070-pfifo-r2 | main | router->switch | 0.709 (0.7) | 0.308 (0.3) |
| v3-C4-sramp-s030u070-pie-r1 | main | router->switch | 0.707 (0.7) | 0.311 (0.3) |
| v3-C4-sramp-s030u070-pie-r2 | main | router->switch | 0.709 (0.7) | 0.308 (0.3) |
| v3-C5-stcp-s030u070-codel-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-C5-stcp-s030u070-codel-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-C5-stcp-s030u070-fq_codel-r1 | main | router->switch | 0.707 (0.7) | 0.309 (0.3) |
| v3-C5-stcp-s030u070-fq_codel-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-C5-stcp-s030u070-pfifo-r1 | main | router->switch | 0.707 (0.7) | 0.309 (0.3) |
| v3-C5-stcp-s030u070-pfifo-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-C5-stcp-s030u070-pie-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-C5-stcp-s030u070-pie-r2 | main | router->switch | 0.707 (0.7) | 0.308 (0.3) |
| v3-C6-sjoin-s030u070-codel-r1 | main | router->switch | 0.705 (0.7) | 0.308 (0.3) |
| v3-C6-sjoin-s030u070-codel-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-C6-sjoin-s030u070-fq_codel-r1 | main | router->switch | 0.705 (0.7) | 0.308 (0.3) |
| v3-C6-sjoin-s030u070-fq_codel-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-C6-sjoin-s030u070-pfifo-r1 | main | router->switch | 0.705 (0.7) | 0.308 (0.3) |
| v3-C6-sjoin-s030u070-pfifo-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-C7-hhier-s030-codel-r1 | up | r1->r2 | 0.711 (0.7) | 0.312 (0.3) |
| v3-C7-hhier-s030-codel-r1 | a | r2->switch-a | 0.711 (0.7) | 0.311 (0.3) |
| v3-C7-hhier-s030-codel-r1 | b | r2->switch-b | 0.712 (0.7) | 0.314 (0.3) |
| v3-C7-hhier-s030-codel-r2 | up | r1->r2 | 0.71 (0.7) | 0.311 (0.3) |
| v3-C7-hhier-s030-codel-r2 | a | r2->switch-a | 0.71 (0.7) | 0.31 (0.3) |
| v3-C7-hhier-s030-codel-r2 | b | r2->switch-b | 0.711 (0.7) | 0.312 (0.3) |
| v3-C7-hhier-s030-fq_codel-r1 | up | r1->r2 | 0.711 (0.7) | 0.312 (0.3) |
| v3-C7-hhier-s030-fq_codel-r1 | a | r2->switch-a | 0.712 (0.7) | 0.312 (0.3) |
| v3-C7-hhier-s030-fq_codel-r1 | b | r2->switch-b | 0.712 (0.7) | 0.314 (0.3) |
| v3-C7-hhier-s030-fq_codel-r2 | up | r1->r2 | 0.712 (0.7) | 0.312 (0.3) |
| v3-C7-hhier-s030-fq_codel-r2 | a | r2->switch-a | 0.711 (0.7) | 0.311 (0.3) |
| v3-C7-hhier-s030-fq_codel-r2 | b | r2->switch-b | 0.712 (0.7) | 0.314 (0.3) |
| v3-C7-hhier-s030-pfifo-r1 | up | r1->r2 | 0.71 (0.7) | 0.311 (0.3) |
| v3-C7-hhier-s030-pfifo-r1 | a | r2->switch-a | 0.71 (0.7) | 0.31 (0.3) |
| v3-C7-hhier-s030-pfifo-r1 | b | r2->switch-b | 0.711 (0.7) | 0.311 (0.3) |
| v3-C7-hhier-s030-pfifo-r2 | up | r1->r2 | 0.709 (0.7) | 0.31 (0.3) |
| v3-C7-hhier-s030-pfifo-r2 | a | r2->switch-a | 0.709 (0.7) | 0.31 (0.3) |
| v3-C7-hhier-s030-pfifo-r2 | b | r2->switch-b | 0.709 (0.7) | 0.31 (0.3) |
| v3-C7-hhier-s030-pie-r1 | up | r1->r2 | 0.709 (0.7) | 0.31 (0.3) |
| v3-C7-hhier-s030-pie-r1 | a | r2->switch-a | 0.709 (0.7) | 0.309 (0.3) |
| v3-C7-hhier-s030-pie-r1 | b | r2->switch-b | 0.709 (0.7) | 0.311 (0.3) |
| v3-C7-hhier-s030-pie-r2 | up | r1->r2 | 0.709 (0.7) | 0.309 (0.3) |
| v3-C7-hhier-s030-pie-r2 | a | r2->switch-a | 0.708 (0.7) | 0.309 (0.3) |
| v3-C7-hhier-s030-pie-r2 | b | r2->switch-b | 0.709 (0.7) | 0.309 (0.3) |
| v3-C8-hhier-s065-pfifo-r1 | up | r1->r2 | 0.72 (0.7) | 0.664 (0.65) |
| v3-C8-hhier-s065-pfifo-r1 | a | r2->switch-a | 0.721 (0.7) | 0.663 (0.65) |
| v3-C8-hhier-s065-pfifo-r1 | b | r2->switch-b | 0.721 (0.7) | 0.661 (0.65) |
| v3-C8-hhier-s065-pfifo-r2 | up | r1->r2 | 0.721 (0.7) | 0.663 (0.65) |
| v3-C8-hhier-s065-pfifo-r2 | a | r2->switch-a | 0.72 (0.7) | 0.663 (0.65) |
| v3-C8-hhier-s065-pfifo-r2 | b | r2->switch-b | 0.721 (0.7) | 0.663 (0.65) |
| v3-C9-hdepth-tree16-codel-r1 | root | rr->r0 | 0.711 (0.7) | 0.312 (0.3) |
| v3-C9-hdepth-tree16-codel-r1 | X | r0->r1 | 0.712 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-codel-r1 | Y | r0->r2 | 0.712 (0.7) | 0.312 (0.3) |
| v3-C9-hdepth-tree16-codel-r1 | A | r1->switch-a | 0.712 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-codel-r1 | B | r1->switch-b | 0.712 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-codel-r1 | C | r2->switch-c | 0.714 (0.7) | 0.312 (0.3) |
| v3-C9-hdepth-tree16-codel-r1 | D | r2->switch-d | 0.712 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-codel-r2 | root | rr->r0 | 0.712 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-codel-r2 | X | r0->r1 | 0.712 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-codel-r2 | Y | r0->r2 | 0.713 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-codel-r2 | A | r1->switch-a | 0.714 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-codel-r2 | B | r1->switch-b | 0.711 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-codel-r2 | C | r2->switch-c | 0.714 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-codel-r2 | D | r2->switch-d | 0.71 (0.7) | 0.311 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r1 | root | rr->r0 | 0.709 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r1 | X | r0->r1 | 0.71 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r1 | Y | r0->r2 | 0.71 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r1 | A | r1->switch-a | 0.711 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r1 | B | r1->switch-b | 0.71 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r1 | C | r2->switch-c | 0.712 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r1 | D | r2->switch-d | 0.71 (0.7) | 0.309 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r2 | root | rr->r0 | 0.71 (0.7) | 0.309 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r2 | X | r0->r1 | 0.71 (0.7) | 0.309 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r2 | Y | r0->r2 | 0.711 (0.7) | 0.309 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r2 | A | r1->switch-a | 0.711 (0.7) | 0.309 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r2 | B | r1->switch-b | 0.71 (0.7) | 0.309 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r2 | C | r2->switch-c | 0.711 (0.7) | 0.309 (0.3) |
| v3-C9-hdepth-tree16-fq_codel-r2 | D | r2->switch-d | 0.709 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r1 | root | rr->r0 | 0.71 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r1 | X | r0->r1 | 0.71 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r1 | Y | r0->r2 | 0.71 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r1 | A | r1->switch-a | 0.711 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r1 | B | r1->switch-b | 0.711 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r1 | C | r2->switch-c | 0.712 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r1 | D | r2->switch-d | 0.711 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r2 | root | rr->r0 | 0.711 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r2 | X | r0->r1 | 0.71 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r2 | Y | r0->r2 | 0.712 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r2 | A | r1->switch-a | 0.712 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r2 | B | r1->switch-b | 0.711 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r2 | C | r2->switch-c | 0.712 (0.7) | 0.31 (0.3) |
| v3-C9-hdepth-tree16-pfifo-r2 | D | r2->switch-d | 0.71 (0.7) | 0.31 (0.3) |
| v3-G1-calm-legacy-pfifo-r1 | main | router->switch | 0.669 (0.65) | 1.008 (1.0) |
| v3-G1-calm-s030u070-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-G2-calm-access-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-G2-calm-rev-pfifo-r1 | main | r1->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-G2-calm-split4-pfifo-r1 | up | r1->r2 | 0.706 (0.7) | 0.308 (0.3) |
| v3-G2-calm-split4-pfifo-r1 | a | r2->switch-a | 0.708 (0.7) | 0.307 (0.3) |
| v3-G2-calm-split4-pfifo-r1 | b | r2->switch-b | 0.707 (0.7) | 0.308 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | root | rr->r0 | 0.708 (0.7) | 0.309 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | X | r0->r1 | 0.711 (0.7) | 0.308 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | Y | r0->r2 | 0.71 (0.7) | 0.309 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | A | r1->switch-a | 0.71 (0.7) | 0.309 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | B | r1->switch-b | 0.709 (0.7) | 0.309 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | C | r2->switch-c | 0.712 (0.7) | 0.308 (0.3) |
| v3-G2-calm-tree16-pfifo-r1 | D | r2->switch-d | 0.709 (0.7) | 0.309 (0.3) |
| v3-G2-calm-uneven-pfifo-r1 | A | r2->switch-a | 0.705 (0.7) | 0.307 (0.3) |
| v3-G2-calm-uneven-pfifo-r1 | B | r2->switch-b | 0.709 (0.7) | 0.307 (0.3) |
| v3-G2-calm-uneven-pfifo-r1 | C | r2->switch-c | 0.707 (0.7) | 0.308 (0.3) |
| v3-G3-sburst-s030u070-fq_codel-r1 | main | router->switch | 0.713 (0.7) | 0.316 (0.3) |
| v3-G3-sburst-s030u070-pfifo-r1 | main | router->switch | 0.71 (0.7) | 0.312 (0.3) |
| v3-M1-sburst-q100-pfifo-r1 | main | router->switch | 0.71 (0.7) | 0.311 (0.3) |
| v3-M1-sburst-q100-pfifo-r2 | main | router->switch | 0.709 (0.7) | 0.31 (0.3) |
| v3-M1-sburst-q300-pfifo-r1 | main | router->switch | 0.712 (0.7) | 0.314 (0.3) |
| v3-M1-sburst-q300-pfifo-r2 | main | router->switch | 0.711 (0.7) | 0.312 (0.3) |
| v3-M10-sburst-ip2-pfifo-r1 | main | router->switch | 0.712 (0.7) | 0.314 (0.3) |
| v3-M10-sburst-ip2-pfifo-r2 | main | router->switch | 0.709 (0.7) | 0.311 (0.3) |
| v3-M10-sburst-ip8-pfifo-r1 | main | router->switch | 0.709 (0.7) | 0.311 (0.3) |
| v3-M10-sburst-ip8-pfifo-r2 | main | router->switch | 0.707 (0.7) | 0.308 (0.3) |
| v3-M11-sburst-bw4x1-pfifo-r1 | main | router->switch | 0.73 (0.7) | 0.664 (0.65) |
| v3-M11-sburst-bw4x1-pfifo-r2 | main | router->switch | 0.729 (0.7) | 0.663 (0.65) |
| v3-M11-sburst-bw4x12-pfifo-r1 | main | router->switch | 0.719 (0.7) | 0.664 (0.65) |
| v3-M11-sburst-bw4x12-pfifo-r2 | main | router->switch | 0.72 (0.7) | 0.664 (0.65) |
| v3-M11-sburst-bw4x8-pfifo-r1 | main | router->switch | 0.717 (0.7) | 0.661 (0.65) |
| v3-M11-sburst-bw4x8-pfifo-r2 | main | router->switch | 0.717 (0.7) | 0.661 (0.65) |
| v3-M12-sburst-jitfwd-pfifo-r1 | main | router->switch | 0.711 (0.7) | 0.312 (0.3) |
| v3-M12-sburst-jitfwd-pfifo-r2 | main | router->switch | 0.708 (0.7) | 0.31 (0.3) |
| v3-M12-sburst-jitrev-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.31 (0.3) |
| v3-M12-sburst-jitrev-pfifo-r2 | main | router->switch | 0.708 (0.7) | 0.309 (0.3) |
| v3-M13-sburst-copa-codel-r1 | main | router->switch | 0.706 (0.7) | 0.307 (0.3) |
| v3-M13-sburst-copa-codel-r2 | main | router->switch | 0.706 (0.7) | 0.307 (0.3) |
| v3-M13-sburst-copa-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-M13-sburst-copa-pfifo-r2 | main | router->switch | 0.706 (0.7) | 0.307 (0.3) |
| v3-M14-ssparse-s030u070-pfifo-r1 | main | router->switch | 0.707 (0.7) | 0.309 (0.3) |
| v3-M14-ssparse-s030u070-pfifo-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-M2-sburst-capdrop-codel-r1 | main | router->switch | 0.709 (0.7) | 0.31 (0.3) |
| v3-M2-sburst-capdrop-codel-r2 | main | router->switch | 0.708 (0.7) | 0.309 (0.3) |
| v3-M2-sburst-capdrop-pfifo-r1 | main | router->switch | 0.709 (0.7) | 0.311 (0.3) |
| v3-M2-sburst-capdrop-pfifo-r2 | main | router->switch | 0.71 (0.7) | 0.311 (0.3) |
| v3-M3-sburst-bgbursty-codel-r1 | main | router->switch | 0.651 (0.7) | 0.338 (0.3) |
| v3-M3-sburst-bgbursty-codel-r2 | main | router->switch | 0.714 (0.7) | 0.311 (0.3) |
| v3-M3-sburst-bgbursty-pfifo-r1 | main | router->switch | 0.65 (0.7) | 0.338 (0.3) |
| v3-M3-sburst-bgbursty-pfifo-r2 | main | router->switch | 0.713 (0.7) | 0.31 (0.3) |
| v3-M3-sburst-bgmix-codel-r1 | main | router->switch | 0.712 (0.7) | 0.306 (0.3) |
| v3-M3-sburst-bgmix-codel-r2 | main | router->switch | 0.712 (0.7) | 0.307 (0.3) |
| v3-M3-sburst-bgmix-pfifo-r1 | main | router->switch | 0.713 (0.7) | 0.307 (0.3) |
| v3-M3-sburst-bgmix-pfifo-r2 | main | router->switch | 0.712 (0.7) | 0.307 (0.3) |
| v3-M4-sburst-rttwide-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.31 (0.3) |
| v3-M4-sburst-rttwide-pfifo-r2 | main | router->switch | 0.71 (0.7) | 0.311 (0.3) |
| v3-M4-sburst-rttx05-pfifo-r1 | main | router->switch | 0.708 (0.7) | 0.309 (0.3) |
| v3-M4-sburst-rttx05-pfifo-r2 | main | router->switch | 0.708 (0.7) | 0.309 (0.3) |
| v3-M4-sburst-rttx4-pfifo-r1 | main | router->switch | 0.71 (0.7) | 0.312 (0.3) |
| v3-M4-sburst-rttx4-pfifo-r2 | main | router->switch | 0.708 (0.7) | 0.31 (0.3) |
| v3-M5-sburst-fps15-codel-r1 | main | router->switch | 0.709 (0.7) | 0.311 (0.3) |
| v3-M5-sburst-fps15-codel-r2 | main | router->switch | 0.709 (0.7) | 0.31 (0.3) |
| v3-M5-sburst-fps15-pfifo-r1 | main | router->switch | 0.709 (0.7) | 0.31 (0.3) |
| v3-M5-sburst-fps15-pfifo-r2 | main | router->switch | 0.707 (0.7) | 0.309 (0.3) |
| v3-M5-sburst-fps60-codel-r1 | main | router->switch | 0.713 (0.7) | 0.315 (0.3) |
| v3-M5-sburst-fps60-codel-r2 | main | router->switch | 0.709 (0.7) | 0.311 (0.3) |
| v3-M5-sburst-fps60-pfifo-r1 | main | router->switch | 0.712 (0.7) | 0.314 (0.3) |
| v3-M5-sburst-fps60-pfifo-r2 | main | router->switch | 0.709 (0.7) | 0.311 (0.3) |
| v3-M6-calm-stag-pfifo-r1 | main | router->switch | 0.706 (0.7) | 0.308 (0.3) |
| v3-M6-calm-stag-pfifo-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-M6-sburst-stag-pfifo-r1 | main | router->switch | 0.71 (0.7) | 0.311 (0.3) |
| v3-M6-sburst-stag-pfifo-r2 | main | router->switch | 0.709 (0.7) | 0.31 (0.3) |
| v3-M7-hhier-noroot-pfifo-r1 | a | r2->switch-a | 0.71 (0.7) | 0.311 (0.3) |
| v3-M7-hhier-noroot-pfifo-r1 | b | r2->switch-b | 0.709 (0.7) | 0.311 (0.3) |
| v3-M7-hhier-noroot-pfifo-r2 | a | r2->switch-a | 0.709 (0.7) | 0.309 (0.3) |
| v3-M7-hhier-noroot-pfifo-r2 | b | r2->switch-b | 0.71 (0.7) | 0.311 (0.3) |
| v3-M8-hhier-mixab-mixab-r1 | up | r1->r2 | 0.711 (0.7) | 0.312 (0.3) |
| v3-M8-hhier-mixab-mixab-r1 | a | r2->switch-a | 0.71 (0.7) | 0.31 (0.3) |
| v3-M8-hhier-mixab-mixab-r1 | b | r2->switch-b | 0.712 (0.7) | 0.314 (0.3) |
| v3-M8-hhier-mixab-mixab-r2 | up | r1->r2 | 0.71 (0.7) | 0.311 (0.3) |
| v3-M8-hhier-mixab-mixab-r2 | a | r2->switch-a | 0.709 (0.7) | 0.31 (0.3) |
| v3-M8-hhier-mixab-mixab-r2 | b | r2->switch-b | 0.711 (0.7) | 0.312 (0.3) |
| v3-M9-sstress-s030u070-codel-r1 | main | router->switch | 0.703 (0.7) | 0.306 (0.3) |
| v3-M9-sstress-s030u070-codel-r2 | main | router->switch | 0.707 (0.7) | 0.307 (0.3) |
| v3-M9-sstress-s030u070-pfifo-r1 | main | router->switch | 0.702 (0.7) | 0.305 (0.3) |
| v3-M9-sstress-s030u070-pfifo-r2 | main | router->switch | 0.7 (0.7) | 0.3 (0.3) |

## Keyframe queueing peak (calm, 200 ms after each keyframe; not gating)

| run | egress | hop | n | p50 / p90 / max ms | 0.121 s U ms |
|---|---|---|---|---|---|
| v3-C10-hindep-s030-codel-r1 | up | r1->r2 | 211 | 9.2 / 16.3 / 25.2 | 25.4 |
| v3-C10-hindep-s030-codel-r1 | a | r2->switch-a | 211 | 5.2 / 10.1 / 15.9 | 25.4 |
| v3-C10-hindep-s030-codel-r1 | b | r2->switch-b | 211 | 6.0 / 10.5 / 15.4 | 25.4 |
| v3-C10-hindep-s030-codel-r2 | up | r1->r2 | 163 | 8.4 / 12.2 / 21.9 | 25.4 |
| v3-C10-hindep-s030-codel-r2 | a | r2->switch-a | 163 | 5.0 / 9.8 / 13.2 | 25.4 |
| v3-C10-hindep-s030-codel-r2 | b | r2->switch-b | 163 | 4.7 / 8.8 / 13.4 | 25.4 |
| v3-C10-hindep-s030-fq_codel-r1 | up | r1->r2 | 211 | 10.5 / 15.6 / 24.2 | 25.4 |
| v3-C10-hindep-s030-fq_codel-r1 | a | r2->switch-a | 211 | 3.1 / 5.5 / 12.0 | 25.4 |
| v3-C10-hindep-s030-fq_codel-r1 | b | r2->switch-b | 211 | 3.1 / 5.8 / 15.3 | 25.4 |
| v3-C10-hindep-s030-fq_codel-r2 | up | r1->r2 | 163 | 9.5 / 13.3 / 21.9 | 25.4 |
| v3-C10-hindep-s030-fq_codel-r2 | a | r2->switch-a | 163 | 3.1 / 6.3 / 12.6 | 25.4 |
| v3-C10-hindep-s030-fq_codel-r2 | b | r2->switch-b | 163 | 2.7 / 5.0 / 10.2 | 25.4 |
| v3-C10-hindep-s030-pfifo-r1 | up | r1->r2 | 211 | 9.1 / 13.2 / 27.4 | 25.4 |
| v3-C10-hindep-s030-pfifo-r1 | a | r2->switch-a | 211 | 4.9 / 9.0 / 15.2 | 25.4 |
| v3-C10-hindep-s030-pfifo-r1 | b | r2->switch-b | 211 | 5.5 / 9.9 / 14.8 | 25.4 |
| v3-C10-hindep-s030-pfifo-r2 | up | r1->r2 | 163 | 8.3 / 12.2 / 21.6 | 25.4 |
| v3-C10-hindep-s030-pfifo-r2 | a | r2->switch-a | 163 | 4.5 / 8.8 / 12.8 | 25.4 |
| v3-C10-hindep-s030-pfifo-r2 | b | r2->switch-b | 163 | 5.0 / 9.1 / 16.8 | 25.4 |
| v3-C11-huneven-uneven-codel-r1 | A | r2->switch-a | 150 | 8.3 / 12.8 / 28.2 | 25.4 |
| v3-C11-huneven-uneven-codel-r1 | B | r2->switch-b | 150 | 9.1 / 13.5 / 27.0 | 25.4 |
| v3-C11-huneven-uneven-codel-r1 | C | r2->switch-c | 150 | 10.1 / 13.8 / 25.5 | 25.4 |
| v3-C11-huneven-uneven-codel-r2 | A | r2->switch-a | 191 | 8.5 / 14.7 / 25.3 | 25.4 |
| v3-C11-huneven-uneven-codel-r2 | B | r2->switch-b | 191 | 10.3 / 15.5 / 25.3 | 25.4 |
| v3-C11-huneven-uneven-codel-r2 | C | r2->switch-c | 191 | 10.0 / 13.8 / 22.5 | 25.4 |
| v3-C11-huneven-uneven-pfifo-r1 | A | r2->switch-a | 150 | 8.2 / 13.3 / 27.4 | 25.4 |
| v3-C11-huneven-uneven-pfifo-r1 | B | r2->switch-b | 150 | 9.2 / 12.8 / 26.7 | 25.4 |
| v3-C11-huneven-uneven-pfifo-r1 | C | r2->switch-c | 150 | 10.4 / 13.9 / 25.7 | 25.4 |
| v3-C11-huneven-uneven-pfifo-r2 | A | r2->switch-a | 191 | 7.7 / 12.4 / 26.3 | 25.4 |
| v3-C11-huneven-uneven-pfifo-r2 | B | r2->switch-b | 191 | 9.3 / 13.2 / 24.0 | 25.4 |
| v3-C11-huneven-uneven-pfifo-r2 | C | r2->switch-c | 191 | 9.8 / 13.1 / 23.6 | 25.4 |
| v3-C12-amixed-access-codel-r1 | main | router->switch | 220 | 8.5 / 13.7 / 21.2 | 25.4 |
| v3-C12-amixed-access-codel-r2 | main | router->switch | 219 | 9.0 / 14.3 / 19.6 | 25.4 |
| v3-C12-amixed-access-fq_codel-r1 | main | router->switch | 220 | 11.1 / 16.3 / 26.6 | 25.4 |
| v3-C12-amixed-access-fq_codel-r2 | main | router->switch | 219 | 10.7 / 16.1 / 23.2 | 25.4 |
| v3-C12-amixed-access-pfifo-r1 | main | router->switch | 220 | 8.8 / 14.6 / 23.3 | 25.4 |
| v3-C12-amixed-access-pfifo-r2 | main | router->switch | 219 | 9.3 / 14.3 / 23.1 | 25.4 |
| v3-C12-amixed-access-pie-r1 | main | router->switch | 220 | 8.2 / 14.2 / 23.9 | 25.4 |
| v3-C12-amixed-access-pie-r2 | main | router->switch | 219 | 8.2 / 13.7 / 19.4 | 25.4 |
| v3-C13-llong-s030-codel-r1 | up | r1->r2 | 115 | 10.1 / 14.7 / 18.1 | 25.4 |
| v3-C13-llong-s030-codel-r1 | a | r2->switch-a | 115 | 6.0 / 16.9 / 22.2 | 25.4 |
| v3-C13-llong-s030-codel-r1 | b | r2->switch-b | 115 | 6.2 / 10.5 / 13.5 | 25.4 |
| v3-C13-llong-s030-codel-r2 | up | r1->r2 | 118 | 9.0 / 12.1 / 15.2 | 25.4 |
| v3-C13-llong-s030-codel-r2 | a | r2->switch-a | 118 | 5.3 / 9.2 / 13.0 | 25.4 |
| v3-C13-llong-s030-codel-r2 | b | r2->switch-b | 118 | 5.1 / 8.6 / 11.8 | 25.4 |
| v3-C13-llong-s030-pfifo-r1 | up | r1->r2 | 115 | 9.8 / 15.5 / 24.3 | 25.4 |
| v3-C13-llong-s030-pfifo-r1 | a | r2->switch-a | 115 | 5.6 / 15.4 / 20.2 | 25.4 |
| v3-C13-llong-s030-pfifo-r1 | b | r2->switch-b | 115 | 5.9 / 9.6 / 16.9 | 25.4 |
| v3-C13-llong-s030-pfifo-r2 | up | r1->r2 | 118 | 8.8 / 12.3 / 17.6 | 25.4 |
| v3-C13-llong-s030-pfifo-r2 | a | r2->switch-a | 118 | 5.0 / 8.2 / 13.2 | 25.4 |
| v3-C13-llong-s030-pfifo-r2 | b | r2->switch-b | 118 | 5.4 / 9.3 / 13.4 | 25.4 |
| v3-C14-rrev-rev-fq_codel-r1 | main | r1->switch | 173 | 12.1 / 18.3 / 22.1 | 25.4 |
| v3-C14-rrev-rev-fq_codel-r2 | main | r1->switch | 191 | 11.4 / 17.1 / 25.1 | 25.4 |
| v3-C14-rrev-rev-pfifo-r1 | main | r1->switch | 173 | 9.0 / 15.8 / 22.2 | 25.4 |
| v3-C14-rrev-rev-pfifo-r2 | main | r1->switch | 191 | 9.2 / 15.5 / 31.8 | 25.4 |
| v3-C15-nloss-s030u070-codel-r1 | main | router->switch | 90 | 16.0 / 19.8 / 32.4 | 25.4 |
| v3-C15-nloss-s030u070-codel-r2 | main | router->switch | 87 | 12.2 / 17.6 / 25.1 | 25.4 |
| v3-C15-nloss-s030u070-pfifo-r1 | main | router->switch | 90 | 15.8 / 22.0 / 28.8 | 25.4 |
| v3-C15-nloss-s030u070-pfifo-r2 | main | router->switch | 87 | 14.3 / 19.3 / 30.5 | 25.4 |
| v3-C1a-calm-legacy-codel-r1 | main | router->switch | 103 | 71.9 / 85.5 / 115.1 | None |
| v3-C1a-calm-legacy-codel-r2 | main | router->switch | 103 | 69.2 / 81.1 / 136.1 | None |
| v3-C1a-calm-legacy-pfifo-r1 | main | router->switch | 103 | 45.9 / 57.6 / 58.2 | None |
| v3-C1a-calm-legacy-pfifo-r2 | main | router->switch | 103 | 47.0 / 56.8 / 58.0 | None |
| v3-C1a-calm-s010u070-codel-r1 | main | router->switch | 103 | 6.3 / 8.2 / 9.6 | 8.5 |
| v3-C1a-calm-s010u070-codel-r2 | main | router->switch | 103 | 5.9 / 7.3 / 11.3 | 8.5 |
| v3-C1a-calm-s010u070-pfifo-r1 | main | router->switch | 103 | 6.1 / 8.3 / 9.4 | 8.5 |
| v3-C1a-calm-s010u070-pfifo-r2 | main | router->switch | 103 | 6.0 / 7.3 / 10.2 | 8.5 |
| v3-C1a-calm-s010u085-codel-r1 | main | router->switch | 103 | 8.8 / 11.7 / 15.9 | 10.3 |
| v3-C1a-calm-s010u085-codel-r2 | main | router->switch | 103 | 9.0 / 10.9 / 16.3 | 10.3 |
| v3-C1a-calm-s010u085-pfifo-r1 | main | router->switch | 103 | 9.1 / 11.5 / 16.0 | 10.3 |
| v3-C1a-calm-s010u085-pfifo-r2 | main | router->switch | 103 | 8.5 / 10.5 / 15.8 | 10.3 |
| v3-C1a-calm-s030u050-codel-r1 | main | router->switch | 103 | 13.7 / 17.4 / 25.4 | 18.1 |
| v3-C1a-calm-s030u050-codel-r2 | main | router->switch | 103 | 13.4 / 15.9 / 21.2 | 18.1 |
| v3-C1a-calm-s030u050-pfifo-r1 | main | router->switch | 103 | 14.5 / 17.4 / 20.2 | 18.1 |
| v3-C1a-calm-s030u050-pfifo-r2 | main | router->switch | 103 | 13.2 / 16.4 / 19.8 | 18.1 |
| v3-C1a-calm-s030u070-codel-r1 | main | router->switch | 103 | 21.8 / 26.7 / 34.3 | 25.4 |
| v3-C1a-calm-s030u070-codel-r2 | main | router->switch | 103 | 21.2 / 25.4 / 33.2 | 25.4 |
| v3-C1a-calm-s030u070-pfifo-r1 | main | router->switch | 103 | 23.2 / 27.0 / 32.6 | 25.4 |
| v3-C1a-calm-s030u070-pfifo-r2 | main | router->switch | 103 | 21.2 / 25.1 / 30.5 | 25.4 |
| v3-C1a-calm-s030u085-codel-r1 | main | router->switch | 103 | 28.3 / 34.1 / 42.1 | 30.9 |
| v3-C1a-calm-s030u085-codel-r2 | main | router->switch | 103 | 27.9 / 33.6 / 52.0 | 30.9 |
| v3-C1a-calm-s030u085-pfifo-r1 | main | router->switch | 103 | 28.3 / 33.8 / 41.9 | 30.9 |
| v3-C1a-calm-s030u085-pfifo-r2 | main | router->switch | 103 | 27.5 / 32.8 / 38.9 | 30.9 |
| v3-C1a-calm-s065u050-codel-r1 | main | router->switch | 103 | 35.7 / 41.3 / 52.3 | 39.3 |
| v3-C1a-calm-s065u050-codel-r2 | main | router->switch | 103 | 32.5 / 38.5 / 48.1 | 39.3 |
| v3-C1a-calm-s065u050-pfifo-r1 | main | router->switch | 103 | 35.0 / 40.5 / 42.5 | 39.3 |
| v3-C1a-calm-s065u050-pfifo-r2 | main | router->switch | 103 | 32.7 / 39.3 / 42.1 | 39.3 |
| v3-C1a-calm-s065u070-codel-r1 | main | router->switch | 103 | 52.0 / 59.9 / 73.2 | 55.1 |
| v3-C1a-calm-s065u070-codel-r2 | main | router->switch | 103 | 48.5 / 57.6 / 69.0 | 55.1 |
| v3-C1a-calm-s065u070-pfifo-r1 | main | router->switch | 103 | 33.6 / 41.0 / 42.1 | 55.1 |
| v3-C1a-calm-s065u070-pfifo-r2 | main | router->switch | 103 | 34.3 / 40.5 / 42.1 | 55.1 |
| v3-C1a-calm-s065u085-codel-r1 | main | router->switch | 103 | 53.7 / 69.5 / 92.5 | 66.9 |
| v3-C1a-calm-s065u085-codel-r2 | main | router->switch | 103 | 59.2 / 70.4 / 103.1 | 66.9 |
| v3-C1a-calm-s065u085-pfifo-r1 | main | router->switch | 103 | 29.8 / 40.3 / 41.9 | 66.9 |
| v3-C1a-calm-s065u085-pfifo-r2 | main | router->switch | 103 | 28.2 / 37.1 / 42.0 | 66.9 |
| v3-C1b-calm-split4-pfifo-r1 | up | r1->r2 | 103 | 22.7 / 26.4 / 29.6 | 25.4 |
| v3-C1b-calm-split4-pfifo-r1 | a | r2->switch-a | 103 | 11.0 / 14.1 / 20.1 | 25.4 |
| v3-C1b-calm-split4-pfifo-r1 | b | r2->switch-b | 103 | 11.5 / 14.2 / 24.5 | 25.4 |
| v3-C1b-calm-split4-pfifo-r2 | up | r1->r2 | 103 | 20.8 / 24.2 / 31.3 | 25.4 |
| v3-C1b-calm-split4-pfifo-r2 | a | r2->switch-a | 103 | 11.1 / 14.5 / 23.6 | 25.4 |
| v3-C1b-calm-split4-pfifo-r2 | b | r2->switch-b | 103 | 10.7 / 14.5 / 27.7 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r1 | root | rr->r0 | 103 | 21.5 / 25.8 / 28.9 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r1 | X | r0->r1 | 103 | 12.0 / 15.0 / 19.3 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r1 | Y | r0->r2 | 103 | 10.8 / 13.7 / 19.0 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r1 | A | r1->switch-a | 103 | 7.3 / 10.6 / 17.8 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r1 | B | r1->switch-b | 103 | 7.4 / 12.0 / 28.7 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r1 | C | r2->switch-c | 103 | 7.2 / 10.9 / 17.0 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r1 | D | r2->switch-d | 103 | 7.0 / 10.6 / 22.5 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r2 | root | rr->r0 | 103 | 21.1 / 25.4 / 33.6 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r2 | X | r0->r1 | 103 | 10.9 / 13.5 / 18.1 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r2 | Y | r0->r2 | 103 | 11.1 / 14.0 / 17.4 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r2 | A | r1->switch-a | 103 | 6.6 / 10.6 / 12.9 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r2 | B | r1->switch-b | 103 | 7.0 / 11.1 / 20.4 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r2 | C | r2->switch-c | 103 | 6.4 / 10.1 / 15.9 | 25.4 |
| v3-C1b-calm-tree16-pfifo-r2 | D | r2->switch-d | 103 | 6.9 / 10.3 / 15.3 | 25.4 |
| v3-C1b-calm-uneven-pfifo-r1 | A | r2->switch-a | 103 | 22.1 / 27.9 / 35.4 | 25.4 |
| v3-C1b-calm-uneven-pfifo-r1 | B | r2->switch-b | 103 | 21.9 / 25.7 / 35.2 | 25.4 |
| v3-C1b-calm-uneven-pfifo-r1 | C | r2->switch-c | 103 | 21.5 / 25.4 / 30.3 | 25.4 |
| v3-C1b-calm-uneven-pfifo-r2 | A | r2->switch-a | 103 | 21.4 / 26.2 / 33.9 | 25.4 |
| v3-C1b-calm-uneven-pfifo-r2 | B | r2->switch-b | 103 | 21.1 / 24.6 / 29.8 | 25.4 |
| v3-C1b-calm-uneven-pfifo-r2 | C | r2->switch-c | 103 | 21.1 / 24.7 / 31.0 | 25.4 |
| v3-C2-sburst-s030u070-cake-r1 | main | router->switch | 178 | 15.8 / 24.8 / 30.6 | 25.4 |
| v3-C2-sburst-s030u070-cake-r2 | main | router->switch | 183 | 13.4 / 19.6 / 26.6 | 25.4 |
| v3-C2-sburst-s030u070-codel-r1 | main | router->switch | 178 | 8.9 / 13.1 / 17.7 | 25.4 |
| v3-C2-sburst-s030u070-codel-r2 | main | router->switch | 183 | 8.3 / 11.8 / 17.4 | 25.4 |
| v3-C2-sburst-s030u070-fq_codel-r1 | main | router->switch | 178 | 10.2 / 15.0 / 21.0 | 25.4 |
| v3-C2-sburst-s030u070-fq_codel-r2 | main | router->switch | 183 | 10.1 / 14.3 / 19.5 | 25.4 |
| v3-C2-sburst-s030u070-pfifo-r1 | main | router->switch | 178 | 8.5 / 12.1 / 18.2 | 25.4 |
| v3-C2-sburst-s030u070-pfifo-r2 | main | router->switch | 183 | 7.9 / 12.1 / 19.1 | 25.4 |
| v3-C2-sburst-s030u070-pie-r1 | main | router->switch | 178 | 6.8 / 12.3 / 22.4 | 25.4 |
| v3-C2-sburst-s030u070-pie-r2 | main | router->switch | 183 | 10.6 / 17.1 / 23.8 | 25.4 |
| v3-C2-sburst-s030u070-red-r1 | main | router->switch | 178 | 8.8 / 13.6 / 19.6 | 25.4 |
| v3-C2-sburst-s030u070-red-r2 | main | router->switch | 183 | 8.1 / 13.9 / 25.8 | 25.4 |
| v3-C3a-sburst-s010u070-codel-r1 | main | router->switch | 178 | 1.8 / 2.7 / 4.0 | 8.5 |
| v3-C3a-sburst-s010u070-codel-r2 | main | router->switch | 183 | 1.8 / 2.7 / 3.7 | 8.5 |
| v3-C3a-sburst-s010u070-pfifo-r1 | main | router->switch | 178 | 1.6 / 2.3 / 3.1 | 8.5 |
| v3-C3a-sburst-s010u070-pfifo-r2 | main | router->switch | 183 | 1.5 / 2.3 / 3.0 | 8.5 |
| v3-C3a-sburst-s065u070-codel-r1 | main | router->switch | 178 | 24.4 / 32.9 / 41.5 | 55.1 |
| v3-C3a-sburst-s065u070-codel-r2 | main | router->switch | 183 | 22.9 / 32.9 / 50.0 | 55.1 |
| v3-C3a-sburst-s065u070-pfifo-r1 | main | router->switch | 178 | 23.9 / 33.7 / 42.0 | 55.1 |
| v3-C3a-sburst-s065u070-pfifo-r2 | main | router->switch | 183 | 23.6 / 33.4 / 42.4 | 55.1 |
| v3-C3b-sburst-legacy-pfifo-r1 | main | router->switch | 178 | 34.7 / 47.2 / 57.8 | None |
| v3-C3b-sburst-legacy-pfifo-r2 | main | router->switch | 183 | 31.4 / 43.2 / 57.3 | None |
| v3-C4-sramp-s030u070-codel-r1 | main | router->switch | 96 | 8.6 / 19.1 / 30.1 | 25.4 |
| v3-C4-sramp-s030u070-codel-r2 | main | router->switch | 86 | 8.4 / 17.3 / 23.2 | 25.4 |
| v3-C4-sramp-s030u070-fq_codel-r1 | main | router->switch | 96 | 9.9 / 14.6 / 22.0 | 25.4 |
| v3-C4-sramp-s030u070-fq_codel-r2 | main | router->switch | 86 | 10.3 / 15.0 / 22.9 | 25.4 |
| v3-C4-sramp-s030u070-pfifo-r1 | main | router->switch | 96 | 8.6 / 12.7 / 17.0 | 25.4 |
| v3-C4-sramp-s030u070-pfifo-r2 | main | router->switch | 86 | 7.0 / 11.0 / 15.4 | 25.4 |
| v3-C4-sramp-s030u070-pie-r1 | main | router->switch | 96 | 7.4 / 12.9 / 22.6 | 25.4 |
| v3-C4-sramp-s030u070-pie-r2 | main | router->switch | 86 | 10.2 / 16.0 / 20.1 | 25.4 |
| v3-C5-stcp-s030u070-codel-r1 | main | router->switch | 171 | 7.9 / 14.9 / 29.2 | 25.4 |
| v3-C5-stcp-s030u070-codel-r2 | main | router->switch | 163 | 9.2 / 16.1 / 33.3 | 25.4 |
| v3-C5-stcp-s030u070-fq_codel-r1 | main | router->switch | 171 | 13.7 / 18.3 / 23.4 | 25.4 |
| v3-C5-stcp-s030u070-fq_codel-r2 | main | router->switch | 163 | 13.2 / 17.6 / 23.7 | 25.4 |
| v3-C5-stcp-s030u070-pfifo-r1 | main | router->switch | 171 | 6.9 / 11.4 / 14.4 | 25.4 |
| v3-C5-stcp-s030u070-pfifo-r2 | main | router->switch | 163 | 7.0 / 10.7 / 14.8 | 25.4 |
| v3-C5-stcp-s030u070-pie-r1 | main | router->switch | 171 | 7.3 / 13.6 / 23.5 | 25.4 |
| v3-C5-stcp-s030u070-pie-r2 | main | router->switch | 163 | 6.7 / 11.6 / 28.6 | 25.4 |
| v3-C6-sjoin-s030u070-codel-r1 | main | router->switch | 38 | 13.5 / 22.9 / 28.1 | 25.4 |
| v3-C6-sjoin-s030u070-codel-r2 | main | router->switch | 36 | 20.0 / 25.3 / 27.9 | 25.4 |
| v3-C6-sjoin-s030u070-fq_codel-r1 | main | router->switch | 38 | 22.6 / 26.4 / 29.6 | 25.4 |
| v3-C6-sjoin-s030u070-fq_codel-r2 | main | router->switch | 36 | 21.9 / 26.3 / 29.8 | 25.4 |
| v3-C6-sjoin-s030u070-pfifo-r1 | main | router->switch | 38 | 7.2 / 10.6 / 14.6 | 25.4 |
| v3-C6-sjoin-s030u070-pfifo-r2 | main | router->switch | 36 | 6.9 / 9.5 / 12.6 | 25.4 |
| v3-C7-hhier-s030-codel-r1 | up | r1->r2 | 534 | 9.5 / 13.1 / 18.3 | 25.4 |
| v3-C7-hhier-s030-codel-r1 | a | r2->switch-a | 534 | 5.5 / 9.2 / 15.9 | 25.4 |
| v3-C7-hhier-s030-codel-r1 | b | r2->switch-b | 534 | 5.4 / 8.8 / 14.5 | 25.4 |
| v3-C7-hhier-s030-codel-r2 | up | r1->r2 | 501 | 9.4 / 12.8 / 21.8 | 25.4 |
| v3-C7-hhier-s030-codel-r2 | a | r2->switch-a | 501 | 5.4 / 9.4 / 18.4 | 25.4 |
| v3-C7-hhier-s030-codel-r2 | b | r2->switch-b | 501 | 5.6 / 9.3 / 18.4 | 25.4 |
| v3-C7-hhier-s030-fq_codel-r1 | up | r1->r2 | 534 | 10.2 / 13.9 / 18.2 | 25.4 |
| v3-C7-hhier-s030-fq_codel-r1 | a | r2->switch-a | 534 | 2.9 / 5.6 / 10.4 | 25.4 |
| v3-C7-hhier-s030-fq_codel-r1 | b | r2->switch-b | 534 | 2.8 / 5.4 / 9.5 | 25.4 |
| v3-C7-hhier-s030-fq_codel-r2 | up | r1->r2 | 501 | 10.3 / 13.9 / 18.8 | 25.4 |
| v3-C7-hhier-s030-fq_codel-r2 | a | r2->switch-a | 501 | 3.0 / 5.9 / 13.6 | 25.4 |
| v3-C7-hhier-s030-fq_codel-r2 | b | r2->switch-b | 501 | 2.8 / 5.4 / 14.1 | 25.4 |
| v3-C7-hhier-s030-pfifo-r1 | up | r1->r2 | 534 | 8.8 / 12.2 / 17.6 | 25.4 |
| v3-C7-hhier-s030-pfifo-r1 | a | r2->switch-a | 534 | 5.2 / 8.4 / 13.4 | 25.4 |
| v3-C7-hhier-s030-pfifo-r1 | b | r2->switch-b | 534 | 5.6 / 8.7 / 14.7 | 25.4 |
| v3-C7-hhier-s030-pfifo-r2 | up | r1->r2 | 501 | 8.6 / 12.3 / 26.0 | 25.4 |
| v3-C7-hhier-s030-pfifo-r2 | a | r2->switch-a | 501 | 5.4 / 9.3 / 19.1 | 25.4 |
| v3-C7-hhier-s030-pfifo-r2 | b | r2->switch-b | 501 | 5.1 / 9.3 / 24.9 | 25.4 |
| v3-C7-hhier-s030-pie-r1 | up | r1->r2 | 534 | 8.4 / 12.7 / 24.0 | 25.4 |
| v3-C7-hhier-s030-pie-r1 | a | r2->switch-a | 534 | 5.6 / 10.4 / 19.2 | 25.4 |
| v3-C7-hhier-s030-pie-r1 | b | r2->switch-b | 534 | 5.0 / 9.0 / 22.3 | 25.4 |
| v3-C7-hhier-s030-pie-r2 | up | r1->r2 | 501 | 8.0 / 12.9 / 23.3 | 25.4 |
| v3-C7-hhier-s030-pie-r2 | a | r2->switch-a | 501 | 5.2 / 9.5 / 17.9 | 25.4 |
| v3-C7-hhier-s030-pie-r2 | b | r2->switch-b | 501 | 5.1 / 8.9 / 16.2 | 25.4 |
| v3-C8-hhier-s065-pfifo-r1 | up | r1->r2 | 534 | 24.7 / 31.8 / 42.4 | 55.1 |
| v3-C8-hhier-s065-pfifo-r1 | a | r2->switch-a | 534 | 8.8 / 15.1 / 41.2 | 55.1 |
| v3-C8-hhier-s065-pfifo-r1 | b | r2->switch-b | 534 | 8.7 / 15.1 / 41.1 | 55.1 |
| v3-C8-hhier-s065-pfifo-r2 | up | r1->r2 | 501 | 25.3 / 32.5 / 42.2 | 55.1 |
| v3-C8-hhier-s065-pfifo-r2 | a | r2->switch-a | 501 | 9.8 / 17.9 / 41.8 | 55.1 |
| v3-C8-hhier-s065-pfifo-r2 | b | r2->switch-b | 501 | 9.0 / 15.7 / 30.9 | 55.1 |
| v3-C9-hdepth-tree16-codel-r1 | root | rr->r0 | 491 | 10.9 / 15.0 / 26.1 | 25.4 |
| v3-C9-hdepth-tree16-codel-r1 | X | r0->r1 | 491 | 6.3 / 10.2 / 14.5 | 25.4 |
| v3-C9-hdepth-tree16-codel-r1 | Y | r0->r2 | 491 | 6.5 / 10.7 / 16.7 | 25.4 |
| v3-C9-hdepth-tree16-codel-r1 | A | r1->switch-a | 491 | 5.2 / 9.3 / 14.9 | 25.4 |
| v3-C9-hdepth-tree16-codel-r1 | B | r1->switch-b | 491 | 5.4 / 9.4 / 18.5 | 25.4 |
| v3-C9-hdepth-tree16-codel-r1 | C | r2->switch-c | 491 | 5.8 / 10.0 / 25.4 | 25.4 |
| v3-C9-hdepth-tree16-codel-r1 | D | r2->switch-d | 491 | 6.1 / 10.3 / 19.0 | 25.4 |
| v3-C9-hdepth-tree16-codel-r2 | root | rr->r0 | 493 | 11.0 / 14.9 / 32.2 | 25.4 |
| v3-C9-hdepth-tree16-codel-r2 | X | r0->r1 | 493 | 6.5 / 10.4 / 16.8 | 25.4 |
| v3-C9-hdepth-tree16-codel-r2 | Y | r0->r2 | 493 | 6.2 / 10.0 / 16.5 | 25.4 |
| v3-C9-hdepth-tree16-codel-r2 | A | r1->switch-a | 493 | 5.4 / 9.6 / 18.0 | 25.4 |
| v3-C9-hdepth-tree16-codel-r2 | B | r1->switch-b | 493 | 5.5 / 9.6 / 17.0 | 25.4 |
| v3-C9-hdepth-tree16-codel-r2 | C | r2->switch-c | 493 | 5.3 / 9.4 / 15.5 | 25.4 |
| v3-C9-hdepth-tree16-codel-r2 | D | r2->switch-d | 493 | 4.9 / 8.7 / 14.0 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r1 | root | rr->r0 | 491 | 11.9 / 16.0 / 25.0 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r1 | X | r0->r1 | 491 | 3.1 / 5.6 / 11.9 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r1 | Y | r0->r2 | 491 | 3.0 / 5.7 / 11.2 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r1 | A | r1->switch-a | 491 | 3.6 / 6.2 / 19.0 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r1 | B | r1->switch-b | 491 | 3.4 / 6.2 / 19.8 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r1 | C | r2->switch-c | 491 | 3.6 / 6.4 / 11.2 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r1 | D | r2->switch-d | 491 | 3.6 / 6.6 / 15.1 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r2 | root | rr->r0 | 493 | 11.6 / 15.2 / 29.7 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r2 | X | r0->r1 | 493 | 3.0 / 5.7 / 10.1 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r2 | Y | r0->r2 | 493 | 3.1 / 5.7 / 9.8 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r2 | A | r1->switch-a | 493 | 3.7 / 6.7 / 12.9 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r2 | B | r1->switch-b | 493 | 3.4 / 6.6 / 11.7 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r2 | C | r2->switch-c | 493 | 3.7 / 6.5 / 12.0 | 25.4 |
| v3-C9-hdepth-tree16-fq_codel-r2 | D | r2->switch-d | 493 | 3.3 / 5.8 / 10.8 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r1 | root | rr->r0 | 491 | 10.6 / 14.6 / 21.8 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r1 | X | r0->r1 | 491 | 6.2 / 10.3 / 15.8 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r1 | Y | r0->r2 | 491 | 6.0 / 9.5 / 14.7 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r1 | A | r1->switch-a | 491 | 5.3 / 9.4 / 22.5 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r1 | B | r1->switch-b | 491 | 5.2 / 9.9 / 18.7 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r1 | C | r2->switch-c | 491 | 5.5 / 9.5 / 15.7 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r1 | D | r2->switch-d | 491 | 5.5 / 9.6 / 16.5 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r2 | root | rr->r0 | 493 | 11.1 / 15.1 / 25.7 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r2 | X | r0->r1 | 493 | 6.1 / 9.8 / 17.4 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r2 | Y | r0->r2 | 493 | 6.4 / 9.8 / 15.8 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r2 | A | r1->switch-a | 493 | 5.1 / 8.9 / 15.0 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r2 | B | r1->switch-b | 493 | 5.3 / 9.4 / 18.5 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r2 | C | r2->switch-c | 493 | 5.5 / 10.2 / 16.2 | 25.4 |
| v3-C9-hdepth-tree16-pfifo-r2 | D | r2->switch-d | 493 | 5.3 / 9.1 / 21.8 | 25.4 |
| v3-G1-calm-legacy-pfifo-r1 | main | router->switch | 103 | 42.4 / 56.3 / 57.8 | None |
| v3-G1-calm-s030u070-pfifo-r1 | main | router->switch | 103 | 22.3 / 27.1 / 34.1 | 25.4 |
| v3-G2-calm-access-pfifo-r1 | main | router->switch | 103 | 22.4 / 26.9 / 37.3 | 25.4 |
| v3-G2-calm-rev-pfifo-r1 | main | r1->switch | 103 | 17.6 / 22.0 / 33.9 | 25.4 |
| v3-G2-calm-split4-pfifo-r1 | up | r1->r2 | 103 | 22.6 / 26.9 / 29.9 | 25.4 |
| v3-G2-calm-split4-pfifo-r1 | a | r2->switch-a | 103 | 11.4 / 14.7 / 24.8 | 25.4 |
| v3-G2-calm-split4-pfifo-r1 | b | r2->switch-b | 103 | 11.5 / 14.3 / 24.8 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | root | rr->r0 | 103 | 22.1 / 26.1 / 29.4 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | X | r0->r1 | 103 | 11.3 / 14.3 / 17.0 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | Y | r0->r2 | 103 | 11.1 / 14.4 / 17.4 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | A | r1->switch-a | 103 | 7.5 / 11.1 / 16.2 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | B | r1->switch-b | 103 | 6.7 / 10.8 / 15.2 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | C | r2->switch-c | 103 | 8.4 / 12.3 / 23.2 | 25.4 |
| v3-G2-calm-tree16-pfifo-r1 | D | r2->switch-d | 103 | 7.0 / 11.1 / 15.6 | 25.4 |
| v3-G2-calm-uneven-pfifo-r1 | A | r2->switch-a | 103 | 22.7 / 28.1 / 35.3 | 25.4 |
| v3-G2-calm-uneven-pfifo-r1 | B | r2->switch-b | 103 | 22.5 / 26.4 / 31.0 | 25.4 |
| v3-G2-calm-uneven-pfifo-r1 | C | r2->switch-c | 103 | 21.6 / 25.3 / 33.1 | 25.4 |
| v3-G3-sburst-s030u070-fq_codel-r1 | main | router->switch | 178 | 10.0 / 13.9 / 20.0 | 25.4 |
| v3-G3-sburst-s030u070-pfifo-r1 | main | router->switch | 178 | 8.1 / 12.7 / 17.5 | 25.4 |
| v3-M1-sburst-q100-pfifo-r1 | main | router->switch | 178 | 9.3 / 13.7 / 19.9 | 25.4 |
| v3-M1-sburst-q100-pfifo-r2 | main | router->switch | 183 | 7.9 / 11.5 / 15.3 | 25.4 |
| v3-M1-sburst-q300-pfifo-r1 | main | router->switch | 178 | 9.1 / 13.7 / 40.3 | 25.4 |
| v3-M1-sburst-q300-pfifo-r2 | main | router->switch | 183 | 8.4 / 12.6 / 19.8 | 25.4 |
| v3-M10-sburst-ip2-pfifo-r1 | main | router->switch | 178 | 4.1 / 5.7 / 8.7 | 25.4 |
| v3-M10-sburst-ip2-pfifo-r2 | main | router->switch | 183 | 3.9 / 5.5 / 9.0 | 25.4 |
| v3-M10-sburst-ip8-pfifo-r1 | main | router->switch | 178 | 12.0 / 16.9 / 21.6 | 25.4 |
| v3-M10-sburst-ip8-pfifo-r2 | main | router->switch | 183 | 11.6 / 16.6 / 20.3 | 25.4 |
| v3-M11-sburst-bw4x1-pfifo-r1 | main | router->switch | 178 | 31.5 / 39.2 / 42.7 | 55.1 |
| v3-M11-sburst-bw4x1-pfifo-r2 | main | router->switch | 183 | 31.9 / 40.3 / 42.7 | 55.1 |
| v3-M11-sburst-bw4x12-pfifo-r1 | main | router->switch | 178 | 18.2 / 26.7 / 34.2 | 55.1 |
| v3-M11-sburst-bw4x12-pfifo-r2 | main | router->switch | 183 | 16.4 / 26.0 / 35.4 | 55.1 |
| v3-M11-sburst-bw4x8-pfifo-r1 | main | router->switch | 178 | 16.2 / 25.7 / 38.2 | 55.1 |
| v3-M11-sburst-bw4x8-pfifo-r2 | main | router->switch | 183 | 15.9 / 24.2 / 41.2 | 55.1 |
| v3-M12-sburst-jitfwd-pfifo-r1 | main | router->switch | 178 | 9.7 / 13.8 / 19.5 | 25.4 |
| v3-M12-sburst-jitfwd-pfifo-r2 | main | router->switch | 183 | 8.4 / 14.0 / 19.8 | 25.4 |
| v3-M12-sburst-jitrev-pfifo-r1 | main | router->switch | 178 | 11.5 / 15.8 / 24.3 | 25.4 |
| v3-M12-sburst-jitrev-pfifo-r2 | main | router->switch | 183 | 10.9 / 15.6 / 23.9 | 25.4 |
| v3-M13-sburst-copa-codel-r1 | main | router->switch | 178 | 22.8 / 26.5 / 30.8 | 25.4 |
| v3-M13-sburst-copa-codel-r2 | main | router->switch | 183 | 22.5 / 26.0 / 32.9 | 25.4 |
| v3-M13-sburst-copa-pfifo-r1 | main | router->switch | 178 | 22.4 / 26.3 / 32.4 | 25.4 |
| v3-M13-sburst-copa-pfifo-r2 | main | router->switch | 183 | 22.5 / 26.5 / 30.7 | 25.4 |
| v3-M14-ssparse-s030u070-pfifo-r1 | main | router->switch | 477 | 10.1 / 14.1 / 20.9 | 25.4 |
| v3-M14-ssparse-s030u070-pfifo-r2 | main | router->switch | 482 | 9.7 / 13.9 / 20.2 | 25.4 |
| v3-M2-sburst-capdrop-codel-r1 | main | router->switch | 178 | 9.9 / 15.5 / 22.8 | 25.4 |
| v3-M2-sburst-capdrop-codel-r2 | main | router->switch | 183 | 8.4 / 12.6 / 19.9 | 25.4 |
| v3-M2-sburst-capdrop-pfifo-r1 | main | router->switch | 178 | 8.8 / 13.4 / 19.6 | 25.4 |
| v3-M2-sburst-capdrop-pfifo-r2 | main | router->switch | 183 | 8.5 / 12.7 / 15.8 | 25.4 |
| v3-M3-sburst-bgbursty-codel-r1 | main | router->switch | 178 | 6.3 / 15.3 / 23.0 | 25.4 |
| v3-M3-sburst-bgbursty-codel-r2 | main | router->switch | 183 | 8.0 / 16.7 / 164.8 | 25.4 |
| v3-M3-sburst-bgbursty-pfifo-r1 | main | router->switch | 178 | 6.0 / 15.0 / 21.0 | 25.4 |
| v3-M3-sburst-bgbursty-pfifo-r2 | main | router->switch | 183 | 7.3 / 16.5 / 41.7 | 25.4 |
| v3-M3-sburst-bgmix-codel-r1 | main | router->switch | 178 | 8.0 / 15.9 / 83.0 | 25.4 |
| v3-M3-sburst-bgmix-codel-r2 | main | router->switch | 183 | 7.0 / 12.6 / 16.4 | 25.4 |
| v3-M3-sburst-bgmix-pfifo-r1 | main | router->switch | 178 | 7.2 / 11.9 / 46.3 | 25.4 |
| v3-M3-sburst-bgmix-pfifo-r2 | main | router->switch | 183 | 6.4 / 11.4 / 47.0 | 25.4 |
| v3-M4-sburst-rttwide-pfifo-r1 | main | router->switch | 178 | 5.5 / 9.6 / 12.4 | 25.4 |
| v3-M4-sburst-rttwide-pfifo-r2 | main | router->switch | 183 | 5.6 / 9.1 / 17.2 | 25.4 |
| v3-M4-sburst-rttx05-pfifo-r1 | main | router->switch | 178 | 8.3 / 12.8 / 19.7 | 25.4 |
| v3-M4-sburst-rttx05-pfifo-r2 | main | router->switch | 183 | 7.6 / 11.7 / 19.3 | 25.4 |
| v3-M4-sburst-rttx4-pfifo-r1 | main | router->switch | 178 | 3.4 / 6.0 / 9.1 | 25.4 |
| v3-M4-sburst-rttx4-pfifo-r2 | main | router->switch | 183 | 3.0 / 5.8 / 8.9 | 25.4 |
| v3-M5-sburst-fps15-codel-r1 | main | router->switch | 178 | 11.7 / 16.6 / 21.0 | 25.4 |
| v3-M5-sburst-fps15-codel-r2 | main | router->switch | 183 | 11.4 / 16.2 / 24.3 | 25.4 |
| v3-M5-sburst-fps15-pfifo-r1 | main | router->switch | 178 | 11.6 / 16.3 / 21.2 | 25.4 |
| v3-M5-sburst-fps15-pfifo-r2 | main | router->switch | 183 | 10.7 / 15.5 / 20.9 | 25.4 |
| v3-M5-sburst-fps60-codel-r1 | main | router->switch | 178 | 4.9 / 7.2 / 9.1 | 25.4 |
| v3-M5-sburst-fps60-codel-r2 | main | router->switch | 183 | 4.4 / 7.1 / 9.2 | 25.4 |
| v3-M5-sburst-fps60-pfifo-r1 | main | router->switch | 178 | 4.9 / 7.5 / 9.3 | 25.4 |
| v3-M5-sburst-fps60-pfifo-r2 | main | router->switch | 183 | 4.1 / 6.5 / 8.5 | 25.4 |
| v3-M6-calm-stag-pfifo-r1 | main | router->switch | 103 | 3.7 / 4.9 / 18.9 | 25.4 |
| v3-M6-calm-stag-pfifo-r2 | main | router->switch | 103 | 3.8 / 4.9 / 19.6 | 25.4 |
| v3-M6-sburst-stag-pfifo-r1 | main | router->switch | 178 | 1.9 / 2.6 / 3.5 | 25.4 |
| v3-M6-sburst-stag-pfifo-r2 | main | router->switch | 183 | 1.8 / 2.5 / 3.4 | 25.4 |
| v3-M7-hhier-noroot-pfifo-r1 | a | r2->switch-a | 363 | 9.2 / 12.9 / 18.9 | 25.4 |
| v3-M7-hhier-noroot-pfifo-r1 | b | r2->switch-b | 363 | 8.9 / 13.2 / 16.7 | 25.4 |
| v3-M7-hhier-noroot-pfifo-r2 | a | r2->switch-a | 355 | 9.0 / 12.8 / 18.9 | 25.4 |
| v3-M7-hhier-noroot-pfifo-r2 | b | r2->switch-b | 355 | 8.7 / 13.2 / 18.1 | 25.4 |
| v3-M8-hhier-mixab-mixab-r1 | up | r1->r2 | 534 | 9.3 / 13.0 / 17.3 | 25.4 |
| v3-M8-hhier-mixab-mixab-r1 | a | r2->switch-a | 534 | 5.1 / 8.8 / 13.9 | 25.4 |
| v3-M8-hhier-mixab-mixab-r1 | b | r2->switch-b | 534 | 5.9 / 9.3 / 14.7 | 25.4 |
| v3-M8-hhier-mixab-mixab-r2 | up | r1->r2 | 501 | 9.3 / 13.2 / 17.8 | 25.4 |
| v3-M8-hhier-mixab-mixab-r2 | a | r2->switch-a | 501 | 5.2 / 9.5 / 21.6 | 25.4 |
| v3-M8-hhier-mixab-mixab-r2 | b | r2->switch-b | 501 | 5.6 / 9.2 / 17.5 | 25.4 |
| v3-M9-sstress-s030u070-codel-r1 | main | router->switch | 163 | 9.6 / 16.4 / 26.5 | 25.4 |
| v3-M9-sstress-s030u070-codel-r2 | main | router->switch | 172 | 8.4 / 15.0 / 26.3 | 25.4 |
| v3-M9-sstress-s030u070-pfifo-r1 | main | router->switch | 163 | 6.5 / 14.2 / 25.6 | 25.4 |
| v3-M9-sstress-s030u070-pfifo-r2 | main | router->switch | 172 | 6.6 / 14.2 / 21.6 | 25.4 |

## Installed AQM leaves (`tc qdisc show`, handle 20:; `ecn` must not appear; cake has no ECN switch)

- v3-C10-hindep-s030-codel-r1 r1/r1-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r1 r1/r1-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r1 r1/r1-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r1 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r1 r2/r2-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r1 r2/r2-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r2 r1/r1-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r2 r1/r1-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r2 r1/r1-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r2 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r2 r2/r2-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-codel-r2 r2/r2-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C10-hindep-s030-fq_codel-r1 r1/r1-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r1 r1/r1-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r1 r1/r1-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r1 r2/r2-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r1 r2/r2-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r1 r2/r2-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r2 r1/r1-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r2 r1/r1-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r2 r1/r1-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r2 r2/r2-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r2 r2/r2-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-fq_codel-r2 r2/r2-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C10-hindep-s030-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C10-hindep-s030-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C10-hindep-s030-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-C10-hindep-s030-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C10-hindep-s030-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C10-hindep-s030-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C10-hindep-s030-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C10-hindep-s030-pfifo-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C10-hindep-s030-pfifo-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-C10-hindep-s030-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C10-hindep-s030-pfifo-r2 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C10-hindep-s030-pfifo-r2 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C11-huneven-uneven-codel-r1 r1/r1-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r1 r1/r1-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r1 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r1 r2/r2-eth1: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r1 r2/r2-eth3: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r1 r2/r2-eth5: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r2 r1/r1-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r2 r1/r1-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r2 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r2 r2/r2-eth1: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r2 r2/r2-eth3: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-codel-r2 r2/r2-eth5: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C11-huneven-uneven-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C11-huneven-uneven-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C11-huneven-uneven-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C11-huneven-uneven-pfifo-r1 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 154p`
- v3-C11-huneven-uneven-pfifo-r1 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C11-huneven-uneven-pfifo-r1 r2/r2-eth5: `qdisc pfifo 20: parent 5:1 limit 338p`
- v3-C11-huneven-uneven-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C11-huneven-uneven-pfifo-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C11-huneven-uneven-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C11-huneven-uneven-pfifo-r2 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 154p`
- v3-C11-huneven-uneven-pfifo-r2 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C11-huneven-uneven-pfifo-r2 r2/r2-eth5: `qdisc pfifo 20: parent 5:1 limit 338p`
- v3-C12-amixed-access-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 ra/ra-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 ra/ra-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 rb/rb-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 rb/rb-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 rc/rc-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 rc/rc-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 rd/rd-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r1 rd/rd-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 ra/ra-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 ra/ra-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 rb/rb-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 rb/rb-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 rc/rc-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 rc/rc-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 rd/rd-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-codel-r2 rd/rd-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C12-amixed-access-fq_codel-r1 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 ra/ra-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 ra/ra-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 rb/rb-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 rb/rb-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 rc/rc-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 rc/rc-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 rd/rd-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r1 rd/rd-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 ra/ra-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 ra/ra-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 rb/rb-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 rb/rb-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 rc/rc-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 rc/rc-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 rd/rd-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-fq_codel-r2 rd/rd-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C12-amixed-access-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C12-amixed-access-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C12-amixed-access-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C12-amixed-access-pfifo-r1 ra/ra-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C12-amixed-access-pfifo-r1 ra/ra-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-C12-amixed-access-pfifo-r1 rb/rb-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C12-amixed-access-pfifo-r1 rb/rb-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-C12-amixed-access-pfifo-r1 rc/rc-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C12-amixed-access-pfifo-r1 rc/rc-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-C12-amixed-access-pfifo-r1 rd/rd-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C12-amixed-access-pfifo-r1 rd/rd-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-C12-amixed-access-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C12-amixed-access-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C12-amixed-access-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C12-amixed-access-pfifo-r2 ra/ra-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C12-amixed-access-pfifo-r2 ra/ra-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-C12-amixed-access-pfifo-r2 rb/rb-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C12-amixed-access-pfifo-r2 rb/rb-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-C12-amixed-access-pfifo-r2 rc/rc-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C12-amixed-access-pfifo-r2 rc/rc-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-C12-amixed-access-pfifo-r2 rd/rd-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C12-amixed-access-pfifo-r2 rd/rd-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-C12-amixed-access-pie-r1 router/router-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 router/router-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 router/router-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 ra/ra-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 ra/ra-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 rb/rb-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 rb/rb-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 rc/rc-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 rc/rc-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 rd/rd-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r1 rd/rd-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 router/router-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 router/router-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 router/router-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 ra/ra-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 ra/ra-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 rb/rb-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 rb/rb-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 rc/rc-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 rc/rc-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 rd/rd-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C12-amixed-access-pie-r2 rd/rd-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C13-llong-s030-codel-r1 r1/r1-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r1 r1/r1-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r1 r1/r1-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r1 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r1 r2/r2-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r1 r2/r2-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r2 r1/r1-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r2 r1/r1-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r2 r1/r1-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r2 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r2 r2/r2-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-codel-r2 r2/r2-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C13-llong-s030-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C13-llong-s030-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C13-llong-s030-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-C13-llong-s030-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C13-llong-s030-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C13-llong-s030-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C13-llong-s030-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C13-llong-s030-pfifo-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C13-llong-s030-pfifo-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-C13-llong-s030-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C13-llong-s030-pfifo-r2 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C13-llong-s030-pfifo-r2 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C14-rrev-rev-fq_codel-r1 r0/r0-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r1 r0/r0-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r1 r0/r0-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r1 r1/r1-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r1 r1/r1-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r2 r0/r0-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r2 r0/r0-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r2 r0/r0-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r2 r1/r1-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-fq_codel-r2 r1/r1-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C14-rrev-rev-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C14-rrev-rev-pfifo-r1 r0/r0-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C14-rrev-rev-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C14-rrev-rev-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 42p`
- v3-C14-rrev-rev-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C14-rrev-rev-pfifo-r2 r0/r0-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C14-rrev-rev-pfifo-r2 r0/r0-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C14-rrev-rev-pfifo-r2 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C14-rrev-rev-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 42p`
- v3-C14-rrev-rev-pfifo-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C15-nloss-s030u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C15-nloss-s030u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C15-nloss-s030u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C15-nloss-s030u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C15-nloss-s030u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C15-nloss-s030u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C15-nloss-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C15-nloss-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C15-nloss-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C15-nloss-s030u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C15-nloss-s030u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C15-nloss-s030u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C1a-calm-legacy-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-legacy-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-legacy-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-legacy-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-legacy-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-legacy-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-legacy-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-C1a-calm-legacy-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-C1a-calm-legacy-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 100p`
- v3-C1a-calm-legacy-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-C1a-calm-legacy-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-C1a-calm-legacy-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 100p`
- v3-C1a-calm-s010u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s010u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s010u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 307p`
- v3-C1a-calm-s010u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s010u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s010u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 307p`
- v3-C1a-calm-s010u085-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u085-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u085-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u085-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u085-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u085-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s010u085-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s010u085-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s010u085-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 253p`
- v3-C1a-calm-s010u085-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s010u085-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s010u085-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 253p`
- v3-C1a-calm-s030u050-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u050-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u050-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u050-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u050-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u050-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u050-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s030u050-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s030u050-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 315p`
- v3-C1a-calm-s030u050-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s030u050-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s030u050-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 315p`
- v3-C1a-calm-s030u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C1a-calm-s030u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s030u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s030u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C1a-calm-s030u085-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u085-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u085-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u085-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u085-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u085-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s030u085-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s030u085-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s030u085-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 186p`
- v3-C1a-calm-s030u085-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s030u085-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s030u085-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 186p`
- v3-C1a-calm-s065u050-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u050-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u050-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u050-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u050-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u050-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u050-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s065u050-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s065u050-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 146p`
- v3-C1a-calm-s065u050-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s065u050-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s065u050-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 146p`
- v3-C1a-calm-s065u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s065u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s065u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 104p`
- v3-C1a-calm-s065u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s065u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s065u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 104p`
- v3-C1a-calm-s065u085-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u085-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u085-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u085-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u085-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u085-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C1a-calm-s065u085-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s065u085-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s065u085-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 86p`
- v3-C1a-calm-s065u085-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1a-calm-s065u085-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1a-calm-s065u085-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 86p`
- v3-C1b-calm-split4-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1b-calm-split4-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1b-calm-split4-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-C1b-calm-split4-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-split4-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C1b-calm-split4-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C1b-calm-split4-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1b-calm-split4-pfifo-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1b-calm-split4-pfifo-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-C1b-calm-split4-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-split4-pfifo-r2 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C1b-calm-split4-pfifo-r2 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C1b-calm-tree16-pfifo-r1 rr/rr-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1b-calm-tree16-pfifo-r1 rr/rr-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1b-calm-tree16-pfifo-r1 rr/rr-eth2: `qdisc pfifo 20: parent 5:1 limit 409p`
- v3-C1b-calm-tree16-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-tree16-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C1b-calm-tree16-pfifo-r1 r0/r0-eth4: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C1b-calm-tree16-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-tree16-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C1b-calm-tree16-pfifo-r1 r1/r1-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C1b-calm-tree16-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-tree16-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C1b-calm-tree16-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C1b-calm-tree16-pfifo-r2 rr/rr-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1b-calm-tree16-pfifo-r2 rr/rr-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1b-calm-tree16-pfifo-r2 rr/rr-eth2: `qdisc pfifo 20: parent 5:1 limit 409p`
- v3-C1b-calm-tree16-pfifo-r2 r0/r0-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-tree16-pfifo-r2 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C1b-calm-tree16-pfifo-r2 r0/r0-eth4: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C1b-calm-tree16-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-tree16-pfifo-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C1b-calm-tree16-pfifo-r2 r1/r1-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C1b-calm-tree16-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-tree16-pfifo-r2 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C1b-calm-tree16-pfifo-r2 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C1b-calm-uneven-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1b-calm-uneven-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1b-calm-uneven-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-uneven-pfifo-r1 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 154p`
- v3-C1b-calm-uneven-pfifo-r1 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C1b-calm-uneven-pfifo-r1 r2/r2-eth5: `qdisc pfifo 20: parent 5:1 limit 338p`
- v3-C1b-calm-uneven-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C1b-calm-uneven-pfifo-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C1b-calm-uneven-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C1b-calm-uneven-pfifo-r2 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 154p`
- v3-C1b-calm-uneven-pfifo-r2 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C1b-calm-uneven-pfifo-r2 r2/r2-eth5: `qdisc pfifo 20: parent 5:1 limit 338p`
- v3-C2-sburst-s030u070-cake-r1 router/router-eth0: `qdisc cake 20: parent 10:1 bandwidth unlimited besteffort triple-isolate nonat nowash no-ack-filter split-gso rtt 100ms raw overhead 0`
- v3-C2-sburst-s030u070-cake-r1 router/router-eth1: `qdisc cake 20: parent 10:1 bandwidth unlimited besteffort triple-isolate nonat nowash no-ack-filter split-gso rtt 100ms raw overhead 0`
- v3-C2-sburst-s030u070-cake-r1 router/router-eth2: `qdisc cake 20: parent 5:1 bandwidth unlimited besteffort triple-isolate nonat nowash no-ack-filter split-gso rtt 100ms raw overhead 0`
- v3-C2-sburst-s030u070-cake-r2 router/router-eth0: `qdisc cake 20: parent 10:1 bandwidth unlimited besteffort triple-isolate nonat nowash no-ack-filter split-gso rtt 100ms raw overhead 0`
- v3-C2-sburst-s030u070-cake-r2 router/router-eth1: `qdisc cake 20: parent 10:1 bandwidth unlimited besteffort triple-isolate nonat nowash no-ack-filter split-gso rtt 100ms raw overhead 0`
- v3-C2-sburst-s030u070-cake-r2 router/router-eth2: `qdisc cake 20: parent 5:1 bandwidth unlimited besteffort triple-isolate nonat nowash no-ack-filter split-gso rtt 100ms raw overhead 0`
- v3-C2-sburst-s030u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C2-sburst-s030u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C2-sburst-s030u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C2-sburst-s030u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C2-sburst-s030u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C2-sburst-s030u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C2-sburst-s030u070-fq_codel-r1 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C2-sburst-s030u070-fq_codel-r1 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C2-sburst-s030u070-fq_codel-r1 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C2-sburst-s030u070-fq_codel-r2 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C2-sburst-s030u070-fq_codel-r2 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C2-sburst-s030u070-fq_codel-r2 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C2-sburst-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C2-sburst-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C2-sburst-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C2-sburst-s030u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C2-sburst-s030u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C2-sburst-s030u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C2-sburst-s030u070-pie-r1 router/router-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C2-sburst-s030u070-pie-r1 router/router-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C2-sburst-s030u070-pie-r1 router/router-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C2-sburst-s030u070-pie-r2 router/router-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C2-sburst-s030u070-pie-r2 router/router-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C2-sburst-s030u070-pie-r2 router/router-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C2-sburst-s030u070-red-r1 router/router-eth0: `qdisc red 20: parent 10:1 limit 1875000b min 187500b max 562500b`
- v3-C2-sburst-s030u070-red-r1 router/router-eth1: `qdisc red 20: parent 10:1 limit 937500b min 93750b max 281250b`
- v3-C2-sburst-s030u070-red-r1 router/router-eth2: `qdisc red 20: parent 5:1 limit 1012500b min 101156b max 303469b`
- v3-C2-sburst-s030u070-red-r2 router/router-eth0: `qdisc red 20: parent 10:1 limit 1875000b min 187500b max 562500b`
- v3-C2-sburst-s030u070-red-r2 router/router-eth1: `qdisc red 20: parent 10:1 limit 937500b min 93750b max 281250b`
- v3-C2-sburst-s030u070-red-r2 router/router-eth2: `qdisc red 20: parent 5:1 limit 1012500b min 101156b max 303469b`
- v3-C3a-sburst-s010u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s010u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s010u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s010u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s010u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s010u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s010u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C3a-sburst-s010u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C3a-sburst-s010u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 307p`
- v3-C3a-sburst-s010u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C3a-sburst-s010u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C3a-sburst-s010u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 307p`
- v3-C3a-sburst-s065u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s065u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s065u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s065u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s065u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s065u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C3a-sburst-s065u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C3a-sburst-s065u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C3a-sburst-s065u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 104p`
- v3-C3a-sburst-s065u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C3a-sburst-s065u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C3a-sburst-s065u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 104p`
- v3-C3b-sburst-legacy-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-C3b-sburst-legacy-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-C3b-sburst-legacy-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 100p`
- v3-C3b-sburst-legacy-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-C3b-sburst-legacy-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-C3b-sburst-legacy-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 100p`
- v3-C4-sramp-s030u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C4-sramp-s030u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C4-sramp-s030u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C4-sramp-s030u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C4-sramp-s030u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C4-sramp-s030u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C4-sramp-s030u070-fq_codel-r1 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C4-sramp-s030u070-fq_codel-r1 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C4-sramp-s030u070-fq_codel-r1 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C4-sramp-s030u070-fq_codel-r2 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C4-sramp-s030u070-fq_codel-r2 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C4-sramp-s030u070-fq_codel-r2 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C4-sramp-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C4-sramp-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C4-sramp-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C4-sramp-s030u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C4-sramp-s030u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C4-sramp-s030u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C4-sramp-s030u070-pie-r1 router/router-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C4-sramp-s030u070-pie-r1 router/router-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C4-sramp-s030u070-pie-r1 router/router-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C4-sramp-s030u070-pie-r2 router/router-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C4-sramp-s030u070-pie-r2 router/router-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C4-sramp-s030u070-pie-r2 router/router-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C5-stcp-s030u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C5-stcp-s030u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C5-stcp-s030u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C5-stcp-s030u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C5-stcp-s030u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C5-stcp-s030u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C5-stcp-s030u070-fq_codel-r1 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C5-stcp-s030u070-fq_codel-r1 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C5-stcp-s030u070-fq_codel-r1 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C5-stcp-s030u070-fq_codel-r2 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C5-stcp-s030u070-fq_codel-r2 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C5-stcp-s030u070-fq_codel-r2 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C5-stcp-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C5-stcp-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C5-stcp-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C5-stcp-s030u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C5-stcp-s030u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C5-stcp-s030u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C5-stcp-s030u070-pie-r1 router/router-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C5-stcp-s030u070-pie-r1 router/router-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C5-stcp-s030u070-pie-r1 router/router-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C5-stcp-s030u070-pie-r2 router/router-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C5-stcp-s030u070-pie-r2 router/router-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C5-stcp-s030u070-pie-r2 router/router-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C6-sjoin-s030u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C6-sjoin-s030u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C6-sjoin-s030u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C6-sjoin-s030u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C6-sjoin-s030u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C6-sjoin-s030u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C6-sjoin-s030u070-fq_codel-r1 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C6-sjoin-s030u070-fq_codel-r1 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C6-sjoin-s030u070-fq_codel-r1 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C6-sjoin-s030u070-fq_codel-r2 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C6-sjoin-s030u070-fq_codel-r2 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C6-sjoin-s030u070-fq_codel-r2 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C6-sjoin-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C6-sjoin-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C6-sjoin-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C6-sjoin-s030u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C6-sjoin-s030u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C6-sjoin-s030u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-C7-hhier-s030-codel-r1 r1/r1-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r1 r1/r1-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r1 r1/r1-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r1 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r1 r2/r2-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r1 r2/r2-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r2 r1/r1-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r2 r1/r1-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r2 r1/r1-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r2 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r2 r2/r2-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-codel-r2 r2/r2-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C7-hhier-s030-fq_codel-r1 r1/r1-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r1 r1/r1-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r1 r1/r1-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r1 r2/r2-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r1 r2/r2-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r1 r2/r2-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r2 r1/r1-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r2 r1/r1-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r2 r1/r1-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r2 r2/r2-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r2 r2/r2-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-fq_codel-r2 r2/r2-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C7-hhier-s030-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C7-hhier-s030-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C7-hhier-s030-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-C7-hhier-s030-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C7-hhier-s030-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C7-hhier-s030-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C7-hhier-s030-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C7-hhier-s030-pfifo-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C7-hhier-s030-pfifo-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-C7-hhier-s030-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C7-hhier-s030-pfifo-r2 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C7-hhier-s030-pfifo-r2 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-C7-hhier-s030-pie-r1 r1/r1-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r1 r1/r1-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r1 r1/r1-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r1 r2/r2-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r1 r2/r2-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r1 r2/r2-eth4: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r2 r1/r1-eth0: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r2 r1/r1-eth1: `qdisc pie 20: parent 10:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r2 r1/r1-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r2 r2/r2-eth0: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r2 r2/r2-eth2: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C7-hhier-s030-pie-r2 r2/r2-eth4: `qdisc pie 20: parent 5:1 limit 1000p target 15ms tupdate 15ms alpha 2 beta 20`
- v3-C8-hhier-s065-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C8-hhier-s065-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C8-hhier-s065-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 180p`
- v3-C8-hhier-s065-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C8-hhier-s065-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 90p`
- v3-C8-hhier-s065-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 90p`
- v3-C8-hhier-s065-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C8-hhier-s065-pfifo-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C8-hhier-s065-pfifo-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 180p`
- v3-C8-hhier-s065-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C8-hhier-s065-pfifo-r2 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 90p`
- v3-C8-hhier-s065-pfifo-r2 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 90p`
- v3-C9-hdepth-tree16-codel-r1 rr/rr-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 rr/rr-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 rr/rr-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r0/r0-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r0/r0-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r0/r0-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r1/r1-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r1/r1-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r1/r1-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r2/r2-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r1 r2/r2-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 rr/rr-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 rr/rr-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 rr/rr-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r0/r0-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r0/r0-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r0/r0-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r1/r1-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r1/r1-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r1/r1-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r2/r2-eth0: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r2/r2-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-codel-r2 r2/r2-eth4: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-C9-hdepth-tree16-fq_codel-r1 rr/rr-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 rr/rr-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 rr/rr-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r0/r0-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r0/r0-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r0/r0-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r1/r1-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r1/r1-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r1/r1-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r2/r2-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r2/r2-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r1 r2/r2-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 rr/rr-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 rr/rr-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 rr/rr-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r0/r0-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r0/r0-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r0/r0-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r1/r1-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r1/r1-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r1/r1-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r2/r2-eth0: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r2/r2-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-fq_codel-r2 r2/r2-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-C9-hdepth-tree16-pfifo-r1 rr/rr-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C9-hdepth-tree16-pfifo-r1 rr/rr-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C9-hdepth-tree16-pfifo-r1 rr/rr-eth2: `qdisc pfifo 20: parent 5:1 limit 409p`
- v3-C9-hdepth-tree16-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C9-hdepth-tree16-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C9-hdepth-tree16-pfifo-r1 r0/r0-eth4: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C9-hdepth-tree16-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C9-hdepth-tree16-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C9-hdepth-tree16-pfifo-r1 r1/r1-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C9-hdepth-tree16-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C9-hdepth-tree16-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C9-hdepth-tree16-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C9-hdepth-tree16-pfifo-r2 rr/rr-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-C9-hdepth-tree16-pfifo-r2 rr/rr-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-C9-hdepth-tree16-pfifo-r2 rr/rr-eth2: `qdisc pfifo 20: parent 5:1 limit 409p`
- v3-C9-hdepth-tree16-pfifo-r2 r0/r0-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C9-hdepth-tree16-pfifo-r2 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C9-hdepth-tree16-pfifo-r2 r0/r0-eth4: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-C9-hdepth-tree16-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C9-hdepth-tree16-pfifo-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C9-hdepth-tree16-pfifo-r2 r1/r1-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C9-hdepth-tree16-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-C9-hdepth-tree16-pfifo-r2 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-C9-hdepth-tree16-pfifo-r2 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G1-calm-legacy-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-G1-calm-legacy-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 100p`
- v3-G1-calm-legacy-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 100p`
- v3-G1-calm-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G1-calm-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G1-calm-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-G2-calm-access-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-access-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-G2-calm-access-pfifo-r1 ra/ra-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 ra/ra-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-G2-calm-access-pfifo-r1 rb/rb-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 rb/rb-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-G2-calm-access-pfifo-r1 rc/rc-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 rc/rc-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-G2-calm-access-pfifo-r1 rd/rd-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-access-pfifo-r1 rd/rd-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-G2-calm-rev-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-rev-pfifo-r1 r0/r0-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-rev-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-rev-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 42p`
- v3-G2-calm-rev-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-G2-calm-split4-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-split4-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-split4-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-G2-calm-split4-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-split4-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-G2-calm-split4-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-G2-calm-tree16-pfifo-r1 rr/rr-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-tree16-pfifo-r1 rr/rr-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-tree16-pfifo-r1 rr/rr-eth2: `qdisc pfifo 20: parent 5:1 limit 409p`
- v3-G2-calm-tree16-pfifo-r1 r0/r0-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-tree16-pfifo-r1 r0/r0-eth2: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-G2-calm-tree16-pfifo-r1 r0/r0-eth4: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-G2-calm-tree16-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-tree16-pfifo-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G2-calm-tree16-pfifo-r1 r1/r1-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G2-calm-tree16-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-tree16-pfifo-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G2-calm-tree16-pfifo-r1 r2/r2-eth4: `qdisc pfifo 20: parent 5:1 limit 103p`
- v3-G2-calm-uneven-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G2-calm-uneven-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G2-calm-uneven-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-G2-calm-uneven-pfifo-r1 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 154p`
- v3-G2-calm-uneven-pfifo-r1 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 205p`
- v3-G2-calm-uneven-pfifo-r1 r2/r2-eth5: `qdisc pfifo 20: parent 5:1 limit 338p`
- v3-G3-sburst-s030u070-fq_codel-r1 router/router-eth0: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-G3-sburst-s030u070-fq_codel-r1 router/router-eth1: `qdisc fq_codel 20: parent 10:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-G3-sburst-s030u070-fq_codel-r1 router/router-eth2: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-G3-sburst-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-G3-sburst-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-G3-sburst-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M1-sburst-q100-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 834p`
- v3-M1-sburst-q100-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M1-sburst-q100-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 450p`
- v3-M1-sburst-q100-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 834p`
- v3-M1-sburst-q100-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M1-sburst-q100-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 450p`
- v3-M1-sburst-q300-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 2500p`
- v3-M1-sburst-q300-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 1250p`
- v3-M1-sburst-q300-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 1349p`
- v3-M1-sburst-q300-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 2500p`
- v3-M1-sburst-q300-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 1250p`
- v3-M1-sburst-q300-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 1349p`
- v3-M10-sburst-ip2-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M10-sburst-ip2-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M10-sburst-ip2-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M10-sburst-ip2-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M10-sburst-ip2-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M10-sburst-ip2-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M10-sburst-ip8-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M10-sburst-ip8-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M10-sburst-ip8-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M10-sburst-ip8-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M10-sburst-ip8-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M10-sburst-ip8-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M11-sburst-bw4x1-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M11-sburst-bw4x1-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M11-sburst-bw4x1-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 38p`
- v3-M11-sburst-bw4x1-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M11-sburst-bw4x1-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M11-sburst-bw4x1-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 38p`
- v3-M11-sburst-bw4x12-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M11-sburst-bw4x12-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M11-sburst-bw4x12-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 194p`
- v3-M11-sburst-bw4x12-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M11-sburst-bw4x12-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M11-sburst-bw4x12-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 194p`
- v3-M11-sburst-bw4x8-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M11-sburst-bw4x8-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M11-sburst-bw4x8-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 302p`
- v3-M11-sburst-bw4x8-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M11-sburst-bw4x8-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M11-sburst-bw4x8-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 302p`
- v3-M12-sburst-jitfwd-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M12-sburst-jitfwd-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M12-sburst-jitfwd-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M12-sburst-jitfwd-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M12-sburst-jitfwd-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M12-sburst-jitfwd-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M12-sburst-jitrev-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M12-sburst-jitrev-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M12-sburst-jitrev-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M12-sburst-jitrev-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M12-sburst-jitrev-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M12-sburst-jitrev-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M13-sburst-copa-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M13-sburst-copa-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M13-sburst-copa-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M13-sburst-copa-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M13-sburst-copa-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M13-sburst-copa-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M13-sburst-copa-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M13-sburst-copa-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M13-sburst-copa-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M13-sburst-copa-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M13-sburst-copa-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M13-sburst-copa-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M14-ssparse-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M14-ssparse-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M14-ssparse-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M14-ssparse-s030u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M14-ssparse-s030u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M14-ssparse-s030u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M2-sburst-capdrop-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M2-sburst-capdrop-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M2-sburst-capdrop-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M2-sburst-capdrop-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M2-sburst-capdrop-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M2-sburst-capdrop-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M2-sburst-capdrop-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M2-sburst-capdrop-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M2-sburst-capdrop-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M2-sburst-capdrop-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M2-sburst-capdrop-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M2-sburst-capdrop-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M3-sburst-bgbursty-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgbursty-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgbursty-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgbursty-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgbursty-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgbursty-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgbursty-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M3-sburst-bgbursty-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M3-sburst-bgbursty-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M3-sburst-bgbursty-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M3-sburst-bgbursty-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M3-sburst-bgbursty-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M3-sburst-bgmix-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgmix-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgmix-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgmix-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgmix-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgmix-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M3-sburst-bgmix-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M3-sburst-bgmix-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M3-sburst-bgmix-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M3-sburst-bgmix-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M3-sburst-bgmix-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M3-sburst-bgmix-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M4-sburst-rttwide-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 834p`
- v3-M4-sburst-rttwide-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M4-sburst-rttwide-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 450p`
- v3-M4-sburst-rttwide-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 834p`
- v3-M4-sburst-rttwide-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M4-sburst-rttwide-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 450p`
- v3-M4-sburst-rttx05-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M4-sburst-rttx05-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-M4-sburst-rttx05-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 113p`
- v3-M4-sburst-rttx05-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M4-sburst-rttx05-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 105p`
- v3-M4-sburst-rttx05-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 113p`
- v3-M4-sburst-rttx4-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 1667p`
- v3-M4-sburst-rttx4-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 834p`
- v3-M4-sburst-rttx4-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 900p`
- v3-M4-sburst-rttx4-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 1667p`
- v3-M4-sburst-rttx4-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 834p`
- v3-M4-sburst-rttx4-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 900p`
- v3-M5-sburst-fps15-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps15-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps15-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps15-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps15-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps15-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps15-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M5-sburst-fps15-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M5-sburst-fps15-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M5-sburst-fps15-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M5-sburst-fps15-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M5-sburst-fps15-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M5-sburst-fps60-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps60-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps60-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps60-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps60-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps60-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M5-sburst-fps60-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M5-sburst-fps60-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M5-sburst-fps60-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M5-sburst-fps60-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M5-sburst-fps60-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M5-sburst-fps60-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M6-calm-stag-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M6-calm-stag-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M6-calm-stag-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M6-calm-stag-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M6-calm-stag-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M6-calm-stag-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M6-sburst-stag-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M6-sburst-stag-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M6-sburst-stag-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M6-sburst-stag-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M6-sburst-stag-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M6-sburst-stag-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M7-hhier-noroot-pfifo-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M7-hhier-noroot-pfifo-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M7-hhier-noroot-pfifo-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-M7-hhier-noroot-pfifo-r1 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-M7-hhier-noroot-pfifo-r1 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-M7-hhier-noroot-pfifo-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M7-hhier-noroot-pfifo-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M7-hhier-noroot-pfifo-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-M7-hhier-noroot-pfifo-r2 r2/r2-eth1: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-M7-hhier-noroot-pfifo-r2 r2/r2-eth3: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-M8-hhier-mixab-mixab-r1 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M8-hhier-mixab-mixab-r1 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M8-hhier-mixab-mixab-r1 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-M8-hhier-mixab-mixab-r1 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-M8-hhier-mixab-mixab-r1 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-M8-hhier-mixab-mixab-r1 r2/r2-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-M8-hhier-mixab-mixab-r2 r1/r1-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M8-hhier-mixab-mixab-r2 r1/r1-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M8-hhier-mixab-mixab-r2 r1/r1-eth2: `qdisc pfifo 20: parent 5:1 limit 389p`
- v3-M8-hhier-mixab-mixab-r2 r2/r2-eth0: `qdisc pfifo 20: parent 5:1 limit 417p`
- v3-M8-hhier-mixab-mixab-r2 r2/r2-eth2: `qdisc pfifo 20: parent 5:1 limit 195p`
- v3-M8-hhier-mixab-mixab-r2 r2/r2-eth4: `qdisc fq_codel 20: parent 5:1 limit 10240p flows 1024 quantum 1514 target 5ms interval 100ms memory_limit 32Mb drop_batch 64`
- v3-M9-sstress-s030u070-codel-r1 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M9-sstress-s030u070-codel-r1 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M9-sstress-s030u070-codel-r1 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M9-sstress-s030u070-codel-r2 router/router-eth0: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M9-sstress-s030u070-codel-r2 router/router-eth1: `qdisc codel 20: parent 10:1 limit 1000p target 5ms interval 100ms`
- v3-M9-sstress-s030u070-codel-r2 router/router-eth2: `qdisc codel 20: parent 5:1 limit 1000p target 5ms interval 100ms`
- v3-M9-sstress-s030u070-pfifo-r1 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M9-sstress-s030u070-pfifo-r1 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M9-sstress-s030u070-pfifo-r1 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`
- v3-M9-sstress-s030u070-pfifo-r2 router/router-eth0: `qdisc pfifo 20: parent 10:1 limit 417p`
- v3-M9-sstress-s030u070-pfifo-r2 router/router-eth1: `qdisc pfifo 20: parent 10:1 limit 209p`
- v3-M9-sstress-s030u070-pfifo-r2 router/router-eth2: `qdisc pfifo 20: parent 5:1 limit 225p`

## Check 4 per traced egress (target = gated; info = reported only)

| run | hop | role | dequeues | unmatched deq / enq (allowed) | max per 200 ms deq / enq | 4a | backlogged gaps | within max(10 %, 15 us) (within 10 %) | jitter us p1 / p99 | 20 ms windows within 5 % (n) | 4b |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v3-C10-hindep-s030-codel-r1 | pub->r1 | info | 1369237 | 0 / 0 (68.46) | 0 / 0 | ok | 544047 | 0.9993 (0.6739) | -9.34 / 3.84 | nan (0) | ok |
| v3-C10-hindep-s030-codel-r1 | r1->sub-ctrl | info | 169025 | 0 / 0 (8.45) | 0 / 0 | ok | 107495 | 0.9024 (0.9024) | -200.54 / 2.11 | nan (0) | FAIL |
| v3-C10-hindep-s030-codel-r1 | r1->r2 | target | 4454060 | 0 / 0 (222.7) | 0 / 0 | ok | 3158917 | 0.9994 (0.9978) | -2.95 / 2.92 | 1.0 (8955) | ok |
| v3-C10-hindep-s030-codel-r1 | r2->switch-a | target | 2092139 | 0 / 0 (104.61) | 0 / 0 | ok | 1197198 | 0.9994 (0.9991) | -2.99 / 2.94 | 1.0 (4885) | ok |
| v3-C10-hindep-s030-codel-r1 | r2->switch-b | target | 2187971 | 0 / 0 (109.4) | 0 / 0 | ok | 1403701 | 0.9995 (0.9992) | -3.35 / 3.32 | 1.0 (8125) | ok |
| v3-C10-hindep-s030-codel-r2 | pub->r1 | info | 1291813 | 0 / 0 (64.59) | 0 / 0 | ok | 477701 | 0.9988 (0.6196) | -9.44 / 4.47 | nan (0) | ok |
| v3-C10-hindep-s030-codel-r2 | r1->sub-ctrl | info | 168432 | 0 / 0 (8.42) | 0 / 0 | ok | 112014 | 0.8861 (0.8860) | -200.63 / 2.29 | nan (0) | FAIL |
| v3-C10-hindep-s030-codel-r2 | r1->r2 | target | 4429524 | 0 / 0 (221.48) | 0 / 0 | ok | 3073986 | 0.9993 (0.9978) | -2.94 / 2.91 | 1.0 (8934) | ok |
| v3-C10-hindep-s030-codel-r2 | r2->switch-a | target | 2172155 | 0 / 0 (108.61) | 0 / 0 | ok | 1369340 | 0.9995 (0.9992) | -3.38 / 3.33 | 1.0 (7736) | ok |
| v3-C10-hindep-s030-codel-r2 | r2->switch-b | target | 2187557 | 0 / 0 (109.38) | 0 / 0 | ok | 1403190 | 0.9996 (0.9992) | -3.37 / 3.34 | 1.0 (8415) | ok |
| v3-C10-hindep-s030-fq_codel-r1 | pub->r1 | info | 1356658 | 0 / 0 (67.83) | 0 / 0 | ok | 658128 | 0.9964 (0.5148) | -9.48 / 9.52 | nan (0) | ok |
| v3-C10-hindep-s030-fq_codel-r1 | r1->sub-ctrl | info | 169014 | 0 / 0 (8.45) | 0 / 0 | ok | 120669 | 0.8871 (0.8871) | -199.6 / 2.39 | nan (0) | FAIL |
| v3-C10-hindep-s030-fq_codel-r1 | r1->r2 | target | 4448566 | 0 / 0 (222.43) | 0 / 0 | ok | 2649776 | 0.9987 (0.9950) | -4.02 / 4.11 | 1.0 (168) | ok |
| v3-C10-hindep-s030-fq_codel-r1 | r2->switch-a | target | 2095674 | 0 / 0 (104.78) | 0 / 0 | ok | 797411 | 0.9979 (0.9971) | -4.35 / 4.27 | 1.0 (203) | ok |
| v3-C10-hindep-s030-fq_codel-r1 | r2->switch-b | target | 2180974 | 0 / 0 (109.05) | 0 / 0 | ok | 988886 | 0.9984 (0.9977) | -4.38 / 4.35 | 1.0 (445) | ok |
| v3-C10-hindep-s030-fq_codel-r2 | pub->r1 | info | 1312713 | 0 / 0 (65.64) | 0 / 0 | ok | 568883 | 0.9964 (0.4664) | -9.49 / 9.43 | nan (0) | ok |
| v3-C10-hindep-s030-fq_codel-r2 | r1->sub-ctrl | info | 168320 | 0 / 0 (8.42) | 0 / 0 | ok | 115192 | 0.8814 (0.8813) | -199.61 / 2.37 | nan (0) | FAIL |
| v3-C10-hindep-s030-fq_codel-r2 | r1->r2 | target | 4435337 | 0 / 0 (221.77) | 0 / 0 | ok | 2632799 | 0.9985 (0.9944) | -4.08 / 4.15 | 1.0 (317) | ok |
| v3-C10-hindep-s030-fq_codel-r2 | r2->switch-a | target | 2175947 | 0 / 0 (108.8) | 0 / 0 | ok | 1000867 | 0.9984 (0.9977) | -4.45 / 4.42 | 1.0 (529) | ok |
| v3-C10-hindep-s030-fq_codel-r2 | r2->switch-b | target | 2186582 | 0 / 0 (109.33) | 0 / 0 | ok | 1040789 | 0.9984 (0.9977) | -4.57 / 4.56 | 1.0 (868) | ok |
| v3-C10-hindep-s030-pfifo-r1 | pub->r1 | info | 1418896 | 0 / 0 (70.94) | 0 / 0 | ok | 533114 | 0.9991 (0.6320) | -9.39 / 4.02 | nan (0) | ok |
| v3-C10-hindep-s030-pfifo-r1 | r1->sub-ctrl | info | 169112 | 0 / 0 (8.46) | 0 / 0 | ok | 119758 | 0.8964 (0.8964) | -200.09 / 2.18 | nan (0) | FAIL |
| v3-C10-hindep-s030-pfifo-r1 | r1->r2 | target | 4467542 | 0 / 0 (223.38) | 0 / 0 | ok | 3166160 | 0.9994 (0.9979) | -2.17 / 2.19 | 1.0 (8764) | ok |
| v3-C10-hindep-s030-pfifo-r1 | r2->switch-a | target | 2079957 | 0 / 0 (104) | 0 / 0 | ok | 1153956 | 0.9994 (0.9991) | -2.36 / 2.33 | 1.0 (4576) | ok |
| v3-C10-hindep-s030-pfifo-r1 | r2->switch-b | target | 2181768 | 0 / 0 (109.09) | 0 / 0 | ok | 1374499 | 0.9995 (0.9993) | -2.25 / 2.25 | 1.0 (7824) | ok |
| v3-C10-hindep-s030-pfifo-r2 | pub->r1 | info | 1364836 | 0 / 0 (68.24) | 0 / 0 | ok | 477861 | 0.9989 (0.6077) | -9.44 / 4.09 | nan (0) | ok |
| v3-C10-hindep-s030-pfifo-r2 | r1->sub-ctrl | info | 168658 | 0 / 0 (8.43) | 0 / 0 | ok | 116437 | 0.8946 (0.8945) | -199.91 / 2.17 | nan (0) | FAIL |
| v3-C10-hindep-s030-pfifo-r2 | r1->r2 | target | 4458002 | 0 / 0 (222.9) | 0 / 0 | ok | 3112054 | 0.9993 (0.9980) | -2.1 / 2.12 | 1.0 (8792) | ok |
| v3-C10-hindep-s030-pfifo-r2 | r2->switch-a | target | 2160748 | 0 / 0 (108.04) | 0 / 0 | ok | 1330121 | 0.9995 (0.9992) | -2.2 / 2.18 | 1.0 (7372) | ok |
| v3-C10-hindep-s030-pfifo-r2 | r2->switch-b | target | 2174875 | 0 / 0 (108.74) | 0 / 0 | ok | 1369559 | 0.9996 (0.9993) | -2.15 / 2.16 | 1.0 (8058) | ok |
| v3-C11-huneven-uneven-codel-r1 | pub->r1 | info | 2351580 | 0 / 0 (117.58) | 0 / 0 | ok | 1259294 | 0.9974 (0.4970) | -9.51 / 8.34 | nan (0) | ok |
| v3-C11-huneven-uneven-codel-r1 | r1->sub-ctrl | info | 169365 | 0 / 0 (8.47) | 0 / 0 | ok | 116929 | 0.9360 (0.9360) | -199.72 / 2.32 | nan (0) | FAIL |
| v3-C11-huneven-uneven-codel-r1 | r1->r2 | info | 2182238 | 0 / 0 (109.11) | 0 / 0 | ok | 11680 | 0.9994 (0.5683) | -7.95 / 5.06 | nan (0) | ok |
| v3-C11-huneven-uneven-codel-r1 | r2->switch-a | target | 1773897 | 0 / 0 (88.69) | 0 / 0 | ok | 1278560 | 0.9998 (0.9996) | -4.01 / 3.93 | 1.0 (10152) | ok |
| v3-C11-huneven-uneven-codel-r1 | r2->switch-b | target | 2386916 | 0 / 0 (119.35) | 0 / 0 | ok | 1746990 | 0.9996 (0.9990) | -3.78 / 3.71 | 1.0 (10003) | ok |
| v3-C11-huneven-uneven-codel-r1 | r2->switch-c | target | 3827590 | 0 / 0 (191.38) | 0 / 0 | ok | 2675197 | 0.9993 (0.9979) | -3.36 / 3.3 | 1.0 (7365) | ok |
| v3-C11-huneven-uneven-codel-r2 | pub->r1 | info | 2357681 | 0 / 0 (117.88) | 0 / 0 | ok | 1271697 | 0.9977 (0.4925) | -9.53 / 8.16 | nan (0) | ok |
| v3-C11-huneven-uneven-codel-r2 | r1->sub-ctrl | info | 168387 | 0 / 0 (8.42) | 0 / 0 | ok | 113599 | 0.9104 (0.9102) | -199.87 / 2.2 | nan (0) | FAIL |
| v3-C11-huneven-uneven-codel-r2 | r1->r2 | info | 2189318 | 0 / 0 (109.47) | 0 / 0 | ok | 11580 | 0.9996 (0.5365) | -7.99 / 4.82 | nan (0) | ok |
| v3-C11-huneven-uneven-codel-r2 | r2->switch-a | target | 1751983 | 0 / 0 (87.6) | 0 / 0 | ok | 1235139 | 0.9997 (0.9996) | -3.99 / 3.91 | 1.0 (9216) | ok |
| v3-C11-huneven-uneven-codel-r2 | r2->switch-b | target | 2350833 | 0 / 0 (117.54) | 0 / 0 | ok | 1673806 | 0.9996 (0.9990) | -3.76 / 3.68 | 1.0 (8752) | ok |
| v3-C11-huneven-uneven-codel-r2 | r2->switch-c | target | 3816020 | 0 / 0 (190.8) | 0 / 0 | ok | 2649079 | 0.9993 (0.9978) | -3.31 / 3.25 | 1.0 (7152) | ok |
| v3-C11-huneven-uneven-pfifo-r1 | pub->r1 | info | 2409483 | 0 / 0 (120.47) | 0 / 0 | ok | 1245718 | 0.9976 (0.4702) | -9.54 / 8.12 | nan (0) | ok |
| v3-C11-huneven-uneven-pfifo-r1 | r1->sub-ctrl | info | 169290 | 0 / 0 (8.46) | 0 / 0 | ok | 116341 | 0.9121 (0.9120) | -200.32 / 2.08 | nan (0) | FAIL |
| v3-C11-huneven-uneven-pfifo-r1 | r1->r2 | info | 2240218 | 0 / 0 (112.01) | 0 / 0 | ok | 10172 | 0.9993 (0.5507) | -8.16 / 5.14 | nan (0) | ok |
| v3-C11-huneven-uneven-pfifo-r1 | r2->switch-a | target | 1768136 | 0 / 0 (88.41) | 0 / 0 | ok | 1268970 | 0.9998 (0.9997) | -2.91 / 2.81 | 1.0 (9935) | ok |
| v3-C11-huneven-uneven-pfifo-r1 | r2->switch-b | target | 2377473 | 0 / 0 (118.87) | 0 / 0 | ok | 1729438 | 0.9996 (0.9992) | -2.89 / 2.83 | 1.0 (9802) | ok |
| v3-C11-huneven-uneven-pfifo-r1 | r2->switch-c | target | 3810760 | 0 / 0 (190.54) | 0 / 0 | ok | 2642098 | 0.9993 (0.9979) | -2.88 / 2.83 | 1.0 (7129) | ok |
| v3-C11-huneven-uneven-pfifo-r2 | pub->r1 | info | 2389360 | 0 / 0 (119.47) | 0 / 0 | ok | 1228298 | 0.9977 (0.4798) | -9.53 / 8.04 | nan (0) | ok |
| v3-C11-huneven-uneven-pfifo-r2 | r1->sub-ctrl | info | 168493 | 0 / 0 (8.42) | 0 / 0 | ok | 103132 | 0.9074 (0.9074) | -200.36 / 2.32 | 1.0 (1) | FAIL |
| v3-C11-huneven-uneven-pfifo-r2 | r1->r2 | info | 2220904 | 0 / 0 (111.05) | 0 / 0 | ok | 10027 | 0.9996 (0.5604) | -8.08 / 4.72 | nan (0) | ok |
| v3-C11-huneven-uneven-pfifo-r2 | r2->switch-a | target | 1743322 | 0 / 0 (87.17) | 0 / 0 | ok | 1214817 | 0.9998 (0.9997) | -2.96 / 2.82 | 1.0 (8813) | ok |
| v3-C11-huneven-uneven-pfifo-r2 | r2->switch-b | target | 2335609 | 0 / 0 (116.78) | 0 / 0 | ok | 1637639 | 0.9997 (0.9992) | -2.88 / 2.79 | 1.0 (8289) | ok |
| v3-C11-huneven-uneven-pfifo-r2 | r2->switch-c | target | 3800096 | 0 / 0 (190) | 0 / 0 | ok | 2615319 | 0.9993 (0.9979) | -2.84 / 2.77 | 1.0 (6885) | ok |
| v3-C12-amixed-access-codel-r1 | pub->router | info | 551244 | 0 / 0 (27.56) | 0 / 0 | ok | 209059 | 0.9959 (0.5613) | -9.51 / 7.67 | nan (0) | ok |
| v3-C12-amixed-access-codel-r1 | ra->sub-a | target | 48377 | 0 / 0 (3) | 0 / 0 | ok | 2330 | 0.9137 (0.9137) | -404.68 / 10.16 | 0.01633 (796) | FAIL |
| v3-C12-amixed-access-codel-r1 | rb->sub-b | target | 105200 | 0 / 0 (5.26) | 0 / 0 | ok | 6042 | 0.9467 (0.9467) | -404.61 / 6.86 | 0.67949 (390) | FAIL |
| v3-C12-amixed-access-codel-r1 | rc->sub-c | target | 106675 | 0 / 0 (5.33) | 0 / 0 | ok | 7338 | 0.9334 (0.9334) | -404.59 / 5.72 | 0.52414 (580) | FAIL |
| v3-C12-amixed-access-codel-r1 | rd->sub-d | target | 172078 | 0 / 0 (8.6) | 0 / 0 | ok | 22279 | 0.9808 (0.9808) | -403.99 / 6.8 | 0.70411 (632) | FAIL |
| v3-C12-amixed-access-codel-r1 | router->sub-ctrl | info | 112907 | 0 / 0 (5.65) | 0 / 0 | ok | 81920 | 0.8802 (0.8802) | -199.33 / 2.54 | nan (0) | FAIL |
| v3-C12-amixed-access-codel-r1 | router->switch | target | 1610541 | 0 / 0 (80.53) | 0 / 0 | ok | 999066 | 0.9992 (0.9986) | -3.72 / 3.69 | 1.0 (3549) | ok |
| v3-C12-amixed-access-codel-r2 | pub->router | info | 550709 | 0 / 0 (27.54) | 0 / 0 | ok | 235954 | 0.9959 (0.6146) | -9.48 / 7.81 | nan (0) | ok |
| v3-C12-amixed-access-codel-r2 | ra->sub-a | target | 48261 | 0 / 0 (3) | 0 / 0 | ok | 2536 | 0.7792 (0.7792) | -405.34 / 10.37 | 0.00121 (825) | FAIL |
| v3-C12-amixed-access-codel-r2 | rb->sub-b | target | 106049 | 0 / 0 (5.3) | 0 / 0 | ok | 10321 | 0.9369 (0.9369) | -404.51 / 7.79 | 0.59619 (577) | FAIL |
| v3-C12-amixed-access-codel-r2 | rc->sub-c | target | 105504 | 0 / 0 (5.28) | 0 / 0 | ok | 13145 | 0.9712 (0.9712) | -404.24 / 5.34 | 0.57231 (325) | FAIL |
| v3-C12-amixed-access-codel-r2 | rd->sub-d | target | 171371 | 0 / 0 (8.57) | 0 / 0 | ok | 20093 | 0.9778 (0.9778) | -404.32 / 8.03 | 0.70703 (669) | FAIL |
| v3-C12-amixed-access-codel-r2 | router->sub-ctrl | info | 112990 | 0 / 0 (5.65) | 0 / 0 | ok | 73193 | 0.8849 (0.8849) | -199.92 / 2.54 | nan (0) | FAIL |
| v3-C12-amixed-access-codel-r2 | router->switch | target | 1615294 | 0 / 0 (80.76) | 0 / 0 | ok | 1003477 | 0.9992 (0.9985) | -3.81 / 3.75 | 1.0 (3551) | ok |
| v3-C12-amixed-access-fq_codel-r1 | pub->router | info | 562614 | 0 / 0 (28.13) | 0 / 0 | ok | 272510 | 0.9914 (0.5080) | -9.45 / 13.91 | nan (0) | ok |
| v3-C12-amixed-access-fq_codel-r1 | ra->sub-a | target | 49651 | 0 / 0 (3) | 0 / 0 | ok | 1646 | 0.8317 (0.8317) | -404.73 / 13.53 | 0.00985 (812) | FAIL |
| v3-C12-amixed-access-fq_codel-r1 | rb->sub-b | target | 111825 | 0 / 0 (5.59) | 0 / 0 | ok | 4686 | 0.9161 (0.9157) | -404.7 / 10.56 | 0.63333 (630) | FAIL |
| v3-C12-amixed-access-fq_codel-r1 | rc->sub-c | target | 109787 | 0 / 0 (5.49) | 0 / 0 | ok | 3305 | 0.8439 (0.8436) | -405.61 / 12.17 | 0.62413 (431) | FAIL |
| v3-C12-amixed-access-fq_codel-r1 | rd->sub-d | target | 169936 | 0 / 0 (8.5) | 0 / 0 | ok | 21762 | 0.9762 (0.9762) | -403.93 / 8.29 | 0.69861 (647) | FAIL |
| v3-C12-amixed-access-fq_codel-r1 | router->sub-ctrl | info | 112948 | 0 / 0 (5.65) | 0 / 0 | ok | 75045 | 0.8318 (0.8318) | -199.66 / 3.22 | nan (0) | FAIL |
| v3-C12-amixed-access-fq_codel-r1 | router->switch | target | 1612873 | 0 / 0 (80.64) | 0 / 0 | ok | 811662 | 0.9987 (0.9962) | -5.64 / 5.76 | 1.0 (328) | ok |
| v3-C12-amixed-access-fq_codel-r2 | pub->router | info | 557943 | 0 / 0 (27.9) | 0 / 0 | ok | 245974 | 0.9898 (0.4856) | -9.45 / 15.16 | nan (0) | FAIL |
| v3-C12-amixed-access-fq_codel-r2 | ra->sub-a | target | 50575 | 0 / 0 (3) | 0 / 0 | ok | 1767 | 0.8138 (0.8138) | -404.97 / 13.4 | 0.00492 (813) | FAIL |
| v3-C12-amixed-access-fq_codel-r2 | rb->sub-b | target | 109434 | 0 / 0 (5.47) | 0 / 0 | ok | 3712 | 0.8812 (0.8812) | -405.1 / 10.34 | 0.66787 (554) | FAIL |
| v3-C12-amixed-access-fq_codel-r2 | rc->sub-c | target | 109911 | 1 / 0 (5.5) | 1 / 0 | ok | 3480 | 0.8052 (0.8049) | -405.33 / 7.9 | 0.56579 (380) | FAIL |
| v3-C12-amixed-access-fq_codel-r2 | rd->sub-d | target | 167908 | 0 / 0 (8.4) | 0 / 0 | ok | 21009 | 0.9749 (0.9749) | -404.19 / 7.78 | 0.7234 (658) | FAIL |
| v3-C12-amixed-access-fq_codel-r2 | router->sub-ctrl | info | 113048 | 0 / 0 (5.65) | 0 / 0 | ok | 80000 | 0.8741 (0.8740) | -199.16 / 3.42 | nan (0) | FAIL |
| v3-C12-amixed-access-fq_codel-r2 | router->switch | target | 1612474 | 0 / 0 (80.62) | 0 / 0 | ok | 804653 | 0.9987 (0.9968) | -5.44 / 5.57 | 1.0 (365) | ok |
| v3-C12-amixed-access-pfifo-r1 | pub->router | info | 557435 | 0 / 0 (27.87) | 0 / 0 | ok | 204604 | 0.9968 (0.5526) | -9.53 / 6.8 | nan (0) | ok |
| v3-C12-amixed-access-pfifo-r1 | ra->sub-a | target | 48960 | 0 / 0 (3) | 0 / 0 | ok | 1984 | 0.9299 (0.9299) | -404.75 / 4.84 | 0.02091 (813) | FAIL |
| v3-C12-amixed-access-pfifo-r1 | rb->sub-b | target | 105886 | 0 / 0 (5.29) | 0 / 0 | ok | 6280 | 0.9554 (0.9554) | -404.68 / 3.62 | 0.72084 (523) | FAIL |
| v3-C12-amixed-access-pfifo-r1 | rc->sub-c | target | 105052 | 0 / 0 (5.25) | 0 / 0 | ok | 7421 | 0.9414 (0.9413) | -404.73 / 3.81 | 0.68566 (544) | FAIL |
| v3-C12-amixed-access-pfifo-r1 | rd->sub-d | target | 172085 | 0 / 0 (8.6) | 0 / 0 | ok | 21503 | 0.9808 (0.9808) | -403.68 / 5.06 | 0.73237 (624) | FAIL |
| v3-C12-amixed-access-pfifo-r1 | router->sub-ctrl | info | 113143 | 0 / 0 (5.66) | 0 / 0 | ok | 79508 | 0.8678 (0.8678) | -199.42 / 2.92 | nan (0) | FAIL |
| v3-C12-amixed-access-pfifo-r1 | router->switch | target | 1604293 | 0 / 0 (80.21) | 0 / 0 | ok | 987351 | 0.9993 (0.9987) | -2.57 / 2.61 | 1.0 (3433) | ok |
| v3-C12-amixed-access-pfifo-r2 | pub->router | info | 553970 | 0 / 0 (27.7) | 0 / 0 | ok | 207387 | 0.9960 (0.5460) | -9.51 / 7.52 | nan (0) | ok |
| v3-C12-amixed-access-pfifo-r2 | ra->sub-a | target | 49623 | 0 / 0 (3) | 0 / 0 | ok | 2869 | 0.9247 (0.9247) | -404.49 / 7.07 | 0.01564 (831) | FAIL |
| v3-C12-amixed-access-pfifo-r2 | rb->sub-b | target | 106507 | 0 / 0 (5.33) | 0 / 0 | ok | 16825 | 0.9821 (0.9821) | -403.13 / 4.43 | 0.69291 (635) | FAIL |
| v3-C12-amixed-access-pfifo-r2 | rc->sub-c | target | 106512 | 0 / 0 (5.33) | 0 / 0 | ok | 9766 | 0.9660 (0.9660) | -404.09 / 3.76 | 0.73264 (677) | FAIL |
| v3-C12-amixed-access-pfifo-r2 | rd->sub-d | target | 166328 | 0 / 0 (8.32) | 0 / 0 | ok | 18461 | 0.9740 (0.9740) | -404.21 / 4.78 | 0.73295 (704) | FAIL |
| v3-C12-amixed-access-pfifo-r2 | router->sub-ctrl | info | 113160 | 0 / 0 (5.66) | 0 / 0 | ok | 81650 | 0.8801 (0.8800) | -199.32 / 2.68 | nan (0) | FAIL |
| v3-C12-amixed-access-pfifo-r2 | router->switch | target | 1606613 | 0 / 0 (80.33) | 0 / 0 | ok | 987841 | 0.9993 (0.9986) | -2.56 / 2.59 | 1.0 (3438) | ok |
| v3-C12-amixed-access-pie-r1 | pub->router | info | 576797 | 0 / 0 (28.84) | 0 / 0 | ok | 220736 | 0.9968 (0.5577) | -9.51 / 7.17 | nan (0) | ok |
| v3-C12-amixed-access-pie-r1 | ra->sub-a | target | 49953 | 0 / 0 (3) | 0 / 0 | ok | 2024 | 0.8582 (0.8582) | -405.0 / 13.85 | 0.0274 (730) | FAIL |
| v3-C12-amixed-access-pie-r1 | rb->sub-b | target | 110142 | 0 / 0 (5.51) | 0 / 0 | ok | 6557 | 0.9382 (0.9382) | -404.79 / 7.05 | 0.66837 (392) | FAIL |
| v3-C12-amixed-access-pie-r1 | rc->sub-c | target | 110169 | 1 / 0 (5.51) | 1 / 0 | ok | 5135 | 0.9280 (0.9280) | -405.2 / 7.74 | 0.61538 (299) | FAIL |
| v3-C12-amixed-access-pie-r1 | rd->sub-d | target | 179431 | 0 / 0 (8.97) | 0 / 0 | ok | 21449 | 0.9773 (0.9773) | -404.19 / 5.74 | 0.69195 (435) | FAIL |
| v3-C12-amixed-access-pie-r1 | router->sub-ctrl | info | 112981 | 0 / 0 (5.65) | 0 / 0 | ok | 80618 | 0.8711 (0.8711) | -199.56 / 2.83 | nan (0) | FAIL |
| v3-C12-amixed-access-pie-r1 | router->switch | target | 1602354 | 0 / 0 (80.12) | 0 / 0 | ok | 970358 | 0.9992 (0.9985) | -2.65 / 2.66 | 1.0 (2917) | ok |
| v3-C12-amixed-access-pie-r2 | pub->router | info | 577198 | 0 / 0 (28.86) | 0 / 0 | ok | 232281 | 0.9968 (0.5744) | -9.5 / 6.92 | nan (0) | ok |
| v3-C12-amixed-access-pie-r2 | ra->sub-a | target | 50054 | 0 / 0 (3) | 0 / 0 | ok | 2059 | 0.8674 (0.8674) | -405.09 / 14.88 | 0.00894 (783) | FAIL |
| v3-C12-amixed-access-pie-r2 | rb->sub-b | target | 109536 | 0 / 0 (5.48) | 0 / 0 | ok | 8176 | 0.9587 (0.9587) | -404.44 / 5.99 | 0.65084 (358) | FAIL |
| v3-C12-amixed-access-pie-r2 | rc->sub-c | target | 110611 | 0 / 0 (5.53) | 0 / 0 | ok | 16133 | 0.9786 (0.9785) | -403.86 / 4.14 | 0.61837 (283) | FAIL |
| v3-C12-amixed-access-pie-r2 | rd->sub-d | target | 179111 | 0 / 0 (8.96) | 0 / 0 | ok | 19200 | 0.9696 (0.9696) | -404.74 / 6.4 | 0.68249 (337) | FAIL |
| v3-C12-amixed-access-pie-r2 | router->sub-ctrl | info | 113027 | 0 / 0 (5.65) | 0 / 0 | ok | 80960 | 0.8670 (0.8670) | -199.76 / 2.52 | nan (0) | FAIL |
| v3-C12-amixed-access-pie-r2 | router->switch | target | 1606418 | 0 / 0 (80.32) | 0 / 0 | ok | 974588 | 0.9993 (0.9986) | -2.54 / 2.57 | 1.0 (3019) | ok |
| v3-C13-llong-s030-codel-r1 | pub->r1 | info | 851325 | 0 / 0 (42.57) | 0 / 0 | ok | 360674 | 0.9990 (0.6660) | -9.42 / 4.29 | nan (0) | ok |
| v3-C13-llong-s030-codel-r1 | r1->sub-ctrl | info | 111962 | 0 / 0 (5.6) | 0 / 0 | ok | 78499 | 0.9115 (0.9115) | -200.03 / 2.09 | nan (0) | FAIL |
| v3-C13-llong-s030-codel-r1 | r1->r2 | target | 2852875 | 0 / 0 (142.64) | 0 / 0 | ok | 1890618 | 0.9993 (0.9977) | -3.24 / 3.19 | 1.0 (4662) | ok |
| v3-C13-llong-s030-codel-r1 | r2->switch-a | target | 1401711 | 0 / 0 (70.09) | 0 / 0 | ok | 859783 | 0.9996 (0.9992) | -3.77 / 3.75 | 1.0 (4715) | ok |
| v3-C13-llong-s030-codel-r1 | r2->switch-b | target | 1402798 | 0 / 0 (70.14) | 0 / 0 | ok | 857244 | 0.9995 (0.9991) | -3.77 / 3.72 | 1.0 (4778) | ok |
| v3-C13-llong-s030-codel-r2 | pub->r1 | info | 854200 | 0 / 0 (42.71) | 0 / 0 | ok | 303794 | 0.9991 (0.6271) | -9.44 / 3.8 | nan (0) | ok |
| v3-C13-llong-s030-codel-r2 | r1->sub-ctrl | info | 112917 | 0 / 0 (5.65) | 0 / 0 | ok | 77562 | 0.9109 (0.9108) | -200.01 / 2.32 | nan (0) | FAIL |
| v3-C13-llong-s030-codel-r2 | r1->r2 | target | 2859913 | 0 / 0 (143) | 0 / 0 | ok | 1858777 | 0.9993 (0.9978) | -3.3 / 3.25 | 1.0 (4581) | ok |
| v3-C13-llong-s030-codel-r2 | r2->switch-a | target | 1420953 | 0 / 0 (71.05) | 0 / 0 | ok | 870137 | 0.9996 (0.9992) | -3.75 / 3.72 | 1.0 (4711) | ok |
| v3-C13-llong-s030-codel-r2 | r2->switch-b | target | 1414906 | 0 / 0 (70.75) | 0 / 0 | ok | 859640 | 0.9996 (0.9992) | -3.73 / 3.7 | 1.0 (4656) | ok |
| v3-C13-llong-s030-pfifo-r1 | pub->r1 | info | 879047 | 0 / 0 (43.95) | 0 / 0 | ok | 386922 | 0.9990 (0.6774) | -9.38 / 4.26 | nan (0) | ok |
| v3-C13-llong-s030-pfifo-r1 | r1->sub-ctrl | info | 112146 | 0 / 0 (5.61) | 0 / 0 | ok | 78506 | 0.9018 (0.9017) | -200.68 / 1.95 | nan (0) | FAIL |
| v3-C13-llong-s030-pfifo-r1 | r1->r2 | target | 2869052 | 0 / 0 (143.45) | 0 / 0 | ok | 1912598 | 0.9993 (0.9977) | -2.15 / 2.16 | 1.0 (4685) | ok |
| v3-C13-llong-s030-pfifo-r1 | r2->switch-a | target | 1397008 | 0 / 1 (69.85) | 0 / 0 | FAIL | 851308 | 0.9995 (0.9992) | -2.2 / 2.21 | 1.0 (4709) | ok |
| v3-C13-llong-s030-pfifo-r1 | r2->switch-b | target | 1397896 | 0 / 0 (69.89) | 0 / 0 | ok | 849666 | 0.9996 (0.9993) | -2.21 / 2.21 | 1.0 (4678) | ok |
| v3-C13-llong-s030-pfifo-r2 | pub->r1 | info | 852216 | 0 / 0 (42.61) | 0 / 0 | ok | 331434 | 0.9993 (0.6284) | -9.46 / 4.05 | nan (0) | ok |
| v3-C13-llong-s030-pfifo-r2 | r1->sub-ctrl | info | 112847 | 0 / 0 (5.64) | 0 / 0 | ok | 78004 | 0.9016 (0.9016) | -200.44 / 2.04 | nan (0) | FAIL |
| v3-C13-llong-s030-pfifo-r2 | r1->r2 | target | 2864536 | 1 / 0 (143.23) | 1 / 0 | ok | 1859482 | 0.9993 (0.9978) | -2.14 / 2.15 | 1.0 (4532) | ok |
| v3-C13-llong-s030-pfifo-r2 | r2->switch-a | target | 1408877 | 0 / 0 (70.44) | 0 / 0 | ok | 850307 | 0.9996 (0.9993) | -2.21 / 2.21 | 1.0 (4660) | ok |
| v3-C13-llong-s030-pfifo-r2 | r2->switch-b | target | 1406296 | 0 / 0 (70.31) | 0 / 0 | ok | 850196 | 0.9996 (0.9994) | -2.21 / 2.22 | 1.0 (4660) | ok |
| v3-C14-rrev-rev-fq_codel-r1 | pub->r0 | info | 460841 | 0 / 0 (23.04) | 0 / 0 | ok | 242892 | 0.9959 (0.4885) | -9.62 / 8.07 | nan (0) | ok |
| v3-C14-rrev-rev-fq_codel-r1 | r0->sub-ctrl | info | 87281 | 0 / 0 (4.36) | 0 / 0 | ok | 54641 | 0.8425 (0.8425) | -199.81 / 1.98 | nan (0) | FAIL |
| v3-C14-rrev-rev-fq_codel-r1 | r0->r1 | info | 373570 | 0 / 0 (18.68) | 0 / 0 | ok | 219349 | 0.9993 (0.9973) | -2.83 / 2.79 | nan (0) | ok |
| v3-C14-rrev-rev-fq_codel-r1 | r1->switch | target | 1296234 | 0 / 0 (64.81) | 0 / 0 | ok | 703406 | 0.9992 (0.9986) | -3.82 / 3.91 | 1.0 (281) | ok |
| v3-C14-rrev-rev-fq_codel-r2 | pub->r0 | info | 478965 | 0 / 0 (23.95) | 0 / 0 | ok | 243140 | 0.9944 (0.5156) | -9.57 / 9.8 | nan (0) | ok |
| v3-C14-rrev-rev-fq_codel-r2 | r0->sub-ctrl | info | 91787 | 0 / 0 (4.59) | 0 / 0 | ok | 58516 | 0.8811 (0.8811) | -200.09 / 2.1 | nan (0) | FAIL |
| v3-C14-rrev-rev-fq_codel-r2 | r0->r1 | info | 387194 | 0 / 0 (19.36) | 0 / 0 | ok | 225437 | 0.9993 (0.9976) | -2.56 / 2.54 | nan (0) | ok |
| v3-C14-rrev-rev-fq_codel-r2 | r1->switch | target | 1351179 | 0 / 0 (67.56) | 0 / 0 | ok | 724711 | 0.9994 (0.9989) | -3.54 / 3.61 | 1.0 (356) | ok |
| v3-C14-rrev-rev-pfifo-r1 | pub->r0 | info | 468675 | 0 / 0 (23.43) | 0 / 0 | ok | 217994 | 0.9980 (0.5653) | -9.63 / 4.76 | nan (0) | ok |
| v3-C14-rrev-rev-pfifo-r1 | r0->sub-ctrl | info | 87797 | 0 / 0 (4.39) | 0 / 0 | ok | 62643 | 0.8994 (0.8994) | -200.42 / 2.06 | nan (0) | FAIL |
| v3-C14-rrev-rev-pfifo-r1 | r0->r1 | info | 380890 | 0 / 0 (19.04) | 0 / 0 | ok | 217709 | 0.9996 (0.9986) | -2.38 / 2.36 | nan (0) | ok |
| v3-C14-rrev-rev-pfifo-r1 | r1->switch | target | 1290385 | 0 / 0 (64.52) | 0 / 0 | ok | 860300 | 0.9997 (0.9994) | -2.02 / 2.03 | 1.0 (3379) | ok |
| v3-C14-rrev-rev-pfifo-r2 | pub->r0 | info | 484502 | 0 / 0 (24.23) | 0 / 0 | ok | 239762 | 0.9981 (0.6088) | -9.59 / 4.89 | nan (0) | ok |
| v3-C14-rrev-rev-pfifo-r2 | r0->sub-ctrl | info | 91646 | 0 / 0 (4.58) | 0 / 0 | ok | 56303 | 0.8847 (0.8847) | -200.57 / 1.73 | nan (0) | FAIL |
| v3-C14-rrev-rev-pfifo-r2 | r0->r1 | info | 392879 | 0 / 0 (19.64) | 0 / 0 | ok | 228112 | 0.9996 (0.9987) | -2.35 / 2.25 | nan (0) | ok |
| v3-C14-rrev-rev-pfifo-r2 | r1->switch | target | 1349048 | 0 / 0 (67.45) | 0 / 0 | ok | 893970 | 0.9997 (0.9994) | -2.04 / 2.06 | 1.0 (3417) | ok |
| v3-C15-nloss-s030u070-codel-r1 | pub->router | info | 326187 | 0 / 0 (16.31) | 0 / 0 | ok | 180287 | 0.9999 (0.8679) | -9.4 / 1.71 | nan (0) | ok |
| v3-C15-nloss-s030u070-codel-r1 | router->sub-ctrl | info | 60879 | 0 / 0 (3.04) | 0 / 0 | ok | 31492 | 0.8801 (0.8799) | -201.56 / 1.35 | nan (0) | FAIL |
| v3-C15-nloss-s030u070-codel-r1 | router->switch | target | 839531 | 0 / 0 (41.98) | 0 / 0 | ok | 487330 | 0.9998 (0.9996) | -1.57 / 1.61 | 1.0 (692) | ok |
| v3-C15-nloss-s030u070-codel-r2 | pub->router | info | 322640 | 0 / 0 (16.13) | 0 / 0 | ok | 150552 | 0.9999 (0.8334) | -9.37 / 1.71 | nan (0) | ok |
| v3-C15-nloss-s030u070-codel-r2 | router->sub-ctrl | info | 60296 | 0 / 0 (3.01) | 0 / 0 | ok | 40178 | 0.8838 (0.8837) | -200.98 / 1.62 | nan (0) | FAIL |
| v3-C15-nloss-s030u070-codel-r2 | router->switch | target | 832754 | 0 / 0 (41.64) | 0 / 0 | ok | 482538 | 0.9998 (0.9995) | -1.66 / 1.69 | 1.0 (651) | ok |
| v3-C15-nloss-s030u070-pfifo-r1 | pub->router | info | 326207 | 0 / 0 (16.31) | 0 / 0 | ok | 176656 | 0.9999 (0.8658) | -9.32 / 1.63 | nan (0) | ok |
| v3-C15-nloss-s030u070-pfifo-r1 | router->sub-ctrl | info | 60801 | 0 / 0 (3.04) | 0 / 0 | ok | 29167 | 0.8935 (0.8935) | -201.71 / 1.54 | nan (0) | FAIL |
| v3-C15-nloss-s030u070-pfifo-r1 | router->switch | target | 839623 | 0 / 0 (41.98) | 0 / 0 | ok | 487199 | 0.9998 (0.9996) | -1.56 / 1.59 | 1.0 (682) | ok |
| v3-C15-nloss-s030u070-pfifo-r2 | pub->router | info | 323319 | 0 / 0 (16.17) | 0 / 0 | ok | 174872 | 0.9999 (0.8743) | -9.25 / 1.61 | nan (0) | ok |
| v3-C15-nloss-s030u070-pfifo-r2 | router->sub-ctrl | info | 60248 | 0 / 0 (3.01) | 0 / 0 | ok | 41298 | 0.9000 (0.9000) | -201.03 / 1.46 | nan (0) | FAIL |
| v3-C15-nloss-s030u070-pfifo-r2 | router->switch | target | 833490 | 0 / 0 (41.67) | 0 / 0 | ok | 485182 | 0.9998 (0.9996) | -1.49 / 1.52 | 1.0 (684) | ok |
| v3-C1a-calm-legacy-codel-r1 | pub->router | info | 181883 | 0 / 0 (9.09) | 0 / 0 | ok | 99523 | 0.9998 (0.8795) | -9.45 / 1.44 | nan (0) | ok |
| v3-C1a-calm-legacy-codel-r1 | router->sub-ctrl | info | 33972 | 1 / 0 (3) | 1 / 0 | ok | 18183 | 0.8549 (0.8548) | -201.83 / 1.12 | nan (0) | FAIL |
| v3-C1a-calm-legacy-codel-r1 | router->switch | target | 147818 | 0 / 0 (7.39) | 0 / 0 | ok | 135542 | 1.0000 (1.0000) | -1.98 / 2.37 | 1.0 (1815) | ok |
| v3-C1a-calm-legacy-codel-r2 | pub->router | info | 181633 | 0 / 0 (9.08) | 0 / 0 | ok | 117847 | 0.9998 (0.8903) | -9.47 / 1.66 | nan (0) | ok |
| v3-C1a-calm-legacy-codel-r2 | router->sub-ctrl | info | 33791 | 0 / 0 (3) | 0 / 0 | ok | 22268 | 0.9314 (0.9314) | -200.31 / 1.44 | nan (0) | FAIL |
| v3-C1a-calm-legacy-codel-r2 | router->switch | target | 147760 | 0 / 0 (7.39) | 0 / 0 | ok | 135151 | 1.0000 (0.9999) | -2.16 / 2.33 | 1.0 (1830) | ok |
| v3-C1a-calm-legacy-pfifo-r1 | pub->router | info | 181934 | 0 / 0 (9.1) | 0 / 0 | ok | 81464 | 0.9997 (0.8122) | -9.59 / 1.83 | nan (0) | ok |
| v3-C1a-calm-legacy-pfifo-r1 | router->sub-ctrl | info | 34016 | 1 / 0 (3) | 1 / 0 | ok | 19159 | 0.9090 (0.9088) | -201.37 / 1.35 | nan (0) | FAIL |
| v3-C1a-calm-legacy-pfifo-r1 | router->switch | target | 147169 | 0 / 0 (7.36) | 0 / 0 | ok | 134707 | 1.0000 (0.9999) | -2.1 / 2.17 | 1.0 (1775) | ok |
| v3-C1a-calm-legacy-pfifo-r2 | pub->router | info | 180841 | 0 / 0 (9.04) | 0 / 0 | ok | 75669 | 0.9991 (0.7971) | -9.62 / 1.8 | nan (0) | ok |
| v3-C1a-calm-legacy-pfifo-r2 | router->sub-ctrl | info | 33715 | 0 / 0 (3) | 0 / 0 | ok | 15657 | 0.8106 (0.8106) | -201.84 / 1.55 | nan (0) | FAIL |
| v3-C1a-calm-legacy-pfifo-r2 | router->switch | target | 146520 | 0 / 0 (7.33) | 0 / 0 | ok | 134340 | 1.0000 (1.0000) | -2.05 / 2.27 | 1.0 (1794) | ok |
| v3-C1a-calm-s010u070-codel-r1 | pub->router | info | 107687 | 0 / 0 (5.38) | 0 / 0 | ok | 51193 | 0.9999 (0.8221) | -9.65 / 1.99 | nan (0) | ok |
| v3-C1a-calm-s010u070-codel-r1 | router->sub-ctrl | info | 33971 | 0 / 0 (3) | 0 / 0 | ok | 22576 | 0.9108 (0.9108) | -201.35 / 1.37 | nan (0) | FAIL |
| v3-C1a-calm-s010u070-codel-r1 | router->switch | target | 632759 | 0 / 0 (31.64) | 0 / 0 | ok | 213975 | 0.9997 (0.9992) | -1.46 / 1.43 | 1.0 (96) | ok |
| v3-C1a-calm-s010u070-codel-r2 | pub->router | info | 107000 | 0 / 0 (5.35) | 0 / 0 | ok | 36922 | 0.9997 (0.7157) | -9.79 / 2.32 | nan (0) | ok |
| v3-C1a-calm-s010u070-codel-r2 | router->sub-ctrl | info | 33697 | 0 / 0 (3) | 0 / 0 | ok | 18214 | 0.8117 (0.8116) | -202.05 / 1.14 | nan (0) | FAIL |
| v3-C1a-calm-s010u070-codel-r2 | router->switch | target | 633712 | 0 / 0 (31.69) | 0 / 0 | ok | 215847 | 0.9996 (0.9992) | -1.46 / 1.46 | 1.0 (98) | ok |
| v3-C1a-calm-s010u070-pfifo-r1 | pub->router | info | 107591 | 0 / 0 (5.38) | 0 / 0 | ok | 40498 | 0.9997 (0.7428) | -9.68 / 2.38 | nan (0) | ok |
| v3-C1a-calm-s010u070-pfifo-r1 | router->sub-ctrl | info | 33915 | 1 / 0 (3) | 1 / 0 | ok | 19944 | 0.8407 (0.8407) | -201.46 / 1.24 | nan (0) | FAIL |
| v3-C1a-calm-s010u070-pfifo-r1 | router->switch | target | 632726 | 0 / 0 (31.64) | 0 / 0 | ok | 214406 | 0.9996 (0.9990) | -1.51 / 1.52 | 1.0 (100) | ok |
| v3-C1a-calm-s010u070-pfifo-r2 | pub->router | info | 107343 | 0 / 0 (5.37) | 0 / 0 | ok | 50735 | 0.9998 (0.8492) | -9.39 / 1.83 | nan (0) | ok |
| v3-C1a-calm-s010u070-pfifo-r2 | router->sub-ctrl | info | 33849 | 0 / 0 (3) | 0 / 0 | ok | 21950 | 0.9314 (0.9314) | -200.68 / 1.69 | 1.0 (1) | FAIL |
| v3-C1a-calm-s010u070-pfifo-r2 | router->switch | target | 633908 | 0 / 0 (31.7) | 0 / 0 | ok | 215134 | 0.9996 (0.9992) | -1.43 / 1.43 | 1.0 (99) | ok |
| v3-C1a-calm-s010u085-codel-r1 | pub->router | info | 107642 | 0 / 0 (5.38) | 0 / 0 | ok | 46263 | 0.9999 (0.8371) | -9.51 / 1.69 | nan (0) | ok |
| v3-C1a-calm-s010u085-codel-r1 | router->sub-ctrl | info | 33934 | 1 / 0 (3) | 1 / 0 | ok | 18792 | 0.8413 (0.8412) | -201.53 / 1.6 | nan (0) | FAIL |
| v3-C1a-calm-s010u085-codel-r1 | router->switch | target | 632752 | 0 / 0 (31.64) | 0 / 0 | ok | 361123 | 0.9998 (0.9995) | -1.36 / 1.42 | 1.0 (571) | ok |
| v3-C1a-calm-s010u085-codel-r2 | pub->router | info | 107375 | 0 / 0 (5.37) | 0 / 0 | ok | 44114 | 0.9998 (0.7960) | -9.53 / 1.91 | nan (0) | ok |
| v3-C1a-calm-s010u085-codel-r2 | router->sub-ctrl | info | 33793 | 0 / 0 (3) | 0 / 0 | ok | 20026 | 0.8533 (0.8532) | -201.37 / 1.24 | nan (0) | FAIL |
| v3-C1a-calm-s010u085-codel-r2 | router->switch | target | 634007 | 0 / 0 (31.7) | 0 / 0 | ok | 364754 | 0.9998 (0.9995) | -1.4 / 1.44 | 1.0 (586) | ok |
| v3-C1a-calm-s010u085-pfifo-r1 | pub->router | info | 107503 | 0 / 0 (5.38) | 0 / 0 | ok | 48878 | 0.9999 (0.8296) | -9.58 / 1.92 | nan (0) | ok |
| v3-C1a-calm-s010u085-pfifo-r1 | router->sub-ctrl | info | 33852 | 1 / 0 (3) | 1 / 0 | ok | 16502 | 0.8648 (0.8647) | -201.79 / 1.29 | nan (0) | FAIL |
| v3-C1a-calm-s010u085-pfifo-r1 | router->switch | target | 632705 | 0 / 0 (31.64) | 0 / 0 | ok | 362274 | 0.9998 (0.9995) | -1.34 / 1.36 | 1.0 (569) | ok |
| v3-C1a-calm-s010u085-pfifo-r2 | pub->router | info | 107181 | 0 / 0 (5.36) | 0 / 0 | ok | 45725 | 0.9999 (0.8573) | -9.36 / 1.58 | nan (0) | ok |
| v3-C1a-calm-s010u085-pfifo-r2 | router->sub-ctrl | info | 33771 | 0 / 0 (3) | 0 / 0 | ok | 18119 | 0.9041 (0.9041) | -201.07 / 1.64 | nan (0) | FAIL |
| v3-C1a-calm-s010u085-pfifo-r2 | router->switch | target | 633821 | 0 / 0 (31.69) | 0 / 0 | ok | 363615 | 0.9998 (0.9996) | -1.32 / 1.36 | 1.0 (577) | ok |
| v3-C1a-calm-s030u050-codel-r1 | pub->router | info | 182100 | 0 / 0 (9.11) | 0 / 0 | ok | 116640 | 0.9999 (0.8731) | -9.33 / 1.78 | nan (0) | ok |
| v3-C1a-calm-s030u050-codel-r1 | router->sub-ctrl | info | 33926 | 1 / 0 (3) | 1 / 0 | ok | 18521 | 0.8333 (0.8330) | -202.02 / 1.22 | nan (0) | FAIL |
| v3-C1a-calm-s030u050-codel-r1 | router->switch | target | 467266 | 0 / 0 (23.36) | 0 / 0 | ok | 207430 | 0.9997 (0.9993) | -1.61 / 1.65 | 1.0 (135) | ok |
| v3-C1a-calm-s030u050-codel-r2 | pub->router | info | 181291 | 0 / 0 (9.06) | 0 / 0 | ok | 123806 | 0.9998 (0.8881) | -9.27 / 1.78 | nan (0) | ok |
| v3-C1a-calm-s030u050-codel-r2 | router->sub-ctrl | info | 33714 | 0 / 0 (3) | 0 / 0 | ok | 15673 | 0.8770 (0.8770) | -202.0 / 1.39 | nan (0) | FAIL |
| v3-C1a-calm-s030u050-codel-r2 | router->switch | target | 467423 | 0 / 0 (23.37) | 0 / 0 | ok | 207418 | 0.9997 (0.9993) | -1.61 / 1.62 | 1.0 (136) | ok |
| v3-C1a-calm-s030u050-pfifo-r1 | pub->router | info | 182128 | 0 / 0 (9.11) | 0 / 0 | ok | 122839 | 0.9999 (0.8859) | -9.22 / 1.79 | nan (0) | ok |
| v3-C1a-calm-s030u050-pfifo-r1 | router->sub-ctrl | info | 33962 | 1 / 0 (3) | 1 / 0 | ok | 22123 | 0.9277 (0.9277) | -200.99 / 1.3 | nan (0) | FAIL |
| v3-C1a-calm-s030u050-pfifo-r1 | router->switch | target | 467273 | 0 / 0 (23.36) | 0 / 0 | ok | 208646 | 0.9998 (0.9994) | -1.56 / 1.59 | 1.0 (140) | ok |
| v3-C1a-calm-s030u050-pfifo-r2 | pub->router | info | 181726 | 0 / 0 (9.09) | 0 / 0 | ok | 121998 | 0.9999 (0.8683) | -9.27 / 1.9 | nan (0) | ok |
| v3-C1a-calm-s030u050-pfifo-r2 | router->sub-ctrl | info | 33788 | 0 / 0 (3) | 0 / 0 | ok | 19464 | 0.8477 (0.8477) | -201.74 / 1.31 | nan (0) | FAIL |
| v3-C1a-calm-s030u050-pfifo-r2 | router->switch | target | 467791 | 0 / 0 (23.39) | 0 / 0 | ok | 208999 | 0.9997 (0.9993) | -1.59 / 1.59 | 1.0 (136) | ok |
| v3-C1a-calm-s030u070-codel-r1 | pub->router | info | 181964 | 0 / 0 (9.1) | 0 / 0 | ok | 129145 | 1.0000 (0.9041) | -9.17 / 1.68 | nan (0) | ok |
| v3-C1a-calm-s030u070-codel-r1 | router->sub-ctrl | info | 33945 | 1 / 0 (3) | 1 / 0 | ok | 21532 | 0.9499 (0.9499) | -200.11 / 1.4 | nan (0) | FAIL |
| v3-C1a-calm-s030u070-codel-r1 | router->switch | target | 467110 | 0 / 0 (23.36) | 0 / 0 | ok | 272791 | 0.9998 (0.9996) | -1.51 / 1.57 | 1.0 (411) | ok |
| v3-C1a-calm-s030u070-codel-r2 | pub->router | info | 181422 | 0 / 0 (9.07) | 0 / 0 | ok | 107553 | 0.9999 (0.8872) | -9.27 / 1.6 | nan (0) | ok |
| v3-C1a-calm-s030u070-codel-r2 | router->sub-ctrl | info | 33772 | 1 / 0 (3) | 1 / 0 | ok | 18511 | 0.8654 (0.8652) | -201.27 / 1.74 | nan (0) | FAIL |
| v3-C1a-calm-s030u070-codel-r2 | router->switch | target | 467503 | 0 / 0 (23.38) | 0 / 0 | ok | 272828 | 0.9998 (0.9996) | -1.53 / 1.56 | 1.0 (398) | ok |
| v3-C1a-calm-s030u070-pfifo-r1 | pub->router | info | 181884 | 0 / 0 (9.09) | 0 / 0 | ok | 104359 | 0.9998 (0.8699) | -9.38 / 1.72 | nan (0) | ok |
| v3-C1a-calm-s030u070-pfifo-r1 | router->sub-ctrl | info | 33830 | 0 / 0 (3) | 0 / 0 | ok | 15464 | 0.8191 (0.8190) | -201.8 / 1.65 | nan (0) | FAIL |
| v3-C1a-calm-s030u070-pfifo-r1 | router->switch | target | 467155 | 0 / 0 (23.36) | 0 / 0 | ok | 272466 | 0.9998 (0.9996) | -1.58 / 1.59 | 1.0 (403) | ok |
| v3-C1a-calm-s030u070-pfifo-r2 | pub->router | info | 181411 | 0 / 0 (9.07) | 0 / 0 | ok | 111786 | 0.9999 (0.8929) | -9.24 / 1.65 | nan (0) | ok |
| v3-C1a-calm-s030u070-pfifo-r2 | router->sub-ctrl | info | 33824 | 0 / 0 (3) | 0 / 0 | ok | 18248 | 0.9187 (0.9186) | -201.1 / 1.64 | nan (0) | FAIL |
| v3-C1a-calm-s030u070-pfifo-r2 | router->switch | target | 467427 | 0 / 0 (23.37) | 0 / 0 | ok | 273531 | 0.9998 (0.9996) | -1.49 / 1.53 | 1.0 (407) | ok |
| v3-C1a-calm-s030u085-codel-r1 | pub->router | info | 182062 | 0 / 0 (9.1) | 0 / 0 | ok | 125348 | 1.0000 (0.9099) | -9.16 / 1.58 | nan (0) | ok |
| v3-C1a-calm-s030u085-codel-r1 | router->sub-ctrl | info | 33912 | 1 / 0 (3) | 1 / 0 | ok | 21501 | 0.9481 (0.9481) | -200.39 / 1.34 | nan (0) | FAIL |
| v3-C1a-calm-s030u085-codel-r1 | router->switch | target | 467173 | 0 / 0 (23.36) | 0 / 0 | ok | 348318 | 0.9999 (0.9997) | -1.54 / 1.58 | 1.0 (1919) | ok |
| v3-C1a-calm-s030u085-codel-r2 | pub->router | info | 181395 | 0 / 0 (9.07) | 0 / 0 | ok | 119250 | 0.9998 (0.8808) | -9.29 / 1.97 | nan (0) | ok |
| v3-C1a-calm-s030u085-codel-r2 | router->sub-ctrl | info | 33798 | 1 / 0 (3) | 1 / 0 | ok | 18242 | 0.9095 (0.9095) | -201.58 / 1.44 | nan (0) | FAIL |
| v3-C1a-calm-s030u085-codel-r2 | router->switch | target | 467369 | 0 / 0 (23.37) | 0 / 0 | ok | 350481 | 0.9999 (0.9997) | -1.61 / 1.66 | 1.0 (1947) | ok |
| v3-C1a-calm-s030u085-pfifo-r1 | pub->router | info | 182003 | 0 / 0 (9.1) | 0 / 0 | ok | 109625 | 0.9999 (0.8847) | -9.3 / 1.76 | nan (0) | ok |
| v3-C1a-calm-s030u085-pfifo-r1 | router->sub-ctrl | info | 33937 | 0 / 0 (3) | 0 / 0 | ok | 20037 | 0.9315 (0.9314) | -200.66 / 1.6 | nan (0) | FAIL |
| v3-C1a-calm-s030u085-pfifo-r1 | router->switch | target | 467157 | 0 / 0 (23.36) | 0 / 0 | ok | 348922 | 0.9999 (0.9998) | -1.54 / 1.59 | 1.0 (1927) | ok |
| v3-C1a-calm-s030u085-pfifo-r2 | pub->router | info | 181542 | 0 / 0 (9.08) | 0 / 0 | ok | 125939 | 0.9999 (0.8930) | -9.22 / 1.84 | nan (0) | ok |
| v3-C1a-calm-s030u085-pfifo-r2 | router->sub-ctrl | info | 33857 | 0 / 0 (3) | 0 / 0 | ok | 21297 | 0.9485 (0.9485) | -200.31 / 1.54 | nan (0) | FAIL |
| v3-C1a-calm-s030u085-pfifo-r2 | router->switch | target | 467547 | 0 / 0 (23.38) | 0 / 0 | ok | 349814 | 0.9999 (0.9997) | -1.54 / 1.57 | 1.0 (1949) | ok |
| v3-C1a-calm-s065u050-codel-r1 | pub->router | info | 182027 | 0 / 0 (9.1) | 0 / 0 | ok | 123340 | 0.9998 (0.8882) | -9.38 / 1.69 | nan (0) | ok |
| v3-C1a-calm-s065u050-codel-r1 | router->sub-ctrl | info | 34048 | 0 / 0 (3) | 0 / 0 | ok | 20005 | 0.9108 (0.9107) | -200.97 / 1.22 | nan (0) | FAIL |
| v3-C1a-calm-s065u050-codel-r1 | router->switch | target | 221886 | 0 / 0 (11.09) | 0 / 0 | ok | 162952 | 0.9999 (0.9998) | -1.66 / 1.75 | 1.0 (353) | ok |
| v3-C1a-calm-s065u050-codel-r2 | pub->router | info | 181263 | 0 / 0 (9.06) | 0 / 0 | ok | 122498 | 0.9999 (0.8805) | -9.32 / 1.75 | nan (0) | ok |
| v3-C1a-calm-s065u050-codel-r2 | router->sub-ctrl | info | 33747 | 1 / 0 (3) | 1 / 0 | ok | 22198 | 0.8808 (0.8807) | -201.26 / 1.39 | nan (0) | FAIL |
| v3-C1a-calm-s065u050-codel-r2 | router->switch | target | 221504 | 0 / 0 (11.08) | 0 / 0 | ok | 162379 | 0.9999 (0.9997) | -1.87 / 1.93 | 1.0 (344) | ok |
| v3-C1a-calm-s065u050-pfifo-r1 | pub->router | info | 182252 | 0 / 0 (9.11) | 0 / 0 | ok | 114442 | 0.9999 (0.9035) | -9.22 / 1.47 | nan (0) | ok |
| v3-C1a-calm-s065u050-pfifo-r1 | router->sub-ctrl | info | 33956 | 1 / 0 (3) | 1 / 0 | ok | 18387 | 0.9180 (0.9180) | -201.03 / 1.51 | nan (0) | FAIL |
| v3-C1a-calm-s065u050-pfifo-r1 | router->switch | target | 222003 | 0 / 0 (11.1) | 0 / 0 | ok | 162531 | 0.9999 (0.9998) | -1.61 / 1.65 | 1.0 (345) | ok |
| v3-C1a-calm-s065u050-pfifo-r2 | pub->router | info | 181455 | 0 / 0 (9.07) | 0 / 0 | ok | 100489 | 0.9998 (0.8780) | -9.37 / 1.5 | nan (0) | ok |
| v3-C1a-calm-s065u050-pfifo-r2 | router->sub-ctrl | info | 33825 | 1 / 0 (3) | 1 / 0 | ok | 20586 | 0.8881 (0.8879) | -201.26 / 1.73 | nan (0) | FAIL |
| v3-C1a-calm-s065u050-pfifo-r2 | router->switch | target | 221526 | 0 / 0 (11.08) | 0 / 0 | ok | 162203 | 0.9998 (0.9997) | -1.65 / 1.71 | 1.0 (339) | ok |
| v3-C1a-calm-s065u070-codel-r1 | pub->router | info | 181874 | 0 / 0 (9.09) | 0 / 0 | ok | 111282 | 0.9999 (0.8960) | -9.24 / 1.44 | nan (0) | ok |
| v3-C1a-calm-s065u070-codel-r1 | router->sub-ctrl | info | 33902 | 0 / 0 (3) | 0 / 0 | ok | 22097 | 0.8937 (0.8937) | -201.0 / 1.57 | nan (0) | FAIL |
| v3-C1a-calm-s065u070-codel-r1 | router->switch | target | 221776 | 0 / 0 (11.09) | 0 / 0 | ok | 179626 | 0.9999 (0.9999) | -1.91 / 2.05 | 1.0 (1357) | ok |
| v3-C1a-calm-s065u070-codel-r2 | pub->router | info | 181527 | 0 / 0 (9.08) | 0 / 0 | ok | 116724 | 0.9999 (0.9047) | -9.26 / 1.53 | nan (0) | ok |
| v3-C1a-calm-s065u070-codel-r2 | router->sub-ctrl | info | 33855 | 1 / 0 (3) | 1 / 0 | ok | 16238 | 0.9156 (0.9156) | -201.47 / 1.29 | nan (0) | FAIL |
| v3-C1a-calm-s065u070-codel-r2 | router->switch | target | 221570 | 0 / 0 (11.08) | 0 / 0 | ok | 179148 | 0.9999 (0.9998) | -1.83 / 1.91 | 1.0 (1364) | ok |
| v3-C1a-calm-s065u070-pfifo-r1 | pub->router | info | 181516 | 0 / 0 (9.08) | 0 / 0 | ok | 79390 | 0.9999 (0.8314) | -9.47 / 1.55 | nan (0) | ok |
| v3-C1a-calm-s065u070-pfifo-r1 | router->sub-ctrl | info | 33855 | 0 / 0 (3) | 0 / 0 | ok | 19860 | 0.8851 (0.8851) | -200.76 / 1.82 | nan (0) | FAIL |
| v3-C1a-calm-s065u070-pfifo-r1 | router->switch | target | 220972 | 0 / 0 (11.05) | 0 / 0 | ok | 178876 | 0.9999 (0.9999) | -1.78 / 1.93 | 1.0 (1329) | ok |
| v3-C1a-calm-s065u070-pfifo-r2 | pub->router | info | 180658 | 0 / 0 (9.03) | 0 / 0 | ok | 78369 | 0.9999 (0.8494) | -9.47 / 1.5 | nan (0) | ok |
| v3-C1a-calm-s065u070-pfifo-r2 | router->sub-ctrl | info | 33742 | 1 / 0 (3) | 1 / 0 | ok | 15561 | 0.8696 (0.8696) | -201.85 / 1.77 | nan (0) | FAIL |
| v3-C1a-calm-s065u070-pfifo-r2 | router->switch | target | 220547 | 0 / 0 (11.03) | 0 / 0 | ok | 179013 | 0.9999 (0.9998) | -1.79 / 1.91 | 1.0 (1359) | ok |
| v3-C1a-calm-s065u085-codel-r1 | pub->router | info | 181651 | 0 / 0 (9.08) | 0 / 0 | ok | 98845 | 0.9998 (0.8554) | -9.39 / 1.66 | nan (0) | ok |
| v3-C1a-calm-s065u085-codel-r1 | router->sub-ctrl | info | 33927 | 1 / 0 (3) | 1 / 0 | ok | 19092 | 0.8566 (0.8566) | -201.67 / 1.4 | nan (0) | FAIL |
| v3-C1a-calm-s065u085-codel-r1 | router->switch | target | 221117 | 0 / 0 (11.06) | 0 / 0 | ok | 196216 | 0.9999 (0.9999) | -2.22 / 2.31 | 1.0 (3588) | ok |
| v3-C1a-calm-s065u085-codel-r2 | pub->router | info | 181378 | 0 / 0 (9.07) | 0 / 0 | ok | 100012 | 0.9999 (0.8903) | -9.26 / 1.46 | nan (0) | ok |
| v3-C1a-calm-s065u085-codel-r2 | router->sub-ctrl | info | 33783 | 0 / 0 (3) | 0 / 0 | ok | 21664 | 0.8901 (0.8900) | -201.15 / 1.81 | nan (0) | FAIL |
| v3-C1a-calm-s065u085-codel-r2 | router->switch | target | 221081 | 0 / 0 (11.05) | 0 / 0 | ok | 195905 | 0.9999 (0.9999) | -2.25 / 2.39 | 1.0 (3548) | ok |
| v3-C1a-calm-s065u085-pfifo-r1 | pub->router | info | 179609 | 0 / 0 (8.98) | 0 / 0 | ok | 53563 | 0.9997 (0.7176) | -9.69 / 1.81 | nan (0) | ok |
| v3-C1a-calm-s065u085-pfifo-r1 | router->sub-ctrl | info | 33840 | 1 / 0 (3) | 1 / 0 | ok | 16372 | 0.8199 (0.8197) | -201.95 / 1.3 | nan (0) | FAIL |
| v3-C1a-calm-s065u085-pfifo-r1 | router->switch | target | 219194 | 0 / 0 (10.96) | 0 / 0 | ok | 193983 | 1.0000 (0.9999) | -2.03 / 2.11 | 1.0 (3539) | ok |
| v3-C1a-calm-s065u085-pfifo-r2 | pub->router | info | 179097 | 0 / 0 (8.95) | 0 / 0 | ok | 63829 | 0.9997 (0.7370) | -9.65 / 2.03 | nan (0) | ok |
| v3-C1a-calm-s065u085-pfifo-r2 | router->sub-ctrl | info | 33795 | 1 / 0 (3) | 1 / 0 | ok | 22306 | 0.8774 (0.8773) | -201.44 / 1.34 | nan (0) | FAIL |
| v3-C1a-calm-s065u085-pfifo-r2 | router->switch | target | 218822 | 0 / 0 (10.94) | 0 / 0 | ok | 193355 | 0.9999 (0.9999) | -1.95 / 2.0 | 1.0 (3498) | ok |
| v3-C1b-calm-split4-pfifo-r1 | pub->r1 | info | 292681 | 0 / 0 (14.63) | 0 / 0 | ok | 198240 | 0.9996 (0.8063) | -8.93 / 3.57 | nan (0) | ok |
| v3-C1b-calm-split4-pfifo-r1 | r1->sub-ctrl | info | 33986 | 0 / 0 (3) | 0 / 0 | ok | 18420 | 0.8922 (0.8920) | -201.07 / 1.88 | nan (0) | FAIL |
| v3-C1b-calm-split4-pfifo-r1 | r1->r2 | target | 809355 | 1 / 0 (40.47) | 1 / 0 | ok | 481800 | 0.9995 (0.9976) | -2.36 / 2.36 | 1.0 (384) | ok |
| v3-C1b-calm-split4-pfifo-r1 | r2->switch-a | target | 405878 | 0 / 0 (20.29) | 0 / 0 | ok | 228627 | 0.9996 (0.9992) | -2.35 / 2.36 | 1.0 (378) | ok |
| v3-C1b-calm-split4-pfifo-r1 | r2->switch-b | target | 405189 | 0 / 0 (20.26) | 0 / 0 | ok | 225646 | 0.9997 (0.9993) | -2.36 / 2.37 | 1.0 (391) | ok |
| v3-C1b-calm-split4-pfifo-r2 | pub->r1 | info | 291730 | 0 / 0 (14.59) | 0 / 0 | ok | 193332 | 0.9994 (0.8035) | -8.92 / 3.58 | nan (0) | ok |
| v3-C1b-calm-split4-pfifo-r2 | r1->sub-ctrl | info | 33757 | 0 / 0 (3) | 0 / 0 | ok | 19418 | 0.8955 (0.8952) | -200.71 / 1.79 | nan (0) | FAIL |
| v3-C1b-calm-split4-pfifo-r2 | r1->r2 | target | 809937 | 0 / 0 (40.5) | 0 / 0 | ok | 483438 | 0.9995 (0.9978) | -2.27 / 2.29 | 1.0 (371) | ok |
| v3-C1b-calm-split4-pfifo-r2 | r2->switch-a | target | 405340 | 0 / 0 (20.27) | 0 / 0 | ok | 224919 | 0.9996 (0.9992) | -2.27 / 2.24 | 1.0 (385) | ok |
| v3-C1b-calm-split4-pfifo-r2 | r2->switch-b | target | 404951 | 0 / 0 (20.25) | 0 / 0 | ok | 224456 | 0.9997 (0.9993) | -2.21 / 2.21 | 1.0 (358) | ok |
| v3-C1b-calm-tree16-pfifo-r1 | pub->rr | info | 328626 | 0 / 0 (16.43) | 0 / 0 | ok | 194247 | 0.9955 (0.6154) | -8.97 / 10.37 | nan (0) | ok |
| v3-C1b-calm-tree16-pfifo-r1 | r0->r1 | target | 438775 | 0 / 0 (21.94) | 0 / 0 | ok | 247285 | 0.9988 (0.9966) | -4.34 / 4.16 | 1.0 (396) | ok |
| v3-C1b-calm-tree16-pfifo-r1 | r0->r2 | target | 437890 | 0 / 0 (21.89) | 0 / 0 | ok | 245209 | 0.9990 (0.9968) | -4.23 / 4.14 | 1.0 (391) | ok |
| v3-C1b-calm-tree16-pfifo-r1 | r1->switch-a | target | 219045 | 0 / 0 (10.95) | 0 / 0 | ok | 102272 | 0.9991 (0.9987) | -4.07 / 3.98 | 1.0 (325) | ok |
| v3-C1b-calm-tree16-pfifo-r1 | r1->switch-b | target | 218617 | 0 / 0 (10.93) | 0 / 0 | ok | 106795 | 0.9992 (0.9987) | -4.15 / 4.05 | 1.0 (358) | ok |
| v3-C1b-calm-tree16-pfifo-r1 | r2->switch-c | target | 219539 | 0 / 0 (10.98) | 0 / 0 | ok | 104288 | 0.9989 (0.9984) | -4.18 / 3.99 | 1.0 (350) | ok |
| v3-C1b-calm-tree16-pfifo-r1 | r2->switch-d | target | 218481 | 0 / 0 (10.92) | 0 / 0 | ok | 105671 | 0.9991 (0.9984) | -4.28 / 4.15 | 1.0 (333) | ok |
| v3-C1b-calm-tree16-pfifo-r1 | rr->sub-ctrl | info | 33851 | 0 / 0 (3) | 0 / 0 | ok | 21686 | 0.9012 (0.9011) | -200.25 / 2.88 | nan (0) | FAIL |
| v3-C1b-calm-tree16-pfifo-r1 | rr->r0 | target | 874426 | 0 / 0 (43.72) | 0 / 0 | ok | 528051 | 0.9981 (0.9898) | -4.42 / 4.4 | 1.0 (384) | ok |
| v3-C1b-calm-tree16-pfifo-r2 | pub->rr | info | 328038 | 0 / 0 (16.4) | 0 / 0 | ok | 193720 | 0.9938 (0.5895) | -9.1 / 11.95 | nan (0) | ok |
| v3-C1b-calm-tree16-pfifo-r2 | r0->r1 | target | 437796 | 0 / 0 (21.89) | 0 / 0 | ok | 244548 | 0.9987 (0.9965) | -4.35 / 4.23 | 1.0 (362) | ok |
| v3-C1b-calm-tree16-pfifo-r2 | r0->r2 | target | 437701 | 0 / 0 (21.89) | 0 / 0 | ok | 244944 | 0.9986 (0.9964) | -4.41 / 4.23 | 1.0 (366) | ok |
| v3-C1b-calm-tree16-pfifo-r2 | r1->switch-a | target | 219257 | 0 / 0 (10.96) | 0 / 0 | ok | 103940 | 0.9990 (0.9985) | -4.43 / 4.26 | 1.0 (324) | ok |
| v3-C1b-calm-tree16-pfifo-r2 | r1->switch-b | target | 218895 | 0 / 0 (10.94) | 0 / 0 | ok | 103697 | 0.9990 (0.9985) | -4.26 / 4.09 | 1.0 (332) | ok |
| v3-C1b-calm-tree16-pfifo-r2 | r2->switch-c | target | 218654 | 0 / 0 (10.93) | 0 / 0 | ok | 101049 | 0.9990 (0.9986) | -4.2 / 4.08 | 1.0 (299) | ok |
| v3-C1b-calm-tree16-pfifo-r2 | r2->switch-d | target | 218554 | 0 / 0 (10.93) | 0 / 0 | ok | 105062 | 0.9990 (0.9984) | -4.4 / 4.15 | 1.0 (329) | ok |
| v3-C1b-calm-tree16-pfifo-r2 | rr->sub-ctrl | info | 33776 | 0 / 0 (3) | 0 / 0 | ok | 17570 | 0.8583 (0.8580) | -200.34 / 2.95 | nan (0) | FAIL |
| v3-C1b-calm-tree16-pfifo-r2 | rr->r0 | target | 875418 | 0 / 0 (43.77) | 0 / 0 | ok | 530363 | 0.9977 (0.9893) | -4.71 / 4.69 | 1.0 (368) | ok |
| v3-C1b-calm-uneven-pfifo-r1 | pub->r1 | info | 502163 | 0 / 0 (25.11) | 0 / 0 | ok | 408671 | 0.9990 (0.6882) | -9.01 / 6.68 | nan (0) | ok |
| v3-C1b-calm-uneven-pfifo-r1 | r1->sub-ctrl | info | 33952 | 0 / 0 (3) | 0 / 0 | ok | 21632 | 0.9468 (0.9466) | -199.47 / 1.97 | nan (0) | FAIL |
| v3-C1b-calm-uneven-pfifo-r1 | r1->r2 | info | 468222 | 0 / 0 (23.41) | 0 / 0 | ok | 5233 | 1.0000 (0.5924) | -3.64 / 4.25 | nan (0) | ok |
| v3-C1b-calm-uneven-pfifo-r1 | r2->switch-a | target | 316394 | 0 / 0 (15.82) | 0 / 0 | ok | 180785 | 0.9997 (0.9994) | -3.63 / 3.29 | 1.0 (401) | ok |
| v3-C1b-calm-uneven-pfifo-r1 | r2->switch-b | target | 429680 | 0 / 0 (21.48) | 0 / 0 | ok | 250261 | 0.9996 (0.9986) | -3.51 / 3.4 | 1.0 (403) | ok |
| v3-C1b-calm-uneven-pfifo-r1 | r2->switch-c | target | 709587 | 0 / 0 (35.48) | 0 / 0 | ok | 421251 | 0.9993 (0.9972) | -3.28 / 3.16 | 1.0 (382) | ok |
| v3-C1b-calm-uneven-pfifo-r2 | pub->r1 | info | 500691 | 0 / 0 (25.03) | 0 / 0 | ok | 401464 | 0.9983 (0.6808) | -8.97 / 7.24 | nan (0) | ok |
| v3-C1b-calm-uneven-pfifo-r2 | r1->sub-ctrl | info | 33746 | 0 / 0 (3) | 0 / 0 | ok | 15702 | 0.8916 (0.8912) | -201.0 / 2.03 | nan (0) | FAIL |
| v3-C1b-calm-uneven-pfifo-r2 | r1->r2 | info | 466954 | 0 / 0 (23.35) | 0 / 0 | ok | 6164 | 0.9992 (0.6476) | -4.08 / 4.7 | nan (0) | ok |
| v3-C1b-calm-uneven-pfifo-r2 | r2->switch-a | target | 316974 | 0 / 0 (15.85) | 0 / 0 | ok | 180206 | 0.9996 (0.9995) | -3.56 / 3.21 | 1.0 (416) | ok |
| v3-C1b-calm-uneven-pfifo-r2 | r2->switch-b | target | 428847 | 0 / 0 (21.44) | 0 / 0 | ok | 248022 | 0.9995 (0.9987) | -3.49 / 3.27 | 1.0 (391) | ok |
| v3-C1b-calm-uneven-pfifo-r2 | r2->switch-c | target | 709530 | 0 / 0 (35.48) | 0 / 0 | ok | 421235 | 0.9993 (0.9972) | -3.28 / 3.17 | 1.0 (368) | ok |
| v3-C2-sburst-s030u070-cake-r1 | pub->router | info | 506512 | 0 / 0 (25.33) | 0 / 0 | ok | 316116 | 0.9998 (0.8523) | -9.28 / 2.17 | nan (0) | ok |
| v3-C2-sburst-s030u070-cake-r1 | router->sub-ctrl | info | 94623 | 1 / 0 (4.73) | 1 / 0 | ok | 66920 | 0.9015 (0.9015) | -201.63 / 3.02 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-cake-r1 | router->switch | target | 1465784 | 0 / 0 (73.29) | 0 / 0 | ok | 892761 | 0.9997 (0.9989) | -3.15 / 3.31 | 1.0 (407) | ok |
| v3-C2-sburst-s030u070-cake-r2 | pub->router | info | 518384 | 0 / 0 (25.92) | 0 / 0 | ok | 278756 | 0.9997 (0.8093) | -9.36 / 2.27 | nan (0) | ok |
| v3-C2-sburst-s030u070-cake-r2 | router->sub-ctrl | info | 96662 | 0 / 0 (4.83) | 0 / 0 | ok | 71539 | 0.8256 (0.8255) | -201.94 / 3.37 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-cake-r2 | router->switch | target | 1499940 | 0 / 0 (75) | 0 / 0 | ok | 909602 | 0.9997 (0.9989) | -3.1 / 3.25 | 1.0 (442) | ok |
| v3-C2-sburst-s030u070-codel-r1 | pub->router | info | 469680 | 0 / 0 (23.48) | 0 / 0 | ok | 195391 | 0.9998 (0.8103) | -9.46 / 1.92 | nan (0) | ok |
| v3-C2-sburst-s030u070-codel-r1 | router->sub-ctrl | info | 94455 | 0 / 0 (4.72) | 0 / 0 | ok | 65696 | 0.9211 (0.9211) | -200.62 / 1.57 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-codel-r1 | router->switch | target | 1475856 | 0 / 1 (73.79) | 0 / 0 | ok | 1100531 | 0.9998 (0.9997) | -2.37 / 2.38 | 1.0 (6068) | ok |
| v3-C2-sburst-s030u070-codel-r2 | pub->router | info | 480747 | 0 / 0 (24.04) | 0 / 0 | ok | 179148 | 0.9999 (0.7779) | -9.56 / 1.9 | nan (0) | ok |
| v3-C2-sburst-s030u070-codel-r2 | router->sub-ctrl | info | 96788 | 0 / 0 (4.84) | 0 / 0 | ok | 65259 | 0.9110 (0.9110) | -201.05 / 1.42 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-codel-r2 | router->switch | target | 1508580 | 0 / 0 (75.43) | 0 / 0 | ok | 1118186 | 0.9999 (0.9997) | -2.38 / 2.38 | 1.0 (6056) | ok |
| v3-C2-sburst-s030u070-fq_codel-r1 | pub->router | info | 481034 | 0 / 0 (24.05) | 0 / 0 | ok | 193151 | 0.9996 (0.6835) | -9.69 / 2.77 | nan (0) | ok |
| v3-C2-sburst-s030u070-fq_codel-r1 | router->sub-ctrl | info | 94222 | 1 / 0 (4.71) | 1 / 0 | ok | 49416 | 0.8533 (0.8532) | -201.71 / 1.37 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-fq_codel-r1 | router->switch | target | 1472535 | 0 / 0 (73.63) | 0 / 0 | ok | 924226 | 0.9997 (0.9993) | -2.99 / 3.07 | 1.0 (667) | ok |
| v3-C2-sburst-s030u070-fq_codel-r2 | pub->router | info | 492594 | 0 / 0 (24.63) | 0 / 0 | ok | 196002 | 0.9992 (0.6325) | -9.7 / 3.28 | nan (0) | ok |
| v3-C2-sburst-s030u070-fq_codel-r2 | router->sub-ctrl | info | 96713 | 0 / 0 (4.84) | 0 / 0 | ok | 66267 | 0.8776 (0.8775) | -200.45 / 1.49 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-fq_codel-r2 | router->switch | target | 1505142 | 0 / 0 (75.26) | 0 / 0 | ok | 932173 | 0.9997 (0.9993) | -2.97 / 3.06 | 1.0 (689) | ok |
| v3-C2-sburst-s030u070-pfifo-r1 | pub->router | info | 484486 | 0 / 0 (24.22) | 0 / 0 | ok | 187019 | 0.9999 (0.7716) | -9.62 / 1.88 | nan (0) | ok |
| v3-C2-sburst-s030u070-pfifo-r1 | router->sub-ctrl | info | 94380 | 0 / 0 (4.72) | 0 / 0 | ok | 65150 | 0.8830 (0.8829) | -201.0 / 1.41 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-pfifo-r1 | router->switch | target | 1466773 | 0 / 0 (73.34) | 0 / 0 | ok | 1083442 | 0.9999 (0.9998) | -1.46 / 1.52 | 1.0 (5850) | ok |
| v3-C2-sburst-s030u070-pfifo-r2 | pub->router | info | 495037 | 0 / 0 (24.75) | 0 / 0 | ok | 176928 | 0.9999 (0.7699) | -9.52 / 1.79 | nan (0) | ok |
| v3-C2-sburst-s030u070-pfifo-r2 | router->sub-ctrl | info | 96580 | 0 / 0 (4.83) | 0 / 0 | ok | 66072 | 0.8964 (0.8964) | -200.75 / 1.75 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-pfifo-r2 | router->switch | target | 1500460 | 0 / 0 (75.02) | 0 / 0 | ok | 1098403 | 0.9998 (0.9997) | -1.43 / 1.48 | 1.0 (5840) | ok |
| v3-C2-sburst-s030u070-pie-r1 | pub->router | info | 519979 | 0 / 0 (26) | 0 / 0 | ok | 217768 | 0.9999 (0.7985) | -9.51 / 2.0 | nan (0) | ok |
| v3-C2-sburst-s030u070-pie-r1 | router->sub-ctrl | info | 94488 | 0 / 0 (4.72) | 0 / 0 | ok | 62717 | 0.9106 (0.9105) | -201.22 / 1.48 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-pie-r1 | router->switch | target | 1462604 | 0 / 0 (73.13) | 0 / 0 | ok | 1051843 | 0.9998 (0.9996) | -1.47 / 1.52 | 1.0 (4913) | ok |
| v3-C2-sburst-s030u070-pie-r2 | pub->router | info | 544313 | 0 / 0 (27.22) | 0 / 0 | ok | 270425 | 0.9999 (0.8585) | -9.32 / 1.7 | nan (0) | ok |
| v3-C2-sburst-s030u070-pie-r2 | router->sub-ctrl | info | 96764 | 0 / 0 (4.84) | 0 / 0 | ok | 64580 | 0.9095 (0.9095) | -201.08 / 1.62 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-pie-r2 | router->switch | target | 1500288 | 0 / 0 (75.01) | 0 / 0 | ok | 1077501 | 0.9998 (0.9996) | -1.45 / 1.49 | 1.0 (4972) | ok |
| v3-C2-sburst-s030u070-red-r1 | pub->router | info | 515473 | 0 / 0 (25.77) | 0 / 0 | ok | 210542 | 0.9998 (0.7863) | -9.51 / 2.13 | nan (0) | ok |
| v3-C2-sburst-s030u070-red-r1 | router->sub-ctrl | info | 94334 | 1 / 0 (4.72) | 1 / 0 | ok | 59455 | 0.9021 (0.9021) | -201.47 / 1.39 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-red-r1 | router->switch | target | 1466820 | 0 / 0 (73.34) | 0 / 0 | ok | 1088999 | 0.9999 (0.9997) | -1.5 / 1.55 | 1.0 (5923) | ok |
| v3-C2-sburst-s030u070-red-r2 | pub->router | info | 529512 | 0 / 0 (26.48) | 0 / 0 | ok | 232129 | 0.9999 (0.8278) | -9.46 / 1.63 | nan (0) | ok |
| v3-C2-sburst-s030u070-red-r2 | router->sub-ctrl | info | 96524 | 0 / 0 (4.83) | 0 / 0 | ok | 57306 | 0.9180 (0.9180) | -201.09 / 1.72 | nan (0) | FAIL |
| v3-C2-sburst-s030u070-red-r2 | router->switch | target | 1501320 | 0 / 0 (75.07) | 0 / 0 | ok | 1106854 | 0.9998 (0.9997) | -1.43 / 1.48 | 1.0 (5902) | ok |
| v3-C3a-sburst-s010u070-codel-r1 | pub->router | info | 280093 | 0 / 0 (14) | 0 / 0 | ok | 106862 | 0.9999 (0.7539) | -9.74 / 1.86 | nan (0) | ok |
| v3-C3a-sburst-s010u070-codel-r1 | router->sub-ctrl | info | 94408 | 1 / 0 (4.72) | 1 / 0 | ok | 63644 | 0.8936 (0.8936) | -201.27 / 1.26 | nan (0) | FAIL |
| v3-C3a-sburst-s010u070-codel-r1 | router->switch | target | 2000575 | 0 / 0 (100.03) | 0 / 0 | ok | 1187778 | 0.9998 (0.9995) | -2.22 / 2.22 | 1.0 (5425) | ok |
| v3-C3a-sburst-s010u070-codel-r2 | pub->router | info | 286902 | 0 / 0 (14.35) | 0 / 0 | ok | 108653 | 0.9999 (0.7409) | -9.75 / 1.98 | nan (0) | ok |
| v3-C3a-sburst-s010u070-codel-r2 | router->sub-ctrl | info | 96877 | 0 / 0 (4.84) | 0 / 0 | ok | 67129 | 0.8632 (0.8631) | -201.06 / 1.51 | 1.0 (1) | FAIL |
| v3-C3a-sburst-s010u070-codel-r2 | router->switch | target | 2050198 | 0 / 0 (102.51) | 0 / 0 | ok | 1207455 | 0.9998 (0.9995) | -2.25 / 2.25 | 1.0 (5449) | ok |
| v3-C3a-sburst-s010u070-pfifo-r1 | pub->router | info | 284074 | 0 / 0 (14.2) | 0 / 0 | ok | 94927 | 0.9999 (0.6953) | -9.78 / 2.03 | nan (0) | ok |
| v3-C3a-sburst-s010u070-pfifo-r1 | router->sub-ctrl | info | 94382 | 1 / 0 (4.72) | 1 / 0 | ok | 66924 | 0.8749 (0.8749) | -200.99 / 1.39 | nan (0) | FAIL |
| v3-C3a-sburst-s010u070-pfifo-r1 | router->switch | target | 1989351 | 0 / 0 (99.47) | 0 / 0 | ok | 1158303 | 0.9998 (0.9995) | -1.33 / 1.36 | 1.0 (5223) | ok |
| v3-C3a-sburst-s010u070-pfifo-r2 | pub->router | info | 289281 | 0 / 0 (14.46) | 0 / 0 | ok | 109922 | 0.9999 (0.7688) | -9.68 / 1.91 | nan (0) | ok |
| v3-C3a-sburst-s010u070-pfifo-r2 | router->sub-ctrl | info | 96654 | 1 / 0 (4.83) | 1 / 0 | ok | 65129 | 0.8978 (0.8978) | -200.87 / 1.54 | nan (0) | FAIL |
| v3-C3a-sburst-s010u070-pfifo-r2 | router->switch | target | 2037120 | 0 / 0 (101.86) | 0 / 0 | ok | 1170043 | 0.9998 (0.9996) | -1.3 / 1.32 | 1.0 (5231) | ok |
| v3-C3a-sburst-s065u070-codel-r1 | pub->router | info | 484958 | 0 / 0 (24.25) | 0 / 0 | ok | 207752 | 0.9999 (0.8251) | -9.49 / 1.68 | nan (0) | ok |
| v3-C3a-sburst-s065u070-codel-r1 | router->sub-ctrl | info | 94334 | 1 / 0 (4.72) | 1 / 0 | ok | 60050 | 0.9083 (0.9083) | -201.27 / 1.44 | nan (0) | FAIL |
| v3-C3a-sburst-s065u070-codel-r1 | router->switch | target | 694561 | 0 / 0 (34.73) | 0 / 0 | ok | 615715 | 0.9999 (0.9999) | -2.87 / 2.87 | 1.0 (8147) | ok |
| v3-C3a-sburst-s065u070-codel-r2 | pub->router | info | 499003 | 0 / 0 (24.95) | 0 / 0 | ok | 178717 | 0.9999 (0.7637) | -9.6 / 1.79 | nan (0) | ok |
| v3-C3a-sburst-s065u070-codel-r2 | router->sub-ctrl | info | 96683 | 0 / 0 (4.83) | 0 / 0 | ok | 62464 | 0.8997 (0.8997) | -201.1 / 1.62 | nan (0) | FAIL |
| v3-C3a-sburst-s065u070-codel-r2 | router->switch | target | 711700 | 0 / 0 (35.59) | 0 / 0 | ok | 630369 | 0.9999 (0.9998) | -2.94 / 2.95 | 1.0 (8317) | ok |
| v3-C3a-sburst-s065u070-pfifo-r1 | pub->router | info | 500694 | 0 / 0 (25.03) | 0 / 0 | ok | 176097 | 0.9998 (0.7702) | -9.54 / 1.73 | nan (0) | ok |
| v3-C3a-sburst-s065u070-pfifo-r1 | router->sub-ctrl | info | 94302 | 1 / 0 (4.72) | 1 / 0 | ok | 58742 | 0.9006 (0.9006) | -201.35 / 1.52 | nan (0) | FAIL |
| v3-C3a-sburst-s065u070-pfifo-r1 | router->switch | target | 690672 | 0 / 0 (34.53) | 0 / 0 | ok | 609215 | 0.9999 (0.9999) | -1.77 / 1.85 | 1.0 (7943) | ok |
| v3-C3a-sburst-s065u070-pfifo-r2 | pub->router | info | 511188 | 0 / 0 (25.56) | 0 / 0 | ok | 189731 | 0.9999 (0.7766) | -9.56 / 1.84 | nan (0) | ok |
| v3-C3a-sburst-s065u070-pfifo-r2 | router->sub-ctrl | info | 96744 | 0 / 0 (4.84) | 0 / 0 | ok | 60432 | 0.8869 (0.8869) | -201.48 / 1.38 | nan (0) | FAIL |
| v3-C3a-sburst-s065u070-pfifo-r2 | router->switch | target | 706853 | 0 / 0 (35.34) | 0 / 0 | ok | 622337 | 1.0000 (0.9999) | -1.74 / 1.84 | 1.0 (7991) | ok |
| v3-C3b-sburst-legacy-pfifo-r1 | pub->router | info | 491011 | 0 / 0 (24.55) | 0 / 0 | ok | 195769 | 0.9999 (0.8038) | -9.55 / 1.56 | nan (0) | ok |
| v3-C3b-sburst-legacy-pfifo-r1 | router->sub-ctrl | info | 94374 | 1 / 0 (4.72) | 1 / 0 | ok | 62973 | 0.8903 (0.8903) | -200.62 / 1.49 | nan (0) | FAIL |
| v3-C3b-sburst-legacy-pfifo-r1 | router->switch | target | 472222 | 0 / 0 (23.61) | 0 / 0 | ok | 447644 | 1.0000 (0.9999) | -1.88 / 2.01 | 1.0 (8925) | ok |
| v3-C3b-sburst-legacy-pfifo-r2 | pub->router | info | 505096 | 0 / 0 (25.25) | 0 / 0 | ok | 188655 | 0.9998 (0.7770) | -9.59 / 1.78 | nan (0) | ok |
| v3-C3b-sburst-legacy-pfifo-r2 | router->sub-ctrl | info | 96719 | 0 / 0 (4.84) | 0 / 0 | ok | 55128 | 0.8913 (0.8913) | -201.48 / 1.38 | nan (0) | FAIL |
| v3-C3b-sburst-legacy-pfifo-r2 | router->switch | target | 483433 | 0 / 0 (24.17) | 0 / 0 | ok | 458460 | 1.0000 (1.0000) | -2.0 / 2.06 | 1.0 (9119) | ok |
| v3-C4-sramp-s030u070-codel-r1 | pub->router | info | 322794 | 0 / 0 (16.14) | 0 / 0 | ok | 135598 | 0.9999 (0.8135) | -9.46 / 1.81 | nan (0) | ok |
| v3-C4-sramp-s030u070-codel-r1 | router->sub-ctrl | info | 62834 | 0 / 0 (3.14) | 0 / 0 | ok | 40386 | 0.9007 (0.9007) | -201.27 / 1.54 | nan (0) | FAIL |
| v3-C4-sramp-s030u070-codel-r1 | router->switch | target | 994541 | 0 / 0 (49.73) | 0 / 0 | ok | 743933 | 0.9999 (0.9996) | -2.27 / 2.29 | 1.0 (4086) | ok |
| v3-C4-sramp-s030u070-codel-r2 | pub->router | info | 300596 | 0 / 0 (15.03) | 0 / 0 | ok | 115487 | 0.9998 (0.7936) | -9.51 / 1.77 | nan (0) | ok |
| v3-C4-sramp-s030u070-codel-r2 | router->sub-ctrl | info | 59310 | 0 / 0 (3) | 0 / 0 | ok | 31558 | 0.8237 (0.8237) | -201.46 / 1.37 | nan (0) | FAIL |
| v3-C4-sramp-s030u070-codel-r2 | router->switch | target | 949140 | 0 / 0 (47.46) | 0 / 0 | ok | 722020 | 0.9999 (0.9997) | -2.34 / 2.34 | 1.0 (4096) | ok |
| v3-C4-sramp-s030u070-fq_codel-r1 | pub->router | info | 322742 | 0 / 0 (16.14) | 0 / 0 | ok | 128875 | 0.9993 (0.6707) | -9.68 / 2.59 | nan (0) | ok |
| v3-C4-sramp-s030u070-fq_codel-r1 | router->sub-ctrl | info | 62825 | 0 / 0 (3.14) | 0 / 0 | ok | 37783 | 0.8416 (0.8415) | -201.27 / 1.44 | nan (0) | FAIL |
| v3-C4-sramp-s030u070-fq_codel-r1 | router->switch | target | 991907 | 0 / 0 (49.6) | 0 / 0 | ok | 609139 | 0.9997 (0.9992) | -2.89 / 2.94 | 1.0 (296) | ok |
| v3-C4-sramp-s030u070-fq_codel-r2 | pub->router | info | 307103 | 0 / 0 (15.36) | 0 / 0 | ok | 117948 | 0.9996 (0.6771) | -9.66 / 2.35 | nan (0) | ok |
| v3-C4-sramp-s030u070-fq_codel-r2 | router->sub-ctrl | info | 59471 | 0 / 0 (3) | 0 / 0 | ok | 35135 | 0.8547 (0.8547) | -200.13 / 1.6 | nan (0) | FAIL |
| v3-C4-sramp-s030u070-fq_codel-r2 | router->switch | target | 948696 | 0 / 0 (47.43) | 0 / 0 | ok | 596184 | 0.9997 (0.9991) | -2.95 / 3.04 | 1.0 (300) | ok |
| v3-C4-sramp-s030u070-pfifo-r1 | pub->router | info | 327474 | 0 / 0 (16.37) | 0 / 0 | ok | 126204 | 0.9999 (0.7913) | -9.5 / 1.77 | nan (0) | ok |
| v3-C4-sramp-s030u070-pfifo-r1 | router->sub-ctrl | info | 62911 | 0 / 0 (3.15) | 0 / 0 | ok | 35520 | 0.9032 (0.9032) | -201.39 / 1.66 | nan (0) | FAIL |
| v3-C4-sramp-s030u070-pfifo-r1 | router->switch | target | 990309 | 0 / 0 (49.52) | 0 / 0 | ok | 737235 | 0.9998 (0.9997) | -1.4 / 1.44 | 1.0 (4003) | ok |
| v3-C4-sramp-s030u070-pfifo-r2 | pub->router | info | 310725 | 0 / 0 (15.54) | 0 / 0 | ok | 124642 | 0.9999 (0.7954) | -9.51 / 1.88 | nan (0) | ok |
| v3-C4-sramp-s030u070-pfifo-r2 | router->sub-ctrl | info | 59434 | 0 / 0 (3) | 0 / 0 | ok | 41121 | 0.9104 (0.9104) | -201.12 / 1.42 | nan (0) | FAIL |
| v3-C4-sramp-s030u070-pfifo-r2 | router->switch | target | 942925 | 0 / 0 (47.15) | 0 / 0 | ok | 709491 | 0.9998 (0.9997) | -1.44 / 1.48 | 1.0 (3966) | ok |
| v3-C4-sramp-s030u070-pie-r1 | pub->router | info | 345651 | 0 / 0 (17.28) | 0 / 0 | ok | 133965 | 0.9999 (0.8001) | -9.44 / 1.75 | nan (0) | ok |
| v3-C4-sramp-s030u070-pie-r1 | router->sub-ctrl | info | 62860 | 0 / 0 (3.14) | 0 / 0 | ok | 38387 | 0.9095 (0.9095) | -201.23 / 1.67 | nan (0) | FAIL |
| v3-C4-sramp-s030u070-pie-r1 | router->switch | target | 988699 | 0 / 0 (49.43) | 0 / 0 | ok | 725227 | 0.9999 (0.9997) | -1.41 / 1.46 | 1.0 (3632) | ok |
| v3-C4-sramp-s030u070-pie-r2 | pub->router | info | 332270 | 0 / 0 (16.61) | 0 / 0 | ok | 131754 | 0.9999 (0.8138) | -9.42 / 1.7 | nan (0) | ok |
| v3-C4-sramp-s030u070-pie-r2 | router->sub-ctrl | info | 59338 | 0 / 0 (3) | 0 / 0 | ok | 32561 | 0.8609 (0.8609) | -201.3 / 1.61 | nan (0) | FAIL |
| v3-C4-sramp-s030u070-pie-r2 | router->switch | target | 944247 | 0 / 0 (47.21) | 0 / 0 | ok | 705802 | 0.9999 (0.9997) | -1.47 / 1.52 | 1.0 (3723) | ok |
| v3-C5-stcp-s030u070-codel-r1 | pub->router | info | 517461 | 0 / 0 (25.87) | 0 / 0 | ok | 215215 | 0.9999 (0.8012) | -9.46 / 1.91 | nan (0) | ok |
| v3-C5-stcp-s030u070-codel-r1 | router->sub-ctrl | info | 96387 | 1 / 0 (4.82) | 1 / 0 | ok | 67544 | 0.8914 (0.8914) | -200.98 / 1.65 | nan (0) | FAIL |
| v3-C5-stcp-s030u070-codel-r1 | router->switch | target | 1483732 | 0 / 0 (74.19) | 0 / 0 | ok | 1115525 | 0.9999 (0.9996) | -2.45 / 2.45 | 1.0 (6676) | ok |
| v3-C5-stcp-s030u070-codel-r2 | pub->router | info | 508981 | 0 / 0 (25.45) | 0 / 0 | ok | 270436 | 0.9999 (0.8692) | -9.35 / 1.76 | nan (0) | ok |
| v3-C5-stcp-s030u070-codel-r2 | router->sub-ctrl | info | 94791 | 0 / 0 (4.74) | 0 / 0 | ok | 63181 | 0.9205 (0.9205) | -200.72 / 1.64 | nan (0) | FAIL |
| v3-C5-stcp-s030u070-codel-r2 | router->switch | target | 1465452 | 0 / 0 (73.27) | 0 / 0 | ok | 1109266 | 0.9999 (0.9996) | -2.37 / 2.38 | 1.0 (6683) | ok |
| v3-C5-stcp-s030u070-fq_codel-r1 | pub->router | info | 517347 | 0 / 0 (25.87) | 0 / 0 | ok | 279122 | 0.9997 (0.7848) | -9.49 / 2.37 | nan (0) | ok |
| v3-C5-stcp-s030u070-fq_codel-r1 | router->sub-ctrl | info | 96394 | 0 / 0 (4.82) | 0 / 0 | ok | 67502 | 0.8889 (0.8888) | -199.74 / 1.68 | nan (0) | FAIL |
| v3-C5-stcp-s030u070-fq_codel-r1 | router->switch | target | 1488743 | 0 / 0 (74.44) | 0 / 0 | ok | 867924 | 0.9998 (0.9993) | -2.45 / 2.73 | nan (0) | ok |
| v3-C5-stcp-s030u070-fq_codel-r2 | pub->router | info | 508603 | 0 / 0 (25.43) | 0 / 0 | ok | 252102 | 0.9995 (0.7513) | -9.54 / 2.87 | nan (0) | ok |
| v3-C5-stcp-s030u070-fq_codel-r2 | router->sub-ctrl | info | 94675 | 0 / 0 (4.73) | 0 / 0 | ok | 61385 | 0.8644 (0.8644) | -200.79 / 1.67 | nan (0) | FAIL |
| v3-C5-stcp-s030u070-fq_codel-r2 | router->switch | target | 1470013 | 0 / 0 (73.5) | 0 / 0 | ok | 858362 | 0.9998 (0.9994) | -2.43 / 2.68 | nan (0) | ok |
| v3-C5-stcp-s030u070-pfifo-r1 | pub->router | info | 509621 | 0 / 0 (25.48) | 0 / 0 | ok | 192684 | 0.9998 (0.7840) | -9.5 / 1.81 | nan (0) | ok |
| v3-C5-stcp-s030u070-pfifo-r1 | router->sub-ctrl | info | 96478 | 0 / 0 (4.82) | 0 / 0 | ok | 64879 | 0.9289 (0.9289) | -200.78 / 1.46 | nan (0) | FAIL |
| v3-C5-stcp-s030u070-pfifo-r1 | router->switch | target | 1483250 | 0 / 0 (74.16) | 0 / 0 | ok | 1115793 | 0.9999 (0.9997) | -1.47 / 1.52 | 1.0 (6720) | ok |
| v3-C5-stcp-s030u070-pfifo-r2 | pub->router | info | 499397 | 0 / 0 (24.97) | 0 / 0 | ok | 192488 | 0.9999 (0.8043) | -9.45 / 1.77 | nan (0) | ok |
| v3-C5-stcp-s030u070-pfifo-r2 | router->sub-ctrl | info | 94651 | 0 / 0 (4.73) | 0 / 0 | ok | 65367 | 0.8949 (0.8949) | -200.63 / 1.43 | nan (0) | FAIL |
| v3-C5-stcp-s030u070-pfifo-r2 | router->switch | target | 1463741 | 0 / 0 (73.19) | 0 / 0 | ok | 1106270 | 0.9999 (0.9997) | -1.43 / 1.49 | 1.0 (6693) | ok |
| v3-C5-stcp-s030u070-pie-r1 | pub->router | info | 528788 | 0 / 0 (26.44) | 0 / 0 | ok | 202726 | 0.9998 (0.7910) | -9.49 / 1.87 | nan (0) | ok |
| v3-C5-stcp-s030u070-pie-r1 | router->sub-ctrl | info | 96409 | 0 / 0 (4.82) | 0 / 0 | ok | 60470 | 0.9178 (0.9177) | -200.87 / 1.69 | nan (0) | FAIL |
| v3-C5-stcp-s030u070-pie-r1 | router->switch | target | 1481666 | 0 / 0 (74.08) | 0 / 0 | ok | 1109970 | 0.9998 (0.9996) | -1.5 / 1.56 | 1.0 (6605) | ok |
| v3-C5-stcp-s030u070-pie-r2 | pub->router | info | 517857 | 0 / 0 (25.89) | 0 / 0 | ok | 202430 | 0.9998 (0.8005) | -9.46 / 1.72 | nan (0) | ok |
| v3-C5-stcp-s030u070-pie-r2 | router->sub-ctrl | info | 94610 | 0 / 0 (4.73) | 0 / 0 | ok | 59702 | 0.8780 (0.8780) | -200.9 / 1.59 | nan (0) | FAIL |
| v3-C5-stcp-s030u070-pie-r2 | router->switch | target | 1459890 | 0 / 0 (72.99) | 0 / 0 | ok | 1092340 | 0.9999 (0.9997) | -1.47 / 1.53 | 1.0 (6419) | ok |
| v3-C6-sjoin-s030u070-codel-r1 | pub->router | info | 354548 | 0 / 0 (17.73) | 0 / 0 | ok | 193976 | 1.0000 (0.8888) | -9.21 / 1.6 | nan (0) | ok |
| v3-C6-sjoin-s030u070-codel-r1 | router->sub-ctrl | info | 63810 | 0 / 0 (3.19) | 0 / 0 | ok | 41521 | 0.9264 (0.9264) | -200.73 / 1.61 | nan (0) | FAIL |
| v3-C6-sjoin-s030u070-codel-r1 | router->switch | target | 1083562 | 0 / 0 (54.18) | 0 / 0 | ok | 915305 | 0.9999 (0.9994) | -2.66 / 2.66 | 1.0 (6320) | ok |
| v3-C6-sjoin-s030u070-codel-r2 | pub->router | info | 369916 | 0 / 0 (18.5) | 0 / 0 | ok | 205192 | 0.9999 (0.8792) | -9.2 / 1.73 | nan (0) | ok |
| v3-C6-sjoin-s030u070-codel-r2 | router->sub-ctrl | info | 63008 | 0 / 0 (3.15) | 0 / 0 | ok | 42254 | 0.8867 (0.8866) | -201.11 / 1.43 | nan (0) | FAIL |
| v3-C6-sjoin-s030u070-codel-r2 | router->switch | target | 1080984 | 0 / 0 (54.05) | 0 / 0 | ok | 918445 | 0.9999 (0.9991) | -2.74 / 2.73 | 1.0 (6319) | ok |
| v3-C6-sjoin-s030u070-fq_codel-r1 | pub->router | info | 342162 | 0 / 0 (17.11) | 0 / 0 | ok | 226931 | 0.9992 (0.8657) | -9.25 / 2.05 | nan (0) | ok |
| v3-C6-sjoin-s030u070-fq_codel-r1 | router->sub-ctrl | info | 63781 | 1 / 0 (3.19) | 1 / 0 | ok | 40247 | 0.9180 (0.9179) | -199.82 / 1.74 | nan (0) | FAIL |
| v3-C6-sjoin-s030u070-fq_codel-r1 | router->switch | target | 1083294 | 0 / 0 (54.16) | 0 / 0 | ok | 671274 | 0.9959 (0.9950) | -3.51 / 3.84 | nan (0) | ok |
| v3-C6-sjoin-s030u070-fq_codel-r2 | pub->router | info | 340799 | 0 / 0 (17.04) | 0 / 0 | ok | 226415 | 0.9998 (0.8635) | -9.26 / 2.13 | nan (0) | ok |
| v3-C6-sjoin-s030u070-fq_codel-r2 | router->sub-ctrl | info | 63095 | 1 / 0 (3.15) | 1 / 0 | ok | 39691 | 0.9116 (0.9116) | -200.13 / 1.62 | nan (0) | FAIL |
| v3-C6-sjoin-s030u070-fq_codel-r2 | router->switch | target | 1077756 | 0 / 0 (53.89) | 0 / 0 | ok | 668697 | 0.9956 (0.9946) | -3.58 / 3.88 | nan (0) | ok |
| v3-C6-sjoin-s030u070-pfifo-r1 | pub->router | info | 343562 | 0 / 0 (17.18) | 0 / 0 | ok | 121925 | 0.9999 (0.8041) | -9.46 / 1.7 | nan (0) | ok |
| v3-C6-sjoin-s030u070-pfifo-r1 | router->sub-ctrl | info | 63653 | 1 / 0 (3.18) | 1 / 0 | ok | 39796 | 0.8798 (0.8797) | -201.02 / 1.42 | nan (0) | FAIL |
| v3-C6-sjoin-s030u070-pfifo-r1 | router->switch | target | 1078608 | 0 / 0 (53.93) | 0 / 0 | ok | 908563 | 0.9999 (0.9998) | -1.38 / 1.45 | 1.0 (6295) | ok |
| v3-C6-sjoin-s030u070-pfifo-r2 | pub->router | info | 340664 | 0 / 0 (17.03) | 0 / 0 | ok | 127107 | 0.9998 (0.7893) | -9.48 / 1.88 | nan (0) | ok |
| v3-C6-sjoin-s030u070-pfifo-r2 | router->sub-ctrl | info | 63167 | 0 / 0 (3.16) | 0 / 0 | ok | 40221 | 0.9111 (0.9110) | -201.38 / 1.41 | 1.0 (1) | FAIL |
| v3-C6-sjoin-s030u070-pfifo-r2 | router->switch | target | 1071693 | 0 / 0 (53.58) | 0 / 0 | ok | 905926 | 0.9999 (0.9998) | -1.37 / 1.44 | 1.0 (6274) | ok |
| v3-C7-hhier-s030-codel-r1 | pub->r1 | info | 2205343 | 0 / 0 (110.27) | 0 / 0 | ok | 939358 | 0.9991 (0.6756) | -9.33 / 4.32 | nan (0) | ok |
| v3-C7-hhier-s030-codel-r1 | r1->sub-ctrl | info | 273794 | 0 / 0 (13.69) | 0 / 0 | ok | 185641 | 0.9249 (0.9248) | -200.17 / 2.09 | nan (0) | FAIL |
| v3-C7-hhier-s030-codel-r1 | r1->r2 | target | 6687984 | 0 / 0 (334.4) | 0 / 0 | ok | 4088322 | 0.9993 (0.9976) | -2.63 / 2.61 | 1.0 (6497) | ok |
| v3-C7-hhier-s030-codel-r1 | r2->switch-a | target | 3526677 | 0 / 0 (176.33) | 0 / 0 | ok | 2295225 | 0.9996 (0.9993) | -3.26 / 3.22 | 1.0 (12043) | ok |
| v3-C7-hhier-s030-codel-r1 | r2->switch-b | target | 3465119 | 0 / 0 (173.26) | 0 / 0 | ok | 2155898 | 0.9995 (0.9992) | -3.26 / 3.21 | 1.0 (10267) | ok |
| v3-C7-hhier-s030-codel-r2 | pub->r1 | info | 2141124 | 0 / 0 (107.06) | 0 / 0 | ok | 815872 | 0.9988 (0.6516) | -9.33 / 4.28 | nan (0) | ok |
| v3-C7-hhier-s030-codel-r2 | r1->sub-ctrl | info | 265033 | 0 / 0 (13.25) | 0 / 0 | ok | 188370 | 0.8993 (0.8993) | -200.15 / 2.18 | 1.0 (1) | FAIL |
| v3-C7-hhier-s030-codel-r2 | r1->r2 | target | 6513474 | 0 / 0 (325.67) | 0 / 0 | ok | 3984188 | 0.9992 (0.9977) | -2.56 / 2.54 | 1.0 (6377) | ok |
| v3-C7-hhier-s030-codel-r2 | r2->switch-a | target | 3436551 | 0 / 0 (171.83) | 0 / 0 | ok | 2245663 | 0.9995 (0.9992) | -3.22 / 3.19 | 1.0 (12032) | ok |
| v3-C7-hhier-s030-codel-r2 | r2->switch-b | target | 3373366 | 0 / 0 (168.67) | 0 / 0 | ok | 2109847 | 0.9995 (0.9992) | -3.16 / 3.13 | 1.0 (10320) | ok |
| v3-C7-hhier-s030-fq_codel-r1 | pub->r1 | info | 2232232 | 0 / 0 (111.61) | 0 / 0 | ok | 1046015 | 0.9960 (0.5025) | -9.46 / 9.98 | nan (0) | ok |
| v3-C7-hhier-s030-fq_codel-r1 | r1->sub-ctrl | info | 273954 | 0 / 0 (13.7) | 0 / 0 | ok | 193749 | 0.9073 (0.9073) | -199.69 / 2.45 | nan (0) | FAIL |
| v3-C7-hhier-s030-fq_codel-r1 | r1->r2 | target | 6699656 | 0 / 0 (334.98) | 0 / 0 | ok | 3334960 | 0.9984 (0.9945) | -3.73 / 3.8 | 1.0 (137) | ok |
| v3-C7-hhier-s030-fq_codel-r1 | r2->switch-a | target | 3523986 | 0 / 0 (176.2) | 0 / 0 | ok | 1635933 | 0.9986 (0.9978) | -4.38 / 4.37 | 1.0 (1135) | ok |
| v3-C7-hhier-s030-fq_codel-r1 | r2->switch-b | target | 3465161 | 0 / 0 (173.26) | 0 / 0 | ok | 1496135 | 0.9984 (0.9977) | -4.39 / 4.34 | 1.0 (964) | ok |
| v3-C7-hhier-s030-fq_codel-r2 | pub->r1 | info | 2162489 | 0 / 0 (108.12) | 0 / 0 | ok | 944382 | 0.9956 (0.4680) | -9.47 / 10.25 | nan (0) | ok |
| v3-C7-hhier-s030-fq_codel-r2 | r1->sub-ctrl | info | 264871 | 0 / 0 (13.24) | 0 / 0 | ok | 186361 | 0.8958 (0.8958) | -199.26 / 2.45 | nan (0) | FAIL |
| v3-C7-hhier-s030-fq_codel-r2 | r1->r2 | target | 6516949 | 0 / 0 (325.85) | 0 / 0 | ok | 3242543 | 0.9984 (0.9946) | -3.79 / 3.84 | 1.0 (190) | ok |
| v3-C7-hhier-s030-fq_codel-r2 | r2->switch-a | target | 3431250 | 0 / 0 (171.56) | 0 / 0 | ok | 1609699 | 0.9984 (0.9976) | -4.55 / 4.54 | 1.0 (1087) | ok |
| v3-C7-hhier-s030-fq_codel-r2 | r2->switch-b | target | 3370969 | 0 / 0 (168.55) | 0 / 0 | ok | 1467937 | 0.9984 (0.9976) | -4.49 / 4.44 | 1.0 (968) | ok |
| v3-C7-hhier-s030-pfifo-r1 | pub->r1 | info | 2282466 | 0 / 0 (114.12) | 0 / 0 | ok | 905256 | 0.9993 (0.6813) | -9.33 / 3.5 | nan (0) | ok |
| v3-C7-hhier-s030-pfifo-r1 | r1->sub-ctrl | info | 273749 | 0 / 0 (13.69) | 0 / 0 | ok | 186605 | 0.9354 (0.9354) | -199.56 / 2.32 | nan (0) | FAIL |
| v3-C7-hhier-s030-pfifo-r1 | r1->r2 | target | 6743190 | 0 / 0 (337.16) | 0 / 0 | ok | 4156877 | 0.9992 (0.9977) | -2.22 / 2.23 | 1.0 (6328) | ok |
| v3-C7-hhier-s030-pfifo-r1 | r2->switch-a | target | 3512596 | 0 / 0 (175.63) | 0 / 0 | ok | 2246792 | 0.9996 (0.9993) | -2.22 / 2.23 | 1.0 (11405) | ok |
| v3-C7-hhier-s030-pfifo-r1 | r2->switch-b | target | 3449398 | 0 / 0 (172.47) | 0 / 0 | ok | 2127716 | 0.9996 (0.9993) | -2.23 / 2.25 | 1.0 (9771) | ok |
| v3-C7-hhier-s030-pfifo-r2 | pub->r1 | info | 2196642 | 0 / 0 (109.83) | 0 / 0 | ok | 909437 | 0.9988 (0.6680) | -9.35 / 4.23 | nan (0) | ok |
| v3-C7-hhier-s030-pfifo-r2 | r1->sub-ctrl | info | 265313 | 0 / 0 (13.27) | 0 / 0 | ok | 184283 | 0.9266 (0.9266) | -200.14 / 2.28 | nan (0) | FAIL |
| v3-C7-hhier-s030-pfifo-r2 | r1->r2 | target | 6548271 | 0 / 0 (327.41) | 0 / 0 | ok | 4021410 | 0.9992 (0.9977) | -2.24 / 2.23 | 1.0 (6214) | ok |
| v3-C7-hhier-s030-pfifo-r2 | r2->switch-a | target | 3416882 | 0 / 0 (170.84) | 0 / 0 | ok | 2216241 | 0.9996 (0.9993) | -2.21 / 2.22 | 1.0 (11411) | ok |
| v3-C7-hhier-s030-pfifo-r2 | r2->switch-b | target | 3354335 | 0 / 0 (167.72) | 0 / 0 | ok | 2063452 | 0.9995 (0.9993) | -2.26 / 2.26 | 1.0 (9670) | ok |
| v3-C7-hhier-s030-pie-r1 | pub->r1 | info | 2417108 | 0 / 0 (120.86) | 0 / 0 | ok | 1060903 | 0.9991 (0.6712) | -9.31 / 4.41 | nan (0) | ok |
| v3-C7-hhier-s030-pie-r1 | r1->sub-ctrl | info | 274073 | 0 / 0 (13.7) | 0 / 0 | ok | 190850 | 0.9310 (0.9310) | -200.21 / 2.22 | 1.0 (1) | FAIL |
| v3-C7-hhier-s030-pie-r1 | r1->r2 | target | 6821684 | 0 / 0 (341.08) | 0 / 0 | ok | 4288511 | 0.9993 (0.9973) | -2.35 / 2.34 | 1.0 (6137) | ok |
| v3-C7-hhier-s030-pie-r1 | r2->switch-a | target | 3517559 | 0 / 0 (175.88) | 0 / 0 | ok | 2222812 | 0.9996 (0.9992) | -2.35 / 2.34 | 1.0 (9406) | ok |
| v3-C7-hhier-s030-pie-r1 | r2->switch-b | target | 3463400 | 0 / 0 (173.17) | 0 / 0 | ok | 2085071 | 0.9995 (0.9991) | -2.35 / 2.33 | 1.0 (7948) | ok |
| v3-C7-hhier-s030-pie-r2 | pub->r1 | info | 2352064 | 0 / 0 (117.6) | 0 / 0 | ok | 1020865 | 0.9989 (0.6755) | -9.3 / 4.45 | nan (0) | ok |
| v3-C7-hhier-s030-pie-r2 | r1->sub-ctrl | info | 265487 | 0 / 0 (13.27) | 0 / 0 | ok | 182112 | 0.9097 (0.9095) | -200.53 / 2.24 | nan (0) | FAIL |
| v3-C7-hhier-s030-pie-r2 | r1->r2 | target | 6647545 | 0 / 0 (332.38) | 0 / 0 | ok | 4192446 | 0.9992 (0.9973) | -2.34 / 2.33 | 1.0 (6081) | ok |
| v3-C7-hhier-s030-pie-r2 | r2->switch-a | target | 3424509 | 0 / 0 (171.23) | 0 / 0 | ok | 2167633 | 0.9996 (0.9992) | -2.36 / 2.35 | 1.0 (9567) | ok |
| v3-C7-hhier-s030-pie-r2 | r2->switch-b | target | 3373197 | 0 / 0 (168.66) | 0 / 0 | ok | 2042028 | 0.9995 (0.9991) | -2.37 / 2.36 | 1.0 (8119) | ok |
| v3-C8-hhier-s065-pfifo-r1 | pub->r1 | info | 2348114 | 0 / 0 (117.41) | 0 / 0 | ok | 926233 | 0.9989 (0.6827) | -9.35 / 3.69 | nan (0) | ok |
| v3-C8-hhier-s065-pfifo-r1 | r1->sub-ctrl | info | 273505 | 0 / 0 (13.68) | 0 / 0 | ok | 193819 | 0.9000 (0.9000) | -199.83 / 2.3 | nan (0) | FAIL |
| v3-C8-hhier-s065-pfifo-r1 | r1->r2 | target | 3224392 | 0 / 0 (161.22) | 0 / 0 | ok | 2657989 | 0.9997 (0.9993) | -2.37 / 2.39 | 1.0 (13606) | ok |
| v3-C8-hhier-s065-pfifo-r1 | r2->switch-a | target | 1654832 | 0 / 0 (82.74) | 0 / 0 | ok | 1238349 | 0.9997 (0.9997) | -2.56 / 2.61 | 1.0 (15259) | ok |
| v3-C8-hhier-s065-pfifo-r1 | r2->switch-b | target | 1630829 | 0 / 0 (81.54) | 0 / 0 | ok | 1177425 | 0.9998 (0.9997) | -2.55 / 2.6 | 1.0 (13669) | ok |
| v3-C8-hhier-s065-pfifo-r2 | pub->r1 | info | 2269185 | 0 / 0 (113.46) | 0 / 0 | ok | 863919 | 0.9990 (0.6880) | -9.35 / 3.47 | nan (0) | ok |
| v3-C8-hhier-s065-pfifo-r2 | r1->sub-ctrl | info | 265253 | 0 / 0 (13.26) | 0 / 0 | ok | 187836 | 0.9020 (0.9019) | -199.79 / 2.19 | nan (0) | FAIL |
| v3-C8-hhier-s065-pfifo-r2 | r1->r2 | target | 3126086 | 0 / 0 (156.3) | 0 / 0 | ok | 2563013 | 0.9997 (0.9993) | -2.36 / 2.37 | 1.0 (12988) | ok |
| v3-C8-hhier-s065-pfifo-r2 | r2->switch-a | target | 1614305 | 0 / 0 (80.72) | 0 / 0 | ok | 1248392 | 0.9998 (0.9998) | -2.54 / 2.6 | 1.0 (15552) | ok |
| v3-C8-hhier-s065-pfifo-r2 | r2->switch-b | target | 1582694 | 0 / 0 (79.13) | 0 / 0 | ok | 1170782 | 0.9998 (0.9997) | -2.56 / 2.61 | 1.0 (13754) | ok |
| v3-C9-hdepth-tree16-codel-r1 | pub->rr | info | 2317013 | 0 / 0 (115.85) | 0 / 0 | ok | 1091811 | 0.9959 (0.5674) | -9.22 / 9.96 | nan (0) | ok |
| v3-C9-hdepth-tree16-codel-r1 | r0->r1 | target | 3225740 | 0 / 0 (161.29) | 0 / 0 | ok | 1788857 | 0.9987 (0.9967) | -4.71 / 4.59 | 1.0 (4002) | ok |
| v3-C9-hdepth-tree16-codel-r1 | r0->r2 | target | 3225688 | 0 / 0 (161.28) | 0 / 0 | ok | 1789534 | 0.9987 (0.9967) | -4.72 / 4.58 | 1.0 (3965) | ok |
| v3-C9-hdepth-tree16-codel-r1 | r1->switch-a | target | 1640325 | 0 / 0 (82.02) | 0 / 0 | ok | 819919 | 0.9991 (0.9986) | -5.77 / 5.57 | 1.0 (5687) | ok |
| v3-C9-hdepth-tree16-codel-r1 | r1->switch-b | target | 1614963 | 0 / 0 (80.75) | 0 / 0 | ok | 766461 | 0.9990 (0.9985) | -5.33 / 5.08 | 1.0 (3921) | ok |
| v3-C9-hdepth-tree16-codel-r1 | r2->switch-c | target | 1645533 | 0 / 0 (82.28) | 0 / 0 | ok | 846608 | 0.9991 (0.9986) | -5.59 / 5.42 | 1.0 (5823) | ok |
| v3-C9-hdepth-tree16-codel-r1 | r2->switch-d | target | 1615715 | 0 / 0 (80.79) | 0 / 0 | ok | 770175 | 0.9990 (0.9985) | -5.13 / 4.93 | 1.0 (4003) | ok |
| v3-C9-hdepth-tree16-codel-r1 | rr->sub-ctrl | info | 249590 | 0 / 0 (12.48) | 0 / 0 | ok | 176745 | 0.9105 (0.9104) | -199.82 / 3.59 | nan (0) | FAIL |
| v3-C9-hdepth-tree16-codel-r1 | rr->r0 | target | 6461138 | 0 / 0 (323.06) | 0 / 0 | ok | 3903744 | 0.9978 (0.9901) | -4.66 / 4.6 | 1.0 (3994) | ok |
| v3-C9-hdepth-tree16-codel-r2 | pub->rr | info | 2342328 | 0 / 0 (117.12) | 0 / 0 | ok | 1180186 | 0.9945 (0.5599) | -9.19 / 11.19 | nan (0) | ok |
| v3-C9-hdepth-tree16-codel-r2 | r0->r1 | target | 3264646 | 0 / 0 (163.23) | 0 / 0 | ok | 1825014 | 0.9987 (0.9967) | -4.74 / 4.59 | 1.0 (3995) | ok |
| v3-C9-hdepth-tree16-codel-r2 | r0->r2 | target | 3261762 | 0 / 0 (163.09) | 0 / 0 | ok | 1798743 | 0.9987 (0.9967) | -4.74 / 4.58 | 1.0 (3944) | ok |
| v3-C9-hdepth-tree16-codel-r2 | r1->switch-a | target | 1661740 | 0 / 0 (83.09) | 0 / 0 | ok | 841702 | 0.9991 (0.9985) | -5.68 / 5.5 | 1.0 (5859) | ok |
| v3-C9-hdepth-tree16-codel-r2 | r1->switch-b | target | 1633916 | 0 / 0 (81.7) | 0 / 0 | ok | 781912 | 0.9990 (0.9985) | -5.31 / 5.09 | 1.0 (3978) | ok |
| v3-C9-hdepth-tree16-codel-r2 | r2->switch-c | target | 1660512 | 0 / 0 (83.03) | 0 / 0 | ok | 829418 | 0.9991 (0.9986) | -5.72 / 5.52 | 1.0 (5665) | ok |
| v3-C9-hdepth-tree16-codel-r2 | r2->switch-d | target | 1631371 | 0 / 0 (81.57) | 0 / 0 | ok | 768808 | 0.9990 (0.9985) | -5.29 / 5.08 | 1.0 (3846) | ok |
| v3-C9-hdepth-tree16-codel-r2 | rr->sub-ctrl | info | 251539 | 0 / 0 (12.58) | 0 / 0 | ok | 173540 | 0.9236 (0.9235) | -199.66 / 3.15 | nan (0) | FAIL |
| v3-C9-hdepth-tree16-codel-r2 | rr->r0 | target | 6532846 | 0 / 0 (326.64) | 0 / 0 | ok | 3944242 | 0.9978 (0.9901) | -4.71 / 4.64 | 1.0 (4008) | ok |
| v3-C9-hdepth-tree16-fq_codel-r1 | pub->rr | info | 2378733 | 0 / 0 (118.94) | 0 / 0 | ok | 1395048 | 0.9647 (0.3111) | -9.33 / 29.33 | nan (0) | FAIL |
| v3-C9-hdepth-tree16-fq_codel-r1 | r0->r1 | target | 3253813 | 0 / 0 (162.69) | 0 / 0 | ok | 1355082 | 0.9937 (0.9877) | -9.55 / 8.31 | 1.0 (372) | ok |
| v3-C9-hdepth-tree16-fq_codel-r1 | r0->r2 | target | 3251642 | 0 / 0 (162.58) | 0 / 0 | ok | 1332316 | 0.9938 (0.9881) | -9.58 / 8.28 | 1.0 (403) | ok |
| v3-C9-hdepth-tree16-fq_codel-r1 | r1->switch-a | target | 1651938 | 0 / 0 (82.6) | 0 / 0 | ok | 567289 | 0.9963 (0.9949) | -9.98 / 8.67 | 1.0 (1013) | ok |
| v3-C9-hdepth-tree16-fq_codel-r1 | r1->switch-b | target | 1626467 | 0 / 0 (81.32) | 0 / 0 | ok | 506011 | 0.9957 (0.9943) | -10.33 / 8.18 | 1.0 (500) | ok |
| v3-C9-hdepth-tree16-fq_codel-r1 | r2->switch-c | target | 1650535 | 0 / 0 (82.53) | 0 / 0 | ok | 555520 | 0.9960 (0.9943) | -10.27 / 8.57 | 1.0 (1003) | ok |
| v3-C9-hdepth-tree16-fq_codel-r1 | r2->switch-d | target | 1627269 | 0 / 0 (81.36) | 0 / 0 | ok | 526655 | 0.9960 (0.9946) | -9.95 / 8.09 | 1.0 (485) | ok |
| v3-C9-hdepth-tree16-fq_codel-r1 | rr->sub-ctrl | info | 249502 | 0 / 0 (12.48) | 0 / 0 | ok | 169829 | 0.8957 (0.8956) | -199.3 / 4.71 | nan (0) | FAIL |
| v3-C9-hdepth-tree16-fq_codel-r1 | rr->r0 | target | 6504553 | 0 / 0 (325.23) | 0 / 0 | ok | 3483577 | 0.9902 (0.9712) | -9.64 / 9.62 | 1.0 (193) | ok |
| v3-C9-hdepth-tree16-fq_codel-r2 | pub->rr | info | 2404697 | 0 / 0 (120.23) | 0 / 0 | ok | 1363298 | 0.9639 (0.2983) | -9.34 / 29.45 | nan (0) | FAIL |
| v3-C9-hdepth-tree16-fq_codel-r2 | r0->r1 | target | 3289498 | 0 / 0 (164.47) | 0 / 0 | ok | 1365748 | 0.9937 (0.9876) | -9.55 / 8.33 | 1.0 (404) | ok |
| v3-C9-hdepth-tree16-fq_codel-r2 | r0->r2 | target | 3288895 | 0 / 0 (164.44) | 0 / 0 | ok | 1362412 | 0.9936 (0.9879) | -9.61 / 8.39 | 1.0 (416) | ok |
| v3-C9-hdepth-tree16-fq_codel-r2 | r1->switch-a | target | 1671537 | 0 / 0 (83.58) | 0 / 0 | ok | 584478 | 0.9962 (0.9948) | -10.28 / 8.71 | 1.0 (934) | ok |
| v3-C9-hdepth-tree16-fq_codel-r2 | r1->switch-b | target | 1645241 | 0 / 0 (82.26) | 0 / 0 | ok | 537232 | 0.9960 (0.9946) | -10.36 / 8.35 | 1.0 (494) | ok |
| v3-C9-hdepth-tree16-fq_codel-r2 | r2->switch-c | target | 1670656 | 0 / 0 (83.53) | 0 / 0 | ok | 577269 | 0.9963 (0.9948) | -10.18 / 8.57 | 1.0 (977) | ok |
| v3-C9-hdepth-tree16-fq_codel-r2 | r2->switch-d | target | 1641826 | 0 / 0 (82.09) | 0 / 0 | ok | 512141 | 0.9960 (0.9947) | -9.9 / 8.06 | 1.0 (494) | ok |
| v3-C9-hdepth-tree16-fq_codel-r2 | rr->sub-ctrl | info | 251468 | 0 / 0 (12.57) | 0 / 0 | ok | 174151 | 0.8968 (0.8967) | -199.53 / 4.65 | nan (0) | FAIL |
| v3-C9-hdepth-tree16-fq_codel-r2 | rr->r0 | target | 6584871 | 0 / 0 (329.24) | 0 / 0 | ok | 3546564 | 0.9902 (0.9714) | -9.58 / 9.62 | 1.0 (193) | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | pub->rr | info | 2361178 | 0 / 0 (118.06) | 0 / 0 | ok | 1076226 | 0.9940 (0.5180) | -9.25 / 11.54 | nan (0) | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | r0->r1 | target | 3237215 | 0 / 0 (161.86) | 0 / 0 | ok | 1802557 | 0.9987 (0.9967) | -4.34 / 4.2 | 1.0 (3910) | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | r0->r2 | target | 3233316 | 0 / 0 (161.67) | 0 / 0 | ok | 1789623 | 0.9986 (0.9966) | -4.37 / 4.23 | 1.0 (3817) | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | r1->switch-a | target | 1636858 | 0 / 0 (81.84) | 0 / 0 | ok | 815877 | 0.9990 (0.9986) | -4.09 / 3.97 | 1.0 (5262) | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | r1->switch-b | target | 1614130 | 0 / 0 (80.71) | 0 / 0 | ok | 758390 | 0.9990 (0.9986) | -4.22 / 4.04 | 1.0 (3661) | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | r2->switch-c | target | 1638860 | 0 / 0 (81.94) | 0 / 0 | ok | 824882 | 0.9991 (0.9987) | -4.22 / 4.06 | 1.0 (5354) | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | r2->switch-d | target | 1612151 | 0 / 0 (80.61) | 0 / 0 | ok | 777554 | 0.9991 (0.9986) | -4.29 / 4.15 | 1.0 (3693) | ok |
| v3-C9-hdepth-tree16-pfifo-r1 | rr->sub-ctrl | info | 249060 | 0 / 0 (12.45) | 0 / 0 | ok | 171288 | 0.8985 (0.8983) | -199.88 / 3.21 | nan (0) | FAIL |
| v3-C9-hdepth-tree16-pfifo-r1 | rr->r0 | target | 6495072 | 0 / 0 (324.75) | 0 / 0 | ok | 3954055 | 0.9977 (0.9901) | -4.55 / 4.49 | 1.0 (3975) | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | pub->rr | info | 2390234 | 0 / 0 (119.51) | 0 / 0 | ok | 1106136 | 0.9948 (0.5354) | -9.24 / 10.9 | nan (0) | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | r0->r1 | target | 3269631 | 0 / 0 (163.48) | 0 / 0 | ok | 1814985 | 0.9987 (0.9968) | -4.3 / 4.17 | 1.0 (3853) | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | r0->r2 | target | 3274364 | 0 / 0 (163.72) | 0 / 0 | ok | 1822365 | 0.9987 (0.9968) | -4.32 / 4.17 | 1.0 (3890) | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | r1->switch-a | target | 1660664 | 0 / 0 (83.03) | 0 / 0 | ok | 822559 | 0.9990 (0.9986) | -4.13 / 3.97 | 1.0 (5322) | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | r1->switch-b | target | 1628245 | 0 / 0 (81.41) | 0 / 0 | ok | 774892 | 0.9991 (0.9986) | -4.23 / 4.09 | 1.0 (3720) | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | r2->switch-c | target | 1657477 | 0 / 0 (82.87) | 0 / 0 | ok | 839854 | 0.9992 (0.9987) | -4.14 / 4.06 | 1.0 (5410) | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | r2->switch-d | target | 1629223 | 0 / 0 (81.46) | 0 / 0 | ok | 767166 | 0.9990 (0.9984) | -4.29 / 4.12 | 1.0 (3640) | ok |
| v3-C9-hdepth-tree16-pfifo-r2 | rr->sub-ctrl | info | 251675 | 0 / 0 (12.58) | 0 / 0 | ok | 178963 | 0.9001 (0.9000) | -200.02 / 3.21 | nan (0) | FAIL |
| v3-C9-hdepth-tree16-pfifo-r2 | rr->r0 | target | 6574974 | 0 / 0 (328.75) | 0 / 0 | ok | 4009750 | 0.9977 (0.9903) | -4.51 / 4.46 | 1.0 (3990) | ok |
| v3-G1-calm-legacy-pfifo-r1 | pub->router | info | 181427 | 0 / 0 (9.07) | 0 / 0 | ok | 76181 | 0.9997 (0.8137) | -9.62 / 1.65 | nan (0) | ok |
| v3-G1-calm-legacy-pfifo-r1 | router->sub-ctrl | info | 33933 | 1 / 0 (3) | 1 / 0 | ok | 19728 | 0.9018 (0.9018) | -201.32 / 1.53 | nan (0) | FAIL |
| v3-G1-calm-legacy-pfifo-r1 | router->switch | target | 146871 | 0 / 0 (7.34) | 0 / 0 | ok | 134580 | 1.0000 (0.9999) | -2.08 / 2.22 | 1.0 (1767) | ok |
| v3-G1-calm-s030u070-pfifo-r1 | pub->router | info | 181880 | 0 / 0 (9.09) | 0 / 0 | ok | 110820 | 0.9999 (0.8847) | -9.37 / 1.55 | nan (0) | ok |
| v3-G1-calm-s030u070-pfifo-r1 | router->sub-ctrl | info | 33879 | 0 / 0 (3) | 0 / 0 | ok | 18255 | 0.8628 (0.8627) | -201.39 / 1.78 | nan (0) | FAIL |
| v3-G1-calm-s030u070-pfifo-r1 | router->switch | target | 467091 | 0 / 0 (23.35) | 0 / 0 | ok | 272342 | 0.9998 (0.9997) | -1.53 / 1.57 | 1.0 (393) | ok |
| v3-G2-calm-access-pfifo-r1 | pub->router | info | 181776 | 0 / 0 (9.09) | 0 / 0 | ok | 113521 | 0.9978 (0.7725) | -9.18 / 5.67 | nan (0) | ok |
| v3-G2-calm-access-pfifo-r1 | ra->sub-a | info | 15260 | 0 / 0 (3) | 0 / 0 | ok | 348 | 0.5058 (0.5058) | -406.14 / 1.99 | nan (0) | not evaluated |
| v3-G2-calm-access-pfifo-r1 | rb->sub-b | info | 34013 | 0 / 0 (3) | 0 / 0 | ok | 10899 | 0.9940 (0.9940) | -5.01 / 3.34 | nan (0) | ok |
| v3-G2-calm-access-pfifo-r1 | rc->sub-c | info | 33912 | 0 / 0 (3) | 0 / 0 | ok | 8174 | 0.9916 (0.9916) | -8.41 / 3.44 | nan (0) | ok |
| v3-G2-calm-access-pfifo-r1 | rd->sub-d | info | 64736 | 0 / 0 (3.24) | 0 / 0 | ok | 37579 | 0.9952 (0.9952) | -4.38 / 3.54 | 1.0 (17) | ok |
| v3-G2-calm-access-pfifo-r1 | router->sub-ctrl | info | 33889 | 0 / 0 (3) | 0 / 0 | ok | 18596 | 0.8874 (0.8873) | -200.37 / 2.87 | nan (0) | FAIL |
| v3-G2-calm-access-pfifo-r1 | router->switch | target | 466972 | 0 / 0 (23.35) | 0 / 0 | ok | 272227 | 0.9993 (0.9984) | -2.6 / 2.61 | 1.0 (399) | ok |
| v3-G2-calm-rev-pfifo-r1 | pub->r0 | info | 181999 | 0 / 0 (9.1) | 0 / 0 | ok | 113918 | 0.9992 (0.7860) | -9.2 / 2.99 | nan (0) | ok |
| v3-G2-calm-rev-pfifo-r1 | r0->sub-ctrl | info | 33882 | 0 / 0 (3) | 0 / 0 | ok | 18394 | 0.8337 (0.8337) | -200.18 / 1.94 | nan (0) | FAIL |
| v3-G2-calm-rev-pfifo-r1 | r0->r1 | info | 148124 | 0 / 0 (7.41) | 0 / 0 | ok | 132273 | 0.9999 (0.9986) | -2.26 / 2.26 | 1.0 (1) | ok |
| v3-G2-calm-rev-pfifo-r1 | r1->switch | target | 467214 | 0 / 0 (23.36) | 0 / 0 | ok | 271085 | 0.9997 (0.9993) | -2.01 / 2.04 | 1.0 (409) | ok |
| v3-G2-calm-split4-pfifo-r1 | pub->r1 | info | 292803 | 0 / 0 (14.64) | 0 / 0 | ok | 195154 | 0.9995 (0.8025) | -8.89 / 3.74 | nan (0) | ok |
| v3-G2-calm-split4-pfifo-r1 | r1->sub-ctrl | info | 33998 | 0 / 0 (3) | 0 / 0 | ok | 18577 | 0.8822 (0.8821) | -201.18 / 2.08 | nan (0) | FAIL |
| v3-G2-calm-split4-pfifo-r1 | r1->r2 | target | 809463 | 0 / 0 (40.47) | 0 / 0 | ok | 482101 | 0.9994 (0.9974) | -2.28 / 2.29 | 1.0 (382) | ok |
| v3-G2-calm-split4-pfifo-r1 | r2->switch-a | target | 406002 | 0 / 0 (20.3) | 0 / 0 | ok | 225962 | 0.9996 (0.9993) | -2.27 / 2.29 | 1.0 (379) | ok |
| v3-G2-calm-split4-pfifo-r1 | r2->switch-b | target | 405178 | 0 / 0 (20.26) | 0 / 0 | ok | 224711 | 0.9997 (0.9993) | -2.23 / 2.23 | 1.0 (389) | ok |
| v3-G2-calm-tree16-pfifo-r1 | pub->rr | info | 328512 | 0 / 0 (16.43) | 0 / 0 | ok | 195240 | 0.9939 (0.5767) | -9.12 / 11.98 | nan (0) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r0->r1 | target | 438546 | 0 / 0 (21.93) | 0 / 0 | ok | 246839 | 0.9987 (0.9963) | -4.49 / 4.31 | 1.0 (400) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r0->r2 | target | 437938 | 0 / 0 (21.9) | 0 / 0 | ok | 244703 | 0.9987 (0.9964) | -4.45 / 4.23 | 1.0 (393) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r1->switch-a | target | 218879 | 2 / 0 (10.94) | 2 / 0 | ok | 103423 | 0.9990 (0.9986) | -4.3 / 4.12 | 1.0 (340) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r1->switch-b | target | 218573 | 0 / 0 (10.93) | 0 / 0 | ok | 103530 | 0.9990 (0.9985) | -4.29 / 4.09 | 1.0 (322) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r2->switch-c | target | 219564 | 0 / 0 (10.98) | 0 / 0 | ok | 106189 | 0.9990 (0.9985) | -4.37 / 4.11 | 1.0 (360) | ok |
| v3-G2-calm-tree16-pfifo-r1 | r2->switch-d | target | 218509 | 0 / 0 (10.93) | 0 / 0 | ok | 108874 | 0.9994 (0.9989) | -4.29 / 4.14 | 1.0 (337) | ok |
| v3-G2-calm-tree16-pfifo-r1 | rr->sub-ctrl | info | 33912 | 0 / 0 (3) | 0 / 0 | ok | 20628 | 0.9048 (0.9046) | -199.85 / 3.07 | nan (0) | FAIL |
| v3-G2-calm-tree16-pfifo-r1 | rr->r0 | target | 874249 | 0 / 0 (43.71) | 0 / 0 | ok | 528086 | 0.9979 (0.9895) | -4.61 / 4.63 | 1.0 (382) | ok |
| v3-G2-calm-uneven-pfifo-r1 | pub->r1 | info | 502317 | 0 / 0 (25.12) | 0 / 0 | ok | 412477 | 0.9987 (0.6649) | -9.01 / 7.27 | nan (0) | ok |
| v3-G2-calm-uneven-pfifo-r1 | r1->sub-ctrl | info | 33989 | 0 / 0 (3) | 0 / 0 | ok | 19795 | 0.9149 (0.9148) | -200.49 / 1.91 | nan (0) | FAIL |
| v3-G2-calm-uneven-pfifo-r1 | r1->r2 | info | 468339 | 0 / 0 (23.42) | 0 / 0 | ok | 5634 | 0.9997 (0.5818) | -3.96 / 4.56 | nan (0) | ok |
| v3-G2-calm-uneven-pfifo-r1 | r2->switch-a | target | 316329 | 0 / 0 (15.82) | 0 / 0 | ok | 180769 | 0.9998 (0.9996) | -3.62 / 3.35 | 1.0 (401) | ok |
| v3-G2-calm-uneven-pfifo-r1 | r2->switch-b | target | 429851 | 0 / 0 (21.49) | 0 / 0 | ok | 250452 | 0.9996 (0.9987) | -3.67 / 3.51 | 1.0 (414) | ok |
| v3-G2-calm-uneven-pfifo-r1 | r2->switch-c | target | 709615 | 0 / 0 (35.48) | 0 / 0 | ok | 421457 | 0.9993 (0.9971) | -3.37 / 3.24 | 1.0 (381) | ok |
| v3-G3-sburst-s030u070-fq_codel-r1 | pub->router | info | 482372 | 0 / 0 (24.12) | 0 / 0 | ok | 206830 | 0.9995 (0.7090) | -9.66 / 2.89 | nan (0) | ok |
| v3-G3-sburst-s030u070-fq_codel-r1 | router->sub-ctrl | info | 94687 | 1 / 0 (4.73) | 1 / 0 | ok | 66867 | 0.9071 (0.9071) | -199.62 / 1.69 | nan (0) | FAIL |
| v3-G3-sburst-s030u070-fq_codel-r1 | router->switch | target | 1470595 | 0 / 0 (73.53) | 0 / 0 | ok | 918376 | 0.9998 (0.9992) | -3.0 / 3.04 | 1.0 (705) | ok |
| v3-G3-sburst-s030u070-pfifo-r1 | pub->router | info | 482655 | 0 / 0 (24.13) | 0 / 0 | ok | 183916 | 0.9998 (0.7891) | -9.52 / 1.8 | nan (0) | ok |
| v3-G3-sburst-s030u070-pfifo-r1 | router->sub-ctrl | info | 94395 | 0 / 0 (4.72) | 0 / 0 | ok | 61275 | 0.8931 (0.8931) | -201.43 / 1.37 | nan (0) | FAIL |
| v3-G3-sburst-s030u070-pfifo-r1 | router->switch | target | 1466716 | 0 / 0 (73.34) | 0 / 0 | ok | 1080766 | 0.9998 (0.9998) | -1.44 / 1.49 | 1.0 (5822) | ok |
| v3-M1-sburst-q100-pfifo-r1 | pub->router | info | 475594 | 0 / 0 (23.78) | 0 / 0 | ok | 167912 | 0.9999 (0.7730) | -9.51 / 1.85 | nan (0) | ok |
| v3-M1-sburst-q100-pfifo-r1 | router->sub-ctrl | info | 94214 | 0 / 0 (4.71) | 0 / 0 | ok | 61881 | 0.9131 (0.9130) | -200.74 / 1.48 | nan (0) | FAIL |
| v3-M1-sburst-q100-pfifo-r1 | router->switch | target | 1472767 | 0 / 0 (73.64) | 0 / 0 | ok | 1094612 | 0.9998 (0.9997) | -1.43 / 1.49 | 1.0 (5973) | ok |
| v3-M1-sburst-q100-pfifo-r2 | pub->router | info | 479869 | 0 / 0 (23.99) | 0 / 0 | ok | 171740 | 0.9997 (0.7384) | -9.63 / 2.14 | nan (0) | ok |
| v3-M1-sburst-q100-pfifo-r2 | router->sub-ctrl | info | 96736 | 0 / 0 (4.84) | 0 / 0 | ok | 66455 | 0.8740 (0.8740) | -201.22 / 1.36 | 1.0 (1) | FAIL |
| v3-M1-sburst-q100-pfifo-r2 | router->switch | target | 1504951 | 0 / 0 (75.25) | 0 / 0 | ok | 1110508 | 0.9998 (0.9997) | -1.45 / 1.49 | 1.0 (5985) | ok |
| v3-M1-sburst-q300-pfifo-r1 | pub->router | info | 462903 | 0 / 0 (23.15) | 0 / 0 | ok | 203185 | 0.9999 (0.8399) | -9.49 / 1.67 | nan (0) | ok |
| v3-M1-sburst-q300-pfifo-r1 | router->sub-ctrl | info | 94412 | 1 / 0 (4.72) | 1 / 0 | ok | 61884 | 0.9233 (0.9232) | -200.92 / 1.38 | nan (0) | FAIL |
| v3-M1-sburst-q300-pfifo-r1 | router->switch | target | 1483951 | 0 / 0 (74.2) | 0 / 0 | ok | 1121679 | 0.9999 (0.9998) | -1.44 / 1.49 | 1.0 (6380) | ok |
| v3-M1-sburst-q300-pfifo-r2 | pub->router | info | 474672 | 0 / 0 (23.73) | 0 / 0 | ok | 183396 | 0.9999 (0.8065) | -9.5 / 1.92 | nan (0) | ok |
| v3-M1-sburst-q300-pfifo-r2 | router->sub-ctrl | info | 96898 | 1 / 0 (4.84) | 1 / 0 | ok | 65674 | 0.9121 (0.9121) | -200.92 / 1.46 | nan (0) | FAIL |
| v3-M1-sburst-q300-pfifo-r2 | router->switch | target | 1516977 | 0 / 0 (75.85) | 0 / 0 | ok | 1134382 | 0.9998 (0.9997) | -1.42 / 1.48 | 1.0 (6305) | ok |
| v3-M10-sburst-ip2-pfifo-r1 | pub->router | info | 480338 | 0 / 0 (24.02) | 0 / 0 | ok | 159165 | 0.9998 (0.7434) | -9.63 / 1.91 | nan (0) | ok |
| v3-M10-sburst-ip2-pfifo-r1 | router->sub-ctrl | info | 94244 | 0 / 0 (4.71) | 0 / 0 | ok | 56620 | 0.8441 (0.8441) | -201.43 / 1.42 | nan (0) | FAIL |
| v3-M10-sburst-ip2-pfifo-r1 | router->switch | target | 1469134 | 0 / 0 (73.46) | 0 / 0 | ok | 1081701 | 0.9998 (0.9997) | -1.45 / 1.52 | 1.0 (5488) | ok |
| v3-M10-sburst-ip2-pfifo-r2 | pub->router | info | 490499 | 0 / 0 (24.52) | 0 / 0 | ok | 200218 | 0.9999 (0.7809) | -9.54 / 1.94 | nan (0) | ok |
| v3-M10-sburst-ip2-pfifo-r2 | router->sub-ctrl | info | 96713 | 0 / 0 (4.84) | 0 / 0 | ok | 70042 | 0.8899 (0.8898) | -200.79 / 1.51 | nan (0) | FAIL |
| v3-M10-sburst-ip2-pfifo-r2 | router->switch | target | 1501156 | 0 / 0 (75.06) | 0 / 0 | ok | 1096976 | 0.9998 (0.9997) | -1.45 / 1.49 | 1.0 (5524) | ok |
| v3-M10-sburst-ip8-pfifo-r1 | pub->router | info | 489290 | 0 / 0 (24.46) | 0 / 0 | ok | 174343 | 0.9998 (0.7747) | -9.51 / 1.86 | nan (0) | ok |
| v3-M10-sburst-ip8-pfifo-r1 | router->sub-ctrl | info | 94538 | 1 / 0 (4.73) | 1 / 0 | ok | 65909 | 0.9192 (0.9192) | -200.65 / 1.81 | 1.0 (1) | FAIL |
| v3-M10-sburst-ip8-pfifo-r1 | router->switch | target | 1465427 | 0 / 0 (73.27) | 0 / 0 | ok | 1079779 | 0.9998 (0.9998) | -1.43 / 1.48 | 1.0 (6372) | ok |
| v3-M10-sburst-ip8-pfifo-r2 | pub->router | info | 496039 | 0 / 0 (24.8) | 0 / 0 | ok | 207812 | 0.9999 (0.8004) | -9.52 / 1.89 | nan (0) | ok |
| v3-M10-sburst-ip8-pfifo-r2 | router->sub-ctrl | info | 96837 | 1 / 0 (4.84) | 1 / 0 | ok | 68538 | 0.9169 (0.9169) | -201.09 / 1.54 | 1.0 (5) | FAIL |
| v3-M10-sburst-ip8-pfifo-r2 | router->switch | target | 1497124 | 0 / 0 (74.86) | 0 / 0 | ok | 1094483 | 0.9998 (0.9997) | -1.46 / 1.5 | 1.0 (6368) | ok |
| v3-M11-sburst-bw4x1-pfifo-r1 | pub->router | info | 262022 | 0 / 0 (13.1) | 0 / 0 | ok | 97728 | 0.9998 (0.7504) | -9.8 / 1.89 | nan (0) | ok |
| v3-M11-sburst-bw4x1-pfifo-r1 | router->sub-ctrl | info | 94553 | 0 / 0 (4.73) | 0 / 0 | ok | 64261 | 0.8889 (0.8888) | -201.42 / 1.36 | nan (0) | FAIL |
| v3-M11-sburst-bw4x1-pfifo-r1 | router->switch | target | 266588 | 0 / 0 (13.33) | 0 / 0 | ok | 221266 | 1.0000 (0.9999) | -2.46 / 2.67 | 0.96288 (7812) | FAIL |
| v3-M11-sburst-bw4x1-pfifo-r2 | pub->router | info | 268143 | 0 / 0 (13.41) | 0 / 0 | ok | 101504 | 0.9998 (0.8007) | -9.68 / 1.52 | nan (0) | ok |
| v3-M11-sburst-bw4x1-pfifo-r2 | router->sub-ctrl | info | 96682 | 1 / 0 (4.83) | 1 / 0 | ok | 65951 | 0.9003 (0.9003) | -201.11 / 1.66 | nan (0) | FAIL |
| v3-M11-sburst-bw4x1-pfifo-r2 | router->switch | target | 273046 | 0 / 0 (13.65) | 0 / 0 | ok | 226630 | 0.9999 (0.9999) | -2.56 / 2.9 | 0.96122 (7968) | FAIL |
| v3-M11-sburst-bw4x12-pfifo-r1 | pub->router | info | 825810 | 0 / 0 (41.29) | 0 / 0 | ok | 282532 | 0.9999 (0.7950) | -9.34 / 1.72 | nan (0) | ok |
| v3-M11-sburst-bw4x12-pfifo-r1 | router->sub-ctrl | info | 94311 | 0 / 0 (4.72) | 0 / 0 | ok | 53608 | 0.8708 (0.8708) | -201.41 / 1.63 | nan (0) | FAIL |
| v3-M11-sburst-bw4x12-pfifo-r1 | router->switch | target | 1272511 | 0 / 0 (63.63) | 0 / 0 | ok | 1140886 | 0.9999 (0.9998) | -1.58 / 1.64 | 1.0 (8173) | ok |
| v3-M11-sburst-bw4x12-pfifo-r2 | pub->router | info | 843577 | 0 / 0 (42.18) | 0 / 0 | ok | 295576 | 0.9999 (0.7889) | -9.33 / 1.82 | nan (0) | ok |
| v3-M11-sburst-bw4x12-pfifo-r2 | router->sub-ctrl | info | 96825 | 1 / 0 (4.84) | 1 / 0 | ok | 65580 | 0.9245 (0.9244) | -200.95 / 1.52 | nan (0) | FAIL |
| v3-M11-sburst-bw4x12-pfifo-r2 | router->switch | target | 1301327 | 0 / 0 (65.07) | 0 / 0 | ok | 1161075 | 0.9999 (0.9998) | -1.61 / 1.67 | 1.0 (8081) | ok |
| v3-M11-sburst-bw4x8-pfifo-r1 | pub->router | info | 1205827 | 0 / 0 (60.29) | 0 / 0 | ok | 416830 | 0.9998 (0.8069) | -9.24 / 1.81 | nan (0) | ok |
| v3-M11-sburst-bw4x8-pfifo-r1 | router->sub-ctrl | info | 94315 | 0 / 0 (4.72) | 0 / 0 | ok | 60314 | 0.8835 (0.8835) | -201.28 / 1.67 | nan (0) | FAIL |
| v3-M11-sburst-bw4x8-pfifo-r1 | router->switch | target | 1973678 | 0 / 0 (98.68) | 0 / 0 | ok | 1790104 | 0.9998 (0.9998) | -1.53 / 1.58 | 1.0 (8591) | ok |
| v3-M11-sburst-bw4x8-pfifo-r2 | pub->router | info | 1236147 | 0 / 0 (61.81) | 0 / 0 | ok | 456103 | 0.9999 (0.8181) | -9.2 / 1.77 | nan (0) | ok |
| v3-M11-sburst-bw4x8-pfifo-r2 | router->sub-ctrl | info | 96732 | 0 / 0 (4.84) | 0 / 0 | ok | 58955 | 0.9242 (0.9242) | -201.07 / 1.67 | nan (0) | FAIL |
| v3-M11-sburst-bw4x8-pfifo-r2 | router->switch | target | 2020247 | 0 / 0 (101.01) | 0 / 0 | ok | 1829346 | 0.9999 (0.9998) | -1.53 / 1.57 | 1.0 (8816) | ok |
| v3-M12-sburst-jitfwd-pfifo-r1 | pub->router | info | 475005 | 0 / 0 (23.75) | 0 / 0 | ok | 192140 | 0.9998 (0.7886) | -9.56 / 2.08 | nan (0) | ok |
| v3-M12-sburst-jitfwd-pfifo-r1 | router->sub-ctrl | info | 94551 | 0 / 0 (4.73) | 0 / 0 | ok | 61152 | 0.8955 (0.8955) | -201.57 / 1.42 | nan (0) | FAIL |
| v3-M12-sburst-jitfwd-pfifo-r1 | router->switch | target | 1469437 | 0 / 0 (73.47) | 0 / 0 | ok | 1088090 | 0.9998 (0.9997) | -1.47 / 1.52 | 1.0 (5884) | ok |
| v3-M12-sburst-jitfwd-pfifo-r2 | pub->router | info | 489428 | 0 / 0 (24.47) | 0 / 0 | ok | 201756 | 0.9998 (0.8044) | -9.47 / 2.01 | nan (0) | ok |
| v3-M12-sburst-jitfwd-pfifo-r2 | router->sub-ctrl | info | 96693 | 0 / 0 (4.83) | 0 / 0 | ok | 59309 | 0.9062 (0.9061) | -201.36 / 1.27 | 1.0 (1) | FAIL |
| v3-M12-sburst-jitfwd-pfifo-r2 | router->switch | target | 1501193 | 0 / 0 (75.06) | 0 / 0 | ok | 1103977 | 0.9998 (0.9997) | -1.44 / 1.48 | 1.0 (5876) | ok |
| v3-M12-sburst-jitrev-pfifo-r1 | pub->router | info | 487509 | 0 / 0 (24.38) | 0 / 0 | ok | 193987 | 0.9998 (0.7945) | -9.47 / 1.94 | nan (0) | ok |
| v3-M12-sburst-jitrev-pfifo-r1 | router->sub-ctrl | info | 94564 | 0 / 0 (4.73) | 0 / 0 | ok | 64214 | 0.9125 (0.9124) | -201.17 / 1.41 | nan (0) | FAIL |
| v3-M12-sburst-jitrev-pfifo-r1 | router->switch | target | 1470021 | 0 / 0 (73.5) | 0 / 0 | ok | 1096668 | 0.9999 (0.9997) | -1.45 / 1.51 | 1.0 (5991) | ok |
| v3-M12-sburst-jitrev-pfifo-r2 | pub->router | info | 503770 | 0 / 0 (25.19) | 0 / 0 | ok | 201611 | 0.9999 (0.8022) | -9.5 / 1.85 | nan (0) | ok |
| v3-M12-sburst-jitrev-pfifo-r2 | router->sub-ctrl | info | 96723 | 1 / 0 (4.84) | 1 / 0 | ok | 68651 | 0.8838 (0.8838) | -200.92 / 1.44 | nan (0) | FAIL |
| v3-M12-sburst-jitrev-pfifo-r2 | router->switch | target | 1502584 | 0 / 0 (75.13) | 0 / 0 | ok | 1112283 | 0.9999 (0.9997) | -1.47 / 1.51 | 1.0 (5961) | ok |
| v3-M13-sburst-copa-codel-r1 | pub->router | info | 472577 | 0 / 0 (23.63) | 0 / 0 | ok | 305774 | 0.9999 (0.8906) | -9.16 / 1.75 | nan (0) | ok |
| v3-M13-sburst-copa-codel-r1 | router->sub-ctrl | info | 94590 | 0 / 0 (4.73) | 0 / 0 | ok | 65677 | 0.9217 (0.9216) | -200.7 / 1.53 | nan (0) | FAIL |
| v3-M13-sburst-copa-codel-r1 | router->switch | target | 1482003 | 0 / 0 (74.1) | 0 / 0 | ok | 1123993 | 0.9999 (0.9996) | -2.36 / 2.37 | 1.0 (6341) | ok |
| v3-M13-sburst-copa-codel-r2 | pub->router | info | 485536 | 0 / 0 (24.28) | 0 / 0 | ok | 325738 | 0.9999 (0.8807) | -9.24 / 1.75 | nan (0) | ok |
| v3-M13-sburst-copa-codel-r2 | router->sub-ctrl | info | 97012 | 1 / 0 (4.85) | 1 / 0 | ok | 69916 | 0.8931 (0.8930) | -200.97 / 1.44 | nan (0) | FAIL |
| v3-M13-sburst-copa-codel-r2 | router->switch | target | 1515496 | 0 / 0 (75.77) | 0 / 0 | ok | 1142292 | 0.9999 (0.9996) | -2.43 / 2.43 | 1.0 (6319) | ok |
| v3-M13-sburst-copa-pfifo-r1 | pub->router | info | 549175 | 0 / 0 (27.46) | 0 / 0 | ok | 345669 | 0.9999 (0.8868) | -9.12 / 1.73 | nan (0) | ok |
| v3-M13-sburst-copa-pfifo-r1 | router->sub-ctrl | info | 94612 | 0 / 0 (4.73) | 0 / 0 | ok | 67321 | 0.9041 (0.9041) | -200.78 / 1.43 | nan (0) | FAIL |
| v3-M13-sburst-copa-pfifo-r1 | router->switch | target | 1475434 | 0 / 0 (73.77) | 0 / 0 | ok | 1112422 | 0.9999 (0.9998) | -1.41 / 1.47 | 1.0 (6166) | ok |
| v3-M13-sburst-copa-pfifo-r2 | pub->router | info | 564769 | 0 / 0 (28.24) | 0 / 0 | ok | 340647 | 0.9999 (0.8697) | -9.19 / 1.92 | nan (0) | ok |
| v3-M13-sburst-copa-pfifo-r2 | router->sub-ctrl | info | 97046 | 0 / 0 (4.85) | 0 / 0 | ok | 67318 | 0.9250 (0.9250) | -201.04 / 1.37 | nan (0) | FAIL |
| v3-M13-sburst-copa-pfifo-r2 | router->switch | target | 1508008 | 0 / 0 (75.4) | 0 / 0 | ok | 1127405 | 0.9999 (0.9998) | -1.5 / 1.55 | 1.0 (6126) | ok |
| v3-M14-ssparse-s030u070-pfifo-r1 | pub->router | info | 844368 | 0 / 0 (42.22) | 0 / 0 | ok | 325947 | 0.9998 (0.7885) | -9.5 / 1.96 | nan (0) | ok |
| v3-M14-ssparse-s030u070-pfifo-r1 | router->sub-ctrl | info | 159162 | 0 / 0 (7.96) | 0 / 0 | ok | 113814 | 0.8927 (0.8926) | -201.0 / 1.53 | nan (0) | FAIL |
| v3-M14-ssparse-s030u070-pfifo-r1 | router->switch | target | 2277101 | 0 / 0 (113.86) | 0 / 0 | ok | 1439681 | 0.9998 (0.9997) | -1.52 / 1.56 | 1.0 (4173) | ok |
| v3-M14-ssparse-s030u070-pfifo-r2 | pub->router | info | 841438 | 0 / 0 (42.07) | 0 / 0 | ok | 315081 | 0.9999 (0.7872) | -9.51 / 1.83 | nan (0) | ok |
| v3-M14-ssparse-s030u070-pfifo-r2 | router->sub-ctrl | info | 159803 | 1 / 0 (7.99) | 1 / 0 | ok | 110663 | 0.8915 (0.8915) | -201.0 / 1.53 | nan (0) | FAIL |
| v3-M14-ssparse-s030u070-pfifo-r2 | router->switch | target | 2291934 | 0 / 0 (114.6) | 0 / 0 | ok | 1443965 | 0.9998 (0.9997) | -1.54 / 1.58 | 1.0 (4154) | ok |
| v3-M2-sburst-capdrop-codel-r1 | pub->router | info | 486406 | 0 / 0 (24.32) | 0 / 0 | ok | 200752 | 0.9999 (0.8253) | -9.45 / 1.78 | nan (0) | ok |
| v3-M2-sburst-capdrop-codel-r1 | router->sub-ctrl | info | 94293 | 0 / 0 (4.71) | 0 / 0 | ok | 60313 | 0.9114 (0.9114) | -200.92 / 1.55 | nan (0) | FAIL |
| v3-M2-sburst-capdrop-codel-r1 | router->switch | target | 1256673 | 0 / 0 (62.83) | 0 / 0 | ok | 886429 | 0.9996 (0.9994) | -2.61 / 2.61 | 1.0 (6052) | ok |
| v3-M2-sburst-capdrop-codel-r2 | pub->router | info | 494338 | 0 / 0 (24.72) | 0 / 0 | ok | 185912 | 0.9998 (0.7894) | -9.51 / 1.87 | nan (0) | ok |
| v3-M2-sburst-capdrop-codel-r2 | router->sub-ctrl | info | 96804 | 0 / 0 (4.84) | 0 / 0 | ok | 65977 | 0.9217 (0.9217) | -200.63 / 1.44 | nan (0) | FAIL |
| v3-M2-sburst-capdrop-codel-r2 | router->switch | target | 1290346 | 0 / 0 (64.52) | 0 / 0 | ok | 905413 | 0.9996 (0.9994) | -2.62 / 2.62 | 0.99984 (6061) | ok |
| v3-M2-sburst-capdrop-pfifo-r1 | pub->router | info | 491949 | 0 / 0 (24.6) | 0 / 0 | ok | 172952 | 0.9999 (0.7808) | -9.52 / 1.8 | nan (0) | ok |
| v3-M2-sburst-capdrop-pfifo-r1 | router->sub-ctrl | info | 94233 | 0 / 0 (4.71) | 0 / 0 | ok | 53961 | 0.8976 (0.8974) | -201.11 / 1.62 | nan (0) | FAIL |
| v3-M2-sburst-capdrop-pfifo-r1 | router->switch | target | 1251146 | 0 / 0 (62.56) | 0 / 0 | ok | 872767 | 0.9996 (0.9995) | -1.5 / 1.56 | 1.0 (5860) | ok |
| v3-M2-sburst-capdrop-pfifo-r2 | pub->router | info | 501569 | 0 / 0 (25.08) | 0 / 0 | ok | 166415 | 0.9998 (0.7578) | -9.55 / 1.77 | nan (0) | ok |
| v3-M2-sburst-capdrop-pfifo-r2 | router->sub-ctrl | info | 96465 | 0 / 0 (4.82) | 0 / 0 | ok | 53112 | 0.8420 (0.8420) | -201.5 / 1.51 | nan (0) | FAIL |
| v3-M2-sburst-capdrop-pfifo-r2 | router->switch | target | 1286688 | 0 / 0 (64.33) | 0 / 0 | ok | 894503 | 0.9996 (0.9996) | -1.55 / 1.6 | 0.99983 (5879) | ok |
| v3-M3-sburst-bgbursty-codel-r1 | pub->router | info | 486444 | 0 / 0 (24.32) | 0 / 0 | ok | 198167 | 0.9999 (0.8003) | -9.5 / 1.79 | nan (0) | ok |
| v3-M3-sburst-bgbursty-codel-r1 | router->sub-ctrl | info | 94427 | 0 / 0 (4.72) | 0 / 0 | ok | 60897 | 0.8928 (0.8928) | -201.35 / 1.37 | nan (0) | FAIL |
| v3-M3-sburst-bgbursty-codel-r1 | router->switch | target | 1389321 | 0 / 0 (69.47) | 0 / 0 | ok | 1030069 | 0.9999 (0.9997) | -2.32 / 2.33 | 1.0 (5758) | ok |
| v3-M3-sburst-bgbursty-codel-r2 | pub->router | info | 483994 | 0 / 0 (24.2) | 0 / 0 | ok | 166452 | 0.9998 (0.7645) | -9.52 / 1.82 | nan (0) | ok |
| v3-M3-sburst-bgbursty-codel-r2 | router->sub-ctrl | info | 96667 | 0 / 0 (4.83) | 0 / 0 | ok | 62877 | 0.8759 (0.8759) | -200.9 / 1.76 | nan (0) | FAIL |
| v3-M3-sburst-bgbursty-codel-r2 | router->switch | target | 1505713 | 0 / 0 (75.29) | 0 / 0 | ok | 1156410 | 0.9999 (0.9997) | -2.4 / 2.42 | 1.0 (6741) | ok |
| v3-M3-sburst-bgbursty-pfifo-r1 | pub->router | info | 484061 | 0 / 0 (24.2) | 0 / 0 | ok | 182865 | 0.9999 (0.7877) | -9.49 / 1.75 | nan (0) | ok |
| v3-M3-sburst-bgbursty-pfifo-r1 | router->sub-ctrl | info | 94511 | 0 / 0 (4.73) | 0 / 0 | ok | 66184 | 0.9194 (0.9194) | -200.76 / 1.44 | nan (0) | FAIL |
| v3-M3-sburst-bgbursty-pfifo-r1 | router->switch | target | 1380088 | 0 / 0 (69) | 0 / 0 | ok | 1009020 | 0.9999 (0.9998) | -1.47 / 1.51 | 1.0 (5503) | ok |
| v3-M3-sburst-bgbursty-pfifo-r2 | pub->router | info | 500792 | 0 / 0 (25.04) | 0 / 0 | ok | 207273 | 0.9999 (0.8077) | -9.48 / 1.84 | nan (0) | ok |
| v3-M3-sburst-bgbursty-pfifo-r2 | router->sub-ctrl | info | 96571 | 0 / 0 (4.83) | 0 / 0 | ok | 63119 | 0.9108 (0.9108) | -201.22 / 1.35 | nan (0) | FAIL |
| v3-M3-sburst-bgbursty-pfifo-r2 | router->switch | target | 1496386 | 0 / 0 (74.82) | 0 / 0 | ok | 1134562 | 0.9999 (0.9997) | -1.48 / 1.54 | 1.0 (6491) | ok |
| v3-M3-sburst-bgmix-codel-r1 | pub->router | info | 500202 | 0 / 0 (25.01) | 0 / 0 | ok | 200430 | 0.9999 (0.8340) | -9.38 / 1.79 | nan (0) | ok |
| v3-M3-sburst-bgmix-codel-r1 | router->sub-ctrl | info | 94411 | 0 / 0 (4.72) | 0 / 0 | ok | 53026 | 0.9022 (0.9021) | -200.93 / 1.46 | nan (0) | FAIL |
| v3-M3-sburst-bgmix-codel-r1 | router->switch | target | 1445867 | 0 / 0 (72.29) | 0 / 0 | ok | 1153064 | 0.9977 (0.9974) | -2.59 / 2.37 | 1.0 (6389) | ok |
| v3-M3-sburst-bgmix-codel-r2 | pub->router | info | 512082 | 0 / 0 (25.6) | 0 / 0 | ok | 196420 | 0.9999 (0.8259) | -9.33 / 1.68 | nan (0) | ok |
| v3-M3-sburst-bgmix-codel-r2 | router->sub-ctrl | info | 96823 | 1 / 0 (4.84) | 1 / 0 | ok | 64057 | 0.9063 (0.9063) | -201.15 / 1.54 | nan (0) | FAIL |
| v3-M3-sburst-bgmix-codel-r2 | router->switch | target | 1480314 | 0 / 0 (74.02) | 0 / 0 | ok | 1161807 | 0.9973 (0.9971) | -2.65 / 2.38 | 1.0 (6305) | ok |
| v3-M3-sburst-bgmix-pfifo-r1 | pub->router | info | 499490 | 0 / 0 (24.97) | 0 / 0 | ok | 166356 | 0.9999 (0.7870) | -9.44 / 1.74 | nan (0) | ok |
| v3-M3-sburst-bgmix-pfifo-r1 | router->sub-ctrl | info | 94346 | 0 / 0 (4.72) | 0 / 0 | ok | 60533 | 0.8850 (0.8850) | -201.05 / 1.74 | nan (0) | FAIL |
| v3-M3-sburst-bgmix-pfifo-r1 | router->switch | target | 1440555 | 0 / 0 (72.03) | 0 / 0 | ok | 1136793 | 0.9975 (0.9974) | -1.69 / 1.52 | 1.0 (6185) | ok |
| v3-M3-sburst-bgmix-pfifo-r2 | pub->router | info | 511693 | 0 / 0 (25.58) | 0 / 0 | ok | 199071 | 0.9999 (0.7937) | -9.48 / 1.88 | nan (0) | ok |
| v3-M3-sburst-bgmix-pfifo-r2 | router->sub-ctrl | info | 96839 | 0 / 0 (4.84) | 0 / 0 | ok | 64706 | 0.9044 (0.9044) | -201.3 / 1.41 | nan (0) | FAIL |
| v3-M3-sburst-bgmix-pfifo-r2 | router->switch | target | 1473578 | 0 / 0 (73.68) | 0 / 0 | ok | 1142086 | 0.9974 (0.9973) | -1.71 / 1.55 | 1.0 (6108) | ok |
| v3-M4-sburst-rttwide-pfifo-r1 | pub->router | info | 467895 | 0 / 0 (23.39) | 0 / 0 | ok | 195553 | 0.9999 (0.7950) | -9.54 / 1.83 | nan (0) | ok |
| v3-M4-sburst-rttwide-pfifo-r1 | router->sub-ctrl | info | 94070 | 0 / 0 (4.7) | 0 / 0 | ok | 57006 | 0.8849 (0.8849) | -201.81 / 1.27 | nan (0) | FAIL |
| v3-M4-sburst-rttwide-pfifo-r1 | router->switch | target | 1464937 | 0 / 0 (73.25) | 0 / 0 | ok | 1066809 | 0.9998 (0.9997) | -1.43 / 1.48 | 1.0 (5854) | ok |
| v3-M4-sburst-rttwide-pfifo-r2 | pub->router | info | 482487 | 0 / 0 (24.12) | 0 / 0 | ok | 170390 | 0.9997 (0.7531) | -9.59 / 1.89 | nan (0) | ok |
| v3-M4-sburst-rttwide-pfifo-r2 | router->sub-ctrl | info | 96726 | 1 / 0 (4.84) | 1 / 0 | ok | 63326 | 0.8975 (0.8975) | -201.27 / 1.32 | nan (0) | FAIL |
| v3-M4-sburst-rttwide-pfifo-r2 | router->switch | target | 1501591 | 0 / 0 (75.08) | 0 / 0 | ok | 1089020 | 0.9998 (0.9997) | -1.48 / 1.55 | 1.0 (5869) | ok |
| v3-M4-sburst-rttx05-pfifo-r1 | pub->router | info | 497830 | 0 / 0 (24.89) | 0 / 0 | ok | 222873 | 0.9999 (0.8250) | -9.58 / 1.8 | nan (0) | ok |
| v3-M4-sburst-rttx05-pfifo-r1 | router->sub-ctrl | info | 94531 | 1 / 0 (4.73) | 1 / 0 | ok | 65550 | 0.9378 (0.9378) | -201.08 / 1.63 | nan (0) | FAIL |
| v3-M4-sburst-rttx05-pfifo-r1 | router->switch | target | 1465691 | 0 / 0 (73.28) | 0 / 0 | ok | 1085345 | 0.9998 (0.9997) | -1.44 / 1.48 | 1.0 (5827) | ok |
| v3-M4-sburst-rttx05-pfifo-r2 | pub->router | info | 506071 | 0 / 0 (25.3) | 0 / 0 | ok | 215850 | 0.9999 (0.8297) | -9.63 / 1.6 | nan (0) | ok |
| v3-M4-sburst-rttx05-pfifo-r2 | router->sub-ctrl | info | 96613 | 0 / 0 (4.83) | 0 / 0 | ok | 67127 | 0.9266 (0.9266) | -200.79 / 1.62 | nan (0) | FAIL |
| v3-M4-sburst-rttx05-pfifo-r2 | router->switch | target | 1500669 | 0 / 0 (75.03) | 0 / 0 | ok | 1104070 | 0.9998 (0.9998) | -1.47 / 1.53 | 1.0 (5880) | ok |
| v3-M4-sburst-rttx4-pfifo-r1 | pub->router | info | 465694 | 0 / 0 (23.28) | 0 / 0 | ok | 159247 | 0.9997 (0.6710) | -9.53 / 2.67 | nan (0) | ok |
| v3-M4-sburst-rttx4-pfifo-r1 | router->sub-ctrl | info | 92598 | 0 / 0 (4.63) | 0 / 0 | ok | 41695 | 0.7253 (0.7253) | -202.11 / 1.08 | nan (0) | FAIL |
| v3-M4-sburst-rttx4-pfifo-r1 | router->switch | target | 1469100 | 0 / 0 (73.45) | 0 / 0 | ok | 1059241 | 0.9998 (0.9997) | -1.42 / 1.45 | 1.0 (5887) | ok |
| v3-M4-sburst-rttx4-pfifo-r2 | pub->router | info | 474749 | 0 / 0 (23.74) | 0 / 0 | ok | 187908 | 0.9997 (0.7107) | -9.52 / 2.78 | nan (0) | ok |
| v3-M4-sburst-rttx4-pfifo-r2 | router->sub-ctrl | info | 95007 | 0 / 0 (4.75) | 0 / 0 | ok | 42738 | 0.7266 (0.7266) | -202.11 / 0.97 | nan (0) | FAIL |
| v3-M4-sburst-rttx4-pfifo-r2 | router->switch | target | 1500059 | 0 / 0 (75) | 0 / 0 | ok | 1065764 | 0.9998 (0.9997) | -1.41 / 1.46 | 1.0 (5825) | ok |
| v3-M5-sburst-fps15-codel-r1 | pub->router | info | 467710 | 0 / 0 (23.39) | 0 / 0 | ok | 176482 | 0.9999 (0.8222) | -9.41 / 1.68 | nan (0) | ok |
| v3-M5-sburst-fps15-codel-r1 | router->sub-ctrl | info | 94131 | 0 / 0 (4.71) | 0 / 0 | ok | 75314 | 0.9710 (0.9710) | -60.91 / 1.8 | 1.0 (2) | FAIL |
| v3-M5-sburst-fps15-codel-r1 | router->switch | target | 1471817 | 0 / 0 (73.59) | 0 / 0 | ok | 1103824 | 0.9998 (0.9997) | -2.38 / 2.38 | 1.0 (8244) | ok |
| v3-M5-sburst-fps15-codel-r2 | pub->router | info | 477455 | 0 / 0 (23.87) | 0 / 0 | ok | 176862 | 0.9999 (0.8104) | -9.38 / 1.74 | nan (0) | ok |
| v3-M5-sburst-fps15-codel-r2 | router->sub-ctrl | info | 96469 | 1 / 0 (4.82) | 1 / 0 | ok | 76988 | 0.9503 (0.9503) | -164.02 / 1.76 | 1.0 (3) | FAIL |
| v3-M5-sburst-fps15-codel-r2 | router->switch | target | 1506833 | 0 / 0 (75.34) | 0 / 0 | ok | 1128305 | 0.9999 (0.9997) | -2.41 / 2.42 | 1.0 (8437) | ok |
| v3-M5-sburst-fps15-pfifo-r1 | pub->router | info | 478571 | 0 / 0 (23.93) | 0 / 0 | ok | 167297 | 0.9998 (0.7897) | -9.4 / 1.71 | nan (0) | ok |
| v3-M5-sburst-fps15-pfifo-r1 | router->sub-ctrl | info | 94134 | 0 / 0 (4.71) | 0 / 0 | ok | 76394 | 0.9573 (0.9572) | -61.77 / 1.65 | 1.0 (1) | FAIL |
| v3-M5-sburst-fps15-pfifo-r1 | router->switch | target | 1462335 | 0 / 0 (73.12) | 0 / 0 | ok | 1084650 | 0.9998 (0.9997) | -1.46 / 1.5 | 1.0 (8017) | ok |
| v3-M5-sburst-fps15-pfifo-r2 | pub->router | info | 494312 | 0 / 0 (24.72) | 0 / 0 | ok | 176237 | 0.9998 (0.7804) | -9.43 / 1.84 | nan (0) | ok |
| v3-M5-sburst-fps15-pfifo-r2 | router->sub-ctrl | info | 96443 | 0 / 0 (4.82) | 0 / 0 | ok | 78346 | 0.9561 (0.9561) | -61.62 / 1.86 | 1.0 (5) | FAIL |
| v3-M5-sburst-fps15-pfifo-r2 | router->switch | target | 1496225 | 0 / 0 (74.81) | 0 / 0 | ok | 1103625 | 0.9999 (0.9998) | -1.47 / 1.52 | 1.0 (8098) | ok |
| v3-M5-sburst-fps60-codel-r1 | pub->router | info | 485742 | 0 / 0 (24.29) | 0 / 0 | ok | 191323 | 0.9998 (0.7245) | -9.7 / 1.86 | nan (0) | ok |
| v3-M5-sburst-fps60-codel-r1 | router->sub-ctrl | info | 97140 | 0 / 0 (4.86) | 0 / 0 | ok | 51186 | 0.6962 (0.6961) | -201.76 / 1.01 | nan (0) | FAIL |
| v3-M5-sburst-fps60-codel-r1 | router->switch | target | 1488335 | 0 / 0 (74.42) | 0 / 0 | ok | 1093303 | 0.9998 (0.9997) | -2.31 / 2.31 | 1.0 (5726) | ok |
| v3-M5-sburst-fps60-codel-r2 | pub->router | info | 494808 | 0 / 0 (24.74) | 0 / 0 | ok | 148706 | 0.9997 (0.6525) | -9.79 / 2.08 | nan (0) | ok |
| v3-M5-sburst-fps60-codel-r2 | router->sub-ctrl | info | 99403 | 0 / 0 (4.97) | 0 / 0 | ok | 53864 | 0.6673 (0.6673) | -201.38 / 1.54 | nan (0) | FAIL |
| v3-M5-sburst-fps60-codel-r2 | router->switch | target | 1520077 | 0 / 0 (76) | 0 / 0 | ok | 1106875 | 0.9998 (0.9996) | -2.4 / 2.4 | 1.0 (5731) | ok |
| v3-M5-sburst-fps60-pfifo-r1 | pub->router | info | 499127 | 0 / 0 (24.96) | 0 / 0 | ok | 184785 | 0.9999 (0.7242) | -9.7 / 1.82 | nan (0) | ok |
| v3-M5-sburst-fps60-pfifo-r1 | router->sub-ctrl | info | 97162 | 0 / 0 (4.86) | 0 / 0 | ok | 50667 | 0.7110 (0.7110) | -201.7 / 0.89 | nan (0) | FAIL |
| v3-M5-sburst-fps60-pfifo-r1 | router->switch | target | 1478878 | 0 / 0 (73.94) | 0 / 0 | ok | 1076207 | 0.9998 (0.9997) | -1.42 / 1.46 | 1.0 (5508) | ok |
| v3-M5-sburst-fps60-pfifo-r2 | pub->router | info | 505144 | 0 / 0 (25.26) | 0 / 0 | ok | 176324 | 0.9996 (0.6635) | -9.75 / 2.41 | nan (0) | ok |
| v3-M5-sburst-fps60-pfifo-r2 | router->sub-ctrl | info | 99700 | 0 / 0 (4.99) | 0 / 0 | ok | 50125 | 0.7428 (0.7427) | -201.68 / 1.13 | nan (0) | FAIL |
| v3-M5-sburst-fps60-pfifo-r2 | router->switch | target | 1510702 | 0 / 0 (75.54) | 0 / 0 | ok | 1081519 | 0.9997 (0.9996) | -1.49 / 1.49 | 1.0 (5457) | ok |
| v3-M6-calm-stag-pfifo-r1 | pub->router | info | 181419 | 0 / 0 (9.07) | 0 / 0 | ok | 105946 | 0.9998 (0.8397) | -9.58 / 1.82 | nan (0) | ok |
| v3-M6-calm-stag-pfifo-r1 | router->sub-ctrl | info | 33918 | 0 / 0 (3) | 0 / 0 | ok | 22182 | 0.9044 (0.9043) | -201.3 / 1.51 | nan (0) | FAIL |
| v3-M6-calm-stag-pfifo-r1 | router->switch | target | 466591 | 0 / 0 (23.33) | 0 / 0 | ok | 258099 | 0.9997 (0.9994) | -1.44 / 1.43 | 1.0 (275) | ok |
| v3-M6-calm-stag-pfifo-r2 | pub->router | info | 180867 | 0 / 0 (9.04) | 0 / 0 | ok | 111426 | 0.9998 (0.8450) | -9.68 / 1.91 | nan (0) | ok |
| v3-M6-calm-stag-pfifo-r2 | router->sub-ctrl | info | 33766 | 0 / 0 (3) | 0 / 0 | ok | 20861 | 0.9033 (0.9032) | -201.66 / 1.4 | nan (0) | FAIL |
| v3-M6-calm-stag-pfifo-r2 | router->switch | target | 466968 | 0 / 0 (23.35) | 0 / 0 | ok | 257938 | 0.9997 (0.9994) | -1.54 / 1.55 | 1.0 (241) | ok |
| v3-M6-sburst-stag-pfifo-r1 | pub->router | info | 477355 | 0 / 0 (23.87) | 0 / 0 | ok | 160638 | 0.9998 (0.6871) | -9.71 / 2.11 | nan (0) | ok |
| v3-M6-sburst-stag-pfifo-r1 | router->sub-ctrl | info | 94402 | 0 / 0 (4.72) | 0 / 0 | ok | 59002 | 0.8860 (0.8860) | -201.43 / 1.57 | nan (0) | FAIL |
| v3-M6-sburst-stag-pfifo-r1 | router->switch | target | 1465039 | 0 / 0 (73.25) | 0 / 0 | ok | 1002346 | 0.9997 (0.9997) | -1.4 / 1.45 | 1.0 (5319) | ok |
| v3-M6-sburst-stag-pfifo-r2 | pub->router | info | 490404 | 0 / 0 (24.52) | 0 / 0 | ok | 161602 | 0.9998 (0.6584) | -9.73 / 2.02 | nan (0) | ok |
| v3-M6-sburst-stag-pfifo-r2 | router->sub-ctrl | info | 96743 | 0 / 0 (4.84) | 0 / 0 | ok | 68346 | 0.8841 (0.8841) | -200.87 / 1.69 | nan (0) | FAIL |
| v3-M6-sburst-stag-pfifo-r2 | router->switch | target | 1499293 | 0 / 2 (74.96) | 0 / 2 | ok | 1018466 | 0.9997 (0.9995) | -1.47 / 1.51 | 1.0 (5291) | ok |
| v3-M7-hhier-noroot-pfifo-r1 | pub->r1 | info | 1568789 | 0 / 0 (78.44) | 0 / 0 | ok | 778113 | 0.9978 (0.4693) | -9.59 / 7.08 | nan (0) | ok |
| v3-M7-hhier-noroot-pfifo-r1 | r1->sub-ctrl | info | 193335 | 0 / 0 (9.67) | 0 / 0 | ok | 129765 | 0.9170 (0.9170) | -200.2 / 2.19 | nan (0) | FAIL |
| v3-M7-hhier-noroot-pfifo-r1 | r1->r2 | info | 1375486 | 0 / 0 (68.77) | 0 / 0 | ok | 3862 | 0.9992 (0.6028) | -8.34 / 5.64 | nan (0) | ok |
| v3-M7-hhier-noroot-pfifo-r1 | r2->switch-a | target | 2518367 | 0 / 0 (125.92) | 0 / 0 | ok | 1750299 | 0.9997 (0.9994) | -2.49 / 2.42 | 1.0 (9319) | ok |
| v3-M7-hhier-noroot-pfifo-r1 | r2->switch-b | target | 2514012 | 0 / 0 (125.7) | 0 / 0 | ok | 1747549 | 0.9997 (0.9994) | -2.48 / 2.39 | 1.0 (9320) | ok |
| v3-M7-hhier-noroot-pfifo-r2 | pub->r1 | info | 1542690 | 0 / 0 (77.13) | 0 / 0 | ok | 725799 | 0.9974 (0.4640) | -9.59 / 7.63 | nan (0) | ok |
| v3-M7-hhier-noroot-pfifo-r2 | r1->sub-ctrl | info | 188653 | 0 / 0 (9.43) | 0 / 0 | ok | 130019 | 0.9096 (0.9096) | -199.95 / 2.22 | nan (0) | FAIL |
| v3-M7-hhier-noroot-pfifo-r2 | r1->r2 | info | 1354074 | 0 / 0 (67.7) | 0 / 0 | ok | 3029 | 0.9987 (0.5444) | -8.38 / 6.12 | nan (0) | ok |
| v3-M7-hhier-noroot-pfifo-r2 | r2->switch-a | target | 2472544 | 0 / 0 (123.63) | 0 / 0 | ok | 1720939 | 0.9997 (0.9994) | -2.48 / 2.41 | 1.0 (9259) | ok |
| v3-M7-hhier-noroot-pfifo-r2 | r2->switch-b | target | 2475407 | 0 / 0 (123.77) | 0 / 0 | ok | 1730320 | 0.9997 (0.9994) | -2.47 / 2.41 | 1.0 (9332) | ok |
| v3-M8-hhier-mixab-mixab-r1 | pub->r1 | info | 2264881 | 0 / 0 (113.24) | 0 / 0 | ok | 863273 | 0.9986 (0.6174) | -9.38 / 5.22 | nan (0) | ok |
| v3-M8-hhier-mixab-mixab-r1 | r1->sub-ctrl | info | 273655 | 0 / 0 (13.68) | 0 / 0 | ok | 184326 | 0.9057 (0.9057) | -200.58 / 2.46 | nan (0) | FAIL |
| v3-M8-hhier-mixab-mixab-r1 | r1->r2 | target | 6729223 | 0 / 1 (336.46) | 0 / 0 | FAIL | 4145469 | 0.9992 (0.9973) | -2.37 / 2.36 | 1.0 (6352) | ok |
| v3-M8-hhier-mixab-mixab-r1 | r2->switch-a | target | 3513921 | 0 / 0 (175.7) | 0 / 0 | ok | 2251454 | 0.9995 (0.9992) | -2.34 / 2.35 | 1.0 (11435) | ok |
| v3-M8-hhier-mixab-mixab-r1 | r2->switch-b | target | 3451420 | 0 / 0 (172.57) | 0 / 0 | ok | 1693785 | 0.9994 (0.9988) | -3.72 / 3.79 | 1.0 (921) | ok |
| v3-M8-hhier-mixab-mixab-r2 | pub->r1 | info | 2182446 | 0 / 0 (109.12) | 0 / 0 | ok | 869634 | 0.9984 (0.6173) | -9.36 / 5.54 | nan (0) | ok |
| v3-M8-hhier-mixab-mixab-r2 | r1->sub-ctrl | info | 265274 | 0 / 0 (13.26) | 0 / 0 | ok | 182899 | 0.9152 (0.9151) | -200.08 / 2.1 | nan (0) | FAIL |
| v3-M8-hhier-mixab-mixab-r2 | r1->r2 | target | 6534060 | 0 / 0 (326.7) | 0 / 0 | ok | 4012489 | 0.9991 (0.9970) | -2.42 / 2.41 | 1.0 (6283) | ok |
| v3-M8-hhier-mixab-mixab-r2 | r2->switch-a | target | 3422330 | 0 / 0 (171.12) | 0 / 0 | ok | 2204812 | 0.9995 (0.9992) | -2.41 / 2.38 | 1.0 (11402) | ok |
| v3-M8-hhier-mixab-mixab-r2 | r2->switch-b | target | 3357352 | 0 / 0 (167.87) | 0 / 0 | ok | 1647187 | 0.9993 (0.9986) | -3.88 / 3.95 | 1.0 (932) | ok |
| v3-M9-sstress-s030u070-codel-r1 | pub->router | info | 328897 | 0 / 0 (16.44) | 0 / 0 | ok | 147150 | 0.9998 (0.8138) | -9.54 / 1.84 | nan (0) | ok |
| v3-M9-sstress-s030u070-codel-r1 | router->sub-ctrl | info | 65439 | 1 / 0 (3.27) | 1 / 0 | ok | 43860 | 0.9331 (0.9331) | -200.76 / 1.5 | nan (0) | FAIL |
| v3-M9-sstress-s030u070-codel-r1 | router->switch | target | 935584 | 0 / 0 (46.78) | 0 / 0 | ok | 585087 | 0.9998 (0.9996) | -1.72 / 1.75 | 1.0 (1824) | ok |
| v3-M9-sstress-s030u070-codel-r2 | pub->router | info | 347951 | 0 / 0 (17.4) | 0 / 0 | ok | 130692 | 0.9999 (0.7903) | -9.54 / 1.77 | nan (0) | ok |
| v3-M9-sstress-s030u070-codel-r2 | router->sub-ctrl | info | 68768 | 0 / 0 (3.44) | 0 / 0 | ok | 38447 | 0.8906 (0.8906) | -201.21 / 1.29 | nan (0) | FAIL |
| v3-M9-sstress-s030u070-codel-r2 | router->switch | target | 984901 | 0 / 0 (49.25) | 0 / 0 | ok | 615312 | 0.9998 (0.9996) | -1.74 / 1.79 | 1.0 (1835) | ok |
| v3-M9-sstress-s030u070-pfifo-r1 | pub->router | info | 322874 | 0 / 0 (16.14) | 0 / 0 | ok | 145486 | 0.9998 (0.7941) | -9.65 / 1.83 | nan (0) | ok |
| v3-M9-sstress-s030u070-pfifo-r1 | router->sub-ctrl | info | 65438 | 0 / 0 (3.27) | 0 / 0 | ok | 45118 | 0.8802 (0.8802) | -201.03 / 1.37 | nan (0) | FAIL |
| v3-M9-sstress-s030u070-pfifo-r1 | router->switch | target | 921454 | 0 / 0 (46.07) | 0 / 0 | ok | 543329 | 0.9997 (0.9995) | -1.49 / 1.51 | 1.0 (1483) | ok |
| v3-M9-sstress-s030u070-pfifo-r2 | pub->router | info | 337147 | 0 / 0 (16.86) | 0 / 0 | ok | 140683 | 0.9999 (0.7978) | -9.55 / 1.81 | nan (0) | ok |
| v3-M9-sstress-s030u070-pfifo-r2 | router->sub-ctrl | info | 68787 | 0 / 0 (3.44) | 0 / 0 | ok | 45799 | 0.9275 (0.9274) | -200.62 / 1.57 | nan (0) | FAIL |
| v3-M9-sstress-s030u070-pfifo-r2 | router->switch | target | 965793 | 0 / 0 (48.29) | 0 / 0 | ok | 567255 | 0.9998 (0.9996) | -1.52 / 1.55 | 1.0 (1507) | ok |

## Health, surge, phase-lock details

- v3-C10-hindep-s030-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8801; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.16, '30Hz': 1.24}, 'b': {'1Hz': 5.33, '30Hz': 5.17}, 'up': {'1Hz': 5.53, '30Hz': 1.65}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9521, 1.1979, 1.1009), (1.15, 0.94, 0.9507, 1.1912, 1.0772), (1.15, 0.94, 0.9319, 1.2121, 1.2656), (1.05, 0.84, 0.8437, 1.0433, 0.8943), (1.05, 0.84, 0.8348, 1.1007, 1.196), (1.3, 1.09, 1.0946, 1.2744, 0.8055), (1.15, 0.94, 0.9411, 1.1124, 0.7706), (1.15, 0.94, 0.936, 1.0621, 0.5649), (1.05, 0.84, 0.835, 1.0251, 0.8552), (1.3, 1.09, 1.0931, 1.1891, 0.4301), (1.15, 0.94, 0.9383, 1.0835, 0.6532), (1.05, 0.84, 0.8483, 1.0677, 0.9908), (1.3, 1.09, 1.0887, 1.2412, 0.6856), (1.15, 0.94, 0.9381, 1.0894, 0.6805), (1.3, 1.09, 1.0917, 1.1884, 0.435), (1.15, 0.94, 0.9475, 1.0516, 0.4701), (1.15, 0.94, 0.9435, 1.0858, 0.6397), (1.05, 0.84, 0.8279, 1.0442, 0.9769), (1.15, 0.94, 0.9419, 1.0939, 0.6809), (1.15, 0.94, 0.9472, 1.1481, 0.9035), (1.3, 1.09, 1.0774, 1.237, 0.721), (1.3, 1.09, 1.083, 1.2196, 0.6119), (1.05, 0.84, 0.8447, 1.0473, 0.911), (1.05, 0.84, 0.8446, 1.0356, 0.8553), (1.05, 0.84, 0.8406, 1.0533, 0.9605), (1.15, 0.94, 0.9407, 1.108, 0.7527), (1.05, 0.84, 0.8436, 1.0398, 0.8857), (1.05, 0.84, 0.8359, 0.9723, 0.6114), (1.15, 0.94, 0.937, 1.1247, 0.8445), (1.05, 0.84, 0.8389, 1.0421, 0.9106), (1.15, 0.94, 0.929, 1.1154, 0.8383), (1.05, 0.84, 0.8406, 1.0393, 0.8934), (1.05, 0.84, 0.848, 1.0182, 0.7687), (1.05, 0.84, 0.8439, 1.0639, 0.9857), (1.3, 1.09, 1.0894, 1.1886, 0.4482), (1.3, 1.09, 1.0916, 1.2125, 0.5437), (1.3, 1.09, 1.0879, 1.1456, 0.2582), (1.05, 0.84, 0.8466, 1.0595, 0.9574), (1.3, 1.09, 1.0903, 1.2157, 0.5662), (1.3, 1.09, 1.0924, 1.2851, 0.8704), (1.3, 1.09, 1.092, 1.1972, 0.4733), (1.3, 1.09, 1.0744, 1.1601, 0.3839), (1.05, 0.84, 0.8365, 0.8836, 0.2131), (1.05, 0.84, 0.8318, 1.0439, 0.9535), (1.3, 1.09, 1.0868, 1.1935, 0.4783), (1.15, 0.94, 0.9437, 1.0952, 0.6787), (1.05, 0.84, 0.8338, 1.0449, 0.9533), (1.05, 0.84, 0.8371, 1.009, 0.7728), (1.15, 0.94, 0.9318, 1.1076, 0.7905), (1.15, 0.94, 0.9359, 1.1396, 0.9125), (1.15, 0.94, 0.9428, 1.0839, 0.6373), (1.3, 1.09, 1.1065, 1.2607, 0.691), (1.05, 0.84, 0.8437, 1.0471, 0.9149), (1.05, 0.84, 0.8504, 1.0678, 0.9817), (1.3, 1.09, 1.0971, 1.2318, 0.6034), (1.05, 0.84, 0.847, 0.9828, 0.6132), (1.3, 1.09, 1.0881, 1.2287, 0.6326), (1.15, 0.94, 0.9418, 1.1164, 0.7821), (1.15, 0.94, 0.936, 1.1584, 1.0043), (1.05, 0.84, 0.8394, 1.0572, 0.9756), (1.3, 1.09, 1.0836, 1.2626, 0.805), (1.05, 0.84, 0.8552, 1.0776, 0.996), (1.15, 0.94, 0.9276, 1.105, 0.8011), (1.15, 0.94, 0.9401, 1.083, 0.6424), (1.05, 0.84, 0.8335, 1.0213, 0.8417)]; fq collisions None; errors []
- v3-C10-hindep-s030-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8946; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.75, '30Hz': 0.95}, 'b': {'1Hz': 2.09, '30Hz': 1.43}, 'up': {'1Hz': 6.14, '30Hz': 3.73}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0803, 1.127, 0.2085), (1.3, 1.09, 1.0805, 1.1854, 0.4712), (1.05, 0.84, 0.8363, 1.0515, 0.973), (1.05, 0.84, 0.84, 1.0548, 0.9647), (1.3, 1.09, 1.0835, 1.1829, 0.4439), (1.05, 0.84, 0.8293, 1.0417, 0.9603), (1.05, 0.84, 0.8514, 1.0463, 0.8754), (1.15, 0.94, 0.9395, 1.096, 0.7029), (1.15, 0.94, 0.9353, 1.135, 0.8918), (1.15, 0.94, 0.9449, 1.0773, 0.5986), (1.15, 0.94, 0.942, 1.1085, 0.7474), (1.15, 0.94, 0.9438, 1.0605, 0.5242), (1.3, 1.09, 1.0958, 1.1625, 0.3017), (1.15, 0.94, 0.9456, 1.0806, 0.6029), (1.3, 1.09, 1.0842, 1.2225, 0.621), (1.15, 0.94, 0.9398, 1.0898, 0.6737), (1.15, 0.94, 0.9464, 1.0964, 0.6737), (1.15, 0.94, 0.9434, 1.0896, 0.6567), (1.3, 1.09, 1.0904, 1.1574, 0.3011), (1.05, 0.84, 0.8455, 0.8901, 0.2017), (1.15, 0.94, 0.9204, 1.0112, 0.4107), (1.3, 1.09, 1.1021, 1.2441, 0.6377), (1.3, 1.09, 1.0884, 1.2017, 0.5089), (1.15, 0.94, 0.9313, 1.1028, 0.7701), (1.05, 0.84, 0.8458, 1.0123, 0.7437), (1.3, 1.09, 1.085, 1.1919, 0.48), (1.3, 1.09, 1.0868, 1.1522, 0.2922), (1.3, 1.09, 1.091, 1.1647, 0.3332), (1.15, 0.94, 0.9415, 1.0782, 0.6105), (1.05, 0.84, 0.84, 1.0367, 0.883), (1.3, 1.09, 1.1021, 1.2061, 0.467), (1.15, 0.94, 0.9339, 1.085, 0.6753), (1.05, 0.84, 0.8347, 0.9965, 0.7265), (1.3, 1.09, 1.0839, 1.2476, 0.7401), (1.15, 0.94, 0.9331, 1.1198, 0.8386), (1.05, 0.84, 0.8419, 1.0883, 1.1007), (1.05, 0.84, 0.8452, 1.0606, 0.9676), (1.05, 0.84, 0.8478, 1.0635, 0.9751), (1.3, 1.09, 1.0858, 1.1946, 0.4863), (1.15, 0.94, 0.9503, 1.0835, 0.5982), (1.3, 1.09, 1.0922, 1.154, 0.276), (1.15, 0.94, 0.9431, 1.1139, 0.772), (1.05, 0.84, 0.8359, 1.0494, 0.9651), (1.15, 0.94, 0.9359, 1.1322, 0.877), (1.3, 1.09, 1.0765, 1.251, 0.7888), (1.15, 0.94, 0.9371, 1.0853, 0.6623), (1.15, 0.94, 0.9329, 1.0873, 0.698), (1.15, 0.94, 0.9429, 1.1071, 0.7374), (1.3, 1.09, 1.0804, 1.1636, 0.3719), (1.05, 0.84, 0.8401, 1.064, 1.0057), (1.3, 1.09, 1.0921, 1.2619, 0.7586), (1.05, 0.84, 0.8442, 1.0671, 1.0011), (1.05, 0.84, 0.8468, 1.0693, 0.9941), (1.3, 1.09, 1.0776, 1.2429, 0.7385), (1.3, 1.09, 1.0933, 1.2324, 0.6214), (1.3, 1.09, 1.0801, 1.24, 0.7146), (1.05, 0.84, 0.8422, 1.0224, 0.8091), (1.15, 0.94, 0.9452, 1.0784, 0.6022), (1.05, 0.84, 0.8385, 1.0638, 1.0061), (1.15, 0.94, 0.9355, 1.0763, 0.6289), (1.15, 0.94, 0.9397, 1.1035, 0.7353), (1.3, 1.09, 1.1003, 1.2389, 0.6264), (1.05, 0.84, 0.8461, 1.0496, 0.9088), (1.15, 0.94, 0.9552, 1.1479, 0.8712), (1.15, 0.94, 0.9399, 1.109, 0.7646), (1.3, 1.09, 1.096, 1.2391, 0.647), (1.15, 0.94, 0.9374, 1.0745, 0.6126), (1.15, 0.94, 0.9359, 1.1435, 0.9271), (1.3, 1.09, 1.0876, 1.1716, 0.3774), (1.05, 0.84, 0.8322, 0.9292, 0.4385), (1.3, 1.09, 1.099, 1.1383, 0.1753), (1.3, 1.09, 1.0983, 1.1755, 0.3449), (1.15, 0.94, 0.9386, 1.0977, 0.7194), (1.3, 1.09, 1.0925, 1.2026, 0.4919), (1.15, 0.94, 0.9401, 1.0733, 0.6025), (1.05, 0.84, 0.836, 1.009, 0.7767)]; fq collisions None; errors []
- v3-C10-hindep-s030-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8384; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.16, '30Hz': 1.31}, 'b': {'1Hz': 5.33, '30Hz': 5.06}, 'up': {'1Hz': 5.53, '30Hz': 1.69}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9521, 1.1295, 0.7926), (1.15, 0.94, 0.9507, 1.1216, 0.7637), (1.15, 0.94, 0.9319, 1.1332, 0.9036), (1.05, 0.84, 0.8437, 1.0174, 0.7763), (1.05, 0.84, 0.8348, 1.0228, 0.8415), (1.3, 1.09, 1.0946, 1.2475, 0.6832), (1.15, 0.94, 0.9411, 1.103, 0.7248), (1.15, 0.94, 0.936, 1.0907, 0.6915), (1.05, 0.84, 0.835, 1.0201, 0.8287), (1.3, 1.09, 1.0931, 1.2297, 0.6106), (1.15, 0.94, 0.9383, 1.1002, 0.725), (1.05, 0.84, 0.8483, 1.0652, 0.9734), (1.3, 1.09, 1.0887, 1.2267, 0.6179), (1.15, 0.94, 0.9381, 1.0886, 0.6735), (1.3, 1.09, 1.0917, 1.2264, 0.6027), (1.15, 0.94, 0.9475, 1.1017, 0.6922), (1.15, 0.94, 0.9435, 1.1038, 0.7174), (1.05, 0.84, 0.8278, 1.0292, 0.9039), (1.15, 0.94, 0.9419, 1.1014, 0.7125), (1.15, 0.94, 0.9472, 1.1065, 0.7135), (1.3, 1.09, 1.0774, 1.2162, 0.6228), (1.3, 1.09, 1.083, 1.2264, 0.6404), (1.05, 0.84, 0.8447, 1.0321, 0.839), (1.05, 0.84, 0.8446, 1.0248, 0.805), (1.05, 0.84, 0.8406, 1.0396, 0.8932), (1.15, 0.94, 0.9407, 1.099, 0.709), (1.05, 0.84, 0.8436, 1.0193, 0.7882), (1.05, 0.84, 0.8359, 0.9823, 0.6544), (1.15, 0.94, 0.937, 1.0905, 0.6873), (1.05, 0.84, 0.8388, 1.0194, 0.807), (1.15, 0.94, 0.929, 1.1062, 0.793), (1.05, 0.84, 0.8406, 1.0244, 0.8227), (1.05, 0.84, 0.848, 1.0064, 0.7112), (1.05, 0.84, 0.8439, 1.0198, 0.7864), (1.3, 1.09, 1.0894, 1.2275, 0.6202), (1.3, 1.09, 1.0916, 1.2483, 0.7016), (1.3, 1.09, 1.0879, 1.2226, 0.6017), (1.05, 0.84, 0.8466, 1.0218, 0.7841), (1.3, 1.09, 1.0903, 1.24, 0.6717), (1.3, 1.09, 1.0924, 1.2347, 0.6388), (1.3, 1.09, 1.092, 1.2264, 0.6019), (1.3, 1.09, 1.0744, 1.1911, 0.5213), (1.05, 0.84, 0.8365, 0.9737, 0.616), (1.05, 0.84, 0.8318, 1.0136, 0.8136), (1.3, 1.09, 1.0868, 1.2277, 0.6299), (1.15, 0.94, 0.9437, 1.0927, 0.6657), (1.05, 0.84, 0.8338, 1.0435, 0.9411), (1.05, 0.84, 0.8371, 1.0164, 0.8025), (1.15, 0.94, 0.9318, 1.098, 0.744), (1.15, 0.94, 0.9359, 1.095, 0.711), (1.15, 0.94, 0.9428, 1.1027, 0.7177), (1.3, 1.09, 1.1065, 1.2602, 0.6868), (1.05, 0.84, 0.8437, 1.027, 0.8207), (1.05, 0.84, 0.8504, 1.0349, 0.8277), (1.3, 1.09, 1.0971, 1.2348, 0.6152), (1.05, 0.84, 0.847, 0.9932, 0.6562), (1.3, 1.09, 1.0881, 1.2262, 0.6186), (1.15, 0.94, 0.9418, 1.0926, 0.6739), (1.15, 0.94, 0.936, 1.1444, 0.9351), (1.05, 0.84, 0.8394, 1.0529, 0.9539), (1.3, 1.09, 1.0836, 1.2304, 0.6571), (1.05, 0.84, 0.8552, 1.0311, 0.7859), (1.15, 0.94, 0.9277, 1.0852, 0.707), (1.15, 0.94, 0.9401, 1.0895, 0.6689), (1.05, 0.84, 0.8335, 1.0104, 0.7905)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r1-eth1': {'bg_packets': 34, 'in_pinned_class': 0, 'flows': []}, 'r1-eth2': {'bg_packets': 3278667, 'in_pinned_class': 144632, 'flows': ['10.101.0.1:5201']}, 'r2-eth2': {'bg_packets': 1501699, 'in_pinned_class': 257, 'flows': ['10.101.0.2:5231']}, 'r2-eth4': {'bg_packets': 1615377, 'in_pinned_class': 3899, 'flows': ['10.101.0.3:5248', '10.101.0.3:5251', '10.101.0.3:5259']}}; errors []
- v3-C10-hindep-s030-fq_codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8695; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.75, '30Hz': 0.91}, 'b': {'1Hz': 2.09, '30Hz': 1.45}, 'up': {'1Hz': 6.15, '30Hz': 3.73}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0803, 1.2119, 0.5863), (1.3, 1.09, 1.0805, 1.258, 0.7929), (1.05, 0.84, 0.8363, 1.0225, 0.8354), (1.05, 0.84, 0.84, 1.0197, 0.8024), (1.3, 1.09, 1.0835, 1.2194, 0.6053), (1.05, 0.84, 0.8293, 1.0106, 0.8135), (1.05, 0.84, 0.8514, 1.031, 0.8026), (1.15, 0.94, 0.9395, 1.0912, 0.6779), (1.15, 0.94, 0.9354, 1.0839, 0.6615), (1.15, 0.94, 0.9449, 1.0993, 0.6928), (1.15, 0.94, 0.9421, 1.097, 0.692), (1.15, 0.94, 0.9438, 1.095, 0.6754), (1.3, 1.09, 1.0958, 1.2314, 0.6082), (1.15, 0.94, 0.9456, 1.0944, 0.6624), (1.3, 1.09, 1.0842, 1.2236, 0.6225), (1.15, 0.94, 0.9398, 1.0903, 0.6724), (1.15, 0.94, 0.9464, 1.0962, 0.669), (1.15, 0.94, 0.9434, 1.0966, 0.6844), (1.3, 1.09, 1.0904, 1.227, 0.61), (1.05, 0.84, 0.8455, 0.9801, 0.6036), (1.15, 0.94, 0.9204, 1.069, 0.6671), (1.3, 1.09, 1.1021, 1.2408, 0.6196), (1.3, 1.09, 1.0884, 1.2299, 0.632), (1.15, 0.94, 0.9313, 1.0909, 0.713), (1.05, 0.84, 0.8458, 1.0127, 0.7431), (1.3, 1.09, 1.085, 1.2229, 0.6157), (1.3, 1.09, 1.0868, 1.2183, 0.586), (1.3, 1.09, 1.091, 1.2315, 0.6305), (1.15, 0.94, 0.9415, 1.0947, 0.6822), (1.05, 0.84, 0.84, 1.0153, 0.7829), (1.3, 1.09, 1.1021, 1.2523, 0.6708), (1.15, 0.94, 0.9339, 1.0929, 0.7081), (1.05, 0.84, 0.8347, 1.013, 0.7964), (1.3, 1.09, 1.0839, 1.2404, 0.7023), (1.15, 0.94, 0.9331, 1.0768, 0.6418), (1.05, 0.84, 0.8419, 1.0298, 0.837), (1.05, 0.84, 0.8452, 1.0191, 0.7766), (1.05, 0.84, 0.8478, 1.0203, 0.774), (1.3, 1.09, 1.0858, 1.2299, 0.6419), (1.15, 0.94, 0.9503, 1.1011, 0.6736), (1.3, 1.09, 1.0922, 1.2315, 0.6204), (1.15, 0.94, 0.9431, 1.0904, 0.6609), (1.05, 0.84, 0.836, 1.019, 0.8214), (1.15, 0.94, 0.9359, 1.0875, 0.6753), (1.3, 1.09, 1.0765, 1.2254, 0.6678), (1.15, 0.94, 0.9371, 1.0925, 0.6921), (1.15, 0.94, 0.9329, 1.0903, 0.7061), (1.15, 0.94, 0.9429, 1.0991, 0.6977), (1.3, 1.09, 1.0804, 1.221, 0.6264), (1.05, 0.84, 0.8401, 1.0242, 0.8226), (1.3, 1.09, 1.0921, 1.2484, 0.696), (1.05, 0.84, 0.8442, 1.0195, 0.7831), (1.05, 0.84, 0.8468, 1.0182, 0.7634), (1.3, 1.09, 1.0776, 1.2226, 0.6456), (1.3, 1.09, 1.0933, 1.236, 0.6354), (1.3, 1.09, 1.0801, 1.223, 0.6368), (1.05, 0.84, 0.8422, 1.0113, 0.7555), (1.15, 0.94, 0.9452, 1.0973, 0.6826), (1.05, 0.84, 0.8386, 1.0092, 0.7601), (1.15, 0.94, 0.9355, 1.0887, 0.6825), (1.15, 0.94, 0.9397, 1.0879, 0.6619), (1.3, 1.09, 1.1003, 1.2398, 0.6257), (1.05, 0.84, 0.8461, 1.046, 0.8901), (1.15, 0.94, 0.9552, 1.1198, 0.7385), (1.15, 0.94, 0.9399, 1.0963, 0.7016), (1.3, 1.09, 1.096, 1.2295, 0.5988), (1.15, 0.94, 0.9374, 1.0938, 0.6967), (1.15, 0.94, 0.9359, 1.0999, 0.7303), (1.3, 1.09, 1.0876, 1.2249, 0.6132), (1.05, 0.84, 0.8322, 0.9893, 0.705), (1.3, 1.09, 1.099, 1.2306, 0.586), (1.3, 1.09, 1.0983, 1.2439, 0.6485), (1.15, 0.94, 0.9386, 1.0882, 0.6713), (1.3, 1.09, 1.0924, 1.2295, 0.6102), (1.15, 0.94, 0.9401, 1.0909, 0.6768), (1.05, 0.84, 0.836, 1.0216, 0.8287)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r1-eth1': {'bg_packets': 43, 'in_pinned_class': 0, 'flows': []}, 'r1-eth2': {'bg_packets': 3304469, 'in_pinned_class': 4189, 'flows': ['10.101.0.1:5205', '10.101.0.1:5210', '10.101.0.1:5216', '10.101.0.1:5222']}, 'r2-eth2': {'bg_packets': 1613663, 'in_pinned_class': 2530, 'flows': ['10.101.0.2:5236', '10.101.0.2:5238']}, 'r2-eth4': {'bg_packets': 1628173, 'in_pinned_class': 1725, 'flows': ['10.101.0.3:5265', '10.101.0.3:5272']}}; errors []
- v3-C10-hindep-s030-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8888; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.16, '30Hz': 1.23}, 'b': {'1Hz': 5.34, '30Hz': 5.1}, 'up': {'1Hz': 5.53, '30Hz': 1.67}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9521, 1.2312, 1.264), (1.15, 0.94, 0.9507, 1.182, 1.0473), (1.15, 0.94, 0.9319, 1.1847, 1.1407), (1.05, 0.84, 0.8437, 1.0554, 0.9589), (1.05, 0.84, 0.8348, 1.0826, 1.1201), (1.3, 1.09, 1.0946, 1.2651, 0.7722), (1.15, 0.94, 0.9411, 1.116, 0.7904), (1.15, 0.94, 0.936, 1.158, 1.0057), (1.05, 0.84, 0.835, 1.0681, 1.0539), (1.3, 1.09, 1.0931, 1.2585, 0.7493), (1.15, 0.94, 0.9383, 1.1426, 0.9235), (1.05, 0.84, 0.8483, 1.0796, 1.0438), (1.3, 1.09, 1.0887, 1.2069, 0.5342), (1.15, 0.94, 0.9381, 1.099, 0.727), (1.3, 1.09, 1.0917, 1.1946, 0.4652), (1.15, 0.94, 0.9475, 1.0691, 0.5488), (1.15, 0.94, 0.9435, 1.1051, 0.7303), (1.05, 0.84, 0.8279, 1.0439, 0.9746), (1.15, 0.94, 0.9419, 1.1573, 0.9756), (1.15, 0.94, 0.9472, 1.1054, 0.7152), (1.3, 1.09, 1.0774, 1.2306, 0.6913), (1.3, 1.09, 1.083, 1.2052, 0.5533), (1.05, 0.84, 0.8447, 1.0525, 0.9393), (1.05, 0.84, 0.8446, 1.0577, 0.965), (1.05, 0.84, 0.8406, 1.0643, 1.0093), (1.15, 0.94, 0.9407, 1.1625, 1.0028), (1.05, 0.84, 0.8436, 1.0635, 0.9922), (1.05, 0.84, 0.8359, 0.9847, 0.6741), (1.15, 0.94, 0.937, 1.1452, 0.9413), (1.05, 0.84, 0.8388, 1.0489, 0.9514), (1.15, 0.94, 0.929, 1.1315, 0.9151), (1.05, 0.84, 0.8406, 1.0746, 1.0575), (1.05, 0.84, 0.848, 1.0177, 0.7661), (1.05, 0.84, 0.8439, 1.0937, 1.1315), (1.3, 1.09, 1.0894, 1.2288, 0.6294), (1.3, 1.09, 1.0916, 1.1928, 0.4577), (1.3, 1.09, 1.0879, 1.1708, 0.3751), (1.05, 0.84, 0.8466, 1.068, 1.0006), (1.3, 1.09, 1.0903, 1.2192, 0.5815), (1.3, 1.09, 1.0924, 1.2377, 0.6559), (1.3, 1.09, 1.092, 1.1817, 0.4056), (1.3, 1.09, 1.0744, 1.1184, 0.199), (1.05, 0.84, 0.8365, 0.9058, 0.3127), (1.05, 0.84, 0.8318, 1.0402, 0.9416), (1.3, 1.09, 1.0868, 1.2448, 0.7156), (1.15, 0.94, 0.9437, 1.1419, 0.8977), (1.05, 0.84, 0.8338, 1.0706, 1.0688), (1.05, 0.84, 0.8371, 1.0254, 0.8507), (1.15, 0.94, 0.9318, 1.1263, 0.8791), (1.15, 0.94, 0.9359, 1.2179, 1.2772), (1.15, 0.94, 0.9428, 1.1664, 1.0091), (1.3, 1.09, 1.1065, 1.2996, 0.8747), (1.05, 0.84, 0.8437, 1.0989, 1.1537), (1.05, 0.84, 0.8504, 1.0742, 1.0099), (1.3, 1.09, 1.0971, 1.2632, 0.7521), (1.05, 0.84, 0.847, 0.9512, 0.4703), (1.3, 1.09, 1.0881, 1.2482, 0.724), (1.15, 0.94, 0.9418, 1.1627, 1.0002), (1.15, 0.94, 0.936, 1.1438, 0.9377), (1.05, 0.84, 0.8394, 1.076, 1.0714), (1.3, 1.09, 1.0836, 1.2344, 0.6816), (1.05, 0.84, 0.8552, 1.1126, 1.1656), (1.15, 0.94, 0.9276, 1.0986, 0.7715), (1.15, 0.94, 0.9401, 1.129, 0.8536), (1.05, 0.84, 0.8335, 1.0437, 0.952)]; fq collisions None; errors []
- v3-C10-hindep-s030-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8876; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.75, '30Hz': 0.97}, 'b': {'1Hz': 2.09, '30Hz': 1.45}, 'up': {'1Hz': 6.14, '30Hz': 3.79}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0803, 1.1376, 0.2577), (1.3, 1.09, 1.0805, 1.1829, 0.4611), (1.05, 0.84, 0.8363, 1.0784, 1.0926), (1.05, 0.84, 0.84, 1.0605, 0.9928), (1.3, 1.09, 1.0835, 1.2283, 0.6512), (1.05, 0.84, 0.8293, 1.0658, 1.0675), (1.05, 0.84, 0.8514, 1.0852, 1.0531), (1.15, 0.94, 0.9395, 1.1065, 0.752), (1.15, 0.94, 0.9354, 1.1724, 1.066), (1.15, 0.94, 0.9449, 1.1652, 0.9945), (1.15, 0.94, 0.942, 1.1488, 0.931), (1.15, 0.94, 0.9438, 1.102, 0.7127), (1.3, 1.09, 1.0958, 1.1896, 0.4234), (1.15, 0.94, 0.9456, 1.1136, 0.7551), (1.3, 1.09, 1.0842, 1.2063, 0.5498), (1.15, 0.94, 0.9398, 1.1107, 0.7698), (1.15, 0.94, 0.9464, 1.1046, 0.7122), (1.15, 0.94, 0.9434, 1.1312, 0.8458), (1.3, 1.09, 1.0904, 1.1783, 0.3959), (1.05, 0.84, 0.8455, 0.9007, 0.2491), (1.15, 0.94, 0.9204, 1.0234, 0.4653), (1.3, 1.09, 1.1021, 1.2513, 0.6718), (1.3, 1.09, 1.0884, 1.2333, 0.6527), (1.15, 0.94, 0.9313, 1.1425, 0.951), (1.05, 0.84, 0.8458, 1.074, 1.026), (1.3, 1.09, 1.085, 1.213, 0.5764), (1.3, 1.09, 1.0868, 1.1868, 0.4496), (1.3, 1.09, 1.091, 1.2406, 0.6754), (1.15, 0.94, 0.9415, 1.1544, 0.9571), (1.05, 0.84, 0.84, 1.0779, 1.071), (1.3, 1.09, 1.1021, 1.2054, 0.4654), (1.15, 0.94, 0.9339, 1.1802, 1.1078), (1.05, 0.84, 0.8347, 1.0649, 1.0365), (1.3, 1.09, 1.0839, 1.2115, 0.5761), (1.15, 0.94, 0.9331, 1.1326, 0.8986), (1.05, 0.84, 0.8419, 1.1391, 1.3362), (1.05, 0.84, 0.8452, 1.0835, 1.0731), (1.05, 0.84, 0.8478, 1.0721, 1.0126), (1.3, 1.09, 1.0858, 1.2327, 0.6607), (1.15, 0.94, 0.9503, 1.0909, 0.6332), (1.3, 1.09, 1.0922, 1.2146, 0.5503), (1.15, 0.94, 0.9431, 1.0946, 0.6836), (1.05, 0.84, 0.8359, 1.0736, 1.0729), (1.15, 0.94, 0.9359, 1.1562, 0.9907), (1.3, 1.09, 1.0765, 1.2261, 0.675), (1.15, 0.94, 0.9371, 1.1544, 0.9771), (1.15, 0.94, 0.9329, 1.1607, 1.028), (1.15, 0.94, 0.9429, 1.1116, 0.7598), (1.3, 1.09, 1.0804, 1.1799, 0.4476), (1.05, 0.84, 0.8401, 1.0652, 1.0137), (1.3, 1.09, 1.0921, 1.2725, 0.8112), (1.05, 0.84, 0.8442, 1.071, 1.0213), (1.05, 0.84, 0.8468, 1.0311, 0.8287), (1.3, 1.09, 1.0776, 1.248, 0.7661), (1.3, 1.09, 1.0933, 1.2484, 0.6975), (1.3, 1.09, 1.0801, 1.2196, 0.6274), (1.05, 0.84, 0.8422, 1.0623, 0.991), (1.15, 0.94, 0.9452, 1.1141, 0.7624), (1.05, 0.84, 0.8385, 1.0724, 1.0514), (1.15, 0.94, 0.9355, 1.163, 1.0227), (1.15, 0.94, 0.9397, 1.1325, 0.8681), (1.3, 1.09, 1.1002, 1.1975, 0.4391), (1.05, 0.84, 0.8461, 1.0709, 1.0105), (1.15, 0.94, 0.9552, 1.1541, 0.8976), (1.15, 0.94, 0.9399, 1.1713, 1.0443), (1.3, 1.09, 1.096, 1.2312, 0.61), (1.15, 0.94, 0.9374, 1.1411, 0.9159), (1.15, 0.94, 0.9359, 1.1737, 1.069), (1.3, 1.09, 1.0876, 1.1976, 0.4953), (1.05, 0.84, 0.8322, 0.9398, 0.4859), (1.3, 1.09, 1.099, 1.1457, 0.21), (1.3, 1.09, 1.0983, 1.2379, 0.6278), (1.15, 0.94, 0.9386, 1.1486, 0.9482), (1.3, 1.09, 1.0924, 1.2467, 0.6935), (1.15, 0.94, 0.9401, 1.1677, 1.0276), (1.05, 0.84, 0.836, 1.059, 1.0041)]; fq collisions None; errors []
- v3-C11-huneven-uneven-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8736; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.82, '30Hz': 0.84}, 'B': {'1Hz': 1.26, '30Hz': 1.63}, 'C': {'1Hz': 2.57, '30Hz': 2.01}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8485, 1.0681, 1.0023), (1.3, 1.09, 1.0798, 1.288, 0.9523), (1.05, 0.84, 0.8371, 1.0641, 1.036), (1.3, 1.09, 1.0763, 1.212, 0.6136), (1.3, 1.09, 1.0931, 1.2141, 0.5522), (1.05, 0.84, 0.8471, 1.0388, 0.867), (1.15, 0.94, 0.9508, 1.0689, 0.5404), (1.3, 1.09, 1.0873, 1.2065, 0.5451), (1.15, 0.94, 0.9467, 1.1055, 0.726), (1.15, 0.94, 0.9384, 1.1378, 0.9019), (1.05, 0.84, 0.8342, 1.0521, 0.9966), (1.3, 1.09, 1.0913, 1.2072, 0.5243), (1.15, 0.94, 0.9509, 1.089, 0.6303), (1.3, 1.09, 1.0871, 1.221, 0.6055), (1.3, 1.09, 1.0886, 1.146, 0.2626), (1.05, 0.84, 0.843, 1.0338, 0.8712), (1.05, 0.84, 0.8289, 1.0299, 0.9089), (1.3, 1.09, 1.0827, 1.2097, 0.5742), (1.15, 0.94, 0.96, 1.1367, 0.8084), (1.15, 0.94, 0.9486, 1.0725, 0.567), (1.05, 0.84, 0.8418, 1.0525, 0.9616), (1.3, 1.09, 1.0862, 1.1554, 0.3164), (1.05, 0.84, 0.842, 1.0499, 0.949), (1.15, 0.94, 0.9384, 1.078, 0.6315), (1.15, 0.94, 0.9419, 1.0815, 0.6372), (1.15, 0.94, 0.9423, 1.0788, 0.623), (1.15, 0.94, 0.9117, 1.0922, 0.8239), (1.05, 0.84, 0.8359, 1.0565, 1.0087), (1.3, 1.09, 1.0932, 1.1798, 0.395), (1.3, 1.09, 1.1048, 1.2235, 0.5366), (1.3, 1.09, 1.0784, 1.157, 0.3596), (1.05, 0.84, 0.856, 1.0739, 0.9946), (1.05, 0.84, 0.8364, 1.0527, 0.978), (1.15, 0.94, 0.932, 1.0593, 0.5821), (1.15, 0.94, 0.9451, 1.0997, 0.7057), (1.15, 0.94, 0.9385, 1.0857, 0.6658), (1.15, 0.94, 0.9452, 1.0739, 0.589), (1.05, 0.84, 0.8409, 1.0513, 0.9603), (1.3, 1.09, 1.1124, 1.259, 0.6704), (1.15, 0.94, 0.941, 1.0771, 0.6213), (1.15, 0.94, 0.9447, 1.0954, 0.6895), (1.05, 0.84, 0.8327, 1.0481, 0.9832), (1.15, 0.94, 0.9284, 1.0672, 0.6352), (1.05, 0.84, 0.8442, 1.061, 0.9805), (1.3, 1.09, 1.0887, 1.1423, 0.2454), (1.05, 0.84, 0.8403, 1.0536, 0.9649), (1.15, 0.94, 0.9374, 1.0918, 0.6981), (1.15, 0.94, 0.9491, 1.1167, 0.7581), (1.3, 1.09, 1.0866, 1.1761, 0.4083), (1.3, 1.09, 1.0922, 1.2153, 0.5565), (1.15, 0.94, 0.9469, 1.1137, 0.7542), (1.05, 0.84, 0.8259, 1.0411, 0.9842), (1.3, 1.09, 1.0822, 1.1648, 0.3777), (1.3, 1.09, 1.0931, 1.2267, 0.6046), (1.05, 0.84, 0.836, 1.0575, 1.0133), (1.05, 0.84, 0.8463, 1.0602, 0.9762), (1.15, 0.94, 0.9415, 1.0716, 0.5885), (1.15, 0.94, 0.9453, 1.1139, 0.7715), (1.3, 1.09, 1.0912, 1.1747, 0.3775), (1.3, 1.09, 1.0927, 1.1834, 0.4142), (1.3, 1.09, 1.101, 1.2304, 0.5919), (1.3, 1.09, 1.0862, 1.21, 0.5598), (1.05, 0.84, 0.8462, 1.0532, 0.9363), (1.15, 0.94, 0.9377, 1.0702, 0.6049), (1.15, 0.94, 0.9364, 1.083, 0.6695), (1.05, 0.84, 0.8435, 1.0343, 0.8724), (1.05, 0.84, 0.8451, 1.0518, 0.9433), (1.15, 0.94, 0.9436, 1.0795, 0.6214), (1.3, 1.09, 1.0914, 1.2182, 0.5735), (1.15, 0.94, 0.9497, 1.1318, 0.8239), (1.05, 0.84, 0.8406, 1.059, 0.997), (1.3, 1.09, 1.084, 1.1875, 0.4734), (1.3, 1.09, 1.0813, 1.2074, 0.5702), (1.15, 0.94, 0.9356, 1.0736, 0.6311)]; fq collisions None; errors []
- v3-C11-huneven-uneven-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8789; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 3.71, '30Hz': 1.27}, 'B': {'1Hz': 1.22, '30Hz': 3.86}, 'C': {'1Hz': 4.62, '30Hz': 3.6}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.83, 1.05, 1.0097), (1.05, 0.84, 0.8424, 1.1254, 1.2931), (1.15, 0.94, 0.9261, 1.147, 1.0125), (1.3, 1.09, 1.0885, 1.1794, 0.4154), (1.05, 0.84, 0.8412, 1.0715, 1.0553), (1.05, 0.84, 0.8463, 1.061, 0.9852), (1.05, 0.84, 0.8489, 1.0466, 0.9033), (1.15, 0.94, 0.9434, 1.1364, 0.8861), (1.15, 0.94, 0.9349, 1.0744, 0.6375), (1.15, 0.94, 0.9337, 1.129, 0.8961), (1.05, 0.84, 0.8428, 1.0451, 0.927), (1.05, 0.84, 0.8287, 1.0451, 0.9888), (1.05, 0.84, 0.8457, 1.0413, 0.8981), (1.3, 1.09, 1.1032, 1.2312, 0.5853), (1.3, 1.09, 1.0889, 1.1474, 0.268), (1.05, 0.84, 0.8366, 1.0513, 0.9853), (1.05, 0.84, 0.8409, 1.0538, 0.9732), (1.3, 1.09, 1.089, 1.1592, 0.3214), (1.15, 0.94, 0.9483, 1.1245, 0.8052), (1.3, 1.09, 1.0943, 1.198, 0.475), (1.3, 1.09, 1.0898, 1.172, 0.3755), (1.05, 0.84, 0.8368, 1.0347, 0.9082), (1.3, 1.09, 1.0895, 1.2245, 0.6195), (1.3, 1.09, 1.0927, 1.189, 0.4403), (1.15, 0.94, 0.9395, 1.1281, 0.8655), (1.15, 0.94, 0.9445, 1.1242, 0.8212), (1.05, 0.84, 0.8415, 1.0394, 0.9068), (1.3, 1.09, 1.0778, 1.2107, 0.6102), (1.15, 0.94, 0.9416, 1.0865, 0.6637), (1.3, 1.09, 1.0903, 1.1683, 0.3571), (1.3, 1.09, 1.1155, 1.2501, 0.6175), (1.15, 0.94, 0.9354, 1.1383, 0.9272), (1.3, 1.09, 1.0857, 1.2088, 0.5643), (1.15, 0.94, 0.9384, 1.0738, 0.6203), (1.15, 0.94, 0.9401, 1.1083, 0.7719), (1.05, 0.84, 0.8283, 1.0433, 0.9822), (1.05, 0.84, 0.8514, 1.0626, 0.9678), (1.15, 0.94, 0.9413, 1.0874, 0.6705), (1.15, 0.94, 0.9339, 1.0805, 0.6719), (1.3, 1.09, 1.088, 1.1841, 0.4388), (1.05, 0.84, 0.8296, 1.0441, 0.9799), (1.15, 0.94, 0.9405, 1.1229, 0.8371), (1.3, 1.09, 1.0553, 1.1937, 0.6343), (1.15, 0.94, 0.9495, 1.0819, 0.6081), (1.15, 0.94, 0.9536, 1.1252, 0.7842), (1.05, 0.84, 0.848, 1.0531, 0.94), (1.15, 0.94, 0.9371, 1.0547, 0.5389), (1.3, 1.09, 1.0835, 1.2175, 0.6123), (1.3, 1.09, 1.094, 1.2362, 0.6528), (1.15, 0.94, 0.9512, 1.1388, 0.8611), (1.3, 1.09, 1.092, 1.1462, 0.2483), (1.05, 0.84, 0.8439, 1.0621, 0.997), (1.15, 0.94, 0.9347, 1.0579, 0.5644), (1.15, 0.94, 0.9339, 1.1208, 0.8576), (1.3, 1.09, 1.0819, 1.2146, 0.6063), (1.3, 1.09, 1.0968, 1.1914, 0.4344), (1.15, 0.94, 0.9447, 1.0794, 0.617), (1.05, 0.84, 0.8408, 1.0393, 0.9067), (1.05, 0.84, 0.841, 1.0538, 0.9771), (1.15, 0.94, 0.9453, 1.0769, 0.6029), (1.3, 1.09, 1.1014, 1.2281, 0.5788), (1.15, 0.94, 0.9365, 1.0724, 0.6237), (1.15, 0.94, 0.9517, 1.1155, 0.7505), (1.15, 0.94, 0.9425, 1.0745, 0.6051), (1.15, 0.94, 0.9326, 1.12, 0.86), (1.05, 0.84, 0.842, 1.0373, 0.8949), (1.05, 0.84, 0.8475, 1.0421, 0.8919), (1.15, 0.94, 0.9353, 1.0779, 0.6517), (1.05, 0.84, 0.8383, 1.0459, 0.9516), (1.15, 0.94, 0.9346, 1.0766, 0.6517), (1.3, 1.09, 1.0984, 1.2232, 0.5704), (1.3, 1.09, 1.0968, 1.194, 0.4443), (1.05, 0.84, 0.8339, 1.0606, 1.0409), (1.3, 1.09, 1.0938, 1.1692, 0.3461), (1.15, 0.94, 0.9422, 1.0802, 0.6334), (1.05, 0.84, 0.8386, 1.0545, 0.9897), (1.05, 0.84, 0.8425, 1.0591, 0.9897), (1.05, 0.84, 0.8454, 1.0691, 1.0253), (1.3, 1.09, 1.0897, 1.178, 0.4036), (1.05, 0.84, 0.853, 1.0572, 0.9372)]; fq collisions None; errors []
- v3-C11-huneven-uneven-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 1, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8684; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.81, '30Hz': 0.86}, 'B': {'1Hz': 1.27, '30Hz': 1.64}, 'C': {'1Hz': 2.57, '30Hz': 1.95}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8485, 1.0681, 1.0047), (1.3, 1.09, 1.0798, 1.3028, 1.0239), (1.05, 0.84, 0.8371, 1.0815, 1.1181), (1.3, 1.09, 1.0763, 1.2774, 0.9167), (1.3, 1.09, 1.0931, 1.1826, 0.4097), (1.05, 0.84, 0.8471, 1.085, 1.0839), (1.15, 0.94, 0.9508, 1.0925, 0.6508), (1.3, 1.09, 1.0873, 1.1743, 0.3992), (1.15, 0.94, 0.9468, 1.0797, 0.6105), (1.15, 0.94, 0.9384, 1.1046, 0.7577), (1.05, 0.84, 0.8342, 1.0612, 1.042), (1.3, 1.09, 1.0913, 1.2354, 0.6567), (1.15, 0.94, 0.9509, 1.1398, 0.8641), (1.3, 1.09, 1.0871, 1.2555, 0.7677), (1.3, 1.09, 1.0886, 1.1802, 0.4208), (1.05, 0.84, 0.843, 1.0688, 1.0332), (1.05, 0.84, 0.8289, 1.0564, 1.0365), (1.3, 1.09, 1.0827, 1.1892, 0.4851), (1.15, 0.94, 0.96, 1.1153, 0.7129), (1.15, 0.94, 0.9486, 1.1216, 0.7941), (1.05, 0.84, 0.8418, 1.0747, 1.0655), (1.3, 1.09, 1.0862, 1.1773, 0.4184), (1.05, 0.84, 0.842, 1.0712, 1.0482), (1.15, 0.94, 0.9384, 1.1053, 0.7606), (1.15, 0.94, 0.9419, 1.1249, 0.8369), (1.15, 0.94, 0.9423, 1.1119, 0.7758), (1.15, 0.94, 0.9117, 1.1378, 1.0345), (1.05, 0.84, 0.8359, 1.0702, 1.0753), (1.3, 1.09, 1.0933, 1.1959, 0.4694), (1.3, 1.09, 1.1048, 1.2451, 0.6391), (1.3, 1.09, 1.0784, 1.1827, 0.4787), (1.05, 0.84, 0.856, 1.1046, 1.1376), (1.05, 0.84, 0.8364, 1.0946, 1.1766), (1.15, 0.94, 0.932, 1.1159, 0.844), (1.15, 0.94, 0.9451, 1.1356, 0.8713), (1.15, 0.94, 0.9385, 1.1195, 0.8249), (1.15, 0.94, 0.9451, 1.1, 0.7109), (1.05, 0.84, 0.8409, 1.0876, 1.1282), (1.3, 1.09, 1.1124, 1.2295, 0.5374), (1.15, 0.94, 0.941, 1.1145, 0.7938), (1.15, 0.94, 0.9447, 1.1096, 0.757), (1.05, 0.84, 0.8327, 1.0598, 1.039), (1.15, 0.94, 0.9284, 1.1415, 0.9787), (1.05, 0.84, 0.8442, 1.0621, 0.9931), (1.3, 1.09, 1.0887, 1.179, 0.4144), (1.05, 0.84, 0.8403, 1.0543, 0.9755), (1.15, 0.94, 0.9374, 1.1252, 0.8556), (1.15, 0.94, 0.9491, 1.1042, 0.7069), (1.3, 1.09, 1.0866, 1.1998, 0.5175), (1.3, 1.09, 1.0922, 1.2368, 0.6589), (1.15, 0.94, 0.9469, 1.1106, 0.7461), (1.05, 0.84, 0.8259, 1.071, 1.1254), (1.3, 1.09, 1.0822, 1.1668, 0.3882), (1.3, 1.09, 1.093, 1.2211, 0.5836), (1.05, 0.84, 0.836, 1.0672, 1.0617), (1.05, 0.84, 0.8463, 1.0674, 1.0114), (1.15, 0.94, 0.9415, 1.109, 0.7631), (1.15, 0.94, 0.9453, 1.1827, 1.09), (1.3, 1.09, 1.0912, 1.1913, 0.4562), (1.3, 1.09, 1.0927, 1.1829, 0.4128), (1.3, 1.09, 1.101, 1.2131, 0.5148), (1.3, 1.09, 1.0862, 1.2495, 0.7442), (1.05, 0.84, 0.8462, 1.0777, 1.0552), (1.15, 0.94, 0.9377, 1.1345, 0.9004), (1.15, 0.94, 0.9364, 1.1417, 0.9394), (1.05, 0.84, 0.8435, 1.05, 0.9477), (1.05, 0.84, 0.8451, 1.0725, 1.0402), (1.15, 0.94, 0.9436, 1.1023, 0.7283), (1.3, 1.09, 1.0914, 1.2027, 0.5073), (1.15, 0.94, 0.9496, 1.1593, 0.9555), (1.05, 0.84, 0.8406, 1.0941, 1.1598), (1.3, 1.09, 1.084, 1.1784, 0.4334), (1.3, 1.09, 1.0813, 1.2031, 0.5548), (1.15, 0.94, 0.9356, 1.1063, 0.7834)]; fq collisions None; errors []
- v3-C11-huneven-uneven-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8783; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 3.71, '30Hz': 1.29}, 'B': {'1Hz': 1.22, '30Hz': 3.81}, 'C': {'1Hz': 4.61, '30Hz': 3.53}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.83, 1.0818, 1.1586), (1.05, 0.84, 0.8424, 1.1066, 1.2095), (1.15, 0.94, 0.9261, 1.1657, 1.1051), (1.3, 1.09, 1.0885, 1.1811, 0.4237), (1.05, 0.84, 0.8412, 1.0726, 1.0671), (1.05, 0.84, 0.8463, 1.0576, 0.9721), (1.05, 0.84, 0.8489, 1.0644, 0.9865), (1.15, 0.94, 0.9434, 1.1409, 0.9088), (1.15, 0.94, 0.9349, 1.1105, 0.804), (1.15, 0.94, 0.9337, 1.1106, 0.8139), (1.05, 0.84, 0.8428, 1.0902, 1.1409), (1.05, 0.84, 0.8287, 1.0522, 1.0232), (1.05, 0.84, 0.8457, 1.0694, 1.0296), (1.3, 1.09, 1.1032, 1.2276, 0.5697), (1.3, 1.09, 1.0889, 1.1658, 0.3544), (1.05, 0.84, 0.8366, 1.0664, 1.0574), (1.05, 0.84, 0.8409, 1.046, 0.9391), (1.3, 1.09, 1.089, 1.1717, 0.3814), (1.15, 0.94, 0.9483, 1.1453, 0.9021), (1.3, 1.09, 1.0945, 1.1936, 0.457), (1.3, 1.09, 1.0898, 1.1938, 0.4761), (1.05, 0.84, 0.8368, 1.0395, 0.9328), (1.3, 1.09, 1.0895, 1.2218, 0.6086), (1.3, 1.09, 1.0927, 1.2205, 0.5851), (1.15, 0.94, 0.9395, 1.1106, 0.7871), (1.15, 0.94, 0.9445, 1.1662, 1.0153), (1.05, 0.84, 0.8415, 1.0596, 1.0055), (1.3, 1.09, 1.0778, 1.181, 0.4751), (1.15, 0.94, 0.9416, 1.085, 0.661), (1.3, 1.09, 1.0903, 1.1822, 0.4236), (1.3, 1.09, 1.1155, 1.2494, 0.6159), (1.15, 0.94, 0.9354, 1.1056, 0.779), (1.3, 1.09, 1.0857, 1.2092, 0.5695), (1.15, 0.94, 0.9384, 1.0954, 0.7239), (1.15, 0.94, 0.9401, 1.1032, 0.7503), (1.05, 0.84, 0.8283, 1.0447, 0.9905), (1.05, 0.84, 0.8514, 1.0536, 0.9322), (1.15, 0.94, 0.9413, 1.1132, 0.7912), (1.15, 0.94, 0.9339, 1.1316, 0.9121), (1.3, 1.09, 1.088, 1.1942, 0.486), (1.05, 0.84, 0.8296, 1.0301, 0.9178), (1.15, 0.94, 0.9406, 1.1839, 1.1196), (1.3, 1.09, 1.0553, 1.1997, 0.666), (1.15, 0.94, 0.9495, 1.1552, 0.9469), (1.15, 0.94, 0.9536, 1.138, 0.8442), (1.05, 0.84, 0.848, 1.0579, 0.968), (1.15, 0.94, 0.9371, 1.0959, 0.7324), (1.3, 1.09, 1.0835, 1.1912, 0.4928), (1.3, 1.09, 1.094, 1.2161, 0.562), (1.15, 0.94, 0.9512, 1.1306, 0.8256), (1.3, 1.09, 1.092, 1.1571, 0.3001), (1.05, 0.84, 0.8439, 1.0703, 1.0368), (1.15, 0.94, 0.9347, 1.1036, 0.7788), (1.15, 0.94, 0.9339, 1.0882, 0.7099), (1.3, 1.09, 1.0819, 1.2474, 0.7574), (1.3, 1.09, 1.0968, 1.1972, 0.4624), (1.15, 0.94, 0.9447, 1.0884, 0.6623), (1.05, 0.84, 0.8409, 1.0596, 1.0017), (1.05, 0.84, 0.841, 1.0712, 1.0594), (1.15, 0.94, 0.9453, 1.1249, 0.8282), (1.3, 1.09, 1.1015, 1.2329, 0.6018), (1.15, 0.94, 0.9365, 1.1065, 0.7823), (1.15, 0.94, 0.9517, 1.1709, 1.0106), (1.15, 0.94, 0.9425, 1.0936, 0.6969), (1.15, 0.94, 0.9326, 1.1504, 1.0022), (1.05, 0.84, 0.842, 1.0764, 1.0807), (1.05, 0.84, 0.8475, 1.0722, 1.0362), (1.15, 0.94, 0.9353, 1.1092, 0.7963), (1.05, 0.84, 0.8383, 1.0519, 0.985), (1.15, 0.94, 0.9346, 1.121, 0.8579), (1.3, 1.09, 1.0984, 1.2144, 0.5313), (1.3, 1.09, 1.0968, 1.1929, 0.4398), (1.05, 0.84, 0.8339, 1.0729, 1.0999), (1.3, 1.09, 1.0938, 1.193, 0.4565), (1.15, 0.94, 0.9422, 1.1195, 0.8159), (1.05, 0.84, 0.8386, 1.0495, 0.9729), (1.05, 0.84, 0.8425, 1.0687, 1.0356), (1.05, 0.84, 0.8453, 1.07, 1.036), (1.3, 1.09, 1.0897, 1.2079, 0.5415), (1.05, 0.84, 0.853, 1.08, 1.0443)]; fq collisions None; errors []
- v3-C12-amixed-access-codel-r1: lost 0; target egresses failing ['ra-eth1', 'rb-eth1', 'rc-eth1', 'rd-eth1']; recursion misses {'pub': 0, 'router': 0, 'ra': 1, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8612; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.61, '30Hz': 1.02}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0785, 1.1885, 0.5404), (1.05, 0.84, 0.852, 1.0536, 0.9902), (1.15, 0.94, 0.925, 1.1478, 1.095), (1.05, 0.84, 0.8356, 1.046, 1.0338), (1.15, 0.94, 0.9312, 1.1029, 0.8437), (1.05, 0.84, 0.8504, 1.0658, 1.0585), (1.3, 1.09, 1.0848, 1.154, 0.3403), (1.3, 1.09, 1.0788, 1.1675, 0.4361), (1.15, 0.94, 0.9385, 1.0936, 0.762)]; fq collisions None; errors []
- v3-C12-amixed-access-codel-r2: lost 0; target egresses failing ['ra-eth1', 'rb-eth1', 'rc-eth1', 'rd-eth1']; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8601; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.37, '30Hz': 0.94}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8351, 1.0476, 1.0365), (1.3, 1.09, 1.0811, 1.2238, 0.6961), (1.15, 0.94, 0.9441, 1.0999, 0.76), (1.15, 0.94, 0.9497, 1.1603, 1.0274), (1.3, 1.09, 1.084, 1.1784, 0.4602), (1.05, 0.84, 0.843, 1.0491, 1.0048), (1.3, 1.09, 1.0866, 1.1488, 0.3036), (1.05, 0.84, 0.8414, 1.066, 1.0955), (1.15, 0.94, 0.9417, 1.0692, 0.6218)]; fq collisions None; errors []
- v3-C12-amixed-access-fq_codel-r1: lost 0; target egresses failing ['ra-eth1', 'rb-eth1', 'rc-eth1', 'rd-eth1']; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.7957; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.62, '30Hz': 0.99}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0785, 1.2132, 0.6606), (1.05, 0.84, 0.852, 1.053, 0.9855), (1.15, 0.94, 0.925, 1.1085, 0.9002), (1.05, 0.84, 0.8356, 1.0289, 0.9478), (1.15, 0.94, 0.9312, 1.1114, 0.8834), (1.05, 0.84, 0.8504, 1.0353, 0.907), (1.3, 1.09, 1.0848, 1.2311, 0.7177), (1.3, 1.09, 1.0788, 1.2183, 0.6841), (1.15, 0.94, 0.9385, 1.0971, 0.7779)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'ra-eth1': {'bg_packets': 29, 'in_pinned_class': 0, 'flows': []}, 'rb-eth1': {'bg_packets': 29, 'in_pinned_class': 0, 'flows': []}, 'rc-eth1': {'bg_packets': 28, 'in_pinned_class': 0, 'flows': []}, 'rd-eth1': {'bg_packets': 27, 'in_pinned_class': 0, 'flows': []}, 'router-eth1': {'bg_packets': 19, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 1169051, 'in_pinned_class': 1716, 'flows': ['10.101.0.1:5210']}}; errors []
- v3-C12-amixed-access-fq_codel-r2: lost 0; target egresses failing ['ra-eth1', 'rb-eth1', 'rc-eth1', 'rd-eth1']; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 1 (targets 1); cpu idle min 0.818; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.36, '30Hz': 0.92}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8352, 1.0374, 0.989), (1.3, 1.09, 1.0811, 1.2744, 0.9456), (1.15, 0.94, 0.9441, 1.1164, 0.8427), (1.15, 0.94, 0.9497, 1.1251, 0.8579), (1.3, 1.09, 1.084, 1.2315, 0.7216), (1.05, 0.84, 0.843, 1.0256, 0.8932), (1.3, 1.09, 1.0866, 1.2317, 0.7099), (1.05, 0.84, 0.8414, 1.0352, 0.9479), (1.15, 0.94, 0.9417, 1.0915, 0.7327)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'ra-eth1': {'bg_packets': 25, 'in_pinned_class': 0, 'flows': []}, 'rb-eth1': {'bg_packets': 21, 'in_pinned_class': 0, 'flows': []}, 'rc-eth1': {'bg_packets': 21, 'in_pinned_class': 0, 'flows': []}, 'rd-eth1': {'bg_packets': 23, 'in_pinned_class': 0, 'flows': []}, 'router-eth1': {'bg_packets': 24, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 1172219, 'in_pinned_class': 0, 'flows': []}}; errors []
- v3-C12-amixed-access-pfifo-r1: lost 0; target egresses failing ['ra-eth1', 'rb-eth1', 'rc-eth1', 'rd-eth1']; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8358; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.62, '30Hz': 1.01}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0785, 1.1679, 0.4397), (1.05, 0.84, 0.8521, 1.0752, 1.0976), (1.15, 0.94, 0.925, 1.1874, 1.2906), (1.05, 0.84, 0.8356, 1.079, 1.1972), (1.15, 0.94, 0.9312, 1.1121, 0.8893), (1.05, 0.84, 0.8504, 1.0586, 1.0241), (1.3, 1.09, 1.0848, 1.1666, 0.4025), (1.3, 1.09, 1.0788, 1.196, 0.5766), (1.15, 0.94, 0.9385, 1.154, 1.0598)]; fq collisions None; errors []
- v3-C12-amixed-access-pfifo-r2: lost 0; target egresses failing ['ra-eth1', 'rb-eth1', 'rc-eth1', 'rd-eth1']; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8673; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.37, '30Hz': 0.94}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8352, 1.0861, 1.24), (1.3, 1.09, 1.0811, 1.2035, 0.6051), (1.15, 0.94, 0.9441, 1.1134, 0.8366), (1.15, 0.94, 0.9497, 1.1695, 1.0863), (1.3, 1.09, 1.084, 1.202, 0.5832), (1.05, 0.84, 0.843, 1.0876, 1.2087), (1.3, 1.09, 1.0866, 1.1773, 0.4485), (1.05, 0.84, 0.8414, 1.0804, 1.1812), (1.15, 0.94, 0.9417, 1.1078, 0.8211)]; fq collisions None; errors []
- v3-C12-amixed-access-pie-r1: lost 0; target egresses failing ['ra-eth1', 'rb-eth1', 'rc-eth1', 'rd-eth1']; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 1 (targets 1); cpu idle min 0.8447; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.61, '30Hz': 1.02}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0785, 1.2399, 0.7958), (1.05, 0.84, 0.852, 1.0885, 1.1657), (1.15, 0.94, 0.925, 1.1961, 1.3369), (1.05, 0.84, 0.8356, 1.0636, 1.124), (1.15, 0.94, 0.9312, 1.1943, 1.2968), (1.05, 0.84, 0.8504, 1.0741, 1.1029), (1.3, 1.09, 1.0848, 1.3247, 1.1831), (1.3, 1.09, 1.0788, 1.3422, 1.2989), (1.15, 0.94, 0.9385, 1.1988, 1.2833)]; fq collisions None; errors []
- v3-C12-amixed-access-pie-r2: lost 0; target egresses failing ['ra-eth1', 'rb-eth1', 'rc-eth1', 'rd-eth1']; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8652; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.36, '30Hz': 0.91}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8352, 1.0459, 1.0361), (1.3, 1.09, 1.0811, 1.3749, 1.4454), (1.15, 0.94, 0.9441, 1.2029, 1.2732), (1.15, 0.94, 0.9497, 1.2141, 1.3007), (1.3, 1.09, 1.084, 1.3319, 1.2193), (1.05, 0.84, 0.843, 1.0761, 1.1462), (1.3, 1.09, 1.0866, 1.3282, 1.1883), (1.05, 0.84, 0.8414, 1.0746, 1.1472), (1.15, 0.94, 0.9417, 1.1968, 1.2549)]; fq collisions None; errors []
- v3-C13-llong-s030-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.875; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 1.43, '30Hz': 1.42}, 'b': {'1Hz': 1.45, '30Hz': 4.84}, 'up': {'1Hz': 4.53, '30Hz': 1.93}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9426, 1.2053, 1.1795), (1.3, 1.09, 1.0875, 1.2032, 0.5197), (1.3, 1.09, 1.0877, 1.181, 0.4189), (1.3, 1.09, 1.0861, 1.221, 0.6055), (1.3, 1.09, 1.0893, 1.1735, 0.3779), (1.15, 0.94, 0.9394, 1.1137, 0.7823), (1.15, 0.94, 0.9422, 1.1265, 0.8272), (1.3, 1.09, 1.0895, 1.1755, 0.3861), (1.3, 1.09, 1.0903, 1.188, 0.439), (1.15, 0.94, 0.933, 1.1423, 0.9398), (1.15, 0.94, 0.9448, 1.1626, 0.9777), (1.15, 0.94, 0.9402, 1.093, 0.6857)]; fq collisions None; errors []
- v3-C13-llong-s030-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8926; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 1.23, '30Hz': 0.78}, 'b': {'1Hz': 2.96, '30Hz': 1.44}, 'up': {'1Hz': 5.13, '30Hz': 2.2}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9415, 1.1119, 0.7706), (1.15, 0.94, 0.9474, 1.074, 0.5755), (1.3, 1.09, 1.0879, 1.1737, 0.3865), (1.15, 0.94, 0.9386, 1.1177, 0.8144), (1.15, 0.94, 0.9398, 1.1325, 0.8675), (1.3, 1.09, 1.0923, 1.1859, 0.423), (1.3, 1.09, 1.0858, 1.1743, 0.4002), (1.15, 0.94, 0.9408, 1.1526, 0.9577), (1.3, 1.09, 1.0922, 1.2041, 0.5034), (1.3, 1.09, 1.0849, 1.1983, 0.5154), (1.15, 0.94, 0.9412, 1.078, 0.6153), (1.3, 1.09, 1.0895, 1.2276, 0.6276)]; fq collisions None; errors []
- v3-C13-llong-s030-pfifo-r1: lost 0; target egresses failing ['r2-eth2']; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 1 (targets 1); cpu idle min 0.8578; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 1.43, '30Hz': 1.43}, 'b': {'1Hz': 1.44, '30Hz': 4.77}, 'up': {'1Hz': 4.52, '30Hz': 1.97}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9426, 1.2369, 1.3547), (1.3, 1.09, 1.0875, 1.1958, 0.4987), (1.3, 1.09, 1.0877, 1.2464, 0.7306), (1.3, 1.09, 1.0861, 1.2348, 0.6756), (1.3, 1.09, 1.0893, 1.1593, 0.3198), (1.15, 0.94, 0.9394, 1.1428, 0.9303), (1.15, 0.94, 0.9422, 1.1732, 1.0493), (1.3, 1.09, 1.0895, 1.196, 0.4868), (1.3, 1.09, 1.0903, 1.267, 0.8031), (1.15, 0.94, 0.933, 1.1778, 1.1123), (1.15, 0.94, 0.9448, 1.134, 0.8708), (1.15, 0.94, 0.9403, 1.1406, 0.916)]; fq collisions None; errors []
- v3-C13-llong-s030-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 1 (targets 1); cpu idle min 0.8938; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 1.23, '30Hz': 0.74}, 'b': {'1Hz': 2.96, '30Hz': 1.44}, 'up': {'1Hz': 5.14, '30Hz': 2.28}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9415, 1.1363, 0.895), (1.15, 0.94, 0.9474, 1.138, 0.8718), (1.3, 1.09, 1.0879, 1.2215, 0.6174), (1.15, 0.94, 0.9386, 1.1635, 1.0289), (1.15, 0.94, 0.9398, 1.1624, 1.0285), (1.3, 1.09, 1.0923, 1.1671, 0.3434), (1.3, 1.09, 1.0858, 1.1938, 0.4961), (1.15, 0.94, 0.9408, 1.1308, 0.8732), (1.3, 1.09, 1.0922, 1.197, 0.4839), (1.3, 1.09, 1.0849, 1.2049, 0.5486), (1.15, 0.94, 0.9412, 1.1366, 0.9023), (1.3, 1.09, 1.0895, 1.1917, 0.4676)]; fq collisions None; errors []
- v3-C14-rrev-rev-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r0': 0, 'r1': 0}; unmatched total 0 (targets 0); cpu idle min 0.8884; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.15, '30Hz': 0.85}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0817, 1.2926, 0.958), (1.05, 0.84, 0.8441, 1.0421, 0.8993), (1.3, 1.09, 1.0883, 1.2693, 0.8224), (1.15, 0.94, 0.9377, 1.1035, 0.753), (1.15, 0.94, 0.929, 1.0888, 0.7258), (1.05, 0.84, 0.8297, 1.0361, 0.9378), (1.15, 0.94, 0.9479, 1.1123, 0.747), (1.05, 0.84, 0.8452, 1.0424, 0.896), (1.3, 1.09, 1.0781, 1.2263, 0.6733)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r0-eth1': {'bg_packets': 15, 'in_pinned_class': 0, 'flows': []}, 'r0-eth2': {'bg_packets': 17, 'in_pinned_class': 0, 'flows': []}, 'r1-eth2': {'bg_packets': 928693, 'in_pinned_class': 2058, 'flows': ['10.101.0.2:5206']}}; errors []
- v3-C14-rrev-rev-fq_codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r0': 0, 'r1': 0}; unmatched total 0 (targets 0); cpu idle min 0.9041; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.89, '30Hz': 1.1}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8447, 1.0607, 0.9862), (1.05, 0.84, 0.8495, 1.0207, 0.7816), (1.15, 0.94, 0.9508, 1.1291, 0.8144), (1.3, 1.09, 1.1109, 1.2897, 0.8165), (1.3, 1.09, 1.0924, 1.263, 0.7791), (1.15, 0.94, 0.9421, 1.0971, 0.7078), (1.15, 0.94, 0.9402, 1.0919, 0.6929), (1.3, 1.09, 1.0931, 1.2332, 0.6396), (1.05, 0.84, 0.8369, 1.0146, 0.8111)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r0-eth1': {'bg_packets': 19, 'in_pinned_class': 0, 'flows': []}, 'r0-eth2': {'bg_packets': 17, 'in_pinned_class': 0, 'flows': []}, 'r1-eth2': {'bg_packets': 969514, 'in_pinned_class': 0, 'flows': []}}; errors []
- v3-C14-rrev-rev-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r0': 0, 'r1': 0}; unmatched total 0 (targets 0); cpu idle min 0.9082; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.15, '30Hz': 0.87}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0817, 1.2507, 0.7735), (1.05, 0.84, 0.8442, 1.0627, 0.9999), (1.3, 1.09, 1.0883, 1.272, 0.8411), (1.15, 0.94, 0.9377, 1.1797, 1.1077), (1.15, 0.94, 0.929, 1.1752, 1.1267), (1.05, 0.84, 0.8297, 1.0657, 1.0803), (1.15, 0.94, 0.9479, 1.2166, 1.2298), (1.05, 0.84, 0.8452, 1.0837, 1.0919), (1.3, 1.09, 1.0781, 1.2202, 0.6509)]; fq collisions None; errors []
- v3-C14-rrev-rev-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r0': 0, 'r1': 0}; unmatched total 0 (targets 0); cpu idle min 0.907; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.89, '30Hz': 1.12}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8447, 1.0928, 1.138), (1.05, 0.84, 0.8495, 1.0841, 1.0763), (1.15, 0.94, 0.9508, 1.2076, 1.1782), (1.3, 1.09, 1.1109, 1.263, 0.6978), (1.3, 1.09, 1.0924, 1.2678, 0.8048), (1.15, 0.94, 0.9421, 1.1259, 0.8435), (1.15, 0.94, 0.9402, 1.124, 0.8434), (1.3, 1.09, 1.0932, 1.2263, 0.6109), (1.05, 0.84, 0.8369, 1.0728, 1.0819)]; fq collisions None; errors []
- v3-C15-nloss-s030u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9419; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.45, '30Hz': 1.23}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C15-nloss-s030u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.949; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.54, '30Hz': 2.81}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C15-nloss-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9159; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.45, '30Hz': 1.25}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C15-nloss-s030u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9498; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.54, '30Hz': 2.74}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-legacy-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9565; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-legacy-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9519; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-legacy-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9548; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-legacy-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9392; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s010u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9548; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.17, '30Hz': 1.68}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s010u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9416; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.61, '30Hz': 2.55}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s010u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9557; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.17, '30Hz': 1.72}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s010u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9423; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.61, '30Hz': 2.5}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s010u085-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9541; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.17, '30Hz': 1.69}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s010u085-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9388; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 2.61}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s010u085-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.946; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.17, '30Hz': 1.7}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s010u085-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9371; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.61, '30Hz': 2.49}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u050-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.951; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.57, '30Hz': 2.27}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u050-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9453; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.16, '30Hz': 1.64}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u050-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9182; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.57, '30Hz': 2.26}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u050-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9463; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.16, '30Hz': 1.63}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9523; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.57, '30Hz': 2.11}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9486; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.16, '30Hz': 1.65}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9506; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.57, '30Hz': 2.17}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.946; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.16, '30Hz': 1.59}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u085-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9517; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.57, '30Hz': 2.18}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u085-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9397; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.16, '30Hz': 1.62}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u085-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9573; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.57, '30Hz': 2.23}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s030u085-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9564; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.16, '30Hz': 1.59}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u050-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9518; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.35, '30Hz': 3.61}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u050-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9385; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.59, '30Hz': 2.49}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u050-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9545; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.36, '30Hz': 3.6}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u050-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9399; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.59, '30Hz': 2.47}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9573; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.36, '30Hz': 3.65}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9422; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.59, '30Hz': 2.43}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9518; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.35, '30Hz': 3.71}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9477; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.59, '30Hz': 2.58}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u085-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9497; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.35, '30Hz': 3.64}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u085-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9408; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.59, '30Hz': 2.34}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u085-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9573; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.36, '30Hz': 3.64}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1a-calm-s065u085-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9362; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.58, '30Hz': 2.5}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1b-calm-split4-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 1 (targets 1); cpu idle min 0.9016; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.64, '30Hz': 0.52}, 'b': {'1Hz': 2.34, '30Hz': 2.96}, 'up': {'1Hz': 2.0, '30Hz': 4.23}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1b-calm-split4-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.9014; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 3.97, '30Hz': 0.43}, 'b': {'1Hz': 2.77, '30Hz': 1.19}, 'up': {'1Hz': 1.33, '30Hz': 6.97}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1b-calm-tree16-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8252; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 5.37, '30Hz': 3.21}, 'B': {'1Hz': 2.41, '30Hz': 1.12}, 'C': {'1Hz': 3.71, '30Hz': 2.94}, 'D': {'1Hz': 3.42, '30Hz': 1.83}, 'X': {'1Hz': 0.57, '30Hz': 3.88}, 'Y': {'1Hz': 2.3, '30Hz': 0.66}, 'root': {'1Hz': 4.05, '30Hz': 1.78}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1b-calm-tree16-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.789; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 0.8, '30Hz': 3.45}, 'B': {'1Hz': 2.08, '30Hz': 2.6}, 'C': {'1Hz': 2.13, '30Hz': 1.53}, 'D': {'1Hz': 7.02, '30Hz': 2.12}, 'X': {'1Hz': 2.43, '30Hz': 4.67}, 'Y': {'1Hz': 2.36, '30Hz': 2.44}, 'root': {'1Hz': 2.09, '30Hz': 2.71}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1b-calm-uneven-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.9084; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.18, '30Hz': 4.28}, 'B': {'1Hz': 0.57, '30Hz': 3.84}, 'C': {'1Hz': 5.09, '30Hz': 1.98}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C1b-calm-uneven-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8881; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 0.92, '30Hz': 1.6}, 'B': {'1Hz': 2.43, '30Hz': 4.56}, 'C': {'1Hz': 2.91, '30Hz': 5.56}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C2-sburst-s030u070-cake-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9464; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.42}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.155, 0.9964), (1.05, 0.84, 0.8482, 1.0648, 0.999), (1.3, 1.09, 1.0808, 1.3013, 1.0174), (1.15, 0.94, 0.9408, 1.1568, 0.9968), (1.3, 1.09, 1.0827, 1.299, 0.9977), (1.15, 0.94, 0.9308, 1.1464, 0.9949), (1.05, 0.84, 0.8453, 1.0549, 0.9673), (1.05, 0.84, 0.8352, 1.0521, 1.0006), (1.05, 0.84, 0.8421, 1.0597, 1.004), (1.15, 0.94, 0.9389, 1.1542, 0.9936), (1.05, 0.84, 0.838, 1.0515, 0.9848), (1.3, 1.09, 1.0877, 1.3076, 1.0148), (1.15, 0.94, 0.9537, 1.1685, 0.991), (1.3, 1.09, 1.0928, 1.3118, 1.0107), (1.3, 1.09, 1.0806, 1.292, 0.9754), (1.05, 0.84, 0.8348, 1.0423, 0.9573), (1.3, 1.09, 1.0883, 1.3065, 1.0067), (1.15, 0.94, 0.9348, 1.1502, 0.9939)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-cake-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9234; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.04}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.3017, 0.9929), (1.15, 0.94, 0.9445, 1.1632, 1.0089), (1.15, 0.94, 0.9415, 1.1579, 0.9981), (1.05, 0.84, 0.8444, 1.0608, 0.9985), (1.15, 0.94, 0.9365, 1.1511, 0.9903), (1.05, 0.84, 0.8358, 1.0511, 0.9934), (1.05, 0.84, 0.8432, 1.0646, 1.0215), (1.15, 0.94, 0.9448, 1.1585, 0.986), (1.3, 1.09, 1.0947, 1.3126, 1.0054), (1.3, 1.09, 1.0807, 1.3033, 1.0271), (1.3, 1.09, 1.0873, 1.3035, 0.9972), (1.3, 1.09, 1.0973, 1.3124, 0.9925), (1.15, 0.94, 0.9467, 1.1601, 0.9844), (1.05, 0.84, 0.8343, 1.047, 0.9815), (1.05, 0.84, 0.8375, 1.054, 0.9991), (1.05, 0.84, 0.8423, 1.059, 1.0001), (1.15, 0.94, 0.9446, 1.1585, 0.9872), (1.3, 1.09, 1.0943, 1.3133, 1.0101)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 1}; unmatched total 1 (targets 1); cpu idle min 0.9497; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.45}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1181, 0.8116), (1.05, 0.84, 0.8482, 1.0631, 0.9739), (1.3, 1.09, 1.0808, 1.2226, 0.6429), (1.15, 0.94, 0.9408, 1.0931, 0.6902), (1.3, 1.09, 1.0827, 1.1597, 0.349), (1.15, 0.94, 0.9308, 1.1222, 0.8677), (1.05, 0.84, 0.8453, 1.0498, 0.9272), (1.05, 0.84, 0.8352, 1.0505, 0.9757), (1.05, 0.84, 0.8421, 1.0506, 0.9449), (1.15, 0.94, 0.9389, 1.0668, 0.5799), (1.05, 0.84, 0.838, 1.0443, 0.9349), (1.3, 1.09, 1.0877, 1.1978, 0.4993), (1.15, 0.94, 0.9537, 1.1474, 0.8778), (1.3, 1.09, 1.0928, 1.1894, 0.438), (1.3, 1.09, 1.0806, 1.2193, 0.6284), (1.05, 0.84, 0.8348, 1.0389, 0.9248), (1.3, 1.09, 1.0883, 1.1567, 0.3103), (1.15, 0.94, 0.9348, 1.0938, 0.7207)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.937; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.01}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1878, 0.4607), (1.15, 0.94, 0.9445, 1.1403, 0.8906), (1.15, 0.94, 0.9415, 1.0729, 0.5973), (1.05, 0.84, 0.8444, 1.0435, 0.9058), (1.15, 0.94, 0.9365, 1.1421, 0.9349), (1.05, 0.84, 0.8358, 1.0547, 0.9958), (1.05, 0.84, 0.8432, 1.0567, 0.9709), (1.15, 0.94, 0.9448, 1.1572, 0.9658), (1.3, 1.09, 1.0947, 1.1827, 0.4001), (1.3, 1.09, 1.0807, 1.2513, 0.7759), (1.3, 1.09, 1.0873, 1.1479, 0.2753), (1.3, 1.09, 1.0972, 1.1892, 0.4182), (1.15, 0.94, 0.9467, 1.1565, 0.9539), (1.05, 0.84, 0.8343, 1.0378, 0.9256), (1.05, 0.84, 0.8375, 1.0481, 0.9576), (1.05, 0.84, 0.8423, 1.0472, 0.932), (1.15, 0.94, 0.9446, 1.0761, 0.5982), (1.3, 1.09, 1.0943, 1.2376, 0.6514)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9418; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.48}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.113, 0.7799), (1.05, 0.84, 0.8482, 1.0294, 0.8123), (1.3, 1.09, 1.0808, 1.2291, 0.665), (1.15, 0.94, 0.9408, 1.1047, 0.7348), (1.3, 1.09, 1.0827, 1.2244, 0.6352), (1.15, 0.94, 0.9308, 1.0918, 0.7217), (1.05, 0.84, 0.8453, 1.0487, 0.9121), (1.05, 0.84, 0.8352, 1.0321, 0.8826), (1.05, 0.84, 0.8421, 1.0435, 0.9028), (1.15, 0.94, 0.9389, 1.0931, 0.6912), (1.05, 0.84, 0.838, 1.0259, 0.8425), (1.3, 1.09, 1.0877, 1.2267, 0.6235), (1.15, 0.94, 0.9537, 1.1141, 0.719), (1.3, 1.09, 1.0928, 1.227, 0.6019), (1.3, 1.09, 1.0806, 1.231, 0.6741), (1.05, 0.84, 0.8348, 1.0321, 0.8845), (1.3, 1.09, 1.0883, 1.2436, 0.6962), (1.15, 0.94, 0.9348, 1.0864, 0.6794)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 17, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 1094955, 'in_pinned_class': 1462, 'flows': ['10.101.0.1:5207', '10.101.0.1:5213']}}; errors []
- v3-C2-sburst-s030u070-fq_codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9251; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.77, '30Hz': 0.96}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.2685, 0.8198), (1.15, 0.94, 0.9445, 1.0928, 0.6681), (1.15, 0.94, 0.9415, 1.0999, 0.7132), (1.05, 0.84, 0.8444, 1.041, 0.8857), (1.15, 0.94, 0.9365, 1.0828, 0.659), (1.05, 0.84, 0.8358, 1.0277, 0.8645), (1.05, 0.84, 0.8432, 1.0328, 0.8541), (1.15, 0.94, 0.9448, 1.1059, 0.7256), (1.3, 1.09, 1.0947, 1.2343, 0.6288), (1.3, 1.09, 1.0807, 1.2556, 0.7877), (1.3, 1.09, 1.0873, 1.2255, 0.6226), (1.3, 1.09, 1.0973, 1.2323, 0.6082), (1.15, 0.94, 0.9467, 1.1002, 0.6915), (1.05, 0.84, 0.8343, 1.0334, 0.8972), (1.05, 0.84, 0.8375, 1.0319, 0.8756), (1.05, 0.84, 0.8423, 1.0231, 0.8147), (1.15, 0.94, 0.9446, 1.0989, 0.6949), (1.3, 1.09, 1.0943, 1.2405, 0.6586)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 27, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 1117664, 'in_pinned_class': 455, 'flows': ['10.101.0.1:5206']}}; errors []
- v3-C2-sburst-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9453; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.59, '30Hz': 1.44}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1313, 0.8757), (1.05, 0.84, 0.8482, 1.101, 1.1511), (1.3, 1.09, 1.0808, 1.2824, 0.9181), (1.15, 0.94, 0.9408, 1.1628, 1.0111), (1.3, 1.09, 1.0827, 1.1801, 0.4433), (1.15, 0.94, 0.9308, 1.0937, 0.7419), (1.05, 0.84, 0.8453, 1.0789, 1.0642), (1.05, 0.84, 0.8352, 1.0845, 1.1352), (1.05, 0.84, 0.8421, 1.0903, 1.1302), (1.15, 0.94, 0.9389, 1.137, 0.9022), (1.05, 0.84, 0.838, 1.0666, 1.0412), (1.3, 1.09, 1.0877, 1.1946, 0.4872), (1.15, 0.94, 0.9537, 1.1373, 0.836), (1.3, 1.09, 1.0928, 1.1938, 0.4602), (1.3, 1.09, 1.0806, 1.2406, 0.7288), (1.05, 0.84, 0.8348, 1.0337, 0.9057), (1.3, 1.09, 1.0883, 1.1756, 0.3974), (1.15, 0.94, 0.9348, 1.125, 0.8662)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9262; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.0}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.2015, 0.5244), (1.15, 0.94, 0.9445, 1.1991, 1.1614), (1.15, 0.94, 0.9415, 1.1364, 0.8888), (1.05, 0.84, 0.8444, 1.0858, 1.1011), (1.15, 0.94, 0.9365, 1.1755, 1.0899), (1.05, 0.84, 0.8358, 1.0664, 1.0519), (1.05, 0.84, 0.8432, 1.0649, 1.0109), (1.15, 0.94, 0.9448, 1.1386, 0.8837), (1.3, 1.09, 1.0947, 1.1675, 0.332), (1.3, 1.09, 1.0807, 1.2301, 0.6814), (1.3, 1.09, 1.0873, 1.1655, 0.3566), (1.3, 1.09, 1.0973, 1.1913, 0.4288), (1.15, 0.94, 0.9467, 1.2096, 1.1991), (1.05, 0.84, 0.8343, 1.0668, 1.0609), (1.05, 0.84, 0.8375, 1.0834, 1.1215), (1.05, 0.84, 0.8423, 1.0891, 1.1256), (1.15, 0.94, 0.9446, 1.1269, 0.8316), (1.3, 1.09, 1.0944, 1.1934, 0.4517)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-pie-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.7607; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.51}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.2088, 1.236), (1.05, 0.84, 0.8482, 1.0875, 1.0962), (1.3, 1.09, 1.0808, 1.3382, 1.1795), (1.15, 0.94, 0.9408, 1.2111, 1.2385), (1.3, 1.09, 1.0827, 1.3157, 1.0673), (1.15, 0.94, 0.9308, 1.1739, 1.1137), (1.05, 0.84, 0.8453, 1.0559, 0.9651), (1.05, 0.84, 0.8352, 1.0662, 1.0584), (1.05, 0.84, 0.8421, 1.0779, 1.0801), (1.15, 0.94, 0.9389, 1.2006, 1.199), (1.05, 0.84, 0.838, 1.0635, 1.0329), (1.3, 1.09, 1.0877, 1.3058, 0.9995), (1.15, 0.94, 0.9537, 1.203, 1.1419), (1.3, 1.09, 1.0928, 1.2912, 0.9093), (1.3, 1.09, 1.0806, 1.2932, 0.974), (1.05, 0.84, 0.8348, 1.0416, 0.9472), (1.3, 1.09, 1.0883, 1.3077, 1.0053), (1.15, 0.94, 0.9348, 1.1999, 1.2146)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-pie-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9377; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 0.98}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.4155, 1.5041), (1.15, 0.94, 0.9445, 1.2028, 1.1807), (1.15, 0.94, 0.9415, 1.2066, 1.2117), (1.05, 0.84, 0.8444, 1.0793, 1.0741), (1.15, 0.94, 0.9365, 1.195, 1.1819), (1.05, 0.84, 0.8358, 1.0614, 1.0317), (1.05, 0.84, 0.8432, 1.0846, 1.1038), (1.15, 0.94, 0.9448, 1.2169, 1.2437), (1.3, 1.09, 1.0947, 1.3726, 1.2708), (1.3, 1.09, 1.0807, 1.3362, 1.1682), (1.3, 1.09, 1.0873, 1.281, 0.8856), (1.3, 1.09, 1.0973, 1.3308, 1.0679), (1.15, 0.94, 0.9467, 1.2102, 1.2046), (1.05, 0.84, 0.8343, 1.0613, 1.0382), (1.05, 0.84, 0.8375, 1.0706, 1.0658), (1.05, 0.84, 0.8423, 1.0773, 1.0746), (1.15, 0.94, 0.9446, 1.2034, 1.1833), (1.3, 1.09, 1.0943, 1.3153, 1.0103)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-red-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9447; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.46}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.2024, 1.2135), (1.05, 0.84, 0.8482, 1.0831, 1.0817), (1.3, 1.09, 1.0808, 1.2369, 0.7191), (1.15, 0.94, 0.9408, 1.1602, 1.0108), (1.3, 1.09, 1.0827, 1.3401, 1.1857), (1.15, 0.94, 0.9308, 1.1792, 1.1442), (1.05, 0.84, 0.8453, 1.063, 1.0031), (1.05, 0.84, 0.8352, 1.063, 1.0493), (1.05, 0.84, 0.8421, 1.0728, 1.0623), (1.15, 0.94, 0.9389, 1.1661, 1.0469), (1.05, 0.84, 0.838, 1.0568, 1.0076), (1.3, 1.09, 1.0877, 1.2972, 0.9653), (1.15, 0.94, 0.9537, 1.1864, 1.0719), (1.3, 1.09, 1.0928, 1.314, 1.0191), (1.3, 1.09, 1.0806, 1.3343, 1.1687), (1.05, 0.84, 0.8348, 1.045, 0.968), (1.3, 1.09, 1.0883, 1.3557, 1.2317), (1.15, 0.94, 0.9348, 1.1902, 1.1767)]; fq collisions None; errors []
- v3-C2-sburst-s030u070-red-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.943; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.02}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.4266, 1.5683), (1.15, 0.94, 0.9445, 1.2039, 1.1962), (1.15, 0.94, 0.9415, 1.1916, 1.1532), (1.05, 0.84, 0.8444, 1.0744, 1.0609), (1.15, 0.94, 0.9365, 1.1619, 1.0395), (1.05, 0.84, 0.8358, 1.0583, 1.026), (1.05, 0.84, 0.8432, 1.0704, 1.0474), (1.15, 0.94, 0.9448, 1.2, 1.1767), (1.3, 1.09, 1.0947, 1.3003, 0.9479), (1.3, 1.09, 1.0807, 1.2551, 0.8042), (1.3, 1.09, 1.0873, 1.3394, 1.1625), (1.3, 1.09, 1.0972, 1.3405, 1.1216), (1.15, 0.94, 0.9467, 1.1852, 1.0998), (1.05, 0.84, 0.8343, 1.0576, 1.0299), (1.05, 0.84, 0.8375, 1.0639, 1.044), (1.05, 0.84, 0.8423, 1.07, 1.0498), (1.15, 0.94, 0.9446, 1.1968, 1.1629), (1.3, 1.09, 1.0943, 1.2962, 0.9306)]; fq collisions None; errors []
- v3-C3a-sburst-s010u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9474; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.27, '30Hz': 1.96}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 1.08, 1.0789, 1.1451, 0.9015), (1.05, 0.98, 0.9864, 1.0656, 1.077), (1.3, 1.23, 1.2251, 1.2663, 0.5615), (1.15, 1.08, 1.0764, 1.127, 0.6889), (1.3, 1.23, 1.2261, 1.2546, 0.3868), (1.15, 1.08, 1.0688, 1.1312, 0.8501), (1.05, 0.98, 0.9821, 1.0539, 0.9781), (1.05, 0.98, 0.9782, 1.0564, 1.0642), (1.05, 0.98, 0.9786, 1.0522, 1.001), (1.15, 1.08, 1.0801, 1.1282, 0.6555), (1.05, 0.98, 0.9741, 1.0457, 0.9752), (1.3, 1.23, 1.2261, 1.2569, 0.4189), (1.15, 1.08, 1.0863, 1.1533, 0.9119), (1.3, 1.23, 1.2337, 1.2624, 0.3911), (1.3, 1.23, 1.2326, 1.2727, 0.5452), (1.05, 0.98, 0.9794, 1.0511, 0.9767), (1.3, 1.23, 1.2264, 1.2541, 0.376), (1.15, 1.08, 1.0663, 1.1271, 0.8271)]; fq collisions None; errors []
- v3-C3a-sburst-s010u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9324; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.91, '30Hz': 3.38}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.23, 1.2236, 1.258, 0.465), (1.15, 1.08, 1.0715, 1.1465, 1.0137), (1.15, 1.08, 1.0794, 1.1209, 0.5606), (1.05, 0.98, 0.9835, 1.0565, 0.9863), (1.15, 1.08, 1.0785, 1.1374, 0.7963), (1.05, 0.98, 0.9892, 1.0641, 1.0116), (1.05, 0.98, 0.9908, 1.0673, 1.0343), (1.15, 1.08, 1.0804, 1.1383, 0.7826), (1.3, 1.23, 1.2354, 1.2609, 0.3454), (1.3, 1.23, 1.2345, 1.2724, 0.5117), (1.3, 1.23, 1.2318, 1.2612, 0.3977), (1.3, 1.23, 1.2427, 1.2731, 0.4111), (1.15, 1.08, 1.0786, 1.1249, 0.6255), (1.05, 0.98, 0.9723, 1.0434, 0.9617), (1.05, 0.98, 0.976, 1.0509, 1.0121), (1.05, 0.98, 0.9757, 1.0492, 0.9937), (1.15, 1.08, 1.0861, 1.1522, 0.8934), (1.3, 1.23, 1.2198, 1.2637, 0.5937)]; fq collisions None; errors []
- v3-C3a-sburst-s010u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9427; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.27, '30Hz': 1.95}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 1.08, 1.0789, 1.141, 0.8498), (1.05, 0.98, 0.9864, 1.0684, 1.1209), (1.3, 1.23, 1.2251, 1.2708, 0.6249), (1.15, 1.08, 1.0764, 1.1372, 0.8316), (1.3, 1.23, 1.2261, 1.2634, 0.5092), (1.15, 1.08, 1.0688, 1.1377, 0.9428), (1.05, 0.98, 0.9821, 1.0586, 1.0469), (1.05, 0.98, 0.9782, 1.065, 1.1875), (1.05, 0.98, 0.9786, 1.0622, 1.1426), (1.15, 1.08, 1.0801, 1.1456, 0.8959), (1.05, 0.98, 0.9741, 1.0524, 1.0707), (1.3, 1.23, 1.2261, 1.2665, 0.5525), (1.15, 1.08, 1.0863, 1.1564, 0.9582), (1.3, 1.23, 1.2337, 1.2796, 0.6274), (1.3, 1.23, 1.2326, 1.2829, 0.6872), (1.05, 0.98, 0.9794, 1.0515, 0.9873), (1.3, 1.23, 1.2264, 1.2597, 0.4555), (1.15, 1.08, 1.0663, 1.1266, 0.8244)]; fq collisions None; errors []
- v3-C3a-sburst-s010u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9319; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.91, '30Hz': 3.34}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.23, 1.2236, 1.2767, 0.7331), (1.15, 1.08, 1.0715, 1.1555, 1.1598), (1.15, 1.08, 1.0794, 1.1352, 0.7704), (1.05, 0.98, 0.9835, 1.0616, 1.0774), (1.15, 1.08, 1.0785, 1.1572, 1.087), (1.05, 0.98, 0.9892, 1.0591, 0.9641), (1.05, 0.98, 0.9908, 1.0726, 1.1304), (1.15, 1.08, 1.0804, 1.1312, 0.7003), (1.3, 1.23, 1.2353, 1.2686, 0.4596), (1.3, 1.23, 1.2345, 1.2724, 0.5227), (1.3, 1.23, 1.2318, 1.266, 0.4716), (1.3, 1.23, 1.2427, 1.2762, 0.4626), (1.15, 1.08, 1.0786, 1.1358, 0.7903), (1.05, 0.98, 0.9723, 1.0482, 1.0482), (1.05, 0.98, 0.976, 1.0623, 1.1918), (1.05, 0.98, 0.9757, 1.0571, 1.1236), (1.15, 1.08, 1.0861, 1.1562, 0.9677), (1.3, 1.23, 1.2197, 1.2744, 0.7547)]; fq collisions None; errors []
- v3-C3a-sburst-s065u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9476; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 4.03, '30Hz': 2.29}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.695, 0.6911, 1.1222, 0.9041), (1.05, 0.595, 0.6015, 1.1017, 1.0488), (1.3, 0.845, 0.8512, 1.1619, 0.6516), (1.15, 0.695, 0.6945, 1.0656, 0.7781), (1.3, 0.845, 0.8464, 1.1357, 0.6067), (1.15, 0.695, 0.6975, 1.1288, 0.9043), (1.05, 0.595, 0.5982, 1.059, 0.9663), (1.05, 0.595, 0.5948, 1.0865, 1.031), (1.05, 0.595, 0.5821, 1.0584, 0.9986), (1.15, 0.695, 0.6967, 1.1009, 0.8475), (1.05, 0.595, 0.588, 1.0568, 0.983), (1.3, 0.845, 0.8266, 1.0783, 0.5279), (1.15, 0.695, 0.7139, 1.1005, 0.8107), (1.3, 0.845, 0.8643, 1.0961, 0.4859), (1.3, 0.845, 0.8609, 1.1685, 0.6449), (1.05, 0.595, 0.5934, 1.0357, 0.9274), (1.3, 0.845, 0.8419, 1.1043, 0.5502), (1.15, 0.695, 0.6959, 1.0636, 0.771)]; fq collisions None; errors []
- v3-C3a-sburst-s065u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.938; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.94, '30Hz': 2.31}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 0.845, 0.831, 1.1811, 0.733), (1.15, 0.695, 0.7047, 1.0774, 0.7802), (1.15, 0.695, 0.6981, 1.0971, 0.8352), (1.05, 0.595, 0.5945, 1.0864, 1.0298), (1.15, 0.695, 0.6947, 1.101, 0.8505), (1.05, 0.595, 0.6145, 1.0743, 0.9624), (1.05, 0.595, 0.6197, 1.0427, 0.8854), (1.15, 0.695, 0.7017, 1.0596, 0.7493), (1.3, 0.845, 0.8451, 1.1137, 0.5622), (1.3, 0.845, 0.848, 1.2101, 0.7581), (1.3, 0.845, 0.8496, 1.1255, 0.5776), (1.3, 0.845, 0.8579, 1.137, 0.5842), (1.15, 0.695, 0.6874, 1.1296, 0.9257), (1.05, 0.595, 0.5919, 1.0531, 0.9654), (1.05, 0.595, 0.5923, 1.0824, 1.026), (1.05, 0.595, 0.5953, 1.0571, 0.9668), (1.15, 0.695, 0.7007, 1.1154, 0.868), (1.3, 0.845, 0.8256, 1.1458, 0.6703)]; fq collisions None; errors []
- v3-C3a-sburst-s065u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9285; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 4.03, '30Hz': 2.19}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.695, 0.6911, 1.2451, 1.1599), (1.05, 0.595, 0.6016, 1.1538, 1.1562), (1.3, 0.845, 0.8511, 1.1976, 0.7253), (1.15, 0.695, 0.6945, 1.1174, 0.8854), (1.3, 0.845, 0.8464, 1.1752, 0.6884), (1.15, 0.695, 0.6975, 1.2, 1.052), (1.05, 0.595, 0.5982, 1.0684, 0.9846), (1.05, 0.595, 0.5948, 1.1567, 1.1764), (1.05, 0.595, 0.5821, 1.0779, 1.0379), (1.15, 0.695, 0.6967, 1.1946, 1.0424), (1.05, 0.595, 0.588, 1.1108, 1.0946), (1.3, 0.845, 0.8266, 1.1874, 0.7554), (1.15, 0.695, 0.7139, 1.2087, 1.036), (1.3, 0.845, 0.8643, 1.2046, 0.7125), (1.3, 0.845, 0.8609, 1.1574, 0.6207), (1.05, 0.595, 0.5934, 1.0382, 0.9314), (1.3, 0.845, 0.8419, 1.159, 0.6639), (1.15, 0.695, 0.6959, 1.1464, 0.9431)]; fq collisions None; errors []
- v3-C3a-sburst-s065u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.938; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.94, '30Hz': 2.31}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 0.845, 0.831, 1.2166, 0.8132), (1.15, 0.695, 0.7047, 1.173, 0.9874), (1.15, 0.695, 0.6981, 1.1438, 0.9398), (1.05, 0.595, 0.5945, 1.1477, 1.1665), (1.15, 0.695, 0.6947, 1.1464, 0.9523), (1.05, 0.595, 0.6145, 1.12, 1.0658), (1.05, 0.595, 0.6197, 1.166, 1.152), (1.15, 0.695, 0.7017, 1.1359, 0.9155), (1.3, 0.845, 0.8451, 1.1946, 0.7369), (1.3, 0.845, 0.848, 1.324, 1.0037), (1.3, 0.845, 0.8496, 1.1606, 0.6558), (1.3, 0.845, 0.8578, 1.1309, 0.5756), (1.15, 0.695, 0.6874, 1.1383, 0.9508), (1.05, 0.595, 0.5919, 1.1089, 1.0902), (1.05, 0.595, 0.5923, 1.1164, 1.1052), (1.05, 0.595, 0.5953, 1.1195, 1.1053), (1.15, 0.695, 0.7007, 1.1824, 1.0158), (1.3, 0.845, 0.8256, 1.2376, 0.8688)]; fq collisions None; errors []
- v3-C3b-sburst-legacy-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9468; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C3b-sburst-legacy-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9422; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C4-sramp-s030u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.951; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.09, '30Hz': 1.19}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C4-sramp-s030u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9374; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.13, '30Hz': 2.98}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C4-sramp-s030u070-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9383; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.09, '30Hz': 1.16}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 15, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 739270, 'in_pinned_class': 1270, 'flows': ['10.101.0.1:5209']}}; errors []
- v3-C4-sramp-s030u070-fq_codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.935; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.13, '30Hz': 3.01}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 10, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 708323, 'in_pinned_class': 1770, 'flows': ['10.101.0.1:5206']}}; errors []
- v3-C4-sramp-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9527; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.08, '30Hz': 1.18}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C4-sramp-s030u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9392; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.13, '30Hz': 2.99}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C4-sramp-s030u070-pie-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9506; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.08, '30Hz': 1.22}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C4-sramp-s030u070-pie-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9437; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.13, '30Hz': 2.94}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C5-stcp-s030u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9466; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.32, '30Hz': 1.32}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C5-stcp-s030u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9435; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.65, '30Hz': 1.14}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C5-stcp-s030u070-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.946; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.32, '30Hz': 1.34}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 20, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 1072499, 'in_pinned_class': 0, 'flows': []}}; errors []
- v3-C5-stcp-s030u070-fq_codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9175; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.65, '30Hz': 1.11}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 20, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 1060914, 'in_pinned_class': 16, 'flows': ['10.101.0.1:5217']}}; errors []
- v3-C5-stcp-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9497; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.32, '30Hz': 1.32}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C5-stcp-s030u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9125; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.65, '30Hz': 1.09}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C5-stcp-s030u070-pie-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9469; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.32, '30Hz': 1.27}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C5-stcp-s030u070-pie-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9383; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.65, '30Hz': 1.14}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C6-sjoin-s030u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9466; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.61, '30Hz': 1.32}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C6-sjoin-s030u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9351; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.66, '30Hz': 2.05}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C6-sjoin-s030u070-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9427; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.61, '30Hz': 1.28}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 12, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 805063, 'in_pinned_class': 0, 'flows': []}}; errors []
- v3-C6-sjoin-s030u070-fq_codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9249; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.66, '30Hz': 2.11}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 15, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 801335, 'in_pinned_class': 49280, 'flows': ['10.101.0.1:5205']}}; errors []
- v3-C6-sjoin-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9474; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 5.61, '30Hz': 1.31}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C6-sjoin-s030u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9457; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.66, '30Hz': 2.1}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-C7-hhier-s030-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8841; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.33, '30Hz': 2.66}, 'b': {'1Hz': 1.9, '30Hz': 1.72}, 'up': {'1Hz': 6.39, '30Hz': 1.91}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9368, 1.1827, 1.1127), (1.15, 0.94, 0.9467, 1.1649, 0.9827), (1.3, 1.09, 1.0898, 1.172, 0.3721), (1.15, 0.94, 0.939, 1.0293, 0.4085), (1.15, 0.94, 0.9388, 1.0715, 0.5991), (1.15, 0.94, 0.9422, 1.0968, 0.6997), (1.15, 0.94, 0.9361, 1.1069, 0.7693), (1.3, 1.09, 1.0828, 1.2599, 0.7973), (1.15, 0.94, 0.9463, 1.0934, 0.6642), (1.3, 1.09, 1.0899, 1.1833, 0.4227), (1.3, 1.09, 1.0871, 1.1745, 0.3935), (1.3, 1.09, 1.0824, 1.2309, 0.6723), (1.05, 0.84, 0.8393, 1.0624, 1.0046), (1.05, 0.84, 0.8398, 1.0641, 1.015), (1.15, 0.94, 0.9457, 1.0981, 0.6866), (1.15, 0.94, 0.9417, 1.1225, 0.8162), (1.3, 1.09, 1.0838, 1.2713, 0.8485), (1.3, 1.09, 1.0779, 1.2418, 0.7378), (1.3, 1.09, 1.0786, 1.1936, 0.5178), (1.05, 0.84, 0.8365, 1.0443, 0.9381), (1.15, 0.94, 0.945, 1.1527, 0.9353), (1.15, 0.94, 0.934, 1.1198, 0.8387), (1.15, 0.94, 0.9373, 1.1072, 0.769), (1.15, 0.94, 0.9397, 1.0805, 0.6341), (1.05, 0.84, 0.8371, 1.045, 0.9363), (1.15, 0.94, 0.9411, 1.1477, 0.935), (1.15, 0.94, 0.9469, 1.1962, 1.1284), (1.15, 0.94, 0.9559, 1.1755, 0.9888), (1.3, 1.09, 1.0878, 1.1805, 0.4197), (1.3, 1.09, 1.0994, 1.1856, 0.3882), (1.3, 1.09, 1.0915, 1.2484, 0.7103), (1.15, 0.94, 0.9394, 1.0953, 0.7059), (1.3, 1.09, 1.0956, 1.1237, 0.1273), (1.3, 1.09, 1.0932, 1.1522, 0.266), (1.05, 0.84, 0.8293, 1.0435, 0.9697), (1.15, 0.94, 0.9302, 1.1328, 0.9122), (1.3, 1.09, 1.0785, 1.2603, 0.8229), (1.3, 1.09, 1.0824, 1.2625, 0.8108), (1.05, 0.84, 0.8435, 1.051, 0.9392), (1.3, 1.09, 1.1142, 1.1912, 0.3486), (1.3, 1.09, 1.0818, 1.2051, 0.5562), (1.3, 1.09, 1.0882, 1.2058, 0.5325), (1.3, 1.09, 1.0878, 1.2377, 0.6748), (1.3, 1.09, 1.092, 1.1862, 0.4251), (1.15, 0.94, 0.9373, 1.0333, 0.4345), (1.15, 0.94, 0.9385, 1.1067, 0.7592), (1.05, 0.84, 0.8429, 1.0526, 0.9446), (1.15, 0.94, 0.9518, 1.1678, 0.9777), (1.05, 0.84, 0.8389, 1.0514, 0.9593), (1.3, 1.09, 1.0958, 1.2128, 0.5294), (1.3, 1.09, 1.0916, 1.2312, 0.6283), (1.15, 0.94, 0.935, 1.1442, 0.9472), (1.15, 0.94, 0.9547, 1.1796, 1.013), (1.3, 1.09, 1.0908, 1.2267, 0.6152), (1.3, 1.09, 1.0867, 1.1888, 0.4597), (1.15, 0.94, 0.9393, 1.1222, 0.8278), (1.15, 0.94, 0.9308, 1.1327, 0.9091), (1.3, 1.09, 1.0933, 1.138, 0.2023), (1.3, 1.09, 1.0866, 1.1687, 0.3706), (1.15, 0.94, 0.9422, 1.1449, 0.9175), (1.15, 0.94, 0.95, 1.136, 0.8377), (1.15, 0.94, 0.946, 1.1143, 0.7616), (1.15, 0.94, 0.9377, 1.0729, 0.6086), (1.3, 1.09, 1.0983, 1.2708, 0.7808), (1.3, 1.09, 1.0838, 1.2458, 0.7297), (1.15, 0.94, 0.9436, 1.0651, 0.5499), (1.15, 0.94, 0.9388, 1.1022, 0.7376), (1.3, 1.09, 1.0917, 1.1753, 0.3772), (1.3, 1.09, 1.0876, 1.1907, 0.465), (1.3, 1.09, 1.0842, 1.161, 0.3474), (1.3, 1.09, 1.097, 1.1903, 0.4204), (1.3, 1.09, 1.0877, 1.191, 0.4655), (1.15, 0.94, 0.9486, 1.1168, 0.7615), (1.15, 0.94, 0.9396, 1.1213, 0.8183), (1.05, 0.84, 0.8366, 1.0712, 1.0592)]; fq collisions None; errors []
- v3-C7-hhier-s030-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8792; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.01, '30Hz': 1.22}, 'b': {'1Hz': 0.86, '30Hz': 3.81}, 'up': {'1Hz': 2.07, '30Hz': 3.58}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9383, 1.1765, 1.0772), (1.3, 1.09, 1.0855, 1.2684, 0.8271), (1.3, 1.09, 1.0957, 1.2083, 0.5121), (1.3, 1.09, 1.0988, 1.1955, 0.4372), (1.15, 0.94, 0.9446, 1.1303, 0.8448), (1.15, 0.94, 0.9368, 1.1289, 0.8682), (1.15, 0.94, 0.9458, 1.1062, 0.7299), (1.15, 0.94, 0.9387, 1.1176, 0.8092), (1.3, 1.09, 1.0983, 1.1803, 0.3709), (1.3, 1.09, 1.0895, 1.1749, 0.3872), (1.3, 1.09, 1.0818, 1.2222, 0.6387), (1.3, 1.09, 1.1099, 1.271, 0.7286), (1.15, 0.94, 0.935, 1.0848, 0.6818), (1.15, 0.94, 0.936, 1.1397, 0.9238), (1.15, 0.94, 0.9389, 1.0985, 0.7259), (1.3, 1.09, 1.0807, 1.249, 0.7656), (1.3, 1.09, 1.091, 1.274, 0.8271), (1.3, 1.09, 1.085, 1.2547, 0.7722), (1.15, 0.94, 0.9233, 1.1424, 0.9968), (1.15, 0.94, 0.9277, 1.1274, 0.9031), (1.3, 1.09, 1.098, 1.2018, 0.4721), (1.3, 1.09, 1.0985, 1.1929, 0.4267), (1.15, 0.94, 0.9404, 1.081, 0.6395), (1.15, 0.94, 0.9321, 1.0734, 0.6392), (1.3, 1.09, 1.0845, 1.2412, 0.7127), (1.3, 1.09, 1.0808, 1.256, 0.7922), (1.05, 0.84, 0.8292, 1.0473, 0.9925), (1.3, 1.09, 1.0876, 1.2671, 0.8165), (1.3, 1.09, 1.1039, 1.2565, 0.6899), (1.15, 0.94, 0.9301, 1.0959, 0.7544), (1.15, 0.94, 0.9465, 1.0975, 0.6828), (1.3, 1.09, 1.0913, 1.1439, 0.2393), (1.3, 1.09, 1.0876, 1.1895, 0.462), (1.05, 0.84, 0.8258, 1.0391, 0.9676), (1.15, 0.94, 0.9468, 1.1358, 0.8602), (1.15, 0.94, 0.949, 1.1567, 0.9391), (1.15, 0.94, 0.942, 1.1041, 0.7349), (1.15, 0.94, 0.9389, 1.0847, 0.6634), (1.15, 0.94, 0.9384, 1.1343, 0.8859), (1.05, 0.84, 0.8394, 1.0483, 0.9474), (1.05, 0.84, 0.8463, 1.058, 0.9574), (1.3, 1.09, 1.0925, 1.1704, 0.3533), (1.15, 0.94, 0.9435, 1.1505, 0.9421), (1.15, 0.94, 0.9395, 1.1116, 0.778), (1.15, 0.94, 0.9294, 1.0356, 0.4829), (1.15, 0.94, 0.9445, 1.0845, 0.6351), (1.15, 0.94, 0.9285, 1.1197, 0.8699), (1.3, 1.09, 1.0876, 1.1593, 0.326), (1.3, 1.09, 1.09, 1.2106, 0.5468), (1.3, 1.09, 1.0882, 1.2055, 0.5339), (1.3, 1.09, 1.0887, 1.2159, 0.5748), (1.3, 1.09, 1.088, 1.1939, 0.4818), (1.3, 1.09, 1.0985, 1.1943, 0.433), (1.3, 1.09, 1.0815, 1.2027, 0.5515), (1.3, 1.09, 1.092, 1.2454, 0.6957), (1.3, 1.09, 1.0872, 1.2045, 0.5338), (1.3, 1.09, 1.0932, 1.2471, 0.696), (1.15, 0.94, 0.9584, 1.1749, 0.9853), (1.15, 0.94, 0.9435, 1.1389, 0.8834), (1.15, 0.94, 0.9521, 1.0541, 0.4644), (1.15, 0.94, 0.9341, 1.0836, 0.678), (1.15, 0.94, 0.9408, 1.1123, 0.7776), (1.05, 0.84, 0.8408, 1.0571, 0.9781), (1.05, 0.84, 0.8402, 1.0559, 0.9814), (1.15, 0.94, 0.933, 1.1335, 0.9121), (1.15, 0.94, 0.9348, 1.1324, 0.8933), (1.05, 0.84, 0.8335, 1.0472, 0.9725), (1.05, 0.84, 0.8385, 1.0483, 0.9512), (1.3, 1.09, 1.0769, 1.1817, 0.4769), (1.3, 1.09, 1.0966, 1.2045, 0.4879), (1.15, 0.94, 0.9397, 1.1194, 0.8152), (1.15, 0.94, 0.9514, 1.1618, 0.9516), (1.3, 1.09, 1.0859, 1.1186, 0.1489), (1.3, 1.09, 1.0888, 1.1484, 0.2706), (1.05, 0.84, 0.839, 1.0539, 0.9717)]; fq collisions None; errors []
- v3-C7-hhier-s030-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8561; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.32, '30Hz': 2.61}, 'b': {'1Hz': 1.9, '30Hz': 1.7}, 'up': {'1Hz': 6.38, '30Hz': 1.93}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9368, 1.1108, 0.7858), (1.15, 0.94, 0.9467, 1.1486, 0.9088), (1.3, 1.09, 1.0898, 1.2241, 0.6065), (1.15, 0.94, 0.939, 1.0572, 0.5339), (1.15, 0.94, 0.9388, 1.0848, 0.6582), (1.15, 0.94, 0.9422, 1.0973, 0.7007), (1.15, 0.94, 0.9361, 1.0883, 0.685), (1.3, 1.09, 1.0828, 1.241, 0.712), (1.15, 0.94, 0.9463, 1.1114, 0.7443), (1.3, 1.09, 1.0899, 1.2322, 0.6427), (1.3, 1.09, 1.0871, 1.2232, 0.6125), (1.3, 1.09, 1.0824, 1.2255, 0.6464), (1.05, 0.84, 0.8393, 1.0213, 0.8191), (1.05, 0.84, 0.8398, 1.0219, 0.8225), (1.15, 0.94, 0.9457, 1.0945, 0.67), (1.15, 0.94, 0.9417, 1.1112, 0.764), (1.3, 1.09, 1.0838, 1.2413, 0.7116), (1.3, 1.09, 1.0779, 1.222, 0.6485), (1.3, 1.09, 1.0786, 1.2197, 0.6351), (1.05, 0.84, 0.8365, 1.0462, 0.9453), (1.15, 0.94, 0.945, 1.1085, 0.736), (1.15, 0.94, 0.934, 1.0889, 0.6983), (1.15, 0.94, 0.9373, 1.09, 0.6894), (1.15, 0.94, 0.9397, 1.0919, 0.6852), (1.05, 0.84, 0.8371, 1.0194, 0.8209), (1.15, 0.94, 0.9411, 1.093, 0.6862), (1.15, 0.94, 0.9469, 1.1055, 0.7165), (1.15, 0.94, 0.9559, 1.1039, 0.6661), (1.3, 1.09, 1.0878, 1.2393, 0.6846), (1.3, 1.09, 1.0994, 1.2124, 0.5084), (1.3, 1.09, 1.0915, 1.2368, 0.6567), (1.15, 0.94, 0.9394, 1.095, 0.7029), (1.3, 1.09, 1.0956, 1.2294, 0.6043), (1.3, 1.09, 1.0932, 1.2324, 0.6273), (1.05, 0.84, 0.8293, 1.0115, 0.8233), (1.15, 0.94, 0.9302, 1.0855, 0.6989), (1.3, 1.09, 1.0785, 1.2343, 0.7037), (1.3, 1.09, 1.0824, 1.2475, 0.743), (1.05, 0.84, 0.8435, 1.0266, 0.8269), (1.3, 1.09, 1.1142, 1.2428, 0.581), (1.3, 1.09, 1.0818, 1.2215, 0.6295), (1.3, 1.09, 1.0882, 1.2212, 0.6008), (1.3, 1.09, 1.0878, 1.2212, 0.6004), (1.3, 1.09, 1.092, 1.2327, 0.6343), (1.15, 0.94, 0.9373, 1.0646, 0.5748), (1.15, 0.94, 0.9385, 1.0949, 0.7049), (1.05, 0.84, 0.8429, 1.0214, 0.8038), (1.15, 0.94, 0.9518, 1.1233, 0.7746), (1.05, 0.84, 0.8389, 1.0216, 0.8236), (1.3, 1.09, 1.0958, 1.2351, 0.6292), (1.3, 1.09, 1.0916, 1.2575, 0.7466), (1.15, 0.94, 0.935, 1.1161, 0.8182), (1.15, 0.94, 0.9547, 1.1272, 0.7767), (1.3, 1.09, 1.0908, 1.2317, 0.6365), (1.3, 1.09, 1.0867, 1.2308, 0.6487), (1.15, 0.94, 0.9393, 1.097, 0.712), (1.15, 0.94, 0.9308, 1.0984, 0.7543), (1.3, 1.09, 1.0933, 1.2031, 0.4958), (1.3, 1.09, 1.0866, 1.2189, 0.5965), (1.15, 0.94, 0.9422, 1.1174, 0.7912), (1.15, 0.94, 0.95, 1.1412, 0.8606), (1.15, 0.94, 0.946, 1.0952, 0.6738), (1.15, 0.94, 0.9377, 1.0867, 0.6707), (1.3, 1.09, 1.0983, 1.2441, 0.6588), (1.3, 1.09, 1.0838, 1.2325, 0.6694), (1.15, 0.94, 0.9436, 1.0934, 0.6768), (1.15, 0.94, 0.9388, 1.1057, 0.7522), (1.3, 1.09, 1.0917, 1.2285, 0.6168), (1.3, 1.09, 1.0876, 1.2332, 0.656), (1.3, 1.09, 1.0842, 1.2197, 0.612), (1.3, 1.09, 1.097, 1.2309, 0.6031), (1.3, 1.09, 1.0877, 1.2225, 0.6071), (1.15, 0.94, 0.9486, 1.1069, 0.7154), (1.15, 0.94, 0.9396, 1.0961, 0.7044), (1.05, 0.84, 0.8366, 1.0337, 0.8886)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r1-eth1': {'bg_packets': 69, 'in_pinned_class': 0, 'flows': []}, 'r1-eth2': {'bg_packets': 4749217, 'in_pinned_class': 3613, 'flows': ['10.101.0.1:5208', '10.101.0.1:5223', '10.101.0.1:5249']}, 'r2-eth2': {'bg_packets': 2557940, 'in_pinned_class': 3607, 'flows': ['10.101.0.2:5204', '10.101.0.2:5230', '10.101.0.2:5240', '10.101.0.2:5261', '10.101.0.2:5267']}, 'r2-eth4': {'bg_packets': 2496478, 'in_pinned_class': 2567, 'flows': ['10.101.0.3:5233', '10.101.0.3:5246']}}; errors []
- v3-C7-hhier-s030-fq_codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8532; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.01, '30Hz': 1.17}, 'b': {'1Hz': 0.86, '30Hz': 3.85}, 'up': {'1Hz': 2.07, '30Hz': 3.55}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9383, 1.1275, 0.8509), (1.3, 1.09, 1.0855, 1.2223, 0.6151), (1.3, 1.09, 1.0957, 1.2644, 0.7636), (1.3, 1.09, 1.0988, 1.2384, 0.6279), (1.15, 0.94, 0.9446, 1.0923, 0.6686), (1.15, 0.94, 0.9369, 1.0877, 0.6781), (1.15, 0.94, 0.9458, 1.0954, 0.6771), (1.15, 0.94, 0.9387, 1.0997, 0.7242), (1.3, 1.09, 1.0983, 1.2322, 0.6023), (1.3, 1.09, 1.0895, 1.2336, 0.6499), (1.3, 1.09, 1.0818, 1.2272, 0.6581), (1.3, 1.09, 1.1099, 1.2667, 0.7052), (1.15, 0.94, 0.935, 1.08, 0.6563), (1.15, 0.94, 0.936, 1.102, 0.7488), (1.15, 0.94, 0.9389, 1.1053, 0.7528), (1.3, 1.09, 1.0807, 1.2289, 0.671), (1.3, 1.09, 1.091, 1.2384, 0.6626), (1.3, 1.09, 1.085, 1.2374, 0.6898), (1.15, 0.94, 0.9234, 1.0868, 0.7397), (1.15, 0.94, 0.9277, 1.0908, 0.7333), (1.3, 1.09, 1.098, 1.2412, 0.6479), (1.3, 1.09, 1.0985, 1.2331, 0.6048), (1.15, 0.94, 0.9404, 1.0943, 0.6964), (1.15, 0.94, 0.9321, 1.0842, 0.6838), (1.3, 1.09, 1.0845, 1.2393, 0.7007), (1.3, 1.09, 1.0808, 1.2302, 0.6717), (1.05, 0.84, 0.8292, 1.0175, 0.8524), (1.3, 1.09, 1.0876, 1.245, 0.7122), (1.3, 1.09, 1.1039, 1.2478, 0.6468), (1.15, 0.94, 0.9301, 1.0916, 0.7309), (1.15, 0.94, 0.9465, 1.1093, 0.7318), (1.3, 1.09, 1.0913, 1.22, 0.5824), (1.3, 1.09, 1.0876, 1.2328, 0.6547), (1.05, 0.84, 0.8258, 1.0151, 0.8538), (1.15, 0.94, 0.9468, 1.1107, 0.7419), (1.15, 0.94, 0.949, 1.1136, 0.7398), (1.15, 0.94, 0.9419, 1.1033, 0.7276), (1.15, 0.94, 0.9389, 1.0958, 0.71), (1.15, 0.94, 0.9384, 1.0944, 0.7013), (1.05, 0.84, 0.8394, 1.0214, 0.8208), (1.05, 0.84, 0.8463, 1.0355, 0.8509), (1.3, 1.09, 1.0925, 1.2318, 0.6282), (1.15, 0.94, 0.9435, 1.0919, 0.6716), (1.15, 0.94, 0.9395, 1.0896, 0.675), (1.15, 0.94, 0.9294, 1.0743, 0.6555), (1.15, 0.94, 0.9445, 1.0951, 0.679), (1.15, 0.94, 0.9285, 1.0845, 0.7061), (1.3, 1.09, 1.0876, 1.2221, 0.6088), (1.3, 1.09, 1.09, 1.2208, 0.5896), (1.3, 1.09, 1.0882, 1.2215, 0.6031), (1.3, 1.09, 1.0887, 1.2353, 0.659), (1.3, 1.09, 1.088, 1.2242, 0.6163), (1.3, 1.09, 1.0985, 1.234, 0.6095), (1.3, 1.09, 1.0815, 1.2216, 0.6344), (1.3, 1.09, 1.092, 1.2419, 0.676), (1.3, 1.09, 1.0872, 1.2247, 0.6226), (1.3, 1.09, 1.0932, 1.2275, 0.604), (1.15, 0.94, 0.9584, 1.1251, 0.7545), (1.15, 0.94, 0.9435, 1.099, 0.6992), (1.15, 0.94, 0.9521, 1.0996, 0.6677), (1.15, 0.94, 0.9341, 1.0955, 0.7276), (1.15, 0.94, 0.9408, 1.1002, 0.7185), (1.05, 0.84, 0.8408, 1.0232, 0.82), (1.05, 0.84, 0.8402, 1.0313, 0.8649), (1.15, 0.94, 0.933, 1.1074, 0.7893), (1.15, 0.94, 0.9348, 1.0877, 0.6875), (1.05, 0.84, 0.8335, 1.0196, 0.8421), (1.05, 0.84, 0.8385, 1.0182, 0.8103), (1.3, 1.09, 1.0769, 1.2176, 0.6365), (1.3, 1.09, 1.0966, 1.2437, 0.6612), (1.15, 0.94, 0.9396, 1.0987, 0.7171), (1.15, 0.94, 0.9514, 1.1134, 0.7285), (1.3, 1.09, 1.0859, 1.2194, 0.6042), (1.3, 1.09, 1.0888, 1.2292, 0.6335), (1.05, 0.84, 0.839, 1.0297, 0.8575)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r1-eth1': {'bg_packets': 65, 'in_pinned_class': 0, 'flows': []}, 'r1-eth2': {'bg_packets': 4627270, 'in_pinned_class': 2538, 'flows': ['10.101.0.1:5243', '10.101.0.1:5252']}, 'r2-eth2': {'bg_packets': 2493270, 'in_pinned_class': 927, 'flows': ['10.101.0.2:5222', '10.101.0.2:5261']}, 'r2-eth4': {'bg_packets': 2434971, 'in_pinned_class': 1922, 'flows': ['10.101.0.3:5205', '10.101.0.3:5220', '10.101.0.3:5239']}}; errors []
- v3-C7-hhier-s030-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8958; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.32, '30Hz': 2.63}, 'b': {'1Hz': 1.89, '30Hz': 1.7}, 'up': {'1Hz': 6.4, '30Hz': 1.97}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9368, 1.1385, 0.9166), (1.15, 0.94, 0.9467, 1.1766, 1.0408), (1.3, 1.09, 1.0898, 1.298, 0.9467), (1.15, 0.94, 0.939, 1.0441, 0.4776), (1.15, 0.94, 0.9388, 1.0978, 0.7215), (1.15, 0.94, 0.9422, 1.138, 0.8901), (1.15, 0.94, 0.9361, 1.1398, 0.922), (1.3, 1.09, 1.0829, 1.2439, 0.7285), (1.15, 0.94, 0.9463, 1.1176, 0.7773), (1.3, 1.09, 1.0899, 1.2571, 0.7603), (1.3, 1.09, 1.0871, 1.2413, 0.6978), (1.3, 1.09, 1.0824, 1.2479, 0.7522), (1.05, 0.84, 0.8393, 1.0794, 1.0866), (1.05, 0.84, 0.8398, 1.0786, 1.0854), (1.15, 0.94, 0.9457, 1.1271, 0.8215), (1.15, 0.94, 0.9417, 1.1245, 0.8292), (1.3, 1.09, 1.0838, 1.2802, 0.893), (1.3, 1.09, 1.0779, 1.2114, 0.6042), (1.3, 1.09, 1.0786, 1.2535, 0.7919), (1.05, 0.84, 0.8365, 1.0783, 1.0967), (1.15, 0.94, 0.945, 1.1674, 1.0066), (1.15, 0.94, 0.934, 1.1456, 0.96), (1.15, 0.94, 0.9373, 1.2312, 1.3361), (1.15, 0.94, 0.9397, 1.1447, 0.9279), (1.05, 0.84, 0.8371, 1.0699, 1.0541), (1.15, 0.94, 0.9411, 1.2072, 1.2101), (1.15, 0.94, 0.9469, 1.1904, 1.1071), (1.15, 0.94, 0.9559, 1.2342, 1.2596), (1.3, 1.09, 1.0878, 1.1955, 0.4896), (1.3, 1.09, 1.0994, 1.2361, 0.6187), (1.3, 1.09, 1.0915, 1.3234, 1.0544), (1.15, 0.94, 0.9394, 1.1625, 1.0145), (1.3, 1.09, 1.0956, 1.128, 0.1475), (1.3, 1.09, 1.0932, 1.1652, 0.3262), (1.05, 0.84, 0.8293, 1.0628, 1.0616), (1.15, 0.94, 0.9302, 1.1288, 0.8989), (1.3, 1.09, 1.0785, 1.249, 0.7753), (1.3, 1.09, 1.0824, 1.2243, 0.6421), (1.05, 0.84, 0.8435, 1.0702, 1.0306), (1.3, 1.09, 1.1142, 1.1679, 0.2443), (1.3, 1.09, 1.0818, 1.1693, 0.3965), (1.3, 1.09, 1.0882, 1.2573, 0.7689), (1.3, 1.09, 1.0878, 1.2527, 0.7463), (1.3, 1.09, 1.092, 1.1955, 0.4694), (1.15, 0.94, 0.9373, 1.0644, 0.5777), (1.15, 0.94, 0.9385, 1.1185, 0.8164), (1.05, 0.84, 0.8429, 1.0684, 1.0208), (1.15, 0.94, 0.9518, 1.1511, 0.9061), (1.05, 0.84, 0.8389, 1.0505, 0.96), (1.3, 1.09, 1.0958, 1.2661, 0.7742), (1.3, 1.09, 1.0916, 1.2283, 0.6187), (1.15, 0.94, 0.935, 1.1134, 0.8114), (1.15, 0.94, 0.9547, 1.175, 0.9974), (1.3, 1.09, 1.0908, 1.197, 0.4827), (1.3, 1.09, 1.0867, 1.2518, 0.7474), (1.15, 0.94, 0.9394, 1.1612, 1.0087), (1.15, 0.94, 0.9308, 1.1323, 0.9119), (1.3, 1.09, 1.0933, 1.137, 0.1988), (1.3, 1.09, 1.0866, 1.1817, 0.4313), (1.15, 0.94, 0.9422, 1.16, 0.99), (1.15, 0.94, 0.95, 1.1626, 0.9625), (1.15, 0.94, 0.946, 1.1609, 0.9769), (1.15, 0.94, 0.9377, 1.1415, 0.9222), (1.3, 1.09, 1.0983, 1.2488, 0.6841), (1.3, 1.09, 1.0838, 1.2565, 0.7817), (1.15, 0.94, 0.9436, 1.0508, 0.4871), (1.15, 0.94, 0.9388, 1.0954, 0.7101), (1.3, 1.09, 1.0917, 1.1836, 0.4168), (1.3, 1.09, 1.0876, 1.2541, 0.755), (1.3, 1.09, 1.0842, 1.2441, 0.7267), (1.3, 1.09, 1.097, 1.2489, 0.6879), (1.3, 1.09, 1.0877, 1.2723, 0.8355), (1.15, 0.94, 0.9486, 1.1731, 1.021), (1.15, 0.94, 0.9396, 1.1727, 1.0552), (1.05, 0.84, 0.8366, 1.1019, 1.2033)]; fq collisions None; errors []
- v3-C7-hhier-s030-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8809; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.01, '30Hz': 1.19}, 'b': {'1Hz': 0.86, '30Hz': 3.94}, 'up': {'1Hz': 2.07, '30Hz': 3.68}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9383, 1.2468, 1.4072), (1.3, 1.09, 1.0855, 1.239, 0.7002), (1.3, 1.09, 1.0957, 1.228, 0.6043), (1.3, 1.09, 1.0988, 1.2177, 0.5427), (1.15, 0.94, 0.9446, 1.1335, 0.8628), (1.15, 0.94, 0.9369, 1.1463, 0.9555), (1.15, 0.94, 0.9458, 1.1063, 0.7332), (1.15, 0.94, 0.9387, 1.1307, 0.876), (1.3, 1.09, 1.0983, 1.2624, 0.7485), (1.3, 1.09, 1.0895, 1.1788, 0.4078), (1.3, 1.09, 1.0818, 1.2468, 0.754), (1.3, 1.09, 1.1099, 1.3478, 1.0851), (1.15, 0.94, 0.935, 1.0801, 0.6629), (1.15, 0.94, 0.936, 1.1538, 0.9942), (1.15, 0.94, 0.9389, 1.1769, 1.0875), (1.3, 1.09, 1.0807, 1.3939, 1.431), (1.3, 1.09, 1.091, 1.2578, 0.7607), (1.3, 1.09, 1.085, 1.2579, 0.7902), (1.15, 0.94, 0.9233, 1.1148, 0.8748), (1.15, 0.94, 0.9277, 1.119, 0.8726), (1.3, 1.09, 1.098, 1.2237, 0.5743), (1.3, 1.09, 1.0985, 1.2858, 0.8542), (1.15, 0.94, 0.9404, 1.1413, 0.9177), (1.15, 0.94, 0.9321, 1.1349, 0.9251), (1.3, 1.09, 1.0845, 1.2349, 0.6869), (1.3, 1.09, 1.0808, 1.2335, 0.6964), (1.05, 0.84, 0.8292, 1.0579, 1.0448), (1.3, 1.09, 1.0876, 1.3376, 1.1419), (1.3, 1.09, 1.1039, 1.2491, 0.6622), (1.15, 0.94, 0.9301, 1.1689, 1.0911), (1.15, 0.94, 0.9465, 1.1767, 1.0499), (1.3, 1.09, 1.0913, 1.1383, 0.2145), (1.3, 1.09, 1.0876, 1.1857, 0.4479), (1.05, 0.84, 0.8258, 1.0407, 0.9811), (1.15, 0.94, 0.9468, 1.1532, 0.9428), (1.15, 0.94, 0.949, 1.1751, 1.031), (1.15, 0.94, 0.9419, 1.1189, 0.8081), (1.15, 0.94, 0.9389, 1.1592, 1.0063), (1.15, 0.94, 0.9384, 1.1401, 0.92), (1.05, 0.84, 0.8394, 1.084, 1.1164), (1.05, 0.84, 0.8463, 1.0816, 1.0736), (1.3, 1.09, 1.0925, 1.1927, 0.4576), (1.15, 0.94, 0.9435, 1.1533, 0.9585), (1.15, 0.94, 0.9395, 1.1354, 0.8935), (1.15, 0.94, 0.9294, 1.0261, 0.4417), (1.15, 0.94, 0.9445, 1.0931, 0.6783), (1.15, 0.94, 0.9285, 1.1523, 1.0227), (1.3, 1.09, 1.0876, 1.1387, 0.2332), (1.3, 1.09, 1.09, 1.1921, 0.4662), (1.3, 1.09, 1.0882, 1.2544, 0.7591), (1.3, 1.09, 1.0887, 1.258, 0.7719), (1.3, 1.09, 1.088, 1.2046, 0.5326), (1.3, 1.09, 1.0985, 1.2422, 0.6555), (1.3, 1.09, 1.0815, 1.2249, 0.6551), (1.3, 1.09, 1.092, 1.2177, 0.5737), (1.3, 1.09, 1.0872, 1.2224, 0.6175), (1.3, 1.09, 1.0932, 1.2063, 0.516), (1.15, 0.94, 0.9584, 1.1868, 1.0436), (1.15, 0.94, 0.9435, 1.1827, 1.0911), (1.15, 0.94, 0.9521, 1.056, 0.475), (1.15, 0.94, 0.9341, 1.1001, 0.7575), (1.15, 0.94, 0.9409, 1.1304, 0.865), (1.05, 0.84, 0.8408, 1.0791, 1.0869), (1.05, 0.84, 0.8402, 1.0864, 1.1247), (1.15, 0.94, 0.933, 1.1842, 1.1475), (1.15, 0.94, 0.9348, 1.1474, 0.9698), (1.05, 0.84, 0.8335, 1.0725, 1.092), (1.05, 0.84, 0.8385, 1.0923, 1.1584), (1.3, 1.09, 1.0769, 1.2453, 0.7691), (1.3, 1.09, 1.0966, 1.2592, 0.7416), (1.15, 0.94, 0.9396, 1.1518, 0.9685), (1.15, 0.94, 0.9514, 1.2182, 1.2172), (1.3, 1.09, 1.0859, 1.1268, 0.1869), (1.3, 1.09, 1.0888, 1.1643, 0.345), (1.05, 0.84, 0.839, 1.067, 1.0402)]; fq collisions None; errors []
- v3-C7-hhier-s030-pie-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8969; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.32, '30Hz': 2.76}, 'b': {'1Hz': 1.89, '30Hz': 1.7}, 'up': {'1Hz': 6.4, '30Hz': 1.88}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9368, 1.2126, 1.2619), (1.15, 0.94, 0.9467, 1.2257, 1.2702), (1.3, 1.09, 1.0898, 1.3969, 1.4053), (1.15, 0.94, 0.939, 1.1551, 0.9889), (1.15, 0.94, 0.9388, 1.2045, 1.2126), (1.15, 0.94, 0.9422, 1.2123, 1.2362), (1.15, 0.94, 0.9361, 1.2026, 1.2134), (1.3, 1.09, 1.0828, 1.309, 1.0294), (1.15, 0.94, 0.9463, 1.2096, 1.2015), (1.3, 1.09, 1.0899, 1.3665, 1.266), (1.3, 1.09, 1.0871, 1.3301, 1.106), (1.3, 1.09, 1.0824, 1.385, 1.3848), (1.05, 0.84, 0.8393, 1.0698, 1.0493), (1.05, 0.84, 0.8398, 1.0775, 1.0878), (1.15, 0.94, 0.9457, 1.2096, 1.2014), (1.15, 0.94, 0.9417, 1.189, 1.1286), (1.3, 1.09, 1.0838, 1.3596, 1.2623), (1.3, 1.09, 1.0779, 1.3059, 1.038), (1.3, 1.09, 1.0785, 1.2938, 0.98), (1.05, 0.84, 0.8365, 1.0679, 1.056), (1.15, 0.94, 0.945, 1.2028, 1.1735), (1.15, 0.94, 0.934, 1.1916, 1.1755), (1.15, 0.94, 0.9373, 1.2038, 1.2192), (1.15, 0.94, 0.9397, 1.2056, 1.2104), (1.05, 0.84, 0.8371, 1.067, 1.0468), (1.15, 0.94, 0.9411, 1.1744, 1.0678), (1.15, 0.94, 0.9469, 1.2188, 1.2442), (1.15, 0.94, 0.9559, 1.2355, 1.273), (1.3, 1.09, 1.0878, 1.3252, 1.0867), (1.3, 1.09, 1.0994, 1.2579, 0.7213), (1.3, 1.09, 1.0915, 1.3245, 1.0664), (1.15, 0.94, 0.9394, 1.2008, 1.1965), (1.3, 1.09, 1.0956, 1.1899, 0.4319), (1.3, 1.09, 1.0932, 1.2529, 0.7283), (1.05, 0.84, 0.8293, 1.0623, 1.0662), (1.15, 0.94, 0.9302, 1.1881, 1.1738), (1.3, 1.09, 1.0785, 1.3122, 1.0697), (1.3, 1.09, 1.0826, 1.3636, 1.279), (1.05, 0.84, 0.8435, 1.07, 1.0366), (1.3, 1.09, 1.1142, 1.1985, 0.3859), (1.3, 1.09, 1.0818, 1.2231, 0.6445), (1.3, 1.09, 1.0882, 1.3389, 1.1475), (1.3, 1.09, 1.0878, 1.3178, 1.0468), (1.3, 1.09, 1.092, 1.3, 0.9491), (1.15, 0.94, 0.9373, 1.1292, 0.8779), (1.15, 0.94, 0.9385, 1.1813, 1.1078), (1.05, 0.84, 0.8429, 1.0682, 1.026), (1.15, 0.94, 0.9518, 1.2226, 1.2394), (1.05, 0.84, 0.8389, 1.0586, 1.0023), (1.3, 1.09, 1.0958, 1.356, 1.1905), (1.3, 1.09, 1.0916, 1.3418, 1.1387), (1.15, 0.94, 0.935, 1.1957, 1.1933), (1.15, 0.94, 0.9547, 1.1938, 1.0883), (1.3, 1.09, 1.0908, 1.3027, 0.9697), (1.3, 1.09, 1.0867, 1.3109, 1.0207), (1.15, 0.94, 0.9393, 1.1777, 1.0906), (1.15, 0.94, 0.9308, 1.1463, 0.9812), (1.3, 1.09, 1.0933, 1.1976, 0.4774), (1.3, 1.09, 1.0866, 1.2376, 0.689), (1.15, 0.94, 0.9422, 1.2021, 1.1892), (1.15, 0.94, 0.95, 1.2253, 1.2531), (1.15, 0.94, 0.946, 1.2155, 1.2332), (1.15, 0.94, 0.9377, 1.1932, 1.1631), (1.3, 1.09, 1.0983, 1.3024, 0.934), (1.3, 1.09, 1.0838, 1.3183, 1.0674), (1.15, 0.94, 0.9436, 1.1356, 0.8785), (1.15, 0.94, 0.9388, 1.1714, 1.0614), (1.3, 1.09, 1.0917, 1.2738, 0.8309), (1.3, 1.09, 1.0876, 1.239, 0.6907), (1.3, 1.09, 1.0842, 1.3048, 1.0095), (1.3, 1.09, 1.097, 1.2844, 0.8531), (1.3, 1.09, 1.0877, 1.3393, 1.1454), (1.15, 0.94, 0.9486, 1.2122, 1.2065), (1.15, 0.94, 0.9396, 1.1973, 1.1732), (1.05, 0.84, 0.8366, 1.0735, 1.081)]; fq collisions None; errors []
- v3-C7-hhier-s030-pie-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8834; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.01, '30Hz': 1.12}, 'b': {'1Hz': 0.86, '30Hz': 3.78}, 'up': {'1Hz': 2.07, '30Hz': 3.65}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9383, 1.2032, 1.2118), (1.3, 1.09, 1.0855, 1.411, 1.4889), (1.3, 1.09, 1.0957, 1.403, 1.4062), (1.3, 1.09, 1.0988, 1.4151, 1.4469), (1.15, 0.94, 0.9446, 1.2114, 1.221), (1.15, 0.94, 0.9368, 1.2087, 1.2435), (1.15, 0.94, 0.9458, 1.2159, 1.2363), (1.15, 0.94, 0.9387, 1.2117, 1.2488), (1.3, 1.09, 1.0983, 1.3788, 1.2833), (1.3, 1.09, 1.0895, 1.2824, 0.8827), (1.3, 1.09, 1.0818, 1.3299, 1.1353), (1.3, 1.09, 1.1099, 1.3855, 1.2609), (1.15, 0.94, 0.935, 1.1381, 0.9297), (1.15, 0.94, 0.936, 1.1888, 1.1567), (1.15, 0.94, 0.9389, 1.1959, 1.1761), (1.3, 1.09, 1.0807, 1.3296, 1.1389), (1.3, 1.09, 1.091, 1.3843, 1.3417), (1.3, 1.09, 1.085, 1.3531, 1.2272), (1.15, 0.94, 0.9233, 1.1826, 1.1867), (1.15, 0.94, 0.9277, 1.1609, 1.0666), (1.3, 1.09, 1.098, 1.3056, 0.9499), (1.3, 1.09, 1.0985, 1.3223, 1.0235), (1.15, 0.94, 0.9404, 1.2041, 1.2067), (1.15, 0.94, 0.9321, 1.1887, 1.1739), (1.3, 1.09, 1.0845, 1.3297, 1.1223), (1.3, 1.09, 1.0808, 1.2794, 0.9085), (1.05, 0.84, 0.8292, 1.0549, 1.0331), (1.3, 1.09, 1.0876, 1.3133, 1.0329), (1.3, 1.09, 1.104, 1.3739, 1.2349), (1.15, 0.94, 0.9301, 1.2027, 1.2475), (1.15, 0.94, 0.9465, 1.216, 1.2326), (1.3, 1.09, 1.0913, 1.213, 0.5569), (1.3, 1.09, 1.0876, 1.245, 0.7204), (1.05, 0.84, 0.8258, 1.0505, 1.0281), (1.15, 0.94, 0.9468, 1.2135, 1.2205), (1.15, 0.94, 0.949, 1.2134, 1.2095), (1.15, 0.94, 0.9419, 1.1824, 1.1002), (1.15, 0.94, 0.9389, 1.2064, 1.2241), (1.15, 0.94, 0.9384, 1.2018, 1.2049), (1.05, 0.84, 0.8394, 1.0719, 1.064), (1.05, 0.84, 0.8463, 1.0746, 1.0445), (1.3, 1.09, 1.0925, 1.2511, 0.7258), (1.15, 0.94, 0.9435, 1.1942, 1.1473), (1.15, 0.94, 0.9395, 1.1873, 1.1338), (1.15, 0.94, 0.9294, 1.1383, 0.9558), (1.15, 0.94, 0.9445, 1.1994, 1.1663), (1.15, 0.94, 0.9285, 1.1886, 1.1905), (1.3, 1.09, 1.0876, 1.1879, 0.4589), (1.3, 1.09, 1.09, 1.251, 0.7364), (1.3, 1.09, 1.0882, 1.2968, 0.9547), (1.3, 1.09, 1.0887, 1.3261, 1.0859), (1.3, 1.09, 1.088, 1.3024, 0.9811), (1.3, 1.09, 1.0985, 1.3138, 0.985), (1.3, 1.09, 1.0815, 1.3418, 1.1915), (1.3, 1.09, 1.092, 1.2815, 0.8669), (1.3, 1.09, 1.0872, 1.2925, 0.9398), (1.3, 1.09, 1.0932, 1.3806, 1.3146), (1.15, 0.94, 0.9584, 1.1904, 1.0618), (1.15, 0.94, 0.9435, 1.1984, 1.166), (1.15, 0.94, 0.9521, 1.1607, 0.955), (1.15, 0.94, 0.9341, 1.1914, 1.177), (1.15, 0.94, 0.9408, 1.2002, 1.1865), (1.05, 0.84, 0.8408, 1.0709, 1.0526), (1.05, 0.84, 0.8402, 1.0773, 1.0848), (1.15, 0.94, 0.933, 1.2092, 1.264), (1.15, 0.94, 0.9348, 1.1869, 1.1531), (1.05, 0.84, 0.8335, 1.0629, 1.0497), (1.05, 0.84, 0.8385, 1.0753, 1.0832), (1.3, 1.09, 1.0769, 1.2991, 1.017), (1.3, 1.09, 1.0966, 1.3026, 0.9423), (1.15, 0.94, 0.9396, 1.1981, 1.1822), (1.15, 0.94, 0.9514, 1.2173, 1.2166), (1.3, 1.09, 1.0859, 1.1785, 0.424), (1.3, 1.09, 1.0888, 1.2487, 0.7317), (1.05, 0.84, 0.839, 1.0597, 1.0095)]; fq collisions None; errors []
- v3-C8-hhier-s065-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8719; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 1.9, '30Hz': 2.2}, 'b': {'1Hz': 3.23, '30Hz': 0.67}, 'up': {'1Hz': 2.22, '30Hz': 0.31}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.695, 0.6851, 1.3117, 1.3168), (1.15, 0.695, 0.706, 1.3517, 1.3577), (1.3, 0.845, 0.8542, 1.537, 1.435), (1.15, 0.695, 0.6928, 1.0045, 0.655), (1.15, 0.695, 0.693, 1.1631, 0.988), (1.15, 0.695, 0.6956, 1.2128, 1.0869), (1.15, 0.695, 0.6967, 1.1697, 0.9946), (1.3, 0.845, 0.8409, 1.4235, 1.2249), (1.15, 0.695, 0.6999, 1.1371, 0.9187), (1.3, 0.845, 0.8488, 1.2786, 0.9032), (1.3, 0.845, 0.8431, 1.2012, 0.753), (1.3, 0.845, 0.8296, 1.2738, 0.9336), (1.05, 0.595, 0.5896, 1.1047, 1.0832), (1.05, 0.595, 0.603, 1.1482, 1.1457), (1.15, 0.695, 0.6929, 1.2045, 1.0757), (1.15, 0.695, 0.6973, 1.2082, 1.0738), (1.3, 0.845, 0.8479, 1.2898, 0.9287), (1.3, 0.845, 0.8426, 1.2846, 0.9295), (1.3, 0.845, 0.8382, 1.3047, 0.9809), (1.05, 0.595, 0.595, 1.0919, 1.0446), (1.15, 0.695, 0.692, 1.1494, 0.9618), (1.15, 0.695, 0.6915, 1.1473, 0.9579), (1.15, 0.695, 0.6991, 1.2605, 1.1797), (1.15, 0.695, 0.694, 1.1927, 1.0485), (1.05, 0.595, 0.5842, 1.096, 1.076), (1.15, 0.695, 0.6886, 1.1965, 1.0674), (1.15, 0.695, 0.696, 1.2544, 1.1735), (1.15, 0.695, 0.6893, 1.2113, 1.0976), (1.3, 0.845, 0.8419, 1.2007, 0.754), (1.3, 0.845, 0.8641, 1.2597, 0.8317), (1.3, 0.845, 0.8426, 1.2428, 0.8411), (1.15, 0.695, 0.6967, 1.1626, 0.979), (1.3, 0.845, 0.8402, 1.0289, 0.3966), (1.3, 0.845, 0.8495, 1.2075, 0.7526), (1.05, 0.595, 0.5963, 1.0837, 1.0245), (1.15, 0.695, 0.6814, 1.2395, 1.1734), (1.3, 0.845, 0.8389, 1.3727, 1.1218), (1.3, 0.845, 0.8585, 1.3963, 1.1308), (1.05, 0.595, 0.6023, 1.0787, 1.001), (1.3, 0.845, 0.8756, 1.0648, 0.3977), (1.3, 0.845, 0.8467, 1.1498, 0.6372), (1.3, 0.845, 0.8308, 1.2753, 0.9341), (1.3, 0.845, 0.8559, 1.2257, 0.7774), (1.3, 0.845, 0.8561, 1.1662, 0.6516), (1.15, 0.695, 0.6937, 1.0123, 0.6696), (1.15, 0.695, 0.6936, 1.1955, 1.0548), (1.05, 0.595, 0.5989, 1.0738, 0.9986), (1.15, 0.695, 0.7236, 1.2001, 1.0013), (1.05, 0.595, 0.5965, 1.0641, 0.9828), (1.3, 0.845, 0.8613, 1.227, 0.7686), (1.3, 0.845, 0.8475, 1.2602, 0.8679), (1.15, 0.695, 0.6816, 1.1721, 1.0309), (1.15, 0.695, 0.7037, 1.1989, 1.0412), (1.3, 0.845, 0.8511, 1.2278, 0.7917), (1.3, 0.845, 0.8427, 1.3066, 0.9754), (1.15, 0.695, 0.6945, 1.2783, 1.2269), (1.15, 0.695, 0.7201, 1.1872, 0.982), (1.3, 0.845, 0.8557, 1.0611, 0.4317), (1.3, 0.845, 0.837, 1.1691, 0.698), (1.15, 0.695, 0.676, 1.1741, 1.0468), (1.15, 0.695, 0.7012, 1.1592, 0.9631), (1.15, 0.695, 0.7041, 1.1668, 0.9723), (1.15, 0.695, 0.6966, 1.2358, 1.1337), (1.3, 0.845, 0.8365, 1.2711, 0.9133), (1.3, 0.845, 0.8587, 1.328, 0.9868), (1.15, 0.695, 0.6908, 1.0376, 0.7288), (1.15, 0.695, 0.6976, 1.0904, 0.8258), (1.3, 0.845, 0.8483, 1.1877, 0.7132), (1.3, 0.845, 0.8475, 1.2344, 0.8133), (1.3, 0.845, 0.8449, 1.2889, 0.9331), (1.3, 0.845, 0.8578, 1.3265, 0.9855), (1.3, 0.845, 0.8444, 1.2739, 0.9032), (1.15, 0.695, 0.7034, 1.1968, 1.0368), (1.15, 0.695, 0.6966, 1.2491, 1.1618), (1.05, 0.595, 0.5937, 1.117, 1.0999)]; fq collisions None; errors []
- v3-C8-hhier-s065-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8645; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 3.32, '30Hz': 5.73}, 'b': {'1Hz': 1.89, '30Hz': 1.6}, 'up': {'1Hz': 0.57, '30Hz': 1.18}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.695, 0.6681, 1.2967, 1.321), (1.3, 0.845, 0.856, 1.3201, 0.9752), (1.3, 0.845, 0.8432, 1.2644, 0.8874), (1.3, 0.845, 0.8544, 1.2426, 0.8159), (1.15, 0.695, 0.6907, 1.1614, 0.9916), (1.15, 0.695, 0.7007, 1.19, 1.0283), (1.15, 0.695, 0.7083, 1.204, 1.0445), (1.15, 0.695, 0.7005, 1.1678, 0.982), (1.3, 0.845, 0.8476, 1.2237, 0.7904), (1.3, 0.845, 0.8433, 1.2082, 0.7675), (1.3, 0.845, 0.8401, 1.2722, 0.9105), (1.3, 0.845, 0.859, 1.3116, 0.9512), (1.15, 0.695, 0.6788, 1.0384, 0.7576), (1.15, 0.695, 0.6792, 1.1774, 1.048), (1.15, 0.695, 0.6882, 1.1994, 1.077), (1.3, 0.845, 0.852, 1.3955, 1.1451), (1.3, 0.845, 0.8467, 1.3627, 1.0844), (1.3, 0.845, 0.8423, 1.303, 0.9707), (1.15, 0.695, 0.6864, 1.2442, 1.1753), (1.15, 0.695, 0.6779, 1.1567, 1.0062), (1.3, 0.845, 0.8401, 1.2504, 0.8646), (1.3, 0.845, 0.8519, 1.2568, 0.8508), (1.15, 0.695, 0.6882, 1.1959, 1.0696), (1.15, 0.695, 0.6897, 1.1856, 1.0422), (1.3, 0.845, 0.8296, 1.3006, 0.9923), (1.3, 0.845, 0.8527, 1.34, 1.0239), (1.05, 0.595, 0.5772, 1.0805, 1.0606), (1.3, 0.845, 0.8624, 1.3309, 0.9871), (1.3, 0.845, 0.8391, 1.2224, 0.8055), (1.15, 0.695, 0.6856, 1.1658, 1.0117), (1.15, 0.695, 0.69, 1.2479, 1.1723), (1.3, 0.845, 0.8611, 1.0411, 0.3791), (1.3, 0.845, 0.8425, 1.186, 0.7225), (1.05, 0.595, 0.5842, 1.0511, 0.9821), (1.15, 0.695, 0.6998, 1.2815, 1.2256), (1.15, 0.695, 0.6968, 1.1879, 1.0319), (1.15, 0.695, 0.6816, 1.1808, 1.05), (1.15, 0.695, 0.6992, 1.1589, 0.9685), (1.15, 0.695, 0.6897, 1.1777, 1.0254), (1.05, 0.595, 0.6001, 1.1342, 1.1236), (1.05, 0.595, 0.6033, 1.1216, 1.0892), (1.3, 0.845, 0.8556, 1.1628, 0.6461), (1.15, 0.695, 0.7009, 1.1709, 0.9901), (1.15, 0.695, 0.6915, 1.1983, 1.0649), (1.15, 0.695, 0.6942, 0.9792, 0.6004), (1.15, 0.695, 0.6952, 1.1451, 0.9462), (1.15, 0.695, 0.6799, 1.18, 1.0538), (1.3, 0.845, 0.8548, 1.1255, 0.5704), (1.3, 0.845, 0.85, 1.2062, 0.7492), (1.3, 0.845, 0.8497, 1.2537, 0.8514), (1.3, 0.845, 0.8421, 1.2687, 0.8966), (1.3, 0.845, 0.8467, 1.2555, 0.8614), (1.3, 0.845, 0.8473, 1.2359, 0.8166), (1.3, 0.845, 0.8415, 1.1469, 0.6434), (1.3, 0.845, 0.8477, 1.1252, 0.5837), (1.3, 0.845, 0.8414, 1.2845, 0.9336), (1.3, 0.845, 0.8451, 1.3226, 1.0034), (1.15, 0.695, 0.6998, 1.2236, 1.1035), (1.15, 0.695, 0.6816, 1.1867, 1.0614), (1.15, 0.695, 0.7036, 1.0373, 0.7032), (1.15, 0.695, 0.6941, 1.1524, 0.964), (1.15, 0.695, 0.692, 1.2129, 1.0957), (1.05, 0.595, 0.5815, 1.0934, 1.0759), (1.05, 0.595, 0.5959, 1.135, 1.1357), (1.15, 0.695, 0.6941, 1.1977, 1.0612), (1.15, 0.695, 0.6849, 1.2034, 1.0896), (1.05, 0.595, 0.5863, 1.1044, 1.0916), (1.05, 0.595, 0.5895, 1.1351, 1.1476), (1.3, 0.845, 0.8318, 1.314, 1.0159), (1.3, 0.845, 0.8531, 1.2817, 0.9008), (1.15, 0.695, 0.6889, 1.1777, 1.0281), (1.15, 0.695, 0.71, 1.169, 0.9645), (1.3, 0.845, 0.8421, 1.0358, 0.4081), (1.3, 0.845, 0.8433, 1.1146, 0.5707), (1.05, 0.595, 0.597, 1.0814, 1.0178)]; fq collisions None; errors []
- v3-C9-hdepth-tree16-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.7533; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.54, '30Hz': 1.64}, 'B': {'1Hz': 2.3, '30Hz': 1.32}, 'C': {'1Hz': 5.95, '30Hz': 2.58}, 'D': {'1Hz': 1.85, '30Hz': 0.53}, 'X': {'1Hz': 1.88, '30Hz': 1.73}, 'Y': {'1Hz': 4.85, '30Hz': 2.06}, 'root': {'1Hz': 5.76, '30Hz': 6.42}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.928, 1.1493, 0.9987), (1.15, 0.94, 0.9471, 1.1998, 1.1369), (1.15, 0.94, 0.9464, 1.1738, 1.0188), (1.15, 0.94, 0.9381, 1.1833, 1.1028), (1.15, 0.94, 0.9403, 1.1368, 0.8845), (1.15, 0.94, 0.9436, 1.1356, 0.8664), (1.15, 0.94, 0.9408, 1.0941, 0.6873), (1.15, 0.94, 0.9393, 1.1636, 1.0088), (1.15, 0.94, 0.9371, 1.138, 0.9006), (1.3, 1.09, 1.0878, 1.2518, 0.7393), (1.3, 1.09, 1.0919, 1.2868, 0.8773), (1.3, 1.09, 1.0937, 1.2875, 0.8749), (1.3, 1.09, 1.1036, 1.2775, 0.7826), (1.3, 1.09, 1.1006, 1.2937, 0.8656), (1.15, 0.94, 0.9255, 1.1326, 0.9346), (1.15, 0.94, 0.939, 1.1053, 0.7498), (1.15, 0.94, 0.9371, 1.1079, 0.7683), (1.3, 1.09, 1.0866, 1.1972, 0.4987), (1.3, 1.09, 1.0882, 1.2289, 0.6352), (1.15, 0.94, 0.9279, 1.1434, 0.9714), (1.15, 0.94, 0.949, 1.1619, 0.9578), (1.15, 0.94, 0.9496, 1.1426, 0.8649), (1.3, 1.09, 1.0925, 1.2526, 0.7176), (1.3, 1.09, 1.0932, 1.2721, 0.8049), (1.3, 1.09, 1.0832, 1.189, 0.4759), (1.15, 0.94, 0.9391, 1.1116, 0.7765), (1.3, 1.09, 1.0992, 1.2474, 0.6668), (1.3, 1.09, 1.0874, 1.2071, 0.5365), (1.3, 1.09, 1.1046, 1.2854, 0.8158), (1.3, 1.09, 1.0921, 1.2613, 0.7623), (1.15, 0.94, 0.9399, 1.0996, 0.7186), (1.15, 0.94, 0.954, 1.1075, 0.688), (1.3, 1.09, 1.0838, 1.2301, 0.6601), (1.3, 1.09, 1.0901, 1.216, 0.564), (1.3, 1.09, 1.0864, 1.211, 0.5611), (1.15, 0.94, 0.937, 1.1125, 0.7922), (1.3, 1.09, 1.0882, 1.1974, 0.4915), (1.3, 1.09, 1.0856, 1.1683, 0.373), (1.15, 0.94, 0.9522, 1.1396, 0.8459), (1.15, 0.94, 0.9361, 1.1171, 0.816), (1.15, 0.94, 0.9426, 1.1517, 0.941), (1.3, 1.09, 1.0807, 1.1928, 0.5061), (1.3, 1.09, 1.0859, 1.215, 0.5809), (1.3, 1.09, 1.0953, 1.2099, 0.5137), (1.15, 0.94, 0.94, 1.1288, 0.8523), (1.15, 0.94, 0.9407, 1.1001, 0.7142), (1.15, 0.94, 0.9454, 1.1445, 0.896), (1.3, 1.09, 1.0972, 1.2255, 0.5772), (1.15, 0.94, 0.935, 1.1526, 0.98), (1.3, 1.09, 1.1056, 1.2131, 0.4839), (1.15, 0.94, 0.949, 1.1154, 0.7492), (1.3, 1.09, 1.0922, 1.2087, 0.5242), (1.3, 1.09, 1.0803, 1.1968, 0.5219), (1.3, 1.09, 1.0842, 1.2117, 0.5743)]; fq collisions None; errors []
- v3-C9-hdepth-tree16-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.741; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.06, '30Hz': 1.44}, 'B': {'1Hz': 5.72, '30Hz': 0.92}, 'C': {'1Hz': 3.65, '30Hz': 2.81}, 'D': {'1Hz': 0.95, '30Hz': 2.63}, 'X': {'1Hz': 1.75, '30Hz': 0.85}, 'Y': {'1Hz': 4.63, '30Hz': 1.42}, 'root': {'1Hz': 2.1, '30Hz': 1.73}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9262, 1.1358, 0.9483), (1.3, 1.09, 1.0969, 1.2338, 0.6176), (1.15, 0.94, 0.946, 1.1294, 0.8277), (1.3, 1.09, 1.092, 1.2378, 0.6579), (1.15, 0.94, 0.9481, 1.1332, 0.837), (1.3, 1.09, 1.0913, 1.2474, 0.7013), (1.3, 1.09, 1.1245, 1.3075, 0.8231), (1.15, 0.94, 0.9387, 1.1424, 0.9215), (1.15, 0.94, 0.9313, 1.1108, 0.8065), (1.15, 0.94, 0.9376, 1.1087, 0.7698), (1.15, 0.94, 0.9341, 1.1159, 0.8166), (1.3, 1.09, 1.1009, 1.1964, 0.4321), (1.3, 1.09, 1.083, 1.264, 0.8134), (1.15, 0.94, 0.932, 1.1118, 0.8112), (1.3, 1.09, 1.085, 1.2715, 0.8437), (1.15, 0.94, 0.9332, 1.1277, 0.8795), (1.3, 1.09, 1.0789, 1.2029, 0.5568), (1.3, 1.09, 1.0939, 1.2174, 0.5555), (1.15, 0.94, 0.9342, 1.1105, 0.795), (1.3, 1.09, 1.09, 1.2123, 0.5533), (1.15, 0.94, 0.944, 1.1519, 0.9343), (1.15, 0.94, 0.9188, 1.1388, 0.9895), (1.3, 1.09, 1.093, 1.2077, 0.5188), (1.3, 1.09, 1.1016, 1.2306, 0.5815), (1.15, 0.94, 0.9448, 1.1145, 0.7622), (1.15, 0.94, 0.9452, 1.1125, 0.7524), (1.3, 1.09, 1.0873, 1.1907, 0.4665), (1.15, 0.94, 0.9331, 1.1418, 0.9415), (1.15, 0.94, 0.9373, 1.1196, 0.8215), (1.3, 1.09, 1.0753, 1.2118, 0.6138), (1.3, 1.09, 1.0961, 1.268, 0.773), (1.15, 0.94, 0.9478, 1.1596, 0.9513), (1.3, 1.09, 1.0837, 1.1916, 0.4853), (1.3, 1.09, 1.0861, 1.2042, 0.5325), (1.15, 0.94, 0.9433, 1.1516, 0.9394), (1.3, 1.09, 1.0848, 1.2305, 0.6546), (1.3, 1.09, 1.0838, 1.2672, 0.8268), (1.3, 1.09, 1.0935, 1.2936, 0.899), (1.15, 0.94, 0.9381, 1.1288, 0.86), (1.15, 0.94, 0.9523, 1.1594, 0.9369), (1.3, 1.09, 1.0804, 1.2093, 0.5832), (1.3, 1.09, 1.0934, 1.2033, 0.4935), (1.3, 1.09, 1.0877, 1.2217, 0.6028), (1.15, 0.94, 0.943, 1.1288, 0.8406), (1.3, 1.09, 1.0813, 1.2388, 0.7101), (1.15, 0.94, 0.9467, 1.1034, 0.7049), (1.15, 0.94, 0.9391, 1.1562, 0.9764), (1.15, 0.94, 0.9377, 1.1476, 0.9467), (1.3, 1.09, 1.0855, 1.199, 0.5116), (1.3, 1.09, 1.0605, 1.2355, 0.7918), (1.15, 0.94, 0.938, 1.1075, 0.7621), (1.3, 1.09, 1.0896, 1.2511, 0.7283), (1.15, 0.94, 0.9533, 1.1468, 0.8723), (1.15, 0.94, 0.9381, 1.1167, 0.8022)]; fq collisions None; errors []
- v3-C9-hdepth-tree16-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.694; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.53, '30Hz': 1.56}, 'B': {'1Hz': 2.3, '30Hz': 1.32}, 'C': {'1Hz': 5.95, '30Hz': 2.6}, 'D': {'1Hz': 1.85, '30Hz': 0.52}, 'X': {'1Hz': 1.87, '30Hz': 1.75}, 'Y': {'1Hz': 4.86, '30Hz': 2.06}, 'root': {'1Hz': 5.76, '30Hz': 6.28}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.928, 1.1677, 1.0905), (1.15, 0.94, 0.9471, 1.1901, 1.1018), (1.15, 0.94, 0.9464, 1.1906, 1.1065), (1.15, 0.94, 0.9381, 1.1613, 1.0137), (1.15, 0.94, 0.9403, 1.1528, 0.9647), (1.15, 0.94, 0.9436, 1.1429, 0.9065), (1.15, 0.94, 0.9408, 1.1493, 0.9451), (1.15, 0.94, 0.9393, 1.1736, 1.064), (1.15, 0.94, 0.9371, 1.1313, 0.88), (1.3, 1.09, 1.0878, 1.283, 0.8865), (1.3, 1.09, 1.0919, 1.2763, 0.8364), (1.3, 1.09, 1.0935, 1.2845, 0.8677), (1.3, 1.09, 1.1036, 1.3268, 1.0122), (1.3, 1.09, 1.1006, 1.287, 0.845), (1.15, 0.94, 0.9255, 1.1387, 0.9687), (1.15, 0.94, 0.939, 1.1375, 0.9015), (1.15, 0.94, 0.9371, 1.1391, 0.9175), (1.3, 1.09, 1.0866, 1.2765, 0.8621), (1.3, 1.09, 1.0882, 1.2761, 0.8534), (1.15, 0.94, 0.9279, 1.1439, 0.9807), (1.15, 0.94, 0.949, 1.1474, 0.8994), (1.15, 0.94, 0.9496, 1.1527, 0.9201), (1.3, 1.09, 1.0925, 1.2809, 0.854), (1.3, 1.09, 1.0932, 1.2861, 0.8763), (1.3, 1.09, 1.0832, 1.2699, 0.8465), (1.15, 0.94, 0.9391, 1.1438, 0.9292), (1.3, 1.09, 1.0992, 1.2801, 0.8216), (1.3, 1.09, 1.0874, 1.2936, 0.9346), (1.3, 1.09, 1.1046, 1.2925, 0.8545), (1.3, 1.09, 1.0921, 1.2764, 0.8365), (1.15, 0.94, 0.9399, 1.1445, 0.9281), (1.15, 0.94, 0.954, 1.1554, 0.9129), (1.3, 1.09, 1.0838, 1.276, 0.8742), (1.3, 1.09, 1.0901, 1.277, 0.8471), (1.3, 1.09, 1.0864, 1.28, 0.879), (1.15, 0.94, 0.937, 1.136, 0.9042), (1.3, 1.09, 1.0882, 1.2802, 0.8716), (1.3, 1.09, 1.0856, 1.2741, 0.8578), (1.15, 0.94, 0.9522, 1.1537, 0.9153), (1.15, 0.94, 0.9361, 1.1443, 0.9452), (1.15, 0.94, 0.9426, 1.1411, 0.8999), (1.3, 1.09, 1.0807, 1.2701, 0.8601), (1.3, 1.09, 1.0859, 1.2739, 0.8526), (1.3, 1.09, 1.0953, 1.285, 0.8598), (1.15, 0.94, 0.94, 1.14, 0.9101), (1.15, 0.94, 0.9407, 1.1453, 0.9273), (1.15, 0.94, 0.9454, 1.1697, 1.0171), (1.3, 1.09, 1.0972, 1.2796, 0.8284), (1.15, 0.94, 0.935, 1.1545, 0.9965), (1.3, 1.09, 1.1056, 1.2961, 0.8641), (1.15, 0.94, 0.9489, 1.1581, 0.9485), (1.3, 1.09, 1.0922, 1.2801, 0.8517), (1.3, 1.09, 1.0803, 1.27, 0.8596), (1.3, 1.09, 1.0842, 1.281, 0.8935)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r0-eth2': {'bg_packets': 2191632, 'in_pinned_class': 346, 'flows': ['10.101.0.2:5237']}, 'r0-eth4': {'bg_packets': 2191938, 'in_pinned_class': 211254, 'flows': ['10.101.0.3:5203', '10.101.0.3:5215']}, 'r1-eth2': {'bg_packets': 1123281, 'in_pinned_class': 2634, 'flows': ['10.101.0.4:5238', '10.101.0.4:5248']}, 'r1-eth4': {'bg_packets': 1095673, 'in_pinned_class': 0, 'flows': []}, 'r2-eth2': {'bg_packets': 1124708, 'in_pinned_class': 1825, 'flows': ['10.101.0.6:5251']}, 'r2-eth4': {'bg_packets': 1096299, 'in_pinned_class': 0, 'flows': []}, 'rr-eth1': {'bg_packets': 62, 'in_pinned_class': 0, 'flows': []}, 'rr-eth2': {'bg_packets': 4378688, 'in_pinned_class': 1642, 'flows': ['10.101.0.1:5212', '10.101.0.1:5242', '10.101.0.1:5256']}}; errors []
- v3-C9-hdepth-tree16-fq_codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.706; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.06, '30Hz': 1.49}, 'B': {'1Hz': 5.72, '30Hz': 0.87}, 'C': {'1Hz': 3.66, '30Hz': 2.73}, 'D': {'1Hz': 0.96, '30Hz': 2.54}, 'X': {'1Hz': 1.76, '30Hz': 0.88}, 'Y': {'1Hz': 4.63, '30Hz': 1.39}, 'root': {'1Hz': 2.1, '30Hz': 1.69}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9262, 1.1718, 1.1185), (1.3, 1.09, 1.0969, 1.3013, 0.93), (1.15, 0.94, 0.946, 1.1512, 0.9331), (1.3, 1.09, 1.092, 1.2804, 0.8568), (1.15, 0.94, 0.9481, 1.1668, 0.9934), (1.3, 1.09, 1.0913, 1.2762, 0.8411), (1.3, 1.09, 1.1245, 1.3149, 0.8661), (1.15, 0.94, 0.9387, 1.1641, 1.026), (1.15, 0.94, 0.9313, 1.1346, 0.9245), (1.15, 0.94, 0.9376, 1.1428, 0.9335), (1.15, 0.94, 0.9341, 1.1502, 0.9829), (1.3, 1.09, 1.1009, 1.2921, 0.8684), (1.3, 1.09, 1.083, 1.2739, 0.8683), (1.15, 0.94, 0.932, 1.1325, 0.9115), (1.3, 1.09, 1.085, 1.2717, 0.8479), (1.15, 0.94, 0.9332, 1.1451, 0.9648), (1.3, 1.09, 1.0789, 1.2719, 0.8776), (1.3, 1.09, 1.0939, 1.2828, 0.8597), (1.15, 0.94, 0.9342, 1.139, 0.9324), (1.3, 1.09, 1.09, 1.2756, 0.8451), (1.15, 0.94, 0.944, 1.1797, 1.0721), (1.15, 0.94, 0.9188, 1.1519, 1.0603), (1.3, 1.09, 1.093, 1.2852, 0.8726), (1.3, 1.09, 1.1016, 1.2929, 0.8707), (1.15, 0.94, 0.9448, 1.1422, 0.8977), (1.15, 0.94, 0.9452, 1.1394, 0.8834), (1.3, 1.09, 1.0873, 1.2776, 0.8653), (1.15, 0.94, 0.933, 1.1451, 0.9644), (1.15, 0.94, 0.9373, 1.1416, 0.9297), (1.3, 1.09, 1.0753, 1.2666, 0.8702), (1.3, 1.09, 1.0961, 1.2871, 0.8687), (1.15, 0.94, 0.9478, 1.1775, 1.0445), (1.3, 1.09, 1.0837, 1.2702, 0.8486), (1.3, 1.09, 1.0861, 1.2864, 0.911), (1.15, 0.94, 0.9433, 1.164, 1.0047), (1.3, 1.09, 1.0848, 1.2715, 0.8491), (1.3, 1.09, 1.0838, 1.3029, 0.9971), (1.3, 1.09, 1.0935, 1.2955, 0.9185), (1.15, 0.94, 0.9381, 1.1536, 0.9802), (1.15, 0.94, 0.9523, 1.1681, 0.9804), (1.3, 1.09, 1.0804, 1.2697, 0.8618), (1.3, 1.09, 1.0935, 1.2915, 0.9005), (1.3, 1.09, 1.0877, 1.2775, 0.8635), (1.15, 0.94, 0.943, 1.1463, 0.9234), (1.3, 1.09, 1.0813, 1.3011, 0.9998), (1.15, 0.94, 0.9467, 1.1442, 0.8985), (1.15, 0.94, 0.9391, 1.1404, 0.9157), (1.15, 0.94, 0.9377, 1.1426, 0.9321), (1.3, 1.09, 1.0855, 1.2744, 0.8599), (1.3, 1.09, 1.0605, 1.2549, 0.8854), (1.15, 0.94, 0.938, 1.1417, 0.9263), (1.3, 1.09, 1.0896, 1.2756, 0.8457), (1.15, 0.94, 0.9533, 1.1884, 1.0693), (1.15, 0.94, 0.9381, 1.139, 0.9133)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r0-eth2': {'bg_packets': 2214985, 'in_pinned_class': 0, 'flows': []}, 'r0-eth4': {'bg_packets': 2217864, 'in_pinned_class': 2135, 'flows': ['10.101.0.3:5221']}, 'r1-eth2': {'bg_packets': 1137407, 'in_pinned_class': 0, 'flows': []}, 'r1-eth4': {'bg_packets': 1108287, 'in_pinned_class': 921, 'flows': ['10.101.0.5:5248']}, 'r2-eth2': {'bg_packets': 1137504, 'in_pinned_class': 391, 'flows': ['10.101.0.6:5238']}, 'r2-eth4': {'bg_packets': 1106220, 'in_pinned_class': 0, 'flows': []}, 'rr-eth1': {'bg_packets': 54, 'in_pinned_class': 0, 'flows': []}, 'rr-eth2': {'bg_packets': 4436697, 'in_pinned_class': 3634, 'flows': ['10.101.0.1:5209', '10.101.0.1:5252', '10.101.0.1:5255']}}; errors []
- v3-C9-hdepth-tree16-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.7419; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.53, '30Hz': 1.61}, 'B': {'1Hz': 2.3, '30Hz': 1.28}, 'C': {'1Hz': 5.94, '30Hz': 2.61}, 'D': {'1Hz': 1.85, '30Hz': 0.55}, 'X': {'1Hz': 1.87, '30Hz': 1.68}, 'Y': {'1Hz': 4.86, '30Hz': 2.01}, 'root': {'1Hz': 5.78, '30Hz': 6.24}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.928, 1.1959, 1.2146), (1.15, 0.94, 0.9471, 1.2256, 1.2613), (1.15, 0.94, 0.9464, 1.1904, 1.1054), (1.15, 0.94, 0.9381, 1.1717, 1.059), (1.15, 0.94, 0.9403, 1.1768, 1.0715), (1.15, 0.94, 0.9436, 1.1661, 1.0086), (1.15, 0.94, 0.9408, 1.1327, 0.8698), (1.15, 0.94, 0.9393, 1.1762, 1.0738), (1.15, 0.94, 0.9371, 1.1647, 1.0313), (1.3, 1.09, 1.0878, 1.2953, 0.9405), (1.3, 1.09, 1.0919, 1.2951, 0.9206), (1.3, 1.09, 1.0937, 1.3169, 1.0117), (1.3, 1.09, 1.1036, 1.3332, 1.0397), (1.3, 1.09, 1.1006, 1.3903, 1.3124), (1.15, 0.94, 0.9255, 1.1448, 0.9941), (1.15, 0.94, 0.939, 1.1899, 1.1373), (1.15, 0.94, 0.9371, 1.1357, 0.9004), (1.3, 1.09, 1.0866, 1.249, 0.7359), (1.3, 1.09, 1.0882, 1.3612, 1.2374), (1.15, 0.94, 0.9279, 1.1546, 1.0277), (1.15, 0.94, 0.949, 1.1947, 1.1128), (1.15, 0.94, 0.9497, 1.1703, 0.9994), (1.3, 1.09, 1.0925, 1.2897, 0.8936), (1.3, 1.09, 1.0933, 1.2736, 0.8175), (1.3, 1.09, 1.0832, 1.2476, 0.7448), (1.15, 0.94, 0.9391, 1.1401, 0.9109), (1.3, 1.09, 1.0992, 1.266, 0.7561), (1.3, 1.09, 1.0874, 1.2669, 0.8134), (1.3, 1.09, 1.1046, 1.29, 0.8404), (1.3, 1.09, 1.0921, 1.2528, 0.728), (1.15, 0.94, 0.9399, 1.1271, 0.8482), (1.15, 0.94, 0.954, 1.1624, 0.9441), (1.3, 1.09, 1.0839, 1.2948, 0.9561), (1.3, 1.09, 1.0901, 1.2422, 0.689), (1.3, 1.09, 1.0864, 1.2238, 0.623), (1.15, 0.94, 0.937, 1.1409, 0.9247), (1.3, 1.09, 1.0882, 1.2211, 0.6022), (1.3, 1.09, 1.0856, 1.2486, 0.7388), (1.15, 0.94, 0.9522, 1.1612, 0.9476), (1.15, 0.94, 0.9361, 1.1652, 1.0383), (1.15, 0.94, 0.9426, 1.2312, 1.3069), (1.3, 1.09, 1.0807, 1.2663, 0.8411), (1.3, 1.09, 1.0859, 1.2513, 0.7489), (1.3, 1.09, 1.0953, 1.2421, 0.665), (1.15, 0.94, 0.94, 1.2008, 1.1824), (1.15, 0.94, 0.9407, 1.1749, 1.0611), (1.15, 0.94, 0.9454, 1.2252, 1.267), (1.3, 1.09, 1.0972, 1.2572, 0.7255), (1.15, 0.94, 0.935, 1.137, 0.9156), (1.3, 1.09, 1.1056, 1.2475, 0.6424), (1.15, 0.94, 0.949, 1.1804, 1.0485), (1.3, 1.09, 1.0922, 1.2881, 0.8872), (1.3, 1.09, 1.0803, 1.2928, 0.9627), (1.3, 1.09, 1.0842, 1.2219, 0.6243)]; fq collisions None; errors []
- v3-C9-hdepth-tree16-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.7165; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.06, '30Hz': 1.48}, 'B': {'1Hz': 5.72, '30Hz': 0.95}, 'C': {'1Hz': 3.66, '30Hz': 2.7}, 'D': {'1Hz': 0.95, '30Hz': 2.51}, 'X': {'1Hz': 1.76, '30Hz': 0.85}, 'Y': {'1Hz': 4.63, '30Hz': 1.44}, 'root': {'1Hz': 2.1, '30Hz': 1.73}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9262, 1.179, 1.1464), (1.3, 1.09, 1.0969, 1.2393, 0.6452), (1.15, 0.94, 0.946, 1.1835, 1.0766), (1.3, 1.09, 1.092, 1.333, 1.0923), (1.15, 0.94, 0.9481, 1.187, 1.0828), (1.3, 1.09, 1.0913, 1.2999, 0.9455), (1.3, 1.09, 1.1245, 1.4256, 1.3633), (1.15, 0.94, 0.9387, 1.1586, 0.9973), (1.15, 0.94, 0.9313, 1.1525, 1.0024), (1.15, 0.94, 0.9376, 1.165, 1.0298), (1.15, 0.94, 0.9341, 1.1269, 0.8734), (1.3, 1.09, 1.1009, 1.281, 0.8165), (1.3, 1.09, 1.083, 1.2324, 0.6769), (1.15, 0.94, 0.932, 1.1598, 1.0322), (1.3, 1.09, 1.085, 1.2817, 0.8915), (1.15, 0.94, 0.9332, 1.1163, 0.8301), (1.3, 1.09, 1.0789, 1.2293, 0.6813), (1.3, 1.09, 1.0939, 1.2636, 0.7685), (1.15, 0.94, 0.9342, 1.1416, 0.9405), (1.3, 1.09, 1.09, 1.2661, 0.7984), (1.15, 0.94, 0.944, 1.1536, 0.9499), (1.15, 0.94, 0.9188, 1.1659, 1.1185), (1.3, 1.09, 1.093, 1.2958, 0.9189), (1.3, 1.09, 1.1016, 1.3034, 0.9151), (1.15, 0.94, 0.9448, 1.2034, 1.1716), (1.15, 0.94, 0.9452, 1.1283, 0.8289), (1.3, 1.09, 1.0873, 1.2532, 0.752), (1.15, 0.94, 0.9331, 1.2123, 1.2651), (1.15, 0.94, 0.9373, 1.1742, 1.074), (1.3, 1.09, 1.0753, 1.286, 0.954), (1.3, 1.09, 1.0961, 1.3074, 0.9568), (1.15, 0.94, 0.9478, 1.2031, 1.1565), (1.3, 1.09, 1.0837, 1.2652, 0.8219), (1.3, 1.09, 1.0861, 1.2154, 0.5857), (1.15, 0.94, 0.9433, 1.2084, 1.2019), (1.3, 1.09, 1.0848, 1.2729, 0.852), (1.3, 1.09, 1.0838, 1.2707, 0.8471), (1.3, 1.09, 1.0935, 1.3385, 1.1101), (1.15, 0.94, 0.9381, 1.1417, 0.9225), (1.15, 0.94, 0.9523, 1.1686, 0.9806), (1.3, 1.09, 1.0804, 1.2651, 0.8373), (1.3, 1.09, 1.0934, 1.3017, 0.9437), (1.3, 1.09, 1.0877, 1.3267, 1.0823), (1.15, 0.94, 0.943, 1.2107, 1.2137), (1.3, 1.09, 1.0812, 1.2276, 0.6634), (1.15, 0.94, 0.9467, 1.2033, 1.1618), (1.15, 0.94, 0.9391, 1.1421, 0.919), (1.15, 0.94, 0.9377, 1.1596, 1.0059), (1.3, 1.09, 1.0855, 1.2612, 0.7965), (1.3, 1.09, 1.0605, 1.3365, 1.2515), (1.15, 0.94, 0.938, 1.195, 1.1634), (1.3, 1.09, 1.0896, 1.3183, 1.0362), (1.15, 0.94, 0.9533, 1.1369, 0.8317), (1.15, 0.94, 0.9381, 1.1728, 1.0633)]; fq collisions None; errors []
- v3-G1-calm-legacy-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9362; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G1-calm-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9427; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.56, '30Hz': 2.21}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-access-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0, 'ra': 0, 'rb': 0, 'rc': 0, 'rd': 0}; unmatched total 0 (targets 0); cpu idle min 0.8704; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.56, '30Hz': 2.19}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-rev-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r0': 0, 'r1': 0}; unmatched total 0 (targets 0); cpu idle min 0.9045; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.56, '30Hz': 2.24}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-split4-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8816; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 0.65, '30Hz': 0.55}, 'b': {'1Hz': 2.33, '30Hz': 3.08}, 'up': {'1Hz': 2.01, '30Hz': 4.14}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-tree16-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'rr': 0, 'r0': 0, 'r1': 0, 'r2': 0}; unmatched total 2 (targets 2); cpu idle min 0.7869; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 5.37, '30Hz': 3.21}, 'B': {'1Hz': 2.42, '30Hz': 1.12}, 'C': {'1Hz': 3.7, '30Hz': 2.92}, 'D': {'1Hz': 3.41, '30Hz': 1.91}, 'X': {'1Hz': 0.57, '30Hz': 3.86}, 'Y': {'1Hz': 2.31, '30Hz': 0.66}, 'root': {'1Hz': 4.06, '30Hz': 1.78}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G2-calm-uneven-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8967; ECN {}; oversize {}, offloads not off []; phase {'A': {'1Hz': 1.18, '30Hz': 4.19}, 'B': {'1Hz': 0.57, '30Hz': 3.93}, 'C': {'1Hz': 5.08, '30Hz': 1.95}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-G3-sburst-s030u070-fq_codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9252; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.46}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1712, 1.0359), (1.05, 0.84, 0.8482, 1.049, 0.8956), (1.3, 1.09, 1.0808, 1.2274, 0.654), (1.15, 0.94, 0.9408, 1.0954, 0.6898), (1.3, 1.09, 1.0827, 1.2221, 0.6218), (1.15, 0.94, 0.9308, 1.0914, 0.7168), (1.05, 0.84, 0.8453, 1.0327, 0.8363), (1.05, 0.84, 0.8352, 1.0294, 0.8665), (1.05, 0.84, 0.8421, 1.0306, 0.841), (1.15, 0.94, 0.9389, 1.0883, 0.6669), (1.05, 0.84, 0.838, 1.019, 0.8076), (1.3, 1.09, 1.0877, 1.2351, 0.6578), (1.15, 0.94, 0.9537, 1.1263, 0.77), (1.3, 1.09, 1.0928, 1.2313, 0.6182), (1.3, 1.09, 1.0806, 1.2278, 0.6566), (1.05, 0.84, 0.8348, 1.0168, 0.8118), (1.3, 1.09, 1.0883, 1.204, 0.5164), (1.15, 0.94, 0.9348, 1.0907, 0.6956)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'router-eth1': {'bg_packets': 21, 'in_pinned_class': 0, 'flows': []}, 'router-eth2': {'bg_packets': 1095329, 'in_pinned_class': 1564, 'flows': ['10.101.0.1:5218']}}; errors []
- v3-G3-sburst-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.938; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.59, '30Hz': 1.5}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1265, 0.8498), (1.05, 0.84, 0.8482, 1.0857, 1.0763), (1.3, 1.09, 1.0808, 1.2121, 0.5952), (1.15, 0.94, 0.9408, 1.155, 0.971), (1.3, 1.09, 1.0827, 1.1775, 0.4294), (1.15, 0.94, 0.9308, 1.0988, 0.7617), (1.05, 0.84, 0.8453, 1.0609, 0.9777), (1.05, 0.84, 0.8352, 1.0851, 1.1326), (1.05, 0.84, 0.8421, 1.0825, 1.0896), (1.15, 0.94, 0.9389, 1.1432, 0.9263), (1.05, 0.84, 0.838, 1.0551, 0.9839), (1.3, 1.09, 1.0877, 1.1842, 0.4374), (1.15, 0.94, 0.9537, 1.1322, 0.8091), (1.3, 1.09, 1.0928, 1.1871, 0.4276), (1.3, 1.09, 1.0806, 1.2248, 0.6536), (1.05, 0.84, 0.8348, 1.0337, 0.9013), (1.3, 1.09, 1.0883, 1.2055, 0.5312), (1.15, 0.94, 0.9348, 1.1151, 0.8171)]; fq collisions None; errors []
- v3-M1-sburst-q100-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9509; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.59, '30Hz': 1.51}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1554, 0.9811), (1.05, 0.84, 0.8482, 1.0498, 0.9135), (1.3, 1.09, 1.0808, 1.2106, 0.5883), (1.15, 0.94, 0.9408, 1.1388, 0.8977), (1.3, 1.09, 1.0827, 1.18, 0.4408), (1.15, 0.94, 0.9308, 1.0917, 0.7292), (1.05, 0.84, 0.8453, 1.046, 0.9099), (1.05, 0.84, 0.8352, 1.0255, 0.8623), (1.05, 0.84, 0.8421, 1.0468, 0.9276), (1.15, 0.94, 0.9389, 1.1301, 0.8668), (1.05, 0.84, 0.838, 1.0514, 0.9672), (1.3, 1.09, 1.0877, 1.1809, 0.4224), (1.15, 0.94, 0.9537, 1.131, 0.8035), (1.3, 1.09, 1.0928, 1.174, 0.3681), (1.3, 1.09, 1.0806, 1.1961, 0.5234), (1.05, 0.84, 0.8349, 1.0347, 0.9058), (1.3, 1.09, 1.0883, 1.1727, 0.3828), (1.15, 0.94, 0.9348, 1.0925, 0.7146)]; fq collisions None; errors []
- v3-M1-sburst-q100-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9243; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.01}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1913, 0.4785), (1.15, 0.94, 0.9445, 1.1528, 0.9509), (1.15, 0.94, 0.9415, 1.1017, 0.7311), (1.05, 0.84, 0.8444, 1.047, 0.9248), (1.15, 0.94, 0.9365, 1.1062, 0.7748), (1.05, 0.84, 0.8358, 1.0514, 0.9842), (1.05, 0.84, 0.8432, 1.062, 0.9985), (1.15, 0.94, 0.9448, 1.0813, 0.6229), (1.3, 1.09, 1.0947, 1.1684, 0.3365), (1.3, 1.09, 1.0807, 1.2461, 0.7551), (1.3, 1.09, 1.0873, 1.1706, 0.3803), (1.3, 1.09, 1.0973, 1.1991, 0.4649), (1.15, 0.94, 0.9467, 1.1171, 0.7777), (1.05, 0.84, 0.8343, 1.0569, 1.0166), (1.05, 0.84, 0.8375, 1.0406, 0.9271), (1.05, 0.84, 0.8423, 1.0399, 0.9023), (1.15, 0.94, 0.9446, 1.078, 0.6092), (1.3, 1.09, 1.0943, 1.1897, 0.4352)]; fq collisions None; errors []
- v3-M1-sburst-q300-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9535; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.51}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.0798, 0.6327), (1.05, 0.84, 0.8482, 1.0247, 0.7932), (1.3, 1.09, 1.0808, 1.264, 0.8233), (1.15, 0.94, 0.9408, 1.1149, 0.7825), (1.3, 1.09, 1.0827, 1.1813, 0.4432), (1.15, 0.94, 0.9308, 1.1371, 0.9275), (1.05, 0.84, 0.8453, 1.055, 0.943), (1.05, 0.84, 0.8352, 1.0319, 0.8841), (1.05, 0.84, 0.8421, 1.0359, 0.8711), (1.15, 0.94, 0.9389, 1.046, 0.4813), (1.05, 0.84, 0.838, 1.0515, 0.9596), (1.3, 1.09, 1.0877, 1.1854, 0.4395), (1.15, 0.94, 0.9537, 1.1494, 0.8795), (1.3, 1.09, 1.0928, 1.1798, 0.3914), (1.3, 1.09, 1.0806, 1.233, 0.685), (1.05, 0.84, 0.8348, 1.0422, 0.932), (1.3, 1.09, 1.0883, 1.1491, 0.2736), (1.15, 0.94, 0.9348, 1.0705, 0.6098)]; fq collisions None; errors []
- v3-M1-sburst-q300-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.926; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.77, '30Hz': 1.01}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1884, 0.4606), (1.15, 0.94, 0.9444, 1.147, 0.9154), (1.15, 0.94, 0.9415, 1.0481, 0.4818), (1.05, 0.84, 0.8444, 1.0103, 0.7501), (1.15, 0.94, 0.9365, 1.1435, 0.9356), (1.05, 0.84, 0.8358, 1.0512, 0.9739), (1.05, 0.84, 0.8432, 1.0643, 0.9991), (1.15, 0.94, 0.9448, 1.0874, 0.6445), (1.3, 1.09, 1.0947, 1.1521, 0.2596), (1.3, 1.09, 1.0807, 1.2435, 0.7356), (1.3, 1.09, 1.0873, 1.1416, 0.2453), (1.3, 1.09, 1.0973, 1.1938, 0.4364), (1.15, 0.94, 0.9467, 1.1415, 0.8804), (1.05, 0.84, 0.8343, 1.0448, 0.9517), (1.05, 0.84, 0.8375, 1.0129, 0.7929), (1.05, 0.84, 0.8423, 1.0459, 0.9202), (1.15, 0.94, 0.9446, 1.1331, 0.8519), (1.3, 1.09, 1.0943, 1.2602, 0.7498)]; fq collisions None; errors []
- v3-M10-sburst-ip2-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9361; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.46}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1305, 0.8615), (1.05, 0.84, 0.8482, 1.0809, 1.0465), (1.3, 1.09, 1.0808, 1.2032, 0.5507), (1.15, 0.94, 0.9408, 1.084, 0.6442), (1.3, 1.09, 1.0827, 1.1975, 0.5162), (1.15, 0.94, 0.9308, 1.0811, 0.676), (1.05, 0.84, 0.8453, 1.053, 0.9345), (1.05, 0.84, 0.8352, 1.0998, 1.1902), (1.05, 0.84, 0.8421, 1.0679, 1.0159), (1.15, 0.94, 0.9389, 1.1022, 0.7345), (1.05, 0.84, 0.838, 1.057, 0.985), (1.3, 1.09, 1.0877, 1.1922, 0.4702), (1.15, 0.94, 0.9537, 1.1228, 0.7605), (1.3, 1.09, 1.0928, 1.1851, 0.4153), (1.3, 1.09, 1.0806, 1.2126, 0.5938), (1.05, 0.84, 0.8348, 1.0397, 0.9215), (1.3, 1.09, 1.0883, 1.1788, 0.4072), (1.15, 0.94, 0.9348, 1.1132, 0.8024)]; fq collisions None; errors []
- v3-M10-sburst-ip2-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9412; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 0.99}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.212, 0.5708), (1.15, 0.94, 0.9445, 1.1813, 1.0774), (1.15, 0.94, 0.9415, 1.1327, 0.8698), (1.05, 0.84, 0.8444, 1.0973, 1.1506), (1.15, 0.94, 0.9365, 1.1266, 0.8648), (1.05, 0.84, 0.8358, 1.0671, 1.0523), (1.05, 0.84, 0.8432, 1.0706, 1.0345), (1.15, 0.94, 0.9448, 1.1271, 0.8294), (1.3, 1.09, 1.0947, 1.1674, 0.331), (1.3, 1.09, 1.0807, 1.1881, 0.4884), (1.3, 1.09, 1.0873, 1.1736, 0.3924), (1.3, 1.09, 1.0973, 1.191, 0.4266), (1.15, 0.94, 0.9467, 1.1269, 0.8196), (1.05, 0.84, 0.8343, 1.0622, 1.0371), (1.05, 0.84, 0.8375, 1.0785, 1.0967), (1.05, 0.84, 0.8423, 1.0667, 1.0208), (1.15, 0.94, 0.9446, 1.0956, 0.6869), (1.3, 1.09, 1.0943, 1.1878, 0.4251)]; fq collisions None; errors []
- v3-M10-sburst-ip8-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9209; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.46}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1442, 0.9341), (1.05, 0.84, 0.8482, 1.0897, 1.099), (1.3, 1.09, 1.0808, 1.2339, 0.6969), (1.15, 0.94, 0.9408, 1.1341, 0.8799), (1.3, 1.09, 1.0827, 1.1955, 0.5134), (1.15, 0.94, 0.9308, 1.1367, 0.9371), (1.05, 0.84, 0.8453, 1.0642, 0.9966), (1.05, 0.84, 0.8352, 1.0818, 1.1221), (1.05, 0.84, 0.8421, 1.0969, 1.1596), (1.15, 0.94, 0.9389, 1.1735, 1.0679), (1.05, 0.84, 0.838, 1.0779, 1.0917), (1.3, 1.09, 1.0877, 1.1902, 0.4669), (1.15, 0.94, 0.9537, 1.2179, 1.2026), (1.3, 1.09, 1.0928, 1.2071, 0.5203), (1.3, 1.09, 1.0806, 1.2587, 0.8107), (1.05, 0.84, 0.8348, 1.0474, 0.9673), (1.3, 1.09, 1.0883, 1.2014, 0.5149), (1.15, 0.94, 0.9348, 1.1601, 1.0254)]; fq collisions None; errors []
- v3-M10-sburst-ip8-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9416; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.0}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.2193, 0.6115), (1.15, 0.94, 0.9445, 1.1903, 1.1322), (1.15, 0.94, 0.9415, 1.149, 0.9557), (1.05, 0.84, 0.8444, 1.0796, 1.0837), (1.15, 0.94, 0.9365, 1.1967, 1.1986), (1.05, 0.84, 0.8358, 1.062, 1.0424), (1.05, 0.84, 0.8432, 1.0831, 1.1053), (1.15, 0.94, 0.9448, 1.1507, 0.9483), (1.3, 1.09, 1.0947, 1.1771, 0.3795), (1.3, 1.09, 1.0807, 1.2445, 0.7544), (1.3, 1.09, 1.0873, 1.1774, 0.4148), (1.3, 1.09, 1.0973, 1.1983, 0.4657), (1.15, 0.94, 0.9467, 1.1644, 1.003), (1.05, 0.84, 0.8343, 1.0765, 1.1161), (1.05, 0.84, 0.8375, 1.0787, 1.1112), (1.05, 0.84, 0.8423, 1.0829, 1.1085), (1.15, 0.94, 0.9446, 1.1654, 1.0173), (1.3, 1.09, 1.0943, 1.2153, 0.5573)]; fq collisions None; errors []
- v3-M11-sburst-bw4x1-pfifo-r1: lost 0; target egresses failing ['router-eth2']; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9347; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.11, '30Hz': 2.4}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.695, 0.6954, 1.271, 1.1883), (1.05, 0.595, 0.5885, 1.1497, 1.1586), (1.3, 0.845, 0.8388, 1.266, 0.882), (1.15, 0.695, 0.706, 1.2393, 1.1011), (1.3, 0.845, 0.8599, 1.2673, 0.841), (1.15, 0.695, 0.7114, 1.2428, 1.0969), (1.05, 0.595, 0.6225, 1.1286, 1.0449), (1.05, 0.595, 0.5849, 1.1334, 1.1323), (1.05, 0.595, 0.6032, 1.1534, 1.1358), (1.15, 0.695, 0.7056, 1.1738, 0.9664), (1.05, 0.595, 0.5892, 1.112, 1.0794), (1.3, 0.845, 0.8278, 1.2741, 0.9214), (1.15, 0.695, 0.6906, 1.2053, 1.0626), (1.3, 0.845, 0.8551, 1.2745, 0.8659), (1.3, 0.845, 0.8586, 1.286, 0.8825), (1.05, 0.595, 0.5874, 1.0668, 0.9898), (1.3, 0.845, 0.8386, 1.222, 0.7914), (1.15, 0.695, 0.686, 1.2397, 1.143)]; fq collisions None; errors []
- v3-M11-sburst-bw4x1-pfifo-r2: lost 0; target egresses failing ['router-eth2']; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9337; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.05, '30Hz': 2.56}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 0.845, 0.7868, 1.3251, 1.1091), (1.15, 0.695, 0.7087, 1.1972, 1.0065), (1.15, 0.695, 0.6963, 1.1917, 1.0207), (1.05, 0.595, 0.6066, 1.1485, 1.1166), (1.15, 0.695, 0.6999, 1.2458, 1.1247), (1.05, 0.595, 0.5819, 1.137, 1.1437), (1.05, 0.595, 0.5792, 1.1661, 1.2092), (1.15, 0.695, 0.6978, 1.1999, 1.0344), (1.3, 0.845, 0.8421, 1.2701, 0.8818), (1.3, 0.845, 0.8267, 1.2854, 0.9451), (1.3, 0.845, 0.8434, 1.2359, 0.8087), (1.3, 0.845, 0.8368, 1.2385, 0.8277), (1.15, 0.695, 0.6695, 1.1831, 1.0582), (1.05, 0.595, 0.6082, 1.1363, 1.0881), (1.05, 0.595, 0.5997, 1.1276, 1.0877), (1.05, 0.595, 0.6241, 1.1086, 0.9982), (1.15, 0.695, 0.7067, 1.2061, 1.0288), (1.3, 0.845, 0.8339, 1.3196, 1.0009)]; fq collisions None; errors []
- v3-M11-sburst-bw4x12-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.8978; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 4.09, '30Hz': 3.72}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.695, 0.6932, 1.1643, 0.9931), (1.05, 0.595, 0.603, 1.1209, 1.0916), (1.3, 0.845, 0.8327, 1.2608, 0.9022), (1.15, 0.695, 0.6886, 1.1308, 0.9322), (1.3, 0.845, 0.8447, 1.1592, 0.6629), (1.15, 0.695, 0.6887, 1.1432, 0.9579), (1.05, 0.595, 0.5925, 1.0657, 0.9973), (1.05, 0.595, 0.5958, 1.1053, 1.0738), (1.05, 0.595, 0.5964, 1.0963, 1.0536), (1.15, 0.695, 0.6951, 1.1353, 0.9279), (1.05, 0.595, 0.5949, 1.0965, 1.0572), (1.3, 0.845, 0.8407, 1.1768, 0.7085), (1.15, 0.695, 0.6959, 1.2447, 1.1568), (1.3, 0.845, 0.8605, 1.1551, 0.6208), (1.3, 0.845, 0.8335, 1.1239, 0.6122), (1.05, 0.595, 0.5929, 1.1235, 1.1184), (1.3, 0.845, 0.8457, 1.1583, 0.659), (1.15, 0.695, 0.6833, 1.1286, 0.9385)]; fq collisions None; errors []
- v3-M11-sburst-bw4x12-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9368; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 0.37, '30Hz': 0.71}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 0.845, 0.8419, 1.1798, 0.7112), (1.15, 0.695, 0.703, 1.1169, 0.8713), (1.15, 0.695, 0.6938, 1.1286, 0.9152), (1.05, 0.595, 0.5988, 1.1129, 1.0825), (1.15, 0.695, 0.7104, 1.2155, 1.0633), (1.05, 0.595, 0.6093, 1.1282, 1.0923), (1.05, 0.595, 0.6142, 1.1375, 1.1015), (1.15, 0.695, 0.6961, 1.1121, 0.8759), (1.3, 0.845, 0.8486, 1.166, 0.6682), (1.3, 0.845, 0.8292, 1.2603, 0.9075), (1.3, 0.845, 0.8444, 1.1265, 0.5938), (1.3, 0.845, 0.8525, 1.1269, 0.5776), (1.15, 0.695, 0.6925, 1.18, 1.0263), (1.05, 0.595, 0.5936, 1.1174, 1.1028), (1.05, 0.595, 0.5926, 1.0958, 1.0594), (1.05, 0.595, 0.5909, 1.0763, 1.022), (1.15, 0.695, 0.6958, 1.1507, 0.9575), (1.3, 0.845, 0.8432, 1.2, 0.7511)]; fq collisions None; errors []
- v3-M11-sburst-bw4x8-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9393; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.27, '30Hz': 3.85}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.695, 0.6917, 1.1406, 0.9518), (1.05, 0.595, 0.5976, 1.071, 1.0036), (1.3, 0.845, 0.8385, 1.1887, 0.7426), (1.15, 0.695, 0.692, 1.1119, 0.8902), (1.3, 0.845, 0.8434, 1.1143, 0.5744), (1.15, 0.695, 0.6896, 1.1889, 1.0587), (1.05, 0.595, 0.5975, 1.0973, 1.0596), (1.05, 0.595, 0.5997, 1.0807, 1.0197), (1.05, 0.595, 0.5982, 1.0725, 1.0054), (1.15, 0.695, 0.6932, 1.1419, 0.9512), (1.05, 0.595, 0.5955, 1.0562, 0.9767), (1.3, 0.845, 0.844, 1.1721, 0.6957), (1.15, 0.695, 0.6877, 1.2241, 1.137), (1.3, 0.845, 0.8537, 1.1293, 0.5843), (1.3, 0.845, 0.8327, 1.1979, 0.7742), (1.05, 0.595, 0.5921, 1.0292, 0.9267), (1.3, 0.845, 0.8415, 1.1417, 0.6362), (1.15, 0.695, 0.6868, 1.0972, 0.87)]; fq collisions None; errors []
- v3-M11-sburst-bw4x8-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9246; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.4, '30Hz': 5.65}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 0.845, 0.8398, 1.1849, 0.7319), (1.15, 0.695, 0.6999, 1.199, 1.0586), (1.15, 0.695, 0.6982, 1.1102, 0.8737), (1.05, 0.595, 0.6003, 1.0819, 1.0214), (1.15, 0.695, 0.6919, 1.1978, 1.0728), (1.05, 0.595, 0.6, 1.111, 1.0837), (1.05, 0.595, 0.6046, 1.1005, 1.0516), (1.15, 0.695, 0.692, 1.0829, 0.829), (1.3, 0.845, 0.8483, 1.1393, 0.6171), (1.3, 0.845, 0.8497, 1.1853, 0.7118), (1.3, 0.845, 0.8463, 1.1404, 0.6237), (1.3, 0.845, 0.8508, 1.1134, 0.5569), (1.15, 0.695, 0.6849, 1.1804, 1.0509), (1.05, 0.595, 0.5926, 1.0568, 0.9846), (1.05, 0.595, 0.5937, 1.0603, 0.9896), (1.05, 0.595, 0.5908, 1.0696, 1.0154), (1.15, 0.695, 0.6954, 1.11, 0.8793), (1.3, 0.845, 0.8403, 1.2016, 0.7662)]; fq collisions None; errors []
- v3-M12-sburst-jitfwd-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9386; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.46}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1207, 0.8212), (1.05, 0.84, 0.8482, 1.05, 0.9121), (1.3, 1.09, 1.0808, 1.1827, 0.4604), (1.15, 0.94, 0.9408, 1.1275, 0.8439), (1.3, 1.09, 1.0827, 1.1677, 0.3841), (1.15, 0.94, 0.9308, 1.1075, 0.7988), (1.05, 0.84, 0.8453, 1.0611, 0.9754), (1.05, 0.84, 0.8352, 1.0645, 1.0362), (1.05, 0.84, 0.8421, 1.0587, 0.9787), (1.15, 0.94, 0.9389, 1.1124, 0.7842), (1.05, 0.84, 0.838, 1.0624, 1.0142), (1.3, 1.09, 1.0877, 1.1776, 0.4066), (1.15, 0.94, 0.9537, 1.1191, 0.7473), (1.3, 1.09, 1.0928, 1.1842, 0.4134), (1.3, 1.09, 1.0806, 1.1955, 0.5191), (1.05, 0.84, 0.8348, 1.0445, 0.9477), (1.3, 1.09, 1.0883, 1.1591, 0.3199), (1.15, 0.94, 0.9348, 1.0947, 0.7227)]; fq collisions None; errors []
- v3-M12-sburst-jitfwd-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9397; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.01}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1883, 0.4656), (1.15, 0.94, 0.9445, 1.1454, 0.919), (1.15, 0.94, 0.9415, 1.113, 0.7842), (1.05, 0.84, 0.8444, 1.0685, 1.0251), (1.15, 0.94, 0.9365, 1.111, 0.7982), (1.05, 0.84, 0.8358, 1.0374, 0.9225), (1.05, 0.84, 0.8432, 1.0685, 1.0307), (1.15, 0.94, 0.9448, 1.1269, 0.8328), (1.3, 1.09, 1.0947, 1.1742, 0.3638), (1.3, 1.09, 1.0807, 1.2807, 0.9149), (1.3, 1.09, 1.0873, 1.1701, 0.3783), (1.3, 1.09, 1.0973, 1.1839, 0.3964), (1.15, 0.94, 0.9467, 1.1116, 0.7543), (1.05, 0.84, 0.8343, 1.0835, 1.1401), (1.05, 0.84, 0.8375, 1.0637, 1.0347), (1.05, 0.84, 0.8423, 1.0834, 1.1032), (1.15, 0.94, 0.9446, 1.1343, 0.8678), (1.3, 1.09, 1.0944, 1.2059, 0.5103)]; fq collisions None; errors []
- v3-M12-sburst-jitrev-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9378; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.48}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1395, 0.9172), (1.05, 0.84, 0.8482, 1.1016, 1.1592), (1.3, 1.09, 1.0808, 1.1826, 0.4656), (1.15, 0.94, 0.9408, 1.121, 0.8244), (1.3, 1.09, 1.0827, 1.1941, 0.5094), (1.15, 0.94, 0.9308, 1.1097, 0.8184), (1.05, 0.84, 0.8453, 1.0503, 0.938), (1.05, 0.84, 0.8352, 1.0817, 1.1277), (1.05, 0.84, 0.8421, 1.084, 1.1066), (1.15, 0.94, 0.9389, 1.1344, 0.8946), (1.05, 0.84, 0.838, 1.0852, 1.1308), (1.3, 1.09, 1.0877, 1.2017, 0.5217), (1.15, 0.94, 0.9537, 1.1483, 0.8903), (1.3, 1.09, 1.0928, 1.1916, 0.4522), (1.3, 1.09, 1.0806, 1.2073, 0.5794), (1.05, 0.84, 0.8348, 1.0349, 0.9154), (1.3, 1.09, 1.0883, 1.1766, 0.4041), (1.15, 0.94, 0.9348, 1.1421, 0.9483)]; fq collisions None; errors []
- v3-M12-sburst-jitrev-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9368; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 0.99}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.2042, 0.5385), (1.15, 0.94, 0.9445, 1.1556, 0.9663), (1.15, 0.94, 0.9415, 1.1708, 1.0497), (1.05, 0.84, 0.8444, 1.1128, 1.2287), (1.15, 0.94, 0.9365, 1.1217, 0.8477), (1.05, 0.84, 0.8358, 1.0832, 1.1328), (1.05, 0.84, 0.8432, 1.077, 1.0701), (1.15, 0.94, 0.9448, 1.1217, 0.8096), (1.3, 1.09, 1.0947, 1.189, 0.432), (1.3, 1.09, 1.0807, 1.1915, 0.5074), (1.3, 1.09, 1.0873, 1.2232, 0.6222), (1.3, 1.09, 1.0973, 1.173, 0.3468), (1.15, 0.94, 0.9467, 1.1713, 1.0281), (1.05, 0.84, 0.8343, 1.0742, 1.0984), (1.05, 0.84, 0.8375, 1.0906, 1.1589), (1.05, 0.84, 0.8423, 1.1149, 1.248), (1.15, 0.94, 0.9446, 1.1399, 0.8941), (1.3, 1.09, 1.0943, 1.1974, 0.4718)]; fq collisions None; errors []
- v3-M13-sburst-copa-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9421; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.59, '30Hz': 1.48}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.0643, 0.5782), (1.05, 0.84, 0.8482, 1.0479, 0.9217), (1.3, 1.09, 1.0808, 1.2162, 0.625), (1.15, 0.94, 0.9408, 1.051, 0.5086), (1.3, 1.09, 1.0827, 1.1753, 0.4273), (1.15, 0.94, 0.9308, 1.0798, 0.6875), (1.05, 0.84, 0.8453, 1.0418, 0.9072), (1.05, 0.84, 0.8352, 1.0493, 0.988), (1.05, 0.84, 0.8421, 1.0294, 0.8645), (1.15, 0.94, 0.9389, 1.0583, 0.551), (1.05, 0.84, 0.838, 1.0321, 0.8956), (1.3, 1.09, 1.0877, 1.1813, 0.4324), (1.15, 0.94, 0.9537, 1.0919, 0.6376), (1.3, 1.09, 1.0928, 1.1885, 0.4421), (1.3, 1.09, 1.0806, 1.2048, 0.5734), (1.05, 0.84, 0.8348, 1.0308, 0.9046), (1.3, 1.09, 1.0883, 1.198, 0.5065), (1.15, 0.94, 0.9348, 1.0492, 0.5282)]; fq collisions None; errors []
- v3-M13-sburst-copa-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9352; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.0}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1828, 0.4446), (1.15, 0.94, 0.9445, 1.0852, 0.6497), (1.15, 0.94, 0.9415, 1.0604, 0.549), (1.05, 0.84, 0.8444, 1.0474, 0.9374), (1.15, 0.94, 0.9365, 1.0684, 0.6089), (1.05, 0.84, 0.8358, 1.0301, 0.8971), (1.05, 0.84, 0.8432, 1.0388, 0.9029), (1.15, 0.94, 0.9448, 1.0534, 0.5015), (1.3, 1.09, 1.0947, 1.1997, 0.4851), (1.3, 1.09, 1.0807, 1.1998, 0.55), (1.3, 1.09, 1.0873, 1.2286, 0.6523), (1.3, 1.09, 1.0972, 1.183, 0.396), (1.15, 0.94, 0.9467, 1.0558, 0.5038), (1.05, 0.84, 0.8343, 1.0264, 0.887), (1.05, 0.84, 0.8375, 1.0489, 0.9761), (1.05, 0.84, 0.8423, 1.0321, 0.8762), (1.15, 0.94, 0.9446, 1.064, 0.5513), (1.3, 1.09, 1.0943, 1.2142, 0.5533)]; fq collisions None; errors []
- v3-M13-sburst-copa-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9376; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.44}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.2625, 1.4931), (1.05, 0.84, 0.8482, 1.0944, 1.1363), (1.3, 1.09, 1.0808, 1.3845, 1.4018), (1.15, 0.94, 0.9408, 1.2116, 1.2504), (1.3, 1.09, 1.0827, 1.4163, 1.5398), (1.15, 0.94, 0.9308, 1.1894, 1.194), (1.05, 0.84, 0.8453, 1.0701, 1.0381), (1.05, 0.84, 0.8352, 1.0751, 1.1075), (1.05, 0.84, 0.8421, 1.0746, 1.0731), (1.15, 0.94, 0.9389, 1.2283, 1.3359), (1.05, 0.84, 0.838, 1.0648, 1.047), (1.3, 1.09, 1.0877, 1.3744, 1.3236), (1.15, 0.94, 0.9537, 1.2342, 1.2948), (1.3, 1.09, 1.0928, 1.3816, 1.3331), (1.3, 1.09, 1.0806, 1.3831, 1.3964), (1.05, 0.84, 0.8349, 1.0433, 0.9622), (1.3, 1.09, 1.0883, 1.3701, 1.3008), (1.15, 0.94, 0.9348, 1.2046, 1.2454)]; fq collisions None; errors []
- v3-M13-sburst-copa-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9149; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 0.98}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.3702, 1.3105), (1.15, 0.94, 0.9445, 1.2306, 1.3214), (1.15, 0.94, 0.9415, 1.2691, 1.5133), (1.05, 0.84, 0.8444, 1.1352, 1.3433), (1.15, 0.94, 0.9365, 1.2083, 1.2556), (1.05, 0.84, 0.8358, 1.0613, 1.0419), (1.05, 0.84, 0.8432, 1.0906, 1.1429), (1.15, 0.94, 0.9448, 1.2077, 1.2145), (1.3, 1.09, 1.0947, 1.3969, 1.396), (1.3, 1.09, 1.0807, 1.3819, 1.3914), (1.3, 1.09, 1.0873, 1.4013, 1.45), (1.3, 1.09, 1.0972, 1.3849, 1.3289), (1.15, 0.94, 0.9467, 1.2083, 1.2083), (1.05, 0.84, 0.8343, 1.0523, 1.0073), (1.05, 0.84, 0.8375, 1.0813, 1.1261), (1.05, 0.84, 0.8423, 1.0801, 1.0985), (1.15, 0.94, 0.9446, 1.2884, 1.5882), (1.3, 1.09, 1.0943, 1.3815, 1.3262)]; fq collisions None; errors []
- v3-M14-ssparse-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9359; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.87, '30Hz': 1.82}}; surge (u, planned non-video, measured, total, video / calm) [(1.05, 0.84, 0.8403, 1.1195, 1.2834), (1.15, 0.94, 0.9441, 1.1142, 0.7821), (1.3, 1.09, 1.0722, 1.1853, 0.5197), (1.15, 0.94, 0.9365, 1.1721, 1.0831), (1.3, 1.09, 1.0903, 1.1757, 0.3925), (1.15, 0.94, 0.9471, 1.1278, 0.8306), (1.05, 0.84, 0.841, 1.0733, 1.0678), (1.3, 1.09, 1.0823, 1.2404, 0.7268), (1.05, 0.84, 0.8368, 1.0647, 1.0477)]; fq collisions None; errors []
- v3-M14-ssparse-s030u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.939; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 3.72, '30Hz': 1.53}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9415, 1.1967, 1.178), (1.3, 1.09, 1.0961, 1.1828, 0.4), (1.05, 0.84, 0.8338, 1.0569, 1.03), (1.15, 0.94, 0.9488, 1.1323, 0.8469), (1.3, 1.09, 1.0867, 1.2026, 0.535), (1.05, 0.84, 0.8399, 1.079, 1.1041), (1.05, 0.84, 0.8417, 1.0593, 1.0048), (1.15, 0.94, 0.946, 1.1467, 0.9262), (1.3, 1.09, 1.0949, 1.1847, 0.4147)]; fq collisions None; errors []
- v3-M2-sburst-capdrop-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9518; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.5}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-M2-sburst-capdrop-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9394; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 0.98}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-M2-sburst-capdrop-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.949; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.47}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-M2-sburst-capdrop-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9385; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.77, '30Hz': 0.98}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-M3-sburst-bgbursty-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9508; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.898, 1.1438, 1.1234), (1.05, 0.84, 0.8183, 1.0324, 0.9787), (1.3, 1.09, 1.0026, 1.1497, 0.6719), (1.15, 0.94, 0.7873, 1.0043, 0.9913), (1.3, 1.09, 1.046, 1.1798, 0.6113), (1.15, 0.94, 0.811, 1.0302, 1.0017), (1.05, 0.84, 0.7968, 1.007, 0.9606), (1.05, 0.84, 0.8057, 1.0081, 0.9248), (1.05, 0.84, 0.782, 1.0023, 1.0066), (1.15, 0.94, 0.8648, 1.064, 0.9103), (1.05, 0.84, 0.8275, 1.0458, 0.9972), (1.3, 1.09, 1.0813, 1.1857, 0.4773), (1.15, 0.94, 0.8281, 1.0399, 0.9676), (1.3, 1.09, 0.9725, 1.134, 0.738), (1.3, 1.09, 0.9572, 1.1354, 0.8142), (1.05, 0.84, 0.7316, 0.9393, 0.9489), (1.3, 1.09, 1.0492, 1.1284, 0.3619), (1.15, 0.94, 0.9115, 1.1024, 0.872)]; fq collisions None; errors []
- v3-M3-sburst-bgbursty-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9413; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.1243, 1.2061, 0.3697), (1.15, 0.94, 0.9137, 1.1293, 0.9745), (1.15, 0.94, 0.9613, 1.0951, 0.6046), (1.05, 0.84, 0.7866, 1.0056, 0.9896), (1.15, 0.94, 0.8699, 1.0831, 0.9634), (1.05, 0.84, 0.9123, 1.1089, 0.8885), (1.05, 0.84, 0.7345, 0.9566, 1.0035), (1.15, 0.94, 0.8812, 1.056, 0.7897), (1.3, 1.09, 1.0196, 1.1164, 0.4373), (1.3, 1.09, 0.954, 1.1574, 0.919), (1.3, 1.09, 0.946, 1.0787, 0.5996), (1.3, 1.09, 1.0031, 1.1118, 0.4912), (1.15, 0.94, 0.8064, 1.0147, 0.9412), (1.05, 0.84, 0.7998, 1.0154, 0.974), (1.05, 0.84, 0.8512, 1.0544, 0.918), (1.05, 0.84, 0.9695, 1.0946, 0.5651), (1.15, 0.94, 1.0349, 1.1406, 0.4773), (1.3, 1.09, 1.2113, 1.3214, 0.4974)]; fq collisions None; errors []
- v3-M3-sburst-bgbursty-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9448; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.898, 1.1019, 0.9337), (1.05, 0.84, 0.8183, 1.0309, 0.9742), (1.3, 1.09, 1.0026, 1.101, 0.4504), (1.15, 0.94, 0.7873, 1.0111, 1.0247), (1.3, 1.09, 1.046, 1.1592, 0.5182), (1.15, 0.94, 0.811, 1.0403, 1.0502), (1.05, 0.84, 0.7968, 1.0143, 0.996), (1.05, 0.84, 0.8057, 1.0308, 1.0309), (1.05, 0.84, 0.782, 1.012, 1.0532), (1.15, 0.94, 0.8648, 1.0696, 0.938), (1.05, 0.84, 0.8275, 1.0584, 1.0573), (1.3, 1.09, 1.0813, 1.1732, 0.4209), (1.15, 0.94, 0.8281, 1.0548, 1.0384), (1.3, 1.09, 0.9725, 1.1139, 0.6477), (1.3, 1.09, 0.9572, 1.1102, 0.7006), (1.05, 0.84, 0.7317, 0.9482, 0.9915), (1.3, 1.09, 1.0492, 1.1565, 0.4914), (1.15, 0.94, 0.9115, 1.1253, 0.979)]; fq collisions None; errors []
- v3-M3-sburst-bgbursty-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9421; ECN {}; oversize {}, offloads not off []; phase None; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.1243, 1.2446, 0.5463), (1.15, 0.94, 0.9137, 1.1085, 0.8842), (1.15, 0.94, 0.9613, 1.1417, 0.8184), (1.05, 0.84, 0.7866, 1.0134, 1.0291), (1.15, 0.94, 0.8699, 1.0414, 0.7781), (1.05, 0.84, 0.9123, 1.0854, 0.7854), (1.05, 0.84, 0.7346, 0.9685, 1.0617), (1.15, 0.94, 0.8813, 1.0642, 0.8303), (1.3, 1.09, 1.0196, 1.139, 0.5416), (1.3, 1.09, 0.954, 1.2095, 1.1594), (1.3, 1.09, 0.946, 1.1437, 0.8971), (1.3, 1.09, 1.0031, 1.1835, 0.8188), (1.15, 0.94, 0.8064, 1.0234, 0.9849), (1.05, 0.84, 0.7998, 1.0334, 1.0602), (1.05, 0.84, 0.8512, 1.1075, 1.1631), (1.05, 0.84, 0.9695, 1.1375, 0.7624), (1.15, 0.94, 1.0349, 1.191, 0.7082), (1.3, 1.09, 1.2113, 1.3021, 0.4121)]; fq collisions None; errors []
- v3-M3-sburst-bgmix-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9521; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 7.46, '30Hz': 1.16}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.8214, 1.0479, 1.042), (1.05, 0.84, 0.8087, 1.0326, 1.0298), (1.3, 1.09, 0.9182, 1.1334, 0.99), (1.15, 0.94, 0.8377, 1.0533, 0.9919), (1.3, 1.09, 0.8968, 1.0605, 0.7529), (1.15, 0.94, 0.8366, 1.0536, 0.9979), (1.05, 0.84, 0.8376, 1.0484, 0.9696), (1.05, 0.84, 0.8119, 1.0356, 1.0291), (1.05, 0.84, 0.7986, 1.0193, 1.0155), (1.15, 0.94, 0.8242, 1.0485, 1.0317), (1.05, 0.84, 0.8062, 1.0236, 1.0001), (1.3, 1.09, 0.9125, 1.1257, 0.9806), (1.15, 0.94, 0.9054, 1.1109, 0.9452), (1.3, 1.09, 0.8981, 1.0767, 0.8219), (1.3, 1.09, 0.9723, 1.1672, 0.8963), (1.05, 0.84, 0.8345, 1.0422, 0.9557), (1.3, 1.09, 0.9164, 1.1115, 0.8975), (1.15, 0.94, 0.8173, 1.0365, 1.0081)]; fq collisions None; errors []
- v3-M3-sburst-bgmix-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9381; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 15.48, '30Hz': 4.46}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 0.8855, 1.0844, 0.9138), (1.15, 0.94, 0.8512, 1.063, 0.9729), (1.15, 0.94, 0.824, 1.0487, 1.0323), (1.05, 0.84, 0.8192, 1.0452, 1.0384), (1.15, 0.94, 0.8573, 1.0644, 0.9513), (1.05, 0.84, 0.7995, 1.0179, 1.0036), (1.05, 0.84, 0.8025, 1.0255, 1.0246), (1.15, 0.94, 0.8324, 1.0449, 0.9761), (1.3, 1.09, 0.906, 1.0896, 0.8436), (1.3, 1.09, 0.9389, 1.1247, 0.854), (1.3, 1.09, 0.9197, 1.0717, 0.6983), (1.3, 1.09, 0.9153, 1.0888, 0.7974), (1.15, 0.94, 0.824, 1.0332, 0.9612), (1.05, 0.84, 0.8023, 1.0159, 0.9812), (1.05, 0.84, 0.8137, 1.0381, 1.0309), (1.05, 0.84, 0.8053, 1.0264, 1.0157), (1.15, 0.94, 0.8304, 1.0519, 1.0176), (1.3, 1.09, 0.9007, 1.0962, 0.8982)]; fq collisions None; errors []
- v3-M3-sburst-bgmix-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9519; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 6.13, '30Hz': 1.13}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.8381, 1.1141, 1.263), (1.05, 0.84, 0.8031, 1.0349, 1.0604), (1.3, 1.09, 1.002, 1.123, 0.5535), (1.15, 0.94, 0.8864, 1.0703, 0.8414), (1.3, 1.09, 0.9446, 1.1465, 0.9237), (1.15, 0.94, 0.8676, 1.0692, 0.9224), (1.05, 0.84, 0.8578, 1.0495, 0.8771), (1.05, 0.84, 0.8165, 1.0502, 1.0691), (1.05, 0.84, 0.8197, 1.0312, 0.9677), (1.15, 0.94, 0.8561, 1.073, 0.9923), (1.05, 0.84, 0.8205, 1.0483, 1.0419), (1.3, 1.09, 0.9475, 1.1254, 0.8139), (1.15, 0.94, 0.9281, 1.1029, 0.7997), (1.3, 1.09, 0.9757, 1.187, 0.9667), (1.3, 1.09, 1.0295, 1.1722, 0.653), (1.05, 0.84, 0.8661, 1.0494, 0.8383), (1.3, 1.09, 0.9967, 1.134, 0.6285), (1.15, 0.94, 0.8841, 1.0607, 0.8079)]; fq collisions None; errors []
- v3-M3-sburst-bgmix-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9397; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 19.35, '30Hz': 3.8}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 0.9384, 1.219, 1.2872), (1.15, 0.94, 0.8776, 1.1546, 1.2704), (1.15, 0.94, 0.848, 1.1013, 1.1622), (1.05, 0.84, 0.8069, 1.0423, 1.0798), (1.15, 0.94, 0.8898, 1.0623, 0.7913), (1.05, 0.84, 0.8121, 1.0355, 1.0249), (1.05, 0.84, 0.8156, 1.0487, 1.0692), (1.15, 0.94, 0.8725, 1.064, 0.8788), (1.3, 1.09, 0.9833, 1.1138, 0.5984), (1.3, 1.09, 0.9703, 1.2152, 1.1235), (1.3, 1.09, 0.9782, 1.1199, 0.6499), (1.3, 1.09, 0.9751, 1.1348, 0.7326), (1.15, 0.94, 0.8639, 1.0781, 0.9826), (1.05, 0.84, 0.8134, 1.021, 0.9524), (1.05, 0.84, 0.8083, 1.0412, 1.0685), (1.05, 0.84, 0.8095, 1.0437, 1.0741), (1.15, 0.94, 0.8888, 1.1052, 0.9927), (1.3, 1.09, 0.9718, 1.1193, 0.6767)]; fq collisions None; errors []
- v3-M4-sburst-rttwide-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9493; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.59, '30Hz': 1.45}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1249, 0.851), (1.05, 0.84, 0.8482, 1.0628, 0.9824), (1.3, 1.09, 1.0808, 1.2533, 0.7897), (1.15, 0.94, 0.9408, 1.1047, 0.7505), (1.3, 1.09, 1.0827, 1.1568, 0.3392), (1.15, 0.94, 0.9308, 1.1032, 0.7894), (1.05, 0.84, 0.8453, 1.0533, 0.9526), (1.05, 0.84, 0.8352, 1.0682, 1.0667), (1.05, 0.84, 0.8421, 1.0767, 1.074), (1.15, 0.94, 0.9389, 1.1079, 0.7736), (1.05, 0.84, 0.838, 1.0525, 0.982), (1.3, 1.09, 1.0877, 1.1618, 0.3396), (1.15, 0.94, 0.9537, 1.1263, 0.79), (1.3, 1.09, 1.0928, 1.2057, 0.5172), (1.3, 1.09, 1.0806, 1.2038, 0.5638), (1.05, 0.84, 0.8349, 1.0421, 0.9489), (1.3, 1.09, 1.0883, 1.1613, 0.3341), (1.15, 0.94, 0.9348, 1.1323, 0.904)]; fq collisions None; errors []
- v3-M4-sburst-rttwide-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9071; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 0.99}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.2135, 0.5764), (1.15, 0.94, 0.9445, 1.1441, 0.9056), (1.15, 0.94, 0.9415, 1.1086, 0.7579), (1.05, 0.84, 0.8444, 1.0733, 1.0389), (1.15, 0.94, 0.9365, 1.1514, 0.9751), (1.05, 0.84, 0.8358, 1.0671, 1.0496), (1.05, 0.84, 0.8432, 1.0724, 1.0399), (1.15, 0.94, 0.9448, 1.1107, 0.7526), (1.3, 1.09, 1.0947, 1.1585, 0.2896), (1.3, 1.09, 1.0807, 1.1946, 0.5167), (1.3, 1.09, 1.0873, 1.1836, 0.4366), (1.3, 1.09, 1.0973, 1.1884, 0.4137), (1.15, 0.94, 0.9467, 1.0935, 0.6661), (1.05, 0.84, 0.8343, 1.0519, 0.9878), (1.05, 0.84, 0.8375, 1.0741, 1.0738), (1.05, 0.84, 0.8423, 1.0632, 1.0025), (1.15, 0.94, 0.9446, 1.0982, 0.6972), (1.3, 1.09, 1.0943, 1.1935, 0.4501)]; fq collisions None; errors []
- v3-M4-sburst-rttx05-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9492; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.5}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.162, 1.0209), (1.05, 0.84, 0.8482, 1.1257, 1.2708), (1.3, 1.09, 1.0808, 1.1911, 0.5049), (1.15, 0.94, 0.9408, 1.1375, 0.9007), (1.3, 1.09, 1.0827, 1.215, 0.6055), (1.15, 0.94, 0.9308, 1.1319, 0.921), (1.05, 0.84, 0.8453, 1.0772, 1.0621), (1.05, 0.84, 0.8352, 1.0983, 1.2047), (1.05, 0.84, 0.8421, 1.0868, 1.1202), (1.15, 0.94, 0.9389, 1.1619, 1.0211), (1.05, 0.84, 0.838, 1.0976, 1.1887), (1.3, 1.09, 1.0877, 1.2318, 0.66), (1.15, 0.94, 0.9537, 1.2101, 1.1739), (1.3, 1.09, 1.0928, 1.2235, 0.5987), (1.3, 1.09, 1.0806, 1.2122, 0.6025), (1.05, 0.84, 0.8348, 1.0465, 0.9693), (1.3, 1.09, 1.0883, 1.2201, 0.6035), (1.15, 0.94, 0.9348, 1.1573, 1.0188)]; fq collisions None; errors []
- v3-M4-sburst-rttx05-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9128; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.0}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.2387, 0.6982), (1.15, 0.94, 0.9445, 1.1536, 0.9594), (1.15, 0.94, 0.9415, 1.1225, 0.8302), (1.05, 0.84, 0.8444, 1.112, 1.2278), (1.15, 0.94, 0.9365, 1.1487, 0.9734), (1.05, 0.84, 0.8358, 1.0774, 1.1084), (1.05, 0.84, 0.8432, 1.1054, 1.2026), (1.15, 0.94, 0.9448, 1.156, 0.9689), (1.3, 1.09, 1.0947, 1.1887, 0.4314), (1.3, 1.09, 1.0807, 1.229, 0.6801), (1.3, 1.09, 1.0873, 1.1961, 0.4987), (1.3, 1.09, 1.0973, 1.225, 0.586), (1.15, 0.94, 0.9467, 1.1806, 1.073), (1.05, 0.84, 0.8343, 1.0872, 1.1603), (1.05, 0.84, 0.8375, 1.1044, 1.2243), (1.05, 0.84, 0.8423, 1.0799, 1.0899), (1.15, 0.94, 0.9446, 1.1672, 1.0212), (1.3, 1.09, 1.0943, 1.2196, 0.5747)]; fq collisions None; errors []
- v3-M4-sburst-rttx4-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9505; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.51}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1236, 0.8367), (1.05, 0.84, 0.8482, 1.0773, 1.0386), (1.3, 1.09, 1.0808, 1.2359, 0.7029), (1.15, 0.94, 0.9408, 1.1169, 0.7982), (1.3, 1.09, 1.0827, 1.1758, 0.4218), (1.15, 0.94, 0.9308, 1.1441, 0.9668), (1.05, 0.84, 0.8453, 1.0552, 0.9517), (1.05, 0.84, 0.8352, 1.0683, 1.0567), (1.05, 0.84, 0.8421, 1.0614, 0.9941), (1.15, 0.94, 0.9389, 1.092, 0.6941), (1.05, 0.84, 0.838, 1.0567, 0.9912), (1.3, 1.09, 1.0877, 1.2032, 0.5236), (1.15, 0.94, 0.9537, 1.1479, 0.8803), (1.3, 1.09, 1.0928, 1.1946, 0.4615), (1.3, 1.09, 1.0806, 1.2268, 0.6626), (1.05, 0.84, 0.8348, 1.0435, 0.9461), (1.3, 1.09, 1.0883, 1.1692, 0.367), (1.15, 0.94, 0.9348, 1.1127, 0.8066)]; fq collisions None; errors []
- v3-M4-sburst-rttx4-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9398; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.0}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1812, 0.4342), (1.15, 0.94, 0.9445, 1.1594, 0.9854), (1.15, 0.94, 0.9415, 1.1254, 0.8431), (1.05, 0.84, 0.8444, 1.0545, 0.9636), (1.15, 0.94, 0.9365, 1.1351, 0.911), (1.05, 0.84, 0.8358, 1.0516, 0.99), (1.05, 0.84, 0.8432, 1.0547, 0.9697), (1.15, 0.94, 0.9448, 1.1879, 1.1149), (1.3, 1.09, 1.0947, 1.1765, 0.3751), (1.3, 1.09, 1.0807, 1.2288, 0.6792), (1.3, 1.09, 1.0873, 1.1691, 0.3751), (1.3, 1.09, 1.0973, 1.2123, 0.5275), (1.15, 0.94, 0.9467, 1.1167, 0.7798), (1.05, 0.84, 0.8343, 1.0443, 0.9632), (1.05, 0.84, 0.8375, 1.0708, 1.07), (1.05, 0.84, 0.8423, 1.075, 1.0672), (1.15, 0.94, 0.9446, 1.0994, 0.7101), (1.3, 1.09, 1.0943, 1.2239, 0.5942)]; fq collisions None; errors []
- v3-M5-sburst-fps15-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9501; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.55}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.0981, 0.7229), (1.05, 0.84, 0.8482, 1.0504, 0.9185), (1.3, 1.09, 1.0808, 1.2266, 0.6626), (1.15, 0.94, 0.9408, 1.1414, 0.9117), (1.3, 1.09, 1.0827, 1.1827, 0.4542), (1.15, 0.94, 0.9308, 1.1413, 0.9567), (1.05, 0.84, 0.8453, 1.0667, 1.0062), (1.05, 0.84, 0.8352, 1.048, 0.9668), (1.05, 0.84, 0.8421, 1.0489, 0.9395), (1.15, 0.94, 0.9389, 1.0861, 0.669), (1.05, 0.84, 0.838, 1.0554, 0.9881), (1.3, 1.09, 1.0877, 1.1815, 0.4262), (1.15, 0.94, 0.9537, 1.1534, 0.9074), (1.3, 1.09, 1.0928, 1.1856, 0.4221), (1.3, 1.09, 1.0806, 1.2289, 0.6739), (1.05, 0.84, 0.8348, 1.0438, 0.9494), (1.3, 1.09, 1.0883, 1.1764, 0.4002), (1.15, 0.94, 0.9348, 1.0901, 0.7058)]; fq collisions None; errors []
- v3-M5-sburst-fps15-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.9291; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 0.97}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1815, 0.433), (1.15, 0.94, 0.9445, 1.148, 0.9275), (1.15, 0.94, 0.9415, 1.0656, 0.5655), (1.05, 0.84, 0.8444, 1.047, 0.9237), (1.15, 0.94, 0.9365, 1.1434, 0.9431), (1.05, 0.84, 0.8358, 1.0672, 1.0553), (1.05, 0.84, 0.8432, 1.0539, 0.9603), (1.15, 0.94, 0.9448, 1.1244, 0.8188), (1.3, 1.09, 1.0947, 1.1714, 0.35), (1.3, 1.09, 1.0807, 1.2257, 0.6609), (1.3, 1.09, 1.0873, 1.1607, 0.3342), (1.3, 1.09, 1.0972, 1.1784, 0.3702), (1.15, 0.94, 0.9467, 1.1394, 0.8786), (1.05, 0.84, 0.8343, 1.0418, 0.9461), (1.05, 0.84, 0.8375, 1.0482, 0.9605), (1.05, 0.84, 0.8423, 1.0407, 0.9045), (1.15, 0.94, 0.9446, 1.0815, 0.624), (1.3, 1.09, 1.0943, 1.2466, 0.694)]; fq collisions None; errors []
- v3-M5-sburst-fps15-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9493; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.45}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1231, 0.8407), (1.05, 0.84, 0.8482, 1.0926, 1.1159), (1.3, 1.09, 1.0808, 1.2276, 0.6701), (1.15, 0.94, 0.9408, 1.1114, 0.779), (1.3, 1.09, 1.0827, 1.199, 0.5311), (1.15, 0.94, 0.9308, 1.155, 1.0237), (1.05, 0.84, 0.8453, 1.0566, 0.9649), (1.05, 0.84, 0.8352, 1.0924, 1.1744), (1.05, 0.84, 0.8421, 1.0459, 0.9303), (1.15, 0.94, 0.9389, 1.1262, 0.8554), (1.05, 0.84, 0.838, 1.0923, 1.1613), (1.3, 1.09, 1.0877, 1.171, 0.3805), (1.15, 0.94, 0.9537, 1.2293, 1.2583), (1.3, 1.09, 1.0928, 1.1998, 0.4889), (1.3, 1.09, 1.0806, 1.2718, 0.8732), (1.05, 0.84, 0.8348, 1.0537, 0.9995), (1.3, 1.09, 1.0883, 1.1868, 0.4499), (1.15, 0.94, 0.9348, 1.0899, 0.708)]; fq collisions None; errors []
- v3-M5-sburst-fps15-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9359; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.77, '30Hz': 1.0}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.23, 0.6578), (1.15, 0.94, 0.9445, 1.2252, 1.2871), (1.15, 0.94, 0.9415, 1.1493, 0.9529), (1.05, 0.84, 0.8444, 1.0775, 1.0688), (1.15, 0.94, 0.9365, 1.223, 1.3136), (1.05, 0.84, 0.8358, 1.0847, 1.1416), (1.05, 0.84, 0.8432, 1.0675, 1.0285), (1.15, 0.94, 0.9448, 1.1282, 0.8408), (1.3, 1.09, 1.0947, 1.1993, 0.4797), (1.3, 1.09, 1.0807, 1.2087, 0.5869), (1.3, 1.09, 1.0873, 1.1638, 0.3506), (1.3, 1.09, 1.0973, 1.1725, 0.3451), (1.15, 0.94, 0.9467, 1.1825, 1.0813), (1.05, 0.84, 0.8343, 1.1008, 1.2223), (1.05, 0.84, 0.8375, 1.0779, 1.1022), (1.05, 0.84, 0.8423, 1.0857, 1.1162), (1.15, 0.94, 0.9446, 1.1364, 0.8793), (1.3, 1.09, 1.0943, 1.2355, 0.6474)]; fq collisions None; errors []
- v3-M5-sburst-fps60-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9431; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.59, '30Hz': 1.51}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.0882, 0.6685), (1.05, 0.84, 0.8482, 1.07, 0.9936), (1.3, 1.09, 1.0808, 1.2208, 0.6272), (1.15, 0.94, 0.9408, 1.1102, 0.7593), (1.3, 1.09, 1.0827, 1.1829, 0.4488), (1.15, 0.94, 0.9308, 1.1384, 0.93), (1.05, 0.84, 0.8453, 1.065, 0.9848), (1.05, 0.84, 0.8352, 1.0464, 0.9463), (1.05, 0.84, 0.8421, 1.0475, 0.9203), (1.15, 0.94, 0.9389, 1.0958, 0.703), (1.05, 0.84, 0.838, 1.0515, 0.9568), (1.3, 1.09, 1.0877, 1.1924, 0.4693), (1.15, 0.94, 0.9537, 1.1618, 0.9324), (1.3, 1.09, 1.0928, 1.1774, 0.3792), (1.3, 1.09, 1.0806, 1.2571, 0.791), (1.05, 0.84, 0.8348, 1.0489, 0.9592), (1.3, 1.09, 1.0883, 1.1582, 0.3134), (1.15, 0.94, 0.9348, 1.0685, 0.599)]; fq collisions None; errors []
- v3-M5-sburst-fps60-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9382; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.77, '30Hz': 0.96}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.2027, 0.5282), (1.15, 0.94, 0.9445, 1.1531, 0.9484), (1.15, 0.94, 0.9415, 1.0857, 0.6555), (1.05, 0.84, 0.8444, 1.0651, 1.0035), (1.15, 0.94, 0.9365, 1.1211, 0.8392), (1.05, 0.84, 0.8358, 1.0365, 0.9125), (1.05, 0.84, 0.8432, 1.0596, 0.984), (1.15, 0.94, 0.9448, 1.1061, 0.7331), (1.3, 1.09, 1.0947, 1.1566, 0.2814), (1.3, 1.09, 1.0807, 1.2165, 0.6174), (1.3, 1.09, 1.0873, 1.1693, 0.3727), (1.3, 1.09, 1.0972, 1.2002, 0.4681), (1.15, 0.94, 0.9467, 1.128, 0.8243), (1.05, 0.84, 0.8343, 1.0521, 0.9906), (1.05, 0.84, 0.8375, 1.0543, 0.9857), (1.05, 0.84, 0.8423, 1.0511, 0.9496), (1.15, 0.94, 0.9446, 1.0853, 0.6398), (1.3, 1.09, 1.0944, 1.2498, 0.7066)]; fq collisions None; errors []
- v3-M5-sburst-fps60-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.944; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.41}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1511, 0.953), (1.05, 0.84, 0.8482, 1.0749, 1.0183), (1.3, 1.09, 1.0808, 1.2407, 0.7185), (1.15, 0.94, 0.9408, 1.1263, 0.8335), (1.3, 1.09, 1.0827, 1.1876, 0.4712), (1.15, 0.94, 0.9308, 1.1167, 0.8352), (1.05, 0.84, 0.8453, 1.0671, 0.9967), (1.05, 0.84, 0.8352, 1.0874, 1.1329), (1.05, 0.84, 0.8421, 1.0846, 1.0892), (1.15, 0.94, 0.9389, 1.1164, 0.7976), (1.05, 0.84, 0.838, 1.0704, 1.0439), (1.3, 1.09, 1.0877, 1.1987, 0.4989), (1.15, 0.94, 0.9537, 1.1501, 0.8823), (1.3, 1.09, 1.0928, 1.2293, 0.6135), (1.3, 1.09, 1.0806, 1.1995, 0.534), (1.05, 0.84, 0.8348, 1.0543, 0.9857), (1.3, 1.09, 1.0883, 1.1754, 0.3915), (1.15, 0.94, 0.9348, 1.1572, 0.9992)]; fq collisions None; errors []
- v3-M5-sburst-fps60-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9274; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.76, '30Hz': 1.0}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1822, 0.4348), (1.15, 0.94, 0.9445, 1.1259, 0.8246), (1.15, 0.94, 0.9415, 1.1341, 0.8751), (1.05, 0.84, 0.8444, 1.0712, 1.0309), (1.15, 0.94, 0.9365, 1.107, 0.7751), (1.05, 0.84, 0.8358, 1.0508, 0.9776), (1.05, 0.84, 0.8432, 1.0613, 0.9911), (1.15, 0.94, 0.9448, 1.1514, 0.9388), (1.3, 1.09, 1.0947, 1.1837, 0.4045), (1.3, 1.09, 1.0807, 1.1865, 0.4809), (1.3, 1.09, 1.0873, 1.1724, 0.3867), (1.3, 1.09, 1.0973, 1.2077, 0.5022), (1.15, 0.94, 0.9467, 1.1336, 0.8493), (1.05, 0.84, 0.8343, 1.0489, 0.9758), (1.05, 0.84, 0.8375, 1.1021, 1.2029), (1.05, 0.84, 0.8423, 1.0726, 1.0469), (1.15, 0.94, 0.9446, 1.1321, 0.8522), (1.3, 1.09, 1.0943, 1.2026, 0.4921)]; fq collisions None; errors []
- v3-M6-calm-stag-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9534; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.56, '30Hz': 2.22}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-M6-calm-stag-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9514; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.16, '30Hz': 1.62}}; surge (u, planned non-video, measured, total, video / calm) []; fq collisions None; errors []
- v3-M6-sburst-stag-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9502; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.6, '30Hz': 1.52}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.939, 1.1155, 0.8011), (1.05, 0.84, 0.8482, 1.0955, 1.122), (1.3, 1.09, 1.0808, 1.1943, 0.5151), (1.15, 0.94, 0.9408, 1.1119, 0.7767), (1.3, 1.09, 1.0827, 1.1791, 0.4375), (1.15, 0.94, 0.9308, 1.1087, 0.8072), (1.05, 0.84, 0.8453, 1.0613, 0.9805), (1.05, 0.84, 0.8352, 1.087, 1.1427), (1.05, 0.84, 0.8421, 1.062, 0.9977), (1.15, 0.94, 0.9389, 1.1107, 0.7796), (1.05, 0.84, 0.838, 1.0671, 1.0395), (1.3, 1.09, 1.0877, 1.1767, 0.4041), (1.15, 0.94, 0.9537, 1.1988, 1.112), (1.3, 1.09, 1.0928, 1.1833, 0.4108), (1.3, 1.09, 1.0806, 1.2002, 0.5425), (1.05, 0.84, 0.8348, 1.0576, 1.011), (1.3, 1.09, 1.0883, 1.1811, 0.4212), (1.15, 0.94, 0.9348, 1.1285, 0.879)]; fq collisions None; errors []
- v3-M6-sburst-stag-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 2}; unmatched total 2 (targets 2); cpu idle min 0.9185; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 1.77, '30Hz': 0.99}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0865, 1.1765, 0.4105), (1.15, 0.94, 0.9445, 1.1352, 0.8701), (1.15, 0.94, 0.9415, 1.1259, 0.8414), (1.05, 0.84, 0.8444, 1.087, 1.1073), (1.15, 0.94, 0.9365, 1.1177, 0.8271), (1.05, 0.84, 0.8358, 1.0602, 1.0245), (1.05, 0.84, 0.8432, 1.0619, 0.9981), (1.15, 0.94, 0.9448, 1.0936, 0.6791), (1.3, 1.09, 1.0947, 1.2033, 0.4958), (1.3, 1.09, 1.0807, 1.1992, 0.5406), (1.3, 1.09, 1.0873, 1.1676, 0.3664), (1.3, 1.09, 1.0973, 1.2137, 0.5313), (1.15, 0.94, 0.9467, 1.1132, 0.7597), (1.05, 0.84, 0.8343, 1.0595, 1.0278), (1.05, 0.84, 0.8375, 1.0959, 1.1795), (1.05, 0.84, 0.8423, 1.0619, 1.0024), (1.15, 0.94, 0.9446, 1.1421, 0.9014), (1.3, 1.09, 1.0943, 1.2027, 0.4944)]; fq collisions None; errors []
- v3-M7-hhier-noroot-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.9039; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 4.41, '30Hz': 1.43}, 'b': {'1Hz': 1.53, '30Hz': 1.41}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0866, 1.2018, 0.5234), (1.3, 1.09, 1.0956, 1.1744, 0.3584), (1.15, 0.94, 0.9433, 1.219, 1.2516), (1.15, 0.94, 0.9394, 1.1132, 0.7909), (1.3, 1.09, 1.0877, 1.2038, 0.527), (1.3, 1.09, 1.0928, 1.1902, 0.4433), (1.15, 0.94, 0.93, 1.0879, 0.7188), (1.05, 0.84, 0.83, 1.0578, 1.0368), (1.3, 1.09, 1.0716, 1.2314, 0.7251), (1.3, 1.09, 1.0856, 1.2196, 0.6099), (1.3, 1.09, 1.0844, 1.2238, 0.6326), (1.3, 1.09, 1.0907, 1.2098, 0.5418), (1.15, 0.94, 0.9427, 1.1381, 0.8871), (1.15, 0.94, 0.9475, 1.1559, 0.9484), (1.3, 1.09, 1.0894, 1.2132, 0.5621), (1.05, 0.84, 0.8287, 1.0664, 1.0791), (1.15, 0.94, 0.9395, 1.1182, 0.8113), (1.05, 0.84, 0.8389, 1.0917, 1.1504), (1.15, 0.94, 0.9343, 1.1451, 0.9569), (1.15, 0.94, 0.9369, 1.1547, 0.9913), (1.15, 0.94, 0.9429, 1.0756, 0.6027), (1.15, 0.94, 0.9423, 1.1319, 0.863), (1.3, 1.09, 1.083, 1.202, 0.5404), (1.3, 1.09, 1.0965, 1.1865, 0.4097), (1.3, 1.09, 1.0582, 1.1896, 0.5964), (1.3, 1.09, 1.0934, 1.2263, 0.6049), (1.15, 0.94, 0.9413, 1.1107, 0.7692), (1.05, 0.84, 0.8437, 1.0696, 1.0281), (1.15, 0.94, 0.9422, 1.106, 0.7434), (1.15, 0.94, 0.943, 1.115, 0.7828), (1.05, 0.84, 0.8502, 1.0429, 0.875), (1.3, 1.09, 1.0767, 1.1906, 0.5185), (1.15, 0.94, 0.9432, 1.1367, 0.8784), (1.15, 0.94, 0.9473, 1.1644, 0.9884), (1.15, 0.94, 0.9286, 1.108, 0.8148), (1.15, 0.94, 0.9333, 1.0732, 0.6369), (1.3, 1.09, 1.0928, 1.1979, 0.4774), (1.3, 1.09, 1.0926, 1.2349, 0.6478), (1.15, 0.94, 0.9451, 1.2002, 1.1612), (1.15, 0.94, 0.9424, 1.1327, 0.866), (1.3, 1.09, 1.0875, 1.183, 0.4347), (1.3, 1.09, 1.0809, 1.1763, 0.434), (1.15, 0.94, 0.9451, 1.1229, 0.8072), (1.15, 0.94, 0.9534, 1.1359, 0.8306), (1.3, 1.09, 1.0904, 1.184, 0.4251), (1.3, 1.09, 1.0869, 1.1897, 0.4682), (1.15, 0.94, 0.9358, 1.0781, 0.6461), (1.3, 1.09, 1.0965, 1.2119, 0.524), (1.3, 1.09, 1.0762, 1.227, 0.6845), (1.15, 0.94, 0.941, 1.1313, 0.8638), (1.15, 0.94, 0.9417, 1.1371, 0.8893), (1.3, 1.09, 1.0849, 1.1794, 0.429), (1.3, 1.09, 1.0911, 1.1773, 0.3924), (1.05, 0.84, 0.837, 1.0975, 1.1827)]; fq collisions None; errors []
- v3-M7-hhier-noroot-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8899; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 3.4, '30Hz': 1.49}, 'b': {'1Hz': 1.05, '30Hz': 1.21}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0945, 1.1976, 0.4707), (1.3, 1.09, 1.0911, 1.1849, 0.4251), (1.15, 0.94, 0.9446, 1.1351, 0.8643), (1.15, 0.94, 0.9465, 1.1555, 0.9546), (1.15, 0.94, 0.9448, 1.1247, 0.816), (1.3, 1.09, 1.1021, 1.2046, 0.4681), (1.3, 1.09, 1.0853, 1.2414, 0.7131), (1.3, 1.09, 1.0755, 1.1662, 0.4113), (1.15, 0.94, 0.94, 1.1661, 1.0333), (1.3, 1.09, 1.086, 1.1962, 0.5035), (1.3, 1.09, 1.0821, 1.2179, 0.6159), (1.05, 0.84, 0.8616, 1.0931, 1.0573), (1.3, 1.09, 1.0897, 1.2288, 0.6357), (1.3, 1.09, 1.0882, 1.2751, 0.8479), (1.15, 0.94, 0.937, 1.1969, 1.1872), (1.15, 0.94, 0.9495, 1.2291, 1.268), (1.15, 0.94, 0.9467, 1.1678, 1.0025), (1.15, 0.94, 0.941, 1.0999, 0.7262), (1.15, 0.94, 0.9355, 1.1301, 0.8828), (1.3, 1.09, 1.092, 1.1927, 0.4597), (1.3, 1.09, 1.103, 1.1914, 0.401), (1.15, 0.94, 0.9466, 1.1523, 0.9397), (1.15, 0.94, 0.9365, 1.1146, 0.8077), (1.3, 1.09, 1.0937, 1.22, 0.573), (1.15, 0.94, 0.9303, 1.1968, 1.2086), (1.05, 0.84, 0.8418, 1.0935, 1.1417), (1.3, 1.09, 1.0919, 1.1861, 0.4308), (1.3, 1.09, 1.0915, 1.2275, 0.6169), (1.3, 1.09, 1.0888, 1.1824, 0.4249), (1.3, 1.09, 1.0905, 1.1781, 0.4002), (1.15, 0.94, 0.9337, 1.1871, 1.1577), (1.3, 1.09, 1.1074, 1.2159, 0.4922), (1.15, 0.94, 0.9414, 1.1438, 0.9248), (1.15, 0.94, 0.9401, 1.1126, 0.7823), (1.15, 0.94, 0.9546, 1.1206, 0.7582), (1.15, 0.94, 0.937, 1.1164, 0.8137), (1.3, 1.09, 1.0923, 1.1867, 0.4311), (1.3, 1.09, 1.0916, 1.1764, 0.3847), (1.05, 0.84, 0.8374, 1.0968, 1.1854), (1.05, 0.84, 0.8378, 1.0627, 1.0195), (1.15, 0.94, 0.9456, 1.1273, 0.8298), (1.15, 0.94, 0.9418, 1.1675, 1.0239), (1.3, 1.09, 1.097, 1.2235, 0.5779), (1.05, 0.84, 0.8398, 1.0935, 1.1505), (1.15, 0.94, 0.9423, 1.1503, 0.95), (1.15, 0.94, 0.9419, 1.1216, 0.8148), (1.05, 0.84, 0.8341, 1.0601, 1.0326), (1.15, 0.94, 0.9386, 1.1422, 0.9299), (1.3, 1.09, 1.1019, 1.1964, 0.4314), (1.3, 1.09, 1.0662, 1.1781, 0.5074), (1.3, 1.09, 1.0795, 1.1887, 0.4986), (1.3, 1.09, 1.0791, 1.1697, 0.4107), (1.15, 0.94, 0.935, 1.1331, 0.9053), (1.15, 0.94, 0.9275, 1.1124, 0.8387)]; fq collisions None; errors []
- v3-M8-hhier-mixab-mixab-r1: lost 0; target egresses failing ['r1-eth2']; recursion misses {'pub': 0, 'r1': 1, 'r2': 0}; unmatched total 1 (targets 1); cpu idle min 0.8787; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.32, '30Hz': 2.65}, 'b': {'1Hz': 1.89, '30Hz': 1.69}, 'up': {'1Hz': 6.4, '30Hz': 2.01}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9368, 1.202, 1.206), (1.15, 0.94, 0.9467, 1.145, 0.8908), (1.3, 1.09, 1.0898, 1.3344, 1.1125), (1.15, 0.94, 0.939, 1.0457, 0.4852), (1.15, 0.94, 0.9388, 1.1141, 0.7923), (1.15, 0.94, 0.9422, 1.1549, 0.9675), (1.15, 0.94, 0.9361, 1.0879, 0.6817), (1.3, 1.09, 1.0828, 1.2139, 0.5887), (1.15, 0.94, 0.9463, 1.1275, 0.819), (1.3, 1.09, 1.0899, 1.2924, 0.921), (1.3, 1.09, 1.0871, 1.2238, 0.6138), (1.3, 1.09, 1.0824, 1.2953, 0.9686), (1.05, 0.84, 0.8393, 1.0199, 0.8112), (1.05, 0.84, 0.8398, 1.0877, 1.1272), (1.15, 0.94, 0.9457, 1.0983, 0.6856), (1.15, 0.94, 0.9417, 1.128, 0.8417), (1.3, 1.09, 1.0838, 1.2184, 0.6121), (1.3, 1.09, 1.0779, 1.2254, 0.6625), (1.3, 1.09, 1.0786, 1.2178, 0.6254), (1.05, 0.84, 0.8365, 1.054, 0.983), (1.15, 0.94, 0.945, 1.0962, 0.6793), (1.15, 0.94, 0.934, 1.1282, 0.8776), (1.15, 0.94, 0.9373, 1.2083, 1.2326), (1.15, 0.94, 0.9397, 1.092, 0.684), (1.05, 0.84, 0.8371, 1.02, 0.8214), (1.15, 0.94, 0.9411, 1.1559, 0.9771), (1.15, 0.94, 0.9469, 1.1522, 0.9339), (1.15, 0.94, 0.9559, 1.1126, 0.7039), (1.3, 1.09, 1.0878, 1.2318, 0.6548), (1.3, 1.09, 1.0994, 1.2386, 0.6252), (1.3, 1.09, 1.0915, 1.3634, 1.237), (1.15, 0.94, 0.9394, 1.149, 0.9537), (1.3, 1.09, 1.0956, 1.1277, 0.146), (1.3, 1.09, 1.0932, 1.1661, 0.3292), (1.05, 0.84, 0.8293, 1.0646, 1.0706), (1.15, 0.94, 0.9302, 1.0884, 0.7104), (1.3, 1.09, 1.0785, 1.2597, 0.8244), (1.3, 1.09, 1.0826, 1.2328, 0.6744), (1.05, 0.84, 0.8435, 1.0853, 1.0997), (1.3, 1.09, 1.1142, 1.1614, 0.2149), (1.3, 1.09, 1.0818, 1.1775, 0.4322), (1.3, 1.09, 1.0882, 1.2403, 0.6918), (1.3, 1.09, 1.0878, 1.2366, 0.6682), (1.3, 1.09, 1.092, 1.1937, 0.4596), (1.15, 0.94, 0.9373, 1.0428, 0.4799), (1.15, 0.94, 0.9385, 1.1207, 0.8233), (1.05, 0.84, 0.8429, 1.0197, 0.7941), (1.15, 0.94, 0.9518, 1.1254, 0.7893), (1.05, 0.84, 0.8389, 1.0604, 1.0008), (1.3, 1.09, 1.0958, 1.3247, 1.0409), (1.3, 1.09, 1.0916, 1.234, 0.6392), (1.15, 0.94, 0.935, 1.1377, 0.922), (1.15, 0.94, 0.9547, 1.1185, 0.7359), (1.3, 1.09, 1.0908, 1.2301, 0.6338), (1.3, 1.09, 1.0867, 1.2304, 0.6454), (1.15, 0.94, 0.9393, 1.1616, 1.0109), (1.15, 0.94, 0.9308, 1.0892, 0.7114), (1.3, 1.09, 1.0933, 1.1352, 0.1907), (1.3, 1.09, 1.0866, 1.1608, 0.3354), (1.15, 0.94, 0.9422, 1.1578, 0.9804), (1.15, 0.94, 0.95, 1.1045, 0.6941), (1.15, 0.94, 0.946, 1.1645, 0.9938), (1.15, 0.94, 0.9377, 1.0868, 0.6694), (1.3, 1.09, 1.0983, 1.2361, 0.6269), (1.3, 1.09, 1.0838, 1.2331, 0.6704), (1.15, 0.94, 0.9436, 1.05, 0.4839), (1.15, 0.94, 0.9388, 1.1182, 0.8106), (1.3, 1.09, 1.0917, 1.1797, 0.3978), (1.3, 1.09, 1.0876, 1.2156, 0.5782), (1.3, 1.09, 1.0842, 1.281, 0.8947), (1.3, 1.09, 1.097, 1.2334, 0.6127), (1.3, 1.09, 1.0877, 1.226, 0.6212), (1.15, 0.94, 0.9486, 1.171, 1.0117), (1.15, 0.94, 0.9396, 1.0924, 0.6862), (1.05, 0.84, 0.8366, 1.0842, 1.1189)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r1-eth1': 'unverifiable (no skb hash in the trace)', 'r1-eth2': {'bg_packets': 6729223, 'in_pinned_class': 1043, 'flows': ['10.101.0.1:5247']}, 'r2-eth2': {'bg_packets': 3513921, 'in_pinned_class': 2343, 'flows': ['10.101.0.2:5206', '10.101.0.2:5220']}, 'r2-eth4': {'bg_packets': 2494535, 'in_pinned_class': 2925, 'flows': ['10.101.0.3:5211', '10.101.0.3:5216']}}; errors []
- v3-M8-hhier-mixab-mixab-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'r1': 0, 'r2': 0}; unmatched total 0 (targets 0); cpu idle min 0.8812; ECN {}; oversize {}, offloads not off []; phase {'a': {'1Hz': 2.01, '30Hz': 1.11}, 'b': {'1Hz': 0.86, '30Hz': 3.84}, 'up': {'1Hz': 2.07, '30Hz': 3.61}}; surge (u, planned non-video, measured, total, video / calm) [(1.15, 0.94, 0.9383, 1.1403, 0.9133), (1.3, 1.09, 1.0855, 1.2264, 0.6369), (1.3, 1.09, 1.0957, 1.2579, 0.7398), (1.3, 1.09, 1.0988, 1.2381, 0.6298), (1.15, 0.94, 0.9446, 1.1389, 0.8865), (1.15, 0.94, 0.9368, 1.0855, 0.6717), (1.15, 0.94, 0.9458, 1.1523, 0.9422), (1.15, 0.94, 0.9387, 1.0958, 0.7103), (1.3, 1.09, 1.0983, 1.2354, 0.6197), (1.3, 1.09, 1.0895, 1.1822, 0.4208), (1.3, 1.09, 1.0818, 1.2469, 0.7532), (1.3, 1.09, 1.1099, 1.2819, 0.7772), (1.15, 0.94, 0.935, 1.0732, 0.6307), (1.15, 0.94, 0.936, 1.1421, 0.9359), (1.15, 0.94, 0.9389, 1.1617, 1.0165), (1.3, 1.09, 1.0807, 1.3203, 1.0934), (1.3, 1.09, 1.091, 1.2431, 0.6872), (1.3, 1.09, 1.085, 1.2535, 0.7688), (1.15, 0.94, 0.9234, 1.1539, 1.052), (1.15, 0.94, 0.9277, 1.0925, 0.7449), (1.3, 1.09, 1.098, 1.2401, 0.6483), (1.3, 1.09, 1.0986, 1.2159, 0.5306), (1.15, 0.94, 0.9404, 1.1201, 0.8197), (1.15, 0.94, 0.9321, 1.0836, 0.6849), (1.3, 1.09, 1.0845, 1.2358, 0.69), (1.3, 1.09, 1.0808, 1.2249, 0.6514), (1.05, 0.84, 0.8292, 1.0541, 1.0262), (1.3, 1.09, 1.0875, 1.3617, 1.2509), (1.3, 1.09, 1.1039, 1.2404, 0.6169), (1.15, 0.94, 0.9301, 1.1666, 1.0788), (1.15, 0.94, 0.9465, 1.1032, 0.708), (1.3, 1.09, 1.0913, 1.1361, 0.2045), (1.3, 1.09, 1.0876, 1.1931, 0.4791), (1.05, 0.84, 0.8258, 1.0346, 0.9483), (1.15, 0.94, 0.9468, 1.1182, 0.7822), (1.15, 0.94, 0.949, 1.1105, 0.7297), (1.15, 0.94, 0.9419, 1.1553, 0.9686), (1.15, 0.94, 0.9389, 1.1692, 1.0507), (1.15, 0.94, 0.9384, 1.0896, 0.6833), (1.05, 0.84, 0.8394, 1.0915, 1.1449), (1.05, 0.84, 0.8463, 1.0302, 0.8314), (1.3, 1.09, 1.0925, 1.1865, 0.4268), (1.15, 0.94, 0.9435, 1.1553, 0.9665), (1.15, 0.94, 0.9395, 1.0911, 0.6853), (1.15, 0.94, 0.9294, 1.0336, 0.4752), (1.15, 0.94, 0.9445, 1.0857, 0.641), (1.15, 0.94, 0.9285, 1.1881, 1.1845), (1.3, 1.09, 1.0876, 1.1345, 0.2137), (1.3, 1.09, 1.09, 1.1894, 0.451), (1.3, 1.09, 1.0882, 1.2622, 0.7939), (1.3, 1.09, 1.0887, 1.2272, 0.6261), (1.3, 1.09, 1.088, 1.2119, 0.5654), (1.3, 1.09, 1.0985, 1.2328, 0.6069), (1.3, 1.09, 1.0815, 1.2443, 0.7428), (1.3, 1.09, 1.092, 1.2413, 0.6776), (1.3, 1.09, 1.0872, 1.2678, 0.8241), (1.3, 1.09, 1.0932, 1.2294, 0.6157), (1.15, 0.94, 0.9584, 1.2139, 1.1657), (1.15, 0.94, 0.9435, 1.111, 0.757), (1.15, 0.94, 0.9521, 1.0786, 0.5773), (1.15, 0.94, 0.9341, 1.1067, 0.7836), (1.15, 0.94, 0.9409, 1.1251, 0.8362), (1.05, 0.84, 0.8408, 1.0126, 0.7767), (1.05, 0.84, 0.8402, 1.0752, 1.0722), (1.15, 0.94, 0.9331, 1.1972, 1.2052), (1.15, 0.94, 0.9348, 1.1199, 0.8365), (1.05, 0.84, 0.8335, 1.0728, 1.0919), (1.05, 0.84, 0.8385, 1.0628, 1.0183), (1.3, 1.09, 1.0769, 1.2519, 0.7983), (1.3, 1.09, 1.0966, 1.2336, 0.6192), (1.15, 0.94, 0.9396, 1.1584, 0.9933), (1.15, 0.94, 0.9514, 1.1031, 0.6856), (1.3, 1.09, 1.0859, 1.1226, 0.1677), (1.3, 1.09, 1.0888, 1.1597, 0.3223), (1.05, 0.84, 0.839, 1.0462, 0.9364)]; fq collisions {'pub-eth0': 'unverifiable (no skb hash in the trace)', 'r1-eth1': 'unverifiable (no skb hash in the trace)', 'r1-eth2': {'bg_packets': 6534060, 'in_pinned_class': 484, 'flows': ['10.101.0.1:5240']}, 'r2-eth2': {'bg_packets': 3422330, 'in_pinned_class': 238777, 'flows': ['10.101.0.2:5202', '10.101.0.2:5214', '10.101.0.2:5221', '10.101.0.2:5241']}, 'r2-eth4': {'bg_packets': 2435448, 'in_pinned_class': 239123, 'flows': ['10.101.0.3:5203', '10.101.0.3:5225', '10.101.0.3:5232', '10.101.0.3:5247', '10.101.0.3:5262']}}; errors []
- v3-M9-sstress-s030u070-codel-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 1 (targets 0); cpu idle min 0.936; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 6.03, '30Hz': 1.75}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0931, 1.3967, 1.4171), (2.0, 1.79, 1.793, 1.847, 0.2521), (2.0, 1.79, 1.7964, 1.8289, 0.1516), (1.3, 1.09, 1.0507, 1.2355, 0.8626), (2.0, 1.79, 1.7878, 1.8485, 0.2829), (2.0, 1.79, 1.7616, 1.9829, 1.033), (1.3, 1.09, 1.0807, 1.2733, 0.8987), (1.3, 1.09, 1.0973, 1.316, 1.0209), (2.0, 1.79, 1.8113, 2.0114, 0.9338), (2.0, 1.79, 1.7248, 1.9183, 0.9031), (2.0, 1.79, 1.7874, 1.8175, 0.1402), (1.3, 1.09, 1.1047, 1.3083, 0.9505), (2.0, 1.79, 1.8266, 1.9876, 0.7514), (1.3, 1.09, 1.094, 1.355, 1.2182), (2.0, 1.79, 1.7717, 1.9408, 0.7893), (2.0, 1.79, 1.8104, 1.981, 0.7962)]; fq collisions None; errors []
- v3-M9-sstress-s030u070-codel-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9446; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.08, '30Hz': 2.17}}; surge (u, planned non-video, measured, total, video / calm) [(2.0, 1.79, 1.7505, 2.0567, 1.4173), (2.0, 1.79, 1.7973, 1.8275, 0.1396), (1.3, 1.09, 1.0951, 1.3351, 1.111), (2.0, 1.79, 1.7561, 1.9566, 0.9285), (2.0, 1.79, 1.7859, 1.8462, 0.2791), (2.0, 1.79, 1.785, 1.9729, 0.8698), (1.3, 1.09, 1.0673, 1.5076, 2.0383), (1.3, 1.09, 1.1059, 1.2945, 0.8729), (2.0, 1.79, 1.7766, 1.8371, 0.2803), (2.0, 1.79, 1.7459, 1.9534, 0.9602), (1.3, 1.09, 1.1297, 1.3201, 0.8814), (1.3, 1.09, 1.0811, 1.2781, 0.9119), (1.3, 1.09, 1.0619, 1.2958, 1.0826), (2.0, 1.79, 1.7397, 1.9211, 0.8396), (2.0, 1.79, 1.7732, 1.9534, 0.8344), (2.0, 1.79, 1.7662, 1.8016, 0.1638)]; fq collisions None; errors []
- v3-M9-sstress-s030u070-pfifo-r1: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.9418; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 6.03, '30Hz': 1.69}}; surge (u, planned non-video, measured, total, video / calm) [(1.3, 1.09, 1.0931, 1.3313, 1.1189), (2.0, 1.79, 1.793, 1.8659, 0.3422), (2.0, 1.79, 1.7965, 1.8262, 0.1399), (1.3, 1.09, 1.0507, 1.2183, 0.7872), (2.0, 1.79, 1.7878, 1.8284, 0.1905), (2.0, 1.79, 1.7616, 1.9447, 0.8598), (1.3, 1.09, 1.0807, 1.2268, 0.686), (1.3, 1.09, 1.0973, 1.2321, 0.6329), (2.0, 1.79, 1.8113, 1.9719, 0.7542), (2.0, 1.79, 1.7248, 1.8799, 0.7286), (2.0, 1.79, 1.7874, 1.817, 0.1388), (1.3, 1.09, 1.1047, 1.2555, 0.7085), (2.0, 1.79, 1.8266, 1.9242, 0.4584), (1.3, 1.09, 1.094, 1.3502, 1.2031), (2.0, 1.79, 1.7717, 1.8604, 0.4166), (2.0, 1.79, 1.8104, 1.8986, 0.4143)]; fq collisions None; errors []
- v3-M9-sstress-s030u070-pfifo-r2: lost 0; target egresses failing []; recursion misses {'pub': 0, 'router': 0}; unmatched total 0 (targets 0); cpu idle min 0.8551; ECN {}; oversize {}, offloads not off []; phase {'main': {'1Hz': 2.08, '30Hz': 2.08}}; surge (u, planned non-video, measured, total, video / calm) [(2.0, 1.79, 1.7505, 2.0065, 1.2265), (2.0, 1.79, 1.7973, 1.834, 0.1756), (1.3, 1.09, 1.0951, 1.3204, 1.0796), (2.0, 1.79, 1.7561, 1.9271, 0.8196), (2.0, 1.79, 1.7859, 1.8265, 0.1947), (2.0, 1.79, 1.785, 1.8737, 0.4249), (1.3, 1.09, 1.0673, 1.4097, 1.6407), (1.3, 1.09, 1.1059, 1.2946, 0.904), (2.0, 1.79, 1.7766, 1.8145, 0.1816), (2.0, 1.79, 1.7459, 2.018, 1.3036), (1.3, 1.09, 1.1297, 1.2851, 0.7444), (1.3, 1.09, 1.0811, 1.2966, 1.0329), (1.3, 1.09, 1.0619, 1.2569, 0.9343), (2.0, 1.79, 1.7397, 1.8181, 0.3757), (2.0, 1.79, 1.7732, 1.8612, 0.4216), (2.0, 1.79, 1.7662, 1.8021, 0.172)]; fq collisions None; errors []
