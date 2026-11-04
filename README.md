# Winter World

A public, browser-playable WebGL2 exploration prototype. The repository now includes an automatic GitHub Pages deployment workflow.

**Current playtest package:** Build 015 — Final V52 Hero Spruce  
**Hosted URL after the first successful deployment:** https://danielvr124.github.io/WinterWorld/

## One-time setup

1. Open [Repository Pages settings](https://github.com/DanielVr124/WinterWorld/settings/pages).
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Download the [Winter World playtest archive](https://github.com/DanielVr124/WinterWorld) from this conversation and upload it to the repository root using **Add file → Upload files**. The exact filename must be `WinterWorld_Playtest.zip`.
4. Commit the upload to `main`. The **Publish Winter World Playtest** workflow will extract the archive, validate the required game files, and deploy the site.

The workflow is at `.github/workflows/deploy-pages.yml`. You can also start it manually from the repository's **Actions** tab after Pages has been enabled.

## Publishing future playtests

The approved V52 build pipeline runs on the `render-v52-cycles` branch through `.github/workflows/build-v52-game.yml`. After the game build passes its Blender conversion, WebGL2 mesh-buffer, JavaScript, triangle-budget, and ZIP checks, it uploads a `WinterWorld-Build015-V52-HeroSpruce` artifact.

The default-branch workflow at `.github/workflows/deploy-pages.yml` listens for successful Build 015 workflow runs, downloads that exact run's artifact, validates the game files, and deploys the extracted `WinterWorld_Prototype/` folder to the **same hosted URL**. Asset URLs receive a unique deployment-run query so browsers fetch the new files after each publish.

For a manual playtest package outside the V52 pipeline, the Pages workflow still supports the root-level `WinterWorld_Playtest.zip` upload path. Keep its contents inside `WinterWorld_Prototype/` with `index.html`, `style.css`, `src/main.js`, and `src/sakura_mesh_data.js`; Build 015 also includes `src/hero_spruce_v52_data.js` and its stats file.

If GitHub does not offer an overwrite for the existing ZIP, delete the old `WinterWorld_Playtest.zip` from the repository first, then upload the replacement with the exact same filename.

## Local play

Extract the archive and serve the `WinterWorld_Prototype` folder over HTTP (for example, `python -m http.server 8000`). Open `http://localhost:8000/`. Do not open `index.html` directly as a `file://` URL.

## Public access

This repository and its GitHub Pages website are public. Game files deployed to Pages are therefore publicly downloadable. Do not put credentials, private information, or unapproved experimental builds in the published archive.
