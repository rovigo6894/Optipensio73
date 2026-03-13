import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from fpdf import FPDF 
import io

# --- IMPORTACIÓN DE TUS ARCHIVOS ---
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Optipensión 73 PRO", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- ESTILOS CSS REVISADOS PARA NO PERDER EL BOTÓN DEL SIDEBAR ---
st.markdown("""
    <style>
    /* Ocultamos el botón de configuración y el menú de hamburguesa, pero NO el header completo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Esto quita el espacio blanco de arriba pero mantiene el botón del sidebar funcional */
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    header[data-testid="stHeader"] > div:first-child {
        visibility: hidden; /* Oculta logo de streamlit y menús */
    }
    /* Forzamos que el botón del sidebar sea visible siempre que se necesite */
    button[kind="header"] {
        visibility: visible !important;
        color: white !important;
    }

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

# --- FUNCIÓN PDF ---
def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    try: pdf.image("assets/image.jpg", 10, 10, 30)
    except: pass
    
    pdf.set_font("helvetica", "B", 16)
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, "REPORTE ESTRATÉGICO DE PENSIÓN", ln=True, align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")

    pdf.set_y(55)
    pdf.set_fill_color(235, 235, 235)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, " 1. Diagnóstico de Situación Actual", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.ln(3)
    pdf.cell(0, 6, f"      - Edad actual: {edad_act} años", ln=True)
    pdf.cell(0, 6, f"      - Semanas reconocidas: {sem}", ln=True)
    pdf.cell(0, 6, f"      - Salario Diario (SBC): ${sal:,.2f} MXN", ln=True)

    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, " 2. Resultados Proyectados", ln=True, fill=True)
    pdf.ln(4)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 7, f"      PENSIÓN ESTIMADA HOY: ${p_hoy:,.2f} MXN", ln=True)
    pdf.cell(0, 7, f"      PENSIÓN A LOS {edad_obj} AÑOS: ${p_proyectada:,.2f} MXN", ln=True)
    
    pdf.ln(8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(210, 210, 210)
    pdf.cell(40, 8, "Año", 1, 0, "C", True)
    pdf.cell(40, 8, "Edad", 1, 0, "C", True)
    pdf.cell(60, 8, "Pensión Mensual", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 10)
    for i, row in df.iterrows():
        if i < 10: 
            pdf.cell(40, 7, str(int(row['Año'])), 1, 0, "C")
            pdf.cell(40, 7, str(int(row['Edad'])), 1, 0, "C")
            pdf.cell(60, 7, f"${row['Pensión']:,.2f}", 1, 1, "C")

    pdf.set_y(260)
    pdf.line(130, 275, 190, 275)
    pdf.set_y(276)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    
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

# --- CABECERA PRINCIPAL CON LOGO ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try: st.image("assets/image.jpg", width=100)
    except: pass
with col_title:
    st.title("OPTIPENSIÓN 73")
    st.subheader("Consultoría Especializada en Retiro")

tab1, tab2, tab3 = st.tabs(["📊 Escenario Actual", "🚀 Estrategia Mod 40", "📈 ROI & Comparativa"])

# PESTAÑA 1
with tab1:
    p_60, _ = calcular_pension_ley73(sal_val, sem_val, edad_val, 60, inf_val, esp_val)
    p_100 = p_60 / 0.75
    
    datos = []
    for i in range((65 - edad_val) + 1):
        ed_i = edad_val + i
        f_i = (1 + (inf_val/100)) ** i
        f_ed = 0.75 if ed_i < 60 else FACTORES_EDAD.get(ed_i, 1.0)
        p_i = (p_100 * f_ed) * f_i
        datos.append({"Año": 2026 + i, "Edad": ed_i, "Pensión": round(p_i, 2)})
    
    df_actual = pd.DataFrame(datos)
    
    st.markdown("### ¿A qué edad planea retirarse?")
    edad_obj = st.select_slider("Seleccione la edad de retiro para comparar", options=list(range(60, 66)), value=60)
    
    p_hoy = df_actual[df_actual['Edad'] == edad_val]['Pensión'].values[0]
    p_proyectada = df_actual[df_actual['Edad'] == edad_obj]['Pensión'].values[0]
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Pensión Estimada Hoy</div>
                <div class="metric-value">${p_hoy:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="metric-container-pro">
                <div class="metric-label">Pensión a los {edad_obj} años</div>
                <div class="metric-value">${p_proyectada:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📥 Descargar Reporte PDF"):
            pdf_out = generar_pdf_pro(df_actual, p_hoy, p_proyectada, edad_val, edad_obj, sal_val, sem_val)
            st.download_button("Click para Guardar", pdf_out, "Reporte_Optipension.pdf")

    with c2:
        fig = px.bar(df_actual, x="Edad", y="Pensión", color="Pensión", color_continuous_scale="Blues", text_auto=".2s")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.info("Pestaña de Modalidad 40 en preparación.")

with tab3:
    st.info("Pestaña de ROI y Comparativas en preparación.")

st.caption(f"Ing. Roberto Villarreal Glz. | 2026")


# ---------------------------------------------------
# FOOTER PRO (ESTILO IMÁGENES)
# ---------------------------------------------------
st.divider()

st.markdown(
"""
<div style='text-align:left;'>

### 📌 TÉRMINOS Y CONDICIONES
El uso de este simulador implica la aceptación de los siguientes términos:
* **Naturaleza del servicio**: Este simulador proporciona estimaciones basadas en modelos matemáticos y la Ley 73 del IMSS. Los resultados son aproximados y no constituyen un dictamen oficial ni una garantía de pago.
* **Limitación de responsabilidad**: Optipensión 73 no se hace responsable por decisiones tomadas basadas exclusivamente en los resultados de esta demo. Se recomienda consultar con un asesor certificado.
* **Uso personal**: Esta herramienta es para uso informativo personal.

---

### 🔒 AVISO DE PRIVACIDAD
**Protección de datos**: Esta aplicación DEMO **NO almacena, guarda ni comparte** ningún dato personal ingresado por el usuario. Todos los cálculos se realizan en tiempo real y los datos se descartan al cerrar la sesión.

**Cookies**: No utilizamos cookies de rastreo ni almacenamos información de navegación.

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
