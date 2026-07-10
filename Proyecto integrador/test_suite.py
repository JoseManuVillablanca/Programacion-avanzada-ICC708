"""
test_suite.py
Suite de pruebas unitarias para el Sistema de Gestion de Rutas de Emergencia.

Utiliza unicamente la libreria estandar `unittest` de Python.

Cubre:
  - HashTable: insercion, busqueda, actualizacion, borrado, colisiones, rehash.
  - MaxHeap (PriorityQueue): insercion, extraccion, propiedad de heap,
    update_priority, show_top_k.
  - MergeSort y QuickSort: correccion del orden en multiples criterios.
  - BFS y Dijkstra: rutas correctas en grafos de prueba conocidos.
  - RoadNetwork: construccion, vecinos, grafos dirigidos vs no dirigidos.
  - Incident: calculo de prioridad, cambio de estado.
"""

import unittest
import time
import sys
import os

# Asegura que el directorio actual este en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Incident, EmergencyCenter, RoadNetwork
from hash_table import HashTable
from priority_queue import MaxHeap
from sorting import merge_sort, quick_sort, key_prioridad, key_timestamp
from search_algorithms import bfs, dijkstra, astar, _path_cost


# ══════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════

def _make_incident(iid="INC-0001", tipo="Incendio", ubicacion="NodoA",
                   severidad=5, timestamp=None, estado="reportado"):
    ts = timestamp if timestamp is not None else time.time()
    return Incident(iid, tipo, ubicacion, severidad, ts, estado)


def _make_triangle_graph() -> RoadNetwork:
    """Grafo: A--(1)--B--(2)--C--(5)--A"""
    g = RoadNetwork(dirigido=False)
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("A", "C", 5.0)
    return g


def _make_linear_graph(n=5) -> RoadNetwork:
    """Grafo lineal: N0--(i+1)--N1-- ... --N(n-1)"""
    g = RoadNetwork(dirigido=False)
    for i in range(n - 1):
        g.add_edge(f"N{i}", f"N{i+1}", float(i + 1))
    return g


# ══════════════════════════════════════════════════════════════════
# Tests: Incident
# ══════════════════════════════════════════════════════════════════

class TestIncident(unittest.TestCase):

    def test_creation_valid(self):
        inc = _make_incident(severidad=7)
        self.assertEqual(inc.incident_id, "INC-0001")
        self.assertEqual(inc.estado, "reportado")
        self.assertGreater(inc.prioridad, 0)

    def test_priority_increases_with_severity(self):
        now = time.time()
        inc_low  = _make_incident(iid="A", severidad=1,  timestamp=now)
        inc_high = _make_incident(iid="B", severidad=10, timestamp=now)
        self.assertGreater(inc_high.prioridad, inc_low.prioridad)

    def test_priority_increases_with_time(self):
        """Un incidente mas antiguo deberia tener mayor prioridad."""
        now = time.time()
        inc_new = _make_incident(iid="NEW", severidad=5, timestamp=now)
        inc_old = _make_incident(iid="OLD", severidad=5,
                                 timestamp=now - 3600)  # 1h atras
        self.assertGreater(inc_old.prioridad, inc_new.prioridad)

    def test_change_state_valid(self):
        inc = _make_incident()
        inc.cambiar_estado("en_atencion")
        self.assertEqual(inc.estado, "en_atencion")

    def test_change_state_invalid(self):
        inc = _make_incident()
        with self.assertRaises(ValueError):
            inc.cambiar_estado("inexistente")

    def test_invalid_severidad(self):
        with self.assertRaises(ValueError):
            _make_incident(severidad=0)
        with self.assertRaises(ValueError):
            _make_incident(severidad=11)

    def test_comparison_operators(self):
        now = time.time()
        i1 = _make_incident(iid="I1", severidad=3, timestamp=now)
        i2 = _make_incident(iid="I2", severidad=9, timestamp=now)
        self.assertLess(i1, i2)
        self.assertGreater(i2, i1)
        self.assertEqual(i1, i1)

    def test_actualizar_prioridad(self):
        now = time.time()
        inc = _make_incident(severidad=5, timestamp=now - 120)  # 2 min atras
        old_prio = inc.prioridad
        time.sleep(0.01)  # pequena espera
        inc.actualizar_prioridad()
        # La prioridad deberia ser ≥ la original (no disminuye con el tiempo)
        self.assertGreaterEqual(inc.prioridad, old_prio - 0.01)


