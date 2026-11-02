# Southern Mercenaries — GPL-3.0-or-later
extends "res://tools/spectator/spectator.gd"
## Espectador do Esgoto visto de cima, com o nome de cada monstro (e quantos), NPC, cartaz e portal flutuando sobre o lugar dele; mini-chefes e chefe em dourado.
##   XDG_DATA_HOME=$(mktemp -d) godot --path . res://tools/spectator/sewer_names.tscn           (visão de cima de todo o mapa)
##   ... res://tools/spectator/sewer_names.tscn -- sewers_01_drains X Y Z INCLINAÇÃO              (outra posição/área, como o espectador comum)
## Controles do espectador: W A S D andam, Q / E descem e sobem, Shift acelera; botão direito + arrastar olha; roda: velocidade; F1 ajuda; Esc fecha.
## `shot=<arquivo.png>` salva uma captura e sai.

const AREA := "sewers_01_drains"


func _ready() -> void:
	TranslationServer.set_locale("pt_BR")
	await super._ready()
	if _arena == null:
		return
	var args := OS.get_cmdline_user_args()
	var data: Dictionary = GameData.arenas[args[0] if args.size() > 0 and GameData.arenas.has(args[0]) else AREA]
	var root: Node = _arena.get("_area_root")
	# o Esgoto é escuro: luz branca por cima para ver a planta de cima
	for node in _arena.find_children("*", "WorldEnvironment", true, false):
		var we := node as WorldEnvironment
		if we and we.environment:
			we.environment.adjustment_enabled = true
			we.environment.adjustment_brightness = 1.5
			we.environment.adjustment_contrast = 1.1
			we.environment.fog_enabled = false
			we.environment.ambient_light_energy = 1.2
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-90, 0, 0)
	sun.light_energy = 0.5
	add_child(sun)
	# monstros: um nome por encontro (monstro x quantidade), no centro do encontro
	for enc: Dictionary in data.get("encounters", []):
		var parts: Array[String] = []
		var gold := false
		for m: Dictionary in enc.monsters:
			var info: Dictionary = GameData.monsters.get(m.monster, {})
			parts.append("%s x%d" % [TranslationServer.translate(info.get("name_key", m.monster)), int(m.get("count", 1))] if int(m.get("count", 1)) > 1 else TranslationServer.translate(info.get("name_key", m.monster)))
			gold = gold or info.get("category", "") in ["miniboss", "boss"] or m.get("rank", "") == "miniboss"
		_tag(_arena, enc.position, "\n".join(PackedStringArray(parts)), gold, 4.5 if gold else 3.2)
	for prop: Dictionary in data.get("props", []):
		var kind := String(prop.get("kind", ""))
		if kind in ["npc", "exit", "sign", "shop"]:
			var key := ""
			if prop.has("npc"):
				key = String(GameData.npcs.get(prop.npc, {}).get("name_key", ""))
			else:
				key = String(prop.get("name_key", ""))
			var text: String = String(TranslationServer.translate(key)) if key != "" else String(prop.get("id", ""))
			_tag(_arena, prop.position, "[%s]" % text, false, 3.0, Color(0.6, 0.9, 1.0))
	# títulos dos setores (nome do cartaz + os monstros que moram nele), grandes, no centro de cada setor
	var sector_of := func(id: String) -> int:
		if id.begins_with("sw") and id.length() > 2 and id[2].is_valid_int():
			return int(id[2])
		return 4 if id == "sw_old_gator" else 0
	var by_sector := {}
	for enc: Dictionary in data.get("encounters", []):
		var sec: int = sector_of.call(String(enc.id))
		if sec == 0:
			continue
		for m: Dictionary in enc.monsters:
			by_sector[sec] = by_sector.get(sec, []) + [TranslationServer.translate(GameData.monsters.get(m.monster, {}).get("name_key", m.monster))]
	by_sector[2] = by_sector.get(2, []) + [TranslationServer.translate("MONSTER_PLANK_MONSTER") if TranslationServer.translate("MONSTER_PLANK_MONSTER") != "MONSTER_PLANK_MONSTER" else "Rei dos Sapos (altar)"]
	var centers := {1: [0, -30], 2: [-45, -80], 3: [45, -80], 4: [45, -130], 5: [-45, -135]}
	for sec: int in centers:
		var names: Array = []
		for n in by_sector.get(sec, []):
			if n not in names:
				names.append(n)
		var title := "SETOR %d — %s\n%s" % [sec, TranslationServer.translate("PROP_SEWER_SECTOR_%d" % sec), ", ".join(PackedStringArray(names))]
		var big := Label3D.new()
		big.text = title
		big.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		big.no_depth_test = true
		big.font_size = 56
		big.pixel_size = 0.075
		big.outline_size = 16
		big.shaded = false
		big.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		big.modulate = [Color(1, 0.6, 0.3), Color(0.5, 1, 0.5), Color(0.5, 0.8, 1), Color(1, 0.9, 0.4), Color(0.9, 0.6, 1)][sec - 1]
		big.position = Vector3(centers[sec][0], 6.0, centers[sec][1])
		_arena.add_child(big)
	for entry: Dictionary in data.get("crowd", []):
		_tag(_arena, entry.position, String(entry.role), false, 2.5, Color(0.85, 0.85, 0.85))
	for arg in args:
		if String(arg).begins_with("shot="):
			await get_tree().create_timer(4.0).timeout
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(String(arg).trim_prefix("shot="))
			get_tree().quit()


func _tag(root: Node, position: Array, text: String, gold: bool, height: float, color := Color(1, 0.95, 0.6)) -> void:
	var label := Label3D.new()
	label.text = text
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.no_depth_test = true
	label.font_size = 40
	label.pixel_size = 0.11 if gold else 0.085
	label.shaded = false
	label.fixed_size = false
	label.outline_size = 10
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	label.modulate = Color(1.0, 0.8, 0.2) if gold else color
	label.position = Vector3(float(position[0]), height, float(position[1]))
	root.add_child(label)
