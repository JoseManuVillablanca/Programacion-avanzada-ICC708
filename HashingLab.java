import java.util.*;

public class HashingLab {
    static class Pair {
        String key;
        int value;
        Pair(String key, int value) {
            this.key = key;
            this.value = value;
        }
    }

    static class HashTableChaining {
        private List<List<Pair>> table;
        private int size;
        private int count;
        private int collisions;
        private String hashStrategy;

        public HashTableChaining(int size, String hashStrategy) {
            this.size = size;
            this.hashStrategy = hashStrategy;
            this.count = 0;
            this.collisions = 0;
            this.table = new ArrayList<>();
            for (int i = 0; i < size; i++) {
                table.add(new LinkedList<>());
            }
        }

        private int hashSum(String key) {   
            int t = 0;
            for (int i = 0; i < key.length(); i++) {
                t = t + key.charAt(i);
            }
            return Math.floorMod(t,size);
        }

        private int hashPolynomial(String key) {
            int h = 0;
            int base = 31;
            for (int i = 0; i < key.length(); i++) {
                h = Math.floorMod(h * base + key.charAt(i), size);
            }
            return h;
        }

        private int hash(String key) {
            if (hashStrategy.equals("sum")) {
                return hashSum(key);
            } else if (hashStrategy.equals("polynomial")) {
                return hashPolynomial(key);
            }
            throw new IllegalArgumentException("Unknown hash strategy");
        }

        public void insert(String key, int value) {
            int idx = hash(key);
            List<Pair> bucket = table.get(idx);
            for(Pair p : bucket){
                if (p.key.equals(key)) {
                    p.value = value;
                    return;
                }
            }
            if(!bucket.isEmpty()) collisions++; 
            bucket.add(new Pair(key, value));
            count++; 
        }

        public Integer search(String key) {
            int idx = hash(key);
            for (Pair p : table.get(idx)) {
                if (p.key.equals(key)) return p.value;
            }
            return null;
        }

        public boolean delete(String key) {
           int idx = hash(key);
           Iterator<Pair> iterator = table.get(idx).iterator();
           while (iterator.hasNext()){
               Pair p = iterator.next();
               if(p.key.equals(key)){
                   iterator.remove();
                   count--;
                   return true;
               }
           }
            return false;
        }

        public double loadFactor() {
            return (double) count / size;
        }

        public int usedBuckets() {
            int used = 0;
            for (List<Pair> bucket : table) {
                if (!bucket.isEmpty()) used++;
            }
            return used;
        }

        public int maxBucketSize() {
            int max = 0;
            for (List<Pair> bucket : table) {
                max = Math.max(max, bucket.size());
            }
            return max;
        }

        public void printReport(double elapsedSeconds) {
            System.out.println("strategy=" + hashStrategy
                    + ", size=" + size
                    + ", elements=" + count
                    + ", loadFactor=" + String.format("%.3f", loadFactor())
                    + ", collisions=" + collisions
                    + ", usedBuckets=" + usedBuckets()
                    + ", maxBucketSize=" + maxBucketSize()
                    + ", insertTimeSeconds=" + String.format("%.6f", elapsedSeconds));
        }
    }

    static List<String> generateRandomKeys(int n, int length) {
        Random random = new Random(42);
        List<String> keys = new ArrayList<>();
        String alphabet = "abcdefghijklmnopqrstuvwxyz";
        for (int i = 0; i < n; i++) {
            StringBuilder sb = new StringBuilder();
            for (int j = 0; j < length; j++) {
                sb.append(alphabet.charAt(random.nextInt(alphabet.length())));
            }
            keys.add(sb.toString());
        }
        return keys;
    }

    static List<String> generateSequentialKeys(int n) {
        List<String> keys = new ArrayList<>();
        for (int i = 0; i < n; i++) keys.add("user" + i);
        return keys;
    }

    static List<String> generateClusteredKeys(int n) {
        List<String> keys = new ArrayList<>();
        for (int i = 0; i < n; i++) keys.add("aaa" + i);
        return keys;
    }

    static void runExperiment(String datasetName, List<String> keys, int tableSize) {
        System.out.println("\nDataset: " + datasetName);
        for (String strategy : Arrays.asList("sum", "polynomial")) {
            HashTableChaining ht = new HashTableChaining(tableSize, strategy);
            long start = System.nanoTime();
            for (int i = 0; i < keys.size(); i++) {
                ht.insert(keys.get(i), i);
            }
            long end = System.nanoTime();
            double elapsedSeconds = (end - start) / 1_000_000_000.0;
            ht.printReport(elapsedSeconds);
        }
    }

    public static void main(String[] args) {
        int n = 1000;
        int tableSize = 1009;
        runExperiment("random", generateRandomKeys(n, 8), tableSize);
        runExperiment("sequential", generateSequentialKeys(n), tableSize);
        runExperiment("clustered", generateClusteredKeys(n), tableSize);
    }
}
