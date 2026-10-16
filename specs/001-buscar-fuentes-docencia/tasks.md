# Tareas — 001 Encontrar nuevas fuentes de empleo docente

Spec: [`spec.md`](spec.md). Respuestas de Laureano del 16/10/2026 en la spec.

## H1 · Cuánto se está perdiendo
- [ ] Buscar a mano ofertas reales del perfil de las últimas 4 semanas (mín. 20): públicas, privadas en la Comunidad de Madrid, online y ELE
- [ ] Anotar de cada una dónde apareció (todas las webs) y la fecha
- [ ] Cruzar con la base real de docencia (rama `state`): ¿la vio el bot?
- [ ] Resultado: tabla `cobertura.md` en esta carpeta, con «el bot vio X de N» por mercado
- [ ] **Parar y validar con Laureano**: ¿las ofertas encontradas son las que le interesan a su hermano?

## H2 · Catálogo comprobado
Cada candidata se mira hoy contra la web real (sin esquivar bloqueos, sin cuenta) y acaba con veredicto, prueba, valor y coste en `catalogo.md`. Por tandas:
- [ ] **Agregadores del privado**: Colejobs, Colegios.es, Edutalent, Trabajos.com, ETT con sección de educación, Empléate (SEPE)
- [ ] **Con clave**: InfoJobs (API), Jooble (API), Indeed (RSS), LinkedIn (búsqueda de invitado). Para cada una: qué clave, cómo se saca, qué volumen da para «profesor historia / secundaria / ELE» en Madrid
- [ ] **Plataformas de empleo de grupos de colegios**: Inspired, SEK (Teamtailor), Brains (Factorial), Colegios RC / Highlands (SAP SuccessFactors: el núcleo ya tiene una fuente para esa plataforma), y otros grupos de la Comunidad que salgan de H1
- [ ] **Colegios sin listado de vacantes** (solo «trabaja con nosotros»): ¿merece la pena vigilar cambios en la página?
- [ ] **ELE**: TodoELE, Hispanismo Cervantes, sede del Instituto Cervantes, Nebrija, International House, academias que salgan de H1
- [ ] **Online**: academias ELE en remoto (Lingoda y similares); marketplaces de tutores (italki, Preply, Superprof) → *solo recordatorio*
- [ ] **Público además de BOE/BOCM**: profesorado interino y listas extraordinarias de comunidad.madrid, administracion.gob.es, ayuntamientos (adultos, música): ¿lo cubre ya el BOCM?
- [ ] **Sindicatos**: canales de Telegram (¿se leen por la versión web pública `t.me/s/…` sin cuenta?), webs de ANPE, CSIF, UGT, CCOO, STEM: ¿traen convocatorias concretas antes que el BOCM?
- [ ] **Recordatorios**: lectorados y programas con fecha (AECID, Fulbright, auxiliares, Cervantes), PADI, Talento ECM, FSIE
- [ ] Buscar fuentes nuevas que no estén en el informe (las que salgan de H1 y búsqueda abierta)
- [ ] Orden de construcción por valor / coste, con las claves que hay que sacar
- [ ] **Parar y validar con Laureano**: orden de construcción y claves

## H3 · Construir (una fuente por PR, en el orden validado)
Por cada fuente:
- [ ] (se rellena al cerrar H2)

Cada una lleva, antes de publicar:
- prueba contra la web real (qué habría avisado);
- simulación con copia de la base real: sin avalancha y sin repetidas;
- tests: el probe da error si lee 0; ofertas reales fuera de alcance no pasan el extractor; dos lecturas seguidas no dan avisos nuevos.

- [ ] Actualizar la regla 1 del `CLAUDE.md` de docencia con el alcance nuevo (Comunidad de Madrid y online)

## H4 · Lo que no se puede vigilar
- [ ] Decidir con Laureano la forma (avisos por fecha, lista fija en el dashboard…) cuando H2 diga cuántas son

## Cierre
- [ ] Repetir la medida de H1 con las fuentes nuevas: «X de N» antes y después
- [ ] Suite del bot y del núcleo en verde; dry-run del CI
- [ ] Primer daily real de cada fuente vigilado (`MANTENIMIENTO.md` §3 del núcleo)
- [ ] Lo aprendido, aquí; `RELEVO.md` al día
