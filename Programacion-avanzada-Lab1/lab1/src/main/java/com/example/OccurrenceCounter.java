
package com.example;

import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class OccurrenceCounter {

    public static Map<Integer, Integer> countLinear(List<Integer> list) {
        Map<Integer, Integer> result = new HashMap<>();
        Set<Integer> seen = new HashSet<>(list);

        for (Integer element : seen) {
            result.put(element, Collections.frequency(list, element));
        }

        return result;
    }

    public static Map<Integer, Integer> countHashMap(List<Integer> list) {
        Map<Integer, Integer> result = new HashMap<>();

        for (Integer element : list) {
            result.put(element, result.getOrDefault(element, 0) + 1);
        }

        return result;
    }
}
