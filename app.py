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

# --- FUNCIÓN PDF: DISEÑO PRO CON ESPACIOS CORREGIDOS ---
def generar_pdf(df, p_hoy, p_meta, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=False) 
    
    # 1. ENCABEZADO (Logo con espacio)
    try:
        pdf.image("assets/image.jpg", 12, 12, 38) # Logo a la izquierda
    except:
        pass
        
    pdf.set_font("helvetica", "B", 20)
    pdf.set_xy(60, 18)
    pdf.cell(0, 10, "Reporte Estratégico de Pensión IMSS", ln=True, align="R")
    pdf.set_font("helvetica", "", 12)
    pdf.set_x(60)
    pdf.cell(0, 7, "Consultoría Especializada Ley 1973", ln=True, align="R")
    pdf.set_font("helvetica", "I", 9)
    pdf.set_x(60)
    pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    
    # --- AQUÍ BAJAMOS TODO EL BLOQUE PARA QUE NO SE EMPALME ---
    pdf.set_y(55) 

    # 2. SECCIÓN DATOS
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 9, "  1. Diagnóstico de Situación Actual", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 6, f"      - Edad del Asegurado: {edad_act} años", ln=True)
    pdf.cell(0, 6, f"      - Semanas Cotizadas: {sem} semanas", ln=True)
    pdf.cell(0, 6, f"      - Salario Diario (SBC): ${sal:,.2f} MXN", ln=True)
    
    pdf.ln(8)

    # 3. RESULTADOS
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 9, "  2. Resultados Proyectados", ln=True, fill=True)
    pdf.ln(3)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 6, f"      Pensión estimada hoy: ${p_hoy:,.2f} MXN", ln=True)
    pdf.ln(2)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, f"      PENSIÓN A LOS {edad_obj} AÑOS: ${p_meta:,.2f} MXN", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(8)

    # 4. TABLA (COMPACTA)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(30, 7, "Año", border=1, align="C", fill=True)
    pdf.cell(30, 7, "Edad", border=1, align="C", fill=True)
    pdf.cell(70, 7, "Pensión Mensual Proyectada", border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 10)
    # Limitamos a 8 filas para asegurar que quepa la firma en la misma hoja
    for index, row in df.head(8).iterrows():
        pdf.cell(30, 6, str(int(row['Año'])), border=1, align="C")
        pdf.cell(30, 6, str(int(row['Edad'])), border=1, align="C")
        pdf.cell(70, 6, f"${row['Pensión']:,.2f} MXN", border=1, align="C")
        pdf.ln()

    # 5. BLOQUE LEGAL (ANCLADO AL FONDO)
    pdf.set_y(240) 
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 5, "Notas Legales:", ln=True)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    legal_text = (
        "Este documento es una proyección informativa basada en la Ley 73 del IMSS. Los montos son estimados y no garantizan "
        "derechos ante el Instituto. El Ing. Roberto Villarreal Glz no se hace responsable por el uso de esta información."
    )
    pdf.multi_cell(0, 4, legal_text)
    
    # 6. FIRMA
    pdf.set_y(255)
    pdf.set_text_color(0, 0, 0)
    pdf.line(130, 272, 195, 272) 
    try:
        pdf.image("assets/firma.png", 145, 252, 40) 
    except:
        pass
    
    pdf.set_y(274)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 4, "Director General de Optipensión 73", ln=True, align="R")
    
    return bytes(pdf.output())

# ---------------------------------------------------
# INTERFAZ STREAMLIT
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])
with col_logo:
    st.image("assets/image.jpg", width=85)
with col_title:
    st.title("Optipensión 73")
    st.caption("Consultoría Especializada en Pensiones IMSS")

st.divider()

st.subheader("Datos del trabajador")
c1, c2 = st.columns(2)

with c1:
    edad_val = st.number_input("Edad actual", 50, 65, 57)
    sem_val = st.number_input("Semanas cotizadas", 500, 3000, 1315)

with c2:
    sal_val = st.number_input("Salario diario (SDI)", 100.0, value=959.15)
    edad_meta = st.selectbox("Edad de retiro objetivo", [60,61,62,63,64,65], index=0)

inf_val = st.number_input("Inflación anual estimada (%)", value=4.50)
esp_val = st.checkbox("Asignación por esposa (15%)", value=True)

if st.button("Generar Proyección Profesional"):
    p_60, _ = calcular_pension_ley73(sal_val, sem_val, edad_val, 60, inf_val, esp_val)
    p_100 = p_60 / 0.75 
    
    datos_l = []
    for i in range((65 - edad_val) + 1):
        ed_i = edad_val + i
        f_i = (1 + (inf_val/100)) ** i
        f_ed = 0.75 if ed_i < 60 else FACTORES_EDAD.get(ed_i, 1.0)
        p_i = (p_100 * f_ed) * f_i
        datos_l.append({"Año": 2026 + i, "Edad": ed_i, "Pensión": round(p_i, 2)})

    df_res = pd.DataFrame(datos_l)
    val_h = df_res[df_res['Edad'] == edad_val]['Pensión'].values[0]
    val_m = df_res[df_res['Edad'] == edad_meta]['Pensión'].values[0]

    st.success(f"### Pensión hoy: ${val_h:,.2f} MXN")
    st.info(f"### PENSION PROYECTADA AL RETIRO ({edad_meta} AÑOS): ${val_m:,.2f} MXN")

    fig = px.bar(
        df_res, 
        x="Edad", 
        y="Pensión", 
        color="Pensión",
        color_continuous_scale="Viridis",
        template="plotly_dark", 
        text_auto=".0f"
    )
    st.plotly_chart(fig, use_container_width=True)

    try:
        pdf_out = generar_pdf(df_res, val_h, val_m, edad_val, edad_meta, sal_val, sem_val)
        st.download_button(
            label="📥 Descargar Reporte PDF con Firma",
            data=pdf_out,
            file_name=f"Reporte_Optipension_{edad_val}anos.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error técnico: {e}")

st.divider()
st.markdown("Ing. Roberto Villarreal Glz. © 2026 | Torreón, Coahuila")


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
