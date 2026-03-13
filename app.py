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
    [data-testid="stSidebar"] { background-color: #111827; min-width: 260px !important; }
    .metric-container {
        background-color: #1e293b; padding: 20px; border-radius: 10px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    .metric-container-pro {
        background-color: #064e3b; padding: 20px; border-radius: 10px;
        border-left: 5px solid #10b981; margin-bottom: 20px;
    }
    .metric-label { font-size: 14px; color: #94a3b8; }
    .metric-value { font-size: 32px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PDF PROFESIONAL CORREGIDA ---
def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. ENCABEZADO (Más espacio arriba)
    try: pdf.image("assets/image.jpg", 10, 12, 35)
    except: pass
    
    pdf.set_font("helvetica", "B", 20)
    pdf.set_xy(50, 18)
    pdf.cell(0, 10, "ESTRATEGIA DE RETIRO PROFESIONAL", ln=True, align="R")
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 7, "OPTIPENSIÓN 73", ln=True, align="R")
    
    pdf.ln(15)
    pdf.line(10, 42, 200, 42)

    # 2. DIAGNÓSTICO (Bajamos la posición inicial)
    pdf.set_y(50)
    pdf.set_fill_color(243, 244, 246)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  1. DIAGNÓSTICO DE SITUACIÓN ACTUAL", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.ln(3)
    pdf.cell(0, 8, f" Edad Actual: {edad_act} años  |  Semanas: {sem}  |  Salario Diario: ${sal:,.2f}", ln=True)

    # 3. CUADROS DE RESULTADOS (Más amplios y bajos)
    pdf.ln(12)
    y_pos = pdf.get_y()
    
    # Izquierdo (Hoy)
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(10, y_pos, 92, 30, 'F')
    pdf.set_xy(10, y_pos + 5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(92, 8, "PENSIÓN ESTIMADA HOY", ln=True, align="C")
    pdf.set_font("helvetica", "B", 18)
    pdf.set_x(10)
    pdf.cell(92, 12, f"${p_hoy:,.2f} MXN", ln=False, align="C")

    # Derecho (Proyectada)
    pdf.set_fill_color(6, 78, 59)
    pdf.rect(105, y_pos, 92, 30, 'F')
    pdf.set_xy(105, y_pos + 5)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(92, 8, f"PENSIÓN A LOS {edad_obj} AÑOS", ln=True, align="C")
    pdf.set_font("helvetica", "B", 18)
    pdf.set_x(105)
    pdf.cell(92, 12, f"${p_proyectada:,.2f} MXN", ln=True, align="C")
    
    # 4. TABLA DE PROYECCIÓN
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20) 
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  2. PROYECCIÓN DE CRECIMIENTO ANUAL", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(45, 10, "Año", 1, 0, "C", True)
    pdf.cell(45, 10, "Edad", 1, 0, "C", True)
    pdf.cell(95, 10, "Pensión Estimada Mensual", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    for i, row in df.iterrows():
        pdf.cell(45, 8, str(int(row['Año'])), 1, 0, "C")
        pdf.cell(45, 8, str(int(row['Edad'])), 1, 0, "C")
        pdf.cell(95, 8, f"${row['Pensión']:,.2f} MXN", 1, 1, "R")

    # 5. NOTAS LEGALES
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 5, "TÉRMINOS Y CONDICIONES:", ln=True)
    pdf.set_font("helvetica", "", 8)
    pdf.multi_cell(0, 4, "Los cálculos son proyecciones informativas basadas en la Ley del Seguro Social de 1973. El monto real será determinado únicamente por el IMSS. Se considera la inflación anual capturada.")

    # 6. FIRMA DESDE ASSETS
    pdf.set_y(250)
    try:
        # Ajusta "firma.png" al nombre real de tu archivo de firma en assets
        pdf.image("assets/firma.png", 145, 245, 45) 
    except:
        pdf.line(140, 265, 195, 265) # Línea de respaldo si no hay imagen
    
    pdf.set_y(266)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 5, "Especialista en Pensiones Ley 73", ln=True, align="R")
    
    return bytes(pdf.output())

# --- SIDEBAR ---
with st.sidebar:
    try: st.image("assets/image.jpg", width=120)
    except: st.title("OPTIPENSIÓN 73")
    st.markdown("### 📍 Parámetros Base")
    edad_val = st.number_input("Edad actual", 50, 65, 57)
    sem_val = st.number_input("Semanas Reconocidas", 500, 3000, 1315)
    sal_val = st.number_input("Salario Diario (SBC)", 100.0, 3500.0, 959.15)
    inf_val = st.number_input("Inflación Est. %", value=4.5)
    esp_val = st.checkbox("Asignación Esposa", value=True)

# --- CUERPO PRINCIPAL (SIN DIVIDER) ---
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
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div class="metric-container"><div class="metric-label">Pensión Hoy</div><div class="metric-value">${p_hoy:,.2f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-container-pro"><div class="metric-label">Pensión a los {edad_obj} años</div><div class="metric-value">${p_proyectada:,.2f}</div></div>', unsafe_allow_html=True)
        
        pdf_bytes = generar_pdf_pro(df_actual, p_hoy, p_proyectada, edad_val, edad_obj, sal_val, sem_val)
        st.download_button("📥 Descargar Reporte PDF", pdf_bytes, f"Reporte_{edad_obj}_años.pdf", "application/pdf")

    with col2:
        fig = px.bar(df_actual, x="Edad", y="Pensión", color="Pensión", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

with tab2: st.info("Próximamente: Cálculos de Modalidad 40")
with tab3: st.info("Próximamente: Análisis de Inversión")

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
