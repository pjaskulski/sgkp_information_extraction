""" MODEL - instytucje, urzędy"""
from typing import List
from pydantic import BaseModel, Field


class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None, description="Kroki wyjaśniające prowadzące do ustalenia poszukiwanych danych dla hasła")
    szkoly: List[str] | None = Field(None, description="Lista szkół w miejscowości np. szkoła elementarna, gimnazjum itp.")
    urzedy: List[str] | None = Field(None, description="Lista urzędów: miejski, poborowy itp.")
    celne: List[str] | None = Field(None, description="Lista obiektów celnych: komory celne, urzędy celne, przykomorki, posterunki celne itp.")
    biblioteki: List[str] | None = Field(None, description="Lista: biblioteki, czytelnie")
    gastronomia: List[str] | None = Field(None, description="Punkty gastronomiczne: karczmy, gospody, szynki, oberże, austerie, kawiarnie, restauracje")
    opieka_zdrowotna: List[str] | None = Field(None, description="Szpitale, ambulatoria, lecznice")
    handel: List[str] | None = Field(None, description="Lista obiektów handlowych: sklepy, targi, jatki, kramy")
    dobroczynnosc: List[str] | None = Field(None, description="Instytucje dobroczynne: przytułki, domy opieki, fundacje dla ubogich itp.")
    sady: List[str] | None = Field(None, description="Sądy")
    hodowla: List[str] | None = Field(None, description="Stajnie/owczarnie i obiekty hodowlane")
    ksiegarnie: List[str] | None = Field(None, description="Księgarnie, drukarnie, składy map, składy nut, antykwariaty")
    zegluga: List[str] | None = Field(None, description="Porty, przystanie, promy, spław, tratwy, łodzie, przeprawy")
    bursy: List[str] | None = Field(None, description="Lista obiektów typu: bursa, internat, konwikt")
    infrastruktura_miejska: List[str] | None = Field(None, description="Wodociągi, bruk, oświetlenie")
    poczta: List[str] | None = Field(None, description="obiekty w rodzaju: stacja pocztowa, poczta, poczthalteria, stacja telegrafu, położone w opisywanej miejscowości")
    samorzad: List[str] | None = Field(None, description="zarządy gmin/powiatów")
    policja: List[str] | None = Field(None, description="posterunki, zarządy policyjne, biuro policmajstra")
    instytucje_finansowe: List[str] | None = Field(None, description="banki, kasy pożyczkowe, kasy zapomogowe")
    uzdrowiska: List[str] | None = Field(None, description="uzdrowisko, zakład kąpielowy, zakład przyrodoleczniczy, kurort, zdrój, dom zdrojowy, zakład wodoleczniczy, pijalnia wód, inhalatorium, zakład borowinowy, kurhaus")
    stacje_drogi_zelaznej: List[str] | None = Field(None, description="stacje drogi żelaznej położone w miejscowości, lub w pobliżu opisywanej miejscowości (wówczas z nazwą), informacje te często apisane są skrótowo np. st. dr. żel., uwzględnij także przystanki drogi żelaznej, dworce kolejowe, przystanki kolejowe")
