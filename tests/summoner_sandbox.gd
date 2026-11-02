# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Abre a arena com um Invocador de teste: nível máximo, todas as habilidades no rank máximo, nada gravado em disco.
##   godot --path . res://tests/summoner_sandbox.tscn -- [water|air|fire|earth]   (padrão: water) [area=<id>, ex.: area=tavern]; chama todos os animais, ou só os listados depois do elemento (otter = lobo de água, fox, falcon, boar, bear)


func _ready() -> void:
	# Saves isolados: nada daqui entra na lista de personagens nem nas campanhas de verdade.
	SaveSystem.root = "user://test_saves/summoner_sandbox"
	var args: PackedStringArray = []
	var area := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("area="):
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
	_summon_all(arena, args.slice(1))


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
