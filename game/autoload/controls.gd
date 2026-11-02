# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Mapeamento de ações (08-controles.md). O jogo só consulta ações do Input Map,
## nunca teclas fixas. Os padrões ficam aqui; o remapeamento do jogador fica em
## user://controls.cfg e é aplicado por cima ao iniciar.
##
## Cada ação tem um vínculo de teclado/mouse ("kb") e um de controle ("pad").
## O remapeamento troca o vínculo principal da classe escolhida.

signal bindings_changed

const PATH := "user://controls.cfg"
## Versão do padrão do teclado: 2 = habilidades nos números 1–4 e poções em Q/E/R
## (decisão do autor). Arquivos antigos não levam as teclas antigas dessas ações.
const LAYOUT_VERSION := 3
## 3 = ataque básico no 1 (e no clique do mouse) e as oito habilidades nos números 2–9.
const LAYOUT_2_ACTIONS := [&"attack", &"skill_1", &"skill_2", &"skill_3", &"skill_4", &"skill_5", &"skill_6", &"skill_7", &"skill_8", &"potion_health", &"potion_mana", &"potion_elemental"]
const KB := "kb"
const PAD := "pad"

## Ações mostradas no menu de remapeamento, nesta ordem.
const REMAPPABLE: Array[StringName] = [
	&"move_up", &"move_down", &"move_left", &"move_right",
	&"aim_up", &"aim_down", &"aim_left", &"aim_right",
	&"attack", &"skill_1", &"skill_2", &"skill_3", &"skill_4", &"skill_5", &"skill_6", &"skill_7", &"skill_8",
	&"evade", &"jump", &"block", &"mount", &"potion_health", &"potion_mana", &"potion_elemental",
	&"interact", &"pickup_all", &"inventory", &"skills", &"menu", &"map", &"chat_quick",
]
## Ações analógicas: recebem a zona morta configurável.
const ANALOG: Array[StringName] = [
	&"move_up", &"move_down", &"move_left", &"move_right",
	&"aim_up", &"aim_down", &"aim_left", &"aim_right",
]
## Gatilhos usados como botão.
const TRIGGER_DEADZONE := 0.5

const PAD_BUTTON_LABELS := {
	JOY_BUTTON_A: "A", JOY_BUTTON_B: "B", JOY_BUTTON_X: "X", JOY_BUTTON_Y: "Y",
	JOY_BUTTON_BACK: "View", JOY_BUTTON_START: "Menu", JOY_BUTTON_GUIDE: "Guide",
	JOY_BUTTON_LEFT_STICK: "L3", JOY_BUTTON_RIGHT_STICK: "R3",
	JOY_BUTTON_LEFT_SHOULDER: "LB", JOY_BUTTON_RIGHT_SHOULDER: "RB",
	JOY_BUTTON_DPAD_UP: "D-Pad ↑", JOY_BUTTON_DPAD_DOWN: "D-Pad ↓",
	JOY_BUTTON_DPAD_LEFT: "D-Pad ←", JOY_BUTTON_DPAD_RIGHT: "D-Pad →",
}

## action -> {"kb": Array[InputEvent], "pad": Array[InputEvent]}
var _defaults := {}


func _ready() -> void:
	_build_defaults()
	_apply(_defaults)
	_load_user()
	apply_deadzone(Settings.deadzone)
	_extend_ui_navigation()


# --- API -------------------------------------------------------------------

## Vínculo principal de uma classe ("kb" ou "pad") ou null.
func get_binding(action: StringName, kind: String) -> InputEvent:
	for event in InputMap.action_get_events(action):
		if event_kind(event) == kind:
			return event
	return null


