# Southern Mercenaries — GPL-3.0-or-later
class_name SkillSystem
extends Node
## Executa as habilidades ativas (02-1-mago.md, seção 6) no servidor, a partir
## de data/skills.json. Cada habilidade tem um "effect":
##   projectile  projétil (pode explodir em área: Bola de Fogo)
##   nova        área em volta do herói (Nova de Gelo, Tremor)
##   cone        cone na direção da mira, empurra (Onda)
##   line        linha na direção da mira (Espinhos de Pedra)
##   instant     acerta na hora o alvo na mira (Relâmpago)
##   chain       salta entre inimigos (Corrente de Raios)
##   buff        bônus nos aliados em volta (Bênção das Chamas, Vento a Favor)
##   shield      escudo no aliado mais ferido por perto (Pele de Pedra)
##   teleport    teleporte na direção da mira, sem atravessar paredes
##   delayed     marca no chão e cai depois (Meteoro, Terremoto)
##   area        área que dura (Muralha de Fogo, Nevasca, Tornado, Tempestade, Chuva,
##               Fogueira do Caçador, chuvas do Arqueiro)
##   leap        salto para trás que deixa lento quem está perto (Salto para Trás)
##   trap        armadilha que prende quem pisar (até 3 por herói)
##   fan         várias flechas em leque (Leque de Flechas)
##   mark        marca o alvo na mira: recebe mais dano de todos (Marcar Alvo)
##   melee       cortes no inimigo à frente (Corte Duplo, Golpe da Chama…)
##   shadow_step teleporta para as costas do alvo; o próximo golpe causa mais dano
##   smoke       nuvem: o herói some para os monstros, que erram ataques nela
##   iron_body   menos dano recebido e provoca os monstros em volta
##   blink       salta entre vários inimigos cortando cada um (Golpe Relâmpago, Mil Cortes)
##   dash_strike atravessa o alvo como um raio (Lampejo)
##   summon      chama um animal amigo (Chamar Companheiro, Urso Guardião)
##   escape      vira revoada e reaparece à frente; os animais provocam (Fuga em Bando)
##   rescue      um animal reanima de longe o aliado caído mais perto (Resgate)
##   charge      investida em linha atravessando os inimigos (Investida; os finais do
##               Cavaleiro fazem 3 seguidas, indo e voltando)
##   taunt       provoca os monstros em volta (Desafio)
## Bônus, escudos e curas de grupo também valem para os animais amigos.
## Cavaleiro a pé: campos foot_* dão a versão mais fraca das habilidades do cavalo.
## "imbued": habilidade de classe que aplica o estado básico do elemento atual.
## Habilidades com alvo usam a mira como direção; quando precisam de um ponto
## (Meteoro, Nevasca), escolhem o inimigo mais perto no cone da mira.
## Todo dano passa por Enemy.take_hit (fraqueza, combos, crítico). Os efeitos
## visuais são discos e feixes simples, mandados a todos os PCs (_fx).

const TICK := 0.5
const AIM_CONE := deg_to_rad(30.0)

## Áreas que duram (servidor).
var _areas: Array[Dictionary] = []
## Golpes marcados que caem depois (servidor).
var _delayed: Array[Dictionary] = []
## Armadilhas no chão (servidor): {position, time, hit, caster, skill, rank}.
var _traps: Array[Dictionary] = []
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()


## Troca de área ou volta ao checkpoint: áreas, golpes marcados, armadilhas e
## efeitos visuais da área anterior somem (servidor e, pelo _fx, todos os PCs).
func clear() -> void:
	_areas.clear()
	_delayed.clear()
	_traps.clear()
	_clear_fx.rpc()


@rpc("authority", "call_local", "reliable")
func _clear_fx() -> void:
	for child in get_children():
		child.queue_free()


func _arena() -> Node:
	return get_parent()


