"""
models.py
Modulo de modelos y estructuras de datos base (ADTs) para el sistema de
gestion y optimizacion de rutas de emergencia.

No utiliza librerias externas.
"""

import time


# ──────────────────────────────────────────────
# Constantes de Tipo de Incidente
# ──────────────────────────────────────────────
TIPOS_INCIDENTE = [
    "Incendio",
    "Accidente_Vial",
    "Emergencia_Medica",
    "Robo",
    "Derrumbe",
    "Inundacion",
    "Explosion",
    "Rescate",
]

ESTADOS_INCIDENTE = ("reportado", "en_atencion", "resuelto")


# ──────────────────────────────────────────────
# Clase Incident
# ──────────────────────────────────────────────
class Incident:
    """
    Representa un incidente de emergencia registrado en el sistema.

    Atributos
    ---------
    incident_id : str
        Identificador unico del incidente (ej. 'INC-0001').
    tipo : str
        Categoria del incidente (Incendio, Accidente_Vial, etc.).
    ubicacion : str
        Nodo de la red vial donde ocurre el incidente.
    severidad : int
        Nivel de severidad del 1 (leve) al 10 (critico).
    timestamp : float
        Marca de tiempo Unix en que fue reportado.
    estado : str
        Estado actual: 'reportado', 'en_atencion' o 'resuelto'.
    """

    # Pesos de severidad por tipo (para calculo de prioridad)
    _PESO_TIPO = {
        "Incendio":         1.5,
        "Accidente_Vial":   1.3,
        "Emergencia_Medica": 1.8,
        "Robo":             1.0,
        "Derrumbe":         1.4,
        "Inundacion":       1.2,
        "Explosion":        2.0,
        "Rescate":          1.6,
    }

    def __init__(self, incident_id: str, tipo: str, ubicacion: str,
                 severidad: int, timestamp: float = None,
                 estado: str = "reportado"):
        if estado not in ESTADOS_INCIDENTE:
            raise ValueError(f"Estado invalido '{estado}'. "
                             f"Use: {ESTADOS_INCIDENTE}")
        if not (1 <= severidad <= 10):
            raise ValueError("La severidad debe estar entre 1 y 10.")

        self.incident_id = incident_id
        self.tipo = tipo
        self.ubicacion = ubicacion
        self.severidad = severidad
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.estado = estado
        self.prioridad = self._calcular_prioridad()

    def _calcular_prioridad(self) -> float:
        """
        Calcula la prioridad numerica del incidente.

        Formula:
            prioridad = severidad * peso_tipo * factor_tiempo

        El factor_tiempo penaliza incidentes mas antiguos: a mayor tiempo
        transcurrido, mas urge su atencion (factor crece con la edad).
        """
        peso = self._PESO_TIPO.get(self.tipo, 1.0)
        # Factor tiempo: cada minuto sin atencion incrementa la urgencia
        minutos_transcurridos = (time.time() - self.timestamp) / 60.0
        factor_tiempo = 1.0 + (minutos_transcurridos * 0.05)
        return round(self.severidad * peso * factor_tiempo, 4)

    def actualizar_prioridad(self):
        """Recalcula y actualiza la prioridad segun el tiempo actual."""
        self.prioridad = self._calcular_prioridad()

    def cambiar_estado(self, nuevo_estado: str):
        """Actualiza el estado del incidente."""
        if nuevo_estado not in ESTADOS_INCIDENTE:
            raise ValueError(f"Estado invalido '{nuevo_estado}'.")
        self.estado = nuevo_estado

    def __repr__(self):
        return (f"Incident(id={self.incident_id!r}, tipo={self.tipo!r}, "
                f"ubicacion={self.ubicacion!r}, severidad={self.severidad}, "
                f"prioridad={self.prioridad:.4f}, estado={self.estado!r})")

    def __lt__(self, other):
        """Permite comparacion para el heap (prioridad menor = menos urgente)."""
        return self.prioridad < other.prioridad

    def __le__(self, other):
        return self.prioridad <= other.prioridad

    def __gt__(self, other):
        return self.prioridad > other.prioridad

    def __ge__(self, other):
        return self.prioridad >= other.prioridad

    def __eq__(self, other):
        if isinstance(other, Incident):
            return self.incident_id == other.incident_id
        return False


