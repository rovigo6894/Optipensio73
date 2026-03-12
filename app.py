import streamlit as st
from Core.pension_imss import calcular_pension_base

st.set_page_config(page_title="OptiPensión 73", layout="centered")

st.title("💰 OptiPensión 73")
st.subheader("Simulador de pensión IMSS Ley 73")

st.divider()

salario = st.number_input(
    "Salario promedio diario",
    min_value=0.0,
    max_value=10000.0,
    value=965.0,
    step=10.0
)

semanas = st.number_input(
    "Semanas cotizadas",
    min_value=0,
    max_value=3000,
    value=1315,
    step=1
)

edad = st.selectbox(
    "Edad de retiro",
    [60, 61, 62, 63, 64, 65]
)

esposa = st.checkbox(
    "Asignación por esposa",
    value=True
)

if st.button("Calcular pensión"):

    pension = calcular_pension_base(
        salario,
        semanas,
        edad,
        esposa
    )

    st.success(f"Pensión estimada mensual: ${pension:,.2f}")