## Usa a habilidade. Retorna false se não houve efeito (ex.: Relâmpago sem alvo),
## e aí o herói não gasta mana nem recarga.
func cast(player: Player, skill_id: String, rank: int) -> bool:
	if not multiplayer.is_server():
		return false
	var skill := Skills.def(skill_id)
	var aim := Vector3(player.facing.x, 0, player.facing.y).normalized()
	var origin := player.global_position
	var color := Elements.color(player.element)
	match String(skill.get("effect", "")):
		"projectile":
			_arena().spawn_projectile({
				"position": origin + Vector3.UP * Player.PROJECTILE_HEIGHT + aim * 0.6,
				"direction": aim, "speed": skill.speed, "range": skill.range,
				"radius": skill.radius, "pierce": int(skill.get("pierce", 0)), "damage": 0.0,
				"color": color, "hit": hit_for(player, skill, rank), "explode": float(skill.get("explode", 0.0)),
			})
		"nova":
			var hit := hit_for(player, skill, rank)
			var radius := float(skill.area)
			if not player.mounted and skill.has("foot_area"):
				radius = float(skill.foot_area)
				hit.damage = float(hit.damage) * float(skill.get("foot_power_mult", 1.0))
			for e in enemies_in(origin, radius):
				e.take_hit(hit)
			_fx.rpc("disc", origin, Vector3.ZERO, radius, color, 0.4)
		"cone":
			var hit := hit_for(player, skill, rank)
			var half := deg_to_rad(float(skill.angle) / 2.0)
			for e in enemies_in(origin, skill.range):
				var to := _flat(e.global_position - origin)
				if to.length() < 0.01 or absf(Vector2(aim.x, aim.z).angle_to(to)) <= half:
					e.take_hit(hit)
					e.push(Vector3(to.x, 0, to.y).normalized() * float(skill.push), 0.3)
			_fx.rpc("disc", origin + aim * skill.range * 0.5, Vector3.ZERO, skill.range * 0.5, color, 0.4)
		"line":
			var hit := hit_for(player, skill, rank)
			var end: Vector3 = origin + aim * float(skill.range)
			for e in enemies_in(origin, skill.range + skill.width):
				if _distance_to_segment(e.global_position, origin, end) <= skill.width / 2.0:
					e.take_hit(hit)
			_fx.rpc("beam", origin, end, skill.width, color, 0.5)
		"instant":
			var target := target_in_aim(player, skill.range)
			if target == null:
				return false
			target.take_hit(hit_for(player, skill, rank))
			_fx.rpc("beam", origin + Vector3.UP, target.global_position + Vector3.UP * 0.5, 0.25, color, 0.25)
		"chain":
			var target := target_in_aim(player, skill.range)
			if target == null:
				return false
			var hit := hit_for(player, skill, rank)
			var hits: Array[Enemy] = []
			var from := origin + Vector3.UP
			for i in Skills.jumps(skill, rank):
				var step := hit.duplicate()
				step.damage = float(hit.damage) * pow(1.0 - float(skill.falloff), i)
				target.take_hit(step)
				hits.append(target)
				_fx.rpc("beam", from, target.global_position + Vector3.UP * 0.5, 0.18, color, 0.3)
				from = target.global_position + Vector3.UP * 0.5
				target = _nearest(target.global_position, skill.jump_range, hits)
				if target == null:
					break
		"buff":
			var value := Skills.scaled(skill, "value", "per_rank", rank)
			for p in allies_in(origin, skill.area):
				p.add_buff(String(skill.buff), value, skill.duration)
			for comp in companions_in(origin, skill.area):
				comp.add_buff(String(skill.buff), value, skill.duration)
			_fx.rpc("disc", origin, Vector3.ZERO, skill.area, color, 0.6)
		"shield":
			var amount := player.power * Skills.scaled(skill, "value", "per_rank", rank)
			if skill.has("area"):
				# Flecha Baluarte: todos os aliados em volta.
				for p in allies_in(origin, skill.area):
					p.add_shield(amount, skill.duration)
				for comp in companions_in(origin, skill.area):
					comp.add_shield(amount, skill.duration)
				_fx.rpc("disc", origin, Vector3.ZERO, skill.area, color, 0.6)
			else:
				var best: Player = player
				for p in allies_in(origin, skill.range):
					if p.health / p.max_health < best.health / best.max_health:
						best = p
				best.add_shield(amount, skill.duration)
				_fx.rpc("disc", best.global_position, Vector3.ZERO, 1.2, color, 0.6)
		"leap":
			for e in enemies_in(origin, skill.area):
				Elements.apply_state(e.status, String(skill.state), e.element, e.is_boss())
			_fx.rpc("disc", origin, Vector3.ZERO, skill.area, color, 0.4)
			player.teleport_to(_ray_limited(player, origin, origin - aim * float(skill.distance)))
		"trap":
			var spot := _ray_limited(player, origin, origin + aim * float(skill.distance))
			var mine := _traps.filter(func(t: Dictionary) -> bool: return t.caster == player)
			if mine.size() >= int(skill.max_traps):
				_traps.erase(mine[0])
			var trap_hit := hit_for(player, skill, rank)
			trap_hit.root = Skills.scaled(skill, "root", "root_per_rank", rank)
			_traps.append({"position": spot, "time": float(skill.duration), "hit": trap_hit,
				"caster": player, "radius": float(skill.area), "trigger": float(skill.trigger)})
			_fx.rpc("disc", spot, Vector3.ZERO, skill.trigger, color.darkened(0.4), skill.duration)
		"fan":
			var n := Skills.count(skill, rank, "count")
			var spread := deg_to_rad(float(skill.angle))
			var hit := hit_for(player, skill, rank)
			for i in n:
				var t := 0.0 if n == 1 else float(i) / (n - 1) - 0.5
				var dir := aim.rotated(Vector3.UP, t * spread)
				_arena().spawn_projectile({
					"position": origin + Vector3.UP * Player.PROJECTILE_HEIGHT + dir * 0.6,
					"direction": dir, "speed": skill.speed, "range": skill.range, "radius": skill.radius,
					"pierce": 0, "damage": 0.0, "color": color, "hit": hit, "explode": 0.0,
				})
		"mark":
			var target := target_in_aim(player, skill.range)
			if target == null:
				return false
			Elements.apply_state(target.status, "marked", target.element, target.is_boss(),
				Skills.scaled(skill, "value", "per_rank", rank), skill.duration)
			_fx.rpc("beam", origin + Vector3.UP, target.global_position + Vector3.UP * 0.5, 0.08,
				Elements.state_color("marked"), 0.4)
		"teleport":
			var dest := _ray_limited(player, origin, origin + aim * float(skill.distance))
			_fx.rpc("disc", origin, Vector3.ZERO, 0.9, color, 0.3)
			player.teleport_to(dest)
			_fx.rpc("disc", dest, Vector3.ZERO, 0.9, color, 0.3)
		"delayed":
			var center := origin if skill.get("at", "aim") == "self" else _aim_point(player, skill.range)
			_delayed.append({"position": center, "time": float(skill.delay), "radius": float(skill.area),
				"hit": hit_for(player, skill, rank), "skill": skill, "rank": rank, "caster": player})
			_fx.rpc("disc", center, Vector3.ZERO, skill.area, color.darkened(0.3), skill.delay)
		"area":
			_start_area(player, skill, rank)
		"melee":
			melee_strike(player, hit_for(player, skill, rank), skill.range, skill.arc, false, int(skill.get("strikes", 1)))
		"shadow_step":
			var target := target_in_aim(player, skill.range)
			if target == null:
				return false
			var away := _flat(target.global_position - origin).normalized()
			var behind := target.global_position + Vector3(away.x, 0, away.y) * 1.2
			player.teleport_to(_ray_limited(player, target.global_position, behind))
			player.facing = -away
			player.add_buff("next_hit", Skills.scaled(skill, "value", "per_rank", rank), 3.0)
			_fx.rpc("disc", origin, Vector3.ZERO, 0.8, Color(0.2, 0.2, 0.25), 0.4)
		"smoke":
			var duration := Skills.scaled(skill, "duration", "duration_per_rank", rank)
			player.add_buff("hidden", 1.0, duration)
			_add_area(origin, skill.area, duration, {"damage": 0.0, "element": "", "state": "smoke"}, player)
			_fx.rpc("disc", origin, Vector3.ZERO, skill.area, Elements.state_color("smoke"), duration)
		"iron_body":
			var duration := Skills.scaled(skill, "duration", "duration_per_rank", rank)
			player.add_buff("iron_body", float(skill.value), duration)
			for e in enemies_in(origin, skill.area):
				e.taunt(player, duration)
			_fx.rpc("disc", origin, Vector3.ZERO, skill.area, Color(0.7, 0.7, 0.75), 0.5)
		"blink":
			var targets := enemies_in(origin, skill.range)
			if targets.is_empty():
				return false
			targets.sort_custom(func(a: Enemy, b: Enemy) -> bool:
				return a.global_position.distance_to(origin) < b.global_position.distance_to(origin))
			var max_targets := int(skill.targets)
			targets = targets.slice(0, max_targets)
			var hit := hit_for(player, skill, rank)
			if skill.get("power_total", false):
				hit.damage = float(hit.damage) / max_targets
			var from := origin
			for e in targets:
				if not is_instance_valid(e) or e.health <= 0.0:
					continue
				_fx.rpc("beam", from + Vector3.UP, e.global_position + Vector3.UP * 0.6, 0.15, color, 0.3)
				from = e.global_position
				player.teleport_to(_ray_limited(player, e.global_position, e.global_position - Vector3(aim.x, 0, aim.z)))
				_strike(player, e, hit)
				# Mil Cortes do Trovão: faíscas eletrizam os vizinhos.
				if skill.has("sparks"):
					for n in enemies_in(e.global_position, skill.sparks):
						Elements.apply_state(n.status, "shocked", n.element, n.is_boss())
		"dash_strike":
			var target := target_in_aim(player, skill.range)
			if target == null:
				return false
			_strike(player, target, hit_for(player, skill, rank))
			var through := _flat(target.global_position - origin).normalized()
			var dest := target.global_position + Vector3(through.x, 0, through.y) * 1.5
			_fx.rpc("beam", origin + Vector3.UP, dest + Vector3.UP, 0.2, color, 0.3)
			player.teleport_to(_ray_limited(player, target.global_position, dest))
		"summon":
			_summon(player, skill, rank)
		"charge":
			_charge(player, skill, rank)
		"taunt":
			var duration := Skills.scaled(skill, "duration", "duration_per_rank", rank)
			for e in enemies_in(origin, skill.area):
				e.taunt(player, duration)
			_fx.rpc("disc", origin, Vector3.ZERO, skill.area, Color(0.9, 0.75, 0.3), 0.5)
		"escape":
			var dest := _ray_limited(player, origin, origin + aim * float(skill.distance))
			_fx.rpc("disc", origin, Vector3.ZERO, 1.2, color, 0.4)
			player.teleport_to(dest)
			for comp in companions_of(player):
				comp.taunt_around(5.0, float(skill.taunt))
		"rescue":
			var best: Player = null
			var best_d := float(skill.range)
			for p: Player in get_tree().get_nodes_in_group(&"players"):
				var d := _flat(p.global_position - origin).length()
				if not p.alive and p.connected and d <= best_d:
					best = p
					best_d = d
			if best == null:
				return false
			best.revive(Skills.scaled(skill, "value", "per_rank", rank))
			_fx.rpc("beam", origin + Vector3.UP * 0.5, best.global_position + Vector3.UP * 0.5, 0.2, color, 0.5)
		_:
			return false
	return true


