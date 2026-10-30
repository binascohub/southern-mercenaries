# Personagem — Mago (`mage`)

> Versão 8 · 2026-10-30 · Detalha a classe Mago de `02-personagens.md`
> Modelo de personagem: **misto** — herói fixo (nome, história, visual de referência); o jogador pode mudar o nome, a aparência e **escolher o sexo (masculino ou feminino)**.
> **Elemento:** escolhido na criação (Água, Fogo, Ar ou Terra); troca temporária com Poção Elemental. Regras em `02-0-elementos.md`.
> **Vestimenta:** começa só com roupa de baixo simples de pano e um cajado simples; a roupa muda conforme os equipamentos encontrados (`02-personagens.md`, seção 1).
> Nome e números são propostas para revisar.

## 1. O herói

| Campo | Valor |
|---|---|
| Nome padrão | **Oren Valdris** (masculino) / **Orana Valdris** (feminino) — o jogador pode trocar |
| Sexo | Escolhido pelo jogador: masculino ou feminino |
| Raça | Humano |
| Idade aparente | ~20 anos |
| Arma | Cajado + magia |
| Alcance | À distância |
| Elemento | Escolhido pelo jogador: Água, Fogo, Ar ou Terra |
| Personalidade | Curioso, observador, um pouco solitário; fascinado por tudo que não entende; sede de conhecimento acima de tudo |

### História
(A história é a mesma para todas as versões; o texto usa a versão masculina.)

Desde pequeno, **coisas estranhas aconteciam perto de Oren**, e ele **não entendia o porquê**. Velas acendiam sozinhas quando ele se assustava, a água do balde congelava em noites de choro, o vento abria janelas quando ele ficava com raiva, e plantas brotavam onde ele dormia. As pessoas da vila começaram a olhar torto. Ele também tinha medo de si mesmo.

**Aos poucos, foi descobrindo que tinha um dom com os elementos.** Passou anos testando escondido, errando, se queimando, se molhando, caindo. Dos quatro elementos que respondiam a ele, **conseguiu aprender a controlar apenas um** — o elemento escolhido pelo jogador. Os outros ainda respondem, mas fracos e sem controle.

> **Origem do dom (decidido):** **Deus deu o dom a Oren porque sabia que o destino dele era derrotar Lúcifer.** Oren só descobre isso no final da campanha (e o jogo nunca o diz de forma explícita antes).

Cada resposta só trouxe mais perguntas: de onde vem esse dom? Existem outros como ele? Por que só um elemento obedece? Oren passou a **buscar conhecimento em qualquer lugar**: livros velhos, ruínas, histórias de viajantes. Descobriu que os maiores segredos da magia estão escondidos **nos tesouros guardados pelos demônios** — grimórios antigos, relíquias, objetos que nenhum sábio jamais estudou.

Então foi para Tortuga e virou mercenário. **O ouro paga as viagens; o que ele quer de verdade é o conhecimento** que vem junto com cada tesouro.

- **Motivação:** entender o próprio dom e dominar todos os elementos.
- **Ligação com a campanha:** cada tesouro de demônio pode guardar uma resposta. As **Poções Elementais** despertam por um tempo os elementos que ele ainda não controla — por isso ele as estuda com obsessão.
- **Gancho visual:** os **olhos brilham na cor do elemento** quando ele conjura (e mudam de cor ao beber uma Poção Elemental). Carrega sempre um **caderno de anotações** preso ao corpo por uma tira de couro.

## 2. Aparência

### Início do jogo
- **Roupa de baixo simples de pano** (cor crua), descalço.
- **Caderno de anotações** gasto, preso por uma tira de couro (sempre visível, por cima de qualquer roupa).
- **Cajado simples** de madeira com um cristal pequeno e opaco na cor do elemento.
- Pequenas marcas dos treinos de infância: queimaduras leves, arranhões.

### Visual de referência (com o conjunto típico da classe)
Usado na arte do herói, no menu e como meta visual dos equipamentos de Mago:
- Manto longo de viajante, com bolsos cheios de papéis e frascos, na cor do elemento (tabela abaixo).
- Capuz, cabelo bagunçado, olhar atento.
- Cajado de madeira escura com cristal na cor do elemento, que **brilha conforme a mana atual** (cheio = brilho forte, vazio = apagado). Vale para qualquer cajado.

