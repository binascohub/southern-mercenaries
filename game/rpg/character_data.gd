# Southern Mercenaries — GPL-3.0-or-later
class_name CharacterData
extends RefCounted
## Ficha do personagem: o mesmo dicionário vai no save do PC do dono
## (11-saves.md) e na rede, onde a cópia do servidor é a verdade durante a
## partida (07-rede.md, seção 8). Só IDs e números, nunca texto traduzido.

const SLOTS: Array[String] = ["weapon", "head", "body", "hands", "feet", "ring_1", "ring_2", "amulet"]
const ATTRIBUTES: Array[String] = ["str", "dex", "int", "vit"]
const SEXES: Array[String] = ["male", "female"]
const NAME_MAX := 24
## Sal do resumo da ficha (anti-trapaça leve entre amigos; o código é aberto).
const CHECK_SALT := "southern-mercenaries/character"

var data: Dictionary


static func create(class_id: String, sex: String, hero_name: String, element := "fire") -> CharacterData:
	var c := CharacterData.new()
	var cls := GameData.get_class_data(class_id)
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var equipment := {}
	for slot in SLOTS:
		equipment[slot] = null
	var inventory := []
	inventory.resize(GameData.balance.inventory_size)
	c.data = {
		"save_version": GameData.balance.save_version,
		"id": Items.new_uid(rng),
		"name": clean_name(hero_name),
		"class_id": class_id,
		"sex": sex if sex in SEXES else "male",
		# Elemento de origem (não muda) e o da Poção Elemental ativa ("" = nenhuma).
		"element": element if element in Elements.ALL else "fire",
		"element_potion": "",
		# Habilidades por chave (Skills): a de nível 1 vem no rank 1 e no atalho 1.
		"skills": {Skills.keys(class_id)[0]: 1},
		"skill_slots": [Skills.keys(class_id)[0], "", "", ""],
		"level": 1,
		"xp": 0,
		"attributes": cls.attributes.duplicate(),
		"free_points": 0,
		"skill_points": 0,
		"gold": 0,
		"equipment": equipment,
		"inventory": inventory,
		"created": Time.get_datetime_string_from_system(true),
		"played_seconds": 0,
	}
	var kit: Dictionary = cls.get("starting_kit", {})
	for slot in kit.get("equipment", {}):
		var e: Dictionary = kit.equipment[slot]
		equipment[slot] = Items.equipment(e.base, e.material, "common", 1, {}, rng)
	for entry in kit.get("items", []):
		c.add_item(Items.stack(Items.CONSUMABLE, entry.id, int(entry.count)))
	c.data.gold = int(kit.get("gold", 0))
	c.seal()
	return c


## Lê um dicionário (save ou rede). Retorna null se for inválido.
static func from_dict(source: Variant) -> CharacterData:
	if not source is Dictionary:
		return null
	var c := CharacterData.new()
	# Ficha legítima antes da migração continua legítima depois (os campos novos
	# mudam o resumo, mas não foram editados à mão).
	var before := CharacterData.new()
	before.data = source.duplicate(true)
	var was_sealed := before.data.has("check") and not before.is_edited()
	# O JSON devolve todo número como float: inteiros voltam a ser int ("Nível 2", não "2.0").
	c.data = _canonical(SaveSystem.migrate_character(source.duplicate(true)))
	if was_sealed:
		c.seal()
	return c if c.validate().is_empty() else null


func to_dict() -> Dictionary:
	return data.duplicate(true)


func class_data() -> Dictionary:
	return GameData.get_class_data(data.class_id)


## Problemas encontrados (vazio = válido). O servidor recusa personagens
## inválidos na entrada (07-rede.md, seção 3).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if not GameData.classes.has(data.get("class_id", "")):
		return PackedStringArray(["classe"])
	for key in ["id", "name", "level", "xp", "attributes", "free_points", "gold", "equipment", "inventory"]:
		if not data.has(key):
			errors.append("faltando " + key)
	if not errors.is_empty():
		return errors
	if data.get("element", "") not in Elements.ALL:
		errors.append("elemento")
	if data.get("element_potion", "") != "" and data.element_potion not in Elements.ALL:
		errors.append("poção elemental")
	errors.append_array(_validate_skills())
	if int(data.level) < 1 or int(data.level) > GameData.balance.max_level:
		errors.append("nível")
	if int(data.gold) < 0 or int(data.xp) < 0 or int(data.free_points) < 0:
		errors.append("valores negativos")
	var start: Dictionary = class_data().attributes
	var spent := 0
	for attr in ATTRIBUTES:
		var value := int(data.attributes.get(attr, -1))
		if value < int(start[attr]):
			errors.append("atributo " + attr)
		spent += value - int(start[attr])
	if spent + int(data.free_points) > GameData.balance.attribute_points_per_level * (int(data.level) - 1):
		errors.append("pontos de atributo demais")
	if data.inventory.size() > GameData.balance.inventory_size:
		errors.append("bolsa grande demais")
	for item in data.inventory:
		if item != null and not Items.is_valid(item):
			errors.append("item inválido na bolsa")
	for slot in SLOTS:
		var item: Variant = data.equipment.get(slot)
		if item != null and (not Items.is_valid(item) or item.kind != Items.EQUIPMENT):
			errors.append("item inválido em " + slot)
	return errors


