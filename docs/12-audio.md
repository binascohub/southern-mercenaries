# Áudio

> Versão 1 · 2026-10-30 · Trilha, efeitos, ambiente e vozes. Complementa `01-escopo.md` (seção 7, áudio), `09-interface.md` (sons de interface), `10-distribuicao.md` (licenças) e `03-inimigos.md` (monstros)
> Números e listas são propostas para revisar. Itens **em aberto** não devem ser decididos sem consultar o autor.

## 1. Princípios

- **Sem dublagem:** as falas são só texto (`01-escopo.md`). Assim a tradução não exige regravar áudio.
- **Só áudio próprio ou com licença livre** compatível com open source: **CC0, CC BY, CC BY-SA** (mesma regra dos assets, `01-escopo.md`, seção 5). Nada de bibliotecas pagas que proíbem redistribuição, e nada de trilhas de jogos ou filmes. Toda origem e licença vai em `CREDITS.md`.
- **Tom sombrio e medieval:** coerente com o visual do 0 A.D. e com o clima de Dark Alliance. Cordas graves, tambores, flautas, coral, madeira, ferro e couro.
- **Leitura de combate:** o som avisa o que a imagem pode esconder (câmera próxima): golpe forte de monstro, chefe mudando de fase, aliado caído, item raro no chão.
- **Leve:** o jogo roda em PC fraco. Arquivos comprimidos, poucos sons ao mesmo tempo, músicas em *streaming*.

## 2. Mixagem (barramentos do Godot)

| Barramento | Conteúdo | Padrão |
|---|---|---|
| `Master` | Tudo | 100% |
| `Music` | Trilha | 70% |
| `SFX` | Combate, habilidades, monstros, passos | 100% |
| `Ambience` | Som ambiente de cada área e cidade | 80% |
| `UI` | Interface (madeira, couro, metal, papel) | 90% |
| `Voice` | Gritos e sons curtos dos heróis | 90% |

- Cada barramento tem controle de volume em **Opções → Áudio** (`09-interface.md`, seção 8).
- **Ducking:** a música baixa um pouco nos golpes de chefe e nos diálogos; os efeitos importantes (aviso de ataque forte) passam por cima.
- **Compressor leve** no `Master` para os efeitos de muitos jogadores não estourarem.

## 3. Música

### Estrutura
- **Música por mapa** com **duas camadas**: *exploração* (calma e tensa) e *combate* (tambores e cordas fortes). O jogo troca de camada com um *crossfade* de ~2 s quando o primeiro grupo de monstros acorda, e volta à exploração ~6 s depois do fim da luta.
- **Música de chefe**, separada, com fases (a música ganha intensidade a cada fase da luta, `03-inimigos.md`).
- **Música das cidades:** Tortuga (taverna desafinada, canções de piratas, porto), Capital Real (corte, cordas e metais mais ricos).
- **Música de interface:** menu principal, criação de personagem, tela de carregamento.
- **Stingers** curtos: nível novo, missão concluída, item lendário, checkpoint, derrota, vitória sobre chefe, abertura do portal.

### Lista de faixas (proposta)

| Faixa | Onde | Clima |
|---|---|---|
| `menu_main` | Menu principal | Tema do jogo: grave, épico, melancólico |
| `town_tortuga` | Tortuga (rua e porto) | Taverna, rabeca, tambor, mar |
| `tavern` | Interior da Taverna | Música ao vivo desafinada; o Bardo toca de verdade |
| `town_capital` | Capital Real | Corte, cravo, cordas, falsa elegância |
| `training` | Áreas de treinamento | Percussão leve, ritmo marcial |
| `map_sewers` | Esgoto | Gotas, graves, tensão baixa |
| `map_ruins` | Ruínas do Reino do Arqueiro | Marcha fúnebre, uivos ao longe |
| `map_forest` | Floresta Escura | Cordas e flautas, vozes distantes |
| `map_horses` | Cavalos Míticos | Galope, cordas rápidas |
| `map_birds` | Aves | Vento, cordas agudas, asas |
| `map_desert` | Deserto | Instrumentos de sopro e percussão do deserto, ritmo lento |
| `map_waters` | Águas | Ondas, coral grave, sinos de navio |
| `map_swamp` | Pântano | Sons lamacentos, flauta baixa, tensão |
| `map_serpents` | Serpentes | Percussão tribal, sussurros |
| `map_hell` | Inferno | Coral demoníaco, metal, graves |
| `boss_*` | Um tema por chefe, ou por família (proposta) | Fases intensificando |
| `boss_lucifer` | Lúcifer | Tema final, três fases |
| `stinger_*` | Eventos | 3 a 8 s |

