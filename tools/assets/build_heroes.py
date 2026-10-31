"""Monta hero_male.glb e hero_female.glb (Quaternius, CC0): o esqueleto e as 43
animações do Universal Animation Library; do Universal Base Characters só a
cabeça (olhos, sobrancelhas) e os cabelos; as roupas de Camponês e Ranger do
Modular Character Outfits - Fantasy, peça por peça. Texturas em 1024 (cabelo 512)."""
import bpy, bmesh, sys, os
args = sys.argv[sys.argv.index("--") + 1:]
ual, ubc, outfits, out_dir = args
CUT = {"Male": 1.50, "Female": 1.46}
HAIR = {"Male": ["Hair_SimpleParted", "Hair_Buzzed", "Hair_Beard"], "Female": ["Hair_Long", "Hair_Buns", "Hair_BuzzedFemale"]}

def imported(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]

def adopt(objs, arm, prefix=""):
    """Prende as malhas ao esqueleto principal e apaga o esqueleto importado."""
    keep = []
    names = [o.name for o in objs]
    for n in list(names):
        o = bpy.data.objects.get(n)
        if o and o.type == "MESH" and n.startswith("Icosphere"):
            bpy.data.objects.remove(o, do_unlink=True)
            names.remove(n)
    objs = [bpy.data.objects[n] for n in names if n in bpy.data.objects]
    for o in [o for o in objs if o.type == "MESH"]:
        mw = o.matrix_world.copy()
        o.parent = arm
        o.matrix_world = mw
        for m in o.modifiers:
            if m.type == "ARMATURE":
                m.object = arm
        if not any(m.type == "ARMATURE" for m in o.modifiers):
            mod = o.modifiers.new("Armature", "ARMATURE")
            mod.object = arm
        if prefix and not o.name.startswith(prefix):
            o.name = prefix + o.name
        keep.append(o)
    for o in [o for o in objs if o.type == "ARMATURE" and o != arm]:
        bpy.data.objects.remove(o, do_unlink=True)
    return keep

def cut_to_head(o, z_cut):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    mw = o.matrix_world
    gone = [v for v in bm.verts if not ((mw @ v.co).z > z_cut and abs((mw @ v.co).x) < 0.2)]
    bmesh.ops.delete(bm, geom=gone, context="VERTS")
    bm.to_mesh(o.data)
    bm.free()

for sex in ["Male", "Female"]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = imported(ual)
    arm = [o for o in objs if o.type == "ARMATURE"][0]
    arm.name = "Armature"
    for o in objs:
        if o.type == "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    base = adopt(imported(os.path.join(ubc, "Base Characters/Godot - UE/Superhero_%s_FullBody.gltf" % sex)), arm)
    for o in base:
        if o.name.lower().startswith("superhero"):
            o.name = "Head"
            cut_to_head(o, CUT[sex])
    for hair in HAIR[sex]:
        path = os.path.join(ubc, "Hairstyles/Rigged to Head Bone/glTF (Godot -Unreal)/%s.gltf" % hair)
        for o in adopt(imported(path), arm):
            o.name = hair
    for outfit in ["Peasant", "Ranger"]:
        adopt(imported(os.path.join(outfits, "%s_%s.gltf" % (sex, outfit))), arm)
    # Nomes curtos: Peasant_Body, Ranger_Head_Hood…
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith(sex + "_"):
            o.name = o.name[len(sex) + 1:].split(".")[0]
    for img in bpy.data.images:
        if img.size[0] > 1024:
            side = 512 if "Hair" in img.name else 1024
            img.scale(side, side)
    arm.animation_data_create()
    arm.animation_data.action = bpy.data.actions.get("Idle_Loop")
    out = os.path.join(out_dir, "hero_%s.glb" % sex.lower())
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animation_mode="ACTIONS",
        export_image_format="JPEG", export_jpeg_quality=85, export_apply=False)
    print("WROTE", out, os.path.getsize(out), sorted(o.name for o in bpy.data.objects if o.type == "MESH"))
