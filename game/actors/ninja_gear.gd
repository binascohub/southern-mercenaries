# Southern Mercenaries — GPL-3.0-or-later
class_name NinjaGear
extends RefCounted
## Roupas e armadura do Ninja (assassino) por rank, de D (a mais simples) a S (a mais rara e melhor),
## no corpo masculino (referência do autor). Cada peça troca separadamente: corpo, cabeça, mãos
## e pés. A base é o conjunto do Camponês (D) ou do Patrulheiro (C a S) tingido de cada rank, e o
## que muda de rank para rank é montado por código (malhas presas aos ossos, com tecido, couro, malha
## de aço e chapa pintados por PaintedTextures), como Clothing.
##   D  colete rasgado de pano cinza, corda na cintura
##   C  capuz cinza, faixas de couro nos antebraços, cinto marrom
##   B  capuz e tabardo azuis, mangas de malha de aço, lâminas nos antebraços
##   A  armadura de lâminas escura (estilo samurai): ombreiras, placas no peito e na cintura, máscara
##   S  armadura negra e roxa ornamentada: chifres, espinhos, capa e luzes roxas

const RANKS: Array[String] = ["D", "C", "B", "A", "S"]
## Material (tiers de 05-itens-e-loot.md) -> rank. Pano e ferro dividem o D (mesma faixa de nível).
const RANK_OF_MATERIAL := {"cloth": "D", "iron": "D", "steel": "C", "copper": "B", "silver": "A", "gold": "S"}
const SLOTS: Array[String] = ["body", "head", "hands", "feet"]
const META := "ninja_gear_nodes"

## Cor principal, de acabamento (couro, aço) e de destaque de cada rank.
const PALETTE := {
	"D": {"main": Color(0.3, 0.29, 0.28), "trim": Color(0.45, 0.37, 0.26), "glow": Color(0, 0, 0)},
	"C": {"main": Color(0.27, 0.27, 0.28), "trim": Color(0.36, 0.24, 0.14), "glow": Color(0, 0, 0)},
	"B": {"main": Color(0.13, 0.19, 0.36), "trim": Color(0.55, 0.57, 0.6), "glow": Color(0, 0, 0)},
	"A": {"main": Color(0.17, 0.16, 0.16), "trim": Color(0.34, 0.22, 0.12), "glow": Color(0, 0, 0)},
	"S": {"main": Color(0.1, 0.08, 0.13), "trim": Color(0.5, 0.2, 0.75), "glow": Color(0.7, 0.3, 1.0)},
}
const HEAD_BONES := ["Head_2", "head", "Head"]


## Só o Ninja masculino tem os conjuntos por rank por enquanto (o feminino e as outras classes vêm depois).
static func has_gear(class_id: String, _sex: String) -> bool:
	return class_id == "ninja"


static func rank_of(material: String) -> String:
	return String(RANK_OF_MATERIAL.get(material, "D"))


## Veste o modelo: `ranks` = {body, head, hands, feet} com o rank de cada peça ("" = sem a peça).
static func apply(model: HeroModel, ranks: Dictionary) -> void:
	clear(model)
	if model.is_suit():  # o corpo próprio do Ninja só muda a cor do tecido
		model.dress_suit(ranks)
		return
	model.set_outfit({})  # volta ao corpo de base (cabelo, texturas) antes de vestir
	var skeleton := model.skeleton
	if skeleton == null:
		return
	var body: String = ranks.get("body", "")
	var head: String = ranks.get("head", "")
	var hands: String = ranks.get("hands", "")
	var feet: String = ranks.get("feet", "")
	_base(model, body, head, hands, feet)
	var frame := Clothing._measure(model, skeleton, Clothing.HERO_BONES)
	var made: Array[Node] = []
	if body != "":
		made.append_array(_body(skeleton, frame, body))
	if head != "":
		made.append_array(_head(skeleton, frame, head))
	if hands != "":
		made.append_array(_hands(skeleton, frame, hands))
	if feet != "":
		made.append_array(_feet(skeleton, frame, feet))
	model.set_meta(META, made)


static func clear(model: HeroModel) -> void:
	for holder: Node in model.get_meta(META, []):
		if is_instance_valid(holder):
			holder.queue_free()
	model.set_meta(META, [])


