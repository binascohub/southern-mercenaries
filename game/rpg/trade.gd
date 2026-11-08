# Southern Mercenaries — GPL-3.0-or-later
class_name Trade
extends Node
## Troca entre jogadores do grupo (05-itens-e-loot.md, seção 8): só entre
## jogadores presentes na mesma partida, perto um do outro; cada lado oferece
## itens da bolsa e ouro, e a troca só acontece quando os dois confirmam.
## Qualquer mudança na oferta desfaz as confirmações. O servidor guarda as
## ofertas, valida tudo de novo na hora de trocar e faz a troca de uma vez
## (ou nada muda).
##
## Fica como filho da arena, com o mesmo nome em todos os PCs (as RPCs usam o
## caminho do nó). Os jogadores são os irmãos com o nome do ID de rede.

## Alguém chamou este PC para trocar.
signal invited(trade_id: int, from_name: String)
## Estado da troca deste PC: {id, you: {...}, them: {...}} (ver _state_for).
signal updated(state: Dictionary)
## A troca deste PC acabou (TRADE_DONE, TRADE_DECLINED, TRADE_CANCELLED…).
signal ended(reason_key: String)

## Distância máxima entre os dois jogadores (proposta).
const RANGE := 5.0
## Sai da troca se se afastarem mais que isto.
const LEAVE_RANGE := 8.0
const INVITE_TIME := 20.0
const MAX_ITEMS := 12

## Servidor: id -> {a, b, open, offers: {peer: {items, gold}}, snapshot: {peer: [item]},
## confirmed: {peer: bool}, invite_left}.
var _trades := {}
var _next_id := 1


# --- Pedidos (qualquer PC) -------------------------------------------------------

func request_trade() -> void:
	_ask(&"_rpc_request", [])


func answer(trade_id: int, accept: bool) -> void:
	_ask(&"_rpc_answer", [trade_id, accept])


func set_offer(trade_id: int, indices: Array, gold: int) -> void:
	_ask(&"_rpc_offer", [trade_id, indices, gold])


func confirm(trade_id: int) -> void:
	_ask(&"_rpc_confirm", [trade_id])


func cancel(trade_id: int) -> void:
	_ask(&"_rpc_cancel", [trade_id])


func _ask(method: StringName, args: Array) -> void:
	if multiplayer.is_server():
		callv(method, args)
	else:
		rpc_id.callv([1, method] + args)


func _sender() -> int:
	var sender := multiplayer.get_remote_sender_id()
	return sender if sender != 0 else multiplayer.get_unique_id()


@rpc("any_peer", "reliable")
func _rpc_request() -> void:
	if multiplayer.is_server():
		server_request(_sender())


@rpc("any_peer", "reliable")
func _rpc_answer(trade_id: int, accept: bool) -> void:
	if multiplayer.is_server():
		server_answer(_sender(), trade_id, accept)


@rpc("any_peer", "reliable")
func _rpc_offer(trade_id: int, indices: Array, gold: int) -> void:
	if multiplayer.is_server():
		server_offer(_sender(), trade_id, indices, gold)


@rpc("any_peer", "reliable")
func _rpc_confirm(trade_id: int) -> void:
	if multiplayer.is_server():
		server_confirm(_sender(), trade_id)


@rpc("any_peer", "reliable")
func _rpc_cancel(trade_id: int) -> void:
	if multiplayer.is_server():
		server_cancel(_sender(), trade_id)


# --- Servidor --------------------------------------------------------------------

## Troca em que o jogador está (0 = nenhuma).
func trade_of(peer_id: int) -> int:
	for id: int in _trades:
		if _trades[id].a == peer_id or _trades[id].b == peer_id:
			return id
	return 0


