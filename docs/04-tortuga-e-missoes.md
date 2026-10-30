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
  [Navios piratas]   [PORTO / CAIS]
                     Mercado Pirata (itens roubados pelo mundo)
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
| `pirate_market` | **Mercado Pirata** | **Porto**: barracas, caixotes e conveses no cais | **Piratas vendem itens que roubaram pelo mundo afora** (estoque que muda a cada navio que chega), **compram os valiosos** dos tesouros sem perguntas e vendem **Poções Elementais** (`05-itens-e-loot.md`, seção 5) |
| `shop_potions` | Boticário | Banca na Rua Principal | Poções de vida e de recurso |
| `shop_weapons` | Loja de armas | Banca na Rua Principal | Compra e venda de armas comuns de **madeira, ferro e aço** (cobre e prata só na Capital) |
| `shop_armor` | Loja de armaduras | Banca na Rua Principal | Compra e venda de equipamentos comuns de **pano, ferro e aço** (cobre e prata só na Capital) |
| `blacksmith` | Ferreiro | Forja ao ar livre na Rua Principal | Crafting: encaixar gemas/runas, desmontar itens; **refino** com pergaminhos de **Ferro e Aço** (vende os pergaminhos desses tiers) — `05-1-refino.md` |
| `stash` | Baú | Na Rua Principal (baú acorrentado, guardado por um capanga de aluguel) | Baú compartilhado entre os personagens do jogador (guardar valiosos para vender quando o preço subir) |
| `respec` | Altar / Mestre | Canto da Rua Principal | Redistribuir pontos, pagando ouro |
| `sewer_entrance` | **Bueiro** | Rua Principal | Entrada do **Esgoto** (mapa 1); trancado até a missão do velho bêbado |
| `port` | **Porto** e Portal de Tortuga | Fim da Rua Principal, no cais | **Portal** para os demais mapas (seção 5) + Mercado Pirata |
| — | Becos, prostíbulos, casas de apostas | Laterais | Só ambientação (fachadas fechadas) |

- Tortuga é pequena e compacta: tudo perto, para não perder tempo andando.
- Para usar uma loja, basta chegar perto da banca e interagir: abre a janela da loja sem trocar de cena.
- No co-op, todos os jogadores ficam juntos na cidade do host.

### O Mercado Pirata
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

### A primeira missão: o tesouro embaixo da cidade
A campanha começa com os mercenários chegando à taverna sem nada. O **velho bêbado** puxa conversa e conta a primeira história:

> **Velho bêbado:** "Vocês têm cara de quem está atrás de ouro… Escutem só. Quando fundaram Tortuga, trouxeram junto parte do tesouro do reino que perdeu a guerra e esconderam lá embaixo, no esgoto, longe dos vencedores. Anos depois, o povo daqui envenenou e queimou os ratos de lá… mas esqueceram da mãe. Dizem que a Rainha dos Ratos fez um pacto com um demônio, cresceu do tamanho de uma carroça e agora dorme em cima do tesouro, com a coroa do rei na cabeça. **Se vocês estão procurando tesouro, estão em cima de um!** Só levem fogo. Ela já sabe o que é fogo — e odeia."

- A missão libera o **Bueiro** da Rua Principal.
- Recompensa: o **Tesouro Perdido da Guerra** (`05-itens-e-loot.md`), que liga o primeiro mapa à origem de Tortuga e ao reino do Arqueiro.
- No baú, um **mapa antigo** mostra onde ficou o resto do tesouro: nas **Ruínas do Reino do Arqueiro**, que viram a segunda missão principal (contada pela taberneira).
- É a única missão principal contada pelo velho bêbado — e, desta vez, ele estava falando a verdade.

### Missões principais em Tortuga (mapas 1 a 5)

