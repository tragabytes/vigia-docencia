"""
Perfil docente: secundaria Geografía e Historia (especialidad 005) + ELE/EOI
(Cuerpo 0592) + lectorados/auxiliares + colegios privados del noroeste de Madrid.

Portado 1:1 del bot desplegado `alerta-empleo-profe` (su `config.py` y
`enricher.py`), ahora expresado como un `Profile` del núcleo compartido
(vigia-core). El motor de matching es el mismo del core, así que el
comportamiento de extracción se preserva.

Alcance (informe.md): INCLUYE Cuerpo 0590 esp. 005, Cuerpo 0592/ELE, bolsas e
interinidades, traslados, lectorados (AECID/MEFP/Fulbright/Cervantes) y privados
noroeste. EXCLUYE a propósito primaria (0597), universidad/PDI general (solo
universidad en contexto ELE) y roles 100% en inglés.
"""
from __future__ import annotations

from vigia.profile import Profile
from vigia_docencia.sources.bocm import BOCMSource
from vigia_docencia.sources.profesoresdeele import ProfesoresDeEleSource

# ---------------------------------------------------------------------------
# Matching — patrones (informe.md, regex maestro docente)
# Texto normalizado antes de aplicar (minúsculas, sin tildes, solo [a-z0-9 ]),
# por eso los patrones no llevan tildes.
# ---------------------------------------------------------------------------

# Match fuerte: cualquiera de estos en el texto normalizado → alerta.
_STRONG_PATTERNS = [
    # --- Especialidad principal (Geografía e Historia) ---
    r"geografia\s+e\s+historia",
    r"especialidad\s+005\b",
    r"\b005\s+geografia",
    # --- Cuerpo 0590 (Profesores de Enseñanza Secundaria) ---
    r"cuerpo\s+0590",
    r"profesor(?:ado|es)?\s+(?:de\s+)?(?:ensenanza\s+)?secundaria",
    r"profesores?\s+de\s+secundaria",
    # --- Cuerpo 0592 (EOI) y especialidad ELE ---
    r"cuerpo\s+0592",
    r"escuelas?\s+oficiales?\s+de\s+idiomas",
    r"\beoi\b",
    r"espanol\s+para\s+extranjeros",
    r"espanol\s+como\s+lengua\s+extranjera",
    r"\bele\b",
    # --- Listas, bolsas, interinidad ---
    r"interinidad",
    r"interin[oa]s?\s+docente",
    r"listas?\s+extraordinaria",
    r"bolsa\s+de\s+empleo.{0,40}docente",
    r"bolsa\s+de\s+(?:trabajo|empleo)\s+(?:de\s+)?(?:profesor|docente)",
    r"bolsa\s+(?:de\s+)?(?:trabajo|empleo).{0,40}(?:secundaria|profesor)",
    r"profesorado\s+interino",
    # --- Concursos de traslados y procesos selectivos docentes ---
    r"concurso\s+de\s+traslados.{0,40}docente",
    r"concurso\s+de\s+traslados.{0,40}(?:profesor|secundaria|cuerpo)",
    r"proceso\s+selectivo.{0,40}(?:profesor|docente|secundaria|cuerpo\s+05)",
    # --- Educación de adultos / compensatoria ---
    r"profesor\s+(?:de\s+)?adultos",
    r"educacion\s+(?:de\s+)?adultos",
    r"educacion\s+compensatoria",
    # --- Lectorados y auxiliares (Cervantes, AECID, MEFP, Fulbright) ---
    r"\blectorad[oa]s?\b",
    r"auxiliar(?:es)?\s+(?:de\s+)?conversacion",
    r"profesor(?:ado|es)?\s+visitante",
    r"profesor(?:ado|es)?\s+(?:de\s+)?espanol\s+(?:en|para)",
]

# Match débil: solo si ADEMÁS aparece el confirmador en una ventana de 100 chars.
_WEAK_CONTEXT_PATTERNS = [
    (r"convocatoria",          r"profesor|docente|secundaria|cuerpo\s+05"),
    (r"proceso\s+selectivo",   r"profesor|docente|secundaria|cuerpo\s+05"),
    (r"oposicion(?:es)?",      r"profesor|docente|secundaria|cuerpo\s+05"),
    (r"plazas?",               r"profesor|docente|interino|cuerpo\s+05"),
    (r"consejeria\s+de\s+educacion", r"profesor|docente|interino"),
    (r"ministerio\s+de\s+educacion", r"profesor|docente|cuerpo"),
]

