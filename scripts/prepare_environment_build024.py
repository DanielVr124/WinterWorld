from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
main_path = root / 'src' / 'main.js'
html_path = root / 'index.html'
main = main_path.read_text(encoding='utf-8')

def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {n}')
    return text.replace(old, new, 1)

old_terrain = """  // Shared height/center functions keep the compacted path and its snow edges aligned.
  const terrainHeight=(x,z)=>-.05+Math.sin(x*.11+z*.045)*.09+Math.cos(z*.13)*.06;
  const pathCenter=(t)=>Math.sin(t*5.3)*5+Math.sin(t*12)*.55;
  // Undulating snowfield.
  const terrain=planeGrid(160,110,terrainHeight,(x,z)=>{
    const drift=Math.sin(x*.19+z*.07)*Math.sin(z*.15-x*.11);
    const patch=Math.cos(x*.47+z*.31)*.012;
    return [.91+drift*.035+patch,.95+drift*.025+patch,1.0+drift*.012];
  });
"""
new_terrain = """  // Smooth, deterministic winter terrain: broad landforms, smaller wind-shaped
  // undulations, and a level foundation around the bakery. The same height
  // function drives the rendered grid, path geometry, props, and first-person collision.
  const terrainSmooth=t=>{t=clamp01(t);return t*t*(3-2*t);};
  function terrainHash(ix,iz){const n=Math.sin(ix*127.1+iz*311.7)*43758.5453123;return n-Math.floor(n);}
  function terrainValueNoise(x,z){
    const ix=Math.floor(x),iz=Math.floor(z),fx=terrainSmooth(x-ix),fz=terrainSmooth(z-iz);
    const a=terrainHash(ix,iz),b=terrainHash(ix+1,iz),c=terrainHash(ix,iz+1),d=terrainHash(ix+1,iz+1);
    const top=a+(b-a)*fx,bottom=c+(d-c)*fx;
    return top+(bottom-top)*fz;
  }
  const snowDriftSites=[
    [-29,18,10,15,.42],[28,5,12,16,.36],[-34,-29,13,16,.38],
    [31,-43,12,17,.42],[-9,36,16,9,.27],[22,-17,8,10,.23],
    [-43,-2,8,13,.22],[43,-24,9,13,.24]
  ];
  function terrainNaturalHeight(x,z){
    const broad=(terrainValueNoise(x*.026+8,z*.026-13)-.5)*1.25;
    const rolling=(terrainValueNoise(x*.061-21,z*.061+7)-.5)*.48;
    const windDetail=(terrainValueNoise(x*.145+43,z*.145-31)-.5)*.13;
    let h=-.10+broad+rolling+windDetail;
    for(const [cx,cz,rx,rz,amp] of snowDriftSites){
      const dx=(x-cx)/rx,dz=(z-cz)/rz;
      h+=amp*Math.exp(-(dx*dx+dz*dz)*1.45);
    }
    return h;
  }
  const terrainHeight=(x,z)=>{
    const natural=terrainNaturalHeight(x,z);
    const padDistance=Math.hypot((x-5)/7.8,(z+24)/6.8);
    const padBlend=1-terrainSmooth((padDistance-.92)/.40);
    return natural*(1-padBlend)+.05*padBlend;
  };
  // The final approach gently bends toward the bakery entrance, so the path
  // and its snow shoulders meet the building instead of ending off to one side.
  const pathCenter=(t)=>{
    const original=Math.sin(t*5.3)*5+Math.sin(t*12)*.55;
    const approach=terrainSmooth((t-.42)/.58);
    return original*(1-approach)+5*approach;
  };
  const terrain=planeGrid(160,144,terrainHeight,(x,z)=>{
    const broad=terrainValueNoise(x*.045+12,z*.045-9)-.5;
    const fine=terrainValueNoise(x*.13-17,z*.13+25)-.5;
    const shade=broad*.075+fine*.026;
    return [.91+shade,.95+shade*.78,.985+shade*.42];
  });
"""
main = replace_once(main, old_terrain, new_terrain, 'natural terrain heightfield')
main = main.replace('steps=120;', 'steps=160;', 1)
main = main.replace('steps=120,offsets=[2.0,2.45,3.15]', 'steps=160,offsets=[2.0,2.45,3.15]', 1)

