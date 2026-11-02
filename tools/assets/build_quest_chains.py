"""Cadeias de missões por mapa (docs/04-tortuga-e-missoes.md, "Trocas dos mapas"): todo mapa de combate tem 2 chefes (mini-chefes) e 2 NPCs; o NPC da cidade pede
SEMPRE 2 itens, e esses 2 itens só saem das 2 trocas do mapa. Cada troca: o chefe larga um item do mapa (monstro com "quest_drop"); o NPC do mapa, longe do chefe,
pede esse item e, ao receber, dá o item que o NPC da cidade pediu ("gives" da missão). O NPC do mapa só oferece a troca com a missão da cidade ativa ("requires").
Gera/atualiza (idempotente): data/quest_chains.json, valuables (itens de missão), npcs.json (NPCs e conversas), quests.json (1 missão da cidade + 2 trocas por mapa),
data/arenas.json (props dos NPCs, sem 'summon'), monsters.json (quest_drop) e os textos pt/en/es em locale/. Chamado no fim de tools/assets/build_maps.py.
uso: python3 tools/assets/build_quest_chains.py   (a partir da raiz do projeto)"""
import json, math, re

ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES, CHAINS = ("data/arenas.json", "data/monsters.json", "data/npcs.json", "data/quests.json", "data/valuables.json", "data/quest_chains.json")
LANGS = ("pt_BR", "en", "es")