| Elemento | Cor de referência dos mantos | Detalhe visual do cajado |
|---|---|---|
| Água | Azul-marinho | Gotas e gelo flutuando ao redor do cristal |
| Fogo | Vinho | Brasas soltando do cristal |
| Ar | Cinza-claro | Faíscas e vento movendo a roupa |
| Terra | Marrom-escuro | Pequenas pedras orbitando o cristal |

### Personalização (tela de criação)
| Opção | Escolhas |
|---|---|
| Elemento | Água / Fogo / Ar / Terra |
| Sexo | Masculino / feminino |
| Nome | Texto livre (padrão conforme o sexo) |
| Rosto | 4 opções por sexo |
| Cabelo | 6 estilos por sexo + cor |
| Barba | Só masculino: 4 opções (incluindo sem barba) |
| Pele | 6 tons |

- Sexo é só visual e de voz: **não muda atributos nem habilidades**.
- Elemento **muda as habilidades** (seção 6).
- O resto do visual vem dos **equipamentos encontrados no mapa** (cabeça, corpo, mãos, pés, cajado).

## 3. O Mago em cada elemento

| Elemento | Papel do Mago | Suporte | Dificuldade |
|---|---|---|---|
| Fogo | Maior dano em área do jogo | Aumenta o dano dos aliados | Fácil |
| Água | Controle e cura do grupo | Cura | Média |
| Ar | Ataques rápidos e dano em cadeia; frágil | Velocidade para o grupo | Difícil |
| Terra | Mago mais resistente; atordoa e protege | Escudo em aliado | Média |

## 4. Recurso e Poder Mágico

| Item | Valor |
|---|---|
| Mana inicial | 120 |
| Mana por ponto de INT | +2 |
| Regeneração base | 2 por segundo |
| Regeneração por ponto de INT | +0,05 por segundo |

Todo dano e cura do Mago é calculado a partir do **Poder Mágico (PM)**:

```
PM = dano_do_cajado + (INT × 0,5)
```

Os valores das habilidades são porcentagens do PM.

## 5. Ações básicas

O ataque básico usa o elemento atual (cor e efeito mudam; o dano é igual).

| Ação | Descrição | Custo | Dano |
|---|---|---|---|
| Ataque básico | Rajada curta do cajado, projétil reto, alcance 10 m | 0 | 70% PM |
| Ataque forte | Segurar o botão por 1 s; projétil maior que atravessa 1 inimigo e aplica o estado básico do elemento | 0 | 160% PM |
| Bloqueio | Barreira na frente do cajado enquanto segura; absorve até 30% da vida máxima e consome mana | 1 mana por dano bloqueado | — |
| Esquiva | Rolamento curto (recarga 4 s) | 0 | — |

## 6. Habilidades

O Mago tem **10 habilidades**: **4 comuns** + **6 do elemento**. Cada elemento segue o mesmo padrão:

| Nível | Tipo (`02-0-elementos.md`, seção 5.1) |
|---|---|
| 1 | Básica (alvo único, sem recarga, dano baixo) |
| 2 | Área (`aoe`) |
| 6 | **Suporte** (`support`) |
| 10 | **Alvo único** (`single`) — dano maior |
| 14 | Área (`aoe`) |
| 18 | Área final (`aoe`) |

Ao beber uma Poção Elemental, as 6 habilidades do elemento são trocadas pelas do novo elemento nos mesmos níveis e ranks. Valores do rank 1; máximo rank 5.

### 6.1 Comuns (todos os elementos)

| Nível | ID | Habilidade | Tipo | Mana | Recarga | Efeito |
|---|---|---|---|---|---|---|
| 4 | `sharp_mind` | Mente Afiada | Passiva | — | — | +10% de regeneração de mana por rank |
| 8 | `teleport` | Teleporte | Ativa (**evasão**) | 20 | 8 s (-1 s por rank) | Teleporta até 8 m na direção da mira; atravessa inimigos, não paredes |
| 12 | `mana_shield` | Escudo de Mana | Passiva | — | — | 20% do dano recebido sai da mana (+5% por rank); 1 de mana absorve 2 de dano |
| 16 | `elemental_mastery` | Domínio Elemental | Passiva | — | — | +6% de dano do elemento atual e +10% de duração dos estados por rank |

### 6.2 Fogo (`fire`)

