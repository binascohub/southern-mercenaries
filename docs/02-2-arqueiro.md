# Personagem — Arqueiro (`archer`)

> Versão 2 · 2026-10-30 · Detalha a classe Arqueiro de `02-personagens.md`
> Modelo de personagem: **misto** — herói fixo (nome, história, visual de referência); o jogador pode mudar o nome, a aparência e **escolher o sexo (masculino ou feminino)**.
> **Elemento:** escolhido na criação (Água, Fogo, Ar ou Terra); troca temporária com Poção Elemental. Regras em `02-0-elementos.md`.
> **Vestimenta:** começa só com roupa de baixo simples de pano e um arco simples; a roupa muda conforme os equipamentos encontrados (`02-personagens.md`, seção 1).
> Nome e números são propostas para revisar.

## 1. O herói

| Campo | Valor |
|---|---|
| Nome padrão | **Kael Thorne** (masculino) / **Kaela Thorne** (feminino) — o jogador pode trocar |
| Sexo | Escolhido pelo jogador: masculino ou feminino |
| Raça | Humano |
| Idade aparente | ~22 anos |
| Origem | Uma vila pobre do **reino que perdeu a guerra** (`06-mundo-e-historia.md`) |
| Arma | Arco e flecha |
| Alcance | À distância |
| Elemento | Escolhido pelo jogador: Água, Fogo, Ar ou Terra |
| Personalidade | Calado, prático e desconfiado; nunca desperdiça comida nem flecha; generoso com quem passa fome |

### História
(A história é a mesma para as duas versões; o texto usa a versão masculina.)

Kael nasceu numa vila pobre, onde o inverno levava a comida antes de levar o frio. **Passou fome quando criança** e viu os irmãos menores chorarem de fome. Decidiu que seria **o maior caçador da região** para que a família nunca mais ficasse sem comer. Treinou todos os dias: primeiro com estilingue, depois com um arco feito à mão. Antes dos quinze anos, era ele quem alimentava a casa.

Na adolescência, **a guerra chegou à vila**. O reino vizinho — rico e poderoso, o mesmo de onde vêm Dorian e Dália — invadiu, e o reino de Kael **perdeu a guerra**. Soldados queimaram as casas e os campos, e quando a fumaça baixou, **Kael estava sozinho**. Não sabia fazer mais nada além de caçar, e caçar animais não pagava o pão de um órfão. Então passou a caçar o que pagava melhor: monstros, recompensas, tesouros. **Virou mercenário.**

Hoje vive em Tortuga contando cada moeda, como contava cada flecha. Não confia em quase ninguém, mas sempre divide a comida.

- **Motivação:** dinheiro, para nunca mais passar fome. No fundo, quer reconstruir um lar.
- **Ligação com a campanha:**
  - Os **dois primeiros tesouros do jogo** são riquezas do **seu próprio reino**: o Tesouro Perdido da Guerra (no Esgoto de Tortuga) e o Cofre Real (nas ruínas do castelo).
  - O **mapa 2 é a sua terra**: as **Ruínas do Reino do Arqueiro**, tomadas por lobos e cães demoníacos.
  - Lutar ao lado de Dorian ou Dália, que vêm do reino que destruiu o seu, gera tensão no grupo (**proposta** de falas entre eles).
- **Gancho visual:** usa no pescoço um **dente da sua primeira caça**, preso num cordão.

## 2. Aparência

### Início do jogo
- **Roupa de baixo simples de pano** (cor crua), descalço.
- **Dente da primeira caça** no cordão do pescoço (sempre visível, por cima de qualquer roupa).
- **Arco simples** de madeira tosca e uma aljava de couro gasta com poucas flechas.
- Mãos calejadas, cicatriz pequena no queixo.

### Visual de referência (com o conjunto típico da classe)
- Capuz e capa curta de caçador, roupas de couro curtido, braçadeira no braço do arco.
- Botas de couro macio para andar sem barulho.
- Arco longo de madeira escura; as penas das flechas e a ponta brilham na cor do elemento.

