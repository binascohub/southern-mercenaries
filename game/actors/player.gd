# Southern Mercenaries — GPL-3.0-or-later
class_name Player
extends CharacterBody3D
## Herói controlável. Mago com ataque básico, ataque forte (segurar) e esquiva
## (02-1-mago.md, seção 5); números em data/classes.json.
##
## Rede: o nó se chama com o ID de rede do dono. O PC dono lê a entrada e a
## envia ao servidor; só o servidor simula, aplica dano e decide queda/revive.
## Posição e estado chegam aos outros PCs pelo MultiplayerSynchronizer.
##
## Habilidades (Fase 5): os atalhos 1–4 usam as habilidades ativas da ficha;
## o servidor confere rank, recarga e mana e chama o SkillSystem da arena.
## Passivas: Mente Afiada (regeneração), Escudo de Mana (parte do dano sai da
## mana), Domínio Elemental (dano e duração dos estados). Bônus de aliados
## (Bênção das Chamas, Vento a Favor) e escudo (Pele de Pedra) ficam aqui.
##
## Ficha (Fase 3): o servidor guarda a cópia oficial do personagem
## (CharacterData) e aplica XP, loot, ouro, poções e equipamento; cada mudança
## volta ao PC do dono, que grava no próprio disco (07-rede.md, seção 8).

signal health_changed(current: float, maximum: float)
signal resource_changed(current: float, maximum: float)
## Caiu (vida zerou). Só emitido no servidor.
signal downed
## Levou dano (só no servidor); interrompe uma reanimação em andamento.
signal hurt
## A ficha deste PC mudou (só no PC dono). `levels` = níveis ganhos agora.
signal character_changed(levels: int)

const AIM_ASSIST_ANGLE := deg_to_rad(15.0)
const PROJECTILE_HEIGHT := 1.0
const TURN_SPEED := 18.0
## Cor do anel de cada jogador (1 a 4), para se reconhecerem no co-op.
const SLOT_COLORS: Array[Color] = [
	Color(0.95, 0.75, 0.2), Color(0.3, 0.7, 1.0), Color(0.4, 0.9, 0.4), Color(0.9, 0.4, 0.9),
]
const BODY_COLOR := Color(0.78, 0.72, 0.6)

# Sincronizados (servidor -> todos).
var peer_id := 1
var slot := 0
var class_id := "mage"
var facing := Vector2(0, 1)
var health := 100.0
var max_health := 100.0
var resource := 100.0
var max_resource := 100.0
var alive := true
var charge_time := 0.0
var revive_progress := 0.0
var evade_cooldown := 0.0
## false enquanto o dono caiu da rede: o herói espera parado e invulnerável.
var connected := true
## Posição no servidor; os clientes mostram com interpolação.
var net_position := Vector3.ZERO
## Nome e nível do herói e material de cada peça visível (para os outros verem).
var hero_name := ""
var level := 1
var equip_visual := {}
var potion_cooldown := 0.0
var armor_value := 0.0
## Elemento em uso (de origem ou da Poção Elemental): cor do cristal e dos projéteis.
var element := "fire"
## Escudo que absorve dano (Pele de Pedra); sincronizado para a barra.
var shield := 0.0
## Invisível para os monstros (Bomba de Fumaça do Ninja).
var hidden := false
## Cavaleiro montado (02-3-cavaleiro.md, seção 3).
var mounted := false

var data: Dictionary
var move_speed := 5.0
var power := 0.0

## Ficha: no servidor é a oficial; no PC dono é a cópia que vai para o disco.
var character: CharacterData

# Só no servidor.
var _input := PlayerInput.new()
var _seen := PlayerInput.new()
## Contadores já tratados de poções e coleta (separado de _seen, que zera ao cair).
var _seen_extra := PlayerInput.new()
var _attack_cooldown := 0.0
var _evade_time := 0.0
var _evade_dir := Vector2.ZERO
## Recargas das habilidades (chave -> s), bônus ativos (id -> {value, time}) e escudo.
var _skill_cd := {}
var _buffs := {}
var _shield_time := 0.0
var _rng_dodge := RandomNumberGenerator.new()
## Cavaleiro: desmontou por conta própria (não remonta sozinho) e espera para remontar.
var _manual_dismount := false
var _remount_timer := 0.0
var _body_shape: CapsuleShape3D
var _horse: Node3D

# Só no PC dono.
var _local_input := PlayerInput.new()
var _sent_input := PlayerInput.new()
var _input_timer := 0.0
## Recargas vistas pelo dono (para o HUD): chave -> segundos.
var skill_cd_view := {}

# Só nos clientes.
var _snapshots := SnapshotBuffer.new()
var _last_net_position := Vector3.INF

var _visual: Node3D
var _body_material: StandardMaterial3D
var _crystal_material: StandardMaterial3D
var _revive_bar: MeshInstance3D
var _ring_material: StandardMaterial3D
var _staff_material: StandardMaterial3D
## Peças equipadas no corpo (placeholder até os modelos modulares).
var _gear := {}
var _shown_visual := {}
var _flash := 0.0
var _shown_health := -1.0
var _shown_resource := -1.0


## Criado pelo spawner em todos os PCs, com os mesmos dados.
static func create(spawn: Dictionary) -> Player:
	var player := Player.new()
	player.peer_id = spawn.peer_id
	player.name = str(spawn.peer_id)
	player.slot = spawn.slot
	player.class_id = spawn.class_id
	player.position = spawn.position
	player.net_position = spawn.position
	player.hero_name = spawn.get("name", "")
	player.level = spawn.get("level", 1)
	player.equip_visual = spawn.get("visual", {})
	player.element = spawn.get("element", "fire")
	player._add_synchronizer()
	return player


