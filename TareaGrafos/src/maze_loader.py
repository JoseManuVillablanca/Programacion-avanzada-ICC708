from __future__ import annotations

import os
from typing import Any, List, Optional, Tuple


Celda = Tuple[int, int]


_DIRECCIONES: List[Tuple[int, int]] = [
    (-1,  0),  # Arriba
    ( 1,  0),  # Abajo
    ( 0, -1),  # Izquierda
    ( 0,  1),  # Derecha
]


class Laberinto:


    def __init__(
        self,
        cuadricula: List[List[int]],
        inicio: Optional[Celda] = None,
        objetivo: Optional[Celda] = None,
    ) -> None:

        if not cuadricula or not cuadricula[0]:
            raise ValueError("La matriz del laberinto no puede estar vacía.")

        self.cuadricula = cuadricula
        self.filas = len(cuadricula)
        self.columnas = len(cuadricula[0])
        for indice_f, fila in enumerate(cuadricula):
            if len(fila) != self.columnas:
                raise ValueError(f"Fila {indice_f} tiene una longitud de {len(fila)}, se esperaba {self.columnas}.")
        self.inicio: Optional[Celda] = None
        self.objetivo: Optional[Celda] = None

        if inicio is not None:
            self.establecer_inicio(inicio)
        if objetivo is not None:
            self.establecer_objetivo(objetivo)



    def establecer_inicio(self, celda: Celda) -> None:

        self._validar_celda(celda, "Inicio")
        self.inicio = celda

    def establecer_objetivo(self, celda: Celda) -> None:

        self._validar_celda(celda, "Objetivo")
        self.objetivo = celda

    def _validar_celda(self, celda: Celda, etiqueta: str) -> None:

        f, c = celda
        if not (0 <= f < self.filas and 0 <= c < self.columnas):
            raise ValueError(
                f"{etiqueta} ({f}, {c}) está fuera del laberinto "
                f"({self.filas}x{self.columnas})."
            )
        if self.cuadricula[f][c] == 1:
            raise ValueError(f"{etiqueta} ({f}, {c}) es un muro (valor=1).")



    def obtener_vecinos(self, nodo: Celda) -> List[Tuple[Celda, float]]:

        f, c = nodo
        vecinos: List[Tuple[Celda, float]] = []
        for df, dc in _DIRECCIONES:
            nf, nc = f + df, c + dc
            if 0 <= nf < self.filas and 0 <= nc < self.columnas and self.cuadricula[nf][nc] == 0:
                vecinos.append(((nf, nc), 1.0))
        return vecinos

    def heuristica(self, nodo: Celda, objetivo: Celda) -> float:

        return float(abs(nodo[0] - objetivo[0]) + abs(nodo[1] - objetivo[1]))



    def a_cadena(
        self,
        visitados: Optional[List[Celda]] = None,
        camino: Optional[List[Celda]] = None,
    ) -> str:

        conjunto_visitados = set(visitados) if visitados else set()
        conjunto_camino = set(camino) if camino else set()

        lineas: List[str] = []
        for f in range(self.filas):
            caracteres_fila = []
            for c in range(self.columnas):
                celda: Celda = (f, c)
                if celda == self.inicio:
                    caracteres_fila.append("S")
                elif celda == self.objetivo:
                    caracteres_fila.append("G")
                elif celda in conjunto_camino:
                    caracteres_fila.append("*")
                elif celda in conjunto_visitados:
                    caracteres_fila.append("·")
                elif self.cuadricula[f][c] == 1:
                    caracteres_fila.append("█")
                else:
                    caracteres_fila.append(".")
            lineas.append(" ".join(caracteres_fila))
        return "\n".join(lineas)



    @classmethod
    def cargar_desde_txt(
        cls,
        ruta_archivo: str,
        inicio: Optional[Celda] = None,
        objetivo: Optional[Celda] = None,
    ) -> "Laberinto":

        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")

        cuadricula: List[List[int]] = []
        with open(ruta_archivo, encoding="utf-8") as f:
            for num_linea, linea in enumerate(f, 1):
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue

                if "," in linea:
                    componentes = [t.strip() for t in linea.split(",")]
                elif " " in linea:
                    componentes = linea.split()
                else:
                    componentes = list(linea)
                try:
                    fila = [int(t) for t in componentes if t]
                except ValueError:
                    raise ValueError(
                        f"Error en línea {num_linea}: se esperan valores 0 o 1, "
                        f"encontrado: '{linea}'"
                    )
                cuadricula.append(fila)

        if not cuadricula:
            raise ValueError("El archivo del laberinto está vacío.")

        return cls(cuadricula, inicio=inicio, objetivo=objetivo)

    @classmethod
    def cargar_predefinido(cls, nombre: str = "default") -> "Laberinto":

        if nombre == "default":
            cuadricula = [
                [0, 0, 1, 0, 0, 0, 0],
                [1, 0, 1, 0, 1, 1, 0],
                [1, 0, 0, 0, 1, 0, 0],
                [1, 1, 1, 0, 1, 0, 1],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
            return cls(cuadricula, inicio=(0, 0), objetivo=(6, 6))

        elif nombre == "hard":
            cuadricula = [
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                [0, 1, 1, 1, 1, 0, 1, 0, 1, 0],
                [0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 1, 0, 1, 1, 0, 1, 1, 1, 0],
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 1, 1, 0, 1, 0],
            ]
            return cls(cuadricula, inicio=(0, 0), objetivo=(9, 9))

        else:
            raise ValueError(
                f"Laberinto predefinido '{nombre}' no encontrado. Opciones: 'default', 'hard'."
            )