## Investida: atravessa uma linha acertando quem estiver nela; montado vai longe,
## a pé é um avanço curto com escudo que empurra. Os finais fazem 3 seguidas.
func _charge(player: Player, skill: Dictionary, rank: int) -> void:
	var mounted := player.mounted
	var length := float(skill.range) if mounted else float(skill.get("foot_range", 5.0))
	var charges := int(skill.get("charges", 1))
	var hit := hit_for(player, skill, rank)
	if skill.get("power_total", false):
		hit.damage = float(hit.damage) / charges
	if not mounted:
		hit.damage = float(hit.damage) * float(skill.get("foot_power_mult", 1.0))
		hit.erase("extra_state")  # a pé empurra em vez de derrubar
	var push := float(skill.get("push", 0.0 if mounted else skill.get("foot_push", 0.0)))
	var dir := Vector3(player.facing.x, 0, player.facing.y).normalized()
	var from := player.global_position
	var color := Elements.color(player.element)
	for i in charges:
		var to := _ray_limited(player, from, from + dir * length)
		for e in enemies_in(from, length + skill.width):
			if _distance_to_segment(e.global_position, from, to) <= float(skill.width) / 2.0:
				_strike(player, e, hit)
				if push > 0.0:
					e.push(dir * push, 0.25)
				# Carga da Tempestade: raios saltam para os vizinhos.
				if skill.has("sparks"):
					for n in enemies_in(e.global_position, skill.sparks):
						Elements.apply_state(n.status, "shocked", n.element, n.is_boss())
		_fx.rpc("beam", from + Vector3.UP * 0.5, to + Vector3.UP * 0.5, float(skill.width) * 0.6, color, 0.4)
		from = to
		dir = -dir
	player.teleport_to(from)


