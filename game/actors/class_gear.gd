# Southern Mercenaries — GPL-3.0-or-later
class_name ClassGear
extends RefCounted
## Roupas e armaduras por rank (D a S = nível 1 a 5 da referência do autor, `clothes.jpeg`) do Mago,
## do Cavaleiro, do Arqueiro e do Invocador; o Ninja está em NinjaGear. Cada peça (corpo, cabeça,
## mãos, pés) troca separadamente. A base é o conjunto do Camponês (D) ou do Patrulheiro (C a S),
## tingido e com a textura em tons de cinza (HeroModel.show_part); o que muda de rank é montado
## por código com o GearKit e o Clothing, presas aos ossos.
##   Mago       D túnica de estopa rasgada · C manto bege com capuz e bolsas · B manto verde-acinzentado
##              com pergaminhos · A veludo carmesim com ombreiras prateadas · S azul e ouro com cristais
##   Cavaleiro  D gibão acolchoado · C peitoral de aço e malha · B placas e tabardo azul ·
##              A armadura dourada e tabardo longo · S armadura negra e dourada com capa
##   Arqueiro   D túnica verde esfarrapada · C jaqueta de couro com capuz · B túnica e capa verdes ·
##              A couro e escamas · S armadura élfica verde e dourada com capa e folhas
##   Invocador  D retalhos de couro e colar de ossos · C poncho escuro com penas · B túnica tribal com
##              contas · A manto de pele e pingente · S túnica cósmica com chifres e asas de cristal

const CLASSES: Array[String] = ["mage", "knight", "archer", "summoner"]
const RANKS: Array[String] = ["D", "C", "B", "A", "S"]

## Cores por classe e rank: main (tecido), trim (couro, acabamento), accent (metal, bordado) e glow.
const PALETTE := {
	"mage": {
		"D": {"main": Color(0.55, 0.46, 0.31), "trim": Color(0.4, 0.3, 0.18), "accent": Color(0.5, 0.4, 0.25), "glow": Color(0, 0, 0)},
		"C": {"main": Color(0.62, 0.53, 0.37), "trim": Color(0.3, 0.2, 0.12), "accent": Color(0.45, 0.32, 0.18), "glow": Color(0, 0, 0)},
		"B": {"main": Color(0.27, 0.3, 0.27), "trim": Color(0.33, 0.22, 0.13), "accent": Color(0.55, 0.45, 0.28), "glow": Color(0, 0, 0)},
		"A": {"main": Color(0.4, 0.07, 0.1), "trim": Color(0.82, 0.66, 0.26), "accent": Color(0.55, 0.57, 0.62), "glow": Color(0, 0, 0)},
		"S": {"main": Color(0.07, 0.1, 0.27), "trim": Color(0.92, 0.74, 0.27), "accent": Color(0.3, 0.55, 1.0), "glow": Color(0.3, 0.6, 1.0)},
	},
	"knight": {
		"D": {"main": Color(0.5, 0.42, 0.3), "trim": Color(0.36, 0.25, 0.15), "accent": Color(0.45, 0.35, 0.22), "glow": Color(0, 0, 0)},
		"C": {"base": Color(0.3, 0.25, 0.2), "main": Color(0.55, 0.57, 0.6), "trim": Color(0.33, 0.21, 0.12), "accent": Color(0.6, 0.5, 0.35), "glow": Color(0, 0, 0)},
		"B": {"base": Color(0.2, 0.22, 0.3), "main": Color(0.66, 0.68, 0.72), "trim": Color(0.12, 0.22, 0.5), "accent": Color(0.85, 0.85, 0.9), "glow": Color(0, 0, 0)},
		"A": {"base": Color(0.15, 0.19, 0.34), "main": Color(0.75, 0.62, 0.3), "trim": Color(0.1, 0.13, 0.3), "accent": Color(0.95, 0.8, 0.35), "glow": Color(0, 0, 0)},
		"S": {"base": Color(0.1, 0.09, 0.1), "main": Color(0.1, 0.09, 0.1), "trim": Color(0.9, 0.7, 0.25), "accent": Color(0.95, 0.75, 0.3), "glow": Color(1.0, 0.65, 0.2)},
	},
	"archer": {
		"D": {"main": Color(0.25, 0.3, 0.15), "trim": Color(0.33, 0.24, 0.12), "accent": Color(0.4, 0.33, 0.18), "glow": Color(0, 0, 0)},
		"C": {"main": Color(0.35, 0.22, 0.12), "trim": Color(0.26, 0.16, 0.09), "accent": Color(0.5, 0.35, 0.2), "glow": Color(0, 0, 0)},
		"B": {"main": Color(0.15, 0.28, 0.15), "trim": Color(0.33, 0.21, 0.12), "accent": Color(0.5, 0.4, 0.22), "glow": Color(0, 0, 0)},
		"A": {"main": Color(0.2, 0.31, 0.21), "trim": Color(0.34, 0.22, 0.13), "accent": Color(0.55, 0.62, 0.55), "glow": Color(0, 0, 0)},
		"S": {"main": Color(0.08, 0.3, 0.17), "trim": Color(0.82, 0.7, 0.28), "accent": Color(0.3, 0.9, 0.55), "glow": Color(0.3, 1.0, 0.55)},
	},
	"summoner": {
		"D": {"main": Color(0.42, 0.31, 0.2), "trim": Color(0.3, 0.2, 0.12), "accent": Color(0.85, 0.8, 0.7), "glow": Color(0, 0, 0)},
		"C": {"main": Color(0.22, 0.15, 0.1), "trim": Color(0.3, 0.2, 0.12), "accent": Color(0.8, 0.75, 0.62), "glow": Color(0, 0, 0)},
		"B": {"main": Color(0.4, 0.25, 0.14), "trim": Color(0.1, 0.5, 0.5), "accent": Color(0.85, 0.8, 0.68), "glow": Color(0, 0, 0)},
		"A": {"main": Color(0.4, 0.3, 0.2), "trim": Color(0.1, 0.55, 0.55), "accent": Color(0.3, 0.9, 0.85), "glow": Color(0, 0, 0)},
		"S": {"main": Color(0.14, 0.1, 0.4), "trim": Color(0.35, 0.5, 0.95), "accent": Color(0.7, 0.8, 1.0), "glow": Color(0.5, 0.6, 1.0)},
	},
}

