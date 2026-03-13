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
    [data-testid="stSidebar"] { background-color: #111827; min-width: 260px !important; }
    .metric-container {
        background-color: #1e293b; padding: 20px; border-radius: 10px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    .metric-container-pro {
        background-color: #064e3b; padding: 20px; border-radius: 10px;
        border-left: 5px solid #10b981; margin-bottom: 20px;
    }
    .metric-value { font-size: 32px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN PDF LIMPIA Y PROFESIONAL ---
def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    
    # 1. ENCABEZADO (Logo más pequeño y texto alineado)
    try: 
        pdf.image("assets/image.jpg", 15, 12, 20) 
    except: 
        pass
    
    pdf.set_font("helvetica", "B", 16)
    pdf.set_xy(40, 15)
    pdf.cell(0, 10, "ESTRATEGIA DE RETIRO PROFESIONAL", ln=True, align="R")
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 5, f"Consultoría: Ing. Roberto Villarreal | {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="R")
    pdf.line(15, 35, 195, 35)

    # 2. DIAGNÓSTICO
    pdf.set_y(42)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, " 1. Diagnóstico de Situación Actual", ln=True, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.ln(2)
    pdf.cell(0, 6, f"   Edad actual: {edad_act} años  |  Semanas: {sem}  |  SBC: ${sal:,.2f} MXN", ln=True)

    # 3. CUADROS DE PENSIONES (Simulando los recuadros de la app)
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)
    
    # Cuadro Izquierdo
    pdf.set_fill_color(30, 41, 59)
    pdf.cell(88, 8, "  PENSIÓN ESTIMADA HOY", 0, 0, "L", True)
    pdf.cell(4, 8, "", 0, 0) # Espacio intermedio
    # Cuadro Derecho
    pdf.set_fill_color(6, 78, 59)
    pdf.cell(88, 8, f"  PENSIÓN A LOS {edad_obj} AÑOS", 0, 1, "L", True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(88, 12, f"${p_hoy:,.2f} MXN", 1, 0, "C")
    pdf.cell(4, 12, "", 0, 0)
    pdf.cell(88, 12, f"${p_proyectada:,.2f} MXN", 1, 1, "C")

    # 4. TABLA DE PROYECCIÓN (Ajustada para que no invada el pie)
    pdf.ln(8)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(0, 8, " 2. Proyección de Crecimiento Anual", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(40, 7, "Año Calendario", 1, 0, "C", True)
    pdf.cell(30, 7, "Edad", 1, 0, "C", True)
    pdf.cell(110, 7, "Pensión Mensual Estimada (Proyectada)", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 9)
    for i, row in df.iterrows():
        if i < 10: # Limitamos filas para asegurar espacio de firma
            pdf.cell(40, 6, str(int(row['Año'])), 1, 0, "C")
            pdf.cell(30, 6, str(int(row['Edad'])), 1, 0, "C")
            pdf.cell(110, 6, f"${row['Pensión']:,.2f} MXN", 1, 1, "R")

    # 5. PIE DE PÁGINA Y FIRMA (Fijos al final)
    pdf.set_y(250)
    pdf.set_font("helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 4, "Aviso: Los cálculos son proyecciones informativas basadas en la Ley 73 del IMSS. El monto final será determinado únicamente por la institución al momento de la solicitud.", align="C")
    
    try:
        pdf.image("assets/firma.png", 150, 240, 35) # Firma colocada sobre el nombre
    except:
        pass

    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 4, "Especialista en Pensiones Ley 73", ln=True, align="R")
    
    return bytes(pdf.output())

# --- RESTO DEL CÓDIGO (INTERFAZ) ---
with st.sidebar:
    try: st.image("assets/image.jpg", width=120)
    except: pass
    st.header("📍 Parámetros")
    edad_val = st.number_input("Edad actual", 50, 65, 57)
    sem_val = st.number_input("Semanas", 500, 3000, 1315)
    sal_val = st.number_input("Salario (SBC)", 100.0, 3500.0, 959.15)
    inf_val = st.number_input("Inflación %", value=4.5)
    esp_val = st.checkbox("Asignación Esposa", value=True)

st.title("OPTIPENSIÓN 73")
tab1, tab2, tab3 = st.tabs(["📊 Escenario", "🚀 Estrategia", "📈 ROI"])

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
    
    edad_obj = st.select_slider("Edad de retiro", options=list(range(60, 66)), value=60)
    p_hoy = df_actual[df_actual['Edad'] == edad_val]['Pensión'].values[0]
    p_proyectada = df_actual[df_actual['Edad'] == edad_obj]['Pensión'].values[0]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div class="metric-container"><div class="metric-value">${p_hoy:,.2f}</div>Hoy</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-container-pro"><div class="metric-value">${p_proyectada:,.2f}</div>A los {edad_obj}</div>', unsafe_allow_html=True)
        if st.button("📥 Descargar Reporte"):
            pdf_bytes = generar_pdf_pro(df_actual, p_hoy, p_proyectada, edad_val, edad_obj, sal_val, sem_val)
            st.download_button("Guardar PDF", pdf_bytes, "Reporte_Optipension.pdf")
    with col2:
        st.plotly_chart(px.bar(df_actual, x="Edad", y="Pensión"), use_container_width=True)

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
