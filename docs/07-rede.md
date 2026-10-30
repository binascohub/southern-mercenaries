# Rede e Multiplayer

> Versão 1 · 2026-10-30 · Detalhes técnicos de sincronização. Complementa `01-escopo.md` (seção 4), `11-saves.md` (seção 5), `05-itens-e-loot.md`, `05-1-refino.md`, `03-inimigos.md` e `04-tortuga-e-missoes.md`
> Números (taxas, portas, limites) são propostas para ajustar em teste. Itens **em aberto** não devem ser decididos sem consultar o autor.

## 1. Modelo

- **Host-cliente com servidor autoritativo.** Um jogador hospeda; o servidor roda dentro do jogo dele e **também é um jogador**. Os demais são clientes.
- **Solo = o mesmo servidor, sem rede.** Um só código para solo e multiplayer: o jogo sobe o servidor local e o jogador é o único cliente (peer `1`). Nada de caminho de código separado para solo.
- **Só LAN** (1 a 4 jogadores). Internet, servidor dedicado e matchmaking estão fora do escopo da v1.0.
- **Windows e Linux juntos** na mesma partida. O servidor não depende de determinismo entre máquinas (ele decide tudo e envia o resultado), então não há problema de ponto flutuante entre sistemas.
- **Tecnologia:** MultiplayerAPI do Godot 4 sobre `ENetMultiplayerPeer` (UDP), com `MultiplayerSpawner`, `MultiplayerSynchronizer` e RPCs.

## 2. Quem decide o quê

| Assunto | Autoridade | Observação |
|---|---|---|
| Movimento do herói | **Servidor** | O cliente envia **intenção** (direção, mira, botões); o servidor simula. Ver seção 5 sobre a sensação de resposta |
| Dano, vida, mortes, estados, combos de elementos | **Servidor** | Cliente só mostra |
| IA e vida dos monstros, animais amigos do Invocador | **Servidor** | `03-inimigos.md`, `02-5-invocador.md` |
| Despertar de grupos de encontro, emboscadas, armadilhas | **Servidor** | Cada grupo desperta uma vez (`03-inimigos.md`, "Encontros por exploração") |
| Loot, ouro, baús, drops | **Servidor** | Sorteio no servidor; entrega **individual** (seção 7) |
| Refino, troca, compra e venda | **Servidor** | Sorteios e validações sempre no servidor (`05-1-refino.md`) |
| Experiência, nível, pontos de atributo e de habilidade | **Servidor** | O cliente pede; o servidor valida e confirma |
| Missões, bestiário, estado do mundo | **Servidor** | Salvos no PC do host (`11-saves.md`) |
| Câmera, interface, efeitos visuais, sons, aura | **Cliente** | Só local; a rede envia IDs e valores, nunca texto traduzido |
| Mapa revelado | **Servidor** (do grupo) | Um só mapa explorado, compartilhado por todos; vai no save da campanha (`09-interface.md`) |

Regra geral: **o cliente nunca decide resultado de jogo**; só pede e mostra.

## 3. Descoberta e conexão

### Descoberta automática (broadcast UDP)
- O host, ao abrir a partida, **anuncia** na LAN a cada ~1 s (porta de descoberta, proposta `24568`) um pacote curto: versão do jogo, nome da partida, nome do host, número de jogadores/máximo, IP e porta, se está cheia, ID da campanha (hash curto).
- Quem escolhe **Entrar na LAN** escuta essa porta e monta a **lista de partidas** (`09-interface.md`, lobby). A lista some partidas sem anúncio há mais de ~5 s.
- **Conexão manual por IP:porta** como alternativa (para redes que bloqueiam broadcast).
- **Porta do jogo:** proposta `24567` (UDP), configurável em Opções → Rede. Aviso no lobby se o firewall bloquear (e instrução curta de liberar a porta no Windows e no Linux).

### Handshake de entrada
1. O cliente abre a conexão ENet.
2. Envia: **versão do jogo**, **versão do formato de save** (`save_version`), **hash do conteúdo** (dados do jogo), idioma, nome do jogador, ID do personagem e o **personagem** (dados do save, seção 8).
3. O servidor **recusa** se a versão do jogo ou o hash de conteúdo forem diferentes (mensagem clara com as duas versões), se a partida estiver cheia, ou se o personagem for inválido (formato, nível acima do permitido, itens inexistentes).
4. Se aceitar: envia o **estado do mundo** (seção 9) e o cliente carrega a cena atual.
5. O cliente aparece **ao lado do host** (`01-escopo.md`).

