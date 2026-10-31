# Southern Mercenaries — GPL-3.0-or-later
class_name Town
extends Node
## A cidade (04-tortuga-e-missoes.md): missões, lojas e conversas com os NPCs.
## O servidor guarda tudo na campanha do host (missões, o que já abriu, o navio
## do dia) e manda uma cópia para todos os PCs (marcas "!" nos NPCs, diário no
## HUD, estoque das lojas). As janelas abrem só no PC de quem interagiu;
## compras, vendas e missões aceitas são validadas no servidor.
##
## Fica como filho da arena, com o mesmo nome em todos os PCs (as RPCs usam o caminho).

signal state_changed
signal shop_opened(shop_id: String)
signal dialogue_opened(npc_id: String, index: int)
signal training_opened
signal portals_opened
signal stash_opened
signal bestiary_opened
signal forge_opened
## Conversa montada (visitantes): nome, falas [[chave, args]], índice do visitante.
signal visitor_opened(name: String, lines: Array, visitor_index: int)
## Abertura na Taverna: os heróis dos jogadores ([{name, class_id, sex}], ver Opening).
signal opening_started(players: Array)

const REACH := 4.0

## Cópia em todos os PCs.
var quests := {}
var unlocked: Array = []
var ship := {}
## Checkpoints já alcançados nos mapas ("area:checkpoint"), para o Macumbeiro.
var reached: Array = []
## Visitantes da taverna, missões secundárias e bestiário do grupo.
var visitors: Array = []
var side_quests := {}
var bestiary: Array = []
## Relíquias dos chefes já conquistadas pelo grupo.
var relics: Array = []


func _arena() -> Node:
	return get_parent()


func _campaign() -> Dictionary:
	return _arena()._campaign


# --- Estado (servidor -> todos) --------------------------------------------------

func sync(peer_id := 0) -> void:
	var c := _campaign()
	var args := [c.get("quests", {}), c.get("unlocked", []), c.get("ship", {}), c.get("checkpoints_reached", []),
		c.get("visitors", []), c.get("side_quests", {}), c.get("bestiary", []), c.get("relics", [])]
	if peer_id == 0:
		rpc.callv([&"_set_state"] + args)
	else:
		rpc_id.callv([peer_id, &"_set_state"] + args)


@rpc("authority", "call_local", "reliable")
func _set_state(new_quests: Dictionary, new_unlocked: Array, new_ship: Dictionary, new_reached: Array,
		new_visitors: Array, new_side: Dictionary, new_bestiary: Array, new_relics: Array) -> void:
	quests = new_quests
	unlocked = new_unlocked
	ship = new_ship
	reached = new_reached
	visitors = new_visitors
	side_quests = new_side
	bestiary = new_bestiary
	relics = new_relics
	state_changed.emit()


## Abertura na Taverna (06-mundo-e-historia.md, seção 5): quem está na Taverna
## antes de aceitar a primeira missão ouve as histórias dos heróis. Servidor.
func send_opening(peer_id: int) -> void:
	if not multiplayer.is_server() or _arena().area_id != "tavern" \
			or _campaign().get("quests", {}).has(GameData.opening.quest):
		return
	var heroes := []
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.character:
			heroes.append({"name": p.hero_name, "class_id": String(p.character.data.class_id),
				"sex": String(p.character.data.sex)})
	if peer_id == multiplayer.get_unique_id():
		_rpc_opening(heroes)
	elif peer_id in multiplayer.get_peers():
		_rpc_opening.rpc_id(peer_id, heroes)


@rpc("authority", "reliable")
func _rpc_opening(heroes: Array) -> void:
	opening_started.emit(heroes)


## Preço do portal do Macumbeiro para um ponto salvo, por jogador (seção 5.1).
static func portal_price(key: String) -> int:
	var area: Dictionary = GameData.arenas.get(key.get_slice(":", 0), {})
	var voodoo := Shops.shop("voodoo")
	return int(voodoo.get("portal_base", 40)) + int(voodoo.get("portal_per_level", 15)) * int(area.get("area_level", 1))


## Conversa que o NPC tem agora (a primeira cujo "when" bate com as missões).
static func dialogue_index(npc_id: String, quest_states: Dictionary) -> int:
	var dialogues: Array = GameData.npcs.get(npc_id, {}).get("dialogues", [])
	for i in dialogues.size():
		var when: Dictionary = dialogues[i].get("when", {})
		if when.has("quest_new") and quest_states.has(when.quest_new):
			continue
		if when.has("quest_active") and quest_states.get(when.quest_active, "") != "active":
			continue
		return i
	return -1


