""" przygotowanie danych dla zadań Batch API OpenAI - właściciel, przemysł, zabytki """
import os
import sys
import json
import time
import glob
from typing import List
from pathlib import Path
from pydantic import BaseModel, Field


# --------------------------- STALE i KONFIGURACJA -----------------------------
VOLUME = '15'
MODEL = "gpt-4.1-mini"

# ------------------------------- MODEL ----------------------------------------
class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None, description="Kroki wyjaśniające prowadzące do ustalenia poszukiwanych danych dla hasła")
    wlasciciel: str | None = Field(None, description="Właściciel miejscowości/majątku (aktualny) - pomiń informacje historyczne sprzed XIX wieku")
    przemyslowe: List[str] | None = Field(None, description="Lista obiektów przemysłowych występujących w opisywanej miejscowości np. fabryki, huty, wytwórnie, kopalnie")
    mlyny: List[str] | None = Field(None, description="Lista młynów i wiatraków w opisywanej miejscowości np. młyn, 2 wiatraki, młyn o 2 kołach itp.")
    archeo: List[str] | None = Field(None, description="Lista znalezisk archeologicznych występujących w opisywanej miejscowości np. urny, ozdoby, szpile, broń, siekierki, narzędzia kamienne")
    zabytki: List[str] | None = Field(None, description="lista zabytków, ruin")
    architektura_krajobrazu: List[str] | None = Field(None, description="lista obiektów architektury krajobrazu np. park, ogród, oranżeria")
    kolekcjonerstwo: List[str] | None = Field(None, description="lista różnego rodzaju zbiorów: monet, książek, rycin (ale nie muzea!)")
    muzealnictwo: List[str] | None = Field(None, description="instytucje: muzea, gabinety archeologiczne")
    nekropolie: List[str] | None = Field(None, description="cmentarze, grobowce (bez obiektów archeologicznych)")
    rzemioslo: List[str] | None = Field(None, description="rzemieślnicy lub zakłady rzemieślnicze np. krawiec, kaletnik, stolarz, (pomiń przemysł, fabryki)")
    lesniczowki: List[str] | None = Field(None, description="leśniczówki, nadleśnictwa, gajówki")
    budownictwo_palacowe: List[str] | None = Field(None, description="obiekty pałacowe, dwory")
    magazyny: List[str] | None = Field(None, description="magazyny, spichlerze")
    wojsko: List[str] | None = Field(None, description="lista obiektów wojskowych np. koszary, fort, twierdza, żandarmeria, zarząd okręgu wojskowego, strzelnica")
    obiekty_sakralne: List[str] | None = Field(None, description="np. kościół, meczet, kaplica, synagoga, cerkiew, klasztor, dom modlitwy, sobór, katedra, jeżeli podano to z wezwaniem")

# ------------------------------- PROMPT ---------------------------------------

