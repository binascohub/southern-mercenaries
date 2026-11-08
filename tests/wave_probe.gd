extends "res://tests/perf_probe.gd"

var _boss: Enemy
var _mon := String(OS.get_cmdline_user_args()[3]) if OS.get_cmdline_user_args().size() > 3 else "leshy"
func _process(delta: float) -> void:
	_frame += 1
	if _frame == 30:
		var p: Player = _arena.local_player
		var before := get_tree().get_nodes_in_group(&"enemies").size()
		_arena.spawn_adds(p.global_position + Vector3(8, 0, 0), _mon, 1, 0.0)
		for n in get_tree().get_nodes_in_group(&"enemies"):
			if n.data.get("name_key","") == GameData.monsters[_mon].name_key:
				_boss = n
		print("spawn: antes %d depois %d boss %s" % [before, get_tree().get_nodes_in_group(&"enemies").size(), _boss])
	if _frame > 30:
		_elapsed += delta
		if _boss and is_instance_valid(_boss):
			_boss.health = _boss.max_health
		if int(_elapsed * 2) != int((_elapsed - delta) * 2):
			print("t=%.0f inimigos %d boss_bar %s estado %s" % [_elapsed, get_tree().get_nodes_in_group(&"enemies").size(), _arena.hud.boss_visible(), ("%s %s %.0f" % [_boss.state, _boss._special, _boss.global_position.distance_to(_arena.local_player.global_position)]) if _boss and is_instance_valid(_boss) else "-"])
		if _elapsed > 20:
			get_tree().quit(0)
func _physics_process(_d: float) -> void:
	var p: Player = _arena.local_player if _arena else null
	if p: p.health = p.max_health
