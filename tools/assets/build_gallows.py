"""Forca (death.blend enviado pelo autor do projeto: "vintage death sentence", palanque de 8,6 x 6 m com o pórtico de duas forcas, duas alçapões e cordas, texturas em caminhos de outro computador
que NÃO vieram junto; autor/licença a confirmar): enfeite da avenida da Capital. Aqui ficam as peças de madeira e as cordas (a malha da corda cai a ~1,5 mil polígonos), com dois materiais lisos
(madeira e corda), a frente (os degraus, em +X no arquivo) virada para +Z do glTF, o palanque centrado em x/z e com o chão em y = 0 (a parte do pórtico abaixo do chão vai enterrada). Sem as luzes, a câmera,
o cubo do fundo nem as animações das alçapões.
Gera assets/models/props/Gallows.glb.
uso: blender -b -P tools/assets/build_gallows.py -- <death.blend> <saida.glb>"""
import bpy, sys, math
from mathutils import Vector, Matrix

src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
WOOD, ROPE = (0.36, 0.24, 0.14), (0.62, 0.52, 0.36)
bpy.ops.wm.open_mainfile(filepath=src)
dg = bpy.context.evaluated_depsgraph_get()
KEEP_WOOD = ("Cube.001", "Cube.002", "Cube.004", "Cube.005", "Cube.006")
KEEP_ROPE = ("NurbsPath.002", "NurbsPath.003")


def make_mat(name, color, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    return m


m_wood, m_rope = make_mat("m_gallows_wood", WOOD, 0.85), make_mat("m_gallows_rope", ROPE, 0.9)
parts = []
for name in KEEP_WOOD + KEEP_ROPE:
    o = bpy.data.objects[name]
    mesh = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    mesh.transform(o.matrix_world)
    mesh.materials.clear()
    mesh.materials.append(m_rope if name in KEEP_ROPE else m_wood)
    ob = bpy.data.objects.new("P_" + name, mesh)
    bpy.context.scene.collection.objects.link(ob)
    parts.append(ob)
    print("PARTE", name, len(mesh.polygons))
for o in list(bpy.data.objects):
    if o not in parts:
        bpy.data.objects.remove(o, do_unlink=True)
for o in parts:
    if o.name.startswith("P_NurbsPath") and len(o.data.polygons) > 1500:
        bpy.context.view_layer.objects.active = o
        mod = o.modifiers.new("d", 'DECIMATE')
        mod.ratio = 1500 / len(o.data.polygons)
        bpy.ops.object.modifier_apply(modifier="d")
# a frente (degraus) está em +X: gira -90 graus em Z para ir a -Y (= +Z do glTF); centra o palanque em x/z; chão no topo dos degraus de baixo (z = -0,05 no arquivo); escala 0,8
R = Matrix.Rotation(math.radians(-90), 4, "Z")
box = [R @ Vector(v.co) for o in parts for v in o.data.vertices if o.name != "P_NurbsPath.003"]
lo = Vector([min(v[i] for v in box) for i in range(3)])
hi = Vector([max(v[i] for v in box) for i in range(3)])
S = 0.8
T = Matrix.Scale(S, 4) @ Matrix.Translation((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, 0.05)) @ R
for o in parts:
    o.data.transform(T)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', use_selection=True, export_animations=False)
print("OK", dst, [round(x * S, 2) for x in (hi - lo)])
