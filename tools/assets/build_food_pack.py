"""Peças do Food Pack (yd, CC0, opengameart.org/content/food-pack-0: pão, queijo e salsicha com textura): cada peça do .blend vira um .glb em assets/models/props
(Food_Bread, Food_Bread_Half, Food_Cheese, Food_Cheese_Wheel, Food_Sausage, Food_Sausage_Single), com a malha na origem (centrada em x e y, base em y = 0 do glTF),
texturas a 512 px. Servem para a mesa do banquete do rei, ao lado das frutas do kit.
uso: blender -b -P tools/assets/build_food_pack.py -- <foodPackOGACC0.blend> <pasta de saída>"""
import bpy, sys, os
import numpy as np
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
PIECES = {"bread": "Food_Bread", "breadHalf": "Food_Bread_Half", "Circle.004": "Food_Cheese", "Circle.002": "Food_Cheese_Wheel",
          "sausage.001": "Food_Sausage", "sausage": "Food_Sausage_Single"}
bpy.ops.wm.open_mainfile(filepath=src)
for im in bpy.data.images:
    if im.size[0] > 512:
        im.scale(512, 512)
# os materiais do pacote são do Blender 2.7 (texturas em "slots", sem nós): refaz cada um com a textura difusa ligada à cor base
DIFFUSE = {"bread01": "breadD", "cheese01": "cheese", "sausage01": "sausage01D"}
for mat in bpy.data.materials:
    if mat.name in DIFFUSE:
        mat.use_nodes = True
        mat.node_tree.nodes.clear()
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.7
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images[DIFFUSE[mat.name]]
        mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        outn = mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
        mat.node_tree.links.new(bsdf.outputs["BSDF"], outn.inputs["Surface"])
os.makedirs(out, exist_ok=True)
for name, out_name in PIECES.items():
    bpy.ops.object.select_all(action='DESELECT')
    src_obj = bpy.data.objects[name]
    obj = src_obj.copy()
    obj.data = src_obj.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = None
    obj.data.transform(src_obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    pts = np.array([v.co[:] for v in obj.data.vertices])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    obj.data.transform(Matrix.Translation(Vector((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]))))
    obj.name = out_name
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    print("PIECE", out_name, "size", tuple(round(x, 3) for x in (hi - lo)))
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, out_name + ".glb"), export_format='GLB', export_image_format='WEBP', use_selection=True,
                              export_animations=False)
    bpy.data.objects.remove(obj, do_unlink=True)
print("OK")
