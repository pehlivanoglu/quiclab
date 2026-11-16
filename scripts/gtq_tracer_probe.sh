#!/bin/bash
# Probe: the GT-Q router tracer (quiclab/router_trace.bt) on one HTB-shaped
# egress, outside any testbed run. Runs inside the quiclab image:
#
#   docker run --rm --privileged -v "$PWD:$PWD" -w "$PWD" quiclab:latest \
#       bash scripts/gtq_tracer_probe.sh {pfifo|fq_codel|codel|pie|red} [OUT_DIR]
#
# Two namespaces joined by a veth, a 10 Mbit/s HTB class, an AQM leaf with a
# short limit, a 15 Mbit/s iperf3 UDP flow to .2 and a 1 Mbit/s one to .3 for
# 4 s (drops guaranteed). The tracer output is converted with
# quiclab.router_trace and checked: tracer attached, enqueue = dequeue + drops,
# rows = counters, no lost events, nothing larger than MTU, drops attributed.
set -u
MODE=${1:?pfifo|fq_codel|codel|pie|red}
OUT=${2:-/tmp/gtq-probe-$MODE}
rm -rf "$OUT"; mkdir -p "$OUT/router-trace"
A="ip netns exec a"; B="ip netns exec b"
cleanup() { ip netns del a 2>/dev/null; ip netns del b 2>/dev/null; }
trap cleanup EXIT
cleanup
ip netns add a; ip netns add b
ip link add va netns a type veth peer name vb netns b
ip -n a addr add 10.0.0.1/24 dev va
for x in 2 3; do ip -n b addr add 10.0.0.$x/24 dev vb; done
ip -n a link set va up; ip -n b link set vb up; ip -n a link set lo up; ip -n b link set lo up
for ns in a b; do ip netns exec $ns ethtool -K v${ns} gro off gso off tso off >/dev/null 2>&1; done
sleep 0.5
$A tc qdisc add dev va root handle 5: htb default 1
$A tc class add dev va parent 5: classid 5:1 htb rate 10mbit ceil 10mbit burst 15k quantum 1500
case $MODE in
  pfifo)    $A tc qdisc add dev va parent 5:1 handle 20: pfifo limit 30 ;;
  fq_codel) $A tc qdisc add dev va parent 5:1 handle 20: fq_codel limit 60 ecn ;;
  codel)    $A tc qdisc add dev va parent 5:1 handle 20: codel limit 60 ;;
  pie)      $A tc qdisc add dev va parent 5:1 handle 20: pie limit 60 ;;
  red)      $A tc qdisc add dev va parent 5:1 handle 20: red limit 90000 min 15000 max 45000 avpkt 1200 burst 25 probability 0.02 bandwidth 10mbit ;;
esac
[ -e /sys/kernel/tracing/events/qdisc ] || mount -t tracefs nodev /sys/kernel/tracing
NETNS=$($A stat -L -c %i /proc/self/ns/net)
IDX=$($A ip -o link show dev va | cut -d: -f1)
echo "netns=$NETNS ifindex=$IDX"
$B iperf3 -s -D -1 -p 5201 >/dev/null; $B iperf3 -s -D -1 -p 5202 >/dev/null; sleep 0.3
MASK=$((1 << IDX))
# bpftrace in the container's own namespaces: `ip netns exec` remounts /sys and hides
# tracefs; the script filters by the netns inode, so where it runs does not matter.
env BPFTRACE_MAX_MAP_KEYS=262144 BPFTRACE_PERF_RB_PAGES=512 \
    bpftrace -B full -o "$OUT/router-trace/router.raw" quiclab/router_trace.bt "$NETNS" "$MASK" \
    > "$OUT/tracer.log" 2>&1 &
TP=$!
for i in $(seq 1 150); do grep -qs "Attaching" "$OUT/tracer.log" "$OUT/router-trace/router.raw" && break; sleep 0.1; done
sleep 0.5
echo "tracer log:"; cat "$OUT/tracer.log"
$A iperf3 -c 10.0.0.2 -p 5201 -u -b 15M -l 1400 -t 4 >/dev/null &
$A iperf3 -c 10.0.0.3 -p 5202 -u -b 1M -l 1200 -t 4 >/dev/null
wait %2 2>/dev/null
sleep 0.5
kill -INT $TP; wait $TP; echo "tracer exit $?"
$A tc -s qdisc show dev va | sed -n 1,12p
python3 - "$OUT" "$IDX" <<'EOF'
import sys
from pathlib import Path
sys.path.insert(0, ".")
from quiclab import router_trace as rt
out, idx = Path(sys.argv[1]), int(sys.argv[2])
tr = rt.Tracer(router="a", ifaces={idx: "va"}, hops={"va": ("a", "b")}, raw=out / "router-trace" / "router.raw",
               log=out / "tracer.log", started_ns=1, stopped_clean=True)
counts = rt.finalize(out, [tr])
row = counts[0]
print({k: row[k] for k in row if k != "errors"}, "errors:", row["errors"])
print("identity:", rt.identity(row))
t = rt.read_packets(out / "router-trace" / "va-packets.csv")
print(t.groupby(["kind", "daddr"]).size())
dq = t[t.kind == "dequeue"]
print("sojourn ms p50/p99:", ((dq.t_deq_ns - dq.t_enq_ns) / 1e6).quantile([0.5, 0.99]).round(2).tolist())
print("drop reasons:", t[t.kind == "drop"].reason.value_counts().to_dict())
print("ports:", sorted(set(t.dport[t.proto == 17]))[:5], "len max:", t.len.max())
ok = (rt.identity(row)[0] and row["lost_events"] == 0 and row["oversize"] == 0 and row["rows_drop"] > 0
      and row["n_enq"] > 0 and not row["errors"])
print("PROBE", "PASS" if ok else "FAIL")
EOF
