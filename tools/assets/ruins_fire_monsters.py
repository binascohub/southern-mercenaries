"""Ruínas (ruins_01_city): todos os monstros são de FOGO (fracos a Água).
Os comuns que também aparecem em outros mapas ganham uma variante só das Ruínas, com o mesmo modelo avermelhado:
Goblin -> Goblin das Cinzas (ember_goblin), Morcego Pestilento -> Morcego de Brasa (ember_bat), Escorpião Venenoso -> Escorpião de Fogo
(fire_scorpion, cuspe em brasa) e Mímico -> Mímico em Brasa (ember_mimic). Os que só existem nas Ruínas (Espectro, Alfa da Matilha,
Guardião, Campeão, Rei Caído) mudam de elemento direto. As missões das Ruínas passam a dizer Fogo ("target_element").
Os outros compartilhados que aparecerem (o roster dos mapas troca alguns) viram "ru_fire_<id>". Idempotente.
Roda no fim de build_maps.py (depois do roster, dos Mímicos e do balanceamento).
uso: python3 tools/assets/ruins_fire_monsters.py   (a partir da raiz do projeto)"""
import json

ARENAS, MONSTERS, QUESTS = "data/arenas.json", "data/monsters.json", "data/quests.json"
mons = json.load(open(MONSTERS, encoding="utf-8"))
arenas = json.load(open(ARENAS, encoding="utf-8"))
quests = json.load(open(QUESTS, encoding="utf-8"))
ruins = arenas["ruins_01_city"]

EMBER = [1.0, 0.55, 0.4]
VARIANTS = {   # novo id: (base, name_key, cor, mudanças, comentário)
    "ember_goblin": ("goblin", "MONSTER_EMBER_GOBLIN", EMBER, {}, "Goblin das Cinzas: o Goblin das Ruínas, queimado pela guerra; de Fogo."),
    "ember_bat": ("plague_bat", "MONSTER_EMBER_BAT", [1.0, 0.5, 0.3], {}, "Morcego de Brasa: o Morcego Pestilento das Ruínas; de Fogo."),
    "fire_scorpion": ("venom_scorpion", "MONSTER_FIRE_SCORPION", [1.0, 0.45, 0.3],
                      {"spit": {"radius": 1.5, "puddle_time": 4.0, "puddle_dps": 6.0, "glob": [1.0, 0.45, 0.1]}},
                      "Escorpião de Fogo: o Escorpião Venenoso das Ruínas; cospe brasa que deixa o chão queimando. De Fogo."),
    "ember_mimic": ("chest_mimic", "MONSTER_EMBER_MIMIC", [1.0, 0.6, 0.45], {}, "Mímico em Brasa: o Mímico das Ruínas; de Fogo."),
}
for new_id, (base, name_key, color, changes, comment) in VARIANTS.items():
    m = dict(mons[base])
    m.update({"name_key": name_key, "element": "fire", "color": color, "_comment": comment})
    m.update(changes)
    mons[new_id] = m
SWAP = {base: new_id for new_id, (base, *_rest) in VARIANTS.items()}


def ids_in(arena):
    out = {m["monster"] for e in arena.get("encounters", []) for m in e["monsters"]}
    for p in arena.get("props", []):
        for s in [p.get("summon")] + [x["summon"] for x in p.get("extra_summons", [])]:
            if s:
                out |= {m["monster"] for m in s["monsters"]}
    return out


elsewhere = set().union(*(ids_in(a) for aid, a in arenas.items() if isinstance(a, dict) and aid != "ruins_01_city"))
for mid in sorted(ids_in(ruins)):
    if mid in SWAP or mid in VARIANTS or mons[mid].get("element") == "fire":
        continue
    if mid not in elsewhere:
        mons[mid]["element"] = "fire"          # só existe nas Ruínas: muda direto
    else:                                      # outro monstro compartilhado (o roster dos mapas pode trocar): variante de fogo com o mesmo nome
        new_id = "ru_fire_" + mid
        m = dict(mons[mid])
        m.update({"element": "fire", "color": EMBER, "_comment": "Variante de Fogo das Ruínas de " + mid + " (ruins_fire_monsters.py)."})
        mons[new_id] = m
        SWAP[mid] = new_id


def swap(entries):
    for entry in entries:
        entry["monster"] = SWAP.get(entry["monster"], entry["monster"])


for e in ruins["encounters"]:
    swap(e["monsters"])
for p in ruins["props"]:
    if "summon" in p:
        swap(p["summon"]["monsters"])
    for extra in p.get("extra_summons", []):
        swap(extra["summon"]["monsters"])
left = sorted({m["monster"] for e in ruins["encounters"] for m in e["monsters"] if mons[m["monster"]]["element"] != "fire"})
assert not left, left

for q in quests.values():
    if isinstance(q, dict) and q.get("area") == "ruins_01_city" and "target_element" in q:
        q["target_element"] = "fire"

for path, data in ((MONSTERS, mons), (ARENAS, arenas), (QUESTS, quests)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")

# Nomes (pt_BR, en, es) e a descrição da missão dos goblins, que dizia "Terra — temem o Fogo".
NAMES = {"MONSTER_EMBER_GOBLIN": ("Goblin das Cinzas", "Ash Goblin", "Goblin de Ceniza"),
         "MONSTER_EMBER_BAT": ("Morcego de Brasa", "Ember Bat", "Murciélago de Brasa"),
         "MONSTER_FIRE_SCORPION": ("Escorpião de Fogo", "Fire Scorpion", "Escorpión de Fuego"),
         "MONSTER_EMBER_MIMIC": ("Mímico em Brasa", "Ember Mimic", "Mímico Ardiente")}
FIX = (("São de Terra — temem o Fogo.", "São de Fogo — temem a Água."),
       ("They are Earth — they fear Fire.", "They are Fire — they fear Water."),
       ("Son de Tierra: temen el Fuego.", "Son de Fuego: temen el Agua."))
for idx, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po")):
    text = open(path, encoding="utf-8").read()
    old, new = FIX[idx]
    if text.count(old) == 1:
        text = text.replace(old, new)
    text += "".join('\nmsgid "%s"\nmsgstr "%s"\n' % (k, v[idx]) for k, v in NAMES.items() if 'msgid "%s"' % k not in text)
    open(path, "w", encoding="utf-8").write(text)
print("OK ruins: monstros de fogo (%s)" % ", ".join(sorted(SWAP.values())))
