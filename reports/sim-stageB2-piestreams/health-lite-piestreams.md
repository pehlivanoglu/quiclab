| run | frozen | light | items 1-6 | totals = tracer | busy-rate median / share (frozen interdeq within tol) | balance / drops |
|---|---|---|---|---|---|---|
| B2 matched sim-B-A2-sburst-def-codel-r1 | True | True | o-oooo | - | router-eth2 1.0097 / 0.9998 (0.97149) | 1192 / 88956 |
| B2 matched sim-B-A2-sburst-def-pfifo-r1 | True | True | o-oooo | - | router-eth2 1.0095 / 0.9995 (0.9753) | 1167 / 114777 |
| B2 matched sim-B-A2-sburst-def-pie-r1 | True | True | o-oooo | - | router-eth2 1.0097 / 0.9997 (0.97594) | 529 / 114056 |
| B2 matched sim-B-A2-sburst-def-pie-r2 | True | True | o-oooo | - | router-eth2 1.0095 / 1.0 (0.9754) | 631 / 122989 |
| B2 matched sim-B-A4-hhier-def-codel-r1 | True | True | o-oooo | - | r1-eth2 1.0096 / 0.9986 (0.891); r2-eth2 1.0091 / 0.9995 (0.92349); r2-eth4 1.0094 / 0.9998 (0.91365) | 4002 / 241013 |
| B2 matched sim-B-A4-hhier-def-pfifo-r1 | True | True | o-oooo | - | r1-eth2 1.0098 / 0.9991 (0.91569); r2-eth2 1.0099 / 0.9995 (0.92989); r2-eth4 1.0099 / 0.9998 (0.92346) | 3098 / 337711 |
| B2 matched sim-B-G1-sburst-n16-pfifo-r1 | True | True | o-oooo | - | router-eth2 1.0098 / 0.9996 (0.85977) | 1315 / 81819 |
| B2 spec sim-B-A2-sburst-def-codel-r1 | True | True | o-oooo | - | router-eth2 1.01 / 0.999 (0.9634) | 1496 / 82301 |
| B2 spec sim-B-A2-sburst-def-pfifo-r1 | True | True | o-oooo | - | router-eth2 1.0095 / 0.999 (0.9688) | 1106 / 111233 |
| B2 spec sim-B-A2-sburst-def-pie-r1 | True | True | o-oooo | - | router-eth2 1.0096 / 0.999 (0.96643) | 619 / 120002 |
| B2 spec sim-B-A2-sburst-def-pie-r2 | True | True | o-oooo | - | router-eth2 1.0095 / 0.9997 (0.96791) | 642 / 120505 |
| regress-d1 matched sim-B-A4-hhier-def-pfifo-r1 | True | True | o-oooo | - | r1-eth2 1.0098 / 0.9991 (0.91569); r2-eth2 1.0099 / 0.9995 (0.92989); r2-eth4 1.0099 / 0.9998 (0.92346) | 3098 / 337711 |
| regress-d1 matched sim-B-G1-sburst-n24-pfifo-r1 | True | True | o-oooo | - | router-eth2 1.01 / 0.998 (0.87112) | 2091 / 123000 |
| regress-d1 sample sim-B-A4-hhier-def-pfifo-r1 | True | True | oooooo | True | r1-eth2 1.0098 / 0.9991 (0.91569); r2-eth2 1.0099 / 0.9995 (0.92989); r2-eth4 1.0099 / 0.9998 (0.92346) | 3098 / 337711 |
| regress-d1 none sim-B-A4-hhier-def-pfifo-r1 | None | True | oooooo | - | r1-eth2 1.0098 / 0.9991 (None); r2-eth2 1.0099 / 0.9995 (None); r2-eth4 1.0099 / 0.9998 (None) | 3098 / 337711 |

negative: {'test': 'truncated sender file', 'file': 'a1-sent.csv', 'caught': True, 'overall': False}

negative: {'test': 'missing counter row', 'file': 'r1-eth1-totals.csv', 'caught': True, 'overall': False}

negative: {'test': 'wrong capacity (x1.25)', 'egress': 'a r2->switch-a', 'links_edited': 1, 'caught': True, 'overall': False}

ACCEPT: 0 problem(s)
