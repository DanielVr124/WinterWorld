# Winter World

A public, browser-playable WebGL2 first-person winter-world prototype.

**Current build:** Development Build 019 — Distance-Based V52 LODs  
**Live playtest:** https://danielvr124.github.io/WinterWorld/  
**Latest release:** https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-019-v52-distance-lods

## Build 019 — Distance-based V52 conifer detail

Build 016's repeated forest trees looked broken because the forest mesh had individual snow and needle faces removed at random. Build 018 improved this by keeping connected geometry islands, but the reduction was still too aggressive because component decimation and island selection compounded.

Build 019 uses three separate V52 meshes, each generated independently from the original V52 source:

- **Near:** full-detail hero mesh, 834,798 triangles, selected within 26m.
- **Medium:** 577,808 triangles, retaining 70% of the optimized complete snow/needle islands, selected from 26m to 78m.
- **Far:** 241,964 triangles, retaining 28% of the optimized complete snow/needle islands, selected at 78m and beyond and on small/distant trees.

All conifers use the same V52 source model. The runtime re-batches the scene as the player moves and exposes near/mid/far counts in the F3 diagnostics.

## Build downloads and reports

The [Build 019 GitHub Release](https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-019-v52-distance-lods) includes:
- Playable Build 019 ZIP.
- Automated test report (Markdown).
- Machine-readable QA results (JSON).
- Blender comparison render of the actual near, medium, and far mesh buffers.
- V52 source renders, geometry stats, and changelog.

**Test distinction:** automated geometry, buffer, orientation, distance-LOD wiring, JavaScript, and archive checks passed in CI. In-browser visual confirmation and target-PC FPS remain pending hands-on review; they are not represented as passed tests.

## Run locally

1. Download and extract the playtest ZIP.
2. Open the `WinterWorld_Prototype` folder.
3. Open `index.html` in Chrome or Edge.
4. If local-file loading is blocked, run `py -m http.server 8000` in that folder and open `http://127.0.0.1:8000/`.

## Controls

- `W`, `A`, `S`, `D` or arrow keys: move
- Mouse: look around
- `Shift`: move faster
- `Esc`: release the mouse / close settings
- Click the scene: capture the mouse
- `E`: development note
- `F3`: performance, player, and live V52 LOD diagnostics

## Build history

- **Build 016:** Corrected V52 orientation, but its repeated-tree mesh was too aggressively reduced.
- **Build 017–018:** Tried connected-island sampling; reports exposed that the repeated trees remained too sparse.
- **Build 019:** Adds distance-based full, medium, and far V52 detail levels and restores published build reports.
