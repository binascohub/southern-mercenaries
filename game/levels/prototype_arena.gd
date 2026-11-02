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
## Portão do chefe (Boss_Gate): o arquivo tem 2,0 m de largura; com 3,0 fecha o vão de uma porta (DOOR_WIDTH 6 m).
const GATE_SCALE := 3.0
const MAIN_SCENE := "res://game/main/main.tscn"
const WALL_HEIGHT := 2.5
const DOOR_WIDTH := 6.0
## Largura de um telhado do kit (Roof_RoundTiles_4x4) atrás das casas.
const ROOF_WIDTH := 5.5
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
## Todos os baús têm a mesma largura nos arquivos (0,9 m); no jogo ficam um pouco maiores (~1,17 m).
const CHEST_SCALE := 1.3
## Miniatura da campanha: primeira captura logo depois de entrar, depois a cada minuto.
## Segundos entre a fala da estátua e o surgimento do mini-chefe.
const SUMMON_DELAY := 4.0
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
## Grupos de estátuas já invocados e ainda esperando surgir (ids).
var _summoning: Array[String] = []
## Tabela de loot própria de alguns caixotes ("box:id" -> chave em loot.json).
var _box_table := {}
var _encounter_timer := 0.0
## Campanha deste host (11-saves.md): grupos mortos não voltam. Vazia nos
## clientes (mesmo depois de desconectados, quando o Godot os trata como servidor).
var _campaign: Dictionary = {}
## Loot no chão (servidor): id -> {client, peer, position, item, gold}.
var _loot := {}
## Quando cada jogador viu o aviso de bolsa cheia (peer -> ms), para o autoloot não repetir o aviso.
var _bag_full_toast := {}
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
## Pegadas até o objetivo da missão ativa (opção "Pegadas da missão").
var _quest_trail: QuestTrail
## Mapa que se revela (servidor): máscara da área atual e o próximo passo.
var _explored := PackedByteArray()
var _explore_timer := 0.0
## Saída em grupo: contagem do host em andamento (id da saída) e em que partida.
var _exit_countdown := ""
## Nós da área atual (paredes, chão, luzes, objetos), trocados a cada viagem.
var _area_root: Node3D
## Tinta do estilo da área e materiais do kit já tingidos (original → cópia).
var _style_tint := Color.WHITE
var _tinted := {}
## Tom único da madeira da área (style.wood_tone, alfa 0 = desligado): ver _tone_wood.
var _wood_tone := Color(0, 0, 0, 0)
var _toned := {}
var _wood_average := {}
var _sludge: StandardMaterial3D
## Cristal de save do checkpoint (flutua; acende quando o jogo salva).
var _crystal_material: StandardMaterial3D
## Paredes altas do kit (com o cano e a sujeira presos a elas): as que ficam
## entre a câmera (ao sul) e o herói somem para não tapar a visão.
var _cut_walls: Array[Node3D] = []
var _cut_timer := 0.0
## Bocas de cano do esgoto desta área: [boca, direção para fora da parede].
var _pipes: Array = []
## Sujeira do esgoto: materiais das poças, da faixa de umidade e dos escorridos.
var _grime_materials := {}
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
	_quest_trail = QuestTrail.new()
	_quest_trail.setup(self)
	add_child(_quest_trail)
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
			_update_save_point()
		_update_zones(delta)
		_update_training()
	hud.set_boss(_awake_boss())
	_update_minimap_marks()
	if multiplayer.is_server():
		_update_explored(delta)
	_update_cutaway(delta)
	if local_player and is_instance_valid(local_player):
		hud.set_training(training if in_training(local_player.global_position) else {})
		var near := prop_near(local_player)
		var name_key: String = near.get("name_key", GameData.npcs.get(near.get("npc", ""), {}).get("name_key", ""))
		hud.set_interact_prompt(tr(name_key) if not near.is_empty() else "")
	if not _campaign.is_empty():
		_campaign.played_seconds = float(_campaign.get("played_seconds", 0)) + delta
		_update_thumbnail(delta)


## Corte das paredes: a câmera olha do sul, então paredes ao sul do herói (até
## onde a câmera alcança, e perto dele de lado) somem (só as de uns 6 m à frente e 3,5 m de lado); voltam quando ele passa.
func _update_cutaway(delta: float) -> void:
	_cut_timer -= delta
	if _cut_timer > 0.0 or _cut_walls.is_empty() or local_player == null or not is_instance_valid(local_player):
		return
	_cut_timer = 0.1
	var at := local_player.global_position
	for wall in _cut_walls:
		if not is_instance_valid(wall):
			continue
		var p := wall.global_position
		wall.visible = not (p.z > at.z + 1.0 and p.z < at.z + 6.0 and absf(p.x - at.x) < 3.5)  # só as paredes na frente do herói (antes 14 m x 9 m: sumiam demais e escondiam o caminho)


## Paredes escondidas agora pelo corte (testes).
func hidden_walls() -> int:
	return _cut_walls.filter(func(w: Node3D) -> bool: return is_instance_valid(w) and not w.visible).size()


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
	if _wood_tone.a > 0.0 and String(GameData.monsters.get(spawn.get("monster_id", ""), {}).get("category", "")) == "breakable":
		# Barris e caixotes quebráveis: a mesma madeira do resto da área (o visual nasce no _ready).
		enemy.ready.connect(func() -> void: _tone_wood(enemy._visual, enemy._kit_piece))
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
func skill_burst(at: Vector3, radius: float, hit: Dictionary, fx := "") -> void:
	if multiplayer.is_server():
		skills.burst(at, radius, hit, fx)


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
		"look": character.data.get("look", {}),
		"visual": character.equipment_visual(),
		"element": character.current_element(),
	})
	if resume == null and character.is_edited():
		# Ficha mudada fora do jogo: só avisa, nunca bloqueia (11-saves.md, seção 5).
		push_warning("Ficha editada fora do jogo: %s" % character.data.name)
		_toast_all.call_deferred("TOAST_CHARACTER_EDITED", {"name": character.data.name})
	player.set_character(character)
	for book: Array in [["book_frog_altar", "altar_book"], ["book_gator_altar", "gator_book"]]:
		if book[0] in _campaign.get("keys", []) and character.count_of(book[1]) == 0:
			character.add_item(Items.stack(Items.VALUABLE, book[1]))  # quem entra depois da missão aceita também recebe o livro dela (Livro do Altar, Grimório das Brasas)
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
	hud.show_area_foes(_area_foes())


## Monstros desta área (um de cada, na ordem dos encontros) e o elemento deles.
func _area_foes() -> Array:
	var seen := {}
	var foes := []
	for encounter: Dictionary in arena.get("encounters", []):
		for entry: Dictionary in encounter.get("monsters", []):
			var id := String(entry.get("monster", ""))
			var data := GameData.get_monster(id)
			if id == "" or seen.has(id) or data.is_empty() or data.get("breakable", false):
				continue
			seen[id] = true
			foes.append({"name_key": data.get("name_key", id), "element": data.get("element", "")})
	return foes


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
	for saved: Dictionary in _campaign.get("mini_chests", []):
		if saved.area == area_id and "%s:%s" % [area_id, saved.prop.id] not in opened:
			dynamic.append(saved.prop)
	for prop: Dictionary in arena.get("props", []):
		if prop.kind in ["chest", "gate"] and "%s:%s" % [area_id, prop.id] in opened:
			continue
		if prop.get("after_victory", false):
			if result == Result.VICTORY:
				dynamic.append(prop)
		elif prop.kind in ["chest", "gate"]:
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


## Monstros raros (dados "rare_spawn"): com a chance dada, um deles aparece
## acordado no meio de uma sala que não é a da entrada.
func _maybe_spawn_rare() -> void:
	if arena.get("town", false) or arena.rooms.is_empty():
		return
	for monster_id: String in GameData.monsters:
		var data: Variant = GameData.monsters[monster_id]
		if not data is Dictionary or not (data.has("rare_spawn") or data.get("guaranteed_spawn", false)):
			continue
		if not data.get("guaranteed_spawn", false):
			if arena.get("final", false) or arena.rooms.size() < 2 or _rng.randf() >= float(data.rare_spawn):
				continue
		var room: Dictionary = arena.rooms[_rng.randi_range(1 if arena.rooms.size() > 1 else 0, arena.rooms.size() - 1)]
		spawn_adds(Vector3(room.center[0], 0, room.center[1]), monster_id, 1, 0.0)


## Ponto sorteado dentro de uma sala do mapa (longe das bordas) a pelo menos `min_dist` de `from`: para onde o
## Dragãozinho Dourado se teleporta. Sem sala longe o bastante, devolve `from`.
func random_room_point(from: Vector3, min_dist := 20.0) -> Vector3:
	var best := from
	for i in 12:
		var room: Dictionary = arena.rooms[_rng.randi_range(0, arena.rooms.size() - 1)]
		var half_x := maxf(float(room.size[0]) / 2.0 - 4.0, 0.0)
		var half_z := maxf(float(room.size[1]) / 2.0 - 4.0, 0.0)
		var p := Vector3(float(room.center[0]) + _rng.randf_range(-half_x, half_x), 0.0,
			float(room.center[1]) + _rng.randf_range(-half_z, half_z))
		if p.distance_to(from) >= min_dist:
			return p
		if p.distance_to(from) > best.distance_to(from):
			best = p
	return best


## Moedas que caem de um monstro (o Coelho Dourado, a cada golpe): para cada herói.
## Moedas no chão (cada herói vê as dele); `pieces` as espalha em várias moedas.
func drop_coins(at: Vector3, amount: int, pieces := 1) -> void:
	if not multiplayer.is_server():
		return
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.connected and p.character:
			var total := maxi(roundi(amount * (1.0 + p.character.gold_find_bonus())), 1)
			var count := clampi(pieces, 1, total)
			for i in count:
				_add_loot(p, at, {}, total / count + (1 if i < total % count else 0))


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


## Save point no meio do mapa ("save_point" em arenas.json, uma entrada): quando um herói de pé chega perto do cristal dele,
## ele vira o checkpoint (autosave) se ainda não era.
func _update_save_point() -> void:
	var id := String(arena.get("save_point", ""))
	if id == "" or String(_campaign.get("checkpoint", "start")) == id:
		return
	var at := entry_point(id) + Vector3(2.2, 0, -0.5)
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.alive and p.connected and p.global_position.distance_to(at) < 3.5:
			_reach_checkpoint(id)
			return


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


## A estátua falou (Town.interact): depois de uns segundos o grupo dela (`prop.summon`, igual a um encontro de
## arenas.json) surge e já acorda. Uma vez só por vida do grupo: não repete enquanto ele existe nem depois de derrotado.
func summon_encounter(player: Player, prop: Dictionary) -> void:
	if not multiplayer.is_server():
		return
	var group: Dictionary = prop.summon
	var id := String(group.id)
	if id in _campaign.get("dead_groups", []) or _groups.has(id) or id in _summoning:
		return
	_summoning.append(id)
	await get_tree().create_timer(SUMMON_DELAY).timeout
	_summoning.erase(id)
	if not is_inside_tree() or _groups.has(id):
		return
	_spawn_group(group)
	_wake_group(id)
	_toast_all(String(group.get("toast", "TOAST_STATUE_AWAKENS")), {})


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
	_box_table.clear()
	var dead: Array = _campaign.get("dead_groups", [])
	for encounter: Dictionary in arena.encounters:
		if encounter.id not in dead:
			_spawn_group(encounter)
	# Barris e caixotes que ainda não quebraram nesta campanha.
	var broken: Array = _campaign.get("broken", [])
	for box: Dictionary in arena.get("breakables", []):
		if Breakables.key(area_id, box.id) not in broken:
			if box.has("table"):
				_box_table["box:" + String(box.id)] = box.table
			_enemy_spawner.spawn({"monster_id": box.monster, "group": "box:" + String(box.id),
				"level": arena.get("area_level", 1), "position": Vector3(box.position[0], 0, box.position[1]),
				"yaw": _rng.randf() * TAU})
	# Dragãozinho Dourado (um por mapa) e outros raros: aparecem numa sala do mapa.
	_maybe_spawn_rare()
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
	if multiplayer.is_server():
		_crystal_glow.rpc()


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


## Vitória: todos os encontros da área final vencidos, ou só os de "victory_groups"
## quando a área os lista (as outras áreas só contam o progresso; a saída leva adiante).
func _is_won(done: int) -> bool:
	if not arena.get("final", false) or total_encounters == 0:
		return false
	# victory_groups: a vitória é vencer só estes grupos (o chefe do mapa), sem precisar limpar o resto do mapa.
	var need: Array = arena.get("victory_groups", [])
	if not need.is_empty():
		var dead: Array = _campaign.get("dead_groups", [])
		return need.all(func(id: String) -> bool: return id in dead)
	return done >= total_encounters


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
			"monster_id": entries[i].monster, "group": encounter.id, "level": int(encounter.get("level", arena.get("area_level", 1))),
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

## Põe um objeto de missão na bolsa de todos os heróis presentes (uma cópia só; quem já o tem não ganha outra).
func grant_quest_item_to_all(item_id: String) -> void:
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.connected and p.character and p.character.count_of(item_id) == 0:
			p.character.add_item(Items.stack(Items.VALUABLE, item_id))
			p.refresh_character()


## Baú (segredos e tesouro): cada jogador presente ganha o seu loot; abre uma
## vez por campanha.
func open_chest(player: Player, prop: Dictionary) -> void:
	var key := "%s:%s" % [area_id, prop.id]
	var opened: Array = _campaign.get("opened", [])
	if key in opened:
		return
	# Tesouro do chefe: trancado até o grupo pegar a chave que ele deixa cair.
	var needs: String = prop.get("key", "")
	if needs != "" and needs not in _campaign.get("keys", []):
		_toast_to(player, "TOAST_CHEST_LOCKED", {})
		return
	_campaign.opened = opened + [key]
	player.act("open")
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


