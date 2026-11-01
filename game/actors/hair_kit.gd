# Southern Mercenaries — GPL-3.0-or-later
class_name HairKit
extends RefCounted
## Penteados femininos montados por código (nomes "Kit_*" em data/appearance.json), presos ao osso da
## cabeça: calota do couro cabeludo, cortinas de fios (bob, liso, ondulado, franja), coques, tranças,
## rabo de cavalo e puffs. Seguem as proporções do corpo medidas por Clothing; o cabelo é uma
## malha só, com listras de fios no vertex color e a cor da paleta de cabelo da criação.

const STYLES: Array[String] = [
	"Kit_Pixie", "Kit_Bob", "Kit_BobBangs", "Kit_Wavy", "Kit_Ponytail", "Kit_DoubleBun",
	"Kit_AfroPuffs", "Kit_MessyBun", "Kit_SpaceBuns", "Kit_Braids", "Kit_Shag", "Kit_LongStraight",
]

const SEGMENTS := 28


static func is_kit(style: String) -> bool:
	return style in STYLES


## Cria o cabelo `style` na cabeça do esqueleto. Retorna a peça (MeshInstance3D) ou null.
static func build(skeleton: Skeleton3D, frame: Clothing.Frame, style: String, color: Color) -> MeshInstance3D:
	var bone := NinjaGear._head_bone(skeleton)
	if bone == "" or not is_kit(style):
		return null
	var h := frame.height
	var origin := skeleton.get_bone_global_rest(skeleton.find_bone(bone)).origin
	var head := Head.new()
	head.c = origin + Vector3(0, h * 0.05, 0)
	var r := h * 0.085
	head.rx = r * 0.72
	head.ry = r * 0.95
	head.rz = r * 0.82
	head.f = frame.forward
	head.s = frame.side
	var tool := Clothing._tool()
	match style:
		"Kit_Pixie":
			_cap(tool, head, 26.0, 1.07, 0.35)
			_curtain(tool, head, -150.0, 150.0, 0.45, 0.75, 1.08, 0.0, 0.35)
			_fringe(tool, head, 55.0, 24.0, 0.55, 0.0)
		"Kit_Bob":
			_cap(tool, head, 22.0, 1.07, 0.0)
			_curtain(tool, head, -180.0, 180.0, 1.0, 1.0, 1.1, 0.0, 0.0, true)
		"Kit_BobBangs":
			_cap(tool, head, 22.0, 1.07, 0.0)
			_curtain(tool, head, -180.0, 180.0, 1.0, 1.0, 1.1, 0.0, 0.0, true)
			_fringe(tool, head, 60.0, 14.0, 1.0, 0.0)
		"Kit_Wavy":
			_cap(tool, head, 22.0, 1.07, 0.0)
			_curtain(tool, head, -180.0, 180.0, 2.0, 2.6, 1.12, 0.07, 0.0)
		"Kit_LongStraight":
			_cap(tool, head, 22.0, 1.07, 0.0)
			_curtain(tool, head, -180.0, 180.0, 2.4, 3.3, 1.12, 0.0, 0.0)
			_fringe(tool, head, 62.0, 12.0, 1.0, 0.0)
		"Kit_Shag":
			_cap(tool, head, 24.0, 1.07, 0.15)
			_curtain(tool, head, -180.0, 180.0, 1.7, 1.9, 1.12, 0.03, 0.55)
			_fringe(tool, head, 60.0, 16.0, 0.85, 0.5)
		"Kit_Ponytail":
			_cap(tool, head, 24.0, 1.05, 0.0)
			_tail(tool, head, [Vector3(0, 0.8, -0.8), Vector3(0, 1.15, -1.5), Vector3(0, 0.6, -2.2), Vector3(0, -0.9, -2.5), Vector3(0, -2.6, -2.3)], 0.5, 0.1)
		"Kit_DoubleBun":
			_cap(tool, head, 24.0, 1.05, 0.0)
			_ball(tool, head, Vector3(0, 1.28, -0.2), 0.52, 0.0)
			_ball(tool, head, Vector3(0, 0.92, -0.82), 0.4, 0.0)
		"Kit_AfroPuffs":
			_cap(tool, head, 24.0, 1.05, 0.0)
			for side in [-1.0, 1.0]:
				_ball(tool, head, Vector3(side * 0.82, 0.95, -0.3), 0.66, 0.2)
		"Kit_MessyBun":
			_cap(tool, head, 24.0, 1.05, 0.0)
			_ball(tool, head, Vector3(0, 1.3, -0.45), 0.5, 0.12)
			_ball(tool, head, Vector3(0.18, 1.55, -0.55), 0.3, 0.15)
			_ball(tool, head, Vector3(-0.3, 1.2, -0.5), 0.28, 0.15)
			_fringe(tool, head, 70.0, 22.0, 0.35, 0.8)
			for side in [-1.0, 1.0]:
				_tail(tool, head, [Vector3(side * 0.85, 0.35, 0.55), Vector3(side * 0.95, -0.1, 0.5), Vector3(side * 0.88, -0.6, 0.45)], 0.1, 0.03)
		"Kit_SpaceBuns":
			_cap(tool, head, 24.0, 1.05, 0.0)
			for side in [-1.0, 1.0]:
				_ball(tool, head, Vector3(side * 0.82, 1.0, -0.05), 0.4, 0.0)
		"Kit_Braids":
			_cap(tool, head, 24.0, 1.05, 0.0)
			for side in [-1.0, 1.0]:
				_braid(tool, head, side)
	var mesh := Clothing._finish(tool)
	var holder := BoneAttachment3D.new()
	holder.bone_name = bone
	skeleton.add_child(holder)
	var piece := MeshInstance3D.new()
	piece.mesh = mesh
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.albedo_color = color
	material.roughness = 0.55
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.rim_enabled = true
	material.rim = 0.25
	material.rim_tint = 0.6
	piece.material_override = material
	piece.transform = skeleton.get_bone_global_rest(skeleton.find_bone(bone)).affine_inverse()
	holder.add_child(piece)
	piece.name = style
	return piece


