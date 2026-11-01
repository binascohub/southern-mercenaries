"""Diablous (Animated Diablous, Botanic / plankes-projects, CC-BY 3.0, opengameart.org/content/animated-diablous): o demônio
de chifres e asas, com o esqueleto e as animações do arquivo (Idle, Walk, Run, Attack, Hit, Die; a Idle_2 e a Pose ficam de fora),
renomeadas em minúsculas (uma faixa NLA cada); em unidades do arquivo (~19,6 de altura; a escala 0,0919 fica em MonsterModel), pés em y = 0, textura de cor
em 512 px. É o chefe final (Lúcifer, `lucifer` em data/monsters.json).
uso: build_diablous.py <pasta com diablous.blend e diablous_texture.png> <saída.glb>"""
import bpy, sys, os
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "diablous.blend"))
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = bpy.data.objects["Armature"]
mesh = bpy.data.objects["Cube"]
KEEP = {"Idle": "idle", "Walk": "walk", "Run": "run", "Attack": "attack", "Hit": "hit", "Die": "die"}
for act in list(bpy.data.actions):
    if act.name in KEEP:
        act.name = KEEP[act.name]
    else:
        bpy.data.actions.remove(act)
ad = arm.animation_data_create()
ad.action = None
for name in ("idle", "walk", "run", "attack", "hit", "die"):  # uma faixa NLA por animação (o exportador usa o nome da faixa)
    act = bpy.data.actions[name]
    track = ad.nla_tracks.new()
    track.name = name
    track.strips.new(name, int(act.frame_range[0]), act)
tex = bpy.data.images.load(os.path.join(src, "diablous_texture.png"))
tex.scale(512, 512)
mat = bpy.data.materials.new("Diablous")
mat.use_nodes = True
nodes, links = mat.node_tree.nodes, mat.node_tree.links
nodes.clear()
o_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
bsdf.inputs["Roughness"].default_value = 0.7
t = nodes.new("ShaderNodeTexImage"); t.image = tex
links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
mesh.data.materials.clear()
mesh.data.materials.append(mat)
bpy.context.view_layer.update()
pts = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
# O arquivo tem ~19,6 unidades de altura: no jogo a família "diablous" (MonsterModel) escala 1,8 / 19,58 para 1,8 m no tamanho 1.
arm.location = Vector((arm.location.x - (mn.x + mx.x) / 2, arm.location.y - (mn.y + mx.y) / 2, arm.location.z - mn.z))
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", export_animations=True,
                          export_animation_mode="NLA_TRACKS", export_force_sampling=True)
print("OK diablous", [round(x, 2) for x in (mx - mn)], "scale no jogo", round(1.8 / (mx.z - mn.z), 4))
