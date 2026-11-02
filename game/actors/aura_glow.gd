# Southern Mercenaries — GPL-3.0-or-later
class_name AuraGlow
extends Node3D
## Brilho em volta de um personagem, como o dos heróis de rank S (09-interface.md, seção 7: luz suave, nunca contorno duro): um halo radial
## que acompanha a câmera (aditivo, sem sombra nem borda) mais uma luz quente que pulsa de leve e ilumina o chão em volta.

const SHADER := """
shader_type spatial;
render_mode blend_add, unshaded, depth_draw_never, cull_disabled, shadows_disabled;
uniform vec4 color : source_color = vec4(1.0, 0.85, 0.5, 1.0);
uniform float strength = 1.0;
uniform float pulse_speed = 1.6;
void vertex() {
	// Sempre de frente para a câmera, mantendo o tamanho do quad.
	vec3 size = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0] * size.x, INV_VIEW_MATRIX[1] * size.y, INV_VIEW_MATRIX[2] * size.z, MODEL_MATRIX[3]);
}
void fragment() {
	float d = length(UV * 2.0 - 1.0);
	float halo = pow(clamp(1.0 - d, 0.0, 1.0), 2.2);
	float core = pow(clamp(1.0 - d * 1.6, 0.0, 1.0), 2.0) * 0.5;
	float pulse = 0.88 + 0.12 * sin(TIME * pulse_speed);
	ALBEDO = color.rgb * strength * pulse;
	ALPHA = clamp(halo * 0.75 + core, 0.0, 1.0);
}
"""

var _light: OmniLight3D
var _time := randf() * TAU


## Põe o brilho em `parent`: `center` é o ponto do corpo (m, a partir dos pés), `size` o diâmetro do halo.
static func attach(parent: Node3D, color: Color, center: float, size: float, strength := 1.0) -> AuraGlow:
	var glow := AuraGlow.new()
	glow.name = "AuraGlow"
	glow.position.y = center
	var quad := MeshInstance3D.new()
	var mesh := QuadMesh.new()
	mesh.size = Vector2(size, size)
	quad.mesh = mesh
	var shader := Shader.new()
	shader.code = SHADER
	var material := ShaderMaterial.new()
	material.shader = shader
	material.set_shader_parameter("color", color)
	material.set_shader_parameter("strength", strength)
	quad.material_override = material
	quad.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	glow.add_child(quad)
	glow._light = OmniLight3D.new()
	glow._light.light_color = color
	glow._light.omni_range = size * 0.9
	glow._light.light_energy = 0.9 * strength
	glow._light.shadow_enabled = false
	glow.add_child(glow._light)
	parent.add_child(glow)
	return glow


func _process(delta: float) -> void:
	_time += delta * 1.6
	_light.light_energy = (0.9 + 0.15 * sin(_time)) * 0.9
