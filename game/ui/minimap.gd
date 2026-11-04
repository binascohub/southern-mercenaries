# Southern Mercenaries — GPL-3.0-or-later
class_name Minimap
extends Control
## Minimapa (09-interface.md, seção 3): a área atual vista de cima, só com o que já foi
## explorado (o resto fica em branco, sem a sombra da planta); o herói deste PC (dourado), os aliados
## (azul), as saídas e os lugares de missão já vistos. Nas cidades não há névoa.
## A ação `map` alterna para o mapa grande, no meio da tela. Desenhado com
## _draw() (sem câmera extra), redesenhado poucas vezes por segundo.

const SMALL := Vector2(190, 190)
const LARGE := Vector2(560, 560)
const FLOOR_COLOR := Color(0.55, 0.5, 0.42, 0.9)
const REDRAW := 0.2

var large := false
var _area: Dictionary = {}
var _mask := PackedByteArray()
var _ground := PackedByteArray()
var _bounds := Rect2()
var _grid := Vector2i.ZERO
var _town := false
## {position: Vector2 (x, z), local: bool}
var _heroes: Array[Dictionary] = []
## Marcas: {position: Vector2, kind: "exit" | "quest" | "altar" | "miniboss" | "teleporter" | "questgiver"}
var _marks: Array[Dictionary] = []
var _timer := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_apply_size()


func set_area(area: Dictionary, mask: PackedByteArray) -> void:
	_area = area
	_town = area.get("town", false)
	_bounds = ExploreMap.bounds(area)
	_grid = ExploreMap.grid_size(area)
	_ground = ExploreMap.floor_cells(area)
	_mask = mask
	queue_redraw()


func reveal(cells: PackedInt32Array) -> void:
	for index in cells:
		if index >= 0 and index < _mask.size():
			_mask[index] = 1
	queue_redraw()


func is_seen(at: Vector2) -> bool:
	return _town or ExploreMap.is_seen(_mask, _area, at)


func set_markers(heroes: Array[Dictionary], marks: Array[Dictionary]) -> void:
	_heroes = heroes
	_marks = marks


func toggle_large() -> void:
	large = not large
	_apply_size()


func _apply_size() -> void:
	var size_ := LARGE if large else SMALL
	if large:
		set_anchors_preset(Control.PRESET_CENTER)
		offset_left = -size_.x / 2.0
		offset_right = size_.x / 2.0
		offset_top = -size_.y / 2.0
		offset_bottom = size_.y / 2.0
	else:
		set_anchors_preset(Control.PRESET_TOP_RIGHT)
		offset_left = -size_.x - 24
		offset_right = -24
		offset_top = 16
		offset_bottom = 16 + size_.y
	queue_redraw()


func _process(delta: float) -> void:
	_timer -= delta
	if _timer <= 0.0:
		_timer = REDRAW
		queue_redraw()


## Ponto do mundo (x, z) dentro do retângulo do mapa (mantém a proporção).
func _to_map(at: Vector2) -> Vector2:
	var box := size
	var scale_ := minf(box.x / maxf(_bounds.size.x, 1.0), box.y / maxf(_bounds.size.y, 1.0))
	var offset := (box - _bounds.size * scale_) / 2.0
	return offset + (at - _bounds.position) * scale_


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.08, 0.07, 0.06, 0.7))
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.45, 0.33, 0.2), false, 2.0)
	if _area.is_empty():
		return
	var cell := _to_map(_bounds.position + Vector2.ONE * ExploreMap.CELL) - _to_map(_bounds.position)
	for y in _grid.y:
		for x in _grid.x:
			var index := y * _grid.x + x
			if index >= _ground.size() or _ground[index] == 0:
				continue
			var at := _to_map(_bounds.position + Vector2(x, y) * ExploreMap.CELL)
			var seen := _town or (index < _mask.size() and _mask[index] != 0)
			if not seen:
				continue  # o que ainda não foi explorado não aparece, nem como sombra do mapa
			draw_rect(Rect2(at, cell + Vector2(0.5, 0.5)), FLOOR_COLOR)
	for mark in _marks:
		if mark.kind == "miniboss":
			continue  # desenhado por último, por cima dos heróis
		if not is_seen(mark.position):
			continue
		var p := _to_map(mark.position)
		if mark.kind == "altar":  # losango roxo pequeno
			draw_colored_polygon(PackedVector2Array([p + Vector2(0, -4.5), p + Vector2(4, 0), p + Vector2(0, 4.5), p + Vector2(-4, 0)]), Color(0.75, 0.4, 1.0))
			continue
		if mark.kind == "questgiver":  # ponto laranja
			draw_circle(p, 4.0, Color(1.0, 0.55, 0.05))
			continue
		if mark.kind == "teleporter":  # círculo roxo com contorno claro
			draw_circle(p, 5.5, Color(0.95, 0.88, 1.0))
			draw_circle(p, 4.2, Color(0.6, 0.2, 0.95))
			continue
		var color := Color(0.4, 0.85, 1.0) if mark.kind == "exit" else Color(1.0, 0.85, 0.3)
		draw_rect(Rect2(p - Vector2(3, 3), Vector2(6, 6)), color)
	for hero in _heroes:
		var p := _to_map(hero.position)
		draw_circle(p, 5.0 if hero.local else 4.0, Color(1.0, 0.8, 0.25) if hero.local else Color(0.35, 0.6, 1.0))
	for mark in _marks:
		if mark.kind == "miniboss":
			var p := _to_map(mark.position)
			draw_circle(p, 6.5, Color(1.0, 1.0, 1.0))
			draw_circle(p, 5.0, Color(0.95, 0.05, 0.05))
