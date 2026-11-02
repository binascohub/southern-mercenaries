extends "res://tools/spectator/spectator.gd"
var out := ""
func _ready() -> void:
	out = OS.get_environment("OUT")
	await super._ready()
	_cam.fov = 60.0
	_cam.global_position = Vector3(0, 70, -80.0)
	_cam.rotation_degrees = Vector3(-90, 0, 0)
	await get_tree().create_timer(1.0).timeout
	await _snap("g_alto70")
	get_tree().quit()
func _snap(name: String) -> void:
	for i in 4: await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, name])
