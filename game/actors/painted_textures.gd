# Southern Mercenaries — GPL-3.0-or-later
class_name PaintedTextures
extends RefCounted
## Texturas geradas por código (albedo + normal map) para os modelos que vêm só
## com cor lisa (a cortesã), para ficarem no nível dos heróis e do
## cenário, que usam texturas pintadas com relevo. Cada tipo é gerado uma vez.
## O albedo é claro e quase neutro: a cor do material (albedo_color) multiplica.

const SIZE := 128
## Tipos que precisam de mais detalhe (costuras, rebites, argolas): textura de 256 px.
const DETAILED := 256
const DETAILED_KINDS: Array[String] = ["cloth", "leather", "metal", "chain", "fur", "trim"]

static var _cache := {}


## Material pintado: `color` é a cor base; `kind` um de skin, cloth, leather,
## hair, wood, chain (malha), metal (chapa); `tile` o tamanho (em unidades do modelo) de uma repetição.
static func material(source: StandardMaterial3D, kind: String, color: Color, tile: float) -> StandardMaterial3D:
	var out := source.duplicate() as StandardMaterial3D
	var textures := _textures(kind)
	out.albedo_color = color
	out.albedo_texture = textures.albedo
	out.normal_enabled = true
	out.normal_texture = textures.normal
	out.normal_scale = float(textures.strength)
	out.roughness = float(textures.roughness)
	out.metallic = float(textures.get("metallic", 0.0))
	out.uv1_triplanar = true
	out.uv1_scale = Vector3.ONE / tile
	out.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	return out


