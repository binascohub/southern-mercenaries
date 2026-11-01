# Southern Mercenaries — GPL-3.0-or-later
class_name MarketStall
extends RefCounted
## Barracas de comércio de Tortuga montadas por código, nos estilos da referência do autor
## (barracas de feira de madeira): toldo listrado com barra recortada, telhado de ripas,
## tenda com cortinas e telhado de pano xadrez remendado. Cada uma tem estrutura de
## madeira, balcão, prateleiras ao fundo e um teto de tecido ou de ripas.
##
## Frente para +Z (a rua); a origem é o centro do chão da barraca. Largura 3,8 m, 2,2 m de
## fundo e uns 2,9 m de altura.

const WIDTH := 3.8
const DEPTH := 2.2
const HEIGHT := 2.9

## Estilos: cores da madeira, dos postes e do teto; "roof" escolhe o tipo de teto.
const STYLES := {
	"awning_yellow": {"roof": "awning", "stripe_a": Color(0.9, 0.82, 0.2), "stripe_b": Color(0.62, 0.7, 0.16),
		"wood": Color(0.36, 0.14, 0.11), "post": Color(0.3, 0.12, 0.1), "top": Color(0.72, 0.5, 0.2), "counter": true},
	"awning_blue": {"roof": "awning", "stripe_a": Color(0.3, 0.34, 0.68), "stripe_b": Color(0.9, 0.9, 0.92),
		"wood": Color(0.62, 0.42, 0.3), "post": Color(0.5, 0.34, 0.24), "top": Color(0.84, 0.55, 0.45), "counter": true},
	"shingle_blue": {"roof": "shingle", "shingle_a": Color(0.5, 0.36, 0.28), "shingle_b": Color(0.62, 0.44, 0.34),
		"wood": Color(0.5, 0.36, 0.28), "post": Color(0.2, 0.46, 0.66), "top": Color(0.6, 0.7, 0.74), "counter": false},
	"tent_teal": {"roof": "tent", "tent": Color(0.2, 0.58, 0.7), "trim": Color(0.82, 0.46, 0.4), "curtain": Color(0.45, 0.65, 0.78),
		"wood": Color(0.46, 0.34, 0.24), "post": Color(0.4, 0.28, 0.2), "top": Color(0.78, 0.6, 0.28), "counter": false},
	"patch": {"roof": "patch", "cloth_a": Color(0.3, 0.3, 0.5), "cloth_b": Color(0.74, 0.74, 0.84),
		"wood": Color(0.52, 0.5, 0.3), "post": Color(0.48, 0.46, 0.26), "top": Color(0.32, 0.5, 0.2), "counter": false},
}


static func build(style_name: String) -> Node3D:
	var style: Dictionary = STYLES.get(style_name, STYLES.awning_yellow)
	var root := Node3D.new()
	var wood := SurfaceTool.new()
	wood.begin(Mesh.PRIMITIVE_TRIANGLES)
	var cloth := SurfaceTool.new()
	cloth.begin(Mesh.PRIMITIVE_TRIANGLES)
	var wood_color: Color = style.wood
	var post_color: Color = style.post
	var front := DEPTH * 0.5
	var back := -DEPTH * 0.5
	var half := WIDTH * 0.5
	# Piso de tábuas e estrado.
	_box(wood, Vector3(0, 0.05, 0), Vector3(WIDTH + 0.2, 0.1, DEPTH + 0.2), wood_color.darkened(0.2))
	# Postes dos quatro cantos.
	for x in [-half + 0.1, half - 0.1]:
		for z in [back + 0.1, front - 0.1]:
			_box(wood, Vector3(x, HEIGHT * 0.42, z), Vector3(0.16, HEIGHT * 0.84, 0.16), post_color)
	# Fundo: tábuas na vertical e três prateleiras.
	var planks := 14
	for i in planks:
		var shade := 1.0 + 0.1 * sin(i * 2.3)
		_box(wood, Vector3(-half + (i + 0.5) * WIDTH / planks, 1.2, back + 0.04), Vector3(WIDTH / planks - 0.01, 2.2, 0.06), wood_color * shade)
	for y in [0.9, 1.45, 2.0]:
		_box(wood, Vector3(0, y, back + 0.26), Vector3(WIDTH - 0.3, 0.05, 0.42), wood_color.lightened(0.1))
	for x in [-half + 0.3, half - 0.3]:
		_box(wood, Vector3(x, 1.45, back + 0.26), Vector3(0.05, 1.1, 0.42), wood_color.lightened(0.1))
	# Balcão (barracas fechadas) ou mesa com estrado (as abertas).
	if style.counter:
		for i in 12:
			var shade := 1.0 + 0.08 * sin(i * 1.7)
			_box(wood, Vector3(-half + 0.2 + (i + 0.5) * (WIDTH - 0.4) / 12.0, 0.47, front - 0.3), Vector3((WIDTH - 0.4) / 12.0 - 0.01, 0.92, 0.5), wood_color * shade)
		_box(wood, Vector3(0, 0.96, front - 0.28), Vector3(WIDTH - 0.1, 0.07, 0.8), style.top)
	else:
		_box(wood, Vector3(0, 0.42, front - 0.55), Vector3(WIDTH - 0.8, 0.07, 0.95), style.top)
		for x in [-half + 0.55, half - 0.55]:
			for z in [front - 0.95, front - 0.15]:
				_box(wood, Vector3(x, 0.2, z), Vector3(0.1, 0.38, 0.1), wood_color)
	# Teto.
	match String(style.roof):
		"awning":
			_awning(cloth, wood, style.stripe_a, style.stripe_b)
		"shingle":
			_shingle_roof(wood, style.shingle_a, style.shingle_b, post_color)
		"tent":
			_tent(cloth, wood, style)
		"patch":
			_patch_roof(cloth, wood, style)
	root.add_child(_instance(wood, "wood", Color.WHITE))
	root.add_child(_instance(cloth, "cloth", Color.WHITE))
	return root


