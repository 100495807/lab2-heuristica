import ast
from difflib import SequenceMatcher
from collections import Counter


def obtener_nodos_ast(archivo):
    """Convierte el código fuente en una lista de nodos AST."""
    with open(archivo, 'r', encoding='utf-8') as f:
        codigo = f.read()
    try:
        tree = ast.parse(codigo)
        nodos = [type(node).__name__ for node in ast.walk(tree)]
        return nodos
    except SyntaxError:
        print(f"Error de sintaxis en {archivo}. Asegúrate de que sea un archivo válido de Python.")
        return []


def comparar_estructura_ast(archivo1, archivo2):
    """Compara la estructura AST de dos archivos."""
    nodos1 = obtener_nodos_ast(archivo1)
    nodos2 = obtener_nodos_ast(archivo2)

    if not nodos1 or not nodos2:
        return 0, None

    # Calcula la similitud basada en los nodos del AST
    secuencia = SequenceMatcher(None, nodos1, nodos2)
    similitud = secuencia.ratio() * 100

    # Conteo de nodos por tipo para información adicional
    contador1 = Counter(nodos1)
    contador2 = Counter(nodos2)

    return similitud, (contador1, contador2)


def comparar_codigos_por_tokens(archivo1, archivo2):
    """Compara los tokens de código fuente entre dos archivos."""
    with open(archivo1, 'r', encoding='utf-8') as f1, open(archivo2, 'r', encoding='utf-8') as f2:
        codigo1 = f1.read()
        codigo2 = f2.read()

    secuencia = SequenceMatcher(None, codigo1, codigo2)
    return secuencia.ratio() * 100


def mostrar_reporte(similitud_ast, nodos_ast, similitud_tokens):
    """Genera un reporte detallado de la comparación."""
    print(f"Similitud de estructura AST: {similitud_ast:.2f}%")
    if nodos_ast:
        contador1, contador2 = nodos_ast
        print("\nTipos de nodos en el AST de Archivo 1:")
        for nodo, cantidad in contador1.items():
            print(f"  {nodo}: {cantidad}")

        print("\nTipos de nodos en el AST de Archivo 2:")
        for nodo, cantidad in contador2.items():
            print(f"  {nodo}: {cantidad}")

    print(f"\nSimilitud de tokens: {similitud_tokens:.6f}%")
    if similitud_ast > 80 or similitud_tokens > 80:
        print("\n⚠️ Los códigos son altamente similares. Podrían ser detectados como plagio.")
    elif similitud_ast > 50 or similitud_tokens > 50:
        print("\n⚠️ Los códigos tienen similitudes moderadas. Podrían levantar sospechas.")
    else:
        print("\n✅ Los códigos tienen diferencias significativas y son menos probables de ser detectados como plagio.")


# Archivos de entrada
archivo1 = 'prueba.py'
archivo2 = 'probando.py'

# Comparación avanzada
similitud_ast, nodos_ast = comparar_estructura_ast(archivo1, archivo2)
similitud_tokens = comparar_codigos_por_tokens(archivo1, archivo2)

# Reporte
mostrar_reporte(similitud_ast, nodos_ast, similitud_tokens)
