"""Cavalo de tração (Rigged Horse, Lyndon Daniels / ChadM, CC0, opengameart.org/content/rigged-horse): o arquivo
tem o esqueleto mas nenhuma animação; esta cena cria o ciclo "walk" (passo em diagonal, 1 s, em laço) girando
as pernas em volta do eixo lateral, deixa os pés em y = 0, 1,75 m de altura e olhando para +Z.
uso: build_horse.py <riggedHorse.blend> <saída.glb>"""
import bpy, sys, math
from mathutils import Matrix, Vector
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=src)
arm = bpy.data.objects["Armature"]


def textured(mat_name, color_img, normal_img=None, alpha=False, rough=0.8):
    """O arquivo guarda as texturas como imagens soltas: reconstrói o material com elas."""
    mat = bpy.data.materials[mat_name]
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images[color_img]
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha:
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        mat.blend_method = "CLIP" if hasattr(mat, "blend_method") else None
    if normal_img:
        nm = nodes.new("ShaderNodeTexImage")
        nm.image = bpy.data.images[normal_img]
        nm.image.colorspace_settings.name = "Non-Color"
        nmap = nodes.new("ShaderNodeNormalMap")
        links.new(nm.outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough


textured("Material", "HorseMain4k00.png", "HorseMain4k00Norm00.p")
textured("Material.003", "Hair12Main2k.png", "Hair12Main2kNorm.png", alpha=True)
textured("Eye_brown", "eye_texture.bmp.001", rough=0.2)
for name in ("HorseMain4k00.png", "HorseMain4k00Norm00.p", "Hair12Main2k.png", "Hair12Main2kNorm.png"):
    bpy.data.images[name].scale(1024, 1024)
# Cabeça em -Y. Pernas: (cadeia, fase em volta do ciclo): dianteira esq/dir e traseira esq/dir em diagonal.
LEGS = {"FL": (["Bone_L", "Bone_L.001", "Bone_L.002"], 0.0), "FR": (["Bone_R", "Bone_R.001", "Bone_R.002"], 0.5),
        "HL": (["Bone_L.003", "Bone_L.004", "Bone_L.005"], 0.5), "HR": (["Bone_R.003", "Bone_R.004", "Bone_R.005"], 0.0)}
SWING, BEND = math.radians(24), math.radians(38)
FRAMES = 24
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="POSE")
for pb in arm.pose.bones:
    pb.rotation_mode = "QUATERNION"
# Rotação em torno do eixo lateral do mundo, escrita no espaço local de cada osso (os filhos herdam a do pai).
world_rot = arm.matrix_world.to_3x3()
act = bpy.data.actions.new("walk")
arm.animation_data_create()
arm.animation_data.action = act
TAU = 2 * math.pi
for frame in range(FRAMES + 1):
    t = frame / FRAMES
    for names, phase in LEGS.values():
        ang = SWING * math.sin(TAU * (t + phase))
        lift = max(0.0, math.sin(TAU * (t + phase) + math.pi / 2)) * BEND  # dobra o joelho quando a perna volta
        for k, name in enumerate(names):
            bone = arm.data.bones[name]
            basis = (world_rot @ bone.matrix_local.to_3x3())
            a = ang if k == 0 else (-lift if k == 1 else lift * 0.6)
            rot = Matrix.Rotation(a, 3, "X")
            arm.pose.bones[name].rotation_quaternion = (basis.inverted() @ rot @ basis).to_quaternion()
            arm.pose.bones[name].keyframe_insert("rotation_quaternion", frame=frame + 1)
bpy.ops.object.mode_set(mode="OBJECT")
for o in bpy.data.objects:
    if o.type == "MESH" and o.parent is None:  # crina, cauda e olhos: presos ao esqueleto como peças rígidas
        world = o.matrix_world.copy()
        o.parent = arm
        o.matrix_parent_inverse = arm.matrix_world.inverted()
        o.matrix_world = world
bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, FRAMES + 1
deps = bpy.context.evaluated_depsgraph_get()
zs = []
for o in bpy.data.objects:
    if o.type == "MESH":
        me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), depsgraph=deps)
        me.transform(o.matrix_world)
        zs += [v.co.z for v in me.vertices]
s = 1.75 / (max(zs) - min(zs))
arm.scale = (s, s, s)
arm.location.z = -min(zs) * s
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT"):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="JPEG", export_animations=True,
    export_force_sampling=True, export_apply=False)
print("OK horse scale", round(s, 4))
