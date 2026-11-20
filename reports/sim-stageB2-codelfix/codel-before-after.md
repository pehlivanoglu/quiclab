
## matched: 8 runs matching 'codel'

### Packet identity per egress (tracer counts): enq / deq / drop, residual enq - deq - drop

| run | egress | before | residual before | after | residual after |
|---|---|---|---|---|---|
| sim-B-A1-calm-base-codel-r1 | pub-eth0 | 176751 / 176751 / 0 | 0 | 176751 / 176751 / 0 | 0 |
| sim-B-A1-calm-base-codel-r1 | router-eth1 | 32944 / 32944 / 0 | 0 | 32944 / 32944 / 0 | 0 |
| sim-B-A1-calm-base-codel-r1 | router-eth2 | 462862 / 462862 / 0 | 0 | 462862 / 462862 / 0 | 0 |
| sim-B-A1-calm-base-codel-r2 | pub-eth0 | 176203 / 176203 / 0 | 0 | 176203 / 176203 / 0 | 0 |
| sim-B-A1-calm-base-codel-r2 | router-eth1 | 32829 / 32829 / 0 | 0 | 32829 / 32829 / 0 | 0 |
| sim-B-A1-calm-base-codel-r2 | router-eth2 | 463185 / 463185 / 0 | 0 | 463185 / 463185 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | pub-eth0 | 171938 / 171938 / 0 | 0 | 171938 / 171938 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | r1-eth1 | 32944 / 32944 / 0 | 0 | 32944 / 32944 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | r1-eth2 | 429311 / 429311 / 0 | 0 | 429311 / 429311 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | r2-eth2 | 214761 / 214761 / 0 | 0 | 214761 / 214761 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | r2-eth4 | 214843 / 214843 / 0 | 0 | 214843 / 214843 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | pub-eth0 | 171500 / 171500 / 0 | 0 | 171500 / 171500 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | r1-eth1 | 32829 / 32829 / 0 | 0 | 32829 / 32829 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | r1-eth2 | 429573 / 429573 / 0 | 0 | 429573 / 429573 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | r2-eth2 | 214713 / 214713 / 0 | 0 | 214713 / 214713 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | r2-eth4 | 214752 / 214752 / 0 | 0 | 214752 / 214752 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r1 | pub-eth0 | 474088 / 474088 / 0 | 0 | 474088 / 474088 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r1 | router-eth1 | 91685 / 91685 / 0 | 0 | 91685 / 91685 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r1 | router-eth2 | 1789918 / 1721131 / 88956 | -20169 | 1789918 / 1700962 / 88956 | 0 |
| sim-B-A2-sburst-def-codel-r2 | pub-eth0 | 480522 / 480522 / 0 | 0 | 480522 / 480522 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r2 | router-eth1 | 93919 / 93919 / 0 | 0 | 93919 / 93919 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r2 | router-eth2 | 1819358 / 1754950 / 84436 | -20028 | 1819358 / 1734922 / 84436 | 0 |
| sim-B-A4-hhier-def-codel-r1 | pub-eth0 | 1341504 / 1341504 / 0 | 0 | 1341504 / 1341504 / 0 | 0 |
| sim-B-A4-hhier-def-codel-r1 | r1-eth1 | 265593 / 265593 / 0 | 0 | 265593 / 265593 / 0 | 0 |
| sim-B-A4-hhier-def-codel-r1 | r1-eth2 | 3823162 / 3760825 / 79239 | -16902 | 3823162 / 3743923 / 79239 | 0 |
| sim-B-A4-hhier-def-codel-r1 | r2-eth2 | 2158818 / 2111462 / 85188 | -37832 | 2158818 / 2073630 / 85188 | 0 |
| sim-B-A4-hhier-def-codel-r1 | r2-eth4 | 2085362 / 2040198 / 76586 | -31422 | 2085362 / 2008776 / 76586 | 0 |
| sim-B-A4-hhier-def-codel-r2 | pub-eth0 | 1308003 / 1308003 / 0 | 0 | 1308003 / 1308003 / 0 | 0 |
| sim-B-A4-hhier-def-codel-r2 | r1-eth1 | 257276 / 257276 / 0 | 0 | 257276 / 257276 / 0 | 0 |
| sim-B-A4-hhier-def-codel-r2 | r1-eth2 | 3735116 / 3666892 / 85378 | -17154 | 3735116 / 3649738 / 85378 | 0 |
| sim-B-A4-hhier-def-codel-r2 | r2-eth2 | 2115601 / 2068063 / 85721 | -38183 | 2115601 / 2029880 / 85721 | 0 |
| sim-B-A4-hhier-def-codel-r2 | r2-eth4 | 2037120 / 1993660 / 74738 | -31278 | 2037120 / 1962382 / 74738 | 0 |

