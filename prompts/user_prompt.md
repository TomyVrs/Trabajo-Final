# User prompt — plantilla para cada corrida

## 2 · Contexto

Somos Samsung Argentina. Vendemos planes de garantía extendida/seguro
(producto "AAI") a través de ~20 a 71 canales comerciales activos por mes
(marketplaces propios y de terceros, bancos, retailers). Los planes se
financian en distintas cantidades de cuotas. Cada canal emite facturas
(FC) por ventas y notas de crédito (NC) por rechazos, devoluciones y
acuerdos comerciales.

Te paso el JSON agregado del mes `{MES}`, producido por la herramienta
`agregar_metricas_canal.py` sobre la facturación real de SAP. Cada canal
incluye su facturación neta, participación en el mes, ratio de notas de
crédito sobre facturas, motivos de esas notas, mix de cuotas, y su
historia de los 6 meses previos.

```json
{DATOS_HERRAMIENTA}
```

## 3 · Tarea

Analizá estos datos y producí el diagnóstico de canal del mes según el
formato del system prompt: qué canales requieren atención prioritaria (por
riesgo, oportunidad de upselling de cuotas más largas, o capilaridad —
participación baja vs. lo esperable), y una proyección simple de
facturación del próximo mes para los canales con historia suficiente.