### Lobby e partida
- Antes de iniciar: sala com os jogadores, classes e elementos; o host escolhe a campanha (nova ou carregada) e inicia.
- **Entrar no meio da partida é permitido** (`01-escopo.md`). Se os jogadores estiverem numa luta de chefe, o novato espera na **borda da arena** até a luta acabar (proposta).

## 4. Salas, áreas e jogadores

- **Todos os jogadores estão sempre na mesma cena.** Cidade, área de treinamento ou uma área de mapa; não existe jogador em outra área ao mesmo tempo. Isso simplifica o servidor e a sincronização.
- Os jogadores podem se **separar dentro da mesma área** (cada câmera segue o seu herói).
- **Passagem entre áreas e viagem por portal:** só acontece quando o host confirma e os outros aceitam, ou quando **todos estão perto da saída** (contagem de 10 s do host, `03-2-areas.md`). Jogador longe do portal é puxado ao confirmar (`04-tortuga-e-missoes.md`, seção 5).
- **Troca de cena:** o servidor manda "carregar a cena X" (ID da área), cada cliente carrega localmente e avisa "pronto"; o servidor só libera o jogo quando todos estiverem prontos (com limite de tempo; quem demorar demais fica numa tela de carregamento e é solto ao terminar).
- **Cada área é uma cena separada** (`03-2-areas.md`), então o servidor só mantém **uma área ativa** por vez (poucas entidades, menos tráfego).

## 5. Sincronização em jogo

### Taxas (propostas)
| Fluxo | Taxa |
|---|---|
| Física/jogo no servidor | 60 Hz |
| Entrada do cliente → servidor | 30 Hz (e imediata para botões/habilidades) |
| Estado do mundo servidor → clientes | **20 Hz** (50 ms), só o que mudou |
| Eventos (dano, morte, loot, mensagens) | Na hora, por RPC confiável |

### O que viaja
- **Heróis:** posição, direção, animação/estado, vida, recurso, elemento atual, aura (nível), equipamento (**IDs** de cada slot, não malhas; `02-personagens.md`), montado ou a pé (Cavaleiro).
- **Monstros:** posição, animação, vida (percentual), estados visíveis (queimando, congelado…), alvo. Só os **acordados e perto de algum jogador**; monstros dormindo não são enviados (aparecem quando acordam ou entram no raio de interesse).
- **Projéteis e efeitos de área:** o servidor envia **o evento** (origem, direção, habilidade, rank, momento); o cliente reproduz o efeito visual. O dano é calculado no servidor.
- **Animais amigos do Invocador:** como monstros do time do jogador, simulados no servidor.
- **Interesse:** como só existe uma área ativa e a câmera é próxima, basta enviar o que está num raio de ~30 m de cada jogador (proposta).

### Sensação de resposta
- LAN tem latência muito baixa (poucos ms), então a primeira versão usa **servidor autoritativo com o cliente enviando entrada e mostrando o resultado**, com **interpolação** dos outros jogadores e dos monstros (mostrar ~100 ms no passado).
- **Predição do próprio herói** (mover imediatamente e corrigir se o servidor discordar) fica como melhoria: **só se o teste mostrar atraso perceptível** (proposta). O Cavaleiro montado, que tem inércia, é o caso mais sensível.
- **Habilidades:** o cliente toca animação e som na hora (confirmação visual imediata) e o servidor confirma o dano. Se o servidor recusar (sem recurso, em recarga), o efeito é cancelado.
- **Esquiva, teleporte do Ninja e Teleporte do Mago:** o servidor valida distância e obstáculos.

### Escala por jogador
- **A única coisa que muda com o número de jogadores é a força dos monstros** (vida e dano), para equilibrar (`01-escopo.md`). O loot **não** escala. O servidor recalcula quando alguém entra ou sai (monstros já acordados mantêm o valor; grupos ainda dormindo usam o novo).
- Cooldowns, recursos e custos são os mesmos para qualquer número de jogadores.

