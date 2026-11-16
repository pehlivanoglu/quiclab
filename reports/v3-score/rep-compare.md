# Suite v3: rep 1 vs rep 2

Flag: |r1 - r2| above the largest |r1 - r2| of the other cells of the block for that metric. Nothing is averaged.

| block | cell | metric | r1 | r2 | abs diff | largest abs diff, other cells | flag |
|---|---|---|---|---|---|---|---|
| C10 | v3-C10-hindep-s030-codel | keyframe peak p50 ms a | 5.2 | 5.0 | 0.200 | 0.400 |  |
| C10 | v3-C10-hindep-s030-fq_codel | keyframe peak p50 ms a | 3.1 | 3.1 | 0.000 | 0.400 |  |
| C10 | v3-C10-hindep-s030-pfifo | keyframe peak p50 ms a | 4.9 | 4.5 | 0.400 | 0.200 | **disagree** |
| C10 | v3-C10-hindep-s030-codel | keyframe peak p50 ms b | 6.0 | 4.7 | 1.300 | 0.500 | **disagree** |
| C10 | v3-C10-hindep-s030-fq_codel | keyframe peak p50 ms b | 3.1 | 2.7 | 0.400 | 1.300 |  |
| C10 | v3-C10-hindep-s030-pfifo | keyframe peak p50 ms b | 5.5 | 5.0 | 0.500 | 1.300 |  |
| C10 | v3-C10-hindep-s030-codel | keyframe peak p50 ms up | 9.2 | 8.4 | 0.800 | 1.000 |  |
| C10 | v3-C10-hindep-s030-fq_codel | keyframe peak p50 ms up | 10.5 | 9.5 | 1.000 | 0.800 | **disagree** |
| C10 | v3-C10-hindep-s030-pfifo | keyframe peak p50 ms up | 9.1 | 8.3 | 0.800 | 1.000 |  |
| C10 | v3-C10-hindep-s030-codel | load a | 0.711 | 0.712 | 0.001 | 0.001 |  |
| C10 | v3-C10-hindep-s030-fq_codel | load a | 0.712 | 0.713 | 0.001 | 0.001 |  |
| C10 | v3-C10-hindep-s030-pfifo | load a | 0.711 | 0.712 | 0.001 | 0.001 |  |
| C10 | v3-C10-hindep-s030-codel | load b | 0.713 | 0.714 | 0.001 | 0.002 |  |
| C10 | v3-C10-hindep-s030-fq_codel | load b | 0.714 | 0.715 | 0.001 | 0.002 |  |
| C10 | v3-C10-hindep-s030-pfifo | load b | 0.711 | 0.713 | 0.002 | 0.001 | **disagree** |
| C10 | v3-C10-hindep-s030-codel | load up | 0.712 | 0.713 | 0.001 | 0.002 |  |
| C10 | v3-C10-hindep-s030-fq_codel | load up | 0.713 | 0.714 | 0.001 | 0.002 |  |
| C10 | v3-C10-hindep-s030-pfifo | load up | 0.711 | 0.713 | 0.002 | 0.001 | **disagree** |
| C11 | v3-C11-huneven-uneven-codel | keyframe peak p50 ms A | 8.3 | 8.5 | 0.200 | - | - |
| C11 | v3-C11-huneven-uneven-pfifo | keyframe peak p50 ms A | 8.2 | 7.7 | 0.500 | - | - |
| C11 | v3-C11-huneven-uneven-codel | keyframe peak p50 ms B | 9.1 | 10.3 | 1.200 | - | - |
| C11 | v3-C11-huneven-uneven-pfifo | keyframe peak p50 ms B | 9.2 | 9.3 | 0.100 | - | - |
| C11 | v3-C11-huneven-uneven-codel | keyframe peak p50 ms C | 10.1 | 10.0 | 0.100 | - | - |
| C11 | v3-C11-huneven-uneven-pfifo | keyframe peak p50 ms C | 10.4 | 9.8 | 0.600 | - | - |
| C11 | v3-C11-huneven-uneven-codel | load A | 0.709 | 0.709 | 0.000 | - | - |
| C11 | v3-C11-huneven-uneven-pfifo | load A | 0.709 | 0.708 | 0.001 | - | - |
| C11 | v3-C11-huneven-uneven-codel | load B | 0.709 | 0.707 | 0.002 | - | - |
| C11 | v3-C11-huneven-uneven-pfifo | load B | 0.708 | 0.707 | 0.001 | - | - |
| C11 | v3-C11-huneven-uneven-codel | load C | 0.711 | 0.709 | 0.002 | - | - |
| C11 | v3-C11-huneven-uneven-pfifo | load C | 0.709 | 0.709 | 0.000 | - | - |
| C12 | v3-C12-amixed-access-codel | keyframe peak p50 ms main | 8.5 | 9.0 | 0.500 | 0.500 |  |
| C12 | v3-C12-amixed-access-fq_codel | keyframe peak p50 ms main | 11.1 | 10.7 | 0.400 | 0.500 |  |
| C12 | v3-C12-amixed-access-pfifo | keyframe peak p50 ms main | 8.8 | 9.3 | 0.500 | 0.500 |  |
| C12 | v3-C12-amixed-access-pie | keyframe peak p50 ms main | 8.2 | 8.2 | 0.000 | 0.500 |  |
| C12 | v3-C12-amixed-access-codel | load main | 0.691 | 0.693 | 0.002 | 0.002 |  |
| C12 | v3-C12-amixed-access-fq_codel | load main | 0.691 | 0.693 | 0.002 | 0.002 |  |
| C12 | v3-C12-amixed-access-pfifo | load main | 0.691 | 0.69 | 0.001 | 0.002 |  |
| C12 | v3-C12-amixed-access-pie | load main | 0.69 | 0.691 | 0.001 | 0.002 |  |
| C13 | v3-C13-llong-s030-codel | keyframe peak p50 ms a | 6.0 | 5.3 | 0.700 | - | - |
| C13 | v3-C13-llong-s030-pfifo | keyframe peak p50 ms a | 5.6 | 5.0 | 0.600 | - | - |
| C13 | v3-C13-llong-s030-codel | keyframe peak p50 ms b | 6.2 | 5.1 | 1.100 | - | - |
| C13 | v3-C13-llong-s030-pfifo | keyframe peak p50 ms b | 5.9 | 5.4 | 0.500 | - | - |
| C13 | v3-C13-llong-s030-codel | keyframe peak p50 ms up | 10.1 | 9.0 | 1.100 | - | - |
| C13 | v3-C13-llong-s030-pfifo | keyframe peak p50 ms up | 9.8 | 8.8 | 1.000 | - | - |
| C13 | v3-C13-llong-s030-codel | load a | 0.712 | 0.714 | 0.002 | - | - |
| C13 | v3-C13-llong-s030-pfifo | load a | 0.709 | 0.709 | 0.000 | - | - |
| C13 | v3-C13-llong-s030-codel | load b | 0.711 | 0.711 | 0.000 | - | - |
| C13 | v3-C13-llong-s030-pfifo | load b | 0.705 | 0.709 | 0.004 | - | - |
| C13 | v3-C13-llong-s030-codel | load up | 0.712 | 0.711 | 0.001 | - | - |
| C13 | v3-C13-llong-s030-pfifo | load up | 0.708 | 0.707 | 0.001 | - | - |
| C14 | v3-C14-rrev-rev-fq_codel | keyframe peak p50 ms main | 12.1 | 11.4 | 0.700 | - | - |
| C14 | v3-C14-rrev-rev-pfifo | keyframe peak p50 ms main | 9.0 | 9.2 | 0.200 | - | - |
| C14 | v3-C14-rrev-rev-fq_codel | load main | 0.71 | 0.709 | 0.001 | - | - |
| C14 | v3-C14-rrev-rev-pfifo | load main | 0.708 | 0.708 | 0.000 | - | - |
| C15 | v3-C15-nloss-s030u070-codel | keyframe peak p50 ms main | 16.0 | 12.2 | 3.800 | - | - |
| C15 | v3-C15-nloss-s030u070-pfifo | keyframe peak p50 ms main | 15.8 | 14.3 | 1.500 | - | - |
| C15 | v3-C15-nloss-s030u070-codel | load main | 0.704 | 0.708 | 0.004 | - | - |
| C15 | v3-C15-nloss-s030u070-pfifo | load main | 0.705 | 0.708 | 0.003 | - | - |
| C1a | v3-C1a-calm-legacy-codel | keyframe peak p50 ms main | 71.9 | 69.2 | 2.700 | 5.500 |  |
| C1a | v3-C1a-calm-legacy-pfifo | keyframe peak p50 ms main | 45.9 | 47.0 | 1.100 | 5.500 |  |
| C1a | v3-C1a-calm-s010u070-codel | keyframe peak p50 ms main | 6.3 | 5.9 | 0.400 | 5.500 |  |
| C1a | v3-C1a-calm-s010u070-pfifo | keyframe peak p50 ms main | 6.1 | 6.0 | 0.100 | 5.500 |  |
| C1a | v3-C1a-calm-s010u085-codel | keyframe peak p50 ms main | 8.8 | 9.0 | 0.200 | 5.500 |  |
| C1a | v3-C1a-calm-s010u085-pfifo | keyframe peak p50 ms main | 9.1 | 8.5 | 0.600 | 5.500 |  |
| C1a | v3-C1a-calm-s030u050-codel | keyframe peak p50 ms main | 13.7 | 13.4 | 0.300 | 5.500 |  |
| C1a | v3-C1a-calm-s030u050-pfifo | keyframe peak p50 ms main | 14.5 | 13.2 | 1.300 | 5.500 |  |
| C1a | v3-C1a-calm-s030u070-codel | keyframe peak p50 ms main | 21.8 | 21.2 | 0.600 | 5.500 |  |
| C1a | v3-C1a-calm-s030u070-pfifo | keyframe peak p50 ms main | 23.2 | 21.2 | 2.000 | 5.500 |  |
| C1a | v3-C1a-calm-s030u085-codel | keyframe peak p50 ms main | 28.3 | 27.9 | 0.400 | 5.500 |  |
| C1a | v3-C1a-calm-s030u085-pfifo | keyframe peak p50 ms main | 28.3 | 27.5 | 0.800 | 5.500 |  |
| C1a | v3-C1a-calm-s065u050-codel | keyframe peak p50 ms main | 35.7 | 32.5 | 3.200 | 5.500 |  |
| C1a | v3-C1a-calm-s065u050-pfifo | keyframe peak p50 ms main | 35.0 | 32.7 | 2.300 | 5.500 |  |
| C1a | v3-C1a-calm-s065u070-codel | keyframe peak p50 ms main | 52.0 | 48.5 | 3.500 | 5.500 |  |
| C1a | v3-C1a-calm-s065u070-pfifo | keyframe peak p50 ms main | 33.6 | 34.3 | 0.700 | 5.500 |  |
| C1a | v3-C1a-calm-s065u085-codel | keyframe peak p50 ms main | 53.7 | 59.2 | 5.500 | 3.500 | **disagree** |
| C1a | v3-C1a-calm-s065u085-pfifo | keyframe peak p50 ms main | 29.8 | 28.2 | 1.600 | 5.500 |  |
| C1a | v3-C1a-calm-legacy-codel | load main | 0.669 | 0.667 | 0.002 | 0.003 |  |
| C1a | v3-C1a-calm-legacy-pfifo | load main | 0.669 | 0.667 | 0.002 | 0.003 |  |
| C1a | v3-C1a-calm-s010u070-codel | load main | 0.702 | 0.704 | 0.002 | 0.003 |  |
| C1a | v3-C1a-calm-s010u070-pfifo | load main | 0.702 | 0.704 | 0.002 | 0.003 |  |
| C1a | v3-C1a-calm-s010u085-codel | load main | 0.852 | 0.855 | 0.003 | 0.002 | **disagree** |
| C1a | v3-C1a-calm-s010u085-pfifo | load main | 0.852 | 0.854 | 0.002 | 0.003 |  |
| C1a | v3-C1a-calm-s030u050-codel | load main | 0.504 | 0.505 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s030u050-pfifo | load main | 0.504 | 0.505 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s030u070-codel | load main | 0.706 | 0.707 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s030u070-pfifo | load main | 0.706 | 0.707 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s030u085-codel | load main | 0.857 | 0.859 | 0.002 | 0.003 |  |
| C1a | v3-C1a-calm-s030u085-pfifo | load main | 0.857 | 0.859 | 0.002 | 0.003 |  |
| C1a | v3-C1a-calm-s065u050-codel | load main | 0.511 | 0.51 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s065u050-pfifo | load main | 0.511 | 0.51 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s065u070-codel | load main | 0.715 | 0.714 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s065u070-pfifo | load main | 0.715 | 0.714 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s065u085-codel | load main | 0.868 | 0.867 | 0.001 | 0.003 |  |
| C1a | v3-C1a-calm-s065u085-pfifo | load main | 0.868 | 0.867 | 0.001 | 0.003 |  |
| C1b | v3-C1b-calm-tree16-pfifo | keyframe peak p50 ms A | 7.3 | 6.6 | 0.700 | - | - |
| C1b | v3-C1b-calm-uneven-pfifo | keyframe peak p50 ms A | 22.1 | 21.4 | 0.700 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | keyframe peak p50 ms B | 7.4 | 7.0 | 0.400 | - | - |
| C1b | v3-C1b-calm-uneven-pfifo | keyframe peak p50 ms B | 21.9 | 21.1 | 0.800 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | keyframe peak p50 ms C | 7.2 | 6.4 | 0.800 | - | - |
| C1b | v3-C1b-calm-uneven-pfifo | keyframe peak p50 ms C | 21.5 | 21.1 | 0.400 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | keyframe peak p50 ms D | 7.0 | 6.9 | 0.100 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | keyframe peak p50 ms X | 12.0 | 10.9 | 1.100 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | keyframe peak p50 ms Y | 10.8 | 11.1 | 0.300 | - | - |
| C1b | v3-C1b-calm-split4-pfifo | keyframe peak p50 ms a | 11.0 | 11.1 | 0.100 | - | - |
| C1b | v3-C1b-calm-split4-pfifo | keyframe peak p50 ms b | 11.5 | 10.7 | 0.800 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | keyframe peak p50 ms root | 21.5 | 21.1 | 0.400 | - | - |
| C1b | v3-C1b-calm-split4-pfifo | keyframe peak p50 ms up | 22.7 | 20.8 | 1.900 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | load A | 0.71 | 0.711 | 0.001 | - | - |
| C1b | v3-C1b-calm-uneven-pfifo | load A | 0.705 | 0.707 | 0.002 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | load B | 0.709 | 0.71 | 0.001 | - | - |
| C1b | v3-C1b-calm-uneven-pfifo | load B | 0.709 | 0.707 | 0.002 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | load C | 0.712 | 0.71 | 0.002 | - | - |
| C1b | v3-C1b-calm-uneven-pfifo | load C | 0.707 | 0.708 | 0.001 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | load D | 0.709 | 0.708 | 0.001 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | load X | 0.711 | 0.71 | 0.001 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | load Y | 0.71 | 0.71 | 0.000 | - | - |
| C1b | v3-C1b-calm-split4-pfifo | load a | 0.708 | 0.707 | 0.001 | - | - |
| C1b | v3-C1b-calm-split4-pfifo | load b | 0.707 | 0.707 | 0.000 | - | - |
| C1b | v3-C1b-calm-tree16-pfifo | load root | 0.708 | 0.71 | 0.002 | - | - |
| C1b | v3-C1b-calm-split4-pfifo | load up | 0.706 | 0.707 | 0.001 | - | - |
| C2 | v3-C2-sburst-s030u070-cake | keyframe peak p50 ms main | 15.8 | 13.4 | 2.400 | 3.800 |  |
| C2 | v3-C2-sburst-s030u070-codel | keyframe peak p50 ms main | 8.9 | 8.3 | 0.600 | 3.800 |  |
| C2 | v3-C2-sburst-s030u070-fq_codel | keyframe peak p50 ms main | 10.2 | 10.1 | 0.100 | 3.800 |  |
| C2 | v3-C2-sburst-s030u070-pfifo | keyframe peak p50 ms main | 8.5 | 7.9 | 0.600 | 3.800 |  |
| C2 | v3-C2-sburst-s030u070-pie | keyframe peak p50 ms main | 6.8 | 10.6 | 3.800 | 2.400 | **disagree** |
| C2 | v3-C2-sburst-s030u070-red | keyframe peak p50 ms main | 8.8 | 8.1 | 0.700 | 3.800 |  |
| C2 | v3-C2-sburst-s030u070-cake | load main | 0.706 | 0.706 | 0.000 | 0.001 |  |
| C2 | v3-C2-sburst-s030u070-codel | load main | 0.71 | 0.709 | 0.001 | 0.001 |  |
| C2 | v3-C2-sburst-s030u070-fq_codel | load main | 0.712 | 0.712 | 0.000 | 0.001 |  |
| C2 | v3-C2-sburst-s030u070-pfifo | load main | 0.709 | 0.709 | 0.000 | 0.001 |  |
| C2 | v3-C2-sburst-s030u070-pie | load main | 0.707 | 0.708 | 0.001 | 0.001 |  |
| C2 | v3-C2-sburst-s030u070-red | load main | 0.707 | 0.707 | 0.000 | 0.001 |  |
| C3a | v3-C3a-sburst-s010u070-codel | keyframe peak p50 ms main | 1.8 | 1.8 | 0.000 | 1.500 |  |
| C3a | v3-C3a-sburst-s010u070-pfifo | keyframe peak p50 ms main | 1.6 | 1.5 | 0.100 | 1.500 |  |
| C3a | v3-C3a-sburst-s065u070-codel | keyframe peak p50 ms main | 24.4 | 22.9 | 1.500 | 0.300 | **disagree** |
| C3a | v3-C3a-sburst-s065u070-pfifo | keyframe peak p50 ms main | 23.9 | 23.6 | 0.300 | 1.500 |  |
| C3a | v3-C3a-sburst-s010u070-codel | load main | 0.703 | 0.705 | 0.002 | 0.002 |  |
| C3a | v3-C3a-sburst-s010u070-pfifo | load main | 0.703 | 0.703 | 0.000 | 0.002 |  |
| C3a | v3-C3a-sburst-s065u070-codel | load main | 0.721 | 0.723 | 0.002 | 0.002 |  |
| C3a | v3-C3a-sburst-s065u070-pfifo | load main | 0.721 | 0.72 | 0.001 | 0.002 |  |
| C3b | v3-C3b-sburst-legacy-pfifo | keyframe peak p50 ms main | 34.7 | 31.4 | 3.300 | - | - |
| C3b | v3-C3b-sburst-legacy-pfifo | load main | 0.677 | 0.678 | 0.001 | - | - |
| C4 | v3-C4-sramp-s030u070-codel | keyframe peak p50 ms main | 8.6 | 8.4 | 0.200 | 2.800 |  |
| C4 | v3-C4-sramp-s030u070-fq_codel | keyframe peak p50 ms main | 9.9 | 10.3 | 0.400 | 2.800 |  |
| C4 | v3-C4-sramp-s030u070-pfifo | keyframe peak p50 ms main | 8.6 | 7.0 | 1.600 | 2.800 |  |
| C4 | v3-C4-sramp-s030u070-pie | keyframe peak p50 ms main | 7.4 | 10.2 | 2.800 | 1.600 | **disagree** |
| C4 | v3-C4-sramp-s030u070-codel | load main | 0.708 | 0.712 | 0.004 | 0.007 |  |
| C4 | v3-C4-sramp-s030u070-fq_codel | load main | 0.71 | 0.717 | 0.007 | 0.004 | **disagree** |
| C4 | v3-C4-sramp-s030u070-pfifo | load main | 0.707 | 0.709 | 0.002 | 0.007 |  |
| C4 | v3-C4-sramp-s030u070-pie | load main | 0.707 | 0.709 | 0.002 | 0.007 |  |
| C5 | v3-C5-stcp-s030u070-codel | keyframe peak p50 ms main | 7.9 | 9.2 | 1.300 | 0.600 | **disagree** |
| C5 | v3-C5-stcp-s030u070-fq_codel | keyframe peak p50 ms main | 13.7 | 13.2 | 0.500 | 1.300 |  |
| C5 | v3-C5-stcp-s030u070-pfifo | keyframe peak p50 ms main | 6.9 | 7.0 | 0.100 | 1.300 |  |
| C5 | v3-C5-stcp-s030u070-pie | keyframe peak p50 ms main | 7.3 | 6.7 | 0.600 | 1.300 |  |
| C5 | v3-C5-stcp-s030u070-codel | load main | 0.706 | 0.707 | 0.001 | 0.001 |  |
| C5 | v3-C5-stcp-s030u070-fq_codel | load main | 0.707 | 0.707 | 0.000 | 0.001 |  |
| C5 | v3-C5-stcp-s030u070-pfifo | load main | 0.707 | 0.707 | 0.000 | 0.001 |  |
| C5 | v3-C5-stcp-s030u070-pie | load main | 0.706 | 0.707 | 0.001 | 0.001 |  |
| C6 | v3-C6-sjoin-s030u070-codel | keyframe peak p50 ms main | 13.5 | 20.0 | 6.500 | 0.700 | **disagree** |
| C6 | v3-C6-sjoin-s030u070-fq_codel | keyframe peak p50 ms main | 22.6 | 21.9 | 0.700 | 6.500 |  |
| C6 | v3-C6-sjoin-s030u070-pfifo | keyframe peak p50 ms main | 7.2 | 6.9 | 0.300 | 6.500 |  |
| C6 | v3-C6-sjoin-s030u070-codel | load main | 0.705 | 0.707 | 0.002 | 0.002 |  |
| C6 | v3-C6-sjoin-s030u070-fq_codel | load main | 0.705 | 0.707 | 0.002 | 0.002 |  |
| C6 | v3-C6-sjoin-s030u070-pfifo | load main | 0.705 | 0.707 | 0.002 | 0.002 |  |
| C7 | v3-C7-hhier-s030-codel | keyframe peak p50 ms a | 5.5 | 5.4 | 0.100 | 0.400 |  |
| C7 | v3-C7-hhier-s030-fq_codel | keyframe peak p50 ms a | 2.9 | 3.0 | 0.100 | 0.400 |  |
| C7 | v3-C7-hhier-s030-pfifo | keyframe peak p50 ms a | 5.2 | 5.4 | 0.200 | 0.400 |  |
| C7 | v3-C7-hhier-s030-pie | keyframe peak p50 ms a | 5.6 | 5.2 | 0.400 | 0.200 | **disagree** |
| C7 | v3-C7-hhier-s030-codel | keyframe peak p50 ms b | 5.4 | 5.6 | 0.200 | 0.500 |  |
| C7 | v3-C7-hhier-s030-fq_codel | keyframe peak p50 ms b | 2.8 | 2.8 | 0.000 | 0.500 |  |
| C7 | v3-C7-hhier-s030-pfifo | keyframe peak p50 ms b | 5.6 | 5.1 | 0.500 | 0.200 | **disagree** |
| C7 | v3-C7-hhier-s030-pie | keyframe peak p50 ms b | 5.0 | 5.1 | 0.100 | 0.500 |  |
| C7 | v3-C7-hhier-s030-codel | keyframe peak p50 ms up | 9.5 | 9.4 | 0.100 | 0.400 |  |
| C7 | v3-C7-hhier-s030-fq_codel | keyframe peak p50 ms up | 10.2 | 10.3 | 0.100 | 0.400 |  |
| C7 | v3-C7-hhier-s030-pfifo | keyframe peak p50 ms up | 8.8 | 8.6 | 0.200 | 0.400 |  |
| C7 | v3-C7-hhier-s030-pie | keyframe peak p50 ms up | 8.4 | 8.0 | 0.400 | 0.200 | **disagree** |
| C7 | v3-C7-hhier-s030-codel | load a | 0.711 | 0.71 | 0.001 | 0.001 |  |
| C7 | v3-C7-hhier-s030-fq_codel | load a | 0.712 | 0.711 | 0.001 | 0.001 |  |
| C7 | v3-C7-hhier-s030-pfifo | load a | 0.71 | 0.709 | 0.001 | 0.001 |  |
| C7 | v3-C7-hhier-s030-pie | load a | 0.709 | 0.708 | 0.001 | 0.001 |  |
| C7 | v3-C7-hhier-s030-codel | load b | 0.712 | 0.711 | 0.001 | 0.002 |  |
| C7 | v3-C7-hhier-s030-fq_codel | load b | 0.712 | 0.712 | 0.000 | 0.002 |  |
| C7 | v3-C7-hhier-s030-pfifo | load b | 0.711 | 0.709 | 0.002 | 0.001 | **disagree** |
| C7 | v3-C7-hhier-s030-pie | load b | 0.709 | 0.709 | 0.000 | 0.002 |  |
| C7 | v3-C7-hhier-s030-codel | load up | 0.711 | 0.71 | 0.001 | 0.001 |  |
| C7 | v3-C7-hhier-s030-fq_codel | load up | 0.711 | 0.712 | 0.001 | 0.001 |  |
| C7 | v3-C7-hhier-s030-pfifo | load up | 0.71 | 0.709 | 0.001 | 0.001 |  |
| C7 | v3-C7-hhier-s030-pie | load up | 0.709 | 0.709 | 0.000 | 0.001 |  |
| C8 | v3-C8-hhier-s065-pfifo | keyframe peak p50 ms a | 8.8 | 9.8 | 1.000 | - | - |
| C8 | v3-C8-hhier-s065-pfifo | keyframe peak p50 ms b | 8.7 | 9.0 | 0.300 | - | - |
| C8 | v3-C8-hhier-s065-pfifo | keyframe peak p50 ms up | 24.7 | 25.3 | 0.600 | - | - |
| C8 | v3-C8-hhier-s065-pfifo | load a | 0.721 | 0.72 | 0.001 | - | - |
| C8 | v3-C8-hhier-s065-pfifo | load b | 0.721 | 0.721 | 0.000 | - | - |
| C8 | v3-C8-hhier-s065-pfifo | load up | 0.72 | 0.721 | 0.001 | - | - |
| C9 | v3-C9-hdepth-tree16-codel | keyframe peak p50 ms A | 5.2 | 5.4 | 0.200 | 0.200 |  |
| C9 | v3-C9-hdepth-tree16-fq_codel | keyframe peak p50 ms A | 3.6 | 3.7 | 0.100 | 0.200 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | keyframe peak p50 ms A | 5.3 | 5.1 | 0.200 | 0.200 |  |
| C9 | v3-C9-hdepth-tree16-codel | keyframe peak p50 ms B | 5.4 | 5.5 | 0.100 | 0.100 |  |
| C9 | v3-C9-hdepth-tree16-fq_codel | keyframe peak p50 ms B | 3.4 | 3.4 | 0.000 | 0.100 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | keyframe peak p50 ms B | 5.2 | 5.3 | 0.100 | 0.100 |  |
| C9 | v3-C9-hdepth-tree16-codel | keyframe peak p50 ms C | 5.8 | 5.3 | 0.500 | 0.100 | **disagree** |
| C9 | v3-C9-hdepth-tree16-fq_codel | keyframe peak p50 ms C | 3.6 | 3.7 | 0.100 | 0.500 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | keyframe peak p50 ms C | 5.5 | 5.5 | 0.000 | 0.500 |  |
| C9 | v3-C9-hdepth-tree16-codel | keyframe peak p50 ms D | 6.1 | 4.9 | 1.200 | 0.300 | **disagree** |
| C9 | v3-C9-hdepth-tree16-fq_codel | keyframe peak p50 ms D | 3.6 | 3.3 | 0.300 | 1.200 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | keyframe peak p50 ms D | 5.5 | 5.3 | 0.200 | 1.200 |  |
| C9 | v3-C9-hdepth-tree16-codel | keyframe peak p50 ms X | 6.3 | 6.5 | 0.200 | 0.100 | **disagree** |
| C9 | v3-C9-hdepth-tree16-fq_codel | keyframe peak p50 ms X | 3.1 | 3.0 | 0.100 | 0.200 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | keyframe peak p50 ms X | 6.2 | 6.1 | 0.100 | 0.200 |  |
| C9 | v3-C9-hdepth-tree16-codel | keyframe peak p50 ms Y | 6.5 | 6.2 | 0.300 | 0.400 |  |
| C9 | v3-C9-hdepth-tree16-fq_codel | keyframe peak p50 ms Y | 3.0 | 3.1 | 0.100 | 0.400 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | keyframe peak p50 ms Y | 6.0 | 6.4 | 0.400 | 0.300 | **disagree** |
| C9 | v3-C9-hdepth-tree16-codel | keyframe peak p50 ms root | 10.9 | 11.0 | 0.100 | 0.500 |  |
| C9 | v3-C9-hdepth-tree16-fq_codel | keyframe peak p50 ms root | 11.9 | 11.6 | 0.300 | 0.500 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | keyframe peak p50 ms root | 10.6 | 11.1 | 0.500 | 0.300 | **disagree** |
| C9 | v3-C9-hdepth-tree16-codel | load A | 0.712 | 0.714 | 0.002 | 0.001 | **disagree** |
| C9 | v3-C9-hdepth-tree16-fq_codel | load A | 0.711 | 0.711 | 0.000 | 0.002 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | load A | 0.711 | 0.712 | 0.001 | 0.002 |  |
| C9 | v3-C9-hdepth-tree16-codel | load B | 0.712 | 0.711 | 0.001 | 0.000 | **disagree** |
| C9 | v3-C9-hdepth-tree16-fq_codel | load B | 0.71 | 0.71 | 0.000 | 0.001 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | load B | 0.711 | 0.711 | 0.000 | 0.001 |  |
| C9 | v3-C9-hdepth-tree16-codel | load C | 0.714 | 0.714 | 0.000 | 0.001 |  |
| C9 | v3-C9-hdepth-tree16-fq_codel | load C | 0.712 | 0.711 | 0.001 | 0.000 | **disagree** |
| C9 | v3-C9-hdepth-tree16-pfifo | load C | 0.712 | 0.712 | 0.000 | 0.001 |  |
| C9 | v3-C9-hdepth-tree16-codel | load D | 0.712 | 0.71 | 0.002 | 0.001 | **disagree** |
| C9 | v3-C9-hdepth-tree16-fq_codel | load D | 0.71 | 0.709 | 0.001 | 0.002 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | load D | 0.711 | 0.71 | 0.001 | 0.002 |  |
| C9 | v3-C9-hdepth-tree16-codel | load X | 0.712 | 0.712 | 0.000 | 0.000 |  |
| C9 | v3-C9-hdepth-tree16-fq_codel | load X | 0.71 | 0.71 | 0.000 | 0.000 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | load X | 0.71 | 0.71 | 0.000 | 0.000 |  |
| C9 | v3-C9-hdepth-tree16-codel | load Y | 0.712 | 0.713 | 0.001 | 0.002 |  |
| C9 | v3-C9-hdepth-tree16-fq_codel | load Y | 0.71 | 0.711 | 0.001 | 0.002 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | load Y | 0.71 | 0.712 | 0.002 | 0.001 | **disagree** |
| C9 | v3-C9-hdepth-tree16-codel | load root | 0.711 | 0.712 | 0.001 | 0.001 |  |
| C9 | v3-C9-hdepth-tree16-fq_codel | load root | 0.709 | 0.71 | 0.001 | 0.001 |  |
| C9 | v3-C9-hdepth-tree16-pfifo | load root | 0.71 | 0.711 | 0.001 | 0.001 |  |
| M1 | v3-M1-sburst-q100-pfifo | keyframe peak p50 ms main | 9.3 | 7.9 | 1.400 | - | - |
| M1 | v3-M1-sburst-q300-pfifo | keyframe peak p50 ms main | 9.1 | 8.4 | 0.700 | - | - |
| M1 | v3-M1-sburst-q100-pfifo | load main | 0.71 | 0.709 | 0.001 | - | - |
| M1 | v3-M1-sburst-q300-pfifo | load main | 0.712 | 0.711 | 0.001 | - | - |
| M10 | v3-M10-sburst-ip2-pfifo | keyframe peak p50 ms main | 4.1 | 3.9 | 0.200 | - | - |
| M10 | v3-M10-sburst-ip8-pfifo | keyframe peak p50 ms main | 12.0 | 11.6 | 0.400 | - | - |
| M10 | v3-M10-sburst-ip2-pfifo | load main | 0.712 | 0.709 | 0.003 | - | - |
| M10 | v3-M10-sburst-ip8-pfifo | load main | 0.709 | 0.707 | 0.002 | - | - |
| M11 | v3-M11-sburst-bw4x1-pfifo | keyframe peak p50 ms main | 31.5 | 31.9 | 0.400 | 1.800 |  |
| M11 | v3-M11-sburst-bw4x12-pfifo | keyframe peak p50 ms main | 18.2 | 16.4 | 1.800 | 0.400 | **disagree** |
| M11 | v3-M11-sburst-bw4x8-pfifo | keyframe peak p50 ms main | 16.2 | 15.9 | 0.300 | 1.800 |  |
| M11 | v3-M11-sburst-bw4x1-pfifo | load main | 0.73 | 0.729 | 0.001 | 0.001 |  |
| M11 | v3-M11-sburst-bw4x12-pfifo | load main | 0.719 | 0.72 | 0.001 | 0.001 |  |
| M11 | v3-M11-sburst-bw4x8-pfifo | load main | 0.717 | 0.717 | 0.000 | 0.001 |  |
| M12 | v3-M12-sburst-jitfwd-pfifo | keyframe peak p50 ms main | 9.7 | 8.4 | 1.300 | - | - |
| M12 | v3-M12-sburst-jitrev-pfifo | keyframe peak p50 ms main | 11.5 | 10.9 | 0.600 | - | - |
| M12 | v3-M12-sburst-jitfwd-pfifo | load main | 0.711 | 0.708 | 0.003 | - | - |
| M12 | v3-M12-sburst-jitrev-pfifo | load main | 0.708 | 0.708 | 0.000 | - | - |
| M13 | v3-M13-sburst-copa-codel | keyframe peak p50 ms main | 22.8 | 22.5 | 0.300 | - | - |
| M13 | v3-M13-sburst-copa-pfifo | keyframe peak p50 ms main | 22.4 | 22.5 | 0.100 | - | - |
| M13 | v3-M13-sburst-copa-codel | load main | 0.706 | 0.706 | 0.000 | - | - |
| M13 | v3-M13-sburst-copa-pfifo | load main | 0.706 | 0.706 | 0.000 | - | - |
| M14 | v3-M14-ssparse-s030u070-pfifo | keyframe peak p50 ms main | 10.1 | 9.7 | 0.400 | - | - |
| M14 | v3-M14-ssparse-s030u070-pfifo | load main | 0.707 | 0.707 | 0.000 | - | - |
| M2 | v3-M2-sburst-capdrop-codel | keyframe peak p50 ms main | 9.9 | 8.4 | 1.500 | - | - |
| M2 | v3-M2-sburst-capdrop-pfifo | keyframe peak p50 ms main | 8.8 | 8.5 | 0.300 | - | - |
| M2 | v3-M2-sburst-capdrop-codel | load main | 0.709 | 0.708 | 0.001 | - | - |
| M2 | v3-M2-sburst-capdrop-pfifo | load main | 0.709 | 0.71 | 0.001 | - | - |
| M3 | v3-M3-sburst-bgbursty-codel | keyframe peak p50 ms main | 6.3 | 8.0 | 1.700 | 1.300 | **disagree** |
| M3 | v3-M3-sburst-bgbursty-pfifo | keyframe peak p50 ms main | 6.0 | 7.3 | 1.300 | 1.700 |  |
| M3 | v3-M3-sburst-bgmix-codel | keyframe peak p50 ms main | 8.0 | 7.0 | 1.000 | 1.700 |  |
| M3 | v3-M3-sburst-bgmix-pfifo | keyframe peak p50 ms main | 7.2 | 6.4 | 0.800 | 1.700 |  |
| M3 | v3-M3-sburst-bgbursty-codel | load main | 0.651 | 0.714 | 0.063 | 0.063 |  |
| M3 | v3-M3-sburst-bgbursty-pfifo | load main | 0.65 | 0.713 | 0.063 | 0.063 |  |
| M3 | v3-M3-sburst-bgmix-codel | load main | 0.712 | 0.712 | 0.000 | 0.063 |  |
| M3 | v3-M3-sburst-bgmix-pfifo | load main | 0.713 | 0.712 | 0.001 | 0.063 |  |
| M4 | v3-M4-sburst-rttwide-pfifo | keyframe peak p50 ms main | 5.5 | 5.6 | 0.100 | 0.700 |  |
| M4 | v3-M4-sburst-rttx05-pfifo | keyframe peak p50 ms main | 8.3 | 7.6 | 0.700 | 0.400 | **disagree** |
| M4 | v3-M4-sburst-rttx4-pfifo | keyframe peak p50 ms main | 3.4 | 3.0 | 0.400 | 0.700 |  |
| M4 | v3-M4-sburst-rttwide-pfifo | load main | 0.708 | 0.71 | 0.002 | 0.002 |  |
| M4 | v3-M4-sburst-rttx05-pfifo | load main | 0.708 | 0.708 | 0.000 | 0.002 |  |
| M4 | v3-M4-sburst-rttx4-pfifo | load main | 0.71 | 0.708 | 0.002 | 0.002 |  |
| M5 | v3-M5-sburst-fps15-codel | keyframe peak p50 ms main | 11.7 | 11.4 | 0.300 | 0.900 |  |
| M5 | v3-M5-sburst-fps15-pfifo | keyframe peak p50 ms main | 11.6 | 10.7 | 0.900 | 0.800 | **disagree** |
| M5 | v3-M5-sburst-fps60-codel | keyframe peak p50 ms main | 4.9 | 4.4 | 0.500 | 0.900 |  |
| M5 | v3-M5-sburst-fps60-pfifo | keyframe peak p50 ms main | 4.9 | 4.1 | 0.800 | 0.900 |  |
| M5 | v3-M5-sburst-fps15-codel | load main | 0.709 | 0.709 | 0.000 | 0.004 |  |
| M5 | v3-M5-sburst-fps15-pfifo | load main | 0.709 | 0.707 | 0.002 | 0.004 |  |
| M5 | v3-M5-sburst-fps60-codel | load main | 0.713 | 0.709 | 0.004 | 0.003 | **disagree** |
| M5 | v3-M5-sburst-fps60-pfifo | load main | 0.712 | 0.709 | 0.003 | 0.004 |  |
| M6 | v3-M6-calm-stag-pfifo | keyframe peak p50 ms main | 3.7 | 3.8 | 0.100 | - | - |
| M6 | v3-M6-sburst-stag-pfifo | keyframe peak p50 ms main | 1.9 | 1.8 | 0.100 | - | - |
| M6 | v3-M6-calm-stag-pfifo | load main | 0.706 | 0.707 | 0.001 | - | - |
| M6 | v3-M6-sburst-stag-pfifo | load main | 0.71 | 0.709 | 0.001 | - | - |
| M7 | v3-M7-hhier-noroot-pfifo | keyframe peak p50 ms a | 9.2 | 9.0 | 0.200 | - | - |
| M7 | v3-M7-hhier-noroot-pfifo | keyframe peak p50 ms b | 8.9 | 8.7 | 0.200 | - | - |
| M7 | v3-M7-hhier-noroot-pfifo | load a | 0.71 | 0.709 | 0.001 | - | - |
| M7 | v3-M7-hhier-noroot-pfifo | load b | 0.709 | 0.71 | 0.001 | - | - |
| M8 | v3-M8-hhier-mixab-mixab | keyframe peak p50 ms a | 5.1 | 5.2 | 0.100 | - | - |
| M8 | v3-M8-hhier-mixab-mixab | keyframe peak p50 ms b | 5.9 | 5.6 | 0.300 | - | - |
| M8 | v3-M8-hhier-mixab-mixab | keyframe peak p50 ms up | 9.3 | 9.3 | 0.000 | - | - |
| M8 | v3-M8-hhier-mixab-mixab | load a | 0.71 | 0.709 | 0.001 | - | - |
| M8 | v3-M8-hhier-mixab-mixab | load b | 0.712 | 0.711 | 0.001 | - | - |
| M8 | v3-M8-hhier-mixab-mixab | load up | 0.711 | 0.71 | 0.001 | - | - |
| M9 | v3-M9-sstress-s030u070-codel | keyframe peak p50 ms main | 9.6 | 8.4 | 1.200 | - | - |
| M9 | v3-M9-sstress-s030u070-pfifo | keyframe peak p50 ms main | 6.5 | 6.6 | 0.100 | - | - |
| M9 | v3-M9-sstress-s030u070-codel | load main | 0.703 | 0.707 | 0.004 | - | - |
| M9 | v3-M9-sstress-s030u070-pfifo | load main | 0.702 | 0.7 | 0.002 | - | - |

