SCENARIOS = [
    ("burstcap", False, "Darboğaz kapasitesi düşüyor: yük u = 1.1 / 1.3 / 2.0, süre 1 / 2 / 4 s. Temel tıkanıklık testi."),
    ("burstudp", False, "Aynı şiddet ve süre ızgarası, ama tıkanıklığı UDP patlaması yapıyor. fq_codel UDP'yi ayrı kuyrukta tutar."),
    ("bursttiny", False, "0.2–0.5 s'lik çok kısa kapasite düşüşleri (u 1.3 / 2.0). Kuyruğun çoğunu emdiği geçici olaylar."),
    ("burstlong", False, "Uzun tıkanıklık: 10 / 30 / 60 s. BBR uyum sağladıktan sonra da alarmın açık kalması gerekiyor."),
    ("burstcapshallow", False, "burstcap, kuyruk 0.25 BDP: gecikme büyümeden önce paket kaybı başlar."),
    ("burstcapdeep", False, "burstcap, kuyruk 4 BDP: uzun gecikme, az kayıp."),
    ("burstcaplowrtt", False, "burstcap, bütün link gecikmeleri × 0.25 (kısa RTT)."),
    ("burstcaphighrtt", False, "burstcap, bütün link gecikmeleri × 2 (uzun RTT)."),
    ("capacity", False, "Kapasite farklı şiddet (u 1.05–2.0) ve sürelerde (1–10 s) düşüyor; arada alarm vermemesi gereken sakin değişimler var."),
    ("ramp", False, "Kapasite 2 s'lik adımlarla yavaşça u 1.05 / 1.1 / 1.2 tepesine çıkıp iniyor. Sınırda yük."),
    ("cbr", False, "Sabit hızlı UDP çapraz trafik belirli sürelerle açılıyor. FIFO'da herkes etkilenir, fq_codel izole eder."),
    ("onoff", False, "UDP çapraz trafik 2 s açık, 4 s kapalı; hafif / orta / ağır seviyeler."),
    ("tcpcubic", False, "Rakip TCP Cubic bulk akışı 2 / 4 / 8 s. Elastik trafik kuyruğu doldurur."),
    ("tcpbbr", False, "Rakip TCP BBR bulk akışı 2 / 4 / 8 s."),
    ("ppbp", False, "Patlamalı, kendine benzer UDP trafik (Hurst 0.8), ortalama yük ~0.95. Koşu baştan yüklü, tıkanıklık gelip gidiyor."),
    ("revdelay", False, "burstcap, ama her client'ın dönüş (ACK) yoluna 0 / 20 / 40 / 80 ms ek gecikme. İleri yön aynı: RTT'yi yanıltan senaryo."),
    ("isolate", False, "access topolojisi: sadece bir client'ın kendi erişim router'ı düşüyor. Yalnız o client alarm vermeli."),
    ("splitcap", False, "split topolojisi: üst akış ve iki alt akış darboğazı. Kapasite düşüşü bir seferde birinde, ya da üst + a seri."),
    ("splitudp", False, "split topolojisi, UDP patlamaları bir darboğazda."),
    ("calm030", True, "Tıkanıklık yok, link kullanımı 0.3. Her alarm yanlış alarm."),
    ("calm065", True, "Tıkanıklık yok, link kullanımı 0.65."),
    ("calm090", True, "Tıkanıklık yok, link kullanımı 0.9 (dar link). Keyframe'ler kısa kuyruk yapabilir."),
    ("calmcbr090", True, "Kullanım 0.9, ama sabit UDP çapraz trafikle (link geniş)."),
    ("randloss", True, "Yayıncı → router yolunda %0.5 / 1 / 2 rastgele kayıp, 10 s; kuyruk yok. Kablosuz benzeri kayıp testi (bağımsız kayıp)."),
]

GT_HTML = """
<div class="gt-grid">
  <div class="gt"><span class="tag">GT1 · router kuyruğu</span><h3>Kuyruk var mı?</h3>
    <p>Router çıkışının kuyruk gecikmesi en az 150 ms boyunca hiç 5 ms'nin altına düşmezse olay başlar (CoDel'in kalıcı kuyruk testi). Router'ın kendi sayaçlarından gelir ve o çıkıştan geçen bütün client'lara yazılır.</p>
    <p><b>Önemli olan:</b> ağda gerçekten kuyruk olduğunu gösterir, ama client'ın zarar görüp görmediğini söylemez. Keyframe'lerin yaptığı kısa kuyrukları da sayar, bu yüzden her detector'ın GT1 recall'u düşük çıkar.</p></div>
  <div class="gt"><span class="tag">GT2 · talep ≥ kapasite</span><h3>Link aşırı yüklü mü?</h3>
    <p>Bir çıkışa gelen trafik 150 ms boyunca kapasiteyi geçince olay başlar, 300 ms boyunca altında kalınca biter. Kaynak seviyesinde aşırı yükü ölçer.</p>
    <p><b>Önemli olan:</b> fq_codel'de veya rakip TCP varken, link aşırı yüklü olsa bile her client aynı oranda etkilenmez. Link seviyesi bir truth'tur.</p></div>
  <div class="gt"><span class="tag">GT3 · ana truth</span><h3>Bu client etkileniyor mu?</h3>
    <p>Client'ın tek yön gecikmesi kendi tabanından 10 ms'den fazla artarsa ya da kaybı %10'u geçerse ve bu en az 0.5 s sürerse, aynı anda yolunda bir GT1 veya GT2 kuyruğu da varsa olay vardır. Ölçüm alıcı tarafından gelir. Client başınadır. 0.15–0.5 s arası belirsiz durumlar AMBIGUOUS sayılır ve skora girmez.</p>
    <p><b>Önemli olan:</b> detector'ın asıl işi bu. Hem ağda kuyruk var, hem bu client gerçekten etkileniyor.</p></div>
</div>
<p class="note">Skorlama üç truth'ta da aynı: alarm, olay başlangıcından 1 s önce ile başlangıçtan 10 s sonra (ya da olay sonu) arasında başlarsa olay yakalanmış sayılır. Olay dışında ve CLEAR zamanında başlayan alarm yanlış alarmdır. AMBIGUOUS zaman yok sayılır. İlk 5 s skorlanmaz. Gecikme: olay başlangıcından sonraki alarmlar için alarm − başlangıç.</p>
"""
