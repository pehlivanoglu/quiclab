import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from static import GT_HTML, SCENARIOS  # noqa: E402

src = Path(sys.argv[1])
rep = (src / "report.md").read_text().splitlines()
overall = []
for line in rep:
    m = re.match(r"\| (GT[123][^|]*) \| ([^|]+) \| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", line)
    if m:
        g = [x.strip() for x in m.groups()]
        g[0] = {"GT3 (B) owd-cmp": "GT3 kaynak B · RTT ve OWD karşılaştırması"}.get(g[0], g[0])
        overall.append(g)

c = pd.read_csv(src / "cells.csv")
o = c[c.truth == "GT3 (B) owd-cmp"].pivot_table(index=["scenario", "aqm"], columns="detector", values=["recall", "fa_per_min"])
weak = [f"{s}|{a}" for (s, a), r in o.iterrows()
        if r[("recall", "v2 RTT")] < 0.7 or r[("fa_per_min", "v2 RTT")] > 0.3 or r[("fa_per_min", "v2-fixed RTT")] > 0.3 or s == "revdelay"]

INTRO = """
<p class="lead">I/P oranı 4 ile koşulan 192 koşu: 24 senaryo, 4 AQM (pfifo, fq_codel, pie, red), her biri 2 tekrar. Toplam 769 dakika video, 9374 client olayı (GT3). Bütün sayılar dondurulmuş dedektörle üretildi; sadece önceden tanımlı kurallarla fit edilen değerler (G_ref, alt sınırlar, v2-fixed ölçeği) bu koşulardan yeniden çıkarıldı.</p>
<div class="prose"><ul>
<li><b>Ana truth GT3'te v2:</b> precision 0.97, recall 0.82, dakikada 0.27 yanlış alarm, gecikme p50 231 ms, p90 448 ms. v2-fixed: 0.97 / 0.84 / 0.28 / 240 / 429.</li>
<li><b>gcc</b> aynı recall'a yakın (0.80) ve en az yanlış alarmı veriyor (0.06), ama yaklaşık 4 kat geç: p50 904 ms. Kısa olayları ve sığ kuyrukları kaçırıyor.</li>
<li><b>BBR</b>'ın kendi bant genişliği düşüş olayı hem geç (723 ms) hem gürültülü: dakikada 1.15 yanlış alarm.</li>
<li><b>Copa</b> bu testbed'de yok, bu yüzden sonuçlarda yer almıyor.</li>
</ul></div>
"""

OVERALL_NOTE = """
<div class="prose"><ul>
<li><b>İki recall var.</b> Tabloda her olayda yeni bir alarmın başlaması gerekiyor. Alarmın olay sırasında açık olması yeterli sayılırsa recall v2'de 0.92, v2-fixed'de 0.97. Fark, hold kuralının uzun bir olay boyunca tek bir alarmı açık tutmasından geliyor.</li>
<li><b>GT1 ve GT2 recall'u her dedektörde düşük</b> (0.33–0.43), çünkü bu link seviyesi truth'lar keyframe'lerin yaptığı ve client'a zarar vermeyen kısa kuyrukları da sayıyor. Precision yüksek kaldığı için alarmların neredeyse hepsi gerçek bir kuyruk sırasında geliyor.</li>
<li><b>gcc'nin gecikmesine dikkat:</b> replay'de gcc'ye 500 ms'lik bir tespit tabanı uygulanıyor. Bu yüzden gecikmesi yapısal olarak yüksek.</li>
<li><b>I/P 8 ile karşılaştırma (eski 200 koşu):</b> v2'de GT3 yanlış alarmı dakikada 0.43'ten 0.27'ye, p90 gecikme 556 ms'den 448 ms'ye indi. Recall 0.80'den 0.82'ye çıktı. Küçük keyframe'ler daha az sahte kuyruk yapıyor.</li>
</ul></div>
"""

