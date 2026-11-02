# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Testes do núcleo de RPG (Fase 3), com os autoloads carregados:
##   godot --headless --path . res://tests/rpg_tests.tscn
## Confere as fórmulas de 13-balanceamento.md, a bolsa, a validação do
## personagem, os saves (escrita segura, backups e recuperação, lista de
## campanhas, ficha editada fora do jogo) e a troca entre jogadores.

const TEST_ROOT := "user://test_saves"

var _failures := 0
var _checks := 0


func _ready() -> void:
	SaveSystem.root = TEST_ROOT
	_clean(TEST_ROOT)
	_test_new_character()
	_test_progression()
	_test_item_generation()
	_test_item_rules()
	_test_inventory()
	_test_validation()
	_test_saves()
	_test_campaign_list()
	_test_background_saves()
	_test_edited_character()
	_test_trade()
	_test_elements()
	_test_states()
	_test_combos()
	_test_character_element()
	_test_appearance()
	_test_ninja_gear()
	_test_skills()
	_test_archer()
	_test_ninja()
	_test_summoner()
	_test_knight()
	_test_shops()
	_test_town_rules()
	_test_side_quests()
	_test_minibosses_and_relics()
	_test_refine()
	_test_opening()
	_test_sewers()
	_test_explore_map()
	_test_ui_theme()
	_test_tips()
	_test_names()
	_clean(TEST_ROOT)
	if _failures == 0:
		print("OK: %d verificações de RPG passaram" % _checks)
	else:
		printerr("FALHOU: %d de %d verificações" % [_failures, _checks])
	get_tree().quit(1 if _failures else 0)


func _check(ok: bool, what: String) -> void:
	_checks += 1
	if not ok:
		_failures += 1
		printerr("  ✗ " + what)


func _near(a: float, b: float, what: String) -> void:
	_check(absf(a - b) < 0.01, "%s: esperado %s, veio %s" % [what, b, a])


func _test_new_character() -> void:
	var c := CharacterData.create("mage", "female", "Orana")
	_check(c.validate().is_empty(), "personagem novo válido: %s" % [c.validate()])
	_near(c.max_health(), 75, "vida do Mago no nível 1")
	_near(c.max_resource(), 120, "mana do Mago no nível 1")
	_near(c.power(), 25, "poder mágico: cajado de madeira 10 + INT 30 × 0,5")
	_check(c.data.equipment.weapon.material == "wood", "começa com cajado de madeira")
	_check(c.data.equipment.body == null, "começa só com roupa de baixo")
	_check(c.count_of("potion_health") == 3 and c.count_of("potion_resource") == 1, "poções do kit: 3 de vida e 1 de recurso")
	_check(int(c.data.gold) == 150, "começa com 150 de ouro (14-tutorial.md)")


func _test_progression() -> void:
	var c := CharacterData.create("mage", "male", "Oren")
	_check(CharacterData.xp_to_next(1) == 700, "XP para o nível 2 = 700 × 1")
	_check(c.add_xp(700) == 1 and int(c.data.level) == 2, "700 XP sobe para o nível 2")
	_check(int(c.data.free_points) == 5 and int(c.data.skill_points) == 1, "+5 atributos e +1 habilidade por nível")
	_near(c.max_health(), 105, "vida no nível 2 (75 + 30)")
	_check(c.spend_point("int"), "gasta ponto em INT")
	_near(c.max_resource(), 122, "+2 de mana por INT")
	_near(c.power(), 25.5, "+0,5 de poder por INT")
	_check(c.spend_point("vit"), "gasta ponto em VIT")
	_near(c.max_health(), 110, "+5 de vida por VIT")
	_check(not c.spend_point("luck"), "atributo inexistente é recusado")
	c.add_xp(10_000_000)
	_check(int(c.data.level) == 20 and int(c.data.xp) == 0, "nível máximo 20")
	var total := 0
	for n in range(1, 20):
		total += CharacterData.xp_to_next(n)
	_check(total == 133_000, "nível 20 = 133.000 XP no total")


func _test_item_generation() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 42
	for level in [1, 2, 5, 10, 18]:
		for i in 60:
			var rarity := Items.roll_rarity({"common": 50, "magic": 35, "rare": 15}, rng)
			var item := Items.generate_equipment(level, "mage", rarity, rng)
			_check(Items.is_valid(item), "item gerado válido: %s" % item)
			var range_: Array = GameData.rarities[rarity].affixes
			_check(item.affixes.size() >= range_[0] and item.affixes.size() <= range_[1], "afixos da raridade %s" % rarity)
			_check(Items.usable_by_class(item, "mage"), "item da classe do jogador")
			if level > 2:
				_check(GameData.materials[item.material].tier > 0, "pano/madeira não cai depois do nível 2")


func _test_item_rules() -> void:
	var iron_staff := Items.equipment("staff", "iron")
	_near(Items.weapon_damage(iron_staff), 16, "cajado de ferro comum = 10 × 1,6")
	var magic := Items.equipment("staff", "iron", "magic")
	_near(Items.weapon_damage(magic), 17.6, "mágico +10% de dano")
	var steel := Items.equipment("staff", "steel", "common", 6)
	_check(Items.value(steel) == 87, "valor de aço comum nível 6 = 87 (13-balanceamento.md)")
	_check(Items.required_level(Items.equipment("hood", "copper")) == 9, "cobre a partir do nível 9")
	_near(Items.armor(Items.equipment("tunic", "iron"), 0.35), 5.6, "túnica de ferro do Mago")
	var c := CharacterData.create("mage", "male", "Oren")
	for base in ["hood", "tunic", "gloves", "boots"]:
		c.data.equipment[GameData.item_bases[base].slot] = Items.equipment(base, "iron", "common", 4)
	_near(c.armor(), 12.88, "conjunto de ferro do Mago")
	_near(c.damage_reduction(4), 12.88 / (12.88 + 40 + 60), "redução de dano contra nível 4")


func _test_inventory() -> void:
	var c := CharacterData.create("mage", "male", "Oren")
	_check(c.add_item(Items.stack(Items.CONSUMABLE, "potion_health", 30)), "poções empilham")
	_check(c.count_of("potion_health") == 33, "33 poções de vida")
	_check(c.take_one("potion_health") and c.count_of("potion_health") == 32, "usar tira uma")
	var staff := Items.equipment("staff", "iron", "common", 1)
	_check(c.add_item(staff), "cabe um cajado")
	var index: int = c.data.inventory.find(staff)
	_check(c.equip_from_bag(index), "equipa o cajado de ferro")
	_check(c.data.equipment.weapon.material == "iron", "arma trocada")
	_check(c.data.inventory[index].material == "wood", "o de madeira volta para a bolsa")
	_near(c.power(), 31, "poder com cajado de ferro")
	var gold_hood := Items.equipment("hood", "gold", "common", 17)
	c.add_item(gold_hood)
	_check(not c.equip_from_bag(c.data.inventory.find(gold_hood)), "nível insuficiente para ouro")
	_check(c.unequip("weapon"), "desequipa")
	while c.free_slots() > 0:
		c.add_item(Items.equipment("ring", "iron"))
	_check(not c.add_item(Items.equipment("ring", "iron")), "bolsa cheia recusa item")
	_check(not c.unequip("head"), "nada para tirar da cabeça")


func _test_validation() -> void:
	var c := CharacterData.create("mage", "male", "Oren")
	var cheat := c.to_dict()
	cheat.attributes.int = 999
	_check(CharacterData.from_dict(cheat) == null, "recusa atributos editados")
	cheat = c.to_dict()
	cheat.inventory[5] = {"kind": "equipment", "base": "excalibur", "material": "gold", "rarity": "legendary", "level": 20, "affixes": {}, "refine": 0}
	_check(CharacterData.from_dict(cheat) == null, "recusa item inexistente")
	cheat = c.to_dict()
	cheat.level = 99
	_check(CharacterData.from_dict(cheat) == null, "recusa nível acima do máximo")
	_check(CharacterData.from_dict("lixo") == null, "recusa dado que não é personagem")
	_check(CharacterData.from_dict(c.to_dict()) != null, "aceita personagem honesto")


func _test_saves() -> void:
	var c := CharacterData.create("mage", "male", "Oren")
	c.add_xp(1500)
	_check(SaveSystem.save_character(c), "grava personagem")
	var back := SaveSystem.load_character(c.data.id)
	_check(back != null and back.data.level == c.data.level and back.data.name == "Oren", "lê o mesmo personagem")
	_near(back.power(), c.power(), "poder igual depois de ler")
	for i in 5:
		c.data.gold = i
		SaveSystem.save_character(c)
	var path := SaveSystem.character_path(c.data.id)
	_check(FileAccess.file_exists(path + ".bak3") and not FileAccess.file_exists(path + ".bak4"), "mantém 3 backups")
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string("{ corrompido")
	file.close()
	var restored := SaveSystem.load_character(c.data.id)
	_check(restored != null and int(restored.data.gold) == 3 and SaveSystem.restored_from_backup,
		"save corrompido volta do backup mais recente")
	_check(SaveSystem.list_characters().size() == 1, "lista de personagens")
	var campaign := SaveSystem.new_campaign()
	campaign.dead_groups = ["corridor_patrol"]
	SaveSystem.save_campaign(campaign)
	_check(SaveSystem.load_campaign(campaign.id).dead_groups == ["corridor_patrol"], "campanha guarda grupos mortos")


func _test_campaign_list() -> void:
	_check(SaveSystem.format_played(0) == "0:00", "tempo de jogo zerado")
	_check(SaveSystem.format_played(3725) == "1:02", "1 h 2 min de jogo")
	var older := SaveSystem.new_campaign()
	older.hero_names = {"a": "Orana"}
	SaveSystem.save_campaign(older)
	var newer := SaveSystem.new_campaign()
	newer.played_seconds = 600
	SaveSystem.save_campaign(newer)
	newer.updated = "9999-01-01T00:00:00"  # garante a ordem sem depender do relógio
	SaveSystem.write_json(SaveSystem.campaign_path(newer.id), newer)
	var list := SaveSystem.list_campaigns()
	_check(list.size() >= 2 and list[0].id == newer.id, "campanha mais recente primeiro")
	_check(CampaignMenu.local_time("2026-10-31T01:38:00").length() == 16, "data local no formato AAAA-MM-DD HH:MM")
	var text := CampaignMenu.describe(older)
	_check(text.contains("Orana") and text.contains("0:00"), "linha da campanha com heróis e tempo: %s" % text)


func _test_background_saves() -> void:
	# Gravação na thread: duas na fila para o mesmo arquivo viram uma (a mais nova).
	var path := TEST_ROOT.path_join("bg/test.json")
	SaveSystem.write_json(path, {"save_version": 1, "value": 1}, true)
	SaveSystem.write_json(path, {"save_version": 1, "value": 2}, true)
	SaveSystem.flush()
	_check(int(SaveSystem.read_json(path).get("value", 0)) == 2, "gravação em segundo plano grava a mais nova")
	var c := CharacterData.create("mage", "male", "Oren")
	c.data.gold = 77
	SaveSystem.save_character(c, true)
	var back := SaveSystem.load_character(c.data.id)  # ler espera a fila
	_check(back != null and int(back.data.gold) == 77, "ler depois de gravar em segundo plano vê o save novo")
	# Apagar personagem.
	var before := SaveSystem.list_characters().size()
	SaveSystem.delete_character(c.data.id)
	_check(SaveSystem.load_character(c.data.id) == null and SaveSystem.list_characters().size() == before - 1,
		"personagem apagado (com os backups)")
	# Miniatura da campanha.
	var campaign := SaveSystem.new_campaign()
	SaveSystem.save_campaign(campaign, true)
	var image := Image.create_empty(320, 180, false, Image.FORMAT_RGB8)
	image.fill(Color(0.5, 0.2, 0.1))
	SaveSystem.save_thumbnail(campaign.id, image)
	var thumb := SaveSystem.load_thumbnail(campaign.id)
	_check(thumb != null and thumb.get_size() == SaveSystem.THUMB_SIZE, "miniatura gravada e reduzida")
	# Checkpoints alcançados e campos novos em campanhas antigas.
	var old := {"save_version": 1, "id": "antiga", "dead_groups": []}
	var migrated := SaveSystem.migrate_campaign(old)
	_check(migrated.checkpoints_reached == [] and migrated.hero_names == {}, "campanha antiga ganha os campos novos")
	SaveSystem.delete_campaign(campaign.id)
	_check(SaveSystem.load_campaign(campaign.id).is_empty() and SaveSystem.load_thumbnail(campaign.id) == null,
		"campanha apagada com a miniatura")
	_check(not DirAccess.dir_exists_absolute(SaveSystem.campaign_path(campaign.id).get_base_dir()), "pasta da campanha removida")
	# Espaços de save: 12 personagens e 6 campanhas.
	_check(SaveSystem.slot_limit("characters") == 12 and SaveSystem.slot_limit("campaigns") == 6, "limites de espaços")
	while SaveSystem.list_campaigns().size() < SaveSystem.slot_limit("campaigns"):
		SaveSystem.save_campaign(SaveSystem.new_campaign())
	_check(not SaveSystem.can_create_campaign(), "sem espaço para a 7ª campanha")
	SaveSystem.delete_campaign(SaveSystem.list_campaigns()[0].id)
	_check(SaveSystem.can_create_campaign(), "apagar libera um espaço")


