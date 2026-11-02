# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Galeria das mulheres do jogo, em fila, cada uma com nome: as cortesãs (a Aldeã) e a Reni (modelos próprios), as NPCs de corpo
## feminino (data/npcs.json) e o primeiro visual feminino de cada papel da multidão (data/crowd.json).
##
##   XDG_DATA_HOME=$(mktemp -d) godot --path . res://tools/gallery/women_gallery.tscn
## Controles: W A S D andam, Q / E descem e sobem, Shift acelera; botão direito + arrastar olha; Esc fecha.

const COLUMNS := 7
const CELL := 2.6

var _cam: Camera3D
var _yaw := 0.0
var _pitch := -0.3
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
	sun.rotation_degrees = Vector3(-35, 150, 0)
	add_child(sun)
	var entries: Array = []  # {name, node}
	for role: String in ["courtesan", "courtesan_red", "courtesan_green", "courtesan_black", "courtesan_gold", "courtesan_white", "reni", "woman_dress"]:
		if NpcModel.has_model(role):
			var courtesan := NpcModel.create(role)
			courtesan.call("set_pose", "idle")
			entries.append({"name": role, "node": courtesan})
	for id: String in GameData.npcs:
		var body: Dictionary = GameData.npcs[id].get("body", {}) if GameData.npcs[id] is Dictionary else {}
		if String(body.get("sex", "")) == "female":
			entries.append({"name": "npc: " + id, "node": _hero(body)})
	var roles: Dictionary = GameData.crowd.get("roles", {})
	for role: String in roles:
		var r: Dictionary = roles[role]
		if not "female" in r.get("sex", []):
			continue
		var hairs: Array = r.get("hair", {}).get("female", [[]])
		var styles: Array = r.get("clothes", {}).get("female", [])
		entries.append({"name": "multidão: " + role, "node": _hero({"sex": "female", "hair": hairs[0],
			"hair_color": r.get("hair_color", [[0.2, 0.15, 0.1]])[0], "outfit": r.get("outfit", [{}])[0], "pose": "idle",
			"clothes": NpcModel.clothing_style(styles[0]) if not styles.is_empty() else {}})})
	for i in entries.size():
		var node: Node3D = entries[i].node
		if node == null:
			continue
		var pos := Vector3((i % COLUMNS) * CELL, 0, -(i / COLUMNS) * CELL * 1.6)
		var holder := Node3D.new()
		holder.position = pos
		holder.add_child(node)
		add_child(holder)
		var label := Label3D.new()
		label.text = entries[i].name
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.no_depth_test = true
		label.font_size = 40
		label.outline_size = 10
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.position = pos + Vector3(0, 2.2, 0)
		add_child(label)
	var rows := ceili(entries.size() / float(COLUMNS))
	_cam = Camera3D.new()
	_cam.far = 300.0
	add_child(_cam)
	_cam.global_position = Vector3((minf(entries.size(), COLUMNS) - 1) * CELL / 2.0, 3.0 + rows * 0.7, 6.0 + rows * 1.2)
	_cam.rotation = Vector3(_pitch, 0, 0)
	_cam.make_current()


func _hero(look: Dictionary) -> Node3D:
	var model := HeroModel.new()
	add_child(model)
	remove_child(model)
	model.setup("female", look)
	model.set_outfit(look.get("outfit", {}))
	model.set_pose(String(look.get("pose", "idle")))
	if not look.get("clothes", {}).is_empty():
		Clothing.dress(model, Clothing.HERO_BONES, look.clothes)
	return model


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
	_cam.global_position += (b.x * move.x + Vector3.UP * move.y + b.z * move.z).normalized() * 8.0 * boost * delta
