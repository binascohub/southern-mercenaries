"""Guerreiro espartano da missão das Ruínas a partir de "Achilles Spartan Greek Warrior" (gamekorp, OpenGameArt, CC0,
opengameart.org/content/achilles-spartan-greek-warrior): o pacote traz só a malha (mesh.obj, um corpo com elmo,
escudo, lança e espada) e a textura, em T-pose e sem esqueleto. Aqui os braços são baixados girando os vértices
em torno do ombro (com uma faixa de transição no ombro), o modelo é normalizado (1,9 m de altura com a crista do
elmo, pés em y = 0, centro em x/z, frente em +Z do Godot), a textura é reduzida e tudo vira um .glb sem animação:
o NPC fica parado na pose do arquivo (NpcModel, "poses": {}).
uso: blender -b -P tools/assets/build_achilles.py -- <pasta do pacote extraído> <saída.glb> [prévia.png]"""
import bpy, sys, os, math
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
src, out = args[0], args[1]
preview = args[2] if len(args) > 2 else None
HEIGHT = 1.9                   # com a crista do elmo
ARM_DOWN = math.radians(78)    # quanto o braço desce a partir do T
SHOULDER_X, SHOULDER_UP = 15.0, 70.0   # ombro no arquivo (x lateral, y para cima, em unidades do arquivo)
BLEND = 4.0                    # largura (em x) da faixa de transição do ombro

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "mesh.obj"), forward_axis="NEGATIVE_Z", up_axis="Y")
body = next(o for o in bpy.data.objects if o.type == "MESH")
mesh = body.data
# O importador deixa os vértices nas coordenadas do OBJ (Y para cima) e gira o objeto: aplica a rotação nos vértices.
mesh.transform(body.matrix_world)
body.matrix_world = Matrix.Identity(4)

# Braços: no Blender o eixo da frente/trás é Y, o de cima é Z. Quem está além do ombro gira em torno dele.
for v in mesh.vertices:
    side = 1 if v.co.x > 0 else -1
    reach = abs(v.co.x) - SHOULDER_X
    if reach <= -BLEND or v.co.z < SHOULDER_UP - 22 or v.co.z > SHOULDER_UP + 8:
        continue
    weight = max(0.0, min(1.0, (reach + BLEND) / (2 * BLEND)))
    pivot = Vector((side * SHOULDER_X, v.co.y, SHOULDER_UP))
    rot = Matrix.Rotation(side * ARM_DOWN * weight, 4, "Y")
    v.co = pivot + rot @ (v.co - pivot)

# Normaliza: altura, pés em z = 0, centro; o arquivo olha para -Y do Blender depois da importação? (conferido na prévia)
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
mesh.transform(Matrix.Scale(HEIGHT / (mx.z - mn.z), 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
if "--flip" in sys.argv:
    mesh.transform(Matrix.Rotation(math.pi, 4, "Z"))

# Material: a textura única (reduzida a 1024 px).
img = bpy.data.images.load(os.path.join(src, "texture.png"))
img.scale(1024, 1024)
mat = bpy.data.materials.new("Spartan")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
tex.image = img
mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.7
bsdf.inputs["Metallic"].default_value = 0.0
mesh.materials.clear()
mesh.materials.append(mat)
body.name = "Spartan"
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85)
print("OK", [round(x, 2) for x in (mx - mn)])

if preview:
    sc = bpy.context.scene
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam)
    cam.location = (0.0, -4.0, 1.0); cam.rotation_euler = (math.radians(90), 0, 0); sc.camera = cam
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.rotation_euler = (math.radians(50), 0, math.radians(20))
    sc.collection.objects.link(sun)
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
    sc.render.resolution_x = sc.render.resolution_y = 600
    sc.render.filepath = preview
    bpy.ops.render.render(write_still=True)
