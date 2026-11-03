"""Mapa do Deserto: o Cânion (desert_01_canyon), ligado à Capital (Canyon Terrain Asset, loafbrr / Ian87, CC0: peças de
assets/models/maps/desert/ feitas por tools/assets/build_canyon_pieces.py). Mapa grande de salas abertas, com a MESMA estrutura da Floresta
(forest_01_path) mas outro caminho: o acampamento fica ao sul e a rota sobe para o norte em laço (estrada -> ruínas de carroças -> passagem -> poço
de areia movediça -> dunas), com ramais sem saída. Duas áreas de mini-chefe (o NPC do Oásis desperta a Rainha Escorpião; o templo das Ruínas do Sol
desperta o Lamassu da Areia), o Sentinela do Portão (pede as duas chaves) e, atrás do portão, o Salão da Esfinge (chefe final, com a saída).
Sorteio com semente fixa: rodar de novo reproduz o mesmo mapa. Também põe os NPCs/missões/itens do Deserto (data/npcs.json, quests.json, valuables.json, monsters.json), os textos pt/en/es e os ícones.
Idempotente; chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/build_desert.py   (a partir da raiz do projeto)"""
import json, math, random, re
ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json")
arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
rng = random.Random("desert-canyon-v2")
DOOR = 6.0

# ---------------------------------------------------------------- salas (centro, tamanho); as portas saem dos "links" (salas encostadas)
ROOMS = [("camp", 0, 0, 44, 26), ("caravan", -36, 6, 28, 30), ("road", 0, -36, 36, 46), ("oasis", -34, -36, 32, 24), ("wrecks", 36, -30, 36, 30),
         ("pass", 46, -57, 12, 24), ("dunes", 0, -84, 44, 50), ("nest", -40, -84, 36, 32), ("quicksand", 40, -84, 36, 30), ("ruins", 76, -84, 36, 36),
         ("gate_lane", 0, -124, 12, 30), ("sphinx", 0, -167, 56, 56)]
LINKS = [("camp", "caravan", "west"), ("camp", "road", "north"), ("road", "oasis", "west"), ("road", "wrecks", "east"), ("wrecks", "pass", "north"),
         ("pass", "quicksand", "north"), ("road", "dunes", "north"), ("dunes", "nest", "west"), ("dunes", "quicksand", "east"), ("quicksand", "ruins", "east"),
         ("dunes", "gate_lane", "north"), ("gate_lane", "sphinx", "north")]
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
    assert hi - lo >= DOOR + 2, (a, b)
    for rid, s, off in ((a, side, offs[0]), (b, OPP[side], offs[1])):
        doors[rid].append(s if abs(off) < 1e-6 else "%s:%g" % (s, off))
rooms = []
for rid, cx, cz, w, h in ROOMS:
    r = {"id": rid, "center": [cx, cz], "size": [w, h], "doors": doors[rid], "wall_height": 0.8}
    if rid == "camp":
        r["torch"] = True
    rooms.append(r)
for i, (_, ax, az, aw, ah) in enumerate(ROOMS):  # nenhuma sala invade a outra
    for _, bx, bz, bw, bh in ROOMS[i + 1:]:
        assert abs(ax - bx) >= (aw + bw) / 2 - 1e-6 or abs(az - bz) >= (ah + bh) / 2 - 1e-6, "salas sobrepostas"


def room_at(x, z, pad=0.0):
    for r in rooms:
        if abs(x - r["center"][0]) < r["size"][0] / 2 + pad and abs(z - r["center"][1]) < r["size"][1] / 2 + pad:
            return r
    return None


# ---------------------------------------------------------------- objetos do mapa (também servem para deixar o cenário longe deles)
SUMMON_GUIDE = {"id": "d_queen", "position": [-43.0, -42.0], "spread": 3.0, "toast": "TOAST_OASIS_AWAKENS",
                "monsters": [{"monster": "queen_scorpion", "count": 1, "rank": "miniboss"}]}
SUMMON_TEMPLE = {"id": "d_lamassu", "position": [76.0, -75.0], "spread": 3.0, "toast": "TOAST_SUN_TEMPLE_AWAKENS",
                 "monsters": [{"monster": "sand_lamassu", "count": 1, "rank": "miniboss"}]}
props = [
    {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-8, 9], "to": "capital_01_aurenhold", "entry": "desert"},
    {"id": "victory_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [0, -191.5], "to": "capital_01_aurenhold", "entry": "desert", "after_victory": True, "group": True},
    {"id": "desert_nomad", "kind": "npc", "npc": "desert_nomad", "position": [8, -4], "rotation": 200},
    {"id": "desert_oasis_keeper", "kind": "npc", "npc": "desert_oasis_keeper", "position": [-26, -30], "rotation": 0, "summon": SUMMON_GUIDE, "needs_quest": "desert_scarab"},
    {"id": "oasis_pond", "kind": "water", "position": [-34, -37], "size": [10.0, 6.0], "round": True, "color": [0.12, 0.38, 0.45]},
    {"id": "oasis_pond_b", "kind": "water", "position": [-30.5, -35.5], "size": [5.0, 3.5], "round": True, "color": [0.12, 0.38, 0.45]},
    {"id": "desert_temple", "kind": "npc", "npc": "desert_temple", "kit": "Ruin_Temple1", "rotation": 0, "position": [76.0, -84.0], "summon": SUMMON_TEMPLE, "needs_quest": "desert_horn"},
    {"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": [0.0, -135.0], "rotation": 0, "scale": 3.0, "block": 12.0, "count": 2, "opened_by": "desert_gate"},
    {"id": "desert_sentinel", "kind": "npc", "npc": "desert_sentinel", "position": [0.0, -131.0], "rotation": 0},
    {"id": "desert_chest_1", "kind": "chest", "position": [-46, 14], "loot": "chest"}, {"id": "desert_chest_2", "kind": "chest", "position": [-46, -28], "loot": "chest"},
    {"id": "desert_chest_3", "kind": "chest", "position": [-55, -94], "loot": "chest"}, {"id": "desert_chest_4", "kind": "chest", "position": [88, -98], "loot": "chest"},
    {"id": "desert_chest_5", "kind": "chest", "position": [52, -40], "loot": "chest"}, {"id": "desert_chest_6", "kind": "chest", "position": [-22, -190], "loot": "chest"},
    {"id": "desert_chest_7", "kind": "chest", "position": [22, -190], "loot": "chest"}]