## Per-client pacing and emission of the flagged cells (r1 / r2)

### v3-C10-hindep-s030-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| a1 | 1000 | 4.17 / 4.16 | 23.53 / 23.81 | 0.0 / 0.0 |
| a2 | 1000 | 3.7 / 3.41 | 27.17 / 29.04 | 0.0 / 0.0 |
| a3 | 2500 | 10.38 / 10.11 | 28.67 / 29.27 | 4.84 / 4.95 |
| a4 | 5000 | 17.52 / 18.51 | 34.53 / 33.95 | 7.01 / 7.62 |
| b1 | 1000 | 5.08 / 4.41 | 19.38 / 22.55 | 0.0 / 0.0 |
| b2 | 1000 | 3.88 / 3.91 | 25.36 / 25.34 | 0.0 / 0.0 |
| b3 | 2500 | 8.99 / 9.82 | 32.05 / 30.48 | 5.55 / 5.07 |
| b4 | 5000 | 19.89 / 18.51 | 32.9 / 34.21 | 6.55 / 7.54 |
| sub-ctrl | 2500 | 72.01 / 76.4 | 4.54 / 3.87 | 0.0 / 0.0 |

### v3-C10-hindep-s030-fq_codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| a1 | 1000 | 64.54 / 45.97 | 1.28 / 2.4 | 0.0 / 0.0 |
| a2 | 1000 | 37.33 / 6.59 | 2.85 / 16.04 | 0.0 / 0.0 |
| a3 | 2500 | 11.2 / 9.51 | 26.37 / 31.53 | 4.46 / 5.39 |
| a4 | 5000 | 21.04 / 19.3 | 31.4 / 32.9 | 6.41 / 7.26 |
| b1 | 1000 | 34.1 / 168.48 | 3.08 / 0.0 | 0.0 / 0.0 |
| b2 | 1000 | 4.61 / 46.45 | 22.52 / 2.38 | 0.0 / 0.0 |
| b3 | 2500 | 10.11 / 10.1 | 29.04 / 28.92 | 5.07 / 4.97 |
| b4 | 5000 | 20.86 / 20.25 | 32.79 / 31.52 | 6.99 / 6.71 |
| sub-ctrl | 2500 | 97.87 / 100.76 | 3.52 / 3.54 | 0.0 / 0.0 |

