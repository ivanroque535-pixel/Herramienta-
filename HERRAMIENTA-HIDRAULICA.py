import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

import io
import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


def generar_excel_memoria_calculo(
    df_memoria, info_critica, temp_agua, p_min_req, desnivel_top
):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Memoria Hidráulica UAA"
    ws.views.sheetView[0].showGridLines = True

    # Estilos profesionales
    font_title = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
    font_section = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_regular = Font(name="Calibri", size=10)
    font_italic = Font(name="Calibri", size=9, italic=True)

    fill_navy = PatternFill(
        start_color="1E3A8A", end_color="1E3A8A", fill_type="solid"
    )
    fill_blue = PatternFill(
        start_color="2563EB", end_color="2563EB", fill_type="solid"
    )
    fill_critico = PatternFill(
        start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"
    )

    thin_border = Side(border_style="thin", color="D1D5DB")
    border_cell = Border(
        left=thin_border, right=thin_border, top=thin_border, bottom=thin_border
    )

    # 1. ENCABEZADO INSTITUCIONAL
    ws.merge_cells("A1:S1")
    ws["A1"] = (
        "UNIVERSIDAD AUTÓNOMA DE AGUASCALIENTES — DEPARTAMENTO DE INGENIERÍA"
        " CIVIL"
    )
    ws["A1"].font = font_title

    ws.merge_cells("A2:S2")
    ws["A2"] = (
        "INSTALACIONES BÁSICAS — MEMORIA DE CÁLCULO HIDRÁULICO Y BOMBEO OFICIAL"
    )
    ws["A2"].font = Font(name="Calibri", size=11, bold=True, color="2563EB")

    # 2. SECCIÓN 1: TABLA RESUMEN DE CÁLCULO POR TRAMOS
    ws.merge_cells("A4:S4")
    ws["A4"] = (
        "1. TABLA RESUMEN DE CÁLCULO POR TRAMOS (DARCY-WEISBACH VS"
        " HAZEN-WILLIAMS)"
    )
    ws["A4"].font = font_section
    ws["A4"].fill = fill_navy

    headers = [
        "Tramo",
        "Nodo Inicio",
        "Nodo Fin",
        "Longitud L (m)",
        "DN (mm)",
        "D real (m)",
        "UM Term.",
        "UM Acum.",
        "Q Dis. (L/s)",
        "Q Dis. (m³/s)",
        "Velocidad (m/s)",
        "Estado Vel.",
        "Re",
        "Factor f",
        "hf Darcy (m)",
        "hf HW (m)",
        "Σ K Acc.",
        "hm Acc. (m)",
        "h Total (m)",
    ]

    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=5, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_blue
        cell.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )

    row_start = 6
    num_tramos = len(df_memoria)
    for i, r in df_memoria.iterrows():
        row_num = row_start + i
        ws.cell(row=row_num, column=1, value=str(r.get("Tramo", "")))
        ws.cell(row=row_num, column=2, value=str(r.get("Desde", "")))
        ws.cell(row=row_num, column=3, value=str(r.get("Hasta", "")))
        ws.cell(row=row_num, column=4, value=float(r.get("L_m", 0)))
        ws.cell(row=row_num, column=5, value=float(r.get("DN_mm", 0)))
        ws.cell(row=row_num, column=6, value=float(r.get("D_m", 0)))
        ws.cell(row=row_num, column=7, value=int(r.get("UM_Terminales", 0)))
        ws.cell(row=row_num, column=8, value=int(r.get("UM_Acumuladas", 0)))
        ws.cell(row=row_num, column=9, value=float(r.get("Q_diseno_Lps", 0)))
        ws.cell(row=row_num, column=10, value=float(r.get("Q_diseno_m3s", 0)))
        ws.cell(row=row_num, column=11, value=float(r.get("Velocidad_ms", 0)))
        ws.cell(row=row_num, column=12, value=str(r.get("Estado_Velocidad", "")))
        ws.cell(row=row_num, column=13, value=float(r.get("Re", 0)))
        ws.cell(row=row_num, column=14, value=float(r.get("Factor_f", 0)))
        ws.cell(row=row_num, column=15, value=float(r.get("hf_Darcy_m", 0)))
        ws.cell(row=row_num, column=16, value=float(r.get("hf_HW_m", 0)))
        ws.cell(row=row_num, column=17, value=float(r.get("Acc_K_total", 0.0)))
        ws.cell(row=row_num, column=18, value=float(r.get("hm_K_m", 0.0)))
        ws.cell(row=row_num, column=19, value=float(r.get("h_Total_Tramo_m", 0)))

        for c in range(1, 20):
            cell = ws.cell(row=row_num, column=c)
            cell.font = font_regular
            cell.border = border_cell

    # 3. SECCIÓN 2: EVALUACIÓN DE TRAYECTORIAS Y RUTA CRÍTICA
    r_rutas = row_start + num_tramos + 2
    ws.merge_cells(f"A{r_rutas}:S{r_rutas}")
    ws[f"A{r_rutas}"] = "2. EVALUACIÓN DE TRAYECTORIAS Y RUTA CRÍTICA DEL SISTEMA"
    ws[f"A{r_rutas}"].font = font_section
    ws[f"A{r_rutas}"].fill = fill_navy

    headers_rutas = [
        "Mueble Terminal",
        "Trayectoria Topológica",
        "Desnivel ΔZ (m)",
        "Σ hf Darcy (m)",
        "Σ hm Acc. (m)",
        "Pérdida Total (m)",
        "Pmin Req. (m.c.a.)",
        "CDT Requerida (m.c.a.)",
        "Estado",
    ]
    for col_idx, h in enumerate(headers_rutas, start=1):
        cell = ws.cell(row=r_rutas + 1, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_blue
        cell.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )

    df_rutas = st.session_state.get("df_rutas", pd.DataFrame())
    r_curr = r_rutas + 2
    if not df_rutas.empty:
        for idx_r, r_row in df_rutas.iterrows():
            r = r_curr + idx_r
            ws.cell(
                row=r, column=1, value=str(r_row.get("Mueble / Descarga", ""))
            ).font = font_bold
            ws.cell(
                row=r, column=2, value=str(r_row.get("Trayectoria", ""))
            ).font = font_regular
            ws.cell(
                row=r, column=3, value=float(r_row.get("H_estatica_m", 0.0))
            ).font = font_regular
            ws.cell(
                row=r, column=4, value=float(r_row.get("Sum_hf_m", 0.0))
            ).font = font_regular
            ws.cell(
                row=r, column=5, value=float(r_row.get("Sum_hm_m", 0.0))
            ).font = font_regular
            ws.cell(
                row=r, column=6, value=float(r_row.get("Perdida_Total_m", 0.0))
            ).font = font_regular
            ws.cell(
                row=r,
                column=7,
                value=float(r_row.get("P_min_req_mca", p_min_req)),
            ).font = font_regular
            ws.cell(
                row=r,
                column=8,
                value=float(r_row.get("CDT_Requerida_mca", 0.0)),
            ).font = font_bold

            is_critico = r_row.get("Mueble / Descarga", "") == info_critica.get(
                "Mueble / Descarga", ""
            )
            ws.cell(
                row=r, column=9, value="🚨 RUTA CRÍTICA" if is_critico else "OK"
            ).font = font_bold

            for c in range(1, 10):
                cell = ws.cell(row=r, column=c)
                cell.border = border_cell
                if is_critico:
                    cell.fill = fill_critico
                if c in [3, 4, 5, 6, 7, 8]:
                    cell.number_format = "0.000"
        r_bomba = r_curr + len(df_rutas) + 2
    else:
        r_bomba = r_curr + 2

    # 4. SECCIÓN 3: SECCIÓN DE BOMBEO (TAL COMO TU IMAGEN)
    ws.merge_cells(f"A{r_bomba}:S{r_bomba}")
    ws[f"A{r_bomba}"] = (
        "3. DIMENSIONAMIENTO ELECTROMECÁNICO DEL EQUIPO DE BOMBEO"
    )
    ws[f"A{r_bomba}"].font = font_section
    ws[f"A{r_bomba}"].fill = fill_navy

    row_q = df_memoria.iloc[0]
    q_bombeo_val = float(row_q.get("Q_diseno_Lps", 0.0))
    cdt_val = float(info_critica.get("CDT_Requerida_mca", 0.0))
    eficiencia_val = float(st.session_state.get("eficiencia_bomba", 0.60))

    # Cálculo dinámico de potencias
    p_hid_val = (1000.0 * (q_bombeo_val / 1000.0) * cdt_val) / 75.0
    p_mec_val = p_hid_val / eficiencia_val if eficiencia_val > 0 else 0.0

    potencias_comerciales = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 7.5, 10.0]
    p_comercial = next(
        (p for p in potencias_comerciales if p >= p_mec_val),
        potencias_comerciales[-1],
    )

    bomba_rows = [
        ("Caudal Máximo de Bombeo (Q)", q_bombeo_val, "L/s"),
        ("Carga Dinámica Total (CDT):", cdt_val, "m.c.a."),
        ("Eficiencia Electromecánica (η):", eficiencia_val, "%"),
        ("Potencia Hidráulica (Phid):", p_hid_val, "HP"),
        ("Potencia Mecánica Requerida (Pmec):", p_mec_val, "HP"),
        (
            "Potencia Comercial Sugerida:",
            f"{p_comercial:.2f} HP (ó {p_comercial+0.25:.2f} HP)",
            "HP Comercial",
        ),
    ]

    for idx, (lbl, val, unit) in enumerate(bomba_rows, start=r_bomba + 1):
        ws.cell(row=idx, column=1, value=lbl).font = font_bold
        c_val = ws.cell(row=idx, column=2, value=val)
        c_val.font = font_bold
        c_unit = ws.cell(row=idx, column=3, value=unit)
        c_unit.font = font_italic

        if "Phid" in lbl or "Pmec" in lbl or "CDT" in lbl or "Caudal" in lbl:
            c_val.number_format = "0.000"
        elif "%" in unit:
            c_val.number_format = "0.00"

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 24
    ws.column_dimensions["C"].width = 16

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS UI
# ==============================================================================
st.set_page_config(
    page_title="HIDRA-NET PRO | Análisis Hidráulico UAA (10/10)",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2563EB;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💧 HIDRA-NET PRO: Redes de Agua Potable y Bombeo</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Universidad Autónoma de Aguascalientes | Auditoría Hidráulica e Ingeniería de Fluidos</div>', unsafe_allow_html=True)

# ==============================================================================
# MÓDULO A: MOTOR HIDRÁULICO AVANZADO, TABLAS Y MÉTODOS NUMÉRICOS
# ==============================================================================

TABLA_LEQ_OFICIAL = {
    13:  {"Codo 90° R.Largo": 0.23, "Codo 90° R.Medio": 0.32, "Codo 90° R.Corto": 0.41, "Codo 45°": 0.16, "Curva 90° R/D=1.5": 0.14, "Curva 90° R/D=1": 0.23, "Curva 45°": 0.11, "Entrada Normal": 0.11, "Entrada Borda": 0.26, "Válvula Compuerta": 0.09, "Válvula Globo": 3.55, "Válvula Ángulo": 1.79, "Tee Directo": 0.23, "Tee Bilateral": 0.86, "Tee Red. Directo": 0.46, "Válvula de Pie": 2.70, "Salida": 0.32, "Válvula Retención Liviana": 0.90, "Válvula Retención Pesada": 1.23, "Reducción": 0.06, "Ampliación": 0.12},
    19:  {"Codo 90° R.Largo": 0.32, "Codo 90° R.Medio": 0.45, "Codo 90° R.Corto": 0.56, "Codo 45°": 0.23, "Curva 90° R/D=1.5": 0.20, "Curva 90° R/D=1": 0.30, "Curva 45°": 0.15, "Entrada Normal": 0.20, "Entrada Borda": 0.40, "Válvula Compuerta": 0.12, "Válvula Globo": 5.14, "Válvula Ángulo": 2.60, "Tee Directo": 0.33, "Tee Bilateral": 1.16, "Tee Red. Directo": 0.56, "Válvula de Pie": 3.90, "Salida": 0.46, "Válvula Retención Liviana": 1.28, "Válvula Retención Pesada": 1.83, "Reducción": 0.09, "Ampliación": 0.18},
    25:  {"Codo 90° R.Largo": 0.42, "Codo 90° R.Medio": 0.57, "Codo 90° R.Corto": 0.70, "Codo 45°": 0.30, "Curva 90° R/D=1.5": 0.26, "Curva 90° R/D=1": 0.38, "Curva 45°": 0.18, "Entrada Normal": 0.29, "Entrada Borda": 0.55, "Válvula Compuerta": 0.15, "Válvula Globo": 6.72, "Válvula Ángulo": 3.40, "Tee Directo": 0.43, "Tee Bilateral": 1.45, "Tee Red. Directo": 0.67, "Válvula de Pie": 5.10, "Salida": 0.61, "Válvula Retención Liviana": 1.65, "Válvula Retención Pesada": 2.43, "Reducción": 0.12, "Ampliación": 0.24},
    31:  {"Codo 90° R.Largo": 0.52, "Codo 90° R.Medio": 0.70, "Codo 90° R.Corto": 0.84, "Codo 45°": 0.37, "Curva 90° R/D=1.5": 0.31, "Curva 90° R/D=1": 0.45, "Curva 45°": 0.21, "Entrada Normal": 0.37, "Entrada Borda": 0.69, "Válvula Compuerta": 0.18, "Válvula Globo": 8.31, "Válvula Ángulo": 4.20, "Tee Directo": 0.53, "Tee Bilateral": 1.74, "Tee Red. Directo": 0.77, "Válvula de Pie": 6.30, "Salida": 0.75, "Válvula Retención Liviana": 2.03, "Válvula Retención Pesada": 3.03, "Reducción": 0.15, "Ampliación": 0.30},
    38:  {"Codo 90° R.Largo": 0.62, "Codo 90° R.Medio": 0.82, "Codo 90° R.Corto": 0.98, "Codo 45°": 0.44, "Curva 90° R/D=1.5": 0.37, "Curva 90° R/D=1": 0.52, "Curva 45°": 0.25, "Entrada Normal": 0.46, "Entrada Borda": 0.84, "Válvula Compuerta": 0.21, "Válvula Globo": 9.89, "Válvula Ángulo": 5.00, "Tee Directo": 0.63, "Tee Bilateral": 2.04, "Tee Red. Directo": 0.88, "Válvula de Pie": 7.50, "Salida": 0.90, "Válvula Retención Liviana": 2.41, "Válvula Retención Pesada": 3.63, "Reducción": 0.18, "Ampliación": 0.36},
    50:  {"Codo 90° R.Largo": 0.81, "Codo 90° R.Medio": 1.08, "Codo 90° R.Corto": 1.27, "Codo 45°": 0.59, "Curva 90° R/D=1.5": 0.48, "Curva 90° R/D=1": 0.67, "Curva 45°": 0.32, "Entrada Normal": 0.63, "Entrada Borda": 1.13, "Válvula Compuerta": 0.28, "Válvula Globo": 13.07, "Válvula Ángulo": 6.61, "Tee Directo": 0.83, "Tee Bilateral": 2.62, "Tee Red. Directo": 1.09, "Válvula de Pie": 9.89, "Salida": 1.19, "Válvula Retención Liviana": 3.16, "Válvula Retención Pesada": 4.83, "Reducción": 0.23, "Ampliación": 0.47},
    63:  {"Codo 90° R.Largo": 1.01, "Codo 90° R.Medio": 1.33, "Codo 90° R.Corto": 1.56, "Codo 45°": 0.73, "Curva 90° R/D=1.5": 0.59, "Curva 90° R/D=1": 0.82, "Curva 45°": 0.38, "Entrada Normal": 0.80, "Entrada Borda": 1.42, "Válvula Compuerta": 0.34, "Válvula Globo": 16.24, "Válvula Ángulo": 8.21, "Tee Directo": 1.03, "Tee Bilateral": 3.21, "Tee Red. Directo": 1.30, "Válvula de Pie": 12.29, "Salida": 1.48, "Válvula Retención Liviana": 3.91, "Válvula Retención Pesada": 6.04, "Reducción": 0.29, "Ampliación": 0.59},
    75:  {"Codo 90° R.Largo": 1.20, "Codo 90° R.Medio": 1.58, "Codo 90° R.Corto": 1.84, "Codo 45°": 0.87, "Curva 90° R/D=1.5": 0.71, "Curva 90° R/D=1": 0.96, "Curva 45°": 0.45, "Entrada Normal": 0.98, "Entrada Borda": 1.71, "Válvula Compuerta": 0.41, "Válvula Globo": 19.41, "Válvula Ángulo": 9.82, "Tee Directo": 1.23, "Tee Bilateral": 3.80, "Tee Red. Directo": 1.51, "Válvula de Pie": 14.69, "Salida": 1.77, "Válvula Retención Liviana": 4.66, "Válvula Retención Pesada": 7.24, "Reducción": 0.35, "Ampliación": 0.71},
    100: {"Codo 90° R.Largo": 1.59, "Codo 90° R.Medio": 2.08, "Codo 90° R.Corto": 2.41, "Codo 45°": 1.16, "Curva 90° R/D=1.5": 0.93, "Curva 90° R/D=1": 1.26, "Curva 45°": 0.59, "Entrada Normal": 1.32, "Entrada Borda": 2.29, "Válvula Compuerta": 0.53, "Válvula Globo": 25.76, "Válvula Ángulo": 13.03, "Tee Directo": 1.62, "Tee Bilateral": 4.97, "Tee Red. Directo": 1.93, "Válvula de Pie": 19.49, "Salida": 2.35, "Válvula Retención Liviana": 6.17, "Válvula Retención Pesada": 9.65, "Reducción": 0.46, "Ampliación": 0.94}
}

def resolver_colebrook_white(Re: float, eps_m: float, D_m: float, tol: float = 1e-7, max_iter: int = 100) -> float:
    """Resuelve la Ecuación Implícita de Colebrook-White usando Newton-Raphson (Rúbrica 5.2)."""
    if Re <= 0: return 0.0
    if Re < 2300.0: return 64.0 / Re
    
    rel_rough = eps_m / (3.7 * D_m)
    log_sj = np.log10(rel_rough + (5.74 / (Re ** 0.9)))
    f_guess = 0.25 / (log_sj ** 2)
    
    x = 1.0 / np.sqrt(f_guess)
    factor_ln = 2.0 / np.log(10.0)
    
    for _ in range(max_iter):
        arg = rel_rough + (2.51 * x / Re)
        if arg <= 0: break
        fx = x + factor_ln * np.log(arg)
        dfx = 1.0 + (factor_ln * (2.51 / Re)) / arg
        dx = fx / dfx
        x_new = x - dx
        if abs(x_new - x) < tol:
            x = x_new
            break
        x = x_new
        
    return 1.0 / (x ** 2)

def calcular_gasto_hunter_mapas(um: float, tipo_sistema: str = "tanque") -> float:
    """Calcula el caudal de diseño Q (L/s) según la curva normalizada MAPAS-CONAGUA (Rúbrica 5.1)."""
    if um <= 0: return 0.0
    if tipo_sistema.lower() == "fluxometro":
        if um <= 5: return 0.15 + (um * 0.08)
        elif um <= 10: return 0.55 + ((um - 5) * 0.04)
        elif um <= 50: return 0.75 + ((um - 10) * 0.025)
        elif um <= 100: return 1.75 + ((um - 50) * 0.015)
        else: return 2.50 + ((um - 100) * 0.010)
    else:
        if um <= 3: return 0.12 * (um ** 0.50)
        elif um <= 10: return 0.12 + ((um - 3) * 0.035)
        elif um <= 30: return 0.365 + ((um - 10) * 0.018)
        elif um <= 60: return 0.725 + ((um - 30) * 0.0125)
        elif um <= 100: return 1.10 + ((um - 60) * 0.0090)
        else: return 1.46 + ((um - 100) * 0.0065)

def obtener_leq_accesorio(dn_mm: float, nombre_accesorio: str) -> float:
    """Obtiene la Longitud Equivalente Leq (m) desde la tabla indexada."""
    dn_closest = min(TABLA_LEQ_OFICIAL.keys(), key=lambda x: abs(x - dn_mm))
    return TABLA_LEQ_OFICIAL[dn_closest].get(nombre_accesorio, 0.0)

# ==============================================================================
# MÓDULOS B & C: PROCESAMIENTO TOPOLÓGICO Y EVALUACIÓN DUAL DE PÉRDIDAS
# ==============================================================================

def procesar_evaluacion_hidraulica_completa(df_tramos_in: pd.DataFrame, metodo_simultaneidad: str, tipo_hunter: str, nu_agua: float) -> pd.DataFrame:
    """Integra la agregación de tramos (Grafo DFS), caudales, velocidades y evaluación dual de pérdidas."""
    df = df_tramos_in.copy()
    g = 9.81
    
    adj, um_directas = {}, {}
    for _, row in df.iterrows():
        u = str(row["Desde"]).strip()
        v = str(row["Hasta"]).strip()
        if u not in adj: adj[u] = []
        adj[u].append(v)
        um_directas[v] = float(row.get("UM_Terminales", 0))

    def acumular_um(nodo):
        total = um_directas.get(nodo, 0.0)
        for hijo in adj.get(nodo, []):
            total += acumular_um(hijo)
        return total

    df["UM_Acumuladas"] = df["Hasta"].apply(lambda v: acumular_um(str(v).strip()))
    df["Tramo"] = df["Desde"].astype(str) + " -> " + df["Hasta"].astype(str)

    # Caudales y Velocidades
    q_dis_list = []
    for idx, row in df.iterrows():
        um_acum = row["UM_Acumuladas"]
        q_dir = float(row.get("Q_directo_Lps", 0.0))
        if "Hunter" in metodo_simultaneidad:
            q_calc = calcular_gasto_hunter_mapas(um_acum, tipo_sistema=tipo_hunter)
        elif "Coeficiente" in metodo_simultaneidad:
            n_muebles = max(1, um_acum)
            ks = 1.0 if n_muebles <= 1 else 1.0 / np.sqrt(n_muebles - 1.0)
            q_calc = n_muebles * 0.15 * ks
        else:
            q_calc = q_dir
        q_dis_list.append(q_calc)

    df["Q_diseno_Lps"] = q_dis_list
    df["Q_diseno_m3s"] = df["Q_diseno_Lps"] / 1000.0
    df["D_m"] = df["DN_mm"] / 1000.0
    df["Area_m2"] = (np.pi * (df["D_m"] ** 2)) / 4.0
    df["Velocidad_ms"] = np.where(df["Area_m2"] > 0, df["Q_diseno_m3s"] / df["Area_m2"], 0.0)

    # Alertas Normativas de Velocidad (0.60 m/s <= v <= 2.50 m/s)
    condiciones = [(df["Velocidad_ms"] < 0.60), (df["Velocidad_ms"] > 2.50)]
    elecciones = ["⚠️ Baja (< 0.60 m/s)", "🚨 Alta (> 2.50 m/s)"]
    df["Estado_Velocidad"] = np.select(condiciones, elecciones, default="✅ Normativa (0.60-2.50 m/s)")

    # Pérdidas Duales
    Re_list, f_list, hf_darcy_list, hf_hw_list, hm_k_list, htotal_list = [], [], [], [], [], []
    for idx, row in df.iterrows():
        L_real = float(row["L_m"])
        D_m = float(row["D_m"])
        v = float(row["Velocidad_ms"])
        Q_m3s = float(row["Q_diseno_m3s"])
        eps_m = float(row["Rugosidad_mm"]) / 1000.0
        C = float(row["Coef_C"])
        K_acc = float(row.get("Acc_K_total", 0.0))
        Leq_acc = float(row.get("Leq_total_m", 0.0))
        
        L_total = L_real + Leq_acc
        Re = (v * D_m) / nu_agua if (nu_agua > 0 and D_m > 0) else 0.0
        Re_list.append(Re)
        
        f = resolver_colebrook_white(Re, eps_m, D_m)
        f_list.append(f)
        
        hf_darcy = f * (L_total / D_m) * ((v ** 2) / (2.0 * g)) if D_m > 0 else 0.0
        hf_darcy_list.append(hf_darcy)
        
        hf_hw = (10.674 * L_total * (Q_m3s ** 1.852)) / ((C ** 1.852) * (D_m ** 4.871)) if (D_m > 0 and C > 0 and Q_m3s > 0) else 0.0
        hf_hw_list.append(hf_hw)
        
        hm_k = K_acc * ((v ** 2) / (2.0 * g))
        hm_k_list.append(hm_k)
        
        h_total = hf_darcy if Leq_acc > 0 else (hf_darcy + hm_k)
        htotal_list.append(h_total)

    df["Re"] = Re_list
    df["Factor_f"] = f_list
    df["hf_Darcy_m"] = hf_darcy_list
    df["hf_HW_m"] = hf_hw_list
    df["hm_K_m"] = hm_k_list
    df["h_Total_Tramo_m"] = htotal_list

    return df

# ==============================================================================
# MÓDULO D: SOLVER DE RUTA CRÍTICA Y CARGA DINÁMICA TOTAL (CDT)
# ==============================================================================

def resolver_ruta_critica_y_cdt(df_evaluado: pd.DataFrame, p_min_mca: float) -> tuple[pd.DataFrame, dict]:
    """Determina de forma computacional la ruta crítica y calcula la CDT (Rúbrica 2.2-e, f)."""
    df = df_evaluado.copy()
    nodos_origen = set(df["Desde"].astype(str).str.strip())
    nodos_destino = set(df["Hasta"].astype(str).str.strip())
    nodos_raiz = list(nodos_origen - nodos_destino)
    raiz = nodos_raiz[0] if nodos_raiz else str(df.iloc[0]["Desde"]).strip()
    
    grafo = {}
    for _, row in df.iterrows():
        u = str(row["Desde"]).strip()
        v = str(row["Hasta"]).strip()
        if u not in grafo: grafo[u] = []
        grafo[u].append({
            "hasta": v,
            "h_total": float(row["h_Total_Tramo_m"]),
            "hf": float(row["hf_Darcy_m"]),
            "hm": float(row.get("hm_K_m", 0.0)),
            "dz": float(row.get("Desnivel_m", 0.0)),
            "um_term": float(row.get("UM_Terminales", 0.0))
        })
        
    reporte_muebles = []
    def trazar_ramales(nodo_actual, hf_acum, hm_acum, htot_acum, dz_acum, camino_str):
        if nodo_actual not in grafo: return
        for arista in grafo[nodo_actual]:
            v = arista["hasta"]
            n_hf = hf_acum + arista["hf"]
            n_hm = hm_acum + arista["hm"]
            n_htot = htot_acum + arista["h_total"]
            n_dz = dz_acum + arista["dz"]
            n_camino = f"{camino_str} ➔ {v}"
            
            if arista["um_term"] > 0 or v not in grafo:
                cdt_requerida = n_dz + n_htot + p_min_mca
                reporte_muebles.append({
                    "Mueble / Descarga": v,
                    "Trayectoria": n_camino,
                    "H_estatica_m": n_dz,
                    "Sum_hf_m": n_hf,
                    "Sum_hm_m": n_hm,
                    "Perdida_Total_m": n_htot,
                    "P_min_req_mca": p_min_mca,
                    "CDT_Requerida_mca": cdt_requerida
                })
            trazar_ramales(v, n_hf, n_hm, n_htot, n_dz, n_camino)

    trazar_ramales(raiz, 0.0, 0.0, 0.0, 0.0, raiz)
    df_rutas = pd.DataFrame(reporte_muebles)
    
    if not df_rutas.empty:
        idx_critico = df_rutas["CDT_Requerida_mca"].idxmax()
        info_critica = df_rutas.loc[idx_critico].to_dict()
    else:
        info_critica = {}
        
    return df_rutas, info_critica

# ==============================================================================
# MÓDULO E & F: EXCELENCIA INGENIERIL (PUNTOS EXTRAS & OPTIMIZACIÓN)
# ==============================================================================

def dimensionar_bomba_y_transitorios(q_bombeo_lps: float, cdt_mca: float, eficiencia: float, d_mm: float, e_mm: float, v_ms: float, L_m: float, t_cierre_s: float):
    """Calcula bombeo electromecánico y análisis transitorio de golpe de ariete (Puntos Extra 2 y 3)."""
    q_m3s = q_bombeo_lps / 1000.0
    gamma = 1000.0
    p_hid_hp = (gamma * q_m3s * cdt_mca) / 75.0 if q_m3s > 0 else 0.0
    p_mec_hp = p_hid_hp / eficiencia if eficiencia > 0 else 0.0
    
    potencias_comerciales = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 7.5, 10.0]
    p_comercial = next((p for p in potencias_comerciales if p >= p_mec_hp), potencias_comerciales[-1])
    
    # Golpe de Ariete
    K_agua = 2.2e9
    E_mat = 3.0e9 # CPVC
    d_m, e_m = d_mm / 1000.0, e_mm / 1000.0
    celeridad_a = np.sqrt(K_agua / 1000.0) / np.sqrt(1.0 + (K_agua / E_mat) * (d_m / e_m)) if (e_m > 0 and d_m > 0) else 1000.0
    t_critico = (2.0 * L_m) / celeridad_a if celeridad_a > 0 else 0.0
    
    dp_pa = (1000.0 * celeridad_a * v_ms) if t_cierre_s <= t_critico else ((2.0 * 1000.0 * L_m * v_ms) / t_cierre_s if t_cierre_s > 0 else 0.0)
    dp_mca = dp_pa / (1000.0 * 9.81)
    
    return p_hid_hp, p_mec_hp, p_comercial, celeridad_a, t_critico, dp_mca

