# Southern Mercenaries — GPL-3.0-or-later
extends "res://tests/smoke_arena.gd"
## Roda o bot do teste de fumaça e salva uma captura de tela da arena.
##   godot --path . res://tests/screenshot.tscn -- <saída.png> [frames] [host N | join IP]

var _out := "user://screenshot.png"
var _at_frame := 420


func _args() -> PackedStringArray:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		_out = args[0]
	if args.size() > 1:
		_at_frame = int(args[1])
	return args.slice(2)


func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	if _frame == _at_frame:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(_out)
		print("captura salva em ", _out)
		NetworkManager.leave()
		get_tree().quit()


func _report(_ok: bool, _detail: String) -> void:
	pass
