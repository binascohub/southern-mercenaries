"""Tufos de capim (Grass Pack 01, Yughues / Nobiax, CC0): assets/models/maps/Pl_Grass1..3.glb.
O grass.obj é uma cruz de dois cartões (50 x 50); as pastas grass_01..03 trazem três texturas (diffus.tga já com
alfa) para ela: cada textura vira uma peça, com recorte como nas outras plantas Pl_*. Em pé, base em y = 0, centrado.
uso: blender -b -P tools/assets/build_grass.py -- <pasta do pacote extraído> assets/models/maps"""
import bpy, sys, os
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:]
HEIGHT = 0.6
for n in (1, 2, 3):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=os.path.join(src, "grass.obj"), forward_axis="NEGATIVE_Y", up_axis="Z")
    obj = next(o for o in bpy.data.objects if o.type == "MESH")
    obj.name = obj.data.name = "Pl_Grass%d" % n
    mat = bpy.data.materials.new("Pl_Grass%d" % n)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(src, "grass_%02d" % n, "diffus.tga"))
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.85
    mat.blend_method = "CLIP"
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj.data.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    pts = [v.co for v in obj.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    s = HEIGHT / (mx.z - mn.z)
    obj.data.transform(Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, obj.name + ".glb"), export_format="GLB", use_selection=True, export_image_format="AUTO")
    print("OK", obj.name, "pegada %.2f x %.2f m" % ((mx.x - mn.x) * s, (mx.y - mn.y) * s))
