import sys
import time
from constraint import Problem
from collections import defaultdict
import re


class MaintenanceScheduler:
    def __init__(self, input_file_path):
        self.input_file_path = input_file_path
        self.output_file_path = input_file_path.replace(".txt", ".csv")
        self.file_manager = FileManager()

    # Cargamos los datos del archivo
    def load_data(self):
        '''
        Metodo para cargar los datos del archivo .txt
        '''
        try:
            print("Cargando datos...")
            self.time_slots, self.matrix_size, self.standard_workshops, self.special_workshops, self.parking_spots, self.aircrafts = self.file_manager.load_file_data(
                self.input_file_path)
        except Exception as e:
            raise ValueError(f"Error al cargar los datos del archivo: {e}")

    # Configuramos el problema CSP
    def setup_problem(self):
        '''
        Metodo para configurar el problema CSP
        '''
        self.problem = setup_problem(self.time_slots, self.matrix_size, self.standard_workshops, self.special_workshops,
                                     self.parking_spots, self.aircrafts)

    # Resolvemos el problema CSP
    def solve_problem(self):
        '''
        Metodo para resolver el problema CSP
        '''
        start_time = time.time()
        self.solutions = self.problem.getSolutions()
        end_time = time.time()
        self.execution_time = end_time - start_time

    # Guardamos los resultados en un archivo
    def save_results(self):
        '''
        Metodo para guardar los resultados en un archivo .csv
        '''
        print("Guardando resultados...")
        self.file_manager.save_results(self.output_file_path, self.solutions, self.aircrafts, self.time_slots,
                                       self.special_workshops, self.standard_workshops)

    # Ejecutamos el proceso
    def execute(self):
        '''
        Metodo para ejecutar el proceso
        '''
        self.load_data()
        print(
            f"Franjas: {self.time_slots} \nTamaño matriz: {self.matrix_size} \nTalleres estandar (STD): {self.standard_workshops} "
            f"\nTalleres especiales (SPC): {self.special_workshops} \nParkings (PRK): {self.parking_spots} \nAviones: {self.aircrafts}")
        self.setup_problem()
        self.solve_problem()
        print(f"Tiempo de ejecucion: {self.execution_time:.10f} segundos \nNumero de soluciones encontradas: {len(self.solutions)}")
        self.save_results()
        print("Proceso completado.")


class FileManager:
    def __init__(self):
        pass

    def extract_positions(self, line):
        '''
        Metodo para extraer las posiciones de los talleres
        '''
        positions_str = line.split(":")[1].strip()
        positions = [tuple(map(int, re.findall(r'\d+', pos))) for pos in positions_str.split()]
        return positions


    def extract_aircraft(self, line):
        '''
        Metodo para extraer los datos de los aviones
        '''
        parts = line.strip().split("-")
        return {
            "ID": parts[0],
            "TIPO": parts[1],
            "RESTR": parts[2],
            "T1": int(parts[3]),
            "T2": int(parts[4])
        }


    def load_file_data(self, file_path):
        '''
        Metodo para cargar los datos del archivo .txt
        '''
        with open(file_path, "r") as file:
            lines = file.readlines()

        num_time_slots = int(lines[0].split(":")[1].strip())
        matrix_dimensions = tuple(map(int, lines[1].strip().split("x")))

        standard_workshops = self.extract_positions(lines[2])
        special_workshops = self.extract_positions(lines[3])
        parking_spots = self.extract_positions(lines[4])

        aircrafts = [self.extract_aircraft(line) for line in lines[5:]]

        return num_time_slots, matrix_dimensions, standard_workshops, special_workshops, parking_spots, aircrafts


    def save_results(self, output_file_path, solutions, aircrafts, time_slots, special_workshops, standard_workshops):
        '''
        Metodo para guardar los resultados en un archivo .csv
        '''
        with open(output_file_path, 'w') as file:
            file.write(f"N. Sol: {len(solutions)}\n")
            if not solutions:
                file.write("No se encontraron soluciones válidas.\n")
                print("No se encontro ninguna solucion valida.")
                return

            i = 1
            for solution in solutions[:50]:
                file.write(f"Solucion {i}:\n")
                for aircraft in aircrafts:
                    file.write(
                        f"{aircraft['ID']}-{aircraft['TIPO']}-{aircraft['RESTR']}-{aircraft['T1']}-{aircraft['T2']}: ")
                    for time_slot in range(time_slots):
                        position = solution[f"{aircraft['ID']}-{time_slot}"]
                        if position in special_workshops:
                            workshop_type = "SPC"
                        elif position in standard_workshops:
                            workshop_type = "STD"
                        else:
                            workshop_type = "PRK"
                        file.write(f"{workshop_type}{position} ")
                    file.write("\n")
                i += 1


