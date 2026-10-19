# Relevo — vigia-docencia

Para arrancar una sesión: lee primero el `RELEVO.md` de vigia-core (estado común) y luego esto.

**Estado (16/10/2026).** En producción con vigia-core **v0.16.0** (mira 3 días hacia atrás). Además de BOE, BOCM y ProfesoresdeELE, desde el 16/10 lee **10 fuentes nuevas** (spec 001): TodoELE, Colejobs, Colegios.es, Novedades de RRHH de la Comunidad, Colegios RC e Inspired (SuccessFactors), CEU e ISP (Workday), SEK (Teamtailor), TES e Instituto Cervantes. El alcance del perfil se amplió el 16/10 (regla 1 del `CLAUDE.md`). Detalle y medidas en [`specs/001-buscar-fuentes-docencia/`](specs/001-buscar-fuentes-docencia/).

## Por comprobar
1. **Primer daily real con las fuentes nuevas (lunes 19/10, run 39274370809)**: dos fuentes en error y la issue de salud #51 abierta. Lo demás (avisos del orden de lo simulado: 13 el primer día antes del enricher, luego unos 3-5 al día, sobre todo ELE en el extranjero) sigue por comprobar; cómo: `MANTENIMIENTO.md` §3 del núcleo.
   - **Workday: era el probe, no la lectura.** El probe miraba la raíz del dominio (`https://ceu.wd3.myworkdayjobs.com`), que Workday contesta con 406 a cualquiera, también desde local. La lectura usa la API y estaba bien (0 errores; desde local, también 0 ofertas del perfil esos días). Arreglado en el núcleo: [vigia-core#63](https://github.com/tragabytes/vigia-core/pull/63), sin fusionar. Tras fusionar: etiqueta `v0.16.2` y subir `requirements.txt` aquí; el probe debe salir `ok 200 …/COL`.
   - **Colejobs: bloquea los servidores de GitHub.** Desde local responde 200 con cualquier cabecera (también sin User-Agent); desde el runner, 403 de Cloudflare a la primera página, en la lectura y otra vez en el probe 17 min después. TodoELE, también detrás de Cloudflare, sí responde al runner. Las medidas del 16/10 se hicieron todas en local y el CI no sale a la red: el 19/10 fue la primera vez que se leyó desde GitHub. No se fuerza (nada de proxies ni de disfrazarse). **Lo decide Laureano**: ver Pendientes.
2. **Que el enricher no descarte lo que vale**: en el dashboard, las ofertas de TodoELE, TES y colegios deberían salir como relevantes salvo las que exijan algo imposible (p. ej. universidad con plaza titular). Si descarta muchas, revisar el prompt (`_ENRICHER_SYSTEM_PROMPT`).
3. **Prueba de Haiku 5.5 hasta el 30/10** (spec 002 del núcleo, D36-D38): el enricher usa Haiku 5.5 con Sonnet 4.6 de testigo y avisa si cualquiera de los dos dice SÍ. Cada lunes, buscar `Testigo:` en el log del daily. Se abandona si Haiku dice NO a algo que sí era para el perfil.

## Pendientes
- **Decidir (Laureano): Colejobs**, que no aporta nada desde GitHub (arriba, punto 1). Era la mejor fuente abierta de colegios de Madrid, pero el catálogo le calculaba solo 1-2 ofertas del perfil al mes. Dos opciones acotadas:
  - **A. Desactivarla** (recomendado): quitar `colejobs` de `sources_enabled` en el perfil, sin borrar la fuente ni sus tests. Se cierra la issue de salud. Se deshace volviendo a añadirla.
  - **B. Mantenerla una semana con criterio de abandono**: sigue activa hasta el **lunes 26/10**; si en ninguno de esos dailies sale `colejobs … 0 errores`, se desactiva como en A. Mientras tanto la issue de salud sigue abierta cada día por Colejobs. Solo tiene sentido si crees que el bloqueo puede ser pasajero; las señales dicen que no (403 inmediato, a la primera petición).
- **Decidir (Laureano): InfoJobs por su API oficial.** Es donde publican muchos colegios (p. ej. Gredos San Diego); la web bloquea. Hace falta que alguien saque una clave en developer.infojobs.net y sus condiciones prohíben guardar sus datos (el bot guardaría solo título y enlace): zona gris. Detalle en `specs/001-buscar-fuentes-docencia/catalogo.md`.
- **Decidir (Laureano): H4 de la spec 001**, lo que no se puede vigilar: recordatorio de Fulbright (no sale en el BOE; abre a mediados de septiembre), PADI, Talento ECM, bolsa de FSIE. La lista de Español en EOI (0592-006) de Madrid está abierta permanentemente.
- **Hueco que queda: ELE en Madrid y online.** Las academias pequeñas de Madrid (Aware, Expanish…) y las ofertas online solo aparecían en agregadores (Jobsora, Jooble) o LinkedIn, descartados por anti-robots, falta de clave o condiciones de uso.
- **TES solo da las 20 más recientes** (la paginación por URL no funciona). Si un día hay más, se perderían; vigilar el volumen.
- **Descartadas en el catálogo** (no volver a mirarlas sin motivo nuevo): sindicatos (van detrás de la Consejería), Nebrija, International House, Lingoda, FORMESPA, Jobsora/Jobijoba/Edutalent, Indeed, Empléate, Fomento, Talento ECM, colegios sin listado. Jooble y LinkedIn, fuera por decisión del 16/10.

Histórico del ROADMAP original en [`historico/ROADMAP.md`](historico/ROADMAP.md).
