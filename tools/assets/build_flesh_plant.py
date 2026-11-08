"""Planta Carnívora, no lugar dos Sapos Ácidos da Floresta: "Cartoon flesh-eating plant with animations" (Jungle Jim na Sketchfab, CC BY 4.0;
arquivo trazido pelo autor). Esqueleto de 22 ossos e duas animações longas (Attack1: bote; Roar: ergue a cabeça e abre a boca). O arquivo
tem ~500 mil polígonos em cinco pedaços; aqui cada pedaço é reduzido (o Decimate guarda os pesos dos ossos) até ~TARGET triângulos no total
e as texturas caem para MAX_TEX px. Nada mais muda (nem escala nem posição: regravar mexendo na raiz estragou animação de outro modelo);
a velocidade e o trecho parado ("speeds" e "idle_clip" da família flesh_plant) são acertados no jogo, em game/actors/monster_model.gd.
Obs.: o Roar não tem todos os canais dos ossos (no jogo a planta deita); o jogo usa só o Attack1.
uso: blender -b --python tools/assets/build_flesh_plant.py -- <cartoon_flesh-eating_plant.glb> <saída.glb>"""
import bpy, sys
src, out = sys.argv[sys.argv.index("--") + 1:][:2]
TARGET, MAX_TEX = 9000, 512
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Icosphere")]:
    bpy.data.objects.remove(o, do_unlink=True)  # a esfera que o importador cria para desenhar os ossos
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
total = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
for obj in meshes:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = TARGET / total
    bpy.ops.object.modifier_move_to_index(modifier="dec", index=0)   # antes do esqueleto: reduz a malha de repouso
    bpy.ops.object.modifier_apply(modifier="dec")
for image in bpy.data.images:
    w, h = image.size
    if max(w, h) > MAX_TEX:
        s = MAX_TEX / max(w, h)
        image.scale(max(1, int(w * s)), max(1, int(h * s)))
print("planta", sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes), "tri;", [a.name for a in bpy.data.actions])
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
