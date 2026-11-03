# Roteiro — O Livro das Dívidas

> Versão 1 · 2026-11-03 · A trama macabra da campanha, costurada em todas as missões do jogo, na **ordem dos mapas**: 1 Esgoto, 2 Floresta, 3 Docas, 4 Ruínas, 5 Cemitério, 6 Forte, 7 Catacumbas, 8 Deserto, 9 Mina, 10 Bunker, 11 Floresta Escura.
> Complementa `06-mundo-e-historia.md` (premissa, reinos, heróis, Lúcifer), `04-tortuga-e-missoes.md`, `04-1-capital-real.md` e `13-balanceamento.md`. Onde este roteiro propõe algo novo, está marcado como **proposta**. Os textos de jogo ainda precisam ser escritos nas falas (pt/en/es) seguindo estas cenas.
> Ids de missão (`quests.json`), NPCs (`npcs.json`) e itens (`valuables.json`) estão entre crases para a equipe achar cada cena no jogo.

---

## 1. A ideia: ouro é dívida

**Lúcifer não rouba ouro: ele empresta.** Em Eldrath, toda moeda que sobrou da guerra foi emprestada por ele, em contratos escritos com tinta de cinza e assinados com um dedo. Quem não paga entrega a **alma**; a alma vai para uma **garrafa**, uma **peça de corpo** ou um **cargo** (guardião de um covil). Os demônios dos mapas não "guardam tesouros": **cobram dívidas**, e cada tesouro é o lucro de uma.

Três fios correm juntos pela campanha:

| Fio | O que é | Onde aparece |
|---|---|---|
| **As dívidas** | Cada NPC de cidade que manda os mercenários buscar um item **assinou um contrato** com Lúcifer. O item que o chefe do mapa guarda é a **garantia** da dívida dele. Entregá-lo quita o contrato, mas **o ouro que o NPC paga é ouro de Lúcifer**, então quem recebe também fica devendo (ver 1.1) | As 12 missões de cidade (`sewer_treasure` … `map_dark_forest`) |
| **O Rei Faminto** | O último rei de Veldmark foi **desenterrado e repartido**: coroa, coração, pulmões, crânio, alma e a carne do banquete. Lúcifer quer **montar o corpo de novo** para ter um rei de verdade no mundo dos vivos: um corpo que **nunca morre porque já morreu** | As relíquias do Padre (`royal_heart`, `ce_lungs`, `royal_skull`, `royal_soul`), `royal_banquet`, `map_ruins` |
| **A Moeda Negra** | A companhia dos mercenários nasceu de um brinde na taverna de Tortuga, com **um livro de registro assinado a sangue**. O livro é **o último contrato**: o deles | Prólogo e Ato Final |

### 1.1 A regra que torna tudo macabro

- Cada missão de cidade termina com uma **recompensa em ouro** (o jogo paga) e **uma cena curta no dia seguinte** (`after_quest`, na volta à cidade): o NPC está **diferente** — livre, ausente, ou pior. A cena mostra o preço.
- O jogador nunca é obrigado a perceber: a dívida só fecha para quem junta as pistas (os diários, os livros, as falas das almas). Quem ler tudo, entende no Ato Final que **o ouro das recompensas também era emprestado**.

### 1.2 Tom e regras de escrita

- **Macabro, frio e específico**: corpos, garrafas, ossos, sinos, cinzas, trapos, carne, gordura, correntes; sempre uma imagem concreta, nunca "o mal".
- **Sem vilões de desenho animado**: os demônios são cobradores educados. O horror vem da **burocracia** da dívida.
- Humor só nas falas cínicas dos mercenários, dos piratas e do Bobo; **nunca** nas almas presas.
- Cada mapa termina com **uma imagem que fica** (as "peças" de cada cena abaixo).
- Os heróis são mercenários: **não resgatam ninguém por bondade**; o macabro bate neles pelo preço.

---

## 2. Elenco

| Papel | Quem | Onde |
|---|---|---|
| **O Credor** | **Lúcifer** (chefe final, Inferno ainda por construir) | Fora de cena até o final |
| **O Tabelião** | **Sacristão Ambrósio** (`sacristan`): o demônio que redige os contratos, disfarçado de sacristão | Igreja da Capital |
| **O Bobo da Corte** | Quem descobre a dívida do reino e passa as pistas; será sequestrado | Castelo da Capital (`court_jester`) |
| **O Viajante do Tempo** | Viajante que entra e sai das cidades; ele **já viu** o fim (proposta: é o único que paga a dívida dos outros em tempo) | Uma por cidade |
| **O Padre** | Sincero e errado: quer sepultar o rei inteiro, e sem saber **monta o corpo** | Igreja da Capital (`priest`) |
| **Os devedores** (NPCs de cidade que pedem itens) | Velho Bêbado, Taberneira, Capitão Pirata, Veterano de Guerra, Padre, Irmã Penitente, Peregrino Haled, Cartógrafo, Fazendeiro Tadeu, Ferreiro Gorm, Lenhadora Odete, Sacristão | Taverna, Igreja, Casa de Equipamentos |
| **Os cobradores** (chefes) | Necromante, Leshy, Capitão Afogado, Rei Caído, Senhor da Cripta, Barão Infernal, Rei Acorrentado, Esfinge, Golem de Cristal, General Ferrugem, Ancião Sombrio | Um por mapa |
| **Os mercenários** | Mago, Arqueiro, Cavaleiro (Dorian ou Dália), Ninja (Ren ou Rin), Invocador | A companhia da Moeda Negra |

---

## 3. Prólogo — Tortuga, a taverna (abertura)

**Cena.** Noite de chuva fina. A taverna fede a sebo e cerveja azeda. Cada herói conta por que está ali (`06`, seção 5). O **Velho Bêbado** (`old_drunk`) interrompe com um brinde. Para pagar a rodada, o taberneiro abre o **livro de registro** da casa: quem quer fiado assina. Os heróis assinam como companhia: **Companhia da Moeda Negra**. A tinta é preta e quente. Ninguém percebe que ela não seca.

