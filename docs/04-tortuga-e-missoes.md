# Tortuga e Missões

> Versão 14 · 2026-10-30 · Complementa `01-escopo.md` (cidade-base), `05-1-refino.md` (refino), `02-0-elementos.md` (Poção Elemental), `03-inimigos.md` e `03-1-bestiario.md` (monstros e lendas), `05-itens-e-loot.md` (mercados e tesouros) e `06-mundo-e-historia.md` (premissa)
> Nomes e números são propostas para revisar.

## 1. Tortuga — a cidade-base

### Origem
**Tortuga nasceu do caos do pós-guerra.** Quando a guerra acabou, sobraram ruínas, fome e gente sem lugar no mundo. Num porto abandonado, longe da lei de qualquer reino, se juntaram **desertores, renegados, ladrões, assassinos, prostitutas, piratas** e todo tipo de gente que não tinha mais para onde ir. Ergueram barracos sobre os destroços, depois tavernas, depois um mercado.

Nessa época, os fundadores trouxeram consigo **parte das riquezas do reino derrotado** (o reino do Arqueiro), roubadas durante a queda para salvá-las do saque dos vencedores, e as esconderam **nos túneis embaixo da cidade**. Anos depois, os moradores envenenaram e queimaram os ratos do esgoto — e a **mãe deles**, uma ratazana enorme, fez um **pacto com um demônio** para se vingar. Os animais dominaram os túneis, os fundadores perderam o acesso ao tesouro, e ele virou só mais uma história de bêbado.

### Sem rei, sem regras
**Tortuga não tem rei, nem lei, nem governo.** Ninguém manda; quem tem ouro ou lâmina faz as próprias regras. Para quem **não quer ter um rei** e **não quer seguir regras**, é **o lugar perfeito** — e é esse o espírito da cidade: liberdade total, com todos os perigos que vêm junto.

### Hoje
Tortuga é uma **cidade portuária suja, barulhenta e perigosa**, de ruas estreitas, lampiões, neblina e gente de passagem. Vive do **comércio ilegal**: mercado negro, **piratas** que desembarcam com o que roubaram pelo mundo, contrabando, **tavernas**, **prostíbulos**, casas de apostas e negócios que ninguém pergunta de onde vêm. Isso **atrai todo tipo de mal elemento** — e é exatamente por isso que os **mercenários** (os heróis) se sentem em casa: ali ninguém pergunta quem você foi.

- A superfície de Tortuga **não tem monstros** — mas não é um lugar seguro: brigas, golpes e ladrões fazem parte da paisagem (só como ambientação; a cidade não tem combate).
- **Embaixo** da cidade fica o **Esgoto**, o primeiro mapa do jogo (`03-inimigos.md`).
- Muitos heróis chegaram a Tortuga fugindo de alguma coisa: o Ninja desertou do clã, Dorian se afundou na bebida, Dália fugiu do castelo, o Arqueiro ficou sem vila por causa da guerra.

### Clima e ambientação
- Paleta escura, lama nas ruas, madeira podre, cordas, redes e barcos velhos no porto; navios piratas ancorados com bandeiras negras.
- NPCs de ambientação: bêbados nas portas, marinheiros, piratas, estivadores, contrabandistas, apostadores, guardas de aluguel, mendigos, gatos e ratos.
- Sons: briga em taverna, sinos do porto, gaivotas, ondas batendo no cais, canções de piratas, música desafinada.
- Os prostíbulos e casas de apostas aparecem **só como ambientação** (fachadas, luzes, NPCs na porta), sem cenas explícitas e sem interação do jogador.

## 2. Mapa de Tortuga

**A única construção em que se pode entrar é a Taverna.** O comércio fica **ao ar livre**: as lojas na **Rua Principal** e o **Mercado Pirata no Porto**, no cais, entre navios piratas e caixotes de carga roubada.

```
  ~~~~~~~~~~~~~~~~~~~~ MAR ~~~~~~~~~~~~~~~~~~~~
  [NAVIO PIRATA atracado = Mercado Pirata]
                     │ doca (píer) — vendedor pirata na frente do navio
                     [PORTO / CAIS]
                     Portal para os mapas
                            │
  ══════════════════════════╪══════ RUA PRINCIPAL ═════════════
     Boticário   Armas   Armaduras   Ferreiro
     Baú   Altar/Mestre                         [Bueiro] → Esgoto
  ══════════════════════════╪══════════════════════════════════
                            │
                       [TAVERNA] ← única porta que abre
                            │
     becos, prostíbulos, casas de apostas (só fachadas)
```