func _test_edited_character() -> void:
	var c := CharacterData.create("mage", "female", "Orana")
	_check(not c.is_edited(), "personagem novo não é acusado")
	SaveSystem.save_character(c)
	var back := SaveSystem.load_character(c.data.id)
	_check(back != null and not back.is_edited(), "personagem lido do disco não é acusado (inteiros viram float no JSON)")
	_check(back != null and typeof(back.data.level) == TYPE_INT and typeof(back.data.gold) == TYPE_INT
		and typeof(back.data.attributes.int) == TYPE_INT, "números inteiros continuam int depois do disco")
	_check(back != null and str(back.data.free_points) == "0", "pontos livres sem \".0\"")
	var net := CharacterData.from_dict(JSON.parse_string(JSON.stringify(c.to_dict())))
	_check(net != null and not net.is_edited(), "ficha que passou por JSON continua igual")
	# Edita o arquivo à mão: continua válido, mas o resumo não bate.
	var path := SaveSystem.character_path(c.data.id)
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	d.gold = 99999
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(JSON.stringify(d, "\t"))
	file.close()
	var edited := SaveSystem.load_character(c.data.id)
	_check(edited != null, "ficha editada ainda é aceita (só avisa)")
	_check(edited != null and edited.is_edited(), "ficha editada é detectada")
	var old := c.to_dict()
	old.erase("check")
	_check(not CharacterData.from_dict(old).is_edited(), "ficha antiga sem resumo não é acusada")


func _test_trade() -> void:
	var a := CharacterData.create("mage", "male", "Oren")
	var b := CharacterData.create("mage", "female", "Orana")
	a.data.gold = 100
	b.data.gold = 10
	var staff := Items.equipment("staff", "iron", "magic", 3)
	a.add_item(staff)
	var ring := Items.equipment("ring", "iron", "rare", 3)
	b.add_item(ring)
	var ia: int = a.data.inventory.find(staff)
	var ib: int = b.data.inventory.find(ring)
	var potions_a := a.count_of("potion_health")
	_check(Trade.swap(a, {"items": [], "gold": 0}, b, {"items": [], "gold": 0}) == "TRADE_EMPTY", "troca vazia é recusada")
	_check(Trade.swap(a, {"items": [ia], "gold": 30}, b, {"items": [ib], "gold": 5}) == "", "troca feita")
	_check(a.data.inventory.find(ring) >= 0 and b.data.inventory.find(staff) >= 0, "itens trocados de bolsa")
	_check(a.data.inventory.find(staff) < 0 and b.data.inventory.find(ring) < 0, "nenhum item duplicado")
	_check(int(a.data.gold) == 75 and int(b.data.gold) == 35, "ouro trocado (100 − 30 + 5, 10 − 5 + 30)")
	_check(Trade.swap(a, {"items": [], "gold": 500}, b, {"items": [], "gold": 0}) == "TRADE_CHANGED", "não oferece mais ouro do que tem")
	_check(int(a.data.gold) == 75, "troca recusada não muda nada")
	# Poções empilham na bolsa do outro.
	var ip: int = a.data.inventory.find(a.data.inventory.filter(func(it: Variant) -> bool:
		return it != null and it.get("id", "") == "potion_health")[0])
	_check(Trade.swap(a, {"items": [ip], "gold": 0}, b, {"items": [], "gold": 0}) == "", "dá as poções de vida")
	_check(a.count_of("potion_health") == 0 and b.count_of("potion_health") == 3 + potions_a, "poções empilham no outro")
	# Bolsa cheia: nada muda.
	while b.free_slots() > 0:
		b.add_item(Items.equipment("ring", "iron"))
	var bag_before: Array = b.data.inventory.duplicate(true)
	var ia2: int = a.data.inventory.find(ring)
	_check(Trade.swap(a, {"items": [ia2], "gold": 0}, b, {"items": [], "gold": 0}) == "TRADE_NO_ROOM", "bolsa cheia recusa a troca")
	_check(b.data.inventory == bag_before and a.data.inventory.find(ring) >= 0, "bolsa cheia não perde nem duplica item")


# --- Fase 4: elementos (02-0-elementos.md) ---------------------------------------

func _test_elements() -> void:
	# Ciclo: Água > Fogo > Terra > Ar > Água.
	for pair in [["water", "fire"], ["fire", "earth"], ["earth", "air"], ["air", "water"]]:
		_near(Elements.multiplier(pair[0], pair[1]), 1.5, "%s contra %s (fraqueza)" % pair)
		_check(Elements.weakness_of(pair[1]) == pair[0], "fraqueza de %s é %s" % [pair[1], pair[0]])
	for id in Elements.ALL:
		_near(Elements.multiplier(id, id), 0.5, "%s contra %s (mesmo elemento)" % [id, id])
	_near(Elements.multiplier("fire", "water"), 1.0, "fogo contra água: normal")
	_near(Elements.multiplier("earth", "fire"), 1.0, "terra contra fogo: normal")
	_near(Elements.multiplier("", "earth"), 1.0, "sem elemento: normal")


func _test_states() -> void:
	var s := StatusSet.new()
	s.apply("soaked", 4.0)
	s.tick(3.0)
	s.apply("soaked", 4.0)
	s.tick(3.0)
	_check(s.has("soaked"), "reaplicar renova a duração")
	s.tick(1.5)
	_check(not s.has("soaked"), "estado acaba")
	_near(StatusSet.new().move_mult(), 1.0, "sem estado: velocidade normal")
	s.apply("soaked", 4.0)
	_near(s.move_mult(), 0.8, "molhado: -20% de velocidade")
	s.apply("mud", 1.0)
	_near(s.move_mult(), 0.6, "lentidões não somam: vale a maior (lama 40%)")
	_check(s.can_act(), "molhado ainda age")
	s.apply("frozen", 2.0)
	_check(not s.can_act(), "congelado não age")
	# Queimando: um tique por segundo durante 3 s.
	var burn := StatusSet.new()
	burn.apply("burning", 3.0, 10.0)
	var total := 0.0
	for i in 12:
		total += burn.tick(0.25)
	_near(total, 30.0, "queimando 3 s × 10 por segundo")
	_check(not burn.has("burning"), "queimando acaba")
	# Imunidades e chefes.
	var t := StatusSet.new()
	_check(Elements.apply_state(t, "burning", "fire", false, 5.0) == "", "monstro de fogo não queima")
	_check(Elements.apply_state(t, "soaked", "water", false) == "", "monstro de água não fica molhado")
	_check(Elements.apply_state(t, "stunned", "earth", true) == "slowed" and not t.has("stunned"), "chefe: lentidão no lugar de atordoar")
	var mask := StatusSet.new()
	mask.apply("frozen", 1.0)
	mask.apply("burning", 1.0)
	var ids := StatusSet.ids_from_mask(mask.mask())
	_check(ids.size() == 2 and "frozen" in ids and "burning" in ids, "estados viajam como bits")


func _test_combos() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	var s := StatusSet.new()
	# Golpe forte de Água num monstro de Terra: dano normal, deixa molhado.
	var r := Elements.resolve_hit({"damage": 100.0, "element": "water", "state": "soaked", "crit_chance": 0.0}, "earth", s, false, rng)
	_near(r.damage, 100.0, "água contra terra: dano normal")
	_check(r.effect == "normal" and s.has("soaked"), "ataque forte de água molha")
	# Ar completa: Eletrocutar (+50%, atordoa 1 s, consome o molhado).
	r = Elements.resolve_hit({"damage": 100.0, "element": "air", "state": "", "crit_chance": 0.0}, "earth", s, false, rng)
	_check(r.combo == "electrocute", "molhado + ar = Eletrocutar")
	_near(r.damage, 150.0, "Eletrocutar: +50% (ar contra terra é dano normal)")
	_check(not s.has("soaked") and s.has("stunned"), "consome o molhado e atordoa")
	# Fogo num atordoado: Fundir (+30%) somado à fraqueza (terra é fraca a fogo).
	r = Elements.resolve_hit({"damage": 100.0, "element": "fire", "state": "", "crit_chance": 0.0}, "earth", s, false, rng)
	_check(r.combo == "melt" and r.effect == "weak", "atordoado + fogo = Fundir, na fraqueza")
	_near(r.damage, 100.0 * 1.5 * 1.3, "fraqueza e combo somam")
	# Incêndio: queimando + ar espalha o fogo.
	var b := StatusSet.new()
	b.apply("burning", 3.0, 12.0)
	r = Elements.resolve_hit({"damage": 10.0, "element": "air", "state": "", "crit_chance": 0.0}, "earth", b, false, rng)
	_check(r.combo == "wildfire" and is_equal_approx(r.spread_dps, 12.0) and not b.has("burning"), "queimando + ar = Incêndio")
	# Vapor e Lama viram áreas.
	b.apply("burning", 3.0, 5.0)
	r = Elements.resolve_hit({"damage": 10.0, "element": "water", "state": "", "crit_chance": 0.0}, "earth", b, false, rng)
	_check(r.combo == "steam" and r.zone.get("state", "") == "steam", "queimando + água = Vapor (área)")
	b.apply("soaked", 4.0)
	r = Elements.resolve_hit({"damage": 10.0, "element": "earth", "state": "", "crit_chance": 0.0}, "air", b, false, rng)
	_check(r.combo == "mud" and r.zone.get("state", "") == "mud" and is_equal_approx(r.zone.duration, 5.0), "molhado + terra = Lama (área de 5 s)")
	# Eletrizado: +15% de dano de Ar; congelado: crítico garantido (x1,5).
	var e := StatusSet.new()
	e.apply("shocked", 4.0)
	r = Elements.resolve_hit({"damage": 100.0, "element": "air", "state": "", "crit_chance": 0.0}, "fire", e, false, rng)
	_near(r.damage, 115.0, "eletrizado: +15% de ar")
	var f := StatusSet.new()
	f.apply("frozen", 2.0)
	r = Elements.resolve_hit({"damage": 100.0, "element": "fire", "state": "", "crit_chance": 0.0}, "air", f, false, rng)
	_check(r.crit, "congelado: crítico garantido")
	_near(r.damage, 150.0, "crítico x1,5")
	# Mesmo elemento: metade, número cinza.
	r = Elements.resolve_hit({"damage": 100.0, "element": "earth", "state": "", "crit_chance": 0.0}, "earth", StatusSet.new(), false, rng)
	_check(r.effect == "resist", "mesmo elemento resiste")
	_near(r.damage, 50.0, "resistência: -50%")
	# Queimando do ataque forte: 30% do golpe por segundo.
	var fb := StatusSet.new()
	r = Elements.resolve_hit({"damage": 100.0, "element": "fire", "state": "burning", "crit_chance": 0.0}, "air", fb, false, rng)
	_near(fb.dps("burning"), 30.0, "queimando = 30% do golpe por segundo")
	# Terra: 30% de chance de atordoar.
	var stuns := 0
	for i in 2000:
		var st := StatusSet.new()
		Elements.resolve_hit({"damage": 1.0, "element": "earth", "state": "stunned", "crit_chance": 0.0}, "air", st, false, rng)
		stuns += int(st.has("stunned"))
	_check(stuns > 500 and stuns < 700, "terra atordoa ~30%% das vezes (%d de 2000)" % stuns)