old_shell = """  // A small first-pass timber bakery/cabin at the end of the approach.
  const bx=5,bz=-24,by=.05;
  add(box,[bx,by+2.1,bz],[9,4.2,7],[.25,.19,.15]);
  // The cabin interior is not built yet, so the complete footprint is solid for now.
  addBoxCollider(bx-4.5,bx+4.5,bz-3.5,bz+3.5,'cabin');
"""
new_shell = """  // Timber bakery at the end of the approach, with a walkable furnished interior.
  const bx=5,bz=-24,by=.05;
  // Raised timber floor and separate wall sections leave the front doorway open.
  add(box,[bx,by+.10,bz],[8.72,.20,6.72],[.17,.12,.085]);
  add(box,[bx,by+2.20,bz+3.39],[8.9,4.0,.22],[.25,.19,.15]);
  add(box,[bx-4.39,by+2.20,bz],[.22,4.0,6.8],[.25,.19,.15]);
  add(box,[bx+4.39,by+2.20,bz],[.22,4.0,6.8],[.25,.19,.15]);
  const frontWallZ=bz-3.39;
  add(box,[bx-2.95,by+2.20,frontWallZ],[3.1,4.0,.22],[.25,.19,.15]);
  add(box,[bx+2.95,by+2.20,frontWallZ],[3.1,4.0,.22],[.25,.19,.15]);
  add(box,[bx,by+3.55,frontWallZ],[2.8,1.3,.22],[.25,.19,.15]);
  // Room-aware wall collision preserves a clear 2.8m entrance opening.
  addBoxCollider(bx-4.52,bx+4.52,bz+3.24,bz+3.54,'bakery rear wall');
  addBoxCollider(bx-4.54,bx-4.24,bz-3.55,bz+3.55,'bakery left wall');
  addBoxCollider(bx+4.24,bx+4.54,bz-3.55,bz+3.55,'bakery right wall');
  addBoxCollider(bx-4.52,bx-1.40,bz-3.55,bz-3.24,'bakery front left wall');
  addBoxCollider(bx+1.40,bx+4.52,bz-3.55,bz-3.24,'bakery front right wall');
"""
main = replace_once(main, old_shell, new_shell, 'bakery floor and open wall shell')
main = replace_once(
    main,
    "for(const x of [bx-4.45,bx+4.45])for(const z of [bz-3.45,bz+3.45])add(box,[x,by+2.1,z],[.25,4.3,.25],[.12,.09,.075]);",
    "for(const x of [bx-4.45,bx+4.45])for(const z of [bz-3.45,bz+3.45])add(box,[x,by+2.2,z],[.25,4.0,.25],[.12,.09,.075]);",
    'bakery corner posts'
)
old_siding = """  for(let y=.65;y<4.1;y+=.48){add(box,[bx,by+y,bz-3.57],[8.8,.075,.13],[.34,.23,.16]);add(box,[bx,by+y,bz+3.57],[8.8,.075,.13],[.34,.23,.16]);}
"""
new_siding = """  for(let y=.65;y<4.1;y+=.48){
    add(box,[bx,by+y,bz+3.57],[8.8,.075,.13],[.34,.23,.16]);
    add(box,[bx-2.95,by+y,bz-3.57],[3.0,.075,.13],[.34,.23,.16]);
    add(box,[bx+2.95,by+y,bz-3.57],[3.0,.075,.13],[.34,.23,.16]);
  }
"""
main = replace_once(main, old_siding, new_siding, 'front siding doorway clearance')
main = replace_once(
    main,
    "  add(box,[bx,by+1.4,bz-3.72],[1.5,2.8,.18],[.095,.065,.055]);",
    """  // The front door is swung open beside the entrance, not sealing the doorway.
  add(box,[bx+1.62,by+1.48,bz-3.43],[1.08,2.56,.14],[.095,.065,.055],{rot:[0,.88,0]});
  add(box,[bx+1.12,by+1.48,bz-3.91],[.10,.12,.08],[.72,.48,.20],{emissive:.25});
  for(const x of [bx-1.42,bx+1.42])add(box,[x,by+1.55,bz-3.56],[.18,3.1,.20],[.13,.095,.07]);
  add(box,[bx,by+3.14,bz-3.56],[2.95,.20,.20],[.13,.095,.07]);""",
    'open bakery entrance'
)