# ══════════════════════════════════════════════════════════════════
# Tests: HashTable
# ══════════════════════════════════════════════════════════════════

class TestHashTable(unittest.TestCase):

    def setUp(self):
        self.ht = HashTable(initial_size=8)

    def test_insert_and_search(self):
        inc = _make_incident(iid="INC-001")
        self.ht.insert("INC-001", inc)
        result = self.ht.search("INC-001")
        self.assertIsNotNone(result)
        self.assertEqual(result.incident_id, "INC-001")

    def test_search_missing_key(self):
        self.assertIsNone(self.ht.search("NO_EXISTE"))

    def test_update_existing(self):
        inc = _make_incident(iid="INC-002", estado="reportado")
        self.ht.insert("INC-002", inc)
        inc.cambiar_estado("en_atencion")
        updated = self.ht.update("INC-002", inc)
        self.assertTrue(updated)
        res = self.ht.search("INC-002")
        self.assertEqual(res.estado, "en_atencion")

    def test_update_missing_key(self):
        updated = self.ht.update("NO_EXISTE", "valor")
        self.assertFalse(updated)

    def test_delete_existing(self):
        self.ht.insert("KEY", "value")
        deleted = self.ht.delete("KEY")
        self.assertTrue(deleted)
        self.assertIsNone(self.ht.search("KEY"))

    def test_delete_missing_key(self):
        deleted = self.ht.delete("NO_EXISTE")
        self.assertFalse(deleted)

    def test_len(self):
        for i in range(10):
            self.ht.insert(f"K{i}", i)
        self.assertEqual(len(self.ht), 10)

    def test_insert_duplicate_does_not_increase_count(self):
        self.ht.insert("DUP", "first")
        self.ht.insert("DUP", "second")
        self.assertEqual(len(self.ht), 1)
        self.assertEqual(self.ht.search("DUP"), "second")

    def test_rehash_triggered(self):
        """Con initial_size=8, insertar >6 elementos debe provocar rehash."""
        ht = HashTable(initial_size=8)
        initial_size = ht._size
        for i in range(20):
            ht.insert(f"K{i:04d}", i)
        self.assertGreater(ht._size, initial_size)
        self.assertGreater(ht._rehash_count, 0)

    def test_items_iteration(self):
        keys = [f"K{i}" for i in range(5)]
        for k in keys:
            self.ht.insert(k, k + "_val")
        found_keys = [k for k, _ in self.ht.items()]
        for k in keys:
            self.assertIn(k, found_keys)

    def test_metrics_structure(self):
        for i in range(30):
            self.ht.insert(f"INC-{i:03d}", i)
        m = self.ht.get_metrics()
        self.assertIn("load_factor", m)
        self.assertIn("total_collisions", m)
        self.assertGreaterEqual(m["load_factor"], 0)
        self.assertLessEqual(m["load_factor"], self.ht._LOAD_FACTOR_LIMIT + 0.1)

    def test_contains(self):
        self.ht.insert("EXIST", 1)
        self.assertTrue(self.ht.contains("EXIST"))
        self.assertFalse(self.ht.contains("NOT_EXIST"))

    def test_all_values_list(self):
        for i in range(5):
            self.ht.insert(f"K{i}", i * 10)
        vals = self.ht.all_values_list()
        self.assertEqual(len(vals), 5)


# ══════════════════════════════════════════════════════════════════
# Tests: MaxHeap (Priority Queue)
# ══════════════════════════════════════════════════════════════════

