import streamlit as st
import pandas as pd
import plotly.express as px

from Core.pension_imss import calcular_pension_ley73
from Core.proyeccion_pension import proyectar_pension


st.set_page_config(
    page_title="Simulador Pensión IMSS Ley 73",
    page_icon="📊",
    layout="centered"
)

st.title("Simulador de Pensión IMSS - Ley 73")

st.write("Herramienta de estimación de pensión conforme a reglas del IMSS.")

st.divider()

# =========================
# ENTRADAS
# =========================

st.subheader("Datos del trabajador")

salario = st.number_input(
    "Salario diario promedio",
    min_value=0.0,
    value=965.0
)

semanas = st.number_input(
    "Semanas cotizadas",
    min_value=500,
    value=1315
)

edad_actual = st.number_input(
    "Edad actual",
    min_value=40,
    max_value=65,
    value=57
)

edad_retiro = st.number_input(
    "Edad de retiro",
    min_value=60,
    max_value=65,
    value=60
)

inflacion = st.number_input(
    "Inflación anual (%)",
    min_value=0.0,
    max_value=20.0,
    value=4.0
) / 100

esposa = st.checkbox("Tiene esposa dependiente")

st.divider()

# =========================
# CALCULO
# =========================

if st.button("Calcular pensión"):

    pension_hoy, pension_futura = calcular_pension_ley73(
        salario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa
    )

    st.subheader("Resultado")

    col1, col2 = st.columns(2)

    col1.metric(
        "Pensión estimada hoy",
        f"${pension_hoy:,.2f}"
    )

    col2.metric(
        f"Pensión estimada a los {edad_retiro} años",
        f"${pension_futura:,.2f}"
    )

    st.divider()

    # =========================
    # PROYECCION
    # =========================

    st.subheader("Proyección de pensión por inflación")

    años = edad_retiro - edad_actual

    datos = proyectar_pension(
        pension_hoy,
        inflacion,
        años
    )

    lista_años = list(range(edad_actual, edad_retiro + 1))

    df = pd.DataFrame({
        "Edad": lista_años,
        "Pensión mensual": datos
    })

    fig = px.line(
        df,
        x="Edad",
        y="Pensión mensual",
        markers=True,
        title="Proyección de pensión hasta el retiro"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Tabla de proyección")

    st.dataframe(
        df.style.format({
            "Pensión mensual": "${:,.2f}"
        })
    )
