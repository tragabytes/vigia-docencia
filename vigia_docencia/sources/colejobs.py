"""
Fuente Colejobs: ofertas de empleo de colegios privados y concertados
(colejobs.es). Spec 001, catálogo n.º 2: la mejor fuente abierta de colegios
de Madrid (81 de 94 ofertas activas eran de Madrid el 16/10/2026).

Listado general: https://www.colejobs.es/ofertas-de-empleo/ y
`/ofertas-de-empleo/paginador/N-5/` (20 por página, de más nueva a más
antigua). El listado "de Madrid" no sirve: su paginador devuelve siempre la
página 1. Cada oferta es `section.ofertas-empleo article > a`: enlace propio
estable, título en `h3`, colegio en `h4`, fecha absoluta ("16 octubre de 2026")
junto a `.ico-calendar` y lugar en `p.meta` antes del primer "|".

Ámbito (Laureano, 16/10/2026): colegios de la Comunidad de Madrid y puestos
online, de las materias del perfil (Historia, Geografía, Sociales,
Humanidades, ELE). Lo demás se descarta aquí; el extractor y el enricher
hacen el filtrado fino.
"""
from __future__ import annotations

import logging
import re
from datetime import date
from typing import Optional

import requests

from vigia.sources.base import RawItem, Source

logger = logging.getLogger(__name__)

BASE_URL = "https://www.colejobs.es/"
LISTADO_URL = BASE_URL + "ofertas-de-empleo/"
PAGINA_URL = BASE_URL + "ofertas-de-empleo/paginador/{n}-5/"
ITEM_CSS = "section.ofertas-empleo article > a"
MAX_PAGINAS = 8
HTTP_TIMEOUT = 30

# Lugar aceptado: cualquier municipio "…, Madrid", Madrid capital u online.
_LUGAR_OK = ("madrid", "online", "remoto", "teletrabajo")

# Materias del perfil, sobre el título normalizado. Corte en la fuente porque
# el patrón «profesor de secundaria» del perfil (pensado para el BOE) dejaba
# pasar conserjes y profesores de Religión, Lengua o Alemán (simulación del
# 16/10/2026).
_MATERIA_RE = re.compile(
    r"historia|geograf|sociales|humanidades|\bele\b|espanol para extranjeros"
    r"|espanol como lengua extranjera|spanish"
)

_MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}
_FECHA_RE = re.compile(r"(\d{1,2})\s+(?:de\s+)?([a-záéíóú]+)\s+de\s+(\d{4})", re.I)


class ColejobsSource(Source):
    name = "colejobs"
    probe_url = LISTADO_URL

    def probe_content_count(self) -> int:
        return self._probe_count_selector(LISTADO_URL, ITEM_CSS)

    def fetch(self, since_date: date) -> list[RawItem]:
        items: list[RawItem] = []
        vistas: set[str] = set()
        for n in range(1, MAX_PAGINAS + 1):
            url = LISTADO_URL if n == 1 else PAGINA_URL.format(n=n)
            try:
                resp = requests.get(
                    url, headers=self._default_headers(), timeout=HTTP_TIMEOUT
                )
                resp.raise_for_status()
            except Exception as exc:
                logger.warning("Colejobs error (página %d): %s", n, exc)
                self.last_errors.append(f"página {n}: {exc}")
                break
            ofertas = _ofertas(resp.content)
            urls = {o[0] for o in ofertas}
            # Página vacía, o el paginador repite una ya vista: fin.
            if not urls or urls <= vistas:
                break
            vistas |= urls
            items.extend(
                i for i in self._parse(resp.content, since_date)
                if i.url not in {x.url for x in items}
            )
            # De más nueva a más antigua: si toda la página es anterior a la
            # ventana, las siguientes también.
            fechas = [o[3] for o in ofertas if o[3]]
            if fechas and max(fechas) < since_date:
                break
        logger.info("Colejobs: %d ofertas en rango (Madrid u online)", len(items))
        return items

    def _parse(self, content: bytes, since_date: Optional[date]) -> list[RawItem]:
        """Ofertas del listado → RawItems de Madrid u online. Sin red."""
        items: list[RawItem] = []
        from vigia.config import normalize

        for a, titulo, colegio, fecha, lugar, meta in _ofertas(content):
            if not any(ok in lugar.lower() for ok in _LUGAR_OK):
                continue
            if not _MATERIA_RE.search(normalize(titulo)):
                continue
            pub = fecha or date.today()
            if since_date is not None and pub < since_date:
                continue
            items.append(RawItem(
                source=self.name,
                url=a,
                title=titulo,
                date=pub,
                text=f"{colegio}. {meta}",
                extra={"colegio": colegio, "lugar": lugar},
            ))
        return items


def _ofertas(content: bytes) -> list[tuple]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(content, "lxml")
    out = []
    for a in soup.select(ITEM_CSS):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        url = href if href.startswith("http") else BASE_URL + href.lstrip("/")
        titulo = _texto(a.select_one("h3"))
        colegio = _texto(a.select_one("h4"))
        cal = a.select_one(".ico-calendar")
        fecha = _parse_fecha(cal.parent.get_text(" ", strip=True)) if cal else None
        meta = _texto(a.select_one("p.meta"))
        lugar = meta.split("|", 1)[0].strip()
        out.append((url, titulo, colegio, fecha, lugar, meta))
    return out


def _parse_fecha(texto: str) -> Optional[date]:
    m = _FECHA_RE.search(texto or "")
    if not m:
        return None
    mes = _MESES.get(m.group(2).lower())
    try:
        return date(int(m.group(3)), mes, int(m.group(1))) if mes else None
    except ValueError:
        return None


def _texto(el) -> str:
    return el.get_text(" ", strip=True) if el is not None else ""