### Locais
| ID | Local | Onde | Função |
|---|---|---|---|
| `tavern` | **Taverna** | **Construção com interior** (a única) | NPCs bebem e contam histórias que **geram as missões** e **revelam as fraquezas** dos monstros (seção 3) |
| `pirate_market` | **Mercado Pirata** | **Porto**: um **navio pirata atracado na doca do porto** (decisão do autor); um **NPC pirata mercador, o único capitão da cidade, anda entre o navio e a rua** (a loja abre onde ele estiver) | **Piratas vendem itens que roubaram pelo mundo afora** (estoque que muda a cada navio que chega), **compram os valiosos** dos tesouros sem perguntas e vendem **Poções Elementais** (`05-itens-e-loot.md`, seção 5) |
| `shop_potions` | Boticário (**Meliodas**) | **Dentro da Taverna**, atrás do balcão, ao lado do Taverneiro (decisão do autor; não há banca de poções na Rua Principal) | Poções de vida e de recurso |
| `shop_weapons` | Loja de armas | Banca na Rua Principal | Compra e venda de armas comuns de **madeira, ferro e aço** (cobre e prata só na Capital) |
| `shop_armor` | Loja de armaduras | Banca na Rua Principal | Compra e venda de equipamentos comuns de **pano, ferro e aço** (cobre e prata só na Capital) |
| `blacksmith` | Ferreiro | Forja ao ar livre na Rua Principal | Crafting: encaixar gemas/runas, desmontar itens; **refino** com pergaminhos de **Ferro e Aço** (vende os pergaminhos desses tiers) — `05-1-refino.md` |
| `stash` | Baú | Na Rua Principal (baú acorrentado, guardado por um capanga de aluguel) | Baú compartilhado entre os personagens do jogador (guardar valiosos para vender quando o preço subir) |
| `respec` | Altar / Mestre | Canto da Rua Principal | Redistribuir pontos, pagando ouro |
| `training_yard` | **Área de treinamento** | Pátio nos fundos da Rua Principal | Bonecos para testar habilidades, elementos e equipamentos, sem risco (seção 5.2) | Sem guardas: os soldados que treinavam aqui foram para a segurança da Capital Real (`04-1-capital-real.md`).
| `voodoo_priest` | **Viajante do Tempo (teleporte)** | Tenda de velas, ervas e ossos num beco da Rua Principal | **Teleporta entre Tortuga, Capital e Fazenda** (há um em cada cidade), **abre portais para os pontos salvos** (checkpoints) mediante ouro e **vende o Patuá de Retorno** (seção 5.1) |
| `sewer_entrance` | **Bueiro** | Rua Principal | Entrada do **Esgoto** (mapa 1); trancado até a missão do velho bêbado |
| `port` | **Porto** e Portal de Tortuga | Fim da Rua Principal, no cais | **Portal** para os demais mapas (seção 5) + Mercado Pirata |
| — | Becos, prostíbulos, casas de apostas | Laterais | Só ambientação (fachadas fechadas) |

- Tortuga é pequena e compacta: tudo perto, para não perder tempo andando. O Viajante do Tempo fica entre a Rua Principal e o porto.
- Para usar uma loja, basta chegar perto da banca e interagir: abre a janela da loja sem trocar de cena.
- No co-op, todos os jogadores ficam juntos na cidade do host.

### O Mercado Pirata
- **Fica num navio atracado na doca do porto** (decisão do autor): um píer sai do cais até o navio, e um **pirata na frente do navio**, na ponta do píer, é quem atende (interagir com ele abre a loja). O navio do dia é o mesmo que "chega" a cada volta para Tortuga.
- **Os piratas trazem itens roubados pelo mundo afora**: armas, armaduras e acessórios de outras terras, às vezes raros ou únicos que não caem nos mapas.
- **Estoque rotativo:** a cada volta para Tortuga, "chega um navio" e o estoque muda (3 a 6 itens por vez, de raridades variadas, com preço alto).
- **Compram os valiosos** que os mercenários trazem dos tesouros (para revender em outros portos), com preços que variam conforme o navio do dia.
- Vendem as **Poções Elementais**, trazidas de terras distantes.
- Cada navio que chega tem um capitão pirata com nome e frase própria (ambientação); eles também podem contar rumores de tesouros na taverna (**proposta**).
- Regras de preço e estoque em `05-itens-e-loot.md`, seção 5.

