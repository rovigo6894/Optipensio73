import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF 
import io

# --- IMPORTACIÓN DE TUS ARCHIVOS ---
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD
from core.mod40 import calcular_mod40

# ============================================
# FUNCIÓN PDF PROFESIONAL (SIN CARACTERES ESPECIALES)
# ============================================
def generar_pdf_comparativo(df_edades, pension_base, pensiones_edad, mejor_edad, mejor_pension, 
                           resultado_m40=None, edad_val=None, sem_val=None, sal_val=None, 
                           inf_val=None, edad_retiro=None):
    
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Logo
    try:
        pdf.image("assets/image.jpg", 10, 8, 20)
    except:
        pass
    
    # Encabezado (sin acentos)
    pdf.set_font("helvetica", "B", 18)
    pdf.set_xy(40, 12)
    pdf.cell(0, 10, "OPTIPENSION 73", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.set_xy(40, 20)
    pdf.cell(0, 5, "Consultoria Especializada en Retiro", ln=True)
    pdf.set_font("helvetica", "", 8)
    pdf.set_xy(40, 25)
    pdf.cell(0, 5, f"Reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    
    pdf.ln(15)
    
    # Datos del usuario
    if edad_val and sem_val and sal_val:
        pdf.set_fill_color(240,240,240)
        pdf.set_draw_color(200,200,200)
        pdf.rect(10, 45, 190, 25, 'DF')
        
        pdf.set_font("helvetica", "B", 10)
        pdf.set_xy(15, 50)
        pdf.cell(0, 5, f"Edad: {edad_val} años", ln=False)
        pdf.set_xy(80, 50)
        pdf.cell(0, 5, f"Semanas: {sem_val}", ln=False)
        pdf.set_xy(140, 50)
        pdf.cell(0, 5, f"Salario: ${sal_val:,.2f}", ln=True)
        
        if edad_retiro:
            pdf.set_xy(15, 57)
            pdf.cell(0, 5, f"Retiro: {edad_retiro} años", ln=False)
        if inf_val:
            pdf.set_xy(80, 57)
            pdf.cell(0, 5, f"Inflacion: {inf_val}%", ln=True)
    
    pdf.ln(15)
    
    # Resultado actual
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(0,51,102)
    pdf.cell(0, 10, f"Pension a los {edad_retiro} años", ln=True, align='C')
    pdf.set_font("helvetica", "B", 20)
    pdf.set_text_color(0,102,204)
    pdf.cell(0, 12, f"${pension_base:,.2f}", ln=True, align='C')
    
    pdf.ln(10)
    
    # Tabla comparativa
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0,0,0)
    pdf.cell(0, 8, "Comparativa por edad de retiro:", ln=True)
    pdf.set_font("helvetica", "", 10)
    
    for i, edad in enumerate(range(60,66)):
        pdf.cell(0, 6, f"{edad} años: ${pensiones_edad[i]:,.2f}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(0,102,0)
    pdf.cell(0, 7, f"Mejor opcion: {mejor_edad} años (${mejor_pension:,.2f})", ln=True)
    
    pdf.ln(8)
    
    # Modalidad 40
    if resultado_m40:
        pdf.set_text_color(0,0,0)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 8, "Modalidad 40:", ln=True)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 6, f"Pension con M40: ${resultado_m40['con_m40']:,.2f}", ln=True)
        pdf.cell(0, 6, f"Incremento: +${resultado_m40['incremento']:,.2f}", ln=True)
        pdf.cell(0, 6, f"Inversion: ${resultado_m40['inversion']:,.2f}", ln=True)
        pdf.cell(0, 6, f"Recuperacion: {resultado_m40['recuperacion']} meses", ln=True)
        pdf.cell(0, 6, f"ROI: {resultado_m40['roi']}%", ln=True)
        pdf.cell(0, 6, f"Utilidad 20 años: ${resultado_m40['utilidad_20']:,.2f}", ln=True)
    
    # Firma
    pdf.set_y(250)
    pdf.line(120, 255, 190, 255)
    try:
        pdf.image("assets/firma.png", 140, 240, 40)
    except:
        pass
    pdf.set_xy(120, 257)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(70, 5, "Ing. Roberto Villarreal Glz", ln=True, align='C')
    pdf.set_xy(120, 262)
    pdf.set_font("helvetica", "", 8)
    pdf.cell(70, 5, "Director General", ln=True, align='C')
    
    return bytes(pdf.output())

# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Optipensión 73 PRO", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { 
        background-color: #111827; 
        min-width: 260px !important;
        max-width: 260px !important;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        width: 120px !important;
        height: auto;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .metric-container {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 20px;
    }
    .metric-container-pro {
        background-color: #064e3b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #10b981;
        margin-bottom: 20px;
    }
    .metric-label {
        font-size: 14px;
        color: #94a3b8;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    try: st.image("assets/image.jpg", width=120)
    except: st.title("OPTIPENSIÓN 73")
    
    st.header("📍 Parámetros Base")
    edad_val = st.number_input("Edad actual", 50, 65, 57)
    sem_val = st.number_input("Semanas Reconocidas", 500, 3000, 1315)
    sal_val = st.number_input("Salario Diario (SBC)", 100.0, 3500.0, 959.15)
    inf_val = st.number_input("Inflación Est. %", value=4.5)
    esp_val = st.checkbox("Asignación Esposa", value=True)

# ============================================
# CABECERA PRINCIPAL
# ============================================
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try: st.image("assets/image.jpg", width=100)
    except: pass
with col_title:
    st.title("OPTIPENSIÓN 73")
    st.subheader("Consultoría Especializada en Retiro")

# ============================================
# PESTAÑAS
# ============================================
tab1, tab2, tab3 = st.tabs(["📊 Escenario Actual", "🚀 Estrategia Mod 40", "📈 ROI & Comparativa"])


# ============================================
# PESTAÑA 1: ESCENARIO ACTUAL (CÁLCULOS CORREGIDOS)
# ============================================
with tab1:
    st.markdown("### 📊 Escenario Actual")
    
    # --- SELECTOR DE EDAD DE RETIRO ---
    edad_retiro = st.select_slider(
        "🎯 Edad de retiro deseada",
        options=[60, 61, 62, 63, 64, 65],
        value=60,
        help="Selecciona la edad a la que planeas retirarte"
    )
    st.session_state.edad_retiro = edad_retiro
    
    # Mostrar factor por edad
    factor_edad = FACTORES_EDAD.get(edad_retiro, 0.75)
    st.caption(f"Factor por edad aplicado: {factor_edad*100:.0f}%")
    
    # --- CÁLCULO DE PENSIÓN BASE (a los 60 años) ---
    p_base, _ = calcular_pension_ley73(sal_val, sem_val, edad_val, 60, 0, esp_val)
    
    # --- GENERAR TABLA DE PROYECCIÓN CORREGIDA ---
    datos = []
    # Proyectar hasta la edad máxima (65) o la seleccionada, la que sea mayor
    edad_maxima = max(edad_retiro, 65)
    
    for i in range(edad_maxima - edad_val + 1):
        ed_i = edad_val + i
        años_desde_hoy = i
        
        # Factor de inflación acumulado desde hoy
        f_inf = (1 + (inf_val/100)) ** años_desde_hoy
        
        # Para la edad actual, usar el valor base exacto
        if ed_i == edad_val:
            p_i = p_base
        
        # Para edades futuras
        else:
            # Si es menor de 60 años, solo inflación (mismo factor 75%)
            if ed_i < 60:
                p_i = p_base * f_inf
            
            # Si tiene 60 años o más, aplicar factor de edad + inflación
            else:
                factor_ed = FACTORES_EDAD.get(ed_i, 0.75)
                # La pensión base es a los 60 con factor 75%, por eso dividimos entre 0.75
                p_i = p_base * f_inf * (factor_ed / 0.75)
        
        datos.append({
            "Año": 2026 + años_desde_hoy,
            "Edad": ed_i,
            "Pensión": round(p_i, 2)
        })
    
    df_actual = pd.DataFrame(datos)
    
    # --- OBTENER VALORES PARA MOSTRAR ---
    p_hoy = df_actual[df_actual['Edad'] == edad_val]['Pensión'].values[0]
    p_futura = df_actual[df_actual['Edad'] == edad_retiro]['Pensión'].values[0]
    
    # --- GUARDAR EN SESSION STATE ---
    st.session_state.pension_futura = p_futura
    st.session_state.pension_base = p_base
    
    # --- TARJETAS DE RESULTADOS ---
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Pensión Estimada Hoy</div>
            <div class="metric-value">${p_hoy:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container-pro">
            <div class="metric-label">Pensión a los {edad_retiro} años</div>
            <div class="metric-value">${p_futura:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # --- BOTÓN PDF PROFESIONAL ---
    if st.button("📥 Descargar Reporte PDF (Escenario Actual)", use_container_width=True):
        from fpdf import FPDF
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        # Logo
        try:
            pdf.image("assets/image.jpg", 10, 8, 20)
        except:
            pass
        
        # Encabezado
        pdf.set_font("helvetica", "B", 18)
        pdf.set_xy(40, 12)
        pdf.cell(0, 10, "OPTIPENSIÓN 73", ln=True)
        pdf.set_font("helvetica", "", 10)
        pdf.set_xy(40, 20)
        pdf.cell(0, 5, "Consultoría Especializada en Retiro", ln=True)
        pdf.set_font("helvetica", "", 8)
        pdf.set_xy(40, 25)
        pdf.cell(0, 5, f"Reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        
        pdf.ln(15)
        
        # Datos del usuario en recuadro
        pdf.set_fill_color(240,240,240)
        pdf.set_draw_color(200,200,200)
        pdf.rect(10, 45, 190, 25, 'DF')
        
        pdf.set_font("helvetica", "B", 10)
        pdf.set_xy(15, 50)
        pdf.cell(0, 5, f"Edad: {edad_val} años", ln=False)
        pdf.set_xy(80, 50)
        pdf.cell(0, 5, f"Semanas: {sem_val}", ln=False)
        pdf.set_xy(140, 50)
        pdf.cell(0, 5, f"Salario: ${sal_val:,.2f}", ln=True)
        
        pdf.set_xy(15, 57)
        pdf.cell(0, 5, f"Retiro: {edad_retiro} años", ln=False)
        pdf.set_xy(80, 57)
        pdf.cell(0, 5, f"Inflación: {inf_val}%", ln=True)
        
        pdf.ln(15)
        
        # Resultado destacado
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0,51,102)
        pdf.cell(0, 10, "PENSIÓN ESTIMADA", ln=True, align='C')
        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(0,102,204)
        pdf.cell(0, 15, f"${p_futura:,.2f}", ln=True, align='C')
        
        pdf.ln(10)
        
        # --- TABLA DE PROYECCIÓN (CENTRADA) ---
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(0,0,0)
        pdf.cell(0, 8, "Proyección a 5 años:", ln=True, align='C')
        pdf.ln(3)
        
        # Calcular posición para centrar la tabla
        ancho_total = 150  # 45+45+60
        margen_izquierdo = (210 - ancho_total) / 2  # 210mm es el ancho de A4
        
        # Encabezados de tabla
        pdf.set_font("helvetica", "B", 10)
        pdf.set_fill_color(200,200,200)
        pdf.set_x(margen_izquierdo)
        pdf.cell(45, 8, "Año", 1, 0, "C", True)
        pdf.cell(45, 8, "Edad", 1, 0, "C", True)
        pdf.cell(60, 8, "Pensión", 1, 1, "C", True)
        
        # Datos (primeros 5 años)
        pdf.set_font("helvetica", "", 9)
        for i in range(min(5, len(df_actual))):
            row = df_actual.iloc[i]
            pdf.set_x(margen_izquierdo)
            pdf.cell(45, 7, str(int(row['Año'])), 1, 0, "C")
            pdf.cell(45, 7, str(int(row['Edad'])), 1, 0, "C")
            pdf.cell(60, 7, f"${row['Pensión']:,.2f}", 1, 1, "C")
        
        pdf.ln(10)
        
        # --- FIRMA CON CARGO (CENTRADA) ---
        pdf.set_y(250)
        pdf.line(120, 255, 190, 255)
        try:
            pdf.image("assets/firma.png", 140, 240, 40)
        except:
            pass
        
        # Nombre centrado
        pdf.set_xy(120, 257)
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(70, 5, "Ing. Roberto Villarreal Glz", ln=True, align='C')
        
        # Cargo centrado DEBAJO del nombre
        pdf.set_xy(120, 262)
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(70, 5, "Director General - Optipensión 73", ln=True, align='C')
        
        st.download_button(
            "📥 Guardar PDF",
            bytes(pdf.output()),
            "Reporte_Pension.pdf",
            "application/pdf"
        )

        
# ============================================
# PESTAÑA 2: MODALIDAD 40
# ============================================
with tab2:
    st.markdown("### 🚀 Estrategia de Modalidad 40")
    
    pension_base_m40 = st.session_state.get('pension_futura', 16382.65)
    edad_retiro = st.session_state.get('edad_retiro', 60)
    
    st.info(f"""
    🎯 **Edad de retiro: {edad_retiro} años**  
    💰 **Pensión base (sin M40): ${pension_base_m40:,.2f}**
    """)
    
    col_ref1, col_ref2, col_ref3 = st.columns(3)
    with col_ref1:
        st.metric("Edad actual", f"{edad_val} años")
    with col_ref2:
        st.metric("Semanas", f"{sem_val}")
    with col_ref3:
        st.metric("Salario actual", f"${sal_val:,.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        sal_m40_tope = st.number_input(
            "💰 Salario a cotizar en M40",
            min_value=500.0,
            max_value=5000.0,
            value=2932.0,
            step=50.0
        )
    with col2:
        meses_m40 = st.select_slider(
            "📅 Meses a cotizar",
            options=[6, 12, 18, 24, 30, 36, 42, 48],
            value=36
        )
    
    if st.button("📈 Calcular impacto M40", use_container_width=True, type="primary"):
        
        resultado_m40 = calcular_mod40(
            edad_val, sem_val, sal_val, sal_m40_tope, meses_m40, edad_retiro, esp_val
        )
        
        st.session_state.resultado_m40 = resultado_m40
        st.session_state.m40_calculado = True
        
        st.markdown("---")
        st.markdown("### 📊 Resultado de la Estrategia")
        
        incremento = resultado_m40['con_m40'] - pension_base_m40
        
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Pensión Base (sin M40)", f"${pension_base_m40:,.2f}")
        with col_r2:
            st.metric("Pensión con M40", f"${resultado_m40['con_m40']:,.2f}")
        with col_r3:
            st.metric("Incremento mensual", f"+${incremento:,.2f}")
        
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.metric("Inversión total", f"${resultado_m40['inversion']:,.2f}")
        with col_d2:
            st.metric("Recuperación", f"{resultado_m40['recuperacion']} meses")
        with col_d3:
            st.metric("ROI a 20 años", f"{resultado_m40['roi']}%")
        
        fig = go.Figure(data=[
            go.Bar(name='Sin M40', x=['Comparación'], y=[pension_base_m40],
                   marker_color='#3b82f6'),
            go.Bar(name='Con M40', x=['Comparación'], y=[resultado_m40['con_m40']],
                   marker_color='#10b981')
        ])
        fig.update_layout(title="Comparación rápida", height=300)
        st.plotly_chart(fig, use_container_width=True)



# ============================================
# PESTAÑA 3: ROI Y COMPARATIVA (UNA SOLA HOJA + DESLINDE)
# ============================================
with tab3:
    st.markdown("### 📈 Análisis Comparativo Profesional")
    
    pension_base = st.session_state.get('pension_futura', 16382.65)
    edad_retiro = st.session_state.get('edad_retiro', 60)
    salario = sal_val
    semanas = sem_val
    edad = edad_val
    inflacion = inf_val / 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Tu escenario actual")
        st.markdown(f"""
        <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6;">
            <p style="color: #94a3b8; margin:0">Edad de retiro</p>
            <p style="color: white; font-size: 24px; font-weight: bold; margin:0">{edad_retiro} años</p>
            <p style="color: #94a3b8; margin:5px 0 0 0">Pensión estimada</p>
            <p style="color: white; font-size: 28px; font-weight: bold; margin:0">${pension_base:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⚙️ Parámetros base")
        st.markdown(f"""
        <div style="background-color: #1e293b; padding: 15px; border-radius: 10px;">
            <table style="width:100%; color:white;">
                <tr><td>Edad actual</td><td style="text-align:right; font-weight:bold;">{edad} años</td></tr>
                <tr><td>Semanas</td><td style="text-align:right; font-weight:bold;">{semanas}</td></tr>
                <tr><td>Salario</td><td style="text-align:right; font-weight:bold;">${salario:,.2f}</td></tr>
                <tr><td>Inflación</td><td style="text-align:right; font-weight:bold;">{inf_val}%</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    from config.parametros import FACTORES_EDAD
    p_base_60, _ = calcular_pension_ley73(salario, semanas, edad, 60, 0, esp_val)
    
    edades = []
    pensiones_edad = []
    
    for ed in range(60, 66):
        factor = FACTORES_EDAD.get(ed, 1.0)
        años_faltan = max(0, ed - edad)
        f_inf = (1 + inflacion) ** años_faltan
        p_ed = p_base_60 * (factor / 0.75) * f_inf
        edades.append(ed)
        pensiones_edad.append(p_ed)
    
    st.markdown("#### 📊 Comparativa por edad de retiro")
    
    colores = ['#3b82f6' if ed == edad_retiro else '#94a3b8' for ed in edades]
    
    fig = go.Figure(data=[
        go.Bar(
            x=[f"{ed} años" for ed in edades],
            y=pensiones_edad,
            marker_color=colores,
            text=[f"${p:,.0f}" for p in pensiones_edad],
            textposition='outside'
        )
    ])
    
    fig.add_hline(
        y=pension_base,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text=f" Tu selección ({edad_retiro} años) ",
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title="Pensión mensual según edad de retiro",
        xaxis_title="Edad de retiro",
        yaxis_title="Pensión mensual ($)",
        yaxis_tickformat="$,.0f",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("#### 📋 Análisis de diferencias")
    
    mejor_edad = edades[pensiones_edad.index(max(pensiones_edad))]
    mejor_pension = max(pensiones_edad)
    
    datos_tabla = []
    for i, ed in enumerate(edades):
        dif = pensiones_edad[i] - pension_base
        datos_tabla.append({
            "Edad": f"{ed} años",
            "Pensión mensual": f"${pensiones_edad[i]:,.2f}",
            "Diferencia mensual": f"+${dif:,.2f}" if dif > 0 else f"${dif:,.2f}",
            "Diferencia anual": f"+${dif * 12:,.0f}" if dif > 0 else f"${dif * 12:,.0f}"
        })
    
    df_tabla = pd.DataFrame(datos_tabla)
    st.dataframe(df_tabla, use_container_width=True, hide_index=True)
    
    st.success(f"""
    ### ✨ Mejor estrategia
    
    **Retirarte a los {mejor_edad} años** te daría una pensión de **${mejor_pension:,.2f}**,
    lo que representa **+${mejor_pension - pension_base:,.2f} mensuales**
    y **+${(mejor_pension - pension_base) * 12:,.0f} anuales** más que tu escenario actual.
    """)
    
    st.markdown("---")
    
    st.markdown("#### 🚀 Impacto de Modalidad 40")
    
    if 'resultado_m40' in st.session_state and st.session_state.get('m40_calculado', False):
        res = st.session_state.resultado_m40
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Pensión actual", f"${pension_base:,.2f}")
        with col_m2:
            st.metric("Con M40", f"${res['con_m40']:,.2f}")
        with col_m3:
            st.metric("Incremento", f"+${res['incremento']:,.2f}")
        
        fig_m40 = go.Figure(data=[
            go.Bar(name='Sin M40', x=['Comparación'], y=[pension_base],
                   marker_color='#3b82f6'),
            go.Bar(name='Con M40', x=['Comparación'], y=[res['con_m40']],
                   marker_color='#10b981')
        ])
        fig_m40.update_layout(
            title="Pensión actual vs Modalidad 40",
            yaxis_title="Pensión mensual ($)",
            yaxis_tickformat="$,.0f",
            height=400,
            barmode='group'
        )
        st.plotly_chart(fig_m40, use_container_width=True)
        
        with st.expander("📋 Ver análisis detallado de Modalidad 40"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.metric("Inversión total", f"${res['inversion']:,.2f}")
                st.metric("Recuperación", f"{res['recuperacion']} meses")
            with col_d2:
                st.metric("ROI a 20 años", f"{res['roi']}%")
                st.metric("Utilidad neta 20 años", f"${res['utilidad_20']:,.2f}")
    else:
        st.info("💡 **Calcula un escenario de Modalidad 40 en la pestaña 2** para ver la comparativa.")
    
    st.markdown("---")
    
    st.markdown("#### 💰 Proyección de vida financiera")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        expectativa = st.number_input("Expectativa de vida (años)", 70, 100, 85)
    
    años_retiro = expectativa - edad_retiro
    ingreso_total = pension_base * 12 * años_retiro
    
    with col_p2:
        st.metric("Ingreso total estimado", f"${ingreso_total:,.0f}")
    
    if 'resultado_m40' in st.session_state:
        ingreso_m40 = st.session_state.resultado_m40['con_m40'] * 12 * años_retiro
        with col_p3:
            st.metric(
                "Con Modalidad 40",
                f"${ingreso_m40:,.0f}",
                delta=f"+${ingreso_m40 - ingreso_total:,.0f}"
            )
    
    st.markdown("---")
    
    # ============================================
    # FUNCIÓN PDF PROFESIONAL (UNA SOLA HOJA + DESLINDE LEGAL)
    # ============================================
    def generar_pdf_comparativo_profesional(df_edades, pension_base, pensiones_edad, mejor_edad, mejor_pension, 
                                           resultado_m40=None, edad_val=None, sem_val=None, sal_val=None, 
                                           inf_val=None, edad_retiro=None):
        """
        Genera un PDF profesional en UNA SOLA HOJA con deslinde legal
        """
        from fpdf import FPDF
        import datetime
        
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        # Márgenes reducidos para aprovechar espacio
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        
        # --- Logo ---
        try:
            pdf.image("assets/image.jpg", 15, 8, 20)
        except:
            pass
        
        # --- Encabezado compacto ---
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(0, 51, 102)
        pdf.set_xy(40, 12)
        pdf.cell(0, 8, "OPTIPENSION 73", ln=True)
        
        pdf.set_font("helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(40, 20)
        pdf.cell(0, 4, "Consultoria Especializada en Retiro", ln=True)
        pdf.set_xy(40, 24)
        pdf.cell(0, 4, f"Reporte: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
        
        pdf.ln(8)
        
        # --- Tarjeta de datos compacta ---
        if edad_val and sem_val and sal_val:
            pdf.set_fill_color(245, 245, 245)
            pdf.set_draw_color(200, 200, 200)
            pdf.rect(15, 35, 180, 18, 'DF')
            
            pdf.set_font("helvetica", "B", 8)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(20, 38)
            pdf.cell(0, 4, f"Edad: {edad_val} a | Sem: {sem_val} | Sal: ${sal_val:,.2f}", ln=False)
            pdf.set_xy(20, 43)
            pdf.cell(0, 4, f"Retiro: {edad_retiro} a | Infl: {inf_val}%", ln=True)
        
        pdf.ln(12)
        
        # --- Título sección compacto ---
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, "COMPARATIVA POR EDAD", ln=True, align='C')
        pdf.ln(2)
        
        # --- Tabla comparativa compacta ---
        ancho_total = 160
        margen_izquierdo = (210 - ancho_total) / 2
        
        # Encabezados más pequeños
        pdf.set_font("helvetica", "B", 8)
        pdf.set_fill_color(0, 51, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_x(margen_izquierdo)
        pdf.cell(40, 6, "Edad", 1, 0, "C", True)
        pdf.cell(50, 6, "Mensual", 1, 0, "C", True)
        pdf.cell(70, 6, "Anual", 1, 1, "C", True)
        
        # Datos más compactos
        pdf.set_font("helvetica", "", 7)
        pdf.set_text_color(0, 0, 0)
        fill = False
        for i, edad in enumerate(range(60, 66)):
            pdf.set_x(margen_izquierdo)
            pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(40, 5, f"{edad} a", 1, 0, "C", fill)
            pdf.cell(50, 5, f"${pensiones_edad[i]:,.2f}", 1, 0, "R", fill)
            pdf.cell(70, 5, f"${pensiones_edad[i] * 12:,.2f}", 1, 1, "R", fill)
            fill = not fill
        
        pdf.ln(4)
        
        # --- Mejor opción compacta ---
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 5, f"MEJOR: {mejor_edad} a - ${mejor_pension:,.2f}", ln=True, align='C')
        pdf.ln(2)
        
        # --- Modalidad 40 compacta (si aplica) ---
        if resultado_m40:
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 5, "MODALIDAD 40", ln=True, align='C')
            pdf.ln(1)
            
            # Una sola línea con los datos clave
            pdf.set_font("helvetica", "", 7)
            pdf.set_text_color(0, 0, 0)
            texto_m40 = f"Pension M40: ${resultado_m40['con_m40']:,.2f} | "
            texto_m40 += f"+${resultado_m40['incremento']:,.2f} | "
            texto_m40 += f"Inv: ${resultado_m40['inversion']:,.2f} | "
            texto_m40 += f"Rec: {resultado_m40['recuperacion']}m | "
            texto_m40 += f"ROI: {resultado_m40['roi']}%"
            pdf.multi_cell(0, 3, texto_m40, align='C')
            pdf.ln(2)
        
        # ===== DESLINDE LEGAL (en la misma hoja) =====
        pdf.set_y(230)  # Posición fija cerca del final
        
        # Línea separadora
        pdf.set_draw_color(200, 200, 200)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)
        
        # Texto legal en letra pequeña
        pdf.set_font("helvetica", "I", 6)
        pdf.set_text_color(100, 100, 100)
        deslinde = """NOTA LEGAL: Este reporte es una estimación basada en la Ley 73 del IMSS. Los montos son aproximados y no constituyen una garantía de pago. "
        "Recomendamos consultar con un asesor certificado. Optipensión 73 no se hace responsable por decisiones tomadas con esta información."""
        pdf.multi_cell(0, 3, deslinde, align='C')
        pdf.ln(2)
        
        # ===== FIRMA COMPACTA =====
        # Línea de firma
        pdf.set_draw_color(0, 51, 102)
        pdf.line(120, pdf.get_y() + 2, 190, pdf.get_y() + 2)
        
        # Imagen de firma
        try:
            pdf.image("assets/firma.png", 140, pdf.get_y() + 3, 35)
            pdf.ln(10)
        except:
            pdf.ln(5)
        
        # Nombre y cargo
        pdf.set_font("helvetica", "B", 8)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 4, "Ing. Roberto Villarreal Glz", ln=True, align='C')
        
        pdf.set_font("helvetica", "", 7)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 3, "Director General - Optipensión 73", ln=True, align='C')
        
        # Pie
        pdf.ln(2)
        pdf.set_font("helvetica", "I", 5)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 2, "Optipensión 73 - Consultoría Especializada en Pensiones", ln=True, align='C')
        
        return bytes(pdf.output())
    
    # --- Botón de descarga ---
    if st.button("📥 DESCARGAR REPORTE COMPLETO PDF", use_container_width=True):
        import datetime
        
        pdf_bytes = generar_pdf_comparativo_profesional(
            None,
            pension_base,
            pensiones_edad,
            mejor_edad,
            mejor_pension,
            st.session_state.get('resultado_m40'),
            edad,
            semanas,
            salario,
            inf_val,
            edad_retiro
        )
        
        st.download_button(
            "📥 Guardar PDF",
            pdf_bytes,
            f"Reporte_Comparativa_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "application/pdf"
        )

        
# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown(
"""
<div style='text-align:left; font-size:12px; color:#666;'>

### 📌 TÉRMINOS Y CONDICIONES
El uso de este simulador implica la aceptación de los siguientes términos:
* **Naturaleza del servicio**: Este simulador proporciona estimaciones basadas en modelos matemáticos y la Ley 73 del IMSS. Los resultados son aproximados y no constituyen un dictamen oficial ni una garantía de pago.
* **Limitación de responsabilidad**: Optipensión 73 no se hace responsable por decisiones tomadas basadas exclusivamente en los resultados. Se recomienda consultar con un asesor certificado.

---

### 🔒 AVISO DE PRIVACIDAD
**Protección de datos**: Esta aplicación NO almacena, guarda ni comparte ningún dato personal ingresado por el usuario.

---

### ⚖️ LEGAL
**Propiedad intelectual**: El código, diseño y contenido de Optipensión 73 son propiedad del Ing. Roberto Villarreal Glz. © 2026. Todos los derechos reservados.

📧 **Email**: contacto@optipension73.com  
📱 **WhatsApp**: 871 579 1810  
📍 **Oficina**: Torreón, Coahuila · México

<br>
<div style='text-align:center;'>
**© 2026 Optipensión 73 · Versión PRO**
</div>

</div>
""",
unsafe_allow_html=True
)
