"""Fire Golem (Fire_Golem.blend enviado pelo autor do projeto: golem de fogo bípede de 6,4 m feito no Blender 2.79, malha LOW_POLY1 de 14,8 mil vértices, esqueleto
metarig de 43 ossos, sem animação e sem as texturas, que ficaram fora do arquivo; autor/licença a confirmar), companheiro de Fogo do Invocador.
Sem as texturas originais, aqui a malha ganha uma textura procedural: basalto escuro com veios de lava (cor e emissão, 1024 px, assadas no UV da malha). Como é bípede,
usa os movimentos dos humanos: as animações dos heróis (Universal Animation Library, assets/models/characters/hero_male.glb) são retargetadas para o metarig quadro a quadro:
idle (Idle_Loop), walk (Walk_Loop), run (Jog_Fwd_Loop) e attack (Punch_Jab). Tronco, pescoço, cabeça e pernas copiam a rotação relativa ao repouso; os braços copiam a direção
absoluta (o golem está em A-pose e o herói em T-pose). Mesmo método de build_samurai_companion.py. Gera assets/models/props/FireGolem.glb.
uso: blender -b -P tools/assets/build_fire_golem_companion.py -- <Fire_Golem.blend> <hero_male.glb> <saida.glb>"""
import bpy, sys, math
import numpy as np
from mathutils import Vector, Quaternion, Matrix

src, hero_path, dst = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.open_mainfile(filepath=src)
sam = bpy.data.objects["metarig"]
body = bpy.data.objects["LOW_POLY1"]
meshes = [body]
for o in list(bpy.data.objects):
    if o not in (sam, body):
        bpy.data.objects.remove(o, do_unlink=True)
sam.name = "GolemArmature"
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
for im in list(bpy.data.images):  # as imagens do arquivo apontam para arquivos que não vieram
    bpy.data.images.remove(im)
while body.data.color_attributes:
    body.data.color_attributes.remove(body.data.color_attributes[0])
print("POLYS", len(body.data.polygons), "VERTS", len(body.data.vertices))


# --- textura procedural: basalto escuro com veios de lava, assada no UV da malha -------------------------------------------------------------------------
def _hash(ix, iy, iz):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def vnoise(p):
    base = np.floor(p).astype(np.int64)
    f = p - base
    f = f * f * (3 - 2 * f)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * _hash(base[:, 0] + dx, base[:, 1] + dy, base[:, 2] + dz)
    return out


def fbm(p, octaves=3):
    total, amp, freq, norm = 0.0, 0.5, 1.0, 0.0
    for _ in range(octaves):
        total = total + amp * vnoise(p * freq)
        norm += amp
        amp *= 0.5
        freq *= 2.1
    return total / norm


