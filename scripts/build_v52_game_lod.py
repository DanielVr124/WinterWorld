import base64
import json
import math
import os
import random
import re

import bmesh
import bpy
import numpy as np


def env_required(key):
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


input_glb = env_required("V52_INPUT_GLB")
output_hero_js = env_required("V52_OUTPUT_HERO_JS")
output_forest_js = env_required("V52_OUTPUT_FOREST_JS")
output_forest_low_js = env_required("V52_OUTPUT_FOREST_LOW_JS")
output_stats = env_required("V52_OUTPUT_STATS")
output_preview = env_required("V52_OUTPUT_PREVIEW")

COMPONENT_RATIOS = {
    "Spruce_Trunk_Bark": 1.0,
    "Spruce_Primary_Secondary_Boughs": 0.35,
    "Spruce_Settled_Snow_Patches": 0.0045,
    "Spruce_Individual_Needles": 0.03,
}
FOREST_COMPONENT_RATIOS = {
    "Spruce_Trunk_Bark": 0.85,
    "Spruce_Primary_Secondary_Boughs": 0.25,
    "Spruce_Settled_Snow_Patches": 0.0045,
    "Spruce_Individual_Needles": 0.03,
}
FOREST_ISLAND_KEEP_PERCENT = {
    "Spruce_Settled_Snow_Patches": 9.0,
    "Spruce_Individual_Needles": 9.0,
}
FOREST_LOW_COMPONENT_RATIOS = {
    "Spruce_Trunk_Bark": 0.85,
    "Spruce_Primary_Secondary_Boughs": 0.10,
    "Spruce_Settled_Snow_Patches": 0.0045,
    "Spruce_Individual_Needles": 0.03,
}
FOREST_LOW_ISLAND_KEEP_PERCENT = {
    "Spruce_Settled_Snow_Patches": 3.5,
    "Spruce_Individual_Needles": 3.5,
}


