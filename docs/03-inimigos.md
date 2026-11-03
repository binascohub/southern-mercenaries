# Inimigos — Monstros e Demônios

> Versão 11 · 2026-10-30 · Complementa `01-escopo.md`, `02-0-elementos.md`, `03-1-bestiario.md`, `03-2-areas.md`, `05-itens-e-loot.md` e `06-mundo-e-historia.md`
> Este arquivo traz a **mecânica** dos monstros. As **lendas** e as **pistas de fraqueza** estão em `03-1-bestiario.md`. A divisão de cada mapa em áreas está em `03-2-areas.md`.
> Números são propostas iniciais para balancear depois. Vida e dano são para nível 1 e escalam com o nível da área; a vida dos chefes ainda recebe o **fator de chefe** de `13-balanceamento.md`, seção 2.4.

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
| 1 | 2 | `map_sewers` | **Esgoto de Tortuga** | Túneis, canais de lixo, câmaras alagadas sob a cidade | Animais contaminados | Terra | **Feiticeiro-Aranha** (pacto com um demônio) | Terra | Fogo |
| 2 | 2 | `map_ruins` | **Ruínas do Reino do Arqueiro** | Capital em ruínas, vilas queimadas, campos de batalha, cemitérios, floresta nevada | Lobos e cães míticos | Terra | **Cérbero** | Fogo / Água / Terra (uma por cabeça) | Água / Ar / Fogo |
| 3 | 2 | `map_forest` | **Floresta Escura** | Mata fechada sem luz do sol, árvores gigantes, teias, cachoeira, clareiras | Espíritos e feras da floresta | Terra | **Leshy** | Terra | Fogo |
| 4 | 3 | `map_desert` | **Deserto** | Dunas, rotas de caravana, oásis, templo de pedra soterrado | Feras híbridas do deserto | Fogo | **Esfinge** | Ar | Terra |
| 5 | 3 | `map_swamp` | **Pântano** | Charcos, atoleiros, neblina, túmulos afundados, lago negro | Mortos e espíritos do pântano | Água | **Grendel** (e sua Mãe) | Água | Ar |
| 6 | 4 | `map_hell` | Inferno | Inferno, rios de lava e de ouro | Súcubos e ecos dos demônios | Fogo | **Lúcifer** | **Muda a cada fase** (Ar → Fogo → todos) | Terra → Água → o que vence o elemento do momento |

- O **Esgoto** é o primeiro mapa: fica **embaixo de Tortuga** e é acessado por um bueiro na Rua Principal (não precisa de barco).
- As **Ruínas do Reino do Arqueiro** são o segundo: continuação direta da história do Esgoto (o resto do tesouro real ficou lá).
- Mapas 1–3 saem de **Tortuga** (missões da taverna); mapas 4–5 saem da **Capital Real** (missões do Bobo da Corte); o 6 é o resgate do Bobo.
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
- **Por número de jogadores:** vida +60% e dano +10% por jogador extra; **o loot não escala** (decisão do autor, `07-rede.md`). Tabela completa em `13-balanceamento.md`, seção 2.5.
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

### Encontros por exploração (sem ondas)
Decisão do autor: **o jogo não é feito de ondas (waves)**. O jogador **explora a área, revela o mapa e mata os monstros que encontra**, como em Dark Alliance.
- **Monstros ficam posicionados no mapa**, à mão, em **grupos de encontro** (um pequeno bando numa sala, uma patrulha num corredor, um elite guardando um baú). Nada surge do nada em ciclos.
- Cada grupo fica **dormindo** até um jogador chegar perto (raio de despertar, ~15 m) ou ser visto; ao acordar, **alerta os vizinhos** (`Aggro em grupo`). Quem não foi alertado continua dormindo.
- **Emboscadas** (`ambush`) são parte do desenho da área: o monstro escondido salta quando o jogador chega no ponto marcado; acontece uma vez.
- **Armadilhas de encontro** (alavanca, baú, altar) podem despertar um grupo extra **uma única vez**; nunca em loop.
- **Sem respawn (decidido):** monstros mortos **ficam mortos**, inclusive ao sair da área e voltar pelo portal ou checkpoint; a área só é reiniciada numa nova campanha. Isso mantém o ritmo de exploração e ajuda o desempenho.
- **Elites e mini-chefes** ficam em lugares fixos, com nome e pista (sala, ponte, cruzamento) e guardam loot.
- **Chefes** têm arena própria, fechada ao começar a luta; podem **chamar poucos ajudantes** como parte de uma fase (ex.: filhotes da Rainha), nunca ondas contínuas ou cronometradas.
- **Mapa que se revela:** o jogador começa a área sem ver o mapa; ele é **revelado conforme explora** (seção de interface, `09-interface.md`). Áreas escondidas e segredos recompensam quem vasculha os cantos.
- **Ritmo:** pouca coisa ao mesmo tempo (câmera próxima, ~40 entidades ativas no máximo), muita exploração entre os encontros.

### Desempenho (requisito do escopo)
- Limite de **~40 entidades ativas** na área (monstros + animais amigos do Invocador).
- Monstros longe dos jogadores ficam "dormindo" (sem IA nem física).
- Reaproveitar instâncias (pooling) em vez de criar e destruir.
- IA processada no servidor (host); clientes só recebem posição, animação e vida.
- **Cada família compartilha esqueleto e animações**: esgoto (roedor, réptil, morcego), ruínas (quadrúpede canino), floresta (humanoide pequeno, gigante peludo, aranha), cavalos (quadrúpede equino), aves (ave), deserto (quadrúpede felino/touro alado, escorpião, verme), águas (humanoide aquático + tentáculos), pântano (humanoide morto-vivo, gigante), serpentes (serpente + dragão).

