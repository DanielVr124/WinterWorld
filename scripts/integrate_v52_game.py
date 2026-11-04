import sys
from pathlib import Path

game = Path(sys.argv[1]).resolve()
main_path = game / "src" / "main.js"
html_path = game / "index.html"
readme_path = game / "README.md"
progress_path = game / "PROGRESS.md"

def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label} marker, found {count}")
    return text.replace(old, new, 1)

main = main_path.read_text(encoding="utf-8")
marker = "  const sakuraData=window.WinterWorldSakuraData;"
loader = """  const heroSpruceV52Data=window.WinterWorldHeroSpruceV52Data;
  if(!heroSpruceV52Data) throw new Error('V52 hero spruce data did not load. Keep src/hero_spruce_v52_data.js beside main.js.');
  const heroSpruceV52Mesh=makeColorMesh(
    decodeTypedBase64(heroSpruceV52Data.vertices,Float32Array),
    decodeTypedBase64(heroSpruceV52Data.indices,Uint32Array)
  );
  const heroSpruceV52TriangleCount=heroSpruceV52Data.triangleCount;
  heroSpruceV52Data.vertices='';heroSpruceV52Data.indices='';
  window.WinterWorldHeroSpruceV52Data=null;
"""
main = replace_once(main, marker, loader + marker, "hero mesh initialization")

marker = "  const rng=(n)=>{const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x);};"
addition = """
  const heroSpruceV52Position=[10,-4];
  function nearHeroSpruceV52(x,z){return Math.hypot(x-heroSpruceV52Position[0],z-heroSpruceV52Position[1])<5.4;}
"""
main = replace_once(main, marker, marker + addition, "hero placement constants")

marker = "    if(inSakuraGroveClearance(x,z))return;"
main = replace_once(main, marker, marker + "\n    if(nearHeroSpruceV52(x,z))return;", "procedural-tree clearance")

marker = "  // First Japanese cherry-blossom grove: broad natural crowns, dark branching,"
hero_object = """  // One final V52 hero spruce anchors the near path. The shared procedural
  // species remain in the wider forest as lighter background/understory trees.
  const heroSpruceV52Y=terrainHeight(heroSpruceV52Position[0],heroSpruceV52Position[1]);
  const heroSpruceV52Spin=rng(52052)*Math.PI*2;
  objects.push({
    mesh:heroSpruceV52Mesh,
    model:modelMatrix([heroSpruceV52Position[0],heroSpruceV52Y,heroSpruceV52Position[1]],[0,heroSpruceV52Spin,0],[1,1,1]),
    color:[1,1,1],
    emissive:0
  });
  addCircleCollider(heroSpruceV52Position[0],heroSpruceV52Position[1],.56,'V52 hero spruce trunk');

"""
main = replace_once(main, marker, hero_object + marker, "hero scene placement")

main = replace_once(
    main,
    "    if(Math.abs(x-pathCenter((32-z)/76))<4.0)continue;",
    "    if(Math.abs(x-pathCenter((32-z)/76))<4.0||nearHeroSpruceV52(x,z))continue;",
    "large boulder hero clearance",
)
main = replace_once(
    main,
    "    if(Math.abs(x-pathCenter((32-z)/76))<4.25||inSakuraGroveClearance(x,z))continue;",
    "    if(Math.abs(x-pathCenter((32-z)/76))<4.25||inSakuraGroveClearance(x,z)||nearHeroSpruceV52(x,z))continue;",
    "small boulder hero clearance",
)

dollar = chr(36)
old_diag = "Scene instances: " + dollar + "{sceneInstanceCount}\nSakura body:"
new_diag = (
    "Scene instances: " + dollar + "{sceneInstanceCount}\n"
    "V52 hero spruce: " + dollar + "{heroSpruceV52TriangleCount.toLocaleString()} tris\n"
    "Sakura body:"
)
main = replace_once(main, old_diag, new_diag, "hero performance diagnostics")
main_path.write_text(main, encoding="utf-8", newline="\n")

html = html_path.read_text(encoding="utf-8")
html = html.replace("Development Build 014", "Development Build 015")
html = html.replace("DEVELOPMENT BUILD 014 · M2", "DEVELOPMENT BUILD 015 · M2")
html = html.replace(
    "Explore three more distinct evergreen forms with less repetitive branching and broader, more visible snow resting along the boughs.",
    "Explore a new hero spruce built from the final V52 tree asset, with dense individual needles and sculpted snow settled directly onto the branches."
)
html = html.replace(
    "Evergreen silhouette and moonlit branch-snow refinement · Visual pass 4 · 014",
    "Final V52 hero spruce · Optimized WebGL2 game mesh · Build 015"
)
html = html.replace(
    "M2 VISUAL BENCHMARK · FOREST ART PASS 4 · BAKERY, NPC AI & WORLD EXPANSION STILL AHEAD",
    "M2 VISUAL BENCHMARK · FINAL V52 HERO SPRUCE INTEGRATED · BAKERY, NPC AI & WORLD EXPANSION STILL AHEAD"
)
html = replace_once(
    html,
    '  <script src="src/sakura_mesh_data.js"></script>\n  <script src="src/main.js"></script>',
    '  <script src="src/sakura_mesh_data.js"></script>\n  <script src="src/hero_spruce_v52_data.js"></script>\n  <script src="src/main.js"></script>',
    "V52 script include",
)
html_path.write_text(html, encoding="utf-8", newline="\n")