def bake_lava(obj, size=1024):
    me = obj.data
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    mw = obj.matrix_world
    pos = np.array([(mw @ v.co)[:] for v in me.vertices], dtype=np.float32)
    P = np.zeros((size, size, 3), dtype=np.float32)
    mask = np.zeros((size, size), dtype=bool)
    for tri in me.loop_triangles:
        t = np.array([uv[l].uv[:] for l in tri.loops], dtype=np.float32) * size
        p = pos[list(tri.vertices)]
        x0, x1 = max(int(t[:, 0].min()), 0), min(int(t[:, 0].max()) + 1, size - 1)
        y0, y1 = max(int(t[:, 1].min()), 0), min(int(t[:, 1].max()) + 1, size - 1)
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (t[1, 1] - t[2, 1]) * (t[0, 0] - t[2, 0]) + (t[2, 0] - t[1, 0]) * (t[0, 1] - t[2, 1])
        if abs(d) < 1e-9:
            continue
        w0 = ((t[1, 1] - t[2, 1]) * (xs - t[2, 0]) + (t[2, 0] - t[1, 0]) * (ys - t[2, 1])) / d
        w1 = ((t[2, 1] - t[0, 1]) * (xs - t[2, 0]) + (t[0, 0] - t[2, 0]) * (ys - t[2, 1])) / d
        w2 = 1 - w0 - w1
        inside = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
        if not inside.any():
            continue
        pts = w0[..., None] * p[0] + w1[..., None] * p[1] + w2[..., None] * p[2]
        ix, iy = np.nonzero(inside)
        P[y0 + ix, x0 + iy] = pts[ix, iy]
        mask[y0 + ix, x0 + iy] = True
    idx = np.nonzero(mask)
    q = P[idx].astype(np.float64)
    # veios: linhas onde o ruído cruza um nível (duas escalas), mais largos no peito
    n1 = fbm(q * 1.15 + 3.1, 4)
    n2 = fbm(q * 3.4 + 11.7, 3)
    v1 = np.exp(-((n1 - 0.5) / 0.03) ** 2)
    v2 = np.exp(-((n2 - 0.5) / 0.034) ** 2) * 0.8
    chest = np.exp(-(((q[:, 2] - 4.9) / 0.9) ** 2 + (q[:, 0] / 0.9) ** 2 + ((q[:, 1] + 0.25) / 0.5) ** 2))
    lava = np.clip(np.maximum(v1, v2) + chest * 0.5, 0.0, 1.0)
    grain = fbm(q * 6.0 + 0.5, 3)
    rock = np.stack([0.11, 0.085, 0.07]) [None, :] * (0.55 + 0.9 * grain)[:, None]
    hot = np.clip((lava - 0.55) / 0.45, 0, 1)[:, None]
    lava_rgb = (1.0 - hot) * np.array([1.0, 0.28, 0.03])[None, :] + hot * np.array([1.0, 0.82, 0.25])[None, :]
    albedo = rock * (1 - lava[:, None]) + lava_rgb * lava[:, None] * 0.55
    emis = lava_rgb * (lava ** 1.4)[:, None]
    A = np.zeros((size, size, 3), dtype=np.float32)
    E = np.zeros((size, size, 3), dtype=np.float32)
    A[idx] = albedo
    E[idx] = emis
    # margem de 3 texels em volta das ilhas (sem emendas visíveis)
    filled = mask.copy()
    for _ in range(3):
        grown = filled.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            shifted = np.roll(filled, (dy, dx), axis=(0, 1))
            new = shifted & ~grown
            A[new] = np.roll(A, (dy, dx), axis=(0, 1))[new]
            E[new] = np.roll(E, (dy, dx), axis=(0, 1))[new]
            grown |= shifted
        filled = grown

    def to_image(name, arr):
        im = bpy.data.images.new(name, size, size, alpha=False)
        rgba = np.ones((size, size, 4), dtype=np.float32)
        rgba[:, :, :3] = np.clip(arr, 0, 1)
        im.pixels = rgba.ravel().tolist()
        im.pack()
        return im
    img_a = to_image("FireGolem_albedo", A)
    img_e = to_image("FireGolem_emissive", E)
    mat = bpy.data.materials.new("FireGolem")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Metallic"].default_value = 0.0
    ta = nt.nodes.new("ShaderNodeTexImage"); ta.image = img_a
    te = nt.nodes.new("ShaderNodeTexImage"); te.image = img_e
    nt.links.new(ta.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(te.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 1.4
    outn = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], outn.inputs["Surface"])
    me.materials.clear()
    me.materials.append(mat)
    print("BAKED", int(mask.sum()), "texels, lava mean", round(float(lava.mean()), 3))


bake_lava(body)

# herói: só o esqueleto e as animações
bpy.ops.import_scene.gltf(filepath=hero_path)
hero = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o is not sam)
hero_meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o not in meshes]
for o in hero_meshes:
    bpy.data.objects.remove(o, do_unlink=True)