### v3-C10-hindep-s030-pfifo

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| a1 | 1000 | 3.43 / 3.25 | 28.98 / 29.69 | 0.0 / 0.0 |
| a2 | 1000 | 3.39 / 3.14 | 29.07 / 28.69 | 0.0 / 0.0 |
| a3 | 2500 | 9.55 / 8.97 | 29.75 / 32.79 | 5.25 / 5.54 |
| a4 | 5000 | 18.69 / 17.52 | 33.49 / 35.48 | 7.04 / 7.91 |
| b1 | 1000 | 3.9 / 3.43 | 25.13 / 26.21 | 0.0 / 0.0 |
| b2 | 1000 | 3.53 / 3.54 | 27.65 / 27.81 | 0.0 / 0.0 |
| b3 | 2500 | 9.96 / 10.17 | 29.35 / 30.87 | 5.04 / 4.94 |
| b4 | 5000 | 18.7 / 18.9 | 34.44 / 33.64 | 7.42 / 7.35 |
| sub-ctrl | 2500 | 115.61 / 107.88 | 2.41 / 3.55 | 0.0 / 0.0 |

### v3-C1a-calm-s010u085-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 500 | 19.63 / 18.48 | 2.5 / 2.76 | 0.0 / 0.0 |
| sub-b | 1000 | 32.94 / 34.37 | 3.35 / 3.07 | 0.0 / 0.0 |
| sub-c | 1000 | 21.88 / 25.69 | 4.7 / 3.95 | 0.0 / 0.0 |
| sub-ctrl | 2500 | 56.75 / 61.0 | 5.74 / 4.94 | 1.14 / 1.14 |
| sub-d | 2500 | 101.32 / 94.05 | 3.55 / 3.52 | 0.0 / 0.0 |

