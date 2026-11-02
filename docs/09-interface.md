# Interface, Câmera e Visual

> Versão 1 · 2026-10-30 · Complementa `01-escopo.md` (câmera e tecnologia), `08-controles.md`, `02-personagens.md`, `05-itens-e-loot.md`, `05-1-refino.md`, `11-saves.md`
> Direção do autor: **visual e interface no estilo do 0 A.D. (menus medievais), com a câmera mais próxima, como em Dark Alliance.** Viagem entre mapas por **portais**.
> Números são propostas para ajustar em teste. Pontos marcados como **proposta** ou **em aberto** não devem ser decididos sem consultar o autor.

## 1. Direção visual

- **Referência de visual:** 0 A.D. — modelos de baixa/média contagem de polígonos, texturas pintadas à mão, cores terrosas, iluminação simples, leitura clara de longe.
- **Referência de câmera:** Dark Alliance — mais **perto** do personagem do que o 0 A.D., para o combate parecer direto e pesado.
- **Tom:** sombrio (neblina, lampiões, brasas, olhos brilhando), mas sempre legível. Nada de escuridão que esconda monstro ou item.
- **Leitura acima de tudo:** o jogador precisa distinguir de relance herói, aliados, monstros, itens no chão e áreas de perigo.

## 2. Câmera

| Item | Valor (proposta) |
|---|---|
| Ângulo | Inclinada para baixo, ~55° (ajustável entre 50° e 60° em teste) |
| Distância padrão | **Próxima**: o herói ocupa ~1/8 da altura da tela; vê ~14 m à frente e ~10 m para os lados |
| Zoom | Roda do mouse / botões do controle; vai de **muito próximo** (combate) a **médio** (explorar). Nunca chega à distância de um RTS |
| Rotação | **Fixa** (sem rotação livre) |
| Seguimento | Suave, com leve antecipação na direção do movimento; no Cavaleiro montado afasta um pouco com a velocidade |
| Paredes e objetos | Entre a câmera e o herói ficam **transparentes** ou desaparecem (corte por distância) |
| Co-op | Cada PC tem a sua câmera; jogadores podem se separar |

- Câmera mais próxima significa **menos coisas na tela**, o que ajuda o desempenho em vídeo integrado (`01-escopo.md`, seção 5).
- Por ver menos do mapa, o jogo precisa de **avisos fora da tela**: setas na borda indicando aliados distantes, o objetivo da missão e perigo se aproximando (seção 6).
- Monstros com ataques de longo alcance (Manticora, Estinfálias, Fênix) mostram uma **marca no chão ou aviso na borda** antes do golpe.
- Opção em **Vídeo → Câmera**: distância padrão (próxima / média / longa) e tremor de câmera (liga/desliga).
- Nos mapas, as áreas são pensadas para essa câmera: corredores e salas legíveis, sem exigir visão ampla.

## 3. HUD em jogo

Estilo medieval do 0 A.D. (seção 7): painéis de madeira escura e pedra com detalhes de metal, bordas simples, pouca transparência, ícones grandes. Fica nas bordas para não cobrir a ação.

```
┌────────────────────────────────────────────────────────────┐
│ [Aliados: retratos + vida]        [Missão ativa]  [Minimapa]│
│                                                            │
│                       (ação do jogo)                       │
│                                                            │
│ [Retrato][Vida][Recurso]  [Skills 1-4][Poções] [Buffs/Estados]│
│ [XP ──────────────────────────────────────── Nível]        │
└────────────────────────────────────────────────────────────┘
```

