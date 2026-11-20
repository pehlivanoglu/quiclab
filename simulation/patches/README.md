# Patches to ns-3.48 (the only changes to ns-3)

`build_ns3.sh` applies every `*.patch` here (idempotent) and refuses to build without them. The run metadata's
source hash (`simlab/run.py build_id`) includes these files.

## ns3-tcp-app-limited-before-add.patch (user decision 2026-11-18, stage B)

`TcpSocketBase::Send` checks for application-limited sending (`TcpRateLinux::CalculateAppLimited`, rule: less than
one segment unsent, not cwnd-limited, all losses retransmitted) **after** adding the new data to the send buffer
(ns-3.48 `src/internet/model/tcp-socket-base.cc:920-937`). Linux makes the same check **before** the new data is
queued: `tcp_sendmsg_locked()` calls `tcp_rate_check_app_limited()` at `net/ipv4/tcp.c:1204` (v7.0), the check itself
at `tcp.c:1113-1127` ("less than one packet to send" = `write_seq - snd_nxt < mss_cache`, measured before the copy
into the write queue). With the ns-3 order, an application that writes in chunks of at least one segment (a video
frame) is never marked application-limited, so BBR's bandwidth filter takes its delivery rate as the path's rate
(stage B report, section 3). The patch moves the call before `m_txBuffer->Add(p)`; nothing else changes.

FLAG (to be stated in the paper): (1) one ns-3 file changed; (2) Linux's further condition "nothing in the host's
qdisc / NIC queue" is still not implemented in ns-3 (`tcp-rate-ops.cc:139-141`); (3) mvfst, the testbed's sender,
marks application-limited whenever its write loop runs out of data (`QuicTransportBaseLite.cpp:1910-1913`), not only
when new data is written; any remaining gap to mvfst is measured, not closed.

## dropped/ns3-tcp-app-limited-mvfst-drain.patch (user, 2026-11-18: one pre-declared attempt) -- DROPPED 2026-11-19

**Not applied.** Result: no effect (reports/sim-stageB3-mvfst-drain/README.md); the tree was reversed with
`patch -R` and build_ns3.sh refuses a tree that still contains it. Kept for the record; the text below is as written
before the check.

Applies on top of the first patch. **FLAG: this models mvfst; it is no longer plain Linux behaviour.**

mvfst 4b691f3 (the testbed's sender, `qvideo/build/_deps/mvfst-src`) checks for application-limited sending at the
end of every write round (`QuicTransportBaseLite.cpp:1899-1919`): if the stream send buffers hold less than one
packet (`sumCurStreamBufferLen < udpSendPacketLen`), no loss is pending, and the congestion controller still has
writable bytes, it calls `setAppLimited()`. BBR ignores the call while inflight > cwnd (`Bbr.cpp:648-656`); otherwise
the bandwidth sampler is marked application-limited until a packet sent after the mark is acknowledged
(`BbrBandwidthSampler.cpp:72-75, 188-191`). App-limited samples cannot lower the max filter (`:166-173`).

The patch runs the same check (`TcpRateLinux::CalculateAppLimited`: less than one segment unsent, inflight < cwnd,
all losses retransmitted) at the end of `TcpSocketBase::SendPendingData` whenever a segment was sent, in addition to
the check in `Send()`. It is behind a GlobalValue, `QuiclabAppLimitedAtDrain` (default false), so one build serves
both profiles; `simlab/run.py --applimited mvfst` sets `NS_GLOBAL_VALUE=QuiclabAppLimitedAtDrain=1`, and the run's
`sim/meta.json` records the profile. With the value false the code path is the first patch's (checked: re-run of one
B2 run, file by file, reports/sim-stageB3-mvfst-drain/).

Expected effect, written before the check: none or almost none. In ns-3 the mark stores `delivered + inflight`
(`tcp-rate-ops.cc:158-162`); between the end of a write round that empties the buffer and the next `Send()` nothing is
sent, so that sum does not change (each ACK moves bytes from inflight to delivered), and the packets marked are the
same. The two checks differ only when the conditions hold at one moment and not the other (inflight >= cwnd at the
end of the round but not at the next write, or the reverse).
