"""Casas da Capital (Modular Medieval House Pack 06, hreikin sobre o Modular Medieval Building Pack de Daniel
Andersson, CC0, opengameart.org/content/modular-medieval-house-pack-06): as 8 casas de sobrado thouse17 ... thouse24
viram House_Cap_1 ... House_Cap_8. Cada arquivo tem a casa montada de várias peças (andares, vigas, telhado, varandas,
portas e janelas); aqui elas se juntam numa malha só, com os materiais refeitos a partir das texturas embutidas
(o arquivo usa o renderizador antigo do Blender), escala de 0,74, frente para +Z (glTF), origem no centro da planta e
base em y = 0 (o chão do térreo; os pés das varandas ficam abaixo).
uso: build_capital_houses.py <pasta com thouse17.blend ... thouse24.blend> <pasta de saída>"""
import bpy, sys, os, difflib
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
SCALE = 0.74
for n in range(17, 25):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "thouse%d.blend" % n))
    for o in list(bpy.data.objects):
        if o.type != "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    imgs = {}
    for i in bpy.data.images:
        if i.packed_file:
            imgs[i.name.lower().replace(" ", "").replace(".jpg", "").split(".")[0]] = i
    def pick(name):
        key = name.lower().replace(" ", "").split(".")[0].replace("_001", "").replace("_005", "")
        if key in imgs:
            return imgs[key]
        close = difflib.get_close_matches(key, list(imgs), n=1, cutoff=0.6)
        return imgs[close[0]] if close else None
    for m in bpy.data.materials:
        img = pick(m.name)
        m.use_nodes = True
        nodes, links = m.node_tree.nodes, m.node_tree.links
        nodes.clear()
        o_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
        bsdf.inputs["Roughness"].default_value = 0.9
        if img:
            t = nodes.new("ShaderNodeTexImage")
            t.image = img
            links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    for img in set(imgs.values()):
        if max(img.size) > 256:
            img.scale(256, 256)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    me = obj.data
    me.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    # Planta e chão: o térreo (House2_Level1 + House5_Level1) vai de y = -4,3 a 4,4 e z = 0 a 2,6.
    me.transform(Matrix.Scale(SCALE, 4) @ Matrix.Translation(Vector((0, 0, 0))))
    obj.name = "House_Cap_%d" % (n - 16)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "House_Cap_%d.glb" % (n - 16)), export_format="GLB", export_image_format="JPEG")
    pts = [v.co for v in me.vertices]
    print("OK house", n - 16, [round(min(p[i] for p in pts), 1) for i in range(3)], [round(max(p[i] for p in pts), 1) for i in range(3)])
