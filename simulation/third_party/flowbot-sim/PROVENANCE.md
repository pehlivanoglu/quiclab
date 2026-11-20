# Provenance: flowbot-sim

| file | source path | sha256 |
|---|---|---|
| `config_generator.py` | `flowbot/ns3/script/config_generator.py` | see below |
| `inflator.py` | `flowbot/ns3/script/inflator.py` | see below |

- Remote: https://github.com/PrinceS17/flowbot.git
- Commit: a7a21fa (local checkout HEAD, "Add init README.", 2023-10-22); both files last changed in that history
  and unmodified in the working tree. Upstream HEAD 18c3418 (2026-11-08) changes only the README.
- Copied unmodified on 2026-11-17. Our changes go in separate files, never here.
- Permission: the authors have given permission to use and modify the code (user, 2026-11-17). The
  repository itself carries no licence file.
- Use: scenario grammar and PPBP / cross parameters, for re-creating FlowBot's published blocks with our own
  reader on mainline ns-3 (not needed for stage B). The program that consumed these CSVs (submodule
  `ns3/BBR_test`, ns-3.27) is not available.
    e5ec964800c3fdca1beda8bd2a0eeab10e6dd7094b3b179a2cc4ba47deb5604a  /home/ubuntu/Research/Repos/multirelay/quiclab/simulation/third_party/flowbot-sim/config_generator.py
    28139efa890e1c2b8c3e6aaf37422bc1a11bc9cd7a98d4571b6b192b756032b9  /home/ubuntu/Research/Repos/multirelay/quiclab/simulation/third_party/flowbot-sim/inflator.py
