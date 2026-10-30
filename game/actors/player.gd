# Southern Mercenaries — GPL-3.0-or-later
class_name Player
extends CharacterBody3D
## Herói controlável. Mago com ataque básico, ataque forte (segurar) e esquiva
## (02-1-mago.md, seção 5); números em data/classes.json.
##
## Rede: o nó se chama com o ID de rede do dono. O PC dono lê a entrada e a
## envia ao servidor; só o servidor simula, aplica dano e decide queda/revive.
## Posição e estado chegam aos outros PCs pelo MultiplayerSynchronizer.

signal health_changed(current: float, maximum: float)
signal resource_changed(current: float, maximum: float)
## Caiu (vida zerou). Só emitido no servidor.
signal downed
## Levou dano (só no servidor); interrompe uma reanimação em andamento.
signal hurt

const AIM_ASSIST_ANGLE := deg_to_rad(15.0)
const PROJECTILE_HEIGHT := 1.0
const TURN_SPEED := 18.0
## Cor do anel de cada jogador (1 a 4), para se reconhecerem no co-op.
const SLOT_COLORS: Array[Color] = [
	Color(0.95, 0.75, 0.2), Color(0.3, 0.7, 1.0), Color(0.4, 0.9, 0.4), Color(0.9, 0.4, 0.9),
]
const BODY_COLOR := Color(0.78, 0.72, 0.6)

# Sincronizados (servidor -> todos).
var peer_id := 1
var slot := 0
var class_id := "mage"
var facing := Vector2(0, 1)
var health := 100.0
var max_health := 100.0
var resource := 100.0
var max_resource := 100.0
var alive := true
var charge_time := 0.0
var revive_progress := 0.0
var evade_cooldown := 0.0
## false enquanto o dono caiu da rede: o herói espera parado e invulnerável.
var connected := true
## Posição no servidor; os clientes mostram com interpolação.
var net_position := Vector3.ZERO

var data: Dictionary
var move_speed := 5.0
var power := 0.0

# Só no servidor.
var _input := PlayerInput.new()
var _seen := PlayerInput.new()
var _attack_cooldown := 0.0
var _evade_time := 0.0
var _evade_dir := Vector2.ZERO

# Só no PC dono.
var _local_input := PlayerInput.new()
var _sent_input := PlayerInput.new()
var _input_timer := 0.0

# Só nos clientes.
var _snapshots := SnapshotBuffer.new()
var _last_net_position := Vector3.INF

var _visual: Node3D
var _body_material: StandardMaterial3D
var _crystal_material: StandardMaterial3D
var _revive_bar: MeshInstance3D
var _ring_material: StandardMaterial3D
var _flash := 0.0
var _shown_health := -1.0
var _shown_resource := -1.0


## Criado pelo spawner em todos os PCs, com os mesmos dados.
static func create(spawn: Dictionary) -> Player:
	var player := Player.new()
	player.peer_id = spawn.peer_id
	player.name = str(spawn.peer_id)
	player.slot = spawn.slot
	player.class_id = spawn.class_id
	player.position = spawn.position
	player.net_position = spawn.position
	player._add_synchronizer()
	return player


func _ready() -> void:
	add_to_group(&"players")
	_snapshots.delay = GameData.balance.net.interpolation_delay
	collision_layer = 2
	collision_mask = 1 | 4
	# Visão de cima, sem gravidade nem plataformas.
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	_load_class()
	_build_visual()


func is_local() -> bool:
	return peer_id == multiplayer.get_unique_id()


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
	if is_local():
		_send_local_input(delta)
	if multiplayer.is_server():
		_server_step(delta)
		net_position = global_position
	else:
		_follow_server()
	_tick_visual(delta)


func _follow_server() -> void:
	if net_position != _last_net_position:
		_last_net_position = net_position
		_snapshots.push(net_position)
	global_position = _snapshots.sample()


