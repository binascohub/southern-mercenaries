"""Peixes (3d low poly catfish, gfroad / Snabisch, CC0) nadando em círculo no riacho da Fazenda e no mar das Docas (data/arenas.json "decor",
peça Fish_Catfish com "swim": raio, velocidade e fase). Idempotente; chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_fish.py   (a partir da raiz do projeto)"""
import json, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))


def fish(x, z, radius, speed, phase, scale=1.4):
    return {"piece": "Fish_Catfish", "position": [round(x, 2), round(z, 2)], "y": -0.03, "scale": scale, "swim": {"radius": radius, "speed": speed, "phase": round(phase, 2)}}


def put(area, items):
    a = arenas[area]
    a["decor"] = [d for d in a["decor"] if d.get("piece") != "Fish_Catfish"] + items


# Riacho da Fazenda: tira de 3,6 m de largura no x do prop "creek"; cada peixe faz um círculo de 0,8 m.
creek = next(p for p in arenas["farm_01_fields"]["props"] if p["id"] == "creek")
r = random.Random("farm-fish")
cx, cz = creek["position"]
half = creek["size"][1] / 2.0
put("farm_01_fields", [fish(cx + r.uniform(-0.3, 0.3), cz - half + 5.0 + i * (creek["size"][1] - 10.0) / 6.0, 0.8, r.uniform(0.5, 0.9), r.uniform(0, 6.28)) for i in range(7)])
# Mar das Docas: peixes soltos fora das salas (cais), perto o bastante para aparecer na tela.
sea = next(p for p in arenas["docks_01_pier"]["props"] if p["id"] == "sea")
rooms = arenas["docks_01_pier"]["rooms"]
r = random.Random("docks-fish")
out = []
tries = 0
while len(out) < 16 and tries < 4000:
    tries += 1
    x = r.uniform(-48, 48)
    z = r.uniform(-60, -4)
    radius = r.uniform(1.0, 2.2)
    if any(abs(x - rm["center"][0]) < rm["size"][0] / 2 + radius + 1.0 and abs(z - rm["center"][1]) < rm["size"][1] / 2 + radius + 1.0 for rm in rooms):
        continue
    if any((x - f["position"][0]) ** 2 + (z - f["position"][1]) ** 2 < 36 for f in out):
        continue
    out.append(fish(x, z, radius, r.uniform(0.5, 1.0), r.uniform(0, 6.28), 2.2))  # no mar escuro o peixe tem de ser maior para aparecer de cima
put("docks_01_pier", out)
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK fish", len(arenas["farm_01_fields"]["decor"]), len(out))
