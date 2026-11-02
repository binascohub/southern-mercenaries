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
## Variações da dança profissional dos heróis (DanceRetarget): espelhada ou não, quadril mais
## ou menos marcado e velocidade. As danças acima só entram se o retarget falhar.
const DANCE_UAL := {
	"dance_sway": {"mirror": false, "hips": 1.8, "speed": 0.8},   # lenta, de quadril
	"dance_hips": {"mirror": true, "hips": 1.4, "speed": 0.9},
	"dance_twirl": {"mirror": false, "hips": 1.0, "speed": 1.1},  # gira o corpo todo (DANCE_STYLE)
	"dance_wild": {"mirror": true, "hips": 1.0, "speed": 1.3},    # farra, com pulos
}
## Movimentos do corpo todo durante a dança: giro (rad/s) e pulo (m).
const DANCE_STYLE := {
	"dance_twirl": {"spin": 2.2},
	"dance_wild": {"bounce": 0.08},
}
const COURTESAN_POSES := {"walk": "walk", "run": "run", "dance_sway": "dance_sway",
	"dance_hips": "dance_hips", "dance_twirl": "dance_twirl", "dance_wild": "dance_wild"}

## Vestidos das cortesãs (Clothing): cores do corpo, do painel central e dos detalhes;
## mangas "bell" (em sino), "puff" (bufante) ou "cap" (curta); "laced" = cadarços em X.
const GOWN_BLUE := {"body": [0.14, 0.22, 0.5], "panel": [0.78, 0.58, 0.14], "trim": [0.82, 0.66, 0.22], "sleeve": "cap", "laced": false}
const GOWN_CRIMSON := {"body": [0.52, 0.1, 0.16], "panel": [0.58, 0.14, 0.2], "trim": [0.8, 0.62, 0.22], "sleeve": "bell", "laced": false}
const GOWN_TEAL := {"body": [0.5, 0.1, 0.16], "panel": [0.12, 0.38, 0.42], "trim": [0.82, 0.66, 0.22], "sleeve": "cap", "laced": true}
const GOWN_ORANGE := {"body": [0.78, 0.38, 0.1], "panel": [0.55, 0.7, 0.28], "trim": [0.85, 0.75, 0.5], "sleeve": "bell", "laced": true}
const GOWN_NIGHT := {"body": [0.12, 0.1, 0.14], "panel": [0.32, 0.12, 0.38], "trim": [0.7, 0.7, 0.75], "sleeve": "bell", "laced": true}
const GOWN_LINEN := {"body": [0.62, 0.28, 0.26], "panel": [0.8, 0.76, 0.64], "trim": [0.8, 0.76, 0.64], "sleeve": "puff", "laced": false}
const COURTESAN_BONES := {"hips": "hips", "skirt": "root", "chest": "brust", "upper_l": "oberArm_L", "upper_r": "oberArm_R",
	"lower_l": "unterarm_L", "lower_r": "unterarm_R", "hand_l": "hand_L", "hand_r": "hand_R"}