func _send_local_input(delta: float) -> void:
	var viewport := get_viewport()
	_local_input = PlayerInput.gather(_local_input,
		global_position + Vector3.UP * PROJECTILE_HEIGHT, viewport.get_camera_3d(), viewport)
	if _local_input.aim != Vector2.ZERO and InputDevice.using_gamepad and Settings.aim_assist:
		_local_input.aim = _assisted_aim(_local_input.aim, data.basic_attack.range)
	if multiplayer.is_server():
		_input = _local_input
		return
	# Movimento e mira a ~30 Hz; apertos e solturas saem na hora (07-rede.md).
	_input_timer -= delta
	var buttons_changed := _local_input.attack_presses != _sent_input.attack_presses \
		or _local_input.attack_releases != _sent_input.attack_releases \
		or _local_input.evade_presses != _sent_input.evade_presses \
		or _local_input.interact_held != _sent_input.interact_held
	if buttons_changed or _input_timer <= 0.0:
		_input_timer = 1.0 / GameData.balance.net.input_rate_hz
		_sent_input = _local_input
		_submit_input.rpc_id(1, _local_input.to_array())


@rpc("any_peer", "unreliable_ordered")
func _submit_input(packed: Array) -> void:
	if multiplayer.get_remote_sender_id() != peer_id:
		return
	_input = PlayerInput.from_array(packed)


# --- Simulação (servidor) ---------------------------------------------------

func _server_step(delta: float) -> void:
	var input := _input
	var attack_pressed := input.attack_presses != _seen.attack_presses
	var attack_released := input.attack_releases != _seen.attack_releases
	var evade_pressed := input.evade_presses != _seen.evade_presses
	_seen = input
	if not alive:
		velocity = Vector3.ZERO
		return

	_attack_cooldown = maxf(_attack_cooldown - delta, 0.0)
	evade_cooldown = maxf(evade_cooldown - delta, 0.0)
	resource = minf(resource + data.resource_regen * delta, max_resource)

	if _evade_time > 0.0:
		_evade_time -= delta
		var evade: Dictionary = data.evade
		velocity = Vector3(_evade_dir.x, 0, _evade_dir.y) * (evade.distance / evade.duration)
		move_and_slide()
		return

	var aim := input.aim
	if aim == Vector2.ZERO and input.move.length() > 0.2:
		aim = input.move.normalized()
	if aim != Vector2.ZERO:
		facing = aim.normalized()

	velocity = Vector3(input.move.x, 0, input.move.y) * move_speed
	move_and_slide()
	global_position.y = 0.0

	if evade_pressed and evade_cooldown <= 0.0:
		_evade_dir = input.move.normalized() if input.move.length() > 0.2 else facing
		_evade_time = data.evade.duration
		evade_cooldown = data.evade.cooldown
		charge_time = 0.0
		return

	# Toque: ataque básico na hora. Segurando por charge_time e soltando: ataque forte.
	if attack_pressed and _attack_cooldown <= 0.0:
		_fire(data.basic_attack)
		_attack_cooldown = data.basic_attack.cooldown
	if input.attack_held:
		charge_time += delta
	if attack_released or (not input.attack_held and charge_time > 0.0):
		if charge_time >= data.strong_attack.charge_time:
			_fire(data.strong_attack)
		charge_time = 0.0


## O dono caiu: o herói fica parado, sem entrada, e não leva dano.
func set_disconnected() -> void:
	connected = false
	_input = PlayerInput.new()
	_seen = PlayerInput.new()
	charge_time = 0.0


## Copia o estado de um herói que esperava o dono voltar.
func take_over(old: Player) -> void:
	health = old.health
	resource = old.resource
	alive = old.alive
	facing = old.facing


func wants_to_revive() -> bool:
	return alive and connected and _input.interact_held


func is_charged() -> bool:
	return charge_time >= data.strong_attack.charge_time


func evade_cooldown_left() -> float:
	return evade_cooldown


func is_invulnerable() -> bool:
	return _evade_time > 0.0 or not connected


func take_damage(amount: float) -> void:
	if not multiplayer.is_server() or not alive or is_invulnerable():
		return
	health = maxf(health - amount, 0.0)
	hurt.emit()
	if amount >= max_health * GameData.balance.heavy_hit_fraction:
		if peer_id == multiplayer.get_unique_id():
			_heavy_hit()
		elif peer_id in multiplayer.get_peers():
			_heavy_hit.rpc_id(peer_id)
	if health <= 0.0:
		alive = false
		charge_time = 0.0
		revive_progress = 0.0
		downed.emit()


func revive(fraction: float) -> void:
	alive = true
	health = max_health * fraction
	revive_progress = 0.0


## Volta ao começo da área com tudo cheio (checkpoint).
func reset_at(spot: Vector3) -> void:
	global_position = spot
	net_position = spot
	alive = true
	health = max_health
	resource = max_resource
	revive_progress = 0.0
	charge_time = 0.0
	_evade_time = 0.0
	evade_cooldown = 0.0


