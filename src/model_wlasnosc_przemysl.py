""" MODEL - właściciel, przemysł, zabytki """
from typing import List
from pydantic import BaseModel, Field


class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None, description="Kroki wyjaśniające prowadzące do ustalenia poszukiwanych danych dla hasła")
    wlasciciel: str | None = Field(None, description="Właściciel miejscowości/majątku (aktualny) - pomiń informacje historyczne sprzed XIX wieku")
    przemyslowe: List[str] | None = Field(None, description="Lista obiektów przemysłowych występujących w opisywanej miejscowości np. fabryki, huty, wytwórnie, kopalnie")
    mlyny: List[str] | None = Field(None, description="Lista młynów i wiatraków w opisywanej miejscowości np. młyn, 2 wiatraki, młyn o 2 kołach itp.")
    archeo: List[str] | None = Field(None, description="Lista znalezisk archeologicznych występujących w opisywanej miejscowości np. urny, ozdoby, szpile, broń, siekierki, narzędzia kamienne")
    zabytki: List[str] | None = Field(None, description="lista zabytków, ruin")
    architektura_krajobrazu: List[str] | None = Field(None, description="lista obiektów architektury krajobrazu np. park, ogród, oranżeria")
    kolekcjonerstwo: List[str] | None = Field(None, description="lista różnego rodzaju zbiorów: monet, książek, rycin (ale nie muzea!)")
    muzealnictwo: List[str] | None = Field(None, description="instytucje: muzea, gabinety archeologiczne")
    nekropolie: List[str] | None = Field(None, description="cmentarze, grobowce (bez obiektów archeologicznych)")
    rzemioslo: List[str] | None = Field(None, description="rzemieślnicy lub zakłady rzemieślnicze np. krawiec, kaletnik, stolarz, (pomiń przemysł, fabryki)")
    lesniczowki: List[str] | None = Field(None, description="leśniczówki, nadleśnictwa, gajówki")
    budownictwo_palacowe: List[str] | None = Field(None, description="obiekty pałacowe, dwory")
    magazyny: List[str] | None = Field(None, description="magazyny, spichlerze")
    wojsko: List[str] | None = Field(None, description="lista obiektów wojskowych np. koszary, fort, twierdza, żandarmeria, zarząd okręgu wojskowego, strzelnica")
    obiekty_sakralne: List[str] | None = Field(None, description="np. kościół, meczet, kaplica, synagoga, cerkiew, klasztor, dom modlitwy, sobór, katedra, jeżeli podano to z wezwaniem")
    zgromadzenia_religijne: List[str] | None = Field(None, description="np. zakon, monaster, klasztor, zgromadzenie, opactwo, zbór innowierców ")
