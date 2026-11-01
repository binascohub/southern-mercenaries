# Southern Mercenaries — GPL-3.0-or-later
class_name NpcModel
extends Node3D
## Corpo de NPC num modelo próprio (fora dos heróis): o arquivo, a escala para
## a altura do jogo e as animações por pose. Mesma interface de pose que o
## HeroModel usa com o Wanderer (set_pose): "walk" anda; as outras ficam paradas
## na pose de andar (sem animação de parado no arquivo) ou na animação dada.

## Materiais pintados (tipo, cor, tamanho da repetição em unidades do arquivo).
const COURTESAN_PAINT := {
	"skin": ["skin", [0.84, 0.64, 0.50], 1.3],
	"mouth": ["skin", [0.62, 0.22, 0.22], 1.3],
	"hair": ["hair", [0.14, 0.09, 0.06], 1.1],
	"hair.001": ["hair", [0.14, 0.09, 0.06], 1.1],
	"bra": ["cloth", [0.27, 0.36, 0.50], 0.65],
	"trouser": ["cloth", [0.42, 0.26, 0.34], 0.65],
	"shoe": ["leather", [0.30, 0.20, 0.13], 0.8],
}
## Danças da cortesã (o arquivo só tem andar e correr). Por osso: [eixo (0 X inclina
## de lado, 1 Y torce, 2 Z inclina para frente), posição média, amplitude, ciclos, fase],
## somados à pose-base (tronco e braços do "walk", pernas do esqueleto em repouso).
## Os braços "_R" abrem com Z positivo; os "_L" são espelhados (Z negativo).
const DANCES := {
	# Sensual e lenta: quadril balançando, braços para o alto.
	"dance_sway": {"length": 3.2, "bones": {
		"hips": [[0, 0.0, 0.18, 1, 0.0], [1, 0.0, 0.30, 1, 1.57]],
		"spine": [[0, 0.0, 0.12, 1, 3.14], [1, 0.0, 0.18, 1, -1.57]],
		"kopf": [[0, 0.0, 0.12, 1, 3.14]],
		"oberArm_R": [[2, 2.5, 0.25, 1, 0.0]], "unterarm_R": [[0, 0.5, 0.3, 1, 1.57]],
		"oberArm_L": [[2, -2.5, 0.25, 1, 3.14]], "unterarm_L": [[0, -0.5, 0.3, 1, 1.57]]}},
	# Giro de quadril e uma mão no cabelo: a mais provocante.
	"dance_hips": {"length": 2.8, "bones": {
		"hips": [[0, 0.0, 0.30, 1, 0.0], [1, 0.0, 0.40, 1, 1.57], [2, 0.0, 0.08, 1, 3.14]],
		"spine": [[0, 0.0, 0.15, 1, 3.14], [1, 0.0, 0.20, 1, -1.57]],
		"brust": [[0, 0.0, 0.10, 1, 3.14]],
		"kopf": [[0, 0.0, 0.15, 1, 3.14]],
		"oberArm_R": [[2, 2.8, 0.15, 1, 0.0]], "unterarm_R": [[0, 1.4, 0.2, 1, 0.0]],
		"oberArm_L": [[2, -0.5, 0.25, 1, 1.57]],
		"unterSchenkel_L": [[2, 0.35, 0.2, 1, 0.0]], "unterSchenkel_R": [[2, 0.35, 0.2, 1, 3.14]]}},
	# Rodopio de braços abertos (gira o corpo todo, ver DANCE_STYLE).
	"dance_twirl": {"length": 1.6, "bones": {
		"hips": [[1, 0.0, 0.25, 2, 0.0], [0, 0.0, 0.08, 2, 1.57]],
		"oberArm_R": [[2, 1.3, 0.1, 2, 0.0]], "oberArm_L": [[2, -1.3, 0.1, 2, 3.14]],
		"oberSchenkel_L": [[2, 0.0, 0.45, 1, 0.0]], "oberSchenkel_R": [[2, 0.0, 0.45, 1, 3.14]],
		"unterSchenkel_L": [[2, 0.3, 0.3, 1, 1.57]], "unterSchenkel_R": [[2, 0.3, 0.3, 1, 4.71]]}},
	# Farra: pulos, braços alternados para o alto e joelhos para cima.
	"dance_wild": {"length": 1.2, "bones": {
		"hips": [[0, 0.0, 0.15, 2, 0.0], [2, 0.0, 0.12, 2, 1.57]],
		"spine": [[2, 0.0, 0.15, 2, 0.0]], "kopf": [[0, 0.0, 0.2, 2, 1.57]],
		"oberArm_R": [[2, 2.2, 0.5, 1, 0.0]], "oberArm_L": [[2, -2.2, 0.5, 1, 3.14]],
		"unterSchenkel_L": [[2, 0.5, 0.5, 2, 0.0]], "unterSchenkel_R": [[2, 0.5, 0.5, 2, 3.14]],
		"oberSchenkel_L": [[2, 0.0, 0.35, 1, 0.0]], "oberSchenkel_R": [[2, 0.0, 0.35, 1, 3.14]]}},
}
## Movimentos do corpo todo durante a dança: giro (rad/s) e pulo (m).
const DANCE_STYLE := {
	"dance_twirl": {"spin": 2.2},
	"dance_wild": {"bounce": 0.08},
}
const COURTESAN_POSES := {"walk": "walk", "run": "run", "dance_sway": "dance_sway",
	"dance_hips": "dance_hips", "dance_twirl": "dance_twirl", "dance_wild": "dance_wild"}