**Gancho.** O Velho Bêbado oferece a primeira missão: *"Se vocês estão procurando tesouro, estão em cima de um."*

**Imagem que fica.** A assinatura da companhia, no livro, **ainda úmida** de manhã.

---

## 4. Ato I — Tortuga (mapas 1 a 4)

A cidade sem rei, onde a dívida circula de mão em mão sem que ninguém pergunte de quem era.

### Mapa 1 — Esgoto de Tortuga (nível 1)

**Verdade do lugar.** Os fundadores de Tortuga roubaram o ouro do reino derrotado e o esconderam no esgoto, **junto com os mortos da guerra** (a Vala dos Mortos). Murar tudo era mais barato que enterrar. O alquimista do rei, deixado no escuro para vigiar o ouro, assinou com Lúcifer em troca de **não morrer**: virou o **Necromante** (chefe).

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `sewer_treasure` — *A Família na Garrafa* (Velho Bêbado) | O velho, bêbado e rico, assinou o primeiro contrato da cidade: Lúcifer levou a **família dele** e a engarrafou. Pede a **Garrafa da Tempestade de Almas** (`storm_bottle`) |
| **O primeiro morador** | `sewer_frog_king` — *A Garrafa do Tormento Eterno* (Ossael, o Anjo Caveira) | Guardião dos afogados, despojado de carne e penas. Entrega o **Livro do Altar** (`altar_book`), as preces dos afogados. Pede a **Garrafa do Tormento Eterno** (`torment_bottle`) e paga com a **chave de copas** |
| **O segundo morador** | `sewer_old_gator` — *A Garrafa das Almas Condenadas* (Azazel, o Anjo Flamejante) | Mandado por Lúcifer, mas cansado de ser cobrador. Entrega o **Grimório das Brasas** (`gator_book`). Pede a **Garrafa das Almas Condenadas** (`souls_bottle`) e paga com a **chave de espadas** |
| **O altar único** | Altar do centro (`sewer_frog_altar`) | O livro de cada anjo desperta um mini-chefe: o **Empalado** (carne, ossos e tábuas; cada prego prende uma alma) ou o **Carniceiro Chifrudo** (demônio açougueiro). Quando o mini-chefe cai, **o livro some da bolsa** |
| **O portão** | Guardião do Portão do Ninho (`gate_keeper`) | Só abre com as duas chaves |
| **O cobrador** | Necromante (`demon_rat_queen`) | Costura mortos em servos; guarda a Garrafa da Tempestade de Almas e o **Tesouro Perdido da Guerra** |

**Preço.** Voltando com a garrafa, o Velho Bêbado a abre sozinho, no balcão. A família some em fumaça, e ele **pega no sono no mesmo banco, sorrindo, e não acorda**. A taberneira limpa a mesa e conta: *"Quitado."*

**Imagem que fica.** O velho sentado, com a garrafa vazia na mão e o brinde do primeiro dia ainda no copo.

**Gancho.** No baú do Necromante, junto do tesouro, um **mapa antigo** com uma cruz sobre uma **floresta** e uma frase: *"Quem leva, devolve."*

---

### Mapa 2 — Floresta (nível 3)

**Verdade do lugar.** O caminho que os fundadores abriram para levar o ouro até Tortuga: as árvores engoliram a trilha **e os carregadores**. Os troncos têm **rostos**.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `forest_treasure` — *A Costela de Adão* (Taberneira) | A taberneira confessa: pagou a casa da taverna com a **costela de um homem vivo**. Pede a **Costela de Adão** (`adams_rib`), guardada pelo Leshy |
| **O morador** | `forest_leshy` — *A Adaga de Osso* (Exploradora, `elf_archer`) | A Exploradora perdeu o grupo nas raízes. Entrega o **Mapa das Trilhas** (`forest_book_1`). Pede a **Adaga de Osso de Dinossauro** (`bone_dagger`) e paga com a **chave de espadas** |
| **A moradora** | `forest_fire_golem` — *A caveira de Morvak* (Aelindra, Guardiã da Pira) | Queima os mortos da floresta para que não voltem; entre eles, Morvak voltou. Entrega as **Cinzas da Pira** (`forest_book_2`). Pede a **Caveira de Morvak** (`cursed_skull`) e paga com a **chave de copas** |
| **O altar único** | Templo em ruínas (`forest_temple`) | O mapa desperta o **Rei Golem de Pedra** (e o Guardião do Túmulo); as cinzas despertam o **Golem de Fogo** |
| **O portão** | `forest_gate` — *O Portão do Leshy* (Guardião do Portão) | Pede as duas chaves |
| **O cobrador** | **Leshy**, o gigante de casca | Guarda a Costela de Adão e o **ouro dos viajantes perdidos** (`treasure_forest`) |

**Preço.** A taberneira pega a costela e a **encaixa no próprio peito**, por baixo do avental. Fica mais alta, mais calada. Dali em diante **atende sem olhar nos olhos**.

**Imagem que fica.** O Leshy caído, com os troncos em volta **soltando os rostos**, um a um, como quem finalmente expira.

---

### Mapa 3 — Docas (nível 5)

**Verdade do lugar.** O cais onde os piratas descarregam o que roubam: e também os **corpos** que sobram dos roubos. As marés devolvem o que o Capitão Afogado não quis.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `docks_smugglers` — *O cais do Velho Lobo* (Capitão Pirata, na taverna) | O capitão vendeu a **tripulação inteira** em troca de uma travessia sem tempestade. Pede o **Diário do Capitão Afogado** (`captain_log`): a lista de quem ficou |
| **O morador** | `dock_helm` — *O Leme Perdido* (Mestre do Porto) | Entrega o **Diário do Mestre do Cais** (`docks_book_1`). Pede o **Leme do Casco Vivo** (`ship_helm`) e paga com a **chave da âncora** |
| **A moradora** | `dock_tooth` — *O Dente de Ouro* (Peixeira) | Entrega a **Receita da Peixeira** (`docks_book_2`), um molho que **não deveria ser comido**. Pede o **Dente de Ouro do Tubarão** (`golden_shark_tooth`) e paga com a **chave da bússola** |
| **O altar único** | Altar do Cais (`wrecked_hull`) | Desperta o **Casco Vivo** (casco encalhado que respira) ou o **Tubarão-Porco** |
| **O portão** | `dock_gate` — *O Portão do Capitão* (Vigia do Cais) | Duas chaves |
| **O cobrador** | **Capitão Afogado**, esqueleto verde do mar | Guarda o Diário e o ouro dos naufrágios |

