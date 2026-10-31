# Southern Mercenaries — GPL-3.0-or-later
extends "res://tests/smoke_arena.gd"
## Capturas das telas para conferir o visual (precisa de tela; no CI, Xvfb):
##   godot --path . res://tests/ui_screens.tscn -- <pasta>
## 0. elements.png: ratos com estados (molhado, queimando, congelado), números de
##    dano na fraqueza/resistência, um combo e a área de vapor;
## 0b. skill_fx.png: Nevasca, Corrente de Raios e Muralha de Fogo nos mesmos ratos;
## 0c. skills.png: janela de habilidades de um Mago nível 12 e a barra de atalhos;
## 0d. classes.png: as 5 classes lado a lado (Cavaleiro montado), cada uma de um elemento;
## 1. trade.png: janela de troca com um aliado fictício (peer 99) e ofertas dos dois lados;
## 1b. tavern.png: conversa com o Velho Bêbado na Taverna (a primeira missão);
## 1c. tortuga.png: Rua Principal com as bancas; shop.png: Mercado Pirata;
## 2. load_campaign.png: menu principal → Carregar campanha, com três campanhas
##    (uma com miniatura capturada da própria arena).

const ELEMENTS_FRAME := 200
const ELEMENTS_SHOT := 206
const SKILL_FX_FRAME := 210
const SKILL_FX_SHOT := 216
const SKILL_MENU_FRAME := 222
const SKILL_MENU_SHOT := 228
const CLASSES_FRAME := 230
const CLASSES_SHOT := 236
const THUMB_FRAME := 240
const TRADE_FRAME := 260
const TRADE_SHOT := 290
const TAVERN_FRAME := 292
const TAVERN_SHOT := 300
const STREET_FRAME := 302
const STREET_SHOT := 310
const SHOP_FRAME := 312
const SHOP_SHOT := 318
const MENU_FRAME := 330

var _dir := "user://"
var _menu: Node


func _args() -> PackedStringArray:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		_dir = args[0]
	return PackedStringArray()  # solo


func _physics_process(delta: float) -> void:
	if _arena and _frame < MENU_FRAME:
		super._physics_process(delta)
	else:
		_frame += 1
	if _frame == ELEMENTS_FRAME:
		_show_elements()
	elif _frame == ELEMENTS_SHOT:
		await _shot("elements.png")
	elif _frame == SKILL_FX_FRAME:
		_show_skills()
	elif _frame == SKILL_FX_SHOT:
		await _shot("skill_fx.png")
	elif _frame == SKILL_MENU_FRAME:
		_arena._skill_menu.toggle()
	elif _frame == SKILL_MENU_SHOT:
		await _shot("skills.png")
		_arena._skill_menu.close()
	elif _frame == CLASSES_FRAME:
		_show_classes()
	elif _frame == CLASSES_SHOT:
		await _shot("classes.png")
		for peer in [91, 92, 93, 94]:
			var hero := _arena.get_node_or_null(str(peer))
			if hero:
				hero.queue_free()
	elif _frame == THUMB_FRAME:
		await RenderingServer.frame_post_draw
		SaveSystem.save_thumbnail(Session.campaign.id, get_viewport().get_texture().get_image())
	elif _frame == TRADE_FRAME:
		_open_trade()
	elif _frame == TRADE_SHOT:
		await _shot("trade.png")
	elif _frame == TAVERN_FRAME:
		_open_tavern()
	elif _frame == TAVERN_SHOT:
		await _shot("tavern.png")
	elif _frame == STREET_FRAME:
		_open_street()
	elif _frame == STREET_SHOT:
		await _shot("tortuga.png")
	elif _frame == SHOP_FRAME:
		_open_pirate_market()
	elif _frame == SHOP_SHOT:
		await _shot("shop.png")
		_arena._shop_menu.close()
	elif _frame == MENU_FRAME:
		_open_load_campaign()
	elif _frame == MENU_FRAME + 20:
		await _shot("load_campaign.png")
		get_tree().quit()


## Traz seis ratos para perto do herói (o bot para) e acerta cada um com um
## elemento diferente, para a captura.
func _show_elements() -> void:
	_stop_bot()
	var player: Player = _arena.local_player
	var rats: Array = get_tree().get_nodes_in_group(&"enemies")
	var spots := [Vector3(-3.5, 0, -2.5), Vector3(0, 0, -3.5), Vector3(3.5, 0, -2.5),
		Vector3(-3.5, 0, 1.5), Vector3(3.5, 0, 1.5), Vector3(0, 0, 3.0)]
	rats = rats.slice(0, spots.size())
	for i in rats.size():
		var spot: Vector3 = player.global_position + spots[i]
		rats[i].global_position = spot
		rats[i].net_position = spot
		rats[i].home = spot
	var hits := [
		[{"damage": 4.0, "element": "fire", "state": "burning", "crit_chance": 0.0}],
		[{"damage": 4.0, "element": "water", "state": "soaked", "crit_chance": 0.0}],
		[{"damage": 4.0, "element": "earth", "state": "", "crit_chance": 0.0}],
		[{"damage": 3.0, "element": "water", "state": "soaked", "crit_chance": 0.0},
			{"damage": 3.0, "element": "air", "state": "", "crit_chance": 0.0}],
		[{"damage": 3.0, "element": "fire", "state": "burning", "crit_chance": 0.0},
			{"damage": 3.0, "element": "water", "state": "", "crit_chance": 0.0}],
	]
	for i in mini(hits.size(), rats.size()):
		for hit: Dictionary in hits[i]:
			rats[i].take_hit(hit)
	if rats.size() > hits.size():
		Elements.apply_state(rats[hits.size()].status, "frozen", "earth", false)