func _ready() -> void:
	add_to_group(&"players")
	_rng_dodge.randomize()
	_snapshots.delay = GameData.balance.net.interpolation_delay
	collision_layer = 2
	collision_mask = 1 | 4
	# Visão de cima, sem gravidade nem plataformas.
	motion_mode = CharacterBody3D.MOTION_MODE_FLOATING
	_load_class()
	_build_visual()


func is_local() -> bool:
	return peer_id == multiplayer.get_unique_id()


func _load_class() -> void:
	data = GameData.get_class_data(class_id)
	max_health = data.max_health
	max_resource = data.max_resource
	health = max_health
	resource = max_resource
	mounted = data.has("mount")
	move_speed = GameData.balance.base_move_speed * _speed_pct() / 100.0


## Velocidade da classe; o Cavaleiro a pé anda a 95% (montado, 120%).
func _speed_pct() -> float:
	if data.has("mount") and not mounted:
		return float(data.get("foot_speed_pct", data.move_speed_pct))
	return float(data.move_speed_pct)


## Servidor: assume a ficha do personagem e calcula vida, recurso, poder etc.
func set_character(c: CharacterData) -> void:
	character = c
	_apply_character(true)
	_push_character(0)


## Recalcula as estatísticas pela ficha (13-balanceamento.md). Ao subir de
## nível ou trocar equipamento, a vida e o recurso acompanham o novo máximo.
func _apply_character(fill := false) -> void:
	var old_max_health := max_health
	var old_max_resource := max_resource
	max_health = character.max_health()
	max_resource = character.max_resource()
	power = character.power()
	armor_value = character.armor()
	move_speed = GameData.balance.base_move_speed * _speed_pct() / 100.0 \
		* (1.0 + character.move_speed_bonus())
	if fill:
		health = max_health
		resource = max_resource
	else:
		health = clampf(health + maxf(max_health - old_max_health, 0.0), 0.0, max_health) if alive else 0.0
		resource = clampf(resource + maxf(max_resource - old_max_resource, 0.0), 0.0, max_resource)
	hero_name = character.data.name
	level = int(character.data.level)
	equip_visual = character.equipment_visual()
	element = character.current_element()


## Servidor: manda a ficha atual para o dono gravar.
func _push_character(levels: int) -> void:
	if peer_id == multiplayer.get_unique_id():
		_receive_character(character.data, levels)
	elif peer_id in multiplayer.get_peers() and connected:
		_receive_character.rpc_id(peer_id, character.data, levels)


@rpc("authority", "reliable")
func _receive_character(d: Dictionary, levels: int) -> void:
	var c := CharacterData.new()
	c.data = d.duplicate(true)
	c.seal()  # mudança legítima, vinda do servidor
	character = c
	if is_local():
		Session.character = c
		SaveSystem.request_character_save(c)
	character_changed.emit(levels)


## Servidor: a ficha mudou por fora (troca entre jogadores): recalcula e propaga.
func refresh_character() -> void:
	_apply_character()
	_push_character(0)


## Servidor: muda a ficha e propaga (XP, ouro, loot…). Retorna níveis ganhos.
func grant(xp: int, gold: int, items: Array = []) -> Array:
	var leftover := []
	var levels := character.add_xp(xp) if xp > 0 else 0
	character.data.gold = int(character.data.gold) + maxi(gold, 0)
	for item: Dictionary in items:
		if not character.add_item(item):
			leftover.append(item)
	_apply_character()
	_push_character(levels)
	return leftover


# --- Pedidos do inventário (validados no servidor) -------------------------------

func request_spend_point(attr: String) -> void:
	_rpc_or_local(&"_spend_point", [attr])


func request_equip(index: int) -> void:
	_rpc_or_local(&"_equip", [index])


func request_unequip(slot_name: String) -> void:
	_rpc_or_local(&"_unequip", [slot_name])


func request_use(index: int) -> void:
	_rpc_or_local(&"_use", [index])


func _rpc_or_local(method: StringName, args: Array) -> void:
	if multiplayer.is_server():
		callv(method, args)
	else:
		rpc_id.callv([1, method] + args)


func _from_owner() -> bool:
	if not multiplayer.is_server() or character == null:
		return false
	var sender := multiplayer.get_remote_sender_id()
	return sender == 0 or sender == peer_id


@rpc("any_peer", "reliable")
func _spend_point(attr: String) -> void:
	if _from_owner() and character.spend_point(attr):
		_apply_character()
		_push_character(0)


@rpc("any_peer", "reliable")
func _equip(index: int) -> void:
	if _from_owner() and character.equip_from_bag(index):
		_apply_character()
		_push_character(0)


@rpc("any_peer", "reliable")
func _unequip(slot_name: String) -> void:
	if _from_owner() and character.unequip(slot_name):
		_apply_character()
		_push_character(0)


## Usar um item da bolsa: equipamento equipa; poção bebe.
@rpc("any_peer", "reliable")
func _use(index: int) -> void:
	if not _from_owner() or index < 0 or index >= character.data.inventory.size():
		return
	var item: Variant = character.data.inventory[index]
	if item == null:
		return
	if item.kind == Items.EQUIPMENT:
		_equip(index)
	elif item.kind == Items.CONSUMABLE:
		_drink(item.id)


