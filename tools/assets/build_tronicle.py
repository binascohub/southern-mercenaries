"""Domo de energia das magias ("Tronicle", tamminen na Sketchfab, CC BY 4.0; arquivo trazido pelo autor do projeto): 128 cascas de icosfera girando e
pulsando numa animação de 10 s, com um material preto quase transparente (o brilho vinha dos reflexos do Sketchfab). Aqui fica uma casca a cada duas
(64, metade das chamadas de desenho, para vídeo integrado), com a animação de cada uma; o material é trocado no jogo (game/combat/spell_fx.gd, motivo
"star_seal": brilho aditivo na cor do elemento). Vai para assets/fx/tronicle.glb, com 4,8 m de diâmetro (raio 2,42).
uso: blender -b --python tools/assets/build_tronicle.py -- <tronicle.glb> <saída.glb>"""
import bpy, sys

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
shells = sorted([o for o in bpy.data.objects if o.type == "EMPTY" and o.name.startswith("Icosphere")], key=lambda o: o.name)
drop = shells[1::2]
for shell in drop:
    for child in list(shell.children):
        bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(shell, do_unlink=True)
for action in list(bpy.data.actions):
    if action.users == 0:
        bpy.data.actions.remove(action)
print("cascas", len(shells) - len(drop), "ações", len(bpy.data.actions))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=False, export_animations=True, export_materials="NONE")
