# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Abre a arena com um Invocador de teste: nível máximo, todas as habilidades no rank máximo, nada gravado em disco.
##   godot --path . res://tests/summoner_sandbox.tscn -- [water|air|fire|earth]   (padrão: water) [class=mage|archer|knight|ninja (padrão: summoner)] [area=<id>, ex.: area=tavern] [at=x,z, ex.: at=0,-185 para ir a um ponto do mapa] [shot=<arquivo.png>: salva uma captura e sai] [kill=<id do monstro, ex.: old_gator>: mata esse monstro e abre o baú que ele deixa; com "nochest" deixa o baú fechado para ver]; chama todos os animais, ou só os listados depois do elemento (otter = lobo de água, fox, falcon, boar, bear)


var _cam: Camera3D
var _yaw := 0.0
var _pitch := 0.0
var _speed := 12.0


func _process(delta: float) -> void:
	if _cam == null:
		return
	var move := Vector3.ZERO
	move.z = float(Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN)) - float(Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP))
	move.x = float(Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT)) - float(Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT))
	move.y = float(Input.is_key_pressed(KEY_E) or Input.is_key_pressed(KEY_SPACE)) - float(Input.is_key_pressed(KEY_Q) or Input.is_key_pressed(KEY_CTRL))
	_cam.position += _cam.global_transform.basis * move * _speed * (3.0 if Input.is_key_pressed(KEY_SHIFT) else 1.0) * delta
	if not _cam.current:
		_cam.make_current()


func _unhandled_input(event: InputEvent) -> void:
	if _cam == null:
		return
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		_yaw -= event.relative.x * 0.003
		_pitch = clampf(_pitch - event.relative.y * 0.003, -1.5, 1.5)
		_cam.rotation = Vector3(_pitch, _yaw, 0.0)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_speed = minf(_speed * 1.25, 80.0)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_speed = maxf(_speed / 1.25, 1.0)


