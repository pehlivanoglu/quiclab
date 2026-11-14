#!/bin/bash
# tc behaviours the per-client pins rely on (docs/per-flow-queue-counters.md), run in the
# quiclab image: docker run --rm --privileged -v /lib/modules:/lib/modules:ro -v "$PWD/scripts:/probe:ro" quiclab:latest bash /probe/tc_pin_semantics_probe.sh
# Checks: flower `replace` with fixed pref / handle is idempotent; `tc qdisc replace clsact`
# keeps the egress filters; `continue` after skbedit lets the later matchall still count.
ip link add dmy0 type dummy; ip link set dmy0 up; ip addr add 10.9.0.1/24 dev dmy0
tc qdisc add dev dmy0 root handle 5: htb default 1; tc class add dev dmy0 parent 5: classid 5:1 htb rate 100mbit
tc qdisc add dev dmy0 parent 5:1 handle 20: fq_codel
tc qdisc replace dev dmy0 clsact
tc filter replace dev dmy0 egress pref 100 handle 1 protocol ip flower dst_ip 10.9.0.2 action skbedit priority 20:301 continue && echo flower1
tc filter replace dev dmy0 egress pref 100 handle 1 protocol ip flower dst_ip 10.9.0.2 action skbedit priority 20:301 continue && echo flower1-again
tc qdisc replace dev dmy0 clsact && echo clsact-replaced
tc filter replace dev dmy0 egress protocol all pref 49152 handle 1 matchall action pass
tc filter show dev dmy0 egress | grep -c "pref 100" 
ping -c 5 -i 0.05 -W 0.1 10.9.0.2 >/dev/null
tc -s -j filter show dev dmy0 egress | python3 -c "import json,sys
for f in json.load(sys.stdin):
  o=f.get('options',{})
  for a in o.get('actions',[]): print(f.get('pref'), f.get('kind'), a.get('kind'), a.get('control_action'), a.get('stats',{}).get('packets'))"
tc -s class show dev dmy0 parent 20: | head -4
ip netns add c; ip link add dmy1 type dummy; ip link set dmy1 up; tc qdisc add dev dmy1 root handle 5: htb default 1; tc class add dev dmy1 parent 5: classid 5:1 htb rate 100mbit; tc qdisc add dev dmy1 parent 5:1 handle 20: cake unlimited besteffort
tc filter replace dev dmy1 parent 20: pref 100 handle 1 protocol ip flower dst_ip 10.9.0.2 classid 20:301 && echo cake-flower
tc filter replace dev dmy1 parent 20: pref 100 handle 1 protocol ip flower dst_ip 10.9.0.2 classid 20:301 && echo cake-flower-again
