# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Confere a boca do Mímico: godot --path . res://tests/mimic_view.tscn -- <pasta de saída> [idle]; salva três quadros (mv_0..2.png) e sai.


func _ready() -> void:
	var out := OS.get_cmdline_user_args()[0] if OS.get_cmdline_user_args().size() > 0 else "/tmp"
	var m := MonsterModel.new()
	add_child(m)
	m.setup("chest_mimic", 1.0, Color.WHITE)
	m.play("idle" if "idle" in OS.get_cmdline_user_args() else "run", 0.0)
	var cam := Camera3D.new()
	add_child(cam)
	cam.look_at_from_position(Vector3(1.3, 1.1, 1.8), Vector3(0, 0.4, 0))
	var light := DirectionalLight3D.new()
	add_child(light)
	light.rotation_degrees = Vector3(-50, 30, 0)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.6, 0.6, 0.6)
	add_child(env)
	for i in 3:
		await get_tree().create_timer(0.3 if i == 0 else 0.15).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s/mv_%d.png" % [out, i])
	get_tree().quit()
