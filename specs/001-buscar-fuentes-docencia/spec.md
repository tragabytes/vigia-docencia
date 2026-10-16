# Especificación: encontrar nuevas fuentes de empleo docente

**Carpeta**: `specs/001-buscar-fuentes-docencia/` · **Fecha**: 2026-10-16 · **Estado**: H1-H3 hechas (16/10/2026); H4 pendiente

**Lo que se pidió** (Laureano, 16/10/2026): «elabora un plan a fondo para encontrar nuevas fuentes de docencia».

## De dónde partimos

- **Lo que vigila hoy el bot**: BOE, BOCM y ProfesoresdeELE.
- **Lo que ha encontrado** (26/04 a 14/10/2026): 316 items, de los que el enricher considera relevantes **35** (unos 6 al mes). De ProfesoresdeELE, la única fuente de empleo privado, han llegado **6**. Ni un aviso en las dos últimas semanas.
- **El mercado del perfil** tiene tres partes: la pública (oposiciones e interinidades de Geografía e Historia en Madrid), la privada (colegios de la Comunidad de Madrid y puestos online) y la de ELE (academias, universidades, lectorados, en cualquier lugar). La pública está cubierta por BOE y BOCM; **la privada y la de ELE casi no se ven**.
- **Ya hay un mapa**: el informe del bot anterior (`alerta-empleo-profe/informe.md`, abril de 2026) lista unas 60 fuentes con su web, su plataforma y una prioridad. Pero **nadie lo ha comprobado**: es de hace seis meses, y en este proyecto ya hemos visto webs que cambian (UAH), que bloquean (ePreselec) o que no tienen lo que se esperaba (URJC).

Este plan no construye nada todavía: decide **qué fuentes valen la pena, con pruebas**, y en qué orden se construyen.

## Historias

### H1 — Saber cuánto se está perdiendo (P1) · lo primero

Antes de añadir fuentes, medir el hueco con ofertas de verdad. Se buscan a mano (en los portales del sector, los colegios y las bolsas ELE) **las ofertas reales de las últimas 4 semanas que encajan en el perfil**, se anota dónde se publicó cada una, y se cruza con lo que el bot cazó.

**Por qué es la primera**: dice qué fuentes importan de verdad (dónde salen las ofertas que interesan) y da el número con el que comparar al final. Sin esto, añadiríamos fuentes por intuición.

**Cómo se comprueba sola**: una tabla de ofertas reales con su fuente y un porcentaje: «el bot vio X de N».

**Criterios de aceptación**:
1. **Dado** el perfil, **cuando** termine la búsqueda, **entonces** hay al menos 20 ofertas reales de las últimas 4 semanas, separadas en pública, privada y ELE, cada una con dónde apareció primero y si el bot la vio.
2. **Dado** que una oferta aparece en varios sitios, **entonces** se anotan todos: eso dice qué fuente cubre más.

---

### H2 — Catálogo comprobado de candidatas (P1)

Cada fuente del informe, más las que salgan de H1, se comprueba **hoy, contra la web real**, con estas preguntas:

- ¿Responde y se puede leer sin navegador, sin cuenta y sin esquivar bloqueos?
- ¿Cuántas ofertas que encajan en el perfil tiene hoy y en el último mes?
- ¿Cada oferta tiene enlace propio estable y fecha? (Si no, se repetirían avisos.)
- ¿Repite lo que ya trae otra fuente? (Un agregador puede cubrir a cinco colegios.)
- ¿Qué cuesta mantenerla? (Una tabla HTML sencilla frente a una web que cambia cada mes.)

Cada candidata acaba con un **veredicto**: *construir*, *no merece la pena* (con el porqué), *imposible sin cuenta o navegador*, o *solo recordatorio* (lo que no se puede vigilar, pero el usuario debe saber que existe: PADI, Talento ECM, la bolsa de FSIE, lectorados con fecha fija).

**Criterios de aceptación**:
1. **Dado** el catálogo, **entonces** cada candidata tiene veredicto, prueba (fecha y lo que se vio) y, si es *construir*, un valor estimado (ofertas útiles al mes) y un coste (pequeño/medio/grande).
2. **Dado** una web que bloquea, **entonces** se apunta como bloqueada y se sigue: **no se esquiva**.

---

### H3 — Construir las mejores, de una en una (P2)

Con H1 y H2, un orden de construcción por *valor / coste*. Se construye una fuente por PR, en ese orden, y cada una se comprueba antes de publicarla:

- contra la web real, viendo qué ofertas habría avisado;
- con una copia de la base real del bot: el primer día **no puede llegar una avalancha** de ofertas viejas a Telegram (como se midió para la ventana de 3 días).

**Criterios de aceptación**:
1. **Dado** una fuente nueva, **cuando** se publica, **entonces** el primer daily manda como mucho los avisos de las ofertas de los últimos 3 días y ninguna repetida.
2. **Dado** que la web cambia y la fuente deja de leer, **entonces** el probe del dashboard lo marca en error (no «0 ofertas» en silencio).

---

### H4 — Lo que no se puede vigilar (P3)

Las fuentes con veredicto *solo recordatorio* se convierten en avisos por fecha o en una lista para el usuario: lectorados (AECID en enero, Fulbright en septiembre, auxiliares de conversación), registro en Talento ECM o en la bolsa de FSIE, PADI. Se decide qué forma darles cuando H2 diga cuántas son.

