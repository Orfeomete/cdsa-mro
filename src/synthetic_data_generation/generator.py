"""
CDSA-MRO Sentetik Veri Üretim Motoru v2 — Şablon Tabanlı
==========================================================
LLM bağımsız, deterministik (seed=42), parametre havuzları ile
varyasyon üretimi. Bir saniyede 1000+ kayıt üretebilir.

Tez başlığı: Pekiştirmeli Öğrenme ve Veri Yerelliği ile Bakım
Organizasyonlarında Sürekli Uçuşa Elverişlilik için Sentetik Veri
Tabanlı Siber-Emniyet Olay Tahmini

Sürüm: CDSA-MRO-SDG v2.0
Yazar: Mete Cantekin
Lisans: CC-BY 4.0
"""

import json
import random
import os
from datetime import datetime, timedelta
from pathlib import Path

# Deterministik üretim
SEED = 42
random.seed(SEED)

URETIM_MOTORU_VERSIYON = "CDSA-MRO-SDG-v2.0"
EPSILON_DP = 0.8

# ------------------------------------------------------------------
# OLAY TÜRLERİ ve AĞIRLIKLAR (toplam = 1.00)
# ------------------------------------------------------------------
OLAY_TURLERI = [
    ("oltalama_saldirisi", 0.10),
    ("hesap_ele_gecirme", 0.07),
    ("ot_sistem_sizmasi", 0.08),
    ("fidye_yazilimi", 0.05),
    ("ddos_saldirisi", 0.05),
    ("tedarik_zinciri_kontaminasyonu", 0.05),
    ("usb_zararli_yazilim", 0.08),
    ("shadow_it", 0.10),
    ("konfigurasyon_hatasi", 0.08),
    ("yetki_iptal_eksikligi", 0.07),
    ("egitim_sistem_manipulasyonu", 0.04),
    ("kalibrasyon_butunluk_ihlali", 0.05),
    ("portal_erisim_ihlali", 0.05),
    ("sosyal_muhendislik", 0.07),
    ("is_emri_sahteciligi", 0.06),
]

# Olay türü → tipik risk seviyesi (varyasyon ±1)
OLAY_RISK_HARITA = {
    "oltalama_saldirisi": 3, "hesap_ele_gecirme": 4, "ot_sistem_sizmasi": 4,
    "fidye_yazilimi": 4, "ddos_saldirisi": 3, "tedarik_zinciri_kontaminasyonu": 4,
    "usb_zararli_yazilim": 3, "shadow_it": 2, "konfigurasyon_hatasi": 3,
    "yetki_iptal_eksikligi": 3, "egitim_sistem_manipulasyonu": 3,
    "kalibrasyon_butunluk_ihlali": 4, "portal_erisim_ihlali": 4,
    "sosyal_muhendislik": 3, "is_emri_sahteciligi": 4,
}

# MITRE ATT&CK haritası
MITRE_HARITASI = {
    "oltalama_saldirisi": ("TA0001", "T1566", "T1566.002"),
    "hesap_ele_gecirme": ("TA0006", "T1110", ""),
    "ot_sistem_sizmasi": ("TA0001", "T1091", ""),
    "fidye_yazilimi": ("TA0040", "T1486", ""),
    "ddos_saldirisi": ("TA0040", "T1498", ""),
    "tedarik_zinciri_kontaminasyonu": ("TA0001", "T1195", "T1195.002"),
    "usb_zararli_yazilim": ("TA0001", "T1091", ""),
    "shadow_it": ("TA0010", "T1567", ""),
    "konfigurasyon_hatasi": ("TA0007", "T1133", ""),
    "yetki_iptal_eksikligi": ("TA0001", "T1078", ""),
    "egitim_sistem_manipulasyonu": ("TA0009", "T1565", ""),
    "kalibrasyon_butunluk_ihlali": ("TA0009", "T1565", "T1565.001"),
    "portal_erisim_ihlali": ("TA0001", "T1556", ""),
    "sosyal_muhendislik": ("TA0006", "T1556", ""),
    "is_emri_sahteciligi": ("TA0040", "T1565", ""),
}

# Ek-19 kontrol noktası haritası (her olay türü için 3-4 nokta)
EK19_KONTROL_HARITA = {
    "oltalama_saldirisi": ["1.2.1", "4.1.1", "1.4.2"],
    "hesap_ele_gecirme": ["1.1.1", "1.4.2", "13.2.1"],
    "ot_sistem_sizmasi": ["12.3.5", "6.2.1", "1.3.1", "15.1.1"],
    "fidye_yazilimi": ["9.1.1", "14.1.1", "5.2.1"],
    "ddos_saldirisi": ["12.2.1", "14.1.1", "5.1.1"],
    "tedarik_zinciri_kontaminasyonu": ["15.1.1", "18.2.1", "12.3.7"],
    "usb_zararli_yazilim": ["1.3.1", "4.2.1", "12.4.1"],
    "shadow_it": ["2.1.1", "1.5.1", "4.2.1"],
    "konfigurasyon_hatasi": ["12.4.1", "3.1.1", "18.1.1"],
    "yetki_iptal_eksikligi": ["1.1.4", "7.2.1", "1.4.2"],
    "egitim_sistem_manipulasyonu": ["4.3.1", "7.4.1", "3.2.1"],
    "kalibrasyon_butunluk_ihlali": ["3.2.1", "6.1.2", "1.4.2"],
    "portal_erisim_ihlali": ["1.4.2", "13.2.1", "1.6.1"],
    "sosyal_muhendislik": ["4.1.1", "1.6.1", "1.4.2"],
    "is_emri_sahteciligi": ["6.3.1", "3.2.2", "1.4.2"],
}

# ------------------------------------------------------------------
# PARAMETRE HAVUZLARI (varyasyon kaynağı)
# ------------------------------------------------------------------

TESISLER = [
    "İstanbul ana üs bakım hangarı", "Ankara hat bakım istasyonu",
    "İzmir hat bakım istasyonu", "Sabiha Gökçen ana üs bakım tesisi",
    "Antalya komponent atölyesi", "Esenboğa NDT atölyesi",
    "Adana hat bakım istasyonu", "Trabzon hat bakım istasyonu",
    "Gaziantep komponent atölyesi", "Diyarbakır hat bakım istasyonu",
]

PERSONEL_ROLLERI = [
    "B1 kategori onaylayıcı tekniker", "B2 kategori aviyonik teknisyeni",
    "B3 kategori pistonlu motor teknisyeni", "C kategori üs bakım sorumlu mühendisi",
    "Kurumsal SOME izleme uzmanı", "SGSYY (Siber Güvenlik Sorumlu Yöneticisi)",
    "BT operasyon yöneticisi", "Kalibrasyon teknisyeni", "Tedarikçi ilişkileri yöneticisi",
    "Sorumlu Müdür", "BKEK editör personeli", "Hat bakım vardiya sorumlusu",
    "Üs bakım koordinatörü", "Bakım kayıt yönetim sorumlusu",
]

SISTEMLER = [
    "AMOS bakım kayıt yazılımı", "TRAX bakım yönetim sistemi",
    "Ramco MRO çözümü", "kalibrasyon kayıt sunucusu",
    "ARBİS portal arabirimi", "BKEK doküman yönetim sistemi",
    "iş emri yönetim platformu", "tedarikçi entegrasyon API",
    "NDT cihaz kontrol bilgisayarı", "tork anahtarı kalibrasyon sistemi",
    "yedek parça envanter veritabanı", "personel yetkilendirme portalı",
    "uçak yer destek iletişim ağı", "ofis e-posta sunucusu",
]