### O ciclo do mercenário em Tortuga
1. Entrar na **Taverna**, ouvir histórias, aceitar missões e **descobrir o elemento e a fraqueza** dos monstros e do chefe.
2. Ir ao **Porto**: comprar as **Poções Elementais** certas no Mercado Pirata e conferir os itens roubados que chegaram no navio do dia (poções de vida no Boticário da Rua Principal).
3. Descer pelo **Bueiro** (Esgoto) ou atravessar o **Portal** do porto (demais mapas), enfrentar as criaturas e o chefe, pegar os tesouros.
4. Voltar (o elemento volta ao de origem) e **vender os valiosos aos piratas**.
5. Gastar o ouro em equipamentos, itens piratas, poções, crafting e bebidas.
6. Voltar à taverna para a próxima história.

## 3. A Taverna

### Conceito
A taverna (nome proposto: **Taverna do Corvo Afogado**) é o coração de Tortuga, a única construção em que se pode entrar, e o lugar onde os mercenários conseguem trabalho. Desertores, piratas, contrabandistas, marinheiros, caçadores, sobreviventes e bêbados **aparecem para beber e contar histórias**. Cada história é um rumor de tesouro, um contrato pago ou um pedido de ajuda, e **vira uma missão** que o grupo pode aceitar.

### Interior
- Salão principal com balcão, mesas e lareira; palco pequeno para o Bardo.
- Escada para um mezanino com o quadro de avisos.
- Quartos fechados (só ambientação).

### Como funciona
1. A cada volta para Tortuga, a taverna recebe **2 a 4 NPCs visitantes** sentados nas mesas ou no balcão.
2. Os visitantes têm um ícone acima da cabeça quando têm uma história para contar.
3. O jogador conversa: o NPC conta a história em um diálogo curto (3 a 6 falas).
4. **Toda história segue o mesmo roteiro:**
   1. O que está acontecendo e onde (o mapa).
   2. A **lenda real** da criatura ou do chefe, contada do jeito do NPC; se a criatura era boa na lenda, o NPC conta **como ela mudou de lado** (`03-1-bestiario.md`).
   3. O que há para ganhar (ouro, tesouro, item).
   4. **A pista de elemento e fraqueza**, sempre clara (ex.: "fogo assim só se apaga com água").
5. No fim, o jogador **aceita ou recusa** a missão.
6. A missão aceita vai para o **diário de missões**, com o **ícone do elemento do alvo e da fraqueza**, e aparece marcada no mapa.
7. A criatura entra no **bestiário** (lenda, elemento, fraqueza, dica).
8. Visitantes cujas missões não foram aceitas podem ir embora na próxima volta (e outros chegam).

### A primeira missão: a família na garrafa (e o tesouro embaixo da cidade)

> **Atualização:** o Velho Bêbado já foi rico e poderoso; Lúcifer levou as almas da família dele para a coleção e as prendeu numa garrafa (a **Garrafa da Tempestade de Almas**), que o Necromante guarda sobre o tesouro perdido da guerra. A missão pede essa garrafa (item de missão que o chefe final solta; `quest_drop` em `data/monsters.json`); ele a recebe em Tortuga e paga 400 de ouro e 450 de XP. O tesouro continua sendo a isca da conversa.

A campanha começa com os mercenários chegando à taverna sem nada. O **velho bêbado** puxa conversa e conta a primeira história:

> **Velho bêbado:** "Vocês têm cara de quem está atrás de ouro… Escutem só. Quando fundaram Tortuga, trouxeram junto parte do tesouro do reino que perdeu a guerra e esconderam lá embaixo, no esgoto, com o alquimista do rei de guarda. Anos depois, o povo daqui envenenou e queimou os ratos de lá… mas esqueceram do homem. Dizem que o Feiticeiro-Aranha fez um pacto com um demônio, ganhou patas de aranha e agora dorme em cima do tesouro, com a coroa do rei no manto. **Se vocês estão procurando tesouro, estão em cima de um!** Só levem fogo. Ele já sabe o que é fogo — e odeia."

- A missão libera o **Bueiro** da Rua Principal.
- Recompensa: o **Tesouro Perdido da Guerra** (`05-itens-e-loot.md`), que liga o primeiro mapa à origem de Tortuga e ao reino do Arqueiro.
- No baú, um **mapa antigo** mostra onde ficou o resto do tesouro: nas **Ruínas do Reino do Arqueiro**, que viram a segunda missão principal (contada pela taberneira).
- É a única missão principal contada pelo velho bêbado — e, desta vez, ele estava falando a verdade.

