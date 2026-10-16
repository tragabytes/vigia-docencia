"""
Fuente Instituto Cervantes (spec 001, catálogo n.º 10). Offline, con
títulos y fichas reales del 16/10/2026.

Fallos que impiden: avisar el primer día de convocatorias viejas que siguen
listadas (la fecha sale de la ficha); colar convocatorias internas para el
personal del Cervantes; pérdida silenciosa si cambia la página (probe).
"""
from datetime import date
from unittest.mock import MagicMock, patch

from vigia.extractor import extract
from vigia_docencia.sources import cervantes
from vigia_docencia.sources.cervantes import CervantesSource, _candidatas, _primera_fecha


def _link(i, t):
    return f'<dnt-link slot="title" to="/procedimiento/portada?idProc={i}">{t}</dnt-link>'


LISTADO = ("<div>" + "".join(_link(i, t) for i, t in [
    (100735, "Convocatoria pública de Profesores - Ref. CVA-PROF-PUB-01/24"),
    (133578, "Convocatoria pública de Profesores – Ref. CVA-PROF-PUB-01/26"),
    (133463, "Convocatoria restringida de Profesores – Ref. CVA-PROF-RES-01/25"),
    (134649, "Concurso de traslado de Profesores - Ref. CVA-PROF-TRAI-01/26"),
    (100692, "Reclamaciones"),
]) + "</div>").encode("utf-8")


def _ficha(fecha):
    return MagicMock(status_code=200, text=f"<html>Resumen del procedimiento [{fecha}] Bases [12/07/2026]</html>",
                     raise_for_status=lambda: None)


def test_solo_convocatorias_publicas_de_profesores():
    titulos = [t for t, _ in _candidatas(LISTADO)]
    assert titulos == [
        "Convocatoria pública de Profesores - Ref. CVA-PROF-PUB-01/24",
        "Convocatoria pública de Profesores – Ref. CVA-PROF-PUB-01/26",
    ]


def test_primera_fecha_es_la_de_publicacion():
    assert _primera_fecha("Resumen del procedimiento [06/02/2026] … [08/04/2026]") == date(2026, 2, 6)
    assert _primera_fecha("sin fechas") is None


def test_las_viejas_no_avisan_y_una_nueva_si():
    listado = MagicMock(status_code=200, content=LISTADO, raise_for_status=lambda: None)
    fechas = {"100735": "19/11/2024", "133578": "15/10/2026"}

    def get(url, **kw):
        if "idProc=" in url:
            return _ficha(fechas[url.split("idProc=")[1]])
        return listado

    with patch.object(cervantes.requests, "get", side_effect=get):
        items = CervantesSource().fetch(since_date=date(2026, 10, 13))
    assert [i.title for i in items] == ["Convocatoria pública de Profesores – Ref. CVA-PROF-PUB-01/26"]
    assert extract(items[0]) is not None


def test_probe_da_cero_si_cambia_la_estructura():
    resp = MagicMock(status_code=200, text="<html>rediseño</html>", raise_for_status=lambda: None)
    with patch("vigia.sources.base.requests.get", return_value=resp):
        assert CervantesSource().probe_content_count() == 0
