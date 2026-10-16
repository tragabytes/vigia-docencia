# H2 — Catálogo comprobado de fuentes (16/10/2026)

Cada candidata se comprobó hoy contra la web real con peticiones normales, sin cuenta y sin esquivar bloqueos. **No probado**: cómo responden desde la IP de GitHub Actions (EE. UU.); se verá en la prueba de cada fuente antes de publicarla.

Veredictos: **construir** · **con clave** (hace falta que alguien saque una clave) · **recordatorio** (no se vigila; se avisa por fecha) · **no** (con el porqué).

## Orden de construcción propuesto

Ordenado por *valor / coste*. Una fuente por PR (regla 2 de docencia). «Núcleo» = lector genérico que sirve a cualquier bot (va a vigia-core); «docencia» = propio de este bot.

| # | Fuente | Qué trae | Valor | Coste | Dónde |
|---|---|---|---|---|---|
| 1 | **TodoELE** | ELE en todo el mundo (EE. UU., Emiratos, Reino Unido, China, España) | **~13 ofertas nuevas por semana**, casi todas del perfil | pequeño | docencia |
| 2 | **Colejobs** | Colegios privados y concertados (81 de 94 ofertas activas son de Madrid) | 1-2 del perfil al mes; fecha y enlace fijos | pequeño | docencia |
| 3 | **Colegios.es** | Colegios (anónimos), con RSS | ~2 al mes con «historia» | pequeño | docencia |
| 4 | **Novedades de Recursos Humanos de Educación (comunidad.madrid)** | Listados de listas extraordinarias, adjudicaciones, listas ordinarias: lo que **no** pasa por el BOCM | 15-60 novedades al mes; la especialidad va dentro del PDF | pequeño (medio si se abre el PDF) | docencia |
| 5 | **Colegios RC / Highlands** | Colegios bilingües de Madrid | pocas, con fecha fiable | **casi nulo**: el lector SuccessFactors del núcleo ya sirve, basta añadir la dirección | perfil de docencia |
| 6 | **Workday: Colegios CEU + ISP** (Laude, Aravaca, Fontenebro, St George, Kensington…) | Los grupos que más Historia publicaron en H1; CEU tiene hoy una bolsa de Sociales/Humanidades en Madrid | alto para el perfil | medio (lector nuevo, sirve para los dos) | núcleo |
| 7 | **Inspired** (San Patricio, Mirabal, Kensington, British School…) | 36 ofertas en Madrid; hoy Historia solo en Murcia y Barcelona | medio | pequeño-medio (variante del lector SuccessFactors) | núcleo |
| 8 | **SEK** (Teamtailor, RSS público) | ~12 ofertas en Madrid | bajo-medio | pequeño (lector Teamtailor reutilizable) | núcleo |
| 9 | **TES** | ELE en colegios del Reino Unido e internacionales; 109 activas | medio (muchas piden la habilitación británica o permiso de trabajo) | pequeño-medio | docencia |
| 10 | **Instituto Cervantes, sede electrónica** | Convocatorias de profesores | 1-2 al año | pequeño | docencia |

Más adelante, prioridad baja: **Brains** (Factorial, sin fecha), **Cognita** (Colegio Europeo de Madrid; API con permiso temporal), **Maristas Ibérica** (sin enlace ni fecha).

## Con clave (decisión de Laureano)

| Fuente | Qué aportaría | Pega | Cómo se saca la clave |
|---|---|---|---|
| **InfoJobs (API oficial)** | Donde publican Gredos San Diego y muchos colegios; la web bloquea, la API no | Las condiciones prohíben «almacenar o exportar» sus datos y crear «otro portal de empleo»: el bot guardaría lo mínimo (título y enlace). Zona gris | Cuenta de candidato en infojobs.net → developer.infojobs.net → registrar una aplicación → guardar `client_id` y `client_secret` como secrets del repo |
| **Jooble (API)** | Agregador: academias pequeñas de Madrid, CEU, ISP | Detrás de Cloudflare (403 hoy); campos y límites sin verificar; con 6 y 7 construidos aporta poco | Formulario en jooble.org/api/about (nombre, cargo, email, web, teléfono) → clave por email |
| **LinkedIn (búsqueda pública)** | Alguna oferta que no está en otro sitio (Kensington) | Sus condiciones prohíben leerlo así y suele bloquear IPs de servidores | No hay clave. Solo como prueba en rama aparte, con criterio de abandono escrito (fuera si bloquea o pide login 3 días seguidos) |