class TestMaxHeap(unittest.TestCase):

    def _make_heap_with_incidents(self, n=10):
        now = time.time()
        incidents = [
            _make_incident(iid=f"INC-{i:04d}", severidad=((i % 10) + 1),
                           timestamp=now - i * 60)
            for i in range(1, n + 1)
        ]
        heap = MaxHeap()
        for inc in incidents:
            heap.insert(inc)
        return heap, incidents

    def test_insert_and_peek(self):
        heap, incidents = self._make_heap_with_incidents(5)
        max_prio = max(inc.prioridad for inc in incidents)
        self.assertIsNotNone(heap.peek_max())
        self.assertAlmostEqual(heap.peek_max().prioridad, max_prio, places=2)

    def test_extract_max_order(self):
        heap, incidents = self._make_heap_with_incidents(10)
        extracted = []
        while not heap.is_empty():
            extracted.append(heap.extract_max())
        # Verificar orden descendente
        for i in range(len(extracted) - 1):
            self.assertGreaterEqual(extracted[i].prioridad,
                                    extracted[i + 1].prioridad)

    def test_extract_from_empty(self):
        heap = MaxHeap()
        self.assertIsNone(heap.extract_max())

    def test_peek_from_empty(self):
        heap = MaxHeap()
        self.assertIsNone(heap.peek_max())

    def test_size(self):
        heap, _ = self._make_heap_with_incidents(7)
        self.assertEqual(heap.size(), 7)

    def test_is_empty(self):
        heap = MaxHeap()
        self.assertTrue(heap.is_empty())
        heap.insert(_make_incident())
        self.assertFalse(heap.is_empty())

    def test_heap_property_after_inserts(self):
        """El elemento en la raiz debe ser el de mayor prioridad."""
        heap = MaxHeap()
        now = time.time()
        for i in range(1, 21):
            inc = _make_incident(iid=f"INC-{i:04d}", severidad=i % 10 + 1,
                                 timestamp=now - i)
            heap.insert(inc)
        top = heap.peek_max()
        for inc in heap._heap:
            self.assertGreaterEqual(top.prioridad, inc.prioridad)

    def test_update_priority_increases(self):
        heap = MaxHeap()
        now = time.time()
        inc_low = _make_incident(iid="LOW", severidad=1, timestamp=now)
        inc_high = _make_incident(iid="HIGH", severidad=10, timestamp=now)
        heap.insert(inc_low)
        heap.insert(inc_high)

        # Subir prioridad de LOW a un valor muy alto
        result = heap.update_priority("LOW", 9999.0)
        self.assertTrue(result)
        # Ahora LOW deberia ser el maximo
        self.assertEqual(heap.peek_max().incident_id, "LOW")

    def test_update_priority_nonexistent(self):
        heap = MaxHeap()
        result = heap.update_priority("NOEXIST", 100.0)
        self.assertFalse(result)

    def test_show_top_k(self):
        heap, incidents = self._make_heap_with_incidents(20)
        k = 5
        top_k = heap.show_top_k(k)
        self.assertEqual(len(top_k), k)
        # Los k elementos deben estar en orden descendente
        for i in range(len(top_k) - 1):
            self.assertGreaterEqual(top_k[i].prioridad, top_k[i + 1].prioridad)
        # El heap original no debe ser afectado
        self.assertEqual(heap.size(), 20)

    def test_build_from_list(self):
        now = time.time()
        incidents = [
            _make_incident(iid=f"INC-{i:04d}", severidad=i % 10 + 1,
                           timestamp=now - i * 30)
            for i in range(1, 16)
        ]
        heap = MaxHeap()
        heap.build_from_list(incidents)
        self.assertEqual(heap.size(), 15)
        # Extraer todo y verificar orden
        extracted = []
        while not heap.is_empty():
            extracted.append(heap.extract_max())
        for i in range(len(extracted) - 1):
            self.assertGreaterEqual(extracted[i].prioridad,
                                    extracted[i + 1].prioridad)


# ══════════════════════════════════════════════════════════════════
# Tests: Sorting
# ══════════════════════════════════════════════════════════════════