## Poções de vida e de recurso dividem uma recarga (13-balanceamento.md 5.3).
## A Poção Elemental troca o elemento (sem recarga; 02-0-elementos.md, seção 4).
func _drink(id: String) -> void:
	if not alive or character == null or not GameData.consumables.has(id):
		return
	var def: Dictionary = GameData.consumables[id]
	if def.restore == "element":
		if character.count_of(id) > 0 and character.drink_elemental(def.element) and character.take_one(id):
			_apply_character()
			_push_character(0)
		return
	if potion_cooldown > 0.0:
		return
	if def.restore == "health" and health >= max_health:
		return
	if def.restore == "resource" and resource >= max_resource:
		return
	if not character.take_one(id):
		return
	if def.restore == "health":
		health = minf(health + max_health * def.fraction, max_health)
	else:
		resource = minf(resource + max_resource * def.fraction, max_resource)
	potion_cooldown = def.cooldown
	_push_character(0)


## Atalho da Poção Elemental: bebe a primeira da bolsa de outro elemento.
func _drink_next_elemental() -> void:
	if character == null:
		return
	for item: Variant in character.data.inventory:
		if item == null or item.kind != Items.CONSUMABLE:
			continue
		var def: Dictionary = GameData.consumables.get(item.id, {})
		if def.get("restore", "") == "element" and def.element != character.current_element():
			_drink(item.id)
			return


func _physics_process(delta: float) -> void:
	if is_local():
		_send_local_input(delta)
	if multiplayer.is_server():
		_server_step(delta)
		net_position = global_position
	else:
		_follow_server()
	_tick_visual(delta)


func _follow_server() -> void:
	if net_position != _last_net_position:
		_last_net_position = net_position
		_snapshots.push(net_position)
	global_position = _snapshots.sample()


func _send_local_input(delta: float) -> void:
	var viewport := get_viewport()
	_local_input = PlayerInput.gather(_local_input,
		global_position + Vector3.UP * PROJECTILE_HEIGHT, viewport.get_camera_3d(), viewport)
	if _local_input.aim != Vector2.ZERO and InputDevice.using_gamepad and Settings.aim_assist:
		_local_input.aim = _assisted_aim(_local_input.aim, data.basic_attack.range)
	if multiplayer.is_server():
		_input = _local_input
		return
	# Movimento e mira a ~30 Hz; apertos e solturas saem na hora (07-rede.md).
	_input_timer -= delta
	var buttons_changed := _local_input.attack_presses != _sent_input.attack_presses \
		or _local_input.attack_releases != _sent_input.attack_releases \
		or _local_input.evade_presses != _sent_input.evade_presses \
		or _local_input.interact_held != _sent_input.interact_held \
		or _local_input.skill_presses != _sent_input.skill_presses
	if buttons_changed or _input_timer <= 0.0:
		_input_timer = 1.0 / GameData.balance.net.input_rate_hz
		_sent_input = _local_input
		_submit_input.rpc_id(1, _local_input.to_array())


@rpc("any_peer", "unreliable_ordered")
func _submit_input(packed: Array) -> void:
	if multiplayer.get_remote_sender_id() != peer_id:
		return
	_input = PlayerInput.from_array(packed)


# --- Simulação (servidor) ---------------------------------------------------

func _server_step(delta: float) -> void:
	var input := _input
	var attack_pressed := input.attack_presses != _seen.attack_presses
	var attack_released := input.attack_releases != _seen.attack_releases
	var evade_pressed := input.evade_presses != _seen.evade_presses
	_seen = input
	if not alive:
		_seen_extra = input
		velocity = Vector3.ZERO
		return

	_attack_cooldown = maxf(_attack_cooldown - delta, 0.0)
	_tick_skills(delta)
	evade_cooldown = maxf(evade_cooldown - delta, 0.0)
	potion_cooldown = maxf(potion_cooldown - delta, 0.0)
	var regen: float = character.resource_regen() if character else data.resource_regen
	# Foco do Arqueiro: regenera bem mais devagar andando (02-2-arqueiro.md, seção 4).
	if data.has("resource_regen_moving") and input.move.length() > 0.2:
		regen *= float(data.resource_regen_moving) / float(data.resource_regen)
	resource = minf(resource + regen * delta, max_resource)
	if input.potion_health_presses != _seen_extra.potion_health_presses:
		_drink("potion_health")
	if input.potion_resource_presses != _seen_extra.potion_resource_presses:
		_drink("potion_resource")
	if input.potion_elemental_presses != _seen_extra.potion_elemental_presses:
		_drink_next_elemental()
	var mount_pressed := input.mount_presses != _seen_extra.mount_presses
	var skill_pressed: Array[int] = []
	for i in 4:
		if input.skill_presses[i] != _seen_extra.skill_presses[i]:
			skill_pressed.append(i)
	if input.interact_presses != _seen_extra.interact_presses:
		get_tree().call_group(&"arena", &"request_pickup", self, false)
	if input.pickup_all_presses != _seen_extra.pickup_all_presses:
		get_tree().call_group(&"arena", &"request_pickup", self, true)
	_seen_extra = input

	if _evade_time > 0.0:
		_evade_time -= delta
		var evade: Dictionary = data.evade
		velocity = Vector3(_evade_dir.x, 0, _evade_dir.y) * (evade.distance / evade.duration)
		move_and_slide()
		return

	var aim := input.aim
	if aim == Vector2.ZERO and input.move.length() > 0.2:
		aim = input.move.normalized()
	if aim != Vector2.ZERO:
		facing = aim.normalized()

	_update_mount(delta, mount_pressed)
	var desired := Vector3(input.move.x, 0, input.move.y) * move_speed * speed_mult()
	if mounted:
		# Cavalo: acelera e faz curvas mais abertas (inércia).
		velocity = velocity.move_toward(desired, float(data.mount.acceleration) * delta)
	else:
		velocity = desired
	move_and_slide()
	global_position.y = 0.0
	if data.has("momentum"):
		_update_momentum(delta)
	for i in skill_pressed:
		_cast_slot(i)

	if evade_pressed and evade_cooldown <= 0.0:
		_evade_dir = input.move.normalized() if input.move.length() > 0.2 else facing
		_evade_time = data.evade.duration
		evade_cooldown = data.evade.cooldown
		charge_time = 0.0
		if data.evade.get("teleport", false):
			# Ninja: a esquiva é um teleporte curto (sem atravessar paredes).
			var to := global_position + Vector3(_evade_dir.x, 0, _evade_dir.y) * float(data.evade.distance)
			teleport_to(get_parent().skills._ray_limited(self, global_position, to))
			_evade_dir = Vector2.ZERO
		return

	# Toque: ataque básico na hora. Segurando por charge_time e soltando: ataque forte.
	if attack_pressed and _attack_cooldown <= 0.0:
		_fire(data.basic_attack)
		_attack_cooldown = data.basic_attack.cooldown / speed_mult()
	if input.attack_held:
		charge_time += delta
	if attack_released or (not input.attack_held and charge_time > 0.0):
		if charge_time >= data.strong_attack.charge_time:
			_fire(data.strong_attack)
		charge_time = 0.0


