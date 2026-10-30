# Tutorial e Primeiros Minutos

> Versão 1 · 2026-10-30 · Como o jogador aprende o jogo sem parar a ação. Complementa `06-mundo-e-historia.md` (abertura), `04-tortuga-e-missoes.md`, `03-2-areas.md` (Esgoto), `08-controles.md`, `09-interface.md` e `13-balanceamento.md`
> Textos entram por chave de tradução (en, es, pt_BR). Números são propostas. Itens **em aberto** não devem ser decididos sem consultar o autor.

## 1. Princípios

- **Aprender jogando:** nada de telas longas de instrução. Cada dica aparece **na hora em que serve** e some sozinha.
- **Curto e opcional:** quem já conhece o gênero chega à primeira luta em ~10 minutos e pode desligar as dicas (**Opções → Jogabilidade → Dicas**).
- **O primeiro mapa é o tutorial:** o Esgoto (mapa 1) ensina o combate e a exploração, sem fase separada (`03-2-areas.md`).
- **Mesmas dicas com teclado e com controle**, mostrando o ícone do botão do último dispositivo usado (`08-controles.md`).
- **Solo e co-op iguais:** as dicas aparecem para cada jogador no seu PC; no co-op nada para o jogo.
- **Dica vista = dica guardada:** o personagem lembra quais dicas já viu (`tutorial_seen` no save do personagem, `11-saves.md`), então não repete em outra campanha.
- Voz do tutorial: **tom do jogo** (cínico, sombrio), em frases curtas. Quem fala é o **velho mercenário aposentado** do pátio de treino (proposta), ou apenas o texto na tela.

## 2. Linha do tempo (primeiros 10 a 15 minutos)

| Passo | Onde | O que acontece | O que o jogador aprende |
|---|---|---|---|
| 1 | Menu → **Criação de personagem** | Escolhe classe, elemento, sexo, nome, aparência; vê a história resumida do herói | Escolhas que mudam o jogo (classe, elemento) e que são só visuais (sexo, aparência) |
| 2 | **Abertura na taverna** (`06-mundo-e-historia.md`, seção 5) | Cada herói conta sua história; o grupo forma a companhia | Quem são os personagens; clima do jogo |
| 3 | **Velho bêbado** conta o tesouro do esgoto | Primeira missão no diário, com o ícone do elemento do alvo e da fraqueza (**Fogo**) | Missões, diário, **elemento e fraqueza** |
| 4 | **Taverna → Rua Principal** | Dica de **movimento** e de **interagir** (`interact`); pega o equipamento inicial | Andar, câmera, falar com NPC |
| 5 | **Loja do Boticário** | O jogo dá **150 de ouro** e recomenda comprar poções; o jogador abre a janela da loja | Comprar, ouro, atalho de poção |
| 6 | **Pátio de treino** (opcional, recomendado) | Bonecos de palha, painel de dano; boneco de Fogo mostra o **+50% de dano de Água** etc. | Ataque básico e forte, habilidades, recarga, **fraqueza** |
| 7 | **Altar/Mestre e Ferreiro** (só olhar) | Dica curta de que existem refino e redistribuição, para mais tarde | Que a cidade tem serviços |
| 8 | **Bueiro** (liberado pela missão) | Desce a escada para o Esgoto | Entrada do primeiro mapa |
| 9 | **Esgoto, área 1** (`sewers_01_drains`) | Tutorial de combate real, seção 3 | Combate, esquiva, bloqueio, poções, loot, mapa |
| 10 | **Esgoto, áreas 2 a 4** | Dicas pontuais: inventário/equipar, checkpoint, elite, mini-chefe, chefe | Resto dos sistemas |

- Os passos 5 e 6 **não são obrigatórios**: o bueiro só abre depois da conversa com o velho bêbado, e o jogo avisa (uma vez) se o jogador sair sem poções ("Você não vai querer descer sem poções").
- Para jogadores que **repetem a campanha** ou que desligaram as dicas, a taverna pode ser pulada com um botão (**Pular abertura**), mas as histórias dos heróis ficam disponíveis no bestiário/diário.

