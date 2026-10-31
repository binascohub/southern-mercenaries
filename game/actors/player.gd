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
## Arma no punho (osso da mão do Universal Animation Library: Y segue os dedos).
## Cajado, arco e livro: o cabo sai do punho para cima, de pé ao lado do corpo
## quando o herói está parado. Lança e adagas: apontam para a frente.
const HAND_GRIP := Transform3D(Basis(Vector3.RIGHT, deg_to_rad(150.0)), Vector3(0, 0.08, 0))
const POINT_GRIP := Transform3D(Basis(Vector3.RIGHT, deg_to_rad(60.0)), Vector3(0, 0.08, 0))
## Altura do osso do peito (spine_03) na pose de descanso.
const CHEST := Vector3(0, 1.315, 0)

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
## Corpo masculino ou feminino (vem com o herói ao nascer; não muda).
var sex := "male"
## Última ação para a animação nos PCs ("tipo:número"): melee, cast, shoot, roll, hit.
var action := ""
## Cavaleiro montado (02-3-cavaleiro.md, seção 3).
var mounted := false
## Pátio de treino com "recursos e recargas livres" (servidor).
var free_cooldowns := false
## Segurando o bloqueio (escudo, barreira ou aparar do Ninja).
var blocking := false
## Aura do refino (05-1-refino.md, seção 5): refino da arma, elemento de origem
## (não muda com a Poção Elemental) e conjunto de armadura todo em +4.
var aura_level := 0
var origin_element := "fire"
var aura_set := false

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
## Empurrão em andamento (velocidade e tempo restante; servidor).
var _knock := Vector3.ZERO
var _knock_time := 0.0
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
var _horse_material: StandardMaterial3D
var _block_visual: MeshInstance3D
var _aura: MeshInstance3D
var _aura_material: StandardMaterial3D
## Bloqueio (servidor): quando apertou (para o aparar) e o que sobra da barreira do Mago.
var _block_pressed_ms := -100000
var _barrier_left := 0.0

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
## Corpo animado (manequim do Universal Animation Library) e a última ação mostrada.
var _model: HeroModel
var _shown_action := ""
var _last_visual_pos := Vector3.ZERO
var _action_seq := 0
var _crystal_material: StandardMaterial3D
var _revive_bar: MeshInstance3D
var _ring_material: StandardMaterial3D
var _staff_material: StandardMaterial3D
## Peças equipadas no corpo (placeholder até os modelos modulares).
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
	player.sex = spawn.get("sex", "male")
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
	origin_element = String(character.data.get("element", "fire"))
	aura_level = character.aura_level()
	aura_set = character.armor_set_refined()


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


## Dono: uma dica do tutorial foi mostrada; o servidor guarda na ficha.
@rpc("any_peer", "reliable")
func request_tip_seen(id: String) -> void:
	if not multiplayer.is_server() or character == null:
		return
	var sender := multiplayer.get_remote_sender_id()
	if sender != peer_id and not (sender == 0 and is_local()):
		return
	if character.mark_tip_seen(id):
		_push_character(0)


