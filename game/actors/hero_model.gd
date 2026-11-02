# Southern Mercenaries — GPL-3.0-or-later
class_name HeroModel
extends Node3D
## Corpo animado do herói (Quaternius, CC0, montado por tools/build_heroes.py):
## o esqueleto e as 43 animações do Universal Animation Library, a cabeça e os
## cabelos do Universal Base Characters e as roupas do Modular Character
## Outfits - Fantasy (Camponês e Ranger), num modelo por sexo. Cada peça é uma
## malha separada: o equipamento aparece no corpo (05-itens-e-loot.md) — sem
## peça no slot, a roupa de Camponês (a "roupa de baixo" do início); com peça,
## a parte de Ranger tingida pela cor do material. Armas vão presas aos ossos.
## Sem o arquivo do modelo (testes sem importação), fica uma cápsula.
##
## Animação dirigida pelo estado que chega a todos os PCs: velocidade (parado,
## andar, correr), ação de uma vez (ataque, magia, tiro, esquiva, golpe
## sofrido), montado, carregando o ataque forte, bloqueando e caído.

const SCENES := {
	"male": "res://assets/models/characters/hero_male.glb",
	"female": "res://assets/models/characters/hero_female.glb",
}
const ANIMS := {
	"idle": "Idle_Loop", "walk": "Walk_Loop", "run": "Jog_Fwd_Loop",
	"melee": "Sword_Attack", "cast": "Spell_Simple_Shoot", "shoot": "Pistol_Shoot",
	"roll": "Roll", "hit": "Hit_Chest", "death": "Death01", "ride": "Driving_Loop",
	"charge": "Spell_Simple_Idle_Loop", "block": "Sword_Idle", "jump": "Jump_Loop",
	# NPCs: sentado, conversando, segurando a tocha, e a gente da rua de Tortuga:
	# caído (bêbado desmaiado), dançando, agachado (mendigo), empurrando carga,
	# sentado conversando (apostadores).
	"sit": "Sitting_Idle_Loop", "talk": "Idle_Talking_Loop", "torch": "Idle_Torch_Loop",
	"lie": "Death01", "dance": "Dance_Loop", "crouch": "Crouch_Idle_Loop", "push": "Push_Loop",
	"sit_talk": "Sitting_Talking_Loop",
	# Briga de rua: socos e o golpe na cabeça.
	"punch_jab": "Punch_Jab", "punch_cross": "Punch_Cross", "hit_head": "Hit_Head",
	# O chute não existe nas bibliotecas: _build_kick() o monta por código (chave "kick").
	# Universal Animation Library 2: combo de espada (o golpe corpo a corpo
	# alterna A, B, C), beber poção, abrir baú, jogado para trás (Rajada das Asas),
	# a Rainha dos Ratos (andar e arranhar de zumbi) e poses de NPC.
	"melee_b": "Sword_Regular_B", "melee_c": "Sword_Regular_C", "drink": "Consume", "open": "Chest_Open",
	"knockback": "Hit_Knockback", "zombie_idle": "Zombie_Idle_Loop", "zombie_walk": "Zombie_Walk_Fwd_Loop",
	"zombie_scratch": "Zombie_Scratch", "fold_arms": "Idle_FoldArms_Loop", "lantern": "Idle_Lantern_Loop",
	"carry": "Walk_Carry_Loop", "rail": "Idle_Rail_Loop",
}
## Golpes corpo a corpo em sequência (dentro de COMBO_WINDOW s, o próximo da lista).
const MELEE_COMBO := ["melee", "melee_b", "melee_c"]
const COMBO_WINDOW := 1.2
## Ninja: corpo próprio (ninja.glb ligado ao mesmo esqueleto e às mesmas animações, tools/assets/build_ninja_hero.py), em quatro
## peças (uma por slot de equipamento) cujo tecido é tingido com a cor do rank (dress_suit); pele e faixa vermelha não mudam.
const NINJA_SCENE := "res://assets/models/characters/hero_ninja.glb"
## A Maga (feminina) tem o corpo do witch.glb pelo mesmo caminho (tools/assets/build_witch_hero.py): o roxo vira a cor do elemento.
const WITCH_SCENE := "res://assets/models/characters/hero_witch.glb"
## A Arqueira (feminina), a Elfa do elf.glb (tools/assets/build_elf_hero.py): o verde-oliva vira a cor do elemento.
const ELF_SCENE := "res://assets/models/characters/hero_elf.glb"
## O Cavaleiro (masculino), o armored-knight do knight.glb (tools/assets/build_knight_hero.py): o azul vira a cor do elemento.
## O Mago (masculino), o wizard do mage.glb (tools/assets/build_mage_hero.py): o azul do manto vira a cor do elemento.
const MAGE_SCENE := "res://assets/models/characters/hero_mage.glb"
## O Arqueiro (masculino), o anão do dwarf.glb (tools/assets/build_dwarf_hero.py): a camisa azul vira a cor do elemento.
const DWARF_SCENE := "res://assets/models/characters/hero_dwarf.glb"
## O corpo do anão é feito ampliado (1,3x) para caber no esqueleto do herói; aqui ele volta ao tamanho de anão.
const SUIT_SCALE := {"Dwarf_": 0.8, "Goblin_": 0.5}
## O Invocador (sem sexo), o goblin do goblin.glb (tools/assets/build_goblin_hero.py): o casaco amarelo vira a cor do elemento.
const GOBLIN_SCENE := "res://assets/models/characters/hero_goblin.glb"
const KNIGHT_SCENE := "res://assets/models/characters/hero_knight.glb"
## A cor da roupa do Ninja identifica o elemento de origem (fogo vermelho, água azul, vento branco, terra verde); o rank não muda a cor.
const SUIT_COLORS := {
	"fire": Color(0.8, 0.22, 0.2), "water": Color(0.27, 0.4, 0.8), "air": Color(0.92, 0.92, 0.9), "earth": Color(0.3, 0.55, 0.28),
}
## Peças por slot de equipamento: sem item, as de Camponês; com item, as de Ranger.
const OUTFIT := {
	"body": [["Peasant_Body", "Peasant_Legs"], ["Ranger_Body", "Ranger_Legs", "Ranger_Acc"]],
	"hands": [["Peasant_Arms"], ["Ranger_Arms"]],
	"feet": [["Peasant_Feet"], ["Ranger_Feet"]],
	"head": [[], ["Ranger_Head_Hood"]],
}
## Sempre à mostra (o rosto); o cabelo vem do visual da classe.
const ALWAYS := ["Head", "Eyes", "Eyebrows"]
## Velocidades (m/s) em que troca para andar e para correr.
const WALK_SPEED := 0.4
const RUN_SPEED := 3.0
const BLEND := 0.12

