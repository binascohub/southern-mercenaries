# Inimigos — Monstros e Demônios

> Versão 11 · 2026-10-30 · Complementa `01-escopo.md`, `02-0-elementos.md`, `03-1-bestiario.md`, `03-2-areas.md`, `05-itens-e-loot.md` e `06-mundo-e-historia.md`
> Este arquivo traz a **mecânica** dos monstros. As **lendas** e as **pistas de fraqueza** estão em `03-1-bestiario.md`. A divisão de cada mapa em áreas está em `03-2-areas.md`.
> Números são propostas iniciais para balancear depois. Vida e dano são para nível 1 e escalam com o nível da área.

## Tom

**Dark / sombrio.** Os inimigos são **criaturas mitológicas** de vários folclores, em versão macabra, corrompidas pelo inferno — e, no esgoto de Tortuga, **animais contaminados** que viraram monstros. Nada fofo ou cômico. **Os chefes são demônios ou criaturas que fizeram pacto com demônios**, e o **chefão final é Lúcifer**, que quer todo o ouro do mundo.

## Regras dos mapas e elementos

- **Cada mapa tem uma família de criaturas** (animais/criaturas de um mesmo tipo).
- **O chefe do mapa é ligado a essa família**: a criatura mais famosa da família, corrompida por um demônio (ou que fez pacto com um).
- Cada chefe guarda um **tesouro** — parte do ouro que Lúcifer está juntando (`05-itens-e-loot.md`, `06-mundo-e-historia.md`).
- **Todo monstro tem um elemento e é fraco a outro**, pelo ciclo **Água → Fogo → Terra → Ar → Água** (`02-0-elementos.md`, seção 3): +50% de dano do elemento que o vence, -50% do mesmo elemento.
- **A história de cada monstro sempre revela o elemento e a fraqueza** (contada na taverna de Tortuga ou pelo Bobo da Corte na Capital), para o jogador saber qual Poção Elemental comprar antes de partir (`03-1-bestiario.md`).

## Os mapas

**10 mapas**, do mais fácil ao mais difícil:

| Ordem | Ato | ID | Mapa | Ambiente | Família | Elemento predominante | Chefe | Elemento do chefe | Chefe é fraco a |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 | `map_sewers` | **Esgoto de Tortuga** | Túneis, canais de lixo, câmaras alagadas sob a cidade | Animais contaminados | Terra | **Rainha dos Ratos** (pacto com um demônio) | Terra | Fogo |
| 2 | 2 | `map_ruins` | **Ruínas do Reino do Arqueiro** | Capital em ruínas, vilas queimadas, campos de batalha, cemitérios, floresta nevada | Lobos e cães míticos | Terra | **Cérbero** | Fogo / Água / Terra (uma por cabeça) | Água / Ar / Fogo |
| 3 | 2 | `map_forest` | **Floresta Escura** | Mata fechada sem luz do sol, árvores gigantes, teias, cachoeira, clareiras | Espíritos e feras da floresta | Terra | **Leshy** | Terra | Fogo |
| 4 | 2 | `map_horses` | Cavalos Míticos | Planícies e ruínas no alto | Cavalos míticos | Misto | **Pégaso** | Fogo | Água |
| 5 | 2 | `map_birds` | Aves | Picos, penhascos e ninhos | Aves míticas | Ar | **Fênix** | Fogo | Água |
| 6 | 3 | `map_desert` | **Deserto** | Dunas, rotas de caravana, oásis, templo de pedra soterrado | Feras híbridas do deserto | Fogo | **Esfinge** | Ar | Terra |
| 7 | 3 | `map_waters` | Águas | Costa, naufrágios e grutas alagadas | Criaturas das águas | Água | **Kraken** | Água | Ar |
| 8 | 3 | `map_swamp` | **Pântano** | Charcos, atoleiros, neblina, túmulos afundados, lago negro | Mortos e espíritos do pântano | Água | **Grendel** (e sua Mãe) | Água | Ar |
| 9 | 3 | `map_serpents` | Serpentes | Selva, templos em ruínas, templo meio afundado no mar | Serpentes e dragões | Terra | **Jörmungandr** | Água | Ar |
| 10 | 4 | `map_hell` | Inferno | Inferno, rios de lava e de ouro | Súcubos e ecos dos demônios | Fogo | **Lúcifer** | **Muda a cada fase** (Ar → Fogo → todos) | Terra → Água → o que vence o elemento do momento |

- O **Esgoto** é o primeiro mapa: fica **embaixo de Tortuga** e é acessado por um bueiro na Rua Principal (não precisa de barco).
- As **Ruínas do Reino do Arqueiro** são o segundo: continuação direta da história do Esgoto (o resto do tesouro real ficou lá).
- Mapas 1–5 saem de **Tortuga** (missões da taverna); mapas 6–9 saem da **Capital Real** (missões do Bobo da Corte); o 10 é o resgate do Bobo.
- O Cavaleiro **desmonta** em áreas estreitas (ver o tipo de cada área em `03-2-areas.md`).
- Mapas com elementos mistos obrigam o grupo a combinar elementos diferentes (cada jogador com uma poção diferente).