## Chave do chefe (por grupo): fica guardada na campanha e abre o baú dele.
func pick_key(player: Player, prop: Dictionary) -> void:
	var key: String = prop.get("key", "")
	if key == "" or key in _campaign.get("keys", []):
		return
	_campaign.keys = _campaign.get("keys", []) + [key]
	player.act("open")
	_remove_prop.rpc(String(prop.id))
	_toast_all("TOAST_KEY_FOUND", {"name": player.hero_name})
	SaveSystem.save_campaign(_campaign, true)
	_open_key_gates()


## Portões que só abrem com várias chaves da campanha (prop "gate" com "needs_keys"): caem sozinhos quando o grupo as tem todas.
func _open_key_gates() -> void:
	var keys: Array = _campaign.get("keys", [])
	for prop: Dictionary in arena.get("props", []):
		if prop.kind == "gate" and prop.has("needs_keys") and prop.needs_keys.all(func(k: String) -> bool: return k in keys):
			open_gate(String(prop.id))


## Portão do chefe (prop "gate"): só cai quando o Guardião do Portão recebe as duas chaves (missão "opens_gate", entregue em Town._turn_in); fica aberto para sempre na campanha.
func open_gate(gate_id: String) -> void:
	var key := "%s:%s" % [area_id, gate_id]
	if key in _campaign.get("opened", []):
		return
	_campaign.opened = _campaign.get("opened", []) + [key]
	_open_gate.rpc(gate_id)
	_toast_all("TOAST_GATE_OPENED", {})
	SaveSystem.save_campaign(_campaign, true)


@rpc("authority", "call_local", "reliable")
func _open_gate(id: String) -> void:
	_props = _props.filter(func(p: Dictionary) -> bool: return p.id != id)
	var node := _area_root.get_node_or_null(id) as Node3D
	if node == null:
		return
	var body := node.get_node_or_null("gate_body")
	if body:
		body.queue_free()  # a passagem já libera
	var sink := node.create_tween()
	sink.tween_property(node, "position:y", -5.0, 2.5).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	sink.tween_callback(node.queue_free)


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
		# Áreas pacíficas (o Esgoto): os bichos só revidam — quem chega perto não
		# os acorda; só atacam por conta própria os chefes e os "aggressive" (o Baú Monstro, o único monstro comum do Esgoto que ataca sem ser atacado).
		if arena.get("passive", false) and not _group_has_boss(group) and not _group_is_aggressive(group):
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
	if arena.get("passive", false):
		return  # revida só o grupo atacado; os vizinhos continuam em paz
	for other_id in _groups:
		var other: Dictionary = _groups[other_id]
		if other.awake or _groups_distance(group, other) > arena.alert_radius:
			continue
		_wake_group(other_id)


## O grupo tem um monstro "aggressive" (data/monsters.json): acorda por proximidade mesmo na área pacífica.
func _group_is_aggressive(group: Dictionary) -> bool:
	for enemy: Enemy in group.members:
		if is_instance_valid(enemy) and enemy.data.get("aggressive", false):
			return true
	return false


func _group_has_boss(group: Dictionary) -> bool:
	for enemy: Enemy in group.members:
		if is_instance_valid(enemy) and enemy.is_boss():
			return true
	return false


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
	if enemy.category() == "miniboss" or enemy.category() == "boss":
		_drop_miniboss_chest(enemy)
	if (enemy.is_boss() or enemy.category() == "miniboss") and enemy.data.has("drops_key") and String(enemy.data.drops_key) not in _campaign.get("keys", []):
		# A chave cai onde o chefe (ou o mini-chefe) morreu; as chaves do Esgoto abrem o portão do corredor do Ninho.
		_add_prop.rpc({"id": "key_%s" % enemy.data.drops_key, "kind": "key", "key": String(enemy.data.drops_key), "name_key": String(enemy.data.get("key_name_key", "PROP_BOSS_KEY")),
			"model": String(enemy.data.get("key_model", "Key_Gold")),
			"position": [enemy.global_position.x + 2.2, enemy.global_position.z + 1.2]})  # ao lado do baú (no mesmo ponto, o aviso de interagir mostrava a chave e não o baú)
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
		town.complete_cleared(area_id)  # missões da aldeia que pedem limpar este bando
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
	var outcome := Breakables.roll(_rng, String(_box_table.get(box.group, "breakable")))
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
				# Tabela própria do objeto (a bolsa de moedas tem a sua em data/loot.json) e, na bolsa, o ouro cai em várias moedas espalhadas.
				var table_id := String(_box_table.get(box.group, "breakable"))
				var gold: Dictionary = GameData.loot[table_id].get("gold", table.gold)
				var total := _rng.randi_range(int(gold.min), int(gold.max)) + roundi(float(gold.per_level) * level)
				var pieces := 5 if table_id == "coin_bag" else 1
				for i in pieces:
					_add_loot(p, at, {}, total / pieces + (1 if i < total % pieces else 0))
			"potion_health", "potion_resource":
				_add_loot(p, at, Items.stack(Items.CONSUMABLE, outcome), 0)
			"venison":
				# Carne do cervo: cura como a poção de vida (tabela "breakable_meat").
				var meat: Dictionary = GameData.loot.breakable_meat.venison
				_add_loot(p, at, Items.stack(Items.CONSUMABLE, "venison", _rng.randi_range(int(meat.min), int(meat.max))), 0)
			"valuable":
				_add_loot(p, at, Items.stack(Items.VALUABLE, _random_valuable()), 0)


## Um valioso do tema do mapa (05-itens-e-loot.md, seção 5).
func _random_valuable() -> String:
	var options: Array[String] = []
	for id in GameData.valuables:
		if GameData.valuables[id].get("quest_item", false):
			continue  # relíquias de missão (caveira de Morvak, chaves, costela…) só caem de quem a missão manda, nunca no sorteio comum
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
			if enemy.category() == "miniboss":  # o mini-chefe solta só poções; o resto vem do baú que ele deixa (ver _drop_miniboss_chest)
				_drop_table(p, enemy.global_position, GameData.loot.miniboss_drop, enemy.level)
			else:
				_drop_loot_for(p, enemy)
			_drop_quest_item(p, enemy)


## Baú do mini-chefe (Treasure Chest, WeaponGuy, CC-BY 3.0): no lugar onde ele caiu; ao abrir (interagir), sai o loot de cada herói
## (tabela "miniboss" de data/loot.json). Fica guardado na campanha até ser aberto, mesmo se o grupo sair da área.
func _drop_miniboss_chest(enemy: Enemy) -> void:
	# O mini-chefe deixa o baú médio ou o grande; o chefão do mapa, o épico (tabela "boss_chest").
	# "chest_loot" no monstro: o mini-chefe que é o chefe do mapa (o Leshy) deixa o baú épico com a tabela própria (tesouro e relíquia).
	var boss := enemy.category() == "boss" or enemy.data.has("chest_loot")
	var prop := {"id": "mbchest_%s" % enemy.monster_id, "kind": "chest", "name_key": "PROP_BOSS_CHEST" if boss else "PROP_MINIBOSS_CHEST",
		"model": "Chest_Epic" if boss else ("Chest_Large" if _rng.randf() < 0.5 else "Chest_Medium"),
		"loot": String(enemy.data.get("chest_loot", "boss_chest")) if boss else "miniboss", "position": [snappedf(enemy.global_position.x, 0.1), snappedf(enemy.global_position.z, 0.1)]}
	var saved: Array = _campaign.get("mini_chests", []).filter(func(c: Variant) -> bool: return c.prop.id != prop.id or c.area != area_id)
	saved.append({"area": area_id, "prop": prop})
	_campaign.mini_chests = saved
	_add_prop.rpc(prop)
	_toast_all("TOAST_BOSS_CHEST" if boss else "TOAST_MINIBOSS_CHEST", {})
	SaveSystem.save_campaign(_campaign, true)


## Relíquia de missão (data/quests.json "item"): o mini-chefe com "quest_drop" a deixa cair para cada herói que
## tem a missão ativa e ainda não tem o item na bolsa.
func _drop_quest_item(player: Player, enemy: Enemy) -> void:
	var item_id: String = enemy.data.get("quest_drop", "")
	if item_id == "" or player.character.count_of(item_id) > 0:
		return
	for quest_id: String in _campaign.get("quests", {}):
		if _campaign.quests[quest_id] == "active" and GameData.quests.get(quest_id, {}).get("item", "") == item_id:
			# O chefe do mapa encerra a expedição ao morrer: a relíquia cai aos pés de cada herói (o autoloot a pega na hora), para ninguém sair sem ela.
			var at := player.global_position if enemy.is_boss() else enemy.global_position
			_add_loot(player, at, Items.stack(Items.VALUABLE, item_id), 0)
			return


func _drop_loot_for(player: Player, enemy: Enemy) -> void:
	_drop_table(player, enemy.global_position, GameData.loot.get(enemy.category(), GameData.loot.common), enemy.level)


## Sorteia uma tabela de loot (data/loot.json) para um jogador: ouro, itens
## (chance ou "items" garantidos, o primeiro com a raridade "guaranteed"),
## poções (chance ou "potions" garantidas) e valiosos.
func _drop_table(player: Player, origin: Vector3, table: Dictionary, level: int) -> void:
	if _rng.randf() < table.gold.chance:
		var amount := roundi(_rng.randi_range(table.gold.min, table.gold.max) + table.gold.per_level * level)
		amount = roundi(amount * (1.0 + player.character.gold_find_bonus()))
		# "gold_piles": o ouro cai em várias moedas espalhadas (o chefão), em vez de uma só.
		var piles := maxi(1, mini(int(table.get("gold_piles", 1)), amount))
		for i in piles:
			_add_loot(player, origin, {}, maxi(amount / piles + (1 if i < amount % piles else 0), 1))
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
	# Baú de poções: um número garantido de poções (vida ou recurso).
	if table.has("potions"):
		for i in _rng.randi_range(int(table.potions[0]), int(table.potions[1])):
			_add_loot(player, origin, Items.stack(Items.CONSUMABLE, "potion_health" if _rng.randf() < 0.6 else "potion_resource"), 0)
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


## Autoloot: ouro e itens ao alcance de quem passa por cima são pegos (o que não couber na bolsa fica no chão).
func _auto_pickup_gold() -> void:
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if not p.alive or not p.connected:
			continue
		var ids: Array[int] = []
		for id: int in _loot:
			var entry: Dictionary = _loot[id]
			if entry.peer == p.peer_id and entry.position.distance_to(p.global_position) <= GOLD_AUTO_PICKUP:  # ouro e itens: passar por cima pega (autoloot)
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
	if not leftover.is_empty() and Time.get_ticks_msec() - int(_bag_full_toast.get(player.peer_id, -10000)) >= 3000:  # o autoloot tenta a cada instante: avisa a cada 3 s
		_bag_full_toast[player.peer_id] = Time.get_ticks_msec()
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
		if prop.kind not in ["chest", "gate"] and not prop.get("after_victory", false):
			_build_prop(prop)
	_refresh_markers()
	_refresh_visitors()


