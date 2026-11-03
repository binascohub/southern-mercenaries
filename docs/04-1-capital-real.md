# Capital Real — a cidade do Cavaleiro

> Versão 4 · 2026-10-30 · Segunda cidade-base da campanha. Complementa `04-tortuga-e-missoes.md`, `06-mundo-e-historia.md` e `02-3-cavaleiro.md`
> A cidade se chama **Aurenhold**, capital do reino de **Aurenval** (`06-mundo-e-historia.md`, seção 3). Números são propostas para revisar.

## 1. Conceito

A **Capital Real** é a cidade do reino que **venceu a guerra** — o reino de Dorian e Dália. É o oposto de Tortuga: **rica, limpa, cheia de leis, guardas e nobres**, com um rei no trono e um castelo no alto da cidade.

- É a **segunda cidade-base** do jogo, liberada **no meio da campanha** (depois do mapa 5, ver seção 7).
- Tem **comércio mais elevado**: itens melhores e mais caros que os de Tortuga.
- As **novas missões principais** passam a ser entregues pelo **Bobo da Corte**, que vive no castelo e quer descobrir **onde a família real esconde seus tesouros**.
- Depois de liberada, o grupo pode viajar entre **Tortuga e a Capital** pelos portais.

> **No jogo hoje (primeira passada):** a Capital (`capital_01_aurenhold`) já existe como mapa-cidade (praça do portão, avenida e pátio do castelo) com os 10 guardas, e é o destino do **Forte** (o último mapa da cadeia atual). A ordem no jogo é Tortuga → Floresta → Ruínas → Cemitério → Floresta Escura → Forte → Capital; a ordem narrativa abaixo (depois do mapa 5) continua sendo a proposta final.

### Como o grupo chega à Capital
- Depois do mapa 5 (Aves), as pistas da taverna acabam. É o **Cavaleiro** (Dorian ou Dália) quem conta que **sabe de um Bobo da Corte, no castelo da Capital, que sabe de coisas** — segredos da família real, ouro escondido, rumores que ninguém mais ouve.
  - **Dorian:** conheceu o Bobo nos tempos da guarda do castelo; ele era o único que sabia do romance com a princesa e nunca contou ao rei.
  - **Dália:** cresceu com o Bobo fazendo graça para ela nos salões; ele era quem contava os segredos do castelo para a princesinha.
- **No co-op**, se ninguém joga com o Cavaleiro, ou **no solo**, o Cavaleiro aparece como **NPC em Tortuga** (como na abertura) e conta a mesma coisa.

> **Dorian:** "Tem um homem no castelo que sabe de tudo. Ninguém presta atenção num bobo — e é por isso que ele ouve tudo. Ele me deve um favor. Se alguém sabe onde tem mais ouro, é ele."
>
> **Dália:** "Quando eu era criança, o Bobo me contava todos os segredos do castelo. Se tem alguém que sabe onde o ouro está escondido, é ele. Só não esperem que os nobres me recebam bem."

### Contraste com Tortuga
| | Tortuga | Capital Real |
|---|---|---|
| Governo | Sem rei, sem regras | Rei, nobreza, guardas e leis |
| Comércio | Ilegal, piratas, mercado negro | Oficial, lojas finas, guildas |
| Itens | Comuns a raros; ofertas piratas | Raros a únicos; mais caros |
| Quem dá missões | Taverna (bêbado, taberneira, visitantes) | Bobo da Corte |
| Clima | Sujo, perigoso, neblina | Rico, iluminado, mas frio e falso |

## 2. Mapa da cidade

Seguindo o padrão de Tortuga: **área externa** com o comércio ao ar livre e **um único lugar especial** — o **pátio do castelo**, onde fica o Bobo da Corte.

```
                 [CASTELO] (fechado)
                     │
               [Pátio do Castelo] ← Bobo da Corte
                     │
  ═══════════ AVENIDA REAL ═══════════════════════
    Mercado Real   Armeiro Real   Alfaiate de Armaduras
    Joalheiro      Alquimista     Ferreiro Real
    Banco (baú)    Estábulo Real
  ════════════════════╪═══════════════════════════
                      │
                [Portal Real] → portal para Tortuga e para os mapas
```

