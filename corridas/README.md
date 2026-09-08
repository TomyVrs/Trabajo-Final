# corridas/

Este trabajo incluye **3 corridas reales** del agente contra la API de
Anthropic (modelo `claude-sonnet-4-6`), una por cada mes analizado. Ver
`manifest.json` para el resumen estructurado.

| # | Mes | Carpeta |
|---|---|---|
| 1 | 2025-11 | `corrida_1_2025-11/` |
| 2 | 2026-03 | `corrida_2_2026-03/` |
| 3 | 2026-06 | `corrida_3_2026-06/` |

Cada carpeta contiene, por separado:

- **`entrada.md`** — qué se le mandó al modelo (system prompt, user prompt
  con el mes y los datos, modelo y parámetros usados), y cómo regenerar
  los datos de entrada desde la herramienta.
- **`salida.json`** — la respuesta real del modelo: uso de tokens,
  duración, y el JSON estructurado del diagnóstico.
- **`fecha.txt`** — fecha y hora exacta (ISO 8601) en que se ejecutó la
  corrida.
- **`corrida.json`** — el mismo contenido consolidado en un solo archivo,
  por si resulta más cómodo de leer de una vez.

Los datos de entrada y salida están **anonimizados** por confidencialidad
(nombres de canal reemplazados por `Canal-XXX`, montos escalados). Ver
`../README.md` y `../DECISIONES.md` (iteración 7) para el detalle.
