# Health failures in K2 (2026-11-17, offline look)

## N8 negpriv, check 4 on the private access egresses: same effect as K1 A7 and v3 C12

Every private access egress ra..rd -> sub-a..d fails the service part of check 4 the same way in all three:

| runs | private egress (allowed Mb/s) | gap within tol | jitter p1 / p99 us |
|---|---|---|---|
| K2 N8 negpriv (pfifo, codel, r1 / r2) | ra 3, rb ~6.1-6.3 | ra 0.92-0.95, rb 0.96-0.99 | ra -404.4 to -404.7 / 3.7-13.9 |
| K1 A7 amixed (codel r1-r5, fq_codel r1) | ra 3, rb ~5.2-5.5 | ra 0.77-0.95, rb 0.90-0.98 | -404.1 to -405.2 / - |
| v3 C12 amixed-access (pfifo, codel, fq_codel, r1 / r2) | ra 3, rb ~5.3-5.6 | ra 0.78-0.93, rb 0.88-0.98 | -403.1 to -405.3 / - |

The same constant ~-404 us early dequeue and the same gap shares on the same low-capacity private links: the known
shaper resolution effect at low rate (the earlier "resolution limit at about 0.8 Mb/s" case), present whether or not
the run has capacity drops. Flagged; nothing different to understand before K2's GT-Q scoring. Lost events 0,
unmatched 0, accounting ok in all of them.

## N3 hchurn and T1 dclean, check 1: passes over the time when all planned clients are present and bg is on

[loadshare-present.md](loadshare-present.md): all 10 runs (N3 hchurn codel / pfifo r1 / r2; T1 dclean def / ext /
hs50 r1 / r2) pass check 1 restricted that way (load and share within tolerance). The raw FAIL stays in each run's
v3-checks.json. N3 has only 38-56 s of calm time with every client present (churn), T1 211-223 s (bg starts at 60 s).
