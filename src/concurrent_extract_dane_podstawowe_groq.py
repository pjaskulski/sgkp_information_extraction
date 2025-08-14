""" openai gpt - informacje podstawowe dla hasła SGKP, przetwarzanie wielowątkowe """
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
from pydantic import BaseModel, Field
from groq import Groq
import instructor


#============================== STAŁE I KONFIGURACJA ===========================
# LICZBA WĄTKÓW
NUM_THREADS = 5

# numer tomu
VOLUME = 'test' # '16'

# API-KEY
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Model
#MODEL = "openai/gpt-oss-120b"
#MODEL = "openai/gpt-oss-20b"
MODEL = "deepseek-r1-distill-llama-70b"

LOG_FILE = f'sgkp_{VOLUME}.log'
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

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
1.  **Przeanalizuj tekst hasła słownika SGKP:**
2.  **Wypełnij pola:** Na podstawie swojej analizy, wypełnij pola w strukturze JSON.

**SZCZEGÓŁOWE REGUŁY EKSTRAKCJI:**

**1. Typ Hasła (`typ`):**
*   Określ, co opisuje hasło (np. wieś, miasto, folwark, rzeka, jezioro, góra).
*   **Reguła specjalna:** Jeżeli tekst hasła zawiera skrót `ob.` (obacz), jest to odsyłacz (chyba, że
    skrót występuje w nawiasie wówczas nie oznacza to że hasło jest odsyłaczem). W takim przypadku wypełnij **tylko**
    pole `typ` wartością "odsyłacz" i pozostaw resztę pól jako `null`. Nazwa po `ob.` to inne hasło, a nie wariant nazwy.

**2. Warianty Nazw (`warianty_nazw`):**
*   Wyszukaj alternatywne lub obcojęzyczne nazwy hasła, podane zwykle na samym początku. Niekiedy warianty nazw podane są razem z datą, kiedy występowały. Warinat nazwy musi się różnić od nazwy hasła podanej na początku tekstu hasła.
*   Zapisz język (np. `niem.`, `ros.`, `łac.`). Jeśli język nie jest podany, użyj wartości `nieokr.`.

**3. Dane Administracyjne (`powiat`, `gmina`, `gubernia`):**
*   Wyodrębnij te informacje z tekstu. Często występują po skrótach: `pow.`, `gm.`, `gub.`.

**4. Parafie (`parafia_katolicka`, `parafia_inna`):**
*   Postępuj według następującej logiki:
    *   **Krok 1:** Szukaj skrótu `par.` (parafia).
    *   **Krok 2:** Jeśli znajdziesz `par.` z określeniem wyznania: kat., katol., rz.-kat. lub bez określenia wyznania, przyjmij, że to `parafia_katolicka`.
    *   **Krok 3:** Jeśli znajdziesz `par.` z wyznaniem (np. `par. gr.-kat.`, `par. ewang.`), zapisz nazwę i wyznanie w polu `parafia_inna`.
    *   **Krok 4:** **JEŚLI NIE ZNAJDZIESZ SKRÓTU `par.`**, sprawdź, czy w tekście jest mowa o "kościele parafialnym" (kościół par.) lub "cerkwi parafialnej" (cerkiew par.).
                    Jeśli tak, oznacza to, że parafia (odpowiednio katolicka lub inna) znajduje się w opisywanej miejscowości. Zapisz wówczas jako parafię nazwę miejscowości.
                    Uwaga: Zwykła wzmianka o kościele lub cerkwi (bez słowa "parafialny", "par.") NIE JEST wystarczająca do ustalenia siedziby parafii.

**5. Autor (`autor`):**
*   **Kluczowa reguła:** Autor to **TYLKO I WYŁĄCZNIE** inicjały lub nazwisko znajdujące się na **samym końcu** tekstu hasła, często po kropce lub tabulatorze (np. `Br. Ch.`, `F. S.`, `Sulimierski`).
*   **ZIGNORUJ** wszelkie inicjały i nazwiska pojawiające się w środku tekstu, ponieważ dotyczą one postaci historycznych, a nie autorów hasła.

