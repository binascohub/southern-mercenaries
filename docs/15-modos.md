# Modos de jogo — Novo Jogo+ e dificuldades

> Versão 1 · 2026-10-30 · Complementa `11-saves.md`, `13-balanceamento.md`, `03-inimigos.md` e `06-mundo-e-historia.md`
> **Todo o conteúdo é proposta** para o autor revisar. Itens **em aberto** não devem ser decididos sem consultar o autor.
> Escopo: **v1.0 tem só o modo Normal**. Os modos abaixo entram depois do jogo base estar completo (fase final de `01-escopo.md`).

## 1. Resumo

| Modo | Quando libera | O que muda |
|---|---|---|
| **Normal** | Desde o início | A campanha como desenhada (`13-balanceamento.md`) |
| **Novo Jogo+** | Ao vencer Lúcifer (fim do mapa 10) | Recomeça a campanha com o personagem e o equipamento; monstros mais fortes |
| **Pesadelo** (dificuldade) | Junto com o Novo Jogo+ | Escala de monstros maior, mais loot |
| **Expedição** (rejogar áreas) | Ao vencer Lúcifer | Voltar a qualquer área já completada para farmar |

## 2. Novo Jogo+

- A **campanha** é nova (save de campanha separado, começa em Tortuga, mapa 1); o **personagem** vem junto: nível, atributos, habilidades e equipamento (inclusive refino).
- Cada Novo Jogo+ é um **ciclo**: ciclo 1 é a campanha normal, ciclo 2 é o primeiro Novo Jogo+, e assim por diante (proposta: até o ciclo 5).
- **Escala por ciclo (proposta):** vida dos monstros +50% e dano +25% por ciclo, somados à escala do co-op (`07-rede.md`). O nível dos monstros sobe em +4 por ciclo.
- **Nível máximo sobe** para 20 + 5 por ciclo (proposta: máximo 40). Pontos novos seguem as regras de `02-personagens.md`.
- **Loot melhor:** itens de raridade alta têm chance maior por ciclo e aparecem materiais nobres (prata e ouro) mais cedo.
- A história **não muda**; cada mapa ganha uma fala nova do Bobo e dos NPCs lembrando o que já aconteceu (opcional).
- Os **chefes** são os mesmos, com uma habilidade extra cada (proposta, a detalhar depois).
- Os **tutoriais** (`14-tutorial.md`) não repetem (`tutorial_seen` é do personagem).
- No co-op, cada jogador entra com seu personagem; o host escolhe o ciclo da partida e **o ciclo máximo permitido é o menor entre os personagens** que já o venceram (proposta), para ninguém ser lançado num ciclo que não liberou.

## 3. Dificuldades

Duas camadas separadas, para não misturar com o ciclo:

| Dificuldade | Vida dos monstros | Dano dos monstros | XP | Loot raro | Disponível |
|---|---|---|---|---|---|
| **História** | -30% | -30% | ×1,0 | ×1,0 | Sempre |
| **Normal** | base | base | ×1,0 | ×1,0 | Sempre |
| **Pesadelo** | +60% | +40% | ×1,3 | ×1,5 | Depois de vencer Lúcifer |

- A dificuldade é escolhida pelo **host** ao criar a campanha e **pode ser trocada em Tortuga**; os jogadores veem a escolha ao entrar.
- **História** serve para jogar mais pela história com amigos novatos ou crianças.
- A morte não tem penalidade extra em nenhuma dificuldade (a regra de `04-tortuga-e-missoes.md` vale).
- Os modificadores multiplicam a escala do co-op e do ciclo.

## 4. Expedição (rejogar áreas)

- Depois de vencer Lúcifer, o portal da cidade permite entrar em qualquer área **já completada** com os monstros **reaparecidos** (a exploração é refeita, `03-2-areas.md`).
- Os mini-chefes e chefes reaparecem **uma vez por dia real** (proposta) para evitar farm infinito.
- A recompensa segue a escala do ciclo e da dificuldade atuais.
- O mapa revelado volta ao estado "não explorado" nessa expedição, sem apagar o progresso da campanha.

## 5. Notas técnicas

- Salvar no save de campanha: `cycle` (inteiro), `difficulty` (`story`, `normal`, `nightmare`) e `max_cycle_unlocked` por personagem.
- Os modificadores ficam em arquivo de dados (`data/modes.json`), nunca no código.
- O servidor aplica os multiplicadores (autoritativo); o cliente só mostra.
- Aumentar a versão do formato de save (`save_version`) quando esses campos entrarem (`11-saves.md`).
- Textos de modos e dificuldades usam chaves de tradução (`tr()`).

## 6. Decisões em aberto

- O Novo Jogo+ traz o equipamento todo ou só uma parte (ex.: uma peça por mapa)?
- Teto de ciclos e do nível máximo (propostas: 5 ciclos, nível 40)?
- Chefes ganham habilidades extras ou só números maiores?
- Os valores da seção 3 e da seção 2 saem de testes de balanceamento (`13-balanceamento.md`).
