# Sistema de Elementos

> Versión 3 · 2026-10-30 · Rige para **todas las clases** (`02-personagens.md`) y **todos los monstruos** (`03-inimigos.md`)
> Este archivo es la fuente oficial de elementos, ciclo de debilidades, cambio de elemento, estados, combos y de la regla de composición de las habilidades.

## 1. Regla general

- Todo personaje elige **un elemento al crearse**: **Agua, Fuego, Aire o Tierra**. Es el **elemento de origen** y no cambia.
- El elemento **cambia las habilidades**, el efecto de los ataques y el aspecto visual de los efectos.
- El jugador puede **cambiar de elemento temporalmente** con una **Poción Elemental** comprada en el Mercado de Tortuga (sección 4).
- **Todo monstruo también tiene un elemento** y es **débil a otro** (sección 3).
- El sexo y la apariencia no afectan nada del juego; **clase + elemento** definen al personaje.

## 2. Los cuatro elementos

| ID | Elemento | Identidad | Punto fuerte | Punto débil | Colores |
|---|---|---|---|---|---|
| `fire` | Fuego | Daño máximo | Daño en área y con el tiempo | Poco control | Naranja y rojo |
| `water` | Agua | Control y apoyo | Ralentización, congelación, curación leve | Daño más bajo | Azul y blanco |
| `air` | Aire | Velocidad y rayos | Ataques rápidos, empujones, daño en cadena | Poca defensa | Blanco y violeta |
| `earth` | Tierra | Defensa y aturdimiento | Aturde, barreras, protección | Más lento | Verde y marrón |

## 3. Ciclo de debilidades

```
Agua ──vence──▶ Fuego ──vence──▶ Tierra ──vence──▶ Aire ──vence──▶ Agua
```

| Elemento del monstruo | **Débil a** (+50% de daño) | Resiste (-50% de daño) | Por qué |
|---|---|---|---|
| Fuego | **Agua** | Fuego | El agua apaga el fuego |
| Tierra | **Fuego** | Tierra | El fuego derrite la piedra y quema el bosque |
| Aire | **Tierra** | Aire | La tierra atrapa y derriba lo que vuela |
| Agua | **Aire** | Agua | Los rayos corren por el agua |

- Los ataques del **mismo elemento** del monstruo causan **-50%** de daño; los del elemento **fuerte contra él**, **+50%**; los otros dos, daño normal.
- Rige para todo el daño del jugador (ataques básicos, habilidades, esbirros del Invocador).
- Los estados de control (`frozen`, `stunned`…) funcionan con normalidad; solo cambia el daño.

### Cómo descubre el jugador la debilidad
1. **En la historia:** quien cuenta la misión en la taberna **siempre habla del elemento del monstruo/demonio y de lo que lo vence** (p. ej. "el fuego de ese Pegaso solo se apaga con agua"). Ver `04-tortuga-e-missoes.md`.
2. **En el bestiario:** el Bardo registra el elemento y la debilidad de cada monstruo.
3. **En el mapa:** cada monstruo muestra un **icono de su elemento** junto a la barra de vida; el número de daño aparece **más grande y coloreado** cuando acierta la debilidad, y **gris y más pequeño** cuando el monstruo resiste.

## 4. Cambio de elemento — Poción Elemental

| Objeto | Valor |
|---|---|
| ID | `elemental_potion_water`, `elemental_potion_fire`, `elemental_potion_air`, `elemental_potion_earth` |
| Dónde comprar | **Mercado de Tortuga** |
| Precio | Crece con el nivel del personaje (propuesta: 100 + 25 × nivel de oro) |
| Duración | **Una expedición**: desde que se bebe hasta volver a Tortuga |
| Límite | Una poción activa a la vez; beber otra cambia el efecto |

**Efecto al beber:**
- El personaje pasa a usar el **nuevo elemento**: ataques, estado básico y color de los efectos.
- Las **habilidades del elemento** se cambian por las equivalentes del nuevo elemento, **con los mismos rangos** (la habilidad de nivel 6 del elemento de origen pasa a ser la de nivel 6 del nuevo elemento, y así sucesivamente).
- Las habilidades de clase no cambian.
- Al volver a Tortuga, el personaje regresa a su **elemento de origen**.

**Por qué existe:** cada mapa tiene monstruos y un demonio de un elemento; las historias avisan de la debilidad, y el grupo se prepara comprando las pociones adecuadas antes de partir por el puerto.

## 5. Composición de las habilidades

### 5.1 Tipos de habilidad

Todo conjunto de habilidades de elemento debe tener los tres tipos:

