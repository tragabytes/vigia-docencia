"""
Colegios CEU e ISP con el lector Workday del núcleo (spec 001, catálogo n.º 6).

Comprueba de punta a punta, con el perfil docente, que una oferta de Historia
de un colegio llega y pasa el extractor, que las de otras materias se quedan
en la fuente, y que la búsqueda de ISP trae «Spanish Teacher» de cualquier país.
"""
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from vigia.extractor import extract
from vigia.sources import workday
from vigia.sources.workday import WorkdaySource


def _resp(postings):
    r = MagicMock(status_code=200)
    r.json.return_value = {"total": len(postings), "jobPostings": postings}
    r.raise_for_status = lambda: None
    return r


def _o(title, path, lugar):
    return {"title": title, "postedOn": "Posted Today", "externalPath": path,
            "locationsText": lugar}


def test_historia_en_colegio_y_spanish_teacher_en_el_mundo():
    colegio = [
        _o("Profesor/a Business e Historia Curso 26-27", "/job/Aravaca/Historia_JR1",
           "Colegio Internacional Aravaca, Spain, Madrid"),
        _o("Profesor/a Francés ESO-BACH", "/job/Aravaca/Frances_JR2",
           "Colegio Internacional Aravaca, Spain, Madrid"),
    ]
    mundo = [_o("Spanish Teacher", "/job/Warsaw/Spanish_JR3",
                "Einstein Primary School, Poland, Warsaw")]

    def post(url, json=None, **kw):
        return _resp(mundo if json.get("searchText") == "Spanish" else colegio)

    with patch.object(workday.requests, "post", side_effect=post):
        items = WorkdaySource().fetch(since_date=date.today() - timedelta(days=3))

    titulos = [i.title for i in items]
    assert "Profesor/a Francés ESO-BACH" not in titulos
    assert "Profesor/a Business e Historia Curso 26-27" in titulos
    assert "Spanish Teacher" in titulos
    assert all(extract(i) is not None for i in items)
