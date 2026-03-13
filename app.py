import streamlit as st
import pandas as pd
import plotly.express as px

# 1. IMPORTACIÓN DE TU LÓGICA ORIGINAL (Para que los números cuadren)
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

st.set_page_config(page_title="Optipensión 73 PRO", layout="wide")

# --- SIDEBAR ORIGINAL ---
with st.sidebar:
    st.header("Configuración")
    edad_actual = st.number_input("Edad actual", 50, 65, 57)
    semanas = st.number_input("Semanas Reconocidas", 500, 2500, 1315)
    salario_sbc = st.number_input("Salario Diario (SBC)", 100.0, 3500.0, 959.15)
    inflacion = st.number_input("Inflación Est. %", 0.0, 10.0, 4.50)
    asignacion_esposa = st.checkbox("Asignación Esposa", value=True)

# --- LÓGICA DE CÁLCULO PROFESIONAL ---
# Calculamos la base a los 60 años usando tu función externa
p_60, _ = calcular_pension_ley73(salario_sbc, semanas, edad_actual, 60, inflacion, asignacion_esposa)
p_base_100 = p_60 / 0.75  # Recuperamos la pensión al 100% para proyectar

datos_proyeccion = []
for i in range((65 - edad_actual) + 1):
    ed_i = edad_actual + i
    factor_edad = FACTORES_EDAD.get(ed_i, 0.75 if ed_i < 60 else 1.0)
    # Aplicamos inflación compuesta por año
    p_i = (p_base_100 * factor_edad) * ((1 + inflacion/100)**i)
    datos_proyeccion.append({
        "Año": 2026 + i,
        "Edad": ed_i,
        "Pensión": round(p_i, 2)
    })

df_resumen = pd.DataFrame(datos_proyeccion)

# --- INTERFAZ VISUAL ---
st.title("OPTIPENSIÓN 73")
st.markdown("---") # Reemplazo seguro del divider que fallaba

# Métricas destacadas
pension_hoy = df_resumen.iloc[0]['Pensión']
st.metric(label="Pensión Estimada Hoy", value=f"${pension_hoy:,.2f}")

# Gráfica Profesional
fig = px.bar(
    df_resumen, 
    x="Edad", 
    y="Pensión", 
    text="Pensión",
    title="Crecimiento de Pensión por Edad",
    color="Pensión",
    color_continuous_scale="Blues"
)
fig.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
st.plotly_chart(fig, use_container_width=True)

# Tabla de datos
st.subheader("Detalle de Proyección Anual")
st.dataframe(df_resumen.style.format({"Pensión": "${:,.2f}"}), use_container_width=True)

# Sección de Términos (al final para que no estorbe)
with st.expander("Ver Términos y Condiciones Legales"):
    st.write("El uso de este simulador implica la aceptación de los siguientes términos...")
    st.write("1. Naturaleza del servicio: Estimaciones basadas en la Ley 73 del IMSS.")


# ---------------------------------------------------
# FOOTER PRO (ESTILO IMÁGENES)
# ---------------------------------------------------
st.divider()

st.markdown(
"""
<div style='text-align:left;'>

### 📌 TÉRMINOS Y CONDICIONES
El uso de este simulador implica la aceptación de los siguientes términos:
* **Naturaleza del servicio**: Este simulador proporciona estimaciones basadas en modelos matemáticos y la Ley 73 del IMSS. Los resultados son aproximados y no constituyen un dictamen oficial ni una garantía de pago.
* **Limitación de responsabilidad**: Optipensión 73 no se hace responsable por decisiones tomadas basadas exclusivamente en los resultados de esta demo. Se recomienda consultar con un asesor certificado.
* **Uso personal**: Esta herramienta es para uso informativo personal.

---

### 🔒 AVISO DE PRIVACIDAD
**Protección de datos**: Esta aplicación DEMO **NO almacena, guarda ni comparte** ningún dato personal ingresado por el usuario. Todos los cálculos se realizan en tiempo real y los datos se descartan al cerrar la sesión.

**Cookies**: No utilizamos cookies de rastreo ni almacenamos información de navegación.

---

### ⚖️ LEGAL
**Propiedad intelectual**: El código, diseño y contenido de Optipensión 73 son propiedad del Ing. Roberto Villarreal Glz. © 2026. Todos los derechos reservados.

📧 **Email**: contacto@optipension73.com  
📱 **WhatsApp**: 871 579 1810  
📍 **Oficina**: Torreón, Coahuila · México

<br>

<div style='text-align:center;'>
**© 2026 Optipensión 73 · Versión PRO**
</div>

</div>
""",
unsafe_allow_html=True
)
