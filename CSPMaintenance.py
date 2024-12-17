import sys
import time
from constraint import Problem
from collections import defaultdict
import re

class CSPMaintenance:
    def __init__(self, archivo_entrada):
        self.archivo_entrada = archivo_entrada
        self.archivo_salida = archivo_entrada.replace(".txt", ".csv")
        self.gestion = GestionDeArchivos()

    def cargar_datos(self):
        try:
            print("Cargando datos...")
            self.franjas, self.tamano, self.talleres_std, self.talleres_spc, self.parkings, self.aviones = self.gestion.cargar_datos_archivo(self.archivo_entrada)
        except Exception as e:
            raise ValueError(f"Error al cargar los datos del archivo: {e}")

    def configurar_problema(self):
        self.problem = configuracion_problema(self.franjas, self.tamano, self.talleres_std, self.talleres_spc, self.parkings, self.aviones)

    def resolver_problema(self):
        start_time = time.time()
        self.solutions = self.problem.getSolutions()
        end_time = time.time()
        self.final_time = end_time - start_time

    def guardar_resultados(self):
        print("Guardando resultados...")
        self.gestion.guardar_resultados(self.archivo_salida, self.solutions, self.aviones, self.franjas, self.talleres_spc, self.talleres_std)

    def ejecutar(self):
        self.cargar_datos()
        print(f"Franjas: {self.franjas} \nTamaño de la matriz: {self.tamano} \nTalleres STD: {self.talleres_std} "
              f"\nTalleres SPC: {self.talleres_spc} \nParkings: {self.parkings} \nAviones: {self.aviones}")
        self.configurar_problema()
        self.resolver_problema()
        print(f"Tiempo: {self.final_time:.2f} segundos \nNúmero de soluciones encontradas: {len(self.solutions)}")
        self.guardar_resultados()
        print("Proceso finalizado.")

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

            for i, solucion in enumerate(soluciones[:50]):
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

    # Creamos el problema
    problema = Problem()

    dominio = talleres_estandar + talleres_especiales + parkings

    # Variables
    for avion in aviones:
        for franja in range(num_franjas):
            problema.addVariable(f"{avion['ID']}-{franja}", dominio)

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
        # Agrupar elementos de las listas usando comprensión de listas
        resultado_lista = [(aviones[i], asignaciones[i]) for i in range(min(len(aviones), len(asignaciones)))]
        for avion, posicion in resultado_lista:
            if avion["TIPO"] == "JMB":
                conteo_jumbo[posicion] += 1
                if conteo_jumbo[posicion] > 1:
                    return False
        return True

    for franja in range(num_franjas):
        variables_franja = [f"{avion['ID']}-{franja}" for avion in aviones]
        problema.addConstraint(restriccion_max_2_aviones, variables_franja)
        problema.addConstraint(restriccion_max_1_jumbo, variables_franja)

    # Restricción: Completar tareas en talleres válidos con orden si aplica
    def restriccion_tareas(*asignaciones):
        for avion in aviones:
            talleres_spc_cont = 0
            talleres_cont = 0
            tareas_restantes = {"T1": avion["T1"], "T2": avion["T2"]}

            for franja in range(num_franjas):
                posicion = asignaciones[aviones.index(avion) * num_franjas + franja]
                if posicion in talleres_especiales:
                    talleres_spc_cont += 1
                    talleres_cont += 1
                    if tareas_restantes["T2"] > 0:
                        tareas_restantes["T2"] -= 1
                    elif avion["RESTR"] == "T" and tareas_restantes["T2"] == 0 and tareas_restantes["T1"] > 0:
                        tareas_restantes["T1"] -= 1
                elif posicion in talleres_estandar:
                    talleres_cont += 1
                    if tareas_restantes["T2"] > 0 and avion["RESTR"] == "T":
                        return False
                    if tareas_restantes["T1"] > 0:
                        tareas_restantes["T1"] -= 1

            # Verrificar que las Tareas de tipo 2 se realizaron en talleres especiales
            if talleres_spc_cont < avion["T2"]:
                return False

            # Verificar que las Tareas de tipo 1 se realizaron en talleres especiales o estandar
            if talleres_cont < avion["T1"] + avion["T2"]:
                return False

        return True

    # Añadir restricciones
    problema.addConstraint(restriccion_tareas, [f"{avion['ID']}-{franja}" for avion in aviones for franja in range(num_franjas)])

    # Restricción: Asegurar adyacencia libre
    def restriccion_adyacencia(*asignaciones):
        ocupados = set()
        for asignacion in asignaciones:
            ocupados.add(asignacion)
        for posicion in ocupados:
            if posicion in parkings + talleres_estandar + talleres_especiales:
                x, y = posicion
                adyacentes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if all(adj in ocupados for adj in adyacentes if adj in dominio):
                    return False
        return True

    for franja in range(num_franjas):
        variables_franja = [f"{avion['ID']}-{franja}" for avion in aviones]
        problema.addConstraint(restriccion_adyacencia, variables_franja)

    # Restricción: Evitar aviones JUMBO adyacentes
    def restriccion_jumbos_no_adyacentes(*asignaciones):
        # Agrupar elementos de las listas usando comprensión de listas
        resultado_lista = [(aviones[i], asignaciones[i]) for i in range(min(len(aviones), len(asignaciones)))]
        posiciones_jumbos = [pos for avion, pos in resultado_lista if avion["TIPO"] == "JMB"]
        for pos in posiciones_jumbos:
            x, y = pos
            adyacentes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if any(adj in posiciones_jumbos for adj in adyacentes if adj in dominio):
                return False
        return True

    for franja in range(num_franjas):
        variables_franja = [f"{avion['ID']}-{franja}" for avion in aviones]
        problema.addConstraint(restriccion_jumbos_no_adyacentes, variables_franja)

    return problema


def main():
    if len(sys.argv) != 2:
        raise ValueError("Formato valido: python CSPMaintenance.py <path maintenance>")

    archivo_entrada = sys.argv[1]
    csp_maintenance = CSPMaintenance(archivo_entrada)
    csp_maintenance.ejecutar()

if __name__ == "__main__":
    main()