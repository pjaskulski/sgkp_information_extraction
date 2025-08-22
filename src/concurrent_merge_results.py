""" sklejanie wyników zapiszanych w osobnych wątkach """
import sys
import json
from pathlib import Path
import glob


# nr tomu lub 'test'
VOLUME = '09'
DANE = 'dane_podstawowe'
#DANE = 'wlasnosc_przemysl'
# DANE = 'instytucje_urzedy'
# DANE = 'statystyka'
# DANE = 'struktura'
# DANE = 'wlasnosc_ziemska'

# ścieżka do oryginalnego pliku, który był źródłem danych
ORIGINAL_DATA_PATH = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}.json'

# katalog, w którym znajdują się częściowe pliki wynikowe
PARTS_DIR = Path('..') / 'SGKP' / 'JSON' / f'output_parts_{VOLUME}_{DANE}'

# nazwa finalnego, połączonego pliku JSON
FINAL_OUTPUT_PATH = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}_{DANE}_merged.json'


# ================================ MAIN ========================================
if __name__ == "__main__":
    print("Rozpoczynanie łączenia plików...")

    # wczytywanie przetworzonych danych z plików częściowych do słownika dla szybkiego dostępu
    processed_data_map = {}
    part_files = glob.glob(str(PARTS_DIR / 'output_part_*.json'))

    if not part_files:
        print(f"BŁĄD: Nie znaleziono żadnych plików częściowych w katalogu '{PARTS_DIR}'.")
        sys.exit(1)

    print(f"Znaleziono {len(part_files)} plików częściowych do połączenia.")

    for file_path in part_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for entry in data:
                entry_id = entry.get("ID")
                if entry_id:
                    processed_data_map[entry_id] = entry
                else:
                    print(f"OSTRZEŻENIE: Znaleziono wpis bez ID w pliku {file_path}")

    print(f"Wczytano {len(processed_data_map)} unikalnych, przetworzonych haseł.")

    # wczytywanie oryginalnego pliku JSON
    with open(ORIGINAL_DATA_PATH, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    print(f"Wczytano {len(original_data)} haseł z oryginalnego pliku: {ORIGINAL_DATA_PATH}")

    # finalna lista z uzupełneniem wpisów
    final_data = []
    updated_count = 0
    for original_entry in original_data:
        entry_id = original_entry.get("ID")

        # jeśli hasło zostało przetworzone, użyj nowej wersji
        if entry_id in processed_data_map:
            final_data.append(processed_data_map[entry_id])
            updated_count += 1
        # w przeciwnym razie, zachowaj oryginalną wersję
        else:
            final_data.append(original_entry)

    # zapis danych do nowego pliku
    with open(FINAL_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    print('---')
    print(f"Zaktualizowano {updated_count} haseł.")
    print(f"Uzupełniony plik: {FINAL_OUTPUT_PATH}")
