"""Garrafas e copos do Cups and bottles little pack (DREAM_SEARCH_REPEAT, CC0, opengameart.org/content/cups-and-bottles-little-pack; rótulos de imagens de domínio público):
cada peça do glasses.blend vira um .glb em assets/models/props, com altura real, centrada em x e y e a base em y = 0 do glTF. Os vidros do pacote são shaders próprios
(não vão para o glTF): aqui cada material é refeito (vidro colorido translúcido, rótulos com a textura do pacote a 512 px, rolha e tampa em cor lisa).
Glass_Bottle_{Wine,Whiskey,Champagne,Beer}, Glass_Cup_{Wine,Champagne,Martini}, Glass_Tumbler, Glass_Tumbler_Whiskey, Glass_Shot, Glass_Stein.
uso: blender -b -P tools/assets/build_glass_pack.py -- <glasses.blend> <pasta de saída>"""
import bpy, sys, os
import numpy as np
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=src)
# (objeto do .blend, nome do .glb, altura real em metros; a Tapa da cerveja é unida à garrafa)
PIECES = [("BotellaVino", "Glass_Bottle_Wine", 0.30), ("BotellaWiskey", "Glass_Bottle_Whiskey", 0.27), ("BotellaChampan", "Glass_Bottle_Champagne", 0.31),
          ("BotellaCerveza", "Glass_Bottle_Beer", 0.23), ("CopaVino", "Glass_Cup_Wine", 0.18), ("CopaChampan", "Glass_Cup_Champagne", 0.20),
          ("CopaMartini", "Glass_Cup_Martini", 0.13), ("VasoLargo", "Glass_Tumbler", 0.12), ("VasoWisky", "Glass_Tumbler_Whiskey", 0.09),
          ("VasoChico", "Glass_Shot", 0.07), ("Chop", "Glass_Stein", 0.14)]
for im in bpy.data.images:
    if im.size[0] > 512:
        im.scale(512, int(512 * im.size[1] / im.size[0]))
LABEL = {"BeerLabel": "vintage-beer-poster.jpg", "ChampanLabel": "french-poster-1673751663Cii.jpg", "ChampanUpperLabel": "champanTexture.png",
         "WineLabel": "vintage-advertisement-1683767933oxK.jpg"}
# nome do material -> (cor base, alfa, rugosidade, metálico)
FLAT = {"BeerBottle": ((0.20, 0.09, 0.02, 1), 0.82, 0.08, 0.0), "ChampangeBottle": ((0.03, 0.10, 0.04, 1), 0.88, 0.08, 0.0),
        "RedWineBottle": ((0.03, 0.07, 0.03, 1), 0.9, 0.08, 0.0), "YellowWiskeyBottle": ((0.75, 0.45, 0.08, 1), 0.7, 0.06, 0.0),
        "glassTraslucent": ((0.85, 0.92, 0.95, 1), 0.28, 0.03, 0.0), "paper": ((0.12, 0.10, 0.05, 1), 1.0, 0.8, 0.0), "Tap": ((0.05, 0.03, 0.02, 1), 1.0, 0.9, 0.0),
        "metal": ((0.55, 0.55, 0.55, 1), 1.0, 0.35, 0.9), "cap": ((0.75, 0.62, 0.20, 1), 1.0, 0.35, 0.8)}
for mat in bpy.data.materials:
    name = mat.name
    if name not in FLAT and name not in LABEL:
        continue
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    outn = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], outn.inputs["Surface"])
    if name in LABEL:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images[LABEL[name]]
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.6
    else:
        color, alpha, rough, metal = FLAT[name]
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Alpha"].default_value = alpha
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if alpha < 1.0:
            try:
                mat.surface_render_method = 'BLENDED'
            except Exception:
                pass
            try:
                mat.blend_method = 'BLEND'
            except Exception:
                pass
os.makedirs(out, exist_ok=True)
for obj_name, out_name, height in PIECES:
    src_obj = bpy.data.objects[obj_name]
    parts = [src_obj] + [o for o in bpy.data.objects if o.parent is src_obj and o.type == 'MESH']
    copies = []
    for p in parts:
        c = p.copy()
        c.data = p.data.copy()
        bpy.context.scene.collection.objects.link(c)
        c.parent = None
        c.data.transform(p.matrix_world)
        c.matrix_world = Matrix.Identity(4)
        copies.append(c)
    for o in bpy.data.objects:
        o.select_set(o in copies)
    bpy.context.view_layer.objects.active = copies[0]
    if len(copies) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    pts = np.array([v.co[:] for v in obj.data.vertices])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    s = height / (hi[2] - lo[2])
    obj.data.transform(Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]))))
    obj.data.transform(Matrix.Scale(s, 4))
    obj.name = out_name
    for o in bpy.data.objects:
        o.select_set(o is obj)
    print("PIECE", out_name, "height", height, "width", round((hi[0] - lo[0]) * s, 3), round((hi[1] - lo[1]) * s, 3))
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, out_name + ".glb"), export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=False)
    bpy.data.objects.remove(obj, do_unlink=True)
print("OK")
