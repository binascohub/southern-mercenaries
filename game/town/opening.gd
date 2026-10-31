# Southern Mercenaries — GPL-3.0-or-later
class_name Opening
extends RefCounted
## Abertura na Taverna (06-mundo-e-historia.md, seção 5), sem nós: quem chega à
## Taverna antes da primeira missão ouve cada herói contar a própria história.
## Primeiro os heróis dos jogadores (na ordem de chegada); os heróis que nenhum
## jogador escolheu entram como NPCs e convidam o grupo. No fim, o brinde e o
## velho bêbado chamando para o tesouro do esgoto. Dados em data/opening.json.

## Elenco: os heróis dos jogadores e, depois, os outros heróis como NPCs.
## players: [{name, class_id, sex}]. Cada um sai com "player" (true/false).
static func cast(players: Array) -> Array:
	var heroes := []
	var present: Array[String] = []
	for hero: Dictionary in players:
		heroes.append({"name": hero.name, "class_id": hero.class_id, "sex": hero.sex, "player": true})
		present.append(String(hero.class_id))
	for class_id: String in GameData.opening.order:
		if class_id in present:
			continue
		var sex: String = GameData.opening.npc_sex.get(class_id, "male")
		var name_key: String = GameData.get_class_data(class_id).hero_name_keys[sex]
		heroes.append({"name": str(TranslationServer.translate(name_key)), "class_id": class_id, "sex": sex, "player": false})
	return heroes


## História do herói (por classe_sexo quando a versão feminina é outra pessoa).
static func story_of(class_id: String, sex: String) -> Dictionary:
	var stories: Dictionary = GameData.opening.stories
	return stories.get("%s_%s" % [class_id, sex], stories.get(class_id, {}))


## Falas em ordem: [{speaker, key, args}]; speaker "" é a narração.
static func lines(players: Array) -> Array:
	var out := []
	for hero: Dictionary in cast(players):
		var story := story_of(hero.class_id, hero.sex)
		if story.is_empty():
			continue
		var args := {"name": hero.name}
		out.append({"speaker": "", "key": story.scene, "args": args})
		for key: String in story.lines:
			out.append({"speaker": hero.name, "key": key, "args": args})
		if not hero.player:
			out.append({"speaker": hero.name, "key": GameData.opening.npc_invite, "args": args})
	for key: String in GameData.opening.ending:
		out.append({"speaker": "", "key": key, "args": {}})
	return out
