"""Gera os mapas da expedição depois do Esgoto (data/arenas.json): Floresta, Ruínas, Cemitério e Forte, na
ordem Tortuga -> Floresta -> Ruínas -> Cemitério -> Forte. As salas, os encontros e o cenário saem daqui
(sorteio com semente fixa), então rodar de novo reproduz o mesmo mapa. Também cria os monstros novos
(data/monsters.json) e o portal de Tortuga para a Floresta.
uso: python3 tools/assets/build_maps.py   (a partir da raiz do projeto)"""
import json, random, math

ARENAS = "data/arenas.json"
MONSTERS = "data/monsters.json"
arenas = json.load(open(ARENAS))
monsters = json.load(open(MONSTERS))


def rng(name):
    return random.Random(name)


def room(rid, cx, cz, w, h, doors, **extra):
    r = {"id": rid, "center": [cx, cz], "size": [w, h], "doors": doors}
    r.update(extra)
    return r


def scatter(r, room_def, pieces, count, margin=2.0, keep=(), scale=(1.0, 1.0), solid=None, avoid=()):
    """Espalha `count` peças (sorteadas de `pieces`) dentro da sala, longe das portas e dos pontos em `avoid`."""
    cx, cz = room_def["center"]
    w, h = room_def["size"]
    out = []
    tries = 0
    while len(out) < count and tries < count * 40:
        tries += 1
        x = cx + r.uniform(-w / 2 + margin, w / 2 - margin)
        z = cz + r.uniform(-h / 2 + margin, h / 2 - margin)
        if any(math.hypot(x - ax, z - az) < ar for ax, az, ar in list(keep) + list(avoid)):
            continue
        piece = r.choice(pieces)
        entry = {"piece": piece, "position": [round(x, 1), round(z, 1)], "rotation": r.randrange(0, 360, 15)}
        sc = r.uniform(*scale)
        if sc != 1.0:
            entry["scale"] = round(sc, 2)
        if solid:
            entry["solid"] = solid
        out.append(entry)
    return out


def ring(r, room_def, pieces, step, inset=0.8, gaps=(), scale=(1.0, 1.0)):
    """Fileira de peças junto às paredes (vegetação de borda), deixando vãos nas portas."""
    cx, cz = room_def["center"]
    w, h = room_def["size"]
    out = []
    for side in ("north", "south", "west", "east"):
        horizontal = side in ("north", "south")
        length = w if horizontal else h
        n = int(length / step)
        for i in range(n):
            t = -length / 2 + step * (i + 0.5) + r.uniform(-0.3, 0.3)
            x, z = (cx + t, cz + (-h / 2 + inset if side == "north" else h / 2 - inset)) if horizontal else \
                (cx + (-w / 2 + inset if side == "west" else w / 2 - inset), cz + t)
            if side in room_def["doors"] or any(d.split(":")[0] == side for d in room_def["doors"]):
                off = [float(d.split(":")[1]) if ":" in d else 0.0 for d in room_def["doors"] if d.split(":")[0] == side][0]
                if abs(t - off) < 3.0:
                    continue
            if any(math.hypot(x - gx, z - gz) < gr for gx, gz, gr in gaps):
                continue
            out.append({"piece": r.choice(pieces), "position": [round(x, 1), round(z, 1)], "rotation": r.randrange(0, 360, 15),
                        "scale": round(r.uniform(*scale), 2)})
    return out


def monster(name, base, **changes):
    m = json.loads(json.dumps(monsters[base]))
    m.pop("_comment", None)
    m.update(changes)
    monsters[name] = m


# --- Monstros novos (placeholders de arte: reaproveitam os modelos existentes) --------------------
monster("leshy", "old_gator", _comment="Mini-chefe da Floresta (04-tortuga-e-missoes.md: o Leshy guarda a árvore anciã): gigante de casca, "
        "investidas e pisões; modelo do Monstro da Floresta (cdmir, CC0).", name_key="MONSTER_LESHY", max_health=220, damage=18, size=2.0,
        element="earth", look="forest", color=[0.8, 0.85, 0.7])
