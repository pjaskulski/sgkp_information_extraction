
## Scripts and materials related to the processing of the Geographical Dictionary of the Kingdom of Poland

The texts of individual volumes of the SGKP were divided into entries and sub-entries, then saved in JSON files.

JSON files are processed by scripts (Python) using the LLM model (gpt-4.1-mini) via the OpenAI API. The scripts search for the expected information and return it in the form of structures that supplement the source JSON file.

There are two types of scripts in the **SRC** folder, depending on the processing method:

1. The ‘concurrent*.py’ scripts run immediately, with the JSON files for each volume divided into several to several dozen parts and processed in parallel. The processing time for one volume is approximately 40-50 minutes.

2. 'batch*.py' scripts use the Batch API, i.e., processing tasks are prepared and uploaded to OpenAI servers and processed in a 24-hour cycle (often earlier), after which the results can be downloaded. The advantage of processing in this mode is a 50% lower cost.

3. The auxiliary ‘prompt*.py’ files contain the definition of dynamically created prompts for individual queries/modules.

4. The auxiliary ‘model*.py’ files contain definitions of pydantic classes.

Due to the large amount of different types of data that need to be searched for in the SGKP entries, the extraction procedure has been divided into 6 separate modules (implemented by separate scripts) so that the excess of expected data does not impair the performance of the language model. Particularly difficult data requiring more analysis, such as population, religious structure, or land ownership structure, are processed separately:

  - **basic data**: type, county, municipality, province, Catholic parish, other parish, entry author, name variants
  - **industry monuments**: property owner, industrial facilities, mills, archaeological finds, monuments, landscape architecture, collecting, museology,   necropolises, crafts, forest lodges, palace construction, warehouses, military, sacred buildings, religious congregations
  - **institutions, offices**: schools, offices, customs facilities, libraries, catering, healthcare, trade, charity, courts, breeding, bookstores, shipping, dormitories, urban infrastructure, post office, local government, police, financial institutions, health resorts
  - **statistics**: number of inhabitants, number of houses
  - **religious structure**: number of inhabitants by religion
  - **land ownership**: land ownership structure (types and area of land)

In the **TEST** folder - test results for various models on a test series (basic data extraction)

In the **EXAMPLES** folder - examples of results for various categories of information (for the test series)

In the **DICTIONARY** folder - additional dictionaries (standardized counties, types of settlement points)

In the **OCR** folder - auxiliary scripts for OCR

In the **PROMPT** folder - an example of SGKP content processing directly in aistudio using Gemini Pro: prompt, data file (content of entries) to be attached, example of the result in JSON format, and in the file ‘przygotowywanie_promptow_wskazowki.docx’ - a guide with tips on how to prepare prompts for data extraction.

## Data processing sequence:

1. Basic data: names, administrative units, parishes (concurrent_extract_dane_podstawowe.py)
2. Data completion:
  - counties (uniform names, data_completion_powiaty_ujednolicone.py)
  - settlement point types (data_completion_typy_punktow_osadniczych.py)
  - superior localities for parts of localities (concurrent_extract_miejscowosci_nadrzedne.py)
3. Categories: ownership, industry, historical monuments (concurrent_extract_wlasnosc_przemysl.py)
4. Categories: institutions, offices (concurrent_extract_instytucje_urzedy.py)
5. Statistical data: number of inhabitants, number of houses (concurrent_extract_statystyka.py)
6. Religious structure (concurrent_extract_struktura.py)
7. Land ownership: land type structure (concurrent_extract_landownership.py)
8. Data verification and corrections

## Processing example (Stage 3: owner, industry, monuments, religious buildings, archaeology, etc.), entry Kabarowce from volume 3 of the dictionary. Content:

(The original data, prompt text and results are in Polish and have been translated.)

