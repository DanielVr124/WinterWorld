import base64
import json
import os

import bpy
import numpy as np

def env_required(key):
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value

input_glb = env_required("V52_INPUT_GLB")
output_js = env_required("V52_OUTPUT_JS")
output_stats = env_required("V52_OUTPUT_STATS")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=input_glb)

ratios = {
    "Spruce_Trunk_Bark": 1.0,
    "Spruce_Primary_Secondary_Boughs": 0.45,
    "Spruce_Settled_Snow_Patches": 0.025,
    "Spruce_Individual_Needles": 0.12,
}

objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if len(objects) != 4:
    raise RuntimeError(f"Expected 4 V52 mesh components, found {len(objects)}: {[o.name for o in objects]}")

parts = []
component_stats = {}
total_source_triangles = 0
total_output_triangles = 0

for obj in objects:
    name = obj.name
    ratio = next((v for key, v in ratios.items() if key in name), None)
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
        modifier = obj.modifiers.new(name="V52 WebGL2 Game LOD", type="DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = ratio
        modifier.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)

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
        accum = np.zeros((vertex_count, 4), dtype=np.float64)
        counts = np.zeros(vertex_count, dtype=np.float64)
        if color_attr.domain == "POINT":
            raw = np.asarray([tuple(item.color) for item in color_attr.data], dtype=np.float64)
            colors[:, :] = raw[:, :3]
        else:
            for loop in mesh.loops:
                color = color_attr.data[loop.index].color
                accum[loop.vertex_index] += np.asarray(color, dtype=np.float64)
                counts[loop.vertex_index] += 1.0
            valid = counts > 0
            colors[valid] = (accum[valid, :3] / counts[valid, None]).astype(np.float32)

    world = obj.matrix_world.copy()
    normal_matrix = world.to_3x3().inverted().transposed()
    positions = np.empty((vertex_count, 3), dtype=np.float32)
    normals = np.empty((vertex_count, 3), dtype=np.float32)
    for index, vertex in enumerate(mesh.vertices):
        world_pos = world @ vertex.co
        world_normal = normal_matrix @ vertex.normal
        if world_normal.length > 1e-12:
            world_normal.normalize()
        positions[index] = (world_pos.x, world_pos.y, world_pos.z)
        normals[index] = (world_normal.x, world_normal.y, world_normal.z)

    colors = np.clip(colors, 0.0, 1.0)
    vertices = np.column_stack((positions, normals, colors)).astype(np.float32, copy=False)
    triangles = np.asarray([tuple(tri.vertices) for tri in mesh.loop_triangles], dtype=np.uint32)
    if triangles.size == 0:
        raise RuntimeError(f"Decimation removed every face from {name}")

    parts.append((vertices, triangles))
    output_triangles = int(len(triangles))
    total_output_triangles += output_triangles
    component_stats[name] = {
        "source_triangles": source_triangles,
        "game_triangles": output_triangles,
        "vertices": int(vertex_count),
        "decimate_ratio": ratio,
    }
    print(f"{name}: {source_triangles:,} -> {output_triangles:,} triangles, {vertex_count:,} vertices")

if not 180_000 <= total_output_triangles <= 450_000:
    raise RuntimeError(
        f"Optimized V52 game mesh has {total_output_triangles:,} triangles; "
        "expected 180,000–450,000 to balance detail and the existing GTX 1050 Ti target."
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
vertex_b64 = base64.b64encode(vertex_data.tobytes()).decode("ascii")
index_b64 = base64.b64encode(index_data.tobytes()).decode("ascii")

os.makedirs(os.path.dirname(output_js), exist_ok=True)
with open(output_js, "w", encoding="utf-8", newline="\n") as handle:
    handle.write("/* V52 hero spruce WebGL2 buffers. Generated from the final Blender/Cycles asset. */\n")
    handle.write("window.WinterWorldHeroSpruceV52Data = {\n")
    handle.write(f"  vertexCount: {len(vertex_data)},\n")
    handle.write(f"  triangleCount: {total_output_triangles},\n")
    handle.write(f'  vertices: "{vertex_b64}",\n')
    handle.write(f'  indices: "{index_b64}"\n')
    handle.write("};\n")

stats = {
    "source": os.path.basename(input_glb),
    "source_triangles": total_source_triangles,
    "game_triangles": total_output_triangles,
    "vertex_count": int(len(vertex_data)),
    "vertex_format": ["position_xyz", "normal_xyz", "color_rgb"],
    "components": component_stats,
    "placement": {"x": 10.0, "z": -4.0, "scale": 1.0},
    "integration": "One full V52 hero spruce anchors the near forest path; existing procedural conifers remain as background/understory species to preserve the Build 014 forest budget."
}
with open(output_stats, "w", encoding="utf-8") as handle:
    json.dump(stats, handle, indent=2)
print(f"V52 game LOD complete: {total_source_triangles:,} -> {total_output_triangles:,} triangles; {vertex_data.nbytes:,} vertex bytes + {index_data.nbytes:,} index bytes.")
