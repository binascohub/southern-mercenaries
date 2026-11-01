extends Node3D
func _ready() -> void:
	var out := OS.get_cmdline_user_args()[0]
	var cam := Camera3D.new(); add_child(cam)
	cam.position = Vector3(3.4, 1.8, 4.4); cam.look_at(Vector3(0, 1.1, 0))
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-40, 40, 0); add_child(sun)
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR; env.environment.background_color = Color(0.1, 0.12, 0.15)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; env.environment.ambient_light_color = Color(0.7, 0.7, 0.75)
	add_child(env)
	var m := MonsterModel.new(); add_child(m)
	print("setup ", m.setup("troll", 1.0, Color.WHITE))
	for n in ["idle", "walk", "run", "attack", "hit", "die"]:
		m.play(n, 0.0)
		await get_tree().create_timer(0.7 if n != "die" else 2.0).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, n])
	get_tree().quit()
