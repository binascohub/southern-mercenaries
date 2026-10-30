# Refino de equipamentos

> Versão 5 · 2026-10-30 · Melhorar equipamentos com **pergaminhos de refino**, inspirado no sistema de *enchant* do **Lineage 2** (decisão do autor). Complementa `05-itens-e-loot.md` (materiais e raridades) e `02-0-elementos.md` (cores dos elementos).
> Números são propostas para balancear depois.

## 1. Como funciona (estilo Lineage 2)

- O jogador usa um **Pergaminho de Refino** em um equipamento (pelo inventário, só **na cidade** — fora de combate).
- Cada uso tenta subir o equipamento **+1**, até o máximo de **+5** (decisão do autor: o jogador vai trocar de equipamento ao longo do jogo, pelos materiais mais fortes, então o refino não precisa ir longe).
- **Até +3 é seguro:** nunca falha.
- **+4 e +5 têm risco:** o refino pode **falhar**, e o que acontece depende do tipo de pergaminho (seção 3).
- **Quanto mais refinado, mais brilho aparece em volta do herói** (decisão do autor), como o brilho das armas no Lineage 2 — mas aqui é uma **aura ao redor do personagem**, **na cor do elemento do herói**, vista por todos no co-op (seção 5).
- O refino aparece no nome do item: **"Espada de Aço +4"**.

## 2. Pergaminhos

Existem pergaminhos **de arma** e **de armadura**, um para cada **material (tier)**. O pergaminho precisa ser do mesmo material do item.

| ID (exemplo) | Pergaminho | Onde conseguir |
|---|---|---|
| `scroll_refine_weapon_iron` / `scroll_refine_armor_iron` | Pergaminho de Refino de Arma/Armadura (Ferro) | Ferreiro de Tortuga, drops de monstros e elites |
| `…_steel` | (Aço) | Ferreiro de Tortuga, drops |
| `…_copper` | (Cobre) | Ferreiro Real (Capital), drops |
| `…_silver` | (Prata) | Ferreiro Real, drops |
| `…_gold` | (Ouro) | Só drops de mini-chefes e chefes, e tesouros |
| `blessed_scroll_refine_*` | **Pergaminho Abençoado** (de cada tier) | Raro: mini-chefes, chefes, tesouros, às vezes no Mercado Pirata |

- Itens de **pano/madeira** (tier 0) não podem ser refinados (são só o equipamento inicial).
- Lendários usam o pergaminho do tier do nível em que caíram.
- Pergaminhos são itens normais: empilham, podem ser vendidos e guardados no baú.

## 3. Chance e falha

| Refino tentado | Chance de sucesso (proposta) |
|---|---|
| +1, +2, +3 | **100%** (seguro) |
| +4 | 65% |
| +5 | 45% |

**Quando falha (+4 ou +5):**

| Pergaminho | Resultado da falha |
|---|---|
| **Normal** | O equipamento **se quebra** e vira **cristais do material** (ex.: Cristais de Aço), como no Lineage 2. Os cristais servem para o ferreiro fazer pergaminhos |
| **Abençoado** | O equipamento **não quebra**, mas o refino **volta a +0** |

- Antes de tentar +4 ou +5, o jogo mostra um aviso com a chance: "Este refino pode falhar e destruir o item. Continuar?"
- Efeito visual e sonoro diferentes para sucesso (o brilho sobe) e falha (o item racha e explode em cristais).
- **Proposta:** itens **únicos** e **lendários** nunca se quebram com pergaminho normal — na falha voltam a +0 (para ninguém perder o lendário de um chefe). Em aberto.

## 4. Bônus do refino

| Refino | Bônus nos valores base do item (dano da arma / armadura) |
|---|---|
| +1 | +5% |
| +2 | +10% |
| +3 | +15% |
| +4 | +25% (salto maior acima do seguro, como no Lineage 2) |
| +5 | +35% |

