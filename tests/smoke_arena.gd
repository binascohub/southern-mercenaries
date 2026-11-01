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
##   cidade:  ... res://tests/smoke_arena.tscn -- town
##            (campanha nova na Taverna: missão do Velho Bêbado, descansar, Rua
##            Principal, comprar e vender, Mercado Pirata, Poção Elemental, bueiro,
##            vitória conclui a missão, portal de volta encerra a expedição)
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
	# Os testes de combate jogam na área de teste; o da cidade começa na Taverna.
	if role_name not in ["town", "sewers"]:
		Session.campaign.area = "prototype_arena"
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
		_role = args[0] if args.size() > 0 and args[0] in ["revive", "trade", "elements", "skills", "town", "sewers"] else "solo"
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
	if _role == "town":
		_town_test()
		return
	if _role == "sewers":
		_sewers_test()
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
	# O teste avalia habilidades, não a esquiva: o herói não cai (senão a arena volta
	# ao checkpoint e os ratos dormem de novo).
	if player.alive:
		player.health = maxf(player.health, player.max_health * 0.5)
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
	# Invocador: um aliado caído para o Resgate reanimar.
	var fallen: Player = null
	if "animal_rescue" in Skills.keys(class_id):
		_arena._spawn_player(99)
		fallen = _arena.get_node("99")
		fallen.global_position = start + Vector3(-3, 0, 0)
		fallen.take_damage(99999)
	player.resource = player.max_resource
	for element in Elements.ALL:
		player.element = element
		for key in Skills.keys(class_id):
			var id := Skills.skill_id(class_id, key, element)
			if not Skills.is_active(id):
				continue
			player.teleport_to(start)
			player.facing = Vector2(0, 1)
			if id == "animal_rescue" and fallen:
				fallen.take_damage(99999)  # cai de novo para cada elemento testar o Resgate
			var ok := system.cast(player, id, 3)
			check.call(ok, "habilidade %s funcionou" % id)
			player.teleport_to(start)
			player.health = player.max_health * 0.5
			await get_tree().physics_frame
	check.call(player.shield > 0.0, "habilidade de escudo de Terra")
	check.call(player._buffs.has("damage") and player._buffs.has("speed"), "bônus de dano (Fogo) e de velocidade (Ar)")
	check.call(not system._areas.is_empty(), "áreas que duram ativas")
	# Cavaleiro: desmonta sozinho no corredor (área estreita) e monta de novo ao sair.
	if player.data.has("mount"):
		check.call(player.mounted, "Cavaleiro começa montado")
		player.teleport_to(Vector3(0, 0, -17))
		await get_tree().physics_frame
		await get_tree().physics_frame
		check.call(not player.mounted, "desmonta na área estreita")
		player.teleport_to(start)
		await get_tree().create_timer(1.5, false).timeout
		check.call(player.mounted, "monta de novo ao sair")
	if fallen:
		check.call(fallen.alive, "Resgate reanimou o aliado caído")
		var animals := system.companions_of(player)
		check.call(animals.size() >= 2 and animals.any(func(a: Companion) -> bool: return a.kind == "bear"),
			"companheiros e Urso Guardião chamados (%d)" % animals.size())
		var essence := player.resource
		player.resource = 0.0
		await get_tree().create_timer(1.5, false).timeout
		var info := PackedStringArray()
		for a in system.companions_of(player):
			var near := INF
			var near_state := -1
			for r in get_tree().get_nodes_in_group(&"enemies"):
				var d: float = r.global_position.distance_to(a.global_position)
				if d < near:
					near = d
					near_state = r.state
			info.append("%s d=%.1f estado=%d vida=%.0f pos=%s" % [a.kind, near, near_state, a.health, a.global_position])
		check.call(player.resource > 2.0 * 1.5 + 0.5, "golpes dos animais devolvem Essência (Essência %.1f, vivo %s; %s)" % [
			player.resource, player.alive, "; ".join(info)])
		player.resource = essence
	# Áreas, golpes com atraso e projéteis agem com o tempo.
	await get_tree().create_timer(2.5, false).timeout
	check.call(system._delayed.is_empty(), "Meteoro e Terremoto caíram")
	var total_after := 0.0
	for r in get_tree().get_nodes_in_group(&"enemies"):
		total_after += r.health
	check.call(total_after < total_before, "as habilidades tiraram vida dos ratos")
	# Bloqueio de frente (o Arqueiro não bloqueia; o Ninja apara no tempo certo).
	var rat: Enemy = get_tree().get_nodes_in_group(&"enemies")[0]
	rat.global_position = player.global_position + Vector3(0, 0, 1.5)
	player.facing = Vector2(0, 1)
	player.alive = true
	player.health = player.max_health
	player.resource = player.max_resource
	player.shield = 0.0  # escudos das habilidades ainda ativos atrapalhariam a medida
	var block: Dictionary = player.data.get("block", {})
	if block.has("parry_window"):
		Input.action_press(&"block")
		await get_tree().physics_frame
		await get_tree().physics_frame
		var rat_health := rat.health
		var before := player.health
		player.take_damage(30.0, 1, rat)
		check.call(is_equal_approx(player.health, before) and rat.health < rat_health, "Ninja apara no tempo certo e contra-ataca")
		Input.action_release(&"block")
		await get_tree().physics_frame
	elif not block.is_empty():
		var before := player.health
		player.take_damage(30.0, 1, rat)
		var open_loss := before - player.health
		player.health = player.max_health
		Input.action_press(&"block")
		await get_tree().physics_frame
		await get_tree().physics_frame
		check.call(player.blocking, "segurando o bloqueio")
		var resource_before := player.resource
		before = player.health
		player.take_damage(30.0, 1, rat)
		check.call(before - player.health < open_loss - 1.0, "bloqueio de frente reduz o dano (%.1f contra %.1f)" % [before - player.health, open_loss])
		# Barreiras gastam por dano bloqueado; o escudo do Cavaleiro, por segundo erguido.
		await get_tree().physics_frame
		check.call(player.resource < resource_before, "bloquear gasta o recurso")
		Input.action_release(&"block")
		await get_tree().physics_frame
	else:
		Input.action_press(&"block")
		await get_tree().physics_frame
		check.call(not player.blocking, "o Arqueiro não bloqueia")
		Input.action_release(&"block")
	player.health = player.max_health
	# Escudo absorve antes da vida; Escudo de Mana tira da mana.
	player.alive = true
	player.health = player.max_health
	player.add_shield(50.0, 5.0)
	var health := player.health
	# O Ninja pode desviar (evasão): tenta até um golpe pegar.
	for i in 30:
		player.take_damage(20.0)
		if player.shield < 50.0:
			break
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


