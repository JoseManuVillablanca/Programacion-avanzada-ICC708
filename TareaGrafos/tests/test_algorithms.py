import sys
import os
import unittest


_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from src.algorithms import bfs, dfs, ucs, astar, ALGORITMOS
from src.graph_loader import Grafo
from src.maze_loader import Laberinto




class TestMazeWithDeadEnd(unittest.TestCase):


    def setUp(self) -> None:
        cuadricula = [
            [0, 0, 1, 0, 0],  # Fila 0: S en (0,0), G en (0,4)
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ]
        self.laberinto = Laberinto(cuadricula, inicio=(0, 0), objetivo=(0, 4))

    def _verificar_camino_valido(self, camino, visitados, costo, nombre_algo):

        self.assertGreater(len(camino), 0, f"{nombre_algo}: No encontró camino.")
        self.assertEqual(camino[0], self.laberinto.inicio,
                         f"{nombre_algo}: El camino no empieza en inicio.")
        self.assertEqual(camino[-1], self.laberinto.objetivo,
                         f"{nombre_algo}: El camino no termina en objetivo.")

        for i in range(len(camino) - 1):
            r1, c1 = camino[i]
            r2, c2 = camino[i + 1]
            self.assertEqual(abs(r1 - r2) + abs(c1 - c2), 1,
                             f"{nombre_algo}: Paso no adyacente en posición {i}.")
            self.assertEqual(self.laberinto.cuadricula[r2][c2], 0,
                             f"{nombre_algo}: El camino pasa por un muro.")

    def test_bfs_finds_optimal_path(self):

        camino, visitados, costo = bfs(self.laberinto, self.laberinto.inicio, self.laberinto.objetivo)
        self._verificar_camino_valido(camino, visitados, costo, "BFS")
        self.assertLessEqual(len(camino), 14, "BFS debería encontrar un camino corto.")

    def test_dfs_explores_dead_end(self):

        camino_dfs, visitados_dfs, _ = dfs(self.laberinto, self.laberinto.inicio, self.laberinto.objetivo)
        camino_bfs, visitados_bfs, _ = bfs(self.laberinto, self.laberinto.inicio, self.laberinto.objetivo)
        self.assertGreater(len(visitados_bfs), 0)
        self.assertGreater(len(visitados_dfs), 0)

    def test_astar_optimal_and_efficient(self):

        camino_astar, visitados_astar, costo_astar = astar(self.laberinto, self.laberinto.inicio, self.laberinto.objetivo)
        camino_bfs,   visitados_bfs,   costo_bfs   = bfs(self.laberinto, self.laberinto.inicio, self.laberinto.objetivo)
        self._verificar_camino_valido(camino_astar, visitados_astar, costo_astar, "A*")
        self.assertAlmostEqual(costo_astar, costo_bfs, places=5,
                               msg="A* y BFS deben encontrar el mismo costo óptimo.")
        self.assertLessEqual(len(visitados_astar), len(visitados_bfs) * 2,
                             "A* no debería expandir muchos más nodos que BFS.")

    def test_ucs_optimal_cost(self):

        _, _, costo_ucs  = ucs(self.laberinto, self.laberinto.inicio, self.laberinto.objetivo)
        _, _, costo_astar = astar(self.laberinto, self.laberinto.inicio, self.laberinto.objetivo)
        self.assertAlmostEqual(costo_ucs, costo_astar, places=5,
                               msg="UCS y A* deben tener el mismo costo óptimo.")




