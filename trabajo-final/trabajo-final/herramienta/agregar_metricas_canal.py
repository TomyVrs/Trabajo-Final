"""
Herramienta real del sistema agéntico: agregar_metricas_canal.py

Qué hace: lee el export crudo de SAP (Ventas_samsung.xlsx, nivel factura) y
calcula, para un mes objetivo, un paquete de métricas agregadas por canal
comercial (columna "Solicitante"). El agente NUNCA ve las 12.000 filas
crudas — solo ve la salida de esta herramienta, que es determinística y
auditable independientemente del LLM.

Métricas que calcula por canal, para el mes objetivo:
  - facturacion_neta_ars: suma de "Valor neto" (ya viene con signo: las
    notas de crédito restan solas)
  - cantidad_documentos: cantidad de líneas de documento
  - ratio_nc_fc: (líneas de tipo NC) / (líneas de tipo FC) -> proxy de fricción
  - motivos_nc: desglose de las notas de crédito por subtipo (rechazo,
    devolución comercial, devolución DOA, etc.)
  - mix_cuotas_pct: % de facturación en planes cortos (1-9 cuotas),
    medios (10-18) y largos (20+) -> proxy de oportunidad de upselling
  - historia_6m: facturación neta de los 6 meses previos al mes objetivo,
    para que el agente pueda razonar tendencia sin tener que recalcularla

También calcula el share de cada canal sobre el total del mes, para dar
contexto de tamaño (una caída de $ en un canal chico no es lo mismo que en
uno grande).

Uso:
    python agregar_metricas_canal.py --mes 2026-06 --min-facturacion 500000
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime

import openpyxl

COL_SOLICITANTE = 1
COL_CLASE_FACTURA = 3
COL_FECHA = 7
COL_VALOR_NETO = 18
COL_MODALIDAD_PAGO = 52

NC_SUBTIPOS = {
    "NC Rechazo Cliente (OR)": "rechazo_cliente",
    "NC Dev. Comercial (OD)": "devolucion_comercial",
    "NC Dev. Gefco (OA)": "devolucion_logistica",
    "NC Dev. DOA (N6)": "devolucion_doa",
    "NC Administrativa AR": "administrativa",
    "NC Acuerdo Comercial A": "acuerdo_comercial",
    "NC Acuerdo Comercial M": "acuerdo_comercial",
}


def cuotas_bucket(modalidad_pago: str) -> str:
    """Clasifica la modalidad de pago ('12 CUOTAS', '01 CUOTAS', ...) en
    corto/medio/largo. Vacío o no numérico -> 'sin_dato'."""
    if not modalidad_pago:
        return "sin_dato"
    digits = "".join(ch for ch in modalidad_pago if ch.isdigit())
    if not digits:
        return "sin_dato"
    n = int(digits)
    if n <= 9:
        return "corto_1_9"
    if n <= 18:
        return "medio_10_18"
    return "largo_20_mas"


def cargar_filas(path_excel: str):
    wb = openpyxl.load_workbook(path_excel, data_only=True)
    ws = wb["Data"]
    filas = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        fecha = row[COL_FECHA]
        if not isinstance(fecha, datetime):
            continue
        filas.append(row)
    return filas


def mes_de(fecha: datetime) -> str:
    return f"{fecha.year:04d}-{fecha.month:02d}"


def agregar(filas, mes_objetivo: str, meses_historia: int = 6):
    por_canal = defaultdict(lambda: {
        "facturacion_neta_ars": 0.0,
        "cantidad_documentos": 0,
        "cantidad_fc": 0,
        "cantidad_nc": 0,
        "motivos_nc": defaultdict(int),
        # cuotas_monto se calcula SOLO sobre facturas (FC), no sobre notas
        # de crédito: mezclar signos negativos de las NC producía
        # porcentajes sin sentido (ver DECISIONES.md, iteración 2).
        "cuotas_monto": defaultdict(float),
    })
    total_mes = 0.0

    # historia: mes -> facturación neta total (todo canal) y por canal
    historia_por_canal = defaultdict(lambda: defaultdict(float))

    for row in filas:
        fecha = row[COL_FECHA]
        mes = mes_de(fecha)
        canal = (row[COL_SOLICITANTE] or "SIN CANAL").strip()
        clase = (row[COL_CLASE_FACTURA] or "").strip()
        valor = row[COL_VALOR_NETO] or 0.0
        modalidad = (row[COL_MODALIDAD_PAGO] or "").strip()

        historia_por_canal[canal][mes] += valor

        if mes != mes_objetivo:
            continue

        c = por_canal[canal]
        c["facturacion_neta_ars"] += valor
        c["cantidad_documentos"] += 1
        total_mes += valor

        es_factura = clase.startswith("FC") or clase.startswith("Factura")
        if es_factura:
            c["cantidad_fc"] += 1
            # el mix de cuotas solo mira ventas reales (FC), no NC
            c["cuotas_monto"][cuotas_bucket(modalidad)] += valor
        elif clase.startswith("NC"):
            c["cantidad_nc"] += 1
            subtipo = NC_SUBTIPOS.get(clase, "otro")
            c["motivos_nc"][subtipo] += 1

    # armar salida final
    canales_out = []
    for canal, m in por_canal.items():
        ratio_nc_fc = round(m["cantidad_nc"] / m["cantidad_fc"], 4) if m["cantidad_fc"] else None
        cuotas_total = sum(m["cuotas_monto"].values())
        mix_cuotas_pct = {
            k: round(100 * v / cuotas_total, 1) if cuotas_total else 0.0
            for k, v in m["cuotas_monto"].items()
        }
        share_pct = round(100 * m["facturacion_neta_ars"] / total_mes, 2) if total_mes else 0.0

        # historia de los N meses previos (orden cronológico)
        todos_meses = sorted(historia_por_canal[canal].keys())
        idx_objetivo = todos_meses.index(mes_objetivo) if mes_objetivo in todos_meses else len(todos_meses)
        meses_previos = todos_meses[max(0, idx_objetivo - meses_historia):idx_objetivo]
        historia = [
            {"mes": mp, "facturacion_neta_ars": round(historia_por_canal[canal][mp], 2)}
            for mp in meses_previos
        ]

        canales_out.append({
            "canal": canal,
            "facturacion_neta_ars": round(m["facturacion_neta_ars"], 2),
            "share_pct_del_mes": share_pct,
            "cantidad_documentos": m["cantidad_documentos"],
            "cantidad_fc": m["cantidad_fc"],
            "cantidad_nc": m["cantidad_nc"],
            "ratio_nc_fc": ratio_nc_fc,
            "motivos_nc": dict(m["motivos_nc"]),
            "mix_cuotas_pct": mix_cuotas_pct,
            "historia_6m_previa": historia,
        })

    canales_out.sort(key=lambda x: x["facturacion_neta_ars"], reverse=True)

    return {
        "mes_objetivo": mes_objetivo,
        "facturacion_neta_total_ars": round(total_mes, 2),
        "cantidad_canales_activos": len(canales_out),
        "canales": canales_out,
    }


def main():
    ap = argparse.ArgumentParser(description="Agrega métricas de venta por canal-mes desde el export SAP.")
    ap.add_argument("--excel", default="Ventas_samsung.xlsx", help="Ruta al archivo Excel de origen")
    ap.add_argument("--mes", required=True, help="Mes objetivo en formato AAAA-MM, ej: 2026-06")
    ap.add_argument("--min-facturacion", type=float, default=0.0,
                     help="Filtra del output canales con facturación neta absoluta menor a este umbral (reduce ruido de canales marginales)")
    ap.add_argument("--out", default=None, help="Si se pasa, escribe el JSON a este archivo además de stdout")
    args = ap.parse_args()

    filas = cargar_filas(args.excel)
    resultado = agregar(filas, args.mes)

    if args.min_facturacion:
        resultado["canales"] = [
            c for c in resultado["canales"]
            if abs(c["facturacion_neta_ars"]) >= args.min_facturacion
        ]
        resultado["cantidad_canales_activos"] = len(resultado["canales"])

    salida = json.dumps(resultado, ensure_ascii=False, indent=2)
    print(salida)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(salida)


if __name__ == "__main__":
    main()
