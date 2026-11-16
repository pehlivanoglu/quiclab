# Scenario catalog, suite v3 (measured)

Topologies, sizing, stimuli and the campaign matrix: reports/v3-suite/README.md and `scripts/v3_suite.py --plan-only` (per-egress C_e / BG_e table). This file adds the measured values.

## 5. Measured calm load and video share per router egress (scenario_catalog.calm_load), rep 1 / rep 2

| cell | egress | load r1 / r2 | video share r1 / r2 (QUIC bytes / router bytes) |
|---|---|---|---|
| C10-hindep-s030-codel | r1->r2 | 0.712 / 0.713 | 0.301 / 0.301 |
| C10-hindep-s030-codel | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C10-hindep-s030-codel | r2->switch-a | 0.711 / 0.712 | 0.3 / 0.299 |
| C10-hindep-s030-codel | r2->switch-b | 0.713 / 0.714 | 0.301 / 0.302 |
| C10-hindep-s030-fq_codel | r1->r2 | 0.713 / 0.714 | 0.302 / 0.302 |
| C10-hindep-s030-fq_codel | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.964 |
| C10-hindep-s030-fq_codel | r2->switch-a | 0.712 / 0.713 | 0.301 / 0.301 |
| C10-hindep-s030-fq_codel | r2->switch-b | 0.714 / 0.715 | 0.302 / 0.303 |
| C10-hindep-s030-pfifo | r1->r2 | 0.711 / 0.713 | 0.3 / 0.3 |
| C10-hindep-s030-pfifo | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C10-hindep-s030-pfifo | r2->switch-a | 0.711 / 0.712 | 0.3 / 0.3 |
| C10-hindep-s030-pfifo | r2->switch-b | 0.711 / 0.713 | 0.299 / 0.301 |
| C11-huneven-uneven-codel | r1->r2 | 0.037 / 0.036 | 0.962 / 0.963 |
| C11-huneven-uneven-codel | r1->sub-ctrl | 0.053 / 0.053 | 0.964 / 0.963 |
| C11-huneven-uneven-codel | r2->switch-a | 0.709 / 0.709 | 0.297 / 0.297 |
| C11-huneven-uneven-codel | r2->switch-b | 0.709 / 0.707 | 0.297 / 0.297 |
| C11-huneven-uneven-codel | r2->switch-c | 0.711 / 0.709 | 0.299 / 0.297 |
| C11-huneven-uneven-pfifo | r1->r2 | 0.037 / 0.036 | 0.963 / 0.963 |
| C11-huneven-uneven-pfifo | r1->sub-ctrl | 0.053 / 0.053 | 0.964 / 0.964 |
| C11-huneven-uneven-pfifo | r2->switch-a | 0.709 / 0.708 | 0.296 / 0.296 |
| C11-huneven-uneven-pfifo | r2->switch-b | 0.708 / 0.707 | 0.297 / 0.296 |
| C11-huneven-uneven-pfifo | r2->switch-c | 0.709 / 0.709 | 0.298 / 0.297 |
| C12-amixed-access-codel | ra->sub-a | 0.043 / 0.043 | 0.957 / 0.958 |
| C12-amixed-access-codel | rb->sub-b | 0.108 / 0.107 | 0.963 / 0.964 |
| C12-amixed-access-codel | rc->sub-c | 0.107 / 0.108 | 0.963 / 0.963 |
| C12-amixed-access-codel | rd->sub-d | 0.178 / 0.18 | 0.965 / 0.965 |
| C12-amixed-access-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C12-amixed-access-codel | router->switch | 0.691 / 0.693 | 0.281 / 0.283 |
| C12-amixed-access-fq_codel | ra->sub-a | 0.043 / 0.043 | 0.958 / 0.958 |
| C12-amixed-access-fq_codel | rb->sub-b | 0.107 / 0.106 | 0.963 / 0.964 |
| C12-amixed-access-fq_codel | rc->sub-c | 0.107 / 0.106 | 0.964 / 0.964 |
| C12-amixed-access-fq_codel | rd->sub-d | 0.18 / 0.182 | 0.965 / 0.965 |
| C12-amixed-access-fq_codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C12-amixed-access-fq_codel | router->switch | 0.691 / 0.693 | 0.282 / 0.282 |
| C12-amixed-access-pfifo | ra->sub-a | 0.043 / 0.043 | 0.957 / 0.958 |
| C12-amixed-access-pfifo | rb->sub-b | 0.108 / 0.106 | 0.964 / 0.963 |
| C12-amixed-access-pfifo | rc->sub-c | 0.107 / 0.106 | 0.965 / 0.964 |
| C12-amixed-access-pfifo | rd->sub-d | 0.177 / 0.177 | 0.965 / 0.966 |
| C12-amixed-access-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C12-amixed-access-pfifo | router->switch | 0.691 / 0.69 | 0.281 / 0.28 |
| C12-amixed-access-pie | ra->sub-a | 0.043 / 0.043 | 0.958 / 0.959 |
| C12-amixed-access-pie | rb->sub-b | 0.107 / 0.106 | 0.963 / 0.964 |
| C12-amixed-access-pie | rc->sub-c | 0.107 / 0.106 | 0.964 / 0.964 |
| C12-amixed-access-pie | rd->sub-d | 0.177 / 0.179 | 0.964 / 0.966 |
| C12-amixed-access-pie | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C12-amixed-access-pie | router->switch | 0.69 / 0.691 | 0.281 / 0.281 |
| C13-llong-s030-codel | r1->r2 | 0.712 / 0.711 | 0.301 / 0.3 |
| C13-llong-s030-codel | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| C13-llong-s030-codel | r2->switch-a | 0.712 / 0.714 | 0.301 / 0.3 |
| C13-llong-s030-codel | r2->switch-b | 0.711 / 0.711 | 0.302 / 0.298 |
| C13-llong-s030-pfifo | r1->r2 | 0.708 / 0.707 | 0.297 / 0.297 |
| C13-llong-s030-pfifo | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C13-llong-s030-pfifo | r2->switch-a | 0.709 / 0.709 | 0.299 / 0.295 |
| C13-llong-s030-pfifo | r2->switch-b | 0.705 / 0.709 | 0.297 / 0.297 |
| C14-rrev-rev-fq_codel | r0->r1 | 0.119 / 0.118 | 0.964 / 0.964 |
| C14-rrev-rev-fq_codel | r0->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C14-rrev-rev-fq_codel | r1->r0 | 0.026 / 0.026 | None / None |
| C14-rrev-rev-fq_codel | r1->switch | 0.71 / 0.709 | 0.299 / 0.298 |
| C14-rrev-rev-pfifo | r0->r1 | 0.118 / 0.118 | 0.964 / 0.964 |
| C14-rrev-rev-pfifo | r0->sub-ctrl | 0.053 / 0.053 | 0.961 / 0.963 |
| C14-rrev-rev-pfifo | r1->r0 | 0.026 / 0.026 | None / None |
| C14-rrev-rev-pfifo | r1->switch | 0.708 / 0.708 | 0.297 / 0.297 |
| C15-nloss-s030u070-codel | router->sub-ctrl | 0.053 / 0.054 | 0.962 / 0.963 |
| C15-nloss-s030u070-codel | router->switch | 0.704 / 0.708 | 0.297 / 0.295 |
| C15-nloss-s030u070-pfifo | router->sub-ctrl | 0.054 / 0.054 | 0.963 / 0.963 |
| C15-nloss-s030u070-pfifo | router->switch | 0.705 / 0.708 | 0.297 / 0.295 |
| C1a-calm-legacy-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-legacy-codel | router->switch | 0.669 / 0.667 | 0.964 / 0.964 |
| C1a-calm-legacy-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-legacy-pfifo | router->switch | 0.669 / 0.667 | 0.969 / 0.968 |
| C1a-calm-s010u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s010u070-codel | router->switch | 0.702 / 0.704 | 0.1 / 0.1 |
| C1a-calm-s010u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s010u070-pfifo | router->switch | 0.702 / 0.704 | 0.1 / 0.1 |
| C1a-calm-s010u085-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s010u085-codel | router->switch | 0.852 / 0.855 | 0.1 / 0.1 |
| C1a-calm-s010u085-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s010u085-pfifo | router->switch | 0.852 / 0.854 | 0.1 / 0.1 |
| C1a-calm-s030u050-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s030u050-codel | router->switch | 0.504 / 0.505 | 0.296 / 0.295 |
| C1a-calm-s030u050-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s030u050-pfifo | router->switch | 0.504 / 0.505 | 0.296 / 0.295 |
| C1a-calm-s030u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s030u070-codel | router->switch | 0.706 / 0.707 | 0.296 / 0.295 |
| C1a-calm-s030u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s030u070-pfifo | router->switch | 0.706 / 0.707 | 0.296 / 0.295 |
| C1a-calm-s030u085-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s030u085-codel | router->switch | 0.857 / 0.859 | 0.296 / 0.295 |
| C1a-calm-s030u085-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s030u085-pfifo | router->switch | 0.857 / 0.859 | 0.296 / 0.295 |
| C1a-calm-s065u050-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s065u050-codel | router->switch | 0.511 / 0.51 | 0.633 / 0.632 |
| C1a-calm-s065u050-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s065u050-pfifo | router->switch | 0.511 / 0.51 | 0.634 / 0.632 |
| C1a-calm-s065u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s065u070-codel | router->switch | 0.715 / 0.714 | 0.633 / 0.632 |
| C1a-calm-s065u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s065u070-pfifo | router->switch | 0.715 / 0.714 | 0.636 / 0.634 |
| C1a-calm-s065u085-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s065u085-codel | router->switch | 0.868 / 0.867 | 0.635 / 0.634 |
| C1a-calm-s065u085-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1a-calm-s065u085-pfifo | router->switch | 0.868 / 0.867 | 0.635 / 0.634 |
| C1b-calm-split4-pfifo | r1->r2 | 0.706 / 0.707 | 0.296 / 0.295 |
| C1b-calm-split4-pfifo | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1b-calm-split4-pfifo | r2->switch-a | 0.708 / 0.707 | 0.295 / 0.295 |
| C1b-calm-split4-pfifo | r2->switch-b | 0.707 / 0.707 | 0.296 / 0.295 |
| C1b-calm-tree16-pfifo | r0->r1 | 0.711 / 0.71 | 0.296 / 0.296 |
| C1b-calm-tree16-pfifo | r0->r2 | 0.71 / 0.71 | 0.297 / 0.296 |
| C1b-calm-tree16-pfifo | r1->switch-a | 0.71 / 0.711 | 0.297 / 0.296 |
| C1b-calm-tree16-pfifo | r1->switch-b | 0.709 / 0.71 | 0.297 / 0.297 |
| C1b-calm-tree16-pfifo | r2->switch-c | 0.712 / 0.71 | 0.296 / 0.296 |
| C1b-calm-tree16-pfifo | r2->switch-d | 0.709 / 0.708 | 0.297 / 0.297 |
| C1b-calm-tree16-pfifo | rr->r0 | 0.708 / 0.71 | 0.297 / 0.296 |
| C1b-calm-tree16-pfifo | rr->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1b-calm-uneven-pfifo | r1->r2 | 0.036 / 0.036 | 0.963 / 0.963 |
| C1b-calm-uneven-pfifo | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C1b-calm-uneven-pfifo | r2->switch-a | 0.705 / 0.707 | 0.295 / 0.294 |
| C1b-calm-uneven-pfifo | r2->switch-b | 0.709 / 0.707 | 0.295 / 0.295 |
| C1b-calm-uneven-pfifo | r2->switch-c | 0.707 / 0.708 | 0.296 / 0.296 |
| C2-sburst-s030u070-cake | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C2-sburst-s030u070-cake | router->switch | 0.706 / 0.706 | 0.296 / 0.296 |
| C2-sburst-s030u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C2-sburst-s030u070-codel | router->switch | 0.71 / 0.709 | 0.299 / 0.299 |
| C2-sburst-s030u070-fq_codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C2-sburst-s030u070-fq_codel | router->switch | 0.712 / 0.712 | 0.302 / 0.301 |
| C2-sburst-s030u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C2-sburst-s030u070-pfifo | router->switch | 0.709 / 0.709 | 0.298 / 0.298 |
| C2-sburst-s030u070-pie | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| C2-sburst-s030u070-pie | router->switch | 0.707 / 0.708 | 0.297 / 0.298 |
| C2-sburst-s030u070-red | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C2-sburst-s030u070-red | router->switch | 0.707 / 0.707 | 0.296 / 0.296 |
| C3a-sburst-s010u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C3a-sburst-s010u070-codel | router->switch | 0.703 / 0.705 | 0.1 / 0.101 |
| C3a-sburst-s010u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C3a-sburst-s010u070-pfifo | router->switch | 0.703 / 0.703 | 0.1 / 0.099 |
| C3a-sburst-s065u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C3a-sburst-s065u070-codel | router->switch | 0.721 / 0.723 | 0.638 / 0.637 |
| C3a-sburst-s065u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C3a-sburst-s065u070-pfifo | router->switch | 0.721 / 0.72 | 0.638 / 0.635 |
| C3b-sburst-legacy-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.962 / 0.963 |
| C3b-sburst-legacy-pfifo | router->switch | 0.677 / 0.678 | 0.964 / 0.963 |
| C4-sramp-s030u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.962 / 0.963 |
| C4-sramp-s030u070-codel | router->switch | 0.708 / 0.712 | 0.3 / 0.299 |
| C4-sramp-s030u070-fq_codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| C4-sramp-s030u070-fq_codel | router->switch | 0.71 / 0.717 | 0.302 / 0.303 |
| C4-sramp-s030u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C4-sramp-s030u070-pfifo | router->switch | 0.707 / 0.709 | 0.298 / 0.296 |
| C4-sramp-s030u070-pie | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C4-sramp-s030u070-pie | router->switch | 0.707 / 0.709 | 0.299 / 0.296 |
| C5-stcp-s030u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.964 |
| C5-stcp-s030u070-codel | router->switch | 0.706 / 0.707 | 0.296 / 0.295 |
| C5-stcp-s030u070-fq_codel | router->sub-ctrl | 0.053 / 0.053 | 0.962 / 0.963 |
| C5-stcp-s030u070-fq_codel | router->switch | 0.707 / 0.707 | 0.297 / 0.295 |
| C5-stcp-s030u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C5-stcp-s030u070-pfifo | router->switch | 0.707 / 0.707 | 0.297 / 0.295 |
| C5-stcp-s030u070-pie | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C5-stcp-s030u070-pie | router->switch | 0.706 / 0.707 | 0.296 / 0.296 |
| C6-sjoin-s030u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| C6-sjoin-s030u070-codel | router->switch | 0.705 / 0.707 | 0.296 / 0.295 |
| C6-sjoin-s030u070-fq_codel | router->sub-ctrl | 0.053 / 0.054 | 0.962 / 0.963 |
| C6-sjoin-s030u070-fq_codel | router->switch | 0.705 / 0.707 | 0.296 / 0.295 |
| C6-sjoin-s030u070-pfifo | router->sub-ctrl | 0.053 / 0.054 | 0.963 / 0.963 |
| C6-sjoin-s030u070-pfifo | router->switch | 0.705 / 0.707 | 0.296 / 0.295 |
| C7-hhier-s030-codel | r1->r2 | 0.711 / 0.71 | 0.3 / 0.299 |
| C7-hhier-s030-codel | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C7-hhier-s030-codel | r2->switch-a | 0.711 / 0.71 | 0.299 / 0.298 |
| C7-hhier-s030-codel | r2->switch-b | 0.712 / 0.711 | 0.301 / 0.3 |
| C7-hhier-s030-fq_codel | r1->r2 | 0.711 / 0.712 | 0.3 / 0.3 |
| C7-hhier-s030-fq_codel | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C7-hhier-s030-fq_codel | r2->switch-a | 0.712 / 0.711 | 0.3 / 0.299 |
| C7-hhier-s030-fq_codel | r2->switch-b | 0.712 / 0.712 | 0.301 / 0.301 |
| C7-hhier-s030-pfifo | r1->r2 | 0.71 / 0.709 | 0.299 / 0.298 |
| C7-hhier-s030-pfifo | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C7-hhier-s030-pfifo | r2->switch-a | 0.71 / 0.709 | 0.298 / 0.298 |
| C7-hhier-s030-pfifo | r2->switch-b | 0.711 / 0.709 | 0.299 / 0.298 |
| C7-hhier-s030-pie | r1->r2 | 0.709 / 0.709 | 0.298 / 0.297 |
| C7-hhier-s030-pie | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| C7-hhier-s030-pie | r2->switch-a | 0.709 / 0.708 | 0.297 / 0.297 |
| C7-hhier-s030-pie | r2->switch-b | 0.709 / 0.709 | 0.299 / 0.297 |
| C8-hhier-s065-pfifo | r1->r2 | 0.72 / 0.721 | 0.637 / 0.636 |
| C8-hhier-s065-pfifo | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C8-hhier-s065-pfifo | r2->switch-a | 0.721 / 0.72 | 0.636 / 0.636 |
| C8-hhier-s065-pfifo | r2->switch-b | 0.721 / 0.721 | 0.635 / 0.636 |
| C9-hdepth-tree16-codel | r0->r1 | 0.712 / 0.712 | 0.299 / 0.299 |
| C9-hdepth-tree16-codel | r0->r2 | 0.712 / 0.713 | 0.3 / 0.298 |
| C9-hdepth-tree16-codel | r1->switch-a | 0.712 / 0.714 | 0.299 / 0.299 |
| C9-hdepth-tree16-codel | r1->switch-b | 0.712 / 0.711 | 0.299 / 0.298 |
| C9-hdepth-tree16-codel | r2->switch-c | 0.714 / 0.714 | 0.3 / 0.299 |
| C9-hdepth-tree16-codel | r2->switch-d | 0.712 / 0.71 | 0.299 / 0.299 |
| C9-hdepth-tree16-codel | rr->r0 | 0.711 / 0.712 | 0.3 / 0.299 |
| C9-hdepth-tree16-codel | rr->sub-ctrl | 0.053 / 0.053 | 0.962 / 0.963 |
| C9-hdepth-tree16-fq_codel | r0->r1 | 0.71 / 0.71 | 0.298 / 0.297 |
| C9-hdepth-tree16-fq_codel | r0->r2 | 0.71 / 0.711 | 0.298 / 0.297 |
| C9-hdepth-tree16-fq_codel | r1->switch-a | 0.711 / 0.711 | 0.298 / 0.297 |
| C9-hdepth-tree16-fq_codel | r1->switch-b | 0.71 / 0.71 | 0.298 / 0.297 |
| C9-hdepth-tree16-fq_codel | r2->switch-c | 0.712 / 0.711 | 0.298 / 0.297 |
| C9-hdepth-tree16-fq_codel | r2->switch-d | 0.71 / 0.709 | 0.297 / 0.298 |
| C9-hdepth-tree16-fq_codel | rr->r0 | 0.709 / 0.71 | 0.298 / 0.297 |
| C9-hdepth-tree16-fq_codel | rr->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| C9-hdepth-tree16-pfifo | r0->r1 | 0.71 / 0.71 | 0.298 / 0.298 |
| C9-hdepth-tree16-pfifo | r0->r2 | 0.71 / 0.712 | 0.298 / 0.298 |
| C9-hdepth-tree16-pfifo | r1->switch-a | 0.711 / 0.712 | 0.298 / 0.298 |
| C9-hdepth-tree16-pfifo | r1->switch-b | 0.711 / 0.711 | 0.298 / 0.298 |
| C9-hdepth-tree16-pfifo | r2->switch-c | 0.712 / 0.712 | 0.298 / 0.298 |
| C9-hdepth-tree16-pfifo | r2->switch-d | 0.711 / 0.71 | 0.298 / 0.298 |
| C9-hdepth-tree16-pfifo | rr->r0 | 0.71 / 0.711 | 0.298 / 0.298 |
| C9-hdepth-tree16-pfifo | rr->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| G1-calm-legacy-pfifo | router->sub-ctrl | 0.053 / - | 0.963 / - |
| G1-calm-legacy-pfifo | router->switch | 0.669 / - | 0.968 / - |
| G1-calm-s030u070-pfifo | router->sub-ctrl | 0.053 / - | 0.963 / - |
| G1-calm-s030u070-pfifo | router->switch | 0.706 / - | 0.296 / - |
| G2-calm-access-pfifo | ra->sub-a | 0.043 / - | 0.958 / - |
| G2-calm-access-pfifo | rb->sub-b | 0.107 / - | 0.963 / - |
| G2-calm-access-pfifo | rc->sub-c | 0.107 / - | 0.963 / - |
| G2-calm-access-pfifo | rd->sub-d | 0.211 / - | 0.965 / - |
| G2-calm-access-pfifo | router->sub-ctrl | 0.053 / - | 0.963 / - |
| G2-calm-access-pfifo | router->switch | 0.706 / - | 0.296 / - |
| G2-calm-rev-pfifo | r0->r1 | 0.117 / - | 0.964 / - |
| G2-calm-rev-pfifo | r0->sub-ctrl | 0.053 / - | 0.963 / - |
| G2-calm-rev-pfifo | r1->r0 | 0.026 / - | None / - |
| G2-calm-rev-pfifo | r1->switch | 0.706 / - | 0.296 / - |
| G2-calm-split4-pfifo | r1->r2 | 0.706 / - | 0.296 / - |
| G2-calm-split4-pfifo | r1->sub-ctrl | 0.053 / - | 0.963 / - |
| G2-calm-split4-pfifo | r2->switch-a | 0.708 / - | 0.295 / - |
| G2-calm-split4-pfifo | r2->switch-b | 0.707 / - | 0.296 / - |
| G2-calm-tree16-pfifo | r0->r1 | 0.711 / - | 0.296 / - |
| G2-calm-tree16-pfifo | r0->r2 | 0.71 / - | 0.297 / - |
| G2-calm-tree16-pfifo | r1->switch-a | 0.71 / - | 0.297 / - |
| G2-calm-tree16-pfifo | r1->switch-b | 0.709 / - | 0.297 / - |
| G2-calm-tree16-pfifo | r2->switch-c | 0.712 / - | 0.296 / - |
| G2-calm-tree16-pfifo | r2->switch-d | 0.709 / - | 0.297 / - |
| G2-calm-tree16-pfifo | rr->r0 | 0.708 / - | 0.297 / - |
| G2-calm-tree16-pfifo | rr->sub-ctrl | 0.053 / - | 0.963 / - |
| G2-calm-uneven-pfifo | r1->r2 | 0.036 / - | 0.962 / - |
| G2-calm-uneven-pfifo | r1->sub-ctrl | 0.053 / - | 0.963 / - |
| G2-calm-uneven-pfifo | r2->switch-a | 0.705 / - | 0.295 / - |
| G2-calm-uneven-pfifo | r2->switch-b | 0.709 / - | 0.295 / - |
| G2-calm-uneven-pfifo | r2->switch-c | 0.707 / - | 0.296 / - |
| G3-sburst-s030u070-fq_codel | router->sub-ctrl | 0.053 / - | 0.963 / - |
| G3-sburst-s030u070-fq_codel | router->switch | 0.713 / - | 0.303 / - |
| G3-sburst-s030u070-pfifo | router->sub-ctrl | 0.053 / - | 0.963 / - |
| G3-sburst-s030u070-pfifo | router->switch | 0.71 / - | 0.3 / - |
| M1-sburst-q100-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.964 |
| M1-sburst-q100-pfifo | router->switch | 0.71 / 0.709 | 0.299 / 0.298 |
| M1-sburst-q300-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.962 / 0.963 |
| M1-sburst-q300-pfifo | router->switch | 0.712 / 0.711 | 0.301 / 0.3 |
| M10-sburst-ip2-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M10-sburst-ip2-pfifo | router->switch | 0.712 / 0.709 | 0.301 / 0.299 |
| M10-sburst-ip8-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M10-sburst-ip8-pfifo | router->switch | 0.709 / 0.707 | 0.299 / 0.296 |
| M11-sburst-bw4x1-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.962 / 0.963 |
| M11-sburst-bw4x1-pfifo | router->switch | 0.73 / 0.729 | 0.637 / 0.636 |
| M11-sburst-bw4x12-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| M11-sburst-bw4x12-pfifo | router->switch | 0.719 / 0.72 | 0.637 / 0.637 |
| M11-sburst-bw4x8-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M11-sburst-bw4x8-pfifo | router->switch | 0.717 / 0.717 | 0.635 / 0.635 |
| M12-sburst-jitfwd-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M12-sburst-jitfwd-pfifo | router->switch | 0.711 / 0.708 | 0.3 / 0.298 |
| M12-sburst-jitrev-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.962 / 0.963 |
| M12-sburst-jitrev-pfifo | router->switch | 0.708 / 0.708 | 0.298 / 0.297 |
| M13-sburst-copa-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| M13-sburst-copa-codel | router->switch | 0.706 / 0.706 | 0.295 / 0.295 |
| M13-sburst-copa-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M13-sburst-copa-pfifo | router->switch | 0.706 / 0.706 | 0.296 / 0.295 |
| M14-ssparse-s030u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M14-ssparse-s030u070-pfifo | router->switch | 0.707 / 0.707 | 0.297 / 0.295 |
| M2-sburst-capdrop-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M2-sburst-capdrop-codel | router->switch | 0.709 / 0.708 | 0.298 / 0.297 |
| M2-sburst-capdrop-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.964 |
| M2-sburst-capdrop-pfifo | router->switch | 0.709 / 0.71 | 0.299 / 0.299 |
| M3-sburst-bgbursty-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M3-sburst-bgbursty-codel | router->switch | 0.651 / 0.714 | 0.324 / 0.299 |
| M3-sburst-bgbursty-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M3-sburst-bgbursty-pfifo | router->switch | 0.65 / 0.713 | 0.324 / 0.298 |
| M3-sburst-bgmix-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.964 |
| M3-sburst-bgmix-codel | router->switch | 0.712 / 0.712 | 0.294 / 0.295 |
| M3-sburst-bgmix-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M3-sburst-bgmix-pfifo | router->switch | 0.713 / 0.712 | 0.295 / 0.295 |
| M4-sburst-rttwide-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M4-sburst-rttwide-pfifo | router->switch | 0.708 / 0.71 | 0.298 / 0.299 |
| M4-sburst-rttx05-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M4-sburst-rttx05-pfifo | router->switch | 0.708 / 0.708 | 0.297 / 0.297 |
| M4-sburst-rttx4-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.964 / 0.965 |
| M4-sburst-rttx4-pfifo | router->switch | 0.71 / 0.708 | 0.3 / 0.298 |
| M5-sburst-fps15-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| M5-sburst-fps15-codel | router->switch | 0.709 / 0.709 | 0.299 / 0.298 |
| M5-sburst-fps15-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.961 |
| M5-sburst-fps15-pfifo | router->switch | 0.709 / 0.707 | 0.298 / 0.297 |
| M5-sburst-fps60-codel | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.962 |
| M5-sburst-fps60-codel | router->switch | 0.713 / 0.709 | 0.302 / 0.299 |
| M5-sburst-fps60-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M5-sburst-fps60-pfifo | router->switch | 0.712 / 0.709 | 0.301 / 0.299 |
| M6-calm-stag-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M6-calm-stag-pfifo | router->switch | 0.706 / 0.707 | 0.296 / 0.295 |
| M6-sburst-stag-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.961 / 0.963 |
| M6-sburst-stag-pfifo | router->switch | 0.71 / 0.709 | 0.299 / 0.298 |
| M7-hhier-noroot-pfifo | r1->r2 | 0.021 / 0.02 | 0.963 / 0.963 |
| M7-hhier-noroot-pfifo | r1->sub-ctrl | 0.053 / 0.053 | 0.962 / 0.963 |
| M7-hhier-noroot-pfifo | r2->switch-a | 0.71 / 0.709 | 0.299 / 0.297 |
| M7-hhier-noroot-pfifo | r2->switch-b | 0.709 / 0.71 | 0.299 / 0.299 |
| M8-hhier-mixab-mixab | r1->r2 | 0.711 / 0.71 | 0.3 / 0.299 |
| M8-hhier-mixab-mixab | r1->sub-ctrl | 0.053 / 0.053 | 0.963 / 0.963 |
| M8-hhier-mixab-mixab | r2->switch-a | 0.71 / 0.709 | 0.298 / 0.298 |
| M8-hhier-mixab-mixab | r2->switch-b | 0.712 / 0.711 | 0.301 / 0.3 |
| M9-sstress-s030u070-codel | router->sub-ctrl | 0.053 / 0.053 | 0.961 / 0.962 |
| M9-sstress-s030u070-codel | router->switch | 0.703 / 0.707 | 0.294 / 0.295 |
| M9-sstress-s030u070-pfifo | router->sub-ctrl | 0.053 / 0.053 | 0.961 / 0.963 |
| M9-sstress-s030u070-pfifo | router->switch | 0.702 / 0.7 | 0.293 / 0.288 |