**Preço.** Com o diário em mãos, o Capitão Pirata lê em voz alta **cada nome da tripulação**, até o último. No fim, lê o próprio. **Vai ao cais e se joga**. A taverna aposta quanto ele leva para afundar. Ninguém ganha.

**Imagem que fica.** Os afogados do cais, finalmente deitados **de bruços**, olhando para o fundo.

---

### Mapa 4 — Ruínas da Cidade (nível 7)

**Verdade do lugar.** O que sobrou da cidade que perdeu a guerra: ruas de pedra, casas sem teto, um banquete que **nunca terminou**. Os mortos continuam à mesa e **ainda esperam o rei**.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `map_ruins` — *A Cripta do Rei Caído* (Veterano de Guerra, na taverna) | O veterano lutou do lado vencedor e **vendeu a vitória**: cada morto que ele mandou à cova pagou um juro. Pede a **Coroa do Rei Caído** (`fallen_crown`) |
| **O banquete** | `royal_banquet` — *Banquete do rei* (Bobo da Corte) | O Bobo precisa de **Carne Selvagem** (`wild_meat`) do **Alfa da Matilha** (elite) para o rei de Aurenval, que "só come o que a guerra deixou". **Proposta:** o Bobo sabe que a carne é **do reino derrotado**: o rei vencedor está se alimentando dele |
| **A limpeza** | `ruins_goblins` — *Praga de Goblins* (Leônidas, o Veterano) | Os goblins comem os vivos que sobram. Leônidas conta **quantos** sobraram: nenhum |
| **O morador** | `ruins_seal` — *O Coração de Pedra* (Erudita) | Entrega o **Códice do Erudito** (`ruins_book_1`). Pede o **Coração de Pedra** (`stone_heart`) do **Guardião das Ruínas** e paga com a **chave do leão** |
| **A moradora** | `ruins_banner` — *O Estandarte do Campeão* (Sacerdotisa) | Entrega a **Prece da Sacerdotisa** (`ruins_book_2`). Pede o **Estandarte do Campeão** (`champion_banner`) do **Campeão Caído** e paga com a **chave da águia** |
| **O altar único** | Estátua do Cavaleiro (`ruins_knight_statue`) | Códice desperta o Guardião; prece desperta o Campeão |
| **O portão** | `ruins_gate` — *O Portão do Rei* (Porteiro) | Duas chaves |
| **O cobrador** | **Rei Caído** (`fallen_king`) | Guarda a **Coroa**: o primeiro pedaço do corpo do último rei, e o **Cofre Real** |

**Preço.** Depois que o veterano recebe a coroa, **perde a idade de uma vez**: os cabelos brancos viram pó, o rosto desce, os olhos secam. Um velho de 90 anos senta-se e **pergunta em que ano estamos**.

**Imagem que fica.** A mesa do banquete, pela primeira vez **com o lugar do rei vazio e a cadeira empurrada para trás**.

**Interlúdio — o mapa selado.** Terminando as Ruínas, o **Cartógrafo Aldrin** (`cartographer`) aparece na taverna: precisa do **Mapa Selado** (`sealed_map`, missão `trav_to_capital`) que o **Sacristão Ambrósio** guarda na igreja da Capital. O **Viajante do Tempo** leva o grupo à Capital. O Sacristão entrega o mapa com um **sorriso quieto demais**. *(Proposta: o mapa mostra a Raiz do Mundo sob a Floresta Escura. Só o último ato revela isso.)*

---

## 5. Ato II — Capital Real (mapas 5 a 8)

Aurenhold, rica, limpa e falsa. O Bobo da Corte sussurra pelas colunas. A igreja cheira a incenso e a **carne**.

> **O Padre** (`priest`) abre a campanha de relíquias: ele lutou contra o último rei de Veldmark em vida e **acha que ninguém merece o que fizeram com o corpo**. Paga em ouro da Igreja a quem trouxer as peças de volta, para uma sepultura inteira.

### Mapa 5 — Cemitério (nível 9)

**Verdade do lugar.** O campo da batalha final. Os mortos foram enterrados em covas rasas, de pé, para **caber mais**. À noite as covas se abrem sozinhas.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `royal_heart` — *O coração do rei caído* (Padre) | Pede o **Coração Humano** (`human_heart`) guardado pelo **Senhor da Cripta** |
| **O morador** | `ce_lungs` — *Os Pulmões do Coveiro* (Coveiro Abel) | Abel enterrou **quarenta anos** de mortos e conta que alguns **voltaram pedindo mais terra**. Entrega o **Rol do Coveiro** (`cemetery_book_1`). Pede os **Pulmões Humanos** (`human_lungs`) do **Ogro da Cripta** e paga com a **Chave do Ossuário** |
| **A moradora** | `ce_lantern` — *A Lamparina do Sentinela* (Zeladora Mirta) | Acende as lamparinas dos mortos **para que eles achem o caminho de volta**; a última foi roubada pelo Sentinela. Entrega o **Registro da Zeladora** (`cemetery_book_2`). Pede a **Lamparina do Sentinela** (`warden_lantern`) e paga com a **Chave da Cripta** |
| **O altar único** | Estátua do poste de luz, o **Altar da Alameda** (`lamp_statue`) | O Rol desperta o **Ogro da Cripta**; o Registro, o **Sentinela do Túmulo** |
| **O portão** | `ce_gate` — *O Portão da Cripta* (Guardião da Cripta) | Duas chaves |
| **O cobrador** | **Senhor da Cripta** (`crypt_lord`) | Guarda o **coração**, que **ainda bate** |