## O corpo por baixo: Camponês no D, Patrulheiro nos outros; cada parte tingida do rank da sua peça.
static func _base(model: HeroModel, body: String, head: String, hands: String, feet: String) -> void:
	var used := body if body != "" else (hands if hands != "" else feet)
	var peasant := used == "D" or used == ""
	model.hide_clothes()
	var prefix := "Peasant" if peasant else "Ranger"
	var dim := 1.0 if peasant else 2.0  # o conjunto sem textura fica mais claro que o de pano: escurece
	var body_tint: Color = PALETTE[body if body != "" else "D"].main * dim
	for part in ["_Body", "_Legs"]:
		model.show_part(prefix + part, body_tint, not peasant)
	if not peasant:
		for belt in ["Ranger_Body_Belt_1", "Ranger_Body_Belt_2"]:
			model.show_part(belt, PALETTE[body if body != "" else "C"].trim, true)
	model.show_part(prefix + "_Arms", PALETTE[hands if hands != "" else (body if body != "" else "D")].main * dim, not peasant)
	for boots in ["Peasant_Feet"] if feet == "" or feet == "D" else ["Ranger_Feet_Boots", "Ranger_Feet"]:
		model.show_part(boots, PALETTE[feet if feet != "" else "D"].main * 1.7 if boots.begins_with("Ranger") else PALETTE["D"].trim.darkened(0.2), boots.begins_with("Ranger"))
	if head in ["C", "B", "A"]:
		model.show_part("Ranger_Head_Hood", PALETTE[head].main * 1.9, true)
		model.hide_hair()
	elif head == "S":
		model.hide_hair()
	if head == "A" or head == "S":
		pass


# --- Corpo -------------------------------------------------------------------

static func _body(skeleton: Skeleton3D, frame: Clothing.Frame, rank: String) -> Array[Node]:
	var colors: Dictionary = PALETTE[rank]
	var main: Color = colors.main
	var trim: Color = colors.trim
	var h := frame.height
	var waist := h * 0.52
	var chest := h * 0.72
	var made: Array[Node] = []
	match rank:
		"D":
			# Colete aberto de pano rasgado, preso por uma corda.
			# Colete sem mangas por cima da camisa: dois painéis na frente (aberto no meio) e um atrás.
			for side in [-1.0, 1.0]:
				made.append(_attach(skeleton, "spine_03", _panel(frame, chest + h * 0.025, h * 0.25, h * 0.045, true, main.darkened(0.25), trim, side * h * 0.052, false), "cloth", 0.7))
			made.append(_attach(skeleton, "spine_03", _panel(frame, chest + h * 0.025, h * 0.25, h * 0.1, false, main.darkened(0.25), trim, 0.0, false), "cloth", 0.7))
			made.append(_attach(skeleton, "pelvis", _hem(frame, waist, h * 0.2, main, 9), "cloth", 0.7))
			made.append(_attach(skeleton, "pelvis", Clothing._belt(frame, waist, h * 0.03, trim), "leather", 0.4))
		"C":
			made.append(_attach(skeleton, "pelvis", Clothing._belt(frame, waist, h * 0.045, trim), "leather", 0.5))
			made.append(_attach(skeleton, "pelvis", _hem(frame, waist, h * 0.24, main, 7), "cloth", 0.7))
		"B":
			# Tabardo azul na frente e atrás, com a faixa de aço na cintura.
			made.append(_attach(skeleton, "spine_03", _panel(frame, chest, h * 0.28, h * 0.075, true, main, trim), "cloth", 0.7))
			made.append(_attach(skeleton, "spine_03", _panel(frame, chest, h * 0.28, h * 0.075, false, main, trim), "cloth", 0.7))
			made.append(_attach(skeleton, "pelvis", _band(frame, waist, h * 0.045, main.darkened(0.45), h * 0.016), "leather", 0.5))
			made.append(_attach(skeleton, "pelvis", _buckle(frame, waist, trim, h), "metal", 0.6))
		"A", "S":
			# Armadura de lâminas: faixas de chapa no tronco, saia de placas e ombreiras.
			var plate := Color(0.2, 0.19, 0.19) if rank == "A" else Color(0.12, 0.1, 0.15)
			for i in 6:
				var y := lerpf(waist - h * 0.01, chest - h * 0.015, float(i) / 5.0)
				var bone := "spine_03" if i > 1 else "pelvis"
				# Cada lâmina é mais alta que o espaço e abre um pouco embaixo: as camadas se sobrepõem.
				made.append(_attach(skeleton, bone, _band(frame, y, h * 0.042, plate.lightened(0.06 * (i % 2)), h * 0.014, h * 0.008), "metal", 1.0))
				made.append(_attach(skeleton, bone, _band(frame, y - h * 0.02, h * 0.006, trim, h * 0.021), "leather", 0.4))
			made.append(_attach(skeleton, "spine_03", _cords(frame, waist - h * 0.03, chest, trim, h), "leather", 0.4))
			made.append(_attach(skeleton, "pelvis", Clothing._belt(frame, waist - h * 0.015, h * 0.05, trim.darkened(0.3)), "leather", 0.5))
			made.append(_attach(skeleton, "pelvis", _skirt_plates(frame, waist - h * 0.02, h * 0.2, plate, trim, 12 if rank == "A" else 14, rank == "S"), "metal", 1.0))
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				var origin := skeleton.get_bone_global_rest(skeleton.find_bone(up)).origin
				made.append(_attach(skeleton, up, _pauldron(frame, origin, side, plate, trim, rank == "S"), "metal", 1.0))
			if rank == "S":
				made.append(_attach(skeleton, "spine_03", _cape(frame, chest + h * 0.01, h * 0.4, Color(0.05, 0.035, 0.07), trim), "cloth", 0.8))
				made.append(_attach_glow(skeleton, "spine_03", _chest_lines(frame, chest, waist, trim), colors.glow))
	return made


