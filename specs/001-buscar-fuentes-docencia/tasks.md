# Tareas — 001 Encontrar nuevas fuentes de empleo docente

Spec: [`spec.md`](spec.md). Respuestas de Laureano del 16/10/2026 en la spec.

## H1 · Cuánto se está perdiendo
- [x] Buscar a mano ofertas reales del perfil de las últimas 4 semanas (mín. 20): públicas, privadas en la Comunidad de Madrid, online y ELE
- [x] Anotar de cada una dónde apareció (todas las webs) y la fecha
- [x] Cruzar con la base real de docencia (rama `state`): ¿la vio el bot?
- [x] Resultado: tabla [`cobertura.md`](cobertura.md) — **el bot vio 0 de 25** (11 colegios, 14 ELE; 0 públicas abiertas)
- [x] **Parar y validar con Laureano**: validado el 16/10 (mixtas, parte en inglés y ELE en el extranjero valen; respuestas en la spec)

## H2 · Catálogo comprobado
Resultado: [`catalogo.md`](catalogo.md) (16/10).
- [x] Agregadores del privado
- [x] Con clave: InfoJobs, Jooble, Indeed, LinkedIn (pasos para sacar las claves en el catálogo)
- [x] Plataformas de empleo de grupos de colegios
- [x] Colegios sin listado de vacantes (ninguno tiene listado real)
- [x] ELE
- [x] Online (marketplaces → recordatorio; Lingoda solo formulario)
- [x] Público además de BOE/BOCM (→ Novedades de Recursos Humanos)
- [x] Sindicatos (descartados: van detrás de la Consejería)
- [x] Recordatorios
- [x] Fuentes nuevas fuera del informe (TES, Workday CEU/ISP, Cognita, Maristas Ibérica)
- [x] Orden de construcción por valor / coste
- [x] **Parar y validar con Laureano** (16/10): «adelante con todo»; Laureano sube el límite de gasto de la API; InfoJobs queda pendiente (ver `RELEVO.md`); Jooble y LinkedIn fuera

## H3 · Construir (una fuente por PR, en el orden validado)
- [x] Paso 0: perfil con el alcance del 16/10 (el extractor tiraba 11 de 15 ofertas reales) — PR #32
- [x] 1 TodoELE — primer día: 1 aviso (simulado); 64 ofertas leídas
- [ ] 2 Colejobs
- [ ] 3 Colegios.es
- [ ] 4 Novedades de Recursos Humanos (comunidad.madrid)
- [ ] 5 Colegios RC / Highlands (lector SuccessFactors del núcleo)
- [ ] 6 Workday: CEU + ISP (núcleo)
- [ ] 7 Inspired (núcleo)
- [ ] 8 SEK / Teamtailor (núcleo)
- [ ] 9 TES
- [ ] 10 Instituto Cervantes

Por cada fuente:

Cada una lleva, antes de publicar:
- prueba contra la web real (qué habría avisado);
- simulación con copia de la base real: sin avalancha y sin repetidas;
- tests: el probe da error si lee 0; ofertas reales fuera de alcance no pasan el extractor; dos lecturas seguidas no dan avisos nuevos.

- [x] Actualizar la regla 1 del `CLAUDE.md` de docencia con el alcance nuevo (Comunidad de Madrid y online) — PR #32

## H4 · Lo que no se puede vigilar
- [ ] Decidir con Laureano la forma (avisos por fecha, lista fija en el dashboard…) cuando H2 diga cuántas son

## Aparecido al ejecutar (16/10)
- **Límite de gasto de la API agotado a finales de septiembre** («You have reached your specified API usage limits… 2026-10-01»). Del 22 al 29/09 el enricher no resumió nada: 15 items de docencia y 1 de enfermería siguen sin enriquecer, y por no estar marcados «no relevantes» probablemente llegaron a Telegram sin filtrar. Docencia no tiene workflow de mantenimiento que los reintente. **Afecta a H3**: más fuentes = más llamadas. Pendiente: decidir con Laureano el límite y reintentar esos items.

- **Etiqueta errónea en el perfil**: la watchlist dice «EOI (especialidad 008)», pero en Madrid Español para extranjeros es la **0592-006** (la 008 es Francés). No afecta a la búsqueda (se busca «cuerpo 0592» sin especialidad); sí conviene corregir la etiqueta y mirar si «cuerpo 0592» deja pasar EOI de otros idiomas.
- **Los listados de las listas extraordinarias de Madrid no pasan por el BOCM** (las convocatorias sí): salen en Novedades de Recursos Humanos de comunidad.madrid. N.º 4 del catálogo.

## Cierre
- [ ] Repetir la medida de H1 con las fuentes nuevas: «X de N» antes y después
- [ ] Suite del bot y del núcleo en verde; dry-run del CI
- [ ] Primer daily real de cada fuente vigilado (`MANTENIMIENTO.md` §3 del núcleo)
- [ ] Lo aprendido, aquí; `RELEVO.md` al día
