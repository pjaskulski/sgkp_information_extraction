""" ekstrakcja danych z hasła SGKP, przetwarzanie  wielowątkowe:
- liczba mieszkańców
- liczba domów
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
from pydantic import BaseModel, Field
from prompt_statystyka import prepare_prompt


#============================== STAŁE I KONFIGURACJA ===========================
# LICZBA WĄTKÓW
NUM_THREADS = 5 # dla dużych zbiorów - 50

# numer tomu
VOLUME = 'test'

# API-KEY
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Model
MODEL = "gpt-4.1-mini"

system_prompt = """
Jesteś asystentem historyka, specjalizującym się w badaniach historyczno - geograficznych,
ekspertem w analizie tekstów haseł Słownika Geograficznego Królestwa Polskiego (SGKP).
"""

user_prompt = prepare_prompt()


# ================================= MODELE =====================================
class LiczbaMkModel(BaseModel):
    data: str | None = Field(None, description="Data dla której podano liczbę mieszkańców, lub sformułowanie 'obecnie'")
    liczba: str | None = Field(None, description="Liczba mieszkańców")

class LiczbaDmModel(BaseModel):
    data: str | None = Field(None, description="Data dla której podano liczbę domów, lub sformułowanie 'obecnie'")
    liczba: str | None = Field(None, description="Liczba domów")

class SettlementMkStatModel(BaseModel):
    dotyczy: str | None = Field(None, description="czego dotyczą dane: główna miejscowość, inne miejsce opisane w haśle np. folwark, gmina")
    liczba: List[LiczbaMkModel] | None = Field(None, description="Liczba mieszkańców (wiele, jeżeli ppodano dane dla różnych lat)")

class SettlementDmStatModel(BaseModel):
    dotyczy: str | None = Field(None, description="czego dotyczą dane: główna miejscowość, inne miejsce opisane w haśle np. folwark, gmina")
    liczba: List[LiczbaDmModel] | None = Field(None, description="Liczba domów (wiele, jeżeli ppodano dane dla różnych lat)")

class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None, description="Kroki wyjaśniające prowadzące do ustalenia poszukiwanych danych dla hasła")
    l_mk_statystyka: List[SettlementMkStatModel] | None = Field(None, description="Dane o liczbie mieszkańców podane w tekście hasła")
    l_dm_statystyka: List[SettlementDmStatModel] | None = Field(None, description="Dane o liczbie domów podane w tekście hasła")

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


def process_entry(entry_data: dict, client: OpenAI) -> dict:
    """Przetwarza pojedyncze hasło lub hasło zbiorcze."""
    entry_id = entry_data.get("ID", "")
    rodzaj = entry_data.get("rodzaj")

    if rodzaj == "zbiorcze":
        elements = entry_data.get("elementy", [])
        for i, element in enumerate(elements):
            name = element.get("nazwa", "")
            text = element.get("text", "")
            element_id = element.get("ID", "")
            print(f"  -> Przetwarzanie pod-hasła: {name} ({element_id}) w wątku {threading.get_ident()}")

            try:
                result = get_data(tekst_hasla=f'Hasło: {name}\n Treść hasła: {text}', client=client)

                if result.l_mk_statystyka:
                    element['l_mk_statystyka'] = [item.model_dump() for item in result.l_mk_statystyka]
                if result.l_dm_statystyka:
                    element['l_dm_statystyka'] = [item.model_dump() for item in result.l_dm_statystyka]

            except Exception as e:
                print(f"BŁĄD przetwarzania elementu {element_id} ({name}): {e}", file=sys.stderr)

    else: # Hasło pojedyncze
        name = entry_data.get("nazwa", "")
        text = entry_data.get("text", "")
        print(f"-> Przetwarzanie hasła: {name} ({entry_id}) w wątku {threading.get_ident()}")

        try:
            result = get_data(tekst_hasla=f'Hasło: {name}\nTreść hasła: {text}', client=client)

            if result.l_mk_statystyka:
                entry_data['l_mk_statystyka'] = [item.model_dump() for item in result.l_mk_statystyka]
            if result.l_dm_statystyka:
                entry_data['l_dm_statystyka'] = [item.model_dump() for item in result.l_dm_statystyka]


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

    processed_results = []
    for entry in chunk:
        processed_entry = process_entry(entry, client)
        processed_results.append(processed_entry)

        # Zapis wyników wątku do osobnego pliku
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(processed_results, f_out, indent=4, ensure_ascii=False)

    print(f"Wątek {worker_id} zakończył pracę. Wyniki zapisano w {output_path}")
    return len(processed_results)


# ================================== MAIN ======================================
if __name__ == "__main__":
    start_time = time.time()

    data_path = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}.json'
    output_dir = Path('..') / 'SGKP' / 'JSON' / f'output_parts_{VOLUME}'

    # Utwórz katalog na pliki częściowe, jeśli nie istnieje
    output_dir.mkdir(exist_ok=True)

    print(f"Ładowanie danych z: {data_path}")
    with open(data_path, "r", encoding='utf-8') as f:
        data_to_process = json.load(f)

    if not data_to_process:
        print("Brak danych do przetworzenia. Zakończono.")
        sys.exit(0)

    # Dzielenie danych na równe części dla każdego wątku
    total_entries = len(data_to_process)
    chunk_size = math.ceil(total_entries / NUM_THREADS)
    chunks = [data_to_process[i:i + chunk_size] for i in range(0, total_entries, chunk_size)]

    print(f"Uruchamianie przetwarzania dla {total_entries} haseł w {len(chunks)} wątkach.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # poszczególne partie danych przekazywane do puli wątków
        futures = [executor.submit(process_chunk, chunk, i, output_dir) for i, chunk in enumerate(chunks)]

        # Oczekiwanie na zakończenie wszystkich zadań
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
