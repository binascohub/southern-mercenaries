"""Lagoa na sala dos sapos da Floresta (a Praça da Pira, sala "pira": os sapos foram para lá na troca com a Guardiã, swap_forest_keeper.py): tira as pedras da sala e
põe a lagoa no centro da praça (duas elipses de água sobrepostas, adereço "water" com "round": true; a trilha leste-oeste, z = -17,5, termina na margem), com o cenário
solto de dentro dela (inclusive as lajes do piso) limpo. Roda depois de move_forest_village.py (é chamado no fim de tools/assets/build_maps.py). Idempotente.
uso: python3 tools/assets/add_forest_pond.py   (a partir da raiz do projeto)"""
import json
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
room = next(r for r in forest["rooms"] if r["id"] == "pira")
cx, cz = room["center"]
hw, hd = room["size"][0] / 2, room["size"][1] / 2
PONDS = [("toad_pond", [cx, cz], [12.0, 6.5]), ("toad_pond_b", [cx + 4.5, cz - 1.2], [6.0, 4.0])]


def in_ellipse(pt, at, size, extra=0.6):
    return ((pt[0] - at[0]) / (size[0] / 2 + extra)) ** 2 + ((pt[1] - at[1]) / (size[1] / 2 + extra)) ** 2 < 1.0


def in_room(pt):
    return abs(pt[0] - cx) <= hw and abs(pt[1] - cz) <= hd


before = len(forest["decor"])
forest["decor"] = [d for d in forest["decor"]
                   if not (in_room(d["position"]) and (str(d.get("piece", "")).startswith("Rock")
                                                      or any(in_ellipse(d["position"], at, size) for _, at, size in PONDS)))]
forest["props"] = [p for p in forest["props"] if not p["id"].startswith("toad_pond")]
for pid, at, size in PONDS:
    forest["props"].append({"id": pid, "kind": "water", "position": [round(at[0], 1), round(at[1], 1)], "size": size, "round": True, "color": [0.12, 0.3, 0.3]})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK lagoa em", room["center"], "- cenário removido:", before - len(forest["decor"]))
