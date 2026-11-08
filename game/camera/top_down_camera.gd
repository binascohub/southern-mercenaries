# Southern Mercenaries — GPL-3.0-or-later
class_name TopDownCamera
extends Camera3D
## Câmera de cima, inclinada (~55°), seguindo o personagem do jogador local.
## Zoom limitado (01-escopo.md, seção 2). O analógico direito (ações cam_*) gira a câmera em volta do herói e aproxima/afasta;
## o movimento e a mira do controle seguem o giro (PlayerInput.gather).

const PITCH_DEG := 55.0
## Padrão: o herói ocupa ~1/8 da altura da tela (09-interface.md, seção 2);
## do muito próximo (combate) ao médio (explorar), nunca distância de RTS.
const ZOOM_MIN := 8.0
const ZOOM_MAX := 17.0
const ZOOM_STEP := 1.5
const FOLLOW_SPEED := 8.0
## Giro pelo analógico (graus por segundo, com ele todo para o lado) e zoom contínuo (metros por segundo).
const TURN_SPEED := 120.0
const ZOOM_SPEED := 9.0

var target: Node3D
var distance := 10.5
## Giro em volta do herói (radianos; 0 = a visão de sempre, o norte para cima).
var yaw := 0.0


func _ready() -> void:
	fov = 50.0
	rotation_degrees = Vector3(-PITCH_DEG, 0, 0)
	current = true


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"zoom_in"):
		distance = clampf(distance - ZOOM_STEP, ZOOM_MIN, ZOOM_MAX)
	elif event.is_action_pressed(&"zoom_out"):
		distance = clampf(distance + ZOOM_STEP, ZOOM_MIN, ZOOM_MAX)


func _process(delta: float) -> void:
	if not Session.ui_open:
		var turn := Input.get_axis(&"cam_turn_left", &"cam_turn_right")
		if turn != 0.0:
			yaw = wrapf(yaw - deg_to_rad(TURN_SPEED) * turn * delta, -PI, PI)
		var zoom := Input.get_axis(&"cam_zoom_in", &"cam_zoom_out")
		if zoom != 0.0:
			distance = clampf(distance + ZOOM_SPEED * zoom * delta, ZOOM_MIN, ZOOM_MAX)
	rotation = Vector3(-deg_to_rad(PITCH_DEG), yaw, 0)
	if target == null:
		return
	var desired := target.global_position + _offset()
	global_position = global_position.lerp(desired, minf(FOLLOW_SPEED * delta, 1.0))


## Sem alvo (ex.: conectando), olha para o centro da área.
func snap() -> void:
	var center := target.global_position if target else Vector3.ZERO
	global_position = center + _offset()


func _offset() -> Vector3:
	var pitch := deg_to_rad(PITCH_DEG)
	return (Vector3(0, sin(pitch), cos(pitch)) * distance).rotated(Vector3.UP, yaw)
