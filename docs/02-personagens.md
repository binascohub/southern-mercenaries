# Personagens — Visão geral das classes

> Versão 11 · 2026-10-30 · Complementa `01-escopo.md`
> Números são propostas iniciais para balancear depois.

## 1. Regras de personagem

- **Mercenários:** todos os heróis são mercenários que vivem de caçar tesouros, cada um com um motivo próprio (`06-mundo-e-historia.md`).
- **Modelo misto:** cada classe tem um herói fixo (nome, história, visual de referência); o jogador pode mudar o nome e a aparência.
- **Sexo:** o jogador escolhe masculino ou feminino. Muda visual e voz; **não muda atributos nem habilidades**. Diferenças de história:
  - **Cavaleiro:** cada sexo tem uma **história totalmente diferente** (Dorian e Dália).
  - **Ninja:** mesma origem, mas o **motivo da deserção** muda (Ren e Rin).
  - **Mago, Arqueiro, Invocador:** mesma história para os dois.
- **Elemento:** o jogador escolhe um elemento de origem (Água, Fogo, Ar ou Terra), que muda as habilidades. Pode trocar **temporariamente** com uma Poção Elemental do Mercado de Tortuga. Regras em `02-0-elementos.md`.
- **Classe + elemento** definem o personagem (ex.: Ninja de Ar, Cavaleiro de Fogo).

### Vestimenta e equipamentos
- **Todo personagem começa só com roupa de baixo simples de pano** (sem armadura, sem capa, sem elmo).
- **A roupa muda conforme os equipamentos** que o jogador encontra no mapa e equipa: cada peça equipada aparece no corpo do personagem.
- Slots visíveis: **cabeça, corpo, mãos, pés** e **arma** (+ mão secundária quando houver; + barda do cavalo no Cavaleiro).
- Slot vazio = mostra a parte do corpo com a roupa de baixo.
- A arma inicial é a **arma básica da classe, de madeira** (cajado simples, arco simples, par de adagas de treino, livro simples, lança simples), para conseguir lutar desde o começo.
- Cada herói tem um **objeto pessoal** sempre visível:

| Classe | Objeto pessoal |
|---|---|
| Mago | Caderno de anotações |
| Arqueiro | Dente da primeira caça |
| Cavaleiro | Fita da princesa (Dorian) / broche real (Dália) |
| Ninja | Guarda da espada do pai |
| Invocador | Pássaro amigo no ombro |

- O "visual de referência" de cada herói (descrito no arquivo da classe) é a aparência com o conjunto típico da classe, usado na arte do jogo, no menu e como meta visual dos equipamentos.

### Notas técnicas (personagem modular)
- Corpo base (masculino e feminino) com roupa de baixo + uma malha por peça de equipamento, todas no **mesmo esqueleto**.
- Ao equipar, troca a malha do slot; partes do corpo cobertas pela peça são escondidas para evitar sobreposição.
- Para desempenho, juntar as malhas do personagem em uma só depois de trocar o equipamento (menos chamadas de desenho).
- Cada peça precisa de versão para os dois sexos (ou uma malha ajustada aos dois corpos).
- No co-op, os outros jogadores veem os equipamentos de cada um (sincronizar os IDs dos itens equipados, não as malhas).

## 2. Arquivos de cada classe

Todas as classes estão detalhadas. **O arquivo da classe é a fonte oficial**; o resumo aqui é só visão geral.

| Arquivo | Classe | Herói padrão (m / f) |
|---|---|---|
| `02-0-elementos.md` | Sistema de elementos (todas as classes e monstros) | — |
| `02-1-mago.md` | Mago | Oren / Orana Valdris |
| `02-2-arqueiro.md` | Arqueiro | Kael / Kaela Thorne |
| `02-3-cavaleiro.md` | Cavaleiro | Dorian Vale / Dália Vale (histórias diferentes) |
| `02-4-ninja.md` | Ninja | Ren / Rin Kurogane (motivo da deserção diferente) |
| `02-5-invocador.md` | Invocador | Ari / Aria Fennel |

## 3. As 5 classes

