# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Teste de fumaça: abre a área de teste e joga sozinho com "controle"
## simulado: explora até o monstro mais próximo (pelo centro dos corredores),
## mira e atira, até vencer todos os grupos de encontro.
##
##   solo:    godot --headless --path . --fixed-fps 60 res://tests/smoke_arena.tscn
##   co-op:   ... res://tests/smoke_arena.tscn -- host 2     (espera 2 jogadores)
##            ... res://tests/smoke_arena.tscn -- host 2 resume  (e um herói retomado após queda)
##            ... res://tests/smoke_arena.tscn -- join 127.0.0.1
##   versão:  ... res://tests/smoke_arena.tscn -- join 127.0.0.1 0.0.0-outra
##            (passa se o host recusar com NET_VERSION_MISMATCH)
##   busca:   ... res://tests/smoke_arena.tscn -- discover   (passa se achar um host na LAN)
##   revive:  ... res://tests/smoke_arena.tscn -- revive
##            (solo com um aliado fictício: cai, é reanimado; todos caem, volta ao checkpoint)
##   elementos: ... res://tests/smoke_arena.tscn -- elements
##            (golpes com elemento em ratos de verdade: estados, combos, queimando,
##            área de vapor, congelado parado, Poção Elemental e projétil do herói)
##   habilidades: ... res://tests/smoke_arena.tscn -- skills [classe]
##            (todas as habilidades da classe (padrão: mage), dos 4 elementos, em ratos de verdade;
##            atalho com mana e recarga; passivas; escudo, cura, bônus e teleporte)
##   troca:   ... res://tests/smoke_arena.tscn -- trade
##            (solo com um aliado fictício: convite, ofertas, confirmações, troca e
##            cancelamento ao se afastarem; o aliado responde direto no servidor)
##
## No co-op o host só começa a contar quando todos entraram, e o teste do
## cliente passa se ele viu o próprio jogador, os monstros e a vitória.
##
## Fase 3: depois da vitória o bot recolhe o loot dele e equipa um item achado;
## passa se subiu de nível, ganhou ouro e itens e se a ficha gravada no disco
## (pasta de testes) tem o mesmo nível. O personagem começa perto do nível 2.

const MAX_FRAMES := 60 * 120

var _arena: Node
var _frame := 0
var _role := "solo"
var _expected_players := 1
var _max_players_seen := 0
var _max_enemies_seen := 0
var _done := false
var _expect_refusal := ""
var _expect_resume := false
var _resumed := 0
# Teste de revive: etapas e o aliado fictício.
var _stage := 0
var _ally: Player
var _stage_frame := 0
# Fase 3: coleta de loot depois da vitória.
var _collecting := false
var _collect_frame := 0
var _equipped_item := false


func _ready() -> void:
	var args := _args()
	var role_name: String = args[0] if args.size() > 0 else "solo"
	SaveSystem.root = "user://test_saves".path_join(role_name)
	_clean(SaveSystem.root)
	var hero_class: String = args[1] if args.size() > 1 and args[0] == "skills" else "mage"
	var hero := CharacterData.create(hero_class, "male", "Bot")
	hero.data.xp = 680  # quase no nível 2, para o teste ver a subida
	hero.seal()
	Session.character = hero
	Session.campaign = SaveSystem.new_campaign()
	# Todo monstro deixa um item, para o teste sempre ter o que recolher.
	GameData.loot.common.item_chance = 1.0
	if args.size() > 0 and args[0] == "host":
		_role = "host"
		_expected_players = int(args[1]) if args.size() > 1 else 2
		_expect_resume = args.size() > 2 and args[2] == "resume"
		NetworkManager.prepare_host()
	elif args.size() > 1 and args[0] == "join":
		_role = "client"
		NetworkManager.prepare_join(args[1])
		if args.size() > 2:
			ProjectSettings.set_setting("application/config/version", args[2])
			_expect_refusal = "NET_VERSION_MISMATCH"
	elif args.size() > 0 and args[0] == "discover":
		set_physics_process(false)
		NetworkManager.start_discovery()
		await get_tree().create_timer(3.5).timeout
		print("hosts encontrados: ", NetworkManager.hosts.keys())
		var found := not NetworkManager.hosts.is_empty()
		print(("OK: " if found else "FALHOU: ") + "[discover] %d host(s)" % NetworkManager.hosts.size())
		get_tree().quit(0 if found else 1)
		return
	else:
		_role = args[0] if args.size() > 0 and args[0] in ["revive", "trade", "elements", "skills"] else "solo"
		NetworkManager.prepare_solo()
	NetworkManager.session_ended.connect(func(reason: String) -> void:
		if _expect_refusal != "":
			_report(reason == _expect_refusal, "host recusou com " + reason)
		else:
			_report(false, "sessão terminou: " + reason))
	_arena = load("res://game/levels/prototype_arena.tscn").instantiate()
	add_child(_arena)
	_arena.hero_resumed.connect(func(peer_id: int) -> void:
		_resumed += 1
		print("herói retomado pelo peer %d" % peer_id))


