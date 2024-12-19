#!/bin/bash

# Ejecutar los casos de prueba y generar archivos de salida .csv
echo "Ejecutando test1"
python parte-1/CSPMaintenance.py parte-1/CSP-tests/maintenance01.txt # Tiempo = 0.69s, Soluciones = 0
echo ""
echo "Ejecutando test2"
python parte-1/CSPMaintenance.py parte-1/CSP-tests/maintenance02.txt # Tiempo = 0.025s, Soluciones = 54
echo ""
echo "Ejecutando test3"
python parte-1/CSPMaintenance.py parte-1/CSP-tests/maintenance03.txt # Tiempo = 0.21s, Soluciones = 66
echo ""
echo "Ejecutando test4"
python parte-1/CSPMaintenance.py parte-1/CSP-tests/maintenance04.txt # Tiempo = 37s, Soluciones = 1624
echo ""
echo "Ejecutando test5"
python parte-1/CSPMaintenance.py parte-1/CSP-tests/maintenance05.txt # Tiempo = 738.68s, Soluciones = 3312
echo ""
echo "Ejecutando test6"
python parte-1/CSPMaintenance.py parte-1/CSP-tests/maintenance06.txt # Tiempo = 1415.35s, Soluciones = 1180164