# Itens que já existiam (nomes e ícones prontos): não recebem texto novo.
EXISTING_ITEMS = {"human_heart", "human_lungs", "old_skull", "royal_soul", "wild_meat"}
ITEM_NAMES = {  # id: (pt, en, es)
    "gator_tooth": ("Dente do Gator Velho", "Old Gator's Tooth", "Diente del Caimán Viejo"),
    "frog_crown": ("Coroa do Rei dos Sapos", "Frog King's Crown", "Corona del Rey de los Sapos"),
    "sewer_pearl": ("Pérola do Esgoto", "Sewer Pearl", "Perla de la Alcantarilla"),
    "sewer_cheese": ("Queijo Curado do Esgoto", "Aged Sewer Cheese", "Queso Curado de la Alcantarilla"),
    "leshy_heartwood": ("Cerne do Leshy", "Leshy's Heartwood", "Corazón de Madera del Leshy"),
    "viper_fang": ("Presa da Rainha das Víboras", "Viper Queen's Fang", "Colmillo de la Reina Víbora"),
    "forbidden_grimoire": ("Grimório Proibido", "Forbidden Grimoire", "Grimorio Prohibido"),
    "pyre_ember": ("Brasa da Pira", "Pyre Ember", "Brasa de la Pira"),
    "alpha_fang": ("Presa do Alfa da Matilha", "Pack Alpha's Fang", "Colmillo del Alfa de la Manada"),
    "warden_key": ("Chave do Guardião do Cofre", "Vault Warden's Key", "Llave del Guardián de la Cámara"),
    "ruin_wine": ("Vinho dos Cofres", "Vault Wine", "Vino de las Cámaras"),
    "crypt_seal": ("Selo do Senhor da Cripta", "Crypt Lord's Seal", "Sello del Señor de la Cripta"),
    "ogre_club": ("Clava do Ogro da Cripta", "Crypt Ogre's Club", "Maza del Ogro de la Cripta"),
    "commander_sword": ("Espada do Comandante", "Commander's Sword", "Espada del Comandante"),
    "queen_ring": ("Anel da Rainha das Súcubas", "Succubus Queen's Ring", "Anillo de la Reina Súcubo"),
    "guardian_rune": ("Runa do Guardião do Túmulo", "Tomb Guardian's Rune", "Runa del Guardián de la Tumba"),
    "troll_tusk": ("Presa do Chefe Troll", "Troll Chief's Tusk", "Colmillo del Jefe Troll"),
    "blue_crystal": ("Cristal Azul da Mina", "Mine's Blue Crystal", "Cristal Azul de la Mina"),
    "gold_nugget": ("Pepita Real", "Royal Nugget", "Pepita Real"),
    "lamassu_horn": ("Chifre do Lamassu da Areia", "Sand Lamassu's Horn", "Cuerno del Lamasu de la Arena"),
    "queen_stinger": ("Ferrão da Rainha Escorpião", "Scorpion Queen's Stinger", "Aguijón de la Reina Escorpión"),
    "oasis_water": ("Frasco de Água do Oásis", "Oasis Water Flask", "Frasco de Agua del Oasis"),
    "golden_scarab": ("Escaravelho de Ouro", "Golden Scarab", "Escarabajo de Oro"),
}
# Cada mapa: a missão da cidade (quem pede, nome em pt/en/es, recompensa) e as 2 trocas (NPC do mapa, o chefe, item do chefe, item que o NPC devolve).
# "npc_room"/"near": onde pôr o NPC novo (sala e ponto desejado; o script acha um lugar livre perto).
CHAINS_DEF = [
    {"map": "sewers", "town_npc": "court_jester", "quest": "gifts_sewers", "name": ("Presentes do Esgoto", "Gifts from the Sewers", "Regalos de las Alcantarillas"),
     "reward": (240, 400), "label": ("o Esgoto", "the Sewers", "las Alcantarillas"),
     "pairs": [
         {"area": "sewers_01_drains", "npc": "sewer_scavenger", "boss": "old_gator", "take": "gator_tooth", "give": "sewer_pearl", "new": True,
          "name": ("Catador do Esgoto", "Sewer Scavenger", "Rebuscador de la Alcantarilla"), "near": [4, -3], "color": [0.4, 0.4, 0.3]},
         {"area": "sewers_02_canals", "npc": "sewer_ratcatcher", "boss": "frog_king", "take": "frog_crown", "give": "sewer_cheese", "new": True,
          "name": ("Caçador de Pragas", "Pest Hunter", "Cazador de Plagas"), "near": [4, 2], "color": [0.45, 0.35, 0.25]}]},
    {"map": "forest", "town_npc": "court_jester", "quest": "gifts_forest", "name": ("Presentes da Floresta", "Gifts from the Forest", "Regalos del Bosque"),
     "reward": (300, 500), "label": ("a Floresta", "the Forest", "el Bosque"),
     "pairs": [
         {"area": "forest_01_path", "npc": "forest_hermit", "boss": "leshy", "take": "leshy_heartwood", "give": "forbidden_grimoire", "new": False},
         {"area": "forest_01_path", "npc": "forest_pyre_keeper", "boss": "viper_queen", "take": "viper_fang", "give": "pyre_ember", "new": False}]},
    {"map": "ruins", "town_npc": "court_jester", "quest": "gifts_ruins", "name": ("Presentes das Ruínas", "Gifts from the Ruins", "Regalos de las Ruinas"),
     "reward": (360, 600), "label": ("as Ruínas", "the Ruins", "las Ruinas"),
     "pairs": [
         {"area": "ruins_01_city", "npc": "ruins_spartan", "boss": "ruin_alpha", "take": "alpha_fang", "give": "wild_meat", "new": False},
         {"area": "ruins_01_city", "npc": "ruins_scout", "boss": "ruin_warden", "take": "warden_key", "give": "ruin_wine", "new": True,
          "name": ("Batedor das Ruínas", "Ruins Scout", "Explorador de las Ruinas"), "near": [-18, -20], "color": [0.5, 0.42, 0.3]}]},
    {"map": "cemetery", "town_npc": "priest", "quest": "remains_cemetery", "name": ("Os restos do rei: coração e pulmões", "The King's Remains: Heart and Lungs", "Los restos del rey: corazón y pulmones"),
     "reward": (420, 750), "label": ("o Cemitério", "the Cemetery", "el Cementerio"),
     "pairs": [
         {"area": "cemetery_01_yard", "npc": "lightpost_statue", "boss": "crypt_lord", "take": "crypt_seal", "give": "human_heart", "new": False},
         {"area": "cemetery_01_yard", "npc": "cemetery_gravedigger", "boss": "crypt_scorpion", "take": "ogre_club", "give": "human_lungs", "new": True,
          "name": ("Coveiro", "Gravedigger", "Sepulturero"), "near": [8, 1], "color": [0.3, 0.3, 0.35]}]},
    {"map": "fort", "town_npc": "priest", "quest": "remains_fort", "name": ("Os restos do rei: crânio e alma", "The King's Remains: Skull and Soul", "Los restos del rey: cráneo y alma"),
     "reward": (600, 1000), "label": ("o Forte", "the Fort", "el Fuerte"),
     "pairs": [
         {"area": "fort_01_gate", "npc": "fort_penitent", "boss": "fort_commander", "take": "commander_sword", "give": "old_skull", "new": False},
         {"area": "fort_01_gate", "npc": "fort_exile", "boss": "succubus_queen", "take": "queen_ring", "give": "royal_soul", "new": False}]},
    {"map": "mine", "town_npc": "court_jester", "quest": "gifts_mine", "name": ("Presentes da Mina", "Gifts from the Mine", "Regalos de la Mina"),
     "reward": (480, 800), "label": ("a Mina", "the Mine", "la Mina"),
     "pairs": [
         {"area": "mine_01_crystal_vein", "npc": "mine_foreman", "boss": "tomb_guardian", "take": "guardian_rune", "give": "blue_crystal", "new": True,
          "name": ("Capataz da Mina", "Mine Foreman", "Capataz de la Mina"), "near": [6, -4], "color": [0.5, 0.4, 0.25]},
         {"area": "mine_01_crystal_vein", "npc": "mine_old_miner", "boss": "troll_chief", "take": "troll_tusk", "give": "gold_nugget", "new": True,
          "name": ("Velho Minerador", "Old Miner", "Viejo Minero"), "near": [20, -22], "color": [0.45, 0.45, 0.4]}]},
    {"map": "desert", "town_npc": "court_jester", "quest": "gifts_desert", "name": ("Presentes do Deserto", "Gifts from the Desert", "Regalos del Desierto"),
     "reward": (540, 900), "label": ("o Deserto", "the Desert", "el Desierto"),
     "pairs": [
         {"area": "desert_01_canyon", "npc": "desert_trader", "boss": "sand_lamassu", "take": "lamassu_horn", "give": "oasis_water", "new": True,
          "name": ("Mercador Nômade", "Nomad Trader", "Mercader Nómada"), "near": [6, -3], "color": [0.7, 0.55, 0.3]},
         {"area": "desert_01_canyon", "npc": "desert_guide", "boss": "queen_scorpion", "take": "queen_stinger", "give": "golden_scarab", "new": True,
          "name": ("Guia do Oásis", "Oasis Guide", "Guía del Oasis"), "near": [30, -24], "color": [0.6, 0.45, 0.3]}]},
]
# Quem na cidade pede: a ordem das missões de cada NPC (a conversa oferece uma por vez, na ordem)
TOWN_ORDER = {"court_jester": ["gifts_sewers", "gifts_forest", "gifts_ruins", "gifts_mine", "gifts_desert"], "priest": ["remains_cemetery", "remains_fort"]}