### v3-C1a-calm-s065u085-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 21.98 / 19.91 | 6.38 / 22.01 | 0.0 / 0.0 |
| sub-b | 2500 | 5.9 / 88.09 | 46.29 / 3.59 | 8.44 / 0.0 |
| sub-c | 2500 | 67.77 / 61.88 | 4.77 / 4.98 | 1.13 / 1.14 |
| sub-ctrl | 2500 | 59.89 / 78.92 | 5.74 / 4.61 | 1.16 / 0.0 |
| sub-d | 5000 | 97.3 / 102.38 | 7.06 / 7.06 | 1.16 / 1.16 |

### v3-C2-sburst-s030u070-pie

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 2.94 / 3.44 | 30.11 / 28.98 | 0.0 / 0.0 |
| sub-b | 2500 | 8.09 / 9.81 | 34.52 / 29.3 | 6.35 / 5.31 |
| sub-c | 2500 | 7.56 / 9.0 | 35.24 / 30.58 | 6.84 / 5.53 |
| sub-ctrl | 2500 | 114.6 / 95.69 | 2.45 / 3.53 | 0.0 / 0.0 |
| sub-d | 5000 | 16.94 / 93.78 | 38.23 / 23.88 | 8.01 / 1.21 |

### v3-C3a-sburst-s065u070-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 3.0 / 3.37 | 29.16 / 28.83 | 0.0 / 0.0 |
| sub-b | 2500 | 6.69 / 6.12 | 41.91 / 51.27 | 7.85 / 8.46 |
| sub-c | 2500 | 6.46 / 7.3 | 38.57 / 36.78 | 7.8 / 7.13 |
| sub-ctrl | 2500 | 74.88 / 68.58 | 4.56 / 3.73 | 1.1 / 0.0 |
| sub-d | 5000 | 12.8 / 13.39 | 43.26 / 42.74 | 10.08 / 9.96 |

