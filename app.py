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
# PESTAÑA 1: ESCENARIO ACTUAL (CORREGIDA)
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
    # Guardar en session_state para otras pestañas
    st.session_state.edad_retiro = edad_retiro
    
    # Mostrar factor de edad
    factor_edad = FACTORES_EDAD.get(edad_retiro, 0.75)
    st.caption(f"Factor por edad aplicado: {factor_edad*100:.0f}%")
    
    # Calcular pensión base (con inflación 0 para obtener valor actual)
    p_base, _ = calcular_pension_ley73(sal_val, sem_val, edad_val, 60, 0, esp_val)
    st.session_state.pension_base = p_base
    
    # Generar tabla desde edad actual hasta edad de retiro
    datos = []
    for i in range((edad_retiro - edad_val) + 1):
        ed_i = edad_val + i
        años_desde_hoy = i
        factor_ed = FACTORES_EDAD.get(ed_i, 1.0)
        f_inf = (1 + (inf_val/100)) ** años_desde_hoy
        
        # Para la edad actual, usar el valor base exacto
        if ed_i == edad_val:
            p_i = p_base
        else:
            # Para edades futuras, proyectar con inflación y factor por edad
            p_i = p_base * f_inf * (factor_ed / 0.75)
        
        datos.append({
            "Año": 2026 + años_desde_hoy,
            "Edad": ed_i,
            "Pensión": round(p_i, 2),
            "Factor": f"{factor_ed*100:.0f}%"
        })
    
    df_actual = pd.DataFrame(datos)
    
    # Mostrar resultados
    p_hoy = df_actual[df_actual['Edad'] == edad_val]['Pensión'].values[0]
    p_futura = df_actual[df_actual['Edad'] == edad_retiro]['Pensión'].values[0]
    
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
    
    # Tabla de proyección
    with st.expander("📈 Ver proyección año por año"):
        st.dataframe(
            df_actual[['Año', 'Edad', 'Factor', 'Pensión']].style.format({
                'Pensión': '${:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

# ============================================
# PESTAÑA 2: MODALIDAD 40
# ============================================
with tab2:
    st.markdown("### 🚀 Estrategia de Modalidad 40")
    
    # Recuperar edad de retiro de pestaña 1
    edad_retiro = st.session_state.get('edad_retiro', 60)
    
    st.info(f"""
    🎯 **Edad de retiro seleccionada: {edad_retiro} años**  
    *(puedes cambiarla en la pestaña "Escenario Actual")*
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
        st.markdown("##### ⚙️ Estrategia M40")
        sal_m40_tope = st.number_input(
            "💰 Salario a cotizar en M40", 
            min_value=500.0, 
            max_value=5000.0, 
            value=2932.0, 
            step=50.0,
            help="Máximo recomendado: 25 UMAS (~$3,126)"
        )
    
    with col2:
        st.markdown("##### 📅 Tiempo")
        meses_m40 = st.select_slider(
            "Meses a cotizar",
            options=[6, 12, 18, 24, 30, 36, 42, 48],
            value=36,
            help="A mayor tiempo, mayor inversión pero también mayor pensión"
        )
    
    # Botón de cálculo
    if st.button("📈 Calcular impacto M40", use_container_width=True, type="primary"):
        
        resultado_m40 = calcular_mod40(
            edad_val,
            sem_val,
            sal_val,
            sal_m40_tope,
            meses_m40,
            edad_retiro,
            esp_val
        )
        
        st.markdown("---")
        st.markdown("### 📊 Resultado de la Estrategia")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        with col_r1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Pensión Base</div>
                <div class="metric-value">${resultado_m40['base']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_r2:
            st.markdown(f"""
            <div class="metric-container-pro">
                <div class="metric-label">Pensión con M40</div>
                <div class="metric-value">${resultado_m40['con_m40']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_r3:
            incremento = resultado_m40['con_m40'] - resultado_m40['base']
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; border-left: 5px solid #f59e0b; margin-bottom: 20px;">
                <div class="metric-label">Incremento mensual</div>
                <div class="metric-value" style="color: #fbbf24;">+${incremento:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.metric("Inversión total", f"${resultado_m40['inversion']:,.2f}")
        
        with col_d2:
            st.metric("Tiempo de recuperación", f"{resultado_m40['recuperacion']} meses")
        
        with col_d3:
            st.metric("ROI a 20 años", f"{resultado_m40['roi']}%")
        
        # Gráfica
        fig = go.Figure(data=[
            go.Bar(name='Pensión Base', x=['Actual'], y=[resultado_m40['base']], 
                   marker_color='#3b82f6', text=[f"${resultado_m40['base']:,.0f}"],
                   textposition='outside'),
            go.Bar(name='Con M40', x=['Actual'], y=[resultado_m40['con_m40']], 
                   marker_color='#10b981', text=[f"${resultado_m40['con_m40']:,.0f}"],
                   textposition='outside')
        ])
        
        fig.update_layout(
            title=f"Comparación de pensión mensual (retiro a los {edad_retiro} años)",
            yaxis_title="Pensión mensual ($)",
            yaxis_tickformat="$,.0f",
            height=400,
            showlegend=True,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"""
        ### 💰 Utilidad estimada a 20 años: **${resultado_m40['utilidad_20']:,.2f} MXN**
        """)

# ============================================
# PESTAÑA 3: EN PREPARACIÓN
# ============================================
with tab3:
    st.info("Pestaña de ROI y Comparativas en preparación.")

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