Kabarowce (Kabarivci in Russian), a village in Złoczów County, 20 kilometers southeast of Złoczów, 7 kilometers northwest of the post office and district court in Zborów, and 5 kilometers southeast of the nearest railway station in Płuhów. To the north lie Wołczkowce, to the east Jarosławce and Kadobińce, to the south Młynowce, to the west Młynowce, Meteniów, and Kazimirówka (a subdivision of Płuhów). The Strypa stream flows through the center of the village. It enters here from Wołczkowio, flows initially southward, forms the village boundary for a short distance, spreads out into a small pond, then turns southwest, forms another pond, turns southward, forms the boundary again for a short distance, then turns west, flows along the southern boundary, enters Młynowce, and flows into the main Strypa River here. The stream valley rises to 356 m at the village entrance and 348 m at the village mouth. On the left bank of the stream, it reaches 413 m at the southeastern end of the village of Złota Góra (Senia Avenue), and on the right bank rises point one to 401 m. The buildings lie in the stream valley, and the Orthodox church is in the very center of the area. On the left bank of the Strypa there is a quarry, 0.5 km. long, and in it the following layers can be distinguished: immediately above the chalk marl lie sandstone beds, 45 m thick, containing only the uppermost layer of the fossil Paludina of stagnalis Bast. This sandstone provides good gravel for road construction. On this sandstone bed lies a shell bed, 0.2 m thick, composed of countless shells (Pectunculus, Arca, Oardum, etc.) and white, fine-grained sand, containing here and there beautiful shells; on top of this lies a 0.8 m thick layer of gray, calcareous, hard clay without fossils, the higher the layer, the richer in sand, finally passing into a layer of yellow sand. A more detailed description of the quarry was given by Dunikowski entitled "Das Gebiet des Strypa-Flusses in Galizien" in Jahrbuch der k. k. geologist. Reichsanst., Wien, vol. 30, p. 45. The larger property has 509 m2 of arable land, 112 meadows and gardens, and 29 pastures; the smaller property has 1,155 m2 of arable land, 22 meadows and gardens, and 4 m2 of pasture. According to the 1880 census, there were 612 m2 in the commune, 60 on the manor area. The inhabitants are of the Greek Catholic faith. Only 29 of the Roman Catholic faith are shematistic. The Greek Catholic parish in this location belongs to the Zborów deanery, Lviv archdiocese. The Roman Catholic parish in Zborów. The village has an Orthodox church, a full-time, single-grade school, a manor house, and a mill. At the beginning of the 19th century, the village belonged to Antoni Kriegshuber, who founded a wax bleaching and candle factory here in 1806 and handed over its management to Józef Kettner, who had been brought from Bohemia. The manager trained a dozen or so village peasants as skilled workers and, with their help, achieved an average annual production of 1,200 stones (a 12-kg stone) of raw wax. The wax bleached in this factory was distinguished by its whiteness, and the wax candles were produced not only in Lviv but also as far as Brody, Bern, Vienna, Prague, and even Munich, etc. (O.B. Gazeta Lwowska 1812, No. 38).

### A series of model 'thoughts':

1. I am looking for information about the owner of the village in the 19th century. The text says that at the beginning of the 19th century, the village belonged to Antoni Kriegshuber, which is information from the 19th century, so the owner is Antoni Kriegshuber.
2. I'm looking for industrial facilities. The text mentions a wax candle factory founded in 1806 by Antoni Kriegshuber, so I'm entering 'wax candle factory'.
3. I'm looking for mills and windmills. The text mentions that there is a mill in the village, so I'm entering 'mill'.
4. I'm looking for archaeological finds. The text lacks information about archaeological finds, so I'm skipping this field.
5. I'm looking for historical monuments. There's no information about historical monuments, so I'm skipping this field.
6. I'm looking for landscape architecture. There's no information, so I'm skipping this field.
7. I'm looking for information about collecting. There's no information, so I'm skipping this field.
8. I'm looking for museums. There's no information, so I'm skipping this field.
9. I'm looking for a necropolis. No information, I'm skipping this field.
10. I'm looking for crafts. No information about craftsmen, I'm skipping this field.
11. I'm looking for forester's lodges. No information, I'm skipping this field.
12. I'm looking for palace buildings. There's a mention of a manor house, so I'm entering 'manor house'.
13. I'm looking for warehouses. No information, I'm skipping this field.
14. I'm looking for military facilities. No information, I'm skipping this field.
15. I'm looking for religious buildings. There's a mention of an Orthodox church, so I'm entering 'Orthodox church'.
16. I'm looking for religious congregations. There's a mention of a Greek Catholic parish, but it's a parish, not a congregation, so I'm skipping this field.

### JSON output (including the results of previous processing steps):