# --- Tetos -------------------------------------------------------------------

## Toldo inclinado de listras, com a barra da frente recortada em semicírculos.
static func _awning(cloth: SurfaceTool, wood: SurfaceTool, color_a: Color, color_b: Color) -> void:
	var half := WIDTH * 0.5
	var stripes := 12
	var back := Vector3(0, HEIGHT - 0.05, -DEPTH * 0.5 - 0.1)
	var front := Vector3(0, HEIGHT - 0.78, DEPTH * 0.5 + 0.32)
	for i in stripes:
		var x0 := -half - 0.1 + i * (WIDTH + 0.2) / stripes
		var x1 := x0 + (WIDTH + 0.2) / stripes
		var color := color_a if i % 2 == 0 else color_b
		_quad(cloth, Vector3(x0, back.y, back.z), Vector3(x1, back.y, back.z), Vector3(x1, front.y, front.z), Vector3(x0, front.y, front.z), color)
		# Barra recortada: semicírculo pendurado na ponta da listra.
		var mid := (x0 + x1) * 0.5
		var radius := (x1 - x0) * 0.5
		var hang := 0.2
		var steps := 6
		for s in steps:
			var a0 := PI * s / steps
			var a1 := PI * (s + 1) / steps
			var p0 := Vector3(mid + cos(a0) * radius, front.y - sin(a0) * hang, front.z + 0.03 * sin(a0))
			var p1 := Vector3(mid + cos(a1) * radius, front.y - sin(a1) * hang, front.z + 0.03 * sin(a1))
			_tri(cloth, Vector3(mid, front.y, front.z), p0, p1, color)
	# Viga da frente e ganchos.
	_box(wood, Vector3(0, front.y + 0.04, front.z - 0.02), Vector3(WIDTH + 0.3, 0.07, 0.07), Color(0.3, 0.2, 0.14))