func _build_prop(prop_data: Dictionary) -> void:
	# "route": o objeto anda (o mercador pirata); a cópia guarda a posição de agora e os dados ficam intactos.
	var prop := prop_data.duplicate(true) if prop_data.has("route") else prop_data
	# Cenário (navio, mar, pontes) não é interagível.
	if prop.kind not in ["ship", "water", "bridge", "gate"]:
		_props.append(prop)
	if true:
		var at := Vector3(prop.position[0], 0, prop.position[1])
		var node: Node3D = Wanderer.new() if prop.has("route") else Node3D.new()
		node.name = String(prop.id)
		_area_root.add_child(node)
		node.position = at
		var label_key: String = prop.get("name_key", "")
		var color := Color(0.5, 0.4, 0.3)
		match String(prop.kind):
			"shop" when prop.get("look", "") == "vendor":
				# Vendedor em pé (o pirata na frente do navio): corpo e lenço na cabeça.
				var c: Array = prop.get("color", [0.6, 0.2, 0.15])
				var vendor := _npc_body(node, {"sex": "male", "hair": ["Hair_Buzzed", "Hair_Beard"], "hair_color": [0.08, 0.06, 0.05],
						"pose": "talk", "outfit": {"body": "copper", "feet": "iron", "head": "cloth"}})
				if node is Wanderer:
					# Mercador ambulante: vai e volta pela rota; a loja abre onde ele estiver.
					var walker := node as Wanderer
					var route: Array = prop.route
					walker.from = Vector3(route[0][0], 0, route[0][1])
					walker.to = Vector3(route[1][0], 0, route[1][1])
					walker.speed = float(prop.get("speed", 1.0))
					walker.synced = true
					walker.tracked = prop
					walker.model = vendor
				if vendor == null:
					var body := CapsuleMesh.new()
					body.radius = 0.35
					body.height = 1.7
					_prop_mesh(node, body, Vector3.ONE, Vector3(0, 0.85, 0), Color(0.55, 0.45, 0.35))
				_prop_mesh(node, SphereMesh.new(), Vector3(0.42, 0.2, 0.42), Vector3(0, 1.72, 0), Color(c[0], c[1], c[2]))
			"shop" when prop.has("stall"):
				node.add_child(MarketStall.build(String(prop.stall)))  # barraca de feira, de frente para a rua
			"shop" when _kit(node, "Stall_Empty", Transform3D(Basis(Vector3.UP, PI), Vector3.ZERO)):
				pass  # barraca de feira com toldo, de frente para a rua
			"shop":
				# Banca: balcão e toldo.
				_prop_mesh(node, BoxMesh.new(), Vector3(2.4, 1.0, 1.0), Vector3(0, 0.5, 0), Color(0.42, 0.3, 0.2))
				_prop_mesh(node, BoxMesh.new(), Vector3(2.8, 0.1, 1.6), Vector3(0, 2.2, 0), Color(0.6, 0.25, 0.2))
			"ship" when _kit(node, "pirate_ship", Transform3D(Basis().scaled(Vector3.ONE * 0.95), Vector3(-1.5, 0, 0))):
				pass  # galeão pirata (tools/assets/build_galleon.py): a quilha fica embaixo da água
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
			"water" when not arena.get("outdoor", false):
				# Água do esgoto: lodo verde-escuro, liso e com brilho (reflete as tochas).
				var size: Array = prop.get("size", [10, 4])
				var sludge := MeshInstance3D.new()
				var plane := BoxMesh.new()
				plane.size = Vector3(size[0], 0.1, size[1])
				sludge.mesh = plane
				sludge.position.y = 0.03
				sludge.material_override = _sludge_material()
				node.add_child(sludge)
			"water":
				# Mar do porto: um plano simples (04-tortuga-e-missoes.md, seção 6).
				var size: Array = prop.get("size", [40, 20])
				var tint: Array = prop.get("color", [0.07, 0.16, 0.24])  # riacho da Fazenda: água mais clara
				if prop.get("round", false):
					# Lagoa: elipse (o "size" é o diâmetro em x e em z).
					_prop_mesh(node, CylinderMesh.new(), Vector3(size[0], 0.05, size[1]), Vector3(0, 0.02, 0), Color(tint[0], tint[1], tint[2]))
					_block_pond(node, Vector2(size[0], size[1]))
				else:
					_prop_mesh(node, BoxMesh.new(), Vector3(size[0], 0.1, size[1]), Vector3(0, 0.02, 0), Color(tint[0], tint[1], tint[2]))
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
				var look: Dictionary = npc.get("body", {})
				if prop.has("visitor_name"):
					# Visitante: corpo e cabelo escolhidos pelo nome; sentado à mesa.
					var h := absi(hash(String(prop.visitor_name)))
					var hairs := [["Hair_SimpleParted", "Hair_Beard"], ["Hair_Buzzed"], ["Hair_Long"], ["Hair_Buns"]]
					var colors := [[0.2, 0.13, 0.08], [0.06, 0.06, 0.06], [0.55, 0.3, 0.12], [0.7, 0.62, 0.5]]
					look = {"sex": "male" if h % 2 == 0 else "female", "hair": hairs[h % 2 * 2 + (h / 2) % 2],
						"hair_color": colors[(h / 4) % colors.size()], "pose": "sit", "outfit": {"body": "cloth"} if h % 3 == 0 else {}}
				var seated_woman: bool = prop.has("visitor_name") and look.get("sex", "") == "female" and _visitor_woman(node)
				var own_model: Node3D = NpcModel.create(String(prop.npc)) if String(prop.npc) in ["voodoo_priest", "priest", "castle_guard", "court_jester", "seated_pirate", "elf_archer", "forest_reptile", "ruins_spartan", "old_lady", "forest_pyre_keeper", "sewer_scavenger", "sewer_ratcatcher"] else null
				var statue_kit: String = prop.get("kit", "")
				if statue_kit != "" and _kit(node, statue_kit, Transform3D(Basis(Vector3.UP, deg_to_rad(float(prop.get("rotation", 0.0)))), Vector3.ZERO)):
					# Estátua do mapa: a peça do kit no lugar do corpo humano; com "solid" ([largura, fundo]), o herói não atravessa (o altar do Esgoto).
					if prop.has("solid"):
						var blocker := StaticBody3D.new()
						blocker.collision_layer = 1
						blocker.collision_mask = 0
						var blocker_shape := CollisionShape3D.new()
						var blocker_box := BoxShape3D.new()
						blocker_box.size = Vector3(float(prop.solid[0]), 1.0, float(prop.solid[1]))
						blocker_shape.shape = blocker_box
						blocker.add_child(blocker_shape)
						blocker.position.y = 0.5
						node.add_child(blocker)
				elif own_model:
					node.add_child(own_model)
					if own_model.has_method("set_pose") and String(prop.npc) in ["seated_pirate", "old_lady", "sewer_scavenger", "sewer_ratcatcher", "elf_archer", "forest_reptile"]:  # a Aeliana (elf_archer) respira e se mexe parada no lugar (idle)
						own_model.call("set_pose", "sit" if String(prop.npc) == "old_lady" else "idle")  # o Macumbeiro (mago de capuz) e o Padre (monge) têm modelo próprio
				elif not seated_woman and _npc_body_with_instrument(node, look) == null:
					var body := CapsuleMesh.new()
					body.radius = 0.35
					body.height = 1.7
					_prop_mesh(node, body, Vector3.ONE, Vector3(0, 0.85, 0), color)
				if node is Wanderer and own_model:
					# NPC que passeia ("route": [[x, z], [x, z]]): vai e volta pela rota, parando nas pontas; a posição de interação o acompanha (como o mercador ambulante).
					var walker := node as Wanderer
					var route: Array = prop.route
					walker.from = Vector3(route[0][0], 0, route[0][1])
					walker.to = Vector3(route[1][0], 0, route[1][1])
					walker.speed = float(prop.get("speed", 1.0))
					walker.synced = true
					walker.tracked = prop
					walker.model = own_model
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
			"exit" when Kit.has("Portal_Well") and Kit.has("Portal_Crystal"):
				_portal_well(node)
			"exit":
				# Saída: moldura de porta / boca do bueiro / círculo do portal.
				_prop_mesh(node, CylinderMesh.new(), Vector3(1.4, 0.06, 1.4), Vector3(0, 0.03, 0), Color(0.25, 0.22, 0.2))
			"sign" when prop.get("look", "") == "crest":
				# Brasão do reino do Arqueiro na parede da passagem.
				_prop_mesh(node, BoxMesh.new(), Vector3(1.4, 1.8, 0.15), Vector3(0, 1.6, 0), Color(0.25, 0.32, 0.5))
				_prop_mesh(node, SphereMesh.new(), Vector3(0.5, 0.5, 0.1), Vector3(0, 1.7, 0.1), Color(0.8, 0.7, 0.3))
			"sign":
				_prop_mesh(node, CylinderMesh.new(), Vector3(2.2, 0.3, 2.2), Vector3(0, 0.15, 0), Color(0.35, 0.35, 0.4))
			"quest_spot" when _kit(node, "Crate_Wooden"):
				_prop_mesh(node, CylinderMesh.new(), Vector3(1.6, 0.03, 1.6), Vector3(0, 0.02, 0), Color(0.9, 0.75, 0.3))
			"quest_spot":
				# Lugar do rumor / carga perdida: caixote marcado.
				_prop_mesh(node, BoxMesh.new(), Vector3(0.9, 0.7, 0.9), Vector3(0, 0.35, 0), Color(0.55, 0.42, 0.25))
				_prop_mesh(node, CylinderMesh.new(), Vector3(1.6, 0.03, 1.6), Vector3(0, 0.02, 0), Color(0.9, 0.75, 0.3))
			"forge" when _forge_shed(node, prop) and _kit(node, "Anvil", Transform3D(Basis(), Vector3(-0.7, 0, 0))):
				_kit(node, "Workbench", Transform3D(Basis(), Vector3(1.0, 0, -0.3)))
				_kit(node, "Whetstone", Transform3D(Basis(), Vector3(-1.8, 0, 0)))
			"forge":
				# Forja ao ar livre: bigorna e fornalha acesa.
				_prop_mesh(node, BoxMesh.new(), Vector3(0.9, 0.7, 0.5), Vector3(-0.7, 0.35, 0), Color(0.25, 0.25, 0.27))
				_prop_mesh(node, BoxMesh.new(), Vector3(1.4, 1.2, 1.2), Vector3(0.9, 0.6, 0), Color(0.35, 0.25, 0.2))
				_prop_mesh(node, BoxMesh.new(), Vector3(0.6, 0.3, 0.05), Vector3(0.9, 0.7, 0.61), Color(1.0, 0.45, 0.1))
			"gate" when Kit.has("Boss_Gate"):
				# Portão do chefe: vários arcos de pedra com portão de ferro lado a lado ("count") fecham a passagem inteira; a colisão ("block": largura) bloqueia até as chaves das missões abrirem.
				var gate_scale := float(prop.get("scale", GATE_SCALE))
				var gate_count := int(prop.get("count", 1))
				var gate_yaw := deg_to_rad(float(prop.get("rotation", 0.0)))
				for g in gate_count:
					var piece_at := (g - (gate_count - 1) / 2.0) * 2.0 * gate_scale
					_kit(node, "Boss_Gate", Transform3D(Basis(Vector3.UP, gate_yaw).scaled(Vector3.ONE * gate_scale), Vector3(piece_at, 0, 0).rotated(Vector3.UP, gate_yaw)))
				var gate_body := StaticBody3D.new()
				gate_body.name = "gate_body"
				gate_body.collision_layer = 1
				gate_body.collision_mask = 0
				var gate_shape := CollisionShape3D.new()
				var gate_box := BoxShape3D.new()
				gate_box.size = Vector3(float(prop.get("block", 2.0 * gate_scale * gate_count + 0.2)), 6.0, 0.47 * gate_scale)
				gate_shape.shape = gate_box
				gate_body.add_child(gate_shape)
				gate_body.position.y = 2.0
				gate_body.rotation.y = gate_yaw
				node.add_child(gate_body)
			"chest" when prop.has("model") and _kit(node, String(prop.model), Transform3D(Basis(Vector3.UP, PI).scaled(Vector3.ONE * CHEST_SCALE), Vector3.ZERO)):
				pass  # baú do tesouro do chefe (de ferro, com cravos)
			"key" when _kit(node, String(prop.get("model", "Key_Gold")), Transform3D(Basis(Vector3.RIGHT,
					-PI / 2.0 if String(prop.get("model", "Key_Gold")) == "Key_Gold" else PI / 2.0), Vector3(0, 0.3, 0))):
				# Chave dourada caída, girando e brilhando.
				var glow := OmniLight3D.new()
				glow.light_color = Color(1.0, 0.8, 0.35)
				glow.omni_range = 3.0
				glow.light_energy = 1.2
				glow.position.y = 0.6
				node.add_child(glow)
				var spin := node.get_child(0).create_tween().set_loops()
				spin.tween_property(node.get_child(0), "rotation:y", TAU, 2.0).as_relative()
			"key":
				_prop_mesh(node, BoxMesh.new(), Vector3(0.15, 0.08, 0.6), Vector3(0, 0.3, 0), Color(0.95, 0.75, 0.25))
			"chest" when _kit(node, "Chest_Small", Transform3D(Basis(Vector3.UP, PI).scaled(Vector3.ONE * CHEST_SCALE), Vector3.ZERO),
					Color(0.55, 0.45, 0.4) if prop.get("secret", false) else Color.WHITE):
				pass  # baú de madeira com ferragens (o do segredo, mais escuro)
			"chest":
				# Baú do mapa; o do segredo fica escuro e sem nome, num canto.
				var wood := Color(0.3, 0.2, 0.12) if prop.get("secret", false) else Color(0.5, 0.34, 0.16)
				_prop_mesh(node, BoxMesh.new(), Vector3(1.2, 0.7, 0.8), Vector3(0, 0.35, 0), wood)
				_prop_mesh(node, BoxMesh.new(), Vector3(1.25, 0.12, 0.85), Vector3(0, 0.72, 0), Color(0.75, 0.6, 0.25))
			"bridge" when Kit.has("Floor_WoodDark"):
				# Ponte de tábuas escuras sobre o canal: ladrilhos de madeira do kit.
				var size: Array = prop.get("size", [4, 6])
				var nz := maxi(ceili(float(size[1]) / Kit.FLOOR_SIZE), 1)
				for iz in nz:
					var plank := Kit.piece("Floor_WoodDark")
					plank.scale = Vector3(float(size[0]) / Kit.FLOOR_SIZE, 1, float(size[1]) / nz / Kit.FLOOR_SIZE)
					plank.position = Vector3(0, 0.08, -float(size[1]) / 2.0 + float(size[1]) / nz * (iz + 0.5))
					node.add_child(plank)
				for side in [-1.0, 1.0]:
					_prop_mesh(node, BoxMesh.new(), Vector3(0.15, 0.5, size[1]), Vector3(side * float(size[0]) / 2.0, 0.3, 0), Color(0.25, 0.17, 0.1))
			"bridge":
				# Ponte de madeira podre sobre o canal (cenário).
				var size: Array = prop.get("size", [4, 6])
				_prop_mesh(node, BoxMesh.new(), Vector3(size[0], 0.12, size[1]), Vector3(0, 0.06, 0), Color(0.33, 0.24, 0.15))
			"stash" when _kit(node, "Chest_Small", Transform3D(Basis(Vector3.UP, PI).scaled(Vector3.ONE * CHEST_SCALE), Vector3.ZERO)):
				pass
			"stash":
				# Baú acorrentado.
				_prop_mesh(node, BoxMesh.new(), Vector3(1.4, 0.8, 0.9), Vector3(0, 0.4, 0), Color(0.4, 0.27, 0.15))
				_prop_mesh(node, BoxMesh.new(), Vector3(1.45, 0.1, 0.95), Vector3(0, 0.55, 0), Color(0.3, 0.3, 0.32))
			"training" when _kit(node, "WeaponStand"):
				pass
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


