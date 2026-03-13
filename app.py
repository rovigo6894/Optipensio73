# --- FUNCIÓN PDF CORREGIDA Y ALINEADA ---
def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. ENCABEZADO Y LOGO
    try: pdf.image("assets/image.jpg", 10, 8, 33)
    except: pass
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(17, 24, 39) 
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, "ESTRATEGIA DE RETIRO: OPTIPENSIÓN 73", ln=True, align="R")
    
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %I:%M %p')}", ln=True, align="R")
    
    pdf.ln(15)
    pdf.set_draw_color(59, 130, 246) 
    pdf.line(10, 38, 200, 38)

    # 2. SECCIÓN: SITUACIÓN ACTUAL
    pdf.set_y(45)
    pdf.set_fill_color(243, 244, 246)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 10, "  1. DIAGNÓSTICO DE SITUACIÓN ACTUAL", ln=True, fill=True)
    
    pdf.ln(4)
    pdf.set_font("helvetica", "", 11)
    pdf.cell(45, 8, f" Edad Actual: {edad_act} años", 0)
    pdf.cell(55, 8, f" Semanas: {sem}", 0)
    pdf.cell(60, 8, f" Salario Diario (SBC): ${sal:,.2f}", 0, 1)

    # 3. SECCIÓN: RESULTADOS DESTACADOS (CUADROS CORREGIDOS)
    pdf.ln(8)
    y_cuadros = pdf.get_y()
    
    # --- CUADRO IZQUIERDO (PENSIÓN HOY) ---
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 10)
    # Título del cuadro
    pdf.set_xy(10, y_cuadros)
    pdf.cell(92, 8, "PENSIÓN ESTIMADA AL DÍA DE HOY", ln=0, fill=True, align="C")
    # Fondo para el valor
    pdf.set_xy(10, y_cuadros + 8)
    pdf.set_fill_color(255, 255, 255) # Fondo blanco para resaltar el número
    pdf.set_text_color(30, 41, 59)   # Texto en azul oscuro
    pdf.set_draw_color(30, 41, 59)
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(92, 14, f"${p_hoy:,.2f} MXN", border=1, ln=0, align="C")

    # --- CUADRO DERECHO (PENSIÓN PROYECTADA) ---
    pdf.set_fill_color(6, 78, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 10)
    # Título del cuadro
    pdf.set_xy(105, y_cuadros)
    pdf.cell(92, 8, f"PENSIÓN PROYECTADA ({edad_obj} AÑOS)", ln=0, fill=True, align="C")
    # Fondo para el valor
    pdf.set_xy(105, y_cuadros + 8)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(6, 78, 59)    # Texto en verde oscuro
    pdf.set_draw_color(6, 78, 59)
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(92, 14, f"${p_proyectada:,.2f} MXN", border=1, ln=1, align="C")
    
    pdf.set_text_color(0, 0, 0) # Reset color texto

    # 4. TABLA DE CRECIMIENTO ANUAL
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  2. PROYECCIÓN DE CRECIMIENTO POR EDAD", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    
    pdf.cell(45, 10, "Año Calendario", 1, 0, "C", True)
    pdf.cell(45, 10, "Edad del Asegurado", 1, 0, "C", True)
    pdf.cell(95, 10, "Pensión Mensual Estimada", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    fill = False
    for i, row in df.iterrows():
        pdf.cell(45, 8, str(int(row['Año'])), 1, 0, "C", fill)
        pdf.cell(45, 8, str(int(row['Edad'])), 1, 0, "C", fill)
        pdf.cell(95, 8, f"${row['Pensión']:,.2f} MXN", 1, 1, "R", fill)
        fill = not fill

    # Pie de página
    pdf.set_y(265)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "Este documento es una proyección informativa basada en la Ley del Seguro Social de 1973.", ln=True, align="C")
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    
    return bytes(pdf.output())


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
