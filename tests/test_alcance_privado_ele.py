"""
Alcance del perfil ampliado por Laureano el 16/10/2026 (spec 001, H1):
colegios privados y concertados de toda la Comunidad de Madrid y online,
también puestos que mezclan materias o con parte de las clases en inglés,
y ELE en cualquier país (incluidos colegios de EE. UU., Reino Unido o
Emiratos). Siguen fuera los puestos enteramente en inglés.

Fallo que impide: el perfil se escribió para boletines oficiales y el
extractor tiraba en silencio las ofertas reales de colegios y de ELE que
traen las fuentes nuevas («Spanish Teacher», «Profesor/a de Historia ESO y
Bachillerato», «… con C1 de inglés»). Los títulos son los reales de
`specs/001-buscar-fuentes-docencia/cobertura.md`.
"""
from datetime import date

import pytest

from vigia.extractor import extract
from vigia.sources.base import RawItem


def _raw(title: str) -> RawItem:
    return RawItem(source="test", url=f"http://x/{abs(hash(title))}",
                   title=title, date=date(2026, 10, 16), text="")


@pytest.mark.parametrize("titulo", [
    "Profesor de Lengua Castellana, Valores y Geografía e Historia",
    "Se necesita profesor/a de Geografía e Historia con C1 de inglés para ESO y Bachillerato",
    "Profesor de Economía y Geografía e Historia con inglés alto",
    "Profesor/a de Business e Historia curso 26-27",
    "Profesor de Historia ESO y Bachillerato",
    "Profesores/as de Ciencias Sociales y/o Humanidades ESO y Bachillerato curso 26-27",
    "Profesor/a de Humanidades, sustitución",
    "SOCIALES/HUMANIDADES ESO y Bachillerato. Madrid",
    "Profesor/a de Lengua y Literatura con Historia y Geografía",
    "Profesor/a de Español ELE",
    "Spanish Language Teacher",
    "AP Spanish Teacher",
    "PYP Spanish Teacher",
    "Profesor de Español a jornada completa en Hong Kong",
    "Profesor de secundaria bilingüe en inglés - colegio Madrid",
])
def test_ofertas_del_perfil_pasan_el_extractor(titulo):
    assert extract(_raw(titulo)) is not None


@pytest.mark.parametrize("titulo", [
    "Teacher of Geography",
    "Teacher of Geography Key Stage 3 and 4",
    "Philosophy Teacher 2026/2027",
    "English Teacher - Madrid",
    "Maestro/a de Educación Primaria",
    "Profesor/a de Matemáticas ESO",
])
def test_ofertas_fuera_del_perfil_no_pasan(titulo):
    assert extract(_raw(titulo)) is None
