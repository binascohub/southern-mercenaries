"""Bordel de Tortuga, a Sereia Rubra (área "brothel"): interior de uma sala só, como a Taverna (a parede sul fica aberta para a câmera), com a porta na rua
principal de Tortuga, no lado leste da beira sul (a da Taverna fica no oeste).
 - Fundo (norte): cinco camas lado a lado, separadas por cortinas de pano penduradas; na do meio, uma moça de biquíni de quatro.
 - Meio: dois conjuntos de sofás com clientes e cortesãs sentados, e uma mesa redonda com vinho e dois clientes nos banquinhos.
 - Oeste: o balcão, com garrafas e a prateleira; leste: a lareira e um vaso de planta.
 - As moças de biquíni (que antes ficavam no quarto do rei da Capital, e de lá saem): a moça da praia e a Asila dançam na frente; a Anna passeia na frente,
   a Adriana entre as camas e os sofás, a Afrique entre a mesa redonda e as dançarinas e a moça sci-fi rente aos pés das camas;
   a moça da dança do ventre à direita da frente e a Prix, a anfitriã, ao lado do balcão. Os clientes ficam na mesa redonda e nos sofás.
 - Luz: três lustres e luzes avermelhadas; uma luz vermelha marca a porta na rua.
Só cenário (sem missão nem loja). A música é a da Taverna (game/autoload/music.gd). Idempotente. Roda no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/build_brothel.py   (a partir da raiz do projeto)"""
import json

ARENAS = "data/arenas.json"
arenas = json.load(open(ARENAS, encoding="utf-8"))
tavern = arenas["tavern"]
tortuga = arenas["tortuga"]
DOOR = [9.0, 7.2]  # na rua principal, beira sul (lado da câmera), a leste do centro

RED = [1.0, 0.28, 0.32]
WARM = [1.0, 0.6, 0.3]
decor = []


def add(piece, x, z, **extra):
    d = {"piece": piece, "position": [x, z]}
    d.update(extra)
    decor.append(d)


# Camas no fundo, separadas por cortinas (duas faixas de pano por divisória, penduradas a 2,4 m).
add("Bed_2", -8.0, -5.0, rotation=0, solid=[2.7, 3.73], scale=1.8)
add("Bed_3", -3.8, -5.4, rotation=0, solid=[2.0, 2.9], scale=1.4)
add("Bed_1", 0.0, -5.4, rotation=0, solid=[1.4, 2.9], scale=1.4)
add("Brothel_Bed_Woman", 0.0, -5.0, y=0.45, rotation=37)  # a moça de biquíni de quatro em cima da cama do meio (o arquivo vem na diagonal: 37° a deixa ao longo da cama, de frente para o sul) (tools/assets/build_bed_pose.py)
add("Bed_3", 3.8, -5.4, rotation=0, solid=[2.0, 2.9], scale=1.4)
add("Bed_4", 8.0, -5.0, rotation=0, solid=[1.8, 3.7], scale=1.8)
for x in (-5.9, -1.9, 1.9, 5.9):
    for z in (-6.4, -5.6, -4.8, -4.0):
        add("Banner_1_Cloth", x, z, y=2.4, rotation=90)
for x in (-6.0, 6.0):
    add("Tv_Candle", x - 0.7, -6.6, y=0.0)
# Sofás e a mesa redonda do meio (o Sofa_Group traz o sofá grande ao fundo, virado para o sul, a poltrona, a mesinha e o tapete).
add("Sofa_Group", -5.6, 0.2, rotation=0, solid=[4.2, 2.6])
add("Sofa_Group", 5.6, 0.2, rotation=0, solid=[4.2, 2.6])
add("Tv_Table_Round", 0.0, 1.4, solid=[1.9, 1.9])
add("Tv_Stool_Round", -1.4, 1.4, rotation=90)
add("Tv_Stool_Round", 1.4, 1.4, rotation=-90)
add("Fk_Wine_Red", 0.1, 1.2, y=0.75, rotation=20)
add("Glass_Cup_Wine", -0.45, 1.55, y=0.75, rotation=80, scale=1.8)
add("Glass_Cup_Wine", 0.5, 1.7, y=0.75, rotation=250, scale=1.8)
add("Tv_Candle", -0.1, 1.75, y=0.75)
# Balcão da cafetina (oeste) e lareira (leste).
add("Table_Large", -8.9, 3.6, rotation=90, solid=[1.1, 2.8])
add("Shelf_Small_Bottles", -10.6, 3.6, rotation=90)
add("Bottle_3", -8.8, 2.8, y=0.81, rotation=40)
add("Bottle_2", -9.0, 4.3, y=0.81, rotation=200)
add("Glass_Cup_Wine", -8.7, 3.5, y=0.81, rotation=10, scale=1.8)
add("Tv_Fireplace", 10.4, 3.4, rotation=-90, solid=[1.36, 1.28])
add("Vase_Big", 10.2, -1.6)
add("Pl_Flower", -10.0, -1.4)
# Lustres e luzes.
add("Chandelier_Royal", 0.0, -1.0, y=3.8)
add("Chandelier", -6.0, 2.4, y=3.9)
add("Chandelier", 6.0, 2.4, y=3.9)
for x, z, y, color, energy, rng in ((-6.0, -4.5, 2.0, RED, 1.3, 8), (6.0, -4.5, 2.0, RED, 1.3, 8), (0.0, 2.2, 2.2, RED, 1.0, 9),
                                    (-8.5, 3.6, 1.8, WARM, 0.8, 6), (9.6, 3.4, 0.9, WARM, 1.3, 7)):
    decor.append({"light": color, "position": [x, z], "y": y, "energy": energy, "range": rng})

