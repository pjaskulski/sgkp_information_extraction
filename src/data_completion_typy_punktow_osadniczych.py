""" SGKP - uzupełnienie typów punktów osadniczych """
import os
import json
import time
import csv
from pathlib import Path


VOLUMES = ['01', '02', '03', '04', '05', '06', '07', '08',
           '09', '10', '11', '12', '13', '14', '15', '16']

# -------------------------------- MAIN ----------------------------------------
if __name__ == '__main__':

    # pomiar czasu wykonania
    start_time = time.time()

    typy_file = Path('..') / 'dictionary' / 'typy_punktow_osadniczych_v2.csv'

    typy = {}
    with open(typy_file, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",", quotechar='"')
        for row in csv_reader:
            # "typ_model","typ_punktu_osadniczego"
            rodzaj = row["typ_model"].strip()
            typ = row["typ_punktu_osadniczego"].strip()
            typy[rodzaj] = typ

    typ_nieznany = []

    # przetwarzanie całej kolekcji tomów
    for VOLUME in VOLUMES:
        input_path = Path('..') / 'SGKP' / 'JSON' / 'merged_dane_podstawowe' / f'sgkp_{VOLUME}_powiaty.json'
        output_path = Path('..') / 'SGKP' / 'JSON' / 'merged_dane_podstawowe' / f'sgkp_{VOLUME}_typy_punktow.json'

        if os.path.exists(output_path):
            os.remove(output_path)

        with open(input_path, "r", encoding='utf-8') as f:
            json_data = json.load(f)

            for item_result in json_data:
                nazwa = item_result["nazwa"]
                item_id = item_result["ID"]
                strona = item_result["strona"]
                rodzaj = item_result.get("rodzaj", None)

                if rodzaj == "zbiorcze":
                    elementy = item_result["elementy"]
                    for element in elementy:
                        element_typy = element.get("typ", [])
                        if not element_typy:
                            element_typy = ['miejscowość']
                            element['typ'] = element_typy

                        typy_osadnicze = []

                        for typ in element_typy:
                            if typ in typy:
                                if typy[typ].strip() != 'nie dotyczy':
                                    typy_osadnicze.append(typy[typ])
                            else:
                                if typ not in typ_nieznany:
                                    typ_nieznany.append(typ)
                        if typy_osadnicze:
                            element["typ_punktu_osadniczego"] = typy_osadnicze
                else:
                    item_typy = item_result.get("typ", None)
                    if not item_typy:
                        item_typy = ['miejscowość']
                        item_result['typ'] = item_typy

                    typy_osadnicze = []

                    for typ in item_typy:
                        if typ in typy:
                            if typy[typ].strip() != 'nie dotyczy':
                                typy_osadnicze.append(typy[typ])
                        else:
                            if typ not in typ_nieznany:
                                typ_nieznany.append(typ)
                    if typy_osadnicze:
                        item_result["typ_punktu_osadniczego"] = typy_osadnicze

        # zapis
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(json_data, f_out, indent=4, ensure_ascii=False)

    for t in typ_nieznany:
        print(t)

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
