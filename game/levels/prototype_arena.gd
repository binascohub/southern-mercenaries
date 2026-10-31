# Southern Mercenaries — GPL-3.0-or-later
extends Node3D
## Área de teste: sala inicial (checkpoint), corredor e duas câmaras, com
## monstros posicionados em grupos de encontro que dormem até um jogador chegar
## perto (03-inimigos.md, "Encontros por exploração"; nada de ondas). A
## geometria vem de data/arenas.json e é gerada aqui como placeholder até os
## mapas feitos à mão.
##
## Rede: o servidor (host, ou este PC no solo) decide encontros, quedas, revive
## e checkpoint; os MultiplayerSpawners replicam jogadores, monstros e
## projéteis nos outros PCs, inclusive para quem entra no meio da partida.
##
## Áreas (Fase 6): a mesma cena carrega qualquer área de data/arenas.json pelo
## nome — Tortuga (Rua Principal e porto), a Taverna e, por enquanto, esta área
## de teste no papel do Esgoto. Viajar (porta da Taverna, bueiro, portal de
## retorno) troca a área de todos os PCs sem trocar de cena: o servidor manda
## _load_area e os heróis continuam os mesmos nós. Objetos da área ("props"):
## lojas, NPCs, saídas e placas; o Town cuida de missões, lojas e conversas.
##
## Mapas (Fase 7, 03-2-areas.md): o Esgoto de Tortuga em 4 áreas, cada uma com
## checkpoint na entrada, segredos (baús escondidos), poças de lodo, elites e,
## no fim, a saída para a próxima área — que só leva o grupo quando todos estão
## perto (ou o host confirma, com contagem). Só a área final ("final") termina
## em vitória; a área de teste ("replayable") pode ser jogada de novo.
##
## RPG (Fase 3): o XP de cada monstro é dividido entre os jogadores presentes;
## o loot é sorteado e mostrado por jogador (cada um vê só o seu) e a coleta é
## validada no servidor. A campanha (grupos mortos) fica no PC do host.

const ARENA_ID := "prototype_arena"
## Distância para interagir com um objeto da área (loja, NPC, porta).
const PROP_REACH := 2.8
const MAIN_SCENE := "res://game/main/main.tscn"
const WALL_HEIGHT := 2.5
const DOOR_WIDTH := 6.0
const FLOOR_COLOR := Color(0.18, 0.17, 0.16)
const WALL_COLOR := Color(0.28, 0.25, 0.23)
## Onde cada jogador surge em relação ao host (entrar no meio: "ao lado do host").
const SLOT_OFFSETS: Array[Vector3] = [Vector3(0, 0, 0), Vector3(1.6, 0, 0), Vector3(-1.6, 0, 0), Vector3(0, 0, 1.6)]
## Ponto de checkpoint na entrada da área (03-2-areas.md).
const CHECKPOINT := Vector3(0, 0, 3)
const ENCOUNTER_CHECK_INTERVAL := 0.2
const CHECKPOINT_DELAY := 3.0
## Ouro no chão é recolhido sozinho a esta distância (proposta).
const GOLD_AUTO_PICKUP := 1.6
const LOOT_SCATTER := 1.2
## Miniatura da campanha: primeira captura logo depois de entrar, depois a cada minuto.
const THUMB_FIRST := 3.0
const THUMB_INTERVAL := 60.0

enum Result { NONE, VICTORY, DEFEAT }

## Um jogador que caiu voltou e assumiu o mesmo herói (só no servidor).
signal hero_resumed(peer_id: int)

var arena: Dictionary = {}
## Área carregada agora (id em data/arenas.json).
var area_id := ""
var local_player: Player
## Missões, lojas e conversas da cidade.
var town: Town
# Estado da partida (decidido no servidor, espelhado nos clientes).
var cleared := 0
var total_encounters := 0
var result := Result.NONE
var finished := false

var _players_spawner: MultiplayerSpawner
var _enemy_spawner: MultiplayerSpawner
var _projectile_spawner: MultiplayerSpawner
var _companion_spawner: MultiplayerSpawner
var _camera: TopDownCamera
var _inventory: InventoryMenu
## Habilidades (efeitos no servidor, visual em todos os PCs).
var skills: SkillSystem
## Troca entre jogadores (lógica no servidor) e a janela deste PC.
var trade: Trade
var _trade_menu: TradeMenu
var _skill_menu: SkillMenu
var _shop_menu: ShopMenu
var _dialogue_menu: DialogueMenu
var _training_menu: TrainingMenu
var _portal_menu: PortalMenu
var _stash_menu: StashMenu
var _journal_menu: JournalMenu
var _forge_menu: ForgeMenu
var _opening_menu: OpeningMenu
## Dicas do tutorial: olha o jogo e avisa o TipManager (14-tutorial.md, seção 4).
var tips: TipWatcher
var _bestiary_menu: BestiaryMenu
## Aumenta a cada reinício; timers da partida anterior são ignorados.
var _run := 0
## Grupos de encontro (servidor): id -> {position, awake, members}.
var _groups := {}
var _encounter_timer := 0.0
## Campanha deste host (11-saves.md): grupos mortos não voltam. Vazia nos
## clientes (mesmo depois de desconectados, quando o Godot os trata como servidor).
var _campaign: Dictionary = {}
## Loot no chão (servidor): id -> {client, peer, position, item, gold}.
var _loot := {}
var _next_loot_id := 1
var _rng := RandomNumberGenerator.new()
## Nós de loot deste PC (só os do jogador local).
var _loot_nodes := {}
## Reanimação em andamento: caído -> quem está reanimando.
var _revivers := {}
## Quem foi atingido reanimando precisa soltar o botão antes de tentar de novo.
var _interrupted: Array[Player] = []
## Heróis esperando o dono que caiu: client_id -> Player (07-rede.md, seção 9).
var _held := {}
var _thumb_timer := THUMB_FIRST
## Áreas dos combos Lama e Vapor (servidor): [{position, radius, time, state}].
var _zones: Array[Dictionary] = []
## Poças tóxicas e avisos de golpe no chão (Fase 7).
var hazards: Hazards
## Mapa que se revela (servidor): máscara da área atual e o próximo passo.
var _explored := PackedByteArray()
var _explore_timer := 0.0
## Saída em grupo: contagem do host em andamento (id da saída) e em que partida.
var _exit_countdown := ""
## Nós da área atual (paredes, chão, luzes, objetos), trocados a cada viagem.
var _area_root: Node3D
var _props: Array[Dictionary] = []
## Objeto ao alcance do herói deste PC (aviso de interagir) e suas marcas "!".
var _prop_markers := {}
## Pátio de treino (04-tortuga-e-missoes.md, seção 5.2): painel do grupo
## {total, biggest, crits, hits, start_ms, last_ms} e quem ligou "recursos livres".
var training := {}
var _training_free := {}

@onready var hud: Hud = $Hud
@onready var pause_menu: PauseMenu = $PauseMenu


func _ready() -> void:
	add_to_group(&"arena")
	_area_root = Node3D.new()
	_area_root.name = "Area"
	add_child(_area_root)
	hazards = Hazards.new()
	hazards.name = "Hazards"
	hazards.root = _area_root
	add_child(hazards)
	_build_spawners()
	town = Town.new()
	town.name = "Town"
	add_child(town)
	town.state_changed.connect(_refresh_markers)
	town.state_changed.connect(_refresh_visitors)
	_camera = TopDownCamera.new()
	add_child(_camera)
	_camera.snap()
	_inventory = InventoryMenu.new()
	add_child(_inventory)
	skills = SkillSystem.new()
	skills.name = "Skills"
	add_child(skills)
	trade = Trade.new()
	trade.name = "Trade"
	add_child(trade)
	_trade_menu = TradeMenu.new()
	add_child(_trade_menu)
	_trade_menu.bind(trade, hud)
	_inventory.trade_requested.connect(trade.request_trade)
	_skill_menu = SkillMenu.new()
	add_child(_skill_menu)
	_inventory.skills_requested.connect(_skill_menu.toggle)
	_shop_menu = ShopMenu.new()
	add_child(_shop_menu)
	_shop_menu.bind(town)
	_dialogue_menu = DialogueMenu.new()
	add_child(_dialogue_menu)
	_dialogue_menu.bind(town)
	var training_layer := CanvasLayer.new()
	training_layer.layer = 6
	add_child(training_layer)
	_training_menu = TrainingMenu.new()
	training_layer.add_child(_training_menu)
	_training_menu.bind(self, town)
	_portal_menu = PortalMenu.new()
	training_layer.add_child(_portal_menu)
	_portal_menu.bind(town)
	_journal_menu = JournalMenu.new()
	training_layer.add_child(_journal_menu)
	_journal_menu.bind(town)
	_inventory.journal_requested.connect(_journal_menu.show_journal)
	_bestiary_menu = BestiaryMenu.new()
	training_layer.add_child(_bestiary_menu)
	_bestiary_menu.bind(town)
	_stash_menu = StashMenu.new()
	add_child(_stash_menu)
	_stash_menu.bind(town)
	_forge_menu = ForgeMenu.new()
	add_child(_forge_menu)
	_forge_menu.bind(town)
	_opening_menu = OpeningMenu.new()
	add_child(_opening_menu)
	_opening_menu.bind(town)
	tips = TipWatcher.new()
	tips.name = "Tips"
	add_child(tips)
	tips.bind(self)
	InputDevice.gamepad_lost.connect(_on_gamepad_lost)
	InputDevice.gamepad_restored.connect(_on_gamepad_restored)
	NetworkManager.session_ended.connect(_on_session_ended)
	NetworkManager.peer_joined.connect(_on_peer_joined)
	NetworkManager.peer_left.connect(_on_peer_left)

	if NetworkManager.mode == NetworkManager.Mode.NONE:
		NetworkManager.prepare_solo()  # cena aberta direto (editor ou testes)
	NetworkManager.begin()
	if NetworkManager.mode == NetworkManager.Mode.NONE:
		return  # falhou ao abrir; _on_session_ended volta ao menu
	if NetworkManager.mode == NetworkManager.Mode.HOST:
		hud.show_hosting(NetworkManager.local_addresses())
	if multiplayer.is_server():
		_rng.randomize()
		if Session.campaign.is_empty():
			Session.continue_or_new_campaign()
		_campaign = Session.campaign
		var start_area: String = _campaign.get("area", ARENA_ID)
		if not GameData.arenas.has(start_area):
			start_area = ARENA_ID
		_load_area(start_area, "")
		_spawn_player(multiplayer.get_unique_id())
		_start_run()
		town.sync()
		_add_dynamic_props()
	else:
		hud.show_connecting(true)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"menu") and not pause_menu.is_open and not _inventory.visible \
			and not _trade_menu.is_open() and not _skill_menu.visible and not _shop_menu.visible \
			and not _dialogue_menu.visible and not _training_menu.visible and not _portal_menu.visible \
			and not _stash_menu.visible and not _journal_menu.visible and not _bestiary_menu.visible \
			and not _forge_menu.visible and not _opening_menu.visible:
		pause_menu.open(not NetworkManager.is_online())
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed(&"map") and not Session.ui_open:
		hud.minimap.toggle_large()
		get_viewport().set_input_as_handled()
	elif result == Result.VICTORY and arena.get("replayable", false) and event.is_action_pressed(&"attack"):
		if multiplayer.is_server():
			_restart_area()
		else:
			_request_restart.rpc_id(1)


