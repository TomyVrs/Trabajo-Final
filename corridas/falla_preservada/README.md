# falla_preservada/

Este archivo (`salida_truncada_original.json`) guarda la salida **real y
original** de una corrida que falló — no una recreación ni un resumen.

**Qué pasó:** la primera corrida real del sistema (mes 2025-11) se ejecutó
con `max_tokens: 1000`. La API devolvió exactamente `output_tokens: 1000`
— el modelo fue cortado a mitad del JSON, antes de poder cerrar el
esquema completo. El campo `salida_parseada` da `null` porque el texto
truncado no es JSON válido (queda una comilla sin cerrar al final).

**Por qué esto importa como evidencia:** el corte real muestra el síntoma
tal como ocurrió — no es una descripción de lo que pasó, es lo que pasó.
La historia completa de la causa (no era el volumen de datos, era el campo
`metodo` del forecast sin acotar) y el fix real están documentados en
`../../DECISIONES.md`, iteraciones 2 y 3.

**Nota de confidencialidad:** los nombres de canal en el texto truncado
fueron anonimizados con el mismo mapeo (`Canal-XXX`) que el resto del
repo. El corte en sí — dónde exactamente se interrumpe el JSON — se
preservó intacto, porque es la parte que constituye la evidencia.
