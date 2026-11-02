"""Trilho da Mina (Rails, yd, GPL 2.0, opengameart.org/content/rails): assets/models/maps/Rail_Straight.glb.
Pega a malha "rail01" do .blend (textura difusa de 512 px embutida), deita o comprimento no eixo Z, centra em x/z, base em y = 0
e escala para 6 m de comprimento (bitola ~0,75 m); a peça emenda de ponta a ponta.
uso: blender -b <rail01OGA_GPL.blend> --python build_rails.py -- <saída.glb>"""
import bpy, sys
from mathutils import Vector, Matrix
out = sys.argv[sys.argv.index("--") + 1]
LENGTH = 6.0
deps = bpy.context.evaluated_depsgraph_get()
o = bpy.data.objects["rail01"]
mesh = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
mesh.transform(o.matrix_world)
pts = [v.co for v in mesh.vertices]
mn = Vector([min(p[i] for p in pts) for i in range(3)])
mx = Vector([max(p[i] for p in pts) for i in range(3)])
s = LENGTH / (mx.y - mn.y)
mesh.transform(Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
for m in mesh.materials:  # só a cor difusa (o glTF não leva o mapa de especular)
    for n in list(m.node_tree.nodes):
        if n.type == "TEX_IMAGE" and "D512" not in n.image.name:
            m.node_tree.nodes.remove(n)
for other in list(bpy.data.objects):
    bpy.data.objects.remove(other, do_unlink=True)
obj = bpy.data.objects.new("Rail_Straight", mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP")
print("OK", [round((mx - mn)[i] * s, 2) for i in range(3)])
