"""
Fuente ProfesoresdeELE: feed RSS de ofertas de empleo del blog
profesoresdeele.org (WordPress), para el bloque ELE del perfil docente.

Por qué el feed de CATEGORÍA y no el general
--------------------------------------------
El feed raíz (`/feed/`) mezcla artículos didácticos ("...para el aula ELE")
con ofertas de trabajo. Los didácticos contienen "ELE"/"español" y se colarían
como falsos positivos. WordPress expone un feed por categoría, así que tiramos
del de la categoría "Ofertas de trabajo":

    https://profesoresdeele.org/category/ofertas-de-trabajo/feed/

Es 100% señal: solo ofertas (Cádiz, Madrid, Tánger, Bratislava, online...).

Por qué `text` se compone de los <category>/tags y NO de la description
-----------------------------------------------------------------------
El extractor del core aplica los FALSE_POSITIVE_PATTERNS del perfil ANTES de
buscar match. Esos FP están pensados para boletines oficiales (p.ej.
"educación infantil" descarta convocatorias de maestros 0597). Pero el excerpt
de una oferta ELE en un colegio internacional menciona a menudo "desde
educación infantil...", lo que tumbaría una oferta legítima (caso real: Tánger).

Los <category> del post, en cambio, son señal curada por el blog y siempre
incluyen marcadores ELE limpios ("empleo ELE", "español para extranjeros",
"profesor de ELE") + ubicación, sin disparar FP. Validado sobre el feed real:
con `text` = tags se capturan 10/10 ofertas (categoría "ele"); con la
description, 9/10 (se pierde Tánger). La description queda fuera del matching;
el enricher la recupera leyendo el cuerpo (profesoresdeele.org está en
`enricher_allowed_fetch_hosts`).

A diferencia de codem, esta fuente NO filtra por `fast_keywords`: el feed de
categoría ya es íntegramente ofertas, y el filtrado fino lo hace el extractor
del perfil. La red está aislada en `fetch`; `_parse_items` es testeable offline.

Limitación conocida: el feed solo guarda los ~10 últimos posts de la categoría.
El blog publica ofertas con baja frecuencia (~mensual), así que el cron diario
las captura de sobra; para un hueco largo, usar `--since` con backfill.
"""
from __future__ import annotations

import logging
from datetime import date
from email.utils import parsedate
from typing import Optional
from xml.etree import ElementTree as ET

import requests

from vigia.sources.base import RawItem, Source

logger = logging.getLogger(__name__)

FEED_URL = "https://profesoresdeele.org/category/ofertas-de-trabajo/feed/"
HTTP_TIMEOUT = 30


class ProfesoresDeEleSource(Source):
    name = "profesoresdeele"
    probe_url = FEED_URL

    def fetch(self, since_date: date) -> list[RawItem]:
        try:
            resp = requests.get(
                FEED_URL, headers=self._default_headers(), timeout=HTTP_TIMEOUT
            )
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("ProfesoresdeELE RSS error: %s", exc)
            self.last_errors.append(str(exc))
            return []

        items = self._parse_items(resp.content, since_date)
        logger.info("ProfesoresdeELE: %d ofertas en rango", len(items))
        return items

    def _parse_items(self, content: bytes, since_date: date) -> list[RawItem]:
        """Parsea el RSS (bytes) y devuelve las ofertas en rango. Sin red:
        separado de `fetch` para poder testearlo offline con un fixture."""
        try:
            root = ET.fromstring(content)
        except ET.ParseError as exc:
            logger.error("ProfesoresdeELE: error parseando RSS: %s", exc)
            self.last_errors.append(f"parse error: {exc}")
            return []

        items: list[RawItem] = []
        for rss_item in root.iter("item"):
            title = (rss_item.findtext("title") or "").strip()
            url = (rss_item.findtext("link") or "").strip()
            cats = [
                c.text.strip()
                for c in rss_item.findall("category")
                if c.text and c.text.strip()
            ]

            pub_date = self._parse_date(rss_item.findtext("pubDate"))
            if pub_date < since_date:
                continue

            # `text` = tags curados (ver docstring del módulo): señal ELE limpia
            # para el matching sin arrastrar los FP que viven en el excerpt.
            items.append(
                RawItem(
                    source=self.name,
                    url=url,
                    title=title,
                    date=pub_date,
                    text=" ".join(cats),
                    extra={"tags": cats},
                )
            )

        return items

    @staticmethod
    def _parse_date(raw: Optional[str]) -> date:
        """pubDate RFC-822 → date; hoy como fallback si falta o no parsea."""
        if raw:
            parsed = parsedate(raw)
            if parsed:
                try:
                    return date(parsed[0], parsed[1], parsed[2])
                except ValueError:
                    pass
        return date.today()
