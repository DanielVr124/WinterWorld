# Winter World

A public, browser-playable WebGL2 exploration prototype. The repository now includes an automatic GitHub Pages deployment workflow.

**Current playtest package:** Build 014  
**Hosted URL after the first successful deployment:** https://danielvr124.github.io/WinterWorld/

## One-time setup

1. Open [Repository Pages settings](https://github.com/DanielVr124/WinterWorld/settings/pages).
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Download the [Winter World playtest archive](https://github.com/DanielVr124/WinterWorld) from this conversation and upload it to the repository root using **Add file → Upload files**. The exact filename must be `WinterWorld_Playtest.zip`.
4. Commit the upload to `main`. The **Publish Winter World Playtest** workflow will extract the archive, validate the required game files, and deploy the site.

The workflow is at `.github/workflows/deploy-pages.yml`. You can also start it manually from the repository's **Actions** tab after Pages has been enabled.

## Publishing future playtests

For each approved build, create a ZIP with this same filename:

`WinterWorld_Playtest.zip`

Keep the game files inside a `WinterWorld_Prototype/` folder, including `index.html`, `style.css`, `src/main.js`, and `src/sakura_mesh_data.js`. Upload the updated archive to the same repository path and commit it to `main`. The workflow will replace the hosted game at the **same URL** and add a commit-based cache-busting query to the asset URLs so browsers fetch the updated build.

If GitHub does not offer an overwrite for the existing ZIP, delete the old `WinterWorld_Playtest.zip` from the repository first, then upload the replacement with the exact same filename.

## Local play

Extract the archive and serve the `WinterWorld_Prototype` folder over HTTP (for example, `python -m http.server 8000`). Open `http://localhost:8000/`. Do not open `index.html` directly as a `file://` URL.

## Public access

This repository and its GitHub Pages website are public. Game files deployed to Pages are therefore publicly downloadable. Do not put credentials, private information, or unapproved experimental builds in the published archive.
