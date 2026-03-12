UMA_HISTORICA = {
    2020: 86.88,
    2021: 89.62,
    2022: 96.22,
    2023: 103.74,
    2024: 108.57,
    2025: 113.14,
    2026: 117.31
}


def obtener_uma(anio):
    return UMA_HISTORICA.get(anio, UMA_HISTORICA[max(UMA_HISTORICA.keys())])