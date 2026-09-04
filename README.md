# Agente de Salud de Canal — Samsung AAI

## Qué construí

Un sistema agéntico que analiza mensualmente la facturación real de Samsung
Argentina (planes de garantía extendida/seguro, producto "AAI", vendidos a
través de ~20-161 canales comerciales — marketplaces, bancos, retailers) y
produce un diagnóstico estructurado: qué canales requieren atención por
riesgo (notas de crédito anómalas), oportunidad (mix de cuotas, tendencia)
o capilaridad, más una proyección simple de facturación a un mes. Es para
el equipo de trade/channel management, como insumo de la reunión mensual
de canal — no reemplaza la decisión humana, la prepara.

## Cómo se lo pedí

El contrato completo (system prompt + user prompt, con las seis piezas de
la Clase 2: rol, contexto, tarea, restricciones, formato, ejemplos) está en
`prompts/`. En resumen:

- **Rol:** analista senior de trade/channel management de Samsung
  Argentina, con foco en diagnóstico, no en decisión ni ejecución.
- **Contexto:** el negocio (AAI, canales, cuotas, tipos de factura/NC) y
  los datos agregados que produce la herramienta.
- **Tarea:** identificar canales prioritarios (riesgo/oportunidad/
  capilaridad) y proyectar facturación a 1 mes para canales con historia
  suficiente.
- **Restricciones:** sin inventar cifras, sin recomendar acciones
  comerciales concretas, con un método de forecast fijo (evolucionó en la
  iteración 3, ver `DECISIONES.md`), y topes de extensión.
- **Formato:** JSON puro, esquema fijo.
- **Ejemplos:** input→output de un canal, más un ejemplo de forecast.

La **herramienta real** (`herramienta/agregar_metricas_canal.py`) es la
pieza que hace posible todo esto: lee el export crudo de SAP (12.051 filas
de facturas y notas de crédito, un año de datos reales) y lo convierte en
métricas agregadas por canal-mes — el agente nunca ve una fila cruda.

**Nota de confidencialidad:** el Excel original (`Ventas_samsung.xlsx`)
**no está en este repositorio público** porque contiene facturación real
de un empleador con nombres de socios comerciales y montos reales — datos
comercialmente sensibles. Lo que sí está, en `herramienta/salidas/`, es la
salida ya agregada y **anonimizada** de la herramienta (nombres de canal
reemplazados por `Canal-XXX`, montos escalados por un factor aleatorio por
canal) para las 3 corridas de este trabajo, así el pipeline completo
(herramienta → contrato → agente → salida) sigue siendo reproducible sin
exponer información real. El detalle de esta decisión está en
`DECISIONES.md`, iteración 7.

## Qué funciona

- La herramienta agrega correctamente 12.051 filas reales en métricas por
  canal-mes (facturación neta, ratio NC/FC, motivos de NC, mix de cuotas,
  historia de 6 meses) — validado y corregido en la iteración 1.
- El agente corrió 3 veces sobre datos reales de 3 meses distintos
  (2025-11, 2026-03, 2026-06 — elegidos a propósito por ser un mes pico,
  uno bajo, y uno reciente), con salida JSON válida las 3 veces, respetando
  el esquema y las restricciones del contrato.
- El agente distingue correctamente entre canales con evidencia sólida
  (`confianza: alta`) y débil (`confianza: baja`), y usa `datos_insuficientes`
  para ser explícito sobre lo que no puede evaluar — nunca rellena huecos
  con inferencias no respaldadas.
- Análisis económico con datos reales de uso: ver `ANALISIS_ECONOMICO.md`.
- Gobierno, niveles de autonomía (L0-L4) y riesgos: ver `GOBIERNO_Y_RIESGO.md`.

## Qué falta o qué falló

El historial completo de fallas reales está en `DECISIONES.md`. Los puntos
más importantes:

- Un bug de cálculo real en la herramienta (porcentajes de mix de cuotas
  que daban negativos por mezclar facturas y notas de crédito).
- Dos rondas de corridas truncadas por `max_tokens` insuficiente — la
  causa raíz no era el volumen de datos, sino que el contrato dejaba
  abierto cómo explicar el método de forecast, y el modelo lo resolvía de
  la forma más cara (comparando múltiples métodos en prosa).
- Un bug de *race condition* en el artefacto de prueba: una corrida podía
  guardarse con la etiqueta de mes equivocada si el usuario cambiaba de
  pestaña mientras esperaba la respuesta — no rompía nada visiblemente,
  se detectó por inspección manual.
- **No se probó con Haiku 4.5** por una limitación del entorno de prueba
  (el artefacto usado para las corridas reales solo corre con Sonnet
  4.6 de forma fija). El análisis económico recomienda Haiku para
  producción, pero deja explícito que falta correr el mismo protocolo de
  3 corridas con ese modelo antes de confirmar la elección.
- El sistema está acotado a 5 canales prioritarios por corrida — en meses
  de alta actividad (52 canales activos en 2025-11) esto deja afuera
  señales reales, mitigado parcialmente por `datos_insuficientes`.

## Qué aprendí

La lección más fuerte fue sobre diagnóstico de fallas: la primera hipótesis
frente a un output cortado (subir `max_tokens`) trató el síntoma, no la
causa — y el síntoma volvió a aparecer con un límite mayor. Solo cuando
miré *qué* estaba generando el modelo (una comparación de métodos de
forecast en prosa, no pedida explícitamente) entendí que el
problema vivía en una de las seis piezas del contrato (Restricciones), no
en un parámetro de la API. Es exactamente el diagnóstico que enseña la
Clase 2: cuando un resultado decepciona, la pregunta es cuál pieza del
contrato está floja, no "el modelo falló".

También aprendí que separar la herramienta determinística (agregación de
datos) del agente (juicio/diagnóstico) no es solo una cuestión de
prolijidad: es lo que vuelve el sistema barato. Todo el análisis económico
salió casi irrelevante en términos absolutos ($0,78/año con Sonnet)
precisamente porque el LLM nunca procesa los datos crudos — la arquitectura
resuelve el costo antes de que la elección de modelo importe.

Por último, construir el artefacto de prueba (que llama a la API real
desde el navegador) terminó siendo una lección aparte de ingeniería de
software común y corriente: el bug de `re.sub()` reinterpretando
backslashes, y el de la variable de estado leída en el momento equivocado,
no tienen nada que ver con agentes de IA — son errores de JavaScript y
Python de toda la vida. Documentarlos igual me pareció coherente con la
filosofía de la materia: el proceso completo, no solo la parte que sale
bien.
