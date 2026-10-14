# Relevo — vigia-docencia

Para arrancar una sesión: lee primero el `RELEVO.md` de vigia-core (estado común) y luego esto.

**Estado (14/10/2026).** En producción con vigia-core **v0.8.4**. Vigila BOE y BOCM (oposiciones e interinidades de secundaria, 0590/005 y 0592) y ProfesoresdeELE (ofertas ELE). Dailies en verde del 1 al 14/10; el enricher descartó como falsos positivos entre 2 y 8 items algunos días, y no salió ningún aviso nuevo.

## Fuentes que faltan

Sacadas de `historico/ROADMAP.md` (que venía del bot anterior, `alerta-empleo-profe`, archivado). Ninguna está hecha a 14/10/2026.

### Alta prioridad: privado y ELE
- **Colegios privados y concertados del noroeste** → categoría `privada`. Cada uno con su plataforma: Inspired (`jobs.inspirededu.com`), SEK (Teamtailor), Brains (Factorial), Colegios RC / Highlands (SAP SuccessFactors; pausa de 4-6 s entre peticiones). *Grande.*
- **Portales ELE** → categoría `ele`: Instituto Cervantes (sede y `hispanismo.cervantes.es`), TodoELE (HTML), Universidad Nebrija (la más activa en ELE). *Medio.*

### Media prioridad: tiempo real y agregadores
- **Canales sindicales de Telegram** (Telethon, o la versión web `t.me/s/{canal}`): `@ANPEmadrid`, `@csifeducacionmadrid`, `@ugteducacionpublicamadrid`, `@educacion_ccoomadrid`, `@noticiasoposicionessecundaria`, `@bolsasdocentes`, `@opobusca`. Dan horas de ventaja. *Medio.*
- **InfoJobs y Jooble por API** (claves gratuitas; Jooble agrega InfoJobs, Indeed y LinkedIn). Filtro Madrid; búsquedas `profesor historia`, `profesor secundaria`, `profesor español extranjeros`. *Medio.*

### Baja prioridad
- **LinkedIn** (API de invitado, con calma) e **Indeed** (RSS no oficial, frágil). *Medio.*
- **Revisión semanal** de ayuntamientos del noroeste y universidades (UCM, UC3M, Comillas, CEU, URJC, UCJC, UFV, UEM). *Medio.*
- **Alertas de calendario**, sin web que leer: Fulbright FLTA y Auxiliares MEFP (septiembre), AECID lectorados y Profesores Visitantes (enero), oposiciones EOI Madrid (marzo-abril), becas Cervantes (mayo-julio). *Pequeño.*
- **Recordatorios manuales** de webs que no se pueden automatizar: Talento ECM, FSIE, italki, Preply, Superprof, Lingoda. *Pequeño, quizá fuera del bot.*

Secrets que harán falta: `INFOJOBS_CLIENT_ID`, `INFOJOBS_CLIENT_SECRET`, `JOOBLE_API_KEY`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`.

### Mantenimiento
- **Acciones de GitHub con Node 20** (`checkout@v4`, `setup-python@v5`): GitHub ya las ejecuta con Node 24 y funcionan, pero avisa. Ver núcleo, `DECISIONES.md` D17.
