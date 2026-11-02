# Balanceamento

> Versão 1 · 2026-10-30 · Tabelas e fórmulas iniciais de vida, dano, armadura, XP, ouro e preços. Complementa `02-personagens.md`, `03-inimigos.md`, `03-2-areas.md`, `05-itens-e-loot.md`, `05-1-refino.md` e `07-rede.md`
> **Todos os números são propostas de partida**, calculadas para ficar coerentes entre si. Devem ser afinados em teste (de preferência com uma planilha ou script de simulação que leia os mesmos arquivos de dados do jogo). Itens **em aberto** não devem ser decididos sem consultar o autor.

## 1. Metas de sensação

| Situação | Meta (1 jogador, equipamento típico da faixa de nível) |
|---|---|
| Monstro comum | Morre em **1 a 3 s** de ataque contínuo |
| Elite | **8 a 12 s** |
| Mini-chefe | **30 a 45 s** |
| Chefe | **2 min** (mapa 1) até **4,5 min** (mapa 9); **Lúcifer ~6 min** (3 fases) |
| Cavaleiro com armadura típica | Aguenta **6 a 8 golpes** de um comum do mesmo nível; **~5 golpes fortes** de chefe |
| Mago, Arqueiro, Invocador | Aguentam **3 a 5 golpes** de um comum; **2 a 3 golpes fortes** de chefe (por isso precisam de distância, evasão e aviso no chão) |
| Ritmo de nível | **2 níveis por mapa** (`01-escopo.md`) |
| Grupo de 4 | Luta **~30% mais rápida** que solo contra a mesma criatura, e mais perigosa (+30% de dano) |

## 2. Fórmulas

### 2.1 Dano do jogador
```
dano_arma   = 10 × mult_material × (1 + afixo_raridade) × (1 + bônus_refino)
poder (PA/PL/PT/PM/PI) = dano_arma + 0,5 × atributo_principal      (02-personagens.md)
dano_da_habilidade = poder × % da habilidade × (1 + bônus de rank) × mult_elemento × mult_crítico
```
- `mult_material`: x1,0 / 1,6 / 2,3 / 3,1 / 4,0 / 5,0 (madeira ou pano → ouro, `05-itens-e-loot.md`).
- `afixo_raridade`: comum 0%, mágico +10%, raro +25%, único +40%, lendário +60% (proposta).
- `bônus_refino`: +1 5%, +2 10%, +3 15%, +4 25%, +5 35% (`05-1-refino.md`).
- Rank das habilidades: +10% de dano por rank acima do 1 (já descrito nas tabelas de cada classe).
- `mult_elemento`: x1,5 na fraqueza, x0,5 no mesmo elemento (`02-0-elementos.md`).
- Crítico: x1,5 (base 5% de chance; +DES e passivas).

### 2.2 Vida do jogador
```
vida = vida_inicial + (nível − 1) × vida_por_nível + 5 × (VIT − VIT_inicial)
```
| Classe | Vida inicial | Vida por nível | Vida no nível 20 (sem VIT extra) |
|---|---|---|---|
| Cavaleiro | 150 | +55 | 1.195 |
| Ninja | 130 | +45 | 985 |
| Arqueiro | 90 | +35 | 755 |
| Mago | 75 | +30 | 645 |
| Invocador | 80 | +32 | 688 |

(Os 95 pontos livres dão à vontade mais vida pela VIT, ~5 de vida por ponto.) A vida cresce ~8x do nível 1 ao 20, junto com o dano dos monstros (seção 3), para o jogador aguentar um número parecido de golpes ao longo do jogo.

### 2.3 Armadura e redução de dano
```
armadura_total  = Σ (armadura_base_da_peça × mult_material × fator_classe × (1 + afixo) × (1 + bônus_refino))
redução_de_dano = armadura_total / (armadura_total + 40 + 15 × nível_do_monstro)        (máximo 75%)
```
| Peça | Armadura base |
|---|---|
| Corpo | 10 |
| Cabeça | 5 |
| Mãos | 4 |
| Pés | 4 |
| Escudo (Cavaleiro) | 8 (e bloqueio de -60% de dano frontal) |

| Classe | Fator de classe |
|---|---|
| Cavaleiro | 1,0 |
| Ninja | 0,7 |
| Arqueiro | 0,6 |
| Mago | 0,35 |
| Invocador | 0,35 |

