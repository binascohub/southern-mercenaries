# Escopo — Southern Mercenaries

> Versão 11 · 2026-10-30 · Autor: Fernando

## 1. Visão geral

**Southern Mercenaries** é um RPG de ação com **visão de cima**, como em *Baldur's Gate: Dark Alliance II*, para PC com **Windows e Linux**. Deve ser **leve o bastante para rodar sem placa de vídeo dedicada** (referência visual e de desempenho: [0 A.D.](https://play0ad.com/)). Jogável sozinho ou em co-op de 1 a 4 jogadores pela rede local (LAN). **Open source sob GPL-3.0**, publicado no GitHub, com download por um website próprio (`10-distribuicao.md`). **Três idiomas: inglês, espanhol e português** (seção 6).

- **Premissa:** os heróis são **mercenários** que se conhecem na taverna de **Tortuga** — cidade portuária sem rei e sem regras, nascida do pós-guerra — e vão atrás dos **tesouros guardados por chefes demoníacos**. **Lúcifer**, ganancioso, quer todo o ouro do mundo e está dominando terras e tesouros em segredo. Ver `06-mundo-e-historia.md`.
- **Campanha em 4 atos e 10 mapas:** abertura em Tortuga → tesouro do reino derrotado (Esgoto e Ruínas) e mapas 3–5 → **Capital Real** (cidade do Cavaleiro, aonde ele leva o grupo para conhecer o **Bobo da Corte**) e mapas 6–9 → **resgate do Bobo** no Inferno e Lúcifer. Final com gancho para uma continuação.
- **Tom:** sombrio (dark). Criaturas míticas reais e animais contaminados, corrompidos pelo inferno.
- **O que trazer de Dark Alliance 2:** câmera de cima, combate direto e rápido, classes bem distintas, muito loot, cidade-base entre missões, mapas divididos em áreas curtas, campanha inteira jogável em grupo.
- **O que muda:** cada jogador no seu PC, conectados pela LAN (sem tela dividida).
- **Público:** o autor, família e amigos na mesma rede; e qualquer um que baixar (open source).
- **Meta da v1.0:** campanha completa de **10 mapas em 41 áreas** (estimativa: 10 a 13 horas), jogável do início ao fim solo ou em grupo.

## 2. Câmera e mapas

- **Visão de cima, inclinada e próxima** (estilo Dark Alliance): olhando para baixo em ângulo de ~55°, mais perto do personagem do que no 0 A.D. Visual e interface no estilo do 0 A.D. Detalhes em `09-interface.md`.
- **Câmera segue o personagem** de cada jogador, no PC dele. Os jogadores podem se separar no mapa.
- **Sem rotação livre** da câmera; zoom limitado (de muito próximo a médio).
- Paredes e objetos entre a câmera e o personagem ficam **transparentes** ou somem, para o personagem estar sempre visível.
- Mapas pensados para essa visão: corredores, salas e áreas abertas lidos de cima, com caminhos claros e segredos em cantos.
- **Cada mapa é dividido em 4 ou 5 áreas** (cenas separadas, com checkpoint na entrada) — ver `03-2-areas.md`.
- Cada mapa tem **áreas abertas** (o Cavaleiro luta montado) e **áreas estreitas** (o Cavaleiro desmonta).
- A visão de cima ajuda o desempenho: menos coisas na tela ao mesmo tempo e sem horizonte distante para desenhar.

## 3. Mecânicas centrais

### Combate
- Movimento livre com WASD ou **controle USB**; mira com mouse ou analógico direito. Controles configuráveis (`08-controles.md`).
- Ataque básico, ataque forte, esquiva, bloqueio.
- 4 habilidades ativas por personagem em atalhos, com custo de recurso e tempo de recarga.
- Poções de vida e recurso em atalhos rápidos.
- Inimigos com padrões simples e legíveis; mini-chefes; chefes com fases.

### Classes e elementos
- 5 classes: Cavaleiro (cavalo + lança), Ninja (adagas), Arqueiro (arco e flecha), Mago (cajado + magia), Invocador (livro e animais amigos). Ver `02-personagens.md` e os arquivos de cada classe.
- Cada personagem escolhe um elemento de origem: Água, Fogo, Ar ou Terra. Pode trocar temporariamente com **Poção Elemental**. Ver `02-0-elementos.md`.
- **Todo monstro tem um elemento e uma fraqueza** (ciclo Água → Fogo → Terra → Ar → Água). As histórias da taverna e do Bobo da Corte revelam a fraqueza.
- O jogador escolhe o sexo do herói (masculino ou feminino).