### Missões principais em Tortuga (mapas 1 a 5)

| Ordem | Mapa | Quem conta | Resumo da história | Pista de fraqueza |
|---|---|---|---|---|
| 1 | Esgoto de Tortuga | Velho bêbado | A Feiticeiro-Aranha guarda o tesouro perdido da guerra | Fogo |
| 2 | Ruínas do Reino do Arqueiro | Taberneira (após achar o mapa antigo no baú do Esgoto) | O Cofre Real, tomado por lobos e cães demoníacos; Cérbero guarda a porta do inferno | Água, Ar e Fogo (uma por cabeça) |
| 3 | Floresta Escura | Taberneira | Viajantes e caçadores nunca voltam; ouro nas raízes da árvore anciã, guardada pelo Leshy | Fogo |
| 4 | Cavalos Míticos | Taberneira | Pégaso e as Rédeas de Ouro do Céu | Água |
| 5 | Aves | Taberneira | Fênix e a Pena da Chama Eterna | Água |

- Os textos completos das falas e das pistas estão em `03-1-bestiario.md`.
- Equipamentos dos mapas 1 a 5 vão até o tier **Aço**; o Ferreiro de Tortuga refina até **+5** com pergaminhos de Ferro e Aço.
- Depois do mapa 5, as pistas da taverna acabam: o **Cavaleiro** conta do **Bobo da Corte** (próxima seção).

### A virada para a Capital Real
- Ao voltar a Tortuga depois da Fênix, a taberneira não tem mais histórias de tesouro.
- O **Cavaleiro** (Dorian ou Dália) conta que **conhece um Bobo da Corte, no castelo da Capital, que sabe de coisas**. No solo, ou se ninguém joga com o Cavaleiro, ele aparece como NPC na taverna e conta a mesma coisa (`04-1-capital-real.md`, seção 1).
- Isso libera o **Portal Real** (viagem Tortuga ⇄ Capital pelo portal do porto). Missões secundárias e o Mercado Pirata continuam em Tortuga.

### Exemplo de história (missão principal do Pégaso, mapa 4)
> **Taberneira:** "Você já ouviu falar do Pégaso? O cavalo de asas que nasceu do sangue da Medusa e carregava os raios de Zeus. Dizem que ele cansou dos deuses e aceitou o fogo do inferno. Agora as asas dele queimam, e ele manda em todos os cavalos das planícies… Lá em cima, nas ruínas, ele guarda as Rédeas de Ouro do Céu e mais ouro do que esta taverna viu em cem anos. Mas escuta: fogo assim só se apaga com **água**. Não suba sem ela."

### NPCs fixos da taverna
| ID | NPC | Papel |
|---|---|---|
| `tavern_keeper` | Taberneira(o) | Uma das fundadoras de Tortuga; conhece todo mundo e todos os segredos (inclusive o do tesouro roubado). Conta as **missões principais** dos mapas 2 a 5 |
| `bard` | Bardo | Canta as lendas das criaturas e dos demônios; abre o **bestiário** (lenda, elemento, fraqueza) e pode repetir qualquer pista já ouvida |
| `old_drunk` | Velho bêbado | Ex-soldado da guerra; conta a **primeira missão** (o Feiticeiro-Aranha e o tesouro do esgoto) e depois histórias exageradas de tesouros, às vezes verdadeiras (recompensa extra), às vezes não. **A pista de fraqueza dele é sempre verdadeira**, mesmo quando o tesouro é mentira |

### NPCs visitantes (tipos)
| ID | Tipo | Histórias que contam |
|---|---|---|
| `pirate` | Pirata | Ilhas distantes, navios afundados e tesouros vistos nas viagens de saque |
| `sailor` | Marinheiro / contrabandista | Naufrágios com carga valiosa, portos estranhos |
| `hunter` | Caçador de recompensas | Pagamento pela cabeça de uma criatura elite |
| `survivor` | Sobrevivente | Paga para resgatar quem ficou para trás |
| `merchant` | Mercador do mercado negro | Paga para recuperar cargas perdidas ou roubadas (ex.: pelas Harpias, no mapa 5) |
| `pilgrim` | Peregrino / sacerdote renegado | Paga para destruir locais amaldiçoados |
| `deserter` | Desertor | Conta o que viu nos campos depois da guerra: ruínas, covis, tesouros esquecidos |
| `stranger` | Estranho encapuzado | Contratos arriscados com boas recompensas; às vezes uma armadilha |

