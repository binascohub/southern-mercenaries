# Southern Mercenaries — GPL-3.0-or-later
class_name Player
extends CharacterBody3D
## Herói controlável. Fase 1: Mago com ataque básico, ataque forte (segurar)
## e esquiva (02-1-mago.md, seção 5). Atributos e números vêm de data/classes.json.

signal health_changed(current: float, maximum: float)
signal resource_changed(current: float, maximum: float)
signal died

const AIM_ASSIST_ANGLE := deg_to_rad(15.0)
const PROJECTILE_HEIGHT := 1.0
const TURN_SPEED := 18.0

var class_id := "mage"
var data: Dictionary
var max_health := 100.0
var health := 100.0
var max_resource := 100.0
var resource := 100.0
var move_speed := 5.0
var power := 0.0
var alive := true

var _facing := Vector2(0, 1)
var _attack_cooldown := 0.0
var _charge_time := 0.0
var _evade_cooldown := 0.0
var _evade_time := 0.0
var _evade_dir := Vector2.ZERO
var _visual: Node3D
var _body_material: StandardMaterial3D
var _crystal_material: StandardMaterial3D
var _flash := 0.0


func _ready() -> void:
	add_to_group(&"players")
	collision_layer = 2
	collision_mask = 1 | 4
	# Visão de cima, sem gravidade nem plataformas.
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	_load_class()
	_build_visual()


func _load_class() -> void:
	data = GameData.get_class_data(class_id)
	var attrs: Dictionary = data.attributes
	max_health = data.max_health
	max_resource = data.max_resource
	health = max_health
	resource = max_resource
	move_speed = GameData.balance.base_move_speed * data.move_speed_pct / 100.0
	# Poder da classe = dano da arma + atributo × 0,5 (02-personagens.md, seção 4).
	power = data.weapon_damage + attrs[data.power_attribute] * GameData.balance.power_attribute_factor


func _physics_process(delta: float) -> void:
	_tick_visual(delta)
	if not alive:
		return
	_attack_cooldown = maxf(_attack_cooldown - delta, 0.0)
	_evade_cooldown = maxf(_evade_cooldown - delta, 0.0)
	_set_resource(resource + data.resource_regen * delta)

	var input := PlayerInput.gather(global_position + Vector3.UP * PROJECTILE_HEIGHT,
		get_viewport().get_camera_3d(), get_viewport())
	_simulate(input, delta)


## Toda a lógica que depende da entrada. Na rede, roda só no servidor.
func _simulate(input: PlayerInput, delta: float) -> void:
	if _evade_time > 0.0:
		_evade_time -= delta
		var evade: Dictionary = data.evade
		var speed: float = evade.distance / evade.duration
		velocity = Vector3(_evade_dir.x, 0, _evade_dir.y) * speed
		move_and_slide()
		return

	var aim := input.aim
	if aim == Vector2.ZERO and input.move.length() > 0.2:
		aim = input.move.normalized()
	if aim != Vector2.ZERO:
		if InputDevice.using_gamepad and Settings.aim_assist:
			aim = _assisted_aim(aim, data.basic_attack.range)
		_facing = aim

	velocity = Vector3(input.move.x, 0, input.move.y) * move_speed
	move_and_slide()
	global_position.y = 0.0

	if input.evade_pressed and _evade_cooldown <= 0.0:
		_evade_dir = input.move.normalized() if input.move.length() > 0.2 else _facing
		_evade_time = data.evade.duration
		_evade_cooldown = data.evade.cooldown
		_charge_time = 0.0
		return

	# Toque: ataque básico na hora. Segurando por charge_time e soltando: ataque forte.
	if input.attack_pressed and _attack_cooldown <= 0.0:
		_fire(data.basic_attack)
		_attack_cooldown = data.basic_attack.cooldown
	if input.attack_held:
		_charge_time += delta
	if input.attack_released:
		if _charge_time >= data.strong_attack.charge_time:
			_fire(data.strong_attack)
		_charge_time = 0.0


func is_charged() -> bool:
	return _charge_time >= data.strong_attack.charge_time


func evade_cooldown_left() -> float:
	return _evade_cooldown


func is_invulnerable() -> bool:
	return _evade_time > 0.0


