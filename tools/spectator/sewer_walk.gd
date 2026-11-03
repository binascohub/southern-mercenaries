# Southern Mercenaries — GPL-3.0-or-later
extends "res://tools/spectator/spectator.gd"
## Espectador do Esgoto com os monstros ANDANDO (patrulham em volta de onde nasceram, como o Mímico) e um marcador colorido por tipo em cima de cada um,
## para ver a densidade do mapa. Sem nomes: a legenda de cores fica no canto da tela.
##   XDG_DATA_HOME=$(mktemp -d) godot --path . res://tools/spectator/sewer_walk.tscn            (de cima, no centro do mapa)
##   ... res://tools/spectator/sewer_walk.tscn -- sewers_01_drains X Y Z INCLINAÇÃO              (outra posição, como o espectador comum)
## Controles: os do espectador (W A S D, Q / E, Shift, botão direito + arrastar, roda, F1, Esc).

const COLORS := {
	"mutant": Color(0.75, 0.3, 1.0), "chest_mimic": Color(1.0, 0.15, 0.15), "troll_mauler": Color(1.0, 0.55, 0.1),
	"shadow_spirit": Color(0.2, 0.9, 1.0), "barbarian_monster": Color(0.65, 0.4, 0.15), "demon_twelve": Color(1.0, 0.2, 0.7),
	"champ_warrior": Color(0.3, 1.0, 0.3), "golden_dragon": Color(0.9, 0.9, 1.0), "demon_rat_queen": Color(1.0, 0.85, 0.2), "frog_king": Color(1.0, 0.85, 0.2), "old_gator": Color(1.0, 0.85, 0.2),
}


func _ready() -> void:
	TranslationServer.set_locale("pt_BR")
	default_area = "sewers_01_drains"
	default_pos = Vector3(0, 110, -60)
	default_look = Vector3(0, -1, -60.001)
	await super._ready()
	if _arena == null:
		return
	for node in _arena.find_children("*", "WorldEnvironment", true, false):
		var we := node as WorldEnvironment
		if we and we.environment:
			we.environment.adjustment_enabled = true
			we.environment.adjustment_brightness = 1.6
			we.environment.fog_enabled = false
			we.environment.ambient_light_energy = 1.3
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-90, 0, 0)
	sun.light_energy = 0.5
	add_child(sun)
	var count := {}
	for node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy := node as Enemy
		if enemy == null or enemy.data.get("breakable", false) or enemy.data.get("dummy", false):
			continue
		count[enemy.monster_id] = int(count.get(enemy.monster_id, 0)) + 1
		enemy.data = enemy.data.duplicate()
		enemy.data["patrol"] = true  # dormindo, mas andando em volta do ponto de origem
		enemy.data["patrol_radius"] = 7.0
		enemy.data["patrol_speed"] = 0.9
		var marker := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = 1.1
		sphere.height = 2.2
		marker.mesh = sphere
		var material := StandardMaterial3D.new()
		material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		material.albedo_color = COLORS.get(enemy.monster_id, Color.WHITE)
		marker.material_override = material
		marker.position.y = 4.0
		marker.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		enemy.add_child(marker)
	var layer := CanvasLayer.new()
	add_child(layer)
	var box := VBoxContainer.new()
	box.position = Vector2(14, 60)
	layer.add_child(box)
	var total := 0
	var rows: Array = [["Monstros andando (cor do marcador):", Color.WHITE]]
	for id: String in count:
		rows.append(["● %s: %d" % [TranslationServer.translate(GameData.monsters.get(id, {}).get("name_key", id)), count[id]], COLORS.get(id, Color.WHITE)])
		total += int(count[id])
	rows.append(["Total: %d (o altar invoca mais 4)" % total, Color.WHITE])
	for row: Array in rows:
		var label := Label.new()
		label.text = String(row[0])
		label.add_theme_font_size_override("font_size", 18)
		label.add_theme_color_override("font_color", row[1])
		label.add_theme_color_override("font_outline_color", Color(0, 0, 0))
		label.add_theme_constant_override("outline_size", 6)
		box.add_child(label)