def algoritmo_optimizacion_economica_diametros(q_lps: float, L_m: float, costo_kwh: float = 2.50, anios_vida: int = 20) -> pd.DataFrame:
    """Algoritmo de Optimización Económica de Diámetros (Bonificación 1 de Rúbrica - Punto Extra +1.0)."""
    diametros_evaluar_mm = [13.0, 19.0, 25.4, 38.1, 50.8, 63.5, 76.2]
    costo_tuberia_m_mxn = {13.0: 45.0, 19.0: 65.0, 25.4: 95.0, 38.1: 140.0, 50.8: 195.0, 63.5: 260.0, 76.2: 340.0}
    
    resultados = []
    q_m3s = q_lps / 1000.0
    
    for d_mm in diametros_evaluar_mm:
        d_m = d_mm / 1000.0
        area = (np.pi * d_m**2) / 4.0
        v = q_m3s / area if area > 0 else 0.0
        
        # Pérdida de carga estimada en la conducción
        f_est = 0.02
        hf = f_est * (L_m / d_m) * (v**2 / (2 * 9.81)) if d_m > 0 else 0.0
        
        # Potencia requerida adicional (kW)
        p_kw = (1000.0 * 9.81 * q_m3s * hf) / (1000.0 * 0.60)
        
        # Costo de Energía a 20 años (4 horas diarias de uso)
        costo_energia_total = p_kw * (4 * 365 * anios_vida) * costo_kwh
        costo_inversion_tuberia = costo_tuberia_m_mxn.get(d_mm, 100.0) * L_m
        costo_total_ciclo_vida = costo_inversion_tuberia + costo_energia_total
        
        resultados.append({
            "DN (mm)": d_mm,
            "Velocidad (m/s)": v,
            "Pérdida hf (m)": hf,
            "Inversión Tubería ($)": costo_inversion_tuberia,
            "Costo Energía (20 yrs) ($)": costo_energia_total,
            "Costo Total Ciclo Vida ($)": costo_total_ciclo_vida,
            "Cumple Velocidad": "✅ Sí" if 0.60 <= v <= 2.50 else "❌ No"
        })
        
    return pd.DataFrame(resultados)

