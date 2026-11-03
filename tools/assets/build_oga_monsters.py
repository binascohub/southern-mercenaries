"""Converte monstros baixados de fora (OpenGameArt, todos CC0) em .glb de malha única, parada, em assets/models/monsters/ (o jogo os anima por código: `static`).
Para cada um: abre o arquivo de origem, junta as malhas na pose de repouso (aplicando modificadores e a armadura), gira para a frente ficar em -Y do Blender (+Z no glTF),
põe os pés em y = 0, centraliza e escala para a MAIOR dimensão ficar com 1 m (o jogo multiplica pelo `scale` e pelo `size` de cada monstro). `flat` troca os materiais por uma cor só
(para quem veio sem as texturas).
uso: blender -b -P tools/assets/build_oga_monsters.py -- <pasta com os arquivos baixados> <pasta de saída> [nome ...]"""
import bpy, sys, os, math, json
from mathutils import Vector, Matrix

args = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = args[0], args[1]
ONLY = set(args[2:])
# nome: (arquivo relativo, giro em graus em volta de Z, cor lisa ou None)
SPECS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "oga_monsters.json")))


def import_any(path):
    p = path.lower()
    if p.endswith(".blend"):
        bpy.ops.wm.open_mainfile(filepath=path)
    elif p.endswith((".glb", ".gltf")):
        bpy.ops.import_scene.gltf(filepath=path)
    elif p.endswith(".fbx"):
        bpy.ops.import_scene.fbx(filepath=path)
    elif p.endswith(".obj"):
        bpy.ops.wm.obj_import(filepath=path)


def flat_material(rgb):
    """Cor lisa como TEXTURA de 4 x 4 pixels (o jogo troca a cor-base dos materiais pela cor do monstro, então a cor lisa precisa vir de uma textura)."""
    img = bpy.data.images.new("FlatColor", 4, 4)
    img.pixels = [c for _ in range(16) for c in (rgb[0], rgb[1], rgb[2], 1.0)]
    img.pack()
    m = bpy.data.materials.new("Flat")
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    b = nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.7
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    links.new(tex.outputs["Color"], b.inputs["Base Color"])
    return m


for name, spec in SPECS.items():
    if ONLY and name not in ONLY:
        continue
    path = os.path.join(SRC, spec["file"])
    if not os.path.exists(path):
        print("FALTA", name, path)
        continue
    if not path.lower().endswith(".blend"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
    import_any(path)
    scene = bpy.context.scene
    scene.frame_set(spec.get("frame", 1))
    deps = bpy.context.evaluated_depsgraph_get()
    parts = []
    for o in [o for o in scene.objects if o.type == "MESH" and not o.hide_render and not o.hide_viewport]:
        if spec.get("skip") and any(s in o.name for s in spec["skip"]):
            continue
        me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        me.transform(o.matrix_world)
        parts.append(me)
    for o in list(scene.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    objs = []
    for me in parts:
        ob = bpy.data.objects.new(name, me)
        scene.collection.objects.link(ob)
        objs.append(ob)
    if not objs:
        print("SEM MALHA", name)
        continue
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objs:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if spec.get("flat"):
        mat = flat_material(spec["flat"])
        for ob in objs:
            ob.data.materials.clear()
            ob.data.materials.append(mat)
    bpy.ops.object.join()
    whole = bpy.context.view_layer.objects.active
    whole.name = whole.data.name = name
    whole.data.transform(Matrix.Rotation(math.radians(spec.get("yaw", 0.0)), 4, "Z"))
    pts = [v.co for v in whole.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    big = max(mx.x - mn.x, mx.y - mn.y, mx.z - mn.z)
    whole.data.transform(Matrix.Scale(1.0 / big, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
    bpy.ops.object.select_all(action="DESELECT")
    whole.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, name + ".glb"), export_format="GLB", use_selection=True, export_image_format="WEBP", export_image_quality=80)
    print("OK", name, "%d vértices, %.1f x %.1f x %.1f antes" % (len(whole.data.vertices), mx.x - mn.x, mx.y - mn.y, mx.z - mn.z))
