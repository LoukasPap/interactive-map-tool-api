from pydantic import BaseModel, Field
from datetime import datetime

class UserRegister(BaseModel):
    username: str = Field()
    password: str = Field()
    
    class Config:
        validate_by_name = True

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
    isSaved: bool = Field(default=True, alias="isSaved")

class CollectionUpdate(Collection):
    markers: list[dict] = Field(default=[])
    shape: dict = Field(default={})

class CollectionOut(CollectionCreate):
    isSaved: bool = Field(default=True, alias="is_saved")