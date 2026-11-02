# Personagem — Invocador (`summoner`)

> Versão 1 · 2026-10-30 · Detalha a classe Invocador de `02-personagens.md`
> Modelo de personagem: **misto** — herói fixo (nome, história, visual de referência); o jogador pode mudar o nome, a aparência e **escolher o sexo (masculino ou feminino)**.
> **Elemento:** escolhido na criação (Água, Fogo, Ar ou Terra); troca temporária com Poção Elemental. Regras em `02-0-elementos.md`.
> **Vestimenta:** começa só com roupa de baixo simples de pano e um livro simples; a roupa muda conforme os equipamentos encontrados (`02-personagens.md`, seção 1).
> **Os lacaios do Invocador são animais amigos** (não demônios nem espíritos).
> Nome e números são propostas para revisar.

## 1. O herói

| Campo | Valor |
|---|---|
| Nome padrão | **Ari Fennel** (masculino) / **Aria Fennel** (feminino) — o jogador pode trocar |
| Sexo | Escolhido pelo jogador: masculino ou feminino |
| Raça | Humano |
| Idade aparente | ~19 anos |
| Arma | Livro (o **Livro dos Amigos**) |
| Alcance | À distância (os animais amigos lutam de perto) |
| Elemento | Escolhido pelo jogador: Água, Fogo, Ar ou Terra |
| Personalidade | Gentil, alegre e paciente com os animais; desconfiado e calado com pessoas; fica furioso com quem maltrata qualquer criatura |

### História
(A história é a mesma para as duas versões; o texto usa a versão masculina.)

Ari era uma criança que **adorava animais**. Fazia amizade com eles com uma facilidade que ninguém entendia: pássaros pousavam no seu ombro, raposas dormiam no seu colo, e até os animais que todos temiam — ursos, javalis, lobos — se acalmavam perto dele. As pessoas achavam estranho; os animais achavam natural.

Com o tempo, esse **dom** ficou mais forte. Ari aprendeu a **chamar os amigos** de longe, e cada amigo novo ganhava um desenho no seu caderno, que virou o **Livro dos Amigos**. Basta abrir a página certa e chamar pelo nome, e o animal aparece para ajudar.

Um dia, ouvindo seus amigos, Ari descobriu algo terrível: **muitos deles eram órfãos**. Suas famílias tinham sido mortas pelos **animais maus** — as criaturas corrompidas pelos demônios, que caçam tudo o que vive. Ari decidiu que não ia mais só cuidar dos órfãos: **ia lutar contra quem os deixou sozinhos**. Foi para Tortuga e se juntou aos mercenários, porque são os únicos que vão até os covis dos demônios.

- **Motivação:** proteger os animais e acabar com as criaturas corrompidas que matam suas famílias. O ouro dos tesouros alimenta e cuida dos seus amigos órfãos.
- **Ligação com a campanha:** cada mapa é o lar de uma família de criaturas; Ari sente a dor das criaturas que **mudaram de lado** (as "viradas" do bestiário) e luta contra elas, mas **não consegue libertá-las**; o que ele pode é **conhecer animais amigos novos** pelo caminho (seção 6.6).
- **Gancho visual:** um **pequeno pássaro amigo** vive no seu ombro (só visual, não luta) e o acompanha em todos os mapas.

## 2. Aparência

### Início do jogo
- **Roupa de baixo simples de pano** (cor crua), descalço.
- **Pássaro amigo no ombro** (sempre visível, por cima de qualquer roupa); a cor das penas segue o elemento.
- **Livro dos Amigos simples:** capa de couro gasta, páginas cheias de desenhos de animais, preso a uma alça.
- Pequenas marcas de bicada e arranhões nas mãos.

### Visual de referência (com o conjunto típico da classe)
- Capa de viajante com penas, pelos e pequenos amuletos de osso dados pelos amigos.
- Roupas leves de couro e tecido, bolsas com comida para os animais.
- Livro aberto flutuando ao lado ao chamar um amigo; o desenho da página brilha na cor do elemento.

