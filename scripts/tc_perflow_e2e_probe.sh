#!/bin/bash
# End-to-end probe: the orchestrator's own flow_pin_commands plus quiclab/router_metrics.py
# (--flows) on a veth pair, three UDP flows (9 / 2 / 6 Mbit/s, two pinned) through a
# 10 Mbit/s HTB + AQM. Writes /out/va.csv and /out/va-flows.csv and prints per-flow backlog.
#   docker run --rm --privileged -v /lib/modules:/lib/modules:ro -v "$PWD:/q:ro" -v /some/dir:/out \
#       -v "$PWD/scripts/tc_perflow_e2e_probe.sh:/out/run.sh:ro" quiclab:latest bash /out/run.sh fq_codel fq_codel
#   (second run: "cake unlimited besteffort" cake)
set -u
A="ip netns exec a"
ip netns add a; ip netns add b
ip link add va netns a type veth peer name vb netns b
ip -n a addr add 10.0.0.1/24 dev va; for x in 2 3 4; do ip -n b addr add 10.0.0.$x/24 dev vb; done
ip -n a link set va up; ip -n b link set vb up; sleep 0.5
$A tc qdisc add dev va root handle 5: htb default 1
$A tc class add dev va parent 5: classid 5:1 htb rate 10mbit ceil 10mbit
$A tc qdisc add dev va parent 5:1 handle 20: $1
# the orchestrator's own commands
$A python3 -c "
import sys; sys.path.insert(0, '/q')
from quiclab.config.schema import AqmKind
from quiclab.orchestrator.shaping import flow_pin_commands
for c in flow_pin_commands('va', AqmKind('$2'), {'sub-a': '10.0.0.2', 'sub-b': '10.0.0.3'}, {'sub-a': 0x301, 'sub-b': 0x302}): print(c)" > /tmp/pins.sh
bash -x /tmp/pins.sh 2>&1 | sed 's/^/  /' | head -4; while read -r c; do $A $c; done < /tmp/pins.sh
$A tc qdisc replace dev va clsact; $A tc filter replace dev va egress protocol all pref 49152 handle 1 matchall action pass
for x in 2 3 4; do $A ping -c1 -W1 10.0.0.$x >/dev/null || echo "ping .$x FAILED"; done
$A python3 /q/quiclab/router_metrics.py --interface va --interval-ms 25 --output /out/va.csv --flows 301=sub-a,302=sub-b &
RM=$!
sleep 0.5
cat > /tmp/blast.py <<'PY'
import multiprocessing, socket, time
def blast(dst, mbps, dur=3.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.setblocking(False)
    gap, t0, n = 1200 * 8 / (mbps * 1e6), time.time(), 0
    while time.time() - t0 < dur:
        try: s.sendto(b"x" * 1200, (dst, 5201))
        except BlockingIOError: pass
        n += 1
        while time.time() < t0 + n * gap: pass
if __name__ == "__main__":
    for d, m in (("10.0.0.2", 9), ("10.0.0.3", 2), ("10.0.0.4", 6)):
        multiprocessing.Process(target=blast, args=(d, m)).start()
PY
$A python3 /tmp/blast.py; sleep 3.5; kill $RM; wait $RM 2>/dev/null
echo "rows: $(wc -l < /out/va.csv) main, $(wc -l < /out/va-flows.csv) flows"
python3 - <<'PY'
import csv, collections
rows = list(csv.DictReader(open("/out/va-flows.csv")))
by = collections.defaultdict(list)
for r in rows: by[r["flow"] or "hash:" + r["class"]].append(int(r["backlog_bytes"]))
for k, v in sorted(by.items()): print(f"  {k:12s} samples {len(v):3d} max backlog {max(v):6d} B, median {sorted(v)[len(v)//2]:6d}")
main = list(csv.DictReader(open("/out/va.csv")))
print("  offered", sum(int(r["offered_bytes"]) for r in main), "transmitted", sum(int(r["transmitted_bytes"]) for r in main))
PY
