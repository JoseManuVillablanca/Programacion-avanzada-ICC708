"""
data_generator.py
Generador de datos sinteticos para el sistema de emergencias.

Genera:
  - Red vial: minimo 50 nodos y 100 aristas (grafo conectado).
  - Incidentes: minimo 500 registros variados.
  - Centros de emergencia: al menos 10 centros distribuidos en la red.

Los datos se guardan en archivos CSV en el directorio del proyecto.
NO utiliza librerias externas (ni random, usamos LCG propio).
"""

import os
import time


# ──────────────────────────────────────────────
# Generador Pseudo-Aleatorio (LCG)
# ──────────────────────────────────────────────
class LCG:
    """
    Generador de Congruencia Lineal (Linear Congruential Generator).
    Genera numeros pseudo-aleatorios sin usar el modulo random.

    Parametros Numerical Recipes:
        m = 2^32, a = 1664525, c = 1013904223
    """
    _A = 1664525
    _C = 1013904223
    _M = 2 ** 32

    def __init__(self, seed: int = None):
        self._state = seed if seed is not None else int(time.time() * 1000) % self._M

    def next_int(self) -> int:
        """Genera el siguiente entero pseudo-aleatorio en [0, M)."""
        self._state = (self._A * self._state + self._C) % self._M
        return self._state

    def randint(self, lo: int, hi: int) -> int:
        """Entero en [lo, hi] (inclusive)."""
        return lo + (self.next_int() % (hi - lo + 1))

    def random(self) -> float:
        """Float en [0.0, 1.0)."""
        return self.next_int() / self._M

    def choice(self, lst: list):
        """Elige un elemento aleatorio de una lista."""
        return lst[self.randint(0, len(lst) - 1)]

    def shuffle(self, lst: list):
        """Mezcla la lista in-place (Fisher-Yates)."""
        for i in range(len(lst) - 1, 0, -1):
            j = self.randint(0, i)
            lst[i], lst[j] = lst[j], lst[i]


# ──────────────────────────────────────────────
# Instancia global del RNG
# ──────────────────────────────────────────────
_rng = LCG(seed=42)


# ──────────────────────────────────────────────
# Parametros de generacion
# ──────────────────────────────────────────────
NUM_NODOS = 55
NUM_ARISTAS = 110
NUM_INCIDENTES = 500
NUM_CENTROS = 12

ZONAS = [
    "Centro", "Norte", "Sur", "Este", "Oeste",
    "Noreste", "Noroeste", "Sureste", "Suroeste", "Periferia"
]

TIPOS_ZONA = [
    "Comercial", "Residencial", "Industrial",
    "Hospitalaria", "Universitaria", "Rural"
]

TIPOS_INCIDENTE = [
    "Incendio", "Accidente_Vial", "Emergencia_Medica",
    "Robo", "Derrumbe", "Inundacion", "Explosion", "Rescate"
]

TIPOS_CENTRO = ["Hospital", "Bomberos", "Policia", "Rescate_Civil", "SAMU"]

NOMBRES_CENTROS = [
    "Centro Medico Norte", "Cuartel Bomberos Sur", "Comisaria Central",
    "Hospital Universitario", "Unidad SAMU Este", "Cuartel Rescate Oeste",
    "Hospital Periferia", "Comisaria Sur", "Hospital Emergencia Central",
    "Cuartel Norte", "Unidad SAMU Oeste", "Centro de Crisis"
]


# ──────────────────────────────────────────────
# Generadores de nodos y aristas
# ──────────────────────────────────────────────
def _generate_node_names(n: int) -> list:
    """
    Genera n nombres unicos de nodos de la red vial.
    Formato: 'Zona_N' o 'Zona_Tipo_N'.
    """
    nombres = []
    conteo = {}
    for i in range(n):
        zona = ZONAS[i % len(ZONAS)]
        tipo = TIPOS_ZONA[i % len(TIPOS_ZONA)]
        base = f"{zona}_{tipo}"
        conteo[base] = conteo.get(base, 0) + 1
        c = conteo[base]
        if c == 1:
            nombres.append(f"Nodo_{zona}_{tipo}")
        else:
            nombres.append(f"Nodo_{zona}_{tipo}_{c}")
    return nombres


