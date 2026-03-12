import streamlit as st
import pandas as pd

from Core.pension_imss import (
    calcular_pension_ley73,
    proyectar_pension_anual
)

st.set_page_config(page_title="OptiPensión 73", page_icon="💰")

st.title("💰 OptiPensión 73")
st.subheader("Simulador de pensión IMSS Ley 73")

st.divider()

salario = st.number_input(
    "Salario promedio diario",
    min_value=100.0,
    max_value=5000.0,
    value=959.15
)

semanas = st.number_input(
    "Semanas cotizadas",
    min_value=500,
    max_value=3000,
    value=1315
)

edad_actual = st.number_input(
    "Edad actual",
    min_value=40,
    max_value=65,
    value=57
)

edad_retiro = st.selectbox(
    "Edad de retiro",
    [60, 61, 62, 63, 64, 65]
)

inflacion = st.number_input(
    "Inflación anual estimada (%)",
    min_value=0.0,
    max_value=15.0,
    value=4.5
) / 100

esposa = st.checkbox("Asignación por esposa")

st.divider()

if st.button("Calcular pensión"):

    pension_actual, pension_futura = calcular_pension_ley73(
        salario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa
    )

    st.success(f"Pensión estimada mensual hoy: ${pension_actual:,.2f}")

    st.info(
        f"Pensión estimada al retiro ajustada por inflación: ${pension_futura:,.2f}"
    )

    st.divider()

    st.subheader("Proyección anual de pensión")

    proyeccion = proyectar_pension_anual(
        pension_actual,
        edad_actual,
        edad_retiro,
        inflacion
    )

    df = pd.DataFrame(proyeccion)

    st.dataframe(df)

    st.line_chart(
        df.set_index("Edad")["Pension_mensual"]
    )
