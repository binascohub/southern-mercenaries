# Southern Mercenaries — GPL-3.0-or-later
class_name JoinMenu
extends MenuPanel
## Entrar numa partida na LAN: lista das partidas encontradas por broadcast
## (navegável com o controle) e conexão manual por IP.

signal join_requested(address: String)

var _list: VBoxContainer
var _searching: Label
var _address: LineEdit


func _ready() -> void:
	add_title("JOIN_TITLE")
	_searching = Label.new()
	_searching.text = "JOIN_SEARCHING"
	_searching.modulate = Color(1, 1, 1, 0.7)
	content.add_child(_searching)
	_list = VBoxContainer.new()
	content.add_child(_list)

	var manual := Label.new()
	manual.text = "JOIN_MANUAL_ADDRESS"
	content.add_child(manual)
	var row := HBoxContainer.new()
	_address = LineEdit.new()
	_address.placeholder_text = "192.168.0.10:%d" % NetworkManager.game_port
	_address.custom_minimum_size = Vector2(220, 40)
	_address.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_address.text_submitted.connect(func(_t: String) -> void: _join_manual())
	row.add_child(_address)
	var connect_button := Button.new()
	connect_button.text = "JOIN_CONNECT"
	connect_button.pressed.connect(_join_manual)
	row.add_child(connect_button)
	content.add_child(row)

	add_button("MENU_BACK", close)
	NetworkManager.hosts_changed.connect(_refresh)


func _on_open() -> void:
	NetworkManager.start_discovery()
	_refresh()


func close() -> void:
	NetworkManager.stop_discovery()
	super.close()


func _refresh() -> void:
	for child in _list.get_children():
		child.queue_free()
	_searching.visible = NetworkManager.hosts.is_empty()
	for key in NetworkManager.hosts:
		var host: Dictionary = NetworkManager.hosts[key]
		var button := Button.new()
		button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		button.custom_minimum_size = Vector2(320, 44)
		if host.version != NetworkManager.version():
			button.text = tr("JOIN_HOST_OTHER_VERSION").format({"address": host.address, "version": host.version})
			button.disabled = true
		else:
			button.text = tr("JOIN_HOST_ENTRY").format({"host": host.host, "address": host.address,
				"players": host.players, "max": host.max})
			button.disabled = host.full
			button.pressed.connect(_join_address.bind("%s:%d" % [host.address, host.port]))
		_list.add_child(button)
	if visible and get_viewport().gui_get_focus_owner() == null:
		focus_first()


func _join_manual() -> void:
	var address := _address.text.strip_edges()
	var ip: String = NetworkManager.parse_address(address)[0]
	if ip.is_valid_ip_address() or ip == "localhost":
		_join_address(address)


func _join_address(address: String) -> void:
	NetworkManager.stop_discovery()
	join_requested.emit(address)
