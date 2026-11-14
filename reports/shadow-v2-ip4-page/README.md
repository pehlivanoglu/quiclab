# Shadow v2 ip4 results page (generator)

Moved here on 2026-11-11 from a temporary session folder. Published page:
https://claude.ai/artifact/4BY7opaeKJVdyuqPfS44Tk (`shadow-v2-ip4.html` is the built copy).

- `narrative.py SRC OUT/narrative.json`: builds the Turkish narrative from the ip4
  results (`reports/detector-v2/ip4/`: cells.csv, events.csv, alarm_on.csv, report.md).
- `build.py SRC narrative.json OUT.html`: fills `template.html` (static parts from `static.py`).
- `check.js`: page checks.

Automating the generation is an open item in TODO.md ("Shadow v2 open notes").
