# Southern Mercenaries — GPL-3.0-or-later
class_name Clothing
extends RefCounted
## Roupas medievais montadas por código (malhas procedurais com o tecido pintado de
## PaintedTextures), presas aos ossos do esqueleto do modelo: vestidos longos com
## painel contrastante, cadarços e mangas (em sino, bufantes ou curtas), coletes,
## faixas, túnicas e camisas de linho com cadarço. As formas seguem as referências
## do autor (vestidos de gala, vestidos de linho, camisa e calça de camponês, colete
## laranja e túnica azul com faixa).
##
## As peças são construídas no espaço de repouso do esqueleto (o do modelo na pose de
## T) e presas a um osso com a transformação inversa do repouso dele: no repouso ficam
## onde foram desenhadas e depois acompanham o osso. Medidas do corpo vêm das malhas.

const SIDES := 96  ## segmentos em volta de cada peça
## Ossos do esqueleto dos heróis (Universal Animation Library).
const HERO_BONES := {"hips": "pelvis", "chest": "spine_03", "upper_l": "upperarm_l", "upper_r": "upperarm_r",
	"lower_l": "lowerarm_l", "lower_r": "lowerarm_r", "hand_l": "hand_l", "hand_r": "hand_r"}

## Cor de um painel/trim nas malhas (cor por vértice, multiplicada pela textura).
class Frame:
	var skeleton: Skeleton3D
	var forward := Vector3.BACK
	var side := Vector3.RIGHT  ## do lado direito do personagem para o esquerdo
	var centre := Vector3.ZERO  ## no eixo do corpo, na altura de y = 0
	var vertices := PackedVector3Array()
	var height := 1.0


# --- API ---------------------------------------------------------------------

## Veste o modelo (um Node3D com um Skeleton3D) conforme `style`; os ossos vêm de `bones`
## ({hips, chest, upper_l, upper_r, lower_l, lower_r, hand_l, hand_r}). Retorna as peças.
static func dress(model: Node, bones: Dictionary, style: Dictionary) -> Array[MeshInstance3D]:
	var skeleton := model.find_child("Skeleton3D", true, false) as Skeleton3D
	var made: Array[MeshInstance3D] = []
	if skeleton == null:
		return made
	var frame := _measure(model, skeleton, bones)
	var kind := String(style.get("kind", "gown"))
	var body: Color = style.get("body", Color(0.5, 0.1, 0.1))
	var panel: Color = style.get("panel", body)
	var trim: Color = style.get("trim", Color(0.8, 0.65, 0.25))
	var scale := frame.height / 9.0  ## as medidas abaixo foram feitas para o corpo de 9 unidades
	var top: Color = style.get("top", body)  ## corpete e mangas (a saia usa `body`)
	var rest := func(bone: String) -> Vector3: return skeleton.get_bone_global_rest(skeleton.find_bone(bone)).origin
	var hips: Vector3 = rest.call(bones.hips)
	var chest_y := float(style.get("chest_y", 7.0)) * scale
	var waist_y := float(style.get("waist_y", 4.7)) * scale
	var floor_y := float(style.get("floor_y", 0.18)) * scale
	if kind == "gown":
		var torso := _torso(frame, waist_y, chest_y, top, style.get("top", panel), trim, bool(style.get("laced", true)), style.get("lace", trim))
		for piece in torso:
			made.append(_attach(skeleton, bones.chest, piece, style))
		made.append(_attach(skeleton, bones.get("skirt", bones.hips), _skirt(frame, waist_y, floor_y, body, panel, trim, float(style.get("flare", 1.0)), float(style.get("panel_angle", 28.0))), style))
		for side_sign in [1.0, -1.0]:
			var up := String(bones.upper_l if side_sign > 0 else bones.upper_r)
			var low := String(bones.lower_l if side_sign > 0 else bones.lower_r)
			var hand := String(bones.hand_l if side_sign > 0 else bones.hand_r)
			var sleeve := String(style.get("sleeve", "bell"))
			var pieces := _sleeves(frame, rest.call(up), rest.call(low), rest.call(hand), sleeve, top, trim, scale)
			made.append(_attach(skeleton, up, pieces[0], style))
			if pieces.size() > 1:
				made.append(_attach(skeleton, low, pieces[1], style))
	elif kind == "vest":
		# Colete aberto na frente, amarrado com tiras, e uma faixa na cintura (referência 5).
		var vest := _torso(frame, waist_y, chest_y, body, panel, trim, true, style.get("lace", trim), true)
		for piece in vest:
			made.append(_attach(skeleton, bones.chest, piece, style))
		made.append(_attach(skeleton, bones.hips, _belt(frame, waist_y + frame.height * 0.02, frame.height * 0.035, style.get("belt", trim)), style))
	elif kind == "robe":
		# Túnica longa transpassada, de mangas largas, com uma faixa de couro (referência 6).
		var robe := _torso(frame, waist_y, chest_y, body, body, body, false, trim, true)
		for piece in robe:
			made.append(_attach(skeleton, bones.chest, piece, style))
		made.append(_attach(skeleton, bones.hips, _skirt(frame, waist_y, frame.height * float(style.get("hem", 0.18)), body, body, body, 0.75, 0.0, true), style))
		made.append(_attach(skeleton, bones.hips, _belt(frame, waist_y + frame.height * 0.015, frame.height * 0.06, style.get("belt", Color(0.3, 0.2, 0.14))), style))
		for side_sign in [1.0, -1.0]:
			var up := String(bones.upper_l if side_sign > 0 else bones.upper_r)
			var low := String(bones.lower_l if side_sign > 0 else bones.lower_r)
			var hand := String(bones.hand_l if side_sign > 0 else bones.hand_r)
			var pieces := _sleeves(frame, rest.call(up), rest.call(low), rest.call(hand), "wide", body, trim, scale)
			made.append(_attach(skeleton, up, pieces[0], style))
			made.append(_attach(skeleton, low, pieces[1], style))
	elif kind == "laced_shirt":
		# Camisa de linho com cadarço no decote e punhos escuros (referência 4): só os detalhes
		# por cima da camisa do corpo.
		made.append(_attach(skeleton, bones.chest, _neck_lacing(frame, chest_y, style.get("lace", Color(0.32, 0.25, 0.18))), style))
		for side_sign in [1.0, -1.0]:
			var low := String(bones.lower_l if side_sign > 0 else bones.lower_r)
			var hand := String(bones.hand_l if side_sign > 0 else bones.hand_r)
			var elbow: Vector3 = rest.call(low)
			var wrist: Vector3 = rest.call(hand)
			made.append(_attach(skeleton, low, _tube(frame, elbow.lerp(wrist, 0.82), wrist, [[0.0, 0.0325 * frame.height], [1.0, 0.0315 * frame.height]], trim, trim), style))
	return made


