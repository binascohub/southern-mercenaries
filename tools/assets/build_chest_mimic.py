"""Mímico (chest_monster.glb enviado pelo autor do projeto: um baú-mímico de ferro e madeira com dentes, língua vermelha e espinhos, já com esqueleto de 14 ossos (a tampa e 9 pedaços de língua) e as animações
Attack, Idle e Run; autoria e licença a confirmar): monstro do Esgoto, espalhado por todo o mapa. Aqui só se reduz a textura a 1024 px (WebP) e se exporta de novo com as três animações como estão;
a frente (a boca) olha para -Y do Blender (+Z do glTF), com ~2 m de largura e a base em y = 0.
Gera assets/models/monsters/chest_mimic.glb.
uso: blender -b -P tools/assets/build_chest_mimic.py -- <chest_monster.glb> <saida.glb>"""
import bpy, sys

src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in list(bpy.data.objects):
    if o.name == "Icosphere":
        bpy.data.objects.remove(o, do_unlink=True)
for im in bpy.data.images:
    if im.size[0] > 1024 or im.size[1] > 1024:
        im.scale(1024, 1024)
print("AÇÕES", sorted(a.name for a in bpy.data.actions))
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
if arm.animation_data:
    arm.animation_data.action = None
    for tr in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(tr)
else:
    arm.animation_data_create()
for a in bpy.data.actions:
    tr = arm.animation_data.nla_tracks.new()
    tr.name = a.name
    tr.strips.new(a.name, int(a.frame_range[0]), a)
for o in bpy.data.objects:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True, export_animation_mode='NLA_TRACKS', export_skins=True, use_selection=True)
print("OK", dst)
