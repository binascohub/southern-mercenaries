# Southern Mercenaries — GPL-3.0-or-later
class_name PauseMenu
extends CanvasLayer
## Menu de pausa do modo solo.

const MAIN_SCENE := "res://game/main/main.tscn"

var is_open := false
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
	_panel.add_button("MENU_MAIN_MENU", func() -> void:
		get_tree().paused = false
		get_tree().change_scene_to_file(MAIN_SCENE))
	_panel.add_button("MENU_QUIT", func() -> void: get_tree().quit())
	_panel.closed.connect(resume)

	_options = OptionsMenu.new()
	add_child(_options)
	_options.closed.connect(func() -> void: _panel.open(_options_button))


func _unhandled_input(event: InputEvent) -> void:
	if is_open and _panel.visible and event.is_action_pressed(&"menu"):
		get_viewport().set_input_as_handled()
		resume()


func open() -> void:
	is_open = true
	get_tree().paused = true
	_panel.open()


func resume() -> void:
	if not is_open:
		return
	is_open = false
	_panel.visible = false
	_options.visible = false
	get_tree().paused = false


func _open_options() -> void:
	_panel.visible = false
	_options.open()