- Total estimado: ~20 faixas longas (2 a 4 min, em loop) + temas de chefe + stingers.
- **Esgoto** e **Ruínas** são as primeiras a existir (v0.1, `01-escopo.md`, seção 9); o resto vem junto com cada mapa.

## 4. Efeitos sonoros

### Categorias
| Categoria | Exemplos |
|---|---|
| **Armas e golpes** | Lança, adagas, cajado, arco e flecha, livro; acerto em carne, armadura, madeira; defesa, aparar do Ninja, escudo do Cavaleiro |
| **Material** | O som de impacto e dos passos muda com o material equipado (pano, ferro, aço, cobre, prata, ouro; `05-itens-e-loot.md`) |
| **Habilidades por elemento** | Conjunto de sons por elemento (Água, Fogo, Ar, Terra), reaproveitado por todas as classes (`02-0-elementos.md`); estados (queimando, congelado, eletrizado, atordoado) e combos têm som próprio |
| **Classe** | Galope e relincho do Cavaleiro; teleporte do Ninja e do Mago; cântico do Invocador e sons dos animais amigos; corda do arco |
| **Monstros** | Rugidos, passos, ataques e morte por família (esqueleto compartilhado também compartilha os sons: roedores, canídeos, aves, felinos…); aviso sonoro antes de golpe forte |
| **Chefes** | Vozes e rugidos exclusivos, mudança de fase, golpes grandes (Esfinge fazendo o enigma, Kraken, Lúcifer) |
| **Itens e loot** | Cair no chão por raridade (comum a lendário), abrir baú, pegar ouro, equipar por material, refino (sucesso sobe, falha racha e explode em cristais; `05-1-refino.md`) |
| **Mundo** | Portais (no chão do Macumbeiro, de pedra da cidade), checkpoint, passagem de área, armadilhas, alavancas, portas |
| **Cidade** | Lojas, forja do ferreiro, pagar ouro, taverna, brigas, gaivotas, sinos |

### Regras
- **Prioridade:** golpe forte de monstro e aviso de perigo > habilidade do jogador > passos e ambiente.
- **Limite de vozes simultâneas** (proposta: 32 no total, 8 por categoria) e reaproveitamento de *players* (pool) para ficar leve.
- **Posicional:** efeitos tocam em 3D a partir da posição na cena (`AudioStreamPlayer3D`) com atenuação curta, já que a câmera é próxima; música, interface e voz do herói local são 2D.
- **Variações:** 3 a 5 variações de cada golpe e passo, com leve mudança aleatória de tom, para não ficar repetitivo.

## 5. Ambiente

Cada área e cidade tem uma camada contínua de som ambiente (`Ambience`), em loop, separada da música:
- Esgoto: água, gotas, ratos, eco.
- Ruínas: vento, corvos, madeira rangendo, uivos.
- Floresta: folhas, galhos, aves noturnas, silêncios estranhos.
- Cavalos: vento aberto, relinchos distantes.
- Aves: vento forte, asas, gritos.
- Deserto: vento e areia.
- Águas: ondas, madeira de navio, gaivotas, ranger de casco.
- Pântano: sapos, bolhas, insetos.
- Serpentes: selva, chuva, chiado.
- Inferno: fogo, gritos distantes, rachaduras de rocha.
- Tortuga: multidão, gaivotas, briga em taverna, ondas, sinos do porto.
- Capital Real: passos em pedra, sinos de catedral, trompetes, murmúrio da corte.

## 6. Sons de interface

Madeira, couro, metal e papel (`09-interface.md`, seção 7): clicar, passar o cursor, abrir pergaminho, selo de cera nas confirmações, arrastar item, vender (moedas), erro (uma batida seca), subir de nível. **Sem bipes sintéticos.**

## 7. Vozes dos heróis

