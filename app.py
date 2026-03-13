import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Importación del motor y parámetros centralizados
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

# ---------------------------------------------------
# CONFIGURACION
# ---------------------------------------------------
st.set_page_config(
    page_title="Optipensión 73",
    layout="centered"
)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])

with col_logo:
    st.image("assets/image.jpg", width=90)

with col_title:
    st.title("Optipensión 73")
    st.caption("Simulador Estratégico de Pensión IMSS Ley 73")

st.divider()

# ---------------------------------------------------
# FORMULARIO
# ---------------------------------------------------
st.subheader("Datos del trabajador")

col1, col2 = st.columns(2)

with col1:
    edad_actual = st.number_input("Edad actual", min_value=50, max_value=65, value=57)
    semanas = st.number_input("Semanas cotizadas", min_value=500, max_value=3000, value=1315)

with col2:
    salario = st.number_input("Salario diario (SDI)", min_value=100.0, value=960.0)
    edad_retiro = st.selectbox("Edad de retiro deseada", [60,61,62,63,64,65], index=0)

inflacion = st.number_input("Inflación anual (%)", value=4.5)
esposa = st.checkbox("Asignación por esposa (15%)", value=True)

# ---------------------------------------------------
# CALCULO
# ---------------------------------------------------
if st.button("Recalcular simulación"):

    # Llamada limpia al motor: el motor ya aplica factor de edad y asignaciones
    pension_hoy, pension_futura = calcular_pension_ley73(
        salario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa
    )

    st.success(f"### 💰 Pensión estimada actual (a los {edad_retiro} años): ${pension_hoy:,.2f} MXN")
    st.info(f"### 📈 Pensión proyectada al retiro (con inflación): ${pension_futura:,.2f} MXN")

    # ---------------------------------------------------
    # PROYECCION ANUAL (CRECIMIENTO POR INFLACIÓN)
    # ---------------------------------------------------
    ano_actual = datetime.now().year
    datos = []

    # Proyectamos el efecto del tiempo e inflación sobre la base calculada por el motor
    for i in range((65 - edad_actual) + 1):
        edad_iter = edad_actual + i
        anio_iter = ano_actual + i
        
        # Aplicamos crecimiento compuesto por inflación partiendo del valor base
        pension_iter = pension_hoy * ((1 + (inflacion/100)) ** i)
        
        datos.append({
            "Edad": edad_iter,
            "Año": anio_iter,
            "Pensión mensual": round(pension_iter, 2)
        })

    df = pd.DataFrame(datos)

    # ---------------------------------------------------
    # VISUALIZACIÓN
    # ---------------------------------------------------
    st.subheader("📊 Proyección de crecimiento")
    fig = px.bar(df, x="Edad", y="Pensión mensual", template="plotly_dark", text_auto=".0f")
    fig.update_traces(marker_color='#1E88E5')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Tabla de proyección anual")
    st.dataframe(df.style.format({"Pensión mensual": "${:,.2f}"}), use_container_width=True)

# ---------------------------------------------------
# FOOTER PRO (RESTAURADO)
# ---------------------------------------------------
st.divider()

st.markdown(
"""
<div style='text-align:center;'>

### 📌 TÉRMINOS Y CONDICIONES
Este simulador proporciona estimaciones basadas en modelos matemáticos y la Ley 73 del IMSS.  
Los resultados son aproximados y no constituyen un dictamen oficial.

---

### 🔒 AVISO DE PRIVACIDAD
Esta aplicación DEMO no almacena datos personales ingresados por el usuario.  
Los cálculos se realizan en tiempo real.

---

### ⚖️ LEGAL
Propiedad intelectual © 2026  
**Ing. Roberto Villarreal Glz** 📧 contacto@optipension73.com  
📱 WhatsApp: 871 579 1810  
📍 Torreón, Coahuila · México

<br>

**© 2026 Optipensión 73 · Versión PRO**

</div>
""",
unsafe_allow_html=True
)
