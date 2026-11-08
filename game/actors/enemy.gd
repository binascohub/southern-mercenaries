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
var monster_id := "plague_frog"
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
## Golpe especial do chefe em curso, para a animação em todos os PCs: 0 nenhum, 1 pisão, 2 magia (cuspe), 3 investida, 4 rajada, 5 golpe pesado, 6 convocação.
var skill_pose := 0
var boss_timers := {}
var _wave_timer := -1.0  ## ondas de ajudantes (dados "waves"): tempo até a próxima, número da próxima e quem já veio
var _wave_index := 0
var _wave_adds: Array = []

var data: Dictionary
var _was_attacking := false

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
var _summon_time := 0.0
var _pose_time := 0.0
var _pose_shown := 0
var _pose_pitch := 0.0
var _pose_lift := 0.0
var _pose_yaw := 0.0
var _pose_scale := Vector3.ONE
var _visual_scale0 := Vector3.ZERO
var _trail_timer := 0.0
var _ripple: MeshInstance3D
## Modelo animado da família (rato, morcego, jacaré); null = cápsula.
var _model: MonsterModel
## Ninho de filhotes da Rainha: monte de palha e trapos (a cor do monstro, que
## pisca no golpe), palhas soltas, um caixote quebrado e filhotes de rato
## mexendo-se em cima. Igual em todos os PCs (sorteio pela posição).
func _build_nest(size: float) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(Vector2i(roundi(home.x * 10.0), roundi(home.z * 10.0)))
	var mound := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.75 * size
	sphere.height = 0.7 * size
	sphere.radial_segments = 14
	sphere.rings = 6
	mound.mesh = sphere
	mound.material_override = _material
	mound.position.y = 0.05
	_visual.add_child(mound)
	var straw := StandardMaterial3D.new()
	straw.albedo_color = Color(0.55, 0.45, 0.22)
	straw.roughness = 1.0
	var rag := StandardMaterial3D.new()
	rag.albedo_color = Color(0.3, 0.27, 0.22)
	rag.roughness = 1.0
	for i in 26:
		var stick := MeshInstance3D.new()
		var rod := CylinderMesh.new()
		rod.top_radius = 0.012
		rod.bottom_radius = 0.012
		rod.height = rng.randf_range(0.4, 0.9) * size
		rod.radial_segments = 4
		stick.mesh = rod
		stick.material_override = straw
		var angle := rng.randf() * TAU
		var reach := rng.randf_range(0.2, 0.85) * size
		stick.position = Vector3(cos(angle) * reach, 0.18 * size + rng.randf_range(-0.05, 0.12), sin(angle) * reach)
		stick.rotation = Vector3(PI / 2.0 + rng.randf_range(-0.4, 0.4), rng.randf() * TAU, rng.randf_range(-0.3, 0.3))
		_visual.add_child(stick)
	for i in 5:
		var cloth := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = Vector3(rng.randf_range(0.25, 0.5), 0.02, rng.randf_range(0.2, 0.4)) * size
		cloth.mesh = box
		cloth.material_override = rag
		var angle := rng.randf() * TAU
		cloth.position = Vector3(cos(angle), 0.0, sin(angle)) * rng.randf_range(0.3, 0.7) * size + Vector3.UP * 0.25 * size
		cloth.rotation = Vector3(rng.randf_range(-0.5, 0.5), rng.randf() * TAU, rng.randf_range(-0.5, 0.5))
		_visual.add_child(cloth)
	var crate := Kit.piece("Crate_Open")
	if crate:
		crate.scale = Vector3.ONE * 0.6 * size
		crate.position = Vector3(0.55, 0.05, -0.35) * size
		crate.rotation = Vector3(0.0, rng.randf() * TAU, 0.45)
		_visual.add_child(crate)
	# Filhotes: ratinhos parados/andando no lugar em cima do monte.
	if MonsterModel.has_family("rat"):
		for i in 3:
			var pup := MonsterModel.new()
			_visual.add_child(pup)
			pup.setup("rat", 0.28, Color(0.5, 0.42, 0.36))
			var angle := TAU * i / 3.0 + rng.randf() * 0.6
			pup.position = Vector3(cos(angle) * 0.35, 0.28, sin(angle) * 0.35) * size
			pup.rotation.y = angle + PI / 2.0
			pup.play("walk" if i % 2 == 0 else "idle", 0.0)


