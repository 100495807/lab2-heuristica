import time
from itertools import product
import sys
import os

class MapInputReader:
    @staticmethod
    def read_map_input(ruta):
        with open(ruta, 'r') as file:
            lines = file.read().strip().split('\n')

        n_aircrafts = int(lines[0])
        aircrafts = []
        for i in range(1, n_aircrafts + 1):
            init, goal = lines[i].split()
            aircrafts.append({
                'init': tuple(map(int, init.strip('()').split(','))),
                'goal': tuple(map(int, goal.strip('()').split(',')))
            })

        map_data = [linea.split(';') for linea in lines[n_aircrafts + 1:]]
        return map_data, aircrafts

class Heuristics:
    @staticmethod
    def manhattan_heuristic(positions, goals):
        return sum(abs(x - gx) + abs(y - gy) for (x, y), (gx, gy) in zip(positions, goals))

    @staticmethod
    def max_manhattan_heuristic(positions, goals):
        distances = [abs(x - gx) + abs(y - gy) for (x, y), (gx, gy) in zip(positions, goals)]
        return max(distances)

class MovementValidator:
    @staticmethod
    def obtain_valid_movements(pos, map_data):
        movements = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        x, y = pos
        valid = [(x + dx, y + dy) for dx, dy in movements
                 if 0 <= x + dx < len(map_data) and 0 <= y + dy < len(map_data[0]) and map_data[x + dx][y + dy] != 'G']
        if map_data[x][y] != 'A':
            valid = [pos] + valid
        return valid

class SuccessorGenerator:
    @staticmethod
    def generate_successors(state, map_data, goals):
        successors = []
        aircrafts = state['posiciones']
        time = state['tiempo']
        current_movements = state['movimientos']
        directions = {(0, 1): '→', (0, -1): '←', (1, 0): '↓', (-1, 0): '↑', (0, 0): 'w'}

        possible_movements = []
        for i, pos in enumerate(aircrafts):
            if pos == goals[i]:
                possible_movements.append([pos])
            else:
                valid_movements = MovementValidator.obtain_valid_movements(pos, map_data)
                possible_movements.append(valid_movements)

        for movements in product(*possible_movements):
            new_positions = list(movements)
            if len(set(new_positions)) != len(new_positions):
                continue

            cross_collision = False
            for i in range(len(aircrafts)):
                for j in range(i + 1, len(aircrafts)):
                    if new_positions[i] == aircrafts[j] and new_positions[j] == aircrafts[i]:
                        cross_collision = True
                        break
                if cross_collision:
                    break

            if cross_collision:
                continue

            new_movements = [m[:] for m in current_movements]
            for i, (prev, new) in enumerate(zip(aircrafts, new_positions)):
                dx, dy = new[0] - prev[0], new[1] - prev[1]
                movement_label = directions.get((dx, dy), 'w')
                new_movements[i].append(f"{movement_label} ({new[0]},{new[1]})")

            successors.append({
                'posiciones': new_positions,
                'tiempo': time + 1,
                'movimientos': new_movements
            })

        return successors

class AStarAlgorithm:
    def __init__(self, map_data, aircrafts, heuristic):
        self.map_data = map_data
        self.aircrafts = aircrafts
        self.heuristic = heuristic

    def a_star(self):
        start = {
            'posiciones': [a['init'] for a in self.aircrafts],
            'tiempo': 0,
            'movimientos': [[f"({a['init'][0]},{a['init'][1]})"] for a in self.aircrafts]
        }
        goal = [a['goal'] for a in self.aircrafts]

        queue = []
        counter = 0
        initial_cost = self.heuristic(start['posiciones'], goal)
        queue.append((initial_cost, counter, start))

        visited = set()
        h_initial = initial_cost
        expanded_nodes = 0

        while queue:
            queue.sort(key=lambda x: x[0])
            _, _, state = queue.pop(0)
            positions = state['posiciones']

            if positions == goal:
                return state['movimientos'], state['tiempo'], h_initial, expanded_nodes

            state_key = (tuple(positions), state['tiempo'])
            if state_key in visited:
                continue
            visited.add(state_key)
            expanded_nodes += 1

            for successor in SuccessorGenerator.generate_successors(state, self.map_data, goal):
                counter += 1
                cost = successor['tiempo'] + self.heuristic(successor['posiciones'], goal)
                queue.append((cost, counter, successor))

        return None, None, h_initial, expanded_nodes

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ASTARRodaje.py <path mapa01.csv> <num-h>")
        sys.exit(1)

    csv_route = sys.argv[1]
    num_heuristic = int(sys.argv[2])
    name_map = os.path.basename(csv_route).split('.')[0]

    map_data, aircraft = MapInputReader.read_map_input(csv_route)

    if num_heuristic == 1:
        heuristic = Heuristics.manhattan_heuristic
    elif num_heuristic == 2:
        heuristic = Heuristics.max_manhattan_heuristic
    else:
        print("Heurística no implementada. Use 1 para suma, 2 para máxima.")
        sys.exit(1)

    a_star_algorithm = AStarAlgorithm(map_data, aircraft, heuristic)

    start_time = time.time()
    solution, makespan, h_initial, expanded_nodes = a_star_algorithm.a_star()
    end_time = time.time()

    if solution:
        output_dir = "./parte-2/ASTAR-tests"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = f"{output_dir}/{name_map}-{num_heuristic}.output"
        stat_path = f"{output_dir}/{name_map}-{num_heuristic}.stat"

        with open(output_path, 'w') as f_output:
            for movements in solution:
                f_output.write(' '.join(movements) + '\n')

        with open(stat_path, 'w') as f_stat:
            f_stat.write(f"Tiempo total: {end_time - start_time:.10f}s\n")
            f_stat.write(f"Makespan: {makespan}\n")
            f_stat.write(f"h inicial: {h_initial}\n")
            f_stat.write(f"Nodos expandidos: {expanded_nodes}\n")

        print("Solución y estadísticas guardadas en ./ASTAR-tests/")
    else:
        print("No se encontró solución")
        print(f"h inicial: {h_initial}")
        print(f"Nodos expandidos: {expanded_nodes}")
        print(f"Tiempo total: {end_time - start_time:.10f} segundos")