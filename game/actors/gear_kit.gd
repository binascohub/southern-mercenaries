# Southern Mercenaries — GPL-3.0-or-later
class_name GearKit
extends RefCounted
## Peças de roupa e armadura montadas por código para os conjuntos por rank (ClassGear, NinjaGear):
## túnica longa (robe), mangas, tiras, bolsas, pergaminhos, peitoral, ombreiras, colar, pelagem,
## penas, gemas, coroa de chifres... Todas se ajustam à silhueta medida do corpo (Clothing._slice) e
## usam as malhas e materiais pintados do Clothing.


## Túnica longa do peito até `hem_y`: acompanha o corpo até o quadril e abre em A abaixo dele.
## `ragged` > 0 rasga a barra (em pontas de alturas diferentes); a última linha leva a cor `trim`.
static func robe(frame: Clothing.Frame, top_y: float, hem_y: float, color: Color, trim: Color, flare: float, ragged: float) -> ArrayMesh:
	var tool := Clothing._tool()
	var h := frame.height
	var hip_y := h * 0.5
	var margin := h * 0.014
	var rows := 14
	var rings: Array = []
	for j in rows + 1:
		var t := float(j) / rows
		var y := lerpf(top_y, hem_y, t)
		var below := clampf((hip_y - y) / maxf(hip_y - hem_y, 0.01), 0.0, 1.0)
		var s := Clothing._slice(frame, maxf(y, hip_y * 0.98) if y < hip_y else y, h * 0.135)
		var grow := h * flare * below
		var leg_room := h * 0.075 * below  # as pernas ficam um pouco abertas: dá folga
		rings.append({"y": y, "half": s.x + margin + grow + leg_room, "front": s.y + margin + grow * 0.8 + leg_room * 1.25, "back": s.z - margin - grow * 0.8 - leg_room * 0.6})
	var pleat := func(j: int, angle: float) -> Vector3:
		# Pregas verticais: o tecido ondula para fora e para dentro, mais fundo perto da barra.
		var below := clampf((hip_y - float(rings[j].y)) / maxf(hip_y - hem_y, 0.01), 0.0, 1.0)
		return Clothing._ring_point(frame, rings[j], angle, h * 0.016 * below * sin(angle * 13.0 + 0.4) + h * 0.006 * below * sin(angle * 29.0))
	for j in rows:
		var shade := trim if j == rows - 1 else color.darkened(0.12 * float(j) / rows)
		for i in Clothing.SIDES:
			var a0 := TAU * i / Clothing.SIDES
			var a1 := TAU * (i + 1) / Clothing.SIDES
			var p00: Vector3 = pleat.call(j, a0)
			var p01: Vector3 = pleat.call(j, a1)
			var p10: Vector3 = pleat.call(j + 1, a1)
			var p11: Vector3 = pleat.call(j + 1, a0)
			if j == rows - 1 and ragged > 0.0:
				p10.y -= h * ragged * absf(sin(a1 * 7.0 + 0.6))
				p11.y -= h * ragged * absf(sin(a0 * 7.0 + 0.6))
			# Sombra nas dobras: o fundo de cada prega fica mais escuro.
			var fold := 0.5 + 0.5 * sin((a0 + a1) * 0.5 * 13.0 + 0.4)
			Clothing._quad(tool, p00, p01, p10, p11, shade.darkened(0.22 * (1.0 - fold) * float(j) / rows))
	return Clothing._finish(tool)