static func _textures(kind: String) -> Dictionary:
	if _cache.has(kind):
		return _cache[kind]
	var size := DETAILED if kind in DETAILED_KINDS else SIZE
	var height := PackedFloat32Array()
	var albedo := Image.create(size, size, false, Image.FORMAT_RGB8)
	height.resize(size * size)
	var blotch := _noise(0.025, 3, size)
	var grain := _noise(0.30, 11, size)
	var coarse := _noise(0.09, 5, size)
	var strength := 1.0
	var roughness := 0.85
	var metallic := 0.0
	for y in size:
		for x in size:
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
					# Tecido: trama fina de fios, dobras compridas na vertical, manchas e desgaste.
					var warp := 0.5 + 0.5 * sin(TAU * x / 6.0)
					var weft := 0.5 + 0.5 * sin(TAU * y / 6.0)
					var weave := warp if (x / 3 + y / 3) % 2 == 0 else weft
					var fold := 0.5 + 0.5 * sin(TAU * (x * 3.0 / size + (c - 0.5) * 1.4))
					h = weave * 0.3 + fold * 0.5 + (g - 0.5) * 0.2
					shade = 0.76 + (b - 0.5) * 0.34 + (fold - 0.5) * 0.24 + (weave - 0.5) * 0.1
					if b > 0.78:
						shade -= 0.14 * (b - 0.78) / 0.22
					strength = 2.2
					roughness = 0.92
				"leather":
					# Couro curtido: grão fino, vincos largos, arranhões claros e bordas escurecidas.
					var crease := 1.0 if absf(c - 0.5) < 0.025 else 0.0
					h = 0.5 + (g - 0.5) * 0.55 + (c - 0.5) * 0.5 - crease * 0.3
					shade = 0.7 + (b - 0.5) * 0.4 + (c - 0.5) * 0.2 - crease * 0.28
					if g > 0.86:
						shade += 0.09
					strength = 1.8
					roughness = 0.55
				"wood":
					# Tábuas: veios compridos (na horizontal da textura), nós e manchas.
					var grain_line := 0.5 + 0.5 * sin(TAU * (y * 3.0 + (g - 0.5) * 5.0 + (b - 0.5) * 9.0) / SIZE * 2.0)
					h = 0.5 + (grain_line - 0.5) * 0.5 + (c - 0.5) * 0.2
					shade = 0.72 + grain_line * 0.2 + (b - 0.5) * 0.25
					strength = 0.9
					roughness = 0.88
				"chain":
					# Cota de malha: argolas entrelaçadas de 12 px em fileiras alternadas, cada uma com
					# furo escuro no meio e aro em relevo.
					var row := y / 6
					var cx := (x + (6 if row % 2 == 0 else 0)) % 12 - 6
					var cy := y % 6 - 3
					var d := sqrt(float(cx * cx) + float(cy * cy * 4))
					var ring := absf(d - 4.4)
					var tube := clampf(1.0 - ring * 0.6, 0.0, 1.0)
					h = tube * 0.85 + (g - 0.5) * 0.15
					shade = 0.18 + tube * 0.8 + (b - 0.5) * 0.08
					strength = 2.4
					roughness = 0.4
					metallic = 0.8
				"metal":
					# Chapa: riscos de escova, rebites a cada 64 px, linhas gravadas entre painéis,
					# arranhões e pátina nas manchas.
					var streak := 0.5 + 0.5 * sin(TAU * (y * 2.0 + (g - 0.5) * 12.0) / size * 3.0)
					h = 0.5 + (streak - 0.5) * 0.18 + (c - 0.5) * 0.15
					shade = 0.66 + streak * 0.12 + (b - 0.5) * 0.28
					var rx := float(x % 64 - 32)
					var ry := float(y % 64 - 32)
					var rivet := sqrt(rx * rx + ry * ry)
					if rivet < 6.0:
						var lit := clampf(1.0 - rivet / 6.0, 0.0, 1.0)
						h += 0.5 * lit
						shade += (0.18 if rx + ry < 0.0 else -0.14) * lit + 0.05
					if x % 128 < 2 or y % 128 < 2:
						h -= 0.35
						shade -= 0.3
					if g > 0.94:
						shade += 0.1
					if b > 0.68:
						shade -= 0.16 * (b - 0.68) / 0.32
					strength = 1.5
					roughness = 0.38
					metallic = 0.8
				"fur":
					# Pelo: tufos compridos e irregulares na vertical, claros nas pontas.
					var strand := 0.5 + 0.5 * sin(TAU * (x * 9.0 / size + sin(TAU * y / size * 2.0) * 0.4 + (g - 0.5) * 0.8))
					h = strand * 0.7 + (c - 0.5) * 0.3
					shade = 0.45 + strand * 0.45 + (b - 0.5) * 0.3
					strength = 1.6
					roughness = 0.96
				"trim":
					# Bordado: fileira de losangos com pontos, em relevo sobre um tecido escuro.
					var u := float(x % 32) / 32.0
					var vv := float(y % 32) / 32.0
					var diamond := absf(u - 0.5) + absf(vv - 0.5)
					var line := 1.0 if absf(diamond - 0.36) < 0.045 else 0.0
					var dot := 1.0 if diamond < 0.07 else 0.0
					var edge := 1.0 if (y % 32 < 3 or y % 32 > 28) else 0.0
					var motif := maxf(maxf(line, dot), edge)
					var warp_t := 0.5 + 0.5 * sin(TAU * x / 5.0)
					h = motif * 0.8 + warp_t * 0.15 + (g - 0.5) * 0.1
					shade = 0.32 + motif * 0.68 + (warp_t - 0.5) * 0.05
					strength = 1.8
					roughness = 0.7
				"hair":
					# Fios compridos (na vertical da textura) com brilho fraco.
					var strand := 0.5 + 0.5 * sin(TAU * (x * 2.0 + sin(TAU * y / SIZE) * 0.6) / 8.0 + g * 5.0)
					h = strand
					shade = 0.7 + strand * 0.45 + (b - 0.5) * 0.2
					strength = 0.9
					roughness = 0.55
			height[y * size + x] = h
			var v := clampf(shade, 0.0, 1.0)
			albedo.set_pixel(x, y, Color(v, v, v))
	albedo.generate_mipmaps()
	var normal := Image.create(size, size, false, Image.FORMAT_RGB8)
	for y in size:
		for x in size:
			# Relevo do mapa de altura (ladrilhável: os vizinhos dão a volta).
			var dx := height[y * size + (x + 1) % size] - height[y * size + (x + size - 1) % size]
			var dy := height[((y + 1) % size) * size + x] - height[((y + size - 1) % size) * size + x]
			var n := Vector3(-dx * 3.0, -dy * 3.0, 1.0).normalized()
			normal.set_pixel(x, y, Color(n.x * 0.5 + 0.5, n.y * 0.5 + 0.5, n.z * 0.5 + 0.5))
	normal.generate_mipmaps()
	var result := {
		"albedo": ImageTexture.create_from_image(albedo),
		"normal": ImageTexture.create_from_image(normal),
		"strength": strength,
		"roughness": roughness,
		"metallic": metallic,
	}
	_cache[kind] = result
	return result


## Ruído ladrilhável normalizado em 0..1.
static func _noise(frequency: float, seed_value: int, size := SIZE) -> Image:
	var noise := FastNoiseLite.new()
	noise.frequency = frequency * float(SIZE) / float(size)
	noise.seed = seed_value
	var image := noise.get_seamless_image(size, size, false, false, 0.2)
	image.convert(Image.FORMAT_RF)
	return image