# --- Medidas -----------------------------------------------------------------

static func _measure(model: Node, skeleton: Skeleton3D, bones: Dictionary) -> Frame:
	var frame := Frame.new()
	frame.skeleton = skeleton
	var left: Vector3 = skeleton.get_bone_global_rest(skeleton.find_bone(bones.upper_l)).origin
	var right: Vector3 = skeleton.get_bone_global_rest(skeleton.find_bone(bones.upper_r)).origin
	frame.side = (left - right).normalized()
	frame.forward = frame.side.cross(Vector3.UP).normalized()
	var hips: Vector3 = skeleton.get_bone_global_rest(skeleton.find_bone(bones.hips)).origin
	frame.centre = Vector3(hips.x, 0.0, hips.z)
	var low := INF
	var high := -INF
	var all := PackedVector3Array()
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := (node as MeshInstance3D).mesh
		if mesh == null or not (node as MeshInstance3D).visible:
			continue
		for surface in mesh.get_surface_count():
			var verts: PackedVector3Array = mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
			all.append_array(verts)
			for v in verts:
				low = minf(low, v.y)
				high = maxf(high, v.y)
	# O corpo até o topo da cabeça (o cabelo alto pode passar um pouco).
	frame.height = maxf(high - minf(low, 0.0), 0.5)
	# Só o tronco interessa às medidas (sem os braços e a cabeça), de 2 em 2 vértices.
	var limit := frame.height * 0.14
	for i in range(0, all.size(), 1):
		var offset := all[i] - frame.centre
		if all[i].y > frame.height * 0.15 and all[i].y < frame.height * 0.85 and absf(offset.dot(frame.side)) < limit:
			frame.vertices.append(all[i])
	return frame


## Meia-largura, profundidade à frente e atrás (a partir do eixo do corpo) da silhueta do
## tronco na altura `y`; ignora os braços (fora de `limit` do eixo).
static func _slice(frame: Frame, y: float, limit: float) -> Vector3:
	var window := frame.height * 0.02
	for attempt in 4:
		var half := 0.0
		var front := 0.0
		var back := 0.0
		var found := 0
		for v in frame.vertices:
			if absf(v.y - y) > window:
				continue
			var offset := v - frame.centre
			var lateral := offset.dot(frame.side)
			if absf(lateral) > limit:
				continue
			found += 1
			half = maxf(half, absf(lateral))
			front = maxf(front, offset.dot(frame.forward))
			back = minf(back, offset.dot(frame.forward))
		if found >= 6:
			return Vector3(half, front, back)
		window *= 2.0  # pouca malha nesta altura (herói): olha uma faixa maior
	return Vector3(frame.height * 0.1, frame.height * 0.06, -frame.height * 0.06)