func _physics_process(delta: float) -> void:
	# Nos mapas a área segue viva depois da vitória (reanimar, ouro, tesouro);
	# a área de teste para, esperando o recomeço.
	var running: bool = result == Result.NONE or (result == Result.VICTORY and not arena.get("replayable", false))
	if multiplayer.is_server() and running:
		_update_revives(delta)
		_encounter_timer -= delta
		if _encounter_timer <= 0.0:
			_encounter_timer = ENCOUNTER_CHECK_INTERVAL
			_update_encounters()
			_auto_pickup_gold()
		_update_zones(delta)
		_update_training()
	hud.set_boss(_awake_boss())
	_update_minimap_marks()
	if multiplayer.is_server():
		_update_explored(delta)
	if local_player and is_instance_valid(local_player):
		hud.set_training(training if in_training(local_player.global_position) else {})
		var near := prop_near(local_player)
		var name_key: String = near.get("name_key", GameData.npcs.get(near.get("npc", ""), {}).get("name_key", ""))
		hud.set_interact_prompt(tr(name_key) if not near.is_empty() else "")
	if not _campaign.is_empty():
		_campaign.played_seconds = float(_campaign.get("played_seconds", 0)) + delta
		_update_thumbnail(delta)


# --- Spawners -----------------------------------------------------------------

func _build_spawners() -> void:
	_players_spawner = _spawner("PlayerSpawner", Player.create)
	_enemy_spawner = _spawner("EnemySpawner", _create_enemy)
	_projectile_spawner = _spawner("ProjectileSpawner", Projectile.create)
	_companion_spawner = _spawner("CompanionSpawner", Companion.create)
	_players_spawner.spawned.connect(_on_node_spawned)


func _spawner(node_name: String, function: Callable) -> MultiplayerSpawner:
	var spawner := MultiplayerSpawner.new()
	spawner.name = node_name
	add_child(spawner)
	spawner.spawn_path = spawner.get_path_to(self)
	spawner.spawn_function = function
	return spawner


func _create_enemy(spawn: Dictionary) -> Enemy:
	var enemy := Enemy.create(spawn)
	if multiplayer.is_server():
		enemy.died.connect(_on_enemy_died)
		enemy.disturbed.connect(func(e: Enemy) -> void: _wake_group(e.group))
	return enemy


## Combo que mexe com quem está em volta (só no servidor, 02-0-elementos.md 7):
## Incêndio passa o fogo para os vizinhos; Lama e Vapor deixam uma área no chão.
func element_combo(at: Vector3, result: Dictionary) -> void:
	if not multiplayer.is_server():
		return
	var combo: Dictionary = GameData.elements.combos.get(result.combo, {})
	if result.spread_dps > 0.0:
		for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
			var d := e.global_position.distance_to(at)
			if d > 0.01 and d <= float(combo.get("radius", 3.0)):
				Elements.apply_state(e.status, "burning", e.element, e.is_boss(), result.spread_dps)
	if not result.zone.is_empty():
		var zone := {"position": at, "radius": float(result.zone.radius),
			"time": float(result.zone.duration), "state": String(result.zone.state)}
		_zones.append(zone)
		_show_zone.rpc(zone.state, at, zone.radius, zone.time)


func _update_zones(delta: float) -> void:
	for zone in _zones.duplicate():
		zone.time -= delta
		if zone.time <= 0.0:
			_zones.erase(zone)
			continue
		for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
			if Vector2(e.global_position.x - zone.position.x, e.global_position.z - zone.position.z).length() <= zone.radius:
				Elements.apply_state(e.status, zone.state, e.element, e.is_boss())


## Disco translúcido da área (todos os PCs), some sozinho.
@rpc("authority", "call_local", "reliable")
func _show_zone(state_id: String, at: Vector3, radius: float, duration: float) -> void:
	var disc := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = 0.04
	mesh.radial_segments = 24
	disc.mesh = mesh
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	var c := Elements.state_color(state_id)
	material.albedo_color = Color(c.r, c.g, c.b, 0.35)
	disc.material_override = material
	disc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(disc)
	disc.global_position = Vector3(at.x, 0.03, at.z)
	get_tree().create_timer(duration, false).timeout.connect(disc.queue_free)


# --- Patuá de Retorno (04-tortuga-e-missoes.md, seção 5.1) ---------------------------

## Abre no chão, por 15 s, um portal de volta a Tortuga (só nos mapas). Retorna
## false se não deu (o patuá não é gasto).
func open_return_charm(player: Player) -> bool:
	if not multiplayer.is_server() or arena.get("town", false) or not prop_near(player, "exit", "charm_portal", 50.0).is_empty():
		_toast_to(player, "TOAST_CHARM_NOT_HERE", {})
		return false
	_reach_checkpoint(str(_campaign.get("checkpoint", "start")))  # ponto de volta para o Macumbeiro
	var prop := {"id": "charm_portal", "kind": "exit", "look": "charm_portal", "name_key": "PROP_CHARM_PORTAL",
		"position": [player.global_position.x, player.global_position.z + 1.5], "to": "tortuga",
		"entry": "start", "expedition_end": true}
	_add_prop.rpc(prop)
	var area_now := area_id
	var time: float = GameData.consumables.return_charm.get("portal_time", 15.0)
	get_tree().create_timer(time, false).timeout.connect(func() -> void:
		if area_id == area_now:
			_remove_prop.rpc("charm_portal"))
	return true


@rpc("authority", "call_local", "reliable")
func _add_prop(prop: Dictionary) -> void:
	_build_prop(prop)


@rpc("authority", "call_local", "reliable")
func _remove_prop(id: String) -> void:
	_props = _props.filter(func(p: Dictionary) -> bool: return p.id != id)
	var node := _area_root.get_node_or_null(id)
	if node:
		node.queue_free()


# --- Pátio de treino ---------------------------------------------------------------

## O ponto fica no pátio de treino (sala marcada "training").
func in_training(at: Vector3) -> bool:
	for room: Dictionary in arena.get("rooms", []):
		if room.get("training", false):
			var half := Vector2(room.size[0], room.size[1]) / 2.0
			if absf(at.x - room.center[0]) <= half.x and absf(at.z - room.center[1]) <= half.y:
				return true
	return false


## Golpe num boneco (chamado pelo boneco no servidor): soma no painel do grupo.
func on_dummy_hit(amount: float, crit: bool) -> void:
	if not multiplayer.is_server():
		return
	var now := Time.get_ticks_msec()
	if int(training.get("hits", 0)) == 0:
		training.start_ms = now
	training.total = float(training.get("total", 0.0)) + amount
	training.biggest = maxf(float(training.get("biggest", 0.0)), amount)
	training.crits = int(training.get("crits", 0)) + int(crit)
	training.hits = int(training.get("hits", 0)) + 1
	training.last_ms = now
	_set_training.rpc(training)


func reset_training() -> void:
	training = {"total": 0.0, "biggest": 0.0, "crits": 0, "hits": 0, "start_ms": 0, "last_ms": 0}
	if multiplayer.is_server():
		_set_training.rpc(training)


@rpc("authority", "call_local", "unreliable_ordered")
func _set_training(stats: Dictionary) -> void:
	training = stats