E = lambda eid, pos, *mons: (eid, pos, list(mons))
encounters = [
    E("d_road_scorp", [-8, -28], ("venom_scorpion", 3)), E("d_road_chitin", [8, -44], ("chitin_beast", 2)), E("d_road_stalker", [0, -53], ("stalker", 2)),
    E("d_caravan", [-36, 2], ("venom_scorpion", 3)), E("d_caravan_mimic", [-44, 16], ("chest_mimic", 1)),
    E("d_oasis", [-30, -44], ("venom_scorpion", 2), ("chitin_beast", 1)),
    E("d_wrecks_a", [30, -24], ("goblin", 4), ("stalker", 1)), E("d_wrecks_b", [28, -38], ("chitin_beast", 2)), E("d_wrecks_troll", [47, -36], ("troll", 1)),
    E("d_wrecks_mimic", [50, -22], ("chest_mimic", 1)),
    E("d_pass", [46, -57], ("stalker", 2)),
    E("d_dunes_a", [-10, -70], ("venom_scorpion", 3)), E("d_dunes_b", [10, -96], ("chitin_beast", 3)), E("d_dunes_c", [-8, -101], ("stalker", 2)),
    E("d_dunes_d", [12, -74], ("goblin", 4)),
    E("d_nest_a", [-40, -84], ("venom_scorpion", 4)), E("d_nest_b", [-48, -90], ("chitin_beast", 3)), E("d_nest_troll", [-34, -76], ("troll", 1)),
    E("d_nest_mimic", [-52, -94], ("chest_mimic", 1)),
    E("d_sand_a", [34, -90], ("venom_scorpion", 3)), E("d_sand_b", [46, -78], ("chitin_beast", 2)), E("d_sand_mimic", [54, -72], ("chest_mimic", 1)),
    E("d_ruins_a", [64, -94], ("stalker", 2)), E("d_ruins_b", [88, -76], ("chitin_beast", 2)), E("d_ruins_mimic", [90, -96], ("chest_mimic", 1)),
    E("d_sphinx_a", [-14, -152], ("chitin_beast", 2)), E("d_sphinx_b", [14, -152], ("chitin_beast", 2)),
    E("d_sphinx", [0, -180], ("sphinx", 1))]
interest = [p["position"] for p in props if p["kind"] != "water"] + [e[1] for e in encounters] + [SUMMON_GUIDE["position"], SUMMON_TEMPLE["position"], [0, 4]]
interest += [list(d) for d in door_points]


def near_interest(x, z, rad=3.5):
    return any(math.hypot(x - ix, z - iz) < rad for ix, iz in interest)


# ---------------------------------------------------------------- paredes de rocha e cenário
# Paredes: (largura aproximada, peças altas para norte/leste/oeste e baixas para o sul, que fica de frente para a câmera)
TALL = {"Rock_Formations_3": 13.5, "Rock_Formations_4": 6.7, "Rock_Formations_5": 16.9, "Rock_Formations_6": 3.8, "Rock_Formations_7": 10.4,
        "Rock_Formations_8": 9.0, "Rock_Formations_9": 8.0, "Rock_Formations_10": 8.5, "Rock_Formations_12": 7.0,
        "Rock_Platforms_5": 12.0, "Rock_Platforms_7": 21.0, "Rock_Platforms_9": 21.0, "Rock_Platforms_10": 18.0}
LOW = {"Rock_Boulders_1": 2.4, "Rock_Boulders_4": 4.0, "Rock_Boulders_5": 2.4, "Rock_Boulders_6": 1.9, "Rock_Platforms_1": 4.6, "Rock_Platforms_4": 5.2,
       "Rock_Platforms_6": 5.4, "Rock_Formations_1": 6.3, "Rock_Formations_2": 4.8}
decor = []
for idx, r in enumerate(rooms):
    cx, cz = r["center"]
    hw, hh = r["size"][0] / 2, r["size"][1] / 2
    for side in ("north", "south", "east", "west"):
        horizontal = side in ("north", "south")
        length = r["size"][0] if horizontal else r["size"][1]
        pool = LOW if side == "south" else TALL
        t = -length / 2 + 2.0
        while t < length / 2 - 1.0:
            name = rng.choice(list(pool))
            w = pool[name]
            mid = t + w / 2
            t += w * 0.9
            if mid + w / 2 > length / 2 + 2:
                break
            door_off = next((float(d.split(":")[1]) if ":" in d else 0.0 for d in r["doors"] if d.split(":")[0] == side), None)
            if door_off is not None and abs(mid - door_off) < DOOR / 2 + w / 2:
                continue  # vão da porta
            depth = 2.0 + w * 0.22
            if side == "north":
                x, z, rot = cx + mid, cz - hh - depth, 0
            elif side == "south":
                x, z, rot = cx + mid, cz + hh + depth, 180
            elif side == "east":
                x, z, rot = cx + hw + depth, cz + mid, 270
            else:
                x, z, rot = cx - hw - depth, cz + mid, 90
            other = room_at(x, z)
            if other is not None:  # encosta noutra sala: só a primeira da lista põe o divisor de rocha, sobre a linha da borda
                if rooms.index(other) < idx:
                    continue
                x, z = (cx + mid, cz - hh) if side == "north" else (cx + mid, cz + hh) if side == "south" else (cx + hw, cz + mid) if side == "east" else (cx - hw, cz + mid)
            decor.append({"piece": "Canyon_" + name, "position": [round(x, 1), round(z, 1)], "rotation": rot + rng.choice((0, 15, -15))})
# ---------------------------------------------------------------- decoração temática (assets do projeto que combinam com deserto: ossos, obeliscos, ruínas, carroças, acampamento)
taken = []  # (x, z, raio) das peças temáticas: o cenário aleatório fica longe delas


def near_taken(x, z, rad=0.0):
    return any(math.hypot(x - tx, z - tz) < tr + rad for tx, tz, tr in taken)


def put(piece, x, z, rot=None, scale=1.0, solid=None, y=None, r=1.0, free=2.2, force=False):
    """Põe uma peça se couber dentro de uma sala, longe dos objetos do mapa e das outras peças. Devolve se pôs."""
    if room_at(x, z, -1.2) is None:
        return False
    if not force and (near_interest(x, z, free) or near_taken(x, z, r)):
        return False
    d = {"piece": piece, "position": [round(x, 1), round(z, 1)], "rotation": int(rot if rot is not None else rng.randrange(0, 360, 15))}
    if scale != 1.0:
        d["scale"] = round(scale, 2)
    if solid:
        d["solid"] = [round(solid[0], 1), round(solid[1], 1)]
    if y is not None:
        d["y"] = y
    decor.append(d)
    taken.append((x, z, r))
    return True


def scatter(rid, pieces, n, scale=(1.0, 1.0), solid=None, margin=4.0, r=1.2, tries=40, **kw):
    cx, cz = by_id[rid][1], by_id[rid][2]
    w, h = by_id[rid][3], by_id[rid][4]
    done = 0
    for _ in range(n):
        for _t in range(tries):
            x, z = cx + rng.uniform(-w / 2 + margin, w / 2 - margin), cz + rng.uniform(-h / 2 + margin, h / 2 - margin)
            s = rng.uniform(*scale)
            if put(rng.choice(pieces) if isinstance(pieces, list) else pieces, x, z, scale=s, solid=[solid[0] * s, solid[1] * s] if solid else None, r=r * s, **kw):
                done += 1
                break
    return done


