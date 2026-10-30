# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Sala de testes da Fase 1: um porão fechado com pilares e ondas de ratos.
## A geometria é gerada aqui como placeholder até os mapas feitos à mão.

const ARENA_ID := "prototype_arena"
const ROOM_HALF := 14.0
const WALL_HEIGHT := 2.5
const PILLARS: Array[Vector2] = [Vector2(-6, -5), Vector2(6, -5), Vector2(-6, 5), Vector2(6, 5)]
const SPAWNS: Array[Vector2] = [
	Vector2(-12, -12), Vector2(0, -12.5), Vector2(12, -12),
	Vector2(-12.5, 0), Vector2(12.5, 0),
	Vector2(-12, 12), Vector2(0, 12.5), Vector2(12, 12),
]
const SPAWN_INTERVAL := 0.35
const WAVE_DELAY := 2.0

var arena: Dictionary
var player: Player
var wave := 0
var enemies_alive := 0
var finished := false

@onready var hud: Hud = $Hud
@onready var pause_menu: PauseMenu = $PauseMenu


func _ready() -> void:
	arena = GameData.get_arena(ARENA_ID)
	_build_environment()
	_build_room()
	_spawn_player()
	hud.bind_player(player)
	hud.set_wave(0, arena.waves.size(), 0)
	InputDevice.gamepad_lost.connect(_on_gamepad_lost)
	InputDevice.gamepad_restored.connect(_on_gamepad_restored)
	get_tree().create_timer(1.0).timeout.connect(_next_wave)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"menu") and not get_tree().paused:
		pause_menu.open()
		get_viewport().set_input_as_handled()
	elif finished and event.is_action_pressed(&"attack"):
		get_tree().reload_current_scene()


func _next_wave() -> void:
	if finished:
		return
	if wave >= arena.waves.size():
		finished = true
		hud.show_victory()
		return
	var groups: Array = arena.waves[wave]
	wave += 1
	var queue: Array[String] = []
	for group in groups:
		for i in int(group.count):
			queue.append(group.monster)
	queue.shuffle()
	enemies_alive += queue.size()
	hud.set_wave(wave, arena.waves.size(), enemies_alive)
	for i in queue.size():
		get_tree().create_timer(i * SPAWN_INTERVAL, false).timeout.connect(_spawn_enemy.bind(queue[i], i))


func _spawn_enemy(monster_id: String, index: int) -> void:
	if finished:
		return
	var enemy := Enemy.new()
	enemy.monster_id = monster_id
	var spot := SPAWNS[(index + wave * 3) % SPAWNS.size()]
	enemy.position = Vector3(spot.x + randf_range(-1, 1), 0, spot.y + randf_range(-1, 1))
	add_child(enemy)
	enemy.died.connect(_on_enemy_died)


func _on_enemy_died(_enemy: Enemy) -> void:
	enemies_alive -= 1
	hud.set_wave(wave, arena.waves.size(), enemies_alive)
	if enemies_alive <= 0:
		get_tree().create_timer(WAVE_DELAY, false).timeout.connect(_next_wave)


func _on_player_died() -> void:
	finished = true
	hud.show_defeat()


func _on_gamepad_lost() -> void:
	# Solo: pausa até reconectar (08-controles.md, seção 1).
	hud.show_gamepad_lost(true)
	get_tree().paused = true


func _on_gamepad_restored() -> void:
	if hud.is_gamepad_lost_visible():
		hud.show_gamepad_lost(false)
		if not pause_menu.is_open:
			get_tree().paused = false


func _spawn_player() -> void:
	player = Player.new()
	player.class_id = arena.player_class
	add_child(player)
	player.died.connect(_on_player_died)
	var camera := TopDownCamera.new()
	add_child(camera)
	camera.target = player
	camera.snap()


func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.03, 0.03, 0.05)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.35, 0.38, 0.5)
	env.ambient_light_energy = 0.6
	env.fog_enabled = true
	env.fog_light_color = Color(0.06, 0.06, 0.09)
	env.fog_density = 0.02
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	add_child(world_env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-60, 30, 0)
	sun.light_energy = 0.8
	sun.light_color = Color(0.85, 0.8, 0.75)
	sun.shadow_enabled = true
	add_child(sun)

	# Uma única luz pontual quente (tocha) — poucas luzes dinâmicas.
	var torch := OmniLight3D.new()
	torch.position = Vector3(0, 3, 0)
	torch.omni_range = 12.0
	torch.light_color = Color(1.0, 0.6, 0.3)
	torch.light_energy = 1.2
	add_child(torch)


func _build_room() -> void:
	var size := ROOM_HALF * 2.0
	_box(Vector3(0, -0.5, 0), Vector3(size + 2, 1, size + 2), Color(0.18, 0.17, 0.16))
	var wall_color := Color(0.28, 0.25, 0.23)
	var h := WALL_HEIGHT
	_box(Vector3(0, h / 2, -ROOM_HALF - 0.5), Vector3(size + 2, h, 1), wall_color)
	_box(Vector3(0, h / 2, ROOM_HALF + 0.5), Vector3(size + 2, h, 1), wall_color)
	_box(Vector3(-ROOM_HALF - 0.5, h / 2, 0), Vector3(1, h, size), wall_color)
	_box(Vector3(ROOM_HALF + 0.5, h / 2, 0), Vector3(1, h, size), wall_color)
	for p in PILLARS:
		_box(Vector3(p.x, h / 2, p.y), Vector3(1.4, h, 1.4), wall_color)


func _box(center: Vector3, box_size: Vector3, color: Color) -> void:
	var body := StaticBody3D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = box_size
	shape.shape = box
	body.add_child(shape)
	var mesh := MeshInstance3D.new()
	var box_mesh := BoxMesh.new()
	box_mesh.size = box_size
	mesh.mesh = box_mesh
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	mesh.material_override = material
	body.add_child(mesh)
	add_child(body)
	body.position = center
