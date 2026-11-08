"""Pilhas de caveiras de ouro (Gold_SkullPile, tools/assets/build_gold_skulls.py; "A bunch of gold skull", IIAdantII, CC BY 4.0) nos cantos das
salas das Catacumbas e do Cemitério: uma pilha por sala grande (os dois lados com pelo menos MIN_SIDE metros; corredores e a entrada ficam de
fora) e duas na sala do chefe. Cada pilha vai para um canto sorteado, INSET metros para dentro das paredes, longe das peças sólidas, dos objetos
e das outras pilhas (tenta os outros cantos se não couber). Sólida (1,4 x 1,3 m). Idempotente: as antigas ("gold_skulls": true) são refeitas.
Roda no fim de tools/assets/build_maps.py.  uso: python3 tools/assets/add_gold_skulls.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
MAPS = {"catacombs_01_depths": "crypt", "cemetery_01_yard": "top"}     # mapa: sala do chefe
SKIP = {"entry", "gate"}
MIN_SIDE, INSET = 20, 2.6
arenas = json.load(open(ARENAS, encoding="utf-8"))


def blocked(arena, x, z):
    for d in arena.get("decor", []):
        s = d.get("solid") or d.get("collider")
        if not s and "piece" in d and "position" in d and not str(d["piece"]).startswith(("Floor", "Ground", "Trail_")):
            s = [1.0, 1.0]       # peça solta (ossos, velas): a pilha não vai por cima
        if s and "position" in d:
            sx, sz = s[0], s[-1]
            rot = int(d.get("rotation", 0)) % 180
            if rot == 90:
                sx, sz = sz, sx
            elif rot != 0:
                sx = sz = max(sx, sz)
            if abs(d["position"][0] - x) < sx / 2 + 0.9 and abs(d["position"][1] - z) < sz / 2 + 0.9:
                return True
    return any("position" in p and math.hypot(p["position"][0] - x, p["position"][1] - z) < 2.2 for p in arena.get("props", []))


for aid, boss_room in MAPS.items():
    arena = arenas[aid]
    arena["decor"] = [d for d in arena["decor"] if not d.get("gold_skulls")]
    rng = random.Random("gold-skulls-" + aid)
    count = 0
    for room in arena["rooms"]:
        (cx, cz), (w, h) = room["center"], room["size"]
        if room["id"] in SKIP or min(w, h) < MIN_SIDE:
            continue
        corners = [(sx, sz) for sx in (-1, 1) for sz in (-1, 1)]
        rng.shuffle(corners)
        want = 2 if room["id"] == boss_room else 1
        for sx, sz in corners:
            if want == 0:
                break
            x, z = cx + sx * (w / 2 - INSET), cz + sz * (h / 2 - INSET)
            if blocked(arena, x, z):
                continue
            arena["decor"].append({"piece": "Gold_SkullPile", "position": [round(x, 2), round(z, 2)], "rotation": rng.randrange(0, 360, 15),
                                   "scale": round(rng.uniform(0.9, 1.15), 2), "solid": [1.4, 1.3], "gold_skulls": True})
            want -= 1
            count += 1
    print(aid, count, "pilhas")
open(ARENAS, "w", encoding="utf-8").write(json.dumps(arenas, indent=2, ensure_ascii=False) + "\n")