def around(piece, cx, cz, radius, n, start=0.0, scale=1.0, solid=None, face_center=False, r=0.8, **kw):
    for i in range(n):
        a = start + i * 2 * math.pi / n
        x, z = cx + radius * math.cos(a), cz + radius * math.sin(a)
        rot = math.degrees(-a) + 90 if face_center else None
        put(piece, x, z, rot=rot, scale=scale, solid=solid, r=r, **kw)


def fire_light(x, z, energy=1.5, rng_=10.0, y=1.2, color=(1.0, 0.55, 0.2)):
    decor.append({"light": list(color), "position": [round(x, 1), round(z, 1)], "y": y, "range": rng_, "energy": energy, "flicker": True})


def brazier(x, z, scale=1.6):
    if put("Tv_Fire", x, z, rot=0, scale=scale, solid=[0.9 * scale, 0.7 * scale], r=1.3, free=1.5):
        decor.append({"piece": "Fire_Flame", "position": [round(x, 1), round(z, 1)], "y": 0.12 * scale, "scale": round(scale * 0.9, 2), "flicker": True})
        fire_light(x, z, 1.7, 11.0)


def torch(x, z):
    if put("Tv_Torch", x, z, scale=1.5, r=0.5, free=1.5):
        fire_light(x, z, 0.8, 6.0, 1.7)


BONES = ["Dungeon_BonePile_%d" % i for i in range(1, 7)] + ["Dungeon_CrossBones", "Dungeon_Pelvis", "Dungeon_Arm", "Dungeon_Leg", "Dungeon_Bone", "Dungeon_Skull_1", "Dungeon_Skull_2"]
BIG_BONES = ["Dungeon_Ribcage", "Dungeon_Spine", "Dungeon_Pelvis"]
CARGO = ["Crate_Big", "Crate_Small", "Crate_Open", "Barrel", "Barrel_Oga_1", "Barrel_Oga_2", "Tv_Sack", "Tv_Sack_2", "Bag", "Pot_Large", "Pot_Small", "Pot_Large_Shards", "Vase_Big_Shards", "Vase_2", "Tv_Basket", "Pr_Basket"]
WRECKS = ["Pr_CartLarge", "Pr_CartSmall", "Cart_Wood", "Prop_Wagon"]

# --- acampamento (partida): fogueira com pedras e toras, barracas (as bancas), carga, poço e estandartes
FX, FZ = -6.0, -3.0
put("Tv_Fire", FX, FZ, rot=0, scale=1.7, solid=[1.6, 1.6], r=2.0, free=0, force=True)
decor.append({"piece": "Fire_Flame", "position": [FX, FZ], "y": 0.2, "scale": 1.5, "flicker": True})
fire_light(FX, FZ, 1.8, 13.0, 1.0)
around("Rock_MossyStone", FX, FZ, 2.0, 10, scale=0.6, r=0.4, free=0, force=True)
for dx, dz, rot in ((3.4, 0.8, 80), (-3.2, 1.6, 15), (0.6, -3.4, 120), (-1.2, 3.4, 200)):
    put("Tv_Firewood", FX + dx, FZ + dz, rot=rot, scale=1.6, r=0.6, free=0, force=True)
for x, z, rot in ((-14, -7, 160), (-13, 6, 20), (14, 6, 200), (17, -4, 250)):
    put("Stall_Empty", x, z, rot=rot, scale=1.6, solid=[2.9, 1.5], r=2.0)
put("Stall_Cart_Empty", 15, -9, rot=170, scale=1.4, solid=[4.2, 1.5], r=2.5)
put("Pr_CoveredWell", -15, 10, rot=0, scale=1.3, solid=[2.3, 2.3], r=1.8)
for x, z in ((-4.5, -11), (4.5, -11), (-21, 8.5), (21, -9.5)):
    put("War_Banner" if abs(x) < 5 else "Banner_1", x, z, rot=0 if abs(x) < 5 else 90, scale=1.1, r=0.8)
for x, z in ((-19, -11), (19, 11), (-19, 11), (19, -11), (-11, -3), (-1, 1)):
    torch(x, z)
scatter("camp", CARGO, 18, scale=(0.8, 1.1), margin=3.0, r=0.9)
scatter("camp", ["Cart_Wood"], 1, scale=(1.4, 1.4), solid=[3.2, 1.5], margin=5.0, r=2.0)
# --- caravana arruinada (oeste do acampamento)
scatter("caravan", WRECKS, 5, scale=(1.0, 1.4), solid=(2.6, 1.6), margin=4.0, r=2.4)
scatter("caravan", CARGO, 20, scale=(0.8, 1.2), margin=3.0)
scatter("caravan", BONES, 12, scale=(2.5, 3.5), margin=3.0, r=0.8)
scatter("caravan", ["Canyon_Tree_1", "Canyon_Tree_2", "Dead_Tree"], 3, scale=(0.8, 1.1), margin=3.0, r=2.2)
# --- estrada das caravanas: obeliscos em fileira, colunas quebradas, ossos e uma estátua caída
for i, z in enumerate((-20, -28, -36, -44, -52)):
    for sx in (-1, 1):
        put("Pr_Obelisk3" if i % 2 == 0 else "Pr_Obelisk2", sx * 11, z, rot=0, scale=1.3 if i % 2 == 0 else 1.5, solid=[1.2, 1.2], r=1.4)
