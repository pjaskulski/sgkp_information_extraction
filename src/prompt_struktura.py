""" prompt do ekstrakcji informacji:
- struktura wyznaniowa
"""

def prepare_prompt() -> str:
    """ przygotowanie promptu """

    # lista skrótów z SGKP
    with open('prompt_sgkp_skroty.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        skroty = [x.strip() for x in lines]

    lista_skrotow = ', '.join(skroty)

    user_prompt = f"""
    Twoim zadaniem jest precyzyjna ekstrakcja danych z podanego hasła.
    Przeanalizuj poniższy tekst i wypełnij strukturę JSON zgodnie z podanymi polami i regułami.

    **KROKI POSTĘPOWANIA:**
    1.  **Przemyśl analizę:** W polu `chain_of_thought` zapisz swoje rozumowanie krok po kroku, jak doszedłeś do poszczególnych wartości.
    2.  **Wypełnij pola:** Na podstawie swojej analizy, wypełnij pozostałe pola w strukturze JSON.

    **SZCZEGÓŁOWE REGUŁY EKSTRAKCJI:**

    Wyszukaj i zapisz w polach struktury JSON poszukiwane informacje.
    Uwzględniaj **TYLKO** dane dotyczące XIX wieku, pomiń starsze informacje historyczne.

    **Struktura wyznaniowa (pole 'struktura_wyznaniowa')**
    *   wyszukaj dane na temat struktury wyznaniowej ludności w analizowanym haśle (liczby osób dla poszczególnych wyznań religijnych)
    *   określenia dot. wyznania ludności mogą być zapisane skrótem np. rz.-kat., gr.-kat., izrael. żyd. itp.
    *   jeżeli w tekście opisywane dane wyznaniowe dotyczące dodatkowych miejscowości (mp. opisana jest osobno wieś i folwark), lub terenu całej gminy, parafii, powiatu (i jest to wskazane wprost w tekście) - zapisz te informacje w osobnych strukturach
    *   zapisz dane w strukturze JSON "ludność_wyznanie", która przechowuje listę struktur z polami "dotyczy" (czego dotyczy struktura np. główna miejscowość, wieś, folwark), oraz "struktura_wyznaniowa", to drugie pole jest listą wyznań i liczebności wyznawców zapisanych w formie struktury typu:  {{"wyznanie_ocr": "rz. kat.", "liczba": "29"}}.

    **INFORMACJE POMOCNICZE:**
    *   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
    *   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
    *   Jeżeli w tekście brak jakiejś informacji, pomiń daną kategorię informacji w wynikowej strukturze.

    ---
    **PRZYKŁAD:**

    **Hasło:** Bolkowce
    **Tekst hasła:** Bolkowce, niem. Bolkowitz, ros. Bolkovicje, mczko, pow. woliński, par. Więcko, par. gr.-kat. w miejscu, gm. Pastwiska w gub. lidzkiej, szkoła w Pustkowiu. W 1800 r. było własnością Adama Lankckowskiego sędziego ziemskiego. Ma 25 dm., 98 mk. Według szem. duch. z r. 1878 było w miejscu dusz rz.kat. 78, żyd. 20. Grunty orne, liczne sady, budynków z drewna 23, bud. mur. 2, na południu wsi staw rybny oraz wiatrak i karczma. W pobliskiej dolinie mała huta szkła. Zabytkowy kościół z XVI w. św. Piotra i Pawła w centrum wsi. W 1860 r. Lanckowscy założyli tu mały przytułek dla włościan. L. Doz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "Rozpoczynam analizę hasła 'Bolkowce', koncentrując się na ekstrakcji danych dotyczących struktury wyznaniowej ludności, aby wypełnić strukturę 'ludność_wyznanie'.",
        "Przeszukuję tekst w poszukiwaniu słów kluczowych wskazujących na dane demograficzne o charakterze religijnym, takich jak 'dusze', 'wyznanie', 'kat.', 'żyd.', 'ewang.', 'prawosł.' lub odniesień do źródeł kościelnych jak 'szematyzm' ('szem.').",
        "Identyfikuję kluczowe zdanie zawierające poszukiwane dane: 'Według szem. duch. z r. 1878 było w miejscu dusz rz.kat. 78, żyd. 20.'.",
        "Analizuję kontekst. Sformułowanie 'było w miejscu' jednoznacznie wskazuje, że dane dotyczą głównej miejscowości opisywanej w haśle. Na tej podstawie ustalam wartość pola 'dotyczy' na 'główna miejscowość'.",
        "Tworzę główny obiekt w liście 'ludność_wyznanie', ustawiam jego pole 'dotyczy' i inicjuję wewnątrz pustą listę 'struktura_wyznaniowa', którą będę teraz wypełniać.",
        "Przechodzę do parsowania listy wyznań i liczby wiernych:",
        " - Pierwszy element to 'rz.kat. 78'.",
        "   - Ekstrahuję oryginalny skrót 'rz.kat.' (w wynikowej strukturze normalizuję go do 'rz. kat.', dodając spację dla spójności) i przypisuję go do pola 'wyznanie_ocr'.",
        "   - Ekstrahuję liczbę '78' i przypisuję ją do pola 'liczba'.",
        "   - Tworzę pierwszy obiekt w liście 'struktura_wyznaniowa'.",
        " - Drugi element to 'żyd. 20'.",
        "   - Ekstrahuję skrót 'żyd.' i przypisuję go do pola 'wyznanie_ocr'.",
        "   - Ekstrahuję liczbę '20' i przypisuję ją do pola 'liczba'.",
        "   - Tworzę drugi obiekt w liście 'struktura_wyznaniowa'.",
        "Odnotowuję również informację o dacie, z której pochodzą dane ('z r. 1878'). Chociaż jest to cenny kontekst, docelowa struktura JSON nie posiada pola na datę w tym miejscu, więc informacja ta nie jest dodawana do finalnego wyniku.",
        "Skanuję pozostałą część hasła, aby upewnić się, że nie ma w niej innych danych dotyczących wyznań. Nie znajduję. Proces ekstrakcji danych o strukturze wyznaniowej został zakończony. Finalna lista zawiera dwa wpisy, co odpowiada informacjom zawartym w tekście."
    ],
    "ludność_wyznanie": [
        {{
            "dotyczy": "główna miejscowość",
            "struktura_wyznaniowa": [
                {{
                    "wyznanie_ocr": "rz. kat.",
                    "liczba": "78"
                }},
                {{
                    "wyznanie_ocr": "żyd.",
                    "liczba": "20"
                }}
            ]
        }}
    ]
    }}```
    ---
    **PRZYKŁAD:**

    **Hasło:** Wielkowice
    **Tekst hasła:** Wielkowice albo Wielkowiec, wś i folw., pow. pruski, gm. Hotków. Cerkiew par. i szkoła religijna,
    parafia kat. w Hotkowie,. W 1827 r. wieś ma 115 dm., 456 mk., w 1878 r. 123 dm. i 569 mk., 370 prawosł., 130 katol., 69 żyd. Folwark położony jest po drugiej stronie strumienia Malinowskiego, w w 1878 r. miał 12 dm. i 40 mk. (18 obrz. gr.-kat., 22 rzym.-kat). 1560 roku król Zygmunt August nadał wieś Janowi Potockiemu za zasługi. We wsi 2 młyny i wiatrak, gospoda przydrożna. Na płn od wsi znaleziono urny i starożytne siekierki z brązu. Przy folwarku stacja hodowli koni. We wsi kasa pożyczkowa z kapitałem 350 rb. Obecnie własność skarbowa. K. Prz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "Rozpoczynam analizę hasła 'Wielkowice' pod kątem ekstrakcji danych o strukturze wyznaniowej. Hasło opisuje zarówno wieś ('wś'), jak i folwark ('folw.'), więc spodziewam się, że dane wyznaniowe mogą być podane oddzielnie dla obu tych części.",
            "Przeszukuję tekst w poszukiwaniu danych liczbowych powiązanych z terminologią wyznaniową (np. 'prawosł.', 'katol.', 'żyd.', 'obrz. gr.-kat.').",
            "Identyfikuję pierwszy blok danych wyznaniowych, który pojawia się w kontekście opisu wsi: '...w 1878 r. ... 569 mk., 370 prawosł., 130 katol., 69 żyd.'.",
            " - Dane te bezpośrednio następują po łącznej liczbie mieszkańców wsi (569 mk) dla roku 1878. To jednoznacznie określa podmiot. Tworzę pierwszy obiekt w liście 'ludność_wyznanie' i ustawiam jego pole 'dotyczy' na 'wieś Wielkowice'.",
            " - Wykonuję kontrolę spójności danych: 370 + 130 + 69 = 569. Suma zgadza się z podaną liczbą mieszkańców wsi, co potwierdza, że jest to kompletny rozkład wyznaniowy dla tej grupy.",
            " - Przystępuję do ekstrakcji poszczególnych par, zwracając uwagę na pole 'liczebność' w schemacie wynikowym:",
            "   - '370 prawosł.' -> tworzę obiekt {{'wyznanie_ocr': 'prawosł.', 'liczebność': '370'}}.",
            "   - '130 katol.' -> tworzę obiekt {{'wyznanie_ocr': 'katol.', 'liczebność': '130'}}.",
            "   - '69 żyd.' -> tworzę obiekt {{'wyznanie_ocr': 'żyd.', 'liczebność': '69'}}.",
            " - Zakończyłem przetwarzanie danych dla wsi.",
            "Identyfikuję drugi blok danych wyznaniowych, znajdujący się w opisie folwarku: 'Folwark ... w 1878 r. miał 12 dm. i 40 mk. (18 obrz. gr.-kat., 22 rzym.-kat).'.",
            " - Podmiot jest jasno określony jako 'folwark'. Tworzę drugi obiekt w liście 'ludność_wyznanie' i ustawiam jego pole 'dotyczy' na 'folwark Wielkowice'.",
            " - Ponownie wykonuję kontrolę spójności: 18 + 22 = 40. Suma zgadza się z podaną liczbą mieszkańców folwarku (40 mk), co potwierdza, że dane w nawiasie to kompletny rozkład wyznaniowy dla folwarku.",
            " - Przystępuję do ekstrakcji danych z nawiasu:",
            "   - '18 obrz. gr.-kat.' -> tworzę obiekt {{'wyznanie_ocr': 'obrz. gr.-kat.', 'liczebność': '18'}}.",
            "   - '22 rzym.-kat' -> tworzę obiekt {{'wyznanie_ocr': 'rzym.-kat', 'liczebność': '22'}}.",
            " - Zakończyłem przetwarzanie danych dla folwarku.",
            "Przeskanowałem resztę hasła i nie znalazłem więcej informacji o strukturze wyznaniowej. Proces ekstrakcji został zakończony. Udało się poprawnie zidentyfikować i rozdzielić dane dla dwóch odrębnych części miejscowości, tworząc dwa wpisy w finalnej liście 'ludność_wyznanie'."
    ],
    "ludność_wyznanie": [
        {{
            "dotyczy": "wieś Wielkowice",
            "struktura_wyznaniowa": [
                {{
                    "wyznanie_ocr": "prawosł.",
                    "liczba": "370"
                }},
                {{
                    "wyznanie_ocr": "katol.",
                    "liczba": "130"
                }},
                {{
                    "wyznanie_ocr": "żyd.",
                    "liczba": "69"
                }}
            ]
        }},
        {{
            "dotyczy": "folwark Wielkowice",
            "struktura_wyznaniowa": [
                {{
                    "wyznanie_ocr": "obrz. gr.-kat.",
                    "liczba": "18"
                }},
                {{
                    "wyznanie_ocr": "rzym.-kat",
                    "liczba": "22"
                }}
            ]
        }}
    ]
    }}```
    ---
    """

    return user_prompt
