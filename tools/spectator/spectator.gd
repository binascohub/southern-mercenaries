# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Modo espectador: abre uma área do jogo (padrão: o Cemitério) com uma câmera livre, sem herói à vista
## e sem interface, para olhar o mapa, os monstros e a decoração de perto.
##
##   XDG_DATA_HOME=$(mktemp -d) godot --path . res://tools/spectator/spectator.tscn -- [area] [x y z [inclinação_graus]]
## (inclinação: -26 padrão, -90 olha reto para baixo)
##
## O XDG_DATA_HOME temporário isola os saves e as configurações: a arena grava campanha e personagem em user://.
## Controles: W A S D andam, Q / E descem e sobem, Shift acelera; segure o botão direito do mouse e arraste para
## olhar; a roda do mouse muda a velocidade; F1 mostra/esconde a ajuda; Esc fecha.

const DEFAULT_AREA := "cemetery_01_yard"
const START_POS := Vector3(0, 34, 18)
const START_LOOK := Vector3(0, 0, -30)

var _arena: Node
var _cam: Camera3D
var _speed := 14.0
var _looking := false
var _yaw := 0.0
var _pitch := 0.0
var _help: Label


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var area: String = args[0] if args.size() > 0 else DEFAULT_AREA
	if not GameData.arenas.has(area):
		push_error("Área desconhecida: %s" % area)
		get_tree().quit(1)
		return
	Session.campaign = SaveSystem.new_campaign()
	Session.campaign["area"] = area
	Session.campaign["checkpoint"] = "start"
	_arena = load("res://game/levels/prototype_arena.tscn").instantiate()
	add_child(_arena)
	await get_tree().process_frame
	await get_tree().process_frame
	_arena.hud.visible = false
	var hero: Player = _arena.local_player
	if hero:
		hero.visible = false
		hero.process_mode = Node.PROCESS_MODE_DISABLED
	_cam = Camera3D.new()
	_cam.fov = 60.0
	_cam.far = 400.0
	add_child(_cam)
	var pos := START_POS
	var look := START_LOOK
	if args.size() >= 4:
		pos = Vector3(float(args[1]), float(args[2]), float(args[3]))
		var pitch_deg := float(args[4]) if args.size() >= 5 else -26.0
		look = pos + Vector3(0, tan(deg_to_rad(pitch_deg)), -1) if pitch_deg > -89.0 else pos + Vector3(0, -1, -0.001)
	_cam.global_position = pos
	_cam.look_at(look)
	_yaw = _cam.rotation.y
	_pitch = _cam.rotation.x
	_cam.make_current()
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	_help = Label.new()
	_help.text = "ESPECTADOR  ·  WASD anda  ·  Q/E desce/sobe  ·  Shift acelera  ·  botão direito + arrastar olha  ·  roda: velocidade  ·  F1: ajuda  ·  Esc: sair"
	_help.position = Vector2(12, 8)
	_help.add_theme_color_override(&"font_color", Color(1, 1, 1, 0.9))
	_help.add_theme_color_override(&"font_outline_color", Color(0, 0, 0, 1))
	_help.add_theme_constant_override(&"outline_size", 6)
	layer.add_child(_help)
	_label_bosses()


## Nome flutuando sobre cada mini-chefe e chefe (o espectador não tem a interface do jogo).
func _label_bosses() -> void:
	for node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy := node as Enemy
		if enemy == null or not enemy.data.get("category", "") in ["miniboss", "boss"]:
			continue
		var label := Label3D.new()
		label.text = "%s  (%s)" % [TranslationServer.translate(enemy.data.get("name_key", "")), enemy.monster_id]
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.no_depth_test = true
		label.font_size = 64
		label.outline_size = 14
		label.modulate = Color(1.0, 0.85, 0.3)
		label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		label.position = Vector3(0, 5.5 * float(enemy.data.get("size", 1.0)) / 2.0 + 1.5, 0)
		enemy.add_child(label)


func _unhandled_input(event: InputEvent) -> void:
	if _cam == null:
		return
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_RIGHT:
			_looking = mb.pressed
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED if _looking else Input.MOUSE_MODE_VISIBLE
		elif mb.pressed and mb.button_index == MOUSE_BUTTON_WHEEL_UP:
			_speed = minf(_speed * 1.25, 120.0)
		elif mb.pressed and mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_speed = maxf(_speed / 1.25, 1.0)
	elif event is InputEventMouseMotion and _looking:
		var motion := event as InputEventMouseMotion
		_yaw -= motion.relative.x * 0.004
		_pitch = clampf(_pitch - motion.relative.y * 0.004, -1.5, 1.5)
		_cam.rotation = Vector3(_pitch, _yaw, 0)
	elif event is InputEventKey and (event as InputEventKey).pressed and not (event as InputEventKey).echo:
		var key := (event as InputEventKey).keycode
		if key == KEY_F1:
			_help.visible = not _help.visible
		elif key == KEY_ESCAPE:
			get_tree().quit()


func _process(delta: float) -> void:
	if _cam == null:
		return
	var move := Vector3.ZERO
	if Input.is_physical_key_pressed(KEY_W):
		move.z -= 1.0
	if Input.is_physical_key_pressed(KEY_S):
		move.z += 1.0
	if Input.is_physical_key_pressed(KEY_A):
		move.x -= 1.0
	if Input.is_physical_key_pressed(KEY_D):
		move.x += 1.0
	if Input.is_physical_key_pressed(KEY_E):
		move.y += 1.0
	if Input.is_physical_key_pressed(KEY_Q):
		move.y -= 1.0
	if move == Vector3.ZERO:
		return
	var boost := 3.0 if Input.is_physical_key_pressed(KEY_SHIFT) else 1.0
	var basis := _cam.global_transform.basis
	var dir := basis.x * move.x + Vector3.UP * move.y + basis.z * move.z
	_cam.global_position += dir.normalized() * _speed * boost * delta
