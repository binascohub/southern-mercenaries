"""NPCs das cidades que abrem as missões de cada mapa, e a corrente de missões entre as três cidades.
  Tortuga (taverna): o Veterano de Guerra aparece depois da Floresta (`forest_treasure` concluída) e abre as Ruínas; depois de concluir as Ruínas aparece o Cartógrafo, que manda ir à Capital (pelo Viajante do Tempo) buscar o Mapa Selado com o Sacristão e trazê-lo.
  Capital (igreja): a Irmã Penitente abre as Catacumbas e o Peregrino, o Deserto (o Padre já abre o Cemitério e o Forte); o Sacristão entrega o Mapa Selado e, depois do Deserto, pede a Foice de Prata
  que está com o Velho Zeca, na Fazenda.
  Fazenda: a Casa de Equipamentos do fazendeiro (nova, um interior `farm_shed` com porta na lateral dos campos): o Fazendeiro abre a Mina, o Ferreiro o Bunker e a Lenhadora a Floresta Escura.
As missões de mapa (`type: main`) terminam sozinhas quando o chefe do mapa cai (`clear` do grupo do chefe). Falas com `grants_item` entregam o item (Town.interact); props com `after_quest` só aparecem
depois da missão (prototype_arena._build_props).
Chamado no fim de tools/assets/build_maps.py (antes de set_map_order.py); idempotente.
uso: python3 tools/assets/build_city_quests.py   (a partir da raiz do projeto)"""
import json, math, re, random
ARENAS, NPCS, QUESTS, VALUABLES = "data/arenas.json", "data/npcs.json", "data/quests.json", "data/valuables.json"
arenas, npcs, quests, valuables = (json.load(open(p, encoding="utf-8")) for p in (ARENAS, NPCS, QUESTS, VALUABLES))
rng = random.Random("city-quests")


def put_prop(area, prop):
    arenas[area]["props"] = [p for p in arenas[area]["props"] if p["id"] != prop["id"]] + [prop]


def body(sex, hair, color, outfit=None):
    return {"sex": sex, "hair": [hair] if isinstance(hair, str) else hair, "hair_color": color, "pose": "idle", "outfit": outfit or {"body": "cloth"}}


def npc(nid, name_key, color, dialogues, b):
    npcs[nid] = {"name_key": name_key, "color": color, "dialogues": dialogues, "body": b}


def map_quest(qid, giver, area, boss_group, gold, xp, element):
    quests[qid] = {"name_key": "QUEST_" + qid.upper(), "desc_key": "QUEST_%s_DESC" % qid.upper(), "type": "main", "giver": giver, "area": area, "clear": [boss_group],
                   "target_element": element, "reward": {"gold": gold, "xp": xp}}


def opener(qid, prefix, after=None):
    when = {"quest_new": qid}
    if after:
        when["after"] = after
    return [{"when": when, "lines": ["DLG_%s_1" % prefix, "DLG_%s_2" % prefix, "DLG_%s_3" % prefix], "offer": qid},
            {"when": {"quest_active": qid}, "lines": ["DLG_%s_ACTIVE" % prefix]}, {"when": {}, "lines": ["DLG_%s_DONE" % prefix]}]


# ---------------------------------------------------------------- itens
valuables["sealed_map"] = {"name_key": "VALUABLE_SEALED_MAP", "value": 0, "maps": [], "quest_item": True, "model": "Book_A"}
valuables["silver_sickle"] = {"name_key": "VALUABLE_SILVER_SICKLE", "value": 0, "maps": [], "quest_item": True, "model": "Tool_Sickle"}

# ---------------------------------------------------------------- NPCs e missões
npc("war_veteran", "NPC_WAR_VETERAN", [0.5, 0.2, 0.2], opener("map_ruins", "WARVET", after="forest_treasure"), body("male", "Hair_Beard", [0.4, 0.4, 0.38]))
map_quest("map_ruins", "war_veteran", "ruins_01_city", "r_boss", 600, 1200, "earth")
npc("cartographer", "NPC_CARTOGRAPHER", [0.45, 0.4, 0.55], [
    {"when": {"quest_new": "trav_to_capital", "after": "map_ruins"}, "lines": ["DLG_CARTO_1", "DLG_CARTO_2", "DLG_CARTO_3"], "offer": "trav_to_capital"},
    {"when": {"quest_active": "trav_to_capital"}, "lines": ["DLG_CARTO_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_CARTO_DONE"]}], body("male", "Hair_SimpleParted", [0.55, 0.52, 0.48]))
quests["trav_to_capital"] = {"name_key": "QUEST_TRAV_TO_CAPITAL", "desc_key": "QUEST_TRAV_TO_CAPITAL_DESC", "type": "main", "giver": "cartographer", "area": "tortuga", "target_element": "air",
                             "reward": {"gold": 700, "xp": 1400}, "item": "sealed_map"}
npc("penitent_sister", "NPC_PENITENT_SISTER", [0.6, 0.5, 0.6], opener("map_catacombs", "PENSIS", after="royal_skull"), body("female", "Hair_Long", [0.15, 0.12, 0.15]))
map_quest("map_catacombs", "penitent_sister", "catacombs_01_depths", "ct_king", 800, 1600, "water")
npc("pilgrim", "NPC_PILGRIM", [0.7, 0.55, 0.3], opener("map_desert", "PILGRIM", after="map_catacombs"), body("male", "Hair_Beard", [0.3, 0.22, 0.12]))
map_quest("map_desert", "pilgrim", "desert_01_canyon", "d_sphinx", 900, 1800, "air")
npc("sacristan", "NPC_SACRISTAN", [0.45, 0.45, 0.5], [
    {"when": {"requires": "trav_to_capital"}, "lines": ["DLG_SACRI_MAP_1", "DLG_SACRI_MAP_2"], "grants_item": "sealed_map"},
    {"when": {"quest_new": "cap_to_farm", "after": "map_desert"}, "lines": ["DLG_SACRI_1", "DLG_SACRI_2", "DLG_SACRI_3"], "offer": "cap_to_farm"},
    {"when": {"quest_active": "cap_to_farm"}, "lines": ["DLG_SACRI_ACTIVE"], "service": "turn_in"},
    {"when": {}, "lines": ["DLG_SACRI_DONE"]}], body("male", "Hair_Buzzed", [0.4, 0.38, 0.35]))
