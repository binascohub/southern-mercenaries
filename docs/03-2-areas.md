# Áreas dos mapas

> Versão 2 · 2026-10-30 · Divisão de cada mapa em áreas (como as fases do Dark Alliance 2). Complementa `03-inimigos.md` (monstros e chefes), `06-mundo-e-historia.md` (ordem da campanha) e `11-saves.md` (checkpoints).
> Números (tempo, níveis) são propostas para balancear depois.

## 1. Regras

- Cada um dos **10 mapas** é dividido em **4 ou 5 áreas** → **41 áreas** no total (+ 2 cidades).
- Cada área é uma **cena separada** no Godot (carrega rápido, menos coisas na memória — bom para vídeo integrado).
- **Duração:** 10 a 20 min por área → **10 a 13 horas** de campanha.
- **Checkpoint** na entrada de cada área (autosave, `11-saves.md`). A área do chefe sempre começa com checkpoint.
- **Passagem entre áreas:** porta, escada, túnel ou trilha no fim da área. No co-op, a passagem só acontece quando **todos os jogadores** estão perto da saída (ou o host confirma, com contagem de 10 s).
- **Volta à cidade:** pelo **Patuá de Retorno**, item vendido pelo **Macumbeiro** (`04-tortuga-e-missoes.md`, seção 5.1), ou pelos portais de retorno na entrada do mapa e depois de cada chefe. Para voltar ao mesmo checkpoint, o grupo paga ao Macumbeiro, que abre o portal para qualquer **ponto salvo**.
- **Tipo de espaço** (para o Cavaleiro): **aberto** (luta montado), **estreito** (desmonta) ou **misto**.
- **Segredos:** toda área tem ao menos 1 segredo (baú escondido, parede quebrável, passagem lateral) com loot extra.
- **Objetos quebráveis (decisão do autor):** barris, caixotes e sacos espalhados pelas áreas quebram com qualquer golpe. Ao quebrar, podem sair **poções de vida ou de recurso**, um pouco de ouro, raramente um valioso — ou **monstros** escondidos (ex.: ratos que saltam de um barril no Esgoto). Cada objeto quebra **uma vez por campanha** (não volta, como os monstros) e o que sai é sorteado uma vez; o loot segue a regra do loot individual (cada jogador presente vê o seu). Chances propostas (`data/loot.json`, `breakable`): nada 35%, ouro 25%, poção de vida 15%, poção de recurso 10%, monstros 10%, valioso 5%.
- **Exploração, sem ondas:** em cada área os monstros ficam em **grupos de encontro posicionados à mão**, dormindo até o jogador chegar perto; o mapa é **revelado conforme o jogador explora** (`03-inimigos.md`, "Encontros por exploração"; `09-interface.md`).
- **Elites:** 1 a 3 por área; a **penúltima área** de cada mapa tem um **mini-chefe** (elite forte com nome).
- **Nível das áreas** sobe aos poucos dentro do mapa (tabela de cada mapa). Nível máximo 20.

## 1.1. Mini-chefes: dois por mapa de combate

Cada mapa de combate tem **2 mini-chefes** (elites fortes com nome, categoria `miniboss`), incluindo o do mapa 1 (Esgoto) com o Gator Velho e o Rei dos Ratos:

| Mapa | Mini-chefes |
|---|---|
| Esgoto | Gator Velho (Passagem da Guerra) · **Rei dos Sapos** (altar no centro do Esgoto) |
| Floresta | Leshy · **Rainha das Víboras** |
| Ruínas | Guardião do Cofre · **Alfa da Matilha** |
| Cemitério | Ogro da Cripta (era o Escorpião; larga os **Pulmões Humanos**) · Senhor da Cripta (larga o **Coração Humano**) |
| Forte | Comandante (larga o **Crânio Antigo**) · **Rainha das Súcubos** |
| Mina | **Chefe Troll** · Guardião do Túmulo |