## O Esgoto de verdade (Fase 7): as 4 áreas carregam com checkpoint; poças e
## golpes no chão ferem; o Sapo cospe com aviso, o Jacaré embosca, a Ratazana
## investe; elite tóxica, baú secreto (uma vez) e a saída em grupo.
func _sewers_test() -> void:
	var player: Player = _arena.local_player
	if player == null or _stage > 0 or _frame < 10:
		return
	_stage = 1
	var checks: Array[String] = []
	var check := func(ok: bool, what: String) -> void:
		if not ok:
			checks.append(what)
	for id in ["sewers_01_drains", "sewers_02_canals", "sewers_03_war_passage", "sewers_04_nest"]:
		_arena.travel(id, "start")
		await get_tree().physics_frame
		check.call(_arena.area_id == id and not get_tree().get_nodes_in_group(&"enemies").is_empty(), "%s carrega com monstros" % id)
		check.call("%s:start" % id in _arena._campaign.checkpoints_reached, "%s: checkpoint na entrada" % id)
		check.call(_arena.result == 0, "%s: sem vitória ao chegar" % id)
	# Mapa que se revela: só em volta de quem andou; fica na campanha e volta igual.
	_arena.travel("sewers_01_drains", "start")
	await _wait_frames(20)
	check.call(_arena.hud.minimap.is_seen(Vector2(0, 3)) and not _arena.hud.minimap.is_seen(Vector2(0, -63)), "minimapa: começo visto, fundo em névoa")
	# Labirinto da área 1: passagens abertas livres, paredes fechadas barram, e dá para chegar ao fundo.
	var maze_rooms: Array = GameData.arenas.sewers_01_drains.rooms
	var by_center := {}
	for room: Dictionary in maze_rooms:
		by_center[Vector2(room.center[0], room.center[1])] = room
	var space: PhysicsDirectSpaceState3D = _arena.get_world_3d().direct_space_state
	var wrong := 0
	var pairs := 0
	var links := {}
	for room: Dictionary in maze_rooms:
		var from := Vector2(room.center[0], room.center[1])
		for side: String in ["east", "south"]:
			var step := Vector2(9, 0) if side == "east" else Vector2(0, 8)
			if not by_center.has(from + step) or not String(room.id).begins_with("maze_"):
				continue
			var other: Dictionary = by_center[from + step]
			var open: bool = side in room.doors
			pairs += 1
			var query := PhysicsRayQueryParameters3D.create(Vector3(from.x, 0.6, from.y), Vector3(from.x + step.x, 0.6, from.y + step.y), 1)
			if open == not space.intersect_ray(query).is_empty():
				wrong += 1
			if open:
				links[room.id] = links.get(room.id, []) + [other.id]
				links[other.id] = links.get(other.id, []) + [room.id]
	check.call(pairs >= 40 and wrong == 0, "labirinto: %d passagens, %d com a colisão errada" % [pairs, wrong])
	var reached := {"maze_2_0": true}
	var frontier := ["maze_2_0"]
	while not frontier.is_empty():
		for next_id: String in links.get(frontier.pop_back(), []):
			if not reached.has(next_id):
				reached[next_id] = true
				frontier.append(next_id)
	var from_entry := PhysicsRayQueryParameters3D.create(Vector3(0, 0.6, 0), Vector3(0, 0.6, -10), 1)
	var to_outfall := PhysicsRayQueryParameters3D.create(Vector3(0, 0.6, -50), Vector3(0, 0.6, -63), 1)
	check.call(space.intersect_ray(from_entry).is_empty() and space.intersect_ray(to_outfall).is_empty(), "labirinto: ligado à entrada e ao fundo")
	var to_secret := PhysicsRayQueryParameters3D.create(Vector3(18, 0.6, -26), Vector3(35, 0.6, -26), 1)
	check.call(reached.has("maze_2_5") and reached.size() >= 30 and space.intersect_ray(to_secret).is_empty(),
		"labirinto: do começo dá para chegar ao fundo (%d salas) e a passagem ao segredo está livre" % reached.size())
	player.teleport_to(Vector3(0, 0, -63))
	await _wait_frames(20)
	check.call(_arena.hud.minimap.is_seen(Vector2(0, -63)), "andar revela o fundo da área")
	_arena.travel("sewers_02_canals", "start")
	check.call(_arena.hud.area_foes_shown() >= 2, "aviso das criaturas da área com o elemento (%d)" % _arena.hud.area_foes_shown())
	_arena.travel("sewers_01_drains", "start")
	await _wait_frames(2)
	check.call(_arena.hud.minimap.is_seen(Vector2(0, -63)) and _arena._campaign.explored.has("sewers_01_drains"), "o que foi visto continua visto ao voltar")
	_arena.hud.minimap.toggle_large()
	check.call(_arena.hud.minimap.large, "mapa grande")
	_arena.hud.minimap.toggle_large()
	# Paredes ao sul do herói (entre ele e a câmera) somem.
	player.teleport_to(Vector3(0, 0, -45))
	await _wait_frames(8)
	check.call(_arena.hidden_walls() > 0, "paredes entre a câmera e o herói somem")
	# Área 1: poça de lodo fere quem está dentro.
	player.teleport_to(Vector3(0, 0, -43))
	player.health = player.max_health
	await _wait_frames(45)
	check.call(player.health < player.max_health, "poça de lodo tira vida")
	# Esgoto pacífico: chegar perto não acorda; o golpe acorda só aquele grupo.
	var calm := _first_enemy("mutant_frog")
	player.teleport_to(calm.global_position + Vector3(0, 0, 2))
	await _wait_frames(10)
	check.call(calm.state == Enemy.State.SLEEP, "bichos do esgoto não atacam quem chega perto")
	calm.take_hit({"damage": 1.0, "element": "", "crit_chance": 0.0})
	await _wait_frames(2)
	check.call(calm.state != Enemy.State.SLEEP, "golpeado, o bicho revida")
	# Ratazana: investida com aviso.
	var mutant := _first_enemy("mutant_frog")
	_arena._wake_group(mutant.group)
	player.teleport_to(mutant.global_position + Vector3(0, 0, 6))
	player.health = player.max_health
	var charged := false
	for i in 150:
		await get_tree().physics_frame
		if mutant.state == Enemy.State.CHARGE:
			charged = true
			break
	check.call(charged, "Ratazana dá a investida")
	# Elite tóxica do segredo; o baú abre uma vez e some.
	var elite := get_tree().get_nodes_in_group(&"enemies").filter(func(e: Enemy) -> bool: return e.group == "s1_secret" and e.category() == "elite")
	check.call(elite.size() == 1 and elite[0].modifier == "toxic" and elite[0].max_health >= 60.0, "elite tóxica no segredo")
	var boxes := get_tree().get_nodes_in_group(&"enemies").filter(func(e: Enemy) -> bool: return e.data.get("breakable", false))
	var expected: int = GameData.arenas.sewers_01_drains.breakables.size()
	check.call(boxes.size() == expected, "%d barris, caixotes e potes na área 1 (%d)" % [expected, boxes.size()])
	for e in get_tree().get_nodes_in_group(&"enemies"):
		e.take_damage(1e9)
	await get_tree().physics_frame
	check.call(_arena._campaign.get("broken", []).size() == expected, "objetos quebrados ficam na campanha")
	# Ratos que saltaram dos barris também caem.
	for e in get_tree().get_nodes_in_group(&"enemies"):
		e.take_damage(1e9)
	await get_tree().physics_frame
	var chest_at: Array = GameData.arenas.sewers_01_drains.props.filter(func(p: Dictionary) -> bool: return p.id == "secret_chest")[0].position
	player.teleport_to(Vector3(chest_at[0], 0, chest_at[1] + 1.0))
	var loot_before: int = _arena._loot.size()
	_arena.request_interact(player)
	check.call("sewers_01_drains:secret_chest" in _arena._campaign.opened and _arena._loot.size() > loot_before, "baú secreto dá loot")
	check.call(_arena.prop_near(player, "chest", "", 5.0).is_empty(), "baú aberto some")
	# Golpe no chão: aviso, dano e poça.
	var puddles: int = _arena.hazards.count()
	player.health = player.max_health
	_arena.telegraph(player.global_position, 1.6, 0.5)
	_arena.monster_strike(player.global_position, 1.6, 10.0, 1, null, {"puddle_time": 5.0, "puddle_dps": 4.0})
	check.call(player.health < player.max_health and _arena.hazards.count() == puddles + 1, "golpe no chão fere e deixa poça")
	# Saída em grupo (sozinho, todo o grupo está perto): desce para a área 2.
	player.teleport_to(Vector3(0, 0, -68))
	_arena.request_interact(player)
	await get_tree().physics_frame
	check.call(_arena.area_id == "sewers_02_canals", "saída leva à área 2")
	# Sapo Ácido: cospe com aviso no chão.
	var toad := _first_enemy("acid_toad")
	_arena._wake_group(toad.group)
	player.teleport_to(toad.global_position + Vector3(0, 0, 6))
	var spat := false
	for i in 150:
		await get_tree().physics_frame
		if toad.state == Enemy.State.WINDUP and toad._special == "spit":
			spat = true
			break
	check.call(spat, "Sapo prepara o cuspe")
	# Jacaré: escondido até alguém chegar perto.
	_arena.travel("sewers_03_war_passage", "start")
	var gator := _first_enemy("sewer_gator")
	_arena._wake_group(gator.group)
	check.call(gator.state == Enemy.State.HIDDEN, "Jacaré acorda escondido na água")
	player.teleport_to(gator.global_position + Vector3(0, 0, 3))
	await _wait_frames(5)
	check.call(gator.state != Enemy.State.HIDDEN, "Jacaré sai da água quando alguém chega perto")
	var old_gator := _first_enemy("old_gator")
	check.call(old_gator.category() == "miniboss", "Jacaré Velho é mini-chefe")
	# A Rainha dos Ratos: 3 fases, ninhos, Pacto, barra do chefe; o tesouro.
	_arena.travel("sewers_04_nest", "start")
	var queen := _first_enemy("demon_rat_queen")
	_arena._wake_group(queen.group)
	player.max_health = 1e6
	player.health = 1e6
	player.teleport_to(queen.global_position + Vector3(0, 0, 12))
	await _wait_frames(3)
	check.call(queen.phase == 1 and _arena.hud.boss_visible(), "Rainha acorda na fase 1, com a barra do chefe")
	queen.health = queen.max_health * 0.55
	await _wait_frames(2)
	var nests := get_tree().get_nodes_in_group(&"enemies").filter(func(e: Enemy) -> bool: return e.monster_id == "spawn_nest")
	check.call(queen.phase == 2 and nests.size() == 3, "abaixo de 60%%: A Ninhada, com 3 ninhos (%d)" % nests.size())
	var before := queen.health
	await _wait_frames(30)
	check.call(queen.health > before, "com ninhos de pé, a Rainha regenera")
	var nest: Enemy = nests[0]
	var nest_health := nest.health
	nest.take_hit({"damage": 10.0, "element": "fire", "crit_chance": 0.0})
	check.call(nest_health - nest.health >= 20.0, "Fogo em dobro no ninho (%.0f)" % (nest_health - nest.health))
	for n: Enemy in nests:
		n.take_damage(1e9)
	await _wait_frames(2)
	before = queen.health
	await _wait_frames(30)
	check.call(is_equal_approx(queen.health, before) or queen.health < before, "sem ninhos, não regenera")
	# Metade da vida: asas de morcego e a Rajada das Asas, que empurra o herói.
	queen.health = queen.max_health * 0.45
	player.teleport_to(queen.global_position + Vector3(0, 0, 3))
	var pushed := false
	var gusted := false
	var hit_health := player.health
	for i in 300:
		await get_tree().physics_frame
		gusted = gusted or (queen.state == Enemy.State.WINDUP and queen._special == "gust")
		if player.is_knocked_back():
			pushed = true
			break
	check.call(queen.has_wings(), "Rainha ganha asas na metade da vida")
	check.call(gusted and pushed, "Rajada das Asas: aviso e empurrão (aviso %s, empurrão %s, %.1f m, vida %.0f→%.0f, conectado %s, invulnerável %s, estado %d, timers %s)" % [
		gusted, pushed, player.global_position.distance_to(queen.global_position), hit_health, player.health,
		player.connected, player.is_invulnerable(), queen.state, queen.boss_timers])
	queen.health = queen.max_health * 0.2
	# O gás mira um herói de pé: o do teste (nível 1) aguenta a luta toda.
	if not player.alive:
		player.revive(1.0)
	player.max_health = 1e6
	player.health = 1e6
	var gas_before: int = _arena.hazards.count()
	await _wait_frames(420)
	check.call(queen.phase == 3 and _arena._area_root.get_node_or_null("flood") != null, "abaixo de 25%: O Pacto alaga a arena")
	check.call(_arena.hazards.count() > gas_before, "o gás dos canos deixa poças (antes %d, agora %d, timers %s, alvo %s, estado %d, herói vivo %s a %.1f m)" % [
		gas_before, _arena.hazards.count(), queen.boss_timers, queen._nearest_player(), queen.state, player.alive,
		player.global_position.distance_to(queen.global_position)])
	queen.take_damage(1e9)
	await _wait_frames(2)
	var leftovers := get_tree().get_nodes_in_group(&"enemies").filter(func(e: Enemy) -> bool: return e.group == "" and not e.is_queued_for_deletion())
	check.call(leftovers.is_empty() and not _arena.hud.boss_visible(), "ajudantes somem com a Rainha; a barra some")
	for e in get_tree().get_nodes_in_group(&"enemies"):
		e.take_damage(1e9)
	await _wait_frames(2)
	check.call(_arena.result == 1, "vencer o Ninho é a vitória do mapa")
	_arena.pick_key(player, {"id": "boss_key", "key": "key_rat_queen"})
	player.teleport_to(Vector3(0, 0, -48))
	var loot_ids: Array = _arena._loot.keys()
	_arena.request_interact(player)
	var legendary := false
	for id in _arena._loot:
		if id not in loot_ids and _arena._loot[id].item.get("rarity", "") == "legendary":
			legendary = _arena._loot[id].item.get("legendary", "") == Legendaries.for_boss("demon_rat_queen", "mage")
	check.call(legendary, "tesouro dá o lendário do Mago")
	check.call("fallen_king_crown" in _arena.town.relics and "map_ruins" in _arena.town.unlocked, "Coroa do Rei Caído e o mapa das Ruínas")
	# O baú aberto continua aberto ao voltar.
	_arena.travel("sewers_01_drains", "start")
	var chest_left: Dictionary = _arena.prop_near(player, "chest", "", 300.0)
	check.call(chest_left.is_empty() or chest_left.id != "secret_chest", "baú aberto não volta")
	check.call(not get_tree().get_nodes_in_group(&"enemies").any(func(e: Enemy) -> bool: return e.data.get("breakable", false) and not e.is_queued_for_deletion()),
		"barris quebrados não voltam")
	_report(checks.is_empty(), "esgoto: " + ("tudo certo" if checks.is_empty() else "; ".join(PackedStringArray(checks))))


