"""łączenie wyników zadań przetwarzania przez Batch API OpenAI z głównym plikiem danych dla tomu SGKP"""

import sys
import time
import glob
import json
from pathlib import Path


VOLUME = "15"
DANE = "dane_podstawowe"
# DANE = 'wlasnosc_przemysl'
# DANE = 'instytucje_urzedy'
# DANE = 'statystyka'
# DANE = 'struktura'
# DANE = 'wlasnosc_ziemska'

if DANE == "dane_podstawowe":
    KEYS_TO_UPDATE = [
        "warianty_nazw", "typ", "powiat", "gmina", "gubernia", "parafia_katolicka",
        "parafia_inna", "autor"
    ]
elif DANE == 'wlasnosc_przemysl':
    KEYS_TO_UPDATE = [
        "wlasciciel", "przemyslowe", "mlyny", "archeo", "zabytki",
        "architektura_krajobrazu", "kolekcjonerstwo", "muzealnictwo", "nekropolie",
        "rzemioslo", "lesniczowki", "budownictwo_palacowe", "magazyny", "wojsko",
        "obiekty_sakralne"
    ]
elif DANE == 'instytucje_urzedy':
    KEYS_TO_UPDATE = [
        "handel", "dobroczynnosc", "sady", "hodowla", "ksiegarnie", "zegluga",
        "bursy", "infrastruktura_miejska", "poczta", "samorzad", "policja",
        "instytucje_finansowe", "uzdrowiska"
    ]
elif DANE == 'statystyka':
    KEYS_TO_UPDATE = ["l_mk_statystyka", "l_dm_statystyka"]
elif DANE == 'struktura':
    KEYS_TO_UPDATE = ["ludnosc_wyznanie"]
elif DANE == 'wlasnosc_ziemska':
    KEYS_TO_UPDATE = ["lands"]
else:
    KEYS_TO_UPDATE= []


# -------------------------------- FUNCTIONS -----------------------------------
def update_record(record: dict, response_content: dict):
    "uaktualnienie przekazanej struktury o nowe dane z odpowiedzi LLM "
    for key in KEYS_TO_UPDATE:
        new_value = response_content.get(key)
        if new_value is not None:
            record[key] = new_value


# --------------------------------- MAIN ---------------------------------------
if __name__ == "__main__":

    # pomiar czasu wykonania
    start_time = time.time()

    response_dir = Path("..") / "SGKP" / "JSON" / f"response_{DANE}"
    response_files = glob.glob(str(response_dir / "*.json"))

    if not response_files:
        print("Brak plików do przetworzenia")
        sys.exit(1)

    # ścieżka do aktualnego pliku z wynikami poprzednich analiz
    input_path = Path("..") / "SGKP" / "JSON" / f"sgkp_{VOLUME}.json"
    # ścieżka do pliku z uzupełnionymy danymi
    output_path = Path("..") / "SGKP" / "JSON" / f"sgkp_{VOLUME}_{DANE}.json"

    resp_data = {}
    for resp_file in response_files:
        with open(resp_file, "r", encoding="utf-8") as f:
            file_data = json.load(f)
            for data in file_data:
                data_id = data["custom_id"]
                content = data["response"]["body"]["choices"][0]["message"]["content"]
                resp_data[data_id] = content

    with open(input_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

        for item in json_data:
            rodzaj = item.get("rodzaj", None)
            if rodzaj == "zbiorcze":
                elementy = item.get("elementy", [])
                for element in elementy:
                    element_id = element.get("ID", None)
                    if element_id in resp_data:
                        update_record(element, resp_data[element_id])
            else:
                item_id = item.get("ID", None)
                if item_id in resp_data:
                    update_record(item, resp_data[item_id])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(
        f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.'
    )