## O dono caiu: o herói fica parado, sem entrada, e não leva dano.
func set_disconnected() -> void:
	connected = false
	_input = PlayerInput.new()
	_seen = PlayerInput.new()
	charge_time = 0.0


## Copia o estado de um herói que esperava o dono voltar.
func take_over(old: Player) -> void:
	if old.character:
		set_character(old.character)
	health = old.health
	resource = old.resource
	alive = old.alive
	facing = old.facing


func wants_to_revive() -> bool:
	return alive and connected and _input.interact_held


func is_charged() -> bool:
	return charge_time >= data.strong_attack.charge_time


func evade_cooldown_left() -> float:
	return evade_cooldown


func is_invulnerable() -> bool:
	return _evade_time > 0.0 or not connected


## Dano de um monstro; a armadura reduz conforme o nível dele (13-balanceamento.md 2.3).
func take_damage(amount: float, monster_level := 1) -> void:
	if not multiplayer.is_server() or not alive or is_invulnerable():
		return
	# Evasão do Ninja: desvia do golpe inteiro (e recupera Energia com a passiva).
	if character and _rng_dodge.randf() < character.evasion_chance():
		resource = minf(resource + character.passive_value("evasion", "resource_on_dodge", "_none"), max_resource)
		_show_dodge()
		return
	if character:
		amount *= 1.0 - character.damage_reduction(monster_level)
	# Corpo de Ferro: menos dano por alguns segundos; Armadura Pesada sempre.
	amount *= 1.0 - float(_buffs.get("iron_body", {}).get("value", 0.0))
	if character:
		amount *= 1.0 - character.passive_value("heavy_armor")
	# Pele de Pedra absorve primeiro.
	if shield > 0.0:
		var absorbed := minf(shield, amount)
		shield -= absorbed
		amount -= absorbed
	# Escudo de Mana: parte do dano sai da mana (1 de mana absorve 2 de dano).
	if character and amount > 0.0:
		var share := character.passive_value("mana_shield")
		if share > 0.0:
			var per_mana := character.passive_value("mana_shield", "damage_per_mana", "_none")
			var from_mana := minf(amount * share, resource * per_mana)
			resource -= from_mana / per_mana
			amount -= from_mana
	health = maxf(health - amount, 0.0)
	hurt.emit()
	if amount >= max_health * GameData.balance.heavy_hit_fraction:
		if peer_id == multiplayer.get_unique_id():
			_heavy_hit()
		elif peer_id in multiplayer.get_peers():
			_heavy_hit.rpc_id(peer_id)
	if health <= 0.0:
		alive = false
		charge_time = 0.0
		revive_progress = 0.0
		downed.emit()


func revive(fraction: float) -> void:
	alive = true
	health = max_health * fraction
	revive_progress = 0.0


## Volta ao começo da área com tudo cheio (checkpoint).
func reset_at(spot: Vector3) -> void:
	global_position = spot
	net_position = spot
	alive = true
	health = max_health
	resource = max_resource
	revive_progress = 0.0
	charge_time = 0.0
	_evade_time = 0.0
	evade_cooldown = 0.0


func _show_dodge() -> void:
	_dodge_text.rpc()


@rpc("authority", "call_local", "unreliable")
func _dodge_text() -> void:
	var label := Label3D.new()
	label.text = tr("HUD_DODGED")
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.font_size = 56
	label.outline_size = 8
	label.modulate = Color(0.8, 0.9, 1.0)
	add_child(label)
	label.position = Vector3.UP * 2.3
	var tween := label.create_tween()
	tween.tween_property(label, "modulate:a", 0.0, 0.6)
	tween.tween_callback(label.queue_free)


@rpc("authority", "call_local", "reliable")
func _heavy_hit() -> void:
	InputDevice.vibrate(0.4, 0.8, 0.25)


