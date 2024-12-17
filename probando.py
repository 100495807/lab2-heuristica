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

    def load_data(self):
        try:
            print("Loading data...")
            self.time_slots, self.matrix_size, self.standard_workshops, self.special_workshops, self.parking_spots, self.aircrafts = self.file_manager.load_file_data(
                self.input_file_path)
        except Exception as e:
            raise ValueError(f"Error loading data from file: {e}")

    def setup_problem(self):
        self.problem = setup_problem(self.time_slots, self.matrix_size, self.standard_workshops, self.special_workshops,
                                     self.parking_spots, self.aircrafts)

    def solve_problem(self):
        start_time = time.time()
        self.solutions = self.problem.getSolutions()
        end_time = time.time()
        self.execution_time = end_time - start_time

    def save_results(self):
        print("Saving results...")
        self.file_manager.save_results(self.output_file_path, self.solutions, self.aircrafts, self.time_slots,
                                       self.special_workshops, self.standard_workshops)

    def execute(self):
        self.load_data()
        print(
            f"Time slots: {self.time_slots} \nMatrix size: {self.matrix_size} \nStandard Workshops: {self.standard_workshops} "
            f"\nSpecial Workshops: {self.special_workshops} \nParking Spots: {self.parking_spots} \nAircrafts: {self.aircrafts}")
        self.setup_problem()
        self.solve_problem()
        print(f"Execution Time: {self.execution_time:.2f} seconds \nNumber of solutions found: {len(self.solutions)}")
        self.save_results()
        print("Process completed.")


class FileManager:
    def __init__(self):
        pass

    def extract_positions(self, line):
        positions_str = line.split(":")[1].strip()
        positions = [tuple(map(int, re.findall(r'\d+', pos))) for pos in positions_str.split()]
        return positions

    def extract_aircraft(self, line):
        parts = line.strip().split("-")
        return {
            "ID": parts[0],
            "TYPE": parts[1],
            "RESTR": parts[2],
            "T1": int(parts[3]),
            "T2": int(parts[4])
        }

    def load_file_data(self, file_path):
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
        with open(output_file_path, 'w') as file:
            file.write(f"Num. Solutions: {len(solutions)}\n")
            if not solutions:
                file.write("No valid solutions found.\n")
                print("No valid solutions found.")
                return

            for i, solution in enumerate(solutions[:50]):
                file.write(f"Solution {i + 1}:\n")
                for aircraft in aircrafts:
                    file.write(
                        f"{aircraft['ID']}-{aircraft['TYPE']}-{aircraft['RESTR']}-{aircraft['T1']}-{aircraft['T2']}: ")
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

# Setup the CSP problem
def setup_problem(num_time_slots, matrix_size, standard_workshops, special_workshops, parking_spots, aircrafts):
    problem = Problem()

    domain = standard_workshops + special_workshops + parking_spots

    for aircraft in aircrafts:
        for time_slot in range(num_time_slots):
            problem.addVariable(f"{aircraft['ID']}-{time_slot}", domain)

    # Constraint: Max 2 aircraft per workshop
    def max_2_aircrafts_per_workshop(*assignments):
        workshop_counts = defaultdict(int)
        for position in assignments:
            workshop_counts[position] += 1
            if workshop_counts[position] > 2:
                return False
        return True

    # Constraint: Max 1 JMB per workshop
    def max_1_jumbo_per_workshop(*assignments):
        jumbo_counts = defaultdict(int)
        for aircraft, position in zip(aircrafts, assignments):
            if aircraft["TYPE"] == "JMB":
                jumbo_counts[position] += 1
                if jumbo_counts[position] > 1:
                    return False
        return True

    for time_slot in range(num_time_slots):
        variables_for_time_slot = [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts]
        problem.addConstraint(max_2_aircrafts_per_workshop, variables_for_time_slot)
        problem.addConstraint(max_1_jumbo_per_workshop, variables_for_time_slot)

    # Constraint: Tasks completed in valid workshops in order if applicable
    def task_constraints(*assignments):
        for aircraft in aircrafts:
            remaining_tasks = {"T1": aircraft["T1"], "T2": aircraft["T2"]}
            special_workshop_count = 0
            standard_workshop_count = 0

            for time_slot in range(num_time_slots):
                position = assignments[aircrafts.index(aircraft) * num_time_slots + time_slot]
                if position in special_workshops:
                    special_workshop_count += 1
                    standard_workshop_count += 1
                    if remaining_tasks["T2"] > 0:
                        remaining_tasks["T2"] -= 1
                    elif aircraft["RESTR"] == "T" and remaining_tasks["T2"] == 0 and remaining_tasks["T1"] > 0:
                        remaining_tasks["T1"] -= 1
                elif position in standard_workshops:
                    standard_workshop_count += 1
                    if remaining_tasks["T2"] > 0 and aircraft["RESTR"] == "T":
                        return False
                    if remaining_tasks["T1"] > 0:
                        remaining_tasks["T1"] -= 1

            if special_workshop_count < aircraft["T2"]:
                return False

            if standard_workshop_count < aircraft["T1"] + aircraft["T2"]:
                return False

        return True

    problem.addConstraint(task_constraints, [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts for time_slot in
                                             range(num_time_slots)])

    # Constraint: Ensure free adjacency
    def no_adjacent_occupancy(*assignments):
        occupied_positions = set(assignments)
        for position in occupied_positions:
            if position in parking_spots + standard_workshops + special_workshops:
                x, y = position
                neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if all(adj in occupied_positions for adj in neighbors if adj in domain):
                    return False
        return True

    for time_slot in range(num_time_slots):
        variables_for_time_slot = [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts]
        problem.addConstraint(no_adjacent_occupancy, variables_for_time_slot)

    # Constraint: Avoid adjacent JMB aircrafts
    def no_adjacent_jumbo(*assignments):
        jumbo_positions = [pos for aircraft, pos in zip(aircrafts, assignments) if aircraft["TYPE"] == "JMB"]
        for pos in jumbo_positions:
            x, y = pos
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if any(adj in jumbo_positions for adj in neighbors if adj in domain):
                return False
        return True

    for time_slot in range(num_time_slots):
        variables_for_time_slot = [f"{aircraft['ID']}-{time_slot}" for aircraft in aircrafts]
        problem.addConstraint(no_adjacent_jumbo, variables_for_time_slot)

    return problem


def main():
    if len(sys.argv) != 2:
        raise ValueError("Valid format: python MaintenanceScheduler.py <path to maintenance file>")

    input_file_path = sys.argv[1]
    scheduler = MaintenanceScheduler(input_file_path)
    scheduler.execute()


if __name__ == "__main__":
    main()