---

## Casos raros

- **La web bloquea o pide «no eres un robot»**: se apunta como bloqueada. Nunca se esquiva.
- **Hace falta cuenta o clave** (InfoJobs, Jooble, leer canales de Telegram): Claude no crea cuentas. Se apunta qué clave hace falta y cómo sacarla; Laureano o su hermano la sacan (respuesta del 16/10).
- **La oferta está en inglés o es de un colegio bilingüe con el puesto entero en inglés**: fuera del perfil.
- **La misma oferta en un agregador y en la web del colegio**: el bot avisaría dos veces. El catálogo dice cuál de las dos fuentes se queda.
- **Ofertas sin fecha**: la fecha caería a «hoy» y se repetirían cada día. Una fuente así solo vale si tiene enlace estable que evite el duplicado.
- **No aparece ninguna oferta del perfil en 4 semanas** en una fuente: no se construye, aunque el informe la diera por prioritaria.

## Requisitos

- **R-001**: Toda fuente candidata DEBE comprobarse contra la web real y con fecha, no por lo que diga el informe.
- **R-002**: Claude NUNCA DEBE esquivar un bloqueo, resolver un captcha, crear una cuenta ni registrarse en un portal.
- **R-003**: Una fuente nueva NUNCA DEBE publicarse sin la prueba con la copia de la base real (sin avalancha, sin repetidas).
- **R-004**: Cada fuente nueva DEBE avisar en el probe cuando deje de leer (no puede dar 0 en silencio).
- **R-005**: Los errores de las fuentes NUNCA DEBEN llegar al Telegram del usuario: se ven en logs y dashboard.

## Qué invariantes toca

| Invariante | Dónde está escrito | ¿Puede romperse en silencio? |
|---|---|---|
| El alcance del perfil (0590/005 y 0592-006; privado en la Comunidad de Madrid y online, también puestos mixtos de materias o con parte en inglés, desde el 16/10; ELE en cualquier sitio; sin primaria, sin universidad general, sin puestos enteramente en inglés) no se cambia sin preguntar | `CLAUDE.md` de docencia, regla 1 | Sí: una fuente nueva con ofertas fuera de alcance llenaría el dashboard sin que nadie lo note. Test por fuente: ofertas reales fuera de alcance no pasan el extractor |
| Fuente genérica al núcleo; de perfil docente, a este repo; una fuente por PR | `CLAUDE.md` de docencia, regla 2 | No |
| Probe ≠ runtime: una fuente puede responder 200 y no leer nada | núcleo, regla 5 | **Sí, el más peligroso**: un cambio en la web deja la fuente en 0 para siempre (pasó con la UAH cuatro semanas). Test por fuente: el probe cuenta elementos y da error si son 0 |
| Los errores de fuente no van al Telegram | núcleo, `historico/incidents` de enfermería | No (se vería) |
| El bot recuerda lo visto y no repite avisos | núcleo (deduplicación) | Sí, si una fuente no tiene enlace estable o la fecha cae a «hoy». Test por fuente: dos lecturas seguidas no producen avisos nuevos |

## Criterios de éxito

- **E-001**: Cobertura medida en H1: «el bot vio X de N ofertas reales del perfil en 4 semanas», antes y después de H3.
- **E-002**: Catálogo con veredicto para todas las fuentes del informe (unas 60) más las nuevas que salgan de H1.
- **E-003**: Tras H3, los avisos relevantes al mes pasan de ~6 a un número que se fijará con los datos de H1, sin que suba el ruido (medido con el porcentaje de items que el enricher descarta).

## Respuestas de Laureano (16/10/2026)

- **Zona del privado: toda la Comunidad de Madrid y también online** (academias y plataformas que dan clase en remoto). Amplía el alcance del perfil, que antes decía «colegios privados, solo Madrid» sin incluir lo online: al construir H3 se actualiza la regla 1 del `CLAUDE.md` de docencia.
- **InfoJobs, Jooble y canales de Telegram, sí**: se evalúan como el resto, y para cada una se explica qué clave o cuenta hace falta y cómo sacarla. Laureano o su hermano la sacan; Claude no crea cuentas.
- **El perfil sigue igual que en abril**: Historia con máster, ELE, inglés C1, sin puestos bilingües.

**Validación de H1 (Laureano, 16/10/2026):**
- **Ofertas que mezclan materias** (Economía + Historia, Lengua + Historia): **valen**.
- **Colegios con parte de las clases en inglés**: **valen**. Se interpreta que los puestos **enteramente** en inglés (p. ej. Geography en currículo británico) siguen fuera, como decía el perfil.
- **ELE en el extranjero**: **todas valen**, incluidas universidades y colegios de EE. UU., Reino Unido o Emiratos.

## Supuestos

- **Las noticias sindicales** (bolsas extraordinarias, acuerdos de mesa) solo entran si traen una convocatoria concreta, no como noticias sueltas.
- **La búsqueda a mano de H1** la hace Claude en las webs públicas, sin preguntar al hermano.
- **Online** quiere decir puestos de profesor en remoto con contrato o pago por la academia (Lingoda, academias ELE online). Los **marketplaces donde uno se anuncia como tutor** (italki, Preply, Superprof) no son ofertas: van a *solo recordatorio*.