## 1. Regras comuns

### Categorias
| ID | Categoria | Descrição |
|---|---|---|
| `normal` | Comum | Monstro padrão, aparece sozinho ou em grupos |
| `elite` | Elite | Versão maior e mais forte, com 1 a 2 modificadores; aura colorida para ser reconhecida |
| `miniboss` | Mini-chefe | Elite forte com nome, na penúltima área de cada mapa (`03-2-areas.md`) |
| `boss` | Chefe | Fim de cada mapa; 3 fases; arena própria; guarda o tesouro |

### Escala
- **Por nível da área:** vida e dano crescem ~12% por nível. Cada mapa começa num nível maior que o anterior.
- **Por número de jogadores:** vida +60% por jogador extra; loot +30% por jogador extra; dano não muda.
- **Elite:** vida x3, dano x1,5, sempre deixa ao menos 1 item mágico. Uma elite tem o mesmo elemento do monstro base.
- **Mini-chefe:** vida x6, dano x1,8, deixa 1 item raro garantido.

### Comportamento (IA)
| ID | Comportamento | Descrição |
|---|---|---|
| `melee_rush` | Corpo a corpo | Corre até o alvo mais próximo e ataca |
| `swarm` | Enxame | Grupos grandes e fracos que cercam o alvo |
| `pack` | Matilha | Grupo que cerca o alvo e ataca por vários lados ao mesmo tempo |
| `ranged_kite` | À distância | Mantém distância e recua se o jogador se aproximar |
| `caster` | Conjurador | Fica atrás, lança magias, prioriza alvos de baixa vida |
| `support` | Suporte | Cura ou fortalece outros monstros |
| `trickster` | Trapaceiro | Aparece e some, atrapalha e foge |
| `charger` | Investida | Corre em linha reta contra o alvo, com aviso antes |
| `flyer` | Voador | Plana sobre o terreno, ignora obstáculos baixos |
| `ambush` | Emboscada | Escondido (na água, no chão, na areia, nas árvores, no lixo, nos escombros) até o jogador chegar perto |

- **Escolha de alvo:** o jogador mais próximo, exceto quando forçado por `challenge` (Cavaleiro), `iron_body` (Ninja) ou `guardian_bear` (Invocador).
- **Ataques fortes sempre têm aviso** (animação ou marca no chão) de 0,5 a 1,5 s.
- **Aggro em grupo:** ao ver um jogador, o monstro alerta os aliados próximos.
- **Ícone de elemento** ao lado da barra de vida de todo monstro.

### Desempenho (requisito do escopo)
- Limite de **~40 entidades ativas** na área (monstros + animais amigos do Invocador).
- Monstros longe dos jogadores ficam "dormindo" (sem IA nem física).
- Reaproveitar instâncias (pooling) em vez de criar e destruir.
- IA processada no servidor (host); clientes só recebem posição, animação e vida.
- **Cada família compartilha esqueleto e animações**: esgoto (roedor, réptil, morcego), ruínas (quadrúpede canino), floresta (humanoide pequeno, gigante peludo, aranha), cavalos (quadrúpede equino), aves (ave), deserto (quadrúpede felino/touro alado, escorpião, verme), águas (humanoide aquático + tentáculos), pântano (humanoide morto-vivo, gigante), serpentes (serpente + dragão).

## 2. Esgoto de Tortuga (`map_sewers`)

> Túneis escuros e estreitos sob a cidade, canais de lixo e água podre, câmaras alagadas e restos de uma passagem secreta da época da guerra. Os animais que viviam ali foram **contaminados** pelo pacto da Rainha dos Ratos com um demônio e viraram monstros.
> **Mecânica do mapa:** poças de **lodo tóxico** que causam dano ao longo do tempo a quem pisar; algumas áreas alagadas deixam todos `soaked`.

| ID | Monstro | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|
| `plague_rat` | Rato Pestilento | Terra | Fogo | `swarm` | 20 | 4 | Rápida | Enxames de 8 a 12; mordida aplica veneno leve. São os **filhotes da Rainha** |
| `mutant_rat` | Ratazana Mutante | Terra | Fogo | `melee_rush` | 110 | 12 | Média | Do tamanho de um cão; investida curta; costuma ser elite |
| `plague_bat` | Morcego Pestilento | Ar | Terra | `flyer` + `swarm` | 25 | 5 | Rápida | Bandos que saem do teto; guinchos que deixam lento |
| `acid_toad` | Sapo Ácido | Água | Ar | `ranged_kite` | 50 | 9 | Lenta | Cospe ácido à distância, que deixa poça tóxica no chão |
| `sewer_gator` | Jacaré do Esgoto | Água | Ar | `ambush` | 150 | 16 | Média (rápida no bote) | Escondido na água; bote com aviso (bolhas); arrasta a vítima |

### Fúria da Rainha (mecânica do mapa — proposta)
- Cada **Rato Pestilento** morto no mapa deixa a Rainha mais furiosa: **+1% de dano** na luta final, até **+20%**.
- O jogador pode escolher limpar o mapa (mais experiência e loot) ou evitar enxames (luta final mais fácil).