**Preço.** O Padre recebe o coração, cobre-o com um pano e **chora**. Pede que ninguém o toque. Ao anoitecer, o pano **sobe e desce** no ritmo de alguém respirando. O Padre o enterra no jardim da igreja, **em um caixão do tamanho de um punho**.

**Imagem que fica.** Um caixão pequeno, bem cavado, com **uma flor** em cima, e dentro dele, um pulso.

---

### Mapa 6 — Forte (nível 11)

**Verdade do lugar.** O último posto do exército derrotado. O comandante jurou **nunca largar o posto** e Lúcifer aceitou o juramento: o forte hoje é guarnição **de quem não pode sair**.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `royal_skull` — *O crânio do rei caído* (Padre) | Pede o **Crânio Antigo** (`old_skull`). Quem o levou como troféu para Lúcifer foi o **Barão Infernal**; **proposta:** o crânio **fala** no escuro e o barão o ouve toda noite |
| **A limpeza** | `fort_purge` — *Limpar os Quartéis* (Sargento da Guarnição) | O sargento pede que os quartéis sejam esvaziados; **ele mesmo está morto** e só não sabe |
| **O morador** | `fort_sigil` — *A Lâmina do Senhor Elfo* (O Exilado) | Elfo sombrio expulso do próprio povo. Entrega o **Pacto do Exilado** (`fort_book_1`). Pede a **Lâmina do Senhor Elfo** (`dark_blade`) e paga com a **chave de ônix** |
| **A moradora** | `fort_ring` — *O Anel da Rainha* (A Penitente) | Súcubo arrependida. Entrega o **Rosário da Penitente** (`fort_book_2`). Pede o **Anel da Rainha** (`queen_ring`) e paga com a **chave de rubi** |
| **O altar único** | Altar das Muralhas (`fort_altar`) | O Pacto desperta o **Senhor Elfo Sombrio**; o Rosário, a **Rainha das Súcubas** |
| **O portão** | `fort_gate` — *O Portão do Barão* (Carcereiro do Forte) | Duas chaves |
| **O cobrador** | **Barão Infernal** (`fort_baron`) | Guarda o **crânio** e o ouro do exército |

**Preço.** Quando o Padre recebe o crânio, ele o **segura entre as mãos e ouve**. O crânio diz uma frase só, e o Padre **empalidece e guarda o silêncio**. A frase é o nome de quem **assinou a exumação do rei**: ***Ambrósio***. *(Proposta: o jogador só vê o Padre guardando o crânio no cofre; quem escutou o nome é o Bobo, que passa a vigiar o Sacristão.)*

**Imagem que fica.** O Barão caído, e **centenas de soldados sentando-se no chão do forte**, de uma vez, como se alguém tivesse dado a ordem de baixar armas.

---

### Mapa 7 — Catacumbas (nível 13)

**Verdade do lugar.** Sob a Capital: celas, correntes e um rei que **não pôde ser morto** pelos próprios carcereiros. Aqui o reino vencedor **guardou** os que não pôde julgar.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `map_catacombs` — *As Catacumbas dos Condenados* (Irmã Penitente Isolda) | Isolda condenou inocentes por ordem da Igreja e **assinou por cada um**. Pede o **Elo do Rei Acorrentado** (`chained_link`) |
| **A limpeza** | `ct_purge` — *Limpar as Celas* (Frade) | O frade conta as celas e erra: sempre **uma a mais** |
| **O morador** | `ct_axe` — *O Machado do Carrasco* (Carcereiro Cego) | Cego por escolha: **não suportou ver** o que fazia. Entrega o **Registro do Carcereiro** (`catacombs_book_1`). Pede o **Machado do Carrasco** (`headsman_axe`) e paga com a **chave de ferro** |
| **A moradora** | `ct_soul` — *O Grilhão da Alma* (Prisioneira) | Está presa há tantos anos que **esqueceu o crime**. Entrega o **Lamento do Prisioneiro** (`catacombs_book_2`). Pede o **Grilhão da Alma** (`soul_shackle`) e paga com a **chave de osso** |
| **O altar único** | A forca (`ct_gibbet`) | O Registro desperta o **Carrasco das Catacumbas**; o Lamento, a **Alma Acorrentada** |
| **O portão** | `ct_gate` — *O Portão do Rei Acorrentado* (Diretor) | Duas chaves |
| **O cobrador** | **Rei Acorrentado** (`ct_king`) | Guarda o **Elo**: o primeiro elo da corrente que prende **tudo** |

**Preço.** Isolda recebe o elo e **o veste no pescoço**. Ao dia seguinte, as irmãs a encontram **de joelhos no corredor**, ainda rezando, **sem pulsação e sem cair**. Ninguém ousa tocá-la.

**Imagem que fica.** O Rei Acorrentado em pé, quando a corrente cai, **sem saber o que fazer com as mãos**.

---

### Mapa 8 — Deserto, o Cânion (nível 15)

