""" prompt do ekstrakcji informacji:
- szkoly
- urzedy
- celne
- biblioteki_czytelnictwo
- gastronomia_hotelarstwo
- opieka_zdrowotna
- handel
- dobroczynnosc
- sądownictwo
- hodowla (TYLKO stajnie/owczarnie i obiekty hodowlane; bez pastwisk)
- ksiegarnie i drukarnie
- zegluga (porty, przystanie, promy, spław, tratwy, łodzie, przeprawy)
- bursy
- infrastruktura_miejska (wodociągi, bruk, oświetlenie itd.)
- poczta (st. p., poczta, poczthalteria)
- samorzad (zarządy gmin/powiatów)
- policja (posterunki, zarządy policyjne, biuro policmajstra)
- instytucje finansowe
- uzdrowiska
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

    Wyszukaj i zapisz w polach struktury JSON informacje o poszukiwanych obiektach
    Uwzględniaj **TYLKO I WYŁĄCZNIE** obiekty znajdujące się na terenie opisywanej miejscowości.
    Uwzględniaj **TYLKO** obiekty funkcjonujące w czasie powstawania SGKP - w XIX wieku, starsze informacje historyczne - pomiń.

    **1. Szkoły (pole `szkoły`):**
    *   Wyszukaj szkoły i uczelnie w opisywanej miejscowości: szkoła elementarna, 1-oddziałowa, etatowa, jednokl., szkoła niezorganizowana, gimnazjum, liceum, uniwersytet, szkoła religijna, szkoła etat. 1-kl., szkoła początkowa, szkoła ludowa itp.).

    **2. Urzędy ('urzędy')**
    *   wyszukaj obiekty typu: urząd gminny, urząd miejski, urząd ziemski, landratura, urząd powiatowy, urząd poborowy, urząd katastrowy, rada miejska, rada powiatowa, rząd gubernialny, landrat. Informacje o zarządzie gminnym lub powiatowym pomiń, to inna kategoria informacji (samorząd).

    **3. Obiekty, budynki celne ('celne')
    *   urząd celny, izba celna, rogatki, komora celna, podkomorek, posterunek celny itp.

    **4. Biblioteki ('biblioteki')
    *   znajdź obiekty w rodzaju: biblioteka, czytelnia

    **5. Gastronomia, hotelarstwo ('gastronomia_hotele')
    *   karczma, zajazd, piwiarnia, hotel, restauracja, oberża, austeria, garkuchnia, traktiernia, kawiarnia, kafenhauz, szynk

    **6. Opieka_zdrowotna ('opieka_zdrowotna')
    *   szpital, lazaret, klinika, zakład dla obłąkanych, ambulatorium, lecznica

    **7. Handel ('handel')
    *   sklep, targ, kram, jarmark, targowisko, hala targowa, jatka, skład bławatny itp.

    **8. Dobroczynność ('dobroczynność')
    *   przytułek, przytulisko, dom sierot, dom opieki, dom schronienia, zakład dla zniedołężniałych, towarzystwo dobroczynności, fundacja dobroczynna

    **9. Sądownictwo ('sądy')
    *   sąd, sąd gminny, sąd pokoju, sąd okręgowy, sąd powiatowy, sąd ziemski, sąd ziemiański, izba sądowa, trybunał itp.

    **10. Hodowla ('hodowla')**
    *   TYLKO stajnie/owczarnie i obiekty hodowlane, zakłady stadnicze; bez pastwisk.

    **11. Ksiegarnie, drukarnie ('księgarnie_drukarnie')**
    *   księgarnia, drukarnia, skład nut, skład map, antykwariat, oficyna drukarska, zakład litograficzny.

    **12. Żegluga ('żegluga')**
    *   obiekty: porty, przystanie, promy, spław, tratwy, łodzie, przeprawy.

    **13. Bursy ('bursy')**
    *   obiekty: bursa, internat, konwikt itp.

    **14. Infrastruktura_miejska ('infrastruktura_miejska')**
    *   obiekty typu: wodociągi, bruk, oświetlenie itd.

    **15. Poczta ('poczta')**
    *   st. p. (stacja pocztowa), poczta, poczthalteria, stacja telegrafu, agentura pocztowa - tylko na obszarze opisywanej miejscowości, wzmianki np. o st. p. w innych miejscowościach pomiń, np. sformułowanie st. p. Clunie oznacza stację pocztową w miejcowości Clunie a nie w miejscowości opisywanej w haśle.

    **16. Samorząd ('samorząd')**
    *   zarządy gmin/powiatów

    **17. Policja ('policja')**
    *   posterunki policji, zarządy policyjne, biuro policmajstra, naczelnik policji, cyrkuł

    **18. Instytucje finansowe ('instytucje_finansowe')**
    *   banki, kasy pożyczkowe, kasy zapomogowe itp.

    **19. Uzdrowiska ('uzdrowiska')**
    * obiekty typu: uzdrowisko, zakład kąpielowy, zakład przyrodoleczniczy, kurort, zdrój, dom zdrojowy, zakład wodoleczniczy, pijalnia wód, inhalatorium, zakład borowinowy, kurhaus, kąpielisko, stacja klimatyczna, źródło wody siarczanej, zakład kąpielowy, zakład kuracyjny, zakład hydropatyczny, kuracja żętycowa, kurhauz


    **INFORMACJE POMOCNICZE:**
    *   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
    *   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
    *   Uwzględniaj **TYLKO I WYŁĄCZNIE** obiekty znajdujące się w opisywanej przez hasło miejscowości
    *   Nazwy zapisuj w formie mianownika.
    *   Jeżeli w tekście brak jakiejś informacji, pomiń daną kategorię informacji w wynikowej strukturze.

    {text_schema}

    ---
    **PRZYKŁAD:**

    **Hasło:** Bolkowce
    **Tekst hasła:** Bolkowce, niem. Bolkowitz, ros. Bolkovicje, mczko, pow. woliński, par. Więcko, par. gr.-kat. w miejscu, gm. Pastwiska w gub. lidzkiej, szkoła w Pustkowiu. W 1800 r. było własnością Adama Lankckowskiego sędziego ziemskiego, ma 25 dm., 98 mk. Grunty orne, liczne sady, budynków z drewna 23, bud. mur. 2, na południu wsi staw rybny oraz wiatrak i karczma. W pobliskiej dolinie mała huta szkła. Zabytkowy kościół z XVI w. św. Piotra i Pawła w centrum wsi. W 1860 r. Lanckowscy założyli tu mały przytułek dla włościan. L. Doz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "Rozpoczynam analizę hasła 'Bolkowce'. Przeczytam tekst zdanie po zdaniu, identyfikując słowa kluczowe pasujące do zdefiniowanych kategorii w modelu Pydantic.",
        "Pierwsze zdanie zawiera informacje o lokalizacji i przynależności administracyjnej: 'mczko, pow. woliński, par. Więcko, par. gr.-kat. w miejscu, gm. Pastwiska w gub. lidzkiej'. Analizuję pod kątem pól 'urzedy' i 'samorzad'. Tekst wskazuje przynależność do gminy Pastwiska, ale nie mówi o istnieniu urzędu gminy na miejscu w Bolkowcach. Dlatego te pola pomijam.",
        "Następnie znajduję frazę: 'szkoła w Pustkowiu'. Słowo kluczowe 'szkoła' pasuje do pola 'szkoly'. Odnotowuję, że szkoła nie znajduje się bezpośrednio w Bolkowcach, ale w pobliskim Pustkowiu. Mimo, że jest to informacja o infrastrukturze edukacyjnej dla mieszkańców, to zgodnie z instrukcją pomijam ją, gdyż uwzględniane mają być tylko i wyłącznie obiekty na terenie opisywanej miejscowości.",
        "Kolejne zdania opisują charakter wsi: '25 dm., 98 mk. Grunty orne, liczne sady, budynków z drewna 23, bud. mur. 2'. Nie znajduję tu pasujących słów kluczowych do żadnej z kategorii w modelu.",
        "W opisie pojawia się fraza: 'na południu wsi staw rybny oraz wiatrak i karczma'. Dzielę to na części:",
        " - 'staw rybny': Analizuję, gdzie przypisać ten obiekt. Najbardziej pasującą kategorią jest 'hodowla', ponieważ hodowla ryb jest formą gospodarowania zasobami naturalnymi. Zapisuję 'staw rybny' w polu 'hodowla'.",
        " - 'wiatrak': Zastanawiam się nad kategorią dla wiatraka. Jest to obiekt gospodarczy/przemysłowy. W modelu Pydantic nie ma kategorii 'przemysł'. Nie jest to bezpośrednio obiekt handlowy, więc pole 'handel' nie jest idealnym dopasowaniem. Decyduję się pominąć ten obiekt, ponieważ nie pasuje jednoznacznie do żadnej z predefiniowanych kategorii.",
        " - 'karczma': Słowo kluczowe 'karczma' jest bezpośrednim i jednoznacznym dopasowaniem do kategorii 'gastronomia'. Ekstrahuję 'karczma'.",
        "Czytam dalej: 'W pobliskiej dolinie mała huta szkła'. Podobnie jak w przypadku wiatraka, 'huta szkła' to obiekt przemysłowy. Wobec braku odpowiedniej kategorii w modelu, pomijam tę informację.",
        "Następna informacja to 'Zabytkowy kościół z XVI w. św. Piotra i Pawła w centrum wsi'. W modelu nie ma kategorii dla obiektów sakralnych, więc tę informację pomijam.",
        "Ostatnie istotne zdanie: 'W 1860 r. Lanckowscy założyli tu mały przytułek dla włościan'. Słowo kluczowe 'przytułek' jednoznacznie pasuje do kategorii 'dobroczynnosc'. Ekstrahuję całe wyrażenie 'przytułek dla włościan', aby zachować ważny kontekst, dla kogo był przeznaczony. Zapisuję w polu 'dobroczynnosc'.",
        "Przeskanowałem cały tekst. Przeglądam listę pól w modelu Pydantic, aby upewnić się, że niczego nie pominąłem. W tekście nie znaleziono żadnych informacji na temat pól: 'urzedy', 'celne', 'biblioteki', 'opieka_zdrowotna', 'handel', 'sady', 'ksiegarnie', 'zegluga', 'bursy', 'infrastruktura_miejska', 'poczta', 'samorzad', 'policja', 'instytucje_finansowe', 'uzdrowiska'. Proces ekstrakcji dla hasła Bolkowce został zakończony."
    ],
    "hodowla": ["staw rybny"],
    "gastronomia": ["karczma"],
    "dobroczynność": ["przytułek dla włościan"]
    }}
    ---
    **PRZYKŁAD:**

    **Hasło:** Wielkowice
    **Tekst hasła:** Wielkowice albo Wielkowiec, wś i folw., pow. pruski, gm. Hotków. Cerkiew par. i szkoła religijna,
    parafia kat. w Hotkowie, 115 dm., 456 mk. W 1560 roku król Zygmunt August nadał wieś Janowi Potockiemu za zasługi.
    We wsi 2 młyny i wiatrak, gospoda przydrożna. Na płn od wsi znaleziono urny i starożytne siekierki z brązu. Przy folwarku stacja hodowli koni. We wsi kasa pożyczkowa z kapitałem 350 rb. Obecnie własność skarbowa. K. Prz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "Rozpoczynam analizę hasła 'Wielkowice'. Przetwarzam tekst zdanie po zdaniu, aby zidentyfikować słowa kluczowe pasujące do pól w zdefiniowanym modelu Pydantic.",
        "W pierwszym zdaniu znajduję frazę: 'Cerkiew par. i szkoła religijna'.",
        " - 'Cerkiew par.': Jest to obiekt sakralny. Model Pydantic nie posiada pola dla tego typu obiektów, więc informacja ta jest pomijana.",
        " - 'szkoła religijna': Słowo kluczowe 'szkoła' jednoznacznie pasuje do pola 'szkoly'. Ekstrahuję całe wyrażenie 'szkoła religijna', aby zachować kontekst.",
        "Analizuję informacje o przynależności administracyjnej ('gm. Hotków', 'parafia kat. w Hotkowie'), informacja ta nie świadczy o istnieniu urzędów w samej wsi Wielkowice. Pola 'samorzad' i 'urzedy' pozostają puste.",
        "Przechodzę do zdania: 'We wsi 2 młyny i wiatrak, gospoda przydrożna'.",
        " - '2 młyny i wiatrak': Są to obiekty o charakterze przemysłowo-gospodarczym. W zdefiniowanej strukturze Pydantic brakuje odpowiedniej kategorii, takiej jak 'przemysł'. W związku z tym pomijam te obiekty.",
        " - 'gospoda przydrożna': Słowo kluczowe 'gospoda' jest bezpośrednim dopasowaniem do pola 'gastronomia'. Ekstrahuję całe wyrażenie, aby zachować kontekst ('przydrożna').",
        "Kolejne zdanie wspomina o znaleziskach archeologicznych: 'znaleziono urny i starożytne siekierki z brązu'. Model nie posiada kategorii na obiekty historyczne lub archeologiczne, więc pomijam tę informację.",
        "Następnie znajduję frazę: 'Przy folwarku stacja hodowli koni'. Wyrażenie 'stacja hodowli koni' idealnie pasuje do pola 'hodowla'. Ekstrahuję tę informację.",
        "Czytam dalej: 'We wsi kasa pożyczkowa z kapitałem 350 rb.'. Fraza 'kasa pożyczkowa' jest jednoznacznym dopasowaniem do pola 'instytucje_finansowe'. Zapisuję 'kasa pożyczkowa' w odpowiednim polu.",
        "Finalizuję analizę, sprawdzając, czy w tekście znajdują się informacje pasujące do pozostałych, niewypełnionych pól, takich jak 'celne', 'biblioteki', 'opieka_zdrowotna', 'handel', 'dobroczynnosc', 'sady', 'ksiegarnie', 'zegluga', 'bursy', 'infrastruktura_miejska', 'poczta', 'policja' czy 'uzdrowiska'. Nie znajduję w tekście żadnych dalszych pasujących informacji. Proces ekstrakcji został zakończony."
    ],
    "szkoły": ["szkoła religijna"],
    "gastronomia": ["gospoda przydrożna"],
    "hodowla": ["stacja hodowli koni"],
    "instytucje_finansowe": ["kasa pożyczkowa"]
    }}
    ---
    """

    return user_prompt
