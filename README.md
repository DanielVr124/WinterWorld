# Winter World

A public, browser-playable WebGL2 first-person winter-world prototype.

**Current build:** Development Build 017 — V52 Forest LOD Repair  
**Live playtest:** https://danielvr124.github.io/WinterWorld/  
**Latest release:** https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-017-v52-forest-lod-repair

## Build 017 — Shape-preserving V52 conifer forest

Build 016's repeated forest trees looked broken because the low-detail generator removed random individual faces from the dense snow and needle components. Build 017 replaces that with whole connected-island sampling, so retained snow patches and needles stay intact. The high-detail hero tree is kept, and all repeated conifers still come from the same V52 spruce source.

## Build downloads and reports

The latest GitHub Release contains:
- Playable Build 017 ZIP.
- Automated test report (Markdown).
- Machine-readable QA report (JSON).
- Blender render comparing the actual exported hero and forest LODs.
- V52 source renders and geometry stats.

**Important test distinction:** automated geometry, buffer, syntax, and archive checks are run in CI. In-browser appearance and target-PC FPS remain pending hands-on review; they are not represented as passed tests.

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
- `F3`: performance and player diagnostics

## Build history

- **Build 016:** Corrected the V52 tree's Blender Z-up to WebGL Y-up conversion, but its repeated-forest LOD was too aggressively reduced and damaged the visible snow/needle surfaces.
- **Build 017:** Repairs the forest LOD by retaining complete connected snow/needle islands and restores published build test reports plus an actual LOD comparison render.