**Verdade do lugar.** As caravanas do rei de Aurenval **somem aqui**. Cada uma enterrada de pé na areia, com a carga: os mortos continuam a **vender** para quem passa.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `map_desert` — *O Enigma da Esfinge* (Peregrino Haled) | Haled atravessou o deserto com **três irmãos de fé**. A Esfinge propôs um enigma: ele **respondeu** e os três **pagaram a resposta**. Pede o **Olho da Esfinge** (`sphinx_eye`) |
| **O morador** | `desert_horn` — *O Chifre do Lamassu* (Nômade) | Vende água a quem passa; **ninguém vê a cor dela**. Entrega o **Papiro do Nômade** (`desert_book_1`). Pede o **Chifre do Lamassu** (`lamassu_horn`) e paga com a **chave de paus** |
| **A moradora** | `desert_scarab` — *O Escaravelho de Ouro* (Guardiã do Oásis) | O oásis tem **dentes** na água. Entrega a **Tábua do Oásis** (`desert_book_2`). Pede o **Escaravelho de Ouro** (`golden_scarab`) da **Rainha Escorpião** e paga com a **chave de ouros** |
| **O altar único** | O templo soterrado (`desert_temple`) | O Papiro desperta o **Lamassu da Areia**; a Tábua, a **Rainha Escorpião** |
| **O portão** | `desert_gate` — *O Portão da Esfinge* (Sentinela) | Duas chaves |
| **O cobrador** | **Esfinge** (`sphinx`) | Faz o enigma **que ninguém acerta duas vezes**; guarda o **Olho** e o ouro das caravanas |

**Preço.** Haled recebe o olho e **o coloca na cavidade vazia de um dos companheiros que carregou nas costas**. O companheiro **abre a boca** e **diz uma última prece**; Haled responde com o **mesmo enigma**, sem pausa. Dali em diante, os dois **caminham juntos** para o deserto, e **nunca mais voltam**.

**Imagem que fica.** O vento deslizando por uma Esfinge **sem olhos**, e a areia correndo entre os dedos dela como **ampulheta**.

**Interlúdio — a foice de prata.** Concluído o Deserto, o **Sacristão Ambrósio** (`cap_to_farm`) pede a **Foice de Prata** (`silver_sickle`) que o **Velho Zeca** guarda na **Casa de Equipamentos da Fazenda**. O Viajante do Tempo leva o grupo à Fazenda. A foice **não enferruja**.

---

## 6. Ato III — A Fazenda (mapas 9 a 11)

O campo bonito, com a casa de equipamentos, as galinhas, o riacho. E **por baixo, um labirinto**, um forte infectado e uma floresta onde as árvores **sussurram contas**. O campo sempre foi **o celeiro de Lúcifer**: a terra é fértil porque é adubada com o que a guerra deixou.

### Mapa 9 — Mina de Cristais (nível 17)

**Verdade do lugar.** Os mineiros cavaram até onde **não devia haver mais nada** e acharam um coração de cristal, **batendo**. Cavaram em volta.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `map_mine` — *O Coração da Mina* (Fazendeiro Tadeu) | Tadeu mandou seus empregados à mina para pagar a safra: **meia dúzia nunca voltou**. Pede o **Coração de Cristal** (`crystal_heart`) |
| **A alma do rei** | `royal_soul` — *A alma do rei caído* (Padre) | O Padre pede a **Alma do Rei** (`royal_soul`), do **Guardião do Túmulo**. **Proposta:** a alma está **presa na pedra** da mina e **chora** quando o picão bate |
| **A limpeza** | `mn_clear` — *Limpar as Galerias* (Aprendiz de Mineiro) | O aprendiz só sabe **contar os colegas**; sempre dá um número menor |
| **O morador** | `mn_tusk` — *A Presa do Chefe Troll* (Capataz Brokk) | Entrega o **Mapa das Galerias** (`mine_book_1`). Pede a **Presa do Chefe Troll** (`troll_tusk`) e paga com a **chave de picareta** |
| **A moradora** | `mn_quartz` — *O Núcleo de Quartzo* (Joalheiro Dolgrim) | Entrega o **Catálogo do Joalheiro** (`mine_book_2`). Pede o **Núcleo de Quartzo** (`quartz_core`) e paga com a **chave de lanterna** |
| **O altar único** | Altar de Cristal (`mn_ore_cart`) | O Mapa desperta o **Chefe Troll**; o Catálogo, a **Besta de Quartzo** |
| **O portão** | `mn_gate` — *O Portão do Coração da Mina* (Guarda-Chaves Thrain) | Duas chaves |
| **O cobrador** | **Golem de Cristal** (`crystal_golem`) | Guarda o **Coração de Cristal**: o **segundo coração**, que não é de carne |

**Preço.** Tadeu recebe o coração e o põe no peito de um **espantalho** da horta. O espantalho **dá um passo**. Tadeu o **chama de filho** e **o leva para casa**. Naquela noite, as galinhas somem.

**Imagem que fica.** Cristais brotando pelas paredes da mina, e dentro de cada um, **o rosto de um mineiro**, sorrindo.

---

### Mapa 10 — Bunker (nível 19)

**Verdade do lugar.** O abrigo que o reino vencedor construiu **para si** na guerra, e **lacrou com os soldados dentro**. A comida acabou, a doença não. O general **mandou comer os doentes**.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `map_bunker` — *O Bunker Lacrado* (Ferreiro Gorm) | Gorm forjou as **portas do bunker**, **sem saída por dentro**, por ordem do general. Pede o **Bastão do General** (`general_baton`) |
| **A limpeza** | `bk_clear` — *Limpar a Entrada* (Sargento da Guarnição) | **O mesmo sargento do Forte**, **de novo**: não percebeu que morreu duas vezes |
| **O morador** | `bk_seal` — *O Selo do Arsenal* (Intendente Vorn) | Entrega o **Registro do Intendente** (`bunker_book_1`), o racionamento: números que **não fecham**. Pede o **Selo do Arsenal** (`armory_seal`) e paga com a **chave de latão** |
| **A moradora** | `bk_medal` — *A Medalha de Guerra* (Médica de Campo Lena) | Entrega o **Prontuário do Médico** (`bunker_book_2`). Pede a **Medalha do Comandante** (`commander_medal`) e paga com a **chave de aço** |
| **O altar único** | Altar da Armaria (`bk_rack`) | O Registro desperta a **Armadura Viva**; o Prontuário, o **Comandante Podre** |
| **O portão** | `bk_gate` — *O Portão da Sala de Comando* (Sentinela) | Duas chaves |
| **O cobrador** | **General Ferrugem** (`bk_general`) | Guarda o bastão e o **estoque que nunca acabou** |

