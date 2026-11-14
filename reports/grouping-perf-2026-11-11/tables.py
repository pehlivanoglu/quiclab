#!/usr/bin/env python3
"""Step 2 of the 2026-11-11 performance report: medians per campaign x AQM family
(mode "group") or per onset source (mode "src"); see collect.py."""
import json, sys, statistics
from collections import defaultdict
rows = json.load(open(sys.argv[1]))
def med(xs):
    xs=[x for x in xs if x is not None]; return round(statistics.median(xs),2) if xs else None
def fam(a): return "FIFO" if a in ("pfifo","red","pie") else a
def summ(rs):
    tp=sum(r["tp"] for r in rs); fp=sum(r["fp"] for r in rs); fn=sum(r["fn"] for r in rs); tn=sum(r["tn"] for r in rs)
    n=sum(r["n_pairs"] for r in rs); dec=sum(r["decided"] for r in rs); cor=sum(r["correct"] for r in rs)
    pos=[r for r in rs if r["n_shared"]>0]
    sw=sum(len(r["e2e_rows"]) for r in rs)
    da=sum(r["e2e"]["detected_all"] or 0 for r in rs if r["e2e"]["detected_all"] is not None)
    gc=sum(r["e2e"]["grouped_cases"] or 0 for r in rs if r["e2e"]["grouped_cases"] is not None)
    at=sum(r["e2e"]["attributed_ok"] or 0 for r in rs if r["e2e"]["attributed_ok"] is not None)
    def a(k,f): return med([(r["e2e"].get(k) or {}).get(f) for r in pos])
    return dict(runs=len(rs), P=round(tp/(tp+fp),2) if tp+fp else None, R=round(tp/(tp+fn),2) if tp+fn else None,
        acc_dec=round(cor/dec,2) if dec else None, acc_all=round(cor/n,2) if n else None, cov=round(dec/n,2) if n else None,
        fp=fp, tree=f"{sum(r['tree'] for r in pos)}/{len(pos)}",
        tcorr_rel=med([r["t_correct_rel"] for r in pos]), tcorr_reached=f"{sum(r['t_correct'] is not None for r in pos)}/{len(pos)}",
        leaf_lat=med([x for r in pos for x in r["leaf_lat"]]), leaf_ev=med([x for r in pos for x in r["leaf_ev"]]),
        tgroup=med([r["e2e"]["t_group_p50_s"] for r in pos]),
        shared_w=sw, det_all=da, grouped=gc, attributed=at,
        aP=a("alarm_single","precision"), aL=a("alarm_single","latency_p50_s"), gP=a("alarm_grouped","precision"), gL=a("alarm_grouped","latency_p50_s"),
        spread=med([r["spread"].get("p50") for r in pos]), spread90=med([r["spread"].get("p90") for r in pos]))
mode=sys.argv[2]
by=defaultdict(list)
for r in rows:
    if mode=="src":
        if r["group"]!="G0": by[(r["src"], fam(r["aqm"]))].append(r)
    elif r["src"]=="v2-owd":
        key=(r["group"], fam(r["aqm"])) if mode=="group" else (r["group"], r["type"], fam(r["aqm"]))
        by[key].append(r)
for k,rs in sorted(by.items()):
    print(" ".join(map(str,k)), json.dumps(summ(rs)))
