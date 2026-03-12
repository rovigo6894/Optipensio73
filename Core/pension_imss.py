from Config.parametros import *

def calcular_pension_base(
    salario_promedio,
    semanas,
    edad_retiro,
    esposa=True
):

    factor_edad = FACTOR_EDAD.get(edad_retiro, 0.75)

    # Cuantía básica
    cuantia_basica = salario_promedio * CUANTIA_BASICA * DIAS_POR_ANIO

    # Incrementos por semanas adicionales
    anios_extra = max(0, (semanas - 500) / SEMANAS_POR_ANIO)

    incremento = salario_promedio * INCREMENTO_ANUAL * DIAS_POR_ANIO * anios_extra

    pension_anual = cuantia_basica + incremento

    # Asignación por esposa
    if esposa:
        pension_anual *= (1 + ASIGNACION_ESPOSA)

    # Decreto Fox
    pension_anual *= (1 + DECRETO_FOX)

    # Ajuste por edad
    pension_anual *= factor_edad

    pension_mensual = pension_anual / MESES_POR_ANIO

    return round(pension_mensual, 2)
