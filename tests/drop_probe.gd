extends "res://tests/perf_probe.gd"
func _process(_delta: float) -> void:
	_frame += 1
	var p: Player = _arena.local_player if _arena else null
	if p == null:
		return
	if _frame == 30:
		var i := p.character.data.inventory.find_custom(func(x: Variant) -> bool: return x != null)
		print("item ", p.character.data.inventory[i].get("id"), " idx ", i)
		p.facing = Vector2(1, 0)
		p._drop_item(i)
		print("bolsa depois: ", p.character.data.inventory[i], " loot no chão: ", _arena._loot.size(), " perto? ", _arena.loot_near(p))
	if _frame == 60:
		for id in _arena._loot:
			p.global_position = _arena._loot[id].position
		print("em cima: perto? ", _arena.loot_near(p))
		Input.action_press(&"attack")
	if _frame == 70:
		Input.action_release(&"attack")
		print("depois do ataque: loot ", _arena._loot.size(), " bolsa itens ", p.character.data.inventory.filter(func(x: Variant) -> bool: return x != null).size())
		get_tree().quit(0)
func _physics_process(_d: float) -> void:
	pass