## Fuga (Coelho Dourado): tempo correndo depois do golpe e o ponto de passeio.
var _flee_time := 0.0
var _pounce_to := Vector3.INF  ## Lince: ponto para onde corre
var _pounce_run := 0.0  ## Lince: tempo que ainda corre na fuga
var _coins_lost := 0  ## moedas soltas desde o último teleporte (fuga "immortal")
var _patrol_pause := 0.0
var _stuck_time := 0.0
var _wander_to := Vector3.INF
## Peça do kit deste objeto (pote: os cacos são "<peça>_Shards").
var _kit_piece := ""
var _last_visual_pos := Vector3.INF
var _visual_speed := 0.0
## Desempenho: dormindo e longe de todo herói (fora da tela), o monstro some e para de pensar e de animar.
const DORMANT_RANGE := 42.0
var _dormant := false
var _dormant_check := 0.0


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
	_set_crowd_collision(false)
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	_snapshots.delay = GameData.balance.net.interpolation_delay
	data = GameData.get_monster(monster_id)
	_rng.randomize()
	_build_visual(data.size)


## Quem patrulha dormindo atravessa os outros bichos (ratos de 3 a 6 m de comprimento se
## travariam uns nos outros); acordado, volta a esbarrar neles.
func _set_crowd_collision(awake_now: bool) -> void:
	collision_mask = 1 | 2 | 16 | (4 if awake_now or not data.get("patrol", false) else 0)  # 16: lagoas e riachos (só peixes passam por cima da água)


func _physics_process(delta: float) -> void:
	_dormant_check -= delta
	if _dormant_check <= 0.0:
		_dormant_check = 0.4 + _rng.randf() * 0.2
		_set_dormant(_should_sleep_far())
	if _dormant:
		return
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
		_keep_in_leash()
		skill_pose = _boss_skill_pose(delta)
		net_position = global_position
	else:
		if net_position != _last_net_position:
			_last_net_position = net_position
			_snapshots.push(net_position)
		global_position = _snapshots.sample()
	_tick_visual(delta)


## Dormindo (sem patrulha) e a mais de DORMANT_RANGE de todo herói. Sem heróis (modo espectador), nunca.
func _should_sleep_far() -> bool:
	if state != State.SLEEP or data.get("patrol", false) or health <= 0.0 or status.mask() != 0:
		return false
	var players := get_tree().get_nodes_in_group(&"players")
	if players.is_empty():
		return false
	for p: Node3D in players:
		if p.global_position.distance_squared_to(global_position) < DORMANT_RANGE * DORMANT_RANGE:
			return false
	return true


func _set_dormant(on: bool) -> void:
	if on == _dormant:
		return
	_dormant = on
	visible = not on
	if _model:
		_model.set_dormant(on)


## Chefe com "leash" (raio em metros, dado do monstro): nunca se afasta mais que isso do ponto de nascimento, para não sair da sala do chefe.
func _keep_in_leash() -> void:
	var leash := float(data.get("leash", 0.0))
	if leash <= 0.0 or state == State.SLEEP:
		return
	var offset := global_position - home
	offset.y = 0.0
	if offset.length() > leash:
		global_position = home + offset.normalized() * leash
		global_position.y = 0.0


## O grupo acordou: vida e dano escalam com os jogadores de agora.
func wake(health_scale: float, damage: float) -> void:
	if state != State.SLEEP:
		return
	_set_dormant(false)
	health_mult = health_scale
	max_health = base_health() * health_mult
	health = max_health
	damage_mult = damage
	state = State.HIDDEN if data.get("ai", "") == "ambush" else State.CHASE
	_set_crowd_collision(true)
	if data.has("boss_ai"):
		phase = 1
		boss_timers = {"swarm": 8.0, "slam": 4.0}


## Ondas de ajudantes (dados "waves": first, interval, radius, toast e list, uma lista de [{monster, count}] por onda): acordado, o monstro invoca a próxima
## onda em volta de si a cada `interval` segundos; quando ele morre, os ajudantes das ondas que ainda estão vivos somem junto.
func _update_waves(delta: float) -> void:
	var waves: Dictionary = data.waves
	var list: Array = waves.list
	if _wave_index >= list.size():
		return
	if _wave_timer < 0.0:
		_wave_timer = float(waves.get("first", 8.0))
	_wave_timer -= delta
	if _wave_timer > 0.0:
		return
	_wave_timer = float(waves.get("interval", 25.0))
	start_summon()
	var before := get_tree().get_nodes_in_group(&"enemies")
	for entry: Dictionary in list[_wave_index]:
		get_tree().call_group(&"arena", &"spawn_adds", global_position, String(entry.monster), int(entry.count), float(waves.get("radius", 6.0)))
	for node in get_tree().get_nodes_in_group(&"enemies"):
		if node is Enemy and node not in before:
			_wave_adds.append(node)
	_wave_index += 1
	if waves.has("toast"):
		get_tree().call_group(&"arena", &"_toast_all", String(waves.toast), {"n": _wave_index})


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
	_set_crowd_collision(false)
	_wander_to = Vector3.INF
	status.clear()
	states_mask = 0
	health_mult = 1.0
	max_health = base_health()
	health = max_health
	phase = 0
	_pending.clear()