func _test_character_element() -> void:
	var c := CharacterData.create("mage", "female", "Orana", "water")
	_check(c.current_element() == "water" and c.validate().is_empty(), "criado com elemento de Água")
	_check(c.drink_elemental("fire") and c.current_element() == "fire" and c.data.element == "water", "Poção de Fogo troca o elemento; o de origem não muda")
	_check(not c.drink_elemental("fire"), "beber o mesmo elemento de novo não faz nada")
	_check(c.drink_elemental("water") and c.data.element_potion == "", "poção do elemento de origem desfaz a troca")
	c.drink_elemental("air")
	c.end_expedition()
	_check(c.current_element() == "water", "voltar a Tortuga encerra a poção")
	var bad := c.to_dict()
	bad.element = "lava"
	_check(CharacterData.from_dict(bad) == null, "elemento inexistente é recusado")
	# Ficha salva antes da Fase 4 (sem elemento): vira Fogo e não é acusada de editada.
	var old := CharacterData.create("mage", "male", "Oren")
	old.data.erase("element")
	old.data.erase("element_potion")
	old.seal()
	var migrated := CharacterData.from_dict(JSON.parse_string(JSON.stringify(old.to_dict())))
	_check(migrated != null and migrated.data.element == "fire" and not migrated.is_edited(), "ficha antiga ganha Fogo sem ser acusada")
	_near(Items.value(Items.stack(Items.CONSUMABLE, "elemental_potion_fire")), 125.0, "Poção Elemental: 100 + 25 × nível")
	_near(c.crit_chance(), 0.05, "crítico base 5%")


# --- Fase 5: habilidades (02-personagens.md, 02-1-mago.md) -------------------------

func _test_skills() -> void:
	var keys := Skills.keys("mage")
	var levels: Array[int] = []
	for key in keys:
		levels.append(Skills.unlock_level("mage", key))
	var expected: Array[int] = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18]
	_check(levels == expected, "10 habilidades nos níveis 1, 2, 4… 18: %s" % [levels])
	_check(keys[2] == "sharp_mind" and keys[4] == "teleport", "comuns do Mago nos níveis 4 e 8")
	# Toda habilidade existe e tem nome/descrição.
	for element in Elements.ALL:
		for key in keys:
			var id := Skills.skill_id("mage", key, element)
			_check(not Skills.def(id).is_empty(), "habilidade %s/%s existe (%s)" % [element, key, id])
	_check(Skills.skill_id("mage", "element_6", "water") == "healing_rain"
		and Skills.skill_id("mage", "element_18", "earth") == "earthquake", "tabela do elemento")
	# Personagem novo: básica do elemento no rank 1 e no atalho 1.
	var c := CharacterData.create("mage", "female", "Orana", "water")
	_check(c.skill_rank("element_1") == 1 and c.data.skill_slots[0] == "element_1" and c.validate().is_empty(), "começa com a básica no atalho 1")
	_check(c.skill_of("element_1") == "water_bolt", "básica de Água = Jato d'Água")
	_check(not c.can_learn("element_2"), "sem ponto no nível 1")
	c.add_xp(700)
	_check(int(c.data.skill_points) == 1 and c.learn("element_2"), "nível 2: aprende a área")
	_check(c.data.skill_slots[1] == "element_2" and int(c.data.skill_points) == 0, "habilidade nova vai para o atalho livre")
	_check(not c.can_learn("teleport"), "Teleporte só no nível 8")
	_check(c.validate().is_empty(), "ficha com habilidades válida")
	# Poção Elemental troca as do elemento, com os mesmos ranks.
	c.drink_elemental("fire")
	_check(c.skill_of("element_2") == "fireball" and c.skill_rank("element_2") == 1, "Poção de Fogo: Nova de Gelo vira Bola de Fogo, mesmo rank")
	c.end_expedition()
	# Atalhos trocam de lugar.
	_check(c.set_slot(0, "element_2") and c.data.skill_slots[0] == "element_2" and c.data.skill_slots[1] == "element_1", "trocar atalhos")
	_check(not c.set_slot(2, "teleport"), "não põe no atalho o que não aprendeu")
	# Trapaça: rank sem pontos.
	var cheat := c.to_dict()
	cheat.skills.element_2 = 5
	_check(CharacterData.from_dict(cheat) == null, "recusa ranks sem pontos")
	cheat = c.to_dict()
	cheat.skills.meteor = 1
	_check(CharacterData.from_dict(cheat) == null, "recusa habilidade inexistente")
	# Passivas e regras por rank.
	var m := CharacterData.create("mage", "male", "Oren")
	m.add_xp(30000)
	var base_regen := m.resource_regen()
	_check(m.learn("sharp_mind") and m.learn("sharp_mind"), "Mente Afiada rank 2")
	_near(m.resource_regen(), base_regen * 1.2, "Mente Afiada: +10% por rank")
	_check(m.data.skill_slots.find("sharp_mind") < 0, "passiva não vai para atalho")
	var chain := Skills.def("chain_lightning")
	_check(Skills.jumps(chain, 1) == 5 and Skills.jumps(chain, 3) == 6 and Skills.jumps(chain, 5) == 7, "Corrente de Raios: 5, +1 nos ranks 3 e 5")
	_near(Skills.cooldown(Skills.def("teleport"), 3), 6.0, "Teleporte: -1 s por rank")
	_near(Skills.power(Skills.def("fireball"), 3), 1.8, "Bola de Fogo rank 3: 150% + 2 × 15%")
	# Ficha antiga (antes da Fase 5) ganha a básica sem ser acusada.
	var old := CharacterData.create("mage", "male", "Oren")
	old.data.erase("skills")
	old.data.erase("skill_slots")
	old.seal()
	var migrated := CharacterData.from_dict(JSON.parse_string(JSON.stringify(old.to_dict())))
	_check(migrated != null and migrated.skill_rank("element_1") == 1 and not migrated.is_edited(), "ficha antiga ganha a básica")


func _test_archer() -> void:
	var a := CharacterData.create("archer", "female", "Kaela", "earth")
	_check(a.validate().is_empty(), "Arqueiro criado válido: %s" % [a.validate()])
	_near(a.max_health(), 90, "vida do Arqueiro no nível 1")
	_near(a.max_resource(), 100, "Foco inicial 100")
	_near(a.power(), 22.5, "Poder de Tiro: arco de madeira 10 + DES 25 × 0,5")
	_check(a.data.equipment.weapon.base == "bow", "começa com arco de madeira")
	_check(a.skill_rank("precise_shot") == 1 and a.data.skill_slots[0] == "precise_shot", "começa com Tiro Preciso no atalho 1")
	var levels: Array[int] = []
	for key in Skills.keys("archer"):
		levels.append(Skills.unlock_level("archer", key))
	var expected: Array[int] = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18]
	_check(levels == expected, "Arqueiro: 7 de classe + 3 do elemento nos níveis certos: %s" % [levels])
	for element in Elements.ALL:
		for key in Skills.keys("archer"):
			var id := Skills.skill_id("archer", key, element)
			_check(not Skills.def(id).is_empty(), "habilidade do Arqueiro %s/%s existe" % [element, key])
	_check(Skills.skill_id("archer", "element_12", "earth") == "boulder_arrow", "Terra nível 12 = Flecha Rompe-Rocha")
	_check(Skills.count(Skills.def("arrow_fan"), 5, "count") == 7, "Leque de Flechas: 5, +1 nos ranks 3 e 5")
	a.add_xp(30000)
	_check(a.learn("eagle_eye") and a.learn("eagle_eye"), "Olho de Águia rank 2")
	_near(a.crit_chance(), 0.15, "Olho de Águia: +5% de crítico por rank")
	_near(a.crit_mult(), 1.7, "Olho de Águia: +10% de dano crítico por rank")
	# Marcar Alvo soma dano de todos; preso não anda, mas age.
	var s := StatusSet.new()
	Elements.apply_state(s, "marked", "earth", false, 0.15, 8.0)
	var rng := RandomNumberGenerator.new()
	var r := Elements.resolve_hit({"damage": 100.0, "element": "water", "state": "", "crit_chance": 0.0}, "earth", s, false, rng)
	_near(r.damage, 115.0, "alvo marcado recebe +15%")
	var root := StatusSet.new()
	root.apply("rooted", 2.0)
	_check(root.move_mult() == 0.0 and root.can_act(), "preso: não anda, mas ataca")
	# Flecha Incendiária: queimadura em dobro.
	var b := StatusSet.new()
	Elements.resolve_hit({"damage": 100.0, "element": "fire", "state": "burning", "crit_chance": 0.0, "dot_mult": 2.0}, "air", b, false, rng)
	_near(b.dps("burning"), 60.0, "queimadura dobrada: 2 × 30% por segundo")


func _test_ninja() -> void:
	var n := CharacterData.create("ninja", "male", "Ren", "air")
	_check(n.validate().is_empty(), "Ninja criado válido: %s" % [n.validate()])
	_near(n.max_health(), 130, "vida do Ninja no nível 1")
	_near(n.power(), 22.5, "Poder de Lâmina: adagas de madeira 10 + DES 25 × 0,5")
	_near(n.evasion_chance(), 0.10, "evasão base 10%")
	_near(n.gold_find_bonus(), 0.10, "traço Ladrão: +10% de ouro")
	_check(n.data.equipment.weapon.base == "daggers" and n.data.skill_slots[0] == "twin_slash", "adagas e Corte Duplo no atalho 1")
	_near(CharacterData.create("mage", "male", "Oren").evasion_chance(), 0.0, "Mago não tem evasão")
	n.add_xp(200000)
	n.data.free_points = int(n.data.free_points) - 10
	n.data.attributes.dex = int(n.data.attributes.dex) + 10
	_near(n.evasion_chance(), 0.12, "evasão +0,2% por ponto de DES")
	while n.can_learn("evasion"):
		n.learn("evasion")
	_near(n.evasion_chance(), 0.12 + 0.05 + 0.02 * 4, "passiva Evasão rank 5: +5% e +2% por rank")
	for element in Elements.ALL:
		for key in Skills.keys("ninja"):
			_check(not Skills.def(Skills.skill_id("ninja", key, element)).is_empty(), "habilidade do Ninja %s/%s existe" % [element, key])


func _test_summoner() -> void:
	var s := CharacterData.create("summoner", "female", "Aria", "earth")
	_check(s.validate().is_empty(), "Invocador criado válido: %s" % [s.validate()])
	_near(s.max_health(), 80, "vida do Invocador no nível 1")
	_near(s.max_resource(), 120, "Essência inicial 120")
	_near(s.power(), 25, "Poder de Invocação: livro de madeira 10 + INT 30 × 0,5")
	_check(s.data.equipment.weapon.base == "book" and s.data.skill_slots[0] == "call_companion", "livro e Chamar Companheiro no atalho 1")
	_check(GameData.companions.by_element.earth == "boar" and GameData.companions.by_element.water == "otter", "companheiro principal de cada elemento")
	_check(Skills.count(Skills.def("call_companion"), 5, "count") == 3, "até 3 companheiros no rank 5")
	for element in Elements.ALL:
		for key in Skills.keys("summoner"):
			_check(not Skills.def(Skills.skill_id("summoner", key, element)).is_empty(), "habilidade do Invocador %s/%s existe" % [element, key])


