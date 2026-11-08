"""Esqueleto Bêbado das Docas (skeleton_pirate__the_drunk.glb: 'Skeleton Pirate "The Drunk"', FireGoat, CC BY 4.0, Sketchfab): esqueleto pirata com chapéu e garrafa,
com esqueleto próprio e só 2 animações (Default e DrunkWalk). Aqui as duas malhas (corpo e roupa/garrafa) são congeladas na pose de descanso, juntadas numa só, levadas
a metros (1,9 m, pés em z = 0, frente para -Y) e reduzidas (~35 mil triângulos, texturas até 1024 px). Vai para assets/models/monsters/skeleton_drunk.glb;
tools/assets/rig_biped.py (perfil skeleton_drunk) o prende ao esqueleto dos heróis: skeleton_drunk_animated.glb, o que o jogo usa.
uso: blender -b -P tools/assets/build_skeleton_drunk.py -- <skeleton_pirate__the_drunk.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Matrix, Vector

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT = 1.9
TARGET = 35000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
if arm.animation_data:
    arm.animation_data.action = None
for b in arm.pose.bones:
    b.matrix_basis.identity()
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
# os arquivos do Sketchfab vêm com o "em pé" no eixo Y depois da importação: (x, y, z) -> (x, -z, y), frente para -Y como os heróis
fix = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
parts = []
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.find_armature() is arm]:
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    me.transform(fix @ o.matrix_world)
    parts.append(bpy.data.objects.new(o.name + "_baked", me))
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
for o in parts:
    bpy.context.scene.collection.objects.link(o)
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
mod = obj.modifiers.new("dec", "DECIMATE")
mod.ratio = min(1.0, TARGET / len(obj.data.polygons))
bpy.ops.object.modifier_apply(modifier="dec")
pts = np.array([v.co[:] for v in obj.data.vertices])
mn, mx = pts.min(axis=0), pts.max(axis=0)
body = np.abs(pts[:, 0]) < (mx[0] - mn[0]) * 0.1  # o meio do corpo (a garrafa na mão não puxa o centro)
obj.data.transform(Matrix.Translation(-Vector((0.0, float(np.median(pts[body, 1])), mn[2]))))
obj.data.transform(Matrix.Scale(HEIGHT / (mx[2] - mn[2]), 4))
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        im.scale(1024, 1024)
obj.name = "skeleton_drunk"
pts = np.array([v.co[:] for v in obj.data.vertices])
print("TAMANHO", pts.min(axis=0).round(3), pts.max(axis=0).round(3), "POLÍGONOS", len(obj.data.polygons))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=85)
print("OK", out)