# ──────────────────────────────────────────────
# Clase EmergencyCenter
# ──────────────────────────────────────────────
class EmergencyCenter:
    """
    Representa un centro de operaciones de emergencia (hospital, cuartel, etc.)
    disponible para responder a incidentes.

    Atributos
    ---------
    center_id : str
        Identificador unico del centro (ej. 'CEN-01').
    nombre : str
        Nombre descriptivo del centro.
    ubicacion : str
        Nodo de la red vial donde se encuentra el centro.
    tipo : str
        Categoria del centro ('Hospital', 'Bomberos', 'Policia', etc.).
    disponible : bool
        Indica si el centro puede asumir un nuevo incidente.
    """

    TIPOS_CENTRO = ("Hospital", "Bomberos", "Policia", "Rescate_Civil", "SAMU")

    def __init__(self, center_id: str, nombre: str, ubicacion: str,
                 tipo: str = "Hospital", disponible: bool = True):
        self.center_id = center_id
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.tipo = tipo
        self.disponible = disponible
        self.incidentes_atendidos = 0

    def asignar(self):
        """Marca el centro como ocupado tras asignarle un incidente."""
        self.disponible = False
        self.incidentes_atendidos += 1

    def liberar(self):
        """Marca el centro como disponible nuevamente."""
        self.disponible = True

    def __repr__(self):
        estado = "Disponible" if self.disponible else "Ocupado"
        return (f"EmergencyCenter(id={self.center_id!r}, "
                f"nombre={self.nombre!r}, ubicacion={self.ubicacion!r}, "
                f"tipo={self.tipo!r}, estado={estado})")


# ──────────────────────────────────────────────
# Clase RoadNetwork (Grafo de Red Vial)
# ──────────────────────────────────────────────
class RoadNetwork:
    """
    Representa la red vial como un grafo ponderado no dirigido (o dirigido).
    Internamente usa listas de adyacencia implementadas con listas de Python.

    Cada nodo es una cadena de texto (nombre de zona/interseccion).
    Cada arista tiene un peso numerico (tiempo de desplazamiento en minutos).
    """

    def __init__(self, dirigido: bool = False):
        """
        Parametros
        ----------
        dirigido : bool
            Si es True, las aristas son unidireccionales.
        """
        self.dirigido = dirigido
        # _adj almacena: { nodo_str -> lista de (vecino_str, peso_float) }
        # Usamos listas de tuplas; NO usamos dict pero si la estructura de
        # indice de nodos para mapear nombres a indices en la lista _nodes.
        self._nodes = []           # lista de nombres de nodos (str)
        self._adj = []             # lista paralela de listas de (idx, peso)
        self._node_index = []      # lista de pares (nombre, indice) – manual
        self.num_edges = 0

    # ── Metodos internos de busqueda de indice ──
    def _find_node_idx(self, name: str):
        """Retorna el indice del nodo con ese nombre, o -1 si no existe."""
        for i, n in enumerate(self._nodes):
            if n == name:
                return i
        return -1

    # ── Interfaz publica ──
    def add_node(self, name: str):
        """Agrega un nodo a la red. Ignora duplicados."""
        if self._find_node_idx(name) == -1:
            self._nodes.append(name)
            self._adj.append([])

    def add_edge(self, u: str, v: str, weight: float):
        """
        Agrega una arista entre los nodos u y v con el peso indicado.
        Si algun nodo no existe, lo crea automaticamente.
        """
        self.add_node(u)
        self.add_node(v)
        ui = self._find_node_idx(u)
        vi = self._find_node_idx(v)
        self._adj[ui].append((vi, weight))
        if not self.dirigido:
            self._adj[vi].append((ui, weight))
        self.num_edges += 1

    def get_neighbors(self, name: str):
        """
        Retorna la lista de vecinos de un nodo como tuplas (nombre, peso).

        Parametros
        ----------
        name : str
            Nombre del nodo origen.

        Retorna
        -------
        list de (str, float)
        """
        idx = self._find_node_idx(name)
        if idx == -1:
            return []
        return [(self._nodes[ni], w) for ni, w in self._adj[idx]]

    def node_exists(self, name: str) -> bool:
        return self._find_node_idx(name) != -1

    def get_all_nodes(self):
        """Retorna una copia de la lista de nodos."""
        return list(self._nodes)

    def get_num_nodes(self) -> int:
        return len(self._nodes)

    def get_num_edges(self) -> int:
        return self.num_edges

    def __repr__(self):
        return (f"RoadNetwork(nodes={len(self._nodes)}, "
                f"edges={self.num_edges}, dirigido={self.dirigido})")
