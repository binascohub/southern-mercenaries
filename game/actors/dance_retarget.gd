# Southern Mercenaries — GPL-3.0-or-later
class_name DanceRetarget
extends RefCounted
## Passa a dança profissional dos heróis (Universal Animation Library, "Dance",
## Quaternius, CC0) para o esqueleto da cortesã, que é outro: os dois estão em pose
## de T, então o movimento de cada osso mapeado (a rotação global em relação ao
## repouso) vale nos dois. Dá para gerar variações da mesma dança: espelhada,
## com o quadril mais marcado e em outra velocidade.

const SOURCE := "res://assets/models/characters/hero_female.glb"
const SOURCE_ANIMATION := "Dance"
const STEP := 1.0 / 30.0

## Osso do herói -> osso da cortesã.
const BONES := {
	"pelvis": "hips", "spine_01": "spine", "spine_03": "brust", "clavicle_l": "brust_L", "clavicle_r": "brust_R",
	"upperarm_l": "oberArm_L", "lowerarm_l": "unterarm_L", "hand_l": "hand_L",
	"upperarm_r": "oberArm_R", "lowerarm_r": "unterarm_R", "hand_r": "hand_R",
	"neck_01": "hals", "Head_2": "kopf",
	"thigh_l": "oberSchenkel_L", "calf_l": "unterSchenkel_L", "foot_l": "fuss_L",
	"thigh_r": "oberSchenkel_R", "calf_r": "unterSchenkel_R", "foot_r": "fuss_R",
}
## Ossos do tronco que podem ter o movimento exagerado (o quadril e a coluna).
const TORSO := ["pelvis", "spine_01", "spine_03"]

static var _source: Dictionary = {}
static var _cache := {}


## A dança retargetada para `target` (o esqueleto da cortesã), ou null se faltar o arquivo.
## `options`: mirror (espelha esquerda e direita), hips (força do quadril e da coluna,
## 1 = como é), speed (velocidade). `base` é a animação de repouso que dá os ossos que a
## dança não move (e o prefixo dos caminhos das faixas).
static func build(target: Skeleton3D, base: Animation, options: Dictionary) -> Animation:
	var key := "%s|%s|%s" % [options.get("mirror", false), options.get("hips", 1.0), options.get("speed", 1.0)]
	if _cache.has(key):
		return _cache[key]
	if not _load_source():
		return null
	var src_animation: Animation = _source.animation
	var mirror: bool = options.get("mirror", false)
	var hips_gain: float = options.get("hips", 1.0)
	var speed: float = maxf(options.get("speed", 1.0), 0.1)
	var length := src_animation.length
	var steps := int(ceil(length / STEP))

	# Caminho das faixas e ossos que a base já anima (para manter os que a dança não toca).
	var prefix := ""
	var base_tracks := {}
	for t in base.get_track_count():
		var path := base.track_get_path(t)
		prefix = String(path).get_slice(":", 0)
		base_tracks["%d:%s" % [base.track_get_type(t), path.get_concatenated_subnames()]] = t
	var out := Animation.new()
	out.length = length / speed
	out.loop_mode = Animation.LOOP_LINEAR

	# Ossos de origem por osso de destino (espelhado: a esquerda dança com o que era da direita).
	var source_for := {}
	for src_name: String in BONES:
		var dst_name: String = BONES[src_name]
		if mirror:
			dst_name = _swap_side(dst_name)
		source_for[dst_name] = src_name

	# Tabelas do esqueleto de origem (lidas uma vez em _load_source).
	var src_names: Array = _source.names
	var src_parents: Array = _source.parents
	var src_count := src_names.size()
	var src_rest_global: Array = _source.rest_global
	var src_rest_local: Array = _source.rest_local
	var src_tracks := {}
	for t in src_animation.get_track_count():
		var name := String(src_animation.track_get_path(t).get_concatenated_subnames())
		src_tracks["%d:%s" % [src_animation.track_get_type(t), name]] = t
	var src_pelvis: int = src_names.find("pelvis")
	var src_pelvis_rest: Vector3 = _source.pelvis_rest
	var src_parent_basis: Basis = _source.parent_basis
	var pelvis_position_track: int = src_tracks.get("%d:pelvis" % Animation.TYPE_POSITION_3D, -1)

	# Tabelas do esqueleto de destino.
	var dst_count := target.get_bone_count()
	var dst_rest_global: Array[Transform3D] = []
	for i in dst_count:
		dst_rest_global.append(target.get_bone_global_rest(i))
	var hips := target.find_bone("hips")
	var height_ratio := dst_rest_global[hips].origin.y / maxf(float(_source.pelvis_height), 0.01)

	# Uma faixa de rotação por osso de destino (os mapeados se mexem; os outros ficam como na base).
	var rotation_track := {}
	for i in dst_count:
		var name := target.get_bone_name(i)
		if source_for.has(name):
			var track := out.add_track(Animation.TYPE_ROTATION_3D)
			out.track_set_path(track, NodePath("%s:%s" % [prefix, name]))
			rotation_track[name] = track
	var position_track := out.add_track(Animation.TYPE_POSITION_3D)
	out.track_set_path(position_track, NodePath("%s:hips" % prefix))
	# Os ossos da base que a dança não move continuam como na base (primeiro quadro).
	for key_name: String in base_tracks:
		var type := int(key_name.get_slice(":", 0))
		var name := key_name.get_slice(":", 1)
		if source_for.has(name) and type != Animation.TYPE_SCALE_3D:
			continue
		var track := out.add_track(type)
		out.track_set_path(track, NodePath("%s:%s" % [prefix, name]))
		var index: int = base_tracks[key_name]
		var value: Variant
		match type:
			Animation.TYPE_POSITION_3D: value = base.position_track_interpolate(index, 0.0)
			Animation.TYPE_ROTATION_3D: value = base.rotation_track_interpolate(index, 0.0)
			_: value = base.scale_track_interpolate(index, 0.0)
		out.track_insert_key(track, 0.0, value)
		out.track_insert_key(track, out.length, value)

	for step in steps + 1:
		var time := minf(step * STEP, length)
		# Rotações globais da origem neste instante.
		var local: Array[Quaternion] = []
		var global_now: Array[Quaternion] = []
		for i in src_count:
			var q: Quaternion = src_rest_local[i]
			var index: int = src_tracks.get("%d:%s" % [Animation.TYPE_ROTATION_3D, src_names[i]], -1)
			if index >= 0:
				q = src_animation.rotation_track_interpolate(index, time)
			local.append(q)
			var parent: int = src_parents[i]
			global_now.append((global_now[parent] if parent >= 0 else Quaternion.IDENTITY) * q)
		# Rotações globais do destino: mapeados = variação da origem sobre o repouso do destino.
		var dst_global: Array[Quaternion] = []
		for i in dst_count:
			var name := target.get_bone_name(i)
			var parent := target.get_bone_parent(i)
			var rest_q := dst_rest_global[i].basis.get_rotation_quaternion()
			var q: Quaternion
			if source_for.has(name):
				var src_index: int = src_names.find(source_for[name])
				var delta: Quaternion = global_now[src_index] * (src_rest_global[src_index] as Quaternion).inverse()
				if mirror:
					delta = Quaternion(delta.x, -delta.y, -delta.z, delta.w)
				if source_for[name] in TORSO and not is_equal_approx(hips_gain, 1.0):
					delta = Quaternion.IDENTITY.slerp(delta, hips_gain)
				q = delta * rest_q
			elif parent >= 0:
				var parent_rest := dst_rest_global[parent].basis.get_rotation_quaternion()
				q = dst_global[parent] * parent_rest.inverse() * rest_q
			else:
				q = rest_q
			dst_global.append(q)
			if rotation_track.has(name):
				var local_q := (dst_global[parent].inverse() if parent >= 0 else Quaternion.IDENTITY) * q
				out.rotation_track_insert_key(rotation_track[name], time / speed, local_q.normalized())
		# O quadril sobe e desce e balança como o do herói (na proporção da cortesã).
		var pelvis_now := src_pelvis_rest
		if pelvis_position_track >= 0:
			pelvis_now = src_animation.position_track_interpolate(pelvis_position_track, time)
		# A posição da animação está no espaço do osso pai (o raiz do herói é girado): para o espaço do esqueleto.
		var delta_position := src_parent_basis * (pelvis_now - src_pelvis_rest) * height_ratio
		if mirror:
			delta_position.x = -delta_position.x
		var hips_parent := target.get_bone_parent(hips)
		var parent_transform := dst_rest_global[hips_parent] if hips_parent >= 0 else Transform3D.IDENTITY
		var target_position := dst_rest_global[hips].origin + delta_position
		out.position_track_insert_key(position_track, time / speed, parent_transform.affine_inverse() * target_position)
	_cache[key] = out
	return out


