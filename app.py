import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from fpdf import FPDF # Necesitarás instalarlo: pip install fpdf
import io

# Importaciones de tu motor
from core.calculadora_pension import calcular_pension_ley73
from config.parametros import FACTORES_EDAD

# --- FUNCIÓN PARA GENERAR EL PDF ---
def generar_pdf(df, p_ahora, p_meta, edad_actual, edad_obj, salario, semanas):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado con Logo
    try:
        pdf.image("assets/image.jpg", 10, 8, 30) # Logo
    except:
        pass
        
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte Estratégico de Pensión IMSS Ley 73", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(10)
    
    # Datos de entrada
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Resumen de Datos del Trabajador:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"- Edad Actual: {edad_actual} años", ln=True)
    pdf.cell(0, 7, f"- Semanas Cotizadas: {semanas}", ln=True)
    pdf.cell(0, 7, f"- Salario Diario (SDI): ${salario:,.2f} MXN", ln=True)
    pdf.ln(5)
    
    # Resultados Clave
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Proyección de Resultados:", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Pensión estimada a la edad actual ({edad_actual} años): ${p_ahora:,.2f} MXN", ln=True)
    pdf.cell(0, 10, f"Pensión proyectada al retiro ({edad_obj} años): ${p_meta:,.2f} MXN", ln=True)
    pdf.ln(10)
    
    # Tabla de proyección
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 10, "Edad", border=1, align="C")
    pdf.cell(40, 10, "Año", border=1, align="C")
    pdf.cell(60, 10, "Pensión Mensual", border=1, align="C")
    pdf.ln()
    
    pdf.set_font("Arial", "", 10)
    for index, row in df.iterrows():
        pdf.cell(40, 8, str(int(row['Edad'])), border=1, align="C")
        pdf.cell(40, 8, str(int(row['Año'])), border=1, align="C")
        pdf.cell(60, 8, f"${row['Pensión mensual']:,.2f}", border=1, align="C")
        pdf.ln()
    
    pdf.ln(20)
    
    # Firma y Sello Legal
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "__________________________", ln=True, align="R")
    try:
        # Ajusta la posición para que la firma quede sobre la línea
        pdf.image("assets/firma.png", 140, pdf.get_y() - 25, 40) 
    except:
        pass
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 5, "Director General de Optipensión 73", ln=True, align="R")
    
    return pdf.output(dest='S').encode('latin-1')

# --- CÓDIGO PRINCIPAL DE APP.PY ---
# (Mantener el encabezado y formulario igual que antes...)

if st.button("Recalcular simulación"):
    # ... (Cálculos de p_ahora, p_meta y df que ya tienes funcionando) ...
    
    # MOSTRAR RESULTADOS EN PANTALLA
    st.success(f"### 💰 Pensión a la edad actual ({edad_actual} años): ${p_ahora:,.2f} MXN")
    # ... (Gráficas y tabla...)
    
    # BOTÓN PARA DESCARGAR PDF
    pdf_bytes = generar_pdf(df, p_ahora, p_meta, edad_actual, edad_retiro_obj, salario, semanas)
    
    st.download_button(
        label="📥 Descargar Reporte PDF Profesional",
        data=pdf_bytes,
        file_name=f"Reporte_Pension_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )

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
