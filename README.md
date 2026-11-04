# Winter World

A public, browser-playable WebGL2 first-person winter-world prototype.

**Current build:** Development Build 020 — V52 Performance LODs  
**Live playtest:** https://danielvr124.github.io/WinterWorld/  
**Latest release:** https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-020-v52-performance-lod

## Build 020 — V52 forest performance fix

Build 019 rendered far too much geometry at once. Its ordinary trees could use the 834,798-triangle hero mesh near the player, the 577,808-triangle medium mesh, or the 241,964-triangle far mesh. Instancing reduced draw calls but did not reduce the triangle workload.

Build 020 keeps the full-detail mesh on the single showcase tree and uses smaller V52-derived meshes for every other conifer:

- **Showcase:** 834,798 triangles.
- **Ordinary medium trees:** 54,812 triangles each, used within 68m.
- **Far trees:** 21,534 triangles each, used beyond 68m and for small understory/ridgeline trees.

The meshes are generated independently from the original V52 source. The runtime now rebuilds GPU instance buffers only when a tree crosses an LOD boundary, not during ordinary movement.

Based on the current forest placements at the starting viewpoint, this reduces the estimated tree workload from about 67.3 million to 6.2 million triangles per frame (roughly 10.9× fewer). This is a geometry estimate, not a measured FPS result.

## Build downloads and reports

The [Build 020 GitHub Release](https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-020-v52-performance-lod) includes:
- Playable Build 020 ZIP.
- Automated test report (Markdown).
- Machine-readable QA results (JSON).
- Blender comparison render of the actual showcase, medium, and far mesh buffers.
- V52 source renders, geometry stats, and changelog.

**Test distinction:** the automated geometry, buffer, orientation, LOD wiring, JavaScript, and ZIP checks passed in CI. Actual frame rate and in-browser visual quality on target hardware still need hands-on review.

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