monster("ruin_warden", "old_gator", _comment="Mini-chefe das Ruínas: o guardião do cofre real (substitui Cérbero até haver modelo). Investidas rápidas.",
        name_key="MONSTER_RUIN_WARDEN", max_health=260, damage=20, size=2.2, element="fire", look="lizard", color=[1.0, 0.55, 0.3])
monster("crypt_scorpion", "old_gator", _comment="Mini-chefe do Cemitério: escorpião da cripta, gigante e escuro.",
        name_key="MONSTER_CRYPT_SCORPION", max_health=300, damage=22, size=3.0, element="water", look="scorpion", color=[0.45, 0.5, 0.65])
monster("fort_commander", "old_gator", _comment="Chefe do Forte: o comandante amaldiçoado (usa o modelo do Feiticeiro-Aranha até haver arte própria).",
        name_key="MONSTER_FORT_COMMANDER", max_health=400, damage=25, size=2.4, element="air", look="demon", color=[0.8, 0.9, 1.0])


# --- Floresta ---------------------------------------------------------------------------------------
fr = rng("forest")
f_rooms = [
    room("gate", 0, 0, 24, 14, ["north"], torch=True, wall_height=0.8),
    room("glade", 0, -17.5, 34, 21, ["south", "north", "east"], wall_height=0.8),
    room("side", 23, -17.5, 12, 21, ["west"], wall_height=0.8),
    room("path", 0, -34, 10, 12, ["south", "north"], wall_height=0.8),
    room("grove", 0, -62, 36, 44, ["south"], wall_height=0.8),
]
f_enc = [
    {"id": "f_toads", "position": [-8, -17], "monsters": [{"monster": "acid_toad", "count": 2}]},
    {"id": "f_rats", "position": [8, -22], "monsters": [{"monster": "mutant_rat", "count": 3}]},
    {"id": "f_side", "position": [23, -18], "monsters": [{"monster": "golden_lizard", "count": 2}]},
    {"id": "f_path", "position": [0, -34], "monsters": [{"monster": "plague_bat", "count": 3}]},
    {"id": "f_grove_a", "position": [-9, -52], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "f_grove_b", "position": [9, -54], "monsters": [{"monster": "mutant_rat", "count": 4}]},
    {"id": "f_leshy", "position": [0, -76], "monsters": [{"monster": "leshy", "count": 1}]},
]
f_decor = []
plants = ["Pl_Bush", "Pl_Swirl", "Pl_Hemp", "Pl_Flower"]
for rd in f_rooms:
    f_decor += ring(fr, rd, ["Pl_Bamboo", "Pl_Bamboo", "Pl_Bush"], 2.4, scale=(0.9, 1.5))
    f_decor += scatter(fr, rd, plants, int(rd["size"][0] * rd["size"][1] / 22), margin=2.0, avoid=[(0, 3, 3)])
# Pedras (Rocks, Nobiax, CC0): semente própria para não mexer no sorteio das plantas. As grandes bloqueiam, as pequenas são só enfeite.
ROCK_FOOTPRINT = {"Rock_1": 0.9, "Rock_2": 0.75, "Rock_3": 1.2, "Rock_4": 1.0, "Rock_5": 0.75}
rkr = rng("forest_rocks")
f_keep = [(0, 3, 4), (-6, 3, 3), (0, -82, 4), (24, -22, 3), (-14, -74, 3)] + [(e["position"][0], e["position"][1], 3) for e in f_enc]
for rd in f_rooms:
    for rock in scatter(rkr, rd, list(ROCK_FOOTPRINT), int(rd["size"][0] * rd["size"][1] / 70), margin=3.0, scale=(0.6, 2.2), avoid=f_keep):
        if rock["scale"] >= 1.2:
            side = round(ROCK_FOOTPRINT[rock["piece"]] * rock["scale"] * 0.85, 1)
            rock["solid"] = [side, side]
        f_decor.append(rock)
