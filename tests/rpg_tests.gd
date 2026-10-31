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
	_test_skills()
	_test_archer()
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
	_check(c.count_of("potion_health") == 3 and c.count_of("potion_resource") == 2, "poções do kit")


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
