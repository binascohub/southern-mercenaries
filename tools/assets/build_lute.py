"""Alaúde (Lute, aerojockey / Snabisch, CC0, opengameart.org/content/lute): o corpo (cuia), o braço, as cravelhas e as cordas, com as madeiras do pacote (256 px)
num .glb só (Lute.glb), deitado, com o braço para +X e as cordas para cima (+Y), 0,8 m de comprimento, centrado na origem. É o instrumento do
Bardo (no colo, no lugar do violão feito em código).
uso: build_lute.py <lute.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
deps = bpy.context.evaluated_depsgraph_get()
IMG = {"LuteWood": "light-softwood-2.jpg", "BowlWood": "medium-softwood-2.jpg", "NeckWood": "dark-softwood-2.jpg", "PegWood": "black-softwood-2.jpg", "LuteStrings": "lute-strings.png"}
parts = []
for o in bpy.data.objects:
    if o.type == "MESH":
        me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        me.transform(o.matrix_world)
        parts.append((o.name, me, [m.name for m in o.data.materials]))
imgs = {k: bpy.data.images[v] for k, v in IMG.items()}
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
pts = [v.co for _, me, _ in parts for v in me.vertices]
dims = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)]
long_axis = max(range(3), key=lambda i: dims[i])
mid = (max(p[long_axis] for p in pts) + min(p[long_axis] for p in pts)) / 2
other = [i for i in range(3) if i != long_axis]
def spread(sel):
    s = [p for p in sel]
    return max(max(q[other[0]] for q in s) - min(q[other[0]] for q in s), 1e-6) if s else 0
hi = [p for p in pts if p[long_axis] > mid]; lo = [p for p in pts if p[long_axis] <= mid]
neck_at_high = spread(hi) < spread(lo)
print("DIMS", [round(d, 2) for d in dims], "eixo longo", long_axis, "braço no lado alto:", neck_at_high)
# leva o eixo longo para X (braço para +X) e o menor eixo (espessura) para Z do Blender (glTF Y)
swap = {0: Matrix.Identity(4), 1: Matrix.Rotation(-1.5707963, 4, "Z"), 2: Matrix.Rotation(1.5707963, 4, "Y")}[long_axis]
flip = Matrix.Identity(4) if neck_at_high else Matrix.Rotation(3.1415926, 4, "Z")
for _, me, _ in parts:
    me.transform(flip @ swap)
pts = [v.co for _, me, _ in parts for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 0.8 / (mx.x - mn.x)
fix = Matrix.Scale(k, 4) @ Matrix.Translation(-(mn + mx) / 2)
mats = {}
def material(name):
    if name not in mats:
        m = bpy.data.materials.new("Lute_" + name)
        m.use_nodes = True
        nodes, links = m.node_tree.nodes, m.node_tree.links
        nodes.clear()
        o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.6
        t = nodes.new("ShaderNodeTexImage"); t.image = imgs.get(name, imgs["LuteWood"])
        links.new(t.outputs["Color"], b.inputs["Base Color"])
        mats[name] = m
    return mats[name]
for name, me, slots in parts:
    me.transform(fix)
    me.materials.clear()
    for s in slots or ["LuteWood"]:
        me.materials.append(material(s))
    ob = bpy.data.objects.new("Lute_" + name, me)
    bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK lute", [round(x * k, 2) for x in (mx - mn)])