func _think(delta: float) -> void:
	if state == State.SLEEP:
		# Dormindo: sem IA nem movimento (03-inimigos.md, "Desempenho"), a não ser quem
		# "patrulha" (os ratos do Esgoto): anda por perto enquanto há um herói na área.
		if data.get("patrol", false):
			_think_patrol(delta)
		return
	_charge_cd = maxf(_charge_cd - delta, 0.0)
	_update_pending(delta)
	if data.has("waves"):
		_update_waves(delta)
	if data.get("ai", "") == "static":
		return  # ninho: não anda nem ataca
	if data.get("ai", "") == "flee":
		_think_flee(delta)
		return
	if data.get("ai", "") == "pounce":
		_think_pounce(delta)
		return
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
				if _strike.has("glob"):
					_throw_glob.rpc(_spit_at, _timer)
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
				if _special in ["spit", "slam", "gust"]:
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


## Patrulha de quem ainda não foi perturbado: vai a pontos sorteados em volta de
## onde nasceu (raio "patrol_radius"), para um pouco em cada um e troca de ponto se
## esbarra numa parede. Só mexe com um herói a menos de PATROL_RANGE (desempenho).
const PATROL_RANGE := 50.0


func _think_patrol(delta: float) -> void:
	var target := _nearest_player()
	if target == null or target.global_position.distance_to(global_position) > PATROL_RANGE:
		velocity = Vector3.ZERO
		return
	_patrol_pause = maxf(_patrol_pause - delta, 0.0)
	if _patrol_pause > 0.0:
		velocity = Vector3.ZERO
		return
	var radius := float(data.get("patrol_radius", 8.0))
	if _wander_to == Vector3.INF or global_position.distance_to(_wander_to) < 0.8:
		if _wander_to != Vector3.INF:
			_patrol_pause = _rng.randf_range(0.5, 2.5)  # chegou: descansa um pouco
		_wander_to = home + Vector3(_rng.randf_range(-radius, radius), 0, _rng.randf_range(-radius, radius))
		_stuck_time = 0.0
		velocity = Vector3.ZERO
		return
	var to := _wander_to - global_position
	to.y = 0.0
	var speed := float(data.move_speed) * float(data.get("patrol_speed", 0.6)) * status.move_mult()
	velocity = to.normalized() * speed
	move_and_slide()
	global_position.y = 0.0
	yaw = atan2(velocity.x, velocity.z)
	# Preso numa parede ou em outro bicho: escolhe outro ponto.
	_stuck_time = _stuck_time + delta if get_real_velocity().length() < speed * 0.25 else 0.0
	if _stuck_time > 0.4:
		_wander_to = Vector3.INF
		_patrol_pause = 0.1


## Não ataca: passeia devagar perto de onde nasceu; golpeado, corre para longe
## do herói mais perto por alguns segundos.
func _think_flee(delta: float) -> void:
	var flee: Dictionary = data.get("flee", {})
	_flee_time = maxf(_flee_time - delta, 0.0)
	var move := Vector3.ZERO
	if _flee_time > 0.0:
		var threat := _nearest_player()
		var away := global_position - threat.global_position if threat else Vector3(_rng.randf_range(-1, 1), 0, _rng.randf_range(-1, 1))
		away.y = 0.0
		move = away.normalized() * float(flee.get("speed", 7.0)) * status.move_mult()
		_wander_to = Vector3.INF
	else:
		if _wander_to == Vector3.INF or global_position.distance_to(_wander_to) < 0.5:
			_wander_to = home + Vector3(_rng.randf_range(-4, 4), 0, _rng.randf_range(-4, 4))
		var to := _wander_to - global_position
		to.y = 0.0
		move = to.normalized() * float(data.move_speed) if to.length() > 0.3 else Vector3.ZERO
	velocity = move
	move_and_slide()
	global_position.y = 0.0
	if move.length() > 0.1:
		yaw = atan2(move.x, move.z)
	state = State.CHASE


