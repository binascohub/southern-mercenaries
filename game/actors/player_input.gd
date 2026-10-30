# Southern Mercenaries — GPL-3.0-or-later
class_name PlayerInput
extends RefCounted
## Entrada de um jogador em um frame. O PC dono do personagem lê o Input Map e
## envia isto ao servidor autoritativo, que é quem simula (01-escopo.md, seção 4).
##
## Apertos e solturas viajam como contadores crescentes, e não como "apertou
## neste frame": se um pacote se perder, o próximo ainda mostra a diferença.

var move := Vector2.ZERO
## Direção da mira no plano do chão (x, z). Zero = sem mira explícita.
var aim := Vector2.ZERO
var attack_held := false
var interact_held := false
var attack_presses := 0
var attack_releases := 0
var evade_presses := 0


## Lê o Input Map local, continuando os contadores de `previous`.
## `origin` é a posição do personagem (para a mira com mouse).
static func gather(previous: PlayerInput, origin: Vector3, camera: Camera3D, viewport: Viewport) -> PlayerInput:
	var input := PlayerInput.new()
	input.move = Input.get_vector(&"move_left", &"move_right", &"move_up", &"move_down")
	input.attack_held = Input.is_action_pressed(&"attack")
	input.interact_held = Input.is_action_pressed(&"interact")
	input.attack_presses = previous.attack_presses + int(Input.is_action_just_pressed(&"attack"))
	input.attack_releases = previous.attack_releases + int(Input.is_action_just_released(&"attack"))
	input.evade_presses = previous.evade_presses + int(Input.is_action_just_pressed(&"evade"))

	if InputDevice.using_gamepad:
		var stick := Input.get_vector(&"aim_left", &"aim_right", &"aim_up", &"aim_down")
		if Settings.invert_aim_y:
			stick.y = -stick.y
		input.aim = stick.normalized() if stick.length() > 0.0 else Vector2.ZERO
	elif camera:
		var mouse := viewport.get_mouse_position()
		var from := camera.project_ray_origin(mouse)
		var dir := camera.project_ray_normal(mouse)
		var hit: Variant = Plane(Vector3.UP, origin.y).intersects_ray(from, dir)
		if hit != null:
			var flat := Vector2(hit.x - origin.x, hit.z - origin.z)
			if flat.length() > 0.1:
				input.aim = flat.normalized()
	return input


func to_array() -> Array:
	return [move.x, move.y, aim.x, aim.y, attack_held, interact_held,
		attack_presses, attack_releases, evade_presses]


static func from_array(a: Array) -> PlayerInput:
	var input := PlayerInput.new()
	if a.size() != 9:
		return input
	input.move = Vector2(a[0], a[1]).limit_length(1.0)
	input.aim = Vector2(a[2], a[3]).limit_length(1.0)
	input.attack_held = bool(a[4])
	input.interact_held = bool(a[5])
	input.attack_presses = int(a[6])
	input.attack_releases = int(a[7])
	input.evade_presses = int(a[8])
	return input