crowd = [
    # As moças de biquíni (Jungle Jim, CC BY 4.0; modelos em game/actors/npc_model.gd): duas dançam na frente e duas passeiam de um lado a outro.
    {"role": "beach_dancer", "position": [-2.6, 4.4], "rotation": 0, "pose": "dance"},
    {"role": "asila_dancer", "position": [2.6, 4.4], "rotation": 0, "pose": "dance"},
    {"role": "anna_walker", "position": [-6.5, 5.4], "rotation": 90, "pose": "idle", "path": [6.5, 5.4], "speed": 0.8},
    {"role": "adriana_walker", "position": [7.5, -2.4], "rotation": -90, "pose": "idle", "path": [-7.5, -2.4], "speed": 0.9},
    {"role": "afrique_walker", "position": [-7.5, 2.8], "rotation": 90, "pose": "idle", "path": [7.5, 2.8], "speed": 0.85},
    {"role": "scifi_walker", "position": [5.8, -3.3], "rotation": -90, "pose": "idle", "path": [-5.8, -3.3], "speed": 0.8},  # rente aos pés das camas
    {"role": "belly_dancer", "position": [6.2, 4.6], "rotation": -15, "pose": "dance"},  # à direita da frente (o meio é a entrada); a dança anda até ~0,9 m
    {"role": "prix_hostess", "position": [-7.9, 4.6], "rotation": 60, "pose": "stand"},  # a anfitriã, ao lado do balcão
    # Clientes.
    {"role": "pirate", "position": [-1.4, 1.4], "rotation": 90, "pose": "sit"},
    {"role": "sailor", "position": [1.4, 1.4], "rotation": 270, "pose": "sit"},
    {"role": "drunk", "position": [-5.5, -0.55], "rotation": 0, "pose": "sit"},
    {"role": "pirate_2", "position": [5.7, -0.55], "rotation": 0, "pose": "sit"},
]

arenas["brothel"] = {
    "_comment": "Bordel da Sereia Rubra, em Tortuga (gerado por tools/assets/build_brothel.py): camas com cortinas no fundo, sofás e mesa no meio, balcão, "
                "lareira, moças de biquíni dançando e passeando, e clientes. A porta fica na rua principal de Tortuga.",
    "name_key": "AREA_BROTHEL", "town": True, "player_class": tavern.get("player_class", "mage"), "wake_radius": 0, "alert_radius": 0, "area_level": 1,
    "rooms": [{"id": "hall", "center": [0, 0], "size": [22, 14], "doors": [], "torch": True}],
    "encounters": [],
    "entries": {"start": [0, 3], "door": [0, 4.8]},
    "props": [{"id": "brothel_exit", "kind": "exit", "name_key": "PROP_TAVERN_EXIT", "position": [0, 6.2], "to": "tortuga", "entry": "brothel"}],
    "style": dict(tavern["style"], _comment="Paredes de reboco e enxaimel como a Taverna, piso de tijolo; a parede sul fica aberta para a câmera."),
    "decor": decor, "crowd": crowd, "breakables": [],
}

capital = arenas["capital_01_aurenhold"]
capital["crowd"] = [c for c in capital.get("crowd", []) if c.get("role") not in ("anna_walker", "adriana_walker", "beach_dancer", "asila_dancer")]
tortuga["props"] = [p for p in tortuga["props"] if p["id"] != "brothel_door"]
# A entrada é a pedra de energia (tools/assets/build_brothel_stone.py), sem portal e sem marca no minimapa.
# É um easter egg: sem nome flutuando e o aviso de interação só diz "Pedra misteriosa".
tortuga["props"].append({"id": "brothel_door", "kind": "exit", "name_key": "PROP_MYSTERY_STONE", "position": DOOR, "to": "brothel", "entry": "door",
                         "piece": "Brothel_Stone", "minimap": False, "label": False})
tortuga["entries"]["brothel"] = [DOOR[0], DOOR[1] - 1.7]
tortuga["decor"] = [d for d in tortuga["decor"] if not d.get("brothel_sign")]
tortuga["decor"].append({"light": RED, "position": [DOOR[0], DOOR[1] + 0.3], "y": 2.2, "energy": 1.6, "range": 6, "brothel_sign": True})

json.dump(arenas, open(ARENAS, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(ARENAS, "a").write("\n")
NAMES = {"AREA_BROTHEL": ("Bordel da Sereia Rubra", "The Crimson Mermaid", "Burdel de la Sirena Carmesí"),
         "PROP_BROTHEL": ("Bordel", "Brothel", "Burdel"),
         "PROP_MYSTERY_STONE": ("Pedra misteriosa", "Mysterious Stone", "Piedra misteriosa")}
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    text = open(path, encoding="utf-8").read()
    for key, names in NAMES.items():
        if 'msgid "%s"' % key not in text:
            text += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, names[idx])
    open(path, "w", encoding="utf-8").write(text)
print("OK bordel:", len(decor), "peças,", len(crowd), "pessoas; porta em", DOOR)
