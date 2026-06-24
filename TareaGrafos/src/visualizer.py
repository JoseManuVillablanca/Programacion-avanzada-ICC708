from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from .maze_loader import Celda, Laberinto
from .graph_loader import Grafo


_DIR_SALIDA_PRED = os.path.join(os.path.dirname(__file__), "..", "capturas")


def _asegurar_dir_salida(directorio_salida: str) -> str:

    ruta_absoluta = os.path.abspath(directorio_salida)
    os.makedirs(ruta_absoluta, exist_ok=True)
    return ruta_absoluta


def visualizar_laberinto(
    laberinto: Laberinto,
    visitados: List[Celda],
    camino: List[Celda],
    nombre_algoritmo: str,
    directorio_salida: str = _DIR_SALIDA_PRED,
    guardar: bool = True,
    mostrar: bool = True,
) -> str:
    filas, columnas = laberinto.filas, laberinto.columnas

    pantalla = np.ones((filas, columnas, 3))

    for r in range(filas):
        for c in range(columnas):
            if laberinto.cuadricula[r][c] == 1:
                pantalla[r, c] = [0.1, 0.1, 0.1]


    num_visitados = len(visitados)
    for idx, (r, c) in enumerate(visitados):
        if laberinto.cuadricula[r][c] == 0:
            t = idx / max(num_visitados - 1, 1)
            pantalla[r, c] = [
                0.2,
                0.4 + 0.45 * t,
                0.9 - 0.3 * t,
            ]


    for r, c in camino:
        if (r, c) != laberinto.inicio and (r, c) != laberinto.objetivo:
            pantalla[r, c] = [0.95, 0.2, 0.2]


    fig, ax = plt.subplots(figsize=(max(8, columnas * 0.7), max(7, filas * 0.7)))
    ax.imshow(pantalla, interpolation="nearest", aspect="equal")


    if laberinto.inicio:
        sr, sc = laberinto.inicio
        ax.add_patch(plt.Circle((sc, sr), 0.4, color="#00e676", zorder=5))
        ax.text(sc, sr, "S", ha="center", va="center", fontsize=9,
                fontweight="bold", color="white", zorder=6)


    if laberinto.objetivo:
        gr, gc = laberinto.objetivo
        ax.plot(gc, gr, marker="*", markersize=18, color="#ffab40", zorder=5)
        ax.text(gc, gr - 0.5, "G", ha="center", va="center", fontsize=8,
                fontweight="bold", color="#ffab40", zorder=6)


    if camino:
        filas_camino = [p[0] for p in camino]
        columnas_camino = [p[1] for p in camino]
        ax.plot(columnas_camino, filas_camino, color="#ff1744", linewidth=2.5,
                linestyle="-", zorder=4, label="Camino")


    ax.set_xticks(np.arange(-0.5, columnas, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, filas, 1), minor=True)
    ax.grid(which="minor", color="gray", linewidth=0.3, alpha=0.4)
    ax.tick_params(which="both", bottom=False, left=False,
                   labelbottom=False, labelleft=False)


    legend_patches = [
        mpatches.Patch(color=[0.1, 0.1, 0.1], label="Muro"),
        mpatches.Patch(color=[0.2, 0.4, 0.9], label="Visitado (primero)"),
        mpatches.Patch(color=[0.2, 0.85, 0.6], label="Visitado (último)"),
        mpatches.Patch(color=[0.95, 0.2, 0.2], label="Camino final"),
        mpatches.Patch(color="#00e676", label="Inicio"),
        mpatches.Patch(color="#ffab40", label="Objetivo"),
    ]
    ax.legend(handles=legend_patches, loc="upper right", fontsize=7,
              framealpha=0.8, borderpad=0.5)

    ax.set_title(
        f"Laberinto — {nombre_algoritmo}\n"
        f"Nodos visitados: {len(visitados)} | Longitud del camino: {len(camino)}",
        fontsize=11, fontweight="bold", pad=10,
    )
    plt.tight_layout()


    ruta_archivo = ""
    if guardar:
        dir_salida = _asegurar_dir_salida(directorio_salida)
        nombre_archivo = f"laberinto_{nombre_algoritmo.replace('*', 'star').lower()}.png"
        ruta_archivo = os.path.join(dir_salida, nombre_archivo)
        plt.savefig(ruta_archivo, dpi=150, bbox_inches="tight")
        print(f"  💾 Imagen guardada en: {ruta_archivo}")

    if mostrar:
        plt.show()
    else:
        plt.close(fig)

    return ruta_archivo


