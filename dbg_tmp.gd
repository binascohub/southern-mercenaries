extends "res://tests/smoke_arena.gd"
var AREA := OS.get_environment("AREA")
var spots: Array = []
func _physics_process(_delta: float) -> void:
	_frame += 1
	var out := OS.get_environment("OUT")
	if spots.is_empty():
		for s in OS.get_environment("SPOTS").split(";"):
			var p := s.split(",")
			spots.append(Vector3(float(p[0]), 0, float(p[1])))
	if _frame == 20: _arena.travel(AREA, "")
	if _frame >= 100 and (_frame - 100) % 50 == 0:
		var n := (_frame - 100) / 50
		if n > 0 and n <= spots.size():
			get_viewport().get_texture().get_image().save_png(out + AREA + "_%d.png" % n)
		if n < spots.size():
			var p: Player = _arena.local_player
			p.global_position = spots[n]; p.velocity = Vector3.ZERO; _arena._camera.snap()
		else:
			get_tree().quit()
func _report(_ok: bool, _d: String) -> void:
	pass
