# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Galeria de todas as pessoas (e bichos) de uma área, cada uma com o nome: os NPCs com nome (data/npcs.json e o vendedor das lojas), os papéis da multidão
## (data/crowd.json, um de cada sexo) e os modelos próprios (NpcModel, com o arquivo do modelo).
##
##   XDG_DATA_HOME=$(mktemp -d) godot --path . res://tools/gallery/people_gallery.tscn -- [área]      (padrão: tortuga)
## Controles: W A S D andam, Q / E descem e sobem, Shift acelera; botão direito + arrastar olha; Esc fecha.

const COLUMNS := 8
const CELL := 2.4

var _cam: Camera3D
var _yaw := 0.0
var _pitch := -0.3
var _looking := false


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var area: String = args[0] if args.size() > 0 else "tortuga"
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
	var data: Dictionary = GameData.arenas[area]
	var entries: Array = []  # {name, node, named}
	# NPCs com nome e o vendedor.
	for prop: Dictionary in data.get("props", []):
		if prop.get("kind", "") == "npc":
			var id := String(prop.npc)
			var info: Dictionary = GameData.npcs.get(id, {})
			var title := "%s  (%s)" % [tr(String(info.get("name_key", ""))), id]
			if NpcModel.has_model(id):
				entries.append({"name": title + "\n" + _file(id), "node": _own(id), "named": true})
			elif info.has("body"):
				entries.append({"name": title, "node": _hero(info.body), "named": true})
		elif prop.get("kind", "") == "shop" and prop.get("look", "") == "vendor":
			entries.append({"name": "%s  (vendedor)" % tr(String(prop.get("name_key", ""))), "named": true, "node": _hero({"sex": "male",
				"hair": ["Hair_Buzzed", "Hair_Beard"], "hair_color": [0.08, 0.06, 0.05], "pose": "talk",
				"outfit": {"body": "copper", "feet": "iron", "head": "cloth"}})})
	# Papéis da multidão, na ordem em que aparecem.
	var seen := {}
	var roles: Dictionary = GameData.crowd.get("roles", {})
	for entry: Dictionary in data.get("crowd", []):
		var role := String(entry.role)
		if seen.has(role):
			continue
		seen[role] = true
		if role == "brawl":
			role = "drunk"
			if seen.has("brawl_drunk"):
				continue
			seen["brawl_drunk"] = true
			role = String(entry.get("fighters", ["drunk"])[0])
		if NpcModel.has_model(role):
			entries.append({"name": role + "\n" + _file(role), "node": _own(role), "named": false})
		elif roles.has(role):
			for sex: String in _sexes(roles[role]):
				entries.append({"name": "%s · %s" % [role, "mulher" if sex == "female" else "homem"], "node": _crowd_body(roles[role], sex), "named": false})
	for i in entries.size():
		var node: Node3D = entries[i].node
		if node == null:
			continue
		var pos := Vector3((i % COLUMNS) * CELL, 0, -(i / COLUMNS) * CELL * 1.7)
		var holder := Node3D.new()
		holder.position = pos
		holder.add_child(node)
		add_child(holder)
		var label := Label3D.new()
		label.text = entries[i].name
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.no_depth_test = true
		label.font_size = 36
		label.pixel_size = 0.006
		label.outline_size = 10
		label.modulate = Color(1, 0.95, 0.6) if entries[i].named else Color.WHITE
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.position = pos + Vector3(0, 2.15, 0)
		add_child(label)
	var rows := ceili(entries.size() / float(COLUMNS))
	_cam = Camera3D.new()
	_cam.far = 300.0
	add_child(_cam)
	_cam.global_position = Vector3((minf(entries.size(), COLUMNS) - 1) * CELL / 2.0, 2.6 + rows * 0.5, 4.0 + rows * 0.8)
	_cam.rotation = Vector3(_pitch, 0, 0)
	_cam.make_current()


func _file(id: String) -> String:
	return String(NpcModel.MODELS.get(id, {}).get("scene", "")).get_file()


func _own(id: String) -> Node3D:
	var model := NpcModel.create(id)
	if model:
		model.call("set_pose", "idle")
	return model


func _sexes(role: Dictionary) -> Array:
	var result: Array = []
	for sex: String in role.get("sex", ["male"]):
		if not sex in result:
			result.append(sex)
	return result


func _crowd_body(role: Dictionary, sex: String) -> Node3D:
	var hairs: Array = role.get("hair", {}).get(sex, [[]])
	var styles: Array = role.get("clothes", {}).get(sex, [])
	return _hero({"sex": sex, "hair": hairs[0], "hair_color": role.get("hair_color", [[0.2, 0.15, 0.1]])[0],
		"outfit": role.get("outfit", [{}])[0], "pose": "idle",
		"clothes": NpcModel.clothing_style(styles[0]) if not styles.is_empty() else {}})


func _hero(look: Dictionary) -> Node3D:
	var model := HeroModel.new()
	add_child(model)
	remove_child(model)
	model.setup(String(look.get("sex", "male")), look)
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
