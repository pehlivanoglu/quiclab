# Frozen grouping candidates (2026-11-18, user item 3)

Frozen as copied files (no tag: the user commits). Nothing here is changed after this date; a later fix is a new
folder. The loader is `candidates.py` (`run(name, events, clients)`); the files are read-only.

| name | reader | events | alpha | note |
|---|---|---|---|---|
| NPR-B | `npr_var.ReaderB` (past-fitted null) | E1-0.5 | 0.05 | no universal-inference guarantee; error rate measured only |
| NPR-A | `npr_var.ReaderA(m_max 0.20, f_max 0.05)` | E1-0.5 | 0.05 | pre-declared setting |
| NPR-A10 | `npr_var.ReaderA(m_max 0.10, f_max 0.05)` | E1-0.5 | 0.05 | post-hoc, labelled; bound violated in 17 / 312 leaves |
| SETS-v1.1 | `grouping.sets.groups`, k = 2 (k = 3 side by side) | E0 (frozen SETS events, 150 ms) | - | tag `grouping-sets-v1.1`; working tree equal to the tag for grouping/sets.py, sets_engine.py, engine.py, config.py on 2026-11-18 |
| SETS@E1-0.5 | same rule | E1-0.5 | - | event-formation reference row |

Event formation E1-0.5: `npr0b.form_window(onsets, 0.5)` on the frozen v2-owd onsets at T100 (`r1.onsets_at`,
`npr0` patch of `shadow_v2_frozen.tick_files` writing to a cache, never into run folders). E0: the frozen SETS / ECG
event formation (`grouping.sets_engine.replay_records`).

Reproduction check (2026-11-18): `candidates.run` + `step12.score_series` give pair vectors identical to
rows-v3-E1-0.5.jsonl (NPR rows) and rows-v2-E1-0.5.jsonl (SETS rows) on v4-A4-hhier-def-codel-r1,
v4-A7-amixed-def-fq_codel-r3 and v3-C10-hindep-s030-codel-r2 (15 / 15).

## sha256

Copies in this folder:

```
61ac439224cb95a9478ee6bcb931331021b4eeb33ecef5e304d186cad60ebae3  candidates.py
494fa9ab0206408880d9384f22a1b8c245bdb7dc02e3330bdcc4d7efb17c1310  npr.py
23b8bd79163143b0b5498fd1c4e89ccff7f692f11a39dddb06a324c43359df01  npr_var.py
c36a09b2422564849c0a78cb78e7ecf0f952f4ef86ad037bf467a6aab0900ab3  step12.py
68135a59cc25630cf4ec95439e753b4e5233c493bd653a54aa29b275bf84355b  npr0.py
eee7840fd373c08e99022d4d329485bbbbf0fc8dbd2f714d4ba9dc495b6b655a  npr0b.py
146ecd6e0c30b9fc8fa13c6a959b2653b3927295a3618d898325626bc867c6d9  grouping_score.py
```

Dependencies used in place (frozen elsewhere or unchanged), hashes on 2026-11-18:

```
20f0749adce0a1d4f7906fdea26eb3cd639ca3ada6d20900cc6e6caa9eaf3ee3  grouping/sets.py
1901a15f8a55aa44ea0a8ce4cf3a2211611e3ab3e3ef6e204a0adeb268107afe  grouping/sets_engine.py
0f7d1dc25d435d001f4fd7abd71ad8a440a63d83559cc69f105952467bb4009a  grouping/engine.py
cdcd71924dd784b8f05b974886e2beacc1e7983b2716b562d3df12589b8329ad  grouping/config.py
86a95ed48bc9129a17011ef94ddb9a7e3394f93d9efb16ffe35b0f2cd118c2b8  scripts/shadow_v2_frozen.py
21011203dc5a8dc06ca4d6fafe50f61ac179f7447b58de60079716f9fd7b91a2  scripts/shadow_v2_step1.py
cb0bc39327d2eabfbdae6ef7a428c5fc79e25c7410682dcaae9f1b77f31e1ea5  scripts/owd_mode.py
121242e08a001f881603ea4e457920218550b547aece2e30e21387d45d4a74c2  scripts/det_eval.py
ae62e801d652a42a2d9fd954b978ab303108e7e953d472ea5fc7629b08df5625  scripts/grouping_adapter.py
342943b277eb8e731ea8c4e5ba7af705f6cca6b1f041fd197603f27080d13b50  scripts/gtq.py
fcf5d84497ed26555a199d01844af8ce57cb72f1926fc868a39431bd0c35a5a1  reports/sets-low-threshold-2026-11-16/r1.py
```