@rpc("authority", "call_local", "reliable")
func _heavy_hit() -> void:
	InputDevice.vibrate(0.4, 0.8, 0.25)


func _fire(attack: Dictionary) -> void:
	var dir := Vector3(facing.x, 0, facing.y)
	get_tree().call_group(&"arena", &"spawn_projectile", {
		"position": global_position + Vector3.UP * PROJECTILE_HEIGHT + dir * 0.6,
		"direction": dir,
		"speed": attack.projectile_speed,
		"range": attack.range,
		"radius": attack.radius,
		"pierce": attack.pierce,
		"damage": power * attack.power_pct,
		"color": SLOT_COLORS[slot].lerp(Color(0.55, 0.75, 1.0), 0.6),
	})


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


# --- Visual (todos os PCs) ----------------------------------------------------

func _add_synchronizer() -> void:
	var config := SceneReplicationConfig.new()
	var always := [":net_position", ":facing", ":charge_time", ":revive_progress", ":evade_cooldown"]
	var on_change := [":health", ":max_health", ":resource", ":max_resource", ":alive", ":connected"]
	for prop in always + on_change:
		var path := NodePath("." + prop)
		config.add_property(path)
		config.property_set_spawn(path, true)
		config.property_set_replication_mode(path, SceneReplicationConfig.REPLICATION_MODE_ALWAYS
			if prop in always else SceneReplicationConfig.REPLICATION_MODE_ON_CHANGE)
	var sync := MultiplayerSynchronizer.new()
	sync.name = "Sync"
	sync.replication_config = config
	# Estado a ~20 Hz (07-rede.md, seção 5).
	var interval: float = 1.0 / GameData.balance.net.state_rate_hz
	sync.replication_interval = interval
	sync.delta_interval = interval
	add_child(sync)


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
	_body_material = _material(BODY_COLOR)
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

	# Anel no chão com a cor do jogador.
	var ring := MeshInstance3D.new()
	var ring_mesh := TorusMesh.new()
	ring_mesh.inner_radius = 0.5
	ring_mesh.outer_radius = 0.62
	ring.mesh = ring_mesh
	var ring_material := _material(SLOT_COLORS[slot], 1.0)
	ring_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	ring.material_override = ring_material
	ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	ring.position.y = 0.03
	add_child(ring)
	_ring_material = ring_material

	# Barra de reanimação sobre o caído.
	_revive_bar = MeshInstance3D.new()
	var bar_mesh := BoxMesh.new()
	bar_mesh.size = Vector3(1.0, 0.08, 0.08)
	_revive_bar.mesh = bar_mesh
	var bar_material := _material(Color(0.4, 1.0, 0.5), 2.0)
	bar_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bar_material.no_depth_test = true
	_revive_bar.material_override = bar_material
	_revive_bar.position.y = 1.4
	_revive_bar.visible = false
	add_child(_revive_bar)


func _tick_visual(delta: float) -> void:
	if alive:
		var target := atan2(facing.x, facing.y)
		_visual.rotation.y = lerp_angle(_visual.rotation.y, target, minf(TURN_SPEED * delta, 1.0))
		_visual.rotation.x = 0.0
		_visual.position.y = 0.0
	else:
		_visual.rotation.x = -PI / 2.0
		_visual.position.y = 0.3
	if health < _shown_health:
		_flash = 0.15
	if health != _shown_health:
		_shown_health = health
		health_changed.emit(health, max_health)
	if not is_equal_approx(resource, _shown_resource):
		_shown_resource = resource
		resource_changed.emit(resource, max_resource)
	_flash = maxf(_flash - delta, 0.0)
	_body_material.albedo_color = Color(1, 0.35, 0.35) if _flash > 0.0 else BODY_COLOR
	# O cristal brilha mais quando o ataque forte está carregado.
	_crystal_material.emission_energy_multiplier = 4.0 if is_charged() else 1.5
	# Dono desconectado: anel cinza enquanto o herói espera.
	_ring_material.albedo_color = SLOT_COLORS[slot] if connected else Color(0.4, 0.4, 0.4)
	_revive_bar.visible = not alive and revive_progress > 0.0
	_revive_bar.scale.x = maxf(revive_progress, 0.01)


static func _material(color: Color, emission := 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	if emission > 0.0:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = emission
	return m
