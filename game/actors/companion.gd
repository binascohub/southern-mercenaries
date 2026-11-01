# Southern Mercenaries — GPL-3.0-or-later
class_name Companion
extends CharacterBody3D
## Animal amigo do Invocador (02-5-invocador.md, seção 4): segue o dono, ataca
## os monstros acordados perto dele com o elemento atual do dono (aplica o
## estado básico e conta para a fraqueza) e cada golpe devolve Essência ao
## Invocador. Os monstros também atacam os animais. Animal que cai não morre:
## foge ferido (some) e pode ser chamado de novo depois da recarga.
##
## Rede: como os monstros, só o servidor roda a IA; os outros PCs recebem
## posição, direção, vida e elemento pelo MultiplayerSynchronizer.

const FOLLOW_DISTANCE := 2.2
const LEASH := 12.0
const TAUNT_INTERVAL := 1.0

# Sincronizados.
var owner_peer := 1
var kind := "companion"
var element := "fire"
var health := 1.0
var max_health := 1.0
var yaw := 0.0
var net_position := Vector3.ZERO
## Para os monstros: um animal está sempre "de pé e conectado".
var alive := true
var connected := true
var hidden := false

var data: Dictionary
## Só no servidor.
var damage_fraction := 0.5
var time_left := 0.0
var _cooldown := 0.0
var _taunt_timer := 0.0
var _buffs := {}
var _shield := 0.0
var _shield_time := 0.0
var _snapshots := SnapshotBuffer.new()
var _last_net_position := Vector3.INF
var _material: StandardMaterial3D


## spawn: {owner, kind, position, max_health, damage_fraction, time, element}
static func create(spawn: Dictionary) -> Companion:
	var c := Companion.new()
	c.owner_peer = spawn.owner
	c.kind = spawn.kind
	c.element = spawn.get("element", "fire")
	c.position = spawn.position
	c.net_position = spawn.position
	c.max_health = spawn.max_health
	c.health = spawn.max_health
	c.damage_fraction = spawn.get("damage_fraction", 0.5)
	c.time_left = spawn.get("time", 0.0)
	c._add_synchronizer()
	return c


func _ready() -> void:
	add_to_group(&"companions")
	collision_layer = 2
	collision_mask = 1 | 4
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	_snapshots.delay = GameData.balance.net.interpolation_delay
	data = GameData.companions.get(kind, {})
	_build_visual()


func owner_player() -> Player:
	return get_parent().get_node_or_null(str(owner_peer)) as Player


func _physics_process(delta: float) -> void:
	if multiplayer.is_server():
		_think(delta)
		net_position = global_position
	else:
		if net_position != _last_net_position:
			_last_net_position = net_position
			_snapshots.push(net_position)
		global_position = _snapshots.sample()
	rotation.y = yaw
	if _material:
		var c := Elements.color(element) if data.get("element_color", true) else Color(data.color[0], data.color[1], data.color[2])
		_material.albedo_color = c.lerp(Color.WHITE, 0.15)


func _think(delta: float) -> void:
	var master := owner_player()
	if master == null or not master.alive:
		_flee()
		return
	element = master.element
	_cooldown = maxf(_cooldown - delta, 0.0)
	for id: String in _buffs.keys():
		_buffs[id].time -= delta
		if _buffs[id].time <= 0.0:
			_buffs.erase(id)
	if _shield_time > 0.0:
		_shield_time -= delta
		if _shield_time <= 0.0:
			_shield = 0.0
	if time_left > 0.0:
		time_left -= delta
		if time_left <= 0.0:
			_flee()
			return
	# Urso Guardião: provoca os monstros em volta de tempos em tempos.
	if data.get("taunt", 0.0) > 0.0:
		_taunt_timer -= delta
		if _taunt_timer <= 0.0:
			_taunt_timer = TAUNT_INTERVAL
			taunt_around(float(data.taunt), TAUNT_INTERVAL * 2.0)
	var target := _target(master)
	var goal := master.global_position
	var reach: float = data.get("range", 1.6)
	if target:
		goal = target.global_position
	var offset := goal - global_position
	offset.y = 0.0
	var dist := offset.length()
	var stop := reach * 0.85 if target else FOLLOW_DISTANCE
	if dist > stop:
		velocity = offset.normalized() * float(data.get("speed", 5.0)) * speed_mult()
		move_and_slide()
	else:
		velocity = Vector3.ZERO
	if dist > 0.01:
		yaw = atan2(offset.x, offset.z)
	global_position.y = 0.0
	if target and dist <= reach + 0.3 and _cooldown <= 0.0:
		_cooldown = float(data.get("cooldown", 1.0)) / speed_mult()
		_attack(master, target)


