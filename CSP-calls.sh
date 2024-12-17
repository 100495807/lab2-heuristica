#!/bin/bash

# Ejecutar los casos de prueba y generar archivos de salida .csv
python3 CSPMaintenance.py ./CSP-tests/maintenance01.txt
python3 CSPMaintenance.py ./CSP-tests/maintenance02.txt
python3 CSPMaintenance.py ./CSP-tests/maintenance03.txt
# python3 CSPMaintenance.py ./CSP-tests/maintenance04.txt       #no ejecutar, tarda 22 min