func _wait_frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _first_enemy(monster_id: String) -> Enemy:
	for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
		if e.monster_id == monster_id and not e.is_queued_for_deletion():
			return e
	return null


## Uma volta por Tortuga, chamando o servidor como as janelas chamariam.
func _town_test() -> void:
	var player: Player = _arena.local_player
	if player == null or _stage > 0 or _frame < 10:
		return
	_stage = 1
	var checks: Array[String] = []
	var check := func(ok: bool, what: String) -> void:
		if not ok:
			checks.append(what)
	var town: Town = _arena.town
	var c := player.character
	check.call(_arena.area_id == "tavern", "campanha nova começa na Taverna (%s)" % _arena.area_id)
	# Pulo: sai do chão, passa por cima de poças no pico e volta ao chão.
	player._update_jump(0.0, true)
	check.call(player.jump_phase > 0.0, "pular: sai do chão")
	for i in 19:
		player._update_jump(0.016, false)
	check.call(player.is_airborne() and absf(player.jump_height() - Player.JUMP_HEIGHT) < 0.1, "pular: no pico chega perto da altura máxima (%.2f)" % player.jump_height())
	for i in 25:
		player._update_jump(0.016, false)
	check.call(player.jump_phase == 0.0 and not player.is_airborne(), "pular: volta ao chão")
	# Herói montado das peças da Quaternius: todas as animações e a roupa de Camponês.
	var model: HeroModel = player._model
	check.call(model.animations().size() == HeroModel.ANIMS.size(), "herói com todas as animações (%s)" % [model.animations()])
	check.call(model._anim != null and model._anim.is_playing(), "herói animado ao nascer")
	check.call("Peasant_Body" in model.visible_parts() and "Head" in model.visible_parts(), "roupa de Camponês e rosto à mostra (%s)" % [model.visible_parts()])
	# Monstros do Esgoto com modelo animado (rato, morcego, jacaré, a Rainha).
	for monster_id: String in ["plague_frog", "plague_bat", "sewer_gator", "demon_rat_queen"]:
		var probe := Enemy.create({"monster_id": monster_id, "position": Vector3(0, -50, 0)})
		add_child(probe)
		check.call(probe.model_family() != "", "%s com modelo animado" % monster_id)
		check.call(probe.model_animation() == "idle", "%s parado em idle (%s)" % [monster_id, probe.model_animation()])
		if monster_id == "demon_rat_queen":
			check.call(not probe.has_wings(), "Rainha sem asas com a vida cheia")
			probe.health = probe.max_health * 0.4
			probe._tick_visual(0.016)
			check.call(probe.has_wings(), "Rainha ganha asas de morcego na metade da vida")
		if monster_id == "plague_frog":
			# Morte: o corpo fica na área tocando a animação de morrer.
			var corpse := probe._model
			probe.take_damage(1e9)
			check.call(is_instance_valid(corpse) and corpse.get_parent().get_parent() == _arena._area_root and corpse.current() == "die",
				"rato morto deixa o corpo tocando a morte (%s)" % [corpse.current() if is_instance_valid(corpse) else "sumiu"])
			continue
		probe.queue_free()
	# Lagarto Dourado: não ataca; golpeado, corre e solta moedas.
	var lizard := Enemy.create({"monster_id": "golden_lizard", "position": Vector3(3, -50, 3)})
	add_child(lizard)
	var coins_before: int = _arena._loot.size()
	lizard.take_damage(5.0)
	check.call(lizard._flee_time > 0.0 and _arena._loot.size() > coins_before, "Lagarto Dourado foge e solta moedas ao levar golpe")
	lizard.queue_free()
	# Pote de barro: modelo do kit pela posição; quebrado, os cacos voam.
	var pot := Enemy.create({"monster_id": "pot", "position": Vector3(1.3, -50, 0.7)})
	add_child(pot)
	var shards_before: int = _arena._area_root.get_child_count()
	check.call(pot._kit_piece in GameData.monsters.pot.pieces and Kit.has(pot._kit_piece + "_Shards"), "pote com modelo e cacos (%s)" % pot._kit_piece)
	pot.take_damage(1e9)
	check.call(_arena._area_root.get_child_count() > shards_before, "pote quebrado solta os cacos")
	# Toda peça citada no estilo e no cenário das áreas existe no kit.
	var missing: Array[String] = []
	for area_id: String in GameData.arenas:
		if not GameData.arenas[area_id] is Dictionary:
			continue
		var area: Dictionary = GameData.arenas[area_id]
		var style: Dictionary = area.get("style", {})
		var pieces: Array = style.get("walls", []).duplicate()
		pieces.append(style.get("floor", ""))
		for decor: Dictionary in area.get("decor", []):
			pieces.append(decor.get("piece", ""))
		for piece: String in pieces:
			if piece != "" and not Kit.has(piece) and not missing.has(piece):
				missing.append(piece)
	check.call(missing.is_empty(), "peças do kit que faltam: %s" % [missing])
	# Abertura: o herói do jogador conta primeiro; "Pular abertura" fecha.
	var opening: OpeningMenu = _arena._opening_menu
	check.call(opening.visible and opening.current_key() == "OPENING_SCENE_MAGE", "abertura começa pela história do Mago (%s)" % opening.current_key())
	check.call(Session.ui_open, "abertura segura o herói")
	opening._advance()
	check.call(opening.current_key() == "OPENING_MAGE_1", "Continuar passa a fala")
	opening.close()
	check.call(not opening.visible and not Session.ui_open, "pular abertura fecha")
	# Dicas: a primeira aparece no HUD e fica guardada no personagem.
	Settings.tips = true
	player.character.data.tutorial_seen = []
	Session.character.data.tutorial_seen = []
	TipManager.reset()
	_arena.tips._started = false
	_arena.tips.check(player)
	check.call(TipManager.current() == "tip_move" and _arena.hud.tip_text() != "", "dica de movimento no HUD (%s)" % TipManager.current())
	check.call("tip_move" in player.character.data.get("tutorial_seen", []), "dica vista guardada no personagem")
	check.call(town.has_offer("old_drunk") and not town.has_offer("bard"), "Velho Bêbado com \"!\"")
	# Aceitar a missão longe dele não vale; perto, vale e abre o bueiro.
	town._rpc_accept("sewer_treasure")
	check.call(not town.quests.has("sewer_treasure"), "não aceita missão longe do NPC")
	player.teleport_to(Vector3(-5.5, 0, -1))
	town._rpc_accept("sewer_treasure")
	check.call(town.quests.get("sewer_treasure", "") == "active" and "sewer_entrance" in town.unlocked, "missão aceita abre o bueiro")
	check.call(town.active_quest() == "sewer_treasure" and not town.has_offer("old_drunk"), "missão no diário, sem \"!\"")
	town.send_opening(player.peer_id)
	check.call(not opening.visible, "com a missão aceita, a abertura não volta")
	# Descansar com a Taberneira.
	player.health = 10.0
	player.teleport_to(Vector3(0, 0, -4))
	town._rpc_service("tavern_keeper", "rest")
	check.call(is_equal_approx(player.health, player.max_health), "descansar enche a vida")
	# Sair para a Rua Principal.
	player.teleport_to(Vector3(0, 0, 6))
	_arena.request_interact(player)
	await get_tree().physics_frame
	check.call(_arena.area_id == "tortuga", "porta da Taverna leva à Rua Principal")
	# Boticário.
	var gold := int(c.data.gold)
	var potions := c.count_of("potion_health")
	player.teleport_to(Vector3(-20, 0, -4.5))
	town._rpc_buy("potions", 0)
	c = player.character
	check.call(int(c.data.gold) == gold - 18 and c.count_of("potion_health") == potions + 1, "compra poção de vida por 18")
	# Mercado Pirata: Poção Elemental e venda de equipamento e valiosos.
	player.teleport_to(Vector3(0, 0, -25.4))  # ponta da doca, na frente do navio
	gold = int(c.data.gold)
	town._rpc_buy("pirate", 0)
	c = player.character
	check.call(c.count_of("elemental_potion_water") == 1 and int(c.data.gold) == gold - 125, "compra Poção Elemental de Água por 125")
	c.add_item(Items.equipment("staff", "iron", "common", 3))
	c.add_item(Items.stack(Items.VALUABLE, "old_coins", 2))
	gold = int(c.data.gold)
	var staff_index := -1
	var coins_index := -1
	for i in c.data.inventory.size():
		var item: Variant = c.data.inventory[i]
		if item != null and item.kind == Items.EQUIPMENT and item.base == "staff":
			staff_index = i
		if item != null and item.kind == Items.VALUABLE:
			coins_index = i
	var expected := Shops.sell_price("pirate", c.data.inventory[staff_index], 1, town.ship) \
		+ Shops.sell_price("pirate", c.data.inventory[coins_index], 1, town.ship)
	town._rpc_sell("pirate", staff_index)
	town._rpc_sell("pirate", coins_index)
	c = player.character
	check.call(int(c.data.gold) == gold + expected, "vende cajado (25%%) e valiosos (preço do dia): +%d" % expected)
	# Poção Elemental e descida pelo bueiro.
	player._drink("elemental_potion_water")
	check.call(player.element == "water", "bebeu a Poção de Água")
	player.teleport_to(Vector3(22, 0, 3))
	_arena.request_interact(player)
	await get_tree().physics_frame
	check.call(_arena.area_id == "sewers_01_drains" and not get_tree().get_nodes_in_group(&"enemies").is_empty(), "bueiro leva ao Esgoto com monstros")
	# Limpar a área 1 não é vitória (só a área final); a saída leva adiante.
	for e in get_tree().get_nodes_in_group(&"enemies"):
		e.take_damage(1e9)
	await get_tree().physics_frame
	check.call(_arena.result == 0 and town.quests.get("sewer_treasure", "") == "active", "área 1 limpa não conclui a missão")
	# Vencer a Rainha no Ninho conclui a missão; aparecem o tesouro e o portal.
	_arena.travel("sewers_04_nest", "start")
	gold = int(player.character.data.gold)
	# O tesouro já está lá, trancado: a chave cai da Rainha.
	player.teleport_to(Vector3(0, 0, -48))
	_arena.request_interact(player)
	check.call("sewers_04_nest:war_treasure" not in _arena._campaign.get("opened", []), "o tesouro da Rainha começa trancado")
	for e in get_tree().get_nodes_in_group(&"enemies"):
		e.take_damage(1e9)
	await get_tree().physics_frame
	check.call(town.quests.get("sewer_treasure", "") == "done", "vencer a Rainha conclui a missão")
	check.call(int(player.character.data.gold) >= gold + 150, "recompensa da missão")
	var dropped: Dictionary = _arena.prop_near(player, "key", "", 300.0)
	check.call(not dropped.is_empty(), "a Rainha deixa cair a chave do tesouro")
	if not dropped.is_empty():
		_arena.pick_key(player, dropped)
	check.call("key_rat_queen" in _arena._campaign.get("keys", []), "a chave fica com o grupo")
	player.teleport_to(Vector3(0, 0, -48))
	var loot_before: int = _arena._loot.size()
	_arena.request_interact(player)
	check.call(_arena._loot.size() > loot_before + 2 and "sewers_04_nest:war_treasure" in _arena._campaign.opened, "Tesouro Perdido da Guerra abre e dá loot")
	# Portal de volta: Tortuga, fim da expedição, navio novo.
	player.teleport_to(Vector3(8, 0, -48))
	_arena.request_interact(player)
	await get_tree().physics_frame
	check.call(_arena.area_id == "tortuga", "portal de retorno leva a Tortuga")
	check.call(player.element == player.character.data.element and player.character.data.element_potion == "", "voltar a Tortuga encerra a Poção Elemental")
	check.call(int(town.ship.day) == 1, "chegou um navio novo")
	check.call(Session.campaign.area == "tortuga", "a campanha lembra onde o grupo está")
	# Pátio de treino (agora na Capital): bonecos que não morrem, painel do grupo, recursos livres.
	_arena.travel("capital_01_aurenhold", "start")
	var dummies := get_tree().get_nodes_in_group(&"enemies").filter(func(e: Enemy) -> bool: return e.data.get("dummy", false))
	check.call(dummies.size() == 11, "11 bonecos no pátio (%d)" % dummies.size())
	player.teleport_to(Vector3(-9, 0, 11))
	check.call(_arena.in_training(player.global_position), "herói dentro do pátio")
	var xp := int(player.character.data.xp)
	var fire_dummy: Enemy = dummies.filter(func(e: Enemy) -> bool: return e.monster_id == "training_dummy_fire")[0]
	var result: Dictionary = fire_dummy.take_hit({"damage": 40.0, "element": "water", "state": "", "crit_chance": 0.0})
	check.call(result.get("effect", "") == "weak", "Água no boneco de Fogo: fraqueza")
	fire_dummy.take_damage(1e9)
	await get_tree().physics_frame
	check.call(is_instance_valid(fire_dummy) and fire_dummy.health > 0.0, "boneco não morre")
	check.call(int(player.character.data.xp) == xp, "boneco não dá experiência")
	check.call(float(_arena.training.get("total", 0.0)) > 60.0 and int(_arena.training.get("hits", 0)) >= 2, "painel soma o dano do grupo")
	var giant: Enemy = dummies.filter(func(e: Enemy) -> bool: return e.monster_id == "training_dummy_giant")[0]
	Elements.apply_state(giant.status, "stunned", giant.element, giant.is_boss())
	check.call(giant.status.has("slowed") and not giant.status.has("stunned"), "boneco gigante age como chefe (lentidão no lugar de atordoar)")
	var armored: Enemy = dummies.filter(func(e: Enemy) -> bool: return e.monster_id == "training_dummy_armored")[0]
	var before := armored.health
	armored.take_damage(100.0)
	check.call(is_equal_approx(before - armored.health, 50.0), "boneco blindado recebe metade")
	_arena.request_training("toggle_free")
	player.resource = 0.0
	await get_tree().physics_frame
	await get_tree().physics_frame
	check.call(is_equal_approx(player.resource, player.max_resource) and player.free_cooldowns, "recursos e recargas livres no pátio")
	_arena.request_training("reset_stats")
	check.call(int(_arena.training.get("hits", -1)) == 0, "zerar o painel")
	_arena.request_training("toggle_free")
	# Macumbeiro: Patuá de Retorno e portal para o ponto salvo do Esgoto.
	player.character.data.gold = 1000
	player.teleport_to(Vector3(16, 0, -3.5))
	town._rpc_buy("voodoo", 0)
	check.call(player.character.count_of("return_charm") == 1 and int(player.character.data.gold) == 850, "compra o Patuá por 150")
	player._drink("return_charm")
	check.call(player.character.count_of("return_charm") == 1, "Patuá não funciona na cidade")
	check.call("sewers_01_drains:start" in town.reached, "ponto salvo do Esgoto na lista")
	_arena.travel("tortuga", "start")
	player.teleport_to(Vector3(12, 0, -4.5))
	var price := Town.portal_price("sewers_01_drains:start")
	town._rpc_portal("sewers_01_drains:start")
	check.call(_arena.area_id == "sewers_01_drains" and int(player.character.data.gold) == 850 - price, "portal do Macumbeiro leva ao Esgoto por %d" % price)
	player._drink("return_charm")
	check.call(player.character.count_of("return_charm") == 0 and not _arena.prop_near(player, "exit", "charm_portal", 5.0).is_empty(), "Patuá abre o portal no chão")
	_arena.request_interact(player)
	check.call(_arena.area_id == "tortuga", "portal do Patuá volta a Tortuga")
	# Baú: guardar e tirar (o baú fica no PC do dono).
	var bag_coins := Items.stack(Items.VALUABLE, "silver_goblet", 1)
	player.character.add_item(bag_coins)
	var goblet_index: int = player.character.data.inventory.find(bag_coins)
	player.teleport_to(Vector3(-5, 0, 4.5))
	town._rpc_deposit(goblet_index)
	check.call(player.character.count_of("silver_goblet") == 0 and SaveSystem.load_stash().any(func(i: Variant) -> bool: return i != null and i.id == "silver_goblet"), "guarda o cálice no baú")
	var stash_index := SaveSystem.load_stash().find(SaveSystem.load_stash().filter(func(i: Variant) -> bool: return i != null)[0])
	town.request_withdraw(stash_index)
	check.call(player.character.count_of("silver_goblet") == 1 and SaveSystem.load_stash().all(func(i: Variant) -> bool: return i == null), "tira o cálice do baú")
	# Mestre: redistribuir pontos pagando ouro.
	var hero := player.character
	hero.data.free_points = 0
	hero.data.attributes.int = int(hero.data.attributes.int) + 5
	var respec_cost := hero.respec_price()
	var gold_before := int(hero.data.gold)
	player.teleport_to(Vector3(-22, 0, 3.5))
	town._rpc_service("master", "respec")
	hero = player.character
	check.call(int(hero.data.free_points) == 5 * (int(hero.data.level) - 1) and int(hero.data.gold) == gold_before - respec_cost, "Mestre devolve os pontos por %d" % respec_cost)
	# Visitantes, missões secundárias e bestiário.
	check.call("demon_rat_queen" in town.bestiary, "a história do Velho Bêbado pôs a Rainha dos Ratos no bestiário")
	check.call(town.visitors.size() >= 2, "voltar a Tortuga trouxe visitantes (%d)" % town.visitors.size())
	var hunt := {"type": "hunter", "name": "Teste", "quest": SideQuests.make_quest("sq_test_hunt", "hunt", "prototype_arena", RandomNumberGenerator.new())}
	hunt.quest.target = "plague_frog"
	hunt.quest.count = 2
	var cargo := {"type": "merchant", "name": "Teste 2", "quest": SideQuests.make_quest("sq_test_cargo", "retrieve", "prototype_arena", RandomNumberGenerator.new())}
	_arena._campaign.visitors = [hunt, cargo]
	town.sync()
	_arena.travel("tavern", "start")
	check.call(_arena.prop_near(player, "npc", "visitor:0", 50.0).size() > 0, "visitantes sentados na Taverna")
	for i in 2:
		player.teleport_to(Vector3(GameData.visitors.seats[0][0], 0, GameData.visitors.seats[0][1] + 0.8))
		town._rpc_accept_side(0)
	check.call(SideQuests.active(town.side_quests).size() == 2 and town.visitors.is_empty(), "aceitou as duas histórias")
	check.call("plague_frog" in town.bestiary, "a criatura da caçada entrou no bestiário")
	# Caçada: matar 2 ratos no Esgoto; carga: achar o caixote. (O Esgoto já foi
	# limpo neste teste e mortos continuam mortos: os grupos voltam só para a caçada.)
	_arena._campaign.dead_groups = []
	_arena.travel("prototype_arena", "start")
	var spot: Array = GameData.arenas.prototype_arena.quest_spots[int(cargo.quest.spot)]
	check.call(not _arena.prop_near(player, "quest_spot", "", 300.0).is_empty(), "carga perdida aparece no mapa")
	var killed := 0
	for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
		if e.monster_id == "plague_frog" and killed < 2:
			e.take_damage(1e9)
			killed += 1
	await get_tree().physics_frame
	check.call(town.side_quests.sq_test_hunt.status == "done", "caçada concluída")
	player.teleport_to(Vector3(spot[0], 0, spot[1] + 0.5))
	var gold_cargo := int(player.character.data.gold)
	_arena.request_interact(player)
	check.call(town.side_quests.sq_test_cargo.status == "done" and int(player.character.data.gold) > gold_cargo, "carga entregue: recompensa")
	# Ferreiro: comprar pergaminhos, refinar até +3, aura, cristalizar.
	_arena.travel("capital_01_aurenhold", "start")
	player.character.data.gold = 2000
	player.character.add_item(Items.equipment("staff", "iron", "common", 2))
	player.teleport_to(Vector3(4, 0, -3.5))
	for i in 3:
		town._rpc_buy("blacksmith", 0)
	check.call(player.character.count_of("scroll_refine_weapon_iron") == 3, "compra 3 pergaminhos de arma de Ferro")
	var staff_ref := ""
	for i in player.character.data.inventory.size():
		var it: Variant = player.character.data.inventory[i]
		if it != null and it.kind == Items.EQUIPMENT and it.base == "staff" and it.material == "iron":
			staff_ref = "bag:%d" % i
	for i in 3:
		town._rpc_refine(staff_ref, false)
	var refined: Dictionary = Town.item_at(player.character, staff_ref)
	check.call(int(refined.refine) == 3 and player.character.count_of("scroll_refine_weapon_iron") == 0, "refina até +3 (seguro)")
	player.request_equip(int(staff_ref.get_slice(":", 1)))
	await get_tree().physics_frame
	check.call(player.aura_level == 3, "arma +3 acende a aura (%d)" % player.aura_level)
	player.character.add_item(Items.equipment("hood", "iron", "common", 2))
	var hood_index := -1
	for i in player.character.data.inventory.size():
		var it: Variant = player.character.data.inventory[i]
		if it != null and it.kind == Items.EQUIPMENT and it.base == "hood":
			hood_index = i
	town._rpc_crystallize(hood_index)
	check.call(player.character.count_of("crystal_iron") == 2, "cristaliza o capuz em 2 cristais de Ferro")
	_report(checks.is_empty(), "cidade: " + ("tudo certo" if checks.is_empty() else "; ".join(PackedStringArray(checks))))


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
