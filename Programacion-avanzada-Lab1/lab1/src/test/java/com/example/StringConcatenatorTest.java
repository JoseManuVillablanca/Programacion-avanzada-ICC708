
package com.example;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

class StringConcatenatorTest {

    @Test
    void testNormal_severalWords_naive() {
        List<String> words = Arrays.asList("Hola", " ", "Mundo");
        assertEquals("Hola Mundo", StringConcatenator.concatRep(words));
    }

    @Test
    void testNormal_severalWords_efficient() {
        List<String> words = Arrays.asList("Hola", " ", "Mundo");
        assertEquals("Hola Mundo", StringConcatenator.concatBuilder(words));
    }

    @Test
    void testNormal_mixedEmptyStrings_naive() {
        List<String> words = Arrays.asList("A", "", "B", "", "C");
        assertEquals("ABC", StringConcatenator.concatRep(words));
    }

    @Test
    void testNormal_mixedEmptyStrings_efficient() {
        List<String> words = Arrays.asList("A", "", "B", "", "C");
        assertEquals("ABC", StringConcatenator.concatBuilder(words));
    }

    @Test
    void testNormal_longWords_naive() {
        List<String> words = Arrays.asList("Hola", "Como", "Estas");
        String expected = "HolaComoEstas";
        assertEquals(expected, StringConcatenator.concatRep(words));
    }

    @Test
    void testNormal_longWords_efficient() {
        List<String> words = Arrays.asList("Hola", "Como", "Estas");
        assertEquals("HolaComoEstas", StringConcatenator.concatBuilder(words));
    }

    @Test
    void testEdge_emptyList_naive() {
        String result = StringConcatenator.concatRep(Collections.emptyList());
        assertEquals("", result, "Lista vacía debe producir string vacío");
    }

    @Test
    void testEdge_emptyList_efficient() {
        String result = StringConcatenator.concatBuilder(Collections.emptyList());
        assertEquals("", result);
    }

    @Test
    void testEdge_singleElement_naive() {
        String result = StringConcatenator.concatRep(Collections.singletonList("único"));
        assertEquals("único", result);
    }

    @Test
    void testEdge_singleElement_efficient() {
        String result = StringConcatenator.concatBuilder(Collections.singletonList("único"));
        assertEquals("único", result);
    }

    @Test
    void testEdge_listOfEmptyStrings_naive() {
        List<String> words = Arrays.asList("", "", "");
        assertEquals("", StringConcatenator.concatRep(words));
    }

    @Test
    void testEdge_listOfEmptyStrings_efficient() {
        List<String> words = Arrays.asList("", "", "");
        assertEquals("", StringConcatenator.concatBuilder(words));
    }

    @Test
    void testCrossCheck_sameResultForVariedList() {
        List<String> words = Arrays.asList("Hola", " ", "Como", " ", "Estas");
        assertEquals(
                StringConcatenator.concatRep(words),
                StringConcatenator.concatBuilder(words),
                "Ambos enfoques deben producir la misma cadena"
        );
    }

    @Test
    void testCrossCheck_sameResultForEmptyList() {
        List<String> words = Collections.emptyList();
        assertEquals(
                StringConcatenator.concatRep(words),
                StringConcatenator.concatBuilder(words)
        );
    }

    @Test
    void testCrossCheck_sameResultForSingleElement() {
        List<String> words = Collections.singletonList("test");
        assertEquals(
                StringConcatenator.concatRep(words),
                StringConcatenator.concatBuilder(words)
        );
    }
}