## Pedidos do quadro de treino (qualquer PC; o servidor confere se está no pátio).
func request_training(action: String) -> void:
	if multiplayer.is_server():
		_rpc_training(action)
	else:
		_rpc_training.rpc_id(1, action)


@rpc("any_peer", "reliable")
func _rpc_training(action: String) -> void:
	if not multiplayer.is_server():
		return
	var sender := multiplayer.get_remote_sender_id()
	var peer := sender if sender != 0 else multiplayer.get_unique_id()
	var player := get_node_or_null(str(peer)) as Player
	if player == null or not in_training(player.global_position):
		return
	match action:
		"reset_stats":
			reset_training()
		"reset_dummies":
			for e: Enemy in get_tree().get_nodes_in_group(&"enemies"):
				if e.data.get("dummy", false):
					e.health = e.max_health
					e.status.clear()
			reset_training()
		"toggle_free":
			_training_free[peer] = not _training_free.get(peer, false)
			_toast_to(player, "TRAINING_FREE_ON" if _training_free[peer] else "TRAINING_FREE_OFF", {})


## Recursos e recargas livres no pátio: vida, recurso e recargas voltam ao máximo.
func _update_training() -> void:
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		var free: bool = _training_free.get(p.peer_id, false) and p.alive and in_training(p.global_position)
		p.free_cooldowns = free
		if free:
			p.health = p.max_health
			p.resource = p.max_resource


## Área estreita (corredores marcados "narrow"): o Cavaleiro desmonta (02-3-cavaleiro.md, seção 3).
func is_narrow(at: Vector3) -> bool:
	if arena.get("narrow", false):
		return true
	for room: Dictionary in arena.get("rooms", []):
		if not room.get("narrow", false):
			continue
		var half := Vector2(room.size[0], room.size[1]) / 2.0
		if absf(at.x - room.center[0]) <= half.x and absf(at.z - room.center[1]) <= half.y:
			return true
	return false


## Animal amigo do Invocador (só no servidor; o spawner cria nos outros PCs).
func spawn_companion(spawn: Dictionary) -> Node:
	return _companion_spawner.spawn(spawn) if multiplayer.is_server() else null


## Projétil que explode (Bola de Fogo), chamado pelo grupo "arena".
func skill_burst(at: Vector3, radius: float, hit: Dictionary) -> void:
	if multiplayer.is_server():
		skills.burst(at, radius, hit)


## Chamado pelo grupo "arena" quando um jogador atira (só no servidor).
func spawn_projectile(spawn: Dictionary) -> void:
	if multiplayer.is_server():
		_projectile_spawner.spawn(spawn)


func _spawn_player(peer_id: int, resume: Player = null) -> Player:
	var used: Array[int] = []
	var host: Player = null
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p != resume:
			used.append(p.slot)
		if p.peer_id == 1:
			host = p
	var slot := 0
	while slot in used:
		slot += 1
	var origin := host.global_position if host else entry_point(str(_campaign.get("checkpoint", "start")))
	var position := origin + SLOT_OFFSETS[slot % SLOT_OFFSETS.size()]
	if resume:
		slot = resume.slot
		position = resume.global_position
	var character := resume.character if resume and resume.character \
		else NetworkManager.character_of(peer_id)
	if character == null:
		character = CharacterData.create(arena.player_class, "male", "?")
	var player: Player = _players_spawner.spawn({
		"peer_id": peer_id, "slot": slot, "class_id": character.data.class_id,
		"position": position, "name": character.data.name, "level": character.data.level,
		"sex": character.data.get("sex", "male"),
		"visual": character.equipment_visual(),
		"element": character.current_element(),
	})
	if resume == null and character.is_edited():
		# Ficha mudada fora do jogo: só avisa, nunca bloqueia (11-saves.md, seção 5).
		push_warning("Ficha editada fora do jogo: %s" % character.data.name)
		_toast_all.call_deferred("TOAST_CHARACTER_EDITED", {"name": character.data.name})
	player.set_character(character)
	if not _campaign.is_empty():
		if character.data.id not in _campaign.get("participants", []):
			_campaign.participants = _campaign.get("participants", []) + [character.data.id]
		# Nomes para a lista de campanhas (os personagens dos clientes não estão neste PC).
		var names: Dictionary = _campaign.get("hero_names", {})
		names[character.data.id] = character.data.name
		_campaign.hero_names = names
	player.downed.connect(_on_player_downed)
	player.hurt.connect(_on_player_hurt.bind(player))
	_on_node_spawned(player)
	if resume == null:
		town.send_opening.call_deferred(peer_id)
	return player


func _on_node_spawned(node: Node) -> void:
	if node is Player and node.is_local():
		local_player = node
		_camera.target = node
		_camera.snap()
		hud.bind_player(node)
		_inventory.bind_player(node)
		_trade_menu.bind_player(node)
		_skill_menu.bind_player(node)
		_shop_menu.bind_player(node)
		_stash_menu.bind_player(node)
		_forge_menu.bind_player(node)
		hud.show_connecting(false)


func _on_peer_joined(peer_id: int) -> void:
	_load_area.rpc_id(peer_id, area_id, "")
	town.sync(peer_id)
	_set_explored.rpc_id(peer_id, area_id, ExploreMap.encode(_explored))
	_add_dynamic_props(peer_id)
	var held: Player = _held.get(NetworkManager.client_id_of(peer_id))
	if is_instance_valid(held):
		# Voltou dentro do prazo: assume o mesmo herói (vida, lugar, cor).
		_held.erase(NetworkManager.client_id_of(peer_id))
		var player := _spawn_player(peer_id, held)
		player.take_over(held)
		held.queue_free()
		_reassign_loot(NetworkManager.client_id_of(peer_id), peer_id)
		hero_resumed.emit(peer_id)
	else:
		_spawn_player(peer_id)
	_set_state.rpc_id(peer_id, cleared, result)


func _on_peer_left(peer_id: int, dropped: bool) -> void:
	var player: Player = get_node_or_null(str(peer_id))
	if player == null:
		return
	var client := NetworkManager.client_id_of(peer_id)
	if dropped and client != "":
		# Caiu: o herói espera 30 s parado e invulnerável.
		player.set_disconnected()
		_held[client] = player
		var hero: WeakRef = weakref(player)
		get_tree().create_timer(GameData.balance.drop_hold_time, false).timeout.connect(func() -> void:
			var waiting: Player = hero.get_ref()
			if waiting and _held.get(client) == waiting:
				_held.erase(client)
				waiting.queue_free()
				_check_defeat.call_deferred())
	else:
		player.queue_free()
	_check_defeat.call_deferred()


# --- Partida (servidor) ---------------------------------------------------------

# --- Áreas e viagem ----------------------------------------------------------------

## Carrega a área em todos os PCs (o servidor chama com .rpc; quem entra no meio
## recebe a área atual). Só monta o cenário; monstros e heróis vêm do servidor.
@rpc("authority", "call_local", "reliable")
func _load_area(id: String, _entry: String) -> void:
	area_id = id
	arena = GameData.get_arena(id)
	total_encounters = arena.encounters.size()
	for child in _area_root.get_children():
		_area_root.remove_child(child)
		child.queue_free()
	for drop in _loot_nodes.values():
		if is_instance_valid(drop):
			drop.queue_free()
	_loot_nodes.clear()
	_build_environment()
	_build_area()
	_build_props()
	hazards.build_static(arena)
	hud.minimap.set_area(arena, ExploreMap.empty(arena))
	hud.set_replayable(arena.get("replayable", false), String(arena.get("victory_key", "HUD_VICTORY")))
	hud.set_progress(cleared, total_encounters)
	hud.set_area(tr(arena.get("name_key", "")))


## Viagem do grupo (porta, bueiro, portal de retorno): todos vão juntos.
## Voltar de um mapa para a cidade encerra a expedição (a Poção Elemental acaba)
## e traz um navio novo ao porto (02-0-elementos.md, seção 4; 05-itens-e-loot.md, seção 6).
func travel(to: String, entry: String, expedition_end := false) -> void:
	if not multiplayer.is_server() or not GameData.arenas.has(to):
		return
	if expedition_end:
		for p: Player in get_tree().get_nodes_in_group(&"players"):
			if p.character and p.character.data.get("element_potion", "") != "":
				p.character.end_expedition()
				p.refresh_character()
		town.new_ship(_rng)
	_loot.clear()
	_campaign.area = to
	_campaign.checkpoint = entry
	_exit_countdown = ""
	_load_area.rpc(to, entry)
	_start_run()
	_add_dynamic_props()
	SaveSystem.save_campaign(_campaign, true)


## Objetos que dependem da campanha: lugares das missões secundárias (rumores,
## cargas perdidas), baús ainda fechados e, depois da vitória da área final, o
## que aparece com ela (portal de volta, tesouro).
func _add_dynamic_props(peer_id := 0) -> void:
	var opened: Array = _campaign.get("opened", [])
	var dynamic: Array = town.spot_props(area_id)
	for prop: Dictionary in arena.get("props", []):
		if prop.kind == "chest" and "%s:%s" % [area_id, prop.id] in opened:
			continue
		if prop.get("after_victory", false):
			if result == Result.VICTORY:
				dynamic.append(prop)
		elif prop.kind == "chest":
			dynamic.append(prop)
	for prop in dynamic:
		if peer_id == 0:
			_add_prop.rpc(prop)
		else:
			_add_prop.rpc_id(peer_id, prop)