## Barra rasgada de pano (tiras de tamanhos diferentes em volta do quadril).
static func _hem(frame: Clothing.Frame, y: float, length: float, color: Color, strips: int) -> ArrayMesh:
	var tool := Clothing._tool()
	var margin := frame.height * 0.014
	var ring := _ring(frame, y, margin)
	var count := strips * 2
	for i in count:
		var a0 := TAU * i / count
		var a1 := TAU * (i + 0.9) / count
		var drop := length * (0.55 + 0.45 * absf(sin(i * 2.7)))
		var p0 := Clothing._ring_point(frame, ring, a0)
		var p1 := Clothing._ring_point(frame, ring, a1)
		var out := (Vector3(p0.x - frame.centre.x, 0, p0.z - frame.centre.z)).normalized() * frame.height * 0.02
		Clothing._quad(tool, p0, p1, p1 + out - Vector3(0, drop * 0.92, 0), p0 + out - Vector3(0, drop, 0), color.darkened(0.12 * (i % 3)))
	return Clothing._finish(tool)


## Faixa horizontal em volta do tronco, na altura `y` (sem as pontas de nó).
static func _band(frame: Clothing.Frame, y: float, band: float, color: Color, margin: float, flare := 0.0) -> ArrayMesh:
	var tool := Clothing._tool()
	var bottom := _ring(frame, y - band * 0.5, margin + flare)
	var top := _ring(frame, y + band * 0.5, margin)
	for i in Clothing.SIDES:
		var a0 := TAU * i / Clothing.SIDES
		var a1 := TAU * (i + 1) / Clothing.SIDES
		Clothing._quad(tool, Clothing._ring_point(frame, bottom, a0), Clothing._ring_point(frame, bottom, a1),
			Clothing._ring_point(frame, top, a1), Clothing._ring_point(frame, top, a0), color)
	return Clothing._finish(tool)


