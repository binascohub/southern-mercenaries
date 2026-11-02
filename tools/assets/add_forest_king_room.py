"""Amplia a sala do Rei Golem da Floresta (a sala "reptiles" depois da troca de move_forest_village.py, a do canto direito-baixo, x de 72 a 96, z de -45 a -9):
mais 16 m de largura para a direita (leste) e mais 20 m para cima (norte, z menor), com a parede de arbustos nos novos limites e as mesmas plantas nos trechos novos.
A porta (oeste) continua em z = -27, alinhada com o corredor (o deslocamento dela em relação ao centro da sala é refeito).
Roda antes de add_forest_temple.py e add_forest_trees.py (é chamado no fim de tools/assets/build_maps.py). Idempotente: se a sala já tem o tamanho novo, não faz nada.
uso: python3 tools/assets/add_forest_king_room.py   (a partir da raiz do projeto)"""
import json, random
ARENAS = "data/arenas.json"
EXTRA = 16.0
EXTRA_N = 20.0
DOOR_Z = -27.0
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
room = next(r for r in forest["rooms"] if r["id"] == "reptiles")
if room["size"][0] >= 24 + EXTRA - 1e-6 and room["size"][1] >= 36 + EXTRA_N - 1e-6:
    print("OK sala do Rei Golem já ampliada")
    raise SystemExit
x0 = room["center"][0] - room["size"][0] / 2
x1 = room["center"][0] + room["size"][0] / 2
z0 = room["center"][1] - room["size"][1] / 2
z1 = room["center"][1] + room["size"][1] / 2
w, h = room["size"]
room["size"] = [round(w + EXTRA, 2), round(h + EXTRA_N, 2)]
room["center"] = [round(room["center"][0] + EXTRA / 2, 2), round(room["center"][1] - EXTRA_N / 2, 2)]
off = DOOR_Z - room["center"][1]
room["doors"] = ["west:%g" % off if abs(off) > 1e-6 else "west"]
rng = random.Random("forest-king-room")
PIECES = ["Pl_Bamboo"] * 14 + ["Pl_Bush"] * 10 + ["Pl_Weed1", "Pl_Weed2", "Pl_Weed3", "Pl_Weed4", "Pl_Weed5"] * 6 + ["Pl_Hemp"] * 4 + ["Pl_Flower"] * 3 + \
    ["Pl_Shrub1", "Pl_Shrub2", "Pl_Shrub3", "Pl_Shrub4", "Pl_Shrub5"] * 2
strips = [(x1 + 0.5, x1 + EXTRA - 0.5, z0 + 1.0, z1 - 1.0), (x0 + 1.0, x1 - 0.5, z0 - EXTRA_N + 0.5, z0 - 0.5)]   # a faixa leste e a faixa norte
count = 0
for sx0, sx1, sz0, sz1 in strips:
    for i in range(round((sx1 - sx0) * (sz1 - sz0) * 0.18)):
        forest["decor"].append({"piece": PIECES[count % len(PIECES)], "position": [round(rng.uniform(sx0, sx1), 1), round(rng.uniform(sz0, sz1), 1)],
                                "rotation": rng.randrange(360), "scale": round(rng.uniform(0.9, 1.4), 2)})
        count += 1
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK sala do Rei Golem ampliada para", room["size"], "centro", room["center"], "porta", room["doors"], "- plantas novas:", count)
