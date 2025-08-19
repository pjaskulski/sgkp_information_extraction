""" przygotowanie danych dla zadań Batch API OpenAI """
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
class NameVarModel(BaseModel):
    lang: str | None = Field(None,
                             description="język wariantu nazwy, jeżeli podano np. niem., węg., jeżeli brak zapisz nieokr. - nieokreślony")
    wariant_nazwy: str | None = Field(None,
                                      description="wariant nazwy hasła (alias, nazwa w innym języku, nazwa występująca w dokumentach itp.)")

class ParafiaInnaModel(BaseModel):
    wyznanie: str | None = Field(None,
                             description="nazwa wyznania parafii np. ew., gr.-kat. itp.")
    nazwa_parafii: str | None = Field(None,
                                      description="nazwa parafii")

class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None,
                                               description="Kroki wyjaśniające prowadzące do ustalenia danych podstawowych dla hasła")
    typ: str | None = Field(None,
                            description="Typ hasła - co hasło opisuje np. wieś, miasto, miasteczko, rzekę, górę, osiedle, krainę itp. ")
    powiat: str | None = Field(None,
                               description="Nazwa powiatu w którym położona jest miejscowość")
    gmina: str | None = Field(None,
                              description="Nazwa gminy w której położona jest miejscowość")
    gubernia: str | None = Field(None,
                                 description="Nazwa guberni, do której należy miejscowość")
    parafia_katolicka: str | None = Field(None,
                                          description="Nazwa parafii katolickiej (rzymsko-katolickiej)")
    parafia_inna: List[ParafiaInnaModel] | None = Field(None,
                                     description="Lista parafii nie katolickich (np. prawosławnych, greko-katolickich, ewangelickich)")
    autor: str | None = Field(None,
                              description="Inicjały lub nazwisko autora hasła, występuje na końcu hasła, część haseł nie ma podanego autora.")
    warianty_nazw: List[NameVarModel] | None = Field(None,
                                                     description="Lista wariantów nazw (aliasów) dla hasła.")

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
1.  **Przeanalizuj przekazany tekst hasła słownika SGKP:**
2.  **Wypełnij pola:** Na podstawie swojej analizy, wypełnij pozostałe pola w strukturze JSON.

**SZCZEGÓŁOWE REGUŁY EKSTRAKCJI:**

**1. Typ Hasła (`typ`):**
*   Określ, co opisuje hasło (np. wieś, miasto, folwark, rzeka, jezioro, góra).
*   **Reguła specjalna:** Jeżeli tekst hasła zawiera skrót `ob.` (obacz), jest to odsyłacz (). W takim przypadku wypełnij **tylko** pole `typ` wartością "odsyłacz" i pozostaw resztę pól jako `null`. Nazwa po `ob.` to inne hasło, a nie wariant nazwy.

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
*   **Kluczowa reguła:** Autor to **TYLKO I WYŁĄCZNIE** inicjały lub nazwisko znajdujące się na **samym końcu** tekstu hasła (np. `Br. Ch.`, `F. S.`, `Sulimierski`).
*   **ZIGNORUJ** wszelkie inicjały i nazwiska pojawiające się w środku tekstu, ponieważ dotyczą one postaci historycznych, a nie autorów hasła.

**INFORMACJE POMOCNICZE:**
*   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
*   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
*   Nazwy zapisuj w formie mianownika.
*   Jeżeli w tekście brak jakiejś informacji, pozostaw jej wartość jako `null`.

Schemat JSON:
{json.dumps(json_schema, indent=2, ensure_ascii=False)}

---
**PRZYKŁAD:**

**Hasło:** Bolkowce
**Tekst hasła:** Bolkowce, niem. Bolkowitz, ros. Bolkovicje, mczko, pow. woliński, par. Więcko, par. gr.-kat. w miejscu, gm. Pastwiska w gub. lidzkiej. W 1800 r. był własnością Adama Lankckowskiego sędziego ziemskiego, ma 25 dm., 98 mk. Grunty orne, liczne sady, budynków z drewna 23, bud. mur. 2, na południu wsi staw rybny. Zabytkowy kościół z XVI w. św. Piotra i Pawła w centrum wsi. L. Doz.

**Wynik w formie struktury JSON:**
```json
{{
  "chain_of_thought": [
    "1. Analizuję warianty nazw: 'niem. Bolkowitz' i 'ros. Bolkovicje'.",
    "2. Identyfikuję typ miejscowości: 'mczko' to miasteczko.",
    "3. Znajduję dane administracyjne: 'pow. woliński', 'gm. Pastwiska'. Gubernia: lidzka, w niej miejści się gmina więc także miejscowość.",
    "4. Analizuję parafie: 'par. Więcko' to parafia katolicka. 'par. gr.-kat. w miejscu' to parafia inna.",
    "5. Sprawdzam koniec tekstu w poszukiwaniu autora. Znajduję 'L. Doz.'."
  ],
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
  "chain_of_thought": [
    "1. Analizuję warianty nazw: 'albo Wielkowiec'",
    "2. Identyfikuję typ miejscowości: 'wś' to wieś, folw. to folwark",
    "3. Znajduję dane administracyjne: 'pow. pruski', 'gm. Hotków'. Guberni brak.",
    "4. Analizuję parafie: 'cerkiew par.' oznacza że parafia prawosławna jest na miejscu, czyli w Wielkowicach. 'parafia kat w Hotkowie': parafia Hotków",
    "5. Sprawdzam koniec tekstu w poszukiwaniu autora. Znajduję 'K. Prz.'."
  ],
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


# --------------------------------- MAIN ---------------------------------------
if __name__ == '__main__':

     # pomiar czasu wykonania
    start_time = time.time()

    input_path = Path('..') / 'SGKP' / 'JSON' / f'sgkp_{VOLUME}.json'
    output_dir = Path('..') / 'SGKP' / 'JSON' / 'batch'

    output_files = glob.glob(str(output_dir / f'sgkp_{VOLUME}_batch*.jsonl'))

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
                    "max_tokens": 1000,
                    "temperature": 0.0
                }
            }

            if licznik >= 5000:
                file_nr += 1
                licznik = 0

            output_file = Path('..') / 'SGKP' / 'JSON' / 'batch' / f'sgkp_{VOLUME}_batch_{file_nr}.jsonl'
            with open(output_file, 'a', encoding='utf-8') as f:
                # Zapisanie obiektu JSON jako jednej linii w pliku
                f.write(json.dumps(json_request, ensure_ascii=False) + "\n")

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