func companions_of(player: Player) -> Array[Companion]:
	var found: Array[Companion] = []
	for c: Companion in get_tree().get_nodes_in_group(&"companions"):
		if c.owner_peer == player.peer_id and not c.is_queued_for_deletion():
			found.append(c)
	return found


func companions_in(center: Vector3, radius: float) -> Array[Companion]:
	var found: Array[Companion] = []
	for c: Companion in get_tree().get_nodes_in_group(&"companions"):
		if not c.is_queued_for_deletion() and _flat(c.global_position - center).length() <= radius:
			found.append(c)
	return found


## Chama um animal amigo; acima do limite (por tipo ou 5 no total), o mais antigo vai embora.
func _summon(player: Player, skill: Dictionary, rank: int) -> void:
	var kind: String = skill.companion
	if kind == "element":
		kind = String(GameData.companions.by_element.get(player.element, "fox"))
	var mine := companions_of(player)
	var same := mine.filter(func(c: Companion) -> bool:
		return (c.kind == "bear") == (kind == "bear"))
	if same.size() >= Skills.count(skill, rank, "count"):
		same[0]._flee()
		mine.erase(same[0])
	if mine.size() >= int(GameData.companions.max_per_summoner):
		mine[0]._flee()
	var bond := player.character.passive_value("bond") if player.character else 0.0
	var side := Vector3(-player.facing.y, 0, player.facing.x) * (1.2 if mine.size() % 2 == 0 else -1.2)
	_arena().spawn_companion({
		"owner": player.peer_id, "kind": kind, "element": player.element,
		"position": player.global_position + side,
		"max_health": player.max_health * Skills.scaled(skill, "health", "health_per_rank", rank) * (1.0 + bond),
		"damage_fraction": Skills.power(skill, rank), "time": float(skill.get("duration", 0.0)),
	})
	_fx.rpc("disc", player.global_position + side, Vector3.ZERO, 0.8, Elements.color(player.element), 0.4)


