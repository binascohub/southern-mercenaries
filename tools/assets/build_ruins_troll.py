"""Troll das Ruínas, chefe final das Ruínas ("The-Lord-Of-The-Rings-Troll-Walk.", bensimulator2 na Sketchfab, CC BY 4.0; arquivo trazido pelo autor):
o modelo vem com esqueleto próprio e só a animação de andar. Aqui a malha do corpo volta à pose de repouso (sem o esqueleto),
reduzida a ~45 mil triângulos, de pé em z = 0 com 2,6 m, texturas em no máximo 1024 px (WebP). Vai para assets/models/monsters/ruins_troll.glb;
tools/assets/rig_biped.py (perfil ruins_troll) a prende ao esqueleto dos heróis: ruins_troll_animated.glb, o que o jogo usa.
uso: blender -b --python tools/assets/build_ruins_troll.py -- <troll.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
HEIGHT = 2.6
TARGET = 45000
MAX_TEX = 1024
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
# Só o corpo: o arquivo traz uma esfera solta de ajuda e um pedaço de pano (402 polígonos, "TEX_pants") que só fica no lugar pela
# animação de andar; sem ela, ele cai no chão longe dos pés.
meshes = [o for o in bpy.data.objects if o.type == "MESH" and any(m.type == "ARMATURE" for m in o.modifiers) and len(o.data.polygons) > 1000]
for arm in [o for o in bpy.data.objects if o.type == "ARMATURE"]:
    arm.data.pose_position = "REST"  # aplica o esqueleto na pose de repouso: a calça, presa a um osso, vai para o lugar certo
bpy.context.view_layer.update()
for obj in meshes:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for mod in list(obj.modifiers):
        if mod.type == "ARMATURE":
            bpy.ops.object.modifier_apply(modifier=mod.name)
    world = obj.matrix_world.copy()
    obj.parent = None
    obj.data.transform(world)
    obj.matrix_world = Matrix.Identity(4)
for o in [o for o in bpy.data.objects if o not in meshes]:
    bpy.data.objects.remove(o, do_unlink=True)  # esqueleto, nós vazios, a esfera e o pano
bpy.ops.object.select_all(action="DESELECT")
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
if tris > TARGET:
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = TARGET / tris
    bpy.ops.object.modifier_apply(modifier="dec")
pts = np.array([v.co[:] for v in obj.data.vertices])
mn, mx = pts.min(axis=0), pts.max(axis=0)
obj.data.transform(Matrix.Translation(-Vector(((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]))))
obj.data.transform(Matrix.Scale(HEIGHT / (mx[2] - mn[2]), 4))
for poly in obj.data.polygons:
    poly.use_smooth = True
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        k = MAX_TEX / max(w, h)
        image.scale(max(1, int(w * k)), max(1, int(h * k)))
obj.name = "ruins_troll"
print("triângulos", sum(len(p.vertices) - 2 for p in obj.data.polygons), "tamanho", (mx - mn).round(1))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_image_format="WEBP", export_image_quality=80)
