"""Tira as cruzes (Pr_Cross1 a Pr_Cross4) do cenário da Floresta (data/arenas.json "decor" de forest_01_path): o mapa não é um cemitério.
build_maps.py ainda as põe nas divisas dos setores, então este script roda depois dele (é chamado no fim de tools/assets/build_maps.py). Idempotente.
uso: python3 tools/assets/remove_forest_crosses.py   (a partir da raiz do projeto)"""
import json
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
before = len(forest["decor"])
forest["decor"] = [d for d in forest["decor"] if not str(d.get("piece", "")).startswith("Pr_Cross")]
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK cruzes removidas da Floresta:", before - len(forest["decor"]))
