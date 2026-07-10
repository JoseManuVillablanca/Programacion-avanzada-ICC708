"""
search_algorithms.py
Algoritmos de busqueda de rutas sobre grafos ponderados.

Implementados sin librerias externas:
  - BFS  (Breadth-First Search): camino con menor cantidad de aristas.
  - UCS  (Uniform-Cost Search / Dijkstra): camino de menor costo total.
  - A*   (A-star): version heuristica de UCS (opcional/bono).

Cada funcion retorna un namedtuple-like 'SearchResult' con:
  - path        : lista de nombres de nodos desde origen a destino.
  - cost        : costo/distancia acumulada (0 para BFS sin pesos).
  - visited     : numero de nodos explorados durante la busqueda.
  - found       : bool indicando si se alcanzo el destino.
  - hops        : numero de aristas en el camino (pasos).
"""

from models import RoadNetwork


# ──────────────────────────────────────────────
# Clase resultado de busqueda
# ──────────────────────────────────────────────
class SearchResult:
    """Encapsula el resultado de un algoritmo de busqueda de rutas."""

    def __init__(self, path: list, cost: float, visited: int,
                 found: bool, algorithm: str):
        self.path = path
        self.cost = cost
        self.visited = visited
        self.found = found
        self.algorithm = algorithm
        self.hops = len(path) - 1 if len(path) > 1 else 0

    def __repr__(self):
        if not self.found:
            return f"SearchResult({self.algorithm}: No hay ruta)"
        return (f"SearchResult({self.algorithm}: "
                f"hops={self.hops}, cost={self.cost:.2f}, "
                f"visited={self.visited}, path={self.path})")

    def print_result(self):
        """Imprime el resultado de forma legible en consola."""
        print(f"\n  Algoritmo  : {self.algorithm}")
        if not self.found:
            print("  Resultado  : No existe ruta entre los nodos indicados.")
            return
        print(f"  Ruta       : {' → '.join(self.path)}")
        print(f"  Saltos     : {self.hops}")
        print(f"  Costo total: {self.cost:.2f} min")
        print(f"  Nodos vis. : {self.visited}")


# ──────────────────────────────────────────────
# Cola auxiliar para BFS (FIFO sin deque)
# ──────────────────────────────────────────────
class _Queue:
    """Cola FIFO implementada con lista; eficiente para BFS pequenos."""
    def __init__(self):
        self._data = []
        self._head = 0   # puntero para evitar O(n) al desencolar

    def enqueue(self, item):
        self._data.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Cola vacia")
        item = self._data[self._head]
        self._head += 1
        return item

    def is_empty(self) -> bool:
        return self._head >= len(self._data)

    def __len__(self):
        return len(self._data) - self._head


# ──────────────────────────────────────────────
# Min-Heap auxiliar para UCS/Dijkstra y A*
# ──────────────────────────────────────────────
class _MinHeap:
    """
    Min-Heap generico para tuplas (costo, nodo, path).
    Compara por el primer elemento (costo).
    """

    def __init__(self):
        self._heap = []

    def push(self, item):
        """Inserta (costo, nodo, path) en el heap."""
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def pop(self):
        """Extrae y retorna el elemento de menor costo."""
        if not self._heap:
            raise IndexError("Heap vacio")
        self._swap(0, len(self._heap) - 1)
        item = self._heap.pop()
        if self._heap:
            self._sift_down(0)
        return item

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def _swap(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def _sift_up(self, i):
        while i > 0:
            p = (i - 1) // 2
            if self._heap[i][0] < self._heap[p][0]:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i):
        n = len(self._heap)
        while True:
            smallest = i
            l, r = 2 * i + 1, 2 * i + 2
            if l < n and self._heap[l][0] < self._heap[smallest][0]:
                smallest = l
            if r < n and self._heap[r][0] < self._heap[smallest][0]:
                smallest = r
            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break


# ──────────────────────────────────────────────
# Conjunto auxiliar (implementacion manual)
# ──────────────────────────────────────────────
class _VisitedSet:
    """
    Conjunto de nodos visitados implementado con una lista.
    Eficiente para grafos de hasta ~5000 nodos.
    """
    def __init__(self):
        self._items = []

    def add(self, item):
        if item not in self._items:
            self._items.append(item)

    def __contains__(self, item):
        return item in self._items

    def __len__(self):
        return len(self._items)


# ──────────────────────────────────────────────
# Algoritmo BFS
# ──────────────────────────────────────────────
def bfs(graph: RoadNetwork, start: str, target: str) -> SearchResult:
    """
    Busqueda en Anchura (Breadth-First Search).

    Encuentra el camino con menor cantidad de aristas (saltos) entre
    start y target, sin considerar los pesos de las aristas.

    Parametros
    ----------
    graph  : RoadNetwork
    start  : str – nodo origen
    target : str – nodo destino

    Retorna
    -------
    SearchResult
    """
    if not graph.node_exists(start) or not graph.node_exists(target):
        return SearchResult([], 0.0, 0, False, "BFS")

    if start == target:
        return SearchResult([start], 0.0, 1, True, "BFS")

    visited = _VisitedSet()
    visited.add(start)
    queue = _Queue()
    # Cada elemento en la cola: (nodo_actual, camino_hasta_aqui)
    queue.enqueue((start, [start]))
    visited_count = 1

    while not queue.is_empty():
        node, path = queue.dequeue()

        for neighbor, weight in graph.get_neighbors(node):
            if neighbor not in visited:
                new_path = path + [neighbor]
                visited_count += 1
                if neighbor == target:
                    # Calcular costo acumulado (suma de pesos)
                    cost = _path_cost(graph, new_path)
                    return SearchResult(new_path, cost,
                                        visited_count, True, "BFS")
                visited.add(neighbor)
                queue.enqueue((neighbor, new_path))

    return SearchResult([], 0.0, visited_count, False, "BFS")