func _test_knight() -> void:
	var k := CharacterData.create("knight", "female", "Dália", "fire")
	_check(k.validate().is_empty(), "Cavaleiro criado válido: %s" % [k.validate()])
	_near(k.max_health(), 150, "vida do Cavaleiro no nível 1")
	_near(k.max_resource(), 100, "Ímpeto 100 (FOR inicial 25)")
	_near(k.power(), 22.5, "Poder de Ataque: lança de madeira 10 + FOR 25 × 0,5")
	_check(k.data.equipment.weapon.base == "lance" and k.data.skill_slots[0] == "lance_thrust", "lança e Estocada no atalho 1")
	k.add_xp(30000)
	_check(k.learn("heavy_armor") and k.learn("heavy_armor"), "Armadura Pesada rank 2")
	_near(k.passive_value("heavy_armor"), 0.08, "Armadura Pesada: -6%, -2% por rank")
	for element in Elements.ALL:
		for key in Skills.keys("knight"):
			_check(not Skills.def(Skills.skill_id("knight", key, element)).is_empty(), "habilidade do Cavaleiro %s/%s existe" % [element, key])
	# Barda do cavalo: só o Cavaleiro equipa; a armadura só conta montado.
	var barding := Items.equipment("barding", "iron", "common", 3)
	_check(k.can_equip(barding) and not CharacterData.create("mage", "male", "Oren").can_equip(barding), "barda é só do Cavaleiro")
	k.add_item(barding)
	_check(k.equip_from_bag(k.data.inventory.find(barding)) and k.data.equipment.barding != null, "equipa a barda")
	_check(k.armor(true) > k.armor(false), "barda conta montado, não a pé")
	_check(k.equipment_visual().get("barding", "") == "iron", "barda aparece no cavalo")
	var old := CharacterData.create("knight", "male", "Dorian")
	old.data.equipment.erase("barding")
	old.seal()
	var migrated := CharacterData.from_dict(JSON.parse_string(JSON.stringify(old.to_dict())))
	_check(migrated != null and migrated.data.equipment.has("barding") and not migrated.is_edited(), "ficha antiga ganha o slot da barda")
	# Bloqueio por classe (02-personagens.md): só o Arqueiro não bloqueia.
	for cls_id in GameData.classes:
		_check(GameData.classes[cls_id].has("block") == (cls_id != "archer"), "bloqueio de %s" % cls_id)
	# As 5 classes do jogo existem e são jogáveis.
	_check(GameData.classes.size() == 5, "5 classes: %s" % [GameData.classes.keys()])


# --- Fase 6: Tortuga (lojas, missões) ---------------------------------------------

func _test_shops() -> void:
	var c := CharacterData.create("mage", "female", "Orana", "water")
	var rng := RandomNumberGenerator.new()
	rng.seed = 3
	var ship := Shops.new_ship(1, rng)
	# Boticário: preços por nível (13-balanceamento.md 5.3).
	var potions := Shops.stock("potions", c, ship)
	_check(potions.size() == 2 and potions[0].id == "potion_health", "Boticário vende poções de vida e de recurso")
	_check(Shops.buy_price("potions", potions[0], 1) == 18 and Shops.buy_price("potions", potions[0], 5) == 42, "poção de vida: 12 + 6 × nível")
	# Rua Principal: comuns da classe, 2x o valor.
	var weapons := Shops.stock("weapons", c, ship)
	_check(weapons.size() == 3 and weapons.all(func(i: Dictionary) -> bool: return i.base == "staff" and i.rarity == "common"), "armas do Mago: cajados de madeira, ferro e aço")
	_check(Shops.buy_price("weapons", weapons[1], 1) == 2 * Items.value(weapons[1]), "Rua Principal: 2x o valor")
	var armor := Shops.stock("armor", c, ship)
	_check(armor.all(func(i: Dictionary) -> bool: return Items.usable_by_class(i, "mage")), "armaduras só da classe")
	_check(Shops.stock("weapons", c, ship) == weapons, "estoque da Rua Principal é sempre o mesmo")
	# Mercado Pirata: 3 a 6 itens, nunca comum nem lendário, 3x; Poções Elementais.
	var pirate := Shops.stock("pirate", c, ship)
	var gear := pirate.filter(func(i: Dictionary) -> bool: return i.kind == Items.EQUIPMENT)
	_check(gear.size() >= 3 and gear.size() <= 6, "pirata: 3 a 6 itens (%d)" % gear.size())
	_check(gear.all(func(i: Dictionary) -> bool: return i.rarity in ["magic", "rare", "unique"]), "pirata: mágico, raro ou único")
	_check(pirate.filter(func(i: Dictionary) -> bool: return i.kind == Items.CONSUMABLE).size() == 4, "pirata: 4 Poções Elementais")
	_check(Shops.buy_price("pirate", gear[0], 1) == roundi(Items.value(gear[0]) * 3.0), "pirata: 3x o valor")
	_check(Shops.buy_price("pirate", Items.stack(Items.CONSUMABLE, "elemental_potion_fire"), 4) == 200, "Poção Elemental: 100 + 25 × nível")
	_check(Shops.stock("pirate", c, ship) == pirate, "o mesmo navio mostra o mesmo estoque (servidor e cliente)")
	var other_ship := Shops.new_ship(2, rng)
	_check(Shops.stock("pirate", c, other_ship) != pirate, "navio novo, estoque novo")
	# Venda: 25% do equipamento; valiosos só com os piratas, pela variação do dia.
	var staff := Items.equipment("staff", "iron", "common", 3)
	_check(Shops.sell_price("weapons", staff, 1, ship) == roundi(Items.value(staff) * 0.25), "venda: 25% do valor")
	var coins := Items.stack(Items.VALUABLE, "old_coins", 2)
	_check(Shops.sell_price("potions", coins, 1, ship) == -1, "Boticário não compra valiosos")
	var mult := Shops.valuable_mult(ship, "old_coins")
	_check(mult >= 0.8 and mult <= 1.2 and mult == Shops.valuable_mult(ship, "old_coins"), "variação do dia entre 80%% e 120%%: %.2f" % mult)
	_check(Shops.sell_price("pirate", coins, 1, ship) == roundi(20 * mult) * 2, "piratas pagam o valor × variação pela pilha")


func _test_town_rules() -> void:
	_check(Town.dialogue_index("old_drunk", {}) == 0, "Velho Bêbado oferece a primeira missão")
	_check(GameData.npcs.old_drunk.dialogues[0].offer == "sewer_treasure", "a missão é o tesouro do esgoto")
	_check(Town.dialogue_index("old_drunk", {"sewer_treasure": "active"}) == 1, "com a missão ativa, outra fala")
	_check(Town.dialogue_index("old_drunk", {"sewer_treasure": "done"}) == 2, "depois de concluída, outra fala")
	var campaign := SaveSystem.new_campaign()
	_check(campaign.area == "tavern" and campaign.quests.is_empty(), "campanha nova começa na Taverna")
	var old := {"save_version": 1, "id": "antiga", "area": "prototype_arena"}
	var migrated := SaveSystem.migrate_campaign(old)
	_check(migrated.has("quests") and migrated.has("ship") and migrated.unlocked == [], "campanha antiga ganha missões e navio")


## Dois mini-chefes por mapa de combate e as relíquias de missão do Padre da Capital.
func _test_minibosses_and_relics() -> void:
	var capital: Dictionary = GameData.arenas.capital_01_aurenhold
	var maps := {"Esgoto": ["sewers_01_drains", "sewers_02_canals", "sewers_03_war_passage", "sewers_04_nest"], "Floresta": ["forest_01_path"],
		"Ruínas": ["ruins_01_city"], "Cemitério": ["cemetery_01_yard"], "Forte": ["fort_01_gate"], "Mina": ["mine_01_crystal_vein"], "Deserto": ["desert_01_canyon"]}
	for map_name: String in maps:
		var found := {}
		for area_id: String in maps[map_name]:
			for e: Dictionary in GameData.arenas[area_id].encounters:
				for m: Dictionary in e.monsters:
					if GameData.monsters.get(m.monster, {}).get("category", "") == "miniboss":
						found[m.monster] = true
		_check(found.size() == 2, "%s tem 2 mini-chefes (%d)" % [map_name, found.size()])
	for quest_id in ["royal_heart", "royal_lungs", "royal_skull", "royal_soul", "royal_banquet"]:
		var quest: Dictionary = GameData.quests[quest_id]
		var relic: Dictionary = GameData.valuables.get(quest.item, {})
		var droppers := GameData.monsters.values().filter(func(m: Variant) -> bool: return m is Dictionary and m.get("quest_drop", "") == quest.item and m.get("category", "") == "miniboss")
		_check(relic.get("quest_item", false) and Items.is_valid(Items.stack(Items.VALUABLE, quest.item)) and droppers.size() == 1
			and GameData.arenas.has(quest.area) and GameData.npcs.has(quest.giver) and tr(quest.name_key) != quest.name_key,
			"relíquia de %s: item, mini-chefe que larga, mapa e quem pede" % quest_id)
		_check(Shops.sell_price("blacksmith", Items.stack(Items.VALUABLE, quest.item), 1, {}) < 0, "a relíquia de %s não se vende" % quest_id)
	var chain := ["royal_heart", "royal_lungs", "royal_skull", "royal_soul"]
	var priest_ok := Town.dialogue_index("priest", {}) == 0
	var states := {}
	for i in chain.size():
		priest_ok = priest_ok and Town.dialogue_index("priest", states) == 2 * i
		states[chain[i]] = "active"
		priest_ok = priest_ok and Town.dialogue_index("priest", states) == 2 * i + 1
		states[chain[i]] = "done"
	priest_ok = priest_ok and Town.dialogue_index("priest", states) == 2 * chain.size()
	_check(priest_ok, "o Padre oferece, lembra e agradece as quatro relíquias")
	_check(Town.dialogue_index("court_jester", {}) == 0 and Town.dialogue_index("court_jester", {"royal_banquet": "active"}) == 1
		and Town.dialogue_index("court_jester", {"royal_banquet": "done"}) == 2, "o Bobo oferece, lembra e agradece a carne")
	_check(capital.decor.filter(func(d: Dictionary) -> bool: return d.get("piece", "") == "Food_Apple").size() >= 8, "mesa farta com maçãs na sala do rei")
	_check(capital.rooms.any(func(r: Dictionary) -> bool: return r.id == "church") and capital.rooms.any(func(r: Dictionary) -> bool: return r.id == "king_bedroom")
		and capital.props.any(func(p: Dictionary) -> bool: return p.get("npc", "") == "priest" and p.position[0] < -15.0 and p.position[1] < -39.0)
		and capital.decor.any(func(d: Dictionary) -> bool: return d.get("piece", "") == "Podium")
		and capital.decor.filter(func(d: Dictionary) -> bool: return d.get("piece", "") == "Chair_1" and d.position[0] < -15.0).size() >= 6, "igreja com o Padre, o altar e as cadeiras; quarto do rei ao lado")
	_check(capital.rooms.any(func(r: Dictionary) -> bool: return r.id == "throne_room")
		and capital.props.any(func(p: Dictionary) -> bool: return p.get("npc", "") == "court_jester" and p.position[1] < -39.0)
		and capital.decor.any(func(d: Dictionary) -> bool: return d.get("piece", "") == "Sofa_Group"), "a sala do rei tem o Bobo da Corte e os sofás")


func _test_side_quests() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 11
	var campaign := SaveSystem.new_campaign()
	_check(SideQuests.generate_visitors(campaign, rng).is_empty(), "sem mapa liberado, sem visitantes")
	campaign.unlocked = ["sewer_entrance"]
	var templates := {}
	for i in 30:
		var visitors := SideQuests.generate_visitors(campaign, rng)
		_check(visitors.size() >= 2 and visitors.size() <= 4, "2 a 4 visitantes por volta")
		for v: Dictionary in visitors:
			var q: Dictionary = v.quest
			templates[q.template] = true
			_check(q.template in GameData.visitors.types[v.type].templates, "o visitante conta o tipo de história dele")
			_check(GameData.bestiary.has(q.target) and String(q.area).begins_with("sewers_") and q.area != "sewers_04_nest",
				"história de uma criatura do Esgoto (fora do Ninho): %s em %s" % [q.target, q.area])
			_check(q.target in SideQuests.creatures_in(q.area), "a criatura existe na área da missão")
			_check(SideQuests.visitor_lines(v).size() == 3, "roteiro: o que é, lenda e pista")
			if q.template == "hunt":
				_check(int(q.count) >= 4 and int(q.count) <= 8 and int(q.progress) == 0, "caçada de 4 a 8")
			if q.template == "rumor":
				_check(q.outcome in ["treasure", "ambush", "nothing"], "rumor: tesouro, emboscada ou nada")
	_check(templates.size() == 3, "os três modelos aparecem: %s" % [templates.keys()])
	_check(SideQuests.creatures_in("prototype_arena").size() == 2, "criaturas do bestiário que existem na área de teste")
	var title := SideQuests.title({"template": "hunt", "target": "plague_frog", "area": "prototype_arena", "count": 5, "progress": 2, "status": "active"})
	_check(title.contains("2/5"), "título da caçada com progresso: %s" % title)


