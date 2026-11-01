# Southern Mercenaries — GPL-3.0-or-later
class_name PaintedTextures
extends RefCounted
## Texturas geradas por código (albedo + normal map) para os modelos que vêm só
## com cor lisa (a cortesã), para ficarem no nível dos heróis e do
## cenário, que usam texturas pintadas com relevo. Cada tipo é gerado uma vez.
## O albedo é claro e quase neutro: a cor do material (albedo_color) multiplica.

const SIZE := 128

static var _cache := {}


## Material pintado: `color` é a cor base; `kind` um de skin, cloth, leather,
## hair; `tile` o tamanho (em unidades do modelo) de uma repetição.
static func material(source: StandardMaterial3D, kind: String, color: Color, tile: float) -> StandardMaterial3D:
	var out := source.duplicate() as StandardMaterial3D
	var textures := _textures(kind)
	out.albedo_color = color
	out.albedo_texture = textures.albedo
	out.normal_enabled = true
	out.normal_texture = textures.normal
	out.normal_scale = float(textures.strength)
	out.roughness = float(textures.roughness)
	out.metallic = 0.0
	out.uv1_triplanar = true
	out.uv1_scale = Vector3.ONE / tile
	out.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	return out


static func _textures(kind: String) -> Dictionary:
	if _cache.has(kind):
		return _cache[kind]
	var height := PackedFloat32Array()
	var albedo := Image.create(SIZE, SIZE, false, Image.FORMAT_RGB8)
	height.resize(SIZE * SIZE)
	var blotch := _noise(0.025, 3)
	var grain := _noise(0.30, 11)
	var coarse := _noise(0.09, 5)
	var strength := 1.0
	var roughness := 0.85
	for y in SIZE:
		for x in SIZE:
			var b := blotch.get_pixel(x, y).r  # 0..1, manchas grandes
			var g := grain.get_pixel(x, y).r
			var c := coarse.get_pixel(x, y).r
			var h := 0.5
			var shade := 1.0
			match kind:
				"skin":
					# Poros e leve irregularidade; manchas bem suaves de cor.
					h = 0.5 + (g - 0.5) * 0.5 + (c - 0.5) * 0.3
					shade = 0.93 + (b - 0.5) * 0.14 + (g - 0.5) * 0.06
					strength = 0.5
					roughness = 0.7
				"cloth":
					# Trama de tecido: fios cruzados, sujeira e desgaste.
					var warp := 0.5 + 0.5 * sin(TAU * x / 8.0)
					var weft := 0.5 + 0.5 * sin(TAU * y / 8.0)
					h = (warp if (x / 8 + y / 8) % 2 == 0 else weft) * 0.6 + (g - 0.5) * 0.4
					shade = 0.82 + (b - 0.5) * 0.3 + (h - 0.5) * 0.12
					strength = 1.6
					roughness = 0.92
				"leather":
					# Couro curtido: rugas em células e manchas escuras.
					h = 0.5 + (g - 0.5) * 0.7 + (c - 0.5) * 0.6
					shade = 0.72 + (b - 0.5) * 0.45 + (c - 0.5) * 0.15
					strength = 1.3
					roughness = 0.6
				"hair":
					# Fios compridos (na vertical da textura) com brilho fraco.
					var strand := 0.5 + 0.5 * sin(TAU * (x * 2.0 + sin(TAU * y / SIZE) * 0.6) / 8.0 + g * 5.0)
					h = strand
					shade = 0.7 + strand * 0.45 + (b - 0.5) * 0.2
					strength = 0.9
					roughness = 0.55
			height[y * SIZE + x] = h
			var v := clampf(shade, 0.0, 1.0)
			albedo.set_pixel(x, y, Color(v, v, v))
	albedo.generate_mipmaps()
	var normal := Image.create(SIZE, SIZE, false, Image.FORMAT_RGB8)
	for y in SIZE:
		for x in SIZE:
			# Relevo do mapa de altura (ladrilhável: os vizinhos dão a volta).
			var dx := height[y * SIZE + (x + 1) % SIZE] - height[y * SIZE + (x + SIZE - 1) % SIZE]
			var dy := height[((y + 1) % SIZE) * SIZE + x] - height[((y + SIZE - 1) % SIZE) * SIZE + x]
			var n := Vector3(-dx * 3.0, -dy * 3.0, 1.0).normalized()
			normal.set_pixel(x, y, Color(n.x * 0.5 + 0.5, n.y * 0.5 + 0.5, n.z * 0.5 + 0.5))
	normal.generate_mipmaps()
	var result := {
		"albedo": ImageTexture.create_from_image(albedo),
		"normal": ImageTexture.create_from_image(normal),
		"strength": strength,
		"roughness": roughness,
	}
	_cache[kind] = result
	return result


## Ruído ladrilhável normalizado em 0..1.
static func _noise(frequency: float, seed_value: int) -> Image:
	var noise := FastNoiseLite.new()
	noise.frequency = frequency
	noise.seed = seed_value
	var image := noise.get_seamless_image(SIZE, SIZE, false, false, 0.2)
	image.convert(Image.FORMAT_RF)
	return image
