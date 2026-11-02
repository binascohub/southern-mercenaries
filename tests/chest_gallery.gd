# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Galeria dos baús que existem nos assets, lado a lado, com o nome de cada um (godot --path . res://tests/chest_gallery.tscn).
## Modo espectador: W/A/S/D (ou setas) andam, E/Espaço sobe, Q/Ctrl desce, Shift acelera; segure o botão direito do mouse e arraste para olhar; a roda muda a velocidade.

const DEFAULT_PIECES: Array[String] = ["Chest_Mini", "Chest_Small", "Chest_Medium", "Chest_Large", "Chest_Epic", "Ancient_Treasure"]
var _cam: Camera3D
var _row_end := 0.0
var _yaw := 0.0
var _pitch := 0.0
var _speed := 4.0


func _ready() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.12, 0.11, 0.1)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.7, 0.68, 0.65)
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -30, 0)
	add_child(sun)
	var pieces: Array[String] = DEFAULT_PIECES.duplicate()
	var upright := false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("pieces="):
			pieces.assign(arg.trim_prefix("pieces=").split(","))
		elif arg == "upright":
			upright = true  # frascos em pé (os modelos vêm deitados)
	var x := 0.0
	for name in pieces:
		var node := Kit.piece(name)
		var label := Label3D.new()
		label.text = name if node else name + " (não existe)"
		label.font_size = 64
		label.pixel_size = 0.004
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		if node:
			var raw := _bounds(node)
			var factor := 1.3 if name != "Ancient_Treasure" else 1.0  # como no jogo (CHEST_SCALE)
			var width := maxf(raw.size.x, raw.size.z) * factor
			var height := raw.size.y * factor
			var foot := -raw.position.y * factor
			if upright:
				# Frascos: o comprimento vem ao longo de z; giram para ficar em pé.
				factor = 1.0
				node.rotation.x = -PI / 2.0
				width = maxf(raw.size.x, raw.size.y) * factor
				height = raw.size.z * factor
				foot = -raw.position.z * factor
			node.scale = Vector3.ONE * factor
			node.position = Vector3(x + width / 2.0, foot, 0)
			add_child(node)
			label.position = Vector3(x + width / 2.0, height + 0.6, 0)
			x += width + 1.0
		else:
			continue
		add_child(label)
	_row_end = x
	# Modo espectador: câmera livre, começa de frente para a fila toda.
	_cam = Camera3D.new()
	_cam.position = Vector3(x / 2.0, 2.2, maxf(8.0, x * 0.55))
	if "near" in OS.get_cmdline_user_args():  # peças pequenas (itens de missão): a câmera começa perto
		_cam.position = Vector3(x / 2.0, 0.9, maxf(1.8, x * 0.4))
	_cam.rotation_degrees = Vector3(-12, 0, 0)
	_cam.far = 200.0
	add_child(_cam)
	_yaw = 0.0
	_pitch = deg_to_rad(-12.0)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("shot="):  # salva uma captura e sai (conferência)
			await get_tree().create_timer(3.0).timeout
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(arg.trim_prefix("shot="))
			get_tree().quit()


func _bounds(node: Node3D) -> AABB:
	var total := AABB()
	var first := true
	for m in node.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var b := mi.global_transform * mi.get_aabb() if mi.is_inside_tree() else (node.transform * mi.transform) * mi.get_aabb()
		total = b if first else total.merge(b)
		first = false
	return total


func _process(delta: float) -> void:
	if _cam == null:
		return
	var move := Vector3.ZERO
	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
		move.z -= 1.0
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
		move.z += 1.0
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
		move.x -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
		move.x += 1.0
	if Input.is_key_pressed(KEY_E) or Input.is_key_pressed(KEY_SPACE):
		move.y += 1.0
	if Input.is_key_pressed(KEY_Q) or Input.is_key_pressed(KEY_CTRL):
		move.y -= 1.0
	var speed := _speed * (3.0 if Input.is_key_pressed(KEY_SHIFT) else 1.0)
	_cam.position += _cam.global_transform.basis * move * speed * delta


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		_yaw -= event.relative.x * 0.003
		_pitch = clampf(_pitch - event.relative.y * 0.003, -1.5, 1.5)
		_cam.rotation = Vector3(_pitch, _yaw, 0.0)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_speed = minf(_speed * 1.25, 40.0)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_speed = maxf(_speed / 1.25, 0.5)
