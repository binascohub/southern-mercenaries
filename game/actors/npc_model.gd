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
	# Segunda cortesã: o mesmo corpo nas cores da Tetine Elfe (escolha do autor):
	# top, short e botas de couro vermelho e cabelo ruivo.
	"courtesan_red": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": {"walk": "walk", "run": "run"},
		"colors": {"bra": [0.62, 0.06, 0.05], "trouser": [0.5, 0.05, 0.04], "shoe": [0.55, 0.08, 0.06],
			"hair": [0.5, 0.16, 0.06], "hair.001": [0.5, 0.16, 0.06]}},
	# Capitão pirata (Clint Bellanger, CC BY 3.0): preso ao esqueleto dos heróis
	# por tools/assets/rig_to_ual.py, com as animações deles; texturas geradas.
	"pirate_captain": {"scene": "res://assets/models/characters/pirate_captain.glb", "scale": 1.0,
		"poses": {"walk": "Walk_Loop", "idle": "Idle_Loop", "talk": "Idle_Talking_Loop", "drink": "Consume"}},
	# Guarda (Brigand, anthonymyers, CC BY 3.0): parado na pose do modelo, de
	# couraça, alabarda e machado (sem animação).
	"guard": {"scene": "res://assets/models/characters/brigand_guard.glb", "scale": 1.0, "poses": {}},
	# Aranhinha do esgoto (Spider animated, pantherone, CC BY 3.0): não ataca,
	# só anda pelo chão. Arquivo de 1 m -> 40 cm, avermelhada (decisão do autor).
	"spider": {"scene": "res://assets/models/monsters/spider.glb", "scale": 0.4,
		"poses": {"walk": "walk", "idle": "idle", "talk": "idle"},
		"colors": {"Spider": [0.55, 0.1, 0.06]}},
	# Galinha (cdmir, CC0): anda e cisca pelas cozinhas de Tortuga (12,6 unidades -> 0,4 m).
	"chicken": {"scene": "res://assets/models/characters/chicken.glb", "scale": 0.032,
		"poses": {"walk": "walk", "idle": "eat", "talk": "idle"}},
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
	npc._poses = info.poses.duplicate()
	# Cores por material (variantes do mesmo modelo).
	var colors: Dictionary = info.get("colors", {})
	if not colors.is_empty():
		for node in model.find_children("*", "MeshInstance3D", true, false):
			var mesh := node as MeshInstance3D
			for i in mesh.get_surface_override_material_count():
				var source := mesh.get_active_material(i) as StandardMaterial3D
				if source and colors.has(String(source.resource_name)):
					var c: Array = colors[String(source.resource_name)]
					var copy := source.duplicate() as StandardMaterial3D
					copy.albedo_color = Color(c[0], c[1], c[2])
					mesh.set_surface_override_material(i, copy)
	npc._anim = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if npc._anim:
		# O importador do Godot tira o "_Loop" do nome (e marca a repetição).
		for key: String in npc._poses.keys():
			var anim_name: String = npc._poses[key]
			for candidate in [anim_name, anim_name.trim_suffix("_Loop")]:
				if npc._anim.has_animation(candidate):
					npc._poses[key] = candidate
					npc._anim.get_animation(candidate).loop_mode = Animation.LOOP_LINEAR
					break
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
