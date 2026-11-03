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

Cada mapa de combate tem **2 mini-chefes** (elites fortes com nome, categoria `miniboss`), incluindo o do mapa 1 (Esgoto) com o Carniceiro Chifrudo e o Rei dos Ratos:

| Mapa | Mini-chefes |
|---|---|
| Esgoto | **Carniceiro Chifrudo** (demônio açougueiro; o Azazel entrega o Grimório das Brasas, que o invoca no altar do centro; solta a Garrafa das Almas Condenadas) · **Empalado** (altar no centro do Esgoto; quest "As Almas Pregadas", da Ossael) |
| Floresta | Rei Golem de Pedra (templo do leste; larga a **Adaga de Osso**) · Golem de Fogo (pira; larga a **Caveira de Morvak**) · Leshy é o chefe do mapa |
| Ruínas | **Guardião das Ruínas** (golem de pedra; a estátua do cavaleiro o desperta; larga o **Coração de Pedra**) · **Campeão Caído** (a Sacerdotisa o desperta; larga o **Estandarte do Campeão**) · **Alfa da Matilha** (anda solto; larga a carne para o Bobo da Corte) |
| Cemitério | Ogro da Cripta (era o Escorpião; larga os **Pulmões Humanos**) · Senhor da Cripta (larga o **Coração Humano**) |
| Forte | **Senhor Elfo Sombrio** (o Exilado o desperta; larga a **Lâmina do Senhor Elfo**) · **Rainha das Súcubos** (a Penitente a desperta; larga o **Anel da Rainha**) · **Comandante** (anda solto; larga o **Crânio Antigo**) |
| Catacumbas | **Carrasco das Catacumbas** (a gaiola do Poço o desperta com a missão do Carcereiro Cego; larga o **Machado do Carrasco**) · **Alma Acorrentada** (a Prisioneira a desperta; larga o **Grilhão da Alma**) |
| Mina | **Chefe Troll** (a carroça abandonada o desperta com a missão do Capataz; larga a **Presa**) · **Besta de Quartzo** (o Cristal Pulsante a desperta com a missão do Joalheiro; larga o **Núcleo de Quartzo**) · **Guardião do Túmulo** (anda solto no labirinto; larga a **Alma Real** do Padre) |
| Bunker | **Armadura Viva** (o rack de armas do Arsenal a desperta com a missão do Intendente; larga o **Selo do Arsenal**) · **Comandante Podre** (o catre do Alojamento o desperta com a missão da Médica; larga a **Medalha de Guerra**) |
| Floresta Escura | **Víbora Anciã** (o Totem das Serpentes a desperta com a missão da Herbalista; larga a **Presa**) · **Rei dos Esporos** (o Cogumelo Ancestral o desperta com a missão do Encantador; larga a **Coroa de Esporos**) |

Em negrito, os criados nesta rodada (`tools/assets/add_minibosses.py`). A Floresta Sombria ainda não tem encontros.

## 2. Resumo

Ordem dos mapas, por hub (`tools/assets/set_map_order.py` liga os portais; cada mapa volta ao seu hub, sem portais em cadeia entre mapas):

| # | Mapa | Hub | Mini-chefes | Chefe |
|---|---|---|---|---|
| 1 | Esgoto de Tortuga (`sewers_01_drains`) | Tortuga | Carniceiro Chifrudo · Rei dos Sapos | Feiticeiro-Aranha |
| 2 | Floresta (`forest_01_path`, o mapa do Leshy) | Tortuga | Rei Golem de Pedra · Golem de Fogo | Leshy |
| 3 | Docas (`docks_01_pier`) | Tortuga | — | — |
| 4 | Ruínas do Reino do Arqueiro (`ruins_01_city`) | Tortuga | Guardião das Ruínas · Campeão Caído (+ Alfa da Matilha solto) | Rei Caído |
| 5 | Cemitério (`cemetery_01_yard`) | Capital | Ogro da Cripta · Senhor da Cripta | — |
| 6 | Forte (`fort_01_gate`) | Capital | Senhor Elfo Sombrio · Rainha das Súcubos (+ Comandante solto) | Barão Infernal |
| 7 | Catacumbas (`catacombs_01_depths`) | Capital | Carrasco das Catacumbas · Alma Acorrentada | Rei Acorrentado |
| 8 | Deserto (`desert_01_canyon`) | Capital | Lamassu da Areia · Rainha Escorpião | Esfinge |
| 9 | Mina (`mine_01_crystal_vein`) | Fazenda | Chefe Troll · Besta de Quartzo (+ Guardião do Túmulo solto) | Golem de Cristal |
| 10 | Bunker (`bunker_01_entrance`) | Fazenda | Armadura Viva · Comandante Podre | General Ferrugem |
| 11 | Floresta Escura (`dark_forest_01_woods`) | Fazenda | Víbora Anciã · Rei dos Esporos | Ancião Sombrio |