| Elemento | Onde | Conteúdo |
|---|---|---|
| **Retrato + vida + recurso** | Embaixo à esquerda | Barra de vida (vermelha) e do recurso da classe (Mana, Foco, Energia, Ímpeto, Essência), cada uma na sua cor; números pequenos |
| **Habilidades** | Embaixo ao centro | 4 slots (`skill_1` a `skill_4`) com ícone, tecla/botão, **recarga em relógio** e custo; slot fica cinza sem recurso |
| **Poções** | Ao lado das habilidades | Vida, recurso e Elemental (`potion_health`, `potion_mana`, `potion_elemental`), com quantidade; a Elemental mostra o elemento ativo e quanto falta da expedição |
| **Experiência** | Faixa fina na base | Barra de XP e nível |
| **Estados e buffs** | Acima da barra de vida | Ícones pequenos com tempo (queimando, molhado, escudo, bônus de estandarte…) |
| **Aliados** | Topo à esquerda | Retratos pequenos dos outros 1–3 jogadores com vida, nome e ícone do elemento; aliado caído pisca (pede reanimação) |
| **Missão ativa** | Topo à direita, abaixo do minimapa | Objetivo atual em 1–2 linhas, com o **ícone do elemento do alvo e da fraqueza** (`02-0-elementos.md`) |
| **Minimapa** | Topo à direita | Área atual, **revelada aos poucos conforme o jogador explora** (névoa sobre o que ainda não foi visto), aliados, objetivo, checkpoint; pode ser ampliado com `map` |
| **Elemento atual** | Junto ao retrato | Ícone do elemento de origem; muda para o temporário com Poção Elemental |
| **Recurso do Cavaleiro** | Junto à barra | Indicador montado / a pé |

### Informação sobre os monstros
- Barra de vida sobre o monstro, com o **ícone do elemento** ao lado.
- Elites e mini-chefes: barra maior e nome. Chefes: **barra grande no topo da tela**, com nome e fases.
- Número de dano: **maior e colorido** na fraqueza, **cinza e menor** quando resiste (`02-0-elementos.md`, seção 3); crítico com destaque.
- Itens no chão: brilho e etiqueta na cor da raridade (`05-itens-e-loot.md`), só os do próprio jogador (loot individual).

### Avisos
- Setas na borda para aliado fora da tela, objetivo e saída.
- Mensagens curtas no topo (checkpoint salvo, item raro, missão atualizada, subiu de nível).
- Indicador discreto de **salvando…** nos checkpoints (`11-saves.md`).
- Chat de texto e frases rápidas no canto inferior direito, que somem sozinhos depois de alguns segundos.

## 4. Menus e janelas

Abrem sobre o jogo no estilo medieval de pergaminho, madeira e ferro do 0 A.D. (seção 7). No solo o jogo pausa; no co-op, **não pausa** (a janela fica semitransparente e o herói fica vulnerável).

| Janela | Conteúdo |
|---|---|
| **Inventário e equipamento** | Boneco do herói com os slots (cabeça, corpo, mãos, pés, arma, mão secundária, barda do cavalo, 2 anéis, amuleto) + bolsa de 40 espaços (expansível, `05-itens-e-loot.md`, seção 8). Comparação com o item equipado ao passar o cursor. Arrastar para equipar, vender ou jogar fora |
| **Item (dica)** | Nome com material e refino ("Espada de Aço +3"), raridade na cor, valores base, afixos, requisitos, preço de venda |
| **Habilidades** | Árvore da classe e do elemento (10 habilidades, 5 ranks), pontos disponíveis, escolher as 4 ativas e os atalhos; mostra a versão a pé do Cavaleiro |
| **Atributos** | FOR, DES, INT, VIT, pontos livres, vida, poder da classe, resistências |
| **Diário de missões** | Principais e secundárias (até 5 ativas), com ícones do elemento e da fraqueza |
| **Bestiário** | Lenda, elemento, fraqueza e dica de cada criatura já ouvida (`03-1-bestiario.md`); fala do Bardo |
| **Mapa** | Mapa da área atual, **só a parte já explorada**, checkpoints, aliados, objetivo |
| **Troca entre jogadores** | Janela de troca confirmada pelos dois lados (`05-itens-e-loot.md`, seção 8) |
| **Opções** | Vídeo, áudio, controles (`08-controles.md`), idioma, jogabilidade (seção 8) |
| **Macumbeiro** | Lista dos checkpoints alcançados (por mapa e área, com nível e elemento), preço por jogador e botão de confirmar; aba para comprar o Patuá de Retorno |
| **Painel de treino** | Dano total, DPS, maior golpe, críticos, tempo; liga/desliga recursos e recargas livres, boneco que ataca; zerar e reiniciar (`04-tortuga-e-missoes.md`, seção 5.2) |
| **Portal** | Lista de destinos liberados com nível recomendado, elemento do mapa e do chefe, estado (nova / em andamento / concluída) e escolha entre primeira área ou último checkpoint; no co-op, o host escolhe e os outros confirmam |
| **Pausa (Esc)** | Continuar, opções, voltar à cidade (se permitido), sair para o menu |

