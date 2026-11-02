"""Tesouro Antigo (trasure.rar + trasure-texture.rar enviados pelo autor do projeto: "Ancient Treasure", um monte de tesouro de 4,8 x 3,2 m — moedas, barras de ouro, baús, coroa, taças,
potes, escudo, espada — numa só malha de 1 milhão de polígonos com centenas de materiais repetidos, texturas JPG de ~2K; autor/licença a confirmar): enfeite da sala do chefe do Esgoto.
Aqui os materiais repetidos viram um só por textura (27), a malha cai a ~70 mil triângulos (Decimate), as texturas vão a 512 px (WebP), o monte fica centrado em x/z com a base em y = 0.
Gera assets/models/props/Ancient_Treasure.glb.
uso: blender -b -P tools/assets/build_ancient_treasure.py -- <Ancient Treasure.fbx> <pasta Texture> <saida.glb>"""
import bpy, sys, os
from mathutils import Vector

fbx, texdir, dst = sys.argv[sys.argv.index("--") + 1:][:3]
TRIS = 70000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx)
obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
for o in list(bpy.data.objects):
    if o is not obj:
        bpy.data.objects.remove(o, do_unlink=True)
obj.parent = None
bpy.context.view_layer.update()
obj.data.transform(obj.matrix_world)
obj.matrix_world = obj.matrix_world.Identity(4)

# materiais repetidos -> um por textura
by_image = {}
slot_of = []
for m in obj.data.materials:
    img = next((n.image.name for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None) if m.use_nodes else None
    key = img or m.name
    if key not in by_image:
        mat = bpy.data.materials.new(os.path.splitext(key)[0].replace("TX_", "M_").replace("_ALB", ""))
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = 0.55
        bsdf.inputs["Metallic"].default_value = 0.0
        path = os.path.join(texdir, key)
        if img and os.path.exists(path):
            im = bpy.data.images.load(path)
            if im.size[0] > 512 or im.size[1] > 512:
                im.scale(512, 512)
            im.pack()
            tex = nt.nodes.new("ShaderNodeTexImage")
            tex.image = im
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            print("SEM TEXTURA", key)
            bsdf.inputs["Base Color"].default_value = (0.8, 0.65, 0.2, 1)
        by_image[key] = mat
    slot_of.append(key)
keys = list(by_image)
new_index = [keys.index(k) for k in slot_of]
for p in obj.data.polygons:
    p.material_index = new_index[p.material_index]
obj.data.materials.clear()
for k in keys:
    obj.data.materials.append(by_image[k])
print("MATERIAIS", len(keys))

for o in bpy.data.objects:
    o.select_set(o is obj)
bpy.context.view_layer.objects.active = obj
mod = obj.modifiers.new("d", 'DECIMATE')
mod.ratio = min(1.0, TRIS / 2.0 / max(1, len(obj.data.polygons)))  # a malha é de quadriláteros: ~2 triângulos cada
bpy.ops.object.modifier_apply(modifier="d")
print("POLÍGONOS", len(obj.data.polygons))

# centrado em x/z (pela caixa), base em y = 0 (z do Blender)
bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
cx = (min(v.x for v in bb) + max(v.x for v in bb)) / 2
cy = (min(v.y for v in bb) + max(v.y for v in bb)) / 2
obj.data.transform(__import__("mathutils").Matrix.Translation((-cx, -cy, -min(v.z for v in bb))))
print("TAMANHO", [round(x, 2) for x in obj.dimensions])
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=False)
print("OK", dst)