Em negrito, os criados nesta rodada (`tools/assets/add_minibosses.py`). A Floresta Sombria ainda não tem encontros.

## 2. Resumo

| # | Mapa | Ato | Sai de | Áreas | Níveis | Mini-chefe | Chefe |
|---|---|---|---|---|---|---|---|
| 1 | Esgoto de Tortuga | 2 | Tortuga | 4 | 1–2 | Jacaré Velho | Feiticeiro-Aranha |
| 2 | Ruínas do Reino do Arqueiro | 2 | Tortuga | 5 | 3–4 | Alfa da Matilha (Amarok) | Cérbero |
| 3 | Floresta Escura | 2 | Tortuga | 4 | 5–6 | Mapinguari Ancião | Leshy |
| 4 | Cavalos Míticos | 2 | Tortuga | 4 | 7–8 | Arion, o Veloz | Pégaso |
| 5 | Aves | 2 | Tortuga | 4 | 9–10 | Roca Anciã | Fênix |
| 6 | Deserto | 3 | Capital | 4 | 11–12 | Lamassu do Portão | Esfinge |
| 7 | Águas | 3 | Capital | 4 | 13–14 | Rainha das Iaras | Kraken |
| 8 | Pântano | 3 | Capital | 4 | 15–16 | Bunyip do Lago | Grendel e a Mãe |
| 9 | Serpentes | 3 | Capital | 4 | 17–18 | Hidra do Templo | Jörmungandr |
| 10 | Inferno | 4 | Capital | 4 | 19–20 | Ecos dos chefes | Lúcifer |
| | **Total** | | | **41** | | | |

## 3. Esgoto de Tortuga (`map_sewers`)

O Esgoto é **um mapa só, num andar só** (`sewers_01_drains`), grande: uma grade de **11 x 13 salas** de 8 m entre a sala de entrada e o túnel do Ninho. **Não há passagens para outros mapas** (os antigos Canais de Lixo, a Passagem Secreta da Guerra e o Covil do Feiticeiro viraram **setores** do mesmo andar, só com cartazes; a única saída é o portal de volta a Tortuga).

| Setor | Onde | Destaques |
|---|---|---|
| 1 · Bueiros da Rua Principal | linhas de cima | Entrada; tutorial de combate; Catador do Esgoto (Homem-Aranha) na sala de entrada |
| 2 · Canais de Lixo | meio, lado oeste | Praça oeste vazia; **altar do Rei dos Sapos no centro do mapa** (o Livro do Altar, entregue pelo Catador, o desperta: mini-chefe 1) |
| 3 · Galerias dos Morcegos | meio, lado leste | Posto do Caçador de Pragas; segredo com baú |
| 4 · Passagem Secreta da Guerra | embaixo, lado leste | Marcas do reino do Arqueiro nas paredes (o Arqueiro reconhece o brasão); **mini-chefe 2: o Gator Velho (Porco-Tubarão), na praça do canto inferior direito** |
| 5 · Câmaras dos Cogumelos | embaixo, lado oeste | Câmaras estreitas |
| Fundo | túnel e Ninho | **Feiticeiro-Aranha** (chefe); Tesouro Perdido da Guerra e o mapa para as Ruínas |

**Save point:** além do checkpoint da entrada, há um cristal de save **na frente da entrada da sala do altar** (o primeiro mini-chefe): chegar perto dele vira o checkpoint (autosave); se o grupo cair, volta ali (`save_point` em `arenas.json`).

Só os chefes do Esgoto revidam (o Rei dos Sapos, o Gator Velho e o Feiticeiro-Aranha); o resto é cenário (aranhas, ratos, morcegos voando, madeira na cor da mesa da Taverna).