## Lince: espreita o herói mais perto que ainda tenha mais da metade da vida, dá o bote (leva a vida atual à metade) e foge correndo para longe; depois descansa.
## Se todos já estão com metade da vida ou menos, não ataca: só corre de um ponto a outro.
func _think_pounce(delta: float) -> void:
	var cfg: Dictionary = data.get("pounce", {})
	var run_speed := float(cfg.get("run_speed", 15.0)) * status.move_mult()
	_flee_time = maxf(_flee_time - delta, 0.0)
	var arena_node := get_tree().get_first_node_in_group(&"arena")
	var move := Vector3.ZERO
	if state == State.WINDUP:
		_timer -= delta
		velocity = Vector3.ZERO
		if _timer <= 0.0:
			var victim := _pounce_target()
			if victim and global_position.distance_to(victim.global_position) <= float(data.attack_range) + 0.8:
				victim.call(&"pounced")
			_pounce_to = arena_node.random_room_point(global_position, float(cfg.get("escape_min", 45.0))) if arena_node and arena_node.has_method(&"random_room_point") else Vector3.INF
			_pounce_run = float(cfg.get("escape_time", 7.0))
			state = State.CHASE
		return
	var victim := _pounce_target()
	if _pounce_run > 0.0:
		_pounce_run -= delta
		var to := _pounce_to - global_position
		to.y = 0.0
		if _pounce_to == Vector3.INF or to.length() < 1.5:
			_pounce_run = 0.0
			_flee_time = float(cfg.get("rest", 12.0))
		else:
			move = to.normalized() * run_speed
	elif _flee_time > 0.0:
		move = Vector3.ZERO  # descansa por um instante
	elif victim and global_position.distance_to(victim.global_position) < float(data.aggro_range):
		var to := victim.global_position - global_position
		to.y = 0.0
		if to.length() <= float(data.attack_range):
			state = State.WINDUP
			_timer = float(data.attack_windup)
			velocity = Vector3.ZERO
			yaw = atan2(to.x, to.z)
			return
		move = to.normalized() * run_speed * 0.8
	elif _nearest_player() != null and global_position.distance_to(_nearest_player().global_position) < float(data.aggro_range) * 1.5:
		# Ninguém atacável (todos com metade da vida ou menos): só corre, de ponto em ponto.
		if _pounce_to == Vector3.INF or global_position.distance_to(_pounce_to) < 2.0:
			_pounce_to = arena_node.random_room_point(global_position, 20.0) if arena_node and arena_node.has_method(&"random_room_point") else Vector3.INF
		var to := _pounce_to - global_position
		to.y = 0.0
		move = to.normalized() * run_speed * 0.7 if to.length() > 0.5 else Vector3.ZERO
	velocity = move
	move_and_slide()
	global_position.y = 0.0
	if move.length() > 0.1:
		yaw = atan2(move.x, move.z)
	state = State.CHASE


## Herói mais perto com mais da metade da vida (o único que o Lince ataca).
func _pounce_target() -> Node3D:
	var best: Node3D = null
	for node in get_tree().get_nodes_in_group(&"players"):
		var p := node as Player
		if p == null or not p.alive or p.health <= p.max_health * 0.5:
			continue
		if best == null or p.global_position.distance_to(global_position) < best.global_position.distance_to(global_position):
			best = p
	return best


## Teleporte do Dragãozinho Dourado: vai para outro ponto do mapa e passa a passear por lá.
func _teleport_away() -> void:
	var arena_node := get_tree().get_first_node_in_group(&"arena")
	if arena_node == null or not arena_node.has_method(&"random_room_point"):
		return
	var to: Vector3 = arena_node.random_room_point(global_position)
	global_position = to
	net_position = to
	home = to
	velocity = Vector3.ZERO
	_flee_time = 0.0
	_wander_to = Vector3.INF
	_last_visual_pos = Vector3.INF


## O Pacto da Rainha a deixa mais rápida.
func speed_mult() -> float:
	return float(data.get("pact_speed", 1.0)) if phase >= 3 else 1.0


## Convocação (ondas de ajudantes, enxame): o chefe levanta os braços por um instante (animação do chefe, `skill_pose` 6).
func start_summon() -> void:
	_summon_time = 1.4