static func clean_name(text: String) -> String:
	var name := text.strip_edges().replace("\n", " ").substr(0, NAME_MAX)
	return name if name != "" else "?"


# --- Resumo da ficha (11-saves.md, seção 5: detecta arquivo editado, só avisa) -------

## Resumo do conteúdo da ficha (sem o próprio campo "check").
func checksum() -> String:
	var copy := data.duplicate(true)
	copy.erase("check")
	var text := JSON.stringify(_canonical(copy), "", true)
	return (CHECK_SALT + text).sha256_text().left(32)


## Grava o resumo atual. O jogo sela a ficha sempre que ela muda por meios
## legítimos (criação, save, mudança vinda do servidor).
func seal() -> void:
	data.check = checksum()


## A ficha foi mudada fora do jogo (o resumo não bate). Fichas antigas, sem
## resumo, não são acusadas.
func is_edited() -> bool:
	return data.has("check") and str(data.check) != checksum()


## Números inteiros iguais venham do JSON (float) ou da memória (int).
static func _canonical(value: Variant) -> Variant:
	if value is Dictionary:
		var out := {}
		for key in value:
			out[str(key)] = _canonical(value[key])
		return out
	if value is Array:
		var items := []
		for v in value:
			items.append(_canonical(v))
		return items
	if value is float and is_finite(value) and value == floorf(value):
		return int(value)
	return value


# --- Progressão (13-balanceamento.md) ----------------------------------------------

static func xp_to_next(level: int) -> int:
	return int(GameData.balance.xp_per_level_factor) * level


## Soma XP; retorna quantos níveis subiu (nível máximo 20).
func add_xp(amount: int) -> int:
	var gained := 0
	data.xp = int(data.xp) + maxi(amount, 0)
	while int(data.level) < GameData.balance.max_level and int(data.xp) >= xp_to_next(int(data.level)):
		data.xp = int(data.xp) - xp_to_next(int(data.level))
		data.level = int(data.level) + 1
		# Números do JSON chegam como float: a ficha guarda inteiros ("5", não "5.0").
		data.free_points = int(data.free_points) + int(GameData.balance.attribute_points_per_level)
		data.skill_points = int(data.skill_points) + int(GameData.balance.skill_points_per_level)
		gained += 1
	if int(data.level) >= GameData.balance.max_level:
		data.xp = 0
	return gained


func spend_point(attr: String) -> bool:
	if attr not in ATTRIBUTES or int(data.free_points) <= 0:
		return false
	data.attributes[attr] = int(data.attributes[attr]) + 1
	data.free_points = int(data.free_points) - 1
	return true


# --- Estatísticas derivadas ---------------------------------------------------------

func equipped() -> Array[Dictionary]:
	var items: Array[Dictionary] = []
	for slot in SLOTS:
		if data.equipment.get(slot) != null:
			items.append(data.equipment[slot])
	return items


func affix_total(id: String) -> float:
	var total := 0.0
	for item in equipped():
		total += float(item.affixes.get(id, 0))
	return total


func attribute(attr: String) -> int:
	return int(data.attributes[attr]) + int(affix_total(attr))


## Vida = inicial + (nível − 1) × por nível + 5 × (VIT − VIT inicial) + afixos (13-balanceamento.md 2.2).
func max_health() -> float:
	var cls := class_data()
	return cls.max_health + (int(data.level) - 1) * cls.health_per_level \
		+ 5.0 * (attribute("vit") - int(cls.attributes.vit)) + affix_total("life")


func max_resource() -> float:
	var cls := class_data()
	var attr: String = cls.power_attribute
	return cls.max_resource + cls.resource_per_power_point * (attribute(attr) - int(cls.attributes[attr])) \
		+ affix_total("resource")