## 3. Esgoto, área 1: o tutorial de combate

Desenho da área (`sewers_01_drains`, nível 1, estreita): um corredor reto com bifurcações curtas, que **apresenta uma mecânica por vez**, como um nível de jogo comum.

| Trecho | Encontro | Dica na tela | Mecânica ensinada |
|---|---|---|---|
| Entrada | Nenhum monstro; um baú | "Aproxime-se do baú e aperte [interagir]" | Interagir, **loot individual** (só o jogador vê o seu) |
| 1 | **1 Rato Pestilento** (isolado) | "Aperte [ataque] para atacar" | Ataque básico, vida do monstro, número de dano |
| 2 | **3 Ratos** em bando | "Segure [ataque] para um golpe forte" | Ataque forte e estado do elemento |
| 3 | **Poça de lodo tóxico** no chão | "Evite o lodo: ele causa dano" | Perigo do ambiente |
| 4 | **Enxame de Ratos** (8) | "Use [habilidade 1]" — a classe tem 1 habilidade liberada no nível 1 | Habilidades, custo, recarga, recurso |
| 5 | **Ratazana Mutante** (investida com aviso) | "Aviso no chão: desvie com [esquiva]" | Telégrafo de ataque, esquiva (e aparar do Ninja / bloqueio) |
| 6 | Depois da luta, o herói está com **pouca vida** | "Beba uma poção com [poção de vida]" | Poções e atalhos |
| 7 | Itens caídos | "Aperte [pegar tudo] para recolher" | `pickup_all`, raridade por cor |
| 8 | Primeiro item equipável | "Abra o inventário em [inventário] e equipe o item" | Inventário, equipar, o item **aparece no corpo** |
| 9 | Subir de nível (por volta do fim da área) | "Você ganhou pontos: abra [habilidades]" | Atributos, árvore de habilidades |
| Saída | **Checkpoint** | "Progresso salvo" | Autosave, checkpoint, passagem para a próxima área |

- **Poucos monstros por vez** (1 a 3 nos primeiros trechos), sem ondas: cada grupo desperta ao chegar perto (`03-inimigos.md`, "Encontros por exploração").
- A área 1 dá ~**250 XP**, o bastante para o nível 2 com um pouco da área 2.
- A **classe** muda as dicas de combate:
  - **Cavaleiro:** o Esgoto é estreito, então ele **desmonta** logo no início; a dica explica o cavalo, o desmontar e que o cavalo espera na entrada.
  - **Ninja:** dica de esquiva como **teleporte curto** e do **aparar** no tempo certo.
  - **Arqueiro:** dica de Foco, que regenera parado.
  - **Mago e Invocador:** dica do recurso (Mana, Essência) e dos animais/bloqueio.

## 4. Dicas contextuais

Cada dica tem um ID, uma condição para aparecer e é mostrada **uma vez**.

| ID | Quando aparece | Mensagem (resumo) |
|---|---|---|
| `tip_move` | Primeiros segundos | Andar e mira (`move`, `aim`) |
| `tip_interact` | Perto de algo interagível pela primeira vez | Interagir |
| `tip_attack` | Primeiro monstro acordado | Ataque básico |
| `tip_charged` | Depois de 5 ataques básicos | Ataque forte |
| `tip_skill` | Primeira habilidade liberada e recurso cheio | Usar habilidade |
| `tip_dodge` | Primeiro golpe forte telegrafado | Esquiva e aviso no chão |
| `tip_potion` | Vida abaixo de 40% pela primeira vez | Poção |
| `tip_loot` | Primeiro item no chão | Pegar e raridade |
| `tip_equip` | Primeiro equipamento utilizável | Equipar |
| `tip_levelup` | Primeiro nível ganho | Pontos de atributo e habilidade |
| `tip_element` | Primeiro monstro com fraqueza diferente do elemento do jogador | Ícone do elemento e dano maior/menor |
| `tip_checkpoint` | Primeiro checkpoint | Salvar automático e Macumbeiro (`04-tortuga-e-missoes.md`) |
| `tip_map` | Primeira vez que o mapa revela algo | Mapa que se revela |
| `tip_revive` | Primeiro aliado caído (co-op) | Reanimar |
| `tip_ally_arrow` | Aliado fora da tela (co-op) | Seta na borda |
| `tip_elite` | Primeira elite | Elite e loot melhor |
| `tip_boss` | Entrando na arena da Rainha dos Ratos | Barra do chefe e fases |
| `tip_return` | Primeira vez perto de um portal de retorno | Voltar à cidade |
| `tip_shop` | Primeira loja aberta | Comprar e vender |
| `tip_refine` | Primeiro pergaminho de refino | Refino (`05-1-refino.md`) |
| `tip_elemental_potion` | Primeira Poção Elemental comprada | Trocar de elemento por expedição |
| `tip_mount` (Cavaleiro) | Primeira área aberta ou estreita | Montar e desmontar |