**Preço.** Gorm recebe o bastão e **o enfia na bigorna**: a bigorna **sangra**. Ele larga o martelo, vai até a porta e **tranca-se por dentro**, na própria forja. As batidas continuam **por três dias**, sem ninguém dentro para dar.

**Imagem que fica.** As portas do bunker finalmente **abertas por dentro**, e os soldados saindo de fila, **famintos e civilizados**, pedindo para **voltar à fila**.

---

### Mapa 11 — Floresta Escura (nível 20)

**Verdade do lugar.** A mata fechada atrás da Fazenda, onde **a cidade vem enterrar o que não quer**. No centro, o **Ancião Sombrio**: a árvore onde **a Raiz do Mundo** encosta na terra. Daqui, Lúcifer **cobra** a safra.

| Cena | Missão / objeto | O que acontece |
|---|---|---|
| **A dívida da cidade** | `map_dark_forest` — *A Floresta que Escureceu* (Lenhadora Odete) | Odete **derrubou árvores demais** e **plantou** em troca o que não devia. Pede a **Semente do Ancião** (`elder_seed`) |
| **A limpeza** | `fd_clear` — *Limpar o Matagal* (Lenhador Ardo) | Ardo corta, e o mato **volta falando** |
| **O morador** | `fd_fang` — *A Presa da Víbora Anciã* (Herbalista Mirta) | Entrega o **Herbário da Ervanária** (`dark_forest_book_1`). Pede a **Presa da Víbora Anciã** (`viper_fang`) e paga com a **chave de musgo** |
| **O morador** | `fd_crown` — *A Coroa de Esporos* (Encantador Zhar) | Entrega o **Cancioneiro do Encantador** (`dark_forest_book_2`). Pede a **Coroa de Esporos** (`spore_crown`) e paga com a **chave de espinho** |
| **O altar único** | Altar do Pântano (`fd_totem`) | O Herbário desperta a **Víbora Anciã**; o Cancioneiro, o **Rei dos Esporos** |
| **O portão** | `fd_gate` — *O Portão do Ancião* (Guardião da Mata) | Duas chaves |
| **O cobrador** | **Ancião Sombrio** (`fd_elder`) | Guarda a **Semente**, e debaixo dela o **portão para o Inferno** |

**Preço.** Odete recebe a semente e **a planta no lugar do próprio coração**. Ela **vira árvore** em minutos, no meio da Casa de Equipamentos, **sem quebrar o telhado**. As outras árvores da floresta **inclinam-se** na direção da fazenda, uma por uma.

**Imagem que fica.** O Ancião Sombrio ruindo, e **do tronco oco, uma escada de ossos descendo para o escuro**.

---

## 7. Ato Final — O Livro das Dívidas

> **Estado do jogo:** o mapa do **Inferno** e o chefe **Lúcifer** ainda não existem (`06`, seção 2). Esta seção é o **roteiro** das cenas que levam até eles, com o mínimo a construir para fechar a campanha. Marcado como **proposta**.

### Cena 1 — O Bobo sumiu (Capital)
De volta à Capital, o **Bobo da Corte** não está: só a **máscara**, os **guizos** e as **anotações escondidas** nas dobras da cortina. O Bobo havia **ouvido o crânio**, **seguido o Sacristão** e **anotado tudo**: os doze contratos, as doze garantias, **e uma linha no fim da página**: *"A Companhia da Moeda Negra assinou. Falta cobrar."*

### Cena 2 — O Tabelião (Igreja)
O **Sacristão Ambrósio** espera os mercenários no altar da igreja, **sem a batina**. Ele é o **Tabelião**: o demônio que **redige os contratos**. Mostra as **garantias** reunidas (a coroa, o coração, os pulmões, o crânio, a alma, o elo, o olho, o cristal, o bastão, a semente, a foice, o mapa) e **as sentenças de cada NPC de cidade**: o Velho Bêbado, a Taberneira, o Capitão, o Veterano, o Padre, a Irmã, o Peregrino, o Fazendeiro, o Ferreiro, a Lenhadora **e o Cartógrafo**. Todos **quitados**.

Ele não ameaça. Explica, com **voz de funcionário**: o **corpo do último rei** está inteiro agora, **no jardim da igreja**, sob o canteiro onde o Padre enterrou o coração. A **Foice de Prata** serve para **ceifá-lo**: sem ela, o rei é só **um morto**; com ela, **é um recipiente**. Lúcifer vai **vestir** o rei e **andar** entre os vivos. E quem **entregou** cada peça, **quem trouxe o ouro** que pagou cada NPC, e **assinou o primeiro livro** na taverna de Tortuga, foi a Companhia da Moeda Negra.

### Cena 3 — A escolha (proposta)
O Tabelião **oferece o caminho mais barato**: **entregar a Foice** e **sair da dívida**, a companhia inteira **livre e rica**. Ou levar a Foice **até o Inferno**, para **cobrar o credor** antes que ele cobre.

Os mercenários **não são bondosos**: escolhem a segunda porque **o Bobo sabe onde há mais ouro**. É a única motivação que **combina com a história**: **ganância contra o dono da ganância**.

### Cena 4 — A escada de ossos
O **Viajante do Tempo**, calado em todo o jogo, aparece uma última vez no jardim da igreja e **abre a escada de ossos** da Floresta Escura. Diz uma frase só: ***"Já foi assim antes."*** *(Gancho da Campanha 2: o Viajante é quem **reinicia** a história, e a Companhia **já assinou** outras vezes.)*

### Cena 5 — O Inferno (a construir)
**Mapa 12, Inferno**: estrutura dos outros mapas (altar, livros, guardião), mas **cada NPC é um dos doze devedores do jogo, agora como alma presa**, cada um **cobrando o preço** que os mercenários cobraram. Lúcifer espera sentado em uma **mesa de contador**, com **o Bobo na outra cadeira**, escrevendo. Pede que os mercenários **sentem**.

