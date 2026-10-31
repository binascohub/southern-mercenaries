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
##
## Elementos (Fase 4, 02-0-elementos.md): todo monstro tem um elemento; os
## golpes dos jogadores passam por Elements.resolve_hit() (fraqueza, combos,
## crítico) e deixam estados (queimando, molhado, congelado…). Congelado,
## derrubado e atordoado não andam nem atacam; lentidões reduzem a velocidade;
## no vapor erra 30% dos ataques. Os outros PCs veem os estados pelo states_mask.
##
## Fase 7 (03-inimigos.md, seção 1): categorias (comum, elite, mini-chefe,
## chefe) multiplicam vida e dano; o "ai" de data/monsters.json escolhe o jeito
## de lutar — corpo a corpo, investida com aviso (charger), à distância com
## cuspe que marca o chão antes (ranged) e emboscada escondida na água (ambush).
## Elites "tóxicas" deixam poças de lodo por onde passam.

signal died(enemy: Enemy)
## Levou dano dormindo: o grupo dele acorda (só no servidor).
signal disturbed(enemy: Enemy)

enum State { CHASE, WINDUP, RECOVER, SLEEP, HIDDEN, CHARGE }

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
## Multiplicador de vida no despertar (o XP total sobe junto, 13-balanceamento.md 2.5).
var health_mult := 1.0
## Nível da área: vida e dano × 1,12^(nível − 1) (13-balanceamento.md 2.4).
var level := 1
## Elemento do monstro (data/monsters.json) e estados ativos (bits, para o visual).
var element := ""
var states_mask := 0
## Elite/mini-chefe por encontro ("" = a categoria do monstro) e modificador da elite.
var rank := ""
var modifier := ""
## Chefe: fase atual (sincronizada, para a barra do chefe) e temporizadores das ações.
var phase := 0
var boss_timers := {}

var data: Dictionary

var _timer := 0.0
## Estados elementais (só no servidor).
var status := StatusSet.new()
var _rng := RandomNumberGenerator.new()
var _element_gem: MeshInstance3D
## Empurrão/puxão de habilidade (Onda, Tornado): velocidade e tempo restante.
var _push := Vector3.ZERO
var _push_time := 0.0
## Provocado (Corpo de Ferro do Ninja, Urso Guardião): persegue este alvo enquanto durar.
var _taunt: Node3D
var _taunt_time := 0.0
var _visual: Node3D
var _material: StandardMaterial3D
var _base_color := Color(0.36, 0.28, 0.22)
var _flash := 0.0
var _shown_health := -1.0
var _eye_material: StandardMaterial3D
var _snapshots := SnapshotBuffer.new()
var _last_net_position := Vector3.INF
## Investida e cuspe: direção/alvo travados no aviso; recarga da investida.
var _charge_dir := Vector3.ZERO
var _charge_cd := 0.0
var _charge_hit: Array[Node] = []
var _spit_at := Vector3.ZERO
## Golpe no chão em preparação (cuspe, pisão): {radius, damage_mult, puddle_*}.
var _strike := {}
## Golpes agendados no chão (gás da Rainha): {at, radius, time, damage, extra}.
var _pending: Array[Dictionary] = []
var _special := ""
var _trail_timer := 0.0
var _ripple: MeshInstance3D
## Modelo animado da família (rato, morcego, jacaré); null = cápsula.
var _model: MonsterModel
var _last_visual_pos := Vector3.INF
var _visual_speed := 0.0


## Criado pelo spawner em todos os PCs, com os mesmos dados.
static func create(spawn: Dictionary) -> Enemy:
	var enemy := Enemy.new()
	enemy.monster_id = spawn.monster_id
	enemy.position = spawn.position
	enemy.net_position = spawn.position
	enemy.home = spawn.position
	enemy.group = spawn.get("group", "")
	enemy.level = spawn.get("level", 1)
	enemy.yaw = spawn.get("yaw", 0.0)
	enemy.rank = spawn.get("rank", "")
	enemy.modifier = spawn.get("modifier", "")
	enemy.data = GameData.get_monster(enemy.monster_id)
	enemy.element = enemy.data.get("element", "")
	enemy.max_health = enemy.base_health()
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
	_rng.randomize()
	_build_visual(data.size)


