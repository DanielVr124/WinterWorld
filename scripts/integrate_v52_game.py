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
  if(!heroSpruceV52Data) throw new Error('V52 hero spruce data did not load.');
  const heroSpruceV52Mesh=makeColorMesh(
    decodeTypedBase64(heroSpruceV52Data.vertices,Float32Array),
    decodeTypedBase64(heroSpruceV52Data.indices,Uint32Array)
  );
  const heroSpruceV52TriangleCount=heroSpruceV52Data.triangleCount;
  heroSpruceV52Data.vertices='';heroSpruceV52Data.indices='';
  window.WinterWorldHeroSpruceV52Data=null;
  const forestSpruceV52Data=window.WinterWorldForestSpruceV52Data;
  if(!forestSpruceV52Data) throw new Error('V52 forest spruce LOD data did not load.');
  const forestSpruceV52Mesh=makeColorMesh(
    decodeTypedBase64(forestSpruceV52Data.vertices,Float32Array),
    decodeTypedBase64(forestSpruceV52Data.indices,Uint32Array)
  );
  const forestSpruceV52TriangleCount=forestSpruceV52Data.triangleCount;
  forestSpruceV52Data.vertices='';forestSpruceV52Data.indices='';
  window.WinterWorldForestSpruceV52Data=null;
  const forestLowSpruceV52Data=window.WinterWorldForestLowSpruceV52Data;
  if(!forestLowSpruceV52Data) throw new Error('V52 far-forest spruce LOD data did not load.');
  const forestLowSpruceV52Mesh=makeColorMesh(
    decodeTypedBase64(forestLowSpruceV52Data.vertices,Float32Array),
    decodeTypedBase64(forestLowSpruceV52Data.indices,Uint32Array)
  );
  const forestLowSpruceV52TriangleCount=forestLowSpruceV52Data.triangleCount;
  forestLowSpruceV52Data.vertices='';forestLowSpruceV52Data.indices='';
  window.WinterWorldForestLowSpruceV52Data=null;
"""
main = replace_once(main, marker, loader + marker, "hero mesh initialization")

marker = "  const rng=(n)=>{const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x);};"
addition = """
  const heroSpruceV52Position=[10,-4];
  function nearHeroSpruceV52(x,z){return Math.hypot(x-heroSpruceV52Position[0],z-heroSpruceV52Position[1])<5.4;}
  function addV52Conifer(x,z,sc,seed,addCollider=false,forceFar=false){
    const y=terrainHeight(x,z),spin=rng(seed+52000)*Math.PI*2;
    const tint=.93+rng(seed+53000)*.10;
    if(addCollider)addCircleCollider(x,z,.31*sc,'V52 spruce trunk');
    objects.push({
      mesh:forestSpruceV52Mesh,
      lodMeshes:{hero:heroSpruceV52Mesh,medium:forestSpruceV52Mesh,far:forestLowSpruceV52Mesh},
      lodPos:[x,z],
      lodScale:sc,
      lodForceFar:forceFar,
      model:modelMatrix([x,y,z],[0,spin,0],[sc,sc,sc]),
      color:[tint,tint*.99,tint*1.015],
      emissive:0
    });
  }
"""
main = replace_once(main, marker, marker + addition, "hero placement constants")
# Remove the old three-species procedural conifer mesh construction entirely.
species_start = main.find("  const firSpecies=[")
if species_start < 0:
    raise RuntimeError("Legacy procedural conifer species block was not found")
species_end = main.find("  const snowRock=", species_start)
if species_end < 0:
    raise RuntimeError("Could not find end of legacy conifer species block")
main = main[:species_start] + "  // All conifer geometry is loaded from the final V52 spruce asset.\n" + main[species_end:]

# Remove the old cone primitive; no conifer should fall back to a cone silhouette.
main = replace_once(
    main,
    "  const box=boxMesh(), pineCone=coneMesh(1,1,10), trunk=cylinderMesh(.18,1,8), cyl=cylinderMesh(.5,1,12);",
    "  const box=boxMesh(), trunk=cylinderMesh(.18,1,8), cyl=cylinderMesh(.5,1,12);",
    "legacy cone mesh",
)

# Replace the entire old conifer placement function by source boundaries.
# Build 014 has no hero-clearance line yet, so matching its whole body as a
# literal string is brittle; the function boundary is stable across the builds.
tree_start = main.find("  function tree(")
if tree_start < 0:
    raise RuntimeError("Conifer tree placement function was not found")
tree_end = main.find("  let seed=", tree_start)
if tree_end < 0:
    raise RuntimeError("Could not find the forest placement loop after tree()")
new_tree = """  function tree(x,z,sc=1,variant=0,addCollider=true){
    // Keep the denser M2 vegetation clear of the existing cabin and doorway.
    if(Math.abs(x-5)<7.2&&Math.abs(z+24)<8.0)return;
    if(inSakuraGroveClearance(x,z))return;
    if(nearHeroSpruceV52(x,z))return;
    const seed=Math.round((x+75)*91+(z+70)*17)+variant*101;
    addV52Conifer(x,z,sc,seed,addCollider);
  }
