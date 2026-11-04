"""A mecânica de missões do Esgoto aplicada a todos os mapas (docs/04-tortuga-e-missoes.md):
  1. O NPC da cidade passa a missão e pede um item que só o chefe do mapa larga; a recompensa é em ouro.
  2. Dois NPCs do mapa dão uma missão cada: entregam um LIVRO, pedem o item de um mini-chefe e, ao receber o item, entregam uma CHAVE.
  3. Há UM só altar por mapa: o livro que o grupo tem decide qual mini-chefe desperta (`needs_key` + `extra_summons`, como o altar do Esgoto).
  4. O guardião pede as duas chaves e abre o portão do chefe.
  5. O chefe do mapa larga o tesouro (baú do chefe) e o item que o NPC da cidade pediu.
  O livro some da bolsa de todos quando o mini-chefe cai (prototype_arena._consume_books).
Mapas tratados: Cemitério (estrutura montada antes por build_cemetery_quests.py), Floresta, Ruínas, Forte, Catacumbas, Deserto, Docas, Mina, Bunker, Floresta Escura (o Esgoto é o modelo).
Chamado em tools/assets/build_maps.py depois de build_city_quests.py; idempotente.
uso: python3 tools/assets/build_map_mechanics.py   (a partir da raiz do projeto)"""
import json, re
ARENAS, NPCS, QUESTS, VALUABLES, MONSTERS = "data/arenas.json", "data/npcs.json", "data/quests.json", "data/valuables.json", "data/monsters.json"
arenas, npcs, quests, valuables, monsters = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, NPCS, QUESTS, VALUABLES, MONSTERS))
LANGS = ("pt_BR", "en", "es")


def load_po(lang):
    out = {}
    for m in re.finditer(r'msgid "([^"\n]+)"\nmsgstr "([^"\n]*)"', open("locale/%s.po" % lang, encoding="utf-8").read()):
        out[m.group(1)] = m.group(2).replace('\\"', '"')
    return out


PO = [load_po(l) for l in LANGS]


def name(key, i):
    return PO[i].get(key) or key