| Elemento | Cor de referência das roupas | Pássaro do ombro | Brilho das páginas |
|---|---|---|---|
| Água | Azul e verde-água | Martim-pescador | Azul, com gotas |
| Fogo | Laranja e marrom | Pintarroxo de penas em brasa | Laranja, com faíscas |
| Ar | Branco e cinza | Andorinha | Branco-violeta, com vento |
| Terra | Verde e marrom | Pica-pau | Verde, com folhas |

### Personalização (tela de criação)
| Opção | Escolhas |
|---|---|
| Elemento | Água / Fogo / Ar / Terra |
| Sexo | Masculino / feminino |
| Nome | Texto livre (padrão conforme o sexo) |
| Rosto | Planejado (4 opções por sexo): os modelos atuais têm uma cabeça só |
| Cabelo | 3 estilos por sexo + sem cabelo, e 8 cores (implementado; mais estilos dependem de novos modelos) |
| Barba | Só masculino: com ou sem barba (implementado; mais estilos dependem de novos modelos) |
| Pele | 6 tons (implementado) |
| Nome do pássaro do ombro | Texto livre (padrão: "Pip") |

- Sexo é só visual e de voz: **não muda atributos nem habilidades**.
- O resto do visual vem dos **equipamentos encontrados no mapa**.

## 3. O Invocador em cada elemento

O elemento define **quais animais amigos** respondem ao chamado.