### Chefe: Rainha dos Ratos (`demon_rat_queen`)
- **Conceito:** uma ratazana enorme, mãe de todos os ratos do esgoto. Quando os humanos de Tortuga **mataram seus filhotes**, ela **fez um pacto com um demônio** para se vingar. O demônio a transformou num monstro gigante e contaminou todos os animais do esgoto. Ela fez o ninho sobre o **Tesouro Perdido da Guerra** e usa a **coroa do rei perdido** na cabeça.
- **Visual:** ratazana do tamanho de uma carroça, pelo caindo, olhos vermelhos, a coroa torta na cabeça; na cauda, um **"rei dos ratos"** — dezenas de filhotes mortos-vivos presos pelas caudas entrelaçadas, que ela arrasta e usa como arma.
- **Arena:** câmara alagada e ampla no fundo do esgoto, onde está o ninho sobre o tesouro.
- **Vida:** 1.000 (solo).
- **Elemento:** Terra. **Fraco a:** Fogo.
- **Fase 1 — Mãe Furiosa (100%–60%):** investidas e mordidas em área; chicoteia com a cauda de filhotes entrelaçados; a cada 20 s chama um enxame de Ratos Pestilentos.
- **Fase 2 — A Ninhada (60%–25%):** sobe no ninho e protege 3 **ninhos de filhotes**; enquanto houver ninhos, ela regenera vida. O grupo precisa destruir os ninhos (Fogo causa dano dobrado).
- **Fase 3 — O Pacto (25%–0%):** o demônio toma conta do corpo dela: olhos e boca em chamas negras, abre comportas e **alaga a arena** (todos `soaked`); gás tóxico sai dos canos (áreas de dano com aviso).
- **Tesouro:** o **Tesouro Perdido da Guerra** — parte das riquezas do **reino do Arqueiro**, roubada pelos fundadores de Tortuga para salvá-la do saque dos vencedores e escondida no esgoto (`06-mundo-e-historia.md`). Relíquia proposta: **Coroa do Rei Caído**. Entre os papéis do baú, um **mapa** mostra onde ficou o resto do tesouro: nas ruínas do reino (libera o mapa 2).

## 3. Ruínas do Reino do Arqueiro (`map_ruins`)

> A capital e as vilas do reino derrotado na guerra: muralhas caídas, casas queimadas, campos de batalha com armaduras enferrujadas e covas rasas, cemitérios e uma floresta nevada em volta. Depois da guerra, a região foi **dominada por lobos e cães demoníacos**. No coração do castelo, na cripta real, **Cérbero abriu uma fenda do inferno** e guarda o **resto do tesouro real**.
> **Mecânica do mapa:** neblina nos campos de batalha (visão reduzida); de noite, os lobos ficam mais agressivos (+10% de dano).

| ID | Monstro | Origem | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|---|
| `warg` | Warg | Nórdico | Terra | Fogo | `pack` | 45 | 7 | Rápida | Matilhas de 3 a 5 que cercam o alvo |
| `black_dog` | Cão Negro | Inglaterra | Fogo | Água | `ambush` | 55 | 9 | Rápida | Surge da neblina dos cemitérios e campos de batalha; uivo que deixa lento |
| `cadejo` | Cadejo | América Central | Terra | Fogo | `trickster` | 50 | 8 | Rápida | Some e reaparece atrás do jogador mais isolado |
| `amarok` | Amarok | Inuit | Água (gelo) | Ar | `melee_rush` | 120 | 14 | Média | Caça quem anda sozinho (+50% dano em jogador sem aliado a 10 m); costuma ser elite |
| `werewolf` | Lobisomem | Europa / Brasil | Terra | Fogo | `melee_rush` | 100 | 13 | Rápida | Aldeões sobreviventes da guerra, amaldiçoados; abaixo de 30% de vida entra em fúria (+50% velocidade de ataque) |

### Chefe: Cérbero (`demon_cerberus`)
- **Arena:** a cripta real sob o castelo em ruínas, onde está o cofre com o resto do tesouro.
- **Vida:** 1.500 (solo).
- **Três cabeças, três elementos:** cabeça de **Fogo** (fraca a Água), cabeça de **Gelo/Água** (fraca a Ar), cabeça de **Veneno/Terra** (fraca a Fogo). Cada cabeça tem barra de vida própria e pode ser derrotada separadamente; o grupo ideal leva elementos variados.
- **Fase 1 (100%–65%):** mordidas e sopros alternados das três cabeças.
- **Fase 2 (65%–30%):** uiva e chama matilhas de Wargs; investidas pela arena.
- **Fase 3 (30%–0%):** a última cabeça viva fica em fúria; correntes infernais prendem jogadores (aliado acerta para soltar).
- **Tesouro:** o **Cofre Real** (o resto das riquezas do reino do Arqueiro) + relíquia proposta **Coleira dos Portões**.

## 4. Floresta Escura (`map_forest`)

