extends Node
func _ready() -> void:
	Session.campaign = SaveSystem.new_campaign()
	Session.campaign["area"] = "tavern"
	Session.campaign["checkpoint"] = "start"
	var arena = load("res://game/levels/prototype_arena.tscn").instantiate()
	add_child(arena)
	for i in 6:
		await get_tree().process_frame
	var player: Player = arena.local_player
	var town = arena.town
	var kp := arena._props.filter(func(p): return p.get("npc", "") == "tavern_keeper")
	player.global_position = Vector3(kp[0].position[0], 0, kp[0].position[1] + 1)
	town._rpc_accept("forest_treasure")
	print("ACCEPT_NO_SEWER ", arena._campaign.quests.get("forest_treasure", ""), arena._campaign.get("unlocked", []))
	arena._campaign.quests["sewer_treasure"] = "done"
	town.quests = arena._campaign.quests
	town._rpc_accept("forest_treasure")
	print("ACCEPT ", arena._campaign.quests.get("forest_treasure", ""), " unlocked ", arena._campaign.get("unlocked", []))
	town._rpc_service("tavern_keeper", "rest_turn_in")
	print("REST_NO_BAG ", arena._campaign.quests.get("forest_treasure", ""))
	player.character.add_item(Items.stack(Items.VALUABLE, "travelers_bag"))
	var gold_before := int(player.character.data.gold)
	town._rpc_service("tavern_keeper", "rest_turn_in")
	print("TURN_IN ", arena._campaign.quests.get("forest_treasure", ""), " gold +", int(player.character.data.gold) - gold_before, " bag ", player.character.count_of("travelers_bag"))
	get_tree().quit()