## Corpo de NPC (o mesmo dos heróis): sexo, cabelo, pose e roupa por slot
## (data/npcs.json "body"). null se o modelo não existe.
## Corpo do NPC; com "instrument": "guitar" no corpo (data/npcs.json), leva o alaúde no colo (o Bardo da Taverna).
func _npc_body_with_instrument(parent: Node3D, look: Dictionary) -> HeroModel:
	var model := _npc_body(parent, look)
	if model and look.get("instrument", "") == "guitar":
		_give_guitar(model)
	return model


func _npc_body(parent: Node3D, look: Dictionary) -> HeroModel:
	if look.is_empty() or not ResourceLoader.exists(HeroModel.SCENES.get(String(look.get("sex", "male")), "")):
		return null
	var model := HeroModel.new()
	parent.add_child(model)
	model.setup(String(look.get("sex", "male")), look)
	model.set_outfit(look.get("outfit", {}))
	model.set_pose(String(look.get("pose", "idle")))
	if look.get("mug", false) and Kit.has("Mug_Wood"):
		model.attach("hand_r", Kit.piece("Mug_Wood"), Player.HAND_GRIP, Vector3(0.4, 0.9, 0.1))
	if not look.get("clothes", {}).is_empty():
		Clothing.dress(model, Clothing.HERO_BONES, look.clothes)
	# Arma na mão direita (soldados treinando): cada golpe começa num ponto diferente do ciclo.
	var weapon := String(look.get("weapon", ""))
	if weapon != "" and Kit.has(weapon):
		var piece := Kit.piece(weapon)
		piece.position = Vector3(0, 0.12, 0)
		var grip := Node3D.new()
		grip.add_child(piece)
		model.attach("hand_r", grip, Player.HAND_GRIP, Vector3(0.45, 0.9, 0.15))
		model.desync(randf())
	return model


## Visitante da Taverna (Bartender, cdmir, CC0): blusa, saia e cabelo preso,
## sentada à mesa. O arquivo tem 14,6 unidades de altura: escala para 1,7 m.
const VISITOR_WOMAN := "res://assets/models/characters/visitor_woman.glb"
const VISITOR_WOMAN_SCALE := 0.116


func _visitor_woman(parent: Node3D) -> bool:
	if not ResourceLoader.exists(VISITOR_WOMAN):
		return false
	var model := (load(VISITOR_WOMAN) as PackedScene).instantiate() as Node3D
	model.scale = Vector3.ONE * VISITOR_WOMAN_SCALE
	parent.add_child(model)
	var anim := model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if anim and anim.has_animation("sit"):
		anim.get_animation("sit").loop_mode = Animation.LOOP_LINEAR
		anim.play("sit")
	return true


## Corpo de uma pessoa da rua pelo papel (data/crowd.json), escolhido pela
## posição: igual em todos os PCs. {} se o papel não existe.
func _crowd_look(role_name: String, at: Vector3, entry: Dictionary) -> Dictionary:
	var role: Dictionary = GameData.crowd.get("roles", {}).get(role_name, {})
	if role.is_empty():
		return {}
	var h := absi(hash(Vector2(at.x, at.z)))
	var sexes: Array = role.get("sex", ["male"])
	var sex: String = entry.get("sex", sexes[h % sexes.size()])
	var hairs: Array = role.get("hair", {}).get(sex, [[]])
	var colors: Array = role.get("hair_color", [[0.2, 0.15, 0.1]])
	var outfits: Array = role.get("outfit", [{}])
	return {"sex": sex, "hair": hairs[(h / 7) % hairs.size()], "hair_color": colors[(h / 13) % colors.size()],
		"outfit": outfits[(h / 29) % outfits.size()], "pose": entry.get("pose", "idle"),
		"weapon": entry.get("weapon", role.get("weapon", "")) if String(entry.get("pose", "idle")).begins_with("melee") or entry.has("weapon") else "",
		"clothes": _crowd_clothes(role, sex, h)}


## Roupa por cima do corpo (colete, túnica, camisa de cadarço, vestido de linho), sorteada
## pela posição: o papel lista os estilos de cada sexo em data/crowd.json ("clothes").
func _crowd_clothes(role: Dictionary, sex: String, h: int) -> Dictionary:
	var styles: Array = role.get("clothes", {}).get(sex, [])
	if styles.is_empty():
		return {}
	return NpcModel.clothing_style(styles[(h / 31) % styles.size()])


## Briga de rua: dois brigões (papéis em "fighters") frente a frente, trocando socos e chutes.
func _build_brawl(entry: Dictionary, at: Vector3) -> void:
	var brawl := Brawl.new()
	brawl.position = at
	brawl.rotation.y = deg_to_rad(float(entry.get("rotation", 0.0)))
	_area_root.add_child(brawl)
	var roles: Array = entry.get("fighters", ["drunk", "pirate"])
	for i in 2:
		var holder := Node3D.new()
		holder.position.x = (i - 0.5) * Brawl.GAP
		holder.rotation.y = PI / 2.0 if i == 0 else -PI / 2.0  # um de frente para o outro
		brawl.add_child(holder)
		var spot := at + Vector3((i - 0.5) * 3.0, 0, 0.7 * i)
		var model := _npc_body(holder, _crowd_look(String(roles[i]), spot, {"pose": "idle"}))
		if model:
			brawl.fighters.append(model)
			brawl.roles.append(String(roles[i]))


## Gente da rua (data/crowd.json + "crowd" da área): o corpo vem do papel,
## escolhido pela posição (igual em todos os PCs); com "path", vai e volta.
func _build_crowd(entry: Dictionary) -> void:
	var at := Vector3(entry.position[0], 0, entry.position[1])
	if entry.role == "brawl":
		_build_brawl(entry, at)
		return
	var look := _crowd_look(String(entry.role), at, entry)
	if look.is_empty() and not NpcModel.has_model(String(entry.role)):
		return
	var path: Array = entry.get("path", [])
	var node: Node3D = Wanderer.new() if not path.is_empty() else Node3D.new()
	node.position = at
	node.rotation.y = deg_to_rad(float(entry.get("rotation", 0.0)))
	_area_root.add_child(node)
	if entry.has("seat"):
		var seat := Kit.piece(String(entry.seat))
		if seat:
			node.add_child(seat)
	# Papéis com modelo próprio (a cortesã); senão, o corpo dos heróis.
	var model: Node3D = NpcModel.create(String(entry.role)) if NpcModel.has_model(String(entry.role)) else null
	if model:
		node.add_child(model)
		model.call("set_pose", String(entry.get("pose", "idle")))
	else:
		model = _npc_body(node, look)
		if model and entry.get("instrument", "") == "guitar":
			_give_guitar(model)
		# Bêbados com o caneco de madeira na mão.
		if model is HeroModel and (String(entry.role) == "drunk" or GameData.crowd.get("roles", {}).get(String(entry.role), {}).get("mug", false)) and Kit.has("Mug_Wood"):
			(model as HeroModel).attach("hand_r", Kit.piece("Mug_Wood"), Player.HAND_GRIP, Vector3(0.4, 0.9, 0.1))
	if model and node is Wanderer:
		var walker := node as Wanderer
		walker.from = at
		walker.to = Vector3(path[0], 0, path[1])
		walker.sway = float(entry.get("sway", 0.0))
		walker.speed = float(entry.get("speed", 1.2))
		walker.model = model
		model.call("set_pose", "walk")


## Cobertura da forja (o telhado de pano xadrez da barraca "patch"); sempre verdadeiro,
## para encaixar na condição de quem monta a forja.
func _forge_shed(node: Node3D, prop: Dictionary) -> bool:
	if prop.has("stall"):
		node.add_child(MarketStall.build(String(prop.stall)))
	return true


## Põe uma peça do kit dentro do objeto; false se a peça não existe (o objeto
## usa o visual simples). `tint` escurece/colore os materiais da peça.
func _kit(parent: Node3D, piece_name: String, offset := Transform3D.IDENTITY, tint := Color.WHITE) -> bool:
	var piece := Kit.piece(piece_name)
	if piece == null:
		return false
	piece.transform = offset
	parent.add_child(piece)
	if tint != Color.WHITE:
		for mesh in piece.find_children("*", "MeshInstance3D", true, false):
			var m := mesh as MeshInstance3D
			for i in m.get_surface_override_material_count():
				var material := m.get_active_material(i) as StandardMaterial3D
				if material:
					var copy := material.duplicate() as StandardMaterial3D
					copy.albedo_color = copy.albedo_color * tint
					m.set_surface_override_material(i, copy)
	return true


## Lodo do esgoto (canais, câmaras alagadas): verde-escuro, liso e brilhante.
func _sludge_material() -> StandardMaterial3D:
	if _sludge == null:
		_sludge = StandardMaterial3D.new()
		_sludge.albedo_color = Color(0.09, 0.13, 0.06)
		_sludge.roughness = 0.08
		_sludge.metallic = 0.3
		_sludge.metallic_specular = 0.8
	return _sludge


## Lagoa que os jogadores não atravessam (monstros e peixes sim): um prisma de colisão com o contorno da elipse (o "size" é o diâmetro em x e em z).
func _block_pond(node: Node3D, size: Vector2) -> void:
	var points := PackedVector3Array()
	for i in 32:
		var a := TAU * float(i) / 32.0
		var p := Vector3(cos(a) * size.x / 2.0, 0.0, sin(a) * size.y / 2.0)
		points.append(p)
		points.append(p + Vector3(0, 1.5, 0))
	var shape := ConvexPolygonShape3D.new()
	shape.points = points
	var body := StaticBody3D.new()
	body.collision_layer = 16  # camada das lagoas: só jogadores e companheiros colidem (monstros e peixes passam)
	body.collision_mask = 0
	var col := CollisionShape3D.new()
	col.shape = shape
	body.add_child(col)
	node.add_child(body)


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
	# Estilo da área (data/arenas.json): paredes e pisos do kit por cima das
	# caixas de colisão, que ficam invisíveis. Sem estilo (área de teste) ou sem
	# as peças, as caixas aparecem como antes.
	var style: Dictionary = arena.get("style", {})
	var dressed := not style.is_empty() and Kit.has(String(style.get("floor", "")))
	# Tinta do estilo (o limo verde do esgoto) por cima das cores do kit.
	var t: Array = style.get("tint", [1, 1, 1])
	_style_tint = Color(t[0], t[1], t[2])
	_tinted.clear()
	var wt: Array = style.get("wood_tone", [])
	_wood_tone = Color(wt[0], wt[1], wt[2], 1.0) if wt.size() >= 3 else Color(0, 0, 0, 0)
	_toned.clear()
	_pipes.clear()
	_cut_walls.clear()
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
		_wall_x(c.x, c.z - half.z, half.x * 2.0, doors.has("north"), height, doors.get("north", 0.0), not dressed)
		_wall_x(c.x, c.z + half.z, half.x * 2.0, doors.has("south"), height, doors.get("south", 0.0), not dressed)
		_wall_z(c.x - half.x - 0.5, c.z, half.z * 2.0 + 2.0, doors.has("west"), height, doors.get("west", 0.0), not dressed)
		_wall_z(c.x + half.x + 0.5, c.z, half.z * 2.0 + 2.0, doors.has("east"), height, doors.get("east", 0.0), not dressed)
		if dressed:
			_dress_room(room, style, c, half, doors, height)
	var center := bounds.get_center()
	_box(Vector3(center.x, -0.5, center.z), Vector3(bounds.size.x + 4, 1, bounds.size.z + 4),
		Color(style.get("ground", [0.12, 0.11, 0.1])[0], style.get("ground", [0.12, 0.11, 0.1])[1],
			style.get("ground", [0.12, 0.11, 0.1])[2]) if dressed else FLOOR_COLOR)
	if not arena.get("town", false):
		_build_save_crystal()
	if dressed:
		for decor: Dictionary in arena.get("decor", []):
			_build_decor(decor)
		for person: Dictionary in arena.get("crowd", []):
			_build_crowd(person)


## Portal-poço (Well of Lost Souls, bobjh, e Light crystal, Pompei2): um cristal azul brilhante gira e flutua dentro do poço, com uma luz azul;
## é o desenho das saídas dos mapas (return_portal e portões). Sem as peças, fica o círculo simples.
func _portal_well(node: Node3D) -> void:
	var well := Kit.piece("Portal_Well")
	node.add_child(well)
	var crystal := Kit.piece("Portal_Crystal")
	crystal.position = Vector3(0, 0.62, 0)
	node.add_child(crystal)
	var glow := OmniLight3D.new()
	glow.light_color = Color(0.45, 0.7, 1.0)
	glow.omni_range = 4.5
	glow.light_energy = 1.4
	glow.position = Vector3(0, 1.0, 0)
	node.add_child(glow)
	var spin := crystal.create_tween().set_loops()
	spin.tween_property(crystal, "rotation:y", TAU, 6.0).as_relative()
	var bob := crystal.create_tween().set_loops()
	bob.tween_property(crystal, "position:y", 0.74, 1.4).set_trans(Tween.TRANS_SINE)
	bob.tween_property(crystal, "position:y", 0.62, 1.4).set_trans(Tween.TRANS_SINE)