func _test_refine() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	var staff := Items.equipment("staff", "steel", "common", 6)
	_check(Refine.scroll_for(staff, false) == "scroll_refine_weapon_steel", "pergaminho de arma do mesmo material")
	_check(Refine.scroll_for(Items.equipment("hood", "iron"), true) == "blessed_scroll_refine_armor_iron", "pergaminho abençoado de armadura")
	_check(Refine.refuse_reason(Items.equipment("staff", "wood")) == "REFINE_NO_TIER0", "madeira não refina")
	for i in 3:
		_check(Refine.attempt(staff, false, rng) == "ok", "+%d é seguro" % (i + 1))
	_near(Items.weapon_damage(staff), 10 * 2.3 * 1.15, "+3: +15% no dano base")
	_near(Refine.chance(staff), 0.65, "+4: 65%")
	var results := {"ok": 0, "broken": 0}
	for i in 2000:
		var test := Items.equipment("staff", "steel", "common", 6)
		test.refine = 3
		results[Refine.attempt(test, false, rng)] += 1
	_check(results.ok > 1200 and results.ok < 1400, "+4 dá certo ~65%% das vezes (%d de 2000)" % results.ok)
	var unique := Items.equipment("staff", "steel", "unique", 6)
	unique.refine = 4
	var blessed := Items.equipment("staff", "steel", "common", 6)
	blessed.refine = 4
	var never := RandomNumberGenerator.new()
	never.seed = 1
	var u_result := ""
	var b_result := ""
	while u_result != "reset":
		unique.refine = 4
		u_result = Refine.attempt(unique, false, never)
	while b_result != "reset":
		blessed.refine = 4
		b_result = Refine.attempt(blessed, true, never)
	_check(unique.refine == 0 and blessed.refine == 0, "único e pergaminho abençoado: falha volta a +0, não quebra")
	_check(Refine.crystals_for(Items.equipment("staff", "steel", "common", 6)) == 4, "cristais: 1 + nível/2 + refino")
	# Conjunto de armadura em +4: +5% de vida; aura = refino da arma.
	var c := CharacterData.create("mage", "male", "Oren")
	var health := c.max_health()
	for base in ["hood", "tunic", "gloves", "boots"]:
		var piece := Items.equipment(base, "iron")
		piece.refine = 4
		c.data.equipment[GameData.item_bases[base].slot] = piece
	_check(c.armor_set_refined(), "conjunto todo em +4")
	_near(c.max_health(), health * 1.05, "conjunto +4: +5% de vida")
	c.data.equipment.weapon = staff
	_check(c.aura_level() == 1, "brilho no nível do rank das roupas (ferro = D = 1), não do refino da arma")
	c.data.equipment.body = Items.equipment("tunic", "gold")
	_check(c.aura_level() == 2, "brilho: média dos ranks vestidos (3 D e 1 S = 2)")


func _test_opening() -> void:
	# Solo com um Mago: ele conta primeiro; os outros 4 heróis entram como NPCs, na ordem dos docs.
	var cast := Opening.cast([{"name": "Zed", "class_id": "mage", "sex": "female"}])
	_check(cast.size() == 5, "abertura: 5 heróis no solo (%d)" % cast.size())
	_check(cast[0].name == "Zed" and cast[0].player, "o herói do jogador conta primeiro")
	_check(cast.slice(1).map(func(h: Dictionary) -> String: return h.class_id) == ["knight", "ninja", "archer", "summoner"],
		"os outros na ordem de chegada em Tortuga")
	_check(cast.slice(1).all(func(h: Dictionary) -> bool: return not h.player), "os outros são NPCs")
	# Co-op com dois heróis: os dois contam, e só os 3 que faltam são NPCs.
	var coop := Opening.cast([{"name": "A", "class_id": "knight", "sex": "female"}, {"name": "B", "class_id": "ninja", "sex": "male"}])
	_check(coop.size() == 5 and coop[0].player and coop[1].player and not coop[2].player, "co-op: jogadores primeiro, depois 3 NPCs")
	_check(Opening.story_of("knight", "female").scene == "OPENING_SCENE_KNIGHT_FEMALE", "Dália tem a própria história")
	_check(Opening.story_of("mage", "female").scene == "OPENING_SCENE_MAGE", "Mago: mesma história nas duas versões")
	var lines := Opening.lines([{"name": "Zed", "class_id": "mage", "sex": "male"}])
	_check(lines[0].speaker == "" and lines[0].key == "OPENING_SCENE_MAGE", "começa com a cena do herói do jogador")
	_check(lines[1].speaker == "Zed", "as falas são do herói")
	_check(lines.filter(func(l: Dictionary) -> bool: return l.key == "OPENING_NPC_INVITE").size() == 4, "cada NPC convida o grupo")
	_check(lines[-1].key == "OPENING_DRUNK_CALL", "termina com o velho bêbado chamando")
	for line: Dictionary in lines:
		_check(tr(line.key) != line.key, "fala traduzida: " + String(line.key))
	_check(GameData.quests.has(GameData.opening.quest), "a abertura leva a uma missão que existe")


