"""Tortuga: torcida em volta das brigas de rua. As 6 pessoas de build_background_people.py (papéis crowd_cheer_1..6 em game/actors/npc_model.gd, com roupa medieval)
ficam a ~2,3 m de quatro brigas, do lado de fora dos caminhos de quem passeia, viradas para os brigões e comemorando (animação "cheer").
Idempotente (tira as que já estavam e põe de novo); chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_tortuga_cheer_crowd.py   (a partir da raiz do projeto)"""
import json, math

PATH = "data/arenas.json"
# (pessoa, posição [x, z], briga que ela assiste [x, z])
SPOTS = [
    (1, [6.5, -13.6], [6.0, -16.0]),
    (4, [4.6, -17.9], [6.0, -16.0]),
    (2, [-5.4, -13.0], [-5.4, -15.4]),
    (5, [-6.5, -17.5], [-5.4, -15.4]),
    (3, [19.1, -0.3], [19.1, 2.1]),
    (6, [-13.6, 0.3], [-14.0, -2.0]),
]
raw = open(PATH, encoding="utf-8").read()
arenas = json.loads(raw)
crowd = arenas["tortuga"]["crowd"]
crowd[:] = [c for c in crowd if not str(c.get("role", "")).startswith("crowd_cheer_")]
for n, at, fight in SPOTS:
    rot = round(math.degrees(math.atan2(fight[0] - at[0], fight[1] - at[1]))) % 360  # o modelo olha para +Z: vira para a briga
    crowd.append({"role": "crowd_cheer_%d" % n, "position": at, "rotation": rot, "pose": "idle"})
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(arenas, f, indent=2, ensure_ascii=False)
    if raw.endswith("\n"):
        f.write("\n")
print("Tortuga: torcida em volta das brigas,", len(SPOTS), "pessoas")
