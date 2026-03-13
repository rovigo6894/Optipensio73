import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Importamos la lógica y los parámetros
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

st.set_page_config(page_title="Optipensión 73", layout="centered", page_icon="💰")

# --- HEADER ---
col_logo, col_title = st.columns([1,4])
with col_logo:
    st.image("assets/image.jpg", width=90)
with col_title:
    st.title("Optipensión 73")
    st.caption("Simulador Estratégico de Pensión IMSS Ley 73")

st.divider()

# --- FORMULARIO ---
st.subheader("Datos del trabajador")
c1, c2 = st.columns(2)

with c1:
    edad_actual = st.number_input("Edad actual", min_value=50, max_value=65, value=57)
    semanas = st.number_input("Semanas cotizadas", min_value=500, max_value=3000, value=1315)

with c2:
    salario = st.number_input("Salario diario (SDI)", min_value=100.0, value=960.0)
    edad_retiro = st.selectbox("Edad de retiro deseada", [60,61,62,63,64,65], index=0)

inflacion = st.number_input("Inflación anual estimada (%)", value=4.5)
esposa = st.checkbox("Asignación por esposa (15%)", value=True)

# --- EJECUCIÓN ---
if st.button("Recalcular simulación"):
    # Llamada al motor profesional
    pension_hoy, pension_futura = calcular_pension_ley73(
        salario, semanas, edad_actual, edad_retiro, inflacion, esposa
    )

    st.success(f"### 💰 Pensión estimada actual (a los {Edad actual} años): ${pension_hoy:,.2f} MXN")
    st.info(f"### 📈 Pensión proyectada al retiro (con inflación): ${pension_futura:,.2f} MXN")

    # --- PROYECCIÓN ANUAL PARA GRÁFICA ---
    # Solo proyectamos el efecto del tiempo e inflación sobre la base calculada
    ano_actual = datetime.now().year
    datos = []
    
    for i in range((edad_retiro - edad_actual) + 1):
        edad_iter = edad_actual + i
        anio_iter = ano_actual + i
        # Crecimiento compuesto por inflación
        pension_iter = pension_hoy * ((1 + (inflacion/100)) ** i)
        
        datos.append({
            "Edad": edad_iter,
            "Año": anio_iter,
            "Pensión mensual": round(pension_iter, 2)
        })

    df = pd.DataFrame(datos)

    # --- VISUALIZACIÓN ---
    st.subheader("📊 Proyección de crecimiento de la pensión")
    fig = px.bar(df, x="Edad", y="Pensión mensual", text_auto=".0f", template="plotly_dark")
    fig.update_traces(marker_color='#1E88E5')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Tabla de proyección anual")
    st.dataframe(df.style.format({"Pensión mensual": "${:,.2f}"}), use_container_width=True)

# --- FOOTER LEGAL ---
st.divider()
st.markdown("<div style='text-align:center;'>© 2026 Optipensión 73 · Versión PRO</div>", unsafe_allow_html=True)
