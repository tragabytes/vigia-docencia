"""
Fuente Instituto Cervantes: convocatorias públicas de profesores de su sede
electrónica. Spec 001, catálogo n.º 10: una o dos al año (CVA-PROF-PUB-…,
CVA-PRA-PUB-…), que alimentan la bolsa para los centros del extranjero.

Listado: https://cervantes.sede.gob.es/es/procedimientos (todos en una página,
también los de años anteriores). Cada procedimiento es un
`<dnt-link to="/procedimiento/portada?idProc=N">título</dnt-link>`.

El listado no trae fecha. Con la de hoy, el primer día avisaría de las
convocatorias viejas que siguen listadas (2024, 2025). Por eso, solo para las
candidatas (pocas), se abre la ficha y se toma la primera fecha, la de
«Resumen del procedimiento [DD/MM/AAAA]» (las siguientes son fases).

Filtro: «profesor» en el título y fuera las internas para el personal del
Cervantes (restringidas, traslados, promoción interna, comisiones de servicio).
"""
from __future__ import annotations

import logging
import re
from datetime import date
from typing import Optional

import requests

from vigia.sources.base import RawItem, Source

logger = logging.getLogger(__name__)

BASE_URL = "https://cervantes.sede.gob.es"
LISTADO_URL = f"{BASE_URL}/es/procedimientos"
ITEM_CSS = "dnt-link[to*=idProc]"
HTTP_TIMEOUT = 30

_PERFIL_RE = re.compile(r"profesor")
_INTERNA_RE = re.compile(r"restringid|traslado|promocion interna|comision de servicios")
_FECHA_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")


class CervantesSource(Source):
    name = "cervantes"
    probe_url = LISTADO_URL

    def probe_content_count(self) -> int:
        return self._probe_count_selector(LISTADO_URL, ITEM_CSS)

    def fetch(self, since_date: date) -> list[RawItem]:
        try:
            resp = requests.get(LISTADO_URL, headers=self._default_headers(), timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("Cervantes listado error: %s", exc)
            self.last_errors.append(str(exc))
            return []
        items: list[RawItem] = []
        for title, url in _candidatas(resp.content):
            pub = self._fecha_ficha(url)
            if pub is None or pub < since_date:
                continue
            items.append(RawItem(
                source=self.name,
                url=url,
                title=title,
                date=pub,
                text="Instituto Cervantes. Convocatoria de profesores de español "
                     "(ELE) para sus centros.",
            ))
        logger.info("Cervantes: %d convocatorias de profesores en rango", len(items))
        return items

    def _fecha_ficha(self, url: str) -> Optional[date]:
        try:
            resp = requests.get(url, headers=self._default_headers(), timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("Cervantes ficha error (%s): %s", url, exc)
            self.last_errors.append(f"{url}: {exc}")
            return None
        return _primera_fecha(resp.text)


def _candidatas(content: bytes) -> list[tuple[str, str]]:
    """Listado → (título, url) de convocatorias públicas de profesores. Sin red."""
    from bs4 import BeautifulSoup
    from vigia.config import normalize

    out = []
    for el in BeautifulSoup(content, "lxml").select(ITEM_CSS):
        title = el.get_text(" ", strip=True)
        norm = normalize(title)
        if not _PERFIL_RE.search(norm) or _INTERNA_RE.search(norm):
            continue
        to = el.get("to", "").strip()
        out.append((title, to if to.startswith("http") else BASE_URL + to))
    return out


def _primera_fecha(html: str) -> Optional[date]:
    from bs4 import BeautifulSoup

    texto = BeautifulSoup(html, "lxml").get_text(" ", strip=True)
    m = _FECHA_RE.search(texto)
    if not m:
        return None
    try:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None
