"""O Cemitério ganha a estrutura de missões dos outros mapas (ver tools/assets/build_map_mechanics.py, que põe os livros e o altar):
  dois moradores com missão (o Coveiro pede os Pulmões Humanos do Ogro da Cripta; a Zeladora, a Lamparina do Sentinela do Túmulo), o Guardião da Cripta com o portão do Senhor da Cripta,
  e o Senhor da Cripta como chefe do mapa (final). Os dois mini-chefes passam a ser despertados no altar único (a estátua do poste de luz): o Ogro da Cripta deixa de ficar solto na praça.
  A missão `royal_lungs` do Padre vira a missão do Coveiro. Idempotente; chamado antes de build_map_mechanics.py.
uso: python3 tools/assets/build_cemetery_quests.py   (a partir da raiz do projeto)"""
import json, re
ARENAS, NPCS, QUESTS, VALUABLES, MONSTERS = "data/arenas.json", "data/npcs.json", "data/quests.json", "data/valuables.json", "data/monsters.json"
arenas, npcs, quests, valuables, monsters = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, NPCS, QUESTS, VALUABLES, MONSTERS))
AREA = "cemetery_01_yard"
cem = arenas[AREA]
T = {}


def free_spot(arena, around, radius=3.0):
    things = [d["position"] for d in arena["decor"] if "position" in d and ("solid" in d or "collider" in d)] + [p["position"] for p in arena["props"] if "position" in p]
    for r in (0, 3, 6, 9, 12):
        for dx, dz in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, r), (r, -r), (-r, -r)):
            x, z = around[0] + dx, around[1] + dz
            if all(((x - a) ** 2 + (z - b) ** 2) ** 0.5 > radius for a, b in things):
                return [round(x, 1), round(z, 1)]
    return list(around)


def put_prop(prop):
    cem["props"] = [p for p in cem["props"] if p["id"] != prop["id"]] + [prop]


def body(sex, hair, color):
    return {"sex": sex, "hair": [hair] if isinstance(hair, str) else hair, "hair_color": color, "pose": "idle", "outfit": {"body": "cloth"}}


def dlg(prefix, qid):
    return [{"when": {"quest_new": qid}, "lines": ["DLG_%s_1" % prefix, "DLG_%s_2" % prefix, "DLG_%s_3" % prefix], "offer": qid},
            {"when": {"quest_active": qid}, "lines": ["DLG_%s_ACTIVE" % prefix], "service": "turn_in"}, {"when": {}, "lines": ["DLG_%s_DONE" % prefix]}]