# --- Peças -------------------------------------------------------------------

## Corpete: tubo justo da cintura ao peito, com o painel da frente em outra cor, as
## bordas douradas e os cadarços cruzados.
static func _torso(frame: Frame, y0: float, y1: float, body: Color, panel: Color, trim: Color, laced: bool, lace: Color, open_front := false) -> Array[ArrayMesh]:
	var levels := 7
	var margin := frame.height * 0.006
	var limit := frame.height * 0.135
	var rings: Array = []
	for j in levels + 1:
		var y := lerpf(y0, y1, float(j) / levels)
		var s := _slice(frame, y, limit)
		rings.append({"y": y, "half": s.x + margin, "front": s.y + margin, "back": s.z - margin})
	var tool := _tool()
	var panel_half := deg_to_rad(24.0)
	for j in levels:
		for i in SIDES:
			var a0 := TAU * i / SIDES
			var a1 := TAU * (i + 1) / SIDES
			var mid := wrapf(0.5 * (a0 + a1) + PI, 0.0, TAU) - PI  # 0 = frente
			var color := body
			if open_front:
				# Abertura em V: larga no peito, fechando para a cintura.
				# Só o decote em V: fechado até pouco abaixo do meio e abrindo para o pescoço.
				var open_t := clampf((float(j) / (levels - 1) - 0.5) / 0.5, 0.0, 1.0)
				if absf(mid) < lerpf(0.0, deg_to_rad(24.0), open_t):
					continue
			if absf(mid) < panel_half:
				color = panel
			elif absf(mid) < panel_half + deg_to_rad(5.0):
				color = trim
			_quad(tool, _ring_point(frame, rings[j], a0), _ring_point(frame, rings[j], a1),
				_ring_point(frame, rings[j + 1], a1), _ring_point(frame, rings[j + 1], a0), color)
	var parts: Array[ArrayMesh] = [_finish(tool)]
	if laced:
		parts.append(_lacing(frame, rings, panel_half, lace))
	return parts


## Cadarço em X sobre o painel da frente do corpete.
static func _lacing(frame: Frame, rings: Array, panel_half: float, color: Color) -> ArrayMesh:
	var tool := _tool()
	var count := rings.size() - 1
	var thick := frame.height * 0.006
	for j in count:
		for cross in [1.0, -1.0]:
			var from := _ring_point(frame, rings[j], panel_half * 0.85 * cross, 0.012 * frame.height)
			var to := _ring_point(frame, rings[j + 1], -panel_half * 0.85 * cross, 0.012 * frame.height)
			var along := (to - from)
			var width := along.cross(frame.forward).normalized() * thick
			_quad(tool, from - width, from + width, to + width, to - width, color)
	return _finish(tool)


## Saia longa em A: do corpete ao chão, com pregas, painel central, bordas e cauda atrás.
static func _skirt(frame: Frame, y0: float, y1: float, body: Color, panel: Color, trim: Color, flare: float, panel_angle: float, plain := false) -> ArrayMesh:
	var top := _slice(frame, y0 + frame.height * 0.02, frame.height * 0.135)
	var rows := 10
	var tool := _tool()
	var panel_start := deg_to_rad(panel_angle * 0.45)
	var panel_end := deg_to_rad(panel_angle)
	var floor_side := frame.height * 0.30 * flare
	var floor_depth := frame.height * 0.30 * flare
	var tail := frame.height * 0.07 * flare
	var points: Array = []
	for j in rows + 1:
		var t := float(j) / rows
		var y := lerpf(y0, y1, t)
		var spread := pow(t, 0.75)
		var row: Array[Vector3] = []
		for i in SIDES + 1:
			var a := TAU * i / SIDES
			var along_forward := cos(a)
			var side_part := sin(a)
			var side_r := lerpf(top.x + frame.height * 0.006, floor_side, spread)
			var depth_r := lerpf((top.y - top.z) * 0.5 + frame.height * 0.006, floor_depth + (tail if along_forward < 0.0 else 0.0), spread)
			var ripple := 1.0 + t * (0.05 * sin(9.0 * a + 0.8) + 0.03 * sin(17.0 * a + 2.1)) * (0.4 if plain else 1.0)
			var offset := frame.forward * (along_forward * depth_r) + frame.side * (side_part * side_r)
			var middle := frame.centre + frame.forward * ((top.y + top.z) * 0.5)
			row.append(Vector3(middle.x, y, middle.z) + offset * ripple)
		points.append(row)
	for j in rows:
		var t_mid := (float(j) + 0.5) / rows
		var half_panel := lerpf(panel_start, panel_end, t_mid)
		for i in SIDES:
			var mid := wrapf(TAU * (i + 0.5) / SIDES + PI, 0.0, TAU) - PI
			var color := body
			if absf(mid) < half_panel:
				color = panel
			elif absf(mid) < half_panel + deg_to_rad(4.0):
				color = trim
			_quad(tool, points[j][i], points[j][i + 1], points[j + 1][i + 1], points[j + 1][i], color)
	return _finish(tool)


