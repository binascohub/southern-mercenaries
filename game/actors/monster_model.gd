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
	# Corpo: a Dark Elf (danimal, CC BY-SA 3.0) sem a cabeça (tools/assets/behead.py),
	# com as animações dela; 7,09 unidades de altura -> 1,8 (body_scale).
	"queen": {"scene": "res://assets/models/monsters/rat_head.glb", "humanoid": true, "scale": 0.6,
		"body_scene": "res://assets/models/monsters/rat_queen_body.glb", "body_scale": 0.254,
		"bones": {"head": "Head", "chest": "Spine1", "hips": "Hips"},
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "die": "die"}},
	"gator": {"scene": "res://assets/models/monsters/gator.glb", "scale": 0.75,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "die": "die"}},
	# Monstro da Floresta (cdmir, CC0): gigante de casca e pedra com uma árvore nas
	# costas (34,5 unidades de altura: ~2,5 m por unidade de size). Para os mapas seguintes.
	"forest": {"scene": "res://assets/models/monsters/forest_monster.glb", "scale": 0.072,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "die": "die"}},
	# Escorpião (sunburn, CC BY 3.0): sem esqueleto; as peças (corpo, pinças,
	# patas) são animadas aqui ("procedural"). ~1 m por unidade de size.
	"scorpion": {"scene": "res://assets/models/monsters/scorpion.glb", "scale": 1.5, "procedural": true,
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
const RAT_HEAD_SCALE := 2.6
const WING_COLOR := Color(0.22, 0.14, 0.16)
## A Rainha (referência do autor): couro marrom, pelagem clara e rosada nas
## orelhas, mãos e cauda; asas de couro marrom levantadas.
const QUEEN_FUR := Color(1.5, 1.28, 1.22)
const QUEEN_PINK := Color(0.93, 0.66, 0.64)
const QUEEN_WING := Color(0.42, 0.27, 0.19)
var _wing_color := WING_COLOR
## Asas levantadas (radianos para cima, além da batida).
var _wing_raise := 0.0
var _tail: Node3D
## Peças animadas à mão (escorpião): nome -> [nó, transformação de repouso].
var _parts := {}
var _action_time := 0.0


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
	if info.get("procedural", false):
		for key: String in info.anims:
			_names[key] = info.anims[key]
		for node in model.find_children("*", "Node3D", true, false):
			var part := node as Node3D
			if String(part.name).begins_with("Leg_") or String(part.name).begins_with("Claw_") or String(part.name) == "Body":
				_parts[String(part.name)] = [part, part.transform]
		_current = "idle"
		return true
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
	_tint = QUEEN_FUR
	var bones: Dictionary = info.get("bones", {"head": "Head", "chest": "spine_03", "hips": "pelvis"})
	if info.has("body_scene") and ResourceLoader.exists(info.body_scene):
		# Corpo próprio já sem cabeça, com esqueleto e animações.
		var body := Node3D.new()
		body.scale = Vector3.ONE * float(info.body_scale)
		add_child(body)
		var model := (load(info.body_scene) as PackedScene).instantiate()
		body.add_child(model)
		_skeleton = model.find_child("Skeleton3D", true, false) as Skeleton3D
		_anim = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
		for key: String in info.anims:
			if _anim and _anim.has_animation(info.anims[key]):
				_names[key] = info.anims[key]
				_anim.get_animation(info.anims[key]).loop_mode = Animation.LOOP_NONE if key in ONCE else Animation.LOOP_LINEAR
	else:
		_hero = HeroModel.new()
		add_child(_hero)
		_hero.setup("female", {"hair": [], "hair_color": [0.2, 0.15, 0.1]})
		_hero.set_outfit({"body": "copper", "hands": "copper", "feet": "wood"})  # couro marrom
		_hero.hide_parts(["Head", "Eyes", "Eyebrows"])
		_hero.tint_skin(QUEEN_PINK)  # mãos rosadas
		_skeleton = _hero.skeleton
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
	_add_ears(head)
	_fur_skin(head)
	var back := Node3D.new()
	add_child(back)
	_tail = Node3D.new()
	add_child(_tail)
	if _skeleton and _skeleton.find_bone(bones.head) >= 0 and _skeleton.find_bone(bones.chest) >= 0:
		var neck := _rest_in_model(bones.head).origin
		_follow_bone(head, bones.head, Transform3D(Basis.from_scale(Vector3.ONE * RAT_HEAD_SCALE),
			neck - RAT_NECK * RAT_HEAD_SCALE + Vector3(0, -0.04, 0.02)))
		_follow_bone(back, bones.chest, Transform3D(Basis(), _rest_in_model(bones.chest).origin + Vector3(0, 0.05, -0.12)))
		if _skeleton.find_bone(bones.hips) >= 0:
			_follow_bone(_tail, bones.hips, Transform3D(Basis(), _rest_in_model(bones.hips).origin + Vector3(0, -0.05, -0.12)))
	else:
		head.position = Vector3(0, 1.6, 0) - RAT_NECK * RAT_HEAD_SCALE
		head.scale = Vector3.ONE * RAT_HEAD_SCALE
		back.position = Vector3(0, 1.35, -0.12)
	if _tail.position == Vector3.ZERO:
		_tail.position = Vector3(0, 0.9, -0.12)
	_add_tail(_tail)
	_add_crown(head, false)
	_crown.scale = Vector3.ONE * 0.75  # tiara pequena
	_crown.rotation = Vector3(-0.1, 0, 0.05)
	_wing_color = QUEEN_WING
	_wing_size = 1.9
	_wing_raise = 0.55
	_add_wings(back, Vector3(0.08, 0, 0))
	play("idle", 0.0)
	return true


## A pele do corpo ganha a mesma pelagem da cabeça (a textura do rato, projetada
## em três eixos porque o mapa UV do corpo é outro), na mesma cor.
func _fur_skin(head: Node3D) -> void:
	# A textura do corpo do rato (só pelo; a da cabeça tem olhos e boca).
	var fur: Texture2D = null
	if ResourceLoader.exists(FAMILIES.rat.scene):
		var rat := (load(FAMILIES.rat.scene) as PackedScene).instantiate()
		for node in rat.find_children("*", "MeshInstance3D", true, false):
			var mesh := node as MeshInstance3D
			if String(mesh.name) == "Body" and mesh.get_active_material(0) is StandardMaterial3D:
				fur = (mesh.get_active_material(0) as StandardMaterial3D).albedo_texture
		rat.free()
	if fur == null:
		for material in _materials:
			if material.albedo_texture:
				fur = material.albedo_texture
				break
	if fur == null:
		return
	var skin := StandardMaterial3D.new()
	skin.albedo_texture = fur
	skin.albedo_color = _tint
	skin.uv1_triplanar = true
	skin.uv1_scale = Vector3.ONE * 2.5
	skin.roughness = 0.85
	for node in find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		if mesh.is_ancestor_of(head) or head.is_ancestor_of(mesh):
			continue
		for i in mesh.get_surface_override_material_count():
			var source := mesh.get_active_material(i)
			if source and String(source.resource_name).contains("Skin"):
				mesh.set_surface_override_material(i, skin)
	_materials.append(skin)


## Orelhas grandes e rosadas (unidades da cabeça de rato).
func _add_ears(head: Node3D) -> void:
	var outer := StandardMaterial3D.new()
	outer.albedo_color = Color(0.85, 0.72, 0.68)
	var inner := StandardMaterial3D.new()
	inner.albedo_color = QUEEN_PINK
	for side in [-1.0, 1.0]:
		var ear := Node3D.new()
		ear.position = Vector3(0.075 * side, 0.215, 0.35)
		ear.rotation = Vector3(-0.3, 0.5 * side, 0.55 * side)
		head.add_child(ear)
		for layer in [[outer, 1.0, 0.0], [inner, 0.75, 0.012]]:
			var mesh := MeshInstance3D.new()
			var sphere := SphereMesh.new()
			sphere.radius = 0.075 * layer[1]
			sphere.height = 0.15 * layer[1]
			mesh.mesh = sphere
			mesh.scale = Vector3(1.0, 1.15, 0.22)
			mesh.position = Vector3(0, 0.06 * layer[1], layer[2])
			mesh.material_override = layer[0]
			ear.add_child(mesh)


## Cauda longa e rosada: segmentos do quadril até o chão, afinando.
func _add_tail(root: Node3D) -> void:
	var pink := StandardMaterial3D.new()
	pink.albedo_color = QUEEN_PINK
	pink.roughness = 0.6
	var sway := Node3D.new()  # o nó de cima segue o osso; este balança
	root.add_child(sway)
	var points := [Vector3(0, 0, 0), Vector3(0, -0.2, -0.22), Vector3(0.05, -0.5, -0.4), Vector3(0.12, -0.78, -0.6),
		Vector3(0.22, -0.88, -0.9), Vector3(0.36, -0.9, -1.15), Vector3(0.5, -0.86, -1.35), Vector3(0.58, -0.8, -1.5)]
	for i in points.size() - 1:
		var a: Vector3 = points[i]
		var b: Vector3 = points[i + 1]
		var segment := MeshInstance3D.new()
		var rod := CylinderMesh.new()
		var t := float(i) / (points.size() - 1)
		rod.bottom_radius = lerpf(0.05, 0.012, t)
		rod.top_radius = lerpf(0.05, 0.012, t + 1.0 / (points.size() - 1))
		rod.height = a.distance_to(b) + 0.02
		rod.radial_segments = 8
		segment.mesh = rod
		segment.material_override = pink
		segment.position = (a + b) / 2.0
		segment.basis = Basis(Quaternion(Vector3.UP, (b - a).normalized()))
		sway.add_child(segment)


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
	_wing_material.albedo_color = _wing_color
	_wing_material.roughness = 0.65
	_wing_material.cull_mode = BaseMaterial3D.CULL_DISABLED
	var bone_material := StandardMaterial3D.new()
	bone_material.albedo_color = _wing_color.darkened(0.45)
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
	if not _parts.is_empty():
		_animate_parts(delta)
	if not _follows.is_empty() and _skeleton:
		var to_model := global_transform.affine_inverse() * _skeleton.global_transform
		for follow: Array in _follows:
			(follow[0] as Node3D).transform = to_model * _skeleton.get_bone_global_pose(follow[1]) * (follow[2] as Transform3D)
	if _crown and _head_bone >= 0:
		# A cabeça se mexe com a animação: a coroa vai junto (em unidades do modelo).
		var moved := _skeleton.get_bone_global_pose(_head_bone).origin - _head_rest
		var to_model := global_transform.affine_inverse() * _skeleton.global_transform
		_crown.position = CROWN_AT + to_model.basis * moved
	if _tail and _tail.get_child_count() > 0:
		# A cauda balança devagar de um lado para o outro.
		var sway := _tail.get_child(0) as Node3D
		sway.rotation.y = sin(Time.get_ticks_msec() / 700.0) * 0.35
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
		wing.rotation.z = (flap + _wing_raise) * side


## Escorpião: patas em onda ao andar, pinças abrindo e fechando no ataque,
## corpo subindo e descendo; na morte, cai de lado.
func _animate_parts(delta: float) -> void:
	_time += delta
	_action_time += delta
	var moving := _current in ["walk", "run"]
	var t := _time * (11.0 if moving else 2.0)
	for part_name: String in _parts:
		var entry: Array = _parts[part_name]
		var node: Node3D = entry[0]
		var rest: Transform3D = entry[1]
		var turn := Vector3.ZERO
		if part_name.begins_with("Leg_"):
			var index := int(part_name.get_slice("_", 2))
			var side := 1.0 if part_name.contains("_L_") else -1.0
			var phase := index * 2.1 + (0.0 if side > 0.0 else PI)
			turn = Vector3(0.0, sin(t + phase) * (0.45 if moving else 0.05), cos(t + phase) * (0.25 if moving else 0.03) * side)
		elif part_name.begins_with("Claw_"):
			var side := 1.0 if part_name.ends_with("L") else -1.0
			var snap := sin(minf(_action_time / 0.5, 1.0) * PI) if _current == "attack" else 0.0
			turn = Vector3(-0.5 * snap, (0.35 * snap + 0.05 * sin(_time * 1.7)) * side, 0.0)
		elif part_name == "Body":
			var lift := sin(t * 2.0) * (0.015 if moving else 0.006)
			node.transform = rest.translated(Vector3(0, lift, 0))
			continue
		node.transform = Transform3D(rest.basis * Basis.from_euler(turn), rest.origin)
	if _current == "die":
		rotation.z = lerpf(rotation.z, PI * 0.9, minf(delta * 4.0, 1.0))


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
	if not _parts.is_empty():
		_current = key
		_action_time = 0.0
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
		_wing_material.albedo_color = _wing_color * color
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