# tag: (área, nome do altar, [livro 1, livro 2] (pt, en, es), item do chefe (id, nomes, modelo, ícone-base, tinta) ou None, missão da cidade)
MAPS = {
    "cemetery": ("cemetery_01_yard", ("Altar da Alameda", "Avenue Altar", "Altar de la Alameda"),
                 (("Rol do Coveiro", "Gravedigger's Roll", "Rol del Sepulturero"), ("Registro da Zeladora", "Caretaker's Register", "Registro de la Cuidadora")), None, "royal_heart"),
    "forest": ("forest_01_path", ("Altar do Velho Carvalho", "Old Oak Altar", "Altar del Viejo Roble"),
               (("Mapa de Trilhas da Exploradora", "Explorer's Trail Map", "Mapa de Sendas de la Exploradora"), ("Cinzas da Pira", "Pyre Ashes", "Cenizas de la Pira")), None, "forest_treasure"),
    "ruins": ("ruins_01_city", ("Altar do Reino Caído", "Altar of the Fallen Kingdom", "Altar del Reino Caído"),
              (("Códice do Erudito", "Scholar's Codex", "Códice del Erudito"), ("Prece da Sacerdotisa", "Priestess's Prayer", "Oración de la Sacerdotisa")),
              ("fallen_crown", ("Coroa do Rei Caído", "Fallen King's Crown", "Corona del Rey Caído"), "Coin_Gold", "queen_ring", (1.4, 1.2, 0.5)), "map_ruins"),
    "fort": ("fort_01_gate", ("Altar das Muralhas", "Altar of the Ramparts", "Altar de las Murallas"),
             (("Pacto do Exilado", "Exile's Pact", "Pacto del Exiliado"), ("Rosário da Penitente", "Penitent's Rosary", "Rosario de la Penitente")), None, "royal_skull"),
    "catacombs": ("catacombs_01_depths", ("Altar dos Condenados", "Altar of the Condemned", "Altar de los Condenados"),
                  (("Registro do Carcereiro", "Jailer's Ledger", "Registro del Carcelero"), ("Lamento do Prisioneiro", "Prisoner's Lament", "Lamento del Prisionero")),
                  ("chained_link", ("Elo do Rei Acorrentado", "Chained King's Link", "Eslabón del Rey Encadenado"), "Dungeon_Bone", "soul_shackle", (0.8, 0.9, 1.3)), "map_catacombs"),
    "desert": ("desert_01_canyon", ("Altar das Areias", "Altar of the Sands", "Altar de las Arenas"),
               (("Papiro do Nômade", "Nomad's Papyrus", "Papiro del Nómada"), ("Tábua do Oásis", "Oasis Tablet", "Tablilla del Oasis")),
               ("sphinx_eye", ("Olho da Esfinge", "Sphinx's Eye", "Ojo de la Esfinge"), "Crystal_Gem", "golden_scarab", (1.2, 1.0, 0.6)), "map_desert"),
    "docks": ("docks_01_pier", ("Altar do Cais", "Pier Altar", "Altar del Muelle"),
              (("Diário do Mestre do Cais", "Dock Master's Log", "Diario del Maestro del Muelle"), ("Receita da Peixeira", "Fishwife's Recipe", "Receta de la Pescadera")),
              ("captain_log", ("Diário do Capitão Afogado", "Drowned Captain's Log", "Diario del Capitán Ahogado"), "Book_A", "altar_book", (0.7, 1.0, 1.2)), "docks_smugglers"),
    "mine": ("mine_01_crystal_vein", ("Altar de Cristal", "Crystal Altar", "Altar de Cristal"),
             (("Mapa das Galerias", "Gallery Map", "Mapa de las Galerías"), ("Catálogo do Joalheiro", "Jeweler's Catalog", "Catálogo del Joyero")),
             ("crystal_heart", ("Coração de Cristal", "Crystal Heart", "Corazón de Cristal"), "Crystal_Gem", "stone_heart", (0.7, 1.0, 1.5)), "map_mine"),
    "bunker": ("bunker_01_entrance", ("Altar da Armaria", "Armory Altar", "Altar de la Armería"),
               (("Registro do Intendente", "Quartermaster's Ledger", "Registro del Intendente"), ("Prontuário do Médico", "Medic's Chart", "Historial del Médico")),
               ("general_baton", ("Bastão do General", "General's Baton", "Bastón del General"), "Sword_D", "dark_blade", (1.3, 0.9, 0.8)), "map_bunker"),
    "dark_forest": ("dark_forest_01_woods", ("Altar do Pântano", "Bog Altar", "Altar del Pantano"),
                    (("Herbário da Ervanária", "Herbalist's Herbal", "Herbario de la Herbolaria"), ("Cancioneiro do Encantador", "Charmer's Songbook", "Cancionero del Encantador")),
                    ("elder_seed", ("Semente do Ancião", "Elder's Seed", "Semilla del Anciano"), "Mushroom_Cluster", "spore_crown", (0.8, 1.2, 0.7)), "map_dark_forest"),
}
BOOK_MODELS = (("Book_A", (1.0, 1.0, 1.0)), ("Ornate_Book", (1.0, 1.0, 1.0)))
BOOK_TINTS = {"forest": ((0.8, 1.2, 0.7), (1.3, 0.9, 0.6)), "ruins": ((1.1, 1.0, 0.8), (1.0, 0.9, 1.2)), "fort": ((0.8, 0.9, 1.3), (1.3, 0.7, 0.8)), "catacombs": ((0.9, 0.9, 1.1), (0.7, 1.0, 1.2)),
              "desert": ((1.3, 1.1, 0.6), (1.1, 0.8, 0.6)), "docks": ((0.7, 1.0, 1.3), (1.0, 1.1, 0.8)), "mine": ((0.9, 1.0, 1.4), (1.2, 1.0, 0.7)), "bunker": ((1.1, 1.0, 0.8), (0.8, 1.2, 0.9)),
              "dark_forest": ((0.7, 1.1, 0.8), (1.0, 0.7, 1.2)), "cemetery": ((0.9, 0.9, 1.0), (1.0, 0.9, 1.1))}
T = {}


def text(key, trio):
    T[key] = tuple(trio)


def fmt(templates, **kw):
    return tuple(templates[i].format(**{k: (v[i] if isinstance(v, tuple) else v) for k, v in kw.items()}) for i in range(3))


def mini_of(area, quest):
    """Grupo (prop com summon) cujo monstro larga o item da missão."""
    for prop in arenas[area]["props"]:
        groups = ([prop["summon"]] if prop.get("summon") else []) + [e["summon"] for e in prop.get("extra_summons", [])]
        for g in groups:
            if any(monsters[m["monster"]].get("quest_drop") == quest.get("item") for m in g["monsters"]):
                return prop, g
    raise SystemExit("sem mini-chefe para a missão %s" % quest)