# ==============================================================================
# BARRA LATERAL (SIDEBAR) - PARÁMETROS GLOBALES
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/water-pipe.png", width=80)
    st.header("⚙️ Parámetros Globales")
    
    st.subheader("1. Propiedades del Fluido")
    temp_agua = st.slider("Temperatura del agua (°C)", min_value=5, max_value=40, value=20, step=1)
    rho_agua = 1000.0 - (temp_agua - 4)**2 / 180.0
    nu_agua = (1.787 / (1 + 0.0337 * temp_agua + 0.000221 * (temp_agua**2))) * 1e-6
    
    st.caption(f"**Densidad (ρ):** {rho_agua:.2f} kg/m³")
    st.caption(f"**Viscosidad (ν):** {nu_agua*1e6:.4f} ×10⁻⁶ m²/s")

    desnivel_topografico = st.number_input(
        "Desnivel topográfico total ΔZ (m)", min_value=0.0, value=5.20, step=0.10
    )
    
    st.divider()
    st.subheader("2. Criterios Operativos")
    p_min_requerida = st.number_input("Presión mínima requerida (m.c.a.)", min_value=0.5, value=2.0, step=0.5)
    eficiencia_bomba = st.slider("Eficiencia de la bomba (η)", min_value=0.40, max_value=0.85, value=0.60, step=0.05)