ETKILENEN_HIZMET_HAVUZU = {
    "oltalama_saldirisi": [
        "Bakım kayıt yönetim sistemi", "ARBİS bağlantılı kuruluş portal erişimi",
        "Onaylayıcı personel yetkilendirme kuyruğu", "Kurumsal e-posta sunucusu",
        "BKEK doküman erişimi"
    ],
    "hesap_ele_gecirme": [
        "Onaylayıcı personel imza yetkisi", "Bakım çıkış sertifikası onay zinciri",
        "Yetkilendirme yönetim portalı", "Sorumlu Müdür onay arabirimi"
    ],
    "ot_sistem_sizmasi": [
        "NDT cihaz kontrol bilgisayarı", "Atölye yerel ağ segmenti",
        "Kalibrasyon kayıt sunucusu", "Tahribatsız muayene veri tabanı",
        "Motor test rig kontrol sistemi"
    ],
    "fidye_yazilimi": [
        "Bakım kayıt yazılımı veri tabanı", "BKEK doküman arşivi",
        "Personel sicil dosyaları", "Müşteri sözleşme arşivi",
        "Geriye dönük bakım kayıtları (3 yıl)"
    ],
    "ddos_saldirisi": [
        "Yer destek iletişim sistemi", "Hat bakım istasyonu portalı",
        "Tedarikçi sipariş arabirimi", "Hava aracı durum izleme paneli"
    ],
    "tedarik_zinciri_kontaminasyonu": [
        "Yedek parça yönetim yazılımı", "OEM güncelleme dağıtım altyapısı",
        "İş istasyonu kurulu yazılımları", "Envanter veritabanı",
        "Tedarikçi entegrasyon API"
    ],
    "usb_zararli_yazilim": [
        "Atölye terminal bilgisayarı", "NDT cihaz arabirimi",
        "Ofis bilgisayarı", "Vardiya odası ortak kullanım terminali"
    ],
    "shadow_it": [
        "İş kartı fotoğrafları", "Bakım kayıt ekran görüntüleri",
        "Kalibrasyon değer dökümleri", "Vardiya değişim notları",
        "Personel kişisel mesajlaşma platformu"
    ],
    "konfigurasyon_hatasi": [
        "Bulut depolama bucket", "API endpoint", "Geliştirme ortamı veritabanı",
        "Test sunucu arabirimi", "Yedekleme erişim portalı"
    ],
    "yetki_iptal_eksikligi": [
        "İşten ayrılan personelin tüm erişimleri", "ARBİS hesap yetkisi",
        "BKEK yazma yetkisi", "Bakım kayıt sistem erişimi"
    ],
    "egitim_sistem_manipulasyonu": [
        "E-öğrenme platformu", "Sınav sonuç kayıtları",
        "Sertifika düzenleme arabirimi", "Personel yetkilendirme veritabanı"
    ],
    "kalibrasyon_butunluk_ihlali": [
        "Tork anahtarı kalibrasyon kayıtları", "NDT cihaz kalibrasyon değerleri",
        "Yetkilendirilmiş kalibrasyon dökümü süreci", "Bakım çıkış sertifikası geriye dönük inceleme"
    ],
    "portal_erisim_ihlali": [
        "Sorumlu Müdür ARBİS hesabı", "BKEK dijital onay erişimi",
        "SGSYY portal yetkisi", "Yetkilendirme dijital imza"
    ],
    "sosyal_muhendislik": [
        "Yardım masası parola sıfırlama", "Yönetici onay zinciri taklit",
        "Çağrı merkezi yetkilendirme", "BT destek erişim formu"
    ],
    "is_emri_sahteciligi": [
        "Bakım çıkış sertifikası", "İş emri dijital imza",
        "Kalibrasyon iş kartı", "Komponent kabul kaydı"
    ],
}

