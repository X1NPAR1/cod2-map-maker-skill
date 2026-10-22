# -*- coding: utf-8 -*-
"""deney_yol.py -- yol agi deney haritasi 'kr_deney': her odada tek fark.
Amac: merkez binada disaridan iceri bag kurulmamasinin sebebini olcmek."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kmap import Harita
KOK = r'F:\Activision\Call of Duty 2'
H = Harita()
H.ws.update({'ambient': '.5', 'sunlight': '1', 'sundirection': '-45 45 0', 'suncolor': '1 1 1'})
H.oda_kabugu(-4096, -2048, -64, 4096, 2048, 1024, 16, 'caulk', 'sky_tankhunt', 'sky_tankhunt')
H.kutu(-4096, -2048, -64, 4096, 2048, 0, 'stalingradwinter_snow01')
W = 'stalingradwinter_brickwallsnow01'
def oda(cx, taban=4, kasa=False, rampa=False):
    x0, y0, x1, y1 = cx - 300, 0, cx + 300, 400
    H.kutu(x0, y0, 0, x1, y1, taban, 'stalingradwinter_wood_floor', W)
    z0 = taban
    # guney duvari kapili (52x76)
    H.kutu(x0, y0, z0, cx - 26, y0 + 16, z0 + 140, W)
    H.kutu(cx + 26, y0, z0, x1, y0 + 16, z0 + 140, W)
    H.kutu(cx - 26, y0, z0 + 76, cx + 26, y0 + 16, z0 + 140, W)
    H.kutu(x0, y1 - 16, z0, x1, y1, z0 + 140, W)
    H.kutu(x0, y0 + 16, z0, x0 + 16, y1 - 16, z0 + 140, W)
    H.kutu(x1 - 16, y0 + 16, z0, x1, y1 - 16, z0 + 140, W)
    H.kutu(x0, y0, z0 + 140, x1, y1, z0 + 156, W)
    if kasa:                                   # pencere: dogu duvarinda delik + arti kasa
        pass
    if rampa:
        H.kama(cx + 150, 150, cx + 230, 380, z0, z0 + 1, z0 + 100, '+y', 'caulk', 'caulk', alt='caulk', detay=True)
    for (x, y) in ((cx, -120), (cx, -40), (cx, 60), (cx, 150), (cx - 150, 200), (cx + 150, 200), (cx, 300)):
        z = (taban if y > 0 else 0) + 8
        H.ent('node_pathnode', origin=(x, y, z))
    return cx
T = 16
def pen_kasa(cx, y0):
    # guney duvarinda kapinin yaninda pencere (46..88) + arti kasa (detail)
    H.kutu(cx + 100, y0 + 6, T + 46, cx + 152, y0 + 10, T + 88, 'caulk')  # yer tutucu (delik yok: kasa yalniz)
oda(-3000, T)                                                    # 0: kontrol
# 1: buyuk oda (1000x640)
def buyuk(cx):
    x0, y0, x1, y1 = cx - 500, 0, cx + 500, 640
    H.kutu(x0, y0, 0, x1, y1, T, 'stalingradwinter_wood_floor', W)
    H.kutu(x0, y0, T, cx - 26, y0 + 16, T + 140, W); H.kutu(cx + 26, y0, T, x1, y0 + 16, T + 140, W)
    H.kutu(cx - 26, y0, T + 76, cx + 26, y0 + 16, T + 140, W)
    H.kutu(x0, y1 - 16, T, x1, y1, T + 140, W); H.kutu(x0, 16, T, x0 + 16, y1 - 16, T + 140, W)
    H.kutu(x1 - 16, 16, T, x1, y1 - 16, T + 140, W); H.kutu(x0, y0, T + 140, x1, y1, T + 156, W)
    for (x, y) in ((cx, -120), (cx, -40), (cx, 60), (cx, 200), (cx - 300, 300), (cx + 300, 300), (cx, 500)):
        H.ent('node_pathnode', origin=(x, y, (T if y > 0 else 0) + 8))
buyuk(-1700)
c = oda(-300, T)                                                 # 2: arti kasali pencere (gercek delik)
H.kutu(c + 100, 0, T + 46, c + 152, 16, T + 88, 'trigger')        # (delik yerine bos: asagida kasa)
for (a, b_, z0, z1) in ((c + 124.5, c + 127.5, T + 46, T + 88), (c + 100, c + 152, T + 65.5, T + 68.5)):
    H.kutu(a, 6, z0, b_, 10, z1, 'stalingradwinter_wood_trim', detay=True)
c = oda(800, T)                                                  # 3: ic ara duvar (52'lik kapi)
H.kutu(c - 284, 196, T, c - 26, 208, T + 140, W); H.kutu(c + 26, 196, T, c + 284, 208, T + 140, W)
H.kutu(c - 26, 196, T + 76, c + 26, 208, T + 140, W)
# 4: dis zemin MESH (oda cevresi mesh yama, brush zemin ustunde 2 birim)
c = oda(2200, T)
H.mesh([[(x, y, 2) for y in range(-600, 601, 150)] for x in range(c - 600, c + 601, 150)], 'stalingradwinter_snow01')
# disarida baglayici dugum hatti
for x in range(-3600, 3601, 150):
    H.ent('node_pathnode', origin=(x, -250, 10 if 1500 < x < 2900 else 8))
H.ent('info_player_start', origin=(-3500, -500, 8), angles=(0, 90, 0))
r = H.yaz(os.path.join(KOK, 'map_source', 'kr_deney.map'))
print(r['dunya_brush'], r['entity'])