## Argumentos depois de "--" (o teste de captura de tela tira os dele antes).
func _args() -> PackedStringArray:
	return OS.get_cmdline_user_args()


func _physics_process(_delta: float) -> void:
	_frame += 1
	if _done:
		return
	if _frame > MAX_FRAMES:
		_report(false, "tempo esgotado")
		return
	InputDevice.using_gamepad = true
	if _role == "revive":
		_revive_test()
		return
	if _role == "trade":
		_trade_test()
		return
	if _role == "elements":
		_elements_test()
		return
	if _role == "skills":
		_skills_test()
		return
	var players := get_tree().get_nodes_in_group(&"players")
	_max_players_seen = maxi(_max_players_seen, players.size())
	_max_enemies_seen = maxi(_max_enemies_seen, get_tree().get_nodes_in_group(&"enemies").size())
	if multiplayer.is_server():
		# O teste avalia combate e rede, não a esquiva do bot.
		for p: Player in players:
			p.health = p.max_health
	# Na entrada da área nenhum grupo deve estar acordado (encontros por exploração).
	if _frame == 30 and multiplayer.is_server():
		for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
			if e.state != Enemy.State.SLEEP:
				_report(false, "monstro acordado na entrada da área")
				return
	var player: Player = _arena.local_player
	for a in [&"aim_left", &"aim_right", &"aim_up", &"aim_down", &"attack",
			&"move_left", &"move_right", &"move_up", &"move_down", &"pickup_all"]:
		Input.action_release(a)
	if player == null:
		return
	var target := _nearest_enemy(player)
	if target:
		var offset := Vector2(target.global_position.x - player.global_position.x,
			target.global_position.z - player.global_position.z)
		var d := offset.normalized()
		_axis(&"aim_left", &"aim_right", d.x)
		_axis(&"aim_up", &"aim_down", d.y)
		if offset.length() <= 9.0:
			if _frame % 12 < 6:
				Input.action_press(&"attack")
		else:
			# Explora: os corredores ficam em x = 0; volta ao centro antes de mudar de sala.
			var move := d
			if absf(offset.y) > 6.0 and absf(player.global_position.x) > 1.5:
				move = Vector2(-signf(player.global_position.x), signf(offset.y) * 0.4).normalized()
			_axis(&"move_left", &"move_right", move.x)
			_axis(&"move_up", &"move_down", move.y)
	if _arena.result == _arena.Result.VICTORY and not _collecting:
		_collecting = true
		_collect_frame = _frame
	if _collecting:
		_collect_loot(player)


