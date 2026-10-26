#!/usr/bin/env python3
"""bsp_decompile.py -- CoD2 .d3dbsp (IBSP v4) -> editable iwmap 4 .map (reverse engineering).

Usage:
    python bsp_decompile.py <map.d3dbsp> <out.map> [--no-surfaces] [--surface-mesh] [--max-tris N]

What comes back (format measured on stock maps, see references/reverse-engineering.md):
  * every entity from lump 37: misc_models, lights, path/cover nodes, spawners, triggers,
    vehicles, script_* entities with all keys (export/script_* included)
  * world brushes (model 0) rebuilt from lumps 4 (planes), 5 (brushsides), 6 (brushes):
    the first 6 sides of every brush are axial distances (-x,+x,-y,+y,-z,+z), the rest index planes;
    each side keeps its material (lump 0)
  * brush models (doors, destructibles): lump 35 gives the brush range in LOCAL coordinates;
    they are moved to world space by the entity origin and get an origin brush (pivot)
  * triggers compiled without brushes (only bounds in lump 35) come back as boxes
  * terrain / patch / model-less surfaces (triangle soups, lumps 7/8/9) that do not lie on a brush
    face come back as thin detail prism brushes (top face = triangle, material kept) in func_groups.
    --surface-mesh writes 2x2 meshes instead (one per triangle); cod2map CRASHES on those for a big
    map (SANITY CHECK FAILURE, tris_mergeconcave.cpp:560 -- measured on decoytrenches)
  * texture repeat size per material is estimated from the soups (world units per st unit)
Not recoverable: exact brush texture alignment (offsets/rotation), patch control grids
(they come back as triangles), compile-only entities removed by cod2map.
"""
import sys
import struct
import re
import math
from collections import defaultdict, Counter

LM = 'lightmap_gray 16384 16384 0 0 0 0'


class BSP:
    def __init__(self, path):
        self.d = open(path, 'rb').read()
        assert self.d[:4] == b'IBSP', 'not an IBSP file'
        self.ver = struct.unpack('<i', self.d[4:8])[0]
        assert self.ver == 4, 'CoD2 d3dbsp version 4 expected, got %d' % self.ver

    def lump(self, i):
        s, o = struct.unpack('<ii', self.d[8 + i * 8:16 + i * 8])
        return self.d[o:o + s]

    def recs(self, i, fmt):
        b = self.lump(i)
        n = struct.calcsize(fmt)
        return [struct.unpack(fmt, b[k:k + n]) for k in range(0, len(b) - n + 1, n)]


def parse_entities(txt):
    ents = []
    for blk in re.findall(r'\{([^{}]*)\}', txt):
        ents.append(dict(re.findall(r'"([^"]*)" "([^"]*)"', blk)))
    return ents


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a):
    L = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / L, a[1] / L, a[2] / L)


def _fmt(v):
    r = round(v, 3)
    if r == int(r):
        return str(int(r))
    return ('%.3f' % r).rstrip('0').rstrip('.')


def brush_planes(bsp, mats, planes, sides, brush, first_side, ofs=(0, 0, 0)):
    """Return [(n, d, material)] with outward normals: inside = n.x <= d."""
    nsides, _bm = brush
    out = []
    for k in range(nsides):
        val, mat = sides[first_side + k]
        mname = mats[mat] if mat < len(mats) else 'caulk'
        if k < 6:
            dist = struct.unpack('<f', struct.pack('<I', val))[0]
            a = k // 2
            n = [0.0, 0.0, 0.0]
            if k % 2 == 0:                    # min side: outward -axis
                n[a] = -1.0
                d = -dist
            else:
                n[a] = 1.0
                d = dist
            n = tuple(n)
        else:
            px, py, pz, pd = planes[val]
            n, d = (px, py, pz), pd
        d += _dot(n, ofs)
        out.append((n, d, mname))
    return out


