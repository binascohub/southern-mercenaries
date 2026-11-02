# Southern Mercenaries — GPL-3.0-or-later
class_name QuestTrail
extends Node3D
## Pegadas até o objetivo da missão ativa (Opções → Jogabilidade → "Pegadas da missão", ligada por padrão).
## Quando há uma missão ativa nesta área, desenha no chão, à frente do herói, as marcas de passos que levam ao objetivo mais perto:
##   - missões "clear": os bichos vivos dos grupos pedidos (o mini-chefe); se ele ainda não foi invocado, o objeto que o invoca (o altar);
##   - missões de item: quem larga o item (monstros com "quest_drop");
##   - as outras missões da área: o chefe vivo (a vitória do mapa).
## O caminho passa pelas salas e portas da área (grade de 1 m: chão das salas, vãos das portas, sem as caixas de colisão dos objetos "solid") com A*,
## é endireitado (nada de zigue-zague em sala aberta) e vira passos alternados esquerdo/direito; só os próximos ~40 m aparecem, esmaecendo com a distância.
## As funções estáticas (grade, caminho, objetivos, passos) não dependem de nós: os testes as usam.

const CELL := 1.0
const WALL_MARGIN := 0.7  # sobra junto das paredes (elas têm 1 m de espessura)
const DOOR_WIDTH := 6.0  # o mesmo vão de prototype_arena.gd
const STEP := 1.25
const MAX_STEPS := 34
const LEAD := 1.8  # os primeiros passos começam um pouco à frente do herói
const END_GAP := 3.0  # os passos param antes do objetivo
const UPDATE_EVERY := 0.4
const FOOT_COLOR := Color(1.0, 0.86, 0.5)
const FOOT_HEIGHT := 0.05

var _level: Node3D  # a arena (prototype_arena.gd)
var _multi: MultiMeshInstance3D
var _map: Dictionary = {}
var _map_area := ""
var _timer := 0.0
var _last_from := Vector2(1e9, 1e9)
var _last_target := Vector2(1e9, 1e9)


func setup(level: Node3D) -> void:
	_level = level


func _ready() -> void:
	name = "QuestTrail"
	var mesh := PlaneMesh.new()
	mesh.size = Vector2(0.38, 0.7)
	var multi := MultiMesh.new()
	multi.transform_format = MultiMesh.TRANSFORM_3D
	multi.use_colors = true
	multi.mesh = mesh
	multi.instance_count = MAX_STEPS
	multi.visible_instance_count = 0
	_multi = MultiMeshInstance3D.new()
	_multi.multimesh = multi
	_multi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.vertex_color_use_as_albedo = true
	material.albedo_texture = footprint_texture()
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.no_depth_test = false
	_multi.material_override = material
	add_child(_multi)
	Settings.changed.connect(_on_settings_changed)


func _on_settings_changed() -> void:
	if not Settings.quest_trail:
		_multi.multimesh.visible_instance_count = 0
		_last_from = Vector2(1e9, 1e9)


func _process(delta: float) -> void:
	_timer -= delta
	if _timer > 0.0:
		return
	_timer = UPDATE_EVERY
	if not Settings.quest_trail or _level == null:
		_multi.multimesh.visible_instance_count = 0
		return
	var player: Node3D = _level.get("local_player")
	var area_id: String = String(_level.get("area_id"))
	var area: Dictionary = _level.get("arena")
	if player == null or area.is_empty() or _level.town == null:
		_multi.multimesh.visible_instance_count = 0
		return
	var living: Array = []
	for node in get_tree().get_nodes_in_group(&"enemies"):
		var e := node as Enemy
		if e == null or e.is_queued_for_deletion() or e.health <= 0.0 or e.data.get("breakable", false) or e.data.get("dummy", false):
			continue
		living.append({"group": e.group, "monster_id": e.monster_id, "position": Vector2(e.global_position.x, e.global_position.z)})
	# Grupo que ainda vai ser invocado (altar): o objetivo é o altar até ele surgir.
	for prop: Dictionary in area.get("props", []):
		if prop.has("summon") and not living.any(func(l: Dictionary) -> bool: return l.group == prop.summon.id):
			living.append({"group": prop.summon.id, "monster_id": String(prop.summon.monsters[0].monster), "position": Vector2(prop.position[0], prop.position[1])})
	var from := Vector2(player.global_position.x, player.global_position.z)
	var goals := objectives(area_id, _level.town.quests, GameData.quests, GameData.monsters, living, area.get("props", []))
	if goals.is_empty():
		_multi.multimesh.visible_instance_count = 0
		_last_target = Vector2(1e9, 1e9)
		return
	var target := goals[0]
	for g in goals:
		if from.distance_squared_to(g) < from.distance_squared_to(target):
			target = g
	# Só refaz o caminho se o herói andou ou o objetivo mudou (a grade da área é montada uma vez).
	if from.distance_to(_last_from) < 1.0 and target.distance_to(_last_target) < 1.0:
		return
	_last_from = from
	_last_target = target
	if _map_area != area_id or _map.is_empty():
		_map = build_map(area)
		_map_area = area_id
	_show(footprints(route(_map, from, target)))