## Recordatorios (no se vigilan)

| Qué | Cuándo | Nota |
|---|---|---|
| **Lista extraordinaria 0592-006 Español en EOI (Madrid)** | **abierta ya** (desde el 19/11/2024) | Se puede pedir hoy. La de 0590-005 Geografía e Historia **no** tiene lista extraordinaria convocada |
| **Profesores visitantes EE. UU. y Canadá** | principios de **noviembre** (la de 2027/28, previsiblemente en 2-3 semanas) | Sale en el BOE: el bot ya la caza |
| **Lectorados MAEC-AECID** | finales de **diciembre**, plazo en enero | Sale en el BOE: el bot ya la caza |
| **Auxiliares de conversación (MEFP)** | plazo en **junio** | Sale en el BOE |
| **Fulbright, lectores de español** | de mediados de **septiembre** a mediados de octubre | **No sale en el BOE**: recordatorio el 1 de septiembre |
| **PADI** (sustituciones de Madrid) | — | Aplicación con captcha: solo recordar entrar |
| **Talento ECM** (Escuelas Católicas) | — | Exige login: recordar mantener el CV |
| **Bolsa de FSIE** (concertada) | — | Solo afiliados |

## Descartadas

- **Sindicatos** (Telegram de ANPE, CSIF, STEM…; webs con RSS): se leen, pero **van detrás** de la Consejería y meten mucho ruido.
- **administracion.gob.es**: recoge lo que ya está en BOE/BOCM.
- **Página de profesorado interino** y **página de listas extraordinarias**: las cubren el n.º 4 y el BOCM.
- **Hispanismo Cervantes / cervantes.es**: en mantenimiento.
- **Nebrija**: ofertas sin enlace ni fecha, ninguna de ELE. **International House, Edinumen, Difusión, ELEInternacional, FEDELE**: sin ofertas de español. **Lingoda**: solo formulario.
- **FORMESPA**: el archivo pide cuenta; haría falta un buzón suscrito.
- **Jobsora, Jobijoba, Edutalent, Trabajos.com, Adecco/Randstad, Remotive, RemoteOK**: ruido (clases particulares, anuncios reindexados) o sin volumen. **Indeed, Empléate (SEPE)**: bloquean o exigen navegador.
- **Gredos San Diego**: su XML tiene 5 ofertas sin fecha; publica de verdad en InfoJobs.
- **Fomento, Salesianos, Los Sauces**: bloquean. **Talento ECM, Liceo Europeo**: login. **Alegra, Alarcón, Kolbe, Logos, Balder, Zola, Engage, Thames, Veritas, Schoenstatt, Escolapios**: sin listado de ofertas. **SAFA**: fuera de Madrid.

## A tener en cuenta al construir

- **Gasto de la API**: TodoELE sola son ~50 ofertas al mes que el enricher resume. En septiembre se agotó el límite de gasto (ver `tasks.md`). Antes de H3 hay que decidir el límite.
- **Ruido de clases particulares** (Apprentus, Tusclasesparticulares, Superprof): ninguna fuente del orden propuesto los trae; si algún día se añade un agregador, filtrarlos por empleador.
- **Sin fecha de publicación** (TodoELE, Brains): el enlace propio evita repetir avisos; la fecha será la del día en que el bot la ve. TodoELE publica por tandas de madrugada.
- **Corrección a H1**: las *convocatorias* de listas extraordinarias de Madrid **sí** salen en el BOCM; lo que solo sale en comunidad.madrid son los *listados de admitidos* y otras novedades (n.º 4).
