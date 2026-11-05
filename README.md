# Winter World

A public, browser-playable WebGL2 first-person winter-world prototype.

**Current build:** Development Build 025 — Quest Browser & Immersive WebXR  
**Live playtest:** https://danielvr124.github.io/WinterWorld/  
**Latest release:** https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-025-quest-browser-webxr  
**Project roadmap:** [ROADMAP.md](ROADMAP.md)

## Build 025 — Quest Browser playtest

Build 025 keeps the natural snow terrain and walkable bakery from Build 024 and adds browser-first Quest 3 testing:

- Open the GitHub Pages playtest directly in Quest Browser over HTTPS.
- Choose **Open Browser Play** for a flat browser-page version with an on-screen left movement stick, right-side drag-look area, and run button. No keyboard or pointer lock is required.
- Choose **Enter Immersive VR** when the browser reports WebXR support. This starts an immersive stereo headset session.
- In immersive VR, headset pose drives the camera; the left Touch controller thumbstick moves; the right thumbstick snap-turns.
- Touch/Quest and immersive VR start with the Performance graphics preset to reduce the headset rendering load. Desktop keyboard/mouse controls remain available.

## Quest 3 test steps

1. Open the live playtest link above in Quest Browser.
2. On the intro screen, choose **Enter Immersive VR** to launch the stereo headset session.
3. Use the left controller thumbstick to walk and the right controller thumbstick to snap-turn.
4. If immersive mode is unavailable, choose **Open Browser Play** and use the on-screen movement/look controls.
5. Check the natural snowfield, entrance steps, and bakery doorway/interior.

**Manual test status:** The build, JavaScript checks, WebXR/touch-control wiring checks, V52 asset checks, and ZIP integrity passed in CI. Actual Quest 3 WebXR permission, controller axis mapping, movement feel, headset frame rate, and bakery entry/exit still need hands-on testing.

## Downloads and reports

The [Build 025 GitHub Release](https://github.com/DanielVr124/WinterWorld/releases/tag/winter-world-build-025-quest-browser-webxr) includes:
- Playable Build 025 ZIP.
- Human-readable test report.
- Machine-readable QA report.
- Build changelog.

## Desktop controls

- `W`, `A`, `S`, `D` or arrow keys: move
- Mouse: look around
- `Shift`: move faster
- `Esc`: release the mouse / close settings
- Click scene: capture mouse
- `F3`: performance and V52 LOD diagnostics

## Build history

- **Build 020:** Reduced the forest's severe triangle workload and avoided unnecessary GPU-buffer uploads while walking.
- **Build 021–022:** Improved coverage and authored branch structure of medium/far V52 spruce LODs.
- **Build 024:** Natural snow terrain and a walkable bakery interior.
- **Build 025:** Quest Browser flat-play controls and immersive WebXR support; Build 024 environment content preserved.
