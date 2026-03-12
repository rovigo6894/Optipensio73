import pandas as pd


def calcular_promedio_250(semanas_salario):

    if len(semanas_salario) < 250:
        raise ValueError("Se requieren al menos 250 semanas")

    ultimas = semanas_salario[-250:]

    promedio = sum(ultimas) / len(ultimas)

    return promedio