### Progressão
- Experiência e níveis (nível máximo 20 na v1.0; cerca de 2 níveis por mapa).
- Pontos de atributo (FOR, DES, INT, VIT) a cada nível.
- 10 habilidades por classe (parte da classe, parte do elemento).

### Loot, itens e ouro
- Raridades: comum, mágico, raro, único e **lendário** (só nos tesouros dos chefes).
- Equipamentos aparecem no corpo; todos começam só com roupa de baixo de pano.
- **Valiosos** dos tesouros são vendidos aos piratas no Mercado Pirata do porto, que também vende itens roubados pelo mundo.
- Loot individual por jogador (cada um vê o seu, sem disputa).
- **Ouro individual:** cada jogador tem o seu.
- Detalhes em `05-itens-e-loot.md`.

### Cidades-base
- **Tortuga** (Atos 1–2, mapas 1–5): só a **Taverna** tem interior (abertura, histórias que geram missões e revelam fraquezas); as lojas ficam na **Rua Principal**; o **Mercado Pirata** fica no **porto**; o **bueiro** leva ao Esgoto e o **Portal** do porto leva aos demais mapas. Ver `04-tortuga-e-missoes.md`.
- **Capital Real** (Atos 3–4, mapas 6–10): liberada depois do mapa 5, quando o Cavaleiro leva o grupo ao Bobo da Corte; comércio mais elevado (itens melhores e mais caros); missões entregues pelo Bobo. Ver `04-1-capital-real.md`.

### Saves
- Personagem salvo no PC de cada jogador; campanha salva no PC do host; autosave nos checkpoints; continuar depois no solo ou no co-op (`11-saves.md`).

## 4. Multiplayer em LAN

- **Modelo:** host-cliente. Um jogador hospeda (servidor autoritativo dentro do jogo); os demais entram.
- **Solo:** o jogo sobe o mesmo servidor localmente, sem rede. Um só código para solo e multiplayer.
- **Descoberta:** busca automática na LAN (broadcast UDP) + conexão manual por IP.
- **Windows e Linux jogam juntos** na mesma partida (mesma versão do jogo obrigatória; o host recusa versão diferente).
- **Idiomas diferentes na mesma partida:** cada jogador vê o jogo no seu idioma. A rede só envia **IDs** (de itens, falas, missões), nunca texto traduzido; o chat livre vai como digitado, e as frases rápidas são traduzidas no PC de quem recebe.
- **Jogadores:** 1 a 4. Dificuldade escala com o número de jogadores (vida dos inimigos e loot).
- **Entrar no meio:** permitido; o jogador surge ao lado do host.
- **Personagens:** salvos no PC de cada jogador e levados para qualquer partida (estilo Diablo 2 "open").
- **Campanha:** progresso salvo no PC do host (missões, bestiário, relíquias, preços e estoque do Mercado Pirata).
- **Queda e revive:** aliado reanima o caído; se todos caírem, volta ao último checkpoint.
- **Chat de texto** simples e frases rápidas.

## 5. Plataforma e tecnologia

- **Plataformas:** PC **Windows 10/11 x86_64** e **Linux x86_64**, com o mesmo projeto e as mesmas funcionalidades.
- **Requisito central de desempenho:** rodar bem em vídeo integrado (Intel UHD/Iris, AMD Radeon Vega), meta de 60 FPS em 720p–1080p com 4 jogadores na tela.
- **Engine:** Godot 4 (versão estável fixada no projeto), com o renderizador **Compatibility (OpenGL 3.3)**, feito para GPUs integradas e hardware antigo.
- **Linguagem:** **GDScript** (recomendado: mais simples, sem dependência do .NET, export mais leve). C# só se o autor preferir.
- **Rede:** MultiplayerAPI do Godot sobre ENet (UDP), com MultiplayerSynchronizer, MultiplayerSpawner e RPCs.
- **Controles:** Input Map do Godot com ações; teclado/mouse e controle USB, remapeáveis (`08-controles.md`).
- **Visual:** 3D no estilo do 0 A.D.: modelos de baixa/média contagem de polígonos, texturas pintadas, iluminação simples. Câmera de cima (seção 2). Paleta escura, com neblina simples e brilhos (fogo, olhos, magias) para o clima sombrio.
- **Orçamento de desempenho:**
  - poucas luzes dinâmicas; sombras simples;
  - sem pós-processamento pesado;
  - limite de entidades ativas na tela (monstros + animais amigos do Invocador);
  - partículas simples para os elementos;
  - personagem modular com malhas juntadas após trocar equipamento;
  - cada área de mapa é uma cena própria; Tortuga e Capital com poucas cenas cada; mar com plano animado simples;
  - níveis de qualidade (baixo/médio/alto) e escala de resolução.
