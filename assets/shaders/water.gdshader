// Southern Mercenaries — GPL-3.0-or-later
// Água dos lagos, do riacho da Fazenda e do mar: duas camadas de normais que correm em sentidos diferentes, cor que escurece com a "profundidade" (distância da margem),
// linhas de cáustica, espuma na margem e um brilho de Fresnel. Textura e normais feitas por tools/assets/build_water_textures.py.
shader_type spatial;
render_mode specular_schlick_ggx, shadows_disabled;

uniform vec4 shallow_color : source_color = vec4(0.18, 0.4, 0.46, 1.0);
uniform vec4 deep_color : source_color = vec4(0.05, 0.14, 0.22, 1.0);
uniform vec4 foam_color : source_color = vec4(0.88, 0.95, 0.96, 1.0);
uniform sampler2D normal_tex : hint_normal, repeat_enable, filter_linear_mipmap;
uniform sampler2D caustic_tex : repeat_enable, filter_linear_mipmap;
uniform float tex_scale = 0.16;
uniform vec2 flow = vec2(0.02, 0.012);
uniform vec2 half_size = vec2(5.0, 5.0);
uniform float round_shape = 0.0;
uniform float foam_amount = 1.0;
uniform float foam_width = 0.5;
uniform float depth_range = 3.0;
uniform float alpha = 0.92;
uniform float shape_amp[5];   // lagoas redondas: contorno irregular (harmônicos 2..6 do ângulo)
uniform float shape_phase[5];
uniform float edge_wobble = 0.0; // margem irregular (m): o contorno avança e recua até esta distância

varying vec2 wpos;
varying vec2 lpos;

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xz;
	lpos = VERTEX.xz;
}

void fragment() {
	// distância da margem (retângulo ou elipse)
	float d;
	if (round_shape > 0.5) {
		vec2 q = lpos / half_size;
		float e = length(q);
		float ang = atan(q.y, q.x);
		float edge = 1.0;
		for (int k = 0; k < 5; k++) {
			edge += shape_amp[k] * sin(float(k + 2) * ang + shape_phase[k]);
		}
		if (e > edge) {
			discard;
		}
		d = (edge - e) * min(half_size.x, half_size.y);
	} else {
		vec2 q = half_size - abs(lpos);
		d = min(q.x, q.y);
		if (edge_wobble > 0.0) {
			float n = texture(caustic_tex, lpos * 0.071 + 0.13).g * 0.6 + texture(caustic_tex, lpos * 0.19 + 0.47).g * 0.3 + texture(caustic_tex, lpos * 0.53 + 0.81).g * 0.1;
			d += (n - 0.5) * 2.4 * edge_wobble;
			if (d < 0.0) {
				discard;
			}
		}
	}
	vec2 uv1 = wpos * tex_scale + TIME * flow;
	vec2 uv2 = wpos * tex_scale * 0.63 + vec2(0.31, 0.17) - TIME * flow * 0.7;
	vec3 n1 = texture(normal_tex, uv1).rgb;
	vec3 n2 = texture(normal_tex, uv2).rgb;
	NORMAL_MAP = mix(n1, n2, 0.5);
	NORMAL_MAP_DEPTH = 0.9;
	float depth = smoothstep(0.0, depth_range, d);
	vec3 base = mix(shallow_color.rgb, deep_color.rgb, depth);
	float caustic = texture(caustic_tex, wpos * tex_scale * 0.7 + TIME * flow * 0.6).r * texture(caustic_tex, wpos * tex_scale * 1.1 - TIME * flow * 0.4 + 0.5).r;
	base += vec3(0.55, 0.8, 0.85) * caustic * 0.6 * (1.0 - depth * 0.6);
	float noise = texture(caustic_tex, wpos * 0.45 + TIME * 0.05).g;
	float foam = smoothstep(foam_width, 0.0, d + noise * 0.3 - 0.1) * foam_amount * 0.85;
	float fresnel = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0);
	ALBEDO = mix(base, foam_color.rgb, foam) + vec3(0.12, 0.16, 0.2) * fresnel;
	ROUGHNESS = mix(0.06, 0.6, foam);
	SPECULAR = 0.7;
	ALPHA = mix(alpha, 1.0, foam);
}
