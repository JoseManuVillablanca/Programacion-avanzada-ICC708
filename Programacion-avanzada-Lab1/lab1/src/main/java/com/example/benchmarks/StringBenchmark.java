package com.example.benchmarks;

import java.util.ArrayList;
import java.util.List;

import com.example.StringConcatenator;


public class StringBenchmark {

    public static long[][] run() {
        long[][] results = new long[OccurrenceBenchmark.INPUT_SIZES.length][3];

        for (int i = 0; i < OccurrenceBenchmark.INPUT_SIZES.length; i++) {
            int n = OccurrenceBenchmark.INPUT_SIZES[i];
            results[i][0] = n;

            List<String> words = new ArrayList<>(n);
            for (int k = 0; k < n; k++) {
                words.add("word" + k);
            }

            long[] timesNaive = new long[OccurrenceBenchmark.REPETITIONS];
            for (int r = 0; r < OccurrenceBenchmark.REPETITIONS; r++) {
                long start = System.nanoTime();
                StringConcatenator.concatRep(words);
                timesNaive[r] = System.nanoTime() - start;
            }
            results[i][1] = OccurrenceBenchmark.median(timesNaive);

            long[] timesEfficient = new long[OccurrenceBenchmark.REPETITIONS];
            for (int r = 0; r < OccurrenceBenchmark.REPETITIONS; r++) {
                long start = System.nanoTime();
                StringConcatenator.concatBuilder(words);
                timesEfficient[r] = System.nanoTime() - start;
            }
            results[i][2] = OccurrenceBenchmark.median(timesEfficient);
        }

        return results;
    }
}