## 4. Ruínas do Reino do Arqueiro (`map_ruins`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `ruins_01_snow_forest` | **Floresta Nevada** | Aberto | 3 | Chegada; Wargs em matilha; neve que mostra pegadas dos lobos |
| 2 | `ruins_02_burned_village` | **Vila Queimada** | Misto | 3 | Proposta: a **vila do Arqueiro** (cena de história se ele estiver no grupo); Lobisomens; Cadejos entre as casas |
| 3 | `ruins_03_battlefield` | **Campo de Batalha** | Aberto | 4 | Neblina, armaduras e covas; Cães Negros; noite deixa os lobos mais fortes; segredo: estandarte do reino |
| 4 | `ruins_04_capital_walls` | **Muralhas e Cidade Real** | Misto | 4 | Ruas da capital destruída; **mini-chefe: Alfa da Matilha** (Amarok elite) |
| 5 | `ruins_05_royal_crypt` | **Cripta Real** | Estreito → arena | 4 | Fenda do inferno sob o castelo; **Cérbero**; Cofre Real |

## 5. Floresta Escura (`map_forest`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `forest_01_edge` | **Orla da Mata** | Misto | 5 | A luz vai sumindo; bandos de Kodamas; tochas no caminho ensinam a mecânica da escuridão |
| 2 | `forest_02_web_hollow` | **Vale das Teias** | Estreito | 5 | Teias entre as árvores; Jorōgumos perto da **cachoeira escondida**; Dríades presas às árvores; segredo: atrás da cachoeira |
| 3 | `forest_03_lost_trails` | **Trilhas Perdidas** | Misto | 6 | Clareiras que se repetem (o Leshy faz o grupo andar em círculos — achar a árvore marcada para sair); Curupiras com pegadas falsas; **mini-chefe: Mapinguari Ancião** |
| 4 | `forest_04_elder_tree` | **Árvore Anciã** | Aberto (arena) | 6 | **Leshy**; ouro dos viajantes perdidos; Coroa de Galhos |

## 6. Cavalos Míticos (`map_horses`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `horses_01_plains` | **Planícies Selvagens** | Aberto | 7 | Ipotanes em bando; Mulas sem Cabeça em investida (ótimo para o Cavaleiro montado) |
| 2 | `horses_02_bone_field` | **Campo dos Ossos** | Aberto | 7 | Bakotsus que se remontam; Anggitays atirando de longe |
| 3 | `horses_03_cliff_ruins` | **Ruínas da Encosta** | Misto | 8 | Subida em trilhas; Cheollimas mergulhando; **mini-chefe: Arion, o Veloz** |
| 4 | `horses_04_sky_plateau` | **Planalto do Céu** | Aberto (arena) | 8 | **Pégaso**; Rédeas de Ouro do Céu |

## 7. Aves (`map_birds`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `birds_01_foothills` | **Sopé das Montanhas** | Aberto | 9 | Harpias e Corvos Sombrios |
| 2 | `birds_02_bronze_cliffs` | **Penhascos de Bronze** | Misto | 9 | Bandos de Aves Estinfálias; bordas de penhasco (quem é empurrado leva dano e volta ao ponto seguro) |
| 3 | `birds_03_strix_caves` | **Cavernas das Strix** | Estreito | 10 | Escuras; Strix que enxergam o Ninja invisível; **mini-chefe: Roca Anciã** na saída da caverna |
| 4 | `birds_04_ash_nest` | **Ninho de Cinzas** | Aberto (arena) | 10 | No pico; **Fênix**; Pena da Chama Eterna |

> Depois deste mapa, o Cavaleiro fala do Bobo da Corte e a **Capital Real** é liberada (`04-1-capital-real.md`).

## 8. Deserto (`map_desert`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `desert_01_caravan_road` | **Rota das Caravanas** | Aberto | 11 | Carroças abandonadas com o brasão do rei; Ghuls e hienas; primeira tempestade de areia |
| 2 | `desert_02_dunes` | **Mar de Dunas** | Aberto | 11 | Vermes da Morte sob a areia; Manticoras; areia movediça; o **oásis** (descanso e segredo) |
| 3 | `desert_03_buried_gate` | **Portão Soterrado** | Misto | 12 | Entrada do templo; Homens-Escorpião; **mini-chefe: Lamassu do Portão** |
| 4 | `desert_04_sphinx_hall` | **Salão da Esfinge** | Arena | 12 | **Esfinge** (fase do enigma); ouro das caravanas; Olho da Esfinge |