## Golpe especial do chefe visto pela animação (servidor): lê o estado e o `_special`; 0 se não é chefe ou não está golpeando.
func _boss_skill_pose(delta: float) -> int:
	if category() != "boss" and category() != "miniboss":
		return 0
	if _summon_time > 0.0:
		_summon_time -= delta
		return 6
	if state != State.WINDUP and state != State.CHARGE and state != State.RECOVER:
		return 0
	match _special:
		"slam":
			return 1
		"spit":
			return 2
		"charge":
			return 3
		"gust":
			return 4
	return 5


## Pisão em área em volta do monstro (chefe), com aviso no chão.
func start_slam() -> void:
	_special = "slam"
	_strike = data.slam
	state = State.WINDUP
	_timer = float(_strike.windup)
	_spit_at = global_position
	velocity = Vector3.ZERO
	get_tree().call_group(&"arena", &"telegraph", _spit_at, float(_strike.radius), _timer)


## Rajada das Asas da Rainha: vento em volta dela que empurra (aviso no chão).
func start_gust() -> void:
	_special = "gust"
	_strike = data.gust
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
	if not multiplayer.is_server() or health <= 0.0 or data.get("invulnerable", false):
		return  # o Lince não toma dano
	if data.get("dummy", false):
		# Boneco do pátio: blindado recebe menos, nunca morre, avisa o painel de treino.
		amount *= float(data.get("damage_taken", 1.0))
		health -= amount
		if health <= 0.0:
			health = max_health
		_show_damage.rpc(amount, effect, hit_element, crit, combo)
		get_tree().call_group(&"arena", &"on_dummy_hit", amount, crit)
		return
	# Defesa do monstro ("damage_taken" < 1 = resistente): vale também para a vida, não só para os bonecos.
	amount *= float(data.get("damage_taken", 1.0))
	if data.get("ai", "") == "flee":
		# Levou golpe: dispara a correr e solta moedas (no fim, o resto delas).
		var flee: Dictionary = data.get("flee", {})
		_flee_time = float(flee.get("time", 3.0))
		var coins: Array = flee.get("coins_per_hit", [3, 6])
		var pieces := int(flee.get("coin_pieces", 1))
		var dropped := _rng.randi_range(int(coins[0]), int(coins[1]))
		get_tree().call_group(&"arena", &"drop_coins", global_position, dropped, pieces)
		if flee.get("immortal", false):
			# Nunca morre: ao soltar moedas demais, some e reaparece em outro ponto do mapa.
			_coins_lost += dropped
			_show_damage.rpc(amount, effect, hit_element, crit, combo)
			if _coins_lost >= int(flee.get("teleport_after_coins", 100)):
				_coins_lost = 0
				_teleport_away()
			return
		if health - amount <= 0.0:
			get_tree().call_group(&"arena", &"drop_coins", global_position, int(flee.get("coins_on_death", 30)), pieces * 2)
	if state == State.SLEEP:
		disturbed.emit(self)
	elif state == State.HIDDEN:
		state = State.CHASE  # acertado escondido: sai da água
	health -= amount
	_show_damage.rpc(amount, effect, hit_element, crit, combo)
	if health <= 0.0:
		if _model:
			_leave_corpse.rpc()
		elif data.get("shards", false):
			_shatter.rpc()
		for add: Variant in _wave_adds:
			if is_instance_valid(add) and not (add as Node).is_queued_for_deletion():
				(add as Node).queue_free()
		died.emit(self)
		queue_free()


## Veneno arremessado (todos os PCs): uma bola que sai do ferrão em arco e cai
## no aviso quando o golpe acontece.
@rpc("authority", "call_local", "reliable")
func _throw_glob(at: Vector3, time: float) -> void:
	var c: Array = _strike.get("glob", data.get("spit", {}).get("glob", [0.45, 0.85, 0.2]))
	var color := Color(c[0], c[1], c[2])
	var glob := Node3D.new()
	get_parent().add_child(glob)
	var start := global_position + Vector3.UP * 0.9 * float(data.size)
	glob.global_position = start
	Fx.orb(glob, color, "water", 0.16)
	Fx.trail(glob, color, "water", 0.12)
	var flight := minf(time, 0.6)
	var delay := maxf(time - flight, 0.0)
	var peak := (start + at) / 2.0 + Vector3.UP * 2.2
	var tween := glob.create_tween()
	tween.tween_interval(delay)
	tween.tween_property(glob, "global_position", peak, flight / 2.0).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tween.tween_property(glob, "global_position", at + Vector3.UP * 0.1, flight / 2.0).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	tween.tween_callback(func() -> void:
		Fx.burst(get_parent(), at, float(_strike.get("radius", 1.5)), color, "water", 0.5)
		glob.queue_free())
	if _model:
		_model.play("attack")