```json
{
    "name": "Kabarowce",
    "volume": "03",
    "page": 647,
    "type": "individual",
    "ID": "03-07091",
    "type": [
        "village"
    ],
    "ocr_county": "złoczowski",
    "catholic_parish": "Zborów",
    "other_parish": [
        {
            "religion": "Greek Catholic",
            "parish_name": "Kabarowce"
        }
    ],
    "name_variants": [
        {
            "lang": "Russian",
            "name_variant": "Kabariwci"
        }
    ],
    "unified_county": "złoczowski",
    "settlement_point_type": [
        "Village"
    ],
    "owner": "Antoni Kriegshuber",
    "industrial": [
        "wax candle factory"
    ],
    "mills": [
        "mill"
    ],
    "palace_building": [
        "manor house"
    ],
        "religious_buildings": [
            "church"
    ]
}
```

---

## Skrypty i materiały związane z przetwarzaniem Słownika Geograficznego Królestwa Polskiego

Teksty poszczególnych tomów SGKP zostały podzielone na hasła i pod-hasła, następnie zapisane w plikach JSON.

Pliki JSON są przetwarzane skryptami (Python) wykorzystującymi model LLM (gpt-4.1-mini) poprzez API OpenAI. Skrypty wyszukują oczekiwane informacje,
zwracając je w formie struktur, które uzupełniają źródłowy plik JSON.

W folderze **SRC** znajdują się dwa rodzaje skryptów, zależnie od sposobu przetwarzania:

1. Skrypty 'concurrent*.py' działają natychmiast, pliki JSON dla każdego tomu dzielone są na kilka-kilkadziesiąt części i przetwarzane równoległe. Czas przetwarzania jednego tomu to około 40-50 minut. 

2. Skrypty 'batch*.py' korzystają z Batch API, czyli zadania przetwarzania są przygotowywane i wgrywane na serwery OpenAI i przetwarzane w ciąg u 24 godzin (często wcześniej), następnie można pobrać wyniki. Zaletą przetwarzania w tym trybie jest koszt niższy o 50%. 

3. Pomocnicze pliki 'prompt*.py' zawierają definicję dynamicznie tworzonych promptów dla poszczególnych zapytań/modułów. 

4. Pomocnicze pliki 'model*.py' zawierają definicje klas pydantic

Ze względu na dużą liczbę różnego rodzaju danych, które należy wyszukać w tekstach haseł SGKP, procedurę ekstrakcji podzielono na 6 osobnych modułów (realizowanych przez osobne skrypty), tak by nadmiarem oczekiwanych danych nie pogorszyć wyniku pracy modelu językowego, szczególnie trudniejsze, wymagające większej analizy dane dotyczące liczby ludności, struktury wyznaniowej czy stryktury własności ziemskiej są przetwarzane osobno.:

   - **dane podstawowe**: typ, powiat, gmina, gubernia, parafia katolicka, parafia inna, autor hasła, warianty nazw
   - **przemysł zabytki**: właściciel majątku, obiekty przemysłowe, młyny, znaleziska archeologiczne, zabytki, architektura krajobrazu, kolekcjonerstwo, muzealnictwo, nekropolie, rzemiosło, leśniczowki, budownictwo pałacowe, magazyny, wojsko, obiekty sakralne, zgromadzenia religijne
   - **instytycje, urzędy**: szkoły, urzędy, obiekty celne, biblioteki, gastronomia, opieka_zdrowotna, handel, dobroczynność, sądy, hodowla, księgarnie, żegluga, bursy, infrastruktura miejska, poczta, samorząd, policja, instytucje finansowe, uzdrowiska 
   - **statystyka**: liczba mieszkańców, liczba domów
   - **struktura wyznaniowa**: liczba mieszkańców według wyznania
   - **własność ziemska**: struktura własności ziemskiej (rodzaje i powierzchnia gruntów)


W folderze **TESTY** - wyniki testów różnych modeli na serii testowej (ekstrakcja danych podstawowych)

W folderze **EXAMPLES** - przykłady wyników dla różnych kategorii informacji (dla serii testowej)

W folderze **DICTIONARY** - dodatkowe słowniki (powiaty ujednolicone, typy punktów osadniczych)

W folderze **OCR** - pomocnicze skrypty do OCR

