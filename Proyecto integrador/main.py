"""
main.py
Punto de entrada principal del Sistema Inteligente de Gestion y
Optimizacion de Rutas de Emergencia.

Ejecuta:
  1. Generacion de datos (CSV) si no existen.
  2. Carga de datos desde CSV.
  3. Construccion del grafo de red vial.
  4. Insercion de incidentes en Tabla Hash y Cola de Prioridad.
  5. Menu interactivo para gestionar incidentes, calcular rutas y generar reportes.
  6. Analisis experimental comparativo.

No utiliza librerias externas.
"""

import os
import time

from models import Incident, EmergencyCenter, RoadNetwork, TIPOS_INCIDENTE
from hash_table import HashTable
from priority_queue import MaxHeap
from sorting import merge_sort, quick_sort, key_prioridad, key_timestamp
from search_algorithms import bfs, dijkstra, astar, find_nearest_center
from data_generator import generate_all, read_csv


# ==============================================
# Utilidades de presentacion
# ==============================================

def _separator(char="=", width=60):
    print(char * width)

def _header(title: str, width=60):
    _separator(width=width)
    padding = max(0, (width - len(title) - 2) // 2)
    print(" " * padding + f" {title} ")
    _separator(width=width)

def _print_incident(inc: Incident, prefix="  "):
    print(f"{prefix}ID         : {inc.incident_id}")
    print(f"{prefix}Tipo       : {inc.tipo}")
    print(f"{prefix}Ubicacion  : {inc.ubicacion}")
    print(f"{prefix}Severidad  : {inc.severidad}/10")
    print(f"{prefix}Prioridad  : {inc.prioridad:.4f}")
    print(f"{prefix}Estado     : {inc.estado}")

def _format_time(seconds: float) -> str:
    """Formatea segundos en una cadena legible."""
    if seconds < 1e-3:
        return f"{seconds * 1_000_000:.2f} us"
    elif seconds < 1.0:
        return f"{seconds * 1_000:.4f} ms"
    else:
        return f"{seconds:.6f} s"


# ==============================================
# PASO 1: Carga de datos
# ==============================================

def load_data(data_dir: str = ".") -> tuple:
    """
    Carga los datos desde los archivos CSV.

    Retorna (graph, incidents_list, centers_list).
    """
    nodos_path     = os.path.join(data_dir, "nodos.csv")
    aristas_path   = os.path.join(data_dir, "aristas.csv")
    incidentes_path = os.path.join(data_dir, "incidentes.csv")
    centros_path   = os.path.join(data_dir, "centros.csv")

    # Verificar que existan
    for p in [nodos_path, aristas_path, incidentes_path, centros_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Archivo no encontrado: {p}")

    # -- Grafo --
    graph = RoadNetwork(dirigido=False)

    _, nodo_rows = read_csv(nodos_path)
    for row in nodo_rows:
        graph.add_node(row["nodo"])

    _, arista_rows = read_csv(aristas_path)
    for row in arista_rows:
        graph.add_edge(row["origen"], row["destino"], float(row["peso"]))

    # -- Incidentes --
    _, inc_rows = read_csv(incidentes_path)
    incidents = []
    for row in inc_rows:
        inc = Incident(
            incident_id=row["incident_id"],
            tipo=row["tipo"],
            ubicacion=row["ubicacion"],
            severidad=int(row["severidad"]),
            timestamp=float(row["timestamp"]),
            estado=row["estado"],
        )
        incidents.append(inc)

    # -- Centros --
    _, cen_rows = read_csv(centros_path)
    centers = []
    for row in cen_rows:
        cen = EmergencyCenter(
            center_id=row["center_id"],
            nombre=row["nombre"],
            ubicacion=row["ubicacion"],
            tipo=row["tipo"],
            disponible=(row["disponible"].strip() == "True"),
        )
        centers.append(cen)

    return graph, incidents, centers


# ==============================================
# PASO 2: Insercion en estructuras de datos
# ==============================================

def build_structures(incidents: list) -> tuple:
    """
    Construye la Tabla Hash y el Max-Heap con los incidentes dados.

    Retorna (hash_table, max_heap, insert_time_ht, insert_time_heap).
    """
    ht = HashTable()
    heap = MaxHeap()

    t0 = time.perf_counter()
    for inc in incidents:
        ht.insert(inc.incident_id, inc)
    t_ht = time.perf_counter() - t0

    t0 = time.perf_counter()
    heap.build_from_list(incidents)
    t_heap = time.perf_counter() - t0

    return ht, heap, t_ht, t_heap


# ==============================================
# PASO 3: Escenario integrado
# ==============================================

def run_emergency_scenario(graph: RoadNetwork, heap: MaxHeap,
                           ht: HashTable, centers: list):
    """
    Ejecuta el escenario principal de respuesta de emergencia:
      1. Extraer el incidente mas urgente.
      2. Encontrar el centro disponible mas cercano.
      3. Calcular ruta optima (Dijkstra) y alternativa (BFS).
      4. Mostrar resultados completos.
    """
    _header("ESCENARIO DE RESPUESTA A EMERGENCIA")
    print()

    # -- 3.1 Extraer incidente mas urgente --
    most_urgent = heap.extract_max()
    if most_urgent is None:
        print("  [!] No hay incidentes en la cola.")
        return

    most_urgent.actualizar_prioridad()
    print(">> Incidente mas urgente detectado:")
    _print_incident(most_urgent)
    print()

    # Actualizar estado en la Tabla Hash
    most_urgent.cambiar_estado("en_atencion")
    ht.update(most_urgent.incident_id, most_urgent)
    print(f"  Estado actualizado a 'en_atencion' en la Tabla Hash.")
    print()

    # -- 3.2 Centros disponibles --
    available_centers = [c for c in centers if c.disponible]
    if not available_centers:
        print("  [!] No hay centros de emergencia disponibles.")
        return

    center_nodes = [c.ubicacion for c in available_centers]
    print(f">> Centros de emergencia disponibles : {len(available_centers)}")

    # -- 3.3 Buscar ruta optima con Dijkstra --
    print()
    print(">> Buscando ruta optima (Dijkstra/UCS)...")
    t0 = time.perf_counter()
    result_dijk, best_center_dijk = find_nearest_center(
        graph, most_urgent.ubicacion, center_nodes, algorithm="dijkstra"
    )
    t_dijk = time.perf_counter() - t0

    print(">> Buscando ruta alternativa (BFS)...")
    t0 = time.perf_counter()
    result_bfs, best_center_bfs = find_nearest_center(
        graph, most_urgent.ubicacion, center_nodes, algorithm="bfs"
    )
    t_bfs = time.perf_counter() - t0

    # -- 3.4 Mostrar resultados --
    _separator("-", width=60)
    print("  RESULTADO DE BUSQUEDA DE RUTA")
    _separator("-", width=60)

    if result_dijk and result_dijk.found:
        # Encontrar nombre del centro
        cen_dijk = next((c for c in available_centers
                         if c.ubicacion == best_center_dijk), None)
        cen_name = cen_dijk.nombre if cen_dijk else best_center_dijk

        print(f"\n  [Dijkstra/UCS]")
        print(f"  Centro asignado  : {cen_name} ({best_center_dijk})")
        print(f"  Ruta sugerida    : {' -> '.join(result_dijk.path)}")
        print(f"  Saltos (aristas) : {result_dijk.hops}")
        print(f"  Tiempo de viaje  : {result_dijk.cost:.2f} min")
        print(f"  Nodos explorados : {result_dijk.visited}")
        print(f"  Tiempo ejecucion : {_format_time(t_dijk)}")
    else:
        print("\n  [Dijkstra] No se encontro ruta.")

    if result_bfs and result_bfs.found:
        cen_bfs = next((c for c in available_centers
                        if c.ubicacion == best_center_bfs), None)
        cen_name = cen_bfs.nombre if cen_bfs else best_center_bfs

        print(f"\n  [BFS]")
        print(f"  Centro asignado  : {cen_name} ({best_center_bfs})")
        print(f"  Ruta sugerida    : {' -> '.join(result_bfs.path)}")
        print(f"  Saltos (aristas) : {result_bfs.hops}")
        print(f"  Costo de la ruta : {result_bfs.cost:.2f} min")
        print(f"  Nodos explorados : {result_bfs.visited}")
        print(f"  Tiempo ejecucion : {_format_time(t_bfs)}")
    else:
        print("\n  [BFS] No se encontro ruta.")

    # -- 3.5 Asignar el centro optimo --
    if result_dijk and result_dijk.found:
        cen_asignado = next((c for c in available_centers
                             if c.ubicacion == best_center_dijk), None)
        if cen_asignado:
            cen_asignado.asignar()
            print(f"\n  [OK] Centro '{cen_asignado.nombre}' asignado al incidente "
                  f"{most_urgent.incident_id}.")

    print()


# ==============================================
# PASO 4: Analisis Experimental
# ==============================================

def run_experimental_analysis(incidents: list, graph: RoadNetwork,
                               centers: list):
    """
    Realiza el analisis experimental comparativo:
      A. Tiempos de insercion/extraccion en Heap vs tamano.
      B. MergeSort vs QuickSort por prioridad y timestamp.
      C. Comparacion BFS vs Dijkstra en multiples pares origen-destino.
      D. Metricas finales de la Tabla Hash.
    """
    _header("ANALISIS EXPERIMENTAL")

    # -- A. Rendimiento del Heap --
    print("\n[A] Rendimiento del Max-Heap (insercion + extraccion)")
    _separator("-", width=60)
    print(f"  {'Tamano':>8} | {'T_insert (ms)':>14} | {'T_extract (ms)':>15}")
    _separator("-", width=60)

    sizes = [100, 200, 300, 400, 500]
    for size in sizes:
        sample = incidents[:size]

        # Insercion individual
        h = MaxHeap()
        t0 = time.perf_counter()
        for inc in sample:
            h.insert(inc)
        t_ins = (time.perf_counter() - t0) * 1000

        # Extraccion total
        t0 = time.perf_counter()
        while not h.is_empty():
            h.extract_max()
        t_ext = (time.perf_counter() - t0) * 1000

        print(f"  {size:>8} | {t_ins:>14.4f} | {t_ext:>15.4f}")

    # -- B. MergeSort vs QuickSort --
    print(f"\n[B] MergeSort vs QuickSort (n={len(incidents)} incidentes)")
    _separator("-", width=60)
    print(f"  {'Criterio':>15} | {'MergeSort (ms)':>14} | {'QuickSort (ms)':>14}")
    _separator("-", width=60)

    criterios = [
        ("Prioridad desc", key_prioridad, True),
        ("Timestamp asc", key_timestamp, False),
    ]
    for nombre, kf, rev in criterios:
        t0 = time.perf_counter()
        _ = merge_sort(incidents, key_func=kf, reverse=rev)
        t_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        _ = quick_sort(incidents, key_func=kf, reverse=rev)
        t_qs = (time.perf_counter() - t0) * 1000

        print(f"  {nombre:>15} | {t_ms:>14.4f} | {t_qs:>14.4f}")

    # -- C. BFS vs Dijkstra --
    all_nodes = graph.get_all_nodes()

    # Elegir 5 pares de origen-destino representativos
    test_pairs = []
    step = max(1, len(all_nodes) // 6)
    for i in range(0, min(5 * step, len(all_nodes) - step), step):
        src = all_nodes[i]
        dst = all_nodes[(i + step) % len(all_nodes)]
        test_pairs.append((src, dst))

    print(f"\n[C] BFS vs Dijkstra - 5 pares de nodos")
    _separator("-", width=60)
    print(f"  {'Origen -> Destino':>30} | {'BFS cost':>9} | "
          f"{'UCS cost':>9} | {'BFS vis':>7} | {'UCS vis':>7}")
    _separator("-", width=60)

    for src, dst in test_pairs:
        rb = bfs(graph, src, dst)
        rd = dijkstra(graph, src, dst)
        pair_label = f"{src[:12]} -> {dst[:12]}"
        bc = f"{rb.cost:.1f}" if rb.found else "N/A"
        dc = f"{rd.cost:.1f}" if rd.found else "N/A"
        print(f"  {pair_label:>30} | {bc:>9} | {dc:>9} | "
              f"{rb.visited:>7} | {rd.visited:>7}")

    # -- D. Metricas Tabla Hash --
    print(f"\n[D] Metricas de la Tabla Hash (con {len(incidents)} incidentes)")
    ht_exp = HashTable()
    for inc in incidents:
        ht_exp.insert(inc.incident_id, inc)
    ht_exp.print_metrics()

    # -- E. Top-10 incidentes mas urgentes --
    heap_final = MaxHeap()
    heap_final.build_from_list(incidents)
    top10 = heap_final.show_top_k(10)

    print(f"\n[E] Top-10 Incidentes Mas Urgentes")
    _separator("-", width=60)
    print(f"  {'#':>3}  {'ID':>10}  {'Tipo':>20}  {'Prio':>8}  {'Sev':>5}")
    _separator("-", width=60)
    for i, inc in enumerate(top10, 1):
        print(f"  {i:>3}  {inc.incident_id:>10}  {inc.tipo:>20}  "
              f"{inc.prioridad:>8.4f}  {inc.severidad:>5}")

    print()


# ==============================================
# MENU INTERACTIVO - Funciones auxiliares
# ==============================================

def _menu_registrar(graph, incidents, ht, heap):
    """Opcion 1: Registrar un nuevo incidente."""
    print("\n--- REGISTRAR NUEVO INCIDENTE ---")
    iid = input("ID del incidente (ej: INC-1001): ").strip()
    if not iid:
        print("[!] ID vacio. Operacion cancelada.")
        return

    if ht.contains(iid):
        print(f"[!] Ya existe un incidente con ID '{iid}'.")
        return

    print("Tipos disponibles:")
    for idx, t in enumerate(TIPOS_INCIDENTE, 1):
        print(f"  {idx}. {t}")
    try:
        tipo_idx = int(input("Seleccione tipo (numero): "))
        tipo = TIPOS_INCIDENTE[tipo_idx - 1]
    except (ValueError, IndexError):
        print("[!] Seleccion invalida. Operacion cancelada.")
        return

    all_nodes = graph.get_all_nodes()
    print(f"\nNodos disponibles ({len(all_nodes)} en total, mostrando primeros 20):")
    for idx, n in enumerate(all_nodes[:20], 1):
        print(f"  {idx:>2}. {n}")
    if len(all_nodes) > 20:
        print(f"  ... y {len(all_nodes) - 20} nodos mas.")
    ubicacion = input("Nombre del nodo de ubicacion: ").strip()
    if not graph.node_exists(ubicacion):
        print(f"[!] El nodo '{ubicacion}' no existe en la red vial.")
        return

    try:
        severidad = int(input("Severidad (1-10): "))
        if not (1 <= severidad <= 10):
            raise ValueError()
    except ValueError:
        print("[!] Severidad invalida. Debe ser un entero entre 1 y 10.")
        return

    new_inc = Incident(iid, tipo, ubicacion, severidad)
    incidents.append(new_inc)
    ht.insert(iid, new_inc)
    heap.insert(new_inc)
    print(f"\n[OK] Incidente '{iid}' registrado.")
    print(f"     Tipo      : {tipo}")
    print(f"     Ubicacion : {ubicacion}")
    print(f"     Severidad : {severidad}/10")
    print(f"     Prioridad : {new_inc.prioridad:.4f}")


def _menu_buscar(ht):
    """Opcion 2: Buscar incidente por ID (O(1) en Tabla Hash)."""
    print("\n--- BUSCAR INCIDENTE POR ID ---")
    iid = input("ID del incidente: ").strip()
    t0 = time.perf_counter()
    inc = ht.search(iid)
    t_search = time.perf_counter() - t0
    if inc:
        inc.actualizar_prioridad()
        _print_incident(inc)
        print(f"  Tiempo de busqueda (Tabla Hash) : {_format_time(t_search)}")
    else:
        print(f"[!] Incidente '{iid}' no encontrado.")


def _menu_actualizar(incidents, ht, heap):
    """Opcion 3: Actualizar estado de un incidente."""
    print("\n--- ACTUALIZAR ESTADO DE INCIDENTE ---")
    iid = input("ID del incidente: ").strip()
    inc = ht.search(iid)
    if not inc:
        print(f"[!] Incidente '{iid}' no encontrado.")
        return

    print("\nEstado actual:")
    _print_incident(inc)
    print("\nNuevo estado:")
    print("  1. reportado")
    print("  2. en_atencion")
    print("  3. resuelto")
    opc = input("Seleccione (numero): ").strip()
    estados = {"1": "reportado", "2": "en_atencion", "3": "resuelto"}
    nuevo_estado = estados.get(opc)
    if not nuevo_estado:
        print("[!] Opcion invalida.")
        return

    inc.cambiar_estado(nuevo_estado)
    inc.actualizar_prioridad()
    ht.update(iid, inc)
    heap.build_from_list(incidents)
    print(f"[OK] Estado actualizado a '{nuevo_estado}'. Nueva prioridad: {inc.prioridad:.4f}")


def _menu_eliminar(incidents, ht, heap):
    """Opcion 4: Eliminar un incidente."""
    print("\n--- ELIMINAR INCIDENTE ---")
    iid = input("ID del incidente a eliminar: ").strip()
    if not ht.contains(iid):
        print(f"[!] Incidente '{iid}' no encontrado.")
        return

    confirmacion = input(f"Confirmar eliminacion de '{iid}' (s/n): ").strip().lower()
    if confirmacion != "s":
        print("Operacion cancelada.")
        return

    ht.delete(iid)
    for i, inc in enumerate(incidents):
        if inc.incident_id == iid:
            incidents.pop(i)
            break
    heap.build_from_list(incidents)
    print(f"[OK] Incidente '{iid}' eliminado correctamente.")


def _menu_mas_urgente(heap):
    """Opcion 5: Ver (sin extraer) el incidente mas urgente."""
    print("\n--- INCIDENTE MAS URGENTE (PEEK) ---")
    inc = heap.peek_max()
    if inc:
        inc.actualizar_prioridad()
        print(">> Incidente en la cima del MaxHeap:")
        _print_incident(inc)
    else:
        print("[!] La cola de prioridad esta vacia.")


def _menu_zonas(incidents):
    """Opcion 7: Analizar zonas afectadas por frecuencia de incidentes."""
    print("\n--- ANALIZAR ZONAS AFECTADAS ---")
    # Conteo manual de frecuencias por nodo (sin dict nativo)
    zonas = []
    for inc in incidents:
        encontrado = False
        for item in zonas:
            if item[0] == inc.ubicacion:
                item[1] += 1
                encontrado = True
                break
        if not encontrado:
            zonas.append([inc.ubicacion, 1])

    # Ordenar por frecuencia descendente usando QuickSort propio
    sorted_zonas = quick_sort(zonas, key_func=lambda x: x[1], reverse=True)

    print(f"\n  Total de zonas con incidentes : {len(sorted_zonas)}")
    _separator("-", width=60)
    print(f"  {'#':>3}  {'Zona':<35}  {'Incidentes':>10}")
    _separator("-", width=60)
    for i, (zona, freq) in enumerate(sorted_zonas[:20], 1):
        barra = "#" * min(freq, 20)
        print(f"  {i:>3}  {zona:<35}  {freq:>10}  {barra}")
    if len(sorted_zonas) > 20:
        print(f"  ... y {len(sorted_zonas) - 20} zonas mas.")


def _menu_ruta_personalizada(graph, centers, ht):
    """Opcion 8: Calcular ruta personalizada entre un centro y un incidente."""
    print("\n--- CALCULAR RUTA PERSONALIZADA ---")

    print("Centros de operacion disponibles:")
    for idx, c in enumerate(centers, 1):
        estado_str = "Disponible" if c.disponible else "Ocupado"
        print(f"  {idx:>2}. {c.nombre} | {c.ubicacion} [{estado_str}]")

    print("\nIngrese el nombre del centro o su numero (indice):")
    entrada_orig = input("> ").strip()
    
    origen = None
    try:
        c_idx = int(entrada_orig) - 1
        if 0 <= c_idx < len(centers):
            origen = centers[c_idx].ubicacion
            center_name = centers[c_idx].nombre
        else:
            print("[!] Numero de centro fuera de rango.")
            return
    except ValueError:
        # Buscar por nombre del centro
        found_center = None
        for c in centers:
            if c.nombre.lower() == entrada_orig.lower():
                found_center = c
                break
        if found_center:
            origen = found_center.ubicacion
            center_name = found_center.nombre
        else:
            # Intentar ver si es un nodo de red directo
            if graph.node_exists(entrada_orig):
                origen = entrada_orig
                center_name = entrada_orig
            else:
                print(f"[!] Centro o nodo '{entrada_orig}' no encontrado.")
                return

    print(f"\n[i] Centro seleccionado: {center_name} ({origen})")

    # Pedir ID del incidente y buscarlo en la HashTable
    print("\nIngrese el ID del incidente (ej: INC-0052):")
    iid = input("> ").strip()
    inc = ht.search(iid)
    if not inc:
        print(f"[!] Incidente '{iid}' no encontrado en la Tabla Hash.")
        return

    destino = inc.ubicacion
    print(f"[i] Incidente '{iid}' localizado en el nodo: {destino}")

    print("\nSeleccione el metodo para buscar la ruta:")
    print("  1. Dijkstra / UCS  (Ruta mas rapida en tiempo)")
    print("  2. BFS             (Ruta con menor numero de saltos)")
    print("  3. Ambos           (Comparar resultados)")
    alg_opc = input("Opcion: ").strip()

    if alg_opc in ("1", "3"):
        t0 = time.perf_counter()
        res_d = dijkstra(graph, origen, destino)
        t_d = time.perf_counter() - t0
        print(f"\n  [Dijkstra/UCS]")
        if res_d.found:
            print(f"  Ruta      : {' -> '.join(res_d.path)}")
            print(f"  Costo     : {res_d.cost:.2f} min")
            print(f"  Saltos    : {res_d.hops}")
            print(f"  Explorados: {res_d.visited} nodos")
            print(f"  Tiempo    : {_format_time(t_d)}")
        else:
            print("  No existe ruta entre los nodos indicados.")

    if alg_opc in ("2", "3"):
        t0 = time.perf_counter()
        res_b = bfs(graph, origen, destino)
        t_b = time.perf_counter() - t0
        print(f"\n  [BFS]")
        if res_b.found:
            print(f"  Ruta      : {' -> '.join(res_b.path)}")
            print(f"  Costo     : {res_b.cost:.2f} min")
            print(f"  Saltos    : {res_b.hops}")
            print(f"  Explorados: {res_b.visited} nodos")
            print(f"  Tiempo    : {_format_time(t_b)}")
        else:
            print("  No existe ruta entre los nodos indicados.")

    if alg_opc not in ("1", "2", "3"):
        print("[!] Opcion invalida.")


def _menu_reportes(incidents):
    """Opcion 9: Generar reportes ordenados."""
    print("\n--- GENERAR REPORTE ORDENADO ---")
    print("Criterio de ordenamiento:")
    print("  1. Por prioridad descendente (incidentes mas criticos primero)")
    print("  2. Por antiguedad ascendente (incidentes mas antiguos primero)")
    crit_opc = input("Opcion: ").strip()

    if crit_opc == "1":
        kf, rev, titulo = key_prioridad, True, "INCIDENTES MAS CRITICOS"
    elif crit_opc == "2":
        kf, rev, titulo = key_timestamp, False, "INCIDENTES MAS ANTIGUOS"
    else:
        print("[!] Opcion invalida.")
        return

    print("\nAlgoritmo de ordenamiento:")
    print("  1. MergeSort  (estable, O(n log n))")
    print("  2. QuickSort  (rapido en promedio, O(n log n))")
    alg_opc = input("Opcion: ").strip()

    t0 = time.perf_counter()
    if alg_opc == "1":
        sorted_list = merge_sort(incidents, key_func=kf, reverse=rev)
        alg_name = "MergeSort"
    elif alg_opc == "2":
        sorted_list = quick_sort(incidents, key_func=kf, reverse=rev)
        alg_name = "QuickSort"
    else:
        print("[!] Opcion invalida.")
        return
    t_sort = time.perf_counter() - t0

    _separator("-", width=60)
    print(f"  {titulo}  |  Ordenado con {alg_name} en {_format_time(t_sort)}")
    _separator("-", width=60)
    print(f"  {'#':>3}  {'ID':>10}  {'Tipo':>18}  {'Prioridad':>10}  {'Sev':>3}  {'Estado':>12}")
    _separator("-", width=60)

    try:
        n_mostrar = int(input("Cuantos resultados mostrar (ej: 20): "))
    except ValueError:
        n_mostrar = 20

    for idx, inc in enumerate(sorted_list[:n_mostrar], 1):
        print(f"  {idx:>3}  {inc.incident_id:>10}  {inc.tipo:>18}  "
              f"{inc.prioridad:>10.4f}  {inc.severidad:>3}  {inc.estado:>12}")
    if len(sorted_list) > n_mostrar:
        print(f"  ... y {len(sorted_list) - n_mostrar} incidentes mas.")


def _menu_metricas(ht, heap, incidents):
    """Opcion 10: Mostrar metricas de las estructuras de datos."""
    print("\n--- METRICAS DE ESTRUCTURAS DE DATOS ---")
    ht.print_metrics()
    print(f"\n  Incidentes en cola (MaxHeap) : {heap.size()}")
    print(f"  Total incidentes en memoria  : {len(incidents)}")
    activos = sum(1 for i in incidents if i.estado == "reportado")
    en_att  = sum(1 for i in incidents if i.estado == "en_atencion")
    resuel  = sum(1 for i in incidents if i.estado == "resuelto")
    print(f"  - Reportados                 : {activos}")
    print(f"  - En atencion                : {en_att}")
    print(f"  - Resueltos                  : {resuel}")


# ==============================================
# MAIN con Menu Interactivo
# ==============================================

def main():
    """Funcion principal del sistema de emergencias con menu interactivo."""
    print()
    _header("SISTEMA DE GESTION DE RUTAS DE EMERGENCIA", width=60)
    print()

    DATA_DIR = "."

    # -- Generacion de datos si no existen --
    needs_generation = not all(
        os.path.exists(os.path.join(DATA_DIR, f))
        for f in ["nodos.csv", "aristas.csv", "incidentes.csv", "centros.csv"]
    )
    if needs_generation:
        _header("GENERANDO DATOS", width=60)
        info = generate_all(output_dir=DATA_DIR)
        print(f"\n  Nodos    : {info['num_nodes']}")
        print(f"  Aristas  : {info['num_edges']}")
        print(f"  Incident : {info['num_incidents']}")
        print(f"  Centros  : {info['num_centers']}")
        print()

    # -- Carga de datos --
    _header("CARGANDO DATOS", width=60)
    t0 = time.perf_counter()
    graph, incidents, centers = load_data(DATA_DIR)
    t_load = time.perf_counter() - t0

    print(f"\n  Nodos en el grafo   : {graph.get_num_nodes()}")
    print(f"  Aristas en el grafo : {graph.get_num_edges()}")
    print(f"  Incidentes cargados : {len(incidents)}")
    print(f"  Centros cargados    : {len(centers)}")
    print(f"  Tiempo de carga     : {_format_time(t_load)}")
    print()

    # -- Construccion de estructuras --
    _header("CONSTRUCCION DE ESTRUCTURAS", width=60)
    ht, heap, t_ht, t_heap = build_structures(incidents)
    print(f"\n  Insercion en Tabla Hash : {_format_time(t_ht)}")
    print(f"  Build Max-Heap (Floyd)  : {_format_time(t_heap)}")
    ht.print_metrics()
    print()

    # ── Bucle del Menu Principal ──
    while True:
        print()
        _separator("=", width=60)
        print("      MENU PRINCIPAL - GESTION DE EMERGENCIAS")
        _separator("=", width=60)
        print("  1.  Registrar nuevo incidente")
        print("  2.  Buscar incidente por ID")
        print("  3.  Actualizar estado de incidente")
        print("  4.  Eliminar incidente")
        print("  5.  Ver incidente mas urgente")
        print("  6.  Despachar incidente mas urgente (ruta optima)")
        print("  7.  Analizar zonas afectadas")
        print("  8.  Calcular ruta personalizada")
        print("  9.  Generar reporte ordenado")
        print(" 10.  Ver metricas de estructuras")
        print(" 11.  Ejecutar Analisis Experimental completo")
        print("  0.  Salir")
        _separator("=", width=60)

        opcion = input("Seleccione una opcion: ").strip()
        print()

        if opcion == "1":
            _menu_registrar(graph, incidents, ht, heap)
        elif opcion == "2":
            _menu_buscar(ht)
        elif opcion == "3":
            _menu_actualizar(incidents, ht, heap)
        elif opcion == "4":
            _menu_eliminar(incidents, ht, heap)
        elif opcion == "5":
            _menu_mas_urgente(heap)
        elif opcion == "6":
            run_emergency_scenario(graph, heap, ht, centers)
        elif opcion == "7":
            _menu_zonas(incidents)
        elif opcion == "8":
            _menu_ruta_personalizada(graph, centers, ht)
        elif opcion == "9":
            _menu_reportes(incidents)
        elif opcion == "10":
            _menu_metricas(ht, heap, incidents)
        elif opcion == "11":
            run_experimental_analysis(incidents, graph, centers)
        elif opcion == "0":
            _header("FIN DE EJECUCION", width=60)
            print()
            break
        else:
            print("[!] Opcion no reconocida. Intente de nuevo.")


if __name__ == "__main__":
    main()
