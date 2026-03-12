import pandas as pd

# Tabla oficial simplificada de cuantías Ley 73
# columnas:
# limite_inferior, limite_superior, cuantia_basica, incremento_anual

tabla_imss = pd.DataFrame([
    [0.00, 1.00, 80.00, 0.563],
    [1.01, 1.25, 77.11, 0.814],
    [1.26, 1.50, 58.18, 1.178],
    [1.51, 1.75, 49.19, 1.430],
    [1.76, 2.00, 42.67, 1.615],
    [2.01, 2.25, 37.65, 1.756],
    [2.26, 2.50, 33.68, 1.866],
    [2.51, 2.75, 30.48, 1.955],
    [2.76, 3.00, 27.83, 2.031],
    [3.01, 3.25, 25.60, 2.095],
    [3.26, 3.50, 23.70, 2.151],
    [3.51, 3.75, 22.07, 2.200],
    [3.76, 4.00, 20.65, 2.243],
    [4.01, 4.25, 19.39, 2.281],
    [4.26, 4.50, 18.27, 2.315],
    [4.51, 4.75, 17.27, 2.345],
    [4.76, 5.00, 16.37, 2.372],
    [5.01, 5.25, 15.55, 2.396],
    [5.26, 5.50, 14.80, 2.418],
    [5.51, 5.75, 14.12, 2.438],
    [5.76, 6.00, 13.49, 2.457],
    [6.01, 999, 13.00, 2.450]  # tu rango actual
],
columns=[
    "limite_inferior",
    "limite_superior",
    "cuantia_basica",
    "incremento_anual"
])


def buscar_porcentaje(veces_uma):

    fila = tabla_imss[
        (tabla_imss.limite_inferior <= veces_uma) &
        (tabla_imss.limite_superior >= veces_uma)
    ]

    if fila.empty:
        raise ValueError("Salario fuera de rango")

    cuantia = fila.iloc[0]["cuantia_basica"] / 100
    incremento = fila.iloc[0]["incremento_anual"] / 100

    return cuantia, incremento