def setup_problem(num_time_slots, matrix_size, standard_workshops, special_workshops, parking_spots, aircrafts):
    '''
    Funcion para configurar el problema CSP
    '''
    # Creamos una instancia del problema
    problem = Problem()
    # Dominio de las posiciones
    domain = parking_spots + standard_workshops + special_workshops
    # Añadimos las variables al problema
    for aircraft in aircrafts:
        for time_slot in range(num_time_slots):
            problem.addVariable(f"{aircraft['ID']}-{time_slot}", domain)


    def max_1_jumbo_per_workshop(*assignments):
        '''
        Restricción en la que solo puede haber un JMB por taller
        '''
        jumbo_counts = {}
        list_result = [(aircrafts[i], assignments[i]) for i in range(min(len(aircrafts), len(assignments)))]
        for aircraft, position in list_result:
            if aircraft["TIPO"] == "JMB":
                if position not in jumbo_counts:
                    jumbo_counts[position] = 0
                jumbo_counts[position] = jumbo_counts[position] + 1
                if jumbo_counts[position] > 1:
                    return False
        return True

    # Añadimos la restricción al problema
    for time_slot in range(num_time_slots):
        variables_for_time_slot = [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts]
        problem.addConstraint(max_1_jumbo_per_workshop, variables_for_time_slot)


    def max_2_aircrafts_per_workshop(*assignments):
        '''
        Restricción en la que no puede haber más de 2 aviones en un taller
        '''
        workshop_counts = {}
        for position in assignments:
            if position not in workshop_counts:
                workshop_counts[position] = 0
            workshop_counts[position] = workshop_counts[position] + 1
            if workshop_counts[position] > 2:
                return False
        return True

    # Añadimos la restricción al problema
    for time_slot in range(num_time_slots):
        variables_for_time_slot = [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts]
        problem.addConstraint(max_2_aircrafts_per_workshop, variables_for_time_slot)


    def task_constraints(*assignments):
        '''
        Restricción en la que se deben cumplir las tareas de mantenimiento
        '''
        for aircraft in aircrafts:
            remaining_tasks = {"T1": aircraft["T1"], "T2": aircraft["T2"]}
            standard_workshop_count = 0
            special_workshop_count = 0

            for time_slot in range(num_time_slots):
                position = assignments[aircrafts.index(aircraft) * num_time_slots + time_slot]
                if position in special_workshops:
                    standard_workshop_count = standard_workshop_count + 1
                    special_workshop_count = special_workshop_count + 1
                    if remaining_tasks["T2"] > 0:
                        remaining_tasks["T2"] = remaining_tasks["T2"] - 1
                    elif remaining_tasks["T1"] > 0 and aircraft["RESTR"] == "T" and remaining_tasks["T2"] == 0:
                        remaining_tasks["T1"] = remaining_tasks["T1"] - 1
                elif position in standard_workshops:
                    standard_workshop_count += 1
                    if aircraft["RESTR"] == "T" and remaining_tasks["T2"] > 0:
                        return False
                    if remaining_tasks["T1"] > 0:
                        remaining_tasks["T1"] = remaining_tasks["T1"] - 1

            if aircraft["T2"] > special_workshop_count:
                return False

            if aircraft["T1"] + aircraft["T2"] > standard_workshop_count:
                return False

        return True

    # Añadimos la restricción al problema
    problem.addConstraint(task_constraints, [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts for time_slot in
                                             range(num_time_slots)])


    def no_adjacent_jumbo(*assignments):
        '''
        Restricción en la que no puede haber aviones JUMBO adyacentes
        '''
        list_result = [(aircrafts[i], assignments[i]) for i in range(min(len(aircrafts), len(assignments)))]
        jumbo_positions = [pos for aircraft, pos in list_result if aircraft["TIPO"] == "JMB"]
        for pos in jumbo_positions:
            x, y = pos
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            for adj in neighbors:
                if adj in domain and adj in jumbo_positions:
                    return False
        return True

    # Añadimos la restricción al problema
    for time_slot in range(num_time_slots):
        variables_for_time_slot = [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts]
        problem.addConstraint(no_adjacent_jumbo, variables_for_time_slot)


    def no_adjacent_occupancy(*assignments):
        '''
        Restricción en la que no puede haber aviones adyacentes
        '''
        occupied_positions = set(assignments)
        for position in occupied_positions:
            if position in standard_workshops + special_workshops + parking_spots:
                x, y = position
                neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if all(adj in occupied_positions for adj in neighbors if adj in domain):
                    return False
        return True

    # Añadimos la restricción al problema
    for time_slot in range(num_time_slots):
        variables_for_time_slot = [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts]
        problem.addConstraint(no_adjacent_occupancy, variables_for_time_slot)

    return problem


def main():
    if len(sys.argv) != 2:
        raise ValueError("python parte-1/CSPMaintenance.py parte-1/CSP-tests/maintenanceXX.txt")

    input_file_path = sys.argv[1]
    scheduler = MaintenanceScheduler(input_file_path)
    scheduler.execute()


if __name__ == "__main__":
    main()
