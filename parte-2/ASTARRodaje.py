import os
import sys
import time
from itertools import product

class Heuristics:
    @staticmethod
    def manhattan_heuristic(positions, goals):
        '''
        Calcula la distancia de manhattan entre las posiciones y las metas de los aviones.
        '''
        return sum(abs(x - gx) + abs(y - gy) for (x, y), (gx, gy) in zip(positions, goals))

    @staticmethod
    def max_manhattan_heuristic(positions, goals):
        '''
        Calcula la distancia de manhattan máxima entre las posiciones y las metas de los aviones.
        '''
        distances = [abs(x - gx) + abs(y - gy) for (x, y), (gx, gy) in zip(positions, goals)]
        return max(distances)

class MovementValidator:
    @staticmethod
    def obtain_valid_movements(pos, map_data):
        '''
        Se obtienen los movimientos válidos para un avión en una posición dada.
        '''
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
        '''
        Se generan los sucesores de un estado dado.
        '''
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
    def __init__(self, map_data, aircrafts, heuristic, max_expanded_nodes=100000):
        self.map_data = map_data
        self.aircrafts = aircrafts
        self.heuristic = heuristic
        self.max_expanded_nodes = max_expanded_nodes

    def a_star(self):
        '''
        Algoritmo A* para encontrar la solución al problema de los aviones.
        '''
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

            if expanded_nodes > self.max_expanded_nodes:
                print("Se ha alcanzado el número máximo de nodos expandidos.")
                break

            for successor in SuccessorGenerator.generate_successors(state, self.map_data, goal):
                counter += 1
                cost = successor['tiempo'] + self.heuristic(successor['posiciones'], goal)
                queue.append((cost, counter, successor))

        return None, None, h_initial, expanded_nodes

class AStarRunner:
    def __init__(self, csv_route, num_heuristic):
        self.csv_route = csv_route
        self.num_heuristic = num_heuristic
        self.name_map = os.path.basename(csv_route).split('.')[0]
        self.map_data, self.aircraft = self.read_input()
        self.heuristic = self.select_heuristic()
        self.a_star_algorithm = AStarAlgorithm(self.map_data, self.aircraft, self.heuristic)

    def read_input(self):
        '''
        Metodo para leer el archivo de entrada.
        '''
        with open(self.csv_route, 'r') as file:
            lines = file.read().strip().split('\n')

        n_aircrafts = int(lines[0])
        aircrafts = []
        initial_positions = set()
        map_data = [linea.split(';') for linea in lines[n_aircrafts + 1:]]

        for i in range(1, n_aircrafts + 1):
            init, goal = lines[i].split()
            init_pos = tuple(map(int, init.strip('()').split(',')))
            goal_pos = tuple(map(int, goal.strip('()').split(',')))

            if init_pos in initial_positions:
                raise ValueError(f"Dos aviones no pueden comenzar en la misma casilla: {init_pos}")
            if map_data[init_pos[0]][init_pos[1]] == 'G' or map_data[goal_pos[0]][goal_pos[1]] == 'G':
                raise ValueError(f"Un avión no puede tener una casilla gris como inicial o final: {init_pos} o {goal_pos}")

            initial_positions.add(init_pos)
            aircrafts.append({
                'init': init_pos,
                'goal': goal_pos
            })

        return map_data, aircrafts

    def select_heuristic(self):
        '''
        Metodo para seleccionar la heurística a utilizar.
        '''
        if self.num_heuristic == 1:
            return Heuristics.manhattan_heuristic
        elif self.num_heuristic == 2:
            return Heuristics.max_manhattan_heuristic
        else:
            print("Heurística no implementada."
                  "Use 1 (heuristica de manhattan) o 2 (heuristica maxima de manhattan).")
            sys.exit(1)

    def handle_error(self, error):
        '''
        Metodo que maneja los errores y guarda los resultados en un archivo de salida.
        '''
        print(error)
        output_dir = "./parte-2/ASTAR-tests"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = f"{output_dir}/{self.name_map}-{self.num_heuristic}.output"
        stat_path = f"{output_dir}/{self.name_map}-{self.num_heuristic}.stat"

        with open(output_path, 'w') as f_output:
            f_output.write(str(error) + '\n')

        with open(stat_path, 'w') as f_stat:
            f_stat.write(f"Error: {error}\nNo se encontró solución\n")

        sys.exit(1)

    def run(self):
        '''
        Metodo para ejecutar el programa.
        '''
        start_time = time.time()
        solution, makespan, h_initial, expanded_nodes = self.a_star_algorithm.a_star()
        end_time = time.time()

        output_dir = "./parte-2/ASTAR-tests"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = f"{output_dir}/{self.name_map}-{self.num_heuristic}.output"
        stat_path = f"{output_dir}/{self.name_map}-{self.num_heuristic}.stat"

        if solution:
            with open(output_path, 'w') as f_output:
                for movements in solution:
                    f_output.write(' '.join(movements) + '\n')

            with open(stat_path, 'w') as f_stat:
                f_stat.write(f"Tiempo total: {end_time - start_time:.10f}s\n"
                             f"Makespan: {makespan}\n"
                             f"h inicial: {h_initial}\n"
                             f"Nodos expandidos: {expanded_nodes}\n")

            print("Solución y estadísticas guardadas en ./ASTAR-tests/")
        else:
            with open(output_path, 'w') as f_output:
                f_output.write("No se encontró solución\n")

            with open(stat_path, 'w') as f_stat:
                f_stat.write(f"Tiempo total: {end_time - start_time:.10f}s\n"
                             f"No se encontró solución\n"
                             f"h inicial: {h_initial}\n"
                             f"Nodos expandidos: {expanded_nodes}\n")

            print(f"No se encontró solución\n"
                  f"h inicial: {h_initial}\n"
                  f"Nodos expandidos: {expanded_nodes}\n"
                  f"Tiempo total: {end_time - start_time:.10f} segundos")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ASTARRodaje.py <path mapa00.csv> <num-h>")
        sys.exit(1)

    csv_route = sys.argv[1]
    num_heuristic = int(sys.argv[2])

    runner = AStarRunner(csv_route, num_heuristic)
    runner.run()