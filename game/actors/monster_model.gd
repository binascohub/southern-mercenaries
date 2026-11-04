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
	# Mímico (chest_monster.glb do autor; tools/assets/build_chest_mimic.py): mímico com esqueleto e animações próprias (Idle, Run, Attack; sem acerto nem morte: o resto fica por código). ~2 m no arquivo.
	"chest_mimic": {"scene": "res://assets/models/monsters/chest_mimic.glb", "scale": 0.5,
		"anims": {"idle": "Idle", "walk": "Run", "run": "Run", "attack": "Attack"}},
	# Necromante (necromanser.rar do autor; tools/assets/build_necromancer.py): chefe do Esgoto no lugar do Feiticeiro-Aranha. Já vem com esqueleto e animações próprias (sem texturas: materiais
	# lisos pintados por peça). 2,2 m com o cajado; no tamanho 2,6 da Rainha com escala 0.55 -> ~3,1 m.
	"necromancer": {"scene": "res://assets/models/monsters/necromancer.glb", "scale": 0.55, "vertex_colors": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# Guerreiro Cogumelo (champ-warrior.glb do autor; tools/assets/build_champ_warrior.py): guerreiro-cogumelo de armadura e espada, 1,5 m no arquivo (ombro levado a 1,44 m
	# do esqueleto dos heróis, então 2,4 m no arquivo gerado), com os movimentos deles. Escala 0.6 e tamanho 1,1 -> ~1,6 m. Monstro do canto superior esquerdo do Esgoto.
	"champ_warrior": {"scene": "res://assets/models/monsters/champ_warrior.glb", "scale": 0.6,
		"anims": {"idle": "Idle", "walk": "Walk", "run": "Jog_Fwd", "attack": "Punch_Cross", "hit": "Hit_Chest", "die": "Death01"}},
	# Monstro Bárbaro (barbarian-monster.glb do autor; tools/assets/build_barbarian_monster.py): orc bárbaro com chifres, 2,04 m no arquivo, preso ao esqueleto dos heróis
	# com os movimentos deles (os clipes são os dos heróis, como o Godot os importa). No tamanho 1,2 -> ~2,3 m. Monstro do lado esquerdo do meio do Esgoto.
	"barbarian_monster": {"scene": "res://assets/models/monsters/barbarian_monster.glb", "scale": 0.94,
		"anims": {"idle": "Idle", "walk": "Walk", "run": "Jog_Fwd", "attack": "Punch_Cross", "hit": "Hit_Chest", "die": "Death01"}},
	# Mutante (Rigged, textured Mutant, thecubber, CC-BY-SA 3.0; tools/assets/build_mutant.py): humanoide de armadura, 1,8 m no arquivo, preso ao esqueleto dos heróis
	# com os movimentos deles. No tamanho 1,1 -> ~2 m. Monstro do Setor 5 do Esgoto (Câmaras dos Cogumelos, canto inferior esquerdo).
	"mutant": {"scene": "res://assets/models/monsters/mutant.glb", "scale": 1.0,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Troll Mauler (piacenti, CC BY 3.0; tools/assets/build_troll_mauler.py): bruto curvado de 3,1 m no arquivo, preso ao esqueleto dos heróis com os movimentos deles.
	# No tamanho 1,1 -> ~2,4 m. Monstro do Setor 1 do Esgoto.
	# Lince da Floresta (lynx-light.glb do autor, reduzido e animado por tools/assets/build_lynx.py): 0,96 m de comprimento no arquivo -> ~1,3 m com a escala 1,35.
	"lynx": {"scene": "res://assets/models/monsters/lynx.glb", "scale": 1.35,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "idle", "die": "idle"}},
	# Robôs da Mina (pixellabs-glb-3393.glb e pixellabs-glb-3347.glb do autor; esqueleto e animações de tools/assets/build_mine_robots.py): ~1 m no arquivo; o tamanho vem de "size".
	"mine_automaton": {"scene": "res://assets/models/monsters/mine_automaton.glb", "scale": 1.0,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "idle", "die": "idle"}},
	"mine_scout": {"scene": "res://assets/models/monsters/mine_scout.glb", "scale": 1.0,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "idle", "die": "idle"}},
	"troll_mauler": {"scene": "res://assets/models/monsters/troll_mauler.glb", "scale": 0.7,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Monstro de Tábuas (Monster_4, minib1.rar do autor; tools/assets/build_plank_monster.py): humanoide de carne com armadura de tábuas e pregos, 1,87 m no arquivo, preso ao
	# esqueleto dos heróis com os movimentos deles. Mini-chefe do Esgoto (o Rei dos Sapos, no tamanho 2,6 -> ~2,8 m).
	"plank_monster": {"scene": "res://assets/models/monsters/plank_monster.glb", "scale": 0.58,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	"rat": {"scene": "res://assets/models/monsters/rat.glb", "scale": 1.35,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# A Rainha: corpo humano (o dos heróis, com as animações deles) e cabeça de rato.
	# Corpo: a Dark Elf (danimal, CC BY-SA 3.0) sem a cabeça (tools/assets/behead.py),
	# com as animações dela; 7,09 unidades de altura -> 1,8 (body_scale).
	"queen": {"scene": "res://assets/models/monsters/rat_head.glb", "humanoid": true, "scale": 0.6,
		"body_scene": "res://assets/models/monsters/rat_queen_body.glb", "body_scale": 0.254,
		"bones": {"head": "Head", "chest": "Spine1", "hips": "Hips"},
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "die": "die"}},
	# O Feiticeiro-aranha (Wizard, piacenti, CC BY-SA 3.0): malha única sem esqueleto, 1 m de altura no
	# arquivo; o corpo todo balança, avança e cai por código (`static`). Chefe do Esgoto no lugar da Rainha.
	# Anglerman (Angler Man 3D, piacenti, CC BY 3.0): peixe-pescador de pernas finas das Docas; malha única, movida por código.
	"angler": {"scene": "res://assets/models/monsters/angler.glb", "scale": 0.75, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	"demon": {"scene": "res://assets/models/monsters/demon_wizard.glb", "scale": 0.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Sapo (Frog Guy, CC0): malha única de pé sem animação (tools/assets/build_frog.py); balança, avança e cai
	# por código (`static`); 1 m no arquivo. Toma o lugar dos ratos do Esgoto (os ratos viraram cenário).
	"frog": {"scene": "res://assets/models/monsters/frog.glb", "scale": 0.4, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# Tio Fungo (Uncle Fungus, piacenti, CC BY-SA 3.0; tools/assets/build_fungus.py): fera de fungo sem esqueleto
	# nem animação (`static`); 1 m no arquivo -> ~2,2 m no tamanho 1.
	"fungus": {"scene": "res://assets/models/monsters/fungus.glb", "scale": 1.1, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# Espreitador (Stalker 3D, GuieA_7, CC BY-SA 4.0; tools/assets/build_stalker.py): olho alado da Mina, malha única sem animação
	# (`static`); 1 m no arquivo -> ~1,4 m no tamanho 1. Voa e balança por código.
	"stalker": {"scene": "res://assets/models/monsters/stalker.glb", "scale": 1.4, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# Demônio do mini-chefe (a malha do Demônio Doze + as texturas PBR de demon_tex.rar, as de "ferido": cinza com sangue; tools/assets/build_demon_boss.py): malha única `static`,
	# 2,2 m no arquivo -> ~3,6 m no tamanho 1,8. O Gator Velho, mini-chefe do Esgoto, no lugar do Porco-Tubarão.
	"demon_boss": {"scene": "res://assets/models/monsters/demon_boss_rigged.glb", "scale": 1.0,
		"anims": {"idle": "Idle", "walk": "Walk", "run": "Jog_Fwd", "attack": "Punch_Cross", "hit": "Hit_Chest", "die": "Death01"}},
	# (O Gator Velho agora é o Carniceiro Chifrudo: a malha do Demônio Doze presa ao esqueleto dos heróis por tools/assets/build_demon_biped.py, com os movimentos deles; o demon_boss.glb estático ficou como origem.)
	# Demônio Doze (demon-twelve.glb do autor; tools/assets/build_demon_twelve.py): malha única sem esqueleto nem animação (`static`), 2,2 m de altura no arquivo
	# -> ~2,2 m no tamanho 1,1. Balança, avança e cai por código. Monstro do meio do lado direito do Esgoto.
	"demon_twelve": {"scene": "res://assets/models/monsters/demon_twelve.glb", "scale": 0.9, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# Espírito Sombrio (shadow-spirit.glb do autor; tools/assets/build_shadow_spirit.py): malha única sem esqueleto nem animação (`static`), 2,5 m de altura no arquivo
	# -> ~2 m no tamanho 1. Flutua e balança por código. Monstro do canto superior direito do Esgoto.
	"shadow_spirit": {"scene": "res://assets/models/monsters/shadow_spirit.glb", "scale": 0.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# Porco-Tubarão (pork-shark.blend, do autor; tools/assets/build_pork_shark.py): criatura de pé com esqueleto e 17 animações, 5,55 unidades de altura
	# (pés em 0) -> ~1,5 m por unidade de size. O Gator Velho, mini-chefe do Esgoto, no lugar do jacaré.
	"pork_shark": {"scene": "res://assets/models/monsters/pork_shark.glb", "scale": 0.27,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
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
	# Coelho (Rabbit, cdmir, CC0): o Coelho Dourado que solta moedas (tingido de ouro no jogo); ~15 unidades -> ~0,75 m no tamanho 1.
	# Só tem idle, pulo, corrida e sentado: o pulo faz de andar e de ataque, e a sentada faz de queda.
	"rabbit": {"scene": "res://assets/models/characters/rabbit.glb", "scale": 0.05,
		"anims": {"idle": "idle", "walk": "jump", "run": "run", "attack": "jump", "hit": "sit", "die": "sit"}},
	# Dragãozinho (Baby Dragon, grab3d, CC0): malha única dourada sem esqueleto (`static`); 0,55 m no arquivo -> ~0,9 m
	# no tamanho 1. Corre aos pulos (`hop` multiplica a altura do salto do `_animate_static`). Substituiu o Coelho Dourado.
	"baby_dragon": {"scene": "res://assets/models/monsters/baby_dragon.glb", "scale": 1.6, "static": true, "hop": 8.0,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Lagarto Dourado (Lizardman, skorpio, CC BY-SA 3.0): tingido de ouro no jogo (agora só o Guardião do Cofre usa este corpo).
	"lizard": {"scene": "res://assets/models/monsters/golden_lizard.glb", "scale": 0.8,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "die": "die"}},
	# Elfo Sombrio (Dark Elf, danimal, CC BY-SA 3.0; besta de Lamoot, CC BY): o corpo inteiro com chifres, cabelo e a besta,
	# 8,1 unidades de altura -> ~1,8 m no tamanho 1. Atira de longe (animação "attack" = o tiro).
	"dark_elf": {"scene": "res://assets/models/monsters/dark_elf.glb", "scale": 0.22,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "die": "die"}},
	# Esqueleto (Skeleton with rig, rudy85, CC0): humanoide de 1,8 m no tamanho 1, com animações feitas à mão
	# (tools/assets/build_skeleton.py). Morto-vivo comum do Cemitério.
	"skeleton": {"scene": "res://assets/models/monsters/skeleton.glb", "scale": 1.0,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Súcubo (Goth Female "Fleur du Mal", tizeta, CC BY 3.0): corpo único em pose de repouso, sem animações
	# (o Blender o traz com esqueleto, mas sem ações): flutua e inclina por código (`static`); 44,8 unidades de
	# altura no arquivo (`unit`) -> ~1,8 m no tamanho 1. Ataque de magia à distância.
	# Demônio da Noite (Night Demon, nubux / morgan strauss, CC BY 3.0): corpo único sem animações (o pacote só tem a malha;
	# braços baixados por tools/assets/build_night_demon.py): balança, avança e cai por código (`static`); 1 m no arquivo -> ~1,8 m no tamanho 1.
	# Ogro (Ogre lowpoly, nubux / rudy85, CC BY 3.0): malha única sem esqueleto, braços baixados por tools/assets/build_ogre.py; balança,
	# avança e cai por código (`static`); 1 m no arquivo -> ~1,8 m no tamanho 1. Mini-chefe do Cemitério (o Ogro da Cripta).
	"ogre": {"scene": "res://assets/models/monsters/ogre.glb", "scale": 1.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	"night_demon": {"scene": "res://assets/models/monsters/night_demon.glb", "scale": 1.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	"succubus": {"scene": "res://assets/models/monsters/succubus.glb", "scale": 0.04, "static": true, "unit": 44.8,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Senhor da Cripta (Undead male, TiZeta, CC BY): nobre morto-vivo de casaco roxo, 1,8 m no tamanho 1, com animações
	# feitas à mão (tools/assets/build_undead.py). Chefe do Cemitério.
	# Asas pretas de morcego nas costas (osso "schiena"): feitas em código, como as da Rainha dos Ratos.
	"undead": {"scene": "res://assets/models/monsters/undead_lord.glb", "scale": 1.0, "wings": "schiena",
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Zumbi Magro (Thin Zombie, Rosswet Mobile, CC BY 3.0): humanoide com animações próprias (andar, correr, atacar,
	# apanhar, morrer). Morto-vivo comum do Cemitério.
	"zombie": {"scene": "res://assets/models/monsters/zombie.glb", "scale": 0.9,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Troll Magro (Skinny Troll, piacenti, CC BY 3.0): troll de 2,4 m com clava de espinhos na mão esquerda e saia de
	# couro com caveiras; animações feitas à mão (tools/assets/build_troll.py). Elite do Cemitério.
	"troll": {"scene": "res://assets/models/monsters/troll.glb", "scale": 1.0,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Goblin (Goblin, CDmir, CC0): pequeno e ágil, ~12 unidades de altura no arquivo -> ~1,2 m no tamanho 1;
	# animações do arquivo (idle, walk, run, attack, hit, die; tools/assets/build_monsters.py). Bando das Ruínas.
	"goblin": {"scene": "res://assets/models/monsters/goblin.glb", "scale": 0.1,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Sapo Ácido (Triton, guiea7, CC BY-SA 4.0): sapo-homem pintado, 8,2 unidades
	# de altura -> ~1,3 m no tamanho do sapo; tingido de verde pelos dados.
	"toad": {"scene": "res://assets/models/monsters/toad.glb", "scale": 0.187,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "die": "die"}},
	# Golens da Floresta (umask007, CC BY 3.0 / CC BY-SA 3.0; tools/assets/build_golems.sh): 2,3 m de largura no arquivo, "size" 1.6 nos dados.
	# O "hit" é o flinch; o modelo é o mesmo nas três variantes, só a textura muda (fogo, gelo, pedra).
	"golem_fire": {"scene": "res://assets/models/monsters/golem_fire.glb", "scale": 0.62,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"golem_ice": {"scene": "res://assets/models/monsters/golem_ice.glb", "scale": 0.62,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"golem_stone": {"scene": "res://assets/models/monsters/golem_stone.glb", "scale": 0.62,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# Réptil da Floresta (thecubber, CC BY-SA 3.0; tools/assets/build_reptile.sh): ~1,6 m de altura curvado, de garras; animações feitas para o jogo.
	"reptile": {"scene": "res://assets/models/monsters/reptile.glb", "scale": 1.0,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# Besta Quitinosa (Beast 02, Atmostatic, CC BY 3.0 / CC BY-SA 3.0; tools/assets/build_beast.py): malha única sem esqueleto, 1 m de comprimento
	# no arquivo (1,4 m de altura); o corpo todo balança, avança, investe e tomba (de barriga para cima) por código (`static`).
	"chitin_beast": {"scene": "res://assets/models/monsters/chitin_beast.glb", "scale": 1.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Rei Golem de Pedra (stone-golem.glb; tools/assets/build_stone_golem_king.py): malha única sem esqueleto, 1 m de altura no arquivo
	# (o "size" dos dados dá a altura); o corpo todo balança, avança, investe e tomba por código (`static`).
	"golem_king": {"scene": "res://assets/models/monsters/golem_king.glb", "scale": 1.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "run", "attack": "attack", "hit": "hit", "die": "die"}},
	# Troll da Floresta (troll.glb do autor; tools/assets/build_forest_troll.py): malha parada de 2,3 m na pose do arquivo, sem animação.
	"forest_troll": {"scene": "res://assets/models/monsters/forest_troll.glb", "scale": 1.0, "static": true, "anims": {}},
	# Cervos da Floresta (CDmir e TinyWorlds, CC0; tools/assets/build_deer.sh): 1,6 m de comprimento no arquivo, "size" 1.4 nos dados.
	"deer_buck": {"scene": "res://assets/models/monsters/deer_buck.glb", "scale": 0.714,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "die": "die"}},
	"deer_doe": {"scene": "res://assets/models/monsters/deer_doe.glb", "scale": 0.714,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "die": "die"}},
	# Monstros baixados do OpenGameArt (CC0; tools/assets/build_oga_monsters.py): malha única parada de 1 m na maior dimensão, movida por código (`static`); `scale` = metros no tamanho 1.
	"alien_bug": {"scene": "res://assets/models/monsters/alien_bug.glb", "scale": 1.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"cactus": {"scene": "res://assets/models/monsters/cactus.glb", "scale": 1.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"cobra": {"scene": "res://assets/models/monsters/cobra.glb", "scale": 1.2, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"crab": {"scene": "res://assets/models/monsters/crab.glb", "scale": 1.2, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"crawlmaster": {"scene": "res://assets/models/monsters/crawlmaster.glb", "scale": 1.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"darsh": {"scene": "res://assets/models/monsters/darsh.glb", "scale": 2.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"earth_dragon": {"scene": "res://assets/models/monsters/earth_dragon.glb", "scale": 2.2, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"exp_demon": {"scene": "res://assets/models/monsters/exp_demon.glb", "scale": 1.5, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"fatty": {"scene": "res://assets/models/monsters/fatty.glb", "scale": 2.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"ghost_wing": {"scene": "res://assets/models/monsters/ghost_wing.glb", "scale": 1.2, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"glutton": {"scene": "res://assets/models/monsters/glutton.glb", "scale": 2.3, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"golem_block": {"scene": "res://assets/models/monsters/golem_block.glb", "scale": 2.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"hazmat": {"scene": "res://assets/models/monsters/hazmat.glb", "scale": 1.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"horror": {"scene": "res://assets/models/monsters/horror.glb", "scale": 1.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"lava_golem": {"scene": "res://assets/models/monsters/lava_golem.glb", "scale": 2.3, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"mushroom_cap": {"scene": "res://assets/models/monsters/mushroom_cap.glb", "scale": 1.1, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"mutant_grunt": {"scene": "res://assets/models/monsters/mutant_grunt.glb", "scale": 2.2, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"octaminator": {"scene": "res://assets/models/monsters/octaminator.glb", "scale": 2.2, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"raven": {"scene": "res://assets/models/monsters/raven.glb", "scale": 1.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"sonask": {"scene": "res://assets/models/monsters/sonask.glb", "scale": 2.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"spider_big": {"scene": "res://assets/models/monsters/spider_big.glb", "scale": 1.6, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"tentacleye": {"scene": "res://assets/models/monsters/tentacleye.glb", "scale": 1.8, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	"werewolf": {"scene": "res://assets/models/monsters/werewolf.glb", "scale": 2.0, "static": true,
		"anims": {"idle": "idle", "walk": "walk", "run": "walk", "attack": "attack", "hit": "hit", "die": "die"}},
	# O morcego guarda o tamanho original do arquivo (envergadura ~10 unidades).
	"bat": {"scene": "res://assets/models/monsters/bat.glb", "scale": 0.16, "bat_wings": true,
		"anims": {"idle": "fly", "walk": "fly", "run": "fly", "attack": "fly", "die": "die"}},
}
## Animações que não repetem.
const ONCE := ["attack", "hit", "die"]
const BLEND := 0.15
## Inclinação da tampa do Mímico (rad): aberta e fechada (a do arquivo fica entre -0,7 e -0,5 parado; o golpe vai de -1,3 a -0,3).
const CHOMP_OPEN := -1.25
const CHOMP_CLOSED := -0.25

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
## Sem rosa (decisão do autor): cauda e detalhes na cor escura da pelagem.
const QUEEN_PINK := Color(0.24, 0.2, 0.18)
const QUEEN_WING := Color(0.42, 0.27, 0.19)
var _wing_color := WING_COLOR
## Asas levantadas (radianos para cima, além da batida).
var _wing_raise := 0.0
var _tail: Node3D
## Peças animadas à mão (escorpião): nome -> [nó, transformação de repouso].
var _parts := {}
var _action_time := 0.0
## Modelo sem esqueleto (o Feiticeiro-aranha): o corpo todo é movido por código.
var _static_root: Node3D
## Altura do modelo sem esqueleto, nas unidades do arquivo: os deslocamentos do `_animate_static` valem para 1 m.
var _static_unit := 1.0


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
	if info.get("bat_wings", false):
		BatWings.attach(model as Node3D)  # vira o morcego para a frente e bate as asas (a animação do arquivo não mexe nelas)
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
			copy.vertex_color_use_as_albedo = bool(info.get("vertex_colors", false))  # modelo pintado por cor de vértice (o Necromante)
			# Os modelos antigos têm faces viradas para dentro (o morcego visto de cima).
			copy.cull_mode = BaseMaterial3D.CULL_DISABLED
			mesh.set_surface_override_material(i, copy)
			_materials.append(copy)
	if info.get("static", false):
		for key: String in info.anims:
			_names[key] = info.anims[key]
		_static_root = model as Node3D
		_static_unit = float(info.get("unit", 1.0))
		_current = "idle"
		return true
	if info.get("procedural", false):
		for key: String in info.anims:
			_names[key] = info.anims[key]
		for node in model.find_children("*", "Node3D", true, false):
			var part := node as Node3D
			if String(part.name).begins_with("Leg_") or String(part.name).begins_with("Claw_") or String(part.name) == "Body":
				_parts[String(part.name)] = [part, part.transform]
		_current = "idle"
		return true
	if info.has("wings"):
		_add_back_wings(model, String(info.wings))
	_anim = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if _anim:
		for key: String in info.anims:
			var wanted: String = info.anims[key]
			if _anim.has_animation(wanted):
				_names[key] = wanted
				_anim.get_animation(wanted).loop_mode = Animation.LOOP_NONE if key in ONCE and wanted != "fly" \
					else Animation.LOOP_LINEAR
		if look == "chest_mimic":
			_chomp(model)
		play("idle", 0.0)
	return true


## Mímico: a tampa ("top_6") abre e fecha a boca o tempo todo (devagar parado, rápido correndo). A animação do arquivo quase não a mexe fora do golpe;
## aqui as chaves da tampa em Idle e Run são trocadas por uma mordida que abre e fecha, sem mexer nas da língua.
func _chomp(model: Node) -> void:
	var skeleton := model.find_child("Skeleton3D", true, false) as Skeleton3D
	if skeleton == null or _anim == null:
		return
	var skeleton_path := _anim.get_node(_anim.root_node).get_path_to(skeleton)
	var track_path := NodePath("%s:top_6" % skeleton_path)
	for entry: Array in [["Idle", 1.4], ["Run", 0.45]]:
		if not _anim.has_animation(entry[0]):
			continue
		var animation := _anim.get_animation(entry[0])
		var track := -1
		for t in animation.get_track_count():
			if animation.track_get_type(t) == Animation.TYPE_ROTATION_3D and animation.track_get_path(t) == track_path:
				track = t
				break
		if track < 0:
			continue
		var rest := Quaternion(animation.track_get_key_value(track, 0)).get_euler()
		var steps := maxi(roundi(animation.length / float(entry[1])), 1) * 2
		while animation.track_get_key_count(track) > 0:
			animation.track_remove_key(track, 0)
		for k in steps + 1:
			var open := k % 2 == 0
			var pitch := CHOMP_OPEN if open else CHOMP_CLOSED
			animation.rotation_track_insert_key(track, animation.length * k / steps, Quaternion.from_euler(Vector3(pitch, rest.y, rest.z)))


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
	_fur_skin(head)  # as orelhas são as da própria cabeça de rato
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


## Asas pretas de morcego nas costas de um modelo com esqueleto (o Senhor da Cripta): acompanham o osso `bone`, brotam
## ao surgir e batem devagar parado, mais rápido correndo e no golpe (o mesmo código da Rainha); somem quando ele morre.
## Em unidades do modelo (1,8 m, a frente é +Z).
func _add_back_wings(model: Node3D, bone: String) -> void:
	_skeleton = model.find_child("Skeleton3D", true, false) as Skeleton3D
	var back := Node3D.new()
	add_child(back)
	if _skeleton and _skeleton.find_bone(bone) >= 0:
		_follow_bone(back, bone, Transform3D(Basis(), _rest_in_model(bone).origin + Vector3(0, 0.05, -0.1)))
	else:
		back.position = Vector3(0, 1.4, -0.1)
	_wing_color = Color(0.03, 0.03, 0.035)
	_wing_size = 1.35
	_wing_raise = 0.3
	_add_wings(back, Vector3(0.07, 0, 0))
	show_wings(true)


func _process(delta: float) -> void:
	if _static_root:
		_animate_static(delta)
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


## Feiticeiro-aranha: flutua e balança parado, anda inclinado para a frente, investe no golpe e tomba na morte.
func _animate_static(delta: float) -> void:
	_time += delta
	_action_time += delta
	var lift := sin(_time * 1.6) * 0.015
	var pitch := 0.0
	var roll := sin(_time * 0.9) * 0.02
	if _current in ["walk", "run"]:
		var rate := 9.0 if _current == "run" else 6.0
		lift = absf(sin(_time * rate)) * 0.04 * float(FAMILIES[family].get("hop", 1.0))
		pitch = 0.12
		roll = sin(_time * rate * 0.5) * 0.07
	elif _current == "attack":
		var swing := sin(minf(_action_time / 0.7, 1.0) * PI)
		pitch = 0.55 * swing
		lift = 0.05 * swing
	elif _current == "hit":
		pitch = -0.15 * sin(minf(_action_time / 0.3, 1.0) * PI)
	elif _current == "die":
		var fall := minf(_action_time / 0.9, 1.0)
		pitch = -1.45 * ease(fall, 2.0)
	_static_root.position.y = lift * _static_unit
	_static_root.rotation = Vector3(pitch, 0.0, roll)


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
	if not _parts.is_empty() or _static_root:
		_current = key
		_action_time = 0.0
		return
	if _anim == null:
		return
	_current = key
	_anim.play(_names[key], blend)
	if key == "die" and _skeleton and not _wings.is_empty():
		show_wings(false)      # asas pretas do Senhor da Cripta: somem com a morte


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
