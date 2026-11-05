# Winter World Roadmap

This roadmap records the agreed order of work and the quality bar for the world. It is intentionally milestone-based rather than tied to calendar dates: a milestone is not complete just because its automated checks pass.

## Current milestone — Finish the V52 conifer forest

**Status:** In progress. Build 022 is the latest published playtest. Build 023 is being prepared from the fuller, spatially sampled foliage branch.

Acceptance criteria:
- Every conifer uses the same final upright V52 spruce source.
- The showcase, medium, and far versions retain a recognizably full winter-spruce silhouette: layered boughs, visible needles, and snow resting on branches.
- Distant LODs may use fewer triangles, but they must not look dead or stripped.
- The game remains responsive while walking; instance buffers are not rebuilt on every movement step.
- The comparison render is reviewed visually, then the live browser build is checked for appearance and frame rate on the playtest PC.

## Next milestone — Natural snow terrain

**Current state:** The world has a lightly undulating snowfield, a curving compacted path, and raised snow shoulders. This is an early terrain pass, not the finished natural snow surface.

Planned work:
- Replace the subtle mathematical ripples with broader, irregular terrain forms.
- Shape gentle rolls, wind-built drifts, soft mounds, and uneven snow accumulation.
- Blend the snow naturally around trees, rocks, the path, and the bakery/cabin.
- Keep the path readable without making the surrounding snow look like a flat plane or repeated circular piles.
- Preserve stable walking height and collision over the new terrain.

## Next milestone — Finish the bakery/cabin

**Current state:** The first-pass timber exterior and entrance approach exist. The footprint is currently blocked by a solid collider; the interior is not built yet.

Planned work:
- Finish the exterior proportions, woodwork, roof/snow details, windows, trim, and entrance.
- Build a complete walkable interior with believable room layout, materials, warm lighting, and furnishings.
- Replace the temporary solid-footprint collision with doorway and room-aware collision.
- Test entering, walking through, and exiting without clipping or getting stuck.

## World-wide quality pass

After those core areas, bring the rest of the scene up to the same visual standard:
- Trees and understory vegetation.
- Snow-covered rocks, fallen branches, and forest-floor details.
- Terrain materials, lighting, fog, and snowfall.
- Bakery/cabin exterior and interior details.

The quality bar is consistent visual finish, not identical polygon counts. Close objects can use more detail; distant objects should use efficient LODs and instancing while keeping the same recognizable materials and silhouette.

## Release gate

Do not mark a visual milestone finished based only on geometry budgets or JavaScript checks. Each release should include:
- The playable build.
- Automated QA results.
- A render showing the actual exported assets.
- A clear note of what still needs live visual or target-PC performance review.
