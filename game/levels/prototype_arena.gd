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

const ARENA_ID := "prototype_arena"
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

enum Result { NONE, VICTORY, DEFEAT }

## Um jogador que caiu voltou e assumiu o mesmo herói (só no servidor).
signal hero_resumed(peer_id: int)

var arena: Dictionary
var local_player: Player
# Estado da partida (decidido no servidor, espelhado nos clientes).
var cleared := 0
var total_encounters := 0
var result := Result.NONE
var finished := false

var _players_spawner: MultiplayerSpawner
var _enemy_spawner: MultiplayerSpawner
var _projectile_spawner: MultiplayerSpawner
var _camera: TopDownCamera
## Aumenta a cada reinício; timers da partida anterior são ignorados.
var _run := 0
## Grupos de encontro (servidor): id -> {position, awake, members}.
var _groups := {}
var _encounter_timer := 0.0
## Reanimação em andamento: caído -> quem está reanimando.
var _revivers := {}
## Quem foi atingido reanimando precisa soltar o botão antes de tentar de novo.
var _interrupted: Array[Player] = []
## Heróis esperando o dono que caiu: client_id -> Player (07-rede.md, seção 9).
var _held := {}

@onready var hud: Hud = $Hud
@onready var pause_menu: PauseMenu = $PauseMenu


func _ready() -> void:
	add_to_group(&"arena")
	arena = GameData.get_arena(ARENA_ID)
	total_encounters = arena.encounters.size()
	_build_environment()
	_build_area()
	_build_spawners()
	_camera = TopDownCamera.new()
	add_child(_camera)
	_camera.snap()
	hud.set_progress(0, total_encounters)
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
		_spawn_player(multiplayer.get_unique_id())
		_start_run()
	else:
		hud.show_connecting(true)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"menu") and not pause_menu.is_open:
		pause_menu.open(not NetworkManager.is_online())
		get_viewport().set_input_as_handled()
	elif result == Result.VICTORY and event.is_action_pressed(&"attack"):
		if multiplayer.is_server():
			_start_run()
		else:
			_request_restart.rpc_id(1)


func _physics_process(delta: float) -> void:
	if multiplayer.is_server() and result == Result.NONE:
		_update_revives(delta)
		_encounter_timer -= delta
		if _encounter_timer <= 0.0:
			_encounter_timer = ENCOUNTER_CHECK_INTERVAL
			_update_encounters()


# --- Spawners -----------------------------------------------------------------

func _build_spawners() -> void:
	_players_spawner = _spawner("PlayerSpawner", Player.create)
	_enemy_spawner = _spawner("EnemySpawner", _create_enemy)
	_projectile_spawner = _spawner("ProjectileSpawner", Projectile.create)
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
	var origin := host.global_position if host else CHECKPOINT
	var position := origin + SLOT_OFFSETS[slot % SLOT_OFFSETS.size()]
	if resume:
		slot = resume.slot
		position = resume.global_position
	var player: Player = _players_spawner.spawn({
		"peer_id": peer_id, "slot": slot, "class_id": arena.player_class,
		"position": position,
	})
	player.downed.connect(_on_player_downed)
	player.hurt.connect(_on_player_hurt.bind(player))
	_on_node_spawned(player)
	return player


func _on_node_spawned(node: Node) -> void:
	if node is Player and node.is_local():
		local_player = node
		_camera.target = node
		_camera.snap()
		hud.bind_player(node)
		hud.show_connecting(false)


func _on_peer_joined(peer_id: int) -> void:
	var held: Player = _held.get(NetworkManager.client_id_of(peer_id))
	if is_instance_valid(held):
		# Voltou dentro do prazo: assume o mesmo herói (vida, lugar, cor).
		_held.erase(NetworkManager.client_id_of(peer_id))
		var player := _spawn_player(peer_id, held)
		player.take_over(held)
		held.queue_free()
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
		get_tree().create_timer(GameData.balance.drop_hold_time, false).timeout.connect(func() -> void:
			if _held.get(client) == player:
				_held.erase(client)
				player.queue_free()
				_check_defeat.call_deferred())
	else:
		player.queue_free()
	_check_defeat.call_deferred()


# --- Partida (servidor) ---------------------------------------------------------

## Começa a área do zero: todos os grupos no lugar, dormindo.
func _start_run() -> void:
	_run += 1
	for node in get_tree().get_nodes_in_group(&"enemies"):
		node.queue_free()
	for node in get_children():
		if node is Projectile:
			node.queue_free()
	_groups.clear()
	for encounter: Dictionary in arena.encounters:
		_spawn_group(encounter)
	_reset_players()
	_broadcast(0, Result.NONE)


