def generar_pdf_pro(df, p_hoy, p_proyectada, edad_act, edad_obj, sal, sem):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # 1. ENCABEZADO (Logo más pequeño: de 35mm a 25mm)
    try: pdf.image("assets/image.jpg", 10, 10, 25) 
    except: pass
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, "ESTRATEGIA DE RETIRO PROFESIONAL", ln=True, align="R")
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 7, "OPTIPENSIÓN 73", ln=True, align="R")
    
    pdf.ln(10)
    pdf.line(10, 38, 200, 38)

    # 2. DIAGNÓSTICO
    pdf.set_y(45)
    pdf.set_fill_color(243, 244, 246)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "  1. DIAGNÓSTICO DE SITUACIÓN ACTUAL", ln=True, fill=True)
    pdf.set_font("helvetica", "", 10)
    pdf.ln(2)
    pdf.cell(0, 6, f" Edad Actual: {edad_act} años  |  Semanas: {sem}  |  Salario Diario: ${sal:,.2f}", ln=True)

    # 3. CUADROS DE RESULTADOS
    pdf.ln(8)
    y_pos = pdf.get_y()
    
    # Izquierdo
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(10, y_pos, 92, 28, 'F')
    pdf.set_xy(10, y_pos + 4)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(92, 6, "PENSIÓN ESTIMADA HOY", ln=True, align="C")
    pdf.set_font("helvetica", "B", 16)
    pdf.set_x(10)
    pdf.cell(92, 12, f"${p_hoy:,.2f} MXN", ln=False, align="C")

    # Derecho
    pdf.set_fill_color(6, 78, 59)
    pdf.rect(105, y_pos, 92, 28, 'F')
    pdf.set_xy(105, y_pos + 4)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(92, 6, f"PENSIÓN A LOS {edad_obj} AÑOS", ln=True, align="C")
    pdf.set_font("helvetica", "B", 16)
    pdf.set_x(105)
    pdf.cell(92, 12, f"${p_proyectada:,.2f} MXN", ln=True, align="C")
    
    # 4. TABLA DE PROYECCIÓN
    pdf.set_text_color(0, 0, 0)
    pdf.ln(12) 
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "  2. PROYECCIÓN DE CRECIMIENTO ANUAL", ln=True)
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(59, 130, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(45, 8, "Año", 1, 0, "C", True)
    pdf.cell(45, 8, "Edad", 1, 0, "C", True)
    pdf.cell(95, 8, "Pensión Estimada Mensual", 1, 1, "C", True)
    
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    for i, row in df.iterrows():
        pdf.cell(45, 7, str(int(row['Año'])), 1, 0, "C")
        pdf.cell(45, 7, str(int(row['Edad'])), 1, 0, "C")
        pdf.cell(95, 7, f"${row['Pensión']:,.2f} MXN", 1, 1, "R")

    # 5. TÉRMINOS
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 8)
    pdf.cell(0, 4, "TÉRMINOS Y CONDICIONES:", ln=True)
    pdf.set_font("helvetica", "", 7)
    pdf.multi_cell(0, 3, "Cálculos informativos basados en la Ley 1973. Sujeto a cambios por el IMSS e inflación.")

    # 6. FIRMA Y NOMBRE CENTRADO
    # Colocamos la firma a la derecha pero centrando el texto abajo
    pdf.set_y(250)
    x_firma = 150 # Posición horizontal para el bloque de firma
    try:
        pdf.image("assets/firma.png", x_firma, 242, 40) # Imagen de la firma
    except:
        pdf.line(x_firma, 260, x_firma + 40, 260) 
    
    pdf.set_y(262)
    pdf.set_font("helvetica", "B", 10)
    pdf.set_x(x_firma - 10) # Ajuste para centrar el nombre respecto a la firma
    pdf.cell(60, 5, "Ing. Roberto Villarreal Glz", ln=True, align="C")
    
    pdf.set_font("helvetica", "", 8)
    pdf.set_x(x_firma - 10)
    pdf.cell(60, 4, "Especialista en Pensiones Ley 73", ln=True, align="C")
    
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
