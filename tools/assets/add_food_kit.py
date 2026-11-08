"""Comidas do Food Kit da Kenney (CC0; tools/assets/import_food_kit.py) nas cidades:
  - Capital Real: a mesa da fartura do rei (as duas mesas grandes da sala do trono, com peru, pernil, costelas, tortas, bolo, pães, queijos,
    uvas, frutas, vinho e pratos; saem as frutas soltas e os frascos de poção de antes), uma barraca de feira de comida na praça do portão e a
    mesa da avenida com mais variedade;
  - Tortuga: uma barraca de feira na Rua Principal (peixe, mexilhões, frutas da ilha, pães) e o carrinho de mão com peixe e cocos;
  - Fazenda: as quatro carroças carregadas (abóboras, repolhos, milho e legumes; maçãs e peras; sacos de farinha e pães no moinho).
As alturas dos fundos das carroças, das mesas e da barraca foram medidas no jogo (raio de cima nas peças). Cada comida tem um tamanho de
verdade (escala calculada pelo tamanho do modelo) e é espalhada sem sobrepor (semente fixa). Idempotente: apaga as peças "food_kit" antes.
uso: python3 tools/assets/add_food_kit.py   (a partir da raiz do projeto)"""
import json, math, os, random, struct

ARENAS = "data/arenas.json"
FOOD = "assets/models/food"


def piece(model):
    return "Fk_" + "_".join(part.capitalize() for part in model.split("-"))


def glb_size(path):
    """Largura (x), altura (y) e fundo (z) do modelo, pelos limites das malhas (os modelos da Kenney não têm nós girados)."""
    data = open(path, "rb").read()
    length = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + length])
    lo, hi = [1e9] * 3, [-1e9] * 3
    for node in gltf["nodes"]:
        if "mesh" not in node:
            continue
        s = node.get("scale", [1, 1, 1])
        t = node.get("translation", [0, 0, 0])
        for prim in gltf["meshes"][node["mesh"]]["primitives"]:
            acc = gltf["accessors"][prim["attributes"]["POSITION"]]
            for i in range(3):
                lo[i] = min(lo[i], acc["min"][i] * s[i] + t[i])
                hi[i] = max(hi[i], acc["max"][i] * s[i] + t[i])
    return [hi[i] - lo[i] for i in range(3)]


SIZES = {}


def scale_of(model, target):
    if model not in SIZES:
        SIZES[model] = glb_size(os.path.join(FOOD, piece(model) + ".glb"))
    return target / max(SIZES[model])


def footprint(model, target):
    sx, _, sz = SIZES[model]
    k = scale_of(model, target)
    return max(sx, sz) * k * 0.5


arenas = json.load(open(ARENAS, encoding="utf-8"))
rng = random.Random(20261108)


def to_world(cx, cz, rot, lx, lz):
    a = math.radians(rot)
    return cx + lx * math.cos(a) + lz * math.sin(a), cz - lx * math.sin(a) + lz * math.cos(a)


def fill(area, center, rot, rect, y, items, blocked=(), layers=1, tries=300, slope=None):
    """Espalha `items` ([(modelo, tamanho em m, quantos)]) no retângulo local `rect` (x0, x1, z0, z1) de uma superfície à altura `y`,
    girada `rot` graus em volta de `center`. `blocked`: círculos locais (x, z, raio) já ocupados. `slope`: (z0, y0, z1, y1), fundo inclinado."""
    decor = arenas[area]["decor"]
    placed = [tuple(b) for b in blocked]
    added = 0
    for layer in range(layers):
        taken = list(placed) if layer == 0 else []
        for model, target, count in items:
            k = scale_of(model, target)
            r = footprint(model, target)
            for _ in range(count):
                for _try in range(tries):
                    lx = rng.uniform(rect[0] + r, rect[1] - r)
                    lz = rng.uniform(rect[2] + r, rect[3] - r)
                    if all(math.hypot(lx - bx, lz - bz) >= r + br + 0.01 for bx, bz, br in taken):
                        break
                else:
                    continue
                taken.append((lx, lz, r))
                h = y
                if slope:
                    z0, y0, z1, y1 = slope
                    h = y0 + (y1 - y0) * (lz - z0) / (z1 - z0)
                h += layer * SIZES[model][1] * k * 0.55
                wx, wz = to_world(center[0], center[1], rot, lx, lz)
                decor.append({"piece": piece(model), "position": [round(wx, 3), round(wz, 3)], "y": round(h, 3),
                              "rotation": rng.randrange(360), "scale": round(k, 3), "food_kit": True})
                added += 1
    return added