func _fire(attack: Dictionary) -> void:
	if attack.get("melee", false):
		_melee(attack)
		return
	var dir := Vector3(facing.x, 0, facing.y)
	get_tree().call_group(&"arena", &"spawn_projectile", {
		"position": global_position + Vector3.UP * PROJECTILE_HEIGHT + dir * 0.6,
		"direction": dir,
		"speed": attack.projectile_speed,
		"range": attack.range,
		"radius": attack.radius,
		"pierce": attack.pierce,
		"damage": power * attack.power_pct * damage_mult(),
		"color": Elements.color(element),
		# O ataque forte aplica o estado básico do elemento (02-0-elementos.md 5.3).
		"element": element,
		"state": String(Elements.data(element).get("basic_state", "")) if attack.get("applies_state", false) \
			else ("burning" if _buffs.has("damage") else ""),  # Bênção das Chamas: golpes queimam
		"crit_chance": character.crit_chance() if character else GameData.elements.crit_chance,
		"crit_mult": character.crit_mult() if character else GameData.elements.crit_mult,
	})


# --- Habilidades -----------------------------------------------------------------

func _cast_slot(index: int) -> void:
	if not alive or character == null or _evade_time > 0.0:
		return
	var key: String = character.data.skill_slots[index]
	if key == "" or float(_skill_cd.get(key, 0.0)) > 0.0:
		return
	var id := character.skill_of(key)
	var rank := character.skill_rank(key)
	var skill := Skills.def(id)
	if rank <= 0 or not Skills.is_active(id):
		return
	var cost := float(skill.get("cost", 0.0))
	if resource < cost or not get_parent().skills.cast(self, id, rank):
		return
	resource -= cost
	# Sem recarga (as básicas) ainda respeitam o ritmo do ataque básico.
	var cd := maxf(Skills.cooldown(skill, rank), data.basic_attack.cooldown)
	_skill_cd[key] = cd
	charge_time = 0.0
	if is_local():
		_skill_used(key, cd)
	elif peer_id in multiplayer.get_peers():
		_skill_used.rpc_id(peer_id, key, cd)


@rpc("authority", "reliable")
func _skill_used(key: String, cd: float) -> void:
	skill_cd_view[key] = cd


func skill_cooldown_left(key: String) -> float:
	return float(skill_cd_view.get(key, 0.0))


func _tick_skills(delta: float) -> void:
	for key: String in _skill_cd.keys():
		_skill_cd[key] -= delta
		if _skill_cd[key] <= 0.0:
			_skill_cd.erase(key)
	for id: String in _buffs.keys():
		_buffs[id].time -= delta
		if _buffs[id].time <= 0.0:
			_buffs.erase(id)
	if _shield_time > 0.0:
		_shield_time -= delta
		if _shield_time <= 0.0:
			shield = 0.0
	hidden = _buffs.has("hidden")


## Bônus de aliado (renova, não soma): "damage" (Bênção das Chamas), "speed" (Vento a Favor).
func add_buff(id: String, value: float, duration: float) -> void:
	_buffs[id] = {"value": maxf(value, float(_buffs.get(id, {}).get("value", 0.0))), "time": duration}


func consume_buff(id: String) -> void:
	_buffs.erase(id)


## Acertou um crítico: o Ninja recupera Energia (02-4-ninja.md, seção 5).
func on_crit() -> void:
	resource = minf(resource + float(data.get("resource_per_crit", 0.0)), max_resource)


func add_shield(amount: float, duration: float) -> void:
	shield = maxf(shield, amount)
	_shield_time = duration


func heal(amount: float) -> void:
	if alive:
		health = minf(health + amount, max_health)


func teleport_to(spot: Vector3) -> void:
	global_position = Vector3(spot.x, 0, spot.z)
	net_position = global_position


## Dano a mais: Bênção das Chamas / Fogueira / Selo do Fogo, Domínio Elemental e
## o próximo golpe depois do Passo Sombrio.
func damage_mult() -> float:
	var mastery := character.passive_value("mastery") if character else 0.0
	var mult := (1.0 + float(_buffs.get("damage", {}).get("value", 0.0))) * (1.0 + mastery) \
		* (1.0 + float(_buffs.get("next_hit", {}).get("value", 0.0)))
	if data.has("mount"):
		if not mounted:
			mult *= float(data.get("foot_damage_mult", 1.0))  # Cavaleiro a pé: -25%
		elif character:
			# Ímpeto Inabalável: até +20% conforme a velocidade do cavalo.
			mult *= 1.0 + character.passive_value("unstoppable") * clampf(velocity.length() / maxf(move_speed, 0.1), 0.0, 1.0)
	return mult


## Domínio Elemental: estados duram mais.
func state_duration_mult() -> float:
	return 1.0 + (character.passive_value("mastery", "duration_value", "duration_per_rank") if character else 0.0)


## Vento a Favor: anda e ataca mais rápido.
func speed_mult() -> float:
	return 1.0 + float(_buffs.get("speed", {}).get("value", 0.0))


## Pedidos da janela de habilidades (validados no servidor).
func request_learn(key: String) -> void:
	_rpc_or_local(&"_learn", [key])


func request_slot(index: int, key: String) -> void:
	_rpc_or_local(&"_set_slot", [index, key])


@rpc("any_peer", "reliable")
func _learn(key: String) -> void:
	if _from_owner() and character.learn(key):
		_apply_character()
		_push_character(0)


@rpc("any_peer", "reliable")
func _set_slot(index: int, key: String) -> void:
	if _from_owner() and character.set_slot(index, key):
		_push_character(0)


# --- Cavaleiro: cavalo e Ímpeto ------------------------------------------------------