## Faixa diagonal (bandoleira) de um ombro ao quadril oposto, na frente e atrás.
static func strap(frame: Clothing.Frame, from_y: float, to_y: float, side: float, width: float, color: Color) -> ArrayMesh:
	var tool := Clothing._tool()
	var steps := 10
	var margin := frame.height * 0.02
	for k in steps:
		var t0 := float(k) / steps
		var t1 := float(k + 1) / steps
		var r0 := Dictionary(_ring_for(frame, lerpf(from_y, to_y, t0), margin))
		var r1 := Dictionary(_ring_for(frame, lerpf(from_y, to_y, t1), margin))
		for back in [false, true]:
			var base := PI if back else 0.0
			var a0 := base + side * lerpf(1.25, -0.55, t0) * (-1.0 if back else 1.0)
			var a1 := base + side * lerpf(1.25, -0.55, t1) * (-1.0 if back else 1.0)
			var p0: Vector3 = Clothing._ring_point(frame, r0, a0)
			var p1: Vector3 = Clothing._ring_point(frame, r1, a1)
			var w := Vector3(0, width, 0)
			Clothing._quad(tool, p0 - w, p0 + w, p1 + w, p1 - w, color)
	return Clothing._finish(tool)


## Bolsa de cinto: caixa pequena com a aba de cima de outra cor.
static func pouch(frame: Clothing.Frame, y: float, angle: float, size: float, color: Color, flap: Color) -> ArrayMesh:
	var tool := Clothing._tool()
	var ring := _ring_for(frame, y, frame.height * 0.016)
	var c: Vector3 = Clothing._ring_point(frame, ring, angle, size * 0.5)
	var out := (Vector3(c.x - frame.centre.x, 0, c.z - frame.centre.z)).normalized()
	var side := out.cross(Vector3.UP).normalized() * size * 0.55
	var up := Vector3(0, size * 0.6, 0)
	var depth := out * size * 0.5
	var f := c + depth
	Clothing._quad(tool, f - side - up, f + side - up, f + side + up, f - side + up, color)
	Clothing._quad(tool, f - side + up, f + side + up, f + side + up * 0.2 - depth * 0.3, f - side + up * 0.2 - depth * 0.3, flap)
	Clothing._quad(tool, c - side - up, f - side - up, f - side + up, c - side + up, color.darkened(0.2))
	Clothing._quad(tool, f + side - up, c + side - up, c + side + up, f + side + up, color.darkened(0.2))
	return Clothing._finish(tool)


## Pergaminho enrolado pendurado na cintura.
static func scroll(frame: Clothing.Frame, y: float, angle: float, color: Color, paper: Color) -> ArrayMesh:
	var ring := _ring_for(frame, y, frame.height * 0.02)
	var c: Vector3 = Clothing._ring_point(frame, ring, angle, frame.height * 0.012)
	var h := frame.height
	var merged := ArrayMesh.new()
	var tube := Clothing._tube(frame, c - Vector3(0, h * 0.05, 0), c + Vector3(0, h * 0.04, 0), [[0.0, h * 0.009], [1.0, h * 0.009]], paper, color, true)
	merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, tube.surface_get_arrays(0))
	var tie := Clothing._tube(frame, c - Vector3(0, h * 0.005, 0), c + Vector3(0, h * 0.005, 0), [[0.0, h * 0.0105], [1.0, h * 0.0105]], color, color)
	merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, tie.surface_get_arrays(0))
	return merged


## Peitoral: casca de chapa na frente e atrás do peito, com crista no meio e filete nas bordas.
static func chest_plate(frame: Clothing.Frame, y0: float, y1: float, color: Color, trim: Color, bulge: float) -> ArrayMesh:
	var tool := Clothing._tool()
	var h := frame.height
	var rows := 8
	var rings: Array = []
	for j in rows + 1:
		var t := float(j) / rows
		var y := lerpf(y0, y1, t)
		var s := Clothing._slice(frame, y, h * 0.135)
		var swell := h * (0.012 + bulge * sin(t * PI))
		rings.append({"y": y, "half": s.x + swell, "front": s.y + swell * 1.3, "back": s.z - swell})
	var cols := 32
	for j in rows:
		var shade := trim if j == 0 or j == rows - 1 else color.lightened(0.04 * (j % 2))
		for i in cols:
			var a0 := TAU * i / cols
			var a1 := TAU * (i + 1) / cols
			Clothing._quad(tool, Clothing._ring_point(frame, rings[j + 1], a0), Clothing._ring_point(frame, rings[j + 1], a1),
				Clothing._ring_point(frame, rings[j], a1), Clothing._ring_point(frame, rings[j], a0), shade)
	# Crista central na frente e filetes laterais.
	for angle in [0.0, 0.5, -0.5]:
		for j in rows:
			var a: Vector3 = Clothing._ring_point(frame, rings[j], angle, h * 0.004)
			var b: Vector3 = Clothing._ring_point(frame, rings[j + 1], angle, h * 0.004)
			var w := frame.side * (h * (0.005 if angle == 0.0 else 0.003))
			Clothing._quad(tool, a - w, a + w, b + w, b - w, trim)
	return Clothing._finish(tool)