A Capital e a Fazenda são acessadas por Tortuga (`capital_gate`, `farm_gate`). Pântano e Inferno (seções abaixo) continuam só no documento, fora desta ordem.

## 3. Esgoto de Tortuga (`map_sewers`)

O Esgoto é **um mapa só, num andar só** (`sewers_01_drains`), grande: uma grade de **11 x 13 salas** de 12 m entre a sala de entrada e o túnel do Ninho. **Não há passagens para outros mapas** (os antigos Canais de Lixo, a Passagem Secreta da Guerra e o Covil do Feiticeiro viraram **setores** do mesmo andar, só com cartazes; a única saída é o portal de volta a Tortuga).

| Setor | Onde | Destaques |
|---|---|---|
| 1 · Bueiros da Rua Principal | linhas de cima | Entrada; tutorial de combate; Catador do Esgoto (Homem-Aranha) na sala de entrada |
| 2 · Canais de Lixo | meio, lado oeste | Praça oeste vazia; **altar do Rei dos Sapos no centro do mapa** (o Livro do Altar, entregue pelo Catador, o desperta: mini-chefe 1) |
| 3 · Galerias dos Morcegos | meio, lado leste | Posto do Caçador de Pragas; segredo com baú |
| 4 · Passagem Secreta da Guerra | embaixo, lado leste | Marcas do reino do Arqueiro nas paredes (o Arqueiro reconhece o brasão); **mini-chefe 2: o Carniceiro Chifrudo, invocado no altar do centro do mapa com o Grimório das Brasas do Azazel (quest "A Garrafa das Almas Condenadas": ele solta a garrafa; o Azazel a troca pela chave de espadas)** |
| 5 · Câmaras dos Cogumelos | embaixo, lado oeste | Câmaras estreitas |
| Fundo | túnel e Ninho | **Feiticeiro-Aranha** (chefe); Tesouro Perdido da Guerra e o mapa para as Ruínas |

**Save point:** além do checkpoint da entrada, há um cristal de save **na frente da entrada da sala do altar** (o primeiro mini-chefe): chegar perto dele vira o checkpoint (autosave); se o grupo cair, volta ali (`save_point` em `arenas.json`).

Só os chefes do Esgoto revidam (o Rei dos Sapos, o Carniceiro Chifrudo e o Feiticeiro-Aranha); o resto é cenário (aranhas, ratos, morcegos voando, madeira na cor da mesa da Taverna).

## 4. Ruínas do Reino do Arqueiro (`map_ruins`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `ruins_01_snow_forest` | **Floresta Nevada** | Aberto | 3 | Chegada; Wargs em matilha; neve que mostra pegadas dos lobos |
| 2 | `ruins_02_burned_village` | **Vila Queimada** | Misto | 3 | Proposta: a **vila do Arqueiro** (cena de história se ele estiver no grupo); Lobisomens; Cadejos entre as casas |
| 3 | `ruins_03_battlefield` | **Campo de Batalha** | Aberto | 4 | Neblina, armaduras e covas; Cães Negros; noite deixa os lobos mais fortes; segredo: estandarte do reino |
| 4 | `ruins_04_capital_walls` | **Muralhas e Cidade Real** | Misto | 4 | Ruas da capital destruída; **mini-chefe: Alfa da Matilha** (Amarok elite) |
| 5 | `ruins_05_royal_crypt` | **Cripta Real** | Estreito → arena | 4 | Fenda do inferno sob o castelo; **Cérbero**; Cofre Real |

