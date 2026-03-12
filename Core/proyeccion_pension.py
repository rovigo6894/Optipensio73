def proyectar_pension(pension_inicial, inflacion, años):

    proyeccion = []

    pension = pension_inicial

    for i in range(años + 1):

        proyeccion.append(pension)

        pension = pension * (1 + inflacion)

    return proyeccion