## Ombreira larga de camadas curvas que sobem em ponta (cavaleiro e mago): `height` controla a pontas.
static func plate_shoulder(frame: Clothing.Frame, shoulder: Vector3, side: float, color: Color, trim: Color, size: float, rise: float) -> ArrayMesh:
	var merged := ArrayMesh.new()
	var h := frame.height
	for layer in 3:
		var drop := h * 0.032 * layer
		var radius := h * (0.06 + layer * 0.011) * size
		var from := shoulder + Vector3(0, h * 0.04 - drop, 0) - frame.side * side * h * 0.006
		var to := shoulder + frame.side * (side * h * (0.034 + layer * 0.014) * size) + Vector3(0, h * 0.008 - drop, 0)
		var dome := Clothing._tube(frame, from, to, [[0.0, radius * 0.8], [0.45, radius], [0.9, radius * 0.72], [1.0, radius * 0.25]],
			color.lightened(0.05 * layer), trim, false)
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, dome.surface_get_arrays(0))
		var edge := Clothing._tube(frame, to - frame.side * side * h * 0.005, to, [[0.0, radius * 0.74], [1.0, radius * 0.72]], trim, trim, true)
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, edge.surface_get_arrays(0))
	if rise > 0.0:
		var base := shoulder + frame.side * (side * h * 0.04 * size) + Vector3(0, h * 0.06, 0)
		var blade := Clothing._tube(frame, base, base + Vector3(side * h * 0.03, h * rise, 0), [[0.0, h * 0.02], [0.6, h * 0.014], [1.0, 0.0]], trim, trim)
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, blade.surface_get_arrays(0))
	return merged


## Ombreira de folhas (elfo): leques de lâminas que se abrem para cima e para fora.
static func leaf_shoulder(frame: Clothing.Frame, shoulder: Vector3, side: float, color: Color, trim: Color) -> ArrayMesh:
	var tool := Clothing._tool()
	var h := frame.height
	for k in 5:
		var angle := lerpf(-0.2, 1.0, float(k) / 4.0)
		var length := h * (0.09 - 0.008 * k)
		var base := shoulder + Vector3(0, h * 0.04, 0) + frame.side * (side * h * 0.01)
		var dir := (frame.side * (side * sin(angle)) + Vector3(0, cos(angle) * 0.7 + 0.3, 0)).normalized()
		var across := frame.forward * (h * 0.028)
		var tip := base + dir * length
		var mid := base + dir * length * 0.5
		var tint := color.lightened(0.05 * k) if k % 2 == 0 else color
		Clothing._quad(tool, base - across * 0.4, base + across * 0.4, mid + across, mid - across, tint)
		Clothing._quad(tool, mid - across, mid + across, tip, tip, trim if k == 4 else tint.lightened(0.1))
	return Clothing._finish(tool)