quests["cap_to_farm"] = {"name_key": "QUEST_CAP_TO_FARM", "desc_key": "QUEST_CAP_TO_FARM_DESC", "type": "main", "giver": "sacristan", "area": "capital_01_aurenhold", "target_element": "earth",
                         "reward": {"gold": 1000, "xp": 2000}, "item": "silver_sickle"}
npc("shed_farmer", "NPC_SHED_FARMER", [0.5, 0.4, 0.25], opener("map_mine", "FARMER"), body("male", "Hair_Beard", [0.35, 0.25, 0.15]))
map_quest("map_mine", "shed_farmer", "mine_01_crystal_vein", "mn_boss", 1000, 2000, "earth")
npc("shed_smith", "NPC_SHED_SMITH", [0.4, 0.35, 0.3], opener("map_bunker", "SMITH", after="map_mine"), body("male", "Hair_Buzzed", [0.1, 0.1, 0.1]))
map_quest("map_bunker", "shed_smith", "bunker_01_entrance", "bk_boss", 1100, 2200, "fire")
npc("shed_lumberjack", "NPC_SHED_LUMBERJACK", [0.4, 0.5, 0.3], opener("map_dark_forest", "LUMBER", after="map_bunker"), body("female", "Hair_Buns", [0.3, 0.2, 0.1]))
map_quest("map_dark_forest", "shed_lumberjack", "dark_forest_01_woods", "fd_boss", 1200, 2400, "earth")
npc("shed_scarecrow", "NPC_SHED_SCARECROW", [0.5, 0.45, 0.3], [
    {"when": {"requires": "cap_to_farm"}, "lines": ["DLG_ZECA_1", "DLG_ZECA_2"], "grants_item": "silver_sickle"}, {"when": {}, "lines": ["DLG_ZECA_DEFAULT"]}], body("male", "Hair_Beard", [0.6, 0.58, 0.55]))

# ---------------------------------------------------------------- Tortuga: taverna
put_prop("tavern", {"id": "war_veteran", "kind": "npc", "npc": "war_veteran", "position": [6.8, -1.2], "rotation": 200, "after_quest": "forest_treasure"})
put_prop("tavern", {"id": "cartographer", "kind": "npc", "npc": "cartographer", "position": [3.4, -1.2], "rotation": 160, "after_quest": "map_ruins"})
# ---------------------------------------------------------------- Capital: igreja
put_prop("capital_01_aurenhold", {"id": "sacristan", "kind": "npc", "npc": "sacristan", "position": [-42.5, -34.5], "rotation": 90})
put_prop("capital_01_aurenhold", {"id": "penitent_sister", "kind": "npc", "npc": "penitent_sister", "position": [-33.0, -33.6], "rotation": 180})
put_prop("capital_01_aurenhold", {"id": "pilgrim", "kind": "npc", "npc": "pilgrim", "position": [-27.0, -33.6], "rotation": 180})

# ---------------------------------------------------------------- Fazenda: a casa de equipamentos (exterior nos campos + interior `farm_shed`)
farm = arenas["farm_01_fields"]
solid_things = [d["position"] for d in farm["decor"] if d.get("piece") and d.get("shed") is not True and not d["piece"].startswith(("Pl_", "Grass", "Prop_", "Ground_")) and "position" in d] + [p["position"] for p in farm["props"] if "position" in p]
SHED = None
for cx_, cz_ in ((-24, -14), (-18, -4), (18, -3), (-12, -3), (-20, -22), (22, -22), (-6, -9)):
    if not any(math.hypot(cx_ - x, cz_ - z) < 6 for x, z in solid_things):
        SHED = (cx_, cz_)
        break
assert SHED, "sem lugar para a casa de equipamentos"
sx, sz = SHED
farm["decor"] = [d for d in farm["decor"] if d.get("shed") is not True]
shed_parts = []
for piece, x, z, rot in (("Wall_Plaster_Straight", sx - 2, sz + 2, 0), ("Wall_Plaster_Door_Round", sx, sz + 2, 0), ("Wall_Plaster_Straight", sx + 2, sz + 2, 0),
                         ("Wall_Plaster_Straight", sx - 2, sz - 2, 180), ("Wall_Plaster_Straight", sx, sz - 2, 180), ("Wall_Plaster_Straight", sx + 2, sz - 2, 180),
                         ("Wall_Plaster_Window_Wide_Round", sx - 3, sz, 270), ("Wall_Plaster_Window_Thin_Round", sx + 3, sz, 90)):
    shed_parts.append({"piece": piece, "position": [x, z], "rotation": rot, "solid": [2.0, 0.5] if rot in (0, 180) else [0.5, 2.0], "shed": True})
shed_parts += [{"piece": "Corner_Exterior_Wood", "position": [sx + dx, sz + dz], "shed": True} for dx in (-3, 3) for dz in (-2, 2)]
shed_parts += [{"piece": "Floor_WoodDark", "position": [sx + dx, sz + dz], "y": 0.03, "shed": True} for dx in (-2, 0, 2) for dz in (-1, 1)]
shed_parts += [{"piece": "Roof_RoundTiles_4x4", "position": [sx - 1.5, sz], "y": 3.2, "shed": True}, {"piece": "Roof_RoundTiles_4x4", "position": [sx + 1.5, sz], "y": 3.2, "shed": True}]
shed_parts += [{"piece": p, "position": [sx + dx, sz + dz], "rotation": r, "solid": [s, s], "shed": True} for p, dx, dz, r, s in (
    ("Barrel", 4.2, 2.4, 0, 0.9), ("Crate_Wooden", -4.2, 2.3, 20, 0.9), ("Pr_CartSmall", 6.0, 0.5, 70, 1.6))]
