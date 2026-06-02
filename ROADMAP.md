# Roadmap — vigia-docencia

**Estado: MVP (Sprint 1) en producción.** Vigila **BOE + BOCM** → oposiciones e
interinidad oficial de secundaria (Cuerpo 0590, especialidad 005 Geografía e
Historia) + ELE/EOI (0592). Según el informe de perfil, esto cubre el grueso del
empleo público docente.

Lo que sigue es **expansión de fuentes**, incremental: **1 fuente por PR**.
Heredado del roadmap del bot original `alerta-empleo-profe` (archivado), ahora
sobre la arquitectura limpia. Patrón: cada fuente nueva = una clase `Source` en
`vigia_docencia/sources/`, registrada en `extra_sources` del perfil (igual que
[`bocm.py`](vigia_docencia/sources/bocm.py)); las genéricas (boletines de otras
CCAA) van **al core** (`vigia-core`).

## Alta prioridad — privado + ELE (lo que más amplía el radar de tu hermano)
- **Colegios privados/concertados del noroeste** (ATS): Inspired (`jobs.inspirededu.com`),
  SEK (Teamtailor), Brains (Factorial), Colegios RC / Highlands (SAP SuccessFactors,
  pausa 4-6 s entre requests). → categoría `privada`.
- **Portales ELE**: Instituto Cervantes (sede + `hispanismo.cervantes.es`),
  ProfesoresdeELE (RSS WordPress), TodoELE (HTML), Universidad Nebrija (la más
  activa en ELE). → categoría `ele`.

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

---
> Detalle histórico completo (sprints 1-9 con cadencias L1-L4): en `plan_profe.md`
> del repo archivado `tragabytes/alerta-empleo-profe` (read-only, consultable).
> Plan maestro de la plataforma: `PLAN_MAESTRO.md` en `vigia-enfermeria`/`alerta-empleo`.