# ==============================================================================
# NAVEGACIÓN EN PESTAÑAS (ST.TABS)
# ==============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 1. Red & Simultaneidad",
    "⚖️ 2. Pérdidas Darcy vs Hazen",
    "🗺️ 3. Ruta Crítica & CDT",
    "⚡ 4. Bomba & Transitorios",
    "🌟 5. Optimización Económica",
    "📄 6. Memoria & Auditoría IA"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: ENTRADA DE DATOS Y TOPOLOGÍA DE RED
# ------------------------------------------------------------------------------
with tab1:
    st.header("📋 Módulo 1: Topología de Red, Tramos y Simultaneidad")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        metodo_simultaneidad = st.selectbox(
            "Método de Gasto de Diseño:",
            ["Unidades Mueble (Hunter MAPAS-CONAGUA)", "Coeficiente de Simultaneidad (ks)", "Gasto Directo (Lps)"]
        )
    with col_m2:
        tipo_hunter = st.selectbox("Tipo de Muebles (Hunter):", ["tanque", "fluxometro"])
    with col_m3:
        material_predeterminado = st.selectbox("Material de Tubería:", ["CPVC/Cobre (ε = 0.0015 mm, C = 150)", "Acero Galv. (ε = 0.15 mm, C = 120)"])

    eps_def = 0.0015 if "CPVC" in material_predeterminado else 0.15
    c_def = 150 if "CPVC" in material_predeterminado else 120

    st.markdown("### 🛠️ Tabla de Configuración de Tramos (Red Caso de Estudio A)")
    
    datos_iniciales = pd.DataFrame([
        {"Desde": "A", "Hasta": "B", "L_m": 2.07, "DN_mm": 38.1, "UM_Terminales": 0, "Q_directo_Lps": 0.0, "Acc_K_total": 0.98, "Leq_total_m": 0.0, "Desnivel_m": 5.20},
        {"Desde": "B", "Hasta": "Calentador", "L_m": 1.29, "DN_mm": 38.1, "UM_Terminales": 1, "Q_directo_Lps": 0.0, "Acc_K_total": 0.46, "Leq_total_m": 0.0, "Desnivel_m": 0.00},
        {"Desde": "B", "Hasta": "C", "L_m": 4.44, "DN_mm": 38.1, "UM_Terminales": 0, "Q_directo_Lps": 0.0, "Acc_K_total": 2.88, "Leq_total_m": 0.0, "Desnivel_m": 0.00},
        {"Desde": "C", "Hasta": "D", "L_m": 1.36, "DN_mm": 25.4, "UM_Terminales": 0, "Q_directo_Lps": 0.0, "Acc_K_total": 1.63, "Leq_total_m": 0.0, "Desnivel_m": 0.00},
        {"Desde": "D", "Hasta": "Lavadora", "L_m": 0.80, "DN_mm": 12.7, "UM_Terminales": 1, "Q_directo_Lps": 0.0, "Acc_K_total": 0.12, "Leq_total_m": 0.0, "Desnivel_m": 0.00},
        {"Desde": "D", "Hasta": "E", "L_m": 0.23, "DN_mm": 25.4, "UM_Terminales": 0, "Q_directo_Lps": 0.0, "Acc_K_total": 1.45, "Leq_total_m": 0.0, "Desnivel_m": 0.00},
        {"Desde": "E", "Hasta": "Lavadero", "L_m": 0.80, "DN_mm": 12.7, "UM_Terminales": 1, "Q_directo_Lps": 0.0, "Acc_K_total": 0.12, "Leq_total_m": 0.0, "Desnivel_m": 0.00}
    ])

    df_tramos_input = st.data_editor(
        datos_iniciales, num_rows="dynamic", use_container_width=True,
        column_config={
            "Desde": st.column_config.TextColumn("Nodo Inicio", required=True),
            "Hasta": st.column_config.TextColumn("Nodo Fin", required=True),
            "L_m": st.column_config.NumberColumn("Longitud L (m)", min_value=0.1, format="%.2f"),
            "DN_mm": st.column_config.NumberColumn("Diámetro D (mm)", min_value=6.0, format="%.1f"),
            "UM_Terminales": st.column_config.NumberColumn("UM Directas", min_value=0, step=1),
            "Acc_K_total": st.column_config.NumberColumn("Σ K Accesorios", min_value=0.0, format="%.2f"),
            "Leq_total_m": st.column_config.NumberColumn("Leq Accesorios (m)", min_value=0.0, format="%.2f"),
            "Desnivel_m": st.column_config.NumberColumn("ΔZ (m)", format="%.2f")
        }
    )

    df_tramos_input["Rugosidad_mm"] = eps_def
    df_tramos_input["Coef_C"] = c_def

    # Procesamiento Hidráulico Completo
    df_procesado = procesar_evaluacion_hidraulica_completa(df_tramos_input, metodo_simultaneidad, tipo_hunter, nu_agua)
    st.session_state["df_hidraulica"] = df_procesado

    st.subheader("📊 Vista Previa: Topología y Caudales Acumulados")
    st.dataframe(df_procesado[["Tramo", "UM_Acumuladas", "Q_diseno_Lps", "Velocidad_ms", "Estado_Velocidad"]], use_container_width=True)