const MODELS := {
	# Cortesã de Tortuga (Female NPC, umask007, CC BY 3.0): top decotado, short e botas.
	"courtesan": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT},
	# Segunda cortesã: o mesmo corpo nas cores da Tetine Elfe (escolha do autor):
	# top, short e botas de couro vermelho e cabelo ruivo.
	"courtesan_red": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT,
		"colors": {"bra": [0.50, 0.10, 0.09], "trouser": [0.42, 0.08, 0.07], "shoe": [0.40, 0.10, 0.08],
			"hair": [0.40, 0.15, 0.07], "hair.001": [0.40, 0.15, 0.07]}},
	# Mais cortesãs, cada uma com seu jeito: esmeralda, preto com loira, dourado e linho.
	"courtesan_green": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT,
		"colors": {"skin": [0.80, 0.58, 0.45], "bra": [0.12, 0.35, 0.22], "trouser": [0.10, 0.25, 0.18],
			"shoe": [0.22, 0.14, 0.09], "hair": [0.07, 0.05, 0.04], "hair.001": [0.07, 0.05, 0.04]}},
	"courtesan_black": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT,
		"colors": {"skin": [0.90, 0.72, 0.60], "bra": [0.08, 0.08, 0.10], "trouser": [0.12, 0.08, 0.10],
			"shoe": [0.10, 0.08, 0.07], "hair": [0.72, 0.62, 0.40], "hair.001": [0.72, 0.62, 0.40]}},
	"courtesan_gold": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT,
		"colors": {"skin": [0.55, 0.38, 0.28], "bra": [0.70, 0.52, 0.18], "trouser": [0.55, 0.30, 0.12],
			"shoe": [0.30, 0.18, 0.10], "hair": [0.12, 0.07, 0.05], "hair.001": [0.12, 0.07, 0.05]}},
	"courtesan_white": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT,
		"colors": {"skin": [0.72, 0.50, 0.38], "bra": [0.80, 0.76, 0.66], "trouser": [0.70, 0.65, 0.55],
			"shoe": [0.35, 0.24, 0.15], "hair": [0.50, 0.22, 0.09], "hair.001": [0.50, 0.22, 0.09]}},
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
var _spin := 0.0
var _bounce := 0.0
var _dance_time := 0.0


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
	var colors: Dictionary = info.get("colors", {})
	if info.has("paint"):
		_paint(model, info.paint, colors)
	# Cores por material (variantes do mesmo modelo).
	if not colors.is_empty() and not info.has("paint"):
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
	if npc._anim and info.get("dances", false):
		npc._make_dances()
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


