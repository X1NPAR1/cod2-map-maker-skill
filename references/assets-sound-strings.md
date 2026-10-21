# Assets, sounds, strings

## Sound aliases
- **File:** `soundaliases/<map>.csv`. Copy the header from a stock csv in iw_06; its columns include `name, sequence, file, ... loadspec, subtitle`.
- **The loadspec trap:** stock aliases are restricted to their own level through the loadspec column.
  - Copy every alias you use and set its loadspec to `<map>`.
  - If a row has a `secondaryaliasname`, copy that alias too.
- **Check the wav files:** confirm that each `file` exists in an iwd or in loose `main/sound/`.
- **Check the script:** collect every string your GSC passes to `playsound`, `musicplay`, `playloopsound` and `playSoundinSpace`, and diff the list against the csv. A single missing alias stops the game the first time it plays.
- **Custom audio:** 16-bit PCM wav, mono for 3D sounds, stored under `main/sound/<map>/`.

## Localized strings
```
VERSION             "1"
CONFIG              "C:\trees\cod2\bin\StringEd.cfg"
FILENOTES           ""

REFERENCE           OBJ_A
LANG_ENGLISH        "Take the outpost."

ENDMARKER
```
- **Referencing:** use `&"<MAP>_OBJ_A"`, i.e. the file name in uppercase plus `_` plus the reference.
- **Precache:** precache every string with `precacheString`.
- **Key-binding text:** put it in `<map>_platform.str` and reference it as `&"<MAP>_PLATFORM_KEY"`.
- **Encoding:** cp1252 or ASCII.

## Models
- `_obj` models such as `weapon_*_obj` glow. Use them only on pickups that should be highlighted.
- Multi-bone models cannot be static `misc_model`s; make them `script_model`s.
- Confirm every model exists in the `xmodel/` folder of iw_13, and precache each one you spawn from script.
- **Crate tops:** stock `prop_crate*` are 26 units tall.

## FX
Register effects in `<map>_fx.gsc` as `level._effect["name"] = loadfx("fx/...efx");`.

Effects we confirmed:
- `fx/dust/dust_door_ambush.efx`
- `fx/impacts/large_woodhit.efx`
- `fx/muzzleflashes/mortar_flash.efx`

## Level csv (`main/maps/<map>.csv`)
```
levelBriefing,loadscreen_tankhunt
victoryBackdrop,victory_russian
defeatBackdrop,defeat_russian
```

## Look at every texture before you use it
Material names lie. `stalingradwinter_door_wood01`, `stalingrad_wd_door` and `dawnville2_wood_door01-03`
all point to `case256x512brown*` images — **placeholder** crate-coloured textures, not doors. A material
whose image name starts with `case` is a placeholder. Use `scripts/iwi_preview.py` to export the colour
map to PNG and view it. Verified real single-leaf doors: `mtl_caen_door_01` (256x512 brown planks,
ring handle), `mtl_hill400_door_01`, `v_door01`, `mtl_wood_door1`, `mtl_door_wood` (double panelled).
Fit a door texture exactly to the leaf: scale = leaf size / image size, shift = -min.

IWI v5 header: `IWi`, version 5, format (0x0B DXT1, 0x0C DXT3, 0x0D DXT5, 1 RGBA, 2 RGB), usage,
width u16, height u16, depth u16, 4 x int32 mip offsets (28 bytes). Mips are stored smallest first,
so the full-size image is the LAST w*h block.