| Elemento | Cor de referência das roupas | Detalhe visual das flechas |
|---|---|---|
| Água | Azul-acinzentado | Ponta de gelo, rastro de gotas |
| Fogo | Marrom-avermelhado | Ponta em brasa, rastro de faíscas |
| Ar | Cinza-claro | Rastro de vento e pequenos raios |
| Terra | Verde-musgo | Ponta de pedra, rastro de poeira |

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
| Pinturas de caça no rosto | 4 opções (incluindo nenhuma) |

- Sexo é só visual e de voz: **não muda atributos nem habilidades**.
- O resto do visual vem dos **equipamentos encontrados no mapa**.

## 3. O Arqueiro em cada elemento

| Elemento | Papel do Arqueiro | Suporte | Dificuldade |
|---|---|---|---|
| Fogo | Dano contínuo à distância, queima grupos | Fogueira que aumenta o dano dos aliados | Fácil |
| Água | Controle: congela e deixa lento; cura de apoio | Poça que cura | Média |
| Ar | O mais rápido; dano em cadeia com raios | Vento que acelera o grupo | Difícil |
| Terra | Atordoa e protege; o Arqueiro mais seguro | Escudo de pedra nos aliados | Média |

## 4. Recurso e Poder de Tiro

| Item | Valor |
|---|---|
| Foco inicial | 100 |
| Foco por ponto de DES | +1 |
| Regeneração parado | 15 por segundo |
| Regeneração andando | 5 por segundo |

O Foco regenera rápido quando o Arqueiro para de andar: o jogo dele é **atirar parado e se reposicionar**.

Todo dano e efeito do Arqueiro é calculado a partir do **Poder de Tiro (PT)**:

```
PT = dano_do_arco + (DES × 0,5)
```

## 5. Ações básicas

| Ação | Descrição | Custo | Dano |
|---|---|---|---|
| Ataque básico | Flecha rápida, alcance 16 m | 0 | 80% PT |
| Ataque forte | Segurar até 1,5 s; flecha carregada que atravessa 1 inimigo e aplica o estado básico do elemento | 0 | até 200% PT |
| Bloqueio | Não tem; no lugar, a esquiva do Arqueiro tem recarga menor | — | — |
| Esquiva | Rolamento curto (recarga 3 s) | 0 | — |

## 6. Habilidades

O Arqueiro tem **10 habilidades**: **7 de classe** + **3 do elemento** (suporte no nível 6, alvo único no 12, área final no 18), como em `02-0-elementos.md`, seção 5.2. Valores do rank 1; máximo rank 5.

### 6.1 Habilidades de classe (todos os elementos)

Todas são **imbuídas** do elemento atual: aplicam o estado básico dele e mudam de cor.

| Nível | ID | Habilidade | Tipo | Foco | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `precise_shot` | Tiro Preciso | Alvo único | 20 | 4 s | 220% PT | +20% | 20 m | Flecha carregada com **crítico garantido** |
| 2 | `back_leap` | Salto para Trás | **Evasão** | 15 | 8 s (-1 s por rank) | — | — | Salta 6 m para trás | Inimigos a até 4 m ficam 40% mais lentos por 2 s |
| 4 | `eagle_eye` | Olho de Águia | Passiva | — | — | +5% chance de crítico e +10% dano crítico | por rank | — | — |
| 8 | `spike_trap` | Armadilha de Espinhos | Área | 20 | 10 s | 120% PT | +12% | Raio 3 m | Prende quem pisar por 2 s (+0,25 s por rank); dura 20 s; até 3 armadilhas no chão |
| 10 | `arrow_fan` | Leque de Flechas | Área | 25 | 6 s | 90% PT por flecha | +9% | Cone de 12 m | Dispara 5 flechas em leque (+1 nos ranks 3 e 5) |
| 14 | `piercing_arrow` | Flecha Perfurante | Área (linha) | 30 | 8 s | 180% PT | +18% | Linha de 25 m | Atravessa todos os inimigos em linha |
| 16 | `mark_target` | Marcar Alvo | Suporte (grupo) | 20 | 15 s | +15% dano recebido | +3% | 25 m, dura 8 s | O alvo marcado recebe mais dano de todo o grupo |

