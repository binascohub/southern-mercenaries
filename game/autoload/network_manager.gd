# Southern Mercenaries — GPL-3.0-or-later
extends Node
## Sessão de rede (07-rede.md). Host-cliente com servidor autoritativo dentro
## do jogo; o solo usa o mesmo código sem rede (OfflineMultiplayerPeer, onde
## este PC é o servidor, peer 1).
##
## Fluxo: o menu chama prepare_solo/prepare_host/prepare_join e troca para a
## cena da área; a área monta seus spawners e só então chama begin(), para
## que a replicação encontre os mesmos caminhos de nó em todos os PCs.
##
## Descoberta na LAN: o host anuncia a partida por broadcast UDP; quem procura
## escuta a porta de descoberta. A rede só envia IDs e chaves, nunca texto
## traduzido. Entrada: o host recusa versão ou dados do jogo diferentes.

signal peer_joined(peer_id: int)
## `dropped`: caiu sem avisar (o herói espera 30 s, 07-rede.md, seção 9).
signal peer_left(peer_id: int, dropped: bool)
## Este cliente foi aceito pelo host (versão igual e há vaga).
signal accepted
## Sessão terminou ou não começou; o menu mostra `reason_key`.
signal session_ended(reason_key: String)
signal hosts_changed

enum Mode { NONE, SOLO, HOST, CLIENT }

const GAME_ID := "southern-mercenaries"
const ANNOUNCE_INTERVAL := 1.0
const HOST_TIMEOUT := 5.0
const CONNECT_TIMEOUT := 6.0
const DATA_DIR := "res://data"
const CLIENT_ID_PATH := "user://client.cfg"

var mode := Mode.NONE
var game_port := 24567
var discovery_port := 24568
var max_players := 4
## Motivo do último fim de sessão (chave de tradução), para o menu mostrar.
var last_error_key := ""
var last_error_args := {}
## Hosts encontrados na LAN: "ip:porta" -> {address, port, version, players, max, seen}.
var hosts := {}

## ID deste PC, para o host reconhecer quem cai e reentra. Provisório até o
## ID do personagem (Fase 3, 11-saves.md).
var client_id := ""
var _client_ids := {}  # peer -> client_id (no servidor)
var _characters := {}  # peer -> personagem enviado na entrada (no servidor)
var _goodbyes: Array[int] = []
var _join_address := ""
var _join_port := 0
var _content_hash := ""
var _accepted_peers: Array[int] = []
var _announcer: PacketPeerUDP
var _announce_left := 0.0
var _listener: PacketPeerUDP
## Prazo da conexão em relógio real (ms); 0 = sem prazo.
var _connect_deadline := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var net: Dictionary = GameData.balance.get("net", {})
	game_port = net.get("game_port", game_port)
	discovery_port = net.get("discovery_port", discovery_port)
	max_players = net.get("max_players", max_players)
	_content_hash = content_hash()
	client_id = _load_client_id()
	multiplayer.peer_connected.connect(_on_peer_connected)
	multiplayer.peer_disconnected.connect(_on_peer_disconnected)
	multiplayer.connected_to_server.connect(_on_connected_to_server)
	multiplayer.connection_failed.connect(_on_connection_failed)
	multiplayer.server_disconnected.connect(_on_server_disconnected)


static func version() -> String:
	return ProjectSettings.get_setting("application/config/version")


## Resumo dos dados do jogo (data/*.json): quem tiver dados diferentes do host
## é recusado mesmo com a mesma versão (07-rede.md, seção 3).
static func content_hash() -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_MD5)
	var files := Array(DirAccess.get_files_at(DATA_DIR))
	files.sort()
	for file: String in files:
		if file.ends_with(".json"):
			ctx.update(file.to_utf8_buffer())
			ctx.update(FileAccess.get_file_as_bytes(DATA_DIR.path_join(file)))
	return ctx.finish().hex_encode().substr(0, 12)


## Nome deste PC no anúncio da LAN (não é texto traduzido).
static func host_name() -> String:
	for variable in ["COMPUTERNAME", "HOSTNAME", "USER", "USERNAME"]:
		var value := OS.get_environment(variable)
		if value != "":
			return value.substr(0, 32)
	return "host"


func is_server() -> bool:
	return multiplayer.is_server()


func is_online() -> bool:
	return mode == Mode.HOST or mode == Mode.CLIENT


func client_id_of(peer_id: int) -> String:
	return _client_ids.get(peer_id, "")


## Personagem que o jogador trouxe (o host usa o da própria sessão).
func character_of(peer_id: int) -> CharacterData:
	if peer_id == multiplayer.get_unique_id():
		return Session.ensure_character()
	return CharacterData.from_dict(_characters.get(peer_id))


