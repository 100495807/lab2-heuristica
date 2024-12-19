import matplotlib.pyplot as plt
import pandas as pd

# Datos proporcionados
data = {
    "Caso": [1, 2, 3, 4, 5, 6],
    "Franjas Horarias": [3, 2, 2, 3, 3, 3],
    "Tamaño de Matriz": ["3x3", "2x2", "3x3", "3x2", "3x3", "3x3"],
    "Aviones": [3, 3, 3, 3, 3, 3],
    "Tiempo (s)": [69, 0.025, 0.21, 37, 738, 1415],
    "Soluciones": [0, 54, 66, 1626, 3312, 1180164]
}

# Crear un DataFrame
df = pd.DataFrame(data)

# Crear una tabla
plt.figure(figsize=(10, 4))
table = plt.table(cellText=df.values,
                  colLabels=df.columns,
                  cellLoc='center',
                  loc='center')

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)
plt.axis('off')
plt.title("Resumen de Casos de Prueba")

plt.show()

# Gráfico de líneas para el tiempo y las soluciones según el caso
fig, ax1 = plt.subplots(figsize=(12, 6))

# Eje primario (Tiempo de ejecución) con escala logarítmica
ax1.set_xlabel("Caso")
ax1.set_ylabel("Tiempo (s)", color="tab:blue")
ax1.set_yscale("log")
ax1.plot(df["Caso"], df["Tiempo (s)"], marker="o", color="tab:blue", label="Tiempo (s)")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax1.set_xticks(df["Caso"])

# Eje secundario (Número de soluciones) con escala logarítmica
ax2 = ax1.twinx()
ax2.set_ylabel("Soluciones", color="tab:orange")
ax2.set_yscale("log")
ax2.plot(df["Caso"], df["Soluciones"], marker="o", linestyle="-", color="tab:orange", label="Soluciones")
ax2.tick_params(axis="y", labelcolor="tab:orange")

# Títulos y leyendas
fig.tight_layout()
plt.title("Tiempo de Ejecución y Número de Soluciones por Caso")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

plt.show()