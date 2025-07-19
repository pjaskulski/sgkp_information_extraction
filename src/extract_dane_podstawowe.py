""" openai gpt - informacje podstawowe dla hasła SGKP """
import os
import sys
import time
import json
from pathlib import Path
from typing import List
from dotenv import load_dotenv
import openai
from openai import OpenAI
from pydantic import BaseModel, Field
import instructor
from ratelimit import limits, sleep_and_retry


# API-KEY
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# model
MODEL = "gpt-4.1-mini"
#MODEL = "gpt-4.1"

system_prompt = """Jesteś asystentem historyka, specjalizującym się w badaniach
historyczno - geograficznych.
"""

with open('prompt_sgkp_skroty.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    skroty = [x.strip() for x in lines]

lista_skrotow = ', '.join(skroty)

user_prompt = f"""
Jesteś ekspertem w analizie tekstów ze Słownika Geograficznego Królestwa Polskiego (SGKP). Twoim zadaniem jest precyzyjna ekstrakcja danych z podanego hasła.

Przeanalizuj poniższy tekst i wypełnij strukturę JSON zgodnie z podanymi polami i regułami.

**KROKI POSTĘPOWANIA:**
1.  **Przemyśl analizę:** W polu `chain_of_thought` zapisz swoje rozumowanie krok po kroku, jak doszedłeś do poszczególnych wartości.
2.  **Wypełnij pola:** Na podstawie swojej analizy, wypełnij pozostałe pola w strukturze JSON.

**SZCZEGÓŁOWE REGUŁY EKSTRAKCJI:**

**1. Typ Hasła (`typ`):**
*   Określ, co opisuje hasło (np. wieś, miasto, folwark, rzeka, jezioro, góra).
*   **Reguła specjalna:** Jeżeli tekst hasła zawiera skrót `ob.` (obacz), jest to odsyłacz. W takim przypadku wypełnij **tylko** pole `typ` wartością "odsyłacz" i pozostaw resztę pól jako `null`. Nazwa po `ob.` to inne hasło, a nie wariant nazwy.

**2. Warianty Nazw (`warianty_nazw`):**
*   Wyszukaj alternatywne lub obcojęzyczne nazwy hasła, podane zwykle na samym początku. Niekiedy warianty nazw podane są razem z datą, kiedy występowały. Warinat nazwy musi się różnić od nazwy hasła podanej na początku tekstu hasła.
*   Zapisz język (np. `niem.`, `ros.`, `łac.`). Jeśli język nie jest podany, użyj wartości `nieokr.`.

**3. Dane Administracyjne (`powiat`, `gmina`, `gubernia`):**
*   Wyodrębnij te informacje z tekstu. Często występują po skrótach: `pow.`, `gm.`, `gub.`.

**4. Parafie (`parafia_katolicka`, `parafia_inna`):**
*   Postępuj według następującej logiki:
    *   **Krok 1:** Szukaj skrótu `par.` (parafia).
    *   **Krok 2:** Jeśli znajdziesz `par.` bez określenia wyznania, przyjmij, że to `parafia_katolicka`.
    *   **Krok 3:** Jeśli znajdziesz `par.` z wyznaniem (np. `par. gr.-kat.`, `par. ewang.`), zapisz nazwę i wyznanie w polu `parafia_inna`.
    *   **Krok 4:** **JEŚLI NIE ZNAJDZIESZ SKRÓTU `par.`**, sprawdź, czy w tekście jest mowa o "kościele parafialnym" lub "cerkwi parafialnej".
    *   **Krok 5:** Jeśli tak, oznacza to, że parafia (odpowiednio katolicka lub inna) znajduje się w opisywanej miejscowości. Zapisz to jako "w miejscu" lub nazwę miejscowości. Zwykła wzmianka o kościele lub cerkwi (bez słowa "parafialny") NIE JEST wystarczająca do ustalenia siedziby parafii.

**5. Autor (`autor`):**
*   **Kluczowa reguła:** Autor to **TYLKO I WYŁĄCZNIE** inicjały lub nazwisko znajdujące się na **samym końcu** tekstu hasła (np. `Br. Ch.`, `F. S.`, `Sulimierski`).
*   **ZIGNORUJ** wszelkie inicjały i nazwiska pojawiające się w środku tekstu, ponieważ dotyczą one postaci historycznych, a nie autorów hasła.

**INFORMACJE POMOCNICZE:**
*   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
*   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
*   Jeżeli w tekście brak jakiejś informacji, pozostaw jej wartość jako `null`.

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
    "3. Znajduję dane administracyjne: 'pow. woliński', 'gm. Pastwiska'. Guberni brak.",
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
  "gubernia": null,
  "parafia_katolicka": "Więcko",
  "parafia_inna": "gr.-kat. w miejscu",
  "autor": "L. Doz."
}}
"""


# -------------------------------- CLASS ---------------------------------------
class NameVarModel(BaseModel):
    """ model wariantów nazw hasła """
    lang: str | None = Field(None, description="język wariantu nazwy, jeżeli podano np. niem., węg., jeżeli brak zapisz nieokr. - nieokreślony")
    wariant_nazwy: str | None = Field(None, description="wariant nazwy hasła")

class EntryModel(BaseModel):
    """ model danych podstawowych """
    chain_of_thought: List[str] | None = Field(
        None,
        description="Kroki wyjaśniające prowadzące do ustalenia danych podstawowych dla hasła"
        )
    typ: str | None = Field(None, description="Typ hasła - co hasło opisuje np. wieś, miasto, miasteczko, rzekę, górę, osiedle, krainę itp. ")
    powiat: str | None = Field(None, description="Nazwa powiatu w którym położona jest miejscowość")
    gmina: str | None = Field(None, description="Nazwa gminy w której położona jest miejscowość")
    gubernia: str | None = Field(None, description="Nazwa guberni, do której należy miejscowość")
    parafia_katolicka: str | None = Field(None, description="Nazwa parafii katolickiej, do której należy miejscowość, jeżeli w tekście jest tylko nazwa parafii bez wskazania wyznaniam należy przyjąć że chodzi własnie o parafię katolicką. Jeżeli w miejscowości opisywanej w haśle jest kościół parafialny to parafoa mieści się w tej miejscowości.")
    parafia_inna: str | None = Field(None, description="Nazwa parafii nie katolickiej, do której należy miejscowość, np. prawosławnej, greko-katolickiej, ewangelickiej itp., może wystąpić więcej niż 1 taka parafia, wówczas zapisz wszystkie oddzielone przecinkiem. Oprócz nazwy koniecznie zapisz też wyznanie, jeżeli w miejscowości opisanej w haśle jest cerkiew parafialna to znaczy, że parafia jest w tej miejscowości.")
    autor: str | None = Field(None, description="Tekst hasła KOŃCZY SIĘ często inicjałami, a czasem całym nazwiskiem autora (autorów), zapisz je w tym polu, uwzględnij tylko inicjały lub nazwiska znajdujące się na końcu hasła")
    warianty_nazw: List[NameVarModel] | None = Field(None, description="Lista wariantów nazw hasła, warianty podane są zwykle po głównej nazwie hasła, jeżeli podano uwględnij też język np. niem., węg., jeżeli nie podano zapsz: nieokr.")


# ------------------------------ FUNCTIONS -------------------------------------
#@sleep_and_retry
#@limits(calls=120, period=60)
def get_data_instructor(tekst_hasla:str):
    """ ekstrakcja informacji za pomoca biblioteki instructor """

    client = instructor.from_openai(OpenAI())

    u_prompt = f'{user_prompt}\n\n{tekst_hasla}'
    s_prompt = system_prompt

    completion = client.chat.completions.create(
        model=MODEL,
        response_model=EntryModel,
        messages=[
            {"role": "system", "content": s_prompt},
            {"role": "user", "content": u_prompt},
        ],
    )

    return completion


def value_test(value:str) -> bool:
    """ test czy pole zawiera realną wartość """
    result = True

    if value.strip() == '':
        result = False
    if value.strip() == '/':
        result = False
    if value.strip() == 'null':
        result = False

    return result


# ---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":

    # pomiar czasu wykonania
    start_time = time.time()

    # path do danych
    data_path = Path('..') / 'SGKP' / 'JSON' / 'sgkp_16_new_5.json'
    output_path = Path('..') / 'SGKP' / 'JSON' / 'sgkp_16_new_6.json'

    with open(data_path, "r", encoding='utf-8') as f:
        json_data = json.load(f)

    licznik = 0
    start = False

    for entry in json_data:
        entry_id = entry.get("ID", "")

        # początek przetwarzania od ostatnio przetworzonej miejscowości
        if entry_id == '16-06640':
            start = True
        if not start:
            continue

        name = entry.get("nazwa", "")
        rodzaj = entry.get("rodzaj", None)
        page = entry.get("strona", "")

        if rodzaj == "zbiorcze":
            elements = entry.get("elementy", [])

            prev_powiat = None

            for element in elements:

                licznik += 1
                name = element.get("nazwa", "")
                text = element.get("text", "")
                element_id = element.get("ID", "")
                nr = element.get("nr", "")

                result = get_data_instructor(tekst_hasla=f'Hasło: {name}\n Treść hasła: {text}')

                try:
                    if result.typ and value_test(result.typ):
                        element['typ'] = result.typ
                    if result.powiat and value_test(result.powiat):
                        element['powiat_ocr'] = result.powiat
                        prev_powiat = result.powiat
                    else:
                        if 'tamże' in text[:150]:
                            element['powiat_ocr'] = prev_powiat
                    if result.gmina and value_test(result.gmina):
                        element['gmina'] = result.gmina
                    if result.gubernia and value_test(result.gubernia):
                        element['gubernia'] = result.gubernia
                    if result.parafia_katolicka and value_test(result.parafia_katolicka):
                        element['parafia_katolicka'] = result.parafia_katolicka
                    if result.parafia_inna and value_test(result.parafia_inna):
                        element['parafia_inna'] = result.parafia_inna

                    if result.warianty_nazw:
                        parsed_data = []
                        for item in result.warianty_nazw:
                            parsed_data_item = NameVarModel.model_dump(item)
                            parsed_data.append(parsed_data_item)
                        if parsed_data:
                            element['warianty_nazw'] = parsed_data

                except Exception as e:
                    print(f"Błąd parsowania JSON od LLM: {e}")
                    sys.exit(1)

                print(f'{licznik}. {name} ({element_id})')

        else:
            licznik += 1
            name = entry.get("nazwa", "")
            text = entry.get("text", "")
            result = get_data_instructor(tekst_hasla=f'Hasło: {name}\nTreść hasła: {text}')

            try:
                if result.typ and value_test(result.typ):
                    entry['typ'] = result.typ
                if result.powiat and value_test(result.powiat):
                    entry['powiat_ocr'] = result.powiat
                if result.gmina and value_test(result.gmina):
                    entry['gmina'] = result.gmina
                if result.gubernia and value_test(result.gubernia):
                    entry['gubernia'] = result.gubernia
                if result.parafia_katolicka and value_test(result.parafia_katolicka):
                    entry['parafia_katolicka'] = result.parafia_katolicka
                if result.parafia_inna and value_test(result.parafia_inna):
                    entry['parafia_inna'] = result.parafia_inna
                if result.autor and value_test(result.autor):
                    entry['autor'] = result.autor

                if result.warianty_nazw:
                    parsed_data = []
                    for item in result.warianty_nazw:
                        parsed_data_item = NameVarModel.model_dump(item)
                        parsed_data.append(parsed_data_item)
                    if parsed_data:
                        entry['warianty_nazw'] = parsed_data

            except Exception as e:
                print(f"Błąd parsowania JSON od LLM: {e}")
                sys.exit(1)

            print(f'{licznik}. {name} ({entry_id})')

        # zapis do nowego pliku json
        with open(output_path, 'w', encoding='utf-8') as f_out:
            json.dump(json_data, f_out, indent=4, ensure_ascii=False)

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
