"""
priority_queue.py
Implementacion de una Cola de Prioridad basada en un Max-Heap propio.

NO utiliza heapq ni ninguna libreria externa.

El heap almacena objetos Incident y los extrae en orden de mayor
prioridad primero (Max-Heap).

Para soportar update_priority eficiente, el heap mantiene un indice
de posiciones implementado como lista de tuplas (incident_id, index).
"""

from models import Incident


class MaxHeap:
    """
    Max-Heap generico que mantiene el elemento de mayor prioridad en la raiz.

    Almacena objetos Incident y los compara por su atributo `prioridad`.
    """

    def __init__(self):
        self._heap = []          # lista interna del heap
        # Indice de posiciones: lista de pares (incident_id, indice_en_heap)
        # Implementado manualmente como lista de tuplas.
        self._pos_index = []     # [(incident_id_str, int), ...]

    # ──────────────────────────────────────────────
    # Operaciones de indice de posiciones (manual)
    # ──────────────────────────────────────────────
    def _index_get(self, incident_id: str) -> int:
        """Retorna el indice en el heap del incidente dado, o -1 si no existe."""
        for iid, pos in self._pos_index:
            if iid == incident_id:
                return pos
        return -1

    def _index_set(self, incident_id: str, pos: int):
        """Actualiza o inserta la posicion de un incidente en el indice."""
        for i, (iid, _) in enumerate(self._pos_index):
            if iid == incident_id:
                self._pos_index[i] = (incident_id, pos)
                return
        self._pos_index.append((incident_id, pos))

    def _index_remove(self, incident_id: str):
        """Elimina la entrada del incidente del indice de posiciones."""
        for i, (iid, _) in enumerate(self._pos_index):
            if iid == incident_id:
                self._pos_index.pop(i)
                return

    # ──────────────────────────────────────────────
    # Utilidades de posicion en arbol binario
    # ──────────────────────────────────────────────
    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    # ──────────────────────────────────────────────
    # Operaciones de sift (re-heapificacion)
    # ──────────────────────────────────────────────
    def _swap(self, i: int, j: int):
        """Intercambia dos elementos en el heap y actualiza el indice."""
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._index_set(self._heap[i].incident_id, i)
        self._index_set(self._heap[j].incident_id, j)

    def _sift_up(self, i: int):
        """
        Sube el elemento en posicion i hasta su lugar correcto en el Max-Heap.
        Precondicion: todos los elementos excepto i cumplen la propiedad.
        """
        while i > 0:
            p = self._parent(i)
            if self._heap[i].prioridad > self._heap[p].prioridad:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i: int):
        """
        Baja el elemento en posicion i hasta su lugar correcto en el Max-Heap.
        """
        n = len(self._heap)
        while True:
            largest = i
            l = self._left(i)
            r = self._right(i)

            if l < n and self._heap[l].prioridad > self._heap[largest].prioridad:
                largest = l
            if r < n and self._heap[r].prioridad > self._heap[largest].prioridad:
                largest = r

            if largest != i:
                self._swap(i, largest)
                i = largest
            else:
                break

    # ──────────────────────────────────────────────
    # Interfaz publica
    # ──────────────────────────────────────────────
    def insert(self, incident: Incident):
        """
        Inserta un incidente en el heap.
        Complejidad: O(log n)
        """
        pos = len(self._heap)
        self._heap.append(incident)
        self._index_set(incident.incident_id, pos)
        self._sift_up(pos)

    def peek_max(self) -> Incident:
        """
        Retorna el incidente de mayor prioridad SIN extraerlo.

        Retorna None si el heap esta vacio.
        Complejidad: O(1)
        """
        if not self._heap:
            return None
        return self._heap[0]

    def extract_max(self) -> Incident:
        """
        Extrae y retorna el incidente de mayor prioridad.

        Retorna None si el heap esta vacio.
        Complejidad: O(log n)
        """
        if not self._heap:
            return None

        # Intercambiar raiz con el ultimo elemento
        self._swap(0, len(self._heap) - 1)
        max_incident = self._heap.pop()
        self._index_remove(max_incident.incident_id)

        if self._heap:
            self._sift_down(0)

        return max_incident

    def update_priority(self, incident_id: str, new_prioridad: float) -> bool:
        """
        Actualiza la prioridad de un incidente y reubica en el heap.

        Retorna True si el incidente fue encontrado y actualizado.
        Complejidad: O(log n)
        """
        pos = self._index_get(incident_id)
        if pos == -1:
            return False

        old_prioridad = self._heap[pos].prioridad
        self._heap[pos].prioridad = new_prioridad

        if new_prioridad > old_prioridad:
            self._sift_up(pos)
        else:
            self._sift_down(pos)

        return True

    def show_top_k(self, k: int) -> list:
        """
        Retorna los k incidentes de mayor prioridad SIN modificar el heap.
        Implementado creando una copia parcial del heap y extrayendo k veces.

        Retorna una lista de objetos Incident ordenada de mayor a menor prioridad.
        Complejidad: O(k log n)
        """
        # Usamos un heap temporal para no destruir el original
        temp = MaxHeap()
        for inc in self._heap:
            temp.insert(inc)

        result = []
        for _ in range(min(k, len(self._heap))):
            top = temp.extract_max()
            if top:
                result.append(top)
        return result

    def build_from_list(self, incidents: list):
        """
        Construye el heap a partir de una lista de incidentes.
        Usa el algoritmo de heapificacion Floyd en O(n).
        """
        self._heap = list(incidents)
        self._pos_index = []
        for i, inc in enumerate(self._heap):
            self._pos_index.append((inc.incident_id, i))

        # Sift-down desde el ultimo nodo interno hacia arriba
        n = len(self._heap)
        for i in range((n - 2) // 2, -1, -1):
            self._sift_down(i)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)

    def __len__(self):
        return len(self._heap)

    def __repr__(self):
        top = self._heap[0] if self._heap else None
        return (f"MaxHeap(size={len(self._heap)}, "
                f"max={top.prioridad if top else 'N/A'})")
