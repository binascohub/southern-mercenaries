// Southern Mercenaries — GPL-3.0-or-later
// Marca de perigo no chão (avisos dos golpes de monstro, poças, o ponteiro do Capitão): um padrão em preto e branco
// (Kenney Pattern Pack, CC0; assets/fx/patterns) que desliza dentro de um círculo (ou de uma faixa), com a borda acesa.
// `fill` (0..1) é até onde o círculo já se encheu: o aviso cresce do centro e mostra quanto tempo falta.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, shadows_disabled;

uniform sampler2D pattern : source_color, repeat_enable, filter_linear_mipmap;
uniform vec4 color : source_color = vec4(0.95, 0.2, 0.1, 0.6);
uniform vec2 tiles = vec2(3.0, 3.0);
uniform vec2 scroll = vec2(0.35, 0.0);
uniform float fill = 1.0;
uniform float rim = 0.08;
uniform bool band = false;  // faixa (o ponteiro): sem recorte redondo, borda nas laterais
uniform float strength = 1.0;

void fragment() {
	vec2 c = UV * 2.0 - 1.0;
	float d = band ? abs(c.y) : length(c);
	if (d > 1.0) {
		discard;
	}
	float p = texture(pattern, UV * tiles + scroll * TIME).r;
	float inside = band ? 1.0 : smoothstep(fill + 0.02, fill - 0.02, d);
	float edge = smoothstep(1.0 - rim * 2.0, 1.0 - rim * 0.5, d) * (1.0 - smoothstep(1.0 - rim * 0.3, 1.0, d) * 0.4);
	float front = band ? 0.0 : (1.0 - smoothstep(0.0, 0.05, abs(d - fill))) * step(fill, 0.98);
	ALBEDO = color.rgb * (0.75 + 0.5 * p);
	ALPHA = clamp(color.a * strength * (0.18 + 0.55 * p * inside + edge * 1.4 + front * 1.2), 0.0, 1.0);
}