## A cabeça: elipsoide com centro, raios e direções (frente e lado).
class Head:
	var c := Vector3.ZERO
	var rx := 0.1
	var ry := 0.12
	var rz := 0.1
	var f := Vector3.BACK
	var s := Vector3.RIGHT

	## Ponto no elipsoide: az em graus (0 = frente, positivo para o lado `s`), el em graus (90 = topo).
	func at(az: float, el: float, grow: float) -> Vector3:
		var a := deg_to_rad(az)
		var e := deg_to_rad(el)
		return c + s * (sin(a) * cos(e) * rx * grow) + f * (cos(a) * cos(e) * rz * grow) + Vector3.UP * (sin(e) * ry * grow)

	## Posição em unidades do raio (x = lado, y = acima, z = frente), centrada na cabeça.
	func local(v: Vector3) -> Vector3:
		return c + s * (v.x * rx) + Vector3.UP * (v.y * ry) + f * (v.z * rz)


## Altura (graus) até onde a calota desce em cada direção: linha da testa à frente, orelha e nuca.
static func _hairline(az: float, front: float) -> float:
	var k := (1.0 - cos(deg_to_rad(az))) * 0.5
	return lerpf(front, -2.0, k * 2.0) if k < 0.5 else lerpf(-2.0, -22.0, (k - 0.5) * 2.0)


static func _strand(az: float, row: float, base: float = 0.9) -> float:
	return base + (1.0 - base) * (0.5 + 0.5 * sin(az * 0.55 + row * 0.8) * sin(az * 1.37))


static func _shade(az: float, t: float, inner: float = 0.0) -> Color:
	var v := _strand(az, t) * lerpf(1.0, 0.72, t) * (1.0 - inner * 0.25)
	return Color(v, v, v)


## Malha em grade: pts[i][k] (coluna i, linha k); `closed` fecha a última coluna na primeira.
static func _grid(tool: SurfaceTool, pts: Array, cols: Array, closed: bool) -> void:
	var n := pts.size()
	var last := n if closed else n - 1
	for i in last:
		var j := (i + 1) % n
		for k in pts[i].size() - 1:
			var a: Vector3 = pts[i][k]
			var b: Vector3 = pts[j][k]
			var c: Vector3 = pts[j][k + 1]
			var d: Vector3 = pts[i][k + 1]
			var ca: Color = cols[i][k]
			var cb: Color = cols[j][k]
			var cc: Color = cols[j][k + 1]
			var cd: Color = cols[i][k + 1]
			for pair in [[a, ca], [b, cb], [c, cc], [a, ca], [c, cc], [d, cd]]:
				tool.set_smooth_group(0)
				tool.set_color(pair[1])
				tool.add_vertex(pair[0])


