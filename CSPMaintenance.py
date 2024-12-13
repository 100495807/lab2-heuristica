import sys
import time
from constraint import Problem
from collections import defaultdict
import re

class GestionDeArchivos:
    def __init__(self):
        pass

    # Función para extraer las posiciones de los talleres
    def extraer_posiciones(self, cadena):
        posiciones_str = cadena.split(":")[1].strip()
        posiciones = [tuple(map(int, re.findall(r'\d+', pos))) for pos in posiciones_str.split()]
        return posiciones

    # Función para extraer los datos de un avión
    def extraer_avion(self, cadena):
        partes = cadena.strip().split("-")
        return {
            "ID": partes[0],
            "TIPO": partes[1],
            "RESTR": partes[2],
            "T1": int(partes[3]),
            "T2": int(partes[4])
        }

    # Función para cargar los datos del archivo
    def cargar_datos_archivo(self, ruta_archivo):
        with open(ruta_archivo, "r") as archivo:
            lineas = archivo.readlines()

        num_franjas = int(lineas[0].split(":")[1].strip())
        dimensiones = tuple(map(int, lineas[1].strip().split("x")))

        talleres_estandar = self.extraer_posiciones(lineas[2])
        talleres_especiales = self.extraer_posiciones(lineas[3])
        estacionamientos = self.extraer_posiciones(lineas[4])

        lista_aviones = [self.extraer_avion(linea) for linea in lineas[5:]]

        return num_franjas, dimensiones, talleres_estandar, talleres_especiales, estacionamientos, lista_aviones

    # Guardar resultados
    def guardar_resultados(self, ruta_salida, soluciones, aviones, franjas, talleres_especiales, talleres_estandar):
        with open(ruta_salida, 'w') as archivo:
            archivo.write(f"N. Sol: {len(soluciones)}\n")
            if not soluciones:
                archivo.write("No se encontraron soluciones válidas.\n")
                print("No se encontraron soluciones válidas.")
                return

            for i, solucion in enumerate(soluciones):
                archivo.write(f"Solucion {i + 1}:\n")
                for avion in aviones:
                    archivo.write(f"{avion['ID']}-{avion['TIPO']}-{avion['RESTR']}-{avion['T1']}-{avion['T2']}: ")
                    for franja in range(franjas):
                        posicion = solucion[f"{avion['ID']}-{franja}"]
                        if posicion in talleres_especiales:
                            tipo_taller = "SPC"
                        elif posicion in talleres_estandar:
                            tipo_taller = "STD"
                        else:
                            tipo_taller = "PRK"
                        archivo.write(f"{tipo_taller}{posicion} ")
                    archivo.write("\n")