## Monstro acordado mais perto do dono (os animais não acordam grupos sozinhos).
func _target(master: Player) -> Enemy:
	var best: Enemy = null
	var best_d := LEASH
	for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
		# Bonecos do pátio de treino também servem de alvo (para testar os animais).
		if (e.state == Enemy.State.SLEEP and not e.data.get("dummy", false)) or e.health <= 0.0:
			continue
		var d := e.global_position.distance_to(master.global_position)
		if d < best_d:
			best = e
			best_d = d
	return best


func _attack(master: Player, target: Enemy) -> void:
	var bond := master.character.passive_value("bond") if master.character else 0.0
	var hit := {
		"damage": master.power * damage_fraction * (1.0 + bond) * damage_mult(),
		"element": master.element,
		"state": String(Elements.data(master.element).get("basic_state", "")) if _rng_roll() < 0.35 else "",
		"crit_chance": GameData.elements.crit_chance,
	}
	target.take_hit(hit)
	# Cada golpe de um animal amigo devolve Essência ao Invocador.
	master.resource = minf(master.resource + float(master.data.get("resource_per_companion_hit", 0.0)), master.max_resource)
	if data.get("ranged", false):
		get_parent().skills._fx.rpc("beam", global_position + Vector3.UP * 0.5,
			target.global_position + Vector3.UP * 0.5, 0.1, Elements.color(master.element), 0.15)


func _rng_roll() -> float:
	return randf()


## Monstros em volta passam a perseguir este animal (Urso, Fuga em Bando).
func taunt_around(radius: float, time: float) -> void:
	for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
		if e.global_position.distance_to(global_position) <= radius:
			e.taunt(self, time)


# --- Dano e suporte (servidor) -------------------------------------------------------

## Golpe de monstro; mesma assinatura do herói.
func take_damage(amount: float, _monster_level := 1, _attacker: Node3D = null) -> void:
	if not multiplayer.is_server() or health <= 0.0:
		return
	if _shield > 0.0:
		var absorbed := minf(_shield, amount)
		_shield -= absorbed
		amount -= absorbed
	health -= amount
	if health <= 0.0:
		_flee()


func heal(amount: float) -> void:
	health = minf(health + amount, max_health)


func add_buff(id: String, value: float, duration: float) -> void:
	_buffs[id] = {"value": value, "time": duration}


func add_shield(amount: float, duration: float) -> void:
	_shield = maxf(_shield, amount)
	_shield_time = duration


func damage_mult() -> float:
	return 1.0 + float(_buffs.get("damage", {}).get("value", 0.0))


func speed_mult() -> float:
	return 1.0 + float(_buffs.get("speed", {}).get("value", 0.0))


## Caiu ou acabou o tempo: foge (some); o spawner remove dos outros PCs.
func _flee() -> void:
	alive = false
	queue_free()


# --- Rede e visual --------------------------------------------------------------------

func _add_synchronizer() -> void:
	var config := SceneReplicationConfig.new()
	var always := [":net_position", ":yaw"]
	var on_change := [":health", ":max_health", ":element"]
	for prop in always + on_change:
		var path := NodePath("." + prop)
		config.add_property(path)
		config.property_set_spawn(path, true)
		config.property_set_replication_mode(path, SceneReplicationConfig.REPLICATION_MODE_ALWAYS
			if prop in always else SceneReplicationConfig.REPLICATION_MODE_ON_CHANGE)
	var sync := MultiplayerSynchronizer.new()
	sync.name = "Sync"
	sync.replication_config = config
	var interval: float = 1.0 / GameData.balance.net.state_rate_hz
	sync.replication_interval = interval
	sync.delta_interval = interval
	add_child(sync)


## Placeholder até os modelos: corpo na cor do elemento (o urso, marrom).
func _build_visual() -> void:
	var size: float = data.get("size", 0.6)
	var shape := CollisionShape3D.new()
	var sphere := SphereShape3D.new()
	sphere.radius = 0.4 * size
	shape.shape = sphere
	shape.position.y = 0.4 * size
	add_child(shape)
	# Modelo próprio (o Gorila Guardião, Micket, CC0), quando há; senão o corpo provisório abaixo.
	var model_name: String = data.get("model", "")
	if model_name != "" and Kit.has(model_name):
		var model := Kit.piece(model_name)
		model.scale = Vector3.ONE * (size / 1.4)
		add_child(model)
		return
	var body := MeshInstance3D.new()
	var mesh := CapsuleMesh.new()
	mesh.radius = 0.28 * size
	mesh.height = 0.9 * size
	body.mesh = mesh
	body.rotation.x = PI / 2.0
	body.position.y = (0.9 if data.get("flies", false) else 0.3) * size + 0.1
	_material = StandardMaterial3D.new()
	body.material_override = _material
	add_child(body)
	var head := MeshInstance3D.new()
	var head_mesh := SphereMesh.new()
	head_mesh.radius = 0.18 * size
	head_mesh.height = 0.36 * size
	head.mesh = head_mesh
	head.material_override = _material
	head.position = Vector3(0, body.position.y + 0.1 * size, 0.45 * size)
	add_child(head)
