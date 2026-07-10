"""
hash_table.py
Implementacion de una Tabla Hash propia con encadenamiento (Chaining).

NO utiliza el tipo `dict` de Python para la logica de almacenamiento interno.
Los buckets son listas de listas de tuplas (clave, valor).

Soporta:
  - Insercion, busqueda, actualizacion y eliminacion en O(1) amortizado.
  - Redimensionamiento automatico (rehashing) cuando el factor de carga > 0.75.
  - Metricas: colisiones, factor de carga, tamano maximo de bucket.
"""


class HashTable:
    """
    Tabla Hash con encadenamiento.

    Almacena pares (key: str, value: any).
    Las claves deben ser cadenas de texto (ids de incidentes).
    """

    _DEFAULT_SIZE = 64
    _LOAD_FACTOR_LIMIT = 0.75

    def __init__(self, initial_size: int = None):
        """
        Parametros
        ----------
        initial_size : int, opcional
            Tamano inicial de la tabla (numero de buckets).
            Se redondeara a la siguiente potencia de 2 >= initial_size.
        """
        size = initial_size if initial_size else self._DEFAULT_SIZE
        self._size = self._next_power_of_2(size)
        self._count = 0           # numero de elementos almacenados
        self._buckets = [[] for _ in range(self._size)]
        # Metricas
        self._total_collisions = 0
        self._rehash_count = 0

    # ----------------------------------------------
    # Metodos de hash
    # ----------------------------------------------
    def _hash(self, key: str) -> int:
        """
        Funcion hash polinomial para cadenas.

        h = sum( ord(c) * BASE^i ) mod SIZE
        Usa base primo 31 y aplica la operacion modulo incremental
        para evitar desbordamiento.
        """
        BASE = 31
        h = 0
        for ch in key:
            h = (h * BASE + ord(ch)) % self._size
        return h

    # ----------------------------------------------
    # Operaciones CRUD
    # ----------------------------------------------
    def insert(self, key: str, value) -> bool:
        """
        Inserta o actualiza el par (key, value) en la tabla.

        Retorna True si fue una insercion nueva, False si fue una
        actualizacion de clave existente.
        """
        idx = self._hash(key)
        bucket = self._buckets[idx]

        # Existe la clave → actualizar
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return False  # actualizacion, no nueva insercion

        # Colision si el bucket ya tenia elementos
        if len(bucket) > 0:
            self._total_collisions += 1

        bucket.append((key, value))
        self._count += 1

        # Supera el factor de carga
        if self._load_factor() > self._LOAD_FACTOR_LIMIT:
            self._rehash()

        return True  # nueva insercion

    def search(self, key: str):
        """
        Busca y retorna el valor asociado a key.

        Retorna None si la clave no existe.
        """
        idx = self._hash(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return None

    def update(self, key: str, new_value) -> bool:
        """
        Actualiza el valor de una clave existente.

        Retorna True si la clave fue encontrada y actualizada,
        False si la clave no existe.
        """
        idx = self._hash(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, new_value)
                return True
        return False

    def delete(self, key: str) -> bool:
        """
        Elimina la entrada con la clave dada.

        Retorna True si fue eliminada, False si no existia.
        """
        idx = self._hash(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._count -= 1
                return True
        return False

    def contains(self, key: str) -> bool:
        """Retorna True si la clave existe en la tabla."""
        return self.search(key) is not None

    # ----------------------------------------------
    # Iteracion
    # ----------------------------------------------
    def items(self):
        """
        Genera todos los pares (key, value) almacenados en la tabla.
        Equivalente a dict.items() pero implementado manualmente.
        """
        for bucket in self._buckets:
            for k, v in bucket:
                yield k, v

    def keys(self):
        """Genera todas las claves."""
        for k, _ in self.items():
            yield k

    def values(self):
        """Genera todos los valores."""
        for _, v in self.items():
            yield v

    def all_values_list(self):
        """Retorna todos los valores como lista."""
        return [v for _, v in self.items()]

    # ----------------------------------------------
    # Metricas
    # ----------------------------------------------
    def _load_factor(self) -> float:
        return self._count / self._size

    def get_metrics(self) -> dict:
        """
        Retorna metricas de rendimiento de la tabla hash como un diccionario
        nativo de Python (esto SI es permitido; el dict nativo se usa aqui
        solo para retornar resultados al usuario, no como almacenamiento
        interno de la tabla hash).
        """
        buckets_used = sum(1 for b in self._buckets if len(b) > 0)
        max_bucket = max((len(b) for b in self._buckets), default=0)
        return {
            "size": self._size,
            "count": self._count,
            "load_factor": round(self._load_factor(), 4),
            "total_collisions": self._total_collisions,
            "buckets_used": buckets_used,
            "max_bucket_size": max_bucket,
            "rehash_count": self._rehash_count,
        }

    def print_metrics(self):
        """Imprime en consola las metricas de la tabla hash."""
        m = self.get_metrics()
        print("\n" + "=" * 45)
        print("   METRICAS DE LA TABLA HASH")
        print("=" * 45)
        print(f"  Tamano de la tabla (buckets) : {m['size']}")
        print(f"  Elementos almacenados        : {m['count']}")
        print(f"  Factor de carga              : {m['load_factor']:.4f}")
        print(f"  Colisiones totales           : {m['total_collisions']}")
        print(f"  Buckets en uso               : {m['buckets_used']}")
        print(f"  Tamano max. de bucket        : {m['max_bucket_size']}")
        print(f"  Rehashes realizados          : {m['rehash_count']}")
        print("=" * 45)

    # ----------------------------------------------
    # Rehashing
    # ----------------------------------------------
    def _rehash(self):
        """
        Duplica el tamano de la tabla y re-inserta todos los elementos.
        """
        old_buckets = self._buckets
        self._size = self._next_power_of_2(self._size * 2)
        self._buckets = [[] for _ in range(self._size)]
        self._count = 0
        self._rehash_count += 1

        for bucket in old_buckets:
            for k, v in bucket:
                self.insert(k, v)

    # ----------------------------------------------
    # Utilidades
    # ----------------------------------------------
    @staticmethod
    def _next_power_of_2(n: int) -> int:
        """Retorna la siguiente potencia de 2 mayor o igual a n."""
        if n <= 1:
            return 1
        p = 1
        while p < n:
            p <<= 1
        return p

    def __len__(self):
        return self._count

    def __repr__(self):
        m = self.get_metrics()
        return (f"HashTable(size={m['size']}, count={m['count']}, "
                f"load_factor={m['load_factor']:.3f}, "
                f"collisions={m['total_collisions']})")
