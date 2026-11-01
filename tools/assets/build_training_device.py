"""Aparelho de treino (Training Device, Danimal, CC-BY-SA 3.0, textura de metal CC0 de yughues, opengameart.org/content/training-device):
o boneco de treino com braços giratórios do Open Dungeons, com a animação do arquivo ("spin", em laço), 1,6 m de altura,
pés em y = 0, textura embutida em 512 px. Fica no pátio de treino da Capital (a peça gira sozinha: MonsterModel não entra,
é cenário de data/arenas.json "decor").
uso: build_training_device.py <TrainingDummy4.blend> <saída.glb>"""
import bpy, sys
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)
arm = bpy.data.objects["Armature"]
act = bpy.data.actions["ArmatureAction"]
act.name = "spin"
ad = arm.animation_data_create()
ad.action = None
track = ad.nla_tracks.new()
track.name = "spin"
track.strips.new("spin", int(act.frame_range[0]), act)
# O material do arquivo usa o sistema antigo (sem nós): refeito com a textura de cor.
tex = bpy.data.images["TrainingDummy4"]
for mat in bpy.data.materials:
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.6
    t = nodes.new("ShaderNodeTexImage"); t.image = tex
    links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
for img in bpy.data.images:
    if img.packed_file and max(img.size) > 512:
        img.scale(512, 512)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", export_animations=True, export_animation_mode="NLA_TRACKS")
print("OK training device")