## Painel pendurado dos ombros (tabardo), na frente ou atrás: acompanha o corpo linha por linha
## (peito, barriga, coxas) e se afasta um pouco na barra, com um filete e um losango de acabamento.
static func _panel(frame: Clothing.Frame, y: float, length: float, half: float, front: bool, color: Color, trim: Color, offset := 0.0, emblem := true) -> ArrayMesh:
	var tool := Clothing._tool()
	var rows := 8
	var margin := frame.height * 0.012
	var points: Array = []
	for j in rows + 1:
		var t := float(j) / rows
		var row_y := y - length * t
		var s := Clothing._slice(frame, row_y, frame.height * 0.135)
		var depth := (s.y + margin) if front else (s.z - margin)
		var swing := frame.height * (0.045 * t * t)
		depth += swing if front else -swing
		var w := half * (1.0 + t * 0.3)
		var centre := frame.centre + frame.forward * depth + frame.side * offset
		points.append([Vector3(centre.x, row_y, centre.z) - frame.side * w, Vector3(centre.x, row_y, centre.z) + frame.side * w])
	for j in rows:
		var shade := color if j < rows - 1 else trim
		Clothing._quad(tool, points[j][0], points[j][1], points[j + 1][1], points[j + 1][0], shade)
	# Filetes laterais e losango no peito do painel.
	for side in [0, 1]:
		for j in rows - 1:
			var a: Vector3 = points[j][side]
			var b: Vector3 = points[j + 1][side]
			var edge: Vector3 = frame.side * (frame.height * 0.006) * (1.0 if side == 0 else -1.0)
			Clothing._quad(tool, a, a + edge, b + edge, b, trim)
	if front and emblem:
		var mid: Vector3 = (points[2][0] + points[2][1]) * 0.5 + frame.forward * (frame.height * 0.003)
		var r := frame.height * 0.028
		Clothing._quad(tool, mid + Vector3(0, r, 0), mid + frame.side * r, mid - Vector3(0, r, 0), mid - frame.side * r, trim)
	return Clothing._finish(tool)


## Saia de placas penduradas do quadril (cada uma uma lâmina inclinada para fora).
static func _skirt_plates(frame: Clothing.Frame, y: float, length: float, color: Color, trim: Color, count: int, spiked: bool) -> ArrayMesh:
	var tool := Clothing._tool()
	var ring := _ring(frame, y, frame.height * 0.02)
	for i in count:
		var a0 := TAU * (i + 0.04) / count
		var a1 := TAU * (i + 0.96) / count
		var p0 := Clothing._ring_point(frame, ring, a0)
		var p1 := Clothing._ring_point(frame, ring, a1)
		var out0 := Vector3(p0.x - frame.centre.x, 0, p0.z - frame.centre.z).normalized() * frame.height * 0.04
		var out1 := Vector3(p1.x - frame.centre.x, 0, p1.z - frame.centre.z).normalized() * frame.height * 0.04
		var tint := color.lightened(0.05 * (i % 2))
		var mid := (p0 + p1) * 0.5 + (out0 + out1) * 0.5 - Vector3(0, length, 0)
		Clothing._quad(tool, p0, p1, p1 + out1 - Vector3(0, length * 0.55, 0), p0 + out0 - Vector3(0, length * 0.55, 0), tint)
		Clothing._quad(tool, p0 + out0 - Vector3(0, length * 0.55, 0), p1 + out1 - Vector3(0, length * 0.55, 0),
			mid + (out0 + out1) * 0.25 + (p1 - p0) * 0.35, mid + (out0 + out1) * 0.25 - (p1 - p0) * 0.35, trim.darkened(0.3))
		if spiked:
			var tip := mid + (out0 + out1) * 0.6 - Vector3(0, length * 0.12, 0)
			Clothing._quad(tool, mid + (p1 - p0) * 0.3, mid - (p1 - p0) * 0.3, tip, tip, trim)
	return Clothing._finish(tool)


## Ombreira de três lâminas curvas e fechadas (cúpulas que se sobrepõem do ombro para o braço);
## a de rank S tem espinhos roxos.
static func _pauldron(frame: Clothing.Frame, shoulder: Vector3, side: float, color: Color, trim: Color, spiked: bool) -> ArrayMesh:
	var merged := ArrayMesh.new()
	var h := frame.height
	for layer in 3:
		var drop := h * 0.03 * layer
		var radius := h * (0.056 + layer * 0.01)
		var from := shoulder + Vector3(0, h * 0.034 - drop, 0) - frame.side * side * h * 0.004
		var to := shoulder + frame.side * (side * h * (0.03 + layer * 0.012)) + Vector3(0, h * 0.01 - drop, 0)
		var mesh := Clothing._tube(frame, from, to, [[0.0, radius * 0.8], [0.45, radius], [0.9, radius * 0.7], [1.0, radius * 0.25]],
			color.lightened(0.05 * layer), trim, false)
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, mesh.surface_get_arrays(0))
		var rim := Clothing._tube(frame, to - frame.side * side * h * 0.004, to, [[0.0, radius * 0.72], [1.0, radius * 0.7]], trim, trim, true)
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, rim.surface_get_arrays(0))
	if spiked:
		for k in 3:
			var base := shoulder + frame.side * (side * h * 0.05) + frame.forward * (h * (k - 1) * 0.028) + Vector3(0, h * 0.05, 0)
			var spike := Clothing._tube(frame, base, base + Vector3(side * h * 0.025, h * 0.075, 0), [[0.0, h * 0.011], [1.0, 0.0]], trim, trim)
			merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, spike.surface_get_arrays(0))
	return merged


