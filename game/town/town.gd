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

const REACH := 4.0

## Cópia em todos os PCs.
var quests := {}
var unlocked: Array = []
var ship := {}


func _arena() -> Node:
	return get_parent()


func _campaign() -> Dictionary:
	return _arena()._campaign


# --- Estado (servidor -> todos) --------------------------------------------------

func sync(peer_id := 0) -> void:
	var c := _campaign()
	if peer_id == 0:
		_set_state.rpc(c.get("quests", {}), c.get("unlocked", []), c.get("ship", {}))
	else:
		_set_state.rpc_id(peer_id, c.get("quests", {}), c.get("unlocked", []), c.get("ship", {}))


@rpc("authority", "call_local", "reliable")
func _set_state(new_quests: Dictionary, new_unlocked: Array, new_ship: Dictionary) -> void:
	quests = new_quests
	unlocked = new_unlocked
	ship = new_ship
	state_changed.emit()


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


## O NPC tem uma missão para oferecer (marca "!").
func has_offer(npc_id: String) -> bool:
	var i := dialogue_index(npc_id, quests)
	return i >= 0 and GameData.npcs[npc_id].dialogues[i].has("offer")


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
		"npc":
			_send(player.peer_id, &"_open_dialogue", [String(prop.npc), dialogue_index(prop.npc, _campaign().get("quests", {}))])
		"sign":
			_arena()._toast_to(player, String(prop.get("text_key", "")), {})
		"exit":
			var needs: String = prop.get("requires", "")
			if needs != "" and needs not in _campaign().get("unlocked", []):
				_arena()._toast_to(player, "TOAST_LOCKED", {})
				return
			_arena().travel(String(prop.to), String(prop.get("entry", "start")), prop.get("expedition_end", false))


@rpc("authority", "reliable")
func _open_shop(shop_id: String) -> void:
	shop_opened.emit(shop_id)


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
	sync()
	_arena()._toast_all("TOAST_QUEST_ACCEPTED", {"quest": quest.name_key})


@rpc("any_peer", "reliable")
func _rpc_service(npc_id: String, service: String) -> void:
	var player := _sender()
	if not multiplayer.is_server() or player == null or _arena().prop_near(player, "npc", npc_id, REACH).is_empty():
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
			or _arena().prop_near(player, "shop", shop_id, REACH).is_empty():
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
			or _arena().prop_near(player, "shop", shop_id, REACH).is_empty():
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


## Voltou a Tortuga: chega outro navio (estoque pirata e preços dos valiosos novos).
func new_ship(rng: RandomNumberGenerator) -> void:
	var c := _campaign()
	c.ship = Shops.new_ship(int(c.get("ship", {}).get("day", 0)) + 1, rng)
	sync()


func _send(peer_id: int, method: StringName, args: Array) -> void:
	if peer_id == multiplayer.get_unique_id():
		callv(method, args)
	elif peer_id in multiplayer.get_peers():
		rpc_id.callv([peer_id, method] + args)
