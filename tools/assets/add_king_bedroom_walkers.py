"""Quarto do rei (Capital, sala king_bedroom, 32 x 16 m, as camas ao sul e as mesas ao norte): moças que andam de um lado a outro pelo corredor livre do
meio do quarto ("crowd" da área, papéis com modelo próprio em game/actors/npc_model.gd): Anna (anna_walker) e Adriana (adriana_walker), cada uma na sua
faixa para não se cruzarem. Só cenário (Wanderer: vai, para um pouco na ponta e volta). Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/add_king_bedroom_walkers.py   (a partir da raiz do projeto)"""
import json

ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
capital = arenas["capital_01_aurenhold"]
WALKS = [("anna_walker", [19.0, -63.8], [35.0, -63.8], 0.9), ("adriana_walker", [43.0, -62.0], [26.0, -62.0], 1.0)]
roles = {w[0] for w in WALKS}
capital["crowd"] = [c for c in capital.get("crowd", []) if c.get("role") not in roles]
for role, a, b, speed in WALKS:
    capital["crowd"].append({"role": role, "position": a, "rotation": 90 if b[0] > a[0] else -90, "pose": "idle", "path": b, "speed": speed})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK quarto do rei:", [w[0] for w in WALKS])