scatter("road", ["Pr_BrokenPillar1", "Pr_BrokenPillar2", "Ruin_PillarStub"], 5, scale=(1.0, 1.4), solid=(1.0, 1.0), margin=3.0, r=1.3)
scatter("road", BONES, 10, scale=(2.5, 3.5), margin=3.0, r=0.8)
put("Statue_Knight_Lying", 10, -30, scale=1.6, solid=[1.8, 2.8], r=1.8)
scatter("road", ["Dead_Tree", "Canyon_Tree_3"], 3, scale=(0.7, 1.0), margin=4.0, r=2.4)
# --- oásis: lagoa com moitas, flores, juncos (bambu), pedras e uma barraca
OX, OZ = -34, -37
around("Rock_MossyStone", OX, OZ, 6.6, 16, scale=0.9, r=0.8, free=0.5)
around("Pl_Bamboo", OX, OZ, 9.6, 10, scale=0.55, r=1.4, free=0.5)
scatter("oasis", ["Pl_Bush", "Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3"], 14, scale=(0.8, 1.2), margin=3.0, r=1.2)
scatter("oasis", ["Pl_Flower", "Pl_Grass1", "Pl_Grass2", "Pl_Grass3", "Pl_Weed1", "Pl_Weed2"], 34, scale=(0.8, 1.3), margin=2.5, r=0.6, free=1.5)
scatter("oasis", ["Canyon_Tree_1", "Canyon_Tree_2", "Canyon_Tree_4"], 4, scale=(1.2, 1.6), margin=3.5, r=2.0)
put("Stall_Empty", -23, -27, rot=210, scale=1.6, solid=[2.9, 1.5], r=2.0)
scatter("oasis", ["Pot_Large", "Tv_Basket", "Vase_2", "Pr_Basket"], 6, scale=(1.0, 1.3), margin=3.0, r=0.8)
# --- ruínas de carroças (comboio atacado): carroças, carga espalhada, estandartes caídos e esqueletos
scatter("wrecks", WRECKS, 7, scale=(1.0, 1.5), solid=(2.6, 1.6), margin=3.5, r=2.4)
scatter("wrecks", CARGO, 26, scale=(0.8, 1.2), margin=3.0)
scatter("wrecks", BONES, 14, scale=(2.5, 3.5), margin=3.0, r=0.8)
scatter("wrecks", ["War_Banner"], 3, scale=(1.0, 1.2), solid=(0.6, 0.6), margin=4.0, r=1.0)
scatter("wrecks", ["Statue_Knight_Lying"], 2, scale=(1.4, 1.8), solid=(1.8, 2.8), margin=4.0, r=1.8)
scatter("wrecks", ["Pr_BrokenPillar1", "Pr_BrokenPillar2"], 3, scale=(1.0, 1.4), solid=(1.0, 1.0), margin=3.0, r=1.3)
# --- passagem estreita
scatter("pass", BONES, 6, scale=(2.5, 3.5), margin=2.0, r=0.8)
scatter("pass", ["Dungeon_SkullPile", "Dungeon_Ribcage"], 3, scale=(3.0, 4.0), margin=2.0, r=1.0)
# --- dunas: arco monumental na entrada, obeliscos, costelas gigantes, árvores secas
put("Ruin_Arch", 0, -64, rot=0, scale=1.2, r=4.0, free=1.0)
for x, z in ((-16, -78), (16, -78), (-16, -92), (16, -92)):
    put("Pr_Obelisk3", x, z, rot=0, scale=1.5, solid=[1.4, 1.4], r=1.6)
scatter("dunes", BIG_BONES, 8, scale=(4.0, 6.0), margin=4.0, r=2.0)
scatter("dunes", BONES, 14, scale=(2.5, 3.5), margin=3.0, r=0.8)
scatter("dunes", ["Dungeon_SkullPile"], 4, scale=(3.0, 4.0), margin=3.0, r=1.0)
scatter("dunes", ["Dead_Tree", "Canyon_Tree_1", "Canyon_Tree_3"], 5, scale=(0.8, 1.2), margin=4.0, r=2.4)
scatter("dunes", ["Pr_BrokenPillar2", "Ruin_PillarStub"], 4, scale=(1.0, 1.4), solid=(1.0, 1.0), margin=3.0, r=1.3)
# --- ninho dos escorpiões: teias, ossos de vítimas e caveiras
scatter("nest", ["Web_Round_Up"], 9, scale=(3.0, 4.2), margin=3.0, r=1.2, free=1.5)
scatter("nest", BONES, 18, scale=(2.5, 3.5), margin=3.0, r=0.8)
scatter("nest", ["Dungeon_SkullPile", "Dungeon_Ribcage", "Dungeon_Spine"], 8, scale=(3.5, 5.0), margin=3.0, r=1.2)
scatter("nest", ["Dead_Tree"], 2, scale=(0.8, 1.0), margin=4.0, r=2.4)
# --- areia movediça: ossos de bichos enormes, pilares meio afundados
scatter("quicksand", BIG_BONES, 7, scale=(4.5, 6.5), margin=3.5, r=2.0)
scatter("quicksand", ["Pr_BrokenPillar1", "Pr_BrokenPillar2", "Ruin_PillarStub"], 5, scale=(1.0, 1.5), solid=(1.0, 1.0), margin=3.0, r=1.3, y=-0.35)
scatter("quicksand", ["Statue_Knight_Lying"], 1, scale=(1.6, 1.6), margin=4.0, r=1.8, y=-0.3)
scatter("quicksand", BONES, 8, scale=(2.5, 3.5), margin=3.0, r=0.8)
scatter("quicksand", ["Dead_Tree"], 3, scale=(0.8, 1.1), margin=4.0, r=2.4)
# --- Ruínas do Sol: coroa de colunas em volta do templo, muros, estátuas, tochas e obeliscos
TX, TZ = 76, -84
around("Ruin_Column", TX, TZ, 12.5, 14, start=0.2, scale=1.25, solid=[1.0, 1.0], r=1.0, free=1.0)
around("Ruin_PillarStub", TX, TZ, 15.5, 12, start=0.5, scale=1.3, solid=[0.8, 0.8], r=1.0, free=1.0)
put("Ruin_Arch", 62.5, -84, rot=90, scale=1.1, r=4.0, free=1.0)
for x, z, rot in ((TX - 8, TZ + 7, 160), (TX + 8, TZ + 7, 200)):
    put("Statue_Knight", x, z, rot=rot, scale=1.5, solid=[1.5, 1.6], r=1.6)
for x, z in ((TX - 8, TZ - 9), (TX + 8, TZ - 9)):
    put("Statue_Lamp", x, z, rot=0, scale=1.2, solid=[2.2, 1.4], r=1.8)
    fire_light(x, z, 1.1, 8.0, 2.6, (1.0, 0.8, 0.45))
for x, z in ((TX - 14, TZ - 14), (TX + 14, TZ - 14), (TX - 14, TZ + 14), (TX + 14, TZ + 14)):
    put("Pr_Obelisk3", x, z, rot=0, scale=1.6, solid=[1.5, 1.5], r=1.8)
for x, z, rot in ((TX - 14, TZ - 7, 0), (TX + 14, TZ + 4, 90), (TX + 2, TZ + 15, 0)):
    put("Ruin_Wall", x, z, rot=rot, scale=1.0, solid=[6.0, 0.6], r=3.2)
scatter("ruins", ["Ruin_Stones"], 2, scale=(0.9, 1.2), solid=(7.0, 6.0), margin=5.0, r=4.5)
scatter("ruins", ["Pr_BrokenPillar1", "Pr_BrokenPillar2", "Ruin_WallStub"], 8, scale=(1.0, 1.5), solid=(1.0, 1.0), margin=3.0, r=1.3)
scatter("ruins", BONES, 8, scale=(2.5, 3.5), margin=3.0, r=0.8)
for ang in (0.7, 2.3, 3.9, 5.5):
    torch(TX + 10 * math.cos(ang), TZ + 10 * math.sin(ang))
