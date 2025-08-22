# sgkp_information_extraction

Scripts and materials related to the processing of the Geographical Dictionary of the Kingdom of Poland

The texts of individual volumes of the SGKP were divided into entries and sub-entries, then saved in JSON files.

JSON files are processed by scripts (Python) using the LLM model (gpt-4.1-mini) via the OpenAI API. The scripts search for the expected information and return it in the form of structures that supplement the source JSON file.

There are two types of scripts in the **SRC** folder, depending on the processing method:

1. The ‘concurrent*.py’ scripts run immediately, with the JSON files for each volume divided into several to several dozen parts and processed in parallel. The processing time for one volume is approximately 40-50 minutes.

2. 'batch*.py' scripts use the Batch API, i.e., processing tasks are prepared and uploaded to OpenAI servers and processed in a 24-hour cycle (often earlier), after which the results can be downloaded. The advantage of processing in this mode is a 50% lower cost.

3. The auxiliary ‘prompt*.py’ files contain the definition of dynamically created prompts for individual queries/modules.

4. The auxiliary ‘model*.py’ files contain definitions of pydantic classes.

Due to the large amount of different types of data that need to be searched for in the SGKP entries, the extraction procedure has been divided into 6 separate modules (implemented by separate scripts) so that the excess of expected data does not impair the performance of the language model. Particularly difficult data requiring more analysis, such as population, religious structure, or land ownership structure, are processed separately:

  - basic data: type, county, municipality, province, Catholic parish, other parish, entry author, name variants
  - industry monuments: property owner, industrial facilities, mills, archaeological finds, monuments, landscape architecture, collecting, museology,   necropolises, crafts, forest lodges, palace construction, warehouses, military
  - institutions, offices: schools, offices, customs facilities, libraries, catering, healthcare, trade, charity, courts, breeding, bookstores, shipping, dormitories, urban infrastructure, post office, local government, police, financial institutions, health resorts
  - statistics: number of inhabitants, number of houses
  - religious structure: number of inhabitants by religion
  - land ownership: land ownership structure (types and area of land)

In the **TEST** folder - test results for various models on a test series (basic data extraction)

In the **EXAMPLES** folder - examples of results for various categories of information (for the test series)

In the **DICTIONARY** folder - additional dictionaries (standardized counties, types of settlement points)

In the **OCR** folder - auxiliary scripts for OCR

In the **PROMPT** folder - an example of SGKP content processing directly in aistudio using Gemini Pro: prompt, data file (content of entries) to be attached, example of the result in JSON format, and in the file ‘przygotowywanie_promptow_wskazowki.docx’ - a guide with tips on how to prepare prompts for data extraction.

---

Skrypty i materiały związane z przetwarzaniem Słownika Geograficznego Królestwa Polskiego

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
   - **przemysł zabytki**: właściciel majątku, obiekty przemysłowe, młyny, znaleziska archeologiczne, zabytki, architektura krajobrazu, kolekcjonerstwo, muzealnictwo, nekropolie, rzemiosło, leśniczowki, budownictwo pałacowe, magazyny, wojsko
   - **instytycje, urzędy**: szkoły, urzędy, obiekty celne, biblioteki, gastronomia, opieka_zdrowotna, handel, dobroczynność, sądy, hodowla, księgarnie, żegluga, bursy, infrastruktura miejska, poczta, samorząd, policja, instytucje finansowe, uzdrowiska 
   - **statystyka**: liczba mieszkańców, liczba domów
   - **struktura wyznaniowa**: liczba mieszkańców według wyznania
   - **własność ziemska**: struktura własności ziemskiej (rodzaje i powierzchnia gruntów)


W folderze **TESTY** - wyniki testów różnych modeli na serii testowej (ekstrakcja danych podstawowych)

W folderze **EXAMPLES** - przykłady wyników dla różnych kategorii informacji (dla serii testowej)

W folderze **DICTIONARY** - dodatkowe słowniki (powiaty ujednolicone, typy punktów osadniczych)

W folderze **OCR** - pomocnicze skrypty do OCR

W folderze **PROMPT** - przykład przetwarzania treści SGKP bezpośrednio w aistudio z użyciem Gemini Pro: prompt, plik z danymi (treścią haseł) do załączenia, przykład wyniku w formacie JSON oraz w pliku 'przygotowywanie_promptow_wskazowki.docx' - **poradnik** ze wskazówkami jak przygotowywać prompty do ekstrakcji danych.