def keep_connected_island_sample(obj, keep_percent, seed):
    """Keep whole snow/needle islands with coverage spread over the tree crown."""
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()

    remaining = set(bm.faces)
    components = []
    while remaining:
        first = remaining.pop()
        stack = [first]
        component = [first]
        while stack:
            face = stack.pop()
            for edge in face.edges:
                for neighbor in edge.link_faces:
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        stack.append(neighbor)
                        component.append(neighbor)
        components.append(component)

    input_face_count = len(bm.faces)
    target_faces = max(1, round(input_face_count * keep_percent / 100.0))
    rng = random.Random(seed)

    # A random global sample can leave whole crown sectors empty. Group each
    # connected island by its vertical band and azimuth sector, then round-robin
    # the groups so every side and height of the spruce keeps foliage/snow.
    if not mesh.vertices:
        raise RuntimeError("Cannot sample connected islands from an empty mesh")
    min_x = min(vertex.co.x for vertex in mesh.vertices)
    max_x = max(vertex.co.x for vertex in mesh.vertices)
    min_y = min(vertex.co.y for vertex in mesh.vertices)
    max_y = max(vertex.co.y for vertex in mesh.vertices)
    min_z = min(vertex.co.z for vertex in mesh.vertices)
    max_z = max(vertex.co.z for vertex in mesh.vertices)
    center_x = (min_x + max_x) * 0.5
    center_y = (min_y + max_y) * 0.5
    height = max(max_z - min_z, 1e-9)

    vertical_bands = 8
    azimuth_sectors = 12
    buckets = {}
    for component in components:
        component_vertices = {vertex for face in component for vertex in face.verts}
        count = max(1, len(component_vertices))
        cx = sum(vertex.co.x for vertex in component_vertices) / count
        cy = sum(vertex.co.y for vertex in component_vertices) / count
        cz = sum(vertex.co.z for vertex in component_vertices) / count
        band = min(vertical_bands - 1, max(0, int((cz - min_z) / height * vertical_bands)))
        angle = math.atan2(cy - center_y, cx - center_x)
        sector = int(((angle + math.pi) / (2.0 * math.pi)) * azimuth_sectors) % azimuth_sectors
        key = (band, sector)
        buckets.setdefault(key, []).append((len(component), rng.random(), component))

    # Prefer small individual needle/snow islands. Round-robin selection spreads
    # the limited triangle budget throughout the complete tree crown.
    for records in buckets.values():
        records.sort(key=lambda item: (item[0], item[1]))

    keys = sorted(buckets)
    cursors = {key: 0 for key in keys}
    kept_faces = []
    kept_face_count = 0
    selected_bins = set()

    while kept_face_count < target_faces:
        progressed = False
        for key in keys:
            records = buckets[key]
            cursor = cursors[key]
            while cursor < len(records):
                component_size, _, component = records[cursor]
                cursors[key] = cursor + 1
                if kept_face_count + component_size <= target_faces:
                    kept_faces.extend(component)
                    kept_face_count += component_size
                    selected_bins.add(key)
                    progressed = True
                    break
                cursor += 1
        if not progressed:
            break

    if not kept_faces and components:
        smallest = min(components, key=len)
        kept_faces.extend(smallest)
        kept_face_count = len(smallest)

    kept_set = set(kept_faces)
    discarded = [face for face in bm.faces if face not in kept_set]
    if discarded:
        bmesh.ops.delete(bm, geom=discarded, context="FACES")
    loose_edges = [edge for edge in bm.edges if not edge.link_faces]
    if loose_edges:
        bmesh.ops.delete(bm, geom=loose_edges, context="EDGES")
    loose_vertices = [vertex for vertex in bm.verts if not vertex.link_edges]
    if loose_vertices:
        bmesh.ops.delete(bm, geom=loose_vertices, context="VERTS")

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    mesh.calc_loop_triangles()
    output_triangles = len(mesh.loop_triangles)
    retained_islands = sum(
        1 for component in components if all(face in kept_set for face in component)
    )
    return {
        "method": "stratified_vertical_azimuth_whole_connected_islands",
        "source_islands": len(components),
        "retained_islands": retained_islands,
        "source_faces": input_face_count,
        "retained_faces": kept_face_count,
        "target_face_percent": keep_percent,
        "actual_face_percent": round((kept_face_count / max(1, input_face_count)) * 100.0, 3),
        "vertical_bands": vertical_bands,
        "azimuth_sectors": azimuth_sectors,
        "nonempty_spatial_bins": len(buckets),
        "selected_spatial_bins": len(selected_bins),
        "output_triangles": output_triangles,
    }

