# Southern Mercenaries — GPL-3.0-or-later
class_name Elements
extends RefCounted
## Regras dos elementos (02-0-elementos.md), sem nós: o ciclo de fraquezas
## (seção 3), o estado básico de cada elemento (5.3), a aplicação de estados
## com imunidades e chefes (6) e os combos (7). Os números ficam em
## data/elements.json. O servidor usa resolve_hit() para cada golpe de jogador.

const ALL: Array[String] = ["water", "fire", "air", "earth"]


static func data(id: String) -> Dictionary:
	return GameData.elements.elements.get(id, {})


static func state_data(id: String) -> Dictionary:
	return GameData.elements.states.get(id, {})


static func color(id: String) -> Color:
	var c: Array = data(id).get("color", [1, 1, 1])
	return Color(c[0], c[1], c[2])


static func state_color(id: String) -> Color:
	var c: Array = state_data(id).get("color", [1, 1, 1])
	return Color(c[0], c[1], c[2])


## x1,5 se o elemento do golpe vence o do alvo, x0,5 se é o mesmo, x1 nos outros.
static func multiplier(attack: String, target: String) -> float:
	if attack == "" or target == "":
		return 1.0
	if attack == target:
		return GameData.elements.resist_mult
	if data(attack).get("beats", "") == target:
		return GameData.elements.weakness_mult
	return 1.0


## Elemento que vence `target` (o que a história conta como fraqueza).
static func weakness_of(target: String) -> String:
	for id: String in GameData.elements.elements:
		if data(id).beats == target:
			return id
	return ""


## Aplica um estado respeitando as regras: monstros de Fogo não queimam, de
## Água não ficam molhados; chefes trocam controle por lentidão.
## Retorna o estado que ficou (ou "").
static func apply_state(status: StatusSet, id: String, target_element: String, is_boss: bool,
		dps := 0.0, duration := -1.0) -> String:
	var def := state_data(id)
	if def.is_empty() or target_element in def.get("immune", []):
		return ""
	if is_boss and def.get("control", false):
		id = "slowed"
		def = state_data(id)
		duration = -1.0
	status.apply(id, def.duration if duration < 0.0 else duration, dps)
	return id


## Resolve um golpe de jogador num alvo e já muda os estados dele.
## hit: {damage, element, state ("" ou o estado básico), crit_chance}
## Retorna {damage, crit, effect ("weak"/"resist"/"normal"), combo, spread_dps,
## zone ({state, radius, duration} ou {})}. O chamador aplica o dano, espalha o
## fogo do Incêndio e cria a área da Lama/Vapor.
static func resolve_hit(hit: Dictionary, target_element: String, status: StatusSet, is_boss: bool,
		rng: RandomNumberGenerator) -> Dictionary:
	var rules: Dictionary = GameData.elements
	var element: String = hit.get("element", "")
	var mult := multiplier(element, target_element)
	var result := {"crit": false, "combo": "", "spread_dps": 0.0, "zone": {},
		"effect": "weak" if mult > 1.0 else ("resist" if mult < 1.0 else "normal")}
	# Combo: o estado de outro golpe (de qualquer jogador) + este elemento. Consome o estado.
	var bonus := 0.0
	var stun := 0.0
	for id: String in rules.combos:
		var combo: Dictionary = rules.combos[id]
		if combo.element == element and status.has(combo.needs):
			result.combo = id
			if combo.needs == "burning":
				result.spread_dps = status.dps("burning")
			status.remove(combo.needs)
			bonus += float(combo.get("damage_bonus", 0.0))
			stun = float(combo.get("stun", 0.0))
			if combo.has("zone_state"):
				result.zone = {"state": combo.zone_state, "radius": combo.radius, "duration": combo.zone_duration}
			break
	# Eletrizado: +15% de dano de Ar.
	if status.has("shocked") and element == state_data("shocked").get("bonus_element", ""):
		bonus += float(state_data("shocked").bonus)
	var crit_chance := float(hit.get("crit_chance", rules.crit_chance))
	if status.has("frozen") or rng.randf() < crit_chance:
		result.crit = true
	var damage := float(hit.damage) * mult * (1.0 + bonus) * (rules.crit_mult if result.crit else 1.0)
	result.damage = damage
	# Estados depois do dano: o do golpe (forte) e o atordoamento do Eletrocutar.
	var state: String = hit.get("state", "")
	if state != "":
		var chance := float(data(element).get("basic_state_chance", 1.0)) if state == data(element).get("basic_state", "") else 1.0
		if rng.randf() < chance:
			var dps := damage * float(state_data(state).get("dot_fraction", 0.0))
			apply_state(status, state, target_element, is_boss, dps)
	if stun > 0.0:
		apply_state(status, "stunned", target_element, is_boss, 0.0, stun)
	return result
