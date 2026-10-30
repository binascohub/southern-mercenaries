# Southern Mercenaries — Documentación

Documentación de diseño de **Southern Mercenaries**, un RPG de acción cooperativo en LAN, escrita para servir de base a la implementación (incluso por un asistente de IA como Claude). Juego de código abierto (GPL-3.0-or-later) para Windows y Linux, en inglés, español y portugués.

> Idiomas de esta documentación: portugués (`../`, la fuente), inglés (`en/`) y español (`es/`), con los mismos nombres de archivo. Ante la duda, el portugués es la fuente.

## Orden de lectura

| Archivo | Contenido |
|---|---|
| `01-escopo.md` | Visión general, cámara, mecánicas, multijugador LAN, tecnología, idiomas, contenido de la v1.0, fases |
| `02-personagens.md` | Visión general de las 5 clases, vestimenta/equipo visual, atributos, reglas generales |
| `02-0-elementos.md` | Elementos, ciclo de debilidades, Poción Elemental, estados, combos y composición de las habilidades |
| `02-1-mago.md` | Mago en detalle |
| `02-2-arqueiro.md` | Arquero en detalle |
| `02-3-cavaleiro.md` | Caballero en detalle (Dorian y Dália) |
| `02-4-ninja.md` | Ninja en detalle (Ren y Rin) |
| `02-5-invocador.md` | Invocador en detalle |
| `03-inimigos.md` | Los 10 mapas, familias de monstruos (mecánica y elemento), élites, minijefes, jefes y Lucifer |
| `03-1-bestiario.md` | Leyendas reales de cada criatura y las pistas de debilidad que cuentan los NPC y el Bufón |
| `03-2-areas.md` | División de los 10 mapas en 41 áreas, niveles, puntos de control, minijefes |
| `04-tortuga-e-missoes.md` | Tortuga (primera ciudad base), taberna, Mercado Pirata, NPC y sistema de misiones |
| `04-1-capital-real.md` | Capital Real (segunda ciudad base, la ciudad del Caballero), comercio de más nivel, Bufón de la Corte |
| `05-itens-e-loot.md` | Categorías, materiales (tela/madera → oro), rarezas, tesoros, valiosos, mercados, inventario |
| `05-1-refino.md` | Refinado con pergaminos al estilo Lineage 2 (+1 a +5, seguro hasta +3, fallo y cristales) y el aura alrededor del héroe |
| `06-mundo-e-historia.md` | Premisa, la guerra, estructura de la campaña en actos, apertura, tesoros y motivos de los héroes |
| `07-rede.md` | Servidor autoritativo, descubrimiento en LAN, sincronización, botín individual, entrada y salida a mitad de partida |
| `08-controles.md` | Teclado/ratón y mando USB, asignación predeterminada, reasignación, opciones |
| `09-interface.md` | Dirección visual (estilo 0 A.D., cámara cercana como Dark Alliance), HUD, menús, pantallas y opciones |
| `14-tutorial.md` | Primeros minutos, consejos contextuales, equipo inicial y tutorial en las Alcantarillas |
| `13-balanceamento.md` | Fórmulas y tablas de daño, vida, armadura, XP, oro, precios y metas de equilibrio |
| `12-audio.md` | Banda sonora por mapa y jefe, efectos, ambiente, sonidos de interfaz, voces de los héroes y licencias de audio |
| `10-distribuicao.md` | Licencias de código abierto, repositorio, builds Windows/Linux, instaladores, GitHub Actions, sitio web |
| `15-modos.md` | Nueva partida desde cero, dificultades (Historia, Normal, Pesadilla) y expediciones, después de la v1.0 |
| `11-saves.md` | Guardados de personaje y de campaña, autoguardado, puntos de control, continuar en solitario y en cooperativo |

## Reglas para quien implemente

- **Motor:** Godot 4 (versión estable fijada), renderizador Compatibility (OpenGL 3.3), **GDScript**. El rendimiento en vídeo integrado es un requisito, no una optimización opcional.
- **Plataformas:** Windows y Linux con las mismas funciones; probar ambos y el cooperativo entre ellos.
- **Red:** servidor autoritativo; el modo solitario usa el mismo servidor ejecutándose en local. Los sorteos (botín, refinado) siempre en el servidor.
- **Controles:** soporte completo de mando USB desde la primera fase jugable; usar acciones del Input Map, nunca teclas fijas (`08-controles.md`).
- **Idiomas:** en, es y pt_BR. **Ningún texto fijo en el código, las escenas ni los datos** — siempre claves de traducción con `tr()`; la red y los guardados usan IDs, nunca texto traducido (`01-escopo.md`, sección 6). Los textos de esta documentación están en portugués (fuente) y también en inglés (`en/`) y español (`es/`); las traducciones del juego las hace Claude.
- **Equipo visible:** todo lo equipado aparece en el personaje, pieza por pieza, con su material; el refinado genera un aura alrededor del héroe (`05-itens-e-loot.md`, `05-1-refino.md`).
- **Guardados:** escritura segura con copias de seguridad y número de versión desde el primer guardado (`11-saves.md`).
- **Áreas:** cada área de mapa es una escena separada, con punto de control en la entrada (`03-2-areas.md`).
- **Código abierto:** solo assets propios (creados por Claude a partir de las referencias del autor, sin copiar ningún juego) o con licencia libre; registrar todo en `CREDITS.md` (`10-distribuicao.md`).
- **Datos separados del código:** clases, elementos, habilidades, objetos, materiales, pergaminos, refinado, monstruos, bestiario, NPC, tiendas, áreas y plantillas de misión viven en archivos de datos, usando los IDs definidos en los documentos (p. ej. `knight`, `fire`, `fireball`, `headless_mule`, `tavern_keeper`, `court_jester`, `sewers_01_drains`, `steel`).
- **Fuentes oficiales:** el archivo detallado de cada clase vale más que el resumen de `02-personagens.md`; `02-0-elementos.md` rige para todas las clases y monstruos; `03-1-bestiario.md` es la fuente de las líneas de historia y pistas; `06-mundo-e-historia.md` define el orden de la campaña (10 mapas); `05-itens-e-loot.md` define los materiales.
- **Campaña 2 (regla de diseño):** la continuación debe **siempre** empezar con los héroes **pobres de nuevo** (solo ropa interior, arma de madera, sin oro, sin refinado, nivel 1). La Campaña 1 no transfiere nada; la historia lo justifica (`06-mundo-e-historia.md`, sección 9).
- **Implementar por fases**, en el orden de `01-escopo.md` sección 9. Cada fase debe quedar jugable antes de la siguiente.
- Los puntos marcados como **abiertos** o **propuesta** no deben decidirse sin consultar al autor.

## Próximos documentos previstos

- Ninguno por ahora.
