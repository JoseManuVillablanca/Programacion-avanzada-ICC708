from __future__ import annotations

import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple


_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from src.algorithms import ALGORITMOS, ResultadoBusqueda
from src.graph_loader import Grafo
from src.maze_loader import Celda, Laberinto
from src.visualizer import (
    visualizar_comparacion_grafo,
    visualizar_comparacion_laberinto,
)

try:
    from tabulate import tabulate
    _TIENE_TABULATE = True
except ImportError:
    _TIENE_TABULATE = False


_DIR_DATOS = os.path.join(_RAIZ, "data")
_DIR_CAPTURAS = os.path.join(_RAIZ, "capturas")




def _entrada_entero(indicador: str, val_min: int = 0, val_max: int = 9999) -> int:

    while True:
        try:
            valor = int(input(indicador).strip())
            if val_min <= valor <= val_max:
                return valor
            print(f"   Por favor ingresa un valor entre {val_min} y {val_max}.")
        except ValueError:
            print("   Entrada inválida. Ingresa un número entero.")


def _entrada_opcion(indicador: str, opciones: List[str]) -> str:

    while True:
        valor = input(indicador).strip().lower()
        if valor in [o.lower() for o in opciones]:
            return valor
        print(f"   Opción inválida. Opciones: {', '.join(opciones)}")


def _imprimir_banner() -> None:

    print("\n" + "═" * 62)
    print("  ALGORITMOS DE BÚSQUEDA — BFS | DFS | UCS | A*")
    print("  Implementación y Comparación — Grafos y Laberintos")
    print("═" * 62)


def _imprimir_separador(caracter: str = "─", ancho: int = 62) -> None:
    print(caracter * ancho)




def _seleccionar_escenario() -> Tuple[Any, str]:

    print("\nSELECCIONA EL ESCENARIO:")
    print("  [1] Grafo predefinido en código (ciudades)")
    print("  [2] Grafo predefinido en código (árbol binario)")
    print("  [3] Grafo desde CSV — Lista de adyacencia")
    print("  [4] Grafo desde CSV — Matriz de adyacencia")
    print("  [5] Laberinto predefinido (default 7x7)")
    print("  [6] Laberinto predefinido (difícil 10x10)")
    print("  [7] Laberinto desde archivo TXT")

    opcion = _entrada_entero("  → Opción: ", val_min=1, val_max=7)

    if opcion == 1:
        g = Grafo.cargar_predefinido("cities")
        print(f"  ✓ Grafo de ciudades cargado. Nodos: {g.obtener_nodos()}")
        return g, "graph"

    elif opcion == 2:
        g = Grafo.cargar_predefinido("tree")
        print(f"  ✓ Árbol binario cargado. Nodos: {g.obtener_nodos()}")
        return g, "graph"

    elif opcion == 3:
        ruta_predeterminada = os.path.join(_DIR_DATOS, "grafo_lista.csv")
        ruta = input(f"  Ruta del CSV [{ruta_predeterminada}]: ").strip() or ruta_predeterminada
        g = Grafo.cargar_desde_lista_aristas_csv(ruta)
        print(f"  ✓ Grafo cargado. Nodos: {g.obtener_nodos()}")
        return g, "graph"

    elif opcion == 4:
        ruta_predeterminada = os.path.join(_DIR_DATOS, "grafo_matriz.csv")
        ruta = input(f"  Ruta del CSV [{ruta_predeterminada}]: ").strip() or ruta_predeterminada
        g = Grafo.cargar_desde_matriz_adyacencia_csv(ruta)
        print(f"  ✓ Grafo cargado. Nodos: {g.obtener_nodos()}")
        return g, "graph"

    elif opcion == 5:
        m = Laberinto.cargar_predefinido("default")
        print(f"  ✓ Laberinto 7x7 cargado.")
        return m, "maze"

    elif opcion == 6:
        m = Laberinto.cargar_predefinido("hard")
        print(f"  ✓ Laberinto 10x10 cargado.")
        return m, "maze"

    else:
        ruta_predeterminada = os.path.join(_DIR_DATOS, "laberinto_ejemplo.txt")
        ruta = input(f"  Ruta del TXT [{ruta_predeterminada}]: ").strip() or ruta_predeterminada
        m = Laberinto.cargar_desde_txt(ruta)
        print(f"  ✓ Laberinto cargado ({m.filas}x{m.columnas}).")
        return m, "maze"