# ---------------------------------------------------------------- itens
valuables["warden_lantern"] = {"name_key": "VALUABLE_WARDEN_LANTERN", "desc_key": "VALUABLE_WARDEN_LANTERN_DESC", "value": 0, "maps": [], "quest_item": True, "model": "Tv_Lamp"}
valuables["key_ossuary"] = {"name_key": "VALUABLE_KEY_OSSUARY", "desc_key": "VALUABLE_KEY_OSSUARY_DESC", "value": 0, "maps": [], "quest_item": True, "model": "Key_Spades"}
valuables["key_crypt"] = {"name_key": "VALUABLE_KEY_CRYPT", "desc_key": "VALUABLE_KEY_CRYPT_DESC", "value": 0, "maps": [], "quest_item": True, "model": "Key_Clubs"}
T["VALUABLE_WARDEN_LANTERN"] = ("Lamparina do Sentinela", "Sentinel's Lantern", "Linterna del Centinela")
T["VALUABLE_WARDEN_LANTERN_DESC"] = ("Largada pelo Sentinela do Túmulo. Não pode ser vendida nem perdida: leve-a à Zeladora.", "Dropped by the Tomb Sentinel. It cannot be sold or lost: take it to the Caretaker.", "Soltada por el Centinela de la Tumba. No se puede vender ni perder: llévala a la Cuidadora.")
T["VALUABLE_KEY_OSSUARY"] = ("Chave do Ossuário", "Ossuary Key", "Llave del Osario")
T["VALUABLE_KEY_OSSUARY_DESC"] = ("Entregue pelo Coveiro. O Guardião da Cripta a pede, com a outra chave, para abrir o portão do Senhor da Cripta.", "Given by the Gravedigger. The Crypt Guardian asks for it, with the other key, to open the Crypt Lord's gate.", "Entregada por el Sepulturero. El Guardián de la Cripta la pide, con la otra llave, para abrir el portón del Señor de la Cripta.")
T["VALUABLE_KEY_CRYPT"] = ("Chave da Cripta", "Crypt Key", "Llave de la Cripta")
T["VALUABLE_KEY_CRYPT_DESC"] = ("Entregue pela Zeladora. O Guardião da Cripta a pede, com a outra chave, para abrir o portão do Senhor da Cripta.", "Given by the Caretaker. The Crypt Guardian asks for it, with the other key, to open the Crypt Lord's gate.", "Entregada por la Cuidadora. El Guardián de la Cripta la pide, con la otra llave, para abrir el portón del Señor de la Cripta.")
# ---------------------------------------------------------------- NPCs
npcs["ce_gravedigger"] = {"name_key": "NPC_CE_GRAVEDIGGER", "color": [0.4, 0.35, 0.3], "dialogues": dlg("CEGRAVE", "ce_lungs"), "body": body("male", "Hair_Buzzed", [0.3, 0.25, 0.2])}
npcs["ce_caretaker"] = {"name_key": "NPC_CE_CARETAKER", "color": [0.45, 0.4, 0.5], "dialogues": dlg("CECARE", "ce_lantern"), "body": body("female", "Hair_Long", [0.2, 0.2, 0.25])}
npcs["ce_warden"] = {"name_key": "NPC_CE_WARDEN", "color": [0.35, 0.35, 0.4], "dialogues": dlg("CEWARD", "ce_gate"), "body": body("male", "Hair_Beard", [0.5, 0.5, 0.5])}
T.update({
    "NPC_CE_GRAVEDIGGER": ("Coveiro Abel", "Gravedigger Abel", "Sepulturero Abel"), "NPC_CE_CARETAKER": ("Zeladora Mirta", "Caretaker Mirta", "Cuidadora Mirta"), "NPC_CE_WARDEN": ("Guardião da Cripta", "Crypt Guardian", "Guardián de la Cripta"),
    "QUEST_CE_LUNGS": ("Os Pulmões do Coveiro", "The Gravedigger's Lungs", "Los pulmones del Sepulturero"),
    "QUEST_CE_LUNGS_DESC": ("O Coveiro Abel quer os Pulmões Humanos que o Ogro da Cripta carrega. Pegue o livro com ele, desperte o Ogro no altar da alameda e traga os pulmões; ele entrega a Chave do Ossuário.",
                            "Gravedigger Abel wants the Human Lungs the Crypt Ogre carries. Take his book, wake the Ogre at the avenue altar and bring the lungs; he hands over the Ossuary Key.",
                            "El Sepulturero Abel quiere los Pulmones Humanos que lleva el Ogro de la Cripta. Toma su libro, despierta al Ogro en el altar de la alameda y trae los pulmones; él entrega la Llave del Osario."),
    "QUEST_CE_LANTERN": ("A Lamparina do Sentinela", "The Sentinel's Lantern", "La linterna del Centinela"),
    "QUEST_CE_LANTERN_DESC": ("A Zeladora Mirta quer a Lamparina que o Sentinela do Túmulo guarda. Pegue o livro com ela, desperte o Sentinela no altar da alameda e traga a lamparina; ela entrega a Chave da Cripta.",
                              "Caretaker Mirta wants the Lantern the Tomb Sentinel keeps. Take her book, wake the Sentinel at the avenue altar and bring the lantern; she hands over the Crypt Key.",
                              "La Cuidadora Mirta quiere la Linterna que guarda el Centinela de la Tumba. Toma su libro, despierta al Centinela en el altar de la alameda y trae la linterna; ella entrega la Llave de la Cripta."),
    "QUEST_CE_GATE": ("O Portão da Cripta", "The Crypt Gate", "El portón de la cripta"),
    "QUEST_CE_GATE_DESC": ("O Guardião da Cripta só abre o portão do Senhor da Cripta para quem lhe entregar a Chave do Ossuário e a Chave da Cripta.", "The Crypt Guardian only opens the Crypt Lord's gate for those who hand him the Ossuary Key and the Crypt Key.", "El Guardián de la Cripta solo abre el portón del Señor de la Cripta a quien le entregue la Llave del Osario y la Llave de la Cripta."),
    "DLG_CEGRAVE_1": ("Cavo covas há quarenta anos e nunca enterrei um defunto tão teimoso quanto o Ogro da Cripta. Ele ficou com os pulmões de quem não devia.", "I have dug graves for forty years and never buried a corpse as stubborn as the Crypt Ogre. He kept the lungs of someone he should not have.", "Cavo tumbas hace cuarenta años y nunca enterré a un muerto tan terco como el Ogro de la Cripta. Se quedó con los pulmones de quien no debía."),
    "DLG_CEGRAVE_2": ("Se trouxerem os Pulmões Humanos de volta, eu lhes dou a chave do ossuário. O Ogro só desperta no altar da alameda, com o livro certo.", "If you bring the Human Lungs back, I will give you the ossuary key. The Ogre only wakes at the avenue altar, with the right book.", "Si traen de vuelta los Pulmones Humanos, les doy la llave del osario. El Ogro solo despierta en el altar de la alameda, con el libro correcto."),
    "DLG_CEGRAVE_3": ("Cuidado com a clava dele: já abriu mais covas do que eu.", "Watch his club: it has opened more graves than I have.", "Cuidado con su maza: ha abierto más tumbas que yo."),
    "DLG_CEGRAVE_ACTIVE": ("Os pulmões ainda estão com o Ogro, no altar da alameda. Sem eles, a chave do ossuário fica comigo.", "The lungs are still with the Ogre, at the avenue altar. Without them, the ossuary key stays with me.", "Los pulmones siguen con el Ogro, en el altar de la alameda. Sin ellos, la llave del osario se queda conmigo."),
    "DLG_CEGRAVE_DONE": ("Descansem, valentes. Aquele pobre rei vai respirar em paz, onde estiver.", "Rest, brave ones. That poor king will breathe in peace, wherever he is.", "Descansen, valientes. Ese pobre rey respirará en paz, donde esté."),
    "DLG_CECARE_1": ("Acendo as lamparinas deste cemitério há tanto tempo que perdi a conta. A última, a mais velha, o Sentinela do Túmulo tomou para si.", "I have lit this cemetery's lanterns for so long I lost count. The last and oldest one, the Tomb Sentinel took for himself.", "Enciendo las linternas de este cementerio desde hace tanto que perdí la cuenta. La última, la más vieja, el Centinela de la Tumba la tomó para sí."),
    "DLG_CECARE_2": ("Tragam-na de volta e eu lhes entrego a chave da cripta. O Sentinela mora na estátua do altar da alameda: só o livro que lhes dou o desperta.", "Bring it back and I will hand you the crypt key. The Sentinel dwells in the avenue altar's statue: only the book I give you wakes him.", "Tráiganla de vuelta y les entrego la llave de la cripta. El Centinela mora en la estatua del altar de la alameda: solo el libro que les doy lo despierta."),
    "DLG_CECARE_3": ("Ele é de pedra, mas guarda rancor como gente.", "He is made of stone, but holds a grudge like a person.", "Es de piedra, pero guarda rencor como una persona."),
    "DLG_CECARE_ACTIVE": ("A lamparina continua com o Sentinela. Sem ela, a chave da cripta fica comigo.", "The lantern is still with the Sentinel. Without it, the crypt key stays with me.", "La linterna sigue con el Centinela. Sin ella, la llave de la cripta se queda conmigo."),
    "DLG_CECARE_DONE": ("A luz voltou à alameda. Os mortos agradecem, à maneira deles.", "The light is back on the avenue. The dead are grateful, in their way.", "La luz volvió a la alameda. Los muertos lo agradecen, a su manera."),
    "DLG_CEWARD_1": ("O Senhor da Cripta dorme atrás deste portão, e eu cuido para que ninguém o incomode sem merecer.", "The Crypt Lord sleeps behind this gate, and I make sure no one disturbs him without deserving it.", "El Señor de la Cripta duerme tras este portón, y yo cuido de que nadie lo moleste sin merecerlo."),
    "DLG_CEWARD_2": ("Quem me trouxer a Chave do Ossuário, do Coveiro, e a Chave da Cripta, da Zeladora, passa. Só os dois juntos abrem o portão.", "Whoever brings me the Ossuary Key, from the Gravedigger, and the Crypt Key, from the Caretaker, may pass. Only the two together open the gate.", "Quien me traiga la Llave del Osario, del Sepulturero, y la Llave de la Cripta, de la Cuidadora, pasa. Solo las dos juntas abren el portón."),
    "DLG_CEWARD_3": ("Os mini-chefes esperam no altar da alameda. Sem eles, não há chaves.", "The mini-bosses wait at the avenue altar. Without them, there are no keys.", "Los minijefes esperan en el altar de la alameda. Sin ellos, no hay llaves."),
    "DLG_CEWARD_ACTIVE": ("Ainda faltam chaves. Falem com o Coveiro e com a Zeladora.", "Keys are still missing. Speak with the Gravedigger and the Caretaker.", "Aún faltan llaves. Hablen con el Sepulturero y con la Cuidadora."),
    "DLG_CEWARD_DONE": ("O portão está aberto. Que o Senhor da Cripta os encontre prontos.", "The gate is open. May the Crypt Lord find you ready.", "El portón está abierto. Que el Señor de la Cripta los encuentre listos."),
})
# ---------------------------------------------------------------- missões
quests["ce_lungs"] = {"name_key": "QUEST_CE_LUNGS", "desc_key": "QUEST_CE_LUNGS_DESC", "type": "village", "giver": "ce_gravedigger", "area": AREA, "item": "human_lungs", "gives": "key_ossuary",
                      "target_element": "earth", "reward": {"gold": 180, "xp": 300}}
