# Southern Mercenaries — GPL-3.0-or-later
class_name OrnamentDivider
extends Control
## Divisor de livro antigo: fios de latão que somem nas pontas e um losango de ouro com
## duas contas no meio. Separa os grupos do menu e fica sob os títulos das janelas.

const BRASS := Color(0.55, 0.43, 0.2)
const GOLD := Color(0.85, 0.69, 0.32)

var tint := Color.WHITE


func _init() -> void:
	custom_minimum_size = Vector2(0, 22)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _draw() -> void:
	var middle := Vector2(size.x * 0.5, size.y * 0.5)
	var reach := size.x * 0.5 - 20.0
	var segments := 14
	for side in [-1.0, 1.0]:
		for i in segments:
			var t0 := float(i) / segments
			var t1 := float(i + 1) / segments
			var alpha := (1.0 - t0) * 0.9
			draw_line(middle + Vector2(side * (14.0 + reach * t0), 0), middle + Vector2(side * (14.0 + reach * t1), 0), Color(BRASS.r, BRASS.g, BRASS.b, alpha) * tint, 1.6)
			draw_line(middle + Vector2(side * (14.0 + reach * t0), 4.0), middle + Vector2(side * (14.0 + reach * t1 * 0.8), 4.0), Color(BRASS.r, BRASS.g, BRASS.b, alpha * 0.45) * tint, 1.0)
		draw_circle(middle + Vector2(side * 22.0, 0), 2.0, GOLD * tint)
	var diamond := PackedVector2Array([middle + Vector2(0, -7), middle + Vector2(7, 0), middle + Vector2(0, 7), middle + Vector2(-7, 0)])
	draw_colored_polygon(diamond, GOLD * tint)
	draw_polyline(PackedVector2Array([diamond[0], diamond[1], diamond[2], diamond[3], diamond[0]]), Color(0.3, 0.2, 0.06), 1.2, true)
	draw_circle(middle, 2.2, Color(0.55, 0.1, 0.08))
