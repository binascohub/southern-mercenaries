# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Abre a arena com um Invocador de teste: nível máximo, todas as habilidades no rank máximo, nada gravado em disco.
##   godot --path . res://tests/summoner_sandbox.tscn -- [water|air|fire|earth]   (padrão: water) [area=<id>, ex.: area=tavern] [at=x,z, ex.: at=0,-185 para ir a um ponto do mapa] [shot=<arquivo.png>: salva uma captura e sai] [kill=<id do monstro, ex.: old_gator>: mata esse monstro e abre o baú que ele deixa; com "nochest" deixa o baú fechado para ver]; chama todos os animais, ou só os listados depois do elemento (otter = lobo de água, fox, falcon, boar, bear)


func _ready() -> void:
	# Saves isolados: nada daqui entra na lista de personagens nem nas campanhas de verdade.
	SaveSystem.root = "user://test_saves/summoner_sandbox"
	var args: PackedStringArray = []
	var area := ""
	var at := PackedStringArray()
	var shot := ""
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
		else:
			args.append(arg)
	var element: String = args[0] if args.size() > 0 else "water"
	var c := CharacterData.create("summoner", "female", "Teste", element)
	c.data.level = int(GameData.balance.max_level)
	c.data.free_points = 0
	var skills := {}
	var slots: Array = []
	for key in Skills.keys("summoner"):
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
	_summon_all(arena, args.slice(1))
	if kill != "":
		_kill_and_open(arena, kill, open_chest)
	if shot != "":
		await get_tree().create_timer(12.0 if kill != "" else 5.0).timeout
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
		return
	var chest: Dictionary = arena.prop_near(player, "chest", "", 40.0)
	if chest.is_empty():
		push_warning("sandbox: sem baú perto")
		return
	player.teleport_to(Vector3(chest.position[0], 0.5, chest.position[1] + 1.2))
	await get_tree().create_timer(0.5).timeout
	arena.request_interact(player)
