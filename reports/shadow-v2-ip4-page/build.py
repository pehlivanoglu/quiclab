"""Build the ip4 results page from shadow_v2_report.py output + narrative.json."""
import json
import math
import sys
from pathlib import Path

import pandas as pd

src, narr_path, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
cells = pd.read_csv(src / "cells.csv")
events = pd.read_csv(src / "events.csv")
narr = json.loads(narr_path.read_text())


def clean(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


data = {"cells": [{k: clean(v) for k, v in r.items()} for r in cells.to_dict("records")],
        "events": [{k: clean(v) for k, v in r.items()} for r in events.to_dict("records")],
        "scenarios": narr["scenarios"], "overall": narr["overall"], "owdWeak": narr["owdWeak"]}

html = (Path(__file__).parent / "template.html").read_text()
html = html.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False))
for key, val in narr["html"].items():
    html = html.replace(f"<!--{key}-->", val)
out.write_text(html)
print(out, len(html) // 1024, "KiB")