# Textos (pt, en, es); {A}/{B} etc. são trocados antes de gravar.
T_TOWN_ASK = ("Preciso de duas coisas d{article} {map}: {b1} e {b2}. Lá há dois que as têm, {npc1} e {npc2}, mas só trocam por algo que os chefes de lá guardam.",
              "I need two things from {map}: {b1} and {b2}. Two people there have them, {npc1} and {npc2}, but they only trade for something the bosses there keep.",
              "Necesito dos cosas de {map}: {b1} y {b2}. Dos personas allí las tienen, {npc1} y {npc2}, pero solo las cambian por algo que guardan los jefes de allí.")
T_TOWN_ASK2 = ("Falem com os dois, derrotem os chefes que eles apontarem e tragam {b1} e {b2} juntos: eu só pago com os dois na mão.",
               "Talk to both, defeat the bosses they point out and bring {b1} and {b2} together: I only pay with both in hand.",
               "Hablen con los dos, derroten a los jefes que señalen y traigan {b1} y {b2} juntos: solo pago con los dos en la mano.")
T_TOWN_ACTIVE = ("Ainda falta trazer {b1} e {b2}. Os dois vêm das trocas com {npc1} e {npc2}.",
                 "I still need {b1} and {b2}. Both come from the trades with {npc1} and {npc2}.",
                 "Aún faltan {b1} y {b2}. Ambos salen de los trueques con {npc1} y {npc2}.")