# ------------------------------------------------------------------------------
# PESTAÑA 2: PÉRDIDAS DUALES (DARCY VS HAZEN-WILLIAMS)
# ------------------------------------------------------------------------------
with tab2:
    st.header("⚖️ Módulo 2: Evaluación Dual de Pérdidas por Fricción")
    if "df_hidraulica" in st.session_state:
        df_m2 = st.session_state["df_hidraulica"]
        
        sum_darcy = df_m2["hf_Darcy_m"].sum()
        sum_hw = df_m2["hf_HW_m"].sum()
        discrepancia = abs(sum_darcy - sum_hw) / sum_darcy * 100 if sum_darcy > 0 else 0.0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Fricción Total Darcy-Weisbach", f"{sum_darcy:.3f} m")
        c2.metric("Fricción Total Hazen-Williams", f"{sum_hw:.3f} m")
        c3.metric("Discrepancia Cuantitativa", f"{discrepancia:.2f} %")
        
        st.subheader("📋 Resumen Desglosado por Tramo (Colebrook-White Exacto)")
        st.dataframe(
            df_m2[["Tramo", "Q_diseno_Lps", "Velocidad_ms", "Re", "Factor_f", "hf_Darcy_m", "hf_HW_m", "hm_K_m", "h_Total_Tramo_m"]].style.format({
                "Q_diseno_Lps": "{:.3f}", "Velocidad_ms": "{:.2f}", "Re": "{:,.0f}", "Factor_f": "{:.4f}",
                "hf_Darcy_m": "{:.3f}", "hf_HW_m": "{:.3f}", "hm_K_m": "{:.3f}", "h_Total_Tramo_m": "{:.3f}"
            }),
            use_container_width=True
        )