## Telhado de duas águas feito de fileiras de ripas sobrepostas.
static func _shingle_roof(wood: SurfaceTool, color_a: Color, color_b: Color, post_color: Color) -> void:
	var half := WIDTH * 0.5 + 0.25
	var rows := 5
	var ridge := HEIGHT + 0.25
	var eave := HEIGHT - 0.45
	var depth := DEPTH * 0.5 + 0.25
	for side in [-1.0, 1.0]:
		for r in rows:
			var t0 := float(r) / rows
			var t1 := float(r + 1) / rows + 0.03
			var z0: float = side * lerpf(0.0, depth, t0)
			var z1: float = side * lerpf(0.0, depth, minf(t1, 1.0))
			var y0 := lerpf(ridge, eave, t0)
			var y1 := lerpf(ridge, eave, minf(t1, 1.0))
			for i in 18:
				var x0 := -half + i * 2.0 * half / 18.0
				var x1 := x0 + 2.0 * half / 18.0 - 0.015
				var color := (color_a if (i + r) % 2 == 0 else color_b) * (1.0 + 0.06 * sin(i * 3.1 + r))
				_quad(wood, Vector3(x0, y0, z0), Vector3(x1, y0, z0), Vector3(x1, y1 - 0.03, z1), Vector3(x0, y1 - 0.03, z1), color)
	_box(wood, Vector3(0, ridge + 0.04, 0), Vector3(WIDTH + 0.7, 0.1, 0.14), post_color.darkened(0.2))
	# Vigas que seguram o telhado (de poste a poste, com um gancho para pendurar mercadoria).
	for z in [-DEPTH * 0.5 + 0.1, DEPTH * 0.5 - 0.1]:
		_box(wood, Vector3(0, HEIGHT - 0.5, z), Vector3(WIDTH, 0.12, 0.12), post_color)
	for i in 6:
		_box(wood, Vector3(-1.4 + i * 0.56, HEIGHT - 0.7, DEPTH * 0.5 - 0.1), Vector3(0.02, 0.2, 0.02), Color(0.2, 0.2, 0.22))


## Tenda de quatro águas com a barra recortada, ponteiras douradas e cortinas amarradas.
static func _tent(cloth: SurfaceTool, wood: SurfaceTool, style: Dictionary) -> void:
	var half_x := WIDTH * 0.5 + 0.25
	var half_z := DEPTH * 0.5 + 0.25
	var eave := HEIGHT - 0.55
	var peak := HEIGHT + 0.45
	var top_half := 0.45
	var color: Color = style.tent
	var trim: Color = style.trim
	var corners := [Vector3(-half_x, eave, -half_z), Vector3(half_x, eave, -half_z), Vector3(half_x, eave, half_z), Vector3(-half_x, eave, half_z)]
	var tops := [Vector3(-top_half, peak, -top_half * 0.6), Vector3(top_half, peak, -top_half * 0.6), Vector3(top_half, peak, top_half * 0.6), Vector3(-top_half, peak, top_half * 0.6)]
	for i in 4:
		var j := (i + 1) % 4
		_quad(cloth, corners[i], corners[j], tops[j], tops[i], color.lightened(0.08 * (i % 2)))
	_quad(cloth, tops[0], tops[1], tops[2], tops[3], color)
	# Barra rosada recortada em volta.
	for i in 4:
		var j := (i + 1) % 4
		var a: Vector3 = corners[i]
		var b: Vector3 = corners[j]
		var bumps := 9 if i % 2 == 0 else 5
		for k in bumps:
			var p0 := a.lerp(b, float(k) / bumps)
			var p1 := a.lerp(b, float(k + 1) / bumps)
			var mid := (p0 + p1) * 0.5
			_quad(cloth, p0, p1, p1 + Vector3(0, -0.14, 0), p0 + Vector3(0, -0.14, 0), trim)
			_tri(cloth, p0 + Vector3(0, -0.14, 0), p1 + Vector3(0, -0.14, 0), mid + Vector3(0, -0.3, 0), trim)
	for corner: Vector3 in [tops[0], tops[1], tops[2], tops[3]]:
		_box(wood, corner + Vector3(0, 0.08, 0), Vector3(0.05, 0.16, 0.05), Color(0.85, 0.7, 0.3))
	# Cortinas dos lados da frente, amarradas com corda.
	for x in [-half_x + 0.15, half_x - 0.15]:
		var sign := -1.0 if x < 0 else 1.0
		for s in 6:
			var t0 := float(s) / 6
			var t1 := float(s + 1) / 6
			var pull := 1.0 - 0.5 * sin(PI * t0)  # a cortina afina onde é amarrada
			var pull1 := 1.0 - 0.5 * sin(PI * t1)
			var y0 := eave - t0 * (eave - 0.1)
			var y1 := eave - t1 * (eave - 0.1)
			_quad(cloth, Vector3(x, y0, half_z - 0.2), Vector3(x - sign * 0.55 * pull, y0, half_z - 0.2),
				Vector3(x - sign * 0.55 * pull1, y1, half_z - 0.2), Vector3(x, y1, half_z - 0.2), style.curtain)
		_box(wood, Vector3(x - sign * 0.1, 1.3, half_z - 0.18), Vector3(0.12, 0.05, 0.05), Color(0.6, 0.5, 0.3))