# Olay açıklama şablonları (5 varyant × 15 olay = 75 şablon)
OZET_SABLONLAR = {
    "oltalama_saldirisi": [
        "{tesis} merkezinde görev yapan {personel} hesabına, SHGM ARBİS sistemini taklit eden bir oltalama e-postası ulaşmıştır. Personel sahte portal arabirimine kimlik bilgilerini girdikten yaklaşık {sure_dak} dakika sonra Kurumsal SOME tarafından olağandışı IP üzerinden başarılı oturum tespit edilmiş ve hesap askıya alınmıştır.",
        "{tesis} ofisinde {personel} pozisyonundaki personele, uçak üreticisi servis bültenini taklit eden bir e-posta gönderilmiştir. Personel ekteki bağlantıyı tıklayarak {sistem} sayfasının kopyasına yönlenmiş ve kimlik bilgilerini paylaşmıştır.",
        "{tesis} biriminde çalışan {personel}, Form-4 yenileme zorunluluğu gerekçesiyle gönderilen sahte SHGM e-postasına yanıt vererek kurumsal şifresini değiştirme talebi yapmıştır. İstek meşru bir kaynaktan gelmediğinden Kurumsal SOME tarafından gözlemlenmiş ve {sure_dak} dakika içinde yanıt verilmiştir.",
        "{personel} unvanlı bir kullanıcı, vergi dairesinden geldiği iddia edilen sahte bir e-posta üzerinden {sistem} oturum açma sayfasının taklidine yönlendirilmiştir. Kimlik bilgisi girişi sonrası Kurumsal SOME anomali tespit kuralı uyarı üretmiştir.",
        "{tesis} biriminde görev yapan {personel}, kendi kuruluş alan adına benzer bir e-posta hesabından gönderilen takvim daveti içeriği üzerinden kimlik avı saldırısına maruz kalmıştır. Olay {sure_dak} dakika içinde fark edilmiş ve hesap kilitlenmiştir.",
    ],
    "hesap_ele_gecirme": [
        "{personel} unvanlı kullanıcının kurumsal hesabı, zayıf parola örüntüsü nedeniyle yapılan brute force saldırısı sonucu ele geçirilmiştir. Saldırı sırasında {sistem} üzerinde {sure_dak} dakika süren yetkisiz erişim gerçekleştirilmiştir.",
        "{tesis} merkezindeki {personel} hesabına ait kimlik bilgileri, başka bir hizmette yaşanan veri ihlali sonucu sızdırılmıştır. Aynı parolanın kurumsal hesapta yeniden kullanılması nedeniyle saldırgan {sistem} arabirimine erişim sağlamıştır.",
        "Kurumsal SOME, {personel} hesabıyla normal çalışma saatleri dışında yapılmış {sure_dak} dakikalık olağandışı oturum tespit etmiştir. Olay incelendiğinde hesabın ele geçirildiği ve {sistem} üzerinde okuma denemeleri yapıldığı anlaşılmıştır.",
        "{tesis} biriminde çalışan {personel}, çok faktörlü kimlik doğrulama aktive olmadığı için hesabının ele geçirilmesine maruz kalmıştır. Saldırgan {sistem} üzerinden geçmiş bakım kayıtlarını incelemeye başlamıştır.",
        "{personel} hesabına yönelik şifre püskürtme (password spraying) saldırısı tespit edilmiştir. Saldırı, ortak kullanılan zayıf parolalar denenerek gerçekleştirilmiş ve hesap {sure_dak} dakika boyunca yetkisiz erişime açık kalmıştır.",
    ],
    "ot_sistem_sizmasi": [
        "{tesis} bünyesindeki NDT atölyesinde bulunan {sistem}, kalibrasyon güncellemesi sırasında bağlanan bir USB belleğin içerdiği zararlı yazılım nedeniyle kompromize olmuştur. Zararlı kod {sure_dak} dakika sonra atölye yerel ağında yatay geçiş başlatmıştır.",
        "{tesis} motor test atölyesindeki {sistem}, güncel olmayan yazılım sürümü üzerindeki bilinen bir zafiyetin istismarı sonucu yetkisiz erişime maruz kalmıştır. Saldırgan {sure_dak} dakika boyunca cihaz log kayıtlarını manipüle etmeye çalışmıştır.",
        "{tesis} hangarındaki kalibrasyon kontrol sistemi, üretici varsayılan parolasının değiştirilmemesi nedeniyle ele geçirilmiştir. Olay {sure_dak} dakika içinde davranış tabanlı izleme aracı tarafından tespit edilmiştir.",
        "{tesis} avionic atölyesinde kullanılan {sistem}, BT ağı ile OT ağı arasındaki yetersiz segmentasyon nedeniyle ofis ağından bulaşan zararlı yazılıma maruz kalmıştır.",
        "{tesis} bünyesindeki {sistem}, üretici tarafından bildirilmemiş bir güvenlik açığı (zero-day) üzerinden hedeflenmiş saldırıya konu olmuştur. {sure_dak} dakika sürebilmiş etkili olduktan sonra Kurumsal SOME izole etmiştir.",
    ],
    "fidye_yazilimi": [
        "{tesis} merkezindeki {sistem}, bir oltalama e-postası eki üzerinden bulaşan fidye yazılımı tarafından şifrelenmiştir. Şifreleme {sure_dak} dakika içinde tamamlanmış ve bakım kayıt erişimi tamamen kaybedilmiştir.",
        "{tesis} bünyesindeki yedek sunucu, bir RDP zafiyeti üzerinden sızılan fidye yazılımı saldırısına maruz kalmıştır. Yedekler dahil tüm {sistem} verileri şifrelenmiştir.",
        "{personel} hesabı üzerinden bulaşan fidye yazılımı, {tesis} ağındaki paylaşımlı sürücülerde yayılarak {sistem} üzerindeki tüm bakım kayıtlarını şifrelemiştir.",
        "{tesis} biriminde tedarikçi yazılım güncelleme paketi içinde gizli olan fidye yazılımı, yüklendikten {sure_dak} dakika sonra aktif olmuştur. Olay üretim hattının {sure_dak} dakika durmasına neden olmuştur.",
        "{tesis} merkezinde bilinmeyen bir kanaldan iş istasyonuna bulaşan fidye yazılımı, {sistem} veri tabanını şifrelemiş ve fidye mesajı bırakmıştır.",
    ],
    "ddos_saldirisi": [
        "{tesis} hat bakım istasyonu portalına yapılan dağıtık hizmet engelleme saldırısı, {sistem} üzerinde {sure_dak} dakika boyunca erişim kesintisine neden olmuştur.",
        "{tesis} merkezinin internet bağlantısı, botnet kaynaklı HTTP flood saldırısı nedeniyle {sure_dak} dakika boyunca yetersiz performansla çalışmıştır. {sistem} arabirimi etkilenmiştir.",
        "{tesis} bünyesindeki {sistem} servisi, DNS amplification saldırısına maruz kalmıştır. Erişim {sure_dak} dakika boyunca bozulmuştur.",
        "{tesis} dış yüzlü portalına yapılan SYN flood saldırısı, {sistem} sunucusunun {sure_dak} dakika boyunca yanıt verememesine neden olmuştur.",
        "{tesis} ağ geçidi, Layer 7 düzeyinde uygulama tabanlı DDoS saldırısı altında kalmıştır. {sistem} kullanıcı talepleri {sure_dak} dakika boyunca düşmüştür.",
    ],
    "tedarik_zinciri_kontaminasyonu": [
        "{tesis} merkezinde kullanılan {sistem}, tedarikçi tarafından imzalı görünen ancak kompromize edilmiş bir bağımlılık kütüphanesi içeren güncelleme paketi nedeniyle kontamine olmuştur. Zararlı modül {sure_dak} dakika sessiz kaldıktan sonra dış HTTP çağrıları başlatmıştır.",
        "{tesis} bünyesinde dağıtılan üretici güncellemesi, bağımlılık zinciri kompromizasyonu sonucu zararlı kod taşımıştır. {sistem} üzerinde {sure_dak} dakika içinde anormal davranış görülmüştür.",
        "{tesis} kullandığı {sistem} için OEM tarafından imzalanmış güncelleme paketi, üreticinin DevOps boru hattındaki anahtar sızıntısı nedeniyle kompromize edilmiştir.",
        "{tesis} biriminde otomatik dağıtım sistemine yüklenen üretici güncellemesi, üçüncü taraf kütüphane içine gizlenmiş zararlı yazılım modülü içermiştir.",
        "{tesis} tedarikçisinden alınan {sistem} bileşeni, üretici güvenlik incelemesinden geçmeden gelen kompromize bir paketle kontamine olmuştur.",
    ],
    "usb_zararli_yazilim": [
        "{tesis} bünyesindeki {personel}, kişisel USB belleğinden {sistem} terminaline veri kopyalamak istemiştir. USB içinde gizli zararlı yazılım çalışarak ağ keşfi başlatmıştır.",
        "{tesis} atölyesinde çalışan {personel} ziyaretçi USB cihazı kullanırken {sistem} bulaşmıştır. Olay {sure_dak} dakika içinde tespit edilmiştir.",
        "{tesis} biriminde bir üretici teknisyeni kendi USB cihazıyla {sistem} arabirimine bağlanmış ve farkında olmadan zararlı yazılım yüklenmiştir.",
        "{personel} kişisel bilgisayarından getirdiği USB belleği {tesis} ofis bilgisayarında kullanmış ve {sistem} ağına bulaşmıştır.",
        "{tesis} merkezinde dosya transferi için ortak kullanılan USB cihazlardan birinin kompromize olduğu fark edilmiştir. {sistem} {sure_dak} dakika boyunca etkilenmiştir.",
    ],
    "shadow_it": [
        "{tesis} biriminde {personel} grubu, kurumsal iletişim platformu yetersiz bulduğu için WhatsApp grupları üzerinden {sistem} ekran görüntüleri paylaşmıştır. KVKK iç denetiminde olay tespit edilmiştir.",
        "{tesis} merkezinde bazı çalışanlar, onaylanmış kurumsal hizmet yerine kişisel bulut hesaplarına {sistem} verisi yüklemeye başlamıştır.",
        "{personel} pozisyonundaki kullanıcı, kurumsal yazılımın mobil sürümünün geç açıldığı için kişisel telefonundaki üçüncü taraf uygulama üzerinden {sistem} kayıtlarını izlemiştir.",
        "{tesis} biriminde {personel} ekibi, vardiya değişimi notlarını kurumsal sistem yerine kişisel mesajlaşma kanallarında paylaşmaktadır. Olay {sure_dak} dakika sürmüş bir denetimde fark edilmiştir.",
        "{tesis} merkezinde {personel} grubu, kurumsal onaydan geçmemiş bir verimlilik aracını kullanmaya başlamış ve {sistem} verisini bu araca aktarmaktadır.",
    ],
    "konfigurasyon_hatasi": [
        "{tesis} bünyesindeki {sistem}, geliştirme ortamından üretim ortamına geçişte güvenlik ayarları varsayılan değerlerde bırakılmıştır. {sure_dak} dakika boyunca dışarıdan erişilebilir kalmıştır.",
        "{tesis} merkezinin {sistem} bulut depolama paketi yanlış izin ayarları nedeniyle açık duruma gelmiştir.",
        "{tesis} biriminde yapılan altyapı değişikliği sırasında {sistem} API arabirimi kimlik doğrulamasız hale gelmiştir.",
        "{tesis} bünyesinde DevOps boru hattındaki bir hata, {sistem} oturum tokenlarını hatalı yapılandırmaya neden olmuştur.",
        "{personel} tarafından yapılan rutin yapılandırma değişikliği sırasında {sistem} sunucusu yetkisiz tarama isteklerine açık hale gelmiştir.",
    ],
    "yetki_iptal_eksikligi": [
        "{tesis} biriminden bir ay önce ayrılan {personel} hesabının {sistem} erişimi iptal edilmemiştir. Eski personel uzaktan {sure_dak} dakika boyunca giriş yapabilmiştir.",
        "{tesis} merkezinden ayrılan {personel}, kuruluş içinde dağıtılan dijital sertifikası hâlâ aktif olduğu için {sistem} kayıtlarına erişim sağlayabilmiştir.",
        "İşten ayrılan {personel} hesabına ait dijital imza yetkisi, İK ve BT arası iletişim kopukluğu nedeniyle iptal edilmemiştir.",
        "{tesis} biriminde görev değişikliği yapan {personel}, eski görevine ait yetkilerini hâlâ taşıdığı için {sistem} üzerinde gerekli olmayan yetkilerle çalışmaktadır.",
        "{personel} ile sözleşmesi feshedilen bir tedarikçi çalışanı, {sistem} portalına {sure_dak} dakika içinde tekrar giriş yapabildiğini göstermiştir.",
    ],
    "egitim_sistem_manipulasyonu": [
        "{tesis} e-öğrenme platformunda {personel} hesabı üzerinden bir kategori sınavının cevap anahtarına yetkisiz erişim yapılmıştır.",
        "{tesis} biriminin sertifika düzenleme sisteminde {personel} adına geçerli olmayan bir kategori yetkisi tanımlanmıştır.",
        "{personel} pozisyonundaki kişi, e-öğrenme platformunda sınav puanını manipüle ederek kategori yetkisi kazanmıştır.",
        "{tesis} merkezinde bir B2 lisans sınavı sırasında {sistem} arabiriminden cevap anahtarı sızdırılmıştır.",
        "{tesis} biriminde kullanılan sertifika doğrulama servisi, {personel} hesabı üzerinden manipüle edilmiş ve geçersiz bir sertifika geçerli kabul edilmiştir.",
    ],
    "kalibrasyon_butunluk_ihlali": [
        "{tesis} merkezindeki {sistem}, dört adet tork anahtarı kalibrasyon kaydının {personel} hesabıyla manuel olarak değiştirilmesi sonucu bütünlük ihlaline maruz kalmıştır. Olay iç denetimde fark edilmiştir.",
        "{tesis} NDT atölyesinde {sistem} üzerinde son altı ay içindeki kalibrasyon değerlerinde yetkisiz değişiklik yapıldığı tespit edilmiştir.",
        "{tesis} biriminde {personel} tarafından girilen kalibrasyon değerleri, denetim izi olmadan {sistem} üzerinde güncellenmiştir.",
        "{tesis} kalibrasyon kayıtlarında {personel} hesabı üzerinden geriye dönük tarih damgası manipülasyonu yapıldığı anlaşılmıştır.",
        "{tesis} bünyesindeki {sistem} arabiriminde {personel} bilinmeyen bir saldırgan, yetkisiz kalibrasyon değer değişikliği yapmıştır.",
    ],
    "portal_erisim_ihlali": [
        "{personel} ARBİS hesabının parolası başka bir hizmette yaşanan ihlal nedeniyle sızdırılmıştır. {tesis} biriminden yetkili kullanıcı olarak {sistem} arabirimine yetkisiz giriş yapılmıştır.",
        "{tesis} merkezindeki {personel} hesabı, MFA bypass tekniği üzerinden ele geçirilmiş ve {sistem} portalına yetkisiz oturum açılmıştır.",
        "{tesis} biriminden Sorumlu Müdür hesabı, oturum hijacking yöntemiyle ele geçirilmiştir. Saldırgan {sistem} üzerinde yetkili kullanıcı olarak {sure_dak} dakika kalmıştır.",
        "{personel} ARBİS hesabı, kimlik doğrulama mekanizmasının değiştirilmesi yoluyla başka bir cihazdan da erişilebilir hale getirilmiştir.",
        "{tesis} SGSYY hesabına ait dijital imza, fiziksel olarak çalınmış bir USB anahtar üzerinden {sistem} portalına yetkisiz onay vermek için kullanılmıştır.",
    ],
    "sosyal_muhendislik": [
        "{tesis} yardım masasını arayan kimliği bilinmeyen bir kişi, kendisini {personel} olarak tanıtarak parola sıfırlama talep etmiştir. Talep yerine getirilmiş ve {sistem} hesabı saldırgana açık hale gelmiştir.",
        "{tesis} bünyesindeki {personel} pozisyonundaki çalışan, kendisini IT yöneticisi olarak tanıtan bir kişiye telefonla kurumsal şifresini paylaşmıştır.",
        "{tesis} biriminde Sorumlu Müdür adına gönderilen sahte e-posta üzerinden {personel}, bir tedarikçi ödemesini yetkisiz hesap üzerinden yapmıştır.",
        "{personel} pozisyonundaki çalışana sahte SHGM denetim uyarısı içeren bir görüşme yapılmış ve gizli onay kodu paylaşıma açılmıştır.",
        "{tesis} merkezinde {personel} adına oluşturulmuş sahte bir profil üzerinden iç iletişim kanallarında manipülasyon başlatılmıştır.",
    ],
    "is_emri_sahteciligi": [
        "{tesis} merkezinde {personel} adına düzenlenen bir bakım çıkış sertifikası, dijital imza ayarlarındaki bir açık kullanılarak sahte üretilmiştir. Olay {sure_dak} dakika sürmüş bir iç kontrolde fark edilmiştir.",
        "{tesis} biriminde {sistem} üzerinden sahte bir komponent kabul kaydı oluşturulmuş ve fiziksel olmayan bir parçanın bakımdan geçtiği belirtilmiştir.",
        "{personel} hesabı kullanılarak {tesis} bünyesinde {sistem} üzerinde yetkisiz bir iş emri tamamlama kaydı oluşturulmuştur.",
        "{tesis} merkezinde bir bakım iş kartı üzerindeki imza ve sicil numarası, {personel} hesabı üzerinden yetkisiz olarak değiştirilmiştir.",
        "{tesis} biriminde elektronik iş emri arabiriminde {personel} tarafından gerçekleştirilmemiş bir tamir işlemi tamamlanmış olarak işaretlenmiştir.",
    ],
}

