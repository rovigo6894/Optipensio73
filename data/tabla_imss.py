# data/tabla_imss.py

def buscar_porcentaje(veces_uma):
    """
    Determina los porcentajes de cuantía básica e incremento anual 
    según el grupo de salario expresado en veces la UMA.
    Basado en el Art. 167 de la Ley del Seguro Social de 1973.
    """
    
    # Tabla oficial de cuantías e incrementos
    if veces_uma <= 1.0:
        return 0.80, 0.00563
    elif veces_uma <= 1.25:
        return 0.7711, 0.00814
    elif veces_uma <= 1.50:
        return 0.5818, 0.01178
    elif veces_uma <= 1.75:
        return 0.4923, 0.01430
    elif veces_uma <= 2.0:
        return 0.4267, 0.01615
    elif veces_uma <= 2.25:
        return 0.3765, 0.01756
    elif veces_uma <= 2.50:
        return 0.3368, 0.01868
    elif veces_uma <= 2.75:
        return 0.3048, 0.01958
    elif veces_uma <= 3.0:
        return 0.2783, 0.02033
    elif veces_uma <= 3.25:
        return 0.2560, 0.02096
    elif veces_uma <= 3.50:
        return 0.2370, 0.02149
    elif veces_uma <= 3.75:
        return 0.2207, 0.02195
    elif veces_uma <= 4.0:
        return 0.2065, 0.02235
    elif veces_uma <= 4.25:
        return 0.1939, 0.02271
    elif veces_uma <= 4.50:
        return 0.1829, 0.02302
    elif veces_uma <= 4.75:
        return 0.1730, 0.02330
    elif veces_uma <= 5.0:
        return 0.1641, 0.02355
    elif veces_uma <= 5.25:
        return 0.1561, 0.02377
    elif veces_uma <= 5.50:
        return 0.1488, 0.02398
    elif veces_uma <= 5.75:
        return 0.1422, 0.02416
    elif veces_uma <= 6.0:
        return 0.1362, 0.02434
    else:
        # Para salarios mayores a 6.01 veces la UMA
        return 0.13, 0.0245
