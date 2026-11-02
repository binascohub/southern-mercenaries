"""Pedras low-poly (Low Poly Rocks, para, CC0, opengameart.org/content/low-poly-rocks):
assets/models/maps/RockP_1..6.glb. O pacote só traz OBJ + normal maps gigantes (sem cor), então cada pedra
recebe um material cinza liso. Ficam em pé, base em y = 0, centradas em x/z, com ~1 m de altura.
uso: blender -b -P tools/assets/build_rocks_para.py -- <pasta com os .obj> assets/models/maps"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
HEIGHT = 1.0
NAMES = ["rock_c_01", "rock_d_01", "rock_d_02", "rock_d_03", "rock_d_05", "rock_d_06"]
for n, name in enumerate(NAMES, 1):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=os.path.join(src, name + ".obj"), forward_axis="NEGATIVE_Y", up_axis="Z")
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    mat = bpy.data.materials.new("RockP_%d" % n)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.36, 0.34, 0.31, 1)
    bsdf.inputs["Roughness"].default_value = 0.92
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
        o.data.polygons.foreach_set("use_smooth", [False] * len(o.data.polygons))
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
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "RockP_%d.glb" % n), export_format="GLB", use_selection=True, export_apply=False)
    print("OK RockP_%d (%s)  footprint %.2f x %.2f m" % (n, name, (mx.x - mn.x) * s, (mx.y - mn.y) * s))