class TestGraphOptimalityDifference(unittest.TestCase):


    def setUp(self) -> None:
        self.grafo = Grafo(dirigido=True)
        self.grafo.agregar_arista("A", "B", 1.0)
        self.grafo.agregar_arista("B", "D", 1.0)
        self.grafo.agregar_arista("A", "D", 100.0)
        self.inicio = "A"
        self.objetivo = "D"

    def test_bfs_finds_shorter_path_by_steps(self):

        camino, _, costo = bfs(self.grafo, self.inicio, self.objetivo)
        self.assertEqual(camino, ["A", "D"],
                         "BFS debe preferir el camino directo A→D (1 salto).")
        self.assertAlmostEqual(costo, 100.0, places=5,
                               msg="El costo de BFS debe ser 100 (arista directa).")

    def test_ucs_finds_minimum_cost_path(self):

        camino, _, costo = ucs(self.grafo, self.inicio, self.objetivo)
        self.assertEqual(camino, ["A", "B", "D"],
                         "UCS debe elegir el camino de menor costo A→B→D.")
        self.assertAlmostEqual(costo, 2.0, places=5,
                               msg="UCS debe encontrar el costo mínimo de 2.")

    def test_astar_finds_minimum_cost_path(self):

        camino, _, costo = astar(self.grafo, self.inicio, self.objetivo)
        self.assertEqual(camino, ["A", "B", "D"],
                         "A* debe elegir el camino de menor costo A→B→D.")
        self.assertAlmostEqual(costo, 2.0, places=5,
                               msg="A* debe encontrar el costo mínimo de 2.")

    def test_bfs_vs_ucs_cost_difference(self):

        _, _, costo_bfs = bfs(self.grafo, self.inicio, self.objetivo)
        _, _, costo_ucs = ucs(self.grafo, self.inicio, self.objetivo)
        self.assertGreater(costo_bfs, costo_ucs,
                           "El costo de BFS debe ser mayor que el de UCS en este grafo.")




class TestNoSolution(unittest.TestCase):


    def setUp(self) -> None:

        cuadricula_bloqueada = [
            [0, 1, 0],
            [1, 1, 1],
            [1, 1, 1],
        ]
        self.laberinto_sin_sol = Laberinto(cuadricula_bloqueada, inicio=(0, 0), objetivo=(0, 2))


        self.grafo_sin_sol = Grafo(dirigido=False)
        self.grafo_sin_sol.agregar_arista("A", "B", 1.0)
        self.grafo_sin_sol.agregar_arista("C", "D", 1.0)


    def _verificar_sin_solucion(self, camino, visitados, costo, nombre_algo, escenario):

        self.assertEqual(camino, [],
                         f"{nombre_algo} en {escenario}: debería retornar camino vacío.")
        self.assertEqual(costo, 0.0,
                         f"{nombre_algo} en {escenario}: el costo debe ser 0 si no hay solución.")


    def test_all_algorithms_no_solution_maze(self):

        m = self.laberinto_sin_sol
        for nombre, fn in ALGORITMOS.items():
            with self.subTest(algorithm=nombre):
                camino, visitados, costo = fn(m, m.inicio, m.objetivo)
                self._verificar_sin_solucion(camino, visitados, costo, nombre, "Laberinto")

    def test_all_algorithms_no_solution_graph(self):

        g = self.grafo_sin_sol
        for nombre, fn in ALGORITMOS.items():
            with self.subTest(algorithm=nombre):
                camino, visitados, costo = fn(g, "A", "C")
                self._verificar_sin_solucion(camino, visitados, costo, nombre, "Grafo")

    def test_no_solution_visited_nodes_are_partial(self):

        camino_bfs, visitados_bfs, _ = bfs(self.grafo_sin_sol, "A", "C")

        self.assertIn("A", visitados_bfs)
        self.assertIn("B", visitados_bfs)
        self.assertNotIn("C", visitados_bfs)
        self.assertNotIn("D", visitados_bfs)




class TestTrivialPath(unittest.TestCase):


    def setUp(self) -> None:
        self.grafo = Grafo.cargar_predefinido("cities")

    def test_all_algorithms_trivial_path(self):

        for nombre, fn in ALGORITMOS.items():
            with self.subTest(algorithm=nombre):
                camino, _, costo = fn(self.grafo, "A", "A")
                self.assertEqual(camino, ["A"],
                                 f"{nombre}: camino trivial debe ser ['A'].")
                self.assertAlmostEqual(costo, 0.0, places=5,
                                       msg=f"{nombre}: costo trivial debe ser 0.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