### v3-C4-sramp-s030u070-fq_codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 45.05 / 39.27 | 2.48 / 2.67 | 0.0 / 0.0 |
| sub-b | 2500 | 11.41 / 11.02 | 24.84 / 24.16 | 4.54 / 4.53 |
| sub-c | 2500 | 10.11 / 12.32 | 28.97 / 22.82 | 4.96 / 4.14 |
| sub-ctrl | 2500 | 55.95 / 63.06 | 5.02 / 4.87 | 1.15 / 1.14 |
| sub-d | 5000 | 20.1 / 19.9 | 32.16 / 32.65 | 7.01 / 6.84 |

### v3-C4-sramp-s030u070-pie

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 2.94 / 2.94 | 33.4 / 33.56 | 0.0 / 0.0 |
| sub-b | 2500 | 9.43 / 9.44 | 33.12 / 31.47 | 5.74 / 5.36 |
| sub-c | 2500 | 7.86 / 8.15 | 33.3 / 33.48 | 6.53 / 6.33 |
| sub-ctrl | 2500 | 72.4 / 54.76 | 4.69 / 5.73 | 1.13 / 1.14 |
| sub-d | 5000 | 17.93 / 100.11 | 34.75 / 8.21 | 7.8 / 1.2 |

### v3-C5-stcp-s030u070-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 2.9 / 3.44 | 33.72 / 28.39 | 0.0 / 0.0 |
| sub-b | 2500 | 8.26 / 8.1 | 33.57 / 33.28 | 6.09 / 6.32 |
| sub-c | 2500 | 7.59 / 8.01 | 35.47 / 33.2 | 6.64 / 6.33 |
| sub-ctrl | 2500 | 92.46 / 100.57 | 3.53 / 3.01 | 0.0 / 0.0 |
| sub-d | 5000 | 16.34 / 20.3 | 35.72 / 29.56 | 7.25 / 5.77 |