Resultado (conjunto completo do tier, sem afixos nem refino), ~25% de redução para o Cavaleiro em qualquer faixa de nível: nível 4 (ferro) 27%, nível 8 (aço) 25%, nível 12 (cobre) 25%, nível 16 (prata) 25%, nível 20 (ouro) 25%. Afixos e refino levam o Cavaleiro bem equipado a ~35–40%; os conjuntos de pano dos conjuradores ficam em ~9%. O mérito está em **acompanhar o nível dos monstros**: usar equipamento de tier antigo faz a redução cair rápido.

### 2.4 Vida e dano dos monstros
```
vida_do_monstro = vida_base × 1,12^(nível_da_área − 1) × mult_categoria × fator_de_chefe × fator_jogadores
dano_do_monstro = dano_base × 1,12^(nível_da_área − 1) × mult_categoria × fator_dano_jogadores
```
- `vida_base` e `dano_base`: as tabelas de `03-inimigos.md` (valores de nível 1).
- `mult_categoria`: comum x1 / elite vida x3, dano x1,5 / mini-chefe vida x6, dano x1,8 (`03-inimigos.md`).
- **Fator de chefe** (corrige a duração da luta; os valores de vida dos chefes em `03-inimigos.md` são a base):

| Mapa | Nível da área do chefe | Vida base | Fator de chefe | Vida final (solo) |
|---|---|---|---|---|
| 1 Esgoto | 2 | 1.000 | x4,3 | ~4.800 |
| 2 Ruínas | 4 | 1.500 | x3,5 | ~7.300 |
| 3 Floresta | 6 | 2.000 | x3,4 | ~12.000 |
| 4 Cavalos | 8 | 2.500 | x2,5 | ~13.900 |
| 5 Aves | 10 | 3.000 | x2,5 | ~21.000 |
| 6 Deserto | 12 | 3.500 | x1,9 | ~22.700 |
| 7 Águas | 14 | 4.000 | x1,9 | ~33.400 |
| 8 Pântano | 16 | 4.500 | x1,5 | ~35.700 |
| 9 Serpentes | 18 | 5.000 | x1,5 | ~51.700 |
| 10 Inferno | 20 | 6.000 | x1,4 | ~72.900 |

(Esses valores são para o poder típico do jogador em cada faixa, seção 3.) Chefes de duas partes (Grendel e a Mãe) somam a vida final dividida entre os dois.

### 2.5 Escala por número de jogadores (`07-rede.md`)
| Jogadores | Vida do monstro | Dano do monstro | XP total do monstro | XP para cada jogador |
|---|---|---|---|---|
| 1 | x1,0 | x1,0 | x1,0 | 1,00 |
| 2 | x1,6 | x1,1 | x1,6 | 0,80 |
| 3 | x2,2 | x1,2 | x2,2 | 0,73 |
| 4 | x2,8 | x1,3 | x2,8 | 0,70 |

- A única coisa que muda com o número de jogadores é a **força dos monstros** (vida e dano). **Loot e ouro não escalam.**
- O **XP é dividido** entre os jogadores (`07-rede.md`). Em grupo cada um ganha menos XP **por monstro**, mas o grupo mata mais rápido, então o **XP por minuto** fica parecido com o do solo.
- O dano do monstro sobe +10% por jogador extra (proposta) para o grupo não ficar fácil demais.

## 3. Poder típico do jogador por nível

Hipóteses: equipamento do tier da faixa de nível, afixos médios (+15%), refino médio crescente, 60% dos pontos de atributo na estatística principal, bônus de ranks e passivas de 2% por nível. DPS sustentado = poder x 1,3 por segundo (mistura de ataque básico e habilidades).

| Nível | Arma (dano) | Poder | DPS solo | Vida do monstro comum (x vida base) |
|---|---|---|---|---|
| 1 | 10 | 22 | 29 | x1,0 |
| 4 | 18 | 35 | 49 | x1,4 |
| 8 | 29 | 52 | 77 | x2,2 |
| 12 | 39 | 68 | 108 | x3,5 |
| 16 | 53 | 88 | 149 | x5,5 |
| 20 | 72 | 113 | 202 | x8,6 |

- Exemplo, nível 8: Ratazana Mutante (110 de vida base) tem ~243 de vida; um Cavaleiro com 52 de poder usa `lance_thrust` (180%) = 94 por golpe, então precisa de ~3 golpes (~3 s).
- Exemplo, Warg (45 de vida base) no nível 4: ~63 de vida, morre com 1 a 2 habilidades.
- **Saltos de tier:** o poder sobe de uma vez ao trocar de material (níveis 2, 5, 9, 13 e 17), o que é desejado: a troca de equipamento deve ser sentida.