T_TOWN_DESC = ("Entregue {b1} e {b2} a {town}: os dois itens saem das trocas com {npc1} e {npc2} em {map}, que pedem algo dos chefes {boss1} e {boss2}.",
               "Hand {b1} and {b2} to {town}: both items come from the trades with {npc1} and {npc2} in {map}, who ask for something from the bosses {boss1} and {boss2}.",
               "Entrega {b1} y {b2} a {town}: ambos objetos salen de los trueques con {npc1} y {npc2} en {map}, que piden algo de los jefes {boss1} y {boss2}.")
T_MAP_NAME = ("A troca de {npc}", "{npc}'s Trade", "El trueque de {npc}")
T_MAP_DESC = ("{npc} só dá {give} em troca de {take}, que {boss} guarda. Derrote {boss} e leve {take} a {npc}.",
              "{npc} only gives {give} in exchange for {take}, which {boss} keeps. Defeat {boss} and bring {take} to {npc}.",
              "{npc} solo da {give} a cambio de {take}, que guarda {boss}. Derrota a {boss} y lleva {take} a {npc}.")
T_MAP_1 = ("Tenho {give}, mas ando sem nada para trocar. Só o dou por {take}.", "I have {give}, but nothing to trade. I only give it for {take}.", "Tengo {give}, pero nada que intercambiar. Solo lo doy por {take}.")
T_MAP_2 = ("{take} está com {boss}, lá longe. Derrote-o e traga: a troca é justa.", "{take} is with {boss}, far from here. Defeat them and bring it: the trade is fair.", "{take} está con {boss}, lejos de aquí. Derrótalo y tráelo: el trueque es justo.")
T_MAP_ACTIVE = ("Ainda quero {take}. {boss} o carrega, bem longe daqui.", "I still want {take}. {boss} carries it, far from here.", "Aún quiero {take}. {boss} lo lleva, lejos de aquí.")
T_MAP_IDLE = ("Não tenho nada para trocar agora.", "I have nothing to trade right now.", "No tengo nada que intercambiar ahora.")


def L(p):
    return open(p, encoding="utf-8").read()


def W(p, d):
    s = json.dumps(d, indent=2, ensure_ascii=False) + "\n"
    open(p, "w", encoding="utf-8").write(s)


arenas, monsters, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, MONSTERS, NPCS, QUESTS, VALUABLES))
po = {lang: L("locale/%s.po" % lang) for lang in LANGS}


def tr(lang, key):
    m = re.search(r'msgid "%s"\nmsgstr "([^\n]*)"' % re.escape(key), po[lang])
    return m.group(1) if m else key


texts = {}  # key -> (pt, en, es)


def put_text(key, trio):
    texts[key] = tuple(trio)


def fmt(template, i, **kw):
    return template[i].format(**kw)


def item_name(item, i):
    return ITEM_NAMES[item][i] if item in ITEM_NAMES else tr(LANGS[i], valuables[item]["name_key"])


