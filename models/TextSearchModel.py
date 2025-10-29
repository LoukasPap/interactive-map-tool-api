from pydantic import BaseModel, Field

class TextSearch(BaseModel):
    include_input: str | None = Field(default=None, alias="includeInput")
    exclude_input: str | None = Field(default=None, alias="excludeInput")
    limit: str | None = Field(default=None)
    
    class Config:
        validate_by_name = True
        
    def take_int_limit(self):
        if self.limit is not None and self.limit != "":
            return int(self.limit)
        else:
            return None