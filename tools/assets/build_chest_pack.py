"""Pacote de baús (chests.zip enviado pelo autor do projeto: chest_epic, chest_large, treasure_chest_medium e chest_small, cada um com baú, tampa aberta, ouro, sombra e teias, textura de cor e
brilho em TGA de 4096 px, materiais em Maya; autor/licença a confirmar). Para cada baú ficam o corpo, a tampa e o ouro (a sombra e as teias são planos transparentes que o jogo não usa),
com a cor e o brilho (emissão) a 512 px em WebP, na mesma largura de 0,9 m (a do Chest_Mini; a altura segue a proporção de cada um), centrados em x/z e com a base em y = 0.
Gera assets/models/props/Chest_Epic.glb, Chest_Large.glb, Chest_Medium.glb e Chest_Small.glb.
uso: blender -b -P tools/assets/build_chest_pack.py -- <pasta do pacote extraído (com models/ e textures/)> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix

pack, outdir = sys.argv[sys.argv.index("--") + 1:][:2]
CHESTS = {"Chest_Epic": ("chest_epic", "chest_epic"), "Chest_Large": ("chest_large", "chest_large"),
          "Chest_Medium": ("treasure_chest_medium", "chest_medium"), "Chest_Small": ("chest_small", "chest_small")}
SKIP = ("shadow", "spiderweb")
WIDTH = 0.9  # todos os baús do jogo têm a mesma largura (a do Chest_Mini)
for out_name, (fbx, tex) in CHESTS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(pack, "models", fbx + ".fbx"))
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or any(k in o.name.lower() for k in SKIP):
            bpy.data.objects.remove(o, do_unlink=True)
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']

    def load(suffix, srgb=True):
        img = bpy.data.images.load(os.path.join(pack, "textures", "%s_%s.tga" % (tex, suffix)))
        img.scale(512, 512)
        img.pack()
        if not srgb:
            img.colorspace_settings.name = "Non-Color"
        return img
    mat = bpy.data.materials.new("m_" + out_name.lower())
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.6
    col = nt.nodes.new("ShaderNodeTexImage")
    col.image = load("col")
    nt.links.new(col.outputs["Color"], bsdf.inputs["Base Color"])
    glow = nt.nodes.new("ShaderNodeTexImage")
    glow.image = load("glow")
    nt.links.new(glow.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 1.0
    for o in meshes:
        o.data.materials.clear()
        o.data.materials.append(mat)
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
    box = [Vector(v.co) for o in meshes for v in o.data.vertices]
    lo = Vector([min(v[i] for v in box) for i in range(3)])
    hi = Vector([max(v[i] for v in box) for i in range(3)])
    S = WIDTH / max(hi.x - lo.x, hi.y - lo.y)
    T = Matrix.Scale(S, 4) @ Matrix.Translation((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))
    for o in meshes:
        o.data.transform(T)
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    dst = os.path.join(outdir, out_name + ".glb")
    bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=False)
    print("OK", dst, [o.name for o in meshes], [round(x * S, 2) for x in (hi - lo)])
