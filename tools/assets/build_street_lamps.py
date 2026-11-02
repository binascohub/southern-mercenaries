"""Postes de rua medievais (Textured Medieval Street Lamps, bobjh, CC-BY 4.0, opengameart.org/content/textured-medieval-street-lamps, sobre os
Medieval Street Lamp de PolygonDan): Lamp_Street_1 ... Lamp_Street_4, cada um a malha com a textura pintada (cor + sombra de oclusão
já assadas em lampN.png, 512 px) e a normal, base em y = 0, o poste na origem e o braço do lampião para +X.
Alturas: 1 e 2 com 2,8 m; 3 e 4 com 3,0 m. Em data/arenas.json "decor" (rotation 180 vira o braço para -X), junto de uma luz de cenário.
uso: build_street_lamps.py <pasta lamps extraída> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
HEIGHT = {1: 2.8, 2: 2.8, 3: 3.0, 4: 3.0}
for n in range(1, 5):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "lamp%d" % n, "lamp%d.blend" % n))
    obj = bpy.data.objects["lamp%d" % n]
    deps = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
    me.transform(obj.matrix_world)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    k = HEIGHT[n] / (mx.z - mn.z)
    me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((0, 0, -mn.z))))
    mat = bpy.data.materials.new("Lamp%d" % n)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.7
    c = nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images.load(os.path.join(src, "lamp%d" % n, "lamp%d.png" % n)); c.image.scale(512, 512)
    links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
    nrm = nodes.new("ShaderNodeTexImage"); nrm.image = bpy.data.images.load(os.path.join(src, "lamp%d" % n, "lamp%dNormal.png" % n)); nrm.image.scale(512, 512)
    nrm.image.colorspace_settings.name = "Non-Color"
    nm = nodes.new("ShaderNodeNormalMap")
    links.new(nrm.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    me.materials.clear()
    me.materials.append(mat)
    ob = bpy.data.objects.new("Lamp_Street_%d" % n, me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Lamp_Street_%d.glb" % n), export_format="GLB", export_image_format="JPEG")
    print("OK lamp", n, "altura", round((mx.z - mn.z) * k, 2), "braço até x =", round(mx.x * k, 2))
