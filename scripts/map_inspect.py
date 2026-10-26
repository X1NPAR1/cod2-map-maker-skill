#!/usr/bin/env python3
"""map_inspect.py -- CoD2 iwmap 4 .map parser and statistics.

Usage:
    python map_inspect.py <file.map> [--json out.json]

Reads entities, brushes (planes + materials), meshes/curves (patches) and prints:
classname counts, key usage, material usage per geometry kind, patch sizes,
misc_prefab / misc_model usage, light settings, worldspawn sun/fog keys and
the world bounds. Also importable: parse_map(path) -> list of entities.

Entity dict: {'kv': {key: value}, 'brushes': [Brush], 'patches': [Patch]}
Brush:  {'planes': [((x,y,z),(x,y,z),(x,y,z), material)], 'contents': [...]}
Patch:  {'kind': 'mesh'|'curve', 'material': str, 'rows': R, 'cols': C,
         'verts': [(x,y,z), ...], 'flags': [...]}
"""
import re
import sys
import json
import math
from collections import Counter, defaultdict

_NUM = r'-?[0-9.eE+-]+'
_PLANE = re.compile(r'\(\s*(%s)\s+(%s)\s+(%s)\s*\)\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)\s*(\S+)'
                    % ((_NUM,) * 9))
_VERT = re.compile(r'^\s*v\s+(%s)\s+(%s)\s+(%s)' % (_NUM, _NUM, _NUM))
_KV = re.compile(r'^\s*"([^"]*)"\s+"([^"]*)"\s*$')


def parse_map(path):
    with open(path, encoding='latin-1') as f:
        lines = f.read().replace('\r\n', '\n').split('\n')
    ents = []
    i, n = 0, len(lines)
    depth = 0
    ent = None
    while i < n:
        s = lines[i].strip()
        i += 1
        if not s or s.startswith('//') or s.startswith('iwmap'):
            continue
        if depth == 0:
            if s == '{':
                ent = {'kv': {}, 'brushes': [], 'patches': []}
                depth = 1
            continue
        if depth == 1:
            if s == '}':
                ents.append(ent)
                depth = 0
                continue
            m = _KV.match(s)
            if m:
                ent['kv'][m.group(1)] = m.group(2)
                continue
            if s == '{':
                # brush or patch block
                block = []
                d = 1
                while i < n and d > 0:
                    t = lines[i].strip()
                    i += 1
                    if t == '{':
                        d += 1
                    elif t == '}':
                        d -= 1
                        if d == 0:
                            break
                    block.append(t)
                _parse_block(block, ent)
    return ents


def _parse_block(block, ent):
    if block and block[0] in ('mesh', 'curve'):
        kind = block[0]
        # block: kind, '{'-content flattened (braces removed by depth loop keep inner lines)
        body = [b for b in block[1:] if b not in ('{', '}')]
        j = 0
        flags = []
        while j < len(body) and not body[j][0:1].isalpha() is False and body[j].split()[0] in ('contents', 'smoothing', 'toolFlags'):
            flags.append(body[j])
            j += 1
        # material, lightmap, dims
        rest = [b for b in body if not b.startswith(('contents', 'smoothing', 'toolFlags'))]
        flags = [b for b in body if b.startswith(('contents', 'smoothing', 'toolFlags'))]
        mat = rest[0] if rest else '?'
        dims = rest[2].split() if len(rest) > 2 else ['0', '0']
        verts = []
        for b in rest:
            m = _VERT.match(b)
            if m:
                verts.append(tuple(float(m.group(k)) for k in (1, 2, 3)))
        ent['patches'].append({'kind': kind, 'material': mat, 'rows': int(float(dims[0])),
                               'cols': int(float(dims[1])), 'verts': verts, 'flags': flags})
        return
    planes = []
    contents = []
    for b in block:
        m = _PLANE.match(b)
        if m:
            g = [float(m.group(k)) for k in range(1, 10)]
            planes.append(((g[0], g[1], g[2]), (g[3], g[4], g[5]), (g[6], g[7], g[8]), m.group(10)))
        elif b.startswith('contents'):
            contents.append(b.rstrip(';'))
    if planes:
        ent['brushes'].append({'planes': planes, 'contents': contents})


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def brush_vertices(br):
    """Real corner points of a convex brush: intersect every plane triple and keep the points
    inside all half-spaces. Measured convention (iwmap 4, see map-format.md): for a plane
    (a, b, c), n = (b - a) x (c - a) points INTO the brush."""
    pl = []
    for (a, b, c, _m) in br['planes']:
        n = _cross(_sub(b, a), _sub(c, a))
        L = math.sqrt(_dot(n, n))
        if L < 1e-9:
            continue
        n = (n[0] / L, n[1] / L, n[2] / L)
        pl.append((n, _dot(n, a)))          # inside: n.x >= d
    pts = []
    m = len(pl)
    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                n1, d1 = pl[i]; n2, d2 = pl[j]; n3, d3 = pl[k]
                c23 = _cross(n2, n3)
                det = _dot(n1, c23)
                if abs(det) < 1e-9:
                    continue
                c31 = _cross(n3, n1); c12 = _cross(n1, n2)
                p = tuple((d1 * c23[a] + d2 * c31[a] + d3 * c12[a]) / det for a in range(3))
                if all(_dot(n, p) >= d - 0.05 for (n, d) in pl):
                    pts.append(p)
    return pts