W folderze **PROMPT** - przykład przetwarzania treści SGKP bezpośrednio w aistudio z użyciem Gemini Pro: prompt, plik z danymi (treścią haseł) do załączenia, przykład wyniku w formacie JSON oraz w pliku 'przygotowywanie_promptow_wskazowki.docx' - **poradnik** ze wskazówkami jak przygotowywać prompty do ekstrakcji danych.

## Kolejność przetwarzania

1. Dane podstawowe: nazwy, jednostki administracyjne, parafie (concurrent_extract_dane_podstawowe.py)
2. Uzupełnianie danych:
  - powiaty (nazwy ujednolicone, data_completion_powiaty_ujednolicone.py)
  - typy punktów osadniczych (data_completion_typy_punktow_osadniczych.py)
  - miejscowości nadrzędne dla części miejscowości (concurrent_extract_miejscowosci_nadrzedne.py)
3. Kategorie: własność, przemysł, zabytki (concurrent_extract_wlasnosc_przemysl.py)
4. Kategorie: instytucje, urzędy (concurrent_extract_instytucje_urzedy.py)
5. Dane statystyczne: liczba mieszkańców, liczba domów (concurrent_extract_statystyka.py)
6. Struktura wyznaniowa (concurrent_extract_struktura.py)
7. Własność ziemska: struktura rodzajów gruntów (concurrent_extract_wlasnosc_ziemska.py)
8. Weryfikacja i poprawki danych 

## Przykład przetwarzania (etap 3: właściciel, przemysł, zabytki, obiekty sakralne, archeologia itd.), hasło Kabarowce z 3 tomu słownika. Treść:

Kabarowce (po rusku Kabariwci), wś w powiecie złoczowskim, 20 kil. na płd.-wsohód od Złoczowa, 7 kil. na półn. od urzędu pocztowego i sądu powiatowego w Zborowie, a 5 kil. na płd.-wsch. od najbliższej stacyi kolejowej w Płuhowie. Na półn. leżą Wołczkowce, na wschód Jarosławce i Kadobińce, na płd. Młynówce, na zachód Młynówce, Meteniów i Kazimirówka (folw. Płuhowa). Przez środek wsi płynie potok Strypa. Wchodzi on tu z Wołczkowio, płynie zrazu na płd., tworzy na krótkiej przestrzeni granicę wsi, rozlewa się w mały stawek, potem skręca na pfd.-zaohód, tworzy drugi stawek, przybiera kierunek płd. i tworzy znowu na krótkiej przestrzeni granicę, poczem skręca na zachód a płynąc wzdłuż granicy płd. wchodzi do Młynowiec i wpada tutaj do głównej Strypy. Dolina potoku wznosi się przy wnijściu do wsi 356 m., przy ujściu ze wsi 348 m. Na lew. brzegu potoku dochodzi w płd.-wsohod. krańcu wsi Złota góra (al. Senia) 413 m., na prawym brzegu wznosi się punkt jeden do 401 m. Zabudowania leżą w dolinie potoku a cerkiew w samym środku obszaru. Na lewym brzegu Strypy znajduje się kamieniołom, 0.5 kil. długi, a w nim rozeznać można następujące pokłady: bezpośrednio nad marglem kredowym leżą ławy piaskowca, 45 m. grube, posiadające tylko w najwyższej warstwie skamielinę Paludina of. stagnalis Bast. Piaskowiec ten dostarcza dobrego szu-1tru do wysypywania drogi. Na tej ławie piaskowca leży ława muszli, 0.2 m. gruba, utworzona z niezliczonych skorupek (Pectunculus, Arca, Oard;um i t. d.) i piasku białego, cienkoziarnistego, zawierającego tu i ówdzie piękne skorupki; na niej leży 0.8 m. gruba warstwa siwej, wapnistej, twardej gliny bez skamielin, im wyżej tem obfitszej w piasek, przechodzącej nakoniec w warstwę żółtego piasku. Dokładniejszy opis kamieniołomu podał Dunikowski p. t. „Das Gebiet des Strypa-Flusses in Galizien” w Jahrbuch der k. k. geolog. Reichsanst., Wien, tom 30, str. 45. Własność większa ma roli ornej 509, łąk i ogr. 112, pastw. 29; własn. mniejsza roli ornej 1155, łąk i ogr. 22, pastw. 4 mr. Wedle spisu z r. 1880 było 612 mk. w gminie, 60 na obszarze dworskim. Mieszkańcy są wyznania gr. kat. Szematyzm wykazuje tylko 29 wyznania rzym. kat. Par. gr. kat. w miejscu, należy do dekanatu Zborowskiego, archid. lwowskiej. Par. rzym. kat. w Zborowie. We wsi jest cerkiew, szkoła etatowa jednokl., dwór i młyn. Na początku XIX w. należała wieś do Antoniego Kriegshubera, który r. 1806 założył tutaj blich wosku i fabrykę świec woskowych i oddał kierownictwo Józefowi Kettnerowi z Czech sprowadzonemu. Kierownik przysposobił kilkunastu włościan tej wsi na zdolnych robotników i przy ich pomocy doprowadził do tego, że corocznie, biorąc średnią miarę, wyrabiano 1200 kamieni (kamień 12 kg.) surowego wosku. Wosk w tej fabryce bielony odznaczał się białością a świece woskowe miały odbyt nietylko wo Lwowie, lecz wywożono je także do Brodów, Berna, Wiednia, Pragi a nawet do Monachium i t. d. (Ob. Gazetę lwowską 1812, N. 38).