## Paleta feminina: rosa, amarelo, verde e roxo (o masculino segue mais sóbrio).
const PALETTE_FEMALE := {
	"mage": {
		"D": {"main": Color(0.78, 0.55, 0.62), "trim": Color(0.55, 0.3, 0.38), "accent": Color(0.9, 0.75, 0.5), "glow": Color(0, 0, 0)},
		"C": {"main": Color(0.88, 0.45, 0.6), "trim": Color(0.5, 0.22, 0.35), "accent": Color(0.95, 0.8, 0.5), "glow": Color(0, 0, 0)},
		"B": {"main": Color(0.5, 0.28, 0.65), "trim": Color(0.9, 0.5, 0.7), "accent": Color(0.95, 0.85, 0.5), "glow": Color(0, 0, 0)},
		"A": {"main": Color(0.62, 0.2, 0.62), "trim": Color(0.95, 0.78, 0.35), "accent": Color(0.98, 0.6, 0.8), "glow": Color(0, 0, 0)},
		"S": {"main": Color(0.42, 0.15, 0.7), "trim": Color(0.98, 0.8, 0.35), "accent": Color(1.0, 0.5, 0.85), "glow": Color(0.9, 0.4, 1.0)},
	},
	"knight": {
		"D": {"main": Color(0.82, 0.68, 0.32), "trim": Color(0.5, 0.35, 0.15), "accent": Color(0.9, 0.78, 0.4), "glow": Color(0, 0, 0)},
		"C": {"base": Color(0.75, 0.35, 0.5), "main": Color(0.62, 0.64, 0.68), "trim": Color(0.55, 0.2, 0.35), "accent": Color(0.95, 0.8, 0.4), "glow": Color(0, 0, 0)},
		"B": {"base": Color(0.45, 0.25, 0.6), "main": Color(0.75, 0.77, 0.82), "trim": Color(0.55, 0.28, 0.75), "accent": Color(0.95, 0.85, 0.9), "glow": Color(0, 0, 0)},
		"A": {"base": Color(0.85, 0.4, 0.6), "main": Color(0.9, 0.75, 0.4), "trim": Color(0.7, 0.25, 0.5), "accent": Color(1.0, 0.85, 0.45), "glow": Color(0, 0, 0)},
		"S": {"base": Color(0.4, 0.15, 0.55), "main": Color(0.95, 0.8, 0.4), "trim": Color(0.98, 0.5, 0.8), "accent": Color(1.0, 0.85, 0.45), "glow": Color(1.0, 0.5, 0.85)},
	},
	"archer": {
		"D": {"main": Color(0.5, 0.65, 0.25), "trim": Color(0.55, 0.4, 0.2), "accent": Color(0.85, 0.75, 0.3), "glow": Color(0, 0, 0)},
		"C": {"main": Color(0.78, 0.7, 0.25), "trim": Color(0.4, 0.5, 0.2), "accent": Color(0.55, 0.75, 0.3), "glow": Color(0, 0, 0)},
		"B": {"main": Color(0.2, 0.55, 0.3), "trim": Color(0.9, 0.55, 0.7), "accent": Color(0.95, 0.85, 0.4), "glow": Color(0, 0, 0)},
		"A": {"main": Color(0.15, 0.6, 0.4), "trim": Color(0.95, 0.8, 0.35), "accent": Color(0.95, 0.5, 0.75), "glow": Color(0, 0, 0)},
		"S": {"main": Color(0.1, 0.55, 0.35), "trim": Color(0.98, 0.82, 0.35), "accent": Color(0.6, 1.0, 0.5), "glow": Color(0.5, 1.0, 0.6)},
	},
	"summoner": {
		"D": {"main": Color(0.9, 0.78, 0.4), "trim": Color(0.6, 0.4, 0.2), "accent": Color(0.95, 0.9, 0.8), "glow": Color(0, 0, 0)},
		"C": {"main": Color(0.88, 0.5, 0.65), "trim": Color(0.5, 0.3, 0.2), "accent": Color(0.95, 0.9, 0.78), "glow": Color(0, 0, 0)},
		"B": {"main": Color(0.5, 0.65, 0.3), "trim": Color(0.85, 0.35, 0.6), "accent": Color(0.95, 0.9, 0.75), "glow": Color(0, 0, 0)},
		"A": {"main": Color(0.55, 0.3, 0.7), "trim": Color(0.95, 0.5, 0.75), "accent": Color(0.95, 0.85, 0.5), "glow": Color(0, 0, 0)},
		"S": {"main": Color(0.7, 0.3, 0.75), "trim": Color(1.0, 0.7, 0.85), "accent": Color(1.0, 0.9, 0.5), "glow": Color(1.0, 0.6, 0.95)},
	},
}

