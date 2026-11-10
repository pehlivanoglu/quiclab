# Cellular capacity traces (grouping campaign N4)

Produced by `scripts/trace_prepare.py` from public datasets; each `.csv` holds
the capacity per 200 ms step (`t_s,mbps`), `index.json` the source URL,
duration, mean and zero-step fraction of every file. The raw files are not in
the repository (`trace_prepare.py --download <dir>` fetches them).

## Used by N4 (pool of 18; four different traces per run, chosen by seed)

Mahimahi LTE traces, `traces/*.down` of github.com/ravinet/mahimahi (one line
per 1500-byte delivery opportunity, ms):

| file | duration s | mean Mb/s |
|---|---|---|
| ATT-LTE-driving | 786 | 5.17 |
| ATT-LTE-driving-2016 | 120 | 4.55 |
| TMobile-LTE-driving | 475 | 12.77 |
| TMobile-LTE-short | 140 | 16.70 |
| Verizon-LTE-driving | 1363 | 9.72 |
| Verizon-LTE-short | 140 | 5.02 |

Norway HSDPA commute logs (`report.<date>.log`: unix_s, ms, lat, lon, bytes,
interval_ms; one report per ~1 s), two per route from
datasets.simula.no/hsdpa (mirror
skulddata.cs.umass.edu/traces/mmsys/2013/pathbandwidth):

| route | logs |
|---|---|
| bus.ljansbakken-oslo | 2010-09-28_1407CEST, 2010-09-29_0852CEST |
| metro.kalbakken-jernbanetorget | 2010-09-13_1003CEST, 2010-09-13_1046CEST |
| tram.ljabru-jernbanetorget | 2010-11-23_1541CET, 2010-12-09_1244CET |
| ferry.nesoddtangen-oslo | 2010-09-20_1542CEST, 2010-09-21_1001CEST |
| car.snaroya-smestad | 2011-02-14_2032CET, 2011-02-14_2051CET |
| train.oslo-vestby | 2011-02-11_1618CET, 2011-02-14_0644CET |

Prepared but not used (3G, 10–16 % zero steps; `TRACE_EXCLUDE` in
`scripts/grouping_campaign.py`): Verizon-EVDO-driving, TMobile-UMTS-driving.

Traces shorter than a run (600 s) wrap around; each client's segment starts at
a seeded offset and is scaled so its mean is 2 × the client's wire rate (see
`campaign-v2-spec.md`, N4; the final multiplier and below-rate fraction are in
every run's `grouping/plan.json`).

## Citations

- Mahimahi: R. Netravali, A. Sivaraman, S. Das, A. Goyal, K. Winstein, J. Mickens,
  H. Balakrishnan, "Mahimahi: Accurate Record-and-Replay for HTTP", USENIX ATC 2015.
  The cellular traces were recorded for K. Winstein, A. Sivaraman, H. Balakrishnan,
  "Stochastic Forecasts Achieve High Throughput and Low Delay over Cellular
  Networks", NSDI 2013.
- Norway HSDPA: H. Riiser, P. Vigmostad, C. Griwodz, P. Halvorsen, "Commute Path
  Bandwidth Traces from 3G Networks: Analysis and Applications", ACM MMSys 2013
  (dataset track), doi:10.1145/2483977.2483991.