# lista skrótów z SGKP
with open('prompt_sgkp_skroty.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    skroty = [x.strip() for x in lines]

lista_skrotow = ', '.join(skroty)

system_prompt = """
Jesteś asystentem historyka, specjalizującym się w badaniach historyczno - geograficznych,
ekspertem w analizie tekstów haseł Słownika Geograficznego Królestwa Polskiego (SGKP).
"""

json_schema = EntryModel.model_json_schema()

user_prompt = f"""
    Twoim zadaniem jest precyzyjna ekstrakcja danych z podanego hasła.
    Przeanalizuj poniższy tekst i wypełnij strukturę JSON zgodnie z podanymi polami i regułami.

    **KROKI POSTĘPOWANIA:**
    1.  **Przemyśl analizę:** W polu `chain_of_thought` zapisz swoje rozumowanie krok po kroku, jak doszedłeś do poszczególnych wartości.
    2.  **Wypełnij pola:** Na podstawie swojej analizy, wypełnij pozostałe pola w strukturze JSON.

    **SZCZEGÓŁOWE REGUŁY EKSTRAKCJI:**

    Wyszukaj i zapisz w polach struktury JSON informacje o poszukiwanych obiektach
    Uwzględniaj  **TYLKO I WYŁĄCZNIE** te znajdujące się na terenie opisywanej miejscowości.

    **1. Właściciel miejscowości/posiadłości (pole `właściciel`):**
    *   Zapisz właściciela/właścielkę lub jeżeli istnieje wielu - właścicieli miejscowości, majątku. Użyj tylko informacji wskazujących na posiadanie majątku w XIX wieku, wcześniejsze informacje historyczne zignoruj.

    **2. Obiekty (`przemysłowe`):**
    *   obiekty przemysłowe znajdujące się w miejscowości opisanej w haśle, np. fabryka, cegielnia, kopalnia, huta, wytwórnia maszyn itp. Uwaga: nie są obiektem przemysłowym młyny i wiatraki - te powinny trafić do innego pola ('młyny')

    **3. Młyny i wiatraki (`młyny`):**
    *   młyny i wiatraki znajdujące się w miejscowości opisanej w haśle. ZIGNORUJ informacje historyczne, starsze niż
        te z XIXw. jeżeli tekst wyraźnie mówi o takich faktach, podając datę np. z XVI w . lub średniowiecza. Np. informacje o młynie z 1586 r. należy pominąć. Poszukiwane dane powinny dotyczyć XIX wieku.

    **4. Znaleziska archeologiczne ('archeo'):**
    *   wszelkie wzmianki o znaleziskach zabytków archeologicznych, występujących w opisywanej miejscowości np. popielnice, urny, ozdoby, szpile, broń, siekierki, narzędzia kamienne, przedmioty z brązu, paciorki itp. Nie interpretuj zalezionych informacji i nie dodawaj komentarzy, zapisz po prostu wyszukane dane.

    **5. Zabytki ('zabytki')**
    *   obiekty zabytkowe np. zamki, ruiny zamków, pomiń czynne świątynie i inne obiekty sakralne, pomiń zabytki archeologiczne.

    **6. Architektura_krajobrazu ('architektura_krajobrazu')**
    *   obiekty architektury krajobrazu np. park, ogród, oranżeria, mała architektura ogrodowa - stworzone przez człowieka.

    **7. Kolekcjonerstwo ('kolekcjonerstwo')**
    *   informacje o różnego rodzaju zbiorach, znajdujących się w opisywanej przez hasło miejscowości: księgozbiory, zbiory medali, zbiory monet, zbiory rycin, kolekcje obrazów, kolekcje rzeźb. Pomiń informacje o muzeach, te powinny trafić do innego pola (muzealnictwo)

    **8. Muzealnictwo ('muzealnictwo')**
    *   wyszukaj i zapisz informacje na temat muzeów, gabinetów archeologicznych, anatomicznych znajdujących się w opisywanej miejscowości. Chodzi o instytucje, nie uwzględniaj prywatnych zbiorów, kolekcji - te powinny trafić do innej kategorii (kolekcjonerstwo).

    **9. Nekropolie ('nekropolie')**
    *   informacje dotyczące cmentarzy, grobowców znajdujących się na terenie opisywanej miejscowości (informacje archeologiczne np. o kurhanach oraz ruiny - pomiń).

    **10. Rzemiosło ('rzemiosło')**
    *    wyszukaj informacje na temat rzemieśników lub zakładów rzemieślniczych funkcjonujących na obszarze opisywanej miejscowości (np. krawiec, kaletnik, stolarz itp.), pomiń obiekty o charaktrze zakładów przemysłowych, fabryk. Uwzględnij tylko informacje współczesne dla autorów Słownika (XIX wiek), informacje historyczne, dotyczące np. XVI wieku - pomiń.

    **11. Leśniczówki ('leśniczówki')**
    *   obiekty typu: leśniczówka, nadleśnictwo, gajówka, försterei, strażnica leśna, jegierówka

    **12. Budownictwo pałacowe, dworskie ('budownictwo_pałacowe')**
    *   obiekty pałacowe, dwory.

    **13. Magazynowanie ('magazyny')**
    *   poszukiwane obiekty: magazyn, spichlerz, skład, świren, elewator

    **14. Wojsko ('wojsko')**
    *   poszukiwane obiekty: koszary, fort, twierdza, żandarmeria, zarząd okręgu wojskowego, strzelnica.

    **15. Obiekty sakralne ('obiekty_sakralne')**
    *   obiekty sakralne (budowle): kościół, meczet, kaplica, synagoga, cerkiew, klasztor, dom modlitwy, sobór, katedra (jeżeli podano to cała nazwa, wezwanie itp.).


    **INFORMACJE POMOCNICZE:**
    *   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
    *   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
    *   Nazwy zapisuj w formie mianownika.
    *   Jeżeli w tekście brak jakiejś informacji, pomiń daną kategorię informacji w wynikowej strukturze.

    Schemat JSON:
    {json.dumps(json_schema, indent=2, ensure_ascii=False)}

    ---
    **PRZYKŁAD:**

    **Hasło:** Bolkowce
    **Tekst hasła:** Bolkowce, niem. Bolkowitz, ros. Bolkovicje, mczko, pow. woliński, par. Więcko, par. gr.-kat. w miejscu, gm. Pastwiska w gub. lidzkiej. W 1820 r. był własnością Adama Lankckowskiego sędziego ziemskiego, który wybudował na skraju wsi drewniany dwór, ma 25 dm., 98 mk. Grunty orne, liczne sady, budynków z drewna 23, bud. mur. 2, na południu wsi staw rybny oraz wiatrak. W pobliskiej dolinie mała huta szkła, we wsi 1 stolarz. Ruiny wieży rycerskiej z XIII w. w centrum wsi. L. Doz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "1. Identyfikuję właściciela ziemskiego, fragment tekstu mówi 'W 1800 r. był własnością Adama Lankckowskiego sędziego ziemskiego', czyli właścicielem jest Adam Lankckowski",
        "2. Wyszukuję obiekty przemysłowe, jedyne co pasuje do tej kategorii informacji to 'mała huta szkła', zapisuję 'huta szkła'",
        "3. Wyszukuję młyny i wiatraki. W tekście znaduję 'na południu wsi staw rybny oraz wiatrak' - zapisuję 'wiatrak'",
        "4. Szukam znalezisk archeologicznych, w tekście hasła brak takich informacji, pomijam pole w strukturze json",
        "5. Analizuję tekst pod względem występowania informacji o zabytkach, znajduję wzmiankę o riunach wieży rycerskiej, to kwalifikuje się do kategorii 'zabytki', zapisuję w tym polu 'wieża rycerska z XIII w.'",
        "6. Szukam obiektów pasujących do kategorii architektura krajobrazu, brak takich danych, pomijam pole w strukturze json",
        "7. Wyszukuję zbiory i kolekcje, brak takich danych, pomijam pole w strukturze json",
        "8. Analizuję tekst w zakresie występowania muzeów, gabinetów ze zbiorami, brak takich danych, pomijam pole w strukturze json",
        "9. Szukam cmentarzy, grobowców, brak takich danych, pomijam pole w strukturze json",
        "10. Wyszukuję wzmanek o rzemieślnikach, znajduję fragment 'we wsi 1 stolarz', zapisuję na liście '1 stolarz'",
        "11. Badam czy tekst wspomina o leśniczówkach lub podobnych obiektach, ale nie znajduję, pomijam więc pole w strukturze json",
        "12. Szukam budynków pałacowych, dworów, znajduję wzmiankę 'wybudował na skraju wsi drewniany dwór', informacja dotyczy XIX wieku (1820), zapisuję w polu wartość 'drewniany dwór'",
        "13. Szukam informacji o magazynowanach i spichlerzach, brak takich danych, pomijam pole w strukturze json",
        "14. Przeszukanie tekstu w zakresie obiektów związanych z wojskowością nie dało żadnych rezultatów, pomijam więc pole w strukturze json",
        "15. Szukam obiektów sakralnych w tekście, lecz nie dało to żadnych rezultatów, pomijam więc pole w strukturze json"
    ],
    "właściciel": "Adam Lankckowski",
    "przemysłowe": ["huta szkła"],
    "młyny": ["wiatrak"],
    "zabytki": ["wieża rycerska z XIII w."],
    "rzemiosło": ["1 stolarz"],
    "budownictwo_pałacowe": ["drewniany dwór"]
    }}
    ---
    **PRZYKŁAD:**

    **Hasło:** Wielkowice
    **Tekst hasła:** Wielkowice albo Wielkowiec, wś i folw., pow. pruski, gm. Hotków. Cerkiew par. i szkoła religijna,
    parafia kat. w Hotkowie, na skraju wsi kaplica pod wezw. św. Michała. W 1879 r. 115 dm., 456 mk. W 1560 roku król Zygmunt August nadał wieś Janowi Potockiemu za zasługi.
    We wsi 2 młyny i wiatrak, obszerny drewniany spichlerz. Na płn od wsi znaleziono urny i starożytne siekierki z brązu. Obecnie własność skarbowa. K. Prz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "1. Identyfikuję właściciela ziemskiego, tekst wspomina iż wieś nadano Janowi Potockiemu, ale to dotyczy
            XVI wieku, dalej fragment tekstu mówi 'obecnie własność skarbowa', czyli obecnie majątek należy do państwa, i tą aktualną informację zapisuję: 'własność skarbowa'",
        "2. Wyszukuję obiekty przemysłowe, w tekście tylko wzmianki o młynach i wiatrakach, które nie należą do kategorii obiektów przemysłowych, zapisuję więc wartość 'null'",
        "3. Wyszukuję młyny i wiatraki. W tekście znaduję 'We wsi 2 młyny i wiatrak' - zapisuję '2 młyny', 'wiatrak'",
        "4. Szukam znalezisk archeologicznych, w tekście występuje wzmianka o starożytnych siekierkach i urnach, które można zakwaifikować jako znaleziska archeologiczne.",
        "5. Analizuję tekst pod względem występowania informacji o zabytkach, brak takich danych, pomijam pole w strukturze json",
        "6. Szukam obiektów pasujących do kategorii architektura krajobrazu, brak takich danych, pomijam pole w strukturze json",
        "7. Wyszukuję zbiory i kolekcje, brak takich danych, pomijam pole w strukturze json",
        "8. Analizuję tekst w zakresie występowania muzeów, gabinetów ze zbiorami, brak takich danych, pomijam pole w strukturze json",
        "9. Szukam cmentarzy, grobowców, brak takich danych, pomijam pole w strukturze json",
        "10. Wyszukuję wzmanek o rzemieślnikach, brak takich danych, pomijam pole w strukturze json",
        "11. Badam czy tekst wspomina o leśniczówkach lub podobnych obiektach, ale nie znajduję, pomijam więc pole w strukturze json",
        "12. Szukam budynków pałacowych, dworów, zbrak takich danych, pomijam pole w strukturze json",
        "13. Szukam informacji o magazynowanach i spichlerzach, tekst wspomina 'obszerny drewniany spichlerz', zapisuję 'spichlerz'",
        "14. Przeszukanie tekstu w zakresie obiektów związanych z wojskowością nie dało żadnych rezultatów, pomijam więc pole w strukturze json",
        "15. Szukam obiektów sakralnych, znajduję wzmiankę 'Cerkiew par.' oraz 'kaplica pod wezw. św. Michała', więc zapisuję w polu 'cerkiew parafialna' i 'kaplica św. Michała'"
    ],
    "właściciel": "własność skarbowa",
    "przemysłowe": null,
    "młyny": ["2 młyny", "wiatrak"],
    "archeo": ["urny", "starożytne siekierki z brązu"],
    "magazyny": ['spichlerz'],
    "obiekty_sakralne": ['cerkiew parafalna', 'kaplica św. Michała']
    }}
    ---
    """


# --------------------------------- MAIN ---------------------------------------
if __name__ == '__main__':

     # pomiar czasu wykonania
    start_time = time.time()

    input_path = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}.json'
    output_dir = Path('..') / 'SGKP' / 'JSON' / 'batch'

    output_files = glob.glob(str(output_dir / f'sgkp_{VOLUME}_wlasnosc_przemysl_batch*.jsonl'))

    if output_files:
        for out_f in output_files:
            os.remove(out_f)

    # wczytanie danych z pliku json dla tomu
    rekordy = []
    with open(input_path, "r", encoding='utf-8') as f:
        json_data = json.load(f)

        for item_result in json_data:
            rodzaj = item_result["rodzaj"]

            if rodzaj == "zbiorcze":
                elementy = item_result["elementy"]
                for element in elementy:
                    element_nazwa = element.get("nazwa", None)
                    element_id = element.get("ID", None)
                    element_text = element.get("text", None)
                    if element_nazwa and element_id and element_text:
                        rekordy.append((element_id, element_nazwa, element_text))

            else:
                item_nazwa = item_result.get("nazwa", None)
                item_id = item_result.get("ID", None)
                item_text = item_result.get("text", None)
                if item_nazwa and item_id and item_text:
                    rekordy.append((item_id, item_nazwa, item_text))

        licznik = 0
        max_rec = 5000
        file_nr = 1

        unikalny = []

        # przygotowanie pliku JSONL
        for rec in rekordy:
            licznik += 1

            # unikalny identyfikator dla każdego zapytania
            custom_id, nazwa, text = rec

            if custom_id not in unikalny:
                unikalny.append(custom_id)
            else:
                print(custom_id)
                sys.exit(1)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'{user_prompt}\n\nHasło: {nazwa}\n Treść hasła: {text}' }
            ]

            # obiekt JSON dla pojedynczego zadania wsadowego
            json_request = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "max_tokens": 2000,
                    "temperature": 0.0
                }
            }

            if licznik >= 5000:
                file_nr += 1
                licznik = 0

            output_file = Path('..') / 'SGKP' / 'JSON' / 'batch' / f'sgkp_{VOLUME}_wlasnosc_przemysl_batch_{file_nr}.jsonl'
            with open(output_file, 'a', encoding='utf-8') as f:
                # Zapisanie obiektu JSON jako jednej linii w pliku
                f.write(json.dumps(json_request, ensure_ascii=False) + "\n")

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
