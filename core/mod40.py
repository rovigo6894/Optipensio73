"""
Módulo de cálculo de Modalidad 40
Basado en la Ley 73 del IMSS
"""

from core.calculadora_pension import calcular_pension_ley73

def calcular_mod40(edad, semanas, salario, salario_m40, meses_m40, edad_retiro=60, esposa=True):
    """
    Calcula el impacto de la Modalidad 40 en la pensión

    Parámetros:
    - edad: edad actual
    - semanas: semanas cotizadas a la fecha
    - salario: salario diario actual
    - salario_m40: salario diario a cotizar en M40
    - meses_m40: cantidad de meses en M40
    - edad_retiro: edad a la que se planea retirar
    - esposa: si tiene asignación por esposa

    Retorna:
    Diccionario con resultados
    """

    # Factores de costo por año (según IMSS)
    factores_costo = {
        1: 0.13347,  # 13.347% del salario
        2: 0.14438,  # 14.438% del salario
        3: 0.15529,  # 15.529% del salario
        4: 0.16622,  # 16.620% del salario
    }
    
    meses_por_año = 30.4  # Días promedio por mes para cálculo IMSS

    # --- 1. CÁLCULO DE LA INVERSIÓN ---
    inversion = 0
    meses_restantes = meses_m40

    for año in range(1, 5):
        if meses_restantes <= 0:
            break
        meses_en_año = min(12, meses_restantes)
        factor_año = factores_costo.get(año, 0.13347)
        inversion += salario_m40 * meses_en_año * meses_por_año * factor_año
        meses_restantes -= meses_en_año

    # --- 2. SEMANAS APORTADAS EN M40 ---
    semanas_m40 = (meses_m40 / 12) * 52

    # --- 3. NUEVO SALARIO PROMEDIO (últimas 250 semanas) ---
    if meses_m40 >= 6:
        # Si son más de 6 meses, afecta el promedio
        semanas_ponderadas = min(semanas_m40, 250)
        semanas_previas = 250 - semanas_ponderadas
        if semanas_previas > 0:
            nuevo_promedio = ((salario * semanas_previas) + (salario_m40 * semanas_ponderadas)) / 250
        else:
            nuevo_promedio = salario_m40
    else:
        # Menos de 6 meses no afecta el promedio
        nuevo_promedio = salario

    # --- 4. CALCULAR PENSIÓN BASE (sin M40) ---
    # Usamos inflación 0 porque queremos la base actual
    resultado_base = calcular_pension_ley73(salario, semanas, edad, edad_retiro, 0, esposa)
    pension_base = resultado_base[0]  # Primer valor del tuple

    # --- 5. CALCULAR NUEVA PENSIÓN CON M40 ---
    años_para_retiro = max(0, edad_retiro - edad)
    semanas_totales = semanas + (52 * años_para_retiro) + semanas_m40

    # Factores Ley 73
    PCT_CUANTIA = 0.13
    PCT_INCREMENTO = 0.0245
    PCT_ESPOSA = 0.15 if esposa else 0
    DECRETO_FOX = 0.11
    AJUSTE_FINAL = 1.2166

    from config.parametros import FACTORES_EDAD
    factor_edad = FACTORES_EDAD.get(edad_retiro, 0.75)

    # Cuantía básica
    cuantia_basica_anual = nuevo_promedio * PCT_CUANTIA * 365

    # Incremento por semanas extra
    años_despues_500 = max(0, (semanas_totales - 500) / 52)
    incremento_anual = nuevo_promedio * PCT_INCREMENTO * 365 * años_despues_500

    # Total
    total_anual = cuantia_basica_anual + incremento_anual

    # Asignación por esposa
    if esposa:
        total_anual *= (1 + PCT_ESPOSA)

    # Decreto Fox
    total_anual *= (1 + DECRETO_FOX)

    # Ajuste final
    total_anual *= AJUSTE_FINAL

    # Aplicar factor por edad
    pension_anual = total_anual * factor_edad
    pension_mensual = pension_anual / 12

    # --- 6. CÁLCULO DE MÉTRICAS ---
    incremento_mensual = pension_mensual - pension_base
    recuperacion_meses = inversion / incremento_mensual if incremento_mensual > 0 else 0
    utilidad_20 = (incremento_mensual * 12 * 20) - inversion
    roi = ((incremento_mensual * 12 * 20) / inversion * 100) if inversion > 0 else 0

    return {
        'base': round(pension_base, 2),
        'con_m40': round(pension_mensual, 2),
        'incremento': round(incremento_mensual, 2),
        'inversion': round(inversion, 2),
        'recuperacion': round(recuperacion_meses, 1),
        'utilidad_20': round(utilidad_20, 2),
        'roi': round(roi, 0)
    }
