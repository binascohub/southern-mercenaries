"""Peças do Deserto (Canyon Terrain Asset, loafbrr / Ian87, CC0, opengameart.org/content/canyon-terrain-asset): o pacote traz tudo num .glb
(CanyonPlantsRocksTiles.glb, 160 objetos, sem texturas embutidas e feito para o addon Terrain3D); aqui cada peça vira um .glb próprio em
assets/models/maps/desert/ (Canyon_<nome>.glb): formações e plataformas de rocha, pedregulhos, cactos, árvores secas, capim, galhos e folhas,
com a textura de cor e a normal do pacote (paredes e pedras em 256 px, plantas em 256 e o piso em 512, JPG), base em y = 0 e centro da planta na origem. Também gera o piso
de 2 x 2 m `Ground_Canyon.glb` (areia/terra do cânion) em assets/models/maps/.
uso: blender -b -P build_canyon_pieces.py -- <pasta do pacote extraído> <pasta assets/models/maps>"""
import bpy, sys, os
from mathutils import Vector, Matrix
src, maps_dir = sys.argv[sys.argv.index("--") + 1:]
out_dir = os.path.join(maps_dir, "desert")
os.makedirs(out_dir, exist_ok=True)
TEX = os.path.join(src, "tex")  # texturas já reduzidas (PNG de 16 bits -> JPG/PNG de 8 bits, 256 a 512 px) em <pasta do pacote>/tex
SETS = {"CanyonGround": ("CanyonGround", 512), "CanyonWall_3": ("CanyonWall_3", 256), "Rocks": ("Rocks", 256),
        "Plant_1": ("Plants_2", 256), "Plant_2": ("Plants_2", 256)}
PIECES = ([f"Rock_Formations_{i}" for i in range(1, 13)] + [f"Rock_Platforms_{i}" for i in range(1, 11)] + [f"Rock_Boulders_{i}" for i in range(1, 7)]
          + [f"Cactus_Tall_{i}" for i in range(1, 6)] + [f"Cactus_Small_{i}" for i in range(1, 6)] + [f"Cactus_Flat_{i}" for i in range(1, 4)]
          + [f"Tree_{i}" for i in range(1, 5)] + ["Grass_1", "Grass_6", "Grass_10", "Sticks_1", "Sticks_2", "Leafs_1"])
_images = {}


def image(path, size, normal=False):
    key = (path, size, normal)
    if key not in _images:
        img = bpy.data.images.load(path)
        if normal:
            img.colorspace_settings.name = "Non-Color"
        _images[key] = img
    return _images[key]


def material(name):
    base, size = SETS.get(name.split(".")[0], SETS["CanyonWall_3"])
    key = "M_" + name.split(".")[0]
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    nodes.clear()
    o_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], o_node.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.9
    diffuse = os.path.join(TEX, base + "_Diffuse.jpg")
    if not os.path.exists(diffuse):
        diffuse = os.path.join(TEX, base + "_Diffuse.png")
    c = nodes.new("ShaderNodeTexImage"); c.image = image(diffuse, size)
    links.new(c.outputs["Color"], bsdf.inputs["Base Color"])
    normal_path = os.path.join(TEX, base + "_Normal.jpg")
    if os.path.exists(normal_path):
        n = nodes.new("ShaderNodeTexImage"); n.image = image(normal_path, size, True)
        nm = nodes.new("ShaderNodeNormalMap")
        links.new(n.outputs["Color"], nm.inputs["Color"]); links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    if name.startswith("Plant"):
        bsdf.inputs["Alpha"].default_value = 1.0
        m.blend_method = "CLIP" if hasattr(m, "blend_method") else None
        links.new(c.outputs["Alpha"], bsdf.inputs["Alpha"])
    return m


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(src, "glb", "CanyonPlantsRocksTiles.glb"))
objs = {o.name: o for o in bpy.context.scene.objects if o.type == "MESH"}
deps = bpy.context.evaluated_depsgraph_get()
made = 0
for name in PIECES:
    if name not in objs:
        print("FALTA", name)
        continue
    parts = [objs[name]] + [c for c in objs[name].children if not c.name.endswith("-colonly")]
    meshes = []
    for o in parts:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)
        me.transform(o.matrix_world)
        slots = [m.name for m in o.data.materials] or ["CanyonWall_3"]
        me.materials.clear()
        for s in slots:
            me.materials.append(material(s))
        meshes.append(me)
    pts = [v.co for me in meshes for v in me.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    fix = Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
    for obj_ in list(bpy.data.objects):
        if obj_.name.startswith("Canyon_"):
            bpy.data.objects.remove(obj_, do_unlink=True)
    for k, me in enumerate(meshes):
        me.transform(fix)
        ob = bpy.data.objects.new("Canyon_%s_%d" % (name, k), me)
        bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in [o for o in bpy.data.objects if o.name.startswith("Canyon_")]:
        ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out_dir, "Canyon_%s.glb" % name), export_format="GLB", export_image_format="JPEG", use_selection=True)
    made += 1
# Piso de 2 x 2 m
for obj_ in list(bpy.data.objects):
    if obj_.name.startswith("Canyon_"):
        bpy.data.objects.remove(obj_, do_unlink=True)
me = bpy.data.meshes.new("Ground_Canyon")
me.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
uv = me.uv_layers.new(name="UVMap")
for li, (u, v) in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
    uv.data[li].uv = (u, v)
me.materials.append(material("CanyonGround"))
ob = bpy.data.objects.new("Ground_Canyon", me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.object.select_all(action="DESELECT")
ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(maps_dir, "Ground_Canyon.glb"), export_format="GLB", export_image_format="JPEG", use_selection=True)
print("OK canyon", made, "peças")