for a in arenas.values():
    if isinstance(a, dict) and "decor" in a:
        a["decor"] = [d for d in a["decor"] if not d.get("food_kit")]

count = {}
# ---------------------------------------------------------------- Capital Real
CAP = "capital_01_aurenhold"
cap = arenas[CAP]
TABLE = (-1.35, 1.35, -0.45, 0.45)
TABLE_Y = 0.81
KING_TABLES = [(0.0, -61.0), (0.0, -58.2)]
# A mesa do rei antes: frutas soltas, frascos de poção, garrafas e taças em cima das duas mesas. Ficam os castiçais; o resto vira o banquete.
cap["decor"] = [d for d in cap["decor"]
                if not (d.get("y") == 0.9 and d.get("piece", "") != "CandleStick_Triple"
                        and any(abs(d["position"][0] - tx) < 1.5 and abs(d["position"][1] - tz) < 0.6 for tx, tz in KING_TABLES))]
candles = [(-0.8, 0.0, 0.2), (0.8, 0.0, 0.2)]
n = 0
for i, (tx, tz) in enumerate(KING_TABLES):
    centerpiece = ("turkey", 0.55) if i == 0 else ("whole-ham", 0.5)
    blocked = candles if i == 0 else []
    # A peça do meio fica no centro da mesa (os castiçais da primeira mesa estão a 0,8 m para cada lado).
    k = scale_of(*centerpiece)
    cap["decor"].append({"piece": piece(centerpiece[0]), "position": [tx, tz], "y": TABLE_Y, "rotation": 90 * i,
                         "scale": round(k, 3), "food_kit": True})
    n += 1
    feast = [("meat-ribs", 0.38, 1), ("pie", 0.32, 1), ("cake", 0.32, 1) if i == 0 else ("mincemeat-pie", 0.26, 2),
             ("loaf-round", 0.28, 1), ("loaf-baguette", 0.5, 1), ("cheese", 0.3, 1), ("cheese-cut", 0.18, 1), ("grapes", 0.22, 2),
             ("wine-red", 0.32, 2), ("wine-white", 0.32, 1), ("glass-wine", 0.17, 4), ("plate-dinner", 0.28, 3), ("pear", 0.15, 2),
             ("apple", 0.15, 3), ("orange", 0.15, 2), ("honey", 0.14, 1), ("meat-sausage", 0.28, 1)]
    middle = [(0.0, 0.0, footprint(*centerpiece))]
    n += fill(CAP, (tx, tz), 0, TABLE, TABLE_Y, feast, blocked=middle + blocked)
count["mesa do rei"] = n
# Barraca de comida na praça do portão, entre a forja (x = 4) e a barraca do Macumbeiro (x = 16), de frente para a rua.
STALL = (11.8, -4.5)
cap["decor"].append({"stall": "awning_yellow", "piece": "Market_Stall", "position": list(STALL), "rotation": 0, "solid": [3.8, 2.2], "food_kit": True})
COUNTER = (-1.8, 1.8, 0.47, 1.17)
SHELF = (-1.65, 1.65, -1.0, -0.68)
n = fill(CAP, STALL, 0, COUNTER, 0.995, [("pumpkin-basic", 0.32, 2), ("cabbage", 0.26, 3), ("cauliflower", 0.22, 2), ("carrot", 0.22, 5),
                                           ("leek", 0.4, 3), ("onion", 0.11, 6), ("beet", 0.12, 4), ("eggplant", 0.2, 2), ("paprika", 0.12, 4)])
