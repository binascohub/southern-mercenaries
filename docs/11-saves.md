# Saves — salvar e continuar a campanha

> Versão 1 · 2026-10-30 · Como o jogo salva personagens e campanhas, no solo e no co-op.
> Pontos marcados como **proposta** ou **em aberto** devem ser confirmados com o autor.

## 1. Requisito

- O jogador pode **salvar a campanha e continuar depois**, do ponto onde parou, solo ou em grupo.
- Nada de progresso perdido por fechar o jogo, queda de rede ou falta de energia (salvamento automático frequente e seguro).

## 2. Dois tipos de save

| Save | O que guarda | Onde fica | Quem é o dono |
|---|---|---|---|
| **Personagem** | Classe, sexo, nome, elemento, nível, XP, atributos, habilidades, inventário, equipamento, ouro, poções, objeto pessoal | PC de cada jogador | O jogador |
| **Campanha** | Ato e mapa atual, mapas concluídos, chefes derrotados, tesouros abertos, relíquias, missões (ativas e concluídas), histórias já contadas, bestiário/pistas, Capital liberada, estoque e preços do Mercado Pirata e das lojas, último checkpoint, lista de participantes | PC do **host** | Quem hospedou |

- Um personagem pode jogar **em várias campanhas** (estilo Diablo 2 "open"): o nível e os itens vão com ele; o progresso da história fica na campanha.
- Proposta: o bestiário (pistas descobertas) também é guardado no personagem, para o jogador não perder o que já sabe.

## 3. Espaços de save

- **Personagens:** até **12** por PC (proposta).
- **Campanhas:** até **6** espaços por PC (proposta), cada um com nome, data, tempo de jogo, ato/mapa atual, heróis que participaram e uma miniatura.
- Menu principal: **Continuar** (última campanha), **Nova campanha**, **Carregar campanha**, **Entrar em partida (LAN)**.

## 4. Quando salva

### Automático (autosave)
- Ao **entrar e sair de uma cidade** (Tortuga ou Capital).
- Ao passar por um **checkpoint** no mapa (2 a 4 por mapa, proposta: antes do chefe sempre tem um).
- Ao **derrotar um chefe** e ao **abrir o tesouro**.
- Ao **aceitar ou concluir uma missão**.
- Ao comprar/vender (só o personagem).
- Ao sair pelo menu (**Salvar e sair**).

### Manual
- Na **cidade**: salvar a qualquer momento pelo menu.
- No **mapa**: não há save livre; o menu oferece **Salvar e sair**, que guarda o progresso do personagem (XP, itens, ouro) e o último checkpoint.

### Ao continuar
- Na cidade: volta exatamente ao mesmo lugar.
- No mapa: volta no **último checkpoint**. Monstros já mortos **ficam mortos** (decidido): o estado de cada grupo de encontro (dormindo, desperto, morto) e dos baús abertos é salvo na campanha. Itens e XP ganhos depois do checkpoint **não se perdem** (o personagem é salvo continuamente).
- **Checkpoints alcançados:** lista de todos os checkpoints já atingidos na campanha (para o portal do Macumbeiro, `04-tortuga-e-missoes.md`, seção 5.1).
- **Mapa explorado:** a parte já revelada de cada área é salva por jogador (máscara compacta) na campanha, para o mapa continuar revelado ao voltar (`09-interface.md`). Grupos de encontro mortos não voltam.

## 5. Co-op

- A campanha é **do host**. Para continuar, o host abre **Carregar campanha** e hospeda; os amigos entram com os seus personagens.
- O host pode continuar a campanha com **qualquer número de jogadores** (até sozinho); a dificuldade se ajusta.
- Um jogador que entra pela primeira vez numa campanha em andamento começa onde o grupo está (proposta: recebe as pistas do bestiário já descobertas pelo grupo).
- Os **personagens dos clientes são salvos no PC de cada cliente** (o servidor envia as mudanças: XP, loot, ouro, e o cliente grava). Proposta anti-trapaça leve: o servidor guarda um resumo (hash) do personagem para detectar arquivo editado — opcional, já que é jogo entre amigos.
- Se o host cair: os clientes voltam ao menu com o personagem já salvo; o host recarrega a campanha do último autosave.
- Se um cliente cair: o personagem dele já está salvo; ele pode reentrar na mesma partida.

## 6. Implementação (Godot)

- Pasta: `user://saves/` (Windows: `%APPDATA%\Southern Mercenaries\saves`, Linux: `~/.local/share/southern-mercenaries/saves`).
  - `characters/<id>.json`
  - `campaigns/<id>/campaign.json` + `thumb.png`
- **Formato:** JSON legível (fácil de depurar e de migrar), com campo `"save_version"`. Os dados guardam **IDs** (itens, missões, mapas), nunca texto traduzido — assim o save funciona em qualquer idioma.
- **Escrita segura:** gravar em arquivo temporário e depois renomear (não corrompe se o PC desligar no meio). Manter os **3 últimos backups** de cada save (`.bak1`, `.bak2`, `.bak3`) e oferecer restaurar se o principal estiver corrompido.
- **Migração:** ao atualizar o jogo, saves de versões antigas são convertidos (funções `migrate_vN_to_vN+1`). Nunca quebrar save entre versões da mesma série (`1.x`).
- Salvamento em segundo plano (thread) para não travar o jogo.
- Ícone discreto de "salvando…" no canto da tela.

## 7. Decisões em aberto

- Número de espaços de personagens e de campanhas (12 e 6?).
- Monstros depois do checkpoint renascem ao continuar?
- Bestiário guardado no personagem, na campanha ou nos dois?
- Modo "hardcore" (personagem morto é perdido) — fora da v1.0?
- Exportar/importar save (copiar personagem para o PC de um amigo)?
