#!/usr/bin/env python3
"""prefab_catalog.py -- measure every stock CoD2 prefab (map_source/prefabs/**.map).

Usage:
    python prefab_catalog.py "<CoD2>/map_source" out.md [out.json]

For each prefab (nested misc_prefab resolved with origin + yaw) it measures:
  * real bounds from brush corners, patches and nested prefabs (misc_model origins included)
  * floor z relative to the prefab origin (min z) and height
  * opening faces: on which side (+x, -x, +y, -y) the door / window / portal geometry sits
    -> "front" = side with the most door material faces at the bounding-box edge
  * brush count, patch count, top materials, misc_models and nested prefabs
Theme/nation grouping follows the folder (newvillers/corevillers = US/Normandy,
eldaba/matmata/libyatown/toujane/mp_matmata = British/North Africa, rhine = late-war Europe).
"""
import os
import sys
import json
import math
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from map_inspect import parse_map, brush_vertices  # noqa: E402

TEMA = {
    'newvillers': 'US / Normandy (Villers-Bocage)', 'corevillers': 'US / Normandy (Villers-Bocage core)',
    'eldaba': 'British / Egypt (El Daba)', 'matmata': 'British / Tunisia (Matmata)',
    'mp_matmata': 'British / Tunisia (MP Matmata)', 'libyatown': 'British / Libya (town kit)',
    'toujane': 'British / Tunisia (Toujane)', 'rhine': 'US / Germany (Rhine)',
    'interactable_objects': 'Generic props', 'lamps': 'Generic lights', 'traverse': 'AI traverse helpers',
    'MP': 'Multiplayer objective kits',
}
DOOR = ('door',)
WINDOW = ('window', 'shutter')


def _rot(p, yaw):
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c, p[2])


class Olcum:
    def __init__(self):
        self.pts = []
        self.brushes = 0
        self.patches = 0
        self.mats = Counter()
        self.models = Counter()
        self.prefabs = Counter()
        self.acik = []          # (kind, point) door/window/portal face centres
        self.eksik = []


def olc(root, rel, ol, ofs=(0, 0, 0), yaw=0.0, derinlik=0):
    path = os.path.join(root, rel.replace('/', os.sep))
    if not os.path.exists(path):
        ol.eksik.append(rel)
        return
    if derinlik > 6:
        return
    for e in parse_map(path):
        kv = e['kv']
        cls = kv.get('classname', '')
        for br in e['brushes']:
            vs = brush_vertices(br)
            if not vs:
                continue
            mats = set(p[3] for p in br['planes'])
            tool = all(m.startswith(('clip', 'portal', 'caulk', 'nodraw', 'mantle', 'trigger', 'ai', 'origin'))
                       for m in mats)
            wp = [tuple(a + b for a, b in zip(_rot(v, yaw), ofs)) for v in vs]
            if not tool:
                ol.pts.extend(wp)
            ol.brushes += 1
            for m in mats:
                ol.mats[m] += 1
            cx = tuple(sum(v[a] for v in wp) / len(wp) for a in range(3))
            low = ' '.join(mats).lower()
            if any(k in low for k in DOOR):
                ol.acik.append(('door', cx))
            elif any(k in low for k in WINDOW):
                ol.acik.append(('window', cx))
            elif 'portal' in mats:
                ol.acik.append(('portal', cx))
        for p in e['patches']:
            ol.patches += 1
            ol.mats[p['material']] += 1
            ol.pts.extend(tuple(a + b for a, b in zip(_rot(v, yaw), ofs)) for v in p['verts'])
        if cls == 'misc_model':
            ol.models[kv.get('model', '?')] += 1
            o = kv.get('origin')
            if o:
                v = tuple(float(x) for x in o.split())
                ol.pts.append(tuple(a + b for a, b in zip(_rot(v, yaw), ofs)))
        elif cls == 'misc_prefab':
            sub = kv.get('model', '')
            ol.prefabs[sub] += 1
            o = tuple(float(x) for x in kv.get('origin', '0 0 0').split())
            a = kv.get('angles', '0 0 0').split()
            sy = float(a[1]) if len(a) > 1 else 0.0
            no = tuple(x + y for x, y in zip(_rot(o, yaw), ofs))
            olc(root, sub, ol, no, yaw + sy, derinlik + 1)