## 4. Experiência

```
xp_para_o_próximo_nível(n) = 700 × n          (nível 20 = 133.000 XP no total)
```
| Origem do XP | Valor (nível do monstro = L) |
|---|---|
| Comum | 5 x L |
| Elite | 25 x L |
| Mini-chefe | 100 x L |
| Chefe | 300 x L |
| Quest secundária | 20 x L x (número de monstros da missão ou 10) (proposta) |

- Um mapa tem ~40 monstros comuns por área (4 a 5 áreas), ~2 elites por área, 1 mini-chefe e 1 chefe, o que dá ~**1.400 x L** de XP por mapa limpo: o suficiente para **2 níveis por mapa**.
- **Esgoto (mapa 1, fechado por XP):** 7 tipos de monstro comum, **20 de cada (140), 4 de cada em cada um dos 5 setores**, todos de nível 1 e com a **mesma força** (vida 210, dano 16; data/monsters.json), mais os 3 chefes (os 2 mini-chefes iguais: vida 140, dano 15) e 3 quests. Soma de XP de quem limpa tudo: comuns 700 + chefes 800 + quests 900 (A Família na Garrafa 360, Garrafa do Tormento Eterno 270, Garrafa das Almas Condenadas 270) = **~2.400**: nível 3 (2.100) com ~300 de sobra. Mudou a quantidade ou o XP dos monstros, ajuste as quests para a soma voltar a ~2.400 (conferido em tests/rpg_tests.gd). Na Taverna, no início, só o Velho Bêbado oferece missão.
- Quem evita monstros sobe de nível mais devagar, e quem limpa tudo sobe um pouco mais rápido (fica mais forte para o chefe).
- Bebida da taverna: +5% de XP na próxima missão (`04-tortuga-e-missoes.md`).
- Sem perda de XP ao cair em combate.

## 5. Ouro e economia

### 5.1 Renda por mapa (solo, limpando quase tudo, vendendo valiosos)
| Mapa | Renda alvo |
|---|---|
| 1 | ~600 |
| 2 | ~1.000 |
| 3 | ~1.500 |
| 4 | ~2.000 |
| 5 | ~3.500 |
| 6 | ~4.000 |
| 7 | ~5.000 |
| 8 | ~6.000 |
| 9 | ~7.000 |
| 10 | ~7.500 |

Fórmula de partida: `renda ≈ 600 × mapa^1,1`. Vem de: ouro direto dos monstros (comum 0,5 x L, elite x6, mini-chefe x30, chefe 50 x L), baús, valiosos do tesouro e vendas. Os valores dos valiosos em `05-itens-e-loot.md` (150 a 1.500) estão quase planos entre mapas; nos mapas finais conta-se com **mais unidades** de valiosos e com ouro direto maior. Ajustar a tabela de valiosos se a renda real ficar fora da meta.

### 5.2 Valor e preço de equipamentos
```
valor_base = 20 × mult_material × (1 + 0,15 × nível_do_item) × fator_raridade
```
| Raridade | Fator |
|---|---|
| Comum | 1 |
| Mágico | 2,5 |
| Raro | 6 |
| Único | 15 |
| Lendário | 40 (só para seguro; não é vendido nas lojas) |

| Operação | Preço |
|---|---|
| Venda ao NPC | **25%** do valor (`05-itens-e-loot.md`) |
| Compra na Rua Principal de Tortuga (comuns) | **2x** o valor |
| Compra no Mercado Pirata | **3x** |
| Compra no Mercado Real / Capital | **4x** |

Exemplos (valor base → compra na loja certa): Espada de Aço comum nível 6 = 87 → 175 em Tortuga; item raro de cobre nível 10 = 600 → 2.400 na Capital (cerca de **meio mapa de renda**); raro de ouro nível 20 = 2.400 → 9.600 na Capital (**mais que um mapa inteiro**, por isso o ouro vem principalmente de tesouros e do Ferreiro Real).

