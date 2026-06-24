from __future__ import annotations

import heapq
from collections import deque
from typing import Any, List, Protocol, Tuple




class Escenario(Protocol):


    def obtener_vecinos(self, nodo: Any) -> List[Tuple[Any, float]]:

        ...

    def heuristica(self, nodo: Any, objetivo: Any) -> float:

        ...



ResultadoBusqueda = Tuple[List[Any], List[Any], float]




def _reconstruir_camino(procedencia: dict, inicio: Any, objetivo: Any) -> List[Any]:

    camino: List[Any] = []
    actual = objetivo
    while actual is not None:
        camino.append(actual)
        actual = procedencia.get(actual)
    camino.reverse()
    if camino and camino[0] == inicio:
        return camino
    return []




def bfs(escenario: Any, inicio: Any, objetivo: Any) -> ResultadoBusqueda:

    cola: deque = deque([inicio])
    orden_visita: List[Any] = []
    procedencia: dict[Any, Any] = {inicio: None}
    mapa_costos: dict[Any, float] = {inicio: 0.0}

    while cola:
        actual = cola.popleft()
        orden_visita.append(actual)

        if actual == objetivo:
            camino = _reconstruir_camino(procedencia, inicio, objetivo)
            return camino, orden_visita, mapa_costos[objetivo]

        for vecino, costo in escenario.obtener_vecinos(actual):
            if vecino not in procedencia:
                procedencia[vecino] = actual
                mapa_costos[vecino] = mapa_costos[actual] + costo
                cola.append(vecino)

    return [], orden_visita, 0.0




def dfs(escenario: Any, inicio: Any, objetivo: Any) -> ResultadoBusqueda:

    pila: List[Any] = [inicio]
    orden_visita: List[Any] = []
    procedencia: dict[Any, Any] = {inicio: None}
    mapa_costos: dict[Any, float] = {inicio: 0.0}
    conjunto_visitados: set = set()

    while pila:
        actual = pila.pop()

        if actual in conjunto_visitados:
            continue
        conjunto_visitados.add(actual)
        orden_visita.append(actual)

        if actual == objetivo:
            camino = _reconstruir_camino(procedencia, inicio, objetivo)
            return camino, orden_visita, mapa_costos[objetivo]

        for vecino, costo in escenario.obtener_vecinos(actual):
            if vecino not in conjunto_visitados:

                if vecino not in procedencia:
                    procedencia[vecino] = actual
                    mapa_costos[vecino] = mapa_costos[actual] + costo
                pila.append(vecino)

    return [], orden_visita, 0.0




def ucs(escenario: Any, inicio: Any, objetivo: Any) -> ResultadoBusqueda:


    contador = 0
    monticulo: List[Tuple[float, int, Any]] = [(0.0, contador, inicio)]
    procedencia: dict[Any, Any] = {inicio: None}
    mapa_costos: dict[Any, float] = {inicio: 0.0}
    orden_visita: List[Any] = []
    conjunto_visitados: set = set()

    while monticulo:
        g, _, actual = heapq.heappop(monticulo)

        if actual in conjunto_visitados:
            continue
        conjunto_visitados.add(actual)
        orden_visita.append(actual)

        if actual == objetivo:
            camino = _reconstruir_camino(procedencia, inicio, objetivo)
            return camino, orden_visita, g

        for vecino, costo in escenario.obtener_vecinos(actual):
            nuevo_costo = g + costo
            if vecino not in conjunto_visitados and nuevo_costo < mapa_costos.get(vecino, float('inf')):
                procedencia[vecino] = actual
                mapa_costos[vecino] = nuevo_costo
                contador += 1
                heapq.heappush(monticulo, (nuevo_costo, contador, vecino))

    return [], orden_visita, 0.0




def astar(escenario: Any, inicio: Any, objetivo: Any) -> ResultadoBusqueda:

    contador = 0
    h_inicio = escenario.heuristica(inicio, objetivo)

    monticulo: List[Tuple[float, int, float, Any]] = [(h_inicio, contador, 0.0, inicio)]
    procedencia: dict[Any, Any] = {inicio: None}
    mapa_g: dict[Any, float] = {inicio: 0.0}
    orden_visita: List[Any] = []
    conjunto_visitados: set = set()

    while monticulo:
        f, _, g, actual = heapq.heappop(monticulo)

        if actual in conjunto_visitados:
            continue
        conjunto_visitados.add(actual)
        orden_visita.append(actual)

        if actual == objetivo:
            camino = _reconstruir_camino(procedencia, inicio, objetivo)
            return camino, orden_visita, g

        for vecino, costo in escenario.obtener_vecinos(actual):
            nuevo_g = g + costo
            if vecino not in conjunto_visitados and nuevo_g < mapa_g.get(vecino, float('inf')):
                procedencia[vecino] = actual
                mapa_g[vecino] = nuevo_g
                h = escenario.heuristica(vecino, objetivo)
                nuevo_f = nuevo_g + h
                contador += 1
                heapq.heappush(monticulo, (nuevo_f, contador, nuevo_g, vecino))

    return [], orden_visita, 0.0




ALGORITMOS: dict[str, Any] = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "A*":  astar,
}
