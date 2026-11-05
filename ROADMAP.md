# Winter World Roadmap

This roadmap records the agreed order of work and the quality bar for the world. A milestone is not complete just because its automated checks pass.

## Current priority — Natural snow terrain and finished bakery

The next major playable update is focused on making the environment itself feel complete. Forest LOD polishing is deliberately deferred until these two foundational areas are ready.

**Current playtest:** Build 025 — Quest Browser & Immersive WebXR, carrying forward Build 024's natural snow terrain and walkable bakery. The build and Pages deployment succeeded. Quest 3 WebXR permission, controller mapping, headset frame rate, terrain walking, and bakery entry/exit still need hands-on headset testing.

### 1. Natural snow terrain

**Current state:** A lightly undulating snowfield sits on a regular grid, with a curving compacted path and raised snow shoulders. This is only a placeholder-level terrain pass.

Planned work:
- Replace the subtle mathematical ripples with broader, irregular ground forms.
- Sculpt gentle rolls, wind-built drifts, soft mounds, shallow dips, and uneven snow accumulation.
- Create believable transitions around tree roots, rocks, the path, and the bakery.
- Make the path feel packed down and integrated into the snow rather than like a flat strip laid on top.
- Preserve stable walking height, slope limits, and collision as the terrain changes.
- Check that the ground silhouettes and shading look natural from normal first-person view, not only from an overhead view.

### 2. Finish the bakery/cabin

**Current state:** The first-pass timber exterior, roof, windows, sign, chimney, and entrance steps exist. The building is currently blocked by a solid collider across its footprint; no walkable interior has been built.

Planned work:
- Finish exterior proportions, woodwork, roof and snow details, windows, trim, entrance, and surrounding ground connection.
- Replace the solid footprint collider with separate wall and doorway collisions.
- Build a complete walkable interior with a coherent room layout, bakery counter/display, ovens or preparation area, storage, furnishings, warm lighting, and suitable material detail.
- Make the inside visually consistent with the exterior and the winter-world art direction.
- Verify the player can approach, enter through the actual doorway, move around inside, and exit without clipping or getting stuck.
- Ensure the interior is lit and readable from the player's normal eye height.

## Deferred milestone — Finish the V52 conifer forest

**Status:** Deferred until natural terrain and the bakery are ready. Build 022 remains the latest published playtest. Build 023 is an experimental forest-LOD direction, not the next public milestone.

When resumed:
- Every conifer should use the same final upright V52 spruce source.
- Showcase, medium, and far versions must retain a full winter-spruce silhouette: layered boughs, visible needles, and snow resting on branches.
- Distant LODs may use fewer triangles, but must not look dead or stripped.
- Walking must remain responsive; GPU instance buffers must not rebuild on every movement step.
- Visual appearance must be checked in the browser, and frame rate must be checked on the playtest PC.

## World-wide quality pass

After the terrain, bakery, and forest milestones, bring the rest of the world to a consistent visual standard:
- Snow-covered rocks, fallen branches, and forest-floor details.
- Trees and understory vegetation.
- Terrain materials, lighting, fog, and snowfall.
- Bakery exterior and interior finishing details.

The quality bar is consistent visual finish, not identical polygon counts. Close objects can use more detail; distant objects should use efficient LODs and instancing without looking visibly unfinished.

## Release gate

Do not mark a visual milestone finished based only on geometry budgets or JavaScript checks. Each release should include:
- The playable build.
- Automated QA results.
- Comparison views showing the actual in-game result.
- A clear note of what still needs live visual or target-PC performance review.