## O NPC tem uma missão para oferecer (marca "!"). Visitantes sempre têm.
func has_offer(npc_id: String) -> bool:
	if npc_id.begins_with("visitor:"):
		return true
	var i := dialogue_index(npc_id, quests)
	return i >= 0 and GameData.npcs[npc_id].dialogues[i].has("offer")


## DPS do painel de treino: dano total pelo tempo entre o primeiro e o último
## golpe (mínimo 1 s).
static func training_dps(stats: Dictionary) -> float:
	var seconds := maxf((int(stats.get("last_ms", 0)) - int(stats.get("start_ms", 0))) / 1000.0, 1.0)
	return float(stats.get("total", 0.0)) / seconds


## Missão principal ativa (para o HUD).
func active_quest() -> String:
	for id: String in quests:
		if quests[id] == "active":
			return id
	return ""


# --- Interação (servidor) ---------------------------------------------------------

func interact(player: Player, prop: Dictionary) -> void:
	match String(prop.kind):
		"shop":
			_send(player.peer_id, &"_open_shop", [String(prop.shop)])
		"npc" when String(prop.npc).begins_with("visitor:"):
			var index := int(String(prop.npc).get_slice(":", 1))
			var list: Array = _campaign().get("visitors", [])
			if index < list.size():
				_send(player.peer_id, &"_open_visitor", [index])
		"npc":
			var index := dialogue_index(prop.npc, _campaign().get("quests", {}))
			_send(player.peer_id, &"_open_dialogue", [String(prop.npc), index])
			# Ouvir a história põe as criaturas no bestiário.
			if index >= 0:
				learn(GameData.npcs[prop.npc].dialogues[index].get("bestiary", []))
		"quest_spot":
			resolve_spot(player, String(prop.quest))
		"forge":
			_send(player.peer_id, &"_open_forge", [])
		"sign":
			# O Arqueiro reconhece o brasão do próprio reino (03-2-areas.md, seção 3).
			var key: String = prop.get("text_key", "")
			if prop.has("archer_key") and player.character and player.character.data.class_id == "archer":
				key = prop.archer_key
			_arena()._toast_to(player, key, {})
		"training":
			_send(player.peer_id, &"_open_training", [])
		"stash":
			_send(player.peer_id, &"_open_stash", [])
		"exit":
			var needs: String = prop.get("requires", "")
			if needs != "" and needs not in _campaign().get("unlocked", []):
				_arena()._toast_to(player, "TOAST_LOCKED", {})
				return
			if prop.get("group", false):
				_arena().request_exit(player, prop)
			else:
				_arena().travel(String(prop.to), String(prop.get("entry", "start")), prop.get("expedition_end", false))
		"chest":
			_arena().open_chest(player, prop)
		"key":
			_arena().pick_key(player, prop)


@rpc("authority", "reliable")
func _open_shop(shop_id: String) -> void:
	shop_opened.emit(shop_id)


# --- Baú (os itens ficam no PC do dono; o servidor só move entre bolsa e baú) ---------

@rpc("authority", "reliable")
func _open_stash() -> void:
	stash_opened.emit()


func request_deposit(bag_index: int) -> void:
	_ask(&"_rpc_deposit", [bag_index])


## Tirar do baú: o PC do dono manda o item, o servidor confere e põe na bolsa.
func request_withdraw(stash_index: int) -> void:
	var stash := SaveSystem.load_stash()
	if stash_index >= 0 and stash_index < stash.size() and stash[stash_index] != null:
		_ask(&"_rpc_withdraw", [stash_index, stash[stash_index]])


@rpc("any_peer", "reliable")
func _rpc_deposit(bag_index: int) -> void:
	var player := _sender()
	if not multiplayer.is_server() or player == null or _arena().prop_near(player, "stash", "", REACH).is_empty():
		return
	var bag: Array = player.character.data.inventory
	if bag_index < 0 or bag_index >= bag.size() or bag[bag_index] == null:
		return
	var item: Dictionary = bag[bag_index]
	bag[bag_index] = null
	player.refresh_character()
	_send(player.peer_id, &"_stash_add", [item])


