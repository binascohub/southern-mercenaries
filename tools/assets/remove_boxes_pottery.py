"""Remove caixas e cerâmicas (caixotes, caixas, vasos, potes, jarros) de todos os mapas em data/arenas.json:
peças de "decor" e quebráveis ("breakables"). Barris e cestos ficam. Idempotente. uso: python3 tools/assets/remove_boxes_pottery.py"""
import json, re

ARENAS = "data/arenas.json"
PIECE = re.compile(r"^(Crate_.*|Lab_Crate|Dock_Props_(Crate|Box)|Bucket_Crate|FarmCrate_Apple|Furn_Box|Pot_.*|Vase_.*|Dw_Jug)$")
BREAKABLE = {"crate", "mug"}

arenas = json.load(open(ARENAS))
removed = {}
for name, area in arenas.items():
    if not isinstance(area, dict):
        continue
    n = 0
    if isinstance(area.get("decor"), list):
        keep = [d for d in area["decor"] if not (isinstance(d, dict) and PIECE.match(str(d.get("piece", ""))))]
        n += len(area["decor"]) - len(keep)
        area["decor"] = keep
    if isinstance(area.get("breakables"), list):
        keep = [b for b in area["breakables"] if b.get("monster") not in BREAKABLE]
        n += len(area["breakables"]) - len(keep)
        area["breakables"] = keep
    if n:
        removed[name] = n
json.dump(arenas, open(ARENAS, "w"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print(removed, sum(removed.values()))
