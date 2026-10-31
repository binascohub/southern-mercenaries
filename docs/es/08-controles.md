# Controles

> Versión 1 · 2026-10-30 · Teclado/ratón y mando (gamepad) USB en PC Linux.
> Los puntos marcados como **propuesta** son sugerencias para revisar.

## 1. Requisitos

- El juego funciona con **teclado + ratón** y con un **mando USB** conectado al PC.
- El jugador puede **configurar (reasignar) los botones** del mando y del teclado en un menú de opciones.
- **Conexión/desconexión en caliente:** enchufar el mando durante el juego debe funcionar sin reiniciar. Si el mando se desconecta en mitad de la partida, el juego **se pausa** (en solitario) o muestra un aviso (en cooperativo) hasta que se reconecte.
- La interfaz cambia automáticamente los **iconos de los botones** según el último dispositivo usado (teclado o mando).
- Toda la interfaz (menús, inventario, tiendas, diálogos, árbol de habilidades) debe poder **navegarse solo con el mando**.

## 2. Implementación (Godot 4)

- Usar el **Input Map** de Godot con **acciones** (nunca teclas fijas en el código). Cada acción tiene un evento de teclado/ratón y uno de mando.
- Godot usa la base **SDL GameControllerDB**: los mandos Xbox, PlayStation (DualShock 4/DualSense), 8BitDo y USB genéricos ya vienen mapeados en Linux.
- Reasignación guardada en `user://controles.cfg` (ConfigFile), cargada al iniciar. Botón "Restaurar valores predeterminados".
- Señal `Input.joy_connection_changed` para detectar conexión/desconexión.
- **Zona muerta** de los analógicos configurable (predeterminado 0,2).
- Vibración (`Input.start_joy_vibration`) al recibir daño fuerte y al derrotar a un jefe, con opción para desactivarla.
- **Un mando por PC:** como el cooperativo es en LAN (cada jugador en su PC), no hay pantalla dividida; cada PC usa un teclado o un mando.

## 3. Acciones y asignación predeterminada

| Acción (ID) | Teclado + ratón | Mando (predeterminado Xbox) |
|---|---|---|
| `move` | W A S D | Analógico izquierdo |
| `aim` | Posición del ratón | Analógico derecho (si está suelto: apunta en la dirección del movimiento) |
| `attack` | Botón izquierdo | RT |
| `skill_1` | 1 | A |
| `skill_2` | 2 | B |
| `skill_3` | 3 | X |
| `skill_4` (habilidad final) | 4 | Y |
| `evade` (esquiva / teletransporte del Ninja) | Espacio | LT |
| `mount` (el Caballero monta/desmonta) | Shift | L3 |
| `potion_health` | Q | Cruceta ↓ |
| `potion_mana` | E | Cruceta ↑ |
| `potion_elemental` | R | Cruceta → |
| `interact` (hablar, abrir cofre, recoger objeto) | Botón derecho o G | A (cuando hay algo cerca; si no, `skill_1`) — **propuesta**: RB dedicado |
| `pickup_all` | Z | RB |
| `inventory` | I | Select / View |
| `menu` (pausa en solitario) | Esc | Start / Menu |
| `map` | M | Cruceta ← |
| `chat_quick` (frases rápidas del cooperativo) | T | R3 |

- **Apuntado con mando:** los ataques a distancia usan una **asistencia de puntería** ligera (atrae hacia el enemigo más cercano dentro del cono de apuntado). Propuesta: asistencia de 15°, ajustable/desactivable.
- En el mando, las habilidades pueden cambiarse de botón desde el árbol de habilidades.

## 4. Menú de opciones de control

- Lista de acciones con el botón actual; seleccionar y pulsar el nuevo botón para cambiarlo.
- Avisar si el botón ya está en uso (intercambiar entre las dos acciones).
- Sensibilidad del analógico de puntería, zona muerta, invertir eje Y, vibración activada/desactivada, asistencia de puntería activada/desactivada.
- Prueba del mando (muestra los botones pulsados).

## 5. Decisiones abiertas

- Interactuar: ¿usar un botón dedicado (RB) o el mismo de las habilidades cuando hay algo cerca?
- Chat rápido en cooperativo: ¿qué frases (p. ej. "¡Aquí!", "Necesito curación", "¡Cuidado!")?
- Iconos: ¿mostrar estilo Xbox o PlayStation según el mando detectado?
