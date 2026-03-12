from Config.parametros import FACTORES_EDAD
from Config.tabla_ley73 import TABLA_LEY73
from Config.uma_historica import obtener_uma
import math
import datetime

FACTOR_FOX = 1.11


def buscar_tabla(veces_uma):

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

    anio_actual = datetime.datetime.now().year

    UMA = obtener_uma(anio_actual)

    veces_uma = salario_diario / UMA

    cuantia_pct, incremento_pct = buscar_tabla(veces_uma)

    # -------------------------
    # CUANTIA BASICA
    # -------------------------

    cuantia_basica = salario_diario * (cuantia_pct / 100)

    # -------------------------
    # INCREMENTOS POR SEMANAS
    # -------------------------

    semanas_excedentes = max(semanas - 500, 0)

    incrementos = math.floor(semanas_excedentes / 52)

    incremento_total = cuantia_basica * (incremento_pct / 100) * incrementos

    pension_diaria = cuantia_basica + incremento_total

    # -------------------------
    # FACTOR FOX
    # -------------------------

    pension_diaria *= FACTOR_FOX

    # -------------------------
    # FACTOR EDAD
    # -------------------------

    factor = FACTORES_EDAD.get(edad_retiro, 1)

    pension_diaria *= factor

    # -------------------------
    # ASIGNACION ESPOSA
    # -------------------------

    if esposa:
        pension_diaria *= 1.15

    # -------------------------
    # MENSUAL
    # -------------------------

    pension_mensual = pension_diaria * 30

    # -------------------------
    # PROYECCION
    # -------------------------

    años = edad_retiro - edad_actual

    pension_futura = pension_mensual * ((1 + inflacion) ** años)

    return pension_mensual, pension_futura