- Visitantes têm nome e aparência gerados (lista de nomes + combinações de modelo), mantendo o desempenho com poucos modelos base.
- Cada história é ligada a um mapa já liberado e à família de criaturas desse mapa (`03-inimigos.md`).

### Serviços da taverna
| Serviço | Efeito |
|---|---|
| Comprar bebida | Bônus temporário para a próxima missão (ex.: +5% de experiência, +10% de ouro, +5% de vida). Só uma bebida por vez |
| Descansar | Recupera vida e recurso por completo (gratuito na cidade) |
| Quadro de avisos | Lista as missões já ouvidas e ainda não aceitas, com o ícone de fraqueza do alvo |
| Ouvir o Bardo | Lendas e bestiário |

## 4. Missões

### Tipos
| ID | Tipo | Origem | Descrição |
|---|---|---|---|
| `main` | Tesouro do covil (principal) | Velho bêbado (Esgoto), depois Taberneira(o) | Ir até o covil do chefe, derrotá-lo e pegar o tesouro que ele guarda; ordem fixa; libera novos mapas |
| `hunt` | Caçada | Caçador, estranho | Recompensa por matar uma criatura elite ou um grupo específico |
| `rescue` | Resgate | Sobrevivente | Encontrar e escoltar um NPC até a saída do mapa |
| `retrieve` | Recuperar | Mercador, marinheiro, pirata | Achar um item perdido ou roubado no mapa |
| `purge` | Purificar | Peregrino | Destruir altares/ninhos demoníacos numa área |
| `rumor` | Rumor de tesouro | Velho bêbado, desertor, pirata | Ir até um lugar do mapa; pode ter tesouro, emboscada ou nada |

### Geração das missões secundárias
As missões secundárias são montadas a partir de **modelos** com variáveis, escolhidas conforme os mapas liberados. A lenda e a pista vêm do bestiário:

```
modelo: hunt
  npc: hunter
  mapa: <mapa liberado>
  alvo: <criatura da família do mapa> (elite)
  local: <área do mapa>
  recompensa: ouro + item (raridade conforme o nível)
  história:
    "Pago {ouro} moedas pela cabeça de um {alvo} que anda perto de {local}.
     {lenda_curta do alvo}
     {pista do alvo}"
```

- Os modelos e falas ficam em arquivos de dados (ex.: `quests/templates.json`, `npcs/visitors.json`, `bestiary/entries.json` com `lenda`, `elemento`, `fraqueza`, `pista`).
- Missões secundárias **não bloqueiam** a história; servem para ganhar experiência, ouro, itens e materiais.
- Limite de **5 missões secundárias ativas** ao mesmo tempo.

### Recompensas
Conteúdo detalhado dos tesouros em `05-itens-e-loot.md`, seção 3.

| Tipo | Recompensa |
|---|---|
| Tesouro do covil | Equipamento lendário + itens raros/únicos + valiosos para vender + ouro + materiais + relíquia; experiência alta; libera o próximo mapa |
| Secundária | Pagamento em ouro, experiência, chance de item raro, materiais de crafting |
| Rumor verdadeiro | Tesouro escondido com valiosos e item raro ou único |
| Rumor falso | Nada, ou uma emboscada |

### Co-op
- As missões pertencem à **campanha do host**.
- Qualquer jogador pode conversar com os NPCs; o diálogo aparece para todos.
- Qualquer jogador pode aceitar ou recusar; a missão vale para o grupo.
- **Ouro: cada jogador tem o seu.** O pagamento de uma missão é dado inteiro a cada jogador do grupo. Itens e valiosos: loot individual.
- O estoque do Mercado Pirata é **por jogador** (cada um vê suas próprias ofertas, como no loot).

## 5. Saídas para os mapas

### Bueiro — Esgoto
- O **Esgoto** (mapa 1) é acessado pelo **bueiro da Rua Principal**, sem barco: desce uma escada e já está no mapa.
- Depois de derrotar o Feiticeiro-Aranha, o bueiro continua aberto para missões secundárias no Esgoto.