# Süreç detay şablonları (her olay türü için 3 varyant)
SUREC_SABLONLAR = {
    "oltalama_saldirisi": [
        "Olayın kronolojisi sabah saat {saat_h} {saat_m} civarında kurumsal e-posta sunucusuna ulaşan oltalama iletisiyle başlamıştır. İleti, başlık satırında resmi bir kurum referansı taşıyordu ve gönderici alanı meşrulaştırılmış görünüyordu. {personel}, dönemsel BKEK güncelleme süreci nedeniyle bu iletinin gerçek olduğunu varsaydı ve gömülü bağlantıyı tıkladı. Açılan sahte portal arabirimi görsel olarak orijinalinin neredeyse birebir kopyasıydı. Kullanıcı adı ve parola girildikten kısa süre sonra aynı kimlik bilgileriyle olağandışı bir IP adresinden başarılı oturum açıldığı Kurumsal SOME izleme paneline yansıdı. Anormal coğrafi konum tabanlı oturum filtresinin tetiklenmesiyle hesap askıya alındı, parola sıfırlandı ve aynı oltalama dalgasına maruz kalmış diğer personel uyarıldı.",
        "Olay zinciri, {personel} pozisyonundaki kullanıcının üç gün önce alınmış sahte bir yazışmayı sehven açmasıyla başladı. E-posta hizmet sağlayıcısının spam filtresi iletide şüpheli bir parametre tespit edememiş ve mesaj normal kullanıcı kutusuna düşmüştü. Mesajdaki bağlantı tıklandığında yönlendirilen sayfa, çok katmanlı yönlendirme zinciri kullanarak kullanıcıyı sahte oturum açma arabirimine taşıdı. Bilgilerin girilmesinin ardından arka planda gerçek kurumsal portal üzerinde otomatik oturum açıldı ve birkaç dakika içinde okuma denemeleri yapıldı. Olay Kurumsal SOME tarafından ağ akış analizi sırasında fark edildi.",
        "Olay {personel} hesabına gelen ve görünüşte iç iletişim biriminden gönderilmiş bir doküman bildirimi e-postasıyla başladı. Mesajda gömülü olan görsel öğeler resmi kurum kimliğine uygun renkler taşıyordu. Kullanıcı, dokümanın kuruluş içi bir araç üzerinden açılması gerektiği uyarısı nedeniyle sahte oturum açma arabirimine yönlendirildi. Bilgileri girdikten yaklaşık {sure_dak} dakika sonra anormal davranış izleme aracı uyarı üretti ve hesap kilitlendi.",
    ],
    "hesap_ele_gecirme": [
        "Olay, başka bir hizmette yaşanan veri ihlali sonucu sızdırılan kimlik bilgilerinin {personel} hesabında yeniden kullanılması nedeniyle gerçekleşti. Saldırgan, otomatik bir kimlik dolgu (credential stuffing) aracıyla binlerce hesap denerken {personel} hesabına ulaştı. Hesapta çok faktörlü kimlik doğrulama aktif olmadığından doğrudan oturum açıldı. Saldırgan {sistem} üzerinde okuma yetkilerini kullanarak geçmiş bakım kayıtlarını taradı. Kurumsal SOME, normal çalışma saatleri dışındaki coğrafi anormallik nedeniyle olayı {sure_dak} dakika sonra tespit etti.",
        "Olay zinciri, {personel} hesabına yönelik şifre püskürtme saldırısıyla başladı. Saldırgan, ortak kullanılan zayıf parolaların listesini sırayla deneyerek tek bir hesap üzerinde değil çok sayıda hesap üzerinde paralel denemeler yaptı. Çok faktörlü kimlik doğrulamanın aktif olmadığı {personel} hesabı bu yöntemle ele geçirildi. Saldırgan {sistem} arabirimine giriş yaparak yaklaşık {sure_dak} dakika boyunca yetkili kullanıcı olarak hareket etti.",
        "Olay, {personel} kullanıcısının başka bir iş için kullandığı bir cihazda parola yöneticisinin kompromize olması sonucu kurumsal kimlik bilgilerinin sızdırılmasıyla başladı. Sızdırılan veriler dark web pazarlarında satışa çıkarıldı. Saldırgan kimlik bilgilerini satın aldıktan sonra {sistem} arabirimine yetkisiz giriş yaptı. Kurumsal SOME olayı saat 03 yönündeki başarılı oturum nedeniyle tespit etti.",
    ],
    "ot_sistem_sizmasi": [
        "Olayın başlangıç noktası, {tesis} bünyesindeki NDT atölyesinde {sistem} cihazının üretici tarafından önerilen yıllık yazılım güncellemesidir. Teknisyen, üretici sitesinden indirilen paketi kişisel USB belleğe kopyalayıp kontrol bilgisayarına bağladı. USB cihazı beyaz listede olmamasına rağmen port fiziksel olarak kilitli değildi. Güncelleme paketinin imza doğrulaması başarılı görünüyordu ancak içine gizlenmiş ikinci yürütülebilir bileşen, kalibrasyon kayıt sunucusuna yatay geçiş hazırlığı için zamanlanmış görev oluşturdu. Görev {sure_dak} dakika sonra port tarama başlattı. Davranış tabanlı tespit kuralı yatay hareketi yakalayarak cihazı izole etti.",
        "OT sistemine sızma süreci, {tesis} bünyesindeki {sistem} cihazının üretici varsayılan parolasının kuruluş tarafından değiştirilmemiş olmasıyla başladı. Saldırgan kuruluş ofis ağına önceden bulaşmış olan ana arka kapıdan, OT segmentasyonundaki yetersizlik nedeniyle bu cihaza ulaştı. Cihaza yapılan ilk bağlantı sonrası saldırgan {sure_dak} dakika boyunca cihaz log kayıtlarını manipüle etmeye çalıştı.",
        "Olay, {tesis} merkezindeki {sistem} cihazının yazılımındaki bilinen bir zafiyetin istismarı yoluyla başladı. Üreticinin yayımladığı yama, sahada kurulu cihazlara henüz dağıtılmamıştı. Saldırgan zafiyeti istismar ederek cihazda yetki yükseltme yaptı ve {sure_dak} dakika boyunca yetkili kullanıcı olarak hareket etti.",
    ],
    "fidye_yazilimi": [
        "Olay zinciri, {personel} pozisyonundaki kullanıcının açtığı bir e-posta eki ile başladı. Ek görünürde bir fatura PDF dosyasıydı ancak makro içeren bir Office belgesini taklit ediyordu. Belge açıldığında zincirleme bir yükleme süreci başladı ve {sure_dak} dakika içinde {tesis} ağındaki paylaşılan sürücülerdeki tüm {sistem} verilerini şifreledi. Şifreleme tamamlandığında ekrana fidye mesajı geldi. Yedekler offline olduğundan veri kurtarma süreci alternatif kaynaklardan ilerletildi.",
        "Saldırı, {tesis} bünyesindeki bir RDP (Uzak Masaüstü) sunucusunun internete açık bırakılmış olması ve zayıf parolayla korunmasıyla başladı. Saldırgan brute force ile erişim sağladı ve manuel olarak ağda gezinerek {sistem} sunucusunu hedefledi. Fidye yazılımı manuel olarak konuşlandırıldı ve kritik sistemler şifrelendi.",
        "Olay, tedarikçi yazılım güncelleme paketinde gizlenmiş bir fidye yazılımı yükleyicisinin {tesis} üzerinde otomatik dağıtılmasıyla başladı. Yükleyici {sure_dak} dakika sessiz bekledi, ardından şifreleme sürecini tetikledi. {sistem} ve bağlı sürücülerdeki tüm dosyalar erişilemez hale geldi.",
    ],
    "ddos_saldirisi": [
        "Saldırı, {tesis} merkezinin {sistem} portalına ait IP adresine yapılan dağıtık HTTP flood saldırısıyla başladı. Saldırı {sure_dak} dakika boyunca dakikada milyonlarca istek seviyesinde sürdü. Kuruluşun trafik filtreleme altyapısı saldırı paketlerini ayırmakta zorlandı, dış kullanıcılar için portal erişilemez hale geldi.",
        "DDoS olayı, {tesis} bünyesindeki açık DNS çözümleyici üzerinden gerçekleştirilen amplifikasyon saldırısıyla başladı. Saldırgan saldırıyı diğer hedeflere yönlendirmek için kuruluş altyapısını ara sunucu olarak kullandı. Bu süreçte kuruluşun çıkış bant genişliği {sure_dak} dakika boyunca tükendi.",
        "Saldırı, {tesis} merkezinin uygulama katmanındaki belirli bir form gönderim endpoint'ine yönelik düşük hacimli ama yüksek hesaplama yükü oluşturan isteklerle gerçekleştirildi. Saldırgan akıllıca {sistem} sunucusunun veritabanı işlemcisini aşırı yüklemeyi hedefledi ve {sure_dak} dakika boyunca servisin yanıt verme süresi onbinlerce milisaniyeye çıktı.",
    ],
    "tedarik_zinciri_kontaminasyonu": [
        "Olay, {tesis} merkezinde kullanılan {sistem} için tedarikçinin yayımladığı rutin güncelleme paketi ile başladı. Paket resmi imza doğrulamasından geçerek otomatik dağıtım altyapısıyla iş istasyonlarına yüklendi. Sorun, paketin içerdiği üçüncü taraf bağımlılık kütüphanesinin önceden kompromize edilmiş olmasıydı. Kompromize, üreticinin DevOps boru hattındaki bir anahtar sızıntısı yoluyla gerçekleşti. Modül yüklenmenin ardından {sure_dak} dakika sessiz kaldı, daha sonra envanter veritabanından küçük HTTP istekleri ile veri sızdırmaya başladı.",
        "Tedarik zinciri kontaminasyonu, {tesis} kullandığı {sistem} bileşeninin OEM tarafından sertifikalı olmayan bir alt tedarikçi üzerinden temin edilmesiyle başladı. Bileşen kuruluşa ulaştığında üzerinde önceden yüklenmiş arka kapı bulunuyordu. {sure_dak} dakika boyunca etkisi sürdü.",
        "Olay, üreticinin imzalama anahtarı ele geçirilmiş bir paket yayımladığını bildirmesiyle açığa çıktı. Paket {tesis} bünyesinde 11 iş istasyonuna otomatik olarak dağıtılmıştı. Üretici bildirisi sonrası tüm istasyonlar izole edildi ve forensik inceleme başlatıldı.",
    ],
    "usb_zararli_yazilim": [
        "Olay, {personel} kullanıcısının kişisel olarak kullandığı USB bellekteki belgeyi {tesis} ofis bilgisayarına kopyalamak istemesiyle başladı. USB cihazı kullanım öncesinde beyaz listede değildi ve port kilitleme uygulanmamıştı. USB içinde otomatik çalışan zararlı bir bileşen, takıldığı anda zincirleme yükleme başlattı. {sure_dak} dakika içinde ağda yatay hareket denendi ve Kurumsal SOME tespit etti.",
        "Bir ziyaretçi teknisyen, {tesis} atölyesinde {sistem} arabirimine kendi USB cihazıyla bağlandı. Cihaz daha önce başka bir ortamda kompromize olmuştu. Bağlantının ardından zararlı yazılım kuruluş ağına yayıldı.",
        "Olay, {tesis} bünyesinde ortak kullanılan USB cihazlardan birinin kompromize olduğunun fark edilmesiyle başladı. {personel} cihazı son bir hafta içinde birkaç farklı iş istasyonunda kullandığı için yayılma alanı genişti.",
    ],
    "shadow_it": [
        "Mart ayında, hat bakım vardiyalarında değişen ekipler arasında iletişim sorunları yaşandığı için bir kıdemli teknisyen, mesai dışı saatlerde sorulara hızlı cevap üretebilmek amacıyla WhatsApp üzerinden bir grup oluşturdu. Grup zamanla onlarca personele genişledi. {personel} dahil ekip üyeleri, anlık bakım sorularını çözmek için iş kartlarının fotoğraflarını ve {sistem} ekran görüntülerini bu gruba göndermeye başladı. Uygulama iki aydan uzun sürdü. KVKK iç denetiminde fark edildi ve olay özel nitelikli kişisel veri potansiyel ihlali olarak SHGM ve KVKK Kurumu'na bildirildi.",
        "{tesis} merkezinde bazı çalışanlar, kurumsal verimlilik aracının yavaş olduğunu düşünerek piyasada bulunan ücretsiz bir alternatife geçmeye başladı. Kullandıkları araç {sistem} verisini bulut ortamına yüklüyordu ve sözleşme dışı yer aldığı bilinmiyordu.",
        "Bir personel grubu, {tesis} bünyesinde işten ayrılma süreçlerini hızlandırmak için kişisel mobil cihazlarındaki bir uygulamayla {sistem} bilgisini izlemeye başladı. Onaylı kanal dışı bu uygulama, KVKK denetiminde tespit edildi.",
    ],
    "konfigurasyon_hatasi": [
        "Olay, {tesis} merkezinde {sistem} sunucusunun üretim ortamına geçişi sırasında güvenlik ayarlarının varsayılan değerlerde bırakılmasıyla başladı. Geliştirme ortamında devre dışı bırakılmış olan kimlik doğrulama, dağıtım sürecinde tekrar etkinleştirilmedi. Sunucu {sure_dak} dakika boyunca dışarıdan kimlik doğrulamasız erişime açık kaldı.",
        "Konfigürasyon hatası, {tesis} bünyesinde {sistem} bulut depolama paketinin yanlış izin ayarlarıyla yapılandırılmasıyla ortaya çıktı. Paket dış internete açık ACL ile dağıtıldı ve {sure_dak} dakika boyunca herkes tarafından erişilebilir oldu.",
        "Bir rutin altyapı değişikliği sırasında {personel} tarafından yapılan ayar güncellemesi {sistem} API kimlik doğrulamasını devre dışı bıraktı. Olay {sure_dak} dakika içinde fark edilince ayar geri alındı.",
    ],
    "yetki_iptal_eksikligi": [
        "Olay, {tesis} biriminden ayrılan {personel} hesabının {sistem} erişiminin iptal edilmemesiyle başladı. Personel ayrılışından bir ay sonra eski kuruluş hesabıyla uzaktan oturum açtı. {sure_dak} dakika boyunca yetkili kullanıcı olarak hareket etti. Olay haftalık erişim denetiminde fark edildi.",
        "{tesis} merkezinde sözleşmesi feshedilen bir tedarikçi çalışanı, kuruluşa ait dijital sertifikası hâlâ aktif olduğu için {sistem} kayıtlarına erişim sağlamaya devam etti. İK ve BT arasındaki iletişim kopukluğu nedeniyle sertifika iptali atlanmıştı.",
        "Görev değişikliği yapan {personel}, eski rolüne ait yetkilerin iptal edilmemesi nedeniyle {sistem} üzerinde gereksiz yetkilerle çalışmaya devam etti. {sure_dak} dakika içinde periyodik denetimde fark edildi.",
    ],
    "egitim_sistem_manipulasyonu": [
        "Olay, {tesis} e-öğrenme platformunda bir kategori sınavının cevap anahtarına yetkisiz erişim yapılmasıyla başladı. {personel} hesabı üzerinden bu anahtar bir başka kullanıcıyla paylaşıldı. Olay sınav sonuçlarının istatistiksel analizinde anormallik tespit edilince fark edildi.",
        "{tesis} sertifika düzenleme sisteminde {personel} adına geçerli olmayan bir kategori yetkisi tanımlandı. Personel bu yetkiyle imza yetkili görev üstlenmeye çalıştı. Olay ARBİS'e gönderilen kategori onay isteklerinde çapraz kontrol sırasında fark edildi.",
        "{personel} hesabı kullanılarak {sistem} arabirimi üzerinden sınav puanı manipüle edildi ve yetki kazanıldı. Olay {sure_dak} dakika sonra denetimde tespit edildi.",
    ],
    "kalibrasyon_butunluk_ihlali": [
        "Periyodik iç denetim sırasında {tesis} bünyesindeki {sistem} kayıtlarında dört adet tork anahtarı değerinin {personel} hesabıyla manuel olarak değiştirildiği fark edildi. Denetim izi yalnızca son bir hafta için ayrıntılı tutulduğundan eski değişiklikler için sadece özet log mevcuttu. Olay {sure_dak} dakika içinde geriye dönük bakım çıkış sertifikalarının gözden geçirilmesi gerektiğini ortaya koydu. SHY-145 Madde 18 kapsamında bildirim yapıldı.",
        "{tesis} NDT atölyesinde {sistem} üzerinde son altı ay içinde gerçekleştirilen kalibrasyon değerlerinde yetkisiz değişiklik yapıldığı fark edildi. Değişikliklerin tek bir oturumda yapılmış olması saldırının manuel ve hedeflenmiş olduğunu gösterdi.",
        "{personel} hesabı üzerinden {tesis} merkezindeki {sistem} arabiriminde geriye dönük tarih damgası manipülasyonu yapıldığı fark edildi. Manipülasyon, bir bakım kaydının zamanını değiştirerek o tarihte mevcut olmayan bir yetki kullanılmış gibi göstermeyi amaçlıyordu.",
    ],
    "portal_erisim_ihlali": [
        "Olay, {personel} ARBİS hesabına ait parolanın başka bir hizmette yaşanan ihlal sonucu sızdırılmasıyla başladı. Saldırgan, çok faktörlü kimlik doğrulamanın aktif olmadığı hesap üzerinden {sistem} portalına oturum açtı. {sure_dak} dakika boyunca yetkili kullanıcı olarak hareket etti.",
        "{tesis} biriminden Sorumlu Müdür hesabı, oturum hijacking yöntemiyle ele geçirildi. Saldırgan kullanıcının aktif oturum tokenını elde ederek aynı oturumu paralel cihazda kullandı.",
        "{personel} hesabına ait dijital imza, fiziksel olarak çalınan bir USB anahtar üzerinden {sistem} portalına yetkisiz onay vermek için kullanıldı. Olay imzaların çift onay zinciri kontrolünde fark edildi.",
    ],
    "sosyal_muhendislik": [
        "Olay, {tesis} yardım masasına gelen kimliği bilinmeyen bir aramayla başladı. Arayan kendisini {personel} olarak tanıttı ve acil iş gerekçesiyle parola sıfırlama talep etti. Yardım masası çalışanı, doğrulama protokolünü kısmen atlayarak talebi yerine getirdi. Yeni parola ile {sistem} hesabına saldırgan giriş yaptı.",
        "{personel}, kendisini IT yöneticisi olarak tanıtan bir kişiye telefonla kurumsal şifresini paylaştı. Olay daha sonra Kurumsal SOME tarafından yapılan farkındalık tarama aramasında ortaya çıktı.",
        "Sahte SHGM denetim uyarısı içeren bir görüşme {personel} ile yapıldı. Aramada gizli onay kodu istendi ve paylaşıldı. Saldırgan bu kodla {sistem} arabirimine yetkili kullanıcı olarak erişti.",
    ],
    "is_emri_sahteciligi": [
        "Olay, {tesis} merkezinde {personel} adına düzenlenen bir bakım çıkış sertifikasının dijital imza ayarlarındaki açık kullanılarak sahte üretilmesiyle başladı. Sertifika {sistem} kayıtlarına işlendi ve görünürde geçerli olarak değerlendirildi. {sure_dak} dakika içinde gerçekleştirilen iç kontrolde sahte olduğu anlaşıldı.",
        "{tesis} biriminde {sistem} üzerinden sahte bir komponent kabul kaydı oluşturuldu. Fiziksel olarak bakımdan geçmemiş bir parça için kabul kaydı dijital ortamda oluşturulmuştu. Olay parçanın fiziksel envanter kontrolünde fark edildi.",
        "{personel} hesabı kullanılarak {tesis} bünyesinde {sistem} üzerinde yetkisiz bir iş emri tamamlama kaydı oluşturuldu. İşlem çapraz kontrolde fark edildi ve geri alındı.",
    ],
}