- Tudo navegável **só com o controle**; ícones de botão trocam conforme o último dispositivo usado (`08-controles.md`).
- Textos sempre por chave de tradução; contêineres que se ajustam a textos ~30% maiores em espanhol e português (`01-escopo.md`, seção 6).

### Nas cidades
- **Lojas:** janela de compra e venda aberta ao interagir com a banca; abas por tipo de item; mostra o que a classe do jogador pode usar; botão "comprar tudo o que é meu" **(proposta)**.
- **Ferreiro:** janela de **refino** (escolher item + pergaminho, aviso da chance e do risco de quebrar, `05-1-refino.md`) e de crafting.
- **Mercado Pirata e Mercado Real:** estoque do dia por jogador; preço de venda dos valiosos.
- **Taverna:** diálogos com balões e retrato do NPC; escolha de aceitar ou recusar a missão; quadro de avisos.
- **Baú / Banco:** grade de itens ao lado da bolsa.
- **Altar:** redistribuir pontos pagando ouro.

## 5. Telas fora do jogo

| Tela | Conteúdo |
|---|---|
| **Menu principal** | Jogar solo, Hospedar LAN, Entrar na LAN, Personagens, Opções, Créditos, Sair; fundo com Tortuga à noite |
| **Seleção de personagem** | Lista de personagens salvos no PC (classe, elemento, nível, ouro) com o modelo 3D girando; criar, apagar, copiar |
| **Criação de personagem** | Escolher classe, elemento, sexo, nome, aparência (rosto, cabelo, barba, pele, extras da classe); prévia 3D com o herói padrão e o objeto pessoal; mostra a história resumida |
| **Escolha de campanha** | Campanhas salvas (no solo ou como host): mapa liberado, tempo de jogo, data; nova campanha, continuar, apagar (`11-saves.md`) |
| **Lobby LAN** | Lista de partidas encontradas (broadcast) e entrada manual por IP; sala com os jogadores, classes, elementos, versão; o host inicia. Recusa versão diferente |
| **Carregamento** | Arte da área, dica do jogo (por chave) e, nas viagens, efeito de runas do portal |
| **Idioma** | Escolha na primeira execução e em Opções (`01-escopo.md`, seção 6) |
| **Créditos** | Equipe, assets de terceiros (`CREDITS.md`), aviso de licença do Godot |
| **Fim de jogo / checkpoint** | Se todos caírem, tela curta e volta ao último checkpoint |

## 6. Legibilidade em combate (câmera próxima)

- **Telégrafo de ataques:** golpes fortes dos monstros mostram uma marca no chão (círculo, cone ou linha) antes do impacto; chefes têm marcas maiores e cor mais viva.
- **Cores dos elementos:** as mesmas na HUD, nos efeitos, nas auras e nos números (Água azul, Fogo vermelho-alaranjado, Terra verde/âmbar, Ar branco-violeta/amarelo).
- **Aliados:** anel colorido discreto no chão sob cada jogador, na cor do seu elemento; nome pequeno sobre o herói (liga/desliga).
- **Aura do refino:** fica atrás dos efeitos de habilidade e dos avisos dos monstros (`05-1-refino.md`, seção 5).
- **Efeitos de habilidade** semitransparentes e curtos; opção de **reduzir efeitos** para quem tem PC fraco ou acha confuso.
- **Daltonismo (proposta):** além da cor, cada elemento tem um **símbolo** próprio nos ícones.
- Limite de entidades e partículas na tela (`01-escopo.md`, seção 5).

## 7. Identidade visual do jogo (regra para todo o visual)