func _show(prints: Array[Dictionary]) -> void:
	var multi := _multi.multimesh
	multi.visible_instance_count = prints.size()
	for i in prints.size():
		var p: Dictionary = prints[i]
		var dir: Vector2 = p.direction
		# A malha olha para -Z; o pé esquerdo é o direito espelhado.
		var basis := Basis(Vector3.UP, atan2(-dir.x, -dir.y))
		basis = basis * Basis.from_scale(Vector3(-1.0 if p.left else 1.0, 1.0, 1.0))
		multi.set_instance_transform(i, Transform3D(basis, Vector3(p.position.x, FOOT_HEIGHT, p.position.y)))
		multi.set_instance_color(i, Color(FOOT_COLOR.r, FOOT_COLOR.g, FOOT_COLOR.b, p.alpha))


## Textura da pegada (64 x 128): bola do pé e calcanhar, a ponta para cima; bordas macias.
static func footprint_texture() -> ImageTexture:
	var w := 64
	var h := 128
	var image := Image.create(w, h, false, Image.FORMAT_RGBA8)
	for y in h:
		for x in w:
			var u := (x + 0.5) / w
			var v := (y + 0.5) / h
			var d := minf(_ellipse(u, v, 0.5, 0.30, 0.40, 0.25), minf(_ellipse(u, v, 0.5, 0.80, 0.27, 0.17), _ellipse(u, v, 0.56, 0.55, 0.17, 0.2)))
			var alpha := 1.0 - smoothstep(0.82, 1.0, d)
			image.set_pixel(x, y, Color(1, 1, 1, alpha))
	return ImageTexture.create_from_image(image)


## Distância normalizada ao centro de uma elipse (1 = na borda).
static func _ellipse(u: float, v: float, cx: float, cy: float, rx: float, ry: float) -> float:
	return sqrt(pow((u - cx) / rx, 2.0) + pow((v - cy) / ry, 2.0))


# --- Objetivos -------------------------------------------------------------------------------------------------------

## Onde estão os objetivos das missões ativas desta área. `living`: bichos vivos como {group, monster_id, position (x, z)};
## `props`: os objetos da área (um grupo que ainda não nasceu e é invocado por um objeto com "summon" aponta para esse objeto).
static func objectives(area_id: String, quests: Dictionary, defs: Dictionary, monsters: Dictionary, living: Array, props: Array = []) -> Array[Vector2]:
	var found: Array[Vector2] = []
	for id: String in quests:
		if quests[id] != "active":
			continue
		var quest: Dictionary = defs.get(id, {})
		if quest.get("area", "") != area_id:
			continue
		var groups: Array = quest.get("clear", [])
		var items: Array = quest.get("items", [])
		if quest.has("item"):
			items = items + [quest.item]
		for e: Dictionary in living:
			var monster: Dictionary = monsters.get(e.monster_id, {})
			var hit := false
			if not groups.is_empty():
				hit = e.group in groups
			elif not items.is_empty():
				hit = monster.get("quest_drop", "") in items
			else:
				hit = monster.get("category", "") == "boss"
			if hit:
				found.append(e.position)
		if not groups.is_empty() and not found_for(groups, living):
			for prop: Dictionary in props:
				if prop.has("summon") and prop.summon.get("id", "") in groups:
					found.append(Vector2(prop.position[0], prop.position[1]))
	return found


## Algum bicho vivo é de um dos grupos?
static func found_for(groups: Array, living: Array) -> bool:
	for e: Dictionary in living:
		if e.group in groups:
			return true
	return false


# --- Grade de caminhos -------------------------------------------------------------------------------------------------