## Calota: cobre o topo da cabeça até a linha do cabelo; `jag` serrilha a borda.
static func _cap(tool: SurfaceTool, head: Head, front_line: float, grow: float, jag: float) -> void:
	var pts: Array = []
	var cols: Array = []
	for i in SEGMENTS:
		var az := 360.0 * i / SEGMENTS - 180.0
		var low := _hairline(az, front_line)
		low += jag * 14.0 * sin(az * 0.31) * sin(az * 0.9 + 1.0)
		var col: Array = []
		var line: Array = []
		for k in 9:
			var el := lerpf(90.0, low, float(k) / 8.0)
			line.append(head.at(az, el, grow + 0.025 * sin(float(k) * 0.5)))
			col.append(_shade(az, float(k) / 8.0 * 0.4))
		pts.append(line)
		cols.append(col)
	_grid(tool, pts, cols, true)


## Cortina de fios pendurada da borda da calota. `side_len` e `back_len` são comprimentos (em raios
## verticais da cabeça) nas laterais e na nuca; `wave` ondula; `jag` serrilha a barra; `curl` vira a ponta para dentro.
static func _curtain(tool: SurfaceTool, head: Head, az0: float, az1: float, side_len: float, back_len: float, grow: float, wave: float, jag: float, curl := false) -> void:
	var steps := int(SEGMENTS * (az1 - az0) / 360.0)
	var pts: Array = []
	var cols: Array = []
	var closed := absf(az1 - az0) >= 359.0
	var count := steps if closed else steps + 1
	for i in count:
		var az := lerpf(az0, az1, float(i) / steps)
		var back := (1.0 - cos(deg_to_rad(az))) * 0.5
		var low := _hairline(az, 22.0)
		var top := head.at(az, low, 1.04)
		var length := head.ry * lerpf(side_len, back_len, back) * (1.0 - jag * 0.6 * absf(sin(az * 0.7 + 0.4) * sin(az * 1.9)))
		# Na frente do rosto (az perto de 0) não há cortina: o cabelo cai só dos lados.
		var open := smoothstep(0.0, 1.0, clampf((absf(az) - 40.0) / 45.0, 0.0, 1.0))
		length *= open
		var dir := (head.s * sin(deg_to_rad(az)) * head.rx + head.f * cos(deg_to_rad(az)) * head.rz).normalized()
		var line: Array = []
		var col: Array = []
		for k in 9:
			var t := float(k) / 8.0
			var spread := clampf(length / head.ry * 0.45, 0.4, 1.5)
			var out := 0.04 + 0.26 * spread * t * (0.35 + back) - (0.25 * t * t if curl else 0.0)
			var p := top + dir * (head.rx * out) + Vector3.DOWN * (length * t)
			p += head.s * (wave * head.rx * sin(t * 9.0 + az * 0.09)) * t
			p += dir * (wave * head.rx * 0.8 * sin(t * 7.0 + az * 0.2 + 1.0)) * t
			line.append(p)
			col.append(_shade(az, t, 0.0))
		pts.append(line)
		cols.append(col)
	_grid(tool, pts, cols, closed)


## Franja: cortina curta sobre a testa, de `top` (grau de elevação) até `bottom`; `jag` serrilha.
static func _fringe(tool: SurfaceTool, head: Head, spread: float, bottom: float, amount: float, jag: float) -> void:
	var pts: Array = []
	var cols: Array = []
	var n := 10
	for i in n:
		var az := lerpf(-spread, spread, float(i) / (n - 1))
		var line: Array = []
		var col: Array = []
		var low := bottom + 16.0 * (1.0 - amount) + jag * 9.0 * sin(float(i) * 2.1) * sin(float(i) * 0.7 + 1.0)
		for k in 5:
			var t := float(k) / 4.0
			var el := lerpf(62.0, low, t)
			line.append(head.at(az, el, 1.07 + 0.02 * t))
			col.append(_shade(az, t * 0.3))
		pts.append(line)
		cols.append(col)
	_grid(tool, pts, cols, false)