"""
main = main[:tree_start] + new_tree + main[tree_end:]

old_ridge = """  for(let i=0;i<12;i++){const x=(i-5.5)*18,z=-67-rng(i+75)*20,h=10+rng(i+43)*16;add(pineCone,[x,h*.08,z],[11,h,11],[.11,.18,.26]);}
  for(let i=0;i<28;i++){
    const x=-92+rng(i+3100)*184,z=-72-rng(i+3200)*17,h=6+rng(i+3300)*9;
    add(pineCone,[x,h*.48,z],[1.7+rng(i+3400)*1.2,h,1.7+rng(i+3500)*1.2],[.075,.13,.19]);
  }
"""
new_ridge = """  // Distant ridgeline conifers use the same V52-derived forest LOD too.
  for(let i=0;i<12;i++){
    const x=(i-5.5)*18,z=-67-rng(i+75)*20,h=10+rng(i+43)*16;
    addV52Conifer(x,z,h/8.42,i+8000,false,true);
  }
  for(let i=0;i<28;i++){
    const x=-92+rng(i+3100)*184,z=-72-rng(i+3200)*17,h=6+rng(i+3300)*9;
    addV52Conifer(x,z,h/8.42,i+9000,false,true);
  }
"""
main = replace_once(main, old_ridge, new_ridge, "distant conifer silhouettes")



# Replace static batches with distance-aware shared V52 LOD batches.
batch_start = main.find("  const batches = new Map();")
batch_end = main.find("  // A tiny observability system:", batch_start)
if batch_start < 0 or batch_end < 0:
    raise RuntimeError("Could not locate static scene batching block")
distance_batcher = """  let sceneBatches = [];
  let sceneInstanceCount=0,sceneTriangleCount=0;
  let sceneLodCounts={hero:0,medium:0,far:0};
  const meshInstanceBuffers=new Map();
  let lastBatchedCameraX=NaN,lastBatchedCameraZ=NaN;
  function rebuildSceneBatches(force=false){
    if(!force&&Number.isFinite(lastBatchedCameraX)&&Math.hypot(camera.x-lastBatchedCameraX,camera.z-lastBatchedCameraZ)<.65)return;
    const batches=new Map();
    sceneInstanceCount=0;sceneTriangleCount=0;sceneLodCounts={hero:0,medium:0,far:0};
    for(const instance of objects){
      let mesh=instance.mesh;
      if(instance.lodMeshes){
        const distance=Math.hypot(camera.x-instance.lodPos[0],camera.z-instance.lodPos[1]);
        if(instance.lodForceFar||instance.lodScale<.55||distance>=78){mesh=instance.lodMeshes.far;sceneLodCounts.far++;}
        else if(distance<26){mesh=instance.lodMeshes.hero;sceneLodCounts.hero++;}
        else{mesh=instance.lodMeshes.medium;sceneLodCounts.medium++;}
      }else if(mesh===heroSpruceV52Mesh){sceneLodCounts.hero++;}
      let batch=batches.get(mesh);
      if(!batch){batch={mesh,instances:[]};batches.set(mesh,batch);}
      batch.instances.push(instance);
    }
    sceneBatches=[];
    for(const batch of batches.values()){
      const data=new Float32Array(batch.instances.length*20);let cursor=0;
      for(const instance of batch.instances){data.set(instance.model,cursor);cursor+=16;data.set(instance.color,cursor);cursor+=3;data[cursor++]=instance.emissive;}
      let instanceBuffer=meshInstanceBuffers.get(batch.mesh);
      if(!instanceBuffer){
        instanceBuffer=gl.createBuffer();meshInstanceBuffers.set(batch.mesh,instanceBuffer);
        gl.bindVertexArray(batch.mesh.vao);gl.bindBuffer(gl.ARRAY_BUFFER,instanceBuffer);
        const stride=20*4;
        for(let col=0;col<4;col++){const loc=3+col;gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,4,gl.FLOAT,false,stride,col*16);gl.vertexAttribDivisor(loc,1);}
        gl.enableVertexAttribArray(7);gl.vertexAttribPointer(7,3,gl.FLOAT,false,stride,64);gl.vertexAttribDivisor(7,1);
        gl.enableVertexAttribArray(8);gl.vertexAttribPointer(8,1,gl.FLOAT,false,stride,76);gl.vertexAttribDivisor(8,1);
        gl.bindVertexArray(null);
      }
      gl.bindBuffer(gl.ARRAY_BUFFER,instanceBuffer);gl.bufferData(gl.ARRAY_BUFFER,data,gl.DYNAMIC_DRAW);
      sceneBatches.push({mesh:batch.mesh,count:batch.instances.length});
      sceneInstanceCount+=batch.instances.length;sceneTriangleCount+=(batch.mesh.count/3)*batch.instances.length;
    }
    gl.bindBuffer(gl.ARRAY_BUFFER,null);lastBatchedCameraX=camera.x;lastBatchedCameraZ=camera.z;
  }
