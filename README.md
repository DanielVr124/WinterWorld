# Winter World

A public, browser-playable WebGL2 first-person winter-world prototype.

**Current build:** Development Build 024 — Natural Snow Terrain & Walkable Bakery  
**Live playtest:** https://danielvr124.github.io/WinterWorld/  
**Latest release:** https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-024-natural-snow-bakery  
**Project roadmap:** [ROADMAP.md](ROADMAP.md)

## Build 024 — Natural Snow Terrain & Walkable Bakery

This milestone moves the environment ahead of further forest LOD polishing, as requested.

- Replaces the simple repeating ground ripples with a deterministic layered snow heightfield, broad rolling forms, and wind-built drifts.
- Uses one shared terrain height function for the visible snowfield, props, path, and first-person ground height.
- Blends a level foundation under the bakery and bends the path approach toward its entrance.
- Replaces the solid cabin blocker with separate wall collisions and an open doorway.
- Adds a walkable timber floor, service counter and pastry display, oven, ingredient shelves, prep table, ceiling beams, warm interior fixtures, and room-aware collisions.
- Keeps the existing V52 forest meshes and performance-oriented LODs unchanged from Build 022.

**Automated checks:** JavaScript syntax, sampled terrain height/slope bounds, level bakery foundation, doorway and wall-collision markers, stair/floor height alignment, and ZIP integrity passed in CI.

**Still needs hands-on review:** the actual first-person visual quality of the snow, walking the terrain and entrance steps, entering/exiting the bakery and checking furniture collisions, and target-PC FPS. Passing automated checks does not establish that those visual and movement checks are complete.

## Downloads and reports

The [Build 024 GitHub Release](https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-024-natural-snow-bakery) includes:
- Playable Build 024 ZIP.
- Human-readable automated test report.
- Machine-readable QA results and terrain metrics.
- Build changelog.

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
- `F3`: performance and V52 LOD diagnostics

## Build history

- **Build 020:** Reduced the forest's severe triangle workload and avoided unnecessary GPU-buffer uploads while walking.
- **Build 021–022:** Improved the coverage and authored branch structure of medium/far V52 spruce LODs.
- **Build 023:** Experimental forest direction; deferred from public deployment so terrain and the bakery could take priority.
- **Build 024:** Natural snow terrain, bakery doorway/interior, and room-aware walking/collision.
