# Winter World

A browser-playable Windows/WebGL2 development playtest. The hosted site serves the latest approved playtest from the `main` branch.

The site is public because this repository uses GitHub Pages on the GitHub Free plan. Do not commit private data, credentials, or personal information.

Current playable version: **Build 014** (M2 forest benchmark, awaiting further visual asset work).

## Play

After GitHub Pages is enabled and the first deployment succeeds, visit:

https://danielvr124.github.io/WinterWorld/

## Updating playtests

To publish a new playtest, update the website files in the root of `main` and push the changes. `.github/workflows/deploy-pages.yml` publishes the repository automatically. Update the cache-busting version query strings in `index.html` and `src/sakura_loader.js` whenever the game files change.

## Local play

Serve the repository root over HTTP (for example, `python -m http.server 8000`) and open `http://localhost:8000/`. The compressed sakura mesh loader uses `fetch` and browser `DecompressionStream`, so opening `index.html` directly as `file://` is not supported.

## Technical notes

- Static HTML, CSS, and WebGL2; no backend is required.
- The large sakura geometry payload is stored as gzip-compressed binary with float16 vertex attributes and uint32 indices, then decoded in the browser.
- Playtest results are collected in the project conversation, not by a separate website testing form.