func player_count() -> int:
	return _accepted_peers.size() + 1 if is_server() else 0


func prepare_solo() -> void:
	mode = Mode.SOLO


func prepare_host() -> void:
	mode = Mode.HOST


## Aceita "ip" ou "ip:porta" (conexão manual, 07-rede.md, seção 3).
func prepare_join(address: String) -> void:
	mode = Mode.CLIENT
	var parsed := parse_address(address)
	_join_address = parsed[0]
	_join_port = parsed[1]


func parse_address(text: String) -> Array:
	text = text.strip_edges()
	var port := game_port
	if text.count(":") == 1:
		port = int(text.get_slice(":", 1))
		text = text.get_slice(":", 0)
	return [text, port]


## Chamado pela área depois de montar os spawners.
func begin() -> void:
	last_error_key = ""
	last_error_args = {}
	_accepted_peers.clear()
	match mode:
		Mode.HOST:
			var peer := ENetMultiplayerPeer.new()
			var err := peer.create_server(game_port, max_players - 1)
			if err != OK:
				_end("NET_HOST_FAILED", {"port": game_port})
				return
			multiplayer.multiplayer_peer = peer
			_start_announcing()
		Mode.CLIENT:
			var peer := ENetMultiplayerPeer.new()
			var err := peer.create_client(_join_address, _join_port)
			if err != OK:
				_end("NET_CONNECTION_FAILED")
				return
			multiplayer.multiplayer_peer = peer
			_connect_deadline = Time.get_ticks_msec() + int(CONNECT_TIMEOUT * 1000.0)
		_:
			mode = Mode.SOLO
			multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()


## Sai da sessão sem mensagem de erro (ex.: "Menu principal"). O cliente
## avisa o host, para o herói sair na hora em vez de esperar como queda.
func leave() -> void:
	if mode == Mode.CLIENT and multiplayer.multiplayer_peer is ENetMultiplayerPeer \
			and multiplayer.multiplayer_peer.get_connection_status() == MultiplayerPeer.CONNECTION_CONNECTED:
		_goodbye.rpc_id(1)
		multiplayer.multiplayer_peer.host.flush()
	_close()
	mode = Mode.NONE


## IPv4 locais deste PC, para o host informar quem quer entrar por IP.
static func local_addresses() -> Array[String]:
	var found: Array[String] = []
	for address in IP.get_local_addresses():
		if address.count(".") == 3 and not address.begins_with("127.") \
				and not address.begins_with("169.254."):
			found.append(address)
	return found


# --- Descoberta na LAN ------------------------------------------------------

func start_discovery() -> void:
	stop_discovery()
	hosts.clear()
	_listener = PacketPeerUDP.new()
	if _listener.bind(discovery_port) != OK:
		push_warning("Não foi possível escutar a porta de descoberta %d" % discovery_port)
		_listener = null


func stop_discovery() -> void:
	if _listener:
		_listener.close()
		_listener = null


func _start_announcing() -> void:
	_announcer = PacketPeerUDP.new()
	_announcer.set_broadcast_enabled(true)
	_announcer.set_dest_address("255.255.255.255", discovery_port)
	_announce_left = 0.0


func _process(delta: float) -> void:
	if _announcer:
		_announce_left -= delta
		if _announce_left <= 0.0:
			_announce_left = ANNOUNCE_INTERVAL
			var info := {"game": GAME_ID, "version": version(), "port": game_port,
				"host": host_name(), "players": player_count(), "max": max_players,
				"full": player_count() >= max_players}
			_announcer.put_packet(JSON.stringify(info).to_utf8_buffer())
	if _listener:
		_poll_discovery()
	if mode == Mode.CLIENT and _connect_deadline > 0 and Time.get_ticks_msec() > _connect_deadline:
		_end("NET_CONNECTION_FAILED")


func _poll_discovery() -> void:
	var changed := false
	while _listener.get_available_packet_count() > 0:
		var packet := _listener.get_packet()
		var address := _listener.get_packet_ip()
		var info: Variant = JSON.parse_string(packet.get_string_from_utf8())
		if not info is Dictionary or info.get("game") != GAME_ID:
			continue
		var port := int(info.get("port", game_port))
		hosts["%s:%d" % [address, port]] = {
			"address": address, "port": port, "version": str(info.get("version", "")),
			"host": str(info.get("host", "")).substr(0, 32),
			"players": int(info.get("players", 0)), "max": int(info.get("max", max_players)),
			"full": bool(info.get("full", false)),
			"seen": Time.get_ticks_msec(),
		}
		changed = true
	var now := Time.get_ticks_msec()
	for key in hosts.keys():
		if now - hosts[key].seen > HOST_TIMEOUT * 1000.0:
			hosts.erase(key)
			changed = true
	if changed:
		hosts_changed.emit()


