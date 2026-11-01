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

SOUTH_WALL = {"to": None}

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
        {"id": "to_fort", "kind": "exit", "name_key": "PROP_TO_FORT", "position": [0, -62], "to": "fort_01_gate", "entry": "start", "group": True},
        {"id": "cemetery_chest_1", "kind": "chest", "position": [22, -30], "loot": "chest"},
        {"id": "cemetery_chest_2", "kind": "chest", "position": [-22, -36], "loot": "chest"},
    ],
    "quest_spots": [], "breakables": [],
    "style": {"_comment": "Cemitério: terra escura sem piso, cerca de madeira nas bordas (Pr_Fence1 vem de decor).", "walls": [""], "floor": "Ground_Grave", "low": "",
              "ground": [0.09, 0.09, 0.1]},
    "decor": c_decor, "passive": True,
}

json.dump(arenas, open(ARENAS, "w"), indent=2, ensure_ascii=False); open(ARENAS, "a").write("\n")
json.dump(monsters, open(MONSTERS, "w"), indent=2, ensure_ascii=False); open(MONSTERS, "a").write("\n")
print("OK", [k for k in arenas if k.split("_")[0] in ("forest", "ruins", "cemetery", "fort")])
