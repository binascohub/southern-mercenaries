"""Portão do chefe (boss_gate.glb do autor: arco de pedra verde com portão de ferro forjado e duas tochas na parede, 3 malhas de 167 mil vértices e uma textura de 2048 px; autoria e licença a confirmar): fecha, no fundo do
mapa da Floresta (porta norte do covil do Leshy), a passagem para o mapa do chefe e só abre com as duas chaves das missões do mapa. As 3 partes viram UMA malha "Boss_Gate", reduzida a ~60 mil triângulos, textura a 1024 px, girada para a largura (2,0 do
arquivo) ficar em X, a espessura (0,47) em Z e a frente para +Z, com a base em y = 0 e centrada em x/z (no jogo, escala 3: 6 m de largura, o vão das portas).
uso: blender -b -P tools/assets/build_boss_gate.py -- <boss_gate.glb> <saida.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix

src, out = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
parts = [o for o in bpy.data.objects if o.type == "MESH"]
for o in parts:
    o.data.transform(o.matrix_world)
    o.parent = None
    o.matrix_world = Matrix.Identity(4)
for o in list(bpy.data.objects):
    if o.type != "MESH":
        bpy.data.objects.remove(o, do_unlink=True)
for img in bpy.data.images:
    if img.size[0] > 1024:
        img.scale(1024, 1024)
    if img.size[0] > 0:
        img.pack()
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
gate = bpy.context.view_layer.objects.active
gate.name = "Boss_Gate"
dec = gate.modifiers.new("dec", "DECIMATE")
dec.ratio = min(1.0, 60000.0 / max(1, len(gate.data.polygons)))
bpy.ops.object.modifier_apply(modifier="dec")
mesh = gate.data
# a frente do arquivo está em +X do Blender (a largura em Y): gira -90 graus em Z (a frente vai para -Y, que o glTF leva para +Z; a largura vai para X)
mesh.transform(Matrix.Rotation(-math.pi / 2.0, 4, "Z"))
pts = [v.co for v in mesh.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
mesh.transform(Matrix.Translation(Vector((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z))))
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_image_format="WEBP", export_image_quality=85, export_animations=False)
print("OK", out, [round(v, 2) for v in gate.dimensions], len(mesh.vertices))
