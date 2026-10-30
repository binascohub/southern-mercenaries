# Modos de jogo — Novo jogo, dificuldades e expedições

> Versão 1 · 2026-10-30 · Complementa `11-saves.md`, `13-balanceamento.md`, `03-inimigos.md` e `06-mundo-e-historia.md`
> **Todo o conteúdo é proposta** para o autor revisar. Itens **em aberto** não devem ser decididos sem consultar o autor.
> Escopo: **v1.0 tem só o modo Normal**. Os modos abaixo entram depois do jogo base estar completo (fase final de `01-escopo.md`).

## 1. Resumo

| Modo | Quando libera | O que muda |
|---|---|---|
| **Normal** | Desde o início | A campanha como desenhada (`13-balanceamento.md`) |
| **Novo jogo** | Sempre | Começa **do zero**: campanha nova e personagem novo (**decidido**) |
| **Pesadelo** (dificuldade) | Depois de vencer Lúcifer uma vez | Escala de monstros maior, mais loot |
| **Expedição** (rejogar áreas) | Ao vencer Lúcifer | Voltar a qualquer área já completada para farmar |

## 2. Novo jogo começa do zero (decidido)

- **Não há Novo Jogo+.** Todo novo jogo cria uma **campanha nova** e um **personagem novo** (nível 1, só roupa de baixo e arma de madeira, `02-personagens.md`), sem herdar nada.
- O personagem que venceu Lúcifer continua existindo: pode seguir na **Expedição** (seção 4) e na continuação da história.
- O que persiste entre jogos é só o que é do jogador, não do personagem: opções, `tutorial_seen` (o tutorial não repete, `14-tutorial.md`) e o desbloqueio do **Pesadelo** (seção 3).
- Isso mantém o balanceamento de uma só curva (`13-balanceamento.md`) e o nível máximo em 20.

## 3. Dificuldades

Escolha feita ao criar a campanha:

| Dificuldade | Vida dos monstros | Dano dos monstros | XP | Loot raro | Disponível |
|---|---|---|---|---|---|
| **História** | -30% | -30% | ×1,0 | ×1,0 | Sempre |
| **Normal** | base | base | ×1,0 | ×1,0 | Sempre |
| **Pesadelo** | +60% | +40% | ×1,3 | ×1,5 | Em campanhas novas, depois de vencer Lúcifer uma vez |

- A dificuldade é escolhida pelo **host** ao criar a campanha e **pode ser trocada em Tortuga**; os jogadores veem a escolha ao entrar.
- **História** serve para jogar mais pela história com amigos novatos ou crianças.
- A morte não tem penalidade extra em nenhuma dificuldade (a regra de `04-tortuga-e-missoes.md` vale).
- Os modificadores multiplicam a escala do co-op.

## 4. Expedição (rejogar áreas)

- Depois de vencer Lúcifer, o portal da cidade permite entrar em qualquer área **já completada** com os monstros **reaparecidos** (a exploração é refeita, `03-2-areas.md`).
- Os mini-chefes e chefes reaparecem **uma vez por dia real** (proposta) para evitar farm infinito.
- A recompensa segue a dificuldade da campanha.
- O mapa revelado volta ao estado "não explorado" nessa expedição, sem apagar o progresso da campanha.

## 5. Notas técnicas

- Salvar no save de campanha: `difficulty` (`story`, `normal`, `nightmare`); nas opções do jogador: `nightmare_unlocked`.
- Os modificadores ficam em arquivo de dados (`data/modes.json`), nunca no código.
- O servidor aplica os multiplicadores (autoritativo); o cliente só mostra.
- Aumentar a versão do formato de save (`save_version`) quando esses campos entrarem (`11-saves.md`).
- Textos de modos e dificuldades usam chaves de tradução (`tr()`).

## 6. Decisões em aberto

- Os valores da seção 3 saem de testes de balanceamento (`13-balanceamento.md`).
- O Pesadelo libera ao vencer Lúcifer em qualquer personagem (proposta) ou só no personagem que venceu?
