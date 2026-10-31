# Southern Mercenaries — GPL-3.0-or-later
class_name SideQuests
extends RefCounted
## Visitantes da Taverna e missões secundárias (04-tortuga-e-missoes.md,
## seções 3 e 4), sem nós. A cada volta para Tortuga chegam 2 a 4 visitantes;
## cada um conta uma história (modelo + criatura do bestiário + lugar) que vira
## uma missão: caçada (matar N criaturas), rumor (ir a um lugar: tesouro,
## emboscada ou nada) ou recuperar (achar uma carga perdida). Ficam na campanha
## do host; no máximo 5 ativas. Cada história segue o roteiro dos docs: o que é,
## a lenda da criatura, a recompensa e a pista de fraqueza.

## Mapas com missões secundárias: os já liberados (por enquanto, o Esgoto provisório).
static func open_maps(unlocked: Array) -> Array[String]:
	var maps: Array[String] = []
	if "sewer_entrance" in unlocked:
		maps.append("prototype_arena")
	return maps


## Criaturas do bestiário que existem de verdade no mapa (para caçar e contar história).
static func creatures_in(map_id: String) -> Array[String]:
	var found: Array[String] = []
	for id: String in GameData.bestiary:
		var entry: Dictionary = GameData.bestiary[id]
		if entry.get("map", "") == map_id and not entry.get("monsters", []).is_empty():
			found.append(id)
	return found


## Novos visitantes (vazio se nenhum mapa está liberado).
static func generate_visitors(campaign: Dictionary, rng: RandomNumberGenerator) -> Array:
	var maps := open_maps(campaign.get("unlocked", []))
	if maps.is_empty():
		return []
	var rules: Dictionary = GameData.visitors
	var count := rng.randi_range(int(rules.per_return[0]), mini(int(rules.per_return[1]), rules.seats.size()))
	var names: Array = rules.names.duplicate()
	var types: Array = rules.types.keys()
	var day := int(campaign.get("ship", {}).get("day", 0))
	var visitors := []
	for i in count:
		var type: String = types[rng.randi_range(0, types.size() - 1)]
		var name: String = names.pop_at(rng.randi_range(0, names.size() - 1))
		var templates: Array = rules.types[type].templates
		var template: String = templates[rng.randi_range(0, templates.size() - 1)]
		var map_id: String = maps[rng.randi_range(0, maps.size() - 1)]
		visitors.append({"type": type, "name": name,
			"quest": make_quest("sq_%d_%d" % [day, i], template, map_id, rng)})
	return visitors


static func make_quest(id: String, template: String, map_id: String, rng: RandomNumberGenerator) -> Dictionary:
	var rules: Dictionary = GameData.visitors.quest_templates[template]
	var creatures := creatures_in(map_id)
	var level := int(GameData.arenas[map_id].get("area_level", 1))
	var quest := {"id": id, "template": template, "area": map_id, "status": "offered",
		"target": creatures[rng.randi_range(0, creatures.size() - 1)] if not creatures.is_empty() else "",
		"gold": int(rules.gold_per_level) * level, "xp": int(rules.xp_per_level) * level}
	match template:
		"hunt":
			quest.count = rng.randi_range(int(rules.count[0]), int(rules.count[1]))
			quest.progress = 0
			quest.gold = int(quest.gold) * int(quest.count) / 4
		"rumor", "retrieve":
			var spots: Array = GameData.arenas[map_id].get("quest_spots", [[0, 0]])
			quest.spot = rng.randi_range(0, spots.size() - 1)
			if template == "rumor":
				quest.outcome = Items.roll_rarity(rules.outcomes, rng)  # sorteio por peso
	return quest


## Missões ativas agora.
static func active(side_quests: Dictionary) -> Array:
	return side_quests.values().filter(func(q: Dictionary) -> bool: return q.status == "active")


## Falas do visitante: o que é (com recompensa), a lenda da criatura e a pista.
static func visitor_lines(visitor: Dictionary) -> Array:
	var quest: Dictionary = visitor.quest
	var entry: Dictionary = GameData.bestiary.get(quest.target, {})
	var args := {"target": entry.get("name_key", ""), "area": GameData.arenas[quest.area].get("name_key", ""),
		"gold": quest.gold, "count": quest.get("count", 0)}
	var intro: String = GameData.visitors.quest_templates[quest.template].intro_key
	var lines := [[intro, args]]
	if not entry.is_empty():
		lines.append([entry.legend_key, {}])
		lines.append([entry.hint_key, {}])
	return lines


## Título da missão no diário.
static func title(quest: Dictionary) -> String:
	var entry: Dictionary = GameData.bestiary.get(quest.target, {})
	var t := TranslationServer
	var key := "VQ_%s_TITLE" % String(quest.template).to_upper()
	var text := str(t.translate(key)).format({"target": str(t.translate(entry.get("name_key", ""))),
		"area": str(t.translate(GameData.arenas[quest.area].get("name_key", ""))), "count": quest.get("count", 0)})
	if quest.template == "hunt" and quest.status == "active":
		text += "  (%d/%d)" % [int(quest.progress), int(quest.count)]
	return text
