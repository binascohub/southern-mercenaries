# Southern Mercenaries — GPL-3.0-or-later
class_name TopDownCamera
extends Camera3D
## Câmera de cima, inclinada (~55°), seguindo o personagem do jogador local.
## Sem rotação livre; zoom limitado (01-escopo.md, seção 2).

const PITCH_DEG := 55.0
const ZOOM_MIN := 11.0
const ZOOM_MAX := 20.0
const ZOOM_STEP := 1.5
const FOLLOW_SPEED := 8.0

var target: Node3D
var distance := 15.0


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
	return Vector3(0, sin(pitch), cos(pitch)) * distance