var skeleton: Skeleton3D
var _anim: AnimationPlayer
var _action := ""
var _current := ""
var _dead := false
## Malhas por nome e materiais (cópias deste herói) com a cor original.
var _parts := {}
var _materials: Array[StandardMaterial3D] = []
var _base_colors: Array[Color] = []
var _hair: Array[String] = []
var _shown_equip := {}
## Nome real de cada animação no arquivo importado (o importador do Godot tira
## o sufixo "_Loop" e marca a animação como repetida).
var _names := {}
## Pose fixa de NPC: volta a ela quando uma ação (soco, golpe sofrido) acaba.
var _pose := ""
## Caído no chão (lie_down): a queda fica parada no último quadro até get_up().
var _held := false
## Sexo do corpo montado ("male"/"female"); as roupas femininas têm paleta própria.
var sex := "male"
var _combo := 0
## Corpo do Ninja (uma peça por slot, tecido tingido pelo rank).
var _suit := false
var suit_element := "fire"
var _suit_worn := false
var _suit_prefix := "Ninja_"
var _suit_ranks := {}
var _last_melee := -10.0


## Monta o corpo do sexo dado, com o cabelo do visual da classe
## ({hair: [nomes], hair_color: [r, g, b], skin: [r, g, b] opcional}).
func setup(sex: String, look: Dictionary, class_id := "") -> void:
	self.sex = sex
	var path: String = SCENES.get(sex, SCENES.male)
	if class_id == "ninja" and ResourceLoader.exists(NINJA_SCENE):
		path = NINJA_SCENE  # os dois sexos usam o mesmo corpo: o Ninja sempre aparece de capuz e máscara
		_suit = true
		_suit_prefix = "Ninja_"
	elif class_id == "mage" and sex == "male" and ResourceLoader.exists(MAGE_SCENE):
		path = MAGE_SCENE
		_suit = true
		_suit_prefix = "Mage_"
	elif class_id == "mage" and sex == "female" and ResourceLoader.exists(WITCH_SCENE):
		path = WITCH_SCENE
		_suit = true
		_suit_prefix = "Witch_"
	elif class_id == "summoner" and ResourceLoader.exists(GOBLIN_SCENE):
		path = GOBLIN_SCENE  # os dois sexos usam o mesmo corpo
		_suit = true
		_suit_prefix = "Goblin_"
	elif class_id == "knight" and ResourceLoader.exists(KNIGHT_SCENE):
		path = KNIGHT_SCENE  # o Cavaleiro é sempre homem
		_suit = true
		_suit_prefix = "Knight_"
	elif class_id == "archer" and sex == "male" and ResourceLoader.exists(DWARF_SCENE):
		path = DWARF_SCENE
		_suit = true
		_suit_prefix = "Dwarf_"
	elif class_id == "archer" and sex == "female" and ResourceLoader.exists(ELF_SCENE):
		path = ELF_SCENE
		_suit = true
		_suit_prefix = "Elf_"
	var scene: PackedScene = load(path) as PackedScene if ResourceLoader.exists(path) else null
	if scene == null:
		_build_capsule()
		return
	var model := scene.instantiate()
	add_child(model)
	if _suit:
		model.scale = Vector3.ONE * float(SUIT_SCALE.get(_suit_prefix, 1.0))
	skeleton = model.find_child("Skeleton3D", true, false) as Skeleton3D
	_anim = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	var hair_color: Array = look.get("hair_color", [0.25, 0.17, 0.1])
	_hair.assign(look.get("hair", []))
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		_parts[String(mesh.name)] = mesh
		var is_hair := String(mesh.name).begins_with("Hair") or String(mesh.name) == "Eyebrows"
		for i in mesh.get_surface_override_material_count():
			var source := mesh.get_active_material(i) as StandardMaterial3D
			if source == null:
				continue
			var copy := source.duplicate() as StandardMaterial3D
			if _suit_prefix != "Ninja_" and String(mesh.name).begins_with(_suit_prefix):
				copy.set_meta("scissor", true)  # tecido e resto dividem as faces por recorte de alfa na textura
			if is_hair:
				copy.albedo_color = Color(hair_color[0], hair_color[1], hair_color[2])
			mesh.set_surface_override_material(i, copy)
			_materials.append(copy)
			_base_colors.append(copy.albedo_color)
	_build_kit_hair(hair_color)
	for material in _materials:
		if material.has_meta("scissor"):
			material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
			material.alpha_scissor_threshold = 0.5
	set_outfit({})
	if look.has("skin"):
		var skin: Array = look.skin
		tint_skin(Color(skin[0], skin[1], skin[2]))
	if _anim:
		if sex == "female":
			_drop_finger_tracks()
		_anim.animation_finished.connect(_on_animation_finished)
		for key: String in ANIMS:
			var wanted: String = ANIMS[key]
			for candidate in [wanted, wanted.trim_suffix("_Loop")]:
				if _anim.has_animation(candidate):
					_names[key] = candidate
					if wanted.ends_with("_Loop"):
						_anim.get_animation(candidate).loop_mode = Animation.LOOP_LINEAR
					break
		_build_kick()
		_play("idle", 0.0)  # sem transição desde a pose de descanso