func _ready() -> void:
	# Saves isolados: nada daqui entra na lista de personagens nem nas campanhas de verdade.
	SaveSystem.root = "user://test_saves/summoner_sandbox"
	var args: PackedStringArray = []
	var area := ""
	var at := PackedStringArray()
	var shot := ""
	var hero_class := "summoner"  # class=mage|archer|knight|ninja|summoner
	var kill := ""
	var open_chest := true
	for arg in OS.get_cmdline_user_args():
		if arg == "nochest":
			open_chest = false
		elif arg.begins_with("kill="):
			kill = arg.trim_prefix("kill=")
		elif arg.begins_with("shot="):
			shot = arg.trim_prefix("shot=")
		elif arg.begins_with("at="):
			at = arg.trim_prefix("at=").split(",")
		elif arg.begins_with("area="):
			area = arg.trim_prefix("area=")
		elif arg.begins_with("class="):
			hero_class = arg.trim_prefix("class=")
		else:
			args.append(arg)
	var element: String = args[0] if args.size() > 0 else "water"
	var c := CharacterData.create(hero_class, "female", "Teste", element)
	c.data.level = int(GameData.balance.max_level)
	c.data.free_points = 0
	var skills := {}
	var slots: Array = []
	for key in Skills.keys(hero_class):
		skills[key] = Skills.max_rank()
		if slots.size() < int(GameData.skills.slots) and Skills.is_active(c.skill_of(key)):
			slots.append(key)
	while slots.size() < int(GameData.skills.slots):
		slots.append("")
	c.data.skills = skills
	c.data.skill_slots = slots
	c.data.skill_points = 0
	c.data.gold = 100000
	Session.character = c
	Session.campaign = SaveSystem.new_campaign()
	if area != "" and GameData.arenas.has(area):
		Session.campaign.area = area
	NetworkManager.prepare_solo()
	var arena: Node = load("res://game/levels/prototype_arena.tscn").instantiate()
	add_child(arena)
	if at.size() == 2:
		await get_tree().create_timer(1.0).timeout
		if arena.local_player != null:
			arena.local_player.global_position = Vector3(float(at[0]), 0.5, float(at[1]))
	if "spectator" in args:  # modo espectador: câmera livre sobre o mapa (W/A/S/D andam, E/Espaço sobe, Q/Ctrl desce, Shift acelera, botão direito + arrastar olha, roda muda a velocidade)
		await get_tree().create_timer(1.0).timeout
		Session.ui_open = true
		arena.hud.visible = false
		var focus := Vector3(float(at[0]), 0.0, float(at[1])) if at.size() == 2 else Vector3(arena.local_player.global_position.x, 0.0, arena.local_player.global_position.z)
		_cam = Camera3D.new()
		_cam.far = 600.0
		_cam.position = focus + Vector3(0, 60 if not "low" in args else 12, 45 if not "low" in args else 14)
		_pitch = deg_to_rad(-55.0)
		_cam.rotation = Vector3(_pitch, 0, 0)
		add_child(_cam)
		_cam.make_current()
	if hero_class == "summoner":
		_summon_all(arena, args.slice(1))
	if "invpopup" in args:  # abre o inventário com o Livro do Altar e a caveira de Morvak e o detalhe (botão direito) do livro, para conferir
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena.local_player.character.add_item(Items.stack(Items.VALUABLE, "altar_book"))
			arena.local_player.character.add_item(Items.stack(Items.VALUABLE, "cursed_skull"))
			arena._inventory.toggle()
			var bag: Array = arena.local_player.character.data.inventory
			for i in bag.size():
				if bag[i] != null and bag[i].get("id", "") == "altar_book":
					arena._inventory._show_popup({"bag": i}))
	if "flock" in args:  # lança a Revoada de frente para os bonecos de treino da Capital, perto do instante da captura (os falcões ainda estão voando)
		get_tree().create_timer(4.85).timeout.connect(func() -> void:
			arena.local_player.facing = Vector2(0, -1)
			arena.skills.cast(arena.local_player, "flock", 3))
	if "birdshot" in args:  # dispara o ataque básico (a ave do Invocador) para o norte, perto do instante da captura
		get_tree().create_timer(4.85).timeout.connect(func() -> void:
			arena.local_player.facing = Vector2(0, -1)
			arena.local_player._fire(arena.local_player.data.strong_attack if "strong" in args else arena.local_player.data.basic_attack))
	if "shell" in args:  # lança as Asas do Falcão para ver as 3 aves e a poeira (a captura sai 2,5 s depois)
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena.skills.cast(arena.local_player, "falcon_wings", 3))
	if "skillmenu" in args:  # abre o menu de habilidades (tecla K), com o dock dos 4 atalhos por cima, e simula soltar a 1ª habilidade ativa no atalho 4
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena._skill_menu.toggle()
			arena._skill_menu._drop_skill(Vector2.ZERO, {"skill_key": "stampede"}, 3)
			await get_tree().create_timer(0.8).timeout
			arena._skill_menu._refresh()
			print("SLOTS ", arena.local_player.character.data.skill_slots))
	if "cdbar" in args:  # lança as habilidades 2 e 3 (Revoada e Asas do Falcão) para ver o vermelho de recarga descendo nos atalhos
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena.local_player.facing = Vector2(0, -1)
			for i in [1, 2]:
				arena.local_player._cast_slot(i))
	if "feathers" in args:  # solta penas das aves em cima do herói para ver as penas caindo (a captura sai 1 s depois)
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			for i in 8:
				var holder := Node3D.new()
				arena.local_player.add_child(holder)
				holder.position = Vector3(randf_range(-3.0, 3.0), randf_range(2.0, 3.0), randf_range(-3.0, 3.0))
				arena.skills._drop_feather(holder))
	if "blizzard" in args:  # lança a Nevasca (Mago de Água) de frente para os bonecos de treino
		get_tree().create_timer(2.0).timeout.connect(func() -> void:
			arena.local_player.facing = Vector2(0, -1)
			arena.skills.cast(arena.local_player, "blizzard", 3))
	if "callskill" in args:  # usa o atalho 1 (Chamar Companheiro), como o jogador, para ver qual animal sai
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena.local_player._cast_slot(0))
	if "stampede" in args:  # lança o Estouro da Manada para o norte, de frente para os bonecos de treino (a captura sai logo depois)
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena.local_player.facing = Vector2(0, -1)
			print("STAMPEDE cast=", arena.skills.cast(arena.local_player, "stampede", 3), " bull=", Kit.has("Bull")))
	if "rhino" in args:  # lança a Investida do Rinoceronte no boneco de treino mais perto, ao norte (a captura sai no meio da corrida)
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena.local_player.facing = Vector2(0, -1)
			print("RHINO cast=", arena.skills.cast(arena.local_player, "rhino_charge", 3), " model=", Kit.has("Rhino")))
	if "mammoth" in args:  # lança a Pisada do Mamute (a captura sai na primeira pisada)
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena.local_player.facing = Vector2(0, -1)
			print("MAMMOTH cast=", arena.skills.cast(arena.local_player, "mammoth_stomp", 3), " model=", Kit.has("Elephant")))
	if "talk" in args:  # ataque básico perto de um NPC da taverna abre a conversa (imprime o resultado); longe dele, não
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			var npc: Dictionary = arena.prop_near(arena.local_player, "npc", "", 999.0)
			print("TALK far=", arena.local_player._talk_to_npc_near(), " npc=", npc.get("npc", "?"))
			arena.local_player.global_position = Vector3(npc.position[0] + 1.0, 0, npc.position[1])
			print("TALK near=", arena.local_player._talk_to_npc_near())
			var door: Dictionary = arena.prop_near(arena.local_player, "exit", "", 999.0)
			arena.local_player.global_position = Vector3(door.position[0], 0, door.position[1] - 1.0)
			print("TALK exit=", door.get("id", "?"), " ", arena.local_player._talk_to_npc_near()))
	if "airskills" in args:  # lança o Mergulho da Águia e a Tempestade de Asas no pátio de treino (a captura sai logo depois)
		get_tree().create_timer(2.5).timeout.connect(func() -> void:
			arena.local_player.facing = Vector2(0, -1)
			arena.skills.cast(arena.local_player, "eagle_dive", 3)
			arena.skills.cast(arena.local_player, "wing_storm", 3))
	if "summongator" in args:  # desperta o Gator Velho (mini-chefe 2) no altar, como se o grupo lesse o Grimório das Brasas
		for prop: Dictionary in arena.arena.props:
			for extra: Dictionary in prop.get("extra_summons", []):
				if String(extra.summon.get("id", "")) == "sw_old_gator":
					var group: Dictionary = extra.summon.duplicate(true)
					group.monsters = group.monsters.filter(func(m: Dictionary) -> bool: return GameData.monsters.has(m.monster))  # monstros ainda não definidos (sewer_gator) ficam de fora da demonstração
					arena.summon_encounter(arena.local_player, {"summon": group})
	if "summon" in args:  # desperta o Rei dos Sapos (mini-chefe 1 do Esgoto) no altar, como se o grupo tivesse o Livro do Altar
		arena._campaign.keys = arena._campaign.get("keys", []) + ["book_frog_altar"]
		for prop: Dictionary in arena.arena.props:
			if prop.get("id", "") == "sewer_frog_altar":
				arena.summon_encounter(arena.local_player, prop)
	if "tripsummon" in args:  # desperta o Empalado, vai a Tortuga e volta; o altar deve poder despertá-lo de novo
		arena._campaign.keys = arena._campaign.get("keys", []) + ["book_frog_altar"]
		var altar: Dictionary = arena.prop_near(arena.local_player, "npc", "sewer_frog_altar", 9999.0)
		arena.local_player.global_position = Vector3(altar.position[0], 0, altar.position[1] + 1.5)
		arena.request_interact(arena.local_player)
		await get_tree().create_timer(5.0).timeout
		Session.ui_open = false
		print("TRIP groups1=", arena._groups.has("sw_frog_king"), " awake=", arena._groups.get("sw_frog_king", {}).get("awake"))
		arena.travel("tortuga", "start", true)
		await get_tree().create_timer(1.0).timeout
		arena.travel("sewers_01_drains", "start")
		await get_tree().create_timer(1.0).timeout
		print("TRIP back has_king=", arena._groups.has("sw_frog_king"), " summoning=", arena._summoning)
		altar = arena.prop_near(arena.local_player, "npc", "sewer_frog_altar", 9999.0)
		print("TRIP altar=", altar.get("id", "NONE"))
		arena.local_player.global_position = Vector3(altar.position[0], 0, altar.position[1] + 1.5)
		arena.request_interact(arena.local_player)
		await get_tree().create_timer(5.0).timeout
		Session.ui_open = false
		print("TRIP marks=", arena.hud.minimap._marks.filter(func(m): return m.kind == "miniboss").size()); print("TRIP groups2=", arena._groups.has("sw_frog_king"), " awake=", arena._groups.get("sw_frog_king", {}).get("awake"))
	if "givekeys" in args:  # entrega as duas chaves do Esgoto (depois de 6 s): o portão do Ninho deve cair
		get_tree().create_timer(6.0).timeout.connect(func() -> void:
			arena.pick_key(arena.local_player, {"id": "k1", "key": "sewer_key_spades"})
			arena.pick_key(arena.local_player, {"id": "k2", "key": "sewer_key_hearts"})
			print("GATE after keys (still closed, the keeper opens it): ", "sewers_01_drains:nest_gate" in arena._campaign.get("opened", []))
			await get_tree().create_timer(1.0).timeout
			var keeper: Dictionary = arena.prop_near(arena.local_player, "npc", "gate_keeper", 999.0)
			arena.local_player.global_position = Vector3(keeper.position[0] - 1.2, 0, keeper.position[1])
			arena.request_interact(arena.local_player)
			await get_tree().create_timer(0.5).timeout
			Session.ui_open = false
			print("GATE after delivering: ", "sewers_01_drains:nest_gate" in arena._campaign.get("opened", [])))
	if kill != "":
		_kill_and_open(arena, kill, open_chest)
	if shot != "":
		await get_tree().create_timer(4.2 if "airskills" in args else 2.72 if "stampede" in args else 3.3 if "mammoth" in args else 2.62 if "rhino" in args else 5.5 if "callskill" in args else 3.6 if "feathers" in args else 7.0 if ("shell" in args or "skillmenu" in args or "cdbar" in args or "feathers" in args or "callskill" in args) else (16.0 if "givekeys" in args else 12.0 if (kill != "" or "summon" in args or "summongator" in args or "invpopup" in args) else 5.0)).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(shot)
		get_tree().quit()