"""
main = main[:batch_start] + distance_batcher + main[batch_end:]
main = replace_once(main,
    "  const camera={x:0,y:terrainHeight(0,18)+WALK_EYE_HEIGHT,z:18,yaw:Math.PI,pitch:0};",
    "  const camera={x:0,y:terrainHeight(0,18)+WALK_EYE_HEIGHT,z:18,yaw:Math.PI,pitch:0};\n  rebuildSceneBatches(true);",
    "initial distance LOD batch")
main = replace_once(main,"last=now;update(dt);frameCount++;","last=now;update(dt);rebuildSceneBatches();frameCount++;","per-frame distance LOD refresh")

marker = "  // First Japanese cherry-blossom grove: broad natural crowns, dark branching,"
hero_object = """  // One full-detail V52 hero spruce anchors the near path. The other conifers
  // use the repaired shape-preserving V52 forest LOD.
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
    "V52 forest medium LOD: " + dollar + "{forestSpruceV52TriangleCount.toLocaleString()} tris/instance\n"
    "V52 forest far LOD: " + dollar + "{forestLowSpruceV52TriangleCount.toLocaleString()} tris/instance\n"
    "V52 LOD counts: near " + dollar + "{sceneLodCounts.hero}, mid " + dollar + "{sceneLodCounts.medium}, far " + dollar + "{sceneLodCounts.far}\n"
    "Sakura body:"
)
main = replace_once(main, old_diag, new_diag, "hero performance diagnostics")
main_path.write_text(main, encoding="utf-8", newline="\n")

