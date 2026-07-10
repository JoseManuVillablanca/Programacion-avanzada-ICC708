"""
sorting.py
Implementaciones propias de algoritmos de ordenamiento.

NO utiliza sorted() ni list.sort() de Python para los algoritmos.
Ambos algoritmos aceptan una funcion de clave (key_func) para
comparar elementos por el atributo deseado.

Algoritmos implementados:
  - MergeSort  → O(n log n) estable, siempre garantizado.
  - QuickSort  → O(n log n) promedio, O(n²) peor caso; in-place con pivot mediana.
"""


# ──────────────────────────────────────────────
# MergeSort
# ──────────────────────────────────────────────

def merge_sort(arr: list, key_func=None, reverse: bool = False) -> list:
    """
    Ordena una lista mediante el algoritmo Merge Sort.

    Parametros
    ----------
    arr : list
        Lista de elementos a ordenar.
    key_func : callable, opcional
        Funcion que extrae el valor de comparacion de cada elemento.
        Si es None, compara los elementos directamente.
    reverse : bool
        Si es True, ordena de mayor a menor.

    Retorna
    -------
    list
        Nueva lista ordenada (no modifica arr).
    """
    if key_func is None:
        key_func = lambda x: x

    def _merge(left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            lk = key_func(left[i])
            rk = key_func(right[j])
            if (lk <= rk) if not reverse else (lk >= rk):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        # Agregar los elementos restantes
        while i < len(left):
            result.append(left[i])
            i += 1
        while j < len(right):
            result.append(right[j])
            j += 1
        return result

    def _merge_sort_rec(lst):
        if len(lst) <= 1:
            return lst
        mid = len(lst) // 2
        left = _merge_sort_rec(lst[:mid])
        right = _merge_sort_rec(lst[mid:])
        return _merge(left, right)

    return _merge_sort_rec(list(arr))   # copia para no mutar original


# ──────────────────────────────────────────────
# QuickSort
# ──────────────────────────────────────────────

def quick_sort(arr: list, key_func=None, reverse: bool = False) -> list:
    """
    Ordena una lista mediante el algoritmo Quick Sort (in-place sobre copia).

    Usa la estrategia de pivot por mediana-de-tres para reducir el peor caso.

    Parametros
    ----------
    arr : list
        Lista de elementos a ordenar.
    key_func : callable, opcional
        Funcion que extrae el valor de comparacion.
    reverse : bool
        Si es True, ordena de mayor a menor.

    Retorna
    -------
    list
        Nueva lista ordenada (no modifica arr).
    """
    if key_func is None:
        key_func = lambda x: x

    data = list(arr)   # copia para no mutar original

    def _median_of_three(lst, lo, hi):
        """Retorna el indice del valor mediano entre lst[lo], lst[mid], lst[hi]."""
        mid = (lo + hi) // 2
        a, b, c = key_func(lst[lo]), key_func(lst[mid]), key_func(lst[hi])
        if (a <= b <= c) or (c <= b <= a):
            return mid
        elif (b <= a <= c) or (c <= a <= b):
            return lo
        else:
            return hi

    def _partition(lst, lo, hi):
        pivot_idx = _median_of_three(lst, lo, hi)
        lst[pivot_idx], lst[hi] = lst[hi], lst[pivot_idx]
        pivot_val = key_func(lst[hi])
        i = lo - 1
        for j in range(lo, hi):
            jk = key_func(lst[j])
            cond = (jk <= pivot_val) if not reverse else (jk >= pivot_val)
            if cond:
                i += 1
                lst[i], lst[j] = lst[j], lst[i]
        lst[i + 1], lst[hi] = lst[hi], lst[i + 1]
        return i + 1

    def _quick_sort_rec(lst, lo, hi):
        if lo < hi:
            pi = _partition(lst, lo, hi)
            _quick_sort_rec(lst, lo, pi - 1)
            _quick_sort_rec(lst, pi + 1, hi)

    if len(data) > 1:
        _quick_sort_rec(data, 0, len(data) - 1)
    return data


# ──────────────────────────────────────────────
# Funciones auxiliares de clave para Incidents
# ──────────────────────────────────────────────

def key_prioridad(incident):
    """Clave de ordenamiento por prioridad (descendente si reverse=True)."""
    return incident.prioridad


def key_timestamp(incident):
    """Clave de ordenamiento por antigüedad (timestamp ascendente = mas antiguo primero)."""
    return incident.timestamp


def key_severidad(incident):
    """Clave de ordenamiento por severidad."""
    return incident.severidad


def key_tipo(incident):
    """Clave de ordenamiento alfabetico por tipo."""
    return incident.tipo


# ──────────────────────────────────────────────
# Busqueda binaria (auxiliar para analisis)
# ──────────────────────────────────────────────

def binary_search(sorted_arr: list, target_key, key_func=None) -> int:
    """
    Busqueda binaria sobre una lista ya ordenada (ascendente).

    Parametros
    ----------
    sorted_arr : list
        Lista ordenada de menor a mayor segun key_func.
    target_key : comparable
        Valor de clave a buscar.
    key_func : callable, opcional
        Funcion que extrae la clave de comparacion.

    Retorna
    -------
    int
        Indice del primer elemento que coincide, o -1 si no se encuentra.
    """
    if key_func is None:
        key_func = lambda x: x

    lo, hi = 0, len(sorted_arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        mk = key_func(sorted_arr[mid])
        if mk == target_key:
            return mid
        elif mk < target_key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
