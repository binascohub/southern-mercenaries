"""Escudos do Cavaleiro por rank (Cethiel's Weapons 3D, Drummyfish sobre arte de Cethiel, CC0): Shield_D ... Shield_S,
de pé, com a frente para +Z, 0,6 m de altura, centro na origem, com a textura de cada rank.
uso: build_knight_shields.py <pasta do pacote descompactado> <saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
# D broquel de madeira, C leão verde, B caveira vermelha, A leão azul e dourado, S cabeça de dragão roxa.
PICK = {"D": ("shield_c", "shield_c.png"), "C": ("shield_b", "shield_b_2.png"), "B": ("shield_a", "shield_a_3.png"),
        "A": ("shield_b", "shield_b.png"), "S": ("shield_d", "shield_d_2.png")}
SIZE = 0.6
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
    mesh.transform(Matrix.Scale(SIZE / max(mx.x - mn.x, mx.z - mn.z), 4) @ Matrix.Translation(-(mn + mx) / 2))
    mat = bpy.data.materials.new("Shield_" + rank)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    t = mat.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(os.path.join(src, "textures", tex))
    mat.node_tree.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.5
    bsdf.inputs["Metallic"].default_value = 0.3
    mesh.materials.clear()
    mesh.materials.append(mat)
    obj.name = "Shield_" + rank
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Shield_%s.glb" % rank), export_format="GLB", export_image_format="JPEG")
    print("OK", rank, model, tex)
