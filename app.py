import streamlit as st
from core.calculadora_pension import calcular_pension_ley73

st.set_page_config(
    page_title="Simulador Pensión IMSS Ley 73",
    layout="centered"
)

st.title("Simulador de Pensión IMSS Ley 73")

st.write("Calcula tu pensión estimada conforme a la Ley 73 del IMSS.")

st.divider()

# =============================
# DATOS DEL USUARIO
# =============================

salario = st.number_input(
    "Salario diario promedio",
    min_value=100.0,
    max_value=5000.0,
    value=959.15,
    step=1.0
)

semanas = st.number_input(
    "Semanas cotizadas",
    min_value=500,
    max_value=3000,
    value=1315
)

edad_actual = st.number_input(
    "Edad actual",
    min_value=50,
    max_value=65,
    value=57
)

edad_retiro = st.selectbox(
    "Edad de retiro",
    [60, 61, 62, 63, 64, 65],
    index=0
)

inflacion = st.number_input(
    "Inflación anual estimada (%)",
    min_value=0.0,
    max_value=15.0,
    value=4.0,
    step=0.1
)

esposa = st.checkbox("Tiene esposa (asignación familiar 15%)")

st.divider()

# =============================
# BOTON CALCULO
# =============================

if st.button("Calcular pensión"):

    pension_hoy, pension_futura = calcular_pension_ley73(
        salario_diario=salario,
        semanas=semanas,
        edad_actual=edad_actual,
        edad_retiro=edad_retiro,
        inflacion=inflacion,
        esposa=esposa
    )

    st.subheader("Resultados")

    st.success(f"Pensión estimada hoy: ${pension_hoy:,.2f} MXN")

    st.success(f"Pensión proyectada a los {edad_retiro} años: ${pension_futura:,.2f} MXN")

    anos = edad_retiro - edad_actual

    st.info(
        f"Proyección considerando {anos} años de inflación anual estimada de {inflacion}%."
    )