OWD_TEXT = """
<p class="lead">Tek yön gecikme (OWD) modunda gecikme özellikleri RTT yerine paketin ileri yöndeki gecikmesinden hesaplanır; dönüş yolundaki gecikme değişimleri sinyale girmez. Adil karşılaştırma için RTT ve OWD satırları, OWD ile aynı zaman damgalarını kullanmayan GT3 B kaynağına göre skorlandı. B kaynağı daha çok ve daha kısa olay ürettiği için recall'lar ana tablodan düşük.</p>
<div class="prose"><ul>
<li><b>Sonuç: OWD recall'u değiştirmiyor.</b> Genelde v2 0.69 → 0.69, v2-fixed 0.71 → 0.71, gcc 0.69 → 0.68.</li>
<li><b>OWD bazı hücrelerde yanlış alarmı azaltıyor:</b> v2'de burstlong fq_codel 0.45 → 0.00, revdelay pie 0.35 → 0.04, onoff red 0.82 → 0.31, burstcapdeep pie 0.31 → 0.00. Genel FA 0.07 → 0.04.</li>
<li><b>revdelay'de RTT zaten sorun değil.</b> Dönüş yolu gecikmesi koşu boyunca sabit; v2 tabanı client başına ölçtüğü için bu sabit farkı otomatik olarak çıkarıyor.</li>
<li><b>Zayıf hücrelerin hiçbirini OWD kurtarmıyor</b> (ppbp, ramp, burstlong, fq_codel rekabeti). Bu hücrelerdeki sorun gecikme ölçümünün yönü değil (aşağıdaki bölüm).</li>
</ul></div>
"""

WHY = """
<div class="prose">
<h3>1. Ölçüm kaynaklı düşük recall: burstlong, ramp, onoff, capacity, tcpcubic pie</h3>
<ul>
<li>Bu hücrelerde başlangıç tabanlı recall 0.25–0.79, ama alarm-açık recall 0.94–1.00 (fq_codel'deki capacity ve onoff hariç; onlar 4. maddede).</li>
<li>Sebep hold kuralı: uzun bir olay GT3'te birkaç ayrı episode olarak görünüyor ve alarm hepsinde tek parça açık kalıyor. Skorlama her episode için yeni bir başlangıç istediği için sonrakileri kaçırılmış sayıyor.</li>
<li>Örnek: burstlong fq_codel'de recall 0.25, alarm-açık recall 0.99.</li>
</ul>
<h3>2. Baştan yüklü koşular: ppbp (v2)</h3>
<ul>
<li>v2 recall 0.02–0.18, alarm-açık recall de 0.04–0.26: gerçek kaçırma.</li>
<li>Sebep: koşu ilk saniyeden tıkalı başlıyor ve v2 normal davranışı bağlantının kendisinden öğrendiği için yükü normal sanıyor.</li>
<li>v2-fixed bunu çözüyor (alarm-açık 0.90–1.00), gcc de başlangıç tabanlı recall'da en iyisi (0.62–0.89).</li>
</ul>
<h3>3. Yüklü linkler: calm090, calmcbr090</h3>
<ul>
<li>Bu senaryolar "tıkanıklık yok" diye tasarlandı, ama %90 yükte keyframe'ler gerçek kuyruk yapıyor: koşu başına yaklaşık 90 GT1 kuyruğu ve 30–37 GT3 olayı var. Yani truth'a göre negatif değiller.</li>
<li>v2 bu yükü kısmen normal öğreniyor: recall 0.46–0.78. Yanlış alarm fq_codel dışında 0; fq_codel'de 1.48 (calm090) ve 0.90 (calmcbr090).</li>
<li>v2-fixed daha çok olay yakalıyor (alarm-açık 0.75–0.99), ama ölçeği sakin linklerden geldiği için sekiz hücrenin beşinde yanlış alarm 1.1–5.2 FA/dk.</li>
</ul>
<h3>4. fq_codel ile rekabet: tcpcubic, tcpbbr, burstudp, cbr, splitudp, onoff</h3>
<ul>
<li>v2 recall 0.45–0.82 ve alarm-açık recall 0.71–0.86: gerçek kaçırmalar var.</li>
<li>Kaçırılan 54 episode'un 52'si kayıpla tetiklenmiş: CoDel kuyruğu yaklaşık 5 ms'de tutup paket atıyor, gecikme büyümüyor. Dedektör kaybı ancak kuyruk seviyesi yüksekken sayıyor, fq_codel ise akışı ayrı kuyrukta tutup kendi kuyruğunu kısa tutuyor.</li>
<li>Yanlış alarm da fq_codel'de yüksek: bu hücrelerde v2 0.32–0.95 FA/dk. Olay dışındaki alarmların %91'inde yolda gerçek bir router kuyruğu var; GT3 ise o client'ın etkilenmediğini söylüyor. Yani dedektör gerçek kuyruğu görüyor, zarar olup olmadığını ayıramıyor.</li>
</ul>
<h3>5. Rastgele kayıp: randloss</h3>
<ul>
<li>v2: fq_codel 0.10 ve pie 0.28 ile geçiyor, pfifo 0.48 ve red 0.38 ile geçmiyor (eşik 0.3).</li>
<li>Kayıp tek başına alarm başlatamıyor; kalan alarmlar kaybın kurtarılması sırasında gecikme ve bekleyen veri sinyallerinin oynamasından geliyor.</li>
<li>Bu test bağımsız rastgele kayıp kullanıyor. Gerçek kablosuz ağı temsil etmiyor.</li>
</ul>
<h3>6. Karşılaştırma dedektörleri neden zayıf</h3>
<ul>
<li><b>gcc:</b> 500 ms tespit tabanı ve trend çizgisi yüzünden yavaş (p50 yaklaşık 900 ms). Kısa olayları kaçırıyor: bursttiny'de recall 0.08–0.15. Sadece gecikmeye baktığı için kaybın gecikmeden önce geldiği sığ kuyrukları da kaçırıyor: burstcapshallow'da 0.02–0.68. Buna karşılık yanlış alarmı en az olan dedektör o.</li>
<li><b>BBR:</b> bant genişliği tahmini düşünce alarm veriyor. Kısa RTT'de ve rastgele kayıpta bu tahmin sık düşüyor: burstcaplowrtt'de 8–11, randloss'ta yaklaşık 5 yanlış alarm/dk. Gecikmesi de yüksek (p50 yaklaşık 730 ms).</li>
</ul>
</div>
"""

