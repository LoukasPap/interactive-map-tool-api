from pydantic import BaseModel, Field
from typing import Annotated

class User(BaseModel):
    username: str = Field()
    password: str = Field()
    