f_decor += [{"piece": "Pr_RoadSign", "position": [4, 2], "rotation": 200}, {"piece": "Pr_LampPost", "position": [-6, 3], "rotation": 0, "solid": [0.6, 0.6]},
            {"piece": "Pr_Obelisk3", "position": [0, -80], "solid": [1.4, 1.4]}, {"piece": "Pr_Obelisk2", "position": [-6, -78], "solid": [1.0, 1.0]},
            {"piece": "Pr_Obelisk2", "position": [6, -78], "solid": [1.0, 1.0]}, {"piece": "Pr_BrokenPillar2", "position": [-12, -70], "solid": [1.2, 1.2]},
            {"piece": "Pr_BrokenPillar1", "position": [12, -68], "solid": [1.2, 1.2]}, {"piece": "Pr_CoveredWell", "position": [-8, -4], "solid": [1.8, 1.8]}]
arenas["forest_01_path"] = {
    "_comment": "Floresta (04-tortuga-e-missoes.md, missão 3 na ordem do mapa: Tortuga -> Floresta -> Ruínas -> Cemitério -> Forte). Clareiras abertas com cerca viva de bambu e arbustos (Stylish Plants, Nobiax, CC0), obeliscos e pilares quebrados (Medieval Props Textured). O Leshy guarda o bosque do fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_FOREST", "player_class": "mage", "map_id": "map_forest", "area_level": 3, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": f_rooms, "encounters": f_enc, "hazards": [],
    "entries": {"start": [0, 3], "forest": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_ruins", "kind": "exit", "name_key": "PROP_TO_RUINS", "position": [0, -82], "to": "ruins_01_city", "entry": "start", "group": True},
        {"id": "forest_chest_1", "kind": "chest", "position": [24, -22], "loot": "chest"},
        {"id": "forest_chest_2", "kind": "chest", "position": [-14, -74], "loot": "chest"},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Floresta: sem piso do kit (chão de grama), cerca viva de arbustos nas bordas.", "walls": [""], "floor": "Ground_Grass", "low": "Pl_Bush",
              "ground": [0.12, 0.2, 0.09]},
    "decor": f_decor, "passive": True,
}

# --- Ruínas -------------------------------------------------------------------------------------------
rr = rng("ruins")
colliders = json.load(open("data/ruins_colliders.json"))["colliders"]
r_rooms = [
    room("approach", 0, 0, 56, 12, ["north"], wall_height=0.8),
    room("city", 0, -31, 56, 50, ["south", "north"], wall_height=0.8),
    room("vault", 0, -66, 30, 20, ["south"], wall_height=0.8),
]
r_enc = [
    {"id": "r_lizards_a", "position": [-14, -22], "monsters": [{"monster": "golden_lizard", "count": 3}]},
    {"id": "r_scorp", "position": [12, -28], "monsters": [{"monster": "venom_scorpion", "count": 3}]},
    {"id": "r_bats", "position": [0, -42], "monsters": [{"monster": "plague_bat", "count": 4}]},
    {"id": "r_lizards_b", "position": [-18, -44], "monsters": [{"monster": "golden_lizard", "count": 3}]},
    {"id": "r_warden", "position": [0, -70], "monsters": [{"monster": "ruin_warden", "count": 1}]},
]
r_decor = [{"collider": c["size"], "position": [c["position"][0], round(c["position"][1] - 31, 2)]} for c in colliders]
r_decor.append({"piece": "Ruins_Layout", "position": [0, -31], "rotation": 0})
for rd in r_rooms:
    r_decor += scatter(rr, rd, ["Pl_Bush", "Pl_Hemp"], int(rd["size"][0] * rd["size"][1] / 90), margin=2.0)
r_decor += [{"piece": "Pr_BrokenPillar1", "position": [-8, -2], "solid": [1.2, 1.2]}, {"piece": "Pr_BrokenPillar2", "position": [9, -3], "solid": [1.2, 1.2]},
            {"piece": "Pr_Obelisk3", "position": [0, -72], "solid": [1.4, 1.4]}, {"piece": "Pr_Cross4", "position": [-10, -68], "solid": [1.2, 1.2]}]