## Anda até o loot dele, recolhe tudo e equipa o primeiro item que puder.
func _collect_loot(player: Player) -> void:
	var drops := get_tree().get_nodes_in_group(&"loot")
	var c := player.character
	if not drops.is_empty() and _frame - _collect_frame < 60 * 40:
		var nearest: Node3D = drops[0]
		for d: Node3D in drops:
			if d.global_position.distance_to(player.global_position) < nearest.global_position.distance_to(player.global_position):
				nearest = d
		var offset := Vector2(nearest.global_position.x - player.global_position.x,
			nearest.global_position.z - player.global_position.z)
		if offset.length() > 1.0:
			var move := offset.normalized()
			if absf(offset.y) > 6.0 and absf(player.global_position.x) > 1.5:
				move = Vector2(-signf(player.global_position.x), signf(offset.y) * 0.4).normalized()
			_axis(&"move_left", &"move_right", move.x)
			_axis(&"move_up", &"move_down", move.y)
		if _frame % 20 == 0:
			Input.action_press(&"pickup_all")
		else:
			Input.action_release(&"pickup_all")
		return
	if not _equipped_item:
		_equipped_item = true
		# Prefere um slot vazio: trocar só a arma inicial não aumenta o equipamento.
		var choice := -1
		for i in c.data.inventory.size():
			var item: Variant = c.data.inventory[i]
			if item != null and c.can_equip(item):
				var slot := Items.slot_of(item)
				var free: bool = c.data.equipment.ring_1 == null or c.data.equipment.ring_2 == null \
					if slot == "ring" else c.data.equipment.get(slot) == null
				if free:
					choice = i
					break
				if choice < 0:
					choice = i
		if choice >= 0:
			player.request_use(choice)
			_stage_frame = _frame
			return
	if _frame - _stage_frame < 60:
		return  # espera o servidor confirmar o equipamento
	SaveSystem.flush()
	var saved := SaveSystem.load_character(c.data.id)
	var items := 0
	for item in c.data.inventory:
		if item != null and item.kind == "equipment":
			items += 1
	var gear := c.equipped().size()
	# Host/solo: a campanha gravada lembra o checkpoint alcançado e os heróis.
	var campaign_ok := true
	if _role != "client":
		var saved_campaign := SaveSystem.load_campaign(Session.campaign.get("id", ""))
		campaign_ok = "prototype_arena:start" in saved_campaign.get("checkpoints_reached", []) \
			and saved_campaign.get("hero_names", {}).has(c.data.id)
	var ok: bool = _max_players_seen >= _expected_players and _max_enemies_seen > 0 \
		and (_resumed > 0 or not _expect_resume) \
		and int(c.data.level) >= 2 and int(c.data.gold) > 0 and items + gear > 1 and gear >= 2 \
		and saved != null and saved.data.level == c.data.level and saved.data.gold == c.data.gold \
		and campaign_ok
	_report(ok, "vitória com %d jogador(es), %d retomado(s); nível %d, ouro %d, %d itens na bolsa, %d equipados, save no disco: %s, campanha: %s" % [
		_max_players_seen, _resumed, c.data.level, c.data.gold, items, gear, saved != null, campaign_ok])


func _revive_test() -> void:
	var player: Player = _arena.local_player
	if player == null:
		return
	for a in [&"interact", &"move_left", &"move_right", &"move_up", &"move_down"]:
		Input.action_release(a)
	match _stage:
		0:  # Cria um aliado fictício (outro "PC") e derruba ele.
			_arena._spawn_player(99)
			_ally = _arena.get_node("99")
			_ally.take_damage(9999)
			_next_stage()
		1:  # Anda até o aliado segurando "interagir".
			var offset := _ally.global_position - player.global_position
			if offset.length() > 1.0:
				_axis(&"move_left", &"move_right", offset.normalized().x)
				_axis(&"move_up", &"move_down", offset.normalized().z)
			Input.action_press(&"interact")
			if _ally.alive:
				print("aliado reanimado após %.1f s com %d de vida" % [(_frame - _stage_frame) / 60.0, _ally.health])
				_next_stage()
			elif _frame - _stage_frame > 60 * 15:
				_report(false, "aliado não foi reanimado")
		2:  # Todos caem: derrota e volta ao checkpoint.
			player.take_damage(9999)
			_ally.take_damage(9999)
			_next_stage()
		3:
			if _arena.result == _arena.Result.DEFEAT and _stage_frame >= 0:
				_stage_frame = -1
			if _stage_frame == -1 and _arena.result == _arena.Result.NONE:
				var ok: bool = player.alive and _ally.alive \
					and player.global_position.distance_to(_arena.CHECKPOINT) < 3.0
				_report(ok, "derrota voltou ao checkpoint (todos de pé no checkpoint: %s)" % ok)
			elif _frame > MAX_FRAMES:
				_report(false, "não voltou ao checkpoint")