def monster_name(boss, i):
    return tr(LANGS[i], monsters[boss]["name_key"])


def npc_name(pair, i):
    return pair["name"][i] if pair["new"] else tr(LANGS[i], npcs[pair["npc"]]["name_key"])


def free_spot(area_id, target, boss_pos):
    """Um lugar livre (dentro de uma sala, longe de encontros e de peças com colisão) o mais perto possível do alvo e longe do chefe."""
    a = arenas[area_id]
    rooms = a["rooms"]
    avoid = [e["position"] for e in a["encounters"]]
    solid = [d["position"] for d in a["decor"] if d.get("solid") and "position" in d]
    best, best_d = None, 1e9
    for r in rooms:
        cx, cz = r["center"]
        w, h = r["size"]
        for ix in range(-int(w / 2) + 2, int(w / 2) - 1, 2):
            for iz in range(-int(h / 2) + 2, int(h / 2) - 1, 2):
                x, z = cx + ix, cz + iz
                if any(math.hypot(x - ax, z - az) < 6 for ax, az in avoid) or any(math.hypot(x - sx, z - sz) < 2.5 for sx, sz in solid):
                    continue
                d = math.hypot(x - target[0], z - target[1])
                if d < best_d and math.hypot(x - boss_pos[0], z - boss_pos[1]) > 18:
                    best, best_d = (x, z), d
    return [round(best[0], 1), round(best[1], 1)] if best else list(target)


def boss_position(boss):
    for a in arenas.values():
        if not isinstance(a, dict):
            continue
        for e in a.get("encounters", []):
            if any(m["monster"] == boss for m in e["monsters"]):
                return e["position"]
        for p in a.get("props", []):
            if "summon" in p and any(m["monster"] == boss for m in p["summon"]["monsters"]):
                return p["summon"]["position"]
    return [0, 0]


