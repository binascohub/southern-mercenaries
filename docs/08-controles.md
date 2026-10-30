# Controles

> Versão 1 · 2026-10-30 · Teclado/mouse e controle (gamepad) USB no PC Linux.
> Pontos marcados como **proposta** são sugestões para revisar.

## 1. Requisitos

- O jogo funciona com **teclado + mouse** e com **controle USB** conectado ao PC.
- O jogador pode **configurar (remapear) os botões** do controle e do teclado num menu de opções.
- **Conectar/desconectar a quente:** plugar o controle durante o jogo deve funcionar sem reiniciar. Se o controle desconectar no meio da partida, o jogo **pausa** (no solo) ou mostra aviso (no co-op) até reconectar.
- A interface troca os **ícones dos botões** automaticamente conforme o último dispositivo usado (teclado ou controle).
- Toda a interface (menus, inventário, lojas, diálogos, árvore de habilidades) deve ser **navegável só com o controle**.

## 2. Implementação (Godot 4)

- Usar o **Input Map** do Godot com **ações** (nunca teclas fixas no código). Cada ação tem um evento de teclado/mouse e um de controle.
- Godot usa o banco **SDL GameControllerDB**: controles Xbox, PlayStation (DualShock 4/DualSense), 8BitDo e genéricos USB já vêm mapeados no Linux.
- Remapeamento salvo em `user://controles.cfg` (ConfigFile), carregado ao iniciar. Botão "Restaurar padrão".
- Sinal `Input.joy_connection_changed` para detectar conexão/desconexão.
- **Zona morta** dos analógicos configurável (padrão 0,2).
- Vibração (`Input.start_joy_vibration`) ao levar dano forte e ao derrotar chefe, com opção para desligar.
- **Um controle por PC:** como o co-op é em LAN (cada jogador no seu PC), não há tela dividida; cada PC usa um teclado ou um controle.

## 3. Ações e mapeamento padrão

| Ação (ID) | Teclado + mouse | Controle (padrão Xbox) |
|---|---|---|
| `move` | W A S D | Analógico esquerdo |
| `aim` | Posição do mouse | Analógico direito (se solto: mira na direção do movimento) |
| `attack` | Botão esquerdo | RT |
| `skill_1` | Q | A |
| `skill_2` | E | B |
| `skill_3` | R | X |
| `skill_4` (habilidade final) | F | Y |
| `evade` (esquiva / teleporte do Ninja) | Espaço | LT |
| `mount` (Cavaleiro monta/desmonta) | Shift | L3 |
| `potion_health` | 1 | Direcional ↓ |
| `potion_mana` | 2 | Direcional ↑ |
| `potion_elemental` | 3 | Direcional → |
| `interact` (falar, abrir baú, pegar item) | Botão direito ou G | A (quando há algo perto; senão `skill_1`) — **proposta**: RB dedicado |
| `pickup_all` | Z | RB |
| `inventory` | I | Select / View |
| `menu` (pausa no solo) | Esc | Start / Menu |
| `map` | M | Direcional ← |
| `chat_quick` (frases rápidas do co-op) | T | R3 |

- **Mira com controle:** ataques à distância usam **mira assistida** leve (puxa para o inimigo mais próximo no cone da mira). Proposta: assistência de 15°, ajustável/desligável.
- No controle, as habilidades podem ser trocadas de botão pela árvore de habilidades.

## 4. Menu de opções de controle

- Lista de ações com o botão atual; selecionar e apertar o novo botão para trocar.
- Avisar se o botão já está em uso (trocar entre as duas ações).
- Sensibilidade do analógico de mira, zona morta, inverter eixo Y, vibração liga/desliga, mira assistida liga/desliga.
- Teste de controle (mostra os botões apertados).

## 5. Decisões em aberto

- Interagir: usar botão dedicado (RB) ou o mesmo das habilidades quando há algo perto?
- Chat rápido no co-op: quais frases (ex.: "Aqui!", "Preciso de cura", "Cuidado!")?
- Ícones: mostrar estilo Xbox ou PlayStation conforme o controle detectado?
