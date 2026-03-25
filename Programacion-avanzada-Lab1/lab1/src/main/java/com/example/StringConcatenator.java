
package com.example;

import java.util.List;

public class StringConcatenator {

    public static String concatRep(List<String> words) {
        String result = "";

        for (String word : words) {
            result += word;
        }

        return result;
    }

    public static String concatBuilder(List<String> words) {
        StringBuilder sb = new StringBuilder();

        for (String word : words) {
            sb.append(word);
        }

        return sb.toString();
    }
}