> Uma mata tão fechada que a luz do sol não chega ao chão: árvores gigantes, teias entre os galhos, cogumelos que brilham, uma cachoeira escondida. Fica entre o reino derrotado e as planícies; era o **terreno de caça do Arqueiro** quando criança. Os espíritos que protegiam a floresta foram corrompidos pelo **Leshy**, o senhor da mata, que fez pacto com um demônio e guarda o ouro de todos os viajantes que se perderam ali.
> **Mecânica do mapa:**
> - **Escuridão:** visão curta; tochas fixas e magias de Fogo iluminam em volta (e espantam alguns monstros).
> - **Trilhas que enganam:** em certas clareiras, o Leshy faz o caminho dar voltas (a mesma clareira se repete); o grupo precisa achar a marca certa (árvore com símbolo, pista do bestiário) para sair do círculo.

| ID | Monstro | Origem | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|---|
| `kodama` | Kodama | Japão | Ar | Terra | `swarm` | 25 | 5 | Rápida | Espíritos pequenos que saem das árvores em bandos; gritos em eco que deixam lento |
| `curupira` | Curupira | Brasil | Fogo | Água | `trickster` | 60 | 10 | Muito rápida | Deixa **pegadas ao contrário** (rastro falso no chão que leva a armadilhas); some e reaparece; cabelo em chamas queima ao toque |
| `dryad` | Dríade | Grécia | Terra | Fogo | `support` | 70 | 6 | Lenta | Ligada a uma **árvore**: cura monstros próximos enquanto a árvore estiver de pé; destruir a árvore mata a dríade |
| `jorogumo` | Jorōgumo | Japão | Água | Ar | `caster` | 90 | 12 | Média | Aparece como mulher e vira aranha; **teias** que prendem o jogador (aliado acerta para soltar); vive perto da cachoeira |
| `mapinguari` | Mapinguari | Brasil (Amazônia) | Terra | Fogo | `melee_rush` | 200 | 18 | Lenta | Gigante peludo de um olho e boca na barriga; grito que atordoa (aviso: enche o peito); couro duro (-30% dano), exceto golpes **de frente na barriga** (+50%); costuma ser elite |

### Chefe: Leshy demoníaco (`demon_leshy`)
- **Conceito:** o senhor da floresta do folclore eslavo, que muda de tamanho (da grama até a copa das árvores) e faz os viajantes andarem em círculos até morrer. Fez pacto com um demônio: em troca de poder, guarda nas raízes o ouro dos viajantes perdidos — e o ouro que Lúcifer manda esconder ali.
- **Arena:** clareira com uma árvore anciã oca no centro (o covil), cercada por árvores que se mexem.
- **Vida:** 2.000 (solo).
- **Elemento:** Terra. **Fraco a:** Fogo.
- **Fase 1 — O Caminho Errado (100%–65%):** pequeno e rápido, cria **cópias** de si (só uma é real; a verdadeira tem a sombra no lado certo — pista no bestiário); raízes saem do chão (marcas de aviso).
- **Fase 2 — Do Tamanho das Árvores (65%–30%):** cresce até ficar gigante; golpes de galhos em área; chama Kodamas e Dríades. Tochas acesas na arena (com Fogo) o fazem encolher por alguns segundos e ficar vulnerável.
- **Fase 3 — A Floresta Viva (30%–0%):** as árvores da arena fecham o espaço aos poucos; ele se funde à árvore anciã e ataca de dentro dela; queimar as raízes expõe o coração.
- **Tesouro:** o **ouro dos viajantes perdidos** + relíquia proposta **Coroa de Galhos**.

## 5. Cavalos Míticos (`map_horses`)

| ID | Monstro | Origem | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|---|
| `headless_mule` | Mula sem Cabeça | Brasil | Fogo | Água | `charger` | 140 | 16 | Rápida em investida | Rastro de fogo; atordoada após bater numa parede, um jogador pode **arrancar o freio** para derrotá-la na hora |
| `anggitay` | Anggitay | Filipinas | Ar | Terra | `ranged_kite` | 70 | 10 | Rápida | Dispara rajadas pelo chifre e recua galopando |
| `ipotane` | Ipotane | Grécia | Terra | Fogo | `melee_rush` | 90 | 12 | Média | Bandos; coices em área |
| `bakotsu` | Bakotsu | Japão | Terra | Fogo | `swarm` | 40 | 7 | Rápida | Esqueleto que se remonta uma vez se não for destruído com golpe forte |
| `arion` | Arion | Grécia | Água | Ar | `charger` | 160 | 18 | Muito rápida | O mais veloz; investidas seguidas; costuma ser elite |
| `cheollima` | Cheollima | Coreia | Ar | Terra | `flyer` + `charger` | 110 | 14 | Muito rápida | Investidas aéreas em mergulho com sombra no chão como aviso |
| `buraq` | Buraque | Tradição islâmica | Ar | Terra | `flyer` | 100 | 12 | Rápida | **Rever** (ver decisões em aberto) |