## Teto de tábuas com um pano xadrez jogado por cima, torto e remendado.
static func _patch_roof(cloth: SurfaceTool, wood: SurfaceTool, style: Dictionary) -> void:
	var half_x := WIDTH * 0.5 + 0.3
	var back_y := HEIGHT + 0.05
	var front_y := HEIGHT - 0.45
	var z0 := -DEPTH * 0.5 - 0.25
	var z1 := DEPTH * 0.5 + 0.3
	# Tábuas do teto.
	for i in 16:
		var x0 := -half_x + i * 2.0 * half_x / 16.0
		_quad(wood, Vector3(x0, back_y, z0), Vector3(x0 + 2.0 * half_x / 16.0 - 0.02, back_y, z0),
			Vector3(x0 + 2.0 * half_x / 16.0 - 0.02, front_y, z1), Vector3(x0, front_y, z1), style.wood * (1.0 + 0.1 * sin(i * 2.9)))
	# Pano xadrez em dois retalhos, com dobras.
	for patch in [[-half_x - 0.1, 0.1, 0.15], [-0.5, half_x + 0.15, 0.0]]:
		var xa: float = patch[0]
		var xb: float = patch[1]
		var lift: float = patch[2]
		var cols := 10
		var rows := 7
		for c in cols:
			for r in rows:
				var u0 := float(c) / cols
				var u1 := float(c + 1) / cols
				var v0 := float(r) / rows
				var v1 := float(r + 1) / rows
				var color: Color = style.cloth_a if (c + r) % 2 == 0 else style.cloth_b
				_quad(cloth, _drape(xa, xb, u0, v0, back_y, front_y, z0, z1, lift), _drape(xa, xb, u1, v0, back_y, front_y, z0, z1, lift),
					_drape(xa, xb, u1, v1, back_y, front_y, z0, z1, lift), _drape(xa, xb, u0, v1, back_y, front_y, z0, z1, lift), color)
	# Vigas e escoras.
	for x in [-half_x + 0.2, half_x - 0.2]:
		_box(wood, Vector3(x, HEIGHT - 0.4, 0), Vector3(0.1, 0.1, DEPTH + 0.2), style.post)


static func _drape(xa: float, xb: float, u: float, v: float, back_y: float, front_y: float, z0: float, z1: float, lift: float) -> Vector3:
	var x := lerpf(xa, xb, u)
	var z := lerpf(z0, z1, v)
	var y := lerpf(back_y, front_y, v) + 0.1 + lift + 0.07 * sin(u * 9.0 + v * 4.0) + 0.05 * sin(v * 11.0 - u * 3.0)
	return Vector3(x, y - 0.12 * pow(v, 3.0), z)


# --- Malha -------------------------------------------------------------------

static func _box(tool: SurfaceTool, center: Vector3, size: Vector3, color: Color) -> void:
	var h := size * 0.5
	var c := [Vector3(-h.x, -h.y, -h.z), Vector3(h.x, -h.y, -h.z), Vector3(h.x, h.y, -h.z), Vector3(-h.x, h.y, -h.z),
		Vector3(-h.x, -h.y, h.z), Vector3(h.x, -h.y, h.z), Vector3(h.x, h.y, h.z), Vector3(-h.x, h.y, h.z)]
	for i in 8:
		c[i] += center
	for face in [[0, 1, 2, 3], [5, 4, 7, 6], [4, 0, 3, 7], [1, 5, 6, 2], [3, 2, 6, 7], [4, 5, 1, 0]]:
		_quad(tool, c[face[0]], c[face[1]], c[face[2]], c[face[3]], color)


static func _quad(tool: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, color: Color) -> void:
	_tri(tool, a, b, c, color)
	_tri(tool, a, c, d, color)


static func _tri(tool: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, color: Color) -> void:
	for vertex in [a, b, c]:
		tool.set_color(color)
		tool.add_vertex(vertex)


## Malha com normais calculadas, pintada com o tecido ("cloth") ou a madeira ("wood") gerados.
static func _instance(tool: SurfaceTool, kind: String, tint: Color) -> MeshInstance3D:
	tool.generate_normals()
	var piece := MeshInstance3D.new()
	piece.mesh = tool.commit()
	var base := StandardMaterial3D.new()
	base.vertex_color_use_as_albedo = true
	base.cull_mode = BaseMaterial3D.CULL_DISABLED
	piece.material_override = PaintedTextures.material(base, kind, tint, 1.0)
	piece.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	return piece
