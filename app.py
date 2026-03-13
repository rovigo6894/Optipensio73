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

# --- FUNCIÓN PDF: UNA SOLA PÁGINA ---
def generar_pdf(df, p_hoy, p_meta, edad_act, edad_obj, sal, sem):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 10, 15) # Márgenes optimizados
    
    # 1. Logo
    try:
        pdf.image("assets/image.jpg", 15, 12, 28) 
    except:
        pass
        
    # 2. Encabezado
    pdf.set_font("helvetica", "B", 18)
    pdf.ln(5)
    pdf.cell(0, 10, "Reporte Estrategico de Pension IMSS", ln=True, align="R")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 7, "Ley del Seguro Social 1973", ln=True, align="R")
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    
    pdf.ln(15)

    # 3. Datos (Compactos)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  1. Datos del Trabajador:", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(0, 7, f"  - Edad: {edad_act} anos | Semanas: {sem} | SDI: ${sal:,.2f} MXN", ln=True)
    
    pdf.ln(8)

    # 4. Resultados Proyectados
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  2. Proyeccion Estimada:", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, f"  Pension hoy: ${p_hoy:,.2f} MXN", ln=True)
    pdf.set_font("helvetica", "B", 13)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, f"  PENSION AL RETIRO ({edad_obj} ANOS): ${p_meta:,.2f} MXN", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(8)

    # 5. Tabla (Limitada para que no salte de hoja)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "  Crecimiento Anual Estimado:", ln=True)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(30, 7, "Anio", border=1, align="C")
    pdf.cell(30, 7, "Edad", border=1, align="C")
    pdf.cell(60, 7, "Monto Estimado", border=1, align="C")
    pdf.ln()
    
    pdf.set_font("helvetica", "", 10)
    for index, row in df.head(7).iterrows(): # 7 filas máximo para asegurar una hoja
        pdf.cell(30, 6, str(int(row['Año'])), border=1, align="C")
        pdf.cell(30, 6, str(int(row['Edad'])), border=1, align="C")
        pdf.cell(60, 6, f"${row['Pensión']:,.2f}", border=1, align="C")
        pdf.ln()

    # 6. Legal (Al pie)
    pdf.set_y(-45)
    pdf.set_font("helvetica", "I", 7)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 4, "Nota: Esta es una simulacion informativa basada en Ley 73. No garantiza derechos ante el IMSS.", align="C")
    
    # 7. Firma
    pdf.set_y(-30)
    pdf.set_text_color(0, 0, 0)
    pdf.line(130, pdf.get_y() + 10, 190, pdf.get_y() + 10)
    try:
        pdf.image("assets/firma.png", 145, pdf.get_y() - 10, 38) 
    except:
        pass
    
    pdf.set_y(-18)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    
    return bytes(pdf.output())

# ---------------------------------------------------
# INTERFAZ (REGRESO AL DISEÑO ORIGINAL)
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])
with col_logo:
    st.image("assets/image.jpg", width=85)
with col_title:
    st.title("Optipensión 73")
    st.caption("Consultoría Estratégica en Pensiones IMSS")

st.divider()

st.subheader("Datos del trabajador") # Regresamos a tu título original
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
    st.info(f"### PENSION PROYECTADA AL RETIRO ({edad_meta} ANOS): ${val_m:,.2f} MXN")

    # Gráfica con tus colores originales
    fig = px.bar(df_res, x="Edad", y="Pensión", template="plotly_dark", text_auto=".0f")
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
