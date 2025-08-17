# sgkp_information_extraction
Skrypty i materiały związane z przetwarzaniem Słownika Geograficznego Królestwa Polskiego

Teksty poszczególnych tomów SGKP zostały podzielone na hasła i pod-hasła, następnie zapisane w plikach JSON.

Pliki JSON są przetwarzane skryptami (Python) wykorzystującymi model LLM (gpt-4.1-mini) poprzez API OpenAI. Skrypty wyszukują oczekiwane informacje,
zwracając je w formie struktur, które uzupełniają źródłowy plik JSON.

W folderze **SRC** znajdują się dwa rodzaje skryptów, zależnie od sposobu przetwarzania:

Skrypty concurrent*.py działają natychmiast, pliki JSON dla każdego tomu dzielone są na kilka-kilkadziesiąt części i przetwarzane równoległe. Czas przetwarzania jednego tomu to około 40-50 minut.

Skrypty batch*.py korzystają z Batch API, czyli zadania przetwarzania są przygotowywane i wgrywane na serwery OpenAI i przetwarzane w ciąg u 24 godzin (często wcześniej), następnie można pobrać wyniki. Zaletą przetwarzania w tym trybie jest koszt niższy o 50%. 

W folderze **OCR** - pomocnicze skrypty do OCR

W folderze **PROMPT** - przykład przetwarzania treści SGKP bezpośrednio w aistudio z użyciem Gemini Pro: prompt, plik z danymi (treścią haseł) do załączenia, przykład wyniku w formacie JSON oraz w pliku 'przygotowywanie_promptow_wskazowki.docx' - **poradnik** ze wskazówkami jak przygotowywać prompty do ekstrakcji danych.