## Emboscada do rumor falso: monstros acordados em volta do herói.
func spawn_ambush(at: Vector3, monster_id: String, count: int) -> void:
	spawn_adds(at, monster_id, count, 4.0)


## Monstros que chegam acordados (emboscada, ajudantes do chefe): sem grupo de
## encontro, com a força do grupo de agora (13-balanceamento.md 2.5).
func spawn_adds(at: Vector3, monster_id: String, count: int, radius: float) -> void:
	if not multiplayer.is_server():
		return
	var extra := NetworkManager.player_count() - 1
	for i in count:
		var angle := TAU * i / maxi(count, 1)
		var enemy: Enemy = _enemy_spawner.spawn({"monster_id": monster_id, "group": "",
			"level": arena.get("area_level", 1), "position": at + Vector3(cos(angle), 0, sin(angle)) * radius,
			"yaw": angle + PI})
		enemy.wake(1.0 + GameData.balance.health_per_extra_player * extra,
			1.0 + GameData.balance.damage_per_extra_player * extra)


# --- Mapa que se revela (09-interface.md, seção 8) ----------------------------

## Servidor: cada herói de pé revela em volta; o que é novo vai para todos e
## para a campanha (máscara única do grupo).
func _update_explored(delta: float) -> void:
	_explore_timer -= delta
	if _explore_timer > 0.0 or arena.get("town", false) or _explored.is_empty():
		return
	_explore_timer = 0.25
	var found := PackedInt32Array()
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.alive and p.connected:
			found.append_array(ExploreMap.reveal(_explored, arena, Vector2(p.global_position.x, p.global_position.z)))
	if found.is_empty():
		return
	var explored: Dictionary = _campaign.get("explored", {})
	explored[area_id] = ExploreMap.encode(_explored)
	_campaign.explored = explored
	_reveal_cells.rpc(area_id, found)


@rpc("authority", "call_local", "reliable")
func _set_explored(id: String, encoded: String) -> void:
	if id == area_id:
		hud.minimap.set_area(arena, ExploreMap.decode(encoded, arena))


@rpc("authority", "call_local", "reliable")
func _reveal_cells(id: String, cells: PackedInt32Array) -> void:
	if id == area_id:
		hud.minimap.reveal(cells)


## Marcas do minimapa (todos os PCs): heróis, saídas e lugares de missão.
func _update_minimap_marks() -> void:
	var heroes: Array[Dictionary] = []
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		heroes.append({"position": Vector2(p.global_position.x, p.global_position.z), "local": p == local_player})
	var marks: Array[Dictionary] = []
	for prop: Dictionary in _props:
		if prop.kind in ["exit", "quest_spot"]:
			marks.append({"position": Vector2(prop.position[0], prop.position[1]), "kind": "exit" if prop.kind == "exit" else "quest"})
	hud.minimap.set_markers(heroes, marks)


## Chefe acordado na área (para a barra do chefe em todos os PCs).
func _awake_boss() -> Enemy:
	for node in get_tree().get_nodes_in_group(&"enemies"):
		var e := node as Enemy
		if e and e.is_boss() and e.state != Enemy.State.SLEEP and e.health > 0.0 and not e.is_queued_for_deletion():
			return e
	return null


## Chefe mudou de fase: todos veem o nome da fase.
func boss_phase(key: String) -> void:
	_toast_all(key, {})


## O Pacto da Rainha: a arena alaga (água sobre a sala maior da área).
func flood_arena() -> void:
	var biggest: Dictionary = {}
	for room: Dictionary in arena.rooms:
		if biggest.is_empty() or room.size[0] * room.size[1] > biggest.size[0] * biggest.size[1]:
			biggest = room
	_add_prop.rpc({"id": "flood", "kind": "water", "position": biggest.center,
		"size": [biggest.size[0], biggest.size[1]], "flood": true})


## Visitantes sentados nas mesas da Taverna (mudam a cada volta).
func _refresh_visitors() -> void:
	if area_id != "tavern":
		return
	for prop in _props.duplicate():
		if String(prop.id).begins_with("visitor_"):
			_remove_prop(prop.id)
	var seats: Array = GameData.visitors.seats
	for i in mini(town.visitors.size(), seats.size()):
		var visitor: Dictionary = town.visitors[i]
		_build_prop({"id": "visitor_%d" % i, "kind": "npc", "npc": "visitor:%d" % i,
			"position": seats[i], "visitor_name": visitor.name, "visitor_type": visitor.type})
	_refresh_markers()


## Ponto de chegada na área (entradas em data/arenas.json; sem nome, o checkpoint).
func entry_point(entry: String) -> Vector3:
	var entries: Dictionary = arena.get("entries", {})
	var spot: Array = entries.get(entry, entries.get("start", [CHECKPOINT.x, CHECKPOINT.z]))
	return Vector3(spot[0], 0, spot[1])


## Objeto da área ao alcance do herói (kind/id vazios = qualquer um).
func prop_near(player: Node3D, kind := "", id := "", reach := PROP_REACH) -> Dictionary:
	var best := {}
	var best_d := reach
	for prop in _props:
		if kind != "" and prop.kind != kind:
			continue
		if id != "" and prop.get(String(prop.kind), prop.id) != id and prop.id != id:
			continue
		var d := Vector2(player.global_position.x - prop.position[0], player.global_position.z - prop.position[1]).length()
		if d <= best_d:
			best = prop
			best_d = d
	return best


## Botão de interagir (servidor): objeto perto (loja, NPC, porta) ou o loot mais perto.
func request_interact(player: Player) -> void:
	if not multiplayer.is_server() or not player.alive:
		return
	var prop := prop_near(player)
	if not prop.is_empty():
		town.interact(player, prop)
	else:
		request_pickup(player, false)


## Começa (ou continua) a área: os grupos vivos da campanha no lugar, dormindo.
func _start_run() -> void:
	_run += 1
	_zones.clear()
	hazards.reset(arena)
	skills.clear()
	for node in get_tree().get_nodes_in_group(&"enemies"):
		node.queue_free()
	for node in get_children():
		if node is Projectile:
			node.queue_free()
	_groups.clear()
	var dead: Array = _campaign.get("dead_groups", [])
	for encounter: Dictionary in arena.encounters:
		if encounter.id not in dead:
			_spawn_group(encounter)
	# Barris e caixotes que ainda não quebraram nesta campanha.
	var broken: Array = _campaign.get("broken", [])
	for box: Dictionary in arena.get("breakables", []):
		if Breakables.key(area_id, box.id) not in broken:
			_enemy_spawner.spawn({"monster_id": box.monster, "group": "box:" + String(box.id),
				"level": arena.get("area_level", 1), "position": Vector3(box.position[0], 0, box.position[1]),
				"yaw": _rng.randf() * TAU})
	# Bandos das caçadas ativas nesta área (SideQuests.hunt_encounter).
	for quest: Dictionary in SideQuests.active(_campaign.get("side_quests", {})):
		if quest.area == area_id:
			var hunt := SideQuests.hunt_encounter(quest)
			if not hunt.is_empty():
				_spawn_group(hunt)
	# Bonecos do pátio de treino: não acordam, não andam, não morrem.
	for dummy: Dictionary in arena.get("dummies", []):
		_enemy_spawner.spawn({"monster_id": dummy.monster, "group": "",
			"level": 1, "position": Vector3(dummy.position[0], 0, dummy.position[1]), "yaw": PI})
	reset_training()
	_reset_players()
	for c in get_tree().get_nodes_in_group(&"companions"):
		c.queue_free()  # os animais voltam quando o Invocador os chamar de novo
	var done := 0
	for encounter: Dictionary in arena.encounters:
		if encounter.id in dead:
			done += 1
	_broadcast(done, Result.VICTORY if _is_won(done) else Result.NONE)
	_reach_checkpoint(str(_campaign.get("checkpoint", "start")))
	_explored = ExploreMap.decode(String(_campaign.get("explored", {}).get(area_id, "")), arena)
	_set_explored.rpc(area_id, ExploreMap.encode(_explored))


## Passou por um checkpoint (autosave, 11-saves.md, seção 4): vira o último
## checkpoint e entra na lista dos alcançados (portal do Macumbeiro).
func _reach_checkpoint(id: String) -> void:
	if _campaign.is_empty():
		return
	if arena.get("town", false):
		# Na cidade não há checkpoint de mapa (o Macumbeiro só abre portais para os mapas).
		_campaign.area = area_id
		_campaign.checkpoint = id
		SaveSystem.save_campaign(_campaign, true)
		return
	var key := "%s:%s" % [area_id, id]
	var reached: Array = _campaign.get("checkpoints_reached", [])
	if key not in reached:
		_campaign.checkpoints_reached = reached + [key]
	_campaign.area = area_id
	_campaign.checkpoint = id
	SaveSystem.save_campaign(_campaign, true)


## Miniatura da campanha: uma captura da tela de jogo de vez em quando (sem
## menus abertos). Sem tela (headless, testes), não há o que capturar.
func _update_thumbnail(delta: float) -> void:
	_thumb_timer -= delta
	if _thumb_timer > 0.0:
		return
	_thumb_timer = THUMB_INTERVAL
	if DisplayServer.get_name() == "headless" or pause_menu.is_open or _inventory.visible or _trade_menu.is_open():
		return
	var image := get_viewport().get_texture().get_image()
	SaveSystem.save_thumbnail(_campaign.id, image)


