# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Preferências do jogador, salvas em user://settings.cfg.
## Idioma: na primeira execução usa o idioma do sistema (se for um dos 3)
## e o menu principal mostra a tela de escolha (01-escopo.md, seção 6).

signal changed

const PATH := "user://settings.cfg"
const LANGUAGES: Array[String] = ["en", "es", "pt_BR"]

var language := "en"
## false até o jogador confirmar o idioma na primeira execução.
var language_chosen := false
var vibration := true
var aim_assist := true
var invert_aim_y := false
var deadzone := 0.2
## Dicas do tutorial (14-tutorial.md: Opções → Jogabilidade → Dicas).
var tips := true
## Pegadas no chão até o objetivo da missão ativa (Opções → Jogabilidade → Pegadas da missão).
var quest_trail := true
## Último personagem escolhido no menu (ID do save).
var last_character := ""
## Qualidade gráfica (Opções → Gráficos): 0 baixa (PC fraco, sem placa de vídeo), 1 média, 2 alta.
## Baixa e média desenham o 3D em resolução menor, tiram sombras, luzes de cenário e a água com shader, e escondem o cenário distante.
var quality := 2
const RENDER_SCALE: Array[float] = [0.55, 0.78, 1.0]
## Distância (m) da câmera a partir da qual o cenário some, por qualidade (a câmera vê uns 30 m); 0 = sem limite.
const VIEW_RANGE: Array[float] = [48.0, 70.0, 95.0]


func _ready() -> void:
	_load()
	apply_graphics()
	TranslationServer.set_locale(language)
	# Tema medieval de toda a interface (09-interface.md, seção 7).
	UiTheme.apply()


func set_language(code: String) -> void:
	if code not in LANGUAGES:
		return
	language = code
	language_chosen = true
	TranslationServer.set_locale(code)
	save()


func set_value(key: String, value: Variant) -> void:
	set(key, value)
	if key == "quality":
		apply_graphics()
	save()


## Qualidade sugerida na primeira execução: baixa se o "vídeo" for por software (llvmpipe, SwiftShader).
static func default_quality() -> int:
	var adapter := RenderingServer.get_video_adapter_name().to_lower()
	for slow in ["llvmpipe", "softpipe", "swiftshader", "software", "microsoft basic"]:
		if adapter.contains(slow):
			return 0
	return 2


## Resolução do 3D (a interface continua nítida) e filtros; sombras, luzes e alcance do cenário valem ao montar a área.
func apply_graphics() -> void:
	var root := get_tree().root
	root.scaling_3d_mode = Viewport.SCALING_3D_MODE_BILINEAR
	root.scaling_3d_scale = RENDER_SCALE[clampi(quality, 0, 2)]
	root.msaa_3d = Viewport.MSAA_DISABLED


func save() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("general", "language", language)
	cfg.set_value("general", "language_chosen", language_chosen)
	cfg.set_value("controls", "vibration", vibration)
	cfg.set_value("controls", "aim_assist", aim_assist)
	cfg.set_value("controls", "invert_aim_y", invert_aim_y)
	cfg.set_value("controls", "deadzone", deadzone)
	cfg.set_value("gameplay", "tips", tips)
	cfg.set_value("gameplay", "quest_trail", quest_trail)
	cfg.set_value("general", "last_character", last_character)
	cfg.set_value("graphics", "quality", quality)
	cfg.save(PATH)
	changed.emit()


func _load() -> void:
	var cfg := ConfigFile.new()
	quality = default_quality()
	if cfg.load(PATH) != OK:
		language = system_language()
		return
	quality = clampi(int(cfg.get_value("graphics", "quality", quality)), 0, 2)
	language = cfg.get_value("general", "language", system_language())
	if language not in LANGUAGES:
		language = "en"
	language_chosen = cfg.get_value("general", "language_chosen", false)
	vibration = cfg.get_value("controls", "vibration", true)
	aim_assist = cfg.get_value("controls", "aim_assist", true)
	invert_aim_y = cfg.get_value("controls", "invert_aim_y", false)
	deadzone = clampf(cfg.get_value("controls", "deadzone", 0.2), 0.05, 0.6)
	last_character = cfg.get_value("general", "last_character", "")
	tips = cfg.get_value("gameplay", "tips", true)
	quest_trail = cfg.get_value("gameplay", "quest_trail", true)


static func system_language() -> String:
	match OS.get_locale_language():
		"pt":
			return "pt_BR"
		"es":
			return "es"
		_:
			return "en"