## Elementos nos monstros de verdade (o lado de regras puras está em rpg_tests).
func _elements_test() -> void:
	var player: Player = _arena.local_player
	if player == null:
		return
	player.health = player.max_health  # o teste avalia elementos, não a esquiva
	if _stage > 0 or _frame < 10:
		return
	_stage = 1
	var checks: Array[String] = []
	var check := func(ok: bool, what: String) -> void:
		if not ok:
			checks.append(what)
	var rats: Array = get_tree().get_nodes_in_group(&"enemies")
	var rat: Enemy = rats[0]
	check.call(rat.element == "earth", "rato é de Terra")
	# Molhar e completar com Ar: Eletrocutar atordoa; parado não anda.
	rat.take_hit({"damage": 1.0, "element": "water", "state": "soaked", "crit_chance": 0.0})
	await get_tree().physics_frame
	check.call(rat.status.has("soaked") and rat.states_mask != 0, "molhado aplicado e sincronizado")
	var result: Dictionary = rat.take_hit({"damage": 1.0, "element": "air", "state": "", "crit_chance": 0.0})
	check.call(result.get("combo", "") == "electrocute" and rat.status.has("stunned"), "Eletrocutar no rato")
	var before := rat.global_position
	for i in 20:
		await get_tree().physics_frame
	check.call(rat.global_position.distance_to(before) < 0.05, "atordoado fica parado")
	# Fogo na fraqueza; ataque forte deixa queimando e o fogo tira vida sozinho.
	await get_tree().create_timer(1.2, false).timeout
	result = rat.take_hit({"damage": 2.0, "element": "fire", "state": "burning", "crit_chance": 0.0})
	check.call(result.get("effect", "") == "weak", "fogo na fraqueza da terra")
	check.call(rat.status.has("burning"), "queimando")
	var health := rat.health
	await get_tree().create_timer(2.2, false).timeout
	check.call(is_instance_valid(rat) and rat.health < health, "queimando tira vida com o tempo")
	# Água no rato queimando: Vapor vira área e os vizinhos dentro dela erram ataques.
	result = rat.take_hit({"damage": 1.0, "element": "water", "state": "", "crit_chance": 0.0})
	check.call(result.get("combo", "") == "steam" and _arena._zones.size() == 1, "Vapor cria a área")
	await get_tree().physics_frame
	await get_tree().physics_frame
	check.call(rat.status.has("steam") and rat.status.miss_chance() > 0.0, "quem está no vapor erra ataques")
	# Poção Elemental: troca o elemento do herói e dos projéteis.
	player.character.add_item(Items.stack(Items.CONSUMABLE, "elemental_potion_water"))
	var origin: String = player.character.data.element
	player._drink_next_elemental()
	check.call(player.element == "water" and player.character.data.element == origin, "Poção Elemental troca o elemento em uso")
	check.call(player.character.count_of("elemental_potion_water") == 0, "a poção é consumida")
	_report(checks.is_empty(), "elementos: " + ("tudo certo" if checks.is_empty() else "; ".join(PackedStringArray(checks))))


