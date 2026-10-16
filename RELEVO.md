# Relevo — vigia-docencia

Para arrancar una sesión: lee primero el `RELEVO.md` de vigia-core (estado común) y luego esto.

**Estado (16/10/2026).** En producción con vigia-core **v0.15.0** (mira 3 días hacia atrás). Además de BOE, BOCM y ProfesoresdeELE, desde el 16/10 lee **10 fuentes nuevas** (spec 001): TodoELE, Colejobs, Colegios.es, Novedades de RRHH de la Comunidad, Colegios RC e Inspired (SuccessFactors), CEU e ISP (Workday), SEK (Teamtailor), TES e Instituto Cervantes. El alcance del perfil se amplió el 16/10 (regla 1 del `CLAUDE.md`). Detalle y medidas en [`specs/001-buscar-fuentes-docencia/`](specs/001-buscar-fuentes-docencia/).

## Por comprobar
1. **Primer daily real con las fuentes nuevas (lunes 19/10)**: las 12 fuentes con `0 errores`; el probe de todas en `ok`; avisos del orden de lo simulado (13 el primer día antes del enricher, luego unos 3-5 al día, sobre todo ELE en el extranjero). Cómo mirarlo: `MANTENIMIENTO.md` §3 del núcleo.
2. **Que el enricher no descarte lo que vale**: en el dashboard, las ofertas de TodoELE, TES y colegios deberían salir como relevantes salvo las que exijan algo imposible (p. ej. universidad con plaza titular). Si descarta muchas, revisar el prompt (`_ENRICHER_SYSTEM_PROMPT`).

## Pendientes
- **Decidir (Laureano): InfoJobs por su API oficial.** Es donde publican muchos colegios (p. ej. Gredos San Diego); la web bloquea. Hace falta que alguien saque una clave en developer.infojobs.net y sus condiciones prohíben guardar sus datos (el bot guardaría solo título y enlace): zona gris. Detalle en `specs/001-buscar-fuentes-docencia/catalogo.md`.
- **Decidir (Laureano): H4 de la spec 001**, lo que no se puede vigilar: recordatorio de Fulbright (no sale en el BOE; abre a mediados de septiembre), PADI, Talento ECM, bolsa de FSIE. La lista de Español en EOI (0592-006) de Madrid está abierta permanentemente.
- **Revisar el uso de la API de Anthropic** (modelo del enricher, coste, orquestación) frente a lo que hay hoy (pedido por Laureano el 16/10).
- **15 items de finales de septiembre sin enriquecer** (el límite de gasto de la API se agotó del 22 al 29/09; Laureano lo ha subido). Docencia no tiene workflow de mantenimiento que los reintente.
- **Hueco que queda: ELE en Madrid y online.** Las academias pequeñas de Madrid (Aware, Expanish…) y las ofertas online solo aparecían en agregadores (Jobsora, Jooble) o LinkedIn, descartados por anti-robots, falta de clave o condiciones de uso.
- **TES solo da las 20 más recientes** (la paginación por URL no funciona). Si un día hay más, se perderían; vigilar el volumen.
- **Descartadas en el catálogo** (no volver a mirarlas sin motivo nuevo): sindicatos (van detrás de la Consejería), Nebrija, International House, Lingoda, FORMESPA, Jobsora/Jobijoba/Edutalent, Indeed, Empléate, Fomento, Talento ECM, colegios sin listado. Jooble y LinkedIn, fuera por decisión del 16/10.

Histórico del ROADMAP original en [`historico/ROADMAP.md`](historico/ROADMAP.md).