## Chama o aliado mais perto (vivo, conectado, ao alcance e livre).
func server_request(peer_id: int) -> void:
	var me := _player(peer_id)
	if me == null or not me.alive or trade_of(peer_id) != 0:
		return
	var target: Player = null
	var best := RANGE
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p == me or not p.alive or not p.connected or p.character == null or trade_of(p.peer_id) != 0:
			continue
		var d := p.global_position.distance_to(me.global_position)
		if d <= best:
			best = d
			target = p
	if target == null:
		_arena().call(&"_toast_to", me, "TRADE_NOBODY_NEAR", {})
		return
	var id := _next_id
	_next_id += 1
	_trades[id] = {"a": peer_id, "b": target.peer_id, "open": false,
		"offers": {peer_id: _empty_offer(), target.peer_id: _empty_offer()},
		"snapshot": {peer_id: [], target.peer_id: []},
		"confirmed": {peer_id: false, target.peer_id: false}, "invite_left": INVITE_TIME}
	_send(target.peer_id, &"_invited", [id, me.hero_name])
	_arena().call(&"_toast_to", me, "TRADE_INVITE_SENT", {"name": target.hero_name})


func server_answer(peer_id: int, trade_id: int, accept: bool) -> void:
	var t: Dictionary = _trades.get(trade_id, {})
	if t.is_empty() or t.b != peer_id or t.open:
		return
	if not accept:
		_finish(trade_id, "TRADE_DECLINED")
		return
	t.open = true
	_broadcast(trade_id)


func server_offer(peer_id: int, trade_id: int, indices: Array, gold: int) -> void:
	var t: Dictionary = _trades.get(trade_id, {})
	var p := _player(peer_id)
	if t.is_empty() or not t.open or not t.offers.has(peer_id) or p == null:
		return
	var bag: Array = p.character.data.inventory
	var clean: Array[int] = []
	for value: Variant in indices:
		if not (value is int or value is float):
			continue
		var i := int(value)
		if i >= 0 and i < bag.size() and bag[i] != null and not Items.is_quest_item(bag[i]) and i not in clean and clean.size() < MAX_ITEMS:  # objeto de missão não se troca
			clean.append(i)
	t.offers[peer_id] = {"items": clean, "gold": clampi(gold, 0, int(p.character.data.gold))}
	var snapshot := []
	for i in clean:
		snapshot.append(bag[i].duplicate(true))
	t.snapshot[peer_id] = snapshot
	for k: int in t.confirmed:
		t.confirmed[k] = false
	_broadcast(trade_id)


func server_confirm(peer_id: int, trade_id: int) -> void:
	var t: Dictionary = _trades.get(trade_id, {})
	if t.is_empty() or not t.open or not t.confirmed.has(peer_id):
		return
	t.confirmed[peer_id] = true
	if t.confirmed[t.a] and t.confirmed[t.b]:
		_execute(trade_id)
	else:
		_broadcast(trade_id)


func server_cancel(peer_id: int, trade_id: int) -> void:
	var t: Dictionary = _trades.get(trade_id, {})
	if not t.is_empty() and (t.a == peer_id or t.b == peer_id):
		_finish(trade_id, "TRADE_CANCELLED")


func _physics_process(delta: float) -> void:
	if not multiplayer.is_server():
		return
	for id: int in _trades.keys():
		var t: Dictionary = _trades[id]
		var a := _player(t.a)
		var b := _player(t.b)
		if a == null or b == null or not a.alive or not b.alive or not a.connected or not b.connected \
				or a.global_position.distance_to(b.global_position) > LEAVE_RANGE:
			_finish(id, "TRADE_CANCELLED")
			continue
		if not t.open:
			t.invite_left -= delta
			if t.invite_left <= 0.0:
				_finish(id, "TRADE_DECLINED")


func _execute(trade_id: int) -> void:
	var t: Dictionary = _trades[trade_id]
	var a := _player(t.a)
	var b := _player(t.b)
	var error := ""
	# A bolsa mudou desde a oferta (equipou, bebeu…): os dois revisam e confirmam de novo.
	for peer: int in [t.a, t.b]:
		var bag: Array = _player(peer).character.data.inventory
		var items: Array = t.offers[peer].items
		for n in items.size():
			var current: Variant = bag[items[n]]
			if current == null or current != t.snapshot[peer][n]:
				error = "TRADE_CHANGED"
	if error == "":
		error = swap(a.character, t.offers[t.a], b.character, t.offers[t.b])
	if error != "":
		for k: int in t.confirmed:
			t.confirmed[k] = false
		_arena().call(&"_toast_to", a, error, {})
		_arena().call(&"_toast_to", b, error, {})
		_broadcast(trade_id)
		return
	a.refresh_character()
	b.refresh_character()
	_finish(trade_id, "TRADE_DONE")