## As animações giram os dedos pensando no corpo masculino: no esqueleto da heroína eles
## abrem em leque (garras). Sem essas faixas a mão fica na pose de repouso, natural.
func _drop_finger_tracks() -> void:
	for animation_name in _anim.get_animation_list():
		var animation := _anim.get_animation(animation_name)
		for track in range(animation.get_track_count() - 1, -1, -1):
			var bone := String(animation.track_get_path(track).get_concatenated_subnames())
			for finger in ["index_", "middle_", "ring_", "pinky_", "thumb_"]:
				if bone.begins_with(finger):
					animation.remove_track(track)
					break

const KICK := "Kick_Procedural"
const KICK_LENGTH := 0.9
## Quadros do chute (segundos, coxa, canela, em graus sobre o repouso; eixo X do osso, negativo na
## coxa levanta a perna para a frente e positivo na canela dobra o joelho): recolhe o joelho,
## estica a perna à altura da cintura e volta.
const KICK_KEYS := [[0.0, 0.0, 0.0], [0.22, -72.0, 95.0], [0.38, -80.0, 0.0], [0.55, -78.0, 5.0], [0.9, 0.0, 0.0]]


## Monta a animação "kick" (as bibliotecas só têm socos): o Idle com a perna direita trocada.
func _build_kick() -> void:
	if skeleton == null or not _names.has("idle"):
		return
	var library := _anim.get_animation_library("")
	if library == null:
		return
	if not library.has_animation(KICK):
		var kick := _anim.get_animation(_names.idle).duplicate() as Animation
		var prefix := ""
		for track in range(kick.get_track_count() - 1, -1, -1):
			var path := String(kick.track_get_path(track))
			if path.ends_with(":thigh_r") or path.ends_with(":calf_r"):
				prefix = path.substr(0, path.rfind(":") + 1)
				kick.remove_track(track)
		if prefix == "":
			return
		kick.loop_mode = Animation.LOOP_NONE
		kick.length = KICK_LENGTH
		for bone_index in 2:
			var bone := skeleton.find_bone(["thigh_r", "calf_r"][bone_index])
			if bone < 0:
				return
			var rest := skeleton.get_bone_rest(bone).basis.get_rotation_quaternion()
			var track := kick.add_track(Animation.TYPE_ROTATION_3D)
			kick.track_set_path(track, NodePath(prefix + ["thigh_r", "calf_r"][bone_index]))
			for key: Array in KICK_KEYS:
				kick.rotation_track_insert_key(track, key[0], rest * Quaternion(Vector3.RIGHT, deg_to_rad(key[1 + bone_index])))
		library.add_animation(KICK, kick)
	_names["kick"] = KICK