def _seleccionar_extremos_grafo(grafo: Grafo) -> Tuple[Any, Any]:
    nodos = grafo.obtener_nodos()
    print(f"\nNODOS DISPONIBLES: {nodos}")
    tipo_nodo = type(nodos[0]) if nodos else str
    while True:
        inicio_crudo = input("  → Nodo inicial: ").strip()
        try:
            inicio = tipo_nodo(inicio_crudo)
        except ValueError:
            inicio = inicio_crudo
        if inicio in nodos:
            break
        print(f"   '{inicio_crudo}' no está en el grafo.")
    while True:
        objetivo_crudo = input("  → Nodo objetivo: ").strip()
        try:
            objetivo = tipo_nodo(objetivo_crudo)
        except ValueError:
            objetivo = objetivo_crudo
        if objetivo in nodos:
            break
        print(f"   '{objetivo_crudo}' no está en el grafo.")
    return inicio, objetivo




def _seleccionar_extremos_laberinto(laberinto: Laberinto) -> Tuple[Celda, Celda]:

    print(f"\nDIMENSIONES DEL LABERINTO: {laberinto.filas} filas × {laberinto.columnas} columnas")
    print("  Representación textual del laberinto:")
    print()
    print(laberinto.a_cadena())
    print()


    if laberinto.inicio:
        usar_predeterminado = input(
            f"  Inicio actual: {laberinto.inicio}. ¿Usar este? [S/n]: "
        ).strip().lower()
        if usar_predeterminado != "n":
            inicio = laberinto.inicio
        else:
            f = _entrada_entero(f"  Fila inicio (0–{laberinto.filas-1}): ", 0, laberinto.filas - 1)
            c = _entrada_entero(f"  Col  inicio (0–{laberinto.columnas-1}): ", 0, laberinto.columnas - 1)
            laberinto.establecer_inicio((f, c))
            inicio = (f, c)
    else:
        print("  Ingresa la celda de INICIO:")
        f = _entrada_entero(f"  Fila (0–{laberinto.filas-1}): ", 0, laberinto.filas - 1)
        c = _entrada_entero(f"  Col  (0–{laberinto.columnas-1}): ", 0, laberinto.columnas - 1)
        laberinto.establecer_inicio((f, c))
        inicio = (f, c)


    if laberinto.objetivo:
        usar_predeterminado = input(
            f"  Objetivo actual: {laberinto.objetivo}. ¿Usar este? [S/n]: "
        ).strip().lower()
        if usar_predeterminado != "n":
            objetivo = laberinto.objetivo
        else:
            f = _entrada_entero(f"  Fila objetivo (0–{laberinto.filas-1}): ", 0, laberinto.filas - 1)
            c = _entrada_entero(f"  Col  objetivo (0–{laberinto.columnas-1}): ", 0, laberinto.columnas - 1)
            laberinto.establecer_objetivo((f, c))
            objetivo = (f, c)
    else:
        print("  Ingresa la celda OBJETIVO:")
        f = _entrada_entero(f"  Fila (0–{laberinto.filas-1}): ", 0, laberinto.filas - 1)
        c = _entrada_entero(f"  Col  (0–{laberinto.columnas-1}): ", 0, laberinto.columnas - 1)
        laberinto.establecer_objetivo((f, c))
        objetivo = (f, c)

    return inicio, objetivo




def _ejecutar_todos_algoritmos(
    escenario: Any,
    inicio: Any,
    objetivo: Any,
) -> Dict[str, Tuple[ResultadoBusqueda, float]]:

    resultados: Dict[str, Tuple[ResultadoBusqueda, float]] = {}
    for nombre, fn in ALGORITMOS.items():
        t0 = time.perf_counter()
        resultado = fn(escenario, inicio, objetivo)
        transcurrido = time.perf_counter() - t0
        resultados[nombre] = (resultado, transcurrido)
    return resultados




