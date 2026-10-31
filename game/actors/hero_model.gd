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
	"charge": "Spell_Simple_Idle_Loop", "block": "Sword_Idle",
	# NPCs: sentado, conversando, segurando a tocha, e a gente da rua de Tortuga:
	# caído (bêbado desmaiado), dançando, agachado (mendigo), empurrando carga,
	# sentado conversando (apostadores).
	"sit": "Sitting_Idle_Loop", "talk": "Idle_Talking_Loop", "torch": "Idle_Torch_Loop",
	"lie": "Death01", "dance": "Dance_Loop", "crouch": "Crouch_Idle_Loop", "push": "Push_Loop",
	"sit_talk": "Sitting_Talking_Loop",
	# Briga de rua: socos e o golpe na cabeça.
	"punch_jab": "Punch_Jab", "punch_cross": "Punch_Cross", "hit_head": "Hit_Head",
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


## Monta o corpo do sexo dado, com o cabelo do visual da classe
## ({hair: [nomes], hair_color: [r, g, b]}).
func setup(sex: String, look: Dictionary) -> void:
	var path: String = SCENES.get(sex, SCENES.male)
	var scene: PackedScene = load(path) as PackedScene if ResourceLoader.exists(path) else null
	if scene == null:
		_build_capsule()
		return
	var model := scene.instantiate()
	add_child(model)
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
			if is_hair:
				copy.albedo_color = Color(hair_color[0], hair_color[1], hair_color[2])
			mesh.set_surface_override_material(i, copy)
			_materials.append(copy)
			_base_colors.append(copy.albedo_color)
	set_outfit({})
	if _anim:
		_anim.animation_finished.connect(func(_name: StringName) -> void:
			_action = ""
			if _pose != "":
				_play(_pose))
		for key: String in ANIMS:
			var wanted: String = ANIMS[key]
			for candidate in [wanted, wanted.trim_suffix("_Loop")]:
				if _anim.has_animation(candidate):
					_names[key] = candidate
					if wanted.ends_with("_Loop"):
						_anim.get_animation(candidate).loop_mode = Animation.LOOP_LINEAR
					break
		_play("idle", 0.0)  # sem transição desde a pose de descanso


## Mostra as peças conforme o equipamento ({slot: material}); tinge as de Ranger.
func set_outfit(equip: Dictionary) -> void:
	_shown_equip = equip.duplicate()
	if _parts.is_empty():
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


func outfit() -> Dictionary:
	return _shown_equip


## Peças à mostra agora (testes e capturas).
func visible_parts() -> Array[String]:
	var shown: Array[String] = []
	for part_name: String in _parts:
		if _parts[part_name].visible:
			shown.append(part_name)
	return shown


## Golpe sofrido (pisca vermelho), invisível (Bomba de Fumaça) e o brilho do
## conjunto de armadura em +4 (Color com alfa 0 = sem brilho).
func set_effects(flash: bool, alpha: float, glow: Color) -> void:
	for i in _materials.size():
		var material := _materials[i]
		var color := _base_colors[i]
		material.albedo_color = Color(color.r, color.g * 0.4, color.b * 0.4, alpha) if flash \
			else Color(color.r, color.g, color.b, alpha)
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA if alpha < 1.0 else BaseMaterial3D.TRANSPARENCY_DISABLED
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


## Uma ação de uma vez (ataque, magia, esquiva…): toca por cima da locomoção.
func play_action(kind: String) -> void:
	if _anim == null or _dead or not _names.has(kind):
		return
	_action = kind
	_anim.stop()
	_play(kind, 0.05)


## Estado contínuo, a cada quadro.
func update_state(speed: float, alive: bool, mounted: bool, charging: bool, blocking: bool) -> void:
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
	if mounted:
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
	if _anim:
		_play(_pose, 0.0)


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
