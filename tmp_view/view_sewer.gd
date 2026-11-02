extends Node
## Visualizador temporário: abre o Esgoto com um herói perto da anja (teclado/mouse normais do jogo). Apague a pasta tmp_view depois.
var _arena: Node
var _done := false
func _ready() -> void:
	SaveSystem.root = "user://view_saves"
	var hero := CharacterData.create("mage", "female", "Teste")
	hero.seal()
	Session.character = hero
	Session.campaign = SaveSystem.new_campaign()
	Session.campaign.area = OS.get_environment("VIEW_AREA") if OS.get_environment("VIEW_AREA") != "" else "sewers_01_drains"
	NetworkManager.prepare_solo()
	_arena = load("res://game/levels/prototype_arena.tscn").instantiate()
	add_child(_arena)
func _process(_d: float) -> void:
	if _done or _arena == null or _arena.local_player == null or not is_instance_valid(_arena.local_player):
		return
	var at := Vector2.ZERO
	if OS.get_environment("VIEW_AT") != "":
		var parts := OS.get_environment("VIEW_AT").split(",")
		at = Vector2(float(parts[0]), float(parts[1]))
	for prop: Dictionary in _arena.arena.get("props", []):
		if at == Vector2.ZERO and prop.get("id", "") == "sewer_scavenger":
			at = Vector2(prop.position[0], prop.position[1])
	if at == Vector2.ZERO:
		return
	_done = true
	_arena.local_player.teleport_to(Vector3(at.x + 0.0, 0.0, at.y + 5.0))
	print("VIEW: herói a 5 m da anja em ", at)
