# Roadmap — vigia-docencia

**Estado: MVP + 1ª ampliación, en producción.** Vigila **BOE + BOCM** →
oposiciones e interinidad oficial de secundaria (Cuerpo 0590, especialidad 005
Geografía e Historia) + ELE/EOI (0592), y **ProfesoresdeELE** → ofertas ELE
(categoría `ele`). Según el informe de perfil, esto cubre el grueso del empleo
público docente.

Lo que sigue es **expansión de fuentes**, incremental: **1 fuente por PR**.
Heredado del roadmap del bot original `alerta-empleo-profe` (archivado), ahora
sobre la arquitectura limpia. Patrón: cada fuente nueva = una clase `Source` en
`vigia_docencia/sources/`, registrada en `extra_sources` del perfil (igual que
[`bocm.py`](vigia_docencia/sources/bocm.py)); las genéricas (boletines de otras
CCAA) van **al core** (`vigia-core`).

## Hecho
- ✅ **ProfesoresdeELE** (RSS WordPress) — feed de la categoría "Ofertas de
  trabajo" (`/category/ofertas-de-trabajo/feed/`), categoría `ele`. El `text`
  para el matching se compone de los **tags** del feed (no del excerpt), para no
  disparar los FALSE_POSITIVE_PATTERNS del perfil pensados para boletines (p.ej.
  "educación infantil", frecuente en colegios internacionales con ELE en el
  extranjero). `vigia_docencia/sources/profesoresdeele.py`.

## Alta prioridad — privado + ELE (lo que más amplía el radar de tu hermano)
- **Colegios privados/concertados del noroeste** (ATS): Inspired (`jobs.inspirededu.com`),
  SEK (Teamtailor), Brains (Factorial), Colegios RC / Highlands (SAP SuccessFactors,
  pausa 4-6 s entre requests). → categoría `privada`.
- **Portales ELE**: Instituto Cervantes (sede + `hispanismo.cervantes.es`),
  TodoELE (HTML), Universidad Nebrija (la más activa en ELE). → categoría `ele`.
  (ProfesoresdeELE ✅ hecho, ver arriba.)

## Media prioridad — tiempo real + agregadores
- **Canales sindicales de Telegram** (Telethon/MTProto, o fallback HTML `t.me/s/{canal}`):
  `@ANPEmadrid`, `@csifeducacionmadrid`, `@ugteducacionpublicamadrid`,
  `@educacion_ccoomadrid`, `@noticiasoposicionessecundaria`, `@bolsasdocentes`,
  `@opobusca`. Ventaja informativa de horas.
- **InfoJobs API** (`client_id`/`client_secret` gratis en developer.infojobs.net) +
  **Jooble API** (agrega InfoJobs+Indeed+LinkedIn). Filtro provincia Madrid;
  keywords `profesor historia`, `profesor secundaria`, `profesor español extranjeros`.

## Baja prioridad / cuando el resto madure
- **LinkedIn** (guest API, cadencia conservadora) + **Indeed** (RSS no oficial, frágil).
- **Polling semanal**: ayuntamientos noroeste + universidades (UCM, UC3M, Comillas,
  CEU, URJC, UCJC, UFV, UEM).
- **Alertas de calendario** (no hay web que scrapear; disparo por fecha):
  Fulbright FLTA y Auxiliares MEFP (septiembre), AECID lectorados y Profesores
  Visitantes (enero), oposiciones EOI Madrid (marzo-abril), becas Cervantes
  (mayo-julio).
- **Recordatorios manuales** (fuentes no automatizables): Talento ECM, FSIE,
  italki, Preply, Superprof, Lingoda.

## Variables de entorno que añadirán los sprints futuros
`INFOJOBS_CLIENT_ID`, `INFOJOBS_CLIENT_SECRET`, `JOOBLE_API_KEY`,
`TELEGRAM_API_ID`, `TELEGRAM_API_HASH` (Telethon).

## Mantenimiento
- **Deprecación de Node 20 (GitHub Actions).** `daily.yml`, `test-telegram.yml` y
  `ci.yml` usan `actions/checkout@v4` y `actions/setup-python@v5`, que corren sobre
  Node 20. GitHub fuerza Node 24 por defecto desde el **16-jun-2026** y retira Node 20
  el **16-sep-2026**. Antes de esa fecha: subir las versiones de las actions (o, como
  parche temporal, `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`). No urgente; afecta por
  igual a los tres workflows.

---
> Detalle histórico completo (sprints 1-9 con cadencias L1-L4): en `plan_profe.md`
> del repo archivado `tragabytes/alerta-empleo-profe` (read-only, consultable).
> Plan maestro de la plataforma: `PLAN_MAESTRO.md` en `vigia-enfermeria`/`alerta-empleo`.