## Paleta da vez (preenchida em apply conforme o sexo do modelo).
static var _female := false


static func has_gear(class_id: String) -> bool:
	return class_id in CLASSES


## Veste o modelo: `ranks` = {body, head, hands, feet} com o rank de cada peça ("" = sem a peça).
static func apply(model: HeroModel, class_id: String, ranks: Dictionary) -> void:
	NinjaGear.clear(model)
	model.set_outfit({})
	_female = model.sex == "female"
	var skeleton := model.skeleton
	if skeleton == null or not PALETTE.has(class_id):
		return
	var body: String = ranks.get("body", "")
	var head: String = ranks.get("head", "")
	var hands: String = ranks.get("hands", "")
	var feet: String = ranks.get("feet", "")
	_base(model, class_id, body, head, hands, feet)
	var frame := Clothing._measure(model, skeleton, Clothing.HERO_BONES)
	var made: Array[Node] = []
	if body != "":
		made.append_array(_body(skeleton, frame, class_id, body))
	if head != "":
		made.append_array(_head(skeleton, frame, class_id, head))
	if hands != "":
		made.append_array(_hands(skeleton, frame, class_id, hands))
	if feet != "":
		made.append_array(_feet(skeleton, frame, class_id, feet))
	model.set_meta(NinjaGear.META, made)


static func _pal(class_id: String, rank: String) -> Dictionary:
	return (PALETTE_FEMALE if _female else PALETTE)[class_id][rank if rank != "" else "D"]


## O corpo por baixo (Camponês no D, Patrulheiro nos outros), tingido de cada peça.
static func _base(model: HeroModel, class_id: String, body: String, head: String, hands: String, feet: String) -> void:
	var used := body if body != "" else (hands if hands != "" else feet)
	var peasant := used == "D" or used == ""
	model.hide_clothes()
	var prefix := "Peasant" if peasant else "Ranger"
	var dim := 1.0 if peasant else 2.0
	var main: Color = _pal(class_id, body if body != "" else used).get("base", _pal(class_id, body if body != "" else used).main)
	model.show_part(prefix + "_Body", main * dim, not peasant)
	model.show_part(prefix + "_Legs", main * dim * (1.0 if peasant else 1.7), not peasant)  # a calça de origem é bem escura
	# Túnica até o chão: a calça por baixo some (senão a perna atravessa o pano quando o herói anda).
	if (class_id == "mage" and body in ["C", "B", "A", "S"]) or (class_id == "summoner" and body in ["A", "S"]):
		model.hide_part(prefix + "_Legs")
	if not peasant:
		for belt in ["Ranger_Body_Belt_1", "Ranger_Body_Belt_2"]:
			model.show_part(belt, _pal(class_id, body).trim, true)
	var arm_palette := _pal(class_id, hands if hands != "" else used)
	model.show_part(prefix + "_Arms", Color(arm_palette.get("base", arm_palette.main)) * dim, not peasant)
	var boot_rank := feet if feet != "" else "D"
	for boots in ["Peasant_Feet"] if boot_rank == "D" else ["Ranger_Feet_Boots", "Ranger_Feet"]:
		model.show_part(boots, _pal(class_id, boot_rank).trim * (1.0 if boots.begins_with("Peasant") else 1.6), boots.begins_with("Ranger"))
	if head in ["C", "B", "A", "S"] and (class_id != "knight") and (class_id != "summoner" or head == "C"):
		model.show_part("Ranger_Head_Hood", _pal(class_id, head).main * 1.9, true)
		model.hide_hair()
	elif class_id == "knight" and head != "" and head != "D":
		model.hide_hair()


# --- Corpo -------------------------------------------------------------------

static func _body(skeleton: Skeleton3D, frame: Clothing.Frame, class_id: String, rank: String) -> Array[Node]:
	match class_id:
		"mage":
			return _mage_body(skeleton, frame, rank)
		"knight":
			return _knight_body(skeleton, frame, rank)
		"archer":
			return _archer_body(skeleton, frame, rank)
		"summoner":
			return _summoner_body(skeleton, frame, rank)
	return []


static func _shoulder(skeleton: Skeleton3D, side: float) -> Vector3:
	return skeleton.get_bone_global_rest(skeleton.find_bone("upperarm_l" if side > 0 else "upperarm_r")).origin


static func _rope(frame: Clothing.Frame, y: float, color: Color) -> ArrayMesh:
	return NinjaGear._band(frame, y, frame.height * 0.016, color, frame.height * 0.02)


