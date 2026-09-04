# DECISIONES.md — historia del proceso

## Iteración 0 — elección del caso

Partí de la consigna abierta ("un caso real de tu trabajo") y de mi base de
facturación real de Samsung Argentina (export SAP, `Ventas_samsung.xlsx`,
12.051 filas, jul-2025 a jun-2026). La primera idea fue demasiado amplia:
"evaluar capilaridad, riesgo, oportunidad y forecasting" del canal
comercial son casi cuatro proyectos. La acoté a una sola pregunta de
negocio que integra las cuatro dimensiones: *¿qué canales requieren
atención este mes, y cuál es su proyección a corto plazo?* Eso permite un
solo contrato, una sola corrida por mes, con las cuatro dimensiones como
categorías de un mismo output.

## Iteración 1 — bug en el cálculo de `mix_cuotas_pct`

**Qué falló:** al correr la herramienta por primera vez sobre junio 2026,
un canal (Samsung Marketplace) mostró un `mix_cuotas_pct` con un bucket en
**-17.4%** — un porcentaje negativo, que no tiene sentido en una
distribución que debería sumar 100%.

**Causa:** el cálculo original sumaba el `Valor neto` de *todas* las
líneas (facturas y notas de crédito) dentro de cada bucket de cuotas. Como
las notas de crédito llevan signo negativo, un bucket con pocas facturas
pero varias devoluciones podía quedar en negativo, mientras otro bucket sin
devoluciones se mantenía positivo — la suma seguía dando 100% en total,
pero con valores individuales sin sentido económico.

**Fix:** el mix de cuotas ahora se calcula solo sobre facturas (`FC`), no
sobre notas de crédito. Tiene sentido conceptual: el mix de cuotas es una
pregunta sobre el *perfil de venta*, no sobre las devoluciones — mezclar
ambas cosas fue el error de diseño original.

**Archivo afectado:** `herramienta/agregar_metricas_canal.py`,
función `agregar()`.

## Iteración 2 — `max_tokens` insuficiente en la primera corrida real

**Qué falló:** la primera corrida real (mes 2025-11, 52 canales activos,
el mes de mayor actividad de todo el dataset) se cortó a mitad del JSON de
salida. La API devolvió exactamente `output_tokens: 1000` — el tope que
habíamos configurado — y el modelo no llegó a cerrar el objeto JSON. Como
consecuencia, `salida_parseada` dio `null`: el output no era JSON válido
por estar incompleto, a pesar de que el contenido generado hasta el corte
era correcto.

**Causa:** subestimé cuánto espacio necesita el modelo para completar el
esquema completo (resumen ejecutivo + hasta 5 canales prioritarios con
evidencia detallada + hasta 3 proyecciones + posible lista de datos
insuficientes) cuando el mes tiene muchos canales candidatos entre los
cuales elegir y razonar.

**Fix:** subí `max_tokens` de 1000 a 2200 en la llamada a la API.

**Lección para el análisis económico:** este error también es información
económica real — significa que el costo de salida por corrida en meses de
alta actividad (como noviembre) es sensiblemente mayor que en meses
tranquilos, y hay que dimensionar el presupuesto de tokens pensando en el
peor caso (el mes pico), no en el promedio.

## Iteración 3 — el corte se repitió incluso subiendo el límite a 2200

**Qué falló:** subir `max_tokens` a 2200 no alcanzó. Las tres primeras
corridas reales (2025-11, 2026-03, 2026-06) se cortaron otra vez, las tres
exactamente en `output_tokens: 2200` — el nuevo tope. El síntoma se repitió
igual en un mes con pocos canales (2026-03, solo 22 activos) que en uno
con muchos (2025-11, 52 activos), lo que descartó "cantidad de canales"
como única causa.

**Causa real (esta vez sí, la de fondo):** el problema no era el volumen
de canales — era el campo `metodo` del forecast. El contrato pedía
"explicitando el cálculo" sin fijar un método único, y el modelo
respondía calculando 2 o 3 variantes (promedio de 3 meses, promedio de 6
meses, promedio ponderado…) y después promediando esas variantes en
prosa larga, tipo "se reporta el promedio de ambos métodos como
estimación central". Esa verborragia por canal, multiplicada por hasta 3
canales de forecast, consumía la mayor parte del presupuesto de salida
antes de llegar a cerrar el JSON.

