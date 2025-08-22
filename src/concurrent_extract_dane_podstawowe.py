""" openai gpt - informacje podstawowe dla hasła SGKP, przetwarzanie wielowątkowe """
import os
import sys
import time
import json
from typing import List
from pathlib import Path
import concurrent.futures
import math
import threading
from dotenv import load_dotenv
import openai
from openai import OpenAI
from prompt_dane_podstawowe import prepare_prompt
from model_dane_podstawowe import EntryModel


#============================== STAŁE I KONFIGURACJA ===========================
# LICZBA WĄTKÓW
NUM_THREADS = 100 # (dla testowych danych 5, dla większych danych - 50 lub więcej)

# numer tomu lub 'test'
VOLUME = '04'
DANE = 'dane_podstawowe'

# API-KEY
env_path = Path(".") / ".env_ihpan" # ".env_ihpan"
load_dotenv(dotenv_path=env_path)
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PROJECT_ID = os.environ.get('PROJECT_ID')
openai.api_key = OPENAI_API_KEY
openai.project = PROJECT_ID

# Model
MODEL = "gpt-4.1-mini"


system_prompt = """
Jesteś asystentem historyka, specjalizującym się w badaniach historyczno - geograficznych,
ekspertem w analizie tekstów haseł Słownika Geograficznego Królestwa Polskiego (SGKP).
"""

user_prompt = prepare_prompt()


# ================================ FUNKCJE =====================================
def get_data(tekst_hasla:str, client: OpenAI):
    """ Ekstrakcja informacji za pomocą modelu językowego """

    u_prompt = f'{user_prompt}\n\n{tekst_hasla}'
    s_prompt = system_prompt
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": s_prompt},
            {"role": "user", "content": u_prompt},
        ],
        response_format=EntryModel,
        temperature=0.0
    )

    return completion.choices[0].message.parsed


def value_test(value: str) -> bool:
    """ Test czy pole zawiera realną wartość. """
    if not isinstance(value, str):
        return False
    value = value.strip()
    return value not in ['', '/', 'null']


def process_entry(entry_data: dict, client: OpenAI) -> dict:
    """Przetwarza pojedyncze hasło lub hasło zbiorcze."""
    entry_id = entry_data.get("ID", "")
    rodzaj = entry_data.get("rodzaj")

    # hasło zbiorcze
    if rodzaj == "zbiorcze":
        elements = entry_data.get("elementy", [])
        prev_powiat = None
        for i, element in enumerate(elements):
            name = element.get("nazwa", "")
            text = element.get("text", "")
            element_id = element.get("ID", "")
            print(f"  -> Przetwarzanie pod-hasła: {name} ({element_id}) w wątku {threading.get_ident()}")

            try:
                result = get_data(tekst_hasla=f'Hasło: {name}\n Treść hasła: {text}', client=client)

                if result.typ: element['typ'] = result.typ
                if result.powiat and value_test(result.powiat):
                    element['powiat_ocr'] = result.powiat
                    prev_powiat = result.powiat
                elif 'tamże' in text[:150] and prev_powiat:
                    element['powiat_ocr'] = prev_powiat
                if result.gmina and value_test(result.gmina): element['gmina'] = result.gmina
                if result.gubernia and value_test(result.gubernia): element['gubernia'] = result.gubernia
                if result.parafia_katolicka and value_test(result.parafia_katolicka): element['parafia_katolicka'] = result.parafia_katolicka
                if result.parafia_inna:
                    element['parafia_inna'] = [item.model_dump() for item in result.parafia_inna]
                if result.warianty_nazw:
                    element['warianty_nazw'] = [item.model_dump() for item in result.warianty_nazw]
                # autor na poziomie hasła głównego
                if result.autor and value_test(result.autor): entry_data['autor'] = result.autor
            except Exception as e:
                print(f"BŁĄD przetwarzania elementu {element_id} ({name}): {e}", file=sys.stderr)

    else: # Hasło pojedyncze
        name = entry_data.get("nazwa", "")
        text = entry_data.get("text", "")
        print(f"-> Przetwarzanie hasła: {name} ({entry_id}) w wątku {threading.get_ident()}")

        try:
            result = get_data(tekst_hasla=f'Hasło: {name}\nTreść hasła: {text}', client=client)

            if result.typ: entry_data['typ'] = result.typ
            if result.powiat and value_test(result.powiat): entry_data['powiat_ocr'] = result.powiat
            if result.gmina and value_test(result.gmina): entry_data['gmina'] = result.gmina
            if result.gubernia and value_test(result.gubernia): entry_data['gubernia'] = result.gubernia
            if result.parafia_katolicka and value_test(result.parafia_katolicka): entry_data['parafia_katolicka'] = result.parafia_katolicka
            if result.parafia_inna:
                entry_data['parafia_inna'] = [item.model_dump() for item in result.parafia_inna]
            if result.autor and value_test(result.autor): entry_data['autor'] = result.autor
            if result.warianty_nazw:
                entry_data['warianty_nazw'] = [item.model_dump() for item in result.warianty_nazw]
        except Exception as e:
            print(f"BŁĄD przetwarzania hasła {entry_id} ({name}): {e}", file=sys.stderr)

    return entry_data


