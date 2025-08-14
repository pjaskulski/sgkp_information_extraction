# sgkp_information_extraction
Skrypty i materiały związane z przetwarzaniem Słownika Geograficznego Królestwa Polskiego

Teksty poszczególnych tomów SGKP zostały podzielone na hasła i pod-hasła, następnie zapisane w plikach JSON.

Pliki JSON są przetwarzane skryptami (Python) wykorzystującymi model LLM (gpt-4.1-mini) poprzez API OpenAI. Skrypty wyszukują oczekiwane informacje,
zwracając je w formie stuktur, które uzupełniają źródłowy plik JSON.

W folderze znajdują się dwa rodzaje skryptów, zależnie od sposobu przetwarzania:

Skrypty concurrent*.py działają natychmiast, pliki JSON dla tom udzielone są na kilka-kilkadziesiąt części i przetwarzane równoległe. Czas przetwarzania jednego tomu to około 40-50 minut.

Skrypty batch*.py korzystają z Batch API, czyli zadania przetwarzania są przygotowywane i wgrywane na serwery OpenAI i przetwarzane w ciąg u 24 godzin (często wcześniej), następnie można pobrać wyniki. Zaletą przetwarzania w tym trybie jest koszt niższy o 50%. 