## Grade de CELL metros por cima da área: chão das salas (menos a margem das paredes), vãos das portas e sem os objetos "solid".
## Devolve {bounds, size, walk (1 = anda), grid (AStarGrid2D)}.
static func build_map(area: Dictionary) -> Dictionary:
	var rect := Rect2()
	var first := true
	for room: Dictionary in area.get("rooms", []):
		var r := Rect2(room.center[0] - room.size[0] / 2.0, room.center[1] - room.size[1] / 2.0, room.size[0], room.size[1])
		rect = r if first else rect.merge(r)
		first = false
	rect = rect.grow(2.0)
	var size := Vector2i(ceili(rect.size.x / CELL), ceili(rect.size.y / CELL))
	var open: Array[Rect2] = []
	for room: Dictionary in area.get("rooms", []):
		var cx: float = room.center[0]
		var cz: float = room.center[1]
		var hx: float = room.size[0] / 2.0
		var hz: float = room.size[1] / 2.0
		open.append(Rect2(cx - hx + WALL_MARGIN, cz - hz + WALL_MARGIN, room.size[0] - 2.0 * WALL_MARGIN, room.size[1] - 2.0 * WALL_MARGIN))
		for door: String in room.get("doors", []):
			var side := door.get_slice(":", 0)
			var offset := float(door.get_slice(":", 1)) if door.contains(":") else 0.0
			var half_gap := minf(DOOR_WIDTH, room.size[0] if side in ["north", "south"] else room.size[1]) / 2.0 - 0.6
			match side:
				"north":
					open.append(Rect2(cx + offset - half_gap, cz - hz - 1.0, half_gap * 2.0, 2.0 + WALL_MARGIN))
				"south":
					open.append(Rect2(cx + offset - half_gap, cz + hz - 1.0 - WALL_MARGIN, half_gap * 2.0, 2.0 + WALL_MARGIN))
				"east":
					open.append(Rect2(cx + hx - 1.0 - WALL_MARGIN, cz + offset - half_gap, 3.0 + WALL_MARGIN, half_gap * 2.0))
				"west":
					open.append(Rect2(cx - hx - 2.0, cz + offset - half_gap, 3.0 + WALL_MARGIN, half_gap * 2.0))
	var blocked: Array[Rect2] = []
	for decor: Dictionary in area.get("decor", []):
		if decor.has("solid") and decor.has("position"):
			var d: Array = decor.solid
			blocked.append(Rect2(decor.position[0] - d[0] / 2.0, decor.position[1] - d[1] / 2.0, d[0], d[1]).grow(-0.1))
	var walk := PackedByteArray()
	walk.resize(size.x * size.y)
	walk.fill(0)
	for r in open:
		_paint(walk, size, rect.position, r, 1)
	for r in blocked:
		_paint(walk, size, rect.position, r, 0)
	var grid := AStarGrid2D.new()
	grid.region = Rect2i(0, 0, size.x, size.y)
	grid.cell_size = Vector2(CELL, CELL)
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	grid.update()
	for y in size.y:
		for x in size.x:
			if walk[y * size.x + x] == 0:
				grid.set_point_solid(Vector2i(x, y), true)
	return {"bounds": rect, "size": size, "walk": walk, "grid": grid}


## Marca `value` nas células cujo centro cai dentro de `r`.
static func _paint(walk: PackedByteArray, size: Vector2i, origin: Vector2, r: Rect2, value: int) -> void:
	var x0 := clampi(ceili((r.position.x - origin.x) / CELL - 0.5), 0, size.x)
	var x1 := clampi(floori((r.end.x - origin.x) / CELL - 0.5) + 1, 0, size.x)
	var y0 := clampi(ceili((r.position.y - origin.y) / CELL - 0.5), 0, size.y)
	var y1 := clampi(floori((r.end.y - origin.y) / CELL - 0.5) + 1, 0, size.y)
	for y in range(y0, y1):
		for x in range(x0, x1):
			walk[y * size.x + x] = value


static func _cell_of(map: Dictionary, at: Vector2) -> Vector2i:
	var p: Vector2 = (at - Rect2(map.bounds).position) / CELL
	return Vector2i(clampi(floori(p.x), 0, map.size.x - 1), clampi(floori(p.y), 0, map.size.y - 1))


static func _walkable(map: Dictionary, at: Vector2) -> bool:
	var rect: Rect2 = map.bounds
	if not rect.has_point(at):
		return false
	var c := _cell_of(map, at)
	return map.walk[c.y * map.size.x + c.x] == 1


