""" łączenie wyników zadań przetwarzania przez Batch API OpenAI z głównym plikiem danych dla tomu SGKP """
import sys
import time
import glob
import json
from pathlib import Path


VOLUME = '15'


# --------------------------------- MAIN ---------------------------------------
if __name__ == '__main__':

     # pomiar czasu wykonania
    start_time = time.time()

    response_dir = Path('..') / 'SGKP' / 'JSON' / 'response'
    response_files = glob.glob(str(response_dir / '*.json'))

    if not response_files:
        print('Brak plików do przetworzenia')
        sys.exit(1)

    input_path = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}.json'
    output_path = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}_new.json'

    resp_data = {}
    for resp_file in response_files:
        with open(resp_file, 'r', encoding='utf-8') as f:
            file_data = json.load(f)
            for data in file_data:
                data_id = data["custom_id"]
                content = data["response"]["body"]["choices"][0]["message"]["content"]
                resp_data[data_id] = content

    with open(input_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

        for item in json_data:
            rodzaj = item.get("rodzaj", None)
            if rodzaj == "zbiorcze":
                elementy = item.get("elementy", [])
                for element in elementy:
                    element_id = element.get("ID", None)
                    if element_id in resp_data:
                        warianty_nazw = resp_data[element_id].get("warianty_nazw")
                        typ = resp_data[element_id].get("typ")
                        powiat = resp_data[element_id].get("powiat")
                        gmina = resp_data[element_id].get("gmina")
                        gubernia = resp_data[element_id].get("gubernia")
                        parafia_katolicka = resp_data[element_id].get("parafia_katolicka")
                        parafia_inna = resp_data[element_id].get("parafia_inna")
                        autor = resp_data[element_id].get("autor")
                        if typ:
                            element["typ"] = typ
                        if powiat:
                            element["powiat"] = powiat
                        if gmina:
                            element["gmina"] = gmina
                        if gubernia:
                            element["gubernia"] = gubernia
                        if parafia_katolicka:
                            element["parafia_katolicka"] = parafia_katolicka
                        if parafia_inna:
                            element["parafia_inna"] = parafia_inna
                        if warianty_nazw:
                            element["warianty_nazw"] = warianty_nazw
            else:
                item_id = item.get("ID", None)
                if item_id in resp_data:
                    warianty_nazw = resp_data[item_id].get("warianty_nazw")
                    typ = resp_data[item_id].get("typ")
                    powiat = resp_data[item_id].get("powiat")
                    gmina = resp_data[item_id].get("gmina")
                    gubernia = resp_data[item_id].get("gubernia")
                    parafia_katolicka = resp_data[item_id].get("parafia_katolicka")
                    parafia_inna = resp_data[item_id].get("parafia_inna")
                    autor = resp_data[item_id].get("autor")
                    if typ:
                        item["typ"] = typ
                    if powiat:
                        item["powiat"] = powiat
                    if gmina:
                        item["gmina"] = gmina
                    if gubernia:
                        item["gubernia"] = gubernia
                    if parafia_katolicka:
                        item["parafia_katolicka"] = parafia_katolicka
                    if parafia_inna:
                        item["parafia_inna"] = parafia_inna
                    if warianty_nazw:
                        item["warianty_nazw"] = warianty_nazw


    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