## Troca o vínculo principal. Se outra ação remapeável já usa o mesmo botão,
## as duas trocam entre si (08-controles.md, seção 4). Retorna a ação afetada.
func rebind(action: StringName, kind: String, event: InputEvent) -> StringName:
	var previous := get_binding(action, kind)
	var swapped: StringName = &""
	for other in REMAPPABLE:
		if other == action:
			continue
		var other_event := get_binding(other, kind)
		if other_event and events_equal(other_event, event):
			_replace_primary(other, kind, previous)
			swapped = other
	_replace_primary(action, kind, event)
	apply_deadzone(Settings.deadzone)
	_save_user()
	bindings_changed.emit()
	return swapped


func restore_defaults() -> void:
	_apply(_defaults)
	apply_deadzone(Settings.deadzone)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(PATH))
	bindings_changed.emit()


func apply_deadzone(value: float) -> void:
	for action in ANALOG:
		InputMap.action_set_deadzone(action, value)
	for action in [&"attack", &"evade"]:
		InputMap.action_set_deadzone(action, TRIGGER_DEADZONE)


## Texto curto do vínculo atual para a interface (teclado ou controle).
func binding_label(action: StringName, kind: String) -> String:
	return event_label(get_binding(action, kind))


static func event_kind(event: InputEvent) -> String:
	if event is InputEventKey or event is InputEventMouseButton:
		return KB
	if event is InputEventJoypadButton or event is InputEventJoypadMotion:
		return PAD
	return ""


static func event_label(event: InputEvent) -> String:
	if event == null:
		return "—"
	if event is InputEventKey:
		if not event.physical_keycode:
			return OS.get_keycode_string(event.keycode)
		var code: Key = event.physical_keycode
		# Mostra a tecla no layout do jogador (ex.: Z no AZERTY para a posição do W).
		if DisplayServer.get_name() != "headless":
			code = DisplayServer.keyboard_get_label_from_physical(code)
		return OS.get_keycode_string(code)
	if event is InputEventMouseButton:
		match event.button_index:
			MOUSE_BUTTON_LEFT:
				return TranslationServer.translate("INPUT_MOUSE_LEFT")
			MOUSE_BUTTON_RIGHT:
				return TranslationServer.translate("INPUT_MOUSE_RIGHT")
			MOUSE_BUTTON_MIDDLE:
				return TranslationServer.translate("INPUT_MOUSE_MIDDLE")
			MOUSE_BUTTON_WHEEL_UP:
				return TranslationServer.translate("INPUT_MOUSE_WHEEL_UP")
			MOUSE_BUTTON_WHEEL_DOWN:
				return TranslationServer.translate("INPUT_MOUSE_WHEEL_DOWN")
		return TranslationServer.translate("INPUT_MOUSE_BUTTON").format({"n": event.button_index})
	if event is InputEventJoypadButton:
		return PAD_BUTTON_LABELS.get(event.button_index, "#%d" % event.button_index)
	if event is InputEventJoypadMotion:
		var positive: bool = event.axis_value > 0.0
		match event.axis:
			JOY_AXIS_TRIGGER_LEFT:
				return "LT"
			JOY_AXIS_TRIGGER_RIGHT:
				return "RT"
			JOY_AXIS_LEFT_X:
				return "L →" if positive else "L ←"
			JOY_AXIS_LEFT_Y:
				return "L ↓" if positive else "L ↑"
			JOY_AXIS_RIGHT_X:
				return "R →" if positive else "R ←"
			JOY_AXIS_RIGHT_Y:
				return "R ↓" if positive else "R ↑"
		return "Axis %d" % event.axis
	return "?"


static func events_equal(a: InputEvent, b: InputEvent) -> bool:
	if a == null or b == null:
		return false
	return serialize(a) == serialize(b)


## Formato simples e estável para o arquivo de configuração.
static func serialize(event: InputEvent) -> Dictionary:
	if event is InputEventKey:
		return {"type": "key", "code": event.physical_keycode if event.physical_keycode else event.keycode}
	if event is InputEventMouseButton:
		return {"type": "mouse", "button": event.button_index}
	if event is InputEventJoypadButton:
		return {"type": "pad_button", "button": event.button_index}
	if event is InputEventJoypadMotion:
		return {"type": "pad_axis", "axis": event.axis, "sign": signf(event.axis_value)}
	return {}