### A história da Floresta no jogo (`forest_01_path`)

1. **Taberneira** (depois de vencer o Esgoto): "viajantes e caçadores entram na floresta e não voltam"; ouro nas raízes da árvore anciã, guardado pelo Leshy (Terra, fraco a Fogo). Aceitar a missão **O Ouro dos Viajantes Perdidos** libera a trilha da Floresta em Tortuga e pede a **Costela de Adão** (a primeira costela, que Lúcifer mandou esconder nas raízes da árvore anciã), que o Leshy larga.
2. **Guardião do Portão** (réptil da floresta, diante do portão de dois arcos no corredor `c4`): explica que o portão do covil do Leshy só cai com **duas chaves**, que estão com as elfas. Missão **O Portão do Leshy**: entregar a Chave de Espadas e a Chave de Copas; o portão afunda e a passagem fica aberta.
3. **Exploradora**: procura a adaga de osso de dinossauro para a coleção de raridades. A adaga fica no peito do **Rei Golem de Pedra**, mini-chefe do templo em ruínas (tocar o templo, com esta missão ativa, desperta o Rei e o Guardião do Túmulo). Entregando a adaga, ela dá a **Chave de Espadas**.
4. **Aelindra, a Guardiã da Pira**: a caveira do caçador Morvak, amaldiçoado, queima na pira e ameaça as árvores. O **Golem de Fogo** (mini-chefe) a guarda; entregando a **Caveira de Morvak** ela purifica a pira e dá a **Chave de Copas**.
5. **Leshy** (chefe do mapa, atrás do portão): ao morrer deixa o **baú épico** (tabela `treasure_forest`: o ouro dos viajantes perdidos, itens e a relíquia **Coroa de Galhos**) e a **Costela de Adão**; levando a costela à Taberneira (o botão de descansar vira "Descansar / entregar o item"), ela paga 350 de ouro e 700 de XP.

## 5. Floresta Escura (`map_forest`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `forest_01_edge` | **Orla da Mata** | Misto | 5 | A luz vai sumindo; bandos de Kodamas; tochas no caminho ensinam a mecânica da escuridão |
| 2 | `forest_02_web_hollow` | **Vale das Teias** | Estreito | 5 | Teias entre as árvores; Jorōgumos perto da **cachoeira escondida**; Dríades presas às árvores; segredo: atrás da cachoeira |
| 3 | `forest_03_lost_trails` | **Trilhas Perdidas** | Misto | 6 | Clareiras que se repetem (o Leshy faz o grupo andar em círculos — achar a árvore marcada para sair); Curupiras com pegadas falsas; **mini-chefe: Mapinguari Ancião** |
| 4 | `forest_04_elder_tree` | **Árvore Anciã** | Aberto (arena) | 6 | **Leshy**; ouro dos viajantes perdidos; Coroa de Galhos |

## 8. Deserto (`map_desert`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `desert_01_caravan_road` | **Rota das Caravanas** | Aberto | 11 | Carroças abandonadas com o brasão do rei; Ghuls e hienas; primeira tempestade de areia |
| 2 | `desert_02_dunes` | **Mar de Dunas** | Aberto | 11 | Vermes da Morte sob a areia; Manticoras; areia movediça; o **oásis** (descanso e segredo) |
| 3 | `desert_03_buried_gate` | **Portão Soterrado** | Misto | 12 | Entrada do templo; Homens-Escorpião; **mini-chefe: Lamassu do Portão** |
| 4 | `desert_04_sphinx_hall` | **Salão da Esfinge** | Arena | 12 | **Esfinge** (fase do enigma); ouro das caravanas; Olho da Esfinge |

### O Deserto no jogo (`desert_01_canyon`)

