from Config.parametros import UMA_ACTUAL, FACTORES_EDAD
from Config.tabla_ley73 import TABLA_LEY73
import math


def buscar_tabla(salario_uma):

    for li, ls, cuantia, incremento in TABLA_LEY73:
        if salario_uma >= li and salario_uma <= ls:
            return cuantia, incremento

    return 13.00, 2.450


def calcular_pension_ley73(
    salario_diario,
    semanas,
    edad_retiro,
    esposa=False
):

    salario_uma = salario_diario / UMA_ACTUAL

    cuantia_pct, incremento_pct = buscar_tabla(salario_uma)

    cuantia_basica = salario_diario * (cuantia_pct / 100)

    semanas_excedentes = max(semanas - 500,0)

    incrementos = math.floor(semanas_excedentes / 52)

    aumento = salario_diario * (incremento_pct / 100) * incrementos

    pension_diaria = cuantia_basica + aumento

    factor_edad = FACTORES_EDAD.get(edad_retiro,1)

    pension_diaria *= factor_edad

    if esposa:
        pension_diaria *= 1.15

    pension_mensual = pension_diaria * 30

    return pension_mensual