## 2. Esgoto de Tortuga (`map_sewers`)

> Túneis escuros e estreitos sob a cidade, canais de lixo e água podre, câmaras alagadas e restos de uma passagem secreta da época da guerra. Os animais que viviam ali foram **contaminados** pelo pacto do Feiticeiro-Aranha com um demônio e viraram monstros.
> **Mecânica do mapa:** poças de **lodo tóxico** que causam dano ao longo do tempo a quem pisar; algumas áreas alagadas deixam todos `soaked`.

| ID | Monstro | Elemento | Fraco a | Comportamento | Vida | Dano | Velocidade | Mecânica |
|---|---|---|---|---|---|---|---|---|
| `plague_rat` | Rato Pestilento | Terra | Fogo | `swarm` | 20 | 4 | Rápida | Enxames de 8 a 12; mordida aplica veneno leve. São os **filhotes da Rainha** |
| `mutant_rat` | Ratazana Mutante | Terra | Fogo | `melee_rush` | 110 | 12 | Média | Do tamanho de um cão; investida curta; costuma ser elite |
| `plague_bat` | Morcego Pestilento | Ar | Terra | `flyer` + `swarm` | 25 | 5 | Rápida | Bandos que saem do teto; guinchos que deixam lento |
| `acid_toad` | Sapo Ácido | Água | Ar | `ranged_kite` | 50 | 9 | Lenta | Cospe ácido à distância, que deixa poça tóxica no chão |

### Fúria do Feiticeiro (mecânica do mapa — proposta)
- Cada **Rato Pestilento** (familiar dele) morto no mapa deixa o Feiticeiro mais furioso: **+1% de dano** na luta final, até **+20%**.
- O jogador pode escolher limpar o mapa (mais experiência e loot) ou evitar enxames (luta final mais fácil).

### Chefe: Feiticeiro-Aranha (`demon_rat_queen`)
- **Conceito:** o **alquimista da corte do reino derrotado**, deixado no esgoto pelos fundadores de Tortuga para guardar o tesouro roubado. Quando o povo envenenou e queimou seus ratos, ele **fez um pacto com um demônio**: virou um homem de capuz com **oito patas de aranha** nas costas e contaminou todos os animais do esgoto, que passaram a servi-lo como familiares. Dorme sobre o **Tesouro Perdido da Guerra** com a **coroa do rei perdido** guardada no manto.
- **Visual:** homem de capuz e manto escuro com barra vermelha, braços finos e pálidos, **oito patas de aranha** saindo das costas, olho vermelho brilhando no peito; ao redor, os ratos contaminados andam em bando (modelo: Wizard, piacenti, CC BY-SA 3.0).
- **Arena:** câmara alagada e ampla no fundo do esgoto, onde está o ninho sobre o tesouro.
- **Vida:** 1.000 (solo).
- **Elemento:** Terra. **Fraco a:** Fogo.
- **Fase 1 — O Alquimista Furioso (100%–60%):** investidas e golpes em área; açoita com as patas; a cada 20 s chama um enxame de Ratos Pestilentos (seus familiares).
- **Fase 2 — Os Familiares (60%–25%):** recua para o covil e protege 3 **ninhos de familiares**; enquanto houver ninhos, regenera vida. O grupo precisa destruí-los (Fogo causa dano dobrado).
- **Fase 3 — O Pacto (25%–0%):** o demônio toma conta do corpo dele: olhos e boca em chamas negras, abre comportas e **alaga a arena** (todos `soaked`); gás tóxico sai dos canos (áreas de dano com aviso).
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

Materiais raros por família: cauda do Feiticeiro-Aranha, glândula de Sapo Ácido, couro de Jacaré do Esgoto, presa de Warg, olho em brasa do Cão Negro, seda de Jorōgumo, pelo do Mapinguari, freio da Mula sem Cabeça, chifre de Anggitay, pena de bronze Estinfália, pena negra de Pégaso, ferrão de Homem-Escorpião, espinho de Manticora, escama de Kelpie, pérola negra da Iara, prato do Kappa, musgo de Kikimora, dente de Bunyip, olho de Basilisco, escama de Hidra.

## 14. Decisões em aberto

- **Bakotsu:** confirmar a lenda (proposta: esqueleto de cavalo reanimado).
- Qual demônio fez o pacto com o Feiticeiro-Aranha? Ele aparece? (ideia: **Mamon**, demônio da ganância, servo de Lúcifer, atraído pelo ouro da guerra; pode voltar como eco no Inferno)
- "Fúria do Feiticeiro" (cada rato morto deixa a chefe mais forte): manter?
- Enigmas da Esfinge: lista de ~10 enigmas clássicos (ex.: "o que anda com quatro pés de manhã, dois à tarde e três à noite?") — escrever na fase de produção?
- Grendel e a Mãe: luta em dupla (proposta) ou só a Mãe como chefe e Grendel como mini-chefe?
- Ordem dos 10 mapas: manter a proposta?
- Rejogar áreas (Expedição) e dificuldades: propostos em `15-modos.md`; novo jogo começa do zero (decidido).
