import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from core.calculadora_pension import calcular_pension_ley73


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
    edad_actual = st.number_input(
        "Edad actual",
        min_value=50,
        max_value=65,
        value=57
    )

with col2:
    salario = st.number_input(
        "Salario diario (SDI)",
        min_value=100.0,
        max_value=5000.0,
        value=960.0
    )

semanas = st.number_input(
    "Semanas cotizadas",
    min_value=500,
    max_value=3000,
    value=1315
)

edad_retiro = st.selectbox(
    "Edad de retiro",
    [60,61,62,63,64,65]
)

inflacion = st.number_input(
    "Inflación anual (%)",
    min_value=0.0,
    max_value=15.0,
    value=4.5
)

esposa = st.checkbox("Asignación por esposa (15%)")

# ---------------------------------------------------
# TABLA PORCENTAJES LEY 73
# ---------------------------------------------------

porcentaje_edad = {
    60: 0.75,
    61: 0.80,
    62: 0.85,
    63: 0.90,
    64: 0.95,
    65: 1.00
}

# ---------------------------------------------------
# CALCULO
# ---------------------------------------------------

if st.button("Recalcular simulación"):

    pension_hoy, pension_futura = calcular_pension_ley73(
        salario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa
    )

    st.success(f"### 💰 Pensión estimada actual: ${pension_hoy:,.0f} MXN")
    st.info(f"### 📈 Pensión proyectada al retiro: ${pension_futura:,.0f} MXN")

    # ---------------------------------------------------
    # PROYECCION
    # ---------------------------------------------------

    inflacion_decimal = inflacion / 100
    ano_actual = datetime.now().year

    datos = []

    pension_base = pension_hoy

    for i in range((edad_retiro - edad_actual) + 1):

        edad = edad_actual + i
        anio = ano_actual + i

        pension = pension_base * ((1 + inflacion_decimal) ** i)

        # aplicar incremento de porcentaje solo desde los 60
        if edad >= 60:
            porcentaje = porcentaje_edad.get(edad, 1.0)
        else:
            porcentaje = 1.0

        pension = pension * porcentaje

        datos.append({
            "Edad": edad,
            "Año": anio,
            "% Edad": int(porcentaje*100),
            "Pensión mensual": pension
        })

    df = pd.DataFrame(datos)

    # ---------------------------------------------------
    # GRAFICA BARRAS
    # ---------------------------------------------------

    st.subheader("📊 Proyección de crecimiento de la pensión")

    fig = px.bar(
        df,
        x="Edad",
        y="Pensión mensual",
        text_auto=".0f"
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Edad",
        yaxis_title="Pensión mensual MXN"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------
    # TABLA
    # ---------------------------------------------------

    st.subheader("📋 Tabla de proyección anual")

    df["Pensión mensual"] = df["Pensión mensual"].map(lambda x: f"${x:,.2f}")

    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------
# FOOTER
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
Ing. Roberto Villarreal Glz  

📧 contacto@optipension73.com  
📱 WhatsApp: 871 579 1810  
📍 Torreón, Coahuila · México

<br>

© 2026 Optipensión 73 · Versión PRO

</div>
""",
unsafe_allow_html=True
)