static func _mage_body(skeleton: Skeleton3D, frame: Clothing.Frame, rank: String) -> Array[Node]:
	var p := _pal("mage", rank)
	var main: Color = p.main
	var trim: Color = p.trim
	var accent: Color = p.accent
	var h := frame.height
	var waist := h * 0.52
	var chest := h * 0.73
	var made: Array[Node] = []
	var hem := h * (0.18 if rank == "D" else 0.06)
	made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, chest, hem, main, trim if rank != "D" else main.darkened(0.25), 0.045 if rank != "A" else 0.065, 0.045 if rank == "D" else 0.0), "cloth", 0.7))
	match rank:
		"D":
			made.append(NinjaGear._attach(skeleton, "pelvis", _rope(frame, waist, accent), "leather", 0.4))
		"C":
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.04, trim, h * 0.024), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.strap(frame, chest, waist, 1.0, h * 0.012, trim), "leather", 0.4))
			for angle in [0.9, -0.9]:
				made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.pouch(frame, waist - h * 0.02, angle, h * 0.04, trim.lightened(0.1), trim.darkened(0.2)), "leather", 0.4))
		"B":
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.04, trim, h * 0.024), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist - h * 0.05, h * 0.012, trim.darkened(0.2), h * 0.03), "leather", 0.4))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._buckle(frame, waist, accent, h), "metal", 0.6))
			for angle in [1.0, -1.0, 2.2]:
				made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.pouch(frame, waist - h * 0.03, angle, h * 0.045, trim.lightened(0.1), trim.darkened(0.2)), "leather", 0.4))
			for angle in [-0.55, -0.7]:
				made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.scroll(frame, waist - h * 0.01, angle, trim, Color(0.78, 0.7, 0.5)), "cloth", 0.4))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.strap(frame, chest, waist, 1.0, h * 0.011, trim), "leather", 0.4))
		"A", "S":
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.045, trim.darkened(0.15), h * 0.026), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._buckle(frame, waist, accent, h), "metal", 0.6))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._panel(frame, chest, h * 0.5, h * 0.045, true, trim, main.darkened(0.2), 0.0, false), "metal", 0.8))
			var plate := Color(0.5, 0.52, 0.58) if rank == "A" else trim
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				made.append(NinjaGear._attach(skeleton, up, GearKit.plate_shoulder(frame, _shoulder(skeleton, side), side, plate, trim, 1.15, 0.05 if rank == "S" else 0.0), "metal", 1.0))
				if rank == "S":
					made.append(NinjaGear._attach_glow(skeleton, up, GearKit.crystal_fan(frame, _shoulder(skeleton, side), side, accent), accent))
			if rank == "S":
				made.append(NinjaGear._attach_glow(skeleton, "spine_03", GearKit.gem_mesh(frame, Clothing._ring_point(frame, GearKit._ring_for(frame, chest - h * 0.05, h * 0.02), 0.0, h * 0.01), h * 0.022, accent), accent))
			else:
				made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.gem_mesh(frame, Clothing._ring_point(frame, GearKit._ring_for(frame, chest - h * 0.05, h * 0.02), 0.0, h * 0.01), h * 0.02, Color(0.3, 0.7, 0.9)), "metal", 0.4))
	# Mangas largas de manto.
	for side in [1.0, -1.0]:
		var up := "upperarm_l" if side > 0 else "upperarm_r"
		var low := "lowerarm_l" if side > 0 else "lowerarm_r"
		var hand := "hand_l" if side > 0 else "hand_r"
		var pieces := Clothing._sleeves(frame, skeleton.get_bone_global_rest(skeleton.find_bone(up)).origin, skeleton.get_bone_global_rest(skeleton.find_bone(low)).origin,
			skeleton.get_bone_global_rest(skeleton.find_bone(hand)).origin, "wide" if rank != "D" else "bell", main, trim, h / 9.0)
		made.append(NinjaGear._attach(skeleton, up, pieces[0], "cloth", 0.7))
		if pieces.size() > 1:
			made.append(NinjaGear._attach(skeleton, low, pieces[1], "cloth", 0.7))
	return made


