"""Gente, bichos e objetos novos (data/arenas.json; os papéis de "crowd" ficam em game/actors/npc_model.gd):
  Capital: a Cavaleira Nobre (noble_knight, tools/assets/build_noble_knight.py) anda de ida e volta pelo Pátio do Castelo (z = -43,5, longe da forca e dos obeliscos);
           a Princesa-Freira (princess_nun, tools/assets/build_princess_nun.py) anda pela Avenida Norte, no lado leste (x = 6, entre o banco e os guardas);
           a Dama Nobre (noble_beauty, parada na pose do arquivo) fica na igreja, à esquerda do altar, de frente para ele;
           o Cidadão (townsman, parado com as mãos na cintura) na praça do portão, olhando a barraca da feira;
           o piano de cauda (Decor_Grand_Piano) no lado oeste do Quarto do Rei, longe das camas e da porta;
           o varal de carnes (Decor_Meat_Rail) pendurado na frente da barraca da feira, na borda do toldo (embaixo do toldo, ou entre as barracas, a câmera de cima não o via).
  Taverna de Tortuga: o varal de carnes na parede do fundo, à direita das prateleiras, alto (acima do balde).
  Fazenda: uma cabra (goat, tools/assets/build_decor_prop.py) passeia devagar pelo pasto, a leste das ovelhas.
Idempotente (tira o que já estava e põe de novo); chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/add_capital_extras.py   (a partir da raiz do projeto)"""
import json

PATH = "data/arenas.json"
raw = open(PATH, encoding="utf-8").read()
arenas = json.loads(raw)
ROLES = ("noble_knight", "princess_nun", "noble_beauty", "goat", "townsman")
PIECES = ("Decor_Grand_Piano", "Decor_Meat_Rail")


def reset(area):
    a = arenas[area]
    a["crowd"] = [c for c in a.get("crowd", []) if c.get("role") not in ROLES]
    a["decor"] = [d for d in a.get("decor", []) if d.get("piece") not in PIECES]
    return a


cap = reset("capital_01_aurenhold")
cap["crowd"] += [
    {"role": "noble_knight", "position": [-13.0, -43.5], "rotation": 90, "pose": "walk", "path": [13.0, -43.5], "speed": 0.9},
    {"role": "princess_nun", "position": [6.0, -26.5], "rotation": 180, "pose": "walk", "path": [6.0, -38.0], "speed": 0.8},
    {"role": "noble_beauty", "position": [-37.0, -34.6], "rotation": 90, "pose": "idle"},
    {"role": "townsman", "position": [7.2, -2.2], "rotation": 117, "pose": "idle"},
]
cap["decor"] += [
    {"piece": "Decor_Grand_Piano", "position": [21.5, -60.5], "rotation": 90, "solid": [1.6, 2.7]},
    {"piece": "Decor_Meat_Rail", "position": [11.8, -2.95], "rotation": 0, "y": 0.3},
]
tav = reset("tavern")
tav["decor"].append({"piece": "Decor_Meat_Rail", "position": [6.2, -6.6], "rotation": 0, "y": 0.6})
farm = reset("farm_01_fields")
farm["crowd"].append({"role": "goat", "position": [20.0, -18.0], "rotation": 135, "pose": "walk", "path": [26.0, -24.0], "speed": 0.4})

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(arenas, f, indent=2, ensure_ascii=False)
    if raw.endswith("\n"):
        f.write("\n")
print("Capital, taverna e Fazenda: cavaleira, princesa, dama, piano, varais e cabra")
