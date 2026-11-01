"""Bandeira de guerra (War Banner, Danimal, CC-BY-SA 3.0, texturas CC0 de Yughues e caveira Atmostatic CC-BY, opengameart.org/content/war-banner): a bandeira
com o mastro e a caveira (duas malhas: tecido e caveira com alfa), a animação "Loop" do arquivo (balança de um lado ao outro, renomeada "loop") e
as texturas do pacote (512 px) num .glb (War_Banner.glb), 3,5 m de altura, base em y = 0, centrada. Para os campos de batalha das Ruínas.
uso: build_war_banner.py <WarBanner.blend> <saída.glb>"""
import bpy, sys
from mathutils import Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
arm = bpy.data.objects["Armature"]
mesh = bpy.data.objects["WarBanner"]
act = bpy.data.actions["ArmatureAction"]
act.name = "loop"
ad = arm.animation_data_create()
ad.action = None
track = ad.nla_tracks.new()
track.name = "loop"
track.strips.new("loop", int(act.frame_range[0]), act)
imgs = {i.name: i for i in bpy.data.images}
def node_material(m, color_img, normal_img=None, alpha=False):
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial"); b = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(b.outputs["BSDF"], o_node.inputs["Surface"]); b.inputs["Roughness"].default_value = 0.8
    c = nodes.new("ShaderNodeTexImage"); c.image = imgs[color_img]
    links.new(c.outputs["Color"], b.inputs["Base Color"])
    if alpha:
        links.new(c.outputs["Alpha"], b.inputs["Alpha"])
        if hasattr(m, "blend_method"):
            m.blend_method = "CLIP"
    if normal_img:
        n = nodes.new("ShaderNodeTexImage"); n.image = imgs[normal_img]; n.image.colorspace_settings.name = "Non-Color"
        nm = nodes.new("ShaderNodeNormalMap")
        links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], b.inputs["Normal"])
for m in mesh.data.materials:
    if m.name == "WarBanner":
        node_material(m, "WarBanner.png", "WarBannerNormal.png")
    else:
        node_material(m, "Skull_Monster_512.png", None, alpha=True)
bpy.context.view_layer.update()
pts = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
k = 3.5 / (mx.z - mn.z)
arm.scale = arm.scale * k
arm.location = Vector((arm.location.x - (mn.x + mx.x) / 2 * k, arm.location.y - (mn.y + mx.y) / 2 * k, arm.location.z - mn.z * k))
bpy.context.view_layer.update()
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="AUTO", export_animations=True, export_animation_mode="NLA_TRACKS")
print("OK banner", [round(x * k, 2) for x in (mx - mn)])