static func _knight_body(skeleton: Skeleton3D, frame: Clothing.Frame, rank: String) -> Array[Node]:
	var p := _pal("knight", rank)
	var main: Color = p.main
	var trim: Color = p.trim
	var accent: Color = p.accent
	var h := frame.height
	var waist := h * 0.52
	var chest := h * 0.73
	var made: Array[Node] = []
	match rank:
		"D":
			# Gibão acolchoado: linhas de costura em losango, cordas cruzadas e um pano remendado na frente.
			for i in 5:
				made.append(NinjaGear._attach(skeleton, "spine_03" if i > 0 else "pelvis", NinjaGear._band(frame, lerpf(waist, chest, float(i) / 4.0), h * 0.036, main.lightened(0.04 * (i % 2)), h * 0.014), "cloth", 0.5))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.strap(frame, chest, waist, 1.0, h * 0.007, trim), "leather", 0.4))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.strap(frame, chest, waist, -1.0, h * 0.007, trim), "leather", 0.4))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._hem(frame, waist, h * 0.2, main.darkened(0.1), 8), "cloth", 0.6))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._panel(frame, waist, h * 0.2, h * 0.04, true, Color(0.62, 0.5, 0.36), trim, h * 0.02, false), "cloth", 0.6))
		"C":
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.chest_plate(frame, waist + h * 0.01, chest, main, trim, 0.012), "metal", 1.0))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._skirt_plates(frame, waist, h * 0.16, Color(0.4, 0.42, 0.46), trim, 14, false), "chain", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist - h * 0.01, h * 0.04, trim, h * 0.024), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._buckle(frame, waist, accent, h), "metal", 0.6))
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				made.append(NinjaGear._attach(skeleton, up, GearKit.plate_shoulder(frame, _shoulder(skeleton, side), side, main, trim, 0.9, 0.0), "metal", 1.0))
		"B":
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.chest_plate(frame, waist + h * 0.04, chest, main, trim, 0.01), "metal", 1.0))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._panel(frame, chest - h * 0.04, h * 0.52, h * 0.085, true, trim, accent, 0.0, true), "cloth", 0.7))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._panel(frame, chest - h * 0.04, h * 0.5, h * 0.085, false, trim, accent, 0.0, false), "cloth", 0.7))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.04, Color(0.33, 0.21, 0.12), h * 0.03), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._buckle(frame, waist, accent, h), "metal", 0.6))
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				made.append(NinjaGear._attach(skeleton, up, GearKit.plate_shoulder(frame, _shoulder(skeleton, side), side, main, accent, 1.0, 0.0), "metal", 1.0))
		"A":
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.chest_plate(frame, waist, chest, main, accent, 0.018), "metal", 1.0))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._panel(frame, waist + h * 0.02, h * 0.6, h * 0.075, true, trim, accent, 0.0, false), "cloth", 0.7))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._panel(frame, waist + h * 0.02, h * 0.58, h * 0.075, false, trim, accent, 0.0, false), "cloth", 0.7))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist - h * 0.005, h * 0.045, accent.darkened(0.3), h * 0.034), "metal", 0.6))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._buckle(frame, waist, accent, h), "metal", 0.6))
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				made.append(NinjaGear._attach(skeleton, up, GearKit.plate_shoulder(frame, _shoulder(skeleton, side), side, main, accent, 1.25, 0.03), "metal", 1.0))
		"S":
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.chest_plate(frame, waist, chest, main, accent, 0.022), "metal", 1.0))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._skirt_plates(frame, waist - h * 0.01, h * 0.24, main.lightened(0.04), accent, 14, true), "metal", 1.0))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist - h * 0.005, h * 0.05, accent.darkened(0.3), h * 0.036), "metal", 0.6))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._cape(frame, chest + h * 0.01, h * 0.45, Color(0.05, 0.04, 0.05), accent), "cloth", 0.8))
			made.append(NinjaGear._attach_glow(skeleton, "spine_03", NinjaGear._chest_lines(frame, chest, waist, p.glow), p.glow))
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				made.append(NinjaGear._attach(skeleton, up, GearKit.plate_shoulder(frame, _shoulder(skeleton, side), side, main, accent, 1.4, 0.1), "metal", 1.0))
	return made


static func _archer_body(skeleton: Skeleton3D, frame: Clothing.Frame, rank: String) -> Array[Node]:
	var p := _pal("archer", rank)
	var main: Color = p.main
	var trim: Color = p.trim
	var accent: Color = p.accent
	var h := frame.height
	var waist := h * 0.52
	var chest := h * 0.73
	var made: Array[Node] = []
	match rank:
		"D":
			made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, chest - h * 0.04, h * 0.3, main, main.darkened(0.3), 0.02, 0.05), "cloth", 0.7))
			made.append(NinjaGear._attach(skeleton, "pelvis", _rope(frame, waist, trim), "leather", 0.4))
		"C":
			made.append(NinjaGear._attach(skeleton, "spine_03", Clothing._torso(frame, waist, chest, main, main, trim, false, trim, false)[0], "leather", 0.45))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._hem(frame, waist, h * 0.16, main.darkened(0.1), 10), "leather", 0.45))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.04, trim, h * 0.026), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._buckle(frame, waist, accent, h), "metal", 0.6))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.strap(frame, chest, waist, 1.0, h * 0.012, trim.lightened(0.1)), "leather", 0.4))
		"B":
			made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, chest - h * 0.03, h * 0.28, main, trim, 0.03, 0.0), "cloth", 0.7))
			made.append(NinjaGear._attach(skeleton, "spine_03", Clothing._torso(frame, waist, chest, trim, trim, accent, true, accent, true)[0], "leather", 0.45))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.04, trim, h * 0.03), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._buckle(frame, waist, accent, h), "metal", 0.6))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._cape(frame, chest + h * 0.01, h * 0.34, main.darkened(0.15), trim), "cloth", 0.8))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.strap(frame, chest, waist, -1.0, h * 0.012, trim.lightened(0.1)), "leather", 0.4))
		"A":
			for i in 6:
				made.append(NinjaGear._attach(skeleton, "spine_03" if i > 0 else "pelvis", NinjaGear._band(frame, lerpf(waist, chest, float(i) / 5.0), h * 0.04, main.lightened(0.05 * (i % 2)), h * 0.016, h * 0.006), "chain", 0.45))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._skirt_plates(frame, waist, h * 0.14, main, trim, 12, false), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist - h * 0.01, h * 0.04, trim, h * 0.03), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._buckle(frame, waist, accent, h), "metal", 0.6))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.strap(frame, chest, waist, 1.0, h * 0.013, trim), "leather", 0.4))
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				made.append(NinjaGear._attach(skeleton, up, GearKit.plate_shoulder(frame, _shoulder(skeleton, side), side, trim.lightened(0.1), main, 0.95, 0.0), "leather", 0.5))
		"S":
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.chest_plate(frame, waist, chest, main, accent, 0.012), "metal", 1.0))
			made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, waist, h * 0.2, main.darkened(0.1), accent, 0.04, 0.03), "cloth", 0.7))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.045, trim.darkened(0.3), h * 0.034), "metal", 0.6))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._cape(frame, chest + h * 0.015, h * 0.5, main.darkened(0.3), accent), "cloth", 0.8))
			made.append(NinjaGear._attach_glow(skeleton, "spine_03", GearKit.gem_mesh(frame, Clothing._ring_point(frame, GearKit._ring_for(frame, chest - h * 0.05, h * 0.02), 0.0, h * 0.012), h * 0.022, p.glow), p.glow))
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				made.append(NinjaGear._attach(skeleton, up, GearKit.leaf_shoulder(frame, _shoulder(skeleton, side), side, main.lightened(0.05), accent), "metal", 0.8))
	return made


