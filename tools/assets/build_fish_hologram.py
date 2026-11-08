"""Holograma de peixes da Chuva Curativa ("Fish Hologram", Pat Sipes, Sketchfab, CC BY 4.0; arquivo trazido pelo autor): seis peixes nadando em volta
de uma coluna de oito anéis em espiral; animação de objetos (os peixes giram, Take 001, ~24 s em laço), sem esqueleto.
Aqui: as texturas vão a 512 px (WEBP), a animação vira "swim", e o vazio do topo (que a animação não mexe) põe o eixo da espiral em x = z = 0, a base
em y = 0 e a coluna com 1 m de altura (game/combat/spell_fx.gd a aumenta ao tamanho da área e a desenha como luz somada).
uso: blender -b -P tools/assets/build_fish_hologram.py -- <fish_hologram.glb> <saída: assets/models/fx/fish_hologram.glb>"""
import bpy, sys
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in [o for o in bpy.data.objects if o.type == "MESH" and not o.data.polygons]:
    bpy.data.objects.remove(o, do_unlink=True)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
tops = {o for o in bpy.data.objects if o.parent is None}
for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, 512)
act = bpy.data.actions[0]
act.name = "swim"
act.use_fake_user = True
bpy.context.scene.frame_set(int(act.frame_range[0]))
bpy.context.view_layer.update()
rings = [o for o in meshes if o.name.startswith("swirl")]
pts_r = [o.matrix_world @ Vector(c) for o in rings for c in o.bound_box]
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
axis = Vector(((min(p.x for p in pts_r) + max(p.x for p in pts_r)) / 2, (min(p.y for p in pts_r) + max(p.y for p in pts_r)) / 2, 0))
z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
k = 1.0 / (z1 - z0)
fix = Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-axis.x, -axis.y, -z0)))
for t in tops:
    t.matrix_world = fix @ t.matrix_world
bpy.context.view_layer.update()
print("OK fish hologram: altura %.1f no arquivo -> 1 m, %d objetos, %d triângulos" % (z1 - z0, len(meshes), sum(len(o.data.polygons) for o in meshes)))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85,
                          export_animation_mode="ACTIONS", export_force_sampling=True)
