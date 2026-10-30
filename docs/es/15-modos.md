# Modos de juego — Nueva partida, dificultades y expediciones

> Versión 1 · 2026-10-30 · Complementa `11-saves.md`, `13-balanceamento.md`, `03-inimigos.md` y `06-mundo-e-historia.md`
> **Todo el contenido es una propuesta** para que el autor la revise. Los puntos marcados como **abiertos** no deben decidirse sin consultar al autor.
> Alcance: **la v1.0 solo tiene el modo Normal.** Los modos siguientes llegan cuando el juego base esté completo (fase final de `01-escopo.md`).

## 1. Resumen

| Modo | Cuándo se desbloquea | Qué cambia |
|---|---|---|
| **Normal** | Desde el inicio | La campaña tal como fue diseñada (`13-balanceamento.md`) |
| **Nueva partida** | Siempre | Empieza **desde cero**: campaña nueva y personaje nuevo (**decidido**) |
| **Pesadilla** (dificultad) | Tras vencer a Lucifer una vez | Mayor escala de monstruos, más botín |
| **Expedición** (rejugar áreas) | Al vencer a Lucifer | Volver a cualquier área ya completada para farmear |

## 2. Una nueva partida empieza desde cero (decidido)

- **No existe Nueva Partida+.** Cada nueva partida crea una **campaña nueva** y un **personaje nuevo** (nivel 1, solo ropa interior y arma de madera, `02-personagens.md`), sin heredar nada.
- El personaje que venció a Lucifer sigue existiendo: puede continuar en la **Expedición** (sección 4) y en la continuación de la historia.
- Entre partidas solo persiste lo que pertenece al jugador, no al personaje: opciones, `tutorial_seen` (el tutorial no se repite, `14-tutorial.md`) y el desbloqueo de **Pesadilla** (sección 3).
- La historia sigue el mismo principio: la **Campaña 2** (futura, `06-mundo-e-historia.md`, sección 9) también empieza desde cero, y los héroes **lo pierden todo y vuelven a ser pobres**.
- Esto mantiene el equilibrio en una sola curva (`13-balanceamento.md`) y el nivel máximo en 20.

## 3. Dificultades

Se elige al crear la campaña:

| Dificultad | Vida de los monstruos | Daño de los monstruos | XP | Botín raro | Disponible |
|---|---|---|---|---|---|
| **Historia** | -30% | -30% | ×1,0 | ×1,0 | Siempre |
| **Normal** | base | base | ×1,0 | ×1,0 | Siempre |
| **Pesadilla** | +60% | +40% | ×1,3 | ×1,5 | En campañas nuevas, tras vencer a Lucifer una vez |

- La dificultad la elige el **anfitrión** al crear la campaña y **puede cambiarse en Tortuga**; los jugadores ven la elección al entrar.
- **Historia** sirve para jugar más por la historia con amigos novatos o niños.
- La muerte no tiene penalización extra en ninguna dificultad (rige la regla de `04-tortuga-e-missoes.md`).
- Los modificadores multiplican la escala del cooperativo.

## 4. Expedición (rejugar áreas)

- Tras vencer a Lucifer, el portal de la ciudad permite entrar en cualquier área **ya completada** con los monstruos **reaparecidos** (la exploración se rehace, `03-2-areas.md`).
- Los minijefes y jefes reaparecen **una vez por día real** (propuesta) para evitar el farmeo infinito.
- La recompensa sigue la dificultad de la campaña.
- El mapa revelado vuelve a "sin explorar" en esa expedición, sin borrar el progreso de la campaña.

## 5. Notas técnicas

- Guardar en el save de campaña: `difficulty` (`story`, `normal`, `nightmare`); en las opciones del jugador: `nightmare_unlocked`.
- Los modificadores viven en un archivo de datos (`data/modes.json`), nunca en el código.
- El servidor aplica los multiplicadores (autoritativo); el cliente solo los muestra.
- Aumentar la versión del formato de guardado (`save_version`) cuando entren estos campos (`11-saves.md`).
- Los textos de modos y dificultades usan claves de traducción (`tr()`).

## 6. Decisiones abiertas

- Los valores de la sección 3 salen de pruebas de equilibrio (`13-balanceamento.md`).
- ¿Pesadilla se desbloquea al vencer a Lucifer con cualquier personaje (propuesta) o solo con el personaje que lo venció?