## Troca de uma vez as ofertas ({items: [índices da bolsa], gold}) entre duas
## fichas. Retorna "" se trocou, ou a chave do motivo (e nada muda).
static func swap(a: CharacterData, a_offer: Dictionary, b: CharacterData, b_offer: Dictionary) -> String:
	if a_offer.items.is_empty() and b_offer.items.is_empty() and a_offer.gold <= 0 and b_offer.gold <= 0:
		return "TRADE_EMPTY"
	var na := CharacterData.new()
	na.data = a.data.duplicate(true)
	var nb := CharacterData.new()
	nb.data = b.data.duplicate(true)
	for side: Array in [[na, a_offer], [nb, b_offer]]:
		var c: CharacterData = side[0]
		var offer: Dictionary = side[1]
		if int(offer.gold) < 0 or int(offer.gold) > int(c.data.gold):
			return "TRADE_CHANGED"
		for i: int in offer.items:
			if i < 0 or i >= c.data.inventory.size() or c.data.inventory[i] == null or Items.is_quest_item(c.data.inventory[i]):
				return "TRADE_CHANGED"
	var from_a := []
	for i: int in a_offer.items:
		from_a.append(na.data.inventory[i])
		na.data.inventory[i] = null
	var from_b := []
	for i: int in b_offer.items:
		from_b.append(nb.data.inventory[i])
		nb.data.inventory[i] = null
	for item: Dictionary in from_b:
		if not na.add_item(item):
			return "TRADE_NO_ROOM"
	for item: Dictionary in from_a:
		if not nb.add_item(item):
			return "TRADE_NO_ROOM"
	na.data.gold = int(na.data.gold) - int(a_offer.gold) + int(b_offer.gold)
	nb.data.gold = int(nb.data.gold) - int(b_offer.gold) + int(a_offer.gold)
	a.data = na.data
	b.data = nb.data
	return ""


func _finish(trade_id: int, reason_key: String) -> void:
	var t: Dictionary = _trades.get(trade_id, {})
	if t.is_empty():
		return
	_trades.erase(trade_id)
	# O convidado que ainda não abriu a janela não precisa saber da recusa dele.
	_send(t.a, &"_ended", [trade_id, reason_key])
	if t.open or reason_key != "TRADE_DECLINED":
		_send(t.b, &"_ended", [trade_id, reason_key])


func _broadcast(trade_id: int) -> void:
	var t: Dictionary = _trades[trade_id]
	_send(t.a, &"_state", [_state_for(t, t.a, t.b, trade_id)])
	_send(t.b, &"_state", [_state_for(t, t.b, t.a, trade_id)])


func _state_for(t: Dictionary, me: int, other: int, trade_id: int) -> Dictionary:
	return {"id": trade_id, "you": _side(t, me), "them": _side(t, other)}


func _side(t: Dictionary, peer: int) -> Dictionary:
	var p := _player(peer)
	return {"name": p.hero_name if p else "", "indices": t.offers[peer].items.duplicate(),
		"items": t.snapshot[peer].duplicate(true), "gold": t.offers[peer].gold,
		"confirmed": t.confirmed[peer], "bag_gold": int(p.character.data.gold) if p and p.character else 0}


static func _empty_offer() -> Dictionary:
	return {"items": [] as Array[int], "gold": 0}


## Manda para um PC (o próprio host chama direto; peers que não existem são ignorados).
func _send(peer_id: int, method: StringName, args: Array) -> void:
	if peer_id == multiplayer.get_unique_id():
		callv(method, args)
	elif peer_id in multiplayer.get_peers():
		rpc_id.callv([peer_id, method] + args)


func _player(peer_id: int) -> Player:
	var node := _arena().get_node_or_null(str(peer_id)) as Player
	return node if node and not node.is_queued_for_deletion() else null


func _arena() -> Node:
	return get_parent()


# --- Chegam do servidor ----------------------------------------------------------

@rpc("authority", "reliable")
func _invited(trade_id: int, from_name: String) -> void:
	invited.emit(trade_id, from_name)


@rpc("authority", "reliable")
func _state(state: Dictionary) -> void:
	updated.emit(state)


@rpc("authority", "reliable")
func _ended(_trade_id: int, reason_key: String) -> void:
	ended.emit(reason_key)
