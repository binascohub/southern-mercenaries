"""Placas de cruzamento (Medieval Signs, AnyRPG, CC0, opengameart.org/content/medieval-signs): o poste (SignPost) com as quatro placas de madeira
(Sign1 a Sign4), em um só .glb (Signpost_Medieval.glb), com as madeiras do pacote (512 px), base em y = 0, centrado, 2,4 m de altura (escala 1,0).
Fica nos cruzamentos dos mapas ao ar livre (salas com 3 ou mais portas). Peças soltas do arquivo (Board, Post) ficam de fora.
uso: build_signposts.py <medievalsigns.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
deps = bpy.context.evaluated_depsgraph_get()
IMG = {"Wood": "WoodPlanksOld.jpg", "TreeLogEdgeWeathered": "TreeLogEdgeWeathered.jpg.001"}
imgs = {k: bpy.data.images[v] for k, v in IMG.items()}
parts = []
for name in ("SignPost", "Sign1", "Sign2", "Sign3", "Sign4"):
    o = bpy.data.objects[name]
    me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(o.matrix_world)
    parts.append((name, me, [m.name for m in o.data.materials]))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
pts = [v.co for _, me, _ in parts for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
fix = Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
mats = {}
def material(name):
    if name not in mats:
        m = bpy.data.materials.new("Sign_" + name)
        m.use_nodes = True
        nodes, links = m.node_tree.nodes, m.node_tree.links
        nodes.clear()
        o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.85
        t = nodes.new("ShaderNodeTexImage"); t.image = imgs.get(name, imgs["Wood"])
        if max(t.image.size) > 512:
            t.image.scale(512, 512)
        links.new(t.outputs["Color"], b.inputs["Base Color"])
        mats[name] = m
    return mats[name]
for name, me, slots in parts:
    me.transform(fix)
    me.materials.clear()
    for s in slots or ["Wood"]:
        me.materials.append(material(s))
    ob = bpy.data.objects.new("Sign_" + name, me)
    bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK signpost", [round(x, 2) for x in (mx - mn)])