Mapa único e grande, com a mesma estrutura da Floresta (aldeia de partida, duas áreas de mini-chefe, guardião do portão e chefe final), mas com outro caminho: o **Acampamento** fica ao sul e a rota sobe para o norte em laço (Estrada → Ruínas de Carroças → Passagem → Areia Movediça → Dunas), com ramais sem saída (Caravana, Ninho, Oásis, Ruínas do Sol).

1. **Nômade da Areia** (acampamento): pede o **Chifre do Lamassu**. Tocar o templo das Ruínas do Sol (leste), com a missão ativa, desperta o **Lamassu da Areia** (mini-chefe). Entrega a **Chave de Paus**.
2. **Guardiã do Oásis** (oeste da estrada): pede o **Escaravelho de Ouro**, que a **Rainha Escorpião** (mini-chefe, despertada pela fala dela) carrega no ferrão. Entrega a **Chave de Ouros**.
3. **Sentinela do Portão** (corredor ao norte das Dunas): só abre o portão com as duas chaves.
4. **Esfinge** (chefe final) no Salão atrás do portão, com a saída para a Fazenda.

Gerado por `tools/assets/build_desert.py`. O Deserto é aberto pela Capital e o portal do chefe leva de volta a ela.

## 10. Pântano (`map_swamp`)

| # | ID | Área | Espaço | Nível | Destaques |
|---|---|---|---|---|---|
| 1 | `swamp_01_bog_paths` | **Trilhas do Brejo** | Misto | 15 | Atoleiros; Fogos-fátuos na neblina levando para o caminho errado; Kikimoras |
| 2 | `swamp_02_barrows` | **Túmulos Afundados** | Estreito | 15 | Draugrs saindo dos túmulos na lama; segredo: túmulo com tesouro antigo |
| 3 | `swamp_03_black_shore` | **Margem do Lago Negro** | Misto | 16 | Rusalkas dançando na margem; a barcaça do rei afundada; **mini-chefe: Bunyip do Lago** |
| 4 | `swamp_04_grendel_hall` | **Salão em Ruínas** | Arena (margem + lago) | 16 | **Grendel e a Mãe de Grendel**; tesouro do lago + ouro do rei; Espada dos Gigantes |

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

### Ruínas no jogo (`ruins_01_city`)

Mapa grande (cerca de 22 mil m2, 11 salas) com a mesma estrutura da Floresta e outro caminho, misturando **partes murados** e **partes abertas**:

- **Murados:** o **Bairro Velho** (oeste) e o **Bairro do Mercado** (leste), o labirinto de ruas de Destroyed Walls (o segundo virado 180 graus); a **Cidadela**, muralha de Ruin_Wall com dois muros internos que obrigam um caminho em S; o corredor do portão; o **Cofre Real**, salão murado com colunata.
- **Abertos:** o **Acesso** de partida, o **Fórum** (praça de lajes com colunas, fundações de casas caídas, poço e obelisco), a **Praça dos Cavaleiros** (coreto em ruínas), a **Praça dos Monólitos** (círculo de pedras em pé), a **Avenida das Colunas** (pares de colunas, estátuas e arcos) e o **Pátio Alto**.
- Uma muralha caída (trechos de muro, tocos de colunas, pedras e mato) contorna as bordas do mapa.

Caminho: Acesso → Fórum; a oeste, Bairro Velho → Praça dos Cavaleiros; a leste, Bairro do Mercado → Praça dos Monólitos; ao meio, a Avenida; os três fecham no Pátio Alto → Cidadela → corredor do portão → Cofre Real.

1. **Leônidas** (Acesso): a missão dos goblins (limpar os dois bandos dos bairros). **Erudita das Ruínas** (Fórum): pede o **Coração de Pedra**. Tocar o cavaleiro de pedra da Praça dos Cavaleiros, com a missão ativa, desperta o **Guardião das Ruínas** (mini-chefe). Entrega a **Chave do Leão**.
2. **Sacerdotisa** (Praça dos Monólitos): pede o **Estandarte do Campeão**; a fala dela desperta o **Campeão Caído** (mini-chefe). Entrega a **Chave da Águia**.
3. **Porteiro das Ruínas** (corredor ao norte da Cidadela): só abre o portão com as duas chaves.
4. **Rei Caído** (chefe final) no Cofre Real atrás do portão, com a saída de volta a Tortuga.

