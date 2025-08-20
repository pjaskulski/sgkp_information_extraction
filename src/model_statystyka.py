""" MODEL - statystyka """
from typing import List
from pydantic import BaseModel, Field


class LiczbaMkModel(BaseModel):
    data: str | None = Field(None, description="Data dla której podano liczbę mieszkańców, lub sformułowanie 'obecnie'")
    liczba: str | None = Field(None, description="Liczba mieszkańców")

class LiczbaDmModel(BaseModel):
    data: str | None = Field(None, description="Data dla której podano liczbę domów, lub sformułowanie 'obecnie'")
    liczba: str | None = Field(None, description="Liczba domów")

class SettlementMkStatModel(BaseModel):
    dotyczy: str | None = Field(None, description="czego dotyczą dane: główna miejscowość, inne miejsce opisane w haśle np. folwark, gmina")
    liczba: List[LiczbaMkModel] | None = Field(None, description="Liczba mieszkańców (wiele, jeżeli ppodano dane dla różnych lat)")

class SettlementDmStatModel(BaseModel):
    dotyczy: str | None = Field(None, description="czego dotyczą dane: główna miejscowość, inne miejsce opisane w haśle np. folwark, gmina")
    liczba: List[LiczbaDmModel] | None = Field(None, description="Liczba domów (wiele, jeżeli ppodano dane dla różnych lat)")

class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None, description="Kroki wyjaśniające prowadzące do ustalenia poszukiwanych danych dla hasła")
    l_mk_statystyka: List[SettlementMkStatModel] | None = Field(None, description="Dane o liczbie mieszkańców podane w tekście hasła")
    l_dm_statystyka: List[SettlementDmStatModel] | None = Field(None, description="Dane o liczbie domów podane w tekście hasła")
