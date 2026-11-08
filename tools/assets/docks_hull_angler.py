"""Casco Vivo, mini-chefe das Docas (hull_beast), com o modelo novo: o peixe-pescador de pé com a isca luminosa ("MONSTER", NORBERTO-3D, CC BY-SA 4.0;
tools/assets/build_hull_angler.py), no lugar do monstro de tábuas (plank_monster, de set_monster_roster.py). Só muda a aparência: nome, textos,
números, investidas, puxão e ondas ficam. Idempotente. Roda no fim de build_maps.py.
uso: python3 tools/assets/docks_hull_angler.py   (a partir da raiz do projeto)"""
import json

MONSTERS = "data/monsters.json"
mons = json.load(open(MONSTERS, encoding="utf-8"))
mons["hull_beast"].update({"look": "hull_angler", "color": [1.0, 1.0, 1.0], "sound": "beast"})
json.dump(mons, open(MONSTERS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(MONSTERS, "a").write("\n")
print("OK docas: Casco Vivo com o modelo do peixe-pescador")
