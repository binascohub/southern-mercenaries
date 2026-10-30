# Itens, Loot e Tesouros

> Versão 7 · 2026-10-30 · Complementa `02-personagens.md` (equipamento visual), `02-0-elementos.md` (Poção Elemental), `03-inimigos.md` (drops), `04-tortuga-e-missoes.md` (Mercado Pirata), `04-1-capital-real.md` (lojas da Capital), `05-1-refino.md` (refino e aura) e `06-mundo-e-historia.md` (tesouros)
> Números são propostas iniciais para balancear depois.

## 1. Categorias de item

| ID | Categoria | Uso | Pode vender? |
|---|---|---|---|
| `equipment` | Equipamento | Equipar no personagem; **aparece no corpo** (arma, cabeça, corpo, mãos, pés, mão secundária, barda, anéis, amuleto) | Sim (preço baixo) |
| `consumable` | Consumível | Poções de vida/recurso, **Poções Elementais**, bebidas da taverna, **Patuá de Retorno** (`return_charm`, vendido pelo Macumbeiro), **pergaminhos de refino** (`05-1-refino.md`) | Sim |
| `material` | Material | Crafting no ferreiro (lista em `03-inimigos.md`, seção 13) e **cristais** de refino | Sim |
| `valuable` | **Valioso** | Sem uso em combate; serve **só para vender** (piratas, joalheiro) | Sim (preço alto) |
| `relic` | Relíquia | Item da história, guardado por cada chefe | Não |
| `gold` | Ouro | Moeda; **cada jogador tem o seu** | — |

## 2. Materiais dos equipamentos (tiers)

Todo equipamento é feito de um **material**, que define os **valores base** (dano, armadura) e o **visual**. A progressão é sempre nesta ordem (decisão do autor). O primeiro tier é diferente para armaduras e armas: **armaduras começam em pano** e **armas começam em madeira**.

| Tier | ID | Armaduras | Armas | Nível do item | Mapas onde mais cai | Multiplicador base | Visual |
|---|---|---|---|---|---|---|---|
| 0 | `cloth` / `wood` | **Pano** | **Madeira** | 1 | Início do jogo | x1,0 | Armadura: roupa de baixo de pano simples, cinza/bege, gasta. Arma: madeira crua, simples, com marcas de uso. Todos os heróis começam assim |
| 1 | `iron` | **Ferro** | **Ferro** | 1–4 | 1 Esgoto, 2 Ruínas | x1,6 | Metal escuro e fosco, rebites aparentes, um pouco de ferrugem |
| 2 | `steel` | **Aço** | **Aço** | 5–8 | 3 Floresta, 4 Cavalos | x2,3 | Metal cinza-claro polido, bordas afiadas, acabamento militar |
| 3 | `copper` | **Cobre** | **Cobre** | 9–12 | 5 Aves, 6 Deserto | x3,1 | Metal avermelhado/alaranjado com gravuras; proposta: **cobre temperado** de forja antiga, mais forte que o aço comum |
| 4 | `silver` | **Prata (branca)** | **Prata (branca)** | 13–16 | 7 Águas, 8 Pântano | x4,0 | Metal **branco** brilhante, quase reluzente no escuro; detalhes finos |
| 5 | `gold` | **Ouro** | **Ouro** | 17–20 | 9 Serpentes, 10 Inferno | x5,0 | Dourado intenso, ornamentos reais; o material dos tesouros de Lúcifer |

### Armas iniciais de madeira
| Classe | Arma inicial |
|---|---|
| Mago | Cajado de madeira |
| Arqueiro | Arco de madeira simples e flechas de ponta de madeira |
| Cavaleiro | Lança de madeira (e escudo de madeira, proposta) |
| Ninja | **Adagas de madeira** (de treino do clã — decisão do autor) |
| Invocador | Livro com capa de madeira |

