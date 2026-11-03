"""Fazenda (farm_01_fields), refeita e organizada em seis áreas cercadas e ligadas por portões, com caminhos de terra:
  Entrada (estrada leste-oeste, com o Viajante do Tempo, o portal de volta e as saídas para a Floresta Escura, a oeste, e para a Mina, a leste),
  Sede (casa da fazenda, poço, lenha, galinheiro, chiqueiro e o lugar da Casa de Equipamentos), Pasto (curral das ovelhas e dos cavalos),
  Horta (canteiros de verduras e melões), Pomar (macieiras, cestos, caixotes e mesa de piquenique) e Moinho (a serraria sobre o riacho, duas pontes, toras, lagoa e a entrada do Bunker).
Peças do jogo: casa e serraria, poço, carrinho de mão, cochos, cercas, macieiras (Oak_Tree), caixotes de maçã, barris, lenha, lampiões, placas, pontes, terra batida e lama, capim, ervas e flores.
Mantém os ids dos objetos de saída (return_portal, to_bunker, mine_gate, dark_forest_gate, creek); a Casa de Equipamentos (build_city_quests.py) e o Viajante (set_map_order.py) entram depois.
Sorteio com semente fixa; idempotente; chamado em tools/assets/build_maps.py (antes de add_fish.py/add_decor_animals.py, que põem peixes e animais, e do build_city_quests.py).
uso: python3 tools/assets/build_farm.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
old = arenas["farm_01_fields"]
rng = random.Random("farm-v2")
DOOR = 6.0

ROOMS = [("road", 0, 0, 64, 14), ("farmstead", -16, -21, 32, 28), ("pasture", 16, -21, 32, 28), ("gardens", -16, -49, 32, 28), ("orchard", 16, -49, 32, 28), ("mill", 48, -35, 32, 56)]
LINKS = [("road", "farmstead", "north"), ("road", "pasture", "north"), ("farmstead", "pasture", "east"), ("farmstead", "gardens", "north"), ("pasture", "orchard", "north"),
         ("gardens", "orchard", "east"), ("pasture", "mill", "east"), ("orchard", "mill", "east")]
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
by_id = {r[0]: r for r in ROOMS}
doors = {r[0]: [] for r in ROOMS}
door_points = []
for a, b, side in LINKS:
    _, ax, az, aw, ah = by_id[a]
    _, bx, bz, bw, bh = by_id[b]
    if side in ("north", "south"):
        lo, hi = max(ax - aw / 2, bx - bw / 2), min(ax + aw / 2, bx + bw / 2)
        edge = az - ah / 2 if side == "north" else az + ah / 2
        assert abs(edge - (bz + bh / 2 if side == "north" else bz - bh / 2)) < 1e-6, (a, b)
        mid = round((lo + hi) / 2 * 2) / 2
        offs = (mid - ax, mid - bx)
        door_points.append((mid, edge))
    else:
        lo, hi = max(az - ah / 2, bz - bh / 2), min(az + ah / 2, bz + bh / 2)
        edge = ax - aw / 2 if side == "west" else ax + aw / 2
        assert abs(edge - (bx + bw / 2 if side == "west" else bx - bw / 2)) < 1e-6, (a, b)
        mid = round((lo + hi) / 2 * 2) / 2
        offs = (mid - az, mid - bz)
        door_points.append((edge, mid))
    assert hi - lo >= DOOR + 2
    for rid, s, off in ((a, side, offs[0]), (b, OPP[side], offs[1])):
        doors[rid].append(s if abs(off) < 1e-6 else "%s:%g" % (s, off))
rooms = []
for rid, cx, cz, w, h in ROOMS:
    r = {"id": rid, "center": [cx, cz], "size": [w, h], "doors": doors[rid], "wall_height": 0.8}
    if rid == "road":
        r["torch"] = True
    rooms.append(r)
for i, (_, ax, az, aw, ah) in enumerate(ROOMS):
    for _, bx, bz, bw, bh in ROOMS[i + 1:]:
        assert abs(ax - bx) >= (aw + bw) / 2 - 1e-6 or abs(az - bz) >= (ah + bh) / 2 - 1e-6, "salas sobrepostas"


def room_at(x, z, pad=0.0):
    for r in rooms:
        if abs(x - r["center"][0]) < r["size"][0] / 2 + pad and abs(z - r["center"][1]) < r["size"][1] / 2 + pad:
            return r
    return None


CREEK_X, CREEK_W, BRIDGES = 48.0, 3.6, (-16.0, -50.0)
SHED = (-24.0, -14.0)                      # onde o build_city_quests.py põe a Casa de Equipamentos
FARMHOUSE = (-9.0, -17.0)
SAWMILL = (CREEK_X + 2.1, -28.0)
GATE_W, GATE_E, GATE_BUNKER = (-29.5, -2.0), (29.5, -2.0), (56.0, -58.5)
SHEEP_PEN, HORSE_PADDOCK = (3, -32, 16, -18), (19, -32, 30, -18)
PIG_PEN, CHICKEN_YARD = (-30, -33, -21, -26), (-13, -33, -4, -27)
GARDEN = (-30, -61, -3, -38)
interest = [list(p) for p in door_points] + [[0, 3], [-6, 3], [7, 1], list(GATE_W), list(GATE_E), list(GATE_BUNKER), [SHED[0], SHED[1] + 3.2], list(FARMHOUSE)]
decor, taken, crowd = [], [], []


def near_interest(x, z, rad):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


def near_taken(x, z, rad):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def keepout(x, z, r):
    taken.append((x, z, r))


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=None, r=0.8, free=1.6, force=False, wall=1.2):
    if room_at(x, z, -wall) is None:
        return False
    if not force and (near_interest(x, z, free) or near_taken(x, z, r)):
        return False
    d = {"piece": piece, "position": [round(x, 2), round(z, 2)], "rotation": int(rot if rot is not None else rng.randrange(0, 360, 15))}
    if y is not None:
        d["y"] = y
    if scale != 1.0:
        d["scale"] = round(scale, 2)
    if solid:
        d["solid"] = [round(solid[0], 2), round(solid[1], 2)]
    decor.append(d)
    taken.append((x, z, r))
    return True


def scatter_rect(rect, pieces, n, scale=(1.0, 1.0), solid=None, r=0.8, tries=40, **kw):
    x0, z0, x1, z1 = rect
    done = 0
    for _ in range(n):
        for _t in range(tries):
            x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
            s = rng.uniform(*scale)
            if put(rng.choice(pieces) if isinstance(pieces, list) else pieces, x, z, scale=s, solid=[solid[0] * s, solid[1] * s] if solid else None, r=r * s, **kw):
                done += 1
                break
    return done


def room_rect(rid, m=1.5):
    cx, cz, w, h = by_id[rid][1:]
    return (cx - w / 2 + m, cz - h / 2 + m, cx + w / 2 - m, cz + h / 2 - m)


def fence_rect(x0, z0, x1, z1, gaps=(), piece="Prop_WoodenFence_Single", step=2.0):
    """Cerca retangular (2,06 m) com vãos de portão: gaps = (lado, posição ao longo do lado, largura), lados n/s/w/e."""
    sides = {"n": ((x0, z0), (x1, z0)), "s": ((x0, z1), (x1, z1)), "w": ((x0, z0), (x0, z1)), "e": ((x1, z0), (x1, z1))}
    for side, ((ax, az), (bx, bz)) in sides.items():
        length = math.hypot(bx - ax, bz - az)
        dx, dz = (bx - ax) / length, (bz - az) / length
        n = max(1, round(length / step))
        for i in range(n):
            t = (i + 0.5) * length / n
            px, pz = ax + dx * t, az + dz * t
            along = px if side in "ns" else pz
            if any(g[0] == side and abs(along - g[1]) < g[2] / 2 + 0.6 for g in gaps):
                continue
            horiz = side in "ns"
            decor.append({"piece": piece, "position": [round(px, 1), round(pz, 1)], "rotation": 0 if horiz else 90, "scale": round(length / n / 2.06 * 1.02, 2),
                          "solid": [round(length / n, 2), 0.3] if horiz else [0.3, round(length / n, 2)]})
            taken.append((px, pz, 0.9))


# ---------------------------------------------------------------- terra batida e lama (ladrilhos de 2 m), caminhos entre os pontos da fazenda
dirt_n = [0]
dirt_spots = []


def dirt_tile(piece, x, z, scale=1.0, free=False):
    dirt_n[0] += 1
    decor.append({"piece": piece, "position": [round(x, 2), round(z, 2)], "y": round(0.02 + (dirt_n[0] % 6) * 0.003, 3),
                  "rotation": rng.randrange(0, 360, 5) if free else rng.choice([0, 90, 180, 270]), "scale": round(scale, 2)})
    dirt_spots.append((x, z, 1.4))


def dirt_path(points, step=1.6, piece="Ground_FarmDirt"):
    for (ax, az), (bx, bz) in zip(points, points[1:]):
        length = math.hypot(bx - ax, bz - az)
        for i in range(max(1, int(length / step) + 1)):
            t = min(i * step / length, 1.0)
            cx, cz = ax + (bx - ax) * t, az + (bz - az) * t
            dirt_tile(piece, cx + rng.uniform(-0.25, 0.25), cz + rng.uniform(-0.25, 0.25), rng.uniform(0.95, 1.15), free=True)
            if rng.random() < 0.8:
                side = rng.choice([-1, 1]) * rng.uniform(1.0, 1.5)
                dirt_tile(piece, cx - (bz - az) / length * side, cz + (bx - ax) / length * side, rng.uniform(0.4, 0.65), free=True)


def dirt_fill(rect, piece="Ground_FarmDirt", chance=1.0):
    x0, z0, x1, z1 = rect
    for ix in range(int((x1 - x0) // 2)):
        for iz in range(int((z1 - z0) // 2)):
            if rng.random() < chance:
                dirt_tile(piece, x0 + 1 + ix * 2, z0 + 1 + iz * 2, 1.0)


for line in (
        [(-28, -1), (-14, -1), (0, -1), (14, -1), (28, -1)],                       # estrada principal, de oeste (Floresta Escura) a leste (Mina)
        [(0, 3), (0, -1)],                                                          # da partida à estrada
        [(-16, -1), (-16, -9), (-14, -13), (-9, -14.5)],                            # portão da sede e porta da casa
        [(-24, -11.5), (-18, -13)],                                                 # Casa de Equipamentos
        [(16, -1), (16, -9), (13, -14), (10, -19)],                                 # portão do pasto
        [(-16, -14), (-16, -24), (-16, -35), (-16, -40)],                           # sede -> horta
        [(-3, -21), (3, -21)],                                                      # sede <-> pasto
        [(16, -24), (16, -35), (16, -40)],                                          # pasto -> pomar
        [(31, -16), (40, -16), (48, -16), (56, -16)],                               # pasto -> moinho (ponte sul)
        [(31, -49), (40, -50), (48, -50), (54, -53), (56, -58)],                    # pomar -> moinho (ponte norte) -> Bunker
        [(40, -16), (44, -24), (45, -30)],                                          # até a serraria
        [(-4, -49), (4, -49), (16, -49)]):                                          # horta <-> pomar
    dirt_path(line)
dirt_fill((SHED[0] - 3.5, SHED[1] + 2.5, SHED[0] + 3.5, SHED[1] + 6.5), chance=0.8)  # pátio da Casa de Equipamentos
dirt_fill((FARMHOUSE[0] - 4, FARMHOUSE[1] + 3, FARMHOUSE[0] + 4, FARMHOUSE[1] + 7), chance=0.8)
dirt_fill((PIG_PEN[0] + 0.4, PIG_PEN[1] + 0.4, PIG_PEN[2] - 0.4, PIG_PEN[3] - 0.4), "Ground_FarmMud")
dirt_fill((SHEEP_PEN[0] + 0.4, SHEEP_PEN[1] + 0.4, SHEEP_PEN[2] - 0.4, SHEEP_PEN[3] - 0.4), chance=0.25)
dirt_fill((HORSE_PADDOCK[0] + 0.4, HORSE_PADDOCK[1] + 0.4, HORSE_PADDOCK[2] - 0.4, HORSE_PADDOCK[3] - 0.4), chance=0.4)
dirt_fill((GARDEN[0] + 1, GARDEN[1] + 1, GARDEN[2] - 1, GARDEN[3] - 1), chance=0.9)  # canteiros: terra lavrada
dirt_fill((SAWMILL[0] - 4, SAWMILL[1] - 6, SAWMILL[0] + 12, SAWMILL[1] + 6), chance=0.75)  # pátio da serraria
dirt_fill((GATE_W[0] - 2, GATE_W[1] - 3, GATE_W[0] + 5, GATE_W[1] + 3), chance=0.6)
dirt_fill((GATE_E[0] - 5, GATE_E[1] - 3, GATE_E[0] + 2, GATE_E[1] + 3), chance=0.6)
dirt_fill((GATE_BUNKER[0] - 4, GATE_BUNKER[1] - 1, GATE_BUNKER[0] + 4, GATE_BUNKER[1] + 4), chance=0.8)

# ---------------------------------------------------------------- construções, cercados e portões
decor.append({"piece": "Pr_Farmhouse", "position": list(FARMHOUSE), "solid": [7.0, 4.9]})
keepout(FARMHOUSE[0], FARMHOUSE[1], 5.0)
decor.append({"piece": "Pr_Sawmill", "position": list(SAWMILL), "rotation": 270, "solid": [8.0, 6.5]})
keepout(SAWMILL[0], SAWMILL[1], 6.0)
for br in BRIDGES:
    decor.append({"piece": "Pr_Bridge", "position": [CREEK_X, br]})
    decor.append({"collider": [5.0, 0.2], "position": [CREEK_X, br - 0.92]})
    decor.append({"collider": [5.0, 0.2], "position": [CREEK_X, br + 0.92]})
    keepout(CREEK_X, br, 4.0)
keepout(SHED[0], SHED[1], 6.5)
fence_rect(*SHEEP_PEN, gaps=[("s", 9.5, 3.4)])
fence_rect(*HORSE_PADDOCK, gaps=[("s", 24.5, 3.4)])
fence_rect(*PIG_PEN, gaps=[("s", -25.5, 2.6)])
fence_rect(*CHICKEN_YARD, gaps=[("s", -8.5, 2.6)])
fence_rect(*GARDEN, gaps=[("s", -16, 3.0), ("e", -49, 3.0)])
for rect in (SHEEP_PEN, HORSE_PADDOCK, PIG_PEN, CHICKEN_YARD, GARDEN):
    x0, z0, x1, z1 = rect
    taken.append(((x0 + x1) / 2, (z0 + z1) / 2, 2.0))
# cochos, bebedouros e o galinheiro
for x, z, rot in ((9.5, -27, 0), (24.5, -26, 0), (-25.5, -29.5, 90)):
    put("Pr_Trough", x, z, rot=rot, solid=[1.64, 0.68], r=1.3, free=0.5, force=True)
for dx, dz in ((-1.2, 0.0), (1.4, 0.4), (0.2, 1.5)):
    put("Pr_Basket", -8.5 + dx, -30 + dz, r=0.5, free=0.4, force=True)
put("Tv_Sack", -5.5, -28.5, r=0.6, free=0.4, force=True)
put("Barrel", -11.5, -28.0, solid=[0.9, 0.9], r=0.8, free=0.4, force=True)
# poço, lenha, carrinhos e equipamentos da sede
put("Well_Covered", -4.5, -22, solid=[1.6, 1.6], r=2.0, free=0.5, force=True)
put("Bucket_Wooden_1", -3.0, -21.0, r=0.4, free=0.3, force=True)
put("Wheelbarrow", -20.5, -22.0, rot=40, solid=[1.6, 0.8], r=1.2, free=0.4, force=True)
for x, z, rot in ((-30.0, -18.0, 90), (-29.5, -20.5, 95), (-29.3, -23.2, 85)):
    put("Vl_Logs", x, z, rot=rot, solid=[2.2, 0.8], r=1.0, free=0.3, force=True)
put("Vl_ChoppingBlock", -30.4, -14.2, solid=[0.9, 0.9], r=0.8, free=0.3, force=True)
put("Tv_Firewood", -27.5, -20.0, rot=90, solid=[1.4, 0.8], r=1.0, free=0.3, force=True)
put("Pr_CartLarge", -22.5, -23.5, rot=20, solid=[3.2, 2.6], r=2.4, free=0.4, force=True)
put("Barrel_Apples", -13.5, -11.5, solid=[0.9, 0.9], r=0.8, free=0.3, force=True)
put("Crate_Wooden", -14.8, -11.2, rot=15, solid=[0.9, 0.9], r=0.8, free=0.3, force=True)
put("Vl_Outhouse", -29.5, -9.2, rot=90, solid=[1.4, 1.5], r=1.4, free=0.3, force=True)
# estrada de entrada: placas, lampiões com luz, barricadas de toras, carrinho e feno (sacas)
decor.append({"piece": "Pr_Barricade", "position": [-8.5, -4.5], "rotation": 15, "solid": [2.0, 1.2]})
decor.append({"piece": "Pr_Barricade", "position": [8.5, -4.5], "rotation": 345, "solid": [2.0, 1.2]})
for x in (-24, -12, 12, 24):
    for z in (2.2, -4.4):
        if put("Pr_LampPost", x, z, rot=0, solid=[0.6, 0.6], r=0.8, free=0.5, force=True):
            decor.append({"light": [1.0, 0.75, 0.4], "position": [x, z], "y": 2.6, "range": 9.0, "energy": 1.0})
for x, z, text in ((-2.2, -2.6, 0), (-27, -4.2, 90), (27, -4.2, 270), (53.5, -56.5, 0), (16.0, -6.4, 0), (-16.0, -6.4, 0)):
    put("Signpost_Medieval", x, z, rot=text, r=0.8, free=0.3, force=True)
put("Pr_CartSmall", 5.5, -2.8, rot=100, solid=[1.2, 2.4], r=1.6, free=0.3, force=True)
for x, z in ((-19.5, 3.4), (19.5, 3.4), (-6.0, 5.6), (11.5, 5.6)):
    put("Tv_Sack", x, z, r=0.6, free=0.3, force=True)
    put("Barrel", x + 0.9, z + 0.3, solid=[0.9, 0.9], r=0.8, free=0.3, force=True)
# a entrada da Floresta Escura (oeste): árvores secas, bambus e uma placa; a da Mina (leste): rochas, trilho, carroça e lanterna; a do Bunker (Moinho, norte): batente de pedra
gx, gz = GATE_W
for dz in (-3.5, 3.5):
    put("Dead_Tree", gx - 1.5, gz + dz, scale=0.7, solid=[0.9, 0.9], r=1.6, free=0.3, force=True, wall=-5)
decor.append({"light": [0.4, 0.6, 0.9], "position": [gx, gz], "y": 2.0, "range": 8.0, "energy": 1.2})
gx, gz = GATE_E
for dz, piece in ((-3.4, "RockP_6"), (3.4, "RockP_1")):
    put(piece, gx + 1.0, gz + dz, scale=2.2, solid=[1.8, 1.8], r=1.8, free=0.3, force=True, wall=-5)
put("Cart_Wood", gx - 3.0, gz - 3.8, rot=70, solid=[2.2, 1.2], r=1.6, free=0.3, force=True, y=0.05)
decor.append({"light": [0.9, 0.7, 0.4], "position": [gx, gz], "y": 2.0, "range": 8.0, "energy": 1.2})
bx, bz = GATE_BUNKER
decor += [{"piece": "Bk_Pillar", "position": [bx - 1.1, bz], "solid": [0.9, 0.9]}, {"piece": "Bk_Pillar", "position": [bx + 1.1, bz], "solid": [0.9, 0.9]},
          {"piece": "Bk_Lintel", "position": [bx, bz], "rotation": 90}, {"piece": "Bk_Wall", "position": [bx - 3.4, bz], "rotation": 90, "solid": [2.0, 0.5]},
          {"piece": "Bk_Wall", "position": [bx + 3.4, bz], "rotation": 90, "solid": [2.0, 0.5]}]
decor.append({"light": [1.0, 0.65, 0.3], "position": [bx, bz + 1.2], "y": 2.0, "range": 8.0, "energy": 1.2})

# ---------------------------------------------------------------- horta: canteiros de verduras, melões e flores
x0, z0, x1, z1 = GARDEN
for k, bz_ in enumerate((-41, -46, -51, -56)):
    for gx_ in range(int(x0) + 3, int(x1) - 2, 1):
        kind = ("Pl_Hemp", "Pl_Shrub2", "Pl_Weed3", "Pl_Hemp")[k]
        decor.append({"piece": kind, "position": [round(gx_ + rng.uniform(-0.15, 0.15), 2), round(bz_ + rng.uniform(-0.1, 0.1), 2)], "rotation": rng.randrange(0, 360, 15), "scale": round(rng.uniform(0.7, 1.0), 2)})
for _ in range(14):
    decor.append({"piece": rng.choice(("Food_Watermelon", "Food_Watermelon_Half")), "position": [round(rng.uniform(x0 + 3, x1 - 3), 1), round(rng.choice((-43.5, -48.5, -53.5, -58.5)) + rng.uniform(-0.3, 0.3), 1)],
                  "rotation": rng.randrange(0, 360, 15), "scale": round(rng.uniform(1.6, 2.2), 2)})
for x in range(int(x0) + 3, int(x1) - 2, 4):
    decor.append({"piece": "Pl_Flower", "position": [x + rng.uniform(-0.5, 0.5), -39.2], "rotation": rng.randrange(0, 360, 15), "scale": round(rng.uniform(0.4, 0.6), 2)})
put("Well_Covered", -5.5, -59.0, solid=[1.6, 1.6], r=2.0, free=0.3, force=True)
put("Wheelbarrow", -26, -59, rot=80, solid=[1.6, 0.8], r=1.2, free=0.3, force=True)
for dx in (0, 1.1, 2.2):
    put("Bucket_Wooden_1", -8 + dx, -59.3, r=0.4, free=0.3, force=True)

# ---------------------------------------------------------------- pomar: macieiras em fileiras, maçãs caídas, caixotes, cestos, mesa de piquenique
for ix, x in enumerate(range(5, 31, 7)):
    for iz, z in enumerate(range(-43, -61, -6)):
        tx, tz = x + rng.uniform(-0.8, 0.8) + (3.0 if iz % 2 else 0.0), z + rng.uniform(-0.6, 0.6)
        if 4 < tx < 29 and put("Oak_Tree", tx, tz, scale=round(rng.uniform(0.55, 0.75), 2), solid=[1.0, 1.0], r=2.0, free=2.0):
            for _ in range(4):
                a = rng.uniform(0, math.tau)
                put("Food_Apple", tx + math.cos(a) * rng.uniform(1.0, 2.2), tz + math.sin(a) * rng.uniform(1.0, 2.2), scale=1.5, r=0.2, free=0.5)
for x, z in ((3.5, -39.5), (29.0, -57.5), (3.2, -58.0), (29.5, -40.0)):
    put("FarmCrate_Apple", x, z, rot=rng.randrange(0, 360, 15), solid=[1.0, 1.0], r=1.0, free=0.5)
    put("Barrel_Apples", x + 1.2, z + 0.4, solid=[0.9, 0.9], r=0.8, free=0.5)
    put("Pr_Basket", x - 1.0, z + 0.9, r=0.5, free=0.4)
put("Table_Large", 17.5, -41.0, rot=0, solid=[2.2, 1.2], r=2.0, free=0.5, force=True)
put("Bench", 17.5, -42.6, rot=0, solid=[1.6, 0.6], r=1.0, free=0.5, force=True)
put("Bench", 17.5, -39.4, rot=180, solid=[1.6, 0.6], r=1.0, free=0.5, force=True)
put("Vl_Ladder", 10.0, -45.5, rot=70, r=0.8, free=0.5)

# ---------------------------------------------------------------- moinho: toras, lenha, bancos junto ao riacho, uma lagoa e pedras nas margens
for z, rot in ((-36.0, 80), (-38.0, 100), (-40.0, 90)):
    put("Vl_Logs", 54.0, z, rot=rot, solid=[2.2, 0.8], r=1.0, free=0.3, force=True)
put("Tv_Firewood", 58.5, -26, rot=90, solid=[1.4, 0.8], r=1.0, free=0.3, force=True)
put("Vl_ChoppingBlock", 57.0, -23.5, solid=[0.9, 0.9], r=0.8, free=0.3, force=True)
put("Pr_CartSmall", 57.0, -30.0, rot=300, solid=[2.0, 1.8], r=1.8, free=0.3, force=True)
put("Bench", 45.0, -8.8, rot=0, solid=[1.6, 0.6], r=1.0, free=0.3, force=True)
for z in range(-62, -7, 4):
    if any(abs(z - br) < 3.0 for br in BRIDGES):
        continue
    for side in (-1, 1):
        decor.append({"piece": rng.choice(["RockP_1", "RockP_2", "RockP_3", "RockP_6"]), "position": [round(CREEK_X + side * (CREEK_W / 2 + rng.uniform(0.1, 0.6)), 1), z + round(rng.uniform(-1.2, 1.2), 1)],
                      "rotation": rng.randrange(0, 360, 15), "scale": round(rng.uniform(0.6, 1.1), 2)})
        decor.append({"piece": rng.choice(["Pl_Grass1", "Pl_Grass2", "Pl_Grass3", "Pl_Weed2"]), "position": [round(CREEK_X + side * (CREEK_W / 2 + rng.uniform(0.7, 1.6)), 1), z + round(rng.uniform(-1.5, 1.5), 1)],
                      "rotation": rng.randrange(0, 360, 15), "scale": round(rng.uniform(1.0, 1.8), 2)})
for z in range(-62, -7, 6):
    keepout(CREEK_X, z, 3.0)

# ---------------------------------------------------------------- árvores de sombra, arbustos e capim por tudo (fora dos cercados, caminhos e construções)
avoid = dirt_spots + taken
def free_spot(x, z, rad):
    return not any(math.hypot(x - ax, z - az) < ar + rad for ax, az, ar in avoid) and not near_interest(x, z, 2.5)


for rid, trees in (("road", 6), ("farmstead", 5), ("pasture", 5), ("gardens", 4), ("orchard", 0), ("mill", 9)):
    cx, cz, w, h = by_id[rid][1:]
    for _ in range(trees):
        for _t in range(60):
            x, z = cx + rng.uniform(-w / 2 + 2.5, w / 2 - 2.5), cz + rng.uniform(-h / 2 + 2.5, h / 2 - 2.5)
            if free_spot(x, z, 2.5):
                s = round(rng.uniform(0.7, 1.0), 2)
                decor.append({"piece": "Oak_Tree", "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15), "scale": s, "solid": [1.2, 1.2]})
                taken.append((x, z, 2.6))
                avoid.append((x, z, 2.6))
                break
for rid in by_id:
    cx, cz, w, h = by_id[rid][1:]
    area = w * h
    for pieces, per, sc in ((["Pl_Grass1", "Pl_Grass2", "Pl_Grass3"], 5.0, (0.7, 2.0)), (["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"], 24.0, (0.8, 1.5)), (["Pl_Flower"], 40.0, (0.35, 0.6)),
                            (["Pl_Bush", "Pl_Shrub1", "Pl_Shrub3"], 90.0, (0.8, 1.3)), (["RockP_3", "RockP_6", "RockP_1"], 160.0, (0.5, 1.0))):
        n = int(area / per)
        done = 0
        for _ in range(n * 4):
            if done >= n:
                break
            x, z = cx + rng.uniform(-w / 2 + 1.0, w / 2 - 1.0), cz + rng.uniform(-h / 2 + 1.0, h / 2 - 1.0)
            if not free_spot(x, z, 0.4):
                continue
            decor.append({"piece": rng.choice(pieces), "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15), "scale": round(rng.uniform(*sc), 2)})
            done += 1

# ---------------------------------------------------------------- gente e bichos
def walker(role, x, z, dx, dz, speed, **extra):
    d = {"role": role, "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15), "pose": "idle", "path": [round(x + dx, 1), round(z + dz, 1)], "speed": speed}
    d.update(extra)
    crowd.append(d)


for (x, z), (tx, tz), tool, speed in (
        ((-26, -44), (-8, -44), "Tool_Hoe", 0.7), ((-26, -50), (-8, -50), "Tool_Shovel", 0.7), ((-26, -56), (-8, -56), "Tool_Hoe", 0.8), ((-20, -10), (-12, -10), "Tool_Scythe", 0.9),
        ((6, -10), (24, -10), "Tool_Pitchfork", 0.9), ((6, -52), (26, -52), "Tool_Sickle", 0.8), ((52, -20), (52, -40), "Tool_Scythe", 0.9), ((30, -3), (14, -3), "Tool_Hoe", 0.9)):
    crowd.append({"role": "farmer", "position": [x, z], "rotation": 0, "pose": "idle", "weapon": tool, "path": [tx, tz], "speed": speed})
for _ in range(9):
    x, z = rng.uniform(SHEEP_PEN[0] + 1.5, SHEEP_PEN[2] - 1.5), rng.uniform(SHEEP_PEN[1] + 1.5, SHEEP_PEN[3] - 1.5)
    walker("sheep", x, z, min(max(x + rng.uniform(-2.5, 2.5), SHEEP_PEN[0] + 1.2), SHEEP_PEN[2] - 1.2) - x, min(max(z + rng.uniform(-2, 2), SHEEP_PEN[1] + 1.2), SHEEP_PEN[3] - 1.2) - z, 0.5)
for role, box, count, speed in (("pig", PIG_PEN, 5, 0.5), ("farm_horse", HORSE_PADDOCK, 3, 0.7), ("chicken", CHICKEN_YARD, 6, 0.5)):
    for _ in range(count):
        x, z = rng.uniform(box[0] + 1.5, box[2] - 1.5), rng.uniform(box[1] + 1.5, box[3] - 1.5)
        walker(role, x, z, min(max(x + rng.uniform(-3, 3), box[0] + 1.2), box[2] - 1.2) - x, min(max(z + rng.uniform(-3, 3), box[1] + 1.2), box[3] - 1.2) - z, speed)
for x, z in ((-18, -4), (6, -6), (24, -6), (-12, -24), (20, -12), (-4, -45), (36, -14), (40, -60)):
    walker("chicken", x, z, rng.uniform(-3.5, 3.5), rng.uniform(-3, 3), 0.6)
for x, z in ((-2, -4), (24, -24), (-20, -14), (38, -8)):
    walker("rooster", x, z, rng.uniform(-6, 6), rng.uniform(-5, 5), 0.8)
for x, z in ((-24, -26), (10, -14), (4, -4), (-6, -60), (36, -12), (40, -50), (58, -14), (-22, -6)):
    walker("rabbit", x, z, rng.uniform(-4, 4), rng.uniform(-3.5, 3.5), 0.9)
baskets = []
for pos in ((-16.6, -8.3), (-6.4, -7.2), (-12.0, -25.0), (21.0, -30.0), (7.6, -12.0), (-27.5, -42.0), (-8.0, -45.0), (22.0, -52.0), (10.0, -57.0), (58.0, -22.0), (41.0, -12.0), (52.0, -46.0)):
    if room_at(pos[0], pos[1], -1.0) and not near_taken(pos[0], pos[1], 0.6):
        baskets.append({"id": "bk%d" % (len(baskets) + 1), "monster": "basket", "position": [pos[0], pos[1]], "table": "breakable_potion"})
keep_ids = {"return_portal", "creek"}
props = [{**p} for p in old["props"] if p["id"] in keep_ids and p["id"] != "creek"]
props.append({"id": "creek", "kind": "water", "position": [CREEK_X, -35.0], "size": [CREEK_W, 54.0], "color": [0.14, 0.34, 0.42], "flow": [0.0, 0.09]})
props.append({"id": "to_bunker", "kind": "exit", "name_key": "PROP_TO_BUNKER", "position": [bx, bz + 1.0], "to": "bunker_01_entrance", "entry": "start", "group": True})
props.append({"id": "mine_gate", "kind": "exit", "name_key": "PROP_TO_MINE", "position": list(GATE_E), "to": "mine_01_crystal_vein", "entry": "start"})
props.append({"id": "dark_forest_gate", "kind": "exit", "name_key": "PROP_TO_DARK_FOREST", "position": list(GATE_W), "to": "dark_forest_01_woods", "entry": "start"})
for p in props:
    if p["id"] == "return_portal":
        p["position"] = [-6, 3]
style = dict(old["style"])
style.update({"_comment": "Fazenda: chão de capim (Ground_FarmGrass, texturas contínuas de Lattice, CC0), cerca baixa de madeira nas bordas e em volta de cada área; o vazio em volta vira capim.", "fill_grass": True})
arenas["farm_01_fields"] = {
    "_comment": "Fazenda, organizada em áreas cercadas e ligadas por portões: Entrada (estrada, Viajante do Tempo, saídas para a Floresta Escura e a Mina), Sede (casa, poço, galinheiro, chiqueiro e a Casa de Equipamentos), Pasto "
                "(ovelhas e cavalos), Horta (canteiros e melões), Pomar (macieiras) e Moinho (serraria sobre o riacho, pontes, lagoa e a entrada do Bunker). Terra batida e lama (build_farm_ground.py), cercas, "
                "casa e serraria (CC0), carroças, ferramentas e animais. Gerado por tools/assets/build_farm.py.",
    "name_key": "ARENA_FARM", "town": True, "outdoor": True, "player_class": "mage", "map_id": "map_farm", "area_level": 1, "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": rooms, "encounters": [], "hazards": [],
    "entries": {"start": [0, 3], "farm": [0, 3], "bunker": [bx, bz + 3.0], "dark_forest": [GATE_W[0] + 3.0, GATE_W[1]], "mine": [GATE_E[0] - 3.0, GATE_E[1]]},
    "props": props, "quest_spots": [], "breakables": baskets, "style": style, "decor": decor, "crowd": crowd, "passive": True}
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK fazenda: %d salas, %d m2, %d peças, %d bichos e gente, %d cestos" % (len(rooms), sum(r[3] * r[4] for r in ROOMS), len(decor), len(crowd), len(baskets)))