### 5.3 Consumíveis e serviços
| Item / serviço | Preço (proposta) |
|---|---|
| Poção de vida (cura 35% da vida máxima; recarga de 15 s compartilhada) | 12 + 6 x nível |
| Poção de recurso (restaura 40% do recurso máximo) | 10 + 5 x nível |
| **Poção Elemental** (decidido: 100 + 25 x nível; `02-0-elementos.md`) | 100 + 25 x nível |
| Poção Elemental Refinada (Capital) | o dobro |
| Pergaminho de refino normal | 40 x mult_material (ferro 64, aço 92, cobre 124, prata 160, ouro 200) |
| Pergaminho Abençoado | 6x o normal |
| **Patuá de Retorno** | 150 (empilha até 5) |
| **Portal do Macumbeiro** (por jogador) | 40 + 15 x nível da área |
| Redistribuir pontos (reset total) | 50 + 30 x nível |
| Bebida da taverna | 30 + 10 x nível |
| Bolsa pequena (+8 espaços; até 2 em Tortuga) | 300 e 800 |
| Bolsa grande (+12 espaços; até 2 na Capital) | 2.000 e 4.000 |

- Com as 4 bolsas a bolsa chega a **80 espaços** (partindo dos 40 da `05-itens-e-loot.md`).
- Baú de Tortuga e banco da Capital: gratuitos.
- **Refino:** chegar a +5 com pergaminho normal tem ~29% de sucesso partindo de +3 (0,65 x 0,45); falhar quebra o item em cristais. Com Abençoado, a falha só volta a +0. Para um item de aço: 3 pergaminhos seguros custam ~276, e cada tentativa de +4 e +5 outros 92 (mais o item, em caso de quebra) — isso torna o Abençoado valioso a partir do +4.

### 5.4 Morte
- **Sem perda de ouro, XP ou itens** ao cair.
- Solo: se o herói cair, volta ao **último checkpoint** da área.
- Co-op: o caído fica no chão esperando reanimação (3 s segurando o botão, `02-personagens.md`) por **45 s** (proposta); sem ajuda, reaparece no último checkpoint com 50% da vida. Se todos caírem, o grupo volta ao último checkpoint (`01-escopo.md`).
- Reanimar devolve 30% da vida (e 40% no `animal_rescue` do Invocador).

## 6. Equilíbrio entre classes

| Classe | Dano sustentado (relativo) | Dano em rajada | Sobrevivência | Papel |
|---|---|---|---|---|
| Cavaleiro | 85% | médio | **Muito alta** | Tanque; abre a luta |
| Ninja | 100% | **alto** (costas e crítico) | Alta | Tanque ágil e dano em alvo único |
| Arqueiro | 100% | alto (Tiro Preciso) | Baixa | Dano à distância e controle |
| Mago | 105% | muito alto (área) | Muito baixa | Dano em área; gasta mana |
| Invocador | 90% (os animais fazem parte) | médio | Baixa (compensa com animais) | Suporte, mais fácil no solo |

- Todo o dano das habilidades já é uma porcentagem do **poder** da classe (`02-personagens.md`); esta tabela é só a meta final de equilíbrio após testes.
- Os elementos têm ajuste parecido: **Fogo** é o de maior dano, **Água/Ar** de controle e **Terra** de proteção (`02-0-elementos.md`), então a diferença de dano entre elementos fica em ±10% no total.
- Mesma regra para o solo: o Invocador e o Cavaleiro aguentam sozinhos; os conjuradores precisam jogar com atenção.

## 7. Como testar

1. **Planilha ou script de simulação** (GDScript ou Python) que leia os arquivos de dados do jogo (itens, monstros, habilidades) e calcule por nível: poder, DPS, tempo para matar comum, elite, mini-chefe e chefe, e golpes aguentados por classe.
2. **Painel de treino** (`04-tortuga-e-missoes.md`, seção 5.2): confere o DPS e o dano por habilidade no jogo.
3. **Partidas de teste** com cada classe em cada mapa, anotando tempo de cada área e de cada chefe, nível ao entrar e ao sair, ouro ganho e gasto.
4. **Co-op:** repetir os chefes com 2 e 4 jogadores e comparar tempos (meta: ~30% mais rápido que solo).
5. Registrar os números ajustados nos arquivos de dados e **atualizar este documento** com os valores finais.

## 8. Decisões em aberto

- Dano +10% por jogador extra (proposta): manter?
- Tempo de espera do caído no co-op: 45 s (proposta) e reaparecer com 50% de vida?
- Valor dos valiosos: manter a tabela atual ou escalar por mapa?
- Fator de chefe ao longo dos mapas: manter os valores da seção 2.4 ou usar uma curva mais suave?
- Nível máximo continua 20 (novo jogo começa do zero); dificuldade maior: Pesadelo em `15-modos.md`.
- A Poção de vida de 35% com recarga compartilhada de 15 s é suficiente ou deve haver tipos diferentes?
