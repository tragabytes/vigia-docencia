"""
Fuente TodoELE (spec 001, catálogo n.º 1). Offline, con fixtures recortados
del listado y del sitemap reales del 16/10/2026.

Fallos que impiden:
- avalancha el primer día: sin la fecha de alta del sitemap, todas las ofertas
  abiertas (~66) pasarían el filtro de fechas a la vez;
- pérdida silenciosa: si la web cambia y el listado da 0 filas, el probe tiene
  que marcar error (caso UAH, sep-oct 2026);
- avisos repetidos: dos lecturas seguidas deben dar las mismas (url, título).
"""
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from vigia.extractor import extract
from vigia_docencia.sources import todoele
from vigia_docencia.sources.todoele import TodoEleSource, _parse_sitemap

_LISTADO = """
<table class="views-table"><tbody>
<tr>
 <td class="views-field views-field-title"><a href="/ofertas-trabajo/profesor-de-ele-y-catalan-presencial-barcelona">Profesor de ELE y catalán presencial Barcelona</a><br/>
  <span class="empleador"><a href="/x">English for Business</a></span></td>
 <td class="views-field views-field-name-1"><span><a href="/p">España</a></span></td>
 <td class="views-field views-field-field-trabajo-fecha-limite"><time datetime="2026-10-16T12:00:00Z">16/10/2026</time></td>
</tr>
<tr>
 <td class="views-field views-field-title"><a href="/ofertas-trabajo/modern-foreign-language-teachers-ib-myp-ib-dp">Modern Foreign Language Teachers IB-MYP &amp; IB-DP</a><br/>
  <span class="empleador"><a href="/x">Dubai International Academy</a></span></td>
 <td class="views-field views-field-name-1"><span><a href="/p">Emiratos Árabes Unidos</a></span></td>
 <td class="views-field views-field-field-trabajo-fecha-limite"><time datetime="2026-11-06T12:00:00Z">06/11/2026</time></td>
</tr>
<tr>
 <td class="views-field views-field-title"><a href="/ofertas-trabajo/spanish-teacher-2">Spanish teacher</a><br/>
  <span class="empleador"><a href="/x">Bimic Group</a></span></td>
 <td class="views-field views-field-name-1"><span><a href="/p">China</a></span></td>
 <td class="views-field views-field-field-trabajo-fecha-limite"><time datetime="2026-10-31T12:00:00Z">31/10/2026</time></td>
</tr>
</tbody></table>
"""

_SITEMAP = """<urlset>
<url><loc>https://todoele.net/aplicaciones/deepseek</loc><lastmod>2026-08-31T01:01Z</lastmod></url>
<url><loc>https://todoele.net/ofertas-trabajo/spanish-teacher-2</loc><lastmod>2026-09-02T00:11Z</lastmod></url>
<url><loc>https://todoele.net/ofertas-trabajo/modern-foreign-language-teachers-ib-myp-ib-dp</loc><lastmod>2026-10-12T03:28Z</lastmod></url>
</urlset>"""


def _parse(since=None):
    return TodoEleSource()._parse_rows(
        _LISTADO.encode("utf-8"), _parse_sitemap(_SITEMAP), since
    )


def test_fecha_de_alta_del_sitemap_y_hoy_si_aun_no_esta():
    por_titulo = {i.title: i for i in _parse()}
    assert por_titulo["Spanish teacher"].date == date(2026, 9, 2)
    assert por_titulo["Modern Foreign Language Teachers IB-MYP & IB-DP"].date == date(2026, 10, 12)
    # Publicada hoy: el sitemap aún no la tiene.
    assert por_titulo["Profesor de ELE y catalán presencial Barcelona"].date == date.today()


def test_sin_avalancha_las_antiguas_no_pasan_el_filtro_de_fechas():
    titulos = [i.title for i in _parse(since=date(2026, 10, 10))]
    assert "Spanish teacher" not in titulos          # 02/09: antigua
    assert len(titulos) == 2


def test_todas_las_ofertas_pasan_el_extractor_como_ele():
    for item in _parse():
        assert extract(item) is not None, item.title


def test_campos():
    it = next(i for i in _parse() if i.title == "Spanish teacher")
    assert it.url == "https://todoele.net/ofertas-trabajo/spanish-teacher-2"
    assert it.extra == {"empleador": "Bimic Group", "pais": "China", "fecha_limite": "2026-10-31"}


def test_dos_lecturas_seguidas_dan_lo_mismo():
    claves = lambda: [(i.url, i.title) for i in _parse()]
    assert claves() == claves()


def test_probe_da_cero_si_cambia_la_estructura():
    resp = MagicMock(status_code=200, text="<html><body><div>rediseño</div></body></html>")
    resp.raise_for_status = lambda: None
    with patch("vigia.sources.base.requests.get", return_value=resp):
        assert TodoEleSource().probe_content_count() == 0


def test_fetch_recorre_paginas_hasta_una_vacia():
    vacia = MagicMock(content=b"<html></html>", status_code=200, text="")
    vacia.raise_for_status = lambda: None
    llena = MagicMock(content=_LISTADO.encode("utf-8"), status_code=200)
    llena.raise_for_status = lambda: None
    sitemap = MagicMock(status_code=200, text=_SITEMAP)
    sitemap.raise_for_status = lambda: None
    no_hay = MagicMock(status_code=404)

    def get(url, params=None, **kw):
        if url == todoele.SITEMAP_URL:
            return sitemap if params["page"] == 1 else no_hay
        return llena if params["page"] == 0 else vacia

    with patch.object(todoele.requests, "get", side_effect=get):
        items = TodoEleSource().fetch(since_date=date.today() - timedelta(days=3))
    assert [i.title for i in items] == ["Profesor de ELE y catalán presencial Barcelona"]
