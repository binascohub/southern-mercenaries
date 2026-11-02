"""Reduz um modelo escaneado/escultura pesado (fornecido pelo autor, sem animação) para uso no jogo: Decimate para ~N triângulos (mantendo as UVs), texturas de 512 px (JPG),
tamanho original (em metros), pés em y = 0 e centro da planta na origem. Usado nos animais da Fazenda: Llama_Farm.glb e Horse_Brown.glb (assets/models/characters/).
uso: blender -b -P reduce_scan_model.py -- <entrada.glb> <saída.glb> <nome> [triângulos, padrão 14000] [giro em graus em torno do vertical, padrão 0]"""
import bpy, sys, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out, name = args[0], args[1], args[2]
faces = float(args[3]) if len(args) > 3 else 14000.0
spin = float(args[4]) if len(args) > 4 else 0.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
obj = meshes[0]
print("ORIGINAL", obj.name, len(obj.data.polygons), "polígonos")
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
mod = obj.modifiers.new("Decimate", "DECIMATE")
mod.ratio = min(1.0, faces / max(len(obj.data.polygons), 1))
bpy.ops.object.modifier_apply(modifier=mod.name)
me = obj.data
me.transform(Matrix.Rotation(math.radians(spin), 4, "Z"))
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
me.transform(Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
obj.name = name
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", use_selection=True)
print("OK", name, len(me.polygons), [round(x, 2) for x in (mx - mn)])
