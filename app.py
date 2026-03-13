import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from fpdf import FPDF 
import io

# Importación de lógica y parámetros
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

# --- OCULTAR ELEMENTOS DE STREAMLIT ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# CONFIGURACION DE PÁGINA
# ---------------------------------------------------
st.set_page_config(
    page_title="Optipensión 73",
    layout="centered",
    page_icon="💰"
)

# --- FUNCIÓN PARA GENERAR EL PDF (PÁGINA COMPLETA) ---
def generar_pdf(df, p_hoy, p_meta, edad_act, edad_obj, sal, sem):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    # 1. LOGO Y ENCABEZADO
    try:
        pdf.image("assets/image.jpg", 15, 15, 30) 
    except:
        pass
        
    pdf.set_font("helvetica", "B", 22)
    pdf.ln(15)
    pdf.cell(0, 15, "Reporte Estrategico de Pension IMSS", ln=True, align="R")
    pdf.set_font("helvetica", "", 14)
    pdf.cell(0, 8, "Consultoria Especializada Ley 1973", ln=True, align="R")
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 8, f"Fecha de Analisis: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    
    pdf.ln(25) # Espaciado para cubrir la hoja

    # 2. SECCIÓN DE DATOS BASE
    pdf.set_fill_color(230, 235, 245)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 12, "  1. Diagnostico de Situacion Actual", ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"  - Edad del Asegurado: {edad_act} anos", ln=True)
    pdf.cell(0, 10, f"  - Historial de Semanas: {sem} semanas", ln=True)
    pdf.cell(0, 10, f"  - Salario Base de Cotizacion (SBC): ${sal:,.2f} MXN", ln=True)
    
    pdf.ln(15)

    # 3. RESULTADOS DE PROYECCIÓN
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 12, "  2. Resultados de la Proyeccion", ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"  Estimacion de pension a la edad actual: ${p_hoy:,.2f} MXN", ln=True)
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 12, f"  PENSION OBJETIVO A LOS {edad_obj} ANOS: ${p_meta:,.2f} MXN", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(15)

    # 4. TABLA DE CRECIMIENTO (Para llenar la hoja con valor)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  Proyeccion Anual de Incremento:", ln=True)
    pdf.set_font("helvetica", "B", 10)
    # Encabezados de tabla
    pdf.cell(40, 8, "Año", border=1, align="C")
    pdf.cell(40, 8, "Edad", border=1, align="C")
    pdf.cell(80, 8, "Monto Estimado Mensual", border=1, align="C")
    pdf.ln()
    
    pdf.set_font("helvetica", "", 10)
    # Mostrar solo los primeros 5 registros para no saturar
    for index, row in df.head(6).iterrows():
        pdf.cell(40, 8, str(int(row['Año'])), border=1, align="C")
        pdf.cell(40, 8, str(int(row['Edad'])), border=1, align="C")
        pdf.cell(80, 8, f"${row['Pensión']:,.2f} MXN", border=1, align="C")
        pdf.ln()

    # 5. BLOQUE LEGAL (Base de la página)
    pdf.set_y(-75) 
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    aviso = (
        "NOTAS LEGALES: Este documento es una proyeccion informativa basada en los datos proporcionados por el cliente y la Ley 73 del IMSS. "
        "No constituye una resolucion oficial ni garantiza el monto final. El Ing. Roberto Villarreal Glz. no se hace responsable por "
        "decisiones tomadas con base en este simulador. Se recomienda ratificar datos ante el Instituto."
    )
    pdf.multi_cell(0, 4, aviso, align="J")
    
    # 6. FIRMA PROFESIONAL
    pdf.set_y(-45)
    pdf.set_text_color(0, 0, 0)
    pdf.line(120, pdf.get_y() + 15, 190, pdf.get_y() + 15)
    try:
        pdf.image("assets/firma.png", 135, pdf.get_y() - 15, 45) # Firma sobre la línea
    except:
        pass
    
    pdf.set_y(-28)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 5, "Director General de Optipension 73", ln=True, align="R")
    
    return bytes(pdf.output())

# ---------------------------------------------------
# LÓGICA DE LA APLICACIÓN
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])
with col_logo:
    st.image("assets/image.jpg", width=85)
with col_title:
    st.title("Optipensión 73")
    st.caption("Estrategia Integral para tu Retiro")

st.divider()

st.subheader("Configuración del Cálculo")
c1, c2 = st.columns(2)

with c1:
    ed_u = st.number_input("Edad actual", 50, 65, 57)
    se_u = st.number_input("Semanas reconocidas", 500, 3000, 1315)

with c2:
    sa_u = st.number_input("Salario Diario (SDI)", 100.0, 3000.0, 960.0)
    ed_m = st.selectbox("Edad objetivo de retiro", [60,61,62,63,64,65], index=0)

inf_u = st.number_input("Inflación estimada anual (%)", 4.5)
esp_u = st.checkbox("Asignación Familiar (Esposa/Concubina)", True)

if st.button("Generar Analisis y Reporte PDF"):
    # Cálculos
    p_60, _ = calcular_pension_ley73(sa_u, se_u, ed_u, 60, inf_u, esp_u)
    p_100 = p_60 / 0.75 
    
    datos_graf = []
    for i in range((65 - ed_u) + 1):
        e_i = ed_u + i
        f_i = (1 + (inf_u/100)) ** i
        f_e = 0.75 if e_i < 60 else FACTORES_EDAD.get(e_i, 1.0)
        p_i = (p_100 * f_e) * f_i
        datos_graf.append({"Año": 2026 + i, "Edad": e_i, "Pensión": round(p_i, 2)})

    df_res = pd.DataFrame(datos_graf)
    p_ahora = df_res[df_res['Edad'] == ed_u]['Pensión'].values[0]
    p_meta = df_res[df_res['Edad'] == ed_m]['Pensión'].values[0]

    st.success(f"### 💰 Pensión Estimada Hoy: ${p_ahora:,.2f} MXN")
    st.info(f"### 📈 Proyección a los {ed_m} años: ${p_meta:,.2f} MXN")

    fig = px.bar(df_res, x="Edad", y="Pensión", template="plotly_dark", text_auto=".0f", color="Pensión")
    st.plotly_chart(fig, use_container_width=True)

    try:
        pdf_final = generar_pdf(df_res, p_ahora, p_meta, ed_u, ed_m, sa_u, se_u)
        st.download_button(
            label="📥 DESCARGAR REPORTE PROFESIONAL PARA CLIENTE",
            data=pdf_final,
            file_name=f"Reporte_Optipension_{ed_u}anos.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error técnico en PDF: {e}")

st.divider()
st.markdown("<p style='text-align:center;'><b>Optipensión 73</b> | Torreón, Coahuila | Ing. Roberto Villarreal</p>", unsafe_allow_html=True)


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
