"""Arqueiro élfico (Elven Archer - lower poly edition, Julius sobre a malha de theclubber, CC BY-SA 3.0,
opengameart.org/content/elven-archer-lower-poly-edition), o NPC que dá a missão do mini-chefe da Floresta.
O pacote é um OBJ de ~8 mil polígonos (corpo, arco, flechas...) sem esqueleto e sem texturas (vêm do .blend do original);
fica parado na pose do arquivo. Pés em y = 0, 1,85 m de altura, centrado em x/z, texturas do corpo, cabeça, cabelo e arco em JPG.
uso: blender -b -P tools/assets/build_elf_archer.py -- <pasta do pacote extraído> <pasta das texturas> <saída.glb> [render.png]"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:]
src, texdir, out = args[0], args[1], args[2]
preview = args[3] if len(args) > 3 else None
HEIGHT = 1.85
GAIN = 1.8
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "elf_archer_8k.obj"), forward_axis="NEGATIVE_Z", up_axis="Y")
objs = [o for o in bpy.data.objects if o.type == "MESH"]
def material(name, image, alpha=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(texdir, image))
    px = np.array(tex.image.pixels[:], dtype=np.float32).reshape(-1, 4)   # texturas escuras demais sem o AO/especular do original
    px[:, :3] = np.clip(px[:, :3] * GAIN, 0, 1)
    tex.image.pixels = px.ravel().tolist()
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha:
        mat.node_tree.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        mat.blend_method = "CLIP"
    bsdf.inputs["Roughness"].default_value = 0.85
    return mat
# o OBJ não traz texturas (o PNG do pacote é só uma imagem de apresentação): vêm do .blend original
# (Rigged Textured Elven Archer, theclubber, CC BY-SA 3.0), extraídas como body/head/hair/prop.png.
MATS = {"face": material("ElfHead", "head.png"), "hair": material("ElfHair", "hair.png", alpha=True),
        "bow": material("ElfProp", "prop.png"), "bow2": material("ElfProp", "prop.png"), "arrow1": material("ElfProp", "prop.png"),
        "arrow2": material("ElfProp", "prop.png")}
body_mat = material("ElfBody", "body.png")
for o in objs:
    o.data.materials.clear()
    o.data.materials.append(MATS.get(o.name, body_mat))
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
s = HEIGHT / (mx.z - mn.z)
shift = Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
for o in objs:
    o.data.transform(o.matrix_world)
    o.matrix_world = Matrix.Identity(4)
    o.data.transform(shift)
bpy.ops.object.select_all(action="DESELECT")
for o in objs:
    o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_image_format="JPEG", export_apply=False)
print("OK", [o.name for o in objs], "escala %.4f  largura %.2f x %.2f m" % (s, (mx.x - mn.x) * s, (mx.y - mn.y) * s))
if preview:
    sc = bpy.context.scene
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam)
    cam.location = (0.0, -4.2, 0.95); cam.rotation_euler = (math.radians(90), 0, 0); sc.camera = cam
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
    sc.render.resolution_x = sc.render.resolution_y = 600; sc.render.filepath = preview
    bpy.ops.render.render(write_still=True)
