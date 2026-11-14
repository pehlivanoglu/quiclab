#!/bin/bash
# Does netem jitter reorder packets on this kernel, and which setup keeps the order?
# Run in the quiclab image (docker run --rm --privileged -v /lib/modules:/lib/modules:ro
#   -v "$PWD/scripts:/probe:ro" quiclab:latest bash /probe/netem_order_probe.sh).
# A sender pushes numbered UDP packets (1200 B, 2.5 Mbit/s, 10 s) through
# "netem delay 20ms <J>ms distribution normal" on a veth; the receiver counts
# packets that arrive with a lower sequence number than one already received
# (reordered) and reports the one-way delay spread from send / receive stamps
# (same host clock). Setups per J in {5, 10, 20} ms:
#   plain      netem alone (its internal tfifo orders by time_to_send)
#   pfifo      netem with a pfifo child qdisc (the documented order-keeping recipe)
#   rate       netem with a rate far above the flow (time_to_send never earlier
#              than the previous packet's)
set -u
A="ip netns exec a"; B="ip netns exec b"
cat > /tmp/send.py <<'PY'
import socket, struct, sys, time
dst, n, mbps = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
gap, t0 = 1200 * 8 / (mbps * 1e6), time.monotonic()
for i in range(n):
    while time.monotonic() < t0 + i * gap: pass
    s.sendto(struct.pack("!Id", i, time.monotonic()) + b"x" * 1188, (dst, 5300))
PY
cat > /tmp/recv.py <<'PY'
import socket, struct, sys, time, statistics
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.bind(("0.0.0.0", 5300)); s.settimeout(2.0)
got, top, reord, owd = 0, -1, 0, []
try:
    while True:
        d = s.recv(2000); i, ts = struct.unpack("!Id", d[:12])
        owd.append((time.monotonic() - ts) * 1000); got += 1
        if i < top: reord += 1
        top = max(top, i)
except socket.timeout:
    pass
owd.sort()
print(f"received {got} reordered {reord} ({reord / max(got, 1):.3%}) owd ms p10/p50/p90/max "
      f"{owd[len(owd)//10]:.1f}/{owd[len(owd)//2]:.1f}/{owd[9*len(owd)//10]:.1f}/{owd[-1]:.1f} sd {statistics.pstdev(owd):.1f}")
PY
for J in 5 10 20; do
  for SETUP in plain pfifo rate; do
    ip netns add a; ip netns add b
    ip link add va netns a type veth peer name vb netns b
    ip -n a addr add 10.0.0.1/24 dev va; ip -n b addr add 10.0.0.2/24 dev vb
    ip -n a link set va up; ip -n b link set vb up; sleep 0.3
    $A ping -c1 -W1 10.0.0.2 >/dev/null
    case $SETUP in
      plain) $A tc qdisc add dev va root handle 10: netem delay 20ms ${J}ms distribution normal limit 50000 ;;
      pfifo) $A tc qdisc add dev va root handle 10: netem delay 20ms ${J}ms distribution normal limit 50000
             $A tc qdisc add dev va parent 10:1 handle 30: pfifo limit 50000 ;;
      rate)  $A tc qdisc add dev va root handle 10: netem delay 20ms ${J}ms distribution normal rate 10gbit limit 50000 ;;
    esac
    $B python3 /tmp/recv.py > /tmp/r.txt & R=$!
    sleep 0.3
    $A python3 /tmp/send.py 10.0.0.2 2600 2.5
    wait $R
    echo "J=${J}ms $SETUP: $(cat /tmp/r.txt)"
    ip netns del a; ip netns del b
  done
done