arenas["ruins_01_city"] = {
    "_comment": "Ruínas da cidade destruída na guerra (Destroyed Walls, LFA, CC BY 3.0): a cena de paredes inteira do pacote é o labirinto de ruas (Ruins_Layout, 1 unidade = 25 cm); a colisão vem dos recortes de cada parede (data/ruins_colliders.json). O guardião do cofre real espera no fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_RUINS", "player_class": "mage", "map_id": "map_ruins", "area_level": 5, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": r_rooms, "encounters": r_enc, "hazards": [],
    "entries": {"start": [0, 3], "ruins": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_cemetery", "kind": "exit", "name_key": "PROP_TO_CEMETERY", "position": [0, -73], "to": "cemetery_01_yard", "entry": "start", "group": True},
        {"id": "ruins_chest_1", "kind": "chest", "position": [20, -50], "loot": "chest"},
        {"id": "ruins_chest_2", "kind": "chest", "position": [-22, -20], "loot": "chest"},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Ruínas: sem muro de sala (a cena de paredes já fecha as ruas), chão de terra.", "walls": [""], "floor": "Ground_Dirt", "low": "",
              "ground": [0.2, 0.18, 0.14]},
    "decor": r_decor, "passive": True,
}

# --- Cemitério --------------------------------------------------------------------------------------
cr = rng("cemetery")
c_rooms = [
    room("gate", 0, 0, 22, 12, ["north"], wall_height=0.8, torch=True),
    room("yard", 0, -26, 50, 40, ["south", "north"], wall_height=0.8),
    room("crypt", 0, -56, 24, 20, ["south"], wall_height=0.8),
]
c_enc = [
    {"id": "c_rats", "position": [-12, -18], "monsters": [{"monster": "plague_rat", "count": 5}]},
    {"id": "c_bats", "position": [12, -22], "monsters": [{"monster": "plague_bat", "count": 4}]},
    {"id": "c_toads", "position": [-14, -34], "monsters": [{"monster": "acid_toad", "count": 3}]},
    {"id": "c_scorp", "position": [14, -36], "monsters": [{"monster": "venom_scorpion", "count": 3}]},
    {"id": "c_boss", "position": [0, -60], "monsters": [{"monster": "crypt_scorpion", "count": 1}]},
]
c_decor = []
# Fileiras de túmulos (cruzes e lápides) com corredores no meio.
for row, zz in enumerate([-12, -17, -22, -31, -36, -41]):
    for col, xx in enumerate(range(-20, 21, 5)):
        if abs(xx) < 4 or (xx > 5 and row in (1,)) and cr.random() < 0.3:
            continue
        if cr.random() < 0.18:
            continue
        piece = cr.choice(["Pr_Tombstone1", "Pr_Tombstone2", "Pr_Tombstone3", "Pr_Cross1", "Pr_Cross2", "Pr_Cross3"])
        c_decor.append({"piece": piece, "position": [round(xx + cr.uniform(-0.5, 0.5), 1), round(zz + cr.uniform(-0.4, 0.4), 1)],
                        "rotation": cr.choice([0, 0, 10, -10, 180, 190]), "solid": [0.8, 0.5]})
c_decor += [{"piece": "Pr_CoveredWell", "position": [0, -26], "solid": [1.8, 1.8]}, {"piece": "Pr_Obelisk3", "position": [-22, -44], "solid": [1.4, 1.4]},
            {"piece": "Pr_Obelisk2", "position": [22, -44], "solid": [1.2, 1.2]}, {"piece": "Pr_Cross4", "position": [-6, -48], "solid": [1.2, 1.2]},
            {"piece": "Pr_Cross4", "position": [6, -48], "solid": [1.2, 1.2]}, {"piece": "Pr_BrokenPillar2", "position": [-9, -62], "solid": [1.2, 1.2]},
            {"piece": "Pr_BrokenPillar2", "position": [9, -62], "solid": [1.2, 1.2]}, {"piece": "Pr_LampPost", "position": [-3, 3], "solid": [0.6, 0.6]},
            {"piece": "Pr_LampPost", "position": [3, -8], "solid": [0.6, 0.6]}, {"piece": "Pr_Trough", "position": [-16, -26], "rotation": 90, "solid": [3.0, 1.2]}]