**INFORMACJE POMOCNICZE:**
*   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
*   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
*   Nazwy zapisuj w formie mianownika.
*   Dane, które trzeba wydobyć z tekstu hasła powinny dotyczyć stanu miejscowości/obiektu z XIX wieku, informacje wcześniejsze należy pominąć.
*   Jeżeli w tekście brak jakiejś informacji, pozostaw jej wartość jako `null`.

---
**PRZYKŁAD:**

**Hasło:** Bolkowce
**Tekst hasła:** Bolkowce, niem. Bolkowitz, ros. Bolkovicje, mczko, pow. woliński, par. Więcko, par. gr.-kat. w miejscu, gm. Pastwiska w gub. lidzkiej. W 1800 r. był własnością Adama Lankckowskiego sędziego ziemskiego, ma 25 dm., 98 mk. Grunty orne, liczne sady, budynków z drewna 23, bud. mur. 2, na południu wsi staw rybny. Zabytkowy kościół z XVI w. św. Piotra i Pawła w centrum wsi. L. Doz.

**Wynik w formie struktury JSON:**
```json
{{
  "warianty_nazw": [
    {{"lang": "niem.", "wariant_nazwy": "Bolkowitz"}},
    {{"lang": "ros.", "wariant_nazwy": "Bolkovicje"}}
  ],
  "typ": "miasteczko",
  "powiat": "woliński",
  "gmina": "Pastwiska",
  "gubernia": lidzka,
  "parafia_katolicka": "Więcko",
  "parafia_inna": "gr.-kat. w miejscu",
  "autor": "L. Doz."
}}
---
**PRZYKŁAD:**

**Hasło:** Wielkowice
**Tekst hasła:** Wielkowice albo Wielkowiec, wś i folw., pow. pruski, gm. Hotków. Cerkiew par. i szkoła religijna, parafia kat. w Hotkowie, 115 dm., 456 mk. K. Prz.

**Wynik w formie struktury JSON:**
```json
{{
  "warianty_nazw": [
    {{"lang": "nieokr.", "wariant_nazwy": "Wielkowiec"}}
  ],
  "typ": "wieś, folwark",
  "powiat": "pruski",
  "gmina": "Hotków",
  "gubernia": null,
  "parafia_katolicka": "Hotków",
  "parafia_inna": "praw. Wielkowice",
  "autor": "K. Prz."
}}
---
"""

# ================================= MODELE =====================================
class NameVarModel(BaseModel):
    lang: str | None = Field(None, description="język wariantu nazwy, jeżeli podano np. niem., węg., jeżeli brak zapisz nieokr. - nieokreślony")
    wariant_nazwy: str | None = Field(None, description="wariant nazwy hasła (alias, nazwa w innym języku, nazwa występująca w dokumentach itp.)")

class EntryModel(BaseModel):
    typ: str | None = Field(None, description="Typ hasła - co hasło opisuje np. wieś, miasto, miasteczko, rzekę, górę, osiedle, krainę itp. ")
    powiat: str | None = Field(None, description="Nazwa powiatu w którym położona jest miejscowość")
    gmina: str | None = Field(None, description="Nazwa gminy w której położona jest miejscowość")
    gubernia: str | None = Field(None, description="Nazwa guberni, do której należy miejscowość")
    parafia_katolicka: str | None = Field(None, description="Nazwa parafii katolickiej (rzymsko-katolickiej)")
    parafia_inna: str | None = Field(None, description="Nazwa parafii nie katolickiej (prawosławnej, greko-katolickiej, ewangelickiej)")
    autor: str | None = Field(None, description="Inicjały lub nazwisko autora hasła, występuje na końcu hasła, część haseł nie ma podanego autora.")
    warianty_nazw: List[NameVarModel] | None = Field(None, description="Lista wariantów nazw (aliasów) dla hasła.")


# ================================ FUNKCJE =====================================
def get_data(tekst_hasla:str, client: Groq):
    """ Ekstrakcja informacji za pomocą modelu językowego """

    u_prompt = f'{user_prompt}\n\n{tekst_hasla}'
    s_prompt = system_prompt

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": s_prompt},
            {"role": "user", "content": u_prompt},
        ],
        #reasoning_effort="high",
        temperature=0,
        response_model=EntryModel,
        #response_format={type: "json_object"},
        #reasoning_format="parsed"
    )

    return completion


def value_test(value: str) -> bool:
    """ Test czy pole zawiera realną wartość. """
    if not isinstance(value, str):
        return False
    value = value.strip()
    return value not in ['', '/', 'null']


def process_entry(entry_data: dict, client: Groq) -> dict:
    """Przetwarza pojedyncze hasło lub hasło zbiorcze."""
    entry_id = entry_data.get("ID", "")
    rodzaj = entry_data.get("rodzaj")

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

                if result.typ and value_test(result.typ): element['typ'] = result.typ
                if result.powiat and value_test(result.powiat):
                    element['powiat_ocr'] = result.powiat
                    prev_powiat = result.powiat
                elif 'tamże' in text[:150] and prev_powiat:
                    element['powiat_ocr'] = prev_powiat
                if result.gmina and value_test(result.gmina): element['gmina'] = result.gmina
                if result.gubernia and value_test(result.gubernia): element['gubernia'] = result.gubernia
                if result.parafia_katolicka and value_test(result.parafia_katolicka): element['parafia_katolicka'] = result.parafia_katolicka
                if result.parafia_inna and value_test(result.parafia_inna): element['parafia_inna'] = result.parafia_inna
                if result.warianty_nazw:
                    element['warianty_nazw'] = [item.model_dump() for item in result.warianty_nazw]
            except Exception as e:
                print(f"BŁĄD przetwarzania elementu {element_id} ({name}): {e}", file=sys.stderr)
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"BŁĄD przetwarzania elementu {element_id} ({name}): {e}\n\n")

    else: # Hasło pojedyncze
        name = entry_data.get("nazwa", "")
        text = entry_data.get("text", "")
        print(f"-> Przetwarzanie hasła: {name} ({entry_id}) w wątku {threading.get_ident()}")

        try:
            result = get_data(tekst_hasla=f'Hasło: {name}\nTreść hasła: {text}', client=client)

            if result.typ and value_test(result.typ): entry_data['typ'] = result.typ
            if result.powiat and value_test(result.powiat): entry_data['powiat_ocr'] = result.powiat
            if result.gmina and value_test(result.gmina): entry_data['gmina'] = result.gmina
            if result.gubernia and value_test(result.gubernia): entry_data['gubernia'] = result.gubernia
            if result.parafia_katolicka and value_test(result.parafia_katolicka): entry_data['parafia_katolicka'] = result.parafia_katolicka
            if result.parafia_inna and value_test(result.parafia_inna): entry_data['parafia_inna'] = result.parafia_inna
            if result.autor and value_test(result.autor): entry_data['autor'] = result.autor
            if result.warianty_nazw:
                entry_data['warianty_nazw'] = [item.model_dump() for item in result.warianty_nazw]
        except Exception as e:
            print(f"BŁĄD przetwarzania hasła {entry_id} ({name}): {e}", file=sys.stderr)
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"BŁĄD przetwarzania hasła {entry_id} ({name}): {e}\n\n")

    return entry_data


def process_chunk(chunk: List[dict], worker_id: int, output_dir: Path):
    """Funkcja robocza dla wątku: przetwarza fragment danych i zapisuje do pliku."""
    print(f"Wątek {worker_id} uruchomiony, przetwarza {len(chunk)} haseł.")

    # ścieżka do zapisu wyników
    output_path = output_dir / f'output_part_{worker_id}.json'

    # osobny klient da każdego wątku
    client = instructor.from_groq(Groq(), mode=instructor.Mode.JSON)

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

    # ścieżki
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
