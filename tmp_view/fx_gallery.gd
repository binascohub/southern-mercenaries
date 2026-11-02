extends Node
## Galeria temporária dos efeitos de magia (apague tmp_view depois): FX_IDS=a,b,c FX_OUT=/caminho/prefixo
var cam: Camera3D
func _ready() -> void:
	var ids := OS.get_environment("FX_IDS").split(",")
	var out := OS.get_environment("FX_OUT")
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.06, 0.07, 0.09)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.45, 0.48, 0.55)
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, 25, 0)
	sun.light_energy = 0.7
	add_child(sun)
	var cols := 2
	var rows := ceili(ids.size() / float(cols))
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(cols * 12.0 + 6, rows * 11.0 + 6)
	floor_mesh.mesh = plane
	var fm := StandardMaterial3D.new()
	fm.albedo_color = Color(0.2, 0.22, 0.2)
	floor_mesh.material_override = fm
	floor_mesh.position = Vector3(cols * 6.0, 0, rows * 5.5)
	add_child(floor_mesh)
	var holder := Node3D.new()
	add_child(holder)
	for i in ids.size():
		var id := String(ids[i])
		var base := Vector3((i % cols) * 12.0, 0, (i / cols) * 11.0)
		var label := Label3D.new()
		label.text = id
		label.position = base + Vector3(3, 0.2, 4.6)
		label.rotation_degrees.x = -60
		label.font_size = 96
		label.pixel_size = 0.012
		add_child(label)
		_run(holder, id, base)
	cam = Camera3D.new()
	add_child(cam)
	cam.fov = 50
	var center := Vector3(cols * 6.0 - 3.0, 0, rows * 5.5 - 2.0)
	cam.look_at_from_position(center + Vector3(0, 17.0 + rows * 3.0, 11.0 + rows * 3.0), center)
	get_window().size = Vector2i(1600, 1000)
	for t in [0.3, 0.9]:
		await get_tree().create_timer(t if t == 0.3 else 0.6).timeout
		for i in 4: await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png("%s_%d.png" % [out, int(t * 10)])
	get_tree().quit()
func _run(holder: Node, id: String, base: Vector3) -> void:
	var color := Color(1, 0.5, 0.2)
	var p0 := base + Vector3(0, 0, 0)
	SpellFx.play(holder, "cast", id, p0, Vector3.FORWARD, 1.0, color, 0.4)
	var node := Node3D.new()
	holder.add_child(node)
	node.global_position = p0 + Vector3(0, 1.0, 0)
	if SpellFx.projectile(node, id, Vector3.RIGHT, 0.3, color):
		var tw := node.create_tween()
		tw.tween_property(node, "global_position", p0 + Vector3(7, 1.0, 0), 1.2)
	else:
		node.queue_free()
	SpellFx.play(holder, "beam", id, p0 + Vector3(0, 1.0, 2.5), p0 + Vector3(7, 0.6, 2.5), 0.5, color, 1.0)
	SpellFx.play(holder, "disc", id, p0 + Vector3(3.5, 0, -3), Vector3.RIGHT * 6.0, 2.6, color, 1.5)
	SpellFx.play(holder, "warn", id, p0 + Vector3(3.5, 0, -3), Vector3.ZERO, 2.6, color, 1.0)
	SpellFx.play(holder, "hit", id, p0 + Vector3(7.0, 0, -3), Vector3.ZERO, 2.6, color, 0.5)