### Chefe: Pégaso demoníaco (`demon_pegasus`)
- **Elemento:** Fogo. **Fraco a:** Água.
- **Arena:** planalto no alto de ruínas, aberto para voos e investidas (largo para o Cavaleiro montado).
- **Vida:** 2.500 (solo).
- **Fase 1 — Senhor dos Céus (100%–65%):** voa em círculos e mergulha em investida; rajadas de vento das asas empurram os jogadores.
- **Fase 2 — Manada Corrompida (65%–30%):** pousa e convoca Bakotsus e Arion; relincho que atordoa quem estiver perto (aviso visual).
- **Fase 3 — Asas do Inferno (30%–0%):** as asas pegam fogo; ao voar deixa linhas de fogo no chão; áreas seguras diminuem.
- **Tesouro:** proposta **Rédeas de Ouro do Céu** (relíquia).

## 6. Aves (`map_birds`)

| ID | Monstro | Origem | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|---|
| `harpy` | Harpia | Grécia | Ar | Terra | `flyer` + `melee_rush` | 60 | 10 | Rápida | Agarra e solta jogadores de uma pequena altura (dano de queda); rouba poções |
| `stymphalian` | Ave Estinfália | Grécia | Terra (penas de bronze) | Fogo | `swarm` + `flyer` | 30 | 6 | Rápida | Bandos que disparam penas de metal; **barulho forte** (golpes de área de Terra) espanta o bando por 3 s |
| `strix` | Strix | Roma | Ar | Terra | `flyer` + `caster` | 55 | 11 | Média | Drena vida; enxerga jogadores invisíveis (contra o Ninja) |
| `dark_raven` | Corvo Sombrio | Nórdico | Ar | Terra | `support` + `flyer` | 40 | 5 | Rápida | Marca um jogador: todos os monstros atacam o marcado |
| `roc` | Roca | Oriente Médio | Terra | Fogo | `flyer` + `charger` | 220 | 20 | Média | Sempre elite; carrega rochas e as larga sobre o grupo |

### Chefe: Fênix demoníaca (`demon_phoenix`)
- **Elemento:** Fogo. **Fraco a:** Água.
- **Vida:** 3.000 (solo).
- **Renascer:** ao chegar a 0% pela primeira vez, vira um **ovo de cinzas** por 15 s; o grupo precisa destruir o ovo ou ela renasce com 50% da vida.
- **Fase 1 (100%–50%):** voa pela arena soltando chuva de penas em chamas.
- **Fase 2 (50%–0%):** pousa em um ninho, cria anéis de fogo que se expandem (pular/esquivar).
- **Fase 3 (renascimento):** ovo de cinzas; se renascer, fica mais rápida e mais agressiva.
- **Tesouro:** proposta **Pena da Chama Eterna** (relíquia).

> Depois deste mapa, o Cavaleiro leva o grupo à **Capital Real** e ao Bobo da Corte (`04-1-capital-real.md`).

## 7. Deserto (`map_desert`)

> Dunas sem fim, rotas de caravana abandonadas, um oásis e, soterrado na areia, um **templo de pedra** guardado pela Esfinge. O Bobo da Corte descobriu que **caravanas com o ouro do rei** cruzam o deserto e nunca chegam: os guardas somem, e o ouro vai parar no templo.
> **Mecânica do mapa:**
> - **Tempestade de areia** (a cada alguns minutos, com aviso no céu): visão curta e vento que empurra; ficar atrás de rochas protege.
> - **Calor do dia:** longe da sombra, a recuperação de recurso cai 30%; o **oásis** e as sombras restauram.
> - **Areia movediça** em pontos marcados (lento; afunda se ficar parado).

| ID | Monstro | Origem | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|---|
| `ghoul` | Ghul | Folclore árabe pré-islâmico | Terra | Fogo | `swarm` | 40 | 8 | Rápida | Saem dos túmulos da rota de caravanas; alguns aparecem como **hienas** e viram ghuls ao chegar perto; chamam o jogador pelo nome (som de aviso) |
| `scorpion_man` | Homem-Escorpião | Mesopotâmia | Terra | Fogo | `melee_rush` | 120 | 14 | Média | Pinças e ferrão: o ferrão aplica veneno forte; casca dura (-20% dano físico) |
| `death_worm` | Verme da Morte | Mongólia | Ar | Terra | `ambush` | 100 | 15 | Rápida (embaixo da areia) | Anda sob a areia (rastro na superfície como aviso); sai e solta **descarga elétrica** em área (`shocked`) |
| `manticore` | Manticora | Pérsia | Fogo | Água | `ranged_kite` | 150 | 16 | Média | Atira **espinhos venenosos** da cauda em leque; rugido que assusta; costuma ser elite |
| `lamassu` | Lamassu | Assíria | Ar | Terra | `charger` + `flyer` | 260 | 20 | Média | Sempre elite; touro alado de cabeça humana; investida e pisão que derruba (`knocked_down`) |

