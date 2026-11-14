# Why FlowBot's ground truth does not fit ultra-low-latency streaming (note, 2026-11-12)

FlowBot (flowbot/src/siamese/preprocess.py, `get_double_queues`) labels a flow's
bottleneck every 5 ms in ns-3: queue length averaged over the last 50 ms; no
bottleneck when that average is below 50 packets on every candidate queue, else
the larger queue. Ported to our runs in `scripts/gt_flowbot.py`, scored in
`reports/baselines-2026-11-12/` ("FlowBot GT").

Reasons it is not a suitable truth for ULL video:

1. **The threshold is an absolute packet count, not a delay.** 50 packets is
   ~34 ms of queue at 17.5 Mb/s, ~600 ms at 1 Mb/s, ~7 ms at 100 Mb/s. For ULL
   what matters is the added delay against a tens-of-ms playout budget, so the
   same congestion counts or not depending on link rate and packet size.
   On our runs: the 0.5 BDP queues (limit 50 packets) almost never reach it; on
   low-rate cells the whole queue is below it, so every alarm counts as false
   (M5: precision 0.72, 1.04 false alarms per minute).
2. **50 packets is far beyond the ULL tolerance.** A queue that adds 20–30 ms
   already costs a frame or more at 25–60 fps with a ~100 ms budget; FlowBot calls
   it "no bottleneck". It labels late (latency against it ~110 ms vs ~250 ms against
   GT1's 5 ms target: the episode starts only once the queue is large).
3. **No persistence and no hysteresis.** The label flips whenever the 50 ms mean
   crosses the threshold: many very short episodes (G0 calm065 pfifo: 28 episodes,
   p50 38 ms) and CLEAR gaps inside one congestion, where an alarm counts as false.
   Video keyframes produce exactly such short queues; GT1 / GT2 require 150 ms
   (CoDel-style) and a hysteresis band to separate them.
4. **Built for bulk TCP in simulation.** Long-lived saturating flows on a dumbbell
   with two candidate queues per flow and large buffers; it has no notion of
   application-limited, rate-capped flows (our video), multi-hop paths, or AQMs
   other than a FIFO. Per-flow queues (fq_codel / cake) are outside it: it reads
   the total queue, which our per-client measurements show is wrong for
   low-rate clients under fair queueing.
5. **It labels the bottleneck's identity, not the client's experience.** It tells
   which queue is larger, not whether this client's packets are delayed; under
   fair queueing a client can sit behind a full aggregate queue with its own
   queue empty.

What we use instead: GT1 (standing queue, 5 ms target, 150 ms persistence,
hysteresis), GT2 (demand >= capacity, AQM-agnostic), GT3 (the client's own OWD and
loss, with a queue on its path), and per-client GT1 on fq_codel / cake. FlowBot
GT stays as a comparison column. A rate-normalised variant (threshold as a share of
the queue limit, or in ms) would keep FlowBot's idea; not done.