### Regras
- **Tudo que é equipado aparece no jogador** (decisão do autor): cada material tem modelo e textura próprios, e cada peça (arma, cabeça, corpo, mãos, pés, mão secundária, barda) troca **separadamente** no corpo, visível para todos os jogadores no co-op. A evolução fica clara: pano/madeira → ferro → aço → cobre → prata → ouro.
- O **refino** (+1 a +5) não muda o modelo da peça, mas cria uma **aura em volta do herói** na cor do elemento dele (`05-1-refino.md`).
- **Nome do item** = tipo + material (+ refino) (ex.: "Cajado de Madeira", "Espada de Aço +3", "Elmo de Prata", "Lança de Ouro"). Chaves de tradução por tipo e material (`ITEM_TYPE_SWORD` + `MATERIAL_STEEL`).
- **Nível mínimo para equipar** = início da faixa do tier (ex.: Cobre a partir do nível 9).
- **Material e raridade são independentes:** uma "Espada de Ferro" pode ser comum, mágica, rara ou única; os **afixos** vêm da raridade (seção 3). Uma peça de Ouro comum tem valores base altos, mas nenhum afixo.
- **Armas com partes de madeira** (cajado, arco, cabo da lança, capa do livro): a partir do Ferro, o material aparece nas **ponteiras, reforços, lâminas e cantoneiras** (ex.: arco de madeira com reforços de prata; cajado com ponteira de ouro).
- **Classes de pano (Mago e Invocador):** usam túnicas, mas o material aparece em **reforços, bordados, fivelas e ombreiras** (ex.: túnica com placas de cobre; manto com fios de prata; túnica bordada em ouro).
- **Arqueiro:** aljava e couraça leves com peças de metal do tier.
- **Cavaleiro:** a **barda do cavalo** também segue o tier.
- **Lendários** têm visual exclusivo e não seguem a aparência padrão do tier (mas têm o multiplicador do nível em que caem).
- **Onde comprar (proposta):**

| Tier | Tortuga (Rua Principal) | Capital Real |
|---|---|---|
| Pano/Madeira, Ferro, Aço | Sim (comuns) | Sim |
| Cobre, Prata | Não | Sim (comuns e mágicos, preço 4x) |
| Ouro | Não | Só o **Ferreiro Real**, sob encomenda, com materiais raros |

- O **Mercado Pirata** pode trazer qualquer tier até o do nível do jogador +1 (itens roubados).

## 3. Raridades

| ID | Raridade | Cor | Afixos | Onde aparece |
|---|---|---|---|---|
| `common` | Comum | Branco | 0 | Qualquer lugar; lojas |
| `magic` | Mágico | Azul | 1 a 2 aleatórios | Monstros, elites, baús, Mercado Pirata |
| `rare` | Raro | Amarelo | 3 a 4 aleatórios | Elites, mini-chefes, chefes, tesouros, Mercado Pirata |
| `unique` | Único | Laranja | Fixos (item com nome e visual próprio) | Chefes, tesouros, rumores verdadeiros, raramente no Mercado Pirata |
| `legendary` | **Lendário** | Vermelho | Fixos + bônus de elemento + efeito especial | **Só nos tesouros dos chefes** |

- A cor da raridade aparece na **moldura e no nome** do item; o material aparece no **modelo e no ícone**.
- Itens lendários são os **mais raros do jogo** e cada um é ligado ao chefe que guardava o tesouro (ex.: do Pégaso demoníaco sai um equipamento com tema de asas/cavalo; dos tesouros do Esgoto e das Ruínas, peças do arsenal real do reino do Arqueiro).
- Todo lendário tem visual exclusivo no personagem.

## 4. Tesouro do covil

Ao derrotar o chefe de um mapa, o grupo abre o **tesouro do covil**. Conteúdo **por jogador** (loot individual):