**Regra do autor:** tudo o que for implementado na parte visual do jogo — menus, janelas, HUD, personagens, roupas, cenário, objetos, efeitos, ícones, telas novas — **segue a mesma identidade visual**. Antes de fazer qualquer coisa visual nova, confira esta seção; se algo novo não se encaixa, **mude o novo** (ou proponha, aqui, uma mudança na identidade para o jogo todo). Nada de peça de um estilo ao lado de peça de outro: um visual de cada tipo vira bagunça.

**A identidade em uma frase:** *Tortuga à noite* — porto pirata medieval, sujo e vivo, visto em baixa luz com **ouro**, **azul-marinho de noite** e **vermelho de lacre** como cores de marca, sobre couro escuro, pergaminho e ferro velho.

| Item | Regra |
|---|---|
| **Paleta de marca** | Ouro (`#D4AB4A` com sombra `#735420` e brilho `#F7D985`), noite azul-marinho (`#12292F`/`#0A1519`), vermelho de lacre (`#8C1A10`), couro escuro (`#1C1511`), pergaminho (`#D9C294`), latão (`#8C6E33`), aço (`#B8C2C7`). Cores fora disso só para dar informação (elementos, raridades, vida/mana) |
| **Madeira, não** | Moldura de **madeira não é mais usada** em janelas e botões (era o estilo anterior). Madeira só como material do mundo (mesas, barracas, casco do navio) |
| **Janelas** | Couro escuro com **filete de ouro**, linha fina de latão por dentro e **cantoneiras de ouro com losango**; sombra suave. Pergaminho para conversas, diário, dicas e etiquetas |
| **Botões** | Couro escuro com aro de latão que **acende em ouro** no foco (nunca só pela cor: o foco também muda o aro); a ação principal de uma tela é um **lacre de cera vermelho** com aro de ouro; no menu principal, entradas soltas como linhas de um livro-razão, com uma barra de ouro ao lado da que está em foco |
| **Títulos** | **Pirata One** (gótica de pirata), em ouro com contorno escuro, sempre com o **divisor ornamental** (losango de ouro entre fios de latão) logo abaixo. Só títulos: texto corrido nunca usa gótica |
| **Texto** | **Alegreya** nas janelas e **IM Fell English** nas entradas do menu principal; tinta escura sobre pergaminho, creme sobre couro. Legível, com acentos do espanhol e do português |
| **Capa do menu** | O menu principal usa uma **imagem de capa sem texto** (`assets/ui/menu_cover.jpg`): os mercenários descansando sobre um monte de ouro, ruínas e céu de fim de tarde. O título é uma imagem em ouro com relevo e rosa dos ventos (`assets/ui/title.png`, gerada por `tools/ui/make_title.py` com a fonte Cinzel), e a coluna de botões do jogo (couro e latão) ficam por cima, à esquerda, sobre um véu escuro leve. A capa é arte pronta, não cena montada em código; para trocar, basta substituir o arquivo (16:9, sem texto) |
| **Janelas e diálogos** | **Pedaços de papel antigo**: fibras, manchas de umidade, pintas de ferrugem e bordas rasgadas e queimadas (gerado em código, `UiTheme._paper_image`), com texto em tinta escura e títulos em vermelho-lacre. Botões e campos são **couro texturizado** com pesponto e aro de latão. Submenus abrem sobre a mesma cena |
| **Mundo 3D** | Luz quente de tocha e lanterna em ambientes escuros, tons terrosos e dessaturados, madeira e pano **gastos** (nada de cor chapada e vibrante); materiais pintados com relevo (`PaintedTextures`) e peças dos kits livres. Personagens novos vestem **roupa medieval** (linho, couro, lã); cores vivas só em peças de gala |
| **Ícones** | Pintados, com contorno escuro; elementos com cores próprias (`02-0-elementos.md`) e símbolos gravados em medalhão |
| **Barras de vida e recurso** | Tubos de vidro com aro de latão; a vida em vermelho, cada recurso na sua cor |
| **Movimento** | Pouco e com propósito: um balanço lento, uma luz que pisca. Nada de animações vistosas de interface |
| **Sons de interface** | Madeira, couro, metal e papel; sem bipes sintéticos |

