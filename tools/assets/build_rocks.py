"""Pedras da Floresta: assets/models/maps/Rock_1..5.glb (Rocks, Nobiax, CC0).
Cada pedra vem como OBJ + diffuse.tga em <pasta>/0N/; fica em pé, base em y = 0, centrada em x/z, com ~1 m de altura.
uso: blender -b -P tools/assets/build_rocks.py -- <pasta do pacote extraído> assets/models/maps"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
HEIGHT = 1.0
for n in range(1, 6):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    base = os.path.join(src, "%02d" % n)
    bpy.ops.wm.obj_import(filepath=os.path.join(base, "rock_%02d.obj" % n), forward_axis="NEGATIVE_Y", up_axis="Z")
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    mat = bpy.data.materials.new("Rock_%d" % n)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(base, "diffuse.tga"))
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    s = HEIGHT / (mx.z - mn.z)
    shift = Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
    for o in objs:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(shift)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Rock_%d.glb" % n), export_format="GLB", use_selection=True,
                              export_image_format="JPEG", export_apply=False)
    print("OK Rock_%d  footprint %.2f x %.2f m" % (n, (mx.x - mn.x) * s, (mx.y - mn.y) * s))
