# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Galeria de monstros: todos os monstros de data/monsters.json em grade, cada um com nome e id.
##
##   XDG_DATA_HOME=$(mktemp -d) godot --path . res://tools/gallery/monster_gallery.tscn
## Controles: W A S D andam, Q / E descem e sobem, Shift acelera; botão direito + arrastar olha; Esc fecha.

const COLUMNS := 8
const CELL := 14.0

var _cam: Camera3D
var _yaw := 0.0
var _pitch := -0.6
var _looking := false


func _ready() -> void:
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.18, 0.2, 0.24)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.8, 0.8, 0.85)
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, 30, 0)
	add_child(sun)
	var ids: Array = GameData.monsters.keys()
	var rows := ceili(ids.size() / float(COLUMNS))
	for i in ids.size():
		var id: String = ids[i]
		var pos := Vector3((i % COLUMNS) * CELL, 0, (i / COLUMNS) * CELL)
		var enemy := Enemy.create({"monster_id": id, "position": pos, "yaw": PI})
		add_child(enemy)
		var d: Dictionary = GameData.monsters[id]
		var label := Label3D.new()
		label.text = "%s\n%s · %s" % [TranslationServer.translate(d.get("name_key", id)), id, d.get("category", "")]
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.no_depth_test = true
		label.font_size = 48
		label.outline_size = 12
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.position = pos + Vector3(0, 5.5 * float(d.get("size", 1.0)) / 2.0 + 1.5, 0)
		add_child(label)
	_cam = Camera3D.new()
	_cam.far = 600.0
	add_child(_cam)
	_cam.global_position = Vector3((COLUMNS - 1) * CELL / 2.0, 40, rows * CELL + 20)
	_cam.rotation = Vector3(_pitch, 0, 0)
	_cam.make_current()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_RIGHT:
		_looking = (event as InputEventMouseButton).pressed
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if _looking else Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseMotion and _looking:
		var m := event as InputEventMouseMotion
		_yaw -= m.relative.x * 0.004
		_pitch = clampf(_pitch - m.relative.y * 0.004, -1.5, 1.5)
		_cam.rotation = Vector3(_pitch, _yaw, 0)
	elif event is InputEventKey and (event as InputEventKey).pressed and (event as InputEventKey).keycode == KEY_ESCAPE:
		get_tree().quit()


func _process(delta: float) -> void:
	var move := Vector3.ZERO
	move.z = float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W))
	move.x = float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A))
	move.y = float(Input.is_physical_key_pressed(KEY_E)) - float(Input.is_physical_key_pressed(KEY_Q))
	if move == Vector3.ZERO:
		return
	var b := _cam.global_transform.basis
	var boost := 3.0 if Input.is_physical_key_pressed(KEY_SHIFT) else 1.0
	_cam.global_position += (b.x * move.x + Vector3.UP * move.y + b.z * move.z).normalized() * 20.0 * boost * delta