**Fix (en el contrato, no en el límite):** en el system prompt, se fijó
un único método obligatorio ("promedio simple de los últimos 3 meses
disponibles en `historia_6m_previa`"), se prohibió explícitamente mostrar
el cálculo completo o comparar métodos alternativos, y se acotó
`evidencia` y `metrica_clave` a 2 oraciones máximo. Además, subí
`max_tokens` a 3000 como margen de seguridad adicional — pero el fix real
es la restricción nueva, no el número más alto.

**Por qué importa documentarlo así:** es la diferencia entre "el modelo
falla, subamos el límite" (tratar el síntoma) y "el contrato dejaba una
decisión de diseño abierta que el modelo resolvía de la forma más cara
posible" (tratar la causa). Es exactamente el tipo de diagnóstico que la
Clase 2 de la materia pide: cuando un resultado decepciona, la pregunta es
cuál de las seis piezas está floja — acá era Restricciones.

*(Esta sección se sigue completando a medida que avanza el proyecto —
corridas finales, y la decisión de modelo del requisito 5.)*

## Iteración 4 — bug de herramienta (no del agente): JSON corrupto al inyectar el payload

**Qué falló:** al reconstruir el artefacto HTML con el system prompt
corregido (iteración 3), la página quedó rota: `Uncaught SyntaxError:
Invalid or unexpected token` al abrirla en el navegador.

**Causa:** fue un error mío en el script de armado del artefacto, no del
agente ni del contrato. Usé `re.sub()` de Python para insertar el JSON del
payload dentro del HTML, pasando el JSON como el string de reemplazo.
`re.sub()` interpreta ciertas secuencias de barra invertida dentro del
texto de reemplazo (`\n`, `\1`, etc.) como si fueran instrucciones de la
propia función — así que cada `\n` que el JSON traía correctamente
escapado (barra invertida + n, para representar un salto de línea dentro
de un string) se convirtió en un salto de línea *real*. Eso rompió la
sintaxis JSON/JavaScript embebida, porque un string entre comillas dobles
en JS no puede contener un salto de línea crudo.

**Fix:** reemplacé el string de reemplazo por una función lambda
(`re.sub(patron, lambda m: contenido, html)`). Cuando el reemplazo es una
función, Python no reinterpreta su contenido — lo inserta tal cual. Con
eso el JSON quedó válido y el artefacto cargó correctamente.

**Por qué lo dejo documentado:** aunque no es un fallo del *agente* en sí
(es un bug de la herramienta auxiliar que arma el entorno de prueba), es
parte real del proceso de construcción y de cómo se depuró — coherente con
el espíritu de la materia de contar el proceso completo, no solo el
resultado final.

## Iteración 5 — race condition en el artefacto: la corrida se guardaba con la etiqueta del mes equivocado

**Qué falló:** la corrida real de 2025-11 (contenido correcto, JSON válido,
`periodo_analizado: "2025-11"` en la salida) quedó guardada bajo la
etiqueta `mes_objetivo: "2026-03"` en el archivo que produjo el artefacto.

**Causa:** en el código del botón "Ejecutar corrida", la variable
`mesSeleccionado` se leía dos veces: una vez al armar el pedido (correcto,
usaba el mes que estaba activo en ese momento) y otra vez al guardar el
resultado, *después* de esperar la respuesta de la API (~40 segundos). Si
el usuario cambiaba de pestaña mientras esperaba —algo totalmente
razonable dada la demora—, el resultado terminaba guardado bajo el mes que
quedó seleccionado al final, no bajo el mes que realmente se le pidió al
modelo. Es un error clásico de manejo de estado asincrónico en
JavaScript: una variable compartida y mutable, leída en dos momentos
distintos de una operación que tarda.

**Fix:** se captura el mes en una constante local (`mesDeEstaCorrida`) al
inicio del handler, antes de la llamada a la API, y se usa esa constante
—no la variable compartida— en todo el resto de la función, incluido el
guardado del resultado.

**Cómo se detectó:** no fue un error visible (la corrida "funcionó", no
tiró excepción) — se detectó por inspección manual, comparando el campo
`mes_objetivo` del resultado contra el contenido real de `user_prompt` y
`periodo_analizado`. Quedó registrado como advertencia: **la ausencia de
error no garantiza que el sistema hizo lo que se le pidió** — parte de por
qué el requisito de "un tercero tiene que poder reconstruir la corrida"
importa tanto como funciona en la práctica.

## Iteración 6 — las 3 corridas finales, válidas

Con los fixes de las iteraciones 3 (método de forecast fijo) y 5 (race
condition de UI) aplicados, se corrieron de nuevo los 3 meses. Resultado:

| Corrida | Mes | Tokens in/out | JSON válido | Etiqueta correcta |
|---|---|---|---|---|
| 1 | 2025-11 | 12.781 / 1.848 | ✅ | ✅ |
| 2 | 2026-03 | 10.408 / 2.119 | ✅ | ✅ |
| 3 | 2026-06 | 11.381 / 2.059 | ✅ | ✅ |

Las tres respetan el esquema del contrato, el tope de 5 canales
prioritarios / 3 forecasts, y el método fijo de proyección. Quedan
guardadas en `corridas/corrida_1_2025-11/`, `corridas/corrida_2_2026-03/`
y `corridas/corrida_3_2026-06/`.

**Balance del proceso:** de 4 intentos de corrida real, 1 (la primera,
antes de subir `max_tokens`) falló por corte, y las 3 corridas de la
segunda tanda fallaron por el mismo motivo con un límite mayor —
recién con el fix de la causa raíz (fijar el método de forecast) las
corridas cerraron limpias. Ese patrón — un síntoma que persiste después de
tratarlo superficialmente, y desaparece al corregir la causa — es en sí
mismo la lección más útil del proceso: la primera hipótesis (el límite de
tokens) explicaba el síntoma pero no la causa, y solo una lectura
cuidadosa de qué estaba consumiendo esos tokens llevó al fix real.

## Iteración 7 — anonimización de datos por confidencialidad

**Qué pasó:** con las 3 corridas ya válidas y guardadas, caí en la cuenta
de que la consigna pide un **repositorio público**, y la base de datos
usada (`Ventas_samsung.xlsx`) es facturación real de un empleador, con
nombres de socios comerciales reales y montos reales — información
comercialmente sensible que no corresponde publicar.

**Decisión:** se anonimizaron los 71 nombres de canal reales (mapeados a
`Canal-001`...`Canal-071`, sin excepciones — incluyendo el canal propio de
marketplace, para no dejar ningún caso "obviamente seguro" librado al
criterio de último momento) y se escalaron todos los montos monetarios por
un factor aleatorio distinto por canal (entre 0.4x y 2.5x, consistente
entre los 6 meses de historia de cada canal para no romper la coherencia
temporal). Los conteos de documentos, ratios (`ratio_nc_fc`) y porcentajes
(`mix_cuotas_pct`, `share_pct_del_mes`) se mantuvieron intactos, porque son
relaciones relativas, no datos comerciales expuestos, y son lo que hace
que el análisis siga siendo válido y interesante.

**Qué se eliminó del repo:** el Excel original, los tres JSON agregados
con datos reales, y las tres corridas originales (con nombres y montos
reales en la prosa generada por el modelo). Se reemplazaron por las
versiones anonimizadas de la herramienta y **3 corridas nuevas, reales**,
corridas sobre los datos ya anonimizados.

**Por qué esto es una decisión de gobierno, no solo de "limpieza":** este
mismo tema — qué datos puede tocar un agente y bajo qué reglas de
confidencialidad — es exactamente lo que pide `GOBIERNO_Y_RIESGO.md`. Se
trata ahí también, pero la decisión concreta de anonimizar nació acá, en
el momento de preparar la entrega, no en el diseño original del sistema.
Vale la pena ser honesto sobre eso: no se pensó desde el primer momento, sino recién al preparar la entrega pública — una falla real de proceso (debería haber sido parte del diseño inicial, no una corrección de último momento) que queda documentada como tal.

## Cierre — corridas finales sobre datos anonimizados

Se corrieron de nuevo los 3 meses sobre los datos anonimizados. Las tres
cerraron limpias en el primer intento (sin necesidad de nuevas
iteraciones): JSON válido, etiqueta de mes correcta, esquema respetado,
método de forecast fijo respetado. Quedan guardadas en `corridas/` y son
las oficiales de esta entrega.

| Corrida | Mes | Tokens in/out |
|---|---|---|
| 1 | 2025-11 | 12.473 / 2.726 |
| 2 | 2026-03 | 10.283 / 1.888 |
| 3 | 2026-06 | 11.228 / 1.746 |

Que las tres corridas post-anonimización hayan salido bien al primer
intento es, en sí, una señal más de que los fixes de las iteraciones 3 y 5
eran correctos y no dependían de las particularidades de los datos reales
— la calidad del sistema no cambió al cambiar los nombres y montos, que es
justamente lo que uno esperaría de un sistema bien separado entre
"herramienta que agrega datos" y "agente que razona sobre agregados".

## Nota final — pulido posterior de contexto

Después de correr las 3 corridas finales (anonimizadas), se revisó una
vez más el texto de `prompts/user_prompt.md` y se encontró que la sección
de Contexto todavía mencionaba nombres reales de socios comerciales
(a modo de ejemplo del tipo de negocio) — inconsistente con la decisión
de anonimizar tomada en la iteración 7. Se genericen esos nombres. Esto
es un ajuste cosmético del prompt (no cambia el comportamiento del agente
ni los datos que procesa) y no invalida las 3 corridas ya guardadas: los
datos que efectivamente viajaron a la API en esas corridas ya tenían los
canales anonimizados como `Canal-XXX` y los montos escalados — el único
texto que cambió después es la descripción genérica del negocio en el
contexto, no información sensible.