### Portal de Tortuga — demais mapas
- No fim do cais, no **porto**, fica o **Portal de Tortuga**: um círculo de pedra com runas antigas, de antes da guerra, que os piratas descobriram e usam para sumir com a carga (proposta de lenda). **A viagem entre mapas é feita por portais** (decisão do autor), sem barco jogável nem rota a pé.
- Ao interagir, abre a **janela do portal** com os destinos já liberados: cada um mostra nome do mapa, nível recomendado, **elemento predominante do mapa e do chefe** (se a história já foi ouvida) e o estado (nova, em andamento, concluída). Serve de lembrete para comprar as Poções Elementais no Mercado Pirata, ali no cais.
- Do Portal de Tortuga saem os mapas **2 a 5**, o **Portal Real** na Capital e a volta aos mapas já visitados. Os mapas **6 a 10** saem do Portal Real (`04-1-capital-real.md`). O Esgoto continua pelo **bueiro**.
- O portal da cidade leva sempre à **primeira área** do mapa. Para ir direto a um **checkpoint mais adiante**, o grupo paga ao **Macumbeiro** (seção 5.1). Ver `03-2-areas.md`.
- O "mapa afora" entre o Esgoto e as Ruínas deixa de existir: o portal leva direto às Ruínas.
- **Co-op:** o host escolhe o destino; os outros jogadores recebem um aviso de confirmação e vão juntos (quem estiver longe do portal é puxado ao confirmar). Jogador que entra no meio surge ao lado do host.
- **Volta:** dentro de cada mapa há um **portal de retorno** na entrada da primeira área e **depois de cada chefe**; leva ao portal da cidade de onde o grupo saiu (o elemento volta ao de origem). Ao voltar, a campanha é salva (`11-saves.md`).
- Entre as áreas de um mapa, a passagem continua sendo uma porta, escada ou caminho normal (não é portal).

### 5.1 O Viajante do Tempo (antes o Macumbeiro)
| Campo | Valor |
|---|---|
| ID | `voodoo_priest` |
| Onde fica | Tortuga: tenda num beco da Rua Principal. Capital Real: um canto discreto da Avenida Real, mais arrumado (mesmo NPC, outra aparência — proposta) |
| Aparência | Roupas de pano colorido e colares de contas e dentes, cachimbo, velas acesas, galinhas e ossos pendurados; fala baixo e sorri demais |
| Personalidade | Misterioso, cobra bem e nunca pergunta o motivo; "o outro lado também tem preço" |

**Serviços:**
- **Teleporte entre cidades:** há um Viajante do Tempo em **Tortuga, na Capital Real e na Fazenda** (mesmo NPC `voodoo_priest`). A lista mostra as três cidades desde o começo, mas o grupo **só vai para outra cidade quando todas as missões de aldeia (`village`) dos mapas da cidade atual estiverem concluídas** (Tortuga: Esgoto, Floresta, Docas e Ruínas; Capital: Cemitério, Forte, Catacumbas e Deserto; Fazenda: Mina, Bunker e Floresta Escura). Antes disso os botões ficam travados e mostram quantas missões faltam. O teleporte é **de graça** e leva o grupo todo ao início da cidade escolhida (`Town.HUB_MAPS`, `Town.hub_pending`).
- **Portal para ponto salvo:** lista todos os **checkpoints já alcançados** na campanha (agrupados por mapa, com nome da área, nível e elemento do mapa). O grupo escolhe um, **paga em ouro** e atravessa o portal que ele abre. Serve para voltar ao ponto onde parou depois de ir à cidade.
  - Preço (proposta): 40 + 15 × nível da área, **por jogador** (ouro individual). Se um jogador não tiver ouro suficiente, o aviso mostra quem falta.
  - No co-op, o host escolhe e os outros confirmam (como no portal comum).
- **Vender o Patuá de Retorno** (`return_charm`): ver abaixo.
- **O portal dele abre no chão** (decisão do autor): um círculo de símbolos e velas que se risca no solo e vira um redemoinho de sombra e brasas; os jogadores **pisam nele** para atravessar. Some depois de alguns segundos. Vale também para o portal aberto pelo Patuá de Retorno, no meio do mapa.
- Mais caro que o portal comum, porque economiza a caminhada do início do mapa (a ideia é o jogador pagar pela comodidade).

### 5.2 Missões de cada mapa e a corrente entre as cidades

Cada mapa tem uma **missão de mapa** aberta por um NPC da cidade (termina sozinha quando o chefe do mapa cai):