## Mago nível 12 com algumas habilidades e três delas em ação.
func _show_skills() -> void:
	var player: Player = _arena.local_player
	var c := player.character
	c.add_xp(60000)
	for key in ["element_2", "element_6", "element_10", "sharp_mind", "teleport", "mana_shield"]:
		while c.can_learn(key) and c.skill_rank(key) < 2:
			c.learn(key)
	player.refresh_character()
	player.resource = player.max_resource
	player.facing = Vector2(0, -1)
	var system: SkillSystem = _arena.skills
	player.element = "water"
	system.cast(player, "blizzard", 1)
	player.element = "air"
	system.cast(player, "chain_lightning", 2)
	player.facing = Vector2(0, 1)
	player.element = "fire"
	system.cast(player, "fire_wall", 1)
	player.element = player.character.current_element()


## Heróis fictícios (peers 91–94) das outras classes ao lado do Mago.
func _show_classes() -> void:
	var player: Player = _arena.local_player
	for e in get_tree().get_nodes_in_group(&"enemies"):
		e.queue_free()
	var heroes := [[91, "archer", "air"], [92, "ninja", "water"], [93, "summoner", "earth"], [94, "knight", "fire"]]
	for i in heroes.size():
		var peer: int = heroes[i][0]
		var c := CharacterData.create(heroes[i][1], "male" if i % 2 == 0 else "female", "?", heroes[i][2])
		NetworkManager._characters[peer] = c.to_dict()
		_arena._spawn_player(peer)
		var hero: Player = _arena.get_node(str(peer))
		hero.teleport_to(player.global_position + Vector3(-4.0 + 2.0 * i + (2.0 if i >= 2 else 0.0), 0, 0))
		hero.facing = Vector2(0, 1)
	player.facing = Vector2(0, 1)


## Taverna: fecha a troca, viaja e abre a conversa do Velho Bêbado na última fala.
func _open_tavern() -> void:
	_arena._trade_menu._hide_all()
	var ally := _arena.get_node_or_null("99")
	if ally:
		ally.queue_free()
	_arena.travel("tavern", "start")
	var player: Player = _arena.local_player
	player.teleport_to(Vector3(-4.2, 0, 0.2))
	player.facing = Vector2(-0.7, -0.7)
	_arena._camera.snap()
	_arena.town.interact(player, _arena.prop_near(player, "npc", "old_drunk", 4.0))
	var menu: DialogueMenu = _arena._dialogue_menu
	menu._line = 4
	menu._show_line()


func _open_street() -> void:
	_arena._dialogue_menu.close()
	var player: Player = _arena.local_player
	_arena.town._rpc_accept("sewer_treasure")
	_arena.travel("tortuga", "start")
	player.teleport_to(Vector3(-12, 0, -1.5))
	_arena._camera.snap()


func _open_pirate_market() -> void:
	var player: Player = _arena.local_player
	player.teleport_to(Vector3(-6, 0, -16.5))
	_arena._camera.snap()
	_arena.request_interact(player)


func _stop_bot() -> void:
	_done = true
	for a in [&"aim_left", &"aim_right", &"aim_up", &"aim_down", &"attack",
			&"move_left", &"move_right", &"move_up", &"move_down", &"pickup_all"]:
		Input.action_release(a)


func _open_trade() -> void:
	# O bot para (senão se afasta e a troca é cancelada pela distância).
	_stop_bot()
	for e in get_tree().get_nodes_in_group(&"enemies"):
		e.queue_free()  # os ratos da cena dos elementos não atrapalham a troca
	var player: Player = _arena.local_player
	var trade: Trade = _arena.trade
	_arena._spawn_player(99)
	_ally = _arena.get_node("99")
	_ally.global_position = player.global_position + Vector3(1.5, 0, 0)
	var mine := player.character
	mine.data.gold = 120
	var staff := Items.equipment("staff", "steel", "rare", 6)
	mine.add_item(staff)
	var theirs := _ally.character
	theirs.data.name = "Orana"
	_ally.hero_name = "Orana"
	var ring := Items.equipment("ring", "iron", "magic", 3)
	theirs.add_item(ring)
	theirs.data.gold = 40
	trade.request_trade()
	var id := trade.trade_of(1)
	trade.server_answer(99, id, true)
	trade.set_offer(id, [mine.data.inventory.find(staff)], 50)
	trade.server_offer(99, id, [theirs.data.inventory.find(ring)], 15)
	trade.server_confirm(99, id)


func _open_load_campaign() -> void:
	# Outras campanhas na lista: uma mais antiga, com dois heróis e mais tempo de jogo.
	var older := SaveSystem.new_campaign()
	older.hero_names = {"a": "Orana", "b": "Oren"}
	older.played_seconds = 4 * 3600 + 25 * 60
	older.checkpoints_reached = ["prototype_arena:start"]
	SaveSystem.save_campaign(older)
	var oldest := SaveSystem.new_campaign()
	oldest.hero_names = {"c": "Aldric"}
	oldest.played_seconds = 15 * 60
	SaveSystem.save_campaign(oldest)
	older.updated = "2026-10-29T21:40:00"
	SaveSystem.write_json(SaveSystem.campaign_path(older.id), older)
	oldest.updated = "2026-10-12T18:05:00"
	SaveSystem.write_json(SaveSystem.campaign_path(oldest.id), oldest)
	_arena.queue_free()
	_arena = null
	Settings.language_chosen = true
	_menu = load("res://game/main/main.tscn").instantiate()
	add_child(_menu)
	_menu._open_campaigns()


func _shot(file: String) -> void:
	await RenderingServer.frame_post_draw
	var path := _dir.path_join(file)
	get_viewport().get_texture().get_image().save_png(path)
	print("captura salva em ", path)


func _report(_ok: bool, _detail: String) -> void:
	pass
