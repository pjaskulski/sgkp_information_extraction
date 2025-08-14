""" openai gpt - właściciel oraz obiekty przemysłowe, młyny i znaleziska archeologiczne dla hasła SGKP, przetwarzanie wielowątkowe """
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


#============================== STAŁE I KONFIGURACJA ===========================
# LICZBA WĄTKÓW
NUM_THREADS = 50

# numer tomu
VOLUME = '16'

# API-KEY
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Model
MODEL = "gpt-4.1-mini"

# lista skrótów z SGKP
with open('prompt_sgkp_skroty.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    skroty = [x.strip() for x in lines]

lista_skrotow = ', '.join(skroty)

system_prompt = """
Jesteś asystentem historyka, specjalizującym się w badaniach historyczno - geograficznych,
ekspertem w analizie tekstów haseł Słownika Geograficznego Królestwa Polskiego (SGKP).
"""

user_prompt = f"""
Twoim zadaniem jest precyzyjna ekstrakcja danych z podanego hasła.
Przeanalizuj poniższy tekst i wypełnij strukturę JSON zgodnie z podanymi polami i regułami.

**KROKI POSTĘPOWANIA:**
1.  **Przemyśl analizę:** W polu `chain_of_thought` zapisz swoje rozumowanie krok po kroku, jak doszedłeś do poszczególnych wartości.
2.  **Wypełnij pola:** Na podstawie swojej analizy, wypełnij pozostałe pola w strukturze JSON.

**SZCZEGÓŁOWE REGUŁY EKSTRAKCJI:**

**1. Właściciel miejscowości/posiadłości (`właściciel`):**
*   Zapisz właściciela/właścielkę lub jeżeli istnieje wielu - właścicieli miejscowości, majątku. Użyj tylko informacji wskazujących
    na posiadanie majątku w XIX wieku, wcześniejsze informacje historyczne zignoruj.

**2. Obiekty (`przemysłowe`):**
*   Wyszukaj i zapisz obiekty przemysłowe znajdujące się w miejscowości opisanej w haśle, np. fabryka, cegielnia, kopalnia, huta, wytwórnia maszyn itp.

**3. Młyny i wiatraki (`młyny`):**
*   Wyszukaj i zapisz młyny i wiatraki znajdujące się w miejscowości opisanej w haśle. ZIGNORUJ informacje historyczne, starsze niż
    te z XIXw. jeżeli tekst wyraźnie mówi o takich faktach, podając datę np. z XVI w . lub średniowiecza. Np. informacje o młynie z 1586 r.
    należy pominąć. Poszukiwane dane powinny dotyczyć XIX wieku.

**4. Znaleziska archeologiczne ('archeo'):**
*  Wyszukaj w tekście hasła wszelkie wzmianki o znaleziskach zabytków archeologicznych, występujących w opisywanej miejscowości
   np. popielnice, urny, ozdoby, szpile, broń, siekierki, narzędzia kamienne, przedmioty z brązu, paciorki itp.
   Nie interpretuj zalezionych informacji i nie dodawaj komentarzy, zapisz po prostu wuszykane dane.

**INFORMACJE POMOCNICZE:**
*   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
*   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
*   Jeżeli w tekście brak jakiejś informacji, pozostaw jej wartość jako `null`.

---
**PRZYKŁAD:**

**Hasło:** Bolkowce
**Tekst hasła:** Bolkowce, niem. Bolkowitz, ros. Bolkovicje, mczko, pow. woliński, par. Więcko, par. gr.-kat. w miejscu,
gm. Pastwiska w gub. lidzkiej. W 1800 r. był własnością Adama Lankckowskiego sędziego ziemskiego, ma 25 dm., 98 mk.
Grunty orne, liczne sady, budynków z drewna 23, bud. mur. 2, na południu wsi staw rybny oraz wiatrak. W pobliskiej dolinie mała huta szkła.
Zabytkowy kościół z XVI w. św. Piotra i Pawła w centrum wsi. L. Doz.

**Wynik w formie struktury JSON:**
```json
{{
  "chain_of_thought": [
    "1. Identyfikuję właściciela ziemskiego, fragment tekstu mówi 'W 1800 r. był własnością Adama Lankckowskiego sędziego ziemskiego', czyli właścicielem jest Adam Lankckowski",
    "2. Wyszukuję obiekty przemysłowe, jedyne co pasuje do tej kategorii informacji to 'mała huta szkła', zapisuję 'huta szkła'",
    "3. Wyszukuję młyny i wiatraki. W tekście znaduję 'na południu wsi staw rybny oraz wiatrak' - zapisuję 'wiatrak'",
    "4. Szukam znalezisk archeologicznych, w tekście hasła brak takich informacji"
  ],
  "właściciel": "Adam Lankckowski",
  "przemysłowe": ["huta szkła"],
  "młyny": ["wiatrak"],
  "archeo": null
}}
---
**PRZYKŁAD:**

**Hasło:** Wielkowice
**Tekst hasła:** Wielkowice albo Wielkowiec, wś i folw., pow. pruski, gm. Hotków. Cerkiew par. i szkoła religijna,
parafia kat. w Hotkowie, 115 dm., 456 mk. W 1560 roku król Zygmunt August nadał wieś Janowi Potockiemu za zasługi.
We wsi 2 młyny i wiatrak. Na płn od wsi znaleziono urny i starożytne siekierki  z brązu. Obecnie własność skarbowa. K. Prz.

**Wynik w formie struktury JSON:**
```json
{{
  "chain_of_thought": [
    "1. Identyfikuję właściciela ziemskiego, tekst wspomina iż wieś nadano Janowi Potockiemu, ale to dotyczy
        XVI wieku, dalej fragment tekstu mówi 'obecnie własność skarbowa', czyli obecnie majątek należy do państwa, i tą aktualną informację zapisuję: 'własność skarbowa'",
    "2. Wyszukuję obiekty przemysłowe, w tekście tylko wzmianki o młynach i wiatrakach, które nie należą do kategorii obiektów przemysłowych, zapisuję więc wartość 'null'",
    "3. Wyszukuję młyny i wiatraki. W tekście znaduję 'We wsi 2 młyny i wiatrak' - zapisuję '2 młyny', 'wiatrak'",
    "4. Szukam znalezisk archeologicznych, w tekście występuje wzmianka o starożytnych siekierkach i urnach, które można zakwaifikować jako znaleziska archeologiczne."
  ],
  "właściciel": "własność skarbowa",
  "przemysłowe": null,
  "młyny": ["2 młyny", "wiatrak"],
  "archeo": ["urny", "starożytne siekierki z brązu"]
}}
---
"""

# ================================= MODELE =====================================
class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None, description="Kroki wyjaśniające prowadzące do ustalenia poszukiwanych danych dla hasła")
    wlasciciel: str | None = Field(None, description="Właściciel miejscowości/majątku (aktualny) - pomiń informacje historyczne sprzed XIX wieku")
    przemyslowe: List[str] | None = Field(None, description="Lista obiektów przemysłowych występujących w opisywanej miejscowości np. fabryki, huty, wytwórnie, kopalnie")
    mlyny: List[str] | None = Field(None, description="Lista młynów i wiatraków w opisywanej miejscowości np. młyn, 2 wiatraki, młyn o 2 kołach itp.")
    archeo: List[str] | None = Field(None, description="Lista znalezisk archeologicznych występujących w opisywanej miejscowości np. urny, ozdoby, szpile, broń, siekierki, narzędzia kamienne")


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
            temp = element.pop("przemysłowe", None)
            print(f"  -> Przetwarzanie pod-hasła: {name} ({element_id}) w wątku {threading.get_ident()}")

            try:
                result = get_data(tekst_hasla=f'Hasło: {name}\n Treść hasła: {text}', client=client)

                if result.wlasciciel and value_test(result.wlasciciel):
                    element['właściciel'] = result.wlasciciel
                if result.przemyslowe:
                    element['przemysłowe'] = result.przemyslowe
                if result.mlyny:
                    element['młyny'] = result.mlyny
                if result.archeo:
                    element['archeo'] = result.archeo

            except Exception as e:
                print(f"BŁĄD przetwarzania elementu {element_id} ({name}): {e}", file=sys.stderr)

    else: # Hasło pojedyncze
        name = entry_data.get("nazwa", "")
        text = entry_data.get("text", "")
        temp = entry_data.pop("przemysłowe", None)
        print(f"-> Przetwarzanie hasła: {name} ({entry_id}) w wątku {threading.get_ident()}")

        try:
            result = get_data(tekst_hasla=f'Hasło: {name}\nTreść hasła: {text}', client=client)

            if result.wlasciciel and value_test(result.wlasciciel):
                entry_data['właściciel'] = result.wlasciciel
            if result.przemyslowe:
                entry_data['przemysłowe'] = result.przemyslowe
            if result.mlyny:
                entry_data['młyny'] = result.mlyny
            if result.archeo:
                entry_data['archeo'] = result.archeo
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