func _physics_process(delta: float) -> void:
	if multiplayer.is_server():
		var burn := status.tick(delta)
		if burn > 0.0:
			_hurt(burn, "dot", "fire", false, "")
		states_mask = status.mask()
		if not is_inside_tree() or health <= 0.0:
			return
		_taunt_time = maxf(_taunt_time - delta, 0.0)
		if _push_time > 0.0:
			_push_time -= delta
			move_and_collide(_push * delta)
			global_position.y = 0.0
		_think(delta)
		net_position = global_position
	else:
		if net_position != _last_net_position:
			_last_net_position = net_position
			_snapshots.push(net_position)
		global_position = _snapshots.sample()
	_tick_visual(delta)


## O grupo acordou: vida e dano escalam com os jogadores de agora.
func wake(health_scale: float, damage: float) -> void:
	if state != State.SLEEP:
		return
	health_mult = health_scale
	max_health = base_health() * health_mult
	health = max_health
	damage_mult = damage
	state = State.HIDDEN if data.get("ai", "") == "ambush" else State.CHASE
	if data.has("boss_ai"):
		phase = 1
		boss_timers = {"swarm": 8.0, "slam": 4.0}


func level_factor() -> float:
	return pow(1.12, level - 1)


## Comum, elite, mini-chefe ou chefe (a elite vem do encontro).
func category() -> String:
	return rank if rank != "" else String(data.get("category", "common"))


## Vida sem a escala de jogadores: base × nível × categoria × fator de chefe
## (13-balanceamento.md, 2.4).
func base_health() -> float:
	var mults: Dictionary = GameData.balance.get("category_mults", {}).get(category(), {})
	return data.max_health * level_factor() * float(mults.get("health", 1.0)) * float(data.get("boss_factor", 1.0))


func attack_damage(mult := 1.0) -> float:
	var mults: Dictionary = GameData.balance.get("category_mults", {}).get(category(), {})
	return data.damage * level_factor() * damage_mult * float(mults.get("damage", 1.0)) * mult


## XP do monstro: 5 × nível para comuns (13-balanceamento.md, seção 4).
func xp_value() -> float:
	return GameData.balance.xp_per_monster_level.get(category(), 5) * level * health_mult


## Todos caíram: quem sobreviveu volta ao seu lugar e dorme de novo.
func return_home() -> void:
	global_position = home
	net_position = home
	velocity = Vector3.ZERO
	state = State.SLEEP
	status.clear()
	states_mask = 0
	health_mult = 1.0
	max_health = base_health()
	health = max_health
	phase = 0
	_pending.clear()


