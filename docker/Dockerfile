# quiclab: the whole topology runs inside this one privileged container.
# Mininet hosts are network namespaces; qvideo binaries and the quiclab
# Python package are bind-mounted from the checkout at run time, so code
# changes need no image rebuild.
#
# Ubuntu 24.04's iproute2 is too old to know dualpi2, so tc/ip/ss are built
# from a pinned upstream release. The host kernel provides the qdiscs.

FROM ubuntu:24.04 AS iproute2-build

# dualpi2 userspace support landed in iproute2 6.17 (matching the kernel
# release that shipped sch_dualpi2). The build-time check below catches an
# accidental downgrade.
ARG IPROUTE2_VERSION=6.17.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        flex \
        bison \
        pkg-config \
        libmnl-dev \
        wget \
        xz-utils \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q "https://www.kernel.org/pub/linux/utils/net/iproute2/iproute2-${IPROUTE2_VERSION}.tar.xz" \
    && tar -xf "iproute2-${IPROUTE2_VERSION}.tar.xz"

RUN cd "iproute2-${IPROUTE2_VERSION}" \
    && ./configure \
    && make -j"$(nproc)" \
    && make install DESTDIR=/staging SBINDIR=/usr/sbin

# Fail the build if this tc doesn't know dualpi2. Pure userspace parse check
# (`help` prints usage before any netlink call), so no kernel support needed
# at build time.
RUN ! /staging/usr/sbin/tc qdisc add dualpi2 help 2>&1 | grep -q "Unknown qdisc"


FROM ubuntu:24.04

# mininet without its recommended Open vSwitch: links are veth pairs and
# switches are Linux bridges. Runtime libs match the qvideo host build
# (folly/fizz/mvfst/proxygen are linked statically).
RUN apt-get update && apt-get install -y --no-install-recommends \
        mininet \
        iperf3 \
        libmnl0 \
        ethtool \
        tcpdump \
        iputils-ping \
        procps \
        kmod \
        python3 \
        python3-pip \
        ca-certificates \
        libboost-context1.83.0 \
        libsodium23 \
        libgoogle-glog0v6 \
        libfmt9 \
        libgflags2.2 \
        libevent-2.1-7t64 \
        libssl3t64 \
        libzstd1 \
        libunwind8 \
        liblzma5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=iproute2-build /staging/ /

# Ubuntu ships pydantic v1; quiclab needs v2 (same pins as requirements.txt).
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

ENV PYTHONUNBUFFERED=1
