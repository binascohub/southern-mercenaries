"""Baú do mini-chefe (Treasure Chest, WeaponGuy / Supergeek, CC-BY 3.0, opengameart.org/content/treasure-chest): o baú de madeira com
tampa arredondada, aros e fechadura, em um só .glb (Chest_Mini.glb): texturas do arquivo (madeira, aros, bronze) em 512 px,
0,9 m de largura, base em y = 0, centrado, com a fechadura voltada para -Z (a peça é posta com um giro de 180° no jogo, "model" do prop "chest").
uso: build_chest_mini.py <treasurechest.blend> <saída.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
deps = bpy.context.evaluated_depsgraph_get()
IMG = {"Cube": "WoodPlanksBareWindmillCap.jpg", "Cylinder.001": "WoodPlanksBareWindmillCap.jpg", "Cylinder": "BarrelRingsUV.jpg",
       "Plane": "BronzeCopper0029_S.jpg", "Plane.001": "BronzeCopper0029_S.jpg"}
parts = []
for name, img_name in IMG.items():
    o = bpy.data.objects[name]
    me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(o.matrix_world)
    img = next(i for i in bpy.data.images if i.name.startswith(img_name[:20]))
    parts.append((name, me, img))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
pts = [v.co for _, me, _ in parts for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 0.9 / (mx.x - mn.x)
fix = Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
mats = {}
for name, me, img in parts:
    me.transform(fix)
    if img.name not in mats:
        m = bpy.data.materials.new("Chest_" + img.name[:12])
        m.use_nodes = True
        nodes, links = m.node_tree.nodes, m.node_tree.links
        nodes.clear()
        o_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
        bsdf.inputs["Roughness"].default_value = 0.7
        t = nodes.new("ShaderNodeTexImage"); t.image = img
        if max(img.size) > 512:
            img.scale(512, 512)
        links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        mats[img.name] = m
    me.materials.clear()
    me.materials.append(mats[img.name])
    ob = bpy.data.objects.new("Chest_" + name.replace(".", "_"), me)
    bpy.context.scene.collection.objects.link(ob)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG")
print("OK chest", [round(x * k, 2) for x in (mx - mn)])