O **Alfa da Matilha** continua solto no Pátio Alto (a carne dele é da missão do Bobo da Corte). Gerado por `tools/assets/build_ruins.py`.

### Forte no jogo (`fort_01_gate`)

Mapa grande (grade de 54 x 54 células de 2,5 m, cerca de 18 mil m2 de área e 8,7 mil m2 de piso), todo murado, com a mesma estrutura da Floresta e outro caminho: a **Guarnição** (partida, ao sul) sobe ao **Pátio de Armas**; dali saem três rotas paralelas para a **Galeria**, que corta o mapa de leste a oeste: a oeste, **Quartel Oeste → Ossuário**; a leste, **Quartel Leste → Salão do Trono**; no meio, o **Salão das Colunas** (com duas câmaras sem saída). Câmaras com baús também saem da Galeria.

1. **Sargento da Guarnição** (partida): a missão de limpar os dois quartéis.
2. **Exilado** (Ossuário, oeste): pede a **Lâmina do Senhor Elfo**; a fala dele desperta o **Senhor Elfo Sombrio** (mini-chefe). Entrega a **Chave de Ônix**.
3. **Penitente** (Salão do Trono, leste): pede o **Anel da Rainha**; a fala dela desperta a **Rainha das Súcubos** (mini-chefe). Entrega a **Chave de Rubi**.
4. **Carcereiro do Forte** (corredor ao norte da Galeria): só abre o portão com as duas chaves.
5. **Barão Infernal** (chefe final) no Salão do Barão atrás do portão, com a saída para a Capital.

O **Comandante** anda solto no Pátio de Armas (o crânio dele é da missão do Padre). Gerado por `tools/assets/build_fort.py`.

### Catacumbas no jogo (`catacombs_01_depths`)

Mapa novo (cerca de 15,8 mil m2, 15 salas), de salas de parede de pedra do kit como o Esgoto (grade de blocos de 12 m), com a estrutura do Esgoto e da Floresta e outro caminho: o **Portão da Cripta** (partida) leva à **Nave dos Ossos**, e dali saem três rotas até a **Galeria dos Condenados**: a oeste, **Ala das Celas → Sala de Tortura → Poço do Carrasco**; a leste, **Ala das Celas → Ossuário → Capela dos Acorrentados**; no meio, **Salão das Correntes → Pátio do Tribunal**. Salas laterais sem saída: o **Cofre** (oeste) e a **Cela Secreta** (leste).

1. **Frade das Catacumbas** (partida): a missão de limpar as duas Alas das Celas.
2. **Carcereiro Cego** (Nave dos Ossos): pede o **Machado do Carrasco**. Tocar a gaiola do Poço do Carrasco, com a missão ativa, desperta o **Carrasco das Catacumbas** (mini-chefe). Entrega a **Chave de Ferro**.
3. **Prisioneira** (Capela dos Acorrentados): pede o **Grilhão da Alma**; a fala dela desperta a **Alma Acorrentada** (mini-chefe). Entrega a **Chave de Osso**.
4. **Diretor das Catacumbas** (corredor ao norte da Galeria): só abre o portão com as duas chaves.
5. **Rei Acorrentado** (chefe final) na Cripta atrás do portão, com a saída para a Capital.

Decoração: celas de grades de ferro com presos sentados ou encolhidos, bolas de ferro e correntes no chão, grilhões e correntes nas paredes (peças próprias, `tools/assets/build_chains.py`), forcas, caixões, instrumentos de tortura, ossos, braseiros e teias. Gerado por `tools/assets/build_catacombs.py`.

### Mina no jogo (`mine_01_crystal_vein`)