func _think(delta: float) -> void:
	if state == State.SLEEP:
		return  # Dormindo: sem IA nem movimento (03-inimigos.md, "Desempenho").
	_charge_cd = maxf(_charge_cd - delta, 0.0)
	_update_pending(delta)
	if data.get("ai", "") == "static":
		return  # ninho: não anda nem ataca
	if state == State.HIDDEN:
		_think_hidden()
		return
	if not status.can_act():
		# Congelado, derrubado ou atordoado: perde o golpe (ou a investida) que preparava.
		velocity = Vector3.ZERO
		if state == State.WINDUP or state == State.CHARGE:
			state = State.CHASE
		return
	if state == State.CHARGE:
		_think_charge(delta)
		return
	var target := _nearest_player()
	var offset := target.global_position - global_position if target else Vector3.ZERO
	offset.y = 0.0
	var dist := offset.length() if target else INF
	# Chefe: fases, ajudantes e golpes no chão (mesmo sem alvo, a fase muda).
	if data.get("boss_ai", "") == "rat_queen" and RatQueen.update(self, delta, target, dist):
		global_position.y = 0.0
		return
	if target == null:
		velocity = Vector3.ZERO
		state = State.CHASE
		return
	var ai: String = data.get("ai", "melee")
	match state:
		State.CHASE:
			var charge: Dictionary = data.get("charge", {})
			if ai == "charger" and _charge_cd <= 0.0 and dist >= float(charge["min"]) and dist <= float(charge["max"]):
				# Investida: aviso (corpo vermelho) e direção travada.
				_special = "charge"
				state = State.WINDUP
				_timer = float(charge.windup)
				_charge_dir = offset.normalized()
				velocity = Vector3.ZERO
			elif ai == "ranged" and dist <= data.attack_range and dist >= float(data.get("keep_distance", 0.0)) * 0.6:
				# Cuspe: marca o chão onde o alvo está; quem sai a tempo escapa.
				_special = "spit"
				state = State.WINDUP
				_timer = data.attack_windup
				_spit_at = target.global_position
				velocity = Vector3.ZERO
				_strike = data.get("spit", {})
				get_tree().call_group(&"arena", &"telegraph", _spit_at, float(_strike.get("radius", 1.5)), _timer)
			elif ai != "ranged" and dist <= data.attack_range:
				_special = ""
				state = State.WINDUP
				_timer = data.attack_windup
				velocity = Vector3.ZERO
			else:
				var away := ai == "ranged" and dist < float(data.get("keep_distance", 0.0))
				velocity = (-offset if away else offset).normalized() * data.move_speed * status.move_mult() * speed_mult()
				move_and_slide()
				_toxic_trail(delta)
			if dist > 0.01:
				yaw = atan2(offset.x, offset.z)
		State.WINDUP:
			_timer -= delta
			if _special == "charge":
				yaw = atan2(_charge_dir.x, _charge_dir.z)
			if _timer <= 0.0:
				if _special == "charge":
					state = State.CHARGE
					_timer = float(data.charge.time)
					_charge_hit.clear()
					return
				if _special in ["spit", "slam"]:
					get_tree().call_group(&"arena", &"monster_strike", _spit_at, float(_strike.get("radius", 1.5)),
						attack_damage(float(_strike.get("damage_mult", 1.0))), level, self, _strike)
				# No vapor (combo), erra parte dos ataques.
				elif dist <= data.attack_range + 0.4 and _rng.randf() >= status.miss_chance():
					target.call(&"take_damage", attack_damage(), level, self)
				state = State.RECOVER
				_timer = data.attack_cooldown
		State.RECOVER:
			_timer -= delta
			if _timer <= 0.0:
				state = State.CHASE
	global_position.y = 0.0


## O Pacto da Rainha a deixa mais rápida.
func speed_mult() -> float:
	return float(data.get("pact_speed", 1.0)) if phase >= 3 else 1.0


## Pisão em área em volta do monstro (chefe), com aviso no chão.
func start_slam() -> void:
	_special = "slam"
	_strike = data.slam
	state = State.WINDUP
	_timer = float(_strike.windup)
	_spit_at = global_position
	velocity = Vector3.ZERO
	get_tree().call_group(&"arena", &"telegraph", _spit_at, float(_strike.radius), _timer)


## Golpe no chão daqui a `time` s (aviso agora): o gás dos canos.
func schedule_strike(at: Vector3, radius: float, time: float, damage: float, extra: Dictionary) -> void:
	get_tree().call_group(&"arena", &"telegraph", at, radius, time)
	_pending.append({"at": at, "radius": radius, "time": time, "damage": damage, "extra": extra})


func _update_pending(delta: float) -> void:
	for strike in _pending.duplicate():
		strike.time -= delta
		if strike.time <= 0.0:
			_pending.erase(strike)
			get_tree().call_group(&"arena", &"monster_strike", strike.at, strike.radius, strike.damage, level, self, strike.extra)


## Escondido (emboscada, na água): só aparece quando alguém chega bem perto,
## já dando o bote.
func _think_hidden() -> void:
	var target := _nearest_player()
	if target and target.global_position.distance_to(global_position) <= float(data.get("ambush_radius", 4.0)):
		state = State.WINDUP
		_special = ""
		_timer = data.attack_windup * 0.5
		var offset := target.global_position - global_position
		yaw = atan2(offset.x, offset.z)