### Ciąg 'myśli' modelu:

1. Szukam informacji o właścicielu miejscowości w XIX wieku. Tekst mówi, że na początku XIX wieku wieś należała do Antoniego Kriegshubera, co jest informacją z XIX wieku, więc właścicielem jest Antoni Kriegshuber.
2. Szukam obiektów przemysłowych. W tekście jest wzmianka o fabryce świec woskowych założonej w 1806 roku przez Antoniego Kriegshubera, więc wpisuję 'fabryka świec woskowych'.
3. Szukam młynów i wiatraków. W tekście jest wzmianka, że we wsi jest młyn, więc wpisuję 'młyn'.
4. Szukam znalezisk archeologicznych. W tekście brak informacji o znaleziskach archeologicznych, pomijam to pole.
5. Szukam zabytków. Brak informacji o zabytkach, pomijam to pole.
6. Szukam obiektów architektury krajobrazu. Brak informacji, pomijam to pole.
7. Szukam informacji o kolekcjonerstwie. Brak informacji, pomijam to pole.
8. Szukam muzealnictwa. Brak informacji, pomijam to pole.
9. Szukam nekropolii. Brak informacji, pomijam to pole.
10. Szukam rzemiosła. Brak informacji o rzemieślnikach, pomijam to pole.
11. Szukam leśniczówek. Brak informacji, pomijam to pole.
12. Szukam budownictwa pałacowego. Jest wzmianka o dworze, więc wpisuję 'dwór'.
13. Szukam magazynów. Brak informacji, pomijam to pole.
14. Szukam obiektów wojskowych. Brak informacji, pomijam to pole.
15. Szukam obiektów sakralnych. Jest wzmianka o cerkwi, więc wpisuję 'cerkiew'.
16. Szukam zgromadzeń religijnych. Wzmianka o parafii greckokatolickiej, ale to parafia, nie zgromadzenie, więc pomijam to pole.

### Wynik w formacie json (wraz z wynikami poprzednich etapów przetwarzania):

```json
{
        "nazwa": "Kabarowce",
        "tom": "03",
        "strona": 647,
        "rodzaj": "indywidualne",
        "ID": "03-07091",
        "typ": [
            "wieś"
        ],
        "powiat_ocr": "złoczowski",
        "parafia_katolicka": "Zborów",
        "parafia_inna": [
            {
                "wyznanie": "gr. kat.",
                "nazwa_parafii": "Kabarowce"
            }
        ],
        "warianty_nazw": [
            {
                "lang": "ros.",
                "wariant_nazwy": "Kabariwci"
            }
        ],
        "powiat_ujednolicony": "złoczowski",
        "typ_punktu_osadniczego": [
            "Wieś"
        ],
        "właściciel": "Antoni Kriegshuber",
        "przemysłowe": [
            "fabryka świec woskowych"
        ],
        "młyny": [
            "młyn"
        ],
        "budownictwo_palacowe": [
            "dwór"
        ],
        "obiekty_sakralne": [
            "cerkiew"
        ]
}
```
