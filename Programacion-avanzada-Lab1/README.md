# Programacion-avanzada-Lab1

Comparación de algoritmos eficientes vs. ineficientes para conteo de ocurrencias y construcción de strings en Java.

---

## Estructura del Proyecto

```
Programacion-avanzada-Lab1/
├── README.md
├── docs/
│   └── complexity_analysis.md       ← Análisis de complejidad temporal
└── lab1/                            ← Proyecto Maven
    ├── pom.xml
    └── src/
        ├── main/java/com/example/
        │   ├── OccurrenceCounter.java   ← Conteo de ocurrencias (O(N²) y O(N))
        │   ├── StringConcatenator.java  ← Construcción de strings (O(N²) y O(N))
        │   └── benchmarks/
        │       ├── OccurrenceBenchmark.java
        │       ├── StringBenchmark.java
        │       └── BenchmarkRunner.java ← Punto de entrada de benchmarks
        └── test/java/com/example/
            ├── OccurrenceCounterTest.java
            └── StringConcatenatorTest.java
```

---

## Prerrequisitos

- **Java 17+**
- **Maven 3.8+** (verificar con `mvn -version`)

---

## Compilar el proyecto

```bash
cd lab1
mvn compile
```

---

## Ejecutar los Tests Unitarios

Utiliza JUnit 5 (Jupiter). Para correr todos los tests:

```bash
cd lab1
mvn test
```

Salida esperada: `BUILD SUCCESS` con todos los tests en verde.


---

## Ejecutar los Benchmarks

El benchmark es manual (sin frameworks externos). Mide la mediana de 20 ejecuciones para cada tamaño de entrada N ∈ {50, 100, 500, 1000, 5000, 10000}.

```bash
cd lab1
mvn compile exec:java -Dexec.mainClass="com.example.benchmarks.BenchmarkRunner"
```

Esto imprime en consola dos tablas comparativas: una para conteo de ocurrencias y otra para construcción de strings.

---

## Descripción de los Algoritmos

### A. Conteo de Ocurrencias

| Método | Complejidad | Estrategia |
|--------|-------------|------------|
| `countLinear` | O(N²) | `Collections.frequency` dentro de un bucle |
| `countHashMap` | O(N) | Una pasada con `HashMap` |

### B. Construcción de Strings

| Método | Complejidad | Estrategia |
|--------|-------------|------------|
| `concatRep` | O(N²) | Operador `+=` en bucle |
| `concatBuilder` | O(N) | `StringBuilder.append` |
