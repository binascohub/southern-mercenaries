# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Galeria dos passeadores de Tortuga e da Capital, lado a lado, andando no lugar, com o nome de cada um (godot --path . res://tests/npc_gallery.tscn).
## Modo espectador: W/A/S/D (ou setas) andam, E/Espaço sobe, Q/Ctrl desce, Shift acelera; segure o botão direito do mouse e arraste para olhar; a roda muda a velocidade.

const WALKERS: Array = [
	["pirate_2", "Cap. Barnabé"], ["civilian_1", "Baltazar"], ["civilian_2", "Hector"], ["civilian_3", "Otávio"],
	["civilian_5", "Dona Zefa"]]
var _cam: Camera3D
var _yaw := 0.0
var _pitch := 0.0
var _speed := 4.0


func _ready() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.16, 0.15, 0.14)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.75, 0.72, 0.7)
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45, -25, 0)
	add_child(sun)
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(40, 12)
	floor_mesh.mesh = plane
	floor_mesh.position = Vector3(WALKERS.size() * 0.9, -0.01, 0)
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_color = Color(0.33, 0.28, 0.22)
	floor_mesh.material_override = floor_mat
	add_child(floor_mesh)
	var x := 0.0
	for entry: Array in WALKERS:
		var model := NpcModel.create(entry[0])
		var label := Label3D.new()
		label.text = String(entry[1]) if model else "%s (sem modelo)" % entry[1]
		label.font_size = 64
		label.pixel_size = 0.0035
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.no_depth_test = true
		label.position = Vector3(x, 2.15, 0)
		add_child(label)
		if model:
			model.position = Vector3(x, 0, 0)
			add_child(model)
			model.call("set_pose", "walk")
		x += 1.8
	_cam = Camera3D.new()
	_cam.position = Vector3((x - 1.8) / 2.0, 1.3, 4.3)
	_cam.rotation_degrees = Vector3(-6, 0, 0)
	_pitch = deg_to_rad(-6.0)
	_cam.far = 200.0
	add_child(_cam)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("shot="):  # salva uma captura e sai (conferência)
			await get_tree().create_timer(3.0).timeout
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(arg.trim_prefix("shot="))
			get_tree().quit()


func _process(delta: float) -> void:
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