## 6. Interface e rede

- **Pausa:** no **solo** o jogo pausa (servidor local); no **co-op não pausa** — janelas abrem por cima e o herói fica vulnerável (`09-interface.md`).
- **Controle USB desconectado:** no solo pausa; no co-op só mostra um aviso (`08-controles.md`).
- **Diálogos de cidade** (taverna, Bobo): o texto é escolhido pelo ID de fala enviado pelo servidor; cada cliente mostra no seu idioma. O diálogo aparece para todos; qualquer um pode aceitar ou recusar a missão (`04-tortuga-e-missoes.md`, seção 4).
- **Idiomas diferentes** na mesma partida: a rede só envia **IDs** de itens, falas, missões, habilidades (`01-escopo.md`, seção 4).
- **Chat de texto:** o texto livre vai como digitado (limite de ~120 caracteres e taxa de ~1 mensagem por segundo). **Frases rápidas** vão como **ID** e são traduzidas no PC de quem recebe (`08-controles.md`, `chat_quick`).
- **Ping/aviso no mapa** (proposta): marcação com ID de tipo ("Aqui!", "Perigo!") e posição.

## 7. Loot, ouro e economia (individual)

- **Cada jogador vê só o seu loot** (`01-escopo.md`). O servidor sorteia **uma lista de drops por jogador** e envia cada uma só ao dono. O item aparece no chão **apenas para ele** (os outros não veem nem pegam).
- **Ouro individual:** pago a cada jogador; pagamento de missão dado inteiro a cada um (`04-tortuga-e-missoes.md`, seção 4).
- **Experiência dividida (decidido):** o XP de cada monstro é **dividido igualmente** entre os jogadores presentes na área (quem está desconectado ou caído por tempo longo não conta). Como a vida dos monstros sobe com o número de jogadores, o XP total do monstro sobe junto, para o ritmo de nível ficar parecido solo ou em grupo (proposta de ajuste fino em teste).
- **Lojas, Mercado Pirata/Real, ferreiro, Macumbeiro, altar:** o cliente pede a transação; o servidor valida (ouro, espaço na bolsa, estoque do jogador) e responde. O estoque do Mercado é **por jogador** (`04-tortuga-e-missoes.md`).
- **Troca entre jogadores:** janela confirmada pelos dois lados; o servidor valida e troca os itens de forma **atômica** (ou os dois recebem, ou ninguém) (`05-itens-e-loot.md`, seção 8).
- **Refino:** o sorteio é no servidor, e o resultado é gravado no item **antes** de responder ao cliente (para não dar para fechar o jogo e tentar de novo) (`05-1-refino.md`).
- **Portal do Macumbeiro:** o servidor cobra o preço de cada jogador; se alguém não tiver ouro, a viagem não acontece e o aviso mostra quem falta (`04-tortuga-e-missoes.md`, seção 5.1).

## 8. Saves e a rede

- **Personagem:** o arquivo fica no **PC do dono** (`11-saves.md`). Ao entrar, o cliente envia o personagem ao servidor; **durante a partida a cópia do servidor é a verdade** (XP, loot, ouro, refino, compras). O servidor envia as **mudanças** e o cliente grava no seu disco (escrita segura com backups).
- **Campanha:** salva no PC do host (missões, bestiário, checkpoints alcançados, estado de grupos de encontro e baús, mapa explorado, estoque e preços dos mercados).
- **Autosave:** nos checkpoints, ao voltar à cidade, depois do chefe e em missões; o servidor manda o comando "salvar agora" e cada cliente grava o seu personagem.
- **Anti-trapaça leve (opcional):** o servidor guarda um **hash** do personagem e compara na entrada, para detectar arquivo editado. Como é jogo entre amigos, a política é **só aviso**, nunca bloqueio (**decidido**): o grupo vê uma mensagem e o jogador entra normalmente.

## 9. Entrar no meio, sair e cair

### Entrar no meio da partida
O servidor envia ao novo jogador o **estado do mundo** da cena atual:
- IDs e posições dos grupos de encontro (dormindo, despertos, mortos) e de baús abertos;
- estado das missões e do bestiário (pistas já descobertas pelo grupo);
- checkpoints alcançados;
- jogadores presentes (classe, elemento, equipamento, nível);
- o **mapa revelado do grupo** (único e compartilhado; o novato vê tudo o que o grupo já explorou).