static func _summoner_body(skeleton: Skeleton3D, frame: Clothing.Frame, rank: String) -> Array[Node]:
	var p := _pal("summoner", rank)
	var main: Color = p.main
	var trim: Color = p.trim
	var accent: Color = p.accent
	var h := frame.height
	var waist := h * 0.52
	var chest := h * 0.73
	var made: Array[Node] = []
	var bones := [Color(0.88, 0.84, 0.72), Color(0.8, 0.74, 0.6)]
	match rank:
		"D":
			made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, chest - h * 0.03, h * 0.34, main, main.darkened(0.3), 0.02, 0.06), "leather", 0.45))
			made.append(NinjaGear._attach(skeleton, "pelvis", _rope(frame, waist, trim), "leather", 0.4))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.necklace(frame, chest + h * 0.01, accent, Color(0.9, 0.88, 0.8), 11, 0.05), "cloth", 0.3))
		"C":
			made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, chest, h * 0.24, main, main.darkened(0.35), 0.035, 0.07), "leather", 0.45))
			made.append(NinjaGear._attach(skeleton, "pelvis", _rope(frame, waist, trim.lightened(0.1)), "leather", 0.4))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.feathers(frame, Clothing._ring_point(frame, GearKit._ring_for(frame, chest - h * 0.02, h * 0.02), 0.9, 0.0), 4, h * 0.14, bones), "cloth", 0.3))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.necklace(frame, chest + h * 0.01, accent, accent, 9, 0.06), "cloth", 0.3))
		"B":
			made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, chest, h * 0.2, main, trim, 0.04, 0.0), "leather", 0.45))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._band(frame, chest - h * 0.05, h * 0.03, trim, h * 0.02), "cloth", 0.4))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.04, trim.darkened(0.3), h * 0.03), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._panel(frame, waist, h * 0.3, h * 0.05, true, main.darkened(0.15), trim, 0.0, false), "cloth", 0.5))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.necklace(frame, chest + h * 0.01, accent, trim, 13, 0.07), "cloth", 0.3))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.feathers(frame, Clothing._ring_point(frame, GearKit._ring_for(frame, chest - h * 0.02, h * 0.02), -0.9, 0.0), 3, h * 0.13, bones), "cloth", 0.3))
		"A":
			made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, chest, h * 0.12, main, trim, 0.05, 0.0), "leather", 0.45))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.045, trim.darkened(0.3), h * 0.032), "leather", 0.5))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._panel(frame, chest, h * 0.5, h * 0.04, true, trim.darkened(0.2), accent, 0.0, false), "cloth", 0.6))
			made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.fur_mantle(frame, chest + h * 0.03, Color(0.32, 0.27, 0.22), Color(0.6, 0.55, 0.5)), "cloth", 0.3))
			made.append(NinjaGear._attach_glow(skeleton, "spine_03", GearKit.gem_mesh(frame, Clothing._ring_point(frame, GearKit._ring_for(frame, chest - h * 0.06, h * 0.02), 0.0, h * 0.012), h * 0.022, accent), accent))
		"S":
			made.append(NinjaGear._attach(skeleton, "pelvis", GearKit.robe(frame, chest, h * 0.04, main, p.trim, 0.09, 0.0), "cloth", 0.7))
			made.append(NinjaGear._attach(skeleton, "pelvis", NinjaGear._band(frame, waist, h * 0.045, main.lightened(0.1), h * 0.03), "metal", 0.6))
			made.append(NinjaGear._attach_glow(skeleton, "pelvis", NinjaGear._chest_lines(frame, chest, waist, p.glow), p.glow))
			made.append(NinjaGear._attach(skeleton, "spine_03", NinjaGear._cape(frame, chest + h * 0.012, h * 0.52, Color(0.1, 0.07, 0.3), p.trim), "cloth", 0.8))
			made.append(NinjaGear._attach_glow(skeleton, "spine_03", GearKit.gem_mesh(frame, Clothing._ring_point(frame, GearKit._ring_for(frame, chest - h * 0.05, h * 0.02), 0.0, h * 0.012), h * 0.026, p.glow), p.glow))
			for side in [1.0, -1.0]:
				var up := "upperarm_l" if side > 0 else "upperarm_r"
				made.append(NinjaGear._attach_glow(skeleton, up, GearKit.crystal_fan(frame, _shoulder(skeleton, side), side, p.trim), p.trim))
	# Mangas curtas (poncho) ou compridas de tecido.
	for side in [1.0, -1.0]:
		var up := "upperarm_l" if side > 0 else "upperarm_r"
		var low := "lowerarm_l" if side > 0 else "lowerarm_r"
		var hand := "hand_l" if side > 0 else "hand_r"
		var kind := "cap" if rank in ["C", "D"] else "puff"
		var pieces := Clothing._sleeves(frame, skeleton.get_bone_global_rest(skeleton.find_bone(up)).origin, skeleton.get_bone_global_rest(skeleton.find_bone(low)).origin,
			skeleton.get_bone_global_rest(skeleton.find_bone(hand)).origin, kind, main, trim, h / 9.0)
		made.append(NinjaGear._attach(skeleton, up, pieces[0], "leather", 0.45))
		if pieces.size() > 1:
			made.append(NinjaGear._attach(skeleton, low, pieces[1], "cloth", 0.6))
	return made