### Locais
| ID | Local | Função |
|---|---|---|
| `royal_market` | **Mercado Real** | Itens **melhores e mais caros**: sempre de raridade mágica ou maior; estoque maior que o pirata (6 a 10 itens), muda a cada volta |
| `royal_armory` | Armeiro Real | Armas raras garantidas do nível do jogador; às vezes únicas. Vende armas de **cobre e prata** (comuns e mágicas) |
| `royal_tailor` | Alfaiate de Armaduras | Armaduras e roupas finas (visual nobre); raras garantidas; peças de **cobre e prata** |
| `jeweler` | **Joalheiro** | Compra **valiosos** por um preço **fixo e mais alto** (110% do valor base, sem variação) e vende anéis e amuletos raros |
| `alchemist` | Alquimista | Poções de vida/recurso maiores e **Poções Elementais Refinadas** (duram 2 expedições; mais caras) |
| `royal_smith` | Ferreiro Real | Crafting avançado: **adicionar encaixes** a itens e **reforjar** um afixo; **refino** com pergaminhos de **Cobre e Prata** (e Ouro sob encomenda, com materiais raros) — `05-1-refino.md` |
| `royal_stables` | Estábulo Real | Bardas finas para o cavalo do Cavaleiro; trocar a pelagem do cavalo |
| `training_yard` | **Campo de treino** | Quartel da Academia Militar (ao ar livre): mesmos bonecos e regras da área de treinamento de Tortuga (`04-tortuga-e-missoes.md`, seção 5.2), com bonecos de visual militar |
| `voodoo_priest` | **Viajante do Tempo (teleporte)** | Mesmo serviço de Tortuga: portal para checkpoints salvos mediante ouro e venda do Patuá de Retorno (`04-tortuga-e-missoes.md`, seção 5.1) |
| `bank` | Banco | Acesso ao mesmo baú de Tortuga (baú compartilhado entre as cidades) |
| `castle_courtyard` | **Pátio do Castelo** | Onde o **Bobo da Corte** entrega as missões |
| `royal_portal` | **Portal Real** | Portal de pedra no cais do Porto Real; viagem para Tortuga e para os mapas liberados (mesma janela do Portal de Tortuga, `04-tortuga-e-missoes.md`, seção 5). Os mapas 6 a 10 saem daqui |

### Preços
| Item | Tortuga | Capital Real |
|---|---|---|
| Itens à venda | Rua Principal: comuns; Mercado Pirata: mágicos a únicos, 3x o valor | Mágicos a únicos, **4x o valor**, com mais escolha e mais itens da classe do jogador |
| Venda de valiosos | Piratas: 80% a 120% (varia) | Joalheiro: 110% fixo |
| Poção Elemental | Normal (1 expedição) | Refinada (2 expedições), o dobro do preço |

## 3. O Bobo da Corte

| Campo | Valor |
|---|---|
| ID | `court_jester` |
| Onde fica | Pátio do castelo |
| Aparência | Roupa de bobo em losangos desbotados, guizos, máscara meio sorridente, meio triste; olhos atentos demais |
| Personalidade | Engraçado em público, frio e calculista em particular; sabe tudo o que acontece no castelo |
| Objetivo | **Descobrir onde a família real esconde seus tesouros** |
| Ligação com o Cavaleiro | Velho conhecido de Dorian (guarda do castelo) e de Dália (princesa) |