# Temel neden şablonları
KOKNEDEN_SABLONLAR = {
    "oltalama_saldirisi": [
        "Personelin oltalama farkındalık eğitiminin altı aydan uzun süredir yenilenmemiş olması ve kurumsal e-posta ağ geçidinde dış alan adı doğrulamasının (DMARC strict) aktif olmaması.",
        "Çok faktörlü kimlik doğrulamanın yalnızca BT sistem yöneticileri için aktif olması ve diğer rollere yayılmamış olması.",
        "Anormal coğrafi konum tabanlı oturum tespit eşik süresinin saatlik olması, gerçek zamanlı tespit yeteneğinin eksikliği.",
    ],
    "hesap_ele_gecirme": [
        "Çok faktörlü kimlik doğrulamanın tüm kullanıcılara zorunlu kılınmamış olması ve parola politikasının zayıf örüntülere izin vermesi.",
        "Parola tekrar kullanım kontrolünün uygulanmaması ve dark web ihlal monitörlemesinin eksikliği.",
        "Çalışma saatleri dışı oturum açma tespitinin geç tepki vermesi ve davranış tabanlı kullanıcı analitiğinin eksikliği.",
    ],
    "ot_sistem_sizmasi": [
        "OT segmentindeki cihazlarda USB portu fiziksel kilit veya yazılım tabanlı erişim kontrolünün uygulanmamış olması.",
        "BT ve OT ağ segmentasyonunun yalnızca VLAN seviyesinde olması, mikro-segmentasyonun uygulanmaması.",
        "Üretici varsayılan parolalarının değiştirilmemiş olması ve OT cihazlarının yazılım sürümlerinin güncel tutulmaması.",
    ],
    "fidye_yazilimi": [
        "Yedeklerin offline olmaması ve yedek bütünlüğünün düzenli olarak test edilmemesi.",
        "Personelin makro içeren e-posta eki açma riskine karşı eğitilmemiş olması.",
        "Uzak masaüstü hizmetlerinin internete açık bırakılmış olması ve zayıf parolalarla korunması.",
    ],
    "ddos_saldirisi": [
        "Trafik filtreleme altyapısının dağıtık saldırı senaryolarına karşı yeterli kapasiteye sahip olmaması.",
        "Açık DNS çözümleyici olması ve bunun amplifikasyon saldırılarında kötüye kullanılması.",
        "Uygulama katmanı saldırı tespitinin sınırlı kalması ve yalnızca ağ katmanı izlemenin yapılması.",
    ],
    "tedarik_zinciri_kontaminasyonu": [
        "Üretici güncelleme paketinde bağımsız bağımlılık zinciri doğrulamasının (SBOM analizi) yapılmaması.",
        "Dağıtım öncesi karantina döneminin uygulanmaması ve doğrudan otomatik dağıtım.",
        "Tedarikçi sözleşmelerinde SBOM ibrazı zorunluluğunun bulunmaması.",
    ],
    "usb_zararli_yazilim": [
        "USB cihaz beyaz liste politikasının uygulanmaması ve port fiziksel kilidi olmaması.",
        "Personelin USB güvenliği konusunda farkındalık eksikliği.",
        "Antimalware araçlarının USB cihazlarda otomatik tarama yapacak şekilde yapılandırılmamış olması.",
    ],
    "shadow_it": [
        "Kurumsal iletişim yazılımının mobil cihaz desteğinin yetersiz olması ve BYOD politikasının yokluğu.",
        "Personel farkındalık eğitiminde KVKK biyometrik veri kapsamının eksik anlatımı.",
        "Vardiya değişimi iletişim protokolünün dijital olarak desteklenmemesi.",
    ],
    "konfigurasyon_hatasi": [
        "Geliştirmeden üretime geçişte güvenlik ayarlarının otomatik doğrulanmaması.",
        "Bulut yapılandırma denetiminin sürekli izleme aracı olmadan yapılması.",
        "Altyapı kod yönetiminin (Infrastructure as Code) güvenlik onay zincirinden geçirilmemesi.",
    ],
    "yetki_iptal_eksikligi": [
        "İK ve BT birimleri arasındaki personel çıkış bildirimi protokolünün yetersiz olması.",
        "Erişim yetkilerinin periyodik gözden geçirme döngüsünün uzun olması.",
        "Tedarikçi çalışan yetkilerinin sözleşme bitişiyle otomatik iptalinin uygulanmaması.",
    ],
    "egitim_sistem_manipulasyonu": [
        "E-öğrenme platformunda sınav cevap anahtarı erişiminin az sayıda kişiye verilmesinin sağlanmaması.",
        "Sertifika düzenleme yetkisinin tek kişiye bağımlı olması ve görev ayrılığı uygulanmaması.",
        "Sınav sonuçlarının istatistiksel anormallik analizinin yapılmaması.",
    ],
    "kalibrasyon_butunluk_ihlali": [
        "Kalibrasyon kayıt yazılımında değişiklik denetim izinin yalnızca kısa süreli tutulması ve eski değişikliklerin kriptografik korunmaması.",
        "Kalibrasyon değer değişikliklerinin onay zincirli iş akışı yerine tek kullanıcı erişimiyle yapılabilir olması.",
        "İç denetim periyodunun aylık değil çeyrek dönemli olması ve geç tespite yol açması.",
    ],
    "portal_erisim_ihlali": [
        "Çok faktörlü kimlik doğrulamanın tüm yetkili kullanıcılara zorunlu kılınmaması.",
        "Oturum yönetim politikasında oturum tokenlarının sınırlı süreli olmaması ve token rotasyonu uygulanmaması.",
        "Dijital imza modüllerinin fiziksel güvence altına alınmaması.",
    ],
    "sosyal_muhendislik": [
        "Yardım masası kimlik doğrulama protokollerinin yetersiz olması ve çoklu doğrulama gerektirmemesi.",
        "Personelin sosyal mühendislik teknikleri konusunda farkındalık eğitimi almamış olması.",
        "Yönetici taklit saldırılarına karşı imza tabanlı doğrulama prosedürünün uygulanmaması.",
    ],
    "is_emri_sahteciligi": [
        "Dijital imza modüllerinin yeterince güvenli olmaması ve çift imza zincirinin uygulanmaması.",
        "İş emri ve bakım çıkış sertifikası kayıtlarının kriptografik bütünlük korumasından geçmemesi.",
        "Komponent fiziksel envanter ile dijital kayıt arasında otomatik çapraz kontrol mekanizmasının olmaması.",
    ],
}

