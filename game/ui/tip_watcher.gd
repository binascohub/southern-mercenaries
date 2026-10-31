# Southern Mercenaries — GPL-3.0-or-later
class_name TipWatcher
extends Node
## Olha o jogo deste PC (o herói local, os monstros perto, o chão, a bolsa) e
## avisa o TipManager dos eventos das dicas (14-tutorial.md, seção 4). Roda em
## todos os PCs, cada um com o seu herói, sem nada de rede além de guardar a
## dica vista no personagem.

const INTERVAL := 0.4
const ENEMY_NEAR := 12.0
const LOOT_NEAR := 8.0
const RETURN_NEAR := 6.0
const LOW_HEALTH := 0.4
## Ataques básicos antes da dica do ataque forte.
const BASIC_ATTACKS := 5

var _arena: Node
var _timer := 0.0
var _started := false
var _area := ""
var _level := 0
var _attacks_at_start := -1


func bind(arena: Node) -> void:
	_arena = arena
	TipManager.reset()
	TipManager.seen.connect(_on_seen)
	var town: Town = arena.town
	town.shop_opened.connect(func(_id: String) -> void: TipManager.notify("shop_opened"))


func _exit_tree() -> void:
	if TipManager.seen.is_connected(_on_seen):
		TipManager.seen.disconnect(_on_seen)
	TipManager.reset()


func _on_seen(id: String) -> void:
	var player: Player = _arena.local_player if _arena else null
	if player == null or not is_instance_valid(player):
		return
	if multiplayer.is_server():
		player.request_tip_seen(id)
	else:
		player.request_tip_seen.rpc_id(1, id)


func _process(delta: float) -> void:
	_timer -= delta
	if _timer > 0.0:
		return
	_timer = INTERVAL
	var player: Player = _arena.local_player
	if player == null or not is_instance_valid(player) or player.character == null or Session.ui_open:
		return
	check(player)


## Uma rodada de verificação (também chamada pelos testes).
func check(player: Player) -> void:
	var c := player.character
	var class_id := String(c.data.class_id)
	if not _started:
		_started = true
		_level = int(c.data.level)
		TipManager.notify("start")
	if _arena.area_id != _area:
		_area = _arena.area_id
		if not _arena.arena.get("town", false):
			TipManager.notify("checkpoint")  # cada área de mapa começa num checkpoint
			TipManager.notify("map_area", class_id)
	if int(c.data.level) > _level:
		TipManager.notify("level_up")
	_level = int(c.data.level)
	if player.alive and player.health < player.max_health * LOW_HEALTH:
		TipManager.notify("low_health")
	if not _arena.prop_near(player).is_empty():
		TipManager.notify("interact_near")
	if not _arena.prop_near(player, "", "return_portal", RETURN_NEAR).is_empty():
		TipManager.notify("return_near")
	_check_enemies(player, c)
	for drop: Variant in _arena._loot_nodes.values():
		if is_instance_valid(drop) and drop.global_position.distance_to(player.global_position) < LOOT_NEAR:
			TipManager.notify("loot_near")
			break
	_check_bag(c)
	for other: Player in get_tree().get_nodes_in_group(&"players"):
		if other != player and not other.alive:
			TipManager.notify("ally_down")


func _check_enemies(player: Player, c: CharacterData) -> void:
	var near := false
	for node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy := node as Enemy
		if enemy == null:
			continue
		if enemy.data.get("breakable", false):
			if enemy.global_position.distance_to(player.global_position) < 6.0:
				TipManager.notify("breakable_near")
			continue
		if enemy.state == Enemy.State.SLEEP or enemy.health <= 0.0 \
				or enemy.global_position.distance_to(player.global_position) > ENEMY_NEAR:
			continue
		near = true
		if enemy.is_boss():
			TipManager.notify("boss_near")
		if enemy.category() in ["elite", "miniboss"]:
			TipManager.notify("elite_near")
		if enemy.element != "" and not is_equal_approx(Elements.multiplier(c.current_element(), enemy.element), 1.0):
			TipManager.notify("element_matters")
		if enemy.state == Enemy.State.WINDUP:
			TipManager.notify("telegraph")
	if not near:
		return
	TipManager.notify("enemy_near")
	# Ataque forte: depois de alguns ataques básicos com monstro perto.
	var presses: int = player._local_input.attack_presses
	if _attacks_at_start < 0:
		_attacks_at_start = presses
	elif presses - _attacks_at_start >= BASIC_ATTACKS:
		TipManager.notify("basic_attacks")
	var first: String = c.data.get("skill_slots", [""])[0]
	if first != "" and player.resource >= player.max_resource * 0.99:
		TipManager.notify("skill_ready")


func _check_bag(c: CharacterData) -> void:
	for item: Variant in c.data.inventory:
		if item == null:
			continue
		if item.kind == Items.EQUIPMENT and c.can_equip(item):
			TipManager.notify("equipment_usable")
		elif item.kind == Items.CONSUMABLE:
			var id := String(item.id)
			if id.contains("scroll_refine"):
				TipManager.notify("refine_scroll")
			elif id.begins_with("elemental_potion"):
				TipManager.notify("elemental_potion")
