from Config.parametros import UMA_ACTUAL, CRECIMIENTO_UMA, FACTORES_EDAD
from Config.tablas_imss import TABLA_CUANTIA


def obtener_porcentaje_cuantia(salario_uma):

    for minimo, maximo, porcentaje in TABLA_CUANTIA:

        if salario_uma >= minimo and salario_uma < maximo:
            return porcentaje

    return 0.20


def calcular_pension_ley73(
    salario_diario,
    semanas_cotizadas,
    edad_actual,
    edad_retiro,
    inflacion_anual,
    esposa=False
):

    salario_uma = salario_diario / UMA_ACTUAL

    porcentaje_cuantia = obtener_porcentaje_cuantia(salario_uma)

    cuantia_basica = salario_diario * porcentaje_cuantia

    semanas_excedentes = max(semanas_cotizadas - 500, 0)

    incremento = (semanas_excedentes / 52) * 0.015

    pension_base = cuantia_basica * (1 + incremento)

    factor_edad = FACTORES_EDAD.get(edad_retiro, 1)

    pension = pension_base * factor_edad

    if esposa:
        pension *= 1.15

    pension_mensual = pension * 30

    años_para_retiro = edad_retiro - edad_actual

    pension_futura = pension_mensual * ((1 + inflacion_anual) ** años_para_retiro)

    return pension_mensual, pension_futura


def proyectar_pension_anual(
    pension_inicial,
    edad_actual,
    edad_retiro,
    inflacion
):

    proyeccion = []

    pension = pension_inicial

    for edad in range(edad_actual, edad_retiro + 1):

        proyeccion.append({
            "Edad": edad,
            "Pension_mensual": pension
        })

        pension = pension * (1 + inflacion)

    return proyeccion


def proyectar_uma(uma_actual, crecimiento, años):

    uma = uma_actual

    for i in range(años):

        uma = uma * (1 + crecimiento)

    return uma