## Capa longa nas costas, presa nos ombros: estreita em cima, abre embaixo, com dobras e barra.
static func _cape(frame: Clothing.Frame, y: float, length: float, color: Color, trim: Color) -> ArrayMesh:
	var tool := Clothing._tool()
	var rows := 10
	var cols := 8
	var margin := frame.height * 0.016
	var grid: Array = []
	for j in rows + 1:
		var t := float(j) / rows
		var row_y := y - length * t
		var s := Clothing._slice(frame, row_y, frame.height * 0.135)
		var half := frame.height * (0.085 + 0.1 * t)
		var line: Array = []
		for i in cols + 1:
			var u := float(i) / cols * 2.0 - 1.0
			var fold := sin(u * 7.0 + t * 1.5) * frame.height * 0.01 * t
			var depth := s.z - margin - frame.height * 0.035 * t * t + fold
			var point := frame.centre + frame.forward * depth + frame.side * (u * half)
			line.append(Vector3(point.x, row_y, point.z))
		grid.append(line)
	for j in rows:
		var tint := trim if j == rows - 1 else color.lightened(0.02 * (j % 2))
		for i in cols:
			Clothing._quad(tool, grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i], tint)
	return Clothing._finish(tool)


## Fios de luz roxa sobre o peito da armadura S.
static func _chest_lines(frame: Clothing.Frame, chest: float, waist: float, color: Color) -> ArrayMesh:
	var tool := Clothing._tool()
	var margin := frame.height * 0.02
	var ring_top := _ring(frame, chest - frame.height * 0.01, margin)
	var ring_bottom := _ring(frame, waist + frame.height * 0.02, margin)
	for angle in [-0.35, 0.35, 0.0]:
		var a := Clothing._ring_point(frame, ring_top, angle)
		var b := Clothing._ring_point(frame, ring_bottom, angle * 0.6)
		var w := frame.side * (frame.height * 0.004)
		Clothing._quad(tool, a - w, a + w, b + w, b - w, color)
	return Clothing._finish(tool)


## Fivela quadrada na frente da cintura.
static func _buckle(frame: Clothing.Frame, y: float, color: Color, h: float) -> ArrayMesh:
	var tool := Clothing._tool()
	var ring := _ring(frame, y, h * 0.02)
	var c := Clothing._ring_point(frame, ring, 0.0, h * 0.004)
	var w := frame.side * (h * 0.022)
	var up := Vector3(0, h * 0.02, 0)
	Clothing._quad(tool, c - w - up, c + w - up, c + w + up, c - w + up, color)
	Clothing._quad(tool, c - w * 0.5 - up * 0.5, c + w * 0.5 - up * 0.5, c + w * 0.5 + up * 0.5, c - w * 0.5 + up * 0.5, color.darkened(0.55))
	return Clothing._finish(tool)


## Cordões verticais que prendem as lâminas da armadura (do peito à cintura).
static func _cords(frame: Clothing.Frame, y0: float, y1: float, color: Color, h: float) -> ArrayMesh:
	var tool := Clothing._tool()
	var bottom := _ring(frame, y0, h * 0.024)
	var top := _ring(frame, y1, h * 0.024)
	for k in 10:
		var angle := TAU * (k + 0.5) / 10.0
		var a := Clothing._ring_point(frame, bottom, angle)
		var b := Clothing._ring_point(frame, top, angle)
		var w := frame.side * (h * 0.0035)
		Clothing._quad(tool, a - w, a + w, b + w, b - w, color.darkened(0.2))
	return Clothing._finish(tool)


