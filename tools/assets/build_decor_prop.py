"""Objeto de cenário a partir de um .glb do Sketchfab: junta as malhas, reduz para ~N vértices, peça por peça (os originais vêm com centenas de milhares a milhões),
põe o maior lado horizontal no tamanho real pedido, a base no chão (Z = 0 no Blender = Y = 0 no Godot) e o centro em X/Y; texturas em até 1024 px.
Usado para:
  Piano de cauda do quarto do rei ("Realistic Custom Concert Grand Piano", mert16art, CC-BY 4.0) -> Decor_Grand_Piano (2,7 m de comprimento, ~160 mil vértices)
  Varal de açougueiro com presunto e linguiças ("Butcher Meat Hook Rail - Cured Ham & Sausages", Pigcraft, CC-BY 4.0) -> Decor_Meat_Rail (2 m, ~200 mil)
  Cabra da Fazenda ("Realistic Domestic Goat - Curved Horns", Pigcraft, CC-BY 4.0) -> characters/goat_farm.glb (1,3 m, ~60 mil, giro 90: a cabeça para +Z)
  Dama nobre da igreja da Capital ("Noble Beauty", Chenchanchong, CC-BY 4.0) -> characters/noble_beauty.glb (h1.7: 1,7 m de altura, parada na pose do arquivo)
  Cidadão da Capital ("Горожанин 17 века в праздничной зимней одежде", Department Historical Information Science MSU, CC-BY 4.0) -> characters/townsman.glb (h1.75, ~40 mil)
uso: blender -b -P tools/assets/build_decor_prop.py -- <origem.glb> <saída.glb> <nome da peça> <maior lado horizontal em m, ou h<altura>> <vértices> [giro em graus]"""
import bpy, sys
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out, piece, target = args[0], args[1], args[2], int(args[4])
by_height = args[3].startswith("h")  # "h1.7": a medida é a altura (pessoas), não o maior lado horizontal
size = float(args[3].lstrip("h"))
yaw = float(args[5]) if len(args) > 5 else 0.0  # giro em graus em volta do eixo vertical (os animais andam olhando para +Z do Godot)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in meshes:
    o.data = o.data.copy()
    o.data.transform(o.matrix_world)
    o.parent = None
    o.matrix_world = Matrix.Identity(4)
for o in list(bpy.context.scene.objects):
    if o not in meshes:
        bpy.data.objects.remove(o, do_unlink=True)
# Reduz cada peça separadamente, na mesma proporção, antes de juntar: reduzir a malha já junta, e muito, despedaçava as peças finas (o piano virava cacos)
# e deformava a textura nas costuras.
total = sum(len(o.data.vertices) for o in meshes)
before = total
ratio = min(1.0, target / total)
if ratio < 1.0:
    for o in meshes:
        if len(o.data.vertices) < 2000:
            continue  # peças pequenas ficam inteiras
        bpy.context.view_layer.objects.active = o
        mod = o.modifiers.new("d", "DECIMATE")
        mod.ratio = ratio
        bpy.ops.object.modifier_apply(modifier="d")
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
obj = meshes[0]
me = obj.data
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = size / ((mx.z - mn.z) if by_height else max(mx.x - mn.x, mx.y - mn.y))
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
if yaw:
    me.transform(Matrix.Rotation(yaw * 3.14159265 / 180.0, 4, "Z"))
for image in bpy.data.images:
    if image.size[0] > 1024:
        image.scale(1024, 1024)
obj.name = me.name = piece
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=False, export_image_format="AUTO")
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
print("ok", piece, before, "->", len(me.vertices), "vértices; tamanho", [round(d, 2) for d in (mx - mn)])
