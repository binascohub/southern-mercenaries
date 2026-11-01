"""Águia (eagle.glb, fornecida pelo autor em ~/Downloads/assets/eagle.glb; autoria e licença a confirmar): o modelo original tem 444 mil vértices e 29 MB;
aqui ele é reduzido (Decimate, mantendo as UVs) para ~14 mil triângulos, as texturas vão para 512 px (JPG), e o bicho fica com a cabeça para +Z,
base em y = 0 e 0,5 m de comprimento de corpo (Eagle.glb). É o companheiro de Ar do Invocador (no lugar do pombo do Animal Kit).
uso: build_eagle.py <eagle.glb> <saída.glb> [graus de giro em torno do vertical, padrão 0]"""
import bpy, sys, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
spin = float(args[2]) if len(args) > 2 else 0.0
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
print("MESHES", [(o.name, len(o.data.polygons)) for o in meshes])
obj = meshes[0]
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
mod = obj.modifiers.new("Decimate", "DECIMATE")
mod.ratio = min(1.0, 14000.0 / max(len(obj.data.polygons), 1))
bpy.ops.object.modifier_apply(modifier=mod.name)
me = obj.data
me.transform(Matrix.Rotation(math.radians(spin), 4, "Z"))
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
print("DIMS", [round(x, 3) for x in (mx - mn)])
k = 0.5 / max(mx.x - mn.x, mx.y - mn.y)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
obj.name = "Eagle"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", use_selection=True)
print("OK eagle", len(me.polygons), [round(x * k, 2) for x in (mx - mn)])
