# 2.3(b) ECT on mvfst packets

qvideo/build/_deps/mvfst-src/quic/state/TransportSettings.h:
    bool readEcnOnIngress{false};
    bool enableEcnOnEgress{false};
    // Whether to use L4S ECN (enableEcnOnEgress must be enabled)
    bool useL4sEcn{false};
qvideo sources that mention ECN: none
=> mvfst default enableEcnOnEgress=false and qvideo does not change it: video packets are Not-ECT, so an AQM's `ecn` flag never marks them (it drops instead).