Mapa grande e **labirinto** (cerca de 17,6 mil m2, 107 salas), feito como o Esgoto: uma grade de 9 x 11 salas de 12 m ligadas por portas (árvore crescente com muitos becos e alguns laços), em setores de monstros, com paredes de pedras (de todos os tipos) e cristais azuis e roxos que brilham. Os **trilhos do trem são o caminho**: uma linha principal sai da entrada (sul), serpenteia até o túnel do portão e o Coração da Mina (norte), e ramais levam às salas dos NPCs e dos mini-chefes; alguns becos têm trilhos de enfeite que acabam numa carroça virada, com baús, ouro e pedras preciosas.

Salas especiais ligadas à borda do labirinto: **Acampamento dos Anões** (leste, perto da partida), **Gruta das Carroças** (oeste), **Salão dos Cristais** (leste), **Casa do Joalheiro** (oeste, no alto) e **Câmara Secreta** (leste, no alto). Anões mineiros (o corpo do Arqueiro masculino, com pá na mão) são NPCs e gente de cenário pelos trilhos e acampamentos.

1. **Aprendiz de Mineiro** (partida): a missão de limpar os dois primeiros bandos das galerias.
2. **Capataz Brokk** (Acampamento): pede a **Presa do Chefe Troll**. Tocar a carroça abandonada da Gruta das Carroças, com a missão ativa, desperta o **Chefe Troll** (mini-chefe). Entrega a **Chave da Picareta**.
3. **Joalheiro Dolgrim** (Casa do Joalheiro): pede o **Núcleo de Quartzo**. Tocar o **Cristal Pulsante** do Salão dos Cristais, com a missão ativa, desperta a **Besta de Quartzo** (mini-chefe). Entrega a **Chave da Lanterna**.
4. **Guarda-Chaves Thrain** (túnel ao norte): só abre o portão com as duas chaves.
5. **Golem de Cristal** (chefe final) no Coração da Mina, com a saída de volta à Fazenda.

O **Guardião do Túmulo** (a Alma Real do Padre) anda solto em uma sala do labirinto. Gerado por `tools/assets/build_mine.py`.

### Bunker no jogo (`bunker_01_entrance`)

Mapa grande e **labirinto** (grade de 69 x 82 células de 2 m, cerca de 10,6 mil m2 de piso), feito como o Esgoto, com as paredes e pilares do pacote Bk_*: salas de 10 m ligadas por vãos de 6 m (árvore crescente com muitos becos e alguns laços), em três setores de monstros. A **Guarnição** (partida) fica ao sul; o túnel do portão e a **Sala de Comando** (chefe final), ao norte. Salas especiais nas laterais: **Depósito de Suprimentos** e **Alojamento** (leste), **Cofre** (leste, no alto), **Arsenal** e **Enfermaria** (oeste).

Decoração: **armamentos** (racks, espadas, escudos, bestas, machados, martelos, lanças, canhões), **ferramentas** (pás, enxadas, forcados, bigornas, bancadas, pedras de amolar) e **suprimentos** (caixotes, barris, sacos, prateleiras de garrafas, comida, camas e mesas); cada sala do labirinto tem um tema (depósito, arsenal, oficina, alojamento ou refeitório).

1. **Sargento da Guarnição** (partida): a missão de limpar os dois primeiros bandos.
2. **Intendente Vorn** (Depósito, leste): pede o **Selo do Arsenal**. Tocar o rack de armas do Arsenal (oeste), com a missão ativa, desperta a **Armadura Viva** (mini-chefe). Entrega a **Chave de Latão**.
3. **Médica de Campo Lena** (Enfermaria, oeste, no alto): pede a **Medalha de Guerra**. Tocar o catre do Alojamento (leste), com a missão ativa, desperta o **Comandante Podre** (mini-chefe). Entrega a **Chave de Aço**.
4. **Sentinela do Portão** (túnel ao norte): só abre o portão com as duas chaves.
5. **General Ferrugem** (chefe final) na Sala de Comando, com a saída de volta à Fazenda.

Gerado por `tools/assets/build_bunker.py`.

### Floresta Escura no jogo (`dark_forest_01_woods`)

