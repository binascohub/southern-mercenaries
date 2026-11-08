"""Crocodilo Espinhoso do Pântano ("fantasy crocodile animation", hino na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): crocodilo de fantasia com
espinhos nas costas, 8 mil polígonos, esqueleto próprio de 70 ossos e as animações idle, walk, hit, attack, Attack01 e Death. O arquivo vem com ~5 cm:
aqui ele fica com 2,6 m de comprimento, de pé no chão (z = 0), centrado, olhando para -Y (+Z no glTF, a frente dos monstros no jogo), com a textura em
no máximo 1024 px (WebP). Vai para assets/models/monsters/fantasy_crocodile.glb (game/actors/monster_model.gd, família "fantasy_crocodile").
uso: blender -b --python tools/assets/build_fantasy_crocodile.py -- <fantasy_crocodile_animation.glb> <saída.glb>"""
import bpy, sys
import numpy as np
from mathutils import Matrix, Vector

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
LENGTH = 2.6
MAX_TEX = 1024
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.name.startswith("Icosphere"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
body = next(o for o in bpy.data.objects if o.type == "MESH")
top = next(o for o in bpy.data.objects if o.parent is None)
# O tamanho sai da pose parada (idle, quadro 0): é como ele fica no jogo.
arm.animation_data.action = bpy.data.actions["idle"]
bpy.context.scene.frame_set(0)
dg = bpy.context.evaluated_depsgraph_get()
pts = np.array([body.matrix_world @ v.co for v in body.evaluated_get(dg).to_mesh().vertices])
mn, mx = pts.min(0), pts.max(0)
k = LENGTH / (mx[1] - mn[1])
top.matrix_world = Matrix.Translation(Vector((-(mn[0] + mx[0]) / 2 * k, -(mn[1] + mx[1]) / 2 * k, -mn[2] * k))) @ Matrix.Scale(k, 4) @ top.matrix_world
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
pts = np.array([body.matrix_world @ v.co for v in body.evaluated_get(dg).to_mesh().vertices])
print("tamanho", (pts.max(0) - pts.min(0)).round(2), "chão", round(float(pts.min(0)[2]), 3))
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        image.scale(max(1, int(w * MAX_TEX / max(w, h))), max(1, int(h * MAX_TEX / max(w, h))))
print("ações", [(a.name, round(a.frame_range[1] - a.frame_range[0])) for a in bpy.data.actions])
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_animations=True, export_animation_mode="ACTIONS",
                          export_image_format="WEBP", export_image_quality=85)