### Onde ele fica (como está no jogo)
- O Bobo vive na **Sala do Rei** (`throne_room`), atrás do pátio do castelo: sala de madeira com o trono ao fundo, estandartes, uma mesa de centro com velas e **dois conjuntos de sofás** (Sofa-group 5, CC-BY-SA 3.0). Ele tem a missão do **Banquete do rei** (Carne Selvagem do Alfa da Matilha, `04-tortuga-e-missoes.md`); as missões principais dele entram com o Ato 3. Duas **mesas fartas** (maçãs, bananas e carne, Food Props, CC-BY 3.0) ocupam o centro da sala. Um **lustre** (Chandelier, CC0) pende sobre elas. A leste fica o **quarto do rei** (`king_bedroom`), com quatro camas (Beds, mattresses, CC-BY-SA 3.0) e baús. No **pátio de treino** há dois **aparelhos de treino** giratórios (Training Device, CC-BY-SA 3.0) junto dos bonecos.
- A Capital tem ainda: a **igreja** (`church`, a oeste da sala do rei), com o **altar** (Podium, CC-BY-SA 3.0), a cruz, 18 cadeiras em fileiras e o **Padre** atrás do altar, que dá as missões das relíquias do último rei de Veldmark (`06-mundo-e-historia.md`); as **sentinelas do castelo** (Brigand, parado de guarda) na porta do pátio; as **casas** (Modular Medieval House Pack 06) ao norte da Avenida; a **mesa de fartura** (frutas, melancias e carne) e a **carroça de melancias** (A watermelon, CC0) na Avenida; o **pátio de treino** e as **barracas de comércio** (movidas de Tortuga).

### Papel no jogo
- A partir da Capital, o Bobo **substitui a taberneira** como quem conta as **missões principais**.
- Ele finge ser só um palhaço, mas ouve tudo nos salões do castelo. Descobre que os tesouros da família real estão **sumindo**: estão sendo levados para lugares que **só os demônios guardam** — e a família real não sabe de nada.
- Cada missão dele mistura **intriga da corte + lenda da criatura + pista de fraqueza** (mesma regra das histórias da taverna, `03-1-bestiario.md`).
- Ele também entrega **missões secundárias de intriga** (`intrigue`): espionar um nobre, recuperar uma carta, encontrar um mapa escondido num mapa já visitado.
- É ele quem arranja o **salvo-conduto** para Dorian (expulso da cidade) entrar.

### Exemplo de fala
> **Bobo da Corte (primeira missão, Deserto):** "Ah, os famosos mercenários de Tortuga! Que honra, que honra… *(baixa a voz)* Escutem: o ouro do rei está sumindo dos cofres, e ninguém no castelo percebeu. Segui a trilha: as caravanas descem para dentro da areia, perto de um templo de pedra. Alguém está juntando todo o ouro do mundo — e não é o rei. Tragam o que estiver lá, e eu conto o resto. Ah — a guardiã faz uma pergunta e é feita de vento do deserto. Só a pedra segura o vento."

### O que está por trás: Lúcifer
- **Lúcifer é ganancioso e quer todo o ouro do mundo.** Por meio dos demônios, ele vem **dominando os tesouros e as terras em segredo**, sem que a família real saiba — cada chefe demoníaco guarda uma parte do que ele está acumulando.
- O Bobo é o único no castelo que percebe. Ao passar as informações aos mercenários, ele **atrapalha os planos de Lúcifer**.

### O sequestro do Bobo (final do Ato 3)
- Depois do mapa 9, quando o grupo volta à Capital, **o Bobo sumiu**. No pátio ficam só a **máscara dele**, os guizos e marcas de fogo no chão.
- Uma Súcubo (ou um bilhete escrito em brasa) deixa o recado: Lúcifer levou o Bobo para o Inferno por estar ajudando os mercenários.
- **Missão final:** ir ao **Inferno libertar o Bobo**. Os mercenários não vão por bondade: **o Bobo é quem sabe onde há mais tesouros**. De quebra, há todo o ouro que Lúcifer acumulou.
- A última pista de fraqueza vem das **anotações escondidas do Bobo**, encontradas no pátio junto da máscara (`03-1-bestiario.md`, Lúcifer).

### O gancho final
- Libertado, o Bobo comenta que **ouviu falar de um reino ainda maior, do primo da família real** — o que abre a **continuação do jogo** (`06-mundo-e-historia.md`, seção 9).

### Origem do Bobo (decidido)
- O Bobo é **natural da própria Capital** e **filho de um ferreiro** da cidade. Cresceu entre forjas e salões, aprendeu a ouvir sem ser notado e virou o bobo da corte.

## 4. Os heróis na Capital

