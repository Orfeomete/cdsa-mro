"""E15 K2 (dil modeli kodlayıcısı) kodları. 11 Ekim 2026.
Kodlayıcı bu oturumdaki yapay zekâ asistanıdır. Kural ön kayıttadır.
Bayrak 'kapsam_ici_sinifsiz' bilgi güvenliği ya da siber-fiziksel boyutu
olduğu hâlde hiçbir sınıfa uymayan olayı işaretler. 'kesik' notu özetin
125 karakterde kesildiğini ve kodun eldeki metne dayandığını gösterir.
"""
D = "kapsam_disi"
GPS = {
 2062181: "gnss_jamming", 2062063: (D, "kapsam_ici_sinifsiz", "nedeni belirsiz GNSS arızası"),
 2058307: "airspace_infringement", 2054512: "gnss_jamming", 2051526: D, 2051513: D, 2049716: D,
 2048762: (D, "kapsam_ici_sinifsiz", "nedeni belirsiz GNSS sinyal kaybı"), 2048490: D,
 2047819: "gnss_jamming", 2047145: D, 2045714: "gnss_jamming", 2045396: "gnss_jamming",
 2044772: (D, "kapsam_ici_sinifsiz", "GPS, FMC ve transponder arıza göstergesi, neden kesik metinde yok"),
 2044462: "gnss_jamming", 2043541: "gnss_jamming", 2043379: "gnss_jamming",
 2042566: "surveillance_data_loss", 2041999: D, 2041905: D,
 2040998: ("gnss_jamming", None, "kasıtsız girişim, inşaat kaynaklı"), 2040807: D,
 2039976: "gnss_jamming", 2038880: D, 2037634: "gnss_jamming", 2037033: "loss_of_separation",
 2036017: D, 2035864: D, 2035443: "gnss_jamming", 2034531: D, 2031003: "surveillance_data_loss",
 2029651: D, 2029379: "gnss_jamming", 2029348: D, 2028563: D, 2027953: "gnss_jamming",
 2027712: "gnss_jamming", 2027708: "gnss_jamming", 2027217: "loss_of_separation", 2026312: D,
 2024697: "gnss_jamming", 2023441: "loss_of_separation", 2022197: D, 2021847: "gnss_jamming",
 2021354: "gnss_jamming", 2020565: D, 2020242: D, 2000093: "gnss_jamming",
 1998026: (D, "kapsam_ici_sinifsiz", "nedeni belirsiz GPS anomalisi"), 1994554: D,
}
CTLR = {
 2105330: "gnss_jamming", 2105322: D, 2103770: "loss_of_separation", 2103769: D, 2103382: D,
 2103375: D, 2103374: "gnss_jamming", 2102100: D, 2100867: "runway_incursion", 2100496: "gnss_jamming",
 2100054: D, 2100051: D, 2100050: (D, None, "kesik, sonlandırılması istenen şey metinde yok"),
 2099557: D, 2098635: D, 2098625: D, 2097564: "loss_of_separation", 2096127: D,
 2095755: "loss_of_separation", 2095449: D, 2095039: D, 2093647: "loss_of_separation", 2093299: D,
 2092994: D, 2092033: D, 2091195: "gnss_jamming", 2091194: D, 2091189: "gnss_jamming",
 2091187: "loss_of_separation", 2091178: D, 2090425: D, 2090112: D, 2089650: "loss_of_separation",
 2089492: D, 2086529: D, 2085583: D, 2085582: "runway_incursion", 2085581: D,
 2084287: "runway_incursion", 2084286: "runway_incursion", 2082692: D, 2082683: D, 2081579: D,
 2081184: D, 2081180: D, 2080752: D, 2080747: D, 2076812: D, 2076185: D, 2076177: D,
}
PLT = {
 2003314: D, 2003270: "runway_incursion", 2002361: "loss_of_separation", 2001577: D, 2001061: D,
 1999417: D, 1996166: D, 1996154: D, 1995544: D, 1994221: D, 1988358: D, 1987530: D, 1987387: D,
 1985949: D, 1984404: D, 1981530: D, 1981001: "loss_of_separation", 1980154: D, 1979141: D,
 1978509: D, 1977785: D, 1977439: D, 1977434: D, 1977107: "loss_of_separation", 1974847: D,
 1970251: D, 1970208: D, 1969944: "tcas_ra", 1969688: D, 1969524: "loss_of_separation", 1967403: D,
 1966386: D, 1964518: "runway_incursion", 1963705: D, 1962880: D, 1961816: "loss_of_separation",
 1958829: D, 1958407: D, 1957805: "loss_of_separation", 1950817: D, 1940351: D, 1938996: D,
 1938052: D, 1937836: D, 1934630: "runway_incursion", 1934572: D, 1933983: "runway_incursion",
 1930863: D, 1928467: "tcas_ra", 1927304: "runway_incursion",
}
MECH = {a: D for a in [
 2069879, 2062965, 2061958, 2061955, 2061581, 2060780, 2059864, 2059860, 2058249, 2058245, 2058239,
 2054307, 2053650, 2053162, 2053161, 2051190, 2050590, 2050589, 2050585, 2047663, 2040780, 2040479,
 2039328, 2038548, 2036377, 2033529, 2033522, 2032488, 2032484, 2030501, 2030003, 2028354, 2028082,
 2028067, 2027475, 2026576, 2024817, 2024499, 2023499, 2023427, 2022066, 2021140, 2020865, 2017583,
 2017070, 2010947, 2008358, 2008352, 2005229, 2000321]}
