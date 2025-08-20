""" MODEL - własność ziemska """
from typing import List
from pydantic import BaseModel, Field


class LandModel(BaseModel):
    """ model typu gruntu """
    chain_of_thought: List[str] = Field(
        None,
        description="Kroki wyjaśniające prowadzące do ustalenia rodzaju gruntu i jego powierzchni"
        )
    type_of_ground: str = Field(None, description="Rodzaj gruntu uprawnego np. ziemia orna, pstwisko, łąka, nieużytki, lasy itp.")
    area_of_ground: str = Field(None, description="Powierzchnia gruntu")

class LandOwnershipModel(BaseModel):
    """ model struktury własności ziemskiej """
    land_name: str = Field(None, description="Czego dotyczą informacje o własności ziemskiej: główna miejscowość, wieś, folwark - gdy w tekście haśle opisane są osobno różne części własności")
    land: List[LandModel] = Field(..., description="Lista gruntów we własności ziemskiej")

class EntryModel(BaseModel):
    """ lista własności ziemskich """
    chain_of_thought: List[str] = Field(
        None,
        description="Kroki wyjaśniające prowadzące do ustalenia struktury własności ziemskiej w danej miejscowości (haśle) lub w elemencie danego hasła jeżeli opisano osobno własność ziemską i strukturę gruntów dla wsi, folwarku itp."
        )
    lands: List[LandOwnershipModel] = Field(..., description="Lista własności ziemskich ze strukturą gruntów, występujących w analizowanym haśle")
