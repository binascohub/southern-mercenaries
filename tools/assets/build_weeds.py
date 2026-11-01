"""Ervas daninhas da Floresta: assets/models/maps/Pl_Weed1..5.glb (Tiny Weeds, Nobiax, CC0).
Cada erva vem como OBJ + diffuse.tga (com recorte alfa) em <pasta>/0N/; fica em pé, base em y = 0, centrado em x/z.
uso: blender -b -P tools/assets/build_weeds.py -- <pasta do pacote extraído> assets/models/maps"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
HEIGHTS = {1: 0.5, 2: 0.45, 3: 0.45, 4: 0.45, 5: 0.5}  # 01 é o cardo (thistle), um pouco mais alto
for n, height in HEIGHTS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    base = os.path.join(src, "%02d" % n)
    bpy.ops.wm.obj_import(filepath=os.path.join(base, [f for f in os.listdir(base) if f.endswith(".obj")][0]), forward_axis="NEGATIVE_Y", up_axis="Z")
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    mat = bpy.data.materials.new("Pl_Weed%d" % n)  # mesmo material das outras plantas (Pl_*): textura com recorte alfa
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(base, "diffuse.tga"))
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    mat.blend_method = "CLIP" if hasattr(mat, "blend_method") else None  # (a translucency.tga do cardo não é usada)
    bsdf.inputs["Roughness"].default_value = 0.85
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    s = height / (mx.z - mn.z)
    shift = Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
    for o in objs:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(shift)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Pl_Weed%d.glb" % n), export_format="GLB", use_selection=True,
                              export_image_format="AUTO", export_apply=False)
    print("OK Pl_Weed%d  footprint %.2f x %.2f m" % (n, (mx.x - mn.x) * s, (mx.y - mn.y) * s))