## 5b. Inside stimulus windows (v3-stimuli.csv, medians over the windows; loads / C_e at the target's ingress)

| block | stimulus | u | windows | non-video | video | total | video / calm |
|---|---|---|---|---|---|---|---|
| C2 | surge | 1.05 | 72 | 0.840 | 0.217 | 1.058 | 1.000 |
| C2 | surge | 1.15 | 72 | 0.941 | 0.215 | 1.157 | 0.991 |
| C2 | surge | 1.3 | 72 | 1.087 | 0.178 | 1.262 | 0.812 |
| C3a | surge | 1.05 | 48 | 0.796 | 0.255 | 1.062 | 1.033 |
| C3a | surge | 1.15 | 48 | 0.890 | 0.221 | 1.137 | 0.889 |
| C3a | surge | 1.3 | 48 | 1.042 | 0.143 | 1.254 | 0.581 |
| C3b | udp | 1.05 | 12 | 0.416 | 0.686 | 1.103 | 1.014 |
| C3b | udp | 1.15 | 12 | 0.520 | 0.608 | 1.127 | 0.897 |
| C3b | udp | 1.3 | 12 | 0.675 | 0.473 | 1.148 | 0.698 |
| C4 | ramp | 1.05 | 24 | 0.762 | 0.221 | 0.985 | 1.005 |
| C4 | ramp | 1.15 | 24 | 0.842 | 0.206 | 1.049 | 0.938 |
| C4 | ramp | 1.3 | 24 | 0.954 | 0.168 | 1.118 | 0.751 |
| C5 | tcp | - | 128 | 0.809 | 0.220 | 1.028 | 1.012 |
| C6 | join | 1.05 | 12 | 0.741 | 0.222 | 0.965 | 1.027 |
| C6 | join | 1.15 | 12 | 0.810 | 0.226 | 1.036 | 1.043 |
| C7 | surge | 1.05 | 72 | 0.839 | 0.220 | 1.058 | 1.003 |
| C7 | surge | 1.15 | 264 | 0.940 | 0.196 | 1.133 | 0.885 |
| C7 | surge | 1.3 | 264 | 1.088 | 0.146 | 1.236 | 0.660 |
| C8 | surge | 1.05 | 18 | 0.595 | 0.512 | 1.095 | 1.076 |
| C8 | surge | 1.15 | 66 | 0.694 | 0.495 | 1.187 | 1.042 |
| C8 | surge | 1.3 | 66 | 0.847 | 0.410 | 1.258 | 0.863 |
| C9 | surge | 1.15 | 162 | 0.939 | 0.208 | 1.147 | 0.941 |
| C9 | surge | 1.3 | 162 | 1.089 | 0.185 | 1.272 | 0.841 |
| C10 | surge | 1.05 | 135 | 0.841 | 0.200 | 1.042 | 0.894 |
| C10 | surge | 1.15 | 153 | 0.940 | 0.162 | 1.103 | 0.725 |
| C10 | surge | 1.3 | 135 | 1.089 | 0.138 | 1.226 | 0.618 |
| C11 | surge | 1.05 | 98 | 0.842 | 0.218 | 1.059 | 0.994 |
| C11 | surge | 1.15 | 112 | 0.941 | 0.168 | 1.109 | 0.767 |
| C11 | surge | 1.3 | 98 | 1.090 | 0.112 | 1.199 | 0.511 |
| C12 | capdrop | 1.3 | 96 | 0.000 | 0.078 | 0.078 | 0.883 |
| C12 | surge | 1.05 | 24 | 0.842 | 0.214 | 1.061 | 1.047 |
| C12 | surge | 1.15 | 24 | 0.940 | 0.182 | 1.121 | 0.895 |
| C12 | surge | 1.3 | 24 | 1.083 | 0.137 | 1.216 | 0.672 |
| C13 | surge | 1.15 | 24 | 0.941 | 0.195 | 1.137 | 0.899 |
| C13 | surge | 1.3 | 24 | 1.089 | 0.107 | 1.196 | 0.491 |
| C14 | surge | 1.05 | 12 | 0.844 | 0.217 | 1.062 | 0.993 |
| C14 | surge | 1.15 | 12 | 0.941 | 0.181 | 1.125 | 0.829 |
| C14 | surge | 1.3 | 12 | 1.090 | 0.170 | 1.263 | 0.776 |
| C15 | loss | - | 36 | 0.000 | 0.027 | 0.027 | 1.008 |
| G3 | surge | 1.05 | 12 | 0.840 | 0.200 | 1.041 | 0.898 |
| G3 | surge | 1.15 | 12 | 0.939 | 0.176 | 1.121 | 0.790 |
| G3 | surge | 1.3 | 12 | 1.085 | 0.135 | 1.217 | 0.607 |
| M1 | surge | 1.05 | 24 | 0.840 | 0.203 | 1.046 | 0.926 |
| M1 | surge | 1.15 | 24 | 0.941 | 0.172 | 1.116 | 0.780 |
| M1 | surge | 1.3 | 24 | 1.087 | 0.098 | 1.187 | 0.440 |
| M2 | capdrop | 1.05 | 24 | 0.489 | 0.219 | 0.707 | 1.001 |
| M2 | capdrop | 1.15 | 24 | 0.491 | 0.184 | 0.676 | 0.837 |
| M2 | capdrop | 1.3 | 24 | 0.491 | 0.126 | 0.618 | 0.574 |
| M3 | surge | 1.05 | 48 | 0.809 | 0.220 | 1.033 | 1.004 |
| M3 | surge | 1.15 | 48 | 0.865 | 0.212 | 1.064 | 0.970 |
| M3 | surge | 1.3 | 48 | 0.973 | 0.152 | 1.134 | 0.699 |
| M4 | surge | 1.05 | 36 | 0.840 | 0.230 | 1.070 | 1.045 |
| M4 | surge | 1.15 | 36 | 0.941 | 0.195 | 1.132 | 0.890 |
| M4 | surge | 1.3 | 36 | 1.087 | 0.114 | 1.204 | 0.520 |
| M5 | surge | 1.05 | 48 | 0.840 | 0.218 | 1.058 | 0.989 |
| M5 | surge | 1.15 | 48 | 0.941 | 0.186 | 1.128 | 0.845 |
| M5 | surge | 1.3 | 48 | 1.087 | 0.105 | 1.196 | 0.475 |
| M6 | surge | 1.05 | 12 | 0.840 | 0.225 | 1.062 | 1.026 |
| M6 | surge | 1.15 | 12 | 0.941 | 0.180 | 1.117 | 0.817 |
| M6 | surge | 1.3 | 12 | 1.087 | 0.102 | 1.189 | 0.466 |
| M7 | surge | 1.05 | 12 | 0.838 | 0.235 | 1.081 | 1.068 |
| M7 | surge | 1.15 | 48 | 0.942 | 0.190 | 1.133 | 0.865 |
| M7 | surge | 1.3 | 48 | 1.090 | 0.109 | 1.196 | 0.495 |
| M8 | surge | 1.05 | 18 | 0.839 | 0.223 | 1.057 | 1.010 |
| M8 | surge | 1.15 | 66 | 0.940 | 0.180 | 1.120 | 0.815 |
| M8 | surge | 1.3 | 66 | 1.088 | 0.139 | 1.233 | 0.628 |
| M9 | surge | 1.3 | 24 | 1.094 | 0.200 | 1.296 | 0.942 |
| M9 | surge | 2.0 | 40 | 1.781 | 0.089 | 1.877 | 0.423 |
| M10 | surge | 1.05 | 24 | 0.840 | 0.234 | 1.077 | 1.068 |
| M10 | surge | 1.15 | 24 | 0.941 | 0.199 | 1.135 | 0.907 |
| M10 | surge | 1.3 | 24 | 1.087 | 0.110 | 1.196 | 0.501 |
| M11 | surge | 1.05 | 36 | 0.596 | 0.505 | 1.107 | 1.059 |
| M11 | surge | 1.15 | 36 | 0.694 | 0.488 | 1.180 | 1.014 |
| M11 | surge | 1.3 | 36 | 0.843 | 0.348 | 1.187 | 0.737 |
| M12 | surge | 1.05 | 24 | 0.840 | 0.232 | 1.071 | 1.053 |
| M12 | surge | 1.15 | 24 | 0.941 | 0.184 | 1.124 | 0.838 |
| M12 | surge | 1.3 | 24 | 1.087 | 0.102 | 1.189 | 0.463 |
| M13 | surge | 1.05 | 24 | 0.840 | 0.213 | 1.049 | 0.982 |
| M13 | surge | 1.15 | 24 | 0.941 | 0.204 | 1.141 | 0.941 |
| M13 | surge | 1.3 | 24 | 1.087 | 0.212 | 1.299 | 0.977 |
| M14 | surge | 1.05 | 6 | 0.840 | 0.230 | 1.069 | 1.058 |
| M14 | surge | 1.15 | 6 | 0.945 | 0.192 | 1.139 | 0.887 |
| M14 | surge | 1.3 | 6 | 1.089 | 0.101 | 1.185 | 0.467 |