@rpc("any_peer", "reliable")
func _rpc_withdraw(stash_index: int, item: Dictionary) -> void:
	var player := _sender()
	if not multiplayer.is_server() or player == null or _arena().prop_near(player, "stash", "", REACH).is_empty() \
			or not Items.is_valid(item):
		return
	if not player.character.add_item(item.duplicate(true)):
		_arena()._toast_to(player, "TOAST_BAG_FULL", {})
		return
	player.refresh_character()
	_send(player.peer_id, &"_stash_remove", [stash_index])


@rpc("authority", "reliable")
func _stash_add(item: Dictionary) -> void:
	var holder := CharacterData.new()
	holder.data = {"inventory": SaveSystem.load_stash()}
	holder.add_item(item)
	SaveSystem.save_stash(holder.data.inventory)
	stash_opened.emit()


@rpc("authority", "reliable")
func _stash_remove(stash_index: int) -> void:
	var stash := SaveSystem.load_stash()
	if stash_index >= 0 and stash_index < stash.size():
		stash[stash_index] = null
	SaveSystem.save_stash(stash)
	stash_opened.emit()


@rpc("authority", "reliable")
func _open_portals() -> void:
	portals_opened.emit()


func request_portal(key: String) -> void:
	_ask(&"_rpc_portal", [key])


## Portal do Macumbeiro: todos pagam (ouro de cada um); se faltar para alguém,
## o aviso diz quem. O grupo vai junto para o checkpoint escolhido.
@rpc("any_peer", "reliable")
func _rpc_portal(key: String) -> void:
	var player := _sender()
	var c := _campaign()
	if not multiplayer.is_server() or player == null or key not in c.get("checkpoints_reached", []) \
			or _arena().prop_near(player, "npc", "voodoo_priest", REACH).is_empty():
		return
	var price := portal_price(key)
	var missing := PackedStringArray()
	var party := get_tree().get_nodes_in_group(&"players")
	for p: Player in party:
		if p.character == null or int(p.character.data.gold) < price:
			missing.append(p.hero_name)
	if not missing.is_empty():
		_arena()._toast_all("TOAST_PORTAL_MISSING_GOLD", {"names": ", ".join(missing), "price": price})
		return
	for p: Player in party:
		p.character.data.gold = int(p.character.data.gold) - price
		p.refresh_character()
	_arena().travel(key.get_slice(":", 0), key.get_slice(":", 1))


@rpc("authority", "reliable")
func _open_training() -> void:
	training_opened.emit()


@rpc("authority", "reliable")
func _open_dialogue(npc_id: String, index: int) -> void:
	dialogue_opened.emit(npc_id, index)


# --- Pedidos (qualquer PC) ----------------------------------------------------------

func request_accept(quest_id: String) -> void:
	_ask(&"_rpc_accept", [quest_id])


func request_service(npc_id: String, service: String) -> void:
	_ask(&"_rpc_service", [npc_id, service])


func request_buy(shop_id: String, index: int) -> void:
	_ask(&"_rpc_buy", [shop_id, index])


func request_sell(shop_id: String, bag_index: int) -> void:
	_ask(&"_rpc_sell", [shop_id, bag_index])


func _ask(method: StringName, args: Array) -> void:
	if multiplayer.is_server():
		callv(method, args)
	else:
		rpc_id.callv([1, method] + args)


func _sender() -> Player:
	var sender := multiplayer.get_remote_sender_id()
	if sender == 0:
		sender = multiplayer.get_unique_id()
	return _arena().get_node_or_null(str(sender)) as Player


@rpc("any_peer", "reliable")
func _rpc_accept(quest_id: String) -> void:
	var player := _sender()
	var quest: Dictionary = GameData.quests.get(quest_id, {})
	if not multiplayer.is_server() or player == null or quest.is_empty():
		return
	# Só aceita perto de quem oferece e se ainda não foi aceita.
	if _arena().prop_near(player, "npc", String(quest.giver), REACH).is_empty():
		return
	var c := _campaign()
	if c.quests.has(quest_id):
		return
	c.quests[quest_id] = "active"
	if quest.has("unlocks") and quest.unlocks not in c.unlocked:
		c.unlocked.append(quest.unlocks)
	SaveSystem.save_campaign(c, true)
	learn(quest.get("bestiary", []))
	sync()
	_arena()._toast_all("TOAST_QUEST_ACCEPTED", {"quest": quest.name_key})