func _test_sewers() -> void:
	var areas := ["sewers_01_drains", "sewers_02_canals", "sewers_03_war_passage", "sewers_04_nest"]
	var ids := {}
	for i in areas.size():
		var area: Dictionary = GameData.arenas[areas[i]]
		_check(area.map_id == "map_sewers" and area.has("entries") and area.entries.has("start"), "%s: mapa e entrada" % areas[i])
		_check(int(area.area_level) == (1 if i < 2 else 2), "%s: nível da área (1, 1, 2, 2)" % areas[i])
		for encounter: Dictionary in area.encounters:
			_check(not ids.has(encounter.id), "encontro com ID único: " + String(encounter.id))
			ids[encounter.id] = true
			for entry: Dictionary in encounter.monsters:
				_check(GameData.monsters.has(entry.monster), "monstro existe: " + String(entry.monster))
		var exits: Array = area.props.filter(func(p: Dictionary) -> bool: return p.get("id", "") == "deeper")
		if i < 3:
			_check(exits.size() == 1 and exits[0].to == areas[i + 1] and exits[0].get("group", false), "%s leva à área seguinte, em grupo" % areas[i])
			_check(area.props.any(func(p: Dictionary) -> bool: return p.kind == "chest" and p.get("secret", false)), "%s tem um segredo" % areas[i])
			_check(not area.get("final", false), "%s não é a área final" % areas[i])
		for room: Dictionary in area.rooms:
			for door: String in room.doors:
				_check(door.get_slice(":", 0) in ["north", "south", "east", "west"], "porta válida: " + door)
	var nest: Dictionary = GameData.arenas.sewers_04_nest
	_check(nest.final and nest.encounters.any(func(e: Dictionary) -> bool: return e.monsters[0].monster == "demon_rat_queen"), "o Ninho é a área final, com a Rainha")
	_check(nest.props.filter(func(p: Dictionary) -> bool: return p.get("after_victory", false)).size() == 1, "portal só depois da vitória")
	_check(nest.props.any(func(p: Dictionary) -> bool: return p.kind == "chest" and p.get("key", "") == GameData.monsters.demon_rat_queen.get("drops_key", "-")),
		"tesouro trancado com a chave que a Rainha deixa cair")
	_check(GameData.quests.sewer_treasure.area == "sewers_04_nest", "o tesouro do esgoto termina no Ninho")
	_check(GameData.arenas.sewers_01_drains.props.any(func(p: Dictionary) -> bool: return p.get("id", "") == "return_portal"), "portal de retorno na entrada do mapa")
	var grate: Array = GameData.arenas.tortuga.props.filter(func(p: Dictionary) -> bool: return p.get("id", "") == "sewer_entrance")
	_check(grate[0].to == "sewers_01_drains", "o bueiro desce para os Bueiros da Rua Principal")
	# Categorias (03-inimigos.md): elite vida x3 e dano x1,5; mini-chefe x6/x1,8; chefe com fator 4,3.
	var rat := Enemy.create({"monster_id": "plague_frog", "position": Vector3.ZERO, "level": 1})
	var elite := Enemy.create({"monster_id": "plague_frog", "position": Vector3.ZERO, "level": 1, "rank": "elite", "modifier": "toxic"})
	_near(elite.max_health, rat.max_health * 3.0, "elite: vida x3")
	_near(elite.attack_damage(), rat.attack_damage() * 1.5, "elite: dano x1,5")
	_check(elite.category() == "elite" and elite.modifier == "toxic" and elite.xp_value() == 25.0, "elite: categoria, modificador e XP 25 x nível")
	var gator := Enemy.create({"monster_id": "old_gator", "position": Vector3.ZERO, "level": 2})
	_near(gator.max_health, 150 * 1.12 * 6, "Jacaré Velho: vida 150 x 1,12 x 6")
	var queen := Enemy.create({"monster_id": "demon_rat_queen", "position": Vector3.ZERO, "level": 2})
	_near(queen.max_health, 1000 * 1.12 * 4.3, "Rainha: ~4.800 de vida no solo")
	_check(queen.is_boss() and queen.category() == "boss", "Rainha é chefe")
	for e: Enemy in [rat, elite, gator, queen]:
		e.free()
	_check(GameData.loot.elite.items[0] >= 1 and GameData.loot.miniboss.guaranteed == "rare", "elite sempre deixa item; mini-chefe garante raro")
	# Caçada: o bando aparece num ponto da área, com uma elite, só o que falta matar.
	var quest := {"id": "h1", "template": "hunt", "target": "acid_toad", "area": "sewers_02_canals", "count": 5, "progress": 2, "spot": 1, "status": "active"}
	var hunt := SideQuests.hunt_encounter(quest)
	_check(hunt.id == "hunt_h1" and hunt.monsters[0].rank == "elite" and hunt.monsters[0].monster == "acid_toad", "bando da caçada com uma elite")
	_check(int(hunt.monsters[0].count) + int(hunt.monsters[1].count) == 3, "só os 3 que faltam")
	_check(hunt.position == GameData.arenas.sewers_02_canals.quest_spots[1], "no ponto da missão")
	quest.progress = 5
	_check(SideQuests.hunt_encounter(quest).is_empty(), "caçada completa não traz bando")
	_check(", ".join(SideQuests.open_maps(["sewer_entrance"])) == "sewers_01_drains, sewers_02_canals, sewers_03_war_passage",
		"missões secundárias nas áreas 1 a 3 do Esgoto")
	_check(SideQuests.creatures_in("sewers_03_war_passage").has("sewer_gator"), "o Jacaré mora na Passagem da Guerra")
	# A Rainha: fases pela vida (60% e 25%).
	var thresholds: Array = GameData.monsters.demon_rat_queen.phases
	_check(RatQueen.phase_for(1.0, thresholds) == 1 and RatQueen.phase_for(0.61, thresholds) == 1, "fase 1 até 60%")
	_check(RatQueen.phase_for(0.6, thresholds) == 2 and RatQueen.phase_for(0.26, thresholds) == 2, "fase 2 de 60% a 25%")
	_check(RatQueen.phase_for(0.25, thresholds) == 3 and RatQueen.phase_for(0.01, thresholds) == 3, "fase 3 abaixo de 25%")
	_check(GameData.monsters.demon_rat_queen.phase_keys.size() == 3, "nome das 3 fases")
	# Tesouro: um lendário por classe, do arsenal real; relíquia e mapa das Ruínas.
	var rng := RandomNumberGenerator.new()
	rng.seed = 3
	for class_id: String in GameData.classes:
		var id := Legendaries.for_boss("demon_rat_queen", class_id)
		_check(id != "", "lendário do Esgoto para " + class_id)
		if id == "":
			continue
		var item := Legendaries.create(id, 2, rng)
		_check(Items.is_valid(item) and item.rarity == "legendary" and item.material == "iron", "lendário válido, de ferro: " + id)
		_check(Items.usable_by_class(item, class_id) and Items.required_level(item) <= 2, "%s usa o lendário no nível 2" % class_id)
		_check(Items.display_name(item) == tr(GameData.legendaries[id].name_key), "lendário com nome próprio")
		_check(Items.describe(item).has(tr(GameData.legendaries[id].lore_key)), "lendário com lore")
		_check(Items.weapon_damage(item) > Items.weapon_damage(Items.equipment(item.base, "iron", "rare", 2)), "lendário bate mais que raro")
	var treasure: Dictionary = GameData.loot.treasure_sewers
	_check(GameData.relics.has(treasure.relic) and treasure.unlocks == "map_ruins", "tesouro: relíquia e o mapa das Ruínas")
	for kind in ["weapon", "armor"]:
		_check(GameData.consumables.has("scroll_refine_%s_iron" % kind) and GameData.consumables.has("blessed_scroll_refine_%s_iron" % kind),
			"pergaminhos de ferro do tesouro existem (%s)" % kind)
	_check(GameData.monsters.spawn_nest.ai == "static" and GameData.monsters.spawn_nest.fire_mult == 2.0, "ninho parado, Fogo em dobro")
	# Barris e caixotes (decisão do autor): sorteio por peso; monstros ~10%, poções ~25%.
	var outcomes := {}
	var roll_rng := RandomNumberGenerator.new()
	roll_rng.seed = 21
	for i in 4000:
		var outcome := Breakables.roll(roll_rng)
		outcomes[outcome] = int(outcomes.get(outcome, 0)) + 1
	_check(outcomes.keys().all(func(k: String) -> bool: return GameData.loot.breakable.outcomes.has(k)), "só sai o que está na tabela")
	_check(int(outcomes.get("monsters", 0)) > 300 and int(outcomes.get("monsters", 0)) < 500, "monstros em ~10%% (%d de 4000)" % int(outcomes.get("monsters", 0)))
	var potions := int(outcomes.get("potion_health", 0)) + int(outcomes.get("potion_resource", 0))
	_check(potions > 850 and potions < 1150, "poções em ~25%% (%d de 4000)" % potions)
	for area_id in ["sewers_01_drains", "sewers_02_canals", "sewers_03_war_passage", "sewers_04_nest"]:
		var boxes: Array = GameData.arenas[area_id].get("breakables", [])
		_check(boxes.size() >= 4 and boxes.all(func(b: Dictionary) -> bool: return GameData.monsters.get(b.monster, {}).get("breakable", false)),
			"%s tem barris e caixotes" % area_id)
	# Ruínas: caixotes que só soltam poção (tabela "breakable_potion").
	var ruin_boxes: Array = GameData.arenas.ruins_01_city.get("breakables", [])
	_check(ruin_boxes.size() >= 10 and ruin_boxes.all(func(b: Dictionary) -> bool:
		return GameData.monsters.get(b.monster, {}).get("breakable", false) and GameData.loot.has(String(b.get("table", "")))), "Ruínas têm caixotes de poção")
	var ruin_potions := true
	for i in 200:
		ruin_potions = ruin_potions and Breakables.roll(roll_rng, "breakable_potion") in ["potion_health", "potion_resource"]
	_check(ruin_potions, "caixotes das Ruínas só soltam poção")
	# Ruínas: Leônidas dá a missão dos goblins (termina ao limpar os dois bandos).
	var ruins: Dictionary = GameData.arenas.ruins_01_city
	var ruin_ids: Array = ruins.encounters.map(func(e: Dictionary) -> String: return e.id)
	var goblin_quest: Dictionary = GameData.quests.get("ruins_goblins", {})
	_check(goblin_quest.get("area", "") == "ruins_01_city" and goblin_quest.get("clear", []).size() == 2
		and goblin_quest.clear.all(func(id: String) -> bool: return id in ruin_ids)
		and ruins.props.any(func(p: Dictionary) -> bool: return p.get("npc", "") == goblin_quest.get("giver", "")) and tr(goblin_quest.get("name_key", "")) != goblin_quest.get("name_key", ""),
		"missão das Ruínas: encontros e quem a dá existem")
	_check(Town.dialogue_index("ruins_spartan", {}) == 0 and Town.dialogue_index("ruins_spartan", {"ruins_goblins": "active"}) == 1
		and Town.dialogue_index("ruins_spartan", {"ruins_goblins": "done"}) == 2 and NpcModel.has_model("ruins_spartan"),
		"conversa de Leônidas: oferece, lembra e agradece; tem modelo próprio")
	# Floresta: três golens (fogo, gelo, pedra), elites corpo a corpo com modelo.
	# (o de gelo é um encontro comum; os de pedra e de fogo são mini-chefes invocados pelos NPCs das praças, em `summon`.)
	var golems: Array = GameData.arenas.forest_01_path.encounters.filter(func(e: Dictionary) -> bool: return String(e.id).begins_with("f_golem_"))
	for prop: Dictionary in GameData.arenas.forest_01_path.props:
		if prop.has("summon"):
			golems.append(prop.summon)
	_check(golems.size() == 2 and golems.all(func(e: Dictionary) -> bool:
		var m: Dictionary = GameData.monsters.get(e.monsters[0].monster, {})
		return m.get("category", "") == "elite" and MonsterModel.FAMILIES.has(m.get("look", "")) and float(m.get("damage", 0)) > 0.0), "Floresta tem os dois golens invocados (mini-chefes)")
	# Floresta: a Toca dos Répteis só tem o Rei Golem de Pedra (maior) e o Guardião (menor); sem bandos de répteis.
	var den: Array = GameData.arenas.forest_01_path.encounters.filter(func(e: Dictionary) -> bool: return e.id == "f_viper_queen")
	var no_reptiles: bool = GameData.arenas.forest_01_path.encounters.all(func(e: Dictionary) -> bool: return not e.id.begins_with("f_reptiles"))
	_check(den.size() == 1 and den[0].monsters.size() == 2 and den[0].monsters[0].monster == "viper_queen" and den[0].monsters[1].monster == "forest_tomb_guardian"
		and MonsterModel.FAMILIES.has(GameData.monsters.viper_queen.look) and MonsterModel.FAMILIES.has(GameData.monsters.forest_tomb_guardian.look)
		and GameData.monsters.viper_queen.size > GameData.monsters.forest_tomb_guardian.size and no_reptiles, "Floresta: Rei Golem maior que o Guardião e sem répteis")
	# Floresta: trilhas de lajes e marcos de pedra nas divisas dos setores (como no Cemitério).
	var forest_decor: Array = GameData.arenas.forest_01_path.decor
	_check(forest_decor.filter(func(d: Dictionary) -> bool: return d.get("piece", "") == "Trail_Mud").size() > 100 and Kit.has("Trail_Mud")
		and forest_decor.filter(func(d: Dictionary) -> bool: return String(d.get("piece", "")).begins_with("Pr_") and d.get("piece", "") != "Pr_RoadSign").is_empty(),
		"Floresta tem trilhas de barro e nenhum asset de cemitério (cruz, lápide, obelisco, pilar, poste)")
	_check(forest_decor.all(func(d: Dictionary) -> bool: return d.get("piece", "") != "Floor_UnevenBrick"), "Floresta: sem chão de pedra")
	_check(forest_decor.filter(func(d: Dictionary) -> bool: return d.get("piece", "") in ["Dead_Tree", "Vl_Logs"]).is_empty()
		and forest_decor.filter(func(d: Dictionary) -> bool: return String(d.get("piece", "")).begins_with("Pl_")).size() > 100, "Floresta sem troncos secos nem toras, com plantas")
	_check(forest_decor.filter(func(d: Dictionary) -> bool: return d.get("piece", "") == "Oak_Tree" and d.has("solid")).size() >= 20 and Kit.has("Oak_Tree"), "Floresta tem carvalhos vivos (o tronco bloqueia) no lugar de parte da vegetação")
	_check(forest_decor.filter(func(d: Dictionary) -> bool: return String(d.get("piece", "")).begins_with("Wall_") or String(d.get("piece", "")).begins_with("Roof_")).is_empty(), "Floresta sem casas")
	_check(forest_decor.all(func(d: Dictionary) -> bool: return not d.get("piece", "") in ["Well_Covered", "Wheelbarrow", "Vl_Cellar", "Vl_Ladder", "Cart_Wood", "Vl_Outhouse"] and not String(d.get("piece", "")).begins_with("Mushroom_")), "Floresta sem o poço, o carrinho de mão, o porão, a escada, a carroça, a casinha e os cogumelos")
	_check(forest_decor.any(func(d: Dictionary) -> bool: return d.get("piece", "") == "Tv_Fire") and forest_decor.any(func(d: Dictionary) -> bool: return d.has("light") and d.get("camp", false))
		and forest_decor.filter(func(d: Dictionary) -> bool: return d.get("piece", "") == "Rock_MossyStone").size() >= 8 and Kit.has("Rock_MossyStone")
		and forest_decor.any(func(d: Dictionary) -> bool: return d.get("piece", "") == "Fire_Flame" and d.get("flicker", false)) and Kit.has("Fire_Flame"),
		"Floresta tem a fogueira (fogo, luz e círculo de pedras musgosas) no acampamento")
	_check(forest_decor.filter(func(d: Dictionary) -> bool: return d.get("piece", "") == "Butterfly_Anim" and d.has("swim")).size() >= 6 and Kit.has("Butterfly_Anim"), "Floresta tem as borboletas animadas")
	var forest_now: Dictionary = GameData.arenas.forest_01_path
	var keeper: Dictionary = forest_now.props.filter(func(p: Dictionary) -> bool: return p.id == "forest_pyre_keeper")[0]
	var pira_room: Dictionary = forest_now.rooms.filter(func(r: Dictionary) -> bool: return r.id == "pira")[0]
	var pira_toads: Array = forest_now.encounters.filter(func(e: Dictionary) -> bool: return e.id.begins_with("f_toads") and absf(e.position[0] - pira_room.center[0]) <= pira_room.size[0] / 2.0 and absf(e.position[1] - pira_room.center[1]) <= pira_room.size[1] / 2.0 and e.id.length() == 9)
	_check(keeper.position[1] < -40 and keeper.summon.position[1] < -38 and pira_toads.size() == 4, "A Guardiã da Pira fica na sala da lagoa e os sapos na Praça da Pira")
	var forest_map: Dictionary = GameData.arenas.forest_01_path
	var toad_room: Dictionary = forest_map.rooms.filter(func(r: Dictionary) -> bool: return r.id == "pira")[0]
	_check(forest_map.props.any(func(p: Dictionary) -> bool: return p.id == "toad_pond" and p.kind == "water" and p.get("round", false))
		and forest_decor.all(func(d: Dictionary) -> bool: return not (String(d.get("piece", "")).begins_with("Rock")
			and absf(d.position[0] - toad_room.center[0]) <= toad_room.size[0] / 2 and absf(d.position[1] - toad_room.center[1]) <= toad_room.size[1] / 2)),
		"Floresta: lagoa e sem pedras na sala dos sapos (Praça da Pira)")
	# Floresta: a Besta Quitinosa (corpo a corpo, modelo estático animado por código).
	var beasts: Array = GameData.arenas.forest_01_path.encounters.filter(func(e: Dictionary) -> bool: return e.id == "f_beasts")
	_check(beasts.size() == 1 and beasts[0].monsters[0].monster == "chitin_beast" and MonsterModel.FAMILIES.get(GameData.monsters.chitin_beast.look, {}).get("static", false),
		"Floresta tem as Bestas Quitinosas")
	# Floresta: a aldeia de Ferncroft, com o casal que dá duas missões que terminam ao limpar encontros da área.
	var forest: Dictionary = GameData.arenas.forest_01_path
	var forest_ids: Array = forest.encounters.map(func(e: Dictionary) -> String: return e.id)
	for prop: Dictionary in forest.props:
		if prop.has("summon"):
			forest_ids.append(prop.summon.id)    # os grupos invocados também contam como "limpos"
	var village_npcs: Array = forest.props.filter(func(p: Dictionary) -> bool: return p.kind == "npc")
	_check(village_npcs.size() == 3 and village_npcs.all(func(p: Dictionary) -> bool: return GameData.npcs.has(p.npc)), "Floresta tem a elfa e os NPCs das duas praças")
	_check(forest.crowd.any(func(c: Dictionary) -> bool: return c.role == "hunter" and c.has("path")) and forest.crowd.any(func(c: Dictionary) -> bool: return c.role == "tanner" and c.has("path"))
		and GameData.crowd.roles.has("hunter") and GameData.crowd.roles.has("tanner") and not GameData.quests.has("forest_reptiles"), "Bertram e Elara andam pelo mapa, sem missão")
	_check(forest.rooms.any(func(r: Dictionary) -> bool: return r.id == "village"), "Floresta tem a sala da aldeia")
	for quest_id in ["forest_stone_golem", "forest_fire_golem", "forest_leshy"]:
		var mission: Dictionary = GameData.quests.get(quest_id, {})
		_check(mission.get("area", "") == "forest_01_path" and mission.get("clear", []).all(func(id: String) -> bool: return id in forest_ids)
			and (village_npcs.any(func(p: Dictionary) -> bool: return p.npc == mission.get("giver", "")) or GameData.arenas.tavern.props.any(func(p: Dictionary) -> bool: return p.get("npc", "") == mission.get("giver", ""))) and tr(mission.get("name_key", "")) != "",
			"missão da aldeia %s: encontros e quem a dá existem" % quest_id)
		var giver: Dictionary = GameData.npcs[mission.giver]
		_check(Town.dialogue_index(mission.giver, {}) == 0 and Town.dialogue_index(mission.giver, {quest_id: "active"}) == 1
			and Town.dialogue_index(mission.giver, {quest_id: "done"}) == 2 and giver.dialogues[0].get("offer", "") == quest_id,
			"conversa de %s: oferece, lembra e agradece" % quest_id)
	# Floresta: seis setores, um monstro em cada, e duas praças com NPC que invoca um mini-chefe.
	var sectors := {}
	for e: Dictionary in forest.encounters:
		if e.id != "f_viper_queen" and GameData.monsters[e.monsters[0].monster].get("category", "") in ["common", "elite"]:     # (os mini-chefes e a Toca do Rei Golem ficam de fora)
			sectors[e.monsters[0].monster] = true
	_check(sectors.size() == 3 and sectors.has("forest_troll"), "Floresta tem três salas de monstros (sapos, bestas e trolls), um tipo em cada (%d)" % sectors.size())
	var summoners: Array = forest.props.filter(func(p: Dictionary) -> bool: return p.has("summon"))
	_check(summoners.size() == 2 and summoners.all(func(p: Dictionary) -> bool:
		var group: Dictionary = p.summon
		return (GameData.npcs.has(p.npc) and GameData.npcs[p.npc].dialogues[0].lines.size() > 0 and group.monsters[0].get("rank", "") == "miniboss"
			and tr(group.get("toast", "")) != group.get("toast", "") and GameData.monsters.has(group.monsters[0].monster))),
		"Floresta tem duas praças com NPC que invoca um mini-chefe")
	# Floresta: alguns cervos quebráveis, parados, que só soltam carne (cura como a poção de vida).
	var deer: Array = GameData.arenas.forest_01_path.get("breakables", []).filter(func(b: Dictionary) -> bool: return b.monster != "coin_bag")  # a bolsa de moedas é outro objeto
	_check(deer.size() >= 3 and deer.size() <= 10 and deer.all(func(b: Dictionary) -> bool:
		var m: Dictionary = GameData.monsters.get(b.monster, {})
		return m.get("breakable", false) and m.get("ai", "") == "static" and float(m.get("damage", 1)) == 0.0 \
			and MonsterModel.FAMILIES.has(m.get("look", "")) and String(b.get("table", "")) == "breakable_meat"), "Floresta tem cervos que só soltam carne")
	_check(GameData.consumables.has("venison") and GameData.consumables.venison.restore == "health" and GameData.loot.breakable_meat.outcomes.keys() == ["venison"], "carne de cervo é consumível de vida e a tabela só solta carne")


