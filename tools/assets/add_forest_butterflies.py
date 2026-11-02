"""Borboletas animadas (Butterfly (animated), Čestmír Dammer / cdmir, CC0; Butterfly_Anim.glb, tools/assets/build_butterfly_anim.py) na Floresta, voando em
círculo (decor "swim", como as borboletas azuis Butterfly_Small, mas batendo as asas com a animação do próprio modelo): 4 no acampamento, 3 na sala da lagoa
e 3 na sala de entrada. Roda depois de move_forest_village.py (é chamado no fim de tools/assets/build_maps.py). Idempotente ("anim": true).
uso: python3 tools/assets/add_forest_butterflies.py   (a partir da raiz do projeto)"""
import json, random
ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
forest = arenas["forest_01_path"]
rooms = {r["id"]: r for r in forest["rooms"]}
forest["decor"] = [d for d in forest["decor"] if not (d.get("piece") == "Butterfly_Anim")]
rng = random.Random("forest_butterflies_anim")
for rid, count in (("village", 4), ("bats", 3), ("toads", 3)):
    r = rooms[rid]
    cx, cz = r["center"]
    hw, hd = r["size"][0] / 2 - 5.0, r["size"][1] / 2 - 5.0
    for _ in range(count):
        forest["decor"].append({"piece": "Butterfly_Anim", "position": [round(cx + rng.uniform(-hw, hw), 1), round(cz + rng.uniform(-hd, hd), 1)],
                                "y": round(rng.uniform(1.1, 1.8), 2), "scale": 1.4,
                                "swim": {"radius": round(rng.uniform(2.0, 3.5), 1), "speed": round(rng.uniform(0.8, 1.2), 2), "phase": round(rng.uniform(0, 6.28), 2)}})
json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
print("OK borboletas animadas:", sum(1 for d in forest["decor"] if d.get("piece") == "Butterfly_Anim"))