### Sair
- Saída normal: o personagem já está salvo; o herói some do mundo e a escala de dificuldade se ajusta.
- **Cliente caiu (decidido):** o herói **fica parado por 30 s** no lugar (invulnerável durante esse tempo, para não ser morto sem poder reagir); o jogador pode **reentrar na mesma partida** nesse prazo e assume o mesmo herói. Depois dos 30 s o herói sai do mundo e, para voltar, o jogador reentra como novo jogador ao lado do host (`11-saves.md`, seção 5).
- **Host caiu:** a partida acaba; os clientes voltam ao menu com o personagem salvo no último ponto; o host recarrega a campanha do último autosave.
- **Todos caídos:** voltam ao último checkpoint, como em `01-escopo.md`.

### Reanimar
Aliado caído é reanimado segurando o botão por 3 s perto dele. O servidor controla o tempo e quem está reanimando; se o reanimador for atingido, a tentativa é interrompida (`02-personagens.md`).

## 10. Largura de banda e desempenho

- **Meta:** menos de ~50 KB/s por cliente em combate com 4 jogadores e ~40 entidades ativas (proposta; deve caber folgadamente em qualquer LAN).
- Reduções: enviar só o que mudou, quantizar posições e ângulos (16 bits), IDs curtos, agrupar eventos do mesmo tick, não enviar monstros dormindo.
- **Limite de entidades ativas** (`03-inimigos.md`): ~40 monstros e animais amigos juntos; o servidor recusa invocar acima do limite.
- O servidor (host) também é um jogador; manter o custo de IA baixo é requisito (monstros longe dormem, IA em intervalos, pooling).
- Em Opções → Rede: nome, porta e **mostrar latência** (`09-interface.md`).

## 11. Segurança básica

- **Versão e conteúdo:** o servidor recusa clientes com versão ou dados diferentes.
- **Validação:** todo RPC do cliente é validado no servidor (alcance, recarga, recurso, espaço na bolsa, estoque).
- O servidor **ignora** comandos que um cliente não pode enviar (ex.: pedir loot de outro jogador).
- Limite de taxa para RPCs (chat, pedidos de transação) para evitar travar o host.
- **Sem criptografia** na v1.0 (LAN entre amigos). Registrar como decisão consciente.
- Nunca confiar em texto do cliente: tamanho máximo, sem formatação especial.

## 12. Implementação (Godot 4)

- Script `NetworkManager` (autoload): cria o host (`ENetMultiplayerPeer.create_server`), conecta clientes, trata `peer_connected`/`peer_disconnected` e a descoberta por broadcast (`PacketPeerUDP`).
- **Autoridade:** o servidor é o peer `1`; heróis têm `set_multiplayer_authority` conforme o desenho da seção 2 (movimento por intenção).
- `MultiplayerSpawner` para heróis, monstros, projéteis e animais amigos; `MultiplayerSynchronizer` só para o que precisa de estado contínuo (posição, vida), com `replication_interval` ajustado.
- **RPCs:** `@rpc("any_peer", "call_remote", "reliable")` apenas para pedidos do cliente ao servidor (validados); `@rpc("authority", "call_remote", "unreliable")` para estado frequente; `reliable` para eventos únicos.
- Eventos de combate e loot usam **IDs** (definidos nos arquivos de dados) e nunca texto traduzido.
- Estado de cena atual (grupos de encontro, baús, checkpoints) como dados serializáveis, os mesmos usados no save (`11-saves.md`) — assim "entrar no meio" e "carregar campanha" usam o mesmo código.
- Testar sempre **Windows ↔ Linux**, solo e com 4 jogadores, e simular perda de pacotes e latência (ferramentas de rede do sistema) antes de cada versão pública.

## 13. Decisões em aberto

- Predição do próprio herói: necessária? (decidir em teste)
- Portas padrão (`24567` jogo, `24568` descoberta): manter?
- Entrar no meio durante luta de chefe: esperar na borda da arena (proposta)?
- Criptografia: continuar sem na v1.0?