- **Sem falas dubladas.** Cada herói tem apenas sons curtos **sem palavras**: esforço de golpe, dor, queda, morte, reanimação, comemoração e um grito de habilidade final por elemento.
- **Duas vozes por classe** (masculina e feminina), que acompanham o sexo escolhido (`02-personagens.md`).
- Falas de exemplo dos arquivos das classes aparecem **só como texto** (balão sobre o herói ou legenda), nos três idiomas.
- NPCs (taberneira, Bobo da Corte, Macumbeiro, capitães piratas…): sons curtos de reação ("hm", risada, pigarro) e **música/ambiente** como caracterização; também sem diálogo falado.

## 8. Implementação (Godot 4)

- **Formato:** `.ogg` (Vorbis) para música e ambiente (*streaming*); `.ogg` ou `.wav` curto para efeitos (carregados na memória). Música em loop com marcador de loop no arquivo.
- **Autoload `AudioManager`:** controla camadas de música (exploração/combate), crossfade, ducking, stingers e o *pool* de players de efeitos.
- **Dados:** faixas, camadas e sons de cada mapa/monstro/habilidade em arquivos de dados, referenciados por ID (ex.: `music/map_sewers.json`, `sfx/elements.json`), nunca no código (`00-README.md`).
- **Rede:** o servidor envia **eventos** (golpe, habilidade, morte) e cada cliente toca o som localmente; nenhum áudio viaja pela rede (`07-rede.md`). Música é decidida pelo estado local (se há monstros acordados perto).
- **Desempenho:** limite de vozes, *pooling*, taxa de amostragem de 44,1 kHz (22 kHz para sons curtos pouco importantes), sem reverberação pesada por padrão (reverberação leve só nas áreas de eco, como esgoto e cavernas).
- **Tamanho:** meta de ~150 MB de áudio no total na v1.0 (proposta), para o instalador não pesar demais (`10-distribuicao.md`).

## 8.1 RPG Sound Pack (implementado)

- Kit CC0 de artisticdude convertido por `tools/assets/build_rpg_sounds.py` para OGG mono em `assets/audio/sfx/`. Sufixo `_1.._N` = variantes sorteadas por `Sfx.play`; os `.wav` sintetizados continuam como reserva.
- Golpes (`swing`, `swing_heavy`), `coin`, `drink`, `pickup`, `equip`, `block`, `door` (ao trocar de área), `wood` (pote quebrando) e `ui_click` (todo botão, via `node_added`).
- Vozes de monstros `m_<família>_<n>`: slime, beetle, shade, ogre, giant, beast, wolfman. Família pela aparência (`VOICE_BY_LOOK` em `enemy.gd`) ou pelo campo `"sound"` do monstro; ataque no início do golpe, dano (45% das vezes) e morte. Tom varia com o tamanho.

## 9. Licenças e fontes

- Aceitos: **CC0**, **CC BY** e **CC BY-SA 4.0** (a arte e o áudio próprios do projeto saem em **CC BY-SA 4.0**, `LICENSE-ASSETS`). Conferir a licença de **cada arquivo**, não só do site.
- Fontes possíveis (verificar a licença de cada faixa e efeito antes de usar): OpenGameArt, Freesound (só CC0 e CC BY), Kenney (áudio CC0), Incompetech (CC BY), Musopen e similares de domínio público.
- **Não usar:** áudio sob licença que proíbe redistribuição (comum em bibliotecas pagas), faixas "grátis para uso" sem licença clara, e IA generativa de áudio sem origem de licença clara.
- **Registro:** nome do arquivo, autor, link, licença e se foi alterado, tudo em `CREDITS.md`. Atribuição (CC BY) mostrada também na tela de créditos do jogo.
- **Composição própria:** o autor ou colaboradores podem compor faixas originais, que entram sob CC BY-SA 4.0.

## 10. Decisões em aberto

- Um tema de chefe para cada um dos 10 chefes ou um por família (menos arquivos)?
- Orçamento de áudio no instalador: ~150 MB está bom?
- Origem da trilha: compor, usar bibliotecas livres ou misturar?
- Idioma dos "gritos" de habilidade final: só sons curtos (proposta) ou frases curtas dubladas no futuro?
- Modo de música dinâmica (camadas) já na v0.1 ou só uma música por mapa no começo?