# Falsos positivos a descartar antes de cualquier check:
#   - Maestros (cuerpo 0597, primaria) — no aplica al perfil de secundaria.
#   - Roles totalmente bilingües en inglés (el perfil tiene C1, no nativo).
#   - Universidad pública (PDI / contratado doctor / titular) — proceso
#     diferente a las oposiciones de secundaria.
# OJO: NO se filtran otras especialidades de secundaria (Matemáticas, Física…)
# como FP, porque una convocatoria agrupa varias especialidades y caería una
# que SÍ incluye Geografía e Historia. La precisión la da exigir la especialidad
# en STRONG, no excluir las otras.
_FALSE_POSITIVE_PATTERNS = [
    r"\bmaestros?\b.{0,40}(?:cuerpo\s+0597|infantil|primaria)",
    r"cuerpo\s+0597",
    r"educacion\s+infantil",
    # Roles 100% en inglés — filtro intencional del informe
    r"bilingue.{0,40}ingles",
    r"impartir.{0,40}en\s+ingles",
    r"clases.{0,30}en\s+ingles",
    r"english\s+(?:teacher|speaking)",
    # Universidad: PDI, ayudante doctor, profesor contratado, titular
    r"profesor(?:a|es)?\s+(?:ayudante|contratado|titular|asociado|colaborador|emerito)",
    r"\bpdi\b",
    r"personal\s+docente\s+e\s+investigador",
    # Nombramientos universitarios (resoluciones BOE de tomas de posesión etc.)
    r"resoluci[oó]n.{0,60}universidad.{0,60}por\s+la\s+que\s+se\s+nombra",
    r"resoluci[oó]n.{0,60}por\s+la\s+que\s+se\s+nombra.{0,80}universidad",
    r"toma\s+de\s+posesion.{0,40}universidad",
]

# Filtro rápido que las fuentes (BOE del core) aplican sobre el título antes de
# materializar un RawItem. = TITLE_FAST_KEYWORDS del BOE del fork. El BOCM custom
# trae su propia lista embebida.
_FAST_KEYWORDS = [
    "profesor",
    "docente",
    "ensenanza secundaria",
    "secundaria",
    "cuerpo 0590",
    "cuerpo 0592",
    "geografia e historia",
    "interinidad",
    "lectorado",
    "lectorad",
    "auxiliar de conversacion",
    "espanol para extranjeros",
    " ele ",
    "escuelas oficiales de idiomas",
    "concurso de traslados",
    "educacion",
]

# ---------------------------------------------------------------------------
# Clasificación de categorías (orden importa: la primera que matchea gana)
# ---------------------------------------------------------------------------
_CATEGORY_HINTS = {
    "lectorado": [
        "lectorado",
        "auxiliar de conversacion",
        "auxiliares de conversacion",
        "profesor visitante",
        "profesores visitantes",
        "fulbright",
        "aecid",
    ],
    "ele": [
        "ele ",
        "espanol para extranjeros",
        "espanol como lengua extranjera",
        "escuela oficial de idiomas",
        "instituto cervantes",
        "academia de espanol",
    ],
    "traslado": [
        "concurso de traslados",
        "concurso de meritos",
        "concurso traslado",
    ],
    "bolsa": [
        "bolsa de empleo",
        "bolsa de trabajo",
        "bolsa unica",
        "lista extraordinaria",
        "listas extraordinarias",
        "interinidad",
        "interinos",
        "contratacion temporal",
    ],
    "oposicion": [
        "convocatoria",
        "proceso selectivo",
        "pruebas selectivas",
        "concurso oposicion",
        "oposicion",
        "estabilizacion",
        "acceso libre",
    ],
    "oep": ["oferta de empleo publico", "oep "],
    "nombramiento": ["nombramiento", "resolucion", "adjudicacion"],
    "privada": [
        "colegio",
        "colegios",
        "school",
        "international school",
    ],
}

