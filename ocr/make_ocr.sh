#!/bin/bash

# === Konfiguracja ===
# Plik, do którego zostanie zapisany cały rozpoznany tekst
OUTPUT_FILE="sgkp_09_hasla.txt"
# Języki OCR: polski jako główny, niemiecki jako dodatkowy
LANGUAGES="pol_best+deu"
# Tryb segmentacji strony (PSM) dla Tesseracta
# PSM 3: Fully automatic page segmentation, but no OSD.
# PSM 4: Assume a single column of text of variable sizes.
# PSM 6: Assume a single uniform block of text.
TESSERACT_PSM="3"

# === Sprawdzenie zależności ===
if ! command -v tesseract &> /dev/null; then
    echo "BŁĄD: Tesseract OCR nie jest zainstalowany. Proszę go zainstalować."
    echo "Na przykład w systemach Debian/Ubuntu: sudo apt install tesseract-ocr"
    exit 1
fi

# Sprawdzenie danych językowych dla polskiego
if ! tesseract --list-langs | grep -qE "\bpol_best\b"; then
    echo "BŁĄD: Brak danych języka polskiego dla Tesseracta."
    exit 1
fi

# Sprawdzenie danych językowych dla niemieckiego
if ! tesseract --list-langs | grep -qE "\bdeu\b"; then
    echo "BŁĄD: Brak danych języka niemieckiego dla Tesseracta."
    exit 1
fi

# === Główna część skryptu ===

# Wyczyść lub utwórz plik wyjściowy
> "$OUTPUT_FILE"

echo "Rozpoczynanie przetwarzania OCR dla plików TIF w bieżącym katalogu..."
echo "Języki OCR: $LANGUAGES"
echo "Tryb segmentacji strony (PSM): $TESSERACT_PSM"
echo "Plik wyjściowy: $OUTPUT_FILE"
echo "--------------------------------------------------"

processed_files=0
shopt -s nullglob

for image_file in *.tif ; do
    if [[ -f "$image_file" ]]; then
        echo "Przetwarzanie pliku: $image_file ..."
        
        current_input_file="$image_file"
        
        raw_ocr_text=$(tesseract "$current_input_file" stdout -l "$LANGUAGES" --psm "$TESSERACT_PSM" 2>/dev/null)
        
        if [ $? -ne 0 ]; then
            echo "  BŁĄD: Tesseract nie powiódł się dla pliku $current_input_file. Pomijanie post-processingu dla tego pliku."
            processed_text="BŁĄD OCR DLA PLIKU: $image_file" # Zapisz informację o błędzie
        else
            # Post-processing tekstu:
            dehyphenated_text=$(echo "$raw_ocr_text" | sed 's/-\n//g')

            # 2. Łączenie wierszy w akapity i separacja akapitów pustym wierszem.
            processed_text=$(echo "$dehyphenated_text" | awk '
                BEGIN {
                    RS = ""  # Rekordy (akapity) oddzielone pustymi liniami
                    FS = "\n" # Pola w rekordzie (linie) oddzielone newline
                    OFS = " " # Separator wyjściowy pól (spacja do łączenia linii)
                }
                {
                    $1 = $1 # Przebuduj rekord $0, łącząc pola (linie) za pomocą OFS
                    gsub(/^[[:space:]]+|[[:space:]]+$/, "", $0) # Usuń białe znaki na początku/końcu akapitu
                    gsub(/[[:space:]]{2,}/, " ", $0)   # Znormalizuj wielokrotne spacje do pojedynczej
                    
                    if (length($0) > 0) {
                        print $0 # Wydrukuj przetworzony akapit
                        print "" # Wydrukuj pustą linię jako separator akapitów
                    }
                }
            ')
        fi

        # Zapis przetworzonego tekstu do pliku wyjściowego
        printf "%s" "$processed_text" >> "$OUTPUT_FILE"
        
        echo "Zakończono przetwarzanie: $(basename "$image_file")"
        processed_files=$((processed_files + 1))
    fi
done

shopt -u nullglob

echo "--------------------------------------------------"
if [ "$processed_files" -eq 0 ]; then
    echo "Nie znaleziono plików .tif w bieżącym katalogu."
else
    echo "Przetwarzanie zakończone. Przetworzono $processed_files plików."
    echo "Wynik został zapisany do pliku: $OUTPUT_FILE"

    if command -v perl &> /dev/null; then
        perl -i -0777 -pe 's/\n\n(\n*===== Koniec pliku:)/\n$1/g; s/\n{3,}/\n\n/g; s/\n*\z/\n/g' "$OUTPUT_FILE"
        echo "Plik wyjściowy został dodatkowo oczyszczony z nadmiarowych pustych linii."
    else
        echo "Opcjonalne oczyszczanie Perlem pominięte (Perl nie jest zainstalowany)."
    fi
fi
