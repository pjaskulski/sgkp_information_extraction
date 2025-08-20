""" prompt do ekstrakcji informacji:
- liczba mieszkańców
- liczba domów
- struktura wyznaniowa
"""
import json
from pathlib import Path


def prepare_prompt(model=None) -> str:
    """ przygotowanie promptu """

    # lista skrótów z SGKP
    input_path = Path('..') / 'dictionary' / 'prompt_sgkp_skroty.txt'
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        skroty = [x.strip() for x in lines]

    lista_skrotow = ', '.join(skroty)

    # jeżeli prompt dla przetwarzania przez Batch API to dodajemy schemat modelu
    text_schema = ''
    if model:
        json_schema = model.model_json_schema()
        text_schema = f"""Schemat JSON:
        {json.dumps(json_schema, indent=2, ensure_ascii=False)}
        """

    user_prompt = f"""
    Twoim zadaniem jest precyzyjna ekstrakcja danych z podanego hasła.
    Przeanalizuj poniższy tekst i wypełnij strukturę JSON zgodnie z podanymi polami i regułami.

    **KROKI POSTĘPOWANIA:**
    1.  **Przemyśl analizę:** W polu `chain_of_thought` zapisz swoje rozumowanie krok po kroku, jak doszedłeś do poszczególnych wartości.
    2.  **Wypełnij pola:** Na podstawie swojej analizy, wypełnij pozostałe pola w strukturze JSON.

    **SZCZEGÓŁOWE REGUŁY EKSTRAKCJI:**

    Wyszukaj i zapisz w polach struktury JSON poszukiwane informacje.
    Uwzględniaj **TYLKO** dane dotyczące XIX wieku, starsze informacje historyczne - pomiń.

    **Liczba mieszkańców (pole 'l_mk_statystyka')**
    *   wyszukaj dane na temat liczby mieszkańców w danej miejscowości. Często hasła zawieraja takie informacje także o dodatkowych osadach, folwarkach, a nie tylko dla głównej miejscowości. Ustal czy znalezione dane dotyczą głównej miejscowości np. wsi, czy też właśnie np. folwarku. Zapisuj je wówczas osobno w odrębnych strukturach, każda z nich powinna mieć pole 'dotyczy' z wartością wskazującą czy liczba mieszkańców dotyczy głównej miejscowości czy innej osady, miejsca opisanego w treści hasła. Podobnie jeżeli podano dane na temat liczby mieszkańców dla całej gminy - zapisz te infromacje osobno. Jeżeli w tekście są dane z różnych lat XIX wieku zapisz je jako osobne informacje, podając rok dla którego podano te informacje, lub określenie "obecnie" jeżeli rok nie jest podany, ale z kontekstu wynika że chodzi o dane aktualne w momencie pisania Słownika. Informacje o roku i liczbie zapisuj w drugim pole struktury, o nazwie 'liczba_mieszkańców', powino ono zawierać jedną lub więcej struktur z datą i liczbą np. {{"data":"1827", "liczba": "650" }}.

    **Liczba domów (pole 'l_dm_statystyka')**
    *    wyszukaj dane na temat liczby domów w danej miejscowości. Często hasła zawieraja takie informacje o dodatkowych osadach, folwarkach, ustal czy znalezione dane dotyczą głównej miejscowości np. wsi, czy też właśnie np. folwarku. Zapisuj je wówczas osobno w odrębnych strukturach, każda z nich powinna mieć pole 'dotyczy' z wartością wskazującą czy liczba domów dotyczy głównej miejscowości czy innej osady, miejsca opisanego w treści hasła. Podobnie jeżeli podano dane na temat liczby domów dla całej gminy - zapisz te infromacje osobno. Jeżeli w tekście są dane z różnych lat XIX wieku zapisz je jako osobne informacje, podając rok dla którego podano te informacje, lub określenie "obecnie" jeżeli rok nie jest podany, ale z kontekstu wynika że chodzi o dane aktualne w momencie pisania Słownika. Informacje o roku i liczbie zapisuj w drugim polu struktury, o nazwie 'liczba_domów', powino ono zawierać jedną lub więcej struktur z datą i liczbą np. {{"data": "1827", "liczba": "650" }}.


    **INFORMACJE POMOCNICZE:**
    * W tekście Słownika stosowano skróty: dm. - oznacza dom, domów, mk. - oznacza mieszkańca, mieszkańców, uwzględnij tylko informacje podane w taki sposób.
    *   W tekście mogą występować też inne skróty. Oto lista najczęstszych: {lista_skrotow}.
    *   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
    *   Jeżeli w tekście brak jakiejś informacji, pomiń daną kategorię informacji w wynikowej strukturze.

    {text_schema}

    ---
    **PRZYKŁAD:**

    **Hasło:** Bolkowce
    **Tekst hasła:** Bolkowce, niem. Bolkowitz, ros. Bolkovicje, mczko, pow. woliński, par. Więcko, par. gr.-kat. w miejscu, gm. Pastwiska w gub. lidzkiej, szkoła w Pustkowiu. W 1800 r. było własnością Adama Lankckowskiego sędziego ziemskiego. Ma 25 dm., 98 mk. Grunty orne, liczne sady, budynków z drewna 23, bud. mur. 2, na południu wsi staw rybny oraz wiatrak i karczma. W pobliskiej dolinie mała huta szkła. Zabytkowy kościół z XVI w. św. Piotra i Pawła w centrum wsi. W 1860 r. Lanckowscy założyli tu mały przytułek dla włościan. L. Doz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "Rozpoczynam analizę hasła 'Bolkowce' w celu ekstrakcji danych statystycznych o liczbie domów (dm.) i mieszkańców (mk.) zgodnie z zadaną strukturą.",
        "Przeszukuję tekst w poszukiwaniu wzorców zawierających skróty 'dm.' lub 'mk.' oraz powiązanych z nimi dat.",
        "Identyfikuję jedną kluczową frazę zawierającą dane statystyczne: '... Ma 25 dm., 98 mk.' - bez podaje daty, co oznacza że chodzi o okres 'obecnie' - w momencie powstawania hasła.",
        "Analizuję kontekst tej frazy. Odnosi się ona do głównej miejscowości 'Bolkowce', opisanej w haśle jako miasteczko ('mczko'). Nie ma tu mowy o oddzielnym folwarku czy innej części osady, więc wszystkie dane przypisuję do jednego podmiotu, który oznaczę jako 'główna miejscowość'.",
        "dla pola 'l_mk_statystyka' tworzę obiekt z polem `dotyczy` ustawionym na 'główna miejscowość' i pustą listą 'liczba_mieszkańców' na dane liczbowe.",
        "dla pola 'l_dm_statystyka' tworzę obiekt z polem `dotyczy` ustawionym na 'główna miejscowość' i pustą listą 'liczba_domów' na dane liczbowe.",
        "Z frazy '... Ma 25 dm., ...' ustalam liczbę domów = '25', tworzę obiekt z wartościami `data='obecnie'` i `liczba='25'`, a następnie dodaję go do listy `liczba_domów`.",
        "Z tej samej frazy '... 98 mk.' ekstrahuję liczbę mieszkańców '98' i tworzę obiekt z wartościami `data='obecnie'` i `liczba='98'`, a następnie dodaję go do listy `liczba_mieszkańców`.",
        "Zauważam również informację 'budynków z drewna 23, bud. mur. 2'. Jest to informacja o liczbie budynków, ale przedstawiona w formie podziału na typy, a nie jako łączna liczba 'domów' (dm.). Chociaż suma (23+2=25) odpowiada liczbie 'dm.', jest to inna forma danych. Aby zachować precyzję, decyduję się nie włączać tej informacji do struktury `l_dm_statystyka`, która jest przeznaczona dla danych oznaczonych jako 'dm.'.",
        "Przeglądam pozostałą część tekstu i stwierdzam, że nie zawiera ona żadnych dodatkowych danych o liczbie domów ani mieszkańców. Proces ekstrakcji danych statystycznych dla tego hasła został zakończony."
    ],
    "l_mk_statystyka": [
        {{
            "dotyczy": "główna miejscowość",
            "liczba_mieszkańców": [
                {{"data": "obecnie", "liczba": "98"}}
            ]
        }}
    ],
    "l_dm_statystyka": [
        {{
            "dotyczy": "główna miejscowość",
            "liczba_domów": [
                {{"data": "obecnie", "liczba": "25"}}
            ]
        }}
    ],
    }}```
    ---
    **PRZYKŁAD:**

    **Hasło:** Wielkowice
    **Tekst hasła:** Wielkowice albo Wielkowiec, wś i folw., pow. pruski, gm. Hotków. Cerkiew par. i szkoła religijna,
    parafia kat. w Hotkowie,. W 1827 r. wieś ma 115 dm., 456 mk., w 1878 r. 123 dm. i 569 mk. Folwark położony jest po drugiej stronie strumienia Malinowskiego, w w 1878 r. miał 12 dm. i 40 mk. 1560 roku król Zygmunt August nadał wieś Janowi Potockiemu za zasługi. We wsi 2 młyny i wiatrak, gospoda przydrożna. Na płn od wsi znaleziono urny i starożytne siekierki z brązu. Przy folwarku stacja hodowli koni. We wsi kasa pożyczkowa z kapitałem 350 rb. Obecnie własność skarbowa. K. Prz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "Rozpoczynam analizę hasła 'Wielkowice' pod kątem ekstrakcji danych statystycznych o liczbie domów (dm.) i mieszkańców (mk.). Oczekiwana struktura json wymaga precyzyjnego rozróżnienia danych dla różnych lokalizacji (np. wieś, folwark) i różnych lat.",
        "Tworzę puste listy nadrzędne: `l_mk_statystyka` i `l_dm_statystyka`, które będą przechowywać obiekty dla każdej zidentyfikowanej lokalizacji.",
        "Analizuję pierwszą frazę zawierającą dane statystyczne: 'W 1827 r. wieś ma 115 dm., 456 mk.'.",
        " - Identyfikuję podmiot, którego dotyczą dane: 'wieś', tworzę nowe struktury (dotyczy='wieś',  'liczba_mieszkańców'=[]) i  (dotyczy='wieś',  'liczba_domów'=[]) dla tego podmiotu
        " - Identyfikuję datę: '1827 r.'.",
        " - Identyfikuję liczbę domów: '115 dm.'. Tworzę obiekt (data='1827 r.', liczba='115')` i dodaję go do listy 'liczba_domów'",
        " - Identyfikuję liczbę mieszkańców: '456 mk.'. Tworzę obiekt (data='1827 r.', liczba='456')` i dodaję go do listy 'liczba_mieszkańców'",
        "Przechodzę do kolejnej części zdania: 'w 1878 r. 123 dm. i 569 mk.'.",
        " - Kontekst wskazuje, że te dane wciąż dotyczą podmiotu 'wieś'.",
        " - Identyfikuję nową datę: '1878 r.'.",
        " - Identyfikuję liczbę domów dla tej daty: '123 dm.'. Tworzę nowy obiekt (data='1878 r.', liczba='123')` i dodaję go do tej samej listy `liczba_domów` w istniejącym już obiekcie dla podmiotu 'wieś'.",
        " - Identyfikuję liczbę mieszkańców dla tej daty: '569 mk.'. Tworzę nowy obiekt (data='1878 r.', liczba='569')` i dodaję go do tej samej listy `liczba_mieszkańców` w istniejącym obiekcie dla podmiotu 'wieś'.",
        "Analizuję kolejne zdanie: 'Folwark położony jest po drugij stronie strumienia Malinowskiego, w w 1878 r. miał 12 dm. i 40 mk.'.",
        " - Identyfikuję nowy podmiot: 'folwark', tworzę nowe struktury (dotyczy='folwark', liczba_mieszkańców=[])` oraz (dotyczy='folwark', liczba_domów=[])`.",
        " - Identyfikuję datę: '1878 r.'.",
        " - Identyfikuję liczbę domów dla folwarku: '12 dm.'. Tworzę obiekt (data='1878 r.', liczba='12')` i dodaję go do listy `liczba_domów` w nowym obiekcie dla 'folwark'.",
        " - Identyfikuję liczbę mieszkańców dla folwarku: '40 mk.'. Tworzę obiekt (data='1878 r.', liczba='40')` i dodaję go do listy `liczba_mieszkańców` w nowym obiekcie dla 'folwark'.",
        "Przeskanowałem resztę hasła. Nie znajduję więcej danych liczbowych dotyczących domów ani mieszkańców. Finalizuję proces, dodając utworzone obiekty (jeden dla 'wieś' z dwiema datami, drugi dla 'folwark' z jedną datą) do głównych list `l_mk_statystyka` i `l_dm_statystyka` w ostatecznym wyniku.",
        "Proces ekstrakcji danych statystycznych został zakończony. Dane zostały poprawnie przypisane do dwóch różnych lokalizacji ('wieś', 'folwark') i różnych punktów w czasie."
    ],
    "l_mk_statystyka": [
        {{
            "dotyczy": "główna miejscowość",
            "liczba_mieszkańców": [
                {{"data": "1827", "liczba": "456"}},
                {{"data": "1878", "liczba": "569"}}
            ]
        }},
        {{
            "dotyczy": "folwark",
            "liczba_mieszkańców": [
                {{"data": "1878", "liczba": "40"}}
            ]
        }}
    ],
    "l_dm_statystyka": [
        {{
            "dotyczy": "główna miejscowość",
            "liczba_domów": [
                {{"data": "1827", "liczba": "115"}},
                {{"data": "1878", "liczba": "123"}}
            ]
        }},
        {{
            "dotyczy": "folwark",
            "liczba_domów": [
                {{"data": "1878", "liczba": "12"}}
            ]
        }}
    ],
    }}```
    ---
    """

    return user_prompt
