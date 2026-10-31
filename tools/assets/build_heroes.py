"""Monta hero_male.glb e hero_female.glb (Quaternius, CC0): o esqueleto e as 43
animações do Universal Animation Library; do Universal Base Characters só a
cabeça (olhos, sobrancelhas) e os cabelos; as roupas de Camponês e Ranger do
Modular Character Outfits - Fantasy, peça por peça. Texturas em 1024 (cabelo 512).
Opcional: as 43 animações a mais do Universal Animation Library 2 (CC0, mesmo
esqueleto): combos de espada, escudo, arremesso, beber, abrir baú, empurrão,
zumbi (a Rainha dos Ratos), braços cruzados, lampião.
uso: build_heroes.py <UAL1.glb> <pasta UBC> <pasta das roupas> <saída> [UAL2.glb]"""
import bpy, bmesh, sys, os
args = sys.argv[sys.argv.index("--") + 1:]
ual, ubc, outfits, out_dir = args[:4]
ual2 = args[4] if len(args) > 4 else ""
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

def cut_to_head(o, z_cut, keep_head=True):
    """keep_head: só a cabeça ("Head"); senão, o corpo sem a cabeça ("Skin": a
    pele com a roupa de baixo, à mostra só em quem usa roupa curta)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    mw = o.matrix_world
    gone = [v for v in bm.verts if ((mw @ v.co).z > z_cut and abs((mw @ v.co).x) < 0.2) != keep_head]
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
    if ual2:
        # Só as ações (mesmos nomes de ossos); o manequim e o esqueleto dele saem.
        before = set(bpy.data.actions)
        for o in imported(ual2):
            bpy.data.objects.remove(o, do_unlink=True)
        for action in set(bpy.data.actions) - before:
            if action.name.startswith("A_TPose"):
                bpy.data.actions.remove(action)
    base = adopt(imported(os.path.join(ubc, "Base Characters/Godot - UE/Superhero_%s_FullBody.gltf" % sex)), arm)
    for o in base:
        if o.name.lower().startswith("superhero"):
            skin = o.copy()
            skin.data = o.data.copy()
            bpy.context.scene.collection.objects.link(skin)
            o.name = "Head"
            cut_to_head(o, CUT[sex])
            skin.name = "Skin"
            cut_to_head(skin, CUT[sex], keep_head=False)
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
