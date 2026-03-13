import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from fpdf import FPDF 
import io

# Importación de lógica y parámetros
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

# --- OCULTAR OPCIONES DE STREAMLIT ---
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

# --- FUNCIÓN PARA GENERAR EL PDF (CON DESCARGOS LEGALES) ---
def generar_pdf(df, p_hoy, p_meta, edad_act, edad_obj, sal, sem):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. LOGO
    try:
        pdf.image("assets/image.jpg", 10, 10, 25) 
    except:
        pass
        
    # 2. ENCABEZADO
    pdf.set_font("helvetica", "B", 18)
    pdf.ln(10)
    pdf.cell(0, 10, "Reporte Estrategico de Pension IMSS", ln=True, align="C")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, "Ley del Seguro Social 1973", ln=True, align="C")
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", ln=True, align="C")
    
    pdf.ln(15)

    # 3. DATOS DEL TRABAJADOR
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  1. Datos Base para el Calculo:", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 7, f"  * Edad al momento del analisis: {edad_act} anos", ln=True)
    pdf.cell(0, 7, f"  * Semanas cotizadas registradas: {sem}", ln=True)
    pdf.cell(0, 7, f"  * Salario Diario Integrado (SDI): ${sal:,.2f} MXN", ln=True)
    
    pdf.ln(10)

    # 4. RESULTADOS PROYECTADOS
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  2. Proyeccion Estimada:", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 9, f"  Pension estimada con parametros actuales: ${p_hoy:,.2f} MXN", ln=True)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, f"  PENSION PROYECTADA AL RETIRO ({edad_obj} ANOS): ${p_meta:,.2f} MXN", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(15)

    # 5. DESCARGOS LEGALES (IMPORTANTE PARA TU PROTECCIÓN)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 7, "3. Notas Legales y Exencion de Responsabilidad:", ln=True)
    pdf.set_font("helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
    
    clausulas = [
        "a) Este documento es un simulador informativo basado en modelos matematicos de la Ley 73 del IMSS.",
        "b) Los resultados son ESTIMACIONES y pueden variar segun cambios en la legislacion o criterios del Instituto.",
        "c) El presente reporte NO constituye un dictamen legal, resolucion de pension u oferta vinculante.",
        "d) El consultor no se hace responsable por decisiones financieras tomadas basadas en esta proyeccion.",
        "e) Se recomienda validar siempre sus datos ante las instancias oficiales del IMSS antes de iniciar tramites."
    ]
    
    for c in clausulas:
        pdf.multi_cell(0, 5, c)
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)

    # 6. BLOQUE DE FIRMA
    y_firma = pdf.get_y()
    pdf.line(120, y_firma + 15, 190, y_firma + 15)
    try:
        pdf.image("assets/firma.png", 135, y_firma - 10, 45) 
    except:
        pass
    
    pdf.set_y(y_firma + 17)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 5, "Director General de Optipension 73", ln=True, align="R")
    
    return bytes(pdf.output())

# ---------------------------------------------------
# INTERFAZ DE USUARIO (APP)
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])
with col_logo:
    st.image("assets/image.jpg", width=85)
with col_title:
    st.title("Optipensión 73")
    st.caption("Consultoría Estratégica en Pensiones IMSS")

st.divider()

st.subheader("Configuración de la simulación")
c1, c2 = st.columns(2)

with c1:
    ed_a = st.number_input("Edad actual", min_value=50, max_value=65, value=57)
    se_a = st.number_input("Semanas cotizadas", min_value=500, max_value=3000, value=1315)

with c2:
    sa_a = st.number_input("Salario diario (SDI)", min_value=100.0, value=960.0)
    ed_o = st.selectbox("Edad de retiro objetivo", [60,61,62,63,64,65], index=0)

inf_a = st.number_input("Inflación anual estimada (%)", value=4.5)
esp_a = st.checkbox("Asignación por esposa (15%)", value=True)

if st.button("Generar Proyección Profesional"):
    p_60, _ = calcular_pension_ley73(sa_a, se_a, ed_a, 60, inf_a, esp_a)
    p_100 = p_60 / 0.75 
    
    datos_g = []
    for i in range((65 - ed_a) + 1):
        e_i = ed_a + i
        f_i = (1 + (inf_a/100)) ** i
        f_e = 0.75 if e_i < 60 else FACTORES_EDAD.get(e_i, 1.0)
        p_i = (p_100 * f_e) * f_i
        datos_g.append({"Año": 2026 + i, "Edad": e_i, "Pensión": round(p_i, 2)})

    df_res = pd.DataFrame(datos_g)
    val_hoy = df_res[df_res['Edad'] == ed_a]['Pensión'].values[0]
    val_meta = df_res[df_res['Edad'] == ed_o]['Pensión'].values[0]

    st.success(f"### 💰 Estimación a edad actual: ${val_hoy:,.2f} MXN")
    st.info(f"### 📈 Proyección al retiro ({ed_o} años): ${val_meta:,.2f} MXN")

    fig = px.bar(df_res, x="Edad", y="Pensión", template="plotly_dark", text_auto=".0f")
    st.plotly_chart(fig, use_container_width=True)

    try:
        pdf_f = generar_pdf(df_res, val_hoy, val_meta, ed_a, ed_o, sa_a, se_a)
        st.download_button(
            label="📥 Descargar Reporte PDF para el Cliente",
            data=pdf_f,
            file_name=f"Reporte_Optipension_{ed_a}anos.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error al generar PDF: {e}")


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