| ID | Classe | Arma | Alcance | Papel no grupo | Resistência | Velocidade | Recurso |
|---|---|---|---|---|---|---|---|
| `knight` | Cavaleiro | Cavalo + lança | **Corpo a corpo** | Tanque de investida: linha de frente, derruba e provoca; desmonta em áreas estreitas | **Alta (tanque)** | **A mais rápida** (cavalo) | Ímpeto (enche ao galopar e acertar) |
| `ninja` | Ninja | Par de adagas | **Corpo a corpo** | Tanque ágil: aguenta desviando e aparando; **teleporta** para dentro e para fora da luta | **Alta (tanque)** | Rápida + teleporte | Energia (regenera rápido) |
| `archer` | Arqueiro | Arco e flecha | **À distância** | Dano à distância, armadilhas | Baixa | Normal | Foco (regenera rápido parado) |
| `mage` | Mago | Cajado + magia | **À distância** | Dano mágico em área, controle | Baixa | Normal | Mana (regenera devagar) |
| `summoner` | Invocador | Livro dos Amigos | **À distância** (os animais amigos lutam de perto) | Animais amigos e suporte | Baixa | Normal | Essência (enche com os golpes dos animais) |

### Dois grupos de classes
- **Corpo a corpo e tanques:** Cavaleiro e Ninja. Ficam na frente e aguentam o dano.
- **À distância:** Mago, Arqueiro e Invocador. Mesmo movimento (velocidade normal, andam e atacam livremente) e **cada um tem obrigatoriamente pelo menos uma habilidade de evasão** para sair do perigo:

| Classe | Habilidade de evasão | Efeito |
|---|---|---|
| Mago | `teleport` — Teleporte | Teleporta até 8 m na direção da mira |
| Arqueiro | `back_leap` — Salto para Trás | Salta 6 m para trás e deixa inimigos próximos lentos |
| Invocador | `scatter_escape` — Fuga em Bando | Vira uma revoada de pássaros, atravessa inimigos e reaparece até 7 m à frente; os animais provocam os inimigos por 2 s |

Essas habilidades são de **classe** (iguais em todos os elementos), além da esquiva básica que todos têm.

### Como cada um aguenta dano
- **Cavaleiro:** muita vida, armadura pesada e escudo; segura o dano de frente.
- **Ninja:** vida alta, **evasão**, **aparar** com as adagas e teleporte para sair do perigo.
- **Mago, Arqueiro e Invocador:** pouca vida; dependem de distância, da habilidade de evasão e da proteção do grupo (no Invocador, também dos animais amigos e do Urso Guardião).

## 4. Atributos

| ID | Nome | Efeito |
|---|---|---|
| `str` | Força (FOR) | Dano corpo a corpo pesado (lança); requisito de armas/armaduras pesadas |
| `dex` | Destreza (DES) | Dano de flechas e adagas, chance de crítico, velocidade de ataque, evasão |
| `int` | Inteligência (INT) | Dano mágico, força dos animais amigos, recurso máximo |
| `vit` | Vitalidade (VIT) | Vida máxima, resistência a atordoamento |

### Atributos iniciais (nível 1)
| Classe | FOR | DES | INT | VIT | Vida | Velocidade de movimento | Recurso |
|---|---|---|---|---|---|---|---|
| Cavaleiro | 25 | 10 | 10 | 30 | 150 | 120% montado / 95% a pé | 100 Ímpeto |
| Ninja | 15 | 25 | 10 | 25 | 130 | 110% | 100 Energia |
| Arqueiro | 15 | 25 | 15 | 20 | 90 | 100% | 100 Foco |
| Mago | 10 | 15 | 30 | 20 | 75 | 100% | 120 Mana |
| Invocador | 10 | 15 | 30 | 20 | 80 | 100% | 120 Essência |

A resistência alta do Cavaleiro e do Ninja vem da vida e das habilidades; a armadura vem dos equipamentos encontrados (no início todos estão só com roupa de baixo).

### Poder de cada classe
Todo dano das habilidades é uma porcentagem do "poder" da classe:

