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

# --- FUNCIÓN PARA GENERAR EL PDF (TODO EN UNA HOJA) ---
def generar_pdf(df, p_hoy, p_meta, edad_act, edad_obj, sal, sem):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 10, 15) # Márgenes más compactos
    
    # 1. LOGO Y ENCABEZADO REDUCIDO
    try:
        pdf.image("assets/image.jpg", 15, 10, 25) 
    except:
        pass
        
    pdf.set_font("helvetica", "B", 18)
    pdf.ln(5)
    pdf.cell(0, 10, "Reporte Estrategico de Pension IMSS", ln=True, align="R")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 6, "Consultoria Especializada Ley 1973", ln=True, align="R")
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 6, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    
    pdf.ln(10)

    # 2. DATOS BASE
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, " 1. Diagnostico de Situacion Actual", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(0, 7, f" - Edad: {edad_act} anos | Semanas: {sem} | SBC: ${sal:,.2f} MXN", ln=True)
    
    pdf.ln(5)

    # 3. RESULTADOS
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, " 2. Resultados de la Proyeccion", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, f" Pension estimada a la edad actual: ${p_hoy:,.2f} MXN", ln=True)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 10, f" PENSION OBJETIVO A LOS {edad_obj} ANOS: ${p_meta:,.2f} MXN", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(5)

    # 4. TABLA COMPACTA (Solo 5 filas para ahorrar espacio)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, " Proyeccion Anual:", ln=True)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(30, 7, "Anio", border=1, align="C")
    pdf.cell(30, 7, "Edad", border=1, align="C")
    pdf.cell(60, 7, "Monto Mensual", border=1, align="C")
    pdf.ln()
    
    pdf.set_font("helvetica", "", 10)
    for index, row in df.head(8).iterrows(): # Mostramos hasta 8 años
        pdf.cell(30, 6, str(int(row['Año'])), border=1, align="C")
        pdf.cell(30, 6, str(int(row['Edad'])), border=1, align="C")
        pdf.cell(60, 6, f"${row['Pensión']:,.2f}", border=1, align="C")
        pdf.ln()

    # 5. AVISO LEGAL PEQUEÑO
    pdf.ln(8)
    pdf.set_font("helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    aviso = (
        "AVISO LEGAL: Este documento es una proyeccion informativa basada en la Ley 73 del IMSS. No constituye una resolucion oficial. "
        "El Ing. Roberto Villarreal Glz. no se hace responsable por decisiones tomadas con base en este simulador."
    )
    pdf.multi_cell(0, 4, aviso, align="C")
    
    # 6. FIRMA AL PIE (Ajustada para que no salte de hoja)
    pdf.set_y(-35)
    pdf.set_text_color(0, 0, 0)
    pdf.line(130, pdf.get_y() + 10, 190, pdf.get_y() + 10)
    try:
        pdf.image("assets/firma.png", 145, pdf.get_y() - 10, 35) 
    except:
        pass
    
    pdf.set_y(-22)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 4, "Director Optipension 73", ln=True, align="R")
    
    return bytes(pdf.output())

# ---------------------------------------------------
# LÓGICA DE LA APP (STREAMLIT)
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])
with col_logo:
    st.image("assets/image.jpg", width=85)
with col_title:
    st.title("Optipensión 73")
    st.caption("Consultoría Estratégica")

st.divider()

c1, c2 = st.columns(2)
with c1:
    ed_u = st.number_input("Edad actual", 50, 65, 57)
    se_u = st.number_input("Semanas", 500, 3000, 1315)
with c2:
    sa_u = st.number_input("Salario Diario", 100.0, 3000.0, 960.0)
    ed_m = st.selectbox("Edad retiro", [60,61,62,63,64,65], index=0)

inf_u = st.number_input("Inflación (%)", value=4.5)
esp_u = st.checkbox("Asignación Familiar", True)

if st.button("Generar Reporte Una Hoja"):
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

    st.success(f"Pensión Hoy: ${p_ahora:,.2f} | Meta: ${p_meta:,.2f}")
    fig = px.bar(df_res, x="Edad", y="Pensión", template="plotly_dark", text_auto=".0f")
    st.plotly_chart(fig, use_container_width=True)

    try:
        pdf_final = generar_pdf(df_res, p_ahora, p_meta, ed_u, ed_m, sa_u, se_u)
        st.download_button(
            label="📥 Descargar Reporte (1 Hoja)",
            data=pdf_final,
            file_name=f"Reporte_Optipension.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error: {e}")


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