## 9. Águas (`map_waters`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `waters_01_coast` | **Costa dos Naufrágios** | Aberto | 13 | Afogados saindo dos cascos (alguns com farda da marinha do rei); Kappas na areia molhada |
| 2 | `waters_02_flooded_grottos` | **Grutas Alagadas** | Estreito | 13 | Água rasa (`soaked`); Kelpies em emboscada; Sereias curando monstros |
| 3 | `waters_03_ship_graveyard` | **Cemitério de Navios** | Misto | 14 | Pontes entre cascos; **mini-chefe: Rainha das Iaras**; segredo: baú com ouro do rei |
| 4 | `waters_04_sunken_deck` | **Convés Naufragado** | Arena | 14 | **Kraken**; Coração do Abismo + parte do ouro do rei |

## 10. Pântano (`map_swamp`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `swamp_01_bog_paths` | **Trilhas do Brejo** | Misto | 15 | Atoleiros; Fogos-fátuos na neblina levando para o caminho errado; Kikimoras |
| 2 | `swamp_02_barrows` | **Túmulos Afundados** | Estreito | 15 | Draugrs saindo dos túmulos na lama; segredo: túmulo com tesouro antigo |
| 3 | `swamp_03_black_shore` | **Margem do Lago Negro** | Misto | 16 | Rusalkas dançando na margem; a barcaça do rei afundada; **mini-chefe: Bunyip do Lago** |
| 4 | `swamp_04_grendel_hall` | **Salão em Ruínas** | Arena (margem + lago) | 16 | **Grendel e a Mãe de Grendel**; tesouro do lago + ouro do rei; Espada dos Gigantes |

## 11. Serpentes (`map_serpents`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `serpents_01_jungle` | **Selva das Serpes** | Aberto | 17 | Serpes (Wyverns) voando; Boitatás deixando rastro de fogo; Anfisbenas |
| 2 | `serpents_02_naga_temple` | **Templo das Nagas** | Estreito | 17 | Guardiões Naga; Basiliscos nos corredores (olhar petrificante) |
| 3 | `serpents_03_treasure_vault` | **Câmara do Ouro** | Misto | 18 | Mais ouro do rei; inscrições com o símbolo de Lúcifer; **mini-chefe: Hidra do Templo** no pátio |
| 4 | `serpents_04_sea_temple` | **Templo do Mar** | Arena | 18 | Templo meio afundado no mar; **Jörmungandr**; Escama do Mundo; **descoberta do portal para o Inferno** |

> De volta à Capital, o Bobo foi sequestrado. As relíquias abrem o portal para o Inferno (`06-mundo-e-historia.md`, Ato 4).

## 12. Inferno (`map_hell`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `hell_01_gates` | **Portões do Inferno** | Misto | 19 | Entrada aberta com as relíquias; Súcubos; rios de lava |
| 2 | `hell_02_gold_river` | **Rio de Ouro** | Aberto | 19 | Montanhas de ouro roubado do mundo, guardadas por Súcubos; o ouro **não pode ser pego** até o fim (proposta: brilha e some ao tocar) |
| 3 | `hell_03_echo_halls` | **Salões dos Ecos** | Misto | 20 | Ecos dos chefes derrotados (elites); a gaiola do Bobo é vista ao longe, sobre o trono |
| 4 | `hell_04_throne` | **Trono de Lúcifer** | Arena | 20 | **Lúcifer** (3 fases); **resgate do Bobo**; todo o ouro acumulado; fala final e gancho da continuação |

