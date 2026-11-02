# Southern Mercenaries — Documentação

Documentação de design do jogo **Southern Mercenaries**, RPG de ação co-op em LAN, escrita para servir de base à implementação (inclusive por um assistente de IA como o Claude). Jogo open source (GPL-3.0-or-later) para Windows e Linux, em inglês, espanhol e português.

## Ordem de leitura

| Arquivo | Conteúdo |
|---|---|
| `01-escopo.md` | Visão geral, câmera, mecânicas, multiplayer LAN, tecnologia, idiomas, conteúdo da v1.0, fases |
| `02-personagens.md` | Visão geral das 5 classes, vestimenta/equipamento visual, atributos, regras gerais |
| `02-0-elementos.md` | Elementos, ciclo de fraquezas, Poção Elemental, estados, combos e composição das habilidades |
| `02-1-mago.md` | Mago detalhado |
| `02-2-arqueiro.md` | Arqueiro detalhado |
| `02-3-cavaleiro.md` | Cavaleiro detalhado (Dorian e Dália) |
| `02-4-ninja.md` | Ninja detalhado (Ren e Rin) |
| `02-5-invocador.md` | Invocador detalhado |
| `03-inimigos.md` | Os 10 mapas, famílias de monstros (mecânica e elemento), elites, mini-chefes, chefes e Lúcifer |
| `03-1-bestiario.md` | Lendas reais de cada criatura e as pistas de fraqueza contadas pelos NPCs e pelo Bobo |
| `03-2-areas.md` | Divisão dos 10 mapas em 41 áreas, níveis, checkpoints, mini-chefes |
| `04-tortuga-e-missoes.md` | Tortuga (primeira cidade-base), taverna, Mercado Pirata, NPCs e sistema de missões |
| `04-1-capital-real.md` | Capital Real (segunda cidade-base, cidade do Cavaleiro), comércio elevado, Bobo da Corte |
| `05-itens-e-loot.md` | Categorias, materiais (pano/madeira → ouro), raridades, tesouros, valiosos, mercados, inventário |
| `05-1-refino.md` | Refino com pergaminhos estilo Lineage 2 (+1 a +5, seguro até +3, falha e cristais) e a aura em volta do herói |
| `06-mundo-e-historia.md` | Premissa, a guerra, estrutura da campanha em atos, abertura, tesouros e motivos dos heróis |
| `07-rede.md` | Servidor autoritativo, descoberta na LAN, sincronização, loot individual, entrada e saída no meio da partida |
| `08-controles.md` | Teclado/mouse e controle USB, mapeamento padrão, remapeamento, opções |
| `09-interface.md` | **Identidade visual do jogo (regra para todo o visual)**, câmera próxima como Dark Alliance, HUD, menus, telas e opções |
| `14-tutorial.md` | Primeiros minutos, dicas contextuais, equipamento inicial e tutorial no Esgoto |
| `13-balanceamento.md` | Fórmulas e tabelas de dano, vida, armadura, XP, ouro, preços e metas de equilíbrio |
| `12-audio.md` | Trilha por mapa e chefe, efeitos, ambiente, sons de interface, vozes dos heróis e licenças de áudio |
| `10-distribuicao.md` | Licenças open source, repositório, builds Windows/Linux, instaladores, GitHub Actions, website |
| `15-modos.md` | Novo jogo do zero, dificuldades (História, Normal, Pesadelo) e expedições, depois da v1.0 |
| `11-saves.md` | Saves de personagem e de campanha, autosave, checkpoints, continuar no solo e no co-op |

## Regras para quem for implementar

- **Engine:** Godot 4 (versão estável fixada), renderizador Compatibility (OpenGL 3.3), **GDScript**. Desempenho em vídeo integrado é requisito, não otimização opcional.
- **Plataformas:** Windows e Linux com as mesmas funcionalidades; testar os dois e o co-op entre eles.
- **Rede:** servidor autoritativo; o modo solo usa o mesmo servidor rodando localmente. Sorteios (loot, refino) sempre no servidor.
- **Controles:** suporte completo a controle USB desde a primeira fase jogável; usar ações do Input Map, nunca teclas fixas (`08-controles.md`).
- **Idiomas:** en, es e pt_BR. **Nenhum texto fixo no código, nas cenas ou nos dados** — sempre chaves de tradução com `tr()`; a rede e os saves usam IDs, nunca texto traduzido (`01-escopo.md`, seção 6). Os textos desta documentação estão em português (fonte) e também em inglês (`en/`) e espanhol (`es/`); as traduções do jogo são feitas pelo Claude.
- **Equipamento visível:** tudo que é equipado aparece no personagem, peça por peça, com o material; o refino gera uma aura em volta do herói (`05-itens-e-loot.md`, `05-1-refino.md`).
- **Saves:** escrita segura com backups e número de versão desde o primeiro save (`11-saves.md`).
- **Áreas:** cada área de mapa é uma cena separada, com checkpoint na entrada (`03-2-areas.md`).
- **Open source:** só assets próprios (criados pelo Claude a partir das referências do autor, sem copiar nenhum jogo) ou com licença livre; registrar tudo em `CREDITS.md` (`10-distribuicao.md`).
- **Dados separados do código:** classes, elementos, habilidades, itens, materiais, pergaminhos, refino, monstros, bestiário, NPCs, lojas, áreas e modelos de missão ficam em arquivos de dados, usando os IDs definidos nos documentos (ex.: `knight`, `fire`, `fireball`, `headless_mule`, `tavern_keeper`, `court_jester`, `sewers_01_drains`, `steel`).
- **Fontes oficiais:** o arquivo detalhado de cada classe vale mais que o resumo em `02-personagens.md`; `02-0-elementos.md` vale para todas as classes e monstros; `03-1-bestiario.md` é a fonte das falas de história e pistas; `06-mundo-e-historia.md` define a ordem da campanha (10 mapas); `05-itens-e-loot.md` define os materiais.
- **Campanha 2 (regra de design):** a continuação deve **sempre** começar com os heróis **pobres de novo** (só roupa de baixo, arma de madeira, sem ouro, sem refino, nível 1). A Campanha 1 não transfere nada; a história justifica (`06-mundo-e-historia.md`, seção 9).
- **Idiomas da documentação:** português (esta pasta), inglês (`en/`) e espanhol (`es/`), com os mesmos nomes de arquivo; em caso de dúvida, o português é a fonte.
- **Implementar por fases**, na ordem de `01-escopo.md` seção 9. Cada fase deve ficar jogável antes da próxima.
- Itens marcados como **em aberto** ou **proposta** não devem ser decididos sem consultar o autor.

## Próximos documentos previstos

- Nenhum por enquanto.