# ---------------------------------------------------------------------------
# Watchlist de organismos vigilados (sección 06 del dashboard)
# ---------------------------------------------------------------------------
_WATCHLIST_ORGS = [
    # --- Empleo público estatal y autonómico ---
    {"id": "T-01", "name": "Consejería de Educación CM",
     "desc": "Comunidad de Madrid — Consejería de Educación, Ciencia y Universidades",
     "patterns": ["consejeria de educacion", "direccion general de recursos humanos",
                  "comunidad de madrid"]},
    {"id": "T-02", "name": "Ministerio de Educación",
     "desc": "Ministerio de Educación, Formación Profesional y Deportes (MEFD)",
     "patterns": ["ministerio de educacion", "mefd", "mefp"]},
    {"id": "T-03", "name": "Instituto Cervantes",
     "desc": "Sede Cervantes — convocatorias de profesorado y becas",
     "patterns": ["instituto cervantes", "cervantes"]},
    {"id": "T-04", "name": "AECID Lectorados",
     "desc": "MAEC-AECID — lectorados MAEC en universidades extranjeras",
     "patterns": ["aecid", "maec aecid", "lectorad"]},
    {"id": "T-05", "name": "MEFP Auxiliares",
     "desc": "Profex 2 — auxiliares de conversación en el extranjero",
     "patterns": ["auxiliares de conversacion", "auxiliar de conversacion", "profex"]},
    {"id": "T-06", "name": "Fulbright FLTA",
     "desc": "Fulbright España — Foreign Language Teaching Assistant",
     "patterns": ["fulbright", "flta"]},
    {"id": "T-07", "name": "EOI Madrid",
     "desc": "Escuelas Oficiales de Idiomas (especialidad 008)",
     "patterns": ["escuela oficial de idiomas", "escuelas oficiales de idiomas",
                  " eoi ", "cuerpo 0592"]},
    # --- Sindicatos / canales de información en tiempo real ---
    {"id": "T-08", "name": "ANPE Madrid",
     "desc": "Sindicato ANPE Madrid — bolsas y convocatorias",
     "patterns": ["anpe madrid", "anpemadrid", " anpe "]},
    {"id": "T-09", "name": "CSIF Educación",
     "desc": "CSIF Educación Madrid — resoluciones BOCM en directo",
     "patterns": ["csif", "csi f"]},
    {"id": "T-10", "name": "FeSP-UGT",
     "desc": "UGT Servicios Públicos Madrid — enseñanza pública",
     "patterns": ["fesp ugt", "ugt educacion", "ugt ensenanza"]},
    {"id": "T-11", "name": "CCOO Educación",
     "desc": "CCOO Madrid — federación de enseñanza",
     "patterns": ["ccoo", "feccoo", "comisiones obreras"]},
    # --- ATS de colegios privados zona noroeste ---
    {"id": "T-12", "name": "Inspired Education",
     "desc": "Inspired Education — Mirabal, Kensington, King's, San Patricio, Everest",
     "patterns": ["inspired", "mirabal", "kensington", "kings college",
                  "san patricio", "everest"]},
    {"id": "T-13", "name": "SEK Group",
     "desc": "SEK Education — El Castillo, Ciudalcampo, UCJC",
     "patterns": ["sek el castillo", "sek ciudalcampo", "sek group", "sek education",
                  "camilo jose cela", "ucjc"]},
    {"id": "T-14", "name": "Brains Schools",
     "desc": "Brains International Schools — La Moraleja",
     "patterns": ["brains international", "brains schools"]},
    {"id": "T-15", "name": "Highlands / Colegios RC",
     "desc": "Colegios RC — Highlands Los Fresnos, El Encinar, Everest Monteclaro",
     "patterns": ["highlands", "colegios rc", "los fresnos", "el encinar",
                  "everest monteclaro", "monteclaro"]},
    # --- Ayuntamientos noroeste ---
    {"id": "T-16", "name": "Ayto. Alcobendas",
     "desc": "Alcobendas — OEP con plazas docentes (ESO/adultos)",
     "patterns": ["alcobendas"]},
    {"id": "T-17", "name": "Ayto. Tres Cantos",
     "desc": "Tres Cantos — convocatorias de empleo público",
     "patterns": ["tres cantos"]},
    {"id": "T-18", "name": "Ayto. Las Rozas",
     "desc": "Las Rozas — convocatorias en plazo",
     "patterns": ["las rozas"]},
    {"id": "T-19", "name": "Ayto. Pozuelo",
     "desc": "Pozuelo de Alarcón — Patronato de Cultura (música, plástica)",
     "patterns": ["pozuelo de alarcon", "pozuelo"]},
    {"id": "T-20", "name": "Ayto. Majadahonda",
     "desc": "Majadahonda — profesor de pintura/música/cerámica",
     "patterns": ["majadahonda"]},
    {"id": "T-21", "name": "Ayto. Boadilla",
     "desc": "Boadilla del Monte — eAdmin estándar",
     "patterns": ["boadilla del monte", "boadilla"]},
    {"id": "T-22", "name": "Ayto. SS Reyes",
     "desc": "San Sebastián de los Reyes",
     "patterns": ["san sebastian de los reyes", "ss reyes", "ssreyes"]},
    # --- Universidades de la zona (contexto ELE/idiomas) ---
    {"id": "T-23", "name": "Universidad Nebrija",
     "desc": "Nebrija — CEHI, máster ELE, vacantes regulares",
     "patterns": ["universidad nebrija", "nebrija"]},
    {"id": "T-24", "name": "UCM",
     "desc": "Universidad Complutense de Madrid — empleo PDI",
     "patterns": ["complutense", "ucm "]},
    {"id": "T-25", "name": "UC3M",
     "desc": "Universidad Carlos III — Centro de Idiomas",
     "patterns": ["uc3m", "carlos iii"]},
]