marker = "  // Signboard mounted on the front wall below the eaves, not floating above the roof."
interior = """  // Walkable bakery interior: service counter, pastry display, oven, shelves,
  // storage, and warm fixtures. Keep the middle aisle open from the doorway.
  add(box,[bx+3.25,by+.78,bz+.10],[1.35,1.36,3.35],[.20,.12,.075]);
  add(box,[bx+3.25,by+1.50,bz+.10],[1.52,.12,3.52],[.43,.28,.16]);
  add(box,[bx+3.25,by+1.62,bz-.92],[1.25,.12,1.12],[.16,.10,.065]);
  for(let i=0;i<4;i++){
    const pz=bz-1.08+i*.72;
    add(cyl,[bx+3.25,by+1.76,pz],[.19,.075,.16],[.72,.43,.20]);
    add(box,[bx+3.25,by+1.85,pz],[.11,.035,.10],[.40,.19,.09]);
  }
  addBoxCollider(bx+2.45,bx+4.02,bz-1.72,bz+1.92,'bakery service counter');
  // Back-wall bake oven with a dark opening and warm glowing interior.
  add(box,[bx-2.55,by+1.34,bz+2.92],[1.72,2.30,.54],[.18,.13,.095]);
  add(box,[bx-2.55,by+1.26,bz+2.62],[1.32,1.08,.10],[.055,.045,.04]);
  add(box,[bx-2.55,by+1.24,bz+2.55],[1.05,.76,.035],[.95,.34,.105],{emissive:.65});
  add(box,[bx-2.55,by+2.55,bz+2.65],[1.95,.16,.62],[.28,.17,.105]);
  addBoxCollider(bx-3.48,bx-1.62,bz+2.48,bz+3.18,'bakery oven');
  // Flour and ingredient storage on the rear-left side.
  for(let shelf=0;shelf<3;shelf++){
    const sy=by+1.0+shelf*.82;
    add(box,[bx-3.78,sy,bz+.65],[.22,.12,3.5],[.30,.20,.12]);
    for(let jar=0;jar<4;jar++)add(cyl,[bx-3.72,sy+.23,bz-.62+jar*.82],[.16,.32,.16],[.72,.65,.48]);
  }
  addBoxCollider(bx-4.08,bx-3.46,bz-1.72,bz+2.38,'bakery ingredient shelves');
  // Ceiling beams and warm hanging lamps make the room read as an interior.
  for(const z of [bz-1.8,bz+.65])add(box,[bx,by+4.02,z],[8.25,.18,.22],[.16,.105,.075]);
  for(const x of [bx-.9,bx+1.2]){
    add(box,[x,by+3.72,bz-.05],[.16,.22,.16],[.12,.09,.07]);
    add(box,[x,by+3.52,bz-.05],[.52,.16,.52],[1.0,.58,.25],{emissive:1.0});
  }
  // A small standing prep table sits left of the aisle.
  add(box,[bx-1.25,by+.72,bz+.05],[1.55,1.24,.95],[.25,.15,.09]);
  add(box,[bx-1.25,by+1.38,bz+.05],[1.72,.12,1.08],[.44,.29,.17]);
  addBoxCollider(bx-2.15,bx-.35,bz-.58,bz+.68,'bakery prep table');
"""
main = replace_once(main, marker, interior + marker, 'bakery interior furnishings')

