# Winter World

A public, browser-playable WebGL2 exploration prototype.

**Current playtest package:** Development Build 016 — Upright V52 Conifer Forest  
**Live website:** https://danielvr124.github.io/WinterWorld/  
**Build 016 workflow:** https://github.com/DanielVr124/WinterWorld/actions/runs/41827324853

## Build 016

- Corrects the V52 spruce's Blender Z-up to WebGL Y-up coordinate conversion, including vertex normals.
- Normalizes the bottom of the snow-root geometry to the terrain.
- Replaces every conifer in the playable forest with the final V52 spruce model.
- Uses one high-detail V52 hero tree near the path and a shared lightweight V52-derived LOD for the rest of the forest, including the distant ridgeline.
- Preserves the sakura grove, terrain, path, cabin, rocks, lanterns, controls, collision behavior, fog, snowfall, settings, and world layout.
- Build-time checks validate upright bounds, both mesh buffers, index ranges, triangle budgets, JavaScript syntax, and ZIP integrity.

## Automated publishing

The V52 build pipeline runs on the `render-v52-cycles` branch through `.github/workflows/build-v52-game.yml`. A successful build uploads a versioned artifact to its Actions run.

The default-branch workflow at `.github/workflows/deploy-pages.yml` downloads that exact artifact, validates its game files, and deploys it to the same GitHub Pages URL. Asset URLs receive a unique deployment-run query so browsers fetch the latest files after each publish.

The approved playtest package is also published as a [Build 016 GitHub Release](https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-016-v52-conifer-forest) with its ZIP, mesh statistics, changelog, and preview renders.

## Local play

Extract the playtest ZIP, open the `WinterWorld_Prototype` folder, and serve it over HTTP (for example, `python -m http.server 8000`). Then open `http://localhost:8000/` in a current Chrome or Edge browser. Do not open `index.html` directly as a `file://` URL.

## Public access

This repository and its GitHub Pages website are public. Game files deployed to Pages are therefore publicly downloadable. Do not put credentials, private information, or unapproved experimental builds in the published archive.