static func deserialize(data: Dictionary) -> InputEvent:
	match data.get("type", ""):
		"key":
			return key(data.get("code", 0))
		"mouse":
			return mouse(data.get("button", MOUSE_BUTTON_LEFT))
		"pad_button":
			return pad(data.get("button", 0))
		"pad_axis":
			return axis(data.get("axis", 0), data.get("sign", 1.0))
	return null


static func key(code: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.physical_keycode = code
	return e


static func mouse(button: MouseButton) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = button
	return e


static func pad(button: JoyButton) -> InputEventJoypadButton:
	var e := InputEventJoypadButton.new()
	e.button_index = button
	e.device = -1
	return e


static func axis(joy_axis: JoyAxis, direction: float) -> InputEventJoypadMotion:
	var e := InputEventJoypadMotion.new()
	e.axis = joy_axis
	e.axis_value = signf(direction)
	e.device = -1
	return e


# --- Interno ---------------------------------------------------------------

func _build_defaults() -> void:
	var d := {}
	d[&"move_up"] = _pair([key(KEY_W)], [axis(JOY_AXIS_LEFT_Y, -1)])
	d[&"move_down"] = _pair([key(KEY_S)], [axis(JOY_AXIS_LEFT_Y, 1)])
	d[&"move_left"] = _pair([key(KEY_A)], [axis(JOY_AXIS_LEFT_X, -1)])
	d[&"move_right"] = _pair([key(KEY_D)], [axis(JOY_AXIS_LEFT_X, 1)])
	# No teclado a mira é a posição do mouse; estas ações são só do controle.
	d[&"aim_up"] = _pair([], [axis(JOY_AXIS_RIGHT_Y, -1)])
	d[&"aim_down"] = _pair([], [axis(JOY_AXIS_RIGHT_Y, 1)])
	d[&"aim_left"] = _pair([], [axis(JOY_AXIS_RIGHT_X, -1)])
	d[&"aim_right"] = _pair([], [axis(JOY_AXIS_RIGHT_X, 1)])
	d[&"attack"] = _pair([key(KEY_1), mouse(MOUSE_BUTTON_LEFT), key(KEY_KP_1)], [pad(JOY_BUTTON_A)])  # clique ou 1 (A no controle) = ataque simples (segurar: ataque forte)
	d[&"skill_1"] = _pair([key(KEY_2), key(KEY_KP_2)], [pad(JOY_BUTTON_RIGHT_SHOULDER)])
	d[&"skill_2"] = _pair([key(KEY_3), key(KEY_KP_3)], [pad(JOY_BUTTON_B)])
	d[&"skill_3"] = _pair([key(KEY_4), key(KEY_KP_4)], [pad(JOY_BUTTON_X)])
	d[&"skill_4"] = _pair([key(KEY_5), key(KEY_KP_5)], [pad(JOY_BUTTON_Y)])
	for i in 4:  # as quatro de baixo: só no teclado (6–9); o controle tem os quatro botões da frente nas quatro primeiras
		d[StringName("skill_%d" % (i + 5))] = _pair([key(KEY_6 + i), key(KEY_KP_6 + i)], [])
	d[&"evade"] = _pair([key(KEY_SPACE)], [axis(JOY_AXIS_TRIGGER_LEFT, 1)])
	# Pular: sem botão livre no controle (remapeável no menu de controles).
	d[&"jump"] = _pair([key(KEY_X)], [])
	d[&"mount"] = _pair([key(KEY_SHIFT)], [pad(JOY_BUTTON_LEFT_STICK)])
	# Bloquear / aparar (proposta, 08-controles.md): segurar.
	d[&"block"] = _pair([key(KEY_C)], [pad(JOY_BUTTON_LEFT_SHOULDER)])
	d[&"potion_health"] = _pair([key(KEY_Q)], [pad(JOY_BUTTON_DPAD_DOWN)])
	d[&"potion_mana"] = _pair([key(KEY_E)], [pad(JOY_BUTTON_DPAD_UP)])
	d[&"potion_elemental"] = _pair([key(KEY_R)], [pad(JOY_BUTTON_DPAD_RIGHT)])
	# Botão de interagir no controle: decisão em aberto (08-controles.md, seção 5).
	d[&"interact"] = _pair([mouse(MOUSE_BUTTON_RIGHT), key(KEY_G)], [])
	d[&"pickup_all"] = _pair([key(KEY_Z)], [axis(JOY_AXIS_TRIGGER_RIGHT, 1)])  # R2 pega todo o loot (o A é o ataque; o R1, a habilidade 1)
	d[&"inventory"] = _pair([key(KEY_I)], [pad(JOY_BUTTON_BACK)])
	# Habilidades: K no teclado; no controle, pelo botão na janela do inventário.
	d[&"skills"] = _pair([key(KEY_K)], [])
	d[&"menu"] = _pair([key(KEY_ESCAPE)], [pad(JOY_BUTTON_START)])
	d[&"map"] = _pair([key(KEY_M)], [pad(JOY_BUTTON_DPAD_LEFT)])
	d[&"chat_quick"] = _pair([key(KEY_T)], [pad(JOY_BUTTON_RIGHT_STICK)])
	# Zoom limitado da câmera (01-escopo.md, seção 2). Não remapeável por ora.
	d[&"zoom_in"] = _pair([mouse(MOUSE_BUTTON_WHEEL_UP)], [])
	d[&"zoom_out"] = _pair([mouse(MOUSE_BUTTON_WHEEL_DOWN)], [])
	_defaults = d


func _pair(kb: Array, pad_events: Array) -> Dictionary:
	return {KB: kb, PAD: pad_events}


func _apply(table: Dictionary) -> void:
	for action in table:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		InputMap.action_erase_events(action)
		for kind in [KB, PAD]:
			for event in table[action][kind]:
				InputMap.action_add_event(action, event.duplicate())


func _replace_primary(action: StringName, kind: String, event: InputEvent) -> void:
	var current := get_binding(action, kind)
	if current:
		InputMap.action_erase_event(action, current)
	if event:
		InputMap.action_add_event(action, event.duplicate())


func _save_user() -> void:
	var cfg := ConfigFile.new()
	for action in REMAPPABLE:
		for kind in [KB, PAD]:
			var event := get_binding(action, kind)
			cfg.set_value(kind, action, serialize(event) if event else {})
	cfg.set_value("meta", "layout", LAYOUT_VERSION)
	cfg.save(PATH)


func _load_user() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(PATH) != OK:
		return
	var old_layout := int(cfg.get_value("meta", "layout", 1)) < LAYOUT_VERSION
	for action in REMAPPABLE:
		for kind in [KB, PAD]:
			if not cfg.has_section_key(kind, action):
				continue
			if old_layout and kind == KB and action in LAYOUT_2_ACTIONS:
				continue
			var data: Dictionary = cfg.get_value(kind, action, {})
			_replace_primary(action, kind, deserialize(data) if not data.is_empty() else null)


## Menus navegáveis com o analógico esquerdo, além do direcional.
func _extend_ui_navigation() -> void:
	var extra := {
		&"ui_up": axis(JOY_AXIS_LEFT_Y, -1), &"ui_down": axis(JOY_AXIS_LEFT_Y, 1),
		&"ui_left": axis(JOY_AXIS_LEFT_X, -1), &"ui_right": axis(JOY_AXIS_LEFT_X, 1),
	}
	for action in extra:
		if not InputMap.action_has_event(action, extra[action]):
			InputMap.action_add_event(action, extra[action])
