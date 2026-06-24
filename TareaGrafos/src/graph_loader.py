from __future__ import annotations

import csv
import os
from typing import Any, Dict, List, Optional, Tuple


class Grafo:


    def __init__(self, dirigido: bool = False) -> None:

        self._adyacencia: Dict[Any, List[Tuple[Any, float]]] = {}
        self.dirigido = dirigido



    def agregar_arista(self, origen: Any, destino: Any, costo: float = 1.0) -> None:

        self._adyacencia.setdefault(origen, [])
        self._adyacencia.setdefault(destino, [])
        self._adyacencia[origen].append((destino, costo))
        if not self.dirigido:
            self._adyacencia[destino].append((origen, costo))

    def obtener_nodos(self) -> List[Any]:

        return list(self._adyacencia.keys())

    def obtener_aristas(self) -> List[Tuple[Any, Any, float]]:

        aristas = []
        for origen, vecinos in self._adyacencia.items():
            for destino, costo in vecinos:
                aristas.append((origen, destino, costo))
        return aristas



    def obtener_vecinos(self, nodo: Any) -> List[Tuple[Any, float]]:

        return self._adyacencia.get(nodo, [])

    def heuristica(self, nodo: Any, objetivo: Any) -> float:

        return 0.0



    @classmethod
    def cargar_predefinido(cls, nombre: str = "cities") -> "Grafo":

        grafo = cls(dirigido=False)

        if nombre == "cities":

            aristas = [
                ("A", "B", 4), ("A", "C", 2),
                ("B", "C", 5), ("B", "D", 10),
                ("C", "E", 3),
                ("D", "F", 11), ("D", "G", 7),
                ("E", "D", 4), ("E", "F", 6),
                ("F", "G", 2),
            ]
            for o, d, c in aristas:
                grafo.agregar_arista(o, d, c)

        elif nombre == "tree":

            aristas = [
                (1, 2, 1), (1, 3, 1),
                (2, 4, 1), (2, 5, 1),
                (3, 6, 1), (3, 7, 1),
            ]
            for o, d, c in aristas:
                grafo.agregar_arista(o, d, c)

        else:
            raise ValueError(f"Grafo predefinido '{nombre}' no encontrado. Opciones: 'cities', 'tree'.")

        return grafo

    @classmethod
    def cargar_desde_lista_aristas_csv(cls, ruta_archivo: str, dirigido: bool = False) -> "Grafo":

        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")

        grafo = cls(dirigido=dirigido)
        with open(ruta_archivo, newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            requerido = {"Origen", "Destino", "Costo"}
            if not lector.fieldnames or not requerido.issubset(set(lector.fieldnames)):
                raise ValueError(
                    f"El CSV debe tener columnas: {requerido}. "
                    f"Encontradas: {lector.fieldnames}"
                )
            for fila in lector:
                try:
                    costo = float(fila["Costo"])
                except ValueError:
                    raise ValueError(f"Costo inválido en fila: {fila}")
                grafo.agregar_arista(fila["Origen"].strip(), fila["Destino"].strip(), costo)

        return grafo

    @classmethod
    def cargar_desde_matriz_adyacencia_csv(cls, ruta_archivo: str, dirigido: bool = False) -> "Grafo":

        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")

        grafo = cls(dirigido=dirigido)
        with open(ruta_archivo, newline="", encoding="utf-8") as f:
            lector = csv.reader(f)
            filas = list(lector)
        if not filas or not filas[0]:
            raise ValueError("El archivo CSV de la matriz de adyacencia está vacío o no es válido.")

        encabezado = filas[0][1:]
        for fila in filas[1:]:
            origen = fila[0].strip()
            for indice_col, celda in enumerate(fila[1:]):
                celda = celda.strip()
                if celda and celda != "0":
                    try:
                        costo = float(celda)
                        destino = encabezado[indice_col].strip()

                        if dirigido or origen <= destino:
                            grafo.agregar_arista(origen, destino, costo)
                    except (ValueError, IndexError):
                        continue

        return grafo