## Servidor: marca uma ação para a animação em todos os PCs (ataque, magia,
## esquiva, golpe sofrido). Um golpe sofrido não corta um ataque em andamento.
func act(kind: String) -> void:
	if kind == "hit" and _model and _model.current() in ["melee", "cast", "shoot", "roll", "knockback"]:
		return
	_action_seq += 1
	action = "%s:%d" % [kind, _action_seq]


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
	if def.restore == "return_portal":
		# Patuá de Retorno: abre o portal no chão (só nos mapas).
		if character.count_of(id) > 0 and get_parent().open_return_charm(self) and character.take_one(id):
			_push_character(0)
		return
	if def.restore == "element":
		if character.count_of(id) > 0 and character.drink_elemental(def.element) and character.take_one(id):
			_apply_character()
			_push_character(0)
		return
	if def.restore not in ["health", "resource"]:
		return  # pergaminhos e cristais não se bebem (refino é no ferreiro)
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
	act("drink")
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
		or _local_input.skill_presses != _sent_input.skill_presses \
		or _local_input.block_held != _sent_input.block_held
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
	var block_pressed := input.block_presses != _seen_extra.block_presses
	var skill_pressed: Array[int] = []
	for i in 4:
		if input.skill_presses[i] != _seen_extra.skill_presses[i]:
			skill_pressed.append(i)
	if input.interact_presses != _seen_extra.interact_presses:
		get_tree().call_group(&"arena", &"request_interact", self)
	if input.pickup_all_presses != _seen_extra.pickup_all_presses:
		get_tree().call_group(&"arena", &"request_pickup", self, true)
	_seen_extra = input

	if _knock_time > 0.0:
		_knock_time -= delta
		velocity = _knock
		move_and_slide()
		global_position.y = 0.0
		return

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
	_update_block(delta, block_pressed)
	if blocking:
		charge_time = 0.0
		return  # bloqueando não ataca nem usa habilidade
	for i in skill_pressed:
		_cast_slot(i)

	if evade_pressed and evade_cooldown <= 0.0:
		_evade_dir = input.move.normalized() if input.move.length() > 0.2 else facing
		_evade_time = data.evade.duration
		evade_cooldown = data.evade.cooldown
		charge_time = 0.0
		act("roll")
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
func take_damage(amount: float, monster_level := 1, attacker: Node3D = null) -> void:
	if not multiplayer.is_server() or not alive or is_invulnerable():
		return
	if _try_parry(attacker):
		return
	# Evasão do Ninja: desvia do golpe inteiro (e recupera Energia com a passiva).
	if character and _rng_dodge.randf() < character.evasion_chance():
		resource = minf(resource + character.passive_value("evasion", "resource_on_dodge", "_none"), max_resource)
		_show_dodge()
		return
	if character:
		amount *= 1.0 - character.damage_reduction(monster_level, mounted)
	# Corpo de Ferro: menos dano por alguns segundos; Armadura Pesada sempre.
	amount *= 1.0 - float(_buffs.get("iron_body", {}).get("value", 0.0))
	if character:
		amount *= 1.0 - character.passive_value("heavy_armor")
	amount -= _blocked(amount, attacker)
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
	if amount > 0.0:
		act("hit")
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
	_float_text.rpc("HUD_DODGED")


@rpc("authority", "call_local", "unreliable")
func _float_text(key: String) -> void:
	var label := Label3D.new()
	label.text = tr(key)
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
	act("melee" if attack.get("melee", false) else ("shoot" if class_id == "archer" else "cast"))
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
	act("melee" if class_id in ["ninja", "knight"] else ("shoot" if class_id == "archer" else "cast"))
	# Sem recarga (as básicas) ainda respeitam o ritmo do ataque básico; no pátio
	# de treino com recargas livres, todas ficam assim.
	var cd := maxf(Skills.cooldown(skill, rank), data.basic_attack.cooldown)
	if free_cooldowns:
		cd = data.basic_attack.cooldown
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


## Empurrão (a Rajada das Asas da Rainha): `offset` metros em `time` s, sem
## controle. Quem está na esquiva escapa (servidor).
func knock_back(offset: Vector3, time: float) -> void:
	if not multiplayer.is_server() or not alive or _evade_time > 0.0 or is_invulnerable():
		return
	_knock = offset / maxf(time, 0.05)
	_knock_time = time
	act("knockback")


func is_knocked_back() -> bool:
	return _knock_time > 0.0


func teleport_to(spot: Vector3) -> void:
	global_position = Vector3(spot.x, 0, spot.z)
	net_position = global_position


## Troca o cilindro provisório pela arma do kit (de pé, com o meio na origem, como
## o cilindro); as partes de metal ficam na cor do material equipado.
func _dress_weapon(holder: MeshInstance3D, piece_name: String, offset := Vector3.ZERO) -> void:
	var weapon := Kit.piece(piece_name)
	if weapon == null:
		return
	holder.mesh = null
	holder.add_child(weapon)
	weapon.position = offset
	for node in weapon.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for i in mesh.get_surface_override_material_count():
			var source := mesh.get_active_material(i)
			if source and String(source.resource_name) == "Silver":
				mesh.set_surface_override_material(i, _staff_material)


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


