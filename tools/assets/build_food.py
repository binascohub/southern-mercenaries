"""Comidas (Food Props for Games, Vinrax, CC-BY 3.0, opengameart.org/content/food-props): Food_Meat, Food_Banana e Food_Apple
em .glb, com a textura de cor e a normal embutidas (512 px), base em y = 0, centradas na planta. A carne é o item de
missão do Bobo da Corte (Carne Selvagem, solta pelo Alfa da Matilha); a maçã e a banana enfeitam a mesa farta da sala do rei.
Tamanhos (maior dimensão): carne 0,45 m, banana 0,32 m, maçã 0,18 m (um pouco maiores que o real, para aparecer de cima).
uso: build_food.py <pasta do pacote descompactado> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
FOODS = {"Food_Meat": ("Meat", 0.45), "Food_Banana": ("Banana", 0.32), "Food_Apple": ("Apple", 0.18)}
for name, (stem, size) in FOODS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=os.path.join(src, "OBJ", stem + ".obj"))
    obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = obj.data
    me.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    k = size / max(mx.x - mn.x, mx.y - mn.y, mx.z - mn.z)
    me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.55
    c = nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images.load(os.path.join(src, "textures", stem + "_texture.jpg"))
    links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
    n = nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(os.path.join(src, "textures", stem + "_normal.jpg")); n.image.colorspace_settings.name = "Non-Color"
    nm = nodes.new("ShaderNodeNormalMap")
    links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    for img in (c.image, n.image):
        if max(img.size) > 512:
            img.scale(512, 512)
    me.materials.clear()
    me.materials.append(mat)
    obj.name = name
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", export_image_format="JPEG")
    print("OK food", name, [round(x * k, 2) for x in (mx - mn)])