def write_mesh_lod(label, ratios, output_js, min_triangles, max_triangles):
    # Reimport for each LOD so the high-detail and forest reductions are both
    # derived independently from the untouched final V52 source meshes.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=input_glb)
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if len(objects) != 4:
        raise RuntimeError(
            f"Expected 4 V52 mesh components for {label}, found {len(objects)}: "
            f"{[obj.name for obj in objects]}"
        )

    parts = []
    component_stats = {}
    total_source_triangles = 0
    total_output_triangles = 0

    for obj in objects:
        name = obj.name
        ratio = next((value for key, value in ratios.items() if key in name), None)
        if ratio is None:
            raise RuntimeError(f"Unexpected V52 mesh component name: {name}")

        mesh = obj.data
        mesh.calc_loop_triangles()
        source_triangles = len(mesh.loop_triangles)
        total_source_triangles += source_triangles

        if ratio < 0.999:
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            modifier = obj.modifiers.new(name=f"V52 {label} LOD", type="DECIMATE")
            modifier.decimate_type = "COLLAPSE"
            modifier.ratio = ratio
            modifier.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier=modifier.name)

        island_sampling = None
        if label in ("Forest", "ForestLow") and name in FOREST_ISLAND_KEEP_PERCENT:
            keep_percent = (
                FOREST_LOW_ISLAND_KEEP_PERCENT[name]
                if label == "ForestLow"
                else FOREST_ISLAND_KEEP_PERCENT[name]
            )
            island_sampling = keep_connected_island_sample(
                obj,
                keep_percent,
                seed=sum(ord(char) for char in name),
            )

        mesh = obj.data
        mesh.update()
        mesh.calc_loop_triangles()

        color_attr = None
        if hasattr(mesh, "color_attributes") and len(mesh.color_attributes):
            color_attr = mesh.color_attributes.active_color or mesh.color_attributes[0]
        if color_attr is None and hasattr(mesh, "vertex_colors") and len(mesh.vertex_colors):
            color_attr = mesh.vertex_colors.active

        vertex_count = len(mesh.vertices)
        colors = np.ones((vertex_count, 3), dtype=np.float32)
        if color_attr is not None:
            if color_attr.domain == "POINT":
                raw = np.asarray(
                    [tuple(item.color) for item in color_attr.data],
                    dtype=np.float32,
                )
                colors[:, :] = raw[:, :3]
            else:
                accum = np.zeros((vertex_count, 3), dtype=np.float64)
                counts = np.zeros(vertex_count, dtype=np.float64)
                for loop in mesh.loops:
                    color = color_attr.data[loop.index].color
                    accum[loop.vertex_index] += np.asarray(color[:3], dtype=np.float64)
                    counts[loop.vertex_index] += 1.0
                valid = counts > 0
                colors[valid] = (accum[valid] / counts[valid, None]).astype(np.float32)

        world = obj.matrix_world.copy()
        normal_matrix = world.to_3x3().inverted().transposed()
        positions = np.empty((vertex_count, 3), dtype=np.float32)
        normals = np.empty((vertex_count, 3), dtype=np.float32)

        for index, vertex in enumerate(mesh.vertices):
            world_pos = world @ vertex.co
            world_normal = normal_matrix @ vertex.normal
            if world_normal.length > 1e-12:
                world_normal.normalize()

            # Blender's scene is Z-up; Winter World's WebGL scene is Y-up.
            # Rotate -90 degrees around X: (x, y, z) -> (x, z, -y).
            positions[index] = (world_pos.x, world_pos.z, -world_pos.y)
            normals[index] = (world_normal.x, world_normal.z, -world_normal.y)

        colors = np.clip(colors, 0.0, 1.0)
        vertices = np.column_stack((positions, normals, colors)).astype(
            np.float32, copy=False
        )
        triangles = np.asarray(
            [tuple(triangle.vertices) for triangle in mesh.loop_triangles],
            dtype=np.uint32,
        )
        if triangles.size == 0:
            raise RuntimeError(f"Decimation removed every face from {name} ({label})")

        parts.append((vertices, triangles))
        output_triangles = int(len(triangles))
        total_output_triangles += output_triangles
        component_stats[name] = {
            "source_triangles": source_triangles,
            "game_triangles": output_triangles,
            "vertices": int(vertex_count),
            "decimate_ratio": ratio,
        }
        if island_sampling is not None:
            component_stats[name]["island_sampling"] = island_sampling
        print(
            f"{label} / {name}: {source_triangles:,} -> "
            f"{output_triangles:,} triangles, {vertex_count:,} vertices"
        )

    if not min_triangles <= total_output_triangles <= max_triangles:
        raise RuntimeError(
            f"{label} V52 LOD has {total_output_triangles:,} triangles; "
            f"expected {min_triangles:,}–{max_triangles:,}."
        )

    combined_vertices = []
    combined_indices = []
    vertex_offset = 0
    for vertices, triangles in parts:
        combined_vertices.append(vertices)
        combined_indices.append(triangles.reshape(-1) + vertex_offset)
        vertex_offset += len(vertices)

    vertex_data = np.concatenate(combined_vertices, axis=0).astype("<f4", copy=False)
    index_data = np.concatenate(combined_indices, axis=0).astype("<u4", copy=False)

    # Keep the lowest point on the snow root skirt at y=0 for clean terrain placement.
    min_y = float(np.min(vertex_data[:, 1]))
    max_y = float(np.max(vertex_data[:, 1]))
    vertex_data[:, 1] -= min_y
    height = max_y - min_y
    width = float(np.max(vertex_data[:, 0]) - np.min(vertex_data[:, 0]))
    depth = float(np.max(vertex_data[:, 2]) - np.min(vertex_data[:, 2]))
    if height <= max(width, depth):
        raise RuntimeError(
            f"{label} V52 is not upright after the Z-up to Y-up conversion: "
            f"height={height:.3f}, width={width:.3f}, depth={depth:.3f}"
        )

    vertex_b64 = base64.b64encode(vertex_data.tobytes()).decode("ascii")
    index_b64 = base64.b64encode(index_data.tobytes()).decode("ascii")
    os.makedirs(os.path.dirname(output_js), exist_ok=True)
    with open(output_js, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"/* V52 {label} spruce WebGL2 buffers; converted from Blender Z-up to WebGL Y-up. */\n")
        handle.write(f"window.WinterWorld{label}SpruceV52Data = {{\n")
        handle.write(f"  vertexCount: {len(vertex_data)},\n")
        handle.write(f"  triangleCount: {total_output_triangles},\n")
        handle.write(f'  vertices: "{vertex_b64}",\n')
        handle.write(f'  indices: "{index_b64}"\n')
        handle.write("};\n")

    stats = {
        "source": os.path.basename(input_glb),
        "lod": label,
        "source_triangles": total_source_triangles,
        "game_triangles": total_output_triangles,
        "vertex_count": int(len(vertex_data)),
        "vertex_format": ["position_xyz", "normal_xyz", "color_rgb"],
        "coordinate_conversion": {
            "source": "Blender Z-up",
            "game": "WebGL Y-up",
            "position_and_normal_mapping": "(x, y, z) -> (x, z, -y)",
            "ground_origin": "lowest vertex normalized to y=0",
        },
        "bounds_m": {
            "height": round(height, 5),
            "width": round(width, 5),
            "depth": round(depth, 5),
        },
        "components": component_stats,
    }
    return stats