## Investida: corre em linha reta e acerta cada herói no caminho uma vez.
func _think_charge(delta: float) -> void:
	var charge: Dictionary = data.charge
	_timer -= delta
	var collision := move_and_collide(_charge_dir * float(charge.speed) * delta)
	global_position.y = 0.0
	for player: Node3D in get_tree().get_nodes_in_group(&"players") + get_tree().get_nodes_in_group(&"companions"):
		if player in _charge_hit or not player.get("alive"):
			continue
		if player.global_position.distance_to(global_position) <= data.attack_range:
			_charge_hit.append(player)
			player.call(&"take_damage", attack_damage(float(charge.get("damage_mult", 1.0))), level, self)
	if _timer <= 0.0 or (collision and collision.get_collider() is StaticBody3D):
		state = State.RECOVER
		_timer = data.attack_cooldown
		_charge_cd = float(charge.get("cooldown", 4.0))


## Elite tóxica: deixa poças de lodo por onde passa (03-inimigos.md, seção 12).
func _toxic_trail(delta: float) -> void:
	if modifier != "toxic":
		return
	_trail_timer -= delta
	if _trail_timer <= 0.0:
		_trail_timer = 1.5
		get_tree().call_group(&"arena", &"add_hazard", global_position, 1.2, 4.0, attack_damage(0.4), level)


## Desloca o monstro `offset` metros em `time` segundos (sem atravessar paredes).
func push(offset: Vector3, time := 0.25) -> void:
	if not multiplayer.is_server() or is_boss():
		return
	offset.y = 0.0
	_push = offset / maxf(time, 0.01)
	_push_time = time


func taunt(target: Node3D, time: float) -> void:
	_taunt = target
	_taunt_time = time


## O golpe vem de trás do monstro (Golpe pelas Costas do Ninja).
func is_behind(from: Vector3) -> bool:
	var forward := Vector3(sin(yaw), 0, cos(yaw))
	var to_attacker := from - global_position
	to_attacker.y = 0.0
	return to_attacker.length() > 0.01 and forward.dot(to_attacker.normalized()) < -0.3


func is_boss() -> bool:
	return data.get("category", "") == "boss" or data.get("boss", false)


## Golpe de jogador com elemento (projétil, habilidade). Só no servidor.
## hit: {damage, element, state, crit_chance} (ver Elements.resolve_hit).
func take_hit(hit: Dictionary) -> Dictionary:
	if not multiplayer.is_server() or health <= 0.0:
		return {}
	var result := Elements.resolve_hit(hit, element, status, is_boss(), _rng)
	# Ninhos da Rainha: Fogo causa dano dobrado.
	if hit.get("element", "") == "fire":
		result.damage *= float(data.get("fire_mult", 1.0))
	_hurt(result.damage, result.effect, hit.get("element", ""), result.crit, result.combo)
	states_mask = status.mask()
	if result.spread_dps > 0.0 or not result.zone.is_empty():
		# Incêndio espalha o fogo; Lama e Vapor viram áreas no chão (combos, seção 7).
		get_tree().call_group(&"arena", &"element_combo", global_position, result)
	return result


## Dano sem elemento (queimando, testes). Só no servidor.
func take_damage(amount: float) -> void:
	_hurt(amount, "normal", "", false, "")


func _hurt(amount: float, effect: String, hit_element: String, crit: bool, combo: String) -> void:
	if not multiplayer.is_server() or health <= 0.0:
		return
	if data.get("dummy", false):
		# Boneco do pátio: blindado recebe menos, nunca morre, avisa o painel de treino.
		amount *= float(data.get("damage_taken", 1.0))
		health -= amount
		if health <= 0.0:
			health = max_health
		_show_damage.rpc(amount, effect, hit_element, crit, combo)
		get_tree().call_group(&"arena", &"on_dummy_hit", amount, crit)
		return
	if state == State.SLEEP:
		disturbed.emit(self)
	elif state == State.HIDDEN:
		state = State.CHASE  # acertado escondido: sai da água
	health -= amount
	_show_damage.rpc(amount, effect, hit_element, crit, combo)
	if health <= 0.0:
		died.emit(self)
		queue_free()


@rpc("authority", "call_local", "unreliable")
func _show_damage(amount: float, effect := "normal", hit_element := "", crit := false, combo := "") -> void:
	DamageNumber.spawn(get_parent(), global_position + Vector3.UP * (data.size + 0.8), amount,
		effect, hit_element, crit, combo)