static func _swap_side(bone: String) -> String:
	if bone.ends_with("_L"):
		return bone.trim_suffix("_L") + "_R"
	if bone.ends_with("_R"):
		return bone.trim_suffix("_R") + "_L"
	return bone


static func _load_source() -> bool:
	if not _source.is_empty():
		return true
	if not ResourceLoader.exists(SOURCE):
		return false
	var scene := (load(SOURCE) as PackedScene).instantiate()
	var player := scene.find_child("AnimationPlayer", true, false) as AnimationPlayer
	var skeleton := scene.find_child("Skeleton3D", true, false) as Skeleton3D
	if player == null or skeleton == null or not player.has_animation(SOURCE_ANIMATION):
		scene.free()
		return false
	var names: Array = []
	var parents: Array = []
	var rest_local: Array = []
	var rest_global: Array = []
	for i in skeleton.get_bone_count():
		names.append(skeleton.get_bone_name(i))
		var parent := skeleton.get_bone_parent(i)
		parents.append(parent)
		var local_q := skeleton.get_bone_rest(i).basis.get_rotation_quaternion()
		rest_local.append(local_q)
		rest_global.append((rest_global[parent] if parent >= 0 else Quaternion.IDENTITY) * local_q)
	var pelvis := skeleton.find_bone("pelvis")
	var pelvis_parent := skeleton.get_bone_parent(pelvis)
	_source = {"names": names, "parents": parents, "rest_local": rest_local, "rest_global": rest_global,
		"pelvis_rest": skeleton.get_bone_rest(pelvis).origin,
		"pelvis_height": skeleton.get_bone_global_rest(pelvis).origin.y,
		"parent_basis": skeleton.get_bone_global_rest(pelvis_parent).basis if pelvis_parent >= 0 else Basis.IDENTITY,
		"animation": player.get_animation(SOURCE_ANIMATION).duplicate()}
	scene.free()  # só ficam os dados: uma cena instanciada guardada aqui vazaria ao sair
	return true