func take_damage(amount: float) -> void:
	if not alive or is_invulnerable():
		return
	health = maxf(health - amount, 0.0)
	health_changed.emit(health, max_health)
	_flash = 0.15
	if amount >= max_health * GameData.balance.heavy_hit_fraction:
		InputDevice.vibrate(0.4, 0.8, 0.25)
	if health <= 0.0:
		alive = false
		_visual.rotation.x = -PI / 2.0
		_visual.position.y = 0.3
		died.emit()


func _set_resource(value: float) -> void:
	var clamped := clampf(value, 0.0, max_resource)
	if not is_equal_approx(clamped, resource):
		resource = clamped
		resource_changed.emit(resource, max_resource)


func _fire(attack: Dictionary) -> void:
	var projectile := Projectile.new()
	projectile.direction = Vector3(_facing.x, 0, _facing.y)
	projectile.speed = attack.projectile_speed
	projectile.max_range = attack.range
	projectile.radius = attack.radius
	projectile.pierce = attack.pierce
	projectile.damage = power * attack.power_pct
	projectile.color = Color(0.55, 0.75, 1.0)
	get_parent().add_child(projectile)
	projectile.global_position = global_position + Vector3.UP * PROJECTILE_HEIGHT \
		+ projectile.direction * 0.6


## Mira assistida leve: puxa para o inimigo mais próximo dentro do cone.
func _assisted_aim(aim: Vector2, attack_range: float) -> Vector2:
	var best := aim
	var best_dist := INF
	for enemy in get_tree().get_nodes_in_group(&"enemies"):
		var offset := Vector2(enemy.global_position.x - global_position.x,
			enemy.global_position.z - global_position.z)
		var dist := offset.length()
		if dist > attack_range or dist < 0.01 or dist >= best_dist:
			continue
		if absf(aim.angle_to(offset)) <= AIM_ASSIST_ANGLE:
			best = offset.normalized()
			best_dist = dist
	return best


func _build_visual() -> void:
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 1.8
	shape.shape = capsule
	shape.position.y = 0.9
	add_child(shape)

	# Placeholder até os modelos modulares: corpo de "roupa de baixo de pano"
	# (cor crua), cajado simples com cristal e o caderno de anotações.
	_visual = Node3D.new()
	add_child(_visual)
	_body_material = _material(Color(0.78, 0.72, 0.6))
	var body := MeshInstance3D.new()
	var body_mesh := CapsuleMesh.new()
	body_mesh.radius = 0.35
	body_mesh.height = 1.7
	body.mesh = body_mesh
	body.material_override = _body_material
	body.position.y = 0.85
	_visual.add_child(body)

	var staff := MeshInstance3D.new()
	var staff_mesh := CylinderMesh.new()
	staff_mesh.top_radius = 0.04
	staff_mesh.bottom_radius = 0.05
	staff_mesh.height = 1.7
	staff.mesh = staff_mesh
	staff.material_override = _material(Color(0.35, 0.22, 0.12))
	staff.position = Vector3(0.45, 0.9, 0.15)
	_visual.add_child(staff)

	_crystal_material = _material(Color(0.55, 0.75, 1.0), 1.5)
	var crystal := MeshInstance3D.new()
	var crystal_mesh := SphereMesh.new()
	crystal_mesh.radius = 0.1
	crystal_mesh.height = 0.2
	crystal.mesh = crystal_mesh
	crystal.material_override = _crystal_material
	crystal.position = Vector3(0.45, 1.8, 0.15)
	_visual.add_child(crystal)

	var notebook := MeshInstance3D.new()
	var notebook_mesh := BoxMesh.new()
	notebook_mesh.size = Vector3(0.22, 0.28, 0.06)
	notebook.mesh = notebook_mesh
	notebook.material_override = _material(Color(0.4, 0.28, 0.18))
	notebook.position = Vector3(-0.32, 0.95, 0.12)
	_visual.add_child(notebook)


func _tick_visual(delta: float) -> void:
	if alive:
		var target := atan2(_facing.x, _facing.y)
		_visual.rotation.y = lerp_angle(_visual.rotation.y, target, minf(TURN_SPEED * delta, 1.0))
	_flash = maxf(_flash - delta, 0.0)
	_body_material.albedo_color = Color(1, 0.35, 0.35) if _flash > 0.0 else Color(0.78, 0.72, 0.6)
	# O cristal brilha mais quando o ataque forte está carregado.
	_crystal_material.emission_energy_multiplier = 4.0 if is_charged() else 1.5


static func _material(color: Color, emission := 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	if emission > 0.0:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = emission
	return m
