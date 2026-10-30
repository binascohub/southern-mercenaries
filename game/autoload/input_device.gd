# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Acompanha o último dispositivo usado (para trocar os ícones da interface),
## a conexão/desconexão de controles e a vibração (08-controles.md).

signal device_changed(using_gamepad: bool)
signal gamepad_lost
signal gamepad_restored

const AXIS_THRESHOLD := 0.5
const MOUSE_MOTION_THRESHOLD := 4.0

var using_gamepad := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Input.joy_connection_changed.connect(_on_joy_connection_changed)
	using_gamepad = not Input.get_connected_joypads().is_empty()


func _input(event: InputEvent) -> void:
	var is_pad: bool = event is InputEventJoypadButton \
		or (event is InputEventJoypadMotion and absf(event.axis_value) > AXIS_THRESHOLD)
	var is_kbm: bool = event is InputEventKey or event is InputEventMouseButton \
		or (event is InputEventMouseMotion and event.relative.length() > MOUSE_MOTION_THRESHOLD)
	if is_pad and not using_gamepad:
		using_gamepad = true
		device_changed.emit(true)
	elif is_kbm and using_gamepad:
		using_gamepad = false
		device_changed.emit(false)


func current_kind() -> String:
	return Controls.PAD if using_gamepad else Controls.KB


## Texto do botão de uma ação no dispositivo em uso.
func prompt(action: StringName) -> String:
	return Controls.binding_label(action, current_kind())


func vibrate(weak: float, strong: float, duration: float) -> void:
	if not Settings.vibration or not using_gamepad:
		return
	for device in Input.get_connected_joypads():
		Input.start_joy_vibration(device, weak, strong, duration)


func _on_joy_connection_changed(_device: int, connected: bool) -> void:
	if connected:
		gamepad_restored.emit()
	elif using_gamepad and Input.get_connected_joypads().is_empty():
		gamepad_lost.emit()