# ──────────────────────────────────────────────
# Algoritmo UCS / Dijkstra
# ──────────────────────────────────────────────
def dijkstra(graph: RoadNetwork, start: str, target: str) -> SearchResult:
    """
    Busqueda de Costo Uniforme / Dijkstra.

    Encuentra el camino de menor costo total (suma de pesos de aristas)
    desde start hasta target.

    Parametros
    ----------
    graph  : RoadNetwork
    start  : str – nodo origen
    target : str – nodo destino

    Retorna
    -------
    SearchResult
    """
    if not graph.node_exists(start) or not graph.node_exists(target):
        return SearchResult([], 0.0, 0, False, "Dijkstra/UCS")

    if start == target:
        return SearchResult([start], 0.0, 1, True, "Dijkstra/UCS")

    # heap: (costo_acumulado, nodo, camino)
    heap = _MinHeap()
    heap.push((0.0, start, [start]))

    visited = _VisitedSet()
    visited_count = 0

    while not heap.is_empty():
        cost, node, path = heap.pop()

        if node in visited:
            continue

        visited.add(node)
        visited_count += 1

        if node == target:
            return SearchResult(path, cost, visited_count, True, "Dijkstra/UCS")

        for neighbor, weight in graph.get_neighbors(node):
            if neighbor not in visited:
                heap.push((cost + weight, neighbor, path + [neighbor]))

    return SearchResult([], 0.0, visited_count, False, "Dijkstra/UCS")


# ──────────────────────────────────────────────
# Algoritmo A* (bono)
# ──────────────────────────────────────────────
def astar(graph: RoadNetwork, start: str, target: str,
          heuristic=None) -> SearchResult:
    """
    Busqueda A* con heuristica configurable.

    Si no se provee heuristica, equivale a Dijkstra (h=0).

    Parametros
    ----------
    graph     : RoadNetwork
    start     : str
    target    : str
    heuristic : callable(node_name, target_name) → float, opcional
        Funcion que estima el costo minimo restante desde node hasta target.

    Retorna
    -------
    SearchResult
    """
    if heuristic is None:
        heuristic = lambda n, t: 0.0  # sin heuristica = Dijkstra

    if not graph.node_exists(start) or not graph.node_exists(target):
        return SearchResult([], 0.0, 0, False, "A*")

    if start == target:
        return SearchResult([start], 0.0, 1, True, "A*")

    # heap: (f = g + h, g = costo_real, nodo, camino)
    heap = _MinHeap()
    g0 = 0.0
    h0 = heuristic(start, target)
    heap.push((g0 + h0, g0, start, [start]))

    visited = _VisitedSet()
    visited_count = 0

    while not heap.is_empty():
        f, g, node, path = heap.pop()

        if node in visited:
            continue

        visited.add(node)
        visited_count += 1

        if node == target:
            return SearchResult(path, g, visited_count, True, "A*")

        for neighbor, weight in graph.get_neighbors(node):
            if neighbor not in visited:
                new_g = g + weight
                new_h = heuristic(neighbor, target)
                heap.push((new_g + new_h, new_g, neighbor, path + [neighbor]))

    return SearchResult([], 0.0, visited_count, False, "A*")


# ──────────────────────────────────────────────
# Utilidad: Encontrar el centro de emergencia
# mas cercano a un nodo destino
# ──────────────────────────────────────────────
def find_nearest_center(graph: RoadNetwork, target_node: str,
                        center_nodes: list,
                        algorithm: str = "dijkstra") -> tuple:
    """
    Encuentra el centro de emergencia mas cercano al nodo destino.

    Parametros
    ----------
    graph        : RoadNetwork
    target_node  : str – nodo donde ocurre el incidente
    center_nodes : list de str – nodos donde estan los centros disponibles
    algorithm    : 'bfs' o 'dijkstra'

    Retorna
    -------
    (best_result: SearchResult, best_center: str)
        El SearchResult con la ruta de menor costo, y el nombre del centro origen.
    """
    best_result = None
    best_center = None

    for center in center_nodes:
        if algorithm == "bfs":
            result = bfs(graph, center, target_node)
        else:
            result = dijkstra(graph, center, target_node)

        if result.found:
            if best_result is None or result.cost < best_result.cost:
                best_result = result
                best_center = center

    return best_result, best_center


# ──────────────────────────────────────────────
# Utilidad interna: costo de un camino
# ──────────────────────────────────────────────
def _path_cost(graph: RoadNetwork, path: list) -> float:
    """Calcula el costo total de un camino sumando los pesos de las aristas."""
    total = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        for neighbor, weight in graph.get_neighbors(u):
            if neighbor == v:
                total += weight
                break
    return total
