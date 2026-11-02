"""Penas de ave (birds_feather.glb enviado pelo autor do projeto: duas penas num cartão curvo cada, uma azul-vermelha e uma cinza, texturas de 4096 px de cor, brilho e normal; autoria e licença a confirmar):
as penas que caem das aves das Asas do Falcão (SkillSystem._shell_fx). Aqui cada pena vira um modelo à parte (Bird_Feather_Blue.glb e Bird_Feather_Gray.glb), com só a cor (com o alfa que recorta o contorno)
a 512 px em WebP, material de recorte (alpha scissor), a pena com ~0,5 m de comprimento ao longo de +Y e centrada.
uso: blender -b -P tools/assets/build_bird_feathers.py -- <birds_feather.glb> <pasta de saída (assets/models/props)>"""
import bpy, sys, os
import numpy as np
from mathutils import Vector, Matrix

src, outdir = sys.argv[sys.argv.index("--") + 1:][:2]
FEATHERS = {"Object_2": "Bird_Feather_Blue", "Object_3": "Bird_Feather_Gray"}
LENGTH = 0.5
for obj_name, out_name in FEATHERS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    obj = bpy.data.objects[obj_name]
    for o in list(bpy.data.objects):
        if o is not obj:
            bpy.data.objects.remove(o, do_unlink=True)
    obj.parent = None
    obj.data.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    mat = obj.data.materials[0]
    base = next(n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name in ("Image_0", "Image_3"))
    base.scale(512, 512)
    base.pack()
    new = bpy.data.materials.new("m_" + out_name.lower())
    new.use_nodes = True
    nt = new.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.7
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = base
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    new.blend_method = 'CLIP' if hasattr(new, "blend_method") else None
    obj.data.materials.clear()
    obj.data.materials.append(new)
    v = np.array([tuple(p.co) for p in obj.data.vertices])
    ext = v.max(axis=0) - v.min(axis=0)
    axis = int(np.argmax(ext))  # o comprimento da pena
    print("PENA", out_name, [round(float(x), 1) for x in ext], "eixo", axis)
    rot = Matrix.Identity(4)
    if axis == 0:
        rot = Matrix.Rotation(1.5708, 4, "Z")
    elif axis == 2:
        rot = Matrix.Rotation(-1.5708, 4, "X")
    obj.data.transform(rot)
    v = np.array([tuple(p.co) for p in obj.data.vertices])
    ctr = (v.max(axis=0) + v.min(axis=0)) / 2
    k = LENGTH / float(v[:, 1].max() - v[:, 1].min())
    obj.data.transform(Matrix.Scale(k, 4) @ Matrix.Translation(-Vector(ctr)))
    # o cartão fica no plano XZ (normal em Y) vindo do arquivo; a pena é deitada no plano XY do Blender -> em pé no glTF
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    dst = os.path.join(outdir, out_name + ".glb")
    bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', use_selection=True, export_animations=False)
    print("OK", dst, [round(x, 2) for x in obj.dimensions])