| Classe | Poder | Fórmula |
|---|---|---|
| Cavaleiro | Poder de Ataque (PA) | dano_da_lança + FOR × 0,5 |
| Ninja | Poder de Lâmina (PL) | dano_das_adagas + DES × 0,5 |
| Arqueiro | Poder de Tiro (PT) | dano_do_arco + DES × 0,5 |
| Mago | Poder Mágico (PM) | dano_do_cajado + INT × 0,5 |
| Invocador | Poder de Invocação (PI) | dano_do_livro + INT × 0,5 |

### Progressão
- Nível máximo: 20 (v1.0).
- Por nível: +5 pontos de atributo livres e +1 ponto de habilidade.
- Cada habilidade tem até 5 ranks.
- Habilidades liberadas nos níveis 1, 2, 4, 6, 8, 10, 12, 14, 16 e 18.
- 4 habilidades ativas equipadas em atalhos; passivas funcionam sempre.
- Redistribuir pontos: na cidade-base, pagando ouro.

### Habilidades (regra)
- Cada classe tem 10 habilidades: parte da **classe** (iguais para todos os elementos) e parte do **elemento**.
  - Mago: 4 de classe + 6 do elemento.
  - Demais classes: 7 de classe + 3 do elemento (suporte no nível 6, alvo único no 12, área final no 18).
- Todo conjunto de elemento tem **área (dano menor)**, **alvo único (dano maior)** e **suporte**. Detalhes em `02-0-elementos.md`, seção 5.
- Classes à distância têm sempre pelo menos **1 habilidade de evasão** de classe (seção 3).

### Ações básicas (todas as classes)
- Ataque básico com a arma da classe (sem custo).
- **Golpe físico com a arma:** todas as classes batem com a arma que têm nas mãos. Ninja (adagas) e Cavaleiro (lança) sempre; Mago (cajado), Arqueiro (arco) e Invocador (livro) usam a pancada quando há inimigo ao alcance na frente (cerca de 2,2 a 2,4 m, dano menor que o tiro: 60 a 70% do poder) e continuam atirando à distância quando não há ninguém perto (`melee_basic` em `data/classes.json`).
- Ataque forte (segurar o botão); aplica o estado do elemento.
- Esquiva (recarga curta). No Cavaleiro montado é um salto lateral do cavalo; no Ninja é um **teleporte curto**.
- Bloqueio (o Ninja **apara**; o Arqueiro não bloqueia e tem esquiva com recarga menor), usar poção, interagir.
- Reanimar aliado caído (segurar o botão por 3 s).

## 5. Sinergias em grupo

- Cavaleiro e Ninja na frente segurando os inimigos; Arqueiro, Mago e Invocador atrás causando dano e dando suporte.
- `challenge` (Cavaleiro) / `iron_body` (Ninja) / `guardian_bear` (Invocador) + habilidades de área do Mago e as chuvas do Arqueiro.
- Suportes de cada classe se somam: estandartes do Cavaleiro, selos do Ninja, magias do Mago, flechas do Arqueiro e animais do Invocador.
- `mark_target` (Arqueiro) foca o grupo inteiro no chefe ou em elites; o Ninja aproveita com `backstab`.
- `animal_rescue` (Invocador) reanima à distância quem cai na linha de frente.
- Combos de elementos entre jogadores (`02-0-elementos.md`, seção 7).
- Em mapas de elementos mistos, cada jogador leva uma Poção Elemental diferente para cobrir todas as fraquezas.

## 6. Decisões em aberto

- Dois jogadores podem escolher a mesma classe na mesma partida?

## Aparência na criação (implementada)

A tela de criação (menu principal → Personagens) tem, além de classe, elemento, sexo e nome, **estilo de cabelo, cor do cabelo, barba (só masculino) e tom de pele**, com uma prévia 3D do herói girando. A escolha é só visual e fica na ficha (`look`, índices de `data/appearance.json`); personagens antigos, sem `look`, mantêm o visual padrão da classe. O **rosto** do documento original ainda não existe: os modelos têm uma cabeça só.