func resource_regen() -> float:
	var cls := class_data()
	var attr: String = cls.power_attribute
	return (cls.resource_regen + cls.regen_per_power_point * (attribute(attr) - int(cls.attributes[attr]))) \
		* (1.0 + passive_value("regen"))


func weapon_damage() -> float:
	var weapon: Variant = data.equipment.get("weapon")
	return Items.weapon_damage(weapon) if weapon != null else 0.0


## Poder da classe = dano da arma + atributo principal × 0,5 (02-personagens.md).
func power() -> float:
	return weapon_damage() + attribute(class_data().power_attribute) * GameData.balance.power_attribute_factor


func armor() -> float:
	var total := 0.0
	for item in equipped():
		total += Items.armor(item, class_data().armor_factor)
	return total


## Redução de dano contra um monstro de um nível (13-balanceamento.md 2.3).
func damage_reduction(monster_level: int) -> float:
	var a := armor()
	var b: Dictionary = GameData.balance
	return minf(a / (a + b.armor_base_constant + b.armor_base_per_monster_level * monster_level),
		b.max_damage_reduction)


# --- Habilidades (02-personagens.md, "Progressão") -----------------------------------

func _validate_skills() -> PackedStringArray:
	var errors := PackedStringArray()
	var skills: Variant = data.get("skills", {})
	var slots: Variant = data.get("skill_slots", [])
	if not skills is Dictionary or not slots is Array or slots.size() != int(GameData.skills.slots):
		return PackedStringArray(["habilidades"])
	var keys := Skills.keys(data.class_id)
	var spent := 0
	for key: String in skills:
		var rank := int(skills[key])
		if key not in keys or rank < 1 or rank > Skills.max_rank() \
				or Skills.unlock_level(data.class_id, key) > int(data.level):
			errors.append("habilidade " + key)
		spent += rank
	# O rank 1 da habilidade de nível 1 vem de graça; o resto sai dos pontos (+1 por nível).
	var earned := int(GameData.balance.skill_points_per_level) * (int(data.level) - 1) + 1
	if spent + int(data.get("skill_points", 0)) > earned:
		errors.append("pontos de habilidade demais")
	for key: Variant in slots:
		if key != "" and (not skills.has(key) or not Skills.is_active(skill_of(key))):
			errors.append("atalho " + str(key))
	return errors


func skill_rank(key: String) -> int:
	return int(data.get("skills", {}).get(key, 0))


## ID da habilidade da chave no elemento em uso (a Poção Elemental troca as do elemento).
func skill_of(key: String) -> String:
	return Skills.skill_id(data.class_id, key, current_element())


func can_learn(key: String) -> bool:
	return key in Skills.keys(data.class_id) and int(data.get("skill_points", 0)) > 0 \
		and skill_rank(key) < Skills.max_rank() and Skills.unlock_level(data.class_id, key) <= int(data.level)


## Gasta um ponto de habilidade: aprende (rank 1) ou sobe o rank.
func learn(key: String) -> bool:
	if not can_learn(key):
		return false
	data.skills[key] = skill_rank(key) + 1
	data.skill_points = int(data.skill_points) - 1
	# Habilidade ativa nova vai para o primeiro atalho livre.
	if skill_rank(key) == 1 and Skills.is_active(skill_of(key)) and key not in data.skill_slots:
		var free: int = data.skill_slots.find("")
		if free >= 0:
			data.skill_slots[free] = key
	return true


## Põe uma habilidade ativa aprendida num atalho (tira de outro, se estava lá).
func set_slot(index: int, key: String) -> bool:
	if index < 0 or index >= data.skill_slots.size():
		return false
	if key != "" and (skill_rank(key) == 0 or not Skills.is_active(skill_of(key))):
		return false
	var old: int = data.skill_slots.find(key)
	if key != "" and old >= 0:
		data.skill_slots[old] = data.skill_slots[index]
	data.skill_slots[index] = key
	return true


## Soma de uma passiva aprendida (0 se não tiver): ex. "regen" do Mente Afiada.
func passive_value(effect: String, field := "value", per_rank := "per_rank") -> float:
	for key: String in data.get("skills", {}):
		var skill := Skills.def(skill_of(key))
		if skill.get("kind", "") == "passive" and skill.get("effect", "") == effect:
			return Skills.scaled(skill, field, per_rank, skill_rank(key))
	return 0.0