const MODELS := {
	# Cortesã de Tortuga (Female NPC, umask007, CC BY 3.0): top decotado, short e botas.
	"courtesan": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT, "gown": GOWN_BLUE},
	# Segunda cortesã: o mesmo corpo nas cores da Tetine Elfe (escolha do autor):
	# top, short e botas de couro vermelho e cabelo ruivo.
	"courtesan_red": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT, "gown": GOWN_CRIMSON,
		"colors": {"bra": [0.50, 0.10, 0.09], "trouser": [0.42, 0.08, 0.07], "shoe": [0.40, 0.10, 0.08],
			"hair": [0.40, 0.15, 0.07], "hair.001": [0.40, 0.15, 0.07]}},
	# Mais cortesãs, cada uma com seu jeito: esmeralda, preto com loira, dourado e linho.
	"courtesan_green": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT, "gown": GOWN_TEAL,
		"colors": {"skin": [0.80, 0.58, 0.45], "bra": [0.12, 0.35, 0.22], "trouser": [0.10, 0.25, 0.18],
			"shoe": [0.22, 0.14, 0.09], "hair": [0.07, 0.05, 0.04], "hair.001": [0.07, 0.05, 0.04]}},
	"courtesan_black": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT, "gown": GOWN_NIGHT,
		"colors": {"skin": [0.90, 0.72, 0.60], "bra": [0.08, 0.08, 0.10], "trouser": [0.12, 0.08, 0.10],
			"shoe": [0.10, 0.08, 0.07], "hair": [0.72, 0.62, 0.40], "hair.001": [0.72, 0.62, 0.40]}},
	"courtesan_gold": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT, "gown": GOWN_ORANGE,
		"colors": {"skin": [0.55, 0.38, 0.28], "bra": [0.70, 0.52, 0.18], "trouser": [0.55, 0.30, 0.12],
			"shoe": [0.30, 0.18, 0.10], "hair": [0.12, 0.07, 0.05], "hair.001": [0.12, 0.07, 0.05]}},
	"courtesan_white": {"scene": "res://assets/models/characters/courtesan.glb", "scale": 0.186,
		"poses": COURTESAN_POSES, "dances": true, "paint": COURTESAN_PAINT, "gown": GOWN_LINEN,
		"colors": {"skin": [0.72, 0.50, 0.38], "bra": [0.80, 0.76, 0.66], "trouser": [0.70, 0.65, 0.55],
			"shoe": [0.35, 0.24, 0.15], "hair": [0.50, 0.22, 0.09], "hair.001": [0.50, 0.22, 0.09]}},
	# Capitão pirata (Clint Bellanger, CC BY 3.0): preso ao esqueleto dos heróis
	# por tools/assets/rig_to_ual.py, com as animações deles; texturas geradas.
	# Catador do Esgoto (The Amazing Spider-Man 2 suit, Ugo9p1, modelo comprado, crédito pedido pelo autor): malha em T-pose presa ao
	# esqueleto dos heróis por tools/assets/rig_to_ual.py (ver tools/assets/build_spiderman.py), com as animações deles.
	"sewer_scavenger": {"scene": "res://assets/models/characters/spiderman.glb", "scale": 1.0,
		"poses": {"idle": "Dance_Loop", "talk": "Dance_Loop", "stand": "Dance_Loop"}},  # o Catador vive dançando (a dança dos heróis), até quando conversa
	# Itachi (itachi.blend do autor, malha do Mixamo sem textura: pintura por vértice e rigging por tools/assets/build_itachi_npc.py): o Caçador de Pragas do Esgoto,
	# preso ao esqueleto dos heróis, com os movimentos deles.
	"sewer_ratcatcher": {"scene": "res://assets/models/characters/itachi.glb", "scale": 1.0, "vertex_colors": true,
		"poses": {"idle": "Idle_Loop", "talk": "Idle_Talking_Loop", "stand": "Idle_Loop", "walk": "Walk_Loop"}},
	"pirate_captain": {"scene": "res://assets/models/characters/pirate_captain.glb", "scale": 1.0,
		"poses": {"walk": "Walk_Loop", "idle": "Idle_Loop", "talk": "Idle_Talking_Loop", "drink": "Consume"}},
	# Guarda (Brigand, anthonymyers, CC BY 3.0): parado na pose do modelo, de
	# couraça, alabarda e machado (sem animação).
	# Macumbeiro de Tortuga (Rigged Textured Mage, thecubber, CC BY-SA 3.0): mago de capuz e manto
	# escuro com a trama celta nas costas, parado na pose do arquivo (sem animação).
	"voodoo_priest": {"scene": "res://assets/models/characters/voodoo_mage.glb", "scale": 1.0, "poses": {}},
	# Padre da Capital (Monk, CDmir, CC0): monge de hábito, de pé, com a animação de parado
	# ("idle"). Criado por tools/assets/build_monk.py.
	"priest": {"scene": "res://assets/models/characters/monk.glb", "scale": 1.0,
		"poses": {"idle": "idle", "talk": "idle", "stand": "idle"}},
	# Defensor animado (Animated Defender aka Brigand, Danimal sobre o Brigand de anthonymyers, CC BY 3.0): guarda da
	# Capital Real, com alabarda; anda em ronda (walk) ou fica de guarda (idle). Criado por tools/assets/build_defender.py.
	"defender": {"scene": "res://assets/models/characters/defender.glb", "scale": 1.07,
		"poses": {"walk": "walk", "run": "run", "idle": "idle", "talk": "idle", "melee": "attack", "scared": "scared"}},
	# Arqueira élfica da Floresta (Elven Archer - lower poly edition, Julius sobre a malha de theclubber, CC BY-SA 3.0): capuz e
	# capa verdes, arco e aljava nas costas, parada na pose do arquivo (sem animação); 1,85 m. Dá a missão do Leshy.
	# Criada por tools/assets/build_elf_archer.py.
	"elf_archer": {"scene": "res://assets/models/characters/elf_archer.glb", "scale": 1.0, "poses": {}},
	# Leônidas, o Veterano das Ruínas (Achilles Spartan Greek Warrior, gamekorp, CC0): guerreiro espartano de elmo, couraça e
	# capa vermelha, 1,9 m com a crista; a malha vinha em T-pose e sem esqueleto, então os braços foram baixados
	# (tools/assets/build_achilles.py) e ele fica parado nessa pose. Dá a missão dos goblins.
	"ruins_spartan": {"scene": "res://assets/models/characters/ruins_spartan.glb", "scale": 1.0, "poses": {}},
	# Guardiã da Pira (Saxon warrior, Blend Swap #83828, CC0): guerreiro saxão de capa, escudo e lança, parado na pose do arquivo (sem animação); 1,85 m
	# (a lança passa disso). Criado por tools/assets/build_saxon_warrior.py. Dá a missão do Golem de Fogo.
	"forest_pyre_keeper": {"scene": "res://assets/models/characters/saxon_warrior.glb", "scale": 1.0, "poses": {}},
	"guard": {"scene": "res://assets/models/characters/brigand_guard.glb", "scale": 1.0, "poses": {}},
	# Sentinela do castelo da Capital: o mesmo Brigand (anthonymyers, CC BY 3.0; a versão rigada "Brigand2" é o mesmo personagem), parado de guarda.
	# Bobo da Corte (Cerimonial Guard, carlosjorgereis, CC0): figura cerimonial de gorro e saia de pele, sem esqueleto nem animação
	# (parado na pose do arquivo); 1,7 m no arquivo -> ~1,8 m. É o Bobo da Corte da Sala do Rei.
	"court_jester": {"scene": "res://assets/models/characters/court_jester/cerimonial_guard.dae", "scale": 1.05, "poses": {}},
	# Pirata sentado (Seated pirate with poor rig, pre, CC BY 3.0): malha parada na pose de sentado (sem animação); NPC da missão das Docas, na taverna.
	"seated_pirate": {"scene": "res://assets/models/characters/pirate_captain_npc.glb", "scale": 1.0, "poses": {}},  # Capitão Pirata da Taverna (pirate.glb do usuário, malha parada)
	"castle_guard": {"scene": "res://assets/models/characters/brigand_guard.glb", "scale": 1.0, "poses": {}},
	# Aranhinha do esgoto (Spider animated, pantherone, CC BY 3.0): não ataca,
	# só anda pelo chão. Arquivo de 1 m -> 32 cm, preta (decisão do autor, depois diminuída um pouco).
	"spider": {"scene": "res://assets/models/monsters/spider.glb", "scale": 0.32,
		"poses": {"walk": "walk", "idle": "idle", "talk": "idle"},
		"colors": {"Spider": [0.03, 0.03, 0.035]}},
	# Morcego do esgoto (o mesmo modelo dos monstros; só enfeite, voa em círculos: game/levels/flyer.gd). O arquivo tem ~10 unidades de envergadura.
	"bat": {"scene": "res://assets/models/monsters/bat.glb", "scale": 0.14,
		"poses": {"walk": "fly", "idle": "fly", "talk": "fly"}},
	# Ratinho do esgoto (o mesmo modelo dos monstros antigos): não ataca, só cenário como as aranhas.
	"rat": {"scene": "res://assets/models/monsters/rat.glb", "scale": 0.5,
		"poses": {"walk": "walk", "idle": "idle", "talk": "idle"}},
	# Atendente da Taverna (Bartender, cdmir, CC0): o mesmo modelo da visitante sentada, em pé
	# atrás do balcão (a animação "stand" é criada por código: o arquivo só tem a sentada).
	"bartender": {"scene": "res://assets/models/characters/visitor_woman.glb", "scale": 0.116, "bartender": true,
		"poses": {"stand": "stand", "idle": "stand", "talk": "stand", "walk": "stand"}},
	# Velha (Old Lady, cdmir, CC0): sentada à mesa da Taverna. Só tem a animação de sentada
	# (um trecho de 10 s, tocado de ida e volta para não dar salto). Altura ~135 unidades -> 1,5 m.
	"old_lady": {"scene": "res://assets/models/characters/old_lady.glb", "scale": 0.011, "pingpong": true,
		"poses": {"sit": "sit", "idle": "sit", "talk": "sit", "walk": "sit"}},
	# Coelho (Rabbit, cdmir, CC0): pula pelas ruas de Tortuga (o pulo de 1 s fica no lugar:
	# o Wanderer anda enquanto ele pula) e senta alerta nas pontas. Arquivo de ~15 unidades -> 60 cm.
	"rabbit": {"scene": "res://assets/models/characters/rabbit.glb", "scale": 0.04,
		"poses": {"walk": "jump", "run": "run", "idle": "idle", "talk": "sit"}},
	# Galinha (cdmir, CC0): anda e cisca pelas cozinhas de Tortuga (12,6 unidades -> 0,4 m).
	# Gato (Simple Cat, drummyfish, CC0): passeia pelas ruas de Tortuga; parado, fica no 1º quadro da caminhada.
	"cat": {"scene": "res://assets/models/characters/cat.glb", "scale": 0.2,
		"poses": {"walk": "walk"}},
	# Cavalo de tração (Rigged Horse, Lyndon Daniels / ChadM, CC0): passeia pelas ruas de Tortuga; o ciclo de
	# passo foi criado por tools/assets/build_horse.py (o arquivo original não tem animação).
	"horse": {"scene": "res://assets/models/characters/horse.glb", "scale": 1.0,
		"poses": {"walk": "walk", "idle": "walk", "talk": "walk"}},
	"chicken": {"scene": "res://assets/models/characters/chicken.glb", "scale": 0.032,
		"poses": {"walk": "walk", "idle": "eat", "talk": "idle"}},
	# Ovelha da Fazenda (Sheep rigged, textured and animated, p0ss, CC-BY-SA 3.0; tools/assets/build_sheep.sh):
	# 1,2 m de comprimento no arquivo; anda devagar pelos campos e pasta parada.
	"sheep": {"scene": "res://assets/models/characters/sheep.glb", "scale": 1.0,
		"poses": {"walk": "walk", "idle": "eat", "talk": "idle"}},
	# Galo da Fazenda (Rooster (animated), CDmir e TinyWorlds, CC0; tools/assets/build_rooster.sh): 0,5 m de comprimento; anda e bica o chão.
	"rooster": {"scene": "res://assets/models/characters/rooster.glb", "scale": 1.0,
		"poses": {"walk": "walk", "idle": "eat", "talk": "idle"}},
	# Porco (Domestic Pig Male, do autor, pork.zip; tools/assets/build_pig.py): 1,3 m de comprimento, com esqueleto, andar e parado montados pelo script.
	# O cavalo da Fazenda continua o do pacote Farm Animals (Quaternius, CC0; tools/assets/build_farm_animals.sh).
	"pig": {"scene": "res://assets/models/characters/pig.glb", "scale": 1.0,
		"poses": {"walk": "walk", "idle": "idle", "talk": "idle"}},
	# Animais de cenário fornecidos pelo autor (modelos estáticos reduzidos por tools/assets/reduce_scan_model.py; autoria e licença a confirmar):
	# lhama e cavalo marrom da Fazenda, caranguejo das Docas (low-poly, ~0,2 m: dobrado) e guaxinim da Floresta.
	"llama": {"scene": "res://assets/models/characters/llama_farm.glb", "scale": 1.0, "poses": {}},
	"brown_horse": {"scene": "res://assets/models/characters/horse_brown.glb", "scale": 1.0, "poses": {}},
	"crab": {"scene": "res://assets/models/characters/crab.glb", "scale": 2.0, "poses": {}},
	"squirrel": {"scene": "res://assets/models/characters/squirrel_forest.glb", "scale": 1.0, "poses": {}},
	"raccoon": {"scene": "res://assets/models/characters/raccoon_forest.glb", "scale": 1.0, "poses": {}},
	# Benny, o Rottweiler (CC BY-SA 3.0): anda pela Taverna ("walk" é a corrida do arquivo).
	"rottweiler": {"scene": "res://assets/models/props/Rottweiler.glb", "scale": 1.0,
		"poses": {"walk": "walk", "idle": "idle", "talk": "idle"}},
	"farm_horse": {"scene": "res://assets/models/characters/farm_horse.glb", "scale": 1.0,
		"poses": {"walk": "walk", "idle": "idle", "talk": "idle"}},
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
	if info.get("vertex_colors", false):  # modelo pintado por cor de vértice (o Itachi): o Godot não liga o albedo sozinho
		for node in model.find_children("*", "MeshInstance3D", true, false):
			var painted := node as MeshInstance3D
			for i in painted.get_surface_override_material_count():
				var base := painted.get_active_material(i) as BaseMaterial3D
				if base:
					var copy := base.duplicate() as BaseMaterial3D
					copy.vertex_color_use_as_albedo = true
					painted.set_surface_override_material(i, copy)
	var colors: Dictionary = info.get("colors", {})
	if info.has("gown"):
		# O top e o short velhos (o que sobra à vista) combinam com o vestido.
		colors = colors.duplicate()
		colors["bra"] = info.gown.get("top", info.gown.body)
		colors["trouser"] = info.gown.body
	if info.has("paint"):
		_paint(model, info.paint, colors)
	if info.has("gown"):
		Clothing.dress(model, COURTESAN_BONES, clothing_style(info.gown))
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
	if npc._anim and info.get("bartender", false):
		npc._make_bartender(model)
	if npc._anim:
		# O importador do Godot tira o "_Loop" do nome (e marca a repetição).
		for key: String in npc._poses.keys():
			var anim_name: String = npc._poses[key]
			for candidate in [anim_name, anim_name.trim_suffix("_Loop")]:
				if npc._anim.has_animation(candidate):
					npc._poses[key] = candidate
					npc._anim.get_animation(candidate).loop_mode = Animation.LOOP_PINGPONG if info.get("pingpong", false) else Animation.LOOP_LINEAR
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
		var retargeted := DanceRetarget.build(skeleton, walk, DANCE_UAL.get(dance_name, {}))
		if retargeted:
			_anim.get_animation_library("").add_animation(dance_name, retargeted)
			continue
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