### 6.2 Fogo (`fire`)

| Nível | ID | Habilidade | Tipo | Foco | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `hunters_campfire` | Fogueira do Caçador | **Suporte** | 30 | 20 s | +15% de dano | +3% | Aliados a até 6 m da fogueira, dura 8 s | Acende uma fogueira com uma flecha; aliados perto causam mais dano e seus golpes aplicam `burning` |
| 12 | `flaming_arrow` | Flecha Incendiária | **Alvo único** | 30 | 8 s | 320% PT | +30% | 20 m | Flecha em chamas; `burning` com o dobro do dano |
| 18 | `fire_rain` | Chuva de Fogo | **Área final** | 60 | 30 s | 520% PT no total | +50% | 20 m, raio 6 m, 5 s | Flechas em chamas caem do céu; chão em chamas |

### 6.3 Água (`water`)

| Nível | ID | Habilidade | Tipo | Foco | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `spring_arrow` | Flecha da Fonte | **Suporte** | 35 | 15 s | Cura 25% PT por s | +5% | Poça de raio 5 m, dura 6 s | Flecha no chão abre uma fonte que cura aliados e molha inimigos (`soaked`) |
| 12 | `frost_arrow` | Flecha de Gelo | **Alvo único** | 30 | 8 s | 300% PT | +30% | 20 m | Se o alvo estiver `soaked`, fica `frozen` 2 s |
| 18 | `hail_storm` | Chuva de Granizo | **Área final** | 60 | 30 s | 500% PT no total | +50% | 20 m, raio 7 m, 6 s | Deixa lento; quem ficar 3 s dentro fica `frozen` |

### 6.4 Ar (`air`)

| Nível | ID | Habilidade | Tipo | Foco | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `hunters_wind` | Vento do Caçador | **Suporte** | 30 | 20 s | +30% velocidade | +5% | Aliados a até 8 m, dura 8 s | Aliados andam e atacam mais rápido |
| 12 | `thunder_arrow` | Flecha Trovão | **Alvo único** | 30 | 8 s | 330% PT | +30% | 20 m | Atinge como um raio; aplica `shocked`; **Eletrocuta** alvo molhado |
| 18 | `storm_volley` | Saraivada da Tempestade | **Área final** | 60 | 30 s | 550% PT no total | +55% | 20 m, raio 8 m, 4 s | 12 flechas-raio; cada uma salta para mais 2 inimigos |

### 6.5 Terra (`earth`)

| Nível | ID | Habilidade | Tipo | Foco | Recarga | Dano / efeito (rank 1) | Por rank | Alcance / área | Descrição |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `bulwark_arrow` | Flecha Baluarte | **Suporte** | 30 | 16 s | Escudo de 120% PT | +15% | Aliados em raio de 5 m, dura 8 s | Flecha cravada no chão ergue pedras que protegem os aliados com um escudo |
| 12 | `boulder_arrow` | Flecha Rompe-Rocha | **Alvo único** | 30 | 8 s | 320% PT | +30% | 18 m | Flecha pesada de pedra; aplica `stunned` 1,5 s |
| 18 | `stone_rain` | Chuva de Pedras | **Área final** | 60 | 30 s | 500% PT no total | +50% | 20 m, raio 7 m, 5 s | Pedras caem do céu e aplicam `knocked_down` |

## 7. Estilo de jogo

- **Solo:** arma armadilhas na passagem, salta para trás quando os monstros chegam perto, atira parado para recuperar Foco. `piercing_arrow` em corredores.
- **Em grupo:** fica atrás do Cavaleiro e do Ninja; marca o chefe com `mark_target`; usa o crítico garantido em alvos congelados pela Água.
- **Contra voadores** (Mapa das Aves): é a classe mais útil, porque acerta de longe o que os tanques não alcançam.
- **Pontos fracos:** pouca vida, sem bloqueio, Foco cai rápido se precisar correr muito; sofre contra matilhas que cercam (Wargs) e contra a Harpia, que agarra e rouba poções.