## Pote quebrado (todos os PCs): os cacos voam para fora, caem girando, ficam
## um tempo no chão e afundam.
@rpc("authority", "call_local", "reliable")
func _shatter() -> void:
	Sfx.play("wood", global_position, 2.0, randf_range(0.8, 1.1))
	var arena := get_tree().get_first_node_in_group(&"arena")
	var area_root: Node3D = arena.get("_area_root") if arena else null
	var shards := Kit.piece(_kit_piece + "_Shards") if _kit_piece != "" else null
	if shards == null or area_root == null or not is_instance_valid(area_root):
		return
	if _visual:
		_visual.visible = false
	area_root.add_child(shards)
	shards.global_position = global_position
	shards.rotation.y = yaw
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(global_position)
	for node in shards.get_children():
		var shard := node as Node3D
		if shard == null:
			continue
		var out := Vector3(shard.position.x, 0, shard.position.z)
		out = (out.normalized() if out.length() > 0.01 else Vector3(rng.randf_range(-1, 1), 0, rng.randf_range(-1, 1)).normalized())
		var land := shard.position + out * rng.randf_range(0.4, 1.3)
		land.y = 0.04
		var peak := (shard.position + land) / 2.0 + Vector3.UP * rng.randf_range(0.25, 0.6)
		var spin := Vector3(rng.randf_range(-6, 6), rng.randf_range(-6, 6), rng.randf_range(-6, 6))
		var tween := shard.create_tween()
		tween.tween_property(shard, "position", peak, 0.18).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
		tween.tween_property(shard, "position", land, 0.22).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
		shard.create_tween().tween_property(shard, "rotation", shard.rotation + spin * 0.4, 0.4)
	var fade := shards.create_tween()
	fade.tween_interval(4.0)
	fade.tween_property(shards, "position:y", -0.4, 1.5)
	fade.tween_callback(shards.queue_free)


## Morte (todos os PCs): o corpo fica no chão da área tocando a animação de
## morrer, afunda e some — o inimigo em si já saiu do jogo.
@rpc("authority", "call_local", "reliable")
func _leave_corpse() -> void:
	_voice("death")
	var arena := get_tree().get_first_node_in_group(&"arena")
	var area_root: Node3D = arena.get("_area_root") if arena else null
	if _visual == null or _model == null or area_root == null or not is_instance_valid(area_root):
		return
	if _element_gem:
		_element_gem.visible = false
	_model.set_color(Color.WHITE)
	_model.play("die", 0.1)
	var body := _visual
	_visual = null
	for child in body.get_children():
		if child != _model:
			child.visible = false  # aura, asas de cápsula etc.
	body.reparent(area_root)
	# Voador cai no chão.
	var tween := body.create_tween()
	if body.position.y > 0.2:
		tween.tween_property(body, "position:y", 0.0, 0.45).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	tween.tween_interval(1.6)
	tween.tween_property(body, "position:y", -0.8, 1.2)
	tween.tween_callback(body.queue_free)


## Voz do monstro (RPG Sound Pack): família pela aparência, ou pelo campo "sound" do monsters.json.
const VOICE_BY_LOOK := {
	"frog": "slime", "toad": "slime", "angler": "slime", "pork_shark": "beast", "nest": "slime", "mimic": "beetle",
	"scorpion": "beetle", "chitin_beast": "beetle", "chest_mimic": "beetle",
	"shadow_spirit": "shade", "skeleton": "shade", "zombie": "shade", "succubus": "shade", "dark_elf": "shade",
	"undead": "shade", "night_demon": "shade", "stalker": "wolfman", "necromancer": "shade", "demon_twelve": "giant",
	"troll": "ogre", "troll_mauler": "ogre", "barbarian_monster": "ogre", "champ_warrior": "ogre", "fungus": "ogre", "ogre": "ogre",
	"demon_boss": "giant", "golem_fire": "giant", "golem_ice": "giant", "golem_stone": "giant", "golem_king": "giant",
	"plank_monster": "giant", "forest": "giant", "forest_troll": "ogre", "demon": "giant", "lizard": "giant",
	"mutant": "beast", "goblin": "beast", "bat": "beast", "reptile": "beast", "baby_dragon": "beast", "lynx": "beast", "mine_automaton": "giant", "tin_sentinel": "giant", "mine_golem": "giant", "docks_scarecrow": "ogre", "ruins_wraith": "shade", "mine_scout": "beetle", "deer_buck": "beast", "deer_doe": "beast",
	"alien_bug": "beetle", "cactus": "ogre", "cobra": "beast", "crab": "beetle", "crawlmaster": "shade", "darsh": "giant", "earth_dragon": "giant", "exp_demon": "shade", "fatty": "ogre", "ghost_wing": "shade", "glutton": "giant", "golem_block": "giant", "hazmat": "shade", "horror": "giant", "lava_golem": "giant", "mushroom_cap": "ogre", "mutant_grunt": "ogre", "octaminator": "giant", "raven": "beast", "sonask": "shade", "spider_big": "beetle", "tentacleye": "slime", "werewolf": "wolfman", "rat": "beast", "gator": "beast",
}