@rpc("any_peer", "reliable")
func _rpc_service(npc_id: String, service: String) -> void:
	var player := _sender()
	if not multiplayer.is_server() or player == null or _arena().prop_near(player, "npc", npc_id, REACH).is_empty():
		return
	if service == "bestiary":
		_send(player.peer_id, &"_open_bestiary", [])
		return
	if service == "portals":
		_send(player.peer_id, &"_open_portals", [])
		return
	if service == "respec":
		var price := player.character.respec_price()
		if int(player.character.data.gold) < price:
			_arena()._toast_to(player, "TOAST_NO_GOLD", {})
			return
		player.character.data.gold = int(player.character.data.gold) - price
		player.character.respec()
		player.refresh_character()
		_arena()._toast_to(player, "TOAST_RESPEC_DONE", {})
		return
	if service == "rest":
		# Descansar na taverna: vida e recurso cheios, de graça.
		player.health = player.max_health
		player.resource = player.max_resource
		_arena()._toast_to(player, "TOAST_RESTED", {})


@rpc("any_peer", "reliable")
func _rpc_buy(shop_id: String, index: int) -> void:
	var player := _sender()
	if not multiplayer.is_server() or player == null or player.character == null \
			or _arena().prop_near(player, "", shop_id, REACH).is_empty():
		return
	var c := _campaign()
	var items := Shops.stock(shop_id, player.character, c.ship)
	if index < 0 or index >= items.size():
		return
	var item: Dictionary = items[index]
	if Shops.sold_out(shop_id, index, item, player.character, c.ship):
		return
	var price := Shops.buy_price(shop_id, item, int(player.character.data.level))
	if int(player.character.data.gold) < price:
		_arena()._toast_to(player, "TOAST_NO_GOLD", {})
		return
	if not player.character.add_item(item):
		_arena()._toast_to(player, "TOAST_BAG_FULL", {})
		return
	player.character.data.gold = int(player.character.data.gold) - price
	if item.kind == Items.EQUIPMENT and Shops.shop(shop_id).has("rarity_weights"):
		var bought: Dictionary = c.ship.bought
		bought[player.character.data.id] = bought.get(player.character.data.id, []) + [index]
		SaveSystem.save_campaign(c, true)
		sync()
	player.refresh_character()


@rpc("any_peer", "reliable")
func _rpc_sell(shop_id: String, bag_index: int) -> void:
	var player := _sender()
	if not multiplayer.is_server() or player == null or player.character == null \
			or _arena().prop_near(player, "", shop_id, REACH).is_empty():
		return
	var bag: Array = player.character.data.inventory
	if bag_index < 0 or bag_index >= bag.size() or bag[bag_index] == null:
		return
	var price := Shops.sell_price(shop_id, bag[bag_index], int(player.character.data.level), _campaign().ship)
	if price < 0:
		_arena()._toast_to(player, "TOAST_NOT_BUYING", {})
		return
	bag[bag_index] = null
	player.character.data.gold = int(player.character.data.gold) + price
	player.refresh_character()


# --- Missões e navio (servidor) -----------------------------------------------------

## Venceu a área da missão: concluída; cada jogador recebe a recompensa inteira.
func complete_quests_in(area_id: String) -> void:
	var c := _campaign()
	for id: String in c.get("quests", {}):
		var quest: Dictionary = GameData.quests.get(id, {})
		if c.quests[id] != "active" or quest.get("area", "") != area_id:
			continue
		c.quests[id] = "done"
		var reward: Dictionary = quest.get("reward", {})
		for p: Player in get_tree().get_nodes_in_group(&"players"):
			if p.character:
				p.grant(int(reward.get("xp", 0)), int(reward.get("gold", 0)))
		_arena()._toast_all("TOAST_QUEST_DONE", {"quest": quest.name_key})
	SaveSystem.save_campaign(c, true)
	sync()


## Voltou a Tortuga: chega outro navio (estoque pirata e preços dos valiosos novos)
## e outros visitantes sentam na taverna.
func new_ship(rng: RandomNumberGenerator) -> void:
	var c := _campaign()
	c.ship = Shops.new_ship(int(c.get("ship", {}).get("day", 0)) + 1, rng)
	c.visitors = SideQuests.generate_visitors(c, rng)
	sync()


# --- Ferreiro: refino, cristais e pergaminhos (05-1-refino.md) -----------------------

@rpc("authority", "reliable")
func _open_forge() -> void:
	forge_opened.emit()


func request_refine(ref: String, blessed: bool) -> void:
	_ask(&"_rpc_refine", [ref, blessed])


func request_crystallize(bag_index: int) -> void:
	_ask(&"_rpc_crystallize", [bag_index])


func request_craft(scroll_id: String) -> void:
	_ask(&"_rpc_craft", [scroll_id])


