def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # --- 1. ENCABEZADO ---
    try: pdf.image("assets/image.jpg", 10, 8, 33)
    except: pass
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, "ESTRATEGIA DE RETIRO: OPTIPENSIÓN 73", ln=True, align="R")
    pdf.ln(15)
    pdf.line(10, 38, 200, 38)

    # --- 2. DIAGNÓSTICO ---
    pdf.set_y(45)
    pdf.set_fill_color(243, 244, 246)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  1. DIAGNÓSTICO DE SITUACIÓN ACTUAL", ln=True, fill=True)
    pdf.set_font("helvetica", "", 11)
    pdf.ln(2)
    pdf.cell(0, 8, f" Edad Actual: {edad_act} años  |  Semanas: {sem}  |  SBC: ${sal:,.2f}", ln=True)

    # --- 3. CUADROS DE RESULTADOS (Con más espacio) ---
    pdf.ln(10)
    y_pos = pdf.get_y()
    
    # Cuadro Izquierdo
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(10, y_pos, 92, 28, 'F')
    pdf.set_xy(10, y_pos + 4)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(92, 8, "PENSIÓN ESTIMADA HOY", ln=True, align="C")
    pdf.set_font("helvetica", "B", 16)
    pdf.set_x(10)
    pdf.cell(92, 12, f"${p_hoy:,.2f} MXN", ln=False, align="C")

    # Cuadro Derecho
    pdf.set_fill_color(6, 78, 59)
    pdf.rect(105, y_pos, 92, 28, 'F')
    pdf.set_xy(105, y_pos + 4)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(92, 8, f"PENSIÓN A LOS {edad_obj} AÑOS", ln=True, align="C")
    pdf.set_font("helvetica", "B", 16)
    pdf.set_x(105)
    pdf.cell(92, 12, f"${p_proyectada:,.2f} MXN", ln=True, align="C")
    
    # --- 4. TABLA DE PROYECCIÓN (Bajamos el inicio) ---
    pdf.set_text_color(0, 0, 0)
    pdf.ln(18) # Más espacio aquí para que no se vea amontonado
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "  2. PROYECCIÓN DE CRECIMIENTO ANUAL", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(45, 10, "Año", 1, 0, "C", True)
    pdf.cell(45, 10, "Edad", 1, 0, "C", True)
    pdf.cell(95, 10, "Pensión Estimada Mensual", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    for i, row in df.iterrows():
        pdf.cell(45, 8, str(int(row['Año'])), 1, 0, "C")
        pdf.cell(45, 8, str(int(row['Edad'])), 1, 0, "C")
        pdf.cell(95, 8, f"${row['Pensión']:,.2f} MXN", 1, 1, "R")

    # --- 5. NOTAS LEGALES (Términos y Condiciones) ---
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 5, "NOTAS LEGALES Y CONDICIONES:", ln=True)
    pdf.set_font("helvetica", "", 8)
    pdf.set_text_color(50, 50, 50)
    clausulas = [
        "1. Este cálculo es una proyección estimada basada en la Ley del Seguro Social de 1973.",
        "2. Los montos pueden variar según cambios en el valor de la UMA o actualizaciones de la ley.",
        "3. No representa una oferta vinculante del IMSS; es una herramienta de planeación financiera.",
        "4. El cálculo considera la inflación anual estimada proporcionada en el simulador."
    ]
    for linea in clausulas:
        pdf.cell(0, 4, linea, ln=True)

    # --- 6. FIRMA ---
    pdf.set_y(260) # Lo mandamos al fondo de la hoja
    pdf.set_draw_color(0, 0, 0)
    pdf.line(140, 268, 195, 268) # Línea de firma
    pdf.set_y(269)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(17, 24, 39)
    pdf.cell(0, 5, "Ing. Roberto Villarreal Glz", ln=True, align="R")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 5, "Consultoría Especializada Optipensión 73", ln=True, align="R")
    
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
