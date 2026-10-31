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
## Último personagem escolhido no menu (ID do save).
var last_character := ""


func _ready() -> void:
	_load()
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
	save()


func save() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("general", "language", language)
	cfg.set_value("general", "language_chosen", language_chosen)
	cfg.set_value("controls", "vibration", vibration)
	cfg.set_value("controls", "aim_assist", aim_assist)
	cfg.set_value("controls", "invert_aim_y", invert_aim_y)
	cfg.set_value("controls", "deadzone", deadzone)
	cfg.set_value("gameplay", "tips", tips)
	cfg.set_value("general", "last_character", last_character)
	cfg.save(PATH)
	changed.emit()


func _load() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(PATH) != OK:
		language = system_language()
		return
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


static func system_language() -> String:
	match OS.get_locale_language():
		"pt":
			return "pt_BR"
		"es":
			return "es"
		_:
			return "en"
