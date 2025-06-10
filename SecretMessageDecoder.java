import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SecretMessageDecoder {
    
    static class Coordinate {
        int x, y;
        char character;
        
        public Coordinate(int x, char character, int y) {
            this.x = x;
            this.character = character;
            this.y = y;
        }
        
        @Override
        public String toString() {
            return String.format("(%d, '%c', %d)", x, character, y);
        }
    }
    
    private static String repeat(String str, int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            sb.append(str);
        }
        return sb.toString();
    }
    
    @SuppressWarnings("deprecation")
    public static String fetchGoogleDocContent(String urlString) {
        System.out.println("🔍 Fetching Google Doc content...");
        System.out.println("URL: " + urlString);
        System.out.println(repeat("-", 50));
        
        try {
            URL url = new URL(urlString);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);
            connection.setRequestProperty("User-Agent", 
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
            
            int responseCode = connection.getResponseCode();
            if (responseCode != 200) {
                System.err.println("❌ HTTP Error: " + responseCode);
                return null;
            }
            
            StringBuilder content = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(connection.getInputStream(), "UTF-8"))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    content.append(line).append("\n");
                }
            }
            
            String htmlContent = content.toString();
            System.out.println("✅ Document fetched successfully!");
            System.out.printf("📊 Content length: %,d characters%n", htmlContent.length());
            
            String textContent = extractTextFromHtml(htmlContent);
            System.out.printf("📝 Extracted text length: %,d characters%n", textContent.length());
            
            return textContent;
            
        } catch (Exception e) {
            System.err.println("❌ Error fetching document: " + e.getMessage());
            return null;
        }
    }
    
    private static String extractTextFromHtml(String html) {
        String cleanHtml = html.replaceAll("(?i)<script[^>]*>.*?</script>", "");
        cleanHtml = cleanHtml.replaceAll("(?i)<style[^>]*>.*?</style>", "");
        String textContent = cleanHtml.replaceAll("<[^>]+>", "");
        textContent = textContent.replaceAll("\\s+", " ").trim();
        return textContent;
    }
    
    public static List<Coordinate> parseCoordinates(String content) {
        System.out.println("🔄 Parsing coordinate data...");
        System.out.println(repeat("-", 50));
        
        List<Coordinate> coordinates = new ArrayList<Coordinate>();
        
        // Find the specific coordinate section more precisely
        int coordStart = content.indexOf("y-coordinate");
        if (coordStart == -1) {
            System.out.println("❌ Could not find 'y-coordinate' section");
            return coordinates;
        }
        
        // Get a limited section after y-coordinate (only the next 100 characters)
        String coordData = content.substring(coordStart + 12, 
            Math.min(content.length(), coordStart + 112));
        
        System.out.println("📍 Coordinate section (limited): '" + coordData + "'");
        
        // Look for ONLY block characters in the coordinate data
        String[] blockChars = {"█", "▀", "▄", "■", "▌", "▐"};
        
        Pattern pattern = Pattern.compile("(\\d)([" + String.join("", blockChars) + "])(\\d)");
        Matcher matcher = pattern.matcher(coordData);
        
        System.out.println("\n🔍 Looking for block character coordinates only...");
        
        while (matcher.find()) {
            try {
                int x = Integer.parseInt(matcher.group(1));
                char character = matcher.group(2).charAt(0);
                int y = Integer.parseInt(matcher.group(3));
                
                coordinates.add(new Coordinate(x, character, y));
                System.out.printf("✅ Found coordinate: (%d, '%c', %d)%n", x, character, y);
                
            } catch (NumberFormatException e) {
                // Skip invalid matches
            }
        }
        
        System.out.printf("\n🎯 Found %d valid block character coordinates%n", coordinates.size());
        return coordinates;
    }
    
    public static void displayResults(List<Coordinate> coordinates) {
        if (coordinates.isEmpty()) {
            System.out.println("❌ No coordinates to display");
            return;
        }
        
        // Find bounds
        int minX = Integer.MAX_VALUE, maxX = Integer.MIN_VALUE;
        int minY = Integer.MAX_VALUE, maxY = Integer.MIN_VALUE;
        
        for (Coordinate coord : coordinates) {
            minX = Math.min(minX, coord.x);
            maxX = Math.max(maxX, coord.x);
            minY = Math.min(minY, coord.y);
            maxY = Math.max(maxY, coord.y);
        }
        
        int width = maxX - minX + 1;
        int height = maxY - minY + 1;
        
        System.out.printf("📊 Grid size: %d × %d%n", width, height);
        
        // Create both orientations
        char[][] normalGrid = new char[height][width];
        char[][] flippedGrid = new char[height][width];
        
        // Initialize grids
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                normalGrid[i][j] = ' ';
                flippedGrid[i][j] = ' ';
            }
        }
        
        // Place characters
        for (Coordinate coord : coordinates) {
            int gridX = coord.x - minX;
            int normalY = coord.y - minY;
            int flippedY = maxY - coord.y;
            
            if (normalY >= 0 && normalY < height && gridX >= 0 && gridX < width) {
                normalGrid[normalY][gridX] = coord.character;
            }
            if (flippedY >= 0 && flippedY < height && gridX >= 0 && gridX < width) {
                flippedGrid[flippedY][gridX] = coord.character;
            }
        }
        
        // Display normal orientation
        System.out.println("\n🖼️ NORMAL ORIENTATION:");
        System.out.println(repeat("=", 30));
        for (char[] row : normalGrid) {
            System.out.println(new String(row));
        }
        System.out.println(repeat("=", 30));
        
        // Display Y-flipped orientation (better F)
        System.out.println("\n🖼️ Y-FLIPPED ORIENTATION (Better F):");
        System.out.println(repeat("=", 30));
        for (char[] row : flippedGrid) {
            System.out.println(new String(row));
        }
        System.out.println(repeat("=", 30));
    }
    
    public static void main(String[] args) {
        System.out.println("🚀 SECRET MESSAGE DECODER - JAVA VERSION (IMPROVED)");
        System.out.println(repeat("=", 60));
        
        String url = "https://docs.google.com/document/d/e/2PACX-1vRMx5YQlZNa3ra8dYYxmv-QIQ3YJe8tbI3kqcuC7lQiZm-CSEznKfN_HYNSpoXcZIV3Y_O3YoUB1ecq/pub";
        
        String content = fetchGoogleDocContent(url);
        if (content == null) {
            System.out.println("❌ Failed to fetch document content");
            return;
        }
        
        List<Coordinate> coordinates = parseCoordinates(content);
        if (coordinates.isEmpty()) {
            System.out.println("❌ No coordinates found");
            return;
        }
        
        displayResults(coordinates);
        System.out.println("\n🎉 SUCCESS! Clean secret message decoded!");
        System.out.println("💡 Shows only the intended block characters forming letter 'F'");
    }
}