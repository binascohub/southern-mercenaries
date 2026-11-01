extends "res://tools/spectator/spectator.gd"
var _n := 0
func _process(delta: float) -> void:
	super._process(delta)
	_n += 1
	if _n == 300:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(OS.get_cmdline_user_args()[-1])
		print("ENEMIES ", get_tree().get_nodes_in_group(&"enemies").size())
		get_tree().quit()