func _on_animation_finished(_name: StringName) -> void:
	if _held:
		return
	if _pose == "lie" and _action == "" and _names.has("lie"):
		_lie_cycle()
		return
	_action = ""
	if _pose != "" and is_inside_tree():
		_play(_pose)


## Mostra as peças conforme o equipamento ({slot: material}); tinge as de Ranger.
func set_outfit(equip: Dictionary) -> void:
	_restore_textures()
	_shown_equip = equip.duplicate()
	if _parts.is_empty():
		return
	if _suit:
		dress_suit({})
		return
	for part_name: String in _parts:
		(_parts[part_name] as MeshInstance3D).visible = part_name in ALWAYS
	var hooded := String(equip.get("head", "")) != ""
	for hair: String in _hair:
		if _parts.has(hair):
			_parts[hair].visible = not hooded or hair == "Hair_Beard"
	for slot: String in OUTFIT:
		var material_id: String = String(equip.get(slot, ""))
		var worn := material_id != "" and GameData.materials.has(material_id)
		var tint := Color.WHITE.lerp(Color(GameData.materials[material_id].color), 0.45) if worn else Color.WHITE
		for prefix: String in OUTFIT[slot][1 if worn else 0]:
			for part_name: String in _parts:
				if part_name.begins_with(prefix):
					var mesh: MeshInstance3D = _parts[part_name]
					mesh.visible = true
					if worn:
						_tint(mesh, tint)


