"""Capital: o Guerreiro Andarilho (papel hero_warrior em game/actors/npc_model.gd; "hero warrior (downloadable)", Diox..Andrey, CC BY 4.0, preso ao esqueleto dos heróis por
tools/assets/build_mixamo_civilian.py) anda de ida e volta pela Avenida, no lado oeste da fonte (x = -6, linha sem postes, bancos nem barracas).
Idempotente (tira o que já estava e põe de novo); chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_capital_hero_warrior.py   (a partir da raiz do projeto)"""
import json

PATH = "data/arenas.json"
raw = open(PATH, encoding="utf-8").read()
arenas = json.loads(raw)
crowd = arenas["capital_01_aurenhold"]["crowd"]
crowd[:] = [c for c in crowd if c.get("role") != "hero_warrior"]
crowd.append({"role": "hero_warrior", "position": [-6.0, -8.5], "rotation": 180, "pose": "walk", "path": [-6.0, -21.5], "speed": 1.1})
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(arenas, f, indent=2, ensure_ascii=False)
    if raw.endswith("\n"):
        f.write("\n")
print("Capital: Guerreiro Andarilho na Avenida")