# Aksiyon havuzları
AKSIYON_HAVUZU = {
    "oltalama_saldirisi": [
        ("Tüm kullanıcı rollerine zorunlu MFA aktive edilecek.", "SGSYY", "acil"),
        ("Kurumsal e-posta ağ geçidinde DMARC reject politikası uygulanacak.", "BT_Mudur", "acil"),
        ("Anormal coğrafi konum oturum tespiti 5 dakikalık periyoda çekilecek.", "Kurumsal_SOME", "yuksek"),
        ("Yıllık oltalama simülasyonu programı kurulumu yapılacak.", "SGSYY", "yuksek"),
        ("Tüm personele güncellenmiş oltalama farkındalık eğitimi verilecek.", "SGSYY", "yuksek"),
    ],
    "hesap_ele_gecirme": [
        ("Çok faktörlü kimlik doğrulama tüm hesaplara zorunlu hale getirilecek.", "SGSYY", "acil"),
        ("Parola politikası güçlendirilecek ve dark web izleme servisi aktive edilecek.", "BT_Mudur", "yuksek"),
        ("Davranış tabanlı kullanıcı analitiği (UEBA) sistemi devreye alınacak.", "Kurumsal_SOME", "yuksek"),
        ("Olağandışı oturum açma alarmı 5 dakikaya çekilecek.", "Kurumsal_SOME", "acil"),
    ],
    "ot_sistem_sizmasi": [
        ("Tüm OT cihazlarının USB portlarına fiziksel kilit takılacak.", "Sorumlu_Mudur", "acil"),
        ("OT-BT mikro-segmentasyon projesi başlatılacak.", "BT_Mudur", "yuksek"),
        ("Üretici varsayılan parolaları zorunlu olarak değiştirilecek.", "BT_Mudur", "acil"),
        ("OT cihazları için özel davranış tabanlı izleme kuralları kapsamı genişletilecek.", "Kurumsal_SOME", "yuksek"),
    ],
    "fidye_yazilimi": [
        ("Yedekleme stratejisi 3-2-1 prensibine göre yeniden yapılandırılacak.", "BT_Mudur", "acil"),
        ("Yedek bütünlüğü haftalık test edilecek.", "BT_Mudur", "yuksek"),
        ("Uzak masaüstü hizmetleri VPN arkasına alınacak.", "BT_Mudur", "acil"),
        ("E-posta eki çalıştırma kısıtlaması (sandboxing) uygulanacak.", "Kurumsal_SOME", "yuksek"),
    ],
    "ddos_saldirisi": [
        ("DDoS koruma servisi kapasitesi yükseltilecek.", "BT_Mudur", "acil"),
        ("Açık DNS çözümleyici kapatılacak.", "BT_Mudur", "acil"),
        ("Uygulama katmanı saldırı tespiti devreye alınacak.", "Kurumsal_SOME", "yuksek"),
        ("Trafik anomali tespiti gerçek zamanlı yapılandırılacak.", "Kurumsal_SOME", "yuksek"),
    ],
    "tedarik_zinciri_kontaminasyonu": [
        ("Tüm üretici güncelleme paketleri 24 saat sandbox karantinasından geçirilecek.", "Kurumsal_SOME", "acil"),
        ("Tedarikçi sözleşmelerine SBOM ibrazı zorunluluğu eklenecek.", "Tedarikci_Yonetim", "yuksek"),
        ("Davranış tabanlı izleme gerçek zamanlı yapılandırılacak.", "Kurumsal_SOME", "yuksek"),
        ("Etkilenen iş istasyonları forensik analiz sonrası yeniden imaj alınacak.", "BT_Mudur", "acil"),
    ],
    "usb_zararli_yazilim": [
        ("USB cihaz beyaz liste politikası uygulanacak.", "BT_Mudur", "acil"),
        ("Atölye cihazlarının USB portları fiziksel olarak kilitlenecek.", "Sorumlu_Mudur", "acil"),
        ("Personele USB güvenlik farkındalık eğitimi verilecek.", "SGSYY", "yuksek"),
        ("Otomatik antimalware tarama USB takılışında zorunlu olacak.", "BT_Mudur", "yuksek"),
    ],
    "shadow_it": [
        ("KVKK uyumlu kurumsal mobil iletişim platformuna geçiş yapılacak.", "BT_Mudur", "acil"),
        ("BYOD politikası yazılacak ve onaylı uygulama listesi belirlenecek.", "SGSYY", "yuksek"),
        ("Tüm personele KVKK özel nitelikli veri kapsamı eğitimi verilecek.", "SGSYY", "yuksek"),
        ("KVKK iç denetim periyodu aylık seviyeye çekilecek.", "SGSYY", "orta"),
    ],
    "konfigurasyon_hatasi": [
        ("Geliştirmeden üretime geçişte otomatik güvenlik denetimi zorunlu hale getirilecek.", "BT_Mudur", "acil"),
        ("Sürekli yapılandırma izleme aracı (CSPM) kurulacak.", "Kurumsal_SOME", "yuksek"),
        ("Altyapı kod yönetimi (IaC) güvenlik onay zincirinden geçirilecek.", "BT_Mudur", "yuksek"),
    ],
    "yetki_iptal_eksikligi": [
        ("İK ve BT arası personel çıkış protokolü dijitalleştirilecek.", "SGSYY", "acil"),
        ("Erişim yetkileri 3 ayda bir gözden geçirilecek.", "BT_Mudur", "yuksek"),
        ("Tedarikçi çalışan yetkileri sözleşme bitiş tarihine bağlı otomatik iptal edilecek.", "Tedarikci_Yonetim", "yuksek"),
    ],
    "egitim_sistem_manipulasyonu": [
        ("Sınav cevap anahtarı erişimi azaltılacak ve şifrelenecek.", "SGSYY", "acil"),
        ("Sertifika düzenleme yetkisi görev ayrılığı ile uygulanacak.", "Sorumlu_Mudur", "yuksek"),
        ("Sınav sonuçları istatistiksel anormallik analizinden geçirilecek.", "SGSYY", "orta"),
    ],
    "kalibrasyon_butunluk_ihlali": [
        ("Kalibrasyon değişiklik denetim izi süresiz arşivlenecek ve kriptografik özet ile korunacak.", "BT_Mudur", "acil"),
        ("Kalibrasyon değer değişiklikleri için Sorumlu Müdür onay zinciri devreye alınacak.", "Sorumlu_Mudur", "acil"),
        ("İç denetim periyodu aylık seviyeye çekilecek.", "SGSYY", "yuksek"),
        ("Görev ayrılığı politikası tüm bütünlük kritik rollere uygulanacak.", "SGSYY", "yuksek"),
    ],
    "portal_erisim_ihlali": [
        ("MFA tüm yetkili kullanıcılara zorunlu hale getirilecek.", "SGSYY", "acil"),
        ("Oturum tokenları sınırlı süreli ve döner olacak şekilde yapılandırılacak.", "BT_Mudur", "acil"),
        ("Dijital imza modülleri fiziksel güvence altına alınacak.", "Sorumlu_Mudur", "yuksek"),
    ],
    "sosyal_muhendislik": [
        ("Yardım masası kimlik doğrulama protokolü çoklu doğrulama gerektirecek şekilde güncellenecek.", "SGSYY", "acil"),
        ("Tüm personele sosyal mühendislik farkındalık eğitimi verilecek.", "SGSYY", "yuksek"),
        ("Yönetici taklit saldırılarına karşı imza tabanlı doğrulama prosedürü yazılacak.", "SGSYY", "yuksek"),
    ],
    "is_emri_sahteciligi": [
        ("Dijital imza modülleri sertleştirilecek ve çift imza zinciri uygulanacak.", "Sorumlu_Mudur", "acil"),
        ("İş emri kayıtları kriptografik bütünlük korumasından geçirilecek.", "BT_Mudur", "yuksek"),
        ("Komponent fiziksel envanter ile dijital kayıt arasında otomatik çapraz kontrol kurulacak.", "BT_Mudur", "yuksek"),
        ("Bakım çıkış sertifikası geriye dönük incelemesi yapılacak.", "Onaylayici_Personel", "acil"),
    ],
}

