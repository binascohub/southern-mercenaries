"""Melancia (A watermelon, nevak / Cough-E, CC0, opengameart.org/content/a-watermelon): Food_Watermelon (inteira) e
Food_Watermelon_Half (aberta, as duas metades juntas num corte), com a textura pintada à mão (1024 px, em 512) embutida,
base em y = 0, centradas, 0,34 m de comprimento. Para a mesa de fartura e a carroça da Capital.
uso: build_watermelon.py <pasta do pacote descompactado> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
for name, blend in (("Food_Watermelon", "melon.blend"), ("Food_Watermelon_Half", "melon_half.blend")):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(src, blend))
    deps = bpy.context.evaluated_depsgraph_get()
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    first = None
    for o in meshes:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        me.transform(o.matrix_world)
        new = bpy.data.objects.new(o.name + "_c", me)
        bpy.context.scene.collection.objects.link(new)
        first = first or new
    tex = bpy.data.images.load(os.path.join(src, "dif.png"))
    tex.scale(512, 512)
    for o in meshes:
        bpy.data.objects.remove(o, do_unlink=True)
    parts = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    me = obj.data
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    k = 0.34 / max(mx.x - mn.x, mx.y - mn.y, mx.z - mn.z)
    me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.5
    t = nodes.new("ShaderNodeTexImage"); t.image = tex
    links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    me.materials.clear()
    me.materials.append(mat)
    obj.name = name
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", export_image_format="JPEG")
    print("OK melon", name, [round(x * k, 2) for x in (mx - mn)])