## Reveste a sala com as peças do kit: piso em ladrilhos de 2 m, paredes de
## 2 m viradas para dentro (o padrão do estilo varia janelas e portas falsas)
## e, na parede sul e nas muretas, a cerca baixa — a câmera olha do sul, então
## a parede de baixo fica cortada para o herói aparecer (09-interface.md, seção 2).
func _dress_room(room: Dictionary, style: Dictionary, c: Vector3, half: Vector3, doors: Dictionary, height: float) -> void:
	var floor_piece: String = room.get("floor", style.floor)
	if floor_piece == "Dirt":
		var dirt := MeshInstance3D.new()
		var plane := PlaneMesh.new()
		plane.size = Vector2(half.x * 2.0, half.z * 2.0)
		dirt.mesh = plane
		dirt.material_override = _dirt_material()
		dirt.position = Vector3(c.x, 0.01, c.z)
		_area_root.add_child(dirt)
		floor_piece = ""
	var nx := maxi(ceili(half.x * 2.0 / Kit.FLOOR_SIZE), 1)
	var nz := maxi(ceili(half.z * 2.0 / Kit.FLOOR_SIZE), 1)
	var tile := Vector2(half.x * 2.0 / nx, half.z * 2.0 / nz)
	for ix in nx:
		for iz in nz:
			var node := Kit.piece(floor_piece) if floor_piece != "" else null
			if node:
				node.scale = Vector3(tile.x / Kit.FLOOR_SIZE, 1, tile.y / Kit.FLOOR_SIZE)
				node.position = Vector3(c.x - half.x + tile.x * (ix + 0.5), 0.01, c.z - half.z + tile.y * (iz + 0.5))
				_area_root.add_child(node)
				_tint_piece(node)
				_tone_wood(node, floor_piece)
				if floor_piece == "Floor_WoodDark" and style.get("wood", false):
					_deckify(node)
	var low := height < 1.5
	var walls: Array = room.get("walls", style.get("walls", []))
	var fence: String = style.get("low", "")
	# Norte: a caixa fica centrada na borda (a face de dentro, 0,5 m para dentro).
	_dress_side(Vector3(c.x, 0, c.z - half.z + 0.5), Vector3.RIGHT, Vector3.BACK, half.x * 2.0,
		doors.has("north"), doors.get("north", 0.0), [fence] if low else walls)
	_dress_side(Vector3(c.x, 0, c.z + half.z - 0.5), Vector3.RIGHT, Vector3.FORWARD, half.x * 2.0,
		doors.has("south"), doors.get("south", 0.0), [fence])
	# Leste e oeste: a caixa fica do lado de fora (a face de dentro é a borda).
	_dress_side(Vector3(c.x - half.x, 0, c.z), Vector3.BACK, Vector3.RIGHT, half.z * 2.0,
		doors.has("west"), doors.get("west", 0.0), [fence] if low else walls)
	_dress_side(Vector3(c.x + half.x, 0, c.z), Vector3.BACK, Vector3.LEFT, half.z * 2.0,
		doors.has("east"), doors.get("east", 0.0), [fence] if low else walls)
	# Esgoto: sujeira escorrendo nas paredes e poças de água suja no chão.
	if style.get("grime", false) and not low:
		var rng := RandomNumberGenerator.new()
		rng.seed = hash(str(room.get("id", ""), c))
		_grime_side(Vector3(c.x, 0, c.z - half.z + 0.5), Vector3.RIGHT, Vector3.BACK, half.x * 2.0,
			doors.has("north"), doors.get("north", 0.0), rng)
		_grime_side(Vector3(c.x - half.x, 0, c.z), Vector3.BACK, Vector3.RIGHT, half.z * 2.0,
			doors.has("west"), doors.get("west", 0.0), rng)
		_grime_side(Vector3(c.x + half.x, 0, c.z), Vector3.BACK, Vector3.LEFT, half.z * 2.0,
			doors.has("east"), doors.get("east", 0.0), rng)
	if style.get("trash", false):
		_scatter_trash(room, c, half)
	if style.get("spiders", false):
		_scatter_spiders(room, c, half)
		_scatter_critters(room, c, half, "rat", 0.4, 2)  # ratos do Esgoto: poucos por sala (até 2)
	if style.get("bats", false):
		_scatter_bats(room, c, half)
	if style.get("grates", false):
		var grng := RandomNumberGenerator.new()
		grng.seed = hash(str(room.get("id", ""), c, "grates"))
		for i in clampi(roundi(half.x * half.z / 40.0), 0, 3):
			_floor_grate(Vector3(c.x + grng.randf_range(-half.x + 1.5, half.x - 1.5), 0, c.z + grng.randf_range(-half.z + 1.5, half.z - 1.5)), grng)
	if style.get("puddles", false):
		var rng := RandomNumberGenerator.new()
		rng.seed = hash(str(room.get("id", ""), c, "puddles"))
		for i in maxi(roundi(half.x * half.z * 8.0 / 70.0), 2):
			var at := Vector3(c.x + rng.randf_range(-half.x + 1.0, half.x - 1.0), 0.025,
				c.z + rng.randf_range(-half.z + 1.0, half.z - 1.0))
			_puddle(at, rng.randf_range(0.6, 1.6), rng)
	# Telhados atrás das casas do lado norte (a câmera vê a fachada e o telhado).
	var roof: String = style.get("roof", "")
	if room.get("roofs", false) and roof != "" and not low:
		for segment in _wall_pieces(half.x * 2.0, doors.has("north"), doors.get("north", 0.0)):
			var count := floori(segment.y / ROOF_WIDTH)
			for i in count:
				var node := Kit.piece(roof)
				if node:
					var x := c.x + segment.x - segment.y / 2.0 + (segment.y - count * ROOF_WIDTH) / 2.0 + ROOF_WIDTH * (i + 0.5)
					node.position = Vector3(x, 3.4, c.z - half.z - ROOF_WIDTH / 2.0 + 0.6)
					_area_root.add_child(node)
					if style.get("thatch", false):
						_thatchify(node)
					_close_gable(node)
	# Lampião na parede norte das salas com tocha.
	if room.get("torch", false) and not low:
		var lantern := Kit.piece("Lantern_Wall")
		if lantern:
			lantern.position = Vector3(c.x, 1.4, c.z - half.z + 0.5)
			_area_root.add_child(lantern)


var _gable_material: StandardMaterial3D


## Fecha o triângulo aberto na frente do telhado (a câmera olha do sul e via o vão escuro por baixo da palha):
## uma tábua triangular um pouco para dentro da beirada, no formato do perfil do telhado (beiral em y -0,5, cumeeira em 3,3).
func _close_gable(roof_node: Node3D) -> void:
	if _gable_material == null:
		# Tábuas (a mesma textura das paredes de madeira); sem a textura, uma cor lisa de madeira.
		_gable_material = _tiled_material("wood_wall_1", Vector3(0.5, 0.5, 0.5), Color(0.95, 0.8, 0.62))
		if _gable_material == null:
			_gable_material = StandardMaterial3D.new()
			_gable_material.albedo_color = Color(0.3, 0.21, 0.13)
			_gable_material.roughness = 0.95
		_match_wood_tone(_gable_material)
		_gable_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = PackedVector3Array([Vector3(-2.75, -0.55, 2.3), Vector3(2.75, -0.55, 2.3), Vector3(0, 3.35, 2.3)])
	arrays[Mesh.ARRAY_NORMAL] = PackedVector3Array([Vector3.BACK, Vector3.BACK, Vector3.BACK])
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var gable := MeshInstance3D.new()
	gable.mesh = mesh
	gable.material_override = _gable_material
	gable.name = "gable"
	roof_node.add_child(gable)


## Cristal de save (Mese Crystal, rubberduck, CC0) ao lado do checkpoint da
## área: gira devagar e flutua subindo e descendo, com uma luz amarela fraca.
func _build_save_crystal() -> void:
	_crystal_material = null
	var crystal := Kit.piece("Save_Crystal")
	if crystal == null:
		return
	var holder := Node3D.new()
	holder.name = "save_crystal"
	holder.position = entry_point(String(arena.get("save_point", "start"))) + Vector3(2.2, 0, -0.5)  # "save_point": entrada onde fica o cristal (padrão: o início da área)
	_area_root.add_child(holder)
	var bob := Node3D.new()
	holder.add_child(bob)
	bob.add_child(crystal)
	for node in crystal.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		var source := mesh.get_active_material(0) as StandardMaterial3D
		_crystal_material = (source.duplicate() if source else StandardMaterial3D.new()) as StandardMaterial3D
		_crystal_material.emission_enabled = true
		_crystal_material.emission = Color(1.0, 0.85, 0.25)
		_crystal_material.emission_energy_multiplier = 0.6
		for i in mesh.get_surface_override_material_count():
			mesh.set_surface_override_material(i, _crystal_material)
	var light := OmniLight3D.new()
	light.name = "glow"
	light.light_color = Color(1.0, 0.85, 0.3)
	light.omni_range = 4.0
	light.light_energy = 0.6
	light.position.y = 1.4
	holder.add_child(light)
	bob.position.y = 0.9
	var float_tween := bob.create_tween().set_loops()
	float_tween.tween_property(bob, "position:y", 1.25, 1.4).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	float_tween.tween_property(bob, "position:y", 0.9, 1.4).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	var spin := crystal.create_tween().set_loops()
	spin.tween_property(crystal, "rotation:y", TAU, 6.0).as_relative()


## O jogo salvou no checkpoint: o cristal acende forte e volta ao brilho fraco.
@rpc("authority", "call_local", "reliable")
func _crystal_glow() -> void:
	var holder := _area_root.get_node_or_null("save_crystal") if _area_root else null
	if holder == null or _crystal_material == null:
		return
	var light := holder.get_node("glow") as OmniLight3D
	var tween := holder.create_tween().set_parallel()
	_crystal_material.emission_energy_multiplier = 6.0
	light.light_energy = 4.0
	light.omni_range = 9.0
	tween.tween_property(_crystal_material, "emission_energy_multiplier", 0.6, 1.6).set_ease(Tween.EASE_IN)
	tween.tween_property(light, "light_energy", 0.6, 1.6).set_ease(Tween.EASE_IN)
	tween.tween_property(light, "omni_range", 4.0, 1.6)


## Madeira de um tom só (style.wood_tone): nas peças da área, os materiais de madeira (nome com "wood", a "MI_Trim_Furniture" do kit de móveis e o único
## material dos barris e canecas de madeira) ficam com a cor média igual ao tom, mantendo o relevo da textura; fosco e sem metal. Metal, vidro e gesso não mudam.
func _tone_wood(node: Node3D, piece_name: String) -> void:
	if _wood_tone.a == 0.0:
		return
	for mesh in node.find_children("*", "MeshInstance3D", true, false):
		var m := mesh as MeshInstance3D
		for i in m.get_surface_override_material_count():
			var material := m.get_active_material(i) as StandardMaterial3D
			if material == null or not _is_wood_material(material, piece_name):
				continue
			if not _toned.has(material):
				var copy := material.duplicate() as StandardMaterial3D
				var average := _material_average(material)
				copy.albedo_color = Color(
					copy.albedo_color.r * _wood_tone.r / maxf(average.r, 0.01),
					copy.albedo_color.g * _wood_tone.g / maxf(average.g, 0.01),
					copy.albedo_color.b * _wood_tone.b / maxf(average.b, 0.01))
				copy.roughness = 0.85
				copy.metallic = 0.0
				_toned[material] = copy
			m.set_surface_override_material(i, _toned[material])


func _is_wood_material(material: StandardMaterial3D, piece_name: String) -> bool:
	var material_name := String(material.resource_name).to_lower()
	return material_name.contains("wood") or material_name == "mi_trim_furniture" \
		or (piece_name in ["Beer_Barrel", "Mug_Wood"] and material_name == "material.001")


## Cor média do material (média da textura de cor vezes a cor base), guardada por textura.
func _material_average(material: StandardMaterial3D) -> Color:
	var texture := material.albedo_texture
	var average := Color.WHITE
	if texture:
		if not _wood_average.has(texture):
			var image := texture.get_image()
			if image == null:
				_wood_average[texture] = Color.WHITE
			else:
				if image.is_compressed():
					image.decompress()
				image.resize(16, 16)
				var sum := Color(0, 0, 0, 1)
				for y in 16:
					for x in 16:
						var c := image.get_pixel(x, y)
						sum = Color(sum.r + c.r, sum.g + c.g, sum.b + c.b, 1.0)
				_wood_average[texture] = Color(sum.r / 256.0, sum.g / 256.0, sum.b / 256.0, 1.0)
		average = _wood_average[texture]
	return Color(average.r * material.albedo_color.r, average.g * material.albedo_color.g, average.b * material.albedo_color.b)


## Peça do kit na tinta do estilo; os materiais tingidos são compartilhados
## (um por material original), então custa pouco por peça.
func _tint_piece(node: Node3D, extra := Color.WHITE) -> void:
	if _style_tint == Color.WHITE and extra == Color.WHITE:
		return
	var tint := _style_tint * extra
	for mesh in node.find_children("*", "MeshInstance3D", true, false):
		var m := mesh as MeshInstance3D
		for i in m.get_surface_override_material_count():
			var material := m.get_active_material(i) as StandardMaterial3D
			if material == null:
				continue
			var key := [material, extra]
			if not _tinted.has(key):
				var copy := material.duplicate() as StandardMaterial3D
				copy.albedo_color = copy.albedo_color * tint
				copy.roughness = maxf(copy.roughness, 0.9) if extra != Color.WHITE else copy.roughness
				copy.metallic = 0.0 if extra != Color.WHITE else copy.metallic
				_tinted[key] = copy
			m.set_surface_override_material(i, _tinted[key])


## Casas de madeira (estilo "wood", Tortuga): troca o reboco e o tijolo da parede pela madeira do
## próprio kit (a de MI_WoodTrim, a mesma das vigas), em tábuas mais escuras que as vigas (as paredes, a base de pedra e o telhado).
const WOOD_PLANK := Color(0.72, 0.6, 0.5)
## Só a faixa de madeira escura do atlas (o resto tem blocos e pedra): v de 0,33 a 0,61.
const WOOD_UV_SCALE := Vector3(3, 0.27, 1)
const WOOD_UV_OFFSET := Vector3(0, 0.34, 0)
## Materiais do kit que viram madeira: reboco, tijolo e pedra da base.
const WOOD_REPLACES: Array[String] = ["Plaster", "Brick", "Rock"]
var _planks := {}


