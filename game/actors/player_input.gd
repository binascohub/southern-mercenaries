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
var interact_presses := 0
var pickup_all_presses := 0
var potion_health_presses := 0
var potion_resource_presses := 0
var potion_elemental_presses := 0
var mount_presses := 0
var jump_presses := 0
var block_held := false
var block_presses := 0
## Atalhos de habilidade 1 a 8 (teclas 2 a 9; contadores de apertos).
const SKILL_SLOTS := 8
var skill_presses: Array[int] = [0, 0, 0, 0, 0, 0, 0, 0]


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
	input.interact_presses = previous.interact_presses + int(Input.is_action_just_pressed(&"interact"))
	input.pickup_all_presses = previous.pickup_all_presses + int(Input.is_action_just_pressed(&"pickup_all"))
	input.potion_health_presses = previous.potion_health_presses + int(Input.is_action_just_pressed(&"potion_health"))
	input.potion_resource_presses = previous.potion_resource_presses + int(Input.is_action_just_pressed(&"potion_mana"))
	input.potion_elemental_presses = previous.potion_elemental_presses + int(Input.is_action_just_pressed(&"potion_elemental"))
	input.mount_presses = previous.mount_presses + int(Input.is_action_just_pressed(&"mount") and not Session.ui_open)
	input.jump_presses = previous.jump_presses + int(Input.is_action_just_pressed(&"jump") and not Session.ui_open)
	input.block_held = Input.is_action_pressed(&"block") and not Session.ui_open
	input.block_presses = previous.block_presses + int(Input.is_action_just_pressed(&"block") and not Session.ui_open)
	for i in SKILL_SLOTS:
		input.skill_presses[i] = previous.skill_presses[i] \
			+ int(Input.is_action_just_pressed(StringName("skill_%d" % (i + 1))) and not Session.ui_open)
	# Com uma janela aberta (inventário), os botões não atacam nem esquivam.
	if Session.ui_open:
		input.attack_held = false
		input.interact_held = false
		input.attack_presses = previous.attack_presses
		input.attack_releases = previous.attack_releases + int(previous.attack_held)
		input.evade_presses = previous.evade_presses
		input.interact_presses = previous.interact_presses

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
		# Teclado: andando, o herói vira para onde as teclas apontam; a mira do mouse só vale ao atacar (botão segurado ou solto), ao usar uma habilidade ou parado.
		var shooting := input.attack_held or input.attack_releases != previous.attack_releases or input.attack_presses != previous.attack_presses
		var casting := false
		for i in SKILL_SLOTS:
			casting = casting or input.skill_presses[i] != previous.skill_presses[i]
		if input.move.length() > 0.2 and not shooting and not casting and not Session.ui_open:
			input.aim = input.move.normalized()
	return input


func to_array() -> Array:
	return [move.x, move.y, aim.x, aim.y, attack_held, interact_held,
		attack_presses, attack_releases, evade_presses, interact_presses,
		pickup_all_presses, potion_health_presses, potion_resource_presses, potion_elemental_presses] \
		+ skill_presses + [mount_presses, block_held, block_presses, jump_presses]


static func from_array(a: Array) -> PlayerInput:
	var input := PlayerInput.new()
	if a.size() != 26:
		return input
	input.move = Vector2(a[0], a[1]).limit_length(1.0)
	input.aim = Vector2(a[2], a[3]).limit_length(1.0)
	input.attack_held = bool(a[4])
	input.interact_held = bool(a[5])
	input.attack_presses = int(a[6])
	input.attack_releases = int(a[7])
	input.evade_presses = int(a[8])
	input.interact_presses = int(a[9])
	input.pickup_all_presses = int(a[10])
	input.potion_health_presses = int(a[11])
	input.potion_resource_presses = int(a[12])
	input.potion_elemental_presses = int(a[13])
	for i in SKILL_SLOTS:
		input.skill_presses[i] = int(a[14 + i])
	input.mount_presses = int(a[22])
	input.block_held = bool(a[23])
	input.block_presses = int(a[24])
	input.jump_presses = int(a[25])
	return input
