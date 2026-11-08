"""Torcida de Tortuga ("Background People add-on for Blender", Jungle Jim, CC BY 4.0, Sketchfab): 7 pessoas escaneadas, de pouca malha (~1.100 triângulos cada), com
esqueleto próprio e uma animação de torcida em comum ("Scene": pulam, batem palmas, erguem os braços, dançam). Ficam 6 (a moça que faz acrobacia no chão sai).
Cada pessoa vira um arquivo: assets/models/characters/crowd_cheer_<n>.glb, com a animação "cheer", os pés em z = 0, o quadril no meio e a frente para -Y (a dos heróis).
Roupa medieval: as roupas de hoje (jeans, jaqueta, camiseta com logo) são repintadas na textura pela região do corpo (o osso que mais pesa em cada face): túnica no tronco
e nos braços, meia-calça ou calça de lã nas pernas (nas mulheres, a cor da túnica: vestido longo), botas de couro nos pés e um cinto na cintura. A dobra do pano fica
(o claro e escuro da textura, suavizado para apagar estampas); cabeça, pescoço, mãos e a pele dos braços ficam como vieram.
uso: blender -b -P tools/assets/build_background_people.py -- <background_people_add-on_for_blender.glb> <pasta de saída>"""
import bpy, sys, math
import numpy as np
from mathutils import Matrix, Vector

src, out_dir = sys.argv[sys.argv.index("--") + 1:][:2]
# material da pessoa -> (arquivo, túnica, pernas, mulher?) em sRGB 0..1
PEOPLE = {
    "BuMan10_Bake": ("crowd_cheer_1", (0.80, 0.74, 0.60), (0.36, 0.26, 0.17), False),  # linho cru, calça marrom
    "Man10_Bake": ("crowd_cheer_2", (0.34, 0.40, 0.24), (0.45, 0.35, 0.22), False),    # verde musgo, calça ocre
    "Man11_Bake": ("crowd_cheer_3", (0.46, 0.16, 0.13), (0.27, 0.26, 0.24), False),    # vinho, calça cinza-escura
    "Man12_Bake": ("crowd_cheer_4", (0.62, 0.47, 0.22), (0.25, 0.18, 0.12), False),    # mostarda, calça marrom-escura
    "Woman10_Bake": ("crowd_cheer_5", (0.24, 0.32, 0.47), None, True),                 # vestido azul-anil
    "Woman14_Bake": ("crowd_cheer_6", (0.52, 0.20, 0.16), None, True),                 # vestido vermelho-tijolo
}
BOOTS = (0.22, 0.14, 0.08)
BELT = (0.20, 0.13, 0.08)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene = bpy.context.scene
scene.frame_set(1)
for a in bpy.data.actions:
    a.name = "cheer"


def region(group_name):
    n = group_name.lower()
    if "head" in n or "neck" in n:
        return "keep"
    if "hand" in n:
        return "hand"
    if "foot" in n:
        return "foot"
    if "thigh" in n or "calf" in n:
        return "leg"
    if "upperarm" in n or "forearm" in n:
        return "arm"
    if "hip" in n or "pelvis" in n:
        return "hip"
    return "torso"


