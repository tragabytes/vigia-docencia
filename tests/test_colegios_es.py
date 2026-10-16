"""
Fuente Colegios.es (spec 001, catálogo n.º 3). Offline, con un feed recortado
del real del 16/10/2026 (empieza con BOM, como el de verdad).

Fallos que impiden: ofertas de fuera de Madrid o de otras materias colándose;
un feed con BOM que no parsea (0 ofertas en silencio); perder ofertas los
lunes, cuando la ventana (5 días) es mayor que lo que guarda el feed.
"""
from datetime import date
from unittest.mock import MagicMock, patch

from vigia.extractor import extract
from vigia_docencia.sources import colegios_es
from vigia_docencia.sources.colegios_es import ColegiosEsSource


def _item(title, link, fecha, cats):
    c = "".join(f"<category><![CDATA[{x}]]></category>" for x in cats)
    return f"<item><title>{title}</title><link>{link}</link><pubDate>{fecha}</pubDate>{c}</item>"


def _feed(*items):
    return ("﻿<?xml version='1.0' encoding='UTF-8'?><rss><channel>"
            + "".join(items) + "</channel></rss>").encode("utf-8")


HISTORIA_MADRID = _item(
    "Se necesita profesor/a de geografía e historia con C1 de inglés para ESO y Bachillerato",
    "https://colegios.es/empleoprofesores/geografia-historia-13102026/",
    "Tue, 13 Oct 2026 10:00:00 +0000",
    ["Bachillerato", "Comunidad de Madrid", "Geografía", "Historia", "Secundaria", "Alcalá de Henares"])
MATES_MADRID = _item(
    "Se necesita profesor/a de matemáticas para ESO",
    "https://colegios.es/empleoprofesores/matematicas-13102026/",
    "Tue, 13 Oct 2026 09:00:00 +0000",
    ["Comunidad de Madrid", "Matemáticas", "Secundaria", "Madrid"])
HISTORIA_MALAGA = _item(
    "Se necesita profesor/a de historia para ESO",
    "https://colegios.es/empleoprofesores/historia-malaga-12102026/",
    "Mon, 12 Oct 2026 09:00:00 +0000",
    ["Comunidad de Andalucía", "Historia", "Secundaria", "Málaga"])
HISTORIA_VIEJA = _item(
    "Se necesita profesor/a de historia para Bachillerato",
    "https://colegios.es/empleoprofesores/historia-vieja-01092026/",
    "Tue, 01 Sep 2026 09:00:00 +0000",
    ["Comunidad de Madrid", "Historia", "Bachillerato", "Pozuelo"])


def test_solo_madrid_y_materias_del_perfil_y_el_bom_no_rompe():
    items = ColegiosEsSource()._parse(
        _feed(HISTORIA_MADRID, MATES_MADRID, HISTORIA_MALAGA), None)
    assert [i.url for i in items] == [
        "https://colegios.es/empleoprofesores/geografia-historia-13102026/"]
    assert items[0].date == date(2026, 10, 13)


def test_lo_que_emite_pasa_el_extractor():
    items = ColegiosEsSource()._parse(_feed(HISTORIA_MADRID), None)
    assert extract(items[0]) is not None


def test_lee_la_pagina_siguiente_si_la_ventana_es_mas_larga():
    p1 = MagicMock(status_code=200, content=_feed(HISTORIA_MADRID, MATES_MADRID))
    p1.raise_for_status = lambda: None
    p2 = MagicMock(status_code=200, content=_feed(HISTORIA_VIEJA))
    p2.raise_for_status = lambda: None

    def get(url, params=None, **kw):
        return p2 if params and params.get("paged") == 2 else p1

    with patch.object(colegios_es.requests, "get", side_effect=get) as g:
        items = ColegiosEsSource().fetch(since_date=date(2026, 10, 8))
    assert g.call_count == 2                       # la 1.ª no llegaba al 8/10
    assert [i.title for i in items] == [
        "Se necesita profesor/a de geografía e historia con C1 de inglés para ESO y Bachillerato"]


def test_probe_da_cero_si_el_feed_no_trae_entradas():
    resp = MagicMock(status_code=200, content=b"<html>mantenimiento</html>")
    resp.raise_for_status = lambda: None
    with patch.object(colegios_es.requests, "get", return_value=resp):
        assert ColegiosEsSource().probe_content_count() == 0