## Cortes corpo a corpo: no inimigo à frente (dentro do arco) ou, girando, em
## todos em volta. Golpe pelas Costas: por trás é sempre crítico. Retorna quantos
## inimigos acertou.
func melee_strike(player: Player, hit: Dictionary, reach: float, arc_degrees: float, spin: bool, strikes := 1) -> int:
	var origin := player.global_position
	var targets: Array[Enemy] = []
	if spin:
		targets = enemies_in(origin, reach)
		_fx.rpc("disc", origin, Vector3.ZERO, reach, Elements.color(hit.get("element", "")), 0.25)
	else:
		var half := deg_to_rad(arc_degrees / 2.0)
		var best: Enemy = null
		var best_d := INF
		for e in enemies_in(origin, reach + 0.4):
			var to := _flat(e.global_position - origin)
			var d := to.length()
			if (d < 0.8 or absf(player.facing.angle_to(to)) <= half) and d < best_d:
				best = e
				best_d = d
		if best:
			targets.append(best)
			_fx.rpc("beam", origin + Vector3.UP, best.global_position + Vector3.UP * 0.6, 0.12,
				Elements.color(hit.get("element", "")), 0.15)
	for e in targets:
		for i in strikes:
			if is_instance_valid(e) and e.health > 0.0:
				_strike(player, e, hit)
	return targets.size()


## Um golpe de perto: Golpe pelas Costas (crítico garantido por trás) e Energia por crítico.
func _strike(player: Player, e: Enemy, hit: Dictionary) -> void:
	var h := hit.duplicate()
	var backstab := player.character.passive_value("backstab") if player.character else 0.0
	if backstab > 0.0 and e.is_behind(player.global_position):
		h.crit_chance = 1.0
		h.crit_mult = float(h.get("crit_mult", GameData.elements.crit_mult)) + backstab
	var result := e.take_hit(h)
	player.on_hit()
	if result.get("crit", false):
		player.on_crit()


