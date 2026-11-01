# Southern Mercenaries — GPL-3.0-or-later
class_name ControlsMenu
extends MenuPanel
## Remapeamento (08-controles.md, seção 4): lista de ações com o botão atual
## de teclado e de controle; escolher um e apertar o novo botão para trocar.
## Botão já em uso: as duas ações trocam. Inclui teste do controle.

const WAIT_TIMEOUT := 6.0

var _grid: GridContainer
var _status: Label
var _test: Label
var _buttons := {}  # "action|kind" -> Button
var _waiting_action: StringName = &""
var _waiting_kind := ""
var _wait_left := 0.0


func _ready() -> void:
	add_title("CONTROLS_TITLE")

	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(720, 420)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	content.add_child(scroll)
	_grid = GridContainer.new()
	_grid.columns = 3
	_grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_grid)

	for key in ["CONTROLS_ACTION", "CONTROLS_KEYBOARD", "CONTROLS_GAMEPAD"]:
		var header := Label.new()
		header.text = key
		header.add_theme_color_override("font_color", Color(0.45, 0.09, 0.07))
		_grid.add_child(header)
	for action in Controls.REMAPPABLE:
		var label := Label.new()
		label.text = "ACTION_" + String(action).to_upper()
		label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		_grid.add_child(label)
		for kind in [Controls.KB, Controls.PAD]:
			var button := Button.new()
			button.custom_minimum_size = Vector2(200, 36)
			button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
			button.pressed.connect(_start_wait.bind(action, kind))
			_grid.add_child(button)
			_buttons["%s|%s" % [action, kind]] = button

	_status = Label.new()
	_status.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_status.custom_minimum_size = Vector2(720, 0)
	content.add_child(_status)
	_test = Label.new()
	_test.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	content.add_child(_test)

	add_button("CONTROLS_RESTORE", func() -> void:
		Controls.restore_defaults()
		_status.text = ""
		_refresh())
	add_button("MENU_BACK", close)
	Controls.bindings_changed.connect(_refresh)


func _on_open() -> void:
	_status.text = ""
	_test.text = tr("CONTROLS_TEST_IDLE")
	_refresh()


func _refresh() -> void:
	for action in Controls.REMAPPABLE:
		for kind in [Controls.KB, Controls.PAD]:
			_buttons["%s|%s" % [action, kind]].text = Controls.binding_label(action, kind)


func _process(delta: float) -> void:
	if _waiting_action == &"":
		return
	_wait_left -= delta
	if _wait_left <= 0.0:
		_stop_wait()


func _start_wait(action: StringName, kind: String) -> void:
	_waiting_action = action
	_waiting_kind = kind
	_wait_left = WAIT_TIMEOUT
	_status.text = tr("CONTROLS_WAITING_KEY") if kind == Controls.KB else tr("CONTROLS_WAITING_PAD")
	_buttons["%s|%s" % [action, kind]].text = "…"


func _stop_wait() -> void:
	_waiting_action = &""
	_status.text = ""
	_refresh()


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventJoypadButton and event.pressed \
			or event is InputEventJoypadMotion and absf(event.axis_value) > 0.6:
		_test.text = tr("CONTROLS_TEST").format({"input": Controls.event_label(_normalized(event))})
	if _waiting_action == &"":
		return
	var captured := _capture(event)
	if captured == null:
		return
	get_viewport().set_input_as_handled()
	if captured is InputEventKey and captured.physical_keycode == KEY_ESCAPE:
		_stop_wait()
		return
	var action := _waiting_action
	var swapped := Controls.rebind(action, _waiting_kind, captured)
	_stop_wait()
	if swapped != &"":
		_status.text = tr("CONTROLS_SWAPPED").format({"action": tr("ACTION_" + String(swapped).to_upper())})


## Só aceita eventos da mesma classe da coluna escolhida.
func _capture(event: InputEvent) -> InputEvent:
	if _waiting_kind == Controls.KB:
		if event is InputEventKey and event.pressed and not event.echo:
			return Controls.key(event.physical_keycode)
		if event is InputEventMouseButton and event.pressed:
			return Controls.mouse(event.button_index)
	else:
		if event is InputEventKey and event.pressed and event.physical_keycode == KEY_ESCAPE:
			return Controls.key(KEY_ESCAPE)
		if event is InputEventJoypadButton and event.pressed:
			return _normalized(event)
		if event is InputEventJoypadMotion and absf(event.axis_value) > 0.6:
			return _normalized(event)
	return null


static func _normalized(event: InputEvent) -> InputEvent:
	if event is InputEventJoypadButton:
		return Controls.pad(event.button_index)
	if event is InputEventJoypadMotion:
		return Controls.axis(event.axis, event.axis_value)
	return event
