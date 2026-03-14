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

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Optipensión 73 PRO", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- ESTILOS CSS: SIDEBAR, LOGO Y RECUADROS DE COLORES ---
st.markdown("""
    <style>
    /* Sidebar angosto de 260px */
    [data-testid="stSidebar"] { 
        background-color: #111827; 
        min-width: 260px !important;
        max-width: 260px !important;
    }
    /* Logo pequeño en sidebar */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        width: 120px !important;
        height: auto;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    /* Estilo para los recuadros de pensiones */
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
    /* Ajuste de Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PDF PROFESIONAL ---
def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # LOGO
    try:
        pdf.image("assets/image.jpg", 10, 8, 20)
    except:
        pass
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_xy(40, 12)
    pdf.cell(0, 10, "OPTIPENSIÓN 73", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.set_xy(40, 20)
    pdf.cell(0, 5, "Consultoría Especializada en Retiro", ln=True)
    pdf.set_font("helvetica", "", 8)
    pdf.set_xy(40, 25)
    pdf.cell(0, 5, f"Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    
    pdf.ln(15)
    
    # DATOS DEL USUARIO
    pdf.set_fill_color(240, 240, 240)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(10, 45, 190, 25, 'DF')
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_xy(15, 50)
    pdf.cell(0, 5, f"Edad: {edad_act} años", ln=False)
    pdf.set_xy(80, 50)
    pdf.cell(0, 5, f"Semanas: {sem}", ln=False)
    pdf.set_xy(140, 50)
    pdf.cell(0, 5, f"Salario: ${sal:,.2f}", ln=True)
    
    pdf.set_xy(15, 57)
    pdf.cell(0, 5, f"Objetivo: {edad_obj} años", ln=False)
    pdf.set_xy(80, 57)
    pdf.cell(0, 5, f"Asignación esposa: Sí", ln=True)
    
    pdf.ln(12)
    
    # RESULTADOS
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "RESULTADOS", ln=True, align='C')
    
    # Recuadro Pensión Hoy
    pdf.set_fill_color(230, 240, 255)
    pdf.set_draw_color(0, 51, 102)
    pdf.rect(20, 85, 80, 20, 'DF')
    pdf.set_xy(25, 90)
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, "Pensión Hoy", ln=True)
    pdf.set_xy(25, 97)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 5, f"${p_hoy:,.2f}", ln=True)
    
    # Recuadro Pensión Proyectada
    pdf.set_fill_color(220, 255, 220)
    pdf.set_draw_color(0, 102, 0)
    pdf.rect(110, 85, 80, 20, 'DF')
    pdf.set_xy(115, 90)
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, f"Pensión a los {edad_obj} años", ln=True)
    pdf.set_xy(115, 97)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 102, 0)
    pdf.cell(0, 5, f"${p_proyectada:,.2f}", ln=True)
    
    pdf.ln(30)
    
    # TABLA DE PROYECCIÓN
    ancho_total = 150
    margen_izquierdo = (210 - ancho_total) / 2
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(200, 200, 200)
    
    pdf.set_x(margen_izquierdo)
    pdf.cell(45, 8, "Año", 1, 0, "C", True)
    pdf.cell(45, 8, "Edad", 1, 0, "C", True)
    pdf.cell(60, 8, "Pensión Mensual", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 9)
    for i, row in df.iterrows():
        if i < 12:
            pdf.set_x(margen_izquierdo)
            pdf.cell(45, 7, str(int(row['Año'])), 1, 0, "C")
            pdf.cell(45, 7, str(int(row['Edad'])), 1, 0, "C")
            pdf.cell(60, 7, f"${row['Pensión']:,.2f}", 1, 1, "C")
    
    # NOTA LEGAL
    pdf.set_y(205)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "NOTA IMPORTANTE:", ln=True, align='C')
    pdf.set_font("helvetica", "", 7)
    pdf.cell(0, 4, "Este reporte es una estimación basada en la Ley 73 del IMSS y los datos proporcionados.", ln=True, align='C')
    pdf.cell(0, 4, "No constituye un dictamen oficial ni una garantía de pago por parte del Instituto.", ln=True, align='C')
    pdf.cell(0, 4, "Los resultados pueden variar según la legislación vigente y condiciones individuales.", ln=True, align='C')
    pdf.cell(0, 4, "Se recomienda validar la información con un asesor certificado.", ln=True, align='C')
    
    # FIRMA
    pdf.set_y(245)
    pdf.line(120, 250, 190, 250)
    
    try:
        pdf.image("assets/firma.png", 140, 235, 40)
    except:
        pass
    
    pdf.set_xy(120, 252)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(70, 5, "Ing. Roberto Villarreal Glz", ln=True, align='C')
    
    pdf.set_xy(120, 257)
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(70, 5, "Director General - Optipensión 73", ln=True, align='C')
    
    return bytes(pdf.output())

# --- SIDEBAR ---
with st.sidebar:
    try: st.image("assets/image.jpg", width=120)
    except: st.title("OPTIPENSIÓN 73")
    
    st.header("📍 Parámetros Base")
    edad_val = st.number_input("Edad actual", 50, 65, 57)
    sem_val = st.number_input("Semanas Reconocidas", 500, 3000, 1315)
    sal_val = st.number_input("Salario Diario (SBC)", 100.0, 3500.0, 959.15)
    inf_val = st.number_input("Inflación Est. %", value=4.5)
    esp_val = st.checkbox("Asignación Esposa", value=True)

# --- CABECERA PRINCIPAL ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try: st.image("assets/image.jpg", width=100)
    except: pass
with col_title:
    st.title("OPTIPENSIÓN 73")
    st.subheader("Consultoría Especializada en Retiro")

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📊 Escenario Actual", "🚀 Estrategia Mod 40", "📈 ROI & Comparativa"])


# ============================================
# PESTAÑA 1: ESCENARIO ACTUAL
# ============================================
with tab1:
    st.markdown("### 📊 Escenario Actual")
    
    # SELECTOR DE EDAD DE RETIRO
    edad_retiro = st.select_slider(
        "🎯 Edad de retiro deseada",
        options=[60, 61, 62, 63, 64, 65],
        value=60,
        help="Selecciona la edad a la que planeas retirarte"
    )
    # Guardar en session_state
    st.session_state.edad_retiro = edad_retiro
    
    # Mostrar factor de edad
    factor_edad = FACTORES_EDAD.get(edad_retiro, 0.75)
    st.caption(f"Factor por edad aplicado: {factor_edad*100:.0f}%")
    
    # Calcular pensión base (con inflación 0)
    p_base, _ = calcular_pension_ley73(sal_val, sem_val, edad_val, 60, 0, esp_val)
    
    # Generar tabla
    datos = []
    for i in range((edad_retiro - edad_val) + 1):
        ed_i = edad_val + i
        años_desde_hoy = i
        factor_ed = FACTORES_EDAD.get(ed_i, 1.0)
        f_inf = (1 + (inf_val/100)) ** años_desde_hoy
        
        if ed_i == edad_val:
            p_i = p_base
        else:
            p_i = p_base * f_inf * (factor_ed / 0.75)
        
        datos.append({
            "Año": 2026 + años_desde_hoy,
            "Edad": ed_i,
            "Pensión": round(p_i, 2)
        })
    
    df_actual = pd.DataFrame(datos)
    
    # Resultados
    p_hoy = df_actual[df_actual['Edad'] == edad_val]['Pensión'].values[0]
    p_futura = df_actual[df_actual['Edad'] == edad_retiro]['Pensión'].values[0]
    
    # GUARDAR PARA PESTAÑA 2
    st.session_state.pension_futura = p_futura
    st.session_state.pension_base = p_base
    
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
    
    # Botón PDF
    if st.button("📥 Descargar Reporte PDF", use_container_width=True):
        pdf_out = generar_pdf_pro(df_actual, p_hoy, p_futura, edad_val, edad_retiro, sal_val, sem_val)
        st.download_button("Click para Guardar", pdf_out, "Reporte_Optipension.pdf")



# ============================================
# PESTAÑA 2: MODALIDAD 40 (CORREGIDA)
# ============================================
with tab2:
    st.markdown("### 🚀 Estrategia de Modalidad 40")
    
    # Recuperar valores de pestaña 1
    pension_base_m40 = st.session_state.get('pension_futura', 16382.65)
    edad_retiro = st.session_state.get('edad_retiro', 60)
    
    st.info(f"""
    🎯 **Edad de retiro: {edad_retiro} años**  
    💰 **Pensión base (sin M40): ${pension_base_m40:,.2f}**
    """)
    
    # Datos actuales
    col_ref1, col_ref2, col_ref3 = st.columns(3)
    with col_ref1:
        st.metric("Edad actual", f"{edad_val} años")
    with col_ref2:
        st.metric("Semanas", f"{sem_val}")
    with col_ref3:
        st.metric("Salario actual", f"${sal_val:,.2f}")
    
    st.markdown("---")
    
    # Parámetros M40
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
    
    # Botón de cálculo
    if st.button("📈 Calcular impacto M40", use_container_width=True, type="primary"):
        
        # ✅ NOMBRE CORRECTO DE LA FUNCIÓN
        from core.mod40 import calcular_mod40
        resultado_m40 = calcular_mod40(
            edad_val, sem_val, sal_val, sal_m40_tope, meses_m40, edad_retiro, esp_val
        )
        
        # ✅ GUARDAR EN SESSION_STATE (¡ESTAS LÍNEAS SON CLAVE!)
        st.session_state.resultado_m40 = resultado_m40
        st.session_state.m40_calculado = True
        
        st.markdown("---")
        st.markdown("### 📊 Resultado de la Estrategia")
        
        # Usar la pensión base de pestaña 1 como referencia
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
        
        # Gráfica rápida
        import plotly.graph_objects as go
        fig = go.Figure(data=[
            go.Bar(name='Sin M40', x=['Comparación'], y=[pension_base_m40],
                   marker_color='#3b82f6'),
            go.Bar(name='Con M40', x=['Comparación'], y=[resultado_m40['con_m40']],
                   marker_color='#10b981')
        ])
        fig.update_layout(title="Comparación rápida", height=300)
        st.plotly_chart(fig, use_container_width=True)
        


# ============================================
# PESTAÑA 3: ROI Y COMPARATIVA (VERSIÓN PROFESIONAL)
# ============================================
with tab3:
    st.markdown("### 📈 Análisis Comparativo Profesional")
    
    # --- RECUPERAR DATOS DE SESIÓN ---
    pension_base = st.session_state.get('pension_futura', 16382.65)
    edad_retiro = st.session_state.get('edad_retiro', 60)
    salario = sal_val
    semanas = sem_val
    edad = edad_val
    inflacion = inf_val / 100
    
    # --- MOSTAR RESUMEN DEL ESCENARIO ACTUAL ---
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
    
    # --- CALCULAR PENSIONES PARA TODAS LAS EDADES (60-65) ---
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
    
    # --- GRÁFICA DE BARRAS PROFESIONAL ---
    st.markdown("#### 📊 Comparativa por edad de retiro")
    
    colores = ['#3b82f6' if ed == edad_retiro else '#94a3b8' for ed in edades]
    
    fig = go.Figure(data=[
        go.Bar(
            x=[f"{ed} años" for ed in edades],
            y=pensiones_edad,
            marker_color=colores,
            text=[f"${p:,.0f}" for p in pensiones_edad],
            textposition='outside',
            textfont=dict(size=12)
        )
    ])
    
    fig.add_hline(
        y=pension_base,
        line_dash="dash",
        line_color="#ef4444",
        line_width=2,
        annotation_text=f" Tu selección ({edad_retiro} años) ",
        annotation_position="bottom right",
        annotation_font_size=12,
        annotation_font_color="#ef4444"
    )
    
    fig.update_layout(
        title=dict(
            text="Pensión mensual según edad de retiro",
            font=dict(size=16)
        ),
        xaxis_title="Edad de retiro",
        yaxis_title="Pensión mensual ($)",
        yaxis_tickformat="$,.0f",
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # --- TABLA COMPARATIVA PROFESIONAL ---
    st.markdown("#### 📋 Análisis de diferencias")
    
    # Calcular mejor opción
    mejor_edad = edades[pensiones_edad.index(max(pensiones_edad))]
    mejor_pension = max(pensiones_edad)
    
    # Crear DataFrame con formato
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
    
    # Aplicar estilos condicionales
    def resaltar_mejor(row):
        if float(row['Pensión mensual'].replace('$', '').replace(',', '')) == mejor_pension:
            return ['background-color: #065f46'] * len(row)
        return [''] * len(row)
    
    styled_df = df_tabla.style.apply(resaltar_mejor, axis=1)
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Destacar mejor opción
    st.success(f"""
    ### ✨ Mejor estrategia
    
    **Retirarte a los {mejor_edad} años** te daría una pensión de **${mejor_pension:,.2f}**,
    lo que representa **+${mejor_pension - pension_base:,.2f} mensuales**
    y **+${(mejor_pension - pension_base) * 12:,.0f} anuales** más que tu escenario actual.
    """)
    
    st.markdown("---")
    
    # --- MODALIDAD 40 (SI EXISTE) ---
    st.markdown("#### 🚀 Impacto de Modalidad 40")
    
    if 'resultado_m40' in st.session_state and st.session_state.get('m40_calculado', False):
        res = st.session_state.resultado_m40
        
        # Tarjetas de resultado
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6;">
                <p style="color: #94a3b8; margin:0">Pensión actual</p>
                <p style="color: white; font-size: 22px; font-weight: bold; margin:0">${pension_base:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #10b981;">
                <p style="color: #94a3b8; margin:0">Con M40</p>
                <p style="color: white; font-size: 22px; font-weight: bold; margin:0">${res['con_m40']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m3:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #f59e0b;">
                <p style="color: #94a3b8; margin:0">Incremento</p>
                <p style="color: #fbbf24; font-size: 22px; font-weight: bold; margin:0">+${res['incremento']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráfica comparativa M40
        fig_m40 = go.Figure(data=[
            go.Bar(
                name='Sin M40',
                x=['Comparación'],
                y=[pension_base],
                marker_color='#3b82f6',
                text=[f"${pension_base:,.0f}"],
                textposition='outside'
            ),
            go.Bar(
                name='Con M40',
                x=['Comparación'],
                y=[res['con_m40']],
                marker_color='#10b981',
                text=[f"${res['con_m40']:,.0f}"],
                textposition='outside'
            )
        ])
        
        fig_m40.update_layout(
            title="Pensión actual vs Modalidad 40",
            yaxis_title="Pensión mensual ($)",
            yaxis_tickformat="$,.0f",
            height=400,
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig_m40, use_container_width=True)
        
        # Detalles de la estrategia
        with st.expander("📋 Ver análisis detallado de Modalidad 40"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.metric("Inversión total", f"${res['inversion']:,.2f}")
                st.metric("Recuperación", f"{res['recuperacion']} meses")
            with col_d2:
                st.metric("ROI a 20 años", f"{res['roi']}%")
                st.metric("Utilidad neta 20 años", f"${res['utilidad_20']:,.2f}")
    
    else:
        st.info("""
        💡 **Calcula un escenario de Modalidad 40 en la pestaña 2**  
        para ver la comparativa detallada con tu pensión actual.
        """)
    
    st.markdown("---")
    
    # --- PROYECCIÓN DE INGRESOS TOTALES ---
    st.markdown("#### 💰 Proyección de vida financiera")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        expectativa = st.number_input("Expectativa de vida (años)", 70, 100, 85)
    
    años_retiro = expectativa - edad_retiro
    ingreso_total = pension_base * 12 * años_retiro
    ingreso_m40 = res['con_m40'] * 12 * años_retiro if 'res' in locals() else ingreso_total
    
    with col_p2:
        st.metric(
            "Ingreso total estimado",
            f"${ingreso_total:,.0f}",
            help="Basado en tu pensión actual"
        )
    
    with col_p3:
        if 'res' in locals():
            st.metric(
                "Con Modalidad 40",
                f"${ingreso_m40:,.0f}",
                delta=f"+${ingreso_m40 - ingreso_total:,.0f}",
                delta_color="normal"
            )
    
    # --- BOTÓN DE DESCARGA PROFESIONAL ---
    st.markdown("---")
    
    if st.button("📥 DESCARGAR REPORTE COMPLETO PDF", use_container_width=True):
        
        # Recolectar todos los datos para el PDF
        pdf_bytes = generar_pdf_comparativo(
            None,  # df_edades no necesario
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
            f"Reporte_Optipension_{datetime.now().strftime('%Y%m%d')}.pdf",
            "application/pdf"
        )

        
# --- FOOTER ---
st.divider()
st.markdown(
"""
<div style='text-align:left;'>

### 📌 TÉRMINOS Y CONDICIONES
El uso de este simulador implica la aceptación de los siguientes términos:
* **Naturaleza del servicio**: Este simulador proporciona estimaciones basadas en modelos matemáticos y la Ley 73 del IMSS. Los resultados son aproximados y no constituyen un dictamen oficial ni una garantía de pago.
* **Limitación de responsabilidad**: Optipensión 73 no se hace responsable por decisiones tomadas basadas exclusivamente en los resultados. Se recomienda consultar con un asesor certificado.
* **Uso personal**: Esta herramienta es para uso informativo personal.

---

### 🔒 AVISO DE PRIVACIDAD
**Protección de datos**: Esta aplicación NO almacena, guarda ni comparte ningún dato personal ingresado por el usuario.

**Cookies**: No utilizamos cookies de rastreo.

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