func _woodify(node: Node3D) -> void:
	for mesh in node.find_children("*", "MeshInstance3D", true, false):
		var m := mesh as MeshInstance3D
		var trim: StandardMaterial3D = null
		for i in m.get_surface_override_material_count():
			var material := m.get_active_material(i) as StandardMaterial3D
			if material and material.resource_name.contains("WoodTrim"):
				trim = material
				break
		if trim == null:
			continue
		if not _planks.has(trim):
			var boards := _tiled_material("wood_wall_1", Vector3(0.5, 0.25, 0.5), Color(0.95, 0.8, 0.62))
			var copy := boards if boards else trim.duplicate() as StandardMaterial3D
			if boards == null:
				copy.albedo_color = copy.albedo_color * WOOD_PLANK
				copy.uv1_scale = WOOD_UV_SCALE
				copy.uv1_offset = WOOD_UV_OFFSET
			_match_wood_tone(copy)
			_planks[trim] = copy
		for i in m.get_surface_override_material_count():
			var material := m.get_active_material(i) as StandardMaterial3D
			if material and WOOD_REPLACES.any(func(part: String) -> bool: return material.resource_name.contains(part)):
				m.set_surface_override_material(i, _planks[trim])


## Convés do porto e da doca: o piso de tábuas do kit troca a madeira pelas tábuas fotográficas.
func _deckify(node: Node3D) -> void:
	if _deck == null:
		_deck = _tiled_material("wood_floor_2", Vector3.ONE * 0.5, Color(0.92, 0.8, 0.68))
	if _deck == null:
		return
	_match_wood_tone(_deck)
	for mesh in node.find_children("*", "MeshInstance3D", true, false):
		var m := mesh as MeshInstance3D
		for i in m.get_surface_override_material_count():
			m.set_surface_override_material(i, _deck)


var _deck: StandardMaterial3D


## Violão no colo do músico sentado (feito em código): caixa, boca escura e braço para a esquerda dele;
## balança de leve, como quem dedilha.
func _give_guitar(model: HeroModel) -> void:
	var guitar := Node3D.new()
	# O alaúde de verdade (Lute, aerojockey / Snabisch, CC0), quando há; senão o violão de caixa e cilindros abaixo.
	var lute := Kit.piece("Lute")
	if lute:
		lute.rotation.x = PI / 2.0  # as cordas para a frente (o arquivo deixa as cordas para cima)
		lute.position = Vector3(0.28, 0, 0)
		guitar.add_child(lute)
		_place_guitar(model, guitar)
		return
	var wood := _wood_material()
	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.05, 0.03, 0.02)
	for part: Array in [[0.0, 0.0, 0.2, 0.22], [0.2, 0.0, 0.16, 0.18]]:
		var body := MeshInstance3D.new()
		var cyl := CylinderMesh.new()
		cyl.top_radius = part[3]
		cyl.bottom_radius = part[3]
		cyl.height = 0.09
		body.mesh = cyl
		body.material_override = wood
		body.rotation.x = PI / 2.0
		body.position = Vector3(part[0] * 0.0 - part[1], part[1], 0)
		body.position = Vector3(-part[0] * 0.5, 0, 0)
		guitar.add_child(body)
	var hole := MeshInstance3D.new()
	var disc := CylinderMesh.new()
	disc.top_radius = 0.055
	disc.bottom_radius = 0.055
	disc.height = 0.01
	hole.mesh = disc
	hole.material_override = dark
	hole.rotation.x = PI / 2.0
	hole.position = Vector3(-0.02, 0, 0.047)
	guitar.add_child(hole)
	var neck := MeshInstance3D.new()
	var neck_box := BoxMesh.new()
	neck_box.size = Vector3(0.6, 0.05, 0.035)
	neck.mesh = neck_box
	neck.material_override = dark
	neck.position = Vector3(0.38, 0, 0)
	guitar.add_child(neck)
	# Cabeça: onde ficam as tarraxas.
	var head := MeshInstance3D.new()
	var head_box := BoxMesh.new()
	head_box.size = Vector3(0.12, 0.07, 0.03)
	head.mesh = head_box
	head.material_override = wood
	head.position = Vector3(0.72, 0, 0)
	guitar.add_child(head)
	_place_guitar(model, guitar)


## Põe o instrumento no colo do músico e o balança de leve, como quem dedilha.
func _place_guitar(model: HeroModel, guitar: Node3D) -> void:
	guitar.scale = Vector3.ONE * (0.9 if guitar.get_child_count() == 1 else 0.7)
	guitar.position = Vector3(0.0, 0.95, 0.22)
	guitar.rotation = Vector3(0, deg_to_rad(-12), deg_to_rad(18))
	model.add_child(guitar)
	var strum := guitar.create_tween().set_loops()
	strum.tween_property(guitar, "rotation:z", deg_to_rad(21), 0.35).set_trans(Tween.TRANS_SINE)
	strum.tween_property(guitar, "rotation:z", deg_to_rad(15), 0.35).set_trans(Tween.TRANS_SINE)


## Biblioteca de texturas dos mapas (assets/textures/maps, Lattice, CC0): null se faltar o arquivo,
## e quem usa mantém o visual gerado em código.
func _map_texture(file: String) -> Texture2D:
	var path := "res://assets/textures/maps/%s.webp" % file
	return load(path) as Texture2D if ResourceLoader.exists(path) else null


## Material de textura contínua projetada pelos três eixos (serve em qualquer peça, sem depender do UV);
## `scale_` em repetições por metro (a textura de 480 px cobre ~1/scale m).
func _tiled_material(file: String, scale_: Vector3, tint := Color.WHITE, rough := 0.95) -> StandardMaterial3D:
	var texture := _map_texture(file)
	if texture == null:
		return null
	var material := StandardMaterial3D.new()
	material.albedo_texture = texture
	material.albedo_color = tint
	material.uv1_triplanar = true
	material.uv1_scale = scale_
	material.roughness = rough
	return material


## Terra batida (rua de Tortuga) e palha (telhados): geradas por ruído, não há no kit.
var _dirt: StandardMaterial3D
var _thatch: StandardMaterial3D


func _noise_texture(dark: Color, light: Color, stretch: Vector2, frequency: float, seed_: int) -> ImageTexture:
	var noise := FastNoiseLite.new()
	noise.seed = seed_
	noise.frequency = frequency
	noise.fractal_octaves = 4
	var size := 256
	var image := Image.create(size, size, false, Image.FORMAT_RGB8)
	for y in size:
		for x in size:
			var v := noise.get_noise_2d(x * stretch.x, y * stretch.y) * 0.5 + 0.5
			image.set_pixel(x, y, dark.lerp(light, clampf(v * 1.3 - 0.15, 0.0, 1.0)))
	return ImageTexture.create_from_image(image)


func _dirt_material() -> StandardMaterial3D:
	if _dirt == null:
		_dirt = _tiled_material("dirt_1", Vector3.ONE * 0.22, Color(0.78, 0.62, 0.46), 1.0)
	if _dirt == null:
		_dirt = StandardMaterial3D.new()
		_dirt.albedo_texture = _noise_texture(Color(0.25, 0.17, 0.1), Color(0.42, 0.31, 0.19), Vector2.ONE, 0.035, 11)
		_dirt.uv1_triplanar = true
		_dirt.uv1_scale = Vector3.ONE * 0.12
		_dirt.roughness = 1.0
	return _dirt


## Telhado de palha: troca a telha do kit por palha amarelada, com fios no sentido da água.
func _thatchify(node: Node3D) -> void:
	if _thatch == null:
		_thatch = _tiled_material("thatch_2", Vector3.ONE * 0.4, Color(1.2, 0.98, 0.62), 1.0)
	if _thatch == null:
		_thatch = StandardMaterial3D.new()
		_thatch.albedo_texture = _noise_texture(Color(0.45, 0.33, 0.14), Color(0.86, 0.72, 0.38), Vector2(1.0, 0.07), 0.12, 23)
		_thatch.uv1_triplanar = true
		_thatch.uv1_scale = Vector3.ONE * 0.45
		_thatch.roughness = 1.0
	for mesh in node.find_children("*", "MeshInstance3D", true, false):
		var m := mesh as MeshInstance3D
		for i in m.get_surface_override_material_count():
			var material := m.get_active_material(i) as StandardMaterial3D
			if material and material.resource_name.contains("Tiles"):
				m.set_surface_override_material(i, _thatch)


## Madeira escura lisa (a faixa de madeira do atlas do kit, recortada): tábuas e estátua.
var _wood_flat: StandardMaterial3D


func _wood_material() -> StandardMaterial3D:
	if _wood_flat == null:
		_wood_flat = _tiled_material("wood_3", Vector3.ONE * 0.9, Color(1.15, 0.82, 0.58), 0.9)
	if _wood_flat == null:
		_wood_flat = StandardMaterial3D.new()
		_wood_flat.roughness = 0.9
		_wood_flat.albedo_color = Color(0.85, 0.75, 0.68)
		var texture := load("res://assets/models/village/T_WoodTrim_BaseColor.webp") as Texture2D
		if texture:
			var image := texture.get_image()
			if image.is_compressed():
				image.decompress()
			var scale_ := image.get_width() / 1024.0
			_wood_flat.albedo_texture = ImageTexture.create_from_image(
				image.get_region(Rect2i(0, int(335 * scale_), image.get_width(), int(280 * scale_))))
			_wood_flat.uv1_triplanar = true
			_wood_flat.uv1_scale = Vector3.ONE * 0.9
	if not _wood_flat_toned:
		_wood_flat_toned = true
		_match_wood_tone(_wood_flat)
	return _wood_flat


var _wood_flat_toned := false


## Madeira de um tom só (style.wood_tone) nos materiais de madeira feitos em código (paredes de tábuas, convés,
## tábuas e estátua, tímpano do telhado): a cor média da textura passa a ser o tom, mantendo o relevo. O material é trocado no lugar.
func _match_wood_tone(material: StandardMaterial3D) -> void:
	if _wood_tone.a == 0.0 or material == null:
		return
	var average := _material_average(material)
	material.albedo_color = Color(
		material.albedo_color.r * _wood_tone.r / maxf(average.r, 0.01),
		material.albedo_color.g * _wood_tone.g / maxf(average.g, 0.01),
		material.albedo_color.b * _wood_tone.b / maxf(average.b, 0.01))
	material.roughness = 0.85


## Janela quebrada: tábuas pregadas em X na abertura e, em algumas, a veneziana torta,
## pendurada de um lado. Só visual, filho da peça da parede (acompanha o giro e a escala).
func _break_window(wall: Node3D, wide: bool, seed_: int) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	var half_len := 0.65 if wide else 0.4
	for board in rng.randi_range(2, 3):
		var mesh := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = Vector3(half_len * 2.0 * rng.randf_range(0.85, 1.1), 0.15, 0.05)
		mesh.mesh = box
		mesh.material_override = _wood_material()
		mesh.position = Vector3(rng.randf_range(-0.08, 0.08), 1.45 + 0.4 * board + rng.randf_range(-0.08, 0.08), 0.13 + 0.02 * board)
		mesh.rotation.z = deg_to_rad(rng.randf_range(12.0, 32.0) * (1.0 if board % 2 == 0 else -1.0))
		wall.add_child(mesh)
	if wide and rng.randf() < 0.6 and Kit.has("WindowShutters_Wide_Round_Open"):
		# Gira em volta do centro da janela (o pivô fica a 1,9 m do chão), não do pé da parede.
		var pivot := Node3D.new()
		pivot.position = Vector3(0, 1.9, 0.02)
		pivot.rotation.z = deg_to_rad(rng.randf_range(5.0, 11.0) * (1.0 if rng.randf() < 0.5 else -1.0))
		var shutters := Kit.piece("WindowShutters_Wide_Round_Open")
		shutters.position = Vector3(0, -1.9, 0)
		_tone_wood(shutters, "WindowShutters_Wide_Round_Open")
		pivot.add_child(shutters)
		wall.add_child(pivot)


## Estátua de madeira (decor "statue": papel do NPC): o modelo parado numa pose, todo em
## madeira escura, sobre um pedestal de tábuas; bloqueia a passagem.
func _build_statue(decor: Dictionary) -> void:
	var root := Node3D.new()
	root.position = Vector3(decor.position[0], 0, decor.position[1])
	root.rotation.y = deg_to_rad(float(decor.get("rotation", 0.0)))
	_area_root.add_child(root)
	# O pedestal cresce com a estátua ("pedestal" = fator sobre 1,5 m de lado).
	var base := float(decor.get("pedestal", 1.0))
	var steps := [[Vector3(1.5, 0.16, 1.5) * base, 0.08], [Vector3(1.1, 0.5, 1.1) * base, 0.41]]
	steps[0][0].y = 0.16
	steps[1][0].y = 0.5
	for step: Array in steps:
		var mesh := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = step[0]
		mesh.mesh = box
		mesh.material_override = _wood_material()
		mesh.position.y = step[1]
		root.add_child(mesh)
	var top := 0.66
	# Ou um papel de NPC ("statue"), ou um modelo qualquer ("statue_model", ex.: o Ogro como gigante).
	var model: Node3D = null
	if decor.has("statue_model"):
		var packed := load(String(decor.statue_model)) as PackedScene
		model = packed.instantiate() if packed else null
	elif NpcModel.has_model(String(decor.get("statue", ""))):
		model = NpcModel.create(String(decor.statue))
	if model:
		model.position.y = top
		model.scale *= float(decor.get("scale", 1.15))
		root.add_child(model)
		if model.has_method("set_pose"):
			model.call("set_pose", String(decor.get("pose", "idle")))
		for player in model.find_children("*", "AnimationPlayer", true, false):
			(player as AnimationPlayer).speed_scale = 0.0
		for mesh in model.find_children("*", "MeshInstance3D", true, false):
			var m := mesh as MeshInstance3D
			for i in m.get_surface_override_material_count():
				m.set_surface_override_material(i, _wood_material())
			if m.get_surface_override_material_count() == 0:
				m.material_override = _wood_material()
	var body := StaticBody3D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	var shape := CollisionShape3D.new()
	var shape_box := BoxShape3D.new()
	shape_box.size = Vector3(1.5, 1.0, 1.5) * base
	shape_box.size.y = 1.0
	shape.shape = shape_box
	body.add_child(shape)
	body.position.y = 0.5
	root.add_child(body)


