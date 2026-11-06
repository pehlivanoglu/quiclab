# Shadow detector (offline replay)

The sender-side shadow early-congestion detector, as `moqx_shadow_replay`:
`scripts/det_eval.py` runs it over each client's `-acks.csv` / `-sent.csv`.

Copied verbatim on 2026-11-06 from moq-testbed `src/shadow` (github.com/pehlivanoglu/moq-testbed,
commit 7b0eb5d plus the uncommitted working-tree changes to Detector.cpp, Detector.h
and Engine.cpp that every quiclab detector result so far was scored with). Only the
pure-C++ part: Detector, Engine, Replay. Service and Observer (the live moxygen /
mvfst integration) stay in moq-testbed. This copy is now the one quiclab uses; edit it here.

```bash
cmake -S shadow -B shadow/build -DCMAKE_BUILD_TYPE=Release && cmake --build shadow/build
```

Manifest group field: flows with the same non-empty group share one
`SharedBottleneck` (aggregate delivery as capacity, a FIFO model of the
members' own sends). det_eval passes the leaf queue (`leaf_queues`), the queue
those clients really share. A group of one gets no shared context.