chains_out = {}
for ch in CHAINS_DEF:
    town = ch["town_npc"]
    q_town = ch["quest"]
    items = [p["give"] for p in ch["pairs"]]
    npc_names = [npc_name(p, 0) for p in ch["pairs"]]
    # --- itens de missão
    for p in ch["pairs"]:
        for item in (p["take"], p["give"]):
            if item in ITEM_NAMES and item not in EXISTING_ITEMS:
                valuables[item] = {"name_key": "VALUABLE_" + item.upper(), "value": 0, "maps": [], "quest_item": True} | ({"model": valuables[item]["model"]} if item in valuables and "model" in valuables[item] else {})
                put_text("VALUABLE_" + item.upper(), ITEM_NAMES[item])
    # --- NPCs e posições
    for n, p in enumerate(ch["pairs"]):
        a = arenas[p["area"]]
        if p["new"]:
            npcs[p["npc"]] = {"name_key": "NPC_" + p["npc"].upper(), "color": p["color"], "dialogues": [],
                              "body": {"sex": "male" if n == 0 else "female", "hair": ["Hair_SimpleParted"], "hair_color": [0.25, 0.17, 0.1], "pose": "idle", "outfit": {"body": "cloth"}}}
            put_text("NPC_" + p["npc"].upper(), p["name"])
            pos = free_spot(p["area"], p["near"], boss_position(p["boss"]))
            a["props"] = [x for x in a["props"] if x["id"] != p["npc"]] + [{"id": p["npc"], "kind": "npc", "npc": p["npc"], "position": pos, "rotation": 0}]
        else:
            for prop in a["props"]:
                if prop.get("npc") == p["npc"]:
                    prop.pop("summon", None)  # o chefe não é mais despertado pelo NPC: ele está no mapa, longe, e o NPC pede o item dele
    # --- missões do mapa (trocas) e conversas dos NPCs
    for n, p in enumerate(ch["pairs"]):
        qid = "trade_%s" % p["npc"]
        pn = [npc_name(p, i) for i in range(3)]
        bn = [monster_name(p["boss"], i) for i in range(3)]
        tk = [item_name(p["take"], i) for i in range(3)]
        gv = [item_name(p["give"], i) for i in range(3)]
        quests[qid] = {"name_key": "QUEST_" + qid.upper(), "desc_key": "QUEST_%s_DESC" % qid.upper(), "type": "main", "giver": p["npc"], "area": p["area"], "item": p["take"],
                       "gives": p["give"], "requires": q_town, "reward": {"gold": 0, "xp": 60 + 20 * len(CHAINS_DEF)}}
        put_text("QUEST_" + qid.upper(), tuple(fmt(T_MAP_NAME, i, npc=pn[i]) for i in range(3)))
        put_text("QUEST_%s_DESC" % qid.upper(), tuple(fmt(T_MAP_DESC, i, npc=pn[i], give=gv[i], take=tk[i], boss=bn[i]) for i in range(3)))
        for k, T in (("1", T_MAP_1), ("2", T_MAP_2), ("ACTIVE", T_MAP_ACTIVE)):
            put_text("DLG_%s_%s" % (qid.upper(), k), tuple(fmt(T, i, give=gv[i], take=tk[i], boss=bn[i]) for i in range(3)))
        put_text("DLG_%s_IDLE" % qid.upper(), T_MAP_IDLE)
        # os dois NPCs de um mapa podem ter outras conversas antes (ex.: a estátua do Cemitério); a troca vem na frente
        old = [d for d in npcs[p["npc"]].get("dialogues", []) if not str(d.get("offer", "")).startswith("trade_") and "trade_" not in json.dumps(d.get("when", {}))]
        # as falas antigas deste NPC (missões velhas) saem: ficam só a troca e a fala de espera
        npcs[p["npc"]]["dialogues"] = [
            {"when": {"quest_new": qid, "requires": q_town}, "lines": ["DLG_%s_1" % qid.upper(), "DLG_%s_2" % qid.upper()], "offer": qid},
            {"when": {"quest_active": qid}, "lines": ["DLG_%s_ACTIVE" % qid.upper()], "service": "turn_in"},
            {"when": {}, "lines": ["DLG_%s_IDLE" % qid.upper()]}]
        # o chefe larga o item do mapa
        monsters[p["boss"]]["quest_drop"] = p["take"]
    # --- missão da cidade (pede os 2 itens)
    b = [[item_name(it, i) for i in range(3)] for it in items]
    boss_names = [[monster_name(p["boss"], i) for i in range(3)] for p in ch["pairs"]]
    town_name = [tr(LANGS[i], npcs[town]["name_key"]) for i in range(3)]
    label = ch["label"]
    art_pt = "a" if label[0].startswith("a ") else "o"
    quests[q_town] = {"name_key": "QUEST_" + q_town.upper(), "desc_key": "QUEST_%s_DESC" % q_town.upper(), "type": "main", "giver": town, "area": ch["pairs"][0]["area"], "items": items,
                      "reward": {"gold": ch["reward"][0], "xp": ch["reward"][1]}}
    put_text("QUEST_" + q_town.upper(), ch["name"])
    put_text("QUEST_%s_DESC" % q_town.upper(), tuple(fmt(T_TOWN_DESC, i, b1=b[0][i], b2=b[1][i], town=town_name[i], npc1=npc_name(ch["pairs"][0], i), npc2=npc_name(ch["pairs"][1], i),
                                                       map=label[i], boss1=boss_names[0][i], boss2=boss_names[1][i]) for i in range(3)))
    art = [("d" + ("a" if label[0].split()[0] == "a" else "o")), "", ""]
    put_text("DLG_%s_ASK_1" % q_town.upper(), tuple(fmt(T_TOWN_ASK, i, article=art[0][1:] if i == 0 else "", map=label[i].split(" ", 1)[1] if i == 0 else label[i], b1=b[0][i], b2=b[1][i],
                                                       npc1=npc_name(ch["pairs"][0], i), npc2=npc_name(ch["pairs"][1], i)).replace(" da ", " da ") for i in range(3)))
    put_text("DLG_%s_ASK_2" % q_town.upper(), tuple(fmt(T_TOWN_ASK2, i, b1=b[0][i], b2=b[1][i]) for i in range(3)))
    put_text("DLG_%s_ACTIVE" % q_town.upper(), tuple(fmt(T_TOWN_ACTIVE, i, b1=b[0][i], b2=b[1][i], npc1=npc_name(ch["pairs"][0], i), npc2=npc_name(ch["pairs"][1], i)) for i in range(3)))
    chains_out[ch["map"]] = {"town_npc": town, "town_quest": q_town, "areas": sorted({p["area"] for p in ch["pairs"]}),
                             "pairs": [{"npc": p["npc"], "boss": p["boss"], "quest": "trade_" + p["npc"], "take": p["take"], "give": p["give"], "area": p["area"]} for p in ch["pairs"]]}

