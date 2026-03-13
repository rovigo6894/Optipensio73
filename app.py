import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from fpdf import FPDF 
import io

# Importación de lógica y parámetros
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

# ---------------------------------------------------
# CONFIGURACION DE PÁGINA
# ---------------------------------------------------
st.set_page_config(
    page_title="Optipensión 73",
    layout="centered",
    page_icon="💰"
)

# --- FUNCIÓN PARA GENERAR EL PDF (VERSIÓN DEFINITIVA CORREGIDA) ---
def generar_pdf(df, p_ahora, p_meta, edad_actual, edad_obj, salario, semanas):
    # Usamos helvetica para evitar errores de fuentes faltantes en el servidor
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado con Logo
    try:
        pdf.image("assets/image.jpg", 10, 8, 33) 
    except:
        pass
        
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Reporte Estrategico de Pension IMSS Ley 73", ln=True, align="C")
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 10, f"Generado por Optipension 73 el: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(15)
    
    # Resumen Tecnico
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, " Datos del Calculo:", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, f" - Edad al calcular: {edad_actual} anos", ln=True)
    pdf.cell(0, 8, f" - Semanas cotizadas: {semanas}", ln=True)
    pdf.cell(0, 8, f" - Salario Diario Integrado: ${salario:,.2f} MXN", ln=True)
    pdf.ln(5)
    
    # Resultados
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, " Proyeccion de Pension:", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 10, f" Pension estimada a la edad actual: ${p_ahora:,.2f} MXN", ln=True)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 10, f" Pension proyectada al retiro ({edad_obj} anos): ${p_meta:,.2f} MXN", ln=True)
    pdf.ln(10)
    
    # Firma del consultor
    y_actual = pdf.get_y()
    pdf.line(130, y_actual + 20, 190, y_actual + 20)
    try:
        pdf.image("assets/firma.png", 140, y_actual - 5, 40) 
    except:
        pass
    pdf.set_y(y_actual + 22)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 5, "Director General de Optipension 73", ln=True, align="R")
    
    # CONVERSIÓN CRÍTICA: Convertir bytearray a bytes para Streamlit
    return bytes(pdf.output())

# ---------------------------------------------------
# INTERFAZ DE USUARIO (APP)
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])
with col_logo:
    st.image("assets/image.jpg", width=90)
with col_title:
    st.title("Optipensión 73")
    st.caption("Simulador Estratégico de Pensión IMSS Ley 73")

st.divider()

st.subheader("Datos del trabajador")
c1, c2 = st.columns(2)

with c1:
    edad_in = st.number_input("Edad actual", min_value=50, max_value=65, value=57)
    semanas_in = st.number_input("Semanas cotizadas", min_value=500, max_value=3000, value=1315)

with c2:
    salario_in = st.number_input("Salario diario (SDI)", min_value=100.0, value=960.0)
    edad_obj_in = st.selectbox("Edad de retiro objetivo", [60,61,62,63,64,65], index=0)

inflacion_in = st.number_input("Inflación anual estimada (%)", value=4.5)
esposa_in = st.checkbox("Asignación por esposa (15%)", value=True)

if st.button("Recalcular simulación"):
    # Ejecución del motor de cálculo
    p_60, _ = calcular_pension_ley73(salario_in, semanas_in, edad_in, 60, inflacion_in, esposa_in)
    p_base = p_60 / 0.75 
    
    res_list = []
    anio_base = datetime.now().year

    for i in range((65 - edad_in) + 1):
        e_i = edad_in + i
        f_inf = (1 + (inflacion_in/100)) ** i
        f_ed = 0.75 if e_i < 60 else FACTORES_EDAD.get(e_i, 1.0)
        pens_i = (p_base * f_ed) * f_inf
        
        res_list.append({
            "Año": anio_base + i,
            "Edad": e_i,
            "Pensión mensual": round(pens_i, 2)
        })

    df_final = pd.DataFrame(res_list)
    p_hoy = df_final[df_final['Edad'] == edad_in]['Pensión mensual'].values[0]
    p_meta = df_final[df_final['Edad'] == edad_obj_in]['Pensión mensual'].values[0]

    # Visualización de resultados
    st.success(f"### 💰 Pensión estimada hoy ({edad_in} años): ${p_hoy:,.2f} MXN")
    st.info(f"### 📈 Pensión proyectada al retiro ({edad_obj_in} años): ${p_meta:,.2f} MXN")

    fig = px.bar(df_final, x="Edad", y="Pensión mensual", template="plotly_dark", text_auto=".0f")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Tabla de proyección anual")
    st.dataframe(df_final.style.format({"Pensión mensual": "${:,.2f}"}), use_container_width=True)

    # Bloque de descarga de PDF
    try:
        archivo_pdf = generar_pdf(df_final, p_hoy, p_meta, edad_in, edad_obj_in, salario_in, semanas_in)
        st.download_button(
            label="📥 Descargar Reporte PDF con Firma",
            data=archivo_pdf,
            file_name=f"Reporte_Optipension_{edad_in}anos.pdf",
            mime="application/pdf"
        )
    except Exception as error:
        st.error(f"Error técnico al generar el PDF: {error}")


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