- O bônus vale só para os **valores base**; os afixos da raridade não mudam.
- Um item +5 é forte, mas o próximo material ainda é melhor: um Aço +5 (x2,3 × 1,35 ≈ x3,1) empata com um Cobre +0 (x3,1) — então vale trocar e refinar o novo.
- **Bônus de conjunto (proposta):** com **todas as peças de armadura em +4 ou mais**, o herói ganha +5% de vida.

## 5. A aura em volta do herói

- **Aura principal:** a intensidade depende do refino da **arma** (como o brilho de arma do Lineage 2).
- **Contorno no corpo:** se **todas as peças de armadura** estiverem em **+4 ou mais**, aparece também um brilho no contorno do corpo do herói (proposta).

| Refino da arma | Aura em volta do herói |
|---|---|
| +0 | Nenhum brilho |
| +1 | Brilho bem fraco no chão, em volta dos pés |
| +2 | Brilho suave em volta do herói |
| +3 | Brilho visível, envolvendo o corpo todo |
| +4 | Aura forte, pulsando + faíscas subindo |
| +5 | Aura máxima + partículas girando em volta do herói |

### Cor da aura = elemento do herói (decisão do autor)

| Elemento | Cor da aura | Partículas (+4 e +5) |
|---|---|---|
| Água | Azul | Gotas e névoa |
| Fogo | Vermelho-alaranjado | Brasas subindo |
| Terra | Verde-terroso / âmbar | Pequenas pedras e poeira flutuando |
| Ar | Amarelo-elétrico / branco | Faíscas e pequenos raios |

- Usar as **mesmas cores dos elementos** da interface e das habilidades (`02-0-elementos.md`), para o jogador reconhecer de longe o elemento de cada aliado.
- **Com Poção Elemental ativa**, a aura muda para a cor do elemento temporário enquanto a poção durar (proposta) — assim o grupo vê quem está com qual elemento.
- Lendários podem acrescentar um detalhe próprio à aura (proposta), mas a cor base continua sendo a do elemento.
- No **Cavaleiro montado**, a aura envolve herói e cavalo.
- A aura não pode atrapalhar a leitura do combate: fica **atrás** dos efeitos de habilidade e dos avisos de ataque dos monstros, com transparência.

## 6. Cristais e o ferreiro

- Itens quebrados viram **cristais** do material (quantidade proporcional ao nível do item e ao refino que ele tinha).
- O jogador também pode **cristalizar** de propósito um item que não quer mais (no ferreiro) — útil ao trocar por um material mais forte.
- O ferreiro usa cristais + ouro para **fazer pergaminhos normais** do mesmo tier (proposta: 10 cristais + ouro = 1 pergaminho).

## 7. Implementação (Godot, leve para vídeo integrado)

- **Aura:** um plano/cilindro simples em volta do herói com **shader aditivo** (emissão + transparência); cor pelo elemento atual e intensidade pelo refino da arma. **Sem luzes dinâmicas** extras.
- +4: pulsar com seno no shader. +4 e +5: poucas partículas (GPUParticles, 12–24 por herói, com a forma do elemento); somem quando a câmera está longe ou na qualidade "baixo".
- Opção em **Vídeo → Aura dos heróis: completa / reduzida / desligada**.
- **O sorteio do refino é feito no servidor (host)**, nunca no cliente; o resultado é salvo no item, dentro do save do personagem (`11-saves.md`), logo em seguida (para não dar para "fechar o jogo e tentar de novo").
- Pela rede vão só o nível da aura e o elemento atual; o cliente mostra.
- Dados: `items/refine.json` (chances, bônus) e `items/scrolls.json`; cores em `elements.json`.

## 8. Decisões em aberto

- Chances de +4 (65%) e +5 (45%): manter?
- Item normal que falha **quebra** (como no Lineage 2) — manter? Únicos e lendários protegidos?
- Aura muda de cor com a Poção Elemental (proposta)?
- Bônus de conjunto de armadura +4: manter?