| Cidade | Onde | NPC | Mapa |
|---|---|---|---|
| Tortuga | Taverna | Velho Bêbado · Taberneira · Capitão Pirata · **Veterano de Guerra** | Esgoto · Floresta · Docas · Ruínas (`map_ruins`) |
| Capital Real | Igreja | Padre · **Irmã Penitente Isolda** · **Peregrino Haled** | Cemitério e Forte (relíquias do Padre) · Catacumbas (`map_catacombs`) · Deserto (`map_desert`) |
| Fazenda | **Casa de Equipamentos** do fazendeiro (nova: interior `farm_shed`, porta na lateral dos campos) | **Fazendeiro Tadeu** · **Ferreiro Gorm** · **Lenhadora Odete** | Mina (`map_mine`) · Bunker (`map_bunker`) · Floresta Escura (`map_dark_forest`) |

**Corrente de missões entre as cidades** (gerada por `tools/assets/build_city_quests.py`):
0. Ao concluir a **Floresta** (`forest_treasure`, a Costela de Adão entregue à Taberneira), aparece na Taverna de Tortuga o **Veterano de Guerra**, que abre as **Ruínas** (`map_ruins`); as Docas (Capitão Pirata) abrem ao mesmo tempo.
1. Ao concluir as **Ruínas**, aparece na Taverna de Tortuga o **Cartógrafo Aldrin**, que manda ir à Capital (pelo Viajante do Tempo) buscar o **Mapa Selado** com o **Sacristão Ambrósio**, na Igreja, e trazê-lo de volta (`trav_to_capital`).
2. Ao concluir o **Deserto**, o mesmo Sacristão pede a **Foice de Prata**, que está com o **Velho Zeca**, na Casa de Equipamentos da Fazenda (`cap_to_farm`); o herói a pega com o Velho Zeca e a leva ao Sacristão.
Falas com `grants_item` entregam o item (só enquanto a missão que o pede está ativa); props com `after_quest` só aparecem depois dessa missão.

**Patuá de Retorno** (`return_charm`, consumível):
- Usado no mapa (fora de combate, 5 s de canalização), abre, **no chão**, um **portal de volta à cidade** de onde o grupo saiu, que fica aberto por 15 s para qualquer jogador do grupo atravessar.
- Usar o patuá **salva o checkpoint** atual como ponto de volta (o jogador volta a ele com o Macumbeiro).
- Preço (proposta): 150 de ouro; empilha até 5; cai também como loot raro.
- No interior de uma arena de chefe com a luta em andamento o patuá **não funciona**.

### 5.2 Área de treinamento
Decisão do autor: **cada cidade tem uma área de treinamento com bonecos**, para o jogador testar habilidades, builds e equipamentos sem risco.

| Campo | Valor |
|---|---|
| ID | `training_yard` |
| Onde | Tortuga: pátio de terra batida nos fundos da Rua Principal, com cercas de madeira e armas velhas (um velho mercenário aposentado cuida do lugar). Capital Real: campo de treino do quartel da Academia Militar (Dorian e Dália reconhecem o lugar — falas curtas, proposta) |
| Cena | Parte da cena externa da cidade (sem carregamento) |
| Quem entra | Qualquer jogador; no co-op todos veem os golpes uns dos outros. **Sem PvP** |

**Bonecos (`training_dummy_*`):**
| Boneco | Para quê |
|---|---|
| **Boneco de palha** (um por elemento: Água, Fogo, Terra, Ar) | Testar a **fraqueza e a resistência** de cada elemento (+50% / −50%, `02-0-elementos.md`); mostra o ícone do elemento e os números de dano coloridos ou cinza |
| **Boneco blindado** | Alta defesa, para comparar equipamentos e refino |
| **Boneco gigante** | Tamanho de chefe, para testar habilidades de área e de alvo único |
| **Grupo de bonecos pequenos** | Testar habilidades de área, correntes e combos de elementos (`02-0-elementos.md`, seção 7) |
| **Boneco que ataca** (opcional, liga e desliga) | Golpes com aviso no chão, para treinar esquiva, aparar (Ninja) e bloqueio |

**Painel de treino:**
- Mostra o **dano total, dano por segundo (DPS)**, maior golpe, número de críticos e tempo, com botão de zerar.
- **Recursos e recargas livres** (liga e desliga): vida, recurso e recarga das habilidades voltam ao máximo na hora, para testar à vontade.
- **Reiniciar bonecos** a qualquer momento.
- **Testar habilidades ainda não liberadas:** o jogador pode experimentar **qualquer habilidade da sua classe e do seu elemento no rank 5**, mesmo as que ainda não desbloqueou, para planejar a árvore de habilidades (proposta).
- **Testar outro elemento:** um **altar de elementos** no pátio troca o elemento do herói só dentro do pátio, de graça, para testar as habilidades dos outros elementos (proposta). Ao sair, volta ao normal.
- **Equipamento:** o que o herói veste vale normalmente; dá para trocar de arma e armadura ali mesmo (inventário aberto).