| Ordem | Mapa | Quem conta | Resumo da história | Pista de fraqueza |
|---|---|---|---|---|
| 1 | Esgoto de Tortuga | Velho bêbado | A Rainha dos Ratos guarda o tesouro perdido da guerra | Fogo |
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
| `old_drunk` | Velho bêbado | Ex-soldado da guerra; conta a **primeira missão** (a Rainha dos Ratos e o tesouro do esgoto) e depois histórias exageradas de tesouros, às vezes verdadeiras (recompensa extra), às vezes não. **A pista de fraqueza dele é sempre verdadeira**, mesmo quando o tesouro é mentira |

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
- Depois de derrotar a Rainha dos Ratos, o bueiro continua aberto para missões secundárias no Esgoto.

### Portal de Tortuga — demais mapas
- No fim do cais, no **porto**, fica o **Portal de Tortuga**: um círculo de pedra com runas antigas, de antes da guerra, que os piratas descobriram e usam para sumir com a carga (proposta de lenda). **A viagem entre mapas é feita por portais** (decisão do autor), sem barco jogável nem rota a pé.
- Ao interagir, abre a **janela do portal** com os destinos já liberados: cada um mostra nome do mapa, nível recomendado, **elemento predominante do mapa e do chefe** (se a história já foi ouvida) e o estado (nova, em andamento, concluída). Serve de lembrete para comprar as Poções Elementais no Mercado Pirata, ali no cais.
- Do Portal de Tortuga saem os mapas **2 a 5**, o **Portal Real** na Capital e a volta aos mapas já visitados. Os mapas **6 a 10** saem do Portal Real (`04-1-capital-real.md`). O Esgoto continua pelo **bueiro**.
- O destino de cada mapa é sempre a **primeira área** do mapa, ou o **último checkpoint** alcançado nele (o jogador escolhe na janela). Ver `03-2-areas.md`.
- O "mapa afora" entre o Esgoto e as Ruínas deixa de existir: o portal leva direto às Ruínas.
- **Co-op:** o host escolhe o destino; os outros jogadores recebem um aviso de confirmação e vão juntos (quem estiver longe do portal é puxado ao confirmar). Jogador que entra no meio surge ao lado do host.
- **Volta:** dentro de cada mapa há um **portal de retorno** na entrada da primeira área e **depois de cada chefe**; leva ao portal da cidade de onde o grupo saiu (o elemento volta ao de origem). Ao voltar, a campanha é salva (`11-saves.md`).
- Entre as áreas de um mapa, a passagem continua sendo uma porta, escada ou caminho normal (não é portal).

## 6. Notas técnicas

- Tortuga tem **duas cenas**: a **área externa** (Rua Principal + porto/cais + fachadas) e o **interior da Taverna**. Nenhuma outra construção tem interior, o que economiza modelagem e desempenho.
- O Esgoto é um mapa separado, carregado ao descer pelo bueiro.
- Lojas da Rua Principal e o Mercado Pirata abrem como janelas de interface ao interagir com a banca (sem carregamento).
- Iluminação de lampiões feita com poucas luzes (desempenho em vídeo integrado).
- O portal é um modelo simples com partículas poucas e uma luz fraca (sem luz dinâmica extra); a viagem é uma tela de carregamento curta com efeito de runas.
- O mar do porto é um plano simples com animação de textura (sem simulação de água pesada); navios piratas são cenário estático com animação leve de balanço.
- NPCs de ambientação com rotinas simples (encostado, bebendo, carregando caixas, andando entre dois pontos) e poucos modelos base com variações de cor e acessórios.
- NPCs da taverna têm animações simples: sentado bebendo, em pé no balcão, falando, rindo.
- O estado das missões (aceitas, concluídas, visitantes presentes), o bestiário, os preços do dia e o estoque pirata são salvos no PC do host junto com a campanha.

## 7. Decisões em aberto

- Nome da taverna (proposta: Taverna do Corvo Afogado)?
- Os capitães piratas podem contar rumores na taverna (proposta)?
- Bebidas com bônus temporário: manter?
- Mini-jogos na taverna (dados, cartas, queda de braço)?
