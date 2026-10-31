# Southern Mercenaries — GPL-3.0-or-later
class_name ExploreMap
extends RefCounted
## Mapa que se revela (09-interface.md, seções 3 e 8; 03-2-areas.md): a área é
## uma grade de células de CELL metros; cada célula vira "vista" quando um
## herói passa a até REVEAL_RADIUS dela. Uma máscara por área, do grupo
## (decidido: a exploração de um revela para todos), guardada na campanha em
## base64. Sem nós: o nível e o minimapa usam estas funções.

const CELL := 2.0
const REVEAL_RADIUS := 12.0


## Retângulo da área (x, z) que cobre todas as salas, com 1 m de folga.
static func bounds(area: Dictionary) -> Rect2:
	var rect := Rect2()
	var first := true
	for room: Dictionary in area.get("rooms", []):
		var r := Rect2(room.center[0] - room.size[0] / 2.0, room.center[1] - room.size[1] / 2.0, room.size[0], room.size[1])
		rect = r if first else rect.merge(r)
		first = false
	return rect.grow(1.0)


static func grid_size(area: Dictionary) -> Vector2i:
	var b := bounds(area)
	return Vector2i(ceili(b.size.x / CELL), ceili(b.size.y / CELL))


## Máscara vazia (nada visto): um byte por célula.
static func empty(area: Dictionary) -> PackedByteArray:
	var size := grid_size(area)
	var mask := PackedByteArray()
	mask.resize(size.x * size.y)
	mask.fill(0)
	return mask


## Células que ficam dentro de alguma sala (o chão que o minimapa desenha).
static func floor_cells(area: Dictionary) -> PackedByteArray:
	var b := bounds(area)
	var size := grid_size(area)
	var cells := empty(area)
	for y in size.y:
		for x in size.x:
			var center := b.position + Vector2(x + 0.5, y + 0.5) * CELL
			for room: Dictionary in area.get("rooms", []):
				var r := Rect2(room.center[0] - room.size[0] / 2.0, room.center[1] - room.size[1] / 2.0, room.size[0], room.size[1])
				if r.grow(0.5).has_point(center):
					cells[y * size.x + x] = 1
					break
	return cells


## Revela em volta de `at` (x, z); devolve os índices das células que eram névoa.
static func reveal(mask: PackedByteArray, area: Dictionary, at: Vector2, radius := REVEAL_RADIUS) -> PackedInt32Array:
	var b := bounds(area)
	var size := grid_size(area)
	var found := PackedInt32Array()
	if mask.size() != size.x * size.y:
		return found
	var local := (at - b.position) / CELL
	var r := radius / CELL
	for y in range(maxi(floori(local.y - r), 0), mini(ceili(local.y + r), size.y)):
		for x in range(maxi(floori(local.x - r), 0), mini(ceili(local.x + r), size.x)):
			var index := y * size.x + x
			if mask[index] == 0 and Vector2(x + 0.5, y + 0.5).distance_to(local) <= r:
				mask[index] = 1
				found.append(index)
	return found


## Já viu este ponto (x, z)?
static func is_seen(mask: PackedByteArray, area: Dictionary, at: Vector2) -> bool:
	var b := bounds(area)
	var size := grid_size(area)
	var cell := Vector2i(((at - b.position) / CELL).floor())
	if cell.x < 0 or cell.y < 0 or cell.x >= size.x or cell.y >= size.y or mask.size() != size.x * size.y:
		return false
	return mask[cell.y * size.x + cell.x] != 0


## Fração do chão já vista (0 a 1).
static func explored_fraction(mask: PackedByteArray, area: Dictionary) -> float:
	var ground := floor_cells(area)
	var total := 0
	var seen := 0
	for i in ground.size():
		if ground[i] != 0:
			total += 1
			if i < mask.size() and mask[i] != 0:
				seen += 1
	return float(seen) / total if total > 0 else 0.0


static func encode(mask: PackedByteArray) -> String:
	return Marshalls.raw_to_base64(mask.compress(FileAccess.COMPRESSION_DEFLATE)) + ":%d" % mask.size()


## Lê a máscara salva; se não bater com a área (mudou nos dados), começa vazia.
static func decode(text: String, area: Dictionary) -> PackedByteArray:
	var size := grid_size(area)
	if text == "" or not text.contains(":") or int(text.get_slice(":", 1)) != size.x * size.y:
		return empty(area)
	var mask := Marshalls.base64_to_raw(text.get_slice(":", 0)).decompress(size.x * size.y, FileAccess.COMPRESSION_DEFLATE)
	return mask if mask.size() == size.x * size.y else empty(area)
