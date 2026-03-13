import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from fpdf import FPDF 
import io

# --- IMPORTACIÓN DE TUS ARCHIVOS (Esto es lo que faltaba) ---
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Optipensión 73 PRO", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111827; }
    .metric-container {
        background-color: #1e293b; padding: 20px; border-radius: 10px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    .metric-container-pro {
        background-color: #064e3b; padding: 20px; border-radius: 10px;
        border-left: 5px solid #10b981; margin-bottom: 20px;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- PDF PROFESIONAL (Logo pequeño y firma centrada) ---
def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    try: pdf.image("assets/image.jpg", 10, 10, 25) 
    except: pass
    pdf.set_font("helvetica", "B", 18)
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, "ESTRATEGIA DE RETIRO PROFESIONAL", ln=True, align="R")
    pdf.ln(12)
    pdf.line(10, 38, 200, 38)
    pdf.set_y(45)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "  1. DIAGNÓSTICO DE SITUACIÓN ACTUAL", ln=True, fill=False)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, f" Edad Actual: {edad_act} años | Semanas: {sem} | SBC: ${sal:,.2f}", ln=True)
    pdf.ln(10)
    # Tabla de resultados
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(45, 8, "Año", 1, 0, "C", True)
    pdf.cell(45, 8, "Edad", 1, 0, "C", True)
    pdf.cell(95, 8, "Pensión Estimada Mensual", 1, 1, "C", True)
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    for i, row in df.iterrows():
        pdf.cell(45, 7, str(int(row['Año'])), 1, 0, "C")
        pdf.cell(45, 7, str(int(row['Edad'])), 1, 0, "C")
        pdf.cell(95, 7, f"${row['Pensión']:,.2f} MXN", 1, 1, "R")
    # Firma centrada abajo
    pdf.set_y(250)
    try: pdf.image("assets/firma.png", 150, 235, 40)
    except: pdf.line(150, 255, 190, 255)
    pdf.set_y(260)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_x(140)
    pdf.cell(60, 5, "Ing. Roberto Villarreal Glz", ln=True, align="C")
    return bytes(pdf.output())

# --- SIDEBAR ---
with st.sidebar:
    try: st.image("assets/image.jpg", width=100)
    except: pass
    st.markdown("### 📍 Parámetros Base")
    edad_val = st.number_input("Edad actual", 50, 70, 57)
    sem_val = st.number_input("Semanas Reconocidas", 500, 3000, 1315)
    sal_val = st.number_input("Salario Diario (SBC)", 100.0, 3500.0, 959.15)
    inf_val = st.number_input("Inflación Est. %", 0.0, 10.0, 4.5)
    esp_val = st.checkbox("Asignación Esposa", value=True)

# --- CUERPO ---
st.title("OPTIPENSIÓN 73")
st.markdown("---") # ESTO ES EL REEMPLAZO DEL DIVIDER

tab1, tab2, tab3 = st.tabs(["📊 Escenario Actual", "🚀 Estrategia Mod 40", "📝 Términos"])

with tab1:
    # AQUÍ USAMOS TU LÓGICA DE CALCULO REAL
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
    
    edad_obj = st.select_slider("¿A qué edad planea retirarse?", options=list(range(60, 66)), value=60)
    p_hoy = df_actual[df_actual['Edad'] == edad_val]['Pensión'].values[0]
    p_proyectada = df_actual[df_actual['Edad'] == edad_obj]['Pensión'].values[0]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div class="metric-container"><div style="color:#94a3b8">Pensión Hoy</div><div class="metric-value">${p_hoy:,.2f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-container-pro"><div style="color:#a7f3d0">A los {edad_obj} años</div><div class="metric-value">${p_proyectada:,.2f}</div></div>', unsafe_allow_html=True)
        
        pdf_bytes = generar_pdf_pro(df_actual, p_hoy, p_proyectada, edad_val, edad_obj, sal_val, sem_val)
        st.download_button("📥 Descargar Reporte PDF", pdf_bytes, f"Reporte_{edad_obj}.pdf")

    with col2:
        st.plotly_chart(px.bar(df_actual, x="Edad", y="Pensión", color="Pensión", color_continuous_scale="Blues"), use_container_width=True)

with tab2:
    st.info("Módulo de Modalidad 40 en desarrollo.")

with tab3:
    st.markdown("### Términos y Condiciones")
    st.write("Este simulador es una herramienta informativa basada en la Ley 73 del IMSS.")

st.caption("Ing. Roberto Villarreal Glz. | 2026")


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
