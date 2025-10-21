from pydantic import BaseModel, Field
from datetime import datetime

class UserRegister(BaseModel):
    username: str = Field()
    password: str = Field()
    
    class Config:
        validate_by_name = True