### v3-C6-sjoin-s030u070-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 2.87 / 3.43 | 33.81 / 28.9 | 0.0 / 0.0 |
| sub-b | 2500 | 55.06 / 49.57 | 27.84 / 5.63 | 1.13 / 1.23 |
| sub-c | 2500 | 9.56 / 403.69 | 29.6 / 1.24 | 5.23 / 0.0 |
| sub-ctrl | 2500 | 86.2 / 83.06 | 3.54 / 3.58 | 0.0 / 0.0 |
| sub-d | 5000 | 110.64 / 450.22 | 26.65 / 1.29 | 1.14 / 0.0 |

### v3-C7-hhier-s030-pfifo

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| a1 | 1000 | 3.73 / 3.42 | 25.71 / 28.71 | 0.0 / 0.0 |
| a2 | 1000 | 3.37 / 3.3 | 28.73 / 28.55 | 0.0 / 0.0 |
| a3 | 2500 | 10.07 / 9.84 | 29.91 / 30.9 | 5.05 / 5.2 |
| a4 | 5000 | 18.12 / 18.11 | 33.16 / 33.31 | 7.4 / 7.25 |
| b1 | 1000 | 3.43 / 3.31 | 26.68 / 29.4 | 0.0 / 0.0 |
| b2 | 1000 | 3.36 / 3.19 | 28.64 / 28.76 | 0.0 / 0.0 |
| b3 | 2500 | 9.83 / 9.82 | 29.87 / 30.44 | 5.23 / 5.14 |
| b4 | 5000 | 18.9 / 17.91 | 33.47 / 33.82 | 7.41 / 7.52 |
| sub-ctrl | 2500 | 85.05 / 87.48 | 3.61 / 3.55 | 0.0 / 0.0 |

