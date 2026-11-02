# Southern Mercenaries — GPL-3.0-or-later
extends "res://tools/spectator/spectator.gd"
## Espectador com o nome de cada NPC e figurante da área flutuando sobre ele (o papel/id e, quando tem, o nome traduzido):
##   XDG_DATA_HOME=$(mktemp -d) godot --path . res://tools/spectator/npc_names.tscn -- tortuga 0 14 10 -50
## Os rótulos acompanham quem anda. Mesmos controles do espectador.


func _ready() -> void:
	await super._ready()
	var args := OS.get_cmdline_user_args()
	var area: String = args[0] if args.size() > 0 else DEFAULT_AREA
	var data: Dictionary = GameData.arenas[area]
	var root: Node = _arena.get("_area_root")
	if root == null:
		return
	for entry: Dictionary in data.get("crowd", []):
		var role := String(entry.role)
		var role_title := role
		if entry.role == "brawl":
			role_title = "briga: " + " x ".join(PackedStringArray(entry.get("fighters", ["drunk", "pirate"])))
		_tag(root, entry.position, role_title, "", 3.0 if role in ["pig", "cat", "chicken"] else 2.3)
	for prop: Dictionary in data.get("props", []):
		if prop.get("kind", "") in ["npc", "shop"]:
			var key := ""
			if prop.has("npc"):
				key = String(GameData.npcs.get(prop.npc, {}).get("name_key", ""))
			else:
				key = String(prop.get("name_key", ""))
			_tag(root, prop.position, String(prop.get("npc", prop.get("id", ""))), tr(key) if key != "" else "", 2.6)


func _tag(root: Node, position: Array, title: String, translated: String, height: float) -> void:
	var holder: Node3D = null
	for child in root.get_children():
		var n := child as Node3D
		if n and absf(n.position.x - float(position[0])) < 0.05 and absf(n.position.z - float(position[1])) < 0.05 and not n is Label3D:
			holder = n
			break
	var label := Label3D.new()
	label.text = title if translated == "" else "%s\n%s" % [translated, title]
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.font_size = 40
	label.pixel_size = 0.011
	label.outline_size = 10
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	label.modulate = Color(1, 0.95, 0.6) if translated != "" else Color(1, 1, 1)
	if holder:
		label.position = Vector3(0, height, 0)
		holder.add_child(label)
	else:
		label.position = Vector3(float(position[0]), height, float(position[1]))
		root.add_child(label)