## Lixo jogado pelo chão do esgoto: garrafas e canecas caídas, cacos de pote,
## sacos, cordas, baldes virados, tábuas quebradas e trapos/papéis. Só visual;
## espalhado pela posição da sala (igual em todos os PCs), mais perto das paredes.
## Lixo coberto de limo: bem mais escuro e esverdeado que o resto (sem brilho).
const TRASH_GRIME := Color(0.45, 0.5, 0.36)
const TRASH := ["Bottle_1", "Bottle_2", "Bottle_3", "Bottle_4", "Mug_Bottle", "Mug_Jar", "Mug", "Mug_Wood", "Pot_Small_Shards", "Pot_Large_Shards",
	"Bag", "Rope_1", "Bucket_Wooden_1", "Vase_Big_Shards"]


func _scatter_trash(room: Dictionary, c: Vector3, half: Vector3) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(str(room.get("id", ""), c, "trash"))
	var count := clampi(roundi(half.x * half.z * 8.0 / 9.0 * float(arena.get("style", {}).get("trash_density", 1.0))), 5, 80)  # "trash_density" do estilo da área (o Esgoto usa 0,6)
	for i in count:
		# Mais lixo perto das paredes que no meio.
		var u := rng.randf_range(-1.0, 1.0)
		var v := rng.randf_range(-1.0, 1.0)
		if rng.randf() < 0.6:
			if rng.randf() < 0.5:
				u = signf(u) * rng.randf_range(0.7, 1.0)
			else:
				v = signf(v) * rng.randf_range(0.7, 1.0)
		var at := Vector3(c.x + u * (half.x - 0.6), 0.0, c.z + v * (half.z - 0.6))
		if rng.randf() < 0.35:
			_trash_scrap(at, rng)
			continue
		var piece_name: String = TRASH[rng.randi() % TRASH.size()]
		if arena.get("style", {}).get("trash_no_bottles", false) and (piece_name.begins_with("Bottle") or piece_name == "Mug_Bottle"):
			continue  # o Esgoto não tem garrafas jogadas no chão
		var node := Kit.piece(piece_name)
		if node == null:
			continue
		node.position = at
		node.rotation.y = rng.randf() * TAU
		if piece_name in ["Bottle_1", "Bottle_2", "Bottle_3", "Bottle_4", "Mug_Bottle", "Mug_Jar", "Mug", "Mug_Wood", "Bucket_Wooden_1"]:
			# Caído de lado.
			node.rotation.x = PI / 2.0
			node.position.y = 0.08 if piece_name != "Bucket_Wooden_1" else 0.22
		elif piece_name.ends_with("_Shards"):
			node.scale = Vector3(1.0, 0.25, 1.0)  # os cacos espalhados, rentes ao chão
		_area_root.add_child(node)
		if not piece_name.begins_with("Bottle"):  # as garrafas ficam na cor original do vidro (só a sujeira dos outros lixos tinge)
			_tint_piece(node, TRASH_GRIME)
		_tone_wood(node, piece_name)


## Aranhinhas que andam pelo chão do esgoto (não atacam; só cenário, em cada PC).
func _scatter_spiders(room: Dictionary, c: Vector3, half: Vector3) -> void:
	_scatter_critters(room, c, half, "spider", 1.0, 6)


## Morcegos voando em círculos no alto das salas (só enfeite, em cada PC): de 0 a 2 por sala (a maioria não tem), pela posição dela.
func _scatter_bats(room: Dictionary, c: Vector3, half: Vector3) -> void:
	if not NpcModel.has_model("bat"):
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(str(room.get("id", ""), c, "bats"))
	if rng.randf() < 0.65:
		return  # a maioria das salas fica sem morcegos
	for i in rng.randi_range(1, clampi(roundi(half.x * half.z / 40.0), 1, 2)):
		var flyer := Flyer.new()
		flyer.radius = rng.randf_range(1.2, minf(3.2, minf(half.x, half.z) - 1.0))
		flyer.center = Vector3(c.x + rng.randf_range(-1.0, 1.0) * maxf(half.x - flyer.radius - 0.8, 0.0), 0,
				c.z + rng.randf_range(-1.0, 1.0) * maxf(half.z - flyer.radius - 0.8, 0.0))
		flyer.height = rng.randf_range(2.0, 3.0)
		flyer.speed = rng.randf_range(2.2, 3.6)
		flyer.direction = 1.0 if rng.randf() < 0.5 else -1.0
		flyer.phase = rng.randf() * TAU
		_area_root.add_child(flyer)
		var model := NpcModel.create("bat")
		flyer.add_child(model)
		model.call("set_pose", "walk")


## Bichinhos de cenário (aranhas, ratos): andam entre dois pontos do chão da sala; `density` escala a quantidade.
func _scatter_critters(room: Dictionary, c: Vector3, half: Vector3, kind: String, density: float, max_count: int) -> void:
	if not NpcModel.has_model(kind):
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(str(room.get("id", ""), c, kind + "s"))
	var count := clampi(roundi(half.x * half.z / 25.0 * density), 1, max_count)
	for i in count:
		var walker := Wanderer.new()
		var a := Vector3(c.x + rng.randf_range(-half.x + 0.8, half.x - 0.8), 0, c.z + rng.randf_range(-half.z + 0.8, half.z - 0.8))
		var b := Vector3(c.x + rng.randf_range(-half.x + 0.8, half.x - 0.8), 0, c.z + rng.randf_range(-half.z + 0.8, half.z - 0.8))
		walker.position = a
		walker.from = a
		walker.to = b
		walker.speed = rng.randf_range(0.6, 1.4)
		_area_root.add_child(walker)
		var model := NpcModel.create(kind)
		walker.add_child(model)
		walker.model = model
		model.call("set_pose", "walk")


## Trapo, papel ou tábua quebrada no chão (caixas finas na cor da sujeira).
func _trash_scrap(at: Vector3, rng: RandomNumberGenerator) -> void:
	var scrap := MeshInstance3D.new()
	var box := BoxMesh.new()
	var plank := rng.randf() < 0.4
	box.size = Vector3(rng.randf_range(0.08, 0.16), 0.03, rng.randf_range(0.5, 1.1)) if plank \
		else Vector3(rng.randf_range(0.2, 0.45), 0.01, rng.randf_range(0.15, 0.35))
	scrap.mesh = box
	var colors := [Color(0.24, 0.17, 0.1), Color(0.33, 0.3, 0.22), Color(0.2, 0.22, 0.16), Color(0.4, 0.36, 0.28)]
	var material := StandardMaterial3D.new()
	material.albedo_color = (colors[0] if plank else colors[1 + rng.randi() % 3]) * Color(0.7, 0.78, 0.6)
	if plank and _wood_tone.a > 0.0:
		material.albedo_color = _wood_tone  # tábua na cor única da madeira da área
	material.roughness = 0.95
	scrap.material_override = material
	scrap.position = at + Vector3(0, 0.02, 0)
	scrap.rotation = Vector3(rng.randf_range(-0.08, 0.08), rng.randf() * TAU, rng.randf_range(-0.08, 0.08))
	scrap.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_area_root.add_child(scrap)


## Sujeira numa parede: faixa escura de umidade embaixo e escorridos de lodo
## descendo de cima, colados na face de dentro (sem os vãos das portas).
func _grime_side(face: Vector3, along: Vector3, inward: Vector3, length: float, door: bool, offset: float, rng: RandomNumberGenerator) -> void:
	for segment in _wall_pieces(length, door, offset):
		var center: Vector3 = face + along * segment.x + inward * 0.04
		_grime_quad(center + Vector3.UP * 0.55, segment.y, 1.1, inward, "band")
		var count := floori(segment.y / 1.6)
		for i in count:
			if rng.randf() < 0.35:
				continue
			var at: float = segment.x - segment.y / 2.0 + (i + rng.randf_range(0.2, 0.8)) * segment.y / maxf(count, 1)
			var height := rng.randf_range(1.4, 2.8)
			_grime_quad(face + along * at + inward * (0.05 + 0.002 * i) + Vector3.UP * (3.0 - height / 2.0),
				rng.randf_range(0.7, 1.5), height, inward, "drips")
		# Bocas de cano: uma a cada ~7 m de parede, com o lodo escorrendo embaixo.
		var pipes := floori(segment.y / 7.0)
		for i in pipes:
			var at: float = segment.x - segment.y / 2.0 + (i + rng.randf_range(0.3, 0.7)) * segment.y / pipes
			_pipe_mouth(face + along * at, inward, rng)


## Cano saindo da parede: tubo de ferro enferrujado com aro, boca escura e o
## lodo verde que escorre dele até uma poça no chão.
func _pipe_mouth(on_wall: Vector3, inward: Vector3, rng: RandomNumberGenerator) -> void:
	var height := rng.randf_range(0.9, 1.6)
	var radius := rng.randf_range(0.22, 0.32)
	var root := Node3D.new()
	root.position = on_wall + Vector3.UP * height
	root.basis = Basis.looking_at(inward, Vector3.UP)  # -Z do nó = para dentro da sala
	_area_root.add_child(root)
	_cut_walls.append(root)
	var rust := _grime_material("pipe")  # cano de cobre esverdeado (pátina)
	var tube := MeshInstance3D.new()
	var cylinder := CylinderMesh.new()
	cylinder.top_radius = radius
	cylinder.bottom_radius = radius
	cylinder.height = 0.5
	tube.mesh = cylinder
	tube.material_override = rust
	tube.rotation.x = PI / 2.0
	tube.position.z = -0.2
	root.add_child(tube)
	var rim := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = radius * 0.95
	torus.outer_radius = radius * 1.25
	rim.mesh = torus
	rim.material_override = rust
	rim.rotation.x = PI / 2.0
	rim.position.z = -0.45
	root.add_child(rim)
	var hole := MeshInstance3D.new()
	var disc := CylinderMesh.new()
	disc.top_radius = radius * 0.9
	disc.bottom_radius = radius * 0.9
	disc.height = 0.02
	hole.mesh = disc
	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.02, 0.025, 0.02)
	hole.material_override = dark
	hole.rotation.x = PI / 2.0
	hole.position.z = -0.44
	root.add_child(hole)
	# Fio de lodo descendo da boca até o chão, e a poça.
	var slime := MeshInstance3D.new()
	var drip := BoxMesh.new()
	drip.size = Vector3(radius * 0.8, height, 0.03)
	slime.mesh = drip
	slime.material_override = _sludge_material()
	slime.position = Vector3(0, -height / 2.0, -0.47)
	root.add_child(slime)
	_puddle(root.position + (-root.basis.z) * 0.7 - Vector3.UP * (height - 0.025), rng.randf_range(0.5, 0.9), rng)
	_pipes.append([root.position + (-root.basis.z) * 0.5, -root.basis.z])


## Grade de ferro no chão sobre o escuro (o esgoto de baixo).
func _floor_grate(at: Vector3, rng: RandomNumberGenerator) -> void:
	var root := Node3D.new()
	root.position = at
	root.rotation.y = rng.randi_range(0, 3) * PI / 2.0
	_area_root.add_child(root)
	var pit := MeshInstance3D.new()
	var plane := BoxMesh.new()
	plane.size = Vector3(1.2, 0.01, 1.2)
	pit.mesh = plane
	var dark := StandardMaterial3D.new()
	dark.albedo_color = Color(0.01, 0.015, 0.01)
	pit.material_override = dark
	pit.position.y = 0.012
	root.add_child(pit)
	var iron := _grime_material("rust")
	for side in [-1.0, 1.0]:
		for axis in 2:
			var frame := MeshInstance3D.new()
			var bar := BoxMesh.new()
			bar.size = Vector3(1.3, 0.06, 0.1) if axis == 0 else Vector3(0.1, 0.06, 1.3)
			frame.mesh = bar
			frame.material_override = iron
			frame.position = Vector3(0, 0.035, 0.6 * side) if axis == 0 else Vector3(0.6 * side, 0.035, 0)
			root.add_child(frame)
	for i in 5:
		var rod := MeshInstance3D.new()
		var bar := BoxMesh.new()
		bar.size = Vector3(0.06, 0.05, 1.2)
		rod.mesh = bar
		rod.material_override = iron
		rod.position = Vector3(-0.4 + i * 0.2, 0.03, 0)
		root.add_child(rod)


## O gás do Pacto sai do cano mais perto do ponto marcado (todos os PCs):
## nuvem verde na boca do cano e um jato até o aviso no chão.
func pipe_gas(at: Vector3) -> void:
	if multiplayer.is_server():
		_pipe_gas.rpc(at)


