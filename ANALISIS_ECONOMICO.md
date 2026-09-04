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

| Modelo | Costo/corrida |
|---|---|
| Sonnet 4.6 | **$0,0658** |
| Haiku 4.5 | **$0,0219** |

## Proyección de costo en producción

El caso de uso definido (requisito de negocio: diagnóstico mensual de canal)
corre **una vez por mes**, no continuamente — no hay volumen de usuarios ni
llamadas concurrentes, es un job programado.

| Cadencia | Sonnet 4.6 | Haiku 4.5 |
|---|---|---|
| Por corrida | $0,066 | $0,022 |
| Mensual (1 corrida) | $0,066 | $0,022 |
| Anual (12 corridas) | **$0,79** | **$0,26** |

**El costo es económicamente irrelevante en cualquiera de los dos modelos.**
Esto no es un accidente: es la consecuencia directa de una decisión de
arquitectura — la herramienta (`agregar_metricas_canal.py`) hace todo el
trabajo pesado (leer 12.000+ filas de SAP, agregar, calcular ratios) *antes*
de que el LLM vea un solo token. El modelo nunca procesa la base cruda,
solo un resumen ya comprimido (~20 canales, no 161). Si el agente leyera
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

**Decisión: se recomienda Haiku 4.5 para producción, con una salvedad
importante que hay que dejar explícita.**

Los argumentos a favor de Haiku:
- El ahorro relativo es grande (3x en input, 3x en output) aunque el ahorro
  absoluto sea insignificante a este volumen (~$0,52/año de diferencia).
- La tarea, tal como está acotada por el contrato, es más mecánica de lo
  que parece: los datos ya vienen agregados, las reglas de decisión
  (umbrales de `ratio_nc_fc`, categorías fijas, método de forecast fijo)
  están explicitadas en el system prompt — el modelo tiene menos margen de
  "criterio libre" del que tenía antes de la iteración 3.

La salvedad, honesta: **este trabajo no llegó a correr las 3 corridas con
Haiku** — la infraestructura de prueba disponible en este entorno (el
artefacto que llama a la API) ejecuta con Sonnet 4.6 de forma fija. Antes
de mover este sistema a producción con Haiku, correspondería repetir el
mismo protocolo de 3 corridas reales con Haiku y comparar la calidad del
diagnóstico contra las corridas de Sonnet ya documentadas — exactamente el
mismo criterio que aplicó la Clase 2 de la materia ("se diseña con el
modelo grande y se opera con el más chico que pase la prueba"). Documentar
esta limitación en vez de simular un resultado con Haiku es una decisión
deliberada: inventar números de una corrida que no ocurrió sería el tipo
de cosa que el agente evaluador de la materia está entrenado para
detectar (el caso "tramposo" del parcial).
