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
## A Rainha dos Ratos tem corpo humano (HeroModel, roupa escura) com a cabeça
## do rato no lugar da humana; cabeça, coroa e asas seguem os ossos do corpo.
## A Rainha ganha asas de morcego (feitas aqui: membrana e dedos) quando chega
## à metade da vida: elas brotam das costas e batem, mais rápido no ataque.

const FAMILIES := {
	"rat": {"scene": "res://assets/models/monsters/rat.glb", "scale": 1.35,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# A Rainha: corpo humano (o dos heróis, com as animações deles) e cabeça de rato.
	"queen": {"scene": "res://assets/models/monsters/rat_head.glb", "humanoid": true, "scale": 0.6,
		"anims": {"idle": "zombie_idle", "walk": "zombie_walk", "run": "run", "attack": "zombie_scratch", "hit": "hit", "die": "death"}},
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
## Coroa da Rainha: segue o osso da cabeça (posição), sempre de pé.
var _crown: Node3D
var _skeleton: Skeleton3D
var _head_bone := -1
var _head_rest := Vector3.ZERO
## Topo da cabeça do rato em repouso (unidades do modelo; frente +Z).
const CROWN_AT := Vector3(0, 0.215, 0.39)
var _wings_out := false
## Corpo humano (a Rainha) e as peças presas aos ossos: [nó, osso, deslocamento].
var _hero: HeroModel
var _follows: Array = []
var _wing_size := 1.0
## Pescoço da cabeça de rato (rat_head.glb, unidades do rato) e o tamanho dela no corpo.
const RAT_NECK := Vector3(0, 0.12, 0.33)
const RAT_HEAD_SCALE := 1.6
const WING_COLOR := Color(0.22, 0.14, 0.16)


static func has_family(look: String) -> bool:
	return FAMILIES.has(look) and ResourceLoader.exists(FAMILIES[look].scene)


## Monta o modelo da família no tamanho do monstro; tint = cor dos dados.
func setup(look: String, size: float, tint: Color) -> bool:
	if not has_family(look):
		return false
	family = look
	var info: Dictionary = FAMILIES[look]
	if info.get("humanoid", false):
		return _setup_humanoid(info, size, tint)
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
	return true


## Corpo humano com cabeça de rato: as animações são as dos heróis.
func _setup_humanoid(info: Dictionary, size: float, tint: Color) -> bool:
	scale = Vector3.ONE * size * float(info.scale)
	_tint = Color.WHITE.lerp(tint, 0.35)
	_hero = HeroModel.new()
	add_child(_hero)
	_hero.setup("male", {"hair": [], "hair_color": [0.2, 0.15, 0.1]})
	_hero.set_outfit({"body": "iron", "hands": "iron", "feet": "iron"})
	_hero.hide_parts(["Head", "Eyes", "Eyebrows"])
	_hero.tint_skin(Color(0.36, 0.29, 0.26))  # pelagem nas mãos
	for key: String in info.anims:
		_names[key] = info.anims[key]
	var head := Node3D.new()
	add_child(head)
	head.add_child((load(info.scene) as PackedScene).instantiate())
	for node in head.find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for i in mesh.get_surface_override_material_count():
			var source := mesh.get_active_material(i) as StandardMaterial3D
			if source:
				var copy := source.duplicate() as StandardMaterial3D
				copy.albedo_color = _tint
				copy.cull_mode = BaseMaterial3D.CULL_DISABLED
				mesh.set_surface_override_material(i, copy)
				_materials.append(copy)
	var back := Node3D.new()
	add_child(back)
	_skeleton = _hero.skeleton
	if _skeleton and _skeleton.find_bone("Head") >= 0 and _skeleton.find_bone("spine_03") >= 0:
		var neck := _rest_in_model("Head").origin
		_follow_bone(head, "Head", Transform3D(Basis.from_scale(Vector3.ONE * RAT_HEAD_SCALE),
			neck - RAT_NECK * RAT_HEAD_SCALE + Vector3(0, 0.05, 0)))
		_follow_bone(back, "spine_03", Transform3D(Basis(), _rest_in_model("spine_03").origin + Vector3(0, 0.05, -0.12)))
	else:
		head.position = Vector3(0, 1.6, 0) - RAT_NECK * RAT_HEAD_SCALE
		head.scale = Vector3.ONE * RAT_HEAD_SCALE
		back.position = Vector3(0, 1.35, -0.12)
	_add_crown(head, false)
	_wing_size = 1.6
	_add_wings(back, Vector3(0.08, 0, 0))
	play("idle", 0.0)
	return true


## Pose de descanso do osso nas coordenadas deste nó.
func _rest_in_model(bone: String) -> Transform3D:
	var to_model := global_transform.affine_inverse() * _skeleton.global_transform
	return to_model * _skeleton.get_bone_global_rest(_skeleton.find_bone(bone))


## `node` acompanha o osso: em repouso fica em `at` (coordenadas deste nó).
func _follow_bone(node: Node3D, bone: String, at: Transform3D) -> void:
	var rest := _rest_in_model(bone)
	_follows.append([node, _skeleton.find_bone(bone), rest.affine_inverse() * at])
	node.transform = at


## Coroa de ouro com pontas (a coroa torta do rei caído), na cabeça.
func _add_crown(parent: Node3D, follow_head: bool) -> void:
	_crown = Node3D.new()
	parent.add_child(_crown)
	_crown.position = CROWN_AT
	_crown.rotation = Vector3(-0.25, 0, 0.18)  # torta, caindo para trás
	var gold := StandardMaterial3D.new()
	gold.albedo_color = Color(0.95, 0.72, 0.22)
	gold.metallic = 0.85
	gold.roughness = 0.3
	gold.emission_enabled = true
	gold.emission = Color(0.35, 0.22, 0.04)
	var band := MeshInstance3D.new()
	var ring := CylinderMesh.new()
	ring.top_radius = 0.075
	ring.bottom_radius = 0.07
	ring.height = 0.035
	ring.radial_segments = 16
	band.mesh = ring
	band.material_override = gold
	_crown.add_child(band)
	for i in 6:
		var angle := TAU * i / 6.0
		var spike := MeshInstance3D.new()
		var prism := PrismMesh.new()
		prism.size = Vector3(0.035, 0.07, 0.012)
		spike.mesh = prism
		spike.material_override = gold
		spike.position = Vector3(sin(angle) * 0.07, 0.05, cos(angle) * 0.07)
		spike.rotation.y = angle
		_crown.add_child(spike)
	var gem := MeshInstance3D.new()
	var stone := SphereMesh.new()
	stone.radius = 0.016
	stone.height = 0.032
	gem.mesh = stone
	var red := StandardMaterial3D.new()
	red.albedo_color = Color(0.8, 0.05, 0.08)
	red.emission_enabled = true
	red.emission = Color(0.5, 0.02, 0.04)
	gem.material_override = red
	gem.position = Vector3(0, 0.0, 0.075)
	_crown.add_child(gem)
	if not follow_head:
		return
	_skeleton = find_child("Skeleton3D", true, false) as Skeleton3D
	if _skeleton:
		_head_bone = _skeleton.find_bone("Head")
		if _head_bone >= 0:
			_head_rest = _skeleton.get_bone_global_rest(_head_bone).origin


## Duas asas de morcego nas costas (em unidades do modelo: o rato tem 1 m, a
## frente é +Z): membrana com a borda recortada entre os dedos.
func _add_wings(parent: Node3D, at: Vector3) -> void:
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
		pivot.position = Vector3(at.x * side, at.y, at.z)
		pivot.scale = Vector3(side, 1, 1) * 0.001
		pivot.visible = false
		parent.add_child(pivot)
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
	if not _follows.is_empty() and _skeleton:
		var to_model := global_transform.affine_inverse() * _skeleton.global_transform
		for follow: Array in _follows:
			(follow[0] as Node3D).transform = to_model * _skeleton.get_bone_global_pose(follow[1]) * (follow[2] as Transform3D)
	if _crown and _head_bone >= 0:
		# A cabeça se mexe com a animação: a coroa vai junto (em unidades do modelo).
		var moved := _skeleton.get_bone_global_pose(_head_bone).origin - _head_rest
		var to_model := global_transform.affine_inverse() * _skeleton.global_transform
		_crown.position = CROWN_AT + to_model.basis * moved
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
		wing.scale = Vector3(side, 1, 1) * grow * _wing_size
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
	if key == _current or not _names.has(key):
		return
	if _hero:
		_current = key
		_hero.play_key(_names[key], blend)
		return
	if _anim == null:
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
	if _hero:
		_hero.set_effects(color != Color.WHITE, 1.0, Color(0, 0, 0, 0))


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