@rpc("authority", "call_local", "reliable")
func _pipe_gas(at: Vector3) -> void:
	if _pipes.is_empty():
		return
	var best: Array = _pipes[0]
	for pipe: Array in _pipes:
		if (pipe[0] as Vector3).distance_to(at) < (best[0] as Vector3).distance_to(at):
			best = pipe
	var mouth: Vector3 = best[0]
	var color := Color(0.45, 0.85, 0.2)
	Fx.burst(_area_root, Vector3(mouth.x, 0.0, mouth.z), 0.8, color, "air", 1.2)
	Fx.beam(_area_root, mouth, Vector3(at.x, 0.4, at.z), 0.7, color, "air", 1.1)


func _grime_quad(at: Vector3, width: float, height: float, inward: Vector3, kind: String) -> void:
	var quad := MeshInstance3D.new()
	var mesh := QuadMesh.new()
	mesh.size = Vector2(width, height)
	quad.mesh = mesh
	quad.material_override = _grime_material(kind)
	quad.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	quad.position = at
	quad.rotation.y = atan2(inward.x, inward.z)
	_area_root.add_child(quad)
	_cut_walls.append(quad)


## Poça de água suja: mancha irregular, lisa e brilhante (só visual; o lodo
## tóxico que machuca é o verde dos perigos).
func _puddle(at: Vector3, radius: float, rng: RandomNumberGenerator) -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	st.set_normal(Vector3.UP)
	var steps := 14
	var stretch := Vector2(rng.randf_range(0.7, 1.3), rng.randf_range(0.7, 1.3))
	var points: Array[Vector3] = []
	for i in steps:
		var angle := TAU * i / steps
		var r := radius * rng.randf_range(0.7, 1.1)
		points.append(Vector3(cos(angle) * r * stretch.x, 0, sin(angle) * r * stretch.y))
	for i in steps:
		st.add_vertex(Vector3.ZERO)
		st.add_vertex(points[(i + 1) % steps])
		st.add_vertex(points[i])
	var puddle := MeshInstance3D.new()
	puddle.mesh = st.commit()
	puddle.material_override = _grime_material("puddle")
	puddle.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	puddle.position = at
	puddle.rotation.y = rng.randf() * TAU
	_area_root.add_child(puddle)


## Materiais da sujeira (um de cada, compartilhados); as texturas dos escorridos
## e da faixa de umidade são geradas aqui.
func _grime_material(kind: String) -> StandardMaterial3D:
	if _grime_materials.has(kind):
		return _grime_materials[kind]
	var material := StandardMaterial3D.new()
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	match kind:
		"puddle":
			# Água turva por cima dos tijolos: deixa ver o chão e brilha nas luzes.
			material.albedo_color = Color(0.3, 0.29, 0.16, 0.45)
			material.roughness = 0.12
			material.metallic_specular = 1.0
			material.cull_mode = BaseMaterial3D.CULL_DISABLED
		"band":
			material.albedo_texture = _grime_texture(false)
			material.roughness = 0.9
		"pipe":
			material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
			material.albedo_color = Color(0.2, 0.42, 0.28)
			material.metallic = 0.4
			material.roughness = 0.6
		"rust":
			material.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
			material.albedo_color = Color(0.3, 0.17, 0.09)
			material.metallic = 0.5
			material.roughness = 0.75
		_:
			material.albedo_texture = _grime_texture(true)
			material.roughness = 0.9
	_grime_materials[kind] = material
	return material


static func _grime_texture(drips: bool) -> ImageTexture:
	var w := 64
	var h := 128
	var image := Image.create(w, h, false, Image.FORMAT_RGBA8)
	var rng := RandomNumberGenerator.new()
	rng.seed = 7 if drips else 11
	var lengths: Array[float] = []
	for x in w:
		lengths.append(rng.randf_range(0.2, 1.0) if drips else 0.0)
	# Escorridos mais largos: cada coluna puxa a vizinha.
	for x in range(1, w):
		lengths[x] = lerpf(lengths[x], lengths[x - 1], 0.6)
	for y in h:
		var v := float(y) / (h - 1)  # 0 = topo, 1 = base
		for x in w:
			var u := float(x) / (w - 1)
			var edge := clampf(minf(u, 1.0 - u) * 6.0, 0.0, 1.0)
			var alpha := 0.0
			if drips:
				alpha = clampf((lengths[x] - v) * 3.0, 0.0, 1.0) * 0.75 * edge
			else:
				alpha = clampf(v * 1.2 - 0.1, 0.0, 1.0) * 0.6 * (0.8 + 0.2 * rng.randf())
			var tone := 0.6 + 0.4 * rng.randf()
			image.set_pixel(x, y, Color(0.12 * tone, 0.14 * tone, 0.06 * tone, alpha))
	return ImageTexture.create_from_image(image)


## Um lado da sala: peças de 2 m (esticadas para fechar o comprimento), com o
## vão da porta; a frente da peça (+Z) vira para `inward`.
func _dress_side(face: Vector3, along: Vector3, inward: Vector3, length: float, door: bool, offset: float, pieces: Array) -> void:
	if pieces.is_empty() or String(pieces[0]) == "":
		return
	var full := pieces.size() > 1 or String(pieces[0]).begins_with("Wall")
	for segment in _wall_pieces(length, door, offset):
		var count := maxi(roundi(segment.y / Kit.WALL_WIDTH), 1)
		var width := segment.y / count
		for i in count:
			var at := segment.x - segment.y / 2.0 + width * (i + 0.5)
			var piece_name: String = pieces[(i * 3 + roundi(absf(face.x + face.z))) % pieces.size()]
			var node := Kit.piece(piece_name)
			if node == null:
				continue
			node.scale.x = width / Kit.WALL_WIDTH
			# A face da parede do kit fica 0,09 m à frente da origem.
			node.position = face + along * at - inward * (0.09 if full else 0.0)
			node.rotation.y = atan2(inward.x, inward.z)
			_area_root.add_child(node)
			_tint_piece(node)
			_tone_wood(node, piece_name)
			if arena.get("style", {}).get("stone_trim", false):
				_stone_trim(node)
			if arena.get("style", {}).get("wood", false):
				_woodify(node)
			if arena.get("style", {}).get("broken_windows", false) and piece_name.contains("Window"):
				_break_window(node, piece_name.contains("Wide"), hash(Vector2(node.position.x, node.position.z)))
			if full and not arena.get("outdoor", false):
				_cut_walls.append(node)


var _stone_trim_material: StandardMaterial3D


## Estilo "stone_trim" (o Esgoto): a viga de madeira marrom do topo das paredes e dos batentes (material MI_WoodTrim) vira pedra escura. De cima, as vigas marrons
## formavam linhas que cruzavam as passagens e faziam o mapa parecer fechado.
func _stone_trim(node: Node3D) -> void:
	if _stone_trim_material == null:
		_stone_trim_material = StandardMaterial3D.new()
		_stone_trim_material.albedo_color = Color(0.2, 0.2, 0.18)
		_stone_trim_material.roughness = 0.95
	for mesh in node.find_children("*", "MeshInstance3D", true, false):
		var m := mesh as MeshInstance3D
		for i in m.get_surface_override_material_count():
			var material := m.get_active_material(i)
			if material and String(material.resource_name).begins_with("MI_WoodTrim"):
				m.set_surface_override_material(i, _stone_trim_material)


## Objeto de cenário (data/arenas.json "decor"): mesa, banco, barril, carroça…
## Com "solid", uma caixa de colisão do tamanho dado.
func _build_decor(decor: Dictionary) -> void:
	if decor.has("statue") or decor.has("statue_model"):
		_build_statue(decor)
		return
	if decor.has("light"):
		# Luz de cenário (lanterna vermelha da casa da Madame, fogo dos apostadores).
		var c: Array = decor.light
		var light := OmniLight3D.new()
		light.light_color = Color(c[0], c[1], c[2])
		light.omni_range = float(decor.get("range", 6.0))
		light.light_energy = float(decor.get("energy", 1.0))
		light.position = Vector3(decor.position[0], float(decor.get("y", 2.0)), decor.position[1])
		_area_root.add_child(light)
		if decor.get("flicker", false):
			var glow := light.create_tween().set_loops()
			glow.tween_property(light, "light_energy", light.light_energy * 1.25, 0.17).set_trans(Tween.TRANS_SINE)
			glow.tween_property(light, "light_energy", light.light_energy * 0.8, 0.23).set_trans(Tween.TRANS_SINE)
			glow.tween_property(light, "light_energy", light.light_energy * 1.1, 0.12).set_trans(Tween.TRANS_SINE)
		return
	if decor.has("collider"):
		# Só colisão (as paredes das Ruínas já estão desenhadas na peça Ruins_Layout).
		var wall := StaticBody3D.new()
		wall.collision_layer = 1
		wall.collision_mask = 0
		var wall_shape := CollisionShape3D.new()
		var wall_box := BoxShape3D.new()
		wall_box.size = Vector3(decor.collider[0], 3.0, decor.collider[1])
		wall_shape.shape = wall_box
		wall.add_child(wall_shape)
		wall.position = Vector3(decor.position[0], 1.5, decor.position[1])
		_area_root.add_child(wall)
		return
	var node := Kit.piece(String(decor.piece))
	if node == null:
		return
	node.position = Vector3(decor.position[0], float(decor.get("y", 0.0)), decor.position[1])
	node.rotation.y = deg_to_rad(float(decor.get("rotation", 0.0)))
	node.scale = Vector3.ONE * float(decor.get("scale", 1.0))
	if decor.has("swim"):
		# Peixe nadando em círculo (raio e velocidade em "swim"), de cabeça para a frente, na água do riacho ou do mar.
		var radius := float(decor.swim.get("radius", 1.0))
		var pivot := Node3D.new()
		pivot.position = node.position
		pivot.rotation.y = float(decor.swim.get("phase", 0.0))
		node.position = Vector3(radius, node.position.y, 0.0)
		node.rotation.y = PI
		pivot.add_child(node)
		_area_root.add_child(pivot)
		var flyer := node.find_child("AnimationPlayer", true, false) as AnimationPlayer
		if flyer and flyer.has_animation("Flying"):
			# Borboleta com esqueleto (Butterfly_Anim): toca a batida de asas do próprio modelo.
			flyer.get_animation("Flying").loop_mode = Animation.LOOP_LINEAR
			flyer.play("Flying")
		var loop := pivot.create_tween().set_loops()
		loop.tween_property(pivot, "rotation:y", TAU, TAU * radius / float(decor.swim.get("speed", 0.6))).as_relative()
		if decor.get("flap", false):
			# Borboleta: bate as asas (o modelo é parado) e sobe e desce de leve enquanto voa em círculo.
			var wings := node.create_tween().set_loops()
			wings.tween_property(node, "scale:x", node.scale.x * 0.4, 0.09)
			wings.tween_property(node, "scale:x", node.scale.x, 0.09)
			var bob := node.create_tween().set_loops()
			bob.tween_property(node, "position:y", node.position.y + 0.35, 1.1).set_trans(Tween.TRANS_SINE)
			bob.tween_property(node, "position:y", node.position.y, 1.1).set_trans(Tween.TRANS_SINE)
		return
	_area_root.add_child(node)
	_tone_wood(node, String(decor.piece))
	if decor.get("flicker", false):
		# Chama: o fogo estica e encolhe sem parar (a fogueira do acampamento).
		var base := node.scale
		var flame := node.create_tween().set_loops()
		flame.tween_property(node, "scale", base * Vector3(1.0, 1.2, 1.0), 0.17).set_trans(Tween.TRANS_SINE)
		flame.tween_property(node, "scale", base * Vector3(0.92, 0.88, 0.92), 0.23).set_trans(Tween.TRANS_SINE)
		flame.tween_property(node, "scale", base * Vector3(1.04, 1.1, 1.04), 0.12).set_trans(Tween.TRANS_SINE)
		flame.tween_property(node, "scale", base, 0.2).set_trans(Tween.TRANS_SINE)
	# Peça animada (o aparelho de treino gira): toca a primeira animação em laço.
	var animator := node.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if animator and not animator.get_animation_list().is_empty():
		var clip := animator.get_animation_list()[0]
		animator.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
		animator.play(clip)
	if decor.has("solid"):
		var size: Array = decor.solid
		var body := StaticBody3D.new()
		body.collision_layer = 1
		body.collision_mask = 0
		var shape := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(size[0], 1.0, size[1])
		shape.shape = box
		body.add_child(shape)
		body.position = node.position + Vector3(0, 0.5, 0)
		body.rotation.y = node.rotation.y
		_area_root.add_child(body)


## Parede ao longo de x; com porta, deixa um vão de DOOR_WIDTH (no meio, ou
## deslocado `offset` metros).
func _wall_x(cx: float, z: float, width: float, door: bool, height := WALL_HEIGHT, offset := 0.0, shown := true) -> void:
	for piece in _wall_pieces(width, door, offset):
		_box(Vector3(cx + piece.x, height / 2, z), Vector3(piece.y, height, 1), WALL_COLOR, shown)


## Parede ao longo de z (leste/oeste), com o mesmo vão de porta.
func _wall_z(x: float, cz: float, length: float, door: bool, height := WALL_HEIGHT, offset := 0.0, shown := true) -> void:
	for piece in _wall_pieces(length, door, offset):
		_box(Vector3(x, height / 2, cz + piece.x), Vector3(1, height, piece.y), WALL_COLOR, shown)


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


## Caixa com colisão; `shown` falso deixa só a colisão (o kit cobre o visual).
func _box(center: Vector3, box_size: Vector3, color: Color, shown := true) -> void:
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
	mesh.visible = shown
	body.add_child(mesh)
	_area_root.add_child(body)
	body.position = center