- **Diferença de tom entre cidades:** em **Tortuga** tudo parece mais sujo e remendado (madeira de barco, cordas, manchas); na **Capital Real** a mesma identidade fica **mais rica** (dourado mais presente, tecido nobre, madeira polida). A troca é só de tema (cores e texturas), automática ao entrar na cidade — mesmo `Theme` com duas variações (proposta).
- **Como aplicar:** o tema da interface fica em **um único arquivo** (`game/ui/ui_theme.gd`); telas novas usam as variações dele (`TitleLabel`, `GameTitle`, `MenuEntry`, `SealEntry`, `ParchmentPanel`, `HudPanel`) e `MenuPanel`/`OrnamentDivider`, nunca estilos soltos. A capa é `assets/ui/menu_cover.jpg`, carregada por `menu_scene.gd`; título e botões ficam em `main_menu.gd`. Janela de papel: `MenuPanel` ou, em menus próprios, `panel.theme = UiTheme.paper_theme()`. O divisor é `ornament_divider.gd`. Roupas e barracas: `clothing.gd` e `market_stall.gd`.
- **Revisão:** todo pedido de arte ou de interface é conferido em captura de tela do jogo, **ao lado das telas existentes**, antes de ser dado como pronto.
- Tudo feito com assets próprios ou livres (CC0, CC BY, CC BY-SA), registrados em `CREDITS.md`. As molduras são **9-patch** reaproveitadas em todas as janelas (poucas texturas, leve para vídeo integrado).
- **Escala da interface** ajustável (80% a 150%) para telas pequenas e grandes.
- No HUD em jogo (seção 3) o estilo é mais discreto: painéis pequenos nas bordas, com pouca moldura, para não cobrir a ação.

## 8. Opções

| Grupo | Itens |
|---|---|
| **Vídeo** | Resolução e escala de resolução, tela cheia, VSync, qualidade (baixo/médio/alto), sombras, distância de visão, aura dos heróis (completa/reduzida/desligada), câmera (distância e tremor), efeitos reduzidos, escala da interface |
| **Áudio** | Volume geral, música, efeitos, interface |
| **Controles** | Remapear, zona morta, mira assistida, vibração, inverter eixo Y (`08-controles.md`) |
| **Idioma** | English, Español, Português (BR) |
| **Jogabilidade** | Nomes sobre os heróis, números de dano, mostrar elemento dos monstros, legendas, aviso de perigo na borda, confirmar antes de vender raros |
| **Rede** | Nome do jogador, porta, mostrar latência |

- Opções salvas por PC, em `user://`, separadas dos saves de personagem e de campanha.

## 9. Notas técnicas (Godot 4)

- Interface em nós `Control` com `Theme` único; HUD em `CanvasLayer`.
- Marcas de perigo e anéis dos aliados como decalques ou malhas simples no chão (sem luzes dinâmicas).
- Câmera: `Camera3D` com suporte (`SpringArm3D` ou equivalente) e interpolação; transparência de paredes por shader de corte ou desvanecimento por distância.
- Minimapa: `SubViewport` com câmera ortográfica de baixa resolução, atualizada poucas vezes por segundo.
- **Mapa que se revela:** uma textura de máscara (uma por área) pintada conforme os jogadores andam (raio ~12 m ao redor de cada um); o servidor guarda **uma máscara única do grupo** e ela vai no save da campanha (`11-saves.md`). **Mapa compartilhado (decidido):** no co-op, a exploração de qualquer jogador revela o mapa para todos.
- Números de dano e barras de vida dos monstros como `Label3D`/`Sprite3D` reaproveitados em pool (sem criar nós a cada golpe).
- HUD só recebe dados via sinais (vida, recurso, recargas); a rede envia IDs e valores, nunca texto traduzido.

## 10. Decisões em aberto

- Distância exata da câmera e ângulo (decidir em teste com 4 jogadores na tela).
- Ícones de botão: estilo Xbox ou PlayStation conforme o controle detectado?
- Mostrar o nome dos aliados sempre ou só ao aproximar?
- Dicas de carregamento: quantas e sobre o quê?
- Botão "comprar tudo o que é meu" nas lojas: manter?
- Modo para daltônicos com símbolos nos elementos: manter?