def _generate_connected_graph(nodes: list, num_edges: int) -> list:
    """
    Genera una lista de aristas (u, v, peso) garantizando conectividad.

    Primero crea un arbol spanning (n-1 aristas) con los nodos en orden
    aleatorio, luego agrega aristas extras hasta completar num_edges.

    Retorna lista de tuplas (u, v, peso).
    """
    aristas = []
    n = len(nodes)
    shuffled = list(nodes)
    _rng.shuffle(shuffled)

    # Arbol de expansion minimo aleatorio (garantiza conectividad)
    for i in range(1, n):
        u = shuffled[i - 1]
        v = shuffled[i]
        peso = round(1.0 + _rng.random() * 29.0, 1)  # 1–30 minutos
        aristas.append((u, v, peso))

    # Aristas adicionales
    extra_needed = num_edges - (n - 1)
    attempts = 0
    existing = set()
    for u, v, _ in aristas:
        existing.add((u, v))
        existing.add((v, u))

    while extra_needed > 0 and attempts < num_edges * 10:
        attempts += 1
        u = _rng.choice(nodes)
        v = _rng.choice(nodes)
        if u == v or (u, v) in existing:
            continue
        peso = round(1.0 + _rng.random() * 29.0, 1)
        aristas.append((u, v, peso))
        existing.add((u, v))
        existing.add((v, u))
        extra_needed -= 1

    return aristas


# ──────────────────────────────────────────────
# Generadores de incidentes y centros
# ──────────────────────────────────────────────
def _generate_incidents(nodes: list, n: int) -> list:
    """
    Genera n incidentes sinteticos.

    Retorna lista de dicts con campos:
        incident_id, tipo, ubicacion, severidad, timestamp, estado
    """
    incidents = []
    now = time.time()
    for i in range(n):
        inc_id = f"INC-{i + 1:04d}"
        tipo = _rng.choice(TIPOS_INCIDENTE)
        ubicacion = _rng.choice(nodes)
        severidad = _rng.randint(1, 10)
        # timestamp: hasta 24 horas atras
        delta = _rng.random() * 86400
        ts = now - delta
        estado = _rng.choice(["reportado", "reportado", "reportado", "en_atencion"])
        incidents.append({
            "incident_id": inc_id,
            "tipo": tipo,
            "ubicacion": ubicacion,
            "severidad": str(severidad),
            "timestamp": str(round(ts, 2)),
            "estado": estado,
        })
    return incidents


def _generate_centers(nodes: list, n: int) -> list:
    """
    Genera n centros de emergencia distribuidos en la red.

    Retorna lista de dicts con campos:
        center_id, nombre, ubicacion, tipo, disponible
    """
    # Elegir nodos distintos para los centros (sin repetir si es posible)
    center_nodes = []
    available = list(nodes)
    _rng.shuffle(available)
    for i in range(min(n, len(available))):
        center_nodes.append(available[i])

    centers = []
    for i in range(n):
        cid = f"CEN-{i + 1:02d}"
        nombre = NOMBRES_CENTROS[i % len(NOMBRES_CENTROS)]
        tipo = TIPOS_CENTRO[i % len(TIPOS_CENTRO)]
        ubicacion = center_nodes[i % len(center_nodes)]
        centers.append({
            "center_id": cid,
            "nombre": nombre,
            "ubicacion": ubicacion,
            "tipo": tipo,
            "disponible": "True",
        })
    return centers


