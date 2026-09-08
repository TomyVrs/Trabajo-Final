# Comparación real: Sonnet 4.6 vs. Haiku 4.5

Esta carpeta contiene 3 corridas reales adicionales, hechas con
**Claude Haiku 4.5** (`claude-haiku-4-5-20251001`), sobre los mismos 3
meses y los mismos datos (ya anonimizados) que las corridas oficiales con
Sonnet 4.6 en `../corrida_1_2025-11/`, `../corrida_2_2026-03/` y
`../corrida_3_2026-06/`. El objetivo es responder con evidencia, no con
criterio teórico, la pregunta del requisito 5: ¿alcanza el modelo más
chico para esta tarea?

## Costo real (tokens reales de ambas corridas, mismo input)

| Mes | Sonnet $ | Haiku $ | Ahorro |
|---|---|---|---|
| 2025-11 | 0,0783 | 0,0228 | 70,9% |
| 2026-03 | 0,0592 | 0,0191 | 67,7% |
| 2026-06 | 0,0599 | 0,0210 | 64,9% |
| **Promedio** | **0,0658** | **0,0210** | **68,1%** |

(Nota: el ahorro real medido, 68%, es incluso mayor al ~66% proyectado en
`ANALISIS_ECONOMICO.md` antes de correr Haiku — la proyección basada en
precios de lista resultó conservadora.)

## Calidad: ¿eligió los mismos canales?

Para cada mes, comparamos el conjunto de `canales_prioritarios` (con su
`categoria`) entre Sonnet y Haiku:

**2025-11** — coincidencia total: **5 de 5 canales, mismas categorías**
(Canal-004 riesgo, Canal-003 riesgo, Canal-005 riesgo, Canal-006
oportunidad, Canal-001 oportunidad, en ambos modelos).

**2026-03** — coincidencia: **4 de 5 canales, mismas categorías**
(Canal-001 riesgo, Canal-002 riesgo, Canal-056 riesgo, Canal-006
oportunidad, en ambos). Difieren solo en el 5° canal: Sonnet eligió
Canal-005 (riesgo), Haiku eligió Canal-004 (riesgo) — ambos son
selecciones defendibles con los datos disponibles, no un error de Haiku.

**2026-06** — coincidencia: **4 de 5 canales, mismas categorías**
(Canal-064, Canal-053, Canal-002 como riesgo, y una oportunidad, en
ambos). Difieren en cuál canal marcan como "oportunidad" (Sonnet:
Canal-006; Haiku: Canal-001) — de nuevo, ambos son elecciones razonables
sobre datos reales, no un desacierto.

**Formato:** las 3 corridas de Haiku devolvieron JSON válido, respetando
el esquema completo, el tope de 5 canales / 3 forecasts, y el método fijo
de forecast — sin excepciones ni errores de estructura.

## Conclusión (reemplaza la salvedad de "no se probó" en ANALISIS_ECONOMICO.md)

Con datos reales de las 3 corridas: **Haiku 4.5 iguala o casi iguala el
criterio de Sonnet 4.6** en la selección de canales prioritarios (13 de
15 selecciones coinciden exactamente entre los 3 meses), cumple el
formato del contrato sin fallas, y cuesta **68% menos** en la práctica.
Para esta tarea — datos ya agregados, reglas de decisión explícitas en el
contrato, salida estructurada — el criterio del curso ("el más chico que
hace bien la tarea") queda satisfecho con evidencia empírica, no solo con
argumento teórico: **se recomienda Haiku 4.5 para producción.**