### Chefe: Esfinge demoníaca (`demon_sphinx`)
- **Conceito:** a guardiã que devorava quem não respondia seu enigma. Fez pacto com um demônio para guardar o ouro das caravanas no templo soterrado.
- **Arena:** salão do templo de pedra, com quatro estátuas e areia que escorre do teto.
- **Vida:** 3.500 (solo).
- **Elemento:** Ar (vento e tempestade de areia). **Fraca a:** Terra.
- **Fase 1 — A Guardiã (100%–65%):** voa baixo e ataca com garras; levanta redemoinhos de areia que andam pela arena.
- **Fase 2 — O Enigma (65%–30%):** pousa e **propõe um enigma** (texto na tela, nos 3 idiomas). Cada uma das **quatro estátuas** mostra uma resposta; os jogadores têm 30 s para golpear a estátua certa. **Acertou:** ela fica atordoada e recebe +50% de dano por 10 s. **Errou ou o tempo acabou:** tempestade de areia na arena inteira. Repete a cada 25 s nesta fase (enigmas sorteados de uma lista de ~10, proposta).
- **Fase 3 — Areia e Vento (30%–0%):** o teto do templo começa a desabar (areia cai em pontos com aviso, a arena diminui); ela fica mais rápida e chama Ghuls.
- **Tesouro:** o **ouro das caravanas do rei** + relíquia proposta **Olho da Esfinge**.

## 8. Águas (`map_waters`)

> Chão molhado e água rasa por todo lado: em certas áreas, monstros e jogadores ficam `soaked` (combos de Ar são fortes aqui).

| ID | Monstro | Origem | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|---|
| `iara` | Iara | Brasil | Água | Ar | `caster` | 70 | 12 | Média | Canto que **encanta** e puxa jogadores para a água (aliado acerta para libertar) |
| `siren` | Sereia | Grécia | Água | Ar | `support` | 55 | 8 | Média | Canto que cura outros monstros e deixa jogadores lentos |
| `kelpie` | Kelpie | Escócia | Água | Ar | `ambush` + `charger` | 120 | 15 | Rápida | Surge da água e arrasta quem atingir |
| `kappa` | Kappa | Japão | Água | Ar | `melee_rush` | 80 | 11 | Média | Forte enquanto a água do prato da cabeça não derrama: golpe que derruba (`knocked_down`) faz derramar e ele fica fraco (-50% dano) |
| `drowned` | Afogado | Folclore marinho | Terra (lodo) | Fogo | `swarm` | 35 | 6 | Lenta | Marinheiros afogados saindo dos naufrágios em grupos |

### Chefe: Kraken demoníaco (`demon_kraken`)
- **Elemento:** Água. **Fraco a:** Ar.
- **Arena:** convés de um navio naufragado preso entre rochas, cercado pela água.
- **Vida:** 4.000 (solo).
- **Tentáculos:** 6 tentáculos saem da água e atacam separadamente; destruir tentáculos faz o corpo emergir e ficar vulnerável.
- **Fase 1 (100%–65%):** tentáculos batem no convés (marcas de aviso) e agarram jogadores.
- **Fase 2 (65%–30%):** alaga o convés (todos `soaked`) e convoca Afogados; jato de tinta que escurece a tela por 2 s.
- **Fase 3 (30%–0%):** o navio começa a afundar; a área seca diminui; tentáculos voltam mais rápidos.
- **Tesouro:** **Coração do Abismo** (relíquia, proposta) + parte do ouro do rei, levada para o fundo do mar.

## 9. Pântano (`map_swamp`)

> Charcos de água negra, neblina que não se dissipa, árvores mortas, túmulos antigos afundados na lama e, no centro, um **lago escuro e sem fundo**. Lá vive **Grendel**, o monstro que odeia a luz e o barulho dos homens — e, no fundo do lago, a **Mãe de Grendel**, sobre um tesouro de reis antigos e agora o ouro do rei que o Bobo procura.
> **Mecânica do mapa:**
> - **Atoleiros:** lama que deixa lento (-40% velocidade) e impede a esquiva; o Cavaleiro precisa desmontar.
> - **Neblina:** visão média; luzes de Fogo-fátuo aparecem nela (seguir leva a atoleiros).
> - **Água parada** em várias áreas: `soaked` (Ar forte aqui).

| ID | Monstro | Origem | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|---|
| `will_o_wisp` | Fogo-fátuo | Europa | Fogo | Água | `trickster` + `flyer` | 35 | 9 | Rápida | Luzes que flutuam na neblina e atraem jogadores para atoleiros; explodem em chamas quando alguém chega perto |
| `kikimora` | Kikimora do Pântano | Eslavo | Terra (musgo e lodo) | Fogo | `support` | 60 | 6 | Lenta | Pequena e coberta de musgo; cobre os monstros próximos com lodo (escudo que absorve dano) |
| `rusalka` | Rusalka | Eslavo | Água | Ar | `caster` | 75 | 12 | Média | Dança na margem e **encanta** (o jogador caminha até a água; aliado acerta para libertar) |
| `draugr` | Draugr | Nórdico | Terra | Fogo | `melee_rush` | 140 | 16 | Lenta | Morto-vivo dos túmulos afundados; fica **maior e mais pesado** abaixo de 50% de vida (+30% dano, mais lento) |
| `bunyip` | Bunyip | Austrália (aborígene) | Água | Ar | `ambush` | 200 | 19 | Média (rápida no bote) | Escondido na água parada; **rugido** antes do bote (aviso); costuma ser elite |

