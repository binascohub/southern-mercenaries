"""Mapa do Deserto: o Cânion (desert_01_canyon), ligado à Fazenda (Canyon Terrain Asset, loafbrr / Ian87, CC0: peças de
assets/models/maps/desert/ feitas por tools/assets/build_canyon_pieces.py). Cânion de areia em salas abertas (entrada, cânion, oásis, ravina, arena),
com paredes de rocha, cactos, capim e árvores secas, 2 mini-chefes (o Lamassu da Areia e a Rainha Escorpião), baús e a bolsa de moedas. Sorteio com
semente fixa: rodar de novo reproduz o mesmo mapa. Também põe o portal "desert_gate" na Fazenda (e a entrada "desert" dela).
Idempotente; chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/build_desert.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
rng = random.Random("desert-canyon")
DOOR = 6.0


def room(rid, cx, cz, w, h, doors, **extra):
    r = {"id": rid, "center": [cx, cz], "size": [w, h], "doors": doors, "wall_height": 0.8}
    r.update(extra)
    return r


rooms = [room("start", 0, 0, 30, 14, ["north"], torch=True), room("canyon_a", 0, -22, 34, 30, ["south", "north", "east"]),
         room("oasis", 30, -22, 26, 16, ["west"]), room("canyon_b", 0, -56, 38, 38, ["south", "north", "west"]),
         room("ravine", -30, -56, 22, 18, ["east"]), room("arena", 0, -94, 48, 38, ["south"])]
# Paredes de rocha: (largura aproximada, peças altas para norte/leste/oeste e baixas para o sul, que fica de frente para a câmera)
TALL = {"Rock_Formations_3": 13.5, "Rock_Formations_4": 6.7, "Rock_Formations_5": 16.9, "Rock_Formations_6": 3.8, "Rock_Formations_7": 10.4,
        "Rock_Formations_8": 9.0, "Rock_Formations_9": 8.0, "Rock_Formations_10": 8.5, "Rock_Formations_12": 7.0,
        "Rock_Platforms_5": 12.0, "Rock_Platforms_7": 21.0, "Rock_Platforms_9": 21.0, "Rock_Platforms_10": 18.0}
LOW = {"Rock_Boulders_1": 2.4, "Rock_Boulders_4": 4.0, "Rock_Boulders_5": 2.4, "Rock_Boulders_6": 1.9, "Rock_Platforms_1": 4.6, "Rock_Platforms_4": 5.2,
       "Rock_Platforms_6": 5.4, "Rock_Formations_1": 6.3, "Rock_Formations_2": 4.8}


def inside_any(x, z, pad=0.5):
    return any(abs(x - r["center"][0]) < r["size"][0] / 2 + pad and abs(z - r["center"][1]) < r["size"][1] / 2 + pad for r in rooms)


decor = []
for r in rooms:
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
            # vão das portas
            door_off = next((float(d.split(":")[1]) if ":" in d else 0.0 for d in r["doors"] if d.split(":")[0] == side), None)
            if door_off is not None and abs(mid - door_off) < DOOR / 2 + w / 2:
                continue
            depth = 2.0 + w * 0.22
            if side == "north":
                x, z, rot = cx + mid, cz - hh - depth, 0
            elif side == "south":
                x, z, rot = cx + mid, cz + hh + depth, 180
            elif side == "east":
                x, z, rot = cx + hw + depth, cz + mid, 270
            else:
                x, z, rot = cx - hw - depth, cz + mid, 90
            if inside_any(x, z, 0.0):
                continue
            decor.append({"piece": "Canyon_" + name, "position": [round(x, 1), round(z, 1)], "rotation": rot + rng.choice((0, 15, -15))})
# Dentro das salas: pedregulhos com colisão, cactos, capim, árvores secas, galhos e folhas
INTERIOR = {"cactus": (["Canyon_Cactus_Tall_%d" % i for i in range(1, 6)] + ["Canyon_Cactus_Small_%d" % i for i in range(1, 6)] + ["Canyon_Cactus_Flat_%d" % i for i in range(1, 4)], 0.012),
            "grass": (["Canyon_Grass_1", "Canyon_Grass_6", "Canyon_Grass_10", "Canyon_Sticks_1", "Canyon_Sticks_2", "Canyon_Leafs_1"], 0.02),
            "tree": (["Canyon_Tree_%d" % i for i in range(1, 5)], 0.003)}
BOULDERS = {"Canyon_Rock_Boulders_%d" % i: s for i, s in ((1, 2.0), (2, 2.2), (3, 2.2), (4, 3.4), (5, 2.0), (6, 1.6))}
for r in rooms:
    cx, cz = r["center"]
    w, h = r["size"]
    area = w * h
    for _ in range(max(2, round(area / 150))):  # pedregulhos (colisão)
        for _try in range(20):
            x, z = cx + rng.uniform(-w / 2 + 3.5, w / 2 - 3.5), cz + rng.uniform(-h / 2 + 3.5, h / 2 - 3.5)
            if abs(x - cx) < 4.5 and r["id"] in ("start",):
                continue
            name = rng.choice(list(BOULDERS))
            decor.append({"piece": name, "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15), "solid": [round(BOULDERS[name] * 0.8, 1)] * 2})
            break
    for kind, (pieces, density) in INTERIOR.items():
        for _ in range(round(area * density)):
            x, z = cx + rng.uniform(-w / 2 + 1.5, w / 2 - 1.5), cz + rng.uniform(-h / 2 + 1.5, h / 2 - 1.5)
            if r["id"] == "start" and abs(x) < 5 and abs(z - 3) < 4:
                continue  # a chegada fica livre
            d = {"piece": rng.choice(pieces), "position": [round(x, 1), round(z, 1)], "rotation": rng.randrange(0, 360, 15)}
            if kind != "grass":
                d["scale"] = round(rng.uniform(0.9, 1.4), 2)
            decor.append(d)
encounters = [
    ("d_scorp_a", [-8, -18], [("venom_scorpion", 3)]), ("d_chitin_a", [8, -26], [("chitin_beast", 2)]), ("d_stalker_a", [0, -32], [("stalker", 2)]),
    ("d_oasis", [30, -20], [("venom_scorpion", 2), ("chitin_beast", 1)]),
    ("d_scorp_b", [-8, -48], [("venom_scorpion", 3)]), ("d_goblin_b", [10, -52], [("goblin", 4), ("stalker", 1)]), ("d_ravine", [-30, -56], [("troll", 1)]),
    ("d_lamassu", [0, -68], [("sand_lamassu", 1)]),
    ("d_arena_a", [-12, -88], [("chitin_beast", 3)]), ("d_arena_b", [12, -90], [("stalker", 2), ("venom_scorpion", 2)]), ("d_queen", [0, -104], [("queen_scorpion", 1)])]
arenas["desert_01_canyon"] = {
    "_comment": "Deserto — o Cânion (Canyon Terrain Asset, loafbrr / Ian87, CC0): areia e rocha em salas abertas (entrada, cânion, oásis, ravina e arena), com cactos, capim e árvores secas; "
                "2 mini-chefes (Lamassu da Areia e Rainha Escorpião). Liga-se à Fazenda pelo portal do oeste dos campos. Gerado por tools/assets/build_desert.py.",
    "name_key": "ARENA_DESERT", "outdoor": True, "player_class": "mage", "map_id": "map_desert", "area_level": 7, "wake_radius": 10.0, "alert_radius": 5.0,
    "rooms": rooms, "encounters": [{"id": i, "position": p, "monsters": [{"monster": m, "count": c} for m, c in mons]} for i, p, mons in encounters], "hazards": [],
    "entries": {"start": [0, 3], "desert": [0, 3]},
    "props": [{"id": "return_portal", "kind": "exit", "name_key": "PROP_TO_FARM", "position": [-6, 3], "to": "farm_01_fields", "entry": "desert"},
              {"id": "desert_chest_1", "kind": "chest", "position": [38, -26], "loot": "chest"}, {"id": "desert_chest_2", "kind": "chest", "position": [-37, -59], "loot": "chest"},
              {"id": "desert_chest_3", "kind": "chest", "position": [18, -106], "loot": "chest"}, {"id": "desert_chest_4", "kind": "chest", "position": [-18, -106], "loot": "chest"}],
    "quest_spots": [], "breakables": [{"id": "coin_bag", "monster": "coin_bag", "position": [4.0, 1.5], "table": "coin_bag"}],
    "style": {"_comment": "Cânion: chão de areia (Ground_Canyon), sem muro do kit; as paredes são as formações de rocha (decor).", "walls": [""], "floor": "Ground_Canyon", "low": "",
              "ground": [0.5, 0.36, 0.22]},
    "decor": decor, "passive": True}
# Fazenda: portal para o Deserto no oeste dos campos
farm = arenas["farm_01_fields"]
farm["props"] = [p for p in farm["props"] if p["id"] != "desert_gate"] + [
    {"id": "desert_gate", "kind": "exit", "name_key": "PROP_TO_DESERT", "position": [-24, -14], "to": "desert_01_canyon", "entry": "start"}]
farm["entries"]["desert"] = [-22.0, -17.0]
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK desert", len(decor), "peças de cenário,", len(encounters), "encontros")