def taraf(ol, bb):
    """Count door/window/portal centres lying near each bounding-box side."""
    (x0, y0, z0, x1, y1, z1) = bb
    tol_x = max(24.0, (x1 - x0) * 0.12)
    tol_y = max(24.0, (y1 - y0) * 0.12)
    say = {'+x': Counter(), '-x': Counter(), '+y': Counter(), '-y': Counter()}
    for kind, (x, y, z) in ol.acik:
        if x >= x1 - tol_x: say['+x'][kind] += 1
        if x <= x0 + tol_x: say['-x'][kind] += 1
        if y >= y1 - tol_y: say['+y'][kind] += 1
        if y <= y0 + tol_y: say['-y'][kind] += 1
    return say


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    root = sys.argv[1]
    out_md = sys.argv[2]
    out_js = sys.argv[3] if len(sys.argv) > 3 else None
    pre = os.path.join(root, 'prefabs')
    kayit = []
    for dp, _dn, fn in os.walk(pre):
        for f in sorted(fn):
            if not f.lower().endswith('.map'):
                continue
            rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/')
            ol = Olcum()
            try:
                olc(root, rel, ol)
            except Exception as ex:          # never stop the whole catalogue on one file
                kayit.append({'path': rel, 'error': str(ex)})
                continue
            if ol.pts:
                xs, ys, zs = zip(*ol.pts)
                bb = (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
            else:
                bb = (0, 0, 0, 0, 0, 0)
            sd = taraf(ol, bb)
            puan = {k: v['door'] * 3 + v['portal'] + v['window'] for k, v in sd.items()}
            on = max(puan, key=puan.get) if any(puan.values()) else '-'
            kayit.append({
                'path': rel, 'theme': rel.split('/')[1] if rel.count('/') > 1 else 'root',
                'bounds': [round(v, 1) for v in bb],
                'size': [round(bb[3] - bb[0]), round(bb[4] - bb[1]), round(bb[5] - bb[2])],
                'floor_z': round(bb[2], 1), 'brushes': ol.brushes, 'patches': ol.patches,
                'front': on, 'sides': {k: dict(v) for k, v in sd.items()},
                'doors': sum(1 for k, _ in ol.acik if k == 'door'),
                'windows': sum(1 for k, _ in ol.acik if k == 'window'),
                'portals': sum(1 for k, _ in ol.acik if k == 'portal'),
                'materials': [m for m, _ in ol.mats.most_common(8)],
                'models': dict(ol.models.most_common(8)), 'prefabs': dict(ol.prefabs),
                'missing': ol.eksik,
            })
    kayit.sort(key=lambda r: r['path'])
    if out_js:
        with open(out_js, 'w') as f:
            json.dump(kayit, f, indent=1)
    satir = ['# Stock prefab catalogue (measured)', '',
             'Generated by `scripts/prefab_catalog.py` from `map_source/prefabs`. Sizes are real brush-corner',
             'bounds in world units (nested prefabs resolved). `floor` = lowest z relative to the prefab origin',
             '(0 = origin sits on the floor). `front` = bounding-box side with the most door faces',
             '(door x3 + portal + window); place the prefab with `yaw` so that side faces the street.',
             '`-` = no openings found (wall pieces, props). `model-only` prefabs just place an xmodel with a fixed',
             'offset/yaw. Prefabs marked **missing nested** reference prefab files that are not shipped -- do not use',
             'them, or the compile drops those parts.', '']
    tema = None
    for r in kayit:
        if 'error' in r:
            continue
        if r['theme'] != tema:
            tema = r['theme']
            satir += ['', '## %s — %s' % (tema, TEMA.get(tema, '')), '',
                      '| prefab | size x/y/z | floor | front | doors/win/portal | brushes | key materials / models |',
                      '|---|---|---|---|---|---|---|']
        ad = r['path'].split('/', 2)[-1]
        if r['missing']:
            ad += ' **(missing nested: %s)**' % ', '.join(sorted(set(m.split('/')[-1] for m in r['missing'])))
        if r['brushes'] == 0 and r['models']:
            satir.append('| `%s` | model-only | - | - | - | 0 | %s |' % (
                ad, ', '.join(m.replace('xmodel/', '') for m in r['models'])))
            continue
        mm = ', '.join(r['materials'][:3])
        if r['models']:
            mm += '; ' + ', '.join(m.replace('xmodel/', '') for m in list(r['models'])[:2])
        if r['prefabs']:
            mm += '; nested: ' + ', '.join(p.split('/')[-1] for p in r['prefabs'])
        satir.append('| `%s` | %d/%d/%d | %g | %s | %d/%d/%d | %d | %s |' % (
            ad, r['size'][0], r['size'][1], r['size'][2], r['floor_z'], r['front'],
            r['doors'], r['windows'], r['portals'], r['brushes'], mm))
    hata = [r for r in kayit if 'error' in r]
    if hata:
        satir += ['', '## Parse errors', ''] + ['- `%s`: %s' % (r['path'], r['error']) for r in hata]
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(satir) + '\n')
    print('prefabs: %d  errors: %d' % (len(kayit) - len(hata), len(hata)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