# configuración del problema
def configuracion_problema(num_franjas, tamano, talleres_estandar, talleres_especiales, parkings, aviones):
    problem = Problem()

    dominio = talleres_estandar + talleres_especiales + parkings

    # Variables
    for avion in aviones:
        for franja in range(num_franjas):
            problem.addVariable(f"{avion['ID']}-{franja}", dominio)

    # Restricción: Máximo 2 aviones por taller
    def restriccion_max_2_aviones(*asignaciones):
        conteo_talleres = defaultdict(int)
        for posicion in asignaciones:
            conteo_talleres[posicion] += 1
            if conteo_talleres[posicion] > 2:
                return False
        return True

    # Restricción: Máximo 1 JUMBO por taller
    def restriccion_max_1_jumbo(*asignaciones):
        conteo_jumbo = defaultdict(int)
        for avion, posicion in zip(aviones, asignaciones):
            if avion["TIPO"] == "JMB":
                conteo_jumbo[posicion] += 1
                if conteo_jumbo[posicion] > 1:
                    return False
        return True

    # Restricción: Completar tareas en talleres válidos con orden si aplica
    def restriccion_tareas(*asignaciones):
        for avion in aviones:
            tareas_restantes = {"T1": avion["T1"], "T2": avion["T2"]}
            talleres_spc_count = 0
            talleres_count = 0

            for franja in range(num_franjas):
                posicion = asignaciones[aviones.index(avion) * num_franjas + franja]
                if posicion in talleres_especiales:
                    talleres_spc_count += 1
                    talleres_count += 1
                    if tareas_restantes["T2"] > 0:
                        tareas_restantes["T2"] -= 1
                    elif avion["RESTR"] == "T" and tareas_restantes["T2"] == 0 and tareas_restantes["T1"] > 0:
                        tareas_restantes["T1"] -= 1
                elif posicion in talleres_estandar:
                    talleres_count += 1
                    if tareas_restantes["T2"] > 0 and avion["RESTR"] == "T":
                        return False
                    if tareas_restantes["T1"] > 0:
                        tareas_restantes["T1"] -= 1

            # Validar que las tareas tipo 2 se realizaron en talleres especializados
            if talleres_spc_count < avion["T2"]:
                return False

            # Validar que las tareas tipo 1 se realizaron en talleres válidos
            if talleres_count < avion["T1"] + avion["T2"]:
                return False

        return True

    # Restricción: Asegurar adyacencia libre
    def restriccion_adyacencia(*asignaciones):
        ocupados = set(asignaciones)
        for posicion in ocupados:
            if posicion in parkings + talleres_estandar + talleres_especiales:
                x, y = posicion
                adyacentes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if all(adj in ocupados for adj in adyacentes if adj in dominio):
                    return False
        return True

    # Restricción: Evitar aviones JUMBO adyacentes
    def restriccion_jumbos_no_adyacentes(*asignaciones):
        posiciones_jumbos = [pos for avion, pos in zip(aviones, asignaciones) if avion["TIPO"] == "JMB"]
        for pos in posiciones_jumbos:
            x, y = pos
            adyacentes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if any(adj in posiciones_jumbos for adj in adyacentes if adj in dominio):
                return False
        return True

    for franja in range(num_franjas):
        variables_franja = [f"{avion['ID']}-{franja}" for avion in aviones]
        problem.addConstraint(restriccion_max_2_aviones, variables_franja)
        problem.addConstraint(restriccion_max_1_jumbo, variables_franja)
        problem.addConstraint(restriccion_adyacencia, variables_franja)
        problem.addConstraint(restriccion_jumbos_no_adyacentes, variables_franja)

    # Añadir restricciones
    problem.addConstraint(restriccion_tareas, [f"{avion['ID']}-{franja}" for avion in aviones for franja in range(num_franjas)])

    return problem

# Main function
def main():
    if len(sys.argv) != 2:
        raise ValueError("Formato valido: python CSPMaintenance.py <path maintenance>")

    archivo_entrada = sys.argv[1]
    archivo_salida = archivo_entrada.replace(".txt", ".csv")

    # Instanciar la clase
    gestion = GestionDeArchivos()

    # Cargar datos del archivo
    franjas, tamano, talleres_std, talleres_spc, parkings, aviones = gestion.cargar_datos_archivo(archivo_entrada)

    # Imprimir datos
    print(f"Franjas: {franjas} \nTamaño de la matriz: {tamano} \nTalleres STD: {talleres_std} "
          f"\nTalleres SPC: {talleres_spc} \nParkings: {parkings} \nAviones: {aviones}")

    # Configurar el problema
    problem = configuracion_problema(franjas, tamano, talleres_std, talleres_spc, parkings, aviones)

    # Resolver el problema
    start_time = time.time()
    solutions = problem.getSolutions()
    end_time = time.time()
    final_time = end_time - start_time

    print(f"Tiempo: {final_time:.2f} segundos \nNúmero de soluciones encontradas: {len(solutions)}")

    gestion.guardar_resultados(archivo_salida, solutions, aviones, franjas, talleres_spc, talleres_std)

if __name__ == "__main__":
    main()