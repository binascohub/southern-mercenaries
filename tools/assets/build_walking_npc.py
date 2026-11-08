"""Moças andando no quarto do rei (Capital, sala king_bedroom): "Anna Ipati (animated)" e "Adriana Ilma (animated)", Jungle Jim na Sketchfab, CC BY 4.0
(arquivos trazidos pelo autor do projeto). São personagens do Character Creator (esqueleto CC_Base de ~100 ossos), de biquíni, com uma caminhada no lugar
de 18 s cujo primeiro quadro é a T-pose; os arquivos são enormes (Anna: 403 mil triângulos, 74 texturas, 336 MB).
Aqui:
 - saem o que não é a moça: o "shadow catcher" (esqueleto de 4 ossos com uma placa) e as malhas pedidas em --drop (a pistola da Adriana);
 - a malha é reduzida (~TARGET_TRIS triângulos no total) e as texturas vão a no máximo 512 px;
 - "walk" é a caminhada sem o quadro da T-pose; "idle" é uma pose só, a do quadro da caminhada com os pés mais juntos (para as paradas nas pontas);
 - fica com ~1,7 m, de pé no chão, olhando para -Y (+Z no glTF).
Vai para assets/models/characters/<nome>.glb (game/actors/npc_model.gd).
uso: blender -b --python tools/assets/build_walking_npc.py -- <arquivo.glb> <saída.glb> [--drop malha1,malha2]"""
import bpy, sys
import numpy as np
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[:2]
drop = args[args.index("--drop") + 1].split(",") if "--drop" in args else []
TARGET_TRIS = 40000
MAX_TEX = 512
HEIGHT = 1.7

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
rig = max((o for o in bpy.data.objects if o.type == "ARMATURE"), key=lambda o: len(o.data.bones))
doomed = set()
for o in bpy.data.objects:
    skinned_to = next((m.object for m in o.modifiers if m.type == "ARMATURE" and m.object), None) if o.type == "MESH" else None
    if skinned_to is not None and skinned_to is not rig:
        doomed.add(o.name)  # a placa do "shadow catcher" (o esqueleto pequeno fica: às vezes é o pai de tudo)
    elif o.name.startswith("Icosphere") or o.name in drop:
        doomed.add(o.name)
for name in doomed:
    bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
bodies = [o for o in bpy.data.objects if o.type == "MESH"]
total = sum(len(o.data.polygons) for o in bodies)
ratio = min(1.0, TARGET_TRIS / total)
for o in bodies:
    if len(o.data.polygons) < 600:
        continue  # olhos, lágrimas, língua: pequenos demais para reduzir
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    o.shape_key_clear()  # expressões do rosto: não são usadas, e o Decimate não aceita malha com shape keys
    mod = o.modifiers.new("dec", "DECIMATE")
    mod.ratio = ratio
    bpy.ops.object.modifier_move_to_index(modifier="dec", index=0)
    bpy.ops.object.modifier_apply(modifier="dec")
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        image.scale(max(1, w * MAX_TEX // max(w, h)), max(1, h * MAX_TEX // max(w, h)))
print("triângulos", total, "->", sum(len(o.data.polygons) for o in bodies))


def fcurves(action):
    if hasattr(action, "layers") and action.layers:
        return [fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
    return list(action.fcurves)


walk = max(bpy.data.actions, key=lambda a: a.frame_range[1] - a.frame_range[0])
for a in list(bpy.data.actions):
    if a is not walk:
        bpy.data.actions.remove(a)
walk.name = "walk"
walk.use_fake_user = True
f0, f1 = int(walk.frame_range[0]), int(walk.frame_range[1])
for fc in fcurves(walk):  # sai o quadro da T-pose
    for i in reversed(range(len(fc.keyframe_points))):
        if fc.keyframe_points[i].co.x < f0 + 0.5:
            fc.keyframe_points.remove(fc.keyframe_points[i])
rig.animation_data.action = walk
scene = bpy.context.scene

# Quadro com os pés mais juntos (entre os primeiros 3 s): vira a pose parada.
feet = [b.name for b in rig.pose.bones if b.name.endswith(("L_Foot", "R_Foot")) or "_L_Foot_" in b.name or "_R_Foot_" in b.name]
best = (1e9, f0 + 1)
for f in range(f0 + 1, min(f1, f0 + 72)):
    scene.frame_set(f)
    a, b = [rig.matrix_world @ rig.pose.bones[n].head for n in feet[:2]]
    d = (Vector((a.x, a.y, 0)) - Vector((b.x, b.y, 0))).length
    best = min(best, (d, f))
scene.frame_set(best[1])
idle = bpy.data.actions.new("idle")
idle.use_fake_user = True
pose = {p.name: (p.location.copy(), p.rotation_quaternion.copy(), p.scale.copy()) for p in rig.pose.bones}
rig.animation_data.action = idle
for p in rig.pose.bones:
    p.location, p.rotation_quaternion, p.scale = pose[p.name]
    for path in ("location", "rotation_quaternion", "scale"):
        p.keyframe_insert(path, frame=0)
print("pés", feet[:2], "pose parada do quadro", best[1])

# Tamanho: ~1,7 m de pé, centrado nos pés, no chão.
rig.animation_data.action = walk
scene.frame_set(best[1])
dg = bpy.context.evaluated_depsgraph_get()
pts = np.concatenate([np.array([o.matrix_world @ v.co for v in o.evaluated_get(dg).to_mesh().vertices]) for o in bodies])
mn, mx = pts.min(0), pts.max(0)
k = HEIGHT / (mx[2] - mn[2])
top = rig
while top.parent:
    top = top.parent
top.matrix_world = Matrix.Translation(Vector((-(mn[0] + mx[0]) / 2 * k, -(mn[1] + mx[1]) / 2 * k, -mn[2] * k))) @ Matrix.Scale(k, 4) @ top.matrix_world
rig.animation_data.action = idle
print("escala", round(k, 4), "altura original", round(float(mx[2] - mn[2]), 2))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_animations=True, export_animation_mode="ACTIONS",
                          export_image_format="AUTO", export_image_quality=82)  # WebP não aceita as texturas de um canal (transparência)