func _voice_family() -> String:
	return str(data.get("sound", VOICE_BY_LOOK.get(str(data.get("look", "")), "")))


## kind: "attack" (grave e alto), "hurt" (mais agudo e baixo), "death" (mais grave).
func _voice(kind: String) -> void:
	var fam := _voice_family()
	if fam == "":
		return
	var big := float(data.get("size", 1.0))
	var base := clampf(1.25 - 0.25 * big, 0.7, 1.3)
	match kind:
		"attack":
			Sfx.play("m_" + fam, global_position, 2.0, base)
		"hurt":
			if randf() < 0.45:
				Sfx.play("m_" + fam, global_position, -4.0, base * 1.2)
		"death":
			Sfx.play("m_" + fam, global_position, 3.0, base * 0.8)


@rpc("authority", "call_local", "unreliable")
func _show_damage(amount: float, effect := "normal", hit_element := "", crit := false, combo := "") -> void:
	if str(data.get("category", "")) != "breakable":
		_voice("hurt")
		if amount > 0.0:
			Sfx.play("hit_crit" if crit else "hit", global_position, -2.0)  # o golpe que acertou (os packs "hit_N" e "hit_crit_N" do pacote de hits e socos)
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
	var on_change := [":state", ":health", ":max_health", ":states_mask", ":phase", ":skill_pose"]
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
	if data.has("pieces"):
		# Pote: o modelo sai da posição (o mesmo em todos os PCs).
		var pieces: Array = data.pieces
		kit_piece = pieces[absi(hash(Vector2i(roundi(home.x * 10.0), roundi(home.z * 10.0)))) % pieces.size()]
	_kit_piece = kit_piece
	var kit_node: Node3D = Kit.piece(kit_piece) if kit_piece != "" else null
	if kit_node:
		_visual.add_child(kit_node)
		if data.get("dummy", false):
			# Bonecos de elemento tingidos pela cor do elemento; gigante maior.
			kit_node.scale = Vector3.ONE * size / 0.9
	body.mesh = body_mesh
	body.rotation.x = PI / 2.0
	body.position.y = 0.3 * size
	body.visible = kit_node == null and _model == null and look != "nest"
	if look == "nest":
		_build_nest(size)
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
	elif look == "queen" and _model == null:
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

	# O elemento dos monstros aparece no aviso ao entrar na área (HUD), não
	# mais num losango em cima do monstro (decisão do autor).


func _tick_visual(delta: float) -> void:
	if _visual == null:
		return
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
	_tick_boss_pose(delta)


## Comprimento do aviso (s) de cada golpe especial do chefe, para pôr a animação no compasso.
func _pose_length(pose: int) -> float:
	match pose:
		1:
			return float(data.get("slam", {}).get("windup", 0.9))
		3:
			return float(data.get("charge", {}).get("windup", 0.8))
		4:
			return float(data.get("gust", {}).get("windup", 1.0))
		6:
			return 1.4
	return maxf(float(data.get("attack_windup", 0.6)), 0.3)


