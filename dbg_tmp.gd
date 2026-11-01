extends Node
var f := 0
func _ready() -> void:
	var e := Environment.new(); e.background_mode = Environment.BG_COLOR; e.background_color = Color(0.25,0.25,0.3); e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; e.ambient_light_color = Color(0.8,0.75,0.7); e.ambient_light_energy = 0.9
	var we := WorldEnvironment.new(); we.environment = e; add_child(we)
	var l := DirectionalLight3D.new(); l.rotation_degrees = Vector3(-35, -20, 0); add_child(l)
	var mats := ["iron", "steel", "copper", "silver", "gold"]
	for i in 5:
		add_child(Player.create({"peer_id": i + 1, "slot": i, "class_id": "knight", "sex": "male", "position": Vector3(0, 0, i * 1.4), "visual": {"weapon": mats[i]}}))
	var c := Camera3D.new(); add_child(c); c.fov = 28; c.look_at_from_position(Vector3(-8.5, 1.5, 2.8), Vector3(0, 0.9, 2.8)); c.current = true
func _process(_d) -> void:
	f += 1
	if f == 40:
		get_viewport().get_texture().get_image().save_png(OS.get_environment("OUT")); get_tree().quit()