## Herói ou animal amigo mais perto (ou quem provocou).
func _nearest_player() -> Node3D:
	if _taunt_time > 0.0 and is_instance_valid(_taunt) and _taunt.get("alive") and _taunt.get("connected"):
		return _taunt
	var best: Node3D = null
	var best_dist: float = data.aggro_range
	for player: Node3D in get_tree().get_nodes_in_group(&"players") + get_tree().get_nodes_in_group(&"companions"):
		# Invisível (Bomba de Fumaça): os monstros perdem o alvo.
		if not player.get("alive") or not player.get("connected") or player.get("hidden") or player.is_queued_for_deletion():
			continue
		var d := global_position.distance_to(player.global_position)
		if d < best_dist:
			best = player
			best_dist = d
	return best


func _add_synchronizer() -> void:
	var config := SceneReplicationConfig.new()
	var always := [":net_position", ":yaw"]
	var on_change := [":state", ":health", ":max_health", ":states_mask", ":phase"]
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

	# Placeholder por família (data "look"): rato (padrão), morcego, sapo,
	# jacaré e a Rainha; olhos vermelhos brilhando (clima sombrio).
	_visual = Node3D.new()
	add_child(_visual)
	var look: String = data.get("look", "rat")
	var c: Array = data.get("color", [0.36, 0.28, 0.22])
	_base_color = Color(c[0], c[1], c[2])
	_material = StandardMaterial3D.new()
	_material.albedo_color = _base_color
	# Elites maiores; voadores no alto.
	var scale_ := 1.25 if category() == "elite" else (1.15 if category() == "miniboss" else 1.0)
	_visual.scale = Vector3.ONE * scale_
	if data.get("flyer", false):
		_visual.position.y = 1.1
	if not data.get("dummy", false) and MonsterModel.has_family(look):
		_model = MonsterModel.new()
		_visual.add_child(_model)
		if not _model.setup(look, size, _base_color):
			_model.queue_free()
			_model = null
	var body := MeshInstance3D.new()
	var body_mesh := CapsuleMesh.new()
	body_mesh.radius = 0.3 * size
	body_mesh.height = 1.1 * size
	match look:
		"nest":
			# Monte de palha e trapos com filhotes: achatado e largo.
			body_mesh.radius = 0.6 * size
			body_mesh.height = 1.2 * size
		"toad":
			body_mesh.radius = 0.45 * size
			body_mesh.height = 0.95 * size
		"gator":
			body_mesh.radius = 0.28 * size
			body_mesh.height = 1.9 * size
	# Boneco de treino, barril e caixote: peças do kit (game/levels/kit.gd).
	var kit_piece: String = "Dummy" if data.get("dummy", false) else {"barrel": "Barrel", "crate": "Crate_Wooden"}.get(look, "")
	var kit_node: Node3D = Kit.piece(kit_piece) if kit_piece != "" else null
	if kit_node:
		_visual.add_child(kit_node)
		if data.get("dummy", false):
			# Bonecos de elemento tingidos pela cor do elemento; gigante maior.
			kit_node.scale = Vector3.ONE * size / 0.9
	body.mesh = body_mesh
	body.rotation.x = PI / 2.0
	body.position.y = 0.3 * size
	body.visible = kit_node == null and _model == null
	body.material_override = _material
	if look == "barrel":
		var barrel := CylinderMesh.new()
		barrel.top_radius = 0.4 * size
		barrel.bottom_radius = 0.4 * size
		barrel.height = 1.0 * size
		body.mesh = barrel
		body.rotation.x = 0.0
		body.position.y = 0.5 * size
	elif look == "crate":
		var crate := BoxMesh.new()
		crate.size = Vector3(0.85, 0.85, 0.85) * size
		body.mesh = crate
		body.rotation.x = 0.0
		body.position.y = 0.42 * size
	_visual.add_child(body)
	if look == "bat" and _model == null:
		for side in [-1.0, 1.0]:
			var wing := MeshInstance3D.new()
			var wing_mesh := BoxMesh.new()
			wing_mesh.size = Vector3(0.7 * size, 0.04, 0.4 * size)
			wing.mesh = wing_mesh
			wing.material_override = _material
			wing.position = Vector3(0.45 * side * size, 0.35 * size, 0)
			wing.rotation.z = 0.35 * side
			_visual.add_child(wing)
	elif look == "queen":
		# A coroa torta do rei caído e a cauda de filhotes entrelaçados.
		var crown := MeshInstance3D.new()
		var crown_mesh := CylinderMesh.new()
		crown_mesh.top_radius = 0.22 * size
		crown_mesh.bottom_radius = 0.18 * size
		crown_mesh.height = 0.18 * size
		crown.mesh = crown_mesh
		var gold := StandardMaterial3D.new()
		gold.albedo_color = Color(0.95, 0.75, 0.2)
		gold.metallic = 0.8
		crown.material_override = gold
		crown.position = Vector3(0, 0.62 * size, 0.35 * size)
		crown.rotation.z = 0.25
		if _model:
			# Sobre a cabeça do rato (frente +Z, cabeça a ~40% do comprimento).
			crown.position = Vector3(0, 0.3 * size, 0.52 * size)
			crown.rotation = Vector3(-0.35, 0, 0.25)
		_visual.add_child(crown)
	if look == "queen" and _model == null:
		var tail := MeshInstance3D.new()
		var tail_mesh := SphereMesh.new()
		tail_mesh.radius = 0.25 * size
		tail_mesh.height = 0.4 * size
		tail.mesh = tail_mesh
		tail.material_override = _material
		tail.position = Vector3(0, 0.15 * size, -0.85 * size)
		_visual.add_child(tail)
	# Aura da elite (dourada), do mini-chefe (roxa) e do chefe (vermelha).
	var aura_colors := {"elite": Color(1.0, 0.8, 0.25), "miniboss": Color(0.7, 0.35, 1.0), "boss": Color(0.9, 0.15, 0.1)}
	if aura_colors.has(category()):
		var aura := MeshInstance3D.new()
		var ring := TorusMesh.new()
		ring.inner_radius = 0.55 * size
		ring.outer_radius = 0.7 * size
		aura.mesh = ring
		var aura_material := StandardMaterial3D.new()
		aura_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		aura_material.albedo_color = aura_colors[category()]
		aura.material_override = aura_material
		aura.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		aura.position.y = 0.05
		_visual.add_child(aura)
	# Emboscada: só as bolhas na água aparecem enquanto está escondido.
	if data.get("ai", "") == "ambush":
		_ripple = MeshInstance3D.new()
		var disc := CylinderMesh.new()
		disc.top_radius = 0.9
		disc.bottom_radius = 0.9
		disc.height = 0.03
		_ripple.mesh = disc
		var ripple_material := StandardMaterial3D.new()
		ripple_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		ripple_material.albedo_color = Color(0.35, 0.5, 0.45, 0.6)
		ripple_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		_ripple.material_override = ripple_material
		_ripple.position.y = 0.06
		add_child(_ripple)

	var eye_material := StandardMaterial3D.new()
	eye_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	eye_material.albedo_color = Color(1.0, 0.15, 0.1)
	_eye_material = eye_material
	for side in ([] if data.get("breakable", false) or kit_node or _model else [-1.0, 1.0]):
		var eye := MeshInstance3D.new()
		var eye_mesh := SphereMesh.new()
		eye_mesh.radius = 0.05 * size
		eye_mesh.height = 0.1 * size
		eye.mesh = eye_mesh
		eye.material_override = eye_material
		eye.position = Vector3(0.12 * side * size, 0.42 * size, 0.5 * size)
		_visual.add_child(eye)

	# Ícone do elemento: losango na cor do elemento flutuando acima (03-inimigos.md).
	if element != "":
		_element_gem = MeshInstance3D.new()
		var gem := PrismMesh.new()
		gem.size = Vector3(0.3, 0.4, 0.3)
		_element_gem.mesh = gem
		var gem_material := StandardMaterial3D.new()
		gem_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		gem_material.albedo_color = Elements.color(element)
		_element_gem.material_override = gem_material
		_element_gem.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_element_gem.position.y = 0.6 * size + 0.55
		add_child(_element_gem)


