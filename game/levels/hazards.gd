# Southern Mercenaries — GPL-3.0-or-later
class_name Hazards
extends Node
## Perigos no chão dos mapas (03-2-areas.md; 03-inimigos.md): poças de lodo
## tóxico (fixas da área, do cuspe do Sapo Ácido e do rastro das elites tóxicas)
## e as marcas de aviso dos golpes de monstro no chão. O servidor guarda as
## poças e tira vida de quem está dentro a cada `hazard_tick`; os visuais vão
## para a raiz da área (somem ao trocar de área).

const SLUDGE_COLOR := Color(0.35, 0.6, 0.15, 0.45)
const WARNING_COLOR := Color(0.95, 0.2, 0.1, 0.4)

## Onde ficam os discos (a raiz da área atual).
var root: Node3D
## Só no servidor: {position, radius, time (<0 = fixa), dps, level}.
var _list: Array[Dictionary] = []
var _tick := 0.0


## Nova área (servidor): esquece as poças e registra as fixas da área.
func reset(area: Dictionary) -> void:
	_list.clear()
	var level := int(area.get("area_level", 1))
	var dps: float = GameData.balance.get("sludge_dps", 3.0) * pow(1.12, level - 1)
	for hazard: Dictionary in area.get("hazards", []):
		_list.append({"position": Vector3(hazard.position[0], 0, hazard.position[1]),
			"radius": float(hazard.radius), "time": -1.0, "dps": dps, "level": level})


## Visuais das poças fixas (todos os PCs, ao montar a área).
func build_static(area: Dictionary) -> void:
	for hazard: Dictionary in area.get("hazards", []):
		_disc(Vector3(hazard.position[0], 0, hazard.position[1]), float(hazard.radius), SLUDGE_COLOR, -1.0)


## Poça temporária (servidor), vista em todos os PCs.
func add(at: Vector3, radius: float, duration: float, dps: float, level: int) -> void:
	if not multiplayer.is_server():
		return
	_list.append({"position": Vector3(at.x, 0, at.z), "radius": radius, "time": duration, "dps": dps, "level": level})
	_show_sludge.rpc(at, radius, duration)


## Marca vermelha no chão: o golpe cai ali quando o tempo acabar.
func telegraph(at: Vector3, radius: float, time: float) -> void:
	if multiplayer.is_server():
		_show_warning.rpc(at, radius, time)


## Golpe no chão (cuspe, pisão): quem está dentro leva o dano; com "puddle_time", deixa poça.
func strike(at: Vector3, radius: float, damage: float, level: int, source: Node3D, extra: Dictionary) -> void:
	if not multiplayer.is_server():
		return
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if p.alive and _inside(p.global_position, at, radius):
			p.take_damage(damage, level, source)
	if float(extra.get("puddle_time", 0.0)) > 0.0:
		add(at, radius, float(extra.puddle_time), float(extra.get("puddle_dps", 3.0)) * pow(1.12, level - 1), level)


## Quantos perigos o servidor acompanha agora (testes).
func count() -> int:
	return _list.size()


func _physics_process(delta: float) -> void:
	if not multiplayer.is_server() or _list.is_empty():
		return
	for hazard in _list.duplicate():
		if hazard.time >= 0.0:
			hazard.time -= delta
			if hazard.time <= 0.0:
				_list.erase(hazard)
	_tick -= delta
	if _tick > 0.0:
		return
	var tick: float = GameData.balance.get("hazard_tick", 0.5)
	_tick = tick
	for p: Player in get_tree().get_nodes_in_group(&"players"):
		if not p.alive:
			continue
		for hazard in _list:
			if _inside(p.global_position, hazard.position, hazard.radius):
				p.take_damage(hazard.dps * tick, hazard.level, null)
				break


static func _inside(point: Vector3, center: Vector3, radius: float) -> bool:
	return Vector2(point.x - center.x, point.z - center.z).length() <= radius


@rpc("authority", "call_local", "reliable")
func _show_sludge(at: Vector3, radius: float, duration: float) -> void:
	_disc(at, radius, SLUDGE_COLOR, duration)


@rpc("authority", "call_local", "reliable")
func _show_warning(at: Vector3, radius: float, time: float) -> void:
	var disc := _disc(at, radius, WARNING_COLOR, time)
	if disc:
		# Cresce do centro até o tamanho do golpe: dá para ver quanto tempo falta.
		disc.scale = Vector3(0.2, 1, 0.2)
		disc.create_tween().tween_property(disc, "scale", Vector3.ONE, time)


func _disc(at: Vector3, radius: float, color: Color, duration: float) -> MeshInstance3D:
	if root == null or not is_instance_valid(root):
		return null
	var disc := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = 0.03
	mesh.radial_segments = 24
	disc.mesh = mesh
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.albedo_color = color
	disc.material_override = material
	disc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(disc)
	disc.position = Vector3(at.x, 0.04, at.z)
	if duration > 0.0:
		get_tree().create_timer(duration, false).timeout.connect(disc.queue_free)
	return disc