class TestSorting(unittest.TestCase):

    def _make_incidents(self, n=15):
        now = time.time()
        return [
            _make_incident(iid=f"INC-{i:04d}", severidad=(i % 10) + 1,
                           timestamp=now - (n - i) * 60)
            for i in range(n)
        ]

    def _is_sorted_asc(self, lst, key_func):
        return all(key_func(lst[i]) <= key_func(lst[i + 1])
                   for i in range(len(lst) - 1))

    def _is_sorted_desc(self, lst, key_func):
        return all(key_func(lst[i]) >= key_func(lst[i + 1])
                   for i in range(len(lst) - 1))

    def test_merge_sort_by_priority_desc(self):
        incidents = self._make_incidents()
        sorted_list = merge_sort(incidents, key_func=key_prioridad, reverse=True)
        self.assertEqual(len(sorted_list), len(incidents))
        self.assertTrue(self._is_sorted_desc(sorted_list, key_prioridad))

    def test_merge_sort_by_timestamp_asc(self):
        incidents = self._make_incidents()
        sorted_list = merge_sort(incidents, key_func=key_timestamp, reverse=False)
        self.assertTrue(self._is_sorted_asc(sorted_list, key_timestamp))

    def test_quick_sort_by_priority_desc(self):
        incidents = self._make_incidents()
        sorted_list = quick_sort(incidents, key_func=key_prioridad, reverse=True)
        self.assertEqual(len(sorted_list), len(incidents))
        self.assertTrue(self._is_sorted_desc(sorted_list, key_prioridad))

    def test_quick_sort_by_timestamp_asc(self):
        incidents = self._make_incidents()
        sorted_list = quick_sort(incidents, key_func=key_timestamp, reverse=False)
        self.assertTrue(self._is_sorted_asc(sorted_list, key_timestamp))

    def test_merge_sort_empty(self):
        result = merge_sort([], key_func=key_prioridad)
        self.assertEqual(result, [])

    def test_quick_sort_single_element(self):
        inc = [_make_incident()]
        result = quick_sort(inc, key_func=key_prioridad)
        self.assertEqual(len(result), 1)

    def test_merge_sort_does_not_mutate_original(self):
        incidents = self._make_incidents(10)
        original_order = [inc.incident_id for inc in incidents]
        _ = merge_sort(incidents, key_func=key_prioridad)
        self.assertEqual([inc.incident_id for inc in incidents], original_order)

    def test_quick_sort_does_not_mutate_original(self):
        incidents = self._make_incidents(10)
        original_order = [inc.incident_id for inc in incidents]
        _ = quick_sort(incidents, key_func=key_prioridad)
        self.assertEqual([inc.incident_id for inc in incidents], original_order)

    def test_sort_numbers_asc(self):
        data = [5, 3, 1, 4, 2]
        ms = merge_sort(data)
        qs = quick_sort(data)
        self.assertEqual(ms, [1, 2, 3, 4, 5])
        self.assertEqual(qs, [1, 2, 3, 4, 5])

    def test_sort_numbers_desc(self):
        data = [5, 3, 1, 4, 2]
        ms = merge_sort(data, reverse=True)
        qs = quick_sort(data, reverse=True)
        self.assertEqual(ms, [5, 4, 3, 2, 1])
        self.assertEqual(qs, [5, 4, 3, 2, 1])

    def test_sort_already_sorted(self):
        data = [1, 2, 3, 4, 5]
        self.assertEqual(merge_sort(data), [1, 2, 3, 4, 5])
        self.assertEqual(quick_sort(data), [1, 2, 3, 4, 5])

    def test_sort_reverse_sorted(self):
        data = [5, 4, 3, 2, 1]
        self.assertEqual(merge_sort(data), [1, 2, 3, 4, 5])
        self.assertEqual(quick_sort(data), [1, 2, 3, 4, 5])


# ══════════════════════════════════════════════════════════════════
# Tests: RoadNetwork
# ══════════════════════════════════════════════════════════════════

class TestRoadNetwork(unittest.TestCase):

    def test_add_node_and_get_all(self):
        g = RoadNetwork()
        g.add_node("A")
        g.add_node("B")
        self.assertIn("A", g.get_all_nodes())
        self.assertIn("B", g.get_all_nodes())

    def test_duplicate_node_ignored(self):
        g = RoadNetwork()
        g.add_node("A")
        g.add_node("A")
        self.assertEqual(g.get_num_nodes(), 1)

    def test_add_edge_creates_nodes(self):
        g = RoadNetwork()
        g.add_edge("X", "Y", 3.5)
        self.assertTrue(g.node_exists("X"))
        self.assertTrue(g.node_exists("Y"))

    def test_undirected_neighbors(self):
        g = _make_triangle_graph()
        neigh_a = [n for n, _ in g.get_neighbors("A")]
        self.assertIn("B", neigh_a)
        self.assertIn("C", neigh_a)
        neigh_b = [n for n, _ in g.get_neighbors("B")]
        self.assertIn("A", neigh_b)
        self.assertIn("C", neigh_b)

    def test_directed_graph(self):
        g = RoadNetwork(dirigido=True)
        g.add_edge("A", "B", 1.0)
        neigh_a = [n for n, _ in g.get_neighbors("A")]
        neigh_b = [n for n, _ in g.get_neighbors("B")]
        self.assertIn("B", neigh_a)
        self.assertNotIn("A", neigh_b)

    def test_get_neighbors_nonexistent(self):
        g = RoadNetwork()
        self.assertEqual(g.get_neighbors("FANTASMA"), [])

    def test_edge_count(self):
        g = _make_triangle_graph()
        self.assertEqual(g.get_num_edges(), 3)


