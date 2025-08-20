""" prompt do ekstrakcji informacji:
- własność ziemska
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
    Uwzględniaj **TYLKO** dane dotyczące XIX wieku, pomiń starsze informacje historyczne.

    **Własność ziemska (pole 'własność_ziemska')**
    *  wyszukaj informacje o własności ziemskiej, w znaczeniu gruntów, które znajdują się w opisywanej miejscowości. Uwzględnij ogólną powierzchnię gruntów, oraz (jeżeli podano) dane szczegółowe np. ziemia orna, ogrody, łąki, lasy, pastwiska, nieużytki, zarośla itp. Powierzchnia gruntu może być podana w hektarach (ha) morgach (mr), arach (ar) lub innych jednostkach. Niekiedy podana jets tylko ogólna powierzchnia bez wyszczególnienia rodzaju gruntu, wówczas zapisz ta informację z etykieta 'obszar ogółem'. W treści haseł mogą znajdować się inne informacje np. o liczbie mieszkańców (mk) lub liczbie domów (dm), te informacje pomiń, ważna jest tylko struktura własności ziemskiej. W haśle mogą znajdować się informacje o kilku własnościach ziemskich, np. osobno o wsi i osobno o folwarku, zapisz je wówczas osobno, jako kolejne struktury na liście, w polu 'land_name' zapisz nazwę danej własności np. 'wieś Echtz', 'folwark Marienwalde'.

    **INFORMACJE POMOCNICZE:**
    *   W tekście mogą występować skróty. Oto lista najczęstszych: {lista_skrotow}.
    *   Uwzględniaj **TYLKO I WYŁĄCZNIE** dane pochodzące z dostarczonego tekstu hasła.
    *   Jeżeli w tekście brak jakiejś informacji, pomiń daną kategorię informacji w wynikowej strukturze.

    {text_schema}

    ---
    **PRZYKŁAD:**

    **Hasło:** Bolkowce
    **Tekst hasła:** Bolkowce, niem. Bolkowitz, ros. Bolkovicje, wś, pow. woliński, par. Więcko, par. gr.-kat. w miejscu, gm. Pastwiska w gub. lidzkiej, szkoła w Pustkowiu. W 1800 r. było własnością Adama Lankckowskiego sędziego ziemskiego. Ma 25 dm., 98 mk. Według szem. duch. z r. 1878 było w miejscu dusz rz.kat. 78, żyd. 20. Grunty orne, liczne sady: powierzchnia roli or. i ogrodów 516'27 ha., łąk 118'03, pastw. 119'41, boru 412.03, nieużytków 22'62, wody 0'61, razem 1188'97 ha. Budynków z drewna 23, bud. mur. 2, na południu wsi staw rybny oraz wiatrak i karczma. W pobliskiej dolinie mała huta szkła. Zabytkowy kościół z XVI w. św. Piotra i Pawła w centrum wsi. W 1860 r. Lanckowscy założyli tu mały przytułek dla włościan. L. Doz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
         "Rozpoczynam analizę hasła 'Bolkowce' w celu ekstrakcji szczegółowych danych o strukturze własności ziemskiej. Celem jest wypełnienie zagnieżdżonej struktury 'własność_ziemska'.",
        "Przeszukuję tekst w poszukiwaniu słów kluczowych wskazujących na dane powierzchniowe, takich jak 'powierzchnia', 'rola', 'grunty', 'ha' (lub morgi).",
        "Identyfikuję kluczowe zdanie zawierające szczegółowy wykaz gruntów: 'powierzchnia roli or. i ogrodów 516'27 ha., łąk 118'03, pastw. 119'41, boru 412.03, nieużytków 22'62, wody 0'61, razem 1188'97 ha.'.",
        "Na podstawie kontekstu całego hasła, które opisuje 'Bolkowce' jako wieś ('wś'), ustalam, że te dane dotyczą głównej jednostki osadniczej. Tworzę główny obiekt w liście 'własność_ziemska' i ustawiam jego pole 'land_name' na 'wieś Bolkowce'.",
        "Inicjuję pustą listę 'land' wewnątrz tego obiektu, do której będę dodawał poszczególne typy gruntów.",
        "Przetwarzam pierwszy element z listy: 'roli or. i ogrodów 516'27 ha.'.",
        " - Ekstrahuję typ gruntu. Normalizuję formę gramatyczną ('roli') do mianownika, uzyskując 'rola orna i ogrody'.",
        " - Ekstrahuję powierzchnię. Identyfikuję liczbę '516'27' i jednostkę 'ha.'. Normalizuję format, zamieniając separator ' ' ' na przecinek, aby uzyskać '516,27 ha'.",
        " - Tworzę pierwszy obiekt {{'type_of_ground': 'rola orna i ogrody', 'area_of_ground': '516,27 ha'}} i dodaję go do listy 'land'.",
        "Przetwarzam kolejny element: 'łąk 118'03'. Normalizuję 'łąk' do 'łąki' oraz '118'03' do '118,03 ha'. Tworzę i dodaję odpowiedni obiekt.",
        "Przetwarzam 'pastw. 119'41'. Rozwijam skrót 'pastw.' do 'pastwiska'. Normalizuję '119'41' do '119,41 ha'. Tworzę i dodaję obiekt.",
        "Przetwarzam 'boru 412.03'. Normalizuję 'boru' do 'bór'. Dodaję semantyczne uzupełnienie '(las)', aby wynik był bardziej czytelny. Zauważam, że tutaj separatorem jest kropka, więc normalizuję '412.03' do '412,03 ha'. Tworzę i dodaję obiekt.",
        "Przetwarzam 'nieużytków 22'62'. Normalizuję 'nieużytków' do 'nieużytki'. Normalizuję '22'62' do '22,62 ha'. Tworzę i dodaję obiekt.",
        "Przetwarzam ostatni element: 'wody 0'61'. Normalizuję 'wody' do 'wody' i '0'61' do '0,61 ha'. Tworzę i dodaję obiekt.",
        "Zauważam na końcu fragment 'razem 1188'97 ha.'. Ponieważ docelowa struktura JSON nie przewiduje pola na sumę całkowitą, świadomie pomijam tę informację.",
        "Weryfikuję, czy w tekście są inne dane o strukturze agrarnej. Nie znajduję. Odnotowuję, że informacje o historycznych właścicielach (np. 'własnością Adama Lankckowskiego') nie pasują do schematu i również je pomijam.",
        "Proces ekstrakcji danych o własności ziemskiej został zakończony. Lista 'land' zawiera 6 obiektów, co odpowiada liczbie typów gruntów wymienionych w tekście źródłowym."
    ],
    "własność_ziemska": [
        {{
            "land_name": "wieś Bolkowce",
            "land": [
                {{
                    "type_of_ground": "rola orna i ogrody",
                    "area_of_ground": "516,27 ha"
                }},
                {{
                    "type_of_ground": "łąki",
                    "area_of_ground": "118,03 ha"
                }},
                {{
                    "type_of_ground": "pastwiska",
                    "area_of_ground": "119,41 ha"
                }},
                {{
                    "type_of_ground": "bór (las)",
                    "area_of_ground": "412,03 ha"
                }},
                {{
                    "type_of_ground": "nieużytki",
                    "area_of_ground": "22,62 ha"
                }},
                {{
                    "type_of_ground": "wody",
                    "area_of_ground": "0,61 ha"
                }}
            ]
        }}
    ]
    }}```
    ---
    **PRZYKŁAD:**

    **Hasło:** Wielkowice
    **Tekst hasła:** Wielkowice albo Wielkowiec, wś i folw., pow. pruski, gm. Hotków. Cerkiew par. i szkoła religijna,
    parafia kat. w Hotkowie,. W 1827 r. wieś ma 115 dm., 456 mk., w 1878 r. 123 dm. i 569 mk. Folwark położony jest po drugiej stronie strumienia Malinowskiego, w w 1878 r. miał 12 dm. i 40 mk. 1560 roku król Zygmunt August nadał wieś Janowi Potockiemu za zasługi. We wsi 2 młyny i wiatrak, gospoda przydrożna. Grunty we wsi mają obszaru 338 mr. a z tych 249 roli, 9 łąk i ogr., 24 past, i 56 mr. lasu. Grunty folwarku liczą 431 mr., z czego uprawia się 361 mr., 21 jest łąk, 41 past, a 8 lasu. Na płn od wsi znaleziono urny i starożytne siekierki z brązu. Przy folwarku stacja hodowli koni. We wsi kasa pożyczkowa z kapitałem 350 rb. Obecnie własność skarbowa. K. Prz.

    **Wynik w formie struktury JSON:**
    ```json
    {{
    "chain_of_thought": [
        "Rozpoczynam analizę hasła 'Wielkowice' w celu ekstrakcji danych o strukturze własności ziemskiej. Zauważam, że hasło opisuje zarówno wieś, jak i folwark, co sugeruje, że będę musiał utworzyć dwa oddzielne zestawy danych w finalnej strukturze.",
        "Przeszukuję tekst w poszukiwaniu fragmentów opisujących grunty. Identyfikuję dwa kluczowe zdania, które wydają się zawierać poszukiwane informacje.",
        "Przystępuję do analizy pierwszego zdania: 'Grunty we wsi mają obszaru 338 mr. a z tych 249 roli, 9 łąk i ogr., 24 past, i 56 mr. lasu.'.",
        " - Na podstawie frazy 'Grunty we wsi' jednoznacznie identyfikuję podmiot danych. Tworzę pierwszy główny obiekt w liście 'własność_ziemska' i ustawiam jego pole 'land_name' na 'wieś Wielkowice'.",
        " - Odnotowuję informację o całkowitej powierzchni ('338 mr.'), ale pomijam ją w ekstrakcji, ponieważ docelowy schemat JSON nie posiada pola na sumę.",
        " - Przechodzę do szczegółowego wykazu, ekstrahując i normalizując każdą parę 'typ gruntu' - 'powierzchnia':",
        "   - '249 roli' -> typ: 'ziemia orna', powierzchnia: '249 mr.'.",
        "   - '9 łąk i ogr.' -> typ: 'łąki i ogrody', powierzchnia: '9 mr.'.",
        "   - '24 past' -> rozwijam skrót 'past' do 'pastwiska', typ: 'pastwiska', powierzchnia: '24 mr.'.",
        "   - '56 mr. lasu' -> normalizuję dopełniacz 'lasu' do mianownika, typ: 'lasy', powierzchnia: '56 mr.'.",
        " - Zakończyłem przetwarzanie danych dla wsi. Lista 'land' w pierwszym obiekcie zawiera 4 elementy.",
        "Przystępuję do analizy drugiego zdania: 'Grunty folwarku liczą 431 mr., z czego uprawia się 361 mr., 21 jest łąk, 41 past, a 8 lasu.'.",
        " - Fraza 'Grunty folwarku' jasno wskazuje na drugi podmiot. Tworzę drugi, oddzielny obiekt w liście 'własność_ziemska' i ustawiam jego 'land_name' na 'folwark'.",
        " - Ponownie pomijam informację o sumarycznej powierzchni ('431 mr.') zgodnie ze schematem.",
        " - Przechodzę do szczegółowego wykazu dla folwarku:",
        "   - 'uprawia się 361 mr.' -> interpretuję to wyrażenie jako 'ziemia orna', typ: 'ziemia orna', powierzchnia: '361 mr.'.",
        "   - '21 jest łąk' -> typ: 'łąki', powierzchnia: '21 mr.'.",
        "   - '41 past' -> typ: 'pastwiska', powierzchnia: '41 mr.'.",
        "   - '8 lasu' -> typ: 'lasy', powierzchnia: '8 mr.'.",
        " - Zakończyłem przetwarzanie danych dla folwarku. Lista 'land' w drugim obiekcie również zawiera 4 elementy.",
        "Skanuję resztę hasła, aby upewnić się, że nie ma więcej danych o gruntach. Nie znajduję ich. Proces ekstrakcji został zakończony pomyślnie, tworząc dwa odrębne wpisy w liście 'własność_ziemska', co wiernie odzwierciedla strukturę informacji w tekście źródłowym."
    ],
    "własność_ziemska": [
        {{
            "land_name": "wieś Wielkowice",
            "land": [
                {{
                    "type_of_ground": "ziemia orna",
                    "area_of_ground": "249 mr."
                }},
                {{
                    "type_of_ground": "łąki i ogrody",
                    "area_of_ground": "9 mr."
                }},
                {{
                    "type_of_ground": "pastwiska",
                    "area_of_ground": "24 mr."
                }},
                {{
                    "type_of_ground": "lasy",
                    "area_of_ground": "56 mr."
                }}
            ]
        }},
        {{
            "land_name": "folwark",
            "land": [
                {{
                    "type_of_ground": "ziemia orna",
                    "area_of_ground": "361 mr."
                }},
                {{
                    "type_of_ground": "łąki",
                    "area_of_ground": "21 mr."
                }},
                {{
                    "type_of_ground": "pastwiska",
                    "area_of_ground": "41 mr."
                }},
                {{
                    "type_of_ground": "lasy",
                    "area_of_ground": "8 mr."
                }}
            ]
        }}
    ]
    }}```
    ---
    """

    return user_prompt