# Swiss Cheese katmanı havuzu
SWISS_CHEESE_HAVUZU = [
    ("personel_egitimi", "Personel farkındalık eğitiminin son altı ay içinde yenilenmemiş olması."),
    ("teknik_kontrol", "Otomatik teknik güvenlik kontrolünün yetersiz yapılandırılmış olması."),
    ("denetim", "Periyodik denetim aralığının olay tespitine geç tepki vermesi."),
    ("fiziksel_guvenlik", "Fiziksel erişim kontrolünün bazı OT alanlarında yetersiz olması."),
    ("tedarikci", "Tedarikçi güvenlik denetiminin sözleşme düzeyinde zayıf kalması."),
    ("yonetim", "Görev ayrılığı politikasının kritik rollere yayılmamış olması."),
]


# ------------------------------------------------------------------
# ÜRETİM FONKSİYONLARI
# ------------------------------------------------------------------

def benzersiz_olay_id(s):
    return f"CDSA-MRO-SDG-{s:06d}"

def rastgele_mro_id():
    bolge = random.choice(["TR", "TR", "TR", "TR", "EU"])
    return f"MRO-{bolge}-{random.randint(1, 999):03d}"

def rastgele_tarih():
    baslangic = datetime(2024, 1, 1)
    gun = random.randint(0, 730)
    return baslangic + timedelta(
        days=gun, hours=random.randint(0, 23), minutes=random.randint(0, 59)
    )