html = html_path.read_text(encoding="utf-8")
html = html.replace("Development Build 014", "Development Build 016")
html = html.replace("DEVELOPMENT BUILD 014 · M2", "DEVELOPMENT BUILD 016 · M2")
html = html.replace(
    "Explore three more distinct evergreen forms with less repetitive branching and broader, more visible snow resting along the boughs.",
    "Every conifer now uses the final upright V52 spruce model, with a high-detail hero tree and optimized shared forest LOD."
)
html = html.replace(
    "Evergreen silhouette and moonlit branch-snow refinement · Visual pass 4 · 014",
    "Final V52 spruce across the entire conifer forest · Build 016"
)
html = html.replace(
    "M2 VISUAL BENCHMARK · FOREST ART PASS 4 · BAKERY, NPC AI & WORLD EXPANSION STILL AHEAD",
    "M2 VISUAL BENCHMARK · V52 SPRUCE USED FOR EVERY CONIFER · BAKERY, NPC AI & WORLD EXPANSION STILL AHEAD"
)
html = replace_once(
    html,
    '  <script src="src/sakura_mesh_data.js"></script>\n  <script src="src/main.js"></script>',
    '  <script src="src/sakura_mesh_data.js"></script>\n  <script src="src/hero_spruce_v52_data.js"></script>\n  <script src="src/forest_spruce_v52_data.js"></script>\n  <script src="src/forest_spruce_v52_low_data.js"></script>\n  <script src="src/main.js"></script>',
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


# Build 016 — full-forest V52 integration documentation.
changelog = """# Build 016 — Upright V52 Spruce Across the Entire Conifer Forest

## Fixed
- Converted V52 positions and normals from Blender Z-up to the WebGL Y-up world: (x, y, z) -> (x, z, -y).
- Normalized the lowest point of the root snow skirt to y=0 so instances sit on the terrain.
- Added build-time checks that reject a sideways or incorrectly oriented source mesh.

## Implemented
- Replaced every prior procedural conifer with an instance derived from the final V52 spruce asset.
- The near-path showcase tree uses the high-detail hero LOD.
- All other trees—including the young understory and distant ridgeline silhouettes—use a shared lightweight V52 forest LOD from the exact same source mesh.
- Retained subtle per-instance scale, rotation, and tint variation.
- Preserved the sakura grove, terrain, path, cabin, rocks, lanterns, controls, collision behavior, fog, snowfall, settings, and world layout.

## Performance
- The forest LOD is shared across all repeated conifers rather than drawing the 834k-triangle hero mesh hundreds of times.
- LOD counts and upright bounds are recorded in src/hero_spruce_v52_stats.json.
- The hero LOD stays below 900,000 triangles and the repeated forest LOD stays below 25,000 triangles per instance.

## Validation
- Blender import and independent hero/forest LOD conversion.
- Z-up to Y-up position and normal conversion.
- Upright-bounds and ground-origin checks.
- JavaScript syntax, finite vertex, index-range, mesh-buffer, triangle-budget, and ZIP-integrity checks.
- Target-PC visual and FPS review still requires user testing.
"""
(game / "BUILD_016_CHANGELOG.md").write_text(changelog, encoding="utf-8", newline="\n")
readme = """# Winter World — Development Build 016

A Windows-friendly HTML/WebGL2 first-person winter-world prototype. Build 016 fixes the V52 spruce orientation and replaces every conifer in the playable forest with the final V52 model. The near-path showcase tree uses a high-detail LOD; all other conifers use a lightweight LOD derived from the same asset.

## Run the world
1. Extract the ZIP.
2. Open the `WinterWorld_Prototype` folder.
3. Open `index.html` in a current Chrome or Edge browser.
4. Click **Enter the World**.

If local-file rendering is blocked, run `py -m http.server 8000` in this folder and open `http://127.0.0.1:8000/`.

## Controls
- `W`, `A`, `S`, `D` or arrow keys: move
- Mouse: look around
- `Shift`: move faster
- `Esc`: release the mouse / close settings
- Click the scene: capture the mouse
- `E`: development note
- `F3`: performance and player diagnostics

## Build 016 — V52 Conifer Forest
- Corrects Blender Z-up to WebGL Y-up orientation.
- Uses the V52 model for every conifer, including distant silhouettes.
- Uses a detailed hero LOD and a shared lightweight V52-derived forest LOD.
- Sakura and the rest of the existing world remain unchanged.
- Visual review and target-PC performance testing are pending.
"""
readme_path.write_text(readme, encoding="utf-8", newline="\n")
progress = """# Winter World — Development Progress

## Current status
- **Latest build:** 016
- **Current milestone:** M2 — Quality Benchmark
- **Current sub-pass:** Upright V52 conifer forest integration
- **Build 015:** First hero-tree integration exposed the Blender Z-up / WebGL Y-up mismatch and left the other conifers on the previous procedural meshes.
- **Build 016:** Converts V52 into the WebGL Y-up basis and replaces all forest, understory, and distant conifer placements with the same V52 model source. Target-PC visual/performance review is pending.

## Build 016 — Implemented
- V52 vertices and normals converted with (x, y, z) -> (x, z, -y).
- Snow-root base normalized to y=0.
- V52 is the sole conifer model across the playable forest and distant ridgeline.
- High-detail hero LOD plus shared lightweight forest LOD from the same model.
- Existing sakura grove and non-conifer world systems preserved.

## Pending
- User visual confirmation of upright orientation and consistent V52 conifer coverage.
- Target-PC FPS and visual review.
"""
progress_path.write_text(progress, encoding="utf-8", newline="\n")
print("Prepared Build 016: all conifers use upright V52 geometry and shared LODs.")