for rd in c_rooms:
    c_decor += ring(cr, rd, ["Pr_Fence1", "Pr_Fence2"], 2.7, inset=0.7)
c_decor += scatter(cr, c_rooms[1], ["Pl_Hemp", "Pl_Bush"], 14, margin=2.0)
arenas["cemetery_01_yard"] = {
    "_comment": "Cemitério (Medieval Props Textured, Clint Bellanger, CC BY 3.0, modelos de Lamoot): fileiras de lápides e cruzes com corredores, poço coberto, obeliscos, cerca de madeira em volta e a cripta do escorpião no fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_CEMETERY", "player_class": "mage", "map_id": "map_cemetery", "area_level": 7, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": c_rooms, "encounters": c_enc, "hazards": [],
    "entries": {"start": [0, 3], "cemetery": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_fort", "kind": "exit", "name_key": "PROP_TO_DARK_FOREST", "position": [0, -62], "to": "dark_forest_01_woods", "entry": "start", "group": True},
        {"id": "cemetery_chest_1", "kind": "chest", "position": [22, -30], "loot": "chest"},
        {"id": "cemetery_chest_2", "kind": "chest", "position": [-22, -36], "loot": "chest"},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Cemitério: terra escura sem piso, cerca de madeira nas bordas (Pr_Fence1 vem de decor).", "walls": [""], "floor": "Ground_Grave", "low": "",
              "ground": [0.09, 0.09, 0.1]},
    "decor": c_decor, "passive": True,
}

# --- Floresta Escura (entre o Cemitério e o Forte) -----------------------------------------------------
dr = rng("dark_forest")
d_rooms = [
    room("edge", 0, 0, 22, 12, ["north"], wall_height=0.8, torch=True),
    room("thicket", 0, -22, 40, 32, ["south", "north", "west"], wall_height=0.8),
    room("hollow", -26, -22, 12, 20, ["east"], wall_height=0.8),
    room("roots", 0, -52, 30, 28, ["south", "north"], wall_height=0.8),
    room("elder", 0, -82, 36, 32, ["south"], wall_height=0.8),
]
d_enc = []  # por enquanto só o mapa: sem monstros, chefe nem baús
d_decor = []
for rd in d_rooms:
    d_decor += ring(dr, rd, ["Pl_Bamboo", "Pl_Bamboo", "Pl_Bamboo", "Pl_Swirl"], 1.8, scale=(1.1, 1.8))
    d_decor += scatter(dr, rd, ["Pl_Bush", "Pl_Swirl", "Pl_Hemp", "Pl_Bamboo"], int(rd["size"][0] * rd["size"][1] / 14), margin=2.0, avoid=[(0, 3, 3)])
d_decor += [{"piece": "Pr_Obelisk3", "position": [0, -92], "solid": [1.4, 1.4]}, {"piece": "Pr_Obelisk2", "position": [-7, -90], "solid": [1.0, 1.0]},
            {"piece": "Pr_Obelisk2", "position": [7, -90], "solid": [1.0, 1.0]}, {"piece": "Pr_Cross3", "position": [-26, -26], "solid": [1.0, 1.0]},
            {"piece": "Pr_Cross2", "position": [-24, -18], "solid": [1.0, 1.0]}, {"piece": "Pr_BrokenPillar1", "position": [-10, -60], "solid": [1.2, 1.2]},
            {"piece": "Pr_BrokenPillar2", "position": [10, -46], "solid": [1.2, 1.2]}, {"piece": "Pr_LampPost", "position": [-4, 3], "solid": [0.6, 0.6]}]
