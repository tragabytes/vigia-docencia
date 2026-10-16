# Tareas — 001 Encontrar nuevas fuentes de empleo docente

Spec: [`spec.md`](spec.md). Respuestas de Laureano del 16/10/2026 en la spec.

## H1 · Cuánto se está perdiendo
- [x] Buscar a mano ofertas reales del perfil de las últimas 4 semanas (mín. 20): públicas, privadas en la Comunidad de Madrid, online y ELE
- [x] Anotar de cada una dónde apareció (todas las webs) y la fecha
- [x] Cruzar con la base real de docencia (rama `state`): ¿la vio el bot?
- [x] Resultado: tabla [`cobertura.md`](cobertura.md) — **el bot vio 0 de 25** (11 colegios, 14 ELE; 0 públicas abiertas)
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

## Aparecido al ejecutar (16/10)
- **Límite de gasto de la API agotado a finales de septiembre** («You have reached your specified API usage limits… 2026-10-01»). Del 22 al 29/09 el enricher no resumió nada: 15 items de docencia y 1 de enfermería siguen sin enriquecer, y por no estar marcados «no relevantes» probablemente llegaron a Telegram sin filtrar. Docencia no tiene workflow de mantenimiento que los reintente. **Afecta a H3**: más fuentes = más llamadas. Pendiente: decidir con Laureano el límite y reintentar esos items.

- **Etiqueta errónea en el perfil**: la watchlist dice «EOI (especialidad 008)», pero en Madrid Español para extranjeros es la **0592-006** (la 008 es Francés). No afecta a la búsqueda (se busca «cuerpo 0592» sin especialidad); sí conviene corregir la etiqueta y mirar si «cuerpo 0592» deja pasar EOI de otros idiomas.
- **Las listas extraordinarias de interinos de Madrid no pasan por el BOCM**: se publican solo en la sede y en la página de Novedades de Recursos Humanos de comunidad.madrid. Candidata fuerte para H2.

## Cierre
- [ ] Repetir la medida de H1 con las fuentes nuevas: «X de N» antes y después
- [ ] Suite del bot y del núcleo en verde; dry-run del CI
- [ ] Primer daily real de cada fuente vigilado (`MANTENIMIENTO.md` §3 del núcleo)
- [ ] Lo aprendido, aquí; `RELEVO.md` al día
