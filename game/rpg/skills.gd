# Southern Mercenaries — GPL-3.0-or-later
class_name Skills
extends RefCounted
## Regras das habilidades (02-personagens.md, "Progressão" e "Habilidades";
## 02-1-mago.md, seção 6), sem nós. Os dados ficam em data/skills.json.
##
## A ficha guarda as habilidades por "chave": as de classe pelo próprio ID
## (`teleport`) e as do elemento pelo nível em que liberam (`element_6`). Assim,
## ao beber uma Poção Elemental, a habilidade de nível 6 do elemento de origem
## vira a de nível 6 do novo elemento com o mesmo rank (02-0-elementos.md, seção 4).

const ELEMENT_PREFIX := "element_"


static func class_def(class_id: String) -> Dictionary:
	return GameData.skills.classes.get(class_id, {})


static func def(skill_id: String) -> Dictionary:
	return GameData.skills.skills.get(skill_id, {})


static func max_rank() -> int:
	return int(GameData.skills.max_rank)


## As 10 chaves da classe, na ordem dos níveis em que liberam.
static func keys(class_id: String) -> Array[String]:
	var found: Array[String] = []
	var cls := class_def(class_id)
	for key: String in cls.get("class", {}):
		found.append(key)
	for level in cls.get("element_levels", []):
		found.append(ELEMENT_PREFIX + str(int(level)))
	found.sort_custom(func(a: String, b: String) -> bool:
		return unlock_level(class_id, a) < unlock_level(class_id, b))
	return found


static func unlock_level(class_id: String, key: String) -> int:
	if key.begins_with(ELEMENT_PREFIX):
		return int(key.trim_prefix(ELEMENT_PREFIX))
	return int(class_def(class_id).get("class", {}).get(key, 99))


static func is_element_key(key: String) -> bool:
	return key.begins_with(ELEMENT_PREFIX)


## ID da habilidade de uma chave no elemento atual.
static func skill_id(class_id: String, key: String, element: String) -> String:
	if not is_element_key(key):
		return key if class_def(class_id).get("class", {}).has(key) else ""
	var cls := class_def(class_id)
	var levels: Array = cls.get("element_levels", [])
	var i := levels.find(float(unlock_level(class_id, key)))
	if i < 0:
		i = levels.find(unlock_level(class_id, key))
	var table: Array = cls.get("element", {}).get(element, [])
	return String(table[i]) if i >= 0 and i < table.size() else ""


static func is_active(skill_id: String) -> bool:
	return def(skill_id).get("kind", "") == "active"


## Valor que cresce por rank: base + por_rank × (rank − 1).
static func scaled(skill: Dictionary, field: String, per_rank_field: String, rank: int) -> float:
	return float(skill.get(field, 0.0)) + float(skill.get(per_rank_field, 0.0)) * maxi(rank - 1, 0)


static func power(skill: Dictionary, rank: int) -> float:
	return scaled(skill, "power", "per_rank", rank)


static func cooldown(skill: Dictionary, rank: int) -> float:
	return maxf(scaled(skill, "cooldown", "cooldown_per_rank", rank), 0.0)


## Saltos da Corrente de Raios: 5, +1 nos ranks 3 e 5.
static func jumps(skill: Dictionary, rank: int) -> int:
	var n := int(skill.get("jumps", 0))
	for r in skill.get("jumps_at_ranks", []):
		if rank >= int(r):
			n += 1
	return n
