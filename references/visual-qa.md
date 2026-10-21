# Visual QA with screenshots (mandatory before every hand-off)

Compile gates catch leaks and path islands. They do not catch the things players complain about:
- floating props
- textures that are placeholders, stretched or cut off
- doors cutting into walls
- sky box edges at the end of roads
- enemies visible as they spawn
- a staircase with overlapping faces

The only way to catch these is to **look**. Do it yourself before asking the user to play.

## The screenshot tour
1. **Add a tour mode to the level GSC.** For example `if (getcvar("kr_tur") == "N") level thread tour();`. It runs before any mission logic, takes away weapons, and for each view:
   - `setcvar("kr_adim", n)`;
   - holds `setorigin` + `setplayerangles` for about 10 s, so the frame is stable;
   - can trigger scripted states between views (lower doors, open them with the real `kapi_kir`, spawn a vehicle). This also *executes* those code paths, which is how a fatal "brushmodel must have DYNAMICPATH" error was found.
2. **Drive it with a PowerShell script.**
   - Launch windowed with `+set developer 1 +set logfile 2 +set kr_tur N +devmap <map>`.
   - Wait for `Load time:` in console.log, click to continue, toggle noclip.
   - Each time `kr_adim n` appears in console.log, capture the client area of the game window to `ekran/<prefix>_<n>.png`.
   - Watch for error dialogs (`#32770` windows) and for the process exiting.
   - Print `ERROR` / `script runtime error` lines at the end.
3. **The screen must be unlocked.** On a locked Windows session the game renders nothing and the log stalls after "Recovering lost device". Detect `LogonUI.exe` and wait for unlock rather than reporting a broken tour.
4. **Read every image yourself** with the image viewer. Then fix, recompile and re-shoot until nothing is wrong.

## Standard view list
| Group | Views |
|---|---|
| Bird's-eye | whole map (z 4000+, pitch 89); each zone; the river and bridges |
| Start | from the player start in 4 directions, including down the arrival road |
| Approach roads | from each defended window/position, down every enemy road (no sky box, no visible spawn) |
| Buildings | each room on each floor; stairs bottom and top; every door closed AND opened; windows from inside |
| Props | crates with pickups, weapon models on crates, furniture against walls (floating?) |
| Objectives | each mortar/MG nest; final gathering spot |
| Edges | look along the clip border; ravine and river ends |

## What to check in each image
- **Sky:** sky box edge or seam visible? Flat sky at the end of a valley?
- **Floating:** rocks, trees, posts, crates or weapons floating, or sunk into terrain?
- **Textures:** placeholder (case*, checker), stretched, wrong scale, seam/wrap visible, z-fighting?
- **Moving parts:** doors flush when closed, fully open without cutting into walls, thick enough.
- **Interior:** stairs without overlapping faces, rails not stuck through steps, ceilings closed.
- **Lighting:** black interiors, missing lightmaps, overbright?
- **Spawns:** any spawner or vehicle start visible from playable space?

## Reporting to the user
- Send the key images (closed/open states, before/after) with a short caption. Use the file-send tool so they reach the user's phone.
- Only after the images look right, launch the game for the user's playtest. Ask them to play it through and report anything wrong. Their list is the next iteration.