func _add_area(at: Vector3, radius: float, time: float, hit: Dictionary, caster: Player) -> void:
	_areas.append({"position": at, "time": time, "tick": 0.0, "skill": {"area": radius, "shape": "circle"},
		"rank": 1, "caster": caster, "aim": Vector3.FORWARD, "inside": {}, "hit": hit})


## Golpe da habilidade para Elements.resolve_hit: dano = poder × % do rank ×
## bônus do herói (Bênção das Chamas, Domínio Elemental).
func hit_for(player: Player, skill: Dictionary, rank: int) -> Dictionary:
	var state := String(skill.get("state", ""))
	if skill.get("imbued", false):
		state = String(Elements.data(player.element).get("basic_state", ""))
	var hit := {
		"damage": player.power * Skills.power(skill, rank) * player.damage_mult(),
		"element": player.element,
		"state": state,
		"crit_chance": float(skill.get("crit_chance", player.character.crit_chance() if player.character else GameData.elements.crit_chance)),
		"crit_mult": player.character.crit_mult() if player.character else GameData.elements.crit_mult,
		"duration_mult": player.state_duration_mult(),
	}
	if skill.has("dot_mult"):
		hit.dot_mult = float(skill.dot_mult)
	if skill.has("extra_state"):
		hit.extra_state = String(skill.extra_state)
	player.consume_buff("next_hit")  # Passo Sombrio: só o próximo golpe
	if skill.has("state_chance"):
		hit.state_chance = float(skill.state_chance)
	if skill.has("state_duration"):
		hit.state_duration = Skills.scaled(skill, "state_duration", "state_duration_per_rank", rank)
	if skill.has("upgrade"):
		hit.upgrade = skill.upgrade
	return hit


## Bola de Fogo explodindo (chamado pelo projétil via arena).
func burst(at: Vector3, radius: float, hit: Dictionary) -> void:
	for e in enemies_in(at, radius):
		e.take_hit(hit)
	_fx.rpc("disc", at, Vector3.ZERO, radius, Elements.color(hit.get("element", "")), 0.35)


# --- Áreas que duram e golpes com atraso ------------------------------------------

func _start_area(player: Player, skill: Dictionary, rank: int) -> void:
	var aim := Vector3(player.facing.x, 0, player.facing.y).normalized()
	var at: String = skill.get("at", "aim")
	var center := player.global_position
	if skill.get("shape", "circle") == "wall":
		center = player.global_position + aim * float(skill.distance)
	elif at == "aim":
		center = _aim_point(player, skill.get("range", 10.0))
	var area := {"skill": skill, "rank": rank, "caster": player, "position": center, "aim": aim,
		"time": float(skill.duration), "tick": 0.0, "hit": hit_for(player, skill, rank),
		"inside": {}}
	if at == "moving":
		area.velocity = aim * float(skill.travel) / float(skill.duration)
	if skill.has("bolts_per_second"):
		# Raios: o dano é por raio; nas chuvas do Arqueiro, o total dividido pelos raios.
		area.bolts = 0.0
		if skill.get("power_total", false):
			area.hit.damage = float(area.hit.damage) / (float(skill.bolts_per_second) * float(skill.duration))
	elif skill.get("power_total", false):
		# Dano total da habilidade, dividido pelos tiques.
		area.hit.damage = float(area.hit.damage) * TICK / float(skill.duration)
	else:
		# Dano por segundo: cada tique (0,5 s) leva metade.
		area.hit.damage = float(area.hit.damage) * TICK
	_areas.append(area)
	var color := Elements.color(player.element)
	if skill.get("shape", "circle") == "wall":
		var side := Vector3(-aim.z, 0, aim.x) * float(skill.length) / 2.0
		_fx.rpc("beam", center - side, center + side, skill.width, color, skill.duration)
	elif at != "moving":
		_fx.rpc("disc", center, Vector3.ZERO, skill.area, color, skill.duration)