hero.name = "HeroArmature"
scene = bpy.context.scene
scene.render.fps = 24
for o in meshes:
    o.hide_viewport = True  # sem as malhas na avaliação, cada atualização da pose é barata

MAP = {"spine": "pelvis", "spine.001": "spine_01", "spine.002": "spine_02", "spine.003": "spine_03", "spine.004": "neck_01", "Head": "Head"}
for side, s_ in (("L", "l"), ("R", "r")):
    MAP.update({f"shoulder.{side}": f"clavicle_{s_}", f"upper_arm.{side}": f"upperarm_{s_}", f"forearm.{side}": f"lowerarm_{s_}", f"hand.{side}": f"hand_{s_}",
                f"thigh.{side}": f"thigh_{s_}", f"shin.{side}": f"calf_{s_}", f"foot.{side}": f"foot_{s_}", f"toe.{side}": f"ball_{s_}"})
DIRECTION_ONLY = {"upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R", "hand.L", "hand.R"}  # o golem está em A-pose e o herói em T-pose
LEG_AMPLITUDE = 0.9
CLIPS = {"idle": "Idle_Loop", "walk": "Walk_Loop", "run": "Jog_Fwd_Loop", "attack": "Punch_Jab"}

spb, hpb = sam.pose.bones, hero.pose.bones
for p in spb:
    p.rotation_mode = 'QUATERNION'
sam.animation_data_create()
hero.animation_data_create()
sRw = sam.matrix_world.to_3x3().normalized()
sM = sam.matrix_world
hRw = hero.matrix_world.to_3x3().normalized()


def rot_rest_world(arm, bone):
    return (arm.matrix_world @ bone.matrix_local).to_3x3().normalized()


def dir_rest_world(arm, bone):
    return (arm.matrix_world.to_3x3() @ (bone.tail_local - bone.head_local)).normalized()


def dir_pose_world(arm, pb):
    return (arm.matrix_world.to_3x3() @ (pb.tail - pb.head)).normalized()


def depth_order(arm):
    order = []

    def rec(b):
        order.append(b.name)
        for c in b.children:
            rec(c)
    for b in arm.data.bones:
        if b.parent is None:
            rec(b)
    return order


ORDER = [n for n in depth_order(sam) if n in MAP]
sam_h = (sM @ sam.data.bones["spine"].head_local).z
hero_h = (hero.matrix_world @ hero.data.bones["pelvis"].head_local).z
K = sam_h / hero_h
sam_hips_rest = sM @ sam.data.bones["spine"].head_local
hero_pelvis_rest = hero.matrix_world @ hero.data.bones["pelvis"].head_local
print("HIPS", round(sam_h, 3), round(hero_h, 3), "K", round(K, 3))


def retarget_frame():
    bpy.context.view_layer.update()
    for name in ORDER:
        sb = sam.data.bones[name]
        pb = spb[name]
        hb = hero.data.bones[MAP[name]]
        hp = hpb[MAP[name]]
        if sb.parent:
            parent_pb = spb[sb.parent.name]
            base = parent_pb.matrix @ (sb.parent.matrix_local.inverted() @ sb.matrix_local)
        else:
            base = sb.matrix_local.copy()
        if name in DIRECTION_ONLY:
            q = dir_rest_world(sam, sb).rotation_difference(dir_pose_world(hero, hp))
            target = q.to_matrix() @ rot_rest_world(sam, sb)
        else:
            pose_rot = (hero.matrix_world @ hp.matrix).to_3x3().normalized()
            delta = pose_rot @ rot_rest_world(hero, hb).inverted()
            if name.startswith(("thigh", "shin")):  # passada mais curta: o golem tem as pernas curtas e pesadas
                delta = Quaternion().slerp(delta.to_quaternion(), LEG_AMPLITUDE).to_matrix()
            target = delta @ rot_rest_world(sam, sb)
        local_rot = sRw.inverted() @ target
        loc = base.to_translation()
        if name == "spine":
            disp = (hero.matrix_world @ hp.head) - hero_pelvis_rest
            loc = sM.inverted() @ (sam_hips_rest + disp * K)
        m = Matrix.Translation(loc) @ local_rot.to_4x4()
        pb.matrix = m
        bpy.context.view_layer.update()


