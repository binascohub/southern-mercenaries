"""Bertram (o Caçador) e Elara (a Curtidora) deixam de ser NPCs parados e passam a andar pelo mapa (data/arenas.json "crowd", papéis "hunter" e "tanner"
de data/crowd.json): Bertram vai e volta entre o acampamento e a entrada do mapa; Elara, de um lado a outro do acampamento. Sem missão nem conversa (a missão
forest_reptiles saiu). Limpa as plantas e pedras soltas na linha de cada caminhada. Roda depois de move_forest_village.py e add_forest_campfire.py (é
chamado no fim de tools/assets/build_maps.py). Idempotente.
uso: python3 tools/assets/add_forest_walkers.py   (a partir da raiz do projeto)"""
import json, math
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
WALKS = [("hunter", [-33.0, -45.0], [-33.0, -14.0], 1.0), ("tanner", [-37.0, -55.0], [-22.0, -55.0], 0.8)]


def seg_dist(p, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dz) / (dx * dx + dz * dz)))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dz))


forest["props"] = [p for p in forest["props"] if p["id"] not in ("village_hunter", "village_wife")]
forest["decor"] = [d for d in forest["decor"] if str(d.get("piece", "")).startswith("Trail_") or d.get("camp")
                   or not (str(d.get("piece", "")).startswith(("Rock", "Pl_")) and any(seg_dist(d["position"], a, b) < 1.4 for _, a, b, _ in WALKS))]
forest["crowd"] = [c for c in forest["crowd"] if c.get("role") not in ("hunter", "tanner")]
for role, a, b, speed in WALKS:
    forest["crowd"].append({"role": role, "position": a, "rotation": 0, "pose": "idle", "path": b, "speed": speed})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK andarilhos:", [w[0] for w in WALKS])
