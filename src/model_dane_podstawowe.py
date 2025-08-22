""" MODELE DANE PODSTAWOWE """
from typing import List
from pydantic import BaseModel, Field


class NameVarModel(BaseModel):
    lang: str | None = Field(None,
                             description="język wariantu nazwy, jeżeli podano np. niem., węg., jeżeli brak zapisz nieokr. - nieokreślony")
    wariant_nazwy: str | None = Field(None,
                                      description="wariant nazwy hasła (alias, nazwa w innym języku, nazwa występująca w dokumentach itp.)")

class ParafiaInnaModel(BaseModel):
    wyznanie: str | None = Field(None,
                             description="nazwa wyznania parafii np. ew., gr.-kat. itp.")
    nazwa_parafii: str | None = Field(None,
                                      description="nazwa parafii")

class EntryModel(BaseModel):
    chain_of_thought: List[str] | None = Field(None,
                                               description="Kroki wyjaśniające prowadzące do ustalenia danych podstawowych dla hasła")
    typ: List[str] | None = Field(None,
                            description="Lista typów hasła - co hasło opisuje np. wieś, miasto, miasteczko, rzekę, górę, osiedle, krainę itp., dla hasła może występować więcej niż jeden typ")
    powiat: str | None = Field(None,
                               description="Nazwa powiatu w którym położona jest miejscowość")
    gmina: str | None = Field(None,
                              description="Nazwa gminy w której położona jest miejscowość")
    gubernia: str | None = Field(None,
                                 description="Nazwa guberni, do której należy miejscowość")
    parafia_katolicka: str | None = Field(None,
                                          description="Nazwa parafii katolickiej (rzymsko-katolickiej)")
    parafia_inna: List[ParafiaInnaModel] | None = Field(None,
                                     description="Lista parafii nie katolickich (np. prawosławnych, greko-katolickich, ewangelickich)")
    autor: str | None = Field(None,
                              description="Inicjały lub nazwisko autora hasła, występuje na końcu hasła, część haseł nie ma podanego autora.")
    warianty_nazw: List[NameVarModel] | None = Field(None,
                                                     description="Lista wariantów nazw (aliasów) dla hasła.")
