import pandas as pd
from matplotlib import pyplot as plt

data = {
    "Heurística": ["Distancia de Manhattan", "Distancia Máxima de Manhattan"],
    "Tiempo de ejecución (s)": [0.0056955814, 0.0091302395],
    "Makespan": [9, 9],
    "h inicial": [8, 4],
    "Nodos expandidos": [96, 113]
}

# Crear el DataFrame
df = pd.DataFrame(data)

# Mostrar los datos
print("Resultados Comparativos de las Heurísticas")
print(df)

# Generar gráficas

# Gráfica comparativa de tiempos de ejecución
plt.figure(figsize=(8, 5))
plt.bar(df["Heurística"], df["Tiempo de ejecución (s)"], width=0.8)
plt.title("Comparativa de Tiempos de Ejecución")
plt.ylabel("Tiempo (s)")
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()

# Gráfica comparativa de nodos expandidos
plt.figure(figsize=(8, 5))
plt.bar(df["Heurística"], df["Nodos expandidos"], width=0.8)
plt.title("Comparativa de Nodos Expandidos")
plt.ylabel("Nodos expandidos")
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()

# Gráfica comparativa de h inicial
plt.figure(figsize=(8, 5))
plt.bar(df["Heurística"], df["h inicial"], width=0.8)
plt.title("Comparativa de Valores de h Inicial")
plt.ylabel("h inicial")
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()

# Gráfica comparativa de makespan
plt.figure(figsize=(8, 5))
plt.bar(df["Heurística"], df["Makespan"], width=0.8)
plt.title("Comparativa de Makespan")
plt.ylabel("Makespan")
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()
