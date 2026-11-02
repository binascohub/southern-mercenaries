"""Lava Spawn do Invocador (Lava Spawn animated, hwoarangmy, CC-BY-SA 3.0, opengameart.org/content/lava-spawn-animated; arte original do Ancient Beast: Magma Spawn,
Gabriel Verdon e Katarzyna Zalecka; modelo de piacenti): o .blend do pacote (rigado, 17 ossos, ações Idle/Walk/Attack1/Die/Flee/Dance/Happy/Sad/Sleep/TortureFire a 24 fps)
vira assets/models/props/LavaSpawn.glb só com a malha leve (LavaSpawn, ~3,6 mil triângulos; a HD de 70 mil fica de fora), o esqueleto e as animações, sem câmera
nem luz, textura de cor e brilho (emissão) a 1024 px, de frente para +Z do glTF (-Y do Blender) e com os pés em y = 0.
uso: blender -b -P tools/assets/build_lava_spawn_companion.py -- <"lava spawn.blend"> <saida.glb>"""
import bpy, sys, os, math

src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=src)
body = bpy.data.objects["LavaSpawn"]
arm = bpy.data.objects["Armature"]
for o in list(bpy.data.objects):
    if o not in (body, arm):
        bpy.data.objects.remove(o, do_unlink=True)
for im in bpy.data.images:
    if im.size[0] > 1024:
        im.scale(1024, 1024)
bones = arm.data.bones
head = arm.matrix_world @ bones["head"].head_local
base = arm.matrix_world @ bones["master"].head_local
tail = arm.matrix_world @ bones["tail2"].head_local
print("BONES head", tuple(round(x, 2) for x in head), "master", tuple(round(x, 2) for x in base), "tail2", tuple(round(x, 2) for x in tail))
# a cabeça precisa ficar para -Y do Blender (= +Z do glTF) em relação à ponta da cauda
dx, dy = head.x - tail.x, head.y - tail.y
print("FACING vector (head - tail)", round(dx, 2), round(dy, 2))
# gira em torno de Z para o vetor cauda -> cabeça apontar para -Y
angle = math.atan2(dx, -dy)  # ângulo a girar (Z) para (dx, dy) virar (0, -1)
arm.rotation_euler.z += -angle
bpy.context.view_layer.update()
pts = [body.matrix_world @ v.co for v in body.data.vertices]
low = min(p.z for p in pts)
arm.location.z -= low
bpy.context.view_layer.update()
print("DIMS", tuple(round(x, 2) for x in body.dimensions), "ACTIONS", [a.name for a in bpy.data.actions])
for a in bpy.data.actions:
    a.use_fake_user = True
for o in bpy.data.objects:
    o.select_set(o in (body, arm))
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='ACTIONS', export_skins=True, use_selection=True, export_force_sampling=True)
print("OK", dst)
