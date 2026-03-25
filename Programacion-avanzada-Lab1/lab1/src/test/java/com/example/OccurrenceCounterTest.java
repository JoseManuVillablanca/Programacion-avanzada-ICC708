
package com.example;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

class OccurrenceCounterTest {
    
    @Test
    void testNormal_variedListWithDuplicates_linear() {
        List<Integer> input = Arrays.asList(1, 2, 3, 2, 1, 4, 1);
        Map<Integer, Integer> result = OccurrenceCounter.countLinear(input);

        assertEquals(3, result.get(1), "El elemento 1 debe aparecer 3 veces");
        assertEquals(2, result.get(2), "El elemento 2 debe aparecer 2 veces");
        assertEquals(1, result.get(3), "El elemento 3 debe aparecer 1 vez");
        assertEquals(1, result.get(4), "El elemento 4 debe aparecer 1 vez");
    }
    
    @Test
    void testNormal_variedListWithDuplicates_hashMap() {
        List<Integer> input = Arrays.asList(1, 2, 3, 2, 1, 4, 1);
        Map<Integer, Integer> result = OccurrenceCounter.countHashMap(input);

        assertEquals(3, result.get(1));
        assertEquals(2, result.get(2));
        assertEquals(1, result.get(3));
        assertEquals(1, result.get(4));
    }


    @Test
    void testNormal_allSameElements_linear() {
        List<Integer> input = Arrays.asList(5, 5, 5, 5, 5);
        Map<Integer, Integer> result = OccurrenceCounter.countLinear(input);

        assertEquals(1,  result.size(),  "Solo debe existir una clave");
        assertEquals(5,  result.get(5),  "El elemento 5 debe aparecer 5 veces");
    }

    @Test
    void testNormal_allSameElements_hashMap() {
        List<Integer> input = Arrays.asList(5, 5, 5, 5, 5);
        Map<Integer, Integer> result = OccurrenceCounter.countHashMap(input);

        assertEquals(1, result.size());
        assertEquals(5, result.get(5));
    }

    @Test
    void testNormal_negativeAndZeroElements_linear() {
        List<Integer> input = Arrays.asList(-1, 0, -1, 0, 0, 2);
        Map<Integer, Integer> result = OccurrenceCounter.countLinear(input);

        assertEquals(2, result.get(-1));
        assertEquals(3, result.get(0));
        assertEquals(1, result.get(2));
    }

    @Test
    void testNormal_negativeAndZeroElements_hashMap() {
        List<Integer> input = Arrays.asList(-1, 0, -1, 0, 0, 2);
        Map<Integer, Integer> result = OccurrenceCounter.countHashMap(input);

        assertEquals(2, result.get(-1));
        assertEquals(3, result.get(0));
        assertEquals(1, result.get(2));
    }
    
    @Test
    void testEdge_emptyList_linear() {
        Map<Integer, Integer> result = OccurrenceCounter.countLinear(Collections.emptyList());
        assertTrue(result.isEmpty(), "El mapa debe estar vacío para una lista vacía");
    }

    @Test
    void testEdge_emptyList_hashMap() {
        Map<Integer, Integer> result = OccurrenceCounter.countHashMap(Collections.emptyList());
        assertTrue(result.isEmpty());
    }

    @Test
    void testEdge_singleElement_linear() {
        List<Integer> input = Collections.singletonList(42);
        Map<Integer, Integer> result = OccurrenceCounter.countLinear(input);

        assertEquals(1, result.size());
        assertEquals(1, result.get(42));
    }

    @Test
    void testEdge_singleElement_hashMap() {
        List<Integer> input = Collections.singletonList(42);
        Map<Integer, Integer> result = OccurrenceCounter.countHashMap(input);

        assertEquals(1, result.size());
        assertEquals(1, result.get(42));
    }

    @Test
    void testCrossCheck_sameResultForVariedList() {
        List<Integer> input = Arrays.asList(7, 3, 7, 1, 3, 7, 9, 1, 1);
        Map<Integer, Integer> linear  = OccurrenceCounter.countLinear(input);
        Map<Integer, Integer> hashMap = OccurrenceCounter.countHashMap(input);

        assertEquals(linear, hashMap,
                "Ambos enfoques deben devolver el mismo mapa de frecuencias");
    }

    @Test
    void testCrossCheck_sameResultForSingleElement() {
        List<Integer> input = Collections.singletonList(99);
        assertEquals(
                OccurrenceCounter.countLinear(input),
                OccurrenceCounter.countHashMap(input)
        );
    }

    @Test
    void testCrossCheck_sameResultForEmptyList() {
        List<Integer> input = Collections.emptyList();
        assertEquals(
                OccurrenceCounter.countLinear(input),
                OccurrenceCounter.countHashMap(input)
        );
    }
}