| Conteúdo | Quantidade | Observação |
|---|---|---|
| Equipamento **lendário** | 1 garantido | Sempre da classe do jogador, para ele poder usar |
| Equipamentos raros ou únicos | 2 a 3 | Pelo menos 1 da classe do jogador; do tier do mapa ou um acima |
| **Valiosos** | 5 a 10 | Tema do mapa (seção 5); para vender |
| Pergaminhos de refino | 1 a 2 | Chance de 1 Abençoado (`05-1-refino.md`) |
| Ouro | Alto | Escala com o nível do mapa |
| Materiais raros | 2 a 4 | Da família de monstros do mapa |

Conteúdo **por grupo**:
- 1 **relíquia** do chefe (vai para a campanha do host; ver `06-mundo-e-historia.md`).

### O tesouro do reino do Arqueiro (mapas 1 e 2)
O primeiro grande tesouro do jogo é **dividido em duas partes**, ambas riquezas do **reino derrotado na guerra** (o reino do Arqueiro):

| Parte | Onde | Guardião | Conteúdo temático | Relíquia (proposta) |
|---|---|---|---|---|
| **Tesouro Perdido da Guerra** | Esgoto de Tortuga | Rainha dos Ratos | A parte roubada pelos fundadores de Tortuga para salvá-la dos vencedores: moedas do reino, medalhas, joias da coroa, peças do arsenal real e um **mapa antigo** que aponta onde ficou o resto | **Coroa do Rei Caído** |
| **Cofre Real** | Ruínas do Reino do Arqueiro (cripta do castelo) | Cérbero | O resto das riquezas que não deu tempo de levar: o cofre do rei, cetro, joias, armas cerimoniais | **Coleira dos Portões** |

- Os lendários desses dois tesouros são **peças do arsenal real** do reino do Arqueiro.
- **Proposta:** se o Arqueiro estiver no grupo, ele tem falas especiais ao abrir esses tesouros e o seu lendário é uma relíquia da sua própria vila.

### O ouro do rei (mapas 6 a 9)
- Os tesouros do Deserto, Águas, Pântano e Serpentes trazem **ouro com o brasão do reino vencedor**, desviado por Lúcifer. Proposta: o Bobo comenta, e Dália (se estiver no grupo) reconhece peças do castelo.

### Tesouros menores
| Origem | Conteúdo |
|---|---|
| Baú escondido no mapa | Ouro, 1 a 2 valiosos, chance de item mágico/raro, chance de pergaminho |
| Rumor de tesouro verdadeiro | Ouro, 3 a 5 valiosos, 1 item raro ou único |
| Elite | Ouro, 1 a 2 itens (mágico ou melhor), chance de 1 valioso ou pergaminho |
| Mini-chefe | Ouro alto, 2 a 3 itens, 1 raro garantido, 1 a 3 valiosos, chance de pergaminho Abençoado |

## 5. Valiosos

Objetos de valor sem uso no combate. Ocupam espaço na bolsa e **empilham** (até 20 do mesmo tipo por espaço).

### Valiosos comuns (qualquer mapa)
| ID | Valioso | Valor base (ouro) |
|---|---|---|
| `old_coins` | Moedas antigas | 20 |
| `silver_goblet` | Cálice de prata | 60 |
| `rough_gem` | Gema bruta | 80 |
| `jeweled_ring` | Anel cravejado | 150 |
| `gold_bar` | Barra de ouro | 250 |
| `cut_gem` | Gema lapidada | 300 |
| `golden_crown` | Coroa de ouro | 800 |