- **Assets:** apenas assets **próprios ou com licença livre compatível com open source** (CC0, CC BY, CC BY-SA): Kenney, Quaternius, OpenGameArt, Poly Pizza. **Assets pagos que proíbem redistribuição (ex.: Synty) e Mixamo não podem ir para o repositório.** Toda origem/licença registrada em `CREDITS.md`. Esqueletos compartilhados por família de monstros (ver `03-inimigos.md`). Dois corpos base por herói (masculino e feminino) com o mesmo esqueleto.
- **Licença:** código sob **GPL-3.0**; bibliotecas e plugins usados precisam ser compatíveis (`10-distribuicao.md`).
- **Dados do jogo:** classes, elementos, itens, monstros, bestiário, NPCs, lojas, áreas e modelos de missão em arquivos de dados (Resources do Godot ou JSON), separados do código, fáceis de balancear. **Os dados guardam chaves de tradução, não texto** (seção 6).
- **Versionamento:** Git + GitHub, repositório público `southern-mercenaries`; esta documentação fica em `docs/`.
- **Distribuição:** builds automáticas pelo GitHub Actions, instaladores nos GitHub Releases e website no GitHub Pages (`10-distribuicao.md`).

## 6. Idiomas

- **3 idiomas na v1.0:** **inglês (`en`)**, **espanhol (`es`)** e **português do Brasil (`pt_BR`)**. Todos completos: menus, HUD, itens, habilidades, bestiário, falas da história, missões, enigmas da Esfinge e tutoriais.
- **Idioma de origem dos textos:** português (a documentação e a história são escritas em PT-BR).
- **Tradução:** feita pelo Claude ao implementar cada texto (as 3 colunas preenchidas juntas), **sem revisão externa** (decisão do autor). Manter o tom sombrio e cínico das falas em todos os idiomas, não traduzir ao pé da letra.
- **Escolha do idioma:** na primeira vez que o jogo abre, ele usa o idioma do sistema (se for um dos 3; senão, inglês) e mostra a tela de escolha. Pode trocar a qualquer momento em **Opções → Idioma**, sem reiniciar.
- **Implementação (Godot):**
  - sistema de tradução do Godot (`TranslationServer`, função `tr()`) com arquivos **CSV** (`locale/textos.csv`, colunas `keys,en,es,pt_BR`) ou **gettext `.po`** (melhor para colaboradores open source — **em aberto**);
  - **nenhum texto fixo no código ou nas cenas**: tudo por chave (ex.: `ITEM_FIREBALL_NAME`, `NPC_OLD_DRUNK_QUEST1_LINE1`);
  - os arquivos de dados (`/data`) referenciam as chaves;
  - interface com espaço para textos mais longos (espanhol e português costumam ser ~30% maiores que inglês) — usar contêineres que se ajustam;
  - fonte com acentos e caracteres do espanhol (á, é, ñ, ¿, ¡).
- **Nome do jogo:** **"Southern Mercenaries" em todos os idiomas** (não é traduzido).
- **Nomes próprios** (Dorian, Dália, Tortuga, Cérbero…) seguem a forma de cada idioma quando houver (ex.: Cérbero → Cerberus / Cerbero; Jörmungandr igual).
- **Website** também nos 3 idiomas (proposta).
- **Comunidade:** novos idiomas podem ser adicionados por colaboradores (proposta: Weblate grátis para projetos open source).

## 7. Conteúdo da v1.0

