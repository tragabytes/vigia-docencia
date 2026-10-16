"""
Fuente TodoELE: tabla de ofertas de empleo ELE de todoele.net (Drupal), la
referencia del sector. Spec 001, catálogo n.º 1: ~13 ofertas nuevas por
semana, en todo el mundo (EE. UU., Emiratos, Reino Unido, China, España…).

Listado: https://todoele.net/ofertas-trabajo?page=N (15 filas por página, de
más nueva a más antigua). Cada fila: `td.views-field-title a` (título y enlace
propio estable), `span.empleador`, país en `td.views-field-name-1` y fecha
límite en `time[datetime]`.

Por qué la fecha sale del sitemap
---------------------------------
El listado no da fecha de PUBLICACIÓN, solo la límite. Con la fecha de hoy
para todas, el primer día pasarían las ~66 ofertas abiertas de golpe
(avalancha a Telegram). El sitemap de Drupal (`/sitemap.xml?page=N`) trae un
`lastmod` por oferta que coincide con la fecha de alta; se regenera de
madrugada, así que una oferta publicada hoy aún no está y su fecha es hoy, que
es la correcta. Si una oferta se edita, su `lastmod` avanza y vuelve a pasar el
filtro de fechas, pero la deduplicación por (fuente, url, título) evita el
aviso repetido.

Por qué `text` lleva un marcador ELE
------------------------------------
Todo TodoELE es empleo ELE. Muchos títulos vienen en inglés y no siempre dicen
"Spanish" ("Modern Foreign Language Teachers IB-MYP"). Como en
`profesoresdeele`, la señal ELE la pone la fuente y el enricher decide la
relevancia fina.
"""
from __future__ import annotations

import logging
import re
from datetime import date
from typing import Optional

import requests

from vigia.sources.base import RawItem, Source

logger = logging.getLogger(__name__)

BASE_URL = "https://todoele.net"
LISTADO_URL = f"{BASE_URL}/ofertas-trabajo"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
ROW_CSS = "table.views-table tbody tr"
MAX_PAGINAS = 10
HTTP_TIMEOUT = 30

_LASTMOD_RE = re.compile(
    r"<loc>(https://todoele\.net/ofertas-trabajo/[^<]+)</loc>\s*"
    r"<lastmod>(\d{4})-(\d{2})-(\d{2})"
)


class TodoEleSource(Source):
    name = "todoele"
    probe_url = LISTADO_URL

    def probe_content_count(self) -> int:
        return self._probe_count_selector(LISTADO_URL, ROW_CSS)

    def fetch(self, since_date: date) -> list[RawItem]:
        filas_html: list[bytes] = []
        for page in range(MAX_PAGINAS):
            try:
                resp = requests.get(
                    LISTADO_URL, params={"page": page},
                    headers=self._default_headers(), timeout=HTTP_TIMEOUT,
                )
                resp.raise_for_status()
            except Exception as exc:
                logger.warning("TodoELE listado error (page=%d): %s", page, exc)
                self.last_errors.append(f"page={page}: {exc}")
                break
            if not self._parse_rows(resp.content):
                break
            filas_html.append(resp.content)

        fechas = self._fetch_fechas_alta()
        items: list[RawItem] = []
        seen: set[str] = set()
        for html in filas_html:
            for item in self._parse_rows(html, fechas, since_date):
                if item.url not in seen:
                    seen.add(item.url)
                    items.append(item)
        logger.info("TodoELE: %d ofertas en rango", len(items))
        return items

    def _fetch_fechas_alta(self) -> dict[str, date]:
        """url → fecha de alta, leída de las páginas del sitemap."""
        fechas: dict[str, date] = {}
        for page in (1, 2, 3):
            try:
                resp = requests.get(
                    SITEMAP_URL, params={"page": page},
                    headers=self._default_headers(), timeout=HTTP_TIMEOUT,
                )
                if resp.status_code == 404:
                    break
                resp.raise_for_status()
            except Exception as exc:
                logger.warning("TodoELE sitemap error (page=%d): %s", page, exc)
                self.last_errors.append(f"sitemap page={page}: {exc}")
                break
            fechas.update(_parse_sitemap(resp.text))
        return fechas

    def _parse_rows(
        self,
        content: bytes,
        fechas: Optional[dict[str, date]] = None,
        since_date: Optional[date] = None,
    ) -> list[RawItem]:
        """Filas del listado → RawItems. Sin red: testeable con un fixture."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "lxml")
        items: list[RawItem] = []
        for row in soup.select(ROW_CSS):
            enlace = row.select_one("td.views-field-title a[href]")
            if enlace is None:
                continue
            title = enlace.get_text(" ", strip=True)
            href = enlace["href"].strip()
            url = href if href.startswith("http") else BASE_URL + href
            empleador = _texto(row.select_one("span.empleador"))
            pais = _texto(row.select_one("td.views-field-name-1"))
            limite_el = row.select_one("time[datetime]")
            limite = limite_el["datetime"][:10] if limite_el else ""

            pub_date = (fechas or {}).get(url) or date.today()
            if since_date is not None and pub_date < since_date:
                continue
            items.append(RawItem(
                source=self.name,
                url=url,
                title=title,
                date=pub_date,
                text=f"Oferta ELE (español como lengua extranjera). {empleador}. {pais}.",
                extra={"empleador": empleador, "pais": pais, "fecha_limite": limite},
            ))
        return items


def _parse_sitemap(xml: str) -> dict[str, date]:
    return {
        url: date(int(y), int(m), int(d))
        for url, y, m, d in _LASTMOD_RE.findall(xml)
    }


def _texto(el) -> str:
    return el.get_text(" ", strip=True) if el is not None else ""