# --- Elemento (02-0-elementos.md) ---------------------------------------------------

## Elemento em uso: o da Poção Elemental, se houver, senão o de origem.
func current_element() -> String:
	var potion: String = data.get("element_potion", "")
	return potion if potion != "" else String(data.get("element", "fire"))


## Bebeu uma Poção Elemental: passa a usar outro elemento até voltar a Tortuga.
## Uma poção ativa por vez; a do próprio elemento de origem desfaz a troca.
func drink_elemental(element: String) -> bool:
	if element not in Elements.ALL or element == current_element():
		return false
	data.element_potion = "" if element == data.element else element
	return true


## Voltou a Tortuga: a expedição acabou e o efeito da poção também (seção 4).
func end_expedition() -> void:
	data.element_potion = ""


## Crítico: 5% de base + afixos (13-balanceamento.md 2.1) + Olho de Águia.
func crit_chance() -> float:
	return GameData.elements.crit_chance + affix_total("crit") / 100.0 + passive_value("eagle_eye")


## Dano do crítico: x1,5 + Olho de Águia (+10% por rank).
func crit_mult() -> float:
	return GameData.elements.crit_mult + passive_value("eagle_eye", "crit_damage_value", "crit_damage_per_rank")


func move_speed_bonus() -> float:
	return affix_total("move_speed") / 100.0


func gold_find_bonus() -> float:
	return affix_total("gold_find") / 100.0


# --- Bolsa e equipamento ---------------------------------------------------------

func free_slots() -> int:
	return data.inventory.count(null)


## Põe na bolsa, empilhando quando dá. Retorna false se não couber tudo.
func add_item(item: Dictionary) -> bool:
	if item.kind != Items.EQUIPMENT:
		var left := int(item.count)
		for i in data.inventory.size():
			var slot: Variant = data.inventory[i]
			if slot != null and slot.kind == item.kind and slot.id == item.id:
				var room := Items.max_stack(slot) - int(slot.count)
				var moved := mini(room, left)
				slot.count = int(slot.count) + moved
				left -= moved
				if left == 0:
					return true
		while left > 0:
			var free: int = data.inventory.find(null)
			if free < 0:
				item.count = left
				return false
			var moved := mini(Items.max_stack(item), left)
			data.inventory[free] = Items.stack(item.kind, item.id, moved)
			left -= moved
		return true
	var index: int = data.inventory.find(null)
	if index < 0:
		return false
	data.inventory[index] = item
	return true


func count_of(id: String) -> int:
	var total := 0
	for item in data.inventory:
		if item != null and item.kind != Items.EQUIPMENT and item.id == id:
			total += int(item.count)
	return total


## Tira uma unidade de um empilhável; retorna false se não tiver.
func take_one(id: String) -> bool:
	for i in range(data.inventory.size() - 1, -1, -1):
		var item: Variant = data.inventory[i]
		if item != null and item.kind != Items.EQUIPMENT and item.id == id:
			item.count = int(item.count) - 1
			if int(item.count) <= 0:
				data.inventory[i] = null
			return true
	return false


func can_equip(item: Dictionary) -> bool:
	return item.kind == Items.EQUIPMENT and Items.usable_by_class(item, data.class_id) \
		and int(data.level) >= Items.required_level(item)


## Equipa o item da bolsa; o que estava no slot volta para o mesmo espaço.
func equip_from_bag(index: int) -> bool:
	if index < 0 or index >= data.inventory.size() or data.inventory[index] == null:
		return false
	var item: Dictionary = data.inventory[index]
	if not can_equip(item):
		return false
	var slot := Items.slot_of(item)
	if slot == "ring":
		slot = "ring_1" if data.equipment.ring_1 == null or data.equipment.ring_2 != null else "ring_2"
	data.inventory[index] = data.equipment[slot]
	data.equipment[slot] = item
	return true


func unequip(slot: String) -> bool:
	if slot not in SLOTS or data.equipment.get(slot) == null:
		return false
	var index: int = data.inventory.find(null)
	if index < 0:
		return false
	data.inventory[index] = data.equipment[slot]
	data.equipment[slot] = null
	return true


## Material de cada peça visível, para os outros jogadores verem (02-personagens.md).
func equipment_visual() -> Dictionary:
	var visual := {}
	for slot in ["weapon", "head", "body", "hands", "feet"]:
		var item: Variant = data.equipment.get(slot)
		if item != null:
			visual[slot] = item.material
	return visual