arenas["dark_forest_01_woods"] = {
    "_comment": "Floresta Escura (entre o Cemitério e o Forte): a mesma vegetação da Floresta (Stylish Plants), mas mais densa, mais escura e com cruzes esquecidas; uma clareira lateral e o bosque do fundo, por enquanto vazios: só o mapa, sem monstros, chefe nem baús. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_DARK_FOREST", "player_class": "mage", "map_id": "map_dark_forest", "area_level": 8, "outdoor": True,
    "wake_radius": 10.0, "alert_radius": 5.0, "rooms": d_rooms, "encounters": d_enc, "hazards": [],
    "entries": {"start": [0, 3], "dark_forest": [0, 3]},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [-6, 3], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "to_fort", "kind": "exit", "name_key": "PROP_TO_FORT", "position": [0, -95], "to": "fort_01_gate", "entry": "start", "group": True},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Floresta Escura: grama escura, cerca viva densa, tom azulado.", "walls": [""], "floor": "Ground_Grass", "low": "Pl_Bush",
              "ground": [0.05, 0.1, 0.06], "tint": [0.45, 0.55, 0.6]},
    "decor": d_decor, "passive": True,
}

# --- Forte (3D Dungeon Tileset, grade de 2,5 m) -------------------------------------------------------
import os
COLS, ROWS, CELL = 20, 26, 2.5
grid = [["#"] * COLS for _ in range(ROWS)]


def carve(c0, r0, c1, r1, ch="."):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            grid[r][c] = ch


carve(2, 1, 17, 6)      # salão do comandante
carve(8, 7, 11, 9)      # corredor
carve(1, 10, 18, 15)    # salão do meio
carve(3, 16, 4, 17); carve(15, 16, 16, 17)   # dois acessos
carve(1, 18, 7, 20); carve(12, 18, 18, 20)   # celas laterais
carve(3, 21, 4, 21); carve(15, 21, 16, 21)
carve(3, 22, 16, 24)    # pátio de entrada
for r, c in ((12, 5), (12, 14), (13, 5), (13, 14), (3, 6), (3, 13), (4, 6), (4, 13), (23, 9), (23, 10)):
    grid[r][c] = "#"


def is_rock(c, r):
    return c < 0 or r < 0 or c >= COLS or r >= ROWS or grid[r][c] == "#"


def cell_pos(c, r):
    return [round((c - COLS / 2 + 0.5) * CELL, 2), round((r - ROWS / 2 + 0.5) * CELL, 2)]


fort_decor = []
available = set(f[5:13] for f in os.listdir("assets/models/maps/fort") if f.startswith("Fort_") and f.endswith(".gltf") and f != "Fort_Floor.gltf")
NEIGH = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]  # N, NE, E, SE, S, SW, W, NW
for r in range(ROWS):
    for c in range(COLS):
        if grid[r][c] != "#":
            continue
        bits = [is_rock(c + dx, r + dz) for dx, dz in NEIGH]
        for i in (1, 3, 5, 7):  # canto só conta se os dois lados vizinhos também são pedra
            bits[i] = bits[i] and bits[(i - 1) % 8] and bits[(i + 1) % 8]
        mask = "".join("1" if b else "0" for b in bits)
        if mask == "11111111" and not any(not is_rock(c + dx, r + dz) for dx in range(-2, 3) for dz in range(-2, 3)):
            continue  # pedra escondida no meio do maciço
        rotation = 0
        if mask not in available:
            # O pacote só traz uma orientação de cada peça: gira a máscara de 90 em 90 graus até achar uma que exista.
            for k in (1, 2, 3):
                turned = "".join(mask[(i - 2 * k) % 8] for i in range(8))  # máscara do tile base que, girado k vezes no sentido horário, vira `mask`
                if turned in available:
                    mask, rotation = turned, -90 * k
                    break
            else:
                mask = "11111111" if mask.count("1") > 6 else "00000000"
        entry = {"piece": "Fort_" + mask, "position": cell_pos(c, r)}
        if rotation:
            entry["rotation"] = rotation
        fort_decor.append(entry)
