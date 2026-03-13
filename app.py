import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from fpdf import FPDF 
import io

# --- CONFIGURACIÓN DE PÁGINA SaaS ---
st.set_page_config(page_title="Optipensión 73 PRO", layout="wide", page_icon="💰")

# --- ESTILOS PARA OCULTAR INTERFAZ DE STREAMLIT ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS Y PARÁMETROS (Simulado para que corra el test) ---
# Si tienes estos archivos en carpetas, asegúrate de que existan o usa estos locales:
FACTORES_EDAD = {60: 0.75, 61: 0.80, 62: 0.85, 63: 0.90, 64: 0.95, 65: 1.0}

def calcular_pension_ley73_local(salario, semanas, edad_act, edad_ret, inflacion, esposa):
    # Lógica simplificada para el test de interfaz
    factor_semanas = (semanas - 500) / 500 * 0.10 # Ejemplo rápido
    base = salario * 30.4 * 0.40 # 40% de cuantía básica
    pension_base = base + (base * factor_semanas)
    if esposa: pension_base *= 1.15
    factor_edad = FACTORES_EDAD.get(edad_ret, 1.0)
    return pension_base * factor_edad, 0

# --- FUNCIÓN PDF (LA QUE YA QUEDÓ AL 100 CON MÁRGENES) ---
def generar_pdf_pro(df, p_hoy, p_meta, edad_act, edad_obj, sal, sem, titulo):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=False) 
    try:
        pdf.image("assets/image.jpg", 12, 10, 32) 
    except: pass
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, titulo, ln=True, align="R")
    
    pdf.set_y(80) # MARGEN DE SEGURIDAD 80mm
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 9, "  1. Datos del Asegurado", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(0, 6, f"      Edad: {edad_act} años | Semanas: {sem} | SBC: ${sal:,.2f}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 9, "  2. Resultados del Escenario", ln=True, fill=True)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, f"      Pensión Proyectada: ${p_meta:,.2f} MXN", ln=True)
    
    pdf.set_y(255)
    pdf.line(130, 272, 195, 272)
    pdf.set_y(274)
    pdf.set_text_color(0,0,0)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    return bytes(pdf.output())

# --- SIDEBAR (DATOS BASE) ---
with st.sidebar:
    st.header("📍 Datos Maestros")
    edad_val = st.number_input("Edad actual", 50, 65, 57)
    sem_val = st.number_input("Semanas cotizadas", 500, 3000, 1315)
    sal_val = st.number_input("Salario actual (SBC)", 100.0, 3500.0, 959.15)
    st.divider()
    inf_val = st.number_input("Inflación %", value=4.5)
    esp_val = st.checkbox("Asignación Esposa", value=True)

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["📊 Escenario Actual", "🚀 Plan Modalidad 40", "📈 Comparativa & ROI"])

# PESTAÑA 1: SITUACIÓN ACTUAL
with tab1:
    st.subheader("Análisis de Situación Sin Inversión")
    p_est, _ = calcular_pension_ley73_local(sal_val, sem_val, edad_val, 60, inf_val, esp_val)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Pensión Estimada (60 años)", f"${p_est:,.2f}")
        if st.button("Descargar Diagnóstico Actual"):
            # Generamos un DF rápido para el PDF
            df_temp = pd.DataFrame([{"Año": 2026, "Edad": edad_val, "Pensión": p_est}])
            pdf_b = generar_pdf_pro(df_temp, p_est, p_est, edad_val, 60, sal_val, sem_val, "DIAGNÓSTICO ACTUAL")
            st.download_button("Click para guardar PDF", pdf_b, "Diagnostico_Actual.pdf")
    
    with c2:
        st.info("Este cálculo usa tu salario actual de las últimas 250 semanas.")

# PESTAÑA 2: ESTRATEGIA MODALIDAD 40
with tab2:
    st.subheader("Simulación de Inversión (Mod 40)")
    col_a, col_b = st.columns(2)
    
    with col_a:
        u_mas = st.slider("UMAs a contratar", 1, 25, 25)
        sbc_m40 = u_mas * 113.89
        meses_m40 = st.number_input("Meses a pagar", 12, 60, 24)
    
    # Lógica de impacto rápida para el test
    sem_finales = sem_val + int(meses_m40 * 4.33)
    promedio_proyectado = ((int(meses_m40 * 4.33) * sbc_m40) + ((250 - int(meses_m40 * 4.33)) * sal_val)) / 250
    p_con_m40, _ = calcular_pension_ley73_local(promedio_proyectado, sem_finales, edad_val, 60, inf_val, esp_val)

    with col_b:
        st.metric("Nuevo Salario Promedio", f"${promedio_proyectado:,.2f}", f"+{((promedio_proyectado/sal_val)-1)*100:.1f}%")
        st.metric("Pensión con Estrategia", f"${p_con_m40:,.2f}")

# PESTAÑA 3: COMPARATIVA PRO
with tab3:
    st.subheader("Análisis de Retorno de Inversión")
    st.write("Diferencia mensual ganada:")
    st.header(f"${(p_con_m40 - p_est):,.2f} MXN / mes")
    st.progress(0.7, "Nivel de Optimización")
    st.info("Pestaña en desarrollo para visualización de ROI a 20 años.")

st.divider()
st.caption(f"Optipensión 73 PRO | {datetime.now().strftime('%Y')}")


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