hero_stats = write_mesh_lod(
    "Hero",
    COMPONENT_RATIOS,
    output_hero_js,
    min_triangles=180_000,
    max_triangles=900_000,
)
forest_stats = write_mesh_lod(
    "Forest",
    FOREST_COMPONENT_RATIOS,
    output_forest_js,
    min_triangles=105_000,
    max_triangles=115_000,
)
forest_low_stats = write_mesh_lod(
    "ForestLow",
    FOREST_LOW_COMPONENT_RATIOS,
    output_forest_low_js,
    min_triangles=40_000,
    max_triangles=45_000,
)

combined_stats = {
    "source": os.path.basename(input_glb),
    "coordinate_conversion": hero_stats["coordinate_conversion"],
    "hero_lod": hero_stats,
    "forest_lod": forest_stats,
    "forest_low_lod": forest_low_stats,
    "placement": {
        "hero": {"x": 10.0, "z": -4.0, "scale": 1.0},
        "forest": "Distance-selected V52 LODs: one dedicated showcase tree uses the full hero mesh; other mature trees use the medium mesh to 68m and the compact far mesh beyond 68m; small trees use the compact far mesh.",
    },
    "integration": (
        "Every conifer uses the same final V52 spruce source. Trees near the player use "
        "the full hero mesh, mid-distance trees use the fuller medium LOD, and far/small "
        "trees use the low LOD."
    ),
}
with open(output_stats, "w", encoding="utf-8") as handle:
    json.dump(combined_stats, handle, indent=2)

print(
    "V52 LODs complete: "
    f"hero {hero_stats['game_triangles']:,} triangles; "
    f"medium {forest_stats['game_triangles']:,} triangles; "
    f"far {forest_low_stats['game_triangles']:,} triangles; "
    f"upright height {hero_stats['bounds_m']['height']:.3f} m."
)