### Valiosos por mapa
| Mapa | ID | Valioso | Valor base (ouro) |
|---|---|---|---|
| Esgoto | `war_coins` | Moedas do reino derrotado | 40 |
| Esgoto | `war_medal` | Medalha de guerra de ouro | 120 |
| Esgoto | `royal_seal_ring` | Anel-selo real | 300 |
| Esgoto | `crown_jewel` | Joia da coroa | 600 |
| Ruínas | `royal_silverware` | Prataria do castelo | 150 |
| Ruínas | `ceremonial_dagger` | Adaga cerimonial cravejada | 350 |
| Ruínas | `royal_scepter` | Cetro do rei caído | 900 |
| Ruínas | `cerberus_fang` | Presa de Cérbero banhada em ouro | 800 |
| Floresta | `amber_resin` | Âmbar com inseto preso | 150 |
| Floresta | `traveler_purse` | Bolsa de viajante perdido | 250 |
| Floresta | `jorogumo_silk` | Rolo de seda de Jorōgumo | 500 |
| Floresta | `elder_heartwood` | Cerne dourado da Árvore Anciã | 950 |
| Cavalos | `golden_horseshoe` | Ferradura de ouro | 120 |
| Cavalos | `jeweled_saddle` | Sela cravejada de pedras | 400 |
| Cavalos | `arion_mane` | Crina de Arion (fios que nunca se partem) | 600 |
| Cavalos | `pegasus_statuette` | Estatueta de Pégaso em ouro | 900 |
| Aves | `bronze_feather` | Pena de bronze estinfália | 150 |
| Aves | `roc_egg_shell` | Casca de ovo de Roca | 450 |
| Aves | `phoenix_ash_urn` | Urna com cinzas da Fênix | 1.000 |
| Deserto | `royal_caravan_coins` | Moedas das caravanas do rei | 200 |
| Deserto | `scarab_amulet` | Amuleto de escaravelho em ouro | 450 |
| Deserto | `lamassu_tablet` | Tábua com escrita antiga | 600 |
| Deserto | `sphinx_eye_gem` | Gema do olho da Esfinge | 1.100 |
| Águas | `black_pearl` | Pérola negra | 200 |
| Águas | `royal_navy_chest` | Cofrinho da marinha do rei | 450 |
| Águas | `sunken_chalice` | Cálice de naufrágio | 500 |
| Águas | `kraken_ink_vial` | Frasco de tinta de Kraken | 1.100 |
| Pântano | `bog_gold_torc` | Colar de ouro dos túmulos | 350 |
| Pântano | `draugr_ring` | Anel de draugr | 500 |
| Pântano | `royal_barge_bar` | Barra de ouro da barcaça do rei | 700 |
| Pântano | `giant_sword_hilt` | Punho cravejado de espada gigante | 1.200 |
| Serpentes | `naga_idol` | Ídolo de ouro dos naga | 400 |
| Serpentes | `basilisk_eye_gem` | Gema do olho de Basilisco | 650 |
| Serpentes | `world_serpent_scale` | Escama dourada da Serpente do Mundo | 1.300 |
| Inferno | `hellfire_ruby` | Rubi do fogo infernal | 1.500 |
| Inferno | `lucifer_gold_coin` | Moeda do tesouro de Lúcifer | 300 (aparece aos montes) |

## 6. Mercado Pirata (Porto de Tortuga)

O comércio do porto é tocado por **piratas que trazem itens roubados pelo mundo afora** (`04-tortuga-e-missoes.md`).

### Itens roubados à venda
- **Estoque rotativo:** a cada volta para Tortuga, "chega um navio" com **3 a 6 itens** novos, por jogador (cada um vê suas ofertas).
- Raridade das ofertas: mágico (60%), raro (35%), único (5%). Nunca lendário.
- Itens do nível do jogador (±2), de qualquer material até o tier do nível +1, com chance maior de serem da sua classe.
- Às vezes um **Pergaminho Abençoado** (caro).
- Preço alto: **3x** o valor base do item. Vale a pena quando falta uma peça específica.
- Itens "exóticos": alguns itens únicos **só aparecem no Mercado Pirata** (armas e armaduras de terras distantes, com visual próprio) — **proposta**.
- Cada navio tem um capitão pirata (nome, frase e um desconto de 10% para quem comprar 3 itens no mesmo dia — proposta).

