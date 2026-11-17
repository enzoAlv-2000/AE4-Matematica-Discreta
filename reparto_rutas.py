"""
Navegador de rutas de reparto
Matemática Discreta - TIFAS 2026 (Navegador de rutas)

Modelo matemático: grafo no dirigido y ponderado.
    vértices = depósito y clientes
    aristas  = rutas directas entre dos puntos
    peso     = kilómetros de cada ruta
Representación en el programa: matriz de adyacencia ponderada
    M[i][j] = km de la ruta directa entre i y j   (0 = no hay ruta directa)
"""

INF = float("inf")

# ----------------------------------------------------------------------
# DATOS DE EJEMPLO (la misma instancia reducida del anexo manual)
# ----------------------------------------------------------------------
NOMBRES = ["A", "B", "C", "D", "E"]          # A = depósito
RUTAS = [                                     # (origen, destino, km)
    (0, 1, 4), (0, 2, 2), (1, 2, 1), (1, 3, 5),
    (2, 3, 8), (2, 4, 10), (3, 4, 2),
]


# ----------------------------------------------------------------------
# R1 / R2: construir el grafo y su matriz de adyacencia ponderada
# ----------------------------------------------------------------------
def crear_matriz(n):
    """Matriz n x n llena de ceros (sin rutas)."""
    return [[0] * n for _ in range(n)]


def agregar_ruta(M, i, j, km):
    """Agrega una arista no dirigida: la matriz queda simétrica."""
    M[i][j] = km
    M[j][i] = km


def construir_grafo(n, rutas):
    M = crear_matriz(n)
    for i, j, km in rutas:
        agregar_ruta(M, i, j, km)
    return M


def mostrar_matriz(M, nombres):
    print("    " + "  ".join(f"{x:>3}" for x in nombres))
    for i, fila in enumerate(M):
        print(f"{nombres[i]:>3} " + "  ".join(f"{v:>3}" for v in fila))


# ----------------------------------------------------------------------
# R5: grado de cada vértice (cantidad de rutas que salen del punto)
# ----------------------------------------------------------------------
def grados(M):
    return [sum(1 for v in fila if v != 0) for fila in M]


# ----------------------------------------------------------------------
# R4: conexidad (recorrido en anchura desde el vértice 0)
# ----------------------------------------------------------------------
def es_conexo(M):
    n = len(M)
    visitados = {0}
    pendientes = [0]
    while pendientes:
        u = pendientes.pop(0)
        for v in range(n):
            if M[u][v] != 0 and v not in visitados:
                visitados.add(v)
                pendientes.append(v)
    return len(visitados) == n


# ----------------------------------------------------------------------
# R3: camino de peso mínimo (algoritmo de Dijkstra sobre la matriz)
# ----------------------------------------------------------------------
def camino_minimo(M, origen, destino):
    """Devuelve (costo, [vértices del camino]) o None si no hay camino."""
    n = len(M)
    dist = [INF] * n
    previo = [None] * n
    hecho = [False] * n
    dist[origen] = 0
    for _ in range(n):
        # elegir el vértice no fijado con menor distancia
        u, mejor = None, INF
        for v in range(n):
            if not hecho[v] and dist[v] < mejor:
                u, mejor = v, dist[v]
        if u is None:
            break
        hecho[u] = True
        # relajar las aristas que salen de u
        for v in range(n):
            if M[u][v] != 0 and dist[u] + M[u][v] < dist[v]:
                dist[v] = dist[u] + M[u][v]
                previo[v] = u
    if dist[destino] == INF:
        return None
    camino = []
    v = destino
    while v is not None:
        camino.append(v)
        v = previo[v]
    camino.reverse()
    return dist[destino], camino


