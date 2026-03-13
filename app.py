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

# --- FUNCIÓN PARA GENERAR EL PDF (PÁGINA ÚNICA REAL) ---
def generar_pdf(df, p_hoy, p_meta, edad_act, edad_obj, sal, sem):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # 1. LOGO Y ENCABEZADO
    try:
        pdf.image("assets/image.jpg", 15, 15, 30) 
    except:
        pass
        
    pdf.set_font("helvetica", "B", 20)
    pdf.ln(10)
    pdf.cell(0, 12, "Reporte Estrategico de Pension IMSS", ln=True, align="R")
    pdf.set_font("helvetica", "", 14)
    pdf.cell(0, 8, "Consultoria Especializada Ley 1973", ln=True, align="R")
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 8, f"Fecha de Analisis: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    
    pdf.ln(20) # Espacio para que no se amontone arriba

    # 2. DATOS BASE
    pdf.set_fill_color(235, 240, 250)
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, "  1. Diagnostico de Situacion Actual", ln=True, fill=True)
    pdf.ln(4)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"  - Edad del Asegurado: {edad_act} anos", ln=True)
    pdf.cell(0, 8, f"  - Historial de Semanas: {sem} semanas", ln=True)
    pdf.cell(0, 8, f"  - Salario Base de Cotizacion (SBC): ${sal:,.2f} MXN", ln=True)
    
    pdf.ln(10)

    # 3. RESULTADOS
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, "  2. Proyeccion de Resultados", ln=True, fill=True)
    pdf.ln(4)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"  Estimacion de pension a la edad actual: ${p_hoy:,.2f} MXN", ln=True)
    pdf.ln(4)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 50, 120)
    pdf.cell(0, 10, f"  PENSION PROYECTADA AL RETIRO ({edad_obj} ANOS): ${p_meta:,.2f} MXN", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(10)

    # 4. TABLA DE CRECIMIENTO
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "  Tabla de Incremento Anual:", ln=True)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(35, 8, "Anio", border=1, align="C", fill=True)
    pdf.cell(35, 8, "Edad", border=1, align="C", fill=True)
    pdf.cell(80, 8, "Pension Mensual Estimada", border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("helvetica", "", 10)
    # Mostramos los datos clave para que quepa todo en una hoja
    for index, row in df.head(9).iterrows(): 
        pdf.cell(35, 7, str(int(row['Año'])), border=1, align="C")
        pdf.cell(35, 7, str(int(row['Edad'])), border=1, align="C")
        pdf.cell(80, 7, f"${row['Pensión']:,.2f} MXN", border=1, align="C")
        pdf.ln()

    # 5. NOTA LEGAL COMPLETA (Ajustada al final de la página)
    pdf.set_y(-65) 
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, "3. Notas Legales y Exencion de Responsabilidad:", ln=True)
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    txt_legal = (
        "a) Este documento es una proyeccion informativa basada en la Ley 73 del IMSS. "
        "b) Los resultados son estimaciones y pueden variar segun cambios en la legislacion o criterios oficiales del Instituto. "
        "c) Este reporte NO constituye un dictamen legal, resolucion de pension u oferta vinculante. "
        "d) El Ing. Roberto Villarreal Glz. no se hace responsable por decisiones financieras tomadas basadas en esta proyeccion. "
        "e) Se recomienda validar sus datos ante las instancias oficiales del IMSS antes de iniciar tramites."
    )
    pdf.multi_cell(0, 5, txt_legal)
    
    # 6. FIRMA
    pdf.set_y(-35)
    pdf.set_text_color(0, 0, 0)
    pdf.line(125, pdf.get_y() + 12, 195, pdf.get_y() + 12)
    try:
        pdf.image("assets/firma.png", 140, pdf.get_y() - 12, 45) 
    except:
        pass
    
    pdf.set_y(-22)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 5, "Director General de Optipension 73", ln=True, align="R")
    
    return bytes(pdf.output())

# ---------------------------------------------------
# INTERFAZ DE USUARIO
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])
with col_logo:
    st.image("assets/image.jpg", width=85)
with col_title:
    st.title("Optipensión 73")
    st.caption("Consultoría Estratégica en Pensiones IMSS")

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
    # Lógica de cálculo
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
    st.info(f"### PENSION PROYECTADA AL RETIRO ({edad_meta} ANOS): ${val_m:,.2f} MXN")

    # GRÁFICA CON COLORES REALES
    fig = px.bar(
        df_res, 
        x="Edad", 
        y="Pensión", 
        color="Pensión", # Esto activa la escala de colores
        color_continuous_scale="Viridis", # Escala profesional (puedes usar 'Blues' o 'Turbo')
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
        st.error(f"Error en PDF: {e}")

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