**Combate em três fases (`06`, seção 2):** Terra → Água → todos os elementos; o terceiro movimento é **a leitura do contrato em voz alta**: **cada linha** que ele lê **chama** um dos doze cobradores do jogo.

**Tesouro.** O **maior tesouro do mundo**: todo o ouro que Lúcifer acumulou. Ao abri-lo, **o ouro se desfaz em cinzas** nas mãos dos mercenários, **menos uma moeda**, que fica **preta**. Eles **dividem as cinzas**; cada um fica com **a moeda de si**, e todos **continuam devendo**.

### Epílogo — o Bobo (fala final)
Libertado, o Bobo **tira a máscara** e **diz o que ouviu**: o reino do **primo** do nosso rei. Ainda maior. Ainda mais rico. E **muito mais bem guardado**. *"Interessados?"* (`06`, seção 4, Ato 4.) A câmera mostra a **moeda negra** de cada herói **mais quente** que a outra.

### Epílogos por herói
| Herói | Cena curta |
|---|---|
| **Mago** | Compra o grimório que procurava; as páginas estão escritas com **a letra do Tabelião** |
| **Arqueiro** | Reconstrói a casa em Veldmark; no pátio, **uma cova com o próprio nome** (do pai, que a guerra levou) |
| **Dorian** | Volta à Capital rico e **ninguém o reconhece** (a Dália do outro lado da mesa o encara **sem lembrar dele**) |
| **Dália** | Recupera o luxo; a **primeira refeição** é servida com **Carne Selvagem** |
| **Ren / Rin** | Faz o maior roubo da vida: **a própria alma de volta**; mas a moeda está **trocada** |
| **Invocador** | Os animais órfãos **ganham um lar**; o pássaro do ombro **fala um nome** que ele **não conhece** |

---

## 8. Mestre de missões (todas, na ordem)

| # | Mapa | Missão | Quem pede | O que pede | O que dá | O que a cena mostra |
|---|---|---|---|---|---|---|
| 1 | Esgoto | `sewer_treasure` | Velho Bêbado | Garrafa da Tempestade de Almas | Ouro | Família engarrafada; o velho adormece |
| 2 | Esgoto | `sewer_frog_king` | Ossael | Garrafa do Tormento Eterno | Chave de copas | Anjo despojado, livro das preces |
| 3 | Esgoto | `sewer_old_gator` | Azazel | Garrafa das Almas Condenadas | Chave de espadas | Cobrador cansado, grimório das brasas |
| 4 | Floresta | `forest_treasure` | Taberneira | Costela de Adão | Ouro | A costela vira parte dela |
| 5 | Floresta | `forest_leshy` | Exploradora | Adaga de Osso | Chave de espadas | Perdida nas raízes |
| 6 | Floresta | `forest_fire_golem` | Aelindra | Caveira de Morvak | Chave de copas | Queima os mortos que voltam |
| 7 | Floresta | `forest_gate` | Guardião do Portão | As duas chaves | Abre o portão | — |
| 8 | Docas | `docks_smugglers` | Capitão Pirata | Diário do Capitão Afogado | Ouro | Lê a lista e se joga ao mar |
| 9 | Docas | `dock_helm` | Mestre do Porto | Leme do Casco Vivo | Chave da âncora | O casco respira |
| 10 | Docas | `dock_tooth` | Peixeira | Dente de Ouro do Tubarão | Chave da bússola | O molho que não se come |
| 11 | Docas | `dock_gate` | Vigia do Cais | As duas chaves | Abre o portão | — |
| 12 | Ruínas | `map_ruins` | Veterano de Guerra | Coroa do Rei Caído | Ouro | Perde a idade de uma vez |
| 13 | Ruínas | `royal_banquet` | Bobo da Corte | Carne Selvagem | Ouro | O rei vencedor come o reino derrotado |
| 14 | Ruínas | `ruins_goblins` | Leônidas | Limpar os goblins | Ouro | Nenhum sobrevivente |
| 15 | Ruínas | `ruins_seal` | Erudita | Coração de Pedra | Chave do leão | Códice |
| 16 | Ruínas | `ruins_banner` | Sacerdotisa | Estandarte do Campeão | Chave da águia | Prece |
| 17 | Ruínas | `ruins_gate` | Porteiro | As duas chaves | Abre o portão | — |
| 18 | Taverna → Capital | `trav_to_capital` | Cartógrafo Aldrin | Mapa Selado | Ouro | O sorriso quieto do Sacristão |
| 19 | Cemitério | `royal_heart` | Padre | Coração Humano | Ouro | O coração que bate no caixão pequeno |
| 20 | Cemitério | `ce_lungs` | Coveiro Abel | Pulmões Humanos | Chave do Ossuário | Mortos pedindo mais terra |
| 21 | Cemitério | `ce_lantern` | Zeladora Mirta | Lamparina do Sentinela | Chave da Cripta | Luz para os mortos |
| 22 | Cemitério | `ce_gate` | Guardião da Cripta | As duas chaves | Abre o portão | — |
| 23 | Forte | `royal_skull` | Padre | Crânio Antigo | Ouro | O crânio diz *Ambrósio* |
| 24 | Forte | `fort_purge` | Sargento | Limpar os quartéis | Ouro | O sargento já morreu |
| 25 | Forte | `fort_sigil` | O Exilado | Lâmina do Senhor Elfo | Chave de ônix | Pacto |
| 26 | Forte | `fort_ring` | A Penitente | Anel da Rainha | Chave de rubi | Rosário |
| 27 | Forte | `fort_gate` | Carcereiro do Forte | As duas chaves | Abre o portão | — |
| 28 | Catacumbas | `map_catacombs` | Irmã Isolda | Elo do Rei Acorrentado | Ouro | Ajoelhada, sem pulso |
| 29 | Catacumbas | `ct_purge` | Frade | Limpar as celas | Ouro | Sempre uma cela a mais |
| 30 | Catacumbas | `ct_axe` | Carcereiro Cego | Machado do Carrasco | Chave de ferro | Cego por escolha |
| 31 | Catacumbas | `ct_soul` | Prisioneira | Grilhão da Alma | Chave de osso | Esqueceu o crime |
| 32 | Catacumbas | `ct_gate` | Diretor | As duas chaves | Abre o portão | — |
| 33 | Deserto | `map_desert` | Peregrino Haled | Olho da Esfinge | Ouro | Dois companheiros mortos |
| 34 | Deserto | `desert_horn` | Nômade | Chifre do Lamassu | Chave de paus | Água de cor nenhuma |
| 35 | Deserto | `desert_scarab` | Guardiã do Oásis | Escaravelho de Ouro | Chave de ouros | Água com dentes |
| 36 | Deserto | `desert_gate` | Sentinela | As duas chaves | Abre o portão | — |
| 37 | Capital → Fazenda | `cap_to_farm` | Sacristão Ambrósio | Foice de Prata | Ouro | A foice não enferruja |
| 38 | Mina | `map_mine` | Fazendeiro Tadeu | Coração de Cristal | Ouro | O espantalho dá um passo |
| 39 | Mina | `royal_soul` | Padre | Alma do Rei | Ouro | A pedra chora |
| 40 | Mina | `mn_clear` | Aprendiz | Limpar as galerias | Ouro | Conta menos colegas |
| 41 | Mina | `mn_tusk` | Capataz Brokk | Presa do Chefe Troll | Chave de picareta | Mapa das galerias |
| 42 | Mina | `mn_quartz` | Joalheiro Dolgrim | Núcleo de Quartzo | Chave de lanterna | Catálogo |
| 43 | Mina | `mn_gate` | Guarda-Chaves Thrain | As duas chaves | Abre o portão | — |
| 44 | Bunker | `map_bunker` | Ferreiro Gorm | Bastão do General | Ouro | A bigorna sangra |
| 45 | Bunker | `bk_clear` | Sargento | Limpar a entrada | Ouro | Morreu duas vezes |
| 46 | Bunker | `bk_seal` | Intendente Vorn | Selo do Arsenal | Chave de latão | Números que não fecham |
| 47 | Bunker | `bk_medal` | Médica Lena | Medalha do Comandante | Chave de aço | Prontuário |
| 48 | Bunker | `bk_gate` | Sentinela | As duas chaves | Abre o portão | — |
| 49 | Floresta Escura | `map_dark_forest` | Lenhadora Odete | Semente do Ancião | Ouro | Vira árvore sem quebrar o telhado |
| 50 | Floresta Escura | `fd_clear` | Lenhador Ardo | Limpar o matagal | Ouro | O mato volta falando |
| 51 | Floresta Escura | `fd_fang` | Herbalista Mirta | Presa da Víbora Anciã | Chave de musgo | Herbário |
| 52 | Floresta Escura | `fd_crown` | Encantador Zhar | Coroa de Esporos | Chave de espinho | Cancioneiro |
| 53 | Floresta Escura | `fd_gate` | Guardião da Mata | As duas chaves | Abre o portão | — |

