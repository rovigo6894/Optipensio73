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

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stDeployButton {display:none !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stSidebar"] { 
        background-color: #111827; 
        min-width: 260px !important;
        max-width: 260px !important;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        width: 120px !important;
        margin-left: auto;
        margin-right: auto;
        display: block;
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
    .metric-label { font-size: 14px; color: #94a3b8; margin-bottom: 5px; }
    .metric-value { font-size: 32px; font-weight: bold; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PDF MEJORADA ---
def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. ENCABEZADO Y LOGO
    try: pdf.image("assets/image.jpg", 10, 8, 33)
    except: pass
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(17, 24, 39) # Azul muy oscuro
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, "ESTRATEGIA DE RETIRO: OPTIPENSIÓN 73", ln=True, align="R")
    
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", ln=True, align="R")
    
    pdf.ln(15)
    pdf.set_draw_color(59, 130, 246) # Azul acento
    pdf.line(10, 38, 200, 38)

    # 2. SECCIÓN: SITUACIÓN ACTUAL
    pdf.set_y(45)
    pdf.set_fill_color(243, 244, 246)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 10, "  1. DIAGNÓSTICO DE SITUACIÓN ACTUAL", ln=True, fill=True)
    
    pdf.ln(4)
    pdf.set_font("helvetica", "", 11)
    # Tabla simple de datos
    pdf.cell(45, 8, f" Edad Actual: {edad_act} años", 0)
    pdf.cell(55, 8, f" Semanas: {sem}", 0)
    pdf.cell(60, 8, f" Salario Diario (SBC): ${sal:,.2f}", 0, 1)

    # 3. SECCIÓN: RESULTADOS DESTACADOS (CUADROS)
    pdf.ln(8)
    # Cuadro Pensión Hoy
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(90, 10, "  PENSIÓN ESTIMADA AL DÍA DE HOY", ln=0, fill=True)
    pdf.cell(5, 10, "", 0) # Espacio
    # Cuadro Pensión Proyectada
    pdf.set_fill_color(6, 78, 59)
    pdf.cell(90, 10, f"  PENSIÓN PROYECTADA ({edad_obj} AÑOS)", ln=1, fill=True)
    
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(90, 15, f"  ${p_hoy:,.2f} MXN", 1, 0, "C")
    pdf.cell(5, 15, "", 0) # Espacio
    pdf.cell(90, 15, f"  ${p_proyectada:,.2f} MXN", 1, 1, "C")
    
    pdf.set_text_color(0, 0, 0)

    # 4. TABLA DE CRECIMIENTO ANUAL
    pdf.ln(12)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  2. PROYECCIÓN DE CRECIMIENTO POR EDAD", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    
    # Encabezados tabla
    pdf.cell(45, 10, "Año Calendario", 1, 0, "C", True)
    pdf.cell(45, 10, "Edad del Asegurado", 1, 0, "C", True)
    pdf.cell(95, 10, "Pensión Mensual Estimada", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    fill = False
    for i, row in df.iterrows():
        pdf.set_fill_color(249, 250, 251)
        pdf.cell(45, 8, str(int(row['Año'])), 1, 0, "C", fill)
        pdf.cell(45, 8, str(int(row['Edad'])), 1, 0, "C", fill)
        pdf.cell(95, 8, f"${row['Pensión']:,.2f} MXN", 1, 1, "R", fill)
        fill = not fill

    # 5. PIE DE PÁGINA / FIRMA
    pdf.set_y(260)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "Este documento es una proyección informativa basada en los datos proporcionados y la Ley del Seguro Social de 1973.", ln=True, align="C")
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 5, "Consultoría en Pensiones", ln=True, align="R")
    
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

tab1, tab2, tab3 = st.tabs(["📊 Escenario Actual", "🚀 Estrategia Mod 40", "📈 ROI & Comparativa"])

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
    edad_obj = st.select_slider("Seleccione la edad", options=list(range(60, 66)), value=60)
    
    p_hoy = df_actual[df_actual['Edad'] == edad_val]['Pensión'].values[0]
    p_proyectada = df_actual[df_actual['Edad'] == edad_obj]['Pensión'].values[0]
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""<div class="metric-container"><div class="metric-label">Pensión Estimada Hoy</div><div class="metric-value">${p_hoy:,.2f}</div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="metric-container-pro"><div class="metric-label">Pensión a los {edad_obj} años</div><div class="metric-value">${p_proyectada:,.2f}</div></div>""", unsafe_allow_html=True)
        
        # EL BOTÓN DE DESCARGA AHORA DISPARA EL PDF MEJORADO
        pdf_out = generar_pdf_pro(df_actual, p_hoy, p_proyectada, edad_val, edad_obj, sal_val, sem_val)
        st.download_button(
            label="📥 Descargar Reporte PDF Profesional",
            data=pdf_out,
            file_name=f"Reporte_Retiro_{edad_obj}_años.pdf",
            mime="application/pdf"
        )

    with c2:
        fig = px.bar(df_actual, x="Edad", y="Pensión", color="Pensión", color_continuous_scale="Blues", text_auto=".2s")
        st.plotly_chart(fig, use_container_width=True)

with tab2: st.info("Pestaña de Modalidad 40 en preparación.")
with tab3: st.info("Pestaña de ROI y Comparativas en preparación.")

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