# --- Bloqueio (02-personagens.md, "Ações básicas"; detalhes em cada classe) ---------

## Segurar o bloqueio: Mago e Invocador erguem uma barreira (gasta o recurso por
## dano), o Cavaleiro ergue o escudo (gasta Ímpeto por segundo), o Ninja apara.
## O Arqueiro não bloqueia.
func _update_block(delta: float, pressed: bool) -> void:
	var rules: Dictionary = data.get("block", {})
	if rules.is_empty() or not alive:
		blocking = false
		return
	if pressed:
		_block_pressed_ms = Time.get_ticks_msec()
		_barrier_left = max_health * float(rules.get("max_fraction", 0.0))
	blocking = _input.block_held
	if blocking and rules.has("drain_per_second"):
		resource = maxf(resource - float(rules.drain_per_second) * delta, 0.0)
		if resource <= 0.0:
			blocking = false


## O golpe vem da frente do herói (o bloqueio só pega golpes frontais).
func _is_frontal(attacker: Node3D) -> bool:
	if attacker == null or not is_instance_valid(attacker):
		return false
	var to := Vector2(attacker.global_position.x - global_position.x, attacker.global_position.z - global_position.z)
	return to.length() < 0.01 or facing.normalized().dot(to.normalized()) > 0.2


## Aparar no tempo certo (Ninja): anula o golpe e contra-ataca com crítico garantido.
func _try_parry(attacker: Node3D) -> bool:
	var rules: Dictionary = data.get("block", {})
	if not rules.has("parry_window") or not blocking or not (attacker is Enemy) or not _is_frontal(attacker):
		return false
	if Time.get_ticks_msec() - _block_pressed_ms > float(rules.parry_window) * 1000.0:
		return false
	var hit := {
		"damage": power * float(rules.counter_power) * damage_mult(),
		"element": element,
		"state": String(Elements.data(element).get("basic_state", "")),
		"crit_chance": 1.0,
		"crit_mult": character.crit_mult() if character else GameData.elements.crit_mult,
	}
	get_parent().skills._strike(self, attacker, hit)
	_float_text.rpc("HUD_PARRIED")
	return true