> Nas missões de morador, **o livro** vem junto do aceite; **o livro some** quando o mini-chefe cai (`prototype_arena._consume_books`).

---

## 9. Peças do Rei Faminto, onde estão

| Peça | Onde | Missão | Quem a leva |
|---|---|---|---|
| Coroa | Ruínas (Rei Caído) | `map_ruins` | Veterano de Guerra |
| Carne do banquete | Ruínas (Alfa da Matilha) | `royal_banquet` | Bobo da Corte → rei de Aurenval |
| Coração | Cemitério (Senhor da Cripta) | `royal_heart` | Padre (jardim da igreja) |
| Pulmões | Cemitério (Ogro da Cripta) | `ce_lungs` | Coveiro Abel (**proposta:** reenterra em covas rasas) |
| Crânio | Forte (Barão Infernal) | `royal_skull` | Padre (cofre) |
| Elo da corrente | Catacumbas (Rei Acorrentado) | `map_catacombs` | Irmã Isolda (no pescoço) |
| Olho | Deserto (Esfinge) | `map_desert` | Peregrino Haled |
| Alma | Mina (Guardião do Túmulo) | `royal_soul` | Padre |
| Coração de cristal | Mina (Golem de Cristal) | `map_mine` | Fazendeiro Tadeu (espantalho) |
| Bastão | Bunker (General Ferrugem) | `map_bunker` | Ferreiro Gorm (bigorna) |
| Semente | Floresta Escura (Ancião) | `map_dark_forest` | Lenhadora Odete (árvore) |
| Mapa Selado | Capital (Sacristão) | `trav_to_capital` | Cartógrafo Aldrin → grupo |
| Foice de Prata | Fazenda (Velho Zeca) | `cap_to_farm` | Sacristão Ambrósio → grupo |

---

## 10. O que falta escrever e perguntas em aberto

- **Falas** (pt/en/es): as cenas de **preço** (a volta de cada missão de cidade) ainda não existem como falas; hoje as missões de cidade terminam só com o pagamento. Sugestão técnica: uma fala por NPC com `quest_done` e, onde há mudança visual, `after_quest` (como o Cartógrafo).
- **Atos finais**: Cenas 1 a 4 do Ato Final (Capital, Igreja, escada de ossos) e o **Inferno** (mapa 12 e Lúcifer) estão só no roteiro.
- **O Viajante do Tempo**: é o gancho da Campanha 2; confirmar se fica como proposta.
- **O Sacristão é o Tabelião** (proposta nova). Alternativa: o Padre ser o traidor; fica mais trágico, mas contradiz o tom "sincero e errado".
- **Quem é o pai de Dália** e **o que o Arqueiro encontra em casa** (seção 10 de `06`) continuam em aberto.
- **O Bobo**: confirmar se escutou o crânio (Forte) ou apenas desconfia.