## 8. Equipamentos

Todos aparecem no corpo do personagem quando equipados.

| Slot | Itens | Visual |
|---|---|---|
| Arma | Arcos curtos (mais rápidos) e longos (mais dano). Começa com **arco simples de madeira** | Madeira → ferro → aço → cobre → prata → ouro (reforços e ponteiras no material) |
| Mão secundária | **Aljavas** (bônus às flechas: dano de elemento, chance de atravessar, crítico) | Vazio: aljava gasta inicial |
| Cabeça | Capuzes, chapéus de caçador, máscaras de pele | Vazio: cabelo à mostra |
| Corpo | Roupas de couro, peles, armaduras médias leves | Vazio: roupa de baixo de pano |
| Mãos | Braçadeiras e luvas de arqueiro | Vazio: mãos nuas, calejadas |
| Pés | Botas de couro macio | Vazio: descalço |
| Acessórios | 2 anéis, 1 amuleto | O dente da primeira caça fica sempre visível |

- Os lendários do Arqueiro nos dois primeiros tesouros (Esgoto e Ruínas) são peças do **arsenal real do seu próprio reino** (proposta: um deles é o arco do antigo caçador-mor do rei).

## 9. Animações necessárias

Mesmo conjunto para os dois sexos e os quatro elementos (o elemento muda só os efeitos visuais). As animações precisam funcionar com qualquer combinação de equipamentos (personagem modular, mesmo esqueleto):

`idle`, `walk`, `run`, `shoot` (tiro rápido), `shoot_charged` (puxar e segurar a corda), `shoot_volley` (leque/chuva para o alto), `place_trap` (agachar e armar), `back_leap`, `dodge_roll`, `hit`, `downed`, `revive`, `death`, `victory`.

## 10. Falas (exemplos, PT-BR)

Falas neutras, servindo para os dois sexos.

| Situação | Fala |
|---|---|
| Início do jogo | "Um arco, umas flechas e fome. Já comecei com menos." |
| Foco baixo | "Calma… respira… mira." |
| Subiu de nível | "Mais forte. Mais bem pago." |
| Achou comida/poção | "Nunca recuso comida." |
| Achou valioso | "Isso compra um inverno inteiro." |
| Abriu o tesouro do Esgoto | "Essas moedas… têm o brasão do meu reino." |
| Chegou às Ruínas | "Era aqui. Era a minha terra." |
| Perto de Dorian ou Dália (proposta) | "Foi o seu rei que queimou a minha vila. Não esqueço." |
| Perto de um chefe | "Essa é a maior caça da minha vida." |
| Aliado caído | "De pé! Ninguém fica pra trás. Não de novo." |
| Habilidade final (Fogo) | "Que chova fogo!" |
| Habilidade final (Água) | "Congela!" |
| Habilidade final (Ar) | "Tempestade!" |
| Habilidade final (Terra) | "Cuidado com a cabeça!" |

## 11. Decisões em aberto

- Arcos curtos e longos como dois tipos de arma, ou um tipo só?
- A vila do Arqueiro aparece dentro do mapa das Ruínas (com uma cena ou missão pessoal)?

## Visual do equipamento por rank (implementado)

O Arqueiro troca de roupa por **rank**, de **D** (a mais simples) a **S** (a mais rara e melhor), seguindo a referência do autor (`clothes.jpeg`, níveis 1 a 5). Cada peça (corpo, cabeça, mãos, pés) troca separadamente; o rank sai do material da peça (pano e ferro = D, aço = C, cobre = B, prata = A, ouro = S). Vale para os dois sexos. Código em `game/actors/class_gear.gd` e `game/actors/gear_kit.gd`; dá para ver cada rank na tela de criação do personagem ("Equipamento").

D túnica verde esfarrapada com corda; C jaqueta de couro marrom com capuz e bandoleira; B túnica verde com capa, colete de tiras e cinto; A escamas e malha verdes, ombreiras de couro e gola de malha; S armadura élfica verde e dourada, capa, folhas nos ombros e gema esmeralda.
