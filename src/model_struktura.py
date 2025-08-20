""" MODEL - struktura """
from typing import List
from pydantic import BaseModel, Field


class WyznanieModel(BaseModel):
    chain_of_thought: List[str] = Field(
        None,
        description="Kroki wyjaśniające prowadzące do ustalenia nazwy wyznania i liczebności wyznawców"
        )
    wyznanie_ocr: str | None = Field(None, description="Nazwa wyznania, w takiej formie jak wystąpiła w tekście")
    liczba: str | None = Field(None, description="Liczba wyznawców")

class StrukturaWyznaniowaModel(BaseModel):
    dotyczy: str | None = Field(None, description="czego dotyczą dane: główna miejscowość, inne miejsce opisane w haśle np. folwark, gmina")
    struktura_wyznaniowa: List[WyznanieModel] | None = Field(None, description="Liczba wyznawców dla poszczególnych wyznań")

class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None, description="Kroki wyjaśniające prowadzące do ustalenia poszukiwanych danych dla hasła")
    ludnosc_wyznanie: List[StrukturaWyznaniowaModel] | None = Field(None, description="Dane o liczbie wyznawców podane w tekście hasła")