## Esconde toda a roupa de base (o rosto e o cabelo ficam); NinjaGear mostra só o que precisa.
func hide_clothes() -> void:
	_restore_textures()
	if _suit:
		return
	for part_name: String in _parts:
		var mesh: MeshInstance3D = _parts[part_name]
		if part_name in ALWAYS or part_name in _hair:
			continue
		mesh.visible = false


## Corpo do Ninja? (ele se veste com dress_suit, não com peças soltas)
func is_suit() -> bool:
	return _suit


## O Ninja começa sem a roupa ninja (o Camponês de base, com rosto e cabelo) e só a veste ao equipar uma peça.
func suit_worn() -> bool:
	return _suit_worn


## Elemento de origem do Ninja: dá a cor do tecido.
func set_suit_element(element: String) -> void:
	suit_element = element
	if _suit:
		dress_suit(_suit_ranks)


## Veste o corpo do Ninja na cor do elemento (`_ranks` não muda a cor: o rank só dá brilho em torno do herói).
## Só o tecido azul de cada peça muda; botas, luvas, espada, faixa, rosto e mãos ficam como são.
func dress_suit(ranks: Dictionary) -> void:
	_suit_ranks = ranks
	_suit_worn = ["body", "head", "hands", "feet"].any(func(slot: String) -> bool: return String(ranks.get(slot, "")) != "")
	# O Invocador é de outra espécie (goblin): o corpo dele aparece sempre, sem o Camponês, o rosto nem o cabelo humanos.
	var shown := _suit_worn or _suit_prefix == "Goblin_"
	for part_name: String in _parts:
		var piece: MeshInstance3D = _parts[part_name]
		if part_name.begins_with(_suit_prefix):
			piece.visible = shown
		elif part_name.begins_with("Peasant_"):
			piece.visible = not shown
		else:  # rosto e cabelo: a roupa ninja tem capuz e máscara por cima
			piece.visible = not shown and (part_name in ALWAYS or part_name in _hair)
	var tint: Color = SUIT_COLORS.get(suit_element, SUIT_COLORS.fire)
	for part_name: String in _parts:
		var mesh: MeshInstance3D = _parts[part_name]
		if not part_name.begins_with(_suit_prefix):
			continue
		for i in mesh.get_surface_override_material_count():
			var material := mesh.get_surface_override_material(i) as StandardMaterial3D
			var index := _materials.find(material)
			if index >= 0 and String(material.resource_name).contains("Cloth"):
				_base_colors[index] = tint
				material.albedo_color = tint


## Mostra uma parte do corpo pelo nome, tingida de `tint`.
## Com `flat`, troca a textura colorida (o conjunto de origem é verde) pela mesma em tons de cinza:
## guarda costuras, dobras e desgaste, e a cor passa a vir só de `tint`.
func show_part(part_name: String, tint: Color, flat := false) -> void:
	if _parts.has(part_name):
		var mesh: MeshInstance3D = _parts[part_name]
		mesh.visible = true
		_tint(mesh, tint)
		if flat:
			for i in mesh.get_surface_override_material_count():
				var material := mesh.get_surface_override_material(i) as StandardMaterial3D
				if material and material.albedo_texture and not String(material.resource_name).contains("Regular"):
					material.set_meta("original_texture", material.albedo_texture)
					material.albedo_texture = _grey_texture(material.albedo_texture)


static var _grey_cache := {}


