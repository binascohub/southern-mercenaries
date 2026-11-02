extends Node
func _ready() -> void:
	var vp := SubViewport.new()
	vp.size = Vector2i(900, 600)
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.25, 0.27, 0.3)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.7, 0.7, 0.75)
	vp.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, 20, 0)
	vp.add_child(sun)
	var hero := HeroModel.new()
	vp.add_child(hero)
	hero.setup("female", {"hair": ["Hair_Long"], "hair_color": [0.5, 0.25, 0.1]}, "summoner")
	hero.show_wings(1.6)
	var cam := Camera3D.new()
	vp.add_child(cam)
	var pos := Vector3(float(OS.get_environment("CX")), float(OS.get_environment("CY")), float(OS.get_environment("CZ")))
	cam.look_at_from_position(pos, Vector3(0, 1.1, 0))
	await get_tree().create_timer(float(OS.get_environment("T"))).timeout
	for i in 3: await get_tree().process_frame
	vp.get_texture().get_image().save_png(OS.get_environment("OUT"))
	get_tree().quit()
