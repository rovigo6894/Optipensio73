import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# Importación de tu lógica de negocio
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

st.set_page_config(page_title="Optipensión 73 PRO", layout="wide")

def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. LOGO PEQUEÑO (20mm)
    try: pdf.image("assets/image.jpg", 10, 8, 20) 
    except: pass
    
    pdf.set_font("helvetica", "B", 16)
    pdf.set_xy(40, 12)
    pdf.cell(0, 8, "ESTRATEGIA DE RETIRO: OPTIPENSIÓN 73", ln=True, align="R")
    pdf.line(10, 30, 200, 30)

    # 2. DIAGNÓSTICO (Más arriba para ganar espacio)
    pdf.set_y(35)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, "  1. DIAGNÓSTICO DE SITUACIÓN ACTUAL", ln=True, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.ln(2)
    pdf.cell(0, 6, f" Edad Actual: {edad_act} años  |  Semanas: {sem}  |  SBC: ${sal:,.2f}", ln=True)

    # 3. CUADROS DE RESULTADOS
    pdf.ln(5)
    y_res = pdf.get_y()
    pdf.set_fill_color(30, 41, 59) # Azul oscuro
    pdf.rect(10, y_res, 92, 25, 'F')
    pdf.set_xy(10, y_res + 3)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(92, 6, "PENSIÓN ESTIMADA AL DÍA DE HOY", ln=True, align="C")
    pdf.set_font("helvetica", "B", 14)
    pdf.set_x(10)
    pdf.cell(92, 10, f"${p_hoy:,.2f} MXN", ln=False, align="C")

    pdf.set_fill_color(6, 78, 59) # Verde oscuro
    pdf.rect(105, y_res, 92, 25, 'F')
    pdf.set_xy(105, y_res + 3)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(92, 6, f"PENSIÓN PROYECTADA ({edad_obj} AÑOS)", ln=True, align="C")
    pdf.set_font("helvetica", "B", 14)
    pdf.set_x(105)
    pdf.cell(92, 10, f"${p_proyectada:,.2f} MXN", ln=True, align="C")

    # 4. TABLA DE PROYECCIÓN
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "  2. PROYECCIÓN DE CRECIMIENTO POR EDAD", ln=True)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(45, 8, "Año Calendario", 1, 0, "C", True)
    pdf.cell(45, 8, "Edad Asegurado", 1, 0, "C", True)
    pdf.cell(95, 8, "Pensión Mensual Estimada", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    for _, row in df.iterrows():
        pdf.cell(45, 7, str(int(row['Año'])), 1, 0, "C")
        pdf.cell(45, 7, str(int(row['Edad'])), 1, 0, "C")
        pdf.cell(95, 7, f"${row['Pensión']:,.2f} MXN", 1, 1, "R")

    # 5. CONDICIONES LEGALES (Aseguradas)
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(0, 5, "TÉRMINOS Y CONDICIONES LEGALES:", ln=True)
    pdf.set_font("helvetica", "", 7)
    pdf.multi_cell(0, 4, "Este documento es una proyección informativa basada en la Ley del Seguro Social de 1973. El monto real será determinado únicamente por el IMSS al momento del trámite. Se considera la inflación anual capturada en el simulador.")

    # 6. FIRMA Y CARGO CENTRADOS
    pdf.set_y(245)
    try: pdf.image("assets/firma.png", 150, 235, 35)
    except: pdf.line(145, 255, 195, 255)
    
    pdf.set_y(256)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_x(140)
    pdf.cell(60, 5, "Ing. Roberto Villarreal Glz", ln=True, align="C")
    pdf.set_font("helvetica", "", 9)
    pdf.set_x(140)
    pdf.cell(60, 4, "Especialista en Pensiones Ley 73", ln=True, align="C")
    
    return bytes(pdf.output())

# --- INTERFAZ STREAMLIT ---
st.title("OPTIPENSIÓN 73")
st.markdown("---") 

with st.sidebar:
    st.header("Configuración")
    edad = st.number_input("Edad actual", 50, 65, 57)
    semanas = st.number_input("Semanas", 500, 2500, 1315)
    salario = st.number_input("SBC", 100.0, 3500.0, 959.15)
    inflacion = st.number_input("Inflación %", 0.0, 10.0, 4.5)
    esposa = st.checkbox("Asignación Esposa", value=True)

# Lógica de cálculo
p_60, _ = calcular_pension_ley73(salario, semanas, edad, 60, inflacion, esposa)
p_base = p_60 / 0.75
datos = []
for i in range((65 - edad) + 1):
    ed_i = edad + i
    p_i = (p_base * FACTORES_EDAD.get(ed_i, 1.0)) * ((1 + inflacion/100)**i)
    datos.append({"Año": 2026+i, "Edad": ed_i, "Pensión": round(p_i, 2)})
df_res = pd.DataFrame(datos)

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Pensión Hoy", f"${datos[0]['Pensión']:,.2f}")
    pdf_bytes = generar_pdf_pro(df_res, datos[0]['Pensión'], datos[3]['Pensión'], edad, 60, salario, semanas)
    st.download_button("📥 Descargar Reporte PDF", pdf_bytes, "Reporte_Retiro.pdf")

with col2:
    st.plotly_chart(px.bar(df_res, x="Edad", y="Pensión"))


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