shed_parts.append({"piece": "Tool_Hoe", "position": [sx + 3.6, sz + 3.4], "rotation": 90, "shed": True})
farm["decor"] += shed_parts
put_prop("farm_01_fields", {"id": "shed_door", "kind": "exit", "name_key": "PROP_SHED", "position": [sx, sz + 3.2], "to": "farm_shed", "entry": "door"})
farm["entries"]["shed"] = [sx, sz + 4.6]

tavern = arenas["tavern"]
rd = lambda cx, cz, w, h: {"id": "hall", "center": [cx, cz], "size": [w, h], "doors": [], "torch": True}
shed_decor = []
for piece, x, z, rot, solid in (
        ("Workbench", -6.5, -5.2, 0, [2.0, 0.9]), ("Anvil", -3.8, -5.3, 0, [0.9, 0.7]), ("Whetstone", -2.4, -5.3, 0, None), ("Shelf_Simple", 2.0, -5.5, 0, [1.4, 0.5]),
        ("Shelf_Simple", 4.0, -5.5, 0, [1.4, 0.5]), ("Weapon_Rack", 6.4, -5.3, 0, [2.0, 0.8]), ("Barrel", 7.6, -4.2, 0, [0.9, 0.9]), ("Barrel", 7.7, -2.9, 0, [0.9, 0.9]),
        ("Crate_Wooden", -7.6, -3.5, 15, [0.9, 0.9]), ("Crate_Big", -7.5, -2.2, 0, [1.1, 1.1]), ("Tv_Sack", -7.4, 0.2, 40, None), ("Tv_Sack_2", -6.5, 0.5, 0, None),
        ("Table_Large", 5.0, 1.8, 0, [2.2, 1.2]), ("Bench", 5.0, 3.0, 0, [1.6, 0.6]), ("Tv_Firewood", 7.8, 0.5, 90, [1.4, 0.8]), ("Pr_CartSmall", -5.2, 3.4, 20, [2.0, 1.2]),
        ("Tool_Pitchfork", -1.0, -5.6, 0, None), ("Tool_Scythe", 0.4, -5.6, 0, None), ("Tool_Shovel", -0.3, -5.5, 0, None), ("Tool_Hoe", 1.2, -5.5, 0, None),
        ("Bucket_Wooden_1", 3.0, 0.5, 0, None), ("Pr_Basket", -3.0, 3.8, 0, None), ("Tv_Torch", -7.9, -1.0, 90, None), ("Tv_Torch", 7.9, 2.0, 270, None)):
    d = {"piece": piece, "position": [x, z], "rotation": rot}
    if solid:
        d["solid"] = solid
    shed_decor.append(d)
shed_decor += [{"light": [1.0, 0.7, 0.4], "position": [0, -1], "y": 2.6, "range": 12.0, "energy": 1.4}, {"light": [1.0, 0.6, 0.3], "position": [-7.5, -1.5], "y": 1.8, "range": 6.0, "energy": 0.9},
               {"light": [1.0, 0.6, 0.3], "position": [7.5, 1.0], "y": 1.8, "range": 6.0, "energy": 0.9}]
arenas["farm_shed"] = {
    "_comment": "Interior da Casa de Equipamentos do fazendeiro (Fazenda): bancada, bigorna, ferramentas, barris e sacas; o Fazendeiro, o Ferreiro e a Lenhadora abrem as missões da Mina, do Bunker e da Floresta Escura, e o Velho Zeca "
                "guarda a Foice de Prata. Gerado por tools/assets/build_city_quests.py.",
    "name_key": "AREA_FARM_SHED", "town": True, "player_class": "mage", "wake_radius": 0, "alert_radius": 0, "area_level": 1,
    "rooms": [rd(0, 0, 18, 14)], "encounters": [], "entries": {"start": [0, 2], "door": [0, 4.5]},
    "props": [
        {"id": "shed_exit", "kind": "exit", "name_key": "PROP_SHED_EXIT", "position": [0, 6.2], "to": "farm_01_fields", "entry": "shed"},
        {"id": "shed_farmer", "kind": "npc", "npc": "shed_farmer", "position": [-4.8, -2.4], "rotation": 180},
        {"id": "shed_smith", "kind": "npc", "npc": "shed_smith", "position": [-2.6, -3.6], "rotation": 200},
        {"id": "shed_lumberjack", "kind": "npc", "npc": "shed_lumberjack", "position": [3.2, -3.4], "rotation": 160},
        {"id": "shed_scarecrow", "kind": "npc", "npc": "shed_scarecrow", "position": [5.0, -0.4], "rotation": 240}],
    "style": dict(tavern["style"], **{"_comment": "Casa de Equipamentos: paredes de reboco e enxaimel, piso de tábuas escuras; a parede sul fica aberta para a câmera.", "floor": "Floor_WoodDark"}),
    "decor": shed_decor, "crowd": [], "passive": True}

