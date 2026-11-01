"""Garrafas de vidro (Free Glass Bottles, Rakshi Games / Snabisch, CC-BY 3.0, opengameart.org/content/free-glass-bottles): as sete garrafas
(Bottle_Aqua, Blue, Green, Orange, Red, Violet, Yellow) em .glb, em vidro colorido translúcido (o arquivo usa o shader de vidro do Cycles, que não
exporta: aqui cada garrafa vira um material de vidro simples na mesma cor, 55% opaco e liso), de pé, base em y = 0, 0,32 m de altura
(a mais baixa, a violeta, 0,22 m), com o subdivisão aplicada. Para barracas, mesas e barris das cidades (Tortuga e Capital).
uso: build_bottles.py <Bottles.blend> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
NAMES = {"Glasspotaqua": "Aqua", "GlassPotBlue": "Blue", "GlassPotGreen": "Green", "Glasspotorange": "Orange", "GlassPotRed": "Red", "Glasspotviolet": "Violet", "GlassPotYellow": "Yellow"}
bpy.ops.wm.open_mainfile(filepath=src)
deps = bpy.context.evaluated_depsgraph_get()
parts = {}
for name, short in NAMES.items():
    o = bpy.data.objects[name]
    color = o.data.materials[0].diffuse_color[:3]
    me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(o.matrix_world)
    parts[short] = (me, color)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for short, (me, color) in parts.items():
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    k = (0.22 if short == "Violet" else 0.32) / (mx.z - mn.z)
    me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    for poly in me.polygons:
        poly.use_smooth = True
    mat = bpy.data.materials.new("Glass_" + short)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    b.inputs["Roughness"].default_value = 0.05
    b.inputs["Alpha"].default_value = 0.55
    b.inputs["Specular IOR Level"].default_value = 0.8
    if hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"
    me.materials.clear()
    me.materials.append(mat)
    ob = bpy.data.objects.new("Bottle_" + short, me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Bottle_%s.glb" % short), export_format="GLB", use_selection=True)
    bpy.data.objects.remove(ob, do_unlink=True)
    print("OK bottle", short, round((mx.z - mn.z) * k, 2))