| ID | Tipo | Regla | Rango de daño (rango 1) |
|---|---|---|---|
| `aoe` | Área | Alcanza a varios enemigos; **menos daño** por objetivo | 60% a 180% del poder (habilidad final: 500% a 600%) |
| `single` | Objetivo único | Alcanza a un enemigo; **más daño** | 280% a 350% del poder |
| `support` | Apoyo | Ayuda al grupo (curación, escudo, velocidad, bonificación de daño); poco o ningún daño | 0% a 50% del poder |

"Poder" = el atributo de daño de la clase (p. ej. el Poder Mágico del Mago).

### 5.2 División por clase

Cada clase tiene **10 habilidades**:

| Clase | Habilidades de clase (iguales para todos) | Habilidades del elemento |
|---|---|---|
| Mago | 4 | 6: básica (nivel 1), área (2), **apoyo (6)**, **objetivo único (10)**, área (14), área final (18) |
| Caballero, Arquero, Ninja, Invocador | 7 | 3: **apoyo (6)**, **objetivo único (12)**, **área final (18)** |

- **Habilidades de clase:** la mecánica es la misma en todos los elementos, pero el golpe queda **imbuido** del elemento actual: aplica el estado básico de este (sección 5.3) y cambia el color/efecto visual.
- **Habilidades del elemento:** exclusivas de la combinación clase + elemento.
- **Ataque fuerte:** aplica el estado básico del elemento.

### 5.3 Estado básico de cada elemento
| Elemento | Estado básico aplicado por golpes imbuidos y ataques fuertes |
|---|---|
| Fuego | `burning` |
| Agua | `soaked` |
| Aire | `shocked` |
| Tierra | 30% de probabilidad de `stunned` |

### 5.4 Apoyo por elemento (tema)
| Elemento | Tipo de apoyo |
|---|---|
| Fuego | Bonificación de daño para los aliados |
| Agua | Curación |
| Aire | Velocidad de movimiento y de ataque |
| Tierra | Escudo / reducción de daño |

## 6. Estados elementales

| ID | Estado | Origen | Efecto | Duración predeterminada |
|---|---|---|---|---|
| `burning` | Ardiendo | Fuego | Daño con el tiempo (predeterminado: 30% del daño del golpe por s) | 3 s |
| `soaked` | Mojado | Agua | -20% de velocidad de movimiento | 4 s |
| `frozen` | Congelado | Agua (fuerte) | No se mueve ni ataca; recibe crítico garantizado | 2 s |
| `shocked` | Electrizado | Aire | Recibe +15% de daño de Aire | 4 s |
| `knocked_down` | Derribado | Aire / Tierra | Caído, sin poder actuar | 1 s |
| `stunned` | Aturdido | Tierra | No actúa | 1,5 s |

- Los jefes nunca quedan **congelados**, **derribados** ni **aturdidos**: reciben un 50% de ralentización en su lugar.
- Reaplicar un estado renueva la duración, sin acumularse.
- Los monstruos de Fuego no pueden estar `burning`; los de Agua no pueden estar `soaked`.

## 7. Combos entre elementos (cooperativo)

Cualquier jugador puede completar el combo de otro, de cualquier clase. Ejemplo: el Arquero de Agua moja a los enemigos y el Ninja de Aire los electrocuta.

| Estado en el enemigo | + golpe de | Combo | Resultado |
|---|---|---|---|
| Mojado | Aire | **Electrocutar** | +50% de daño de Aire y aturde 1 s |
| Ardiendo | Aire | **Incendio** | El fuego se propaga a los enemigos cercanos (radio de 3 m) |
| Mojado | Tierra | **Barro** | Zona de barro que ralentiza a los enemigos un 40% durante 5 s |
| Ardiendo | Agua | **Vapor** | Nube que hace que los enemigos fallen el 30% de sus ataques durante 4 s |
| Aturdido | Fuego | **Fundir** | +30% de daño sobre el enemigo aturdido |

- Un combo **consume** el estado que lo inició.
- La bonificación por debilidad (sección 3) se suma al combo.

## 8. Visuales y rendimiento

- Cada elemento tiene su conjunto de efectos (color, partículas, sonido), reutilizado por todas las clases y monstruos.
- Partículas simples y en poca cantidad (requisito para funcionar con vídeo integrado).
- El arma de cada clase brilla con el color del elemento actual (cristal del bastón, punta de la lanza, flechas, hojas de las dagas, páginas del libro); cambia al instante al beber una Poción Elemental.

## 9. Decisiones abiertas

- ¿Los objetos con bonificación de elemento (p. ej. "+10% de daño de Fuego") sirven para cualquier clase?
- ¿Precio de la Poción Elemental (propuesta: 100 + 25 × nivel)?
