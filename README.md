# Winter World

A public, browser-playable WebGL2 first-person winter-world prototype.

**Current build:** Development Build 022 — Fuller V52 Spruce Boughs  
**Live playtest:** https://danielvr124.github.io/WinterWorld/  
**Latest release:** https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-022-v52-fuller-boughs

## Build 022 — fuller V52 forest LODs

Build 020 solved the severe performance problem, but its medium and far tree variants lost too much of the source tree's foliage and branch structure. Build 021 distributed snow and needle islands across the crown; Build 022 also restores substantially more of the authored branch geometry.

- **Showcase:** 834,798 triangles.
- **Ordinary medium trees:** 108,394 triangles each, with 25% of the source bough component retained; used within 68m.
- **Far trees:** 43,100 triangles each, with 10% of the source bough component retained; used beyond 68m and for small understory/ridgeline trees.
- Snow and needle islands are sampled across eight vertical bands and twelve azimuth sectors, rather than randomly across the entire mesh.
- The full-detail mesh remains restricted to the single showcase tree. Ordinary trees continue to use distance-based LODs.
- GPU instance buffers rebuild only when a tree crosses an LOD boundary, not during ordinary movement.

Based on the existing starting-view forest placement counts (74 medium, 61 far, and one showcase tree), the estimated workload is about **11.5 million tree triangles per frame**, compared with about **67.3 million** in the laggy Build 019 configuration (roughly **5.9× fewer**). This is a geometry estimate, not a measured FPS result. Build 022 passed the automated mesh, coverage, orientation, LOD wiring, JavaScript, and ZIP-integrity checks; actual in-browser appearance and target-PC FPS still require hands-on review.

## Build downloads and reports

The [Build 022 GitHub Release](https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-022-v52-fuller-boughs) includes:
- Playable Build 022 ZIP.
- Automated test report (Markdown).
- Machine-readable QA results (JSON).
- Blender comparison render of the actual hero, medium, and far mesh buffers.
- V52 source renders, geometry stats, and changelog.

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
- `F3`: performance, player, submitted-triangle, and live V52 LOD diagnostics

## Build history

- **Build 016:** Corrected V52 orientation, but repeated-tree meshes were too aggressively reduced.
- **Build 017–018:** Tried connected-island sampling; repeated trees remained too sparse.
- **Build 019:** Added distance-based detail, but left ordinary trees far too expensive.
- **Build 020:** Keeps the full hero mesh on the showcase tree, reduces ordinary tree meshes to practical budgets, and removes unnecessary GPU-buffer uploads while walking.
- **Build 021:** Spreads retained snow and needle islands across the tree crown.
- **Build 022:** Restores more authored bough structure while keeping ordinary trees on the optimized medium/far LODs.