## Vitória: todos os encontros da área final vencidos (as outras áreas só
## contam o progresso; a saída leva adiante).
func _is_won(done: int) -> bool:
	return arena.get("final", false) and total_encounters > 0 and done >= total_encounters


## Depois da vitória, a área de teste pode ser jogada de novo do zero.
func _restart_area() -> void:
	if not arena.get("replayable", false):
		return
	var ids: Array = arena.encounters.map(func(e: Dictionary) -> String: return e.id)
	_campaign.dead_groups = _campaign.get("dead_groups", []).filter(func(id: String) -> bool: return id not in ids)
	_start_run()


func _spawn_group(encounter: Dictionary) -> void:
	var center := Vector3(encounter.position[0], 0, encounter.position[1])
	var entries: Array[Dictionary] = []
	for entry: Dictionary in encounter.monsters:
		for i in int(entry.count):
			entries.append(entry)
	var members: Array[Enemy] = []
	var spread := float(encounter.get("spread", 1.6))
	for i in entries.size():
		# Bando em círculo em volta do ponto do grupo.
		var angle := TAU * i / entries.size()
		var offset := Vector3(cos(angle), 0, sin(angle)) * (spread if entries.size() > 1 else 0.0)
		var enemy: Enemy = _enemy_spawner.spawn({
			"monster_id": entries[i].monster, "group": encounter.id, "level": arena.get("area_level", 1),
			"position": center + offset, "yaw": randf() * TAU,
			"rank": entries[i].get("rank", ""), "modifier": entries[i].get("modifier", ""),
		})
		members.append(enemy)
	_groups[encounter.id] = {"position": center, "awake": false, "members": members}


func _reset_players() -> void:
	var spot := entry_point(str(_campaign.get("checkpoint", "start")))
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		p.reset_at(spot + SLOT_OFFSETS[p.slot % SLOT_OFFSETS.size()])


# --- Mapas: baús, saídas em grupo, golpes no chão (Fase 7) ---------------------

## Baú (segredos e tesouro): cada jogador presente ganha o seu loot; abre uma
## vez por campanha.
func open_chest(player: Player, prop: Dictionary) -> void:
	var key := "%s:%s" % [area_id, prop.id]
	var opened: Array = _campaign.get("opened", [])
	if key in opened:
		return
	_campaign.opened = opened + [key]
	var table: Dictionary = GameData.loot.get(String(prop.get("loot", "chest")), GameData.loot.chest)
	var at := Vector3(prop.position[0], 0, prop.position[1])
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.connected and p.character:
			_drop_table(p, at, table, int(arena.get("area_level", 1)))
	# Por grupo: a relíquia do chefe e o que o tesouro libera (o mapa antigo das Ruínas).
	if table.has("relic") and table.relic not in _campaign.get("relics", []):
		_campaign.relics = _campaign.get("relics", []) + [table.relic]
		_toast_all("TOAST_RELIC_FOUND", {"relic": GameData.relics.get(table.relic, {}).get("name_key", "")})
	if table.has("unlocks") and table.unlocks not in _campaign.get("unlocked", []):
		_campaign.unlocked = _campaign.get("unlocked", []) + [table.unlocks]
		_toast_all("TOAST_MAP_FOUND", {})
	if table.has("relic") or table.has("unlocks"):
		town.sync()
	_remove_prop.rpc(String(prop.id))
	_toast_all("TOAST_SECRET_FOUND" if prop.get("secret", false) else "TOAST_CHEST_OPENED", {"name": player.hero_name})
	SaveSystem.save_campaign(_campaign, true)


## Saída para a próxima área (03-2-areas.md, seção 1): só quando todos os
## heróis de pé estão perto; senão avisa quem falta. O host pode forçar: o
## segundo aperto dele começa uma contagem de 10 s.
func request_exit(player: Player, prop: Dictionary) -> void:
	var at := Vector3(prop.position[0], 0, prop.position[1])
	var radius: float = GameData.balance.get("group_exit_radius", 8.0)
	var missing: Array[String] = []
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.connected and p.alive and p.global_position.distance_to(at) > radius:
			missing.append(p.hero_name)
	if missing.is_empty():
		travel(String(prop.to), String(prop.get("entry", "start")), prop.get("expedition_end", false))
		return
	if player.peer_id != 1 or _exit_countdown != String(prop.id):
		_toast_all("TOAST_WAITING_GROUP", {"names": ", ".join(missing)})
		if player.peer_id == 1:
			_exit_countdown = String(prop.id)  # o próximo aperto do host força
		return
	var seconds: float = GameData.balance.get("group_exit_countdown", 10.0)
	_toast_all("TOAST_GROUP_EXIT_COUNTDOWN", {"seconds": int(seconds)})
	var area_now := area_id
	_after(seconds, func() -> void:
		if area_id == area_now:
			travel(String(prop.to), String(prop.get("entry", "start")), prop.get("expedition_end", false)))


## Golpe de monstro no chão: aviso (todos veem), depois o dano (Hazards).
func telegraph(at: Vector3, radius: float, time: float) -> void:
	hazards.telegraph(at, radius, time)


func monster_strike(at: Vector3, radius: float, damage: float, level: int, source: Node3D, extra: Dictionary) -> void:
	hazards.strike(at, radius, damage, level, source, extra)


func add_hazard(at: Vector3, radius: float, duration: float, dps: float, level: int) -> void:
	hazards.add(at, radius, duration, dps, level)


## Grupo dormindo acorda quando um jogador chega perto (raio de despertar).
func _update_encounters() -> void:
	var players := get_tree().get_nodes_in_group(&"players")
	for id in _groups:
		var group: Dictionary = _groups[id]
		if group.awake or group.members.is_empty():
			continue
		for p: Player in players:
			if p.alive and p.connected \
					and p.global_position.distance_to(group.position) <= arena.wake_radius:
				_wake_group(id)
				break


## Acorda o grupo com a força de agora (vida +60%, dano +10% por jogador extra,
## 13-balanceamento.md 2.5) e alerta os vizinhos próximos (aggro em grupo).
func _wake_group(id: String) -> void:
	var group: Dictionary = _groups.get(id, {})
	if group.is_empty() or group.awake:
		return
	group.awake = true
	var extra := NetworkManager.player_count() - 1
	var health_mult: float = 1.0 + GameData.balance.health_per_extra_player * extra
	var damage_mult: float = 1.0 + GameData.balance.damage_per_extra_player * extra
	for enemy: Enemy in group.members:
		enemy.wake(health_mult, damage_mult)
	for other_id in _groups:
		var other: Dictionary = _groups[other_id]
		if other.awake or _groups_distance(group, other) > arena.alert_radius:
			continue
		_wake_group(other_id)


func _groups_distance(a: Dictionary, b: Dictionary) -> float:
	var best := INF
	for x: Enemy in a.members:
		for y: Enemy in b.members:
			best = minf(best, x.global_position.distance_to(y.global_position))
	return best


## Monstros mortos ficam mortos (03-inimigos.md, "Sem respawn"); a campanha
## guarda os grupos vencidos.
func _on_enemy_died(enemy: Enemy) -> void:
	if enemy.data.get("breakable", false):
		_break(enemy)
		return
	_reward(enemy)
	if enemy.is_boss():
		# Os ajudantes e os ninhos somem com o chefe.
		for node in get_tree().get_nodes_in_group(&"enemies"):
			var add := node as Enemy
			if add and add != enemy and add.group == "" and not add.data.get("dummy", false):
				add.queue_free()
	town.on_monster_killed(enemy.monster_id, area_id)
	var group: Dictionary = _groups.get(enemy.group, {})
	if group.is_empty():
		return
	group.members.erase(enemy)
	# Bandos de caçada não contam como encontros da área.
	if group.members.is_empty() and not enemy.group.begins_with("hunt_"):
		_campaign.dead_groups = _campaign.get("dead_groups", []) + [enemy.group]
		SaveSystem.save_campaign(_campaign, true)
		var done := cleared + 1
		var won := _is_won(done)
		_broadcast(done, Result.VICTORY if won else Result.NONE)
		if won:
			town.complete_quests_in(area_id)
			for prop: Dictionary in arena.get("props", []):
				if prop.get("after_victory", false):
					_add_prop.rpc(prop)


## Barril/caixote quebrou (03-2-areas.md, seção 1): sorteio único; o loot sai
## para cada jogador presente; às vezes, monstros escondidos saltam dele.
func _break(box: Enemy) -> void:
	_campaign.broken = _campaign.get("broken", []) + [Breakables.key(area_id, box.group.trim_prefix("box:"))]
	var table: Dictionary = GameData.loot.breakable
	var outcome := Breakables.roll(_rng)
	var at := box.global_position
	var level := int(arena.get("area_level", 1))
	if outcome == "monsters":
		var count := _rng.randi_range(int(table.monsters.count[0]), int(table.monsters.count[1]))
		spawn_adds(at, String(table.monsters.monster), count, 1.2)
		_toast_all("TOAST_BREAKABLE_AMBUSH", {})
		return
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if not p.connected or p.character == null:
			continue
		match outcome:
			"gold":
				_add_loot(p, at, {}, _rng.randi_range(int(table.gold.min), int(table.gold.max)) + roundi(float(table.gold.per_level) * level))
			"potion_health", "potion_resource":
				_add_loot(p, at, Items.stack(Items.CONSUMABLE, outcome), 0)
			"valuable":
				_add_loot(p, at, Items.stack(Items.VALUABLE, _random_valuable()), 0)


