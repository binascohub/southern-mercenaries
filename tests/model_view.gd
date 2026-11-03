# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Mostra um modelo .glb qualquer (inclusive de fora do projeto) em modo espectador:
## godot --path . res://tests/model_view.tscn -- glb=<arquivo.glb> [shot=<arquivo.png>: salva uma captura e sai]
## W/A/S/D (ou setas) andam, E/Espaço sobe, Q/Ctrl desce, Shift acelera; botão direito + arrastar olha; a roda muda a velocidade.

var _cam: Camera3D
var _yaw := 0.0
var _pitch := 0.0
var _speed := 3.0


func _ready() -> void:
	var path := ""
	var shot := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("glb="):
			path = arg.trim_prefix("glb=")
		elif arg.begins_with("shot="):
			shot = arg.trim_prefix("shot=")
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.2, 0.2, 0.22)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.7, 0.7, 0.7)
	var world := WorldEnvironment.new()
	world.environment = env
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45, 35, 0)
	add_child(sun)
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(12, 12)
	floor_mesh.mesh = plane
	var floor_material := StandardMaterial3D.new()
	floor_material.albedo_color = Color(0.3, 0.3, 0.32)
	floor_mesh.material_override = floor_material
	add_child(floor_mesh)
	var height := 1.8
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	if document.append_from_file(path, state) == OK:
		var model := document.generate_scene(state) as Node3D
		add_child(model)
		for m in model.find_children("*", "MeshInstance3D", true, false):  # peças pintadas por cor de vértice (como a Isabela): mostra a cor
			var mesh_instance := m as MeshInstance3D
			for i in mesh_instance.mesh.get_surface_count():
				var material := mesh_instance.get_active_material(i) as StandardMaterial3D
				if material:
					material = material.duplicate()
					material.vertex_color_use_as_albedo = true
					mesh_instance.set_surface_override_material(i, material)
		var first_box := AABB()
		var seen := false
		for m in model.find_children("*", "MeshInstance3D", true, false):
			var mi0 := m as MeshInstance3D
			first_box = mi0.global_transform * mi0.get_aabb() if not seen else first_box.merge(mi0.global_transform * mi0.get_aabb())
			seen = true
		if first_box.size.z > first_box.size.y * 2.0:  # modelo com o "alto" no eixo Z (Blender): deita para ficar em pé
			model.rotation_degrees.x = -90.0
		var box := AABB()
		var first := true
		for m in model.find_children("*", "MeshInstance3D", true, false):
			var mi := m as MeshInstance3D
			var b := mi.global_transform * mi.get_aabb()
			box = b if first else box.merge(b)
			first = false
		height = maxf(maxf(box.size.x, box.size.y), box.size.z)
		model.position.y -= box.position.y  # a base no chão
		print("modelo: %.2f x %.2f x %.2f m (x, y, z)" % [box.size.x, box.size.y, box.size.z])
	else:
		push_error("não abriu: " + path)
	_cam = Camera3D.new()
	add_child(_cam)
	_cam.look_at_from_position(Vector3(0, height * 0.5, height * 1.6), Vector3(0, height * 0.4, 0))
	_yaw = _cam.rotation.y
	_pitch = _cam.rotation.x
	_speed = maxf(height, 1.0)
	if shot != "":
		await get_tree().create_timer(1.0).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(shot)
		get_tree().quit()


func _process(delta: float) -> void:
	var move := Vector3.ZERO
	move.z = float(Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN)) - float(Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP))
	move.x = float(Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT)) - float(Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT))
	move.y = float(Input.is_key_pressed(KEY_E) or Input.is_key_pressed(KEY_SPACE)) - float(Input.is_key_pressed(KEY_Q) or Input.is_key_pressed(KEY_CTRL))
	_cam.position += _cam.global_transform.basis * move * _speed * (3.0 if Input.is_key_pressed(KEY_SHIFT) else 1.0) * delta


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		_yaw -= event.relative.x * 0.003
		_pitch = clampf(_pitch - event.relative.y * 0.003, -1.5, 1.5)
		_cam.rotation = Vector3(_pitch, _yaw, 0.0)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_speed = minf(_speed * 1.25, 40.0)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_speed = maxf(_speed / 1.25, 0.2)
