"""
Punto de entrada del bot docente: `python -m vigia_docencia`.

Modelo "un perfil por proceso": el extractor y el enricher del core compilan sus
patrones/enums en import-time leyendo `get_active_profile()`. Por eso fijamos el
perfil docente ANTES de importar el pipeline (`vigia.main`), con import diferido
dentro de `main()`.

Acepta los mismos flags que el core (se leen de sys.argv en `vigia.main.main`):
    python -m vigia_docencia                  # run completo
    python -m vigia_docencia --dry-run        # sin persistir ni notificar
    python -m vigia_docencia --since 2026-04-01
    python -m vigia_docencia --probe          # salud de las fuentes
"""
from __future__ import annotations

from vigia.profile import set_active_profile
from vigia_docencia.profile import PERFIL_DOCENCIA

# 1) Fijar el perfil ANTES de tocar el pipeline.
set_active_profile(PERFIL_DOCENCIA)


def main() -> None:
    # 2) Import diferido: al importarse aquí, vigia.main (y con él extractor,
    #    enricher, notifier y SOURCE_REGISTRY) se enlaza contra el perfil docente.
    from vigia.main import main as _core_main
    _core_main()


if __name__ == "__main__":
    main()