## Mangas: [parte do braço, parte do antebraço]. "bell" abre em sino no punho, "puff" é
## bufante com punho justo, "cap" é uma mangueta curta nos ombros.
static func _sleeves(frame: Frame, shoulder: Vector3, elbow: Vector3, wrist: Vector3, kind: String, body: Color, trim: Color, scale: float) -> Array[ArrayMesh]:
	var arm := 0.040 * frame.height
	var upper := _tube(frame, shoulder - (elbow - shoulder).normalized() * arm * 0.4, elbow,
		[[0.0, arm * 1.15], [1.0, arm * 1.2]] if kind != "cap" else [[0.0, arm * 1.25], [0.55, arm * 1.35], [0.56, 0.0]], body, trim)
	if kind == "cap":
		return [upper]
	if kind == "wide":
		var wide_upper := _tube(frame, shoulder - (elbow - shoulder).normalized() * arm * 0.4, elbow, [[0.0, arm * 1.45], [1.0, arm * 1.75]], body, trim)
		var wide_lower := _tube(frame, elbow, elbow.lerp(wrist, 0.78), [[0.0, arm * 1.75], [0.7, arm * 2.0], [1.0, arm * 2.1]], body, trim)
		return [wide_upper, wide_lower]
	var hand_end := wrist + (wrist - elbow).normalized() * (0.03 * frame.height)
	var profile: Array = [[0.0, arm * 1.2], [0.5, arm * 1.3], [0.7, arm * 1.7], [0.94, arm * 2.3], [1.0, arm * 2.4]] if kind == "bell" \
		else [[0.0, arm * 1.3], [0.6, arm * 1.6], [0.88, arm * 1.7], [0.94, arm * 1.05], [1.0, arm * 1.05]]
	var lower := _tube(frame, elbow, hand_end, profile, body, trim, true)
	return [upper, lower]


## Tubo de `a` a `b`; `profile` = [[t, raio]]; com `rim`, o último anel leva a cor do trim.
static func _tube(frame: Frame, a: Vector3, b: Vector3, profile: Array, color: Color, trim: Color, rim := false) -> ArrayMesh:
	var axis := (b - a).normalized()
	var u := axis.cross(Vector3.UP).normalized()
	if u.length() < 0.1:
		u = axis.cross(Vector3.BACK).normalized()
	var v := axis.cross(u).normalized()
	var tool := _tool()
	var rows: Array = []
	for entry: Array in profile:
		var ring: Array[Vector3] = []
		for i in 24 + 1:
			var ang := TAU * i / 24
			ring.append(a.lerp(b, float(entry[0])) + (u * cos(ang) + v * sin(ang)) * float(entry[1]))
		rows.append(ring)
	for j in rows.size() - 1:
		var last := rim and j == rows.size() - 2
		for i in 24:
			_quad(tool, rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i], trim if last else color)
	return _finish(tool)


## Faixa na cintura, com a ponta do nó caindo na frente.
static func _belt(frame: Frame, y: float, band: float, color: Color) -> ArrayMesh:
	var slice := _slice(frame, y, frame.height * 0.135)
	var margin := frame.height * 0.012
	var tool := _tool()
	var ring := {"y": y, "half": slice.x + margin, "front": slice.y + margin, "back": slice.z - margin}
	var top := ring.duplicate()
	top.y = y + band * 0.5
	var bottom := ring.duplicate()
	bottom.y = y - band * 0.5
	for i in SIDES:
		var a0 := TAU * i / SIDES
		var a1 := TAU * (i + 1) / SIDES
		_quad(tool, _ring_point(frame, bottom, a0), _ring_point(frame, bottom, a1), _ring_point(frame, top, a1), _ring_point(frame, top, a0), color)
	# O nó: duas pontas penduradas à frente, à direita do centro.
	for tail in [[0.14, 1.0], [0.22, 0.7]]:
		var start := _ring_point(frame, ring, float(tail[0]) * 1.0, frame.height * 0.004)
		var drop := frame.height * 0.09 * float(tail[1])
		var side := frame.side * (frame.height * 0.01)
		_quad(tool, start - side, start + side, start + side - Vector3(0, drop, 0), start - side - Vector3(0, drop, 0), color)
	return _finish(tool)


