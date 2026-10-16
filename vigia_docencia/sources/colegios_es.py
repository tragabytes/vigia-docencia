"""
Fuente Colegios.es: feed RSS (WordPress) de su bolsa de empleo para centros
educativos. Spec 001, catálogo n.º 3: anuncios anónimos de colegios de toda
España, ~2 al mes de Historia en la Comunidad de Madrid.

Feed: https://colegios.es/empleoprofesores/feed/ (20 entradas, ~2-3 días).
Los lunes la ventana del bot es de 5 días, así que se leen las páginas
siguientes (`?paged=N`) hasta salir de la ventana. Cada `<item>` trae enlace
propio, `pubDate` y como `<category>` la región ("Comunidad de Madrid"), el
municipio y las materias ("Geografía", "Historia", "Secundaria"…). El feed
empieza con BOM: se quita antes de parsear.

Ámbito (Laureano, 16/10/2026): Comunidad de Madrid u online, y materias del
perfil (Historia, Geografía, Sociales, Humanidades, ELE). `text` = categorías,
como en `profesoresdeele`: señal curada por la web, sin el cuerpo del anuncio.
"""
from __future__ import annotations

import logging
import re
from datetime import date
from email.utils import parsedate
from typing import Optional
from xml.etree import ElementTree as ET

import requests

from vigia.sources.base import RawItem, Source

logger = logging.getLogger(__name__)

FEED_URL = "https://colegios.es/empleoprofesores/feed/"
MAX_PAGINAS = 6
HTTP_TIMEOUT = 30

_REGION_OK = ("comunidad de madrid", "online", "remoto", "teletrabajo")
_MATERIA_RE = re.compile(
    r"historia|geograf|sociales|humanidades|\bele\b|espanol para extranjeros"
    r"|espanol como lengua extranjera|spanish"
)


class ColegiosEsSource(Source):
    name = "colegios_es"
    probe_url = FEED_URL

    def probe_content_count(self) -> int:
        try:
            resp = requests.get(
                FEED_URL, headers=self._default_headers(), timeout=HTTP_TIMEOUT
            )
            resp.raise_for_status()
            return len(_items(resp.content))
        except Exception:
            return 0

    def fetch(self, since_date: date) -> list[RawItem]:
        items: list[RawItem] = []
        for page in range(1, MAX_PAGINAS + 1):
            params = {"paged": page} if page > 1 else None
            try:
                resp = requests.get(
                    FEED_URL, params=params,
                    headers=self._default_headers(), timeout=HTTP_TIMEOUT,
                )
                if page > 1 and resp.status_code == 404:
                    break
                resp.raise_for_status()
            except Exception as exc:
                logger.warning("Colegios.es feed error (página %d): %s", page, exc)
                self.last_errors.append(f"página {page}: {exc}")
                break
            entradas = _items(resp.content)
            if not entradas:
                break
            items.extend(self._parse(resp.content, since_date))
            # Más nuevas primero: si la más antigua de la página ya está fuera
            # de la ventana, no hace falta la siguiente.
            if min(e[2] for e in entradas) < since_date:
                break
        logger.info("Colegios.es: %d ofertas en rango (Madrid u online)", len(items))
        return items

    def _parse(self, content: bytes, since_date: Optional[date]) -> list[RawItem]:
        """Feed → RawItems de Madrid u online y del perfil. Sin red."""
        from vigia.config import normalize

        out: list[RawItem] = []
        for title, url, pub, cats in _items(content):
            cats_norm = normalize(" ".join(cats))
            if not any(r in cats_norm for r in _REGION_OK):
                continue
            if not _MATERIA_RE.search(normalize(title) + " " + cats_norm):
                continue
            if since_date is not None and pub < since_date:
                continue
            out.append(RawItem(
                source=self.name,
                url=url,
                title=title,
                date=pub,
                text=" ".join(cats),
                extra={"categorias": cats},
            ))
        return out


def _items(content: bytes) -> list[tuple]:
    raw = content.lstrip(b"\xef\xbb\xbf").lstrip()
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return []
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        url = (it.findtext("link") or "").strip()
        cats = [c.text.strip() for c in it.findall("category") if c.text and c.text.strip()]
        out.append((title, url, _fecha(it.findtext("pubDate")), cats))
    return out


def _fecha(raw: Optional[str]) -> date:
    parsed = parsedate(raw) if raw else None
    if parsed:
        try:
            return date(parsed[0], parsed[1], parsed[2])
        except ValueError:
            pass
    return date.today()