## Áreas estreitas desmontam sozinhas; ao sair, o cavalo volta depois de um assobio.
## O botão de montar alterna (não monta dentro de área estreita).
func _update_mount(delta: float, pressed: bool) -> void:
	if not data.has("mount"):
		return
	var narrow: bool = get_parent().has_method("is_narrow") and get_parent().is_narrow(global_position)
	if pressed:
		if mounted:
			_set_mounted(false)
			_manual_dismount = true
		elif not narrow:
			_manual_dismount = false
			_set_mounted(true)
	if mounted and narrow:
		_set_mounted(false)
		_remount_timer = float(data.mount.remount_delay)
	elif not mounted and not narrow and not _manual_dismount:
		_remount_timer -= delta
		if _remount_timer <= 0.0:
			_set_mounted(true)


func _set_mounted(value: bool) -> void:
	if mounted == value:
		return
	mounted = value
	velocity = Vector3.ZERO
	move_speed = GameData.balance.base_move_speed * _speed_pct() / 100.0 \
		* (1.0 + (character.move_speed_bonus() if character else 0.0))


## Ímpeto: enche galopando, cai parado (02-3-cavaleiro.md, seção 5).
func _update_momentum(delta: float) -> void:
	var rules: Dictionary = data.momentum
	var speed := velocity.length()
	var change := 0.0
	if mounted and speed > move_speed * 0.8:
		change = float(rules.gallop)
	elif speed < 0.2:
		change = float(rules.idle)
	resource = clampf(resource + change * delta, 0.0, max_resource)


## Golpe acertado: o Cavaleiro ganha Ímpeto (+5 montado, +8 a pé).
func on_hit() -> void:
	if data.has("momentum"):
		var gain := float(data.momentum.hit_mounted if mounted else data.momentum.hit_foot)
		resource = minf(resource + gain, max_resource)


## Ataque de perto (Ninja, Cavaleiro): cortes/estocadas à frente ou, no forte,
## corte giratório (Ninja) ou avanço com a lança baixada (Cavaleiro montado).
func _melee(attack: Dictionary) -> void:
	var hit := {
		"damage": power * attack.power_pct * damage_mult(),
		"element": element,
		"state": String(Elements.data(element).get("basic_state", "")) if attack.get("applies_state", false) \
			else ("burning" if _buffs.has("damage") else ""),
		"crit_chance": character.crit_chance() if character else GameData.elements.crit_chance,
		"crit_mult": character.crit_mult() if character else GameData.elements.crit_mult,
	}
	consume_buff("next_hit")
	if attack.has("lunge") and mounted:
		var dir := Vector3(facing.x, 0, facing.y)
		teleport_to(get_parent().skills._ray_limited(self, global_position, global_position + dir * float(attack.lunge)))
	get_parent().skills.melee_strike(self, hit, attack.range, attack.get("arc", 360.0), attack.get("spin", false))


## Mira assistida leve: puxa para o inimigo mais próximo dentro do cone.
func _assisted_aim(aim: Vector2, attack_range: float) -> Vector2:
	var best := aim
	var best_dist := INF
	for enemy in get_tree().get_nodes_in_group(&"enemies"):
		var offset := Vector2(enemy.global_position.x - global_position.x,
			enemy.global_position.z - global_position.z)
		var dist := offset.length()
		if dist > attack_range or dist < 0.01 or dist >= best_dist:
			continue
		if absf(aim.angle_to(offset)) <= AIM_ASSIST_ANGLE:
			best = offset.normalized()
			best_dist = dist
	return best


# --- Visual (todos os PCs) ----------------------------------------------------

func _add_synchronizer() -> void:
	var config := SceneReplicationConfig.new()
	var always := [":net_position", ":facing", ":charge_time", ":revive_progress", ":evade_cooldown"]
	var on_change := [":health", ":max_health", ":resource", ":max_resource", ":alive", ":connected",
		":hero_name", ":level", ":equip_visual", ":potion_cooldown", ":armor_value", ":element", ":shield", ":hidden", ":mounted"]
	for prop in always + on_change:
		var path := NodePath("." + prop)
		config.add_property(path)
		config.property_set_spawn(path, true)
		config.property_set_replication_mode(path, SceneReplicationConfig.REPLICATION_MODE_ALWAYS
			if prop in always else SceneReplicationConfig.REPLICATION_MODE_ON_CHANGE)
	var sync := MultiplayerSynchronizer.new()
	sync.name = "Sync"
	sync.replication_config = config
	# Estado a ~20 Hz (07-rede.md, seção 5).
	var interval: float = 1.0 / GameData.balance.net.state_rate_hz
	sync.replication_interval = interval
	sync.delta_interval = interval
	add_child(sync)


