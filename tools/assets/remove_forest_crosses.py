"""Tira os assets de cemitério do cenário da Floresta (data/arenas.json "decor" de forest_01_path): cruzes e lápides (Pr_Cross*), obeliscos
(Pr_Obelisk*), pilares quebrados (Pr_BrokenPillar*) e postes de luz (Pr_LampPost) — o mapa não é um cemitério. Só a placa de estrada (Pr_RoadSign) fica.
Também tira as duas casas da aldeia (Wall_*, Corner_Exterior_*, Floor_WoodDark, Roof_*) e os troncos (o poço de pedra, o carrinho de mão e o porão da aldeia, as árvores Dead_Tree e Oak_Tree e a pilha de toras Vl_Logs): a Floresta fica só com plantas, arbustos e pedras.
build_maps.py ainda os põe (divisas dos setores, praças, covil), então este script roda depois dele (é chamado no fim de tools/assets/build_maps.py). Idempotente.
uso: python3 tools/assets/remove_forest_crosses.py   (a partir da raiz do projeto)"""
import json
ARENAS = "data/arenas.json"
KEEP = {"Pr_RoadSign"}
TRUNKS = {"Dead_Tree", "Oak_Tree", "Vl_Logs", "Well_Covered", "Wheelbarrow", "Vl_Cellar", "Vl_Ladder", "Cart_Wood", "Vl_Outhouse"}   # (e o poço de pedra, o carrinho de mão, o porão e a escada das casas da aldeia, a carroça e a casinha)
HOUSE = ("Wall_", "Corner_Exterior_", "Floor_WoodDark", "Roof_", "Mushroom_")   # (e os cogumelos)
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
before = len(forest["decor"])
forest["decor"] = [d for d in forest["decor"] if d.get("piece") not in TRUNKS and not str(d.get("piece", "")).startswith(HOUSE)
                   and (not str(d.get("piece", "")).startswith("Pr_") or d.get("piece") in KEEP)]
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK assets de cemitério, troncos e casas removidos da Floresta:", before - len(forest["decor"]))