def visualizar_grafo(
    grafo: Grafo,
    visitados: List[Any],
    camino: List[Any],
    nombre_algoritmo: str,
    inicio: Any,
    objetivo: Any,
    mostrar: bool = True,
) -> None:


    G = nx.DiGraph() if grafo.dirigido else nx.Graph()
    etiquetas_aristas: Dict[Tuple, str] = {}
    for origen, destino, costo in grafo.obtener_aristas():
        G.add_edge(origen, destino, weight=costo)
        etiquetas_aristas[(origen, destino)] = f"{costo:.0f}"

    todos_nodos = list(G.nodes())
    num_visitados = len(visitados)
    indice_visitados: Dict[Any, int] = {nodo: idx for idx, node in enumerate(visitados) for node in [nodo]}


    node_colors = []
    for nodo in todos_nodos:
        if nodo == inicio:
            node_colors.append("#00e676")
        elif nodo == objetivo:
            node_colors.append("#ffab40")
        elif nodo in camino:
            node_colors.append("#ff1744")
        elif nodo in indice_visitados:
            t = indice_visitados[nodo] / max(num_visitados - 1, 1)
            r = int(51 + (51 - 51) * t)
            g = int(102 + (218 - 102) * t)
            b = int(230 + (152 - 230) * t)
            node_colors.append(f"#{r:02x}{g:02x}{b:02x}")
        else:
            node_colors.append("#cccccc")


    aristas_camino = set(zip(camino[:-1], camino[1:])) if camino else set()
    colores_aristas = []
    anchos_aristas = []
    for u, v in G.edges():
        if (u, v) in aristas_camino or (v, u) in aristas_camino:
            colores_aristas.append("#ff1744")
            anchos_aristas.append(3.5)
        else:
            colores_aristas.append("#aaaaaa")
            anchos_aristas.append(1.0)


    pos = nx.spring_layout(G, seed=42, k=2.5)

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.set_facecolor("#1a1a2e")
    fig.patch.set_facecolor("#1a1a2e")

    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=900, ax=ax, alpha=0.95)
    nx.draw_networkx_labels(G, pos, font_color="white",
                            font_size=9, font_weight="bold", ax=ax)
    argumentos_aristas = {
        "edge_color": colores_aristas,
        "width": anchos_aristas,
        "ax": ax,
        "arrows": grafo.dirigido,
        "alpha": 0.8,
    }
    if grafo.dirigido:
        argumentos_aristas["arrowsize"] = 15
        argumentos_aristas["connectionstyle"] = "arc3,rad=0.05"
    nx.draw_networkx_edges(G, pos, **argumentos_aristas)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas_aristas,
                                 font_size=7, font_color="#f0f0f0",
                                 bbox=dict(alpha=0.3, color="#333355"),
                                 ax=ax)


    legend_patches = [
        mpatches.Patch(color="#00e676",  label=f"Inicio ({inicio})"),
        mpatches.Patch(color="#ffab40",  label=f"Objetivo ({objetivo})"),
        mpatches.Patch(color="#ff1744",  label="Camino final"),
        mpatches.Patch(color="#3366e6",  label="Visitado (primero)"),
        mpatches.Patch(color="#33da98",  label="Visitado (último)"),
        mpatches.Patch(color="#cccccc",  label="No visitado"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=8,
              facecolor="#2a2a4e", labelcolor="white", edgecolor="gray",
              framealpha=0.8)

    ax.set_title(
        f"Grafo — {nombre_algoritmo}\n"
        f"Nodos visitados: {len(visitados)} | Longitud del camino: {len(camino)} nodos",
        fontsize=12, fontweight="bold", color="white", pad=12,
    )
    ax.axis("off")
    plt.tight_layout()


    if mostrar:
        plt.show()
    else:
        plt.close(fig)


def visualizar_comparacion_laberinto(
    laberinto: Laberinto,
    resultados: Dict[str, Tuple[List[Celda], List[Celda], float]],
    directorio_salida: str = _DIR_SALIDA_PRED,
    guardar: bool = True,
    mostrar: bool = True,
) -> str:

    nombres_algos = list(resultados.keys())
    n = len(nombres_algos)
    columnas_rejilla = 2
    filas_rejilla = (n + 1) // columnas_rejilla

    fig, axes = plt.subplots(filas_rejilla, columnas_rejilla,
                             figsize=(columnas_rejilla * 4.5, filas_rejilla * 3.8))
    fig.patch.set_facecolor("#0f0f1a")
    ejes_planos = axes.flatten() if n > 1 else [axes]

    for idx, algo in enumerate(nombres_algos):
        camino, visitados, costo = resultados[algo]
        ax = ejes_planos[idx]

        filas_l, columnas_l = laberinto.filas, laberinto.columnas
        pantalla = np.ones((filas_l, columnas_l, 3))

        for r in range(filas_l):
            for c in range(columnas_l):
                if laberinto.cuadricula[r][c] == 1:
                    pantalla[r, c] = [0.1, 0.1, 0.1]

        num_v = len(visitados)
        for vi, (r, c) in enumerate(visitados):
            if laberinto.cuadricula[r][c] == 0:
                t = vi / max(num_v - 1, 1)
                pantalla[r, c] = [0.2, 0.4 + 0.45 * t, 0.9 - 0.3 * t]

        for r, c in camino:
            if (r, c) != laberinto.inicio and (r, c) != laberinto.objetivo:
                pantalla[r, c] = [0.95, 0.2, 0.2]

        ax.imshow(pantalla, interpolation="nearest", aspect="equal")

        if laberinto.inicio:
            sr, sc = laberinto.inicio
            ax.add_patch(plt.Circle((sc, sr), 0.38, color="#00e676", zorder=5))
        if laberinto.objetivo:
            gr, gc = laberinto.objetivo
            ax.plot(gc, gr, marker="*", markersize=14, color="#ffab40", zorder=5)

        if camino:
            ax.plot([p[1] for p in camino], [p[0] for p in camino],
                    color="#ff1744", linewidth=2.5, zorder=4)

        ax.set_xticks([])
        ax.set_yticks([])
        costo_str = f"{costo:.1f}" if camino else "Sin solución"
        ax.set_title(
            f"{algo} | Visitados: {len(visitados)} | Costo: {costo_str}",
            fontsize=9, fontweight="bold", color="white", pad=5
        )
        ax.set_facecolor("#1a1a2e")


    for idx in range(n, len(ejes_planos)):
        ejes_planos[idx].set_visible(False)

    fig.suptitle("Comparación de Algoritmos — Laberinto",
                 fontsize=13, fontweight="bold", color="white", y=1.01)
    plt.tight_layout()

    ruta_archivo = ""
    if guardar:
        dir_salida = _asegurar_dir_salida(directorio_salida)
        ruta_archivo = os.path.join(dir_salida, "laberinto_comparacion.png")
        plt.savefig(ruta_archivo, dpi=120, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"  💾 Comparación guardada en: {ruta_archivo}")

    if mostrar:
        plt.show()
    else:
        plt.close(fig)

    return ruta_archivo


def visualizar_comparacion_grafo(
    grafo: Grafo,
    resultados: Dict[str, Tuple[List[Any], List[Any], float]],
    inicio: Any,
    objetivo: Any,
    mostrar: bool = True,
) -> None:
    nombres_algos = list(resultados.keys())
    n = len(nombres_algos)
    columnas_rejilla = 2
    filas_rejilla = (n + 1) // columnas_rejilla

    fig, axes = plt.subplots(filas_rejilla, columnas_rejilla,
                             figsize=(columnas_rejilla * 6.5, filas_rejilla * 5.2))
    fig.patch.set_facecolor("#0f0f1a")
    ejes_planos = axes.flatten() if n > 1 else [axes]

    G = nx.DiGraph() if grafo.dirigido else nx.Graph()
    etiquetas_aristas: Dict[Tuple, str] = {}
    for origen, destino, costo in grafo.obtener_aristas():
        G.add_edge(origen, destino, weight=costo)
        etiquetas_aristas[(origen, destino)] = f"{costo:.0f}"

    pos = nx.spring_layout(G, seed=42, k=2.5)

    for idx, algo in enumerate(nombres_algos):
        camino, visitados, costo = resultados[algo]
        ax = ejes_planos[idx]
        ax.set_facecolor("#1a1a2e")

        todos_nodos = list(G.nodes())
        num_visitados = len(visitados)
        indice_visitados = {node: vi for vi, node in enumerate(visitados)}

        node_colors = []
        for nodo in todos_nodos:
            if nodo == inicio:
                node_colors.append("#00e676")
            elif nodo == objetivo:
                node_colors.append("#ffab40")
            elif nodo in camino:
                node_colors.append("#ff1744")
            elif nodo in indice_visitados:
                t = indice_visitados[nodo] / max(num_visitados - 1, 1)
                r = int(51)
                g = int(102 + (218 - 102) * t)
                b = int(230 + (152 - 230) * t)
                node_colors.append(f"#{r:02x}{g:02x}{b:02x}")
            else:
                node_colors.append("#cccccc")

        aristas_camino = set(zip(camino[:-1], camino[1:])) if camino else set()
        colores_aristas = []
        anchos_aristas = []
        for u, v in G.edges():
            if (u, v) in aristas_camino or (v, u) in aristas_camino:
                colores_aristas.append("#ff1744")
                anchos_aristas.append(3.5)
            else:
                colores_aristas.append("#aaaaaa")
                anchos_aristas.append(1.0)

        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                               node_size=700, ax=ax, alpha=0.95)
        nx.draw_networkx_labels(G, pos, font_color="white",
                                font_size=8, font_weight="bold", ax=ax)
        argumentos_aristas = {
            "edge_color": colores_aristas,
            "width": anchos_aristas,
            "ax": ax,
            "arrows": grafo.dirigido,
            "alpha": 0.8,
        }
        if grafo.dirigido:
            argumentos_aristas["arrowsize"] = 12
            argumentos_aristas["connectionstyle"] = "arc3,rad=0.05"
        nx.draw_networkx_edges(G, pos, **argumentos_aristas)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=etiquetas_aristas,
                                     font_size=6, font_color="#f0f0f0",
                                     bbox=dict(alpha=0.3, color="#333355"),
                                     ax=ax)

        ax.axis("off")
        costo_str = f"{costo:.1f}" if camino else "Sin solución"
        ax.set_title(
            f"{algo} | Visitados: {len(visitados)} | Costo: {costo_str}",
            fontsize=10, fontweight="bold", color="white", pad=5
        )

    for idx in range(n, len(ejes_planos)):
        ejes_planos[idx].set_visible(False)

    fig.suptitle("Comparación de Algoritmos — Grafo",
                 fontsize=14, fontweight="bold", color="white", y=1.01)
    plt.tight_layout()

    if mostrar:
        plt.show()
    else:
        plt.close(fig)