# ══════════════════════════════════════════════════════════════════
# Tests: BFS
# ══════════════════════════════════════════════════════════════════

class TestBFS(unittest.TestCase):

    def test_same_node(self):
        g = _make_triangle_graph()
        r = bfs(g, "A", "A")
        self.assertTrue(r.found)
        self.assertEqual(r.path, ["A"])
        self.assertEqual(r.hops, 0)

    def test_direct_neighbor(self):
        g = _make_triangle_graph()
        r = bfs(g, "A", "B")
        self.assertTrue(r.found)
        self.assertEqual(r.hops, 1)

    def test_path_exists(self):
        g = _make_linear_graph(5)
        r = bfs(g, "N0", "N4")
        self.assertTrue(r.found)
        self.assertEqual(r.path[0], "N0")
        self.assertEqual(r.path[-1], "N4")

    def test_path_does_not_exist(self):
        g = RoadNetwork()
        g.add_node("ISLA")
        g.add_edge("A", "B", 1.0)
        r = bfs(g, "A", "ISLA")
        self.assertFalse(r.found)

    def test_bfs_finds_min_hops(self):
        """En el grafo triangulo, BFS debe preferir A→C directo (1 salto)
        sobre A→B→C (2 saltos)."""
        g = _make_triangle_graph()
        r = bfs(g, "A", "C")
        self.assertTrue(r.found)
        self.assertEqual(r.hops, 1)

    def test_nonexistent_node(self):
        g = _make_triangle_graph()
        r = bfs(g, "Z", "A")
        self.assertFalse(r.found)

    def test_algorithm_label(self):
        g = _make_triangle_graph()
        r = bfs(g, "A", "B")
        self.assertEqual(r.algorithm, "BFS")


# ══════════════════════════════════════════════════════════════════
# Tests: Dijkstra/UCS
# ══════════════════════════════════════════════════════════════════

class TestDijkstra(unittest.TestCase):

    def test_same_node(self):
        g = _make_triangle_graph()
        r = dijkstra(g, "A", "A")
        self.assertTrue(r.found)
        self.assertAlmostEqual(r.cost, 0.0)

    def test_direct_edge_cost(self):
        g = _make_triangle_graph()
        r = dijkstra(g, "A", "B")
        self.assertTrue(r.found)
        self.assertAlmostEqual(r.cost, 1.0)

    def test_shortest_path_indirect(self):
        """A→C: directo=5, via B=1+2=3 → Dijkstra debe tomar via B."""
        g = _make_triangle_graph()
        r = dijkstra(g, "A", "C")
        self.assertTrue(r.found)
        self.assertAlmostEqual(r.cost, 3.0)
        self.assertIn("B", r.path)

    def test_linear_graph_cost(self):
        """Grafo lineal N0--(1)--N1--(2)--N2--(3)--N3--(4)--N4; costo=10."""
        g = _make_linear_graph(5)
        r = dijkstra(g, "N0", "N4")
        self.assertTrue(r.found)
        self.assertAlmostEqual(r.cost, 10.0)

    def test_no_path(self):
        g = RoadNetwork()
        g.add_node("ISLA")
        g.add_edge("A", "B", 1.0)
        r = dijkstra(g, "A", "ISLA")
        self.assertFalse(r.found)

    def test_algorithm_label(self):
        g = _make_triangle_graph()
        r = dijkstra(g, "A", "B")
        self.assertEqual(r.algorithm, "Dijkstra/UCS")

    def test_path_cost_matches(self):
        g = _make_triangle_graph()
        r = dijkstra(g, "A", "C")
        computed_cost = _path_cost(g, r.path)
        self.assertAlmostEqual(r.cost, computed_cost, places=5)

    def test_dijkstra_better_than_bfs_cost(self):
        """Dijkstra debe encontrar costo ≤ BFS en grafos ponderados."""
        g = _make_triangle_graph()
        rb = bfs(g, "A", "C")
        rd = dijkstra(g, "A", "C")
        self.assertLessEqual(rd.cost, rb.cost)


