# CLAUDE.md — vigia-docencia

Bot **fino** de la plataforma vigia para empleo **docente** (secundaria Geografía e
Historia / ELE). Consume el núcleo `vigia-core` por pip y aporta solo su perfil y sus
fuentes propias.

> **Reglas generales (obligatorias):** Karpathy Guidelines + convenciones del pipeline
> + guía "cómo crear un bot" viven en el **CLAUDE.md maestro** de vigia-core:
> <https://github.com/tragabytes/vigia-core/blob/main/CLAUDE.md>. Este documento solo
> recoge lo **específico de docencia**. Roadmap de fuentes futuras: [`ROADMAP.md`](ROADMAP.md).

---

## Lo esencial de este repo

- **Consume `vigia-core@v0.4.0`** (`requirements.txt`). El pipeline
  (fetch→extract→enrich→notify→dashboard) **no vive aquí**: vive en el core.
- **Entrypoint:** `python -m vigia_docencia` (`vigia_docencia/__main__.py`). Fija el
  perfil docente con `set_active_profile(PERFIL_DOCENCIA)` **antes** de importar el
  pipeline (import diferido); el core compila patrones/enums en import-time. Flags del
  core: `--dry-run`, `--probe`, `--since YYYY-MM-DD`.
- **Perfil** (`vigia_docencia/profile.py`): Cuerpo **0590 / esp. 005 Geografía e
  Historia** + **0592 EOI / ELE**, bolsas/interinidades, traslados, lectorados.
  **Excluye a propósito** primaria (0597), PDI/universidad general (solo universidad en
  contexto ELE) y roles 100% en inglés. Alcance fijado por `informe.md`; al tocar
  keywords/patrones, respétalo.
- **Fuentes:** `boe` (del core, **parametrizado** por `source_params`) + `bocm`
  (**custom** RSS en `vigia_docencia/sources/bocm.py`, registrada en
  `extra_sources` — sobrescribe el BOCM del core) + `profesoresdeele` (feed RSS
  de ofertas ELE, `vigia_docencia/sources/profesoresdeele.py`, categoría `ele`;
  usa el `text` desde los tags del feed, no el excerpt — ver su docstring).

## Dónde va cada fuente nueva (ROADMAP)

- **Genérica** (boletín de otra CCAA, portal multi-perfil) → **al core** (`vigia-core`),
  no aquí: beneficia a todos los bots.
- **De perfil docente** (ELE, colegios privados, canales sindicales) → **aquí**, como
  clase `Source` en `vigia_docencia/sources/` registrada en `extra_sources`. Patrón:
  igual que `bocm.py`. **1 fuente por PR.**

## Convenciones del pipeline (resumen; detalle en el maestro)

Aplican igual que en cualquier bot; aquí con las rutas de este repo:

- **El estado vive en GitHub**, no en disco: rama **`state`** (`seen.db`) y **`gh-pages`**
  (dashboard, <https://tragabytes.github.io/vigia-docencia/>). `VIGIA_STATE_DIR` apunta
  al `state/` local. Diagnóstico: `git show origin/gh-pages:data/items.json`.
- **Verifica el daño real** antes de arreglar: busca el `id_hash` en `items.json`; un
  WARNING en logs ≠ BD contaminada.
- **Segmenta backfills:** `--since` amplio revienta el runner; `--dry-run` no acorta el
  fetch. Rangos mensuales.
- **Fuentes hermanas:** a medida que el ROADMAP añada fuentes, los patrones (timeouts,
  fast-keywords, FALSE_POSITIVE_PATTERNS) se replicarán; un fix en una suele tocar a las
  gemelas (regla 8 del maestro).
- **Probe ≠ runtime:** lee los `WARNING`/`errores` del workflow, no solo
  `conclusion: success`.

## Tocar el core desde aquí

El código del core **no se edita en este repo**. Si necesitas cambiar el core (p.ej.
parametrizar más una fuente compartida): hazlo en `vigia-core`, publica un **tag nuevo**,
y **bumpea** la línea `vigia-core @ …@vX.Y.Z` de `requirements.txt`. Verifica el CI.

## Tests

```bash
python -m pytest tests                              # con vigia-core instalado por pip
PYTHONPATH=../vigia-core python -m pytest tests     # en local apuntando al core hermano
```

## Secrets / entorno (CI)

`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (obligatorias), `ANTHROPIC_API_KEY` (activa el
enricher), `DASHBOARD_URL`, `VIGIA_STATE_DIR`. Gotchas de entorno (Python 3.9, Windows
`PYTHONIOENCODING=utf-8`, `pytest --capture=no`): ver maestro.
