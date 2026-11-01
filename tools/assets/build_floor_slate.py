"""Piso de pedra das salas do Cemitério: assets/models/maps/Floor_Slate.glb, a lajota do piso do Forte (Fort_Floor, de "3D Dungeon
Tileset", Skorpio, CC BY-SA 3.0; veja build_fort_tiles.py) refeita em 2 x 2 m para encaixar na grade de pisos de 2 m do motor (a
original mede 2 x 2,5 m e as fileiras se sobreporiam). A mesma textura e normal do Forte, esticadas 20% no comprimento.
Roda com o Python do Blender: blender -b -P tools/assets/build_floor_slate.py -- <assets/models/maps/fort/Fort_Floor.gltf> <saída.glb>"""
import bpy, sys
from mathutils import Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
assert len(meshes) == 1, [o.name for o in meshes]
obj = meshes[0]
obj.data.transform(obj.matrix_world)
obj.matrix_world = Matrix.Identity(4)
zs = [v.co.y for v in obj.data.vertices]          # (o glTF importado tem o comprimento em y do Blender)
length = max(zs) - min(zs)
obj.data.transform(Matrix.Diagonal((1.0, 2.0 / length, 1.0, 1.0)))     # 2,5 m -> 2 m
obj.name = "Floor_Slate"
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
xs = [v.co.x for v in obj.data.vertices]; ys = [v.co.y for v in obj.data.vertices]
print("OK Floor_Slate %.2f x %.2f m (era %.2f de comprimento)" % (max(xs) - min(xs), max(ys) - min(ys), length))