def _brush_bounds(br):
    """Axis-aligned bounds from the real brush corners."""
    pts = brush_vertices(br) or [p for pl in br['planes'] for p in pl[:3]]
    xs, ys, zs = zip(*pts)
    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))


def _vec(o):
    try:
        return tuple(float(v) for v in o.split())
    except Exception:
        return None


def summarize(ents, top=30):
    out = []
    cls = Counter(e['kv'].get('classname', '?') for e in ents)
    out.append('## Entities: %d' % len(ents))
    for c, k in cls.most_common(top):
        out.append('  %6d  %s' % (k, c))
    keys = Counter(k for e in ents for k in e['kv'])
    out.append('\n## Keys (top %d)' % top)
    for c, k in keys.most_common(top):
        out.append('  %6d  %s' % (k, c))

    world = [e for e in ents if e['kv'].get('classname') == 'worldspawn']
    if world:
        out.append('\n## worldspawn keys')
        for k, v in world[0]['kv'].items():
            out.append('  %-22s %s' % (k, v))

    nb = sum(len(e['brushes']) for e in ents)
    npch = sum(len(e['patches']) for e in ents)
    out.append('\n## Geometry: %d brushes, %d patches' % (nb, npch))
    bmat = Counter()
    for e in ents:
        for b in e['brushes']:
            for m in set(p[3] for p in b['planes']):
                bmat[m] += 1
    out.append('\n### Brush materials (brushes using it, top %d)' % top)
    for c, k in bmat.most_common(top):
        out.append('  %6d  %s' % (k, c))
    pmat = Counter()
    psize = Counter()
    for e in ents:
        for p in e['patches']:
            pmat[(p['kind'], p['material'])] += 1
            psize['%s %dx%d' % (p['kind'], p['rows'], p['cols'])] += 1
    out.append('\n### Patch materials (top %d)' % top)
    for (kind, m), k in pmat.most_common(top):
        out.append('  %6d  %-5s %s' % (k, kind, m))
    out.append('\n### Patch sizes (top 15)')
    for c, k in psize.most_common(15):
        out.append('  %6d  %s' % (k, c))

    for cname in ('misc_prefab', 'misc_model'):
        mods = Counter(e['kv'].get('model', '?') for e in ents if e['kv'].get('classname') == cname)
        if mods:
            out.append('\n### %s models (%d distinct, top %d)' % (cname, len(mods), top))
            for c, k in mods.most_common(top):
                out.append('  %6d  %s' % (k, c))
    scales = Counter(e['kv'].get('modelscale', '1') for e in ents if e['kv'].get('classname') == 'misc_model')
    if scales:
        out.append('\n### misc_model modelscale values (top 10)')
        for c, k in scales.most_common(10):
            out.append('  %6d  %s' % (k, c))
    lights = [e['kv'] for e in ents if e['kv'].get('classname') == 'light']
    if lights:
        out.append('\n### Lights: %d' % len(lights))
        for key in ('def', 'radius', 'intensity', 'exponent', 'fov_inner', 'fov_outer', '_color'):
            c = Counter(l.get(key, '-') for l in lights)
            out.append('  %-10s %s' % (key, ', '.join('%s x%d' % (v, k) for v, k in c.most_common(6))))

    # world bounds from brushes + patches
    mins = [1e9] * 3
    maxs = [-1e9] * 3
    for e in ents:
        for b in e['brushes']:
            bb = _brush_bounds(b)
            for a in range(3):
                mins[a] = min(mins[a], bb[a])
                maxs[a] = max(maxs[a], bb[a + 3])
        for p in e['patches']:
            for v in p['verts']:
                for a in range(3):
                    mins[a] = min(mins[a], v[a])
                    maxs[a] = max(maxs[a], v[a])
    if mins[0] < 1e9:
        out.append('\n## Bounds: min %s  max %s  size %s' % (
            tuple(round(v) for v in mins), tuple(round(v) for v in maxs),
            tuple(round(maxs[a] - mins[a]) for a in range(3))))
    return '\n'.join(out)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    ents = parse_map(sys.argv[1])
    print(summarize(ents))
    if '--json' in sys.argv:
        out = sys.argv[sys.argv.index('--json') + 1]
        with open(out, 'w') as f:
            json.dump([{'kv': e['kv'], 'brushes': len(e['brushes']), 'patches': len(e['patches'])} for e in ents], f)
    return 0


if __name__ == '__main__':
    sys.exit(main())
