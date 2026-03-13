import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Importación de tu motor de cálculo (asegúrate de que el nombre del archivo en core coincida)
from core.calculadora_pension import calcular_pension_ley73

# ---------------------------------------------------
# CONFIGURACION DE LA PÁGINA
# ---------------------------------------------------
st.set_page_config(
    page_title="Optipensión 73",
    layout="centered",
    page_icon="💰"
)

# ---------------------------------------------------
# HEADER (LOGOTIPO Y TÍTULO)
# ---------------------------------------------------
col_logo, col_title = st.columns([1,4])

with col_logo:
    # Asegúrate de que la ruta assets/image.jpg sea correcta en tu repositorio
    st.image("assets/image.jpg", width=90)

with col_title:
    st.title("Optipensión 73")
    st.caption("Simulador Estratégico de Pensión IMSS Ley 73")

st.divider()

# ---------------------------------------------------
# FORMULARIO DE ENTRADA
# ---------------------------------------------------
st.subheader("Datos del trabajador")

col1, col2 = st.columns(2)

with col1:
    edad_actual = st.number_input(
        "Edad actual",
        min_value=40,
        max_value=65,
        value=57
    )
    semanas = st.number_input(
        "Semanas cotizadas",
        min_value=500,
        max_value=3000,
        value=1315
    )

with col2:
    salario = st.number_input(
        "Salario promedio diario (SDI)",
        min_value=100.0,
        max_value=5000.0,
        value=959.15
    )
    edad_retiro = st.selectbox(
        "Edad de retiro",
        [60, 61, 62, 63, 64, 65],
        index=0  # Por defecto 60 años (75%)
    )

inflacion = st.number_input(
    "Inflación anual estimada (%)",
    min_value=0.0,
    max_value=15.0,
    value=4.5
)

esposa = st.checkbox("Asignación por esposa (15%)", value=True)

# ---------------------------------------------------
# LÓGICA DE CÁLCULO Y RESULTADOS
# ---------------------------------------------------
if st.button("Recalcular simulación"):
    
    # 1. Ejecución del cálculo profesional desde tu motor
    # Esta función ya debe incluir el factor de edad (75%-100%) y asignaciones
    pension_hoy, pension_futura = calcular_pension_ley73(
        salario_diario=salario,
        semanas_cotizadas=semanas,
        edad_actual=edad_actual,
        edad_retiro=edad_retiro,
        inflacion_anual=inflacion,
        esposa=esposa
    )

    # 2. Despliegue de indicadores principales
    st.success(f"### 💰 Pensión estimada actual: ${pension_hoy:,.2f} MXN")
    st.info(f"### 📈 Pensión proyectada al retiro: ${pension_futura:,.2f} MXN")

    # 3. Generación de datos para Proyección Anual (Gráfica y Tabla)
    ano_actual = datetime.now().year
    datos_proyeccion = []

    for i in range((edad_retiro - edad_actual) + 1):
        anio = ano_actual + i
        edad_iter = edad_actual + i
        
        # Proyección basada únicamente en la inflación acumulada sobre la pensión base
        pension_proyectada = pension_hoy * ((1 + (inflacion/100)) ** i)
        
        datos_proyeccion.append({
            "Año": anio,
            "Edad": edad_iter,
            "Pensión mensual": round(pension_proyectada, 2)
        })

    df = pd.DataFrame(datos_proyeccion)

    # 4. Visualización de Gráfica
    st.subheader("📊 Proyección de crecimiento de la pensión")
    fig = px.line(
        df, 
        x="Año", 
        y="Pensión mensual",
        markers=True,
        text="Pensión mensual",
        template="plotly_dark"
    )
    fig.update_traces(textposition="top center", line_color="#1E88E5")
    fig.update_layout(yaxis_tickformat="$,.0f")
    st.plotly_chart(fig, use_container_width=True)

    # 5. Tabla de Datos
    st.subheader("📋 Tabla de proyección anual")
    # Formateamos la tabla para que se vea profesional con signos de pesos
    st.dataframe(
        df.style.format({"Pensión mensual": "${:,.2f}", "Año": "{:.0f}"}),
        use_container_width=True
    )

# ---------------------------------------------------
# FOOTER (LEGAL Y CONTACTO)
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