func _test_explore_map() -> void:
	var area: Dictionary = GameData.arenas.sewers_01_drains
	var mask := ExploreMap.empty(area)
	var size := ExploreMap.grid_size(area)
	_check(mask.size() == size.x * size.y and mask.count(1) == 0, "mapa começa todo em névoa")
	var found := ExploreMap.reveal(mask, area, Vector2(0, 3))
	_check(found.size() > 0 and ExploreMap.is_seen(mask, area, Vector2(0, 3)) and ExploreMap.is_seen(mask, area, Vector2(0, -6)),
		"revela em volta do herói (%d células)" % found.size())
	_check(not ExploreMap.is_seen(mask, area, Vector2(0, -63)), "o fundo da área continua em névoa")
	_check(ExploreMap.reveal(mask, area, Vector2(0, 3)).is_empty(), "o que já foi visto não conta de novo")
	var fraction := ExploreMap.explored_fraction(mask, area)
	_check(fraction > 0.05 and fraction < 0.6, "fração explorada no começo: %.2f" % fraction)
	var copy := ExploreMap.decode(ExploreMap.encode(mask), area)
	_check(copy == mask, "máscara volta igual do save")
	_check(ExploreMap.decode("", area) == ExploreMap.empty(area) and ExploreMap.decode("lixo:3", area).count(1) == 0, "save sem máscara (ou de outra área) começa em névoa")
	# Andando de sala em sala (o centro de cada uma), a área toda aparece.
	for room: Dictionary in area.rooms:
		ExploreMap.reveal(mask, area, Vector2(room.center[0], room.center[1]))
	_check(ExploreMap.explored_fraction(mask, area) > 0.95, "andando pela área toda, quase tudo aparece (%.2f)" % ExploreMap.explored_fraction(mask, area))


## Aparência na criação (data/appearance.json): validação, ficha e visual do modelo.
func _test_appearance() -> void:
	var clean := Appearance.clean("male", {"hair": 99, "hair_color": -5, "skin": 40, "beard": true})
	_check(clean.hair == Appearance.hair_styles("male").size() - 1 and clean.hair_color == 0 and clean.skin == Appearance.skin_count() - 1,
		"aparência: valores fora da lista voltam para dentro dela")
	_check(clean.beard, "aparência: barba só no masculino (masculino mantém)")
	_check(not Appearance.clean("female", {"beard": true}).beard, "aparência: feminino não tem barba")
	_check(Appearance.hair_styles("female").has("Hair_Long") and Appearance.hair_styles("male").has("Hair_Buzzed"),
		"aparência: cada sexo tem os seus cabelos")
	for kit in HairKit.STYLES:
		_check(Appearance.hair_styles("female").has(kit) and tr("CHAR_HAIR_" + kit) != "CHAR_HAIR_" + kit, "cabelo %s: está na lista feminina e tem tradução" % kit)
	var hair_model := HeroModel.new()
	add_child(hair_model)
	hair_model.setup("female", {"hair": HairKit.STYLES.duplicate(), "hair_color": [0.2, 0.1, 0.1]})
	var made := 0
	for kit in HairKit.STYLES:
		made += 1 if hair_model.get_node_or_null("**/" + kit) != null or hair_model.find_child(kit, true, false) != null else 0
	_check(made == HairKit.STYLES.size(), "cabelo: todos os penteados feitos por código geram malha na cabeça")
	hair_model.queue_free()
	var c := CharacterData.create("knight", "male", "Teste", "fire", {"hair": 1, "hair_color": 3, "skin": 4, "beard": true})
	var back := CharacterData.from_dict(c.to_dict())
	_check(back != null and back.data.look == c.data.look and back.data.look.skin == 4 and back.data.look.beard,
		"aparência: a escolha vai na ficha e volta igual do save")
	_check(not back.is_edited(), "aparência: a ficha com aparência não conta como editada")
	var legacy := CharacterData.create("mage", "female", "Antiga")
	_check(legacy.data.look.is_empty(), "aparência: sem escolha, a ficha fica sem 'look' (visual da classe)")
	var look := Appearance.model_look("male", c.data.look, {})
	_check(look.hair == ["Hair_Buzzed", "Hair_Beard"] and look.skin.size() == 3 and look.hair_color.size() == 3,
		"aparência: o visual do modelo junta cabelo, barba, cor e pele")
	_check(Appearance.model_look("female", {}, {"hair": ["Hair_Long"]}).hair == ["Hair_Long"],
		"aparência: personagem antigo mantém o visual padrão da classe")
	var bald := Appearance.model_look("female", {"hair": 3}, {})
	_check(bald.hair.is_empty(), "aparência: a opção 'sem cabelo' não põe malha")


