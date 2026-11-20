"""Grouping rows kept for every stage C run (user 2026-11-19): the event lists any grouping method needs, so that it
can be scored later without re-running. Written next to the frozen onsets (sim/episodes-v2-owd.json):

  sim/events-E0.json       frozen SETS / ECG event formation (grouping.sets_engine.replay_records, default Config):
                           per close t0, close time, members (flow, aligned onset, arrival)
  sim/events-E1-0.5.json   E1-0.5 (npr0b.form_window, W 0.5 s; NA by the STEP 0 rules), the NPR candidates' input:
                           per event t0, close, ones, na
Both from the frozen v2-owd onsets at T100 (r1.onsets_at), as the SETS step uses them. Read-only imports of the
frozen NPR folder (via sets300_diag.e1_events); nothing is written there.
"""

from __future__ import annotations

import json
from pathlib import Path


def write(rd: Path) -> None:
    import stageb_compare  # noqa: F401  (sys.path for scripts/ and the SETS low-threshold folder)
    import det_eval as d
    import grouping_score as gs
    import r1
    import sets300_diag as sd
    from grouping.sets_engine import replay_records

    run = d.Run(rd)
    cfg, records, onsets = r1.onsets_at(rd, r1.LEVELS["T100"])
    e0 = []

    def on_close(eng, e):
        e0.append({"t0": e.t0, "close": eng.now,
                   "members": [[m.flow, m.t_al, m.t_arrival] for m in e.members if m.flow != gs.CTRL]})

    replay_records(records, cfg, on_close=on_close)
    clients = sorted(s for s in run.subs if s != gs.CTRL)
    e1 = sd.e1_events(rd, run, cfg, records, onsets, clients)
    (rd / "sim" / "events-E0.json").write_text(json.dumps(e0))
    (rd / "sim" / "events-E1-0.5.json").write_text(json.dumps(e1))