fit_lines = [l for l in rep if l.startswith("- RTT:") or l.startswith("- OWD:")]
FIT = f"""
<div class="prose">
<p>Dondurulmuş dedektör: dört özellik (gecikme seviyesi, gecikme artışı, bekleyen veri artışı, kayıp oranı), CUSUM birikimi, hold kuralı, level + cap kayıp kapısı. Alarm eşiği skor 0.25, kapanma 0.125. Aşağıdaki değerler önceden tanımlı kurallarla bu koşuların pfifo-r1 sakin koşularından çıkarıldı; truth'a ve tasarıma dokunulmadı.</p>
<ul>{''.join(f'<li><code>{l[2:]}</code></li>' for l in fit_lines)}</ul>
<p class="note">Truth ayarları: GT1 hedef 5 ms, aralık 150 ms; GT2 açılma 150 ms, kapanma 300 ms; GT3 gecikme 10 ms / kayıp %10, en az 0.5 s, belirsiz bant 0.15 s. Detector replay'i grup bilgisi kullanmıyor. Kaynak: <code>reports/detector-v2/ip4/</code> (cells.csv, events.csv, alarm_on.csv, report.md).</p>
</div>
"""

narr = {"scenarios": [{"name": n, "negative": neg, "desc": t} for n, neg, t in SCENARIOS],
        "overall": overall, "owdWeak": weak,
        "html": {"INTRO": INTRO, "GT": GT_HTML, "OVERALL_NOTE": OVERALL_NOTE, "OWD_TEXT": OWD_TEXT, "WHY": WHY, "FIT": FIT}}
Path(sys.argv[2]).write_text(json.dumps(narr, ensure_ascii=False))
print(len(overall), "overall rows,", len(weak), "owd cells")