main = replace_once(
    main,
    "  // A small first-pass timber bakery/cabin at the end of the approach.",
    "  // Timber bakery at the end of the approach, with a walkable furnished interior.",
    'bakery heading'
) if "  // A small first-pass timber bakery/cabin at the end of the approach." in main else main
main = main.replace("  // remains solid until the interior/doorway milestone.\n", "  // remains open at the entry.\n")
main = main.replace("  // walls. The wall body reaches y = by + 4.2 and x = bx +/- 4.5.\n", "  // walls. The separate wall panels meet at y = by + 4.2 and x = bx +/- 4.5.\n")

old_steps = """  for(let i=0;i<4;i++){
    const treadZ=bz-4.3-i*.65;
    const treadTop=terrainHeight(bx,treadZ)+(4-i)*.05;
    add(box,[bx,treadTop-.1,treadZ],[2.8,.2,1.05],[.47,.59,.68]);
  }
"""
new_steps = """  for(let i=0;i<4;i++){
    const treadZ=bz-5.25+i*.72;
    const treadTop=terrainHeight(bx,treadZ)+(i+1)*.05;
    add(box,[bx,treadTop-.1,treadZ],[2.8,.2,1.05],[.47,.59,.68]);
  }
"""
main = replace_once(main, old_steps, new_steps, 'bakery entrance steps')
main = replace_once(
    main,
    "  for(const [x,z] of lampPositions){addCircleCollider(x,z,.13,'lantern post');const y=.15+Math.sin(x*.11+z*.045)*.09+Math.cos(z*.13)*.06;add(trunk,[x,y+1.5,z],[.16,3,.16],[.16,.12,.09]);add(box,[x,y+2.8,z],[.72,.72,.72],[.13,.13,.16]);add(box,[x,y+2.8,z],[.48,.48,.48],lampGold,{emissive:1.1});add(box,[x,y+3.2,z],[.88,.12,.88],[.10,.11,.15]);lampLights.push([x,y+2.7,z]);}",
    "  for(const [x,z] of lampPositions){addCircleCollider(x,z,.13,'lantern post');const y=terrainHeight(x,z);add(trunk,[x,y+1.5,z],[.16,3,.16],[.16,.12,.09]);add(box,[x,y+2.8,z],[.72,.72,.72],[.13,.13,.16]);add(box,[x,y+2.8,z],[.48,.48,.48],lampGold,{emissive:1.1});add(box,[x,y+3.2,z],[.88,.12,.88],[.10,.11,.15]);lampLights.push([x,y+2.7,z]);}\n  lampLights.push([bx-.9,by+3.48,bz-.05],[bx+1.2,by+3.48,bz-.05]);",
    'bakery interior lighting'
)
old_stair = """    for(let i=0;i<4;i++){
      const treadZ=bz-4.3-i*.65;
      if(Math.abs(z-treadZ)<=.525){
        const treadTop=terrainHeight(bx,treadZ)+(4-i)*.05;
        if(top===null||treadTop>top)top=treadTop;
      }
    }
"""
new_stair = """    for(let i=0;i<4;i++){
      const treadZ=bz-5.25+i*.72;
      if(Math.abs(z-treadZ)<=.525){
        const treadTop=terrainHeight(bx,treadZ)+(i+1)*.05;
        if(top===null||treadTop>top)top=treadTop;
      }
    }
"""
main = replace_once(main, old_stair, new_stair, 'stair collision surface')
main = replace_once(
    main,
    "  function walkSurfaceHeight(x,z){\n    const base=terrainHeight(x,z);\n    const stairTop=stairSurfaceHeight(x,z);",
    "  function walkSurfaceHeight(x,z){\n    const base=terrainHeight(x,z);\n    const insideBakery=x>bx-4.18&&x<bx+4.18&&z>bz-3.18&&z<bz+3.18;\n    if(insideBakery)return by+.20;\n    const stairTop=stairSurfaceHeight(x,z);",
    'bakery interior walking surface'
)

