# lab2-heuristica

Segunda practica de Heuristica centrada en dos familias de problemas: satisfaccion de restricciones (CSP) para planificacion de mantenimiento de aviones y busqueda heuristica A* para rodaje de aeronaves sobre mapas.

## Objetivo

Resolver problemas de planificacion y busqueda aplicando tecnicas de IA clasica: restricciones, dominios, generacion de sucesores y heuristicas admisibles/comparables.

## Contenido

| Carpeta / Archivo | Descripcion |
| --- | --- |
| `parte-1/CSPMaintenance.py` | Planificador CSP de mantenimiento. |
| `parte-1/CSP-tests/` | Casos de prueba de mantenimiento. |
| `parte-1/CSP-calls.sh` | Script de ejecucion de CSP. |
| `parte-2/ASTARRodaje.py` | Busqueda A* para rodaje de aviones. |
| `parte-2/ASTAR-tests/` | Mapas, salidas y estadisticas. |
| `parte-2/ASTAR-calls.sh` | Script de ejecucion de A*. |
| `analisis-p1.py`, `analisis-p2.py` | Analisis de resultados. |

## Parte 1: CSP

El planificador asigna aviones a talleres o parkings durante franjas temporales, respetando restricciones como:

- maximo de aviones por taller,
- restricciones especificas para aviones jumbo,
- tareas de mantenimiento estandar/especial,
- disponibilidad de posiciones y franjas.

## Parte 2: A*

El algoritmo busca rutas para mover aviones desde posiciones iniciales a destinos evitando:

- celdas bloqueadas,
- colisiones entre aviones,
- cruces de trayectoria,
- movimientos invalidos fuera del mapa.

Incluye heuristicas de Manhattan total y maxima.

## Tecnologias

- Python
- python-constraint
- Algoritmo A*
- Heuristicas Manhattan
- Lectura/escritura de CSV y TXT
- Scripts Bash de ejecucion

## Como Ejecutarlo

Ejemplo CSP:

```bash
python parte-1/CSPMaintenance.py parte-1/CSP-tests/maintenance01.txt
```

Ejemplo A*:

```bash
python parte-2/ASTARRodaje.py parte-2/ASTAR-tests/mapa01.csv 1
```

## Aprendizajes

- Formular un problema como CSP con variables, dominios y restricciones.
- Generar sucesores validos en busqueda multiagente.
- Comparar heuristicas segun nodos expandidos y tiempo.
- Detectar colisiones y restricciones espaciales en mapas.
- Guardar salidas y estadisticas para analizar rendimiento.

## Estado

Proyecto academico finalizado. Se conserva como practica de CSP, busqueda heuristica y planificacion.