Mapa grande (10 salas, cerca de 20 mil m2) com a mesma estrutura da Floresta e outro caminho: mata aberta de grama escura cercada de arbustos e bambus. A **Clareira da Borda** (partida) abre no **Matagal**, e dali saem três rotas até a **Mata Seca**: a oeste, **Pântano das Cobras → Clareira das Serpentes**; a leste, **Bosque dos Cogumelos → Círculo de Esporos**; e uma direta ao norte. Depois vêm o **Bosque dos Morcegos**, o corredor do portão e o **Covil do Ancião Sombrio**.

Decoração: **árvores secas** em abundância, **cogumelos** (de pequenos a gigantes, alguns brilhando), **morcegos** voando em círculos (papel `bat` do `crowd`) e **cobras** (peças `Snake_*`, feitas por `tools/assets/build_snakes.py`): enroscadas e deslizando em círculos; também lápides, cruzes, ossos, teias e fogueira.

1. **Lenhador Ardo** (partida): a missão de limpar os dois primeiros bandos do Matagal.
2. **Herbalista Mirta** (Bosque dos Cogumelos, leste): pede a **Presa da Víbora Anciã**. Tocar o **Totem das Serpentes** da Clareira (oeste), com a missão ativa, desperta a **Víbora Anciã** (mini-chefe). Entrega a **Chave de Musgo**.
3. **Encantador Zhar** (Pântano das Cobras, oeste): pede a **Coroa de Esporos**. Tocar o **Cogumelo Ancestral** do Círculo de Esporos (leste), com a missão ativa, desperta o **Rei dos Esporos** (mini-chefe). Entrega a **Chave de Espinho**.
4. **Guardião da Mata** (corredor ao norte do Bosque dos Morcegos): só abre o portão com as duas chaves.
5. **Ancião Sombrio** (chefe final) no Covil, com a saída de volta à Fazenda.

Gerado por `tools/assets/build_darkforest.py`.

### Monstros por mapa (cada mapa tem os seus; só o Mímico e os guardiões dos portões se repetem)

A Floresta e o Esgoto mantêm os monstros deles. Nos outros mapas cada monstro tem um visual só dele (modelos do OpenGameArt, CC0, convertidos por `tools/assets/build_oga_monsters.py` e ligados em `tools/assets/set_monster_roster.py`). **Pendente** = ainda sem modelo (aparece como uma cápsula colorida, `look: placeholder`, `visual_pending: true`).

