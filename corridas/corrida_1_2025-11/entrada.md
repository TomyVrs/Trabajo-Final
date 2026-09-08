# Entrada — corrida 1 (2025-11)

## System prompt
Usado tal cual está en `../../prompts/system_prompt.md` (sin cambios
respecto a la última iteración documentada en DECISIONES.md).

## User prompt (plantilla)
Usado tal cual está en `../../prompts/user_prompt.md`, con:
- `{MES}` = `2025-11`
- `{DATOS_HERRAMIENTA}` = contenido completo (minificado) de
  `../../herramienta/salidas/metricas_2025-11.json`

## Cómo regenerar estos datos de entrada
```
python3 agregar_metricas_canal.py --mes 2025-11 --min-facturacion 500000
```
(ejecutado desde `herramienta/`, sobre el Excel de origen — ver nota de
confidencialidad en README.md sobre por qué ese Excel no está en el repo)

## Modelo y parámetros de la llamada
- Modelo: `claude-sonnet-4-6`
- max_tokens: 3000
- Nota de confidencialidad: Los nombres de canal fueron anonimizados (Canal-XXX) y los montos monetarios escalados por un factor aleatorio por canal, consistente entre meses. Ver DECISIONES.md, iteración 7. Ratios, porcentajes y conteos de documentos NO fueron alterados.