def laplace_gurultu(deger, scale=10):
    return max(0, int(deger + random.gauss(0, scale)))

def risk_dagilimina_uygun_sec():
    """Hedef dağılıma göre olay türü seçer ve risk seviyesini ayarlar."""
    olay_turu = random.choices(
        [t[0] for t in OLAY_TURLERI],
        weights=[t[1] for t in OLAY_TURLERI],
        k=1
    )[0]
    # Risk varyasyonu ±1
    risk = OLAY_RISK_HARITA[olay_turu]
    if random.random() < 0.2:
        risk = max(1, min(4, risk + random.choice([-1, 1])))
    return olay_turu, risk

def senaryo_uret(sira):
    olay_turu, risk = risk_dagilimina_uygun_sec()
    tarih = rastgele_tarih()
    sure_dak = laplace_gurultu(random.randint(30, 2000), scale=50)
    bitis = tarih + timedelta(minutes=sure_dak)
    tactic, technique, subtech = MITRE_HARITASI[olay_turu]

    tesis = random.choice(TESISLER)
    personel = random.choice(PERSONEL_ROLLERI)
    sistem = random.choice(SISTEMLER)

    ozet_template = random.choice(OZET_SABLONLAR[olay_turu])
    ozet = ozet_template.format(
        tesis=tesis, personel=personel, sistem=sistem,
        sure_dak=sure_dak
    )

    surec_template = random.choice(SUREC_SABLONLAR[olay_turu])
    surec = surec_template.format(
        tesis=tesis, personel=personel, sistem=sistem,
        sure_dak=sure_dak, saat_h=tarih.hour, saat_m=tarih.minute
    )

    temel_neden = random.choice(KOKNEDEN_SABLONLAR[olay_turu])

    # Katkıda bulunan etmenler (3-5 adet)
    katki_etmenleri = random.sample(KOKNEDEN_SABLONLAR[olay_turu], min(3, len(KOKNEDEN_SABLONLAR[olay_turu])))
    if len(katki_etmenleri) < 3:
        # Diğer olay türlerinden de etmenler al
        diger = random.choice(list(KOKNEDEN_SABLONLAR.values()))
        katki_etmenleri.append(random.choice(diger))

    swiss_cheese = random.sample(SWISS_CHEESE_HAVUZU, k=random.randint(3, 5))

    # Aksiyonlar
    aksiyon_secim = random.sample(AKSIYON_HAVUZU[olay_turu], min(4, len(AKSIYON_HAVUZU[olay_turu])))
    aksiyonlar = []
    for idx, (acik, rol, oncelik) in enumerate(aksiyon_secim, 1):
        aksiyonlar.append({
            "aksiyon_no": idx, "aciklama": acik, "sorumlu_rol": rol, "oncelik": oncelik
        })

    # Projelendirme (aksiyon başına bir proje)
    projelendirme = []
    for idx, aks in enumerate(aksiyonlar, 1):
        gun_suresi = random.choice([14, 30, 60, 90, 180])
        projelendirme.append({
            "proje_no": idx,
            "duzeltici_faaliyet": aks["aciklama"],
            "baslama_tarihi": (tarih + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d"),
            "bitis_tarihi": (tarih + timedelta(days=gun_suresi)).strftime("%Y-%m-%d"),
        })

    etkilenen = random.sample(
        ETKILENEN_HIZMET_HAVUZU[olay_turu],
        k=min(random.randint(2, 4), len(ETKILENEN_HIZMET_HAVUZU[olay_turu]))
    )

    maddi_kayip = laplace_gurultu(random.randint(5000, 500000), scale=2000)

    kvkk_iceriyor = olay_turu in [
        "oltalama_saldirisi", "hesap_ele_gecirme", "shadow_it",
        "yetki_iptal_eksikligi", "egitim_sistem_manipulasyonu", "sosyal_muhendislik"
    ] or random.random() < 0.3

    bildirim_72sa = random.choices([True, False], weights=[0.88, 0.12], k=1)[0]

    return {
        "olay_id": benzersiz_olay_id(sira),
        "olay_tarihi": tarih.isoformat(),
        "firma_anonim_id": rastgele_mro_id(),
        "olay_ozeti": {
            "olay_turu": olay_turu,
            "saat_araligi": {
                "baslangic": tarih.isoformat(),
                "bitis": bitis.isoformat(),
            },
            "olay_aciklama": ozet,
            "kesinti_suresi_dakika": sure_dak,
            "etkilenen_hizmetler": etkilenen,
            "tahmini_maddi_kayip_TL": maddi_kayip,
        },
        "olay_sureci": surec,
        "kok_neden_analizi": {
            "temel_neden": temel_neden,
            "katkida_bulunan_etmenler": katki_etmenleri,
            "swiss_cheese_katmanlari": [
                {"katman": k, "delik_aciklamasi": d} for k, d in swiss_cheese
            ],
        },
        "aksiyonlar": aksiyonlar,
        "projelendirme": projelendirme,
        "etiketler": {
            "risk_seviyesi": risk,
            "risk_seviyesi_metin": ["", "dusuk", "orta", "yuksek", "kritik"][risk],
            "mitre_attack": {"tactic": tactic, "technique": technique, "subtechnique": subtech},
            "shtsiber_ek19_kontrol_atfi": EK19_KONTROL_HARITA[olay_turu],
            "kvkk_ozel_veri_iceriyor": kvkk_iceriyor,
            "shy145_madde18_72saat_uygunluk": bildirim_72sa,
        },
        "metaveri": {
            "uretim_tarihi": datetime.now().isoformat(),
            "uretim_motor_versiyonu": URETIM_MOTORU_VERSIYON,
            "sentetik_garanti": {
                "epsilon_dp": EPSILON_DP,
                "gercek_kisi_atfi": False,
                "gercek_firma_atfi": False,
                "gercek_olay_atfi": False,
            },
            "delphi_dogrulama": {
                "uzman_sayisi": 0,
                "realism_score": None,
                "compliance_score": None,
                "delphi_round_count": 0,
            },
        },
    }


def toplu_uret(N=1000, cikti_dizini="data/output"):
    Path(cikti_dizini).mkdir(parents=True, exist_ok=True)
    senaryolar = []
    for i in range(1, N + 1):
        s = senaryo_uret(i)
        senaryolar.append(s)
        if i % 200 == 0:
            print(f"  Üretildi: {i}/{N}")

    # Tek bir JSON dosyası olarak da kaydet
    out_json = Path(cikti_dizini) / "sentetik_olaylar_v1.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(senaryolar, f, ensure_ascii=False, indent=2)
    print(f"\nTüm kayıtlar tek JSON dosyaya kaydedildi: {out_json}")
    print(f"Toplam kayıt: {len(senaryolar)}")
    print(f"Dosya boyutu: {os.path.getsize(out_json) / (1024*1024):.2f} MB")

    return senaryolar


if __name__ == "__main__":
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    print(f"CDSA-MRO-SDG v2.0 — Şablon Tabanlı Üretim — N={N}")
    print(f"Deterministik seed: {SEED}")
    print()
    senaryolar = toplu_uret(N=N)
    print("\nTamamlandı.")