| Mapa | Monstros (visual) |
|---|---|
| Docas | Marujo Afogado (**pendente**) · Jacaré do Cais (gator) · Caranguejo Carniceiro (crab) · Pirata Morto (**pendente**) · Anglerman (angler) · Capitão Afogado (octaminator) · Casco Vivo (plank_monster) · Tubarão-Porco (pork_shark) |
| Ruínas | Goblin (goblin) · Soldado Fantasma (ghost_wing) · Cão de Guerra Morto (**pendente**) · Alfa da Matilha (**pendente**) · Rei Caído (**pendente**) · Guardião das Ruínas (golem_block) · Campeão Caído (**pendente**) |
| Cemitério | Coveiro Louco (**pendente**) · Verme de Cova (**pendente**) · Esqueleto (skeleton) · Zumbi Magro (zombie) · Gárgula de Lápide (**pendente**) · Carniçal Inchado (fatty) · Ogro Coveiro (**pendente**) · Ogro da Cripta (**pendente**) · Senhor da Cripta (undead) · Sentinela do Túmulo (**pendente**) |
| Forte | Elfo Sombrio (dark_elf) · Diabrete Aranha (exp_demon) · Súcubo (succubus) · Comandante Amaldiçoado (demon) · Cão do Inferno (**pendente**) · Demônio da Noite (night_demon) · Barão Infernal (glutton) · Senhor Elfo Sombrio (dark_elf) · Rainha das Súcubos (succubus) |
| Catacumbas | Preso Esquelético (**pendente**) · Rastejante das Celas (crawlmaster) · Olho de Tentáculos (tentacleye) · Miserável Acorrentado (sonask) · Carniçal da Cela (**pendente**) · Guarda Acorrentado (**pendente**) · Torturador Encapuzado (**pendente**) · Morcego de Ossos (**pendente**) · Atormentador (**pendente**) · Carcereiro Morto (**pendente**) · Rei Acorrentado (darsh) · Carrasco das Catacumbas (ogre) · Alma Acorrentada (**pendente**) |
| Deserto | Escorpião Venenoso (scorpion) · Escaravelho Devorador (alien_bug) · Abutre Carniceiro (**pendente**) · Naja das Dunas (cobra) · Cacto Carnívoro (cactus) · Esfinge (**pendente**) · Rainha Escorpião (scorpion) · Lamassu da Areia (earth_dragon) |
| Mina | Espreitador (stalker) · Aranha das Cavernas (spider_big) · Mineiro Morto (**pendente**) · Verme de Rocha (**pendente**) · Gnomo das Sombras (**pendente**) · Esqueleto de Mineiro (**pendente**) · Golem de Magma (lava_golem) · Guardião do Túmulo (**pendente**) · Golem de Gelo (golem_ice) · Troll das Cavernas (troll) · Golem de Rocha (**pendente**) · Golem de Cristal (golem_ice) · Chefe Troll (troll) · Besta de Quartzo (**pendente**) |
| Bunker | Soldado Morto (**pendente**) · Saqueador do Bunker (**pendente**) · Ratazana de Paiol (rat) · Soldado Infectado (hazmat) · Armadura Vazia (**pendente**) · Besouro de Guerra (**pendente**) · Recruta Infectado (**pendente**) · Brutamontes de Trincheira (**pendente**) · Espectro do Rádio (**pendente**) · General Ferrugem (mutant_grunt) · Armadura Viva (**pendente**) · Comandante Podre (**pendente**) |
| Floresta Escura | Corvo Negro (raven) · Lobisomem (werewolf) · Morcego Pestilento (bat) · Réptil da Floresta (reptile) · Viúva da Mata (**pendente**) · Cogumelo Carniceiro (mushroom_cap) · Enforcado (**pendente**) · Caçador Esquelético (**pendente**) · Cervo Espectral (**pendente**) · Fogo-Fátuo (**pendente**) · Ancião Sombrio (horror) · Víbora Anciã (reptile) · Rei dos Esporos (**pendente**) |

### Docas (`docks_01_pier`) — ligada ao porto de Tortuga

Mapa grande de píeres de madeira sobre o mar (Modular Wooden Docks, CC0), com a mesma estrutura da Floresta e outro caminho: o **Cais** de partida sobe pelo Píer Principal até o **Mercado de Peixe**; dali, um laço a oeste (**Estaleiro**) e um a leste (**Peixaria**) fecham no **Farol** e no **Armazém**; a Calçada ao norte leva ao **Atracadouro**, ao corredor do portão e ao **Convés** do chefe final. A entrada fica no porto de Tortuga e o portal "Voltar ao porto" leva de volta. Tem barcos, galeões piratas ancorados, peixes e caranguejos, e a decoração é de cais (bitolas, caixotes, barris, redes, bancas, tochas e bandeiras).

1. **Mestre do Porto** (cais de chegada): pede o **Leme do Casco Vivo**. Tocar o casco encalhado do Estaleiro, com a missão ativa, desperta o **Casco Vivo** (mini-chefe). Entrega a **Chave da Âncora**.
2. **Peixeira** (Peixaria): pede o **Dente de Ouro do Tubarão**; a fala dela desperta o **Tubarão-Porco** (mini-chefe). Entrega a **Chave da Bússola**.
3. **Vigia do Cais** (corredor ao norte do Atracadouro): só abre o portão com as duas chaves.
4. **Capitão Afogado** (chefe final) no Convés atrás do portão, com a saída de volta a Tortuga.

Os encontros `dk_*` da missão dos contrabandistas continuam no mapa. Gerado por `tools/assets/build_docks.py`.