_WATCHLIST_RECENCY_DAYS = 90

# ---------------------------------------------------------------------------
# Enricher (Sonnet 4.6 + tool use) — prompt docente portado del fork
# ---------------------------------------------------------------------------
_ENRICHER_SYSTEM_PROMPT = """Eres un asistente que extrae datos estructurados de convocatorias de empleo docente en España.

Tu trabajo: recibir el dato bruto de una convocatoria y devolver un JSON con los campos clave. Puedes (y debes, cuando los datos no estén en el resumen recibido) usar la tool `fetch_url` para descargar el cuerpo del boletín o el PDF de bases.

PERFIL OBJETIVO (para evaluar `is_relevant`):
- Cuerpo 0590 PES (Profesores de Enseñanza Secundaria), especialidad 005 Geografía e Historia.
- Cuerpo 0592 EOI (Escuelas Oficiales de Idiomas), especialidad Español para Extranjeros / ELE.
- Bolsas/listas extraordinarias e interinidades de las dos anteriores.
- Concursos de traslados con cupo en Madrid para esas especialidades.
- Lectorados (AECID-MAEC), auxiliares de conversación (MEFP/Profex 2), profesores visitantes y Fulbright FLTA.
- Plazas docentes en colegios privados/concertados de Madrid o academias/universidades ELE.

CRITERIOS PARA `is_relevant`:
- TRUE → la convocatoria/oferta encaja con uno de los puntos del perfil.
- FALSE → falsos positivos típicos:
    * Cuerpo 0597 (Maestros, infantil/primaria).
    * Universidad: PDI, Ayudante Doctor, Profesor Contratado, Titular, Asociado.
    * Otras especialidades de secundaria sin solapamiento (Matemáticas, Física, etc.).
    * Roles "bilingüe" donde se exige impartir TODO en inglés (el perfil tiene C1 sólido pero no es bilingüe nativo).
    * Nombramientos / ceses individuales sin plazas nuevas.
- En la duda, prioriza FALSE — el sistema reduce ruido eliminando items con is_relevant=false.

CRITERIOS PARA `process_type`:
- "oposicion" → proceso selectivo / pruebas selectivas / concurso-oposición de acceso libre
- "bolsa" → bolsa de empleo, lista extraordinaria, interinidad estructurada
- "concurso_traslados" → concurso de traslados / concurso de méritos entre funcionarios
- "interinaje" → nombramiento de interino / sustitución concreta
- "temporal" → contrato temporal puntual no incluido en bolsa
- "lectorado" → lectorado AECID/Fulbright/MAEUEC/Cervantes
- "auxiliar" → auxiliar de conversación
- "privada" → vacante en colegio privado/concertado
- "ele" → vacante en academia/universidad/centro ELE
- "otro" → cualquier otro caso

CRITERIOS PARA `fase`:
- "convocatoria" → publicación inicial con plazo de inscripción abierto
- "admitidos_provisional" / "admitidos_definitivo" → listas de admitidos
- "examen" → fechas/sedes del ejercicio
- "calificacion" → resultados de un ejercicio o calificación final
- "propuesta_nombramiento" → resolución de adjudicación
- "otro" → cualquier otro estado intermedio

REGLAS DE EXTRACCIÓN:
- Fechas en formato `YYYY-MM-DD`. Si solo conoces el mes y año, deja `null`.
- `plazas`: solo el TOTAL de plazas convocadas; si no aparece, `null`.
- `tasas_eur`: tasa de inscripción base en euros (no descuentos ni reducciones).
- `url_bases`: URL al PDF/HTML con las bases completas (a veces es un anexo distinto del que recibes).
- `requisitos_clave`: lista corta (≤4) de requisitos imprescindibles (titulación específica, idiomas, experiencia mínima). No copies todo el listado del BOE — solo lo más diferenciador.
- `next_action`: una frase ≤140 chars con la acción inmediata que el usuario debe tomar (ej. "Presentar instancia online en sede.educacion.gob.es antes del 15/05/2026").
- `summary`: ~200 caracteres en estilo telegrama, factual, sin frases introductorias.
- `confidence`: 0..1 según lo seguro que estés del extracto general.
- Si un campo no es deducible con razonable certeza, devuélvelo como `null`. NO INVENTES NADA.

USO DE LA TOOL:
- Si el título y `raw_text` son suficientes para todos los campos pedidos, NO llames a la tool — responde directamente con el JSON.
- Si te falta algún dato clave (deadline, plazas, tasas, bases, especialidad concreta) y la URL principal está en dominio oficial, llámala una vez para inspeccionar el cuerpo.
- Como mucho 2 llamadas a tool por item. Después responde con lo que tengas.

FORMATO DE SALIDA OBLIGATORIO:
Responde SOLO con un bloque JSON válido (puedes envolverlo en ```json … ``` si quieres). Sin texto antes ni después. El JSON debe seguir este schema (todos los campos opcionales pueden ser null):

{
  "is_relevant": true|false,
  "relevance_reason": "string",
  "process_type": "oposicion|bolsa|concurso_traslados|interinaje|temporal|lectorado|auxiliar|privada|ele|otro",
  "summary": "string ~200 chars",
  "organismo": "string|null",
  "centro": "string|null",
  "plazas": int|null,
  "deadline_inscripcion": "YYYY-MM-DD|null",
  "fecha_publicacion_oficial": "YYYY-MM-DD|null",
  "tasas_eur": float|null,
  "url_bases": "string|null",
  "url_inscripcion": "string|null",
  "requisitos_clave": ["string", ...] | [],
  "fase": "convocatoria|admitidos_provisional|admitidos_definitivo|examen|calificacion|propuesta_nombramiento|otro",
  "next_action": "string|null",
  "confidence": 0.0..1.0
}"""

