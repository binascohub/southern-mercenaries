# Southern Mercenaries — GPL-3.0-or-later
class_name RatQueen
extends RefCounted
## As 3 fases da Rainha dos Ratos (03-inimigos.md, seção 2), sem nós: o Enemy
## chama update() a cada quadro no servidor. Números em data/monsters.json.
##   1. Mãe Furiosa (100%–60%): investidas, pisão em área com aviso e um enxame
##      de Ratos Pestilentos a cada 20 s.
##   2. A Ninhada (60%–25%): volta ao ninho e protege 3 ninhos de filhotes;
##      enquanto houver ninho, regenera vida. Só morde quem chega perto.
##   3. O Pacto (25%–0%): o demônio toma o corpo; alaga a arena, fica mais
##      rápida e o gás tóxico sai dos canos em lugares marcados no chão.
## Os ajudantes não contam como encontro: somem quando ela cai.

## Fase pela vida (1, 2 ou 3); thresholds = [0,6, 0,25].
static func phase_for(ratio: float, thresholds: Array) -> int:
	if ratio > float(thresholds[0]):
		return 1
	return 2 if ratio > float(thresholds[1]) else 3


## true = cuidou do quadro (a IA comum não roda).
static func update(q: Enemy, delta: float, target: Node3D, dist: float) -> bool:
	var data := q.data
	var timers := q.boss_timers
	for key: String in timers:
		timers[key] = float(timers[key]) - delta
	var new_phase := phase_for(q.health / q.max_health, data.phases)
	if new_phase > q.phase:
		_enter(q, new_phase)
	match q.phase:
		1:
			if float(timers.get("swarm", 0.0)) <= 0.0:
				timers["swarm"] = float(data.swarm.interval)
				q.get_tree().call_group(&"arena", &"spawn_adds", q.global_position, String(data.swarm.monster),
					int(data.swarm.count), 3.0)
		2:
			if nests_alive(q) > 0:
				q.health = minf(q.health + q.max_health * float(data.nests.regen) * delta, q.max_health)
		3:
			if float(timers.get("gas", 0.0)) <= 0.0 and target:
				timers["gas"] = float(data.gas.interval)
				# Gás dos canos: perto de um herói, com aviso no chão.
				var angle := randf() * TAU
				var at := target.global_position + Vector3(cos(angle), 0, sin(angle)) * randf_range(0.0, 2.5)
				q.schedule_strike(at, float(data.gas.radius), float(data.gas.windup), q.attack_damage(float(data.gas.damage_mult)), data.gas)
	if q.state != Enemy.State.CHASE:
		return false
	# Pisão em área: quem está em volta tem o aviso para sair.
	if dist <= float(data.slam.radius) and float(timers.get("slam", 0.0)) <= 0.0:
		timers["slam"] = float(data.slam.interval)
		q.start_slam()
		return true
	# Na Ninhada fica no ninho: só ataca quem chega perto.
	if q.phase == 2 and dist > float(data.attack_range):
		var to_home := q.home - q.global_position
		to_home.y = 0.0
		q.velocity = to_home.normalized() * float(data.move_speed) if to_home.length() > 1.0 else Vector3.ZERO
		q.move_and_slide()
		if target:
			var offset := target.global_position - q.global_position
			q.yaw = atan2(offset.x, offset.z)
		return true
	return false


static func nests_alive(q: Enemy) -> int:
	var count := 0
	for node in q.get_tree().get_nodes_in_group(&"enemies"):
		var e := node as Enemy
		if e and e.monster_id == String(q.data.nests.monster) and e.health > 0.0 and not e.is_queued_for_deletion():
			count += 1
	return count


static func _enter(q: Enemy, new_phase: int) -> void:
	q.phase = new_phase
	var data := q.data
	var tree := q.get_tree()
	tree.call_group(&"arena", &"boss_phase", String(data.phase_keys[new_phase - 1]))
	match new_phase:
		2:
			# Três ninhos em volta do ninho dela.
			var nests: Dictionary = data.nests
			for i in int(nests.count):
				var angle := TAU * i / int(nests.count) + PI / 2.0
				var at := q.home + Vector3(cos(angle), 0, sin(angle)) * float(nests.radius)
				tree.call_group(&"arena", &"spawn_adds", at, String(nests.monster), 1, 0.0)
		3:
			tree.call_group(&"arena", &"flood_arena")
			q.boss_timers["gas"] = 1.5
