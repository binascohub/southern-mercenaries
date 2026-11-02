"""Porco-Tubarão (pork-shark.blend do autor): criatura de pé, de tronco largo e boca de tubarão, com esqueleto ("Creep", 55 ossos, com IK) e 17 animações. O arquivo
traz a malha completa (Body_lod0) e uma de menos polígonos (Body_lod1); fica só a completa. O .blend não vem com a textura (a LP_Main_BaseColor.png que ele cita
não está junto e nem está ligada ao material): sem uma imagem, a malha recebe uma cor lisa de pele (rosada e fosca); com a imagem, vai pelo UV dela.
As animações viram faixas NLA com os nomes do jogo: Idle1 -> idle, Walk1 -> walk, Bite -> attack, Damage -> hit, Death -> die; as outras ficam em minúsculas
(punch, roar, crouch, eating, sniff, walk2, idle2, sleep_*, jump_in, jump_out). 5,55 unidades de altura (pés em 0), frente em -Y (+Z no glTF).
uso: blender -b -P tools/assets/build_pork_shark.py -- <pork-shark.blend> <saida.glb> [textura.png]"""
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
src, out = a[:2]
texture = a[2] if len(a) > 2 else ""
bpy.ops.wm.open_mainfile(filepath=src)
arm = bpy.data.objects["Creep"]
body = bpy.data.objects["Body_lod0"]
for o in list(bpy.data.objects):
    if o not in (arm, body):
        bpy.data.objects.remove(o, do_unlink=True)
body.hide_set(False)
body.hide_viewport = False
body.hide_render = False
arm.hide_set(False)
# Material: textura (se houver) ou cor lisa.
mat = bpy.data.materials.new("PorkShark")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.85
if texture:
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(texture)
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
else:
    bsdf.inputs["Base Color"].default_value = (0.62, 0.45, 0.42, 1.0)
body.data.materials.clear()
body.data.materials.append(mat)
# Animações como faixas NLA com os nomes do jogo.
RENAME = {"Idle1_Action": "idle", "Walk1_Action": "walk", "Bite_Action": "attack", "Damage_Action": "hit", "Death_Action": "die",
          "Walk2_Action": "walk2", "Idle2_Action": "idle2", "JumpIn_Action": "jump_in", "JumpOut_Action": "jump_out"}
ad = arm.animation_data_create()
ad.action = None
for old_track in list(ad.nla_tracks):  # o arquivo já traz faixas "[Action Stash]" com as mesmas ações
    ad.nla_tracks.remove(old_track)
for act in list(bpy.data.actions):
    name = RENAME.get(act.name, act.name.replace("_Action", "").lower())
    act.name = name
    track = ad.nla_tracks.new()
    track.name = name
    track.strips.new(name, int(act.frame_range[0]), act)
bpy.context.scene.render.fps = 25
for o in bpy.context.view_layer.objects:
    o.select_set(False)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animation_mode="NLA_TRACKS", export_image_format="WEBP", export_image_quality=85,
                          use_selection=False, export_apply=False)
print("OK", out, [t.name for t in ad.nla_tracks])