## Parte do golpe que o bloqueio segura (e o custo em recurso).
func _blocked(amount: float, attacker: Node3D) -> float:
	var rules: Dictionary = data.get("block", {})
	if not blocking or rules.is_empty() or not _is_frontal(attacker):
		return 0.0
	var blocked := amount * float(rules.get("reduction", 0.0))
	if rules.has("max_fraction"):
		blocked = minf(blocked, _barrier_left)
		_barrier_left -= blocked
	if rules.has("resource_per_damage"):
		var per := float(rules.resource_per_damage)
		blocked = minf(blocked, resource / per)
		resource -= blocked * per
	return blocked


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
		":hero_name", ":level", ":equip_visual", ":potion_cooldown", ":armor_value", ":element", ":shield", ":hidden", ":mounted", ":blocking", ":action",
		":aura_level", ":origin_element", ":aura_set"]
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
	_model = HeroModel.new()
	_visual.add_child(_model)
	_model.setup(sex, data.get("look", {}).get(sex, {}))

	var archer := class_id == "archer"
	var ninja := class_id == "ninja"
	var summoner := class_id == "summoner"
	var knight := class_id == "knight"
	# Arma: cajado (Mago) ou arco (Arqueiro), na cor do material equipado.
	var staff := MeshInstance3D.new()
	var staff_mesh := CylinderMesh.new()
	staff_mesh.top_radius = 0.02 if ninja else (0.03 if archer else 0.04)
	staff_mesh.bottom_radius = 0.03 if ninja else (0.03 if archer else 0.05)
	staff_mesh.height = 0.6 if ninja else (1.3 if archer else 1.7)
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
		staff_mesh.height = 2.4
		staff.position = Vector3(0.4, 1.05, 0.7)
		staff.rotation.x = PI / 2.0
		var shield_node := MeshInstance3D.new()
		var shield_mesh := BoxMesh.new()
		shield_mesh.size = Vector3(0.08, 0.7, 0.5)
		shield_node.mesh = shield_mesh
		shield_node.material_override = _material(Color(0.45, 0.32, 0.2))
		# No antebraço esquerdo, alinhado ao corpo na pose de descanso.
		_model.attach("lowerarm_l", shield_node, Transform3D(Basis(Vector3(0, 1, 0), Vector3(-1, 0, 0), Vector3(0, 0, 1)),
			Vector3(0.0, 0.15, 0.08)), Vector3(-0.42, 1.0, 0.15))
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
		second.rotation = Vector3.ZERO
		second.position = Vector3(0, 0.15, 0)
		_dress_weapon(second, "Weapon_Shortsword")
		var left_hand := Node3D.new()
		left_hand.add_child(second)
		_model.attach("hand_l", left_hand, POINT_GRIP, Vector3(-0.42, 0.9, 0.35))
	# Arma na mão direita: o cabo passa pelo punho, apontando para a frente
	# (o punho segura a um terço do cabo; a lança e o arco mais à frente).
	staff.rotation = Vector3.ZERO
	staff.position = Vector3.ZERO if summoner else Vector3(0, staff_mesh.height * (0.3 if knight else 0.2), 0)
	# Armas do Kingdom Weapon Set: cajado (Mago), alabarda (Cavaleiro), espadas curtas (Ninja).
	if class_id == "mage":
		_dress_weapon(staff, "Weapon_Staff")
	elif knight:
		_dress_weapon(staff, "Weapon_Polearm")
	elif ninja:
		_dress_weapon(staff, "Weapon_Shortsword")
	elif archer:
		_dress_weapon(staff, "Bow_Long")  # arco longo (Archery Set, yd, CC0)
	var right_hand := Node3D.new()
	right_hand.add_child(staff)
	_model.attach("hand_r", right_hand, POINT_GRIP if knight or ninja else HAND_GRIP, Vector3(0.45, 0.9, 0.15))

	# Brilho na cor do elemento: cristal do cajado ou ponta da flecha (02-0-elementos.md, seção 8).
	_crystal_material = _material(Color(0.55, 0.75, 1.0), 1.5)
	var crystal := MeshInstance3D.new()
	var crystal_mesh := SphereMesh.new()
	crystal_mesh.radius = 0.06 if archer else 0.1
	crystal_mesh.height = 0.12 if archer else 0.2
	crystal.mesh = crystal_mesh
	crystal.material_override = _crystal_material
	# Na ponta da arma (cajado, flecha, lança, adaga) ou na página do livro.
	crystal.position = Vector3(0, 0.08, 0) if summoner else Vector3(0, staff_mesh.height / 2.0, 0)
	staff.add_child(crystal)

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
	if archer:
		# Aljava de couro com flechas (Archery Set): a base fica embaixo do centro da caixa.
		_dress_weapon(notebook, "Quiver", Vector3(0, -0.45, 0))
	# Preso ao peito (acompanha o corpo nas animações).
	_model.attach("spine_03", notebook, Transform3D(Basis(), notebook.position - CHEST), notebook.position)


	# Aura do refino: cilindro transparente em volta do herói (sem luz extra).
	_aura = MeshInstance3D.new()
	var aura_mesh := CylinderMesh.new()
	aura_mesh.top_radius = 0.75
	aura_mesh.bottom_radius = 0.9
	aura_mesh.height = 2.0
	aura_mesh.cap_top = false
	aura_mesh.cap_bottom = false
	_aura.mesh = aura_mesh
	_aura_material = StandardMaterial3D.new()
	_aura_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_aura_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_aura_material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	_aura_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	_aura.material_override = _aura_material
	_aura.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_aura.position.y = 1.0
	_aura.visible = false
	_visual.add_child(_aura)

	# Bloqueio: barreira (ou o escudo erguido) à frente do herói.
	if data.has("block"):
		_block_visual = MeshInstance3D.new()
		var barrier := BoxMesh.new()
		barrier.size = Vector3(1.3, 1.5, 0.08)
		_block_visual.mesh = barrier
		var barrier_material := StandardMaterial3D.new()
		barrier_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		barrier_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		barrier_material.albedo_color = Color(0.85, 0.85, 1.0, 0.3)
		_block_visual.material_override = barrier_material
		_block_visual.position = Vector3(0, 1.0, 0.75)
		_block_visual.visible = false
		_visual.add_child(_block_visual)

	# Anel no chão com a cor do jogador.
	var ring := MeshInstance3D.new()
	var ring_mesh := TorusMesh.new()
	ring_mesh.inner_radius = 0.5
	ring_mesh.outer_radius = 0.62
	ring.mesh = ring_mesh
	var ring_material := _material(SLOT_COLORS[slot % SLOT_COLORS.size()], 1.0)
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
	# Animação: velocidade vista na tela (igual em todos os PCs) e ações novas.
	var moved := global_position - _last_visual_pos
	moved.y = 0.0
	_last_visual_pos = global_position
	var speed := moved.length() / maxf(delta, 0.0001)
	if action != _shown_action:
		_shown_action = action
		if action != "":
			_model.play_action(action.get_slice(":", 0))
	_model.update_state(speed, alive, mounted, charge_time > 0.15, blocking)
	if _block_visual:
		_block_visual.visible = blocking
	# Aura: +1 brilho fraco nos pés … +5 aura máxima pulsando; cor do elemento de origem.
	_aura.visible = aura_level > 0
	if aura_level > 0:
		var pulse := 1.0
		if aura_level >= 4:
			pulse = 0.75 + 0.25 * sin(Time.get_ticks_msec() / (180.0 if aura_level == 5 else 320.0))
		var c := Elements.color(origin_element)
		_aura_material.albedo_color = Color(c.r, c.g, c.b, 0.07 * aura_level * pulse)
		var height := 0.2 + 0.4 * aura_level
		_aura.scale = Vector3(1.0, height / 2.0, 1.0)
		_aura.position.y = height / 2.0
	if _horse:
		# Barda do cavalo na cor do material; sem barda, pelagem e sela simples.
		var barding: Variant = equip_visual.get("barding")
		_horse_material.albedo_color = Color(GameData.materials[barding].color) if barding != null \
			and GameData.materials.has(barding) else Color(0.32, 0.22, 0.14)
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
		_visual.position.y = 0.6 if mounted and _horse else 0.0
	elif _model.skeleton:
		_visual.position.y = 0.0  # a animação de queda deita o corpo
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
	# Pisca ao levar golpe, fica translúcido invisível (Bomba de Fumaça) e o
	# conjunto de armadura em +4 brilha na cor do elemento de origem.
	_model.set_effects(_flash > 0.0, 0.3 if hidden else 1.0, Elements.color(origin_element) if aura_set else Color(0, 0, 0, 0))
	# Cristal na cor do elemento (muda na hora com a Poção Elemental); brilha
	# mais quando o ataque forte está carregado.
	var crystal_color := Elements.color(element)
	if _crystal_material.albedo_color != crystal_color:
		_crystal_material.albedo_color = crystal_color
		_crystal_material.emission = crystal_color
	_crystal_material.emission_energy_multiplier = 4.0 if is_charged() else 1.5
	# Dono desconectado: anel cinza enquanto o herói espera.
	_ring_material.albedo_color = SLOT_COLORS[slot % SLOT_COLORS.size()] if connected else Color(0.4, 0.4, 0.4)
	_revive_bar.visible = not alive and revive_progress > 0.0
	_revive_bar.scale.x = maxf(revive_progress, 0.01)


## Cada peça aparece no corpo (05-itens-e-loot.md: tudo que é equipado
## aparece no herói), tingida pela cor do material; a arma também.
func _update_gear() -> void:
	_shown_visual = equip_visual.duplicate()
	_model.set_outfit(equip_visual)
	var weapon: String = equip_visual.get("weapon", "wood")
	_staff_material.albedo_color = Color(GameData.materials.get(weapon, GameData.materials.wood).color)


## Cavalo placeholder: corpo, pescoço, cabeça e quatro patas.
func _build_horse() -> Node3D:
	var horse := Node3D.new()
	var coat := _material(Color(0.32, 0.22, 0.14))
	_horse_material = coat
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
