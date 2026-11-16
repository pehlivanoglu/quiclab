# Suite v3 kampanyası: dedektör raporu (dondurulmuş Shadow v2)

Kampanya `.runs/2026-11-14_1818_v3` (2026-11-14 18:18 → 2026-11-15 16:24): 203 koşu, 19.5 saat emülasyon.

Betikler ve ham satırlar bu klasörde:
- [score_runs.py](score_runs.py): koşu başına skorlama → `rows.jsonl`, `stimuli.jsonl`;
- [summarize.py](summarize.py) → [report.md](report.md) (tüm tablolar, rep'ler yan yana);
- [compact.py](compact.py) → [compact.md](compact.md);
- [stim_pivot.py](stim_pivot.py) → [stim-pivot.md](stim-pivot.md);
- [misses.py](misses.py) → [misses.md](misses.md);
- [gth_alarm_on.py](gth_alarm_on.py) → [gth-alarm-on.md](gth-alarm-on.md).

## 0. Koşular düzgün mü?

- **Tamamlanma:** 203 / 203 koşu bitti (`events.csv` sonunda `end` satırı var). Manifestte 203 "done", başarısız koşu yok. Logda tek hata metni Mininet'in zararsız "resource limits" uyarısı.
- **Gate:** PASS (9 koşu). Manifestteki `stopped: gate failed`, ilk denemeden (kontrol 5 değişmeden önce) kalma bir anahtar.
- **Koşu başına kontroller** (işaretli koşular tutuldu):

| kontrol | geçen | işaretli | neden |
|---|---|---|---|
| 1 yük / pay | 200 | 3 | M3 bgbursty (yük 0.65: PPBP'nin uzun dönem ortalaması koşu içinde tutmuyor), M11 bw4x1 r1 (yük 0.73) |
| 2 ECN | 203 | 0 | |
| 3 MTU / offload | 203 | 0 | |
| 4 GT-Q sağlığı | 191 | 12 | C12'nin 8 koşusu ve M11 bw4x1: access linkinde capdrop sırasında ~0.8 Mb/s, 20 ms pencereye 1–2 paket düşüyor, ±%5 ölçülemez (çözünürlük sınırı). C13 pfifo r1 ve M8 mixab r1: 1.4M ve 6.7M dequeue'da 1 kayıt eksik (`rows_match`). |
| 5 uyaran yükü | 107 (+83 uyaransız) | 13 | M3 (arka plan bilerek değişken: PPBP / TCP), M9 (0.2 s pencere), M11 bw4x1 r2 (1 pencere) |
| 6 faz kilidi | 190 (+11 arka plansız) | 2 | M3 bgmix: açık-kapalı TCP'nin 4 s döngüsünün 4. harmoniği 1 Hz'te (tasarım gereği) |

- GT-Q 201 / 203 koşuda geçerli. Geçersiz olan iki koşu, aynı 1 kayıtlık eksik nedeniyle C13 pfifo r1 ve M8 mixab r1.
- Truth ve dedektör verisini bozan bir durum yok.

## 1. Senaryolar

**Video ve gönderici.** qvideo-server mvfst üzerinde çalışıyor: BBR, pacing açık, istemci başına bir QUIC bağlantısı, GOP başına bir stream. 30 fps, GOP 1 s, I/P boyut oranı 4, lognormal kare gürültüsü σ 0.2. İstemci tamponu 600 ms, gönderici kuyruğu 1000 ms. **Tüm istemcilerin keyframe'leri senkron** (faz 0); tek istisna M6 (0/250/500/750 ms).

**Boyutlandırma.** Her darboğaz çıkışı e için D_e, arkasındaki istemcilerin hızlarının toplamı × 1.03'tür.
- Kapasite C_e = D_e / (s·U); arka plan BG_e = D_e (1−s)/s.
- s: senkron videonun linkteki payı. U: sakin yük.
- Varsayılan nokta s = 0.30, U = 0.70; keyframe kuyruk tepesi beklentisi ≈ 0.121·s·U s ≈ 25 ms.

**Arka plan.** Her darboğazın kendi kaynağı (`tx-e`, çıkışın sahibi router'da) ve kendi alıcısı (`rx-e`, çıkıştan hemen sonraki düğümde) var. Arka plan yalnız o çıkışı geçiyor.
- **BG-CBR (varsayılan):** n = max(4, BG/2.5 Mb/s) UDP akışı. Her akışın ayrı 5-tuple'ı ve kendi Poisson zamanlaması var; video saatinden bağımsız.
- **BG-BURSTY:** PPBP (Hurst 0.8).
- **BG-MIX:** %50 hız sınırlı TCP (yarısı CUBIC, yarısı BBR), %30 açık-kapalı TCP (2 s / 2 s), %20 CBR.

**AQM'ler.**
- pfifo: 50 ms kapasite limiti (M1'de 100 / 300 ms).
- codel, pie, fq_codel: kernel varsayılan limitleri, açıkça `noecn`.
- red: eşikler çıkışın kendi kapasitesinden (15 / 45 ms), limit 150 ms, ecn yok.
- cake: `unlimited besteffort`; cake'in tc'de ECN kapatma seçeneği yok, ama tüm trafik Not-ECT.
- fq_codel ve cake'te istemciler sabit akış sınıflarına iğneleniyor.

**Gecikmeler.** pub → ilk router 5 ms (1000 Mb/s).
- Varsayılan "narrow" küme: access gecikmesi istemcilere sırayla 5 / 7.5 / 12.5 / 20 ms; taban RTT 20–50 ms.
- "wide" küme (5 / 15 / 30 / 45 ms) ve ×0.5 / ×4 ölçekler yalnız M4'te.

**Uyaranlar.** u, video sakin hızındayken uyaranın şiddeti; sunulan yük U(1−s) + (u−U). Videonun tepkisi bir sonuç; `v3-stimuli.csv` dosyasında ölçülüyor.
- **surge:** hedef çıkışın arka plan yoluna 2.5 Mb/s'lik ek Poisson akışları; toplam (u−U)·C, basamak açık / kapalı.
- **ramp:** aynı ek yük, 5 s'de doğrusal artış, 5 s tutma.
- **tcp:** 2 / 4 açgözlü iperf3 akışı (CUBIC / BBR).
- **join (ASV):** 5000 kb/s rendition'ın kare deseni, ölçeklenmiş; 15 s artış, 15 s tutma, 10 s iniş.
- **capdrop:** kapasite U·C/u'ya iniyor. Yalnız access linklerinde ve M2'de.
- **revburst:** yalnız ACK yolunda UDP.
- **loss:** bir istemcinin access linkinde 10 s boyunca %0.5 / 1 / 2 rastgele kayıp.

Izgaralar: u ∈ {1.05, 1.15, 1.3}, d ∈ {2, 5, 10} s. Isınma 15 s, uyaranlar arası U(10, 15) s, kuyruk 10 s.

**Topolojiler.**

| ad | yapı | darboğazlar (s 0.30 / U 0.70) |
|---|---|---|
| T-BASE | pub → router → switch → 4 istemci (1 / 2.5 / 2.5 / 5 Mb/s) | main 54.0 Mb/s, BG 26.4 |
| T-ACCESS | T-BASE + her istemcinin önünde bir access router (25 Mb/s) | main 54.0, access 25 |
| T-SPLIT4 | pub → r1 → r2 → {switch-a, switch-b}, dal başına 4 istemci | up 93.2, a / b 46.6 |
| T-TREE16 | rr → r0 → {r1, r2} → 4 yaprak, yaprak başına 4 istemci (16 istemci) | root 98.1, X / Y 49.0, yapraklar 24.5 |
| T-UNEVEN | r1 → r2 (şekillendirilmemiş) → 2 / 5 / 9 istemcili yapraklar | A 36.8, B 49.0, C 80.9 |
| T-REV | T-BASE, önde r0; ters yön hedefi r1 → r0, 10 Mb/s | main 54.0 |

**Bloklar.** Her satır 2 rep (seed 1, 2); aynı seed tüm AQM'lerde kullanıldı.

| blok | tip | ne | AQM |
|---|---|---|---|
| G1–G3 | gate | sakin ve S-BURST kontrol koşuları | pfifo (+fq_codel) |
| C1a | CALM 120 s | T-BASE'in 9 (s, U) satırı + legacy (17.5 Mb/s, arka plan yok) | pfifo, codel |
| C1b | CALM | SPLIT4, TREE16, UNEVEN | pfifo |
| C2 | S-BURST (18 surge) | T-BASE varsayılan nokta | 6 AQM |
| C3a / C3b | S-BURST | s 0.10 ve 0.65 / legacy, eski burstudp kuralı | pfifo, codel / pfifo |
| C4 | S-RAMP (9 rampa) | | 4 AQM |
| C5 | S-TCP (16 TCP olayı) | | 4 AQM |
| C6 | S-JOIN (4 ASV) | | pfifo, codel, fq_codel |
| C7 / C8 | H-HIER (51 olay: up, a, b; a+b eşzamanlı, a+b 0.5 / 2 s gecikmeli, a+up) | SPLIT4, s 0.30 / 0.65 | 4 AQM / pfifo |
| C9 | H-DEPTH (48 olay, 7 seviye + A+C) | TREE16 | pfifo, codel, fq_codel |
| C10 | H-INDEP (üç hedefte bağımsız zamanlama, 600 s, örtüşmeye izin var) | SPLIT4 | pfifo, codel, fq_codel |
| C11 | H-UNEVEN (aynısı, A / B / C) | UNEVEN | pfifo, codel |
| C12 | A-MIXED (9 paylaşılan surge + 12 özel capdrop; sub-d 60. s'de katılıyor) | ACCESS | 4 AQM |
| C13 | L-LONG (10 / 30 s surge'ler) | SPLIT4 | pfifo, codel |
| C14 | R-REV (9 ileri surge + 9 ters burst) | REV | pfifo, fq_codel |
| C15 | N-LOSS (9 kayıp penceresi) | T-BASE | pfifo, codel |

Mikro bloklar (her biri C2'ye göre tek bir şeyi değiştiriyor):
- M1: pfifo derinliği 100 / 300 ms.
- M2: surge yerine capdrop.
- M3: arka plan BG-BURSTY / BG-MIX.
- M4: RTT ×0.5 / ×4 / wide.
- M5: 15 / 60 fps.
- M6: kaydırılmış keyframe fazları.
- M7: SPLIT4'te kök şekillendirilmemiş (noroot).
- M8: mixab (r2 → a pfifo, r2 → b fq_codel).
- M9: S-STRESS (u 2.0 ve 0.2 / 0.5 s'lik çok kısa surge'ler).
- M10: I/P oranı 2 / 8.
- M11: bitrate karışımları (s 0.65).
- M12: ileri / ters jitter 10 ms.
- M13: Copa.
- M14: seyrek surge'ler (45–75 s ara).

## 2. Dedektör ve truth'lar

**Dedektör.** Dondurulmuş Shadow v2 (`scripts/shadow_v2_frozen.py`):
- özellikler F1–F4 + kayıp; fusion d; CUSUM; hold kuralı; kayıp kapısı level+cap; θ_on 0.25;
- sabitler (floor, scale, G_ref) ip4 kampanyasından; **v3'te hiçbir şey yeniden uydurulmadı**.
- Ana dedektör **v2-owd**: ACK alış zaman damgalarından tek yönlü gecikme.
- Karşılaştırma: v2-fixed-owd (global sabit istatistikler), v2-rtt, v2-fixed-rtt.

**Truth'lar.**

| truth | ne ölçüyor | skorlama |
|---|---|---|
| GT1 | istemcinin yolundaki bir router çıkışında CoDel tarzı kalıcı kuyruk (5 ms / 150 ms) | `gt_score`: istemci başına maruziyet; TP = [t_on − 1 s, min(bitiş, t_on + 10 s)] içindeki ilk alarm başlangıcı; CLEAR zamandaki diğer alarm başlangıçları FA; AMBIGUOUS yok sayılır |
| GT2 | yoldaki bir çıkışta talep ≥ kapasite | aynı |
| GT3 | istemcinin kendi gecikme / kayıp etkisi (frame log, kaynak B; OWD modunun kullandığı ACK zaman damgalarıyla bağımsız), yolunda GT1/GT2 kuyruğu varken | aynı (ana truth) |
| GT-Q | paket izinden akış başına kısıtlayan kuyruk bölümleri | `gtq_score`: collar [t0 − W, t1 + d_obs + W] içinde alarm başlangıcı → TP |
| GT-H | GT-Q bölümlerinden oynatıcının 300 / 600 / 1000 ms bütçesini kaçıranlar (zarar) | aynı |

İki recall raporlanıyor, kararlaştırıldığı gibi:
- **başlangıç-tabanlı:** pencerede yeni bir alarm başlangıcı olmalı;
- **alarm-on:** pencere boyunca alarm açık.

## 3. Genel sonuç (tüm koşular)

| truth | dedektör | bölüm | precision | recall | alarm-on recall | F1 | FA / dk (CLEAR) | gecikme p50 / p90 ms |
|---|---|---|---|---|---|---|---|---|
| **GT3** | **v2-owd** | 39 238 | **1.00** | **0.93** | **0.98** | 0.96 | **0.02** | **222 / 487** |
| GT3 | v2-fixed-owd | 39 238 | 0.99 | 0.92 | 0.99 | 0.95 | 0.06 | 248 / 524 |
| GT3 | v2-rtt | 39 238 | 1.00 | 0.93 | 0.98 | 0.96 | 0.03 | 222 / 490 |
| GT3 | v2-fixed-rtt | 39 238 | 0.99 | 0.92 | 0.98 | 0.96 | 0.03 | 257 / 557 |
| GT1 | v2-owd | 26 513 | 0.99 | 0.62 | 0.75 | 0.76 | 0.02 | 242 / 559 |
| GT2 | v2-owd | 24 399 | 0.99 | 0.66 | 0.74 | 0.79 | 0.02 | 244 / 615 |

GT1 / GT2 bağlantı düzeyinde (hop-level) recall: 0.66 / 0.68.

| dedektör | GT-Q precision [%95 GA] | GT-Q recall | GT-H recall 300 / 600 [GA] / 1000 | sıkı precision (GT-H 600) | FA / akış-saat | L_obs p50 / p95 ms | zarardan önce alarm (collar'da başlangıç ve t_harm'dan önce; bkz. madde 2) |
|---|---|---|---|---|---|---|---|
| **v2-owd** | **0.99** [0.99, 1.00] | 0.04 | 0.53 / **0.57** [0.50, 0.66] / 0.59 | 0.69 | 0.7 | 218 / 690 | 0.57 |
| v2-fixed-owd | 0.98 | 0.04 | 0.52 / 0.56 / 0.58 | 0.65 | 2.1 | 239 / 747 | 0.56 |
| v2-rtt | 0.99 | 0.04 | 0.53 / 0.57 / 0.59 | 0.69 | 1.1 | 219 / 694 | 0.57 |
| v2-fixed-rtt | 0.99 | 0.04 | 0.53 / 0.57 / 0.59 | 0.66 | 1.8 | 253 / 794 | 0.56 |

**Rep 1 / rep 2 (v2-owd):**
- GT3: P 1.00 / 1.00, R 0.92 / 0.93, FA 0.02 / 0.01 dk⁻¹, p50 224 / 216 ms.
- GT-H 600: R 0.57 / 0.58.
- Genel düzeyde iki rep uyumlu.

### Bu sayılar nasıl okunmalı

1. **GT3 (ana truth):** v2-owd neredeyse kusursuz.
   - Precision 1.00, CLEAR zamanda dakikada 0.02 yanlış alarm (≈ saatte 1).
   - Bölümlerin %93'ünde pencere içinde alarm başlıyor, %98'inde pencere boyunca alarm açık.
   - Medyan tespit gecikmesi 222 ms.
2. **GT-H 600 recall 0.57 dedektör eksikliği değil, eşleştirme kuralının hold ile etkileşimi** ([gth-alarm-on.md](gth-alarm-on.md)):

   | AQM | zararlı bölüm | collar'da alarm başlangıcı | kaçırılmış ama alarm açık (hold) | alarm kapalı |
   |---|---|---|---|---|
   | pfifo | 7 453 | 0.78 | 0.22 | 0.00 |
   | codel | 5 424 | 0.69 | 0.31 | 0.00 |
   | fq_codel | 5 662 | 0.20 | 0.79 | 0.01 |
   | pie | 1 369 | 0.52 | 0.47 | 0.00 |
   | **tümü** | **20 458** | **0.57** | **0.42** | **0.01** |

   - Zararlı bölümlerin **%99'unda alarm açık**.
   - **"%99" ile "0.57" çelişmiyor, farklı şeyleri sayıyorlar** ([../v3-score/harm.md](../v3-score/harm.md), REPORT.md Part 5):
     - %99: alarm aralığı bölümle herhangi bir anda çakışıyor. Zararın başladığı anda (t_harm, ilk kaçan 600 ms deadline) alarm açık olma oranı da aynı: 0.99 / 1.00.
     - 0.57: bölümün collar'ı içinde **yeni bir alarm başlangıcı** var.
     - Tablodaki "zarardan önce alarm" (0.56 / 0.57) buna bir koşul daha ekliyor: o ilk başlangıç t_harm'dan önce olmalı. Bu koşul neredeyse hiç bozulmuyor.
     - Adı yanıltıcı: eksik kalan 0.43 "zarardan sonra gelen alarm" değil. Zarar anında zaten açık olan ama daha önceki bir bölümde açılmış alarm.
   - **Alarm zarardan ne kadar önce açılmış:** medyan 1.7 s (p10 0.7, p90 8.0), hiçbir zaman 0.2 s'den az değil.
     - fq_codel'de medyan 3.9–4.0 s, çünkü alarm önceki bölümlerden taşınıyor.
   - **"Zarar anında açık" için rastgele karşılaştırma** (harm.md §D):
     - Alarm zamanın 0.25–0.28'inde açık; fq_codel'de 0.13–0.14.
     - Akışın kendi alarm aralıkları korunup zarar anları rastgele kaydırılınca: 0.31–0.33. Gözlenen 0.99–1.00.
     - Kuyruk olan zamanlarda alarm açık olma oranı: pfifo / codel / pie 0.79–0.82, fq_codel 0.16–0.18.
     - fq_codel'de alarm kuyruk zamanının çoğunda kapalı, ama zarar başlangıçlarının 0.98–0.99'unda açık.
     - Tanım sonuçlardan sonra değiştirildi; makalede iki tanım da gerekçesiyle verilmeli.
   - **Gerçek kaçırma** (zarar anında alarm kapalı): 20 458 bölümde 105. Bunların yarısında alarm collar içinde geç başlıyor.
   - **GT-Q zamanın ne kadarını kaplıyor:** bölümler akış zamanının 0.33'ünü, collar'lar 0.44'ünü kaplıyor (fq_codel'de 0.74–0.76).
     - Rastgele bir alarm aynı kuralla genelde precision 0.45–0.46 alırdı; dedektör 0.99–1.00 alıyor.
     - fq_codel'de rastgele alarm 0.82–0.83, dedektör 0.98; orada precision pek bilgi taşımıyor.
   - **fq_codel GT-H recall 0.20 sayım kuralından geliyor:**
     - Zarar anında alarm 0.98–0.99 oranında açık; 0.78–0.80'i önceki bir bölümün alarmı.
     - fq_codel bir kuyruk dönemini dakikada 109–113 bölüme bölüyor (diğer AQM'lerde 55–63).
     - Aynı akışta aradaki boşluk < 0.5 / 1 / 2 s olan bölümler birleştirilince recall 0.71 / 0.80 / 0.92–0.95 oluyor.
     - Birleştirme yalnızca ölçüm amaçlı; yeni başlık metriği değil.
   - GT-Q uzun bir olayı çok sayıda kısa bölüme bölüyor; kaçırılan bölümlerin medyan süresi 0.06–0.38 s ([misses.md](misses.md)).
   - Hold'lu tek alarm olayın başında başlıyor, sonraki bölümlerin collar'ında yeni başlangıç olmuyor.
3. **GT-Q recall 0.04 anlamlı bir başlık metriği değil.**
   - GT-Q, sakin zamandaki her senkron keyframe kuyruğunu (~20–25 ms) kısıtlayan bölüm olarak sayıyor: 497 bin bölüm.
   - Kanıt, keyframe darbesi zayıflayınca recall'un yükselmesi:
     - M6'da fazlar kaydırılmış: 0.82;
     - 60 fps: 0.72; I/P oranı 2: 0.67;
     - s 0.10: 1.00;
     - RTT ×4 / wide (W büyüyor): 0.99 / 0.90.
   - GT-Q precision 0.99: alarmlar gerçek kuyruklara denk geliyor.
4. **GT1 / GT2 recall'unun (0.62 / 0.66) düşüklüğü bağlantı düzeyinde maruziyetten.**
   - Kuyruklu bir çıkışın arkasındaki her istemci "maruz" sayılıyor, kendi akışı kısıtlanmasa bile.
   - Kayıplar kuyruk izolasyonu olan AQM'lerde toplanıyor: fq_codel 0.46–0.78, cake 0.00.
   - PIE'de 0.29–0.46: PIE'nin GT1 bölümleri parçalı (C2'de pfifo 144'e karşı 356 bölüm), başlangıç-tabanlı sayım düşüyor; alarm-on 0.98.
   - GT3 bu durumları istemcinin kendi etkisine göre ayırıyor.
5. **OWD ve RTT** aynı sonucu veriyor; tek fark ters yön (C14).
   - RTT varyantları ters ACK burst'lerinde dakikada 0.60–0.64 yanlış alarm veriyor (GT3 precision 0.86).
   - v2-owd'de 0.01 (precision 1.00).
6. **v2-fixed** (global sabit istatistikler) daha çok yanlış alarm veriyor: C1a 0.15, C6 0.45, M11 0.43 dk⁻¹.
   - M12'de ileri jitter ile çöküyor: uyaran düzeyinde 0.26, GT3 recall 0.52.
   - Ana dedektör v2-owd'de aynı koşulda 1.00 / 0.96.

## 4. Hücre hücre (v2-owd, rep'ler toplanmış; rep ayrımı ve `*` işaretleri `report.md` bölüm 2'de)

Tablo [compact.md](compact.md) dosyasında; özet:

- **Tekli darboğaz, BG-CBR surge (C2):**

  | AQM | GT3 P / R / alarm-on | GT1 R | GT-H 600 R | gecikme p50 / p90 ms |
  |---|---|---|---|---|
  | pfifo | 1.00 / 0.99 / 1.00 | 1.00 | 0.97 | 175 / 391 |
  | codel | 1.00 / 1.00 / 1.00 | 0.97 | 1.00 | 180 / 359 |
  | red | 1.00 / 0.99 / 0.99 | 0.99 | 1.00 | 195 / 504 |
  | pie | 0.95 / 0.79 / 0.98 | 0.39 | 0.68 | 197 / 446 |
  | fq_codel | 0.99 / 0.96 / 0.98 | 0.78 | 0.22 | 222 / 801 |
  | cake | GT3 bölümü 5 (video izole), R 0.00 | 0.00 | – | – |

  Ek notlar:
  - cake: istemcilerin hiçbiri alarm vermiyor ve video etkilenmiyor (video/sakin 0.98–1.01, ölçülen toplam yük 1.05–1.31). Bu doğru davranış: cake videoyu izole ediyor, kuyruk yalnız arka planda.
  - pie: rep'ler uyuşmuyor (r1 0.86 / r2 0.73; FA 0.55 / 0.00): **"not reliable"**.
- **u ve d'ye göre** ([stim-pivot.md](stim-pivot.md)): pfifo, codel ve RED'de her hücrede istemcilerin %100'ü alarm veriyor, u 1.05 / 2 s dahil.
  - Video, aşırı yükte geri çekiliyor: u 1.3'te pfifo'da 0.38–0.71, codel'de 0.33–0.65. Gerçekleşen toplam yük 1.16–1.24.
  - PIE ve RED'de video düşmüyor (1.0–1.2), toplam ≈ nominal u.
  - fq_codel'de istemcilerin 3/4'ü alarm veriyor (0.75–1.00).
- **s ve U (C1a, C3a):** sakin koşularda dakikada yanlış alarm her (s, U) satırında 0.00. Üç istisna var:
  - legacy pfifo: GT1'e göre 0.18 / 0.35 (sakin keyframe kalıcı kuyruğu ~80 ms, GT3'e göre 0.00);
  - s065u050 codel r2: 0.14;
  - C2 pie r1: 0.40.

  S-BURST'te s 0.10, 0.30 ve 0.65'in hepsinde GT3 recall 0.87–1.00.
- **Rampa (C4):** GT3 R 0.77–1.00; gecikme p50 325–446 ms, rampa yavaş olduğu için daha geç.
- **TCP surge (C5):** pfifo / codel / pie GT3 R 0.87–1.00. fq_codel'de 0.89, uyaran düzeyinde 0.50: TCP adil paya sığdırılıyor, video kısıtlanmıyor (video/sakin 0.99).
- **Katılım / ASV (C6):** başlangıç-tabanlı R 0.30–0.40, alarm-on 0.98 (pfifo, codel). 40 s'lik rampa çok sayıda GT3 bölümü üretiyor, tek hold'lu alarm hepsini kapsıyor.
  - fq_codel'de yalnız 13 GT3 bölümü var; ASV tek akış, fq_codel onu izole ediyor; uyaran düzeyinde 0.22.
- **Hiyerarşiler:**
  - H-HIER (C7) pfifo / codel / pie: her seviyede (up, a, b) istemcilerin %100'ü alarm veriyor; GT3 R 0.80–1.00. fq_codel 0.60–0.67.
  - H-DEPTH (C9) pfifo / codel: 7 seviyenin hepsinde (root, X, Y, A–D) %100. fq_codel 0.38–0.50.
  - H-UNEVEN (C11): %99–100.
  - H-INDEP (C10): yalnız pencerelerde 0.98–0.99, örtüşenlerde 0.76–0.78 ([misses.md](misses.md)). İstemci zaten alarmdayken yeni başlangıç olmuyor.
  - mixab (M8): fq_codel dalı b 0.63, pfifo dalları 1.00.
- **s 0.65 hiyerarşi (C8):** GT3 R 0.81, alarm-on 0.85, gecikme p90 2.8 s. Video payı yüksekken (0.65) sakin istatistiği keyframe kuyruğunu öğreniyor; bu ppbp'de görülen etkiyle aynı.
- **legacy (C3b, video-only 17.5 Mb/s):** GT3 R 0.81, p90 4.2 s. Aynı neden: sakin dönemde ~80 ms'lik keyframe kuyruğu.
- **Uzun surge (C13, 10 / 30 s):** başlangıç-tabanlı R 0.73, alarm-on 1.00. Uzun olayda birden çok GT3 bölümü oluşuyor, tek alarm hepsini kapsıyor.
- **Ters yol (C14):** v2-owd GT3 P 1.00, FA 0.01. RTT varyantlarında FA 0.60.
- **Rastgele kayıp (C15):** GT3 bölümü yok; FA 0.08–0.12 dk⁻¹. Kayıp pencerelerinin %6–11'inde bir istemci alarm veriyor; kayıp kapısı çoğunu bastırıyor.
- **Access (C12):** özel capdrop'larda %100 alarm; paylaşılan surge'lerde 0.86–0.99. GT3 R 0.87–1.00.
- **Mikro bloklar:** v2-owd her mikro blokta GT3 R ≥ 0.89 ve P ≥ 0.98. Gecikmenin değiştiği yerler:
  - fps 15: p50 317–388 ms; fps 60: 100 ms;
  - RTT ×4: 308 ms;
  - ileri jitter (M12 jitfwd): p50 674, p90 4374 ms. Recall korunuyor, ama gecikme ciddi uzuyor.
  - M9'da 0.2 s'lik surge'ler: uyaran düzeyinde 0.98, GT3 R 0.80–0.98.

## 5. Zayıf noktalar ve açık yorumlar

- **fq_codel / cake:** dedektör yalnız kısıtlanan istemciler için alarm veriyor. Bağlantı düzeyindeki truth'lar (GT1/GT2) ve GT-H'nin başlangıç-tabanlı sayımı fq_codel'i düşük gösteriyor. GT3'te ve alarm-on'da ise fq_codel 0.96–0.99.
- **Hold ile başlangıç-tabanlı eşleştirme:** C6, C13, C10 örtüşenler ve GT-H. Hangi recall'un başlık olacağı daha önce kararlaştırıldı (ikisi birden raporlanıyor). GT-H için de alarm-on sütunu eklendi.
- **Yüksek video payı / sürekli yük:** C8 (s 0.65) ve legacy'de kendi kendini kalibre eden sakin istatistikler keyframe kuyruğunu normal sayıyor; recall 0.81, p90 gecikme 2.8–4.2 s.
- **Rep uyuşmazlıkları** (`report.md` bölüm 2.3'te GT3 için 24 `*` işaretli değer). Recall'da en belirgin olanlar:
  - C2 pie: 0.86 / 0.73;
  - C10 fq_codel: 0.82 / 0.93;
  - C1a legacy pfifo: 0.13 / 0.29;
  - C4 pie: 0.71 / 0.83.

  FA'da bir desen var: yanlış alarm çoğunlukla yalnız rep 1'de görülüyor:
  - C2 pie 0.55 / 0.00;
  - C5 pfifo 0.35 / 0.00;
  - M3 bgbursty pfifo 0.38 / 0.00;
  - C10 pfifo 0.15 / 0.00.

  Ters yönde olanlar da var: M3 bgmix pfifo 0.00 / 0.34, M5 fps15 0.00 / 0.27. Genelde rep 1'de 0.02, rep 2'de 0.01 dk⁻¹. Nedeni bilinmiyor: **not reliable**.
- **Sabitler ip4'ten dondurulmuş haliyle kullanıldı.** M5'teki fps 15 / 60 için tick süresi fps'ten alınıyor; G_ref 30 fps'te ölçülmüştü.