# --- conversas dos NPCs da cidade (uma missão por vez, na ordem); a primeira conversa do Padre e a do Bobo mantêm a saudação
for town, order in TOWN_ORDER.items():
    dialogues = []
    for k, q_town in enumerate(order):
        lines = ["DLG_%s_ASK_1" % q_town.upper(), "DLG_%s_ASK_2" % q_town.upper()]
        if k == 0 and town == "priest":
            lines = ["DLG_PRIEST_1", "DLG_PRIEST_2"] + lines
        if k == 0 and town == "court_jester":
            lines = ["DLG_JESTER_1", "DLG_JESTER_2"] + lines
        dialogues += [{"when": {"quest_new": q_town}, "lines": lines, "offer": q_town},
                      {"when": {"quest_active": q_town}, "lines": ["DLG_%s_ACTIVE" % q_town.upper()], "service": "turn_in"}]
    dialogues.append({"when": {}, "lines": ["DLG_PRIEST_DONE"] if town == "priest" else ["DLG_JESTER_BANQUET_DONE", "DLG_JESTER_3"]})
    npcs[town]["dialogues"] = dialogues
# missões velhas de um item só e as dos golens invocados saem
for old in ("royal_heart", "royal_lungs", "royal_skull", "royal_soul", "royal_banquet", "forest_stone_golem", "forest_fire_golem"):
    quests.pop(old, None)
for m in monsters.values():
    pass
# o drop antigo de relíquia solta cedeu lugar ao do item do mapa (acima); os chefes sem troca não largam nada
trade_bosses = {p["boss"] for ch in CHAINS_DEF for p in ch["pairs"]}
for mid, m in monsters.items():
    if isinstance(m, dict) and m.get("quest_drop") and mid not in trade_bosses:
        m.pop("quest_drop")
W(ARENAS, arenas)
W(MONSTERS, monsters)
W(NPCS, npcs)
W(QUESTS, quests)
W(VALUABLES, valuables)
W(CHAINS, chains_out)
# --- locale
for i, lang in enumerate(LANGS + ("messages",)):
    path = "locale/%s.pot" % lang if lang == "messages" else "locale/%s.po" % lang
    t = L(path)
    add = ""
    for key, trio in texts.items():
        val = "" if lang == "messages" else trio[i].replace('"', '\\"')
        if re.search(r'msgid "%s"\n' % re.escape(key), t):
            if lang != "messages":
                t = re.sub(r'(msgid "%s"\nmsgstr )"[^\n]*"' % re.escape(key), lambda m: m.group(1) + '"' + val + '"', t)
        else:
            add += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, val)
    open(path, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + add)
print("OK cadeias:", {k: [p["npc"] + "<-" + p["boss"] for p in v["pairs"]] for k, v in chains_out.items()})
