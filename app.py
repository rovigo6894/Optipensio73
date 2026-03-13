import streamlit as st
from core.calculadora_pension import calcular_pension_ley73

st.title("Simulador de Pensión IMSS Ley 73")

salario = st.number_input("Salario diario promedio", value=959.15)

semanas = st.number_input("Semanas cotizadas", value=1315)

edad_actual = st.number_input("Edad actual", value=57)

edad_retiro = st.selectbox("Edad retiro", [60,61,62,63,64,65])

inflacion = st.number_input("Inflación anual (%)", value=4.0)

esposa = st.checkbox("Tiene esposa")

if st.button("Calcular pensión"):

    hoy, futuro = calcular_pension_ley73(
        salario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa
    )

    st.success(f"Pensión estimada hoy: ${hoy:,.2f}")
    st.success(f"Pensión proyectada: ${futuro:,.2f}")
