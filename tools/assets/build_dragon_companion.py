"""Dragão de Fogo do Invocador (Cethiel's Dragon 3D, Drummyfish a partir do dragão 2D de Cethiel, CC0, opengameart.org/content/cethiels-dragon-3d): o .blend do pacote
(dragon-2_80.blend, rigado, 32 ossos, ações Idle/Walk/Attack/Die a 24 fps) vira assets/models/props/Dragon.glb com o corpo e o esqueleto, sem os auxiliares
do cenário (chão, luz, planos), de frente para +Z do glTF (-Y do Blender) e com a pose de repouso assentada em y = 0. A textura é a original (dragon.png).
uso: blender -b -P tools/assets/build_dragon_companion.py -- <pasta do pacote extraído> <saida.glb>"""
import bpy, sys, os, math
from mathutils import Matrix

src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "dragon-2_80.blend"))
body = bpy.data.objects["dragon"]
arm = bpy.data.objects["Armature"]
for o in list(bpy.data.objects):
    if o not in (body, arm):
        bpy.data.objects.remove(o, do_unlink=True)
# a cabeça (jaw_upper) precisa ficar para -Y do Blender (= +Z do glTF)
bones = arm.data.bones
head_y = (body.matrix_world @ arm.matrix_world.inverted_safe() @ bones["jaw_upper"].head_local).y
base_y = (body.matrix_world @ arm.matrix_world.inverted_safe() @ bones["base"].head_local).y
print("HEAD Y", head_y, "BASE Y", base_y)
if head_y > base_y:
    body.rotation_euler.z += math.pi
bpy.context.view_layer.update()
pts = [(body.matrix_world @ v.co) for v in body.data.vertices]
low = min(p.z for p in pts)
body.location.z -= low  # pés (ponto mais baixo da pose de repouso) em z = 0
bpy.context.view_layer.update()
print("DIMS", tuple(body.dimensions), "ACTIONS", [a.name for a in bpy.data.actions])
for a in bpy.data.actions:
    a.use_fake_user = True
bpy.ops.object.select_all(action='DESELECT')
for o in (body, arm):
    o.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='ACTIONS', export_skins=True, use_selection=True, export_force_sampling=True)
print("OK", dst)
