# Planning interview (plan mode, before any code)

A CoD2 map is weeks of compile-test iterations. Every requirement found late costs a full 10–15 min
recompile plus a user playtest. So **start every new map in plan mode** and interview the user in
depth before writing a single line.

Rules:
- Use the question tool in batches of up to 4 questions. Offer concrete options with a recommended
  default. Keep asking until every section below has an answer.
- Ask in the user's language.
- Read every sketch, scenario text or reference image the user gives before asking. Ask only what
  they leave open.
- After the interview, write the plan, using the template at the end of this file. Get it approved,
  then code.

## Questions to cover

### 1. Identity and story
- Map name (file name, lowercase, no spaces) and display title.
- Campaign/side: Soviet, British, American, German? Date, location, unit, time of day, weather, season.
- Is it a sequel or prequel to another map? Which map loads before it and after it (`missionSuccess` chain)?
- Intro: fade length, intro text lines, intro music, opening event (plane flyby, artillery, truck ride).
- Ending: speech, gathering, fade length, final music, next level or credits.

### 2. Layout (ask for or confirm a sketch)
- Overall size, and where the start is.
- Objectives/zones (A, B, C...): their order, and whether they are independent or locked until another is done.
- Buildings: count, floors, rooms, which are enterable, stairs, windows, doors (locked, breakable, scripted).
- Terrain: hills, ravines, rivers (water depth: can the player jump in?), bridges, forests, roads.
- Map border: what surrounds the playable area. Plan high ridges, cliffs and forest so the sky box is never visible.
- Approach roads for enemies and reinforcements. They must bend out of sight; which directions do they come from?

### 3. Player
- Primary and secondary weapons, grenades and smoke counts.
- Weapon pickups or swap stations (where, which weapon, glowing or not).
- Health/difficulty expectations, and where autosaves go.

### 4. Friendlies
- Squad size, names, and the hero (immortal? which character model?).
- Behaviour: follow the player, bounding assault, hold positions, take windows. Are teleports allowed (default: never in view)?
- Reinforcements: from where (off-map and out of sight), how many, and when.

### 5. Enemies
- Count per zone (exact numbers), weapon mix, when they spawn (at start or on approach), patrols.
- Special roles: MG, mortar crews (use tube until hit?), snipers, officers.
- Waves: total count, batch size and interval, spawn directions, behaviour when in contact, retreat
  rule ("at N left they flee to their own spawn").
- Vehicles: types (truck, halftrack, tank), order, timing, riders per vehicle (fill all seats?), invulnerable or not, where they stop.

### 6. Events and scripting
- Doors, ambushes, explosions, smoke screens, battle cries, flybys, artillery.
- Objective texts and their order. Hint texts with key bindings.
- Invisible walls: when, and for whom (player only)?

### 7. Audio and atmosphere
- Music per phase (stock aliases), loops or one-shots, dialogue lines (stock voice aliases), ambience.
- Fog, sun colour, snow and wind FX.

### 8. Testing and delivery
- Does the user want progress screenshots? (Default: yes, bird's-eye plus key spots.)
- The user plays the final test themselves. Ask how to launch it (fullscreen, resolution, AA).
- Git: publish only on the user's explicit word, and say whether public or private.

## Plan template
```
# <map> — "<title>"
Context / story / chain
Measured facts reused from earlier maps (rules list)
Layout (zones, buildings, terrain, border, hidden roads) with coordinates
Mission flow (numbered phases with triggers, objectives, music, saves)
Squad, enemies, vehicles (counts, behaviours)
Files to create and change
Phases with evidence gates (compile gates, screenshot tour list, audits)
Verification criteria
```