def render_lod_comparison_preview(hero_js, forest_js, forest_low_js, output_png):
    """Render the exported hero, medium, and far LOD buffers side-by-side."""
    def load_buffers(path):
        with open(path, "r", encoding="utf-8") as handle:
            source = handle.read()
        vertex_match = re.search(r'vertices: "([A-Za-z0-9+/=]+)"', source)
        index_match = re.search(r'indices: "([A-Za-z0-9+/=]+)"', source)
        if not vertex_match or not index_match:
            raise RuntimeError(f"Could not read mesh buffers from {path}")
        vertices = np.frombuffer(base64.b64decode(vertex_match.group(1)), dtype="<f4").reshape(-1, 9)
        indices = np.frombuffer(base64.b64decode(index_match.group(1)), dtype="<u4").reshape(-1, 3)
        return vertices, indices

    bpy.ops.wm.read_factory_settings(use_empty=True)

    def make_preview_mesh(label, path):
        vertices, indices = load_buffers(path)
        mesh = bpy.data.meshes.new(label + " preview mesh")
        mesh.from_pydata(vertices[:, :3].tolist(), [], indices.tolist())
        mesh.update()
        colors = mesh.color_attributes.new(name="V52Color", type="FLOAT_COLOR", domain="POINT")
        rgba = np.column_stack((vertices[:, 6:9], np.ones(len(vertices), dtype=np.float32))).astype(np.float32)
        colors.data.foreach_set("color", rgba.reshape(-1))
        try:
            mesh.normals_split_custom_set_from_vertices(vertices[:, 3:6].tolist())
        except Exception:
            pass
        for polygon in mesh.polygons:
            polygon.use_smooth = True
        material = bpy.data.materials.new(label + " vertex color material")
        material.use_nodes = True
        shader = material.node_tree.nodes.get("Principled BSDF")
        vertex_color = material.node_tree.nodes.new("ShaderNodeVertexColor")
        vertex_color.layer_name = "V52Color"
        material.node_tree.links.new(vertex_color.outputs["Color"], shader.inputs["Base Color"])
        shader.inputs["Roughness"].default_value = 0.82
        mesh.materials.append(material)
        return mesh

    hero_mesh = make_preview_mesh("V52 Hero near LOD", hero_js)
    forest_mesh = make_preview_mesh("V52 Forest medium LOD", forest_js)
    forest_low_mesh = make_preview_mesh("V52 Forest far LOD", forest_low_js)
    for label, mesh, x, scale in [
        ("Hero near LOD", hero_mesh, -8.0, 1.0),
        ("Forest medium LOD", forest_mesh, 0.0, 1.0),
        ("Forest far LOD", forest_low_mesh, 8.0, 1.0),
    ]:
        obj = bpy.data.objects.new(label, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = (x, 0.02, 0.0)
        obj.scale = (scale, scale, scale)

    ground_mesh = bpy.data.meshes.new("preview snow ground")
    ground_mesh.from_pydata(
        [(-18, 0, -10), (-18, 0, 10), (18, 0, 10), (18, 0, -10)],
        [],
        [(0, 1, 2, 3)],
    )
    ground_mesh.update()
    ground = bpy.data.objects.new("preview snow ground", ground_mesh)
    bpy.context.scene.collection.objects.link(ground)
    ground_material = bpy.data.materials.new("preview snow")
    ground_material.diffuse_color = (0.68, 0.76, 0.86, 1.0)
    ground.data.materials.append(ground_material)

    from mathutils import Vector
    def aim(obj, point):
        direction = Vector(point) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    bpy.ops.object.camera_add(location=(0.0, 10.0, 36.0))
    camera = bpy.context.object
    aim(camera, (0.0, 4.1, 0.0))
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 32.0
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(0.0, 13.0, 8.0))
    key = bpy.context.object
    key.data.energy = 2600
    key.data.shape = "DISK"
    key.data.size = 10
    aim(key, (0.0, 3.0, 0.0))
    bpy.ops.object.light_add(type="AREA", location=(12.0, 9.0, -8.0))
    fill = bpy.context.object
    fill.data.energy = 1500
    fill.data.size = 8
    aim(fill, (4.0, 3.0, 0.0))

    scene = bpy.context.scene
    world = bpy.data.worlds.new("V52 preview world")
    scene.world = world
    world.color = (0.12, 0.16, 0.22)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    scene.render.filepath = output_png
    bpy.ops.render.render(write_still=True)
    if not os.path.isfile(output_png) or os.path.getsize(output_png) < 50_000:
        raise RuntimeError("The Build 020 performance LOD comparison preview was not rendered.")
    print(f"Rendered actual V52 hero/medium/far performance LOD comparison: {output_png}")


render_lod_comparison_preview(
    output_hero_js,
    output_forest_js,
    output_forest_low_js,
    output_preview,
)