## Colar de contas (osso, dentes, pedras) em volta do pescoço, com um pingente na frente.
static func necklace(frame: Clothing.Frame, y: float, bead: Color, pendant: Color, count: int, drop: float) -> ArrayMesh:
	var merged := ArrayMesh.new()
	var h := frame.height
	var ring := _ring_for(frame, y, h * 0.012)
	for i in count:
		var angle := lerpf(-1.2, 1.2, float(i) / (count - 1))
		var sag := drop * (1.0 - absf(angle) / 1.3)
		var p: Vector3 = Clothing._ring_point(frame, ring, angle, h * 0.006) - Vector3(0, sag * h, 0)
		var bead_mesh := Clothing._tube(frame, p - Vector3(0, h * 0.011, 0), p + Vector3(0, h * 0.011, 0), [[0.0, h * 0.006], [0.5, h * 0.0085], [1.0, h * 0.006]], bead, bead)
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, bead_mesh.surface_get_arrays(0))
	var front: Vector3 = Clothing._ring_point(frame, ring, 0.0, h * 0.01) - Vector3(0, drop * h + h * 0.02, 0)
	var gem := gem_mesh(frame, front, h * 0.022, pendant)
	merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, gem.surface_get_arrays(0))
	return merged


## Gema facetada (losango em pé, dois lados).
static func gem_mesh(frame: Clothing.Frame, centre: Vector3, size: float, color: Color) -> ArrayMesh:
	var tool := Clothing._tool()
	var up := Vector3(0, size * 1.3, 0)
	var w := frame.side * size
	var d := frame.forward * (size * 0.5)
	for sign in [1.0, -1.0]:
		var depth: Vector3 = d * sign
		Clothing._quad(tool, centre + up + depth * 0.2, centre + w + depth, centre - up + depth * 0.2, centre - w + depth, color.lightened(0.12 if sign > 0 else -0.1))
	return Clothing._finish(tool)


## Gola de pelo: anel grosso e irregular nos ombros (o manto de pele do Invocador).
static func fur_mantle(frame: Clothing.Frame, y: float, color: Color, tip: Color) -> ArrayMesh:
	var tool := Clothing._tool()
	var h := frame.height
	var rows := 4
	var rings: Array = []
	for j in rows + 1:
		var t := float(j) / rows
		var s := Clothing._slice(frame, y - h * 0.06 * t, h * 0.2)
		var spread := h * (0.035 + 0.05 * t)
		rings.append({"y": y - h * 0.06 * t, "half": s.x + h * 0.05 + spread, "front": s.y + h * 0.03 + spread * 0.6, "back": s.z - h * 0.03 - spread * 0.6})
	for j in rows:
		for i in 40:
			var a0 := TAU * i / 40
			var a1 := TAU * (i + 1) / 40
			var jitter := 0.5 + 0.5 * sin(i * 2.3 + j)
			var tint := color.lerp(tip, 0.25 * jitter + 0.2 * float(j) / rows)
			var p0: Vector3 = Clothing._ring_point(frame, rings[j], a0)
			var p1: Vector3 = Clothing._ring_point(frame, rings[j], a1)
			var q0: Vector3 = Clothing._ring_point(frame, rings[j + 1], a0, h * 0.02 * jitter)
			var q1: Vector3 = Clothing._ring_point(frame, rings[j + 1], a1, h * 0.02 * (1.0 - jitter))
			q0.y -= h * 0.012 * jitter
			q1.y -= h * 0.012 * (1.0 - jitter)
			Clothing._quad(tool, p0, p1, q1, q0, tint)
	return Clothing._finish(tool)


## Penas penduradas (cada uma uma lâmina estreita), a partir de um ponto.
static func feathers(frame: Clothing.Frame, at: Vector3, count: int, length: float, colors: Array) -> ArrayMesh:
	var tool := Clothing._tool()
	for k in count:
		var base := at + frame.side * ((k - (count - 1) * 0.5) * length * 0.18)
		var tip := base + Vector3(0, -length * (0.8 + 0.2 * sin(k * 2.0)), 0) + frame.forward * length * 0.05
		var w := frame.forward * (length * 0.07)
		var tint: Color = colors[k % colors.size()]
		Clothing._quad(tool, base - w, base + w, tip + w * 0.3, tip - w * 0.3, tint)
		Clothing._quad(tool, base - w * 0.2, base + w * 0.2, tip + w * 0.05, tip - w * 0.05, tint.darkened(0.35))
	return Clothing._finish(tool)


