"""Amplia para a direita (leste) a sala do Rei Golem da Floresta (a sala "reptiles" depois da troca de move_forest_village.py, a do canto direito-baixo, x de 72 a 96):
mais 16 m de largura, com a parede de arbustos no novo limite e as mesmas plantas no trecho novo. A porta (oeste) e o resto da sala não mudam.
Roda antes de add_forest_trees.py (é chamado no fim de tools/assets/build_maps.py). Idempotente: se a sala já tem a largura nova, não faz nada.
uso: python3 tools/assets/add_forest_king_room.py   (a partir da raiz do projeto)"""
import json, random
ARENAS = "data/arenas.json"
EXTRA = 16.0
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
room = next(r for r in forest["rooms"] if r["id"] == "reptiles")
if room["size"][0] >= 24 + EXTRA - 1e-6:
    print("OK sala do Rei Golem já ampliada")
    raise SystemExit
x1 = room["center"][0] + room["size"][0] / 2
cz = room["center"][1]
h = room["size"][1]
room["size"][0] = round(room["size"][0] + EXTRA, 2)
room["center"][0] = round(room["center"][0] + EXTRA / 2, 2)
rng = random.Random("forest-king-room")
PIECES = ["Pl_Bamboo"] * 14 + ["Pl_Bush"] * 10 + ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"] * 6 + ["Pl_Hemp"] * 4 + ["Pl_Flower"] * 3 + \
    ["Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3", "Pl_Shrub4", "Pl_Shrub5"] * 2
count = round(EXTRA * h * 0.18)
for i in range(count):
    piece = PIECES[i % len(PIECES)]
    forest["decor"].append({"piece": piece, "position": [round(x1 + rng.uniform(0.5, EXTRA - 0.5), 1), round(cz + rng.uniform(-h / 2 + 1.0, h / 2 - 1.0), 1)],
                            "rotation": rng.randrange(360), "scale": round(rng.uniform(0.9, 1.4), 2)})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK sala do Rei Golem ampliada para", room["size"], "centro", room["center"], "- plantas novas:", count)
