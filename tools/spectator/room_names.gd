# Southern Mercenaries — GPL-3.0-or-later
extends "res://tools/spectator/spectator.gd"
## Espectador com o nome de cada sala (id) da área sobre ela, e as saídas, portões, NPCs e encontros marcados:
##   XDG_DATA_HOME=$(mktemp -d) godot --path . res://tools/spectator/room_names.tscn -- forest_01_path 60 170 -55 -90
## Mesmos controles do espectador. Salas em branco; saídas em verde; portão em vermelho; NPCs em amarelo; encontros em laranja.


func _ready() -> void:
	await super._ready()
	var args := OS.get_cmdline_user_args()
	var area: String = args[0] if args.size() > 0 else DEFAULT_AREA
	var data: Dictionary = GameData.arenas[area]
	var root: Node = _arena.get("_area_root")
	for room: Dictionary in data.get("rooms", []):
		_label(root, "%s\\n%dx%d" % [room.id, int(room.size[0]), int(room.size[1])], Vector3(room.center[0], 2.0, room.center[1]), Color.WHITE, 0.16)
	for prop: Dictionary in data.get("props", []):
		var text := ""
		var color := Color.WHITE
		match String(prop.kind):
			"exit":
				text = "SAÍDA → %s" % prop.get("to", "")
				color = Color(0.4, 1.0, 0.5)
			"gate":
				text = "PORTÃO DO CHEFE"
				color = Color(1.0, 0.3, 0.3)
			"npc":
				text = "NPC: %s" % prop.get("npc", prop.id)
				color = Color(1.0, 0.9, 0.3)
		if text != "":
			_label(root, text, Vector3(prop.position[0], 6.0, prop.position[1]), color, 0.1)
	for enc: Dictionary in data.get("encounters", []):
		var names: Array = []
		for m: Dictionary in enc.monsters:
			names.append("%s x%d" % [m.monster, int(m.count)])
		if enc.id in ["f_leshy"] or names.any(func(n: String) -> bool: return n.begins_with(("leshy"))) or enc.id.begins_with("fb_"):
			_label(root, "%s: %s" % [enc.id, ", ".join(names)], Vector3(enc.position[0], 9.0, enc.position[1]), Color(1.0, 0.6, 0.2), 0.1)


func _label(root: Node, text: String, at: Vector3, color: Color, pixel: float) -> void:
	var label := Label3D.new()
	label.text = text.replace("\\n", "\n")
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.font_size = 48
	label.pixel_size = pixel
	label.outline_size = 14
	label.modulate = color
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	label.position = at
	root.add_child(label)
