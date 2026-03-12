from Config.parametros import FACTORES_EDAD
import math

UMA = 108.54


def calcular_pension_ley73(
        salario_diario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa=False):

    # salario en UMA
    veces_uma = salario_diario / UMA

    # porcentajes para >6 UMA
    cuantia_pct = 0.13
    incremento_pct = 0.0245

    # cuantía básica diaria
    cuantia_diaria = salario_diario * cuantia_pct

    # años excedentes
    años_excedentes = (semanas - 500) / 52

    # cuantía anual
    cuantia_anual = cuantia_diaria * 365

    # incremento anual
    incremento_anual = salario_diario * incremento_pct * 365

    # incremento total
    incremento_total = incremento_anual * años_excedentes

    total = cuantia_anual + incremento_total

    # asignación esposa
    if esposa:
        total *= 1.15

    # factor fox
    total *= 1.11

    # factor edad
    factor = FACTORES_EDAD.get(edad_retiro, 1)

    total *= factor

    pension_mensual = total / 12

    # proyección inflación
    años = edad_retiro - edad_actual

    pension_futura = pension_mensual * ((1 + inflacion) ** años)

    return pension_mensual, pension_futura