static func _grey_texture(texture: Texture2D) -> Texture2D:
	var key := texture.resource_path if texture.resource_path != "" else str(texture.get_rid())
	if _grey_cache.has(key):
		return _grey_cache[key]
	var image := texture.get_image()
	if image == null:
		return texture
	if image.is_compressed():
		image.decompress()
	image.convert(Image.FORMAT_L8)
	image.convert(Image.FORMAT_RGB8)
	image.adjust_bcs(1.25, 1.4, 1.0)  # mais luz e contraste: costuras e dobras aparecem sob a cor do rank
	image.generate_mipmaps()
	var grey := ImageTexture.create_from_image(image)
	_grey_cache[key] = grey
	return grey


## Esconde uma parte do corpo pelo nome.
func hide_part(part_name: String) -> void:
	if _parts.has(part_name):
		(_parts[part_name] as MeshInstance3D).visible = false


## Devolve as texturas trocadas por show_part(flat).
func _restore_textures() -> void:
	for material in _materials:
		if material.has_meta("original_texture"):
			material.albedo_texture = material.get_meta("original_texture")
			material.remove_meta("original_texture")


## Penteados montados por código (HairKit): entram em `_parts` com o nome do estilo, como as malhas.
func _build_kit_hair(hair_color: Array) -> void:
	var frame: Clothing.Frame = null
	for style in _hair:
		if not HairKit.is_kit(style):
			continue
		if frame == null:
			frame = Clothing._measure(self, skeleton, Clothing.HERO_BONES)
		var piece := HairKit.build(skeleton, frame, style, Color(hair_color[0], hair_color[1], hair_color[2]))
		if piece:
			_parts[style] = piece


## Cabelo e barba somem (capuz, máscara ou elmo por cima); `keep_beard` deixa a barba.
func hide_hair(keep_beard := true) -> void:
	for hair_name: String in _hair:
		if _parts.has(hair_name) and not (keep_beard and hair_name == "Hair_Beard"):
			_parts[hair_name].visible = false


func outfit() -> Dictionary:
	return _shown_equip


## Peças à mostra agora (testes e capturas).
func visible_parts() -> Array[String]:
	var shown: Array[String] = []
	for part_name: String in _parts:
		if _parts[part_name].visible:
			shown.append(part_name)
	return shown


## Esconde peças (a Rainha dos Ratos: sem cabeça humana, a de rato no lugar).
func hide_parts(names: Array) -> void:
	for part_name: String in names:
		if _parts.has(part_name):
			(_parts[part_name] as MeshInstance3D).visible = false


## Pinta a pele (materiais "Regular": braços, mãos) — a pelagem da Rainha.
func tint_skin(color: Color) -> void:
	for i in _materials.size():
		if String(_materials[i].resource_name).contains("Regular"):
			_base_colors[i] = color
			_materials[i].albedo_color = color


## Toca uma animação pela chave (idle, walk, run, melee, hit, death…), sem a
## lógica de estado do herói (monstros de corpo humano).
func play_key(key: String, blend := BLEND) -> void:
	if _anim and _names.has(key):
		_action = ""
		_play(key, blend)


## Golpe sofrido (pisca vermelho), invisível (Bomba de Fumaça) e o brilho do
## conjunto de armadura em +4 (Color com alfa 0 = sem brilho).
func set_effects(flash: bool, alpha: float, glow: Color) -> void:
	for i in _materials.size():
		var material := _materials[i]
		var color := _base_colors[i]
		material.albedo_color = Color(color.r, color.g * 0.4, color.b * 0.4, alpha) if flash \
			else Color(color.r, color.g, color.b, alpha)
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA if alpha < 1.0 \
			else (BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR if material.has_meta("scissor") else BaseMaterial3D.TRANSPARENCY_DISABLED)
		material.emission_enabled = glow.a > 0.0
		if glow.a > 0.0:
			material.emission = glow
			material.emission_energy_multiplier = 0.25


