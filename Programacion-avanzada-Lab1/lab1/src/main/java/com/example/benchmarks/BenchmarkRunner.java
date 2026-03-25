
package com.example.benchmarks;

public class BenchmarkRunner {

    public static void main(String[] args) {

        long[][] occResults = OccurrenceBenchmark.run();
        long[][] strResults = StringBenchmark.run();

        System.out.println("── A. Conteo de Ocurrencias ─────────────────────────────────");
        System.out.printf("%-10s  %-22s  %-22s  %s%n",
                "N",
                "Lineal O(N²) [ns]",
                "HashMap O(N) [ns]",
                "Ratio (Lineal/HashMap)");
        System.out.println("─".repeat(75));

        for (long[] row : occResults) {
            long n       = row[0];
            long linear  = row[1];
            long hashMap = row[2];
            double ratio = hashMap == 0 ? Double.NaN : (double) linear / hashMap;
            System.out.printf("%-10d  %-22d  %-22d  %.2fx%n", n, linear, hashMap, ratio);
        }

        System.out.println();
        System.out.println("── B. Construcción de Strings ───────────────────────────────");
        System.out.printf("%-10s  %-22s  %-22s  %s%n",
                "N",
                "Con. Rep.+= O(N²) [ns]",
                "Builder O(N) [ns]",
                "Ratio (Con. Rep./Builder)");
        System.out.println("─".repeat(75));

        for (long[] row : strResults) {
            long n         = row[0];
            long rep       = row[1];
            long builder   = row[2];
            double ratio   = builder == 0 ? Double.NaN : (double) rep / builder;
            System.out.printf("%-10d  %-22d  %-22d  %.2fx%n", n, rep, builder, ratio);
        }

        System.out.println();
        System.out.println("─".repeat(75));
        System.out.println(" Métrica: MEDIANA de " + OccurrenceBenchmark.REPETITIONS
                + " repeticiones por tamaño N.");
        System.out.println("=============================================================");
    }
}