# ══════════════════════════════════════════════════════════════════
# Tests: A* (bono)
# ══════════════════════════════════════════════════════════════════

class TestAStar(unittest.TestCase):

    def test_astar_no_heuristic_equals_dijkstra(self):
        g = _make_triangle_graph()
        rd = dijkstra(g, "A", "C")
        ra = astar(g, "A", "C")     # h=0 → Dijkstra
        self.assertAlmostEqual(rd.cost, ra.cost, places=5)

    def test_astar_finds_path(self):
        g = _make_linear_graph(5)
        r = astar(g, "N0", "N4")
        self.assertTrue(r.found)

    def test_astar_label(self):
        g = _make_triangle_graph()
        r = astar(g, "A", "B")
        self.assertEqual(r.algorithm, "A*")


# ══════════════════════════════════════════════════════════════════
# Integracion simple: carga desde data_generator
# ══════════════════════════════════════════════════════════════════

class TestIntegration(unittest.TestCase):

    def test_full_pipeline_small(self):
        """
        Prueba de integracion con un grafo y dataset pequenos
        sin tocar archivos CSV.
        """
        # Construir grafo
        g = RoadNetwork()
        edges = [("A","B",2),("B","C",3),("A","C",8),("C","D",1),("B","D",5)]
        for u, v, w in edges:
            g.add_edge(u, v, w)

        # Incidentes
        now = time.time()
        incidents = [
            _make_incident(f"INC-{i:03d}", severidad=(i%10)+1, timestamp=now-i*30)
            for i in range(1, 21)
        ]

        # Hash Table
        ht = HashTable()
        for inc in incidents:
            ht.insert(inc.incident_id, inc)
        self.assertEqual(len(ht), 20)

        # Max Heap
        heap = MaxHeap()
        heap.build_from_list(incidents)
        self.assertEqual(heap.size(), 20)

        # Extraer 3 urgentes
        urgentes = [heap.extract_max() for _ in range(3)]
        self.assertEqual(len(urgentes), 3)
        # Orden correcto
        self.assertGreaterEqual(urgentes[0].prioridad, urgentes[1].prioridad)
        self.assertGreaterEqual(urgentes[1].prioridad, urgentes[2].prioridad)

        # Ruta optima
        r = dijkstra(g, "A", "D")
        self.assertTrue(r.found)
        # A→B→C→D = 2+3+1=6 vs A→B→D=2+5=7 vs A→C→D=8+1=9
        self.assertAlmostEqual(r.cost, 6.0)

        # MergeSort y QuickSort producen el mismo orden de prioridades
        # (los IDs pueden diferir si hay prioridades iguales: MergeSort es
        # estable, QuickSort no lo es, pero ambos deben ordenar correctamente).
        ms = merge_sort(incidents, key_func=key_prioridad, reverse=True)
        qs = quick_sort(incidents, key_func=key_prioridad, reverse=True)
        # Verificar que las prioridades resultantes estan en orden descendente
        for i in range(len(ms) - 1):
            self.assertGreaterEqual(ms[i].prioridad, ms[i + 1].prioridad)
            self.assertGreaterEqual(qs[i].prioridad, qs[i + 1].prioridad)
        # Verificar que los conjuntos de IDs son identicos
        self.assertEqual(
            sorted(inc.incident_id for inc in ms),
            sorted(inc.incident_id for inc in qs)
        )


# ══════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Verbose para ver cada test individualmente
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestIncident,
        TestHashTable,
        TestMaxHeap,
        TestSorting,
        TestRoadNetwork,
        TestBFS,
        TestDijkstra,
        TestAStar,
        TestIntegration,
    ]

    for tc in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(tc))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