def free_spot(arena, around, radius=3.5):
    things = [d["position"] for d in arena["decor"] if "position" in d and ("solid" in d or "collider" in d or d.get("piece", "").startswith(("Wall_", "Pr_")))] + [p["position"] for p in arena["props"] if "position" in p]
    for r in (0, 4, 8, 12, 16):
        for dx, dz in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, r), (r, -r), (-r, -r)):
            x, z = around[0] + dx, around[1] + dz
            if all(((x - a) ** 2 + (z - b) ** 2) ** 0.5 > radius for a, b in things):
                return [round(x, 1), round(z, 1)]
    return list(around)


for tag, (area, altar_name, books, boss_item, city_q) in MAPS.items():
    arena = arenas[area]
    # --- as duas missões das aldeias (item de mini-chefe + chave)
    villagers = [(qid, q) for qid, q in quests.items() if isinstance(q, dict) and q.get("area") == area and q.get("type") == "village" and isinstance(q.get("item"), str) and ("gives_key" in q or "gives" in q)]
    villagers.sort(key=lambda kv: 0 if kv[0].endswith(("leshy", "sigil", "scholar", "seal", "axe", "horn", "helm", "tusk")) else 1)
    assert len(villagers) == 2, (tag, [v[0] for v in villagers])
    picked = []
    for i, (qid, q) in enumerate(villagers):
        prop, group = mini_of(area, q)
        picked.append((qid, q, prop, group))
    # --- o altar: a peça-altar existente (kit, sem ser quem dá missão) ou um novo
    giver_ids = {q["giver"] for _, q in villagers}
    altar = None
    for qid, q, prop, group in picked:
        if prop["npc"] not in giver_ids and altar is None:
            altar = prop
    first_group = picked[0][3]
    if altar is None:
        spawn_ref = first_group["position"]
        altar = {"id": tag + "_altar", "kind": "npc", "npc": tag + "_altar", "kit": "Altar_Summon", "solid": [2.2, 2.0], "rotation": 0,
                 "position": free_spot(arena, [spawn_ref[0], spawn_ref[1] - 4.0]), "needs_key": "x"}
        arena["props"].append(altar)
    spawn = list(altar["summon"]["position"] if altar.get("summon") else [altar["position"][0], altar["position"][1] + 5.0])
    altar["npc"] = tag + "_altar"
    altar["needs_key"] = "book_%s_1" % tag
    altar.pop("needs_quest", None)  # o livro basta: não depende de a missão do outro mini-chefe estar ativa
    if tag not in ("forest", "desert"):  # as ruínas do templo ficam (Floresta e Deserto); nos outros mapas o altar é o do Esgoto
        altar["kit"], altar["solid"] = "Altar_Summon", [2.2, 2.0]
    # grupos: livro i -> mini-chefe da missão i
    altar_groups = [dict(g, position=spawn) for _, _, _, g in picked]
    for g in altar_groups:
        g["position"] = list(spawn)
    altar["summon"] = altar_groups[0]
    altar["extra_summons"] = [{"needs_key": "book_%s_2" % tag, "dialogue": 2, "summon": altar_groups[1]}]
    # as outras peças que despertavam grupos deixam de despertar; as que eram só altares somem
    for qid, q, prop, group in picked:
        if prop is altar:
            continue
        prop.pop("summon", None)
        prop.pop("needs_quest", None)
        if prop["npc"] not in giver_ids:
            arena["props"] = [p for p in arena["props"] if p["id"] != prop["id"]]
    # --- livros, textos e falas
    giver_names = {}
    mini_names = []
    for i, (qid, q, prop, group) in enumerate(picked):
        n = i + 1
        book_id, book_key = "%s_book_%d" % (tag, n), "book_%s_%d" % (tag, n)
        mon = group["monsters"][0]["monster"]
        mini_name = tuple(name(monsters[mon]["name_key"], k) for k in range(3))
        mini_names.append(mini_name)
        giver_name = tuple(name(npcs[q["giver"]]["name_key"], k) for k in range(3))
        item_name = tuple(name(valuables[q["item"]]["name_key"], k) for k in range(3))
        q["grants_key"], q["grants_item"] = book_key, book_id
        q.pop("grants_toast", None)
        valuables[book_id] = {"name_key": "VALUABLE_%s_BOOK_%d" % (tag.upper(), n), "desc_key": "VALUABLE_%s_BOOK_%d_DESC" % (tag.upper(), n), "value": 0, "maps": [], "quest_item": True, "model": BOOK_MODELS[i][0]}
        bname = books[i]
        text("VALUABLE_%s_BOOK_%d" % (tag.upper(), n), bname)
        text("VALUABLE_%s_BOOK_%d_DESC" % (tag.upper(), n), fmt((
            "Entregue por {g}. Leve o grupo ao {a}: lido diante da pedra, o livro desperta {m}. Some da bolsa quando {m} cair. Não pode ser vendido nem perdido.",
            "Given by {g}. Take the group to the {a}: read before the stone, the book awakens {m}. It vanishes from the bag when {m} falls. It cannot be sold or lost.",
            "Entregado por {g}. Lleva al grupo al {a}: leído ante la piedra, el libro despierta a {m}. Desaparece de la bolsa cuando {m} cae. No se puede vender ni perder."), g=giver_name, a=altar_name, m=mini_name))
        # fala extra do NPC: o livro e o altar
        key = "DLG_%s_BOOK_%d" % (tag.upper(), n)
        text(key, fmt((
            "Leve este livro, {b}, ao {a}: lido diante da pedra, ele desperta {m}. Traga-me {i}, que ele guarda, e eu lhes entrego a chave.",
            "Take this book, {b}, to the {a}: read before the stone, it awakens {m}. Bring me {i}, which it keeps, and I will hand you the key.",
            "Lleven este libro, {b}, al {a}: leído ante la piedra, despierta a {m}. Tráiganme {i}, que guarda, y les entrego la llave."), b=bname, a=altar_name, m=mini_name, i=item_name))
        for d in npcs[q["giver"]]["dialogues"]:
            if d.get("offer") == qid and key not in d["lines"]:
                d["lines"] = d["lines"] + [key]
        giver_name_t = giver_name
    # --- o NPC do altar
    npcs[tag + "_altar"] = {"_comment": "Altar único do mapa (%s): o livro que o grupo tem desperta o mini-chefe dele (needs_key + extra_summons no prop). Gerado por build_map_mechanics.py." % area,
                            "name_key": "NPC_%s_ALTAR" % tag.upper(), "color": [0.55, 0.5, 0.45],
                            "dialogues": [{"when": {}, "lines": ["DLG_%s_ALTAR_1" % tag.upper()]}, {"when": {}, "lines": ["DLG_%s_ALTAR_LOCKED" % tag.upper()]}, {"when": {}, "lines": ["DLG_%s_ALTAR_2" % tag.upper()]}]}
    text("NPC_%s_ALTAR" % tag.upper(), altar_name)
    text("DLG_%s_ALTAR_1" % tag.upper(), fmt((
        "Você apoia {b} na pedra do {a} e lê em voz alta. O chão treme, e {m} se levanta diante do altar.",
        "You rest {b} on the stone of the {a} and read aloud. The ground shakes, and {m} rises before the altar.",
        "Apoyas {b} en la piedra del {a} y lees en voz alta. El suelo tiembla y {m} se levanta ante el altar."), b=books[0], a=altar_name, m=mini_names[0]))
    text("DLG_%s_ALTAR_2" % tag.upper(), fmt((
        "Você apoia {b} na pedra do {a} e lê em voz alta. O ar pesa, e {m} surge diante do altar.",
        "You rest {b} on the stone of the {a} and read aloud. The air grows heavy, and {m} appears before the altar.",
        "Apoyas {b} en la piedra del {a} y lees en voz alta. El aire pesa y {m} aparece ante el altar."), b=books[1], a=altar_name, m=mini_names[1]))
    text("DLG_%s_ALTAR_LOCKED" % tag.upper(), fmt((
        "A pedra não reage. Há um vazio no centro, do tamanho de um livro: {b1} ou {b2} devem ter o que falta.",
        "The stone does not react. There is an empty gap in the center, the size of a book: {b1} or {b2} must hold what is missing.",
        "La piedra no reacciona. Hay un hueco en el centro, del tamaño de un libro: {b1} o {b2} deben tener lo que falta."), b1=books[0], b2=books[1]))
    # --- a missão da cidade: item do chefe, ouro de recompensa
    boss_group = next(g for g in arena.get("victory_groups", []) if True) if arena.get("victory_groups") else None
    boss_monster = None
    if boss_group:
        boss_monster = next(e["monsters"][0]["monster"] for e in arena["encounters"] if e["id"] == boss_group)
    cq = quests[city_q]
    if boss_item:
        iid, inames, model, icon, tint = boss_item
        valuables[iid] = {"name_key": "VALUABLE_%s" % iid.upper(), "desc_key": "VALUABLE_%s_DESC" % iid.upper(), "value": 0, "maps": [], "quest_item": True, "model": model}
        text("VALUABLE_%s" % iid.upper(), inames)
        boss_name = tuple(name(monsters[boss_monster]["name_key"], k) for k in range(3))
        text("VALUABLE_%s_DESC" % iid.upper(), fmt((
            "Largado por {b}, o chefe do mapa. Não pode ser vendido nem perdido: leve-o a quem o pediu.", "Dropped by {b}, the map's boss. It cannot be sold or lost: take it to whoever asked for it.",
            "Soltado por {b}, el jefe del mapa. No se puede vender ni perder: llévalo a quien lo pidió."), b=boss_name))
        cq.pop("clear", None)
        cq["item"] = iid
        cq["opens_map"] = True  # a trava dos portões das cidades conta também as missões da cidade que não são `main` (as Docas)
        giver_t = tuple(name(npcs[cq["giver"]]["name_key"], k) for k in range(3))
        text(cq["desc_key"], fmt((
            "{g} quer {i}, que {b} guarda no fundo do mapa. Consiga o livro com os moradores, desperte os mini-chefes no altar, troque os itens deles pelas chaves, abra o portão com o guardião e derrote {b}. Entregue {i} a {g} por uma recompensa em ouro.",
            "{g} wants {i}, which {b} keeps at the bottom of the map. Get the books from the locals, wake the mini-bosses at the altar, trade their items for the keys, open the gate with the guardian and defeat {b}. Hand {i} to {g} for a gold reward.",
            "{g} quiere {i}, que {b} guarda en el fondo del mapa. Consigue los libros con los lugareños, despierta a los minijefes en el altar, cambia sus objetos por las llaves, abre el portón con el guardián y derrota a {b}. Entrega {i} a {g} por una recompensa en oro."), g=giver_t, i=inames, b=boss_name))
        monsters[boss_monster]["quest_drop"] = iid
        for d in npcs[cq["giver"]]["dialogues"]:
            if d.get("when", {}).get("quest_active") == city_q:
                d["service"] = "turn_in"
        try:
            from PIL import Image
            im = Image.open("assets/ui/icons/%s.png" % icon).convert("RGBA")
            r_, g_, b_, a_ = im.split()
            Image.merge("RGBA", tuple(c.point(lambda v, m=m: min(255, int(v * m))) for c, m in zip((r_, g_, b_), tint)) + (a_,)).save("assets/ui/icons/%s.png" % iid)
        except Exception as exc:
            print("aviso: ícone de %s não gerado: %s" % (iid, exc))
    elif city_q == "royal_skull":
        for mid, m in monsters.items():
            if m.get("quest_drop") == "old_skull":
                m.pop("quest_drop")
        monsters[boss_monster]["quest_drop"] = "old_skull"
    if boss_monster and monsters[boss_monster].get("category") not in ("boss",):
        monsters[boss_monster]["category"] = "boss"  # o chefe do mapa deixa o baú do chefe (tesouro) e o item da cidade
    # ícones dos livros
    try:
        from PIL import Image
        for i in range(2):
            im = Image.open("assets/ui/icons/%s.png" % ("altar_book" if i == 0 else "gator_book")).convert("RGBA")
            r_, g_, b_, a_ = im.split()
            tint = BOOK_TINTS[tag][i]
            Image.merge("RGBA", tuple(c.point(lambda v, m=m: min(255, int(v * m))) for c, m in zip((r_, g_, b_), tint)) + (a_,)).save("assets/ui/icons/%s_book_%d.png" % (tag, i + 1))
    except Exception as exc:
        print("aviso: ícones dos livros não gerados:", exc)

# Os mini-chefes só nascem no altar: os que andavam soltos pelos mapas (Alfa da Matilha, Comandante do Forte, Guardião do Túmulo da Mina) viram elites; os itens que largam continuam saindo deles.
for solto in ("ruin_alpha", "fort_commander", "tomb_guardian"):
    monsters[solto]["category"] = "elite"

for lang_i, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po", "locale/messages.pot")):
    t = open(path, encoding="utf-8").read()
    add = ""
    for key, trio in T.items():
        val = "" if path.endswith(".pot") else trio[lang_i].replace("\\", "\\\\").replace('"', '\\"')
        if re.search(r'msgid "%s"\n' % re.escape(key), t):
            if val:
                t = re.sub(r'(msgid "%s"\nmsgstr )"[^\n]*"' % re.escape(key), lambda m: m.group(1) + '"' + val.replace("\\", "\\\\") + '"', t)
        else:
            add += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, val)
    open(path, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + add)
for path, data in ((ARENAS, arenas), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables), (MONSTERS, monsters)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK mecânica de missões em", ", ".join(MAPS))
