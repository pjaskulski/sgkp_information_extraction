""" łączenie wyników zadań przetwarzania przez Batch API OpenAI z głównym plikiem
danych dla tomu SGKP - właściciel, obiekty przemysłowe, zabytki """
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

    response_dir = Path('..') / 'SGKP' / 'JSON' / f'response_wlasnosc_przemysl_{VOLUME}'
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
                        wlasciciel = resp_data[element_id].get("właściciel", None)
                        przemyslowe = resp_data[element_id].get("przemysłowe", None)
                        mlyny = resp_data[element_id].get("młyny", None)
                        archeo = resp_data[element_id].get("archeo", None)
                        zabytki = resp_data[element_id].get("zabytki", None)
                        architektura_krajobrazu = resp_data[element_id].get("architektura_krajobrazu", None)
                        kolekcjonerstwo = resp_data[element_id].get("kolekcjonerstwo", None)
                        muzealnictwo = resp_data[element_id].get("muzealnictwo", None)
                        nekropolie = resp_data[element_id].get("nekropolie", None)
                        rzemioslo = resp_data[element_id].get("rzemiosło", None)
                        lesniczowki = resp_data[element_id].get("leśniczowki", None)
                        budownictwo_palacowe = resp_data[element_id].get("budownictwo_pałacowe", None)
                        magazyny = resp_data[element_id].get("magazyny", None)
                        wojsko = resp_data[element_id].get("wojsko", None)
                        obiekty_sakralne = resp_data[element_id].get("obiekty_sakralne", None)
                        if wlasciciel:
                            item["właściciel"] = wlasciciel
                        if przemyslowe:
                            element["przemysłowe"] = przemyslowe
                        if mlyny:
                            element["młyny"] = mlyny
                        if archeo:
                            element["archeo"] = archeo
                        if zabytki:
                            element["zabytki"] = archeo
                        if architektura_krajobrazu:
                            element["architektura_krajobrazu"] = architektura_krajobrazu
                        if kolekcjonerstwo:
                            element["kolekcjonerstwo"] = kolekcjonerstwo
                        if muzealnictwo:
                            element["muzealnictwo"] = muzealnictwo
                        if nekropolie:
                            element["nekropolie"] = nekropolie
                        if rzemioslo:
                            element["rzemiosło"] = rzemioslo
                        if lesniczowki:
                            element["leśniczowki"] = lesniczowki
                        if budownictwo_palacowe:
                            element["budownictwo_pałacowe"] = budownictwo_palacowe
                        if magazyny:
                            element["magazyny"] = magazyny
                        if wojsko:
                            element["wojsko"] = wojsko
                        if obiekty_sakralne:
                            element["obiekty_sakralne"] = obiekty_sakralne

            else:
                item_id = item.get("ID", None)
                if item_id in resp_data:
                    wlasciciel = resp_data[item_id].get("właściciel", None)
                    przemyslowe = resp_data[item_id].get("przemysłowe", None)
                    mlyny = resp_data[item_id].get("młyny", None)
                    archeo = resp_data[item_id].get("archeo", None)
                    zabytki = resp_data[item_id].get("zabytki", None)
                    architektura_krajobrazu = resp_data[item_id].get("architektura_krajobrazu", None)
                    kolekcjonerstwo = resp_data[item_id].get("kolekcjonerstwo", None)
                    muzealnictwo = resp_data[item_id].get("muzealnictwo", None)
                    nekropolie = resp_data[item_id].get("nekropolie", None)
                    rzemioslo = resp_data[item_id].get("rzemiosło", None)
                    lesniczowki = resp_data[item_id].get("leśniczowki", None)
                    budownictwo_palacowe = resp_data[item_id].get("budownictwo_pałacowe", None)
                    magazyny = resp_data[item_id].get("magazyny", None)
                    wojsko = resp_data[item_id].get("wojsko", None)
                    obiekty_sakralne = resp_data[item_id].get("obiekty_sakralne", None)
                    if wlasciciel:
                        item["właściciel"] = wlasciciel
                    if przemyslowe:
                        item["przemysłowe"] = przemyslowe
                    if mlyny:
                        item["młyny"] = mlyny
                    if archeo:
                        item["archeo"] = archeo
                    if zabytki:
                        item["zabytki"] = archeo
                    if architektura_krajobrazu:
                        item["architektura_krajobrazu"] = architektura_krajobrazu
                    if kolekcjonerstwo:
                        item["kolekcjonerstwo"] = kolekcjonerstwo
                    if muzealnictwo:
                        item["muzealnictwo"] = muzealnictwo
                    if nekropolie:
                        item["nekropolie"] = nekropolie
                    if rzemioslo:
                        item["rzemiosło"] = rzemioslo
                    if lesniczowki:
                        item["leśniczowki"] = lesniczowki
                    if budownictwo_palacowe:
                        item["budownictwo_pałacowe"] = budownictwo_palacowe
                    if magazyny:
                        item["magazyny"] = magazyny
                    if wojsko:
                        item["wojsko"] = wojsko
                    if obiekty_sakralne:
                        item["obiekty_sakralne"] = obiekty_sakralne


    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
