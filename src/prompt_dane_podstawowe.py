""" prompt do ekstrakcji danych podstawowych"""

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
    1.  **Przeanalizuj przekazany tekst hasła słownika SGKP:**
    2.  **Wypełnij pola:** Na podstawie swojej analizy, wypełnij pozostałe pola w strukturze JSON.

    **SZCZEGÓŁOWE REGUŁY EKSTRAKCJI:**

    **1. Typ Hasła (`typ`):**
    *   Określ, co opisuje hasło (np. wieś, miasto, folwark, rzeka, jezioro, góra), czasem może to być więcej niż jedno określenie np. wieś, folwark.
    *   **Reguła specjalna:** Jeżeli tekst hasła zawiera skrót `ob.` (obacz), jest to odsyłacz (chyba, że
        skrót występuje w nawiasie wówczas nie oznacza to że hasło jest odsyłaczem). W takim przypadku wypełnij **tylko** pole `typ` wartością "odsyłacz" i pozostaw resztę pól jako `null`. Nazwa po `ob.` to inne hasło, a nie wariant nazwy.
        Wynik zapisz w formie listy np. ['wieś'] lub ['wieś', 'folwark'] w polu 'typ'.

    **2. Warianty Nazw (`warianty_nazw`):**
    *   Wyszukaj alternatywne lub obcojęzyczne nazwy hasła, podane zwykle na samym początku. Niekiedy warianty nazw podane są razem z datą, kiedy występowały. Wariant nazwy musi się różnić od nazwy hasła podanej na początku tekstu hasła.
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
        * Nazwę parafii katolickiej zapisz w polu 'parafia_katolicka', jeżeli w tekście znajdzie się parafia dla
        innego wyzania zapisz ją w polu 'parafia_inna' jako element listy w formie struktury np. [{ "wyznanie": "nazwa wyznania", "nazwa_parafii": "nazwa miejscowości" }] - zob.
        też przykłady niżej.

    **5. Autor (`autor`):**
    *   **Kluczowa reguła:** Autor to **TYLKO I WYŁĄCZNIE** inicjały lub nazwisko znajdujące się na **samym końcu** tekstu hasła (np. `Br. Ch.`, `F. S.`, `Sulimierski`).
    *   **ZIGNORUJ** wszelkie inicjały i nazwiska pojawiające się w środku tekstu, ponieważ dotyczą one postaci historycznych, a nie autorów hasła.
    * W przypadku haseł zbiorczych pole 'autor' wypełnij tylko raz dla hasła zbiorczego, a nie dla ostatniego pod-hasła z serii. Autor jest w takim przypadku wspólny dla hasła.

    **INFORMACJE POMOCNICZE:**
    *   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
    *   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
    *   Nazwy (miejscowości, gminy, powiaty, parafie) zapisuj w formie mianownika, inne jednostki np. hrabstwa, starostwa - pomiń.
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
        "2. Identyfikuję typ miejscowości: 'mczko' to miasteczko, dodaję taką wartość do listy: ['miasteczki'] i zapisuję w polu 'typ'.",
        "3. Znajduję dane administracyjne: 'pow. woliński', 'gm. Pastwiska'. Gubernia: lidzka, w niej miejści się gmina więc także miejscowość.",
        "4. Analizuję parafie: 'par. Więcko' to parafia katolicka. 'par. gr.-kat. w miejscu' to parafia inna.",
        "5. Sprawdzam koniec tekstu w poszukiwaniu autora. Znajduję 'L. Doz.'."
    ],
    "warianty_nazw": [
        {{"lang": "niem.", "wariant_nazwy": "Bolkowitz"}},
        {{"lang": "ros.", "wariant_nazwy": "Bolkovicje"}}
    ],
    "typ": ["miasteczko"],
    "powiat": "woliński",
    "gmina": "Pastwiska",
    "gubernia": lidzka,
    "parafia_katolicka": "Więcko",
    "parafia_inna":
            [
                { "wyznanie": "gr.-kat.", "nazwa_parafii": "Bolkowce" }
    ],
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
        "2. Identyfikuję typ miejscowości: 'wś' to 'wieś', folw. to 'folwark', zapisuję wyik w formie listy: ['wieś', 'folwark'] w polu 'typ'",
        "3. Znajduję dane administracyjne: 'pow. pruski', 'gm. Hotków'. Guberni brak.",
        "4. Analizuję parafie: 'cerkiew par.' oznacza że parafia prawosławna jest na miejscu, czyli w Wielkowicach. 'parafia kat w Hotkowie': parafia Hotków",
        "5. Sprawdzam koniec tekstu w poszukiwaniu autora. Znajduję 'K. Prz.'."
    ],
    "warianty_nazw": [
        {{"lang": "nieokr.", "wariant_nazwy": "Wielkowiec"}}
    ],
    "typ": ["wieś", "folwark"],
    "powiat": "pruski",
    "gmina": "Hotków",
    "gubernia": null,
    "parafia_katolicka": "Hotków",
    "parafia_inna": [
        { "wyznanie": "praw.", "nazwa_parafii": "Wielkowice" }
    ],
    "autor": "K. Prz."
    }}
    ---
    """

    return user_prompt