## Decote em V escuro com cadarço em X (camisa de linho).
static func _neck_lacing(frame: Frame, y_top: float, color: Color) -> ArrayMesh:
	var margin := frame.height * 0.006
	var limit := frame.height * 0.135
	var rings: Array = []
	var levels := 4
	for j in levels + 1:
		var y := lerpf(y_top, y_top - frame.height * 0.07, float(j) / levels)
		var s := _slice(frame, y, limit)
		rings.append({"y": y, "half": s.x + margin, "front": s.y + margin, "back": s.z - margin})
	var tool := _tool()
	# Fundo do decote: um V escuro.
	for j in levels:
		var half := lerpf(deg_to_rad(22.0), deg_to_rad(4.0), float(j) / levels)
		var next := lerpf(deg_to_rad(22.0), deg_to_rad(4.0), float(j + 1) / levels)
		_quad(tool, _ring_point(frame, rings[j], half, frame.height * 0.004), _ring_point(frame, rings[j], -half, frame.height * 0.004),
			_ring_point(frame, rings[j + 1], -next, frame.height * 0.004), _ring_point(frame, rings[j + 1], next, frame.height * 0.004), color.darkened(0.35))
	var mesh_a := _finish(tool)
	var lace := _lacing(frame, rings, deg_to_rad(14.0), color)
	var merged := ArrayMesh.new()
	for source: ArrayMesh in [mesh_a, lace]:
		merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, source.surface_get_arrays(0))
	return merged


# --- Malha e materiais -------------------------------------------------------

static func _ring_point(frame: Frame, ring: Dictionary, angle: float, out := 0.0) -> Vector3:
	# 0 = frente; o ângulo cresce para o lado esquerdo do personagem.
	var forward_part := cos(angle)
	var depth: float = ring.front if forward_part >= 0.0 else -ring.back
	var point := frame.centre + frame.forward * (forward_part * depth) + frame.side * (sin(angle) * float(ring.half))
	point += (frame.forward * forward_part + frame.side * sin(angle)).normalized() * out
	return Vector3(point.x, float(ring.y), point.z)


static func _tool() -> SurfaceTool:
	var tool := SurfaceTool.new()
	tool.begin(Mesh.PRIMITIVE_TRIANGLES)
	return tool


static func _quad(tool: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, color: Color) -> void:
	for vertex in [a, b, c, a, c, d]:
		tool.set_smooth_group(0)
		tool.set_color(color)
		tool.add_vertex(vertex)


static func _finish(tool: SurfaceTool) -> ArrayMesh:
	tool.generate_normals()
	return tool.commit()


## Prende a malha ao osso: construída no espaço de repouso, com a inversa do repouso do osso.
static func _attach(skeleton: Skeleton3D, bone: String, mesh: ArrayMesh, style: Dictionary) -> MeshInstance3D:
	var holder := BoneAttachment3D.new()
	holder.bone_name = bone
	skeleton.add_child(holder)
	var piece := MeshInstance3D.new()
	piece.mesh = mesh
	var base := StandardMaterial3D.new()
	base.vertex_color_use_as_albedo = true
	base.cull_mode = BaseMaterial3D.CULL_DISABLED
	piece.material_override = PaintedTextures.material(base, String(style.get("cloth", "cloth")), Color.WHITE, float(style.get("tile", 0.65)) * skeleton_scale(skeleton))
	piece.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	piece.transform = skeleton.get_bone_global_rest(skeleton.find_bone(bone)).affine_inverse()
	holder.add_child(piece)
	return piece


## Escala do esqueleto em relação a 9 unidades (o tamanho do corpo da cortesã).
static func skeleton_scale(skeleton: Skeleton3D) -> float:
	var top := 0.0
	for i in skeleton.get_bone_count():
		top = maxf(top, skeleton.get_bone_global_rest(i).origin.y)
	return maxf(top, 0.01) / 8.0