### Chefe: Grendel demoníaco e a Mãe de Grendel (`demon_grendel`, `grendel_mother`)
- **Conceito:** o monstro dos pântanos da lenda de Beowulf, que odiava a luz e a música do salão dos homens. Sua mãe vive no fundo do lago negro, sobre um tesouro e uma espada feita por gigantes. Os dois fizeram pacto com um demônio, que lhes deu o ouro do rei para guardar.
- **Arena:** margem do lago negro, com ruínas de um salão antigo; na fase 2, parte da arena é a água rasa do lago.
- **Vida:** 4.500 (solo) no total (Grendel 2.500 + Mãe 2.000).
- **Elemento:** os dois **Água** (o pântano e o lago). **Fracos a:** Ar (raio = luz e trovão, o que Grendel mais odeia).
- **Fase 1 — O Monstro do Salão (Grendel 100%–0%):** agarra e arremessa jogadores; investidas pela margem; golpes de Ar o deixam atordoado por 1 s (ele odeia a luz e o barulho).
- **Fase 2 — A Mãe no Lago (Mãe 100%–40%):** ferido, Grendel foge para o lago; a **Mãe** sai da água furiosa: ataques vindos de baixo d'água (bolhas como aviso), puxa jogadores para o fundo (aliado acerta para soltar); a margem é `soaked`.
- **Fase 3 — A Vingança (Mãe 40%–0%):** Grendel volta enfurecido para ajudar a Mãe (com pouca vida); a água do lago sobe e a área seca diminui. Proposta: na arena aparece a **Espada dos Gigantes** cravada numa pedra — quem a pegar causa +50% de dano à Mãe por 15 s (como na lenda).
- **Tesouro:** o **tesouro do lago** + parte do ouro do rei + relíquia proposta **Espada dos Gigantes**.

## 10. Serpentes (`map_serpents`)

> Selva quente, templos em ruínas tomados por serpentes e, na costa, um **templo meio afundado no mar**, onde Jörmungandr, a Serpente do Mundo, subiu das profundezas.

| ID | Monstro | Origem | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|---|
| `boitata` | Boitatá | Brasil | Fogo | Água | `charger` | 130 | 16 | Rápida | Cobra de fogo de olhos enormes e brilhantes; deixa rastro de fogo |
| `basilisk` | Basilisco | Europa | Terra | Fogo | `caster` | 100 | 12 | Lenta | Olhar petrificante: quem fica de frente para ele por 2 s fica `stunned` (aviso: brilho nos olhos) |
| `naga` | Naga | Índia | Água | Ar | `melee_rush` | 90 | 13 | Média | Guardiões dos templos, com lâminas |
| `amphisbaena` | Anfisbena | Grécia | Terra | Fogo | `swarm` | 40 | 7 | Rápida | Serpente de duas cabeças; cortada, vira duas menores (uma vez) |
| `wyvern` | Serpe (Wyvern) | Europa | Ar | Terra | `flyer` | 150 | 17 | Média | Dragão de duas patas; cauda venenosa e cuspe em área |
| `hydra` | Hidra | Grécia | Água | Ar | `caster` | 260 | 18 | Lenta | Sempre elite; cabeças cortadas crescem em dobro, **a menos que o pescoço seja queimado** (golpe de Fogo logo após cortar) |

### Chefe: Jörmungandr demoníaco (`demon_jormungandr`)
- **Elemento:** Água (a serpente do mar). **Fraco a:** Ar (raios, como os de Thor).
- **Arena:** templo meio afundado no mar, com o corpo da serpente passando por baixo e em volta.
- **Vida:** 5.000 (solo).
- **Corpo gigante:** a cabeça aparece em pontos diferentes; partes do corpo atravessam a arena como paredes que esmagam.
- **Fase 1 (100%–65%):** cabeça surge e morde; corpo varre a arena (pular/esquivar).
- **Fase 2 (65%–30%):** veneno no chão (poças que se espalham); convoca Anfisbenas.
- **Fase 3 (30%–0%):** a serpente se enrola na arena, que diminui a cada volta; cabeça em fúria.
- **Tesouro:** **Escama do Mundo** (relíquia, proposta) + a última parte do ouro do rei. **Descoberta:** inscrições e um portal no templo mostram que todo o ouro vai para o Inferno, para Lúcifer.

## 11. Inferno (`map_hell`) — mapa final

| ID | Monstro | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|
| `succubus` | Súcubo | Fogo | Água | `caster` + `flyer` | 60 | 12 | Média | Encanta jogadores (aliado acerta para libertar), drena vida; serva direta de Lúcifer |
| `hell_echo` | Ecos dos chefes | Do chefe original | Do chefe original | variado | — | — | — | Versões menores dos chefes derrotados aparecem como elites |

