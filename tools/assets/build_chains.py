"""Correntes e algemas de prisão feitas do zero (elos de torus em ferro escuro; sem pacote de terceiros) para as Catacumbas:
  Prison_WallShackles.glb  placa de ferro com dois grilhões pendurados, colada numa parede (a face fica para +Z; base em y = 0, ~1,9 m de altura)
  Prison_BallChain.glb     bola de ferro presa por uma corrente deitada a uma algema aberta (~2,3 m de comprimento, em x)
  Prison_ChainHang.glb     corrente comprida pendurada de uma argola (3 m de altura)
uso: blender -b -P tools/assets/build_chains.py -- <pasta de saída, ex.: assets/models/maps>"""
import bpy, math, os, sys
from mathutils import Vector

out_dir = sys.argv[sys.argv.index("--") + 1]
IRON = (0.1, 0.1, 0.115, 1.0)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat = bpy.data.materials.new("PrisonIron")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = IRON
    bsdf.inputs["Metallic"].default_value = 0.85
    bsdf.inputs["Roughness"].default_value = 0.55
    return mat


def link(mat, at, along="z", roll=0.0, length=0.13, width=0.075, wire=0.016):
    """Um elo: torus esticado ao longo do eixo `along`, girado `roll` em volta dele."""
    bpy.ops.mesh.primitive_torus_add(major_radius=width / 2, minor_radius=wire, location=at, major_segments=14, minor_segments=6)
    o = bpy.context.active_object
    o.scale = (1.0, 1.0, 1.0)
    # o torus nasce deitado (plano xy); estica em y e vira de pé conforme o eixo
    o.scale = (1.0, length / width, 1.0)
    if along == "z":
        o.rotation_euler = (math.pi / 2, 0, roll)
    elif along == "x":
        o.rotation_euler = (0, 0, math.pi / 2)
        o.rotation_euler = (roll, 0, math.pi / 2)
    o.data.materials.append(mat)
    return o


def box(mat, at, size):
    bpy.ops.mesh.primitive_cube_add(location=at)
    o = bpy.context.active_object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(mat)
    return o


def ring(mat, at, radius, wire, axis="y"):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=wire, location=at, major_segments=18, minor_segments=7)
    o = bpy.context.active_object
    if axis == "y":
        o.rotation_euler = (math.pi / 2, 0, 0)
    o.data.materials.append(mat)
    return o


def export(name, w_size_note=""):
    bpy.ops.object.select_all(action="DESELECT")
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.join()
    whole = bpy.context.view_layer.objects.active
    whole.name = whole.data.name = name
    pts = [whole.matrix_world @ v.co for v in whole.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    whole.data.transform(__import__("mathutils").Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    bpy.ops.object.select_all(action="DESELECT")
    whole.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, name + ".glb"), export_format="GLB", use_selection=True)
    print("OK", name, "caixa %.2f x %.2f x %.2f m (x, y, z do Blender)" % tuple(mx[i] - mn[i] for i in range(3)), w_size_note)


# --- grilhões de parede: placa de ferro no alto, duas correntes e duas algemas (no Blender, +Y é a face que sai da parede; o glTF vira +Z)
mat = reset()
box(mat, (0, 0, 1.85), (0.7, 0.06, 0.16))                      # barra de fixação
for x in (-0.22, 0.22):
    ring(mat, (x, 0.05, 1.78), 0.045, 0.014)                   # argola
    for i in range(9):                                         # corrente de 9 elos
        link(mat, (x, 0.05, 1.68 - 0.1 * i), "z", roll=(math.pi / 2 if i % 2 else 0.0))
    ring(mat, (x, 0.05, 0.72), 0.11, 0.024)                    # algema
    box(mat, (x, 0.05, 0.84), (0.05, 0.05, 0.07))              # a dobradiça da algema
export("Prison_WallShackles")

# --- bola e corrente: a bola de ferro (esfera) numa ponta, a algema aberta na outra, 14 elos deitados no chão
mat = reset()
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(-1.0, 0, 0.2))
ball = bpy.context.active_object
ball.data.materials.append(mat)
for i in range(14):
    link(mat, (-0.78 + 0.1 * i, 0, 0.02), "x", roll=(math.pi / 2 if i % 2 else 0.0), length=0.13)
ring(mat, (0.78 + 0.12, 0, 0.1), 0.1, 0.022, axis="y")
box(mat, (0.78 + 0.12, 0, 0.2), (0.05, 0.05, 0.06))
export("Prison_BallChain")

# --- corrente pendurada: argola grande no alto e 28 elos
mat = reset()
ring(mat, (0, 0, 2.95), 0.1, 0.02)
for i in range(28):
    link(mat, (0, 0, 2.82 - 0.1 * i), "z", roll=(math.pi / 2 if i % 2 else 0.0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0, 0, 0.02))
bpy.context.active_object.data.materials.append(mat)
export("Prison_ChainHang")
