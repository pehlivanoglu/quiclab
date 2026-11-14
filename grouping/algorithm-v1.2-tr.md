# ECG v1.2: koddaki algoritmanın tam tanımı

Bu belge, gruplama algoritmasının (ECG v1.2, varsayılan ayarlar) **kodda yazılı olan** halini adım adım anlatır. Algoritma değişikliklerine başlamadan önce referans olsun diye yazıldı (2026-11-11).

- Kod: `grouping/engine.py`, `grouping/config.py`, `grouping/types.py`, `grouping/replay.py`.
- Girdileri üreten adapter: `scripts/grouping_adapter.py`.
- Brief: `grouping-implementation-v01.md`. Kurallar ve sonuçlar: `grouping/README.md`.

---

## 0. Sabitler (`Config`, varsayılanlar)

| ad | değer | anlamı |
|---|---|---|
| `delta` (δ) | **0.150 s** (2026-11-11'e kadar 0.300) | olay eşleşme penceresi |
| `delta_max` | 2δ = 0.300 s (önce 0.600) | bir olayın en fazla açılımı |
| `hold` | 1.0 s | geç gelen alarmlar için ek bekleme |
| `align_mode` | `half_mrtt` | hizalama yöntemi |
| `obs_mode`, `obs_fraction` | `sent_rate`, 0.5 | gözlenebilirlik testi |
| `alpha_err`, `beta_err` | 0.01, 0.05 | eşikleri belirleyen hata oranları |
| **A** | ln(0.95 / 0.01) = **4.554** | üyelik / onay eşiği |
| **B** | ln(0.05 / 0.99) = **−2.986** | atılma eşiği |
| `L_cap` | 2A = 9.108 | kanıt tavanı |
| `w_cap_frac` | 0.55 → olay başına en fazla **2.505** | |
| `p_det` | 0.8 | sabit tespit olasılığı |
| `p_fa_floor` | 0.03 | yanlış alarm olasılığı tabanı |
| `lambda_init`, `lambda_tau` | 0.02 /s, 60 s | arka plan alarm hızı |
| `tau`, `decay_period` | 300 s, 10 s | her 10 s'de ×e^(−10/300) = 0.967 |
| `sigma_min` | δ/2 = 0.075 s (önce 0.15) | gecikme modeli alt sınırı |
| `k_cand` | 3 | client başına en fazla aday yaprak sayısı |
| `s_split_weight` | 8.0 | yaprak bölme eşiği |
| `dissolve_support` | 0.05 | yaprak dağılma eşiği |
| `obs_window` | 0.020 s | gözlem ve tick adımı |
| `charge_unmatched`, `member_hysteresis`, `report_confirmed_only`, `majority_match` | açık | v1.2 kuralları |
| `c_silent_penalty` | kapalı | v1.2 kuralı |
| `theta_J`, `theta_cov` | 0.7; kampanyada 0.6 | **yalnız v1.1 eşleşmesinde kullanılıyor; v1.2'de etkisiz** |
| `enable_priming`, `enable_slow_path` | kapalı | açılırsa hata veriyor |

## 1. Girdiler (adapter → motor)

Her client (flow) için üç tür kayıt var. Sıralama: zaman, aynı zamanda önce meta, sonra obs, sonra onset.

**FlowMeta:** `mrtt` = o client'ın ACK'lerindeki en küçük RTT. `ecn_capable` her zaman `False`. `rendition_bps` = video bitrate'i.

**Onset** (her dedektör alarmı başına bir tane):
- `t_arrival`: alarmın verildiği an.
- `t_onset`: v2 kaynaklarında, alarmdan önceki son "CUSUM istatistiği 0" anı; tıkanmanın tahmini başlangıcı.
- `track` her zaman `"delay"`, `magnitude` her zaman `1.0`. Adapter ikisini de vermiyor.
- Warmup'tan önceki alarmlar atılıyor.

**ObsSample:** her 20 ms'de, her client için bir örnek.
- `observable`: client son 200 ms'de rendition'ının en az %50'si kadar byte göndermişse ve warmup bitmişse `True`.
- `in_episode`: o an dedektörün alarm episode'u içindeyse (`[t_arrival, end)`) `True`.

**tick:** her 20 ms'de motor bir kez saat ilerletiyor. Bozunmayı ve süresi dolan olayların kapanmasını tick yapıyor.

## 2. Onset gelince (`on_onset`)

1. **Episode bastırma:** Client'ın açık bir episode'u varsa (`episode_since`) yeni onset **yok sayılıyor**. Episode, `in_episode = False` olan ve `t_onset`'ten sonra gelen ilk obs örneğinde kapanıyor. Sonuç: bir tıkanma episode'u en fazla bir onset üretiyor.
2. **Arka plan hızı:** `λ_bg ← λ_bg · e^(−Δt/60) + 1/60`. Kabul edilen her onset sayılıyor, gerçek tıkanmadan gelenler dahil.
3. **Hizalama:** `t_al = t_onset − mrtt/2`.
4. **Olaya ekleme:** Açık olaylar arasında koşulları sağlayan **en yakın** olay seçiliyor. Koşullar:
   - `|t_al − e.t0| ≤ δ`;
   - `t_al ≤ e.t0 + δ_max`;
   - client o olayda zaten yok.

   Uygun olay yoksa yeni bir olay açılıyor ve `t0 = t_al`. Yani olayın zamanı **ilk üyenin** hizalanmış zamanıyla sabitleniyor.
5. **Kapanış zamanı:** `closes_at = t0 + δ_max + hold`, yani t0'dan 1.3 s sonra (δ = 0.3 iken 1.6 s).

## 3. Olay kapanınca (`_close`)

1. **Tekilleştirme:** Her client olayda bir kez sayılıyor (en erken `t_al`'ı). Üye kümesine M diyelim.
2. **touched:** M'deki client'ların üyesi veya adayı olduğu yaprakların kümesi.
3. **Her touched yaprak için:**
   - `nset` = üyeler ∪ adaylar;
   - `nobs` = bu olay için gözlenebilir olanlar;
   - J (Jaccard) ve cov (kapsama) hesaplanıyor; v1.2'de yalnız A'daki aday ekleme kararında (`cov == 1`) kullanılıyor.
4. **Gözlenebilirlik** (`_observable(g, e)`): pencere [t0 − δ, t0 + δ]. Şu koşulların hepsi gerekiyor:
   - pencerede en az bir obs örneği var;
   - örneklerin en az yarısı `observable`;
   - hiçbiri `intervened` değil;
   - pencereden önceki son örnek `in_episode` değil (client zaten tıkanık değildi). Pencereden önce örnek yoksa pencerenin ilk örneğine bakılıyor.
5. **Vaka seçimi:**
   - |M| = 1 → **SOLO**;
   - aksi halde çoğunluk eşleşmesi (aşağıda).
6. **charge_unmatched:** Vakanın güncellemediği touched yapraklara azınlık kuralı uygulanıyor (bölüm 5).
7. **transitions:** M'deki ve touched yaprakların üye/aday client'ları için taşınma ve ayrılma kontrolü.
8. **dissolve:** Zayıf yapraklar dağıtılıyor.

### Çoğunluk eşleşmesi (`_match_majority`, v1.2 kuralı 7)

- **k[n]** = M ∩ nset(n), yani yaprağın kaç client'ı bu olayda alarm verdi.
- **covered:** k ≥ 2 olan ve en az 2 gözlenebilir client'ı bulunan yapraklar.
  - Sıralama: önce onaylı olanlar, sonra büyük k, sonra yüksek support.
  - Hipotezi (üyeler + hiçbir yaprağa ait olmayan adaylar) önceki seçilenlerle çakışan yaprak atlanıyor.
- **≥ 2 covered** → **Vaka B** (GLOBAL kontrolü içinde). GLOBAL oylamasında k ≥ 1 olan her touched yaprak "kapsandı" sayılıyor.
- **k ≥ 2 olan yaprak yok** → **Vaka D**.
- **Aksi halde** en iyi yaprak n seçiliyor (önce büyük k, sonra onay, sonra support). İki durum var:
  - M, nobs'un **kesin alt kümesi** ve alarm veren gözlenebilir client sayısı ≤ nobs'un yarısı → **Vaka C** (alt-örüntü);
  - değilse **Vaka A**. Yaprak dışındaki client'lar yalnız cov = 1 ise (yaprağın tamamı alarm verdiyse) aday yapılıyor.

## 4. Ağırlıklar

**Pozitif ağırlık:**

```
w_pos = min( 0.55·A ,  ln(p_det / p_fa) · c_lag · c_track · c_mag )
p_fa  = clip( 1 − e^(−λ·2δ) , 0.03 , 0.5 )        λ = λ_bg, son onset'ten beri bozunmuş
```

- **c_lag:** O client'ın o düğümdeki olay gecikmesi (`t_al − t0`) için öğrenilmiş Gauss modeli. Ortalama ve varyans 0.3 ağırlıklı EWMA ile güncelleniyor, σ ≥ 0.075 s (önce 0.15). İlk 2 olayda 1.
- **c_track:** Diğer üyelerin çoğunluk track'ine uyuyorsa 1, uymuyorsa 0.5.
- **c_mag:** Büyüklük medyanın 1/3–3 katı arasındaysa 1, değilse 0.7.

**Negatif ağırlık:** `w_neg = ln((1 − p_det) / (1 − p_fa))`. Tabandaki p_fa ile yaklaşık **−1.58**.

Pratikte (episode çalışmasında, `reports/grouping-episode/`, 709 pozitif kanıtta ölçüldü): p_fa tabanda 0.03, `ln(0.8/0.03) = 3.28`, bu da tavana (2.505) kırpılıyor. c_lag, c_track ve c_mag hiç 1'in altına inmedi. Ağırlık ancak λ dakikada ~6.7 alarmı aşınca tavanın altına düşüyor.

## 5. Vakalar

**A** (`_apply_leaf`):
- **fired_in** = M ∩ (üyeler ∪ adaylar). Yaprağın support'u fired_in'deki ağırlıkların **ortalaması** kadar artıyor; `n_events++`; onay kontrolü yapılıyor.
- Gözlenebilir fired_in üyeleri: L += w ve gecikme modeli güncelleniyor. Gözlenebilir fired_in adayları: cand += w.
- Dışarıdan gelenler (extras): `add_extras` açıksa (A'da yalnız cov = 1 iken, B'de hiç) aday yapılıyor, cand += w.
- **Sessiz kalan gözlenebilirler:** Alarm veren gözlenebilir sayısı k, toplam gözlenebilir m olsun.
  - 2k ≥ m ise sessiz üyeler L += w_neg, sessiz adaylar cand += w_neg alıyor.
  - Değilse **alarm verenler azınlıkta**: onlardaki üyeler 0.5·w_neg alıyor ve `solo++`.
- Yaprak onaylıysa **CONFIRMED_SHARED** çıktısı üretiliyor.

**B / GLOBAL** (`_case_b`):
- **all_leaves** = client'ı olan yapraklar. Touched olup 2'den az gözlenebilir client'ı olanlar hariç.
- **GLOBAL**, şu iki koşuldan biri sağlanırsa:
  - en az 2 onaylı yaprak var ve hepsi kapsandı;
  - en az 2 yaprak var ve hepsi kapsandı.

  Bu durumda **yalnız kökün support'u artıyor**. Hiçbir client'ın L'i ya da cand'ı değişmiyor.
- **Aksi halde:**
  - P = covered yaprakların en yakın ortak atası.
  - P kökse ya da P'nin covered olmayan alt dallarında sessiz kalmış gözlenebilir bir client varsa, P'nin altına **yeni bir iç düğüm** açılıyor, covered yapraklar ona taşınıyor ve boşalan eski ebeveynler budanıyor (splice).
  - P'nin support'una ve alt-örüntüsüne ortalama w ekleniyor.
  - Her covered yaprağa A uygulanıyor, ama dışarıdan aday almadan.
  - Hiçbir covered yaprakta olmayan gözlenebilir alarmcılar **iç düğüm P'ye aday** yapılıyor.

**C** (alt-örüntü, `_case_c`):
- Alt-örüntü ağırlığı `sub_patterns[M]` += ortalama w, `n_events++`. **Support artmıyor.**
- Alarm veren üyeler L += w (gecikme modeli de güncelleniyor), adaylar cand += w.
- v1.2'de sessiz üyelere ceza yok (`c_silent_penalty = False`).
- `sub_patterns[M] ≥ 8.0` olursa yaprak **ikiye bölünüyor** (`_split`):
  - a = M'deki üyeler ve adaylar, b = geri kalanlar;
  - a'nın support'u = alt-örüntü ağırlığı, b'nin support'u = eski yaprağınki;
  - eski yaprak iç düğüm oluyor.

**D** (`_case_d`): Kökün altına yeni bir yaprak açılıyor. Support = ortalama w. Gözlenebilir her alarmcı bu yaprağa aday oluyor (cand = w), başka bir yaprakta üye olsa bile.

**SOLO** (`_solo`):
- Client gözlenebilir değilse yalnız **PRIVATE** çıktısı üretiliyor.
- Gözlenebilirse `solo++` ve client'ın üyesi ya da adayı olduğu her yaprak için:
  - yaprakta **en az 2 başka** gözlenebilir client varsa: client üyeyse 0.5·w_neg alıyor;
  - **tam 1 başka** client varsa: o sessiz client w_neg alıyor (üyeyse L'ine, adaysa cand'ına). Bir aday çiftin alabileceği tek negatif kanıt bu.
- Ardından **PRIVATE** çıktısı.

**charge_unmatched** (v1.2 kuralı 1): Vakanın dokunmadığı her touched yaprakta, alarm veren en az bir gözlenebilir client varsa A'daki sessizlik / azınlık kuralı uygulanıyor:
- en az yarısı alarm verdiyse sessizler w_neg alıyor;
- değilse alarm veren üyeler 0.5·w_neg alıyor ve `solo++`.

## 6. Defter tutma

- **`_add_L`:** L = min(L_cap, L + w). w > 0 ise `together++`, w < 0 ise `apart++`. Ardından üyelik güncelleniyor.
- **Üyelik (histerezisli):** L ≥ A → üye. L ≤ A/2 → üyelikten çıkıyor. Düğümü olmayan client üye değil.
- **`_add_cand`:** yeni = min(cap, eski + w).
  - Yeni değer ≤ B ise aday siliniyor.
  - Yeni bir yaprağa aday olacakken zaten 3 adaylığı varsa: en zayıf adaylığı bu yeni değerden küçükse o atılıyor; değilse yeni adaylık hiç eklenmiyor.
- **Onay:** support ≥ A → yaprak onaylı (ilk onay zamanı ve olay sayısı kaydediliyor). support < A/2 → onay geri alınıyor.
- **`_transitions`** (her olay kapanışında):
  - Client'ın yaprak adaylıkları arasında en büyüğü ≥ A ve mevcut L'inden büyükse oraya **taşınıyor**. L = o aday değeri olur, bütün adaylıklar silinir, together/apart sıfırlanır.
  - Bir yaprağın üyesiyse ve L ≤ B ise **yapraktan ayrılıyor**: düğümü yok, L = 0.
- **Bozunma** (her 10 s, `_decay`): L, solo, together, apart, bütün cand'lar, support'lar ve alt-örüntüler ×0.967. Ardından üyelik ve onay güncelleniyor, dissolve çalışıyor.
- **Dağılma** (`_dissolve`): support < 0.05 olan ya da 2'den az client'ı kalan yaprak siliniyor. Üyeleri serbest kalıyor (L = 0), adaylıkları siliniyor. Ebeveyni budanıyor: 2'den az çocuğu kalan iç düğüm kaldırılıyor, çocukları bir üst düğüme bağlanıyor, o düğüme olan adaylıklar siliniyor.

## 7. Çıktı ve çift kararı

`query_pair(f, g)`:
- **SAME:** İkisi de üye, ikisinin yaprağı da onaylı (`report_confirmed_only`), ve aynı yapraktalar.
- **DIFFERENT:** İkisi de üye ve onaylı, ama farklı yapraklarda. Ortak ata seviyesi de veriliyor.
- **UNCERTAIN:** Diğer bütün durumlar.

Raporlardaki çift skorları, her olay kapanışındaki ve koşu sonundaki bu kararlardan hesaplanıyor.

---

## 8. Kodda dikkat çeken noktalar (2026-11-11)

| # | nokta | etkisi |
|---|---|---|
| 1 | Adapter `magnitude`, `track` ve `ecn` bilgisini vermiyor. c_mag ve c_track hep 1, c_lag da pratikte hep 1. | Ağırlıkların Bayesçi parçaları ölü: **her kanıt aynı tavan değerinde (2.505)**. Üyelik her zaman "2 temiz olay" kuralına iniyor. |
| 2 | Vaka B'de hiçbir covered yaprakta olmayan alarmcılar **iç düğüme** aday yapılıyor; ama `_transitions` yalnız **yaprak** adaylıklarına bakıyor. | Bu adaylıklar hiçbir zaman üyeliğe dönüşmüyor; yalnız 3'lük aday kotasında yer tutuyor. Ölü dal gibi duruyor. |
| 3 | Vaka C yaprağın **support'unu artırmıyor**, yalnız alt-örüntü ağırlığını. | Hep alt-örüntüyle (yaprağın bir kısmıyla) tıkanan bir yaprak onay alamıyor; 8.0'a ulaşınca bölünmeyi bekliyor. |
| 4 | Olay zamanı (t0) **ilk gelen üyenin** zamanıyla sabitleniyor, merkezle değil. | Eşleşme alarmların geliş sırasına bağlı. Uç bir ilk üye pencereyi kaydırabilir. |
| 5 | Episode bastırma: bir client'ın açık episode'u varken yeni onset alınmıyor. Episode'un sonu ve süresi hiç kullanılmıyor. | Uzun tıkanma = tek kanıt. Bitiş tartışmasıyla bağlantılı (`reports/grouping-episode/README.md`). |
| 6 | GLOBAL olaylar hiçbir client'a kanıt yazmıyor; yalnız kökün support'u artıyor, o da hiçbir yerde kullanılmıyor. | K1 / K6'daki eşzamanlı olayların bilgisi tamamen kayboluyor. |
| 7 | λ (arka plan hızı) gerçek tıkanma alarmlarını da sayıyor. | Çok sık tıkanmada p_fa yükselip ağırlıklar düşüyor (dakikada ~6.7 alarmın üstünde). Gerçek tıkanma "gürültü" gibi cezalanabilir. |
| 8 | Vaka D, başka yaprakta üye olan client'ları da yeni yaprağa aday yapıyor. 3 aday sınırı dolunca yeni adaylık sessizce eklenmiyor. | Hatalı veya fazla yaprağın kaynağı olabilir; aday sınırı bilgi kaybettirebilir. |
| 9 | `theta_J` / `theta_cov` (kampanyada 0.6) yalnız v1.1 yolunda kullanılıyor. | Raporlarda "engine overrides 0.6" yazıyor ama v1.2'de hiçbir etkisi yok; yanıltıcı. |
| 10 | Gözlenebilirlik testi bitrate'e ve "pencereden önce episode içinde değildi" koşuluna bağlı. | Zaten tıkanık bir client'ın sessizliği kanıt sayılmıyor; bu doğru. Ama uzun tıkanmalarda o client hiç kanıt almıyor. |
| 11 | Phase 2 (priming, `intervened`) ve Phase 4 (slow path, `LatentShared`) tanımlı ama kapalı. `PredictedShared` / `LatentShared` hiç üretilmiyor. | Bilinçli, ama "eksik" listesinde. |
