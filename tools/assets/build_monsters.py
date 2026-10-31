"""Monstros animados do Esgoto a partir dos modelos do OpenGameArt (CC0 e CC BY-SA):
limpa a cena (câmeras, luzes, variantes), deixa a malha com o esqueleto e as
animações que o jogo usa, padroniza o tamanho (comprimento em metros), a frente
(+Z no Godot) e o chão (pés em y = 0), reduz as texturas e exporta .glb.
Os .blend antigos (Blender 2.7x) ligavam a textura por "slots" que o Blender
novo não converte: as imagens são ligadas de novo aos materiais (material=imagem).
uso: build_monsters.py <arquivo.blend> <saida.glb> <malhas,separadas> <comprimento_m> <acao=nova,...> <material=imagem,...>"""
import bpy, sys, math
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
src, out, keep_meshes, length = args[0], args[1], args[2].split(","), float(args[3])
renames = dict(pair.split("=") for pair in args[4].split(",")) if len(args) > 4 and args[4] else {}
textures = dict(pair.split("=") for pair in args[5].split(",")) if len(args) > 5 and args[5] else {}
bpy.ops.wm.open_mainfile(filepath=src)

meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name in keep_meshes]
arms = set()
for o in meshes:
    for m in o.modifiers:
        if m.type == "ARMATURE" and m.object:
            arms.add(m.object)
    if o.parent and o.parent.type == "ARMATURE":
        arms.add(o.parent)
keep = set(meshes) | arms
for arm in arms:  # o esqueleto vira a raiz (sem pai), no mesmo lugar
    if arm.parent:
        world = arm.matrix_world.copy()
        arm.parent = None
        arm.matrix_world = world
# A malha passa a ser filha do esqueleto (escala e posição vão juntas).
arm_obj = next(iter(arms)) if arms else None
for o in meshes:
    if arm_obj and o.parent != arm_obj:
        world = o.matrix_world.copy()
        o.parent = arm_obj
        o.matrix_world = world
# O glTF ignora a transformação da malha com pele: ela vai para os vértices.
from mathutils import Matrix
for o in meshes:
    if arm_obj:
        o.data.transform(arm_obj.matrix_world.inverted() @ o.matrix_world)
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = Matrix.Identity(4)
for o in list(bpy.data.objects):
    if o not in keep:
        bpy.data.objects.remove(o, do_unlink=True)

# Só as animações pedidas, com nomes simples (idle, walk, run, attack, hit, die, fly).
for action in list(bpy.data.actions):
    if action.name in renames:
        action.name = renames[action.name]
        action.use_fake_user = True
    else:
        bpy.data.actions.remove(action)
for arm in arms:
    if arm.animation_data:
        arm.animation_data.action = None
        for track in list(arm.animation_data.nla_tracks):
            arm.animation_data.nla_tracks.remove(track)

# Materiais refeitos do zero: Principled com a imagem (o exportador não segue
# os nós antigos); sem imagem, mantém a cor difusa.
for mat in bpy.data.materials:
    color = tuple(mat.diffuse_color)
    image = bpy.data.images.get(textures.get(mat.name, ""))
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.8
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    if image is None:
        bsdf.inputs["Base Color"].default_value = color
        continue
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if image.name.lower().startswith("hair"):
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    print("TEX", mat.name, "<-", image.name)

# As ações só mexem nos ossos: chaves no próprio objeto (posição, escala)
# desfariam o tamanho e o centro padronizados.
for action in bpy.data.actions:
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in list(bag.fcurves):
                    if not fc.data_path.startswith("pose."):
                        print("DROP", action.name, fc.data_path)
                        bag.fcurves.remove(fc)

# Caixa da malha avaliada (com espelho/armadura em repouso).
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
pts = []
for o in meshes:
    ev = o.evaluated_get(deps)
    pts += [o.matrix_world @ v.co for v in ev.to_mesh().vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
size = mx - mn
# comprimento 0: mantém o tamanho original (o jogo escala; para modelos cujas
# animações guardam as posições dos ossos em tamanho absoluto).
scale = length / max(size.x, size.y) if length > 0 else 1.0
roots = [o for o in keep if o.parent is None]
print("ROOTS", [o.name for o in roots], [tuple(o.scale) for o in roots])
center = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
for o in roots:
    o.location = (o.location - center) * scale
    o.scale = o.scale * scale
print("SIZE", [round(v * scale, 2) for v in size])

# Escala aplicada nos ossos e nas malhas (o exportador às vezes perde a do
# objeto); as posições animadas dos ossos crescem/encolhem junto.
bpy.context.view_layer.update()
for arm in (arms if length > 0 else []):
    factor = arm.scale.x
    arm.data.transform(Matrix.Scale(factor, 4))
    for m in meshes:
        if m.parent == arm:
            m.data.transform(Matrix.Scale(factor, 4))
    arm.scale = (1, 1, 1)
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        if fc.data_path.endswith(".location"):
                            for k in fc.keyframe_points:
                                k.co.y *= factor
                                k.handle_left.y *= factor
                                k.handle_right.y *= factor

for img in bpy.data.images:
    if img.size[0] > 512:
        img.scale(512, max(1, int(img.size[1] * 512 / img.size[0])))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animation_mode="ACTIONS",
    export_apply=True, export_image_format="WEBP", export_image_quality=85)
print("OK", out, [a.name for a in bpy.data.actions])
