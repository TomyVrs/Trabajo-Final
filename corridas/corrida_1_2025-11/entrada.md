# Entrada exacta — corrida 1 (2025-11)

Esta es una copia CONGELADA del texto tal como se envió realmente a la
API en esta corrida — no un puntero a `prompts/`, porque esos archivos
pueden (y de hecho fueron) editados después de esta corrida como parte
del proceso de pulido (ver DECISIONES.md, "Nota final"). Esto garantiza
reproducibilidad exacta independiente de cambios posteriores al contrato.

## Llamada a la API

- Endpoint: `POST https://api.anthropic.com/v1/messages`
- Modelo: `claude-sonnet-4-6`
- max_tokens: 3000
- system: ver más abajo
- messages: [{"role": "user", "content": "<user prompt de más abajo>"}]

## System prompt (exacto, sin cambios desde la iteración 3 de DECISIONES.md)

```
# System prompt — Agente de Salud de Canal (Samsung AAI)

## 1 · Rol

Sos un analista senior de trade/channel management de Samsung Argentina,
especializado en el negocio de seguros y garantías extendidas vendidos a
través de socios comerciales (marketplaces, bancos, retailers). Tenés
criterio comercial, pero tu trabajo es diagnosticar, no decidir ni ejecutar
acciones sobre ningún canal.

## 4 · Restricciones

- Trabajás solo con los datos agregados que te entrega la herramienta
  `agregar_metricas_canal.py` — nunca inventás cifras que no estén en esos
  datos, ni asumís causas que la evidencia no respalda.
- No recomendás acciones comerciales concretas (descuentos, suspensión de
  canal, renegociación de condiciones). Como mucho, señalás que un canal
  "amerita revisión humana" y por qué.
- No mencionás ni comparás canales que no aparezcan en los datos de la
  corrida.
- Si una métrica falta o es ambigua para un canal (ej. `ratio_nc_fc` nulo
  por no tener facturas), lo marcás explícitamente como dato insuficiente
  en vez de omitirlo o inventar un valor.
- Extensión: máximo 5 canales en "prioritarios", máximo 3 en "forecast
  destacado". No analizás los 28+ canales uno por uno en prosa.
- El campo `metodo` de cada forecast usa UN solo método fijo: promedio
  simple de los últimos 3 meses disponibles en `historia_6m_previa` (o
  todos los disponibles si hay menos de 3). Se describe en una sola
  oración corta, sin mostrar el cálculo completo ni comparar métodos
  alternativos — la fórmula es fija, no hay que justificarla cada vez.
- Los campos `evidencia` y `metrica_clave` van directo al punto: máximo
  2 oraciones cada uno. No repitas en `evidencia` los números que ya están
  en `metrica_clave`.

## 5 · Formato

Respondés ÚNICAMENTE con un JSON válido, sin texto antes ni después, con
este esquema exacto:

```json
{
  "periodo_analizado": "AAAA-MM",
  "resumen_ejecutivo": "2-3 frases con el diagnóstico general del mes",
  "canales_prioritarios": [
    {
      "canal": "string, tal como aparece en los datos",
      "categoria": "riesgo | oportunidad | capilaridad",
      "metrica_clave": "string con la métrica y su valor, ej: ratio_nc_fc = 0.14",
      "evidencia": "string, qué dato concreto de la herramienta sostiene esto",
      "confianza": "alta | media | baja",
      "requiere_revision_humana": true
    }
  ],
  "forecast_canal": [
    {
      "canal": "string",
      "proyeccion_proximo_mes_ars": 0,
      "metodo": "string, explicitando el cálculo (ej: promedio móvil 3 meses sobre historia_6m_previa)",
      "confianza": "alta | media | baja"
    }
  ],
  "datos_insuficientes": ["lista de canales o métricas marcadas como incompletas, si las hay"]
}
```

## 6 · Ejemplos

**Entrada (fragmento de la herramienta):**
```json
{"canal": "CANAL EJEMPLO S.A. (MARKETPLACE)", "facturacion_neta_ars": 45000000,
 "share_pct_del_mes": 4.3, "cantidad_fc": 60, "cantidad_nc": 11,
 "ratio_nc_fc": 0.18, "motivos_nc": {"rechazo_cliente": 8, "devolucion_comercial": 3},
 "mix_cuotas_pct": {"corto_1_9": 70.0, "medio_10_18": 25.0, "largo_20_mas": 5.0},
 "historia_6m_previa": [...]}