# ──────────────────────────────────────────────
# Escritura de CSV (sin libreria csv)
# ──────────────────────────────────────────────
def _write_csv(filepath: str, header: list, rows: list):
    """Escribe un archivo CSV manualmente sin usar el modulo csv."""
    lines = [",".join(header)]
    for row in rows:
        fields = []
        for h in header:
            val = str(row.get(h, ""))
            # Escapar comas y comillas si es necesario
            if "," in val or '"' in val:
                val = '"' + val.replace('"', '""') + '"'
            fields.append(val)
        lines.append(",".join(fields))
    content = "\n".join(lines) + "\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return len(rows)


# ──────────────────────────────────────────────
# Lectura de CSV (sin libreria csv)
# ──────────────────────────────────────────────
def read_csv(filepath: str) -> tuple:
    """
    Lee un archivo CSV manualmente.

    Retorna (header: list, rows: list of dicts).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    if not lines:
        return [], []

    header = _parse_csv_line(lines[0])
    rows = []
    for line in lines[1:]:
        if line.strip():
            values = _parse_csv_line(line)
            row = {}
            for i, h in enumerate(header):
                row[h] = values[i] if i < len(values) else ""
            rows.append(row)
    return header, rows


def _parse_csv_line(line: str) -> list:
    """Parsea una linea CSV respetando campos entre comillas."""
    fields = []
    current = ""
    in_quotes = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                current += '"'
                i += 2
                continue
            in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            fields.append(current)
            current = ""
        else:
            current += ch
        i += 1
    fields.append(current)
    return fields


# ──────────────────────────────────────────────
# Funcion principal de generacion
# ──────────────────────────────────────────────
def generate_all(output_dir: str = ".") -> dict:
    """
    Genera todos los archivos de datos y los guarda en output_dir.

    Retorna un diccionario con las rutas de los archivos generados y
    el conteo de registros.
    """
    os.makedirs(output_dir, exist_ok=True)

    print("Generando datos sinteticos...")

    # 1. Nodos
    nodes = _generate_node_names(NUM_NODOS)
    print(f"  Nodos generados          : {len(nodes)}")

    # 2. Aristas (red vial)
    edges = _generate_connected_graph(nodes, NUM_ARISTAS)
    print(f"  Aristas generadas        : {len(edges)}")

    # 3. Incidentes
    incidents = _generate_incidents(nodes, NUM_INCIDENTES)
    print(f"  Incidentes generados     : {len(incidents)}")

    # 4. Centros de emergencia
    centers = _generate_centers(nodes, NUM_CENTROS)
    print(f"  Centros generados        : {len(centers)}")

    # 5. Guardar CSVs
    nodos_path = os.path.join(output_dir, "nodos.csv")
    nodos_rows = [{"nodo": n} for n in nodes]
    _write_csv(nodos_path, ["nodo"], nodos_rows)

    aristas_path = os.path.join(output_dir, "aristas.csv")
    aristas_rows = [{"origen": u, "destino": v, "peso": str(w)}
                    for u, v, w in edges]
    _write_csv(aristas_path, ["origen", "destino", "peso"], aristas_rows)

    incidentes_path = os.path.join(output_dir, "incidentes.csv")
    _write_csv(incidentes_path,
               ["incident_id", "tipo", "ubicacion", "severidad",
                "timestamp", "estado"],
               incidents)

    centros_path = os.path.join(output_dir, "centros.csv")
    _write_csv(centros_path,
               ["center_id", "nombre", "ubicacion", "tipo", "disponible"],
               centers)

    print("\n  Archivos guardados:")
    for label, path in [("Nodos", nodos_path), ("Aristas", aristas_path),
                        ("Incidentes", incidentes_path),
                        ("Centros", centros_path)]:
        print(f"    [{label}] {path}")

    return {
        "nodos_path": nodos_path,
        "aristas_path": aristas_path,
        "incidentes_path": incidentes_path,
        "centros_path": centros_path,
        "num_nodes": len(nodes),
        "num_edges": len(edges),
        "num_incidents": len(incidents),
        "num_centers": len(centers),
    }


# ──────────────────────────────────────────────
# Ejecucion directa
# ──────────────────────────────────────────────
if __name__ == "__main__":
    generate_all(output_dir=".")