## Esfera com ondulações (`bump` > 0 faz o puff crespo); `p` em unidades de raio da cabeça.
static func _ball(tool: SurfaceTool, head: Head, p: Vector3, radius: float, bump: float) -> void:
	var centre := head.local(p)
	var rr := head.rx * radius
	var pts: Array = []
	var cols: Array = []
	var around := 16
	for i in around:
		var az := TAU * i / around
		var line: Array = []
		var col: Array = []
		for k in 9:
			var el := lerpf(PI * 0.5, -PI * 0.5, float(k) / 8.0)
			var wob := 1.0 + bump * sin(az * 5.0 + el * 4.0) * cos(el * 3.0) + bump * 0.6 * sin(az * 9.0 - el * 6.0)
			var d := Vector3(sin(az) * cos(el), sin(el), cos(az) * cos(el)) * wob
			line.append(centre + head.s * (d.x * rr) + Vector3.UP * (d.y * rr * 0.9) + head.f * (d.z * rr))
			var v := _strand(az * 8.0, float(k)) * lerpf(1.0, 0.8, float(k) / 8.0)
			col.append(Color(v, v, v))
		pts.append(line)
		cols.append(col)
	_grid(tool, pts, cols, true)


## Tubo afinando ao longo de pontos (em unidades de raio da cabeça): rabo de cavalo, mechas.
static func _tail(tool: SurfaceTool, head: Head, path: Array, start_radius: float, end_radius: float, ripple := 0.0) -> void:
	var pts: Array = []
	var cols: Array = []
	var around := 8
	var samples := 40
	for i in around:
		var a := TAU * i / around
		var line: Array = []
		var col: Array = []
		for k in samples + 1:
			var t := float(k) / samples
			var centre := _curve(path, t)
			var ahead := _curve(path, minf(t + 0.05, 1.0)) - _curve(path, maxf(t - 0.05, 0.0))
			var tangent := ahead.normalized()
			var side := tangent.cross(Vector3.UP)
			if side.length() < 0.05:
				side = Vector3.RIGHT
			side = side.normalized()
			var up := side.cross(tangent).normalized()
			# O rabo abre um pouco no meio e afina na ponta.
			var rad := lerpf(start_radius, end_radius, t) * (1.0 + 0.35 * sin(t * PI) * (1.0 if start_radius > 0.3 else 0.0) + ripple * sin(t * 70.0))
			var offset := (side * cos(a) + up * sin(a)) * rad
			var world := head.local(centre) + head.s * (offset.x * head.rx) + Vector3.UP * (offset.y * head.ry) + head.f * (offset.z * head.rz)
			line.append(world)
			var v := _strand(a * 6.0, t * 10.0) * lerpf(1.0, 0.75, t)
			col.append(Color(v, v, v))
		pts.append(line)
		cols.append(col)
	_grid(tool, pts, cols, true)


static func _curve(path: Array, t: float) -> Vector3:
	var scaled := t * (path.size() - 1)
	var i := mini(int(scaled), path.size() - 2)
	var f := scaled - i
	var p0: Vector3 = path[maxi(i - 1, 0)]
	var p1: Vector3 = path[i]
	var p2: Vector3 = path[i + 1]
	var p3: Vector3 = path[mini(i + 2, path.size() - 1)]
	return p1.cubic_interpolate(p2, p0, p3, f)


## Trança: contas alternadas descendo de trás da orelha para a frente do ombro.
static func _braid(tool: SurfaceTool, head: Head, side: float) -> void:
	var path := [Vector3(side * 0.92, 0.35, -0.35), Vector3(side * 1.1, -0.4, -0.05), Vector3(side * 1.2, -1.3, 0.2), Vector3(side * 1.1, -2.3, 0.5), Vector3(side * 1.0, -3.2, 0.62)]
	_tail(tool, head, path, 0.27, 0.12, 0.22)