func _build_visual() -> void:
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 1.8
	shape.shape = capsule
	_body_shape = capsule
	shape.position.y = 0.9
	add_child(shape)

	# Placeholder até os modelos modulares: corpo de "roupa de baixo de pano"
	# (cor crua), cajado simples com cristal e o caderno de anotações.
	_visual = Node3D.new()
	add_child(_visual)
	_body_material = _material(BODY_COLOR)
	var body := MeshInstance3D.new()
	var body_mesh := CapsuleMesh.new()
	body_mesh.radius = 0.35
	body_mesh.height = 1.7
	body.mesh = body_mesh
	body.material_override = _body_material
	body.position.y = 0.85
	_visual.add_child(body)

	var archer := class_id == "archer"
	var ninja := class_id == "ninja"
	var summoner := class_id == "summoner"
	var knight := class_id == "knight"
	_body_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA  # invisível (Bomba de Fumaça)
	# Arma: cajado (Mago) ou arco (Arqueiro), na cor do material equipado.
	var staff := MeshInstance3D.new()
	var staff_mesh := CylinderMesh.new()
	staff_mesh.top_radius = 0.02 if ninja else (0.03 if archer else 0.04)
	staff_mesh.bottom_radius = 0.03 if ninja else (0.03 if archer else 0.05)
	staff_mesh.height = 0.5 if ninja else (1.3 if archer else 1.7)
	staff.mesh = staff_mesh
	_staff_material = _material(Color(0.35, 0.22, 0.12))
	staff.material_override = _staff_material
	staff.position = Vector3(0.45, 0.9, 0.35) if archer else Vector3(0.45, 0.9, 0.15)
	if archer:
		staff.rotation.z = 0.15
		staff.rotation.x = -0.25
	if knight:
		# Lança longa apontada para a frente e escudo no braço esquerdo.
		staff_mesh.top_radius = 0.02
		staff_mesh.bottom_radius = 0.04
		staff_mesh.height = 2.6
		staff.position = Vector3(0.4, 1.05, 0.7)
		staff.rotation.x = PI / 2.0
		var shield_node := MeshInstance3D.new()
		var shield_mesh := BoxMesh.new()
		shield_mesh.size = Vector3(0.08, 0.7, 0.5)
		shield_node.mesh = shield_mesh
		shield_node.material_override = _material(Color(0.45, 0.32, 0.2))
		shield_node.position = Vector3(-0.42, 1.0, 0.15)
		_visual.add_child(shield_node)
		_horse = _build_horse()
		_visual.add_child(_horse)
	if summoner:
		# Livro dos Amigos aberto na mão (a capa na cor do material).
		staff.mesh = BoxMesh.new()
		(staff.mesh as BoxMesh).size = Vector3(0.36, 0.06, 0.28)
		staff.position = Vector3(0.38, 1.0, 0.35)
	if ninja:
		# Par de adagas, uma em cada mão, apontando para a frente.
		staff.position = Vector3(0.42, 0.9, 0.35)
		staff.rotation.x = PI / 2.0
		var second := MeshInstance3D.new()
		second.mesh = staff_mesh
		second.material_override = _staff_material
		second.position = Vector3(-0.42, 0.9, 0.35)
		second.rotation.x = PI / 2.0
		_visual.add_child(second)
	_visual.add_child(staff)

	# Brilho na cor do elemento: cristal do cajado ou ponta da flecha (02-0-elementos.md, seção 8).
	_crystal_material = _material(Color(0.55, 0.75, 1.0), 1.5)
	var crystal := MeshInstance3D.new()
	var crystal_mesh := SphereMesh.new()
	crystal_mesh.radius = 0.06 if archer else 0.1
	crystal_mesh.height = 0.12 if archer else 0.2
	crystal.mesh = crystal_mesh
	crystal.material_override = _crystal_material
	crystal.position = Vector3(0.42, 0.9, 0.62) if ninja else (Vector3(0.45, 0.95, 0.6) if archer else Vector3(0.45, 1.8, 0.15))
	if knight:
		crystal.position = Vector3(0.4, 1.05, 2.0)  # ponta da lança
	if summoner:
		crystal.position = Vector3(0.38, 1.08, 0.35)  # página brilhando no livro
	_visual.add_child(crystal)

	# Mago: caderno de anotações; Arqueiro: aljava nas costas.
	var notebook := MeshInstance3D.new()
	var notebook_mesh := BoxMesh.new()
	notebook_mesh.size = Vector3(0.18, 0.6, 0.18) if archer else Vector3(0.22, 0.28, 0.06)
	notebook.mesh = notebook_mesh
	notebook.material_override = _material(Color(0.4, 0.28, 0.18))
	notebook.position = Vector3(-0.2, 1.2, -0.3) if archer else Vector3(-0.32, 0.95, 0.12)
	if summoner:
		# Pássaro amigo no ombro.
		notebook_mesh.size = Vector3(0.16, 0.14, 0.24)
		notebook.position = Vector3(-0.28, 1.72, 0.0)
	if knight:
		# Fita da princesa / broche real no peito.
		notebook_mesh.size = Vector3(0.14, 0.14, 0.04)
		notebook.position = Vector3(0.12, 1.35, 0.33)
	if ninja:
		# Guarda da espada do pai, presa na cintura.
		notebook_mesh.size = Vector3(0.2, 0.06, 0.2)
		notebook.position = Vector3(-0.3, 0.9, 0.0)
	_visual.add_child(notebook)

	_build_gear()

	# Anel no chão com a cor do jogador.
	var ring := MeshInstance3D.new()
	var ring_mesh := TorusMesh.new()
	ring_mesh.inner_radius = 0.5
	ring_mesh.outer_radius = 0.62
	ring.mesh = ring_mesh
	var ring_material := _material(SLOT_COLORS[slot], 1.0)
	ring_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	ring.material_override = ring_material
	ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	ring.position.y = 0.03
	add_child(ring)
	_ring_material = ring_material

	# Barra de reanimação sobre o caído.
	_revive_bar = MeshInstance3D.new()
	var bar_mesh := BoxMesh.new()
	bar_mesh.size = Vector3(1.0, 0.08, 0.08)
	_revive_bar.mesh = bar_mesh
	var bar_material := _material(Color(0.4, 1.0, 0.5), 2.0)
	bar_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bar_material.no_depth_test = true
	_revive_bar.material_override = bar_material
	_revive_bar.position.y = 1.4
	_revive_bar.visible = false
	add_child(_revive_bar)


