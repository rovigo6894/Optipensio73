import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from fpdf import FPDF 
import io

# --- RESTAURACIÓN DE TUS ARCHIVOS CORE ---
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

# --- CONFIGURACIÓN SaaS ---
st.set_page_config(page_title="Optipensión 73 PRO", layout="wide", page_icon="💰")

# --- ESTILOS (Recuperando el Sidebar que se "fue") ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1e2630; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- REUTILIZANDO TU FUNCIÓN DE PDF PERFECTA (LA DE LOS 80MM) ---
def generar_pdf_real(df, p_hoy, p_meta, edad_act, edad_obj, sal, sem, titulo_rep):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=False) 
    try:
        pdf.image("assets/image.jpg", 12, 10, 32) 
    except: pass
    pdf.set_font("helvetica", "B", 18)
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, titulo_rep, ln=True, align="R")
    
    pdf.set_y(80) # EL MARGEN DE ÉXITO
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 9, "  1. Diagnóstico de Situación Actual", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 6, f"      - Edad: {edad_act} años | Semanas: {sem} | SBC: ${sal:,.2f}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 9, "  2. Resultados Proyectados", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, f"      PENSIÓN ESTIMADA: ${p_meta:,.2f} MXN", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    # Tabla en PDF
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(225, 225, 225)
    pdf.cell(30, 7, "Año", border=1, align="C", fill=True)
    pdf.cell(20, 7, "Edad", border=1, align="C", fill=True)
    pdf.cell(80, 7, "Pensión Mensual", border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("helvetica", "", 10)
    for index, row in df.head(8).iterrows():
        pdf.cell(30, 6, str(int(row['Año'])), border=1, align="C")
        pdf.cell(20, 6, str(int(row['Edad'])), border=1, align="C")
        pdf.cell(80, 6, f"${row['Pensión']:,.2f} MXN", border=1, align="C")
        pdf.ln()
    
    pdf.set_y(255)
    try: pdf.image("assets/firma.png", 145, 252, 38)
    except: pass
    pdf.set_y(274)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    return bytes(pdf.output())

# --- SIDEBAR (DATOS REALES) ---
with st.sidebar:
    st.header("⚙️ Configuración Global")
    edad_val = st.number_input("Edad actual", 50, 65, 57)
    sem_val = st.number_input("Semanas cotizadas", 500, 3000, 1315)
    sal_val = st.number_input("Salario diario actual (SBC)", 100.0, 3500.0, 959.15)
    inf_val = st.number_input("Inflación estimada %", value=4.5)
    esp_val = st.checkbox("Asignación por esposa", value=True)

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📊 Escenario Actual", "🚀 Plan Modalidad 40", "📈 Comparativa & ROI"])

# ---------------------------------------------------------
# PESTAÑA 1: RECUPERANDO TODO LO LOGRADO
# ---------------------------------------------------------
with tab1:
    st.subheader("Análisis de Situación Sin Inversión")
    
    # Lógica Real de Pensión
    p_60, _ = calcular_pension_ley73(sal_val, sem_val, edad_val, 60, inf_val, esp_val)
    p_100 = p_60 / 0.75 
    
    datos_l = []
    for i in range((65 - edad_val) + 1):
        ed_i = edad_val + i
        f_i = (1 + (inf_val/100)) ** i
        f_ed = 0.75 if ed_i < 60 else FACTORES_EDAD.get(ed_i, 1.0)
        p_i = (p_100 * f_ed) * f_i
        datos_l.append({"Año": 2026 + i, "Edad": ed_i, "Pensión": round(p_i, 2)})
    
    df_actual = pd.DataFrame(datos_l)
    val_h = df_actual[df_actual['Edad'] == edad_val]['Pensión'].values[0]
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Pensión Hoy", f"${val_h:,.2f}")
        if st.button("Descargar Reporte Actual"):
            pdf_bytes = generar_pdf_real(df_actual, val_h, val_h, edad_val, edad_val, sal_val, sem_val, "DIAGNÓSTICO ACTUAL")
            st.download_button("Guardar PDF", pdf_bytes, "Reporte_Actual.pdf")
    
    with c2:
        fig = px.bar(df_actual, x="Edad", y="Pensión", text_auto=".0f", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PESTAÑA 2: MOD 40 (AISLADA)
# ---------------------------------------------------------
with tab2:
    st.subheader("Simulador Estratégico Mod 40")
    # (Aquí va la lógica de inversión que no afecta a la Tab 1)
    u_mas = st.slider("UMAs", 1, 25, 25)
    st.info("Configura aquí tu inversión sin alterar el diagnóstico inicial.")

st.divider()
st.caption(f"Optipensión 73 PRO | {datetime.now().year}")


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
