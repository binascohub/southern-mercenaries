# Southern Mercenaries — GPL-3.0-or-later
class_name PauseMenu
extends CanvasLayer
## Menu do jogo. No solo pausa; no co-op o jogo continua (01-escopo.md).
## No mapa não há save livre: "Salvar e sair" grava o personagem (e, no host,
## a campanha com o último checkpoint) e volta ao menu (11-saves.md, seção 4).

const MAIN_SCENE := "res://game/main/main.tscn"

var is_open := false
var _paused := false
var _panel: MenuPanel
var _options: OptionsMenu
var _options_button: Button


func _ready() -> void:
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS
	_panel = MenuPanel.new()
	add_child(_panel)
	_panel.add_title("MENU_PAUSED")
	_panel.add_button("MENU_RESUME", resume)
	_options_button = _panel.add_button("MENU_OPTIONS", _open_options)
	_panel.add_button("MENU_SAVE_AND_QUIT", func() -> void:
		get_tree().paused = false
		_save()
		NetworkManager.leave()
		get_tree().change_scene_to_file(MAIN_SCENE))
	_panel.add_button("MENU_QUIT", func() -> void:
		_save()
		NetworkManager.leave()
		get_tree().quit())
	_panel.closed.connect(resume)

	_options = OptionsMenu.new()
	add_child(_options)
	_options.closed.connect(func() -> void: _panel.open(_options_button))


func _unhandled_input(event: InputEvent) -> void:
	if is_open and _panel.visible and event.is_action_pressed(&"menu"):
		get_viewport().set_input_as_handled()
		resume()


func open(pause_game: bool) -> void:
	is_open = true
	_paused = pause_game
	if pause_game:
		get_tree().paused = true
	_panel.open()


func resume() -> void:
	if not is_open:
		return
	is_open = false
	_panel.visible = false
	_options.visible = false
	if _paused:
		get_tree().paused = false


func _save() -> void:
	get_tree().call_group(&"arena", &"save_now")
	SaveSystem.flush()


func _open_options() -> void:
	_panel.visible = false
	_options.open()