# --- Cabeça ------------------------------------------------------------------

static func _head(skeleton: Skeleton3D, frame: Clothing.Frame, class_id: String, rank: String) -> Array[Node]:
	var p := _pal(class_id, rank)
	var main: Color = p.main
	var trim: Color = p.trim
	var accent: Color = p.accent
	var h := frame.height
	var made: Array[Node] = []
	var bone := NinjaGear._head_bone(skeleton)
	if bone == "":
		return made
	var origin := skeleton.get_bone_global_rest(skeleton.find_bone(bone)).origin
	var centre := origin + Vector3(0, h * 0.075, 0)
	var radius := h * 0.08
	match class_id:
		"mage":
			if rank in ["C", "B"]:
				made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.cowl(frame, origin, radius, main, trim, 0.06), "cloth", 0.6))
			elif rank in ["A", "S"]:
				# Gola alta e rígida de cada lado do pescoço e uma gema na testa.
				made.append(NinjaGear._attach(skeleton, "spine_03", Clothing._tube(frame, origin + Vector3(0, h * 0.03, 0), origin - Vector3(0, h * 0.02, 0),
					[[0.0, radius * 1.05], [1.0, radius * 1.3]], main, trim, true), "cloth", 0.5))
				var gem_colour: Color = accent if rank == "S" else Color(0.3, 0.8, 0.9)
				made.append(NinjaGear._attach_glow(skeleton, bone, GearKit.gem_mesh(frame, centre + frame.forward * (radius * 0.72) + Vector3(0, radius * 0.45, 0), h * 0.016, gem_colour), gem_colour))
				if rank == "S":
					made.append(NinjaGear._attach(skeleton, bone, Clothing._tube(frame, centre + Vector3(0, radius * 0.2, 0), centre + Vector3(0, radius * 0.38, 0),
						[[0.0, radius * 0.7], [1.0, radius * 0.7]], trim, trim, true), "metal", 0.6))
		"knight":
			if rank != "D":
				var helm := Color(0.5, 0.52, 0.56) if rank == "C" else (main.darkened(0.1) if rank in ["A", "S"] else Color(0.66, 0.68, 0.72))
				made.append(NinjaGear._attach(skeleton, bone, NinjaGear._dome(frame, centre + Vector3(0, radius * 0.38, 0), radius * 1.1, 0.0, helm, accent if rank != "C" else trim), "metal", 1.0))
				if rank in ["B", "A", "S"]:
					# Protetor de nariz e laterais.
					made.append(NinjaGear._attach(skeleton, bone, Clothing._tube(frame, centre + frame.forward * (radius * 1.1) + Vector3(0, radius * 0.7, 0), centre + frame.forward * (radius * 1.1) + Vector3(0, radius * 0.1, 0),
						[[0.0, radius * 0.07], [1.0, radius * 0.05]], helm, accent), "metal", 0.6))
				if rank == "S":
					for side in [1.0, -1.0]:
						made.append(NinjaGear._attach(skeleton, bone, NinjaGear._horn(frame, centre, side, accent, h), "metal", 1.0))
					made.append(NinjaGear._attach_glow(skeleton, bone, NinjaGear._eyes(frame, centre, radius, h), p.glow))
		"archer":
			if rank == "A":
				made.append(NinjaGear._attach(skeleton, "spine_03", GearKit.cowl(frame, origin, radius, main.lightened(0.05), trim, 0.05), "chain", 0.45))
			elif rank == "S":
				made.append(NinjaGear._attach(skeleton, bone, Clothing._tube(frame, centre + Vector3(0, radius * 0.2, 0), centre + Vector3(0, radius * 0.38, 0),
					[[0.0, radius * 0.7], [1.0, radius * 0.7]], accent, accent, true), "metal", 0.6))
				made.append(NinjaGear._attach_glow(skeleton, bone, GearKit.gem_mesh(frame, centre + frame.forward * (radius * 0.72) + Vector3(0, radius * 0.45, 0), h * 0.014, p.glow), p.glow))
		"summoner":
			if rank == "C":
				made.append(NinjaGear._attach(skeleton, bone, GearKit.feathers(frame, centre + frame.side * (radius * 0.95) + Vector3(0, radius * 0.4, 0), 3, h * 0.1, [Color(0.85, 0.8, 0.65), Color(0.3, 0.2, 0.14)]), "cloth", 0.3))
			elif rank == "B":
				# Faixa de contas na testa com penas.
				made.append(NinjaGear._attach(skeleton, bone, Clothing._tube(frame, centre + Vector3(0, radius * 0.2, 0), centre + Vector3(0, radius * 0.34, 0),
					[[0.0, radius * 0.7], [1.0, radius * 0.7]], trim, accent, true), "leather", 0.4))
			elif rank == "A":
				made.append(NinjaGear._attach(skeleton, bone, Clothing._tube(frame, centre + Vector3(0, radius * 0.2, 0), centre + Vector3(0, radius * 0.38, 0),
					[[0.0, radius * 0.7], [1.0, radius * 0.7]], trim, accent, true), "leather", 0.4))
			elif rank == "S":
				made.append(NinjaGear._attach(skeleton, bone, GearKit.horn_crown(frame, centre, radius, Color(0.55, 0.58, 0.7), p.glow), "metal", 0.8))
	return made


