from Config.parametros import UMA_ACTUAL, FACTORES_EDAD
from Config.tabla_ley73 import TABLA_LEY73
import math

FACTOR_FOX = 1.11


def buscar_tabla(salario_uma):

    for li, ls, cuantia, incremento in TABLA_LEY73:

        if salario_uma >= li and salario_uma <= ls:
            return cuantia, incremento

    return 13.00, 2.450


def calcular_pension_ley73(
        salario_diario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa=False):

    salario_uma = salario_diario / UMA_ACTUAL

    cuantia_pct, incremento_pct = buscar_tabla(salario_uma)

    cuantia_basica = salario_diario * (cuantia_pct / 100)

    semanas_excedentes = max(semanas - 500, 0)

    incrementos = math.floor(semanas_excedentes / 52)

    aumento = salario_diario * (incremento_pct / 100) * incrementos

    pension_diaria = cuantia_basica + aumento

    # 🔵 Factor Fox
    pension_diaria *= FACTOR_FOX

    # factor edad
    factor = FACTORES_EDAD.get(edad_retiro, 1)

    pension_diaria *= factor

    # asignación esposa
    if esposa:
        pension_diaria *= 1.15

    pension_mensual = pension_diaria * 30

    años = edad_retiro - edad_actual

    pension_futura = pension_mensual * ((1 + inflacion) ** años)

    return pension_mensual, pension_futura