## Conjuntos do Ninja por rank (D a S): material -> rank, e cada rank veste e desveste sem sobras.
func _test_ninja_gear() -> void:
	_check(NinjaGear.rank_of("cloth") == "D" and NinjaGear.rank_of("iron") == "D" and NinjaGear.rank_of("steel") == "C"
		and NinjaGear.rank_of("copper") == "B" and NinjaGear.rank_of("silver") == "A" and NinjaGear.rank_of("gold") == "S",
		"ninja: material vira rank (pano/ferro D, aço C, cobre B, prata A, ouro S)")
	_check(NinjaGear.has_gear("ninja", "male") and NinjaGear.has_gear("ninja", "female") and not NinjaGear.has_gear("mage", "male"), "ninja: o Ninja (os dois sexos) tem conjuntos por rank")
	_check(HeroGear.has_gear("mage", "female") and HeroGear.has_gear("knight", "male") and HeroGear.has_gear("ninja", "male") and HeroGear.has_gear("ninja", "female"),
		"conjuntos por rank: todas as classes nos dois sexos")
	var suit := HeroModel.new()
	add_child(suit)
	suit.setup("male", {}, "ninja")
	var base_parts := suit.visible_parts()
	_check(suit.is_suit() and not suit.suit_worn() and base_parts.has("Peasant_Body") and base_parts.has("Head") and not base_parts.has("Ninja_Body"),
		"ninja: sem peça equipada aparece o Camponês, com rosto e cabelo (sem a roupa ninja)")
	NinjaGear.apply(suit, {"body": "D", "head": "", "hands": "", "feet": ""})
	var worn_parts := suit.visible_parts()
	_check(suit.suit_worn() and worn_parts.size() == 4 and worn_parts.all(func(n: String) -> bool: return n.begins_with("Ninja_")),
		"ninja: ao equipar uma peça veste a roupa ninja inteira em 4 peças, com capuz e máscara (sem rosto)")
	NinjaGear.apply(suit, {"body": "", "head": "", "hands": "", "feet": ""})
	_check(not suit.suit_worn(), "ninja: tirando as peças volta ao Camponês")
	var cloth: Array[Color] = []
	var others := func() -> Array:
		var colors := []
		for part: MeshInstance3D in suit.find_children("Ninja_*", "MeshInstance3D", true, false):
			for k in part.get_surface_override_material_count():
				var m := part.get_surface_override_material(k) as StandardMaterial3D
				if m and not String(m.resource_name).contains("Cloth"):
					colors.append(m.albedo_color)
		return colors
	var others_before: Array = others.call()
	var by_rank := []
	for rank in NinjaGear.RANKS:
		NinjaGear.apply(suit, {"body": rank, "head": rank, "hands": rank, "feet": rank})
		by_rank.append((suit.find_child("Ninja_Body", true, false) as MeshInstance3D).get_surface_override_material(0).albedo_color)
	_check(by_rank.all(func(c: Color) -> bool: return c == by_rank[0]), "ninja: o rank não muda a cor da roupa")
	for element in Elements.ALL:
		suit.set_suit_element(element)
		cloth.append((suit.find_child("Ninja_Body", true, false) as MeshInstance3D).get_surface_override_material(0).albedo_color)
	_check(cloth.size() == 4 and cloth[0] != cloth[1] and cloth[1] != cloth[2] and cloth[2] != cloth[3], "ninja: a cor da roupa é a do elemento (água, fogo, vento, terra)")
	suit.set_suit_element("fire")
	_check(cloth[1].r > cloth[1].b and cloth[0].b > cloth[0].r and cloth[3].g > cloth[3].r, "ninja: fogo vermelho, água azul, terra verde")
	_check(others_before == others.call(), "ninja: a pele e a faixa não são tingidas pelo rank")
	suit.queue_free()
	var witch := HeroModel.new()
	add_child(witch)
	witch.setup("female", {"hair": ["Hair_Long"], "hair_color": [0.2, 0.1, 0.1]}, "mage")
	_check(witch.is_suit() and not witch.suit_worn() and witch.visible_parts().has("Peasant_Body") and not witch.visible_parts().has("Witch_Body"),
		"maga: sem peça equipada aparece o Camponês (sem a roupa de bruxa)")
	HeroGear.apply(witch, "mage", {"body": "D", "head": "", "hands": "", "feet": ""})
	_check(witch.suit_worn() and witch.visible_parts() == ["Witch_Body"], "maga: com uma peça equipada veste a roupa de bruxa inteira")
	var witch_colors := []
	for element in Elements.ALL:
		witch.set_suit_element(element)
		witch_colors.append((witch.find_child("Witch_Body", true, false) as MeshInstance3D).get_surface_override_material(0).albedo_color)
	_check(witch_colors[0] != witch_colors[1] and witch_colors[1] != witch_colors[2] and witch_colors[2] != witch_colors[3], "maga: o roxo vira a cor do elemento")
	var other_mage := HeroModel.new()
	add_child(other_mage)
	other_mage.setup("male", {}, "ninja_unknown")
	_check(not other_mage.is_suit(), "classe sem corpo próprio mantém o corpo e as roupas de antes")
	other_mage.queue_free()
	witch.queue_free()
	var elf := HeroModel.new()
	add_child(elf)
	elf.setup("female", {}, "archer")
	_check(elf.is_suit() and not elf.suit_worn() and elf.visible_parts().has("Peasant_Body"), "arqueira: sem peça equipada aparece o Camponês")
	HeroGear.apply(elf, "archer", {"body": "D", "head": "", "hands": "", "feet": ""})
	_check(elf.suit_worn() and elf.visible_parts() == ["Elf_Body"], "arqueira: com uma peça equipada veste a roupa da Elfa inteira")
	var elf_colors := []
	for element in Elements.ALL:
		elf.set_suit_element(element)
		elf_colors.append((elf.find_child("Elf_Body", true, false) as MeshInstance3D).get_surface_override_material(0).albedo_color)
	_check(elf_colors[0] != elf_colors[1] and elf_colors[1] != elf_colors[2] and elf_colors[2] != elf_colors[3], "arqueira: o verde da roupa vira a cor do elemento")
	elf.queue_free()
	var dwarf := HeroModel.new()
	add_child(dwarf)
	dwarf.setup("male", {}, "archer")
	_check(dwarf.is_suit() and not dwarf.suit_worn() and dwarf.visible_parts().has("Peasant_Body"), "arqueiro: sem peça equipada aparece o Camponês")
	HeroGear.apply(dwarf, "archer", {"body": "D", "head": "", "hands": "", "feet": ""})
	_check(dwarf.suit_worn() and dwarf.visible_parts() == ["Dwarf_Body"], "arqueiro: com uma peça equipada veste o anão inteiro")
	var dwarf_colors := []
	for element in Elements.ALL:
		dwarf.set_suit_element(element)
		dwarf_colors.append((dwarf.find_child("Dwarf_Body", true, false) as MeshInstance3D).get_surface_override_material(0).albedo_color)
	_check(dwarf_colors[0] != dwarf_colors[1] and dwarf_colors[1] != dwarf_colors[2] and dwarf_colors[2] != dwarf_colors[3], "arqueiro: o azul da camisa vira a cor do elemento")
	dwarf.queue_free()
	var goblin := HeroModel.new()
	add_child(goblin)
	goblin.setup("female", {}, "summoner")
	_check(goblin.is_suit() and not goblin.suit_worn() and goblin.visible_parts().has("Peasant_Body"), "invocador: sem peça equipada aparece o Camponês (qualquer sexo)")
	HeroGear.apply(goblin, "summoner", {"body": "D", "head": "", "hands": "", "feet": ""})
	_check(goblin.suit_worn() and goblin.visible_parts() == ["Goblin_Body"], "invocador: com uma peça equipada veste o goblin inteiro")
	var goblin_colors := []
	for element in Elements.ALL:
		goblin.set_suit_element(element)
		goblin_colors.append((goblin.find_child("Goblin_Body", true, false) as MeshInstance3D).get_surface_override_material(0).albedo_color)
	_check(goblin_colors[0] != goblin_colors[1] and goblin_colors[1] != goblin_colors[2] and goblin_colors[2] != goblin_colors[3], "invocador: o casaco amarelo vira a cor do elemento")
	goblin.queue_free()
	var knight := HeroModel.new()
	add_child(knight)
	knight.setup("male", {}, "knight")
	_check(knight.is_suit() and not knight.suit_worn() and knight.visible_parts().has("Peasant_Body"), "cavaleiro: sem peça equipada aparece o Camponês")
	HeroGear.apply(knight, "knight", {"body": "D", "head": "", "hands": "", "feet": ""})
	_check(knight.suit_worn() and knight.visible_parts() == ["Knight_Body"], "cavaleiro: com uma peça equipada veste a armadura inteira")
	var knight_colors := []
	for element in Elements.ALL:
		knight.set_suit_element(element)
		knight_colors.append((knight.find_child("Knight_Body", true, false) as MeshInstance3D).get_surface_override_material(0).albedo_color)
	_check(knight_colors[0] != knight_colors[1] and knight_colors[1] != knight_colors[2] and knight_colors[2] != knight_colors[3], "cavaleiro: o azul vira a cor do elemento")
	knight.queue_free()
	var wizard := HeroModel.new()
	add_child(wizard)
	wizard.setup("male", {}, "mage")
	_check(wizard.is_suit() and not wizard.suit_worn() and wizard.visible_parts().has("Peasant_Body"), "mago: sem peça equipada aparece o Camponês")
	HeroGear.apply(wizard, "mage", {"body": "D", "head": "", "hands": "", "feet": ""})
	_check(wizard.suit_worn() and wizard.visible_parts() == ["Mage_Body"], "mago: com uma peça equipada veste o manto inteiro")
	var wizard_colors := []
	for element in Elements.ALL:
		wizard.set_suit_element(element)
		wizard_colors.append((wizard.find_child("Mage_Body", true, false) as MeshInstance3D).get_surface_override_material(0).albedo_color)
	_check(wizard_colors[0] != wizard_colors[1] and wizard_colors[1] != wizard_colors[2] and wizard_colors[2] != wizard_colors[3], "mago: o azul do manto vira a cor do elemento")
	wizard.queue_free()
	for class_id in ClassGear.CLASSES:
		for sex in ["male", "female"]:
			var other := HeroModel.new()
			add_child(other)
			other.setup(sex, {})
			var made := []
			for rank in HeroGear.RANKS:
				HeroGear.apply(other, class_id, {"body": rank, "head": rank, "hands": rank, "feet": rank})
				made.append((other.get_meta(NinjaGear.META) as Array).size())
			_check(made.min() >= 2 and made[4] > made[0], "%s (%s): cada rank monta peças e o S tem mais que o D %s" % [class_id, sex, str(made)])
			HeroGear.apply(other, class_id, {"body": "", "head": "", "hands": "", "feet": ""})
			_check((other.get_meta(NinjaGear.META) as Array).is_empty(), "%s (%s): sem peças equipadas não monta nada" % [class_id, sex])
			other.queue_free()
	var hero := HeroModel.new()
	add_child(hero)
	hero.setup("male", {"hair": ["Hair_SimpleParted"], "hair_color": [0.2, 0.12, 0.07]})
	var counts := {}
	for rank in NinjaGear.RANKS:
		NinjaGear.apply(hero, {"body": rank, "head": rank, "hands": rank, "feet": rank})
		counts[rank] = (hero.get_meta(NinjaGear.META) as Array).size()
	_check(counts.D >= 3 and counts.S > counts.D, "ninja: cada rank monta suas peças (D %d, C %d, B %d, A %d, S %d)" % [counts.D, counts.C, counts.B, counts.A, counts.S])
	NinjaGear.apply(hero, {"body": "", "head": "", "hands": "", "feet": ""})
	_check((hero.get_meta(NinjaGear.META) as Array).is_empty(), "ninja: sem peças equipadas não monta nada")
	hero.queue_free()


func _test_ui_theme() -> void:
	var theme := UiTheme.get_theme()
	_check(theme.default_font != null, "tema: fonte do texto (Alegreya) carregada")
	_check(theme.get_font("font", "TitleLabel") != null and theme.get_font("font", "TitleLabel") != theme.default_font, "tema: fonte dos títulos (Cinzel)")
	for item in [["panel", "PanelContainer"], ["panel", "ParchmentPanel"], ["panel", "HudPanel"], ["normal", "Button"], ["hover", "Button"], ["pressed", "Button"], ["focus", "Button"], ["background", "ProgressBar"]]:
		_check(theme.has_stylebox(item[0], item[1]), "tema: %s de %s" % item)
	var frame := theme.get_stylebox("panel", "PanelContainer") as StyleBoxTexture
	_check(frame != null and frame.texture != null and frame.texture.get_width() == UiTheme.PAPER_PERIOD + UiTheme.PAPER_MARGIN * 2, "janela de papel antigo gerada (9-patch)")
	var default := ThemeDB.get_default_theme()
	_check(default.get_stylebox("panel", "PanelContainer") == theme.get_stylebox("panel", "PanelContainer")
		and default.default_font == theme.default_font, "o tema vale para todos os controles (tema padrão)")


func _test_tips() -> void:
	var c := CharacterData.create("knight", "male", "Tip")
	_check(c.data.tutorial_seen == [], "personagem novo sem dicas vistas")
	_check(c.mark_tip_seen("tip_move") and not c.mark_tip_seen("tip_move"), "dica guardada uma vez só")
	_check(not c.mark_tip_seen("tip_nao_existe"), "dica desconhecida não entra")
	var old := c.to_dict()
	old.erase("tutorial_seen")
	_check(CharacterData.from_dict(old).data.tutorial_seen == [], "save antigo ganha tutorial_seen vazio")
	for id: String in GameData.tips.tips:
		var tip: Dictionary = GameData.tips.tips[id]
		var text := TipManager.text(id)
		_check(tip.key != text and not text.contains("{"), "dica com texto e botões: " + id)
	var previous := Session.character
	var tips_on := Settings.tips
	Session.character = CharacterData.create("knight", "male", "Tip")
	Settings.tips = true
	TipManager.reset()
	var shown: Array[String] = []
	var record := func(id: String, _text: String) -> void: shown.append(id)
	TipManager.tip_shown.connect(record)
	TipManager.notify("start")
	_check(TipManager.current() == "tip_move", "evento mostra a dica")
	TipManager.notify("low_health")
	TipManager.notify("interact_near")
	_check(TipManager.current() == "tip_move", "uma dica por vez")
	TipManager._process(100.0)
	_check(TipManager.current() == "tip_potion", "a fila segue a prioridade (poção antes de interagir)")
	TipManager.notify("start")
	TipManager._process(100.0)
	TipManager._process(100.0)
	_check(shown.count("tip_move") == 1, "dica vista não repete")
	TipManager.notify("map_area", "mage")
	_check(TipManager.current() == "tip_map", "Mago numa área de mapa: só a dica do mapa (%s)" % TipManager.current())
	TipManager._process(100.0)
	_check(TipManager.current() == "", "dica do Cavaleiro não aparece para o Mago")
	TipManager.notify("map_area", "knight")
	_check(TipManager.current() == "tip_mount", "dica de montar para o Cavaleiro")
	Session.character.data.tutorial_seen = ["tip_attack"]
	TipManager.reset()
	TipManager.notify("enemy_near")
	_check(TipManager.current() == "", "dica guardada no personagem não aparece de novo")
	Settings.tips = false
	TipManager.notify("level_up")
	_check(TipManager.current() == "", "dicas desligadas nas Opções")
	_check(TipManager.seen_tips().has("tip_attack"), "ajuda lista as dicas vistas")
	TipManager.tip_shown.disconnect(record)
	Settings.tips = tips_on
	TipManager.reset()
	Session.character = previous


func _test_names() -> void:
	var item := Items.equipment("staff", "wood")
	var expected := {"en": "Wooden Staff", "es": "Bastón de madera", "pt_BR": "Cajado de Madeira"}
	for lang in expected:
		TranslationServer.set_locale(lang)
		_check(Items.display_name(item) == expected[lang], "nome em %s: %s" % [lang, Items.display_name(item)])
	TranslationServer.set_locale(Settings.language)


func _clean(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path):
		return
	for file in DirAccess.get_files_at(path):
		DirAccess.remove_absolute(path.path_join(file))
	for dir in DirAccess.get_directories_at(path):
		_clean(path.path_join(dir))
		DirAccess.remove_absolute(path.path_join(dir))
