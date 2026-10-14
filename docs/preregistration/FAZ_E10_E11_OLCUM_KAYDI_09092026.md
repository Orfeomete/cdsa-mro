# Faz E10 / E11 — ölçüm kaydı

**09.09.2026.** Ön kayıt `FAZ_E10_E11_ON_KAYIT_09092026.md`, **koşudan önce**
donduruldu. 150 eğitim koşusu (10 tohum × 15 kol), her biri aynı 1.800 karar
protokolünde değerlendirildi. Betikler: `e10_e11_kosu.py`, `e10_e11_analiz.py`.
Ham çıktı: `cikti/*.json` (150 dosya).

Ortam kodu, ajan kodu, federe agregasyon kodu ve `makro_f1()` tanımı
değiştirilmemiştir. **Tezin mevcut dondurulmuş sayılarının hiçbiri
değişmemiştir**; aşağıdakiler yanlarına eklenen yeni koldur.

---

## 1. Sonuç tablosu — on tohum, makro-F1

| Damar | Kol | Tohum başına (42→51) | Ort | SD | %95 GA | Dejenere |
|---|---|---|---:|---:|---|---:|
| MRO | fedavg | 0.120 0.121 0.194 0.122 0.240 0.120 0.120 0.120 0.120 0.120 | 0.1395 | 0.0423 | [0.1093, 0.1698] | **7/10** |
| MRO | fedprox | 0.120 0.147 0.196 0.120 0.241 0.120 0.120 0.120 0.120 0.120 | 0.1421 | 0.0424 | [0.1118, 0.1724] | **7/10** |
| MRO | central | 0.120 0.120 0.120 0.120 0.120 0.120 0.239 0.120 0.206 0.224 | 0.1508 | 0.0507 | [0.1146, 0.1870] | **7/10** |
| BB3 | fedavg | 0.336 0.347 0.355 0.352 0.367 0.344 0.356 0.360 0.350 0.351 | 0.3517 | 0.0086 | [0.3456, 0.3579] | 0/10 |
| BB3 | fedprox | 0.331 0.349 0.356 0.361 0.367 0.344 0.356 0.358 0.348 0.344 | 0.3516 | 0.0103 | [0.3442, 0.3589] | 0/10 |
| BB3 | central | 0.349 0.333 0.356 0.350 0.343 0.338 0.339 0.354 0.353 0.352 | 0.3467 | 0.0079 | [0.3410, 0.3523] | 0/10 |
| BB3 | tek-modlu ppg | 0.333 0.328 0.338 0.339 0.338 0.334 0.336 0.339 0.344 0.332 | 0.3361 | 0.0045 | [0.3329, 0.3393] | 0/10 |
| BB3 | tek-modlu ecg | 0.195 0.205 0.213 0.217 0.249 0.257 0.204 0.174 0.221 0.239 | 0.2174 | 0.0256 | [0.1991, 0.2357] | 1/10 |
| BB3 | tek-modlu eeg | 0.257 0.257 0.258 0.259 0.263 0.260 0.174 0.264 0.174 0.266 | 0.2431 | 0.0367 | [0.2168, 0.2694] | 2/10 |
| ATM | fedavg | 0.255 0.068 0.263 0.263 0.068 0.243 0.068 0.068 0.257 0.068 | 0.1621 | 0.0996 | [0.0908, 0.2333] | **5/10** |
| ATM | fedprox | 0.254 0.068 0.267 0.264 0.048 0.242 0.068 0.068 0.257 0.068 | 0.1602 | 0.1021 | [0.0872, 0.2333] | **5/10** |
| ATM | central | 0.262 0.227 0.260 0.249 0.260 0.260 0.251 0.068 0.240 0.260 | 0.2337 | 0.0594 | [0.1912, 0.2761] | 1/10 |
| ATM | tek-modlu trajectory | 0.048 0.068 0.048 0.048 0.048 0.048 0.048 0.048 0.068 0.068 | 0.0536 | 0.0097 | [0.0467, 0.0606] | **10/10** |
| ATM | tek-modlu ats | 0.455 0.068 0.068 0.264 0.258 0.247 0.068 0.263 0.263 0.068 | 0.2020 | 0.1302 | [0.1089, 0.2952] | 4/10 |
| ATM | tek-modlu coord | 0.068 0.068 0.068 0.068 0.048 0.068 0.068 0.048 0.048 0.048 | 0.0597 | 0.0104 | [0.0522, 0.0671] | **10/10** |