### v3-C7-hhier-s030-pie

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| a1 | 1000 | 3.1 / 3.23 | 29.45 / 30.73 | 0.0 / 0.0 |
| a2 | 1000 | 3.14 / 3.26 | 29.37 / 28.84 | 0.0 / 0.0 |
| a3 | 2500 | 9.28 / 9.0 | 31.72 / 31.78 | 5.54 / 5.6 |
| a4 | 5000 | 18.31 / 17.91 | 33.15 / 33.52 | 7.01 / 7.2 |
| b1 | 1000 | 2.95 / 2.93 | 32.69 / 32.84 | 0.0 / 0.0 |
| b2 | 1000 | 2.81 / 2.75 | 32.54 / 33.68 | 0.0 / 0.0 |
| b3 | 2500 | 8.71 / 8.99 | 32.34 / 32.37 | 5.8 / 5.71 |
| b4 | 5000 | 17.91 / 17.72 | 33.58 / 34.05 | 7.32 / 7.52 |
| sub-ctrl | 2500 | 111.89 / 89.76 | 2.43 / 3.54 | 0.0 / 0.0 |

### v3-C9-hdepth-tree16-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| a1 | 500 | 2.46 / 2.8 | 18.28 / 17.21 | 0.0 / 0.0 |
| a2 | 1000 | 4.43 / 4.14 | 22.31 / 25.12 | 0.0 / 0.0 |
| a3 | 1000 | 3.8 / 4.08 | 27.35 / 25.33 | 0.0 / 0.0 |
| a4 | 2500 | 10.01 / 10.03 | 30.97 / 29.88 | 5.05 / 5.0 |
| b1 | 500 | 2.9 / 3.6 | 16.87 / 13.25 | 0.0 / 0.0 |
| b2 | 1000 | 3.87 / 4.18 | 25.7 / 23.98 | 0.0 / 0.0 |
| b3 | 1000 | 5.03 / 3.91 | 19.71 / 25.79 | 0.0 / 0.0 |
| b4 | 2500 | 9.83 / 10.61 | 29.85 / 27.61 | 5.07 / 4.76 |
| c1 | 500 | 2.45 / 2.79 | 18.88 / 17.39 | 0.0 / 0.0 |
| c2 | 1000 | 4.42 / 3.8 | 22.2 / 25.83 | 0.0 / 0.0 |
| c3 | 1000 | 3.92 / 3.76 | 25.34 / 27.17 | 0.0 / 0.0 |
| c4 | 2500 | 10.02 / 9.82 | 30.51 / 29.78 | 5.05 / 5.17 |
| d1 | 500 | 3.13 / 2.53 | 15.17 / 18.36 | 0.0 / 0.0 |
| d2 | 1000 | 4.7 / 4.58 | 20.54 / 22.18 | 0.0 / 0.0 |
| d3 | 1000 | 4.06 / 4.44 | 23.85 / 23.19 | 0.0 / 0.0 |
| d4 | 2500 | 10.61 / 9.77 | 28.38 / 30.02 | 4.82 / 5.22 |
| sub-ctrl | 2500 | 99.92 / 103.55 | 3.56 / 3.55 | 0.0 / 0.0 |