# Keywords para `_extract_relevant_snippets` del enricher v2 del core (el fork
# usaba enricher v1 sin esto). El matcher hace `.lower()` SIN quitar acentos, por
# eso se incluyen variantes acentuadas Y sin acentuar.
_ENRICHER_SNIPPET_KEYWORDS_HIGH = [
    "geografía e historia", "geografia e historia",
    "especialidad 005", "cuerpo 0590", "cuerpo 0592",
    "escuelas oficiales de idiomas", "escuela oficial de idiomas",
    "español para extranjeros", "espanol para extranjeros",
    "español como lengua extranjera", "espanol como lengua extranjera",
    "profesor de español", "profesor de espanol",
    "lectorado", "lectorados",
    "auxiliar de conversación", "auxiliar de conversacion",
    "profesor visitante", "profesores visitantes",
]
_ENRICHER_SNIPPET_KEYWORDS_LOW = [
    "profesor", "profesorado", "docente", "secundaria",
    "interinidad", "interino", "lista extraordinaria",
    "bolsa de empleo", "bolsa de trabajo",
    "concurso de traslados", "concurso de méritos", "concurso de meritos",
    "consejería de educación", "consejeria de educacion",
    "proceso selectivo", "oposición", "oposicion",
]

# Whitelist estricta de hostnames permitidos en `fetch_url` (anti-SSRF). Del fork.
_ENRICHER_ALLOWED_FETCH_HOSTS = frozenset({
    # BOE
    "boe.es", "www.boe.es",
    # BOCM
    "bocm.es", "www.bocm.es",
    # Comunidad de Madrid
    "comunidad.madrid", "www.comunidad.madrid",
    "sede.comunidad.madrid", "transparencia.comunidad.madrid",
    # AECID / Cooperación Española (lectorados)
    "aecid.es", "www.aecid.es",
    # Instituto Cervantes
    "cervantes.es", "www.cervantes.es",
    "cervantes.sede.gob.es", "hispanismo.cervantes.es",
    # Portales ELE (agregadores de ofertas)
    "profesoresdeele.org", "www.profesoresdeele.org",
    # Ministerio de Educación, FP y Deportes
    "educacionfpydeportes.gob.es", "www.educacionfpydeportes.gob.es",
    "educacion.gob.es", "www.educacion.gob.es",
    # Sindicatos (públicos, sin login)
    "anpemadrid.es", "www.anpemadrid.es",
    "csif.es", "www.csif.es",
})