func _physics_process(delta: float) -> void:
	if not multiplayer.is_server():
		return
	for d in _delayed.duplicate():
		d.time -= delta
		if d.time > 0.0:
			continue
		_delayed.erase(d)
		for e in enemies_in(d.position, d.radius):
			e.take_hit(d.hit)
			if d.skill.has("push"):
				var away: Vector3 = e.global_position - d.position
				away.y = 0.0
				e.push(away.normalized() * float(d.skill.push), 0.3)
		_fx.rpc("disc", d.position, Vector3.ZERO, d.radius, Elements.color(d.hit.element).lightened(0.3), 0.3)
		# Meteoro: o chão fica em chamas.
		if d.skill.has("ground_duration") and is_instance_valid(d.caster):
			var ground := {"position": d.position, "time": float(d.skill.ground_duration), "tick": 0.0,
				"skill": {"area": d.radius, "shape": "circle"}, "rank": d.rank, "caster": d.caster,
				"aim": Vector3.FORWARD, "inside": {}, "hit": d.hit.duplicate()}
			ground.hit.damage = d.caster.power * float(d.skill.ground_power) * TICK * d.caster.damage_mult()
			_areas.append(ground)
			_fx.rpc("disc", d.position, Vector3.ZERO, d.radius, Elements.state_color("burning"), ground.time)
	for trap in _traps.duplicate():
		trap.time -= delta
		if trap.time <= 0.0:
			_traps.erase(trap)
			continue
		if enemies_in(trap.position, trap.trigger).is_empty():
			continue
		# Alguém pisou: dano em volta e preso no lugar.
		_traps.erase(trap)
		for e in enemies_in(trap.position, trap.radius):
			e.take_hit(trap.hit)
			Elements.apply_state(e.status, "rooted", e.element, e.is_boss(), 0.0, float(trap.hit.root))
		_fx.rpc("disc", trap.position, Vector3.ZERO, trap.radius, Elements.color(trap.hit.element), 0.4)
	for area in _areas.duplicate():
		area.time -= delta
		if area.has("velocity"):
			area.position += area.velocity * delta
		if area.time <= 0.0:
			_areas.erase(area)
			continue
		area.tick -= delta
		if area.tick > 0.0:
			continue
		area.tick = TICK
		_area_tick(area)


func _area_tick(area: Dictionary) -> void:
	var skill: Dictionary = area.skill
	var inside := _area_enemies(area)
	# Fogueira do Caçador: aliados perto ganham o bônus enquanto ficam ali.
	if skill.has("ally_buff") and is_instance_valid(area.caster):
		var value := Skills.scaled(skill, "value", "per_rank", area.rank)
		for p in allies_in(area.position, skill.area):
			p.add_buff(String(skill.ally_buff), value, TICK * 2.0)
	if skill.has("bolts_per_second"):
		# Tempestade / Saraivada: raios em inimigos ao acaso; os da Saraivada saltam.
		area.bolts += float(skill.bolts_per_second) * TICK
		while area.bolts >= 1.0 and not inside.is_empty():
			area.bolts -= 1.0
			var target: Enemy = inside[_rng.randi_range(0, inside.size() - 1)]
			var hits: Array[Enemy] = []
			var from := target.global_position + Vector3.UP * 8.0
			for jump in int(skill.get("bolt_jumps", 0)) + 1:
				target.take_hit(area.hit)
				hits.append(target)
				_fx.rpc("beam", from, target.global_position, 0.2, Elements.color(area.hit.element), 0.2)
				from = target.global_position + Vector3.UP * 0.5
				target = _nearest(target.global_position, 6.0, hits)
				if target == null:
					break
		return
	for e in inside:
		if float(area.hit.damage) > 0.0:
			e.take_hit(area.hit)
		elif area.hit.state != "":
			Elements.apply_state(e.status, area.hit.state, e.element, e.is_boss())
		# Nevasca: quem fica 3 s dentro congela.
		if skill.has("freeze_after"):
			var key := e.get_instance_id()
			area.inside[key] = float(area.inside.get(key, 0.0)) + TICK
			if area.inside[key] >= float(skill.freeze_after):
				area.inside[key] = 0.0
				Elements.apply_state(e.status, "frozen", e.element, e.is_boss())
		# Tornado: puxa para o centro.
		if skill.has("pull"):
			var to_center: Vector3 = area.position - e.global_position
			to_center.y = 0.0
			e.push(to_center.limit_length(float(skill.pull) * TICK), TICK)
	if area.has("velocity"):
		_fx.rpc("disc", area.position, Vector3.ZERO, skill.area, Elements.color(area.hit.element), TICK)
	# Chuva Restauradora: cura os aliados na área (por segundo, metade a cada tique).
	if skill.has("heal") and is_instance_valid(area.caster):
		var heal: float = area.caster.power * Skills.scaled(skill, "heal", "heal_per_rank", area.rank) * TICK
		for p in allies_in(area.position, skill.area):
			p.heal(heal)
		for comp in companions_in(area.position, skill.area):
			comp.heal(heal)