### Run-wide packet balance (light check item 4: unacked video + lost background - drops)

| run | before: balance / drops | after: balance / drops |
|---|---|---|
| sim-B-A1-calm-base-codel-r1 | 0 / 0 | 0 / 0 |
| sim-B-A1-calm-base-codel-r2 | 0 / 0 | 0 / 0 |
| sim-B-A1-calm-split4l-codel-r1 | 2 / 0 | 2 / 0 |
| sim-B-A1-calm-split4l-codel-r2 | 0 / 0 | 0 / 0 |
| sim-B-A2-sburst-def-codel-r1 | 1192 / 88956 | 1192 / 88956 |
| sim-B-A2-sburst-def-codel-r2 | 1363 / 84436 | 1363 / 84436 |
| sim-B-A4-hhier-def-codel-r1 | 4002 / 241013 | 4002 / 241013 |
| sim-B-A4-hhier-def-codel-r2 | 4066 / 245837 | 4066 / 245837 |

### Simulation-side values that moved (all others identical)

| run | value | before | after |
|---|---|---|---|
| (none) | | | |

### Agreement verdicts that changed (tables-matched.md)

| metric | run | before: testbed / sim / verdict | after |
|---|---|---|---|
| (none) | | | |

## spec: 8 runs matching 'codel'

### Packet identity per egress (tracer counts): enq / deq / drop, residual enq - deq - drop

