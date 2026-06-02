# vigia-docencia

Bot de Telegram + dashboard para alertas de **empleo docente** (secundaria
Geografía e Historia / ELE) en Madrid. Repo **fino** que consume el núcleo
compartido [`vigia-core`](https://github.com/tragabytes/vigia-core) y aporta
solo lo específico de su perfil.

Sustituye al prototipo `alerta-empleo-profe` (un *fork* monolítico del
pipeline): aquí el core se comparte por `pip` y solo viven el `Profile` docente
y la fuente BOCM propia.

## Alcance del perfil (informe.md)
- **Incluye**: Cuerpo 0590 PES esp. **005 Geografía e Historia**, Cuerpo 0592
  EOI / **ELE**, bolsas e interinidades, concursos de traslados, **lectorados**
  (AECID/MEFP/Fulbright/Cervantes), colegios privados/concertados del noroeste.
- **Excluye** a propósito: primaria (Cuerpo 0597), universidad/PDI general
  (solo universidad en contexto ELE), roles 100% en inglés.

## Arquitectura
```
vigia-core (pip)  →  Profile docente (vigia_docencia/profile.py)
sources: boe (del core, parametrizado) + bocm (custom RSS, vigia_docencia/sources/bocm.py)
pipeline: fetch → extract → enrich (opcional) → notify (Telegram) → dashboard
```

El entrypoint fija el perfil antes de importar el pipeline:
```bash
python -m vigia_docencia            # run completo (necesita TELEGRAM_BOT_TOKEN + CHAT_ID)
python -m vigia_docencia --dry-run  # sin notificar ni persistir
python -m vigia_docencia --probe    # salud de las fuentes
```

## Tests / validación offline
```bash
# Con vigia-core instalado por pip:
python -m pytest tests
# En local sin instalar (apuntando al core del repo hermano):
PYTHONPATH=../alerta-empleo python -m pytest tests
```

## Variables de entorno
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (obligatorias en CI), `ANTHROPIC_API_KEY`
(activa el enricher), `DASHBOARD_URL`, `VIGIA_STATE_DIR` (ruta del `state/`).
