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
	var hero := CharacterData.create("mage", "male", "Bot")
	hero.data.xp = 680  # quase no nível 2, para o teste ver a subida
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
		_role = "revive" if args.size() > 0 and args[0] == "revive" else "solo"
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
		for i in c.data.inventory.size():
			var item: Variant = c.data.inventory[i]
			if item != null and c.can_equip(item):
				player.request_use(i)
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
	var ok: bool = _max_players_seen >= _expected_players and _max_enemies_seen > 0 \
		and (_resumed > 0 or not _expect_resume) \
		and int(c.data.level) >= 2 and int(c.data.gold) > 0 and items + gear > 1 and gear >= 2 \
		and saved != null and saved.data.level == c.data.level and saved.data.gold == c.data.gold
	_report(ok, "vitória com %d jogador(es), %d retomado(s); nível %d, ouro %d, %d itens na bolsa, %d equipados, save no disco: %s" % [
		_max_players_seen, _resumed, c.data.level, c.data.gold, items, gear, saved != null])


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
	# O host espera um pouco para o cliente também ver a vitória.
	var wait := 1.5 if _role == "host" else 0.1
	get_tree().create_timer(wait).timeout.connect(func() -> void:
		NetworkManager.leave()
		get_tree().quit(0 if ok else 1))
