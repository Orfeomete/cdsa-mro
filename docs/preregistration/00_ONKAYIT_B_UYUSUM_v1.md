# B makalesi — kodlayıcılar arası uyuşum çalışması ön kaydı ve kodlama kitabı

Tarih 10 Eylül 2026

Durum **örneklem çekilmeden ve hiçbir kodlama yapılmadan donduruldu**

Görev KKT-20260910-BUYUSUM

---

## Neden bu çalışma

B makalesi iki tipoloji öneriyor ve §7'de kendi sınırını yazıyor. Bir tipoloji
bir araçtır, araç ise **farklı kişilerin aynı malzeme üzerinde aynı sınıfa
varması** gösterilerek doğrulanır. Bu gösterilmediği sürece tipoloji tek bir
yazarın yargısıdır. Bu çalışma o boşluğu kapatmak için tasarlanmıştır.

## Kodlamayı kim yapar, kim yapamaz

Kodlama **iki insan kodlayıcı** tarafından yapılacaktır.

**Yapay zekâ ajanı kodlayıcı olarak kullanılmayacaktır.** Gerekçe, CDSA
programının E9 aşamasında konmuş olan yasağın aynısıdır. Ölçülmek istenen şey
insan kodlayıcıların yazılı bir kitapla aynı sınıfa varıp varmadığıdır. Ajan
kodlaması bu soruyu yanıtlamaz, yalnız ajanın tipolojiyi yazan metne ne kadar
benzediğini ölçer ve sonuç şişer.

Tipolojiyi yazan kişi (Mete Cantekin) **kodlayıcı olamaz**. Kendi aracını
uygulayan kişinin uyuşumu, aracın uyuşumu değildir.

## Örneklem

**Kaynak.** NASA Aviation Safety Reporting System (ASRS) kamuya açık olay
bildirim veri tabanı. Kaynak, hem klasik hem bilgi güvenliği kaynaklı olayları
içerdiği ve serbest metin anlatı sunduğu için seçilmiştir.

**Büyüklük.** Her tipoloji için **150 bildirim**, toplam 300.

**Gerekçe.** On beş sınıflı bir şemada şansa göre düzeltilmiş uyuşumun kararlı
kestirimi için sınıf başına ortalama on gözlem hedeflenmiştir. Bu, kabul edilen
bir alt sınırdır ve daha büyük bir örneklem daha iyi olurdu; 150 sayısı iki
insan kodlayıcının makul bir sürede bitirebileceği miktar olarak seçilmiştir.

**Çekim.** Bildirimler, arama sorgusu ve tarih aralığı kayda geçirilerek
çekilecek, ardından **tohum 20260910** ile karıştırılıp ilk 150'si
alınacaktır. Çekilen tam liste, kodlama başlamadan önce kimlik numaralarıyla
dondurulacaktır.

**Sıfır gözlemli sınıf.** Bazı sınıflar örneklemde hiç görünmeyebilir. Bu
durumda o sınıflar analizden çıkarılmayacak, **sıfır gözlemle raporlanacak**
ve uyuşum yalnız gözlem bulunan sınıflar üzerinden hesaplanacaktır. Kaç
sınıfın sıfır kaldığı sonuçta yazılacaktır.

## Körleştirme

Her bildirimden kaynak kimliği, tarih, havayolu ve konum çıkarılacak, yerine
sıra numarası konacaktır. Kodlayıcılar birbirlerinin kodlarını görmeyecek,
yazarın kodlarını görmeyecek ve yazar kodlama sürerken kodlayıcılarla sınıf
tartışmayacaktır. Anahtar dosya kodlama bitene kadar açılmayacaktır.

## Ölçüt ve eşik

**Birincil ölçüt** Krippendorff alfası, nominal düzey.

**İkincil ölçüt** Cohen kappası, ve sınıf bazında uyuşum oranı.

**Güven aralığı** 10 000 tekrarlı bootstrap ile yüzde 95.

**Ön kayıtlı eşikler.**

- α ≥ 0,80 ise tipoloji **kullanılabilir bir araç** olarak raporlanır.
- 0,67 ≤ α < 0,80 ise tipoloji **koşullu kullanılabilir** olarak raporlanır ve
  hangi sınıf çiftlerinin karıştığı yazılır.
- α < 0,67 ise şu cümle yazılır:

> Önerilen tipoloji, iki kör kodlayıcı arasında kabul edilebilir bir şansa göre
> düzeltilmiş uyuşum üretmemiştir; bu haliyle bir ölçüm aracı olarak
> sunulamaz ve makalede bir öneri olarak kalmaktadır.

Eşikler Krippendorff'un kendi önerdiği sınırlardır ve sonuç görüldükten sonra
değiştirilmeyecektir.

## Sonuç görüldükten sonra değiştirilmeyecekler

Örneklem büyüklüğü, tohum, çekim sorgusu, kodlama kitabının metni, birincil
ölçüt, eşikler, bootstrap tekrar sayısı, kodlayıcı sayısı.

---

# KODLAMA KİTABI

## Kullanım

Her bildirim için **tam olarak bir** sınıf seçilir. Sınıf seçilemiyorsa
`99 — sınıflanamaz` kodlanır ve gerekçe bir cümleyle yazılır. `99` oranı da
raporlanacaktır; yüksek çıkması şemanın kapsama sorununu gösterir.