n += fill(CAP, STALL, 0, SHELF, 0.925, [("apple", 0.15, 8), ("pear", 0.15, 6), ("orange", 0.14, 5), ("lemon", 0.12, 4)])
n += fill(CAP, STALL, 0, SHELF, 1.475, [("loaf", 0.32, 2), ("loaf-round", 0.26, 3), ("bread", 0.24, 3), ("cheese", 0.28, 2), ("cheese-cut", 0.16, 2)])
n += fill(CAP, STALL, 0, SHELF, 2.025, [("honey", 0.15, 3), ("wine-red", 0.3, 3), ("wine-white", 0.3, 2), ("mug", 0.13, 3)])
count["barraca da Capital"] = n
# Mesa da avenida (x = 14, z = -14.5): já tem frutas e carne; ganha legumes, pão e queijo no que sobra.
avenue = (14.0, -14.5)
taken = [(d["position"][0] - avenue[0], d["position"][1] - avenue[1], 0.16) for d in cap["decor"]
         if d.get("y") == 0.9 and abs(d["position"][0] - avenue[0]) < 1.5 and abs(d["position"][1] - avenue[1]) < 0.6]
count["mesa da avenida"] = fill(CAP, avenue, 0, TABLE, TABLE_Y, [("cabbage", 0.24, 2), ("loaf-round", 0.26, 1), ("cheese", 0.26, 1), ("grapes", 0.2, 2),
                                                                ("pear", 0.15, 3), ("carrot", 0.22, 3), ("onion", 0.11, 3)], blocked=taken)
# ---------------------------------------------------------------- Tortuga
TOR = "tortuga"
STALL_T = (-18.0, -6.6)
arenas[TOR]["decor"].append({"stall": "tent_teal", "piece": "Market_Stall", "position": list(STALL_T), "rotation": 0, "solid": [3.8, 2.2], "food_kit": True})
OPEN_TABLE = (-1.5, 1.5, 0.1, 1.0)   # as barracas abertas (sem balcão) têm uma mesa baixa na frente, a 0,455 m
n = fill(TOR, STALL_T, 0, OPEN_TABLE, 0.455, [("fish", 0.42, 6), ("mussel", 0.08, 10), ("bowl", 0.22, 1)])
n += fill(TOR, STALL_T, 0, SHELF, 0.925, [("pineapple", 0.32, 3), ("coconut", 0.18, 4), ("coconut-half", 0.17, 2), ("banana", 0.24, 4), ("orange", 0.14, 4)])
n += fill(TOR, STALL_T, 0, SHELF, 1.475, [("loaf", 0.32, 2), ("bread", 0.24, 3), ("lemon", 0.12, 5)])
n += fill(TOR, STALL_T, 0, SHELF, 2.025, [("wine-red", 0.3, 4), ("mug", 0.13, 4)])
count["barraca de Tortuga"] = n
# Carrinho de mão da rua (Cart_Wood, x = -23, z = 7, girado 15 graus): fundo a 0,58 m.
count["carrinho de Tortuga"] = fill(TOR, (-23.0, 7.0), 15, (-1.05, -0.1, -0.22, 0.22), 0.58,
                                    [("fish", 0.4, 3), ("coconut", 0.18, 3), ("banana", 0.24, 2)], layers=2)
# ---------------------------------------------------------------- Fazenda
FARM = "farm_01_fields"
n = fill(FARM, (-22.5, -23.5), 20, (-0.3, 1.4, -0.5, 0.5), 1.14,
         [("pumpkin-basic", 0.4, 4), ("cabbage", 0.28, 5), ("corn", 0.3, 5), ("carrot", 0.24, 6), ("beet", 0.13, 5)], layers=2)
n += fill(FARM, (5.5, -2.8), 100, (-0.2, 0.95, -0.45, -0.05), 0.90, [("apple", 0.15, 10), ("pear", 0.15, 6)], layers=2)
n += fill(FARM, (57.0, -30.0), 300, (-0.2, 0.95, -0.45, -0.05), 0.90, [("bag", 0.42, 2), ("bag-flat", 0.4, 1), ("loaf", 0.3, 1)])
n += fill(FARM, (-18.0, -13.5), 70, (-0.2, 0.95, -0.45, -0.05), 0.90,
          [("cabbage", 0.26, 2), ("leek", 0.4, 2), ("onion", 0.11, 5), ("carrot", 0.22, 4), ("radish", 0.12, 4)], layers=2)
count["carroças da Fazenda"] = n

json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK comidas:", ", ".join("%s %d" % kv for kv in count.items()))