def corners(pl):
    pts = []
    m = len(pl)
    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                n1, d1, _ = pl[i]; n2, d2, _ = pl[j]; n3, d3, _ = pl[k]
                c23 = _cross(n2, n3)
                det = _dot(n1, c23)
                if abs(det) < 1e-9:
                    continue
                c31 = _cross(n3, n1); c12 = _cross(n1, n2)
                p = tuple((d1 * c23[a] + d2 * c31[a] + d3 * c12[a]) / det for a in range(3))
                if all(_dot(n, p) <= d + 0.05 for (n, d, _) in pl):
                    pts.append(p)
    return pts


def face_line(n, d, mat, scale):
    """Three points on the plane ordered so (b-a)x(c-a) points INTO the brush (= -n)."""
    p0 = (n[0] * d, n[1] * d, n[2] * d)
    t = (0.0, 0.0, 1.0) if abs(n[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = _norm(_cross(n, t))
    v = _norm(_cross(n, u))
    # want u' x v' = -n ; cross(u, v) = cross(u, n x u) = n -> swap
    a = p0
    b = tuple(p0[i] + v[i] * 64 for i in range(3))
    c = tuple(p0[i] + u[i] * 64 for i in range(3))
    g = scale.get(mat, 256)
    f = lambda p: '( %s %s %s )' % tuple(_fmt(x) for x in p)
    return ' %s %s %s %s %s %s 0 0 0 0 %s' % (f(a), f(b), f(c), mat, _fmt(g), _fmt(g), LM)


def dedupe_planes(pl):
    """Stock brushes carry bevel planes that repeat an axial side; cod2map rejects
    'duplicate plane' (measured). Keep the first of every (normal, dist) pair."""
    seen = set()
    out = []
    for (n, d, m) in pl:
        k = (round(n[0], 4), round(n[1], 4), round(n[2], 4), round(d, 2))
        if k in seen:
            continue
        seen.add(k)
        out.append((n, d, m))
    return out


def brush_text(pl, scale, detail=False):
    pl = dedupe_planes(pl)
    if len(corners(pl)) < 4:
        return None
    return ' {\n' + ('  contents detail;\n' if detail else '') + \
        '\n'.join(face_line(n, d, m, scale) for (n, d, m) in pl) + '\n }'


def prism_planes(a, b, c, mat, depth=8.0):
    """Triangle -> thin convex prism: top face = the triangle (material), sides/bottom caulk.
    Side planes are VERTICAL through each edge and the bottom is horizontal, snapped to 8 units, so
    neighbouring prisms share planes (MAX_MAP_PLANES was hit with per-triangle planes, measured)."""
    a, b, c = a[:3], b[:3], c[:3]
    n = _norm(_cross(tuple(b[i] - a[i] for i in range(3)), tuple(c[i] - a[i] for i in range(3))))
    if n[2] < 0:
        n = (-n[0], -n[1], -n[2])
    if n[2] < 0.15:                       # near-vertical (trench walls): extrude along the face normal
        top = (n, _dot(n, a), mat)
        bot = ((-n[0], -n[1], -n[2]), -(_dot(n, a) - depth), 'caulk')
        cen = tuple((a[i] + b[i] + c[i]) / 3.0 for i in range(3))
        pl = [top, bot]
        for (p, q) in ((a, b), (b, c), (c, a)):
            e = tuple(q[i] - p[i] for i in range(3))
            sn = _norm(_cross(e, n))
            if _dot(sn, tuple(cen[i] - p[i] for i in range(3))) > 0:
                sn = (-sn[0], -sn[1], -sn[2])
            pl.append((sn, _dot(sn, p), 'caulk'))
        return pl
    top = (n, _dot(n, a), mat)
    zb = math.floor((min(a[2], b[2], c[2]) - depth) / 8.0) * 8.0
    bot = ((0.0, 0.0, -1.0), -zb, 'caulk')
    cen = tuple((a[i] + b[i] + c[i]) / 3.0 for i in range(3))
    pl = [top, bot]
    for (p, q) in ((a, b), (b, c), (c, a)):
        e = (q[0] - p[0], q[1] - p[1], 0.0)
        if abs(e[0]) + abs(e[1]) < 1e-6:
            return None
        sn = _norm((e[1], -e[0], 0.0))
        if _dot(sn, tuple(cen[i] - p[i] for i in range(3))) > 0:
            sn = (-sn[0], -sn[1], 0.0)
        pl.append((sn, _dot(sn, p), 'caulk'))
    return pl


def pair_quads(tris):
    """Pair triangles that share an edge into quads (a, b, d, c) -> non-degenerate 2x2 meshes,
    the same shape the stock terrain uses. Returns (quads, leftover triangles)."""
    key = lambda p: (round(p[0], 1), round(p[1], 1), round(p[2], 1))
    edge = {}
    for i, t in enumerate(tris):
        for e in ((0, 1), (1, 2), (2, 0)):
            k = tuple(sorted((key(t[e[0]]), key(t[e[1]]))))
            edge.setdefault(k, []).append((i, e))
    used = set()
    quads = []
    for k, lst in edge.items():
        if len(lst) != 2:
            continue
        (i, ei), (j, ej) = lst
        if i in used or j in used:
            continue
        ti, tj = tris[i], tris[j]
        other_i = ti[3 - ei[0] - ei[1]]
        other_j = tj[3 - ej[0] - ej[1]]
        p, q = ti[ei[0]], ti[ei[1]]
        quads.append(((other_i, p), (q, other_j)))      # rows of a 2x2 mesh
        used.add(i)
        used.add(j)
    left = [t for i, t in enumerate(tris) if i not in used]
    return quads, left


def box_planes(mn, mx, mat):
    return [((-1, 0, 0), -mn[0], mat), ((1, 0, 0), mx[0], mat), ((0, -1, 0), -mn[1], mat),
            ((0, 1, 0), mx[1], mat), ((0, 0, -1), -mn[2], mat), ((0, 0, 1), mx[2], mat)]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    src, dst = sys.argv[1], sys.argv[2]
    surfaces = '--no-surfaces' not in sys.argv
    max_tris = int(sys.argv[sys.argv.index('--max-tris') + 1]) if '--max-tris' in sys.argv else 400000
    bsp = BSP(src)
    mats = [r[0].split(b'\0')[0].decode('latin-1') for r in bsp.recs(0, '<64sII')]
    mat_cont = [r[2] for r in bsp.recs(0, '<64sII')]     # contents flags (0x1 solid, 0x08000000 detail)
    planes = bsp.recs(4, '<4f')
    sides = bsp.recs(5, '<II')
    brushes = bsp.recs(6, '<HH')
    first = []
    acc = 0
    for b in brushes:
        first.append(acc)
        acc += b[0]
    assert acc == len(sides), ('brush side count mismatch', acc, len(sides))
    models = bsp.recs(35, '<6f6I')
    soups = bsp.recs(7, '<HHIHHI')
    vb = bsp.lump(8)
    verts = [struct.unpack('<3f', vb[k:k + 12]) + struct.unpack('<2f', vb[k + 28:k + 36])
             for k in range(0, len(vb) - 67, 68)]
    ib = bsp.lump(9)
    idx = struct.unpack('<%dH' % (len(ib) // 2), ib[:len(ib) // 2 * 2])
    ents = parse_entities(bsp.lump(37).decode('latin-1'))

    # texture repeat size per material from soups (world units per 1.0 st)
    olc = defaultdict(list)
    for (m, _lm, fv, vc, ic, fi) in soups:
        for t in range(0, min(ic, 60), 3):
            a, b = verts[fv + idx[fi + t]], verts[fv + idx[fi + t + 1]]
            dw = math.dist(a[:3], b[:3])
            ds = math.hypot(a[3] - b[3], a[4] - b[4])
            if ds > 1e-4 and dw > 1:
                olc[mats[m]].append(dw / ds)
    scale = {}
    for m, L in olc.items():
        L.sort()
        scale[m] = max(8, min(4096, round(L[len(L) // 2] / 8) * 8))

    out = ['iwmap 4']
    rep = Counter()

    # --region x0 y0 x1 y1 : keep only geometry/entities whose centre lies inside
    # --prefab             : write a placeable prefab: no sky hull, only visual entities
    #                        (misc_model, light, misc_prefab), origin moved to the region centre / floor
    region = None
    if '--region' in sys.argv:
        k = sys.argv.index('--region')
        region = tuple(float(v) for v in sys.argv[k + 1:k + 5])
    prefab = '--prefab' in sys.argv

    def inreg(p):
        return region is None or (region[0] <= p[0] <= region[2] and region[1] <= p[1] <= region[3])

    shift = (0.0, 0.0, 0.0)
    if region:
        cx, cy = (region[0] + region[2]) / 2.0, (region[1] + region[3]) / 2.0
        zs = []
        for (m, _lm, fv, vc, ic, fi) in soups[models[0][6]:models[0][6] + models[0][7]]:
            for t in range(0, ic, 3):
                a, b, c = (verts[fv + idx[fi + t + kk]] for kk in range(3))
                n = _cross(tuple(b[i] - a[i] for i in range(3)), tuple(c[i] - a[i] for i in range(3)))
                L = math.sqrt(_dot(n, n)) or 1
                cen = tuple((a[i] + b[i] + c[i]) / 3.0 for i in range(3))
                if abs(n[2] / L) > 0.9 and inreg(cen):
                    zs.append(cen[2])
        zs.sort()
        zref = zs[len(zs) // 10] if zs else 0.0          # low ground of the region = prefab floor
        if prefab:
            shift = (-cx, -cy, -zref)
        rep['region ground z (prefab floor)'] = int(zref)

    # world brush plane keys (to skip soups that are brush faces)
    face_keys = set()
    w = models[0]
    wb0, wbn = w[10], w[11]

    # visible face material per plane, from the draw triangles. A compiled brush side only keeps
    # the brush's CONTENTS material on every side; hidden sides were caulk in the source. Writing
    # the contents material on all sides makes thousands of overlapping coplanar visible faces and
    # cod2map dies in tris_mergeconcave.cpp:560 (SANITY CHECK FAILURE) -- measured on decoytrenches.
    TOOL = ('clip', 'sky', 'portal', 'nodraw', 'mantle', 'trigger', 'caulk', 'origin', 'hint', 'ladder')
    gor = {}
    for (m, _lm, fv, vc, ic, fi) in soups:
        mn = mats[m]
        for t in range(0, ic, 3):
            a, b, c = (verts[fv + idx[fi + t + k]] for k in range(3))
            n = _cross(tuple(b[i] - a[i] for i in range(3)), tuple(c[i] - a[i] for i in range(3)))
            if _dot(n, n) < 1e-6:
                continue
            n = _norm(n)
            d = _dot(n, a[:3])
            for s in (1, -1):
                gor.setdefault((round(s * n[0], 2), round(s * n[1], 2), round(s * n[2], 2), round(s * d)), mn)

    def gorunur_malzeme(pl):
        out = []
        for (n, d, m) in pl:
            if m.startswith(TOOL):
                out.append((n, d, m))
                continue
            k = (round(n[0], 2), round(n[1], 2), round(n[2], 2), round(d))
            out.append((n, d, gor.get(k, 'caulk')))
        return out

    def bplanes(bi, ofs=(0, 0, 0)):
        pl = brush_planes(bsp, mats, planes, sides, brushes[bi], first[bi], (0, 0, 0))
        pl = gorunur_malzeme(pl)
        return [(n, d + _dot(n, ofs), m) for (n, d, m) in pl]

    world_txt = []
    VOLUME = ('trigger', 'aitrig', 'mine', 'spawner_trigger', 'kill', 'stopspawn', 'escort', 'goal_volume', 'ambient')
    for bi in range(wb0, wb0 + wbn):
        bm = brushes[bi][1]
        bname = mats[bm] if bm < len(mats) else ''
        if bname.startswith(VOLUME):
            # trigger volumes sit in the model-0 brush range of a compiled map; written into
            # worldspawn they become SOLID walls (measured: 109 'trigger' + 26 'mine' on decoytrenches)
            rep['trigger-volume brushes kept out of world'] += 1
            continue
        pl = bplanes(bi)
        for (n, d, _m) in pl:
            face_keys.add((round(n[0], 2), round(n[1], 2), round(n[2], 2), round(d)))
        if region:
            cs = corners(dedupe_planes(pl))
            if not cs or not inreg(tuple(sum(p[a] for p in cs) / len(cs) for a in range(3))):
                continue
            pl = [(n, d + _dot(n, shift), m) for (n, d, m) in pl]
        t = brush_text(pl, scale, detail=bool(mat_cont[bm] & 0x08000000) if bm < len(mat_cont) else False)
        if t:
            world_txt.append(t)
            rep['world brushes'] += 1
        else:
            rep['degenerate brushes skipped'] += 1

    # SEALING HULL: sky brushes are non-solid (contents 0x800) and are NOT in the collision brush
    # lump, so a decompiled map is open. With any entity present cod2map then floods the outside and
    # crashes (tris_mergeconcave.cpp:560) -- measured. Rebuild a 6-brush sky box around the model-0
    # bounds with the map's own sky material.
    sky = next((m for m in mats if m.startswith('sky')), 'sky_libya')
    mn = [w[a] - 1024 for a in range(3)]
    mx = [w[3 + a] + 1024 for a in range(3)]
    T = 64
    for a in (range(3) if not prefab else ()):
        for side in (0, 1):
            lo, hi = list(mn), list(mx)
            if side == 0:
                hi[a] = mn[a]; lo[a] = mn[a] - T
            else:
                lo[a] = mx[a]; hi[a] = mx[a] + T
            pl = box_planes(tuple(lo), tuple(hi), 'caulk')
            # inward-facing side gets the sky
            k = a * 2 + (1 if side == 0 else 0)
            n, d, _m = pl[k]
            pl[k] = (n, d, sky)
            world_txt.append(brush_text(pl, scale))
    if not prefab:
        rep['sky hull brushes (%s)' % sky] += 6

    # entities
    GORSEL = ('misc_model', 'light', 'misc_prefab')
    for ei, e in enumerate(ents):
        cls = e.get('classname', '')
        body = []
        model = e.get('model', '')
        if cls != 'worldspawn' and region:
            o = e.get('origin')
            if not o or not inreg(tuple(float(x) for x in o.split())):
                continue
            if prefab and cls not in GORSEL:
                continue
            if prefab:
                p = [float(x) for x in o.split()]
                e = dict(e)
                e['origin'] = ' '.join(_fmt(p[a] + shift[a]) for a in range(3))
        if cls == 'worldspawn':
            body = world_txt
            if prefab:
                e = {'classname': 'worldspawn'}
        elif model.startswith('*'):
            mi = int(model[1:])
            if mi < len(models):
                mm = models[mi]
                o = tuple(float(x) for x in e.get('origin', '0 0 0').split())
                b0, bn = mm[10], mm[11]
                for bi in range(b0, b0 + bn):
                    t = brush_text(bplanes(bi, o), scale)
                    if t:
                        body.append(t)
                if bn == 0:          # trigger compiled to bounds only
                    mn = tuple(mm[a] + o[a] for a in range(3))
                    mx = tuple(mm[3 + a] + o[a] for a in range(3))
                    if all(mx[a] - mn[a] > 0.5 for a in range(3)):
                        body.append(brush_text(box_planes(mn, mx, 'trigger'), scale))
                        rep['trigger boxes from bounds'] += 1
                if bn and cls.startswith('script_brushmodel') or (bn and 'origin' in e):
                    body.append(brush_text(box_planes(tuple(v - 4 for v in o), tuple(v + 4 for v in o), 'origin'), scale))
                rep['brush model entities'] += 1
        kv = {k: v for k, v in e.items() if not (k == 'model' and v.startswith('*'))}
        out.append('// entity %d' % ei)
        out.append('{')
        for k, v in kv.items():
            out.append('"%s" "%s"' % (k, v))
        for bt in body:
            if bt:
                out.append(bt)
        out.append('}')
        rep['entities'] += 1

    # surfaces of model 0 that are not brush faces -> 2x2 meshes
    if surfaces:
        s0, sn = w[6], w[7]
        groups = defaultdict(list)
        ntri = 0
        for si in range(s0, s0 + sn):
            m, _lm, fv, vc, ic, fi = soups[si]
            mname = mats[m]
            if mname.startswith(('caulk', 'clip', 'portal', 'nodraw', 'sky')):
                continue
            for t in range(0, ic, 3):
                a, b, c = (verts[fv + idx[fi + t + k]] for k in range(3))
                n = _cross(tuple(b[i] - a[i] for i in range(3)), tuple(c[i] - a[i] for i in range(3)))
                if _dot(n, n) < 1e-6:
                    continue
                n = _norm(n)
                d = _dot(n, a[:3])
                if (round(n[0], 2), round(n[1], 2), round(n[2], 2), round(d)) in face_keys or \
                   (round(-n[0], 2), round(-n[1], 2), round(-n[2], 2), round(-d)) in face_keys:
                    continue
                if region:
                    if not inreg(tuple((a[i] + b[i] + c[i]) / 3.0 for i in range(2))):
                        continue
                    a, b, c = (tuple(v[i] + shift[i] for i in range(3)) + tuple(v[3:]) for v in (a, b, c))
                groups[mname].append((a, b, c))
                ntri += 1
                if ntri >= max_tris:
                    break
        mesh_mode = '--surface-mesh' in sys.argv          # legacy: one degenerate 2x2 per triangle
        prism_only = '--surface-prism' in sys.argv
        for mname, tris in groups.items():
            out.append('// entity surfaces %s' % mname)
            out.append('{')
            out.append('"classname" "func_group"')
            g = scale.get(mname, 256)
            if mesh_mode:
                quad_rows = [((a, b), (c, c)) for (a, b, c) in tris]
                left = []
            elif prism_only:
                quad_rows, left = [], tris
            else:
                quad_rows, left = pair_quads(tris)
            for (a, b, c) in left:
                pp = prism_planes(a, b, c, mname)
                # structural by default: the terrain seals the map; detail prisms leave it open and the
                # leak flood then crashes cod2map (tris_mergeconcave, measured)
                t = brush_text(pp, scale, detail='--surface-detail' in sys.argv) if pp else None
                if t:
                    out.append(t)
                    rep['surface prisms'] += 1
                else:
                    rep['surface triangles dropped (vertical/degenerate)'] += 1
            for rows in quad_rows:
                (r00, r01), (r10, r11) = rows
                A = tuple(r10[i] - r00[i] for i in range(3))
                B = tuple(r01[i] - r00[i] for i in range(3))
                if _cross(A, B)[2] < 0:                   # stock rule: row dir x in-row dir = +z (faces up)
                    rows = ((r00, r10), (r01, r11))
                rep['surface quad meshes'] += 1
                txt = [' {', '  mesh', '  {', '   ' + mname, '   lightmap_gray', '   2 2 0 1']
                for r in rows:
                    txt.append('   (')
                    for p in r:
                        txt.append('\tv %s %s %s t %s %s %s %s' % (
                            _fmt(p[0]), _fmt(p[1]), _fmt(p[2]), _fmt(p[3] * g * 8), _fmt(p[4] * g * 8),
                            _fmt(p[0] / 8.0), _fmt(-p[1] / 8.0)))
                    txt.append('   )')
                txt += ['  }', ' }']
                out.append('\n'.join(txt))
            out.append('}')
    with open(dst, 'w', encoding='latin-1', newline='\r\n') as f:
        f.write('\n'.join(out) + '\n')
    if '--report' in sys.argv or True:
        print('materials %d  planes %d  brushes %d  models %d  soups %d  verts %d' % (
            len(mats), len(planes), len(brushes), len(models), len(soups), len(verts)))
        for k, v in rep.items():
            print('  %-28s %d' % (k, v))
    return 0


if __name__ == '__main__':
    sys.exit(main())