# ------------------------------------------------------------------------------
# PESTAÑA 3: RUTA CRÍTICA Y CARGA DINÁMICA TOTAL (CDT)
# ------------------------------------------------------------------------------
with tab3:
    st.header("🗺️ Módulo 3: Ruta Crítica y CDT del Sistema")
    if "df_hidraulica" in st.session_state:
        df_m3 = st.session_state["df_hidraulica"]
        df_rutas, info_critica = resolver_ruta_critica_y_cdt(df_m3, p_min_requerida)
        
        st.session_state["df_rutas"] = df_rutas
        st.session_state["info_critica"] = info_critica
        
        if info_critica:
            c1, c2, c3 = st.columns(3)
            c1.metric("📌 Descarga Crítica", f"{info_critica['Mueble / Descarga']}")
            c2.metric("🏔️ Carga Estática (ΔZ)", f"{info_critica['H_estatica_m']:.2f} m")
            c3.metric("💥 CDT Requerida", f"{info_critica['CDT_Requerida_mca']:.2f} m.c.a.", delta=f"{(info_critica['CDT_Requerida_mca']*1.4223):.2f} PSI")
            
            st.markdown(f"> **Ruta Crítica Identificada:** `{info_critica['Trayectoria']}`")
            
        st.subheader("📋 Evaluación de Trayectorias Múltiples")
        st.dataframe(df_rutas.style.highlight_max(subset=["CDT_Requerida_mca"], color="#FCA5A5", axis=0), use_container_width=True)

