# CDSA çatı tezi — Faz E deney programı, ön kayıt

**Tarih:** 05.09.2026 · **Sınıf:** ön kayıt — hiçbir koşu başlamadan yazıldı ve donduruldu
**Karar veren:** Mete ("tüm bulguları önerilen adımlar sunarak kapat") · **Yazan:** Claude
**Öncül:** bağımsız hakem denetimi (05.09.2026), Claude değerlendirmesi (`_COWORK/CLAUDE_KKT_HAKEM_DEGERLENDIRMESI_05092026.md`), tez v8
**Kapsam:** v8'de metinle kapatılamayan, yeni deney gerektiren yedi bulgu (3, 4, 5, 6, 7, 14, 19) ve 1–2'nin deneysel tamamlayıcısı

⚠️ **Bu belgedeki metrikler, eşikler ve kurallar sonuç görülmeden yazılmıştır ve ölçüm sonrası değiştirilmez.** Öngörülmeyen sonuç, kuralı değiştirerek değil, tarihli bir Ek ile yazılır. Ödül işlevi ve etiket kuralı sonuca göre ayarlanmaz.

---

## E0 — Kayıt disiplini (bütün deneylere ortak)

Her koşu; koşu kimliği, tohum, kod sürümü (git özeti), yapılandırmanın **koddan okunan** hâli (sabit değil; v7'de `rounds: 100` yazılırken kod 160 koşuyordu), veri dosyasının SHA-256 özeti, tahmin dosyası ve karışıklık matrisini yazar. Bir tabloya giren her sayı bu alanlardan türetilir; türetilemeyen sayı tabloya girmez.

## E1 — Çok-modlu kazanç (bulgu 1'in deneysel tamamlayıcısı)

**Kurgu.** Her damarda tek-modlu (birincil modalite) ve çok-modlu kollar, aynı tohum, aynı bütçe, aynı değerlendirme kümesi; beş tohum.
**Metrik.** Sınıf bazında F1 ve makro-F1, karışıklık matrisinden; ayrıca kritik sınıf kesinlik–duyarlılık.
**Kural E1.1.** Çok-modlu − tek-modlu makro-F1 farkı, beş tohum ortalamasında **+0,05**'i aşarsa "kazanç ölçüldü"; aşmazsa "kazanç ölçülemedi". Tablo 9'un 0,08–0,15 aralığı bir hipotez olarak yazılır, hedef değildir.
**Kural E1.2.** Tek bir damarda ölçülen kazanç üç damara genellenmez; "yakınsak" sözcüğü ancak üç damarın üçünde de E1.1 sağlanırsa kullanılır.

## E2 — Karar dinamiği ve karşılaştırıcılar (bulgu 3)

**Kurgu.** İki koldan biri seçilir ve seçim koşudan önce yazılır: (a) iddia mevcut bağlamsal bant ortamına çekilir; (b) eylemin sonraki durumu değiştirdiği bir dinamik (örneğin uyarı → iş yükü ve yorgunluk göstergelerinin bir sonraki adımda düşmesi) kurulur. Bu ön kayıt **(a)**'yı seçer; (b) ayrı bir ön kayıt ister.
**Karşılaştırıcılar (zorunlu).** Maliyet-duyarlı lojistik sınıflandırıcı, derinliği ≤ 4 karar ağacı, çoğunluk sınıfı sabit politikası, hep-kritik sabit politikası ve sentetik etiket kuralının kendisi (üst sınır).
**Kural E2.1.** PPO, maliyet-duyarlı sınıflandırıcıyı makro-F1'de beş tohum ortalamasında **+0,05** geçmezse "DRL yöntem seçimi bu görevde gerekçelendirilemedi" yazılır. Rastgele politikayı geçmek ölçüt değildir.

## E3 — Ayrık test ve karar anı özellikleri (bulgu 4)

**Kurgu.** Bakım damarında olay ve şablon ailesi bazında ayrık test kümesi (%20, aile düzeyinde); aynı ailenin varyantları eğitim ve teste dağıtılmaz. Her özelliğin bilinme zaman damgası yazılır; kesinti süresi, maddi kayıp, kök neden katman sayısı ve alınan aksiyon sayısı **karar anı listesinden çıkarılır**.
**Kural E3.1.** Test kümesi sonucu eğitim kümesi sonucundan 5 puandan fazla düşerse bu fark "genelleme açığı" olarak raporlanır; ana tabloya yalnız test kümesi girer.

## E4 — Gerçek istemci ayrımı (bulgu 5)

**Kurgu.** Üç damarda istemci başına ayrık kayıt; sınıf ve özellik dağılımları istemci başına ölçülüp raporlanır (Jensen–Shannon uzaklığı ≥ 0,1 olmayan istemci çifti "benzeşik" damgası alır). Açık heterojenlik senaryosu: bir istemcide kritik sınıf payı iki kat.
**Kural E4.1.** "Non-IID" sözcüğü yalnız ölçülmüş dağılım farkı olan kurulumlar için kullanılır. Bir damarda sınanmayan özellik o damarda doğrulandı diye yazılmaz.

## E5 — FedProx (bulgu 6)

**Kurgu.** Yerel PPO kaybına μ/2 ‖w − w_g‖² terimi eklenir (özgün Algoritma 2); mevcut tek adımlı düzeltme "yakınlık düzeltmesi" adıyla ayrı kol olarak korunur.
**Kural E5.1.** İki kol aynı tohum ve bütçeyle koşulur; fark ne çıkarsa yazılır. Eski sonuçlar eski uygulamayla ilişkilendirilerek korunur, üstüne yazılmaz.

## E6 — Eşit bütçe ve maliyet (bulgu 7)

**Kurgu.** Merkezî ve birleşik kollar eşit tur (100/100) **ve** eşit toplam çevre geçişiyle iki ayrı eşleştirmede koşulur; duvar saati ve iletişim baytı kaydedilir.
**Kural E6.1.** "Birleşik toplama maliyeti" yalnız eşit geçiş eşleştirmesinden, yüzde puanı olarak yazılır; göreli yüzde kullanılmaz.

## E7 — Çoklu tohum ve belirsizlik (bulgu 19)

**Kurgu.** Her kol beş tohum (42, 43, 44, 45, 46); tohum düzeyinde yüzde 95 bootstrap güven aralığı (20 000 yeniden örnekleme).
**Kural E7.1.** Beş tohumla sıfırı içeren fark "ölçülemedi" diye yazılır; anlamlı fark bulunamaması eşdeğerlik göstermez.

## E8 — Mahremiyet (bulgu 2)

**Kurgu.** Koşudan önce seçilir ve yazılır: (a) Laplace mekanizması saf-DP olarak belgelenir: korunacak birim = istemci güncellemesi, komşuluk = bir istemcinin güncellemesinin değişmesi, L1 kırpma C ile duyarlılık = C, tur başına ε, T tur için temel bileşim; (b) Gauss mekanizmasına geçilir, L2 kırpma, (ε, δ) muhasebesi RDP ile. Tehdit modeli açıkça yazılır: güvenilir toplayıcı; güvenilmeyen koordinatör istenirse güvenli toplama ayrı bileşen olarak eklenir.

*[05.09.2026 · Ek 2 ile düzeltilmiştir: duyarlılık C değil 2C/n'dir; bu satır tarihçe olarak korunmuştur.]*

**Kural E8.1.** Toplam ε hesaplanana ve yazılana kadar "garanti" sözcüğü kullanılmaz; ε_toplam > 10 ise sonuç "anlamlı mahremiyet güvencesi vermez" diye yazılır.

## E9 — Korpus (bulgu 13, 14)

**Kurgu.** Kör insan kodlayıcı örneklemi: tabaka başına, hedef κ güven aralığı ±0,10 için gereken n (Cohen κ için Donner–Eliasziw yaklaşımıyla hesaplanır, koşudan önce yazılır); iki bağımsız uzman, uyuşmazlık çözümü üçüncü uzmanla. Seçilme olasılığı ağırlıklı duyarlılık analizi: T3/T4'ten 200'er örneğin seçilme oranıyla ağırlıklandırılmış RR.
**Kural E9.1.** Ağırlıklı RR ile ham RR'nin güven aralıkları örtüşmezse tezdeki 13,2 değeri ağırlıklı değerle **yan yana** yazılır, silinmez.

## Kapsam ve dil

Bu program tezin iddiasını genişletmez; v8'in daralttığı iddiayı deneyle destekleyip desteklemediğini ölçer. Olumsuz sonuç silinmez. "Elendi" yerine "bu görevde, bu bütçede, bu kurguda ölçülemedi" yazılır. Her deney bittiğinde bu belgeye tarihli Ek eklenir.

**Tahmini süre:** E1–E7 birlikte ~2 hafta (üç depo, CPU); E8 1 hafta; E9 insan kodlayıcıya bağlı, 2–3 hafta.

---

*05.09.2026'da yazıldı ve hiçbir koşu başlamadan donduruldu · LIMULUS karar 74 ön kayıt kalıbı devralındı*

---

## Ek 1 — Onay ve açık seçimlerin sabitlenmesi (05.09.2026, koşu başlamadan)

**Karar veren:** Mete ("v8 önerilerini onaylıyorum") · **Yazan:** Claude

1. Program **onaylandı**; E0–E9 kural ve eşikleri yukarıdaki hâliyle donmuş kalır.
2. **E2 → (a):** iddia mevcut bağlamsal bant ortamına çekilir; karşılaştırıcılar (maliyet-duyarlı lojistik, derinlik ≤ 4 ağaç, çoğunluk sınıfı, hep-kritik, etiket kuralı) zorunludur. (b) ayrı ön kayıt ister ve açılmamıştır.
3. **E8 → (a):** mevcut Laplace mekanizması saf-DP olarak belgelenir; korunacak birim = istemci güncellemesi, L1 kırpma C ile duyarlılık = C, tur başına ε ve T tur için temel bileşim; tehdit modeli güvenilir toplayıcı. Gauss/RDP koluna geçilmez. Kural E8.1 (ε_toplam yazılmadan "garanti" yok; > 10 ise "anlamlı güvence vermez") geçerlidir.

   *[05.09.2026 · Ek 2 ile düzeltilmiştir: duyarlılık C değil 2C/n'dir; bu satır tarihçe olarak korunmuştur.]*

4. **Makale hizası:** çatı makalesi (Information Fusion hattı) v44 ile tezle aynı kayıt tabanına çekildi; Faz E sonuçları tez v10 ve makale v45'e birlikte işlenir.
5. Bu Ek yazıldığında **hiçbir Faz E koşusu başlamamıştır.** İlk koşudan önce E0 gereği koşu kimliği, tohum, git özeti ve veri SHA-256 alanları kayıt şemasına eklenir.

---

## Ek 2 — E8 duyarlılık türetiminin düzeltilmesi (05.09.2026, koşu başlamadan)

**Öncül:** bağımsız denetim (Codex, 05.09.2026) · **Yazan:** Claude

1. **Hata beyanı.** Ek 1 madde 3'teki ve E8 (a) kolundaki "L1 kırpma C ile duyarlılık = C" ifadesi geri çekilir. Değiştirme komşuluğunda karşı örnek: u = +1, u′ = −1 için ‖u‖₁ = ‖u′‖₁ = 1 = C iken ‖u − u′‖₁ = 2 = 2C. Ek 1 silinmez; tarihçe olarak yerinde kalır ve bu madde ile birlikte okunur.

2. **Tam türetim.** Koordinatörün yayımladığı işlev f(D) = (1/n) Σ_i clip_L1(u_i, C). Komşuluk: tek bir istemcinin güncellemesi değişir, n sabit kalır (değiştirme komşuluğu). Buradan
   Δ₁ = max_{D∼D′} ‖f(D) − f(D′)‖₁ = (1/n)·max ‖clip_L1(u, C) − clip_L1(u′, C)‖₁ ≤ 2C/n,
   çünkü kırpılmış her güncellemenin L1 normu en çok C'dir ve üçgen eşitsizliği 2C sınırını verir; ortalama 1/n çarpanını taşır. Laplace mekanizması her koordinata bağımsız Lap(Δ₁/ε_tur) ekler ve tur başına ε_tur-DP sağlar (Dwork–Roth, Teorem 3.6). Koordinatlar arasında ayrıca bileşim yapılmaz: L1 duyarlılık vektörün tamamı için tanımlıdır, koordinat başına değil. Ekleme/çıkarma komşuluğu (n'in değiştiği durum) farklı bir sınır verir; bu ön kayıt **değiştirme komşuluğunu** seçer ve bu seçim koşu kaydında yinelenir. Mevcut `fedavg.py` bu türetimle uyuşmaz (kırpma yok, duyarlılık 0,01 sabiti); ilk Faz E koşusundan önce clip_L1 uygulanır ve ölçek Δ₁/ε_tur olarak koddan hesaplanır.

3. **Tur bileşimi.** T = 160 tur için temel ardışık bileşim: ε_toplam = T·ε_tur (saf DP). Gelişmiş bileşim bu ölçekte daha gevşektir; ε_tur = 1, δ = 10⁻⁵ için √(2T ln(1/δ))·ε + Tε(e^ε − 1) ≈ 335,6 > 160 = T·ε_tur, dolayısıyla temel bileşim kullanılır. Hedefler: ε_toplam ≤ 10 için ε_tur = 10/160 = 0,0625; ε_toplam ≤ 1 için ε_tur = 0,00625. Karşılık gelen Laplace ölçeği (2C/n)/ε_tur, yani sırasıyla 32C/n ve 320C/n. Kural E8.1 yürürlüktedir: ε_toplam yazılmadan "garanti" sözcüğü kullanılmaz, ε_toplam > 10 ise sonuç "anlamlı mahremiyet güvencesi vermez" diye yazılır.

4. **Kayıt gereği (E0).** C'nin nasıl seçildiği koşu kaydına yazılır: eğitim başlamadan, kırpılmamış istemci güncellemelerinin L1 normlarının medyanı üzerinden, sonuç görülmeden. C sonuca göre ayarlanmaz. Kayda ayrıca n, T, ε_tur, ε_toplam, Δ₁ = 2C/n ve kullanılan Laplace ölçeği koddan okunan hâliyle girer.

5. **Kapsam.** Bu düzeltme mevcut koşuları etkilemez; Faz A ve Faz C sonuçları için "bileşik mahremiyet bütçesi hesaplanamadı" ifadesi tez ve makalede olduğu gibi kalır. Bu Ek yazıldığında hiçbir Faz E koşusu başlamamıştır.

*05.09.2026 · E8 ve Ek 1 madde 3 ile birlikte okunur; önceki satırların hiçbiri değiştirilmedi*

---

## Ek 3 — bileşim gerekçesinin düzeltilmesi (05.09.2026, koşu başlamadan)

**Öncül:** bağımsız yenilik denetimi (05.09.2026), bulgu F1 ve F3 · **Yazan:** Claude

1. **Hata beyanı.** Ek 2 madde 3'teki "Gelişmiş bileşim bu ölçekte daha gevşektir" genellemesi geri çekilir. Cümlenin verdiği örnek doğrudur (ε_tur = 1'de gelişmiş bileşim 335,6 > 160), ancak genelleme aynı maddenin seçtiği çalışma noktalarında geçerli değildir. Ek 2 silinmez; tarihçe olarak yerinde kalır ve bu madde ile birlikte okunur.

2. **Yeniden hesap.** T = 160 tur, δ = 10⁻⁵, Dwork–Roth (2014) Teorem 3.20: ε' = √(2T ln(1/δ))·ε_tur + T·ε_tur·(e^{ε_tur} − 1).

   | ε_tur | Temel bileşim (T·ε_tur) | Gelişmiş bileşim | Hangisi sıkı |
   |---|---:|---:|---|
   | 1,0 | 160,00 | 335,62 | temel |
   | 0,0625 | 10,00 | 4,44 | gelişmiş |
   | 0,00625 | 1,00 | 0,39 | gelişmiş |

   Yani gelişmiş bileşim yalnız ε_tur ≈ 1 civarında daha gevşektir; bu ön kaydın seçtiği ε_tur = 0,0625 ve 0,00625 noktalarında gelişmiş bileşim sırasıyla 4,44 ve 0,39 vererek **daha sıkıdır**.

3. **Doğru gerekçe.** Temel bileşimin seçilme nedeni gevşeklik ya da sıkılık değildir. Gelişmiş bileşim (ε, δ)-DP verir; E8 (a) kolu ise **saf ε-DP** belgelemeyi seçmiştir ve δ > 0'a geçmemek için temel bileşim kullanılır. Ek 2 madde 3'ün "dolayısıyla temel bileşim kullanılır" sonucu geçerliliğini korur, gerekçesi bu maddeyle değiştirilir.

4. **Sonucun yönü.** Temel bileşim saf DP için her zaman geçerli bir üst sınırdır ve burada muhafazakâr bir üst sınır olarak kullanılır: koruma açığı doğmaz, yalnız gereğinden fazla gürültü konur. Aynı ε_tur = 0,0625 çalışma noktasında temel bileşimin verdiği sınır (10), gelişmiş bileşimin verdiğinin (4,44) yaklaşık 2,25 katıdır; gürültü karşılığı olarak, ε_toplam ≤ 10 hedefine gelişmiş bileşimle ε_tur ≈ 0,1226 ile ulaşılabildiğinden temel bileşim yaklaşık **1,96 kat** daha fazla gürültü koymaktadır (ε_toplam ≤ 1 hedefinde yaklaşık 2,53 kat). Kural E8.1 yürürlüktedir ve Ek 2 madde 4'ün kayıt gereği değişmemiştir.

5. **Sürüm eşlemesi (bulgu F3).** Ek 1 madde 4'teki sürüm eşlemesi aşılmıştır: v10 ve v45 Faz E öncesi düzeltme sürümleridir; Faz E sonuçları bir sonraki sürüm çiftine işlenecektir.

6. **Kapsam.** Bu Ek mevcut koşuları etkilemez ve E8'in kural ya da eşiklerini değiştirmez. Bu Ek yazıldığında hiçbir Faz E koşusu başlamamıştır.

*05.09.2026 · Ek 2 ve Ek 1 ile birlikte okunur; önceki satırların hiçbiri değiştirilmedi, yalnız E8 (a) ve Ek 1 madde 3'ün altına birer tarihli işaret satırı eklendi*

---

## Ek 4 — C'nin korunacak veriden bağımsız kalibrasyonla seçilmesi (05.09.2026, koşu başlamadan)

**Öncül:** Mete'nin millî kararı (05.09.2026): *"Ek 2'de C'nin korunacak istemci güncellemelerinin medyanından seçilmesi ayrıca sorunlu. Sonuçlardan bağımsız olmak tek başına mahremiyet sağlamaz. Bu tur C'yi korunacak veriden bağımsız, açık veya sentetik kalibrasyon verisiyle belirleyip dondur."* · **Yazan:** Claude

1. **Hata beyanı.** Ek 2 madde 4'teki "C, kırpılmamış **istemci** güncellemelerinin L1 normlarının medyanı üzerinden seçilir" yönergesi geri çekilir. Gerekçe: bu yordamda C, korunması gereken istemci güncellemelerinin bir istatistiğidir; kırpma eşiğinin kendisi veriye bağımlı bir yayım olur ve duyarlılık türetimi (Δ₁ ≤ 2C/n) C'nin veriden bağımsız bir sabit olması varsayımına dayanır. Sonuçtan bağımsız seçim (C'nin ölçüm görülmeden dondurulması) kayıt disiplini için gereklidir ama **mahremiyet için yeterli değildir**. Ek 2 silinmez; tarihçe olarak yerinde kalır ve bu madde ile birlikte okunur.

2. **Düzeltilmiş yordam (bu turda yürürlükte).** C, **korunacak hiçbir istemcinin verisine bakılmadan**, ayrı bir kalibrasyon kaynağından belirlenir:
   - Aynı sentetik üretici/ortam, **kalibrasyon tohumu** ile ayrı bir kalibrasyon kümesi üretir. Kalibrasyon tohumları: **BB3/ATM/MRO için 9042, 9043, 9044** (ana koşuların eğitim tohumları 42–46 ve değerlendirme tohumları 942–944 / reset 2026–2028 ile çakışmaz).
   - Bu kalibrasyon kümesinde, ana koşulardan bağımsız **kısa bir yerel eğitim koşusu** (3 kalibrasyon istemcisi × K tur) yapılır; her turda her istemcinin güncellemesi u = w_yerel − w_küresel için ‖u‖₁ ölçülür.
   - C = bu kalibrasyon L1 normlarının **medyanı**dır; iki anlamlı basamağa yuvarlanıp dondurulur.
   - Kalibrasyon kümesi **hiçbir istemcinin verisi değildir**, ana koşulara girmez, ana koşuların değerlendirme kümesiyle kesişmez ve C dışında hiçbir çıktısı kullanılmaz.
   - C, **hiçbir ana koşu sonucu görülmeden** dondurulur ve bu Ek'e sayı olarak yazılır. Sonuca göre ayarlanmaz.

3. **Kapsam sınırı (açıkça yazılır).** Kalibrasyon kümesi ana koşularla aynı sentetik üreticiden geldiği için, C üreticinin *dağılımına* ilişkin bilgi taşır; korunan istemcilerin *örneklerine* ilişkin bilgi taşımaz. Kalibrasyon verisinin kendisi mahremiyet talebinin konusu değildir (sentetik, açık, hiçbir kişiye/kuruma atfı yok). Bu, üretici dağılımının kamuya açık kabul edildiği bir modeldir ve koşu kaydına bu haliyle yazılır.

4. **Değişmeyenler.** Ek 2 madde 2'nin türetimi (değiştirme komşuluğu, sabit n, Δ₁ = 2C/n), Ek 2 madde 3'ün çalışma noktaları (T = 160; ε_toplam ≤ 10 için ε_tur = 0,0625; ε_toplam ≤ 1 için ε_tur = 0,00625) ve Ek 3'ün gerekçesi (saf ε-DP tercih edildiği için temel bileşim; δ > 0'a geçilmez) aynen yürürlüktedir. Kural E8.1 yürürlüktedir.

5. **Kanıt cümlesi (E8 raporlamasında zorunlu).** *Deney gürültüsünün eklenmiş olması tek başına diferansiyel mahremiyet kanıtı değildir; kanıt = (i) L1 kırpma C'nin koddan doğrulanmış uygulanışı + (ii) kırpmadan türetilmiş duyarlılık Δ₁ = 2C/n + (iii) kayıtlı ε_tur ve ε_toplam = T·ε_tur.* Bu üçlü kayıtta bulunmayan hiçbir koşu için "diferansiyel mahremiyet sağlandı" yazılmaz.

6. **Kapsam.** Bu Ek yazıldığında **hiçbir Faz E ana koşusu başlamamıştır**; yalnız E0 kayıt modülünün duman testi koşulmuştur (deney değil, kayıt düzeni testi). Dondurulan C değerleri aşağıya, kalibrasyon koşusu biter bitmez ve hiçbir ana koşu sonucu görülmeden yazılır.

**Dondurulan C değerleri (kalibrasyon koşusundan; ana koşu sonucu görülmeden):**

| Damar | Kalibrasyon tohumu | Ölçülen L1 normu (n) | Medyan | **C (dondurulmuş)** | n | Δ₁ = 2C/n | Laplace ölçeği (ε_toplam ≤ 10) | Laplace ölçeği (ε_toplam ≤ 1) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CDSA-BB3 | 9042 | 15 | 9.0422 | **9.0** | 3 | 6.0000 | 96.00 | 960.0 |
| CDSA-MRO | 9044 | 15 | 9.3638 | **9.4** | 3 | 6.2667 | 100.27 | 1002.7 |
| CDSA-ATM | 9043 | 15 | 10.8570 | **11.0** | 3 | 7.3333 | 117.33 | 1173.3 |

Kalibrasyon koşusu: her damarda 3 kalibrasyon istemcisi × 5 tur = 15 güncelleme L1 normu; C = medyanın iki anlamlı basamağa yuvarlanmışı. Kalibrasyon kayıtları: `experiments/results/faz_e8_C.json` ve E0 koşu kaydı `experiments/results/e_kayit/CDSA-*-E8-kalibrasyon_C-t90xx-*.json`. Çalışma noktaları T = 160 tur ve Ek 2 madde 3'ün ε_tur değerleri (0,0625 ve 0,00625) ile hesaplanmıştır.

Bu tablo yazıldığında hiçbir E8 ana koşusu koşulmamış, hiçbir Faz E sonucu görülmemiştir. C bundan sonra değiştirilmez.

*05.09.2026 · Ek 2 madde 4 ile birlikte okunur; önceki satırların hiçbiri değiştirilmedi*

---

## Ek 5 — Faz E başlangıç kaydı (05.09.2026)

**Yazan:** Claude · **Öncül:** Mete'nin millî kararı (05.09.2026) · **Kapsam:** bu Ek, koşulan adımları ve ölçülen sayıları kayda geçirir; E0–E9'un kural ve eşiklerinden hiçbirini değiştirmez.

### 1. Koşulan adımlar

| # | Adım | Durum | Çıktı |
|---|---|---|---|
| 0 | **Ek 4** — C'nin korunacak veriden bağımsız kalibrasyonla seçilmesi | yazıldı, koşu başlamadan | bu belge, Ek 4 |
| 1 | **E0** kayıt disiplini modülü (`experiments/faz_e_kayit.py`, üç depoda birebir kopya) | koşuldu, duman testi geçti | JSON şema + doğrulama CLI; 13/13 zorunlu alan düşürülünce hata |
| 2a | **E3** aile bazlı ayrık test (MRO) | koşuldu | `results/faz_e3_ayrim.json` |
| 2b | **E4** istemci başına ayrık kayıt + JS ölçümü (üç damar) | koşuldu | `results/faz_e4_istemci_ayrimi[_heteroj].json` |
| 2c | Faz A regresyonu (yama sonrası eski komut aynı sonucu veriyor mu) | koşuldu, **bit-birebir aynı** | BB3: random, merkezî PPO, merkezî ve FedAvg öğrenme eğrileri özdeş |

*[05.09.2026 · Ek 6 ile daraltıldı: madde 2c'deki "bit-birebir" hükmü YALNIZ **yama sonrası kod ile yama öncesi HEAD kodunun aynı ortamda yeniden koşulmasının** karşılaştırmasıdır; depoda kayıtlı `faz_a_results.json` (11.06.2026) ile karşılaştırma DEĞİLDİR. Tarihsel kayıt bugünkü kodla birebir yeniden üretilememiştir — bkz. Ek 6.]*
| 3 | **E8** `fedavg.py` L1 kırpma + Δ₁ = 2C/n + Laplace + ε_toplam defteri | koşuldu | 15/15 birim testi üç damarda geçti |
| 4 | **E2** karşılaştırıcılar, 1.800 karar protokolü, beş tohum | koşuldu | `results/faz_e2_karsilastiricilar.json` |
| 5 | Kampanya (bekçi + flock kuyruk) | başlatıldı | `faz_e_kuyruk.{json,log}` |
| 6 | **E9** kör kodlama paketi | hazırlandı | `kkt/FAZ_E9_KOR_KODLAMA/` — ⏳ İNSAN KAYNAĞI ve VERİ ERİŞİMİ BEKLİYOR |

### 2. Dondurulan C değerleri (Ek 4'ten; ana koşu sonucu görülmeden)

| Damar | Kalibrasyon tohumu | L1 medyan | **C** | Δ₁ = 2C/n (n = 3) |
|---|---:|---:|---:|---:|
| CDSA-BB3 | 9042 | 9.0422 | **9.0** | 6.0000 |
| CDSA-MRO | 9044 | 9.3638 | **9.4** | 6.2667 |
| CDSA-ATM | 9043 | 10.8570 | **11.0** | 7.3333 |

> *Gürültü eklenmesi tek başına DP kanıtı değildir; kanıt = kırpma + türetilmiş duyarlılık (2C/n) + kayıtlı ε_toplam.* (Ek 4 madde 5)

### 3. E4 — istemci başına ayrık kayıt ve JS uzaklıkları

| Damar | Senaryo | İstemci kayıtları ayrık mı | Sınıf JS (0-1 / 0-2 / 1-2) | E4.1 hükmü |
|---|---|---|---|---|
| CDSA-BB3 | temel ayrık | evet | 0.0327 / 0.0214 / 0.0302 | **'Non-IID' YAZILAMAZ** — bütün çiftler benzeşik (JS < 0,10) |
| CDSA-BB3 | açık heterojenlik (kritik pay 2×) | evet | 0.1913 / 0.2168 / 0.0302 | 'Non-IID' yazılabilir (çiftler: 0-1, 0-2) |
| CDSA-MRO | temel ayrık | evet | 0.0909 / 0.0584 / 0.0738 | **'Non-IID' YAZILAMAZ** — bütün çiftler benzeşik (JS < 0,10) |
| CDSA-MRO | açık heterojenlik (kritik pay 2×) | evet | 0.0995 / 0.1562 / 0.0738 | 'Non-IID' yazılabilir (çiftler: 0-2) |
| CDSA-ATM | temel ayrık | evet | 0.0288 / 0.0460 / 0.0292 | **'Non-IID' YAZILAMAZ** — bütün çiftler benzeşik (JS < 0,10) |
| CDSA-ATM | açık heterojenlik (kritik pay 2×) | evet | 0.2726 / 0.2935 / 0.0292 | 'Non-IID' yazılabilir (çiftler: 0-1, 0-2) |

### 4. E3 — aile bazlı ayrık test (CDSA-MRO)

- **Aile alanı:** veride ve `schema.json`'da açık bir *şablon ailesi* alanı **yoktur**. Üreticide şablon havuzları `olay_turu` anahtarıyla tutulduğu için aile, `olay_ozeti.olay_turu` alanından **türetilmiştir** (15 aile). Yedek yordam `olay_kimligi_bazli_ayrim` adıyla kayda geçmiştir ve **bu turda kullanılmamıştır**.
- **Ayrım:** test aileleri = fidye_yazilimi, konfigurasyon_hatasi, usb_zararli_yazilim; n_test = 218 (21.8%), n_eğitim = 782. Aile örtüşmesi yok: True; kayıt örtüşmesi yok: True.
- **Karar anı özellik listesi (6 özellik):** olay_turu_id, mitre_tactic, etkilenen_hizmet_sayisi, kvkk_ozel_veri, shy145_72saat_uygunluk, ek19_kontrol_atfi_sayisi.
- **Çıkarılanlar (ön kayıt E3 gereği):** kesinti_suresi_dk, tahmini_maddi_kayip_TL, swiss_cheese_katman_sayisi, aksiyon_sayisi — her biri için bilinme zaman damgası `faz_e3_ayrim.json` içinde yazılıdır.
- **E3.1 hükmü: koşulmadı** — ayrık test kümesiyle eğitim/test karşılaştırması bu turda koşulmamıştır (ayrım ve karar anı listesi hazırlandı, eğitim koşusu kuyrukta değil).
  - *[06.09.2026 · Ek 8 ile koşuldu: E3.1 karşılaştırması sekiz kolda (maliyet-duyarlı lojistik, karar ağacı d≤4, üç sabit politika, etiket kuralı üst sınırı, PPO merkezî ve PPO FedAvg) tamamlanmıştır. Ayrım, karar anı listesi ve 5 puanlık eşik **değişmemiştir**; yukarıdaki satır tarihçe olarak yerinde bırakılmıştır. Sonuçlar: `experiments/results/faz_e3_ayrik_degerlendirme.json`, hüküm tablosu Ek 8 §4'tedir.]*

### 5. E2 — karşılaştırıcılar (1.800 karar, beş tohum: 42–46)

Makro-F1, ortalama ± örneklem standart sapması. Değerlendirme kümesi bütün kollarda özdeştir (`faz_e0_esdeger_degerlendirme.py` protokolü).

| Karşılaştırıcı | CDSA-BB3 | CDSA-MRO | CDSA-ATM |
|---|---|---|---|
| Etiket kuralı (üst sınır) | 1.0000 ± 0.0000 | 0.8000 ± 0.0000 | 1.0000 ± 0.0000 |
| Karar ağacı (derinlik ≤ 4) | 0.7042 ± 0.0012 | 0.4832 ± 0.0648 | 0.9996 ± 0.0005 |
| Maliyet-duyarlı lojistik | 0.4290 ± 0.0072 | 0.4103 ± 0.0032 | 0.8959 ± 0.0079 |

*[05.09.2026 düzeltme: aşağıdaki tablonun **Doğruluk** sütunu yanlış alandan basılmıştı (`kritik_duyarlilik_ort`, `faz_e_ek5_yaz.py:118/123`); dokuz hücrenin tamamı hatalıdır. Makro-F1 sütunu ve buna dayanan bütün hükümler doğrudur ve DEĞİŞMEMİŞTİR. Doğru tablo Ek 7'dedir; aşağıdaki tablo tarihçe olarak yerinde bırakılmıştır.]*

Sabit politikalar (aynı protokol):

| Sabit politika | Damar | Makro-F1 | Doğruluk |
|---|---|---:|---:|
| sabit_cogunluk_a0 | CDSA-BB3 | 0.1736 | 0.0 |
| sabit_hep_kritik_a3 | CDSA-BB3 | 0.0896 | 1.0 |
| sabit_cogunluk_a3 | CDSA-MRO | 0.1218 | 0.5 |
| sabit_cogunluk_a4 | CDSA-MRO | 0.1197 | 0.5 |
| sabit_hep_kritik_a3 | CDSA-MRO | 0.1218 | 0.5 |
| sabit_hep_kritik_a4 | CDSA-MRO | 0.1197 | 0.5 |
| sabit_cogunluk_a0 | CDSA-ATM | 0.1031 | 0.0 |
| sabit_hep_kritik_a3 | CDSA-ATM | 0.0677 | 0.5 |
| sabit_hep_kritik_a4 | CDSA-ATM | 0.0476 | 0.5 |

**PPO kolları ve Kural E2.1 hükmü** (eşik +0,05; referans = maliyet-duyarlı lojistik):

| Damar | PPO kolu | n tohum | PPO makro-F1 | Fark | E2.1 hükmü |
|---|---|---:|---:|---:|---|
| CDSA-ATM | merkezi | 5 | 0.2498 | -0.6461 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-ATM | fedavg | 5 | 0.1772 | -0.7187 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-ATM | fedprox_gercek | 5 | 0.1772 | -0.7187 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-ATM | fedprox_yakinlik | 5 | 0.1725 | -0.7234 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-BB3 | merkezi | 5 | 0.3514 | -0.0776 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-BB3 | fedavg | 5 | 0.3498 | -0.0792 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-BB3 | fedprox_gercek | 5 | 0.3498 | -0.0792 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-BB3 | fedprox_yakinlik | 5 | 0.3502 | -0.0788 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-MRO | merkezi | 5 | 0.1197 | -0.2906 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-MRO | fedavg | 5 | 0.1686 | -0.2417 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-MRO | fedprox_gercek | 5 | 0.1475 | -0.2628 | DRL yontem secimi bu gorevde gerekcelendirilemedi |
| CDSA-MRO | fedprox_yakinlik | 5 | 0.1390 | -0.2713 | DRL yontem secimi bu gorevde gerekcelendirilemedi |

### 6. Kampanya durumu

Kuyruk: **{'bekliyor': 0, 'kosuyor': 0, 'tamam': 145, 'hata': 0, 'kosulamadi': 5}** (toplam 150 iş). Öncelik sırası: E6/E7 merkezi, E6/E7 fedavg, E5 fedprox_gercek, E5 fedprox_yakinlik, E8 eps10, E8 eps1, E4 heterojen, E4 ayrik, E1 tekmodlu, E1 cokmodlu.

| Damar / kol | tamam | koşuyor | bekliyor | koşulamadı | hata |
|---|---:|---:|---:|---:|---:|
| CDSA-ATM/dp_eps1 | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/dp_eps10 | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/e1_cokmodlu | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/e1_tekmodlu | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/e4_ayrik_fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/e4_heteroj_fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/fedprox_gercek | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/fedprox_yakinlik | 5 | 0 | 0 | 0 | 0 |
| CDSA-ATM/merkezi | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/dp_eps1 | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/dp_eps10 | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/e1_cokmodlu | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/e1_tekmodlu | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/e4_ayrik_fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/e4_heteroj_fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/fedprox_gercek | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/fedprox_yakinlik | 5 | 0 | 0 | 0 | 0 |
| CDSA-BB3/merkezi | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/dp_eps1 | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/dp_eps10 | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/e1_cokmodlu | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/e1_tekmodlu | 0 | 0 | 0 | 5 | 0 |
| CDSA-MRO/e4_ayrik_fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/e4_heteroj_fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/fedavg | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/fedprox_gercek | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/fedprox_yakinlik | 5 | 0 | 0 | 0 | 0 |
| CDSA-MRO/merkezi | 5 | 0 | 0 | 0 | 0 |

### 7. Tamamlanan kolların sonuçları ve kural hükümleri

**CDSA-ATM** — makro-F1, beş tohum ortalaması ± ss, %95 bootstrap GA (20.000 yeniden örnekleme):

| Kol | Deney | n tohum | Makro-F1 | GA%95 | Duvar saati (sn) | Çevre geçişi | İletişim (bayt) |
|---|---|---:|---:|---|---:|---:|---:|
| etiket_kurali_ust_sinir | E2 | 5 | 1.0000 ± 0.0000 | [1.0, 1.0] | None | None | None |
| karar_agaci_d4 | E2 | 5 | 0.9996 ± 0.0005 | [0.9991, 0.9999] | None | None | None |
| maliyet_lojistik | E2 | 5 | 0.8959 ± 0.0079 | [0.8899, 0.9023] | None | None | None |
| merkezi | E6 | 5 | 0.2498 ± 0.0140 | [0.2381, 0.2593] | 38.68 | 172800 | None |
| e4_ayrik_fedavg | E4 | 5 | 0.2155 ± 0.0826 | [0.1412, 0.2539] | 32.47 | 172800 | 5865600 |
| e1_cokmodlu | E1 | 5 | 0.1772 ± 0.1002 | [0.1025, 0.2519] | 38.48 | 172800 | 5865600 |
| fedavg | E6 | 5 | 0.1772 ± 0.1002 | [0.1025, 0.2519] | 39.76 | 172800 | 5865600 |
| fedprox_gercek | E5 | 5 | 0.1772 ± 0.1002 | [0.1021, 0.2523] | 40.04 | 172800 | 5865600 |
| fedprox_yakinlik | E5 | 5 | 0.1725 ± 0.1052 | [0.0916, 0.2504] | 39.44 | 172800 | 5865600 |
| e4_heteroj_fedavg | E4 | 5 | 0.1374 ± 0.1050 | [0.0597, 0.2174] | 33.17 | 172800 | 5865600 |
| dp_eps1 | E8 | 5 | 0.1261 ± 0.0600 | [0.0787, 0.1735] | 64.32 | 276480 | 9384960 |
| dp_eps10 | E8 | 5 | 0.1260 ± 0.0602 | [0.0785, 0.1735] | 62.38 | 276480 | 9384960 |
| sabit_cogunluk_a0 | E2 | 5 | 0.1031 ± 0.0000 | [0.1031, 0.1031] | None | None | None |
| sabit_hep_kritik_a3 | E2 | 5 | 0.0677 ± 0.0000 | [0.0677, 0.0677] | None | None | None |
| e1_tekmodlu | E1 | 5 | 0.0516 ± 0.0090 | [0.0476, 0.0597] | 40.68 | 172800 | 5865600 |
| sabit_hep_kritik_a4 | E2 | 5 | 0.0476 ± 0.0000 | [0.0476, 0.0476] | None | None | None |

- **E1.1:** `{"cok_eksi_tek_makro_f1": 0.1256, "esik": 0.05, "hukum": "kazanc olculdu"}`
- **E5.1:** `{"fark_makro_f1_gercek_eksi_yakinlik": 0.0047, "gercek_GA95": [0.1021, 0.2523], "yakinlik_GA95": [0.0916, 0.2504], "hukum": "iki kol ayni tohum ve butceyle kosuldu; fark +0.0047 yazildi"}`
- **E6.1:** `{"esit_gecis_mi": true, "merkezi_gecis": 172800, "fedavg_gecis": 172800, "makro_f1_farki_yuzde_puani": -7.26, "hukum": "birlesik toplama maliyeti = +7.26 yuzde puani (makro-F1; esit tur VE esit gecis)", "duvar_saati_merkezi_sn": 38.68, "duvar_saati_fedavg_sn": 39.76, "iletisim_bayt_merkezi": null, "iletisim_bayt_fedavg": 5865600}`
- **E8.1:** `{"dp_eps10": {"eps_toplam": 10.0, "n_tohum": 5, "makro_f1_ort": 0.126, "hukum": "eps_toplam = 10 hesaplandi ve yazildi; 'garanti' sozcugu ancak bu kayitla birlikte kullanilir", "kanit_ucluSu": "kirpma (C) + duyarlilik 2C/n + kayitli eps_toplam"}, "dp_eps1": {"eps_toplam": 1.0, "n_tohum": 5, "makro_f1_ort": 0.1261, "hukum": "eps_toplam = 1 hesaplandi ve yazildi; 'garanti' sozcugu ancak bu kayitla birlikte kullanilir", "kanit_ucluSu": "kirpma (C) + duyarlilik 2C/n + kayitli eps_toplam"}}`
- **E4.1:** `{"temel_ayrik": {"cift_sinif_js": {"0-1": 0.0288, "0-2": 0.046, "1-2": 0.0292}, "non_iid_ciftler": [], "hukum": "'Non-IID' YAZILAMAZ — butun ciftler benzesik (JS < 0,10)"}, "acik_heterojenlik": {"cift_sinif_js": {"0-1": 0.2726, "0-2": 0.2935, "1-2": 0.0292}, "non_iid_ciftler": ["0-1", "0-2"], "hukum": "'Non-IID' yazilabilir (olculmus fark var)"}, "egitim_farki": {"heteroj_makro_f1": 0.1374, "ayrik_makro_f1": 0.2155, "fark": -0.0781, "n_tohum": [5, 5]}}`

**CDSA-BB3** — makro-F1, beş tohum ortalaması ± ss, %95 bootstrap GA (20.000 yeniden örnekleme):

| Kol | Deney | n tohum | Makro-F1 | GA%95 | Duvar saati (sn) | Çevre geçişi | İletişim (bayt) |
|---|---|---:|---:|---|---:|---:|---:|
| etiket_kurali_ust_sinir | E2 | 5 | 1.0000 ± 0.0000 | [1.0, 1.0] | None | None | None |
| karar_agaci_d4 | E2 | 5 | 0.7042 ± 0.0012 | [0.7032, 0.705] | None | None | None |
| maliyet_lojistik | E2 | 5 | 0.4290 ± 0.0072 | [0.4237, 0.435] | None | None | None |
| merkezi | E6 | 5 | 0.3514 ± 0.0124 | [0.3424, 0.362] | 29.0 | 172800 | None |
| fedprox_yakinlik | E5 | 5 | 0.3502 ± 0.0101 | [0.3427, 0.3587] | 29.01 | 172800 | 4939200 |
| e1_cokmodlu | E1 | 5 | 0.3498 ± 0.0110 | [0.3422, 0.3589] | 27.59 | 172800 | 4939200 |
| fedavg | E6 | 5 | 0.3498 ± 0.0110 | [0.3422, 0.3589] | 28.62 | 172800 | 4939200 |
| fedprox_gercek | E5 | 5 | 0.3498 ± 0.0116 | [0.3416, 0.3596] | 28.41 | 172800 | 4939200 |
| e4_ayrik_fedavg | E4 | 5 | 0.3383 ± 0.0114 | [0.3291, 0.3463] | 31.09 | 172800 | 4939200 |
| e1_tekmodlu | E1 | 5 | 0.3306 ± 0.0045 | [0.3272, 0.3342] | 30.19 | 172800 | 4939200 |
| e4_heteroj_fedavg | E4 | 5 | 0.3207 ± 0.0218 | [0.3038, 0.3377] | 30.68 | 172800 | 4939200 |
| sabit_cogunluk_a0 | E2 | 5 | 0.1736 ± 0.0000 | [0.1736, 0.1736] | None | None | None |
| dp_eps1 | E8 | 5 | 0.1188 ± 0.0508 | [0.0815, 0.1606] | 46.36 | 276480 | 7902720 |
| dp_eps10 | E8 | 5 | 0.1188 ± 0.0509 | [0.0814, 0.1605] | 47.23 | 276480 | 7902720 |
| sabit_hep_kritik_a3 | E2 | 5 | 0.0896 ± 0.0000 | [0.0896, 0.0896] | None | None | None |

- **E1.1:** `{"cok_eksi_tek_makro_f1": 0.0192, "esik": 0.05, "hukum": "kazanc olculemedi"}`
- **E5.1:** `{"fark_makro_f1_gercek_eksi_yakinlik": -0.0004, "gercek_GA95": [0.3416, 0.3596], "yakinlik_GA95": [0.3427, 0.3587], "hukum": "iki kol ayni tohum ve butceyle kosuldu; fark -0.0004 yazildi"}`
- **E6.1:** `{"esit_gecis_mi": true, "merkezi_gecis": 172800, "fedavg_gecis": 172800, "makro_f1_farki_yuzde_puani": -0.16, "hukum": "birlesik toplama maliyeti = +0.16 yuzde puani (makro-F1; esit tur VE esit gecis)", "duvar_saati_merkezi_sn": 29.0, "duvar_saati_fedavg_sn": 28.62, "iletisim_bayt_merkezi": null, "iletisim_bayt_fedavg": 4939200}`
- **E8.1:** `{"dp_eps10": {"eps_toplam": 10.0, "n_tohum": 5, "makro_f1_ort": 0.1188, "hukum": "eps_toplam = 10 hesaplandi ve yazildi; 'garanti' sozcugu ancak bu kayitla birlikte kullanilir", "kanit_ucluSu": "kirpma (C) + duyarlilik 2C/n + kayitli eps_toplam"}, "dp_eps1": {"eps_toplam": 1.0, "n_tohum": 5, "makro_f1_ort": 0.1188, "hukum": "eps_toplam = 1 hesaplandi ve yazildi; 'garanti' sozcugu ancak bu kayitla birlikte kullanilir", "kanit_ucluSu": "kirpma (C) + duyarlilik 2C/n + kayitli eps_toplam"}}`
- **E4.1:** `{"temel_ayrik": {"cift_sinif_js": {"0-1": 0.0327, "0-2": 0.0214, "1-2": 0.0302}, "non_iid_ciftler": [], "hukum": "'Non-IID' YAZILAMAZ — butun ciftler benzesik (JS < 0,10)"}, "acik_heterojenlik": {"cift_sinif_js": {"0-1": 0.1913, "0-2": 0.2168, "1-2": 0.0302}, "non_iid_ciftler": ["0-1", "0-2"], "hukum": "'Non-IID' yazilabilir (olculmus fark var)"}, "egitim_farki": {"heteroj_makro_f1": 0.3207, "ayrik_makro_f1": 0.3383, "fark": -0.0176, "n_tohum": [5, 5]}}`

**CDSA-MRO** — makro-F1, beş tohum ortalaması ± ss, %95 bootstrap GA (20.000 yeniden örnekleme):

| Kol | Deney | n tohum | Makro-F1 | GA%95 | Duvar saati (sn) | Çevre geçişi | İletişim (bayt) |
|---|---|---:|---:|---|---:|---:|---:|
| etiket_kurali_ust_sinir | E2 | 5 | 0.8000 ± 0.0000 | [0.8, 0.8] | None | None | None |
| karar_agaci_d4 | E2 | 5 | 0.4832 ± 0.0648 | [0.4522, 0.5415] | None | None | None |
| maliyet_lojistik | E2 | 5 | 0.4103 ± 0.0032 | [0.4074, 0.4121] | None | None | None |
| e1_cokmodlu | E1 | 5 | 0.1686 ± 0.0502 | [0.1289, 0.2084] | 27.56 | 172800 | 5251200 |
| fedavg | E6 | 5 | 0.1686 ± 0.0502 | [0.1289, 0.2084] | 28.12 | 172800 | 5251200 |
| fedprox_gercek | E5 | 5 | 0.1475 ± 0.0263 | [0.1278, 0.1671] | 28.75 | 172800 | 5251200 |
| fedprox_yakinlik | E5 | 5 | 0.1390 ± 0.0234 | [0.1212, 0.1569] | 28.27 | 172800 | 5251200 |
| e4_heteroj_fedavg | E4 | 5 | 0.1341 ± 0.0310 | [0.1197, 0.1621] | 32.62 | 172800 | 5251200 |
| sabit_cogunluk_a3 | E2 | 1 | 0.1218 ± 0.0000 | — | None | None | None |
| sabit_hep_kritik_a3 | E2 | 5 | 0.1218 ± 0.0000 | [0.1218, 0.1218] | None | None | None |
| e4_ayrik_fedavg | E4 | 5 | 0.1201 ± 0.0009 | [0.1197, 0.121] | 32.37 | 172800 | 5251200 |
| merkezi | E6 | 5 | 0.1197 ± 0.0000 | [0.1197, 0.1197] | 28.15 | 172800 | None |
| sabit_cogunluk_a4 | E2 | 4 | 0.1197 ± 0.0000 | [0.1197, 0.1197] | None | None | None |
| sabit_hep_kritik_a4 | E2 | 5 | 0.1197 ± 0.0000 | [0.1197, 0.1197] | None | None | None |
| dp_eps1 | E8 | 5 | 0.0801 ± 0.0437 | [0.0471, 0.1131] | 45.52 | 276480 | 8401920 |
| dp_eps10 | E8 | 5 | 0.0799 ± 0.0438 | [0.0469, 0.1129] | 45.87 | 276480 | 8401920 |

- **E1.1:** `{"hukum": "kosulamadi — bu damarda cok-modlu/tek-modlu basligi uygulanmamistir (MODALITY_GROUPS bos)"}`
- **E5.1:** `{"fark_makro_f1_gercek_eksi_yakinlik": 0.0085, "gercek_GA95": [0.1278, 0.1671], "yakinlik_GA95": [0.1212, 0.1569], "hukum": "iki kol ayni tohum ve butceyle kosuldu; fark +0.0085 yazildi"}`
- **E6.1:** `{"esit_gecis_mi": true, "merkezi_gecis": 172800, "fedavg_gecis": 172800, "makro_f1_farki_yuzde_puani": 4.89, "hukum": "birlesik toplama maliyeti = -4.89 yuzde puani (makro-F1; esit tur VE esit gecis)", "duvar_saati_merkezi_sn": 28.15, "duvar_saati_fedavg_sn": 28.12, "iletisim_bayt_merkezi": null, "iletisim_bayt_fedavg": 5251200}`
- **E8.1:** `{"dp_eps10": {"eps_toplam": 10.0, "n_tohum": 5, "makro_f1_ort": 0.0799, "hukum": "eps_toplam = 10 hesaplandi ve yazildi; 'garanti' sozcugu ancak bu kayitla birlikte kullanilir", "kanit_ucluSu": "kirpma (C) + duyarlilik 2C/n + kayitli eps_toplam"}, "dp_eps1": {"eps_toplam": 1.0, "n_tohum": 5, "makro_f1_ort": 0.0801, "hukum": "eps_toplam = 1 hesaplandi ve yazildi; 'garanti' sozcugu ancak bu kayitla birlikte kullanilir", "kanit_ucluSu": "kirpma (C) + duyarlilik 2C/n + kayitli eps_toplam"}}`
- **E4.1:** `{"temel_ayrik": {"cift_sinif_js": {"0-1": 0.0909, "0-2": 0.0584, "1-2": 0.0738}, "non_iid_ciftler": [], "hukum": "'Non-IID' YAZILAMAZ — butun ciftler benzesik (JS < 0,10)"}, "acik_heterojenlik": {"cift_sinif_js": {"0-1": 0.0995, "0-2": 0.1562, "1-2": 0.0738}, "non_iid_ciftler": ["0-2"], "hukum": "'Non-IID' yazilabilir (olculmus fark var)"}, "egitim_farki": {"heteroj_makro_f1": 0.1341, "ayrik_makro_f1": 0.1201, "fark": 0.014, "n_tohum": [5, 5]}}`

- **E1.2:** 'yakinsak' YAZILAMAZ — E1.1 uc damarin ucunde de saglanmadi (en az bir damarda kosulamadi/kosulmadi)
- **E7.1:** beş tohumla sıfırı içeren fark 'ölçülemedi' diye yazılır; yukarıdaki GA%95 sütunları bu hükmün dayanağıdır.
- **E9.1:** koşulmadı — insan kodlaması yapılmamıştır (paket hazır, ⏳ İNSAN KAYNAĞI BEKLİYOR).

### 8. Koşulmayanlar (açıkça)

- **E3.1** (genelleme açığı): ayrım hazırlandı, eğitim/test karşılaştırma koşusu **koşulmadı**. *[06.09.2026 · Ek 8 ile koşuldu; bu satır tarihçedir.]*
- **E1 (CDSA-MRO çok-modlu):** `MODALITY_GROUPS` boştur; çok-modlu başlık bu damarda **uygulanmamıştır** — *koşulamadı*.
- **E9 insan kodlaması:** gerçek bağımsız kodlayıcı yoktur; hazırlık tamamlandı, **insan kaynağı bekliyor**. Ajan değerlendirmesi kör insan kodlamasının yerine **konulmamıştır**.
- **E2 (b) kolu** (eylemin sonraki durumu değiştirdiği dinamik): ayrı ön kayıt ister, açılmadı.

*05.09.2026 · Ek 1–4 ile birlikte okunur; önceki satırların hiçbiri değiştirilmedi. Bu Ek'teki hiçbir sayı, sonuç görüldükten sonra değiştirilmiş bir eşik ya da kuraldan türememiştir.*

---

## Ek 6 — Faz A merkezî kaydın yeniden üretim denemesi (05.09.2026)

**Öncül:** Ek 5 madde 2c'nin kapsamı üzerine koordinatör sorusu · **Yazan:** Claude
**Kapsam uyarısı:** Bu Ek hiçbir kuralı, eşiği veya ön kayıt hükmünü değiştirmez; yalnız
tarihsel bir kaydın bugünkü kodla yeniden üretilip üretilemediğini belgeler.

### 1. Ek 5 madde 2c'nin kapsamı (düzeltme değil, daraltma)

Madde 2c'deki **"bit-birebir aynı"** hükmü, yürütülen karşılaştırmayı tam adlandırmıyordu.
Hüküm şu karşılaştırmaya dayanıyordu: **Faz E yaması uygulanmış çalışma ağacı** ile
**`git archive HEAD` ile çıkarılmış yama öncesi kod**, *aynı kapta, aynı anda, aynı komutla*
koşuldu; rastgele kol, merkezî PPO üçlüsü ve **hem merkezî hem FedAvg öğrenme eğrilerinin
tamamı** özdeş çıktı. Bu, "Faz E yaması Faz A davranışını değiştirmedi" demektir ve bu
haliyle geçerlidir. Hüküm, depoda kayıtlı `experiments/results/faz_a_results.json`
(tarih alanı **11.06.2026**) ile bir karşılaştırma **değildi**. Madde 2c'nin altına bu
Ek'e işaret eden tarihli bir satır eklenmiştir; madde silinmemiştir.

### 2. Bugün koşulan komut

```
cd CDSA-BB3/12_GitHub_Repo/cdsa-bb3/experiments
python3 faz_a_staged.py base          # tohum 42, 100 tur, 600 adım değerlendirme
```
Komut bir kez koşuldu (26,7 sn). `faz_a_results.json` ve `faz_a_curves.json` koşudan önce
yedeklendi, koşudan sonra **birebir geri konuldu**; SHA-256 özetleri koşu öncesiyle aynıdır
(`4a09dd27…20cc5` ve `41223d44…4b88f`). **Bu iki dosya değişmemiştir.**
Yeniden üretim koşusu ayrıca E0 şemasıyla, karışıklık matrisi ve tahmin dosyasıyla birlikte
şuraya yazılmıştır (yeni dosya):
`experiments/results/e_kayit/CDSA-BB3-E0-faz_a_merkezi_yeniden_uretim-t42-20260905T222748Z.json`
Betik: `experiments/faz_a_yeniden_uretim.py`.

### 3. Kayıt ile bugünkü değerler

| Kol | Ölçüt | Kayıtlı (11.06.2026) | Bugün (05.09.2026) | Aynı mı |
|---|---|---:|---:|---|
| Rastgele | ortalama ödül | −3,67 | −3,67 | **evet** |
| Rastgele | doğruluk % | 24,8 | 24,8 | **evet** |
| Rastgele | kritik duyarlılık | 0,26 | 0,26 | **evet** |
| Merkezî PPO | ortalama ödül | **5,17** | **5,16** | hayır |
| Merkezî PPO | doğruluk % | **65,3** | **65,7** | hayır |
| Merkezî PPO | kritik duyarlılık | **0,858** | **0,843** | hayır |

Merkezî PPO öğrenme eğrisi (12 sonda, her 8 turda bir):
kayıtlı `[1.18, 2.63, 4.45, 3.48, 4.52, 4.72, 4.8, 5.2, 3.88, 4.55, 5.12, 4.47]`
bugün   `[1.18, 2.63, 4.45, 3.48, 4.52, 4.72, 4.8, 5.2, 3.88, 4.6, 5.07, 4.22]`

→ **İlk 9 sonda (1.–72. turlar) iki eğri birebir aynıdır;**
ayrışma yalnız son 3 sondadadır (80., 88., 96. turlar).

### 4. Farkın nedeni — elenenler ve kalan

**Kanıtla elenen nedenler:**
1. **Faz E yaması değil.** `git archive HEAD` ile çıkarılan yama öncesi kod da bugün
   5,16 / 65,7 / 0,843 veriyor (Ek 5 md 2c'nin dayandığı karşılaştırma).
2. **Kod değişikliği değil.** `git status`, `faz_a_staged.py`, `pilot_state_env.py`,
   `faz_a_config.py` ve sonuç JSON'larının HEAD'e göre **değiştirilmemiş** olduğunu gösteriyor.
   Ayrıca ilk 9 sondanın birebir tutması, tohumların, yapılandırmanın (100 tur, 6 rollout,
   96 adım, lr 0,05) ve ortam kuralının **özdeş** olduğunu doğruluyor; bir kod/yapılandırma
   farkı 0. sondadan itibaren ayrıştırırdı.
3. **Koşudan koşuya rastgelelik değil.** Bugün aynı ortamda dört bağımsız koşu
   (yamalı, HEAD kopyası, gerçek komut, E0 kayıt koşusu) **birbiriyle birebir aynı**
   sonucu verdi; ortam bugün deterministiktir.
4. **BLAS iş parçacığı sayısı değil.** `OMP_NUM_THREADS=1` ve `=2` ile koşulan iki deneme
   birebir aynı eğriyi verdi; ikisi de kayıtlı eğriden aynı sondada (9) ayrıştı.

**Kalan ve en olası neden (kanıt dolaylıdır, bu yüzden "olası" denmektedir):**
Kayıt anındaki çalışma ortamının (NumPy/BLAS yapısı veya makine) bugünkünden farklı olması
ve buradan doğan **son-bit düzeyinde kayan nokta farkının** PPO'nun eğitim yörüngesinde
biriktikten sonra ~72. turdan itibaren bir `argmax`/örnekleme eşiğini karşı tarafa geçirmesi.
Bugünkü ortam: Python 3.11.15, NumPy 1.26.4, OpenBLAS64. Kayıt anındaki ortamın sürüm
bilgisi `faz_a_results.json` içinde **tutulmamıştır** — bu, E0 kayıt disiplininin tam olarak
kapatmak için getirildiği boşluktur (Faz E kayıtları `ortam` alanında Python/NumPy/platform
sürümünü taşır). Bu neden **kanıtlanamamıştır**; yukarıdaki dört madde ise kanıtla elenmiştir.

### 5. Hüküm

**Tarihsel Faz A merkezî PPO kaydı (5,17 / %65,3 / 0,858) bugünkü kodla birebir yeniden
üretilememiştir.** Kayıt silinmez ve değiştirilmez: **Tablo 12b tarihsel kaydı taşımaya
devam eder**, yeniden koşu değeri (5,16 / %65,7 / 0,843; 05.09.2026) **dipnotta** yan yana
verilir. Rastgele kolun birebir yeniden üretilmiş olması, ayrışmanın değerlendirme
protokolünden değil eğitim yörüngesinden geldiğini gösterir.

Bu bulgu, ön kaydın E0 gerekçesini deneysel olarak doğrular: ortam sürümü, git özeti ve
tahmin dosyası kaydedilmeyen bir koşu, aynı depo ve aynı tohumla bile yeniden
üretilemeyebilir. Faz E koşularının tamamı (237 kayıt) bu alanları taşır. *[05.09.2026 · Ek 7 ile düzeltildi: dizinde **238** koşu kaydı vardır — 234 benzersiz kol×tohum anahtarı + 4 geçersiz duman testi; Ek 6'nın yeniden üretim kaydı dâhildir. "237" tarihçe olarak korunmuştur.]*

### 6. Kapsam

Bu Ek E0–E9'un hiçbir kural ya da eşiğini değiştirmez, hiçbir Faz E sonucunu etkilemez ve
Ek 5'in hiçbir satırını silmez; yalnız madde 2c'nin altına tarihli bir daraltma işareti
eklenmiştir.

*05.09.2026 · Ek 5 madde 2c ile birlikte okunur; önceki satırların hiçbiri değiştirilmedi*


---

## Ek 7 — Ek 5 §5 tablo düzeltmesi ve kayıt sayımı (05.09.2026)

**Öncül:** bağımsız doğrulama, dört bulgu · **Yazan:** Claude
**Kapsam uyarısı:** Bu Ek **hiçbir kuralı, eşiği ya da hükmü değiştirmez.** Düzeltilen alan
yalnız Ek 5 §5 tablosunun **Doğruluk** sütunudur; **makro-F1 sütunu doğruydu** ve E1.1, E2.1,
E4.1, E5.1, E6.1, E7.1, E8.1 hükümlerinin hiçbiri makro-F1 dışında bir sütuna dayanmaz —
**bütün hükümler değişmeden geçerlidir.** Ek 5'in hiçbir satırı silinmemiş, tablonun başına
tarihli bir işaret konmuştur.

### 1. Hata beyanı

`faz_e_ek5_yaz.py` içinde tablo başlığı (satır 118) **"Doğruluk"** yazarken gövde (satır 123)
`kritik_duyarlilik_ort` alanını basıyordu. Bu nedenle Ek 5 §5 "Sabit politikalar" tablosunun
**dokuz Doğruluk hücresinin tamamı yanlıştır** (0,0000 / 1,0000 / 0,5000 gibi kritik
duyarlılık değerleri). Betik düzeltilmiştir: Doğruluk artık `dogruluk_ort` alanından basılır,
**Kritik duyarlılık ayrı bir sütun** olarak eklenmiştir ve tabloya **n tohum** sütunu
konmuştur (bulgu 13: `sabit_cogunluk_a3` yalnız bir tohumda — tohum 44 — çoğunluk sınıfı
olmuştur; `sabit_cogunluk_a4` dört tohumda).

### 2. Düzeltilmiş tablo (Ek 5 §5'in yerine geçer)

Kaynak: `faz_e_ozet.json → damarlar.<damar>.<kol>.dogruluk_ort`; aynı 1.800 karar protokolü.

| Sabit politika | Damar | n tohum | Makro-F1 | Doğruluk | Kritik duyarlılık |
|---|---|---:|---:|---:|---:|
| sabit_cogunluk_a0 | CDSA-BB3 | 5 | 0.1736 | 0.5317 | 0.0000 |
| sabit_hep_kritik_a3 | CDSA-BB3 | 5 | 0.0896 | 0.2183 | 1.0000 |
| sabit_cogunluk_a3 | CDSA-MRO | 1 | 0.1218 | 0.4378 | 0.5000 |
| sabit_cogunluk_a4 | CDSA-MRO | 4 | 0.1197 | 0.4272 | 0.5000 |
| sabit_hep_kritik_a3 | CDSA-MRO | 5 | 0.1218 | 0.4378 | 0.5000 |
| sabit_hep_kritik_a4 | CDSA-MRO | 5 | 0.1197 | 0.4272 | 0.5000 |
| sabit_cogunluk_a0 | CDSA-ATM | 5 | 0.1031 | 0.3472 | 0.0000 |
| sabit_hep_kritik_a3 | CDSA-ATM | 5 | 0.0677 | 0.2039 | 0.5000 |
| sabit_hep_kritik_a4 | CDSA-ATM | 5 | 0.0476 | 0.1350 | 0.5000 |

### 3. Diğer üç bulgu

- **`faz_e_ozet.json` çelişkisi giderildi.** `E2.<damar>.kural_E2_1` alanı kaldırıldı; onun
  yerine `_kural_E2_1_notu` konuldu. E2.1 hükmü artık **yalnız**
  `kural_hukumleri.<damar>.E2.1` alanında verilir ve PPO kolları kampanyanın E6 (merkezî,
  FedAvg) ve E5 (FedProx) kayıtlarından okunur; bu alana `_kaynak` ve `_esik` açıklamaları
  eklendi. `faz_e2_karsilastiricilar.json` içindeki "VERILMEDI" ifadesi, o betik koşarken PPO
  kontrol noktalarının **henüz üretilmemiş** olmasının tarihsel kaydıdır ve dokunulmamıştır.
- **Standart sapma sözleşmesi yazıldı.** `faz_e_ozet.json` kök düzeyinde `_ss_sozlesmesi`:
  *makro_f1_ss = örneklem standart sapması (numpy std, ddof=1); tek tohumlu kollarda 0,0
  yazılır ve güven aralığı hesaplanmaz.*
- **Geçersiz kayıtlar işaretlendi.** Dört kısa duman testi kaydının `notlar` alanına
  `{"gecersiz": true, "sebep": "<n> turluk duman testi; tam kosu <dosya adı>"}` eklendi;
  **hiçbir dosya silinmedi veya taşınmadı**. `faz_e_ozet.py` bu kayıtları özete almaz ve
  sayılarını `_gecersiz_kayitlar` alanında raporlar (`sayi: 4`, dosya adlarıyla birlikte).
  Kayıtlar: `CDSA-BB3-E6-fedavg-t42-…204843Z` (tur 20), `CDSA-MRO-E6-fedavg-t42-…204850Z`
  (tur 20), `CDSA-ATM-E6-fedavg-t42-…204859Z` (tur 20),
  `CDSA-ATM-E4-e4_heteroj_fedavg-t42-…212050Z` (tur 5).

### 4. Kayıt sayımı

`results/e_kayit/` dizinlerinde toplam **238** koşu kaydı vardır (tahmin dosyaları hariç):
**234 benzersiz kol × tohum anahtarı + 4 geçersiz duman testi**. Bu sayıya Ek 6'nın
yeniden üretim kaydı (`CDSA-BB3-E0-faz_a_merkezi_yeniden_uretim-t42-…222748Z`) dâhildir.
Ek 5 §6'daki **237** rakamı Ek 6 kaydından önce sayılmıştı; tarihçe olarak korunmuş,
yanına tarihli işaret konmuştur.

### 5. Hükmün durumu

**Ek 5'in hiçbir hükmü değişmemiştir.** Özellikle Kural E2.1 üç damarda da
*"DRL yöntem seçimi bu görevde gerekçelendirilemedi"*, Kural E4.1'in "Non-IID yazılamaz"
hükmü ve E8.1'in ε_toplam kayıtları aynen geçerlidir. Bu Ek yalnız bir raporlama alanı
hatasını ve bir sayımı düzeltir.

*05.09.2026 · Ek 5 ve Ek 6 ile birlikte okunur; önceki satırların hiçbiri silinmedi*


---

## Ek 8 — E3.1 aile bazlı ayrık değerlendirme (06.09.2026)

**Öncül:** Ek 5 §4'te "koşulmadı" diye kayda geçen E3.1 hükmünün, ön kaydın **E3 lafzıyla** ve
**sonuç görülmeden sabitlenmiş** kurguyla koşulması · **Yazan:** Claude ·
**Betik:** `experiments/faz_e3_ayrik_degerlendirme.py` ·
**Sonuç:** `experiments/results/faz_e3_ayrik_degerlendirme.json` · **Özet:** `faz_e_ozet.json → E3`

**Bu Ek hiçbir eşiği, ayrımı, özellik listesini ya da önceki hükmü değiştirmez.** Ek 5'in ve
Ek 7'nin hiçbir satırı silinmemiş; Ek 5 §4 ve §8'deki "koşulmadı" satırlarının altına yalnız
tarihli işaret konmuştur.

### 1. Kurgu (koşudan önce sabit)

- **Ayrım DEĞİŞMEDİ.** `results/faz_e3_ayrim.json` dondurulmuş dosyadan **okunur**; betik
  ayrımı yeniden üretmez. Yeniden üretilebilirlik ayrıca sınanır
  (`ayrim_dondurulmus_ve_yeniden_uretilebilir: true`): 15 aile, test aileleri
  fidye_yazilimi / konfigurasyon_hatasi / usb_zararli_yazilim, **n_test = 218 (%21,8)**,
  **n_eğitim = 782**, aile örtüşmesi yok, kayıt örtüşmesi yok.
- **Özellikler:** yalnız karar anı listesi — olay_turu_id, mitre_tactic,
  etkilenen_hizmet_sayisi, kvkk_ozel_veri, shy145_72saat_uygunluk,
  ek19_kontrol_atfi_sayisi (indeks 0, 1, 2, 5, 6, 7). Çıkarılan dört karar **sonrası** özellik
  (kesinti_suresi_dk, tahmini_maddi_kayip_TL, swiss_cheese_katman_sayisi, aksiyon_sayisi;
  indeks 3, 4, 8, 9) sklearn kollarında **sütun olarak alınmaz**; PPO kollarında gözlem boyutu
  10 kalmak zorunda olduğu için **sıfırlanır** (ön kayıt kodundaki
  `faz_e_veri.e3_ortamlari(karar_ani_maskesi=True)` kuralının aynısı).
- **Ölçü:** makro-F1, `faz_e_kayit.makro_f1` — E2 ile **aynı** tanım (beş sınıf üzerinden).
  Ölçüm birimi kayıtların kendisidir: eğitim kümesinde 782, test kümesinde 218 karar, her kayıt
  bir kez, deterministik karar. Bu, Tablo 12'nin 1.800 karar protokolü **değildir** ve onunla
  aynı satıra yazılmaz.
- **Tohumlar:** E7 protokolü, 42–46. Eğitim kümesi aile ayrımıyla sabit olduğundan
  sklearn/sabit kolları tohumdan bağımsızdır ve bir kez koşulmuştur (n_tohum = 1); PPO kolları
  beş tohumla koşulmuştur.
- **Bütçe:** PPO kollarında 100 tur, 3 istemci, `faz_e_kampanya` ile aynı yerel bütçe
  (172.800 çevre geçişi/tohum). Erken durdurma **yoktur**.
- **Eşik:** Kural E3.1'in 5 puanlık eşiği (`E3_ESIK_PUAN = 5.0`) koddan okunur ve her koşu
  kaydına yazılır. Sonuç görüldükten sonra değiştirilmemiştir.

### 2. Ön işlemenin yalnız eğitimden fit edildiğinin kanıtı

`faz_e3_ayrik_degerlendirme.py` (fonksiyon `_olcekle`, satır 85–87):

```python
    olcek = StandardScaler()
    olcek.fit(Xtr)                      # <-- fit YALNIZ egitim
    return olcek.transform(Xtr), olcek.transform(Xte), olcek
```

- `fit` **yalnız** `Xtr` ile çağrılır; test kümesi yalnızca `transform` edilir.
- Maliyet matrisi K de yalnız eğitim kayıtlarından ölçülür
  (`maliyet_matrisi_egitim`, 782 × 5 = 3.910 gözlem; `maliyet_matrisi_kaynagi` alanı).
- Ortam içindeki bölenler (14.0, 5.0, log 2500, log 500000, 6.0) **kod sabitidir**, veriden
  fit edilmez; bu nedenle test kümesinden bilgi taşımaz.
- Sınama: `tests/test_faz_e3.py` — B1–B7. Özellikle **B4**: test kümesi bozulduğunda eğitim
  dönüşümü ve fit istatistikleri değişmez; **B2**: ölçekleyici ortalaması tam korpus
  ortalamasından farklıdır (yani tüm veriden fit edilmemiştir).
- Test kümesiyle **hiçbir** ayar, eşik seçimi ya da erken durdurma yapılmamıştır;
  hiperparametreler (lojistik `max_iter=2000`, ağaç `max_depth=4, random_state=0`, PPO
  `hidden=64, lr=0.05, 100 tur`) mevcut E2/kampanya kollarından **olduğu gibi** alınmıştır.

### 3. Koşulan ve koşulamayan kollar

| Kol | Durum |
|---|---|
| maliyet-duyarlı lojistik | koşuldu |
| karar ağacı (derinlik ≤ 4) | koşuldu |
| çoğunluk sınıfı sabit politikası (eğitim kümesinde çoğunluk = eylem 4) | koşuldu |
| hep-kritik sabit politikası (eylem 3) | koşuldu |
| hep-kritik sabit politikası (eylem 4) | koşuldu |
| etiket kuralı (üst sınır) | koşuldu |
| PPO merkezî (karar anı gözlemiyle yeniden eğitim, 5 tohum) | koşuldu |
| PPO FedAvg (karar anı gözlemiyle yeniden eğitim, 5 tohum) | koşuldu |
| PPO FedProx / DP / E4 varyantları | **koşulmadı** — ön kayıt E3 bu kolları ayrık kümede istemez; bütçe bu turda merkezî ve FedAvg ile sınırlı tutulmuştur |
| BB3 ve ATM damarları | **uygulanmaz** — E3 yalnız bakım damarında tanımlıdır (aile alanı yalnız MRO korpusunda türetilebilir) |

**Yöntem kararı gerekmedi.** Mevcut PPO ortamı karar anı özellik listesiyle koşabilmektedir:
gözlem vektörü karar sonrası özellikleri **taşımaz**, çünkü ön kayıt tarihli kod
(`faz_e_veri.e3_ortamlari`, 05.09.2026) dört karar sonrası sütunu sıfırlayan maskeyi zaten
içermektedir; gözlem boyutu 10'da kaldığı için ajan ve protokol değişmemiştir. Bu maskeleme
yolu **sütun silme** değildir ve tek farkı budur: sütunlar durur, bilgi içerikleri sıfırdır
(sınama `tests/test_faz_e3.py` C4–C6). Sütunların tümüyle kaldırılması gözlem boyutunu 6'ya
indirir ve ajan mimarisini değiştirirdi; bu, ön kaydın "mevcut ajan/protokol değişmesin"
ilkesine aykırı olacağı için **seçilmemiştir**.

### 4. Sonuç tablosu (Kural E3.1)

Makro-F1; fark = eğitim − test, yüzde puanı. **Ana tabloya yalnız TEST sütunu girer.**

| Kol | n tohum | Eğitim (in-sample) | Test (ayrık) | Fark (pp) | Hüküm |
|---|---:|---:|---:|---:|---|
| Etiket kuralı (üst sınır) | 1 | 0.8000 | 0.6000 | +20.00 | genelleme açığı |
| Karar ağacı (d ≤ 4) | 1 | 0.4795 | 0.1090 | +37.05 | **genelleme açığı** |
| Maliyet-duyarlı lojistik | 1 | 0.3808 | 0.1071 | +27.37 | **genelleme açığı** |
| PPO merkezî | 5 | 0.1418 | 0.1014 | +4.04 | genelleme açığı yazılmaz |
| PPO FedAvg | 5 | 0.1280 | 0.0951 | +3.29 | genelleme açığı yazılmaz |
| Sabit çoğunluk (hep eylem 4 = kurumsal SOME eskalasyonu) | 1 | 0.1280 | 0.0951 | +3.29 | genelleme açığı yazılmaz |
| Sabit hep-kritik (eylem 4) | 1 | 0.1280 | 0.0951 | +3.29 | genelleme açığı yazılmaz |
| Sabit hep-kritik (eylem 3 = kritik uyarı) | 1 | 0.1104 | 0.1472 | −3.68 | genelleme açığı yazılmaz |

*[06.09.2026 · Ek 9 ile düzeltildi: Bu tablodaki sayılar, ölçü ve 5 puanlık eşik **değişmemiştir**.
Yalnız "Hüküm" sütununun okunuşu ayrılmıştır: buradaki hüküm, Kural E3.1'in mekanik sonucu olan
**"eşik tetiklendi"**dir; **"genelleme açığı kanıtlandı"** ayrı bir okumadır ve ortak sınıf
farkına dayanır (Ek 9 §3 tablosu). Özellikle etiket kuralı satırı için eşik tetiklenmiştir, fakat
genelleme açığı **kanıtlı değildir**.]*

Okuma notları (sayı eklenmemiş, yalnız kayıttaki değerler yorumlanmıştır):

- **Etiket kuralı üst sınırının** test makro-F1'i 1,0 değil 0,6'dır; çünkü makro ortalama beş
  sınıf üzerinden alınmakta ve ayrık test kümesinde yalnız üç sınıfın gerçek örneği
  bulunmaktadır (test etiket dağılımı [0, 0, 23, 127, 68]). Bu bir başarım kaybı değil,
  ölçünün tanımının sonucudur ve E2 ile aynı tanım korunduğu için değiştirilmemiştir.
  - *[06.09.2026 · Ek 9: Bu notun sonucu §4 tablosunun hüküm sütununa taşınmamıştı. Ek 9 ile
    taşınmıştır: etiket kuralı için ortak sınıflar {2, 3, 4} üzerinde makro-F1 farkı **0,00
    puandır**; 20 puanlık düşüşün tamamı sınıf desteği etkisidir.]*
- **Öğrendiği söylenen kolların düşüşü, öğrenmeyen kolların düşüşünden büyüktür.** Karar ağacı
  ve lojistik, eğitim ailelerinde makro-F1'i 0,48 ve 0,38'e çıkarmakta, görülmemiş ailelerde
  0,11 dolayına inmektedir: her ikisi için de **genelleme açığı** yazılmıştır. Sabit
  politikaların farkı eşiğin altındadır, çünkü zaten hiçbir şey öğrenmemektedirler.
  - *[06.09.2026 · Ek 9: Bu iki kol için ortak sınıflar üzerinde de kayıp ölçülmüştür —
    karar ağacı **+61,76 puan**, maliyet-duyarlı lojistik **+45,61 puan** — yani bu kollarda
    "genelleme açığı" nitelemesi destek etkisine indirgenemez ve **kanıtlıdır**.]*
- **PPO kolları ayrık kümede de dejeneredir.** `ppo_fedavg` beş tohumun beşinde de 218 test
  kararının tamamını **tek bir eyleme** (eylem 4) vermekte ve karışıklık matrisi
  `sabit_hep_kritik_a4` ile **hücre hücre** aynı çıkmaktadır (0.0951 / 0.0951). `ppo_merkezi`
  beş tohumun üçünde (42, 43, 46) yine tek eylem vermekte, yalnız iki tohumda ikinci bir eylem
  (eylem 3) üretmektedir: tohum 44'te 218 kararın 3'ü, tohum 45'te 41'i. E3.1 eşiğinin bu kollarda aşılmaması bir
  genelleme başarısı değildir: sabit bir politikanın eğitim ile test arasında zaten fark
  vermemesinin sonucudur.
- **E2.1 hükmü ayrık kümede de değişmemiştir.** Aynı +0,05 eşiğiyle, aynı ayrık test kümesinde:
  `ppo_merkezi` 0.1014 ve `ppo_fedavg` 0.0951, maliyet-duyarlı lojistiğin 0.1071'inin
  **altındadır** (fark −0,0057 ve −0,0120) → *"DRL yöntem seçimi bu görevde
  gerekçelendirilemedi"*. Bu okuma Tablo 12'nin 1.800 karar protokolündeki E2.1 hükmünün
  **yerine geçmez**; onu ikinci bir kümede tekrarlar
  (`faz_e_ozet.json → E3.CDSA-MRO.E2_1_ayrik_test_kumesinde`).

### 5. Kayıt disiplini

Her kol × küme × tohum için `faz_e_kayit.KosuKaydi` şemasıyla E0 kaydı yazılmıştır
(`experiments/results/e_kayit/CDSA-MRO-E3-*`): **32 benzersiz kol×küme×tohum anahtarı**;
ayrıca tek tohumlu bir ön koşunun (`--hizli`) 16 kaydı `notlar.gecersiz = true` ile
işaretlenmiştir — **hiçbir dosya silinmemiştir**. `faz_e_ozet.py` E3 kayıtlarını damar
tablosuna **almaz** (farklı protokol) ve ayrı bir `E3` bloğunda raporlar.

*[06.09.2026 · Ek 9: Tanısal analizin E0 kayıtları **ayrı** bir dizine yazılmıştır
(`experiments/results/e_kayit_tanisal/`, kol adları `e3tani_*`); ön kayıtlı E3.1 kayıtlarının
dizinine karıştırılmamıştır. Yukarıdaki 32 + 16 sayısı değişmemiştir.]*

### 6. E9 — insan değerlendirmesi

**E9 insan kodlaması yapılmamıştır.** Kör kodlama paketi hazırdır ve insan kaynağı
beklemektedir; **ajan değerlendirmesi kör insan kodlamasının yerine konulmamıştır** ve bu Ek'te
üretilen hiçbir sayı insan kodlaması olarak sunulmamaktadır. E9.1 hükmü "koşulmadı" olarak
kalır.

### 7. Ek olarak kayda geçen bulgu (bu Ek'te düzeltilmemiştir)

Bakım damarında eylem adları ile ortamın kendi eylem sözlüğü uyuşmamaktadır:
`cdsa_mro_env.ACTIONS` = {0: bekle, 1: dusuk_uyari, 2: yuksek_uyari, 3: kritik_uyari,
4: kurumsal_some_eskale}; buna karşılık raporlamada kullanılan
`faz_a_config.ACTION_LABELS` listesi elle yazılmıştır (BB3 ve ATM'de bu liste ortamdan
türetilir). Kanıt dökümü `/home/claude/kkt/v12_tablo12_mro_adlari.json` dosyasındadır; bu
belge yalnız **adları** düzeltir, hiçbir sayıyı ve hükmü değiştirmez.

*06.09.2026 · Ek 5, Ek 6 ve Ek 7 ile birlikte okunur; önceki satırların hiçbiri silinmedi*


## Ek 9 — E3.1 yorumunun düzeltilmesi ve tanısal analiz (06.09.2026)

**Ne değişmedi.** Ön kayıtlı ölçü (makro-F1, beş sınıf üzerinden; `faz_e_kayit.makro_f1`),
Kural E3.1'in **5 puanlık eşiği** ve Ek 8'de raporlanan **ham sonuçların hiçbiri**
değişmemiştir. `experiments/results/faz_e3_ayrik_degerlendirme.json` dosyasının ham çekirdeği
(`_duzeltme_*` blokları dışındaki bütün alanları) bit düzeyinde korunmuştur; md5
`ae3899e4977815b43026e31e687e30b0` hem düzeltme bloğunda hem tanısal JSON'da kayıtlıdır ve
`tests/test_faz_e3_tanisal.py` A1–A2 ile sınanmaktadır. **Yeni eğitim kampanyası
koşulmamıştır**; tanısal analizin bütün sayıları Ek 8 koşusunda yazılmış E0 kayıtlarının
karışıklık matrislerinden türetilmiştir.

**Ne değişti — yalnız yorum.** Kural E3.1'in lafzı "test sonucu eğitim sonucundan 5 puandan
fazla düşerse bu fark 'genelleme açığı' olarak raporlanır" biçimindedir. Bu lafzın, makro
ortalamanın **sınıf desteğine duyarlılığına** açık olduğu sonuç görüldükten sonra fark
edilmiştir: ön kayıtlı ölçü makro-F1'i beş sınıf üzerinden ortalar ve desteği olmayan sınıf
ortalamaya F1 = 0 olarak girer. Eğitim kümesinde dört sınıfın (destek [0, 1, 115, 298, 368]),
ayrık test kümesinde üç sınıfın (destek [0, 0, 23, 127, 68]) gerçek örneği vardır. Bu nedenle
**hatasız** bir karar kuralı bile eğitimde 4/5 = 0,80, testte 3/5 = 0,60 alır. **Kural
değiştirilmemiştir**; yalnız iki ifade birbirinden ayrılmıştır:

- **"Eşik tetiklendi"** — Kural E3.1'in mekanik sonucu: eğitim makro-F1 − test makro-F1 > 5
  puan. Ek 8 §4 tablosundaki hüküm sütunu budur ve olduğu gibi durmaktadır.
- **"Genelleme açığı kanıtlandı"** — ayrı bir okuma: ancak eğitim ile testte **ortak** olan
  sınıflarda ({2, 3, 4}) da kayıp ölçüldüğünde yazılır.

### 1. Tanısal analiz (ön kayıtlı sonucun yerine geçmez)

Betik `experiments/faz_e3_tanisal.py`, çıktı `experiments/results/faz_e3_tanisal.json`,
E0 kayıtları `experiments/results/e_kayit_tanisal/`. Betik yeni model eğitmez, yeni tohum
koşmaz, yeni veri üretmez; Ek 8'in 32 geçerli E0 kaydındaki karışıklık matrislerini okur
(`notlar.gecersiz = true` işaretli 16 ön koşu kaydı atlanır) ve her kol × {eğitim, test} için
sınıf bazlı kesinlik/duyarlılık/F1 ile destek sayılarını, ardından üç makro okumayı hesaplar:
(a) ön kayıtlı beş sınıflı makro-F1 (**dokunulmaz**; yalnız doğrulama için yeniden üretilir ve
ham JSON ile birebir tutmaktadır), (b) yalnız desteği olan sınıflar üzerinden makro-F1,
(c) ortak sınıflar üzerinde her iki kümede yeniden hesaplanan makro-F1. Kesinlik ve duyarlılık
her zaman tam 5×5 matristen alınır; (b) ve (c) yalnız **ortalamanın alındığı sınıf kümesini**
daraltır.

Ayrıştırma: **ön kayıtlı fark = ortak sınıf farkı + sınıf dağılımı payı.**

### 2. Ölçünün sınıf desteğine duyarlılığı — etiket kuralı

Etiket kuralı üst sınırı eğitimde ve testte **%100 doğrudur** (doğruluk 1,0 / 1,0; test
karışıklık matrisi köşegendir). Ortak sınıflar {2, 3, 4} üzerinde makro-F1 eğitimde de testte
de **1,00**'dir; **ortak sınıf farkı 0,00 puandır**. Ön kayıtlı 20 puanlık düşüşün tamamı
(%100'ü), testte bulunmayan sınıfların beş sınıflı ortalamaya sıfır olarak girmesinden
doğmaktadır. Bu bir genelleme başarısızlığı değil, **ölçünün sınıf desteğine duyarlılığıdır**.

### 3. Kol × hüküm tablosu (Ek 8 §4'ün okunuşu)

Makro-F1, yüzde puanı; fark = eğitim − test. Ön kayıtlı fark sütunu Ek 8 §4 ile **aynıdır**.

| Kol | Ön kayıtlı fark (pp) | Ortak sınıf farkı (pp) | Sınıf dağılımı payı (pp) | Kural E3.1 | Genelleme açığı |
|---|---:|---:|---:|---|---|
| Etiket kuralı (üst sınır) | +20,00 | **0,00** | +20,00 (%100) | eşik tetiklendi | **kanıtlı değil** — destek etkisi |
| Karar ağacı (d ≤ 4) | +37,05 | **+61,76** | −24,71 | eşik tetiklendi | **kanıtlı** — ortak sınıflarda da kayıp |
| Maliyet-duyarlı lojistik | +27,37 | **+45,61** | −18,24 | eşik tetiklendi | **kanıtlı** — ortak sınıflarda da kayıp |
| PPO merkezî | +4,04 | +6,74 | −2,70 | eşik altında | ortak sınıflarda kayıp var, eşik aşılmadı |
| PPO FedAvg | +3,29 | +5,48 | −2,19 | eşik altında | ortak sınıflarda kayıp var, eşik aşılmadı |
| Sabit çoğunluk (eylem 4) | +3,29 | +5,48 | −2,19 | eşik altında | uygulanmaz — sabit politika öğrenmez |
| Sabit hep-kritik (eylem 4) | +3,29 | +5,48 | −2,19 | eşik altında | uygulanmaz — sabit politika öğrenmez |
| Sabit hep-kritik (eylem 3) | −3,68 | −6,14 | +2,46 | eşik altında | uygulanmaz — sabit politika öğrenmez |

Okuma: **Toplam düşüşün tamamı, sınıf dağılımı etkisi ayrılmadan genelleme kaybı ilan
edilemez.** Etiket kuralında düşüşün tamamı destek etkisidir. Öğrenen karşılaştırıcılarda
durum tersidir: ortak sınıflarda ölçülen kayıp, ön kayıtlı farktan **daha büyüktür** (karar
ağacı 0,7992 → 0,1816; lojistik 0,6346 → 0,1785), çünkü beş sınıflı ortalama her iki kümede
de aynı sıfırlarla seyreltilmektedir. Sabit politikalarda "eşiğin aşılmaması" bir genelleme
başarısı değildir; öğrenme olmadığı için eğitim ile test arasında zaten fark oluşmamaktadır.

*[06.09.2026 · Bağımsız doğrulamayla düzeltildi (DOGRULAMA_v51_v13.md B1): yukarıdaki
tablonun **PPO FedAvg** satırı için "genelleme açığı" sütununda yazılı "ortak sınıflarda
kayıp var, eşik aşılmadı" okuması, `faz_e3_tanisal.json`'daki `ppo_fedavg` kolunun eğitim VE
test `sinif_f1` dizilerinin (dolayısıyla +3,29 / +5,48 / −2,19 üçlüsünün) `sabit_cogunluk_a4`
ve `sabit_hep_kritik_a4` kollarıyla **birebir aynı** olmasıyla çelişmektedir; bu kol ayrık
kümede beş tohumun beşinde de tek eyleme çökmekte ve karışıklık matrisi sabit politikayla
hücre hücre örtüşmektedir (bkz. "4. Korunan bulgular" maddesi, aşağıda — bu madde zaten
doğru okunmuştu). Düzeltilmiş okuma: **PPO FedAvg → "uygulanmaz — bu kol ayrık kümede sabit
politikayla özdeştir, fark öğrenmeden değil sınıf bileşiminden doğar"**, tıpkı sabit politika
satırları gibi. **PPO merkezî** satırı için okuma **değişmez**: `ppo_merkezi`'nin F1 dizileri
(test: sınıf 3'te 0,0483, sınıf 4'te 0,4586 — sıfır değil) sabit politikadan **farklıdır**;
+6,74 puanlık ortak sınıf farkı gerçek bir kayıptır ve "kanıtlı — ortak sınıflarda da kayıp"
okuması geçerliliğini korur. Yukarıdaki tablonun satırları **silinmemiştir**; bu not
düzeltmenin gerekçesini ve kapsamını kayda geçirir. Kaynak dosya
(`faz_e3_ayrik_degerlendirme.json`, `faz_e3_tanisal.json`) ve ham sayılar değiştirilmemiştir;
yalnız yorum ayrılmıştır. Aynı düzeltme `faz_e_ozet.py`/`faz_e_ozet.json` E3 bloğuna
(`_duzeltme_06092026._ek_not_06092026_bagimsiz_dogrulama`) ve tez v13 Tablo 17 (T18 R05) ile
makale v48 Bölüm 6.3'e işlenmiştir.]*

### 4. Korunan bulgular

- **Sabit politika davranışı korunur.** `ppo_fedavg` beş tohumun beşinde de 218 test kararının
  tamamını tek bir eyleme vermekte ve karışıklık matrisi `sabit_hep_kritik_a4` ile hücre hücre
  aynı çıkmaktadır; `ppo_merkezi` beş tohumun üçünde tek eylem üretmektedir (Ek 8 §4).
- **E2.1 hükmü korunur.** Aynı +0,05 eşiğiyle, aynı ayrık test kümesinde `ppo_merkezi` 0,1014
  ve `ppo_fedavg` 0,0951, maliyet-duyarlı lojistiğin 0,1071'inin altındadır → *"DRL yöntem
  seçimi bu görevde gerekçelendirilemedi"*. Ayrık kümedeki tanısal okuma da bunu
  değiştirmez: PPO kolları ortak sınıflarda da lojistiğin altındadır.
- **E9 insan kodlaması** yine "koşulmadı" olarak kalır.

### 5. Gelecekteki E3 benzeri kurallar için not (yeni eşik yazılmamaktadır)

Bu Ek yeni bir eşik, yeni bir ölçü ve yeni bir hüküm **yazmaz**. Yalnız gelecekte yazılacak
kurallar için şu kayıt düşülür: eğitim ve test kümelerinin sınıf desteği farklıysa, "puan
düşüşü" biçiminde yazılan bir eşik ölçünün destek duyarlılığını da ölçer. Böyle bir kural
ileride yazılırsa (a) karşılaştırmanın hangi sınıf kümesi üzerinde yapılacağı ve (b) destek
farkının nasıl raporlanacağı **koşudan önce** kararlaştırılmalıdır. Mevcut Kural E3.1
değiştirilmemiştir ve bu turda geçerlidir.

### 6. Sınama

`tests/test_faz_e3.py` **28/28 geçmektedir** (değiştirilmemiştir). Yeni
`tests/test_faz_e3_tanisal.py` **32/32 geçmektedir**: ham çekirdeğin md5'i, ortak sınıf
hesabı, etiket kuralında ortak sınıf farkının 0 olması, ayrıştırmanın toplanması ve tanısal
kayıtların ayrı dizinde tutulması sınanmaktadır.

*06.09.2026 · Ek 8 ile birlikte okunur; Ek 8'in hiçbir satırı silinmemiş, ilgili satırların
altına tarihli işaret düşülmüştür.*

---

## Ek 10 — Programın kapatılması (07.10.2026)

**Karar veren.** Mete, 07.10.2026 ("Artık Karakutu projesini içerik açısından tamamlanmış olarak kabul etmek istiyorum"). **Yazan.** Claude.

Program bu tarihte tezin kapsamında kapatılmıştır. Bu Ek yeni bir koşu, eşik, ölçü ya da hüküm yazmaz ve önceki Eklerin hiçbir satırını değiştirmez. Kapanış koşulmayan kalemleri koşulmuş gibi göstermez, yalnız durumlarını sabitler.

### 1. Koşulanlar

E0 kayıt disiplini bütün koşularda uygulanmıştır. E1'in biyometri ve hava trafiği kolları, E2'nin (a) kolu ve zorunlu karşılaştırıcıları, E4, E5, E6 ve E8'in (a) kolu 05.09.2026'da E7'nin beş tohumlu protokolü altında koşulmuştur (Ek 5 ve Ek 7). E3.1 06.09.2026'da koşulmuştur (Ek 8 ve Ek 9). Programa sonradan eklenen E10 ve E11 kendi ön kayıtlarıyla koşulmuştur (`_COWORK/faz_e/FAZ_E10_E11_ON_KAYIT_09092026.md`). Sonuçlar ve kural hükümleri bu kayıtlardadır ve tezin 9.2, 9.3, 9.7 ve 10.8 bölümlerinde raporlanmaktadır (tez v32).

### 2. Koşulmadan kapatılanlar

| Kalem | Durum | Kuralın hükmü |
|---|---|---|
| E1, bakım kolu | Koşulamadı. `MODALITY_GROUPS` boştur ve çok-modlu başlık bu damarda uygulanmamıştır (Ek 5 §8). Bakım görevi tek-modludur. | Kural E1.1 bu damarda uygulanmadı. Kural E1.2 gereği "yakınsak" yazılamaz. |
| E7, açılmamış kollar | Beş tohumlu protokole alınmayan kollar koşulmamıştır. Ayrık kümede PPO'nun FedProx, DP ve E4 varyantlarını ön kayıt E3 istemiyordu (Ek 8 §3). | Kural E7.1 bu kollara uygulanmadı. |
| E2 (b), dinamik kol | Ön kayıt (a)'yı seçmiş ve (b)'yi ayrı bir ön kayda bırakmıştı (E2 kurgusu ve Ek 1). O ön kayıt yazılmamıştır. | Bu programın yükümlülüğü değildi. |
| E9, kör insan kodlaması ve seçilme olasılığı ağırlıklı duyarlılık analizi | İnsan kodlayıcı ve veri erişimi gerektirir, yapılmamıştır. Ajan değerlendirmesi yerine konulmamıştır. 09.09.2026 tarihli kısa tasarımın (`_COWORK/FAZ_E9_KOR_KODLAMA/E9_KISA_ON_KAYIT_09092026.md`) kodlaması da yapılmamış ve anahtarı açılmamıştır. | Kural E9.1 "koşulmadı" olarak kalır. Tezdeki 13,2 değeri ağırlıklı değerle sınanmamıştır. |

### 3. Kapanışın anlamı

Koşulmayan kalemler için hiçbir sonuç yazılmamış ve hiçbir karar kuralı uygulanmamıştır. Bu kalemlere bağlı savlar tezde kurulmamış olarak kalır. Korpus bulgusu otomatik kodlamaya dayanır ve insan geçerliliği ölçülmemiştir, tez bunu sınırlılık olarak taşır (tez Bölüm 5.5). Kalemlerden biri ileride koşulursa ayrı bir çalışma olarak, bu ön kayda ve bu Eke gönderme yapılarak raporlanır.

*07.10.2026 · Ek 1–9 ile birlikte okunur, önceki satırların hiçbiri değiştirilmedi.*


---

## Ek 11 — Ayrı planla sınırlı E7 gözlem bozulması değerlendirmesi (08.10.2026)

Mete E1/E2/E7/E9 içinden yapılabilir işleri yürütme ve bütün belgeleri yeni sürümlerle üretme talimatı verdi. Bu talimatla yalnız mevcut beş tohumlu kontrol noktalarının gözlem gürültüsü ve girdi kaybı değerlendirmesi açıldı. Bu Ek sonuçların ve kapsamın sonradan tarihli indeksidir ve koşu öncesi planın yerine geçmez. Önceki Ek 1–10 metni ve karar kuralları değiştirilmedi.

Ayrı plan `_COWORK/faz_e/E7_GOZLEM_KAYBI_20261008_ONKAYIT.json` içinde 07.10.2026 saat 22.36.04,502319 UTC'de, yerel 08.10.2026 saat 01.36.04,502319'da yazıldı. İlk değerlendirme 22.36.21,437648 UTC'de başladı. Plan, değerlendirme kodunun ve 701 tarihsel kaynağın SHA-256 değerlerini koşudan önce kaydetti. Kaynak yordamın gürültü ve kayıp kuralları değişmedi. Bakım modalite grupları boş olduğundan burada modalite kaybı üretilmedi.

Üç damar, üç politika ve beş eğitim tohumu kullanıldı. Her koşulda aynı 1.800 karar korunarak 360 değerlendirme ve 648.000 karar sunumu üretildi. Yeniden eğitim yapılmadı. Eşlenik fark aralıkları beş eğitim tohumu üzerinde 20.000 bootstrap yeniden örneklemesiyle hesaplandı. Aralıklar noktasal ve keşifseldir ve Kural E7.1 gereği sıfırı içeren fark ölçülemedi olarak yazıldı. E1 bakım, E2 dinamik görev, E9 insan kodlaması ve ağırlıklı korpus risk oranı bu ölçümde koşulmadı. Bu çalışma tarihsel bütün E7 kollarının tamamlanması değildir.

Yeni ölçüm tez v33 Bölüm 10.8, A v62 Bölüm 5.8 ve Ek H içinde raporlanmıştır. B v16 ve C v55/v65 bu ölçümü kendi kanıtları olarak aktarmaz. İnsan geçerliliği ölçülmemiştir ve uygulanmayan araştırmalar içerik kapanışını engelleyen işler değildir. Kod, plan, üç sonuç ve üç sıkıştırılmış tahmin kaydı yerel teslimde korunur. Yeni dosyalar yayımlanmış GitHub veya Zenodo sürümüne yüklenmedi.
