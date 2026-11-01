"""Adagas do Ninja por rank (Cethiel's Weapons 3D, Drummyfish sobre arte de Cethiel, CC0, opengameart.org/content/cethiels-weapons-3d):
as espadas do pacote em tamanho de adaga (0,5 m), de pé (lâmina em +Y), com o meio na origem, uma .glb por rank
(Dagger_D ... Dagger_S) com a textura escolhida para o rank.
uso: build_ninja_daggers.py <pasta do pacote descompactado> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
# rank: (modelo, textura): D reta e simples, C fina e curva, B serrilhada, A de espinhos de gelo, S escura e ornada.
PICK = {"D": ("sword_h", "sword_h.png"), "C": ("sword_e", "sword_e_3.png"), "B": ("sword_a", "sword_a_2.png"),
        "A": ("sword_f", "sword_f.png"), "S": ("sword_i", "sword_i_3.png")}
LENGTH = 0.5
for rank, (model, tex) in PICK.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=os.path.join(src, model + ".obj"))
    obj = [o for o in bpy.data.objects if o.type == "MESH"][0]
    mesh = obj.data
    mesh.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    pts = [v.co for v in mesh.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    mesh.transform(Matrix.Scale(LENGTH / (mx.z - mn.z), 4) @ Matrix.Translation(-(mn + mx) / 2))
    mat = bpy.data.materials.new("Dagger_" + rank)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    t = mat.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(src, "textures", tex))
    mat.node_tree.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.5
    bsdf.inputs["Metallic"].default_value = 0.3
    mesh.materials.clear()
    mesh.materials.append(mat)
    obj.name = "Dagger_" + rank
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Dagger_%s.glb" % rank), export_format="GLB", export_image_format="JPEG")
    print("OK", rank, model, tex)
