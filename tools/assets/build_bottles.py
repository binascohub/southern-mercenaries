"""Garrafas (bottles.zip enviado pelo autor do projeto: Bottle_1 a Bottle_4 (garrafa e rolha, sem material) e Bottle_set_1 a Bottle_set_4 (grupos de 6 a 11 garrafas numa malha só, com uma textura
"Bottle_old_material" que NÃO veio no pacote; autor/licença a confirmar)). Sem texturas, a cor vem de materiais lisos: cada garrafa avulsa tem um vidro (verde, âmbar, azul, vinho) e rolha;
nos grupos, cada garrafa (parte solta da malha) recebe um vidro da paleta e as partes pequenas no alto viram rolha. Tudo em pé, centrado em x/z e com a base em y = 0.
Gera assets/models/props/Bottle_1.glb a Bottle_4.glb e Bottle_set_1.glb a Bottle_set_4.glb.
uso: blender -b -P tools/assets/build_bottles.py -- <pasta com os .fbx> <pasta de saída>"""
import bpy, bmesh, sys, os
from mathutils import Vector, Matrix

src, outdir = sys.argv[sys.argv.index("--") + 1:][:2]
GLASS = [(0.10, 0.34, 0.14), (0.48, 0.24, 0.06), (0.10, 0.20, 0.48), (0.28, 0.05, 0.10), (0.62, 0.74, 0.72)]
CORK = (0.58, 0.40, 0.22)
SINGLE_GLASS = {1: 0, 2: 1, 3: 2, 4: 3}


def material(name, color, rough=0.2):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*color, 1)
        b.inputs["Roughness"].default_value = rough
    return m


def finish(meshes, dst):
    box = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector([min(v[i] for v in box) for i in range(3)])
    hi = Vector([max(v[i] for v in box) for i in range(3)])
    for o in meshes:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(Matrix.Translation((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z)))
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', use_selection=True, export_animations=False)
    print("OK", os.path.basename(dst), len(meshes), [round(x, 2) for x in (hi - lo)])


for n in (1, 2, 3, 4):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(src, "Bottle_%d.fbx" % n))
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    for o in meshes:
        glass = "cork" not in o.name.lower()
        o.data.materials.clear()
        o.data.materials.append(material("m_glass_%d" % SINGLE_GLASS[n], GLASS[SINGLE_GLASS[n]]) if glass else material("m_cork", CORK, 0.8))
    finish(meshes, os.path.join(outdir, "Bottle_%d.glb" % n))

for n in (1, 2, 3, 4):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(src, "Bottle_set_%d.fbx" % n))
    body = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    parts = [o for o in bpy.data.objects if o.type == 'MESH']
    top = max((o.matrix_world @ Vector(c)).z for o in parts for c in o.bound_box)
    glass_i = 0
    for o in parts:
        zs = [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
        high, size = max(zs), max(zs) - min(zs)
        o.data.materials.clear()
        if size < 0.09 and min(zs) > top * 0.35:
            o.data.materials.append(material("m_cork", CORK, 0.8))
        else:
            o.data.materials.append(material("m_glass_%d" % (glass_i % len(GLASS)), GLASS[glass_i % len(GLASS)]))
            glass_i += 1
    print("PARTES", n, len(parts), "vidros", glass_i)
    finish(parts, os.path.join(outdir, "Bottle_set_%d.glb" % n))
