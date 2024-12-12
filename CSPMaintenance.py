import sys
from constraint import Problem
import time
import csv

# Función para leer los datos desde un archivo
def leer_datos_archivo(ruta):
    with open(ruta, 'r') as archivo:
        lineas = archivo.read().strip().split('\n')

    franjas_horarias = int(lineas[0])
    tamanio_matriz = tuple(map(int, lineas[1].split('x')))

    talleres_std = [tuple(map(int, pos.strip('()').split(','))) for pos in lineas[2].split()]
    talleres_spc = [tuple(map(int, pos.strip('()').split(','))) for pos in lineas[3].split()]
    parkings = [tuple(map(int, pos.strip('()').split(','))) for pos in lineas[4].split()]

    aviones = []
    for avion in lineas[5:]:
        partes = avion.split('-')
        aviones.append({
            "ID": int(partes[0]),
            "TIPO": partes[1],
            "RESTR": partes[2] == 'T',
            "T1": int(partes[3]),
            "T2": int(partes[4])
        })

    return franjas_horarias, tamanio_matriz, talleres_std, talleres_spc, parkings, aviones

# Función para escribir las soluciones en un archivo CSV
def escribir_soluciones_csv(ruta, soluciones, aviones, franjas_horarias, talleres_std, talleres_spc, parkings):
    with open(ruta, 'w', newline='') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow([f"N. Sol: {len(soluciones)}"])

        for idx, solucion in enumerate(soluciones[:5], start=1):
            escritor.writerow([f"Solución {idx}:"])
            for avion in aviones:
                asignaciones = []
                for franja in range(franjas_horarias):
                    pos = solucion[f"Avion{avion['ID']}_Franja{franja}"]
                    # Determinar el tipo de posición (STD, SPC o PRK)
                    if pos in talleres_std:
                        tipo = "STD"
                    elif pos in talleres_spc:
                        tipo = "SPC"
                    elif pos in parkings:
                        tipo = "PRK"
                    else:
                        tipo = "UNK"  # Por si hay un error en los datos
                    asignaciones.append(f"{tipo}{pos}")

                escritor.writerow([
                    f"{avion['ID']}-{avion['TIPO']}-{avion['RESTR']}-{avion['T1']}-{avion['T2']}: " + ", ".join(asignaciones)
                ])

# Función principal
def resolver_problema(ruta_entrada):
    start_time = time.time()
    franjas_horarias, tamanio_matriz, talleres_std, talleres_spc, parkings, aviones = leer_datos_archivo(ruta_entrada)

    print("Iniciando el modelo...")

    # Crear el problema
    problem = Problem()

    # Generar variables y dominios
    for avion in aviones:
        for franja in range(franjas_horarias):
            variable = f"Avion{avion['ID']}_Franja{franja}"

            # Dominios iniciales según las restricciones de talleres
            dominios = []
            for pos in parkings + talleres_std + talleres_spc:
                if pos in parkings or \
                   (pos in talleres_std and avion['TIPO'] == 'STD') or \
                   (pos in talleres_spc and avion['RESTR']):
                    dominios.append(pos)

            problem.addVariable(variable, dominios)

    print("Variables y dominios generados.")

    # Restricción 2: Capacidad de talleres
    for pos in talleres_std + talleres_spc:
        for franja in range(franjas_horarias):
            taller_vars = [
                f"Avion{avion['ID']}_Franja{franja}"
                for avion in aviones
            ]

            def max_dos_aviones(*args, taller=pos):
                return len([v for v in args if v == taller]) <= 2

            problem.addConstraint(max_dos_aviones, taller_vars)

    print("Restricción de capacidad añadida.")

    # Restricción 3 y 4: Talleres especialistas y orden de tareas
    for avion in aviones:
        if avion["RESTR"]:
            for franja in range(avion["T2"], franjas_horarias):
                variable = f"Avion{avion['ID']}_Franja{franja}"

                def especialista(pos):
                    return pos in talleres_spc

                problem.addConstraint(especialista, [variable])

    print("Restricción de talleres especialistas añadida.")

    # Restricción adicional 1: Evitar colisiones adyacentes
    for franja in range(franjas_horarias):
        for avion in aviones:
            var = f"Avion{avion['ID']}_Franja{franja}"
            for other_avion in aviones:
                if avion["ID"] != other_avion["ID"]:
                    other_var = f"Avion{other_avion['ID']}_Franja{franja}"

                    def no_adyacentes(a, b):
                        return abs(a[0] - b[0]) + abs(a[1] - b[1]) > 1

                    problem.addConstraint(no_adyacentes, (var, other_var))

    print("Restricción de colisiones adyacentes añadida.")

    # Restricción adicional 2: No más de un JUMBO por taller
    for pos in talleres_std + talleres_spc:
        for franja in range(franjas_horarias):
            jumbo_vars = [
                f"Avion{avion['ID']}_Franja{franja}"
                for avion in aviones if avion["TIPO"] == "JMB"
            ]

            def max_un_jumbo(*args, taller=pos):
                return len([v for v in args if v == taller]) <= 1

            problem.addConstraint(max_un_jumbo, jumbo_vars)

    print("Restricción de aviones JUMBO añadida.")

    # Resolver el problema
    print("Resolviendo...")
    soluciones = problem.getSolutions()

    # Guardar soluciones en un archivo CSV
    ruta_salida = ruta_entrada.replace('.txt', '.csv')
    escribir_soluciones_csv(ruta_salida, soluciones, aviones, franjas_horarias, talleres_std, talleres_spc, parkings)

    print(f"Tiempo total de ejecución: {time.time() - start_time:.2f} segundos")
    print(f"Se encontraron {len(soluciones)} soluciones. Soluciones guardadas en {ruta_salida}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <path maintenance>")
    else:
        resolver_problema(sys.argv[1])