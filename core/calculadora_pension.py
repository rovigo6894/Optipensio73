from data.tabla_imss import buscar_porcentaje
from config.parametros import FACTORES_EDAD

UMA = 108.54


def calcular_pension_ley73(
        salario_diario,
        semanas,
        edad_actual,
        edad_retiro,
        inflacion,
        esposa=False
):

    # convertir inflación de porcentaje a decimal
    inflacion = inflacion / 100

    # salario en UMAs
    veces_uma = salario_diario / UMA

    cuantia_pct, incremento_pct = buscar_porcentaje(veces_uma)

    # cuantía básica diaria
    cuantia_diaria = salario_diario * cuantia_pct

    # cuantía anual
    cuantia_anual = cuantia_diaria * 365

    # años excedentes
    anos_excedentes = (semanas - 500) / 52

    # incremento anual
    incremento_anual = salario_diario * incremento_pct * 365

    # incremento total
    incremento_total = incremento_anual * anos_excedentes

    # total antes de factores
    total = cuantia_anual + incremento_total

    # asignación esposa
    if esposa:
        total = total * 1.15

    # factor fox
    total = total * 1.11

    # factor edad
    factor = FACTORES_EDAD.get(edad_retiro, 1)

    total = total * factor

    # pensión mensual actual
    pension_mensual = total / 12

    # proyección año por año (ajuste IMSS febrero)
    anos = edad_retiro - edad_actual

    pension_futura = pension_mensual

    for i in range(anos):
        pension_futura = pension_futura * (1 + inflacion)

    return pension_mensual, pension_futura