| Nível | ID | Habilidade | Tipo | Mana | Recarga | Dano / efeito (rank 1) | Por rank | Área / alcance | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `fire_bolt` | Dardo de Fogo | Básica | 8 | 0 s | 120% PM | +10% | 12 m | Projétil rápido; aplica `burning` |
| 2 | `fireball` | Bola de Fogo | Área | 18 | 3 s | 150% PM | +15% | 15 m, raio 3 m | Explode e aplica `burning` |
| 6 | `flame_blessing` | Bênção das Chamas | **Suporte** | 30 | 20 s | +15% de dano | +3% | Aliados em raio de 8 m, dura 8 s | Aliados causam mais dano e seus golpes aplicam `burning` |
| 10 | `fire_lance` | Lança de Fogo | **Alvo único** | 30 | 8 s | 320% PM | +30% | 18 m | Lança flamejante que perfura um alvo; +30% contra alvo atordoado (combo Fundir) |
| 14 | `fire_wall` | Muralha de Fogo | Área | 35 | 12 s | 60% PM por s | +8% | Linha de 8 m, dura 6 s | Bloqueia monstros comuns; aplica `burning` |
| 18 | `meteor` | Meteoro | Área final | 60 | 30 s | 600% PM | +60% | 18 m, raio 5 m | Cai após 1,5 s (marca no chão); chão em chamas por 4 s |

### 6.3 Água (`water`)

| Nível | ID | Habilidade | Tipo | Mana | Recarga | Dano / efeito (rank 1) | Por rank | Área / alcance | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `water_bolt` | Jato d'Água | Básica | 8 | 0 s | 100% PM | +10% | 12 m | Projétil; aplica `soaked` |
| 2 | `frost_nova` | Nova de Gelo | Área | 25 | 10 s | 80% PM | +10% | Raio 5 m ao redor | Aplica `frozen` por 2 s (+0,25 s por rank) |
| 6 | `healing_rain` | Chuva Restauradora | **Suporte** | 40 | 15 s | Cura 25% PM por s | +5% | Raio 5 m, dura 6 s | Cura aliados na área e aplica `soaked` nos inimigos |
| 10 | `ice_lance` | Lança de Gelo | **Alvo único** | 30 | 8 s | 300% PM | +30% | 18 m | Lança de gelo; se o alvo estiver `soaked`, fica `frozen` 2 s |
| 14 | `tidal_wave` | Onda | Área | 30 | 8 s | 130% PM | +15% | Cone de 8 m | Empurra inimigos e aplica `soaked` |
| 18 | `blizzard` | Nevasca | Área final | 60 | 30 s | 90% PM por s | +10% | Raio 7 m, dura 6 s | Deixa lento; quem ficar 3 s dentro fica `frozen` |

### 6.4 Ar (`air`)

| Nível | ID | Habilidade | Tipo | Mana | Recarga | Dano / efeito (rank 1) | Por rank | Área / alcance | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `wind_blade` | Lâmina de Vento | Básica | 7 | 0 s | 110% PM | +10% | 14 m | Projétil muito rápido, longo alcance |
| 2 | `chain_lightning` | Corrente de Raios | Área | 22 | 4 s | 100% PM | +12% | 12 m | Salta entre 5 inimigos (+1 nos ranks 3 e 5); -15% de dano por salto; aplica `shocked` |
| 6 | `tailwind` | Vento a Favor | **Suporte** | 30 | 20 s | +30% velocidade | +5% | Aliados em raio de 8 m, dura 8 s | Aliados ficam mais rápidos para andar e atacar |
| 10 | `lightning_bolt` | Relâmpago | **Alvo único** | 30 | 8 s | 330% PM | +30% | 14 m | Atinge na hora (sem projétil); aplica `shocked`; Eletrocuta alvo molhado |
| 14 | `tornado` | Tornado | Área | 35 | 14 s | 70% PM por s | +8% | Anda 10 m na direção da mira, dura 5 s | Puxa inimigos para o centro e os arrasta |
| 18 | `storm` | Tempestade | Área final | 60 | 30 s | 250% PM por raio | +25% | Raio 9 m, dura 8 s | Raios caem a cada 0,5 s em inimigos aleatórios na área |

### 6.5 Terra (`earth`)