```

**Salida esperada (fragmento):**
```json
{
  "canal": "CANAL EJEMPLO S.A. (MARKETPLACE)",
  "categoria": "riesgo",
  "metrica_clave": "ratio_nc_fc = 0.18",
  "evidencia": "11 notas de crédito sobre 60 facturas, 8 por rechazo de cliente — el motivo dominante es distinto al promedio de otros canales",
  "confianza": "media",
  "requiere_revision_humana": true
}
```

**Ejemplo de forecast (método fijo, sin comparar alternativas):**
```json
{
  "canal": "CANAL EJEMPLO S.A. (MARKETPLACE)",
  "proyeccion_proximo_mes_ars": 32500000,
  "metodo": "promedio simple de los últimos 3 meses de historia_6m_previa",
  "confianza": "media"
}
```

```

## User prompt (exacto, tal como se envió — el texto de negocio en
"Contexto" ya estaba anonimizado en el momento de esta corrida; el JSON
de datos embebido corresponde exactamente al de
`../../herramienta/salidas/metricas_2025-11.json`)

```
# User prompt — plantilla para cada corrida

## 2 · Contexto

Somos Samsung Argentina. Vendemos planes de garantía extendida/seguro
(producto "AAI") a través de ~20 a 71 canales comerciales activos por mes
(marketplaces propios y de terceros, bancos, retailers). Los planes se
financian en distintas cantidades de cuotas. Cada canal emite facturas
(FC) por ventas y notas de crédito (NC) por rechazos, devoluciones y
acuerdos comerciales.

Te paso el JSON agregado del mes `2025-11`, producido por la herramienta
`agregar_metricas_canal.py` sobre la facturación real de SAP. Cada canal
incluye su facturación neta, participación en el mes, ratio de notas de
crédito sobre facturas, motivos de esas notas, mix de cuotas, y su
historia de los 6 meses previos.

```json
{"mes_objetivo": "2025-11", "facturacion_neta_total_ars": 6466371854.89, "cantidad_canales_activos": 52, "canales": [{"canal": "Canal-001", "facturacion_neta_ars": 1579858605.37, "share_pct_del_mes": 24.43, "cantidad_documentos": 1576, "cantidad_fc": 1557, "cantidad_nc": 19, "ratio_nc_fc": 0.0122, "motivos_nc": {"administrativa": 4, "rechazo_cliente": 15}, "mix_cuotas_pct": {"corto_1_9": 68.3, "medio_10_18": 28.3, "sin_dato": 3.4}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 101279965.61}, {"mes": "2025-08", "facturacion_neta_ars": 62247001.07}, {"mes": "2025-09", "facturacion_neta_ars": 151422284.1}, {"mes": "2025-10", "facturacion_neta_ars": 169274324.97}]}, {"canal": "Canal-003", "facturacion_neta_ars": 957954645.78, "share_pct_del_mes": 14.81, "cantidad_documentos": 13, "cantidad_fc": 11, "cantidad_nc": 2, "ratio_nc_fc": 0.1818, "motivos_nc": {"devolucion_logistica": 2}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 215082913.19}, {"mes": "2025-09", "facturacion_neta_ars": 56868355.75}, {"mes": "2025-10", "facturacion_neta_ars": 492982507.75}]}, {"canal": "Canal-005", "facturacion_neta_ars": 457470890.8, "share_pct_del_mes": 7.07, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-09", "facturacion_neta_ars": 2667049568.41}, {"mes": "2025-10", "facturacion_neta_ars": 795330566.76}]}, {"canal": "Canal-002", "facturacion_neta_ars": 397000219.72, "share_pct_del_mes": 6.14, "cantidad_documentos": 10, "cantidad_fc": 10, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-008", "facturacion_neta_ars": 292685927.64, "share_pct_del_mes": 4.53, "cantidad_documentos": 7, "cantidad_fc": 7, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-006", "facturacion_neta_ars": 281466123.72, "share_pct_del_mes": 4.35, "cantidad_documentos": 231, "cantidad_fc": 230, "cantidad_nc": 1, "ratio_nc_fc": 0.0043, "motivos_nc": {"rechazo_cliente": 1}, "mix_cuotas_pct": {"medio_10_18": 97.5, "corto_1_9": 2.5}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 1585896.95}, {"mes": "2025-08", "facturacion_neta_ars": 1795354.19}, {"mes": "2025-09", "facturacion_neta_ars": 52740956.74}, {"mes": "2025-10", "facturacion_neta_ars": 24468952.08}]}, {"canal": "Canal-014", "facturacion_neta_ars": 256992475.67, "share_pct_del_mes": 3.97, "cantidad_documentos": 118, "cantidad_fc": 118, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"corto_1_9": 56.7, "medio_10_18": 43.3}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 4969308.03}, {"mes": "2025-08", "facturacion_neta_ars": 24480182.35}, {"mes": "2025-09", "facturacion_neta_ars": 16487263.72}, {"mes": "2025-10", "facturacion_neta_ars": 12332784.86}]}, {"canal": "Canal-010", "facturacion_neta_ars": 246680444.88, "share_pct_del_mes": 3.81, "cantidad_documentos": 5, "cantidad_fc": 5, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-018", "facturacion_neta_ars": 172994167.81, "share_pct_del_mes": 2.68, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-004", "facturacion_neta_ars": 168801543.63, "share_pct_del_mes": 2.61, "cantidad_documentos": 9, "cantidad_fc": 7, "cantidad_nc": 2, "ratio_nc_fc": 0.2857, "motivos_nc": {"devolucion_logistica": 2}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-10", "facturacion_neta_ars": 100845621.32}]}, {"canal": "Canal-013", "facturacion_neta_ars": 160963462.96, "share_pct_del_mes": 2.49, "cantidad_documentos": 10, "cantidad_fc": 10, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-017", "facturacion_neta_ars": 156274098.55, "share_pct_del_mes": 2.42, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-09", "facturacion_neta_ars": 14363436.45}]}, {"canal": "Canal-021", "facturacion_neta_ars": 129885995.5, "share_pct_del_mes": 2.01, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-019", "facturacion_neta_ars": 113153639.21, "share_pct_del_mes": 1.75, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-007", "facturacion_neta_ars": 106946975.23, "share_pct_del_mes": 1.65, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 109298342.87}, {"mes": "2025-08", "facturacion_neta_ars": -273245.86}, {"mes": "2025-10", "facturacion_neta_ars": 523516224.67}]}, {"canal": "Canal-009", "facturacion_neta_ars": 94678341.81, "share_pct_del_mes": 1.46, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-023", "facturacion_neta_ars": 93312104.83, "share_pct_del_mes": 1.44, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-016", "facturacion_neta_ars": 89169155.15, "share_pct_del_mes": 1.38, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-012", "facturacion_neta_ars": 85851277.04, "share_pct_del_mes": 1.33, "cantidad_documentos": 144, "cantidad_fc": 144, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"medio_10_18": 20.6, "largo_20_mas": 78.6, "sin_dato": 0.8}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 4576105.88}, {"mes": "2025-08", "facturacion_neta_ars": 15021065.7}, {"mes": "2025-09", "facturacion_neta_ars": 19351994.59}, {"mes": "2025-10", "facturacion_neta_ars": 4902344.94}]}, {"canal": "Canal-011", "facturacion_neta_ars": 85508285.29, "share_pct_del_mes": 1.32, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-09", "facturacion_neta_ars": 5865004.05}]}, {"canal": "Canal-015", "facturacion_neta_ars": 77961713.78, "share_pct_del_mes": 1.21, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-020", "facturacion_neta_ars": 72511858.55, "share_pct_del_mes": 1.12, "cantidad_documentos": 54, "cantidad_fc": 54, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"corto_1_9": 100.0}, "historia_6m_previa": [{"mes": "2025-08", "facturacion_neta_ars": 1818185.43}, {"mes": "2025-09", "facturacion_neta_ars": 10918458.23}, {"mes": "2025-10", "facturacion_neta_ars": 0.0}]}, {"canal": "Canal-028", "facturacion_neta_ars": 45801871.85, "share_pct_del_mes": 0.71, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-08", "facturacion_neta_ars": 17469792.5}]}, {"canal": "Canal-024", "facturacion_neta_ars": 38664970.34, "share_pct_del_mes": 0.6, "cantidad_documentos": 6, "cantidad_fc": 6, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-10", "facturacion_neta_ars": 3916135.8}]}, {"canal": "Canal-030", "facturacion_neta_ars": 29556327.1, "share_pct_del_mes": 0.46, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-10", "facturacion_neta_ars": 118962290.33}]}, {"canal": "Canal-027", "facturacion_neta_ars": 29485924.58, "share_pct_del_mes": 0.46, "cantidad_documentos": 22, "cantidad_fc": 22, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"corto_1_9": 95.3, "medio_10_18": 4.7}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 15792765.38}, {"mes": "2025-08", "facturacion_neta_ars": 8978268.35}, {"mes": "2025-09", "facturacion_neta_ars": 12738264.03}, {"mes": "2025-10", "facturacion_neta_ars": 7664608.45}]}, {"canal": "Canal-025", "facturacion_neta_ars": 25241781.07, "share_pct_del_mes": 0.39, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-022", "facturacion_neta_ars": 23871260.17, "share_pct_del_mes": 0.37, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-10", "facturacion_neta_ars": 2373919.29}]}, {"canal": "Canal-031", "facturacion_neta_ars": 23239703.9, "share_pct_del_mes": 0.36, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-10", "facturacion_neta_ars": 16150478.64}]}, {"canal": "Canal-026", "facturacion_neta_ars": 21043259.0, "share_pct_del_mes": 0.33, "cantidad_documentos": 5, "cantidad_fc": 5, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-033", "facturacion_neta_ars": 18762017.7, "share_pct_del_mes": 0.29, "cantidad_documentos": 12, "cantidad_fc": 11, "cantidad_nc": 1, "ratio_nc_fc": 0.0909, "motivos_nc": {"rechazo_cliente": 1}, "mix_cuotas_pct": {"corto_1_9": 100.0}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 13802202.42}, {"mes": "2025-08", "facturacion_neta_ars": 7382323.46}, {"mes": "2025-09", "facturacion_neta_ars": 29173112.54}, {"mes": "2025-10", "facturacion_neta_ars": 8327854.72}]}, {"canal": "Canal-037", "facturacion_neta_ars": 15940821.88, "share_pct_del_mes": 0.25, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-032", "facturacion_neta_ars": 14746617.29, "share_pct_del_mes": 0.23, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-09", "facturacion_neta_ars": 3978377.59}, {"mes": "2025-10", "facturacion_neta_ars": 11273290.95}]}, {"canal": "Canal-029", "facturacion_neta_ars": 14435099.28, "share_pct_del_mes": 0.22, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-038", "facturacion_neta_ars": 10297736.27, "share_pct_del_mes": 0.16, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-040", "facturacion_neta_ars": 9489358.12, "share_pct_del_mes": 0.15, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-043", "facturacion_neta_ars": 8584352.1, "share_pct_del_mes": 0.13, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-036", "facturacion_neta_ars": 8369799.71, "share_pct_del_mes": 0.13, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-041", "facturacion_neta_ars": 7853168.53, "share_pct_del_mes": 0.12, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-034", "facturacion_neta_ars": 6373772.03, "share_pct_del_mes": 0.1, "cantidad_documentos": 9, "cantidad_fc": 9, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 11426877.56}, {"mes": "2025-08", "facturacion_neta_ars": 11451396.16}, {"mes": "2025-09", "facturacion_neta_ars": 7301465.74}, {"mes": "2025-10", "facturacion_neta_ars": 3732639.49}]}, {"canal": "Canal-039", "facturacion_neta_ars": 6299401.08, "share_pct_del_mes": 0.1, "cantidad_documentos": 3, "cantidad_fc": 3, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": [{"mes": "2025-10", "facturacion_neta_ars": 4458660.17}]}, {"canal": "Canal-035", "facturacion_neta_ars": 5763470.39, "share_pct_del_mes": 0.09, "cantidad_documentos": 13, "cantidad_fc": 13, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"corto_1_9": 35.7, "medio_10_18": 64.3}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 545560.9}, {"mes": "2025-08", "facturacion_neta_ars": 1319415.13}, {"mes": "2025-09", "facturacion_neta_ars": 2721293.76}, {"mes": "2025-10", "facturacion_neta_ars": -381935.9}]}, {"canal": "Canal-042", "facturacion_neta_ars": 5130536.76, "share_pct_del_mes": 0.08, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-044", "facturacion_neta_ars": 5109580.03, "share_pct_del_mes": 0.08, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-046", "facturacion_neta_ars": 3064558.0, "share_pct_del_mes": 0.05, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"medio_10_18": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-048", "facturacion_neta_ars": 2459716.36, "share_pct_del_mes": 0.04, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"corto_1_9": 100.0}, "historia_6m_previa": [{"mes": "2025-07", "facturacion_neta_ars": 3328938.25}, {"mes": "2025-08", "facturacion_neta_ars": 2923915.13}]}, {"canal": "Canal-045", "facturacion_neta_ars": 2228210.69, "share_pct_del_mes": 0.03, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-047", "facturacion_neta_ars": 1910404.82, "share_pct_del_mes": 0.03, "cantidad_documentos": 2, "cantidad_fc": 2, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-051", "facturacion_neta_ars": 1828535.55, "share_pct_del_mes": 0.03, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"corto_1_9": 100.0}, "historia_6m_previa": [{"mes": "2025-09", "facturacion_neta_ars": 1886437.2}]}, {"canal": "Canal-049", "facturacion_neta_ars": 1503443.49, "share_pct_del_mes": 0.02, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-050", "facturacion_neta_ars": 781880.15, "share_pct_del_mes": 0.01, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"sin_dato": 100.0}, "historia_6m_previa": []}, {"canal": "Canal-052", "facturacion_neta_ars": 412323.73, "share_pct_del_mes": 0.01, "cantidad_documentos": 1, "cantidad_fc": 1, "cantidad_nc": 0, "ratio_nc_fc": 0.0, "motivos_nc": {}, "mix_cuotas_pct": {"medio_10_18": 100.0}, "historia_6m_previa": []}]}
```

## 3 · Tarea

Analizá estos datos y producí el diagnóstico de canal del mes según el
formato del system prompt: qué canales requieren atención prioritaria (por
riesgo, oportunidad de upselling de cuotas más largas, o capilaridad —
participación baja vs. lo esperable), y una proyección simple de
facturación del próximo mes para los canales con historia suficiente.

```
