"""
Colegios RC / Highlands con el lector SuccessFactors del núcleo (spec 001,
catálogo n.º 5).

Fallo que impide (16/10/2026): el perfil docente importa `SapEmpresa`, eso
cargaba el lector antes de fijar el perfil y filtraba con las palabras de
enfermería: 0 anuncios de Colegios RC, 0 errores. Arreglado en vigia-core
v0.11.1; este test lo comprueba de punta a punta con el perfil docente.
"""
from datetime import date
from unittest.mock import MagicMock, patch

from vigia.extractor import extract
from vigia.sources import sap_successfactors
from vigia.sources.sap_successfactors import SapSuccessfactorsSource

_LISTADO = """
<div class="job"><a class="jobTitle-link" href="/job/Majadahonda-DOCENTE-DE-GEOGRAFIA-E-HISTORIA/123/">DOCENTE DE GEOGRAFÍA E HISTORIA EN SECUNDARIA</a>
  <span class="jobDate">14 oct 2026</span></div>
<div class="job"><a class="jobTitle-link" href="/job/Madrid-TECNICO-PRL/124/">TÉCNICO DE PREVENCIÓN DE RIESGOS LABORALES</a>
  <span class="jobDate">07 oct 2026</span></div>
"""


def test_anuncio_de_historia_de_colegios_rc_llega_y_pasa_el_extractor():
    llena = MagicMock(text=_LISTADO, status_code=200)
    llena.raise_for_status = lambda: None
    vacia = MagicMock(text="<html></html>", status_code=200)
    vacia.raise_for_status = lambda: None

    def get(url, **kw):
        return llena if "colegiosrc.es" in url and "startrow=0" in url else vacia

    with patch.object(sap_successfactors.requests, "get", side_effect=get):
        items = SapSuccessfactorsSource().fetch(since_date=date(2026, 10, 1))

    rc = [i for i in items if i.extra["empresa"] == "COLEGIOS_RC"]
    assert [i.title for i in rc] == ["DOCENTE DE GEOGRAFÍA E HISTORIA EN SECUNDARIA"]
    assert extract(rc[0]) is not None