## Um valioso do tema do mapa (05-itens-e-loot.md, seção 5).
func _random_valuable() -> String:
	var options: Array[String] = []
	for id in GameData.valuables:
		var maps: Array = GameData.valuables[id].maps
		if maps.is_empty() or arena.get("map_id", "") in maps:
			options.append(id)
	return options[_rng.randi_range(0, options.size() - 1)]


# --- XP e loot (servidor) ------------------------------------------------------

## XP dividido igualmente entre os jogadores presentes (07-rede.md, seção 7);
## loot sorteado para cada um (loot individual).
func _reward(enemy: Enemy) -> void:
	var present: Array[Player] = []
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.connected and p.character and not p.is_queued_for_deletion():
			present.append(p)
	if present.is_empty():
		return
	var xp := roundi(enemy.xp_value() / present.size())
	for p in present:
		p.grant(xp, 0)
		if not enemy.data.get("no_loot", false):
			_drop_loot_for(p, enemy)


func _drop_loot_for(player: Player, enemy: Enemy) -> void:
	_drop_table(player, enemy.global_position, GameData.loot.get(enemy.category(), GameData.loot.common), enemy.level)


## Sorteia uma tabela de loot (data/loot.json) para um jogador: ouro, itens
## (chance ou "items" garantidos, o primeiro com a raridade "guaranteed"),
## poções e valiosos.
func _drop_table(player: Player, origin: Vector3, table: Dictionary, level: int) -> void:
	if _rng.randf() < table.gold.chance:
		var amount := roundi(_rng.randi_range(table.gold.min, table.gold.max) + table.gold.per_level * level)
		amount = roundi(amount * (1.0 + player.character.gold_find_bonus()))
		_add_loot(player, origin, {}, maxi(amount, 1))
	var count := 1 if _rng.randf() < table.item_chance else 0
	if table.has("items"):
		count = _rng.randi_range(int(table.items[0]), int(table.items[1]))
	for i in count:
		var rarity := Items.roll_rarity(table.rarity_weights, _rng)
		if i == 0 and table.has("guaranteed"):
			rarity = String(table.guaranteed)
		_add_loot(player, origin, Items.generate_equipment(level, player.character.data.class_id, rarity, _rng), 0)
	if _rng.randf() < table.potion_chance:
		var potion := "potion_health" if _rng.randf() < 0.6 else "potion_resource"
		# Provisório até o Mercado de Tortuga (Fase 6): parte das poções é elemental.
		if _rng.randf() < float(table.get("elemental_potion_share", 0.0)):
			potion = "elemental_potion_" + Elements.ALL[_rng.randi_range(0, Elements.ALL.size() - 1)]
		_add_loot(player, origin, Items.stack(Items.CONSUMABLE, potion), 0)
	var valuables := 1 if _rng.randf() < table.valuable_chance else 0
	if table.has("valuables"):
		valuables = _rng.randi_range(int(table.valuables[0]), int(table.valuables[1]))
	for i in valuables:
		_add_loot(player, origin, Items.stack(Items.VALUABLE, _random_valuable()), 0)
	# Tesouro do covil (05-itens-e-loot.md, seção 4): o lendário da classe e pergaminhos de refino.
	if table.has("legendary_boss"):
		var legendary := Legendaries.for_boss(String(table.legendary_boss), String(player.character.data.class_id))
		if legendary != "":
			_add_loot(player, origin, Legendaries.create(legendary, level, _rng), 0)
	if table.has("scrolls"):
		var tier_material := Items.material_for_tier(maxi(Items.tier_for_level(level), 1), true)
		for i in _rng.randi_range(int(table.scrolls[0]), int(table.scrolls[1])):
			var kind := "weapon" if _rng.randf() < 0.5 else "armor"
			var blessed := _rng.randf() < float(table.get("blessed_chance", 0.0))
			var id := "%sscroll_refine_%s_%s" % ["blessed_" if blessed else "", kind, tier_material]
			if GameData.consumables.has(id):
				_add_loot(player, origin, Items.stack(Items.CONSUMABLE, id), 0)


func _add_loot(player: Player, origin: Vector3, item: Dictionary, gold: int) -> void:
	var id := _next_loot_id
	_next_loot_id += 1
	var angle := _rng.randf() * TAU
	var position := origin + Vector3(cos(angle), 0, sin(angle)) * _rng.randf_range(0.3, LOOT_SCATTER)
	_loot[id] = {"client": _client_key(player.peer_id), "peer": player.peer_id,
		"position": position, "item": item, "gold": gold}
	_send_loot(id)


func _client_key(peer_id: int) -> String:
	return "host" if peer_id == 1 else NetworkManager.client_id_of(peer_id)


func _send_loot(id: int) -> void:
	var entry: Dictionary = _loot[id]
	if entry.peer == multiplayer.get_unique_id():
		_show_loot(id, entry.position, entry.item, entry.gold)
	elif entry.peer in multiplayer.get_peers():
		_show_loot.rpc_id(entry.peer, id, entry.position, entry.item, entry.gold)


## Quem voltou depois de cair continua vendo o loot que era dele.
func _reassign_loot(client: String, peer_id: int) -> void:
	for id in _loot:
		if _loot[id].client == client:
			_loot[id].peer = peer_id
			_send_loot(id)


## Coleta pedida pelo jogador (interagir: o mais perto; pegar tudo: os próximos).
func request_pickup(player: Player, all: bool) -> void:
	if not multiplayer.is_server() or not player.alive:
		return
	var rules: Dictionary = GameData.loot
	var reach: float = rules.pickup_all_range if all else rules.pickup_range
	var ids: Array[int] = []
	var best_dist := INF
	for id: int in _loot:
		var entry: Dictionary = _loot[id]
		if entry.peer != player.peer_id:
			continue
		var d: float = entry.position.distance_to(player.global_position)
		if d > reach:
			continue
		if all:
			ids.append(id)
		elif d < best_dist:
			best_dist = d
			ids = [id]
	_collect(player, ids)


func _auto_pickup_gold() -> void:
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if not p.alive or not p.connected:
			continue
		var ids: Array[int] = []
		for id: int in _loot:
			var entry: Dictionary = _loot[id]
			if entry.peer == p.peer_id and entry.gold > 0 \
					and entry.position.distance_to(p.global_position) <= GOLD_AUTO_PICKUP:
				ids.append(id)
		if not ids.is_empty():
			_collect(p, ids)


func _collect(player: Player, ids: Array[int]) -> void:
	if ids.is_empty():
		return
	var gold := 0
	var items := []
	for id in ids:
		gold += int(_loot[id].gold)
		if not _loot[id].item.is_empty():
			items.append(_loot[id].item)
	var leftover: Array = player.grant(0, gold, items)
	for id in ids:
		var entry: Dictionary = _loot[id]
		if entry.item.is_empty() or entry.item not in leftover:
			_loot.erase(id)
			if entry.peer == multiplayer.get_unique_id():
				_remove_loot(id)
			elif entry.peer in multiplayer.get_peers():
				_remove_loot.rpc_id(entry.peer, id)
	if not leftover.is_empty():
		_toast_to(player, "TOAST_BAG_FULL", {})


@rpc("authority", "reliable")
func _show_loot(id: int, at: Vector3, item: Dictionary, gold: int) -> void:
	if _loot_nodes.has(id):
		return
	var drop := LootDrop.create(id, at, item, gold)
	_loot_nodes[id] = drop
	add_child(drop)


@rpc("authority", "reliable")
func _remove_loot(id: int) -> void:
	var drop: Node = _loot_nodes.get(id)
	if drop:
		drop.queue_free()
	_loot_nodes.erase(id)


func _toast_to(player: Player, key: String, args: Dictionary) -> void:
	if player.peer_id == multiplayer.get_unique_id():
		_toast(key, args)
	elif player.peer_id in multiplayer.get_peers():
		_toast.rpc_id(player.peer_id, key, args)


func _toast_all(key: String, args: Dictionary) -> void:
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		_toast_to(p, key, args)


@rpc("authority", "reliable")
func _toast(key: String, args: Dictionary) -> void:
	# Valores que são chaves (nome da missão…) saem traduzidos.
	var shown := {}
	for k in args:
		shown[k] = tr(args[k]) if args[k] is String else args[k]
	hud.toast(tr(key).format(shown))


func _update_revives(delta: float) -> void:
	var rules: Dictionary = GameData.balance
	var players := get_tree().get_nodes_in_group(&"players")
	_interrupted = _interrupted.filter(func(p: Player) -> bool:
		return is_instance_valid(p) and p.wants_to_revive())
	for downed: Player in players:
		if downed.alive:
			continue
		var helped := false
		for helper: Player in players:
			if helper in _interrupted:
				continue
			if helper.wants_to_revive() \
					and helper.global_position.distance_to(downed.global_position) <= rules.revive_range:
				helped = true
				_revivers[downed] = helper
				break
		if not helped:
			_revivers.erase(downed)
		if helped:
			downed.revive_progress += delta / rules.revive_time
			if downed.revive_progress >= 1.0:
				downed.revive(rules.revive_health_fraction)
		else:
			downed.revive_progress = maxf(downed.revive_progress - delta, 0.0)
	for downed in _revivers.keys():
		if not is_instance_valid(downed) or downed.alive:
			_revivers.erase(downed)


