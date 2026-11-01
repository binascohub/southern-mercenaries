"""Livros de feitiço do Spell Book Pack (opengameart.org/content/spell-book-pack-0, CC BY-SA 3.0;
os círculos arcanos das capas são de redheadstock): uma .glb por rank do Invocador (D a S) com o
livro aberto (quadro final da animação) deitado, largura em +X, comprimento em +Z, lombada em -X,
e a capa de cada rank como textura embutida (1024 px, JPG).
uso: build_spellbook.py <grimoir.blend> <pasta com as texturas> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, texdir, out = sys.argv[sys.argv.index("--") + 1:]
COVERS = {"D": "illusion open texture.png", "C": "earth open texture.png", "B": "ice open texture.png",
          "A": "summoning open texture1.png", "S": "light open texture1.png"}
LENGTH = 0.34
for rank, tex in COVERS.items():
    bpy.ops.wm.open_mainfile(filepath=src)
    bpy.context.scene.frame_set(10)
    deps = bpy.context.evaluated_depsgraph_get()
    o = bpy.data.objects["Cube.001"]
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), depsgraph=deps)
    mesh.transform(o.matrix_world)
    # z (comprimento) -> -y e y (espessura) -> z: no glTF fica comprimento em +Z e espessura em +Y.
    mesh.transform(Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
    pts = [v.co for v in mesh.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    mesh.transform(Matrix.Scale(LENGTH / (mx.y - mn.y), 4) @ Matrix.Translation(-(mn + mx) / 2))
    img = bpy.data.images.load(os.path.join(texdir, tex))
    img.scale(1024, 1024)
    mat = bpy.data.materials.new("Cover")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    node = nodes.new("ShaderNodeTexImage")
    node.image = img
    links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.65
    mesh.materials.clear()
    mesh.materials.append(mat)
    for other in list(bpy.data.objects):
        bpy.data.objects.remove(other, do_unlink=True)
    book = bpy.data.objects.new("Book_" + rank, mesh)
    bpy.context.scene.collection.objects.link(book)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Book_%s.glb" % rank), export_format="GLB",
        export_image_format="JPEG", export_apply=False)
    print("OK", rank, [round(x, 3) for x in (mx - mn)])
