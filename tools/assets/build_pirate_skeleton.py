"""Esqueleto Pirata, mini-chefe das Docas no lugar do Tubarão-Porco: "Paragon Pirate Skeleton Sailor 35 animations" (Prizrakh na Sketchfab,
CC BY-NC 4.0; é o Gideon "Undertow" de Paragon, da Epic Games: ver a nota em CREDITS.md; arquivo trazido pelo autor).
O arquivo traz cinco níveis de detalhe sobrepostos (LOD0..LOD4) e 35 animações. Aqui fica só o LOD2 (~18 mil triângulos) e as animações que o
jogo usa (KEEP_ACTIONS); nada mais muda (nem escala nem posição: regravar mexendo na raiz estragou animação de outro modelo). A altura dos pés
é acertada no jogo ("lift" da família pirate_skeleton em game/actors/monster_model.gd).
uso: blender -b --python tools/assets/build_pirate_skeleton.py -- <paragon_pirate_skeleton.glb> <saída.glb>"""
import bpy, sys
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
LOD_MESHES = {"Object_%d" % i for i in range(22, 29)}          # LOD2: cabeça, corpo, pernas, leme, cracas, gancho, anel
KEEP_ACTIONS = {"Idle", "Run_Fwd", "Jog_Fwd", "Primary_Attack_A_Medium", "Primary_Attack_B_Medium", "Primary_Attack_C_Medium",
                "HitReact_Front", "Death_Fwd", "Cast", "Torn_Space"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.name not in LOD_MESHES]:
    bpy.data.objects.remove(o, do_unlink=True)      # os outros LODs e a esfera que o importador cria para desenhar os ossos
for action in [a for a in bpy.data.actions if a.name not in KEEP_ACTIONS]:
    bpy.data.actions.remove(action)
for obj in bpy.data.objects:                         # as faixas NLA que o importador cria apontam para as ações que saíram
    if obj.animation_data:
        for track in list(obj.animation_data.nla_tracks):
            if not any(s.action for s in track.strips):
                obj.animation_data.nla_tracks.remove(track)
# O brilho do anel mistura uma máscara (Image_14) num nó que o exportador não sabe gravar: a textura sai sem imagem e o Godot recusa o
# arquivo. Sem a máscara, o anel brilha por inteiro.
glow = bpy.data.materials.get("M_Gideon_Ring_Glow")
if glow:
    for node in [n for n in glow.node_tree.nodes if n.type == "TEX_IMAGE" and n.image and n.image.name == "Image_14"]:
        glow.node_tree.nodes.remove(node)
for image in [i for i in bpy.data.images if i.users == 0]:
    bpy.data.images.remove(image)
print("malhas", sorted(o.name for o in bpy.data.objects if o.type == "MESH"), "ações", sorted(a.name for a in bpy.data.actions))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