# Colisão: uma caixa por trecho de pedra em cada linha.
for r in range(ROWS):
    c = 0
    while c < COLS:
        if grid[r][c] == "#":
            c0 = c
            while c < COLS and grid[r][c] == "#":
                c += 1
            x0, z = cell_pos(c0, r)
            x1, _ = cell_pos(c - 1, r)
            fort_decor.append({"collider": [round(x1 - x0 + CELL, 2), CELL], "position": [round((x0 + x1) / 2, 2), z]})
        else:
            c += 1
fort_decor += [{"light": [1.0, 0.65, 0.3], "position": cell_pos(c, r), "y": 2.2, "range": 9.0, "energy": 1.4}
               for c, r in ((4, 3), (15, 3), (9, 12), (3, 19), (16, 19), (9, 23))]
fort_decor += [{"piece": "Pr_Cross4", "position": cell_pos(9, 2), "solid": [1.2, 1.2]}, {"piece": "Pr_BrokenPillar1", "position": cell_pos(5, 11), "solid": [1.2, 1.2]},
               {"piece": "Pr_BrokenPillar2", "position": cell_pos(14, 11), "solid": [1.2, 1.2]}]
arenas["fort_01_gate"] = {
    "_comment": "Forte (3D Dungeon Tileset, Skorpio, CC BY-SA 3.0): uma grade de 20 x 26 células de 2,5 m com pedra e piso do pacote (Fort_<máscara>, a máscara é o 8-vizinhança de pedra); a colisão é uma caixa por trecho de pedra. Pátio de entrada, duas celas, salão do meio e o salão do comandante no fundo. Gerado por tools/assets/build_maps.py.",
    "name_key": "ARENA_FORT", "player_class": "mage", "map_id": "map_fort", "area_level": 10, "final": True, "victory_key": "HUD_VICTORY_SEWERS",
    "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": [room("fort", 0, 0, COLS * CELL, ROWS * CELL, [], wall_height=0.8, torch=False)],
    "encounters": [
        {"id": "fo_cell_w", "position": cell_pos(4, 19), "monsters": [{"monster": "golden_lizard", "count": 3}]},
        {"id": "fo_cell_e", "position": cell_pos(15, 19), "monsters": [{"monster": "venom_scorpion", "count": 3}]},
        {"id": "fo_hall_a", "position": cell_pos(9, 13), "monsters": [{"monster": "plague_bat", "count": 4}]},
        {"id": "fo_hall_b", "position": cell_pos(14, 14), "monsters": [{"monster": "mutant_rat", "count": 4}]},
        {"id": "fo_commander", "position": cell_pos(9, 3), "monsters": [{"monster": "fort_commander", "count": 1}]},
    ],
    "hazards": [], "entries": {"start": cell_pos(9, 23)},
    "props": [
        {"id": "return_portal", "kind": "exit", "name_key": "PROP_RETURN_PORTAL", "position": [cell_pos(6, 23)[0], cell_pos(6, 23)[1]], "to": "tortuga", "entry": "forest", "expedition_end": True},
        {"id": "fort_chest_1", "kind": "chest", "position": cell_pos(2, 19), "loot": "chest"},
        {"id": "fort_chest_2", "kind": "chest", "position": cell_pos(17, 19), "loot": "chest"},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Forte: piso de pedra do pacote; a pedra vem das peças Fort_* em decor.", "walls": [""], "floor": "Fort_Floor", "low": "", "ground": [0.07, 0.07, 0.08]},
    "decor": fort_decor, "passive": True,
}

json.dump(arenas, open(ARENAS, "w"), indent=2, ensure_ascii=False); open(ARENAS, "a").write("\n")
json.dump(monsters, open(MONSTERS, "w"), indent=2, ensure_ascii=False); open(MONSTERS, "a").write("\n")
print("OK", [k for k in arenas if k.split("_")[0] in ("forest", "ruins", "cemetery", "fort")])
