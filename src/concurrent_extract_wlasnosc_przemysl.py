""" ekstrakcja danych z hasła SGKP, przetwarzanie  wielowątkowe:
- właściciel,
- obiekty przemysłowe,
- młyny,
- znaleziska archeologiczne,
- zabytki – bez świątyń czynnych
- architektura_krajobrazu – park, ogród, oranżeria, mała architektura ogrodowa
- kolekcjonerstwo
- muzealnictwo
- nekropolie – nie archeologiczne
- rzemioslo – nie przemysł
- lesniczowki – tylko leśniczówka/nadleśnictwo/gajówka
- mlyny: młyn/wiatrak
- budownictwo pałacowe, dworskie
- magazynowanie: magazyny, spichlerze
- wojsko: koszary, fort, twierdza, żandarmeria, zarząd okręgu wojskowego, strzelnica
"""
import os
import sys
import time
import json
from pathlib import Path
from typing import List
import concurrent.futures
import math
import threading
from dotenv import load_dotenv
import openai
from openai import OpenAI
from model_wlasnosc_przemysl import EntryModel
from prompt_wlasnosc_przemysl import prepare_prompt


#============================== STAŁE I KONFIGURACJA ===========================
# LICZBA WĄTKÓW
NUM_THREADS = 100 # (dla testowych danych 5, dla większych danych - 50 lub więcej)

# numer tomu lub 'test'
VOLUME = '02'
DANE = 'wlasnosc_przemysl'

# API-KEY
env_path = Path(".") / ".env_ihpan"
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

    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": s_prompt},
            {"role": "user", "content": u_prompt},
        ],
        response_format=EntryModel,
        temperature=0
    )

    return completion.choices[0].message.parsed


def value_test(value: str) -> bool:
    """ Test czy pole zawiera realną wartość. """
    if not isinstance(value, str):
        return False
    value = value.strip()
    return value not in ['', '/', 'null']


def update_record(entry: dict, result: EntryModel, thread:int):
    "uaktualnienie przekazanej struktury o nowe dane z odpowiedzi LLM "
    if result.wlasciciel and value_test(result.wlasciciel):
        entry['właściciel'] = result.wlasciciel
    if result.przemyslowe:
        entry['przemysłowe'] = result.przemyslowe
    if result.mlyny:
        entry['młyny'] = result.mlyny
    if result.archeo:
        entry['archeo'] = result.archeo
    if result.zabytki:
        entry['zabytki'] = result.zabytki
    if result.architektura_krajobrazu:
        entry['architektura_krajobrazu'] = result.architektura_krajobrazu
    if result.kolekcjonerstwo:
        entry['kolekcjonerstwo'] = result.kolekcjonerstwo
    if result.muzealnictwo:
        entry['muzealnictwo'] = result.muzealnictwo
    if result.nekropolie:
        entry['nekropolie'] = result.nekropolie
    if result.rzemioslo:
        entry['rzemioslo'] = result.rzemioslo
    if result.lesniczowki:
        entry['lesniczowki'] = result.lesniczowki
    if result.budownictwo_palacowe:
        entry['budownictwo_palacowe'] = result.budownictwo_palacowe
    if result.magazyny:
        entry['magazyny'] = result.magazyny
    if result.wojsko:
        entry['wojsko'] = result.wojsko
    if result.obiekty_sakralne:
        entry['obiekty_sakralne'] = result.obiekty_sakralne

    # log
    if result.chain_of_thought:
       with open(f'wlasnosc_przemysl_{VOLUME}_{thread}.log', 'a', encoding='utf-8') as f_log:
           f_log.write(result.chain_of_thought)


def process_entry(entry_data: dict, client: OpenAI, info:str) -> dict:
    """Przetwarza pojedyncze hasło lub hasło zbiorcze."""
    entry_id = entry_data.get("ID", "")
    rodzaj = entry_data.get("rodzaj")

    if rodzaj == "zbiorcze":
        elements = entry_data.get("elementy", [])
        for i, element in enumerate(elements):
            name = element.get("nazwa", "")
            text = element.get("text", "")
            element_id = element.get("ID", "")
            print(f"  -> [{info}] Przetwarzanie pod-hasła: {name} ({element_id}) w wątku {threading.get_ident()}")

            try:
                result = get_data(tekst_hasla=f'Hasło: {name}\n Treść hasła: {text}', client=client)
                update_record(entry=element, result=result, thread= threading.get_ident())

            except Exception as e:
                print(f"BŁĄD przetwarzania elementu {element_id} ({name}): {e}", file=sys.stderr)

    else: # Hasło pojedyncze
        name = entry_data.get("nazwa", "")
        text = entry_data.get("text", "")
        print(f"-> [{info}] Przetwarzanie hasła: {name} ({entry_id}) w wątku {threading.get_ident()}")

        try:
            result = get_data(tekst_hasla=f'Hasło: {name}\nTreść hasła: {text}', client=client)
            update_record(entry=entry_data, result=result, thread= threading.get_ident())

        except Exception as e:
            print(f"BŁĄD przetwarzania hasła {entry_id} ({name}): {e}", file=sys.stderr)

    return entry_data


def process_chunk(chunk: List[dict], worker_id: int, output_dir: Path):
    """Funkcja robocza dla wątku: przetwarza fragment danych i zapisuje do pliku."""
    print(f"Wątek {worker_id} uruchomiony, przetwarza {len(chunk)} haseł.")

    # ścieżka do zapisu wyników
    output_path = output_dir / f'output_part_{worker_id}.json'

    # oosbny klient da każdego wątku
    client = OpenAI()

    size_of_chunk = len(chunk)
    number_of_chunk = 0
    processed_results = []
    for entry in chunk:
        number_of_chunk += 1
        processed_entry = process_entry(entry, client, info=f'{number_of_chunk}/{size_of_chunk}')
        processed_results.append(processed_entry)

        # zapis wyników wątku do osobnego pliku (to nie jest optymalne, ale zajmuje mało czasu)
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(processed_results, f_out, indent=4, ensure_ascii=False)

    print(f"Wątek {worker_id} zakończył pracę. Wyniki zapisano w {output_path}")
    return len(processed_results)


# ================================== MAIN ======================================
if __name__ == "__main__":
    start_time = time.time()

    data_path = Path('..') / 'SGKP' / 'JSON' / 'dane_etap_3' /f'sgkp_{VOLUME}.json'
    output_dir = Path('..') / 'SGKP' / 'JSON' / f'output_parts_{VOLUME}_{DANE}'

    # katalog na pliki częściowe, jeśli nie istnieje
    output_dir.mkdir(exist_ok=True)

    print(f"Ładowanie danych z: {data_path}")
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
                print(f"Jeden z wątków zakończył, przetworzono {num_processed} elementów.")
            except Exception as e:
                print(f"Wystąpił błąd w jednym z wątków: {e}", file=sys.stderr)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("\n---")
    print(f'Całkowity czas wykonania: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))}')