## Todas as habilidades do Mago em ratos de verdade (efeitos no servidor).
func _skills_test() -> void:
	var player: Player = _arena.local_player
	if player == null:
		return
	if _stage > 0 or _frame < 10:
		return
	_stage = 1
	var checks: Array[String] = []
	var check := func(ok: bool, what: String) -> void:
		if not ok:
			checks.append(what)
	var system: SkillSystem = _arena.skills
	var class_id: String = player.character.data.class_id
	var start := player.global_position
	# Ratos em fila na frente do herói (olhando para +z).
	player.facing = Vector2(0, 1)
	var rats: Array = get_tree().get_nodes_in_group(&"enemies")
	for i in mini(rats.size(), 8):
		var spot: Vector3 = player.global_position + Vector3((i % 4 - 1.5) * 1.2, 0, 3.0 + 1.5 * (i / 4))
		rats[i].global_position = spot
		rats[i].net_position = spot
		rats[i].home = spot
	# Acorda os grupos antes (acordar zera a vida) e deixa os ratos resistentes,
	# para todos continuarem vivos como alvo até o fim.
	for r in rats:
		_arena._wake_group(r.group)
	for r in rats:
		r.max_health = 100000.0
		r.health = r.max_health
	var total_before := 0.0
	for r in rats:
		total_before += r.health
	# Herói forte e com todas as habilidades no rank 3.
	var c := player.character
	c.add_xp(200000)
	for key in Skills.keys(class_id):
		c.data.skills[key] = 3
	player.refresh_character()
	c = player.character  # o servidor troca a cópia ao propagar a ficha
	player.resource = player.max_resource
	for element in Elements.ALL:
		player.element = element
		for key in Skills.keys(class_id):
			var id := Skills.skill_id(class_id, key, element)
			if not Skills.is_active(id):
				continue
			player.teleport_to(start)
			player.facing = Vector2(0, 1)
			var ok := system.cast(player, id, 3)
			check.call(ok, "habilidade %s funcionou" % id)
			player.teleport_to(start)
			player.health = player.max_health * 0.5
			await get_tree().physics_frame
	check.call(player.shield > 0.0, "habilidade de escudo de Terra")
	check.call(player._buffs.has("damage") and player._buffs.has("speed"), "bônus de dano (Fogo) e de velocidade (Ar)")
	check.call(not system._areas.is_empty(), "áreas que duram ativas")
	# Áreas, golpes com atraso e projéteis agem com o tempo.
	await get_tree().create_timer(2.5, false).timeout
	check.call(system._delayed.is_empty(), "Meteoro e Terremoto caíram")
	var total_after := 0.0
	for r in get_tree().get_nodes_in_group(&"enemies"):
		total_after += r.health
	check.call(total_after < total_before, "as habilidades tiraram vida dos ratos")
	# Escudo absorve antes da vida; Escudo de Mana tira da mana.
	player.alive = true
	player.health = player.max_health
	player.add_shield(50.0, 5.0)
	var health := player.health
	player.take_damage(20.0)
	check.call(is_equal_approx(player.health, health) and player.shield < 50.0, "escudo absorve o golpe")
	player.shield = 0.0
	player.resource = player.max_resource
	player.take_damage(20.0)
	if c.passive_value("mana_shield") > 0.0:
		check.call(player.resource < player.max_resource, "Escudo de Mana gasta mana")
	# Atalho: mana e recarga conferidas no servidor.
	player.element = "fire"
	var slot_key: String = Skills.keys(class_id)[1]
	c.data.skill_slots[0] = slot_key
	player.resource = player.max_resource
	var mana := player.resource
	player._cast_slot(0)
	check.call(player.resource < mana and player._skill_cd.has(slot_key), "atalho gasta recurso e entra em recarga")
	mana = player.resource
	player._cast_slot(0)
	check.call(is_equal_approx(player.resource, mana), "em recarga não usa de novo")
	check.call(player.skill_cooldown_left(slot_key) > 0.0, "o dono vê a recarga")
	_report(checks.is_empty(), "habilidades (%s): " % class_id + ("tudo certo" if checks.is_empty() else "; ".join(PackedStringArray(checks))))


