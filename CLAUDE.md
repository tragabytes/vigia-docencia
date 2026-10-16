# CLAUDE.md — vigia-docencia

Bot de empleo **docente** sobre vigia: secundaria de **Geografía e Historia** y **ELE** (español para extranjeros). Cada día laborable busca convocatorias y ofertas, las resume con IA, avisa por Telegram y publica un dashboard (<https://tragabytes.github.io/vigia-docencia/>). Es un **repo fino**: el pipeline vive en [vigia-core](https://github.com/tragabytes/vigia-core), que se instala por etiqueta; aquí solo están el perfil y las fuentes propias.

| Fichero | Para qué |
|---|---|
| [`RELEVO.md`](RELEVO.md) | Estado y fuentes que faltan. **Punto de entrada** |
| [`specs/`](specs/) | Una carpeta por cada cosa nueva: `spec.md` (qué y por qué) y `tasks.md` (estado) |
| [vigia-core: `CLAUDE.md`](https://github.com/tragabytes/vigia-core/blob/main/CLAUDE.md) | Reglas del pipeline, comunes a todos los bots |
| [vigia-core: `DECISIONES.md`](https://github.com/tragabytes/vigia-core/blob/main/DECISIONES.md) | Decisiones tomadas en ausencia de Laureano, de todos los repos de vigia |
| [vigia-core: `MANTENIMIENTO.md`](https://github.com/tragabytes/vigia-core/blob/main/MANTENIMIENTO.md) | Ver producción, leer un run, publicar el núcleo, crear una fuente |
| `requirements.txt` | La versión del núcleo que usa este bot |
| `vigia_docencia/profile.py` | El perfil: patrones, prompts, fuentes activas |
| `vigia_docencia/sources/` | Fuentes propias: `bocm` (RSS; sustituye a la del núcleo) y `profesoresdeele` (RSS de ofertas ELE) |
| `web/` | El dashboard (copia del de vigia-enfermeria: un arreglo allí suele tocar aquí) |
| `tests/` | Tests del perfil y de las fuentes propias |
| [`historico/`](historico/) | El ROADMAP hasta octubre de 2026 |

## Reglas propias

1. **El alcance del perfil no se toca sin preguntar.** Cuerpo **0590, especialidad 005 (Geografía e Historia)** y **0592 (EOI / ELE)**, con bolsas, interinidades, traslados y lectorados. Se excluyen **a propósito** primaria (0597), profesorado universitario general (la universidad solo cuenta en contexto ELE) y puestos solo en inglés. **Ámbito**: la secundaria pública y los colegios privados, solo **Madrid**; ELE, lectorados y auxiliares, **cualquier lugar**.
2. **Una fuente nueva, ¿aquí o en el núcleo?** Genérica (un boletín de otra comunidad, un portal que sirve a varios perfiles) → núcleo. De perfil docente (ELE, colegios privados, canales sindicales) → aquí, como `Source` registrada en `extra_sources`, igual que `bocm.py`. **Una fuente por PR.**
3. **ProfesoresdeELE se filtra por los tags del feed, no por el extracto**: el extracto dispara falsos positivos del perfil (p. ej. «educación infantil» en colegios internacionales).
4. **Este repo nunca copia tests del núcleo** (regla 6 del núcleo). Tests en local: `python -m pytest tests --capture=no` con el núcleo instalado, o `PYTHONPATH=../vigia-core python -m pytest tests --capture=no`.
5. **Comprobar en producción, no en disco**: rama `state` (base de datos) y `gh-pages` (dashboard) de este repo.