# ---------------------------------------------------------------------------
# Diff summarizer — solo se dispara en snapshots/hash-watchers (con boe+bocm
# activos no se usa), pero el campo es obligatorio en Profile.
# ---------------------------------------------------------------------------
_DIFF_SYSTEM_PROMPT = (
    "Eres analista de convocatorias de empleo docente. Recibes el unified diff "
    "entre dos snapshots de la misma página oficial (cuerpo HTML extraído como "
    "texto plano).\n\n"
    "Tu tarea:\n"
    "1. Clasifica el cambio como SUSTANTIVO (información nueva relevante para un "
    "opositor/interino docente: nueva fase publicada, nuevo plazo, lista de "
    "admitidos, adjudicación de destinos, calendario, examen, resolución, cambio "
    "de tribunal, cambio en plazas/especialidades, modificación de fechas "
    "relevantes…) o COSMÉTICO (solo cambia el timestamp \"Última actualización\", "
    "formato, espacios en blanco, redacción equivalente sin información nueva).\n"
    "2. Si es SUSTANTIVO: redacta UNA frase ≤100 caracteres explicando qué ha "
    "cambiado, en español neutro y factual.\n"
    "3. Si es COSMÉTICO: deja el resumen vacío.\n\n"
    "Devuelve EXACTAMENTE este JSON sin texto adicional ni markdown:\n"
    "{\"sustantivo\": true|false, \"resumen\": \"...\"}"
)

# Departamentos BOE cuyo cuerpo HTML merece inspección (del BOE del fork).
_BOE_DEPT_KEYWORDS = [
    "ministerio de educacion",
    "ministerio de asuntos exteriores",  # AECID lectorados
    "ministerio de la presidencia",      # auxiliares conversación
    "comunidad de madrid",
    "consejeria de educacion",
    "comunidades autonomas",
    "administracion local",
    "universidad",
    "instituto cervantes",
    "agencia espanola de cooperacion",
    "aecid",
]


# ---------------------------------------------------------------------------
# Perfil docente
# ---------------------------------------------------------------------------
PERFIL_DOCENCIA = Profile(
    slug="docencia-secundaria",
    display_name="Vigilancia Empleo Docente",
    dashboard_url="https://tragabytes.github.io/vigia-docencia/",
    test_message="✅ vigia-docencia: conexión OK",
    strong_patterns=tuple(_STRONG_PATTERNS),
    weak_context_patterns=tuple(_WEAK_CONTEXT_PATTERNS),
    false_positive_patterns=tuple(_FALSE_POSITIVE_PATTERNS),
    fast_keywords=tuple(_FAST_KEYWORDS),
    category_hints=_CATEGORY_HINTS,
    watchlist_orgs=tuple(_WATCHLIST_ORGS),
    watchlist_recency_days=_WATCHLIST_RECENCY_DAYS,
    enricher_system_prompt=_ENRICHER_SYSTEM_PROMPT,
    enricher_snippet_keywords_high=tuple(_ENRICHER_SNIPPET_KEYWORDS_HIGH),
    enricher_snippet_keywords_low=tuple(_ENRICHER_SNIPPET_KEYWORDS_LOW),
    enricher_allowed_fetch_hosts=_ENRICHER_ALLOWED_FETCH_HOSTS,
    diff_system_prompt=_DIFF_SYSTEM_PROMPT,
    sources_enabled=("boe", "bocm", "profesoresdeele"),
    # El BOCM del fork es una reescritura RSS → fuente custom que sobrescribe la
    # del core (clave "bocm"). El BOE se reusa del core, parametrizado abajo.
    # profesoresdeele: feed RSS de ofertas ELE (categoría "Ofertas de trabajo").
    extra_sources={
        "bocm": BOCMSource,
        "profesoresdeele": ProfesoresDeEleSource,
    },
    source_params={
        "boe": {
            "dept_keywords": _BOE_DEPT_KEYWORDS,
            "fetch_pdfs": False,   # el BOE docente no baja anexos PDF (igual que el fork)
            "timeout_api": 45,
            "timeout_body": 30,
        },
    },
    valid_process_types=(
        "oposicion", "bolsa", "concurso_traslados", "interinaje", "temporal",
        "lectorado", "auxiliar", "privada", "ele", "otro",
    ),
)
