import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from core.calculadora_pension import calcular_pension_ley73

st.set_page_config(
    page_title="Simulador Pensión IMSS Ley 73",
    layout="centered"
)

st.title("Simulador de Pensión IMSS Ley 73")

tabs = st.tabs(["Simulación pensión", "Modalidad 40"])

# =====================================
# TAB 1 SIMULACION PENSION
# =====================================

with tabs[0]:

    st.subheader("Datos del trabajador")

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
        [60,61,62,63,64,65]
    )

    inflacion = st.number_input(
        "Inflación anual estimada (%)",
        min_value=0.0,
        max_value=15.0,
        value=4.5,
        step=0.1
    )

    esposa = st.checkbox("Asignación esposa (15%)")

    st.divider()

    if st.button("Calcular pensión"):

        pension_hoy, pension_futura = calcular_pension_ley73(
            salario,
            semanas,
            edad_actual,
            edad_retiro,
            inflacion,
            esposa
        )

        st.subheader("Resultados")

        st.success(f"Pensión estimada hoy: ${pension_hoy:,.2f}")

        st.success(
            f"Pensión proyectada a los {edad_retiro} años: ${pension_futura:,.2f}"
        )

        # =========================
        # TABLA PROYECCION
        # =========================

        inflacion_decimal = inflacion / 100

        anos = edad_retiro - edad_actual

        ano_actual = datetime.now().year

        datos = []

        pension = pension_hoy

        for i in range(anos + 1):

            datos.append({
                "Año": ano_actual + i,
                "Pensión mensual": round(pension,2)
            })

            pension = pension * (1 + inflacion_decimal)

        df = pd.DataFrame(datos)

        st.subheader("Proyección anual de la pensión")

        st.dataframe(df)

        # =========================
        # GRAFICA
        # =========================

        st.subheader("Crecimiento estimado de la pensión")

        fig, ax = plt.subplots()

        ax.plot(df["Año"], df["Pensión mensual"], marker="o")

        ax.set_xlabel("Año")

        ax.set_ylabel("Pensión mensual")

        ax.set_title("Proyección de pensión con inflación")

        ax.grid(True)

        st.pyplot(fig)


# =====================================
# TAB 2 MODALIDAD 40
# =====================================

with tabs[1]:

    st.subheader("Simulación Modalidad 40")

    st.write(
        """
        En esta sección se analizará el impacto de cotizar en 
        Modalidad 40 sobre la pensión final.

        Próximamente se agregará:
        
        • simulación de salario Modalidad 40  
        • costo total de inversión  
        • incremento de pensión  
        • retorno de inversión (ROI)
        """
    )
