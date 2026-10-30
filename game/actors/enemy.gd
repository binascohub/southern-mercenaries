# Southern Mercenaries — GPL-3.0-or-later
class_name Enemy
extends CharacterBody3D
## Monstro corpo a corpo simples: persegue o jogador vivo mais próximo e morde
## com um aviso visível antes do golpe (padrão simples e legível, 01-escopo.md).
## Os números vêm de data/monsters.json.

signal died(enemy: Enemy)

enum State { CHASE, WINDUP, RECOVER }

const HITBOX_HEIGHT := 1.6

var monster_id := "sewer_rat"
var data: Dictionary
var health := 1.0
var max_health := 1.0

var _state := State.CHASE
var _timer := 0.0
var _target: Node3D
var _visual: Node3D
var _material: StandardMaterial3D
var _base_color := Color(0.36, 0.28, 0.22)
var _flash := 0.0


func _ready() -> void:
	add_to_group(&"enemies")
	collision_layer = 4
	collision_mask = 1 | 2 | 4
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	data = GameData.get_monster(monster_id)
	max_health = data.max_health
	health = max_health
	_build_visual(data.size)


func _physics_process(delta: float) -> void:
	_tick_visual(delta)
	if not multiplayer.is_server():
		return
	_target = _nearest_player()
	if _target == null:
		velocity = Vector3.ZERO
		return
	var offset := _target.global_position - global_position
	offset.y = 0.0
	var dist := offset.length()

	match _state:
		State.CHASE:
			if dist <= data.attack_range:
				_state = State.WINDUP
				_timer = data.attack_windup
				velocity = Vector3.ZERO
			else:
				velocity = offset.normalized() * data.move_speed
				move_and_slide()
			_face(offset)
		State.WINDUP:
			_timer -= delta
			if _timer <= 0.0:
				if dist <= data.attack_range + 0.4:
					_target.take_damage(data.damage)
				_state = State.RECOVER
				_timer = data.attack_cooldown
		State.RECOVER:
			_timer -= delta
			if _timer <= 0.0:
				_state = State.CHASE
	global_position.y = 0.0


func take_damage(amount: float) -> void:
	if health <= 0.0:
		return
	health -= amount
	_flash = 0.12
	DamageNumber.spawn(get_parent(), global_position + Vector3.UP * (data.size + 0.8), amount)
	if health <= 0.0:
		died.emit(self)
		queue_free()


func _nearest_player() -> Node3D:
	var best: Node3D = null
	var best_dist: float = data.aggro_range
	for player in get_tree().get_nodes_in_group(&"players"):
		if not player.alive:
			continue
		var d := global_position.distance_to(player.global_position)
		if d < best_dist:
			best = player
			best_dist = d
	return best


func _face(offset: Vector3) -> void:
	if offset.length() > 0.01:
		_visual.rotation.y = atan2(offset.x, offset.z)


func _build_visual(size: float) -> void:
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	# Altura fixa e generosa: na visão de cima, quem acerta o rato na tela acerta o golpe.
	box.size = Vector3(0.7 * size, HITBOX_HEIGHT, 1.1 * size)
	shape.shape = box
	shape.position.y = HITBOX_HEIGHT / 2.0
	add_child(shape)

	# Placeholder: corpo de rato, olhos vermelhos brilhando (clima sombrio).
	_visual = Node3D.new()
	add_child(_visual)
	_material = StandardMaterial3D.new()
	_material.albedo_color = _base_color
	var body := MeshInstance3D.new()
	var body_mesh := CapsuleMesh.new()
	body_mesh.radius = 0.3 * size
	body_mesh.height = 1.1 * size
	body.mesh = body_mesh
	body.rotation.x = PI / 2.0
	body.position.y = 0.3 * size
	body.material_override = _material
	_visual.add_child(body)

	var eye_material := StandardMaterial3D.new()
	eye_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	eye_material.albedo_color = Color(1.0, 0.15, 0.1)
	for side in [-1.0, 1.0]:
		var eye := MeshInstance3D.new()
		var eye_mesh := SphereMesh.new()
		eye_mesh.radius = 0.05 * size
		eye_mesh.height = 0.1 * size
		eye.mesh = eye_mesh
		eye.material_override = eye_material
		eye.position = Vector3(0.12 * side * size, 0.42 * size, 0.5 * size)
		_visual.add_child(eye)


func _tick_visual(delta: float) -> void:
	_flash = maxf(_flash - delta, 0.0)
	if _flash > 0.0:
		_material.albedo_color = Color(1, 1, 1)
	elif _state == State.WINDUP:
		# Aviso do golpe: o corpo avermelha durante a preparação.
		_material.albedo_color = _base_color.lerp(Color(0.9, 0.2, 0.1), 0.7)
	else:
		_material.albedo_color = _base_color