# --- corredor do portão: avenida de colunas, estandartes e estátuas-lâmpada
for z in (-112, -118, -124):
    for sx in (-1, 1):
        put("Ruin_Column", sx * 4.4, z, rot=0, scale=1.2, solid=[1.0, 1.0], r=0.8, free=1.0)
for z in (-115, -121):
    for sx in (-1, 1):
        put("War_Banner", sx * 4.6, z, rot=90 * sx, scale=1.0, r=0.8, free=0.8)
for sx in (-1, 1):
    put("Statue_Lamp", sx * 4.4, -131, rot=0, scale=1.1, solid=[2.0, 1.2], r=1.4, free=1.2)
    fire_light(sx * 4.4, -131, 1.0, 8.0, 2.5, (1.0, 0.75, 0.4))
for z in (-111, -127):
    torch(-5.0, z)
    torch(5.0, z)
# --- Salão da Esfinge: avenida de colunas, arco, braseiros, estátuas, obeliscos, vasos e as vítimas da Esfinge
put("Ruin_Arch", 0, -142.5, rot=0, scale=1.5, r=5.0, free=0.5)
for i, z in enumerate(range(-148, -179, -6)):
    for sx in (-1, 1):
        put("Ruin_Column", sx * 9.5, z, rot=0, scale=1.4, solid=[1.2, 1.2], r=1.1, free=1.0)
        if i % 2 == 0:
            brazier(sx * 13.5, z)
for x, z in ((-24, -150), (24, -150), (-24, -184), (24, -184), (-24, -167), (24, -167)):
    put("Pr_Obelisk3", x, z, rot=0, scale=1.7, solid=[1.6, 1.6], r=1.8)
for sx in (-1, 1):
    put("Statue_Lamp", sx * 15, -187, rot=0, scale=1.5, solid=[3.0, 1.8], r=2.0)
    fire_light(sx * 15, -187, 1.4, 11.0, 3.2, (1.0, 0.8, 0.45))
    for z in (-158, -172):
        put("Statue_Knight", sx * 20, z, rot=-90 * sx, scale=1.7, solid=[1.7, 1.8], r=1.8)
    for z in (-150, -176):
        put("War_Banner", sx * 18, z, rot=-90 * sx, scale=1.3, r=1.0)
scatter("sphinx", ["Vase_Big", "Vase_2", "Pot_Large"], 12, scale=(0.9, 1.3), margin=3.0, r=1.0)
scatter("sphinx", BIG_BONES, 4, scale=(5.0, 7.0), margin=4.0, r=2.2)
scatter("sphinx", BONES, 16, scale=(2.5, 3.5), margin=4.0, r=0.8)
scatter("sphinx", ["Dungeon_SkullPile"], 5, scale=(3.0, 4.0), margin=4.0, r=1.0)
scatter("sphinx", ["Pr_BrokenPillar1", "Pr_BrokenPillar2", "Ruin_PillarStub"], 6, scale=(1.2, 1.6), solid=(1.0, 1.0), margin=4.0, r=1.4)
# --- um pouco de tudo pelo mapa todo: ossos soltos e árvores secas
for r_ in rooms:
    if r_["id"] not in ("camp", "gate_lane", "sphinx"):
        scatter(r_["id"], BONES, max(2, round(r_["size"][0] * r_["size"][1] / 450)), scale=(2.5, 3.5), margin=2.5, r=0.8)

# Dentro das salas: pedregulhos com colisão, cactos, capim, árvores secas, galhos e folhas
INTERIOR = {"cactus": (["Canyon_Cactus_Tall_%d" % i for i in range(1, 6)] + ["Canyon_Cactus_Small_%d" % i for i in range(1, 6)] + ["Canyon_Cactus_Flat_%d" % i for i in range(1, 4)], 0.012),
            "grass": (["Canyon_Grass_1", "Canyon_Grass_6", "Canyon_Grass_10", "Canyon_Sticks_1", "Canyon_Sticks_2", "Canyon_Leafs_1"], 0.02),
            "tree": (["Canyon_Tree_%d" % i for i in range(1, 5)], 0.003)}