# --- Cabeça ------------------------------------------------------------------

static func _head(skeleton: Skeleton3D, frame: Clothing.Frame, rank: String) -> Array[Node]:
	var colors: Dictionary = PALETTE[rank]
	var main: Color = colors.main
	var trim: Color = colors.trim
	var h := frame.height
	var bone := _head_bone(skeleton)
	var made: Array[Node] = []
	if bone == "":
		return made
	var origin := skeleton.get_bone_global_rest(skeleton.find_bone(bone)).origin
	var centre := origin + Vector3(0, h * 0.075, 0)
	var radius := h * 0.08
	match rank:
		"B":
			# Gola de malha sobre os ombros, por baixo do capuz.
			made.append(_attach(skeleton, "spine_03", Clothing._tube(frame, origin + Vector3(0, h * 0.025, 0), origin - Vector3(0, h * 0.05, 0),
				[[0.0, radius * 0.95], [0.5, radius * 1.3], [1.0, radius * 1.75]], trim.darkened(0.25), trim, true), "chain", 0.5))
		"A":
			# Máscara de pano escuro cobrindo nariz e boca.
			var forward := frame.forward * (h * 0.01)
			made.append(_attach(skeleton, bone, Clothing._tube(frame, origin + forward + Vector3(0, h * 0.004, 0), origin + forward + Vector3(0, h * 0.04, 0),
				[[0.0, radius * 0.95], [0.5, radius * 1.0], [1.0, radius * 0.97]], main.darkened(0.2), main.darkened(0.45), true), "cloth", 0.5))
		"S":
			# Elmo com chifres e olhos de luz roxa.
			made.append(_attach(skeleton, bone, _dome(frame, centre, radius * 1.12, h * 0.002, main, trim), "metal", 1.0))
			for side in [1.0, -1.0]:
				made.append(_attach(skeleton, bone, _horn(frame, centre, side, trim, h), "metal", 1.0))
			made.append(_attach_glow(skeleton, bone, _eyes(frame, centre, radius, h), colors.glow))
	return made


static func _head_bone(skeleton: Skeleton3D) -> String:
	for candidate in HEAD_BONES:
		if skeleton.find_bone(candidate) >= 0:
			return candidate
	return ""


## Calota do elmo: meia esfera mais um aro e uma crista.
static func _dome(frame: Clothing.Frame, centre: Vector3, radius: float, lift: float, color: Color, trim: Color) -> ArrayMesh:
	var profile: Array = []
	for i in 9:
		var t := float(i) / 8.0
		profile.append([t, radius * sqrt(maxf(1.0 - t * t * 0.96, 0.0)) * (1.0 + 0.04 * sin(t * 6.0))])
	var dome := Clothing._tube(frame, centre - Vector3(0, radius * 0.45, 0), centre + Vector3(0, radius * 1.05, 0), profile, color, trim, false)
	var rim := Clothing._tube(frame, centre - Vector3(0, radius * 0.46, 0), centre - Vector3(0, radius * 0.3, 0), [[0.0, radius * 1.04], [1.0, radius * 1.02]], trim, trim, true)
	var crest := Clothing._tube(frame, centre + Vector3(0, radius * 0.9, 0) - frame.forward * radius * 0.7, centre + Vector3(0, radius * 1.15, 0) + frame.forward * radius * 0.4,
		[[0.0, radius * 0.06], [0.5, radius * 0.1], [1.0, radius * 0.02]], trim, trim)
	var merged := ArrayMesh.new()
	for source: ArrayMesh in [dome, rim, crest]:
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, source.surface_get_arrays(0))
	return merged


## Chifre curvo: três segmentos que afinam e viram para cima.
static func _horn(frame: Clothing.Frame, centre: Vector3, side: float, color: Color, h: float) -> ArrayMesh:
	var merged := ArrayMesh.new()
	var points := [Vector3(0.085, 0.03, 0.0), Vector3(0.125, 0.06, 0.0), Vector3(0.15, 0.115, 0.0), Vector3(0.14, 0.18, 0.0)]
	for i in points.size() - 1:
		var a: Vector3 = centre + frame.side * (side * h * points[i].x) + Vector3(0, h * points[i].y, 0)
		var b: Vector3 = centre + frame.side * (side * h * points[i + 1].x) + Vector3(0, h * points[i + 1].y, 0)
		var r0 := h * (0.016 - i * 0.004)
		var r1 := h * maxf(0.016 - (i + 1) * 0.004, 0.0015)
		var segment := Clothing._tube(frame, a, b, [[0.0, r0], [1.0, r1]], color.lightened(0.1 * i), color)
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, segment.surface_get_arrays(0))
	return merged


