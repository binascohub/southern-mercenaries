"""Defensor animado (Animated Defender aka Brigand, Danimal sobre o Brigand de anthonymyers, CC BY 3.0,
opengameart.org/content/animated-defender-aka-brigand): o guarda da Capital Real, com alabarda, couraça e as animações
do arquivo (walk, run, attack, death, scared, idle = a pose parada do primeiro quadro da caminhada). Texturas de cor em 1024 px (JPG); pés em y = 0.
uso: build_defender.py <Defender.blend> <saída.glb>"""
import bpy, sys
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
RENAME = {"Walk-normal.001": "walk", "Run-flee.001": "run", "Attack-two handed2": "attack", "Death-Backwards": "death",
          "scared.001": "scared", "Dance-balls": "dance"}
for o in list(bpy.data.objects):
    if o.name not in ("Defender", "Defender_Ske"):
        bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions):
    if a.name in RENAME:
        a.name = RENAME[a.name]
    else:
        bpy.data.actions.remove(a)
arm = bpy.data.objects["Defender_Ske"]
mesh = bpy.data.objects["Defender"]
# "idle": o primeiro quadro da caminhada, parado (o arquivo não tem animação de espera; a "victory" é um comemorar).
arm.animation_data_create()
arm.animation_data.action = bpy.data.actions["walk"]
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
idle = bpy.data.actions.new("idle")
arm.animation_data.action = idle
bpy.context.view_layer.objects.active = arm
for frame in (1, 12):
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.keyframe_insert("location", frame=frame)
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        pb.keyframe_insert("scale", frame=frame)
arm.animation_data.action = None
for m in mesh.data.materials:
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    t = nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images["DoneWeps.png" if "Weapon" in m.name else "Done3.png"]
    t.image.scale(1024, 1024) if t.image.size[0] > 1024 else None
    links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6
# Uma ação por faixa NLA, para o exportador levar todas.
arm.animation_data_create()
for a in bpy.data.actions:
    track = arm.animation_data.nla_tracks.new()
    track.name = a.name
    track.strips.new(a.name, 1, a)
arm.animation_data.action = None
bpy.ops.object.select_all(action="DESELECT")
mesh.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="JPEG",
    export_animation_mode="NLA_TRACKS", export_apply=False)
print("OK defender", [a.name for a in bpy.data.actions])
