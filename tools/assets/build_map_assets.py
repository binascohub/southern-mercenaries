"""Peças dos mapas novos (Floresta, Ruínas, Cemitério), uma .glb por peça em assets/models/maps/:
- Plantas (Stylish Plants, Nobiax, CC0): Pl_Bamboo, Pl_Bush, Pl_Swirl, Pl_Hemp, Pl_Flower;
- Adereços medievais (Medieval Props Textured, Clint Bellanger, CC BY 3.0, modelos de Lamoot): Pr_*;
- Paredes destruídas (Destroyed Walls, LFA, CC BY 3.0): Ruins_Layout (a cena inteira) e a lista de
  colisores (data/ruins_colliders.json).
uso: build_map_assets.py <pasta dos downloads> <saída>"""
import bpy, sys, os, json
from mathutils import Vector, Matrix
src, out = sys.argv[sys.argv.index("--") + 1:]


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx


def export(objs, name, height=None, scale=None):
    """Põe as peças juntas, em pé, base em y = 0 e centro em x/z, na altura (m) ou na escala pedidas."""
    mn, mx = bbox(objs)
    s = scale if scale is not None else height / (mx.z - mn.z)
    for o in objs:
        o.parent = None
    shift = Matrix.Scale(s, 4) @ Matrix.Translation(Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
    for o in objs:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(shift)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, name + ".glb"), export_format="GLB", use_selection=True,
        export_image_format="JPEG", export_apply=False)
    return s


def textured_material(name, image_path, alpha=False, rough=0.85):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(image_path)
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha:
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        mat.blend_method = "CLIP" if hasattr(mat, "blend_method") else None
    bsdf.inputs["Roughness"].default_value = rough
    return mat


# --- Plantas -----------------------------------------------------------------
PLANTS = {"bamboo": ("Pl_Bamboo", "diffuse.tga", 4.0), "bush": ("Pl_Bush", "dffuse.tga", 1.3), "swirl": ("Pl_Swirl", "diffuse.tga", 1.5),
          "hemp": ("Pl_Hemp", "diffuse.tga", 1.2), "white flower": ("Pl_Flower", "diffuse.tga", 1.5)}
for folder, (name, tga, height) in PLANTS.items():
    reset()
    base = os.path.join(src, "pl", folder)
    bpy.ops.wm.obj_import(filepath=os.path.join(base, folder.replace(" ", "_") + ".obj"), forward_axis="NEGATIVE_Y", up_axis="Z")
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    mat = textured_material(name, os.path.join(base, tga), alpha=True)
    for o in objs:
        o.data.materials.clear()
        o.data.materials.append(mat)
    export(objs, name, height=height)
    print("OK", name)

# --- Adereços ----------------------------------------------------------------
PROPS = ["BrokenPillar1", "BrokenPillar2", "CoveredWell", "Cross1", "Cross2", "Cross3", "Cross4", "Fence1", "Fence2", "LampPost",
         "Obelisk1", "Obelisk2", "Obelisk3", "RoadSign", "Tombstone1", "Tombstone2", "Tombstone3", "Trough"]
for prop in PROPS:
    bpy.ops.wm.open_mainfile(filepath=os.path.join(src, "props.blend"))
    for o in list(bpy.data.objects):
        if o.name != prop:
            bpy.data.objects.remove(o, do_unlink=True)
    obj = bpy.data.objects[prop]
    IMAGES = {"Stone": "461223132.jpg", "Wood": "pine_green.jpg", "maWell": "coveredwell_diffuse.p", "maLampPost": "lamppost_diffuse.png"}
    for mat in obj.data.materials:  # as texturas estão soltas no arquivo: refaz o material com elas
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images[IMAGES[mat.name]]
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.85
    export([obj], "Pr_" + prop, scale=0.5)
    print("OK", prop)

# --- Paredes destruídas --------------------------------------------------------
reset()
bpy.ops.wm.obj_import(filepath=os.path.join(src, "dw", "destroyedWalls_UV1.obj"))
objs = [o for o in bpy.data.objects if o.type == "MESH"]
mat = textured_material("Ruins", os.path.join(src, "dw", "wall.bmp"))
for o in objs:
    o.data.materials.clear()
    o.data.materials.append(mat)
mn, mx = bbox(objs)
print("RUINS bbox", [round(x, 1) for x in mn], [round(x, 1) for x in mx])
whole = objs[0]
bpy.ops.object.select_all(action="DESELECT")
whole.select_set(True)
bpy.context.view_layer.objects.active = whole
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
SCALE = 0.25
parts = [o for o in bpy.data.objects if o.type == "MESH"]
mn, mx = bbox(parts)
cx, cy = (mn.x + mx.x) / 2, (mn.y + mx.y) / 2
colliders = []
for p in parts:
    pmn, pmx = bbox([p])
    if pmx.z - pmn.z < 3.0:
        continue  # só o que tem altura de parede bloqueia
    w, d = (pmx.x - pmn.x) * SCALE, (pmx.y - pmn.y) * SCALE
    if w < 0.3 and d < 0.3:
        continue
    colliders.append({"position": [round(((pmn.x + pmx.x) / 2 - cx) * SCALE, 2), round(-((pmn.y + pmx.y) / 2 - cy) * SCALE, 2)],
                      "size": [round(max(w, 0.4), 2), round(max(d, 0.4), 2)]})
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.join()
whole = bpy.context.view_layer.objects.active
export([whole], "Ruins_Layout", scale=SCALE)
json.dump({"_comment": "Colisores (centro e tamanho em metros, em volta do centro do Ruins_Layout) de tools/assets/build_map_assets.py", "colliders": colliders},
          open(os.path.join(src, "ruins_colliders.json"), "w"))
print("OK ruins", len(colliders), "colliders; height", round((mx.z - mn.z) * SCALE, 2))