func _area_enemies(area: Dictionary) -> Array[Enemy]:
	var skill: Dictionary = area.skill
	if skill.get("shape", "circle") != "wall":
		return enemies_in(area.position, skill.area)
	var found: Array[Enemy] = []
	var aim: Vector3 = area.aim
	var side := Vector3(-aim.z, 0, aim.x)
	for e in enemies_in(area.position, skill.length):
		var rel: Vector3 = e.global_position - area.position
		if absf(rel.dot(side)) <= skill.length / 2.0 and absf(rel.dot(aim)) <= skill.width / 2.0:
			found.append(e)
	return found


# --- Alvos -------------------------------------------------------------------------

func enemies_in(center: Vector3, radius: float) -> Array[Enemy]:
	var found: Array[Enemy] = []
	for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
		if e.health > 0.0 and _flat(e.global_position - center).length() <= radius:
			found.append(e)
	return found


func allies_in(center: Vector3, radius: float) -> Array[Player]:
	var found: Array[Player] = []
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.alive and p.connected and _flat(p.global_position - center).length() <= radius:
			found.append(p)
	return found


## Inimigo mais perto no cone da mira; sem ninguém no cone, o mais perto ao alcance.
func target_in_aim(player: Player, max_range: float) -> Enemy:
	var aim := player.facing
	var best: Enemy = null
	var best_score := INF
	for e in enemies_in(player.global_position, max_range):
		var to := _flat(e.global_position - player.global_position)
		var score := to.length() + (0.0 if absf(aim.angle_to(to)) <= AIM_CONE else 1000.0)
		if score < best_score:
			best_score = score
			best = e
	return best


## Destino na linha de `from` a `to`, parando antes de uma parede.
func _ray_limited(player: Player, from: Vector3, to: Vector3) -> Vector3:
	var query := PhysicsRayQueryParameters3D.create(from + Vector3.UP, to + Vector3.UP, 1)
	var ray := player.get_world_3d().direct_space_state.intersect_ray(query)
	if ray.is_empty():
		return Vector3(to.x, 0, to.z)
	var back: Vector3 = (to - from).normalized() * 0.6
	return Vector3(ray.position.x, 0, ray.position.z) - Vector3(back.x, 0, back.z)


func _aim_point(player: Player, max_range: float) -> Vector3:
	var target := target_in_aim(player, max_range)
	if target and absf(player.facing.angle_to(_flat(target.global_position - player.global_position))) <= AIM_CONE:
		return target.global_position
	return player.global_position + Vector3(player.facing.x, 0, player.facing.y).normalized() * max_range * 0.5


func _nearest(from: Vector3, max_range: float, exclude: Array[Enemy]) -> Enemy:
	var best: Enemy = null
	var best_d := max_range
	for e in enemies_in(from, max_range):
		var d := _flat(e.global_position - from).length()
		if e not in exclude and d <= best_d:
			best = e
			best_d = d
	return best


static func _flat(v: Vector3) -> Vector2:
	return Vector2(v.x, v.z)


static func _distance_to_segment(p: Vector3, a: Vector3, b: Vector3) -> float:
	var closest := Geometry2D.get_closest_point_to_segment(_flat(p), _flat(a), _flat(b))
	return closest.distance_to(_flat(p))


# --- Visual (todos os PCs) ---------------------------------------------------------

## "disc": área no chão em `a` com raio; "beam": feixe de `a` a `b` com largura.
## O elemento vem da cor (fx.gd: partículas por elemento).
@rpc("authority", "call_local", "unreliable")
func _fx(kind: String, a: Vector3, b: Vector3, size: float, color: Color, duration: float) -> void:
	var element := Fx.element_for(color)
	if kind == "disc":
		Fx.burst(self, a, size, color, element, duration)
	else:
		Fx.beam(self, a, b, size, color, element, duration)