**Regras:**
- **Não dá experiência, ouro, loot nem missão** e não gasta consumíveis (poções e pergaminhos não são usados).
- Nada do pátio entra no save, exceto a lembrança das opções do painel.
- Os bonecos não têm IA complexa (poucos nós, sem pathfinding): custo baixo de desempenho.

## 6. Notas técnicas

- Tortuga tem **duas cenas**: a **área externa** (Rua Principal + porto/cais + fachadas) e o **interior da Taverna**. Nenhuma outra construção tem interior, o que economiza modelagem e desempenho.
- O Esgoto é um mapa separado, carregado ao descer pelo bueiro.
- Lojas da Rua Principal e o Mercado Pirata abrem como janelas de interface ao interagir com a banca (sem carregamento).
- Iluminação de lampiões feita com poucas luzes (desempenho em vídeo integrado).
- O portal da cidade é um modelo simples com partículas poucas; o portal do Macumbeiro e do Patuá é só um **decalque no chão** com poucas partículas, sem luz dinâmica extra; a viagem é uma tela de carregamento curta com efeito de runas.
- O mar do porto é um plano simples com animação de textura (sem simulação de água pesada); navios piratas são cenário estático com animação leve de balanço.
- NPCs de ambientação com rotinas simples (encostado, bebendo, carregando caixas, andando entre dois pontos) e poucos modelos base com variações de cor e acessórios.
- NPCs da taverna têm animações simples: sentado bebendo, em pé no balcão, falando, rindo.
- O estado das missões (aceitas, concluídas, visitantes presentes), o bestiário, os preços do dia e o estoque pirata são salvos no PC do host junto com a campanha.

## 7. Decisões em aberto

- Nome da taverna (proposta: Taverna do Corvo Afogado)?
- Os capitães piratas podem contar rumores na taverna (proposta)?
- Bebidas com bônus temporário: manter?
- Mini-jogos na taverna (dados, cartas, queda de braço)?

## Missões de relíquia (Padre da Capital)
- **O coração do rei caído** (`royal_heart`): o **Senhor da Cripta** (mini-chefe do Cemitério) deixa cair o **Coração Humano**; entregar ao Padre rende 220 B$ e 450 XP.
- **Os pulmões do rei caído** (`royal_lungs`, depois do coração): o **Ogro da Cripta** (mini-chefe da praça do Cemitério) deixa cair os **Pulmões Humanos**; 300 B$ e 600 XP.
- **O crânio do rei caído** (`royal_skull`, depois dos pulmões): o **Comandante do Forte** deixa cair o **Crânio Antigo**; 420 B$ e 800 XP.
- O item é um **valioso de missão** no inventário de cada herói (não se vende), cai só para quem tem a missão ativa, e a missão termina pelo botão **Entregar a relíquia** na conversa com o Padre.

## Missão do Bobo da Corte (Sala do Rei)
- **Banquete do rei** (`royal_banquet`): a mesa farta da sala do rei só tem frutas; o **Alfa da Matilha** (mini-chefe das Ruínas) deixa cair a **Carne Selvagem** (item de missão, no inventário, não se vende). Entregar ao Bobo rende 260 B$ e 500 XP.


## Mecânica de missões de todos os mapas (modelo: Esgoto)

1. O **NPC da cidade** passa a missão e pede um **item que só o chefe do mapa larga**; a recompensa é em ouro.
2. Dois **NPCs do mapa** dão uma missão cada: entregam um **livro** (some da bolsa quando o mini-chefe dele cai), pedem o item do mini-chefe e, ao receber o item, entregam uma **chave**.
3. Há **um só altar** por mapa, onde os mini-chefes são invocados: o livro que o grupo tem decide qual desperta (`needs_key` + `extra_summons` no prop). Nenhum mini-chefe anda solto (os que andavam viraram elites).
4. O **guardião** pede as duas chaves e abre o portão do chefe.
5. O **chefe do mapa** solta o tesouro (baú do chefe) e o item que o NPC da cidade pediu.

Gerado por `tools/assets/build_map_mechanics.py` (e `build_cemetery_quests.py`, que monta antes a estrutura do Cemitério: Coveiro, Zeladora, Guardião da Cripta e o portão do Senhor da Cripta). No Cemitério, a missão `royal_lungs` do Padre virou a do Coveiro.
