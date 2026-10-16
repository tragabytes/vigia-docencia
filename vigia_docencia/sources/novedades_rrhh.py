"""
Fuente "Novedades de la Dirección General de Recursos Humanos" de Educación de
la Comunidad de Madrid. Spec 001, catálogo n.º 4.

Por qué: los listados de las listas extraordinarias de interinos (admitidos y
no admitidos), la formación de listas de interinos del curso, adjudicaciones…
se publican aquí y NO pasan por el BOCM (solo las convocatorias pasan por él).

Página: https://www.comunidad.madrid/educacion/novedades-direccion-general-recursos-humanos
Cada novedad es un `<p>` dentro de `.text-editor--content` con
"DD/MM/AAAA" + `<a>` (título y enlace a la sección de comunidad.madrid con
ancla, o a un PDF del BOCM). Hay un RSS oficial, pero solo guarda las 6
últimas; la página tiene el historial entero.

Identidad: la misma novedad se repite casi cada semana con el mismo título y
el mismo enlace ("Listas de nuevos aspirantes admitidos…": 4 veces entre
septiembre y octubre de 2026). Como el bot deduplica por (fuente, url,
título), el título lleva la fecha; si no, solo se avisaría de la primera.

Filtro: palabras del perfil en el título y fuera lo que claramente no es
(catedráticos de Música y Artes Escénicas, maestros, inspección, PAS…). La
especialidad concreta (0590-005, 0592-006) va dentro de los PDF: la decide el
enricher, que puede abrirlos.
"""
from __future__ import annotations

import logging
import re
from datetime import date
from typing import Optional

import requests

from vigia.sources.base import RawItem, Source

logger = logging.getLogger(__name__)

NOVEDADES_URL = (
    "https://www.comunidad.madrid/educacion/"
    "novedades-direccion-general-recursos-humanos"
)
BASE_URL = "https://www.comunidad.madrid"
ENTRADA_CSS = ".text-editor--content p"
HTTP_TIMEOUT = 30

_FECHA_RE = re.compile(r"^\s*(\d{2})/(\d{2})/(\d{4})")
_PERFIL_RE = re.compile(r"interin|extraordinari|secundaria|idiomas|traslad")
_FUERA_RE = re.compile(
    r"catedraticos de musica|artes escenicas|maestros|inspector|asesor"
    r"|administracion y servicios|libre designacion|huelga|elecciones sindicales"
)


class NovedadesRRHHSource(Source):
    name = "novedades_rrhh"
    probe_url = NOVEDADES_URL

    def probe_content_count(self) -> int:
        return self._probe_count_selector(NOVEDADES_URL, ENTRADA_CSS)

    def fetch(self, since_date: date) -> list[RawItem]:
        try:
            resp = requests.get(
                NOVEDADES_URL, headers=self._default_headers(), timeout=HTTP_TIMEOUT
            )
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("Novedades RRHH error: %s", exc)
            self.last_errors.append(str(exc))
            return []
        items = self._parse(resp.content, since_date)
        logger.info("Novedades RRHH: %d novedades del perfil en rango", len(items))
        return items

    def _parse(self, content: bytes, since_date: Optional[date]) -> list[RawItem]:
        """Página → RawItems de novedades del perfil. Sin red."""
        from bs4 import BeautifulSoup
        from vigia.config import normalize

        soup = BeautifulSoup(content, "lxml")
        items: list[RawItem] = []
        for p in soup.select(ENTRADA_CSS):
            enlace = p.find("a", href=True)
            m = _FECHA_RE.match(p.get_text(" ", strip=True))
            if enlace is None or m is None:
                continue
            try:
                fecha = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                continue
            if since_date is not None and fecha < since_date:
                continue
            titulo = enlace.get_text(" ", strip=True)
            href = enlace["href"].strip()
            url = href if href.startswith("http") else BASE_URL + href
            texto_norm = normalize(f"{titulo} {href}")
            if not _PERFIL_RE.search(texto_norm) or _FUERA_RE.search(texto_norm):
                continue
            items.append(RawItem(
                source=self.name,
                url=url,
                title=f"{titulo} ({fecha.strftime('%d/%m/%Y')})",
                date=fecha,
                text="Novedad de la Dirección General de Recursos Humanos, "
                     "Consejería de Educación de la Comunidad de Madrid "
                     "(profesorado docente).",
            ))
        return items