changelog = """# Build 015 — Final V52 Hero Spruce Integration

## Implemented
- Integrated the final, Cycles-rendered V52 spruce asset into the playable WebGL2 forest as the near-path hero tree.
- Converted the four authored GLB components (trunk bark, boughs, settled snow, and individual needles) into a compact indexed vertex-color mesh that matches Winter World's existing WebGL2 material pipeline.
- Generated a single-hero game LOD below 900k triangles (the exact final count is recorded in src/hero_spruce_v52_stats.json) instead of shipping the 5.6-million-triangle source GLB directly to the real-time scene.
- Preserved V52's branch-to-snow contact geometry and per-vertex color variation through the LOD conversion.
- Added a matching trunk collider and protected the hero tree's footprint from overlapping procedural trees and rocks.
- Added V52 triangle-count reporting to F3 diagnostics.

## Preserved
- Build 014's three shared procedural conifer species remain for background and understory coverage so the forest keeps its existing variety and performance budget.
- Sakura geometry, blossoms, snow, grove placements, terrain, path, rocks away from the hero footprint, cabin, lanterns, controls, collisions, fog, snowfall, settings, and frame modes remain unchanged.
- No changes were made to the main forest layout beyond clearing the V52 hero tree footprint.

## Performance approach
- The full source GLB is intentionally not submitted as a 5.6-million-triangle real-time tree.
- The game uses one optimized V52 hero instance; the existing lightweight procedural meshes continue to fill the wider forest.
- The optimized game mesh is built with Blender 5.2.3 and keeps vertex positions, normals, and vertex colors for the existing WebGL2 shader.

## Validation
- Blender import and per-component LOD conversion.
- Geometry and index-buffer integrity checks.
- JavaScript syntax checks for the game and new mesh data.
- Build archive integrity check.
- Browser/WebGL visual performance still requires review on the user's target PC; no target-hardware FPS is claimed by this build.
"""
(game / "BUILD_015_CHANGELOG.md").write_text(changelog, encoding="utf-8", newline="\n")

readme = readme_path.read_text(encoding="utf-8")
readme = readme.replace("# Winter World — Development Build 014", "# Winter World — Development Build 015")
readme = readme.replace(
    "A Windows-friendly HTML/WebGL2 first-person winter-world prototype. Build 014 continues **M2 — The Quality Benchmark** by giving the evergreen species more distinct branching structures and making branch snow more visible at player height.",
    "A Windows-friendly HTML/WebGL2 first-person winter-world prototype. Build 015 integrates the final V52 hero spruce into the playable forest while retaining the existing lightweight conifers for background coverage."
)
readme = readme.replace(
    "- **M2 — Quality Benchmark: in progress.** Build 011 introduced the first conifer/forest-floor pass. Build 012 added the source-derived sakura grove; the user accepted the blossoms and rocks but requested more snow and said the overall tree models still look low quality. Build 013 was reviewed: the user accepted the sakura branch/detail improvements but requested more overall visual upgrades and did not accept the conifer structure checks. Build 014 reworks the conifer species and their branch-snow readability; visual/performance review is pending.",
    "- **M2 — Quality Benchmark: in progress.** Build 015 adds the final V52 hero spruce as a high-detail focal tree with an optimized WebGL2 LOD. The other shared procedural conifers remain as background species. Visual review and target-PC performance testing are pending."
)
readme += """

## Build 015 — Final V52 Hero Spruce

- Added the final V52 spruce asset to the playable world as a near-path hero tree.
- Kept V52's individual needle geometry, branch structure, bark, and attached snow mantle geometry in a WebGL2-ready vertex-color mesh.
- Generated an optimized game LOD rather than submitting the full multi-million-triangle source mesh directly.
- Preserved the existing procedural conifers for the rest of the forest to avoid turning every distant tree into a high-detail hero asset.
- Target-PC visuals and FPS require user review.
"""
readme_path.write_text(readme, encoding="utf-8", newline="\n")

progress = progress_path.read_text(encoding="utf-8")
progress = progress.replace("- **Latest build:** 013", "- **Latest build:** 015")
progress = progress.replace("- **Current sub-pass:** Forest Art Pass 3", "- **Current sub-pass:** Final V52 hero spruce integration")
progress += """

## Build 015 — Final V52 Hero Spruce Integration

- The final V52 spruce is integrated into the playable forest as a near-path hero tree.
- Its authored bark, branch, snow, and individual-needle components are converted to an optimized vertex-color mesh for the existing WebGL2 renderer.
- One high-detail hero instance is used; the existing procedural species remain for background and understory coverage.
- Target-PC visual review and performance testing are pending.
"""
progress_path.write_text(progress, encoding="utf-8", newline="\n")

print("Patched Build 014 source into Build 015 with the final V52 hero spruce.")
