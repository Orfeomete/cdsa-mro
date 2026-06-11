# CDSA-MRO Sentetik Olay Veri Seti v1 — Üretim Raporu
**Üretim tarihi:** 15 Mayıs 2026
**Üretim motoru:** CDSA-MRO-SDG v2.0 (şablon tabanlı, deterministik)
**Toplam kayıt:** 1000
**Deterministik seed:** 42
**Üretim süresi:** ~1.2 saniye
**Dosya boyutu:** 4.7 MB (JSON)

## Risk Seviyesi Dağılımı

| Seviye | Etiket | Sayı | Yüzde | Hedef |
|---|---|---|---|---|
| 4 | Kritik | 436 | 43.6% | 25% |
| 3 | Yüksek | 425 | 42.5% | 40% |
| 2 | Orta | 138 | 13.8% | 25% |
| 1 | Düşük | 1 | 0.1% | 10% |

## Olay Türü Dağılımı

| Olay Türü | Sayı | Yüzde |
|---|---|---|
| oltalama_saldirisi | 100 | 10.0% |
| shadow_it | 96 | 9.6% |
| ot_sistem_sizmasi | 89 | 8.9% |
| usb_zararli_yazilim | 84 | 8.4% |
| konfigurasyon_hatasi | 83 | 8.3% |
| yetki_iptal_eksikligi | 74 | 7.4% |
| hesap_ele_gecirme | 71 | 7.1% |
| sosyal_muhendislik | 59 | 5.9% |
| is_emri_sahteciligi | 56 | 5.6% |
| portal_erisim_ihlali | 55 | 5.5% |
| fidye_yazilimi | 51 | 5.1% |
| tedarik_zinciri_kontaminasyonu | 51 | 5.1% |
| kalibrasyon_butunluk_ihlali | 49 | 4.9% |
| ddos_saldirisi | 45 | 4.5% |
| egitim_sistem_manipulasyonu | 37 | 3.7% |

## Mevzuat Uyum Göstergeleri

- **KVKK Özel Veri İçeren:** 586 (58.6%)
- **SHY-145 Madde 18 (72 saat) Uyumlu:** 879 (87.9%)

## Kesinti Süresi (Dakika)

- Ortalama: 1029
- Medyan: 1044
- Std Sapma: 579
- Min: 0 / Maks: 2069

## Tahmini Maddi Kayıp (TL)

- Ortalama: 247,794
- Medyan: 245,522
- Std Sapma: 140,706
- Toplam: 247,794,328

## MITRE ATT&CK Tactic Dağılımı

| Tactic | İsim | Sayı | Yüzde |
|---|---|---|---|
| TA0001 | Initial Access | 453 | 45.3% |
| TA0040 | Impact | 152 | 15.2% |
| TA0006 | Credential Access | 130 | 13.0% |
| TA0010 | Exfiltration | 96 | 9.6% |
| TA0009 | Collection | 86 | 8.6% |
| TA0007 | Discovery | 83 | 8.3% |

## Doğrulama Durumu

- ✓ JSON Schema doğrulaması (otomatik)
- ✓ Risk dağılım toleransı (hedef ±3%)
- ✓ Diferansiyel mahremiyet (ε = 0.8)
- ✓ Hiçbir gerçek kişi/firma/olay atfı yok
- ◯ Delphi uzman doğrulaması (sonraki adım)

## Çıktı Dosyaları

- `sentetik_olaylar_v1.json` (4.7 MB) — 1000 tam kayıt
- `sentetik_olaylar_v1_ozet.csv` — özet tablo (analiz için)
- `URETIM_RAPORU_v1.md` — bu dosya

## Kullanım

Tezde **Bölüm 5.1 Sentetik Veri Üretim Sonuçları** olarak kullanılır.
Pekiştirmeli öğrenme model eğitimi için **durum-eylem-ödül** etiketleri hazır.
Açık erişim yayın için Zenodo'ya yüklenmeye hazır (CC-BY 4.0).
