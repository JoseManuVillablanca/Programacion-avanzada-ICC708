
package com.example.benchmarks;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Random;

import com.example.OccurrenceCounter;


public class OccurrenceBenchmark {

    
    public static final int[] INPUT_SIZES = {10, 100, 1000, 10000, 50000, 100000};

    public static final int REPETITIONS = 20;

    
    public static long[][] run() {
        long[][] results = new long[INPUT_SIZES.length][3];
        Random rng = new Random(42); 

        for (int i = 0; i < INPUT_SIZES.length; i++) {
            int n = INPUT_SIZES[i];
            results[i][0] = n;

            List<Integer> data = new ArrayList<>(n);
            for (int k = 0; k < n; k++) {
                data.add(rng.nextInt(n / 5 + 1));
            }

            long[] timesLinear = new long[REPETITIONS];
            for (int r = 0; r < REPETITIONS; r++) {
                long start = System.nanoTime();
                OccurrenceCounter.countLinear(data);
                timesLinear[r] = System.nanoTime() - start;
            }
            results[i][1] = median(timesLinear);

            long[] timesHashMap = new long[REPETITIONS];
            for (int r = 0; r < REPETITIONS; r++) {
                long start = System.nanoTime();
                OccurrenceCounter.countHashMap(data);
                timesHashMap[r] = System.nanoTime() - start;
            }
            results[i][2] = median(timesHashMap);
        }

        return results;
    }

    static long median(long[] times) {
        long[] sorted = Arrays.copyOf(times, times.length);
        Arrays.sort(sorted);
        int mid = sorted.length / 2;
        return sorted[mid];
    }
}
