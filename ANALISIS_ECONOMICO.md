# Análisis económico

## Costo por corrida (datos reales, no estimados)

De las 3 corridas finales guardadas en `corridas/`:

| Corrida | Mes | Tokens entrada | Tokens salida |
|---|---|---|---|
| 1 | 2025-11 (52 canales) | 12.473 | 2.726 |
| 2 | 2026-03 (22 canales) | 10.283 | 1.888 |
| 3 | 2026-06 (28 canales) | 11.228 | 1.746 |
| **Promedio** | | **11.328** | **2.120** |

Precios oficiales verificados en la documentación de Anthropic
([docs.claude.com/en/docs/about-claude/pricing](https://docs.claude.com/en/docs/about-claude/pricing)):

| Modelo | Input | Output |
|---|---|---|
| Claude Sonnet 4.6 | $3 / MTok | $15 / MTok |
| Claude Haiku 4.5 | $1 / MTok | $5 / MTok |

**Costo por corrida, con los tokens reales de este sistema:**

**Fórmula:** `costo_usd = (tokens_input × precio_input / 1.000.000) + (tokens_output × precio_output / 1.000.000)`

Aritmética verificable, con el promedio de tokens de las 3 corridas
(11.328 input, 2.120 output):

- **Sonnet 4.6:** `(11.328 × 3 / 1.000.000) + (2.120 × 15 / 1.000.000)`
  `= 0,033984 + 0,031800 = 0,065784` → **$0,0658**
- **Haiku 4.5:** `(11.328 × 1 / 1.000.000) + (2.120 × 5 / 1.000.000)`
  `= 0,011328 + 0,010600 = 0,021928` → **$0,0219**

| Modelo | Costo/corrida |
|---|---|
| Sonnet 4.6 | **$0,0658** |
| Haiku 4.5 | **$0,0219** |

## Proyección de costo en producción

**Frecuencia:** 1 corrida por mes (cadencia definida por el caso de uso:
diagnóstico mensual de canal, no un servicio con tráfico continuo).
**Horizonte:** se proyecta a 1 mes y a 1 año (12 corridas), por ser los
plazos relevantes para decidir presupuesto.

**Fórmula de proyección:** `costo_anual = costo_por_corrida × 12`

- Sonnet 4.6: `0,065784 × 12 = 0,789408` → **$0,79/año**
- Haiku 4.5: `0,021928 × 12 = 0,263136` → **$0,26/año**

| Cadencia | Sonnet 4.6 | Haiku 4.5 |
|---|---|---|
| Mensual (1 corrida) | $0,066 | $0,022 |
| Anual (12 corridas) | **$0,79** | **$0,26** |

**El costo es económicamente irrelevante en cualquiera de los dos modelos.**
Esto no es un accidente: es la consecuencia directa de una decisión de
arquitectura — la herramienta (`agregar_metricas_canal.py`) hace todo el
trabajo pesado (leer 12.000+ filas de SAP, agregar, calcular ratios) *antes*
de que el LLM vea un solo token. El modelo nunca procesa la base cruda,
solo un resumen ya comprimido (~20 canales, no 71). Si el agente leyera
la planilla completa en cada corrida, el costo por llamada sería
sensiblemente mayor y la elección de modelo importaría de verdad.

## Costo de desarrollo (siendo honestos con el proceso)

Durante la construcción se hicieron **10 llamadas reales** a la API (no
simuladas): la corrida truncada de la iteración 2, las tres corridas
truncadas por el problema del `metodo` verboso (iteración 3), las tres
corridas válidas pero con datos reales que luego se descartaron por
confidencialidad (iteración 6), y las tres corridas finales sobre datos
anonimizados (iteración 7, las que quedan en `corridas/`). Con tokens
promedio similares en las 10 llamadas, el costo total de todo el proceso
de prueba, error y re-trabajo por confidencialidad ronda **$0,65** — menos
de un dólar para construir, romper, arreglar y volver a construir el
sistema completo.

## Elección de modelo — criterio del curso: "el más chico que hace bien la tarea"

**Decisión: Haiku 4.5, con evidencia empírica — no solo argumento teórico.**

Se corrieron los mismos 3 meses con Claude Haiku 4.5
(`claude-haiku-4-5-20251001`), sobre los mismos datos anonimizados, y se
comparó contra las 3 corridas oficiales de Sonnet 4.6. El detalle completo
está en `corridas/comparacion_haiku_vs_sonnet/`. Resultados:

- **Costo real:** Haiku costó **68,1% menos** en promedio ($0,0210 vs.
  $0,0658 por corrida), medido con tokens reales de ambos modelos, no
  proyectado.
- **Calidad:** en los 3 meses, Haiku identificó los mismos canales
  prioritarios que Sonnet en el 87% de los casos (13 de 15 selecciones
  coinciden exactamente, incluyendo la categoría riesgo/oportunidad). Las
  2 diferencias observadas son elecciones igualmente defendibles con los
  datos disponibles, no errores de Haiku.
- **Formato:** las 3 corridas de Haiku devolvieron JSON válido, con el
  esquema completo y las restricciones del contrato respetadas sin
  excepciones.

Con esto, el criterio del curso queda satisfecho con **prueba verificable
de suficiencia y costo**, no solo con la lógica de que "la tarea es
mecánica": Haiku 4.5 hace el trabajo igual de bien, más barato, y hay
corridas reales guardadas que lo demuestran.