## Aplica os materiais pintados (PaintedTextures) por nome de material do arquivo:
## {nome: [tipo, cor, tamanho de uma repetição]}. A cor pode ser trocada por
## "colors" (variantes do mesmo modelo). Materiais fora da lista ficam como vieram.
static func _paint(model: Node, paint: Dictionary, colors: Dictionary) -> void:
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for i in mesh.get_surface_override_material_count():
			var source := mesh.get_active_material(i) as StandardMaterial3D
			if source == null or not paint.has(String(source.resource_name)):
				continue
			var entry: Array = paint[String(source.resource_name)]
			var c: Array = colors.get(String(source.resource_name), entry[1])
			mesh.set_surface_override_material(i, PaintedTextures.material(source, entry[0], Color(c[0], c[1], c[2]), float(entry[2])))


## Cria as animações de dança (DANCES) a partir do "walk": ossos sem dança ficam
## parados na pose-base e a pose-base de tronco e braços vem do primeiro quadro do "walk".
func _make_dances() -> void:
	if not _anim.has_animation("walk") or _anim.has_animation("dance_sway"):
		return
	var skeleton := _anim.get_parent().find_child("Skeleton3D", true, false) as Skeleton3D
	if skeleton == null:
		return
	var walk := _anim.get_animation("walk")
	for dance_name: String in DANCES:
		var data: Dictionary = DANCES[dance_name]
		var length: float = data.length
		var dance := Animation.new()
		dance.length = length
		dance.loop_mode = Animation.LOOP_LINEAR
		var moves: Dictionary = data.bones
		for t in walk.get_track_count():
			var path := walk.track_get_path(t)
			var bone_name := String(path.get_concatenated_subnames())
			var type := walk.track_get_type(t)
			if type != Animation.TYPE_ROTATION_3D and type != Animation.TYPE_POSITION_3D and type != Animation.TYPE_SCALE_3D:
				continue
			var track := dance.add_track(type)
			dance.track_set_path(track, path)
			if type != Animation.TYPE_ROTATION_3D:
				var value: Variant = walk.position_track_interpolate(t, 0.0) if type == Animation.TYPE_POSITION_3D else walk.scale_track_interpolate(t, 0.0)
				dance.track_insert_key(track, 0.0, value)
				dance.track_insert_key(track, length, value)
				continue
			var base: Quaternion = walk.rotation_track_interpolate(t, 0.0)
			if bone_name.begins_with("oberSchenkel") or bone_name.begins_with("unterSchenkel") or bone_name.begins_with("fuss"):
				base = skeleton.get_bone_rest(skeleton.find_bone(bone_name)).basis.get_rotation_quaternion()
			if not moves.has(bone_name):
				dance.rotation_track_insert_key(track, 0.0, base)
				dance.rotation_track_insert_key(track, length, base)
				continue
			var steps := 24
			for k in steps + 1:
				var angles := [0.0, 0.0, 0.0]
				for move: Array in moves[bone_name]:
					angles[int(move[0])] += float(move[1]) + float(move[2]) * sin(TAU * float(move[3]) * k / steps + float(move[4]))
				var q := base * Quaternion(Vector3.RIGHT, angles[0]) * Quaternion(Vector3.UP, angles[1]) * Quaternion(Vector3.BACK, angles[2])
				dance.rotation_track_insert_key(track, length * k / steps, q)
		_anim.get_animation_library("").add_animation(dance_name, dance)


func _process(delta: float) -> void:
	if _spin != 0.0 or _bounce != 0.0:
		_dance_time += delta
		rotation.y += _spin * delta
		position.y = absf(sin(_dance_time * 6.0)) * _bounce


func set_pose(key: String) -> void:
	var style: Dictionary = DANCE_STYLE.get(key, {})
	_spin = float(style.get("spin", 0.0))
	_bounce = float(style.get("bounce", 0.0))
	if _spin == 0.0 and _bounce == 0.0:
		position.y = 0.0
	if _anim == null:
		return
	if _poses.has(key) and _anim.has_animation(_poses[key]):
		_anim.play(_poses[key], 0.15)
	else:
		# Parada: a pose de andar congelada no primeiro quadro.
		_anim.play(_poses.get("walk", ""), 0.15)
		_anim.seek(0.0, true)
		_anim.pause()