## Chama todos os animais amigos (fênix, lobo, grifo, javali e urso), em leque na frente do Invocador, sem tempo para ir embora.
func _summon_all(arena: Node, only: PackedStringArray) -> void:
	await get_tree().create_timer(2.0).timeout
	var player: Player = arena.local_player
	if player == null:
		push_warning("sandbox: sem jogador local")
		return
	var kinds := {"fox": "fire", "otter": "water", "falcon": "air", "boar": "earth", "bear": "earth"}
	var i := 0
	for kind: String in kinds:
		if not only.is_empty() and kind not in only:
			continue
		var angle := (i - (kinds.size() if only.is_empty() else only.size()) / 2.0 + 0.5) * 0.7
		arena.spawn_companion({
			"owner": player.peer_id, "kind": kind, "element": kinds[kind],
			"position": player.global_position + Vector3(sin(angle), 0, cos(angle)) * 2.5,
			"max_health": 100000.0, "damage_fraction": 1.0, "time": 0.0,
		})
		i += 1


## Mata o monstro (o primeiro com esse id), vai até o baú do mini-chefe e o abre: o loot cai no chão para ver.
func _kill_and_open(arena: Node, monster_id: String, open_chest := true) -> void:
	await get_tree().create_timer(3.0).timeout
	var player: Player = arena.local_player
	for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
		if e.monster_id == monster_id:
			player.teleport_to(e.global_position + Vector3(0, 0.5, 5.0))
			await get_tree().create_timer(0.5).timeout
			e.take_damage(1e9)
			break
	await get_tree().create_timer(3.0).timeout
	if not open_chest:
		var near_chest: Dictionary = arena.prop_near(player, "chest", "", 40.0)
		if not near_chest.is_empty():
			player.teleport_to(Vector3(near_chest.position[0], 0.5, near_chest.position[1] + 1.2))  # em cima do baú, fechado: para ver o aviso de interagir
		return
	var chest: Dictionary = arena.prop_near(player, "chest", "", 40.0)
	if chest.is_empty():
		push_warning("sandbox: sem baú perto")
		return
	player.teleport_to(Vector3(chest.position[0], 0.5, chest.position[1] + 1.2))
	await get_tree().create_timer(0.5).timeout
	arena.request_interact(player)
