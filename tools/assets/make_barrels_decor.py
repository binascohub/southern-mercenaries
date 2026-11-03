"""Todos os barris dos mapas são só decoração: os barris quebráveis (data/arenas.json "breakables" com monstro `barrel`, que soltavam poção) viram peças de cenário `Barrel` no mesmo lugar,
com colisão, sem quebrar nem largar nada. Idempotente. uso: python3 tools/assets/make_barrels_decor.py   (a partir da raiz do projeto)"""
import json
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
moved = {}
for name, area in arenas.items():
    if not isinstance(area, dict) or not area.get("breakables"):
        continue
    keep, barrels = [], []
    for b in area["breakables"]:
        (barrels if b.get("monster") == "barrel" else keep).append(b)
    if not barrels:
        continue
    area["breakables"] = keep
    for i, b in enumerate(barrels):
        area["decor"].append({"piece": "Barrel", "position": list(b["position"]), "rotation": (i * 67) % 360, "solid": [0.9, 0.9]})
    moved[name] = len(barrels)
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK barris só decorativos:", moved)
