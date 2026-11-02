"""Prende um personagem sem esqueleto (em pose de T) ao esqueleto dos heróis
(Universal Animation Library) com pesos automáticos: ele ganha todas as
animações dos heróis. Alinha pela altura (pés em 0) e centraliza.
uso: rig_to_ual.py <hero.glb> <arquivo.blend> <objeto> <saida.glb> [altura_m] [material=r;g;b,...]"""
import bpy, sys
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]
hero, src, obj_name, out = a[:4]
height = float(a[4]) if len(a) > 4 else 1.8
colors = {}
if len(a) > 5 and a[5]:
    for pair in a[5].split(","):
        k, v = pair.split("=")
        colors[k] = tuple(float(x) for x in v.split(";")) + (1.0,)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=hero)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
hero_pts = [o.matrix_world @ v.co for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("Head", "Peasant")) for v in o.data.vertices]
for o in list(bpy.data.objects):
    if o.type != "ARMATURE":
        bpy.data.objects.remove(o, do_unlink=True)
if arm.animation_data:
    arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
with bpy.data.libraries.load(src) as (lib, dst):
    dst.objects = [n for n in lib.objects if n == obj_name]
body = dst.objects[0]
bpy.context.scene.collection.objects.link(body)
deps = bpy.context.evaluated_depsgraph_get()
mesh = bpy.data.meshes.new_from_object(body.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.transform(body.matrix_world)
body.modifiers.clear()
body.data = mesh
body.parent = None
body.matrix_world = Matrix.Identity(4)
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
# Frente do personagem: o glTF importado tem a frente em -Y (como os heróis).
scale = height / (hi.z - lo.z)
mesh.transform(Matrix.Scale(scale, 4) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))))
for mat in mesh.materials:
    if mat and mat.name in colors:
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        o_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Base Color"].default_value = colors[mat.name]
        bsdf.inputs["Roughness"].default_value = 0.75
        links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
# Braços: gira e estica os braços da malha (em volta do ombro) até a mão bater
# com a mão do esqueleto; a cabeça (chapéu) fica toda no osso da cabeça.
import math
bones = arm.data.bones
def head(name):
    return arm.matrix_world @ bones[name].head_local
