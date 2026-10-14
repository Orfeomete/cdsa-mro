import json, hashlib, sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).parent))
import anahtar_kodlayici as k1
import k2_kodlar as k2
H = Path(__file__).parent
def ozet(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ATM_SINIF = [s for s, _ in k1.ATM]; MRO_SINIF = [s for s, _ in k1.MRO]
EKLENEN_ATM = ATM_SINIF[:10]; KLASIK_ATM = ATM_SINIF[10:]
def oku(f):
    return [(int(l.split('|',1)[0]), l.split('|',1)[1].strip()) for l in (H/'veri'/f).read_text().splitlines() if l.strip()]
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b); pe = sum(ca[c] * cb[c] for c in set(a) | set(b)) / n**2
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0
sonuc = {'on_kayit_sha256': ozet(H/'E15_ON_KAYIT_11102026.md'), 'k1_sha256': ozet(H/'anahtar_kodlayici.py'),
         'k2_sha256': ozet(H/'k2_kodlar.py'), 'kumeler': {}}
tum1, tum2 = [], []
for kume, dosya, tip, K2 in [('GPS', 'gps.txt', 'ATM', k2.GPS), ('Controller', 'ctlr.txt', 'ATM', k2.CTLR),
                             ('PilotController', 'plt_ctlr.txt', 'ATM', k2.PLT), ('Maintenance', 'mechanic.txt', 'MRO', k2.MECH)]:
    veri = oku(dosya); assert len(veri) == 50 and set(a for a, _ in veri) == set(K2), kume
    c1, c2, bay, notlar = [], [], [], []
    for acn, metin in veri:
        v = K2[acn]; kod2 = v if isinstance(v, str) else v[0]
        if not isinstance(v, str):
            if v[1]: bay.append({'acn': acn, 'not': v[2], 'metin': metin})
            elif v[2]: notlar.append({'acn': acn, 'not': v[2]})
        c1.append(k1.kodla(metin, tip)); c2.append(kod2)
    po, kp = kappa(c1, c2)
    eklenen = EKLENEN_ATM if tip == 'ATM' else MRO_SINIF
    sinif_listesi = ATM_SINIF if tip == 'ATM' else MRO_SINIF
    r = {'tipoloji': tip, 'n': 50,
         'k1_kapsama': sum(x != 'kapsam_disi' for x in c1) / 50, 'k2_kapsama': sum(x != 'kapsam_disi' for x in c2) / 50,
         'k1_siklik': dict(Counter(c1)), 'k2_siklik': dict(Counter(c2)),
         'k2_eklenen_sinif_payi': sum(x in eklenen for x in c2) / 50,
         'yuzde_uyum': round(po, 4), 'kappa': round(kp, 4),
         'kapsam_ici_sinifsiz': bay, 'notlar': notlar,
         'uyusmazliklar': [{'acn': a, 'k1': x, 'k2': y} for (a, _), x, y in zip(veri, c1, c2) if x != y]}
    sonuc['kumeler'][kume] = r; tum1 += [(tip, x) for x in c1]; tum2 += [(tip, x) for x in c2]
    print(kume, 'K1 kapsama', r['k1_kapsama'], 'K2 kapsama', r['k2_kapsama'], 'uyum', r['yuzde_uyum'], 'kappa', r['kappa'], 'bayrak', len(bay))
    print('   K2', r['k2_siklik']); print('   K1', r['k1_siklik'])
atm2 = Counter(x for t, x in tum2 if t == 'ATM'); mro2 = Counter(x for t, x in tum2 if t == 'MRO')
sonuc['atm_hic_gorulmeyen_eklenen'] = [s for s in EKLENEN_ATM if atm2[s] == 0]
sonuc['atm_hic_gorulmeyen_klasik'] = [s for s in KLASIK_ATM if atm2[s] == 0]
sonuc['mro_hic_gorulmeyen'] = [s for s in MRO_SINIF if mro2[s] == 0]
po, kp = kappa([f'{t}:{x}' for t, x in tum1], [f'{t}:{x}' for t, x in tum2])
sonuc['toplam'] = {'n': len(tum1), 'yuzde_uyum': round(po, 4), 'kappa': round(kp, 4)}
print('toplam', sonuc['toplam']); print('ATM gorulmeyen eklenen', sonuc['atm_hic_gorulmeyen_eklenen']); print('ATM gorulmeyen klasik', sonuc['atm_hic_gorulmeyen_klasik'])
(H/'e15_sonuc.json').write_text(json.dumps(sonuc, indent=1, ensure_ascii=False))