quests["ce_lantern"] = {"name_key": "QUEST_CE_LANTERN", "desc_key": "QUEST_CE_LANTERN_DESC", "type": "village", "giver": "ce_caretaker", "area": AREA, "item": "warden_lantern", "gives": "key_crypt",
                        "target_element": "earth", "reward": {"gold": 200, "xp": 350}}
quests["ce_gate"] = {"name_key": "QUEST_CE_GATE", "desc_key": "QUEST_CE_GATE_DESC", "type": "village", "giver": "ce_warden", "area": AREA, "items": ["key_ossuary", "key_crypt"], "opens_gate": "boss_gate",
                     "target_element": "earth", "reward": {"gold": 300, "xp": 600}}
quests.pop("royal_lungs", None)  # a missão do Padre virou a do Coveiro (o chefe do mapa é quem larga o item da cidade)
npcs["priest"]["dialogues"] = [d for d in npcs["priest"]["dialogues"] if "royal_lungs" not in json.dumps(d.get("when", {})) and d.get("offer") != "royal_lungs"]
# ---------------------------------------------------------------- mini-chefes: um altar só (o Ogro da Cripta sai da praça)
monsters["ce_warden"]["quest_drop"] = "warden_lantern"
scorpion = next(e for e in cem["encounters"] if e["id"] == "c_plaza_a")
cem["encounters"] = [e for e in cem["encounters"] if e["id"] != "c_plaza_a"]
lamp = next(p for p in cem["props"] if p["id"] == "lamp_statue")
if lamp.get("summon"):
    group = lamp["summon"]
    if not any(e["summon"]["id"] == "ce_crypt_ogre" for e in lamp.get("extra_summons", [])):
        lamp["extra_summons"] = [{"needs_key": "x", "dialogue": 2, "summon": {"id": "ce_crypt_ogre", "position": list(group["position"]), "level": group.get("level", 1), "toast": group.get("toast", ""),
                                                                              "monsters": [{"monster": "crypt_scorpion", "count": 1}]}}]
