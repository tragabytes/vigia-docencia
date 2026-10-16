"""
Fuente Colejobs (spec 001, catálogo n.º 2). Offline, con un fixture recortado
del listado real del 16/10/2026.

Fallos que impiden:
- ofertas de fuera de la Comunidad de Madrid colándose (ámbito de Laureano);
- pérdida silenciosa si la web cambia (probe con conteo);
- avalancha el primer día (fecha absoluta → filtro de la ventana).
"""
from datetime import date
from unittest.mock import MagicMock, patch

from vigia.extractor import extract
from vigia_docencia.sources import colejobs
from vigia_docencia.sources.colejobs import ColejobsSource, _parse_fecha


def _art(href, titulo, colegio, fecha, meta):
    return f"""
<article><a href="{href}" title="{titulo}"><header><div>
  <h3>{titulo}</h3><h4>{colegio}</h4></div></header>
  <footer><p><span class="ico-calendar"></span> {fecha}</p>
  <p class="meta"><span class="ico-pin"></span> {meta}</p></footer></a></article>"""


_LISTADO = ("<section class='ofertas-empleo'>"
    + _art("ofertas-de-empleo/profesor-de-lengua-castellana-valores-y-geografia-e-historia-n45967/",
           "Profesor de Lengua Castellana, Valores y Geografía e Historia",
           "Colegio concertado", "8 octubre de 2026", "Madrid <em>|</em> Completa <em>|</em> Indefinido")
    + _art("ofertas-de-empleo/profesor-geografia-e-historia-zaragoza-n1/",
           "Profesor de Lengua y Geografía e Historia", "Colegio de Zaragoza",
           "9 octubre de 2026", "Zaragoza <em>|</em> Completa")
    + _art("ofertas-de-empleo/early-years-assistant-n4635/",
           "EARLY YEARS ASSISTANT (COVER SICK LEAVE)", "Colegio Laude Fontenebro",
           "16 octubre de 2026", "Moralzarzal, Madrid <em>|</em> Completa <em>|</em> Sustitución")
    + _art("ofertas-de-empleo/conserje-escuela-infantil-n3/",
           "CONSERJE ESCUELA INFANTIL", "Escuela Infantil", "14 octubre de 2026",
           "Rivas-Vaciamadrid, Madrid <em>|</em> Completa")
    + _art("ofertas-de-empleo/profesor-secundaria-religion-n4/",
           "PROFESOR DE SECUNDARIA DE RELIGIÓN Y FILOSOFÍA", "Arenales", "14 octubre de 2026",
           "Arroyomolinos, Madrid <em>|</em> Completa")
    + _art("ofertas-de-empleo/profesor-historia-antigua-n2/",
           "Profesor de Historia ESO", "Colegio X", "3 septiembre de 2026",
           "Boadilla del Monte, Madrid <em>|</em> Parcial")
    + "</section>").encode("utf-8")


def _parse(since=None):
    return ColejobsSource()._parse(_LISTADO, since)


def test_solo_comunidad_de_madrid():
    lugares = {i.extra["lugar"] for i in _parse()}
    assert "Zaragoza" not in lugares
    assert {"Madrid", "Boadilla del Monte, Madrid"} == lugares


def test_solo_materias_del_perfil():
    """Fallo que impide (16/10/2026, simulación con la web real): el patrón
    «profesor de secundaria» del perfil, pensado para el BOE, dejaba pasar
    conserjes y profesores de Religión, Lengua o Alemán de los colegios."""
    titulos = [i.title for i in _parse()]
    assert "CONSERJE ESCUELA INFANTIL" not in titulos
    assert "PROFESOR DE SECUNDARIA DE RELIGIÓN Y FILOSOFÍA" not in titulos
    assert "EARLY YEARS ASSISTANT (COVER SICK LEAVE)" not in titulos


def test_campos_y_url_absoluta():
    it = next(i for i in _parse() if "Valores" in i.title)
    assert it.url == ("https://www.colejobs.es/ofertas-de-empleo/"
                      "profesor-de-lengua-castellana-valores-y-geografia-e-historia-n45967/")
    assert it.date == date(2026, 10, 8)
    assert it.extra["colegio"] == "Colegio concertado"


def test_ventana_de_fechas():
    titulos = [i.title for i in _parse(since=date(2026, 10, 1))]
    assert "Profesor de Historia ESO" not in titulos   # 03/09


def test_todo_lo_que_emite_pasa_el_extractor():
    items = _parse()
    assert items and all(extract(i) is not None for i in items)


def test_fecha_en_castellano():
    assert _parse_fecha("16 octubre de 2026") == date(2026, 10, 16)
    assert _parse_fecha("3 de septiembre de 2026") == date(2026, 9, 3)
    assert _parse_fecha("sin fecha") is None


def test_paginador_que_repite_la_primera_pagina_no_duplica():
    resp = MagicMock(content=_LISTADO)
    resp.raise_for_status = lambda: None
    with patch.object(colejobs.requests, "get", return_value=resp) as get:
        items = ColejobsSource().fetch(since_date=date(2026, 10, 1))
    assert get.call_count == 2          # la 2.ª repite la 1.ª → para
    assert [i.title for i in items] == [
        "Profesor de Lengua Castellana, Valores y Geografía e Historia"]


def test_probe_da_cero_si_cambia_la_estructura():
    resp = MagicMock(status_code=200, text="<html><body>rediseño</body></html>")
    resp.raise_for_status = lambda: None
    with patch("vigia.sources.base.requests.get", return_value=resp):
        assert ColejobsSource().probe_content_count() == 0