"Dejenere": 1.800 kararın tamamının tek bir eyleme verildiği koşu sayısı.

---

## 2. Ön kayıtlı karar kurallarının uygulanması

### E10.1 — tek tohumun temsil gücü: **dokuz kolun dördünde karşılanmadı**

| Damar | Kol | Tohum 42 | On tohumluk %95 GA | Konum |
|---|---|---:|---|---|
| BB3 | fedavg | 0.3357 | [0.3456, 0.3579] | **altında** |
| BB3 | fedprox | 0.3313 | [0.3442, 0.3589] | **altında** |
| ATM | fedavg | 0.2547 | [0.0908, 0.2333] | **üstünde** |
| ATM | fedprox | 0.2537 | [0.0872, 0.2333] | **üstünde** |

Ön kayıt gereği yazılması gereken hüküm: *tezin ana protokolde raporladığı tek
tohumlu değer, koşu-arası dağılımın tipik bir üyesi değildir.* **Hava trafiği
damarında tohum 42, dağılımın üst ucunun da dışındadır**; yani ana protokolün
o damardaki sayısı tipik bir koşudan daha iyidir. Mevcut sayı
değiştirilmemiştir; bu tespit yanına konmaktadır.

### E10.3 — değişkenliğin büyüklüğü: **üç damarda da tetiklendi**

| Damar | Kollar arası en büyük fark | En büyük tohum SD |
|---|---:|---:|
| MRO | 0.0113 | 0.0507 |
| BB3 | 0.0051 | 0.0103 |
| ATM | 0.0735 | 0.1021 |

Üç damarda da tohum-arası standart sapma, kollar arası farktan büyüktür.
Ön kayıt gereği: **fedavg, fedprox ve merkezî kol arasındaki farklar tek
tohumla kurulamaz.** Bu, tezin bu kolları karşılaştıran her cümlesini
etkilemektedir.

### E10.2 — sabit politika karşılaştırıcısı: **iki damarda karşılanmadı**

Karşılaştırıcı kümesinin tamamı (mevcut `faz_e0_esdeger.json` kaydından,
aynı 1.800 karar):

| Damar | sabit çoğunluk | hep-kritik | rastgele | En iyi | fedprox %95 GA | Hüküm |
|---|---:|---:|---:|---:|---|---|
| MRO | 0.1218 | 0.1218 / 0.1197 | **0.1401** | 0.1401 | [0.1118, 0.1724] | **GA rastgeleyi içeriyor** |
| BB3 | 0.1736 | 0.0896 | 0.2194 | 0.2194 | [0.3442, 0.3589] | öğrenilmiş üstünde |
| ATM | 0.1031 | 0.0677 / 0.0476 | **0.1863** | 0.1863 | [0.0872, 0.2333] | **GA rastgeleyi içeriyor** |

Ön kayıt gereği yazılacak hüküm: **bakım ve hava trafiği damarlarında,
öğrenilmiş politikanın rastgele politikayı makro-F1 bakımından geçtiği iddia
edilemez.** Yalnız pilot biyometrisi damarında öğrenilmiş politika bütün
karşılaştırıcıların üzerindedir.

Bu, tezin bakım damarı için zaten kaydettiği olumsuz bulgunun hava trafiği
damarına da yayıldığı anlamına gelmektedir ve öyle yazılacaktır.

### E11a.1 — Tablo 10 (merkezî ↔ birleşik): **üç damarda da fark ölçülemedi**

| Damar | Merkezî (100 tur) | Birleşik (160 tur) | Sonuç |
|---|---|---|---|
| MRO | 0.1508 [0.1146, 0.1870] | 0.1421 [0.1118, 0.1724] | GA örtüşüyor |
| BB3 | 0.3467 [0.3410, 0.3523] | 0.3516 [0.3442, 0.3589] | GA örtüşüyor |
| ATM | 0.2337 [0.1912, 0.2761] | 0.1602 [0.0872, 0.2333] | GA örtüşüyor |

