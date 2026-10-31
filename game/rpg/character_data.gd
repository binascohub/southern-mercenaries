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

var data: Dictionary


static func create(class_id: String, sex: String, hero_name: String) -> CharacterData:
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
	return c


## Lê um dicionário (save ou rede). Retorna null se for inválido.
static func from_dict(source: Variant) -> CharacterData:
	if not source is Dictionary:
		return null
	var c := CharacterData.new()
	c.data = SaveSystem.migrate_character(source.duplicate(true))
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
		data.free_points = int(data.free_points) + GameData.balance.attribute_points_per_level
		data.skill_points = int(data.skill_points) + GameData.balance.skill_points_per_level
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
	return cls.resource_regen + cls.regen_per_power_point * (attribute(attr) - int(cls.attributes[attr]))


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