def box_blur(img, r):
    k = 2 * r + 1
    pad = np.pad(img, ((r, r), (r, r)), mode="edge")
    c = pad.cumsum(axis=0).cumsum(axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def raster(tris_uv, tris_z, w, h):
    """Índice da face em cada pixel (-1 = nenhuma) e a altura do corpo (z da pose de descanso) naquele pixel; os triângulos ganham ~1,5 px de margem
    para não abrir costura."""
    idx = np.full((h, w), -1, dtype=np.int32)
    zmap = np.zeros((h, w), dtype=np.float32)
    for fi, tri in enumerate(tris_uv):
        p = tri * np.array([w, h]) - 0.5
        x0, y0 = np.floor(p.min(axis=0) - 2).astype(int)
        x1, y1 = np.ceil(p.max(axis=0) + 2).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, w - 1), min(y1, h - 1)
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        q = np.stack([xs, ys], axis=-1).astype(float)
        inside = np.ones(xs.shape, dtype=bool)
        for i in range(3):
            a, b = p[i], p[(i + 1) % 3]
            e = b - a
            ln = math.hypot(e[0], e[1]) + 1e-9
            # distância com sinal até a aresta (o lado de dentro depende da ordem dos vértices)
            d = (e[0] * (q[..., 1] - a[1]) - e[1] * (q[..., 0] - a[0])) / ln
            area = (p[1][0] - p[0][0]) * (p[2][1] - p[0][1]) - (p[1][1] - p[0][1]) * (p[2][0] - p[0][0])
            inside &= (d * np.sign(area if area != 0 else 1)) >= -1.5
        sub = idx[y0:y1 + 1, x0:x1 + 1]
        new = inside & (sub < 0)
        sub[new] = fi
        # altura por coordenadas baricêntricas (fora do triângulo, na margem, limitadas)
        m = np.array([[p[0][0] - p[2][0], p[1][0] - p[2][0]], [p[0][1] - p[2][1], p[1][1] - p[2][1]]])
        if abs(np.linalg.det(m)) > 1e-9:
            inv = np.linalg.inv(m)
            l12 = np.einsum("ij,...j->...i", inv, q - p[2])
            l = np.clip(np.concatenate([l12, 1 - l12.sum(axis=-1, keepdims=True)], axis=-1), 0, 1)
            l /= np.maximum(l.sum(axis=-1, keepdims=True), 1e-9)
            zsub = zmap[y0:y1 + 1, x0:x1 + 1]
            zsub[new] = (l @ np.array(tris_z[fi]))[new]
    return idx, zmap


def repaint(mesh_obj, tunic, legs, woman):
    me = mesh_obj.data
    mat = me.materials[0]
    tex = next(n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and any(l.to_socket.name == "Base Color" for l in n.outputs[0].links))
    img = tex.image
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    groups = {g.index: region(g.name) for g in mesh_obj.vertex_groups}
    vreg = []
    for v in me.vertices:
        best = max(v.groups, key=lambda g: g.weight, default=None)
        vreg.append(groups.get(best.group, "torso") if best else "torso")
    # altura do cinto: a cintura do esqueleto (osso Waist) na pose do arquivo
    arm = mesh_obj.find_armature()
    to_mesh = mesh_obj.matrix_world.inverted() @ arm.matrix_world  # ossos na pose de descanso, como os vértices da malha
    waist_z = (to_mesh @ next(b for b in arm.data.bones if "Waist" in b.name).head_local).z
    hip_z = (to_mesh @ next(b for b in arm.data.bones if "Hip" in b.name).head_local).z
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    tris, freg, tz = [], [], []
    for t in me.loop_triangles:
        tris.append(np.array([uv[l].uv[:] for l in t.loops]))
        regs = [vreg[i] for i in t.vertices]
        freg.append(max(set(regs), key=regs.count))
        tz.append([me.vertices[i].co.z for i in t.vertices])
    idx, zmap = raster(tris, tz, w, h)
    rgb = px[..., :3]
    # cor da pele: a das mãos
    hand_mask = np.isin(idx, [i for i, r in enumerate(freg) if r == "hand"])
    skin = np.median(rgb[hand_mask], axis=0) if hand_mask.any() else np.array([0.7, 0.5, 0.4])
    face_col = np.zeros((len(tris), 3))
    flat = idx.ravel()
    ok = flat >= 0
    sums = np.zeros((len(tris), 3))
    np.add.at(sums, flat[ok], rgb.reshape(-1, 3)[ok])
    cnt = np.bincount(flat[ok], minlength=len(tris))[:, None]
    face_col = sums / np.maximum(cnt, 1)
    belt_half = abs(waist_z - hip_z) * 0.35
    belt_mid = waist_z - (waist_z - hip_z) * 0.15
    floor_z = min(v.co.z for v in me.vertices)
    hem_z = hip_z - (hip_z - floor_z) * 0.22  # a túnica desce até o meio da coxa: barra reta, sem o recorte da jaqueta
    # tipo de cada face: 0 = fica como veio, 1 = braço (só túnica), 2 = tronco, 3 = perna/quadril, 4 = pé (bota)
    kind = np.zeros(len(tris) + 1, dtype=np.int8)  # o último índice é o "nenhuma face" (-1)
    for fi, r in enumerate(freg):
        if r in ("keep", "hand"):
            continue
        if r == "arm" and np.linalg.norm(face_col[fi] - skin) < 0.12 and face_col[fi][0] - face_col[fi][2] > 0.06:
            continue  # pele à mostra no braço (a pele puxa para o vermelho; a lã bege não)
        kind[fi] = {"arm": 1, "torso": 2, "hip": 3, "leg": 3, "foot": 4}[r]
    k = kind[idx]
    # cinto, barra e pernas pela altura de cada pixel: linhas retas, sem o serrilhado dos triângulos
    belt = ((k == 2) | (k == 3)) & (np.abs(zmap - belt_mid) < belt_half)
    lower = (k == 3) & (zmap < hem_z) & ~belt
    masks = {BELT: belt, BOOTS: k == 4, tunic: (k > 0) & (k < 4) & ~belt & ~lower}
    if woman:
        masks[tunic] = masks[tunic] | lower
    else:
        masks[legs] = lower
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    lum_s = box_blur(lum, 3) * 0.6 + lum * 0.4  # tira a estampa e o logo, deixa a dobra
    rng = np.random.default_rng(7)
    noise = box_blur(rng.standard_normal((h, w)).astype(np.float32), 1) * 0.05
    for color, mask in masks.items():
        if not mask.any():
            continue
        shade = lum_s[mask] / max(float(np.median(lum[mask])), 0.05)
        shade = np.clip(shade, 0.55, 1.3) * (1.0 + noise[mask])
        c = np.array(color)
        c = (c * 0.7 + c.mean() * 0.3) * 0.85  # tons de tinta vegetal: menos saturados e mais escuros
        rgb[mask] = np.clip(c[None, :] * shade[:, None], 0, 1)
    px[..., :3] = rgb
    img.pixels[:] = px.ravel()
    img.pack()
    print("  pintado", mat.name, "pele", skin.round(2), "faces repintadas", int((kind > 0).sum()), "/", len(tris))


