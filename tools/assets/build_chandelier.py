"""Lustre (Chandelier, Teh_Bucket, CC0, opengameart.org/content/chandelier-0): o corpo com as velas e a corrente (modificadores
aplicados), em metal escuro dourado e chamas que brilham. O ponto de pendurar fica em y = 0 e o lustre desce dali (no jogo
a peça é posta a 3,4 m do chão); 1,6 m de largura. Para a sala do rei da Capital.
uso: build_chandelier.py <chandelier-.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
deps = bpy.context.evaluated_depsgraph_get()
parts = []
for o in bpy.data.objects:
    if o.type == "MESH":
        me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        me.transform(o.matrix_world)
        parts.append((o.name, me, [m.name if m else "" for m in o.data.materials]))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
metal = bpy.data.materials.new("ChandelierMetal")
metal.use_nodes = True
b = metal.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.5, 0.33, 0.08, 1.0)
b.inputs["Metallic"].default_value = 0.5
b.inputs["Roughness"].default_value = 0.35
lamp = bpy.data.materials.new("ChandelierFlame")
lamp.use_nodes = True
l = lamp.node_tree.nodes["Principled BSDF"]
l.inputs["Base Color"].default_value = (0.9, 0.62, 0.25, 1.0)
l.inputs["Emission Color"].default_value = (1.0, 0.7, 0.25, 1.0)
l.inputs["Emission Strength"].default_value = 0.6
pts = [v.co for _, me, _ in parts for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 1.6 / max(mx.x - mn.x, mx.y - mn.y)
fix = Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mx.z)))
for name, me, mats in parts:
    me.transform(fix)
    me.materials.clear()
    for mname in mats or [""]:
        me.materials.append(lamp if mname == "lamp" else metal)
    ob = bpy.data.objects.new("Chandelier_" + name.replace(".", "_"), me)
    bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
print("OK chandelier", [round(x * k, 2) for x in (mx - mn)])
