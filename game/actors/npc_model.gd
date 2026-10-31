# Southern Mercenaries — GPL-3.0-or-later
class_name NpcModel
extends Node3D
## Corpo de NPC num modelo próprio (fora dos heróis): o arquivo, a escala para
## a altura do jogo e as animações por pose. Mesma interface de pose que o
## HeroModel usa com o Wanderer (set_pose): "walk" anda; as outras ficam paradas
## na pose de andar (sem animação de parado no arquivo) ou na animação dada.

const MODELS := {
	# Cortesã de Tortuga (Female NPC, umask007, CC BY 3.0): top decotado, short e botas.
	"courtesan": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": {"walk": "walk", "run": "run"}},
}

var _anim: AnimationPlayer
var _poses := {}


static func has_model(id: String) -> bool:
	return MODELS.has(id) and ResourceLoader.exists(MODELS[id].scene)


static func create(id: String) -> NpcModel:
	if not has_model(id):
		return null
	var npc := NpcModel.new()
	var info: Dictionary = MODELS[id]
	var model := (load(info.scene) as PackedScene).instantiate()
	npc.add_child(model)
	npc.scale = Vector3.ONE * float(info.scale)
	npc._poses = info.poses
	npc._anim = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if npc._anim:
		for anim_name: String in npc._poses.values():
			if npc._anim.has_animation(anim_name):
				npc._anim.get_animation(anim_name).loop_mode = Animation.LOOP_LINEAR
	return npc


func set_pose(key: String) -> void:
	if _anim == null:
		return
	if _poses.has(key) and _anim.has_animation(_poses[key]):
		_anim.play(_poses[key], 0.15)
	else:
		# Parada: a pose de andar congelada no primeiro quadro.
		_anim.play(_poses.get("walk", ""), 0.15)
		_anim.seek(0.0, true)
		_anim.pause()