# ---------------------------------------------------------------- moradores, guardião, portão e vitória
put_prop({"id": "ce_gravedigger", "kind": "npc", "npc": "ce_gravedigger", "position": free_spot(cem, [8.0, -14.0]), "rotation": 200})
put_prop({"id": "ce_caretaker", "kind": "npc", "npc": "ce_caretaker", "position": free_spot(cem, [-8.0, -52.0]), "rotation": 160})
put_prop({"id": "boss_gate", "kind": "gate", "name_key": "PROP_BOSS_GATE", "position": [-80.0, -150.5], "rotation": 0, "scale": 3.0, "block": 12.0, "count": 2, "opened_by": "ce_gate"})
put_prop({"id": "ce_warden", "kind": "npc", "npc": "ce_warden", "position": [-80.0, -147.0], "rotation": 0})
cem["final"] = True
cem["victory_groups"] = ["c_boss"]
for path_i, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po", "locale/messages.pot")):
    t = open(path, encoding="utf-8").read()
    add = ""
    for key, trio in T.items():
        val = "" if path.endswith(".pot") else trio[path_i].replace("\\", "\\\\").replace('"', '\\"')
        if re.search(r'msgid "%s"\n' % re.escape(key), t):
            if val:
                t = re.sub(r'(msgid "%s"\nmsgstr )"[^\n]*"' % re.escape(key), lambda m: m.group(1) + '"' + val.replace("\\", "\\\\") + '"', t)
        else:
            add += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, val)
    open(path, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + add)
try:
    from PIL import Image
    for dst, src, mul in (("key_ossuary", "key_iron", (1.0, 1.0, 1.0)), ("key_crypt", "key_bone", (1.0, 1.0, 1.0)), ("warden_lantern", "old_skull", (0.8, 1.0, 1.4))):
        im = Image.open("assets/ui/icons/%s.png" % src).convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", tuple(c.point(lambda v, m=m: min(255, int(v * m))) for c, m in zip((r_, g_, b_), mul)) + (a_,)).save("assets/ui/icons/%s.png" % dst)
except Exception as exc:
    print("aviso: ícones não gerados:", exc)
for path, data in ((ARENAS, arenas), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables), (MONSTERS, monsters)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK cemitério: moradores, portão, guardião e vitória")
