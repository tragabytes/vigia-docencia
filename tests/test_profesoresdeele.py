"""
Pruebas offline de la fuente ProfesoresdeELE.

Validan el parseo del feed RSS (categoría "Ofertas de trabajo") sin red, usando
un fixture, y blindan la decisión de diseño clave: el `text` del RawItem se
compone de los <category>/tags, no de la description. Así una oferta ELE
legítima cuyo excerpt menciona "educación infantil" (caso real: Tánger) NO se
descarta por el FALSE_POSITIVE_PATTERN del perfil pensado para boletines.

El perfil docente lo fija tests/conftest.py antes de importar el extractor.
"""
from datetime import date

from vigia.extractor import extract
from vigia.sources.base import RawItem
from vigia_docencia.sources.profesoresdeele import ProfesoresDeEleSource

# Fixture: 3 ofertas reales-realistas. Tánger lleva "educación infantil" en la
# description (disparador de FP) pero tags ELE limpios. La 3ª es antigua.
_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel>
  <title>Ofertas de trabajo archivos - Profesores de ELE</title>
  <link>https://profesoresdeele.org/category/ofertas-de-trabajo/</link>
  <item>
    <title>Trabaja como profesor de espanol en Madrid</title>
    <link>https://profesoresdeele.org/2026/05/20/madrid/</link>
    <pubDate>Wed, 20 May 2026 12:00:00 +0000</pubDate>
    <category><![CDATA[Ofertas de trabajo]]></category>
    <category><![CDATA[empleo ELE]]></category>
    <category><![CDATA[espanol para extranjeros]]></category>
    <category><![CDATA[profesor de ELE]]></category>
    <description><![CDATA[Compartimos oferta de empleo para trabajar como profesor de espanol en Madrid. Hasta el 30 de mayo.]]></description>
  </item>
  <item>
    <title>Se busca profesor/a ELE en Tanger (Marruecos)</title>
    <link>https://profesoresdeele.org/2026/05/10/tanger/</link>
    <pubDate>Sun, 10 May 2026 16:00:00 +0000</pubDate>
    <category><![CDATA[Ofertas de trabajo]]></category>
    <category><![CDATA[empleo ELE]]></category>
    <category><![CDATA[profesor de ELE]]></category>
    <category><![CDATA[Secundaria]]></category>
    <description><![CDATA[Profesor/a de ELE. El centro acoge alumnos desde educacion infantil hasta secundaria.]]></description>
  </item>
  <item>
    <title>Oferta antigua de profesor de espanol</title>
    <link>https://profesoresdeele.org/2026/01/01/old/</link>
    <pubDate>Wed, 01 Jan 2026 10:00:00 +0000</pubDate>
    <category><![CDATA[Ofertas de trabajo]]></category>
    <category><![CDATA[empleo ELE]]></category>
    <description><![CDATA[Oferta antigua.]]></description>
  </item>
</channel>
</rss>"""


def _parse(since=date(2026, 5, 1)):
    return ProfesoresDeEleSource()._parse_items(_RSS, since)


# ---------------------------------------------------------------------------
# Parseo del feed
# ---------------------------------------------------------------------------

def test_parsea_items_en_rango_y_filtra_antiguos():
    items = _parse(since=date(2026, 5, 1))
    # 2 en rango (Madrid 20-may, Tanger 10-may); la antigua (1-ene) se filtra.
    assert len(items) == 2
    titulos = [i.title for i in items]
    assert any("Madrid" in t for t in titulos)
    assert any("Tanger" in t for t in titulos)
    assert all("antigua" not in t for t in titulos)


def test_campos_del_rawitem():
    madrid = next(i for i in _parse() if "Madrid" in i.title)
    assert madrid.source == "profesoresdeele"
    assert madrid.date == date(2026, 5, 20)
    assert madrid.url == "https://profesoresdeele.org/2026/05/20/madrid/"
    # text = tags unidos (no la description)
    assert "empleo ELE" in madrid.text
    assert "Hasta el 30 de mayo" not in madrid.text
    assert madrid.extra["tags"]  # tags preservados para trazabilidad


def test_since_amplio_incluye_la_antigua():
    items = _parse(since=date(2026, 1, 1))
    assert len(items) == 3


# ---------------------------------------------------------------------------
# Integración con el extractor del perfil (la razón de ser del diseño)
# ---------------------------------------------------------------------------

def test_ofertas_matchean_categoria_ele():
    for item in _parse():
        out = extract(item)
        assert out is not None, f"no matcheo: {item.title}"
        assert out.categoria == "ele"


def test_tanger_no_cae_por_fp_educacion_infantil():
    """El caso que justifica usar tags y no la description: la oferta de Tanger
    se captura aunque su excerpt mencione 'educacion infantil' (FP del perfil)."""
    tanger = next(i for i in _parse() if "Tanger" in i.title)
    assert extract(tanger) is not None
    # Y al contrario: si el text llevara la description, el FP la descartaria.
    con_excerpt = RawItem(
        source="profesoresdeele", url=tanger.url, title=tanger.title,
        date=tanger.date,
        text="El centro acoge alumnos desde educacion infantil hasta secundaria.",
    )
    assert extract(con_excerpt) is None


# ---------------------------------------------------------------------------
# Robustez
# ---------------------------------------------------------------------------

def test_xml_corrupto_no_revienta():
    src = ProfesoresDeEleSource()
    assert src._parse_items(b"<rss><broken", date(2026, 1, 1)) == []
    assert src.last_errors  # registra el error para la notificacion