func _spawn_group(encounter: Dictionary) -> void:
	var center := Vector3(encounter.position[0], 0, encounter.position[1])
	var ids: Array[String] = []
	for entry in encounter.monsters:
		for i in int(entry.count):
			ids.append(entry.monster)
	var members: Array[Enemy] = []
	for i in ids.size():
		# Bando em círculo em volta do ponto do grupo.
		var angle := TAU * i / ids.size()
		var offset := Vector3(cos(angle), 0, sin(angle)) * (1.6 if ids.size() > 1 else 0.0)
		var enemy: Enemy = _enemy_spawner.spawn({
			"monster_id": ids[i], "group": encounter.id,
			"position": center + offset, "yaw": randf() * TAU,
		})
		members.append(enemy)
	_groups[encounter.id] = {"position": center, "awake": false, "members": members}


func _reset_players() -> void:
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		p.reset_at(CHECKPOINT + SLOT_OFFSETS[p.slot % SLOT_OFFSETS.size()])


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


## Monstros mortos ficam mortos (03-inimigos.md, "Sem respawn").
func _on_enemy_died(enemy: Enemy) -> void:
	var group: Dictionary = _groups.get(enemy.group, {})
	if group.is_empty():
		return
	group.members.erase(enemy)
	if group.members.is_empty():
		var done := cleared + 1
		_broadcast(done, Result.VICTORY if done >= total_encounters else Result.NONE)


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
	for node in get_children():
		if node is Projectile:
			node.queue_free()
	for id in _groups:
		var group: Dictionary = _groups[id]
		if group.awake and not group.members.is_empty():
			group.awake = false
			for enemy: Enemy in group.members:
				enemy.return_home()
	_reset_players()
	_broadcast(cleared, Result.NONE)


@rpc("any_peer", "reliable")
func _request_restart() -> void:
	if multiplayer.is_server() and result == Result.VICTORY:
		_start_run()


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
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.03, 0.03, 0.05)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.35, 0.38, 0.5)
	env.ambient_light_energy = 0.6
	env.fog_enabled = true
	env.fog_light_color = Color(0.06, 0.06, 0.09)
	env.fog_density = 0.02
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	add_child(world_env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-60, 30, 0)
	sun.light_energy = 0.8
	sun.light_color = Color(0.85, 0.8, 0.75)
	sun.shadow_enabled = true
	add_child(sun)

	# Uma tocha quente por sala grande — poucas luzes dinâmicas.
	for room: Dictionary in arena.rooms:
		if room.get("torch", false):
			var torch := OmniLight3D.new()
			torch.position = Vector3(room.center[0], 3, room.center[1])
			torch.omni_range = 12.0
			torch.light_color = Color(1.0, 0.6, 0.3)
			torch.light_energy = 1.2
			add_child(torch)


## Chão único e paredes de cada sala, com vão de porta onde a sala se liga a outra.
func _build_area() -> void:
	var bounds := AABB()
	for i in arena.rooms.size():
		var room: Dictionary = arena.rooms[i]
		var c := Vector3(room.center[0], 0, room.center[1])
		var half := Vector3(room.size[0], 0, room.size[1]) / 2.0
		var box := AABB(c - half, half * 2.0)
		bounds = box if i == 0 else bounds.merge(box)
		var doors: Array = room.get("doors", [])
		_wall_x(c.x, c.z - half.z, half.x * 2.0, "north" in doors)
		_wall_x(c.x, c.z + half.z, half.x * 2.0, "south" in doors)
		_box(Vector3(c.x - half.x - 0.5, WALL_HEIGHT / 2, c.z), Vector3(1, WALL_HEIGHT, half.z * 2.0 + 2.0), WALL_COLOR)
		_box(Vector3(c.x + half.x + 0.5, WALL_HEIGHT / 2, c.z), Vector3(1, WALL_HEIGHT, half.z * 2.0 + 2.0), WALL_COLOR)
	var center := bounds.get_center()
	_box(Vector3(center.x, -0.5, center.z), Vector3(bounds.size.x + 4, 1, bounds.size.z + 4), FLOOR_COLOR)


## Parede ao longo de x; com porta, deixa um vão de DOOR_WIDTH no meio.
func _wall_x(cx: float, z: float, width: float, door: bool) -> void:
	var gap := minf(DOOR_WIDTH, width) if door else 0.0
	var side := (width - gap) / 2.0
	if side <= 0.01:
		return
	if door:
		_box(Vector3(cx - gap / 2 - side / 2, WALL_HEIGHT / 2, z), Vector3(side, WALL_HEIGHT, 1), WALL_COLOR)
		_box(Vector3(cx + gap / 2 + side / 2, WALL_HEIGHT / 2, z), Vector3(side, WALL_HEIGHT, 1), WALL_COLOR)
	else:
		_box(Vector3(cx, WALL_HEIGHT / 2, z), Vector3(width, WALL_HEIGHT, 1), WALL_COLOR)


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
	add_child(body)
	body.position = center
