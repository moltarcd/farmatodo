import sys
from collections import Counter

def process_text_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo '{filepath}' no existe.")
        sys.exit(1)


    char_count = len(content.replace('\r', '').replace('\n', ''))

    words = content.split()
    word_count = len(words)

    frequencies = Counter(words)

    # Ordenar
    sorted_frequencies = sorted(
        frequencies.items(), 
        key=lambda item: (-item[1], item[0])
    )

    print(f"{word_count} words")
    print(f"{char_count} characters")
    for word, freq in sorted_frequencies:
        print(f"{word}: {freq}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python word_counter.py <ruta_archivo>")
        sys.exit(1)
    
    process_text_file(sys.argv[1])