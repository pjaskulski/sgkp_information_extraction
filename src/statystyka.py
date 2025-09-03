""" SGKP - statystyka danych """
import json
import time
from pathlib import Path


VOLUMES = ['01', '02', '03', '04', '05', '06', '07', '08',
           '09', '10', '11', '12', '13', '14', '15', '16']

FIELDS = {
            'gmina': 0,
            'gubernia': 0,
            'parafia_katolicka': 0,
            'typ_punktu_osadniczego': 0,
            'właściciel': 0,
            'parafia_inna': 0,
            'archeo': 0,
            'przemysłowe': 0,
            'zabytki': 0,
            'obiekty_sakralne': 0,
            'młyny': 0,
            'architektura_krajobrazu': 0,
            'magazyny': 0,
            'kolekcjonerstwo': 0,
            'muzealnictwo': 0,
            'nekropolie': 0,
            'lesniczowki': 0,
            'budownictwo_palacowe': 0,
            'wojsko': 0,
            'rzemioslo': 0,
            'szkoły': 0,
            'urzędy': 0,
            'celne': 0,
            'biblioteki': 0,
            'gastronomia': 0,
            'opieka_zdrowotna': 0,
            'handel': 0,
            'dobroczynnosc': 0,
            'sądy': 0,
            'hodowla': 0,
            'księgarnie': 0,
            'żegluga': 0,
            'bursa': 0,
            'infrastruktura_miejska': 0,
            'poczta': 0,
            'samorzad': 0,
            'policja': 0,
            'instytucje_finansowe': 0,
            'uzdrowiska': 0,
            'stacje_drogi_zelaznej': 0
        }

FIELDS_COUNT = {
            'parafia_inna': 0,
            'archeo': 0,
            'przemysłowe': 0,
            'zabytki': 0,
            'obiekty_sakralne': 0,
            'młyny': 0,
            'architektura_krajobrazu': 0,
            'magazyny': 0,
            'kolekcjonerstwo': 0,
            'muzealnictwo': 0,
            'nekropolie': 0,
            'lesniczowki': 0,
            'budownictwo_palacowe': 0,
            'wojsko': 0,
            'rzemioslo': 0,
            'szkoły': 0,
            'urzędy': 0,
            'celne': 0,
            'biblioteki': 0,
            'gastronomia': 0,
            'opieka_zdrowotna': 0,
            'handel': 0,
            'dobroczynnosc': 0,
            'sądy': 0,
            'hodowla': 0,
            'księgarnie': 0,
            'żegluga': 0,
            'bursa': 0,
            'infrastruktura_miejska': 0,
            'poczta': 0,
            'samorzad': 0,
            'policja': 0,
            'instytucje_finansowe': 0,
            'uzdrowiska': 0,
            'stacje_drogi_zelaznej': 0
        }

TYPY_HASEL = {}


# -------------------------------- MAIN ----------------------------------------
if __name__ == '__main__':

    # pomiar czasu wykonania
    start_time = time.time()


    licznik_hasla = 0
    licznik_zbiorcze = 0
    licznik_elementy = 0

    # przetwarzanie całej kolekcji tomów
    for VOLUME in VOLUMES:
        input_path = Path('..') / 'SGKP' / 'JSON' / 'dane_etap_5' / f'sgkp_{VOLUME}.json'

        with open(input_path, "r", encoding='utf-8') as f:
            json_data = json.load(f)

            for item_result in json_data:
                rodzaj = item_result.get("rodzaj", None)

                if rodzaj == "zbiorcze":
                    licznik_zbiorcze += 1
                    elementy = item_result["elementy"]
                    for element in elementy:
                        licznik_elementy += 1

                        for field in element:
                            if field in FIELDS:
                                FIELDS[field] += 1
                            if field in FIELDS_COUNT:
                                FIELDS_COUNT[field] += len(element[field])

                        punkty_osadnicze = element.get("typ_punktu_osadniczego", None)
                        if not punkty_osadnicze:
                            typy = element.get("typ", [])
                            if typy:
                                for typ in typy:
                                    if typ in TYPY_HASEL:
                                        TYPY_HASEL[typ] += 1
                                    else:
                                        TYPY_HASEL[typ] = 1

                else:
                    licznik_hasla += 1

                    for field in item_result:
                        if field in FIELDS:
                            FIELDS[field] += 1

                        if field in FIELDS_COUNT:
                            FIELDS_COUNT[field] += len(item_result[field])

                    punkty_osadnicze = item_result.get("typ_punktu_osadniczego", None)
                    if not punkty_osadnicze:
                        typy = item_result.get("typ", [])
                        for typ in typy:
                            if typ in TYPY_HASEL:
                                TYPY_HASEL[typ] += 1
                            else:
                                TYPY_HASEL[typ] = 1

    print(f'Hasła indywidualne: {licznik_hasla}')
    print(f'Hasła zbiorcze: {licznik_zbiorcze} zawierają elementów: {licznik_elementy}')
    print("W tym:")

    for key, value in FIELDS.items():
        print(f'Kategoria: {key}, liczba haseł: {value}')
        if key in FIELDS_COUNT:
            print(f'  - liczba znalezisk: {FIELDS_COUNT[key]}')

    print()

    for key, value in sorted(TYPY_HASEL.items(), key=lambda item:item[1], reverse=True):
        if value >= 20:
            print(f'Typ: {key}, liczba haseł: {value}')

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