## Reanimador atingido: a tentativa é interrompida (07-rede.md, seção 9).
func _on_player_hurt(player: Player) -> void:
	for downed: Player in _revivers.keys():
		if _revivers[downed] == player:
			downed.revive_progress = 0.0
			_revivers.erase(downed)
			if player not in _interrupted:
				_interrupted.append(player)


func _on_player_downed() -> void:
	_check_defeat()


## Se todos caírem, volta ao último checkpoint (01-escopo.md, seção 4).
func _check_defeat() -> void:
	if result != Result.NONE:
		return
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.alive and p.connected and not p.is_queued_for_deletion():
			return
	_broadcast(cleared, Result.DEFEAT)
	_after(CHECKPOINT_DELAY, _return_to_checkpoint)


## Todos caíram: voltam ao checkpoint. Mortos continuam mortos; os grupos que
## sobreviveram voltam ao lugar e dormem de novo.
func _return_to_checkpoint() -> void:
	_zones.clear()
	for node in get_children():
		if node is Projectile:
			node.queue_free()
	for id in _groups:
		var group: Dictionary = _groups[id]
		if group.awake and not group.members.is_empty():
			group.awake = false
			for enemy: Enemy in group.members:
				enemy.return_home()
	# Ajudantes e ninhos do chefe somem; a água do Pacto baixa.
	for node in get_tree().get_nodes_in_group(&"enemies"):
		var add := node as Enemy
		if add and add.group == "" and not add.data.get("dummy", false):
			add.queue_free()
	_remove_prop.rpc("flood")
	_reset_players()
	_broadcast(cleared, Result.NONE)
	SaveSystem.save_campaign(_campaign, true)


@rpc("any_peer", "reliable")
func _request_restart() -> void:
	if multiplayer.is_server() and result == Result.VICTORY:
		_restart_area()


## Agenda `callback` só para a partida atual (reinícios cancelam o resto).
func _after(seconds: float, callback: Callable) -> void:
	var run := _run
	get_tree().create_timer(seconds, false).timeout.connect(func() -> void:
		if run == _run:
			callback.call())


func _broadcast(new_cleared: int, new_result: Result) -> void:
	_set_state.rpc(new_cleared, new_result)


@rpc("authority", "call_local", "reliable")
func _set_state(new_cleared: int, new_result: Result) -> void:
	cleared = new_cleared
	result = new_result
	finished = result != Result.NONE
	hud.set_progress(cleared, total_encounters)
	hud.show_result(result)


# --- Sessão e dispositivos ------------------------------------------------------

## O host guarda a campanha ao sair da área ("Salvar e sair", 11-saves.md).
func _exit_tree() -> void:
	save_now()


## Grava agora a campanha (só no host) e o personagem deste PC.
func save_now() -> void:
	if not _campaign.is_empty():
		SaveSystem.save_campaign(_campaign)
	SaveSystem.flush()


func _on_session_ended(_reason_key: String) -> void:
	get_tree().paused = false
	# Só troca de cena se a arena for a cena principal (nos testes ela é filha).
	if get_tree().current_scene == self:
		get_tree().change_scene_to_file.call_deferred(MAIN_SCENE)


func _on_gamepad_lost() -> void:
	hud.show_gamepad_lost(true)
	# Solo: pausa até reconectar; no co-op só avisa (08-controles.md, seção 1).
	if not NetworkManager.is_online():
		get_tree().paused = true


func _on_gamepad_restored() -> void:
	if hud.is_gamepad_lost_visible():
		hud.show_gamepad_lost(false)
		if not pause_menu.is_open:
			get_tree().paused = false


func _build_environment() -> void:
	var outdoor: bool = arena.get("outdoor", false)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	# Tortuga à noite, ao ar livre, é mais clara que o esgoto.
	env.background_color = Color(0.05, 0.06, 0.1) if outdoor else Color(0.03, 0.03, 0.05)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.45, 0.5, 0.65) if outdoor else Color(0.35, 0.38, 0.5)
	env.ambient_light_energy = 0.8 if outdoor else 0.6
	env.fog_enabled = true
	env.fog_light_color = Color(0.06, 0.06, 0.09)
	env.fog_density = 0.01 if outdoor else 0.02
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	_area_root.add_child(world_env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-60, 30, 0)
	sun.light_energy = 0.8
	sun.light_color = Color(0.85, 0.8, 0.75)
	sun.shadow_enabled = true
	_area_root.add_child(sun)

	# Uma tocha (ou lampião) quente por sala grande — poucas luzes dinâmicas.
	for room: Dictionary in arena.rooms:
		if room.get("torch", false):
			var torch := OmniLight3D.new()
			torch.position = Vector3(room.center[0], 3, room.center[1])
			torch.omni_range = 12.0 if not outdoor else 20.0
			torch.light_color = Color(1.0, 0.6, 0.3)
			torch.light_energy = 1.2
			_area_root.add_child(torch)


## Objetos da área (lojas, NPCs, saídas, placas): visual provisório + nome.
## Baús e o que aparece com a vitória vêm do servidor (_add_dynamic_props).
func _build_props() -> void:
	_props.clear()
	_prop_markers.clear()
	for prop: Dictionary in arena.get("props", []):
		if prop.kind != "chest" and not prop.get("after_victory", false):
			_build_prop(prop)
	_refresh_markers()
	_refresh_visitors()