## Item da ficha por referência: "bag:3" (bolsa) ou "eq:weapon" (equipado).
static func item_at(character: CharacterData, ref: String) -> Variant:
	var where := ref.get_slice(":", 0)
	var key := ref.get_slice(":", 1)
	if where == "bag" and key.is_valid_int() and int(key) >= 0 and int(key) < character.data.inventory.size():
		return character.data.inventory[int(key)]
	if where == "eq":
		return character.data.equipment.get(key)
	return null


static func _clear_at(character: CharacterData, ref: String) -> void:
	if ref.begins_with("bag:"):
		character.data.inventory[int(ref.get_slice(":", 1))] = null
	else:
		character.data.equipment[ref.get_slice(":", 1)] = null


## Refinar (só na cidade, perto da forja; sorteio no servidor, salvo em seguida).
@rpc("any_peer", "reliable")
func _rpc_refine(ref: String, blessed: bool) -> void:
	var player := _sender()
	if not multiplayer.is_server() or player == null or _arena().prop_near(player, "forge", "", REACH).is_empty():
		return
	var c := player.character
	var item: Variant = item_at(c, ref)
	if item == null or not item is Dictionary:
		return
	var reason := Refine.refuse_reason(item)
	if reason != "":
		_arena()._toast_to(player, reason, {})
		return
	var scroll := Refine.scroll_for(item, blessed)
	if not c.take_one(scroll):
		_arena()._toast_to(player, "REFINE_NO_SCROLL", {})
		return
	var result := Refine.attempt(item, blessed, _arena()._rng)
	match result:
		"ok":
			_arena()._toast_to(player, "REFINE_OK", {"level": int(item.refine)})
		"reset":
			_arena()._toast_to(player, "REFINE_RESET", {})
		"broken":
			var crystals := Refine.crystals_for(item)
			_clear_at(c, ref)
			c.add_item(Items.stack(Items.CONSUMABLE, "crystal_" + String(item.material), crystals))
			_arena()._toast_to(player, "REFINE_BROKEN", {"count": crystals})
	player.refresh_character()


## Cristalizar de propósito um item da bolsa.
@rpc("any_peer", "reliable")
func _rpc_crystallize(bag_index: int) -> void:
	var player := _sender()
	if not multiplayer.is_server() or player == null or _arena().prop_near(player, "forge", "", REACH).is_empty():
		return
	var item: Variant = item_at(player.character, "bag:%d" % bag_index)
	if item == null or Refine.scroll_for(item, false) == "":
		return
	_clear_at(player.character, "bag:%d" % bag_index)
	player.character.add_item(Items.stack(Items.CONSUMABLE, "crystal_" + String(item.material), Refine.crystals_for(item)))
	player.refresh_character()


## Fazer um pergaminho normal com 10 cristais do material + ouro.
@rpc("any_peer", "reliable")
func _rpc_craft(scroll_id: String) -> void:
	var player := _sender()
	var def: Dictionary = GameData.consumables.get(scroll_id, {})
	if not multiplayer.is_server() or player == null or def.get("restore", "") != "refine" or def.get("blessed", true) \
			or _arena().prop_near(player, "forge", "", REACH).is_empty():
		return
	var c := player.character
	var crystal := "crystal_" + String(def.material)
	var need := int(GameData.refine.craft_crystals)
	var gold := Refine.craft_gold(scroll_id)
	if c.count_of(crystal) < need or int(c.data.gold) < gold:
		_arena()._toast_to(player, "REFINE_CRAFT_MISSING", {"count": need, "gold": gold})
		return
	for i in need:
		c.take_one(crystal)
	c.data.gold = int(c.data.gold) - gold
	c.add_item(Items.stack(Items.CONSUMABLE, scroll_id))
	player.refresh_character()


# --- Bestiário e missões secundárias (servidor) ---------------------------------------

## Criaturas cuja história o grupo ouviu entram no bestiário.
func learn(ids: Array) -> void:
	var c := _campaign()
	var changed := false
	for id in ids:
		if GameData.bestiary.has(id) and id not in c.bestiary:
			c.bestiary.append(id)
			_arena()._toast_all("TOAST_BESTIARY_NEW", {"name": GameData.bestiary[id].name_key})
			changed = true
	if changed:
		sync()


@rpc("authority", "reliable")
func _open_bestiary() -> void:
	bestiary_opened.emit()


