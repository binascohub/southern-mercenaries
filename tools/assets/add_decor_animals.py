"""Animais de cenário soltos (data/arenas.json "crowd"): uma lhama e um cavalo marrom andando pelos campos da Fazenda, caranguejos andando pelos cais das Docas poucos guaxinins e esquilos na Floresta, onde também voam borboletas.
Os modelos (llama_farm.glb, horse_brown.glb e crab.glb, em assets/models/characters/) são estáticos: deslizam devagar pelo caminho de ida e volta.
Idempotente; chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_decor_animals.py   (a partir da raiz do projeto)"""
import json, math, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
ROLES = ("llama", "brown_horse", "crab", "raccoon", "squirrel")


def put(area, entries):
    a = arenas[area]
    a["crowd"] = [c for c in a.get("crowd", []) if c.get("role") not in ROLES] + entries


# Fazenda: a lhama perto do poço, o cavalo marrom perto do estábulo (os cavalos de fazenda ficam a leste)
put("farm_01_fields", [
    {"role": "llama", "position": [-8.0, -17.0], "rotation": 40, "pose": "idle", "path": [-4.5, -20.5], "speed": 0.45},
    {"role": "llama", "position": [-14.0, -52.0], "rotation": 90, "pose": "walk", "path": [-6.5, -50.5], "speed": 0.5},
    {"role": "brown_horse", "position": [20.0, -29.5], "rotation": 250, "pose": "idle", "path": [24.0, -31.5], "speed": 0.55}])
# Floresta: um só guaxinim, no oeste, longe dos encontros e da aldeia (nenhum na Praça da Pira nem na sala a leste dela)
put("forest_01_path", [
    {"role": "raccoon", "position": [-30.0, -36.0], "rotation": 80, "pose": "idle", "path": [-28.0, -37.5], "speed": 0.4}])
# Floresta (o "mapa da natureza"): poucos esquilos (4) e borboletas pequenas voando em círculo (decor com "swim" e "flap")
a_forest = arenas["forest_01_path"]
a_forest["crowd"] += [
    {"role": "squirrel", "position": [-12.0, -19.0], "rotation": 120, "pose": "idle", "path": [-10.5, -20.5], "speed": 0.5},
    {"role": "squirrel", "position": [22.0, -22.0], "rotation": 30, "pose": "idle", "path": [23.5, -20.0], "speed": 0.5},
    {"role": "squirrel", "position": [-34.0, -22.0], "rotation": 200, "pose": "idle", "path": [-33.0, -24.0], "speed": 0.5},
    {"role": "squirrel", "position": [6.0, -36.0], "rotation": 270, "pose": "idle", "path": [7.5, -37.0], "speed": 0.5}]
a_forest["decor"] = [d for d in a_forest["decor"] if d.get("piece") != "Butterfly_Small"]
rb = random.Random("forest-butterflies")
glades = [("village", -29, -17.5, 24, 21), ("pira", 12, -17.5, 24, 21), ("c8", -8.5, -17.5, 15, 8), ("c7", 30, -17.5, 10, 8), ("ca", -30, -33, 12, 10), ("cb", 12, -33, 12, 10)]
for gid, gx, gz, gw, gh in glades:
    for _ in range(2):
        a_forest["decor"].append({"piece": "Butterfly_Small", "position": [round(gx + rb.uniform(-gw / 2 + 3, gw / 2 - 3), 1), round(gz + rb.uniform(-gh / 2 + 3, gh / 2 - 3), 1)],
                                  "y": round(rb.uniform(1.0, 2.0), 2), "scale": 1.6, "flap": True,
                                  "swim": {"radius": round(rb.uniform(1.5, 3.5), 1), "speed": round(rb.uniform(0.9, 1.5), 2), "phase": round(rb.uniform(0, 6.28), 2)}})
# Docas: caranguejos nos cais (cruzamento e píeres), cada um com um trecho curto de ida e volta
r = random.Random("docks-crabs")
spots = [("crossing", 0, -25, 40, 8), ("west_pier", -26, -25, 12, 8), ("east_pier", 26, -25, 12, 8), ("end_pier", 0, -37, 10, 16), ("pier_main", 0, -12, 8, 14)]
crabs = []
for room, cx, cz, w, h in spots:
    for _ in range(2 if room == "crossing" else 1):
        x, z = cx + r.uniform(-w / 2 + 2.5, w / 2 - 2.5), cz + r.uniform(-h / 2 + 1.5, h / 2 - 1.5)
        ang = r.uniform(0, math.tau)
        crabs.append({"role": "crab", "position": [round(x, 1), round(z, 1)], "rotation": round(math.degrees(ang)) % 360, "pose": "walk",
                      "path": [round(x + math.cos(ang) * 2.5, 1), round(z + math.sin(ang) * 1.2, 1)], "speed": 0.5})
put("docks_01_pier", crabs)
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK animais de cenário", len(arenas["farm_01_fields"]["crowd"]), len(crabs))
