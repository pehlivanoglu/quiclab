"""Sender queue (send_buffer_ms) per flow on the v3 runs: produced rate, share of bytes dropped by the GOP-aware head
drop, backlog p90 / max against the cap (1 s of media), share of time the oldest queued frame is >= 900 ms old.
Run from .runs/2026-11-14_1818_v3: python send_queue.py out.csv"""
import sys, glob, os, pandas as pd, numpy as np
rows=[]
for run in sorted(glob.glob("v3-*")):
    if not os.path.isdir(run): continue
    for cc in glob.glob(f"{run}/publishers/pub/sub-*-cc.csv"):
        s=os.path.basename(cc)[:-7]
        if s=="sub-ctrl": continue
        c=pd.read_csv(cc,usecols=["t_us","cc","app_bytes","queue_bytes","queue_age_us","quic_unsent_bytes","backlog_bytes","dropped_frames"])
        if len(c)<10: continue
        dur=(c.t_us.iloc[-1]-c.t_us.iloc[0])/1e6
        dr=pd.read_csv(cc.replace("-cc.csv","-drops.csv"))
        fr=pd.read_csv(f"{run}/publishers/pub/{s}-frames.csv",usecols=["size"]) if os.path.exists(f"{run}/publishers/pub/{s}-frames.csv") else None
        prod=(fr["size"].sum() if fr is not None else 0)+dr["size"].sum()
        rate=prod*8/dur
        rows.append(dict(run=run,block=run.split("-")[1],sub=s,cc=c.cc.iloc[-1],aqm=[a for a in ("fq_codel","pfifo","codel","pie","red","cake","mixab") if f"-{a}-" in run+"-"][:1] or ["?"],
            rate_mbps=rate/1e6,drop_frac=dr["size"].sum()/prod if prod else 0,drop_events=int((dr.groupby("gop").size()>0).sum()) if len(dr) else 0,
            backlog_p90_kB=np.percentile(c.backlog_bytes,90)/1e3,backlog_max_kB=c.backlog_bytes.max()/1e3,
            cap_kB=rate/8/1e3,age_ge900=(c.queue_age_us>=900_000).mean(),unsent_p90_kB=np.percentile(c.quic_unsent_bytes,90)/1e3))
d=pd.DataFrame(rows); d["aqm"]=d.aqm.str[0]
d.to_csv(sys.argv[1], index=False)