func _tick_visual(delta: float) -> void:
	_visual.rotation.y = yaw
	if _ripple:
		var submerged := state == State.HIDDEN
		_visual.visible = not submerged
		if _element_gem:
			_element_gem.visible = not submerged
		_ripple.visible = submerged
		if submerged:
			_ripple.scale = Vector3.ONE * (1.0 + 0.15 * sin(Time.get_ticks_msec() / 200.0))
	elif data.get("flyer", false):
		_visual.position.y = 1.1 + 0.15 * sin(Time.get_ticks_msec() / 150.0)
	if health < _shown_health:
		_flash = 0.12
	_shown_health = health
	_flash = maxf(_flash - delta, 0.0)
	# Dormindo: olhos quase apagados.
	_eye_material.albedo_color = Color(0.25, 0.05, 0.03) if state == State.SLEEP else Color(1.0, 0.15, 0.1)
	if phase >= 3:
		_eye_material.albedo_color = Color(0.45, 0.1, 0.9)  # o Pacto: chamas negras nos olhos
	if _element_gem:
		# Sempre visível: dá para planejar o elemento antes de acordar o grupo.
		_element_gem.rotation.y += delta * 2.0
	# O estado mais forte tinge o corpo (congelado fica quase branco; queimando pisca).
	var tint := Color(0, 0, 0, 0)
	for id in StatusSet.ids_from_mask(states_mask):
		var strength := 0.75 if Elements.state_data(id).get("disables", false) else 0.45
		if id == "burning":
			strength = 0.35 + 0.25 * sin(Time.get_ticks_msec() / 60.0)
		if strength > tint.a:
			tint = Elements.state_color(id)
			tint.a = strength
	if _flash > 0.0:
		_material.albedo_color = Color(1, 1, 1)
	elif state == State.WINDUP or state == State.CHARGE:
		# Aviso do golpe: o corpo avermelha durante a preparação.
		_material.albedo_color = _base_color.lerp(Color(0.9, 0.2, 0.1), 0.7)
	else:
		_material.albedo_color = _base_color.lerp(Color(tint.r, tint.g, tint.b), tint.a)
	if _model:
		_tick_model(delta, tint)


