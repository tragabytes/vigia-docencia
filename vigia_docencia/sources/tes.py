"""
Fuente TES (tes.com/jobs): el portal británico de empleo docente. Spec 001,
catálogo n.º 9: profesor de español en colegios del Reino Unido e
internacionales (~110 activas; muchas piden la habilitación británica, QTS, o
permiso de trabajo: lo valora el enricher).

La búsqueda (`/jobs/search?keywords=spanish%20teacher&sort=date`) es una página
Next.js: los datos van en el JSON de `<script id="__NEXT_DATA__">`, en
`props.pageProps.initialData.jobs`. Cada oferta trae `title`, `canonicalUrl`
(enlace estable con id), `advert.startDate` (alta), `employer.name` y
`displayLocation`.

Limitación conocida (16/10/2026): la paginación no funciona por la URL (la
página ignora `page`), así que solo se leen las 20 más recientes por fecha. Con
el bot diario basta salvo un día de mucho movimiento.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import date
from typing import Optional

import requests

from vigia.sources.base import RawItem, Source

logger = logging.getLogger(__name__)

BASE_URL = "https://www.tes.com"
SEARCH_URL = f"{BASE_URL}/jobs/search?keywords=spanish%20teacher&sort=date"
HTTP_TIMEOUT = 30

_NEXT_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
_TITULO_RE = re.compile(r"spanish|espanol")


class TesSource(Source):
    name = "tes"
    probe_url = SEARCH_URL

    def probe_content_count(self) -> int:
        try:
            resp = requests.get(SEARCH_URL, headers=self._default_headers(), timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
            return len(_ofertas(resp.text))
        except Exception:
            return 0

    def fetch(self, since_date: date) -> list[RawItem]:
        try:
            resp = requests.get(SEARCH_URL, headers=self._default_headers(), timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("TES error: %s", exc)
            self.last_errors.append(str(exc))
            return []
        items = self._parse(resp.text, since_date)
        logger.info("TES: %d ofertas de español en rango", len(items))
        return items

    def _parse(self, html: str, since_date: Optional[date]) -> list[RawItem]:
        """Página de búsqueda → RawItems de profesor de español. Sin red."""
        from vigia.config import normalize

        out: list[RawItem] = []
        for job in _ofertas(html):
            title = (job.get("title") or "").strip()
            path = (job.get("canonicalUrl") or "").strip()
            if not title or not path or not _TITULO_RE.search(normalize(title)):
                continue
            pub = _fecha((job.get("advert") or {}).get("startDate"))
            if since_date is not None and pub < since_date:
                continue
            empleador = ((job.get("employer") or {}).get("name") or "").strip()
            lugar = (job.get("displayLocation") or "").strip()
            cierre = ((job.get("application") or {}).get("closeDate") or "")[:10]
            out.append(RawItem(
                source=self.name,
                url=BASE_URL + path,
                title=title,
                date=pub,
                text=f"Oferta de profesor de español (Spanish teacher). {empleador}. {lugar}.",
                extra={"empleador": empleador, "lugar": lugar, "fecha_limite": cierre},
            ))
        return out


def _ofertas(html: str) -> list[dict]:
    m = _NEXT_RE.search(html or "")
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
        return list(data["props"]["pageProps"]["initialData"]["jobs"] or [])
    except (ValueError, KeyError, TypeError):
        return []


def _fecha(iso: Optional[str]) -> date:
    try:
        return date.fromisoformat((iso or "")[:10])
    except ValueError:
        return date.today()
