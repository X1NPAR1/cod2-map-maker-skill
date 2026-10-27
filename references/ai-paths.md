# AI path network

## Lump 38 (paths) decoding
The `.d3dbsp` header is `IBSP` + version, followed by a lump table of (offset, length) pairs.
Lump 37 holds the entity text and lump 38 the path data:
```
int32  unknown (8)
uint16 nodeCount
repeat nodeCount:
    uint16 linkCount
    repeat linkCount: uint16 targetNode, float32 dist
```
Nodes are numbered in the order their entities appear in the bsp entity lump.

## Reachability audit (Python)
```python
import struct, collections, sys
d = open(sys.argv[1], 'rb').read()
def lump(i):
    off, ln = struct.unpack_from('<ii', d, 8 + i * 8)   # check the table layout on your bsp first
    return d[off:off + ln]
p = lump(38); n = struct.unpack_from('<H', p, 4)[0]; o = 6; links = []
for _ in range(n):
    c = struct.unpack_from('<H', p, o)[0]; o += 2
    links.append([struct.unpack_from('<Hf', p, o + 6 * k)[0] for k in range(c)]); o += 6 * c
seen = {0}; q = collections.deque([0])
while q:
    a = q.popleft()
    for b in links[a]:
        if b not in seen: seen.add(b); q.append(b)
print(n, 'nodes', n - len(seen), 'unreachable')
```
- Also look for one-way links (a→b with no b→a). A one-way link marks a step that AI can go down but not up.
- For each unreachable node, print its origin from lump 37 and inspect that spot in game.

## Rules
- **Node height:** put node z on the floor triangle surface, computed from the mesh rather than a constant.
- **Steps:** the engine makes no uphill link across a step of 16 units or more. Put an invisible ramp through the step noses made of `clip_ai` (AI-only solid). Do NOT use caulk: caulk is structural and deletes every step face inside it, so the stairs render as a void. Leave ~80u of floor in front of the first step for a front entry node.
- **Clip brushes:** `clip` and `clip_player` do not count as walkable floor for AI, and they block links at connectpaths time.
- **Player-only walls:** compile them 2000 units higher, then lower them at runtime with `moveZ`.
- **Doors:** keep them open or raised during connectpaths and close them at runtime.
- **Node spacing:** 96–192 units for cover and path nodes, denser inside buildings. A doorway needs a node on each side.
- **Window cover:** use `node_cover_crouch_window` or stand nodes 20–30 units from the wall, facing out.
- **Water:** AI avoid deep water. Give bridges their own nodes, and route intermediate goals across the bridges.

## Lessons from 'burya' (measured with the lump-38 audit)
- **Terrain MESH -> brush floor step = ONE-WAY door.** Measured on a test map (same 52x76-door
  room each time): brush ground + 16u floor -> two-way; MESH ground + 16u floor -> links out
  only ("can leave, cannot enter"); any ground + 4u floor -> one-way. Script_models, triggers,
  lights, detail brushes, window frames, interior walls and a brushmodel ceiling made no
  difference. Fix: give every enterable building a BRUSH apron/porch (or a brush ramp) between
  the terrain mesh and the door, and use a 16u floor. When a cause is unclear, build a tiny
  test map with one variable per room (`scripts/path_experiment_map.py`) -- it compiles in
  seconds and ends the guessing.
- Brushmodels placed over a building at +2000 were suspected first and were NOT the cause, but
  keeping destroyable brushmodels away from the playable area at compile time (shift them
  horizontally, move them into place at runtime) is still the safest pattern.
- **One-way into an area = only a drop leads there.** Print one-way edges from the reachable
  set to find it (e.g. the only way into a camp yard was jumping off a tower stair ramp).
- **Props make walls.** Two sandbags just inside a gate plus two watchtower stairs sealed the
  whole camp. A static truck, barrels or a sandbag in a 100-300u corridor between buildings
  can isolate a region. Keep corridors >= 150u clear.
- **The 150u grid misses narrow corridors.** Add a dense (75u) grid inside built-up areas.
- **Stairs must not run toward other buildings.** Run tower stairs along the fence; leave the
  space under a raised platform walkable (only legs as obstacles).
- **Bridge ends:** set road z near the river to the deck height, or a 30-50u step splits the map.
- **Visible stair steps above the caulk ramp** block the ramp; set each step top = ramp height at
  its back edge - 1 so steps stay under the ramp surface.