people = [o for o in bpy.data.objects if o.type == "MESH" and o.find_armature() and o.data.materials and o.data.materials[0].name in PEOPLE]
for o in [o for o in bpy.data.objects if o.type == "MESH" and o not in people]:
    bpy.data.objects.remove(o, do_unlink=True)
for p in people:
    name, tunic, legs, woman = PEOPLE[p.data.materials[0].name]
    print("PESSOA", p.data.materials[0].name, "->", name)
    repaint(p, tunic, legs, woman)
    arm = p.find_armature()
    # frente: perpendicular à linha dos quadris e dos ombros (esquerda - direita), levada para -Y; pés em z = 0; quadril no meio
    bpy.context.view_layer.update()

    def at(part):
        return arm.matrix_world @ next(b for b in arm.pose.bones if part in b.name).head
    side = (at("L_Thigh") - at("R_Thigh")) + (at("L_Upperarm") - at("R_Upperarm"))
    fwd = side.cross(Vector((0, 0, 1)))
    yaw = math.atan2(fwd.y, fwd.x)
    rot = Matrix.Rotation(-math.pi / 2 - yaw, 4, "Z")
    dg = bpy.context.evaluated_depsgraph_get()
    m = p.evaluated_get(dg).to_mesh()
    pts = np.array([(rot @ p.matrix_world @ v.co)[:] for v in m.vertices])
    hip = rot @ arm.matrix_world @ next(b for b in arm.pose.bones if "Hip" in b.name).head
    move = Matrix.Translation(Vector((-hip.x, -hip.y, -pts[:, 2].min()))) @ rot
    mw_arm, mw_mesh = arm.matrix_world.copy(), p.matrix_world.copy()
    arm.parent = None
    arm.matrix_world = move @ mw_arm
    p.parent = arm
    p.matrix_world = move @ mw_mesh
    p.parent_type = "OBJECT"
    for o in bpy.data.objects:
        o.select_set(o in (arm, p))
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(filepath=f"{out_dir}/{name}.glb", export_format="GLB", use_selection=True, export_animations=True, export_skins=True,
                              export_image_format="WEBP", export_image_quality=85, export_animation_mode="ACTIONS")
    print("OK", name, "giro", round(math.degrees(-math.pi / 2 - yaw)), "altura", round(float(pts[:, 2].max() - pts[:, 2].min()), 2))