def key_frame(frame):
    for p in spb:
        p.keyframe_insert("rotation_quaternion", frame=frame)
        if p.name == "spine":
            p.keyframe_insert("location", frame=frame)


for out_name, src_name in CLIPS.items():
    action_src = bpy.data.actions[src_name]
    f0, f1 = int(action_src.frame_range[0]), int(action_src.frame_range[1])
    hero.animation_data.action = action_src
    if hasattr(hero.animation_data, "action_slot") and action_src.slots:
        hero.animation_data.action_slot = action_src.slots[0]
    for p in spb:
        p.rotation_quaternion = Quaternion((1, 0, 0, 0))
        p.location = Vector((0, 0, 0))
    new = bpy.data.actions.new(out_name)
    new.use_fake_user = True
    sam.animation_data.action = new
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        retarget_frame()
        key_frame(f - f0 + 1)
    print("CLIP", out_name, "<-", src_name, "frames", f1 - f0 + 1)

def natural_speed(arm, bone_names, hips_name, name, source_action=None):
    """Velocidade no chão em que os pés não patinam: o pé de apoio anda para trás em relação ao quadril; passada (amplitude do pé) dividida pelo tempo de apoio."""
    action = source_action or bpy.data.actions[name]
    arm.animation_data.action = action
    if hasattr(arm.animation_data, "action_slot") and action.slots:
        arm.animation_data.action_slot = action.slots[0]
    f0, f1 = int(action.frame_range[0]), int(action.frame_range[1])
    period = (f1 - f0 + 1) / 24.0
    speeds = []
    for foot in bone_names:
        fwd = []
        for f in range(f0, f1 + 1):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            rel = (arm.matrix_world @ arm.pose.bones[foot].head) - (arm.matrix_world @ arm.pose.bones[hips_name].head)
            fwd.append(-rel.y)
        stride = max(fwd) - min(fwd)
        back = sum(1 for i in range(len(fwd) - 1) if fwd[i] > fwd[i + 1])
        duty = max(back / max(len(fwd) - 1, 1), 0.2)
        speeds.append(stride / (duty * period))
        print("   ", arm.name, foot, name, "passada", round(stride, 3), "apoio", round(duty, 2), "ciclo", round(period, 2), "s")
    return sum(speeds) / len(speeds)


for clip_name, hero_clip in (("walk", "Walk_Loop"), ("run", "Jog_Fwd_Loop")):
    mine = natural_speed(sam, ("foot.L", "foot.R"), "spine", clip_name)
    ref = natural_speed(hero, ("foot_l", "foot_r"), "pelvis", hero_clip, bpy.data.actions[hero_clip])
    print("NATURAL SPEED", clip_name, "golem", round(mine, 3), "m/s (arquivo) |", "herói", round(ref, 3), "m/s")
for p in spb:
    p.rotation_quaternion = Quaternion((1, 0, 0, 0))
    p.location = Vector((0, 0, 0))
hero.animation_data.action = None
for a in list(bpy.data.actions):
    if a.name not in CLIPS:
        bpy.data.actions.remove(a)
bpy.data.objects.remove(hero, do_unlink=True)
for o in meshes:
    o.hide_viewport = False
print("ACTIONS", [(a.name, tuple(round(x) for x in a.frame_range)) for a in bpy.data.actions])
for o in bpy.data.objects:
    o.select_set(o in meshes or o is sam)
bpy.context.view_layer.objects.active = sam
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_image_format='WEBP', export_animations=True,
                          export_animation_mode='ACTIONS', export_skins=True, use_selection=True, export_force_sampling=True, export_morph=False)
print("OK", dst)