# ----------------------------------------------------------------------
# R6: camino de Hamilton de menor costo (búsqueda con vuelta atrás)
# ----------------------------------------------------------------------
def mejor_hamilton(M, origen):
    """Camino que sale de 'origen' y visita todos los vértices una sola vez.
    Devuelve (costo, camino) del más corto, o None si no existe."""
    n = len(M)
    mejor = [INF, None]

    def buscar(actual, camino, costo):
        if len(camino) == n:                       # visitó todos
            if costo < mejor[0]:
                mejor[0], mejor[1] = costo, camino[:]
            return
        for v in range(n):
            if M[actual][v] != 0 and v not in camino:
                camino.append(v)
                buscar(v, camino, costo + M[actual][v])
                camino.pop()                       # vuelta atrás

    buscar(origen, [origen], 0)
    if mejor[1] is None:
        return None
    return mejor[0], mejor[1]


# ----------------------------------------------------------------------
# Extra: ¿se pueden recorrer todas las rutas una sola vez? (Euler)
# ----------------------------------------------------------------------
def tipo_euler(M):
    if not es_conexo(M):
        return "ninguno (no es conexo)"
    impares = [i for i, g in enumerate(grados(M)) if g % 2 == 1]
    if len(impares) == 0:
        return "circuito de Euler"
    if len(impares) == 2:
        return "camino de Euler"
    return "ninguno"


def nombres_de(camino, nombres):
    return " -> ".join(nombres[v] for v in camino)


# ----------------------------------------------------------------------
# CASOS DE PRUEBA (cada uno se compara con la resolución manual)
# ----------------------------------------------------------------------
def pruebas():
    M = construir_grafo(5, RUTAS)

    # Prueba 1: grados (suman 2 * cantidad de aristas = 14)
    assert grados(M) == [2, 3, 4, 3, 2]
    assert sum(grados(M)) == 2 * len(RUTAS)

    # Prueba 2: el grafo es conexo
    assert es_conexo(M)

    # Prueba 3: camino mínimo de A a E = 10 km por A-C-B-D-E
    assert camino_minimo(M, 0, 4) == (10, [0, 2, 1, 3, 4])

    # Prueba 4: Hamilton más corto desde A = 10 km por A-C-B-D-E
    assert mejor_hamilton(M, 0) == (10, [0, 2, 1, 3, 4])

    # Prueba 5: B y D son impares -> hay camino de Euler (no circuito)
    assert tipo_euler(M) == "camino de Euler"

    # Prueba 6: cambia un dato (la ruta A-C pasa de 2 a 9 km)
    M2 = construir_grafo(5, RUTAS)
    agregar_ruta(M2, 0, 2, 9)
    assert camino_minimo(M2, 0, 4) == (11, [0, 1, 3, 4])
    assert mejor_hamilton(M2, 0) == (15, [0, 1, 2, 3, 4])

    # Prueba 7: un cliente sin rutas -> no conexo y sin camino
    M3 = construir_grafo(6, RUTAS)
    assert not es_conexo(M3)
    assert camino_minimo(M3, 0, 5) is None

    print("Todas las pruebas pasaron.")


# ----------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# ----------------------------------------------------------------------
def main():
    M = construir_grafo(len(NOMBRES), RUTAS)

    print("MATRIZ DE ADYACENCIA PONDERADA (0 = no hay ruta directa)")
    mostrar_matriz(M, NOMBRES)

    print("\nGRADO DE CADA PUNTO")
    for nombre, g in zip(NOMBRES, grados(M)):
        print(f"  {nombre}: {g}")

    print("\n¿Se llega a todos los puntos desde el depósito?",
          "Sí" if es_conexo(M) else "No")

    print("\nCAMINO MÁS CORTO DESDE EL DEPÓSITO (A)")
    for destino in range(1, len(NOMBRES)):
        costo, camino = camino_minimo(M, 0, destino)
        print(f"  A -> {NOMBRES[destino]}: {costo} km  ({nombres_de(camino, NOMBRES)})")

    print("\nRECORRIDO QUE PASA POR TODOS LOS CLIENTES UNA VEZ (Hamilton)")
    res = mejor_hamilton(M, 0)
    if res:
        print(f"  {res[0]} km  ({nombres_de(res[1], NOMBRES)})")
    else:
        print("  No existe.")

    print("\nRECORRER TODAS LAS RUTAS UNA VEZ (Euler):", tipo_euler(M))


if __name__ == "__main__":
    pruebas()
    print()
    main()