# --- Mãos e pés ----------------------------------------------------------------

static func _hands(skeleton: Skeleton3D, frame: Clothing.Frame, class_id: String, rank: String) -> Array[Node]:
	var p := _pal(class_id, rank)
	var trim: Color = p.trim
	var main: Color = p.main
	var accent: Color = p.accent
	var h := frame.height
	var made: Array[Node] = []
	var arm := h * 0.027
	for side in [1.0, -1.0]:
		var suffix := "l" if side > 0 else "r"
		var low := "lowerarm_" + suffix
		var hand := "hand_" + suffix
		var elbow := skeleton.get_bone_global_rest(skeleton.find_bone(low)).origin
		var wrist := skeleton.get_bone_global_rest(skeleton.find_bone(hand)).origin
		var metal := class_id == "knight" and rank != "D"
		match rank:
			"D":
				made.append(NinjaGear._attach(skeleton, low, GearKit.cuff(frame, elbow.lerp(wrist, 0.7), wrist, arm, trim, trim.darkened(0.3)), "cloth", 0.4))
			"C", "B":
				var color := main if metal else trim
				made.append(NinjaGear._attach(skeleton, low, GearKit.cuff(frame, elbow.lerp(wrist, 0.4), wrist + (wrist - elbow).normalized() * h * 0.008, arm * (1.2 if metal else 1.0), color, trim.darkened(0.2)), "metal" if metal else "leather", 0.8))
			"A", "S":
				var color := main if metal or class_id == "archer" and false else (trim if class_id in ["mage", "summoner"] else main)
				made.append(NinjaGear._attach(skeleton, low, GearKit.cuff(frame, elbow.lerp(wrist, 0.1), wrist + (wrist - elbow).normalized() * h * 0.01, arm * 1.35, color, accent), "metal" if class_id != "summoner" else "leather", 0.8))
				if rank == "S" and class_id in ["mage", "knight", "archer"]:
					made.append(NinjaGear._attach_glow(skeleton, low, GearKit.gem_mesh(frame, elbow.lerp(wrist, 0.5) + Vector3(0, arm * 1.6, 0), h * 0.012, p.glow), p.glow))
	return made


static func _feet(skeleton: Skeleton3D, frame: Clothing.Frame, class_id: String, rank: String) -> Array[Node]:
	var p := _pal(class_id, rank)
	var trim: Color = p.trim
	var main: Color = p.main
	var accent: Color = p.accent
	var h := frame.height
	var made: Array[Node] = []
	var leg := h * 0.032
	for side in [1.0, -1.0]:
		var suffix := "l" if side > 0 else "r"
		var calf := "calf_" + suffix
		var foot := "foot_" + suffix
		var knee := skeleton.get_bone_global_rest(skeleton.find_bone(calf)).origin
		var ankle := skeleton.get_bone_global_rest(skeleton.find_bone(foot)).origin
		var metal := class_id == "knight" and rank != "D"
		match rank:
			"D":
				if class_id != "knight":
					made.append(NinjaGear._attach(skeleton, calf, GearKit.cuff(frame, knee.lerp(ankle, 0.6), knee.lerp(ankle, 0.82), leg, trim, trim.darkened(0.3)), "cloth", 0.4))
			"C", "B":
				made.append(NinjaGear._attach(skeleton, calf, GearKit.cuff(frame, knee.lerp(ankle, 0.15), knee.lerp(ankle, 0.9), leg * 1.0, main if metal else trim, trim.darkened(0.25)), "metal" if metal else "leather", 0.6))
			"A", "S":
				made.append(NinjaGear._attach(skeleton, calf, GearKit.cuff(frame, knee.lerp(ankle, 0.08), knee.lerp(ankle, 0.94), leg * 1.1, main if class_id in ["knight", "archer"] else trim, accent), "metal", 0.9))
				if rank == "S" and class_id == "knight":
					made.append(NinjaGear._attach(skeleton, calf, Clothing._tube(frame, knee, knee + frame.forward * h * 0.045, [[0.0, leg * 0.9], [1.0, 0.0]], accent, accent), "metal", 1.0))
	return made
