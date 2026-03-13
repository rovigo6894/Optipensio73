import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# Configuración inicial
st.set_page_config(page_title="Optipensión 73 PRO", layout="wide")

# PDF con logo pequeño y firma centrada
def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Logo (25mm)
    try: pdf.image("assets/image.jpg", 10, 10, 25) 
    except: pass
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, "ESTRATEGIA DE RETIRO PROFESIONAL", ln=True, align="R")
    pdf.ln(12)
    pdf.line(10, 38, 200, 38)

    # Diagnóstico
    pdf.set_y(48)
    pdf.set_fill_color(243, 244, 246)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "  1. DIAGNÓSTICO DE SITUACIÓN ACTUAL", ln=True, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.ln(2)
    pdf.cell(0, 6, f" Edad Actual: {edad_act} años | Semanas: {sem} | SBC: ${sal:,.2f}", ln=True)

    # Cuadros de Resultados
    pdf.ln(10)
    y_pos = pdf.get_y()
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(10, y_pos, 92, 28, 'F')
    pdf.set_xy(10, y_pos + 4)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(92, 6, "PENSIÓN ESTIMADA HOY", ln=True, align="C")
    pdf.set_font("helvetica", "B", 16)
    pdf.set_x(10)
    pdf.cell(92, 10, f"${p_hoy:,.2f} MXN", ln=False, align="C")

    pdf.set_fill_color(6, 78, 59)
    pdf.rect(105, y_pos, 92, 28, 'F')
    pdf.set_xy(105, y_pos + 4)
    pdf.cell(92, 6, f"PENSIÓN A LOS {edad_obj} AÑOS", ln=True, align="C")
    pdf.set_font("helvetica", "B", 16)
    pdf.set_x(105)
    pdf.cell(92, 10, f"${p_proyectada:,.2f} MXN", ln=True, align="C")
    
    # Tabla
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15) 
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "  2. PROYECCIÓN DE CRECIMIENTO ANUAL", ln=True)
    pdf.ln(5)
    
    # Firma y nombre centrado abajo
    pdf.set_y(250)
    try: pdf.image("assets/firma.png", 150, 235, 40)
    except: pdf.line(150, 255, 190, 255)
    
    pdf.set_y(260)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_x(140)
    pdf.cell(60, 5, "Ing. Roberto Villarreal Glz", ln=True, align="C")
    pdf.set_font("helvetica", "", 8)
    pdf.set_x(140)
    pdf.cell(60, 4, "Especialista en Pensiones Ley 73", ln=True, align="C")
    
    return bytes(pdf.output())

# Interfaz Streamlit (SIN st.divider)
st.title("OPTIPENSIÓN 73")
st.markdown("---") # Esto reemplaza la línea que fallaba

edad_val = st.sidebar.number_input("Edad", 50, 70, 57)
sem_val = st.sidebar.number_input("Semanas", 500, 2500, 1315)
sal_val = st.sidebar.number_input("Salario", 100.0, 3000.0, 959.15)

# Valores de prueba para ver el PDF
p_hoy = 14356.06
p_obj = 16382.65
df = pd.DataFrame([{"Año": 2026, "Edad": 57, "Pensión": 14356.06}])

pdf_bytes = generar_pdf_pro(df, p_hoy, p_obj, edad_val, 60, sal_val, sem_val)
st.download_button("📥 Descargar Reporte PDF", pdf_bytes, "Reporte.pdf")


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
