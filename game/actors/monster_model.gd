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
	return true


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
