# sgkp_information_extraction
Skrypty i materiały związane z przetwarzaniem Słownika Geograficznego Królestwa Polskiego

Teksty poszczególnych tomów SGKP zostały podzielone na hasła i pod-hasła, następnie zapisane w plikach JSON.

Pliki JSON są przetwarzane skryptami (Python) wykorzystującymi model LLM (gpt-4.1-mini) poprzez API OpenAI. Skrypty wyszukują oczekiwane informacje,
zwracając je w formie struktur, które uzupełniają źródłowy plik JSON.

W folderze **SRC** znajdują się dwa rodzaje skryptów, zależnie od sposobu przetwarzania:

Skrypty concurrent*.py działają natychmiast, pliki JSON dla każdego tomu dzielone są na kilka-kilkadziesiąt części i przetwarzane równoległe. Czas przetwarzania jednego tomu to około 40-50 minut.

Pliki prompt*.py zawierają definicję dynamicznie tworzonych promptów dla poszczególnych zapytań/modułów. 

Ze względu na dużą liczbę różnego rodzaju danych, które należy wyszukać w tekstach haseł SGKP, procedurę ekstrakcji podzielono na 6 osobnych modułów (realizowanych przez osobne skrypty), tak by nadmiarem oczekiwanych danych nie pogorszyć wyniku pracy modelu językowego, szczególnie trudniejsze, wymagające większej analizy dane dotyczące liczby ludności, struktury wyznaniowej czy stryktury własności ziemskiej są przetwarzane osobno.:

 - **dane podstawowe**: typ, powiat, gmina, gubernia, parafia katolicka, parafia inna, autor hasła, warianty nazw
 - **przemysł zabytki**: właściciel majątku, obiekty przemysłowe, młyny, znaleziska archeologiczne, zabytki, architektura krajobrazu, kolekcjonerstwo, muzealnictwo, nekropolie, rzemiosło, leśniczowki, budownictwo pałacowe, magazyny, wojsko
 - **instytycje, urzędy**: szkoły, urzędy, obiekty celne, biblioteki, gastronomia, opieka_zdrowotna, handel, dobroczynność, sądy, hodowla, księgarnie, żegluga, bursy, infrastruktura miejska, poczta, samorząd, policja, instytucje finansowe, uzdrowiska 
 - **statystyka**: liczba mieszkańców, liczba domów
 - **struktura wyznaniowa**: liczba mieszkańców według wyznania
 - **własność ziemska**: struktura własności ziemskiej (rodzaje i powierzchnia gruntów)

Skrypty batch*.py korzystają z Batch API, czyli zadania przetwarzania są przygotowywane i wgrywane na serwery OpenAI i przetwarzane w ciąg u 24 godzin (często wcześniej), następnie można pobrać wyniki. Zaletą przetwarzania w tym trybie jest koszt niższy o 50%. 

W folderze **TESTY** - wyniki testów różnych modeli na serii testowej (ekstrakcja danych podstawowych)

W folderze **EXAMPLES** - przykłady wyników dla różnych kategorii informacji (dla serii testowej)

W folderze **DICTIONARY** - dodatkowe słowniki (powiaty ujednolicone, typy punktów osadniczych)

W folderze **OCR** - pomocnicze skrypty do OCR

W folderze **PROMPT** - przykład przetwarzania treści SGKP bezpośrednio w aistudio z użyciem Gemini Pro: prompt, plik z danymi (treścią haseł) do załączenia, przykład wyniku w formacie JSON oraz w pliku 'przygotowywanie_promptow_wskazowki.docx' - **poradnik** ze wskazówkami jak przygotowywać prompty do ekstrakcji danych.
