import heapq
import csv
import time
from itertools import product
import sys

def leer_mapa_csv(ruta):
    with open(ruta, 'r') as archivo:
        lineas = archivo.read().strip().split('\n')

    n_aviones = int(lineas[0])
    aviones = []
    for i in range(1, n_aviones + 1):
        inicio, fin = lineas[i].split()
        aviones.append({
            'init': tuple(map(int, inicio.strip('()').split(','))),
            'goal': tuple(map(int, fin.strip('()').split(',')))
        })

    mapa = [linea.split(';') for linea in lineas[n_aviones + 1:]]
    return mapa, aviones

def obtener_movimientos_validos(pos, mapa):
    """Devuelve las posiciones adyacentes o la misma posición (si no es 'A') a las que puede moverse el avión."""
    movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    x, y = pos
    validos = [(x + dx, y + dy) for dx, dy in movimientos
               if 0 <= x + dx < len(mapa) and 0 <= y + dy < len(mapa[0]) and mapa[x + dx][y + dy] != 'G']
    # Permitir esperar si no es 'A'
    if mapa[x][y] != 'A':
        validos = [pos] + validos
    return validos

def heuristica_manhattan(posiciones, metas):
    """Heurística 1 (Suma de Manhattan): Suma de las distancias Manhattan de cada avión a su meta."""
    return sum(abs(x - gx) + abs(y - gy) for (x, y), (gx, gy) in zip(posiciones, metas))

def heuristica_max_manhattan(posiciones, metas):
    """Heurística 2 (Máxima Manhattan): Máximo de las distancias Manhattan."""
    distancias = [abs(x - gx) + abs(y - gy) for (x, y), (gx, gy) in zip(posiciones, metas)]
    return max(distancias)

def generar_sucesores(estado, mapa, metas):
    """Genera todos los sucesores posibles a partir del estado actual, cumpliendo las restricciones."""
    sucesores = []
    aviones = estado['posiciones']
    tiempo = estado['tiempo']
    movimientos_actuales = estado['movimientos']
    direcciones = {(0, 1): '→', (0, -1): '←', (1, 0): '↓', (-1, 0): '↑', (0, 0): 'w'}

    posibles_movimientos = []
    for i, pos in enumerate(aviones):
        if pos == metas[i]:
            # Si el avión está en su meta, sólo puede esperar
            posibles_movimientos.append([pos])
        else:
            movimientos_validos = obtener_movimientos_validos(pos, mapa)
            posibles_movimientos.append(movimientos_validos)

    for movimientos in product(*posibles_movimientos):
        nuevas_posiciones = list(movimientos)

        # Colisión directa: no dos aviones en la misma celda
        if len(set(nuevas_posiciones)) != len(nuevas_posiciones):
            continue

        # Colisión cruzada: evitar intercambio de posiciones
        colision_cruzada = False
        for i in range(len(aviones)):
            for j in range(i + 1, len(aviones)):
                # Si el avión i va a la posición que tenía el j, y el j va a la posición que tenía el i
                if nuevas_posiciones[i] == aviones[j] and nuevas_posiciones[j] == aviones[i]:
                    colision_cruzada = True
                    break
            if colision_cruzada:
                break

        if colision_cruzada:
            continue

        # Generar sucesor válido
        nuevo_movimientos = [m[:] for m in movimientos_actuales]
        for i, (prev, nueva) in enumerate(zip(aviones, nuevas_posiciones)):
            dx, dy = nueva[0] - prev[0], nueva[1] - prev[1]
            movimiento_etiqueta = direcciones.get((dx, dy), 'w')
            nuevo_movimientos[i].append(f"{movimiento_etiqueta} ({nueva[0]},{nueva[1]})")

        sucesores.append({
            'posiciones': nuevas_posiciones,
            'tiempo': tiempo + 1,
            'movimientos': nuevo_movimientos
        })

    return sucesores

def a_estrella(mapa, aviones, heuristica):
    """Implementación del algoritmo A* para el problema."""
    inicio = {
        'posiciones': [a['init'] for a in aviones],
        'tiempo': 0,
        'movimientos': [[f"({a['init'][0]},{a['init'][1]})"] for a in aviones]
    }
    meta = [a['goal'] for a in aviones]

    cola = []
    contador = 0
    coste_inicial = heuristica(inicio['posiciones'], meta)
    heapq.heappush(cola, (coste_inicial, contador, inicio))

    visitados = set()
    h_inicial = coste_inicial
    nodos_expandidos = 0

    while cola:
        _, _, estado = heapq.heappop(cola)
        posiciones = estado['posiciones']

        # Verificar si es estado objetivo
        if posiciones == meta:
            return estado['movimientos'], estado['tiempo'], h_inicial, nodos_expandidos

        clave_estado = (tuple(posiciones), estado['tiempo'])
        if clave_estado in visitados:
            continue
        visitados.add(clave_estado)
        nodos_expandidos += 1

        # Generar sucesores
        for sucesor in generar_sucesores(estado, mapa, meta):
            contador += 1
            costo = sucesor['tiempo'] + heuristica(sucesor['posiciones'], meta)
            heapq.heappush(cola, (costo, contador, sucesor))

    return None, None, h_inicial, nodos_expandidos

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python p2.py <path mapa.csv> <num-h>")
        sys.exit(1)

    ruta_csv = sys.argv[1]
    num_heuristica = int(sys.argv[2])

    mapa, aviones = leer_mapa_csv(ruta_csv)

    if num_heuristica == 1:
        heuristica = heuristica_manhattan
    elif num_heuristica == 2:
        heuristica = heuristica_max_manhattan
    else:
        print("Heurística no implementada. Use 1 para suma, 2 para máxima.")
        sys.exit(1)

    inicio_tiempo = time.time()
    solucion, makespan, h_inicial, nodos_expandidos = a_estrella(mapa, aviones, heuristica)
    fin_tiempo = time.time()

    if solucion:
        print("Solución encontrada:")
        for i, movimientos in enumerate(solucion):
            print(f"Avion {i + 1}: " + ' '.join(movimientos))
        print(f"Makespan: {makespan}")
        print(f"h inicial: {h_inicial}")
        print(f"Nodos expandidos: {nodos_expandidos}")
        print(f"Tiempo total: {fin_tiempo - inicio_tiempo:.2f} segundos")
    else:
        print("No se encontró solución")
        print(f"h inicial: {h_inicial}")
        print(f"Nodos expandidos: {nodos_expandidos}")
        print(f"Tiempo total: {fin_tiempo - inicio_tiempo:.2f} segundos")