static func _eyes(frame: Clothing.Frame, centre: Vector3, radius: float, h: float) -> ArrayMesh:
	var tool := Clothing._tool()
	for side in [1.0, -1.0]:
		var c: Vector3 = centre + frame.forward * (radius * 1.12) + frame.side * (side * radius * 0.36) + Vector3(0, radius * 0.08, 0)
		var w := frame.side * (radius * 0.2)
		var up := Vector3(0, radius * 0.07, 0)
		Clothing._quad(tool, c - w - up, c + w - up * 0.2, c + w + up, c - w + up * 0.2, Color.WHITE)
	return Clothing._finish(tool)


# --- Mãos e pés ----------------------------------------------------------------

static func _hands(skeleton: Skeleton3D, frame: Clothing.Frame, rank: String) -> Array[Node]:
	var colors: Dictionary = PALETTE[rank]
	var trim: Color = colors.trim
	var main: Color = colors.main
	var h := frame.height
	var made: Array[Node] = []
	for side in [1.0, -1.0]:
		var suffix := "l" if side > 0 else "r"
		var up := "upperarm_" + suffix
		var low := "lowerarm_" + suffix
		var hand := "hand_" + suffix
		var shoulder := skeleton.get_bone_global_rest(skeleton.find_bone(up)).origin
		var elbow := skeleton.get_bone_global_rest(skeleton.find_bone(low)).origin
		var wrist := skeleton.get_bone_global_rest(skeleton.find_bone(hand)).origin
		var arm := h * 0.027
		match rank:
			"C":
				# Faixas de couro enroladas no antebraço e no pulso.
				for k in 4:
					var t0 := 0.18 + k * 0.2
					made.append(_attach(skeleton, low, Clothing._tube(frame, elbow.lerp(wrist, t0), elbow.lerp(wrist, t0 + 0.14),
						[[0.0, arm * 1.18], [1.0, arm * 1.18]], trim, trim.darkened(0.3), true), "leather", 0.4))
			"B":
				# Mangas de malha de aço do ombro ao pulso e uma lâmina presa ao antebraço.
				made.append(_attach(skeleton, up, Clothing._tube(frame, shoulder, elbow, [[0.0, arm * 1.35], [1.0, arm * 1.25]], Color(0.55, 0.57, 0.62), trim), "chain", 0.5))
				made.append(_attach(skeleton, low, Clothing._tube(frame, elbow, elbow.lerp(wrist, 0.92), [[0.0, arm * 1.25], [1.0, arm * 1.1]], Color(0.55, 0.57, 0.62), trim), "chain", 0.5))
				made.append(_attach(skeleton, low, _blade(frame, elbow.lerp(wrist, 0.45), wrist, side, h), "metal", 1.0))
			"A", "S":
				var plate := Color(0.2, 0.19, 0.19) if rank == "A" else Color(0.12, 0.1, 0.15)
				made.append(_attach(skeleton, low, Clothing._tube(frame, elbow.lerp(wrist, 0.05), wrist + (wrist - elbow).normalized() * h * 0.012,
					[[0.0, arm * 1.45], [0.55, arm * 1.25], [1.0, arm * 1.1]], plate, trim, true), "metal", 1.0))
				for k in 3:
					var t := 0.2 + k * 0.28
					made.append(_attach(skeleton, low, Clothing._tube(frame, elbow.lerp(wrist, t), elbow.lerp(wrist, t + 0.06),
						[[0.0, arm * 1.5], [1.0, arm * 1.5]], trim, trim.darkened(0.3), true), "leather", 0.4))
				if rank == "S":
					for k in 2:
						var base := elbow.lerp(wrist, 0.25 + k * 0.3) + Vector3(0, arm * 1.3, 0)
						made.append(_attach(skeleton, low, Clothing._tube(frame, base, base + Vector3(0, arm * 1.8, 0).rotated(Vector3.FORWARD, side * 0.5),
							[[0.0, arm * 0.3], [1.0, 0.0]], trim, trim), "metal", 1.0))
	return made


