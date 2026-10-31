# Southern Mercenaries — GPL-3.0-or-later
class_name MonsterModel
extends Node3D
## Corpo animado dos monstros do Esgoto (modelos do OpenGameArt convertidos por
## tools/assets/build_monsters.py; créditos no CREDITS.md): rato (Rato
## Pestilento, Ratazana e a Rainha, de coroa), morcego e jacaré. Cada família
## tem o arquivo, o tamanho por unidade de `size` do monstro e as animações por
## estado. Sem o arquivo (testes sem importação), quem chama mantém a cápsula.
##
## A cor do monstro (dados "color") tinge a textura de leve; o aviso do golpe,
## o golpe sofrido e os estados elementais tingem por cima (set_color).
## A Rainha ganha asas de morcego (feitas aqui: membrana e dedos) quando chega
## à metade da vida: elas brotam das costas e batem, mais rápido no ataque.

const FAMILIES := {
	"rat": {"scene": "res://assets/models/monsters/rat.glb", "scale": 1.35,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	"queen": {"scene": "res://assets/models/monsters/rat.glb", "scale": 1.35,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	"gator": {"scene": "res://assets/models/monsters/gator.glb", "scale": 0.75,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "die": "die"}},
	# O morcego guarda o tamanho original do arquivo (envergadura ~10 unidades).
	"bat": {"scene": "res://assets/models/monsters/bat.glb", "scale": 0.2,
		"anims": {"idle": "fly", "walk": "fly", "run": "fly", "attack": "fly", "die": "die"}},
}
## Animações que não repetem.
const ONCE := ["attack", "hit", "die"]
const BLEND := 0.15

var family := ""
var _anim: AnimationPlayer
var _names := {}
var _current := ""
var _materials: Array[StandardMaterial3D] = []
var _tint := Color.WHITE
## Asas de morcego da Rainha (pivôs que batem) e o material delas.
var _wings: Array[Node3D] = []
var _wing_material: StandardMaterial3D
var _time := 0.0
## 0 = asas recolhidas (escondidas); cresce até 1 quando elas brotam.
var _wing_growth := 0.0
var _wings_out := false
const WING_COLOR := Color(0.22, 0.14, 0.16)


static func has_family(look: String) -> bool:
	return FAMILIES.has(look) and ResourceLoader.exists(FAMILIES[look].scene)


## Monta o modelo da família no tamanho do monstro; tint = cor dos dados.
func setup(look: String, size: float, tint: Color) -> bool:
	if not has_family(look):
		return false
	family = look
	var info: Dictionary = FAMILIES[look]
	var model := (load(info.scene) as PackedScene).instantiate()
	add_child(model)
	scale = Vector3.ONE * size * float(info.scale)
	_tint = Color.WHITE.lerp(tint, 0.35)
	for node in model.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for i in mesh.get_surface_override_material_count():
			var source := mesh.get_active_material(i) as StandardMaterial3D
			if source == null:
				continue
			var copy := source.duplicate() as StandardMaterial3D
			copy.albedo_color = _tint
			# Os modelos antigos têm faces viradas para dentro (o morcego visto de cima).
			copy.cull_mode = BaseMaterial3D.CULL_DISABLED
			mesh.set_surface_override_material(i, copy)
			_materials.append(copy)
	_anim = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if _anim:
		for key: String in info.anims:
			var wanted: String = info.anims[key]
			if _anim.has_animation(wanted):
				_names[key] = wanted
				_anim.get_animation(wanted).loop_mode = Animation.LOOP_NONE if key in ONCE and wanted != "fly" \
					else Animation.LOOP_LINEAR
		play("idle", 0.0)
	if look == "queen":
		_add_wings()
	return true


## Duas asas de morcego nas costas (em unidades do modelo: o rato tem 1 m, a
## frente é +Z): membrana com a borda recortada entre os dedos.
func _add_wings() -> void:
	_wing_material = StandardMaterial3D.new()
	_wing_material.albedo_color = WING_COLOR
	_wing_material.roughness = 0.65
	_wing_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	var bone_material := StandardMaterial3D.new()
	bone_material.albedo_color = Color(0.12, 0.08, 0.08)
	# Dedos (pontas) e os recortes da borda entre eles.
	var tips := [Vector3(0.95, 0.3, 0.05), Vector3(0.85, 0.12, -0.3), Vector3(0.6, 0.02, -0.52), Vector3(0.3, 0.0, -0.5)]
	var edge: Array[Vector3] = [Vector3(0.12, 0.08, 0.12), tips[0]]
	for i in range(1, tips.size()):
		var mid: Vector3 = (tips[i - 1] + tips[i]) / 2.0
		edge.append(mid.lerp(Vector3.ZERO, 0.22))
		edge.append(tips[i])
	edge.append(Vector3(0.05, 0.0, -0.3))
	for side in [-1.0, 1.0]:
		var pivot := Node3D.new()
		pivot.position = Vector3(0.07 * side, 0.27, 0.1)
		pivot.scale = Vector3(side, 1, 1) * 0.001
		pivot.visible = false
		add_child(pivot)
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		for i in range(1, edge.size() - 1):
			st.add_vertex(edge[0])
			st.add_vertex(edge[i])
			st.add_vertex(edge[i + 1])
		st.generate_normals()
		var membrane := MeshInstance3D.new()
		membrane.mesh = st.commit()
		membrane.material_override = _wing_material
		pivot.add_child(membrane)
		for tip: Vector3 in tips:
			var finger := MeshInstance3D.new()
			var rod := CylinderMesh.new()
			rod.top_radius = 0.008
			rod.bottom_radius = 0.018
			rod.height = tip.length()
			finger.mesh = rod
			finger.material_override = bone_material
			finger.position = tip / 2.0
			finger.basis = Basis(Quaternion(Vector3.UP, tip.normalized()))
			pivot.add_child(finger)
		_wings.append(pivot)


func _process(delta: float) -> void:
	if _wings.is_empty():
		return
	# Bate devagar parada, mais rápido correndo ou no golpe.
	if _wings_out and _wing_growth < 1.0:
		_wing_growth = minf(_wing_growth + delta / 0.8, 1.0)
	_time += delta * (6.0 if _current in ["run", "attack"] or _wing_growth < 1.0 else 2.5)
	var flap := 0.15 + 0.4 * sin(_time)
	var grow := maxf(ease(_wing_growth, 0.4), 0.001)
	for wing in _wings:
		var side := signf(wing.scale.x)
		wing.visible = _wings_out
		wing.scale = Vector3(side, 1, 1) * grow
		wing.rotation.z = flap * side


## As asas de morcego brotam das costas (a Rainha na metade da vida).
func show_wings(out: bool) -> void:
	_wings_out = out
	if not out:
		_wing_growth = 0.0


func wings_out() -> bool:
	return _wings_out


## Toca a animação (idle, walk, run, attack, hit, die) se ainda não está nela.
func play(key: String, blend := BLEND) -> void:
	if _anim == null or key == _current or not _names.has(key):
		return
	_current = key
	_anim.play(_names[key], blend)


func current() -> String:
	return _current


## Cor por cima da textura (Color.WHITE = cor própria do monstro).
func set_color(color: Color) -> void:
	var final := _tint * color
	for material in _materials:
		material.albedo_color = final
	if _wing_material:
		_wing_material.albedo_color = WING_COLOR * color


## Animações que este modelo tem (testes).
func animations() -> Array:
	return _names.keys()


## Tamanho ocupado pelos ossos agora (x, y, z no mundo): confere a escala e a
## orientação nas capturas do CI.
func bone_extent() -> Vector3:
	var skeleton := find_child("Skeleton3D", true, false) as Skeleton3D
	if skeleton == null or skeleton.get_bone_count() == 0:
		return Vector3.ZERO
	var box := AABB(skeleton.global_transform * skeleton.get_bone_global_pose(0).origin, Vector3.ZERO)
	for i in skeleton.get_bone_count():
		box = box.expand(skeleton.global_transform * skeleton.get_bone_global_pose(i).origin)
	return box.size
