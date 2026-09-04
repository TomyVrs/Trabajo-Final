# Gobierno y riesgo

## Qué sistemas toca el agente y con qué permisos

El agente tiene acceso de **solo lectura** a un único sistema: el export
mensual de facturación de SAP (`Ventas_samsung.xlsx`), procesado primero
por la herramienta determinística `agregar_metricas_canal.py`. El agente
nunca:

- escribe ni modifica datos en SAP ni en ningún otro sistema,
- se comunica directamente con ningún canal comercial,
- tiene acceso a sistemas de pago, CRM, o herramientas de comunicación
  (email, Slack, etc.).

Es un sistema de **diagnóstico puro**: lee datos agregados, produce un
JSON. No ejecuta ninguna acción sobre el mundo real. Ese es precisamente
el límite que fija la Restricción del system prompt: "No recomendás
acciones comerciales concretas".

## Nivel de autonomía (vocabulario del curso, L0–L4)

| Actividad | Nivel | Quién interviene |
|---|---|---|
| Leer el export SAP y calcular métricas agregadas (la herramienta) | L4 — autónomo | Nadie; es código determinístico, no un LLM, y el error es barato (se puede re-correr) |
| Generar el diagnóstico de canal (el agente/LLM) | **L2 — ejecutar con revisión** | El channel manager revisa el JSON completo del mes antes de actuar sobre cualquier hallazgo |
| Contactar a un canal, ajustar condiciones comerciales, escalar una alerta | L1 — proponer, nunca L2+ | El agente puede señalar "amerita revisión humana", pero la decisión y la ejecución las toma siempre una persona |
| Firma final del diagnóstico mensual | Humano | El channel manager (o quien tenga ese rol) es quien "firma" el diagnóstico antes de que se use en la reunión mensual de trade — el agente no tiene autoridad para cerrar el ciclo |

Este es el mismo nivel (L2) que la materia usa como estándar de la propia
cursada, con una razón de negocio concreta: los datos que ve el agente
tienen huecos reales (canales sin historia, valores negativos sin
explicar, mix de cuotas sin dato) — un L3 o L4 asumiría que el agente
puede decidir solo con información que las propias corridas muestran que
es incompleta.

## Qué puede salir mal, y qué pasa cuando sale mal

**Falso positivo de riesgo:** el agente marca un canal grande (ej. Samsung
Marketplace, ~25-45% del volumen mensual según el mes) como "riesgo" sin
suficiente base. Impacto: una conversación incómoda o innecesaria con un
canal importante. Mitigación: el campo `confianza` obliga al agente a
declarar cuándo la evidencia es débil, y el humano revisa antes de actuar
— ningún hallazgo de "confianza baja" debería derivar en contacto directo
sin verificación adicional.

**Falso negativo (canal en problemas, no detectado):** el contrato limita
a 5 canales prioritarios por corrida; con meses de hasta 52 canales
activos, es matemáticamente inevitable dejar afuera señales reales. Se
mitiga en parte porque `datos_insuficientes` deja constancia de qué
canales quedaron sin evaluar y por qué — no oculta la limitación.

**Forecast tomado como promesa, no como estimación:** el método de
proyección es un promedio simple de 3 meses, explícitamente marcado con
nivel de `confianza` bajo/media en casi todas las corridas reales (la
volatilidad del negocio es alta — se ven saltos de 10x mes a mes). Si
alguien usa ese número como compromiso de ventas sin leer el campo
`confianza`, el riesgo es de mal uso del output, no de un error del
agente. Mitigación: el `metodo` queda explicitado en cada forecast,
así cualquiera puede auditar de dónde sale el número.

**Alucinación de causa:** el system prompt prohíbe explícitamente asumir
causas que la evidencia no respalda (Restricción #1). En las 3 corridas
reales, el agente respetó esto de forma consistente — cuando no podía
explicar una caída (ej. un canal con historia insuficiente en 2025-11),
la marcó como tal
en vez de inventar un motivo.

## Qué revisa un humano antes de confiar en la salida

Antes de que cualquier hallazgo del agente se use en la reunión mensual de
trade, el channel manager debería:

1. Confirmar que `datos_insuficientes` no dejó afuera un canal
   estratégico por falta de historia (algo corregible manualmente).
2. Contrastar los canales de `confianza: baja` contra su propio
   conocimiento del negocio antes de escalar cualquier alerta.
3. Tratar todo `forecast_canal` como una estimación de referencia, nunca
   como un compromiso — el propio agente ya marca la mayoría con
   confianza baja/media.

## Quién firma

El **channel manager de Samsung Argentina** (o el rol equivalente que
reciba el diagnóstico mensual) es quien firma el uso del diagnóstico: es
quien decide si un hallazgo se convierte en una acción real (contacto,
ajuste comercial, escalamiento). El agente nunca firma nada — produce
información para que una persona firme una decisión.