## Prende `node` ao osso (mão, antebraço, peito…), com um deslocamento local.
## Sem esqueleto, fica preso ao próprio corpo em `fallback`.
func attach(bone: String, node: Node3D, offset := Transform3D.IDENTITY, fallback := Vector3.ZERO) -> void:
	if skeleton == null or skeleton.find_bone(bone) < 0:
		node.position = fallback
		add_child(node)
		return
	var holder := BoneAttachment3D.new()
	holder.bone_name = bone
	skeleton.add_child(holder)
	node.transform = offset
	holder.add_child(node)


## Asas de revoada (Fuga em Bando): brotam das costas do herói, batem (a animação "Fly" do arquivo, as duas asas juntas) e se recolhem. Só visual, em todos os PCs.
## O arquivo está em centímetros (as malhas vêm escaladas por 100 no Godot): WINGS_SCALE leva cada asa a ~0,8 m (o herói mede ~1 m e os ombros ficam em y ≈ 0,7); o osso da raiz fica nas costas, na altura do ombro.
const WINGS_SCENE := "res://assets/models/props/Hero_Wings.glb"
const WINGS_SCALE := 0.0029
const WINGS_ROOT := Vector3(0.0, 142.9, -39.7)  # onde fica a raiz das asas no arquivo (já com a escala de 100)


func show_wings(duration := 1.0) -> void:
	if not ResourceLoader.exists(WINGS_SCENE):
		return
	var pivot := Node3D.new()
	pivot.position = Vector3(0.0, 0.7, -0.07)  # ombros, um pouco atrás do corpo
	add_child(pivot)
	var wings := (load(WINGS_SCENE) as PackedScene).instantiate() as Node3D
	wings.scale = Vector3.ONE * WINGS_SCALE
	wings.position = -WINGS_ROOT * WINGS_SCALE  # a raiz das asas no pivô
	pivot.add_child(wings)
	var player := wings.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if player:
		var left: Animation = null
		var right: Animation = null
		for anim_name in player.get_animation_list():
			if String(anim_name).ends_with("Fly"):
				if String(anim_name).begins_with("Armature_001"):
					right = player.get_animation(anim_name)
				elif String(anim_name).begins_with("Armature|"):
					left = player.get_animation(anim_name)
		if left and right:
			var both := left.duplicate() as Animation  # as duas asas batem juntas
			for i in right.get_track_count():
				right.copy_track(i, both)
			both.loop_mode = Animation.LOOP_LINEAR
			var library := AnimationLibrary.new()
			library.add_animation("both", both)
			player.add_animation_library("wings", library)
			player.play("wings/both")
	pivot.scale = Vector3.ONE * 0.05
	var tween := pivot.create_tween()
	tween.tween_property(pivot, "scale", Vector3.ONE, 0.12).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tween.tween_interval(maxf(duration - 0.4, 0.1))
	tween.tween_property(pivot, "scale", Vector3.ONE * 0.05, 0.25).set_ease(Tween.EASE_IN)
	tween.tween_callback(pivot.queue_free)


## Uma ação de uma vez (ataque, magia, esquiva…): toca por cima da locomoção.
func play_action(kind: String) -> void:
	if _anim == null or _dead or not _names.has(kind):
		return
	_action = kind
	_anim.stop()
	var anim_key := kind
	if kind == "melee":
		# Combo de espada: A, B, C se os golpes vêm seguidos.
		var now := Time.get_ticks_msec() / 1000.0
		_combo = (_combo + 1) % MELEE_COMBO.size() if now - _last_melee < COMBO_WINDOW else 0
		_last_melee = now
		anim_key = MELEE_COMBO[_combo] if _names.has(MELEE_COMBO[_combo]) else "melee"
	_play(anim_key, 0.05)


## Cai no chão e fica lá (a queda para no último quadro) até get_up().
func lie_down() -> void:
	if _anim == null or not _names.has("lie"):
		return
	_held = true
	_action = "lie"
	_anim.play(_names.lie, 0.05)


