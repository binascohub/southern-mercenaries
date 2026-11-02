# Southern Mercenaries — GPL-3.0-or-later
class_name OptionsMenu
extends MenuPanel
## Opções: idioma (troca na hora, sem reiniciar), vibração, mira assistida,
## inverter eixo Y, dicas do tutorial, pegadas até o objetivo da missão, zona morta e remapeamento de controles.

const LANGUAGE_KEYS := {"en": "LANGUAGE_NAME_EN", "es": "LANGUAGE_NAME_ES", "pt_BR": "LANGUAGE_NAME_PT_BR"}

var _language: OptionButton
var _vibration: CheckButton
var _aim_assist: CheckButton
var _invert_y: CheckButton
var _tips: CheckButton
var _quest_trail: CheckButton
var _deadzone: HSlider
var _controls_button: Button
var _controls_menu: ControlsMenu


func _ready() -> void:
	add_title("OPTIONS_TITLE")

	_language = OptionButton.new()
	for code in Settings.LANGUAGES:
		_language.add_item(LANGUAGE_KEYS[code])
	_language.item_selected.connect(func(i: int) -> void: Settings.set_language(Settings.LANGUAGES[i]))
	_row("OPTIONS_LANGUAGE", _language)

	_vibration = _toggle("OPTIONS_VIBRATION", "vibration")
	_aim_assist = _toggle("OPTIONS_AIM_ASSIST", "aim_assist")
	_invert_y = _toggle("OPTIONS_INVERT_AIM_Y", "invert_aim_y")
	_tips = _toggle("OPTIONS_TIPS", "tips")
	_quest_trail = _toggle("OPTIONS_QUEST_TRAIL", "quest_trail")

	_deadzone = HSlider.new()
	_deadzone.min_value = 0.05
	_deadzone.max_value = 0.6
	_deadzone.step = 0.05
	_deadzone.custom_minimum_size = Vector2(200, 0)
	_deadzone.value_changed.connect(func(v: float) -> void:
		Settings.set_value("deadzone", v)
		Controls.apply_deadzone(v))
	_row("OPTIONS_DEADZONE", _deadzone)

	_controls_button = add_button("OPTIONS_CONTROLS", _open_controls)
	add_button("MENU_BACK", close)

	_controls_menu = ControlsMenu.new()
	add_sibling.call_deferred(_controls_menu)
	_controls_menu.closed.connect(func() -> void: visible = true)


func _on_open() -> void:
	_language.select(Settings.LANGUAGES.find(Settings.language))
	_vibration.set_pressed_no_signal(Settings.vibration)
	_aim_assist.set_pressed_no_signal(Settings.aim_assist)
	_invert_y.set_pressed_no_signal(Settings.invert_aim_y)
	_tips.set_pressed_no_signal(Settings.tips)
	_quest_trail.set_pressed_no_signal(Settings.quest_trail)
	_deadzone.set_value_no_signal(Settings.deadzone)


func _open_controls() -> void:
	visible = false
	_controls_menu.open(_controls_button)


func _toggle(key: String, setting: String) -> CheckButton:
	var toggle := CheckButton.new()
	toggle.toggled.connect(func(on: bool) -> void: Settings.set_value(setting, on))
	_row(key, toggle)
	return toggle


func _row(key: String, control: Control) -> void:
	var row := HBoxContainer.new()
	var label := Label.new()
	label.text = key
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	label.custom_minimum_size = Vector2(240, 0)
	row.add_child(label)
	row.add_child(control)
	content.add_child(row)