## A célula andável mais perto de `at` (espiral de até 8 células).
static func _nearest_cell(map: Dictionary, at: Vector2) -> Vector2i:
	var origin := _cell_of(map, at)
	if map.walk[origin.y * map.size.x + origin.x] == 1:
		return origin
	for radius in range(1, 9):
		var best := Vector2i(-1, -1)
		var best_d := 1e9
		for dy in range(-radius, radius + 1):
			for dx in range(-radius, radius + 1):
				if maxi(absi(dx), absi(dy)) != radius:
					continue
				var c := origin + Vector2i(dx, dy)
				if c.x < 0 or c.y < 0 or c.x >= map.size.x or c.y >= map.size.y or map.walk[c.y * map.size.x + c.x] != 1:
					continue
				var d := float(dx * dx + dy * dy)
				if d < best_d:
					best = c
					best_d = d
		if best.x >= 0:
			return best
	return Vector2i(-1, -1)


## Caminho (pontos x, z) de `from` até `to`, passando pelas salas e portas; vazio se não há como chegar. Já endireitado.
static func route(map: Dictionary, from: Vector2, to: Vector2) -> PackedVector2Array:
	var a := _nearest_cell(map, from)
	var b := _nearest_cell(map, to)
	if a.x < 0 or b.x < 0:
		return PackedVector2Array()
	var cells: Array[Vector2i] = map.grid.get_id_path(a, b)
	if cells.is_empty():
		return PackedVector2Array()
	var origin: Vector2 = Rect2(map.bounds).position
	var points := PackedVector2Array()
	for c in cells:
		points.append(origin + (Vector2(c) + Vector2(0.5, 0.5)) * CELL)
	points[0] = from if _walkable(map, from) else points[0]
	# Puxa a corda: de cada ponto, vai direto ao mais longe que ainda se vê sem tocar parede.
	var pulled := PackedVector2Array([points[0]])
	var i := 0
	while i < points.size() - 1:
		var far := i + 1
		for j in range(points.size() - 1, i, -1):
			if _clear(map, points[i], points[j]):
				far = j
				break
		pulled.append(points[far])
		i = far
	return pulled


## O trecho a-b cabe no chão (com 0,4 m de folga dos lados)?
static func _clear(map: Dictionary, a: Vector2, b: Vector2) -> bool:
	var length := a.distance_to(b)
	if length < 0.01:
		return true
	var dir := (b - a) / length
	var side := Vector2(-dir.y, dir.x) * 0.4
	var steps := ceili(length / 0.4)
	for s in range(steps + 1):
		var p := a.lerp(b, float(s) / steps)
		if not _walkable(map, p) or not _walkable(map, p + side) or not _walkable(map, p - side):
			return false
	return true


# --- Passos ----------------------------------------------------------------------------------------------------------------------

## Pegadas ao longo do caminho (que sai do herói): {position, direction, left, alpha}; alternam esquerda e direita, começam LEAD à frente do começo,
## param END_GAP antes do fim e esmaecem com a distância.
static func footprints(path: PackedVector2Array) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if path.size() < 2:
		return result
	var total := 0.0
	for i in range(path.size() - 1):
		total += path[i].distance_to(path[i + 1])
	var end_at := total - END_GAP
	var distance := LEAD
	var count := 0
	while distance < end_at and count < MAX_STEPS:
		var at := _point_along(path, distance)
		var dir := _direction_along(path, distance)
		var side := Vector2(-dir.y, dir.x) * (0.15 if count % 2 == 0 else -0.15)
		result.append({"position": at + side, "direction": dir, "left": count % 2 == 0,
			"alpha": clampf(1.0 - float(count) / MAX_STEPS * 0.75, 0.2, 0.9)})
		distance += STEP
		count += 1
	return result


static func _point_along(path: PackedVector2Array, distance: float) -> Vector2:
	var left := distance
	for i in range(path.size() - 1):
		var seg := path[i].distance_to(path[i + 1])
		if left <= seg:
			return path[i].lerp(path[i + 1], left / maxf(seg, 0.001))
		left -= seg
	return path[path.size() - 1]


static func _direction_along(path: PackedVector2Array, distance: float) -> Vector2:
	var left := distance
	for i in range(path.size() - 1):
		var seg := path[i].distance_to(path[i + 1])
		if left <= seg:
			return (path[i + 1] - path[i]).normalized()
		left -= seg
	return (path[path.size() - 1] - path[path.size() - 2]).normalized()