- Na tela: um balão pequeno com ícone do botão, até 2 linhas, **sem pausar o jogo** (no solo e no co-op).
- Todas ficam listadas no menu **Ajuda** (relê as dicas já vistas) para o jogador reler.
- Textos por chave: `TIP_MOVE`, `TIP_ATTACK`, … traduzidos nos 3 idiomas (`01-escopo.md`, seção 6).

## 5. Equipamento e recursos iniciais

| Item | Valor |
|---|---|
| Roupa | Só roupa de baixo de pano (`02-personagens.md`) |
| Arma | Arma básica de madeira da classe (adagas de treino, cajado, arco, livro, lança) |
| Poções | 3 de vida, 1 de recurso |
| Ouro | **150** |
| Habilidades | 1 liberada no nível 1; a segunda no nível 2 (`02-personagens.md`, progressão) |
| Atributos | Os iniciais da classe (nível 1) |
| Bolsa | 40 espaços, vazia exceto pelas poções |

- O primeiro equipamento utilizável cai no **Esgoto, área 1** (do tier ferro), para o jogador ver o item aparecer no corpo logo.
- No co-op, cada jogador tem o seu início; a taverna é compartilhada, mas o ouro e as poções são de cada um.

## 6. Solo e co-op

| Modo | Diferença |
|---|---|
| **Solo** | Os outros 4 heróis aparecem como NPCs na taverna e contam suas histórias; depois ficam em Tortuga (`06-mundo-e-historia.md`) |
| **Co-op** | Cada jogador conta a própria história na abertura; as dicas de reanimar, de setas e de troca aparecem no momento certo; quem entra no meio recebe só as dicas que ainda não viu |

- O host pode **pular a abertura** apenas se todos concordarem (aviso de confirmação).
- Jogadores experientes e novatos misturados: as dicas dependem do `tutorial_seen` de cada personagem, então só o novato vê as dicas.

## 7. Notas técnicas (Godot 4)

- Sistema `TipManager` (autoload): lê `tips.json` (ID, condição, chave de texto, ação, prioridade), consulta o estado do jogo e mostra no máximo **uma dica por vez** (fila com prioridade).
- Condições como sinais do jogo (primeiro monstro acordado, vida baixa, item no chão…), sem código especial por dica.
- O ícone do botão vem do Input Map e muda conforme o último dispositivo (`08-controles.md`).
- Estado salvo em `tutorial_seen` (lista de IDs) no personagem (`11-saves.md`).
- A abertura na taverna é uma sequência de diálogo com câmera simples (sem cinemática pesada, `01-escopo.md`, seção 8).
- Textos só por chaves de tradução; nenhum texto fixo.

## 8. Decisões em aberto

- Ouro inicial de 150 e 3 poções de vida: manter?
- Quem fala nas dicas: o velho mercenário do pátio (voz de personagem) ou só texto?
- **Pular abertura**: permitir sempre ou só a partir da segunda campanha?
- Tutorial de co-op (conectar, lobby) como tela de ajuda dentro do menu?
- Modo "ajuda extra" (mais dicas) para quem pedir?
