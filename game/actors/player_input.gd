# Southern Mercenaries — GPL-3.0-or-later
class_name PlayerInput
extends RefCounted
## Entrada de um jogador em um frame. Fica separada do personagem para que,
## na Fase 2 (rede), o cliente só envie isto ao servidor autoritativo.

var move := Vector2.ZERO
## Direção da mira no plano do chão (x, z). Zero = sem mira explícita.
var aim := Vector2.ZERO
var attack_pressed := false
var attack_held := false
var attack_released := false
var evade_pressed := false


## Lê o Input Map local. `origin` é a posição do personagem (mira com mouse).
static func gather(origin: Vector3, camera: Camera3D, viewport: Viewport) -> PlayerInput:
	var input := PlayerInput.new()
	input.move = Input.get_vector(&"move_left", &"move_right", &"move_up", &"move_down")
	input.attack_pressed = Input.is_action_just_pressed(&"attack")
	input.attack_held = Input.is_action_pressed(&"attack")
	input.attack_released = Input.is_action_just_released(&"attack")
	input.evade_pressed = Input.is_action_just_pressed(&"evade")

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
