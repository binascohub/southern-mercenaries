"""Os dois robôs da Mina (modelos do autor; build_mine_robots.py): o Autômato Enferrujado (bruto lento e resistente, golpeia de cima para baixo) e o Vigia de Latão (robozinho amarelo rápido
e frágil, ataca em grupo com cabeçadas). Cria os dois monstros (data/monsters.json), os nomes nas três línguas e os põe nos grupos de monstros dos setores da Mina: um autômato a cada 4º grupo
e dois vigias a cada 3º. Idempotente; roda antes do balance_monsters.py (que ajusta vida, dano e XP pelo nível do mapa e pelo papel).
uso: python3 tools/assets/add_mine_robots.py   (a partir da raiz do projeto)"""
import json

def load(p):
    return json.load(open(p, encoding="utf-8"))

def dump(p, d, raw):
    open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent="\t" if raw.startswith("{\n\t") else 2) + ("\n" if raw.endswith("\n") else ""))

raw = open("data/monsters.json", encoding="utf-8").read()
mdata = json.loads(raw)
monsters = mdata.get("monsters", mdata)
monsters["mine_automaton"] = {
    "_comment": "Autômato Enferrujado da Mina (pixellabs-glb-3393.glb do autor; tools/assets/build_mine_robots.py): robô steampunk de latão e ferrugem; lento, resistente, golpeia com os dois braços. Terra.",
    "name_key": "MONSTER_MINE_AUTOMATON", "max_health": 220, "move_speed": 2.0, "damage": 18, "attack_range": 2.4, "attack_windup": 0.8, "attack_cooldown": 1.6, "aggro_range": 40.0,
    "size": 1.6, "category": "common", "element": "earth", "look": "mine_automaton", "color": [1.0, 1.0, 1.0], "role": "tank"}
monsters["mine_scout"] = {
    "_comment": "Vigia de Latão da Mina (pixellabs-glb-3347.glb do autor; tools/assets/build_mine_robots.py): robozinho amarelo de antenas; rápido e frágil, ataca em grupo com cabeçadas. Fogo.",
    "name_key": "MONSTER_MINE_SCOUT", "max_health": 120, "move_speed": 3.8, "damage": 12, "attack_range": 1.7, "attack_windup": 0.45, "attack_cooldown": 1.1, "aggro_range": 40.0,
    "size": 1.3, "category": "common", "element": "fire", "look": "mine_scout", "color": [1.0, 1.0, 1.0], "role": "light"}
dump("data/monsters.json", mdata, raw)

raw = open("data/arenas.json", encoding="utf-8").read()
adata = json.loads(raw)
mine = adata.get("arenas", adata)["mine_01_crystal_vein"]
sector = [e for e in mine["encounters"] if e["id"].startswith("mn_s")]
for e in sector:
    e["monsters"] = [m for m in e["monsters"] if m["monster"] not in ("mine_automaton", "mine_scout")]
for i, e in enumerate(sector):
    if i % 4 == 1:
        e["monsters"].append({"monster": "mine_automaton", "count": 1})
    if i % 3 == 2:
        e["monsters"].append({"monster": "mine_scout", "count": 2})
dump("data/arenas.json", adata, raw)

NAMES = {"MONSTER_MINE_AUTOMATON": ("Rust Automaton", "Autómata Oxidado", "Autômato Enferrujado"), "MONSTER_MINE_SCOUT": ("Brass Watcher", "Vigía de Latón", "Vigia de Latão")}
for f, i in (("messages.pot", None), ("en.po", 0), ("es.po", 1), ("pt_BR.po", 2)):
    s = open("locale/" + f, encoding="utf-8").read()
    anchor = 'msgid "MONSTER_GOBLIN"\nmsgstr'
    for key, names in NAMES.items():
        if 'msgid "%s"' % key in s:
            continue
        k = s.index(anchor)
        j = s.index("\n\n", k) + 2
        s = s[:j] + 'msgid "%s"\nmsgstr "%s"\n\n' % (key, names[i] if i is not None else "") + s[j:]
    open("locale/" + f, "w", encoding="utf-8").write(s)
print("OK robôs da Mina: %d grupos com autômato, %d com vigias" % (sum(1 for e in sector if any(m["monster"] == "mine_automaton" for m in e["monsters"])), sum(1 for e in sector if any(m["monster"] == "mine_scout" for m in e["monsters"]))))
