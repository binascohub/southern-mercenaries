# Southern Mercenaries — GPL-3.0-or-later
class_name HeroModel
extends Node3D
## Corpo animado do herói: o manequim do Universal Animation Library
## (Quaternius, CC0) com 43 animações no esqueleto padrão. Quando o pacote de
## roupas modulares (mesmo esqueleto) entrar, só a malha muda. Armas e peças de
## equipamento vão presas aos ossos (attach). Sem o arquivo do modelo (testes
## sem importação), fica uma cápsula, como antes.
##
## Animação dirigida pelo estado que chega a todos os PCs: velocidade (parado,
## andar, correr), ação de uma vez (ataque, magia, tiro, esquiva, golpe
## sofrido), montado, carregando o ataque forte, bloqueando e caído.

const SCENE := "res://assets/models/characters/ual_mannequin.glb"
const ANIMS := {
	"idle": "Idle_Loop", "walk": "Walk_Loop", "run": "Jog_Fwd_Loop",
	"melee": "Sword_Attack", "cast": "Spell_Simple_Shoot", "shoot": "Pistol_Shoot",
	"roll": "Roll", "hit": "Hit_Chest", "death": "Death01", "ride": "Driving_Loop",
	"charge": "Spell_Simple_Idle_Loop", "block": "Sword_Idle",
}
## Velocidades (m/s) em que troca para andar e para correr.
const WALK_SPEED := 0.4
const RUN_SPEED := 3.0
const BLEND := 0.12

var skeleton: Skeleton3D
var body: MeshInstance3D
var _anim: AnimationPlayer
var _action := ""
var _current := ""
var _dead := false


## O corpo (ou a cápsula de reserva) com o material dado.
func setup(material: StandardMaterial3D) -> void:
	var scene: PackedScene = load(SCENE) as PackedScene if ResourceLoader.exists(SCENE) else null
	if scene == null:
		body = MeshInstance3D.new()
		var capsule := CapsuleMesh.new()
		capsule.radius = 0.35
		capsule.height = 1.7
		body.mesh = capsule
		body.position.y = 0.85
		body.material_override = material
		add_child(body)
		return
	var model := scene.instantiate()
	add_child(model)
	skeleton = model.find_child("Skeleton3D", true, false) as Skeleton3D
	_anim = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		if mesh.name.begins_with("Mannequin"):
			body = mesh
			mesh.material_override = material
		else:
			mesh.visible = false  # o "Icosphere" de referência do pacote
	if _anim:
		_anim.animation_finished.connect(func(_name: StringName) -> void: _action = "")
		for key: String in ANIMS:
			var anim_name: String = ANIMS[key]
			if _anim.has_animation(anim_name) and anim_name.ends_with("_Loop"):
				_anim.get_animation(anim_name).loop_mode = Animation.LOOP_LINEAR
		_play("idle")


## Prende `node` ao osso (mão, cabeça, pé…), com um deslocamento local.
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
	if _anim == null or _dead or not ANIMS.has(kind):
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


func current() -> String:
	return _action if _action != "" else _current


func _play(key: String, blend := BLEND) -> void:
	var anim_name: String = ANIMS.get(key, "")
	if not _anim.has_animation(anim_name):
		return
	_current = key
	_anim.play(anim_name, blend)