def process_chunk(chunk: List[dict], worker_id: int, output_dir: Path):
    """Funkcja robocza dla wątku: przetwarza fragment danych i zapisuje do pliku."""
    print(f"Wątek {worker_id} uruchomiony, przetwarza {len(chunk)} haseł.")

    # ścieżka do zapisu wyników
    output_path = output_dir / f'output_part_{worker_id}.json'

    # osobny klient da każdego wątku
    client = OpenAI()

    processed_results = []
    for entry in chunk:
        processed_entry = process_entry(entry, client)
        processed_results.append(processed_entry)

        # zapis wyników wątku do osobnego pliku (to nie jest optymalne, ale zajmuje mało czasu)
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(processed_results, f_out, indent=4, ensure_ascii=False)

    print(f"Wątek {worker_id} zakończył pracę. Wyniki zapisano w {output_path}")
    return len(processed_results)


# ================================== MAIN ======================================
if __name__ == "__main__":
    start_time = time.time()

    # ścieżki
    data_path = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}.json'
    output_dir = Path('..') / 'SGKP' / 'JSON' / f'output_parts_{VOLUME}_{DANE}'

    # katalog na pliki częściowe, jeśli nie istnieje
    output_dir.mkdir(exist_ok=True)

    print(f"Ładowanie danych z: {data_path}")
    data_to_process = None
    with open(data_path, "r", encoding='utf-8') as f:
        data_to_process = json.load(f)

    if not data_to_process:
        print("Brak danych do przetworzenia. Zakończono.")
        sys.exit(0)

    # dzielenie danych na równe części dla każdego wątku
    total_entries = len(data_to_process)
    chunk_size = math.ceil(total_entries / NUM_THREADS)
    chunks = [data_to_process[i:i + chunk_size] for i in range(0, total_entries, chunk_size)]

    print(f"Uruchamianie przetwarzania dla {total_entries} haseł w {len(chunks)} wątkach.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # poszczególne partie danych przekazywane do puli wątków
        futures = [executor.submit(process_chunk, chunk, i, output_dir) for i, chunk in enumerate(chunks)]

        # oczekiwanie na zakończenie wszystkich zadań
        for future in concurrent.futures.as_completed(futures):
            try:
                num_processed = future.result()
                print(f"Jeden z wątków zakończył pracę, przetworzono {num_processed} elementów.")
            except Exception as e:
                print(f"Wystąpił błąd w jednym z wątków: {e}", file=sys.stderr)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("\n---")
    print(f'Całkowity czas wykonania: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))}')