**Karar sırası.** Önce olayın **nedensel yolu** sorulur, sonucu değil. Bir
ayrılma kaybına siber bir müdahale yol açtıysa siber sınıf kodlanır, ayrılma
kaybı değil. Neden belirsizse `99` kodlanır, tahmin edilmez.

## Bakım tipolojisi, on beş sınıf

| Kod | Sınıf | Karar kuralı |
|---|---|---|
| 1 | Oltalama saldırısı | Personelin aldatıcı bir ileti aracılığıyla kimlik bilgisi veya erişim vermesi |
| 2 | Gölge bilişim | Onaylanmamış donanım, yazılım veya bulut hizmetinin bakım işine sokulması |
| 3 | OT sistem sızması | Bakım test veya ölçüm donanımına yetkisiz erişim |
| 4 | USB zararlı yazılımı | Taşınabilir ortam yoluyla kod bulaşması |
| 5 | Konfigürasyon hatası | Yanlış yapılandırılmış sistem veya kurulum parametresi |
| 6 | Yetersiz erişim iptali | Ayrılan veya görev değiştiren personelin erişiminin sürmesi |
| 7 | Hesap ele geçirme | Meşru bir hesabın başkası tarafından kullanılması |
| 8 | Sosyal mühendislik | Aldatıcı ileti dışında insan manipülasyonu, örneğin telefonla |
| 9 | İş emri sahteciliği | Bakım kaydının veya iş emrinin yetkisiz değiştirilmesi |
| 10 | Portal erişim ihlali | Bakım portalına veya teknik yayın sistemine yetkisiz erişim |
| 11 | Fidye yazılımı | Şifreleyip erişimi engelleyen kod |
| 12 | Tedarik zinciri kirlenmesi | Tedarikçiden gelen parça, yazılım veya veride bütünlük kaybı |
| 13 | Kalibrasyon bütünlüğü ihlali | Ölçüm donanımının kalibrasyon kaydının bozulması |
| 14 | DDoS saldırısı | Erişilebilirliğin yük ile engellenmesi |
| 15 | Eğitim sistemi manipülasyonu | Eğitim kaydı veya yeterlilik verisinin değiştirilmesi |

**Sınır durumları.** 1 ile 8 arasında karar verirken taşıyıcıya bakılır; yazılı
aldatıcı ileti 1, sözlü veya yüz yüze manipülasyon 8. 5 ile 12 arasında karar
verirken hatanın kaynağına bakılır; kuruluş içinde yapılmış yapılandırma 5,
dışarıdan gelmiş bileşen 12. 9 ile 13 arasında karar verirken değiştirilen
kayda bakılır; iş emri 9, kalibrasyon kaydı 13.

## Hava trafiği tipolojisi, on beş sınıf

| Kod | Sınıf | Karar kuralı |
|---|---|---|
| 1 | Ayrılma kaybı | Asgari ayrılma değerinin altına düşülmesi |
| 2 | Piste izinsiz giriş | Korunan pist alanına yetkisiz girilmesi |
| 3 | Hava sahası ihlali | İzinsiz hava sahasına girilmesi |
| 4 | Frekans tıkanıklığı | Telsiz frekansının kullanılamaz hâle gelmesi |
| 5 | TCAS çözüm tavsiyesi | TCAS'ın çözüm tavsiyesi üretmesi |
| 6 | GNSS aldatması | Yanlış konum üreten sahte uydu sinyali |
| 7 | GNSS karıştırması | Uydu sinyalinin gürültü ile engellenmesi |
| 8 | ADS-B enjeksiyonu | Sahte uçak izinin yayına sokulması |
| 9 | Veri hattı kesintisi | Sayısal veri hattının kaybı |
| 10 | Gözetim verisi kaybı | Radar veya ADS-B verisinin kaybı |
| 11 | ATM sistem sızması | ATM sistemine yetkisiz erişim |
| 12 | Ses kanalı aldatması | Sahte telsiz talimatı verilmesi |
| 13 | NOTAM kurcalaması | NOTAM içeriğinin yetkisiz değiştirilmesi |
| 14 | Zaman eşitleme saldırısı | Sistem zaman kaynağının bozulması |
| 15 | Konum sahteciliği | Uçak konum bilgisinin kasten yanlış bildirilmesi |

**Sınır durumları.** 6 ile 7 arasında karar verirken çıktıya bakılır; yanlış
ama makul konum 6, konum yokluğu 7. 8 ile 15 arasında karar verirken sahte izin
kaynağına bakılır; dışarıdan enjekte edilmiş iz 8, uçağın kendi vericisinin
yanlış bildirimi 15. 9 ile 10 arasında karar verirken kaybedilen şeye bakılır;
talimat hattı 9, gözetim resmi 10. 4 ile 12 arasında karar verirken kastın
varlığına bakılır; kasıt yoksa 4, sahte talimat varsa 12.

---

*Bu metin örneklem çekilmeden yazılmış ve dondurulmuştur. Kodlar ve sonuçlar
bu dosyaya dokunulmadan ayrı dosyalara yazılacaktır.*
