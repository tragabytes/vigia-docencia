"""
Fuente Novedades de RRHH de Educación de la Comunidad de Madrid (spec 001,
catálogo n.º 4). Offline, con entradas reales del 16/10/2026.

Fallos que impiden:
- perder la segunda y siguientes publicaciones de un listado semanal que repite
  título y enlace (dedup por url+título): la fecha va en el título;
- ruido de catedráticos de Música, maestros, PAS…;
- pérdida silenciosa si la página cambia (probe con conteo).
"""
from datetime import date
from unittest.mock import MagicMock, patch

from vigia.extractor import extract
from vigia_docencia.sources.novedades_rrhh import NovedadesRRHHSource

_P = '<p>{f}<br><a href="{h}"><strong>{t}</strong></a></p>'
_PAGINA = ("<div class='text-editor--content'>" + "".join(_P.format(f=f, h=h, t=t) for f, h, t in [
    ("06/10/2026", "/educacion/listas-extraordinarias#admision-determinadas-especialidades",
     "Listas extraordinarias de interinos permanentemente abiertas. Listas de nuevos aspirantes admitidos y no admitidos en determinadas especialidades."),
    ("29/09/2026", "/educacion/listas-extraordinarias#admision-determinadas-especialidades",
     "Listas extraordinarias de interinos permanentemente abiertas. Listas de nuevos aspirantes admitidos y no admitidos en determinadas especialidades."),
    ("14/10/2026", "/educacion/listas-extraordinarias-catedraticos-musica-artes-escenicas#admision",
     "Listas extraordinarias de interinos permanentemente abiertas en especialidades del Cuerpo de Catedráticos de Música y Artes Escénicas."),
    ("15/10/2026", "/educacion/listas-interinos-docentes-2026-2027#maestros",
     "Formación de las listas de aspirantes a desempeñar puestos docentes en régimen de interinidad durante el curso 2026-2027."),
    ("13/10/2026", "https://www.bocm.es/boletin/CM_Orden_BOCM/2026/10/13/BOCM-20261013-31.PDF",
     "Procedimiento selectivo para ingreso y accesos a los Cuerpos de Profesores de Secundaria, FP y RE. Emplazamiento."),
    ("16/10/2026", "/educacion/asesores-formacion-2026#admision",
     "Concurso de méritos para puestos de Asesor de Formación. Listados provisionales de admitidos."),
]) + "</div>").encode("utf-8")


def _parse(since=None):
    return NovedadesRRHHSource()._parse(_PAGINA, since)


def test_el_mismo_listado_en_dos_semanas_son_dos_novedades():
    listados = [i for i in _parse() if "nuevos aspirantes" in i.title]
    assert len(listados) == 2
    assert len({(i.url, i.title) for i in listados}) == 2
    assert {i.date for i in listados} == {date(2026, 10, 6), date(2026, 9, 29)}


def test_fuera_musica_maestros_y_asesores():
    titulos = " ".join(i.title for i in _parse())
    assert "Catedráticos de Música" not in titulos
    assert "Asesor de Formación" not in titulos
    assert "2026-2027" not in titulos          # la de #maestros


def test_entran_secundaria_y_listas_y_pasan_el_extractor():
    items = _parse()
    assert any("Profesores de Secundaria" in i.title for i in items)
    assert items and all(extract(i) is not None for i in items)


def test_url_absoluta_y_ventana():
    items = _parse(since=date(2026, 10, 1))
    assert all(i.date >= date(2026, 10, 1) for i in items)
    assert all(i.url.startswith("https://") for i in items)


def test_probe_da_cero_si_cambia_la_estructura():
    resp = MagicMock(status_code=200, text="<html><body><main>rediseño</main></body></html>")
    resp.raise_for_status = lambda: None
    with patch("vigia.sources.base.requests.get", return_value=resp):
        assert NovedadesRRHHSource().probe_content_count() == 0