### Compra de valiosos
- Os piratas **compram os valiosos** dos tesouros sem perguntas, para revender em outros portos.
- Preço de venda = valor base × **variação do dia**.
- A variação muda a cada navio (a cada volta para Tortuga): entre **80% e 120%** para cada tipo de valioso. Assim vale a pena guardar no baú e vender quando o preço estiver alto.
- O **capitão do dia** pode pagar +25% pelos valiosos de um tema específico ("meu cliente quer peças de Pégaso").
- Na Capital, o **joalheiro** paga 110% fixo (`04-1-capital-real.md`).
- Equipamentos vendidos: **25%** do valor do item. Materiais: preço fixo.

### Poções Elementais
- Os piratas vendem as 4 **Poções Elementais** (Água, Fogo, Ar, Terra), trazidas de terras distantes. Regras em `02-0-elementos.md`, seção 4.
- Preço proposto: 100 + 25 × nível do personagem.
- Ao lado de cada poção, a janela mostra os mapas/monstros já conhecidos em que ela é forte.

### Uso do ouro
Itens piratas, equipamentos e poções nas lojas, Poções Elementais, pergaminhos de refino, crafting no ferreiro, bebidas na taverna, redistribuir pontos.

### Exemplo de venda
| Valioso | Valor base | Variação do dia | Bônus do capitão | Recebe |
|---|---|---|---|---|
| Estatueta de Pégaso | 900 | 110% | +25% (tema do dia) | 1.237 |
| Gema bruta x5 | 80 cada | 90% | — | 360 |

## 7. Geração de equipamentos

```
item = item_base (tipo, slot, classe)
     + material (tier → multiplicador base e visual; seção 2)
     + raridade
     + afixos sorteados (conforme a raridade)
     + nível do item (nível da área onde caiu; define o tier provável)
     + refino (sempre +0 ao cair; sobe com pergaminhos — 05-1-refino.md)
```

- **Tier sorteado pelo nível da área:** 80% o tier da faixa, 15% o tier anterior, 5% o próximo (proposta).
- Tier 0 só existe como equipamento inicial e nas lojas de Tortuga (não cai de monstros depois do nível 2).

| Exemplo de afixo | Efeito |
|---|---|
| `+str` / `+dex` / `+int` / `+vit` | Atributo |
| `+life` | Vida máxima |
| `+resource` | Recurso máximo (mana, energia…) |
| `+elem_damage` | +% dano de um elemento |
| `+crit` | Chance de crítico |
| `+move_speed` | Velocidade de movimento |
| `+res_fire` … `+res_earth` | Resistência a dano de um elemento (contra monstros desse elemento) |
| `+gold_find` | Mais ouro encontrado (combina com mercenários) |

- Itens base, materiais, afixos, únicos, lendários, valiosos, poções, pergaminhos e tabelas das lojas ficam em arquivos de dados (ex.: `items/bases.json`, `items/materials.json`, `items/affixes.json`, `items/legendaries.json`, `items/valuables.json`, `items/consumables.json`, `items/scrolls.json`, `shops/pirate_market.json`).

## 8. Inventário

- Bolsa por personagem com **40 espaços** (decidido). Pode ser **expandida comprando bolsas maiores** nas lojas das cidades (Tortuga e Capital; as da Capital são maiores e mais caras). Valiosos, pergaminhos e cristais empilham.
- **Troca entre jogadores (decidido):** no co-op, jogadores do grupo podem trocar itens entre si, com janela de troca confirmada pelos dois lados. Troca só entre jogadores presentes na mesma partida; o servidor valida.
- Baú em Tortuga (e na Capital, o **banco**) compartilhado entre os personagens do mesmo jogador.
- Loot e ouro individuais: cada jogador vê e pega só o seu.

## 9. Decisões em aberto

- Raridade **Lendário** só nos tesouros dos chefes: manter?
- Itens únicos exclusivos do Mercado Pirata: manter?
- Faixas de nível e multiplicadores de cada material: manter?
- Preço e tamanho das bolsas expandidas (espaços extras por bolsa e custo)?