@rpc("authority", "reliable")
func _open_visitor(index: int) -> void:
	if index < visitors.size():
		var visitor: Dictionary = visitors[index]
		visitor_opened.emit(String(visitor.name), SideQuests.visitor_lines(visitor), index)


func request_accept_side(visitor_index: int) -> void:
	_ask(&"_rpc_accept_side", [visitor_index])


## Aceitar a história de um visitante: vira missão ativa (até 5); ele vai embora
## e a criatura entra no bestiário.
@rpc("any_peer", "reliable")
func _rpc_accept_side(visitor_index: int) -> void:
	var player := _sender()
	var c := _campaign()
	var list: Array = c.get("visitors", [])
	if not multiplayer.is_server() or player == null or visitor_index < 0 or visitor_index >= list.size() \
			or _arena().prop_near(player, "npc", "visitor:%d" % visitor_index, REACH).is_empty():
		return
	if SideQuests.active(c.side_quests).size() >= int(GameData.visitors.max_active):
		_arena()._toast_to(player, "TOAST_SIDE_FULL", {})
		return
	var quest: Dictionary = list[visitor_index].quest
	quest.status = "active"
	c.side_quests[quest.id] = quest
	list.remove_at(visitor_index)
	SaveSystem.save_campaign(c, true)
	learn([quest.target])
	sync()
	_arena()._toast_all("TOAST_SIDE_ACCEPTED", {"quest": SideQuests.title(quest)})


## Monstro morto: conta para as caçadas ativas dessa criatura nesta área.
func on_monster_killed(monster_id: String, area_id: String) -> void:
	var c := _campaign()
	for quest: Dictionary in SideQuests.active(c.get("side_quests", {})):
		if quest.template != "hunt" or quest.area != area_id:
			continue
		if monster_id in GameData.bestiary.get(quest.target, {}).get("monsters", []):
			quest.progress = int(quest.progress) + 1
			if int(quest.progress) >= int(quest.count):
				_complete_side(quest)
			sync()


## Lugares de rumor e cargas perdidas das missões ativas nesta área.
func spot_props(area_id: String) -> Array:
	var props := []
	var spots: Array = GameData.arenas.get(area_id, {}).get("quest_spots", [])
	for quest: Dictionary in SideQuests.active(_campaign().get("side_quests", {})):
		if quest.area != area_id or not quest.has("spot") or int(quest.spot) >= spots.size():
			continue
		props.append({"id": "spot_" + String(quest.id), "kind": "quest_spot", "quest": quest.id,
			"name_key": "PROP_LOST_CARGO" if quest.template == "retrieve" else "PROP_RUMOR_SPOT",
			"position": spots[int(quest.spot)]})
	return props


## Chegou ao lugar: carga achada, ou o rumor era verdade (tesouro), armadilha
## (emboscada) ou nada.
func resolve_spot(player: Player, quest_id: String) -> void:
	var c := _campaign()
	var quest: Dictionary = c.get("side_quests", {}).get(quest_id, {})
	if quest.is_empty() or quest.status != "active":
		return
	_arena()._remove_prop.rpc("spot_" + quest_id)
	if quest.template == "rumor":
		match String(quest.outcome):
			"ambush":
				var ambush: Dictionary = GameData.visitors.quest_templates.rumor.ambush
				_arena().spawn_ambush(player.global_position, String(ambush.monster), int(ambush.count))
				_arena()._toast_all("TOAST_RUMOR_AMBUSH", {})
				quest.gold = 0
				quest.xp = 0
			"nothing":
				_arena()._toast_all("TOAST_RUMOR_NOTHING", {})
				quest.gold = 0
				quest.xp = 0
			_:
				_arena()._toast_all("TOAST_RUMOR_TREASURE", {})
				for p: Player in get_tree().get_nodes_in_group(&"players"):
					if p.character:
						p.grant(0, 0, [Items.stack(Items.VALUABLE, "silver_goblet")])
	_complete_side(quest)
	sync()


func _complete_side(quest: Dictionary) -> void:
	quest.status = "done"
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.character:
			p.grant(int(quest.xp), int(quest.gold))
	_arena()._toast_all("TOAST_SIDE_DONE", {"quest": SideQuests.title(quest)})
	SaveSystem.save_campaign(_campaign(), true)


func _send(peer_id: int, method: StringName, args: Array) -> void:
	if peer_id == multiplayer.get_unique_id():
		callv(method, args)
	elif peer_id in multiplayer.get_peers():
		rpc_id.callv([peer_id, method] + args)