### v3-C9-hdepth-tree16-fq_codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| a1 | 500 | 30.44 / 37.59 | 1.67 / 1.37 | 0.0 / 0.0 |
| a2 | 1000 | 4.5 / 25.48 | 21.72 / 4.44 | 0.0 / 0.0 |
| a3 | 1000 | 18.18 / 4.45 | 8.45 / 22.15 | 0.0 / 0.0 |
| a4 | 2500 | 9.99 / 9.62 | 29.31 / 30.84 | 5.05 / 5.24 |
| b1 | 500 | 29.56 / 32.23 | 1.8 / 1.59 | 0.0 / 0.0 |
| b2 | 1000 | 4.31 / 4.29 | 22.48 / 21.9 | 0.0 / 0.0 |
| b3 | 1000 | 27.62 / 30.46 | 3.82 / 3.48 | 0.0 / 0.0 |
| b4 | 2500 | 10.01 / 10.4 | 29.67 / 28.82 | 5.04 / 4.88 |
| c1 | 500 | 36.32 / 34.49 | 1.44 / 1.54 | 0.0 / 0.0 |
| c2 | 1000 | 4.54 / 4.23 | 22.98 / 23.36 | 0.0 / 0.0 |
| c3 | 1000 | 27.2 / 4.19 | 3.93 / 23.84 | 0.0 / 0.0 |
| c4 | 2500 | 9.81 / 9.82 | 30.38 / 30.89 | 5.17 / 5.08 |
| d1 | 500 | 29.47 / 33.52 | 1.74 / 1.56 | 0.0 / 0.0 |
| d2 | 1000 | 5.05 / 29.79 | 19.7 / 3.95 | 0.0 / 0.0 |
| d3 | 1000 | 21.62 / 3.92 | 10.8 / 25.28 | 0.0 / 0.0 |
| d4 | 2500 | 9.82 / 10.02 | 30.66 / 29.72 | 5.15 / 5.0 |
| sub-ctrl | 2500 | 116.87 / 107.45 | 2.71 / 3.61 | 0.0 / 0.0 |

### v3-C9-hdepth-tree16-pfifo

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| a1 | 500 | 1.95 / 1.89 | 25.26 / 25.79 | 0.0 / 0.0 |
| a2 | 1000 | 3.74 / 3.78 | 25.88 / 25.45 | 0.0 / 0.0 |
| a3 | 1000 | 3.51 / 3.65 | 28.38 / 27.48 | 0.0 / 0.0 |
| a4 | 2500 | 9.83 / 9.64 | 30.58 / 30.68 | 5.07 / 5.15 |
| b1 | 500 | 1.95 / 1.89 | 25.36 / 25.58 | 0.0 / 0.0 |
| b2 | 1000 | 3.52 / 4.31 | 27.15 / 22.11 | 0.0 / 0.0 |
| b3 | 1000 | 3.64 / 3.41 | 27.36 / 29.1 | 0.0 / 0.0 |
| b4 | 2500 | 10.02 / 10.42 | 30.67 / 28.55 | 5.03 / 4.78 |
| c1 | 500 | 1.95 / 1.92 | 25.27 / 25.5 | 0.0 / 0.0 |
| c2 | 1000 | 3.53 / 3.74 | 27.97 / 26.23 | 0.0 / 0.0 |
| c3 | 1000 | 3.57 / 3.63 | 28.11 / 27.39 | 0.0 / 0.0 |
| c4 | 2500 | 10.03 / 10.62 | 29.46 / 28.05 | 4.99 / 4.74 |
| d1 | 500 | 1.95 / 2.22 | 25.27 / 21.49 | 0.0 / 0.0 |
| d2 | 1000 | 3.5 / 3.81 | 27.26 / 25.63 | 0.0 / 0.0 |
| d3 | 1000 | 3.88 / 3.87 | 25.49 / 25.71 | 0.0 / 0.0 |
| d4 | 2500 | 9.83 / 10.03 | 30.64 / 29.53 | 5.07 / 4.95 |
| sub-ctrl | 2500 | 113.72 / 101.99 | 2.7 / 2.63 | 0.0 / 0.0 |

### v3-M11-sburst-bw4x12-pfifo

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 2.63 / 2.74 | 34.68 / 33.75 | 0.0 / 0.0 |
| sub-b | 2500 | 7.46 / 5.9 | 33.85 / 45.32 | 7.03 / 8.43 |
| sub-c | 5000 | 12.38 / 12.1 | 47.23 / 45.65 | 9.94 / 10.5 |
| sub-ctrl | 2500 | 63.35 / 105.88 | 4.91 / 3.4 | 1.16 / 0.0 |
| sub-d | 12000 | 27.58 / 27.39 | 50.92 / 53.04 | 13.1 / 13.58 |

### v3-M3-sburst-bgbursty-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 4.41 / 3.44 | 25.29 / 26.27 | 0.0 / 0.0 |
| sub-b | 2500 | 10.62 / 9.45 | 27.45 / 30.41 | 4.74 / 5.26 |
| sub-c | 2500 | 9.52 / 8.36 | 31.16 / 33.86 | 5.55 / 6.03 |
| sub-ctrl | 2500 | 80.71 / 77.38 | 3.58 / 4.57 | 0.0 / 1.13 |
| sub-d | 5000 | 18.31 / 16.94 | 34.38 / 34.28 | 7.55 / 7.61 |

### v3-M4-sburst-rttx05-pfifo

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 4.91 / 3.91 | 17.89 / 25.3 | 0.0 / 0.0 |
| sub-b | 2500 | 7.37 / 7.83 | 42.11 / 40.79 | 7.04 / 6.47 |
| sub-c | 2500 | 8.43 / 8.92 | 33.0 / 33.8 | 5.99 / 5.94 |
| sub-ctrl | 2500 | 125.74 / 137.57 | 2.35 / 2.41 | 0.0 / 0.0 |
| sub-d | 5000 | 20.47 / 19.29 | 32.09 / 31.43 | 6.47 / 6.99 |

### v3-M5-sburst-fps15-pfifo

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 2.94 / 2.88 | 75.5 / 80.35 | 14.54 / 14.55 |
| sub-b | 2500 | 8.44 / 8.27 | 72.15 / 68.16 | 13.58 / 13.36 |
| sub-c | 2500 | 8.15 / 8.11 | 70.97 / 73.62 | 14.27 / 14.26 |
| sub-ctrl | 2500 | 80.28 / 100.76 | 8.02 / 5.96 | 1.16 / 1.16 |
| sub-d | 5000 | 16.93 / 17.32 | 68.54 / 70.99 | 15.62 / 15.74 |

### v3-M5-sburst-fps60-codel

| client | kb/s | pacing Mb/s | keyframe ms | P-frame ms |
|---|---|---|---|---|
| sub-a | 1000 | 3.9 / 3.92 | 12.74 / 13.29 | 0.0 / 0.0 |
| sub-b | 2500 | 10.6 / 8.65 | 14.38 / 15.89 | 0.0 / 0.0 |
| sub-c | 2500 | 9.0 / 9.0 | 16.62 / 15.77 | 0.0 / 0.0 |
| sub-ctrl | 2500 | 61.44 / 79.63 | 2.37 / 2.28 | 0.0 / 0.0 |
| sub-d | 5000 | 15.17 / 16.16 | 19.76 / 17.28 | 3.34 / 3.14 |

