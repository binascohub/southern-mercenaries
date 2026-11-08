"""Esqueleto sentado (Previous Victim Skeleton - Granny, Arthurzin, Sketchfab, CC-BY 4.0): a vítima de antes, sentada no chão com as pernas
esticadas, para encostar nas paredes das Catacumbas (tools/assets/build_catacombs.py). As quatro malhas viram uma, a textura (1024 -> 512 px, JPG)
fica, e o modelo sai com ~1,05 m de altura sentado, base em y = 0, centrado em x, as costas na origem e as pernas para -Z no glTF (a mesma
convenção do Prison_WallShackles: rotação 180 na parede norte, 270 na oeste, 90 na leste).
uso: blender -b -P tools/assets/build_seated_skeleton.py -- <previous_victim_skeleton_-_granny.glb> <saída: assets/models/maps/Skeleton_Seated.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT = 1.05
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
for o in meshes:  # tira os pais (os vazios do Sketchfab) guardando a posição no mundo
    mw = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = mw
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
ob.data.transform(ob.matrix_world)
ob.matrix_world = Matrix.Identity(4)
for o in list(bpy.data.objects):
    if o is not ob:
        bpy.data.objects.remove(o, do_unlink=True)
me = ob.data
me.transform(Matrix.Rotation(math.pi, 4, "Z"))  # o rosto (pernas) ia para -Y no Blender (+Z no glTF); vira +Y no Blender = -Z no glTF
pts = [v.co for v in me.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = HEIGHT / (mx.z - mn.z)
me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -mn.y, -mn.z))))  # costas (y mínimo) na origem
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
ob.name = "Skeleton_Seated"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", use_selection=False)
print("OK seated skeleton", [round(x * k, 2) for x in (mx - mn)], len(me.polygons), "faces")