## Coroa de chifres curvos (Invocador de rank S) sobre uma tiara.
static func horn_crown(frame: Clothing.Frame, centre: Vector3, radius: float, color: Color, glow: Color) -> ArrayMesh:
	var merged := ArrayMesh.new()
	var h := frame.height
	var band := Clothing._tube(frame, centre + Vector3(0, radius * 0.15, 0), centre + Vector3(0, radius * 0.4, 0), [[0.0, radius * 0.7], [1.0, radius * 0.7]], color, glow, true)
	merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, band.surface_get_arrays(0))
	for side in [1.0, -1.0]:
		for k in 2:
			var points := [Vector3(0.05, 0.04, 0.0), Vector3(0.09, 0.08, 0.0), Vector3(0.11, 0.15, 0.0), Vector3(0.09, 0.22, 0.0)]
			var shift := 0.045 * k * (1.0 if k == 1 else 0.0)
			for i in points.size() - 1:
				var a: Vector3 = centre + frame.side * (side * h * (points[i].x + shift)) + Vector3(0, h * (points[i].y + 0.03 * k), 0) + frame.forward * (h * 0.02 * k)
				var b: Vector3 = centre + frame.side * (side * h * (points[i + 1].x + shift)) + Vector3(0, h * (points[i + 1].y + 0.03 * k), 0) + frame.forward * (h * 0.02 * k)
				var segment := Clothing._tube(frame, a, b, [[0.0, h * (0.014 - i * 0.003)], [1.0, h * maxf(0.014 - (i + 1) * 0.003, 0.002)]], color.lightened(0.12 * i), color)
				merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, segment.surface_get_arrays(0))
	return merged


## Cristais em leque nos ombros (Mago de rank S): lâminas altas que apontam para cima e para fora.
static func crystal_fan(frame: Clothing.Frame, shoulder: Vector3, side: float, color: Color) -> ArrayMesh:
	var tool := Clothing._tool()
	var h := frame.height
	for k in 4:
		var angle := lerpf(0.0, 0.9, float(k) / 3.0)
		var base := shoulder + Vector3(0, h * 0.05, 0) + frame.side * (side * h * (0.03 + 0.012 * k))
		var tip := base + (frame.side * (side * sin(angle)) + Vector3(0, cos(angle), 0)) * h * (0.12 - 0.012 * k)
		var w := frame.forward * (h * 0.012)
		var mid := (base + tip) * 0.5 + frame.side * side * h * 0.006
		Clothing._quad(tool, base - w, base + w, mid + w * 1.4, mid - w * 1.4, color)
		Clothing._quad(tool, mid - w * 1.4, mid + w * 1.4, tip, tip, color.lightened(0.25))
	return Clothing._finish(tool)


## Capuz de pano com gola alta (cowl) caindo sobre os ombros.
static func cowl(frame: Clothing.Frame, origin: Vector3, radius: float, color: Color, trim: Color, drop: float) -> ArrayMesh:
	var h := frame.height
	return Clothing._tube(frame, origin + Vector3(0, h * 0.03, 0), origin - Vector3(0, drop * h, 0),
		[[0.0, radius * 0.95], [0.45, radius * 1.25], [1.0, radius * 1.9]], color, trim, true)


## Aro de metal no tornozelo ou punho: tubo curto e justo.
static func cuff(frame: Clothing.Frame, a: Vector3, b: Vector3, radius: float, color: Color, trim: Color) -> ArrayMesh:
	return Clothing._tube(frame, a, b, [[0.0, radius * 1.05], [0.5, radius * 1.15], [1.0, radius * 1.05]], color, trim, true)


static func _ring_for(frame: Clothing.Frame, y: float, margin: float) -> Dictionary:
	var s := Clothing._slice(frame, y, frame.height * 0.135)
	return {"y": y, "half": s.x + margin, "front": s.y + margin, "back": s.z - margin}
