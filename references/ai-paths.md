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
- **Steps:** the engine makes no uphill link across a step of 16 units or more. Put an invisible solid caulk ramp under every stair and porch. The visible steps can sit on top as detail.
- **Clip brushes:** `clip` and `clip_player` do not count as walkable floor for AI, and they block links at connectpaths time.
- **Player-only walls:** compile them 2000 units higher, then lower them at runtime with `moveZ`.
- **Doors:** keep them open or raised during connectpaths and close them at runtime.
- **Node spacing:** 96–192 units for cover and path nodes, denser inside buildings. A doorway needs a node on each side.
- **Window cover:** use `node_cover_crouch_window` or stand nodes 20–30 units from the wall, facing out.
- **Water:** AI avoid deep water. Give bridges their own nodes, and route intermediate goals across the bridges.
