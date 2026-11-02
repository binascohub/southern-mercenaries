"""Elmos anglo-saxões do Cavaleiro (Anglo-Saxons helmets and spears, Lotnik / ulf, CC-BY 3.0,
opengameart.org/content/anglo-saxons-helmets-and-spears): Helm_1 ... Helm_6 (helm1.blend ... helm6.blend), as malhas
juntas, com a textura de cor de cada elmo (helm4 a helm6 usam a helm3), centradas em x/y e com a base em y = 0,
escaladas para a mesma largura de cabeça (0,30 m no maior eixo horizontal).
uso: build_knight_helmets.py <pasta do pacote descompactado> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
WIDTH = 0.30
for n in range(1, 7):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(os.path.join(src, "helm%d.blend" % n)) as (data_from, data_to):
        data_to.objects = [o for o in data_from.objects]
    for o in data_to.objects:
        if o is not None and o.type == "MESH":
            bpy.context.scene.collection.objects.link(o)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.convert(target="MESH")  # aplica os modificadores (espelho: o arquivo guarda só metade do elmo)
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    me = obj.data
    me.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    k = WIDTH / max(mx.x - mn.x, mx.y - mn.y)
    me.transform(Matrix.Scale(k, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    tex = "helm%d.png" % (n if n <= 3 else 3)
    mat = bpy.data.materials.new("Helm_%d" % n)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    t = nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(src, tex))
    t.image.scale(512, 512)
    links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.5
    bsdf.inputs["Roughness"].default_value = 0.5
    me.materials.clear()
    me.materials.append(mat)
    obj.name = "Helm_%d" % n
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Helm_%d.glb" % n), export_format="GLB", export_image_format="JPEG")
    print("OK helm", n, [round(x * k, 3) for x in (mx - mn)], "uv" , len(me.uv_layers))