## Estilo de roupa com as cores como Color (os dados guardam [r, g, b]).
static func clothing_style(style: Dictionary) -> Dictionary:
	var out := style.duplicate()
	for key: String in ["body", "panel", "trim", "lace", "top", "belt"]:
		if style.has(key):
			var c: Array = style[key]
			out[key] = Color(c[0], c[1], c[2])
	return out


## "stand": o corpo em pé (o arquivo está em pose de T), braços baixos e os antebraços à
## frente (conversando com quem chega ao balcão), respirando e balançando de leve.
## As rotações são globais por osso (o repouso é a pose de T): braço desce, antebraço dobra.
func _make_bartender(model: Node) -> void:
	var skeleton := model.find_child("Skeleton3D", true, false) as Skeleton3D
	if skeleton == null or _anim.has_animation("stand"):
		return
	var prefix := String(_anim.get_animation("sit").track_get_path(0)).get_slice(":", 0)
	var length := 3.6
	var animation := Animation.new()
	animation.length = length
	animation.loop_mode = Animation.LOOP_LINEAR
	var count := skeleton.get_bone_count()
	var rest_local: Array[Quaternion] = []
	var rest_global: Array[Quaternion] = []
	for i in count:
		var local := skeleton.get_bone_rest(i).basis.get_rotation_quaternion()
		rest_local.append(local)
		var parent := skeleton.get_bone_parent(i)
		rest_global.append((rest_global[parent] if parent >= 0 else Quaternion.IDENTITY) * local)
	# Só os ossos deste conjunto mudam; o resto fica no repouso.
	var moving := {}
	for side in ["L", "R"]:
		for bone: String in ["Arm_", "ForeArm_", "Hand_"]:
			moving[skeleton.find_bone(bone + side)] = side
	var spine := skeleton.find_bone("Spine")
	var head := skeleton.find_bone("Head")
	var tracks := {}
	for i in [spine, head] + moving.keys():
		var track := animation.add_track(Animation.TYPE_ROTATION_3D)
		animation.track_set_path(track, NodePath("%s:%s" % [prefix, skeleton.get_bone_name(i)]))
		tracks[i] = track
	var steps := 36
	for k in steps + 1:
		var t := length * k / steps
		var phase := TAU * k / steps
		var global_now: Array[Quaternion] = []
		for i in count:
			var parent := skeleton.get_bone_parent(i)
			var parent_new: Quaternion = global_now[parent] if parent >= 0 else Quaternion.IDENTITY
			var parent_rest: Quaternion = rest_global[parent] if parent >= 0 else Quaternion.IDENTITY
			var q := parent_new * parent_rest.inverse() * rest_global[i]  # sem mexer: segue o pai
			if i == spine:
				q = q * Quaternion(Vector3.RIGHT, 0.02 * sin(phase))
			elif i == head:
				q = q * Quaternion(Vector3.UP, 0.12 * sin(phase * 0.5)) * Quaternion(Vector3.RIGHT, 0.03 * sin(phase))
			elif moving.has(i):
				var side: String = moving[i]
				var outward := 1.0 if skeleton.get_bone_global_rest(i).origin.x >= 0.0 else -1.0
				var name := skeleton.get_bone_name(i)
				if name.begins_with("Arm_"):
					# Braço: da pose de T para baixo, um pouco à frente.
					q = Quaternion(Vector3.BACK, -outward * deg_to_rad(72.0)) * q
					q = Quaternion(Vector3.RIGHT, deg_to_rad(-22.0)) * q
				elif name.begins_with("ForeArm_"):
					# Antebraço dobrado para a frente (a direita faz o gesto de polir).
					var direction := q * Vector3(0, 1, 0)
					var along := skeleton.get_bone_global_rest(skeleton.find_bone("Hand_" + side)).origin - skeleton.get_bone_global_rest(i).origin
					var axis := (along.normalized()).cross(Vector3.BACK).normalized()
					var wipe := 0.0
					if side == "R":
						wipe = deg_to_rad(10.0) * sin(phase * 2.0)
					q = Quaternion(Vector3.RIGHT, deg_to_rad(-52.0) + wipe) * q
					direction = direction
					axis = axis
			global_now.append(q)
			if tracks.has(i):
				var local_q := (global_now[parent].inverse() if parent >= 0 else Quaternion.IDENTITY) * q
				animation.rotation_track_insert_key(tracks[i], t, local_q.normalized())
	_anim.get_animation_library("").add_animation("stand", animation)


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
		# Parada: a pose de andar congelada no primeiro quadro (modelo estático: não há o que tocar).
		if not _anim.has_animation(_poses.get("walk", "")):
			return
		_anim.play(_poses.get("walk", ""), 0.15)
		_anim.seek(0.0, true)
		_anim.pause()