| Elemento | Companheiro principal | Papel do Invocador | Suporte | Dificuldade |
|---|---|---|---|---|
| Fogo | **Fênix** (rápido, ataques que queimam) | Mais dano dos companheiros | Aumenta o dano dos aliados e dos animais | Fácil |
| Água | **Lobo** (ataca à distância com jatos d'água) | Controle e cura | Cura | Fácil |
| Ar | **Grifo** (voa, ataques rápidos e elétricos) | Velocidade e dano em cadeia | Velocidade para o grupo | Média |
| Terra | **Orc** (resistente, chance de atordoar) | O Invocador mais seguro | Escudo nos aliados | Fácil |

## 4. Recurso e Poder de Invocação

| Item | Valor |
|---|---|
| Essência inicial | 120 |
| Essência por ponto de INT | +2 |
| Regeneração base | 2 por segundo |
| Regeneração extra | +3 a cada golpe de um animal amigo |

Todo dano e efeito do Invocador e dos animais é calculado a partir do **Poder de Invocação (PI)**:

```
PI = dano_do_livro + (INT × 0,5)
```

### Regras dos animais amigos
- Limite de **5 animais ativos** ao mesmo tempo (contam no limite de entidades da área, `03-inimigos.md`).
- Os animais usam o **elemento atual** do Invocador: aplicam o estado do elemento e contam para a fraqueza dos monstros.
- Ao beber uma Poção Elemental, os animais chamados mudam para os do novo elemento.
- Animais que caem **não morrem**: fogem feridos e voltam a estar disponíveis depois da recarga da habilidade.
- IA dos animais roda no servidor, como a dos monstros. Comandos simples: seguem o Invocador e atacam o alvo que ele ataca.

## 5. Ações básicas

| Ação | Descrição | Custo | Dano |
|---|---|---|---|
| Ataque básico | Uma página do livro se solta e voa como projétil (penas/folhas na cor do elemento), alcance 10 m | 0 | 70% PI |
| Ataque forte | Segurar 1 s; um pássaro sai do livro e atravessa até 2 inimigos, aplicando o estado do elemento | 0 | 160% PI |
| Bloqueio | O livro aberto cria uma barreira de penas e folhas enquanto segura; consome Essência | 1 Essência por dano bloqueado | — |
| Esquiva | Rolamento curto (recarga 4 s) | 0 | — |

## 6. Habilidades

O Invocador tem **10 habilidades**: **7 de classe** + **3 do elemento** (suporte no nível 6, alvo único no 12, área final no 18), como em `02-0-elementos.md`, seção 5.2. Valores do rank 1; máximo rank 5.

### 6.1 Habilidades de classe (todos os elementos)

Todas são **imbuídas** do elemento atual.

| Nível | ID | Habilidade | Tipo | Essência | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `call_companion` | Chamar Companheiro | Invocação | 30 | 10 s | Animal com 40% da vida do Invocador; golpes de 50% PI | +10% vida e dano | Ao lado do Invocador | Chama o **companheiro principal** do elemento (tabela da seção 3); até 2 ao mesmo tempo (3 no rank 5); fica até cair |
| 2 | `flock` | Revoada | Área | 18 | 4 s | 110% PI | +12% | Cone de 8 m | Uma revoada de pássaros sai do livro e ataca tudo à frente |
| 4 | `bond` | Laço de Amizade | Passiva | — | — | +8% de vida e dano dos animais | por rank | — | — |
| 8 | `scatter_escape` | Fuga em Bando | **Evasão** | 20 | 9 s (-1 s por rank) | — | — | Até 7 m à frente | O Invocador se desfaz numa revoada de pássaros, atravessa inimigos e reaparece à frente; os animais provocam os inimigos por 2 s |
| 10 | `guardian_bear` | Gorila Guardião | Invocação (tanque) | 40 | 25 s | Gorila com 150% da vida do Invocador; golpes de 70% PI | +12% | Ao lado do Invocador, dura 15 s | Gorila amigo que **provoca e segura os inimigos**; só 1 por vez |
| 14 | `stampede` | Estouro da Manada | Área (linha) | 35 | 14 s | 180% PI | +18% | Linha de 15 m | Uma manada de animais amigos atravessa o campo derrubando (`knocked_down`) |
| 16 | `animal_rescue` | Resgate | Suporte (grupo) | 40 | 40 s | Reanima com 40% da vida | +5% | Aliado caído a até 20 m | Um animal amigo corre até o aliado caído e o reanima à distância |

### 6.2 Fogo (`fire`)

| Nível | ID | Habilidade | Tipo | Essência | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `den_warmth` | Calor da Toca | **Suporte** | 30 | 20 s | +15% de dano | +3% | Aliados e animais em raio de 8 m, dura 8 s | Raposas de fogo cercam o grupo; aliados e animais causam mais dano e aplicam `burning` |
| 12 | `salamander_bite` | Mordida da Salamandra | **Alvo único** | 30 | 8 s | 320% PI | +30% | 15 m | Uma salamandra gigante surge sob o alvo e o morde; `burning` com o dobro do dano |
| 18 | `fire_stampede` | Manada em Chamas | **Área final** | 60 | 30 s | 520% PI no total | +50% | Faixa de 20 m × 6 m | Cervos de fogo atravessam a área deixando o chão em chamas |

### 6.3 Água (`water`)

| Nível | ID | Habilidade | Tipo | Essência | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `otter_spring` | Fonte das Lontras | **Suporte** | 35 | 15 s | Cura 25% PI por s | +5% | Raio 5 m, dura 6 s | Lontras trazem água fresca que cura aliados e animais; molha os inimigos (`soaked`) |
| 12 | `narwhal_charge` | Investida do Narval | **Alvo único** | 30 | 8 s | 300% PI | +30% | Linha até o alvo, 18 m | Um narval de água atravessa até o alvo; se o alvo estiver `soaked`, fica `frozen` 2 s |
| 18 | `whale_song` | Canto da Baleia | **Área final** | 60 | 30 s | 500% PI no total | +50% | Raio 8 m | Uma baleia espiritual emerge e cai como onda gigante: dano, empurra e aplica `soaked` |

### 6.4 Ar (`air`)

| Nível | ID | Habilidade | Tipo | Essência | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `falcon_wings` | Asas do Falcão | **Suporte** | 30 | 20 s | +30% velocidade | +5% | Aliados e animais em raio de 8 m, dura 8 s | Falcões voam sobre o grupo; todos andam e atacam mais rápido |
| 12 | `eagle_dive` | Mergulho da Águia | **Alvo único** | 30 | 8 s | 330% PI | +30% | 20 m | Uma águia de raios mergulha no alvo; aplica `shocked`; **Eletrocuta** alvo molhado |
| 18 | `wing_storm` | Tempestade de Asas | **Área final** | 60 | 30 s | 550% PI no total | +55% | Raio 9 m, dura 5 s | Centenas de pássaros elétricos atacam todos os inimigos da área |

### 6.5 Terra (`earth`)

| Nível | ID | Habilidade | Tipo | Essência | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `turtle_shell` | Casco da Tartaruga | **Suporte** | 30 | 16 s | Escudo de 120% PI | +15% | Aliados e animais em raio de 5 m, dura 8 s | Uma tartaruga gigante ergue o casco sobre o grupo; todos recebem um escudo |
| 12 | `rhino_charge` | Investida do Rinoceronte | **Alvo único** | 30 | 8 s | 320% PI | +30% | Linha até o alvo, 15 m | Um rinoceronte de pedra atropela o alvo; aplica `stunned` 1,5 s |
| 18 | `mammoth_stomp` | Pisada do Mamute | **Área final** | 60 | 30 s | 500% PI no total | +50% | Raio 9 m | Um mamute surge e pisa o chão três vezes; aplica `knocked_down` |

### 6.6 Páginas do Livro: conhecer animais novos (decidido pelo autor)
O Invocador **não liberta criaturas corrompidas**. O que abre mais habilidades é **conhecer animais amigos novos** durante a aventura.

- Cada mapa esconde **1 animal amigo raro e não corrompido** (por exemplo, um animal ferido, escondido num canto da área, num segredo). O jogador o encontra, **cuida dele** (interação) e ele vira uma **nova página do Livro dos Amigos**.
- Cada página desbloqueia um **companheiro alternativo** e **uma habilidade extra** ligada a ele, que o jogador pode trocar pelos companheiros do elemento fora de combate (as 4 ativas continuam sendo as equipadas, `02-personagens.md`).
- Uma página por mapa (**10 páginas**), mais uma de bônus por segredo especial (**proposta**).
- Os animais conhecidos aparecem no **bestiário** (aba "Amigos") e na janela de habilidades do Invocador.
- Lista de animais (proposta, a detalhar: habilidade, elemento, papel): Esgoto — gato de rua; Ruínas — lobo cinzento; Floresta — coruja; Cavalos — potro; Aves — águia-pescadora; Deserto — raposa-do-deserto; Águas — golfinho; Pântano — garça; Serpentes — mangusto; Inferno — cervo de luz.
- Valores (vida, dano, custo de Essência) sob a regra de `13-balanceamento.md`; cada habilidade segue a mesma estrutura das tabelas da seção 6.
- Os outros heróis não têm esse sistema.

## 7. Estilo de jogo

- **Solo:** a classe mais fácil para jogar sozinho: o Gorila Guardião e os companheiros seguram os monstros enquanto o Invocador ataca de longe. Fuga em Bando quando cercado.
- **Em grupo:** o "cuidador" do grupo: reanima à distância (`animal_rescue`), dá suporte e enche a tela de aliados.
- **Pontos fortes:** muitos alvos para distrair os inimigos; ótimo contra matilhas (Mapa dos Lobos).
- **Pontos fracos:** pouca vida; se os animais caírem todos, fica exposto; sofre contra criaturas que atacam em área (Kraken, Jörmungandr) e contra a Strix, que drena vida.

## 8. Equipamentos

Todos aparecem no corpo do personagem quando equipados.

| Slot | Itens | Visual |
|---|---|---|
| Arma | **Livros** (bônus aos animais: vida, dano, número de companheiros). Começa com **Livro dos Amigos simples** (capa de couro gasto) | Couro → capa com cantoneiras de ferro → aço → cobre → prata → ouro (cantoneiras, fecho e detalhes no material) |
| Mão secundária | **Totens e amuletos de animal** (bônus a um tipo de animal ou a um elemento) | Vazio: mão livre |
| Cabeça | Capuzes, tiaras de penas, máscaras de animal | Vazio: cabelo à mostra |
| Corpo | Capas com penas e pelos, roupas leves | Vazio: roupa de baixo de pano |
| Mãos | Luvas de couro grosso (para pássaros pousarem) | Vazio: mãos nuas com arranhões |
| Pés | Sandálias e botas leves | Vazio: descalço |
| Acessórios | 2 anéis, 1 amuleto | O pássaro do ombro fica sempre visível |

## 9. Animações necessárias

Mesmo conjunto para os dois sexos e os quatro elementos (o elemento muda só os efeitos e os animais). As animações precisam funcionar com qualquer combinação de equipamentos:

- **Invocador:** `idle` (faz carinho no pássaro do ombro), `walk`, `run`, `cast_short` (folhear e soltar página), `summon` (abrir o livro e chamar), `cast_buff`, `cast_channel` (bloqueio), `charge_attack`, `scatter_out` / `scatter_in` (virar revoada e voltar), `dodge_roll`, `hit`, `downed`, `revive`, `death`, `victory`.
- **Animais amigos:** reaproveitar os esqueletos das famílias de monstros quando possível (ex.: raposa e lobo no esqueleto canino; falcão e águia no de ave) para economizar animação; animações básicas `idle`, `run`, `attack`, `hit`, `flee`.

## 10. Falas (exemplos, PT-BR)

Falas neutras, servindo para os dois sexos.

| Situação | Fala |
|---|---|
| Início do jogo | "Pip, vamos lá. Tem muita gente precisando da gente." |
| Essência baixa | "Preciso de um tempo pra chamar mais amigos!" |
| Subiu de nível | "Mais amigos vão poder vir!" |
| Chamou um companheiro | "Vem, amigo!" |
| Companheiro caiu | "Fuja! Descansa que eu te chamo depois." |
| Viu uma criatura "virada" | "Você não era assim… o que fizeram com você?" |
| Achou valioso | "Isso compra comida pra todos os órfãos da toca." |
| Perto de um chefe | "Foi ele. Foi ele que deixou tantos sozinhos." |
| Aliado caído | "Aguenta! Um amigo já está indo te buscar!" |
| Habilidade final (Fogo) | "Corram, amigos de fogo!" |
| Habilidade final (Água) | "Canta, baleia!" |
| Habilidade final (Ar) | "Todos os pássaros, agora!" |
| Habilidade final (Terra) | "Pisa forte, grandão!" |

## 11. Decisões em aberto

- Detalhar as habilidades e o papel de cada um dos 10 animais novos (seção 6.6).
- O pássaro do ombro tem algum efeito de jogo (ex.: avisa armadilhas e emboscadas) ou é só visual?

## Visual do equipamento por rank (implementado)

O Invocador troca de roupa por **rank**, de **D** (a mais simples) a **S** (a mais rara e melhor), seguindo a referência do autor (`clothes.jpeg`, níveis 1 a 5). Cada peça (corpo, cabeça, mãos, pés) troca separadamente; o rank sai do material da peça (pano e ferro = D, aço = C, cobre = B, prata = A, ouro = S). Vale para os dois sexos. Código em `game/actors/class_gear.gd` e `game/actors/gear_kit.gd`; dá para ver cada rank na tela de criação do personagem ("Equipamento").

D retalhos de couro com colar de ossos e corda; C poncho escuro com barra rasgada, penas e contas; B túnica tribal com faixas turquesa, colar de contas e penas; A manto de pele, bordado e pingente turquesa; S túnica cósmica azul e roxa com cristais nos ombros, luzes e coroa de chifres.