## Animação dos golpes especiais do chefe por cima de qualquer corpo (modelo animado, malha parada ou cápsula): o pisão sobe e desaba, a magia
## infla e se inclina para trás, a investida agacha e dispara, a rajada gira, a convocação ergue o corpo e o golpe pesado se arma e cai.
func _tick_boss_pose(delta: float) -> void:
	if _visual_scale0 == Vector3.ZERO:
		_visual_scale0 = _visual.scale
	if skill_pose != _pose_shown:
		_pose_shown = skill_pose
		_pose_time = 0.0
	_pose_time += delta
	var length := _pose_length(skill_pose)
	var p := clampf(_pose_time / length, 0.0, 1.0)
	var after := _pose_time - length  # tempo depois do aviso (o golpe saiu)
	var pitch := 0.0
	var lift := 0.0
	var yaw_extra := 0.0
	var squash := Vector3.ONE
	match skill_pose:
		1:
			if p < 1.0:
				pitch = -0.5 * ease(p, 0.6)
				lift = 0.55 * ease(p, 0.6)
				squash = Vector3(0.95, 1.1, 0.95)
			elif after < 0.7:
				pitch = 0.5
				squash = Vector3(1.12, 0.84, 1.12)
		2:
			if p < 1.0:
				pitch = -0.32 * p
				lift = 0.25 * p
				squash = Vector3.ONE * (1.0 + 0.14 * p + 0.03 * sin(_pose_time * 18.0))
			elif after < 0.5:
				pitch = 0.4
		3:
			if p < 1.0:
				pitch = 0.3 * p
				lift = -0.08 * p
				squash = Vector3(1.05, 1.0 - 0.14 * p, 1.1)
			else:
				pitch = 0.38
				squash = Vector3(0.94, 0.94, 1.16)
		4:
			yaw_extra = TAU * 2.0 * ease(minf(_pose_time / (length + 0.5), 1.0), 0.8)
			lift = 0.3 * sin(minf(_pose_time / (length + 0.5), 1.0) * PI)
			squash = Vector3.ONE * (1.0 + 0.1 * sin(_pose_time * 10.0))
		5:
			if p < 1.0:
				pitch = -0.22 * ease(p, 0.6)
				lift = 0.12 * p
			elif after < 0.4:
				pitch = 0.4
				squash = Vector3(1.06, 0.94, 1.06)
		6:
			lift = 0.45 * minf(_pose_time * 3.0, 1.0) + 0.05 * sin(_pose_time * 14.0)
			pitch = -0.25
			squash = Vector3.ONE * (1.06 + 0.04 * sin(_pose_time * 12.0))
	var k := minf(delta * 14.0, 1.0)
	_pose_pitch = lerpf(_pose_pitch, pitch, k)
	_pose_lift = lerpf(_pose_lift, lift, k)
	_pose_yaw = yaw_extra if skill_pose == 4 else lerpf(_pose_yaw, 0.0, k)
	_pose_scale = _pose_scale.lerp(squash, k)
	if absf(_pose_pitch) < 0.002 and absf(_pose_lift) < 0.002 and skill_pose == 0 and _pose_scale.is_equal_approx(Vector3.ONE):
		_visual.rotation.x = 0.0
		_visual.scale = _visual_scale0
		return
	_visual.rotation.y = yaw + _pose_yaw
	_visual.rotation.x = _pose_pitch
	_visual.scale = _visual_scale0 * _pose_scale
	_visual.position.y = (_visual.position.y + _pose_lift) if data.get("flyer", false) else _pose_lift


## Modelo animado: animação pelo estado e pela velocidade vista na tela (vale
## nos PCs que só recebem a posição); cor por cima da textura.
func _tick_model(delta: float, tint: Color) -> void:
	if _last_visual_pos != Vector3.INF and delta > 0.0:
		var moved := global_position - _last_visual_pos
		moved.y = 0.0
		_visual_speed = lerpf(_visual_speed, moved.length() / delta, 0.2)
	_last_visual_pos = global_position
	var attacking := state == State.WINDUP or state == State.CHARGE
	if attacking and not _was_attacking:
		_voice("attack")
	_was_attacking = attacking
	var key := "idle"
	match state:
		State.WINDUP:
			key = "attack"
		State.CHARGE:
			key = "run"
		State.SLEEP, State.HIDDEN:
			key = "walk" if state == State.SLEEP and _visual_speed > 0.3 else "idle"
		_:
			if _visual_speed > 2.5:
				key = "run"
			elif _visual_speed > 0.3:
				key = "walk"
	if _model.current() == "attack" and state == State.RECOVER and not _model.action_done():
		key = "attack"  # deixa o golpe terminar (depois volta a ficar parado, sem congelar na última pose)
	_model.play(key)
	# O chefe entra na fase de metade da vida (a Rainha ganhava asas de morcego; o Feiticeiro-Aranha só marca o estado).
	if data.get("look", "") in ["queen", "demon", "necromancer"] and health > 0.0 and health <= max_health * 0.5:
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