Ön kayıt gereği: *bu kurguda ve bu bütçede fark ölçülememiştir.* Üstünlük ya
da veri yerelliğinin bedeli **hiçbir yönde iddia edilmemektedir.** Bütçe
eşitsizliği (merkezî 100 tur, federe 160 tur) kayıtta durmaktadır ve bu
eşitsizliğe rağmen fark çıkmamıştır.

Hava trafiği damarında merkezî kolun ortalaması birleşik kolun ortalamasının
belirgin biçimde üzerindedir (0.2337'ye karşı 0.1602) fakat tohum değişkenliği
bu farkı istatistiksel olarak ayırt edilemez kılmaktadır. **Fark yönü kayda
geçirilmekte, ancak hüküm kurulmamaktadır.**

### E11b.1 — Tablo 9 (çok-modlu ↔ tek-modlu): **bir damarda gösterildi, birinde gösterilemedi**

**BB3 — kazanç gösterildi.**
Çok-modlu 0.3516 [0.3442, 0.3589]; en iyi tek-modlu `ppg` 0.3361
[0.3329, 0.3393]. Güven aralıkları **örtüşmemektedir**; fark **+0.0155**.
Modalite sıralaması: ppg (0.3361) > eeg (0.2431) > ecg (0.2174).

**ATM — kazanç GÖSTERİLEMEDİ.**
Çok-modlu 0.1602 [0.0872, 0.2333]; en iyi tek-modlu `ats` 0.2020
[0.1089, 0.2952]. Güven aralıkları örtüşmektedir **ve en iyi tek-modlu kolun
ortalaması çok-modlu kolun ortalamasının üzerindedir.** Ön kayıt gereği:
*çok-modlu füzyonun kazancı bu damarda gösterilememiştir.* Ortalamaların
yönü çok-modlu füzyonun aleyhinedir; ancak değişkenlik yüksek olduğundan
"füzyon zarar veriyor" hükmü de kurulmamaktadır.
Diğer iki ATM modalitesi (`trajectory` 0.0536, `coord` 0.0597) **on tohumun
onunda da dejenere** olmuştur; tek başlarına öğrenilebilir sinyal
taşımamaktadırlar.

**MRO — tanımsız.** Görev tek-modludur (`MODALITY_GROUPS = {}`,
`faz_a_config.py`; dosyanın kendi notu çok-modlu kurgunun Faz B'de olduğunu
söylemektedir). Tablo 9'da bu satıra **"tanımsız — görev tek-modlu"**
yazılacaktır. Kol imal edilmemiştir.

---

## 3. Ön kayıt §7 — yeniden üretilebilirlik denetimi

Depodaki kontrol noktaları parçalı (chunk'lı) koşuyla üretilmiştir; parçalı
koşuda istemci ajanlarının rastgele sayı üreteci durumu kontrol noktasına
yazılmamaktadır. E10 parçasız koşmuştur. Ön kayıt bu farkın raporlanmasını
şart koşmuştu:

| Damar | Kol | Depodaki kayıt | E10 tohum 42 | Fark |
|---|---|---:|---:|---:|
| MRO | fedavg | 0.1197 | 0.1197 | 0.0000 |
| MRO | fedprox | 0.1197 | 0.1197 | 0.0000 |
| BB3 | fedavg | 0.3490 | 0.3357 | **−0.0133** |
| BB3 | fedprox | 0.3492 | 0.3313 | **−0.0179** |
| ATM | fedavg | 0.2516 | 0.2547 | **+0.0031** |
| ATM | fedprox | 0.2516 | 0.2537 | **+0.0021** |

**Hüküm:** ana protokolün sayıları koşunun parçalanma biçimine duyarlıdır.
Bakım damarında fark yoktur (politika dejenere olduğu için parçalanma etkisi
görünmez). Pilot biyometrisi damarında depodaki değer, parçasız koşunun aynı
tohumdaki değerinden 0.018'e varan biçimde yüksektir. Bu, tezin yeniden
üretilebilirliği aleyhine bir tespittir ve ön kayıt gereği yazılmaktadır.

Not: depodaki BB3 değeri (0.3492) on tohumluk güven aralığının **içindedir**;
parçasız tohum 42 değeri (0.3313) aralığın **altındadır**. Yani depodaki sayı
tipik aralıktadır, tek tohumun kendisi değildir.

---

## 4. Dejenere politika yaygınlığı — yeni ve olumsuz bulgu

Tezin bakım damarı için kaydettiği dejenere politika (1.800 kararın tamamı tek
eyleme) **tek tohuma özgü bir kaza değildir**:

- MRO: on tohumun **yedisinde** dejenere.
- ATM: on tohumun **beşinde** dejenere (federe kollarda); merkezî kolda 1/10.
- BB3: hiçbir tohumda dejenere değil.
- ATM tek-modlu `trajectory` ve `coord`: **10/10 dejenere**.

Bölüm 10.8'in geçiş fonksiyonu analizi bu davranışı zaten açıklamaktadır
(eylemden bağımsız geçiş altında haydut probleminde yerel optimum). E10 o
açıklamanın **yaygınlığını** ölçmektedir: davranış kural, istisna değildir.

---

## 5. Hüküm — özet

1. **Tohum değişkenliği kollar arası farklardan büyüktür** (üç damarda da).
   fedavg/fedprox/merkezî karşılaştırmaları tek tohumla kurulamaz.
2. **Tohum 42 dokuz kolun dördünde atipiktir**; hava trafiği damarında
   dağılımın üst ucunun dışındadır.
3. **Tablo 10: fark hiçbir damarda ölçülememiştir.** Ne birleşik yapının
   üstünlüğü ne veri yerelliğinin bedeli gösterilmiştir.
4. **Tablo 9: kazanç yalnız pilot biyometrisi damarında gösterilmiştir**
   (+0.0155, GA'lar ayrık). Hava trafiği damarında gösterilememiştir; bakım
   damarında tanımsızdır.
5. **Bakım ve hava trafiği damarlarında öğrenilmiş politikanın rastgele
   politikayı geçtiği iddia edilemez** (GA rastgeleyi içermektedir).
6. **Dejenere politika yaygındır** (MRO 7/10, ATM 5/10).
7. **Depodaki sayılar koşunun parçalanmasına duyarlıdır** (BB3'te 0.018'e
   varan fark).

Beş, altı ve yedinci maddeler tezin aleyhinedir. Ön kayıt §8 bunların
yumuşatılmadan yazılmasını şart koşmuştu; yazılacaktır.

*09.09.2026 · Claude · ön kayıt koşudan önce donduruldu; hiçbir tohum
atılmamış, tohum listesi uzatılmamış, karar kuralı değiştirilmemiştir.*

---

## 7. Türetilmiş değerler — tezde basılan fark sütunları

Aşağıdakiler yeni ölçüm değildir; §1'deki ortalamaların farkıdır. Tezin
Tablo 9 ve Tablo 10'unda "fark" sütunu olarak basıldıkları için burada
provenans zincirini tamamlamak üzere ayrıca yazılmışlardır.

**Tablo 9 fark sütunu** (çok-modlu ortalaması − tek-modlu ortalaması):

| Damar ve grup | Hesap | Fark |
|---|---|---:|
| Biyometri, PPG | 0.3516 − 0.3361 | **+0.0155** |
| Biyometri, EEG | 0.3516 − 0.2431 | **+0.1085** |
| Biyometri, EKG | 0.3516 − 0.2174 | **+0.1342** |
| Hava trafiği, ATS | 0.1602 − 0.2020 | **−0.0418** |
| Hava trafiği, koordinasyon | 0.1602 − 0.0597 | **+0.1005** |
| Hava trafiği, yörünge | 0.1602 − 0.0536 | **+0.1066** |

**Tablo 10 fark sütunu** (birleşik ortalaması − merkezî ortalaması):

| Damar | Hesap | Fark |
|---|---|---:|
| Biyometri | 0.3516 − 0.3467 | **+0.0049** |
| Bakım | 0.1421 − 0.1508 | **−0.0087** |
| Hava trafiği | 0.1602 − 0.2337 | **−0.0735** |

Fark sütunları yalnız betimleyicidir; hüküm güven aralıklarının örtüşmesine
göre kurulmuştur (§2, E11a.1 ve E11b.1). Örtüşen aralıklarda fark sütunundaki
işaret bir üstünlük ya da bedel iddiası değildir.

---

## 8. DÜZELTME (10.09.2026) — makro-F1 tanımı

**Bulgu.** §1'in tablosu, `faz_e_kayit.makro_f1()` işlevini olduğu gibi
kullanmaktadır; o işlev makro-F1'i **bütün sınıflar** üzerinden ortalamaktadır.
Tezin Tablo 12 ve Tablo 13'ü ise **gerçek desteği bulunan sınıflar** üzerinden
ortalamaktadır. İki tanım, bir sınıfın gerçek desteği sıfır olduğunda ayrışır.

**Etkilenen tek damar bakım damarıdır.** Orada birinci eylemin (izleme devam)
gerçek desteği sıfırdır; tüm-sınıf değeri destekli-sınıf değerinin tam olarak
4/5'idir. Biyometri (4/4 sınıf destekli) ve hava trafiği (5/5) damarlarında iki
tanım **aynı** değeri vermektedir ve o damarlarda hiçbir sayı değişmemiştir.

**Düzeltilmiş bakım değerleri (tezin tanımı, on tohum):**

| Kol | Tohum 42 | Ort | SD | %95 GA | Dejenere |
|---|---:|---:|---:|---|---:|
| FedAvg | 0,1497 | 0,1744 | 0,0529 | [0,1366, 0,2122] | 7/10 |
| FedProx | 0,1497 | 0,1777 | 0,0529 | [0,1398, 0,2156] | 7/10 |
| Merkezî | 0,1497 | 0,1885 | 0,0633 | [0,1432, 0,2338] | 7/10 |

Karşılaştırıcılar (aynı tanım): rastgele 0,1751 · sabit çoğunluk 0,1522 ·
hep-kritik (eylem 4) 0,1497.

**Hiçbir hüküm değişmemiştir.**

- **E10.2** — fedprox GA'sı [0,1398, 0,2156] rastgele politikanın 0,1751
  değerini hâlâ **içermektedir**; bakım damarında öğrenilmiş politikanın
  rastgeleyi geçtiği iddia edilemez.
- **E10.3** — kollar arası en büyük fark 0,0141, en büyük SD 0,0633; SD hâlâ
  farktan büyüktür.
- **E11a.1** — merkezî 0,1885 [0,1432, 0,2338] ile birleşik 0,1777
  [0,1398, 0,2156] güven aralıkları hâlâ **örtüşmektedir**; fark ölçülememiştir.
- **E10.1** — tohum 42 (0,1497) GA'nın içindedir; bakım damarı bu kuralı zaten
  tetiklememişti.

İki tanım da bir ölçekleme çarpanıyla ilişkili olduğundan sıralamalar,
örtüşmeler ve bütün karşılaştırmalar korunmaktadır. Tez v21'de Tablo 18,
Tablo 10 ve Bölüm 9.7 tezin tanımına çevrilmiştir; Tablo 18'in başlığına tanım
notu eklenmiştir.

*10.09.2026 · Claude · kendi tespit ettiğim tanım tutarsızlığının düzeltmesi.*

**Düzeltilmiş türetilmiş değer.** Tablo 10'un (ve çatı makalesinin Tablo 3'ünün)
bakım satırındaki fark sütunu, düzeltilmiş ortalamalardan yeniden
hesaplanmıştır: birleşik 0.1777 − merkezî 0.1885 = **−0.0108** (önceki tanımla
−0.0087). Fark sütunu yalnız betimleyicidir; hüküm güven aralıklarının
örtüşmesine göre kurulmuştur ve örtüşme sürmektedir.