| run | egress | before | residual before | after | residual after |
|---|---|---|---|---|---|
| sim-B-A1-calm-base-codel-r1 | pub-eth0 | 176826 / 176826 / 0 | 0 | 176826 / 176826 / 0 | 0 |
| sim-B-A1-calm-base-codel-r1 | router-eth1 | 32949 / 32949 / 0 | 0 | 32949 / 32949 / 0 | 0 |
| sim-B-A1-calm-base-codel-r1 | router-eth2 | 462932 / 462932 / 0 | 0 | 462932 / 462932 / 0 | 0 |
| sim-B-A1-calm-base-codel-r2 | pub-eth0 | 176239 / 176239 / 0 | 0 | 176239 / 176239 / 0 | 0 |
| sim-B-A1-calm-base-codel-r2 | router-eth1 | 32833 / 32833 / 0 | 0 | 32833 / 32833 / 0 | 0 |
| sim-B-A1-calm-base-codel-r2 | router-eth2 | 463217 / 463217 / 0 | 0 | 463217 / 463217 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | pub-eth0 | 171982 / 171982 / 0 | 0 | 171982 / 171982 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | r1-eth1 | 32949 / 32949 / 0 | 0 | 32949 / 32949 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | r1-eth2 | 429350 / 429350 / 0 | 0 | 429350 / 429350 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | r2-eth2 | 214770 / 214770 / 0 | 0 | 214770 / 214770 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r1 | r2-eth4 | 214873 / 214873 / 0 | 0 | 214873 / 214873 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | pub-eth0 | 171527 / 171527 / 0 | 0 | 171527 / 171527 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | r1-eth1 | 32833 / 32833 / 0 | 0 | 32833 / 32833 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | r1-eth2 | 429596 / 429596 / 0 | 0 | 429596 / 429596 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | r2-eth2 | 214728 / 214728 / 0 | 0 | 214728 / 214728 / 0 | 0 |
| sim-B-A1-calm-split4l-codel-r2 | r2-eth4 | 214760 / 214760 / 0 | 0 | 214760 / 214760 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r1 | pub-eth0 | 469017 / 469017 / 0 | 0 | 469017 / 469017 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r1 | router-eth1 | 91690 / 91690 / 0 | 0 | 91690 / 91690 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r1 | router-eth2 | 1784842 / 1722632 / 82301 | -20091 | 1784842 / 1702541 / 82301 | 0 |
| sim-B-A2-sburst-def-codel-r2 | pub-eth0 | 475569 / 475569 / 0 | 0 | 475569 / 475569 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r2 | router-eth1 | 93923 / 93923 / 0 | 0 | 93923 / 93923 / 0 | 0 |
| sim-B-A2-sburst-def-codel-r2 | router-eth2 | 1814401 / 1753692 / 80680 | -19971 | 1814401 / 1733721 / 80680 | 0 |
| sim-B-A4-hhier-def-codel-r1 | pub-eth0 | 1327252 / 1327252 / 0 | 0 | 1327252 / 1327252 / 0 | 0 |
| sim-B-A4-hhier-def-codel-r1 | r1-eth1 | 265598 / 265598 / 0 | 0 | 265598 / 265598 / 0 | 0 |
| sim-B-A4-hhier-def-codel-r1 | r1-eth2 | 3808905 / 3746583 / 79212 | -16890 | 3808905 / 3729693 / 79212 | 0 |
| sim-B-A4-hhier-def-codel-r1 | r2-eth2 | 2155860 / 2113562 / 81030 | -38732 | 2155860 / 2074830 / 81030 | 0 |
| sim-B-A4-hhier-def-codel-r1 | r2-eth4 | 2074186 / 2036326 / 68482 | -30622 | 2074186 / 2005704 / 68482 | 0 |
| sim-B-A4-hhier-def-codel-r2 | pub-eth0 | 1281675 / 1281675 / 0 | 0 | 1281675 / 1281675 / 0 | 0 |
| sim-B-A4-hhier-def-codel-r2 | r1-eth1 | 257280 / 257280 / 0 | 0 | 257280 / 257280 / 0 | 0 |
| sim-B-A4-hhier-def-codel-r2 | r1-eth2 | 3708784 / 3650295 / 75570 | -17081 | 3708784 / 3633214 / 75570 | 0 |
| sim-B-A4-hhier-def-codel-r2 | r2-eth2 | 2104544 / 2063707 / 77895 | -37058 | 2104544 / 2026649 / 77895 | 0 |
| sim-B-A4-hhier-def-codel-r2 | r2-eth4 | 2024201 / 1987859 / 67420 | -31078 | 2024201 / 1956781 / 67420 | 0 |

### Run-wide packet balance (light check item 4: unacked video + lost background - drops)

| run | before: balance / drops | after: balance / drops |
|---|---|---|
| sim-B-A1-calm-base-codel-r1 | 0 / 0 | 0 / 0 |
| sim-B-A1-calm-base-codel-r2 | 0 / 0 | 0 / 0 |
| sim-B-A1-calm-split4l-codel-r1 | 3 / 0 | 3 / 0 |
| sim-B-A1-calm-split4l-codel-r2 | 0 / 0 | 0 / 0 |
| sim-B-A2-sburst-def-codel-r1 | 1496 / 82301 | 1496 / 82301 |
| sim-B-A2-sburst-def-codel-r2 | 1109 / 80680 | 1109 / 80680 |
| sim-B-A4-hhier-def-codel-r1 | 5275 / 228724 | 5275 / 228724 |
| sim-B-A4-hhier-def-codel-r2 | 4833 / 220885 | 4833 / 220885 |

### Simulation-side values that moved (all others identical)

| run | value | before | after |
|---|---|---|---|
| (none) | | | |

### Agreement verdicts that changed (tables-spec.md)

| metric | run | before: testbed / sim / verdict | after |
|---|---|---|---|
| (none) | | | |
