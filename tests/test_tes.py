"""
Fuente TES (spec 001, catálogo n.º 9). Offline, con el JSON de Next.js
recortado de la búsqueda real del 16/10/2026.

Fallos que impiden: que un cambio de la página (sin `__NEXT_DATA__`) dé 0
ofertas en silencio (probe a 0); ofertas de otras lenguas («Teacher of
French») colándose; avalancha el primer día (fecha de alta → ventana).
"""
import json
from datetime import date
from unittest.mock import MagicMock, patch

from vigia.extractor import extract
from vigia_docencia.sources import tes
from vigia_docencia.sources.tes import TesSource


def _job(i, title, start, employer="Mulberry School for Girls", loc="Tower Hamlets"):
    return {"id": i, "title": title, "canonicalUrl": f"/jobs/vacancy/x-{i}",
            "displayLocation": loc, "employer": {"name": employer},
            "advert": {"startDate": f"{start}T10:20:00.000Z"},
            "application": {"closeDate": "2026-11-03T00:00:00.000Z"}}


def _pagina(jobs):
    data = {"props": {"pageProps": {"initialData": {"jobs": jobs, "numFound": len(jobs)}}}}
    return f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script></html>'


HTML = _pagina([
    _job(2352581, "Spanish Teacher", "2026-10-15"),
    _job(2352600, "Teacher of French", "2026-10-15"),
    _job(2352000, "Teacher of Spanish (MFL)", "2026-09-20"),
])


def test_solo_espanol_con_fecha_de_alta_y_enlace():
    items = TesSource()._parse(HTML, None)
    assert [i.title for i in items] == ["Spanish Teacher", "Teacher of Spanish (MFL)"]
    assert items[0].date == date(2026, 10, 15)
    assert items[0].url == "https://www.tes.com/jobs/vacancy/x-2352581"
    assert items[0].extra["fecha_limite"] == "2026-11-03"


def test_ventana_y_extractor():
    items = TesSource()._parse(HTML, date(2026, 10, 13))
    assert [i.title for i in items] == ["Spanish Teacher"]
    assert extract(items[0]) is not None


def test_probe_da_cero_si_la_pagina_cambia():
    resp = MagicMock(status_code=200, text="<html>rediseño sin __NEXT_DATA__</html>")
    resp.raise_for_status = lambda: None
    with patch.object(tes.requests, "get", return_value=resp):
        assert TesSource().probe_content_count() == 0