def _imprimir_tabla_comparativa(
    resultados: Dict[str, Tuple[ResultadoBusqueda, float]],
    mejor_costo: float,
) -> None:

    _imprimir_separador()
    print("  TABLA COMPARATIVA DE RESULTADOS")
    _imprimir_separador()

    filas = []
    for algo, ((camino, visitados, costo), transcurrido) in resultados.items():
        if camino:
            es_optimo = "✓ Sí" if abs(costo - mejor_costo) < 1e-9 else "✗ No"
            costo_str = f"{costo:.2f}"
            long_camino = len(camino)
        else:
            es_optimo = "— Sin solución"
            costo_str = "N/A"
            long_camino = 0

        filas.append([
            algo,
            costo_str,
            len(visitados),
            long_camino,
            es_optimo,
            f"{transcurrido * 1000:.3f} ms",
        ])

    encabezados = ["Algoritmo", "Costo", "Nodos visitados", "Long. camino", "Óptimo", "Tiempo"]

    if _TIENE_TABULATE:
        print(tabulate(filas, headers=encabezados, tablefmt="rounded_outline",
                       colalign=("left", "right", "right", "right", "left", "right")))
    else:

        anchos_col = [max(len(h), max((len(str(r[i])) for r in filas), default=0))
                 for i, h in enumerate(encabezados)]
        formato = "  " + "  ".join(f"{{:<{w}}}" for w in anchos_col)
        print(formato.format(*encabezados))
        print("  " + "  ".join("─" * w for w in anchos_col))
        for fila in filas:
            print(formato.format(*fila))

    _imprimir_separador()




def _mostrar_orden_visita(resultados: Dict[str, Tuple[ResultadoBusqueda, float]]) -> None:

    print("\n  ORDEN DE VISITA POR ALGORITMO")
    _imprimir_separador()
    for algo, ((camino, visitados, _), _) in resultados.items():
        visitados_str = " → ".join(str(n) for n in visitados[:20])
        if len(visitados) > 20:
            visitados_str += f" … (+{len(visitados) - 20} más)"
        print(f"  {algo:>4}: {visitados_str}")
        if camino:
            camino_str = " → ".join(str(n) for n in camino)
            print(f"    Camino: {camino_str}")
        else:
            print(f"    Camino: ✗ No encontrado")
        print()




def main() -> None:

    _imprimir_banner()


    try:
        escenario, tipo_escenario = _seleccionar_escenario()
    except (FileNotFoundError, ValueError) as e:
        print(f"\n  ✗ Error al cargar el escenario: {e}")
        sys.exit(1)


    try:
        if tipo_escenario == "graph":
            inicio, objetivo = _seleccionar_extremos_grafo(escenario)
        else:
            inicio, objetivo = _seleccionar_extremos_laberinto(escenario)
    except ValueError as e:
        print(f"\n  ✗ Error en coordenadas: {e}")
        sys.exit(1)

    print(f"\n  ▶ Inicio: {inicio}  |  Objetivo: {objetivo}")


    print("\n  Ejecutando algoritmos...")
    resultados_crudos = _ejecutar_todos_algoritmos(escenario, inicio, objetivo)


    costos = [
        resultado[0][2]
        for resultado in resultados_crudos.values()
        if resultado[0][0]
    ]
    mejor_costo = min(costos) if costos else 0.0


    _imprimir_tabla_comparativa(resultados_crudos, mejor_costo)


    mostrar_detalle = input("\n  ¿Mostrar orden de visita detallado? [S/n]: ").strip().lower()
    if mostrar_detalle != "n":
        _mostrar_orden_visita(resultados_crudos)


    mostrar_grafico = input("  ¿Mostrar visualización gráfica? [S/n]: ").strip().lower()
    if mostrar_grafico != "n":
        print("\n  Generando visualizaciones...")


        resultados_visualizacion: Dict[str, Tuple[List, List, float]] = {
            algo: (res[0][0], res[0][1], res[0][2])
            for algo, res in resultados_crudos.items()
        }

        if tipo_escenario == "maze":
            visualizar_comparacion_laberinto(
                escenario, resultados_visualizacion,
                directorio_salida=_DIR_CAPTURAS, guardar=False, mostrar=True,
            )
        else:
            visualizar_comparacion_grafo(
                escenario, resultados_visualizacion,
                inicio, objetivo,
                mostrar=True,
            )

    print("\n  ¡Programa finalizado!\n")


if __name__ == "__main__":
    main()
