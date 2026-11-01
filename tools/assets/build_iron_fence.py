"""Grade preta de ferro forjado do Cemitério (modelo original do jogo, CC BY-SA 4.0): assets/models/maps/Fence_Iron.glb,
um segmento de 2 m de largura e 1,7 m de altura, com barras redondas, duas travessas, pontas de lança e um poste com
bolinha em cada ponta (segmentos lado a lado formam a grade corrida). Roda com o Python do Blender:
blender -b -P tools/assets/build_iron_fence.py -- <saída.glb>"""
import bpy, bmesh, sys, os
from mathutils import Matrix

out = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bm = bmesh.new()


def move(x, y, z):
    return Matrix.Translation((x, y, z))


def bar(x, z0, z1, r=0.018):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=r, depth=z1 - z0, matrix=move(x, 0, (z0 + z1) / 2))


def spear(x, z, r=0.035, h=0.13):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=0.0, depth=h, matrix=move(x, 0, z + h / 2))


def box(x, y, z, sx, sy, sz):
    bmesh.ops.create_cube(bm, size=1.0, matrix=move(x, y, z) @ Matrix.Diagonal((sx, sy, sz, 1.0)))


# Travessas (cima e baixo), barras com pontas de lança e postes nas pontas.
box(0, 0, 1.38, 2.0, 0.04, 0.045)
box(0, 0, 0.3, 2.0, 0.04, 0.045)
for i in range(11):
    x = -0.85 + i * 0.17
    bar(x, 0.0, 1.58)
    spear(x, 1.58)
for sx in (-0.97, 0.97):
    box(sx, 0, 0.85, 0.075, 0.075, 1.7)
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.06, matrix=move(sx, 0, 1.74))
mesh = bpy.data.meshes.new("Fence_Iron")
bm.to_mesh(mesh)
bm.free()
mat = bpy.data.materials.new("Iron_Black")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.025, 0.025, 0.028, 1.0)
bsdf.inputs["Metallic"].default_value = 0.7
bsdf.inputs["Roughness"].default_value = 0.5
mesh.materials.append(mat)
obj = bpy.data.objects.new("Fence_Iron", mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Fence_Iron.glb") if os.path.isdir(out) else out, export_format="GLB", use_selection=True)
print("OK Fence_Iron", len(mesh.vertices), "vértices")
