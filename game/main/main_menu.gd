# Southern Mercenaries — GPL-3.0-or-later
extends Control
## Menu principal. Na primeira execução mostra a escolha de idioma
## (já pré-selecionado pelo idioma do sistema).

const ARENA_SCENE := "res://game/levels/prototype_arena.tscn"

var _main: MenuPanel
var _language: MenuPanel
var _options: OptionsMenu
var _options_button: Button


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
	_main.add_button("MENU_PLAY_SOLO", func() -> void: get_tree().change_scene_to_file(ARENA_SCENE))
	_options_button = _main.add_button("MENU_OPTIONS", _open_options)
	_main.add_button("MENU_QUIT", func() -> void: get_tree().quit())
	var version := Label.new()
	version.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	version.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	version.modulate = Color(1, 1, 1, 0.4)
	_main.content.add_child(version)
	_set_version_text(version)
	Settings.changed.connect(_set_version_text.bind(version))
	# O menu principal não fecha com "voltar".
	_main.set_process_unhandled_input(false)

	_options = OptionsMenu.new()
	add_child(_options)
	_options.closed.connect(func() -> void: _main.open(_options_button))

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


func _choose_language(code: String) -> void:
	Settings.set_language(code)
	_language.visible = false
	_main.open()


func _open_options() -> void:
	_main.visible = false
	_options.open()


func _set_version_text(label: Label) -> void:
	label.text = tr("MENU_VERSION").format({"version": ProjectSettings.get_setting("application/config/version")})
