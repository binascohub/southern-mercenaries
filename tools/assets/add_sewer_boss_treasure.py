"""Mais tesouro no Ninho da Rainha dos Ratos, a sala do chefe do Esgoto (sewers_01_drains, sala "nest", 32 x 34 m, porta ao sul): uma segunda leva
por cima do que já havia (baús antigos, montes de ouro, as joias de add_boss_treasure.py). O grosso é um grande monte encostado na parede do fundo
(norte, atrás da Rainha), e o resto fica nos cantos e ao longo das paredes de leste e oeste; nada no meio da luta (5 m em volta da Rainha), na porta
nem perto do portal de vitória. Peças: montes e camas de ouro, pilhas e sacos de moedas, moedas soltas, pilhas de caveiras de ouro e joias
(Gold_*, Coin_*). Nada é sólido (dá para pisar), nada é baú (não parece que abre). Idempotente: as entradas antigas (marcadas com
"nest_treasure": true) são refeitas. Roda no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_sewer_boss_treasure.py   (a partir da raiz do projeto)"""
import json, math, random

ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
sewer = arenas["sewers_01_drains"]
room = next(r for r in sewer["rooms"] if r["id"] == "nest")
(cx, cz), (w, h) = room["center"], room["size"]
boss = next(e["position"] for e in sewer["encounters"] if e["id"] == "sw_queen")
door = (cx, cz + h / 2)
portal = next(p["position"] for p in sewer["props"] if p["id"] == "victory_portal")
sewer["decor"] = [d for d in sewer["decor"] if not d.get("nest_treasure")]
rng = random.Random("sewer-nest-treasure")
PILES = ["Gold_Pile_%d" % i for i in range(1, 6)]
JEWELS = ["Gold_Necklace", "Gold_Bangle", "Gold_Brooch", "Gold_Band", "Gold_Plate", "Gold_Orb", "Gold_Medallion", "Gold_Ring"]
placed = [(d["position"][0], d["position"][1], 0.7) for d in sewer["decor"]
          if "position" in d and abs(d["position"][0] - cx) < w / 2 and abs(d["position"][1] - cz) < h / 2 and "piece" in d]


def free(x, z, r):
    if abs(x - cx) > w / 2 - 1.2 or abs(z - cz) > h / 2 - 1.2:
        return False
    if math.hypot(x - boss[0], z - boss[1]) < 5.0 or math.hypot(x - door[0], z - door[1]) < 6.0 or math.hypot(x - portal[0], z - portal[1]) < 2.8:
        return False
    for d in sewer["decor"]:
        s = d.get("solid") or d.get("collider")
        if s and "position" in d and abs(d["position"][0] - x) < s[0] / 2 + r and abs(d["position"][1] - z) < s[-1] / 2 + r:
            return False
    return all(math.hypot(px - x, pz - z) >= pr + r for px, pz, pr in placed)


def put(piece, x, z, r, scale=1.0, y=None):
    if not free(x, z, r):
        return False
    d = {"piece": piece, "position": [round(x, 2), round(z, 2)], "rotation": rng.randrange(0, 360, 5), "nest_treasure": True}
    if scale != 1.0:
        d["scale"] = round(scale, 2)
    if y is not None:
        d["y"] = y
    sewer["decor"].append(d)
    placed.append((x, z, r))
    return True


def scatter(n, pieces, x0, x1, z0, z1, r, scale=(1.0, 1.0), y=None, tries=80):
    done = 0
    for _ in range(n):
        for _t in range(tries):
            if put(rng.choice(pieces), rng.uniform(x0, x1), rng.uniform(z0, z1), r, rng.uniform(*scale), y):
                done += 1
                break
    return done


north, south, west, east = cz - h / 2, cz + h / 2, cx - w / 2, cx + w / 2
n = 0
# o grande monte do fundo: camas de ouro embaixo, montes por cima, moedas e caveiras em volta
n += scatter(2, ["Gold_Bed"], west + 5, east - 5, north + 2.0, north + 4.0, 1.6, (0.45, 0.6), y=-0.3)  # leito deitado de 5 m: menor aqui
n += scatter(14, PILES, west + 3, east - 3, north + 1.4, north + 5.5, 0.9, (3.0, 4.5))  # Gold_Pile tem 0,34 m: bem maior, para ler de cima
n += scatter(5, ["Coin_Pile", "Coin_Bag"], west + 3, east - 3, north + 2.0, north + 6.5, 0.7, (1.4, 2.0))
n += scatter(3, ["Gold_SkullPile"], west + 3, east - 3, north + 1.5, north + 5.0, 0.8, (0.9, 1.2))
# os quatro cantos
for sx in (-1, 1):
    for sz in (-1, 1):
        x0, x1 = (west + 1.5, west + 5.5) if sx < 0 else (east - 5.5, east - 1.5)
        z0, z1 = (north + 1.5, north + 5.5) if sz < 0 else (south - 7.5, south - 2.5)
        n += scatter(3, PILES, x0, x1, z0, z1, 0.8, (2.6, 4.0))
        n += scatter(1, ["Gold_SkullPile"], x0, x1, z0, z1, 1.0, (0.7, 1.0))
# ao longo das paredes de leste e oeste: moedas, sacos, joias
for x0, x1 in ((west + 1.3, west + 3.5), (east - 3.5, east - 1.3)):
    n += scatter(3, ["Coin_Pile", "Coin_Bag"], x0, x1, north + 6, south - 7, 0.6, (1.3, 1.8))
    n += scatter(3, PILES, x0, x1, north + 6, south - 7, 0.7, (2.4, 3.4))
    n += scatter(4, JEWELS, x0, x1, north + 4, south - 6, 0.4, (1.3, 1.8))
# moedas soltas brilhando no chão pela sala (fora do meio da luta)
n += scatter(14, ["Coin_Gold"], west + 2, east - 2, north + 2, south - 5, 0.35, (0.45, 0.7))
open(ARENAS, "w", encoding="utf-8").write(json.dumps(arenas, indent=2, ensure_ascii=False) + "\n")
print("OK Esgoto: %d peças de tesouro a mais no Ninho da Rainha" % n)
