# CDSA-XYZ kör insan kodlama kitabı — tabakalar T0–T5

**Sürüm:** E9-1.0 · **Tarih:** 05.09.2026 · **Durum:** ⏳ **İNSAN KAYNAĞI BEKLİYOR**
**Ön kayıt:** `FAZ_E_ON_KAYIT_05092026.md`, bölüm E9 · Kural E9.1 yürürlükte.

> Bu kitap, `CDSA-XYZ/03_VAKA_DOSYALARI/NTSB_LLMcoded_v2_raporu.md` (28.06.2026) içindeki
> iki-katmanlı kodlama tanımından türetilmiştir. Ayrı bir `CDSA-XYZ kod kitabı` dosyası
> depoda **bulunamadığı için** tabaka tanımları o rapordaki kullanımdan yeniden yazılmıştır.
> Rapor kendi uyarısını taşır: **"LLM = ikinci kodlayıcı, insan altın-standardı değil."**
> Bu paketin amacı tam olarak o eksiği kapatmaktır.

## 0. Kodlama görevi

Kodlayıcıya bir olay anlatısı (NTSB serbest metin) verilir. Kodlayıcı **tek bir** tabaka
seçer: nedensel **loküsün** ağırlıklı olarak nerede olduğunu belirler. Etiket, anahtar
sözcüğe değil, anlatının bütününe göre verilir.

## 1. Tabakalar

| Kod | Ad | Tanım (loküs) | Dahil | Hariç |
|---|---|---|---|---|
| **T1** | Fizyolojik | Pilotun **bedensel/tıbbi** durumu olayın nedensel zincirinde yer alır | uçuş sırasında tıbbi olay, bilinç kaybı, hipoksi, ilaç/alkol etkisi, mekânsal yönelim bozukluğu | genel "pilot hatası" ifadeleri (→ T0), yalnız yorgunluk (→ T2) |
| **T2** | Yorgunluk | **İnsan** yorgunluğu / uyku borcu / dinlenme ihlali nedensel | görev süresi aşımı, uykusuzluk, sirkadiyen etki | **metal yorgunluğu → T5** |
| **T3** | Bakım | **Bakım / sürekli uçuşa elverişlilik** işlemi nedensel | hatalı montaj, atlanan bakım kalemi, yanlış parça, kayıt/iş emri hatası | üretim/tasarım kaynaklı parça kırılması (→ T5) |
| **T4** | Koordinasyon | **ATC / mürettebat kaynak yönetimi / kurumlar arası koordinasyon** nedensel | yanlış anlaşılan talimat, ayırma/klerans koordinasyon hatası, CRM çöküşü | yalnız yapısal "separation" olayları koordinasyon kaynaklı değilse (→ T0) |
| **T5** | Makine-kontrol | Loküs **uçak/sistem**: mekanik, yapısal, aviyonik veya güç sistemi arızası | motor arızası, yapısal yorulma (metal), sistem/aviyonik hata | insan tarafından tetiklenen ama donanımı sağlam olaylar (→ T0–T4) |
| **T0** | Diğer / tabaka dışı | Metin var ama loküs T1–T5'in hiçbirine ağırlıklı olarak oturmuyor | jenerik "pilot hatası", hava koşulu, çevresel etken | — |

## 2. Karar kuralları (uyuşmazlığı azaltmak için)

1. **Tek etiket.** Birden çok loküs varsa **nedensel zincirde en yukarıdaki** (kök) loküs seçilir.
2. **Metal yorgunluğu T2 değildir**, T5'tir (v2 regex düzeltmesinin kaynağı).
3. **Jenerik "pilot hatası" tek başına T1 yapmaz**; fizyolojik/tıbbi bir bulgu gerekir.
4. **Bakım kaynaklı arıza T3'tür**, arızanın kendisi mekanik olsa bile; tasarım/üretim kaynaklı ise T5.
5. Emin olunamayan kayıtlar **T0** değil, form üzerinde **"karar verilemedi"** işaretlenir ve
   üçüncü uzmana gider (T0 olumlu bir karardır).

## 3. Kodlayıcı ve körleştirme

- **İki bağımsız uzman** aynı örneği birbirinden habersiz kodlar.
- **Kör:** regex etiketi, LLM etiketi, kaza sonucu (ölümcül/ölümcül değil) ve olay kimliği gizlenir;
  kodlayıcı yalnız `kayit_no` (karıştırılmış) ve anlatıyı görür.
- **Uyuşmazlık çözümü:** üçüncü uzman, ilk iki kodun hangi kodlayıcıdan geldiğini bilmeden karar verir.
- **Ajan/LLM değerlendirmesi bu adımın yerine geçmez** (millî karar, 05.09.2026). LLM etiketi
  yalnız *karşılaştırılacak* nesnedir, altın standart değildir.

## 4. Ölçülecek büyüklükler

- Cohen κ (kodlayıcı 1 ↔ kodlayıcı 2), tabaka başına ve toplam; %95 GA.
- κ (insan uzlaşısı ↔ LLM etiketi) — raporda geçen κ = 0,492'nin insan referanslı karşılığı.
- Kural E9.1: seçilme olasılığıyla ağırlıklı RR ile ham RR'nin (13,2) GA'ları örtüşmezse
  iki değer **yan yana** yazılır, silinmez.

## 5. Durum

⏳ **İNSAN KAYNAĞI BEKLİYOR** — iki bağımsız uzman ve bir hakem uzman atanmamıştır.
⏳ **VERİ ERİŞİMİ BEKLİYOR** — kodlanmış korpus (`NTSB_LLMcoded_v2` çıktı tablosu) bu ortamda
yoktur; yalnız özet rapor ve `_istatistik_yukseltme_stats.json` mevcuttur. Örnek çekme betiği
veri yolu parametrelidir ve veri geldiğinde değişiklik gerektirmez.