main = main.replace(
    "if(e.code==='KeyE'&&entered)showToast('M2 forest benchmark: flowering sakura grove, upgraded conifers, snow-covered branches, and layered winter ground detail.');",
    "if(e.code==='KeyE'&&entered)showToast('Environment milestone: natural rolling snow terrain and a walkable timber bakery interior.');"
)
main_path.write_text(main, encoding='utf-8', newline='\n')

html = html_path.read_text(encoding='utf-8')
html = html.replace('Development Build 022', 'Development Build 024')
html = html.replace('DEVELOPMENT BUILD 020 · M2', 'DEVELOPMENT BUILD 024 · M3')
html = html.replace(
    'Every conifer now uses the final upright V52 spruce model, with a high-detail hero tree and optimized shared forest LOD.',
    'Walk across rolling wind-shaped snow and step inside the warm, newly walkable timber bakery.'
)
html = html.replace('Performance-optimized V52 spruce LODs · Build 022', 'Natural Snow Terrain & Walkable Bakery · Build 024')
html = html.replace('M2 · Forest benchmark', 'M3 · Environment buildout')
html = html.replace('M2 VISUAL BENCHMARK · DISTANCE-BASED V52 TREE DETAIL · BAKERY, NPC AI & WORLD EXPANSION STILL AHEAD', 'M3 ENVIRONMENT BUILDOUT · NATURAL SNOW TERRAIN · WALKABLE BAKERY INTERIOR')
html_path.write_text(html, encoding='utf-8', newline='\n')

changelog = """# Build 024 — Natural Snow Terrain and Walkable Bakery

## Environment update
- Replaced the low-amplitude periodic ground ripple with deterministic layered value-noise terrain and broad wind-built snow drifts.
- Increased terrain grid density and kept one shared height function for props, path geometry, and first-person ground collision.
- Flattened and blended a foundation pad under the bakery, and curved the final path approach toward its entrance.
- Replaced the solid cabin block with separate walls and a real open doorway.
- Added a raised interior floor, bakery service counter and pastry display, oven, ingredient shelves, prep table, ceiling beams, warm fixtures, and room-aware collision.
- Rebuilt the entrance stairs so their collision heights match the visible treads and the bakery floor.

## Preserved
- Existing V52 tree meshes and distance-based runtime LODs from the Build 022 playtest.
- Sakura grove, rocks, lanterns, snowfall settings, fog, controls, and overall scene layout outside the updated approach and building footprint.

## Validation distinction
- Automated JavaScript syntax, scene marker, terrain sampling, and archive integrity checks run in CI.
- First-person visual review of the new snowfield, walking the path, entering/exiting the bakery, and target-PC FPS still require hands-on review.
"""
(root / 'BUILD_024_CHANGELOG.md').write_text(changelog, encoding='utf-8', newline='\n')
(root / 'README.md').write_text("""# Winter World — Development Build 024

Browser-playable WebGL2 winter world focused on natural snow terrain and a walkable bakery interior.

## Run locally
1. Extract the playtest ZIP.
2. Open the `WinterWorld_Prototype` folder.
3. Open `index.html` in Chrome or Edge.
4. If local-file loading is blocked, run `py -m http.server 8000` in the folder and open `http://127.0.0.1:8000/`.

## Controls
- W, A, S, D or arrow keys: move
- Mouse: look around
- Shift: move faster
- Esc: release mouse / close settings
- Click scene: capture mouse
- F3: performance diagnostics

See `BUILD_024_CHANGELOG.md` for this milestone's environment changes.
""", encoding='utf-8', newline='\n')
(root / 'PROGRESS.md').write_text("""# Winter World — Development Progress

## Current milestone: Natural snow terrain and bakery
- Layered snow heightfield and broad drifts: implemented in Build 024 source.
- Bakery open doorway, room shell, interior furnishings, and room-aware collision: implemented in Build 024 source.
- Automated checks: pending CI build.
- First-person visual review and target-PC FPS: pending user review.

## Deferred
- Further V52 medium/far tree appearance tuning is deferred until this environment milestone is accepted.
""", encoding='utf-8', newline='\n')
