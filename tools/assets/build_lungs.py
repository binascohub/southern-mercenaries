"""Pulmões Humanos (Human Lungs, Scribe, CC0, opengameart.org/content/human-lungs): os dois pulmões e a traqueia na pose de repouso
(sem a batida do arquivo), em tom de carne, num .glb (Quest_Lungs.glb): de pé, base em y = 0, 0,4 m de altura. Item de missão do Padre da Capital.
uso: build_lungs.py <lung.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
deps = bpy.context.evaluated_depsgraph_get()
parts = []
for name in ("Lung L", "Lung R", "Trachea"):
    o = bpy.data.objects[name]
    me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(o.matrix_world)
    parts.append((name, me))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
pts = [v.co for _, me in parts for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 0.4 / (mx.z - mn.z)
fix = Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
COLORS = {"lung": (0.62, 0.18, 0.2, 1.0), "trachea": (0.78, 0.55, 0.5, 1.0)}
mats = {}
for key, color in COLORS.items():
    m = bpy.data.materials.new("Lungs_" + key)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = 0.35
    mats[key] = m
for name, me in parts:
    me.transform(fix)
    me.materials.clear()
    me.materials.append(mats["trachea" if name == "Trachea" else "lung"])
    ob = bpy.data.objects.new("Lungs_" + name.replace(" ", "_"), me)
    bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
print("OK lungs", [round(x * k, 2) for x in (mx - mn)])
