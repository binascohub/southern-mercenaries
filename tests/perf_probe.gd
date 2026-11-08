# Southern Mercenaries — GPL-3.0-or-later
extends "res://tests/smoke_arena.gd"
## Sonda de desempenho: abre uma área com o bot do teste de fumaça lutando e anota cada travada
## (quadro acima de SPIKE_MS) com o tempo de script, física e desenho daquele quadro.
##   godot --path . res://tests/perf_probe.tscn -- [area] [segundos] [classe]
## Padrão: forest_01_path, 60 s, mage. No fim imprime o resumo (média, p99, pior quadro, quantas travadas).

const SPIKE_MS := 33.0

var _area := "forest_01_path"
var _seconds := 60.0
var _class := "mage"
var _times: PackedFloat32Array = []
var _spikes: Array[String] = []
var _last_us := 0
var _elapsed := 0.0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		_area = args[0]
	if args.size() > 1:
		_seconds = float(args[1])
	if args.size() > 2:
		_class = args[2]
	SaveSystem.root = "user://test_saves/perf"
	_clean(SaveSystem.root)
	var hero := CharacterData.create(_class, "male", "Bot")
	hero.data.xp = 680
	hero.seal()
	Session.character = hero
	Session.campaign = SaveSystem.new_campaign()
	Session.campaign.area = _area
	NetworkManager.prepare_solo()
	_arena = load("res://game/levels/prototype_arena.tscn").instantiate()
	add_child(_arena)
	_last_us = Time.get_ticks_usec()


func _process(_delta: float) -> void:
	var now := Time.get_ticks_usec()
	var ms := (now - _last_us) / 1000.0
	_last_us = now
	_frame += 1
	if _frame < 20:  # carga da área
		return
	_elapsed += ms / 1000.0
	_times.append(ms)
	if ms > SPIKE_MS:
		_spikes.append("t=%5.1fs %6.1f ms | script %.1f física %.1f | draws %d objetos %d | nós %d inimigos %d | nav %.1f" % [
			_elapsed, ms,
			Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0,
			Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0,
			Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
			Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
			Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
			get_tree().get_nodes_in_group(&"enemies").size(),
			Performance.get_monitor(Performance.TIME_NAVIGATION_PROCESS) * 1000.0])
	if _elapsed >= _seconds:
		_summary()


func _physics_process(_delta: float) -> void:
	var player: Player = _arena.local_player if _arena else null
	for a in [&"aim_left", &"aim_right", &"aim_up", &"aim_down", &"attack",
			&"move_left", &"move_right", &"move_up", &"move_down"]:
		Input.action_release(a)
	if player == null or not is_instance_valid(player):
		return
	InputDevice.using_gamepad = true
	player.health = player.max_health
	var target := _nearest_enemy(player)
	if target == null:
		return
	var offset := Vector2(target.global_position.x - player.global_position.x, target.global_position.z - player.global_position.z)
	var d := offset.normalized()
	_axis(&"aim_left", &"aim_right", d.x)
	_axis(&"aim_up", &"aim_down", d.y)
	if offset.length() <= 9.0:
		if Engine.get_physics_frames() % 12 < 6:
			Input.action_press(&"attack")
	else:
		_axis(&"move_left", &"move_right", d.x)
		_axis(&"move_up", &"move_down", d.y)


func _summary() -> void:
	set_process(false)
	var sorted := _times.duplicate()
	sorted.sort()
	var total := 0.0
	for t in _times:
		total += t
	print("--- %s (%s), %d quadros em %.0f s, GPU: %s" % [_area, _class, _times.size(), _elapsed, RenderingServer.get_video_adapter_name()])
	print("média %.1f ms (%.0f fps) | p50 %.1f | p95 %.1f | p99 %.1f | pior %.1f | travadas >%.0f ms: %d" % [
		total / _times.size(), 1000.0 * _times.size() / total, sorted[sorted.size() / 2], sorted[int(sorted.size() * 0.95)],
		sorted[int(sorted.size() * 0.99)], sorted[-1], SPIKE_MS, _spikes.size()])
	for s in _spikes.slice(0, 60):
		print(s)
	get_tree().quit(0)