### Chefe final: Lúcifer (`lucifer`)
- **Conceito:** o anjo caído **ganancioso, que quer todo o ouro do mundo**. Usou os demônios para tomar terras e tesouros em segredo, sem que a família real soubesse. **Sequestrou o Bobo da Corte** por passar informações aos mercenários e o mantém preso numa **gaiola de ouro sobre o trono**.
- **Arena:** trono no coração do inferno, sobre montanhas de ouro, cercado por lava e correntes; a gaiola do Bobo fica acima do trono.
- **Vida:** 6.000 (solo).
- **Muda de elemento a cada fase**, para exigir um grupo com elementos variados (ou várias Poções Elementais). A **cor da aura** mostra o elemento do momento e o ícone ao lado da vida muda junto.
- **Fase 1 — Anjo Caído (100%–70%) — Ar:** aparência quase angelical, asas negras, luz e vento; golpes amplos e investidas aéreas. **Fraco a Terra.**
- **Fase 2 — Corte Infernal (70%–35%) — Fogo:** volta ao trono em chamas e convoca Súcubos e ecos dos chefes derrotados; chuva de fogo e de **moedas de ouro derretido** com marcas no chão. **Fraco a Água.**
- **Fase 3 — Forma Verdadeira (35%–0%) — todos os elementos:** demônio gigante que **alterna entre Água, Fogo, Terra e Ar a cada 15 s** (aviso 2 s antes, com a aura piscando na próxima cor); a arena desmorona e as áreas seguras diminuem. **Fraco ao elemento que vence o do momento.** O Bobo grita dicas da gaiola (qual será o próximo elemento — proposta).
- **Final:** derrotado Lúcifer, a gaiola cai e o grupo **liberta o Bobo**.
- **Tesouro:** **todo o ouro que Lúcifer acumulou** — o maior tesouro do mundo (`06-mundo-e-historia.md`).

## 12. Modificadores de elite

Uma elite recebe 1 modificador nos mapas 1 a 4 e 2 modificadores a partir do mapa 5.

| ID | Modificador | Efeito |
|---|---|---|
| `fast` | Veloz | +50% velocidade de movimento e ataque |
| `vampiric` | Vampírico | Cura-se com parte do dano causado |
| `hellfire_trail` | Rastro Infernal | Deixa fogo no chão por onde passa |
| `cursed` | Amaldiçoado | Ataques reduzem a cura recebida pelo alvo |
| `shielded` | Blindado | Escudo sombrio que precisa ser quebrado antes da vida |
| `summoner` | Invocador | Chama 2 monstros comuns a cada 10 s |
| `explosive` | Explosivo | Explode ao morrer, causando dano em área |
| `toxic` | Tóxico | Deixa poças de lodo tóxico ao andar (comum no Esgoto e no Pântano) |

## 13. Drops (resumo)

| Categoria | Ouro | Chance de item | Raridade mínima |
|---|---|---|---|
| Comum | Baixo | 10% | Comum |
| Elite | Médio | 100% (1 a 2 itens) | Mágico |
| Mini-chefe | Alto | 100% (2 a 3 itens) | Raro garantido |
| Chefe | Tesouro do covil | Ver `05-itens-e-loot.md`, seção 3 | Lendário garantido |

Materiais raros por família: cauda da Rainha dos Ratos, glândula de Sapo Ácido, couro de Jacaré do Esgoto, presa de Warg, olho em brasa do Cão Negro, seda de Jorōgumo, pelo do Mapinguari, freio da Mula sem Cabeça, chifre de Anggitay, pena de bronze Estinfália, pena negra de Pégaso, ferrão de Homem-Escorpião, espinho de Manticora, escama de Kelpie, pérola negra da Iara, prato do Kappa, musgo de Kikimora, dente de Bunyip, olho de Basilisco, escama de Hidra.

## 14. Decisões em aberto

- **Buraque:** é uma figura sagrada no Islã (a montaria do profeta Maomé). Colocá-lo como monstro corrompido a ser morto pode ofender jogadores muçulmanos. Manter, ou trocar por **Nuckelavee** (cavalo-demônio das Órcades sem pele)?
- **Bakotsu:** confirmar a lenda (proposta: esqueleto de cavalo reanimado).
- Qual demônio fez o pacto com a Rainha dos Ratos? Ele aparece? (ideia: **Mamon**, demônio da ganância, servo de Lúcifer, atraído pelo ouro da guerra; pode voltar como eco no Inferno)
- "Fúria da Rainha" (cada rato morto deixa a chefe mais forte): manter?
- Enigmas da Esfinge: lista de ~10 enigmas clássicos (ex.: "o que anda com quatro pés de manhã, dois à tarde e três à noite?") — escrever na fase de produção?
- Grendel e a Mãe: luta em dupla (proposta) ou só a Mãe como chefe e Grendel como mini-chefe?
- Ordem dos 10 mapas: manter a proposta?
- Monstros reaparecem (respawn) ao voltar para uma área já limpa?
- Haverá um modo de dificuldade maior para jogar a campanha de novo?
