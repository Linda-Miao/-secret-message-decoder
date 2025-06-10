import requests
import re
from typing import List, Tuple, Optional


def fetch_google_doc_content(url: str) -> Optional[str]:
    """
    Fetch content from a published Google Doc and extract text
    """
    print(" Fetching Google Doc content...")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        
        print("Document fetched successfully!")
        print(f"Content length: {len(content):,} characters")
        
        # Extract text from HTML
        if content.strip().startswith('<!DOCTYPE html>') or '<html>' in content[:200]:
            print("Extracting text from HTML...")
            
            # Remove script and style tags
            clean_html = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            clean_html = re.sub(r'<style[^>]*>.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove all HTML tags
            text_content = re.sub(r'<[^>]+>', '', clean_html)
            
            # Clean up whitespace
            clean_text = re.sub(r'\s+', ' ', text_content)
            clean_text = clean_text.strip()
            
            print(f"Extracted text length: {len(clean_text):,} characters")
            print(f"First 500 characters:")
            print(repr(clean_text[:500]))
            
            return clean_text
        else:
            print(f"First 500 characters:")
            print(repr(content[:500]))
            return content
            
    except requests.exceptions.RequestException as e:
        print(f" Error fetching document: {e}")
        return None


def parse_coordinates(content: str) -> List[Tuple[int, str, int]]:
    """
    Parse coordinate data from the content
    """
    print("Parsing coordinate data...")
    print("-" * 50)
    
    coordinates = []
    
    # The content shows concatenated format like: "0█00█10█21▀11▀22▀12▀23▀2"
    # We need to find patterns like: digit+character+digit
    
    print(f" Content length: {len(content)} characters")
    print(f" Looking for coordinate patterns in: {repr(content[-100:])}")
    
    # Method 1: Look for digit+character+digit patterns
    print(f"\n Method 1: Looking for digit+character+digit patterns...")
    
    # Find the coordinate data section (after "y-coordinate")
    coord_start = content.find("y-coordinate")
    if coord_start == -1:
        coord_start = content.find("coordinate")
    
    if coord_start != -1:
        # Get the part after the headers
        coord_data = content[coord_start + 12:]  # Skip "y-coordinate"
        print(f"Found coordinate section: {repr(coord_data[:50])}...")
        
        # Look for patterns: single_digit + special_character + single_digit
        # Use non-greedy matching and specify single digits
        pattern = r'(\d)([^\d\s])(\d)'
        matches = re.findall(pattern, coord_data)
        
        print(f" Found {len(matches)} potential coordinate matches")
        
        for match in matches:
            x_str, char, y_str = match
            try:
                x, y = int(x_str), int(y_str)
                # Only accept special characters (not letters)
                if not char.isalpha():
                    coordinates.append((x, char, y))
                    print(f" Found coordinate: ({x}, '{char}', {y})")
            except ValueError:
                continue
    
    # Method 2: Look for specific block characters
    if not coordinates:
        print(f"\n Method 2: Looking for block characters...")
        block_chars = ['█', '▀', '▄', '■', '▌', '▐', '●', '○', '◆', '◇', '★', '☆']
        
        for char in block_chars:
            if char in content:
                print(f"Found block character '{char}' in content")
                
                # Find all occurrences and extract surrounding digits
                char_positions = []
                start = 0
                while True:
                    pos = content.find(char, start)
                    if pos == -1:
                        break
                    char_positions.append(pos)
                    start = pos + 1
                
                for pos in char_positions:
                    # Look for digit before the character
                    x_val = None
                    for i in range(pos - 1, max(0, pos - 5), -1):
                        if content[i].isdigit():
                            # Extract the full number
                            num_start = i
                            while num_start > 0 and content[num_start - 1].isdigit():
                                num_start -= 1
                            x_val = int(content[num_start:i + 1])
                            break
                    
                    # Look for digit after the character
                    y_val = None
                    for i in range(pos + 1, min(len(content), pos + 5)):
                        if content[i].isdigit():
                            # Extract the full number
                            num_end = i
                            while num_end < len(content) - 1 and content[num_end + 1].isdigit():
                                num_end += 1
                            y_val = int(content[i:num_end + 1])
                            break
                    
                    if x_val is not None and y_val is not None:
                        coordinates.append((x_val, char, y_val))
                        print(f"Found coordinate: ({x_val}, '{char}', {y_val})")
    
    # Method 3: Manual parsing of the specific pattern we see
    if not coordinates:
        print(f"\n Method 3: Manual parsing of concatenated format...")
        
        # Look for the pattern at the end: "0█00█10█21▀11▀22▀12▀23▀2"
        # We need to split this carefully
        
        # Find coordinate data after headers
        coord_start = content.find("y-coordinate")
        if coord_start != -1:
            coord_section = content[coord_start + 12:]
            print(f"Coordinate section: {repr(coord_section)}")
            
            # Try to parse character by character
            i = 0
            while i < len(coord_section) - 2:
                # Look for: digit(s) + special_char + digit(s)
                if coord_section[i].isdigit():
                    # Extract the X coordinate
                    x_start = i
                    while i < len(coord_section) and coord_section[i].isdigit():
                        i += 1
                    x_val = int(coord_section[x_start:i])
                    
                    # Check if next character is special (not digit, not letter)
                    if i < len(coord_section) and not coord_section[i].isdigit() and not coord_section[i].isalpha():
                        char = coord_section[i]
                        i += 1
                        
                        # Extract the Y coordinate
                        if i < len(coord_section) and coord_section[i].isdigit():
                            y_start = i
                            while i < len(coord_section) and coord_section[i].isdigit():
                                i += 1
                            y_val = int(coord_section[y_start:i])
                            
                            coordinates.append((x_val, char, y_val))
                            print(f" Found coordinate: ({x_val}, '{char}', {y_val})")
                        else:
                            i += 1
                    else:
                        i += 1
                else:
                    i += 1
    
    print(f"\n Found {len(coordinates)} coordinates total")
    return coordinates


def build_grid(coordinates: List[Tuple[int, str, int]]) -> Optional[List[List[str]]]:
    """
    Build and display the grid
    """
    print(" Building grid...")
    print("-" * 50)
    
    if not coordinates:
        print(" No coordinates to build grid!")
        return None
    
    # Find grid bounds
    x_coords = [coord[0] for coord in coordinates]
    y_coords = [coord[2] for coord in coordinates]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    
    print(f" Grid size: {width} × {height}")
    print(f" X range: {min_x} to {max_x}")
    print(f" Y range: {min_y} to {max_y}")
    
    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Place characters
    for x, char, y in coordinates:
        grid_x = x - min_x
        grid_y = y - min_y
        grid[grid_y][grid_x] = char
        print(f"Placed '{char}' at grid ({grid_x}, {grid_y}) from coord ({x}, {y})")
    
    # Display grid
    print("\n SECRET MESSAGE:")
    print("=" * 50)
    
    # With coordinates
    print("   ", end="")
    for x in range(width):
        print(f"{(x + min_x) % 10}", end="")
    print()
    
    for y in range(height):
        print(f"{(y + min_y) % 10}: ", end="")
        for x in range(width):
            print(grid[y][x], end="")
        print()
    
    print("=" * 50)
    
    # Clean view
    print("\nCLEAN VIEW:")
    print("-" * 20)
    for row in grid:
        print(''.join(row))
    print("-" * 20)
    
    return grid


def main():
    """
    Main function
    """
    print(" SECRET MESSAGE DECODER")
    print("=" * 60)
    
    # The Google Doc URL
    url = "https://docs.google.com/document/d/e/2PACX-1vRMx5YQlZNa3ra8dYYxmv-QIQ3YJe8tbI3kqcuC7lQiZm-CSEznKfN_HYNSpoXcZIV3Y_O3YoUB1ecq/pub"
    
    # Step 1: Fetch content
    content = fetch_google_doc_content(url)
    if not content:
        print(" Failed to fetch document content")
        return
    
    # Step 2: Parse coordinates
    coordinates = parse_coordinates(content)
    if not coordinates:
        print(" No coordinates found")
        print("\n The document might not contain coordinate data in the expected format")
        print("Expected format: sequences of number, character, number")
        return
    
    # Step 3: Build and display grid
    grid = build_grid(coordinates)
    
    if grid:
        print("\nSUCCESS! Secret message decoded!")
    else:
        print(" Failed to build grid")


if __name__ == "__main__":
    main()
