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

# --- FUNCIÓN PARA GENERAR EL PDF (DISEÑO MEJORADO) ---
def generar_pdf(df, p_ahora, p_meta, edad_actual, edad_obj, salario, semanas):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. LOGO (Más chico y elegante)
    try:
        pdf.image("assets/image.jpg", 10, 10, 25) 
    except:
        pass
        
    # 2. ENCABEZADO CENTRADO Y ESPACIADO
    pdf.set_font("helvetica", "B", 18)
    pdf.ln(10)
    pdf.cell(0, 10, "Reporte Estrategico de Pension IMSS", ln=True, align="C")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, "Ley del Seguro Social 1973", ln=True, align="C")
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 10, f"Fecha de emision: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    
    pdf.ln(20) # Espacio generoso para que respire

    # 3. DATOS TÉCNICOS (Distribuidos)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  Resumen del Perfil:", ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 8, f"  * Edad al momento del calculo: {edad_actual} anos", ln=True)
    pdf.cell(0, 8, f"  * Semanas cotizadas reconocidas: {semanas}", ln=True)
    pdf.cell(0, 8, f"  * Salario Diario Integrado (SDI): ${salario:,.2f} MXN", ln=True)
    
    pdf.ln(15) # Más espacio entre secciones

    # 4. RESULTADOS PROYECTADOS
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  Resultados de la Proyeccion:", ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 10, f"  Pension estimada a la edad actual: ${p_ahora:,.2f} MXN", ln=True)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 51, 102) # Azul oscuro profesional
    pdf.cell(0, 10, f"  PENSION PROYECTADA AL RETIRO ({edad_obj} ANOS): ${p_meta:,.2f} MXN", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(30) # Espacio amplio para cubrir la hoja

    # 5. BLOQUE DE FIRMA (Natural)
    # Movemos la firma hacia abajo para que ocupe el final de la hoja
    y_firma = pdf.get_y()
    
    # Línea de firma
    pdf.line(120, y_firma + 20, 190, y_firma + 20)
    
    # Imagen de firma (Sin fondo)
    try:
        # Ajustamos la posición para que "pise" la línea
        pdf.image("assets/firma.png", 135, y_actual_pos := y_firma - 5, 45) 
    except:
        pass
    
    pdf.set_y(y_firma + 22)
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
    edad_user = st.number_input("Edad actual", min_value=50, max_value=65, value=57)
    semanas_user = st.number_input("Semanas cotizadas", min_value=500, max_value=3000, value=1315)

with c2:
    salario_user = st.number_input("Salario diario (SDI)", min_value=100.0, value=960.0)
    edad_meta_user = st.selectbox("Edad de retiro objetivo", [60,61,62,63,64,65], index=0)

inflacion_user = st.number_input("Inflación anual estimada (%)", value=4.5)
esposa_user = st.checkbox("Asignación por esposa (15%)", value=True)

if st.button("Generar Proyección Profesional"):
    # Cálculos
    p_60, _ = calcular_pension_ley73(salario_user, semanas_user, edad_user, 60, inflacion_user, esposa_user)
    p_100 = p_60 / 0.75 
    
    datos_grafica = []
    for i in range((65 - edad_user) + 1):
        ed_i = edad_user + i
        f_inf = (1 + (inflacion_user/100)) ** i
        f_ed = 0.75 if ed_i < 60 else FACTORES_EDAD.get(ed_i, 1.0)
        p_i = (p_100 * f_ed) * f_inf
        datos_grafica.append({"Año": 2026 + i, "Edad": ed_i, "Pensión": round(p_i, 2)})

    df_res = pd.DataFrame(datos_grafica)
    p_hoy_val = df_res[df_res['Edad'] == edad_user]['Pensión'].values[0]
    p_meta_val = df_res[df_res['Edad'] == edad_meta_user]['Pensión'].values[0]

    # Pantalla
    st.success(f"### 💰 Estimación a edad actual: ${p_hoy_val:,.2f} MXN")
    st.info(f"### 📈 Proyección al retiro ({edad_meta_user} años): ${p_meta_val:,.2f} MXN")

    fig = px.bar(df_res, x="Edad", y="Pensión", template="plotly_dark", text_auto=".0f")
    st.plotly_chart(fig, use_container_width=True)

    # Descarga PDF
    try:
        pdf_final = generar_pdf(df_res, p_hoy_val, p_meta_val, edad_user, edad_meta_user, salario_user, semanas_user)
        st.download_button(
            label="📥 Descargar Reporte PDF para el Cliente",
            data=pdf_final,
            file_name=f"Reporte_Optipension_{edad_user}anos.pdf",
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
