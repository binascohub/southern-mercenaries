# Southern Mercenaries — GPL-3.0-or-later
class_name Enemy
extends CharacterBody3D
## Monstro corpo a corpo simples: dorme no seu lugar até o grupo de encontro
## acordar; então persegue o jogador de pé mais próximo e morde com um aviso
## visível antes do golpe (03-inimigos.md). Números em data/monsters.json; vida
## e dano escalam com os jogadores no momento em que o grupo acorda (07-rede.md).
##
## Rede: só o servidor roda a IA e aplica dano; os outros PCs recebem posição,
## direção, estado e vida pelo MultiplayerSynchronizer.

signal died(enemy: Enemy)
## Levou dano dormindo: o grupo dele acorda (só no servidor).
signal disturbed(enemy: Enemy)

enum State { CHASE, WINDUP, RECOVER, SLEEP }

const HITBOX_HEIGHT := 1.6

# Sincronizados.
var monster_id := "sewer_rat"
var health := 1.0
var max_health := 1.0
var yaw := 0.0
var state := State.SLEEP
## Grupo de encontro e lugar de origem (para voltar a dormir no checkpoint).
var group := ""
var home := Vector3.ZERO
## Posição no servidor; os clientes mostram com interpolação.
var net_position := Vector3.ZERO
## Dano +10% por jogador extra (13-balanceamento.md, 2.5). Só no servidor.
var damage_mult := 1.0

var data: Dictionary

var _timer := 0.0
var _visual: Node3D
var _material: StandardMaterial3D
var _base_color := Color(0.36, 0.28, 0.22)
var _flash := 0.0
var _shown_health := -1.0
var _eye_material: StandardMaterial3D
var _snapshots := SnapshotBuffer.new()
var _last_net_position := Vector3.INF


## Criado pelo spawner em todos os PCs, com os mesmos dados.
static func create(spawn: Dictionary) -> Enemy:
	var enemy := Enemy.new()
	enemy.monster_id = spawn.monster_id
	enemy.position = spawn.position
	enemy.net_position = spawn.position
	enemy.home = spawn.position
	enemy.group = spawn.get("group", "")
	enemy.yaw = spawn.get("yaw", 0.0)
	enemy.max_health = GameData.get_monster(enemy.monster_id).max_health
	enemy.health = enemy.max_health
	enemy._add_synchronizer()
	return enemy


func _ready() -> void:
	add_to_group(&"enemies")
	collision_layer = 4
	collision_mask = 1 | 2 | 4
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	_snapshots.delay = GameData.balance.net.interpolation_delay
	data = GameData.get_monster(monster_id)
	_build_visual(data.size)


func _physics_process(delta: float) -> void:
	if multiplayer.is_server():
		_think(delta)
		net_position = global_position
	else:
		if net_position != _last_net_position:
			_last_net_position = net_position
			_snapshots.push(net_position)
		global_position = _snapshots.sample()
	_tick_visual(delta)


## O grupo acordou: vida e dano escalam com os jogadores de agora.
func wake(health_mult: float, damage: float) -> void:
	if state != State.SLEEP:
		return
	max_health = data.max_health * health_mult
	health = max_health
	damage_mult = damage
	state = State.CHASE


## Todos caíram: quem sobreviveu volta ao seu lugar e dorme de novo.
func return_home() -> void:
	global_position = home
	net_position = home
	velocity = Vector3.ZERO
	state = State.SLEEP
	max_health = data.max_health
	health = max_health


func _think(delta: float) -> void:
	if state == State.SLEEP:
		return  # Dormindo: sem IA nem movimento (03-inimigos.md, "Desempenho").
	var target := _nearest_player()
	if target == null:
		velocity = Vector3.ZERO
		state = State.CHASE
		return
	var offset := target.global_position - global_position
	offset.y = 0.0
	var dist := offset.length()

	match state:
		State.CHASE:
			if dist <= data.attack_range:
				state = State.WINDUP
				_timer = data.attack_windup
				velocity = Vector3.ZERO
			else:
				velocity = offset.normalized() * data.move_speed
				move_and_slide()
			if dist > 0.01:
				yaw = atan2(offset.x, offset.z)
		State.WINDUP:
			_timer -= delta
			if _timer <= 0.0:
				if dist <= data.attack_range + 0.4:
					target.take_damage(data.damage * damage_mult)
				state = State.RECOVER
				_timer = data.attack_cooldown
		State.RECOVER:
			_timer -= delta
			if _timer <= 0.0:
				state = State.CHASE
	global_position.y = 0.0


func take_damage(amount: float) -> void:
	if not multiplayer.is_server() or health <= 0.0:
		return
	if state == State.SLEEP:
		disturbed.emit(self)
	health -= amount
	_show_damage.rpc(amount)
	if health <= 0.0:
		died.emit(self)
		queue_free()


@rpc("authority", "call_local", "unreliable")
func _show_damage(amount: float) -> void:
	DamageNumber.spawn(get_parent(), global_position + Vector3.UP * (data.size + 0.8), amount)


func _nearest_player() -> Player:
	var best: Player = null
	var best_dist: float = data.aggro_range
	for player: Player in get_tree().get_nodes_in_group(&"players"):
		if not player.alive or not player.connected:
			continue
		var d := global_position.distance_to(player.global_position)
		if d < best_dist:
			best = player
			best_dist = d
	return best


func _add_synchronizer() -> void:
	var config := SceneReplicationConfig.new()
	var always := [":net_position", ":yaw"]
	var on_change := [":state", ":health", ":max_health"]
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
	_eye_material = eye_material
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
	_visual.rotation.y = yaw
	if health < _shown_health:
		_flash = 0.12
	_shown_health = health
	_flash = maxf(_flash - delta, 0.0)
	# Dormindo: olhos quase apagados.
	_eye_material.albedo_color = Color(0.25, 0.05, 0.03) if state == State.SLEEP else Color(1.0, 0.15, 0.1)
	if _flash > 0.0:
		_material.albedo_color = Color(1, 1, 1)
	elif state == State.WINDUP:
		# Aviso do golpe: o corpo avermelha durante a preparação.
		_material.albedo_color = _base_color.lerp(Color(0.9, 0.2, 0.1), 0.7)
	else:
		_material.albedo_color = _base_color
