# Sistema de Elementos

> Versão 3 · 2026-10-30 · Vale para **todas as classes** (`02-personagens.md`) e **todos os monstros** (`03-inimigos.md`)
> Este arquivo é a fonte oficial de elementos, ciclo de fraquezas, troca de elemento, estados, combos e da regra de composição das habilidades.

## 1. Regra geral

- Todo personagem escolhe **um elemento na criação**: **Água, Fogo, Ar ou Terra**. Esse é o **elemento de origem** e não muda.
- O elemento **muda as habilidades**, o efeito dos ataques e o visual dos efeitos.
- O jogador pode **trocar de elemento temporariamente** com uma **Poção Elemental** comprada no Mercado de Tortuga (seção 4).
- **Todo monstro também tem um elemento** e é **fraco a outro** (seção 3).
- Sexo e aparência não afetam nada de jogo; **classe + elemento** definem o personagem.

## 2. Os quatro elementos

| ID | Elemento | Identidade | Ponto forte | Ponto fraco | Cores |
|---|---|---|---|---|---|
| `fire` | Fogo | Dano máximo | Dano em área e ao longo do tempo | Pouco controle | Laranja e vermelho |
| `water` | Água | Controle e apoio | Lentidão, congelamento, cura leve | Dano mais baixo | Azul e branco |
| `air` | Ar | Velocidade e raios | Ataques rápidos, empurrões, dano em cadeia | Pouca defesa | Branco e violeta |
| `earth` | Terra | Defesa e atordoamento | Atordoa, barreiras, proteção | Mais lento | Verde e marrom |

## 3. Ciclo de fraquezas

```
Água ──vence──▶ Fogo ──vence──▶ Terra ──vence──▶ Ar ──vence──▶ Água
```

| Elemento do monstro | **Fraco a** (+50% dano) | Resiste a (-50% dano) | Por quê |
|---|---|---|---|
| Fogo | **Água** | Fogo | A água apaga o fogo |
| Terra | **Fogo** | Terra | O fogo derrete a pedra e queima a mata |
| Ar | **Terra** | Ar | A terra prende e derruba o que voa |
| Água | **Ar** | Água | Os raios correm pela água |

- Ataques do **mesmo elemento** do monstro causam **-50%** de dano; do elemento **forte contra ele**, **+50%**; os outros dois, dano normal.
- Vale para todo dano de jogador (ataques básicos, habilidades, lacaios do Invocador).
- Estados de controle (`frozen`, `stunned`…) funcionam normalmente; só o dano muda.

### Como o jogador descobre a fraqueza
1. **Na história:** quem conta a missão na taverna **sempre fala do elemento do monstro/demônio e do que o vence** (ex.: "o fogo daquele Pégaso só se apaga com água"). Ver `04-tortuga-e-missoes.md`.
2. **No bestiário:** o Bardo registra o elemento e a fraqueza de cada monstro.
3. **No mapa:** cada monstro mostra um **ícone do seu elemento** junto à barra de vida; o número de dano aparece **maior e colorido** quando acerta a fraqueza, e **cinza e menor** quando o monstro resiste.

## 4. Troca de elemento — Poção Elemental

| Item | Valor |
|---|---|
| ID | `elemental_potion_water`, `elemental_potion_fire`, `elemental_potion_air`, `elemental_potion_earth` |
| Onde comprar | **Mercado de Tortuga** |
| Preço | Cresce com o nível do personagem (proposta: 100 + 25 × nível de ouro) |
| Duração | **Uma expedição**: do momento em que bebe até voltar a Tortuga |
| Limite | Uma poção ativa por vez; beber outra troca o efeito |

**Efeito ao beber:**
- O personagem passa a usar o **novo elemento**: ataques, estado básico e cor dos efeitos.
- As **habilidades do elemento** são trocadas pelas equivalentes do novo elemento, **com os mesmos ranks** (a habilidade de nível 6 do elemento de origem vira a de nível 6 do novo elemento, e assim por diante).
- As habilidades de classe não mudam.
- Ao voltar a Tortuga, o personagem volta ao **elemento de origem**.

**Por que existe:** cada mapa tem monstros e demônio de um elemento; as histórias avisam a fraqueza, e o grupo se prepara comprando as poções certas antes de partir pelo porto.

## 5. Composição das habilidades

### 5.1 Tipos de habilidade

Todo conjunto de habilidades de elemento precisa ter os três tipos:

| ID | Tipo | Regra | Faixa de dano (rank 1) |
|---|---|---|---|
| `aoe` | Área | Atinge vários inimigos; **dano menor** por alvo | 60% a 180% do poder (habilidade final: 500% a 600%) |
| `single` | Alvo único | Atinge um inimigo; **dano maior** | 280% a 350% do poder |
| `support` | Suporte | Ajuda o grupo (cura, escudo, velocidade, bônus de dano); pouco ou nenhum dano | 0% a 50% do poder |

"Poder" = o atributo de dano da classe (ex.: Poder Mágico do Mago).

### 5.2 Divisão por classe

Cada classe tem **10 habilidades**:

| Classe | Habilidades de classe (iguais para todos) | Habilidades do elemento |
|---|---|---|
| Mago | 4 | 6: básica (nível 1), área (2), **suporte (6)**, **alvo único (10)**, área (14), área final (18) |
| Cavaleiro, Arqueiro, Ninja, Invocador | 7 | 3: **suporte (6)**, **alvo único (12)**, **área final (18)** |

- **Habilidades de classe:** a mecânica é a mesma em todos os elementos, mas o golpe é **imbuído** do elemento atual: aplica o estado básico dele (seção 5.3) e muda a cor/efeito visual.
- **Habilidades do elemento:** exclusivas da combinação classe + elemento.
- **Ataque forte:** aplica o estado básico do elemento.

### 5.3 Estado básico de cada elemento
| Elemento | Estado básico aplicado por golpes imbuídos e ataques fortes |
|---|---|
| Fogo | `burning` |
| Água | `soaked` |
| Ar | `shocked` |
| Terra | 30% de chance de `stunned` |

### 5.4 Suporte por elemento (tema)
| Elemento | Tipo de suporte |
|---|---|
| Fogo | Bônus de dano para os aliados |
| Água | Cura |
| Ar | Velocidade de movimento e de ataque |
| Terra | Escudo / redução de dano |

## 6. Estados elementais

| ID | Estado | Origem | Efeito | Duração padrão |
|---|---|---|---|---|
| `burning` | Queimando | Fogo | Dano ao longo do tempo (padrão: 30% do dano do golpe por s) | 3 s |
| `soaked` | Molhado | Água | -20% velocidade de movimento | 4 s |
| `frozen` | Congelado | Água (forte) | Não se move nem ataca; recebe crítico garantido | 2 s |
| `shocked` | Eletrizado | Ar | Recebe +15% de dano de Ar | 4 s |
| `knocked_down` | Derrubado | Ar / Terra | Caído, sem agir | 1 s |
| `stunned` | Atordoado | Terra | Não age | 1,5 s |

- Chefes nunca ficam **congelados**, **derrubados** ou **atordoados**: recebem 50% de lentidão no lugar.
- Reaplicar um estado renova a duração, sem acumular.
- Monstros de Fogo não ficam `burning`; monstros de Água não ficam `soaked`.

## 7. Combos entre elementos (co-op)

Qualquer jogador pode completar o combo de outro, de qualquer classe. Exemplo: o Arqueiro de Água molha os inimigos e o Ninja de Ar eletrocuta.

| Estado no inimigo | + golpe de | Combo | Resultado |
|---|---|---|---|
| Molhado | Ar | **Eletrocutar** | +50% de dano de Ar e atordoa 1 s |
| Queimando | Ar | **Incêndio** | O fogo se espalha para inimigos próximos (raio 3 m) |
| Molhado | Terra | **Lama** | Área de lama que deixa inimigos 40% mais lentos por 5 s |
| Queimando | Água | **Vapor** | Nuvem que faz os inimigos errarem 30% dos ataques por 4 s |
| Atordoado | Fogo | **Fundir** | +30% de dano no inimigo atordoado |

- Um combo **consome** o estado que o iniciou.
- O bônus de fraqueza (seção 3) soma com o combo.

## 8. Visual e desempenho

- Cada elemento tem seu conjunto de efeitos (cor, partículas, som), reaproveitado por todas as classes e monstros.
- Partículas simples e em pouca quantidade (requisito de rodar em vídeo integrado).
- A arma de cada classe ganha um brilho na cor do elemento atual (cristal do cajado, ponta da lança, flechas, lâminas das adagas, páginas do livro); muda na hora ao beber uma Poção Elemental.

## 9. Decisões em aberto

- Itens com bônus de elemento (ex.: "+10% dano de Fogo") servem para qualquer classe?
- Preço da Poção Elemental (proposta: 100 + 25 × nível)?
