# Southern Mercenaries — GPL-3.0-or-later
extends Control
## Menu principal. Na primeira execução mostra a escolha de idioma
## (já pré-selecionado pelo idioma do sistema). Personagem escolhido, campanha
## (Continuar / Nova campanha, 11-saves.md), hospedar ou entrar numa partida
## na LAN (busca automática + IP manual).

const ARENA_SCENE := "res://game/levels/prototype_arena.tscn"

var _main: MenuPanel
var _language: MenuPanel
var _join: JoinMenu
var _characters: CharacterMenu
var _hero: Label
var _continue_button: Button
var _characters_button: Button
var _pending_start: Callable
var _options: OptionsMenu
var _options_button: Button
var _join_button: Button
var _message: Label


func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = Color(0.04, 0.04, 0.06)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)

	_main = MenuPanel.new()
	add_child(_main)
	var title := _main.add_title("GAME_TITLE")
	title.add_theme_font_size_override("font_size", 44)
	var note := Label.new()
	note.text = "MENU_PROTOTYPE_NOTE"
	note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	note.modulate = Color(1, 1, 1, 0.6)
	_main.content.add_child(note)
	_message = Label.new()
	_message.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_message.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_message.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_message.custom_minimum_size = Vector2(320, 0)
	_message.add_theme_color_override("font_color", Color(1.0, 0.6, 0.45))
	_main.content.add_child(_message)
	_hero = Label.new()
	_hero.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_hero.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hero.add_theme_color_override("font_color", Color(0.9, 0.8, 0.5))
	_main.content.add_child(_hero)
	_continue_button = _main.add_button("MENU_CONTINUE", func() -> void:
		_start(NetworkManager.prepare_solo, Session.continue_or_new_campaign))
	_main.add_button("MENU_NEW_CAMPAIGN", func() -> void:
		_start(NetworkManager.prepare_solo, Session.start_new_campaign))
	_main.add_button("MENU_HOST_LAN", func() -> void:
		_start(NetworkManager.prepare_host, Session.continue_or_new_campaign))
	_join_button = _main.add_button("MENU_JOIN_LAN", _open_join)
	_characters_button = _main.add_button("MENU_CHARACTERS", _open_characters)
	_options_button = _main.add_button("MENU_OPTIONS", _open_options)
	_main.add_button("MENU_QUIT", func() -> void: get_tree().quit())
	var version := Label.new()
	version.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	version.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	version.modulate = Color(1, 1, 1, 0.4)
	_main.content.add_child(version)
	_refresh_texts.bind(version).call()
	Settings.changed.connect(_refresh_texts.bind(version))
	# O menu principal não fecha com "voltar".
	_main.set_process_unhandled_input(false)

	_options = OptionsMenu.new()
	add_child(_options)
	_options.closed.connect(func() -> void: _main.open(_options_button))

	_join = JoinMenu.new()
	add_child(_join)
	_join.closed.connect(func() -> void: _main.open(_join_button))
	_join.join_requested.connect(func(address: String) -> void:
		_start(NetworkManager.prepare_join.bind(address), func() -> void: Session.campaign = {}))

	_characters = CharacterMenu.new()
	add_child(_characters)
	_characters.closed.connect(func() -> void:
		_refresh_hero()
		_main.open(_characters_button))
	_characters.chosen.connect(func() -> void:
		if _pending_start.is_valid():
			var start := _pending_start
			_pending_start = Callable()
			start.call())

	_language = MenuPanel.new()
	add_child(_language)
	_language.add_title("LANGUAGE_CHOOSE_TITLE")
	var system_button: Button
	for code in Settings.LANGUAGES:
		var button := _language.add_button(OptionsMenu.LANGUAGE_KEYS[code], _choose_language.bind(code))
		if code == Settings.language:
			system_button = button
	_language.set_process_unhandled_input(false)

	if Settings.language_chosen:
		_main.open()
	else:
		_language.open()
		system_button.grab_focus.call_deferred()


## Sem personagem, abre a criação antes de começar.
func _start(prepare: Callable, campaign: Callable) -> void:
	if Session.character == null:
		_pending_start = _start.bind(prepare, campaign)
		_open_characters()
		return
	prepare.call()
	campaign.call()
	NetworkManager.last_error_key = ""
	get_tree().change_scene_to_file(ARENA_SCENE)


func _open_characters() -> void:
	_main.visible = false
	_characters.open(_characters_button)


func _refresh_hero() -> void:
	var c := Session.character
	_hero.text = tr("CHAR_ENTRY").format({"name": c.data.name,
		"class": tr(c.class_data().name_key), "level": c.data.level}) if c else tr("CHAR_NONE")
	_continue_button.visible = not SaveSystem.list_campaigns().is_empty()


func _choose_language(code: String) -> void:
	Settings.set_language(code)
	_language.visible = false
	_main.open()


func _open_options() -> void:
	_main.visible = false
	_options.open()


func _open_join() -> void:
	_main.visible = false
	_join.open(_join_button)


func _refresh_texts(version: Label) -> void:
	_refresh_hero()
	version.text = tr("MENU_VERSION").format({"version": NetworkManager.version()})
	# Motivo de ter voltado ao menu (host saiu, versão diferente…).
	_message.text = tr(NetworkManager.last_error_key).format(NetworkManager.last_error_args) if NetworkManager.last_error_key != "" else ""
	_message.visible = _message.text != ""