| Nível | ID | Habilidade | Tipo | Mana | Recarga | Dano / efeito (rank 1) | Por rank | Área / alcance | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `stone_bolt` | Pedra Arremessada | Básica | 9 | 0 s | 130% PM | +10% | 11 m | Projétil lento e pesado; 15% de chance de `stunned` |
| 2 | `earth_spikes` | Espinhos de Pedra | Área | 18 | 4 s | 140% PM | +15% | Linha de 10 m | Espinhos saem do chão e aplicam `knocked_down` |
| 6 | `stone_skin` | Pele de Pedra | **Suporte** | 25 | 14 s | Escudo de 150% PM | +20% | Em si ou em um aliado (10 m), dura 8 s | Escudo que absorve dano |
| 10 | `boulder` | Rocha Esmagadora | **Alvo único** | 30 | 8 s | 320% PM | +30% | 14 m | Rocha gigante em um alvo; aplica `stunned` 1,5 s |
| 14 | `quake` | Tremor | Área | 28 | 10 s | 90% PM | +10% | Raio 5 m ao redor | Aplica `stunned` 1,5 s (+0,2 s por rank) |
| 18 | `earthquake` | Terremoto | Área final | 60 | 30 s | 500% PM | +50% | Raio 10 m ao redor | Após 1 s, o chão racha: dano enorme e `stunned` 2 s |

## 7. Estilo de jogo por elemento

- **Fogo:** para quem quer ver números grandes. Bola de Fogo e Meteoro em grupos, Lança de Fogo em elites; perde força contra criaturas de Fogo (Pégaso, Fênix, Lúcifer).
- **Água:** o "suporte" do Mago. Congela para o Arqueiro e o Ninja, cura o grupo, é a arma contra os demônios de Fogo.
- **Ar:** o mais rápido e frágil. Raios constantes, deixa o grupo mais rápido; forte no Mapa das Águas e contra Kraken e Jörmungandr.
- **Terra:** o Mago mais resistente. Atordoa, protege aliados com escudo; forte contra as aves.
- **Pontos fracos de todos:** pouca vida, depende de mana, sofre contra Súcubos e Iaras (o encanto o tira de posição) e contra as Harpias (que agarram e roubam poções).

## 8. Equipamentos

Todos aparecem no corpo do personagem quando equipados.

| Slot | Itens | Visual |
|---|---|---|
| Arma | Cajados (duas mãos). Começa com **cajado simples de madeira**. Cajados podem ter bônus de um elemento | Madeira → ponteira de ferro → aço → cobre → prata → ouro (cristal em todos) |
| Mão secundária | Nenhuma (cajado é de duas mãos) | — |
| Cabeça | Capuzes, chapéus, coroas arcanas | Vazio: cabelo à mostra |
| Corpo | Túnicas, mantos e vestes de tecido | Vazio: roupa de baixo de pano |
| Mãos | Luvas e braçadeiras leves | Vazio: mãos nuas, com marcas de treino |
| Pés | Sandálias e botas leves | Vazio: descalço |
| Acessórios | 2 anéis, 1 amuleto | Não aparecem no modelo (só brilho discreto no amuleto); o caderno fica sempre visível |

## 9. Animações necessárias

Mesmo conjunto para os dois sexos e os quatro elementos (o elemento muda só os efeitos visuais). As animações precisam funcionar com qualquer combinação de equipamentos (personagem modular, mesmo esqueleto):

`idle` (às vezes folheia o caderno), `walk`, `run`, `cast_short` (magias rápidas), `cast_long` (magias grandes), `cast_buff` (suporte), `cast_channel` (bloqueio), `charge_attack`, `teleport_out` / `teleport_in`, `dodge_roll`, `hit`, `downed` (caído esperando reanimação), `revive`, `death`, `victory`.

## 10. Falas (exemplos, PT-BR)

Falas neutras, servindo para os dois sexos. Algumas mudam com o elemento.

| Situação | Fala |
|---|---|
| Início do jogo | "Um cajado velho e um caderno cheio de perguntas. Vamos encontrar respostas." |
| Mana baixa | "Preciso de mana!" |
| Subiu de nível | "Entendi mais um pouco… e surgiram mais dez perguntas." |
| Achou valioso | "Ouro paga livros. Livros pagam respostas." |
| Equipou item raro | "Que magia é essa? Preciso anotar." |
| Bebeu Poção Elemental | "Sinto… outro elemento acordando em mim." |
| Ouviu uma lenda nova | "Isso vai para o caderno." |
| Perto de um chefe | "Esse demônio guarda algo que ninguém nunca estudou." |
| Aliado caído | "Levanta! Ainda temos muito a descobrir." |
| Habilidade final (Fogo) | "Queime!" |
| Habilidade final (Água) | "Que o frio os pare." |
| Habilidade final (Ar) | "Sintam a tempestade!" |
| Habilidade final (Terra) | "A terra vai engolir vocês!" |

## 11. Decisões em aberto

- Os tesouros dos demônios trazem "conhecimento" como item (ex.: grimórios que dão pontos de habilidade ou desbloqueiam lendas no bestiário)?
