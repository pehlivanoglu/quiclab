# delaystep: where do the losses come from? (time-boxed check, 2026-11-08)

Question from Step 1: forward delay steps on pub -> router are followed by real loss
(sender newly_lost 579, receiver never-timestamped 638, router -> switch drops 509
over 24 steps). Three checks on det-delaystep-*-r1 (4 AQMs):

1. **Timing.** router -> switch drops per 0.25 s bin after the step start, forward +20 ms:
   `[0, 0, 0, 221, 5, 1, 3, 0]`; +50 ms: `[0, 3, 35, 180, 12, 52, 0, 8]`. After the step end
   (delay back to 5 ms): +20 ms `[0, 0, 0, 91, 0, 0, 1, 157]`, +50 ms `[0, 0, 0, 18, 0, 0, 0, 0]`.
   Nothing in the first 250 ms of either edge: this is **not** netem releasing held packets
   in a burst when the delay drops (that would land in bin 0 after the end).
2. **Control path.** router -> sub-ctrl (does not cross the bottleneck): 0 drops, queue <= 6 ms
   during every step. The drops are at the shared bottleneck queue.
3. **Who sends.** At the sample with the most drops (0.9-1.0 s after the step), the top sender is
   sub-d at 10-15 Mb/s over the previous 200 ms (2-3x its mean) in 11 of 15 cases: a 5 Mb/s
   keyframe (1.09 Mbit at I/P 8) leaving the sender at BBR's startup pacing rate. The same
   keyframes overflow the 100-packet queue in calm runs too (calm065: 34 % of sub-d keyframes
   drop packets, ~7.5 drops/s). Over the 36 s of forward-step windows that base rate predicts
   ~270 drops; observed 509 (reverse steps: 182, below the base rate).

Conclusion: the delaystep losses are ordinary keyframe overflow, about 2x more frequent in the
second after a forward delay increase (the larger in-flight after the RTT jump leaves less room
in the queue when the keyframe arrives); not a netem artefact, not a sender burst beyond the
keyframe. With the keyframe ratio now 4 (schema default) the effect should shrink; the
scenario comment "nothing queues" is still wrong and the rebase rule must tolerate loss
(decision 3: loss rate <= 2 p0 over the window). Open: mvfst BBR keeps app-limited flows in
STARTUP for the whole run (cwnd 577-795 kB on sub-d), which is why a keyframe can leave at
12-15 Mb/s; that is v1's "settled" mask territory and worth a line in the paper.