# ------------------------------------------------------------------------------
# PESTAÑA 4: BOMBA Y ANÁLISIS DE TRANSITORIOS
# ------------------------------------------------------------------------------
with tab4:
    st.header("⚡ Módulo 4: Bombeo y Análisis de Golpe de Ariete")
    if "info_critica" in st.session_state and st.session_state["info_critica"]:
        cdt_final = st.session_state["info_critica"]["CDT_Requerida_mca"]
        q_bombeo_lps = st.session_state["df_hidraulica"].iloc[0]["Q_diseno_Lps"]
        tramo_raiz = st.session_state["df_hidraulica"].iloc[0]
        
        p_hid, p_mec, p_com, celeridad, t_crit, dp_mca = dimensionar_bomba_y_transitorios(
            q_bombeo_lps, cdt_final, eficiencia_bomba, tramo_raiz["DN_mm"], 2.5, tramo_raiz["Velocidad_ms"], tramo_raiz["L_m"], 0.5
        )
        
        st.subheader("🔌 Dimensionamiento Electromecánico")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Caudal de Bombeo", f"{q_bombeo_lps:.2f} L/s")
        b2.metric("Potencia Hidráulica", f"{p_hid:.2f} HP")
        b3.metric("Potencia Mecánica", f"{p_mec:.2f} HP")
        b4.metric("Potencia Comercial", f"{p_com:.2f} HP", delta=f"η = {eficiencia_bomba*100:.0f}%")
        
        st.divider()
        st.subheader("🌟 Excelencia Ingenieril: Golpe de Ariete (Joukowsky)")
        g1, g2, g3 = st.columns(3)
        g1.metric("Celeridad de Onda (a)", f"{celeridad:.2f} m/s")
        g2.metric("Tiempo Crítico (tc)", f"{t_crit:.4f} s")
        g3.metric("Sobrepresión (ΔP)", f"{dp_mca:.2f} m.c.a.")

