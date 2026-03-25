# Análisis de Complejidad Temporal

Este documento explica la complejidad temporal de los cuatro métodos implementados en el Lab 1.

---

## A. Conteo de Ocurrencias

### Enfoque 1 — Lineal O(N²): `OccurrenceCounter.countLinear`

```
Para cada elemento único u en la lista (hasta N únicos):
    recorrer toda la lista para contar u  → O(N)
Total: O(N × N) = O(N²)
```

**Por qué es lento:** `Collections.frequency(list, element)` recorre la lista completa por cada elemento único procesado. Aunque se evitan recuentos duplicados (gracias al `HashSet`), en el peor caso (todos los elementos distintos) se realizan **N recorridos de N elementos**.

### Enfoque 2 — HashMap O(N): `OccurrenceCounter.countHashMap`

```
Para cada elemento e en la lista (exactamente N iteraciones):
    result.put(e, result.getOrDefault(e, 0) + 1)  → O(1) amortizado
Total: O(N × 1) = O(N)
```

**Por qué es rápido:** Un `HashMap` permite acceso y actualización en tiempo **O(1) amortizado**. Cada elemento se procesa exactamente una vez.

| N       | Operaciones O(N²) | Operaciones O(N) |
|---------|-------------------|-----------------|
| 100     | ~10,000           | ~100            |
| 1,000   | ~1,000,000        | ~1,000          |
| 10,000  | ~100,000,000      | ~10,000         |

---

## B. Construcción de Strings

### Enfoque 1 — Naive O(N²): `StringConcatenator.concatNaive`

```
result = ""
Para cada palabra w de longitud L en la lista:
    result += w   →  crea nuevo String, copia (len_actual + L) caracteres
Total de caracteres copiados: L + 2L + 3L + ... + NL = L × N(N+1)/2 → O(N²·L)
```

**Por qué es lento:** Los `String` en Java son **inmutables**. Cada `+=` crea un nuevo objeto y copia todos los caracteres acumulados hasta ese punto. Con N palabras, se realizan N asignaciones de memoria progresivamente más grandes.

### Enfoque 2 — StringBuilder O(N): `StringConcatenator.concatEfficient`

```
sb = new StringBuilder()
Para cada palabra w en la lista:
    sb.append(w)   →  copia L caracteres al buffer interno (amortizado O(L))
Total de caracteres copiados: L × N → O(N·L)
```

**Por qué es rápido:** `StringBuilder` mantiene un buffer interno de capacidad creciente (estrategia de duplicación). El costo de `append` es **O(L) amortizado**, y la construcción total del string final es **O(N·L)** — lineal en la longitud del resultado.

| N       | Caracteres copiados O(N²) | Caracteres copiados O(N) |
|---------|--------------------------|--------------------------|
| 100     | ~50,500                  | ~500                     |
| 1,000   | ~5,000,500               | ~5,000                   |
| 10,000  | ~500,050,000             | ~50,000                  |

*(Asumiendo L = 5 caracteres por palabra)*

---

## Conclusión

El uso de estructuras de datos apropiadas (`HashMap`, `StringBuilder`) transforma problemas cuadráticos en lineales, lo cual representa una diferencia de **orden de magnitud** observable en los benchmarks para N ≥ 5,000.
