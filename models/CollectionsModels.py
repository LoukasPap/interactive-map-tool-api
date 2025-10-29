from pydantic import BaseModel, Field
from datetime import datetime

class Collection(BaseModel):
    markers: list[dict] = Field(default=[])
    shape: dict = Field(default={})
    date: str = Field(default=datetime.now().strftime("%Y-%m-%d"))
    type: str = Field(default="Unknown")

class CollectionCreate(Collection):
    owner: str = Field(alias="username")
    name: str = Field()
    description: str | None = Field(default=None)
    id: str = Field()
    isSaved: bool = Field(default=True)
    
