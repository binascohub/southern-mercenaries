"""Conteúdo dos modelos do autor (pixellabs-*.glb; autoria e licença a confirmar):
  - Sentinela de Lata (tin_sentinel, pixellabs-robot-3332.glb): monstro da vila da Floresta (a aldeia das elfas): um grupo de 2 nas bordas da aldeia;
  - Espectro das Ruínas (ruins_wraith, pixellabs-undead-3417.glb): encapuzado que flutua, um par a cada 3º grupo de monstros das Ruínas;
  - Estandarte do Dragão (Banner_Dragon, pixellabs-banner-3761.glb): dois na entrada do Cemitério, ladeando o caminho;
  - Golem de Ferro Negro (mine_golem, pixellabs-glb-3350.glb): um em cada 5º grupo de monstros da Mina;
  - Espantalho Afogado (docks_scarecrow, nickpanek-scarecrow-monster-1663.glb): um par a cada 3º grupo de monstros das Docas;
  - Árvore Morta (Dead_Tree_Pixel, pixellabs-dead-tree-3551.glb): decoração espalhada pela Floresta Escura;
  - Trono de Caveiras (Skull_Throne, pixellabs-skull-throne-3562.glb): decoração da sala do chefe do Cemitério, de frente para a entrada da sala.
Os modelos saem de tools/assets/build_mine_robots.py (tin, wraith) e build_static_prop.py. Idempotente; roda antes do balance_monsters.py.
uso: python3 tools/assets/add_pixellabs_content.py   (a partir da raiz do projeto)"""
import json

def dump(p, d, raw):
    open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent="\\t" if False else ("\t" if raw.startswith("{\n\t") else 2)) + ("\n" if raw.endswith("\n") else ""))

raw = open("data/monsters.json", encoding="utf-8").read()
mdata = json.loads(raw)
monsters = mdata.get("monsters", mdata)
monsters["tin_sentinel"] = {
    "_comment": "Sentinela de Lata (pixellabs-robot-3332.glb do autor; build_mine_robots.py, modo tin): ovo de lata com braços grandes que rondam a aldeia das elfas da Floresta; resistente e lento. Terra.",
    "name_key": "MONSTER_TIN_SENTINEL", "max_health": 190, "move_speed": 2.4, "damage": 14, "attack_range": 2.1, "attack_windup": 0.7, "attack_cooldown": 1.5, "aggro_range": 40.0,
    "size": 1.4, "category": "common", "element": "earth", "look": "tin_sentinel", "color": [1.0, 1.0, 1.0], "role": "normal"}
monsters["ruins_wraith"] = {
    "_comment": "Espectro das Ruínas (pixellabs-undead-3417.glb do autor; build_mine_robots.py, modo wraith): encapuzado que flutua, sem pernas, com manoplas enormes; veloz e frágil. Água.",
    "name_key": "MONSTER_RUINS_WRAITH", "max_health": 130, "move_speed": 3.4, "damage": 15, "attack_range": 2.2, "attack_windup": 0.55, "attack_cooldown": 1.3, "aggro_range": 40.0,
    "size": 1.5, "category": "common", "element": "water", "look": "ruins_wraith", "color": [1.0, 1.0, 1.0], "role": "light"}
monsters["mine_golem"] = {
    "_comment": "Golem de Ferro Negro da Mina (pixellabs-glb-3350.glb do autor; build_mine_robots.py, modo golem): golem blindado de punhos enormes; lento e muito resistente. Terra.",
    "name_key": "MONSTER_MINE_GOLEM", "max_health": 260, "move_speed": 1.8, "damage": 20, "attack_range": 2.6, "attack_windup": 0.9, "attack_cooldown": 1.8, "aggro_range": 40.0,
    "size": 2.0, "category": "common", "element": "earth", "look": "mine_golem", "color": [1.0, 1.0, 1.0], "role": "tank"}
monsters["docks_scarecrow"] = {
    "_comment": "Espantalho Afogado das Docas (nickpanek-scarecrow-monster-1663.glb do autor; build_mine_robots.py, modo scarecrow): humanoide curvado de trapos encharcados; arranha com as mãos compridas. Água.",
    "name_key": "MONSTER_DOCKS_SCARECROW", "max_health": 160, "move_speed": 3.0, "damage": 14, "attack_range": 2.0, "attack_windup": 0.6, "attack_cooldown": 1.3, "aggro_range": 40.0,
    "size": 1.9, "category": "common", "element": "water", "look": "docks_scarecrow", "color": [1.0, 1.0, 1.0], "role": "normal"}
dump("data/monsters.json", mdata, raw)

