"""Camas (Beds, mattresses, Q_x / Sirren, para o PARPG, CC-BY-SA 3.0, opengameart.org/content/beds-mattresses): o OBJ traz
quatro camas lado a lado (colchão e travesseiros); aqui cada cama (com os travesseiros dela) vira um .glb: Bed_1 ... Bed_4,
com as texturas do pacote (512 px), escala 0,5 (cerca de 2 m de comprimento), base em y = 0, centro da planta na origem,
cabeceira (travesseiros) para -Z e o pé da cama para +Z.
uso: build_beds.py <pasta do pacote descompactado> <pasta de saída>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=os.path.join(src, "beds.obj"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
parts = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in parts:
    o.data.transform(o.matrix_world)
    o.matrix_world = Matrix.Identity(4)


def centre(o):
    xs = [v.co.x for v in o.data.vertices]
    return (min(xs) + max(xs)) / 2


bodies = [(centre(o), o) for o in sorted([o for o in parts if len(o.data.vertices) > 500], key=centre)]
pillows = [(centre(o), o) for o in parts if len(o.data.vertices) <= 500]  # a posição é guardada antes de juntar (juntar apaga os objetos)
TEX = {"material29": "pillow_1.png", "material30": "pillow_1.png", "material33": "pillow_2.png", "material34": "pillow_2.png",
       "material35": "mat_ii.png", "material36": "mat_ii.png", "material37": "mat.png", "material38": "mat.png"}
images = {}
mats = {}


def material(name):
    if name not in mats:
        m = bpy.data.materials.new("Bed_" + name)
        m.use_nodes = True
        nodes, links = m.node_tree.nodes, m.node_tree.links
        nodes.clear()
        o_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
        bsdf.inputs["Roughness"].default_value = 0.9
        f = TEX.get(name, "mat.png")
        if f not in images:
            images[f] = bpy.data.images.load(os.path.join(src, f))
        t = nodes.new("ShaderNodeTexImage"); t.image = images[f]
        links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        mats[name] = m
    return mats[name]


for i, (c, body) in enumerate(bodies, 1):
    mine = [body] + [p for pc, p in pillows if abs(pc - c) < 2.2]
    bpy.ops.object.select_all(action="DESELECT")
    for o in mine:
        for k, slot in enumerate(o.data.materials):
            o.data.materials[k] = material(slot.name)
        o.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    me = body.data
    pts = [v.co for v in me.vertices]
    mn = Vector([min(p[j] for p in pts) for j in range(3)])
    mx = Vector([max(p[j] for p in pts) for j in range(3)])
    # os travesseiros ficam no lado +Y do arquivo: a cabeceira vai para -Z do glTF (gira 180° em Z do Blender e depois +Z fica a frente)
    me.transform(Matrix.Scale(0.5, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    body.name = "Bed_%d" % i
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "Bed_%d.glb" % i), export_format="GLB", export_image_format="JPEG", use_selection=True)
    print("OK bed", i, [round((mx[j] - mn[j]) * 0.5, 2) for j in range(3)])
    bpy.data.objects.remove(body, do_unlink=True)