func _tick_visual(delta: float) -> void:
	if _horse:
		# Montado: o herói sobe no cavalo e o corpo (hitbox) fica maior.
		_horse.visible = mounted
		_visual.position.y = 0.6 if mounted else 0.0
		_body_shape.radius = 0.75 if mounted else 0.4
	for key: String in skill_cd_view.keys():
		skill_cd_view[key] -= delta
		if skill_cd_view[key] <= 0.0:
			skill_cd_view.erase(key)
	if alive:
		var target := atan2(facing.x, facing.y)
		_visual.rotation.y = lerp_angle(_visual.rotation.y, target, minf(TURN_SPEED * delta, 1.0))
		_visual.rotation.x = 0.0
		_visual.position.y = 0.0
	else:
		_visual.rotation.x = -PI / 2.0
		_visual.position.y = 0.3
	if health < _shown_health:
		_flash = 0.15
	if health != _shown_health:
		_shown_health = health
		health_changed.emit(health, max_health)
	if not is_equal_approx(resource, _shown_resource):
		_shown_resource = resource
		resource_changed.emit(resource, max_resource)
	if equip_visual != _shown_visual:
		_update_gear()
	_flash = maxf(_flash - delta, 0.0)
	_body_material.albedo_color = Color(1, 0.35, 0.35) if _flash > 0.0 else BODY_COLOR
	_body_material.albedo_color.a = 0.3 if hidden else 1.0
	# Cristal na cor do elemento (muda na hora com a Poção Elemental); brilha
	# mais quando o ataque forte está carregado.
	var crystal_color := Elements.color(element)
	if _crystal_material.albedo_color != crystal_color:
		_crystal_material.albedo_color = crystal_color
		_crystal_material.emission = crystal_color
	_crystal_material.emission_energy_multiplier = 4.0 if is_charged() else 1.5
	# Dono desconectado: anel cinza enquanto o herói espera.
	_ring_material.albedo_color = SLOT_COLORS[slot] if connected else Color(0.4, 0.4, 0.4)
	_revive_bar.visible = not alive and revive_progress > 0.0
	_revive_bar.scale.x = maxf(revive_progress, 0.01)


## Cada peça aparece no corpo na cor do material (05-itens-e-loot.md: tudo que
## é equipado aparece no herói); slot vazio mostra a roupa de baixo.
func _build_gear() -> void:
	var hat := CylinderMesh.new()
	hat.top_radius = 0.02
	hat.bottom_radius = 0.34
	hat.height = 0.45
	var robe := CylinderMesh.new()
	robe.top_radius = 0.33
	robe.bottom_radius = 0.45
	robe.height = 1.1
	var glove := SphereMesh.new()
	glove.radius = 0.11
	glove.height = 0.22
	var boot := BoxMesh.new()
	boot.size = Vector3(0.16, 0.14, 0.28)
	var parts := {
		"head": [[hat, Vector3(0, 1.82, 0)]],
		"body": [[robe, Vector3(0, 0.6, 0)]],
		"hands": [[glove, Vector3(0.36, 0.95, 0.12)], [glove, Vector3(-0.36, 0.95, 0.12)]],
		"feet": [[boot, Vector3(0.13, 0.07, 0.06)], [boot, Vector3(-0.13, 0.07, 0.06)]],
	}
	for slot_name in parts:
		var material := StandardMaterial3D.new()
		var nodes: Array[MeshInstance3D] = []
		for part in parts[slot_name]:
			var mesh := MeshInstance3D.new()
			mesh.mesh = part[0]
			mesh.position = part[1]
			mesh.material_override = material
			mesh.visible = false
			_visual.add_child(mesh)
			nodes.append(mesh)
		_gear[slot_name] = {"material": material, "nodes": nodes}


func _update_gear() -> void:
	_shown_visual = equip_visual.duplicate()
	for slot_name in _gear:
		var material_id: String = equip_visual.get(slot_name, "")
		var shown := material_id != "" and GameData.materials.has(material_id)
		for node: MeshInstance3D in _gear[slot_name].nodes:
			node.visible = shown
		if shown:
			_gear[slot_name].material.albedo_color = Color(GameData.materials[material_id].color)
	var weapon: String = equip_visual.get("weapon", "wood")
	_staff_material.albedo_color = Color(GameData.materials.get(weapon, GameData.materials.wood).color)


## Cavalo placeholder: corpo, pescoço, cabeça e quatro patas.
func _build_horse() -> Node3D:
	var horse := Node3D.new()
	var coat := _material(Color(0.32, 0.22, 0.14))
	var parts := [
		[Vector3(0.6, 0.6, 1.6), Vector3(0, 0.95, 0)],
		[Vector3(0.3, 0.6, 0.3), Vector3(0, 1.4, 0.75)],
		[Vector3(0.28, 0.3, 0.55), Vector3(0, 1.7, 1.0)],
		[Vector3(0.15, 0.7, 0.15), Vector3(0.22, 0.35, 0.6)],
		[Vector3(0.15, 0.7, 0.15), Vector3(-0.22, 0.35, 0.6)],
		[Vector3(0.15, 0.7, 0.15), Vector3(0.22, 0.35, -0.6)],
		[Vector3(0.15, 0.7, 0.15), Vector3(-0.22, 0.35, -0.6)],
	]
	for part in parts:
		var mesh := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = part[0]
		mesh.mesh = box
		mesh.material_override = coat
		mesh.position = part[1] - Vector3(0, 0.6, 0)  # o herói sobe 0,6 m quando montado
		horse.add_child(mesh)
	return horse


static func _material(color: Color, emission := 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	if emission > 0.0:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = emission
	return m
