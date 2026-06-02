"""Fija el perfil docente ANTES de que se importe el pipeline del core.

`conftest.py` se ejecuta al arrancar pytest, antes de recolectar los módulos de
test. Como el extractor y el enricher del core compilan sus patrones/enums en
import-time leyendo `get_active_profile()`, fijar aquí PERFIL_DOCENCIA garantiza
que los tests se ejecuten contra el perfil docente y no contra el default
(enfermería).

Para la validación offline local (sin `pip install vigia-core`), añade el repo
del core al PYTHONPATH al invocar:
    PYTHONPATH=../vigia-core python -m pytest tests
En CI, vigia-core está pip-instalado y el PYTHONPATH no hace falta.
"""
from vigia.profile import set_active_profile
from vigia_docencia.profile import PERFIL_DOCENCIA

set_active_profile(PERFIL_DOCENCIA)
