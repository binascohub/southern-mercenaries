"""A Guardiã da Pira (forest_pyre_keeper, com o Golem de Fogo que ela invoca) e os sapos trocam de lugar na Floresta: a Guardiã vai para a sala da lagoa (a sala "bats",
a oeste da lagoa) e os quatro grupos de sapos vão para a Praça da Pira. Roda depois de move_forest_village.py e add_forest_pond.py (é chamado no fim de
tools/assets/build_maps.py). Idempotente.
uso: python3 tools/assets/swap_forest_keeper.py   (a partir da raiz do projeto)"""
import json
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
KEEPER, GOLEM = [-1.5, -47.0], [-1.5, -42.0]          # sala da lagoa, a oeste da água
TOAD_SPOTS = [[4, -11], [20, -11], [4, -24], [20, -24]]  # Praça da Pira (0..24, -28..-7), fora da trilha leste-oeste (z = -17,5)
for p in forest["props"]:
    if p["id"] == "forest_pyre_keeper":
        p["position"] = list(KEEPER)
        p["summon"]["position"] = list(GOLEM)
toads = [e for e in forest["encounters"] if e["id"].startswith("f_toads")]
for e, spot in zip(toads, TOAD_SPOTS):
    e["position"] = list(spot)
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK Guardiã da Pira em", KEEPER, "- sapos na Praça da Pira")