func _build_prop(prop: Dictionary) -> void:
	# Cenário (navio, mar, pontes) não é interagível.
	if prop.kind not in ["ship", "water", "bridge"]:
		_props.append(prop)
	if true:
		var at := Vector3(prop.position[0], 0, prop.position[1])
		var node := Node3D.new()
		node.name = String(prop.id)
		_area_root.add_child(node)
		node.position = at
		var label_key: String = prop.get("name_key", "")
		var color := Color(0.5, 0.4, 0.3)
		match String(prop.kind):
			"shop" when prop.get("look", "") == "vendor":
				# Vendedor em pé (o pirata na frente do navio): corpo e lenço na cabeça.
				var c: Array = prop.get("color", [0.6, 0.2, 0.15])
				var body := CapsuleMesh.new()
				body.radius = 0.35
				body.height = 1.7
				_prop_mesh(node, body, Vector3.ONE, Vector3(0, 0.85, 0), Color(0.55, 0.45, 0.35))
				_prop_mesh(node, SphereMesh.new(), Vector3(0.42, 0.2, 0.42), Vector3(0, 1.72, 0), Color(c[0], c[1], c[2]))
			"shop":
				# Banca: balcão e toldo.
				_prop_mesh(node, BoxMesh.new(), Vector3(2.4, 1.0, 1.0), Vector3(0, 0.5, 0), Color(0.42, 0.3, 0.2))
				_prop_mesh(node, BoxMesh.new(), Vector3(2.8, 0.1, 1.6), Vector3(0, 2.2, 0), Color(0.6, 0.25, 0.2))
			"ship":
				# Navio pirata atracado: casco, convés, dois mastros e velas escuras.
				_prop_mesh(node, BoxMesh.new(), Vector3(16, 2.4, 6), Vector3(0, 0.6, 0), Color(0.3, 0.2, 0.12))
				_prop_mesh(node, BoxMesh.new(), Vector3(15, 0.2, 5.4), Vector3(0, 1.85, 0), Color(0.45, 0.33, 0.2))
				_prop_mesh(node, BoxMesh.new(), Vector3(3, 1.4, 5.6), Vector3(-6, 2.6, 0), Color(0.3, 0.2, 0.12))
				for x in [-2.5, 3.5]:
					_prop_mesh(node, CylinderMesh.new(), Vector3(0.3, 4.5, 0.3), Vector3(x, 6.0, 0), Color(0.35, 0.25, 0.15))
					_prop_mesh(node, BoxMesh.new(), Vector3(0.1, 4.0, 4.6), Vector3(x + 0.3, 7.2, 0), Color(0.2, 0.2, 0.22))
			"water" when prop.get("flood", false):
				# Arena alagada pelo Pacto: lâmina fina (as marcas de aviso ficam por cima).
				var size: Array = prop.size
				_prop_mesh(node, BoxMesh.new(), Vector3(size[0], 0.02, size[1]), Vector3(0, 0.01, 0), Color(0.12, 0.2, 0.16))
			"water":
				# Mar do porto: um plano simples (04-tortuga-e-missoes.md, seção 6).
				var size: Array = prop.get("size", [40, 20])
				_prop_mesh(node, BoxMesh.new(), Vector3(size[0], 0.1, size[1]), Vector3(0, 0.02, 0), Color(0.07, 0.16, 0.24))
			"npc":
				var npc: Dictionary = GameData.npcs.get(prop.npc, {})
				label_key = npc.get("name_key", "")
				var c: Array = npc.get("color", [0.6, 0.5, 0.4])
				if prop.has("visitor_type"):
					# Visitante: nome próprio (não traduzido) e cor do tipo.
					var type: Dictionary = GameData.visitors.types.get(prop.visitor_type, {})
					c = type.get("color", c)
					label_key = "%s (%s)" % [prop.visitor_name, tr(type.get("name_key", ""))]
				color = Color(c[0], c[1], c[2])
				var body := CapsuleMesh.new()
				body.radius = 0.35
				body.height = 1.7
				_prop_mesh(node, body, Vector3.ONE, Vector3(0, 0.85, 0), color)
				# Marca "!" de quem tem história/missão para contar.
				var mark := Label3D.new()
				mark.text = "!"
				mark.font_size = 120
				mark.outline_size = 12
				mark.modulate = Color(1.0, 0.85, 0.3)
				mark.billboard = BaseMaterial3D.BILLBOARD_ENABLED
				mark.position = Vector3(0, 2.6, 0)
				mark.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
				node.add_child(mark)
				_prop_markers[prop.npc] = mark
			"exit" when prop.get("look", "") == "charm_portal":
				# Portal do Patuá: círculo riscado no chão, redemoinho de sombra e brasas.
				_prop_mesh(node, CylinderMesh.new(), Vector3(2.4, 0.04, 2.4), Vector3(0, 0.04, 0), Color(0.35, 0.1, 0.12))
				_prop_mesh(node, CylinderMesh.new(), Vector3(1.4, 0.06, 1.4), Vector3(0, 0.06, 0), Color(1.0, 0.45, 0.15))
			"exit":
				# Saída: moldura de porta / boca do bueiro / círculo do portal.
				_prop_mesh(node, CylinderMesh.new(), Vector3(1.4, 0.06, 1.4), Vector3(0, 0.03, 0), Color(0.25, 0.22, 0.2))
			"sign" when prop.get("look", "") == "crest":
				# Brasão do reino do Arqueiro na parede da passagem.
				_prop_mesh(node, BoxMesh.new(), Vector3(1.4, 1.8, 0.15), Vector3(0, 1.6, 0), Color(0.25, 0.32, 0.5))
				_prop_mesh(node, SphereMesh.new(), Vector3(0.5, 0.5, 0.1), Vector3(0, 1.7, 0.1), Color(0.8, 0.7, 0.3))
			"sign":
				_prop_mesh(node, CylinderMesh.new(), Vector3(2.2, 0.3, 2.2), Vector3(0, 0.15, 0), Color(0.35, 0.35, 0.4))
			"quest_spot":
				# Lugar do rumor / carga perdida: caixote marcado.
				_prop_mesh(node, BoxMesh.new(), Vector3(0.9, 0.7, 0.9), Vector3(0, 0.35, 0), Color(0.55, 0.42, 0.25))
				_prop_mesh(node, CylinderMesh.new(), Vector3(1.6, 0.03, 1.6), Vector3(0, 0.02, 0), Color(0.9, 0.75, 0.3))
			"forge":
				# Forja ao ar livre: bigorna e fornalha acesa.
				_prop_mesh(node, BoxMesh.new(), Vector3(0.9, 0.7, 0.5), Vector3(-0.7, 0.35, 0), Color(0.25, 0.25, 0.27))
				_prop_mesh(node, BoxMesh.new(), Vector3(1.4, 1.2, 1.2), Vector3(0.9, 0.6, 0), Color(0.35, 0.25, 0.2))
				_prop_mesh(node, BoxMesh.new(), Vector3(0.6, 0.3, 0.05), Vector3(0.9, 0.7, 0.61), Color(1.0, 0.45, 0.1))
			"chest":
				# Baú do mapa; o do segredo fica escuro e sem nome, num canto.
				var wood := Color(0.3, 0.2, 0.12) if prop.get("secret", false) else Color(0.5, 0.34, 0.16)
				_prop_mesh(node, BoxMesh.new(), Vector3(1.2, 0.7, 0.8), Vector3(0, 0.35, 0), wood)
				_prop_mesh(node, BoxMesh.new(), Vector3(1.25, 0.12, 0.85), Vector3(0, 0.72, 0), Color(0.75, 0.6, 0.25))
			"bridge":
				# Ponte de madeira podre sobre o canal (cenário).
				var size: Array = prop.get("size", [4, 6])
				_prop_mesh(node, BoxMesh.new(), Vector3(size[0], 0.12, size[1]), Vector3(0, 0.06, 0), Color(0.33, 0.24, 0.15))
			"stash":
				# Baú acorrentado.
				_prop_mesh(node, BoxMesh.new(), Vector3(1.4, 0.8, 0.9), Vector3(0, 0.4, 0), Color(0.4, 0.27, 0.15))
				_prop_mesh(node, BoxMesh.new(), Vector3(1.45, 0.1, 0.95), Vector3(0, 0.55, 0), Color(0.3, 0.3, 0.32))
			"training":
				_prop_mesh(node, BoxMesh.new(), Vector3(1.6, 1.2, 0.15), Vector3(0, 1.3, 0), Color(0.45, 0.33, 0.2))
		if label_key != "":
			var label := Label3D.new()
			label.text = label_key
			label.font_size = 48
			label.outline_size = 8
			label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
			label.position = Vector3(0, 3.0, 0)
			node.add_child(label)


func _prop_mesh(parent: Node3D, mesh: PrimitiveMesh, scale_: Vector3, at: Vector3, color: Color) -> void:
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.scale = scale_
	node.position = at
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	node.material_override = material
	parent.add_child(node)


## "!" só nos NPCs com missão para oferecer agora.
func _refresh_markers() -> void:
	for npc_id: String in _prop_markers:
		var mark: Label3D = _prop_markers[npc_id]
		if is_instance_valid(mark):
			mark.visible = town.has_offer(npc_id)
	hud.set_quest(town.active_quest())


## Chão único e paredes de cada sala, com vão de porta onde a sala se liga a outra.
func _build_area() -> void:
	var bounds := AABB()
	for i in arena.rooms.size():
		var room: Dictionary = arena.rooms[i]
		var c := Vector3(room.center[0], 0, room.center[1])
		var half := Vector3(room.size[0], 0, room.size[1]) / 2.0
		var box := AABB(c - half, half * 2.0)
		bounds = box if i == 0 else bounds.merge(box)
		# Portas: "north", "south", "east", "west", com deslocamento opcional
		# do vão ("east:-3" = 3 m para o norte do meio da parede leste).
		var doors := {}
		for door: String in room.get("doors", []):
			doors[door.get_slice(":", 0)] = float(door.get_slice(":", 1)) if door.contains(":") else 0.0
		# Mureta baixa no cais e na doca (dá para ver o mar); paredes normais no resto.
		var height := float(room.get("wall_height", WALL_HEIGHT))
		_wall_x(c.x, c.z - half.z, half.x * 2.0, doors.has("north"), height, doors.get("north", 0.0))
		_wall_x(c.x, c.z + half.z, half.x * 2.0, doors.has("south"), height, doors.get("south", 0.0))
		_wall_z(c.x - half.x - 0.5, c.z, half.z * 2.0 + 2.0, doors.has("west"), height, doors.get("west", 0.0))
		_wall_z(c.x + half.x + 0.5, c.z, half.z * 2.0 + 2.0, doors.has("east"), height, doors.get("east", 0.0))
	var center := bounds.get_center()
	_box(Vector3(center.x, -0.5, center.z), Vector3(bounds.size.x + 4, 1, bounds.size.z + 4), FLOOR_COLOR)


## Parede ao longo de x; com porta, deixa um vão de DOOR_WIDTH (no meio, ou
## deslocado `offset` metros).
func _wall_x(cx: float, z: float, width: float, door: bool, height := WALL_HEIGHT, offset := 0.0) -> void:
	for piece in _wall_pieces(width, door, offset):
		_box(Vector3(cx + piece.x, height / 2, z), Vector3(piece.y, height, 1), WALL_COLOR)


## Parede ao longo de z (leste/oeste), com o mesmo vão de porta.
func _wall_z(x: float, cz: float, length: float, door: bool, height := WALL_HEIGHT, offset := 0.0) -> void:
	for piece in _wall_pieces(length, door, offset):
		_box(Vector3(x, height / 2, cz + piece.x), Vector3(1, height, piece.y), WALL_COLOR)


## Pedaços de parede (centro relativo, comprimento) em volta do vão da porta.
static func _wall_pieces(length: float, door: bool, offset: float) -> Array[Vector2]:
	if not door:
		return [Vector2(0, length)]
	var gap := minf(DOOR_WIDTH, length)
	var a := -length / 2.0
	var b := offset - gap / 2.0
	var c := offset + gap / 2.0
	var d := length / 2.0
	var pieces: Array[Vector2] = []
	if b - a > 0.01:
		pieces.append(Vector2((a + b) / 2.0, b - a))
	if d - c > 0.01:
		pieces.append(Vector2((c + d) / 2.0, d - c))
	return pieces


func _box(center: Vector3, box_size: Vector3, color: Color) -> void:
	var body := StaticBody3D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = box_size
	shape.shape = box
	body.add_child(shape)
	var mesh := MeshInstance3D.new()
	var box_mesh := BoxMesh.new()
	box_mesh.size = box_size
	mesh.mesh = box_mesh
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	mesh.material_override = material
	body.add_child(mesh)
	_area_root.add_child(body)
	body.position = center
