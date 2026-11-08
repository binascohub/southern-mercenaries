"""Fogueira no centro do acampamento da Floresta (sala "village", (-28, -49)): o fogo de lenha da taverna (Tv_Fire, a lenha e as brasas) com a chama da página Fire (Fire_Flame, janexx, CC BY-SA 3.0, animada por código), um círculo de pedras musgosas
(Rock_MossyStone, Mossy Stone Rock, mastahcez, CC0), algumas toras (Tv_Firewood) e uma luz quente de cenário. Limpa as plantas e pedras soltas em volta. Roda depois de move_forest_village.py
(é chamado no fim de tools/assets/build_maps.py). Idempotente: a fogueira antiga (marcada com "camp": true) é refeita.
uso: python3 tools/assets/add_forest_campfire.py   (a partir da raiz do projeto)"""
import json, math
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
room = next(r for r in forest["rooms"] if r["id"] == "village")
cx, cz = room["center"]
decor = [d for d in forest["decor"] if not d.get("camp")]
decor = [d for d in decor if str(d.get("piece", "")).startswith("Trail_") or math.hypot(d["position"][0] - cx, d["position"][1] - cz) > 2.8]
fire = [{"piece": "Bonfire_Cauldron", "position": [cx, cz], "rotation": 0, "solid": [1.2, 2.2], "camp": True},   # fogueira com caldeirão (tools/assets/build_bonfire.py)
        {"light": [1.0, 0.5, 0.18], "position": [cx, cz], "y": 0.9, "range": 11.0, "energy": 1.6, "flicker": True, "camp": True},
        {"piece": "Fire_Flame", "position": [cx, cz], "y": 0.1, "scale": 0.9, "flicker": True, "camp": True}]   # a chama (Fire, janexx, CC BY-SA 3.0) sobre as brasas
for i in range(9):
    a = i * 2 * math.pi / 9
    fire.append({"piece": "Rock_MossyStone", "position": [round(cx + 1.0 * math.cos(a), 2), round(cz + 1.0 * math.sin(a), 2)],
                 "rotation": i * 40, "scale": round(0.5 + 0.08 * (i % 3), 2), "camp": True})
for i, (dx, dz, rot) in enumerate(((1.9, 0.9, 80), (-1.8, 1.2, 15), (0.4, -2.0, 120))):
    fire.append({"piece": "Tv_Firewood", "position": [round(cx + dx, 2), round(cz + dz, 2)], "rotation": rot, "camp": True})
fire.append({"piece": "Vl_TanningStand", "position": [-27.5, -58.7], "solid": [2.2, 0.5], "camp": True})   # mais uma pele de animal (o varal de couro da Elara)
decor = [d for d in decor if str(d.get("piece", "")).startswith("Trail_") or math.hypot(d["position"][0] + 27.5, d["position"][1] + 58.7) > 1.8]
forest["decor"] = decor + fire
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK fogueira em", [cx, cz])