## Levanta devagar: toca a queda de trás para a frente em câmera lenta. Devolve quanto tempo
## leva (s); no fim volta à pose fixa.
func get_up(speed := 0.3) -> float:
	if _anim == null or not _names.has("lie"):
		return 0.0
	_held = false
	_anim.play(_names.lie, 0.0, -speed, true)
	return _anim.get_animation(_names.lie).length / speed


## Estado contínuo, a cada quadro.
func update_state(speed: float, alive: bool, mounted: bool, charging: bool, blocking: bool, airborne := false) -> void:
	if _anim == null:
		return
	if not alive:
		if not _dead:
			_dead = true
			_action = ""
			_play("death")
		return
	_dead = false
	if _action != "":
		return
	var state := "idle"
	if airborne and not mounted:
		state = "jump"
	elif mounted:
		state = "ride"
	elif blocking:
		state = "block"
	elif charging:
		state = "charge"
	elif speed > RUN_SPEED:
		state = "run"
	elif speed > WALK_SPEED:
		state = "walk"
	if state != _current:
		_play(state)


## Pose fixa de NPC (sit, talk, torch, idle), em repetição.
func set_pose(key: String) -> void:
	_pose = key if _names.has(key) else "idle"
	_lie_rising = false
	if _anim:
		_play(_pose, 0.0)


## Bêbado deitado (pose "lie"): cai, fica no chão um bom tempo (parado no último quadro), levanta devagar,
## fica um pouco de pé e cai de novo. Antes a queda recomeçava do início assim que terminava.
const LIE_HOLD := Vector2(40.0, 70.0)
const LIE_STAND := 4.0
const LIE_RISE_SPEED := 0.3
var _lie_rising := false


func _lie_cycle() -> void:
	if not is_inside_tree():
		return
	if _lie_rising:
		# Acabou de levantar: espera de pé e cai de novo.
		_lie_rising = false
		await get_tree().create_timer(LIE_STAND).timeout
		if _pose == "lie" and _action == "" and is_inside_tree():
			_anim.play(_names.lie, 0.0)
		return
	# Acabou de cair: fica no chão.
	await get_tree().create_timer(randf_range(LIE_HOLD.x, LIE_HOLD.y)).timeout
	if _pose == "lie" and _action == "" and is_inside_tree():
		_lie_rising = true
		_anim.play(_names.lie, 0.0, -LIE_RISE_SPEED, true)


## Começa a pose fixa num ponto do ciclo (0..1), para um grupo não ficar em uníssono.
func desync(fraction: float) -> void:
	if _anim and _anim.current_animation != "":
		_anim.seek(_anim.current_animation_length * fraction, true)


func current() -> String:
	return _action if _action != "" else _current


func _tint(mesh: MeshInstance3D, tint: Color) -> void:
	for i in mesh.get_surface_override_material_count():
		var material := mesh.get_surface_override_material(i) as StandardMaterial3D
		var index := _materials.find(material)
		# A pele dos braços (material do corpo) não é tingida.
		if index >= 0 and not String(material.resource_name).contains("Regular"):
			_base_colors[index] = tint
			material.albedo_color = tint


func _build_capsule() -> void:
	var body := MeshInstance3D.new()
	var capsule := CapsuleMesh.new()
	capsule.radius = 0.35
	capsule.height = 1.7
	body.mesh = capsule
	body.position.y = 0.85
	var material := StandardMaterial3D.new()
	material.albedo_color = Color(0.78, 0.72, 0.6)
	body.material_override = material
	add_child(body)
	_materials.append(material)
	_base_colors.append(material.albedo_color)


## Animações que este modelo tem (testes).
func animations() -> Array:
	return _names.keys()


func _play(key: String, blend := BLEND) -> void:
	var anim_name: String = _names.get(key, "")
	if anim_name == "":
		return
	_current = key
	_anim.play(anim_name, blend)
