"""E15 anahtar sözcük kodlayıcısı (K1). Veri okunmadan donduruldu.

Her sınıf için küçük harfe çevrilmiş özet metninde aranan ifadeler. Bir
özette birden çok sınıf eşleşirse sözlükteki SIRA önceliği belirler
(önce eklenen siber-fiziksel sınıflar, sonra klasik sınıflar). Hiçbiri
eşleşmezse 'kapsam_disi'.
"""
import re

ATM = [
    ("gnss_spoofing", [r"spoof"]),
    ("gnss_jamming", [r"jamm", r"gps (signal )?interference", r"gnss interference", r"interference (testing|test)", r"gps (outage|unreliable|not available|unavailable)", r"raim"]),
    ("adsb_injection", [r"ads-?b.{0,40}(false|ghost|spurious|phantom|bogus)"]),
    ("datalink_interruption", [r"cpdlc", r"data ?link", r"acars"]),
    ("surveillance_data_loss", [r"radar (outage|failure|loss|went down|was out)", r"loss of radar", r"surveillance (outage|loss)", r"radar data"]),
    ("atm_system_intrusion", [r"intrusion", r"hack", r"malware", r"cyber"]),
    ("voice_channel_spoofing", [r"(unauthorized|rogue|phantom|fake|bogus) (transmission|controller|instruction)"]),
    ("notam_tampering", [r"notam.{0,40}(false|tamper|alter|bogus)"]),
    ("time_sync_attack", [r"time ?sync", r"clock (error|drift)", r"gps time"]),
    ("position_falsification", [r"(false|falsified|erroneous|incorrect) position"]),
    ("tcas_ra", [r"tcas", r"\bra\b", r"resolution advisory"]),
    ("loss_of_separation", [r"loss of separation", r"separation (was )?lost", r"less than (standard|required) separation", r"\bnmac\b", r"near mid ?air", r"conflict"]),
    ("runway_incursion", [r"runway incursion", r"incursion", r"crossed (the )?(active )?runway", r"hold short"]),
    ("airspace_infringement", [r"class [bcd] airspace", r"restricted (area|airspace)", r"prohibited (area|airspace)", r"\btfr\b", r"infring", r"penetrat", r"airspace violation", r"without (a )?clearance"]),
    ("frequency_congestion", [r"frequency congestion", r"congested frequency", r"busy frequency", r"blocked (transmission|frequency)", r"stepped on"]),
]

MRO = [
    ("ransomware", [r"ransomware"]),
    ("ddos_attack", [r"denial of service", r"\bddos\b"]),
    ("usb_malware", [r"(usb|flash drive|thumb drive).{0,40}(virus|malware)", r"(virus|malware).{0,40}(usb|flash drive|thumb drive)"]),
    ("phishing_attack", [r"phish"]),
    ("social_engineering", [r"social engineering", r"impersonat", r"pretext"]),
    ("account_takeover", [r"(account|password|credential).{0,40}(compromis|stolen|hijack)"]),
    ("portal_access_breach", [r"portal.{0,40}(breach|unauthori)"]),
    ("ot_system_intrusion", [r"intrusion", r"hack", r"malware", r"cyber"]),
    ("shadow_it", [r"(personal|unapproved|unauthori[sz]ed) (laptop|device|software|computer|app)"]),
    ("inadequate_access_revocation", [r"(former|terminated) employee", r"access (was )?not revoked"]),
    ("training_system_manipulation", [r"training record.{0,40}(falsif|alter|forg)", r"simulator.{0,40}manipul"]),
    ("work_order_forgery", [r"(forg|falsif).{0,60}(work order|task card|signature|sign-?off|logbook|entry|record)", r"(signed|stamped) off.{0,60}(not|never) (perform|done|accomplish)"]),
    ("calibration_integrity_violation", [r"calibrat"]),
    ("supply_chain_contamination", [r"counterfeit", r"unapproved part", r"bogus part", r"suspected unapproved", r"\bsup\b"]),
    ("configuration_error", [r"configur", r"software (load|version|update)", r"wrong (software|database)", r"incorrect (software|database)"]),
]


def kodla(metin: str, tipoloji: str) -> str:
    t = metin.lower()
    for sinif, desenler in (ATM if tipoloji == "ATM" else MRO):
        if any(re.search(d, t) for d in desenler):
            return sinif
    return "kapsam_disi"