- **10 mapas** em **41 áreas**, cada mapa com uma família de criaturas, um mini-chefe e um chefe que guarda um tesouro (ver `03-inimigos.md` e `03-2-areas.md`):
  1. Esgoto de Tortuga — Rainha dos Ratos (Tesouro Perdido da Guerra)
  2. Ruínas do Reino do Arqueiro — Cérbero (Cofre Real)
  3. Floresta Escura — Leshy
  4. Cavalos Míticos — Pégaso
  5. Aves — Fênix
  6. Deserto — Esfinge
  7. Águas — Kraken
  8. Pântano — Grendel e a Mãe de Grendel
  9. Serpentes — Jörmungandr
  10. Inferno — Lúcifer (e o resgate do Bobo da Corte)
- **Tortuga:** cidade-base com taverna (única construção com interior), Rua Principal com as lojas, porto com o Mercado Pirata, bueiro.
- **Capital Real:** segunda cidade-base, Avenida Real com lojas mais caras, pátio do castelo com o Bobo da Corte.
- **Classes:** 5, cada uma com 4 elementos e versões masculina e feminina.
- **Bestiário:** lendas reais de cada criatura, com pistas de fraqueza (`03-1-bestiario.md`).
- **Itens:** ~60 itens base + afixos + únicos + 1 lendário por classe por chefe + valiosos por mapa + itens piratas + itens reais da Capital.
- **História:** abertura na taverna (cada herói conta sua história), histórias da taverna e do Bobo, textos curtos entre os mapas, final com gancho.
- **Idiomas:** en, es, pt_BR (seção 6).
- **Áudio:** trilha e efeitos com licença livre. Sem dublagem (só texto), então a tradução não exige regravar áudio.

## 8. Fora do escopo (v1.0)

- Multiplayer pela internet, matchmaking, servidores dedicados.
- Tela dividida no mesmo PC.
- PvP.
- Geração procedural de mapas (mapas feitos à mão; só as missões secundárias são geradas).
- Câmera livre / terceira pessoa.
- Interiores além da Taverna.
- Navegação de navio jogável (as viagens entre mapas são feitas por **portais**, com tela de carregamento).
- Mais de 5 classes, dublagem, cinemáticas.
- Outros idiomas além de en, es e pt_BR (podem vir da comunidade depois).
- macOS e consoles.
- Publicação em loja (Steam). Itch.io é opcional (`10-distribuicao.md`).
- **Continuação:** o reino do primo da família real (gancho do final) fica para um próximo jogo/expansão.

## 9. Fases de desenvolvimento

1. **Protótipo de combate (solo):** personagem andando com a câmera de cima, atacando e matando monstros simples numa sala, com teclado e controle. **Pipeline de build Windows + Linux e sistema de tradução (chaves + 3 idiomas) funcionando desde aqui.**
2. **Rede básica:** host e cliente na LAN, 2 jogadores lutando contra os mesmos monstros (testar Windows com Linux).
3. **Sistemas de RPG:** atributos, níveis, inventário, equipamento modular, loot, poções, ouro, saves.
4. **Elementos:** ciclo de fraquezas, estados, combos, Poção Elemental.
5. **Classes e habilidades:** as 5 classes com os 4 elementos. Ordem sugerida: Mago, Arqueiro, Ninja, Invocador, Cavaleiro (o cavalo e o desmontar são os mais trabalhosos).
6. **Tortuga:** abertura na taverna, histórias e missões, Rua Principal com as lojas, porto com o Mercado Pirata, bueiro.
7. **Esgoto de Tortuga completo (vertical slice):** as 4 áreas, da história do velho bêbado à Rainha dos Ratos e ao Tesouro Perdido da Guerra, solo e em grupo, nos 3 idiomas. **Primeira versão pública (v0.1) no GitHub.**
8. **Mapas 2 a 5**, depois **Capital Real** e o Bobo da Corte, depois **mapas 6 a 10**.
9. **Polimento:** balanceamento, menus, áudio, testes com 4 jogadores, correções. **Lançamento v1.0.**

## 10. Decisões em aberto

- Qual PC mais fraco será a referência para testes de desempenho?
- Nome do mundo e dos reinos?
- Número máximo de jogadores: 2 ou 4?
- Formato das traduções: CSV ou gettext `.po`?
- Quanto tempo por semana será dedicado (para estimar prazos)?