## Modelo animado: animação pelo estado e pela velocidade vista na tela (vale
## nos PCs que só recebem a posição); cor por cima da textura.
func _tick_model(delta: float, tint: Color) -> void:
	if _last_visual_pos != Vector3.INF and delta > 0.0:
		var moved := global_position - _last_visual_pos
		moved.y = 0.0
		_visual_speed = lerpf(_visual_speed, moved.length() / delta, 0.2)
	_last_visual_pos = global_position
	var key := "idle"
	match state:
		State.WINDUP:
			key = "attack"
		State.CHARGE:
			key = "run"
		State.SLEEP, State.HIDDEN:
			key = "idle"
		_:
			if _visual_speed > 2.5:
				key = "run"
			elif _visual_speed > 0.3:
				key = "walk"
	if _model.current() == "attack" and state == State.RECOVER:
		key = "attack"  # deixa o golpe terminar
	_model.play(key)
	# A Rainha ganha asas de morcego na metade da vida (e as mantém).
	if data.get("look", "") == "queen" and health > 0.0 and health <= max_health * 0.5:
		_model.show_wings(true)
	var color := Color.WHITE
	if _flash > 0.0:
		color = Color(1.8, 1.8, 1.8)
	elif state == State.WINDUP or state == State.CHARGE:
		color = Color.WHITE.lerp(Color(1.0, 0.25, 0.15), 0.6)
	elif tint.a > 0.0:
		color = Color.WHITE.lerp(Color(tint.r, tint.g, tint.b), tint.a)
	_model.set_color(color)


## Família do modelo animado ("" = cápsula; testes e capturas).
func model_family() -> String:
	return _model.family if _model else ""


func model_animation() -> String:
	return _model.current() if _model else ""


func has_wings() -> bool:
	return _model != null and _model.wings_out()