raw = open("data/arenas.json", encoding="utf-8").read()
adata = json.loads(raw)
arenas = adata.get("arenas", adata)
# Floresta: sentinelas na aldeia
forest = arenas["forest_01_path"]
forest["encounters"] = [e for e in forest["encounters"] if e["id"] != "f_village_sentinels"]
forest["encounters"].append({"id": "f_village_sentinels", "position": [-36.0, -67.0], "monsters": [{"monster": "tin_sentinel", "count": 2}], "level": 3})
# Ruínas: espectros
ruins = arenas["ruins_01_city"]
skip = ("boss", "alpha", "mimic", "mm_", "vault", "gate")
grp = [e for e in ruins["encounters"] if not any(s in e["id"] for s in skip)]
for e in grp:
    e["monsters"] = [m for m in e["monsters"] if m["monster"] != "ruins_wraith"]
for i, e in enumerate(grp):
    if i % 3 == 1:
        e["monsters"].append({"monster": "ruins_wraith", "count": 2})
# Mina: golens
mine = arenas["mine_01_crystal_vein"]
msec = [e for e in mine["encounters"] if e["id"].startswith("mn_s")]
for e in msec:
    e["monsters"] = [m for m in e["monsters"] if m["monster"] != "mine_golem"]
for i, e in enumerate(msec):
    if i % 5 == 2:
        e["monsters"].append({"monster": "mine_golem", "count": 1})
# Docas: espantalhos
docks = arenas["docks_01_pier"]
dskip = ("captain", "mimic", "mm_")
dgrp = [e for e in docks["encounters"] if not any(k in e["id"] for k in dskip)]
for e in dgrp:
    e["monsters"] = [m for m in e["monsters"] if m["monster"] != "docks_scarecrow"]
for i, e in enumerate(dgrp):
    if i % 3 == 1:
        e["monsters"].append({"monster": "docks_scarecrow", "count": 2})
# Floresta Escura: árvores mortas
import math, random
dark = arenas["dark_forest_01_woods"]
dark["decor"] = [d for d in dark["decor"] if d.get("piece") != "Dead_Tree_Pixel"]
rngd = random.Random("dead-trees")
solids = [x["position"] for k in ("decor", "props", "breakables") for x in dark[k] if k != "decor" or x.get("solid") or x.get("collider")] + [e["position"] for e in dark["encounters"]]
start = dark["entries"]["start"]
placed = 0
for _ in range(900):
    if placed >= 34:
        break
    room = rngd.choice(dark["rooms"])
    x = room["center"][0] + rngd.uniform(-room["size"][0] / 2 + 5, room["size"][0] / 2 - 5)
    z = room["center"][1] + rngd.uniform(-room["size"][1] / 2 + 5, room["size"][1] / 2 - 5)
    if math.hypot(x - start[0], z - start[1]) < 14 or any(math.hypot(x - q[0], z - q[1]) < 5.0 for q in solids):
        continue
    dark["decor"].append({"piece": "Dead_Tree_Pixel", "position": [round(x, 1), round(z, 1)], "rotation": rngd.randrange(0, 360, 15), "scale": round(rngd.uniform(2.6, 4.2), 2), "solid": [0.9, 0.9]})
    solids.append([x, z])
    placed += 1
# Cemitério: estandartes na entrada e trono na sala do chefe
cem = arenas["cemetery_01_yard"]
cem["decor"] = [d for d in cem["decor"] if d.get("piece") not in ("Banner_Dragon", "Skull_Throne")]
for x in (-4.5, 4.5):
    cem["decor"].append({"piece": "Banner_Dragon", "position": [x, 1.0], "rotation": 0, "scale": 2.0, "solid": [0.6, 0.4]})
cem["decor"].append({"piece": "Skull_Throne", "position": [-72.0, -176.0], "rotation": 0, "scale": 2.2, "solid": [1.6, 1.2]})
dump("data/arenas.json", adata, raw)

NAMES = {"MONSTER_MINE_GOLEM": ("Blackiron Golem", "Gólem de Hierro Negro", "Golem de Ferro Negro"), "MONSTER_DOCKS_SCARECROW": ("Drowned Scarecrow", "Espantapájaros Ahogado", "Espantalho Afogado"), "MONSTER_TIN_SENTINEL": ("Tin Sentinel", "Centinela de Lata", "Sentinela de Lata"), "MONSTER_RUINS_WRAITH": ("Ruins Wraith", "Espectro de las Ruinas", "Espectro das Ruínas")}
for f, i in (("messages.pot", None), ("en.po", 0), ("es.po", 1), ("pt_BR.po", 2)):
    s = open("locale/" + f, encoding="utf-8").read()
    for key, names in NAMES.items():
        if 'msgid "%s"' % key in s:
            continue
        k = s.index('msgid "MONSTER_GOBLIN"\nmsgstr')
        j = s.index("\n\n", k) + 2
        s = s[:j] + 'msgid "%s"\nmsgstr "%s"\n\n' % (key, names[i] if i is not None else "") + s[j:]
    open("locale/" + f, "w", encoding="utf-8").write(s)
print("OK conteúdo pixellabs: %d árvores mortas na Floresta Escura," % placed, sentinelas na Floresta, %d grupos de espectros nas Ruínas, estandartes e trono no Cemitério" % sum(1 for e in grp if any(m["monster"] == "ruins_wraith" for m in e["monsters"])))