| Herói | Situação na Capital |
|---|---|
| **Dorian** | **Expulso** pelo rei e proibido de voltar. Foi ele quem levou o grupo até o Bobo; entra com o **salvo-conduto arranjado pelo Bobo**. Pode ver a princesa de longe (cena/proposta) |
| **Dália** | A **ex-princesa bastarda** que fugiu com um cavalo real. Foi ela quem lembrou do Bobo. Os nobres a reconhecem e sussurram; ela finge não ligar |
| **Arqueiro** | Está na capital do reino que destruiu sua vila; desconfia de todos |
| **Ninja** | Vê o castelo como o maior cofre que já encontrou |
| **Mago** | Interessado na biblioteca real (proposta de missão secundária) |
| **Invocador** | Incomodado com a caça como esporte dos nobres; o Estábulo Real tem animais maltratados (proposta de missão secundária) |

## 5. Notas técnicas

- Mesmo padrão de Tortuga: **uma cena externa** (Avenida Real + porto + pátio do castelo). O castelo em si é fachada (sem interior), o que mantém o desempenho.
- Lojas abrem como janelas de interface ao interagir com a banca/balcão.
- NPCs de ambientação: nobres, guardas, criados, comerciantes, músicos; poucos modelos base com variações de roupa.
- **Segurança da Capital:** os **10 guardas que treinavam no pátio de Tortuga** saem de lá e passam a fazer a **segurança da Capital Real** (portões, castelo e campo de treino da Academia), com as mesmas armas e poses de combate (`data/capital_royal_guards.json`, guardado para quando o mapa existir). Em Tortuga o pátio de treinamento fica só com os bonecos.
- Iluminação mais clara que Tortuga (dia, tochas e lanternas), ainda com poucas luzes dinâmicas.
- Estado da cidade (estoques, missões do Bobo, Bobo sequestrado ou não) salvo no PC do host junto com a campanha.

## 6. Missões do Bobo

| Ordem | Missão | Mapa | O que o Bobo descobriu | Fraqueza do chefe |
|---|---|---|---|---|
| 1 | O ouro das caravanas | 6 · Deserto | As caravanas do rei descem para dentro da areia, perto de um templo soterrado; a Esfinge guarda a porta | Terra |
| 2 | O ouro do fundo do mar | 7 · Águas | Os navios do rei afundam todos na mesma costa, onde o Kraken dorme | Ar |
| 3 | A barcaça do lago negro | 8 · Pântano | Uma barcaça do rei foi puxada para o lago por Grendel e a Mãe | Ar |
| 4 | O templo da serpente | 9 · Serpentes | O último ouro do rei some num templo na costa da selva (Jörmungandr); ali o grupo descobre o **portal para o Inferno** e que tudo vai para Lúcifer | Ar |
| 5 | **O resgate** | 10 · Inferno | O Bobo é sequestrado por Lúcifer; os mercenários vão libertá-lo para saber onde há mais tesouros | Muda por fase: Terra → Água → todos |

- As histórias e pistas completas estão em `03-1-bestiario.md`.
- Equipamentos de **cobre e prata** (e ouro sob encomenda) entram em jogo a partir daqui; o Ferreiro Real refina até **+5** com os pergaminhos desses tiers.

## 7. Onde a Capital entra na campanha

```
Tortuga (abertura) → 1 Esgoto → 2 Ruínas do Reino do Arqueiro → 3 Floresta Escura
      → 4 Cavalos Míticos → 5 Aves
      → o Cavaleiro fala do Bobo da Corte
      → CAPITAL REAL (nova cidade-base, Bobo da Corte)
      → 6 Deserto → 7 Águas → 8 Pântano → 9 Serpentes
      → Bobo sequestrado → 10 Inferno (resgate e Lúcifer)
      → gancho: o reino do primo da família real
```

- A Capital é liberada depois do mapa 5, quando o Cavaleiro conta do Bobo.
- De Tortuga continuam saindo missões secundárias da taverna e o Mercado Pirata segue ativo.
- Os mapas 6 a 10 saem do **Portal Real**; os mapas 1 a 5 continuam acessíveis por Tortuga.

## 8. Decisões em aberto

- O rei e a princesa aparecem como NPCs? Há alguma escolha/final ligado a eles (ex.: contar ou não ao rei sobre o ouro)?
