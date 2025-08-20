""" przygotowanie danych dla zadań Batch API OpenAI """
import os
import sys
import json
import time
import glob
from pathlib import Path
DANE = 'dane_podstawowe'
#DANE = 'wlasnosc_przemysl'
#DANE = 'instytucje_urzedy'
#DANE = 'statystyka'
#DANE = 'struktura'
#DANE = 'wlasnosc_ziemska'

if DANE == 'dane_podstawowe':
    from prompt_dane_podstawowe import prepare_prompt
    from model_dane_podstawowe import EntryModel
elif DANE == 'wlasnosc_przemysl':
    from prompt_wlasnosc_przemysl import prepare_prompt
    from model_wlasnosc_przemysl import EntryModel
elif DANE == 'instytucje_urzedy':
    from prompt_instytucje_urzedy import prepare_prompt
    from model_instytucje_urzedy import EntryModel
elif DANE == 'statystyka':
    from prompt_statystyka import prepare_prompt
    from model_statystyka import EntryModel
elif DANE == 'struktura':
    from prompt_struktura import prepare_prompt
    from model_struktura import EntryModel
elif DANE == 'wlasnosc_ziemska':
    from prompt_wlasnosc_ziemska import prepare_prompt
    from model_wlasnosc_ziemska import EntryModel
else:
    print(f'Nieprawidłowa kategoria danych: {DANE}')
    sys.exit(1)


# --------------------------- STALE i KONFIGURACJA -----------------------------
VOLUME = '15'
MODEL = "gpt-4.1-mini"

# ------------------------------- PROMPT ---------------------------------------
user_prompt = prepare_prompt(model=EntryModel)

system_prompt = """
Jesteś asystentem historyka, specjalizującym się w badaniach historyczno - geograficznych,
ekspertem w analizie tekstów haseł Słownika Geograficznego Królestwa Polskiego (SGKP).
"""

# --------------------------------- MAIN ---------------------------------------
if __name__ == '__main__':

     # pomiar czasu wykonania
    start_time = time.time()

    input_path = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}.json'
    output_dir = Path('..') / 'SGKP' / 'JSON' / f'batch_{DANE}'
    output_dir.mkdir(exist_ok=True)

    output_files = glob.glob(str(output_dir / f'sgkp_{VOLUME}_batch*.jsonl'))

    if output_files:
        for out_f in output_files:
            os.remove(out_f)

    # wczytanie danych z pliku json dla tomu
    rekordy = []
    with open(input_path, "r", encoding='utf-8') as f:
        json_data = json.load(f)

        for item_result in json_data:
            rodzaj = item_result["rodzaj"]

            if rodzaj == "zbiorcze":
                elementy = item_result["elementy"]
                for element in elementy:
                    element_nazwa = element.get("nazwa", None)
                    element_id = element.get("ID", None)
                    element_text = element.get("text", None)
                    if element_nazwa and element_id and element_text:
                        rekordy.append((element_id, element_nazwa, element_text))

            else:
                item_nazwa = item_result.get("nazwa", None)
                item_id = item_result.get("ID", None)
                item_text = item_result.get("text", None)
                if item_nazwa and item_id and item_text:
                    rekordy.append((item_id, item_nazwa, item_text))

        # pliki jsonl do przetwarzania w Batch API nie mogą przekraczać 200 MB
        # dane z tomu SGKP mogą być większe, więc są dzielone na 3-4 części
        licznik = 0
        max_rec = 5000
        file_nr = 1

        unikalny = []

        # przygotowanie pliku JSONL
        for rec in rekordy:
            licznik += 1

            # unikalny identyfikator dla każdego zapytania
            custom_id, nazwa, text = rec

            if custom_id not in unikalny:
                unikalny.append(custom_id)
            else:
                print(custom_id)
                sys.exit(1)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'{user_prompt}\n\nHasło: {nazwa}\n Treść hasła: {text}' }
            ]

            # obiekt JSON dla pojedynczego zadania wsadowego
            json_request = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "max_tokens": 1000,
                    "temperature": 0.0
                }
            }

            if licznik >= 5000:
                file_nr += 1
                licznik = 0

            output_file = Path('..') / 'SGKP' / 'JSON' / f'batch_{DANE}' / f'sgkp_{VOLUME}_batch_{file_nr}.jsonl'
            with open(output_file, 'a', encoding='utf-8') as f:
                # Zapisanie obiektu JSON jako jednej linii w pliku
                f.write(json.dumps(json_request, ensure_ascii=False) + "\n")

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
