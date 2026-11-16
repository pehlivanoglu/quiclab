#!/bin/bash
# Leak probe for the fq_codel client pinning (2026-11-15 fix): the orchestrator's own flow_pin_commands on a
# veth pair through a 10 Mbit/s HTB + fq_codel, two pinned clients that send NOTHING, and 2000 unpinned UDP
# 5-tuples (one socket, 2000 destination ports, 15 Mbit/s in total, so the qdisc is backlogged). Every 50 ms the class
# dump is read; a backlog on a pinned client's class (20:301 / 20:302) means unpinned traffic entered a
# client's sub-queue. Mode "fixed" applies the commands as they are; mode "old" drops the catch-all filter
# (the pre-fix behaviour) for comparison.
#   docker run --rm --privileged -v /lib/modules:/lib/modules:ro -v "$PWD:/q:ro" \
#       quiclab:latest bash /q/scripts/tc_fq_pin_leak_probe.sh fixed
#   (and the same with "old")
set -u
MODE=${1:-fixed}
A="ip netns exec a"
ip netns add a; ip netns add b
ip link add va netns a type veth peer name vb netns b
ip -n a addr add 10.0.0.1/24 dev va; for x in 2 3 4; do ip -n b addr add 10.0.0.$x/24 dev vb; done
ip -n a link set va up; ip -n b link set vb up; sleep 0.5
$A tc qdisc add dev va root handle 5: htb default 1
$A tc class add dev va parent 5: classid 5:1 htb rate 10mbit ceil 10mbit
$A tc qdisc add dev va parent 5:1 handle 20: fq_codel
$A python3 -c "
import sys; sys.path.insert(0, '/q')
from quiclab.config.schema import AqmKind
from quiclab.orchestrator.shaping import flow_pin_commands
for c in flow_pin_commands('va', AqmKind('fq_codel'), {'sub-a': '10.0.0.2', 'sub-b': '10.0.0.3'}, {'sub-a': 0x301, 'sub-b': 0x302}):
    if '$MODE' == 'old' and ' flow hash ' in c:
        continue
    print(c)" > /tmp/pins.sh
cat /tmp/pins.sh | sed 's/^/  /'
while read -r c; do $A $c || echo "FAILED: $c"; done < /tmp/pins.sh
for x in 2 3 4; do $A ping -c1 -W1 10.0.0.$x >/dev/null || echo "ping .$x FAILED"; done
cat > /tmp/blast.py <<'PY'
import socket, time
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setblocking(False)
ports = list(range(20000, 22000))          # 2000 distinct 5-tuples from one socket
gap, t0, n = 1200 * 8 / 15e6, time.time(), 0
while time.time() - t0 < 4.0:
    try:
        s.sendto(b"x" * 1200, ("10.0.0.4", ports[n % len(ports)]))
    except BlockingIOError:
        pass
    n += 1
    while time.time() < t0 + n * gap:
        pass
print(f"sent {n} datagrams")
PY
$A python3 /tmp/blast.py &
B=$!
cat > /tmp/classes.py <<'PY'
import sys
pinned = leak = low = 0
for line in sys.stdin:
    p = line.split()
    if len(p) >= 3 and p[0] == "class" and p[1] == "fq_codel" and p[2].startswith("20:"):
        minor = int(p[2].split(":")[1], 16)
        if minor in (0x301, 0x302):
            leak = 1
        elif minor <= 0x300:
            low = 1
print(leak, low)
PY
leak=0; samples=0; low=0
for i in $(seq 1 70); do
  read l w < <($A tc -s class show dev va | python3 /tmp/classes.py)
  samples=$((samples + 1)); leak=$((leak + l)); low=$((low + w))
  sleep 0.05
done
wait $B
echo "mode $MODE: $samples class dumps; with a backlog on a pinned client class: $leak; with unpinned classes <= 20:300 backlogged: $low"
if [ $low -eq 0 ]; then
  echo "INCONCLUSIVE: no backlogged unpinned class seen (no load reached the qdisc)"
elif [ $leak -eq 0 ]; then
  echo "PASS: unpinned traffic backlogged on classes <= 20:300 and never in a client's sub-queue (mode $MODE)"
else
  echo "LEAK: unpinned traffic in a pinned client's sub-queue (mode $MODE)"
fi
