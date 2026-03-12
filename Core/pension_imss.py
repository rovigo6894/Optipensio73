from Config.parametros import FACTORES_EDAD
from Config.tabla_ley73 import TABLA_LEY73
import math

UMA = 117.31


def buscar_tabla(veces_uma):

    # Si es mayor a 6 UMA, los porcentajes ya no cambian
    if veces_uma >= 6:
        return 13.0, 2.45

    # Si es menor a 6 UMA, se busca en la tabla
    for li, ls, cuantia, incremento in TABLA_LEY73:

        if li <= veces_uma <= ls:
            return cuantia, incremento

    return TABLA_LEY73[-1][2], TABLA_LEY73[-1][3]


def calcular_pension_ley73(
        salario_diario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa=False):

    # salario en UMA
    veces_uma = salario_diario / UMA

    cuantia_pct, incremento_pct = buscar_tabla(veces_uma)

    # ----------------------
    # CUANTIA BASICA
    # ----------------------

    cuantia_basica = salario_diario * (cuantia_pct / 100)

    # ----------------------
    # INCREMENTOS
    # ----------------------

    semanas_excedentes = max(semanas - 500, 0)

    años_excedentes = math.floor(semanas_excedentes / 52)

    incremento_anual = salario_diario * (incremento_pct / 100)

    incremento_total = incremento_anual * años_excedentes

    pension_diaria = cuantia_basica + incremento_total

    # ----------------------
    # FACTOR EDAD
    # ----------------------

    factor = FACTORES_EDAD.get(edad_retiro, 1)

    pension_diaria *= factor

    # ----------------------
    # ASIGNACION ESPOSA
    # ----------------------

    if esposa:
        pension_diaria *= 1.15

    pension_mensual = pension_diaria * 30

    # ----------------------
    # PROYECCION
    # ----------------------

    años = edad_retiro - edad_actual

    pension_futura = pension_mensual * ((1 + inflacion) ** años)

    return pension_mensual, pension_futura