T = {
    "AREA_FARM_SHED": ("Casa de Equipamentos", "Equipment House", "Casa de Equipos"),
    "PROP_SHED": ("Casa de Equipamentos do Fazendeiro", "Farmer's Equipment House", "Casa de Equipos del Granjero"),
    "PROP_SHED_EXIT": ("Sair para os campos", "Out to the fields", "Salir a los campos"),
    "NPC_WAR_VETERAN": ("Veterano de Guerra", "War Veteran", "Veterano de Guerra"),
    "NPC_CARTOGRAPHER": ("Cartógrafo Aldrin", "Cartographer Aldrin", "Cartógrafo Aldrin"),
    "NPC_PENITENT_SISTER": ("Irmã Penitente Isolda", "Sister Isolda the Penitent", "Hermana Penitente Isolda"),
    "NPC_PILGRIM": ("Peregrino Haled", "Pilgrim Haled", "Peregrino Haled"),
    "NPC_SACRISTAN": ("Sacristão Ambrósio", "Sacristan Ambrose", "Sacristán Ambrosio"),
    "NPC_SHED_FARMER": ("Fazendeiro Tadeu", "Farmer Tadeo", "Granjero Tadeo"),
    "NPC_SHED_SMITH": ("Ferreiro Gorm", "Smith Gorm", "Herrero Gorm"),
    "NPC_SHED_LUMBERJACK": ("Lenhadora Odete", "Lumberjack Odette", "Leñadora Odete"),
    "NPC_SHED_SCARECROW": ("Velho Zeca", "Old Zeca", "Viejo Zeca"),
    "VALUABLE_SEALED_MAP": ("Mapa Selado", "Sealed Map", "Mapa Sellado"),
    "VALUABLE_SILVER_SICKLE": ("Foice de Prata", "Silver Sickle", "Hoz de Plata"),
    "QUEST_MAP_RUINS": ("A Cripta do Rei Caído", "The Fallen King's Crypt", "La cripta del Rey Caído"),
    "QUEST_MAP_RUINS_DESC": ("O Veterano de Guerra, na Taverna, quer o fim do Rei Caído, que guarda o Cofre Real nas Ruínas. Conclua a missão derrotando o Rei Caído.",
                             "The War Veteran, in the Tavern, wants an end to the Fallen King, who guards the Royal Vault in the Ruins. Complete the quest by defeating the Fallen King.",
                             "El Veterano de Guerra, en la Taberna, quiere acabar con el Rey Caído, que guarda la Cámara Real en las Ruinas. Completa la misión derrotando al Rey Caído."),
    "QUEST_TRAV_TO_CAPITAL": ("O Mapa Selado", "The Sealed Map", "El mapa sellado"),
    "QUEST_TRAV_TO_CAPITAL_DESC": ("O Cartógrafo Aldrin, na Taverna, precisa do Mapa Selado que o Sacristão Ambrósio guarda na igreja da Capital Real. Use o Viajante do Tempo para ir à Capital, pegue o mapa com o Sacristão e traga-o de volta ao Cartógrafo.",
                                   "Cartographer Aldrin, in the Tavern, needs the Sealed Map that Sacristan Ambrose keeps in the Royal Capital's church. Use the Time Traveler to reach the Capital, get the map from the Sacristan and bring it back to the Cartographer.",
                                   "El Cartógrafo Aldrin, en la Taberna, necesita el Mapa Sellado que el Sacristán Ambrosio guarda en la iglesia de la Capital Real. Usa al Viajero del Tiempo para ir a la Capital, recoge el mapa con el Sacristán y tráelo de vuelta al Cartógrafo."),
    "QUEST_MAP_CATACOMBS": ("As Catacumbas dos Condenados", "The Catacombs of the Condemned", "Las Catacumbas de los Condenados"),
    "QUEST_MAP_CATACOMBS_DESC": ("A Irmã Penitente Isolda, na igreja da Capital, pede que o Rei Acorrentado, no fundo das Catacumbas, finalmente descanse. Conclua a missão derrotando o Rei Acorrentado.",
                                 "Sister Isolda the Penitent, in the Capital's church, asks that the Chained King, deep in the Catacombs, finally rest. Complete the quest by defeating the Chained King.",
                                 "La Hermana Penitente Isolda, en la iglesia de la Capital, pide que el Rey Encadenado, en el fondo de las Catacumbas, por fin descanse. Completa la misión derrotando al Rey Encadenado."),
    "QUEST_MAP_DESERT": ("O Enigma da Esfinge", "The Sphinx's Riddle", "El enigma de la Esfinge"),
    "QUEST_MAP_DESERT_DESC": ("O Peregrino Haled, na igreja da Capital, perdeu três irmãos de fé na travessia do Deserto, onde a Esfinge guarda o salão atrás do portão. Conclua a missão derrotando a Esfinge.",
                              "Pilgrim Haled, in the Capital's church, lost three brothers of faith crossing the Desert, where the Sphinx guards the hall behind the gate. Complete the quest by defeating the Sphinx.",
                              "El Peregrino Haled, en la iglesia de la Capital, perdió a tres hermanos de fe cruzando el Desierto, donde la Esfinge guarda el salón tras el portón. Completa la misión derrotando a la Esfinge."),
    "QUEST_CAP_TO_FARM": ("A Foice de Prata", "The Silver Sickle", "La hoz de plata"),
    "QUEST_CAP_TO_FARM_DESC": ("O Sacristão Ambrósio, na igreja da Capital, precisa da Foice de Prata que o Velho Zeca guarda na Casa de Equipamentos da Fazenda. Use o Viajante do Tempo para ir à Fazenda, pegue a foice com o Velho Zeca e traga-a ao Sacristão.",
                               "Sacristan Ambrose, in the Capital's church, needs the Silver Sickle that Old Zeca keeps in the Farm's Equipment House. Use the Time Traveler to reach the Farm, get the sickle from Old Zeca and bring it to the Sacristan.",
                               "El Sacristán Ambrosio, en la iglesia de la Capital, necesita la Hoz de Plata que el Viejo Zeca guarda en la Casa de Equipos de la Granja. Usa al Viajero del Tiempo para ir a la Granja, recoge la hoz con el Viejo Zeca y tráela al Sacristán."),
    "QUEST_MAP_MINE": ("O Coração da Mina", "The Heart of the Mine", "El corazón de la mina"),
    "QUEST_MAP_MINE_DESC": ("O Fazendeiro Tadeu, na Casa de Equipamentos, perdeu meia dúzia de mineiros no labirinto sob a Fazenda, onde um golem de cristal guarda o fundo. Conclua a missão derrotando o Golem de Cristal.",
                            "Farmer Tadeo, in the Equipment House, lost half a dozen miners in the maze beneath the Farm, where a crystal golem guards the bottom. Complete the quest by defeating the Crystal Golem.",
                            "El Granjero Tadeo, en la Casa de Equipos, perdió media docena de mineros en el laberinto bajo la Granja, donde un gólem de cristal guarda el fondo. Completa la misión derrotando al Gólem de Cristal."),
    "QUEST_MAP_BUNKER": ("O Bunker Lacrado", "The Sealed Bunker", "El búnker sellado"),
    "QUEST_MAP_BUNKER_DESC": ("O Ferreiro Gorm, na Casa de Equipamentos, reconhece o ferro das armas que saem do Bunker, lacrado por um general que não aceitou a rendição. Conclua a missão derrotando o General Ferrugem.",
                              "Smith Gorm, in the Equipment House, recognizes the iron of the weapons coming out of the Bunker, sealed by a general who refused to surrender. Complete the quest by defeating General Rust.",
                              "El Herrero Gorm, en la Casa de Equipos, reconoce el hierro de las armas que salen del Búnker, sellado por un general que no aceptó la rendición. Completa la misión derrotando al General Óxido."),
    "QUEST_MAP_DARK_FOREST": ("A Floresta que Escureceu", "The Forest That Darkened", "El bosque que oscureció"),
    "QUEST_MAP_DARK_FOREST_DESC": ("A Lenhadora Odete, na Casa de Equipamentos, não corta mais lenha na floresta ao norte: as árvores morreram em pé e uma delas se mexe. Conclua a missão derrotando o Ancião Sombrio.",
                                   "Lumberjack Odette, in the Equipment House, no longer cuts wood in the forest to the north: the trees died standing and one of them moves. Complete the quest by defeating the Shadow Elder.",
                                   "La Leñadora Odete, en la Casa de Equipos, ya no corta leña en el bosque del norte: los árboles murieron de pie y uno de ellos se mueve. Completa la misión derrotando al Anciano Sombrío."),
    "DLG_WARVET_1": ("Servi o rei até o último dia, e vi o que sobrou da cidade dele: ruínas, e dentro delas o próprio rei, de pé, sem o ar e sem o descanso.", "I served the king to his last day, and saw what is left of his city: ruins, and inside them the king himself, standing, without breath and without rest.", "Serví al rey hasta su último día, y vi lo que quedó de su ciudad: ruinas, y dentro de ellas el propio rey, de pie, sin aliento y sin descanso."),
    "DLG_WARVET_2": ("As Ruínas ficam ao norte do porto de Tortuga, passando as Docas. O Rei Caído guarda o Cofre Real lá no fundo, atrás de um portão de duas chaves.", "The Ruins lie north of Tortuga's port, past the Docks. The Fallen King guards the Royal Vault deep inside, behind a two-key gate.", "Las Ruinas quedan al norte del puerto de Tortuga, pasando los Muelles. El Rey Caído guarda la Cámara Real en el fondo, tras un portón de dos llaves."),
    "DLG_WARVET_3": ("Derrubem o Rei Caído e eu pago bem. Depois disso, procurem o Cartógrafo Aldrin aqui na taverna: ele sempre sabe para onde ir em seguida.", "Bring the Fallen King down and I will pay well. After that, look for Cartographer Aldrin here in the tavern: he always knows where to go next.", "Derriben al Rey Caído y pago bien. Después, busquen al Cartógrafo Aldrin aquí en la taberna: siempre sabe adónde ir después."),
    "DLG_WARVET_ACTIVE": ("O Rei Caído está no Cofre Real, no fundo das Ruínas. Levem as duas chaves da Erudita e da Sacerdotisa.", "The Fallen King is in the Royal Vault, deep in the Ruins. Take the two keys from the Scholar and the Priestess.", "El Rey Caído está en la Cámara Real, en el fondo de las Ruinas. Lleven las dos llaves de la Erudita y de la Sacerdotisa."),
    "DLG_WARVET_DONE": ("O rei finalmente dorme. Eu também posso, agora. Falem com o Cartógrafo.", "The king finally sleeps. I can, too, now. Talk to the Cartographer.", "El rey por fin duerme. Yo también puedo, ahora. Hablen con el Cartógrafo."),
    "DLG_CARTO_1": ("Vocês limparam as Ruínas, e isso muda o mapa todo: Tortuga já não é o fim da estrada. Há uma cidade ao norte, a Capital Real, e eu nunca vi o mapa dela.", "You cleared the Ruins, and that changes the whole map: Tortuga is no longer the end of the road. There is a city to the north, the Royal Capital, and I have never seen its map.", "Despejaron las Ruinas, y eso cambia todo el mapa: Tortuga ya no es el fin del camino. Hay una ciudad al norte, la Capital Real, y nunca vi su mapa."),
    "DLG_CARTO_2": ("O Sacristão Ambrósio, na igreja de lá, guarda um Mapa Selado desde a guerra. Fale com o Viajante do Tempo: ele os leva até a Capital num piscar de olhos.", "Sacristan Ambrose, in the church there, has kept a Sealed Map since the war. Speak to the Time Traveler: he takes you to the Capital in the blink of an eye.", "El Sacristán Ambrosio, en la iglesia de allá, guarda un Mapa Sellado desde la guerra. Hablen con el Viajero del Tiempo: los lleva a la Capital en un parpadeo."),
    "DLG_CARTO_3": ("Peguem o mapa com o Sacristão e tragam para mim. Não o abram: o selo é a única coisa que mantém os mortos do mapa quietos.", "Get the map from the Sacristan and bring it to me. Do not open it: the seal is the only thing keeping the map's dead quiet.", "Recojan el mapa con el Sacristán y tráiganmelo. No lo abran: el sello es lo único que mantiene quietos a los muertos del mapa."),
    "DLG_CARTO_ACTIVE": ("O Sacristão Ambrósio está na igreja da Capital Real. O Viajante do Tempo, aqui em Tortuga, leva vocês até lá.", "Sacristan Ambrose is in the Royal Capital's church. The Time Traveler, here in Tortuga, takes you there.", "El Sacristán Ambrosio está en la iglesia de la Capital Real. El Viajero del Tiempo, aquí en Tortuga, los lleva allá."),
    "DLG_CARTO_DONE": ("O Mapa Selado! O selo está intacto. Obrigado: a Capital ficou finalmente no papel.", "The Sealed Map! The seal is intact. Thank you: the Capital is finally on paper.", "¡El Mapa Sellado! El sello está intacto. Gracias: la Capital por fin está en el papel."),
    "DLG_SACRI_MAP_1": ("Ah, o Cartógrafo Aldrin os manda. O Mapa Selado está comigo desde a guerra; ninguém o quis, ninguém ousou queimá-lo.", "Ah, Cartographer Aldrin sends you. The Sealed Map has been with me since the war; no one wanted it, no one dared burn it.", "Ah, os manda el Cartógrafo Aldrin. El Mapa Sellado está conmigo desde la guerra; nadie lo quiso, nadie se atrevió a quemarlo."),
    "DLG_SACRI_MAP_2": ("Levem-no, e com cuidado. Digam a Aldrin que o selo é de cera de vela benta: se rachar, o mapa começa a andar sozinho.", "Take it, and carefully. Tell Aldrin the seal is blessed candle wax: if it cracks, the map starts walking by itself.", "Llévenlo, y con cuidado. Díganle a Aldrin que el sello es de cera de vela bendita: si se rompe, el mapa empieza a caminar solo."),
    "DLG_SACRI_1": ("O Deserto está vencido, ouvi dizer, e a Esfinge cala. Mas o mapa de Aldrin trouxe um preço: a Foice de Prata, que corta o que não deve ser cortado, saiu da igreja há anos.", "The Desert is conquered, I hear, and the Sphinx is silent. But Aldrin's map came at a price: the Silver Sickle, which cuts what must not be cut, left the church years ago.", "El Desierto está vencido, dicen, y la Esfinge calla. Pero el mapa de Aldrin trajo un precio: la Hoz de Plata, que corta lo que no debe cortarse, salió de la iglesia hace años."),
    "DLG_SACRI_2": ("Foi parar na Fazenda: o Velho Zeca, na Casa de Equipamentos do Fazendeiro, a guarda entre as ferramentas, achando que é só uma foice velha.", "It ended up on the Farm: Old Zeca, in the Farmer's Equipment House, keeps it among the tools, thinking it is just an old sickle.", "Fue a parar a la Granja: el Viejo Zeca, en la Casa de Equipos del Granjero, la guarda entre las herramientas, creyendo que es solo una hoz vieja."),
    "DLG_SACRI_3": ("Peçam ao Viajante do Tempo que os leve à Fazenda, busquem a foice com o Velho Zeca e tragam-na a mim. A igreja vai precisar dela antes que as árvores do norte acordem.", "Ask the Time Traveler to take you to the Farm, get the sickle from Old Zeca and bring it to me. The church will need it before the trees of the north wake.", "Pidan al Viajero del Tiempo que los lleve a la Granja, recojan la hoz con el Viejo Zeca y tráiganmela. La iglesia la necesitará antes de que despierten los árboles del norte."),
    "DLG_SACRI_ACTIVE": ("A Foice de Prata está com o Velho Zeca, na Casa de Equipamentos da Fazenda. O Viajante do Tempo os leva.", "The Silver Sickle is with Old Zeca, in the Farm's Equipment House. The Time Traveler takes you.", "La Hoz de Plata está con el Viejo Zeca, en la Casa de Equipos de la Granja. El Viajero del Tiempo los lleva."),
    "DLG_SACRI_DONE": ("A foice! Voltou para casa. Que a prata corte só o que deve. Obrigado, mercenários.", "The sickle! It is home again. May the silver cut only what it should. Thank you, mercenaries.", "¡La hoz! Volvió a casa. Que la plata corte solo lo que debe. Gracias, mercenarios."),
    "DLG_PENSIS_1": ("Rezo todos os dias por quem morreu atrás das grades das Catacumbas, e principalmente pelo rei que lá ficou preso, acorrentado, pelos próprios súditos.", "I pray every day for those who died behind the Catacombs' bars, and especially for the king who stayed there chained by his own subjects.", "Rezo todos los días por quienes murieron tras las rejas de las Catacumbas, y sobre todo por el rey que allí quedó preso, encadenado por sus propios súbditos."),
    "DLG_PENSIS_2": ("As Catacumbas ficam ao sul da Capital, depois do portão do Forte. O Rei Acorrentado guarda a Cripta no fundo, atrás de um portão que só abre com duas chaves.", "The Catacombs lie south of the Capital, past the Fort gate. The Chained King guards the Crypt at the bottom, behind a gate that only opens with two keys.", "Las Catacumbas quedan al sur de la Capital, tras el portón del Fuerte. El Rey Encadenado guarda la Cripta en el fondo, tras un portón que solo abre con dos llaves."),
    "DLG_PENSIS_3": ("Derrubem o Rei Acorrentado e a igreja cuida do resto: eu acendo uma vela por ele e uma por vocês. O Peregrino Haled, ao lado, tem a próxima missão.", "Bring down the Chained King and the church will see to the rest: I will light a candle for him and one for you. Pilgrim Haled, beside me, has the next quest.", "Derriben al Rey Encadenado y la iglesia se ocupa del resto: encenderé una vela por él y una por ustedes. El Peregrino Haled, a mi lado, tiene la próxima misión."),
    "DLG_PENSIS_ACTIVE": ("O Rei Acorrentado está na Cripta, no fim das Catacumbas. Levem as chaves de Ferro e de Osso.", "The Chained King is in the Crypt, at the end of the Catacombs. Take the Iron and Bone keys.", "El Rey Encadenado está en la Cripta, al final de las Catacumbas. Lleven las llaves de Hierro y de Hueso."),
    "DLG_PENSIS_DONE": ("O rei descansa. As correntes enfim ficaram leves. Que Deus os guarde.", "The king rests. The chains have finally grown light. God keep you.", "El rey descansa. Las cadenas por fin se volvieron ligeras. Que Dios los guarde."),
    "DLG_PILGRIM_1": ("Atravessei o Deserto cantando, com três irmãos de fé, e só eu voltei. A Esfinge pergunta o que ninguém sabe e devora quem erra.", "I crossed the Desert singing, with three brothers of faith, and only I came back. The Sphinx asks what no one knows and devours whoever errs.", "Crucé el Desierto cantando, con tres hermanos de fe, y solo yo regresé. La Esfinge pregunta lo que nadie sabe y devora a quien yerra."),
    "DLG_PILGRIM_2": ("O Deserto fica depois da Capital, e a Esfinge espera no salão atrás do portão, no fim da estrada de areia. Há um acampamento de nômades logo na entrada.", "The Desert lies past the Capital, and the Sphinx waits in the hall behind the gate, at the end of the sand road. There is a nomad camp right at the entrance.", "El Desierto queda tras la Capital, y la Esfinge espera en el salón tras el portón, al final del camino de arena. Hay un campamento de nómadas justo en la entrada."),
    "DLG_PILGRIM_3": ("Derrubem a Esfinge e me contem a resposta. Depois, falem com o Sacristão Ambrósio: ele tem um pedido para quem vence o Deserto.", "Bring down the Sphinx and tell me the answer. Then speak to Sacristan Ambrose: he has a request for whoever conquers the Desert.", "Derriben a la Esfinge y cuéntenme la respuesta. Luego hablen con el Sacristán Ambrosio: tiene un pedido para quien venza el Desierto."),
    "DLG_PILGRIM_ACTIVE": ("A Esfinge guarda o salão atrás do portão. Levem as chaves de Paus e de Ouros.", "The Sphinx guards the hall behind the gate. Take the Clubs and Diamonds keys.", "La Esfinge guarda el salón tras el portón. Lleven las llaves de Bastos y de Oros."),
    "DLG_PILGRIM_DONE": ("A Esfinge calou. Meus irmãos descansam, e eu canto por eles. Falem com o Sacristão.", "The Sphinx is silent. My brothers rest, and I sing for them. Speak to the Sacristan.", "La Esfinge calló. Mis hermanos descansan, y yo canto por ellos. Hablen con el Sacristán."),
    "DLG_FARMER_1": ("Planto e colho aqui desde os meus avós, e nunca tive medo de nada, até os mineiros começarem a sumir no buraco atrás do meu celeiro.", "I have planted and harvested here since my grandparents, and never feared anything, until the miners began to vanish in the hole behind my barn.", "Siembro y cosecho aquí desde mis abuelos, y nunca temí nada, hasta que los mineros empezaron a desaparecer en el hoyo detrás de mi granero."),
    "DLG_FARMER_2": ("A Mina fica no canto leste dos campos. Por dentro é um labirinto, mas os trilhos de trem levam a todo lugar importante. Um golem de cristal guarda o fundo.", "The Mine lies in the east corner of the fields. Inside it is a maze, but the rails lead to every important place. A crystal golem guards the bottom.", "La Mina queda en la esquina este de los campos. Por dentro es un laberinto, pero los rieles llevan a todos los lugares importantes. Un gólem de cristal guarda el fondo."),
    "DLG_FARMER_3": ("Derrubem o Golem de Cristal e eu pago. Depois falem com o Ferreiro Gorm, aqui ao lado: ele cuida do Bunker.", "Bring down the Crystal Golem and I will pay. Then talk to Smith Gorm, right beside me: he handles the Bunker.", "Derriben al Gólem de Cristal y pago. Luego hablen con el Herrero Gorm, aquí al lado: él se ocupa del Búnker."),
    "DLG_FARMER_ACTIVE": ("O Golem de Cristal está no Coração da Mina. Sigam os trilhos para o norte, depois do labirinto.", "The Crystal Golem is in the Mine's Heart. Follow the rails north, past the maze.", "El Gólem de Cristal está en el Corazón de la Mina. Sigan los rieles al norte, tras el laberinto."),
    "DLG_FARMER_DONE": ("A Mina está calma outra vez, e meus mineiros descansam. Que a terra os receba bem.", "The Mine is calm again, and my miners rest. May the earth receive them well.", "La Mina está en calma otra vez, y mis mineros descansan. Que la tierra los reciba bien."),
    "DLG_SMITH_1": ("Todo ferro que me chega tem a marca do exército do rei, e vem do Bunker, a nordeste dos campos. Alguém lá embaixo ainda forja, e não sou eu.", "Every iron that reaches me bears the king's army mark, and comes from the Bunker, northeast of the fields. Someone down there still forges, and it is not me.", "Todo el hierro que me llega tiene la marca del ejército del rey, y viene del Búnker, al noreste de los campos. Alguien allá abajo todavía forja, y no soy yo."),
    "DLG_SMITH_2": ("O General Ferrugem lacrou o Bunker com todos dentro. Armas, ferramentas e suprimentos para anos: tudo ainda lá. Mas o general ainda manda.", "General Rust sealed the Bunker with everyone inside. Weapons, tools and supplies for years: all still there. But the general still commands.", "El General Óxido selló el Búnker con todos dentro. Armas, herramientas y suministros para años: todo sigue allí. Pero el general todavía manda."),
    "DLG_SMITH_3": ("Derrubem o General Ferrugem. Eu forjo algo bom com o que trouxerem. A Lenhadora Odete tem a próxima missão.", "Bring down General Rust. I will forge something good with whatever you bring. Lumberjack Odette has the next quest.", "Derriben al General Óxido. Forjaré algo bueno con lo que traigan. La Leñadora Odete tiene la próxima misión."),
    "DLG_SMITH_ACTIVE": ("O Bunker é um labirinto de pedra a nordeste. O General está na Sala de Comando, ao norte. Levem as chaves de Latão e de Aço.", "The Bunker is a stone maze to the northeast. The General is in the Command Room, to the north. Take the Brass and Steel keys.", "El Búnker es un laberinto de piedra al noreste. El General está en la Sala de Mando, al norte. Lleven las llaves de Latón y de Acero."),
    "DLG_SMITH_DONE": ("O Bunker está quieto. O ferro dele agora é só ferro. Obrigado.", "The Bunker is still. Its iron is now just iron. Thank you.", "El Búnker está quieto. Su hierro ahora es solo hierro. Gracias."),
    "DLG_LUMBER_1": ("Corto lenha há vinte anos, e a floresta ao norte sempre foi boa de machado. Agora as árvores estão mortas em pé, os morcegos moram nelas, e os troncos sibilam.", "I have cut wood for twenty years, and the forest to the north was always good for an axe. Now the trees stand dead, bats live in them, and the trunks hiss.", "Corto leña desde hace veinte años, y el bosque del norte siempre fue bueno para el hacha. Ahora los árboles están muertos en pie, los murciélagos viven en ellos, y los troncos silban."),
    "DLG_LUMBER_2": ("A Floresta Escura fica a oeste dos campos. Cobras no pântano, cogumelos que brilham, lobisomens: e no fundo, uma árvore que anda, o Ancião Sombrio.", "The Dark Forest lies west of the fields. Snakes in the bog, glowing mushrooms, werewolves: and at the bottom, a walking tree, the Shadow Elder.", "El Bosque Oscuro queda al oeste de los campos. Serpientes en el pantano, hongos que brillan, hombres lobo: y en el fondo, un árbol que anda, el Anciano Sombrío."),
    "DLG_LUMBER_3": ("Derrubem o Ancião Sombrio e a floresta volta a ser só floresta. Eu pago com tudo o que tenho.", "Bring down the Shadow Elder and the forest goes back to being just a forest. I will pay with everything I have.", "Derriben al Anciano Sombrío y el bosque vuelve a ser solo bosque. Pago con todo lo que tengo."),
    "DLG_LUMBER_ACTIVE": ("O Ancião está no Covil, ao norte do Bosque dos Morcegos. Levem as chaves de Musgo e de Espinho.", "The Elder is in the Lair, north of the Bat Grove. Take the Moss and Thorn keys.", "El Anciano está en la Guarida, al norte del Bosque de los Murciélagos. Lleven las llaves de Musgo y de Espina."),
    "DLG_LUMBER_DONE": ("A floresta voltou a respirar. Fiquem com as minhas lenhas e a minha gratidão.", "The forest breathes again. Keep my firewood and my gratitude.", "El bosque volvió a respirar. Quédense con mi leña y mi gratitud."),
    "DLG_ZECA_1": ("Foice de prata? Ah, essa velha coisa que eu uso para cortar o capim ruim... O Sacristão Ambrósio a quer de volta? Pois leve, eu nunca soube por que ela nunca enferruja.", "A silver sickle? Ah, that old thing I use to cut bad grass... Sacristan Ambrose wants it back? Take it, I never knew why it never rusts.", "¿Una hoz de plata? Ah, esa cosa vieja que uso para cortar la hierba mala... ¿El Sacristán Ambrosio la quiere de vuelta? Llévela, nunca supe por qué nunca se oxida."),
    "DLG_ZECA_2": ("Levem logo, antes que eu me apegue. E digam ao Sacristão que as ervas daninhas daqui já foram cortadas por ela mais vezes do que ele imagina.", "Take it quickly, before I grow attached. And tell the Sacristan the weeds here have been cut by it more times than he imagines.", "Llévenla pronto, antes de que me encariñe. Y díganle al Sacristán que las malas hierbas de aquí han sido cortadas por ella más veces de lo que imagina."),
    "DLG_ZECA_DEFAULT": ("Cuido das ferramentas desta casa desde que o fazendeiro nasceu. Ferramentas boas dão trabalho bom.", "I have tended this house's tools since the farmer was born. Good tools make good work.", "Cuido las herramientas de esta casa desde que nació el granjero. Las buenas herramientas dan buen trabajo."),
}
for lang_i, path in enumerate(("locale/pt_BR.po", "locale/en.po", "locale/es.po", "locale/messages.pot")):
    t = open(path, encoding="utf-8").read()
    add = ""
    for key, trio in T.items():
        val = "" if path.endswith(".pot") else trio[lang_i].replace('"', '\\"')
        if re.search(r'msgid "%s"\n' % re.escape(key), t):
            if val:
                t = re.sub(r'(msgid "%s"\nmsgstr )"[^\n]*"' % re.escape(key), lambda m: m.group(1) + '"' + val.replace("\\", "\\\\") + '"', t)
        else:
            add += '\nmsgid "%s"\nmsgstr "%s"\n' % (key, val)
    open(path, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + add)

try:
    from PIL import Image
    ICONS = "assets/ui/icons/"
    for dst, src, mul in (("sealed_map", "altar_book", (1.3, 1.1, 0.7)), ("silver_sickle", "bone_dagger", (0.9, 1.0, 1.3))):
        im = Image.open(ICONS + src + ".png").convert("RGBA")
        r_, g_, b_, a_ = im.split()
        Image.merge("RGBA", (r_.point(lambda v: min(255, int(v * mul[0]))), g_.point(lambda v: min(255, int(v * mul[1]))), b_.point(lambda v: min(255, int(v * mul[2]))), a_)).save(ICONS + dst + ".png")
except Exception as exc:
    print("aviso: ícones não gerados:", exc)

for path, data in ((ARENAS, arenas), (NPCS, npcs), (QUESTS, quests), (VALUABLES, valuables)):
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(path, "a").write("\n")
print("OK cidades: casa de equipamentos em (%.0f, %.0f), %d NPCs, %d missões" % (sx, sz, 9, 8))