BOULDERS = {"Canyon_Rock_Boulders_%d" % i: s for i, s in ((1, 2.0), (2, 2.2), (3, 2.2), (4, 3.4), (5, 2.0), (6, 1.6))}
for r in rooms:
    cx, cz = r["center"]
    w, h = r["size"]
    area = w * h
    calm = 0.35 if r["id"] in ("camp", "gate_lane") else 1.0  # acampamento e corredor do portão: pouca coisa no chão
    for _ in range(max(2, round(area / 150 * calm))):  # pedregulhos (colisão)
        for _try in range(20):
            x, z = cx + rng.uniform(-w / 2 + 3.5, w / 2 - 3.5), cz + rng.uniform(-h / 2 + 3.5, h / 2 - 3.5)
            if near_interest(x, z, 6.0) or near_taken(x, z, 2.5):
                continue
            name = rng.choice(list(BOULDERS))
            decor.append({"piece": name, "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15), "solid": [round(BOULDERS[name] * 0.8, 1)] * 2})
            break
    for kind, (pieces, density) in INTERIOR.items():
        for _ in range(round(area * density * calm)):
            x, z = cx + rng.uniform(-w / 2 + 1.5, w / 2 - 1.5), cz + rng.uniform(-h / 2 + 1.5, h / 2 - 1.5)
            if near_interest(x, z, 3.0) or near_taken(x, z, 1.2):
                continue
            d = {"piece": rng.choice(pieces), "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15)}
            if kind != "grass":
                d["scale"] = round(rng.uniform(0.9, 1.4), 2)
            decor.append(d)

breakables = [{"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"}]
for i, pos in enumerate(([-30, 14], [20, -40], [-8, -62], [-52, -76], [56, -90], [92, -80], [-18, -158], [18, -158]), start=2):
    breakables.append({"id": "coin_bag_%d" % i, "monster": "coin_bag", "position": pos, "table": "coin_bag"})

arenas["desert_01_canyon"] = {
    "_comment": "Deserto — o Cânion (Canyon Terrain Asset, loafbrr / Ian87, CC0), mapa grande com a estrutura da Floresta e outro caminho: acampamento ao sul, rota em laço para o norte "
                "(estrada, ruínas de carroças, passagem, areia movediça, dunas) e ramais sem saída (Caravana, Ninho, Oásis, Ruínas do Sol). 2 mini-chefes: a Rainha Escorpião (o NPC do Oásis a "
                "desperta) e o Lamassu da Areia (o templo das Ruínas do Sol). O Sentinela do Portão pede as duas chaves; atrás do portão fica a Esfinge (chefe final) e a saída. "
                "Liga-se à Capital (tools/assets/set_map_order.py). Gerado por tools/assets/build_desert.py.",
    "name_key": "ARENA_DESERT", "outdoor": True, "player_class": "mage", "map_id": "map_desert", "area_level": 7, "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": rooms, "encounters": [{"id": i, "position": p, "monsters": [{"monster": m, "count": c} for m, c in mons]} for i, p, mons in encounters], "hazards": [],
    "entries": {"start": [0, 7], "desert": [0, 7]}, "props": props, "quest_spots": [], "breakables": breakables,
    "style": {"_comment": "Cânion: chão de areia (Ground_Canyon), sem muro do kit; as paredes são as formações de rocha (decor).", "walls": [""], "floor": "Ground_Canyon", "low": "",
              "ground": [0.5, 0.36, 0.22]},
    "decor": decor, "passive": True}
# (o portal do Deserto fica na Capital: tools/assets/set_map_order.py)

# ---------------------------------------------------------------- monstros (Esfinge) e itens de missão
sphinx = json.loads(json.dumps(monsters["leshy"]))
sphinx.pop("quest_drop", None)
sphinx.update({"_comment": "Chefe final do Deserto (docs/03-2-areas.md): a Esfinge, guardiã do Salão atrás do portão; investidas e pisões (modelo do golem de pedra, dourado).",
               "name_key": "MONSTER_SPHINX", "category": "boss", "aggressive": False, "max_health": 900, "damage": 36, "size": 4.2, "element": "air", "look": "golem_stone", "color": [1.0, 0.8, 0.45], "chest_loot": "chest"})
monsters["sphinx"] = sphinx
monsters["sand_lamassu"]["quest_drop"] = "lamassu_horn"
monsters["queen_scorpion"]["quest_drop"] = "golden_scarab"
valuables.update({
    "lamassu_horn": {"name_key": "VALUABLE_LAMASSU_HORN", "value": 0, "maps": [], "quest_item": True, "model": "Bone_Sickle"},
    "golden_scarab": {"name_key": "VALUABLE_GOLDEN_SCARAB", "value": 0, "maps": [], "quest_item": True, "model": "Crystal_Gem"},
    "key_clubs": {"name_key": "VALUABLE_KEY_CLUBS", "value": 0, "maps": [], "quest_item": True, "model": "Key_Clubs"},
    "key_diamonds": {"name_key": "VALUABLE_KEY_DIAMONDS", "value": 0, "maps": [], "quest_item": True, "model": "Key_Diamonds"}})

# ---------------------------------------------------------------- NPCs e missões (mesma forma da Floresta)
def body(sex, hair, color):
    return {"sex": sex, "hair": [hair], "hair_color": color, "pose": "idle", "outfit": {"body": "cloth"}}


npcs["desert_nomad"] = {"name_key": "NPC_DESERT_NOMAD", "color": [0.7, 0.55, 0.3], "dialogues": [
    {"when": {"quest_new": "desert_horn"}, "lines": ["DLG_NOMAD_1", "DLG_NOMAD_2", "DLG_NOMAD_3"], "offer": "desert_horn"},
    {"when": {"quest_active": "desert_horn"}, "lines": ["DLG_NOMAD_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_NOMAD_DONE"]}], "body": body("male", "Hair_SimpleParted", [0.2, 0.13, 0.08])}
npcs["desert_oasis_keeper"] = {"name_key": "NPC_DESERT_OASIS_KEEPER", "color": [0.2, 0.6, 0.55], "dialogues": [
    {"when": {"quest_new": "desert_scarab"}, "lines": ["DLG_OASIS_1", "DLG_OASIS_2", "DLG_OASIS_3"], "offer": "desert_scarab"},
    {"when": {"quest_active": "desert_scarab"}, "lines": ["DLG_OASIS_ACTIVE"], "service": "turn_in"},
    {"when": {"quest_done": "desert_scarab"}, "lines": ["DLG_OASIS_DONE"]},
    {"when": {}, "lines": ["DLG_OASIS_WAIT"]}], "body": body("female", "Hair_Long", [0.08, 0.06, 0.05])}
npcs["desert_temple"] = {"name_key": "NPC_DESERT_TEMPLE", "color": [0.85, 0.7, 0.4], "dialogues": [
    {"when": {"quest_active": "desert_horn"}, "lines": ["DLG_SUNTEMPLE_1", "DLG_SUNTEMPLE_2"]},
    {"when": {}, "lines": ["DLG_SUNTEMPLE_LOCKED"]}]}
npcs["desert_sentinel"] = {"name_key": "NPC_DESERT_SENTINEL", "color": [0.55, 0.5, 0.4], "dialogues": [
    {"when": {"quest_new": "desert_gate"}, "lines": ["DLG_SENTINEL_1", "DLG_SENTINEL_2", "DLG_SENTINEL_3"], "offer": "desert_gate"},
    {"when": {"quest_active": "desert_gate"}, "lines": ["DLG_SENTINEL_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_SENTINEL_DONE"]}], "body": body("male", "Hair_SimpleParted", [0.12, 0.1, 0.08])}
quests["desert_horn"] = {"name_key": "QUEST_DESERT_HORN", "desc_key": "QUEST_DESERT_HORN_DESC", "type": "village", "giver": "desert_nomad", "area": "desert_01_canyon",
                         "target_element": "water", "reward": {"gold": 350, "xp": 600}, "item": "lamassu_horn", "gives": "key_clubs"}
quests["desert_scarab"] = {"name_key": "QUEST_DESERT_SCARAB", "desc_key": "QUEST_DESERT_SCARAB_DESC", "type": "village", "giver": "desert_oasis_keeper", "area": "desert_01_canyon",
                           "target_element": "earth", "reward": {"gold": 300, "xp": 500}, "item": "golden_scarab", "gives": "key_diamonds"}
quests["desert_gate"] = {"name_key": "QUEST_DESERT_GATE", "desc_key": "QUEST_DESERT_GATE_DESC", "type": "village", "giver": "desert_sentinel", "area": "desert_01_canyon",
                         "items": ["key_clubs", "key_diamonds"], "opens_gate": "boss_gate", "target_element": "air", "reward": {"gold": 450, "xp": 800}}

TEXTS = {  # chave: (pt_BR, en, es)
    "MONSTER_SPHINX": ("Esfinge", "Sphinx", "Esfinge"),
    "NPC_DESERT_NOMAD": ("Nômade da Areia", "Sand Nomad", "Nómada de la Arena"),
    "NPC_DESERT_OASIS_KEEPER": ("Guardiã do Oásis", "Oasis Keeper", "Guardiana del Oasis"),
    "NPC_DESERT_TEMPLE": ("Templo do Sol", "Sun Temple", "Templo del Sol"),
    "NPC_DESERT_SENTINEL": ("Sentinela do Portão", "Gate Sentinel", "Centinela del Portón"),
    "VALUABLE_LAMASSU_HORN": ("Chifre do Lamassu", "Lamassu Horn", "Cuerno del Lamasu"),
    "VALUABLE_GOLDEN_SCARAB": ("Escaravelho de Ouro", "Golden Scarab", "Escarabajo de Oro"),
    "VALUABLE_KEY_CLUBS": ("Chave de Paus", "Key of Clubs", "Llave de Bastos"),
    "VALUABLE_KEY_DIAMONDS": ("Chave de Ouros", "Key of Diamonds", "Llave de Oros"),
    "TOAST_OASIS_AWAKENS": ("A água do oásis se agita: a Rainha Escorpião emerge da areia!", "The oasis water stirs: the Scorpion Queen bursts from the sand!",
                            "El agua del oasis se agita: ¡la Reina Escorpión surge de la arena!"),
    "TOAST_SUN_TEMPLE_AWAKENS": ("O templo do sol estremece: o Lamassu da Areia desperta!", "The sun temple shakes: the Sand Lamassu awakens!",
                                 "El templo del sol tiembla: ¡el Lamasu de la Arena despierta!"),
    "QUEST_DESERT_HORN": ("O Chifre do Lamassu", "The Lamassu's Horn", "El cuerno del Lamasu"),
    "QUEST_DESERT_HORN_DESC": ("O Nômade da Areia quer o chifre do Lamassu, o guardião de pedra das Ruínas do Sol, a leste. Toque o templo, derrote o Lamassu e traga o chifre: em troca, ele dá uma das duas chaves do portão da Esfinge.",
                               "The Sand Nomad wants the horn of the Lamassu, the stone guardian of the Sun Ruins to the east. Touch the temple, defeat the Lamassu and bring the horn: in return he gives one of the two keys to the Sphinx's gate.",
                               "El Nómada de la Arena quiere el cuerno del Lamasu, el guardián de piedra de las Ruinas del Sol, al este. Toca el templo, derrota al Lamasu y trae el cuerno: a cambio te da una de las dos llaves del portón de la Esfinge."),
    "QUEST_DESERT_SCARAB": ("O Escaravelho de Ouro", "The Golden Scarab", "El escarabajo de oro"),
    "QUEST_DESERT_SCARAB_DESC": ("A Guardiã do Oásis perdeu o escaravelho de ouro da sua gente: a Rainha Escorpião o carrega no ferrão. Ela desperta a Rainha com a sua fala; traga o escaravelho e receba a outra chave do portão da Esfinge.",
                                 "The Oasis Keeper lost her people's golden scarab: the Scorpion Queen wears it on her stinger. Her words wake the Queen; bring back the scarab and receive the other key to the Sphinx's gate.",
                                 "La Guardiana del Oasis perdió el escarabajo de oro de su gente: la Reina Escorpión lo lleva en el aguijón. Sus palabras despiertan a la Reina; trae el escarabajo y recibe la otra llave del portón de la Esfinge."),
    "QUEST_DESERT_GATE": ("O Portão da Esfinge", "The Sphinx's Gate", "El portón de la Esfinge"),
    "QUEST_DESERT_GATE_DESC": ("O Sentinela do Portão só abre o caminho para quem trouxer as duas chaves: a de Paus (com o Nômade) e a de Ouros (com a Guardiã do Oásis). Atrás do portão fica o Salão da Esfinge.",
                               "The Gate Sentinel only opens the way for those who bring both keys: Clubs (from the Nomad) and Diamonds (from the Oasis Keeper). Beyond the gate lies the Sphinx's Hall.",
                               "El Centinela del Portón solo abre el paso a quien traiga las dos llaves: la de Bastos (del Nómada) y la de Oros (de la Guardiana del Oasis). Tras el portón está el Salón de la Esfinge."),
    "DLG_NOMAD_1": ("A areia engole caravanas inteiras, viajantes. Sou o que sobrou da última: sei onde cada poço e cada ruína ficam, e sei o que dorme em cada uma.",
                    "The sand swallows whole caravans, travelers. I am what is left of the last one: I know where every well and ruin lies, and what sleeps in each.",
                    "La arena se traga caravanas enteras, viajeros. Soy lo que queda de la última: sé dónde está cada pozo y cada ruina, y qué duerme en cada una."),
    "DLG_NOMAD_2": ("Ao leste, nas Ruínas do Sol, um templo guarda o Lamassu da Areia, um touro alado de pedra. Ele carrega um chifre dourado que vale mais que a minha caravana inteira.",
                    "To the east, in the Sun Ruins, a temple guards the Sand Lamassu, a winged bull of stone. It carries a golden horn worth more than my whole caravan.",
                    "Al este, en las Ruinas del Sol, un templo guarda al Lamasu de la Arena, un toro alado de piedra. Lleva un cuerno dorado que vale más que toda mi caravana."),
    "DLG_NOMAD_3": ("Toquem as pedras do templo, derrubem o Lamassu e tragam o chifre. Em troca, dou a Chave de Paus, uma das duas que abrem o portão da Esfinge, ao norte das dunas.",
                    "Touch the temple stones, bring down the Lamassu and bring me the horn. In return I give the Key of Clubs, one of the two that open the Sphinx's gate, north of the dunes.",
                    "Toquen las piedras del templo, derriben al Lamasu y tráiganme el cuerno. A cambio doy la Llave de Bastos, una de las dos que abren el portón de la Esfinge, al norte de las dunas."),
    "DLG_NOMAD_ACTIVE": ("O templo fica a leste: sigam a estrada, passem pelas dunas e pela areia movediça. O chifre é dourado e do tamanho de um braço. Tragam-no e a chave é de vocês.",
                         "The temple is to the east: follow the road, cross the dunes and the quicksand. The horn is golden and as long as an arm. Bring it and the key is yours.",
                         "El templo está al este: sigan el camino, crucen las dunas y las arenas movedizas. El cuerno es dorado y largo como un brazo. Tráiganlo y la llave es suya."),
    "DLG_NOMAD_DONE": ("Que chifre! Com ele eu refaço a caravana. A Chave de Paus é de vocês; levem-na ao Sentinela do Portão, junto com a de Ouros.",
                       "What a horn! With it I can rebuild my caravan. The Key of Clubs is yours; take it to the Gate Sentinel, together with the Diamonds one.",
                       "¡Qué cuerno! Con él rehago mi caravana. La Llave de Bastos es suya; llévenla al Centinela del Portón, junto con la de Oros."),
    "DLG_OASIS_1": ("Shh... a água ouve. Eu cuido deste oásis desde antes de a areia chegar, e só o que me ficou foi esta poça.",
                    "Shh... the water listens. I have tended this oasis since before the sand arrived, and all that is left to me is this pool.",
                    "Shh... el agua escucha. Cuido este oasis desde antes de que llegara la arena, y solo me queda este charco."),
    "DLG_OASIS_2": ("A Rainha Escorpião dorme sob a areia, aqui perto, e usa no ferrão o escaravelho de ouro da minha gente. Sem ele, o oásis seca de vez.",
                    "The Scorpion Queen sleeps under the sand nearby, wearing my people's golden scarab on her stinger. Without it the oasis dries up for good.",
                    "La Reina Escorpión duerme bajo la arena, cerca de aquí, y lleva en el aguijón el escarabajo de oro de mi gente. Sin él, el oasis se seca para siempre."),
    "DLG_OASIS_3": ("Vou chamá-la para vocês. Derrubem a Rainha e tragam o escaravelho: eu entrego a Chave de Ouros, a outra que abre o portão da Esfinge.",
                    "I will call her for you. Bring down the Queen and bring back the scarab: I will hand over the Key of Diamonds, the other one that opens the Sphinx's gate.",
                    "La llamaré para ustedes. Derriben a la Reina y traigan el escarabajo: les entrego la Llave de Oros, la otra que abre el portón de la Esfinge."),
    "DLG_OASIS_ACTIVE": ("O escaravelho brilha como uma gota de sol. A Rainha o carrega no ferrão. Derrubem-na e tragam-no para mim.",
                         "The scarab shines like a drop of sun. The Queen wears it on her stinger. Bring her down and bring it to me.",
                         "El escarabajo brilla como una gota de sol. La Reina lo lleva en el aguijón. Derríbenla y tráiganmelo."),
    "DLG_OASIS_DONE": ("A água voltou a cantar! A Chave de Ouros é de vocês. Levem-na ao Sentinela, no corredor ao norte das dunas.",
                       "The water sings again! The Key of Diamonds is yours. Take it to the Sentinel, in the lane north of the dunes.",
                       "¡El agua vuelve a cantar! La Llave de Oros es suya. Llévenla al Centinela, en el pasillo al norte de las dunas."),
    "DLG_OASIS_WAIT": ("Bebam, descansem. A água é de quem a respeita.", "Drink, rest. The water belongs to those who respect it.", "Beban, descansen. El agua es de quien la respeta."),
    "DLG_SUNTEMPLE_1": ("As pedras do templo estão quentes, como se alguém tivesse acabado de sair daqui. Um rugido de pedra sobe do subsolo.",
                        "The temple stones are warm, as if someone had just left. A roar of stone rises from below.",
                        "Las piedras del templo están calientes, como si alguien acabara de salir. Un rugido de piedra sube del subsuelo."),
    "DLG_SUNTEMPLE_2": ("O Lamassu da Areia desperta!", "The Sand Lamassu awakens!", "¡El Lamasu de la Arena despierta!"),
    "DLG_SUNTEMPLE_LOCKED": ("Um templo antigo, coberto de areia. Nada responde às suas mãos.", "An ancient temple buried in sand. Nothing answers your hands.",
                             "Un templo antiguo cubierto de arena. Nada responde a sus manos."),
    "DLG_SENTINEL_1": ("Alto, forasteiros. Este portão é mais velho que as dunas, e atrás dele dorme a Esfinge. Eu o vigio desde que o último rei passou por aqui.",
                       "Halt, strangers. This gate is older than the dunes, and behind it sleeps the Sphinx. I have watched it since the last king passed this way.",
                       "Alto, forasteros. Este portón es más viejo que las dunas, y tras él duerme la Esfinge. Lo vigilo desde que pasó el último rey."),
    "DLG_SENTINEL_2": ("O portão só cai para quem trouxer DUAS chaves: a de Paus e a de Ouros. A primeira está com o Nômade da Areia, no acampamento; a segunda, com a Guardiã do Oásis.",
                       "The gate only falls for those who bring TWO keys: Clubs and Diamonds. The first is with the Sand Nomad at the camp; the second, with the Oasis Keeper.",
                       "El portón solo cae para quien traiga DOS llaves: la de Bastos y la de Oros. La primera la tiene el Nómada de la Arena, en el campamento; la segunda, la Guardiana del Oasis."),
    "DLG_SENTINEL_3": ("Os dois cobram um preço: um chifre de pedra, um escaravelho de ouro. Tragam as duas chaves a mim e eu abro a passagem.",
                       "Both charge a price: a stone horn, a golden scarab. Bring both keys to me and I will open the way.",
                       "Ambos cobran un precio: un cuerno de piedra, un escarabajo de oro. Tráiganme las dos llaves y abro el paso."),
    "DLG_SENTINEL_ACTIVE": ("Só abro com as duas chaves, Paus e Ouros, na mesma bolsa. O Nômade fica no acampamento; a Guardiã, no oásis a oeste da estrada.",
                            "I only open with both keys, Clubs and Diamonds, in the same bag. The Nomad is at the camp; the Keeper, at the oasis west of the road.",
                            "Solo abro con las dos llaves, Bastos y Oros, en la misma bolsa. El Nómada está en el campamento; la Guardiana, en el oasis al oeste del camino."),
    "DLG_SENTINEL_DONE": ("As duas chaves! O portão está aberto. Cuidado: a Esfinge faz uma pergunta e não aceita silêncio como resposta.",
                          "Both keys! The gate is open. Beware: the Sphinx asks a question and does not accept silence as an answer.",
                          "¡Las dos llaves! El portón está abierto. Cuidado: la Esfinge hace una pregunta y no acepta el silencio como respuesta."),
}
for lang_i, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po", "locale/messages.pot")):
    t = open(path, encoding="utf-8").read()
    add = ""
    for key, trio in TEXTS.items():
        val = "" if path.endswith(".pot") else trio[lang_i].replace('"', '\\"')
        if re.search(r'msgid "%s"\n' % re.escape(key), t):
            t = re.sub(r'(msgid "%s"\nmsgstr )"[^\n]*"' % re.escape(key), lambda m: m.group(1) + '"' + val.replace("\\", "\\\\") + '"', t) if val else t
        else:
            add += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, val)
    open(path, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + add)

# ---------------------------------------------------------------- ícones dos itens (tingidos dos que já existem)
try:
    from PIL import Image
    ICONS = "assets/ui/icons/"
    for dst, src, mul in (("key_clubs", "key_spades", (0.55, 1.15, 0.6)), ("key_diamonds", "key_hearts", (0.5, 0.8, 1.4)),
                          ("lamassu_horn", "bone_dagger", (1.0, 0.85, 0.55)), ("golden_scarab", "royal_seal_ring", (1.0, 1.0, 0.6))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        im = Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_))
        im.save(ICONS + dst + ".png")
except Exception as exc:  # sem PIL: os itens ficam sem ícone próprio
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (MONSTERS, monsters), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK desert", len(rooms), "salas,", len(decor), "peças de cenário,", len(encounters), "encontros")