# --- Aperto de mão ----------------------------------------------------------

func _on_connected_to_server() -> void:
	_connect_deadline = 0
	_hello.rpc_id(1, version(), _content_hash, client_id, Session.ensure_character().to_dict())


@rpc("any_peer", "reliable")
func _hello(client_version: String, client_content: String, from_client: String, character: Dictionary) -> void:
	if not is_server():
		return
	var peer_id := multiplayer.get_remote_sender_id()
	if client_version != version():
		_refuse(peer_id, "NET_VERSION_MISMATCH", {"host": version(), "local": client_version})
	elif client_content != _content_hash:
		_refuse(peer_id, "NET_CONTENT_MISMATCH", {"host": _content_hash, "local": client_content})
	elif player_count() >= max_players:
		_refuse(peer_id, "NET_SERVER_FULL", {})
	elif CharacterData.from_dict(character) == null:
		_refuse(peer_id, "NET_CHARACTER_INVALID", {})
	elif peer_id not in _accepted_peers:
		# Reentrou antes de o host notar a queda: a conexão antiga conta como caída
		# (e expira sozinha pelo timeout do ENet).
		for old in _accepted_peers.duplicate():
			if from_client != "" and _client_ids.get(old) == from_client:
				_accepted_peers.erase(old)
				peer_left.emit(old, true)
		_client_ids[peer_id] = from_client.substr(0, 64)
		_characters[peer_id] = character
		_accepted_peers.append(peer_id)
		_welcome.rpc_id(peer_id)
		peer_joined.emit(peer_id)


@rpc("any_peer", "reliable")
func _goodbye() -> void:
	var peer_id := multiplayer.get_remote_sender_id()
	if is_server() and peer_id not in _goodbyes:
		_goodbyes.append(peer_id)


@rpc("authority", "reliable")
func _welcome() -> void:
	accepted.emit()


@rpc("authority", "reliable")
func _refused(reason_key: String, args: Dictionary) -> void:
	_end(reason_key, args)


func _refuse(peer_id: int, reason_key: String, args: Dictionary) -> void:
	_refused.rpc_id(peer_id, reason_key, args)
	# Dá tempo da mensagem chegar antes de desconectar.
	get_tree().create_timer(0.5, true).timeout.connect(func() -> void:
		if multiplayer.multiplayer_peer is ENetMultiplayerPeer and peer_id in multiplayer.get_peers():
			multiplayer.multiplayer_peer.disconnect_peer(peer_id))


## O jogador só entra depois do _hello. Na LAN, uma queda é notada em poucos s.
func _on_peer_connected(peer_id: int) -> void:
	if is_server() and multiplayer.multiplayer_peer is ENetMultiplayerPeer:
		var timeout: int = GameData.balance.net.get("peer_timeout_ms", 8000)
		multiplayer.multiplayer_peer.get_peer(peer_id).set_timeout(32, timeout / 2, timeout)


func _on_peer_disconnected(peer_id: int) -> void:
	if peer_id in _accepted_peers:
		_accepted_peers.erase(peer_id)
		peer_left.emit(peer_id, peer_id not in _goodbyes)
	_goodbyes.erase(peer_id)


func _on_connection_failed() -> void:
	_end("NET_CONNECTION_FAILED")


func _on_server_disconnected() -> void:
	_end("NET_HOST_LEFT")


func _end(reason_key: String, args := {}) -> void:
	if last_error_key == "":
		last_error_key = reason_key
		last_error_args = args
	_close()
	mode = Mode.NONE
	session_ended.emit(reason_key)


func _close() -> void:
	_connect_deadline = 0
	if _announcer:
		_announcer.close()
		_announcer = null
	_accepted_peers.clear()
	_client_ids.clear()
	_characters.clear()
	_goodbyes.clear()
	SaveSystem.flush()
	if multiplayer.multiplayer_peer and not multiplayer.multiplayer_peer is OfflineMultiplayerPeer:
		multiplayer.multiplayer_peer.close()
	multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()


static func _load_client_id() -> String:
	var cfg := ConfigFile.new()
	cfg.load(CLIENT_ID_PATH)
	var id: String = cfg.get_value("client", "id", "")
	if id == "":
		var crypto := Crypto.new()
		id = crypto.generate_random_bytes(8).hex_encode()
		cfg.set_value("client", "id", id)
		cfg.save(CLIENT_ID_PATH)
	return id