static func _feet(skeleton: Skeleton3D, frame: Clothing.Frame, rank: String) -> Array[Node]:
	var colors: Dictionary = PALETTE[rank]
	var trim: Color = colors.trim
	var h := frame.height
	var made: Array[Node] = []
	if rank == "D":
		return made
	for side in [1.0, -1.0]:
		var suffix := "l" if side > 0 else "r"
		var calf := "calf_" + suffix
		var foot := "foot_" + suffix
		var knee := skeleton.get_bone_global_rest(skeleton.find_bone(calf)).origin
		var ankle := skeleton.get_bone_global_rest(skeleton.find_bone(foot)).origin
		var leg := h * 0.032
		match rank:
			"C", "B":
				for k in 3:
					var t := 0.45 + k * 0.17
					made.append(_attach(skeleton, calf, Clothing._tube(frame, knee.lerp(ankle, t), knee.lerp(ankle, t + 0.11),
						[[0.0, leg * 1.06], [1.0, leg * 1.06]], trim, trim.darkened(0.3), true), "leather", 0.4))
			"A", "S":
				var plate := Color(0.2, 0.19, 0.19) if rank == "A" else Color(0.12, 0.1, 0.15)
				made.append(_attach(skeleton, calf, Clothing._tube(frame, knee.lerp(ankle, 0.1), knee.lerp(ankle, 0.92),
					[[0.0, leg * 1.12], [0.5, leg * 1.0], [1.0, leg * 1.1]], plate, trim, true), "metal", 1.0))
				if rank == "S":
					made.append(_attach(skeleton, calf, Clothing._tube(frame, knee, knee + frame.forward * h * 0.045,
						[[0.0, leg * 0.9], [1.0, 0.0]], trim, trim), "metal", 1.0))
	return made


## Lâmina curta presa ao antebraço, apontando para além da mão.
static func _blade(frame: Clothing.Frame, from: Vector3, wrist: Vector3, side: float, h: float) -> ArrayMesh:
	var tool := Clothing._tool()
	var axis := (wrist - from).normalized()
	var out := Vector3(0, 0, 1)
	var base := from + Vector3(0, h * 0.02, 0)
	var tip := wrist + axis * h * 0.14 + Vector3(0, h * 0.012, 0)
	var w := out * (h * 0.012)
	var steel := Color(0.72, 0.75, 0.8)
	Clothing._quad(tool, base - w, base + w, wrist + Vector3(0, h * 0.012, 0) + w, wrist + Vector3(0, h * 0.012, 0) - w, steel.darkened(0.25))
	Clothing._quad(tool, wrist + Vector3(0, h * 0.012, 0) - w, wrist + Vector3(0, h * 0.012, 0) + w, tip, tip, steel)
	return Clothing._finish(tool)


# --- Auxiliares ------------------------------------------------------------------

static func _ring(frame: Clothing.Frame, y: float, margin: float) -> Dictionary:
	var s := Clothing._slice(frame, y, frame.height * 0.135)
	return {"y": y, "half": s.x + margin, "front": s.y + margin, "back": s.z - margin}


static func _attach(skeleton: Skeleton3D, bone: String, mesh: ArrayMesh, kind: String, tile: float) -> Node:
	var piece := Clothing._attach(skeleton, bone, mesh, {"cloth": kind, "tile": tile})
	return piece.get_parent()


## Peça que brilha (olhos do elmo, fios de luz): cor própria sem sombreamento.
static func _attach_glow(skeleton: Skeleton3D, bone: String, mesh: ArrayMesh, color: Color) -> Node:
	var holder := BoneAttachment3D.new()
	holder.bone_name = bone
	skeleton.add_child(holder)
	var piece := MeshInstance3D.new()
	piece.mesh = mesh
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.albedo_color = color
	material.emission_enabled = true
	material.emission = color
	material.emission_energy_multiplier = 2.5
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	piece.material_override = material
	piece.transform = skeleton.get_bone_global_rest(skeleton.find_bone(bone)).affine_inverse()
	piece.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	holder.add_child(piece)
	return holder