## 13. Decisões em aberto

- Divisão de 41 áreas: manter?
- "Mapa afora": **resolvido** — a viagem entre mapas é por portais (`04-tortuga-e-missoes.md`, seção 5); não há área extra de estrada.
- Preço do portal do Macumbeiro e do Patuá de Retorno: manter as propostas?
- No co-op, todos precisam estar na saída para passar de área, ou basta o host?
- A vila queimada das Ruínas é a vila do Arqueiro?
- Nomes dos mini-chefes.

## 14. Mapas implementados depois do Esgoto (primeira passada)

Ordem de expedição no jogo: **Tortuga → Floresta → Ruínas → Cemitério → Floresta Escura → Forte → Capital Real (Aurenhold)**. O portal do Forte para a Capital aparece depois de derrotar o Comandante; a Capital é cidade-base (sem monstros) e tem portal de volta a Tortuga. Os mapas saem de `tools/assets/build_maps.py` (sorteio com semente fixa) e ficam em `data/arenas.json`; cada um tem um portal para o próximo e outro de volta a Tortuga (entrada "Trilha para a Floresta", na ponta oeste da rua principal).

| # | id | Mapa | Cenário (pacote, licença) | Chefe (provisório) |
|---|---|---|---|---|
| 1 | `forest_01_path` | Floresta | Plantas Stylish Plants (CC0), obeliscos e pilares | Leshy |
| 2 | `ruins_01_city` | Ruínas da Cidade | Cena inteira de Destroyed Walls (CC BY 3.0) com colisor por parede | Guardião do Cofre |
| 3 | `cemetery_01_yard` | Cemitério | Medieval Props Textured (CC BY 3.0): lápides, cruzes, marcos de pedra; chão de terra acinzentada e escura; trilhas de lajes musgosas; grades pretas; mapa de salas e corredores no desenho de calabouço da referência do autor, ~17,6 mil m2, em 7 setores de um monstro cada (1 Campo de Covas: ratos de esgoto; 2 Terra dos Escorpiões: escorpiões venenosos; 3 Ossuário: esqueletos; 4 Cova dos Mortos: zumbis; 5 Alameda da Estátua: golens de pedra; 6 Catacumbas: morcegos; 7 Covil do Troll: trolls), corredores em anéis (mais de um caminho) e duas praças de ruínas a 171 m uma da outra com mini-chefe (Praça das Pedras: Escorpião da Cripta; Praça da Estátua: a estátua do lampião desperta o Guardião do Túmulo ao falar com ela) | Senhor da Cripta |
| 4 | `dark_forest_01_woods` | Floresta Escura | Mesma vegetação, mais densa e escura; **só o mapa** (sem monstros, chefe ou baús por enquanto) | — |
| 5 | `fort_01_gate` | Forte | 3D Dungeon Tileset (CC BY-SA 3.0), grade de 20 x 26 células de 2,5 m; paredes baixas (0,85 m) por causa da câmera | Comandante Amaldiçoado |

Os monstros comuns reaproveitam os modelos do Esgoto e do Monstro da Floresta; os chefes são provisórios até haver arte e mecânica próprias. As seções 4 e 5 acima (Ruínas do Reino do Arqueiro, Floresta Escura) continuam sendo o desenho final das áreas; este quadro é o que existe hoje.

### Docas (`docks_01_pier`) — ligada ao porto de Tortuga

Mapa de píeres de madeira sobre o mar (Modular Wooden Docks, CC0): pátio de entrada, píer principal, um cruzamento com dois píeres laterais e o píer do fundo, com barcos, defensas, barris e caixotes. A entrada fica no porto de Tortuga (a "Passagem para as Docas" ao lado do cais do navio pirata) e o portal "Voltar ao porto" leva de volta. Tem inimigos leves do esgoto (ratos, sapos, morcegos), dois baús e uma bolsa de moedas; ainda sem chefe, missões ou lojas.