for side, sign in (("l", 1.0), ("r", -1.0)):
    if "upperarm_" + side not in bones:
        continue
    shoulder = head("upperarm_" + side)
    hand = head("hand_" + side)
    # Cuidado com o lado: a mão do esqueleto diz qual x é desse lado.
    sx = 1.0 if hand.x > 0 else -1.0
    arm_verts = [v for v in mesh.vertices if v.co.x * sx > abs(shoulder.x) - 0.02 and v.co.z > shoulder.z - 0.45]
    if not arm_verts:
        continue
    far = sorted(arm_verts, key=lambda v: -v.co.x * sx)[:max(5, len(arm_verts) // 50)]
    tip = sum((v.co for v in far), Vector()) / len(far)
    reach_mesh = Vector((tip.x - shoulder.x, tip.z - shoulder.z))
    reach_bone = Vector((hand.x - shoulder.x, hand.z - shoulder.z)) * 1.12  # a mão passa um pouco do osso
    angle = math.atan2(reach_bone.y, reach_bone.x) - math.atan2(reach_mesh.y, reach_mesh.x)
    k = reach_bone.length / max(reach_mesh.length, 0.01)
    for v in arm_verts:
        d = Vector((v.co.x - shoulder.x, v.co.z - shoulder.z))
        if d.x * sx <= 0:
            continue
        w = min(1.0, (d.x * sx) / 0.12)  # perto do ombro muda pouco
        r = Vector((d.x * math.cos(angle) - d.y * math.sin(angle), d.x * math.sin(angle) + d.y * math.cos(angle))) * k
        new = d.lerp(r, w)
        v.co.x = shoulder.x + new.x
        v.co.z = shoulder.z + new.y
    print("ARM", side, round(math.degrees(angle), 1), round(k, 2))
# Texturas procedurais (pano com trama e desgaste, couro com rachaduras, camisa
# encardida, pele) gravadas numa imagem pelo mapa UV do modelo.
def build_procedural(mat, kind, base):
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()
    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    coord = nodes.new("ShaderNodeTexCoord")
    fine = nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 140.0
    fine.inputs["Detail"].default_value = 6.0
    links.new(coord.outputs["Object"], fine.inputs["Vector"])
    big = nodes.new("ShaderNodeTexNoise")
    big.inputs["Scale"].default_value = 4.0
    links.new(coord.outputs["Object"], big.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    dark = tuple(c * 0.55 for c in base[:3]) + (1,)
    light = tuple(min(1.0, c * 1.45 + 0.03) for c in base[:3]) + (1,)
    ramp.color_ramp.elements[0].color = dark
    ramp.color_ramp.elements[1].color = light
    mix = nodes.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.inputs["Factor"].default_value = 0.5
    links.new(fine.outputs["Fac"], mix.inputs["A"])
    links.new(big.outputs["Fac"], mix.inputs["B"])
    value = mix.outputs["Result"]
    if kind == "cloth":
        wave = nodes.new("ShaderNodeTexWave")
        wave.inputs["Scale"].default_value = 60.0
        links.new(coord.outputs["Object"], wave.inputs["Vector"])
        mix2 = nodes.new("ShaderNodeMix"); mix2.data_type = "FLOAT"; mix2.inputs["Factor"].default_value = 0.3
        links.new(value, mix2.inputs["A"]); links.new(wave.outputs["Fac"], mix2.inputs["B"])
        value = mix2.outputs["Result"]
    elif kind == "leather":
        cells = nodes.new("ShaderNodeTexVoronoi")
        cells.inputs["Scale"].default_value = 90.0
        links.new(coord.outputs["Object"], cells.inputs["Vector"])
        mix2 = nodes.new("ShaderNodeMix"); mix2.data_type = "FLOAT"; mix2.inputs["Factor"].default_value = 0.35
        links.new(value, mix2.inputs["A"]); links.new(cells.outputs["Distance"], mix2.inputs["B"])
        value = mix2.outputs["Result"]
    links.new(value, ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return nodes

KINDS = {"BlackCloth": "cloth", "WhiteCloth": "cloth", "Leather": "leather", "Skin": "skin"}
bake_image = bpy.data.images.new("PirateBake", 1024, 1024)
for mat in mesh.materials:
    if mat and mat.name in KINDS and mat.name in colors:
        mat.use_nodes = True
        nodes = build_procedural(mat, KINDS[mat.name], colors[mat.name])
        target = nodes.new("ShaderNodeTexImage")
        target.image = bake_image
        nodes.active = target
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 4
sc.cycles.device = "CPU"
for o in bpy.context.view_layer.objects:
    o.select_set(False)
body.select_set(True)
bpy.context.view_layer.objects.active = body
if any(m and m.name in KINDS and m.name in colors for m in mesh.materials):  # sem materiais procedurais, não há o que gravar
    with bpy.context.temp_override(active_object=body, object=body, selected_objects=[body], selected_editable_objects=[body]):
        bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
for mat in mesh.materials:
    if mat and mat.name in KINDS and mat.name in colors:
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.55 if KINDS[mat.name] == "leather" else 0.85
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bake_image
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
bake_image.pack()
print("BAKED")
hpts = hero_pts
print("HERO", [round(max(p[i] for p in hpts) - min(p[i] for p in hpts), 2) for i in range(3)],
      "BODY", [round((hi[i] - lo[i]) * scale, 2) for i in range(3)])
for o in bpy.context.view_layer.objects:
    o.select_set(False)
body.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
with bpy.context.temp_override(active_object=arm, object=arm, selected_objects=[body, arm], selected_editable_objects=[body, arm]):
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
neck_z = head("Head").z if "Head" in bones else 1.55
head_group = body.vertex_groups.get("Head")
if head_group:
    above = [v.index for v in mesh.vertices if v.co.z > neck_z + 0.04]
    for g in body.vertex_groups:
        if g != head_group:
            g.remove(above)
    head_group.add(above, 1.0, "REPLACE")
print("GROUPS", len(body.vertex_groups))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animation_mode="ACTIONS",
    export_image_format="WEBP", export_image_quality=85)
print("OK", out)
