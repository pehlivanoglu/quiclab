#!/bin/bash
# Probe: per-client queue counters on one HTB-shaped egress (design note
# docs/per-flow-queue-counters.md). Runs inside the quiclab image:
#
#   docker run --rm --privileged -v /lib/modules:/lib/modules:ro -v "$PWD/scripts:/probe:ro" \
#       quiclab:latest bash /probe/tc_perflow_probe.sh {fq_codel|cake|red}
#
# Two namespaces joined by a veth, a 10 Mbit/s HTB class, three UDP flows of
# 9, 2 and 6 Mbit/s to 10.0.0.2 / .3 / .4. Clients .2 and .3 are pinned to the
# flow ids 0x3e9 / 0x3ea, .4 is left to the qdisc's own hash.
#   fq_codel  clsact egress sets skb->priority = 20:<id> (no filter on fq_codel)
#   cake      u32 filters on cake with flowid 20:<id> (cake falls back to its hash)
#   red       qevent early_drop -> block 10, one counting filter per client
# Expected: per-class backlog for the pinned ids (fq_codel / cake), per-client
# early-drop counts (red), and no packet dropped for want of a class.
set -u
MODE=${1:?fq_codel|cake|red}
A="ip netns exec a"
ip netns add a; ip netns add b
ip link add va netns a type veth peer name vb netns b
ip -n a addr add 10.0.0.1/24 dev va
for x in 2 3 4; do ip -n b addr add 10.0.0.$x/24 dev vb; done
ip -n a link set va up; ip -n b link set vb up; sleep 0.5
$A tc qdisc add dev va root handle 5: htb default 1
$A tc class add dev va parent 5: classid 5:1 htb rate 10mbit ceil 10mbit
case $MODE in
  fq_codel) $A tc qdisc add dev va parent 5:1 handle 20: fq_codel
            $A tc qdisc add dev va clsact ;;
  cake)     $A tc qdisc add dev va parent 5:1 handle 20: cake unlimited besteffort ;;
  red)      $A tc qdisc add dev va parent 5:1 handle 20: red limit 400000 min 30000 max 90000 \
              avpkt 1200 burst 55 bandwidth 10mbit probability 0.1 qevent early_drop block 10 ;;
  *)        echo "unknown mode $MODE"; exit 2 ;;
esac
pin() {   # $1 = destination, $2 = flow id in hex (tc reads class minors as hex)
  case $MODE in
    fq_codel) $A tc filter add dev va egress protocol ip prio 1 u32 match ip dst "$1"/32 \
                action skbedit priority 20:"$2" ;;
    cake)     $A tc filter add dev va parent 20: protocol ip prio 1 u32 match ip dst "$1"/32 flowid 20:"$2" ;;
    red)      $A tc filter add block 10 protocol ip prio 1 u32 match ip dst "$1"/32 action pass ;;
  esac
}
pin 10.0.0.2 3e9
pin 10.0.0.3 3ea
for x in 2 3 4; do $A ping -c1 -W1 10.0.0.$x >/dev/null || echo "ping 10.0.0.$x FAILED"; done
cat > /tmp/blast.py <<'EOF'
import multiprocessing, socket, time
def blast(dst, mbps, dur=4.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(False)
    gap, t0, n = 1200 * 8 / (mbps * 1e6), time.time(), 0
    while time.time() - t0 < dur:
        try:
            s.sendto(b"x" * 1200, (dst, 5201))
        except BlockingIOError:
            pass
        n += 1
        while time.time() < t0 + n * gap:
            pass
if __name__ == "__main__":   # one process per flow: busy-wait pacing needs its own core
    for dst, mbps in (("10.0.0.2", 9), ("10.0.0.3", 2), ("10.0.0.4", 6)):
        multiprocessing.Process(target=blast, args=(dst, mbps)).start()
EOF
$A python3 /tmp/blast.py &
sleep 3
$A tc -s qdisc show dev va parent 5:1 | sed -n 1,4p
if [ "$MODE" = red ]; then
  $A tc -s filter show block 10 | grep -E "match|Sent"
else
  $A tc -s class show dev va parent 20: | grep -E "^class|backlog"
fi
wait
ip netns del a; ip netns del b