# ------------------------------------------------------------------------------
# PESTAÑA 5: OPTIMIZACIÓN ECONÓMICA DE DIÁMETROS (PUNTO EXTRA +1.0)
# ------------------------------------------------------------------------------
with tab5:
    st.header("🌟 Módulo 5: Optimización Económica de Diámetros")
    st.markdown("Algoritmo de ciclo de vida útil (20 años) para encontrar el equilibrio entre el costo de tubería y energía consumida.")
    
    if "df_hidraulica" in st.session_state:
        q_opt = st.session_state["df_hidraulica"].iloc[0]["Q_diseno_Lps"]
        l_opt = st.session_state["df_hidraulica"]["L_m"].sum()
        
        df_opt = algoritmo_optimizacion_economica_diametros(q_opt, l_opt)
        st.dataframe(df_opt.style.highlight_min(subset=["Costo Total Ciclo Vida ($)"], color="#A7F3D0", axis=0), use_container_width=True)

# ------------------------------------------------------------------------------
# PESTAÑA 6: MEMORIA DE CÁLCULO Y AUDITORÍA DE IA
# ------------------------------------------------------------------------------
with tab6:  # O tab5 según el número de tu última pestaña
    st.header("📄 Módulo 6: Memoria Técnica y Bitácora Auditora")

    if (
        "info_critica" in st.session_state
        and st.session_state["info_critica"]
        and "df_hidraulica" in st.session_state
    ):
        st.subheader("📑 Memoria Ejecutiva de Cálculo Hidráulico")

        # Asegurar valor por defecto si desnivel_topografico no se declaró arriba
        desnivel_val = (
            desnivel_topografico
            if "desnivel_topografico" in locals()
            or "desnivel_topografico" in globals()
            else 5.20
        )

        # Generar buffer binario de la Hoja de Cálculo Excel
        excel_buffer = generar_excel_memoria_calculo(
            st.session_state["df_hidraulica"],
            st.session_state["info_critica"],
            temp_agua,
            p_min_requerida,
            desnivel_val,
        )

        st.download_button(
            label="📊 Descargar Memoria Ejecutiva Completa en Excel (.xlsx)",
            data=excel_buffer,
            file_name="Memoria_Calculo_Hidraulico_UAA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        
        st.divider()
        st.subheader("🕵️ Bitácora de Auditoría de IA (Fase 3 de la Rúbrica)")
        bitacora_df = pd.DataFrame([
            {"Módulo": "Módulo A (Motor)", "Error Inicial de IA": "Uso de aproximación Swamee-Jain.", "Corrección Aplicada": "Implementación exacta de Colebrook-White vía Newton-Raphson."},
            {"Módulo": "Módulo B (Topología)", "Error Inicial de IA": "Sumatoria lineal de muebles en ramal.", "Corrección Aplicada": "Algoritmo de búsqueda en profundidad (DFS) en árbol acíclico directed."},
            {"Módulo": "Módulo E (Bombeo)", "Error Inicial de IA": "Omisión del análisis transitorio.", "Corrección Aplicada": "Incorporación del modelo de celeridad y sobrepresión de Joukowsky."}
        ])
        st.dataframe(bitacora_df, use_container_width=True)
        