## Troca com um aliado fictício (peer 99, sem rede): o lado dele é chamado
## direto no servidor, como se as RPCs dele tivessem chegado.
func _trade_test() -> void:
	var player: Player = _arena.local_player
	if player == null or _stage > 0 or _frame < 10:
		return
	_stage = 1
	var trade: Trade = _arena.trade
	var ended: Array[String] = []
	var states: Array[Dictionary] = []
	trade.ended.connect(func(reason: String) -> void: ended.append(reason))
	trade.updated.connect(func(state: Dictionary) -> void: states.append(state))
	_arena._spawn_player(99)
	_ally = _arena.get_node("99")
	var mine := player.character
	var theirs := _ally.character
	mine.data.gold = 50
	theirs.data.gold = 20
	var staff := Items.equipment("staff", "iron", "magic", 2)
	mine.add_item(staff)
	var ring := Items.equipment("ring", "iron", "rare", 2)
	theirs.add_item(ring)
	var checks: Array[String] = []
	var check := func(ok: bool, what: String) -> void:
		if not ok:
			checks.append(what)

	trade.request_trade()
	var id := trade.trade_of(1)
	check.call(id != 0 and trade.trade_of(99) == id, "convite criado para o aliado")
	trade.server_answer(99, id, true)
	check.call(not states.is_empty() and states[-1].them.name == _ally.hero_name, "janela aberta para o host")
	trade.set_offer(id, [mine.data.inventory.find(staff)], 30)
	trade.server_offer(99, id, [theirs.data.inventory.find(ring)], 5)
	trade.confirm(id)
	check.call(states[-1].you.confirmed and not states[-1].them.confirmed, "host confirmou, aliado ainda não")
	trade.server_offer(99, id, [theirs.data.inventory.find(ring)], 6)
	check.call(not states[-1].you.confirmed, "mudar a oferta desfaz as confirmações")
	trade.confirm(id)
	trade.server_confirm(99, id)
	check.call(ended.has("TRADE_DONE"), "troca concluída (%s)" % [ended])
	check.call(mine.data.inventory.find(ring) >= 0 and theirs.data.inventory.find(staff) >= 0, "itens trocados")
	check.call(int(mine.data.gold) == 26 and int(theirs.data.gold) == 44, "ouro trocado: %d e %d" % [mine.data.gold, theirs.data.gold])
	check.call(trade.trade_of(1) == 0, "troca encerrada")

	# Pedido para quem está longe: ninguém por perto.
	_ally.global_position = player.global_position + Vector3(30, 0, 0)
	trade.request_trade()
	check.call(trade.trade_of(1) == 0, "ninguém ao alcance, sem convite")
	# Afastar-se cancela uma troca aberta.
	_ally.global_position = player.global_position + Vector3(1.5, 0, 0)
	trade.request_trade()
	id = trade.trade_of(1)
	trade.server_answer(99, id, true)
	_ally.global_position = player.global_position + Vector3(20, 0, 0)
	await get_tree().physics_frame
	await get_tree().physics_frame
	check.call(trade.trade_of(1) == 0 and ended.has("TRADE_CANCELLED"), "afastar-se cancela a troca")
	_report(checks.is_empty(), "troca: " + ("tudo certo" if checks.is_empty() else "; ".join(PackedStringArray(checks))))


func _clean(path: String) -> void:
	if not DirAccess.dir_exists_absolute(path):
		return
	for file in DirAccess.get_files_at(path):
		DirAccess.remove_absolute(path.path_join(file))
	for dir in DirAccess.get_directories_at(path):
		_clean(path.path_join(dir))
		DirAccess.remove_absolute(path.path_join(dir))


func _next_stage() -> void:
	_stage += 1
	_stage_frame = _frame


func _axis(neg: StringName, pos: StringName, value: float) -> void:
	if value < 0.0:
		Input.action_press(neg, -value)
	elif value > 0.0:
		Input.action_press(pos, value)


func _nearest_enemy(player: Node3D) -> Node3D:
	var best: Node3D = null
	var best_d := INF
	for e in get_tree().get_nodes_in_group(&"enemies"):
		var d := player.global_position.distance_to(e.global_position)
		if d < best_d:
			best = e
			best_d = d
	return best


func _report(ok: bool, detail: String) -> void:
	if _done:
		return
	_done = true
	var line := "[%s] frames=%d encontros=%d/%d jogadores=%d inimigos_max=%d — %s" % [
		_role, _frame, _arena.cleared, _arena.total_encounters, _max_players_seen, _max_enemies_seen, detail]
	if ok:
		print("OK: " + line)
	else:
		printerr("FALHOU: " + line)
	# O host espera os clientes terminarem (cada um recolhe o próprio loot) e
	# saírem, para nenhum deles ver o host cair no meio do teste.
	if _role == "host":
		var deadline := Time.get_ticks_msec() + 45_000
		while NetworkManager.player_count() > 1 and Time.get_ticks_msec() < deadline:
			await get_tree().create_timer(0.2).timeout
	await get_tree().create_timer(0.1).timeout
	NetworkManager.leave()
	get_tree().quit(0 if ok else 1)
