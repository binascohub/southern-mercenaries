# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Teste de fumaça: abre a arena e joga sozinho com "controle" simulado,
## mirando no inimigo mais próximo e atirando. Passa se inimigos nascerem e
## morrerem até a vitória (todas as ondas).
##   godot --headless --path . --fixed-fps 60 res://tests/smoke_arena.tscn

const MAX_FRAMES := 60 * 90

var _arena: Node
var _frame := 0
var _kills := 0
var _max_wave := 0


func _ready() -> void:
	_arena = load("res://game/levels/prototype_arena.tscn").instantiate()
	add_child(_arena)


func _physics_process(_delta: float) -> void:
	_frame += 1
	InputDevice.using_gamepad = true
	var player: Player = _arena.player
	player.health = player.max_health  # o teste avalia o combate, não a esquiva do bot
	_max_wave = maxi(_max_wave, _arena.wave)
	var target := _nearest_enemy(player)
	for a in [&"aim_left", &"aim_right", &"aim_up", &"aim_down", &"attack"]:
		Input.action_release(a)
	if target:
		var d := Vector2(target.global_position.x - player.global_position.x,
			target.global_position.z - player.global_position.z).normalized()
		_axis(&"aim_left", &"aim_right", d.x)
		_axis(&"aim_up", &"aim_down", d.y)
		if _frame % 12 < 6:
			Input.action_press(&"attack")
	if _arena.finished or _frame > MAX_FRAMES:
		_finish()


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


func _finish() -> void:
	var ok: bool = _arena.finished and _arena.enemies_alive == 0
	print("frames=%d onda=%d inimigos_vivos=%d vitória=%s" % [_frame, _arena.wave, _arena.enemies_alive, _arena.finished])
	if ok:
		print("OK: as %d ondas foram vencidas" % _arena.arena.waves.size())
	else:
		printerr("FALHOU: a arena não foi vencida a tempo")
	get_tree().quit(0 if ok else 1)
